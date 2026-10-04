# hotfix

Commit one urgent fix directly to the default branch. Hotfix mode reviews the exact staged change before it commits, instead of reviewing commits afterwards.

Shared guardrails from the cobb router apply. Load `references/commit.md` for its guardrails and its Normal Commit Workflow steps 1–5 (proposal and approval); the rules below are hotfix-specific.

## Workflow

1. Resolve the repository default under the router's shared rule and verify it is the checked-out branch; stop if it is unclear.
2. Prepare one complete hotfix group, including tests and the failure, urgency, rationale, and follow-up in `tasks/context.md`. Use `fix` unless the change is non-behavioural; PRD sync may be `none` with a reason.
3. Use Normal Commit Workflow steps 1–5 for proposal and approval only. Then stage exactly that group. Leave unrelated work untouched; ask for an isolation or defer decision if the worktree cannot match the staged change.
4. Run `review` with caller `hotfix`; it reviews the staged snapshot under Staged Review below. Then load `references/commit-review.md` and run its repair loop as caller `hotfix`, with the Repair Loop Changes below: repairs are restaged, not folded.
5. When that loop completes, identify the user's reply approving the pending group. If approval is missing, return to the proposal/approval steps. Routine in-scope review repairs retain that approval. Commit with the approved message under the Commit Check below.
6. Report the hash and verification result. The verified staged review replaces normal post-commit review; finalise and push remain separate, explicitly requested actions.

## Staged Review

`review` follows this section for caller `hotfix`. Review the staged change against HEAD, not the branch's committed history. An up-to-date branch with a staged fix is a valid input.

Run `scripts/hotfix-check.sh pin <default-branch>` and save its output outside the repository. It refreshes remote refs, pins `HEAD_HASH`, and applies steps 1 to 3 below; judge its `UNTRACKED` lines yourself under step 2.

The caller prepares and stages the complete approved hotfix, including tests and tracking changes. Inspection does not change that staging selection.

1. **Check the branch.** Require the caller-confirmed default branch and no merge, rebase, cherry-pick, or unresolved index entries in progress. Record branch kind `base` for this mode. If an upstream exists, pin its name and hash and require it to be an ancestor of `HEAD_HASH`. A branch behind or diverged from its upstream needs sync before review; equality is allowed.
2. **Require a matching worktree.** `git diff --quiet --ignore-submodules=none` must succeed, so tests exercise only the staged hotfix. Report unstaged tracked changes as a blocker and leave them untouched. List untracked files from `git ls-files --others --exclude-standard`; report them as a blocker only when they sit under source or test paths the checks can read.
3. **Pin the staged tree.** Set `STAGED_TREE=$(git write-tree)`. Stop on failure. Compare it with `git rev-parse "${HEAD_HASH}^{tree}"`; equal trees mean there is no hotfix to review.
4. **Inspect the fixed snapshot.** Use `git diff --binary "$HEAD_HASH" "$STAGED_TREE"`. Apply the Compare, Classify, Decide, and Propose context steps of the `references/review.md` Workflow. Run checks on the matching worktree or an isolated copy of this staged tree. Required evidence and all blockers must be resolved for `Good to commit: Yes`.
5. **Recheck before reporting.** Run `scripts/hotfix-check.sh verify <pin-file>`. The branch name, HEAD hash, staged tree, and upstream name/hash (if present) must still match the recorded values. Repeat the worktree checks from step 2. Any change invalidates this review; take a fresh snapshot and review it before approving.
6. **Return to hotfix mode.** Use `references/templates/report-template.md` with review mode `staged-hotfix`. Record the branch, HEAD, staged tree, upstream or `none`, remote freshness, check results, and `git status --short`. This is approval for one exact pending commit, not permission to finalise or rewrite existing commits. Hotfix mode runs the repair loop in `references/commit-review.md` on this report.

## Repair Loop Changes

Caller `hotfix` runs the repair loop in `references/commit-review.md` with these changes:

- Every repair belongs to the pending commit: skip step 3 (choose each repair's commit) and Commit Folding.
- In step 5, restage the repairs so the index again holds the complete pending change.
- On Completion, return to Workflow step 5 above with the index holding the reviewed tree.

## Commit Check

Immediately before committing, repeat Staged Review step 5 against the report. After committing, run `scripts/hotfix-check.sh commit-check <pin-file>`; it verifies that the checked-out branch is unchanged, the new commit's parent equals the reviewed HEAD, and its tree equals `STAGED_TREE`.

If a hook or concurrent change makes any comparison fail, invalidate approval and review the actual committed change against its parent before claiming success. The commit stays as it is until the user decides. Preserve the work; do not publish or claim a verified hotfix until that review passes.
