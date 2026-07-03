# Post-Commit Review Actions

Load this reference only after normal commit mode or finalise receives a review result.

## Failed Review

When `Good to commit: No`:

1. Number blockers `B1..BN`; finalise is unavailable.
2. Prompt:
   - `0` **Recommended:** fix all blockers; required evidence counts as a blocker
   - `1..N`: fix selected blockers; accept multi-select replies such as `1 3`
   - `N+1`: stop without finalising
3. Route selected work to `implement` in the same session.
4. Update the PRD first when a fix changes approved requirements or scope.
5. Apply still-valid proposed context updates through implementation.
6. Return to approved atomic commits and automatic re-review when clean.

## Passed Review With Suggestions

When `Good to commit: Yes` and `S1..SN` exist:

1. Show each suggestion's scope classification.
2. Prompt:
   - `1..N`: implement selected suggestions; accept multi-select replies
   - `N+1`: implement all suggestions
   - `N+2`: proceed to finalise without optional suggestions on a feature branch, or conclude review on the default branch
   - `N+3`: stop without finalising
   - mark one **Recommended reply** with reasoning (`0` selects it): `N+2` when suggestions are genuinely optional, or the numbered selection that materially reduces security, correctness, data-loss, or near-term operational risk
3. For an out-of-scope selection, route first to `prd` update mode and add requirements, acceptance criteria, implementation slices, and verification evidence.
4. Require numbered confirmation of the expanded scope, then route to `implement` in the same session.
5. Return to approved atomic commits and automatic re-review when clean.

## Clean Review

When `Good to commit: Yes` and suggestions are empty on a feature branch, prompt:

- `0` **Recommended:** enter finalise now
- `1`: stop without finalising

Entering finalise never bypasses merge, push, or deletion confirmations.

On direct default-branch work, report the clean review as complete and do not offer finalise.
