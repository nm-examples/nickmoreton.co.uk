# Home app

## Purpose

Owns the homepage introduction, About copy, portfolio projects, and editorial
article/package lists.

## Key code

| Path | Responsibility |
| --- | --- |
| `models.py` | Homepage fields, hero selection, and scoped editorial lists. |
| `blocks.py` | Portfolio project fields. |

## Content and rendering

The introduction, About body, and portfolio projects are managed in Wagtail.
Headings, identity, role, and profile/archive links are hardcoded in the homepage
include templates. The navigation GitHub link is hardcoded in its own template.
The visible profile YAML and its copyable plain text are hardcoded in
`templates/home/includes/hero.html`; update both together when changing that content.

`HomePage.get_context()` supplies live, public articles/packages and indexes below
the homepage. Lists use editorial order, then newest date and primary key. The hero
selects randomly from all portfolio projects. Selection can repeat on consecutive
requests. An empty portfolio links to the external portfolio archive.

## Editor experience

The homepage content editor contains Introduction, About, and Past website projects,
alongside Wagtail's standard page title. Edit Introduction manually to include any
desired headline text. There is no separate headline, legacy body, or featured-project
control.

Portfolio projects are ordered blocks containing a title, category, optional
description, Wagtail image, image description, and external portfolio-record URL.
The image description supplies alternative text. Manage screenshots through Wagtail
images or restore them with production data/media.

## Verification

There are no homepage-specific application tests. Review homepage output manually
and follow [testing and verification](../../docs/testing.md) for new tests. See the
[data workflows](../../docs/data-and-media.md) for restoring local content and
migration recovery.

## Extending the app

Keep simple homepage queries and context assembly in `models.py`. Fixed profile
values and headings are code changes; do not reintroduce CMS fields for these details.
Follow the [architecture guidance](../../docs/architecture.md) for query and rendering rules.
