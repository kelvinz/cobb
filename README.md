# cobb

A small set of skills for ongoing product development.

Supported workflows:
- Workflow: `new` → `plan` → `implement` → `review` (when needed) → `commit` (`commit` mode) → `review` (when needed) → `commit` (`finalise` mode) → `compact` (periodic)

These skills are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## What this repo contains

- `skills/new/`: create or update `tasks/todo.md` (project overview + prioritised feature list).
- `skills/plan/`: turn a planned feature into a PRD in `tasks/` and sync `tasks/todo.md` status.
- `skills/implement/`: implement a PRD in the codebase and check off completed PRD stories/tasks.
- `skills/review/`: strict decision review for correctness, security, tests, and scope, with optional durable memory capture.
- `skills/commit/`: propose atomic commits, require user approval, commit with emoji + type + imperative summary, and finalise merge/branch cleanup.
- `skills/memory/`: shared guidance for maintaining `tasks/memory.md` inline across other skills (or via explicit backfill).
- `skills/compact/`: compact `tasks/todo.md` + `tasks/memory.md` by summarising older entries when tracking files get noisy.
- `skills/*/references/` (where present): shared templates/rubrics loaded on demand to keep `SKILL.md` concise.

## Files the skills manage

- `tasks/todo.md`
  - Source of truth for planned features.
  - Each feature has an ID like `f-01` and an optional `Dependencies:` list (by feature ID).
  - Each feature has a `Type:` (`feat` / `fix` / `chore`).
  - Checkbox meaning: unchecked = PRD not written yet; checked = PRD exists.
  - Tracks backlog priority by feature ID (no PRD file paths).

- `tasks/f-##-*.md`
  - One PRD per feature, named with feature ID (e.g., `f-01-invite-teammates.md`).
  - Tracks progress through checklist items on user stories/tasks/acceptance criteria.
  - During finalise, completed PRDs are moved to `tasks/archive/` (same filename, no rename).

- `tasks/memory.md`
  - Living "what matters" record: current state, decisions, milestones, gotchas.

- `tasks/archive/`
  - Archived completed PRDs moved during `commit` finalise.

## Recommended workflows

### Workflow: idea → merged

1. `new` → `plan` → `implement`
   Memory: capture durable decisions inline as each step executes.
2. `review` (when needed): run a quality check before commit.
   Memory: capture durable risks/follow-ups inline when needed.
3. `commit` (`commit` mode): create atomic commits with user approval.
   Memory: capture durable rationale/gotchas inline when needed.
4. `review` (when needed): run a quality check before finalise.
   Memory: capture durable risks/follow-ups inline when needed.
5. `commit` (`finalise` mode): prepare tracking updates (archive completed PRD, apply `tasks/todo.md` completion strikethrough, and update `tasks/memory.md` when needed).
   Create one pre-merge finalise commit only when tracking changes exist, then merge using the repository-approved strategy and delete the completed feature branch safely.
6. `compact` (periodic): summarise older completed+archived todo items and older memory entries to keep tracking files easy to scan.

## Conventions

- Prefer checklists + bullets; avoid Markdown tables.
- Keep one feature per PRD; split work that feels like an epic.
