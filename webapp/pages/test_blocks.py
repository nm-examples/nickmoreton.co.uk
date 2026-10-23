"""Protect code expansion and literal display/copy output with synthetic examples."""

from bs4 import BeautifulSoup
from django.test import SimpleTestCase

from webapp.pages.blocks import CodeBlock


class CodeBlockTests(SimpleTestCase):
    def render_code(self, code: str, language: str = "python") -> BeautifulSoup:
        block = CodeBlock()
        value = block.to_python({"code": code, "language": language})
        return BeautifulSoup(block.render(value), "html.parser")

    def test_code_expands_only_above_thirty_lines(self) -> None:
        for line_count, should_expand in ((30, False), (31, True)):
            with self.subTest(line_count=line_count):
                code = "\n".join(f"print({number})" for number in range(line_count))
                soup = self.render_code(code)
                details = soup.pre.find_parent("details")

                self.assertEqual(details is not None, should_expand)
                if should_expand:
                    self.assertFalse(details.has_attr("open"))

    def test_code_expands_only_above_eighteen_hundred_characters(self) -> None:
        for character_count, should_expand in ((1800, False), (1801, True)):
            with self.subTest(character_count=character_count):
                code = "# " + "x" * (character_count - 2)
                soup = self.render_code(code)
                details = soup.pre.find_parent("details")

                self.assertEqual(details is not None, should_expand)
                if should_expand:
                    self.assertFalse(details.has_attr("open"))

    def test_display_and_copy_source_preserve_literal_code(self) -> None:
        examples = {
            "python": "if ready:\n\tprint('café & tea')  \n\n    # Keep indentation\n",
            "html": (
                '<section title="A & B">Example</section>\n'
                "&lt;literal entity&gt;\n"
                '</code></pre><img src="x" onerror="alert(1)">\n'
                "</textarea><script>alert('example')</script>"
            ),
        }
        for language, code in examples.items():
            with self.subTest(language=language):
                soup = self.render_code(code, language)

                self.assertEqual(soup.select_one("pre code").get_text(), code)
                self.assertEqual(
                    soup.select_one("textarea[data-code-source]").get_text(), code
                )
                self.assertIsNone(soup.find("script"))
                self.assertIsNone(soup.find("img"))
