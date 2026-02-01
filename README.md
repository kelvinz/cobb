# cobb

A small set of skills for ongoing product development. The workflow is:

`01-new` → `02-prd` → `03-exe` → `04-rem`

These skills are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## What this repo contains

- `skills/01-new/`: create or update `tasks/todo.md` (project overview + prioritized feature list).
- `skills/02-prd/`: turn a planned feature into a prd in `tasks/` and sync `tasks/todo.md`.
- `skills/03-exe/`: implement a prd in the codebase and keep prd status up to date.
- `skills/04-rem/`: maintain `tasks/memory.md` as durable project memory for handoff.

## Files the skills manage

- `tasks/todo.md`
  - Source of truth for planned features.
  - Each feature has an ID like `f-01` and an optional `Dependencies:` list (by feature ID).
  - Each feature also has a `Type:` (`feat` / `fix` / `chore`).
  - **Checkbox meaning: unchecked = prd not written yet; checked = prd exists (not "done").**
  - Priority is determined by list order (higher in the list = higher priority).
  - Build/release status lives in the prd's `Execution Status (03-exe)` section.

- `tasks/f-##-*.md`
  - One prd per feature, named with feature ID (e.g., `f-01-invite-teammates.md`).
  - Renamed with `done-` prefix when merged (e.g., `done-f-01-invite-teammates.md`).
  - Includes `## Execution Status (03-exe)` with:
    - `Implemented` (code + tests done)
    - `Merged` (PR merged to main)
  - User stories are checklists (so execution can be done in pieces) and include acceptance-criteria checkboxes.
  - `prd:` links in `tasks/todo.md` are managed by `02-prd`.

- `tasks/memory.md`
  - A living “what matters” record: current state, key decisions, completed milestones, and gotchas.
  - Written for someone taking over the project (or you returning later).

## Recommended workflow

1. `01-new`: start a new project or add/reprioritize features in `tasks/todo.md`.
2. `02-prd`: choose a feature (prefer `f-##`) and create/update its prd in `tasks/`.
   - `02-prd` checks the feature box in `tasks/todo.md` (meaning: prd exists).
3. `03-exe`: execute the prd in the codebase.
   - Create a feature branch before making changes.
   - Prefer branch prefixes based on prd `Type`: `feat/`, `fix/`, `chore/`.
   - Check dependency prds and ensure they are **Implemented** before proceeding.
   - Update the prd’s execution status checkboxes as you go.
4. `04-rem`: whenever you make a durable decision, learn a gotcha, or complete a milestone, capture it in `tasks/memory.md`.

## Conventions

- Prefer checklists + bullets; avoid Markdown tables.
- Keep “one feature = one prd”. If it feels like an epic, split it.
