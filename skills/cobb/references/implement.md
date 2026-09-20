# implement

Implement a feature from a PRD.

Shared guardrails from the cobb router apply; the rules below are implement-specific.

When called by `references/commit-review.md`, use Review-Repair Mode at the end of this file.

---

## Guardrails

- Keep product scope exactly as the PRD states while executing:
  - If the PRD is missing details or ambiguous, stop and use `/cobb prd` to refine the PRD first.
  - If implementation reveals a requirement in the PRD is incorrect, pause and propose PRD edits via `/cobb prd`.
  - Fix a factual error that changes no requirement, such as a wrong command or file path, in place with a one-line note in the PRD.
  - Every requirement deviation is stated and routed through `/cobb prd`.
  - Outside review-repair mode, if the feature has no PRD in `tasks/`, stop and use `/cobb prd` first.
  - Out-of-scope requirements or bugs discovered during execution become a new PRD via `/cobb prd`; the current scope stays fixed.
  - For a fix PRD whose RED test fails to reproduce the bug, the cause is not yet known: load `references/diagnose.md` with caller `implement` and run it, then update the fix PRD via `/cobb prd` from its report (root cause, reproduction, regression seam) and resume the slice.
- For fix work, every shipped line traces to the confirmed cause. A change that "might help" is a hypothesis, not a fix, and code motivated by a refuted hypothesis is reverted. A guard that silences a crash is a symptom fix. Fix the pattern, not the instance: search for siblings of the same shape and cover them in the same slice or a new PRD.
- For a review finding that requires scope expansion, return to the repair loop for the unresolved decision and PRD confirmation before changing that scope.
- Treat a confirmed `Status: ready` PRD as approval of its interfaces, behaviour priorities, and TDD plan.
- Ask for a second implementation-plan or testing-plan approval only when execution reveals a material ambiguity or scope change.
- Follow Progress Updates in `references/templates/prd-template.md`; read it when requirements or prior verification evidence change.
- When implementation yields durable decisions/gotchas, update `tasks/context.md` in this step.
- Use `design` as an optional companion for UI/UX-heavy work, function before form:
  - If the PRD's flow, state inventory, or copy is incomplete, return to `/cobb prd`; these are PRD decisions, not visual direction.
  - If visual direction or design-token choices are unclear, run `/cobb design` before coding that area.
  - If approved design artifacts already exist, proceed directly with implementation.
- Require user confirmation before creating or switching git branches.
- Leave commits, merges, pushes, and branch deletions to `/cobb commit`; return review repairs to the calling loop.
- Name new symbols, tests, and messages with the `## Language` section of `tasks/context.md`.

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
   - For UI work, read the root `DESIGN.md` when it exists and the PRD's visual direction block; the PRD overrides `DESIGN.md` for this feature.
   - Parse the PRD into an execution plan.
   - Require traceability from user stories and acceptance criteria to ordered implementation slices and evidence.
   - Include user stories, functional requirements, non-goals, technical design, risks, rollout, rollback, and testing notes.
   - For behavioural `feat` and `fix` work, read `references/tdd.md` and validate the PRD against it.
   - For a `chore` that restructures code, read the Behaviour-Preserving Changes contract in `references/tdd.md` and require the PRD's behaviour pin, equivalence proof, and reader-load target.
   - If the PRD lacks an executable TDD plan or justified exception, transition to `/cobb prd` instead of inventing scope during implementation.
    - Decide whether `design` is needed:
      - Trigger it when the PRD adds/changes UI surfaces, interaction/motion behaviour, or design-system patterns, and no approved design direction is available.
      - Call `/cobb design` for `direction` only at this stage. Treat its output as implementation constraints and keep PRD scope unchanged; this handoff leaves application code untouched.
   - Verify dependencies:
     - Read feature dependency IDs from the PRD Summary's `Dependencies` field.
     - For each ID, inspect its PRD in the resolved feature base's committed tree, for example with `git show <base-ref>:tasks/archive/<filename>`, not only the current worktree.
     - Require a fully checked archived PRD on that base and its delivered work in the current feature history. Check that the target-side delivery commit is an ancestor of HEAD; for squash delivery, use the squash commit, not the old feature tip. A local archive alone proves neither completion nor merge.
     - If the dependency is unfinished or unmerged, recommend finalising it first. If delivered work is absent from this feature, stop for a sync/base decision. If no PRD exists, use `/cobb prd` first.
     - Offer numbered resolve-dependency/override/stop choices when blocked. An explicit override must name the evidence and any unmet requirement, for example work already merged without its archive; record it in `tasks/context.md`.

3. **Execute**
   - Implement the feature as specified.
   - Follow PRD implementation slices in dependency order, a `prefactor` slice first when the PRD has one.
   - Write tests only at the seams the PRD confirmed: section 9 for behavioural work, or the behaviour pin for a restructuring `chore`.
   - For behavioural work with a practical automated harness, execute one vertical RED/GREEN/REFACTOR cycle at a time per `references/tdd.md`, keeping each completed slice together as one future atomic commit group.
   - For a behaviour-preserving `chore`, capture the pin before any structure moves, keep it green through each step, prove equivalence on the real artifact, and revert the reshape if reader load did not fall.
   - For UI/UX work, make it work before making it look right: build structure, semantics, every state in the inventory, keyboard access, and copy first, then apply the visual layer from `DESIGN.md` and the approved direction.
   - Run the project's normal checks (typecheck/lint/tests/build) per repo conventions.
   - For an approved TDD exception, execute its repeatable manual verification and preserve the evidence.

4. **Verify**
   - Verify acceptance criteria and edge cases from the PRD.
   - Verify on the matching surface, using the verification recipe under Repo conventions in `tasks/context.md` when one exists: a CLI change runs the real command, a UI change walks the changed flow in the running app, a parser or migration replays a saved input, a storage change reads back the written value, a performance change reports one primary number as before and after. Tests show branch behaviour; the surface shows the feature works.
   - For a UI slice, capture and inspect under `references/design/visual-verification.md`, function before form.
   - Perform any manual QA steps listed in the PRD.
   - Grade each check `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`. Inconclusive or wrong-surface is flagged, never counted as a pass.
   - Record evidence against the stable acceptance-criterion and slice IDs.
   - Confirm tests exercise observable behaviour through confirmed seams, take expected values from an independent source, keep project-owned collaborators real, and would fail if every imported function returned `undefined`.

5. **Update checklist progress (in-place)**
   - Check off completed user stories/tasks and acceptance criteria in the PRD as implementation progresses.
   - If the PRD lacks checklist items for implementation progress, add a small checklist section and use it.

6. **Update context inline when needed**
   - Update `tasks/context.md` when implementation produces durable information:
     - important gotchas or constraints
     - architectural/technical decisions with trade-offs
     - milestone-level completion notes worth preserving

7. **Close out**
   - Summarise what was changed and what remains.
   - Next steps:
     - If unresolved UI/UX direction remains, run `/cobb design` and continue `/cobb implement`.
     - Run `/cobb commit` in `commit` mode; it runs review and automatic repairs after all intended groups are committed and the worktree is clean.
     - When the PRD is fully checked and the repair loop has passed, run `/cobb commit finalise` to archive the PRD and merge.

---

## Review-Repair Mode

When called by `references/commit-review.md`, keep the current branch and approved scope. Use Execute, Verify, and the tracking-update steps above, then return the verified changes to that loop. Skip PRD selection, priority/branch prompts, and the normal commit handoff. If no PRD exists for the reviewed work, repair only its established behaviour and use repository tests; a PRD is required only for a material scope change. The repair loop owns decisions and commit folding.

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
