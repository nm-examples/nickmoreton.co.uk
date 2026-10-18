# Changelog

Notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), with an `Unreleased` section for changes that have not shipped yet.

## Unreleased

### Changed

- Upgrade to Python 3.14.8, Django 6.0.9, Wagtail 7.4.3 LTS, and Node 24.22.0.
- Refresh dependencies, pin Debian Trixie builds, and standardize locked installs.

### Added

- Add PostgreSQL regression tests and frontend CI checks.
- Add Python and Node upgrade skills, dependency inventories, and verification/rollback records.
- Add a repository-local Node frontend upgrade skill with version selection, the latest stable Debian Node image policy, companion-file checks, and a read-only npm lockfile inventory helper.
- Add a repository-local Python upgrade skill with recorded version selection, companion-file checks, and a read-only lockfile inventory helper.
- Add static redesign reference pages and images, with preview and Wagtail integration documentation.
- Add a Wagtail redesign implementation plan covering content models, templates, assets, and validation.
- Add editable homepage introduction, profile, About, and portfolio content, with a repeatable population command for the supplied redesign content.
- Add article and package presentation fields and optional navigation URLs and section anchors.
- Add heading contents links, expandable code examples, and regression tests.
- Add redesign integration and rollout guidance with desktop and mobile review screenshots.

### Changed
- Increase article, chapter, and package body text to 17px on desktop and mobile, and sidebar text by 1px, and darken body and sidebar text for easier reading.
- Simplify the footer to a single Back to top link.
- Remove numeric prefixes from homepage section labels.
- Replace the header’s n/m lettering with offset orange and white dots and a soft orange-dot shadow inside a purple rounded square, and use the same mark for favicons.
- Remove the circular n/m mark from article and package bylines, retaining the author name and date.
- Correct Nick’s title to Support Engineer and describe him as an engineer working in Torchbox’s support team in the homepage, CMS defaults, and redesign reference.
- Keep homepage and archive listings and related content scoped to published, public pages.
- Replace Pico styling with the supplied design components and Sass modules.
- Support WebP source assets and consistent image output extensions in the frontend image build.
- Apply the redesign theme across the homepage, archives, details, chapters, search, and error pages using app-owned templates and the existing frontend build.
- Add progressive mobile navigation, archive filtering, and code copying while preserving content access without JavaScript.
- Cache PyPI metadata and handle request failures without breaking package pages.
- Exclude restricted pages from site search.

### Fixed

- Clean generated assets before starting frontend watchers and stop watchers on build failures.
- Build and collect static assets in CI before running template-rendering tests.
- Keep article, chapter, and package contents links clear of shared template IDs.

## 2026-04-28

### Added

- Add a production-mode Docker Compose workflow with Gunicorn, Postgres, and nginx for local `DEBUG = False` checks.
- Add commands to mirror local development data and media into the production-mode Docker stack.
- Build frontend assets inside the production-mode Docker image.
- Add a command to pull Heroku data directly into the production-mode Docker database.
- Add a command to pull S3 media directly into production-mode Docker media.
- Add a `prod-destroy` command to remove production-mode Docker volumes.
- Add a `prod-quickstart` command for first production-mode boots.
- Add a favicon based on the header logo mark.

### Changed

- Allow production-mode Docker to run without first setting up local development data or media.
- Wait for production-mode Postgres before importing data.
- Restart production-mode app and nginx services after importing data.

### Removed

- Remove the local Dokku commands and documentation.

## 2026-04-27

### Changed

- Add Biome checks for frontend JavaScript and JSON files.
- Make code block copy tabs directly clickable and improve their keyboard focus and small-screen visibility.
- Upgrade the local Node version and frontend build dependencies.

## 2026-04-26

### Added

- Add changelog tracking for notable project changes.

### Changed

- Replace Black, Flake8, and isort with Ruff for Python formatting and linting.
- Update Python dependency floors, including `psycopg2` 2.9.12 for production runtime and `pre-commit` 4.6.0 for development hooks.
- Clarify that local Dokku is for production-like verification, not day-to-day development.
- Move the Dokku setup script to `scripts/dokku-setup.sh`.
- Make the Dokku setup script accept configurable SSH public keys.
- Remove obsolete Linode deployment documentation.
