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

The test runner and CI discovery step remain available. With the development app
container running:

```sh
docker compose exec -T app python manage.py test --noinput
```

Until tests are added, this discovers zero tests and provides no application coverage.

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
