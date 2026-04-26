# Nick Moreton's Wagtail-Powered Website

[![Wagtail](https://img.shields.io/badge/wagtail-7.3.1-olive.svg)](https://wagtail.org/)
[![Django](https://img.shields.io/badge/django-6.0.4-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

Source code for [www.nickmoreton.co.uk](https://www.nickmoreton.co.uk), a Django and Wagtail site with custom content models, a small frontend build pipeline, and Docker-based local development.

## Project Map

- `webapp/home/`, `webapp/pages/`, `webapp/core/`, and `webapp/search/` contain the Wagtail apps.
- `webapp/settings/` contains shared, development, and production settings.
- `webapp/templates/` and app-level `templates/` directories contain Django templates.
- `webapp/static_src/` contains Sass, JavaScript, and source images.
- `webapp/static_compiled/` contains generated frontend assets served by Django.
- `docker/`, `docker-compose.yaml`, and `Makefile` contain local development support.
- `docs/` contains deployment, staging, data, and media workflows.

## Requirements

- Docker Compose
- Node.js and npm
- Python tooling is installed inside the app container with `uv`

Copy the example environment file before running Make targets:

```bash
cp .env.example .env
```

For basic local development, the placeholder values are enough. Heroku and S3 values are only needed for data and media sync; see [Data and media](./docs/data-and-media.md).

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

In another terminal, watch frontend assets:

```bash
npm start
```

Django Browser Reload is enabled, so browser pages reload when watched frontend files are rebuilt.

## Common Commands

| Command | Purpose |
| --- | --- |
| `make quickstart` | First local boot: frontend build, Docker build/start, migrations, static files, superuser prompt. |
| `make build` | Build Docker images. |
| `make up` | Start Postgres and the app container. |
| `make run` | Run Django at `http://localhost:8000`. |
| `make migrate` | Run Django migrations inside the app container. |
| `make test` | Run the Django test suite inside the app container. |
| `npm run build` | Build Sass, JavaScript, and images once. |
| `npm start` | Watch frontend assets during development. |

## Focused Docs

- [Data and media](./docs/data-and-media.md): Heroku/S3 sync, local database dumps, media copy helpers, and cleanup notes.
- [Local Dokku](./docs/local.dokku.md): production-like local staging with OrbStack and Dokku.
- [Production Dokku](./docs/linode.dokku.md): production or staging deployment on Linode/Akamai Cloud.
