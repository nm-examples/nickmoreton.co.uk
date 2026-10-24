import random

from django.db import models
from django.utils.functional import cached_property
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.models import register_snippet

from webapp.pages.models import (
    ArticleIndexPage,
    ArticlePage,
    PackageIndexPage,
    PackagePage,
)


@register_snippet
class PortfolioProject(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    image_description = models.CharField(max_length=255)
    record_url = models.URLField(max_length=2000)

    panels = [
        FieldPanel("title"),
        FieldPanel("category"),
        FieldPanel("description"),
        FieldPanel("image"),
        FieldPanel("image_description"),
        FieldPanel("record_url"),
    ]

    class Meta:
        ordering = ["title", "pk"]

    def __str__(self) -> str:
        return self.title


class HomePage(Page):
    max_count = 1
    introduction = RichTextField(
        features=["bold", "italic", "link"],
    )
    project_selection = StreamField(
        [("project", SnippetChooserBlock("home.PortfolioProject"))],
        blank=True,
        help_text="Choose and order projects managed in Snippets → Portfolio projects.",
    )
    about_body = RichTextField(
        features=["bold", "italic", "link"],
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("about_body", heading="About"),
        MultiFieldPanel(
            [FieldPanel("project_selection")],
            heading="Past website projects",
        ),
    ]

    @cached_property
    def selected_projects(self) -> list[PortfolioProject]:
        """Keep the chosen order and omit references to deleted snippets."""
        return [
            block.value for block in self.project_selection if block.value is not None
        ]

    @property
    def hero_project(self) -> PortfolioProject | None:
        """Use the grid's selection; consecutive requests may show the same project."""
        return random.choice(self.selected_projects) if self.selected_projects else None

    def all_articles(self):
        return (
            ArticlePage.objects.live()
            .public()
            .descendant_of(self)
            .order_by("homepage_order", "-date", "-pk")
        )

    def all_packages(self):
        return (
            PackagePage.objects.live()
            .public()
            .descendant_of(self)
            .order_by("homepage_order", "-date", "-pk")
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(
            all_articles=self.all_articles(),
            all_packages=self.all_packages(),
            article_index=ArticleIndexPage.objects.live()
            .public()
            .descendant_of(self)
            .first(),
            package_index=PackageIndexPage.objects.live()
            .public()
            .descendant_of(self)
            .first(),
        )
        return context
