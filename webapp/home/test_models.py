from datetime import date

from django.test import TestCase
from wagtail.models import Page, PageViewRestriction

from webapp.home.models import HomePage
from webapp.pages.models import ArticleIndexPage, ArticlePage
from webapp.testutils import content_tree, publish


class HomePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home, cls.articles, cls.packages, cls.article, cls.chapter, cls.package = (
            content_tree()
        )

    def test_homepage_lists_published_public_content_in_editorial_order(self):
        first = publish(
            self.articles,
            ArticlePage(
                title="Featured",
                slug="featured",
                date=date(2020, 1, 1),
                homepage_order=1,
            ),
        )
        private = publish(
            self.articles,
            ArticlePage(title="Private", slug="private", date=date.today()),
        )
        PageViewRestriction.objects.create(
            page=private, restriction_type="password", password="secret"
        )
        draft = publish(
            self.articles, ArticlePage(title="Draft", slug="draft", date=date.today())
        )
        draft.unpublish()
        other = publish(
            Page.get_first_root_node(), ArticleIndexPage(title="Other", slug="other")
        )
        publish(
            other, ArticlePage(title="Other site", slug="other-site", date=date.today())
        )
        self.assertEqual(list(self.home.all_articles()), [first, self.article])
        self.assertEqual(list(self.home.all_packages()), [self.package])

    def test_yaml_uses_editable_values_and_escapes_name(self):
        home = HomePage(
            profile_name='Nick "Example"',
            employer_url="https://example.com",
            cms_url="https://wagtail.org",
        )
        self.assertEqual(
            home.profile_yaml.splitlines()[1], r'  name: "Nick \"Example\""'
        )
        self.assertIn("works_at: https://example.com", home.profile_yaml)
        self.assertIn("preferred_cms: https://wagtail.org", home.profile_yaml)

    def test_hero_project_is_optional(self):
        self.assertIsNone(self.home.hero_project)
