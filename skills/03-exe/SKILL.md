---
name: 03-exe
description: Execute a PRD by implementing the feature in the codebase (`Type: feat` / `fix` / `chore`). Use when given a PRD to build, asked to implement a feature/spec, or moving from planning (02-prd) to execution. Updates the PRD execution status checkboxes (Implemented/Tested/Released) as work progresses.
---

# 03 Exe

Implement a feature from a PRD and keep the PRD’s execution status up to date.

---

## Guardrails

- Follow the repo’s `AGENTS.md` instructions (if present) for any files you touch.
- Keep changes simple and handoff-friendly: assume a junior dev (or another AI) will maintain this later.
- Do not change product scope while executing:
  - If the PRD is missing details or ambiguous, stop and use `02-prd` to refine the PRD first.
  - If the feature is missing from `tasks/todo.md`, stop and use `01-new` first.
- Do not update `tasks/todo.md` during execution; `tasks/todo.md` tracks “PRD exists” (handled by `02-prd`), not build status.
- Do not reset any PRD status checkboxes when updating an existing PRD.

---

## Workflow

1. **Identify the PRD**
   - Ask for the PRD path if not provided (usually `tasks/prd-<slug>.md`).
   - Confirm which feature ID/name this PRD corresponds to.

2. **Pre-flight**
   - Read `AGENTS.md` (if present) and follow it.
   - Check priority (if `tasks/todo.md` exists):
     - Priority is determined by list order.
     - If there are higher-priority items above this feature, ask the user to confirm they want to work on it now (vs a higher-priority item).
       - If the higher-priority item is unchecked (no PRD yet), recommend writing its PRD via `02-prd` first.
   - Create a new feature branch before making changes (unless you are already on an appropriate feature branch):
     - Base it off the default branch (usually `main`) unless the repo has a different branching model.
     - Name it based on the PRD Summary `Type` (or match repo conventions):
       - `Type: fix` → `fix/F-###-<short-slug>`
       - `Type: chore` → `chore/F-###-<short-slug>`
       - default (`Type: feat`) → `feat/F-###-<short-slug>`
   - If `tasks/memory.md` exists, skim key decisions / notes / gotchas relevant to this area before coding.
   - Parse the PRD into an execution plan: user stories, functional requirements, non-goals, risks, rollout, and testing notes.
   - Verify dependencies:
     - Read this PRD’s “Dependencies & Constraints” section for feature dependency IDs.
     - For each dependency ID, locate the dependency’s PRD path from `tasks/todo.md`.
     - Check the dependency PRD’s `## Execution Status (03-exe)` section.
     - If any dependency is not **Implemented**, recommend executing that dependency PRD first.
     - If a dependency has no PRD yet, stop and use `02-prd` to create that dependency PRD first.

3. **Execute**
   - Implement the feature as specified.
   - Add/update tests as appropriate.
   - Run the project’s normal checks (typecheck/lint/tests/build) per `AGENTS.md` or project conventions.

4. **Verify**
   - Verify acceptance criteria and edge cases from the PRD.
   - Perform any manual QA steps listed in the PRD.

5. **Update PRD status (in-place)**
   - Ensure the PRD contains this section (add it if missing):

     ```markdown
     ## Execution Status (03-exe)
     - [ ] Implemented
     - [ ] Tested
     - [ ] Released
     ```

   - Check boxes based on evidence:
     - **Implemented**: code changes complete and acceptance criteria met locally.
     - **Tested**: tests are added/updated and passing (and any required manual QA done).
     - **Released**: only check after release/deploy/merge is completed and confirmed by the user or the repo’s release workflow.
   - If the PRD has user-story checklists (e.g., `- [ ] US-001 …` and acceptance-criteria checkboxes), check them off as you complete them. Do not reset existing checkboxes.

6. **Close out**
   - Summarize what was changed and what remains.
   - Leave **Released** unchecked unless release is actually completed.

---

## Output

- Update code and tests as needed.
- Update the PRD execution status checkboxes in the PRD file.
- If you discover a durable decision/gotcha or complete a significant milestone, capture it in `tasks/memory.md` via `04-rem`.
- Reply with:
  - PRD path
  - Which execution status boxes were checked
  - Any follow-ups or open issues
