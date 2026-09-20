# Commit Rules Reference

## Type selection rubric

Choose `type` in this order (first match wins):

1. `fix`:
   - Corrects wrong behaviour vs expected behaviour
   - Resolves a regression, flaky/error path, broken edge case, or failing test tied to a bug
   - Fixes security/privacy behaviour
2. `feat`:
   - Adds new user-visible capability
   - Expands existing behaviour, workflow, API surface, or output contract in a product-facing way
3. `chore`:
   - No product behaviour change
   - Maintenance-only work such as tooling/config cleanup, dependency bumps, refactors that preserve behaviour, test-only scaffolding, or docs-only edits
   - Docs-only changes (README, comments, changelogs) are always `chore`

## Classification rules

- Use PRD `Type:` as a hint; the real diff intent decides.
- If a commit changes behaviour and internal maintenance together, split and classify each commit separately.
- If uncertain between `feat` and `fix`, prefer `fix` when correcting expected behaviour; otherwise use `feat`.
- If still ambiguous after reviewing diff + context, offer the candidate classifications as a choice and wait before committing.

## Title

`<emoji> <type>: <imperative summary>`

- `feat` -> `✨`
- `fix` -> `🐛`
- `chore` -> `🧹`

Use another emoji only when it is more precise. Keep the summary short, specific, and imperative.

## Standard body template

Use these sections in order in both the proposal and the committed body:

- `Summary` (required): what changed, in 1–3 bullets.
- `Why` (required): why the change was needed, including essential problem context. Mention a rejected alternative only when it helps explain the decision.
- `Cause` (required for `fix`, omitted otherwise): the confirmed cause.
- `Notes` (only when applicable): important effects, trade-offs, limitations, compatibility changes, or migration steps.

Use the literal headings below and omit inapplicable sections rather than writing `None`. Keep routine test results in the verification report; include a result here only when it helps explain the change.

```text
Summary:
- What changed.

Why:
- Why this change was needed.

Cause:
- Confirmed cause.

Notes:
- Important effects or limitations.
```

## Finalise body template

For a closeout tracking commit, use this shorter body format and list only actions actually taken. For a partial delivery, add `(partial)` after the feature name and record that the PRD stays active with its open requirement/slice IDs; do not claim it was completed or archived. Merge and push results belong in the finalise report, not this pre-merge message.

```text
Finalise:
- f-## <feature name>

Actions:
- archived PRD to `tasks/archive/` (if applicable)
- updated `tasks/context.md` completed section (if applicable)
```
