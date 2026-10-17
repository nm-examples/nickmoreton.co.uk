from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from wagtail.models import Page, Site


def search(request):
    search_query = request.GET.get("query", "").strip()
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        pages = Page.objects.live().public()
        site = Site.find_for_request(request)
        if site:
            pages = pages.descendant_of(site.root_page, inclusive=True)
        search_results = pages.search(search_query)
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
        },
    )
