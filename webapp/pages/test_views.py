from datetime import date
from unittest.mock import patch

from bs4 import BeautifulSoup
from django.test import TestCase

from webapp.pages.models import ArticlePage
from webapp.testutils import content_tree, publish


class RedesignedPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home, cls.articles, cls.packages, cls.article, cls.chapter, cls.package = (
            content_tree()
        )

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
    def test_contents_links_avoid_shared_template_ids(self, metadata):
        for page in [self.article, self.chapter, self.package]:
            with self.subTest(page=page.title):
                page.body = [
                    ("heading", {"heading": "Main", "level": "h2"}),
                    ("heading", {"heading": "Navigation", "level": "h2"}),
                    (
                        "rich_text",
                        '<h3 id="main">Explicit main</h3>'
                        '<h3 id="navigation">Explicit navigation</h3>'
                        '<h3 id="main-2">Existing anchor</h3>',
                    ),
                ]
                page.save_revision().publish()
                response = self.client.get(page.url)
                self.assertEqual(response.status_code, 200)
                soup = BeautifulSoup(response.content, "html.parser")
                ids = [element["id"] for element in soup.find_all(id=True)]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertEqual(soup.find(id="main").name, "main")
                self.assertEqual(soup.find(id="navigation").name, "nav")
                self.assertEqual(soup.find(id="main-2").get_text(), "Existing anchor")
                links = soup.select('.sidebar .toc a[href^="#"]')
                self.assertEqual(len(links), 5)
                for link in links:
                    targets = soup.find_all(id=link["href"][1:])
                    self.assertEqual(len(targets), 1)
                    self.assertIn(targets[0].name, ["h2", "h3"])
                    self.assertEqual(targets[0].get_text(), link.get_text())

    @patch(
        "webapp.pages.templatetags.pypi_tags.package_metadata",
        return_value={"release": None},
    )
    def test_package_renders_when_metadata_is_unavailable(self, metadata):
        response = self.client.get(self.package.url)
        self.assertContains(response, "Release information is currently unavailable.")
        self.assertContains(response, "https://pypi.org/project/example-package/")
