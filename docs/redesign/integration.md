# Wagtail redesign integration and review

The original HTML/CSS/JavaScript in this directory remains the visual reference.
Current editing and migration guidance is below; implementation-time verification
is retained as history.

## Preview

- Development: <http://localhost:8000/>
- Production mode: <https://prod-nginx.nickmoreton-production.orb.local>
- Production-mode localhost fallback: <http://localhost:8001/>

Restore production data and media using the [data workflows](../data-and-media.md)
for a populated local site. The production data already includes the redesigned
portfolio, page metadata, and navigation; no population step is required.

## Content editing

Edit the homepage in Wagtail to change the introduction, role, hero headings,
profile/YAML values, About copy, and profile links. The legacy `body` StreamField
is retained in the editor for reference; the redesigned homepage renders the new
structured fields instead. The existing legacy homepage content was the YAML
introduction, which now has editable values shared by the display and copy action.

Portfolio projects are ordered blocks with a title, category, optional description,
Wagtail image, image description, external portfolio-record URL, and a featured
checkbox retained from the initial design. The hero randomly selects from all
portfolio projects on each page request, keeping the image, title, description,
and record link together. The featured checkbox no longer controls the hero.
Random selection can repeat a project on consecutive requests. An empty portfolio
has a link to the external portfolio archive.

Article pages have optional topic and repository fields. Package pages have
category, repository, icon, and featured-card fields. Both types have a homepage
order field: lower numbers appear first, with publication date used to break ties.
Archive listings continue to use publication date. Lists exclude unpublished and
restricted pages and stay within the relevant homepage or index.

Navigation settings retain existing page links and additionally accept external
URLs and optional section IDs. Section IDs omit `#`; use the homepage as the target
page for `work` and `about`. Existing configured menu order is preserved. GitHub
is rendered as the distinct profile action from the homepage settings.

## Assets and templates

- Source Sass, JavaScript, and the six supplied images live in
  `webapp/static_src/`.
- Sass and esbuild retain the existing single CSS and JavaScript bundle outputs in
  `webapp/static_compiled/`.
- The image build copies WebP and SVG source assets and writes converted raster
  images with `.webp` extensions. It still generates the PNG favicons.
- Editable portfolio screenshots are Wagtail images restored with production
  data/media or selected in the editor, and served as Wagtail renditions. Existing
  article/package images remain attached to their CMS content.
- App-owned templates are under each app's `templates/` directory; the document
  shell and error pages remain in `webapp/templates/`.
- Pico and the unused previous theme partials/scripts have been removed.
- Beautiful Soup, already supplied through Wagtail, is now declared directly
  because the application uses it to generate heading anchors and contents links.

No new environment variables are required.

## Theme colours

The shared palette lives in
`webapp/static_src/styles/foundations/_tokens.scss`. It contains 25 colours plus
the two font variables: page/text/borders, violet branding, coral/gold/teal
accents, and dark code surfaces. Components reuse these colours directly instead
of declaring their own near-identical shades. Translucent surfaces and shadows
use `color-mix()` with the shared colours.

For example, `--muted` controls secondary text and labels, `--accent` controls the
main violet accents and buttons, and `--soft` controls pale violet backgrounds.
Use the darker companion colours for text on accent surfaces. After editing the
palette, rebuild the frontend and recheck contrast against affected backgrounds.

The static reference keeps the same palette in
`docs/redesign/assets/styles/foundations/tokens.css`; keep these files aligned.
The SVG favicon/header artwork and third-party syntax-highlighting theme retain
their own embedded colours.

## Migrations and saved content

Homepage copy and URLs are stored CMS values. Their 14 model defaults and the
one-off redesign population command/manifest have been removed. New homepage
instances require explicit content; existing saved values remain unchanged.
Article/package ordering, featured-state, and icon defaults remain in place.

Migration `home.0007_remove_homepage_seed_defaults` deletes non-current, unscheduled
homepage revisions missing any of those 14 fields before removing the defaults.
Live/latest revisions, scheduled revisions, complete homepage revisions, and revisions
of other page types are preserved. Historical migration files remain unchanged.

With the development containers running:

```sh
make migrate
make collectstatic
```

For production-mode local checks:

```sh
make prod-run
```

Run migrations after importing an older production backup. Edit future content in
Wagtail; there is no command to seed the portfolio or metadata. The restored database
and media already supply the four portfolio projects, article/package metadata, and
homepage navigation anchors.

Take a database backup before deploying the cleanup migration. Reversing its field
changes restores model defaults but does not recover deleted historical revisions;
recovering them requires the pre-migration backup. This cleanup has not been deployed
to the live site.

## Verification

See [testing and verification](../testing.md) for the current suite and the
[home app](../../webapp/home/README.md) for homepage and revision-cleanup guidance.
The records below describe checks performed during implementation.

Checks performed during implementation:

- Frontend production build and Biome checks.
- Ruff, pyupgrade, django-upgrade, Django system checks, and migration drift checks.
- All 37 Django regression tests passed in development and production mode, covering content rendering, related cards, chapter
  navigation, public listings, search, editable fields, content population,
  code escaping, unique anchors, and PyPI failure/caching behaviour.
- HTTP rendering of all 21 published development pages.
- Homepage, both indexes, and article/package details at 320, 390, 760, 820, 1000,
  1440, and 1600px, checking document overflow and contents-link targets.
- Mobile menu opening, Escape handling, article/package filtering, empty/reset
  states, YAML copying, and exact code copying.
- A script-free homepage response at 320px, confirming accessible navigation and
  all article content with enhancement controls hidden.
- Production-mode Docker build, migrations, collected static assets, homepage,
  and the themed 404 response with `DEBUG = False`.

The desktop homepage hero, title, introduction, visual area, and section boundary
measurements match the reference at 1440px. CMS excerpts, dates, headings, and
configured navigation order intentionally reflect the site's content.

PyPI metadata has bounded request timeouts, successful-result caching for an hour,
and failure caching for five minutes. A failed request leaves package content and
resource links available.

### Stack rebase verification — 19 October 2026

PR #81 already contains the latest `main`. Rebased the implementation plan (#83)
onto #81 and the redesign (#84) onto the refreshed plan. The runtime and dependency
upgrades from #86 are retained, including Python 3.14.8, Django 6.0.9, Wagtail
7.4.3 LTS, and Node 24.22.0. The redesign still removes Pico and declares Beautiful
Soup directly. The CI workflow retains locked installs, PostgreSQL tests, and
frontend build/static collection before rendering tests.

Updated the inherited upgrade tests to submit the new homepage-order field,
isolate cached PyPI results, assert bounded request timeouts, and model HTTP errors
while checking that fallback resource links remain available.

Fresh checks after the rebase:

- All 48 Django tests pass against PostgreSQL in both development and production
  settings, using isolated test databases.
- Both Docker image builds, the local frontend production build, and Biome pass.
- Lockfile validation, static collection, Django system checks, migration drift
  checks, and applicable pre-commit checks pass.
- The plan document, redesign application code, and source assets are unchanged
  from their previous branch heads; the only application-tree changes are the
  inherited upgrade tests and their compatibility corrections.

The warning-enabled test runs report Wagtail image-rendition `ResourceWarning`s
for unclosed temporary files. Browser interactions and visual layouts were not
rechecked for this rebase; the screenshots and visual checks above are historical.

## Screenshots

Homepage and index images show the full page. Detail, chapter, search, and error
images show the initial viewport. Desktop captures are 1440px wide; mobile captures
are 390px wide.

| Layout | Desktop | Mobile |
| --- | --- | --- |
| Homepage | [Desktop](review/home-desktop.png) | [Mobile](review/home-mobile.png) |
| Article index | [Desktop](review/articles-desktop.png) | [Mobile](review/articles-mobile.png) |
| Package index | [Desktop](review/packages-desktop.png) | [Mobile](review/packages-mobile.png) |
| Article | [Desktop](review/article-desktop.png) | [Mobile](review/article-mobile.png) |
| Package | [Desktop](review/package-desktop.png) | [Mobile](review/package-mobile.png) |
| Chapter | [Desktop](review/chapter-desktop.png) | [Mobile](review/chapter-mobile.png) |
| Search | [Desktop](review/search-desktop.png) | [Mobile](review/search-mobile.png) |
| 404 in production mode | [Desktop](review/404-desktop.png) | [Mobile](review/404-mobile.png) |

Commits, pushing, PR creation, and deployment require the separate review and
instructions described in the repository's `AGENTS.md`.
