# Nick Moreton's Wagtail-Powered Website

[![Wagtail](https://img.shields.io/badge/wagtail-7.4.4-olive.svg)](https://wagtail.org/)
[![Django](https://img.shields.io/badge/django-6.0.9-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/python-3.14.8-blue.svg)](https://www.python.org/)

Source code for [www.nickmoreton.co.uk](https://www.nickmoreton.co.uk), a Django and Wagtail site with custom content models, a small frontend build pipeline, and Docker-based local development.

## Project Map

- `webapp/home/`, `webapp/pages/`, `webapp/core/`, and `webapp/search/` contain the Wagtail apps.
- `webapp/settings/` contains shared, development, and production settings.
- `webapp/templates/` and app-level `templates/` directories contain Django templates.
- `webapp/static_src/` contains Sass, JavaScript, and source images.
- `webapp/static_compiled/` contains generated frontend assets served by Django.
- `docker/`, `docker-compose.yaml`, and `Makefile` contain local development support.
- `docs/` contains deployment, production-mode local checks, data, and media workflows.
- `CHANGELOG.md` records notable unreleased and released changes.

## Requirements

- Docker Compose
- Node.js 24.22.0 LTS and its bundled npm 11.19.1 (see `.nvmrc`)
- Python 3.14 (Docker pins 3.14.8) and uv 0.13.4 are installed inside the app container
- Django 6.0 and Wagtail 7.4 LTS are the supported framework lines

Copy the example environment file before running the normal development or
Heroku-backed data/media targets:

```bash
cp .env.example .env
```

For basic local development, the placeholder values are enough. Production-mode
local checks can run without `.env`. Heroku and S3 values are only needed for
data and media sync; see [Data and media](./docs/data-and-media.md).

## First Run

Build the frontend, build and start the containers, run migrations, collect static files, and create a superuser:

```bash
make quickstart
```

Start the Django development server:

```bash
make run
```

View the site at <http://localhost:8000> and the Wagtail admin at <http://localhost:8000/admin>.

## Daily Development

Start the containers if they are not already running:

```bash
make up
```

Run Django:

```bash
make run
```

In another terminal, select the project runtime, install the accepted lockfile,
and watch frontend assets:

```bash
nvm install
nvm use
npm ci
npm start
```

Django Browser Reload is enabled, so browser pages reload when watched frontend files are rebuilt.

## Production-Mode Local Check

Use this workflow when you want to exercise the site with `DEBUG = False`,
Gunicorn, Postgres, collected static files, and nginx serving `/static/` and
`/media/`:

```bash
make prod-run
```

This can run from source without first starting the normal development stack or
pulling production data/media. It creates a blank production-mode database from
migrations unless you later mirror local data into it.

For a first production-mode boot that also prompts for a Wagtail admin user,
run:

```bash
make prod-quickstart
```

To pull Heroku data directly into production mode without setting up the normal
local development database first, run `make prod-pull-data`. To pull S3 media
directly into production mode, run `make prod-pull-media`.

View the site at
<https://prod-nginx.nickmoreton-production.orb.local> and the Wagtail admin at
<https://prod-nginx.nickmoreton-production.orb.local/admin>. Normal development
still uses `make up`, `make run`, and `npm start`.

The stack also exposes a localhost fallback at <http://localhost:8001>. If port
`8001` is already in use, set `PROD_PORT`, for example
`PROD_PORT=8002 make prod-run`; the OrbStack HTTPS URL remains the same.

For step-by-step commands and troubleshooting, see
[Production-mode local checks](./docs/local.production.md).

## Common Commands

| Command | Purpose |
| --- | --- |
| `make quickstart` | First local boot: frontend build, Docker build/start, migrations, static files, superuser prompt. |
| `make build` | Build Docker images. |
| `make up` | Start Postgres and the app container. |
| `make run` | Run Django at `http://localhost:8000`. |
| `make migrate` | Run Django migrations inside the app container. |
| `make prod-quickstart` | First production-mode boot: build/start, migrations, static files, superuser prompt. |
| `make prod-run` | Build and run production mode from source with Gunicorn behind nginx. |
| `make prod-destroy` | Stop production-mode containers and remove their Docker volumes. |
| `make test` | Run the Django test suite inside the app container. |
| `npm run build` | Build Sass, JavaScript, and images once. |
| `npm start` | Watch frontend assets during development. |

## Focused Docs

- [Redesign integration and review](./docs/redesign/integration.md): content editing, migrations, population commands, checks, and screenshots.

- [Data and media](./docs/data-and-media.md): Heroku/S3 sync, local database dumps, media copy helpers, and cleanup notes.
- [Production-mode local checks](./docs/local.production.md): run the site locally with `DEBUG = False`, Gunicorn, Postgres, and nginx.

## Python Dependency Maintenance

Docker, CI, and pre-commit use uv 0.13.4. The accepted `uv.lock` includes artifact
hashes; Docker and CI install it with `uv sync --locked` and validate it with
`uv lock --check`. The release cutoff and explicit prerelease policy in
`pyproject.toml` are part of the resolution inputs. Advance them deliberately
for a new dependency selection, using the repository's Python upgrade skill.
Heroku detects `uv.lock`; do not generate a competing `requirements.txt`.

See [the Python upgrade record](./docs/python-upgrade.md) for version selections,
verification, migration/reindex/static-file requirements, and rollback steps.

## Node Frontend Maintenance

The Node Docker build stage uses Debian 13 (Trixie), pinned to an exact Node
patch and multi-platform image digest. Local setup, CI, and Heroku select the
Node/npm versions in `.nvmrc` and `package.json`. Routine installs use `npm ci`;
only intentional dependency upgrades regenerate `package-lock.json`.

See [the Node frontend upgrade record](./docs/node-upgrade.md) for selections,
compatibility evidence, verification, and rollback.
