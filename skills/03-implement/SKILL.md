---
name: 03-implement
description: "Implement a prd by building the feature in the codebase (`Type: feat` / `fix` / `chore`), updating tests, running checks, and marking the prd as Implemented. Triggers: implement, build, execute, code this feature, run plan, finish implementation."
---

# 03 implement

Implement a feature from a prd.

---

## Guardrails

- Follow the repo's `AGENTS.md` instructions (if present) for any files you touch.
- Keep changes simple and handoff-friendly: assume a junior dev (or another AI) will maintain this later.
- Do not change product scope while executing:
  - If the prd is missing details or ambiguous, stop and use `02-plan` to refine the prd first.
  - If the feature is missing from `tasks/todo.md`, stop and use `01-new` first.
  - If you discover out-of-scope requirements or bugs during execution, do not expand scope—create a new backlog item via `01-new` instead.
- Do not edit `tasks/todo.md` except updating this feature's status indicator from `—` to `🔨` when implementation is complete.
- Do not reset any prd status checkboxes when updating an existing prd.

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
       - If the higher-priority item is unchecked (no prd yet), recommend writing its prd via `02-plan` first.
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
     - Check the dependency prd's `## Execution Status` section.
     - If any dependency is not **Implemented**, recommend executing that dependency prd first.
     - If a dependency has no prd yet, stop and use `02-plan` to create that dependency prd first.

3. **Execute**
   - Implement the feature as specified.
   - Add/update tests as appropriate.
   - Run the project's normal checks (typecheck/lint/tests/build) per `AGENTS.md` or project conventions.

4. **Verify**
   - Verify acceptance criteria and edge cases from the prd.
   - Perform any manual QA steps listed in the prd.

5. **Update status (in-place)**
   - Ensure the prd contains this section (add it if missing):

     ```markdown
     ## Execution Status
     - [ ] Implemented
     - [ ] Reviewed
     - [ ] Merged
     ```

   - Check boxes based on evidence:
     - **Implemented**: code changes complete, tests added/updated and passing, acceptance criteria met locally. Also update the feature's status indicator in `tasks/todo.md` from `—` to `🔨`.
   - If the prd has user-story checklists (e.g., `- [ ] US-001 …` and acceptance-criteria checkboxes), check them off as you complete them. Do not reset existing checkboxes.

6. **Close out**
   - Summarize what was changed and what remains.
   - Next steps:
     - If you want a PR: run `04-propose`, then `05-review`.
     - If you don't want a PR yet: run `05-review` (local), then `06-memory`.

---

## Output

- Update code and tests as needed.
- Update the prd execution status checkboxes in the prd file.
- If you discover a durable decision/gotcha or complete a significant milestone, capture it in `tasks/memory.md` via `06-memory`.
- Reply with:
  - prd path
  - Which execution status boxes were checked
  - Which status indicator was updated in `tasks/todo.md` (if any)
  - Any follow-ups or open issues
