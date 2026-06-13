# cobb

A single skill for ongoing product development, split into phases you call as subcommands.

`cobb` routes each request to a phase, then runs that phase under shared guardrails. Everything lives in one skill (`skills/cobb/`) — the phases are reference files loaded on demand, not separate skills.

## Subcommands

- `/cobb` — show the subcommand menu and recommend the next phase based on `tasks/` state (read-only; never runs a phase on its own).
- `/cobb prd` — create, update, or list PRDs (`tasks/f-##-*.md`) with status and priority. Handles project setup (first PRD) and ongoing planning.
- `/cobb design` — optional design router for UI/UX direction, interaction/motion, and static imagery (`ui` / `ux` / `motion` / `imagery` modes). **WIP** — all four modes are still basic and being refined; not yet considered ready.
- `/cobb implement` — implement a PRD in the codebase and check off completed stories/tasks.
- `/cobb review` — strict branch review for correctness, security, tests, and scope, with a clear go/no-go decision.
- `/cobb commit` — propose atomic, user-approved commits (emoji + type + imperative summary). Also `/cobb commit finalise` (merge/branch cleanup) and `/cobb commit hotfix`.
- `/cobb context` — maintain `tasks/context.md` inline or via explicit backfill.
- `/cobb compact` — compact `tasks/context.md` by summarising older entries when it gets noisy.

These phases are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## Recommended workflow: idea → merged

1. `/cobb prd` → `/cobb design` (optional, UI/UX-heavy features) → `/cobb implement`
   Context: capture durable decisions inline as each step executes.
2. `/cobb review` (when needed): quality check before commit.
3. `/cobb commit` (`commit` mode): atomic commits with user approval.
4. `/cobb review` (when needed): quality check before finalise.
5. `/cobb commit finalise`: archive the completed PRD, update `tasks/context.md` if needed, create one pre-merge finalise commit (only when tracking changes exist), then merge using the repo-approved strategy and delete the feature branch safely.
6. `/cobb compact` (periodic): summarise older context entries to keep tracking files easy to scan.

## Files the skill manages

- `tasks/f-##-<slug>.md`
  - One PRD per feature, named with feature ID (e.g. `f-01-invite-teammates.md`).
  - Self-contained spec with `Status:` (draft | ready), `Priority:` (P0–P3), and `Type:` (feat | fix | chore).
  - Tracks progress via checklist items on stories/tasks/acceptance criteria.
  - During finalise, completed PRDs move to `tasks/archive/` (same filename, no rename).

- `tasks/context.md`
  - Project state, key decisions, milestones, and gotchas — written for handoff.

- `tasks/archive/`
  - Archived completed PRDs, moved during `commit` finalise.

## Layout

```
skills/cobb/
  SKILL.md                    # router: dispatch table, shared guardrails, bare-/cobb behaviour
  references/
    prd.md  design.md  implement.md  review.md  commit.md  context.md  compact.md
    design/                   # ui / ux / motion / imagery mode references
    templates/                # PRD, report, context, compact, commit, finalise templates
```
