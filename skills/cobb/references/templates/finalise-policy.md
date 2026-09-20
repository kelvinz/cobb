# Finalise Policy Reference

Use this for strategy selection, preparation, and merge in `references/finalise.md`.

`references/finalise.md` owns the approval, re-review, and merge-readiness checks. This reference supplies the selected strategy's operations.

## Default strategy

Resolve the merge strategy using this priority (highest wins):

1. User explicitly requests a strategy in the current session.
2. Repo-level merge preference declared under Repo conventions in `tasks/context.md`.
3. Default: **merge-commit** (`git merge --no-ff`) to preserve the approved atomic commits and an explicit feature boundary when the repository has no stronger policy.

## Preparation

Complete this on the feature branch before the final review:

1. Refresh remote refs and resolve the confirmed target as a local branch. If its upstream is ahead, fast-forward the target to it as part of the confirmed sync; if diverged, stop for a sync decision. A failed fetch leaves remote freshness unverified and prevents automatic history rewrites or publishing.
2. Pin the target hash as `TARGET_HASH`. For `merge-commit` or `squash`, merge that target into the feature branch only when it is not already an ancestor of HEAD. This prepares the combined content for review without rewriting feature history.
3. For `linear-history` or `rebase`:
   - require the feature-only range to contain no merge commits
   - if the target is already an ancestor of HEAD, skip rebase
   - otherwise read History Rewrite Safety in `references/commit-review.md` and apply it to every commit to be replayed
   - when all checks pass, use `git -c rebase.autoStash=false rebase "$TARGET_HASH"`
   - if the range is shared, published, non-linear, or uncertain, ask for another strategy and recommend `merge-commit` or stop
4. On a merge or rebase conflict, abort that operation and report the conflict for a decision. Preserve the original work; never force-push or discard changes to make preparation succeed.
5. Require a clean feature branch with `TARGET_HASH` as an ancestor. Return to finalise for review. Any later target movement returns here before another review.

## Merge

Run only after preparation, review, and closeout, on the confirmed target branch. No history rewrites occur at this stage.

- merge-commit policy:
  - `git merge --no-ff <feature-branch>`
- linear-history or rebase policy:
  - `git merge --ff-only <feature-branch>`
- squash policy:
  - before changing the target branch, propose the combined change with a full title and body; load the title and standard body rules in `references/templates/commit-rules.md`, not the tracking-only finalise body
  - wait for numbered approval of the scope and message; approval of the strategy alone is not message approval
  - `git merge --squash <feature-branch>`
  - verify the staged change matches the approved scope, then create one commit on the target branch with the approved message; if it differs, stop and re-present the proposal

## Branch deletion safety checks

- require the successful merge and tree check from `references/finalise.md`; a squash uses that recorded result because the original feature commits are not ancestors of the target
- confirm the local feature still points to `DELIVERY_HEAD`; for a remote deletion, refresh and record its tip and require that tip to be an ancestor of `DELIVERY_HEAD`; preserve any ref that changes after inspection or contains unmerged work
- confirm `<feature-branch>` is not the target branch
- confirm `<feature-branch>` is not the default branch
- confirm current HEAD is not `<feature-branch>` when deleting it
- require explicit numbered/coded user confirmation before deleting local or remote branch
- recommend deleting the local branch once it is merged (the work is preserved on the target); recommend keeping the remote branch unless evidence clearly favors removing it
