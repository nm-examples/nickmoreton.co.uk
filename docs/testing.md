# Testing and verification

## Application tests

Use Django’s built-in test runner (`python manage.py test` via `make test`). Keep tests
near the custom functionality they cover, using names such as `test_models.py` or
`test_content.py` and methods named `test_<behavior>`. An empty test run does not
establish application coverage.

Before adding a test, identify the project-specific rule or decision it protects and
check whether existing tests already cover it. Add focused tests only for custom
functionality: for example, editorial ordering, chapter selection, table-of-contents
anchor generation, YAML escaping, navigation assembly, or PyPI response handling. Prefer
direct calls to the relevant function, method, rendering helper, or template tag. Use
the database when the custom behavior needs it and mock external services.

Do not add:

- Tests that only prove legacy fields, content, links, files, or code have been removed.
  Remove obsolete tests alongside the deleted functionality; use code searches and
  normal checks to verify cleanup.
- End-to-end journeys, browser automation, broad page-rendering or HTTP-status smoke
  tests, or admin edit/preview/publish workflows.
- Tests of built-in Django or Wagtail behavior, such as ORM persistence, standard field
  validation, routing, authentication, revision publishing, or image rendition
  generation. Calling framework methods to arrange fixtures is fine; the assertions must
  exercise our custom behavior.
- Duplicate coverage, assertions that merely mirror implementation details, or tests
  added solely because a file changed or a dependency was upgraded.

Focused tests of custom template output or view decisions are appropriate when they
exercise project-specific behavior. A custom queryset test may use Wagtail filters while
checking our ordering or scoping rule; it must not merely retest the filters themselves.
Keep deployment/build checks and manual visual verification separate from the automated
application test suite.

Run the existing checks relevant to the change. Before committing test removals, show
the developer the file and test names, why each is being removed, and which custom
behavior remains covered. Do not remove an entire test module just because some tests in
it are out of scope.

### Current coverage

There are currently no application tests. Future additions should be minimal and
protect specific behaviour the site provides, following the scope above.

The test runner and CI coverage step remain available. With the development app
container running:

```sh
docker compose exec -T app python manage.py test --noinput
```

Until tests are added, this discovers zero tests and provides no application coverage.

### Coverage measurement

[Coverage.py](https://coverage.readthedocs.io/en/7.16.2/) is a locked development
dependency. With the development containers running, use:

```sh
make coverage
```

This erases previous measurements, runs Django's tests, prints missing lines and
branches, and writes `htmlcov/index.html` and `coverage.xml`. These outputs and the
`.coverage` data file are ignored by Git. After changing dependencies, rebuild the
app with `make build` and `make up` before using an existing container.

To measure a particular test module once it exists, pass its Django label:

```sh
make coverage TEST_ARGS="webapp.pages.test_content"
```

Configuration lives in `pyproject.toml`. Measurement includes Python code in the
home, pages, core, and search apps, including files not imported by the test run.
It omits migrations, tests, package markers, and app registration modules. Settings,
URL configuration, and process entry points are outside those app directories.
Model and block declarations remain included; their execution during startup does
not demonstrate tested behaviour. Python coverage does not measure template HTML,
browser JavaScript, CSS, or query correctness.

CI uses the same configuration and uploads HTML/XML reports as the
`python-coverage` artifact, including after a test failure when data is available.
There is no minimum percentage gate. Use missing lines and branches to find
unexercised decisions, then choose assertions using the application testing scope
above. A higher percentage alone does not show that the site's behaviour is correct.

### Choosing the first tests

The initial run discovers zero tests but reports 51.5% combined line/branch
execution: startup imports execute model/block declarations. All 28 measured
branches and every custom function/method body remain unexecuted. This is an
instrumentation baseline, not tested application coverage.

Use the report alongside the documented site rules to prioritize:

| Target | Small behavioural contract to protect |
| --- | --- |
| `pages/content.py` | Contents links match unique heading IDs, including collisions with existing and shared IDs. |
| `core/templatetags/navigation_tags.py` | Configured links retain order and usable targets; unavailable linked pages are skipped and an empty usable menu triggers the site's fallback. |
| `pages/templatetags/pypi_tags.py` | Mocked success/failure responses yield usable metadata or resource-link fallbacks; equivalent names reuse cached results. |
| `home/models.py` and `pages/models.py` | Editorial/date tie-breaks, related-list limits and scoping, and chapter neighbours follow the site's rules. Use a synthetic page tree with conflicting order/date values. |
| `home/models.py` and `pages/blocks.py` | Profile YAML preserves special characters; long code examples collapse at the documented boundaries and display/copy sources preserve literal text. |
| `search/views.py` | Blank input avoids a search and nonblank queries stay within the current site's root. Test the view's decisions directly, not search ranking or Django's paginator. |

Start with one focused heading/contents contract, review its assertions and report,
then select the next meaningful gap. Add only the cases needed to protect each
contract; do not test declarations merely to increase coverage.

## Code and build checks

For Python changes, run Ruff, pyupgrade, and django-upgrade before opening a PR. Use the
repository's configured versions and targets, recorded in
[`.pre-commit-config.yaml`](../.pre-commit-config.yaml) and
[`pyproject.toml`](../pyproject.toml).

For frontend JavaScript and JSON, run `npm run biome:check` for the configured file
coverage and `npm run build` to verify production assets. Keep Biome's package version,
pre-commit hook revision, and hook additional dependency aligned; see [Node
maintenance](node-upgrade.md).

Use the [README](../README.md) for local setup and commands, and [production-mode
checks](local.production.md) for verification before deployment. Dependency upgrades
must follow the relevant skill linked from [Python maintenance](python-upgrade.md) or
[Node maintenance](node-upgrade.md).
