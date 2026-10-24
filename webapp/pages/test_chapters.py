from datetime import date

from django.db import connection
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from wagtail.models import Page, PageViewRestriction

from webapp.pages.models import ArticleChapterPage, ArticleIndexPage, ArticlePage


class ChapterNavigationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        index = Page.get_first_root_node().add_child(
            instance=ArticleIndexPage(
                title="Navigation articles", slug="navigation-articles"
            )
        )
        cls.article = index.add_child(
            instance=ArticlePage(
                title="Article", slug="article", date=date(2026, 10, 24)
            )
        )

        def chapter(title: str, *, live: bool = True):
            return cls.article.add_child(
                instance=ArticleChapterPage(title=title, live=live)
            )

        cls.last = chapter("Alpha")
        cls.first = chapter("Zulu")
        cls.draft = chapter("Draft", live=False)
        restricted = chapter("Restricted")
        PageViewRestriction.objects.create(page=restricted, restriction_type="login")
        cls.middle = chapter("Middle")
        chapter("Later draft", live=False)
        restricted = chapter("Later restricted")
        PageViewRestriction.objects.create(page=restricted, restriction_type="login")
        # Tree order must win over creation order and alphabetical titles.
        cls.last.move(cls.article, pos="last-child")
        for page in (cls.first, cls.middle, cls.last, cls.draft):
            page.refresh_from_db()

        other_article = index.add_child(
            instance=ArticlePage(title="Other article", date=date(2026, 10, 24))
        )
        other_article.add_child(instance=ArticleChapterPage(title="Other chapter"))
        cls.empty_article = index.add_child(
            instance=ArticlePage(title="No visible chapters", date=date(2026, 10, 24))
        )
        cls.only_draft = cls.empty_article.add_child(
            instance=ArticleChapterPage(title="Only draft", live=False)
        )

    def setUp(self):
        self.request = RequestFactory().get("/")

    def test_article_uses_first_visible_chapter_in_tree_order(self):
        context = self.article.get_context(self.request)

        self.assertEqual(
            list(context["chapters"]), [self.first, self.middle, self.last]
        )
        self.assertEqual(context["first_chapter"], self.first)

    def test_neighbours_skip_hidden_chapters_and_stay_within_article(self):
        for current, previous, following in (
            (self.first, None, self.middle),
            (self.middle, self.first, self.last),
            (self.last, self.middle, None),
        ):
            with self.subTest(chapter=current.title):
                context = current.get_context(self.request)

                self.assertEqual(context["article"], self.article)
                self.assertEqual(context["current_chapter"], current)
                self.assertEqual(
                    list(context["chapters"]), [self.first, self.middle, self.last]
                )
                self.assertEqual(context["previous_chapter"], previous)
                self.assertEqual(context["next_chapter"], following)

    def test_draft_preview_finds_visible_neighbours_by_tree_position(self):
        context = self.draft.get_context(self.request)

        self.assertNotIn(self.draft, context["chapters"])
        self.assertEqual(context["previous_chapter"], self.first)
        self.assertEqual(context["next_chapter"], self.middle)

    def test_no_visible_chapters_has_no_first_or_neighbour_links(self):
        article_context = self.empty_article.get_context(self.request)
        chapter_context = self.only_draft.get_context(self.request)

        self.assertEqual(list(article_context["chapters"]), [])
        self.assertIsNone(article_context["first_chapter"])
        self.assertEqual(list(chapter_context["chapters"]), [])
        self.assertIsNone(chapter_context["previous_chapter"])
        self.assertIsNone(chapter_context["next_chapter"])

    def test_context_fetches_chapters_once(self):
        for page in (self.article, self.middle):
            with self.subTest(page=type(page).__name__):
                with CaptureQueriesContext(connection) as queries:
                    context = page.get_context(self.request)
                    list(context["chapters"])
                chapter_queries = [
                    query
                    for query in queries
                    if f'FROM "{ArticleChapterPage._meta.db_table}"' in query["sql"]
                ]
                self.assertEqual(len(chapter_queries), 1)
