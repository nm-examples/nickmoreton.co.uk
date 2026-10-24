# Python backend maintenance

## Supported versions

| Component | Current version |
| --- | --- |
| Python | 3.14.8 |
| Django | 6.0.9 |
| Wagtail | 7.4.4 LTS |
| uv | 0.13.4 |

Keep Python 3.14, Django 6.0 and Wagtail 7.4 LTS until a deliberate compatibility
review changes those targets. Retain `wagtail-unveil==0.1.0a7` unless a replacement
is explicitly selected.

The 20 October 2026 refresh applies [Wagtail 7.4.4 security fixes](https://raw.githubusercontent.com/wagtail/wagtail/v7.4.4/docs/releases/7.4.4.md),
updates uv and compatible dependency patches, and retains the existing framework
lines. [Wagtail's compatibility table](https://docs.wagtail.org/en/stable-7.4.x/releases/upgrading.html#compatible-django-python-versions)
guides future selections.

Exact dependencies, resolver cutoff/policies and image digests live in
[`pyproject.toml`](../pyproject.toml), [`uv.lock`](../uv.lock) and
[`docker/Dockerfile`](../docker/Dockerfile). Routine installs use `uv sync --locked`;
validate with `uv lock --check`. Advance the cutoff only for a deliberate refresh.
Docker, CI and pre-commit must use the same uv version. Keep detailed inventories
and logs in ignored scratch files; Git preserves previous upgrade records.

## Upgrade workflow

For Python, Django, Wagtail, or Python tooling upgrades, use the repository's
[Python upgrade skill](../.agents/skills/upgrade-wagtail-python/SKILL.md) to record
exact version selections, align companion files, and verify the Docker stacks.
Follow [the testing scope](testing.md) for application coverage, and keep Node
runtime and frontend dependency changes in their separate upgrade phase.

## Verified on 20 October 2026

- Baseline and upgraded development stacks: all 48 PostgreSQL tests passed,
  including live/draft rendering, editor publishing, search, tags and renditions.
- Rebuilt Docker stacks: locked installs, Ruff, pyupgrade, django-upgrade and
  Python pre-commit hooks passed; configuration and migration checks passed.
- Restored local database into a disposable copy, applied pending migrations,
  reindexed 49 objects and checked home/search/login before migrating locally.
  The disposable database was removed afterward.
- Production mode: all 48 tests passed with `DEBUG=False`; Gunicorn configuration,
  reindexing, OrbStack HTTPS, hashed CSS/JS/icons and a media rendition passed.
- Linux arm64 and amd64: Docker builds, JPEG/PNG/WebP/HEIF encoding/decoding and
  psycopg2 connections passed. The amd64 stack also passed all 48 tests.

Wagtail's temporary rendition-file `ResourceWarning` messages also occur on the
baseline. No new configuration or migration warnings were found. Hosted CI,
live Heroku deployment, S3 and external Unveil submission were not exercised.

## Deployment and rollback

Deployments must apply all pending migrations, collect matching static assets
and rebuild the search index. Heroku's release phase runs migrations; reindexing
remains a separate action.

For local verification, use `make build`, `make up`, `make migrate`,
`make collectstatic`, then `docker compose exec -T app python manage.py update_index`.
For production mode, use `make prod-run`, then run `update_index` in `prod-app`.

For a dependency rollback, rebuild with the earlier code, lockfile and image
pins. This patch adds no database changes requiring reversal. If reverting across
schema changes, stop writers and restore a compatible database/media snapshot;
do not rely on untested reverse migrations. A live rollback needs its own matching
release, database and media recovery points and authorization.
