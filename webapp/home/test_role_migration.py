from importlib import import_module
from types import SimpleNamespace

from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.test import TestCase
from wagtail.models import Revision

from webapp.home.models import HomePage

migration = import_module("webapp.home.migrations.0006_correct_support_engineer_title")


class SupportEngineerTitleMigrationTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.get(slug="home")
        for field, (old, new) in migration.COPY_UPDATES.items():
            setattr(self.home, field, old)
        self.older_revision = self.home.save_revision()
        self.older_revision.publish()
        self.home.hero_title = "An edited hero"
        self.live_revision = self.home.save_revision()
        self.live_revision.publish()
        self.editor = SimpleNamespace(connection=connection)
        self.migration_apps = (
            MigrationLoader(connection)
            .project_state([("home", "0006_correct_support_engineer_title")])
            .apps
        )

    def test_live_and_current_draft_are_corrected_without_publishing(self):
        self.home.introduction = "<p>Custom draft introduction.</p>"
        draft = self.home.save_revision()
        count = Revision.objects.count()
        migration.correct_titles(self.migration_apps, self.editor)
        self.home.refresh_from_db()
        self.assertEqual(self.home.role, "Support Engineer at Torchbox")
        self.assertEqual(self.home.headline, "Support Engineer: loving Wagtail CMS")
        self.assertIn(
            "an engineer working in the support team at", self.home.introduction
        )
        self.assertIn(
            "an engineer working in the support team at", self.home.about_body
        )
        self.assertTrue(self.home.has_unpublished_changes)
        self.assertEqual(Revision.objects.count(), count)
        draft.refresh_from_db()
        self.assertEqual(draft.content["role"], "Support Engineer at Torchbox")
        self.assertEqual(
            draft.content["introduction"], "<p>Custom draft introduction.</p>"
        )
        self.live_revision.refresh_from_db()
        self.assertEqual(
            self.live_revision.content["role"], "Support Engineer at Torchbox"
        )
        self.older_revision.refresh_from_db()
        self.assertEqual(
            self.older_revision.content["role"], "Software Engineer at Torchbox"
        )

    def test_customised_content_is_preserved(self):
        for field in migration.COPY_UPDATES:
            setattr(self.home, field, f"Custom {field}")
        revision = self.home.save_revision()
        revision.publish()
        migration.correct_titles(self.migration_apps, self.editor)
        self.home.refresh_from_db()
        revision.refresh_from_db()
        for field in migration.COPY_UPDATES:
            self.assertEqual(getattr(self.home, field), f"Custom {field}")
            self.assertEqual(revision.content[field], f"Custom {field}")

    def test_correction_is_reversible(self):
        migration.correct_titles(self.migration_apps, self.editor)
        migration.restore_titles(self.migration_apps, self.editor)
        self.home.refresh_from_db()
        self.live_revision.refresh_from_db()
        for field, (old, new) in migration.COPY_UPDATES.items():
            self.assertEqual(getattr(self.home, field), old)
            self.assertEqual(self.live_revision.content[field], old)
