from django.contrib.auth.models import Permission
from django.urls import path
from wagtail import hooks
from wagtail.admin.menu import MenuItem, WagtailMenuRegisterableGroup
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from . import views
from .models import PortfolioProject, PortfolioSourceRecord


class ProjectViewSet(SnippetViewSet):
    model = PortfolioProject
    icon = "image"
    menu_label = "Projects"
    menu_item_is_registered = True
    list_display = ("title", "category", "show_in_hero")
    list_filter = ("show_in_hero", "live")
    search_fields = ("title", "description")


project_viewset = ProjectViewSet()
register_snippet(project_viewset)


class SourceMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.has_perm("portfolio.view_portfoliosourcerecord")


class SourceViewSet(ModelViewSet):
    name = "portfolio_sources"
    model = PortfolioSourceRecord
    menu_label = "Source records"
    icon = "download"
    menu_item_class = SourceMenuItem
    index_view_class = views.SourceIndexView
    index_template_name = "portfolio/admin/source_index.html"
    list_display = ("title", "status", "fetched_at", "project")
    list_filter = ("missing_upstream",)
    search_fields = ("title", "source_path")
    form_fields = ()

    def get_urlpatterns(self):
        return [
            path("", self.index_view, name="index"),
            path("results/", self.index_results_view, name="index_results"),
            path("refresh/", views.refresh, name="refresh"),
            path("<int:pk>/review/", views.review, name="review"),
        ]


source_viewset = SourceViewSet()


class PortfolioMenu(WagtailMenuRegisterableGroup):
    menu_label = "Portfolio"
    menu_icon = "image"
    menu_order = 250
    items = (project_viewset, source_viewset)


@hooks.register("register_admin_viewset")
def register_sources():
    return source_viewset


@hooks.register("register_admin_menu_item")
def portfolio_menu():
    return PortfolioMenu().get_menu_item()


@hooks.register("register_permissions")
def source_permissions():
    return Permission.objects.filter(
        content_type__app_label="portfolio", content_type__model="portfoliosourcerecord"
    )
