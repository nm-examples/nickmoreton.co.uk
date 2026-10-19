# Node frontend upgrade record

## 2026-10-18 selection

Selection timestamp: `2026-10-18T21:06:53+00:00`.

Branch: `node-frontend-upgrade`, based on `50c616fd149f507c3cccd1aa114212ac8f614075` (`wt74-upgrade-integration`). Starting worktree clean; no existing edits. Development Compose stack had app, Postgres, Adminer and Mailhog running; production-mode stack was stopped.

Baseline lock SHA-256: `29710b70368f457d37ca80cc24b226bb7870e88b16633247be6ed958dd28db08` (lock format 3). Baseline inventory and logs saved outside checkout at `/tmp/nickmoreton-node-upgrade/`.

Registry: `https://registry.npmjs.org/`. Stable releases only; no prereleases or exceptions. Timestamp records selection, **not** an npm resolver cutoff; no cutoff applied. No overrides, legacy-peer-deps, omitted optional packages, or special resolver flags intended.

### Runtime and image

Select **Node 24.22.0**, Active LTS Krypton on selection date (maintenance scheduled 2026-10-20, EOL 2028-04-30), and its bundled **npm 11.19.1**. Node 26 is still Current until 2026-10-28, so retain supported LTS. Host initially used Node 22.22.2/npm 10.9.7; explicitly selected installed Node 24.22.0 through nvm without changing default aliases before baseline checks. Previous `.nvmrc` was floating `24`, Docker was `node:24-bookworm`, and engines were absent.

Evidence: [Node distribution index](https://nodejs.org/dist/index.json), [release schedule](https://github.com/nodejs/Release/blob/main/schedule.json), [release policy](https://nodejs.org/en/about/previous-releases), [Heroku Node support](https://devcenter.heroku.com/articles/nodejs-support). Exact engines select Node/npm for the existing Node-before-Python Heroku buildpacks; remote build remains to be tested.

Latest Debian stable is **13.7, trixie**, per [Debian releases](https://www.debian.org/releases/). Select official supported `node:24.22.0-trixie@sha256:ff054b356ab93ed540518ca23cfcd9840e5256dd04db5a8d8afc43f4ecc7c9f8`. `docker buildx imagetools inspect` verified OCI multi-platform index with `linux/amd64` and `linux/arm64/v8` (also ppc64le); manifest availability is distinct from execution coverage. Python stage/image, uv, service images and Python dependencies remain outside scope.

### Direct package decisions

Exact selected registry artifacts and `npm view <package>@<version> engines` checked before resolving. Caret compatibility ranges retained except deliberately advance concurrently to 10.x and Sharp to 0.35.x; Biome remains exact.

| Package | Previous exact | Selected exact | Manifest range | Node engine | Compatibility evidence and reason |
| --- | --- | --- | --- | --- | --- |
| `@biomejs/biome` | 2.4.13 | 2.5.15 | `2.5.15` | `>=14.21.3` | [Upstream](https://github.com/biomejs/biome/blob/main/packages/@biomejs/biome/CHANGELOG.md). Retain exact pin; migrate/check configuration with 2.5. |
| `@picocss/pico` | 2.1.1 | 2.1.1 | `^2.1.1` | `not declared` | [Upstream](https://github.com/picocss/pico/releases/tag/v2.1.1). Retain latest stable; current Sass imports remain available. |
| `concurrently` | 9.2.1 | 10.0.6 | `^10.0.6` | `>=22` | [Upstream](https://github.com/open-cli-tools/concurrently/releases/tag/v10.0.0). CLI-only usage; Node >=22 satisfied; removed API options and ESM change do not affect scripts. |
| `esbuild` | 0.28.0 | 0.28.2 | `^0.28.2` | `>=18` | [Upstream](https://github.com/evanw/esbuild/blob/main/CHANGELOG.md). Retain 0.28 compatibility line; bundling/minify/watch CLI supported. |
| `highlight.js` | 11.11.1 | 11.12.0 | `^11.12.0` | `>=12.0.0` | [Upstream](https://github.com/highlightjs/highlight.js/blob/main/CHANGES.md). Retain v11 core and explicit language imports; includes grammar fixes. |
| `sass` | 1.99.0 | 1.105.2 | `^1.105.2` | `>=20.19.0` | [Upstream](https://github.com/sass/dart-sass/blob/main/CHANGELOG.md). Retain 1.x CLI; reviewed 1.100–1.105 color/importer/watch fixes; no Sass module migration. |
| `sharp` | 0.34.5 | 0.35.5 | `^0.35.5` | `>=20.9.0` | [Upstream](https://github.com/lovell/sharp/releases/tag/v0.35.0). New 0.35 line updates native libraries; verify existing resize/png/webp API and decoded images. |

### Baseline verification

`nvm use 24.22.0`; `npm ci`; `npm ls --depth=0`; `npm run biome:check` (7 files); `npm run build` all passed on macOS arm64. Baseline Sass warnings: import, if-function, global-builtin and color-functions deprecations, with six repeated warnings omitted. Baseline native Sharp 0.34.5/libvips 8.17.3 loaded and generated icons/raster images; decoded pixel fingerprints saved.

`npm audit --json`: 6 affected packages (1 low, 3 high, 2 critical): esbuild Windows dev-server advisory; concurrently → shell-quote command quoting/parse advisories; Sass → immutable and source-map-js DoS advisories; Sharp bundled libvips/libheif/librsvg advisories. These are build dependencies, with differing exposure (this project does not run esbuild dev server or process user shell commands). Refresh direct/transitive packages then audit again; no forced audit fix or overrides. `npm outdated --json` captured separately. npm warned that watcher/esbuild/Sharp install scripts are not covered by allowScripts; no blanket approval added.

### Verification and companion dispositions

| Companion file(s) | Disposition |
| --- | --- |
| `package.json`, `package-lock.json` | Updated all seven direct decisions, exact Node/npm engines and compatible transitives; v3 lock retained. Fixed clean path and sequenced cleanup before watch builders with sibling failure shutdown. Existing `build` script remains Heroku’s default build lifecycle entry. |
| `.npmrc` | Not present; inspected only relevant effective non-secret options: legacy-peer-deps=false, install-links=false, omit empty, ignore-scripts=false, engine-strict=false. No flags required to reproduce the lock. |
| `.nvmrc`, `docker/Dockerfile` | Exact Node patch and verified trixie index digest aligned. Docker uses bundled npm and `npm ci`; Python stage byte-for-byte unchanged. |
| `.github/workflows/test.yml` | Added dedicated frontend job using `.nvmrc`, exact bundled npm assertion, `npm ci`, Biome, production build and manifest/lock diff check. Existing Python job uses the same `.nvmrc`; left its steps unchanged. |
| `.pre-commit-config.yaml`, `biome.json` | Hook tag `v2.5.15` verified upstream (`d1d67cb1a73ea0917eb553c4f025e212c8cd0465`), additional dependency matches exact package. `npx biome migrate --write` changed `rules.recommended` to `rules.preset`; file coverage remains seven JSON/JS files, not Sass/templates/Python. Python hooks unchanged. |
| `Makefile` | frontend, frontend-check and start use `npm ci`; Docker and data targets unchanged. Destructive clean target not used. |
| `app.json` | Checked unchanged: Node-before-Python buildpacks; Node/npm engines now select versions. No remote deployment performed. |
| `README.md`, `AGENTS.md` | Both updated with selected Node/npm versions, nvm setup, locked installs and record link. AGENTS also records exact Biome alignment and frontend verification commands; runtime and Debian policy satisfied. |
| `CHANGELOG.md`, `docs/node-upgrade.md` | Updated Unreleased; this dated record contains choices, graph changes, commands/results and rollback. |
| `scripts/images.js`, frontend JS and Sass | Checked unchanged via before/after source fingerprints. Sharp resize/PNG/WebP and favicon copy work; Highlight.js core/language imports work. Existing Sass deprecations retained. Sharp 0.35 removed deprecated APIs are not used; AVIF/channel-limit changes do not affect the source SVG/JPEG. |
| Templates, compiled assets | References match generated CSS/JS and SVG/PNG icons; outputs remain ignored. Clean watcher start removed pre-existing stale compiled images; source pipeline produces only the current source JPEG and three favicons. |
| `scripts/server.js` | Checked unchanged: legacy unused browser-sync helper; no dependency added. |
| Compose files, production/data docs | Checked unchanged: shared Dockerfile, mounts, nginx URLs and data preservation still apply. No Postgres/nginx/Python image changes or data sync. |

### Upgraded verification

Commands below ran with Node 24.22.0/npm 11.19.1 where Node was involved. Scratch logs and harnesses are outside the checkout in `/tmp/nickmoreton-node-upgrade/`.

| Check | Actual result |
| --- | --- |
| `npm install`, then `npm update` | Resolved the recorded direct versions and refreshed compatible transitives. Initial install retained two high transitives; update removed those findings. No forced fixes or overrides. |
| `npm ci`, `npm ls --depth=0` | Clean locked install passed, seven expected direct versions installed. No engine suppression or omitted optional dependencies. |
| `npm audit --json`, `npm outdated --json` | Audit: zero vulnerabilities across all dependency types. Outdated: empty. Captured separately despite their nonzero status behavior. |
| `npx biome migrate --write`, `npm run biome:check` | Migration succeeded, seven covered files passed lint/format. |
| `docker compose exec -T app pre-commit run biome-ci --all-files` | New hook environment initialized and Biome hook passed. Python hooks were not run for this Node-only change. |
| `npm run build` | Production CSS/JS and maps generated, image task successful. Finished with a fresh production build after watcher restoration. |
| Real `npm start` edits on macOS arm64 | Stale-marker cleanup precedes all builders; CSS/JS/icons recreated. Added CSS rule and JavaScript console statement both appeared in output; restored source bytes removed both markers. Temporary watcher process group stopped. |
| Native Sharp on macOS arm64 | Sharp 0.35.5/libvips 8.18.7 loads. Generated PNGs 32×32/180×180, source SVG copied byte-for-byte, source JPEG output remains WebP bytes under `.jpg`, 1620×1080. Generated icons and raster decoded pixels equal baseline. |
| `docker build --target frontend -t nickmoreton-node-frontend-review -f docker/Dockerfile .` | Passed on Linux arm64; running image confirms Debian 13.7 trixie, Node 24.22.0/npm 11.19.1 and Sharp 0.35.5/libvips 8.18.7. esbuild and Sass native components run during build. |
| Real watcher edits in Linux arm64 frontend image | Same cleanup, initial outputs, changed Sass/JS content and restoration checks passed. Initial scratch harness lacked its log directory inside container; created scratch directory and reran successfully. |
| `docker build --platform linux/amd64 --target frontend -t nickmoreton-node-frontend-review-amd64 -f docker/Dockerfile .` | Passed under local amd64 emulation; Node/npm pins and Sharp 0.35.5/libvips 8.18.7 verified, raster decodes as 1620×1080 WebP. |
| Real watcher edits in Linux amd64 frontend image | Same cleanup, real Sass/JS edits and restoration passed under emulation; temporary watcher stopped. |
| `make build`, then `make up` | Both completed in order; development app recreated from new image while database/media retained. |
| Recreated development app: `python manage.py check`, `migrate --plan`, `test --noinput` | Configuration clean, no pending migrations, all ten PostgreSQL regression tests passed. No Node migration needed. |
| Production migration preflight | `docker compose -f docker-compose.production.yaml run --rm prod-app python manage.py migrate --plan`: no pending operations in existing isolated database. No migration rehearsal needed for this Node-only change. |
| `make prod-run` | Build, migrations (none pending), collectstatic and recreated Gunicorn/nginx all passed. Running app reports `DEBUG=False`; configuration check clean. |
| nginx static/media requests | curl with normal certificate validation returned 200 for HTTPS home/search/admin login, hashed CSS/JS/SVG/PNG/touch icon; localhost HTTP fallback home passed. Existing local rendition copied temporarily to isolated production media, fetched byte-for-byte through nginx, then removed. |
| Browser | In-app browser rendered development home and existing article correctly; observed YAML highlighting (seven token spans), final animated tagline and “Copied!” feedback. Production homepage rendered over trusted HTTPS. |
| Manifest/lock consistency | SHA-256 snapshot before verification matched after installs/builds/watchers. Before/after inventory confirms frontend source fingerprints unchanged. Final diff whitespace check passed. |

Warnings and limits: Sass emits the same import, if-function (Pico modal), global-builtin and color-functions warnings as baseline, with six repeated warnings omitted. npm still warns about allowScripts coverage for esbuild and Parcel watcher; no blanket script approvals added; their prebuilt native components and watcher execution pass. Initial Python urllib HTTPS probe used a CA store that did not trust OrbStack; system curl and browser HTTPS passed without disabling certificate verification. Production database has only initial Root/Home pages, so content/highlighting/copy checks used existing development data. Current template comments out `.menu-switch`; mobile toggle is not an active feature. Browser viewport coverage was desktop only; no device/browser matrix or remote CI/Heroku run.

Sharp’s upstream optional Windows ia32 package is restricted to Node 20 (`^20.9.0`), deprecated by Sharp 0.35. This is the only engine exception in the full lock and is skipped on the tested macOS/Linux architectures. All non-optional and tested-platform package engines accept Node 24.22.0. Do not drop that optional artifact to hide its upstream platform constraint. Parcel watcher 2.6 no longer lists win32-ia32; Linux/macOS variants are retained.

### Complete package graph review

Lock package-path count: 115 → 111, comprising three additions, seven removals, 97 version updates and four same-version license metadata updates. The root lock entry additionally reflects manifest ranges/engines. Every remaining package source is the public npm registry with SHA-512 integrity. Changed source/integrity fingerprints correspond to versioned artifacts; no same-version source/integrity changes. Reviewed changed engines, dependencies, libc/OS/CPU constraints and install scripts: Sharp removes its install script, esbuild and Parcel retain theirs; native optional packages remain represented for macOS and Linux (glibc/musl), as well as upstream additional targets. No local/Git sources or unexpected prereleases.

Every changed package path is listed below; `—` indicates an addition/removal. Metadata lists changed lock entry fields, including fields other than versions.

| Package path | Before | After | Changed fields |
| --- | --- | --- | --- |

| `node_modules/@biomejs/biome` | 2.4.13 | 2.5.15 | integrity, optionalDependencies, resolved, version |
| `node_modules/@biomejs/cli-darwin-arm64` | 2.4.13 | 2.5.15 | integrity, resolved, version |
| `node_modules/@biomejs/cli-darwin-x64` | 2.4.13 | 2.5.15 | integrity, resolved, version |
| `node_modules/@biomejs/cli-linux-arm64` | 2.4.13 | 2.5.15 | integrity, libc, resolved, version |
| `node_modules/@biomejs/cli-linux-arm64-musl` | 2.4.13 | 2.5.15 | integrity, libc, resolved, version |
| `node_modules/@biomejs/cli-linux-x64` | 2.4.13 | 2.5.15 | integrity, libc, resolved, version |
| `node_modules/@biomejs/cli-linux-x64-musl` | 2.4.13 | 2.5.15 | integrity, libc, resolved, version |
| `node_modules/@biomejs/cli-win32-arm64` | 2.4.13 | 2.5.15 | integrity, resolved, version |
| `node_modules/@biomejs/cli-win32-x64` | 2.4.13 | 2.5.15 | integrity, resolved, version |
| `node_modules/@emnapi/runtime` | 1.10.0 | 1.11.3 | integrity, resolved, version |
| `node_modules/@esbuild/aix-ppc64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/android-arm` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/android-arm64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/android-x64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/darwin-arm64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/darwin-x64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/freebsd-arm64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/freebsd-x64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/linux-arm` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/linux-arm64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/linux-ia32` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/linux-loong64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/linux-mips64el` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/linux-ppc64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/linux-riscv64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/linux-s390x` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/linux-x64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/netbsd-arm64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/netbsd-x64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/openbsd-arm64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/openbsd-x64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/openharmony-arm64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/sunos-x64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/win32-arm64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/win32-ia32` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@esbuild/win32-x64` | 0.28.0 | 0.28.2 | integrity, resolved, version |
| `node_modules/@img/sharp-darwin-arm64` | 0.34.5 | 0.35.5 | engines, integrity, optionalDependencies, resolved, version |
| `node_modules/@img/sharp-darwin-x64` | 0.34.5 | 0.35.5 | engines, integrity, optionalDependencies, resolved, version |
| `node_modules/@img/sharp-freebsd-wasm32` | — | 0.35.5 | dependencies, dev, engines, funding, integrity, license, optional, os, resolved, version |
| `node_modules/@img/sharp-libvips-darwin-arm64` | 1.2.4 | 1.3.4 | integrity, resolved, version |
| `node_modules/@img/sharp-libvips-darwin-x64` | 1.2.4 | 1.3.4 | integrity, resolved, version |
| `node_modules/@img/sharp-libvips-linux-arm` | 1.2.4 | 1.3.4 | integrity, libc, resolved, version |
| `node_modules/@img/sharp-libvips-linux-arm64` | 1.2.4 | 1.3.4 | integrity, libc, resolved, version |
| `node_modules/@img/sharp-libvips-linux-ppc64` | 1.2.4 | 1.3.4 | integrity, libc, resolved, version |
| `node_modules/@img/sharp-libvips-linux-riscv64` | 1.2.4 | 1.3.4 | integrity, libc, resolved, version |
| `node_modules/@img/sharp-libvips-linux-s390x` | 1.2.4 | 1.3.4 | integrity, libc, resolved, version |
| `node_modules/@img/sharp-libvips-linux-x64` | 1.2.4 | 1.3.4 | integrity, libc, resolved, version |
| `node_modules/@img/sharp-libvips-linuxmusl-arm64` | 1.2.4 | 1.3.4 | integrity, libc, resolved, version |
| `node_modules/@img/sharp-libvips-linuxmusl-x64` | 1.2.4 | 1.3.4 | integrity, libc, resolved, version |
| `node_modules/@img/sharp-linux-arm` | 0.34.5 | 0.35.5 | engines, integrity, libc, optionalDependencies, resolved, version |
| `node_modules/@img/sharp-linux-arm64` | 0.34.5 | 0.35.5 | engines, integrity, libc, optionalDependencies, resolved, version |
| `node_modules/@img/sharp-linux-ppc64` | 0.34.5 | 0.35.5 | engines, integrity, libc, optionalDependencies, resolved, version |
| `node_modules/@img/sharp-linux-riscv64` | 0.34.5 | 0.35.5 | engines, integrity, libc, optionalDependencies, resolved, version |
| `node_modules/@img/sharp-linux-s390x` | 0.34.5 | 0.35.5 | engines, integrity, libc, optionalDependencies, resolved, version |
| `node_modules/@img/sharp-linux-x64` | 0.34.5 | 0.35.5 | engines, integrity, libc, optionalDependencies, resolved, version |
| `node_modules/@img/sharp-linuxmusl-arm64` | 0.34.5 | 0.35.5 | engines, integrity, libc, optionalDependencies, resolved, version |
| `node_modules/@img/sharp-linuxmusl-x64` | 0.34.5 | 0.35.5 | engines, integrity, libc, optionalDependencies, resolved, version |
| `node_modules/@img/sharp-wasm32` | 0.34.5 | 0.35.5 | cpu, dependencies, engines, integrity, resolved, version |
| `node_modules/@img/sharp-webcontainers-wasm32` | — | 0.35.5 | cpu, dependencies, dev, engines, funding, integrity, license, optional, resolved, version |
| `node_modules/@img/sharp-win32-arm64` | 0.34.5 | 0.35.5 | engines, integrity, resolved, version |
| `node_modules/@img/sharp-win32-ia32` | 0.34.5 | 0.35.5 | engines, integrity, resolved, version |
| `node_modules/@img/sharp-win32-x64` | 0.34.5 | 0.35.5 | engines, integrity, resolved, version |
| `node_modules/@parcel/watcher` | 2.5.6 | 2.6.0 | dependencies, integrity, optionalDependencies, resolved, version |
| `node_modules/@parcel/watcher-android-arm64` | 2.5.6 | 2.6.0 | integrity, resolved, version |
| `node_modules/@parcel/watcher-darwin-arm64` | 2.5.6 | 2.6.0 | integrity, resolved, version |
| `node_modules/@parcel/watcher-darwin-x64` | 2.5.6 | 2.6.0 | integrity, resolved, version |
| `node_modules/@parcel/watcher-freebsd-x64` | 2.5.6 | 2.6.0 | integrity, resolved, version |
| `node_modules/@parcel/watcher-linux-arm-glibc` | 2.5.6 | 2.6.0 | integrity, libc, resolved, version |
| `node_modules/@parcel/watcher-linux-arm-musl` | 2.5.6 | 2.6.0 | integrity, libc, resolved, version |
| `node_modules/@parcel/watcher-linux-arm64-glibc` | 2.5.6 | 2.6.0 | integrity, libc, resolved, version |
| `node_modules/@parcel/watcher-linux-arm64-musl` | 2.5.6 | 2.6.0 | integrity, libc, resolved, version |
| `node_modules/@parcel/watcher-linux-x64-glibc` | 2.5.6 | 2.6.0 | integrity, libc, resolved, version |
| `node_modules/@parcel/watcher-linux-x64-musl` | 2.5.6 | 2.6.0 | integrity, libc, resolved, version |
| `node_modules/@parcel/watcher-win32-arm64` | 2.5.6 | 2.6.0 | integrity, resolved, version |
| `node_modules/@parcel/watcher-win32-ia32` | 2.5.6 | — | cpu, dev, engines, funding, integrity, license, optional, os, resolved, version |
| `node_modules/@parcel/watcher-win32-x64` | 2.5.6 | 2.6.0 | integrity, resolved, version |
| `node_modules/ansi-regex` | 5.0.1 | 6.4.0 | engines, funding, integrity, license, resolved, version |
| `node_modules/ansi-styles` | 4.3.0 | 6.2.3 | dependencies, engines, integrity, license, resolved, version |
| `node_modules/chalk` | 4.1.2 | 5.6.2 | dependencies, engines, integrity, license, resolved, version |
| `node_modules/chokidar` | 4.0.3 | 5.0.0 | dependencies, engines, integrity, resolved, version |
| `node_modules/cliui` | 8.0.1 | 9.0.1 | dependencies, engines, integrity, license, resolved, version |
| `node_modules/color-convert` | 2.0.1 | — | dependencies, dev, engines, integrity, resolved, version |
| `node_modules/color-name` | 1.1.4 | — | dev, integrity, resolved, version |
| `node_modules/concurrently` | 9.2.1 | 10.0.6 | bin, dependencies, engines, integrity, resolved, version |
| `node_modules/concurrently/node_modules/supports-color` | 8.1.1 | — | dependencies, dev, engines, funding, integrity, resolved, version |
| `node_modules/emoji-regex` | 8.0.0 | 10.6.0 | integrity, license, resolved, version |
| `node_modules/esbuild` | 0.28.0 | 0.28.2 | integrity, optionalDependencies, resolved, version |
| `node_modules/escalade` | 3.2.0 | 3.2.0 | license |
| `node_modules/get-caller-file` | 2.0.5 | 2.0.5 | license |
| `node_modules/get-east-asian-width` | — | 1.7.0 | dev, engines, funding, integrity, license, resolved, version |
| `node_modules/has-flag` | 4.0.0 | — | dev, engines, integrity, resolved, version |
| `node_modules/highlight.js` | 11.11.1 | 11.12.0 | integrity, resolved, version |
| `node_modules/immutable` | 5.1.5 | 5.1.9 | integrity, resolved, version |
| `node_modules/is-fullwidth-code-point` | 3.0.0 | — | dev, engines, integrity, resolved, version |
| `node_modules/picomatch` | 4.0.4 | 4.0.7 | integrity, resolved, version |
| `node_modules/readdirp` | 4.1.2 | 5.1.1 | engines, integrity, resolved, version |
| `node_modules/require-directory` | 2.1.1 | — | dev, engines, integrity, resolved, version |
| `node_modules/sass` | 1.99.0 | 1.105.2 | dependencies, engines, integrity, resolved, version |
| `node_modules/semver` | 7.7.4 | 7.8.5 | integrity, resolved, version |
| `node_modules/sharp` | 0.34.5 | 0.35.5 | dependencies, engines, hasInstallScript, integrity, optionalDependencies, peerDependenciesMeta, resolved, version |
| `node_modules/shell-quote` | 1.8.3 | 1.12.0 | integrity, resolved, version |
| `node_modules/source-map-js` | 1.2.1 | 1.2.2 | integrity, license, resolved, version |
| `node_modules/string-width` | 4.2.3 | 7.2.0 | dependencies, engines, funding, integrity, license, resolved, version |
| `node_modules/strip-ansi` | 6.0.1 | 7.2.0 | dependencies, engines, funding, integrity, license, resolved, version |
| `node_modules/supports-color` | 7.2.0 | 10.2.2 | dependencies, engines, funding, integrity, license, resolved, version |
| `node_modules/tree-kill` | 1.2.2 | 1.2.2 | license |
| `node_modules/tslib` | 2.7.0 | 2.8.1 | integrity, license, resolved, version |
| `node_modules/wrap-ansi` | 7.0.0 | 9.0.2 | dependencies, engines, integrity, license, resolved, version |
| `node_modules/y18n` | 5.0.8 | 5.0.8 | license |
| `node_modules/yargs` | 17.7.2 | 18.0.0 | dependencies, engines, integrity, license, resolved, version |
| `node_modules/yargs-parser` | 21.1.1 | 22.0.0 | engines, integrity, license, resolved, version |

### Lock acceptance and operational handoff

Final accepted lock SHA-256: `09dec2dc2c2dea2fd00b4cfc8450fe0e3b54ecca684af49a77bb30e473411ea9`. Manifest/lock verification did not resolve a new graph. The lock and image digest do not freeze apt repositories, future registry metadata or later deliberate resolutions.

For deployment, use the accepted manifest/lock and Node/npm pins together; rebuild frontend/app images and collect hashed static assets. No frontend-specific environment variables, database migrations or reindexing required. Existing backend deployment requirements remain documented separately in `docs/python-upgrade.md`.

For rollback, restore this change’s manifest, lock, `.nvmrc`, Node Docker stage, Biome hook/config, Make/CI companion changes together from base `50c616fd149f507c3cccd1aa114212ac8f614075`. Select the previous Node 24 runtime with nvm, run `npm ci` and `npm run build`, rebuild development/production images and recollect static assets. The previous Docker Node tag was floating; use a known cached/deployed image digest when an exact previous runtime is required. No database restore is implied by a Node rollback. Keep existing data/media volumes.

Temporary frontend watchers and development server stopped after verification; development containers remain up, and production mode is running at `https://prod-nginx.nickmoreton-production.orb.local` for review. Existing data and media preserved.

Developer reviewed the changes and approved the commit on 2026-10-18. Remote push/PR/deployment require the developer’s instruction under `AGENTS.md`.
