# Architecture

## Project layout

The Django/Wagtail project lives under `webapp/`. Core settings are in
`webapp/settings/`, reusable app code is split across `webapp/home/`, `webapp/pages/`,
`webapp/core/`, and `webapp/search/`, and templates live alongside each app plus
`webapp/templates/` for shared pages. Frontend source files are in `webapp/static_src/`
with compiled output written to `webapp/static_compiled/`. Container and deployment
support lives in `docker/`, `docker-compose.yaml`, and `docs/`.

## Coding conventions

Target Python `3.14`, Django `6.0`, and Wagtail `7.4` LTS. Follow PEP 8 with 4-space
indentation. Keep Django modules and template directories lowercase with underscores;
use `PascalCase` for model and test class names, and `snake_case` for functions and
methods. Frontend entry points belong in `webapp/static_src/scripts/` and Sass partials
in `webapp/static_src/styles/`.

See [testing and verification](testing.md) for required code checks and [Python
maintenance](python-upgrade.md) and [Node maintenance](node-upgrade.md) for exact
runtime and tool pins.

## Framework model

This is a content site built around Wagtail pages. Page models own CMS fields,
relationships, small queries, and `get_context()` hooks. Wagtail handles page routing
and rendering; keep that flow when changing the homepage, articles, chapters, or
packages.

The search endpoint is a Django view because it searches across page types. Shared
content processing and template tags provide the other custom rendering behavior.

## Code placement

| Responsibility | Existing location |
| --- | --- |
| Homepage profile, portfolio, and editorial lists | [`home/models.py`](../webapp/home/models.py) and [`home/blocks.py`](../webapp/home/blocks.py) |
| Articles, chapters, packages, related content, and chapter navigation | [`pages/models.py`](../webapp/pages/models.py) |
| Shared StreamField blocks and code-expansion decisions | [`pages/blocks.py`](../webapp/pages/blocks.py) |
| Body rendering, heading anchors, and table of contents | [`pages/content.py`](../webapp/pages/content.py) |
| Per-site navigation settings and menu assembly | [`core/models.py`](../webapp/core/models.py) and [`core/templatetags/navigation_tags.py`](../webapp/core/templatetags/navigation_tags.py) |
| Cached PyPI metadata and package information | [`pages/templatetags/pypi_tags.py`](../webapp/pages/templatetags/pypi_tags.py) |
| Search scoping, query handling, and pagination | [`search/views.py`](../webapp/search/views.py) |
| Page and component HTML | App-level `templates/` directories and `webapp/templates/` |
| Syntax highlighting, navigation, archive filtering, and code copying | `webapp/static_src/scripts/` |

Keep changes with the owning app or helper. This site has no selector or service
modules; extract one only when an actual query or operation becomes complex or reused
enough to benefit. Keep simple page queries in model methods and context hooks.

## Content and rendering rules

- Homepage lists use editorial order, then newest date and primary key. Article and
  package indexes and related-content lists use newest date and primary key; related
  lists exclude the current article/package and are limited to three items.
- Preserve the existing live/public filters and homepage, index, or sibling scoping
  when changing queries. Chapter navigation follows tree order and skips unpublished
  and private chapters. Search is scoped to the current site's root when available.
- Article, chapter, and package contexts call `render_body()`. It renders StreamField
  HTML, assigns unique `h2`/`h3` anchors, and returns the matching table of contents.
  Preserve existing heading IDs where possible and avoid collisions with body IDs and
  the shared `main` and `navigation` IDs.
- Navigation is a per-site Wagtail setting. Its tag combines page links, anchors, and
  external URLs, excludes unpublished or restricted linked pages, and builds a
  homepage/child-page fallback when no usable configured items remain.

## External data and content operations

PyPI metadata is fetched during rendering through the existing template-tag helper.
Keep its name validation, normalized cache keys, explicit request timeouts, and
unavailable-data fallback. The site has no configured background worker; a background
fetching workflow would be a separate design change.

Manage CMS content in Wagtail. Use the [data and media workflows](data-and-media.md)
for local copies and recovery. Keep transactions around complete multi-step writes
in the code that owns them.

## Frontend assets and theme

The frontend build writes CSS/JavaScript bundles and images to `webapp/static_compiled/`.
It copies WebP/SVG files, converts raster images to WebP, and generates PNG favicons
from the SVG favicon. CMS images use Wagtail's media storage and renditions.

The shared colour and font tokens live in
`webapp/static_src/styles/foundations/_tokens.scss`. Reuse these tokens in components;
use `color-mix()` for translucent surfaces and shadows. Rebuild and recheck contrast
after palette changes. SVG artwork and the syntax-highlighting theme contain their
own embedded colours.

## Editor configuration

Page editing is configured through panels on the page models and through StreamField
blocks. Navigation uses a registered Wagtail site setting. There are currently no
custom hook or admin viewset modules. If an admin extension is needed, keep its
registration in the owning app's `wagtail_hooks.py` and viewset definitions in
`viewsets.py`, preserving permissions and stable admin URLs.
