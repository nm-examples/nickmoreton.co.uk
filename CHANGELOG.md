# Changelog

Notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), with an `Unreleased` section for changes that have not shipped yet.

## Unreleased

### Added
- Add changelog tracking for notable project changes.

### Changed
- Document `staging` as the local Dokku verification branch and protect `main` as the production auto-deploy branch.
- Replace Black, Flake8, and isort with Ruff for Python formatting and linting.
- Clarify that local Dokku is for production-like staging, not day-to-day development.
- Move the Dokku setup script to `scripts/dokku-setup.sh`.
- Make the Dokku setup script accept configurable SSH public keys.
- Remove obsolete Linode deployment documentation.
