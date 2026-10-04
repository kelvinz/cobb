# Compact Templates

## Prompt Format for Threshold Choice

Use this short choice prompt before edits:

```text
Proposed compact plan:
- Context detailed entries to keep: <recommended-count> (consolidate: <older-count>)

0 — Recommended: Use the proposed plan — <reason>
1 — Keep a custom number, given as `1 <n>` (for example: `1 20`)
2 — Keep fewer detailed entries
3 — Keep more detailed entries
4 — Stop without editing
```

## Historical Summary Pattern

Use this as a reference pattern when generating historical summaries:

```markdown
## Historical summary
- Earlier phase focused on onboarding, auth hardening, and export reliability.
- Main recurring risk was cross-feature dependency ordering; mitigated by stricter finalise discipline.
- Key tradeoff pattern: shipped simpler defaults first, then expanded configurability.
```
