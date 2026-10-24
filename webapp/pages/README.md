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

There are no pages-specific application tests. Review article, chapter, package,
and shared block output manually. Follow the
[application testing scope](../../docs/testing.md) when adding minimal tests of
the site's behaviour; keep manual visual and production-mode checks separate.

## Extending the app

Keep body-anchor processing in `content.py` so article, chapter, and package
contexts share the same rules. Keep queries and navigation with their page models;
see the [architecture guidance](../../docs/architecture.md) for their ordering and
scoping invariants.
