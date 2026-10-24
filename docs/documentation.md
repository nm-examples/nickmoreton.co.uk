# Documentation standards

Treat documentation as part of the implementation and update it whenever the
corresponding behavior changes.

Apply these standards to new and changed code. Adopting this guidance does not
require a separate pass over untouched source files.

## Keeping docs and guidance aligned

For every code addition, modification, move, or removal, check whether existing
documentation or agent guidance could be affected. Search for references to the
changed files, symbols, commands, and behavior, including indirect assumptions about
how the feature works.

Update affected documentation and guidance as part of the same change, before
presenting it for review or committing it. This includes root and app READMEs,
architecture and operational docs, verification instructions, `AGENTS.md`, repository
skills and their references, and source comments/docstrings. Remove obsolete
instructions and links when code is removed.

Keep guidance focused on current behaviour and maintenance. Use Git and the changelog
for completed-project history. Retain dated records only when they support an ongoing
compatibility, operational, or recovery requirement; do not present them as current
behaviour or coverage.

## Source documentation

- Add module or function docstrings where responsibility or behavior is not clear
  from the code. Useful examples include heading-ID collision handling, navigation
  fallback rules, PyPI caching/failure handling, and data-migration preservation rules.
- Document meaningful inputs, outputs, side effects, exceptions, permissions, or
  transaction behavior when callers need that information. Simple field declarations,
  straightforward framework overrides, and obvious helpers do not need docstrings
  that repeat their names. Empty package markers and generated files need no extra
  documentation.
- Add inline comments around complicated code to explain intent, invariants,
  security or performance constraints, and the reason for non-obvious choices.
  Avoid comments that merely translate an individual line into English.
- Add brief comments to templates, stylesheets, and JavaScript where structure
  or behavior is not self-evident. Document reusable template tags, filters,
  components, and browser-side APIs at their definitions.
- Use parameter and return type hints for new or changed Python functions and
  methods where the framework does not make them impractical.
- Keep documentation concise, accurate, and close to the code it describes;
  remove stale comments when code is deleted or simplified.

## App README template

Use this structure as a starting point for app-level `README.md` files. Keep the
sections that help explain the app; omit sections that do not apply:

```markdown
# <App name> app

## Purpose

## Key code

| Path | Responsibility |
| --- | --- |

## Content model

## Rendering flow

## Editor experience

## Verification

## Extending the app
```

Apply the template as follows:

- Keep small app READMEs short. For example, the search app needs its query-scoping
  and pagination rules, but does not need a content-model or editor-experience
  section. The pages app benefits from documenting its hierarchy, StreamField
  processing, and chapter navigation.
- In **Key code**, list the important app-relative files and describe their
  responsibilities rather than merely restating their names.
- In **Content model**, document fields, relationships, ordering, fallback
  rules, search behavior, and important page-hierarchy constraints that apply.
- In **Rendering flow**, explain the relevant page context or view, rendering
  helper/template tag, template, and browser behavior. Use short prose for simple
  flows; add a Mermaid diagram only when it makes a more involved flow clearer.
- In **Editor experience**, explain where editors manage the feature and how
  their choices affect the frontend.
- In **Verification**, state the actual coverage and relevant verification commands.
  Do not describe an empty test run as coverage. For focused application tests, use
  `docker compose exec -T app python manage.py test webapp.<app>` and follow the
  [custom-behavior scope](testing.md). Record manual browser or
  production-mode verification separately from automated application tests.
- In **Extending the app**, record the intended extension points and invariants
  that future changes must preserve. Do not speculate about features that are
  not supported by the current design.
- Add focused sections such as **Frontend behavior**, **Query and security
  design**, or **External integrations** when they materially clarify the app.
  Place them after the main flow and before **Verification**.
- Use paths relative to the app directory and keep the README synchronized with
  code, migrations, templates, tests, and architectural decisions.
