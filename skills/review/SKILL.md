---
name: review
description: "Run a strict review in exactly one mode: GitHub PR (`pr`) or local diff (`local`). Use when validating correctness, security, tests, and scope before merge or commit. Output a mode-specific decision report: `Ready to accept PR` (pr mode) or `Good to commit` (local mode), and require fixes when the decision is `No`."
---

# review

Review one change set in one mode and return a decision-only report.

---

## Guardrails

- Require an explicit mode: `pr` or `local`.
- Do not implement or modify code.
- Do not commit, merge, push, or delete branches.
- Do not update PRD/todo/memory tracking files here.
- Do not invent test results; run checks or call out missing evidence.

---

## Inputs

- review mode:
  - `pr`: PR URL/number (preferred)
  - `local`: base branch (default: `main`)
- optional prd path (if scope validation is needed)

---

## Workflow

1. Confirm mode and target.
2. Collect context:
   - `pr` mode:
     - `gh pr view --json url,number,title,body,state,isDraft,baseRefName,headRefName,files,additions,deletions`
     - `gh pr diff`
     - `gh pr checks`
   - `local` mode:
     - `git diff "<base>...HEAD"`
     - `git log "<base>..HEAD" --oneline`
     - `git status --short`
3. Compare the change set against required behaviour:
   - correctness and edge cases
   - security risks and data handling
   - test depth and regression risk
   - scope control (especially if prd path is provided)
4. Classify findings:
   - blockers (must fix)
   - suggestions (optional improvements)
   - missing evidence (tests/checks not run, unclear behaviour)
5. Produce the report with a clear recommendation:
   - `pr` mode: `Ready to accept PR: Yes` or `Ready to accept PR: No`
   - `local` mode: `Good to commit: Yes` or `Good to commit: No`
   - if decision is `No`, include explicit fix items and ask the user to address them before rerunning `review` in the same mode

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
PR Mode Report
Mode: pr
Decision:
- Ready to accept PR: Yes | No

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

Recommended next step:
- If Ready to accept PR=No: ask user to fix blockers, then rerun `review` in `pr` mode.
- If Ready to accept PR=Yes: run `commit` in `finalise` mode.
```

```text
Local Mode Report
Mode: local
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

Recommended next step:
- If Good to commit=No: ask user to fix blockers, then rerun `review` in `local` mode.
- If Good to commit=Yes: run `commit` in `commit` mode.
```

---

## Output

- Return only the review report.
- Keep the decision explicit and unambiguous.
