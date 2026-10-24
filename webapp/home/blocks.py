from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class PortfolioProjectBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    category = blocks.CharBlock()
    description = blocks.TextBlock(required=False)
    image = ImageChooserBlock()
    image_description = blocks.CharBlock()
    record_url = blocks.URLBlock()

    class Meta:
        icon = "image"
        label = "Past website project"
