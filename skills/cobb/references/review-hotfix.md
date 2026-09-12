# Staged Hotfix Review

Use only for caller `hotfix`, after `review` refreshes remote refs and pins `HEAD_HASH`. Review the staged change against HEAD, not the branch's committed history. An up-to-date branch with a staged fix is a valid input.

The caller prepares and stages the complete approved hotfix, including tests and tracking changes. Inspection does not change that staging selection.

## Workflow

1. **Check the branch.** Require the caller-confirmed default branch and no merge, rebase, cherry-pick, or unresolved index entries in progress. Record branch kind `base` for this mode. If an upstream exists, pin its name and hash and require it to be an ancestor of `HEAD_HASH`. A branch behind or diverged from its upstream needs sync before review; equality is allowed.
2. **Require a matching worktree.** `git diff --quiet --ignore-submodules=none` must succeed, so tests exercise only the staged hotfix. Report unstaged tracked changes as a blocker and leave them untouched. List untracked files from `git ls-files --others --exclude-standard`; report them as a blocker only when they sit under source or test paths the checks can read.
3. **Pin the staged tree.** Set `STAGED_TREE=$(git write-tree)`. Stop on failure. Compare it with `git rev-parse "${HEAD_HASH}^{tree}"`; equal trees mean there is no hotfix to review.
4. **Inspect the fixed snapshot.** Use `git diff --binary "$HEAD_HASH" "$STAGED_TREE"`. Apply the Compare, Classify, Decide, and Propose context steps of the `references/review.md` Workflow. Run checks on the matching worktree or an isolated copy of this staged tree. Required evidence and all blockers must be resolved for `Good to commit: Yes`.
5. **Recheck before reporting.** The branch name, HEAD hash, staged tree, and upstream name/hash (if present) must still match the recorded values. Repeat the worktree checks from step 2. Any change invalidates this review; take a fresh snapshot and review it before approving.
6. **Return to hotfix mode.** Use `references/templates/report-template.md` with review mode `staged-hotfix`. Record the branch, HEAD, staged tree, upstream or `none`, remote freshness, check results, and `git status --short`. This is approval for one exact pending commit, not permission to finalise or rewrite existing commits. Hotfix mode runs the repair loop in `references/commit-review.md` on this report.

## Commit Check

Immediately before committing, the caller repeats step 5 against this report. After committing, it verifies that the checked-out branch is unchanged, the new commit's parent equals the reviewed HEAD, and its tree equals `STAGED_TREE`.

If a hook or concurrent change makes any comparison fail, invalidate approval and review the actual committed change against its parent. Preserve the work; do not publish or claim a verified hotfix until that review passes.
