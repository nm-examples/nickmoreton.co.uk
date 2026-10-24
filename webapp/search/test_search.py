from unittest.mock import patch

from django.test import RequestFactory, TestCase
from wagtail.models import Page, PageViewRestriction, Site
from wagtail.query import PageQuerySet
from wagtail.search.backends import get_search_backend

from webapp.search.views import search


class SearchDecisionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.get_first_root_node()
        cls.site_root = root.add_child(instance=Page(title="Coverageword site"))
        Site.objects.create(hostname="search.test", root_page=cls.site_root)
        matches = [cls.site_root]
        matches += [
            cls.site_root.add_child(instance=Page(title=f"Coverageword {number}"))
            for number in range(11)
        ]
        cls.site_root.add_child(instance=Page(title="Different content"))
        cls.site_root.add_child(instance=Page(title="Coverageword draft", live=False))
        restricted = cls.site_root.add_child(
            instance=Page(title="Coverageword private")
        )
        PageViewRestriction.objects.create(page=restricted, restriction_type="login")
        restricted.add_child(instance=Page(title="Coverageword restricted descendant"))
        cls.outside = root.add_child(instance=Page(title="Coverageword outside site"))
        cls.match_ids = {page.pk for page in matches}
        # Arrange the index explicitly so tests don't depend on save-signal timing.
        backend = get_search_backend()
        for page in Page.objects.filter(title__icontains="Coverageword"):
            backend.add(page)

    def request(self, **params):
        return RequestFactory().get("/search/", params, HTTP_HOST="search.test")

    def test_trimmed_search_is_scoped_to_live_public_site_content(self):
        first = search(self.request(query="  Coverageword  ")).context_data
        second = search(self.request(query="Coverageword", page=2)).context_data
        results = first["search_results"]

        self.assertEqual(first["search_query"], "Coverageword")
        self.assertEqual(results.paginator.per_page, 10)
        self.assertEqual(results.paginator.count, 12)
        self.assertEqual(len(results), 10)
        self.assertEqual(len(second["search_results"]), 2)
        self.assertEqual(
            {page.pk for page in results}
            | {page.pk for page in second["search_results"]},
            self.match_ids,
        )

    def test_blank_query_does_not_search(self):
        with patch.object(PageQuerySet, "search") as backend:
            context = search(self.request(query="   ")).context_data

        self.assertEqual(context["search_query"], "")
        self.assertEqual(list(context["search_results"]), [])
        backend.assert_not_called()

    def test_invalid_page_values_use_the_chosen_fallback_page(self):
        for supplied, expected in (("invalid", 1), ("999", 2), ("0", 2), ("-1", 2)):
            with self.subTest(page=supplied):
                context = search(
                    self.request(query="Coverageword", page=supplied)
                ).context_data
                self.assertEqual(context["search_results"].number, expected)

    def test_unmatched_query_has_empty_results(self):
        context = search(self.request(query="NoMatchingCoverageTerm")).context_data

        self.assertEqual(list(context["search_results"]), [])
        self.assertEqual(context["search_results"].number, 1)

    def test_no_resolved_site_keeps_public_search_available(self):
        with patch("webapp.search.views.Site.find_for_request", return_value=None):
            context = search(self.request(query="Coverageword")).context_data

        results = context["search_results"]
        self.assertEqual(results.paginator.count, 13)
        self.assertIn(
            self.outside.pk, {page.pk for page in results.paginator.object_list}
        )
