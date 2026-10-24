# Developer documentation

This directory contains project-wide reference material that would otherwise
make the root `AGENTS.md` difficult to scan.

| Document | Purpose |
| --- | --- |
| [`architecture.md`](architecture.md) | Defines the project's Django and Wagtail code-placement boundaries. |
| [`documentation.md`](documentation.md) | Defines source-documentation standards and the app README template. |
| [`testing.md`](testing.md) | Defines the scope of application tests and required code/build verification. |
| [`contributing.md`](contributing.md) | Defines branch, review, commit, changelog, and pull-request rules. |
| [`data-and-media.md`](data-and-media.md) | Covers local and production-mode data/media sync and backup handling. |
| [`local.production.md`](local.production.md) | Describes local verification with Gunicorn, nginx, and `DEBUG = False`. |
| [`python-upgrade.md`](python-upgrade.md) | Records Python backend versions, verification, deployment, and rollback. |
| [`node-upgrade.md`](node-upgrade.md) | Records Node frontend versions, verification, and rollback. |

Feature-specific design and extension guidance belongs in the relevant
app-level `README.md` under `webapp/`. The [pages app](../webapp/pages/README.md)
documents content rendering and its focused tests; the [home app](../webapp/home/README.md)
documents homepage editing. The [core app](../webapp/core/README.md)
documents per-site navigation. Add guidance for other apps when working on them,
following the documentation standards.

`make test` runs Django application tests. See [testing and verification](testing.md)
for current coverage and the scope of future tests.

## Source

Guidance adapted from [agentic-wagtail-docs](https://github.com/nm-examples/agentic-wagtail-docs/tree/6ec46c12e720fbe90441eb3164caac720e838b48).
