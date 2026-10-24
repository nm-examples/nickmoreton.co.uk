# Home app

## Purpose

Owns editable homepage copy, portfolio projects, and editorial article/package lists.

## Key code

| Path | Responsibility |
| --- | --- |
| `models.py` | Homepage fields, YAML output, hero selection, and scoped editorial lists. |
| `blocks.py` | Portfolio project fields. |
| `migrations/0007_remove_homepage_seed_defaults.py` | Removes content defaults and obsolete homepage snapshots that relied on them. |

## Content and rendering

Homepage copy and URLs are required CMS fields without content defaults. Existing
values remain stored in the database and revisions. Restore production data for
the populated site or manage content in Wagtail; there is no population command.
Historical migration files retain their original defaults.

`HomePage.get_context()` supplies live, public articles/packages and indexes below
the homepage. Lists use editorial order, then newest date and primary key. The hero
selects from all portfolio projects; the retained featured checkbox does not control
selection. The legacy body remains available to editors.

## Migrations and verification

Migration `0007` removes non-current, unscheduled homepage revisions missing any of
the 14 seeded content fields. Live/latest, scheduled, and complete revisions are
preserved, along with revisions belonging to other page types. Reversing the field
changes restores defaults but does not recover deleted revisions; recovery requires
a database backup.

The current application tests cover shared rendering and PyPI behaviour in the
pages app; there are no homepage-specific test files. See
[testing and verification](../../docs/testing.md).
Run `make migrate` after updating or restoring an older production backup. Review
homepage output separately from automated application tests.

## Extending the app

Keep simple homepage queries and context assembly in `models.py`. Preserve authored
content and active revisions during future data migrations. Ordering, featured-state,
and icon defaults on article/package models remain useful editing defaults; see
the [architecture guidance](../../docs/architecture.md).
