# Data and Media Workflows

These workflows are for intentional local verification operations. They can replace local data, copy production-derived content, and create temporary files. Do not run them against production unless that is explicitly the goal.

## Requirements

Copy the example environment file before using normal development or
Heroku-backed data/media targets:

```bash
cp .env.example .env
```

Set `HEROKU_APP_NAME` in `.env` before running Heroku-backed commands:

```bash
HEROKU_APP_NAME=your-heroku-app-name
```

The Heroku and S3 workflows also depend on local tools and credentials:

- Heroku CLI access to the configured app.
- `s3cmd` for media sync.
- AWS values from the Heroku app config: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_STORAGE_BUCKET_NAME`.

Use `make extract-vars` to copy Heroku config vars into `.env` when you need the full set of remote environment values locally.

Production-mode local checks do not require `.env`, pulled Heroku data, or
copied media. Run `make prod-run` to start a blank migrated production-mode
site, then use the workflows below only when you want production-derived
content.

## Pull Production Data Locally

Pull a Heroku Postgres backup and import it into the local Docker Postgres database:

```bash
make pull-data
```

This command:

- Downloads the latest Heroku database backup.
- Recreates the local `webapp` database.
- Restores the backup into the local database.
- Removes `db_backups/latest.dump` after import.

The local database is replaced by this workflow.

## Pull Production Media Locally

Sync original images from S3 into local `media/original_images`:

```bash
make pull-media
```

This command:

- Rebuilds `.env` values from Heroku config.
- Removes the local `media/` directory.
- Creates a temporary `.s3cfg`.
- Syncs S3 original images into local media.
- Deletes Wagtail image renditions so they regenerate from the copied originals.

The local media directory is replaced by this workflow.

## Copy Local Data to Production-Mode Docker

This optional workflow mirrors local development content into production mode.
It is not required before running `make prod-run`.

Export the local Docker Postgres database and import it into the isolated
production-mode Postgres volume:

```bash
make prod-push-data
```

This command:

- Exports the normal local development database to `db_backups/backup.dump`.
- Starts the production-mode Postgres service if needed.
- Recreates the production-mode `webapp` database.
- Restores `db_backups/backup.dump` into production-mode Postgres.
- Starts or recreates the production-mode containers.

To import an existing `db_backups/backup.dump` without exporting again, run:

```bash
make prod-import-data
```

This replaces only the production-mode database. It does not modify the normal
local development database or the Heroku database.

## Pull Production Data Directly to Production-Mode Docker

Use this optional workflow when you want production-mode Docker to use Heroku
data without first setting up or exporting the normal local development
database:

```bash
make prod-pull-data
```

This command:

- Downloads the latest Heroku database backup.
- Starts the production-mode Postgres service if needed.
- Recreates the production-mode `webapp` database.
- Restores the backup into production-mode Postgres.
- Starts or recreates the production-mode containers.
- Removes the temporary `db_backups/prod-latest.dump` file after import.

This replaces only the production-mode database. It does not modify the normal
local development database or the Heroku database.

## Copy Local Media to Production-Mode Docker

This optional workflow mirrors local development media into production mode. It
is not required before running `make prod-run`.

Copy local development media into the isolated production-mode media directory:

```bash
make prod-push-media
```

This command:

- Replaces `prod_media/` with a copy of local `media/`.
- Starts the production-mode Postgres service if needed.
- Deletes Wagtail image renditions in the production-mode database so they
  regenerate from the copied originals.

The production-mode nginx container serves files from `prod_media/` at
`/media/`. Check the app after importing data and copying media:

```bash
make prod-run
curl -I -L https://prod-nginx.nickmoreton-production.orb.local
```

## Pull Production Media Directly to Production-Mode Docker

Use this optional workflow when you want production-mode Docker to use S3 media
without first syncing media into the normal local development directory:

```bash
make prod-pull-media
```

This command:

- Rebuilds `.env` values from Heroku config.
- Replaces `prod_media/`.
- Syncs S3 original images into `prod_media/original_images`.
- Deletes Wagtail image renditions in the production-mode database so they
  regenerate from the copied originals.

This replaces only production-mode media. It does not modify normal local
development media or S3.

## Generated Files and Cleanup

These workflows may create or replace:

- `db_backups/`
- `db_backups/backup.dump`
- `.s3cfg`
- `copy-media.sh`
- `media/`
- `prod_media/`
- local database content

Run cleanup intentionally. The `make clean` target removes generated local development files and destroys Docker data after prompting for confirmation.
