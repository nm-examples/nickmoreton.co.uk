from django.test import SimpleTestCase

from webapp.pages.blocks import CodeBlock


class CodeExpansionTests(SimpleTestCase):
    def test_code_expands_only_above_the_line_or_character_threshold(self):
        for code, expected in (
            ("", False),
            ("\n".join(["line"] * 30), False),
            ("\n".join(["line"] * 31), True),
            ("x" * 1800, False),
            ("x" * 1801, True),
        ):
            with self.subTest(lines=len(code.splitlines()), characters=len(code)):
                context = CodeBlock().get_context({"code": code, "language": "python"})
                self.assertEqual(context["expand_code"], expected)
