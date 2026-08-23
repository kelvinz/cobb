# implement

Implement a feature from a PRD.

Shared guardrails from the cobb router apply; the rules below are implement-specific.

---

## Guardrails

- Do not change product scope while executing:
  - If the PRD is missing details or ambiguous, stop and use `/cobb prd` to refine the PRD first.
  - If implementation reveals the PRD is incorrect, pause and propose PRD edits via `/cobb prd`.
  - Do not silently deviate.
  - If the feature has no PRD in `tasks/`, stop and use `/cobb prd` first.
  - If you discover out-of-scope requirements or bugs during execution, do not expand scope.
  - Create a new PRD via `/cobb prd` instead.
- Exception for review-selected scope expansion:
  - First transition to `/cobb prd` in update mode.
  - Add the selected suggestion's requirements, acceptance criteria, implementation slice, and verification evidence.
  - Require focused scope confirmation, then resume implementation on the same branch.
- Treat a confirmed `Status: ready` PRD as approval of its interfaces, behaviour priorities, and TDD plan.
- Do not ask for a second implementation-plan or testing-plan approval unless execution reveals a material ambiguity or scope change.
- Do not reset any existing PRD checklist items when updating an existing PRD.
- When implementation yields durable decisions/gotchas, update `tasks/context.md` in this step.
- Use `design` as an optional companion for UI/UX-heavy work:
  - If visual direction, interaction states, or design-token choices are unclear, run `/cobb design` before coding that area.
  - If approved design artifacts already exist, proceed directly with implementation.
- Require user confirmation before creating or switching git branches.
- For each bounded preflight decision, provide numbered options and mark exactly one **Recommended** from repository state. This includes PRD selection, priority overrides, branch creation/switching, dependency overrides, design hand-offs, and review-driven scope expansion.
- Do not commit, merge, push, or delete branches; delegate these to `/cobb commit`.

---

## Workflow

1. **Identify the PRD**
   - If no path is provided, discover active ready PRDs first. If several remain plausible, number them and recommend the highest-priority unblocked PRD; request an open path only when discovery cannot identify candidates.
   - Confirm which feature ID/name this PRD corresponds to.
   - Require `Status: ready`. If it is `draft`, transition to `/cobb prd` and resolve its numbered blockers first.

2. **Preflight**
   - Check priority:
     - Scan active PRD files in `tasks/` for their `Status:` and `Priority:` fields.
     - If higher-priority PRDs with `Status: ready` exist above this feature (P0 > P1 > P2 > P3), ask the user to confirm working on this item now.
       - Number the choices and recommend the higher-priority ready PRD unless a documented dependency or urgency justifies continuing.
     - If a higher-priority PRD is still `Status: draft`, mention it but proceed (it's not ready yet).
    - Create a new feature branch before making changes (unless you are already on an appropriate feature branch):
      - Base it off the repository default branch (resolve via `origin/HEAD` or repo policy).
      - Propose the branch name and base branch, then ask with numbered create/use-current/custom/stop choices; recommend the repository-conforming safe option.
      - Name it based on the PRD Summary `Type` (or match repo conventions):
        - `Type: fix` → `fix/f-##-<short-slug>`
        - `Type: chore` → `chore/f-##-<short-slug>`
        - default (`Type: feat`) → `feat/f-##-<short-slug>`
   - If `tasks/context.md` exists, skim key decisions / notes / gotchas relevant to this area before coding.
   - Parse the PRD into an execution plan.
   - Require traceability from user stories and acceptance criteria to ordered implementation slices and evidence.
   - Include user stories, functional requirements, non-goals, technical design, risks, rollout, rollback, and testing notes.
   - For behavioural `feat` and `fix` work, read `references/tdd.md` and validate the PRD against it.
   - If the PRD lacks an executable TDD plan or justified exception, transition to `/cobb prd` instead of inventing scope during implementation.
    - Decide whether `design` is needed:
      - Trigger it when the PRD adds/changes UI surfaces, interaction/motion behaviour, or design-system patterns, and no approved design direction is available.
      - If `/cobb design` runs, treat its output as implementation constraints and keep PRD scope unchanged.
   - Verify dependencies:
     - Read this PRD's "Dependencies & Constraints" section for feature dependency IDs.
     - For each dependency ID, locate PRD files by feature ID in `tasks/` and `tasks/archive/`.
     - Treat dependencies as complete only when the dependency PRD is archived in `tasks/archive/`.
     - If any dependency is still in `tasks/`, recommend finalising that dependency first.
     - If a dependency has no PRD yet, stop and use `/cobb prd` to create that dependency PRD first.
    - Override: if the user confirms dependencies are satisfied, proceed.
    - Present numbered finalise-dependency/override/stop choices and recommend finalising unresolved dependencies unless repository evidence proves they are already satisfied.
    - Example: dependency work merged but not yet archived.
    - Record the override in `tasks/context.md`.

3. **Execute**
   - Implement the feature as specified.
   - Follow PRD implementation slices in dependency order.
   - For behavioural work with a practical automated harness, execute one vertical RED/GREEN/REFACTOR cycle at a time per `references/tdd.md`, keeping each completed slice together as one future atomic commit group.
   - For UI/UX work, implement against approved design output (states, tokens, layout rules).
   - Run the project's normal checks (typecheck/lint/tests/build) per repo conventions.
   - For an approved TDD exception, execute its repeatable manual verification and preserve the evidence.

4. **Verify**
   - Verify acceptance criteria and edge cases from the PRD.
   - Perform any manual QA steps listed in the PRD.
   - Record evidence against the stable acceptance-criterion and slice IDs.
   - Confirm tests exercise observable behaviour rather than private methods, internal call order, or project-owned collaborator mocks.

5. **Update checklist progress (in-place)**
   - Check off completed user stories/tasks and acceptance criteria in the PRD as implementation progresses.
   - If the PRD lacks checklist items for implementation progress, add a small checklist section and use it.
   - Do not reset existing checked items.

6. **Update context inline when needed**
   - Update `tasks/context.md` when implementation produces durable information:
     - important gotchas or constraints
     - architectural/technical decisions with trade-offs
     - milestone-level completion notes worth preserving

7. **Close out**
   - Summarise what was changed and what remains.
   - Next steps:
     - If unresolved UI/UX direction remains, run `/cobb design` and continue `/cobb implement`.
     - Run `/cobb commit` in `commit` mode; it will run `/cobb review` automatically after all intended groups are committed and the worktree is clean.
     - Once review has passed, run `/cobb commit` in `finalise` mode to archive the PRD and merge; it trusts the completed review rather than re-running one.

---

## Output

- Update code and tests as needed.
- Update PRD story/task checklist progress in the PRD file.
- If you discover a durable decision/gotcha, update `tasks/context.md` in the same run.
- Also update it when you complete a significant milestone.
- Reply with:
  - PRD path
  - Which checklist items were completed
  - Any follow-ups or open issues
  - RED/GREEN/REFACTOR evidence per completed behavioural slice, or the approved exception evidence
- End with the shared status block. If follow-up work requires a user choice, number the options and mark exactly one **Recommended**.
