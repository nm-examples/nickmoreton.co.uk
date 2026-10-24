# Node frontend maintenance

## Supported versions

Use Node **24.22.0 LTS** with its bundled **npm 11.19.1** and keep Biome pinned
exactly to **2.5.15**. Node 24 remains the supported LTS line; review the
[Node release schedule](https://github.com/nodejs/Release/blob/main/schedule.json)
before changing it.

Exact package versions and image digests live in [`package.json`](../package.json),
[`package-lock.json`](../package-lock.json), [`.nvmrc`](../.nvmrc) and the Node stage
of [`docker/Dockerfile`](../docker/Dockerfile). The image uses Debian 13 Trixie,
pinned by patch tag and multi-platform digest. Keep local setup, CI, Docker and
Heroku runtime selections aligned, and match Biome's package and hook versions.

Select the project runtime with `nvm use`, then use `npm ci` for routine installs.
Regenerate the lockfile only for deliberate dependency updates. Keep detailed
inventories and logs in ignored scratch files; Git preserves earlier records.

## Upgrade workflow

For Node, npm, frontend dependency, or Biome upgrades, use the repository's
[Node upgrade skill](../.agents/skills/upgrade-node-frontend/SKILL.md) to record
version selections, align runtime/npm/Biome pins, and verify builds, watchers,
and Docker. Keep Python image changes in the separate Python upgrade phase.

Check the latest Debian stable release and use its supported Node image variant.
Pin the exact Node patch tag, Debian codename, and verified multi-platform index
digest; verify native dependencies and local Docker workflows. Match Biome's
package pin to both the pre-commit hook revision and its additional dependency.

## Verified on 20 October 2026

- Node/npm and all six direct packages were already current; no dependency
  changes were needed. Newer transitive majors fall outside their parent
  packages' supported ranges.
- Clean `npm ci`, `npm ls --depth=0`, `npm run biome:check` and `npm run build`
  passed on macOS arm64. Biome checked nine configured files.
- `npm audit` reported zero vulnerabilities; direct `npm outdated` was empty.
- Manifest, lockfile and frontend source fingerprints remained unchanged.
- The pinned Node image digest was rechecked, including Linux amd64/arm64
  availability. Docker watcher/browser checks were not repeated in this review;
  hosted CI and Heroku builds were not run.

npm reports install-script notices for esbuild and Parcel watcher; no blanket
approvals were added. The production build completed without Sass deprecations.

## Deployment and rollback

After an upgrade, rebuild frontend/app images and collect matching hashed static
assets. Use `make build` and `make up` for development, or `make prod-run` for
production-mode verification.
Node-only changes require no database migration, reindex or database restore;
[backend upgrade requirements](python-upgrade.md) apply separately.

For rollback, restore the earlier manifest, lockfile, runtime/image pins and any
related Biome configuration together. Select that runtime, run `npm ci` and
`npm run build`, rebuild app images and recollect static files. Preserve existing
database and media volumes.
