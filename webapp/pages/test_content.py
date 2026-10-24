from bs4 import BeautifulSoup
from django.test import SimpleTestCase

from webapp.pages.blocks import BaseBlocks
from webapp.pages.content import render_body


class BodyContentsTests(SimpleTestCase):
    def render(self, html: str) -> dict:
        body = BaseBlocks().to_python([{"type": "rich_text", "value": html}])
        return render_body(body, None)

    def test_contents_match_h2_h3_heading_ids(self):
        result = self.render(
            "<h1>Introduction</h1><h2>Install <em>the package</em></h2>"
            "<h3>Run it</h3><h4>Details</h4>"
        )

        self.assertEqual(
            result["table_of_contents"],
            [
                {
                    "id": "install-the-package",
                    "title": "Install the package",
                    "level": "h2",
                },
                {"id": "run-it", "title": "Run it", "level": "h3"},
            ],
        )
        soup = BeautifulSoup(result["rendered_body"], "html.parser")
        self.assertEqual(
            [heading["id"] for heading in soup.find_all(["h2", "h3"])],
            [entry["id"] for entry in result["table_of_contents"]],
        )
        self.assertEqual(str(soup.find("em")), "<em>the package</em>")
        self.assertFalse(soup.h1.has_attr("id"))
        self.assertFalse(soup.h4.has_attr("id"))

    def test_anchors_avoid_duplicates_shared_ids_and_empty_slugs(self):
        result = self.render(
            "<h2>Main</h2><h3>Navigation</h3><h2>Install</h2><h2>Install</h2>"
            "<h3>Install 2</h3><h2>!!!</h2><h3>???</h3>"
        )
        expected = [
            "main-2",
            "navigation-2",
            "install",
            "install-2",
            "install-2-2",
            "section",
            "section-2",
        ]

        self.assertEqual(
            [entry["id"] for entry in result["table_of_contents"]], expected
        )
        soup = BeautifulSoup(result["rendered_body"], "html.parser")
        self.assertEqual(
            [heading["id"] for heading in soup.find_all(["h2", "h3"])], expected
        )

    def test_body_without_contents_headings_is_preserved(self):
        html = "<h1>Introduction</h1><p>Some <strong>content</strong>.</p>"
        result = self.render(html)

        self.assertEqual(result["table_of_contents"], [])
        self.assertHTMLEqual(result["rendered_body"], html)
