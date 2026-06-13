# Compact Templates

## Prompt Format for Threshold Choice

Use this short choice prompt before edits:

```text
Proposed compact plan:
- Context detailed entries to keep: 15 (consolidate: 41)

Reply with:
- `1` for "use defaults", or
- `2 <n>` for custom number (for example: `2 20`), or
- `3` for "less", `4` for "more".
```

## Historical Summary Pattern

Use this as a reference pattern when generating historical summaries:

```markdown
## Historical summary
- Earlier phase focused on onboarding, auth hardening, and export reliability.
- Main recurring risk was cross-feature dependency ordering; mitigated by stricter finalise discipline.
- Key tradeoff pattern: shipped simpler defaults first, then expanded configurability.
```
