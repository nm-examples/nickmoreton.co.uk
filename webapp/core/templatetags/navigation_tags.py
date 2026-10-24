from django import template
from wagtail.models import Site

from webapp.core.models import Navigation

register = template.Library()


@register.inclusion_tag("core/tags/navigation.html", takes_context=True)
def get_navigation(context: template.Context) -> dict:
    """Keep configured order, falling back to root menu pages and section links.

    Skip unpublished/restricted targets and links to an empty work section. Homepage
    previews use their draft project selection; other pages use the live site root.
    """
    request = context["request"]
    navigation = Navigation.for_request(request)
    site = Site.find_for_request(request)
    root = site.root_page.specific if site else None
    current_page = context.get("page")
    homepage = (
        current_page if current_page and root and current_page.pk == root.pk else root
    )
    has_projects = bool(getattr(homepage, "selected_projects", []))
    root_url = (root.get_url(request) if root else None) or "/"
    work_url = request.build_absolute_uri(root_url + "#work")
    items = []
    for block in navigation.main_menu:
        value = block.value
        page = value.get("page")
        if page and (not page.live or page.get_view_restrictions().exists()):
            continue
        url = page.get_url(request) if page else value.get("url")
        if value.get("anchor"):
            url = url or root_url
            url += "#" + value["anchor"]
        if url:
            if not has_projects and request.build_absolute_uri(url) == work_url:
                continue
            items.append({"label": value["label"], "url": url})
    if not items and root:
        if has_projects:
            items.append({"label": "Websites", "url": root_url + "#work"})
        items += [
            {"label": page.title, "url": page.get_url(request)}
            for page in root.get_children().live().public()
            if page.show_in_menus
        ]
        items.append({"label": "About", "url": root_url + "#about"})
    ctx = {
        "request": request,
        "main_menu": items,
    }
    return ctx
