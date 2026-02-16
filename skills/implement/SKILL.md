---
name: implement
description: "Implement an existing PRD (`Type: feat`/`fix`/`chore`), update tests/checks, and mark completed PRD checklist items. Triggers: implement prd, build feature from prd, execute prd checklist."
---

# implement

Implement a feature from a PRD.

---

## Guardrails

- Follow the repo's `AGENTS.md` instructions (if present) for any files you touch.
- Keep changes simple and handoff-friendly: assume a junior dev (or another AI) will maintain this later.
- Do not change product scope while executing:
  - If the PRD is missing details or ambiguous, stop and use `prd` to refine the PRD first.
  - If implementation reveals the PRD is incorrect, pause and propose PRD edits via `prd`.
  - Do not silently deviate.
  - If the feature has no PRD in `tasks/`, stop and use `prd` first.
  - If you discover out-of-scope requirements or bugs during execution, do not expand scope.
  - Create a new PRD via `prd` instead.
- Do not reset any existing PRD checklist items when updating an existing PRD.
- Treat memory capture as built-in.
- When implementation yields durable decisions/gotchas, update `tasks/memory.md` in this step.
- Use `design` as an optional companion for UI/UX-heavy work:
  - If visual direction, interaction states, or design-token choices are unclear, run `design` before coding that area.
  - If approved design artifacts already exist, proceed directly with implementation.
- Require user confirmation before creating or switching git branches.
- When requesting user decisions or confirmations, use numbered short-reply options (for example: `1`, `2`, `3`).
- Do not commit, merge, push, or delete branches; delegate these to `commit`.
- Do not claim tests passed or checks succeeded without actually running them; if you didn't run it, say so.

---

## Workflow

1. **Identify the PRD**
   - Ask for the PRD path if not provided (usually `tasks/f-##-<slug>.md`).
   - Confirm which feature ID/name this PRD corresponds to.

2. **Preflight**
   - Read `AGENTS.md` (if present) and follow it.
   - Check priority:
     - Scan active PRD files in `tasks/` for their `Status:` and `Priority:` fields.
     - If higher-priority PRDs with `Status: ready` exist above this feature (P0 > P1 > P2 > P3), ask the user to confirm working on this item now.
     - If a higher-priority PRD is still `Status: draft`, mention it but proceed (it's not ready yet).
   - Create a new feature branch before making changes (unless you are already on an appropriate feature branch):
    - Base it off the repository default branch (resolve via `origin/HEAD` or repo policy).
    - Propose the branch name and base branch, then ask the user to confirm before creating it.
     - Name it based on the PRD Summary `Type` (or match repo conventions):
       - `Type: fix` → `fix/f-##-<short-slug>`
       - `Type: chore` → `chore/f-##-<short-slug>`
       - default (`Type: feat`) → `feat/f-##-<short-slug>`
   - If `tasks/memory.md` exists, skim key decisions / notes / gotchas relevant to this area before coding.
   - Parse the PRD into an execution plan.
   - Include user stories, functional requirements, non-goals, risks, rollout, and testing notes.
   - Decide whether `design` is needed:
    - Trigger it when the PRD adds/changes UI surfaces, interaction/motion behaviour, or design-system patterns.
    - Also require that no approved design direction is available.
     - If `design` runs, treat its output as implementation constraints and keep PRD scope unchanged.
   - Verify dependencies:
     - Read this PRD's "Dependencies & Constraints" section for feature dependency IDs.
     - For each dependency ID, locate PRD files by feature ID in `tasks/` and `tasks/archive/`.
     - Treat dependencies as complete only when the dependency PRD is archived in `tasks/archive/`.
     - If any dependency is still in `tasks/`, recommend finalising that dependency first.
     - If a dependency has no PRD yet, stop and use `prd` to create that dependency PRD first.
    - Override: if the user confirms dependencies are satisfied, proceed.
    - Example: dependency work merged but not yet archived.
    - Record the override in `tasks/memory.md`.

3. **Execute**
   - Implement the feature as specified.
   - Implement in small checkpoints aligned to PRD user stories to enable atomic commits.
   - For UI/UX work, implement against approved design output (states, tokens, layout rules).
   - Avoid ad-hoc style drift.
   - Add/update tests as appropriate.
   - Run the project's normal checks (typecheck/lint/tests/build) per `AGENTS.md` or project conventions.

4. **Verify**
   - Verify acceptance criteria and edge cases from the PRD.
   - Perform any manual QA steps listed in the PRD.

5. **Update checklist progress (in-place)**
   - Check off completed user stories/tasks and acceptance criteria in the PRD as implementation progresses.
   - If the PRD lacks checklist items for implementation progress, add a small checklist section and use it.
   - Do not reset existing checked items.

6. **Update memory inline when needed**
   - Update `tasks/memory.md` when implementation produces durable information:
     - important gotchas or constraints
     - architectural/technical decisions with trade-offs
     - milestone-level completion notes worth preserving

7. **Close out**
   - Summarise what was changed and what remains.
   - Next steps:
     - If unresolved UI/UX direction remains, run `design` and continue `implement`.
     - Run `review` when needed, then `commit` in `commit` mode.
     - When the feature is ready to merge, run `review` when needed, then `commit` in `finalise` mode.

---

## Output

- Update code and tests as needed.
- Update PRD story/task checklist progress in the PRD file.
- If you discover a durable decision/gotcha, update `tasks/memory.md` in the same run.
- Also update it when you complete a significant milestone.
- Reply with:
  - PRD path
  - Which checklist items were completed
  - Any follow-ups or open issues
- End with a short status block:
  - **Files changed**: list of created/updated files
  - **Key decisions**: any assumptions or choices made (if any)
  - **Next step**: recommended next skill or action
