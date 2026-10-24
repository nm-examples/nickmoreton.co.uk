from bs4 import BeautifulSoup
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.text import slugify

# IDs rendered outside the body by base.html and core/tags/navigation.html.
SHARED_TEMPLATE_IDS = {"main", "navigation"}


def render_body(body, request):
    """Render body HTML and matching h2/h3 contents links with unique anchors."""
    html = render_to_string("pages/includes/body.html", {"body": body}, request=request)
    soup = BeautifulSoup(html, "html.parser")
    used_ids = set(SHARED_TEMPLATE_IDS)
    toc = []
    for heading in soup.find_all(["h2", "h3"]):
        title = heading.get_text(" ", strip=True)
        base = slugify(title) or "section"
        anchor = base
        suffix = 2
        while anchor in used_ids:
            anchor = f"{base}-{suffix}"
            suffix += 1
        used_ids.add(anchor)
        heading["id"] = anchor
        toc.append({"id": anchor, "title": title, "level": heading.name})
    return {"rendered_body": mark_safe(str(soup)), "table_of_contents": toc}
