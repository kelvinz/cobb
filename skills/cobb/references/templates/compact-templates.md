# Compact Templates

## Prompt Format for Threshold Choice

Use this short choice prompt before edits:

```text
Proposed compact plan:
- Context detailed entries to keep: <recommended-count> (consolidate: <older-count>)

Reply with:
- `0` **Recommended:** use the proposed plan; it preserves recent operational detail while compacting older history
- `1 <n>`: keep a custom number (for example: `1 20`)
- `2`: keep fewer detailed entries
- `3`: keep more detailed entries
- `4`: stop without editing
```

## Historical Summary Pattern

Use this as a reference pattern when generating historical summaries:

```markdown
## Historical summary
- Earlier phase focused on onboarding, auth hardening, and export reliability.
- Main recurring risk was cross-feature dependency ordering; mitigated by stricter finalise discipline.
- Key tradeoff pattern: shipped simpler defaults first, then expanded configurability.
```
