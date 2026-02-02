---
name: 03-exe
description: "Execute a prd by implementing the feature in the codebase (`Type: feat` / `fix` / `chore`). Also use after merging a PR to mark the prd as merged. Triggers: implement, execute, build this feature, run prd, mark as merged, pr merged, complete merge."
---

# 03 exe

Implement a feature from a prd, or mark a prd as merged after PR completion.

This skill handles two modes:
- **Implement mode**: Build the feature from the prd specification.
- **Merge mode**: After a PR is merged, update status and rename the prd.

---

## Guardrails

- Follow the repo's `AGENTS.md` instructions (if present) for any files you touch.
- Keep changes simple and handoff-friendly: assume a junior dev (or another AI) will maintain this later.
- Do not change product scope while executing:
  - If the prd is missing details or ambiguous, stop and use `02-prd` to refine the prd first.
  - If the feature is missing from `tasks/todo.md`, stop and use `01-new` first.
  - If you discover out-of-scope requirements or bugs during execution, do not expand scope—create a new backlog item via `01-new` instead.
- Do not update `tasks/todo.md` during execution; `tasks/todo.md` tracks "prd exists" (handled by `02-prd`), not build status.
- Do not reset any prd status checkboxes when updating an existing prd.

---

## Workflow

1. **Identify the prd and mode**
   - Ask for the prd path if not provided (usually `tasks/f-##-<slug>.md`).
   - Confirm which feature ID/name this prd corresponds to.
   - Determine the mode:
     - If the user says "mark as merged", "pr merged", or similar → **Merge mode** (skip to step 5).
     - Otherwise → **Implement mode** (continue to step 2).

2. **Pre-flight** (Implement mode only)
   - Read `AGENTS.md` (if present) and follow it.
   - Check priority (if `tasks/todo.md` exists):
     - Priority is determined by list order.
     - If there are higher-priority items above this feature, ask the user to confirm they want to work on it now (vs a higher-priority item).
       - If the higher-priority item is unchecked (no prd yet), recommend writing its prd via `02-prd` first.
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
     - Check the dependency prd's `## Execution Status (03-exe)` section.
     - If any dependency is not **Implemented**, recommend executing that dependency prd first.
     - If a dependency has no prd yet, stop and use `02-prd` to create that dependency prd first.

3. **Execute** (Implement mode only)
   - Implement the feature as specified.
   - Add/update tests as appropriate.
   - Run the project's normal checks (typecheck/lint/tests/build) per `AGENTS.md` or project conventions.

4. **Verify** (Implement mode only)
   - Verify acceptance criteria and edge cases from the prd.
   - Perform any manual QA steps listed in the prd.

5. **Update prd status (in-place)** (Both modes)
   - Ensure the prd contains this section (add it if missing):

     ```markdown
     ## Execution Status (03-exe)
     - [ ] Implemented
     - [ ] Merged
     ```

   - Check boxes based on evidence:
     - **Implemented**: code changes complete, tests added/updated and passing, acceptance criteria met locally. Also update the feature's status indicator in `tasks/todo.md` from `—` to `🔨`.
     - **Merged**: only check after PR is merged to main (confirmed by user or repo workflow). When checking this box:
       1. Rename the prd file with a `done-` prefix (e.g., `f-01-invite-teammates.md` → `done-f-01-invite-teammates.md`).
       2. Update the `prd:` link in `tasks/todo.md` to the new path.
       3. Update the feature's status indicator in `tasks/todo.md` from `🔨` to `✅`.
   - If the prd has user-story checklists (e.g., `- [ ] US-001 …` and acceptance-criteria checkboxes), check them off as you complete them. Do not reset existing checkboxes.

6. **Close out**
   - Summarize what was changed and what remains.
   - Leave **Merged** unchecked unless merge is actually completed.
   - When you check **Implemented** or **Merged**, prompt `04-rem` to update "Current state" and "Completed" sections in `tasks/memory.md`.

---

## Output

- Update code and tests as needed.
- Update the prd execution status checkboxes in the prd file.
- If you discover a durable decision/gotcha or complete a significant milestone, capture it in `tasks/memory.md` via `04-rem`.
- Reply with:
  - prd path
  - Which execution status boxes were checked
  - Which status indicator was updated in `tasks/todo.md` (if any)
  - Any follow-ups or open issues
