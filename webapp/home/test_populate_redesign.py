import tempfile
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings
from wagtail.images import get_image_model

from webapp.core.models import Navigation
from webapp.testutils import content_tree


class PopulateRedesignTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home, cls.articles, cls.packages, cls.article, cls.chapter, cls.package = (
            content_tree()
        )

    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        settings = override_settings(MEDIA_ROOT=self.media.name)
        settings.enable()
        self.addCleanup(settings.disable)

    def run_command(self, apply=False):
        output = StringIO()
        call_command("populate_redesign", apply=apply, stdout=output)
        return output.getvalue()

    def test_dry_run_does_not_create_images_or_navigation(self):
        output = self.run_command()
        self.home.refresh_from_db()
        self.assertIn("Dry run", output)
        self.assertEqual(len(self.home.projects), 0)
        self.assertEqual(get_image_model().objects.count(), 0)
        self.assertEqual(Navigation.objects.count(), 0)

    def test_apply_preserves_body_and_is_repeatable(self):
        self.home.body = [("rich_text", "<p>Existing homepage content.</p>")]
        self.home.save_revision().publish()
        body = self.home.body.get_prep_value()
        self.run_command(apply=True)
        self.home.refresh_from_db()
        self.assertEqual(len(self.home.projects), 4)
        self.assertEqual(self.home.body.get_prep_value(), body)
        self.assertEqual(
            self.home.projects[0].value["title"], "Alcott Farm Bed & Breakfast"
        )
        response = self.client.get(self.home.url)
        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.content.decode(), r"/media/images/[^\"]+\.webp")
        revision_id = self.home.latest_revision_id
        menu = Navigation.objects.get().main_menu.get_prep_value()
        self.run_command(apply=True)
        self.home.refresh_from_db()
        self.assertEqual(self.home.latest_revision_id, revision_id)
        self.assertEqual(get_image_model().objects.count(), 4)
        self.assertEqual(Navigation.objects.get().main_menu.get_prep_value(), menu)

    def test_unpublished_homepage_changes_are_not_published(self):
        self.home.headline = "Draft headline"
        self.home.save_revision()
        self.run_command(apply=True)
        self.home.refresh_from_db()
        self.assertTrue(self.home.has_unpublished_changes)
        self.assertEqual(len(self.home.projects), 0)
        self.assertEqual(
            self.home.get_latest_revision_as_object().headline, "Draft headline"
        )

    def test_existing_article_metadata_is_preserved(self):
        self.article.slug = "getting-started-with-wagtail"
        self.article.topic = "Custom editorial label"
        self.article.homepage_order = 42
        self.article.save_revision().publish()
        self.run_command(apply=True)
        self.article.refresh_from_db()
        self.assertEqual(self.article.topic, "Custom editorial label")
        self.assertEqual(self.article.homepage_order, 42)
        self.assertEqual(
            self.article.repository_url,
            "https://github.com/nm-examples/wagtail-starter-kit",
        )
