from datetime import date

from django.test import RequestFactory, TestCase
from wagtail.models import Page, PageViewRestriction

from webapp.pages.models import (
    ArticleChapterPage,
    ArticleIndexPage,
    ArticlePage,
    PackagePage,
)
from webapp.testutils import content_tree, publish


class PageContextTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home, cls.articles, cls.packages, cls.article, cls.chapter, cls.package = (
            content_tree()
        )

    def setUp(self):
        self.request = RequestFactory().get("/")

    def test_indexes_exclude_unpublished_and_private_pages(self):
        draft = publish(
            self.articles, ArticlePage(title="Draft", slug="draft", date=date.today())
        )
        draft.unpublish()
        private = publish(
            self.articles,
            ArticlePage(title="Private", slug="private", date=date.today()),
        )
        PageViewRestriction.objects.create(
            page=private, restriction_type="password", password="secret"
        )
        self.assertEqual(
            list(self.articles.get_context(self.request)["articles"]), [self.article]
        )

    def test_related_articles_stay_in_index_and_exclude_current_article(self):
        related = publish(
            self.articles,
            ArticlePage(title="Related", slug="related", date=date.today()),
        )
        other_index = publish(
            Page.get_first_root_node(),
            ArticleIndexPage(title="Other articles", slug="other-articles"),
        )
        publish(
            other_index,
            ArticlePage(title="Other site", slug="other", date=date.today()),
        )
        self.assertEqual(list(self.article.get_latest_articles()), [related])
        self.assertEqual(list(self.chapter.get_latest_articles()), [related])

    def test_related_packages_exclude_current_page(self):
        related = publish(
            self.packages,
            PackagePage(title="Related", slug="related", date=date.today()),
        )
        self.assertEqual(list(self.package.get_latest_packages()), [related])

    def test_chapter_navigation_skips_drafts_and_private_pages(self):
        draft = publish(self.article, ArticleChapterPage(title="Draft", slug="draft"))
        draft.unpublish()
        private = publish(
            self.article, ArticleChapterPage(title="Private", slug="private")
        )
        PageViewRestriction.objects.create(
            page=private, restriction_type="password", password="secret"
        )
        last = publish(
            self.article, ArticleChapterPage(title="Last chapter", slug="last")
        )
        self.assertEqual(self.article.get_first_chapter(), self.chapter)
        self.assertEqual(self.chapter.get_next_chapter(), last)
        self.assertEqual(last.get_previous_chapter(), self.chapter)
        self.assertIsNone(last.get_next_chapter())
        self.assertIsNone(self.chapter.get_previous_chapter())
