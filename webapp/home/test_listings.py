from datetime import date

from django.test import RequestFactory, TestCase
from wagtail.models import Page, PageViewRestriction

from webapp.home.models import HomePage
from webapp.pages.models import (
    ArticleIndexPage,
    ArticlePage,
    PackageIndexPage,
    PackagePage,
)


class HomepageListingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.get_first_root_node()
        outside_articles = root.add_child(
            instance=ArticleIndexPage(title="Outside articles")
        )
        outside_packages = root.add_child(
            instance=PackageIndexPage(title="Outside packages")
        )
        cls.home = root.add_child(
            instance=HomePage(
                title="Listing home", introduction="Introduction", about_body="About"
            )
        )
        cls.examples = []
        for index_model, model, key, outside_index in (
            (ArticleIndexPage, ArticlePage, "articles", outside_articles),
            (PackageIndexPage, PackagePage, "packages", outside_packages),
        ):
            cls.home.add_child(instance=index_model(title=f"Draft {key}", live=False))
            private_index = cls.home.add_child(
                instance=index_model(title=f"Private {key}")
            )
            PageViewRestriction.objects.create(
                page=private_index, restriction_type="login"
            )
            private_index.add_child(
                instance=model(title="Inherited restriction", date=date(2026, 10, 28))
            )
            index = cls.home.add_child(instance=index_model(title=f"Public {key}"))

            def page(title: str, day: int, order: int = 0, **values):
                return index.add_child(
                    instance=model(
                        title=title,
                        date=date(2026, 10, day),
                        homepage_order=order,
                        **values,
                    )
                )

            oldest = page("Oldest priority", 1)
            tie_first = page("First tie", 20)
            tie_last = page("Last tie", 20)
            lower_priority = page("Newer lower priority", 25, order=10)
            page("Draft", 26, live=False)
            restricted = page("Restricted", 27)
            PageViewRestriction.objects.create(
                page=restricted, restriction_type="login"
            )
            outside_index.add_child(
                instance=model(title="Outside home", date=date(2026, 10, 29))
            )
            if model is PackagePage:
                lower_priority.featured = True
                lower_priority.save(update_fields=["featured"])
            cls.examples.append(
                {
                    "key": key,
                    "index": index,
                    "listing": [tie_last, tie_first, oldest, lower_priority],
                }
            )

    def test_homepage_lists_scope_visible_content_and_use_editorial_order(self):
        context = self.home.get_context(RequestFactory().get("/"))

        for example in self.examples:
            with self.subTest(kind=example["key"]):
                self.assertEqual(
                    list(context[f"all_{example['key']}"]), example["listing"]
                )

    def test_archive_links_use_first_public_live_indexes_under_this_home(self):
        context = self.home.get_context(RequestFactory().get("/"))

        self.assertEqual(context["article_index"], self.examples[0]["index"])
        self.assertEqual(context["package_index"], self.examples[1]["index"])

    def test_homepage_without_indexes_has_empty_lists_and_no_archive_links(self):
        home = Page.get_first_root_node().add_child(
            instance=HomePage(
                title="Empty home", introduction="Introduction", about_body="About"
            )
        )
        context = home.get_context(RequestFactory().get("/"))

        self.assertEqual(list(context["all_articles"]), [])
        self.assertEqual(list(context["all_packages"]), [])
        self.assertIsNone(context["article_index"])
        self.assertIsNone(context["package_index"])
