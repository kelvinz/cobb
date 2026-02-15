# Todo Template Reference

## Template

Use this as the default structure for new `tasks/todo.md` files. Fill in details; keep it concise.

```markdown
# TODO: <Project name>

## Project
- **One-liner**: …
- **Target users**: …
- **Problem**: …
- **Success metrics**: …
- **Constraints** (optional): …
- **Non-goals**: …

## Features

Checkbox meaning:
- unchecked = PRD not written yet
- checked = PRD exists
- checked + ~~strikethrough~~ = completed (PRD archived)
Leave unchecked until a PRD exists.
Feature completion is determined by PRDs archived to `tasks/archive/`
and recorded in `tasks/memory.md`.
Strikethrough here is a derived marker applied during `commit` finalise.

### Features (priority order)
- Higher in the list = higher priority.
- [ ] f-01: <feature name>
  - Type: feat | fix | chore
  - Outcome: <user-visible outcome>
  - In scope: <what ships>
  - Out of scope: <what does not ship>
  - Dependencies: <none> | f-02, f-10

- [ ] f-02: <feature name>
  - Type: feat | fix | chore
  - Outcome: <user-visible outcome>
  - In scope: <what ships>
  - Out of scope: <what does not ship>
  - Dependencies: <none> | f-01

## Open Questions (project-wide only; per-feature questions go under each feature entry)
- Q-1: …
```
