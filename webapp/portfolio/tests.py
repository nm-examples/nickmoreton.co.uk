import io
import tempfile
from unittest.mock import MagicMock, Mock, patch

import requests
import yaml
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.base import ContentFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image as PillowImage
from wagtail.images import get_image_model

from webapp.home.models import HomePage, HomePagePortfolioProject

from .importing import save_import
from .models import PortfolioProject, PortfolioSourceRecord
from .source import (
    RAW_ROOT,
    TEXT_FIELDS,
    SourceError,
    fetch_snapshot,
    parse_record,
    refresh_sources,
)

COMMIT = "a" * 40
MARKDOWN = """---
title: Example business
first_published_at: '2020-02-05T14:46:19+13:00'
site_url: https://example.com/
sector:
  - travel
  - hospitality
---

A local business website.
"""


def snapshot(slug="example-business"):
    return parse_record(MARKDOWN, slug, COMMIT, "tree-sha")


def source_record(**kwargs):
    return PortfolioSourceRecord.objects.create(
        **{**snapshot(), "fetched_at": timezone.now(), **kwargs}
    )


def webp_bytes():
    buffer = io.BytesIO()
    PillowImage.new("RGB", (32, 24), "orange").save(buffer, format="WEBP")
    return buffer.getvalue()


class PortfolioTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        settings = override_settings(MEDIA_ROOT=self.media.name)
        settings.enable()
        self.addCleanup(settings.disable)
        self.user = get_user_model().objects.create_superuser(
            "portfolio-admin", "portfolio@example.com", "test-password"
        )
        self.client.force_login(self.user)

    def project(self, **kwargs):
        image = get_image_model().objects.create(
            title="Screenshot", file=ContentFile(webp_bytes(), name="test.webp")
        )
        project = PortfolioProject.objects.create(
            title="Local title", image=image, live=False, **kwargs
        )
        project.save_revision().publish()
        project.refresh_from_db()
        return project

    def import_data(self, record, **overrides):
        project = record.project
        return {
            **{field: record.data[field] for field in TEXT_FIELDS},
            "source_fingerprint": record.fingerprint,
            "project_revision": str(project.latest_revision_id or "")
            if project
            else "",
            "apply_fields": list(TEXT_FIELDS),
            "import_image": False,
            **overrides,
        }

    def test_hero_pool_is_independent_of_homepage_selection(self):
        home = HomePage.objects.get(slug="home")
        hero = self.project(show_in_hero=True)
        selected = self.project(show_in_hero=False)
        home.portfolio_items.add(
            HomePagePortfolioProject(project=selected, sort_order=0)
        )
        home.save_revision().publish()
        self.assertEqual(home.hero_project, hero)
        self.assertEqual(home.selected_projects, [selected])
        response = self.client.get(home.url)
        self.assertEqual(response.status_code, 200)
        hero.unpublish()
        self.assertIsNone(home.hero_project)

    def test_unpublished_snippets_are_excluded_and_selection_can_be_reordered(self):
        home = HomePage.objects.get(slug="home")
        first, second = self.project(), self.project()
        home.portfolio_items.add(HomePagePortfolioProject(project=first, sort_order=1))
        home.portfolio_items.add(HomePagePortfolioProject(project=second, sort_order=0))
        home.save_revision().publish()
        self.assertEqual(home.selected_projects, [second, first])
        second.unpublish()
        home = HomePage.objects.get(pk=home.pk)
        self.assertEqual(home.selected_projects, [first])

    def test_draft_edits_do_not_change_live_hero(self):
        home = HomePage.objects.get(slug="home")
        project = self.project(show_in_hero=True)
        project.show_in_hero = False
        project.title = "Draft title"
        project.save_revision()
        self.assertEqual(home.hero_project.title, "Local title")

    def test_refresh_preserves_snippets_and_review_baseline(self):
        project = self.project(show_in_hero=True)
        record = source_record(
            project=project, last_applied_data={"title": "Earlier source"}
        )
        values = snapshot()
        values["raw_markdown"] += "New description."
        values["fingerprint"] = "changed"
        with patch("webapp.portfolio.source.fetch_snapshot", return_value=[values]):
            self.assertEqual(refresh_sources(), 1)
            refresh_sources()
        record.refresh_from_db()
        project.refresh_from_db()
        self.assertEqual(PortfolioSourceRecord.objects.count(), 1)
        self.assertEqual(project.title, "Local title")
        self.assertTrue(project.show_in_hero)
        self.assertEqual(record.last_applied_data, {"title": "Earlier source"})
        self.assertEqual(record.status, "Not yet reviewed")

    def test_missing_upstream_is_flagged_and_reappearing_record_is_restored(self):
        project = self.project()
        record = source_record(project=project)
        with patch("webapp.portfolio.source.fetch_snapshot", return_value=[]):
            refresh_sources()
        record.refresh_from_db()
        self.assertEqual(record.status, "Missing upstream")
        self.assertTrue(PortfolioProject.objects.filter(pk=project.pk).exists())
        with patch("webapp.portfolio.source.fetch_snapshot", return_value=[snapshot()]):
            refresh_sources()
        record.refresh_from_db()
        self.assertFalse(record.missing_upstream)

    def test_refresh_links_migrated_project_by_record_url(self):
        project = self.project(record_url=snapshot()["data"]["record_url"])
        with patch("webapp.portfolio.source.fetch_snapshot", return_value=[snapshot()]):
            refresh_sources()
        self.assertEqual(PortfolioSourceRecord.objects.get().project, project)
        self.assertEqual(PortfolioSourceRecord.objects.get().status, "Not yet reviewed")

    def test_failed_refresh_preserves_previous_snapshot(self):
        record = source_record()
        with patch(
            "webapp.portfolio.source.fetch_snapshot",
            side_effect=SourceError("Unavailable"),
        ):
            response = self.client.post(reverse("portfolio_sources:refresh"))
        self.assertRedirects(response, reverse("portfolio_sources:index"))
        record.refresh_from_db()
        self.assertFalse(record.missing_upstream)
        self.assertEqual(record.raw_markdown, MARKDOWN)

    def test_create_prefills_review_and_saves_adjusted_draft(self):
        record = source_record()
        response = self.client.get(
            reverse("portfolio_sources:review", args=[record.pk])
        )
        self.assertContains(response, "Example business")
        data = self.import_data(record, title="My editorial title")
        response = self.client.post(
            reverse("portfolio_sources:review", args=[record.pk]), data
        )
        record.refresh_from_db()
        self.assertRedirects(
            response,
            reverse(
                "wagtailsnippets_portfolio_portfolioproject:edit",
                args=[record.project_id],
            ),
        )
        project = record.project
        self.assertFalse(project.live)
        self.assertFalse(project.show_in_hero)
        self.assertEqual(
            project.get_latest_revision_as_object().title, "My editorial title"
        )
        self.assertEqual(record.last_applied_data["title"], "Example business")
        self.assertEqual(record.status, "Up to date")

    def test_native_project_and_homepage_editors_render(self):
        project = self.project()
        self.assertContains(
            self.client.get(reverse("wagtailsnippets_portfolio_portfolioproject:list")),
            "Local title",
        )
        self.assertContains(
            self.client.get(
                reverse(
                    "wagtailsnippets_portfolio_portfolioproject:edit", args=[project.pk]
                )
            ),
            "Show in hero",
        )
        home = HomePage.objects.get(slug="home")
        self.assertContains(
            self.client.get(reverse("wagtailadmin_pages:edit", args=[home.pk])),
            "Projects",
        )

    def test_source_listing_uses_native_header_search_and_review_actions(self):
        record = source_record()
        response = self.client.get(reverse("portfolio_sources:index"))
        self.assertContains(response, "w-slim-header")
        self.assertContains(response, 'form="portfolio-source-refresh"')
        self.assertContains(response, 'id="portfolio-source-refresh"')
        self.assertIsNotNone(
            BeautifulSoup(response.content, "html.parser").find(
                "button", attrs={"form": "portfolio-source-refresh"}
            )
        )
        self.assertContains(response, "Create snippet")
        self.assertContains(
            response, reverse("portfolio_sources:review", args=[record.pk])
        )
        response = self.client.get(
            reverse("portfolio_sources:index_results"), {"q": "Not a matching title"}
        )
        self.assertNotContains(response, "Example business")
        self.assertNotContains(response, "<header")

    def test_update_preserves_unselected_fields_and_existing_draft(self):
        project = self.project(show_in_hero=True, description="Live copy")
        project.description = "Pending local copy"
        project.save_revision()
        record = source_record(project=project)
        save_import(
            record.pk, self.import_data(record, apply_fields=["title"]), self.user
        )
        project.refresh_from_db()
        draft = project.get_latest_revision_as_object()
        self.assertEqual(project.title, "Local title")
        self.assertEqual(project.description, "Live copy")
        self.assertEqual(draft.title, "Example business")
        self.assertEqual(draft.description, "Pending local copy")
        self.assertTrue(draft.show_in_hero)
        self.assertEqual(draft.image_id, project.image_id)

    def test_review_rejects_intervening_source_or_project_changes(self):
        project = self.project()
        record = source_record(project=project)
        data = self.import_data(record)
        PortfolioSourceRecord.objects.filter(pk=record.pk).update(fingerprint="changed")
        with self.assertRaisesMessage(SourceError, "source changed"):
            save_import(record.pk, data, self.user)
        PortfolioSourceRecord.objects.filter(pk=record.pk).update(
            fingerprint=record.fingerprint
        )
        project.description = "Another edit"
        project.save_revision()
        with self.assertRaisesMessage(SourceError, "project changed"):
            save_import(record.pk, data, self.user)

    def test_repeated_create_submission_cannot_duplicate_snippet(self):
        record = source_record()
        data = self.import_data(record)
        save_import(record.pk, data, self.user)
        with self.assertRaises(SourceError):
            save_import(record.pk, data, self.user)
        self.assertEqual(PortfolioProject.objects.count(), 1)

    def test_screenshot_is_imported_only_when_selected_and_reuses_existing_image(self):
        record = source_record()
        with patch(
            "webapp.portfolio.importing.download_image", return_value=webp_bytes()
        ) as download:
            project = save_import(
                record.pk, self.import_data(record, import_image=True), self.user
            )
            record.refresh_from_db()
            save_import(
                record.pk, self.import_data(record, import_image=True), self.user
            )
        self.assertEqual(download.call_count, 2)
        self.assertEqual(get_image_model().objects.count(), 1)
        self.assertIsNotNone(project.image_id)

    def test_image_failure_does_not_create_snippet(self):
        record = source_record()
        with patch(
            "webapp.portfolio.importing.download_image",
            side_effect=SourceError("Missing screenshot"),
        ):
            response = self.client.post(
                reverse("portfolio_sources:review", args=[record.pk]),
                self.import_data(record, import_image=True),
            )
        self.assertContains(response, "Missing screenshot")
        self.assertEqual(PortfolioProject.objects.count(), 0)
        record.refresh_from_db()
        self.assertIsNone(record.project_id)

    def test_admin_permissions_and_post_only_refresh(self):
        self.assertEqual(
            self.client.get(reverse("portfolio_sources:refresh")).status_code, 405
        )
        record = source_record()
        user = get_user_model().objects.create_user("reader")
        user.user_permissions.add(
            *Permission.objects.filter(
                codename__in=["access_admin", "view_portfoliosourcerecord"]
            )
        )
        self.client.force_login(user)
        self.assertContains(
            self.client.get(reverse("portfolio_sources:index")), "Example business"
        )
        with patch("webapp.portfolio.views.refresh_sources") as refresh:
            self.assertEqual(
                self.client.post(
                    reverse("portfolio_sources:refresh"),
                    headers={"x-requested-with": "XMLHttpRequest"},
                ).status_code,
                403,
            )
        refresh.assert_not_called()
        self.assertEqual(
            self.client.get(
                reverse("portfolio_sources:review", args=[record.pk]),
                headers={"x-requested-with": "XMLHttpRequest"},
            ).status_code,
            403,
        )

    def test_refresh_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        with patch("webapp.portfolio.views.refresh_sources") as refresh:
            self.assertEqual(
                client.post(reverse("portfolio_sources:refresh")).status_code, 403
            )
        refresh.assert_not_called()


class SourceFetchTests(TestCase):
    def test_fetch_uses_one_commit_for_every_record_and_keeps_raw_data(self):
        def response(url):
            if url.endswith("commits/main"):
                return Mock(json=lambda: {"sha": COMMIT})
            if "/contents/" in url:
                self.assertIn(f"ref={COMMIT}", url)
                return Mock(
                    json=lambda: [
                        {"name": "index.md", "type": "file"},
                        {"name": "example-business", "type": "dir", "sha": "tree-sha"},
                    ]
                )
            self.assertTrue(url.startswith(f"{RAW_ROOT}/{COMMIT}/"))
            return Mock(text=MARKDOWN)

        with patch("webapp.portfolio.source.get_response", side_effect=response):
            result = fetch_snapshot()
        self.assertEqual(result[0]["raw_markdown"], MARKDOWN)
        self.assertEqual(result[0]["data"]["category"], "Travel / Hospitality")

    def test_network_errors_abort_snapshot(self):
        with patch(
            "webapp.portfolio.source.get_response", side_effect=requests.Timeout
        ):
            with self.assertRaises(SourceError):
                fetch_snapshot()

    def test_yaml_is_loaded_safely(self):
        with self.assertRaises(yaml.constructor.ConstructorError):
            parse_record(
                "---\ntitle: !!python/object:builtins.object {}\n---\n",
                "example",
                COMMIT,
                "tree",
            )

    def test_invalid_screenshot_url_is_rejected(self):
        from .importing import download_image

        record = source_record()
        record.data["image_url"] = "https://example.com/screenshot.webp"
        with patch("webapp.portfolio.importing.requests.get") as get:
            with self.assertRaises(SourceError):
                download_image(record)
        get.assert_not_called()

    def test_screenshot_response_must_be_valid_webp(self):
        from .importing import download_image

        response = MagicMock()
        response.__enter__.return_value = response
        response.status_code = 200
        response.iter_content.return_value = [b"not an image"]
        with patch("webapp.portfolio.importing.requests.get", return_value=response):
            with self.assertRaises(SourceError):
                download_image(source_record())
