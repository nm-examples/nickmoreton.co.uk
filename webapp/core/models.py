from wagtail import blocks
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField


@register_setting(icon="list-ul")
class Navigation(BaseSiteSetting):
    main_menu = StreamField(
        [
            (
                "main_menu",
                blocks.StructBlock(
                    [
                        ("label", blocks.CharBlock(required=True)),
                        ("page", blocks.PageChooserBlock(required=False)),
                        ("url", blocks.URLBlock(required=False)),
                        (
                            "anchor",
                            blocks.RegexBlock(
                                regex=r"^[A-Za-z][A-Za-z0-9_-]*$",
                                required=False,
                                help_text="Optional section ID, such as work or about, without #.",
                            ),
                        ),
                    ]
                ),
            ),
        ],
        blank=True,
    )
