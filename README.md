# cobb

A small set of skills for ongoing product development.

Supported workflows:
- PR workflow: `new` → `plan` → `implement` → `review` (local, when needed) → `commit` → `open-pr` → `review` (pr, when needed) → `commit` (finalise) → `compact` (periodic)
- Local workflow: `new` → `plan` → `implement` → `review` (local, when needed) → `commit` → `compact` (periodic)

These skills are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## What this repo contains

- `skills/new/`: create or update `tasks/todo.md` (project overview + prioritised feature list).
- `skills/plan/`: turn a planned feature into a prd in `tasks/` and sync `tasks/todo.md` status.
- `skills/implement/`: implement a prd in the codebase and check off completed prd stories/tasks.
- `skills/review/`: strict decision review in either `pr` mode or `local` mode, with optional durable memory capture.
- `skills/commit/`: propose atomic commits, require user approval, commit with emoji + type + imperative summary, and finalise merge/branch cleanup.
- `skills/open-pr/`: push a branch and open/update a Draft PR via `gh`.
- `skills/memory/`: shared guidance for maintaining `tasks/memory.md` inline across other skills (or via explicit backfill).
- `skills/compact/`: compact `tasks/todo.md` + `tasks/memory.md` by summarising older entries when tracking files get noisy.

## Files the skills manage

- `tasks/todo.md`
  - Source of truth for planned features.
  - Each feature has an ID like `f-01` and an optional `Dependencies:` list (by feature ID).
  - Each feature has a `Type:` (`feat` / `fix` / `chore`).
  - Checkbox meaning: unchecked = prd not written yet; checked = prd exists.
  - Tracks backlog priority by feature ID (no PRD file paths).

- `tasks/f-##-*.md`
  - One prd per feature, named with feature ID (e.g., `f-01-invite-teammates.md`).
  - Tracks progress through checklist items on user stories/tasks/acceptance criteria.
  - During finalise, completed prds are moved to `tasks/archive/` (same filename, no rename).

- `tasks/memory.md`
  - Living "what matters" record: current state, decisions, milestones, gotchas.

- `tasks/archive/`
  - Archived completed PRDs moved during `commit` finalise.

## Recommended workflows

### PR flow: idea → merged

1. `new`: define or reprioritise features in `tasks/todo.md`.
   Memory: capture durable project/scope/priority decisions inline when needed.
2. `plan`: create/update one feature prd and mark the feature as planned in `tasks/todo.md`.
   Memory: capture durable requirement/constraint decisions inline when needed.
3. `implement`: build the prd and check off completed stories/tasks.
   Memory: capture durable implementation decisions/gotchas inline when needed.
4. `review` (`local` mode, when needed): run a quality check before commit.
   Memory: capture durable risks/follow-ups inline when needed.
5. `commit` (`commit` mode): create atomic commits with user approval.
   Memory: capture durable rationale/gotchas inline when needed.
6. `open-pr`: push branch and open/update Draft PR.
7. `review` (`pr` mode, when needed): run a quality check before finalise.
   Memory: capture durable risks/follow-ups inline when needed.
8. `commit` (`finalise` mode): prepare tracking updates (archive completed prd, apply `tasks/todo.md` completion strikethrough, and update `tasks/memory.md` when needed), create one pre-merge finalise commit only when tracking changes exist, then merge using the repository-approved strategy (merge/squash/rebase), close branch, and delete the completed feature branch safely.
9. `compact` (periodic): summarise older completed+archived todo items and older memory entries to keep tracking files easy to scan.

### Local flow: idea → committed (no PR)

1. `new` → `plan` → `implement`
   Memory: capture durable decisions inline as each step executes.
2. `review` (`local` mode, when needed)
   Memory: capture durable risks/follow-ups inline when needed.
3. `commit` (`commit` mode)
   Memory: capture durable rationale/gotchas inline when needed.
4. `compact` (periodic)

## Conventions

- Prefer checklists + bullets; avoid Markdown tables.
- Keep one feature per prd; split work that feels like an epic.
