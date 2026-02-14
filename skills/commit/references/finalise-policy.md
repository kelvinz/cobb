# Finalise Policy Reference

Use this when `commit` runs in `finalise` mode.

## Preconditions

- `review` returns `Good to commit: Yes`
- target branch is user-confirmed
- feature branch is not default/base

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
- require explicit user confirmation before deleting local or remote branch
