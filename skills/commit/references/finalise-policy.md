# Finalise Policy Reference

Use this when `commit` runs in `finalise` mode and local merge is allowed.

## Preconditions

- `review` gate is approved for the selected path:
  - PR path: `review pr` returns `Ready to accept PR: Yes`
  - Local path: `review local` returns `Good to commit: Yes`
- target branch is user-confirmed
- feature branch is not default/base

## Policy-specific local flows

- merge-commit policy:
  - `git merge --no-ff <feature-branch>`
- linear-history policy:
  - rebase feature branch onto target branch if needed
  - `git merge --ff-only <feature-branch>`
- local squash policy:
  - `git merge --squash <feature-branch>`
  - create one approved commit on the target branch
- local rebase policy:
  - rebase feature commits onto the target branch
  - fast-forward merge
- PR-only policy:
  - do not merge locally
  - use PR path and repository UI strategy

## Branch deletion safety checks

- confirm `<feature-branch>` is not the target branch
- confirm `<feature-branch>` is not the default branch
- confirm current HEAD is not `<feature-branch>` when deleting it
- require explicit user confirmation before deleting local or remote branch
