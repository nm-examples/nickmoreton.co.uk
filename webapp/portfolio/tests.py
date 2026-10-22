import io
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image as PillowImage
from wagtail.images import get_image_model

from webapp.home.models import HomePage, HomePagePortfolioProject

from .models import PortfolioProject


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
