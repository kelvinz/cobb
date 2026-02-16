# Review Report Template

Use this template for the final review output.

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

Context updates:
- Updated: <summary> | Skipped: <reason>

Recommended next step:
- If Good to commit=No: ask user to fix blockers, then rerun `review`.
- If Good to commit=Yes: run `commit` (`commit` mode for new commits, `finalise` mode when ready to merge).
```
