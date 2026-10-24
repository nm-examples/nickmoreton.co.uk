# Developer documentation

This directory contains project-wide reference material that would otherwise
make the root `AGENTS.md` difficult to scan.

| Document | Purpose |
| --- | --- |
| [`architecture.md`](architecture.md) | Defines the project's Django and Wagtail code-placement boundaries. |
| [`documentation.md`](documentation.md) | Defines concise documentation ownership and maintenance rules. |
| [`testing.md`](testing.md) | Defines the scope of application tests and required code/build verification. |
| [`contributing.md`](contributing.md) | Defines branch, review, commit, changelog, and pull-request rules. |
| [`python-upgrade.md`](python-upgrade.md) | Records Python backend versions, verification, deployment, and rollback. |
| [`node-upgrade.md`](node-upgrade.md) | Records Node frontend versions, verification, and rollback. |

App READMEs provide orientation and editor workflows:
[home](../webapp/home/README.md), [pages](../webapp/pages/README.md), and
[core](../webapp/core/README.md). Implementation reasoning lives beside the code;
link to it rather than repeating it here.

## Source

Guidance adapted from [agentic-wagtail-docs](https://github.com/nm-examples/agentic-wagtail-docs/tree/6ec46c12e720fbe90441eb3164caac720e838b48).
