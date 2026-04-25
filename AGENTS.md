# Repository Guidelines

## Project Structure & Module Organization
The Django/Wagtail project lives under `webapp/`. Core settings are in `webapp/settings/`, reusable app code is split across `webapp/home/`, `webapp/pages/`, `webapp/core/`, and `webapp/search/`, and templates live alongside each app plus `webapp/templates/` for shared pages. Frontend source files are in `webapp/static_src/` with compiled output written to `webapp/static_compiled/`. Container and deployment support lives in `docker/`, `docker-compose.yaml`, and `docs/`.

## Build, Test, and Development Commands
Use `make quickstart` for the first local boot: it installs frontend dependencies, builds assets, starts Docker services, applies migrations, collects static files, and prompts for a superuser. Day-to-day commands:

- `make build` builds the Docker images.
- `make up` starts Postgres and the app container.
- `make run` runs Django on `http://localhost:8000`.
- `npm run build` compiles Sass, JavaScript, and images once.
- `npm start` watches frontend assets during development.
- `make test` runs the Django test suite inside the app container.

Copy `.env.example` to `.env` before starting work.

## Local Development & Staging
Agents may set up the project for local development using `make quickstart` for the first boot, then `make run` for Django and `npm start` for frontend asset watching during day-to-day work. Local Dokku staging is supported by `make make-dokku` and the detailed workflow in `docs/local.dokku.md`.

Only push to the local Dokku staging instance when explicitly requested. Deploy the current branch to Dokku's `main` with `git push dokku <current-branch>:main`. Data and media helpers for local staging are available through `make export-data`, `make import-data`, and `make push-dokku-data`; production data and media sync commands remain local-only and environment-dependent.

## Coding Style & Naming Conventions
Target Python `3.13`, Django `6.0`, and Wagtail `7.3`. Follow PEP 8 with 4-space indentation. Keep Django modules and template directories lowercase with underscores; use `PascalCase` for model and test class names, and `snake_case` for functions and methods. Frontend entry points belong in `webapp/static_src/scripts/` and Sass partials in `webapp/static_src/styles/`. The Python toolchain includes `black`, `isort`, `flake8`, `pyupgrade`, and `django-upgrade`; run them before opening a PR if you touch Python code.

## Testing Guidelines
Tests currently use Django’s built-in test runner (`python manage.py test` via `make test`). Add tests near the app they cover; the current example is `webapp/pages/test.py`, but prefer names like `test_models.py` or `test_views.py` as coverage grows. Name test methods `test_<behavior>` and cover page models, template rendering, and custom template tags when you change them.

## Commit & Pull Request Guidelines
Recent history uses short, imperative commit subjects such as `Update commands and documentation for copying media files to dokku`. Keep subjects specific and under roughly 72 characters. PRs should explain the user-facing or maintenance impact, list any migrations or environment changes, link related issues, and include screenshots for template or styling updates.

Before making or committing new changes, check the current branch. If it is `main`, create or switch to a feature branch first. Use the `codex/` branch prefix unless the user requests another branch name.

## Configuration & Data Handling
Do not commit real secrets or production dumps. Data sync commands such as `make pull-data` and `make pull-media` depend on `.env` values and external tooling; treat them as local-only operations and clean up generated backups after use.
