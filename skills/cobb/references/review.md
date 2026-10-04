# review

Inspect one change set without changing it. Standalone review returns a report; normal commit and finalise use that report in the automatic repair loop.

Shared guardrails from the cobb router apply; the rules below are review-specific.

## Guardrails

- Review changes made on the currently checked-out branch.
- Keep source files, task records, and staging choices unchanged. Git metadata refreshes/snapshots and isolated test outputs are allowed. Run checks that would edit tracked files in a disposable copy, or report the missing evidence.
- Leave commits, merges, pushes, and branch deletions to the calling phase.
- Resolve the comparison base from the ladder alone; the user is never asked which branch to check against.
- For branch review, resolve the comparison base by the ladder in Workflow step 1. If it is unclear, return `Good to commit: No` and require `/cobb review <base-ref>`.
- Pin the reviewed revisions before inspecting content. Use those hashes for every comparison.
- The reviewed base is part of the result, not an implementation detail: report it, and expect finalise to re-review when the merge target differs from it.
- Block approval if the current branch is behind the resolved comparison base; require sync + re-review.
- Report proposed durable context updates for the caller to apply.
- Number every blocker and suggestion in standalone and called reports.
- A pass is valid only for the recorded review state: the branch fingerprint below, or the staged-hotfix snapshot under Staged Review in `references/hotfix.md`.

---

## Inputs

- caller: `standalone` (default), `commit`, `finalise`, or `hotfix`; return to that caller after inspection
- current branch (resolved from `git branch --show-current`)
- optional explicit comparison base argument (`/cobb review <base-ref>`) — wins over automatic resolution without prompting
- otherwise the comparison base resolved by the Workflow step-1 ladder (never prompted for)
- optional PRD path (if scope validation is needed)
- optional caller-confirmed delivery scope from `finalise`: PRD feature ID and included/deferred requirement and slice IDs; inspect the entire diff for correctness and safety even for partial delivery

---

## Workflow

1. Refresh remote state, then pin HEAD and the comparison base.
   - For caller `hotfix`, follow Staged Review in `references/hotfix.md`, then return to the caller. Skip the remaining branch-only workflow below, including the empty-history-range test.
   - For other callers, run `scripts/review-pin.sh pin` and save its output outside the repository. Pass `--arg` for an explicit base argument, `--target` for a confirmed finalise target, and `--session-start` in direct base-branch commit mode; pass `--declared` and `--base` for the default base and extra base branches under Repo conventions in `tasks/context.md`. It applies the rules below and prints the results as `KEY=value` facts.
   - Run `git fetch --all --prune` first (best-effort); if it fails (offline, unreachable remote), continue against local refs and record in the report that remote freshness is unverified.
   - Record `BRANCH_NAME=$(git branch --show-current)` and `HEAD_HASH=$(git rev-parse HEAD)` first. If HEAD is detached, return `Good to commit: No` and ask the user to check out or create a branch.
   - Classify the current branch as `base` when its name is in the shared base-branch list. Otherwise classify it as `feature`.
   - Resolve the base in this order:
     1. explicit `/cobb review <base-ref>` argument
     2. caller-confirmed finalise target
     3. direct base-branch commit mode: use the upstream when it exists and differs from `HEAD_HASH`; otherwise use the session-start hash
     4. current branch upstream, when it exists
     5. the repository default under the router's shared rule; record its source as `repo-convention`, `remote-head`, or `local-fallback`
   - If a ref does not resolve to a commit (`ERROR=`), return `Good to commit: No` and name it.
   - If the repository default is unclear or no base exists (`UNCLEAR=`), return `Good to commit: No`. Tell the user to rerun `/cobb review <base-ref>`; an explicit ref is the only acceptable resolution here.
   - Pin `BASE_HASH=$(git rev-parse --verify "${BASE_REF}^{commit}")`. Record the base ref, source, hash, and branch kind.
2. Collect context against the pinned hashes:
   - `git diff "$BASE_HASH...$HEAD_HASH"`
   - `git log "$BASE_HASH..$HEAD_HASH" --oneline`
   - `git merge-base "$BASE_HASH" "$HEAD_HASH"` (record the effective three-dot merge base)
   - `git merge-base --is-ancestor "$BASE_HASH" "$HEAD_HASH"`
   - `git diff --staged`
   - `git diff`
   - `git status --short`
3. Validate the commit pair before reviewing content:
   - If `HEAD_HASH == BASE_HASH` (`RANGE_EMPTY=yes`), the review range is empty. Return `Good to commit: No`. Direct base-branch work needs commit mode when a session-start hash is required. For a fully pushed feature branch, rerun `/cobb review <merge-target>` to review the full branch.
   - If `git merge-base --is-ancestor "$BASE_HASH" "$HEAD_HASH"` fails (`BASE_IS_ANCESTOR=no`), return `Good to commit: No` and require sync before re-review.
   - Inspect source and run checks against `HEAD_HASH`, not local edits. Use the current worktree only when it is clean, its tracked contents match that hash, and unrelated untracked/ignored files cannot affect the checks. Otherwise use an isolated checkout at `HEAD_HASH`, without copying local source edits into it, and remove it before you report. Keep the user's index and files untouched.
   - Record the verification checkout and revision. If isolation is unavailable, inspect with pinned Git reads and report unrun checks as missing evidence; results from a dirty worktree are not evidence for the committed change. A called repair/finalise flow still requires a matching clean original worktree before it can act.
4. **Compare** the change set against required behaviour:
   - correctness and edge cases
   - security risks and data handling
   - test depth and regression risk
   - changed checks, exceptions, and standards: apply Quality gates in the Review Checklist below
   - operational-diagnosis requirements or deployment-stage data/consumer compatibility: read `references/production.md` and check the applicable contract and evidence against the pinned source, read-only
   - spec fidelity, when a PRD is available; record the reviewed requirement/slice IDs and quote the PRD line for each finding:
     - check the caller-confirmed delivery scope, or otherwise the implemented/claimed stories and checked slices; untouched, unchecked future slices do not block an incremental commit
     - report missing or partial behaviour required by that scope, including its dependencies, safety requirements, and required evidence
     - for a confirmed partial finalise, leave excluded unfinished items open; partial approval is not permission to ship a broken included path or ignore a blocker
     - behaviour in the diff that no PRD requirement asked for (scope creep)
     - requirements that look implemented but whose implementation looks wrong
   - standards: repository coding standards where documented, plus the smell baseline in `references/review-smells.md` and the principles in `references/design-principles.md` when the diff changes logic beyond configuration, documentation, or generated output
   - naming: symbols, tests, and messages use the `## Language` section of `tasks/context.md`
   - user-facing surfaces, when the diff changes UI, judged function before form: captures under `references/design/visual-verification.md` are required evidence when the PRD has a user-facing surface, and review may capture them itself when it can run the app without editing tracked files. Changes to the protected items under Extend, Refine, and Redesign in `references/design.md` need a PRD requirement.
   - trust-sensitive flows, with or without UI: each gets the dark-pattern check in `references/design/ethics.md`, and a Critical match is a blocker.
   - Redact secrets from any command output or artifact quoted in the report.
5. **Classify** findings:
   - blockers (must fix), numbered `B1`, `B2`, ...
   - suggestions (non-blocking improvements), numbered `S1`, `S2`, ...
   - missing evidence (tests/checks not run, unclear behaviour), numbered `E1`, `E2`, ...
     - If unable to run checks (CI-only, permissions), mark as "Missing evidence".
     - Request a specific artifact: CI link, log, or command the user can run.
     - Treat evidence required by the PRD, repository policy, or changed risk surface as a blocker and cross-reference its `E#` from a `B#`.
     - Treat genuinely optional/manual evidence as a numbered suggestion and cross-reference its `E#` from an `S#`.
   - For each finding, state the evidence, concrete repair, and whether a user decision is needed. Identify the actual unresolved choice; routine corrections and clear in-scope improvements do not need selection or approval.
   - A finding needs a reachable execution path (a `file:line` and the call chain that reaches it) or a run that shows it; a hypothetical ("what if this is null") with no reachable path is dismissed. Trace the call site before flagging. A preference ("I would have done it differently") with no concrete problem is not a finding. A security finding shows the input path to the sink. List each dismissed candidate with a one-line reason under Dismissed so the user can override; a review whose candidates are all nits is reporting that the code is fine.
   - Account for every changed file in the reviewed diff: list each one under Coverage with its finding IDs, `dismissed`, or `clean`. A file that is not listed has not been reviewed.
6. **Decide** with a clear recommendation:
   - `Good to commit: Yes` only when there are zero blockers, including required-evidence blockers.
   - `Good to commit: No` otherwise.
   - if decision is `No`, include explicit numbered fix items; finalise remains unavailable
7. **Propose context** entries without editing files:
   - systemic risks likely to recur
   - key security or data-handling decisions
   - durable follow-up decisions that affect future work
   - list proposed context entries and cross-reference each to a `B#`, `S#`, or `Finalise` candidate
   - if no durable outcome exists, mark context as `none` with reason
8. Emit the review fingerprint:
   - Re-verify before emitting with `scripts/review-pin.sh verify <pin-file>`: the current branch must still equal `BRANCH_NAME`, `git rev-parse HEAD` must still equal `HEAD_HASH`, and `git rev-parse "${BASE_REF}^{commit}"` must still equal `BASE_HASH`. If any changed, rerun from step 1. Verify the check environment still represents the pinned source; unexpected source changes invalidate its results. A dirty original worktree prevents a finalise-valid pass even when isolated checks passed.
   - current branch
   - reviewed scope (PRD feature ID and requirement/slice IDs, with confirmed partial-delivery exclusions if any)
   - verification checkout and revision for each check, or missing evidence
   - branch kind (`base` or `feature`)
   - reviewed HEAD hash
   - reviewed comparison-base name, resolution source (`argument`, `finalise-target`, `upstream`, `session-start`, `repo-convention`, `remote-head`, or `local-fallback`), and pinned hash
   - `git status --short` result (must be clean for a finalise-valid pass)
   - invalidate the approval after any scope, branch, commit, base, or worktree change; finalise alone may apply its verified tracking-only closeout exception
9. Report under Output.

---

## Review Checklist

- Correctness:
  - empty/null/error paths
  - boundary values and state transitions
  - ordering/concurrency/time assumptions (if applicable)
  - idempotency: what happens if the operation runs twice, or the previous run crashed halfway
  - shared mutable state: is access separated or serialised structurally, or by convention
- Root cause versus symptom (read callers, callees, and types beyond the diff):
  - guard clauses that mask an invariant violation; retries that hide a broken contract; casts that silence a modelling error
  - a fix in one module that belongs in another module's contract
  - an instruction or comment ("do not call this twice") where a type, lint, or runtime check would make the wrong thing impossible
- Structure (`references/design-principles.md`):
  - validation at the boundary once, trusted types inside
  - the data shape matches the access pattern; new branches on an existing if-else chain or a second boolean kept in sync are a modelling gap
  - bolted-on versus integrated: would the code look like this if the requirement had been known from the start
  - legacy dual paths: a new API beside the old one with no external consumer
- Complexity budget:
  - abstractions that add reader load without meaning or a boundary, parameters for cases that do not exist, dead code, obsolete compatibility paths
  - simple code is not penalised for lacking abstraction; duplication beats a premature abstraction
- Security:
  - authn/authz behaviour
  - input validation and output encoding
  - secret/PII handling and logging safety
  - dependency risk for newly introduced packages
- Tests and verification:
  - happy path + key failure paths
  - regression coverage in touched areas
  - tests cross confirmed seams and take expected values from an independent source (no tautological assertions, no mocks of project-owned collaborators)
  - when assessing test quality, read and apply the Fault check in `references/tdd.md`
  - verification reached the matching surface, not only tests; each check is graded `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`, and inconclusive counts as missing evidence
  - manual verification steps when automation is missing
- Quality gates:
  - Inspect skipped or removed tests/assertions, new type/lint/coverage/mutation/security suppressions, lowered budgets or severities, broader exclusions, checks removed from CI, and changed exceptions or standards.
  - Read the original and replacement checks and repository policy. Name the concrete protection lost and the change's reason; removal alone is a candidate, not proof of a defect.
  - An unauthorised loss of required protection is a blocker. Dismiss an equivalent replacement or approved exception with evidence. Return an unresolved required exception to the user as a specific decision, not an assumed approval.
  - For measured budgets, use the project's accepted baseline, workload, and comparison method. Changed measurement conditions are `INCONCLUSIVE`; report the missing comparison. Keep recorded baselines and targets unchanged unless their change is approved, and use existing tooling.
- Maintainability:
  - naming clarity and control-flow simplicity, using the project language
  - smell baseline matches (`references/review-smells.md`), reported as suggestions
  - hand-built UI primitives where an accessible component is installed or belongs: toasts, dialogs and dropdowns with manual focus trapping, command menus, numbers animated by re-rendering text, very long lists without virtualisation, and drag and drop without a keyboard alternative
  - comments/docs for non-obvious decisions only

---

## Output

Write the report with `references/templates/report-template.md`, using the fields for the review mode, including the proposed context updates and the review fingerprint. Keep the decision explicit and unambiguous.

- Called review: return the report and control to the caller, whose repair loop in `references/commit-review.md` continues from it. Start no other phase or repair loop.
- Standalone review: end read-only with the report and the recommended next action.
