# finalise

Load this reference only for `commit finalise` or `finalise` mode.

Shared guardrails from the cobb router apply; the rules below are finalise-specific.

Finalise follows the completed automatic review-repair loop in `references/commit-review.md`. When finalise itself needs a review, pass caller `finalise` and route the report through that loop, then resume the pending step rather than restarting finalise.

## Guardrails

- Require a clean feature branch, never the default/base branch, with no merge, rebase, cherry-pick, or unresolved index entries in progress.
- **Re-review rule (canonical).** Require a fresh review after code repairs or history rewrites during preparation, when no valid review exists, when the confirmed delivery scope or target differs from the review, or when the target advances. The approved tracking-only closeout commit and the merge/push/delete choices alone never trigger re-review. The final merge or squash needs no further review only when its tree matches the prepared delivery tree (step 7).
- Collect target, merge strategy, push, local deletion, and remote deletion as one decision bundle using the router's shared Choices rule.
- Treat selection of a fully displayed bundle as confirmation of its fields; ask only for missing or conflicting fields.
- Resolve the target from repository defaults and policy; `main` is one candidate, never an assumption.
- Default push to **no**; the recommended bundle always leaves the remote untouched.
- Keep closeout tracking (`tasks/` files only) in one approved pre-merge commit; catching up missed atomic updates there needs explicit approval.
- The target, default, and currently checked-out branches are protected from deletion.
- Require explicit confirmation for push and each deletion, either through the displayed bundle or a field choice.

## Workflow

1. Check the guardrails and record the feature branch and starting HEAD. Resolve the target before running a new review; a fully pushed branch must be reviewed against the merge target, not its equal upstream.
2. Resolve the PRD and delivery scope:
   - prefer the PRD matching the branch feature ID; include `tasks/archive/` when resuming an existing closeout
   - if several candidates exist, number them and recommend the strongest ID/name match; request a path only when discovery cannot identify one
   - full delivery requires every story, acceptance criterion, and task to be checked with valid evidence
   - when items remain open, list them and recommend `/cobb implement`; proceed only if the user confirms a partial delivery with explicit included and deferred requirement/slice IDs
   - a partial delivery must work safely on its own; confirmation does not waive blockers, required evidence, or dependencies of the included work
3. Collect the finalise bundle using the shared Choices rule:
   - state the merge danger first, from PRD section 10 and the branch diff: `Door: one-way | two-way` with why, and `Blast radius: <one phrase>`; a one-way door raises the recommendation to stop and confirm the rollback steps before merging
   - propose all five fields explicitly: resolved target branch, strategy `auto`, push no, delete local yes when safe, delete remote no
   - adjust the proposal to repository policy and safety, and give a brief reason
   - offer approve displayed bundle / change fields / stop; recommend approval only when every field is resolved and safe
   - for changes, ask about each selected field using the shared Choices rule, then show the revised complete bundle and request approval
4. Prepare the feature branch using `references/templates/finalise-policy.md`:
   - resolve `auto` and state its policy rationale without another strategy prompt; ask only when the policy is conflicting
   - refresh and pin the confirmed target, then perform any required sync or safe rebase under that policy's Preparation rules
   - finish all history rewrites here, before review; a conflict or unsafe rewrite needs a decision, not an automatic force-push
5. Review the prepared feature:
   - reuse a completed review-repair result only when the canonical rule allows it; otherwise load `references/review.md` with caller `finalise`, the confirmed target, and the delivery scope from step 2
   - if the target moved or the report requires sync, return to step 4 before code repairs; an unresolved scope change returns to step 2
   - pass each new usable review report through `references/commit-review.md`; resume here with the completed loop result, preserving the bundle and any existing closeout
   - continue only when that loop's Completion criteria hold
6. Prepare the closeout tracking commit:
   - recheck PRD progress; if the confirmed delivery scope no longer fits, return to step 2; archive only a fully completed PRD, at the same filename under `tasks/archive/`; `Status` remains `draft | ready`, not `done`
   - for a confirmed partial delivery, retain or restore the PRD in active `tasks/`, preserve open checkboxes, and record included/deferred IDs in `tasks/context.md`; do not mark the feature complete
   - update applicable review-proposed `Finalise` entries; describe completion or pending delivery accurately, without claiming a merge or push has already happened
   - load `references/templates/commit-rules.md`; propose one `🧹 chore: finalise f-## <short-summary>` commit with the full tracking diff and its Finalise body
   - present numbered commit/edit/stop choices and wait for approval; on stop, preserve the edits and end finalise
   - stage and commit only the approved tracking changes; verify the actual committed diff matches the proposal before using the tracking-only re-review exception
   - skip this commit when no tracking change is needed; reuse an existing valid closeout rather than creating it again
7. Merge using the policy's Merge rules:
   - require the recorded feature branch checked out with a clean worktree and unchanged HEAD since review plus only the verified closeout; stop on unexpected feature changes
   - require the target hash to equal the reviewed base; if it moved or is now behind/diverged from its refreshed upstream, return to step 4
   - record the final feature HEAD and its tree as `DELIVERY_HEAD` and `DELIVERY_TREE`; require the target to be an ancestor of `DELIVERY_HEAD`
   - obtain any required squash-message approval, check out the confirmed target, recheck its hash, and merge without another rebase
   - verify the target's resulting tree equals `DELIVERY_TREE`; a hook or concurrent change that breaks this check stops push and deletion until investigated and reviewed
8. Push the target only when the bundle confirms push; otherwise state that remote update remains pending. Stop if the target changed since the verified merge.
9. Recheck branch-deletion safety under the policy, then apply only the confirmed local/remote deletions. A failed or unverified merge leaves the feature branch intact.

## Output

Report the delivery scope and remaining PRD items, merge danger (door and blast radius), closeout commit, review the merge relied on, verified merge result, push result, and branch cleanup.
