# Compact Templates

## Prompt Format for Threshold Choice

Use this short choice prompt before edits:

```text
Proposed compact plan:
- Context detailed entries to keep: <recommended-count> (consolidate: <older-count>)

Choices (shared numbered format; the proposed plan is the recommendation):
- use the proposed plan
- keep a custom number, given as `<option> <n>` (for example: `1 20`)
- keep fewer detailed entries
- keep more detailed entries
- stop without editing
```

## Historical Summary Pattern

Use this as a reference pattern when generating historical summaries:

```markdown
## Historical summary
- Earlier phase focused on onboarding, auth hardening, and export reliability.
- Main recurring risk was cross-feature dependency ordering; mitigated by stricter finalise discipline.
- Key tradeoff pattern: shipped simpler defaults first, then expanded configurability.
```
