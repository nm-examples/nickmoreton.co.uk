from django import template
from wagtail.models import Site

from webapp.core.models import Navigation

register = template.Library()


@register.inclusion_tag("core/tags/navigation.html", takes_context=True)
def get_navigation(context):
    navigation = Navigation.for_request(context["request"])
    site = Site.find_for_request(context["request"])
    root = site.root_page.specific if site else None
    items = []
    for block in navigation.main_menu:
        value = block.value
        page = value.get("page")
        if page and (not page.live or page.get_view_restrictions().exists()):
            continue
        url = page.get_url(context["request"]) if page else value.get("url")
        if value.get("anchor"):
            url = url or (root.get_url(context["request"]) if root else "/")
            url += "#" + value["anchor"]
        if url:
            items.append({"label": value["label"], "url": url})
    if not items and root:
        items = [
            {"label": "Websites", "url": root.get_url(context["request"]) + "#work"}
        ]
        items += [
            {"label": page.title, "url": page.get_url(context["request"])}
            for page in root.get_children().live().public()
            if page.show_in_menus
        ]
        items.append(
            {"label": "About", "url": root.get_url(context["request"]) + "#about"}
        )
    ctx = {
        "request": context["request"],
        "main_menu": items,
        "profile": root,
    }
    return ctx
