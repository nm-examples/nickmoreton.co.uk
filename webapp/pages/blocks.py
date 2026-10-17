from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class BaseHeadingBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    level = blocks.ChoiceBlock(
        choices=[
            ("h1", "H1"),
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
            ("h5", "H5"),
            ("h6", "H6"),
        ]
    )

    class Meta:
        icon = "title"


class HeadingBlock(BaseHeadingBlock):
    class Meta:
        template = "blocks/heading.html"


class CodeBlock(blocks.StructBlock):
    code = blocks.TextBlock()
    language = blocks.ChoiceBlock(
        choices=[
            ("bash", "Bash"),
            ("css", "CSS"),
            ("html", "HTML"),
            ("javascript", "JavaScript"),
            ("json", "JSON"),
            ("python", "Python"),
            ("yaml", "YAML"),
        ]
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["expand_code"] = (
            len(value["code"].splitlines()) > 30 or len(value["code"]) > 1800
        )
        return context

    class Meta:
        icon = "code"
        template = "blocks/code.html"


class ImageBlockAligned(blocks.StructBlock):
    image = ImageChooserBlock()
    alignment = blocks.ChoiceBlock(
        choices=[
            ("left", "Left"),
            ("center", "Center"),
            ("right", "Right"),
        ]
    )
    content = blocks.RichTextBlock(required=False)

    class Meta:
        icon = "image"
        template = "blocks/image_aligned.html"


class BaseBlocks(blocks.StreamBlock):
    heading = HeadingBlock()
    callout = blocks.RichTextBlock(template="blocks/callout.html")
    rich_text = blocks.RichTextBlock()
    code = CodeBlock()
    image_aligned_block = ImageBlockAligned()
