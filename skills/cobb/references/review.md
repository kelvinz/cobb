# review

Review one change set and return a decision-led report.

Shared guardrails from the cobb router apply; the rules below are review-specific.

---

## Guardrails

- Review changes made on the currently checked-out branch.
- Be fully read-only. Do not modify code, PRDs, `tasks/context.md`, or any other file.
- Do not commit, merge, push, or delete branches.
- Do not ask the user which branch to check against.
- Resolve the comparison base automatically from a caller-confirmed finalise target, a commit-mode session-start hash for direct default-branch work, or the repository default/base branch.
- Block approval if the current branch is behind the resolved comparison base; require sync + re-review.
- Do not update PRD tracking files here.
- Report proposed durable context updates, but do not apply them.
- Do not invent test results; run checks or call out missing evidence.
- Number every blocker and suggestion in standalone and commit-triggered reports.
- A pass is valid only for the exact reviewed HEAD, comparison-base commit, and clean-worktree state.

---

## Inputs

- current branch (resolved from `git branch --show-current`)
- comparison base (a caller-confirmed finalise target, a commit-mode session-start hash for direct default-branch work, or the default/base branch; do not prompt for it)
- optional PRD path (if scope validation is needed)

---

## Workflow

1. Resolve current branch and comparison base automatically.
   - When invoked during finalise after the user confirms a target, use that target without prompting again.
   - When commit mode supplies a session-start hash for direct default-branch work, use that immutable commit without prompting.
   - Otherwise prefer the repository default branch resolved from `origin/HEAD`.
   - Otherwise use the local default branch (`main`, `master`, or `dev`) when exactly one exists.
   - If the comparison base cannot be resolved, return `Good to commit: No` with the exact commands/data needed to resolve it.
2. Collect context:
   - `git fetch --all --prune` to refresh remote state; if it fails (offline, unreachable remote), continue against local refs and record in the report that remote freshness is unverified
   - `git diff "<comparison-base>...HEAD"`
   - `git log "<comparison-base>..HEAD" --oneline`
   - `git merge-base --is-ancestor "<comparison-base>" HEAD`
   - `git diff --staged`
   - `git diff`
   - `git status --short`
   - Resolve and record the exact `HEAD` and comparison-base commit hashes.
3. Compare the change set against required behaviour:
   - If `git merge-base --is-ancestor "<comparison-base>" HEAD` fails, return `Good to commit: No` and require sync before re-review.
   - correctness and edge cases
   - security risks and data handling
   - test depth and regression risk
   - scope control (especially if PRD path is provided)
     - Compare diff vs PRD 'In scope' and completed user stories; flag any diff not attributable to a PRD requirement.
4. Classify findings:
   - blockers (must fix), numbered `B1`, `B2`, ...
   - suggestions (optional improvements), numbered `S1`, `S2`, ...
   - missing evidence (tests/checks not run, unclear behaviour), numbered `E1`, `E2`, ...
     - If unable to run checks (CI-only, permissions), mark as "Missing evidence".
     - Request a specific artifact: CI link, log, or command the user can run.
     - Treat evidence required by the PRD, repository policy, or changed risk surface as a blocker and cross-reference its `E#` from a `B#`.
     - Treat genuinely optional/manual evidence as a numbered suggestion and cross-reference its `E#` from an `S#`.
5. Produce the report with a clear recommendation:
   - `Good to commit: Yes` only when there are zero blockers, including required-evidence blockers.
   - `Good to commit: No` otherwise.
   - if decision is `No`, include explicit numbered fix items; finalise remains unavailable
6. Identify context-worthy review outcomes without editing files:
   - systemic risks likely to recur
   - key security or data-handling decisions
   - durable follow-up decisions that affect future work
   - list proposed context entries and cross-reference each to a `B#`, `S#`, or `Finalise` candidate
   - if no durable outcome exists, mark context as `none` with reason
7. Emit the review fingerprint:
   - current branch
   - reviewed HEAD hash
   - reviewed comparison-base name and hash
   - `git status --short` result (must be clean for a finalise-valid pass)
   - invalidate the approval after any commit, base movement, or worktree change
8. Load `references/commit-review.md` and present its matching numbered action branch, whether review is standalone or commit-triggered. Remain read-only until the user selects an action; then route to `implement` or `finalise`.

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
