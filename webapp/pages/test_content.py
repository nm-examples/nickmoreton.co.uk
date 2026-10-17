from bs4 import BeautifulSoup
from django.test import RequestFactory, SimpleTestCase

from webapp.pages.blocks import BaseBlocks
from webapp.pages.content import render_body


class RenderBodyTests(SimpleTestCase):
    def render(self, values):
        body = BaseBlocks().to_python(values)
        return render_body(body, RequestFactory().get("/"))

    def test_toc_anchors_are_unique_and_match_rendered_headings(self):
        result = self.render(
            [
                {"type": "heading", "value": {"heading": "Setup", "level": "h2"}},
                {
                    "type": "rich_text",
                    "value": "<h2>Setup</h2><h3>Setup</h3><h2>!!!</h2>",
                },
            ]
        )
        anchors = [item["id"] for item in result["table_of_contents"]]
        self.assertEqual(anchors, ["setup", "setup-2", "setup-3", "section"])
        soup = BeautifulSoup(result["rendered_body"], "html.parser")
        self.assertEqual([h["id"] for h in soup.find_all(["h2", "h3"])], anchors)

    def test_anchors_reserve_existing_non_heading_ids(self):
        result = self.render(
            [{"type": "rich_text", "value": '<p id="setup">Intro</p><h2>Setup</h2>'}]
        )
        self.assertEqual(result["table_of_contents"][0]["id"], "setup-2")

    def test_code_is_escaped_and_source_preserves_whitespace(self):
        code = '<script>alert("test")</script>\n  indented & text\n</textarea>'
        result = self.render(
            [{"type": "code", "value": {"code": code, "language": "html"}}]
        )
        soup = BeautifulSoup(result["rendered_body"], "html.parser")
        self.assertIsNone(soup.find("script"))
        self.assertEqual(soup.code.get_text(), code)
        self.assertEqual(soup.textarea.get_text(), code)

    def test_existing_heading_anchor_is_preserved(self):
        result = self.render(
            [
                {
                    "type": "rich_text",
                    "value": '<h2>Setup</h2><h3 id="setup">Custom setup</h3>',
                }
            ]
        )
        self.assertEqual(
            [item["id"] for item in result["table_of_contents"]], ["setup-2", "setup"]
        )

    def test_long_code_is_expandable_without_losing_content(self):
        code = "print('example')\n" * 150
        result = self.render(
            [{"type": "code", "value": {"code": code, "language": "python"}}]
        )
        soup = BeautifulSoup(result["rendered_body"], "html.parser")
        self.assertIsNotNone(soup.select_one("details.code-expand summary"))
        self.assertEqual(soup.code.get_text(), code)

    def test_many_short_code_lines_are_expandable(self):
        code = "# comment\n" * 40
        result = self.render(
            [{"type": "code", "value": {"code": code, "language": "python"}}]
        )
        soup = BeautifulSoup(result["rendered_body"], "html.parser")
        self.assertIsNotNone(soup.select_one("details.code-expand"))
