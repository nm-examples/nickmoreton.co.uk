from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, SimpleTestCase

from webapp.core.templatetags.navigation_tags import get_navigation


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
