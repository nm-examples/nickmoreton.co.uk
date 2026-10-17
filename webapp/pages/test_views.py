from datetime import date
from unittest.mock import patch

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.test import TestCase

from webapp.pages.models import ArticlePage
from webapp.testutils import content_tree, publish


class RedesignedPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home, cls.articles, cls.packages, cls.article, cls.chapter, cls.package = (
            content_tree()
        )

    @patch(
        "webapp.pages.templatetags.pypi_tags.package_metadata",
        return_value={"release": None},
    )
    def test_all_page_types_render_with_shared_navigation(self, metadata):
        for page in [
            self.home,
            self.articles,
            self.packages,
            self.article,
            self.chapter,
            self.package,
        ]:
            with self.subTest(page=page.title):
                response = self.client.get(page.url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'id="main"')
                self.assertContains(response, 'id="navigation"')
                self.assertContains(response, "Skip to content")

    def test_article_renders_cms_content_toc_and_chapter_link(self):
        publish(
            self.articles,
            ArticlePage(
                title="Related article",
                slug="related",
                date=date.today(),
                topic="Tools",
            ),
        )
        response = self.client.get(self.article.url)
        self.assertContains(response, "Some article text.")
        self.assertContains(response, 'href="#getting-started"')
        self.assertContains(response, f'href="{self.chapter.url}"')
        self.assertContains(response, 'id="getting-started"')
        self.assertContains(response, "Related article")

    def test_chapter_has_parent_breadcrumb_and_active_navigation(self):
        response = self.client.get(self.chapter.url)
        soup = BeautifulSoup(response.content, "html.parser")
        self.assertIsNotNone(
            soup.select_one(
                f'.chapter-list a[href="{self.chapter.url}"][aria-current="page"]'
            )
        )
        self.assertIsNotNone(
            soup.select_one(f'.breadcrumb a[href="{self.article.url}"]')
        )
        self.assertEqual(len(soup.find_all("h1")), 1)

    @patch(
        "webapp.pages.templatetags.pypi_tags.package_metadata",
        return_value={"release": None},
    )
    def test_package_renders_when_metadata_is_unavailable(self, metadata):
        response = self.client.get(self.package.url)
        self.assertContains(response, "Release information is currently unavailable.")
        self.assertContains(response, "https://pypi.org/project/example-package/")

    def test_search_and_error_pages_use_theme(self):
        for url, status in [
            ("/search/", 200),
            ("/search/?query=unmatchedsearchphrase", 200),
            ("/missing-page/", 404),
            ("/kitchen-sink/", 200),
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)
                self.assertContains(response, "css/bundle", status_code=status)

    def test_wagtail_edit_forms_render_new_content_fields(self):
        editor = get_user_model().objects.create_superuser(
            username="editor", email="editor@example.com", password=None
        )
        self.client.force_login(editor)
        for page in [self.home, self.article, self.package]:
            with self.subTest(page=page.title):
                response = self.client.get(f"/admin/pages/{page.pk}/edit/")
                self.assertEqual(response.status_code, 200)
        self.assertContains(
            self.client.get(f"/admin/pages/{self.home.pk}/edit/"), 'name="hero_title"'
        )
