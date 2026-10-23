"""Coverage for custom page content, navigation, search, and PyPI integration."""

from datetime import date
from unittest.mock import patch

import requests
from django.core.cache import cache
from django.db import connection
from django.template import RequestContext, Template
from django.test import RequestFactory, TestCase, override_settings
from wagtail.models import Site
from wagtail.search.backends import get_search_backend

from webapp.core.models import Navigation
from webapp.home.models import HomePage
from webapp.pages.models import (
    ArticleChapterPage,
    ArticleIndexPage,
    ArticlePage,
    PackageIndexPage,
    PackagePage,
)
from webapp.pages.templatetags.pypi_tags import pypi_info


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"])
class UpgradeRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.first()
        Site.objects.update_or_create(
            is_default_site=True,
            defaults={"hostname": "localhost", "root_page": cls.home},
        )
        cls.index = cls.home.add_child(
            instance=ArticleIndexPage(title="Articles", slug="articles")
        )
        cls.article = cls.index.add_child(
            instance=ArticlePage(
                title="Live regression article",
                slug="regression-article",
                date=date(2026, 1, 1),
                body=[
                    ("heading", {"heading": "Regression heading", "level": "h2"}),
                    ("rich_text", "<p>Published regression body</p>"),
                    ("code", {"code": "print('<hello>')", "language": "python"}),
                ],
            )
        )
        cls.article.save_revision().publish()
        cls.draft = cls.index.add_child(
            instance=ArticlePage(
                title="Hidden regression draft",
                slug="hidden-draft",
                date=date(2026, 2, 1),
                live=False,
            )
        )
        cls.draft.save_revision()

    def setUp(self):
        cache.clear()

    def test_home_and_index_only_list_live_articles(self):
        for url in ["/", self.index.url]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, self.article.title)
                self.assertNotContains(response, self.draft.title)
        self.assertEqual(self.client.get(self.draft.url).status_code, 404)

    def test_article_renders_custom_streamfield_blocks(self):
        response = self.client.get(self.article.url)
        self.assertContains(response, "Regression heading")
        self.assertContains(response, "Published regression body")
        self.assertContains(response, "language-python")
        self.assertContains(response, "&lt;hello&gt;")
        self.assertContains(response, "Copy code")

    def test_chapter_navigation_skips_unpublished_chapters(self):
        first = self.article.add_child(
            instance=ArticleChapterPage(title="First chapter", slug="first")
        )
        first.save_revision().publish()
        self.article.add_child(
            instance=ArticleChapterPage(
                title="Hidden chapter", slug="hidden", live=False
            )
        )
        last = self.article.add_child(
            instance=ArticleChapterPage(title="Last chapter", slug="last")
        )
        last.save_revision().publish()
        self.assertEqual(first.get_next_chapter().pk, last.pk)
        self.assertEqual(last.get_previous_chapter().pk, first.pk)
        self.assertContains(self.client.get(first.url), last.url)

    def test_postgresql_search_returns_live_pages(self):
        self.assertEqual(connection.vendor, "postgresql")
        backend = get_search_backend()
        backend.add(self.article)
        backend.add(self.draft)
        for page_number in ["1", "invalid", "999"]:
            response = self.client.get(
                "/search/", {"query": "regression", "page": page_number}
            )
            self.assertContains(response, self.article.title)
            self.assertNotContains(response, self.draft.title)
        self.assertContains(
            self.client.get("/search/", {"query": "nonexistentword"}),
            "No results found",
        )

    def test_navigation_tag_renders_site_menu(self):
        navigation = Navigation.for_site(Site.objects.get(is_default_site=True))
        navigation.main_menu = [
            ("main_menu", {"label": "Regression menu", "page": self.index})
        ]
        navigation.save()
        request = RequestFactory().get("/", HTTP_HOST="localhost")
        rendered = Template("{% load navigation_tags %}{% get_navigation %}").render(
            RequestContext(request)
        )
        self.assertIn("Regression menu", rendered)
        self.assertIn(self.index.url, rendered)

    @patch("webapp.pages.templatetags.pypi_tags.requests.get")
    def test_package_page_renders_mocked_pypi_metadata(self, get):
        get.return_value.status_code = 200
        get.return_value.json.return_value = {
            "info": {
                "version": "1.2.3",
                "project_url": "https://pypi.org/project/regression/",
                "home_page": "https://example.com/",
            },
            "releases": {"1.2.3": [{"upload_time": "2026-01-02T12:00:00"}]},
        }
        index = self.home.add_child(
            instance=PackageIndexPage(title="Packages", slug="packages")
        )
        package = index.add_child(
            instance=PackagePage(
                title="Regression package",
                slug="regression-package",
                date=date(2026, 1, 1),
                pypi_package_name="regression",
            )
        )
        package.save_revision().publish()
        response = self.client.get(package.url)
        self.assertContains(response, "1.2.3")
        self.assertContains(response, "02 Jan 2026")
        get.assert_called_once_with(
            "https://pypi.org/pypi/regression/json", timeout=(2, 3)
        )

    @patch("webapp.pages.templatetags.pypi_tags.requests.get")
    def test_pypi_tag_handles_unavailable_package(self, get):
        get.return_value.status_code = 404
        get.return_value.raise_for_status.side_effect = requests.HTTPError
        self.assertEqual(
            pypi_info("missing-package"),
            {
                "release": None,
                "pypi_url": "https://pypi.org/project/missing-package/",
                "repository_url": "",
            },
        )
