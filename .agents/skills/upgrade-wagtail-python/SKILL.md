---
name: upgrade-wagtail-python
description: "Upgrade the Python backend in nickmoreton.co.uk with recorded package selections, uv lockfile reproducibility, companion-file alignment, and Docker/PostgreSQL verification. Use for this repository's Python, Django, Wagtail, or Python tooling upgrades."
---

# Upgrade this repository's Python backend

Use only in `nickmoreton.co.uk` (`[project].name = "nickmoreton"`). Read the root
`AGENTS.md` and [the companion-file checklist](references/companion-files.md).
Read `docs/python-upgrade.md` if it exists; create it as the dated upgrade record
when beginning an upgrade if it does not. Treat existing notes'
versions and results as historical evidence, not future targets. Respect the
user's base branch and any Python/Node review checkpoint. Leave Node packages
and frontend sources for the Node phase unless included in the user's scope.

## Baseline

Check the branch, commit, working tree, and running Docker stacks before editing.
Keep existing work intact and use the appropriate feature branch. Run this
skill's `scripts/inventory.py` with Python 3.11+ and save its JSON in an ignored
scratch directory or outside the checkout. It reads this checkout without
importing the app, contacting an index, reading `.env`, or changing files. It
records all locked packages, including transitives/variants, and companion-file
hashes. Run it again after the upgrade to produce a reviewable comparison.

Record Python/uv versions inside `app`; host versions can differ. Run Django
checks, migration checks, and tests on the original lockfile. Add focused missing
regression coverage for rendering, live/draft content, PostgreSQL search, custom
tags/blocks, image renditions, and editor workflows where needed. Preview's
error page can return HTTP 200: assert the rendered draft title/body. Mock PyPI
requests in tests. Retain baseline warnings for comparison.

## Freeze version-selection inputs

Before resolving, add a dated selection record to `docs/python-upgrade.md`:

- Base commit and baseline `uv.lock` SHA-256.
- One full RFC 3339 UTC release cutoff timestamp for this upgrade.
- Exact Python patch and uv resolver version; chosen Django/Wagtail release
  lines; exact target versions for every direct runtime/dev dependency, including
  unchanged packages; reasons and compatibility evidence for those choices.
- Package-index identity, uv sources/index configuration, resolution strategy,
  and prerelease policy. Exclude credentials from the record.
- Exact Python Docker patch tag, Debian codename, and verified multi-platform
  index digest. Use the approved current Debian stable base, pinned by readable
  patch tag plus digest. Check the registry and native-library compatibility.

Use official Python/Django/Wagtail release notes and compatibility tables, actual
package-index artifacts, and deployment support. Choose the newest non-yanked
stable release available before the cutoff within approved compatibility lines.
Check native wheels/source builds for local Linux arm64 and CI/deployment amd64.
Use the agreed Wagtail LTS policy; do not assume the newest major is the target.
Keep an existing prerelease such as `wagtail-unveil` at its exact recorded version
unless a replacement is deliberately selected. Do not globally allow prereleases
to satisfy one package. Assess major transitive changes too.

The accepted `uv.lock` and artifact hashes make installs repeatable. A cutoff
reduces moving-index drift but cannot guarantee a fresh resolution against later
index metadata/yanks recreates the same graph. Do not claim the entire Docker
build is deterministic from a Python lock and base digest alone; apt repositories
and native builds are separate inputs.

## Resolve and validate in stages

Use the recorded uv version and cutoff for every resolution. Where compatibility
permits, refresh dependencies on the old Python first, upgrade Wagtail one feature
release at a time, then change Python. Adapt the order to the verified matrix;
do not create an unsupported intermediate stack.

Set the following variables from the recorded selections. A targeted update is:

```bash
uv lock --python "$UPGRADE_PYTHON" \
  --exclude-newer "$UPGRADE_CUTOFF" --resolution highest --prerelease explicit \
  --upgrade-package "django==$UPGRADE_DJANGO"
```

Repeat `--upgrade-package` with exact targets for the selected packages in that
stage, including retained prereleases where needed. Use full `--upgrade` only
for an agreed full refresh, with the same cutoff and explicit direct targets.
Confirm flags in the selected uv version's help. Inspect the complete graph before
accepting it. Never silently raise the cutoff or relax compatibility lines to
solve a conflict; identify the blocker and revise the recorded selection within
authorized scope.

After each stage, record direct/transitive additions, removals, exact version
changes, markers, and source changes from the inventory and lockfile diff. Keep
manifest ranges bounded to intended support lines; the lockfile carries exact
pins. Finish `uv sync --locked` before running checks. Run Django configuration,
migration checks, and regression tests with warnings enabled. Diagnose failures
before proceeding to the next stage.

Once accepted, use `uv lock --check` and `uv sync --locked` in verification,
Docker, and CI. Do not regenerate the lockfile in CI or run another unconstrained
resolution just to verify it. `--frozen` alone does not check manifest/lock consistency.

## Align indirect files

Review every row in [companion-files.md](references/companion-files.md). Record
`updated`, `checked unchanged`, or `not applicable`, with a reason for each.
Search tracked and hidden configuration for additional version declarations;
the helper's inventory is not a completeness guarantee. Run Ruff, pyupgrade,
and django-upgrade with the selected Python/Django targets, including new
untracked Python files. Align tooling packages with hook revisions. Keep Node,
Biome, Postgres, and nginx upgrades outside this phase unless explicitly in scope.

## Verify this project's local stacks

Use Docker Compose rather than an accidentally selected host interpreter. Wait
for each build and container recreation to finish before dependent checks;
an old container may still answer during recreation.

1. Run `make build`, then `make up`; verify Python/uv inside `app`. Run the
   baseline/verification commands in the companion checklist and record them in
   `docs/python-upgrade.md`.
2. Before migrating existing local data, make ignored backups and rehearse on a
   disposable PostgreSQL copy following `docs/data-and-media.md`. Record
   `migrate --plan`; distinguish dependency migrations from project migrations.
3. After a successful rehearsal, migrate locally, run `make collectstatic`, and
   run `python manage.py update_index` inside `app`.
4. Run `make prod-run`; it builds, migrates, collects static files, and recreates
   `prod-app`. Reindex in `prod-app`; confirm actual versions and `DEBUG=False`.
   Smoke-test OrbStack HTTPS, home/search, Wagtail login, hashed CSS/JS/favicons,
   and an existing media rendition through nginx.
5. Use isolated regression content for editor publishing, not live content.
   Record the limits of S3/Unveil/live Heroku checks requiring configured access.
6. Remove the disposable database. Keep ignored backups for the agreed review/
   rollback window and remove them after use; never commit dumps.

## Hand off for review

Capture final inventory and lockfile SHA-256; compare the accepted versions with
the selection record. Update badges, repository guidance, upgrade notes, and
`CHANGELOG.md` under `Unreleased`. Include commands/results, baseline warnings,
migration/reindex/static-file requirements, companion-file dispositions, and
database-aware rollback steps. Do not report historical tests as newly executed.

Present the reviewable diff. Follow `AGENTS.md` for commit, push, PR, release-date,
and deployment authorization. Package-upgrade approval does not imply commit or
deployment approval. Honor the agreed review checkpoint before the Node phase.
