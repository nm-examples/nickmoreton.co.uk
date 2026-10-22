import json
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.images import get_image_model
from wagtail.models import Site

from webapp.core.models import Navigation
from webapp.home.models import HomePage, HomePagePortfolioProject
from webapp.pages.models import ArticlePage, PackagePage
from webapp.portfolio.models import PortfolioProject


class Command(BaseCommand):
    help = "Populate missing redesign portfolio and metadata. Dry run unless --apply is supplied."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--home-id", type=int)

    def handle(self, *args, **options):
        homes = HomePage.objects.all()
        if options["home_id"]:
            homes = homes.filter(pk=options["home_id"])
        if homes.count() != 1:
            raise CommandError("Select exactly one homepage with --home-id.")
        home = homes.get()
        data = json.loads(
            (Path(__file__).parents[2] / "data/redesign.json").read_text()
        )
        source = Path(settings.PROJECT_DIR) / "static_src/img"
        if not home.portfolio_items.exists():
            for project in data["projects"]:
                if not (source / project["image"]).is_file():
                    raise CommandError(f"Missing portfolio image: {project['image']}")
        if not options["apply"]:
            self.stdout.write(
                f"Dry run: populate missing portfolio, navigation, and metadata below {home.title} ({home.pk})."
            )
            self.stdout.write(
                "Existing portfolio, metadata, page bodies, and unpublished drafts are preserved. Use --apply to save."
            )
            return
        with transaction.atomic():
            self.populate_home(home, data, source)
            self.populate_pages(home, ArticlePage, data["articles"])
            self.populate_pages(home, PackagePage, data["packages"])
            self.populate_navigation(home)
        self.stdout.write(
            self.style.SUCCESS(
                "Redesign content populated; existing content preserved."
            )
        )

    def populate_home(self, home, data, source):
        if home.portfolio_items.exists():
            return
        if home.has_unpublished_changes or not home.live:
            self.stdout.write(
                self.style.WARNING("Skipped homepage: unpublished changes or not live.")
            )
            return
        image_model = get_image_model()
        for index, project in enumerate(data["projects"]):
            values = dict(project)
            image = image_model.objects.filter(
                title=f"Portfolio: {project['title']}"
            ).first()
            if image is None:
                with (source / project["image"]).open("rb") as image_file:
                    image = image_model(
                        title=f"Portfolio: {project['title']}",
                        file=File(image_file, name=project["image"]),
                    )
                    image.save()
            values["image"] = image
            # Preserve the previous random-hero behaviour for supplied projects.
            snippet = PortfolioProject.objects.filter(
                record_url=values["record_url"]
            ).first()
            if snippet is None:
                snippet = PortfolioProject(**values, show_in_hero=True, live=False)
                snippet.save()
                snippet.save_revision().publish()
                snippet.refresh_from_db()
            home.portfolio_items.add(
                HomePagePortfolioProject(project=snippet, sort_order=index)
            )
        home.save_revision().publish()
        self.stdout.write("Added four portfolio projects to the homepage.")

    def populate_pages(self, home, model, records):
        for record in records:
            page = (
                model.objects.live()
                .descendant_of(home)
                .filter(slug=record["slug"])
                .first()
            )
            if page is None:
                self.stdout.write(
                    self.style.WARNING(f"No published page found for {record['slug']}.")
                )
                continue
            if page.has_unpublished_changes:
                self.stdout.write(
                    self.style.WARNING(f"Skipped draft changes: {page.title}.")
                )
                continue
            changed = False
            for field, value in record.items():
                if field == "slug":
                    continue
                current = getattr(page, field)
                default = page._meta.get_field(field).get_default()
                if not current or current == default:
                    if current != value:
                        setattr(page, field, value)
                        changed = True
            if changed:
                page.save_revision().publish()
                self.stdout.write(f"Added missing metadata: {page.title}.")

    def populate_navigation(self, home):
        for site in Site.objects.filter(root_page=home):
            navigation = Navigation.for_site(site)
            items = [
                (block.block_type, dict(block.value)) for block in navigation.main_menu
            ]
            changed = False
            for label, anchor in [("Websites", "work"), ("About", "about")]:
                if not any(value.get("anchor") == anchor for _, value in items):
                    item = (
                        "main_menu",
                        {"label": label, "page": home, "anchor": anchor, "url": ""},
                    )
                    if anchor == "work":
                        items.insert(0, item)
                    else:
                        items.append(item)
                    changed = True
            if changed:
                navigation.main_menu = items
                navigation.save()
                self.stdout.write(f"Added homepage section links for {site.hostname}.")
