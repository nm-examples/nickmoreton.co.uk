from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import PortfolioProject


class ProjectViewSet(SnippetViewSet):
    model = PortfolioProject
    icon = "image"
    list_display = ("title", "category", "show_in_hero")
    list_filter = ("show_in_hero", "live")
    search_fields = ("title", "description")


register_snippet(ProjectViewSet)
