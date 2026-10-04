# commit

Create approved atomic commits. Normal mode runs review and automatic repairs after the final clean group; the Dispatch table routes `finalise` to `references/finalise.md` and `hotfix` to `references/hotfix.md`.

Shared guardrails from the cobb router apply; the rules below are commit-specific.

Before proposing a commit, load `references/templates/commit-rules.md` for classification, title, and body rules.

## Guardrails

- Require numbered user confirmation for initial commit groups; a batch `approve all` reply confirms the presented groups' intents, titles, and bodies. Invoking `/cobb commit` starts the proposal workflow; it is not approval, even when a proposal is already shown. Permission to edit, upgrade, or document is not permission to commit.
- That initial approval also authorises routine review repairs and safe folding into those commits under `references/commit-review.md`, so a folded commit may contain more than the hunks shown at approval. Those repairs, temporary fixup commits, and safe amendments need no new proposal or confirmation; pause only for that reference's Decisions That Need the User. New follow-up commits use the normal proposal/approval workflow.
- Show the full proposal under Output before initial approval or an approval required by a changed scope/history plan.
- Recommend splitting or editing when a group's scope or message is weak.
- Keep commits atomic; if a title needs "and", split the change set.
- One intent per commit; a behavioural change is `feat` or `fix`, never `chore`.
- Determine type from the diff, not branch name, paths, or habit.
- Add AI attribution or `Co-authored-by` only when explicitly requested.
- Normal mode leaves the remote untouched; push belongs to finalise.
- Couple completed PRD checklist and durable context updates to the atomic change that produced them.
- Commit a new PRD file with the first group of its feature, together with that group's checklist ticks.
- Tracking-only catch-up commits outside finalise need explicit approval.
- In normal mode, run review after all intended groups are committed and the worktree is clean.
- Review approval is tied to the exact recorded state for that review mode.
- On a base branch, preserve the session-start HEAD for review's fallback. Finalise is unavailable.

## Normal Commit Workflow

1. Record the session-start HEAD, then inspect `git status --short`, staged diff, and unstaged diff. Identify the active PRD when applicable. Retain the original session-start hash when returning from review repairs.
2. If the worktree is clean and no new groups remain, continue at step 9 to review the existing commits; a clean worktree is not a reason to skip review and repairs. Otherwise partition changes into atomic groups. Map each group to:
   - completed PRD checklist/story items, or `none` with reason
   - durable context outcomes, or `none` with reason
3. Before presenting each group's proposal, validate its title and body against `references/templates/commit-rules.md`. Present proposals under Output:
   - single group: show it and use the per-group actions in step 5
   - multiple groups: show the full plan (every group's proposal, in commit order), then choose the approval mode in step 4
4. With multiple groups, offer these approval modes. Recommend approve-all only when every group is atomic with an accurate message; otherwise recommend fixing the weakest group:
   - approve all — commit every group sequentially as shown, with no further prompts
   - go one group at a time using the per-group actions below
   - edit a group's scope/message and re-present the plan
   - split a group and re-present the plan
   - stop and leave everything uncommitted
5. Offer these per-group actions for a single group or one-at-a-time mode:
   - commit this group
   - edit scope/message and repropose
   - skip and leave uncommitted
   - split into smaller groups and repropose
6. Before each initial or follow-up commit, identify the user's reply approving that group's current proposal. If approval is missing or the proposal changed, return to step 3 and wait for approval. Then stage only the approved group, commit with the approved title and body, and report it under Output. In approve-all mode, do this per group in the presented order; if staging drifts from the presented plan (missing files, conflicting hunks, new changes), stop the batch, report the drift, and fall back to one-at-a-time for the remaining groups.
7. Repeat until no intended groups remain.
8. Recheck the worktree:
   - review runs only on a clean worktree; while changes remain:
   - offer:
     - resume proposals for remaining groups — recommended when changes are expected intended work
     - defer them and stop; review has not run
     - show remaining files/hunks for a manual keep/discard decision — recommended when changes are unexpected, ambiguous, or potentially unrelated
   - the user decides what happens to every remaining change
9. When clean, run `review` with caller `commit` automatically:
   - use the base-resolution ladder in `references/review.md` Workflow step 1; pass the recorded session-start hash for its base-branch fallback
   - report the reviewed base back to the user; on a pushed branch the base is the upstream, so the pass covers the unpushed delta and finalise will re-review against the merge target
10. Load `references/commit-review.md` and run the automatic repair loop. When already inside that loop, return the review report to it instead of starting another loop.

## Output

- Each proposal shows its files and hunks, a concise change summary, the evidence-based `feat`/`fix`/`chore` rationale, the PRD and context updates included, the full title and body, and the available actions.
- After each commit, report its hash, title, and summary.
- After execution, report the final commit hashes and titles, the repairs folded into them, any remaining groups, the tracking sync, and the final review result.
