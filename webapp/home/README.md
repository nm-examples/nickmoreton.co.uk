# Home app

## Purpose

Owns the homepage introduction, About copy, portfolio projects, and editorial
article/package lists.

## Key code

| Path | Responsibility |
| --- | --- |
| `models.py` | Portfolio project snippets, homepage selection, hero selection, and scoped editorial lists. |
| `test_projects.py` | Project ordering, deleted-reference handling, and hero selection checks. |

## Content and rendering

The introduction and About body are managed on the homepage in Wagtail. Portfolio
content is managed separately as snippets; the homepage stores an ordered selection.
Headings, identity, role, and profile/archive links are hardcoded in the homepage
include templates. The navigation GitHub link is hardcoded in its own template.
The visible profile YAML and its copyable plain text are hardcoded in
`templates/home/includes/hero.html`; update both together when changing that content.

`HomePage.get_context()` supplies live, public articles/packages and indexes below
the homepage. Lists use editorial order, then newest date and primary key. The hero
selects randomly from the homepage's selected projects. Selection can repeat on
consecutive requests. Deleted snippets are skipped in both the grid and hero. An
empty selection hides the projects section, Websites navigation link, hero screenshot,
and Explore past work link.

## Editor experience

Manage project details under **Snippets → Portfolio projects**. Each snippet contains
a title, category, optional description, Wagtail image, image description, and external
portfolio-record URL. The image description supplies alternative text. Manage
screenshots through Wagtail images or restore them with production data/media.

The homepage content editor contains Introduction, About, and Past website projects,
alongside Wagtail's standard page title. Use the project choosers to select, reorder,
or remove projects, then publish the page to apply that selection. Removing a chooser
leaves the snippet available for later use. Saving snippet edits updates its content
wherever selected, including on the published homepage; snippets have no separate
draft/publish step.

Edit Introduction manually to include any desired headline text. There is no separate
headline, legacy body, or featured-project control.

The snippet collection starts empty. The schema migration removes the former inline
project field and adds a separate snippet-selection field. Saved revisions are not
rewritten; their old project field is no longer used. Add projects manually as
snippets, then select them on the homepage. Existing Wagtail images remain available
for reuse. See
[migration recovery](../../docs/data-and-media.md#migration-recovery) for deployment
and rollback steps.

## Verification

Run `docker compose exec -T app python manage.py test webapp.home --noinput` for the
focused selection tests. They protect chosen order, deleted-snippet handling, and
hero candidates.
Review the snippet editor, homepage chooser, and homepage output manually; follow
[testing and verification](../../docs/testing.md) for new tests. See the
[data workflows](../../docs/data-and-media.md) for restoring local content and
migration recovery.

## Extending the app

Keep simple homepage queries and context assembly in `models.py`. Fixed profile
values and headings are code changes; do not reintroduce CMS fields for these details.
Keep project content on snippets and page-specific selection in `HomePage.project_selection`.
Both the hero and portfolio grid use `selected_projects` so they share the same pool.
Follow the [architecture guidance](../../docs/architecture.md) for query and rendering rules.
