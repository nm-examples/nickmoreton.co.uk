# Python backend upgrade — 18 October 2026

## Frozen selection inputs

- Base: `e41db71` (`redesign-integration`); clean tree, feature branch `upgrade-python-backend`.
- Baseline lock SHA-256: `2b4696e5d6c6c28961706580b6b94edd7021266324e0f0d7c55b1749fed75c9f`.
- Release cutoff: **2026-10-18T20:40:43Z**. All selections checked against PyPI upload timestamps and non-yanked artifacts before this cutoff.
- User-approved lines: **Python 3.14, Django 6.0, Wagtail 7.4 LTS**. Exact runtime **Python 3.14.8**, resolver **uv 0.13.1**. Python 3.15 and Wagtail 8 are outside the approved matrix/policy.
- Index: `https://pypi.org/simple`; no custom indexes, sources or credentials. Resolution `highest`; prereleases `explicit`. Retain Unveil exactly at `0.1.0a7`. Resolver inputs are persisted in `[tool.uv]` before resolution.
- Docker: `python:3.14.8-trixie@sha256:446efb4225200a0a196707aa7953898b37962fd3b8859a636035de3af657081e`.
  Verified OCI multi-platform index with `docker buildx imagetools inspect`, including Linux amd64 and arm64/v8. Debian 13 Trixie is current stable.
- uv image: `ghcr.io/astral-sh/uv:0.13.1@sha256:4a1f3666816dafadd20ceb71eac9a7d56d7ef30279f7d64048519ab901ada336`, verified amd64/arm64 index.
- Stages: refresh runtime/dev dependencies and Wagtail 7.3.4 on Python 3.13.16; upgrade one Wagtail feature release to 7.4.3; move Python to 3.14.8 and constrain the supported runtime to `>=3.14,<3.15`.

## Direct package selections

Exact versions are in `uv.lock`; manifest ranges permit updates only inside the intended support lines. Unchanged dependencies are deliberately retained at their newest stable release before the cutoff.

| Package | Baseline | Selected | Final declared range | Rationale |
| --- | --- | --- | --- | --- |
| `dj-database-url` | 3.1.2 | 3.1.2 | `>=3.1.2,<4` | Already latest stable before cutoff; retain. |
| `django` | 6.0.4 | 6.0.9 | `>=6.0.9,<6.1` | Newest patch in approved 6.0 line. |
| `django-browser-reload` | 1.21.0 | 1.21.0 | `>=1.21.0,<2` | Already latest stable before cutoff; retain. |
| `django-storages` | 1.14.6 | 1.14.6 | `>=1.14.6,<2` | Already latest stable before cutoff; retain. |
| `gunicorn` | 25.3.0 | 26.2.0 | `>=26.2.0,<27` | Latest stable, major update; verify gthread behind nginx. |
| `psycopg2` | 2.9.12 | 2.9.13 | `>=2.9.13,<3` | Latest stable before cutoff; validate with framework regression checks. |
| `requests` | 2.33.1 | 2.34.2 | `>=2.34.2,<3` | Latest stable before cutoff; validate with framework regression checks. |
| `wagtail` | 7.3.1 | 7.4.3 | `>=7.4.3,<7.5` | Approved LTS; 7.3.4 intermediate, then one feature release. |
| `wagtail-unveil` | 0.1.0a7 | 0.1.0a7 | `==0.1.0a7` | Retain existing prerelease exactly; no blanket prerelease opt-in. |
| `whitenoise` | 6.12.0 | 6.12.0 | `>=6.12.0,<7` | Already latest stable before cutoff; retain. |
| `django-upgrade` | 1.30.0 | 1.33.0 | `>=1.33.0,<2` | Latest stable before cutoff; validate with framework regression checks. |
| `pre-commit` | 4.6.0 | 4.7.0 | `>=4.7.0,<5` | Latest stable before cutoff; validate with framework regression checks. |
| `pyupgrade` | 3.21.2 | 3.22.0 | `>=3.22.0,<4` | Latest stable before cutoff; validate with framework regression checks. |
| `ruff` | 0.15.12 | 0.17.1 | `>=0.17.1,<0.18` | Latest stable before cutoff; validate with framework regression checks. |

Compatibility and release evidence:

- [Wagtail compatibility matrix](https://docs.wagtail.org/en/stable/releases/upgrading.html#compatible-django-python-versions): 7.4 LTS supports Django 5.2/6.0 and Python through 3.14.
- [Wagtail 7.4 upgrade considerations](https://docs.wagtail.org/en/stable/releases/7.4.html): StreamField adds `w-block-` classes alongside legacy classes; Django 4.2 removed; custom content checker and undocumented header APIs reviewed. This site does not use those custom admin APIs.
- [Wagtail 7.4.3](https://docs.wagtail.org/en/stable/releases/7.4.3.html), [Django 6.0.9](https://docs.djangoproject.com/en/6.0/releases/6.0.9/), [Django Python support](https://docs.djangoproject.com/en/6.0/faq/install/), [Python 3.14.8](https://www.python.org/downloads/release/python-3148/).
- [Heroku Python support](https://devcenter.heroku.com/articles/python-support): Python 3.14 supported; deployment itself is not part of this local upgrade.
- [Debian stable](https://www.debian.org/releases/stable/).
- Each direct package's version-specific `https://pypi.org/pypi/<package>/<version>/json` was inspected for Python requirements, dependencies, timestamps and yanks. Those machine-readable selection inputs and inventories are saved in ignored `db_backups/python-upgrade-20261018/`.

## Baseline

Running development stack: Python 3.13.16, uv 0.13.1, PostgreSQL 16. Production-mode stack initially stopped. Host Python/uv differ and are not used for app verification.

Original lock: `uv lock --check`, Ruff format/lint, Django `check`, migration check, and original one-test suite pass. No baseline configuration or migration warnings. Added regression coverage exercises live/draft rendering, real saved-draft preview content, editor publishing, chapter navigation, PostgreSQL search/pagination, navigation/PyPI tags (mocked HTTP), StreamField blocks, JPEG/WebP renditions. Wagtail 7.3 emits rendition `ResourceWarning` about unclosed temporary files; retain as baseline for comparison.

## Additional compatibility decisions

- Gunicorn's website lists 26.2.1/26.2.2, but PyPI has no artifacts for these versions at selection time. 26.2.0 is the newest installable stable release in the selected index. [Gunicorn's changelog](https://gunicorn.org/news/) removes Eventlet in 26.0; this project uses gthread and does not enable HTTP/2.
- [Pillow 13 release notes](https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html) reviewed, including removed image APIs; the site does not call those APIs. JPEG and WebP rendition regression tests pass. cp314 manylinux wheels exist for Pillow 13.0.0, pillow-heif 1.8.1 and PyYAML 6.0.3 on both amd64 and arm64. psycopg2 is built from its locked source distribution against libpq.
- With Wagtail 7.4 allowing Treebeard 5, select `django-treebeard==5.3.1` before the Python change rather than retain 4.8 (which predates official Python 3.14 support). [Treebeard changes](https://django-treebeard.readthedocs.io/en/latest/changes.html) reviewed: internal node handlers/forms changed in 5.0; this site uses public Wagtail tree APIs. Chapter/editor tests exercise those paths.
- Filelock 4, virtualenv 21, packaging 26 and soupsieve 3 are major transitive updates. They satisfy the owning packages' metadata; they are covered by hook/environment validation, framework startup, HTML rendering and image/editor tests as applicable.
- [Heroku uv detection](https://devcenter.heroku.com/articles/python-behavior-in-heroku) supports `uv.lock`; [multiple manager files are rejected](https://devcenter.heroku.com/changelog-items/3510). Remove CI's obsolete requirements export. Keep the Node-then-Python buildpack order and release migration command.

## Verification and operational record

Commands ran locally in Docker Compose, against PostgreSQL 16:

| Stage/check | Result |
| --- | --- |
| Original-lock checks and original placeholder suite | Passed; no configuration/migration warnings. |
| New regression coverage against original lock | Ten tests passed before dependency changes. |
| Stage 1: full refresh on Python 3.13.16 / Wagtail 7.3.4 | Locked sync, Django/migration checks and regression suite passed. |
| Stage 2: Wagtail 7.4.3, then Treebeard 5.3.1 on Python 3.13.16 | Both targeted updates passed checks and regression suite. |
| `make build` then `make up` | Passed; recreated app reports Python 3.14.8 / uv 0.13.1. |
| `uv lock --check`, `uv sync --locked` inside rebuilt app | Passed without lock changes. |
| `ruff format --check .`, `ruff check .` | Passed (47 Python files). |
| pyupgrade `--py314-plus`, django-upgrade `--target-version 6.0` | Passed across repository Python files, including the new untracked test; no rewrites needed. |
| `python -Wa manage.py check` | No issues. |
| `python manage.py makemigrations --check --dry-run` | No project model changes. |
| `python -Wa manage.py test --noinput` | Ten PostgreSQL regression tests passed. |
| Local DB custom dump → disposable `python_upgrade_rehearsal` DB | Restored; migration plan reviewed, migrations applied, 53 objects reindexed; home content/search/login rendered. Disposable DB removed. |
| `make migrate`, `make collectstatic`, `update_index` in app | Passed after successful migration rehearsal. |
| `make prod-run` | Passed: built image, migrated blank isolated production-mode DB, collected static, started Gunicorn/nginx. |
| Gunicorn `--check-config --config gunicorn.conf.py webapp.wsgi` | Passed; running Gunicorn reports gthread. |
| Versions and settings in recreated `prod-app` | Python 3.14.8, uv 0.13.1, Django 6.0.9, Wagtail 7.4.3, `DEBUG=False`. |
| `update_index` in `prod-app` | Passed; blank production-mode DB indexes two initial pages. |
| Production-mode regression suite | All ten tests passed, including isolated editor publishing/preview; no live content edited. |
| OrbStack HTTPS/nginx | Home/search/login and hashed CSS, JS, touch icon and SVG/PNG favicons returned successfully. Existing local rendition copied temporarily to isolated media mount, fetched byte-for-byte through nginx, then copy removed. |
| Linux amd64 image build and native checks | Built the same pinned Dockerfile for amd64; JPEG/PNG/WebP/HEIF encode/decode and source-built psycopg2/libpq checks passed on x86_64/glibc 2.41. |
| Linux amd64 framework checks | Accepted lock check, Django/migration checks, collectstatic and all ten PostgreSQL regression tests passed under amd64 emulation. |
| Native arm64 checks | JPEG/PNG/WebP/HEIF encode/decode and psycopg2/libpq passed on aarch64/glibc 2.41. |
| pre-commit Python hooks | Config validation, uv-lock, Ruff check/format, django-upgrade and pyupgrade all passed; uv hook validated accepted lock without resolving. |

Warnings: Wagtail emits the same two unclosed temporary rendition-file
`ResourceWarning` messages seen before the upgrade. No new configuration or
migration warnings. They do not prevent successful JPEG/WebP rendition reads.
Gunicorn also logged an OrbStack service-detection HEAD request rejected with
400 and discarded its body; the real hostname GET smoke requests all passed.

The initial in-place `uv sync --locked` needed root to update the image-owned
`/opt/.venv`; retried as root, then all checks ran as the normal app user. The
final image installs dependencies during its build and a normal-user locked
sync is a no-op. An early smoke assertion incorrectly expected the home model's
title in a template that does not render it; corrected to assert the actual
Articles/Packages content and reran successfully.

Resolution used uv 0.13.1 and the recorded cutoff, `highest` and `explicit`
policies at every stage. Stage 1 used `--upgrade` and exact `--upgrade-package`
targets for all direct packages (Wagtail 7.3.4 as intermediate). Stage 2 targeted
`wagtail==7.4.3` and `django-treebeard==5.3.1` separately. Stage 3 changed Python
and resolved without a further upgrade. Later verification used only `--check`
and `--locked`. Ignored logs contain the exact operations and outputs.

Hosted GitHub Actions, a live Heroku deploy, S3 access and external Unveil report
submission were not run. Their repository integration was reviewed; all local
runtime/editor/search/image paths above were exercised. No remote data/media
sync was used. The new production-mode DB is separate from development.

## Complete lock graph comparison

Baseline lock schema 1/3; final 1/5. Python range `>=3.13` → `==3.14.*`. Global resolution markers: `[]` → `[]`. All registry sources remain PyPI; project source remains virtual. Artifact URLs/hashes were refreshed for accepted versions, with no alternate indexes.

| Package | Baseline | Accepted | Markers |
| --- | --- | --- | --- |
| `anyascii` | 0.3.2 | 0.3.3 | `[]` |
| `asgiref` | 3.11.1 | 3.12.1 | `[]` |
| `beautifulsoup4` | 4.13.3 | 4.15.0 | `[]` |
| `boto3` | 1.37.13 | 1.43.114 | `[]` |
| `botocore` | 1.37.13 | 1.43.114 | `[]` |
| `certifi` | 2025.1.31 | 2026.10.18 | `[]` |
| `cfgv` | 3.4.0 | 3.5.0 | `[]` |
| `charset-normalizer` | 3.4.1 | 3.5.2 | `[]` |
| `distlib` | 0.3.9 | 0.4.4 | `[]` |
| `django` | 6.0.4 | 6.0.9 | `[]` |
| `django-filter` | 25.1 | 26.2 | `[]` |
| `django-modelcluster` | 6.4.1 | 6.5 | `[]` |
| `django-stubs-ext` | 5.1.3 | 6.1.2 | `[]` |
| `django-tasks` | 0.9.0 | 0.12.0 | `[]` |
| `django-treebeard` | 4.7.1 | 5.3.1 | `[]` |
| `django-upgrade` | 1.30.0 | 1.33.0 | `[]` |
| `djangorestframework` | 3.15.2 | 3.18.3 | `[]` |
| `draftjs-exporter` | 5.1.0 | 5.2.0 | `[]` |
| `filelock` | 3.18.0 | 4.2.2 | `[]` |
| `gunicorn` | 25.3.0 | 26.2.0 | `[]` |
| `identify` | 2.6.9 | 2.6.20 | `[]` |
| `idna` | 3.10 | 3.20 | `[]` |
| `jmespath` | 1.0.1 | 1.1.0 | `[]` |
| `modelsearch` | 1.1.1 | 1.3.2 | `[]` |
| `nodeenv` | 1.9.1 | 1.11.0 | `[]` |
| `packaging` | 24.2 | 26.3 | `[]` |
| `pillow` | 11.1.0 | 13.0.0 | `[]` |
| `pillow-heif` | 1.3.0 | 1.8.1 | `[]` |
| `platformdirs` | 4.3.6 | 4.13.4 | `[]` |
| `pre-commit` | 4.6.0 | 4.7.0 | `[]` |
| `psycopg2` | 2.9.12 | 2.9.13 | `[]` |
| `python-discovery` | added | 1.6.3 | `[]` |
| `pyupgrade` | 3.21.2 | 3.22.0 | `[]` |
| `pyyaml` | 6.0.2 | 6.0.3 | `[]` |
| `requests` | 2.33.1 | 2.34.2 | `[]` |
| `ruff` | 0.15.12 | 0.17.1 | `[]` |
| `s3transfer` | 0.11.4 | 0.19.2 | `[]` |
| `soupsieve` | 2.6 | 3.0.3 | `[]` |
| `sqlparse` | 0.5.3 | 0.6.0 | `[]` |
| `tokenize-rt` | 6.1.0 | 6.2.0 | `[]` |
| `typing-extensions` | 4.12.2 | 4.16.0 | `[]` |
| `tzdata` | 2025.1 | 2026.5 | `[]` |
| `urllib3` | 2.3.0 | 2.8.0 | `[]` |
| `virtualenv` | 20.29.3 | 21.14.11 | `[]` |
| `wagtail` | 7.3.1 | 7.4.3 | `[]` |

Final accepted lock SHA-256: `da4cdb39fe8bd20b28e81288a404f9409d8c9dff816db9cbca0f1cdda9a7cda4`. 61 → 62 package records. No package removals except marker variants explicitly shown above.

stage1 inventory SHA-256: `c6dc1e639b78647517fa6d04168b17ecc9e634aaa2725e147d4bf5584197fba0`.

stage2 inventory SHA-256: `4cc03cc8dd81bbcbe3793552ad02dad3534e547626ef1cfb0a34d24cd9eb5208`.

## Companion-file dispositions

| File(s) | Disposition | Reason |
| --- | --- | --- |
| `pyproject.toml` | updated | Bounded dependency/runtime lines, Python 3.14 Ruff target, frozen resolver inputs. |
| `uv.lock` | updated | Full refresh, accepted artifact hashes and Python 3.14 graph; complete comparison above. |
| `.python-version` | updated | 3.14 line for Heroku/local/CI; Docker pins patch 3.14.8. |
| `docker/Dockerfile` | updated | Python patch/Trixie and uv OCI index digests; locked install. libpq/JPEG/WebP/zlib build dependencies retained. Node stage untouched. |
| `.github/workflows/test.yml` | updated | uv pin, read-only lock validation, locked runs, PostgreSQL 16 service, built/collected assets before framework tests; obsolete requirements export removed. |
| `.pre-commit-config.yaml` | updated | Python hook versions aligned; uv checks the lock; pyupgrade uses Python 3.14; Django target stays 6.0. Biome unchanged. |
| `AGENTS.md` | updated | Approved Python/Wagtail targets and regression-test pointer. Commit/data rules retained. |
| `README.md` | updated | Version badges, requirements, accepted-lock workflow, uv pin and upgrade-record link. |
| `CHANGELOG.md` | updated | Upgrade, reproducibility and regression coverage under Unreleased. |
| `docs/python-upgrade.md` | added | Selection, compatibility, graph comparison, verification and rollback evidence. |
| `docs/local.production.md` | checked unchanged | Same production-mode commands and OrbStack URL. |
| `docs/data-and-media.md` | checked unchanged | Existing backup/restore paths and PostgreSQL custom dumps remain valid; local disposable rehearsal recorded below. |
| `docker-compose.yaml` | checked unchanged | Source bind mount; virtualenv remains image-installed under `/opt/.venv`; PostgreSQL 16 unchanged. |
| `docker-compose.production.yaml` | checked unchanged | Gunicorn production settings, isolated DB/media and nginx paths unchanged. PostgreSQL/nginx versions outside scope. |
| `gunicorn.conf.py` | checked unchanged | gthread still supported, no Eventlet or HTTP/2 configuration; verify nginx behavior. |
| `Procfile` | checked unchanged | Web/release migration commands valid; reindexing remains a separate deployment action. |
| `app.json` | checked unchanged | Node then Python buildpacks; `uv.lock` detection supported by Heroku. Actual hosted deploy not performed. |
| `webapp/settings/{base,dev,production}.py` | checked unchanged | PostgreSQL/modelsearch, storage/static middleware and Unveil APIs remain compatible. No secrets inspected. |
| `webapp/urls.py` | checked unchanged | Wagtail admin/documents/site and Unveil imports still supported. |
| `webapp/{home,pages,core}/models.py`, `webapp/pages/blocks.py` | checked unchanged | Public panels/StreamField/tree APIs exercised; no project model changes needed. |
| App migrations, templates and tags | checked unchanged | Migration check; rendering, navigation, PyPI tags and image blocks covered; no custom deprecated Wagtail admin APIs. |
| App tests | updated | Replace placeholder test with ten meaningful PostgreSQL regression tests in `webapp/pages/test_upgrade.py`. |

The hidden/tracked-file search found no other active Python pins. Node/npm,
Biome, PostgreSQL and nginx upgrades remain outside this phase.

## Migration, deployment and rollback

The existing development data needed these **dependency** migrations (no new
project migrations):

- `wagtailadmin.0006_formstate`: editor form state.
- `wagtailcore.0097_baselogentry_uuid_action_timestamp_indexes`: log indexes.
- `wagtailsearch.0010_add_text_fields`: title/body fields and SQL changes for search.

The disposable restored DB successfully applied the plan before the real local
DB. Reindex after migration because the search schema changed. Build/collect
static assets after upgrading Wagtail so admin assets and manifest hashes agree.
Normal local order: `make build`, `make up`, `make migrate`,
`make collectstatic`, then `docker compose exec -T app python manage.py update_index`.
Production-mode order: `make prod-run`, then
`docker compose -f docker-compose.production.yaml exec -T prod-app python manage.py update_index`.
Heroku's existing release process handles migrations; arrange its search reindex
as a separate deployment operation. Back up the remote DB/media first when an
actual deployment is authorized. No deployment or commit is authorized by this
upgrade request.

### Local development rollback — Docker Compose only

**The rollback procedure below describes local development only.** Both the
normal `app`/`db` stack and the `prod-app`/`prod-db`/nginx stack run on this
computer. “Production mode” here means local `DEBUG=False` verification; it is
separate from the live Heroku production instance. The commands below address
only Docker Compose services and the local `webapp` database. Verification
covered restoring a local dump into a disposable DB and applying the upgrade;
an end-to-end switch back to the earlier runtime was not performed.

Local rollback snapshots are ignored under
`db_backups/python-upgrade-20261018/`: `development-before.dump` and
`production-mode-before.dump` (the latter was an empty, newly created isolated
local DB). These are **local snapshots, not verified Heroku production recovery
backups**. Keep them for this review/rollback window, then remove them. The
disposable rehearsal DB has been dropped. Existing local media was not replaced;
the temporary production-mode rendition copy was removed after its HTTP check.

For a local rollback, stop the relevant app/nginx writers, restore the matching
pre-upgrade local DB dump, and rebuild the matching earlier code/lock/base image.
Do not point the old Wagtail version at a forward-migrated database or rely on
unverified reverse migrations. The original development image is locally tagged
`nickmoreton-python-upgrade-baseline:20261018` as a temporary fallback.

For the normal development stack, the following replaces **only its local DB**:

```bash
docker compose stop app
docker compose exec -T db dropdb -U postgres --force webapp
docker compose exec -T db createdb -U postgres webapp
docker compose exec -T db pg_restore --no-owner --no-acl -U postgres -d webapp \
  /db_backups/python-upgrade-20261018/development-before.dump
```

Then select the baseline code/lock, rebuild/start its local image, recollect its
static files and rebuild its search index. Restore local media from a matching
backup if subsequent editing has changed it. For the separate local production-
mode stack, use `docker-compose.production.yaml`, stop `prod-app` and `prod-nginx`,
and restore its `production-mode-before.dump` through `prod-db` instead. Neither
workflow operates on Heroku, and the local baseline Docker image is not a Heroku
release artifact.

### Applying the rollback evidence to Heroku production

This section is a planning checklist for a separately authorized production
rollback. **No Heroku rollback, restore, backup or deployment was executed during
this upgrade.** The local rehearsal demonstrates the migration path; production
recovery still needs the actual Heroku release, database and media recovery
points. The local base commit is not automatically the currently deployed Heroku
commit.

1. Before deployment, record the production app identity, deployed release ID and
   commit, database attachment, verified pre-upgrade recovery point and timestamp,
   and matching S3/media recovery arrangements. Record the process formation and
   required configuration securely. Confirm the earlier release artifact is still
   available, or prepare a tested rebuild of its code, Python and dependency set.
2. If rollback is needed, place the site in maintenance mode and stop all database
   writers, including web/worker dynos, scheduled jobs and one-off processes.
   Maintenance mode alone does not stop background writers. Preserve the current
   database/media state before replacing it, and decide how to reconcile content
   created since the selected recovery point.
3. Restore or recover the **Heroku production database** to the chosen compatible
   pre-upgrade state, preferably rehearsing against a separate database first.
   Choose the recovery method supported by the actual Postgres plan. A PGBackups
   restore replaces all data in its target; a Postgres point-in-time rollback
   provisions a separate database that must be validated and promoted. Check the
   destination identity explicitly. Do not substitute either local dump above.
   See [PGBackups](https://devcenter.heroku.com/articles/heroku-postgres-backups)
   and [Postgres rollback](https://devcenter.heroku.com/articles/heroku-postgres-rollback).
4. Coordinate the matching application release with that restored database while
   writers remain stopped. A Heroku release rollback restores the prior slug/OCI
   image and configuration; database contents and S3/media need separate recovery.
   Check database attachment/configuration compatibility **before** rolling back,
   since add-on config vars also revert. Prefer a tested revert/redeploy when
   appropriate; use an available prior release only when its artifact and config
   match the recovery plan. Expired release artifacts cannot be rolled back to.
   See [Heroku releases](https://devcenter.heroku.com/articles/releases).
5. Account for this repository's `release: python manage.py migrate --no-input`:
   Heroku also runs the release phase on release rollback. Ensure its migration
   command will target the intended restored database with compatible code before
   initiating it. A failed release does not prove the database was untouched;
   inspect applied migrations and release logs. Do not run untested reverse
   migrations on production. See [release phase](https://devcenter.heroku.com/articles/release-phase).
6. Verify the release's actual Python/Django/Wagtail versions, migration state,
   configuration and storage destinations. Rebuild search with the matching code
   (`python manage.py update_index` in the intended Heroku app), verify that the
   release contains the matching collected static assets, and check home/search,
   login, isolated editor preview/publishing and media renditions. Restore S3/media
   only if required by the chosen data recovery point. Resume the recorded process
   formation and remove maintenance mode after these checks pass.

Use explicit production app, release and database identifiers for any eventual
Heroku CLI operations; obtain them from the deployment/recovery record, not from
the example local names. Keep recovery credentials and backup URLs out of this
repository. This record's package selections, migration list, local test results
and verification steps assist that production plan without claiming it was
rehearsed on the live instance.

The pinned base index and Python artifact hashes stabilize important inputs;
APT repositories and native build tools remain separate changing inputs. This
record does not claim the whole Docker build is deterministic.
