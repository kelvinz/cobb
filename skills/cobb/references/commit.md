# commit

Create approved atomic commits. Normal mode runs review automatically after the final clean group; finalise and hotfix use conditional workflows.

The default delivery order is `implement -> commit -> review -> finalise`.

## Mode Loading

- `commit`: use this file, then load `references/commit-review.md` only after review returns.
- `finalise` / `commit finalise`: load `references/finalise.md`; do not load normal commit workflow sections unnecessarily.
- `hotfix` / `commit hotfix`: use Hotfix Mode below.

For commit classification and bodies, load `references/templates/commit-rules.md` before the first proposal or when classification is ambiguous.

## Guardrails

- Require numbered user confirmation before every commit.
- Show files/hunks, intent, tracking updates, title, and body before approval.
- Mark exactly one commit action **Recommended** from diff quality. Recommend `split` or `edit`, not `commit`, when atomicity or message quality is weak.
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
3. Propose the next group:
   - files and hunks
   - concise change summary
   - evidence-based `feat`/`fix`/`chore` rationale
   - PRD and context updates included
   - full title and body
4. Prompt with numbered actions:
   - `1`: commit this group
   - `2`: edit scope/message and repropose
   - `3`: skip and leave uncommitted
   - `4`: split into smaller groups and repropose
   - mark exactly one **Recommended** with a short reason
5. On commit approval, stage only that group, commit immediately, and report hash/title/summary.
6. Repeat until no intended groups remain.
7. Recheck the worktree:
   - if changes remain, do not review
   - prompt:
     - `0`: resume proposals for remaining groups
     - `1`: defer them and stop; review has not run
     - `2`: show remaining files/hunks for a manual keep/discard decision
   - mark `0` **Recommended** when changes are expected intended work; mark `2` **Recommended** when they are unexpected, ambiguous, or potentially unrelated
   - never discard automatically
8. When clean, run `review` automatically without another prompt:
   - on a feature branch, compare against the resolved default/base branch
   - on the default branch, compare the recorded session-start commit to HEAD and disable finalise
9. Load `references/commit-review.md` and execute the branch matching the review result.

## Hotfix Mode

Use only for an urgent fix committed directly to the default branch.

1. Verify HEAD is the default branch.
2. Run `review` before committing; post-commit branch comparison cannot review a default-branch hotfix meaningfully.
3. Require `Good to commit: Yes` for the exact staged/unstaged hotfix state.
4. Follow Normal Commit Workflow steps 1-6.
   - use `fix` unless the change is genuinely non-behavioural
   - PRD sync is usually `none` with reason
5. Record the failure, urgency, rationale, and follow-up in `tasks/context.md` within the hotfix commit.
6. Do not run normal post-commit review or finalise; the hotfix is already on the default branch.

## Output

For each proposal, provide atomic scope, summary, type rationale, PRD/context sync, title, body, and numbered actions with one **Recommended** choice.

After execution, report commit hash/title, remaining groups, tracking sync, and automatic review result. End with the shared status block and numbered next steps when a user decision remains.
