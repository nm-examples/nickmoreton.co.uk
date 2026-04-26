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

## Local Development & Staging
Use Docker Compose for normal local development: `make quickstart` for the first boot, then `make run` for Django and `npm start` for frontend asset watching during day-to-day work.

Use Dokku only as a local staging environment for production-like verification before deployment. Local Dokku staging is documented in `docs/local.dokku.md`.

Feature branches should target the GitHub `staging` branch for integration and local Dokku verification. Deploy `staging` to the local Dokku app with `git push dokku staging:main`; the `main` ref here is Dokku's app deployment target, not the GitHub production branch. Only push to the local Dokku staging instance when explicitly requested. Data and media workflows are documented in `docs/data-and-media.md`; production data and media sync commands remain local-only and environment-dependent.

The GitHub `main` branch is protected because pull requests merged into `main` automatically deploy to production. Never merge `staging` into `main`; production changes must go through deliberate PRs targeting `main`.

## Coding Style & Naming Conventions
Target Python `3.13`, Django `6.0`, and Wagtail `7.3`. Follow PEP 8 with 4-space indentation. Keep Django modules and template directories lowercase with underscores; use `PascalCase` for model and test class names, and `snake_case` for functions and methods. Frontend entry points belong in `webapp/static_src/scripts/` and Sass partials in `webapp/static_src/styles/`. The Python toolchain includes `ruff`, `pyupgrade`, and `django-upgrade`; run them before opening a PR if you touch Python code.

## Testing Guidelines
Tests currently use Django’s built-in test runner (`python manage.py test` via `make test`). Add tests near the app they cover; the current example is `webapp/pages/test.py`, but prefer names like `test_models.py` or `test_views.py` as coverage grows. Name test methods `test_<behavior>` and cover page models, template rendering, and custom template tags when you change them.

## Commit, Changelog & Pull Request Guidelines
Recent history uses short, imperative commit subjects such as `Update commands and documentation for copying media files to dokku`. Keep subjects specific and under roughly 72 characters.

Update `CHANGELOG.md` with each commit when the change is user-facing, operationally meaningful, or otherwise notable. Keep new entries under `Unreleased` until a release section is created.

PRs should explain the user-facing or maintenance impact, list any migrations or environment changes, link related issues, and include screenshots for template or styling updates. When pushing additional code to a branch that already has an open PR, update the PR body so it reflects the latest notable changes and matches the changelog where relevant.

Before making or committing new changes, check the current branch. If it is `main`, create or switch to a feature branch first. Use the `codex/` branch prefix unless the user requests another branch name. Open PRs for feature work against `staging` unless the user explicitly requests a production PR against protected `main`.

## Configuration & Data Handling
Do not commit real secrets or production dumps. Data sync commands such as `make pull-data` and `make pull-media` depend on `.env` values and external tooling; treat them as local-only operations and clean up generated backups after use. See `docs/data-and-media.md` for the full workflow and generated files.
