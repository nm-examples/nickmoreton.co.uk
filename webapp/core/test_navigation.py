from django.test import RequestFactory, TestCase
from wagtail.models import Site

from webapp.core.models import Navigation
from webapp.core.templatetags.navigation_tags import get_navigation
from webapp.testutils import content_tree


class NavigationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home, cls.articles, cls.packages, cls.article, cls.chapter, cls.package = (
            content_tree()
        )

    def test_existing_page_links_anchors_and_external_urls_work(self):
        navigation = Navigation.for_site(Site.objects.get(is_default_site=True))
        navigation.main_menu = [
            ("main_menu", {"label": "Articles", "page": self.articles}),
            ("main_menu", {"label": "Work", "page": self.home, "anchor": "work"}),
            ("main_menu", {"label": "External", "url": "https://example.com"}),
        ]
        navigation.save()
        result = get_navigation({"request": RequestFactory().get("/")})
        self.assertEqual(
            result["main_menu"],
            [
                {"label": "Articles", "url": "/articles/"},
                {"label": "Work", "url": "/#work"},
                {"label": "External", "url": "https://example.com"},
            ],
        )

    def test_unpublished_menu_page_is_not_rendered(self):
        navigation = Navigation.for_site(Site.objects.get(is_default_site=True))
        navigation.main_menu = [
            ("main_menu", {"label": "Hidden", "page": self.article})
        ]
        navigation.save()
        self.article.unpublish()
        result = get_navigation({"request": RequestFactory().get("/")})
        self.assertNotIn("Hidden", [item["label"] for item in result["main_menu"]])
