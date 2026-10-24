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
| `test_blocks.py` | Code-expansion boundaries and literal display/copy output. |
| `test_pypi_tags.py` | Metadata validation, caching, request failures, and fallback links. |

## Editor experience

Articles have optional topic and repository fields. Packages have category,
repository, icon, and featured-card fields. The featured flag changes package-card
presentation; it does not control inclusion in the homepage list.

Both page types have a homepage-order field: lower values appear first, with newest
date and primary key breaking ties. Archive lists use newest date and primary key.
Listings exclude unpublished and restricted pages and stay within their owning
homepage or index.

## Rendering flow

Article, chapter, and package contexts call `render_body()`. It renders the body's
StreamField blocks through `templates/pages/includes/body.html`, assigns IDs to
`h2` and `h3` headings, and returns HTML plus contents entries in document order.
Existing heading IDs are preserved where possible. Generated and conflicting IDs
must avoid other heading IDs, non-heading body IDs, and the shared `main` and
`navigation` IDs.

Code blocks use `templates/blocks/code.html`. Examples above 30 lines or 1,800
characters are wrapped in collapsed details. The displayed code and the textarea
used by the copy script must preserve the same literal text, including whitespace
and HTML examples.

## External integration

`pypi_info` renders the package-information component using `package_metadata()`.
The helper rejects invalid names, normalizes equivalent package names for requests
and caching, and uses two-second connect and three-second read timeouts. Successes
are cached for an hour and failures for five minutes. Unavailable metadata leaves
valid PyPI and repository links available.

## Verification

`test_content.py` uses small synthetic rich-text bodies and the real body template.
It covers heading selection and titles, repeated and conflicting IDs, preservation
of later existing IDs, headings without slug characters, and empty contents.
`test_blocks.py` renders synthetic code examples through the real block template.
It checks expansion at and above each limit independently, plus escaped HTML and
whitespace preservation in displayed code and the copy source. These output tests
do not exercise browser clipboard behaviour.

`test_pypi_tags.py` uses synthetic metadata, mocked HTTP responses, and an isolated
in-memory cache. It covers invalid names and versions, date extraction, bounded
requests, normalized cache reuse, success/failure cache lifetimes, request/HTTP/JSON
failures, and fallback resource links in the actual inclusion-tag component.
Cache reuse uses the real cache backend; lifetime assertions check the timeout
passed to it without waiting for expiry.

All three files use `SimpleTestCase` without database access or external requests.
Models, chapter navigation, and other blocks are not yet covered.

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
