# commit

Create approved atomic commits. Normal mode runs review and automatic repairs after the final clean group; the Dispatch table routes `finalise` to `references/finalise.md` and `hotfix` to Hotfix Mode below.

Shared guardrails from the cobb router apply; the rules below are commit-specific.

Before proposing a commit, load `references/templates/commit-rules.md` for classification, title, and body rules.

## Guardrails

- Require numbered user confirmation for initial commit groups; a batch `approve all` reply confirms the presented groups' intents, titles, and bodies. Invoking `/cobb commit` starts the proposal workflow; it is not approval, even when a proposal is already shown. Permission to edit, upgrade, or document is not permission to commit.
- That initial approval also authorises routine review repairs and safe folding into those commits under `references/commit-review.md`, so a folded commit may contain more than the hunks shown at approval. Those repairs, temporary fixup commits, and safe amendments need no new proposal or confirmation; pause only for that reference's Decisions That Need the User. New follow-up commits use the normal proposal/approval workflow.
- Show files/hunks, intent, tracking updates, title, and body before initial approval or an approval required by a changed scope/history plan.
- Recommend splitting or editing when a group's scope or message is weak.
- Keep commits atomic; if a title needs "and", split the change set.
- One intent per commit; a behavioural change is `feat` or `fix`, never `chore`.
- Determine type from the diff, not branch name, paths, or habit.
- Add AI attribution or `Co-authored-by` only when explicitly requested.
- Normal mode leaves the remote untouched; push belongs to finalise.
- Couple completed PRD checklist and durable context updates to the atomic change that produced them.
- Commit a new PRD file with the first group of its feature, together with that group's checklist ticks.
- Tracking-only catch-up commits outside finalise need explicit approval.
- In normal mode, run review after all intended groups are committed and the worktree is clean. Hotfix mode uses the staged-review sequence below.
- Review approval is tied to the exact recorded state for that review mode.
- In normal mode on a base branch (see the shared list in `SKILL.md`), preserve the session-start HEAD and review `<session-start>..HEAD`; never compare the branch to itself or offer finalise.

## Normal Commit Workflow

1. Record the session-start HEAD, then inspect `git status --short`, staged diff, and unstaged diff. Identify the active PRD when applicable. Retain the original session-start hash when returning from review repairs.
2. Partition changes into atomic groups. Map each group to:
   - completed PRD checklist/story items, or `none` with reason
   - durable context outcomes, or `none` with reason
3. Before presenting each group's proposal, validate its title and body against `references/templates/commit-rules.md`. Present:
   - files and hunks
   - concise change summary
   - evidence-based `feat`/`fix`/`chore` rationale
   - PRD and context updates included
   - full title and body
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
6. Before each initial or follow-up commit, identify the user's reply approving that group's current proposal. If approval is missing or the proposal changed, return to step 3 and wait for approval. Then stage only the approved group, commit with the approved title and body, and report hash/title/summary. In approve-all mode, do this per group in the presented order; if staging drifts from the presented plan (missing files, conflicting hunks, new changes), stop the batch, report the drift, and fall back to one-at-a-time for the remaining groups.
7. Repeat until no intended groups remain.
8. Recheck the worktree:
   - review runs only on a clean worktree; while changes remain:
   - offer:
     - resume proposals for remaining groups — recommended when changes are expected intended work
     - defer them and stop; review has not run
     - show remaining files/hunks for a manual keep/discard decision — recommended when changes are unexpected, ambiguous, or potentially unrelated
   - the user decides what happens to every remaining change
9. When clean, run `review` with caller `commit` automatically without another prompt:
   - on a feature branch, compare against an explicit base, its upstream, or one clear repository default; stop and require `/cobb review <base-ref>` when the base is unclear
   - on a base branch (any ref in the shared base-branch list), compare against the upstream when one exists and sits behind HEAD, since that is what a push publishes; otherwise compare the recorded session-start commit to HEAD. Disable finalise either way.
   - report the reviewed base back to the user; on a pushed branch the base is the upstream, so the pass covers the unpushed delta and finalise will re-review against the merge target
10. Load `references/commit-review.md` and run the automatic repair loop. When already inside that loop, return the review report to it instead of starting another loop.

## Hotfix Mode

Use only for an urgent fix committed directly to the default branch.

1. Resolve the repository default and verify it is the checked-out branch; stop if that choice is unclear.
2. Prepare one complete hotfix group, including tests and the failure, urgency, rationale, and follow-up in `tasks/context.md`. Use `fix` unless the change is non-behavioural; PRD sync may be `none` with a reason.
3. Use Normal Commit Workflow steps 1–5 for proposal and approval only. Then stage exactly that group. Leave unrelated work untouched; ask for an isolation or defer decision if the worktree cannot match the staged change.
4. Run `review` with caller `hotfix`; it loads `references/review-hotfix.md` and reviews the staged snapshot. Then load `references/commit-review.md` and run its repair loop as caller `hotfix`: repairs are restaged, not folded.
5. When that loop completes, identify the user's reply approving the pending group. If approval is missing, return to the proposal/approval steps. Routine in-scope review repairs retain that approval. Repeat the snapshot checks from `references/review-hotfix.md` immediately before committing with the approved message.
6. Apply that reference's Commit Check after committing. If it fails, review the actual committed change against its parent before claiming success; the commit stays as it is until the user decides.
7. Report the hash and verification result. The verified staged review replaces normal post-commit review; finalise and push remain separate, explicitly requested actions.

## Output

For each proposal, provide atomic scope, summary, type rationale, PRD/context sync, title, body, and available actions.

After execution, report the final commit hashes/titles, repairs folded into them, remaining groups, tracking sync, and final review result.
