from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from webapp.pages.blocks import BaseBlocks
from webapp.pages.content import render_body


# ABSTRACT MODELS
class BasePage(Page):
    class Meta:
        abstract = True


# ARTICLE MODELS
class ArticleIndexPage(BasePage):
    subpage_types = ["pages.ArticlePage"]
    body = StreamField(
        BaseBlocks,
        blank=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["articles"] = (
            ArticlePage.objects.live()
            .public()
            .descendant_of(self)
            .order_by("-date", "-pk")
        )
        return context


class ArticlePageBase(BasePage):
    body = StreamField(
        BaseBlocks,
        blank=True,
    )
    excerpt = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    def get_latest_articles(self):
        article = self.get_parent() if isinstance(self, ArticleChapterPage) else self
        return (
            ArticlePage.objects.live()
            .public()
            .sibling_of(article)
            .exclude(id=article.id)
            .order_by("-date", "-pk")[:3]
        )

    def get_context(self, request):
        context = super().get_context(request)
        context["latest_articles"] = self.get_latest_articles()
        context.update(render_body(self.body, request))
        return context

    def get_chapters(self):
        chapters = ArticleChapterPage.objects.live().public().child_of(self)
        return chapters

    def get_first_chapter(self):
        chapters = self.get_chapters()
        return chapters.first()

    base_panels_top = [
        FieldPanel("excerpt"),
    ]

    base_panels_bottom = [
        FieldPanel("body"),
    ]


class ArticlePage(ArticlePageBase):
    subpage_types = ["pages.ArticleChapterPage"]
    date = models.DateField("Article published date")
    topic = models.CharField(max_length=100, blank=True)
    repository_url = models.URLField(blank=True)
    homepage_order = models.PositiveIntegerField(default=100)

    panels_top = [
        MultiFieldPanel(
            ArticlePageBase.base_panels_top
            + [
                FieldPanel("date"),
                FieldPanel("topic"),
                FieldPanel("repository_url"),
                FieldPanel("homepage_order"),
            ],
            heading="Article information",
        )
    ]

    panels_bottom = [
        FieldPanel("body"),
    ]

    content_panels = Page.content_panels + panels_top + panels_bottom

    def get_context(self, request):
        context = super().get_context(request)
        context["chapters"] = self.get_chapters()
        context["first_chapter"] = self.get_first_chapter()
        return context


class ArticleChapterPage(ArticlePageBase):
    subpage_types = []

    panels_bottom = ArticlePageBase.base_panels_bottom

    content_panels = Page.content_panels + panels_bottom

    def get_chapters(self):
        chapters = (
            ArticleChapterPage.objects.live().public().child_of(self.get_parent())
        )
        return chapters

    def get_next_chapter(self):
        chapters = self.get_chapters()
        return chapters.filter(path__gt=self.path).first()

    def get_previous_chapter(self):
        chapters = self.get_chapters()
        return chapters.filter(path__lt=self.path).last()

    def get_context(self, request):
        context = super().get_context(request)
        context["article"] = self.get_parent().specific
        context["chapters"] = self.get_chapters()
        context["current_chapter"] = self
        context["next_chapter"] = self.get_next_chapter()
        context["previous_chapter"] = self.get_previous_chapter()
        return context


# PACKAGE MODELS
class PackageIndexPage(BasePage):
    subpage_types = ["pages.PackagePage"]
    body = StreamField(
        BaseBlocks,
        blank=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["packages"] = (
            PackagePage.objects.live()
            .public()
            .descendant_of(self)
            .order_by("-date", "-pk")
        )
        return context


class PackagePage(BasePage):
    parent_page_types = ["pages.PackageIndexPage"]
    body = StreamField(
        BaseBlocks,
        blank=True,
    )
    date = models.DateField("Package published date")
    excerpt = models.CharField(max_length=255, blank=True)
    pypi_package_name = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)
    repository_url = models.URLField(blank=True)
    homepage_order = models.PositiveIntegerField(default=100)
    featured = models.BooleanField(default=False)
    card_icon = models.CharField(
        max_length=10,
        choices=[("{ }", "Code"), ("◇", "Forms"), ("Tt", "Content"), ("▦", "QR code")],
        default="{ }",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("date"),
        FieldPanel("excerpt"),
        FieldPanel("pypi_package_name"),
        MultiFieldPanel(
            [
                FieldPanel(name)
                for name in (
                    "category",
                    "repository_url",
                    "homepage_order",
                    "featured",
                    "card_icon",
                )
            ],
            heading="Presentation and links",
        ),
    ]

    def get_latest_packages(self):
        packages = (
            PackagePage.objects.live()
            .public()
            .sibling_of(self)
            .exclude(id=self.id)
            .order_by("-date", "-pk")
        )
        return packages[:3]

    def get_context(self, request):
        context = super().get_context(request)
        context["latest_packages"] = self.get_latest_packages()
        context.update(render_body(self.body, request))
        return context
