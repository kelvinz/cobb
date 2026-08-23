# review

Review one change set and return a decision-led report.

Shared guardrails from the cobb router apply; the rules below are review-specific.

---

## Guardrails

- Review changes made on the currently checked-out branch.
- Be fully read-only. Do not modify code, PRDs, `tasks/context.md`, or any other file.
- Do not commit, merge, push, or delete branches.
- Do not ask the user which branch to check against.
- Resolve the comparison base strictly by the resolution ladder in Workflow step 1; never guess. If no rung resolves clearly, return `Good to commit: No` and require `/cobb review <base-ref>`.
- Pin HEAD and the comparison base to commit hashes before reviewing. Use those hashes for every history comparison.
- The reviewed base is part of the result, not an implementation detail: report it, and expect finalise to re-review when the merge target differs from it.
- Block approval if the current branch is behind the resolved comparison base; require sync + re-review.
- Do not update PRD tracking files here.
- Report proposed durable context updates, but do not apply them.
- Do not invent test results; run checks or call out missing evidence.
- Number every blocker and suggestion in standalone and commit-triggered reports.
- A pass is valid only for the exact reviewed HEAD, comparison-base commit, and clean-worktree state.

---

## Inputs

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
   - Resolve the base in this order:
     1. explicit `/cobb review <base-ref>` argument
     2. caller-confirmed finalise target
     3. direct base-branch commit mode: use the upstream when it exists and differs from `HEAD_HASH`; otherwise use the session-start hash
     4. current branch upstream, when it exists
     5. repository default declared under Repo conventions in `tasks/context.md`
     6. exactly one symbolic remote HEAD target across all remotes
     7. exactly one local branch from the shared base-branch list when no remote default exists
   - If a ref does not resolve to a commit, return `Good to commit: No` and name it.
   - If several remote HEADs disagree, several local base branches remain possible, or no base exists, return `Good to commit: No`. Tell the user to rerun `/cobb review <base-ref>`. Do not guess from timestamps or nearby branch history.
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
4. Compare the change set against required behaviour:
   - correctness and edge cases
   - security risks and data handling
   - test depth and regression risk
   - scope control (especially if PRD path is provided)
     - Compare diff vs PRD 'In scope' and completed user stories; flag any diff not attributable to a PRD requirement.
5. Classify findings:
   - blockers (must fix), numbered `B1`, `B2`, ...
   - suggestions (optional improvements), numbered `S1`, `S2`, ...
   - missing evidence (tests/checks not run, unclear behaviour), numbered `E1`, `E2`, ...
     - If unable to run checks (CI-only, permissions), mark as "Missing evidence".
     - Request a specific artifact: CI link, log, or command the user can run.
     - Treat evidence required by the PRD, repository policy, or changed risk surface as a blocker and cross-reference its `E#` from a `B#`.
     - Treat genuinely optional/manual evidence as a numbered suggestion and cross-reference its `E#` from an `S#`.
6. Produce the report with a clear recommendation:
   - `Good to commit: Yes` only when there are zero blockers, including required-evidence blockers.
   - `Good to commit: No` otherwise.
   - if decision is `No`, include explicit numbered fix items; finalise remains unavailable
7. Identify context-worthy review outcomes without editing files:
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
9. Load `references/commit-review.md` and present its matching numbered action branch, whether review is standalone or commit-triggered. Remain read-only until the user selects an action; then route to `implement` or `finalise`.

---

## Review Checklist

- Correctness:
  - empty/null/error paths
  - boundary values and state transitions
  - ordering/concurrency/time assumptions (if applicable)
- Security:
  - authn/authz behaviour
  - input validation and output encoding
  - secret/PII handling and logging safety
  - dependency risk for newly introduced packages
- Tests and verification:
  - happy path + key failure paths
  - regression coverage in touched areas
  - manual verification steps when automation is missing
- Maintainability:
  - naming clarity and control-flow simplicity
  - comments/docs for non-obvious decisions only

---

## References

- `references/templates/report-template.md`: standard report structure for review outputs.

---

## Output

- Return the review report with explicit proposed context updates and review fingerprint.
- Keep the decision explicit and unambiguous.
- Return control to `references/commit-review.md` instead of printing a generic next command.
- End with the shared status block (Files changed / Key decisions / Next step).
