# finalise

Load this reference only for `commit finalise` or `finalise` mode.

## Guardrails

- Require a clean feature branch, never the default/base branch.
- Collect target, merge strategy, push, local deletion, and remote deletion in one coded decision bundle.
- Mark one evidence-based value **Recommended** for every field and show one **Recommended** complete bundle.
- Treat explicit coded choices as confirmation; ask only for missing or conflicting fields.
- Never assume `main`; resolve repository defaults and policy.
- Sync with the confirmed target before merge.
- Keep closeout tracking in one approved pre-merge commit; do not use it to catch up missed atomic updates without explicit approval.
- Never delete the target, default, or currently checked-out branch.
- Require explicit coded confirmation for push and each deletion.

## Workflow

1. Verify the worktree is clean and HEAD is a feature branch.
2. Resolve the active PRD:
   - prefer the PRD matching the branch feature ID
   - if several candidates exist, number them and recommend the strongest ID/name match
   - request an open-ended path only when repository discovery cannot produce candidates
3. Prepare closeout tracking:
   - move `tasks/f-##-<slug>.md` to the same filename under `tasks/archive/` when not already archived
   - update `tasks/context.md` completed/current-state sections and applicable review-proposed `Finalise` entries
   - stage only those tracking changes
   - propose one `🧹 chore: finalise f-## <short-summary>` commit with the finalise body from `references/templates/commit-rules.md`
   - present numbered commit/edit/skip choices and mark the safe evidence-based choice **Recommended**
   - skip the commit when no tracking change is needed and state why
4. Collect the finalise bundle:
   - target: coded `1A`, `1B`, ...; make the resolved default `1A`, include `1X` for open custom text
   - strategy: `2A` auto, `2B` merge-commit, `2C` linear-history, `2D` squash, `2E` rebase
   - push: `3A` yes, `3B` no
   - delete local: `4A` yes, `4B` no
   - delete remote: `5A` yes, `5B` no
   - show why each recommended value fits repository policy and risk
   - `0`/`default` means the displayed **Recommended** complete bundle, not a hardcoded strategy
5. Refresh review:
   - a tracking commit invalidates any earlier fingerprint
   - if no valid review exists for the exact clean HEAD and confirmed target-base hash, run `review` automatically against that target
   - load `references/commit-review.md` and apply its decision tree
   - after a clean pass and finalise choice, continue here
6. Confirm HEAD is synced with the target; if sync changes HEAD or the target moves, rerun review automatically.
7. Resolve strategy using `references/templates/finalise-policy.md`.
   - when the user chose `auto`, show the resolved strategy and prompt:
     - `0` **Recommended:** confirm the policy-resolved strategy
     - `1`: merge-commit
     - `2`: linear-history
     - `3`: squash
     - `4`: rebase
     - `5`: stop
8. Merge using the confirmed strategy.
9. Push the target only when the bundle confirms push; otherwise state that remote update remains pending.
10. Recheck branch-deletion safety, then apply only the confirmed local/remote deletions.

## Output

Report the tracking commit, review fingerprint, merge result, push result, and branch cleanup. If any action remains, provide numbered next-step choices and mark one **Recommended**.
