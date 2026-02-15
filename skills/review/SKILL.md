---
name: review
description: "Review branch changes against a base branch for correctness, security, tests, and scope, then return a clear go/no-go decision. Triggers: review, readiness check, pre-commit review, pre-finalise review."
---

# review

Review one change set and return a decision-led report.

---

## Guardrails

- Review branch changes against the selected base branch.
- Do not implement or modify code.
- Do not commit, merge, push, or delete branches.
- Do not update PRD tracking files here.
- Update `tasks/memory.md` only for durable review outcomes.
- Examples: recurring risks, release-critical gotchas, or confirmed follow-up decisions.
- Do not invent test results; run checks or call out missing evidence.

---

## Inputs

- base branch (default: repository default branch resolved from `origin/HEAD`; ask if unclear)
- optional PRD path (if scope validation is needed)

---

## Workflow

1. Confirm base branch and scope target.
2. Collect context:
   - `git diff "<base>...HEAD"`
   - `git log "<base>..HEAD" --oneline`
   - `git status --short`
3. Compare the change set against required behaviour:
   - correctness and edge cases
   - security risks and data handling
   - test depth and regression risk
   - scope control (especially if PRD path is provided)
     - Compare diff vs PRD 'In scope' and completed user stories; flag any diff not attributable to a PRD requirement.
4. Classify findings:
   - blockers (must fix)
   - suggestions (optional improvements)
   - missing evidence (tests/checks not run, unclear behaviour)
     - If unable to run checks (CI-only, permissions), mark as "Missing evidence".
     - Request a specific artifact: CI link, log, or command the user can run.
5. Produce the report with a clear recommendation:
   - `Good to commit: Yes` or `Good to commit: No`
   - if decision is `No`, include explicit fix items and ask the user to address them before rerunning `review`
6. Evaluate memory-worthy review outcomes and update `tasks/memory.md` inline when needed:
   - systemic risks likely to recur
   - key security or data-handling decisions
   - durable follow-up decisions that affect future work
   - if no durable outcome exists, mark memory as skipped with reason in the report

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

## Report Template

```text
Review Report
Decision:
- Good to commit: Yes | No

Blockers (must fix):
- …

Suggestions (nice to have):
- …

Missing evidence:
- …

Security notes:
- …

Regression risks / watch-outs:
- …

Memory updates:
- Updated: <summary> | Skipped: <reason>

Recommended next step:
- If Good to commit=No: ask user to fix blockers, then rerun `review`.
- If Good to commit=Yes: run `commit` (`commit` mode for new commits, `finalise` mode when ready to merge).
```

---

## Output

- Return the review report with explicit memory update status.
- Keep the decision explicit and unambiguous.
- End with a short status block:
  - **Files changed**: list of created/updated files
  - **Key decisions**: any assumptions or choices made (if any)
  - **Next step**: recommended next skill or action
