# Contributor workflow

## Branches

Before making or committing new changes, check the current branch. Start new work on a
feature branch whose name describes the work to be done; create or switch to the
appropriate branch before editing, including when the current branch is for unrelated
work. Do not make new changes directly on `main`. Do not prefix branch names unless the
user requests a prefix.

## Commits and approval

Before presenting a change for review, check that affected documentation and agent
guidance have been updated alongside the code, including removals. Follow the
[documentation maintenance rules](documentation.md#keeping-docs-and-guidance-aligned).

Recent history uses short, imperative commit subjects such as `Mirror data into
production-mode Docker`. Keep subjects specific and under roughly 72 characters.

Only commit changes after a developer has reviewed them and approved them for commit.
Prefer separate, focused commits when the changes are better understood or reviewed
independently.

When the work appears complete, ask the developer whether to push the branch, create a
pull request, or both. Wait for their instruction before taking those actions, unless
they have already explicitly authorized them for the current work.

## Changelog

Update `CHANGELOG.md` with each commit when the change is user-facing, operationally
meaningful, or otherwise notable. Keep new entries under `Unreleased` until a release
section is created. When preparing a PR for merging or deployment, move the PR's
changelog entries from `Unreleased` into a dated release section for the deployment
date.

Keep changelog entries concise: one short bullet per notable outcome, combining related
changes. Include key runtime/framework versions where useful; link supporting docs for
dependency inventories, implementation details, and verification records.

## Pull requests

PRs should explain the user-facing or maintenance impact, list any migrations or
environment changes, link related issues, and include screenshots for template or
styling updates. When pushing additional code to a branch that already has an open PR,
update the PR body so it reflects the latest notable changes and matches the changelog
where relevant.

Keep PR summaries concise: lead with one or two sentences describing the result, then
use a few short bullets for key changes, validation, and deployment requirements as
needed. Link detailed evidence and rollback records in supporting docs. Scale the
summary to the change and preserve essential migration or environment instructions.

Run the [relevant checks](testing.md) before presenting changes for review.
