# Finalise Policy Reference

Use this when `commit` runs in `finalise` mode.

## Preconditions

- feature branch is not default/base
- the review phase already returned `Good to commit: Yes` for the feature code against the target base, before finalise began
- the only change since that review is the finalise closeout commit (`tasks/` tracking files only)
- target branch is user-confirmed
- finalise decision bundle is collected (merge strategy, push/delete choices)

The finalise closeout commit is review-neutral and does not require re-review. A code change, target-base movement, or worktree change since the review does require re-review before merge.

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
