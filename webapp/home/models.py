import random

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from webapp.home.blocks import PortfolioProjectBlock
from webapp.pages.models import (
    ArticleIndexPage,
    ArticlePage,
    PackageIndexPage,
    PackagePage,
)


class HomePage(Page):
    max_count = 1
    introduction = RichTextField(
        features=["bold", "italic", "link"],
    )
    projects = StreamField([("project", PortfolioProjectBlock())], blank=True)
    about_body = RichTextField(
        features=["bold", "italic", "link"],
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("about_body", heading="About"),
        MultiFieldPanel(
            [FieldPanel("projects")],
            heading="Past website projects",
        ),
    ]

    @property
    def hero_project(self):
        projects = [block.value for block in self.projects]
        return random.choice(projects) if projects else None

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
