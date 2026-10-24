from datetime import date

from django.test import RequestFactory, TestCase
from wagtail.models import Page, PageViewRestriction

from webapp.pages.models import (
    ArticleChapterPage,
    ArticleIndexPage,
    ArticlePage,
    PackageIndexPage,
    PackagePage,
)


class ContentQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.get_first_root_node()
        cls.examples = []
        for index_model, model, key in (
            (ArticleIndexPage, ArticlePage, "articles"),
            (PackageIndexPage, PackagePage, "packages"),
        ):
            index = root.add_child(instance=index_model(title=f"Query {key}"))
            other_index = root.add_child(instance=index_model(title=f"Other {key}"))

            def page(title: str, day: int, **values):
                return index.add_child(
                    instance=model(title=title, date=date(2026, 10, day), **values)
                )

            current = page("Current", 24)
            oldest = page("Oldest", 1, homepage_order=0)
            recent = page("Recent", 20)
            tie_first = page("First tie", 23, homepage_order=1)
            tie_last = page("Last tie", 23, homepage_order=200)
            page("Draft", 25, live=False)
            restricted = page("Restricted", 26)
            PageViewRestriction.objects.create(
                page=restricted, restriction_type="login"
            )
            other_index.add_child(
                instance=model(title="Outside index", date=date(2026, 10, 27))
            )
            cls.examples.append(
                {
                    "index": index,
                    "current": current,
                    "key": key,
                    "listing": [current, tie_last, tie_first, recent, oldest],
                    "related": [tie_last, tie_first, recent],
                }
            )
            if model is ArticlePage:
                cls.chapter = current.add_child(
                    instance=ArticleChapterPage(title="Chapter")
                )

    def test_indexes_scope_visible_content_and_order_by_date_then_id(self):
        for example in self.examples:
            with self.subTest(kind=example["key"]):
                context = example["index"].get_context(RequestFactory().get("/"))
                self.assertEqual(list(context[example["key"]]), example["listing"])

    def test_related_lists_limit_visible_siblings_and_exclude_current_page(self):
        for example in self.examples:
            with self.subTest(kind=example["key"]):
                context = example["current"].get_context(RequestFactory().get("/"))
                self.assertEqual(
                    list(context[f"latest_{example['key']}"]), example["related"]
                )

    def test_chapter_uses_parent_articles_related_list(self):
        self.assertEqual(
            list(self.chapter.get_latest_articles()), self.examples[0]["related"]
        )
