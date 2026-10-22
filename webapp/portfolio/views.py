from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.decorators.http import require_http_methods, require_POST
from wagtail.admin import messages
from wagtail.admin.auth import require_admin_access
from wagtail.admin.views.generic.models import IndexView
from wagtail.admin.widgets.button import Button, HeaderButton

from .forms import ProjectImportForm
from .importing import save_import
from .models import PortfolioSourceRecord
from .source import TEXT_FIELDS, SourceError, refresh_sources


class RefreshButton(HeaderButton):
    template_name = "portfolio/admin/refresh_button.html"


class SourceIndexView(IndexView):
    page_title = "Source records"
    add_url = None

    @cached_property
    def header_buttons(self):
        if self.request.user.has_perm("portfolio.refresh_portfoliosource"):
            return [
                RefreshButton(
                    "Refresh from GitHub",
                    icon_name="download",
                    attrs={"type": "submit", "form": "portfolio-source-refresh"},
                )
            ]
        return []

    def get_queryset(self):
        return super().get_queryset().select_related("project")

    def get_edit_url(self, instance):
        permission = "change" if instance.project_id else "add"
        if not instance.missing_upstream and self.request.user.has_perm(
            f"portfolio.{permission}_portfolioproject"
        ):
            return reverse("portfolio_sources:review", args=[instance.pk])

    def get_list_buttons(self, instance):
        if url := self.get_edit_url(instance):
            yield Button(
                "Review source changes" if instance.project_id else "Create snippet",
                url=url,
            )


@require_admin_access
@permission_required("portfolio.refresh_portfoliosource", raise_exception=True)
@permission_required("portfolio.view_portfoliosourcerecord", raise_exception=True)
@require_POST
def refresh(request):
    try:
        count = refresh_sources()
    except SourceError as error:
        messages.error(request, str(error))
    else:
        messages.success(
            request,
            f"Refreshed {count} source records. Project snippets are unchanged.",
        )
    return redirect("portfolio_sources:index")


@require_admin_access
@permission_required("portfolio.view_portfoliosourcerecord", raise_exception=True)
@require_http_methods(["GET", "POST"])
def review(request, pk):
    record = get_object_or_404(
        PortfolioSourceRecord.objects.select_related("project"), pk=pk
    )
    permission = "change" if record.project_id else "add"
    if not request.user.has_perm(f"portfolio.{permission}_portfolioproject"):
        raise PermissionDenied
    project = (
        record.project.get_latest_revision_as_object() if record.project_id else None
    )
    initial = {
        **{field: record.data.get(field, "") for field in TEXT_FIELDS},
        "source_fingerprint": record.fingerprint,
        "project_revision": str(project.latest_revision_id or "") if project else "",
        "apply_fields": [] if project else list(TEXT_FIELDS),
        "import_image": not project
        and request.user.has_perm("wagtailimages.add_image"),
    }
    form = ProjectImportForm(
        request.POST if request.method == "POST" else None, initial=initial
    )
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["import_image"] and not request.user.has_perm(
            "wagtailimages.add_image"
        ):
            raise PermissionDenied
        try:
            updated = save_import(record.pk, form.cleaned_data, request.user)
        except (SourceError, ValidationError) as error:
            form.add_error(None, str(error))
        else:
            messages.success(
                request, "Saved a project draft. Review and publish it when ready."
            )
            return redirect(
                "wagtailsnippets_portfolio_portfolioproject:edit", updated.pk
            )
    rows = [
        {
            "label": field.replace("_", " ").capitalize(),
            "previous": record.last_applied_data.get(field, "—"),
            "current": getattr(project, field) if project else "—",
            "incoming": record.data.get(field, ""),
        }
        for field in TEXT_FIELDS
    ]
    return render(
        request,
        "portfolio/admin/review.html",
        {
            "record": record,
            "header_title": f"Review {record.title}",
            "header_icon": "image",
            "breadcrumbs_items": [
                {"url": reverse("wagtailadmin_home"), "label": "Home"},
                {"url": reverse("portfolio_sources:index"), "label": "Source records"},
                {"url": "", "label": record.title},
            ],
            "project": project,
            "form": form,
            "rows": rows,
            "project_edit_url": reverse(
                "wagtailsnippets_portfolio_portfolioproject:edit", args=[project.pk]
            )
            if project
            else None,
        },
    )
