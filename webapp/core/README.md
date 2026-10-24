# Core app

Owns per-site navigation settings and shared site components.

- [models.py](models.py): navigation setting.
- [navigation_tags.py](templatetags/navigation_tags.py): link assembly and fallback rules.
- [templates/core/](templates/core/): header, footer, and shared controls.

Manage navigation in Wagtail's site settings. Enter section IDs without `#`; use the
homepage as the page target for `work` and `about`. An anchor without another target
uses the site's root page. The GitHub link is maintained in the navigation template.

See [testing](../../docs/testing.md) for verification.
