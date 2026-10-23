# Pages app

## Purpose

Owns articles, chapters, packages, and their shared content rendering.

## Key code

| Path | Responsibility |
| --- | --- |
| `models.py` | Page hierarchy, listings, related content, and chapter navigation. |
| `blocks.py` | Shared StreamField blocks and code-expansion decisions. |
| `content.py` | Body rendering, heading anchors, and table-of-contents entries. |
| `templatetags/pypi_tags.py` | Cached package metadata and unavailable-data fallback. |
| `test_content.py` | Focused tests of heading anchors and contents entries. |

## Rendering flow

Article, chapter, and package contexts call `render_body()`. It renders the body's
StreamField blocks through `templates/pages/includes/body.html`, assigns IDs to
`h2` and `h3` headings, and returns HTML plus contents entries in document order.
Existing heading IDs are preserved where possible. Generated and conflicting IDs
must avoid other heading IDs, non-heading body IDs, and the shared `main` and
`navigation` IDs.

## Verification

`test_content.py` uses small synthetic rich-text bodies and the real body template.
It covers heading selection and titles, repeated and conflicting IDs, preservation
of later existing IDs, headings without slug characters, and empty contents.
The tests use `SimpleTestCase` without database access or external requests.
Models, chapter navigation, code blocks, and PyPI metadata are not yet covered.

```sh
docker compose exec -T app python manage.py test webapp.pages --noinput
```

Follow the [application testing scope](../../docs/testing.md). Manual visual and
production-mode checks are separate from these helper tests.

## Extending the app

Keep body-anchor processing in `content.py` so article, chapter, and package
contexts share the same rules. Keep queries and navigation with their page models;
see the [architecture guidance](../../docs/architecture.md) for their ordering and
scoping invariants.
