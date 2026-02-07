# cobb

A small set of skills for ongoing product development.

Supported workflows:
- PR workflow: `new` → `plan` → `implement` → `review` (local, when needed) → `commit` → `open-pr` → `review` (pr, when needed) → `commit` (finalise) → `memory`
- Local workflow: `new` → `plan` → `implement` → `review` (local, when needed) → `commit` → `memory`

These skills are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## What this repo contains

- `skills/new/`: create or update `tasks/todo.md` (project overview + prioritised feature list).
- `skills/plan/`: turn a planned feature into a prd in `tasks/` and sync `tasks/todo.md`.
- `skills/implement/`: implement a prd in the codebase and check off completed prd stories/tasks.
- `skills/review/`: strict report-only review in either `pr` mode or `local` mode.
- `skills/commit/`: propose atomic commits, require user approval, commit with emoji + type + imperative summary, and finalise merge/branch cleanup.
- `skills/open-pr/`: push a branch and open/update a Draft PR via `gh`.
- `skills/memory/`: maintain `tasks/memory.md` as durable project memory for handoff.

## Files the skills manage

- `tasks/todo.md`
  - Source of truth for planned features.
  - Each feature has an ID like `f-01` and an optional `Dependencies:` list (by feature ID).
  - Each feature has a `Type:` (`feat` / `fix` / `chore`).
  - Checkbox meaning: unchecked = prd not written yet; checked = prd exists.
  - Tracks backlog priority and prd linkage for each feature.

- `tasks/f-##-*.md`
  - One prd per feature, named with feature ID (e.g., `f-01-invite-teammates.md`).
  - Tracks progress through checklist items on user stories/tasks/acceptance criteria.
  - During finalise, prds are renamed to `done-f-##-<slug>.md` before merge.

- `tasks/memory.md`
  - Living "what matters" record: current state, decisions, milestones, gotchas.

## Recommended workflows

### PR flow: idea → merged

1. `new`: define or reprioritise features in `tasks/todo.md`.
2. `plan`: create/update one feature prd and link it in `tasks/todo.md`.
3. `implement`: build the prd and check off completed stories/tasks.
4. `review` (`local` mode, when needed): run a quality check before commit.
5. `commit` (`commit` mode): create atomic commits with user approval.
6. `open-pr`: push branch and open/update Draft PR.
7. `review` (`pr` mode, when needed): run a quality check before finalise.
8. `commit` (`finalise` mode): rename prd with `done-`, update `tasks/todo.md` `prd:` path in a final tracking commit, then merge/close branch and delete completed feature branch safely.
9. `memory`: capture durable outcomes and follow-ups.

### Local flow: idea → committed (no PR)

1. `new` → `plan` → `implement`
2. `review` (`local` mode, when needed)
3. `commit` (`commit` mode)
4. `memory`

## Conventions

- Prefer checklists + bullets; avoid Markdown tables.
- Keep one feature per prd; split work that feels like an epic.
