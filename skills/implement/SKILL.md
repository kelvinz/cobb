---
name: implement
description: "Implement a prd by building the feature in the codebase (`Type: feat` / `fix` / `chore`), updating tests, running checks, and checking off completed prd stories/tasks. Triggers: implement, build, execute, code this feature, run plan, finish implementation."
---

# implement

Implement a feature from a prd.

---

## Guardrails

- Follow the repo's `AGENTS.md` instructions (if present) for any files you touch.
- Keep changes simple and handoff-friendly: assume a junior dev (or another AI) will maintain this later.
- Do not change product scope while executing:
  - If the prd is missing details or ambiguous, stop and use `plan` to refine the prd first.
  - If the feature is missing from `tasks/todo.md`, stop and use `new` first.
  - If you discover out-of-scope requirements or bugs during execution, do not expand scope—create a new backlog item via `new` instead.
- Do not edit `tasks/todo.md` in this skill.
- Do not reset any existing prd checklist items when updating an existing prd.

---

## Workflow

1. **Identify the prd**
   - Ask for the prd path if not provided (usually `tasks/f-##-<slug>.md`).
   - Confirm which feature ID/name this prd corresponds to.

2. **Pre-flight**
   - Read `AGENTS.md` (if present) and follow it.
   - Check priority (if `tasks/todo.md` exists):
     - Priority is determined by list order.
     - If there are higher-priority items above this feature, ask the user to confirm they want to work on it now (vs a higher-priority item).
       - If the higher-priority item is unchecked (no prd yet), recommend writing its prd via `plan` first.
   - Create a new feature branch before making changes (unless you are already on an appropriate feature branch):
     - Base it off the default branch (usually `main`) unless the repo has a different branching model.
     - Name it based on the prd Summary `Type` (or match repo conventions):
       - `Type: fix` → `fix/f-##-<short-slug>`
       - `Type: chore` → `chore/f-##-<short-slug>`
       - default (`Type: feat`) → `feat/f-##-<short-slug>`
   - If `tasks/memory.md` exists, skim key decisions / notes / gotchas relevant to this area before coding.
   - Parse the prd into an execution plan: user stories, functional requirements, non-goals, risks, rollout, and testing notes.
   - Verify dependencies:
     - Read this prd's "Dependencies & Constraints" section for feature dependency IDs.
     - For each dependency ID, locate the dependency's prd path from `tasks/todo.md` (or search `tasks/` by ID if missing).
     - Treat dependencies as complete only when their prd path is already in `done-f-##-<slug>.md` form.
     - If any dependency is not yet `done-`, recommend finalising that dependency first.
     - If a dependency has no prd yet, stop and use `plan` to create that dependency prd first.

3. **Execute**
   - Implement the feature as specified.
   - Add/update tests as appropriate.
   - Run the project's normal checks (typecheck/lint/tests/build) per `AGENTS.md` or project conventions.

4. **Verify**
   - Verify acceptance criteria and edge cases from the prd.
   - Perform any manual QA steps listed in the prd.

5. **Update checklist progress (in-place)**
   - Check off completed user stories/tasks and acceptance criteria in the prd as implementation progresses.
   - If the prd lacks checklist items for implementation progress, add a small checklist section and use it.
   - Do not reset existing checked items.

6. **Close out**
   - Summarise what was changed and what remains.
   - Next steps:
     - PR flow: run `review` (local) when needed, then `commit`, then `open-pr`, then run `review` (PR mode) when needed, then `commit` (finalise mode), then `memory`.
     - Local flow: run `review` (local) when needed, then `commit`, then `memory`.

---

## Output

- Update code and tests as needed.
- Update prd story/task checklist progress in the prd file.
- If you discover a durable decision/gotcha or complete a significant milestone, capture it in `tasks/memory.md` via `memory`.
- Reply with:
  - prd path
  - Which checklist items were completed
  - Any follow-ups or open issues
