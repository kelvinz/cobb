# commit

Create approved atomic commits. Normal mode runs review automatically after the final clean group; finalise and hotfix use conditional workflows.

The default delivery order is `implement -> commit -> review -> finalise`.

## Mode Loading

- `commit`: use this file, then load `references/commit-review.md` only after review returns.
- `finalise` / `commit finalise`: load `references/finalise.md`; do not load normal commit workflow sections unnecessarily.
- `hotfix` / `commit hotfix`: use Hotfix Mode below.

For commit classification and bodies, load `references/templates/commit-rules.md` before the first proposal or when classification is ambiguous.

## Guardrails

- Require numbered user confirmation before every commit; a batch `approve all` reply confirms exactly the presented groups with their shown titles and bodies.
- Show files/hunks, intent, tracking updates, title, and body before approval.
- Render exactly one commit action as option `0` **Recommended** from diff quality. Recommend `split` or `edit`, not `commit`, when atomicity or message quality is weak.
- Keep commits atomic; if a title needs "and", split the change set.
- Never mix unrelated intents or use `chore` for behavioural changes.
- Determine type from the diff, not branch name, paths, or habit.
- Never add AI attribution or `Co-authored-by` unless explicitly requested.
- Never push in normal mode.
- Couple completed PRD checklist and durable context updates to the atomic change that produced them.
- Do not create trailing tracking-only catch-up commits outside finalise unless explicitly approved.
- Run review automatically only after all intended groups are committed and the worktree is clean.
- Review approval is valid only for its exact clean HEAD and comparison-base fingerprint.
- On direct default-branch work, preserve the session-start HEAD and review `<session-start>..HEAD`; never compare the default branch to itself or offer finalise.

## Message Rules

Title:

`<emoji> <type>: <imperative summary>`

- `feat` -> `✨`
- `fix` -> `🐛`
- `chore` -> `🧹`

Use another emoji only when it is more precise. Keep the summary short, specific, and imperative.

## Normal Commit Workflow

1. Record the session-start HEAD, then inspect `git status --short`, staged diff, and unstaged diff. Identify the active PRD when applicable.
2. Partition changes into atomic groups. Map each group to:
   - completed PRD checklist/story items, or `none` with reason
   - durable context outcomes, or `none` with reason
3. Present each group's proposal:
   - files and hunks
   - concise change summary
   - evidence-based `feat`/`fix`/`chore` rationale
   - PRD and context updates included
   - full title and body
   - single group: show it and use the per-group actions in step 5
   - multiple groups: show the full plan (every group's proposal, in commit order), then choose the approval mode in step 4
4. With multiple groups, prompt for the approval mode. Render the evidence-based choice as `0` **Recommended** — approve all only when every group is atomic with an accurate message, otherwise the action that fixes the weakest group — and the remaining actions once each as `1..N`:
   - approve all — commit every group sequentially as shown, with no further prompts
   - go one group at a time using the per-group actions below
   - edit a group's scope/message and re-present the plan
   - split a group and re-present the plan
   - stop and leave everything uncommitted
5. Per-group actions (single group, or one-at-a-time mode). Render the evidence-based action as `0` **Recommended** with a short reason and the remaining actions once each as `1..N`:
   - commit this group
   - edit scope/message and repropose
   - skip and leave uncommitted
   - split into smaller groups and repropose
6. On approval, stage only the approved group, commit immediately, and report hash/title/summary. In approve-all mode, do this per group in the presented order; if staging drifts from the presented plan (missing files, conflicting hunks, new changes), stop the batch, report the drift, and fall back to one-at-a-time for the remaining groups.
7. Repeat until no intended groups remain.
8. Recheck the worktree:
   - if changes remain, do not review
   - prompt, rendering the recommended action as `0` and the remaining actions once each as `1..N`:
     - resume proposals for remaining groups — recommended when changes are expected intended work
     - defer them and stop; review has not run
     - show remaining files/hunks for a manual keep/discard decision — recommended when changes are unexpected, ambiguous, or potentially unrelated
   - never discard automatically
9. When clean, run `review` automatically without another prompt:
   - on a feature branch, compare against the resolved default/base branch
   - on the default branch, compare the recorded session-start commit to HEAD and disable finalise
10. Load `references/commit-review.md` and execute the branch matching the review result.

## Hotfix Mode

Use only for an urgent fix committed directly to the default branch.

1. Verify HEAD is the default branch.
2. Run `review` before committing; post-commit branch comparison cannot review a default-branch hotfix meaningfully.
3. Require `Good to commit: Yes` for the exact staged/unstaged hotfix state.
4. Follow Normal Commit Workflow steps 1-7.
   - use `fix` unless the change is genuinely non-behavioural
   - PRD sync is usually `none` with reason
5. Record the failure, urgency, rationale, and follow-up in `tasks/context.md` within the hotfix commit.
6. Do not run normal post-commit review or finalise; the hotfix is already on the default branch.

## Output

For each proposal, provide atomic scope, summary, type rationale, PRD/context sync, title, body, and numbered actions with the recommended action as `0`.

After execution, report commit hash/title, remaining groups, tracking sync, and automatic review result. End with the shared status block and numbered next steps when a user decision remains.
