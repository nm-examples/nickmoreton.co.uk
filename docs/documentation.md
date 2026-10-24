# Documentation standards

Keep documentation useful, concise, and close to the work it explains. These rules
apply to human and AI contributors.

## Keeping docs and guidance aligned

For every code change, including removal, check existing references to the changed
files and behaviour. Correct or remove inaccurate documentation in the same change.
Check agent guidance and skill references when their instructions are affected.
**Checking documentation does not require adding documentation.** Leave accurate,
unaffected prose alone; do not add a README paragraph for every code change.

## Where information belongs

| Information | Home |
| --- | --- |
| Non-obvious behaviour, constraints, or reasons for an implementation choice | A short docstring or comment beside the owning code. |
| App purpose, useful entry points, and practical CMS editor instructions | A short app README. |
| Setup, commands, deployment, backups, and decisions spanning apps | The relevant project document under `docs/` or the root README. |
| Completed work and migration history | Git and the changelog; retain operational recovery instructions where still needed. |

Keep one authoritative explanation. Link to it when another audience needs it rather
than repeating its details in a README, architecture guide, and source comment.

## Writing source documentation

- Explain reasons, surprising behaviour, side effects, and constraints that a future
  change could accidentally break. Do not narrate readable queries or conditions.
- Omit obvious field inventories, framework boilerplate explanations, and comments
  that restate names or literal values. Delete redundant prose instead of relocating it.
- Keep comments and docstrings proportionate to the code. A sentence is often enough;
  use longer explanations only where the complexity requires them.
- Put template, JavaScript, and stylesheet guidance beside the relevant implementation.
  Document reusable interfaces and non-obvious assumptions at their definitions.
- Use type hints for new or changed functions where practical; do not change behaviour
  merely to move documentation.

## App READMEs

There is no required section template. Usually a brief purpose, a few links to key
code, and editor instructions are enough. Include only sections that answer an actual
reader question. Keep publishing effects and permissions visible to editors; keep
method internals with the implementation.

Link to shared verification and operational instructions instead of copying commands
or test inventories into each app README. Do not create a README solely to satisfy
this guidance, and do not turn a simple feature into a design document.

Before finishing, remove stale links and duplicated explanations. A small code change
may need no prose changes; a documentation cleanup should reduce maintenance work.
