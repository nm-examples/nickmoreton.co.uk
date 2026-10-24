# Testing and verification

## Application tests

Use Django's test runner through `make test`. Keep tests near the owning code, named
`test_*.py` with `test_<behaviour>` methods.

Before adding a test, identify the site-specific rule it protects and check existing
coverage. Prefer direct calls to the method, helper, template tag, or view decision;
use the database where needed and mock external services. Focused template-output
and query tests are appropriate for custom behaviour such as ordering or scoping.

Do not add:

- Tests that merely prove removed fields, content, links, or files are gone. Remove
  obsolete tests with the functionality and use searches/checks to verify cleanup.
- End-to-end journeys, browser automation, broad rendering or HTTP-status smoke tests,
  or admin edit/preview/publish workflows.
- Tests of Django/Wagtail persistence, validation, routing, authentication, publishing,
  or image rendition behaviour. Framework calls may arrange fixtures, but assertions
  must exercise our decisions.
- Duplicate coverage, assertions that mirror implementation details, or tests added
  only because a file or dependency changed.

Before committing test removals, show the developer the file/test names, the reason
for removal, and which custom behaviour remains covered. Do not remove a whole module
because only some tests are obsolete. Keep manual visual and deployment/build checks
separate from the application test suite.

### Current coverage

[Homepage tests](../webapp/home/test_projects.py) cover project selection and hero
candidates. [Navigation tests](../webapp/core/test_navigation.py) cover project-dependent
links and draft previews. [PyPI tests](../webapp/pages/test_pypi.py) cover name
normalization, lookup failures, and release dates, including retaining versions when
optional data is unusable.
Other app behaviour is not yet covered; an empty test run provides no application
coverage.

With development containers running:

```sh
docker compose exec -T app python manage.py test --noinput
```

### Coverage measurement

Run `make coverage` to erase previous measurements, run tests, print missing lines
and branches, and generate `htmlcov/index.html` and `coverage.xml`. These outputs
and `.coverage` are ignored. After dependency changes, rebuild with `make build` and
`make up` before using an existing container.

To measure one module:

```sh
make coverage TEST_ARGS="webapp.home.test_projects"
```

[pyproject.toml](../pyproject.toml) defines measurement scope and exclusions. CI uses
the same configuration and uploads the `python-coverage` artifact; there is no minimum
percentage gate. Startup imports execute declarations, so execution percentages alone
do not show tested behaviour. Python coverage does not measure templates, browser
code, or query correctness. Use missing branches to select the next meaningful
contract, following the test scope above.

## Code and build checks

For Python changes, run Ruff, pyupgrade, and django-upgrade using the versions/targets
in [.pre-commit-config.yaml](../.pre-commit-config.yaml) and
[pyproject.toml](../pyproject.toml). Check Django configuration and migration drift
with `python manage.py check` and `python manage.py makemigrations --check --dry-run`
inside the app container.

For frontend JavaScript/JSON, run `npm run biome:check` and `npm run build`. Keep
Biome pins aligned as described in [Node maintenance](node-upgrade.md).

See the [README](../README.md) for local setup and production-mode commands.
Dependency upgrades follow the relevant
[Python](python-upgrade.md) or [Node](node-upgrade.md) maintenance skill.
