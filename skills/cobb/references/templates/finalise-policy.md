# Finalise Policy Reference

Use this when `commit` runs in `finalise` mode.

## Preconditions

- `review` returns `Good to commit: Yes` for the exact clean HEAD and target-base commit fingerprint
- finalise decision bundle is collected (target branch, merge strategy, push/delete choices)
- target branch is user-confirmed
- feature branch is not default/base

Any commit, target-base movement, or worktree change invalidates the review gate and requires automatic re-review before merge.

## Default strategy

Resolve the merge strategy using this priority (highest wins):

1. User explicitly requests a strategy in the current session.
2. Repo-level merge preference declared in `tasks/context.md`.
3. Default: **merge-commit** (`git merge --no-ff`) to preserve the approved atomic commits and an explicit feature boundary when the repository has no stronger policy.

## Policy-specific merge flows

- merge-commit policy:
  - `git merge --no-ff <feature-branch>`
- linear-history policy:
  - rebase feature branch onto target branch if needed
  - `git merge --ff-only <feature-branch>`
- squash policy:
  - `git merge --squash <feature-branch>`
  - create one approved commit on the target branch
- rebase policy:
  - rebase feature commits onto the target branch
  - fast-forward merge

## Branch deletion safety checks

- confirm `<feature-branch>` is not the target branch
- confirm `<feature-branch>` is not the default branch
- confirm current HEAD is not `<feature-branch>` when deleting it
- require explicit numbered/coded user confirmation before deleting local or remote branch; mark the safer evidence-based choice **Recommended**
