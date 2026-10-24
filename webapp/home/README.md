# Home app

## Purpose

Owns editable homepage copy, portfolio projects, and editorial article/package lists.

## Key code

| Path | Responsibility |
| --- | --- |
| `models.py` | Homepage fields, YAML output, hero selection, and scoped editorial lists. |
| `blocks.py` | Portfolio project fields. |

## Content and rendering

Homepage copy, URLs, and portfolio projects are managed in Wagtail.

`HomePage.get_context()` supplies live, public articles/packages and indexes below
the homepage. Lists use editorial order, then newest date and primary key. The hero
selects from all portfolio projects; the featured checkbox does not control
selection. Selection can repeat on consecutive requests. An empty portfolio links to
the external portfolio archive.

## Editor experience

Edit the homepage in Wagtail to manage its introduction, role, hero headings,
profile/YAML values, About copy, and profile links. Profile values are shared by the
visible YAML display and its copy action. The homepage renders these structured
fields; its `body` field is available in the editor but is not rendered.

Portfolio projects are ordered blocks containing a title, category, optional
description, Wagtail image, image description, and external portfolio-record URL.
The image description supplies alternative text. Manage screenshots through Wagtail
images or restore them with production data/media.

## Verification

There are no homepage-specific application tests. Review homepage output manually
and follow [testing and verification](../../docs/testing.md) when adding minimal
tests of the site's behaviour. See the
[data workflows](../../docs/data-and-media.md) for restoring local content and
migration recovery.

## Extending the app

Keep simple homepage queries and context assembly in `models.py`. Preserve authored
content and active revisions during data migrations. Follow the
[architecture guidance](../../docs/architecture.md) for query and rendering rules.
