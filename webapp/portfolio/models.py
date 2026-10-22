from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PublishingPanel
from wagtail.models import DraftStateMixin, RevisionMixin
from wagtail.search import index


class PortfolioProject(DraftStateMixin, RevisionMixin, index.Indexed, models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    image_description = models.CharField(max_length=255, blank=True)
    website_url = models.URLField(blank=True)
    record_url = models.URLField(blank=True)
    show_in_hero = models.BooleanField(default=False)

    panels = [
        FieldPanel("title"),
        FieldPanel("category"),
        FieldPanel("description"),
        MultiFieldPanel(
            [FieldPanel("image"), FieldPanel("image_description")], heading="Screenshot"
        ),
        FieldPanel("website_url"),
        FieldPanel("record_url"),
        FieldPanel("show_in_hero"),
        PublishingPanel(),
    ]
    search_fields = [index.SearchField("title"), index.SearchField("description")]

    class Meta:
        ordering = ["title", "pk"]

    def __str__(self):
        return self.title


class PortfolioSourceRecord(models.Model):
    source_path = models.CharField(max_length=500, unique=True)
    title = models.CharField(max_length=255)
    raw_markdown = models.TextField()
    metadata = models.JSONField(default=dict)
    data = models.JSONField(default=dict)
    fingerprint = models.CharField(max_length=64)
    commit_sha = models.CharField(max_length=40)
    fetched_at = models.DateTimeField()
    missing_upstream = models.BooleanField(default=False)
    project = models.OneToOneField(
        PortfolioProject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="source_record",
    )
    last_applied_data = models.JSONField(default=dict, blank=True)
    last_applied_fingerprint = models.CharField(max_length=64, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["title", "pk"]
        default_permissions = ("view",)
        permissions = [
            ("refresh_portfoliosource", "Can refresh portfolio data from GitHub"),
        ]

    def __str__(self):
        return self.title

    @property
    def status(self):
        if self.missing_upstream:
            return "Missing upstream"
        if not self.project_id:
            return "New"
        if not self.last_applied_fingerprint:
            return "Not yet reviewed"
        if self.fingerprint != self.last_applied_fingerprint:
            return "Source changed"
        return "Up to date"
