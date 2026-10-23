"""Protect the heading-anchor rules using small synthetic StreamField bodies."""

from bs4 import BeautifulSoup
from django.test import SimpleTestCase

from webapp.pages.blocks import BaseBlocks
from webapp.pages.content import render_body


class RenderBodyTests(SimpleTestCase):
    def render_html(self, html: str) -> tuple[BeautifulSoup, list[dict[str, str]]]:
        body = BaseBlocks().to_python([{"type": "rich_text", "value": html}])
        result = render_body(body, request=None)
        return (
            BeautifulSoup(result["rendered_body"], "html.parser"),
            result["table_of_contents"],
        )

    def test_contents_include_only_h2_and_h3_in_document_order(self) -> None:
        soup, contents = self.render_html(
            "<h1>Article title</h1>"
            "<h2>Build <strong>reliable</strong> sites</h2>"
            "<h4>Implementation detail</h4>"
            "<h3>Deploy <em>safely</em></h3>"
        )

        self.assertEqual(
            contents,
            [
                {
                    "id": "build-reliable-sites",
                    "title": "Build reliable sites",
                    "level": "h2",
                },
                {"id": "deploy-safely", "title": "Deploy safely", "level": "h3"},
            ],
        )
        self.assertEqual(soup.h2["id"], "build-reliable-sites")
        self.assertEqual(soup.h3["id"], "deploy-safely")

    def test_repeated_headings_have_distinct_matching_anchors(self) -> None:
        cases = {
            "generated IDs": "<h2>Setup</h2><h3>Setup</h3><h2>Setup</h2>",
            "existing IDs": (
                '<h2 id="setup">Setup</h2>'
                '<h3 id="setup">Setup</h3>'
                '<h2 id="setup">Setup</h2>'
            ),
        }
        for name, html in cases.items():
            with self.subTest(name=name):
                soup, contents = self.render_html(html)
                anchors = [heading["id"] for heading in soup.select("h2, h3")]

                self.assertEqual(anchors[0], "setup")
                self.assertEqual(len(set(anchors)), 3)
                self.assertTrue(all(anchors))
                self.assertEqual([item["id"] for item in contents], anchors)

    def test_generated_anchor_preserves_a_later_existing_heading_id(self) -> None:
        soup, contents = self.render_html(
            '<h2>Install</h2><h3 id="install">Advanced setup</h3>'
        )

        self.assertEqual(soup.h3["id"], "install")
        self.assertNotEqual(soup.h2["id"], "install")
        self.assertEqual(
            contents,
            [
                {"id": soup.h2["id"], "title": "Install", "level": "h2"},
                {"id": "install", "title": "Advanced setup", "level": "h3"},
            ],
        )

    def test_heading_anchors_avoid_body_and_shared_template_ids(self) -> None:
        soup, contents = self.render_html(
            '<p id="example">An existing link target.</p>'
            "<h2>Example</h2><h2>Main</h2><h3>Navigation</h3>"
            '<h2 id="navigation">Another navigation heading</h2>'
        )
        anchors = [heading["id"] for heading in soup.select("h2, h3")]

        self.assertEqual(soup.p["id"], "example")
        self.assertEqual(len(set(anchors)), 4)
        self.assertTrue(set(anchors).isdisjoint({"example", "main", "navigation"}))
        self.assertEqual([item["id"] for item in contents], anchors)

    def test_headings_without_slug_characters_still_have_usable_anchors(self) -> None:
        soup, contents = self.render_html("<h2>!!!</h2><h3>???</h3>")
        anchors = [soup.h2["id"], soup.h3["id"]]

        self.assertTrue(all(anchors))
        self.assertEqual(len(set(anchors)), 2)
        self.assertEqual(
            contents,
            [
                {"id": anchors[0], "title": "!!!", "level": "h2"},
                {"id": anchors[1], "title": "???", "level": "h3"},
            ],
        )

    def test_body_without_contents_headings_has_empty_contents(self) -> None:
        for html in ("", "<p>Introduction only.</p>", "<h4>A minor heading</h4>"):
            with self.subTest(html=html):
                _, contents = self.render_html(html)

                self.assertEqual(contents, [])
