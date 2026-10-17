# Nick Moreton website mockup

A responsive personal portfolio prototype for the redesign of
[nickmoreton.co.uk](https://www.nickmoreton.co.uk/). These files are layout and styling
references for integration into the existing Django/Wagtail site.

## Preview

Open [index.html](index.html) in a browser. No build step or dependencies are required.
Keep the HTML files and the `assets/` directory together so images, styles,
interactions, and local page links resolve.

For a local server, run this command from the repository root (localhost also supports
the clipboard actions):

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory docs/redesign
```

Then visit [the local preview](http://127.0.0.1:4173).

## Design and behavior

Violet, coral, warm yellow and teal, a colourful client website showcase, subtle
terminal details, and the original `who_am_i` YAML introduction. The primary action
explores past website work. The introduction makes Nick’s current role at Torchbox
clear; the site is a personal portfolio and archive, without freelance enquiries or
new-client calls to action. All four packages and seven articles from the existing
homepage are included. The Getting Started With Wagtail and Wagtail Honeypot links open
local detail examples; other detail links lead to the existing live pages.

Article search filters titles and displayed topic labels. The responsive menu supports
Escape and closes after navigation. YAML can be copied on localhost or HTTPS. The page
includes a skip link, visible keyboard focus states, semantic landmarks, labelled
controls, and a reduced-motion preference.

## Client portfolio

Four real projects and their supplied screenshots are featured from
https://madewithwagtail.org/developers/nick-moreton/: Alcott Farm Bed & Breakfast,
Cotswold Cottage Holidays, Four All Seasons Catering, and Visit Droitwich Spa. Each
links to its Made with Wagtail record. Screenshots depict the work documented in those
records, rather than asserting how live sites look today. Portfolio headings are
interface copy, with no invented outcomes or testimonials. Past projects are explicitly
framed as historical work.

## Content provenance

The original prototype records these content sources as inspected on 15 October 2026:

- https://www.nickmoreton.co.uk/
- https://www.nickmoreton.co.uk/packages/wagtail-exposapi/
- https://www.nickmoreton.co.uk/packages/wagtail-honeypot/
- https://www.nickmoreton.co.uk/packages/wagtail-formatted-richtext/
- https://www.nickmoreton.co.uk/packages/wagtail-qr-code/
- https://www.nickmoreton.co.uk/articles/getting-started-with-wagtail/

The headline uses “Software Engineer” at Nick’s request. The original YAML values,
package names, package description excerpts, article titles, and profile links are
retained. Section headings, navigation labels, article topic labels, and short orienting
text are new interface copy. No testimonials, client logos, invented statistics,
availability claims, email addresses, or business credentials have been added.

## Validation

The original prototype records browser checks at 1440px desktop, 820px tablet, and 390px
and 320px mobile widths, with no document horizontal overflow or browser console errors
observed. It also records checks of article search, the no-results state, reset, YAML
copy, mobile menu navigation, and inner pages at desktop and mobile widths, including
search, copying, expandable code, and local file and fragment links. Repeat these checks
when integrating the prototype into Wagtail.

During the reference-file refactor, all five pages were compared with the original
prototype in Chrome at 320, 390, 760, 820, 1000, 1440, and 1600px widths. Computed
styles and element positions matched, with no horizontal overflow. Responsive menu
controls, filtering, empty/reset states, YAML and code copying, and expandable code were
checked where present. Direct filesystem previews loaded the shared CSS and JavaScript
on all five pages, with no browser JavaScript errors.

## Scope

This directory contains five static HTML pages, shared CSS and JavaScript, and six
images. It provides a homepage, article and package indexes, and two example detail
pages. It does not replace the live website or implement a CMS. Existing detail content
remains on the live site. During integration, adapt the shared layout and styling to the
project's templates and frontend source files, and render site content from Wagtail.

## File organization

- `assets/` — the six supplied screenshots, plus the styles and scripts below.
- `assets/styles/site.css` — shared stylesheet entry point.
- `assets/styles/archives.css` — additional stylesheet entry point for the two indexes.
- `assets/styles/details.css` — additional stylesheet entry point for the two details.
- `assets/styles/foundations/` — colour and font variables, document defaults,
  accessibility, and containers.
- `assets/styles/components/` — navigation, actions, sections, search, terminal, package
  cards, code blocks, and footer modules.
- `assets/styles/home/` — hero, portfolio, article list, About, and closing call to
  action modules.
- `assets/styles/pages/` — inner-page header, archive, prose, sidebar, and related
  content modules.
- `assets/scripts/navigation.js` — responsive menu controls shared by every page.
- `assets/scripts/home.js` — homepage article filtering and YAML copying.
- `assets/scripts/archive.js` — article and package index filtering.
- `assets/scripts/code-copy.js` — code copying on the two detail examples.

HTML and CSS use four-space indentation to match the project's templates and Sass.
JavaScript follows the project's Biome settings: two-space indentation, double quotes,
and semicolons. The YAML display rows retain their exact whitespace with
`prettier-ignore` comments. The prototype uses relative asset paths and classic scripts,
so it can still be opened directly from the filesystem without a build step.

The stylesheet entry points import the relevant modules using native CSS `@import`. Each
component keeps its responsive rules and prototype overrides together. Load `site.css`
first, followed by `archives.css` for an index or `details.css` for a detail page; the
homepage needs only `site.css`.

## Using the reference for implementation

These files are the source and visual guide for later redesign work in the main
codebase. The modules expose useful boundaries for that work:

| Reference                                        | Intended integration area                                         |
| ------------------------------------------------ | ----------------------------------------------------------------- |
| Foundations and shared components                | Shared templates and Sass partials in `webapp/static_src/styles/` |
| Homepage modules and `index.html`                | `webapp/home/` templates and homepage styling                     |
| Inner-page modules and the index/detail examples | `webapp/pages/` templates and page styling                        |
| JavaScript modules                               | Entry points and modules in `webapp/static_src/scripts/`          |

Adapt these references to Wagtail content and the existing frontend build in separate
implementation work. The prototype's native CSS imports and static HTML make the
reference easy to browse; they do not prescribe the final production asset structure.

## Current role and AI

At Nick’s request, the introduction and About section identify his role as a software
engineer in Torchbox’s support team and describe his team’s use of AI to develop tools
for day-to-day client site management, including upgrades, bug reports, and outages and
incidents, as supplied by Nick. No particular models, automation capabilities, or
measured outcomes are claimed.

## Inner page examples

- [articles.html](articles.html) — searchable article index using all seven existing
  titles.
- [article.html](article.html) — Getting Started With Wagtail, retaining the existing
  text, screenshot and code.
- [packages.html](packages.html) — searchable package index using all four existing
  packages.
- [package.html](package.html) — Wagtail Honeypot documentation, retaining text,
  screenshot and code; longer example can be expanded.

Homepage navigation and the two matching detail links open these examples. Other detail
links open the existing site. Content is preserved as a layout sample, not an updated
technical tutorial.
