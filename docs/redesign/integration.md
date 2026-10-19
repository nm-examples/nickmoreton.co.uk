# Wagtail redesign integration and review

The redesign is implemented on `wagtail-redesign` and is ready for local review.
The original HTML/CSS/JavaScript in this directory remains the visual reference.

## Preview

- Development: <http://localhost:8000/>
- Production mode: <https://prod-nginx.nickmoreton-production.orb.local>
- Production-mode localhost fallback: <http://localhost:8001/>

Development currently contains the existing articles, packages, and chapters.
The production-mode database used for verification is a separate, fresh local
database with the supplied portfolio populated. It has not been replaced with a
production dump or the development database. Content-dependent production tests
use fixtures in an isolated test database.

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
- Editable portfolio screenshots are imported into Wagtail images by the setup
  command and served as Wagtail renditions. Existing article/package images remain
  attached to their CMS content.
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

## Migrations and content population

Four migrations cover the homepage fields, article/package presentation fields,
optional navigation URL/anchor values, and the Support Engineer title correction.
The title correction updates matching supplied copy in saved homepage content and
current live/draft revisions; customised copy, older revisions, and draft status
are preserved. Existing body fields, page IDs, slugs, and URLs are preserved.

For an existing checkout with the development containers running:

```sh
npm ci
npm run build
make migrate
make collectstatic
docker compose exec app python manage.py populate_redesign
```

The last command is a dry run. Apply the supplied portfolio content and missing or
default article/package metadata with:

```sh
docker compose exec app python manage.py populate_redesign --apply
```

Use `--home-id PAGE_ID` if a specific homepage needs to be selected. The command:

- Imports the four supplied portfolio images if the homepage portfolio is empty.
- Fills missing/default metadata for known article/package slugs without changing
  their titles, bodies, or URLs.
- Adds homepage section links while preserving existing navigation entries.
- Skips pages with unpublished changes and does not publish draft-only pages.
- Creates and publishes revisions for changed live pages.
- Can be repeated without duplicating projects, images, or navigation entries.

Review warnings for missing pages or skipped drafts. Pages that were skipped can
be updated in the editor or populated after their pending changes are resolved.
The command preserves non-default editorial values; a value intentionally left at
its model default is eligible for population.

For the isolated production-mode local stack:

```sh
make prod-run
docker compose -f docker-compose.production.yaml exec prod-app python manage.py populate_redesign
docker compose -f docker-compose.production.yaml exec prod-app python manage.py populate_redesign --apply
```

Take the usual database and media backup before applying the migrations and
population command to the deployed site. Run the same migrations, frontend build,
and static collection through its existing deployment workflow. This work has
not deployed to the live site.

A rollback must account for both the code and schema: reverse the new migrations
with compatible code, or restore the pre-deployment database and media backups.
Reversing the schema removes the newly edited fields, so preserve any desired
new content before doing so. The original page bodies remain available.

## Verification

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
