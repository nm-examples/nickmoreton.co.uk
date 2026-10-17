from bs4 import BeautifulSoup
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.text import slugify


def render_body(body, request):
    html = render_to_string("pages/includes/body.html", {"body": body}, request=request)
    soup = BeautifulSoup(html, "html.parser")
    headings = soup.find_all(["h2", "h3"])
    reserved = {heading["id"] for heading in headings if heading.has_attr("id")}
    used = {
        element["id"] for element in soup.find_all(id=True) if element not in headings
    }
    toc = []
    for heading in headings:
        title = heading.get_text(" ", strip=True)
        base = heading.get("id") or slugify(title) or "section"
        anchor = base
        suffix = 2
        while anchor in used or (anchor in reserved and anchor != heading.get("id")):
            anchor = f"{base}-{suffix}"
            suffix += 1
        used.add(anchor)
        heading["id"] = anchor
        toc.append({"id": anchor, "title": title, "level": heading.name})
    return {"rendered_body": mark_safe(str(soup)), "table_of_contents": toc}
