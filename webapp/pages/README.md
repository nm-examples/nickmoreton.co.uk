# Pages app

Owns articles, chapters, packages, and their shared content rendering.

- [models.py](models.py): page hierarchy, listings, and chapter navigation.
- [content.py](content.py): rendered body and heading anchors for contents links.
- [blocks.py](blocks.py): shared StreamField blocks.
- [pypi_tags.py](templatetags/pypi_tags.py): package release information.

Manage content through Wagtail pages. Articles can contain chapters; packages belong
under a package index. Lower homepage-order values appear first. A package's featured
flag changes card presentation, not whether it appears on the homepage.

See [testing](../../docs/testing.md) for verification.
