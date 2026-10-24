# Architecture

## Layout and ownership

This is a Wagtail content site. Page models own CMS fields, relationships, simple
queries, and `get_context()` hooks; Wagtail handles routing and rendering. Search is
a Django view because it spans page types.

| Responsibility | Location |
| --- | --- |
| Homepage and portfolio snippets | [`home/models.py`](../webapp/home/models.py) |
| Articles, chapters, packages, and related lists | [`pages/models.py`](../webapp/pages/models.py) |
| StreamField blocks and body rendering | [`pages/blocks.py`](../webapp/pages/blocks.py), [`pages/content.py`](../webapp/pages/content.py) |
| Per-site navigation | [`core/models.py`](../webapp/core/models.py), [`navigation_tags.py`](../webapp/core/templatetags/navigation_tags.py) |
| PyPI integration | [`pypi_tags.py`](../webapp/pages/templatetags/pypi_tags.py) |
| Search | [`search/views.py`](../webapp/search/views.py) |
| HTML | App `templates/` directories and shared `webapp/templates/` |
| Frontend source | `webapp/static_src/`; build output goes to `webapp/static_compiled/` |
| Configuration and deployment | `webapp/settings/`, `docker/`, and `docker-compose.yaml` |

Keep changes with the owning app. Extract a service or query helper only when an
operation becomes complex or reused enough to justify it. Detailed behaviour belongs
beside the implementation; app READMEs cover editor workflows.

## Conventions and boundaries

Target Python 3.14, Django 6.0, and Wagtail 7.4 LTS. Use PEP 8, lowercase module and
template directories, PascalCase classes, and snake_case functions. Runtime pins and
checks are in [Python maintenance](python-upgrade.md), [Node maintenance](node-upgrade.md),
and [testing](testing.md).

Preserve live/public filtering, site or page-tree scoping, and deterministic ordering
when changing content queries. Shared body rendering stays in `pages/content.py` so
article, chapter, and package contents links stay consistent.

Manage content in Wagtail. Keep transactions around complete multi-step writes.
External HTTP integration currently runs during rendering; there is no background
worker.

Configure editors through model panels, StreamField blocks, and registered settings.
If custom admin views are needed, use the owning app's `wagtail_hooks.py` for
registration and `viewsets.py` for definitions; preserve permissions and stable URLs.

Frontend scripts and Sass live in `webapp/static_src/scripts/` and `styles/`. Reuse
colour and font tokens from `styles/foundations/_tokens.scss`; recheck contrast after
palette changes. CMS images use Wagtail media storage and renditions, independently
of compiled frontend assets.
