# cobb

A small set of skills for ongoing product development. The workflow is:

`01-new` → `02-plan` → `03-implement` → `04-propose` (optional) → `05-review` → `06-memory`

These skills are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## What this repo contains

- `skills/01-new/`: create or update `tasks/todo.md` (project overview + prioritized feature list).
- `skills/02-plan/`: turn a planned feature into a prd in `tasks/` and sync `tasks/todo.md`.
- `skills/03-implement/`: implement a prd in the codebase and mark it **Implemented**.
- `skills/04-propose/`: push the branch and open/update a Draft PR via `gh` with a best-practice title/body (optional).
- `skills/05-review/`: review a PR (preferred) or a local diff; mark **Reviewed**, and when merged finalize tracking.
- `skills/06-memory/`: maintain `tasks/memory.md` as durable project memory for handoff.

## Files the skills manage

- `tasks/todo.md`
  - Source of truth for planned features.
  - Each feature has an ID like `f-01` and an optional `Dependencies:` list (by feature ID).
  - Each feature also has a `Type:` (`feat` / `fix` / `chore`).
  - **Checkbox meaning: unchecked = prd not written yet; checked = prd exists (not "done").**
  - **Status legend: `—` = not started | `🔨` = implemented | `✅` = merged** (managed by `03-implement` and `05-review`).
  - Priority is determined by list order (higher in the list = higher priority).
  - Build/release status lives in the prd's `## Execution Status` section.

- `tasks/f-##-*.md`
  - One prd per feature, named with feature ID (e.g., `f-01-invite-teammates.md`).
  - Renamed with `done-` prefix when merged (e.g., `done-f-01-invite-teammates.md`).
  - Includes `## Execution Status` with:
    - `Implemented` (code + tests done)
    - `Reviewed` (review completed with LGTM)
    - `Merged` (PR merged to main)
  - User stories are checklists (so execution can be done in pieces) and include acceptance-criteria checkboxes.
  - `prd:` links in `tasks/todo.md` are managed by `02-plan`.

- `tasks/memory.md`
  - A living "what matters" record: current state, key decisions, completed milestones, and gotchas.
  - Written for someone taking over the project (or you returning later).

## Recommended workflow

### PR flow: idea → merged

1. **`01-new`**: Start a new project or add/reprioritize features in `tasks/todo.md`.
   - Features start with `|  —` status indicator.

2. **`02-plan`**: Choose a feature (prefer highest-priority unchecked) and create its prd.
   - Checks the feature box in `tasks/todo.md` (meaning: prd exists).
   - Status remains `—`.

3. **`03-implement`**: Execute the prd in the codebase.
   - Create a feature branch (`feat/`, `fix/`, or `chore/` prefix based on `Type`).
   - Verify dependency prds are **Implemented** before proceeding.
   - When done: check **Implemented** in prd, update status to `🔨` in `tasks/todo.md`.

4. **`04-propose`** (optional): Push branch and open/update a Draft PR via `gh`.
   - If you’re not using a PR for this work, skip this step.

5. **`05-review`**: Review the change set (PR mode preferred; local diff also supported).
   - When LGTM: check **Reviewed** in the prd.

6. **Merge PR**: After review, merge the PR to the base branch.

7. **`05-review`** (post-merge): Run again to finalize tracking when the PR is merged.
   - Check **Merged** in prd.
   - Rename prd to `done-f-##-<slug>.md`.
   - Update the `prd:` path in `tasks/todo.md`.
   - Update status to `✅` in `tasks/todo.md`.

8. **`06-memory`**: Capture the milestone in `tasks/memory.md`.

### Local flow: idea → reviewed (no PR)

1. **`01-new`** → **`02-plan`** → **`03-implement`**
2. **`05-review`** (local mode): Review `base...HEAD`, capture blockers/risks, and check **Reviewed** if LGTM.
3. **`06-memory`**: Capture durable notes and follow-ups.

### Ongoing: `06-memory`

Use `06-memory` anytime you make a durable decision, learn a gotcha, or complete a milestone.

## Conventions

- Prefer checklists + bullets; avoid Markdown tables.
- Keep "one feature = one prd". If it feels like an epic, split it.
