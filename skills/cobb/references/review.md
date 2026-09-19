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
- A pass is valid only for the recorded review state: the branch fingerprint below, or the staged-hotfix snapshot in `references/review-hotfix.md`.

---

## Inputs

- caller: `standalone` (default), `commit`, `finalise`, or `hotfix`; return to that caller after inspection
- current branch (resolved from `git branch --show-current`)
- optional explicit comparison base argument (`/cobb review <base-ref>`) — wins over automatic resolution without prompting
- otherwise the comparison base resolved by the Workflow step-1 ladder (never prompted for)
- optional PRD path (if scope validation is needed)

---

## Workflow

1. Refresh remote state, then pin HEAD and the comparison base.
   - Run `git fetch --all --prune` first (best-effort); if it fails (offline, unreachable remote), continue against local refs and record in the report that remote freshness is unverified.
   - Resolve `HEAD_HASH=$(git rev-parse HEAD)` first. If HEAD is detached, return `Good to commit: No` and ask the user to check out or create a branch.
   - Classify the current branch as `base` when its name is in the shared base-branch list. Otherwise classify it as `feature`.
   - For caller `hotfix`, load `references/review-hotfix.md`, complete its staged-review workflow, and return to the caller. Skip the remaining branch-only workflow below, including the empty-history-range test.
   - Resolve the base for other callers in this order:
     1. explicit `/cobb review <base-ref>` argument
     2. caller-confirmed finalise target
     3. direct base-branch commit mode: use the upstream when it exists and differs from `HEAD_HASH`; otherwise use the session-start hash
     4. current branch upstream, when it exists
     5. repository default declared under Repo conventions in `tasks/context.md`
     6. exactly one symbolic remote HEAD target across all remotes
     7. exactly one local branch from the shared base-branch list when no remote default exists
   - If a ref does not resolve to a commit, return `Good to commit: No` and name it.
   - If several remote HEADs disagree, several local base branches remain possible, or no base exists, return `Good to commit: No`. Tell the user to rerun `/cobb review <base-ref>`; an explicit ref is the only acceptable resolution here.
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
   - If `HEAD_HASH == BASE_HASH`, the review range is empty. Return `Good to commit: No`. Direct base-branch work needs commit mode when a session-start hash is required. For a fully pushed feature branch, rerun `/cobb review <merge-target>` to review the full branch.
   - If `git merge-base --is-ancestor "$BASE_HASH" "$HEAD_HASH"` fails, return `Good to commit: No` and require sync before re-review.
4. **Compare** the change set against required behaviour:
   - correctness and edge cases
   - security risks and data handling
   - test depth and regression risk
   - spec fidelity, when a PRD is available; quote the PRD line for each finding:
     - requirements or acceptance criteria the PRD asks for that are missing or partial
     - behaviour in the diff that no PRD requirement asked for (scope creep)
     - requirements that look implemented but whose implementation looks wrong
   - standards: repository coding standards where documented, plus the smell baseline in `references/review-smells.md` and the principles in `references/design-principles.md` when the diff changes logic beyond configuration, documentation, or generated output
   - naming: symbols, tests, and messages use the `## Language` section of `tasks/context.md`
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
   - Re-verify before emitting: `git rev-parse HEAD` must still equal `HEAD_HASH`, and `git rev-parse "${BASE_REF}^{commit}"` must still equal `BASE_HASH`. If either moved, rerun from step 1. If the worktree is no longer clean, invalidate a finalise-valid pass.
   - current branch
   - branch kind (`base` or `feature`)
   - reviewed HEAD hash
   - reviewed comparison-base name, resolution source (`argument`, `finalise-target`, `upstream`, `session-start`, `repo-convention`, `remote-head`, or `local-fallback`), and pinned hash
   - `git status --short` result (must be clean for a finalise-valid pass)
   - invalidate the approval after any commit, base movement, or worktree change
9. Return the report to the caller. Called reviews continue through `references/commit-review.md`. Standalone review ends read-only with the report and recommended next action.

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
  - abstractions with one call site, parameters for cases that do not exist, dead code, obsolete compatibility paths
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
  - each test would fail if every imported function returned `undefined` (see the five shapes in `references/tdd.md`)
  - verification reached the matching surface, not only tests; each check is graded `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`, and inconclusive counts as missing evidence
  - manual verification steps when automation is missing
- Maintainability:
  - naming clarity and control-flow simplicity, using the project language
  - smell baseline matches (`references/review-smells.md`), reported as suggestions
  - comments/docs for non-obvious decisions only

---

## References

- Read `references/templates/report-template.md` when producing the report; use its fields for the selected review mode.
- Read `references/review-smells.md` and `references/design-principles.md` in step 4 when the diff changes logic.

---

## Output

- Return the review report with explicit proposed context updates and review fingerprint.
- Keep the decision explicit and unambiguous.
- For a called review, return control and the report to its caller without starting another phase or repair loop.
