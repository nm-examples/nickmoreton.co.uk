# Portfolio management

Portfolio projects are independent Wagtail snippets under **Portfolio → Projects**.
Each project has a title, category, description, screenshot and image description,
website URL, Made with Wagtail record URL, and **Show in hero** checkbox. Projects
support revisions and draft/publish actions.

The homepage's **Past website projects** panel selects and orders project
references. Only published projects appear publicly. The hero independently
chooses a random published project with **Show in hero** enabled and a screenshot
attached. A project can appear in either place, both, or neither. With no eligible
hero project, the screenshot is omitted.

## Fetch and review

1. Open **Portfolio → Source records** and select **Refresh from GitHub**.
2. Review a record and choose **Create snippet** or **Review source changes**.
3. Compare the last reviewed source, current snippet (including pending draft
   edits), and incoming source. Select the fields to apply and adjust their
   incoming values if needed. Existing snippets start with no fields selected.
4. Optionally import the source screenshot into Wagtail's image library.
5. Select **Save project draft**, then review and publish in the snippet editor.
6. Set **Show in hero** on the snippet and select homepage projects independently.

The source listing uses Wagtail's standard slim header, search, sorting, filters,
pagination, and row actions. The header's refresh button submits a POST request;
the records themselves are read-only until reviewed into a snippet draft.

The fixed source is
[`wagtail/madewithwagtail`, Nick Moreton's developer directory](https://github.com/wagtail/madewithwagtail/tree/main/src/content/developers/nick-moreton).
No GitHub credentials or new environment variables are needed. Fetching uses
public GitHub endpoints, so their availability and anonymous API limits apply.
Refresh is an explicit admin request; there is no scheduled fetch or background
worker. Requests have connection/read timeouts and fetch project Markdown with
up to four concurrent requests.

Each refresh pins all records and screenshot URLs to one repository commit. The
complete snapshot is validated before staging records are changed. The staging
table stores raw Markdown, parsed metadata, mapped project fields, the source path,
commit, fingerprint, and fetch time. Source paths identify records across refreshes;
the fingerprint includes the project directory's Git tree so screenshot changes
also flag the record. Metadata sectors map to the editable category; the Markdown
body becomes an editable plain-text description.

This adapter reads Nick's own developer directory. Cooperation credits stored
elsewhere in the upstream repository and automatic path-rename reconciliation
remain outside this implementation. A renamed source path appears as a new
record while its previous path is flagged missing. The broader adapter work is
tracked in [issue #85](https://github.com/nm-examples/nickmoreton.co.uk/issues/85).

Refreshing does not create, edit, or publish snippets. Existing migrated projects
are linked to their first matching source record by exact portfolio-record URL,
when the match is unambiguous. Records missing from a successful complete refresh
are flagged; their data and snippets are retained. Failed fetches preserve the
previous snapshot.

Source status is **New**, **Not yet reviewed**, **Source changed**, **Up to date**,
or **Missing upstream**. **Up to date** means the current source version was
reviewed and used to save a draft. It does not mean every source field was copied
or that the draft has been published. The last reviewed source snapshot and time
are retained separately from edited snippet values. An editor may deliberately
keep local wording while accepting the source version as reviewed.

Import saves a revision based on the latest snippet draft, preserving unselected
fields, its current screenshot unless selected for import, **Show in hero**, and
all homepage references. Intervening source or snippet revisions reject the save
and require a fresh review. Repeating a create submission cannot create a second
snippet for the same source record.

Screenshots are downloaded only during an explicitly selected import, checked
as WebP images with an 8 MB limit, and reused by file hash when already imported.
A failed screenshot import does not save the snippet or its source-review state.
Public page rendering reads the local database and media storage only.

## Permissions

Source browsing requires **Can view portfolio source record**. Fetching additionally
requires **Can refresh portfolio data from GitHub**. Creating/updating snippets
requires the corresponding project permission, and screenshot import requires
**Can add image**. Publication uses Wagtail's separate snippet publish permission.
All mutations use CSRF-protected POST requests. Superusers have these permissions.

## Migration and deployment

Run the normal locked dependency install and migrations:

```sh
docker compose exec app uv sync --locked
docker compose exec app python manage.py migrate
docker compose exec app python manage.py update_index
docker compose exec app python manage.py rebuild_references_index
```

`portfolio.0001` creates the snippet and staging tables. `home.0007` moves existing
inline projects into snippets and ordered homepage references, reusing existing
Wagtail images. It also converts saved homepage revision content, retaining live
and draft selection differences and revision IDs. Current live projects remain
published and hero-eligible, preserving the previous random-hero behaviour.
Projects found only in older revisions or drafts become unpublished snippets;
publish them separately if you later want to display them. The migration performs
no external requests and creates no staging records.

The existing `populate_redesign` setup command remains dry-run by default. Its
`--apply` path now creates snippets and selections when the homepage selection is
empty. Ongoing source refreshes should use the admin workflow.

Build/deploy application dependencies, run migrations, and refresh search/reference
indexes through the usual deployment workflow. No frontend bundle changes are
required. Back up the database and media before deployment. Reversing `home.0007`
reconstructs inline homepage blocks from the then-current snippet values; it
cannot recover earlier inline values after subsequent snippet edits. Restore the
pre-deployment backup when an exact data rollback is needed. Reversing the new
portfolio schema removes its snippet and staging data.

## Verification

All 70 tests pass in both development and production-mode PostgreSQL suites,
covering source failures,
permissions and CSRF, source review and draft creation, selective updates,
stale reviews, image reuse/failures, independent hero selection, ordered homepage
selections, and migration of live/draft/historical content with reversal.

The live local source listing, snippet listing, and review route were checked for
HTTP 200 responses. The public GitHub source snapshot was validated against all
ten records without applying it to snippets. Docker production-mode builds,
migrations, static collection, system checks, and Python checks were also run.

The [source listing screenshot](review/portfolio/source-records.png) shows the
native header and help panel. It was captured from an authenticated server-rendered
HTML snapshot with the local Wagtail assets; it does not represent a browser
sign-in or an import submission.
