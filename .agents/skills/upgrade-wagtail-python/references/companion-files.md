# Companion files in nickmoreton.co.uk

Read during inventory and revisit before handoff. Keep per-file dispositions in
ignored scratch files; mention only consequential exceptions in the short
maintenance note. Do not mechanically change unaffected files.

| File | What to check or align |
| --- | --- |
| `pyproject.toml` | Python range; exact runtime/dev selections and intended upper bounds; Ruff target; uv sources/indexes; persist `[tool.uv].exclude-newer` and `prerelease` to match the selection record and resolver flags. |
| `uv.lock` | All direct/transitive versions, hashes, source/marker changes, and uv lock format. Keep marker-specific variants separate. |
| `.python-version` | Release line for local tooling, CI, and Heroku; compatible with the Docker patch. |
| `docker/Dockerfile` | Python patch + Debian stable codename + multi-platform digest; uv pin; locked install; native libpq/JPEG/WebP/zlib dependencies. Node stage belongs to its own phase. |
| `.github/workflows/test.yml` | uv pin, Python version-file usage, PostgreSQL 16 service, read-only lock validation, locked installs/runs, static preparation, checks/tests. |
| `.pre-commit-config.yaml` | Ruff/uv/django-upgrade/pyupgrade revisions align with packages; Django target and minimum-Python flag align with runtime. Biome belongs to the Node phase. |
| `AGENTS.md`, `docs/{architecture,testing,contributing}.md`, `docs/python-upgrade.md` | Agent routing, supported Python/Django/Wagtail targets, testing scope, and review/commit rules agree with the project. Preserve data-handling rules in `docs/data-and-media.md`. |
| `README.md` | Version badges, requirements, uv pin, locked installation, and operational links. |
| `CHANGELOG.md` | Notable changes under `Unreleased`; date releases according to repository instructions when preparing PR/deployment. |
| `docs/python-upgrade.md` | Short current summary of supported versions, notable decisions, dated verification/limitations, deployment requirements and unusual rollback steps. Git preserves earlier records; keep detailed evidence in scratch. |
| `docs/local.production.md` | Production-mode commands, URLs, and assumptions remain valid. |
| `docs/data-and-media.md` | Backup/rehearsal/restore commands match the database/storage. Do not pull production data just to obtain test fixtures. |
| `docker-compose.yaml` | `app` runtime/env/volume assumptions and database compatibility; source bind mount versus image-installed virtualenv. |
| `docker-compose.production.yaml` | `prod-app` settings/Gunicorn command, isolated database/media volumes, nginx static/media serving. Do not automatically upgrade Postgres/nginx. |
| `gunicorn.conf.py` | Worker support and setting/default changes across versions; currently `gthread`. Verify behind nginx. |
| `Procfile` | Heroku web/release commands, migration release phase, separate reindex requirements. |
| `app.json` | Buildpack order, runtime detection, test command; verify actual hosting support for selected Python/uv. |
| `webapp/settings/{base,dev,production}.py` | Framework settings/middleware, database/search backends, storage/static handling, Unveil. Do not print secrets/local settings. |
| `webapp/urls.py` | Framework and third-party imports/integration routes. |
| `webapp/{home,pages,core}/models.py`, `webapp/pages/blocks.py` | Deprecations, panels, StreamField changes, required project migrations; read intervening Wagtail upgrade considerations. |
| App migrations, templates, template tags | Custom rendering/admin APIs and image/search compatibility. Do not copy dependency migrations into this project. |
| App tests | Follow `docs/testing.md`: focused coverage for custom queries, content processing, navigation, tags/blocks, and mocked external API handling. Do not add framework, end-to-end, generic rendering, editor workflow, image rendition, or legacy-removal tests. Show proposed test removals and retained custom coverage before committing. |

Use `rg --hidden` for discovery, excluding `.git`, virtualenvs, `node_modules`,
generated static/media, and backups. Inspect new CI/deployment configuration
added since this skill was written. Do not read `.env` to locate version pins.

## Selection evidence

Save detailed evidence in ignored scratch files or outside the checkout:

- Base commit; baseline lock hash; full UTC cutoff; exact Python/uv; compatibility
  lines; index identity and resolver policies.
- A direct-package table: **package / old exact version / selected exact version /
  declared range / rationale and official compatibility evidence**. Include all
  runtime/dev packages and retained prereleases.
- Complete transitive change list, preserving marker-specific variants.
- Docker Python patch tag and verified multi-platform digest.
- Companion-file dispositions, staged commands/results and final lock hash.

Summarize only notable choices, actual verification, deployment requirements and
unusual rollback steps in `docs/python-upgrade.md`. Do not copy package tables,
hashes, raw logs or the full companion checklist into the maintained note.

Do not reuse October 2026 versions as future targets. Select and record each
run's explicit targets, then preserve the accepted lockfile.

## Baseline and verification commands

These commands are available before an upgrade report has been created. Run
them against the starting stack and again after each relevant upgrade stage.
Wait for `make build` and `make up` to finish before executing inside `app`.

```bash
make build
make up
docker compose exec -T app python --version
docker compose exec -T app uv --version
docker compose exec -T app uv lock --check
docker compose exec -T app ruff format --check .
docker compose exec -T app ruff check .
docker compose exec -T app python -Wa manage.py check
docker compose exec -T app python manage.py makemigrations --check --dry-run
docker compose exec -T app python -Wa manage.py test --noinput
```

If the baseline uv cannot run `lock --check`, use a disposable copy of the
manifest and lockfile for its consistency check and record the limitation.
Never rewrite the baseline lockfile just to run a check. The existing
`requirements.txt` export step in CI may need removal when moving this project
to a consistent uv-only workflow; verify Heroku's actual package-manager detection.
