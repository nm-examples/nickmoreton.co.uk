# Repository Guidelines

## Project Structure & Module Organization
The Django/Wagtail project lives under `webapp/`. Core settings are in `webapp/settings/`, reusable app code is split across `webapp/home/`, `webapp/pages/`, `webapp/core/`, and `webapp/search/`, and templates live alongside each app plus `webapp/templates/` for shared pages. Frontend source files are in `webapp/static_src/` with compiled output written to `webapp/static_compiled/`. Container and deployment support lives in `docker/`, `docker-compose.yaml`, and `docs/`.

## Build, Test, and Development Commands
Use the root `README.md` for the standard local setup flow. Day-to-day commands:

- `make build` builds the Docker images.
- `make up` starts Postgres and the app container.
- `make run` runs Django on `http://localhost:8000`.
- `npm run build` compiles Sass, JavaScript, and images once.
- `npm start` watches frontend assets during development.
- `make test` runs the Django test suite inside the app container.

Copy `.env.example` to `.env` before starting work.

Use Node.js `24.22.0` LTS and its bundled npm `11.19.1`. Select the project runtime with `nvm install` and `nvm use` from `.nvmrc`, then use `npm ci` for routine installs. Regenerate `package-lock.json` only for deliberate dependency updates. Keep `.nvmrc`, the exact Node/npm engines in `package.json`, Docker, and CI aligned; Heroku uses the package engines. Version selections, verification, and rollback steps are recorded in `docs/node-upgrade.md`.

## Local Development & Production-Mode Checks
Use Docker Compose for normal local development: `make quickstart` for the first boot, then `make run` for Django and `npm start` for frontend asset watching during day-to-day work.

Use the production-mode Docker workflow for production-like local verification before deployment. Run `make prod-run` to start Gunicorn behind nginx with `DEBUG = False`; the OrbStack URL is `https://prod-nginx.nickmoreton-production.orb.local`. Data and media workflows are documented in `docs/data-and-media.md`; production data and media sync commands remain local-only and environment-dependent.

For Node frontend upgrades, check the latest Debian stable release and use its supported Node image variant. Pin the image with an exact Node patch tag, Debian codename, and verified multi-platform index digest, then verify native dependencies and the local Docker workflows. Keep Python image changes in the separate Python upgrade phase.

## Coding Style & Naming Conventions
Target Python `3.14`, Django `6.0`, and Wagtail `7.4` LTS. Follow PEP 8 with 4-space indentation. Keep Django modules and template directories lowercase with underscores; use `PascalCase` for model and test class names, and `snake_case` for functions and methods. Frontend entry points belong in `webapp/static_src/scripts/` and Sass partials in `webapp/static_src/styles/`. The Python toolchain includes `ruff`, `pyupgrade`, and `django-upgrade`; run them before opening a PR if you touch Python code.

Frontend JavaScript and JSON checks use Biome `2.5.15`, pinned exactly in `package.json` and matched by the pre-commit hook revision and additional dependency. Run `npm run biome:check` for its configured file coverage and `npm run build` to verify production assets.

## Testing Guidelines

For Python backend upgrades, use the repository-local skill in `.agents/skills/upgrade-wagtail-python/SKILL.md` to record exact version selections, align companion files, and verify the Docker stacks.

For Node and frontend dependency upgrades, use the repository-local skill in `.agents/skills/upgrade-node-frontend/SKILL.md` to record version selections, align npm/Biome/runtime pins, and verify builds, watchers, and Docker. Keep Python image changes in the separate Python upgrade phase.

Tests currently use Django’s built-in test runner (`python manage.py test` via `make test`). Add tests near the app they cover; the regression suite is `webapp/pages/test_upgrade.py`, but prefer names like `test_models.py` or `test_views.py` as coverage grows. Name test methods `test_<behavior>` and cover page models, template rendering, and custom template tags when you change them.

## Commit, Changelog & Pull Request Guidelines
Recent history uses short, imperative commit subjects such as `Mirror data into production-mode Docker`. Keep subjects specific and under roughly 72 characters.

Only commit changes after a developer has reviewed them and approved them for commit. Prefer separate, focused commits when the changes are better understood or reviewed independently.

When the work appears complete, ask the developer whether to push the branch, create a pull request, or both. Wait for their instruction before taking those actions, unless they have already explicitly authorized them for the current work.

Update `CHANGELOG.md` with each commit when the change is user-facing, operationally meaningful, or otherwise notable. Keep new entries under `Unreleased` until a release section is created. When preparing a PR for merging or deployment, move the PR's changelog entries from `Unreleased` into a dated release section for the deployment date.

PRs should explain the user-facing or maintenance impact, list any migrations or environment changes, link related issues, and include screenshots for template or styling updates. When pushing additional code to a branch that already has an open PR, update the PR body so it reflects the latest notable changes and matches the changelog where relevant.

Before making or committing new changes, check the current branch. Start new work on a feature branch whose name describes the work to be done; create or switch to the appropriate branch before editing, including when the current branch is for unrelated work. Do not make new changes directly on `main`. Do not prefix branch names unless the user requests a prefix.

## Configuration & Data Handling
Do not commit real secrets or production dumps. Data sync commands such as `make pull-data` and `make pull-media` depend on `.env` values and external tooling; treat them as local-only operations and clean up generated backups after use. See `docs/data-and-media.md` for the full workflow and generated files.
