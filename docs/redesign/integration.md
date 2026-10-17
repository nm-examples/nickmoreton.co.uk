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
checkbox. The first featured project appears in the hero; otherwise the first
project is used. An empty portfolio has a link to the external portfolio archive.

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

## Migrations and content population

Three schema migrations add homepage content fields, article/package presentation
fields, and optional navigation URL/anchor values. Existing body fields, page IDs,
slugs, and URLs are preserved.

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
- All 33 Django regression tests passed in development and production mode, covering content rendering, related cards, chapter
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
