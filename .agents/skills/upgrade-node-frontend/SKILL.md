---
name: upgrade-node-frontend
description: "Upgrade the Node runtime and frontend dependencies in nickmoreton.co.uk with locked installs, a pinned stable Debian Node image, Docker verification, and concise maintenance notes. Use for this repository's Node, npm, frontend build-library, or Biome upgrades; keep Python image and backend upgrades separate."
---

# Upgrade this repository's Node frontend

Use only in `nickmoreton.co.uk` (`package.json` name `nickmoreton`, with the
Django/Wagtail app under `webapp/`). Read root `AGENTS.md` and the
[companion-file checklist](references/companion-files.md). Read
`docs/node-upgrade.md` if it exists; maintain it as a short, current maintenance
note, creating it when needed.
Treat earlier version selections and verification results as history, not future
targets. Preserve the user's current scope and review checkpoint.

## Scope and baseline

Keep changes local unless the user authorizes otherwise. Follow `docs/contributing.md` for
branch selection and developer review before commits, pushes, or PRs. Do not
discard existing work to obtain a clean diff; record it separately from this
upgrade's changes. Stash only when useful, preserving the user's untracked work
as well as tracked edits.

This phase owns the Node frontend stage of `docker/Dockerfile`, npm packages,
Biome, and their companion files. Leave the Python image/stage, uv, Python
dependencies/hooks, Postgres, and nginx unchanged unless explicitly included.
In particular, a request to use the latest Debian Node image does not authorize
changing the Python base image.

Check the branch, base commit, worktree, and running local stacks. Run
`node .agents/skills/upgrade-node-frontend/scripts/inventory.mjs` before editing
and save the JSON outside the checkout or in ignored scratch storage. It reads
the manifest/lock, fingerprints sources and companion files, and preserves
platform-specific package paths without installing packages or reading secrets.
It does not inventory `node_modules`; verify installed versions separately.

Compare the actual `node --version` and `npm --version` with `.nvmrc`, package
engines, CI, and Docker. Select the project runtime explicitly with nvm or the
available version manager; do not change its global/default alias. Run a clean
`npm ci`, Biome, production asset build, and audit on the starting lockfile.
If the original runtime cannot run a check, record that limitation and the
runtime used. An incomplete installed tree is not evidence of a broken lockfile.
Capture baseline compiler warnings and audit findings.

## Record selections before resolving

Save detailed selection evidence in ignored scratch files or outside the checkout:

- Base commit, starting worktree state, baseline lock SHA-256, and full UTC
  selection timestamp; identify the registry without credentials.
- Exact Node patch, support line/status, npm version, and reasons. Prefer a
  supported LTS runtime; use the selected Node release's bundled npm unless a
  different npm version has a concrete benefit and is aligned everywhere.
- Every direct package's previous exact version, selected exact version,
  intended manifest range, engine requirements, and official compatibility
  evidence, including packages that stay unchanged.
- Latest Debian stable release/codename, supported official Node variant,
  readable exact Node patch tag, and verified multi-platform OCI index digest.
  Check `linux/arm64` and `linux/amd64` availability; distinguish manifest
  availability from architectures actually tested.
- Prerelease policy and intentional exceptions; whether any resolver time
  cutoff is actually applied. Do not describe a recorded timestamp as an npm
  cutoff or promise future resolution will reproduce today's graph.
- Relevant non-default npm resolution/install options. If the lock depends on
  flags such as `legacy-peer-deps` or `install-links`, preserve the same options
  for `npm ci` through non-secret project configuration rather than CLI-only
  flags that local, CI, Docker or Heroku installs will omit.

In `docs/node-upgrade.md`, summarize only supported runtime/tool versions,
notable compatibility decisions, dated verification results and limitations,
and deployment/rollback requirements. Keep it roughly one page. Git, the
manifest/lock and Dockerfile preserve exact configuration; do not duplicate
package inventories, hashes, image digests, raw logs or per-file checklists in
the note. Replace superseded run details rather than append an audit report for
every upgrade. Link existing operational docs instead of copying procedures.
Add detail only for an actual compatibility issue or a requested audit report.

Use current official release notes, Node's distribution index/release schedule,
Debian's release information, npm registry artifacts, and Heroku support docs.
Check `npm view <package>@<selected-version> engines` and intervening breaking
changes. Recheck even retained tools. `latest` tags and `npm outdated` identify
candidates, not compatibility decisions. `npm outdated` normally exits nonzero
when updates exist; capture audit results independently rather than chaining
the two with `&&`.

Use the newest compatible stable Debian Node variant, not a rolling `latest`
image tag. Pin `node:<exact-patch>-<stable-codename>@sha256:<index-digest>`.
If the chosen Node line has no supported latest-stable Debian variant, report
the conflict and resolve it within authorized runtime scope. Do not silently
use an older Debian release or alter Python to make the images match.

## Handle breaking changes

Review upstream release notes and migration guides between installed and target
versions for changed direct dependencies and relevant transitives, including
minor/patch releases. Map removed APIs, changed defaults/configuration, runtime
requirements and asset/browser behaviour changes to actual repository usage.

Implement necessary compatibility fixes within the authorized upgrade scope.
Verify affected behaviour directly. Follow the testing scope in `docs/testing.md`:
add a focused test only for a missing custom rule affected by the upgrade, not
for upstream library behavior, end-to-end workflows, generic page rendering,
or legacy removal. Keep build, watcher, and manual browser verification separate
from automated application tests. A successful install or build alone does not
establish compatibility.

Flag unresolved incompatibilities and decisions outside scope to the developer
when identified. Give the package/version transition, upstream evidence,
affected code or workflow, impact and recommended options. Pause only work that
depends on that decision; continue independent work. Do not silently bypass
checks or force unsupported versions. Summarize resolved fixes, intentional
behaviour changes and remaining risks in the handoff and short maintenance note.

## Resolve and align

Use the selected Node/npm for resolution. Update manifest ranges to the recorded
targets, then run `npm install` to generate the lockfile. Retain the project's
exact Biome pin and intended compatibility ranges unless deliberately changing
that policy. For a full frontend refresh, use `npm update` to refresh compatible
transitives as needed; keep a targeted request targeted. Inspect all additions,
removals, versions, integrity hashes, sources, engine changes, and optional native
platform variants before accepting the graph.

Check native Sharp/libvips, esbuild, and Sass watcher binaries on the actual
local and Docker platforms. Do not drop optional dependencies or suppress
engines to make an install pass. Review install-script notices for the selected
npm; do not add blanket approvals. Diagnose audit findings through their actual
dependency paths; avoid `npm audit fix --force` or overrides as an automatic fix.
Record unresolved findings and their relevance rather than claim every audit
warning is exploitable in this build pipeline.

Align every applicable row in the companion checklist. Keep `.nvmrc`, exact
Node/npm engines, Docker, CI, and Heroku runtime selection consistent. If using
a non-bundled npm, explicitly install that version in Docker too. Keep Biome's
package, hook revision/additional dependency, and configuration compatible;
use its migration command when required. Do not add an unused browser-sync
dependency just because the legacy `scripts/server.js` mentions it.

Once the lock is accepted, routine installs, Make targets, CI, and Docker use
`npm ci`. Verification must not resolve a new graph. Compare manifest/lock hashes
before and after verification, including when the baseline already has local
changes; a plain diff against HEAD is insufficient in a dirty worktree.

## Verify and hand off

Follow the [project checks](references/companion-files.md#verification) in order:
finish builds and container recreation before testing their results. Verify
production assets and real watcher content edits, then the development and
production-mode Docker workflows. Stop temporary watchers, restore only your
temporary source edits, and rebuild production assets before handoff.

Keep existing databases and media. Do not use `make clean`, destroy volumes, or
pull production data for fixtures. The shared Dockerfile still builds the
existing Python stage; leave it unchanged and record unrelated failures rather
than silently expanding the Node upgrade. Ordinary Node upgrades require no
database migrations of their own; inspect any backend migration plan before
using `make prod-run` on data with pending migrations and follow the documented
backup/rehearsal workflow if needed.

Keep detailed actual commands/results, baseline versus new warnings, native/image
checks, browser coverage and gaps, remote checks not run, companion dispositions,
and the final lock hash in scratch. Summarize consequential results and limits
in the maintenance note; distinguish historical checks from newly executed ones.
Capture a final inventory and compare by package path,
including optional platform variants and source fingerprints. Update
`CHANGELOG.md` under `Unreleased` and present the diff for review. Rebuild assets
and images for rollback using the previous manifest/lock/runtime pins together;
do not imply a Node rollback requires a database restore. Respect a request to
keep the work local and leave creating or updating this skill separate from
running a new upgrade.
