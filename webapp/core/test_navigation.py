from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, SimpleTestCase, TestCase
from wagtail.models import Page, PageViewRestriction, Site

from webapp.core.models import Navigation
from webapp.core.templatetags.navigation_tags import get_navigation
from webapp.home.models import HomePage


class ProjectNavigationTests(SimpleTestCase):
    def menu(self, projects: list, *, configured: bool, preview=None) -> list[dict]:
        root = SimpleNamespace(
            pk=1,
            selected_projects=projects,
            get_url=Mock(return_value="/"),
            get_children=Mock(),
        )
        root.get_children.return_value.live.return_value.public.return_value = []
        menu = (
            [
                SimpleNamespace(value={"label": "Websites", "anchor": "work"}),
                SimpleNamespace(value={"label": "About", "anchor": "about"}),
            ]
            if configured
            else []
        )
        context = {"request": RequestFactory().get("/articles/"), "page": preview}
        with (
            patch(
                "webapp.core.templatetags.navigation_tags.Navigation.for_request",
                return_value=SimpleNamespace(main_menu=menu),
            ),
            patch(
                "webapp.core.templatetags.navigation_tags.Site.find_for_request",
                return_value=SimpleNamespace(root_page=SimpleNamespace(specific=root)),
            ),
        ):
            return get_navigation(context)["main_menu"]

    def test_configured_and_fallback_work_links_follow_homepage_selection(self):
        for configured in (True, False):
            for projects in ([], [object()]):
                with self.subTest(configured=configured, has_projects=bool(projects)):
                    items = self.menu(projects, configured=configured)
                    expected = [{"label": "About", "url": "/#about"}]
                    if projects:
                        expected.insert(0, {"label": "Websites", "url": "/#work"})
                    self.assertEqual(items, expected)

    def test_homepage_preview_uses_draft_selection(self):
        for projects in ([], [object()]):
            with self.subTest(has_projects=bool(projects)):
                preview = SimpleNamespace(pk=1, selected_projects=projects)
                items = self.menu(
                    [] if projects else [object()], configured=True, preview=preview
                )
                self.assertEqual(
                    any(item["url"] == "/#work" for item in items), bool(projects)
                )


class NavigationLinkTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home = Page.get_first_root_node().add_child(
            instance=HomePage(
                title="Navigation home", introduction="Introduction", about_body="About"
            )
        )
        cls.site = Site.objects.create(hostname="navigation.test", root_page=cls.home)
        cls.page = cls.home.add_child(
            instance=Page(title="Zulu", slug="configured-page", show_in_menus=True)
        )
        cls.second = cls.home.add_child(
            instance=Page(title="Alpha", slug="second-page", show_in_menus=True)
        )
        cls.home.add_child(instance=Page(title="Not in menus", show_in_menus=False))
        cls.draft = cls.home.add_child(
            instance=Page(title="Draft", live=False, show_in_menus=True)
        )
        private = cls.home.add_child(instance=Page(title="Private", show_in_menus=True))
        PageViewRestriction.objects.create(page=private, restriction_type="login")
        cls.restricted = private.add_child(instance=Page(title="Restricted descendant"))
        cls.navigation = Navigation.objects.create(site=cls.site)

    def context(self):
        return {"request": RequestFactory().get("/", HTTP_HOST="navigation.test")}

    def test_configured_links_resolve_targets_in_order_and_skip_hidden_pages(self):
        self.navigation.main_menu = [
            (
                "main_menu",
                {
                    "label": "Docs",
                    "url": "https://example.com/docs",
                    "anchor": "install",
                },
            ),
            ("main_menu", {"label": "Page", "page": self.page}),
            (
                "main_menu",
                {
                    "label": "Section",
                    "page": self.page,
                    "url": "https://ignored.example",
                    "anchor": "details",
                },
            ),
            ("main_menu", {"label": "About", "anchor": "about"}),
            ("main_menu", {"label": "Draft", "page": self.draft}),
            ("main_menu", {"label": "Private", "page": self.restricted}),
            ("main_menu", {"label": "Empty"}),
        ]
        self.navigation.save()

        self.assertEqual(
            get_navigation(self.context())["main_menu"],
            [
                {"label": "Docs", "url": "https://example.com/docs#install"},
                {"label": "Page", "url": "/configured-page/"},
                {"label": "Section", "url": "/configured-page/#details"},
                {"label": "About", "url": "/#about"},
            ],
        )

    def test_unusable_configured_menu_falls_back_to_visible_root_menu_pages(self):
        self.navigation.main_menu = [
            ("main_menu", {"label": "Draft", "page": self.draft}),
            ("main_menu", {"label": "Empty"}),
        ]
        self.navigation.save()

        self.assertEqual(
            get_navigation(self.context())["main_menu"],
            [
                {"label": "Zulu", "url": "/configured-page/"},
                {"label": "Alpha", "url": "/second-page/"},
                {"label": "About", "url": "/#about"},
            ],
        )
