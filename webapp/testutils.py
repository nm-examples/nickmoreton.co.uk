from datetime import date

from wagtail.search.backends import get_search_backend

from webapp.home.models import HomePage
from webapp.pages.models import (
    ArticleChapterPage,
    ArticleIndexPage,
    ArticlePage,
    PackageIndexPage,
    PackagePage,
)


def publish(parent, page):
    parent.add_child(instance=page)
    page.save_revision().publish()
    # Search updates normally run on commit, outside TestCase transactions.
    get_search_backend().add(page)
    return page


def content_tree():
    home = HomePage.objects.get(slug="home")
    articles = publish(
        home, ArticleIndexPage(title="Articles", slug="articles", show_in_menus=True)
    )
    packages = publish(
        home, PackageIndexPage(title="Packages", slug="packages", show_in_menus=True)
    )
    article = publish(
        articles,
        ArticlePage(
            title="Example article",
            slug="example-article",
            date=date(2026, 1, 1),
            excerpt="Article introduction",
            topic="Wagtail / Tools",
            body=[
                ("heading", {"heading": "Getting started", "level": "h2"}),
                ("rich_text", "<p>Some article text.</p>"),
            ],
        ),
    )
    chapter = publish(
        article,
        ArticleChapterPage(
            title="First chapter",
            slug="first-chapter",
            body=[("rich_text", "<h2>Chapter contents</h2><p>Chapter text.</p>")],
        ),
    )
    package = publish(
        packages,
        PackagePage(
            title="Example package",
            slug="example-package",
            date=date(2026, 1, 1),
            excerpt="Package introduction",
            pypi_package_name="example-package",
        ),
    )
    return home, articles, packages, article, chapter, package
