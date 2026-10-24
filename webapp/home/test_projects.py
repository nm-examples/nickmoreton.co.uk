from unittest.mock import patch

from django.test import SimpleTestCase

from webapp.home.models import HomePage, PortfolioProject


class ProjectSelectionTests(SimpleTestCase):
    def test_selected_order_and_hero_exclude_deleted_projects(self):
        first = PortfolioProject(title="First")
        second = PortfolioProject(title="Second")
        home = HomePage(
            content_type_id=1,
            project_selection=[
                ("project", second),
                ("project", None),
                ("project", first),
            ],
        )

        self.assertEqual(home.selected_projects, [second, first])
        with patch("webapp.home.models.random.choice", return_value=first) as choose:
            self.assertIs(home.hero_project, first)
        choose.assert_called_once_with([second, first])

    def test_no_remaining_projects_has_no_hero(self):
        home = HomePage(content_type_id=1, project_selection=[("project", None)])

        with patch("webapp.home.models.random.choice") as choose:
            self.assertIsNone(home.hero_project)
        self.assertEqual(home.selected_projects, [])
        choose.assert_not_called()
