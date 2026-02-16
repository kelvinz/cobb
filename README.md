# cobb

A small set of skills for ongoing product development.

Supported workflows:
- Workflow: `prd` → `design` (optional, for UI/UX-heavy features) → `implement` → `review` (when needed) → `commit` (`commit` mode) → `review` (when needed) → `commit` (`finalise` mode) → `compact` (periodic)

These skills are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## What this repo contains

- `skills/prd/`: create, update, or list PRDs (`tasks/f-##-*.md`) with status and priority. Handles project setup and ongoing feature planning.
- `skills/design/`: optional design workflow for UI/UX direction, interaction/motion, and reusable visual patterns before or during implementation.
- `skills/implement/`: implement a PRD in the codebase and check off completed PRD stories/tasks.
- `skills/review/`: strict decision review for correctness, security, tests, and scope, with optional durable context capture.
- `skills/commit/`: propose atomic commits, require user approval, commit with emoji + type + imperative summary, and finalise merge/branch cleanup.
- `skills/context/`: shared guidance for maintaining `tasks/context.md` inline across other skills (or via explicit backfill).
- `skills/compact/`: compact `tasks/context.md` by summarising older entries when tracking files get noisy.
- `skills/*/references/` (where present): shared templates/rubrics loaded on demand to keep `SKILL.md` concise.

## Files the skills manage

- `tasks/f-##-*.md`
  - One PRD per feature, named with feature ID (e.g., `f-01-invite-teammates.md`).
  - Each PRD is a self-contained spec with `Status:` (draft | ready), `Priority:` (P0–P3), and `Type:` (feat | fix | chore).
  - Tracks progress through checklist items on user stories/tasks/acceptance criteria.
  - During finalise, completed PRDs are moved to `tasks/archive/` (same filename, no rename).

- `tasks/context.md`
  - Project state, key decisions, milestones, and gotchas — written for handoff.

- `tasks/archive/`
  - Archived completed PRDs moved during `commit` finalise.

## Recommended workflows

### Workflow: idea → merged

1. `prd` → `design` (optional for UI/UX-heavy features) → `implement`
   Context: capture durable decisions inline as each step executes.
2. `review` (when needed): run a quality check before commit.
   Context: capture durable risks/follow-ups inline when needed.
3. `commit` (`commit` mode): create atomic commits with user approval.
   Context: capture durable rationale/gotchas inline when needed.
4. `review` (when needed): run a quality check before finalise.
   Context: capture durable risks/follow-ups inline when needed.
5. `commit` (`finalise` mode): prepare tracking updates (archive completed PRD and update `tasks/context.md` when needed).
   Create one pre-merge finalise commit only when tracking changes exist, then merge using the repository-approved strategy and delete the completed feature branch safely.
6. `compact` (periodic): summarise older context entries to keep tracking files easy to scan.
