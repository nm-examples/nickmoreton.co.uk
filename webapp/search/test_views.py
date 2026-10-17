from django.test import TestCase
from wagtail.models import PageViewRestriction

from webapp.testutils import content_tree


class SearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home, cls.articles, cls.packages, cls.article, cls.chapter, cls.package = (
            content_tree()
        )

    def test_search_results_exclude_restricted_pages(self):
        PageViewRestriction.objects.create(
            page=self.article, restriction_type="password", password="secret"
        )
        response = self.client.get("/search/", {"query": "Example"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f'href="{self.article.url}"')
        self.assertContains(response, f'href="{self.package.url}"')

    def test_invalid_page_and_blank_query_are_handled(self):
        for query in [
            {"query": "Example", "page": "invalid"},
            {"query": "Example", "page": "999"},
            {"query": "   "},
        ]:
            with self.subTest(query=query):
                self.assertEqual(self.client.get("/search/", query).status_code, 200)
