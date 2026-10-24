import json
import random

from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from webapp.home.blocks import PortfolioProjectBlock
from webapp.pages.blocks import BaseBlocks
from webapp.pages.models import (
    ArticleIndexPage,
    ArticlePage,
    PackageIndexPage,
    PackagePage,
)


class HomePage(Page):
    max_count = 1
    body = StreamField(
        BaseBlocks,
        blank=True,
    )

    profile_name = models.CharField(max_length=100)
    role = models.CharField(max_length=150)
    hero_title = models.TextField()
    hero_highlight = models.TextField()
    headline = models.CharField(max_length=255)
    introduction = RichTextField(
        features=["bold", "italic", "link"],
    )
    employer_url = models.URLField()
    cms_url = models.URLField()
    github_url = models.URLField()
    linkedin_url = models.URLField()
    portfolio_url = models.URLField()
    projects = StreamField([("project", PortfolioProjectBlock())], blank=True)
    about_heading = models.TextField()
    about_title = models.CharField(max_length=150)
    about_body = RichTextField(
        features=["bold", "italic", "link"],
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel(name)
                for name in (
                    "profile_name",
                    "role",
                    "hero_title",
                    "hero_highlight",
                    "headline",
                    "introduction",
                    "employer_url",
                    "cms_url",
                )
            ],
            heading="Introduction",
        ),
        MultiFieldPanel(
            [FieldPanel("projects"), FieldPanel("portfolio_url")],
            heading="Past website projects",
        ),
        MultiFieldPanel(
            [
                FieldPanel(name)
                for name in (
                    "about_title",
                    "about_heading",
                    "about_body",
                    "github_url",
                    "linkedin_url",
                )
            ],
            heading="About and profiles",
        ),
        MultiFieldPanel(
            [FieldPanel("body")],
            heading="Legacy homepage content",
            help_text="Retained for reference; the redesigned homepage uses the fields above.",
        ),
    ]

    @property
    def yaml_name(self):
        return json.dumps(self.profile_name, ensure_ascii=False)

    @property
    def profile_yaml(self):
        return (
            f"who_am_i:\n  name: {self.yaml_name}\n"
            f"  works_at: {self.employer_url}\n  preferred_cms: {self.cms_url}"
        )

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
