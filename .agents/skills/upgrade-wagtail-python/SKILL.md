---
name: upgrade-wagtail-python
description: "Upgrade the Python backend in nickmoreton.co.uk with locked dependencies, aligned companion files, Docker/PostgreSQL verification, and concise maintenance notes. Use for this repository's Python, Django, Wagtail, or Python tooling upgrades."
---

# Upgrade this repository's Python backend

Use only in `nickmoreton.co.uk` (`[project].name = "nickmoreton"`). Read the root
`AGENTS.md` and [the companion-file checklist](references/companion-files.md).
Read `docs/python-upgrade.md` if it exists; maintain it as a short, current
maintenance note. Treat previous versions and results as historical evidence,
not future targets. Respect the
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
checks, migration checks, and existing tests on the original lockfile. Follow
the testing scope in `AGENTS.md`: add coverage only for a missing custom rule
affected by the upgrade, using a focused function, method, or component test.
Do not add framework, end-to-end, admin workflow, generic rendering, rendition,
or legacy-removal tests to establish an upgrade baseline. Mock external
requests in custom integration code. Retain baseline warnings for comparison.

## Freeze version-selection inputs

Before resolving, save detailed selection inputs in ignored scratch files:

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

In `docs/python-upgrade.md`, summarize only the chosen runtime/framework/tool
versions and meaningful compatibility decisions. Link to authoritative release
notes when useful. Keep package tables, inventories, hashes, raw logs and
per-file checklists in scratch; Git and the manifest/lock/Dockerfile already
preserve the exact configuration. Do not duplicate them in the document.

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

## Handle breaking changes

Review upstream release notes and migration guides between installed and target
versions for changed direct dependencies and relevant transitives, including
minor/patch releases. Map removed APIs, changed defaults/configuration, runtime
requirements and data changes to actual repository usage.

Implement necessary compatibility fixes within the authorized upgrade scope.
Verify affected behaviour directly. Add a focused regression test only when a
custom rule lacks coverage, following `AGENTS.md`; do not test upstream methods
or add end-to-end workflows. Use configuration, migration, build, and manual
checks for the relevant operational verification. A successful install or broad
test pass alone does not establish compatibility.

Flag unresolved incompatibilities and decisions outside scope to the developer
when identified. Give the package/version transition, upstream evidence,
affected code or workflow, impact and recommended options. Pause only work that
depends on that decision; continue independent work. Do not silently bypass
checks or force unsupported versions. Summarize resolved fixes, intentional
behaviour changes and remaining risks in the handoff and short maintenance note.

## Resolve and validate in stages

Before the first resolution, persist the recorded cutoff and prerelease policy
in `pyproject.toml` so plain Docker/CI commands use the same resolver inputs:

```toml
[tool.uv]
exclude-newer = "<recorded RFC 3339 UTC cutoff>"
prerelease = "explicit"
```

Replace the placeholder with the selection record's timestamp and merge into
any existing `[tool.uv]` table. Persist any other non-default resolution settings
used by the run too. CLI-only settings are insufficient: uv records them in the
lockfile, and a later plain `uv lock --check` or `uv sync --locked` can reject
the lock when project configuration differs. Keep the manifest, selection record,
and resolver flags aligned; advance the cutoff only for a deliberate new selection.

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

Review every row in [companion-files.md](references/companion-files.md). Keep
per-file dispositions in scratch; document only consequential exceptions.
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
   baseline/verification commands in the companion checklist. Keep detailed
   output in scratch and summarize actual results in `docs/python-upgrade.md`.
2. Before migrating existing local data, make ignored backups and rehearse on a
   disposable PostgreSQL copy following `docs/data-and-media.md`. Record
   `migrate --plan`; distinguish dependency migrations from project migrations.
3. After a successful rehearsal, migrate locally, run `make collectstatic`, and
   run `python manage.py update_index` inside `app`.
4. Run `make prod-run`; it builds, migrates, collects static files, and recreates
   `prod-app`. Reindex in `prod-app`; confirm actual versions and `DEBUG=False`.
   Smoke-test OrbStack HTTPS, home/search, Wagtail login, hashed CSS/JS/favicons,
   and an existing media rendition through nginx.
5. If a manual editor check is needed for an upgrade compatibility issue, use
   isolated content, not live content; do not add an automated editor journey.
   Record the limits of S3/Unveil/live Heroku checks requiring configured access.
6. Remove the disposable database. Keep ignored backups for the agreed review/
   rollback window and remove them after use; never commit dumps.

## Hand off for review

Capture final inventory and lockfile SHA-256 in scratch; compare accepted
versions with the selection inputs. Update badges, repository guidance and
`CHANGELOG.md` under `Unreleased`.

Keep `docs/python-upgrade.md` to a short current summary (roughly one page):
supported versions and reasons for notable choices, dated verification results
and limitations, required migration/reindex/static steps, and any unusual
database-aware rollback requirements. Replace superseded run details instead
of appending an audit report for every upgrade; Git retains earlier records.
Link to existing operational docs rather than copying their procedures. Do not
report historical tests as newly executed. Add detail only when a real migration
or compatibility issue requires it, or the user requests an audit report.

Present the reviewable diff. Follow `AGENTS.md` for commit, push, PR, release-date,
and deployment authorization. Package-upgrade approval does not imply commit or
deployment approval. Honor the agreed review checkpoint before the Node phase.
