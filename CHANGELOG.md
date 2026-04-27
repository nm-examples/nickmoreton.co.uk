# Changelog

Notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), with an `Unreleased` section for changes that have not shipped yet.

## Unreleased

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
- Clarify that local Dokku is for production-like staging, not day-to-day development.
- Move the Dokku setup script to `scripts/dokku-setup.sh`.
- Make the Dokku setup script accept configurable SSH public keys.
- Remove obsolete Linode deployment documentation.
