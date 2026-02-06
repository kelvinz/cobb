# cobb

A small set of skills for ongoing product development.

Supported workflows:
- PR workflow: `new` → `plan` → `implement` → `review` (local) → `commit` → `open-pr` → `review` (pr) → `commit` (finalise) → `memory`
- Local workflow: `new` → `plan` → `implement` → `review` (local) → `commit` → `memory`

These skills are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## What this repo contains

- `skills/new/`: create or update `tasks/todo.md` (project overview + prioritised feature list).
- `skills/plan/`: turn a planned feature into a prd in `tasks/` and sync `tasks/todo.md`.
- `skills/implement/`: implement a prd in the codebase and mark it **Implemented**.
- `skills/review/`: strict report-only review in either `pr` mode or `local` mode.
- `skills/commit/`: propose atomic commits, require user approval, commit with emoji + type + imperative summary, and optionally finalise merge/branch cleanup.
- `skills/open-pr/`: push a branch and open/update a Draft PR via `gh`.
- `skills/memory/`: maintain `tasks/memory.md` as durable project memory for handoff.

## Files the skills manage

- `tasks/todo.md`
  - Source of truth for planned features.
  - Each feature has an ID like `f-01` and an optional `Dependencies:` list (by feature ID).
  - Each feature has a `Type:` (`feat` / `fix` / `chore`).
  - Checkbox meaning: unchecked = prd not written yet; checked = prd exists.
  - Status legend: `—` = not started | `🔨` = implemented | `✅` = merged.
  - Status ownership: `implement` sets `🔨`; `commit` (finalise mode) sets `✅`.

- `tasks/f-##-*.md`
  - One prd per feature, named with feature ID (e.g., `f-01-invite-teammates.md`).
  - Includes `## Execution Status` with `Implemented`, `Reviewed`, and `Merged`.
  - Tracking ownership:
    - `implement`: `Implemented`
    - `commit` (after positive review/finalisation): `Reviewed` / `Merged`
  - May be renamed with a `done-` prefix after merge.

- `tasks/memory.md`
  - Living "what matters" record: current state, decisions, milestones, gotchas.

## Recommended workflows

### PR flow: idea → merged

1. `new`: define or reprioritise features in `tasks/todo.md`.
2. `plan`: create/update one feature prd and link it in `tasks/todo.md`.
3. `implement`: build the prd and mark **Implemented**.
4. `review` (`local` mode): decide whether it is **Good to commit**.
5. `commit` (`commit` mode): create atomic commits with user approval.
6. `open-pr`: push branch and open/update Draft PR.
7. `review` (`pr` mode): decide whether it is **Ready to accept PR**.
8. `commit` (`finalise` mode): ask for target branch (`main`/`dev`/etc), merge/close branch, delete completed feature branch safely, and sync tracking.
9. `memory`: capture durable outcomes and follow-ups.

### Local flow: idea → committed (no PR)

1. `new` → `plan` → `implement`
2. `review` (`local` mode)
3. `commit` (`commit` mode)
4. `memory`

## Conventions

- Prefer checklists + bullets; avoid Markdown tables.
- Keep one feature per prd; split work that feels like an epic.
