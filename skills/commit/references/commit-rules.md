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

- Use PRD `Type:` as a hint, but do not override the real diff intent.
- If a commit changes behaviour and internal maintenance together, split and classify each commit separately.
- If uncertain between `feat` and `fix`, prefer `fix` when correcting expected behaviour; otherwise use `feat`.
- If still ambiguous after reviewing diff + context, ask the user before committing.

## Standard body template

Include both a concise change summary and the decision rationale:

- short summary of what changed (2-5 bullets)
- problem context a future reader would not have
- alternatives considered
- trade-offs made
- consequences or side effects worth noting

```text
Summary:
- ...

Why:
- ...

Context:
- ...

Alternatives considered:
- ...

Trade-offs:
- ...

Consequences:
- ...
```

## Finalise body template

For a finalise commit, use this shorter body format:

```text
Finalise:
- f-## <feature name>

Actions:
- archived PRD to `tasks/archive/` (if applicable)
- updated `tasks/memory.md` completed section (if applicable)
```
