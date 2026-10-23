# Repository guidance

Read [the contributor workflow](docs/contributing.md) before editing or committing.
The linked documents contain this repository's detailed requirements; read those
relevant to the work before starting.

For every code change, including code removal, check for affected documentation and
agent guidance and update it in the same change. Follow the
[documentation maintenance rules](docs/documentation.md#keeping-docs-and-guidance-aligned).

| Work | Required references |
| --- | --- |
| Application code, models, page hooks, queries, integrations, or admin extensions | [Architecture and conventions](docs/architecture.md), [testing and verification](docs/testing.md), and the relevant app's `README.md` when present. |
| Source documentation or app READMEs | [Documentation standards](docs/documentation.md). Add or update app guidance when behavior, structure, or extension points change. |
| Local setup, commands, or frontend watching | [README](README.md). |
| Production-like local verification or deployment preparation | [Production-mode checks](docs/local.production.md). |
| Python, Django, Wagtail, or Python tooling upgrades | [Python maintenance](docs/python-upgrade.md) and the [Python upgrade skill](.agents/skills/upgrade-wagtail-python/SKILL.md). |
| Node, npm, frontend dependency, or Biome upgrades | [Node maintenance](docs/node-upgrade.md) and the [Node upgrade skill](.agents/skills/upgrade-node-frontend/SKILL.md). Keep Python image changes separate. |
| Data, media, backups, or environment configuration | [Data and media workflows](docs/data-and-media.md). Never commit real secrets or production dumps. |

Only commit after developer review and approval. Pushes and pull requests require
the developer's instruction. Preserve existing work and follow the developer's
branch choice.

Use [the documentation index](docs/README.md) to find other project references.
