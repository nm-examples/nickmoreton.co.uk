# Wagtail redesign implementation plan

Status: implemented locally; awaiting developer review.

Prepared: 17 October 2026.

## Objective

Implement the layout and theme in [the redesign reference](README.md) throughout
the existing Django/Wagtail site, rendering content through Wagtail and preserving
existing content and URLs.

The scope includes the five reference layouts plus article chapters, site search,
error pages, the kitchen-sink page, and reusable content blocks so the whole site
adopts the theme consistently.

This document records the agreed strategy. See [integration and review notes](integration.md)
for the implementation, population commands, verification, and screenshots.

## 1. Establish the template and asset structure

Keep the existing Sass, esbuild, and image build pipeline. Place production source
assets in `webapp/static_src/` and continue generating assets into
`webapp/static_compiled/`.

Adapt the reference CSS modules into Sass partials for foundations, shared
components, homepage sections, and inner pages. Keep the existing single CSS and
JavaScript entry points initially; introduce separate bundles only if there is a
demonstrated need.

Use this template ownership:

| Area | Template location | Reference |
| --- | --- | --- |
| Shared document, metadata, stylesheet and script loading | `webapp/templates/base.html` | Shared structure across all five pages |
| Header, navigation, footer | `webapp/core/templates/core/` | Shared reference components |
| Homepage and its section includes | `webapp/home/templates/home/` | `index.html` |
| Article and package indexes | `webapp/pages/templates/pages/` | `articles.html`, `packages.html` |
| Article, chapter, and package details | `webapp/pages/templates/pages/` | `article.html`, `package.html` |
| StreamField block templates | `webapp/pages/templates/blocks/` | Reference prose and content components |
| Search | `webapp/search/templates/search/` | Adapted archive layout |
| Error pages | `webapp/templates/` | Simplified theme layouts |

The existing structure largely supports this already. Keep `docs/redesign/` as an
independent reference that can still be opened in a browser.

## 2. Agree the content model before building the homepage

The current `HomePage` model has a general body StreamField and article/package
queries. It has no dedicated fields for the new hero, portfolio, or About sections.

### Recommended homepage editing approach

Use a fixed homepage layout with structured, editable content:

- **Hero:** introduction, role, supporting text, and a featured project reference.
- **Profile/YAML:** one set of profile values used for both the visible terminal
  and copied text.
- **Portfolio:** an ordered StreamField of projects containing title, category,
  description, image, image description, and external record URL.
- **About:** editable text and profile links.
- **Articles and packages:** continue using published Wagtail pages, with explicit
  featured ordering where the design needs it.

Keep presentation details such as colours, decorative shapes, section numbering,
and card layout in templates and styles.

### Article and package metadata

The reference displays metadata that the current page models do not hold. Add
small, optional fields for article topic labels and package categories,
repository links, and homepage featuring. A full taxonomy system is unnecessary
for the current scope.

### Content preservation and population

Preserve existing body content, page IDs, slugs, and URLs. Use additive migrations
with safe defaults, then a documented population step for the approved homepage
content and metadata.

Review the existing homepage body before replacing its visible introduction to
avoid duplicating or losing content.

**Review outcome:** agree the editing structure and content population approach
before template implementation.

## 3. Implement the shared theme and homepage

Build the shared shell first:

- Brand, responsive navigation, and footer.
- Typography, colours, buttons, and containers.
- Focus styles and a skip link.

The current navigation setting only supports page links. Extend it to support the
homepage anchors and external GitHub link used in the reference while preserving
existing menu entries. Generate homepage URLs through Wagtail so links such as
“Websites” and “About” also work from detail pages.

Implement the homepage sections in reference order:

1. Hero and profile terminal.
2. Historical website portfolio.
3. Open-source packages.
4. Filterable article list.
5. About and profile links.
6. Closing exploration section.

Replace prototype `.html` links and hardcoded live-site article/package URLs with
Wagtail page links. Preserve the supplied wording about Nick’s Torchbox role and
historical projects.

Remove the old Pico-based styling as the redesigned templates are completed,
checking for remaining dependencies before removing the package.

**Review outcome:** a working homepage, with desktop and mobile screenshots
compared against the reference.

## 4. Implement indexes, details, and all existing content types

Build the article and package indexes using reusable cards and list items shared
with the homepage. Counts, descriptions, links, and filter labels must come from
the rendered Wagtail content.

For detail pages:

- Render the existing StreamField content inside the new prose layout.
- Add breadcrumbs, excerpts, appropriate metadata, sidebars, and related content.
- Generate stable, unique heading anchors and a matching table of contents.
- Preserve article chapter lists, the first-chapter link, and previous/next
  navigation.
- Apply the reference styling to rich text, headings, callouts, aligned images,
  and code blocks.
- Retain syntax highlighting and exact code copying; use accessible expandable
  sections for long examples.

The prototype demonstrates only one article and one package. Validate varied
existing pages and chapters as well as those two examples.

Restyle site search and the kitchen-sink page. Give the 404 page the shared theme
and keep the 500 page simple enough to render without database-dependent
navigation.

The existing PyPI template tag makes an external request during rendering without
a timeout. As part of the package sidebar work, add a timeout, caching, and
graceful handling of missing or unavailable metadata.

**Review outcome:** all existing page types and content blocks work within the
new theme.

## 5. Integrate assets and interactions

Address two concrete integration issues:

- `scripts/images.js` currently skips WebP input, including the four portfolio
  screenshots. Extend its handling and keep output extensions consistent with
  the actual image format.
- The prototype scripts assume particular elements exist. Convert them into
  guarded modules so the shared bundle works safely across all page types.

Use static source assets for theme imagery and Wagtail images for editable
portfolio content. Keep article screenshots attached to their existing CMS
content where available.

Implement mobile navigation, filtering, empty/reset states, YAML copying, and code
copying. Preserve useful access to navigation and content when JavaScript is
unavailable, and respect reduced-motion preferences.

## 6. Validate and prepare the completed redesign for review

### Build and backend

- Run `npm run build` and Biome.
- Run the Python tools required by the repository: Ruff, pyupgrade, and
  django-upgrade for touched Python code.
- Check migrations and run `make test`.

### Meaningful regression tests

Add coverage for published-page listings, optional metadata fallbacks, chapter
navigation, heading anchors, navigation links, and PyPI failure handling. The
current test suite contains only a placeholder test.

### Browser and accessibility checks

- Check the reference widths of 320, 390, 760, 820, 1000, 1440, and 1600px.
- Confirm no unintended horizontal overflow, missing assets, or JavaScript errors.
- Check keyboard navigation, Escape handling, visible focus, filtering
  announcements, copying, long code, and reduced motion.
- Check navigation and content access with JavaScript unavailable.

### Production-mode verification

Run `make prod-run` and check collected assets and media with `DEBUG = False`.
Use the documented local data/media workflows only when needed for representative
content, and keep generated backups and production dumps out of version control.

### Review package

Provide:

- Screenshots of each layout, including desktop and mobile examples.
- A migration and content-population checklist.
- Validation results and any remaining limitations.
- An `Unreleased` changelog entry for the implementation.

Deployment preparation should account for database/media backup and any
compatibility implications of the migrations. When preparing a PR for merging or
deployment, move its changelog entries into a dated release section as required by
the repository guidelines.

## Branch and review workflow

Begin implementation on a descriptive feature branch such as `wagtail-redesign`.
Keep changes focused so the shared theme, content models, homepage, and inner-page
integration can be reviewed clearly.

Follow the repository’s `AGENTS.md` requirements:

- Commit only after developer review and explicit approval for commit.
- Ask whether to push the branch, create a pull request, or both, and wait for
  instruction unless already authorized for the current work.
- Keep the changelog and any PR description aligned with the final implementation.

## Main decision for review

Approve or adjust the proposed homepage editing approach before implementation.
The recommendation is a fixed layout with structured Wagtail fields and portfolio
blocks: it closely follows the supplied design while making the content
straightforward to maintain.
