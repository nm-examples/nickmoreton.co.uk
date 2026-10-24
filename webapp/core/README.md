# Core app

## Purpose

Owns per-site navigation settings and shared site components.

## Key code

| Path | Responsibility |
| --- | --- |
| `models.py` | Registered Wagtail navigation setting and menu fields. |
| `templatetags/navigation_tags.py` | Menu assembly and fallback links for the current site. |
| `templates/core/` | Navigation, header, footer, and shared filtering controls. |

## Editor experience and rendering

Manage navigation in Wagtail's site settings. Items retain configured order and
combine a label with a page, external URL, or section anchor. Enter section IDs
without `#`; use the homepage as the page target for `work` and `about`. An anchor
without another target uses the current site's root page.

The navigation tag skips unpublished or restricted linked pages. If no usable
configured links remain, it builds Websites/About section links around live, public
root-page children marked for menu display.

## Verification

There are no core-specific application tests. Review configured links and fallback
navigation manually; follow the [application testing scope](../../docs/testing.md)
when adding focused coverage.

## Extending the app

Keep navigation per site, preserve configured order, and retain the visibility
checks and fallback behaviour in the existing template tag.
