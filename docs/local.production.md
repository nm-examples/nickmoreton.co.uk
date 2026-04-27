# Production-Mode Local Checks

This workflow runs the site locally with production settings, Gunicorn,
Postgres, and nginx. It is intended to replace the useful verification parts of
local Dokku without changing the normal development workflow.

Normal development still uses:

```bash
make up
make run
npm start
```

## Run the production-mode stack

From the project root:

```bash
make prod-run
```

This command:

- installs frontend dependencies and builds frontend assets;
- builds the production-mode app image;
- starts a separate production-mode Postgres service when needed;
- runs migrations with `webapp.settings.production`;
- runs `collectstatic --noinput`;
- starts Gunicorn behind nginx.

When using OrbStack, the site is available at
<https://prod-nginx.nickmoreton-production.orb.local> and the Wagtail admin is
available at <https://prod-nginx.nickmoreton-production.orb.local/admin>.

The stack also exposes a localhost fallback at <http://localhost:8000>.

If port `8000` is already in use, set `PROD_PORT`:

```bash
PROD_PORT=8001 make prod-run
```

The OrbStack HTTPS URL remains the same when you change `PROD_PORT`.

## Step-by-step commands

If you want to run the workflow one step at a time:

```bash
npm run build
make prod-build
make prod-migrate
make prod-collectstatic
make prod-up
```

Stop the production-mode containers with:

```bash
make prod-down
```

## Static and media files

Production mode uses `DEBUG = False`, so Django does not serve files from
`/static/` or `/media/`.

The production-mode Compose stack mounts local directories into both the app and
nginx containers:

- `static/` is populated by `make prod-collectstatic` and served by nginx at
  `/static/`.
- `media/` is served by nginx at `/media/`.

If static files return `404`, run:

```bash
npm run build
make prod-collectstatic
```

If media files return `404`, confirm the expected files exist under `media/`.

## Troubleshooting

- If `localhost:8000` is already in use, stop the normal development server or
  run the production-mode stack with `PROD_PORT=8001 make prod-run`.
- If host or CSRF checks fail, confirm `DJANGO_ALLOWED_HOSTS` and
  `DJANGO_CSRF_TRUSTED_ORIGINS` in `docker-compose.production.yaml`.
- If the app starts but pages fail before migrations run, run
  `make prod-migrate` and restart with `make prod-up`.
- If you change Python dependencies or production settings, rerun
  `make prod-build`.

## Dokku status

The Dokku workflow remains documented in `local.dokku.md` for now. Prefer this
production-mode Docker workflow for local `DEBUG = False` checks; remove Dokku
once this path has had enough real-world use.
