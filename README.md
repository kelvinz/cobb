# cobb

A small set of skills for ongoing product development. The workflow is:

`01-new` → `02-prd` → `03-exe` → `04-rem`

These skills are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## What this repo contains

- `skills/01-new/`: create or update `tasks/todo.md` (project overview + prioritized feature list).
- `skills/02-prd/`: turn a planned feature into a PRD in `tasks/` and sync `tasks/todo.md`.
- `skills/03-exe/`: implement a PRD in the codebase and keep PRD status up to date.
- `skills/04-rem/`: maintain `tasks/memory.md` as durable project memory for handoff.

## Files the skills manage

- `tasks/todo.md`
  - Source of truth for planned features.
  - Each feature has an ID like `F-001` and an optional `Dependencies:` list (by feature ID).
  - Each feature also has a `Type:` (`feat` / `fix` / `chore`).
  - Checkbox meaning: unchecked = PRD not written yet; checked = PRD exists.
  - Priority is determined by list order (higher in the list = higher priority).

- `tasks/prd-*.md`
  - One PRD per feature.
  - Includes `## Execution Status (03-exe)` with:
    - `Implemented`
    - `Tested`
    - `Released`
  - User stories are checklists (so execution can be done in pieces) and include acceptance-criteria checkboxes.

- `tasks/memory.md`
  - A living “what matters” record: current state, key decisions, completed milestones, and gotchas.
  - Written for someone taking over the project (or you returning later).

## Recommended workflow

1. `01-new`: start a new project or add/reprioritize features in `tasks/todo.md`.
2. `02-prd`: choose a feature (prefer `F-###`) and create/update its PRD in `tasks/`.
   - `02-prd` checks the feature box in `tasks/todo.md` (meaning: PRD exists).
3. `03-exe`: execute the PRD in the codebase.
   - Create a feature branch before making changes.
   - Prefer branch prefixes based on PRD `Type`: `feat/`, `fix/`, `chore/`.
   - Check dependency PRDs and ensure they are **Implemented** before proceeding.
   - Update the PRD’s execution status checkboxes as you go.
4. `04-rem`: whenever you make a durable decision, learn a gotcha, or complete a milestone, capture it in `tasks/memory.md`.

## Conventions

- Prefer checklists + bullets; avoid Markdown tables.
- Keep “one feature = one PRD”. If it feels like an epic, split it.
