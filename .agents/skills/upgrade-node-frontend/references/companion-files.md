# Companion files in nickmoreton.co.uk

Read for a Node upgrade and keep per-file dispositions in ignored scratch
files. Mention only consequential exceptions in `docs/node-upgrade.md`.
Discover additional configuration with `rg --hidden`, excluding
`.git`, virtualenvs, `node_modules`, compiled/static assets, media, and backups.
Do not read `.env` or dump npm authentication settings to locate version pins.

| File | Check |
| --- | --- |
| `package.json` | Exact Node/npm engines; all direct/dev packages and intended ranges; build/watch/clean scripts; lifecycle scripts used by Heroku. Keep the existing package manager. |
| `package-lock.json` | Manifest consistency, lock format, full direct/transitive graph, integrity/source changes, engines, install scripts and optional OS/CPU/libc variants. Preserve Linux and macOS native packages. |
| Project `.npmrc`, if present | Inspect relevant non-secret resolver/install options and inherited overrides without printing auth settings. Persist flags needed to reproduce the lock with `npm ci`; do not save credentials. The inventory helper deliberately does not read npm configuration. |
| `.nvmrc` | Exact selected Node patch; actual host runtime must be selected explicitly. |
| `docker/Dockerfile` | Node stage only: latest stable Debian codename supported by Node, exact Node patch and multi-platform index digest, actual npm version, `npm ci`, source copies and production output. Leave the Python image/stage and uv unchanged. |
| `.github/workflows/test.yml`, other workflows | Frontend job selects `.nvmrc` and exact npm; locked install, Biome, production assets and dependency-file consistency check. Leave the Python job alone. |
| `.pre-commit-config.yaml` | Biome hook revision and `additional_dependencies` match the package; check upstream tag exists. Leave Python hooks unchanged. |
| `biome.json` | Configuration schema/migration and actual file coverage. The normal check does not cover every file in this repository. |
| `Makefile` | Frontend targets use `npm ci`; preserve Docker/data commands. Avoid the destructive project-wide `make clean`. |
| `app.json` | Keep Heroku Node-before-Python buildpack order and check how selected Node/npm engines and build scripts are used. A local check does not verify a remote Heroku build. |
| `README.md`, `AGENTS.md`, `docs/{node-upgrade,testing,contributing}.md` | Agent routing, runtime/install instructions, supported workflow, Node-only Debian policy, testing scope, and review rules agree with the actual setup. |
| `CHANGELOG.md`, `docs/node-upgrade.md` | Notable changes under Unreleased; short current maintenance note covering supported versions, important decisions, dated verification/limits and deployment/rollback. Git retains historical details; keep inventories and logs in scratch. |
| `scripts/images.js` | Sharp loads native library; source SVG/bitmap processing completes with errors reflected in exit status; expected dimensions/formats and favicon copying still work. |
| `webapp/static_src/scripts/` | esbuild entry point; Highlight.js core/language imports, tagline, copy button and mobile navigation behavior. |
| `webapp/static_src/styles/` | Pico/theme imports, CSS output and Sass deprecations. Compare baseline warnings; avoid masking them or adding an unrelated Sass module migration. |
| Templates, `webapp/static_compiled/` | Template asset references match generated CSS/JS/icons. Compiled assets remain generated/ignored. Inspect changed appearance when libraries or compiler output change. |
| `scripts/server.js` | Legacy browser-sync helper is not used by current npm scripts; do not treat its missing package as an upgrade blocker. Re-evaluate if the pipeline changes. |
| Compose files | Existing shared Dockerfile/build mounts, collected static files, nginx URLs and data preservation still apply. Do not upgrade service images or sync data as part of Node maintenance. |

## Selection and lock record

Save detailed evidence in ignored scratch files or outside the checkout:

- Selection timestamp, branch/base commit, dirty-worktree baseline and lock hash;
  registry identity, prerelease policy and any actual resolver constraints.
- Direct package table: package / old exact / selected exact / manifest range /
  engine requirement / reason and primary-source compatibility evidence.
- Exact Node/npm, Debian stable codename and Node index digest; supported versus
  tested architectures; every intentional retained package or deferred change.
- Complete package-path/version additions, removals and changes; inspect source,
  integrity and metadata changes even when versions stay equal.
- Companion dispositions, commands/results, warnings, final lock hash, browser
  and remote-check limits, deployment/static requirements and rollback.

Keep the maintained note roughly one page. Summarize only useful decisions,
actual verification and operational requirements. Do not copy these tables,
hashes, raw logs or the companion checklist into `docs/node-upgrade.md`.

The helper's source fingerprints avoid printing private registry locations.
Investigate changed fingerprints locally without copying credentials into notes.
Node image pinning and an accepted npm lock do not freeze apt repositories,
upstream metadata, or future dependency resolution.

## Verification

First record the actual selected runtime and baseline, then repeat relevant
checks after each upgrade stage. Save audit/outdated output even when the
commands exit nonzero; diagnose findings separately from install/build failures.

```bash
node --version
npm --version
npm ci
npm ls --depth=0
npm run biome:check
npm run build
npm audit --json
npm outdated --json
```

1. Check output CSS, JS, maps, source SVG favicon and the generated 32x32 and
   180x180 PNG icons. Check raster image dimensions and actual format with
   Sharp, checking that the output extension matches the encoded format.
   Compare changed images by decoded pixels when
   encoder bytes differ; do not require identical compression across upgrades.
2. Start `npm start` as a temporary managed process. Verify cleanup precedes
   builders, outputs are recreated, and Sass and esbuild emit changed output
   after real source-content edits. Touches or comments can leave esbuild output
   unchanged. Preserve pre-existing edits, stop only your watcher process group,
   restore your temporary edits, and finish with `npm run build`.
3. Build the frontend target with a task-specific local image tag:
   `docker build --target frontend -t <review-image> -f docker/Dockerfile .`.
   Run that image to read Node/npm versions and `/etc/os-release`; load Sharp
   and verify its image outputs there. The final Python runtime image has no
   Node executable, so it cannot report the frontend toolchain's versions.
4. Run `make build`, wait, then `make up`, wait. Check Django configuration,
   pending migrations and existing tests in the newly created app container:

   ```bash
   docker compose exec -T app python manage.py check
   docker compose exec -T app python manage.py migrate --plan
   docker compose exec -T app python manage.py test --noinput
   ```

5. If no unexpected backend migrations need rehearsal, run `make prod-run` and
   wait for completion. It builds, migrates, collects static files and starts
   Gunicorn/nginx. Verify the actual recreated app, home and available content,
   hashed CSS/JS/favicons and available image renditions through nginx at
   `https://prod-nginx.nickmoreton-production.orb.local` (fallback
   `http://localhost:8001`). Do not disable certificate verification to claim a
   passing HTTPS check; record trust/routing limits separately.
6. Inspect the rendered homepage and available article code highlighting/copy
   behavior and mobile nav in a browser, according to what this update affects.
   Record absent local content as a coverage gap; do not pull production data
   just to fill it. Keep remote CI, pre-commit and Heroku checks distinct from
   their local equivalents.
7. Compare manifest/lock hashes against the accepted pre-verification snapshot;
   capture final inventory and `git diff --check`. Leave generated assets and
   scratch reports out of commits.
