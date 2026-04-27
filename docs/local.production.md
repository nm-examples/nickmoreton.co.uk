# Production-Mode Local Checks

This workflow runs the site locally with production settings, Gunicorn,
Postgres, and nginx without changing the normal development workflow.

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

- builds the production-mode app image, including frontend assets;
- starts a separate production-mode Postgres service when needed;
- runs migrations with `webapp.settings.production`;
- runs `collectstatic --noinput`;
- starts Gunicorn behind nginx.

It does not require the normal development Docker stack, `.env`, Heroku data, or
local media. If no production-derived data has been mirrored in, migrations
create a blank Wagtail site with the default homepage.

When using OrbStack, the site is available at
<https://prod-nginx.nickmoreton-production.orb.local> and the Wagtail admin is
available at <https://prod-nginx.nickmoreton-production.orb.local/admin>.

The stack also exposes a localhost fallback at <http://localhost:8001>.

If port `8001` is already in use, set `PROD_PORT`:

```bash
PROD_PORT=8002 make prod-run
```

The OrbStack HTTPS URL remains the same when you change `PROD_PORT`.

## Step-by-step commands

If you want to run the workflow one step at a time:

```bash
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
- `prod_media/` is served by nginx at `/media/`.

Production-mode media is intentionally isolated from normal local development
media. Missing media does not block `make prod-run`. After refreshing local
media with `make pull-media`, optionally copy it into the production-mode stack
with:

```bash
make prod-push-media
```

If static files return `404`, run:

```bash
make prod-build
make prod-collectstatic
```

If media files return `404`, confirm the expected files exist under
`prod_media/`.

## Data and media refresh

Use the normal local development workflow as the source of production-derived
data and media only when you want production-like content:

```bash
make pull-data
make pull-media
```

Then mirror that local state into the production-mode Compose stack:

```bash
make prod-push-data
make prod-push-media
```

`prod-push-data` replaces only the production-mode Postgres database.
`prod-push-media` replaces only `prod_media/`. Neither command is required for
a clean production-mode boot.

If you want Heroku data in production mode without setting up the normal local
development database first, run:

```bash
make prod-pull-data
```

If you want S3 media in production mode without syncing normal local development
media first, run:

```bash
make prod-pull-media
```

## Troubleshooting

- If `localhost:8001` is already in use, stop the process using it or run the
  production-mode stack with `PROD_PORT=8002 make prod-run`.
- If host or CSRF checks fail, confirm `DJANGO_ALLOWED_HOSTS` and
  `DJANGO_CSRF_TRUSTED_ORIGINS` in `docker-compose.production.yaml`.
- If the app starts but pages fail before migrations run, run
  `make prod-migrate` and restart with `make prod-up`.
- If you change Python dependencies, frontend assets, or production settings,
  rerun `make prod-build`.
