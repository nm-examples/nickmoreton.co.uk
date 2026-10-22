import json

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models
from django.utils import timezone
from modelcluster.models import get_serializable_data_for_fields

PROJECT_FIELDS = (
    "title",
    "category",
    "description",
    "image",
    "image_description",
    "record_url",
)


def blocks_list(value):
    if hasattr(value, "get_prep_value"):
        return value.get_prep_value()
    return json.loads(value) if isinstance(value, str) else (value or [])


def move_projects(apps, schema_editor):
    database = schema_editor.connection.alias
    Home = apps.get_model("home", "HomePage")
    Selection = apps.get_model("home", "HomePagePortfolioProject")
    Project = apps.get_model("portfolio", "PortfolioProject")
    Revision = apps.get_model("wagtailcore", "Revision")
    ContentType = apps.get_model("contenttypes", "ContentType")
    Image = apps.get_model("wagtailimages", "Image")
    project_type, _ = ContentType.objects.using(database).get_or_create(
        app_label="portfolio", model="portfolioproject"
    )
    home_type, _ = ContentType.objects.using(database).get_or_create(
        app_label="home", model="homepage"
    )
    images = set(Image.objects.using(database).values_list("pk", flat=True))
    projects = {}

    def selections(blocks, home_id, live=False, persist=False):
        rows = []
        seen = set()
        for block in blocks_list(blocks):
            values = {field: block["value"].get(field, "") for field in PROJECT_FIELDS}
            if values["image"] not in images:
                values["image"] = None
            key = json.dumps(values, sort_keys=True)
            project = projects.get(key)
            if project is None:
                image_id = values.pop("image")
                project = Project.objects.using(database).create(
                    **values,
                    image_id=image_id,
                    live=live,
                    show_in_hero=live,
                    has_unpublished_changes=not live,
                )
                revision = Revision.objects.using(database).create(
                    content_type_id=project_type.pk,
                    base_content_type_id=project_type.pk,
                    object_id=str(project.pk),
                    object_str=project.title,
                    created_at=timezone.now(),
                    content=get_serializable_data_for_fields(project),
                )
                project.latest_revision_id = revision.pk
                if live:
                    project.live_revision_id = revision.pk
                project.save(
                    using=database, update_fields=["latest_revision", "live_revision"]
                )
                projects[key] = project
            if project.pk in seen:
                continue
            seen.add(project.pk)
            row = {
                "pk": None,
                "page": home_id,
                "project": project.pk,
                "sort_order": len(rows),
            }
            if persist:
                row["pk"] = (
                    Selection.objects.using(database)
                    .create(
                        page_id=home_id,
                        project_id=project.pk,
                        sort_order=row["sort_order"],
                    )
                    .pk
                )
            rows.append(row)
        return rows

    # Seed current live values first, so historical/draft-only content is never
    # made eligible for the hero or published by this migration.
    homes = list(Home.objects.using(database).all())
    for home in homes:
        selections(home.projects, home.pk, live=home.live, persist=True)
    for home in homes:
        for revision in (
            Revision.objects.using(database)
            .filter(content_type_id=home_type.pk, object_id=str(home.pk))
            .iterator()
        ):
            content = dict(revision.content)
            content["portfolio_items"] = selections(
                content.pop("projects", []), home.pk
            )
            Revision.objects.using(database).filter(pk=revision.pk).update(
                content=content
            )


def restore_projects(apps, schema_editor):
    database = schema_editor.connection.alias
    Home = apps.get_model("home", "HomePage")
    Selection = apps.get_model("home", "HomePagePortfolioProject")
    Project = apps.get_model("portfolio", "PortfolioProject")
    Revision = apps.get_model("wagtailcore", "Revision")
    projects = {
        project.pk: project for project in Project.objects.using(database).all()
    }

    def blocks(rows):
        result = []
        for row in rows:
            project = projects.get(row["project"])
            if project:
                values = {
                    field: getattr(
                        project, f"{field}_id" if field == "image" else field
                    )
                    for field in PROJECT_FIELDS
                }
                values["featured"] = project.show_in_hero
                result.append({"type": "project", "value": values})
        return result

    for home in Home.objects.using(database).all():
        rows = (
            Selection.objects.using(database)
            .filter(page_id=home.pk)
            .order_by("sort_order")
            .values("project")
        )
        Home.objects.using(database).filter(pk=home.pk).update(projects=blocks(rows))
        for revision in (
            Revision.objects.using(database)
            .filter(
                content_type__app_label="home",
                content_type__model="homepage",
                object_id=str(home.pk),
            )
            .iterator()
        ):
            content = dict(revision.content)
            content["projects"] = blocks(content.pop("portfolio_items", []))
            Revision.objects.using(database).filter(pk=revision.pk).update(
                content=content
            )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0006_correct_support_engineer_title"),
        ("portfolio", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePagePortfolioProject",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portfolio_items",
                        to="home.homepage",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="homepage_selections",
                        to="portfolio.portfolioproject",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"]},
        ),
        migrations.AddConstraint(
            model_name="homepageportfolioproject",
            constraint=models.UniqueConstraint(
                fields=("page", "project"), name="unique_homepage_project"
            ),
        ),
        migrations.RunPython(move_projects, restore_projects),
        migrations.RemoveField(model_name="homepage", name="projects"),
    ]
