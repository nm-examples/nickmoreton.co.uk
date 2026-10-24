# Home app

Owns homepage copy, portfolio snippets, and the article/package lists.

- [models.py](models.py): content models and homepage queries.
- [Homepage templates](templates/home/): page composition and section includes.

Edit Introduction and About on the homepage. Manage projects under **Snippets →
Portfolio projects**, then choose and order them on the homepage. Publish the page
to apply selection changes. Removing a selection leaves the snippet available;
saving a snippet updates its content immediately wherever it is displayed.

Headings, profile details, and profile links are maintained in the templates.
Empty content sections are hidden until content is available.

See [testing](../../docs/testing.md) for verification and
[data and media workflows](../../docs/data-and-media.md) for imports and recovery.
