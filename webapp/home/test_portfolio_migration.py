from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone
from modelcluster.models import get_serializable_data_for_fields


class PortfolioMigrationTests(TransactionTestCase):
    migrate_from = [
        ("home", "0006_correct_support_engineer_title"),
        ("portfolio", "0001_initial"),
    ]
    migrate_to = [("home", "0007_portfolio_snippets")]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        self.old_apps = executor.loader.project_state(self.migrate_from).apps
        self.addCleanup(self.restore_schema)

    def restore_schema(self):
        MigrationExecutor(connection).migrate(self.migrate_to)

    def test_live_draft_and_historical_selections_survive_and_can_be_reversed(self):
        Home = self.old_apps.get_model("home", "HomePage")
        Revision = self.old_apps.get_model("wagtailcore", "Revision")
        ContentType = self.old_apps.get_model("contenttypes", "ContentType")
        home = Home.objects.get(slug="home")
        home_type = ContentType.objects.get(app_label="home", model="homepage")

        def projects(title):
            return [
                {
                    "type": "project",
                    "value": {
                        "title": title,
                        "category": "Local",
                        "description": "Existing copy",
                        "image": None,
                        "image_description": "Screenshot",
                        "record_url": "https://example.com/record/",
                        "featured": False,
                    },
                }
            ]

        def revision(title):
            data = get_serializable_data_for_fields(home)
            data["projects"] = projects(title)
            return Revision.objects.create(
                content_type=home_type,
                base_content_type_id=home_type.pk,
                object_id=str(home.pk),
                object_str="Home",
                created_at=timezone.now(),
                content=data,
            )

        historical = revision("Historical project")
        live = revision("Live project")
        draft = revision("Draft project")
        home.projects = projects("Live project")
        home.live = True
        home.has_unpublished_changes = True
        home.live_revision_id = live.pk
        home.latest_revision_id = draft.pk
        home.save()

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        from webapp.home.models import HomePage
        from webapp.portfolio.models import PortfolioProject

        current = HomePage.objects.get(pk=home.pk)
        self.assertEqual([p.title for p in current.selected_projects], ["Live project"])
        self.assertTrue(current.has_unpublished_changes)
        self.assertEqual(current.latest_revision_id, draft.pk)
        self.assertEqual(current.live_revision_id, live.pk)
        draft_page = current.get_latest_revision_as_object()
        self.assertEqual(
            draft_page.portfolio_items.first().project.title, "Draft project"
        )
        self.assertFalse(PortfolioProject.objects.get(title="Draft project").live)
        self.assertFalse(
            PortfolioProject.objects.get(title="Historical project").show_in_hero
        )
        self.assertTrue(PortfolioProject.objects.get(title="Live project").show_in_hero)
        archived = current.revisions.get(pk=historical.pk).as_object()
        self.assertEqual(
            archived.portfolio_items.first().project.title, "Historical project"
        )

        # Publishing a migrated draft still uses the normal page revision flow.
        current.revisions.get(pk=draft.pk).publish()
        current.refresh_from_db()
        self.assertEqual(current.portfolio_items.first().project.title, "Draft project")

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        Home = executor.loader.project_state(self.migrate_from).apps.get_model(
            "home", "HomePage"
        )
        restored = Home.objects.get(pk=home.pk)
        self.assertEqual(restored.projects[0].value["title"], "Draft project")
