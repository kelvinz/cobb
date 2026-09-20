# Automatic Review Repairs

Load this reference after normal `commit`, `finalise`, or `hotfix` receives a review report. The review itself stays read-only; this calling workflow owns the repairs and commit updates. An explicit review-only request takes precedence.

Fix blockers and suggestions automatically when the solution is clear and within the approved scope. **Process suggestions-only reports too, even when `Good to commit: Yes`.** A useful suggestion is work to complete, not an opt-in task. Routine repairs and safe local commit updates need no further approval; ask only for the decisions listed below.

Normal `commit` and `finalise` fold each repair into its original commit where safe. `hotfix` restages repairs into its single pending commit and skips Commit Folding.

## Decisions That Need the User

Ask only when proceeding requires:

- a product, scope, public-interface, security, cost, or irreversible-data decision not already settled
- resolving conflicting requirements or obtaining required evidence/access that is unavailable
- handling unrelated user changes or choosing a commit for a repair with no clear home
- changing the history plan because the folding safety checks below fail

Use the shared numbered-choice format for that decision. For scope changes, confirm the affected PRD requirements through `prd` before implementation. A blocker cannot be deferred to obtain a passing review; a non-blocking suggestion may be deferred only by an explicit user decision.

## Loop Bound

Repair every finding, including findings a later review raises against your own repairs. Run at most three repair passes. If findings remain after the third pass, pause and report them with the evidence gathered and the decision or input needed.

## Repair Loop

1. **Check the starting state.** Require a usable review report for the current branch, HEAD, and comparison base or staged tree, with a matching worktree. If the reviewed state changed, refresh the review before editing. If the base is unresolved or unrelated work is present, pause for that issue instead of inventing a code fix.
2. **Account for every finding.** Check each `B#`, `S#`, and linked `E#` against the code and requirements. Run available missing checks. Close disproved, duplicate, or already-resolved findings with evidence. Plan repairs under Loop Bound; identify only the decisions that actually need the user. If no repairs remain, go to Completion; first refresh the report if new evidence changes its verdict.
3. **Choose each repair's commit.** Use the reviewed diff and history to find the commit whose intent covers the repair. Check the full rewrite range under Commit Folding before making changes. Resolve any scope or history decision first. `hotfix` skips this step; every repair belongs to the pending commit.
4. **Repair and verify.** Follow `references/implement.md` in review-repair mode on the same branch. Include tests, applicable PRD evidence, and durable context/README updates with the repair that caused them. Complete the relevant deterministic checks before folding or restaging.
5. **Fold or restage the repairs.** Normal `commit` and `finalise` follow Commit Folding below and preserve separate commit intents rather than adding every repair to the latest commit. `hotfix` restages the repairs so the index again holds the complete pending change.
6. **Review the result.** Run `review` again with the same comparison-base argument and caller; retain a confirmed finalise target or direct-base session-start hash. Let review refresh and pin the base again. Replace the old review record with the new one and repeat this loop under Loop Bound. If a completed pass makes no progress on the same findings, pause with the failed evidence and the specific decision or input needed.

## Commit Folding

Before rewriting history, record the original HEAD for recovery and the repair-to-commit mapping, then prove the range is private. The range is every commit from the oldest repair target through HEAD, because rewriting an earlier commit also rewrites its descendants.

- The current branch is a feature branch, and `git fetch --all --prune` succeeded in this pass or `git remote` lists no remotes. A failed fetch is not proof that commits are unpublished.
- For every commit in the range, `git branch -a --contains <hash>` lists only the current branch and `git tag --contains <hash>` lists nothing.
- The range is linear: `git rev-list --merges <oldest-target>^..HEAD` prints nothing, and `<oldest-target>^` resolves.
- Every commit in the range belongs to the reviewed work.

If any check fails, ask for a different plan and recommend approved atomic follow-up commits. Never force-push or discard work to make folding possible.

For an eligible range:

1. Stage only the verified repair hunks and their related tests/tracking updates.
2. For a repair to the latest commit, record the staged tree with `git write-tree`, then use `git commit --amend --no-edit`.
3. For earlier commits, create one `git commit --fixup=<target-hash>` per repair group. Once all groups are committed and the worktree is clean, record the repaired tree with `git rev-parse 'HEAD^{tree}'`, then run `GIT_SEQUENCE_EDITOR=true GIT_EDITOR=true git -c rebase.autoStash=false rebase -i --autosquash <oldest-target>^`.
4. Preserve each commit's original intent and message; revise a message only when needed to describe its repaired contents accurately. For a revised message, load the title and standard body rules in `references/templates/commit-rules.md`. A clear in-scope message correction needs no new approval. Leave temporary `fixup!` messages in Git's format; they disappear during autosquash. If a repair depends on later work and cannot fit its proposed commit, regroup it or ask for a follow-up commit rather than leaving an intermediate commit broken.
5. Confirm the folded tree equals the verified repaired tree from before folding, all intended changes remain, and no temporary fixup commits remain. Run relevant checks for each rewritten commit and the normal checks on the final result.
6. On a rebase conflict, abort the rebase, preserve the repair commits, and report the unresolved grouping/history decision. Leave unrelated changes untouched.

If the user chooses follow-up commits instead, use the normal commit proposal/approval workflow for those groups, then return here for re-review without starting a second repair loop.

## Completion

Finish only when the worktree matches the reviewed state, the latest review returns `Good to commit: Yes`, and every finding is verified as resolved, dismissed with evidence, or deferred by an explicit user decision. No required evidence may remain missing.

Report the repaired findings, any dismissed/deferred items, old-to-new commit hashes, checks run, the final reviewed base and HEAD, and any guardrail proposal from Recurring Findings below.

- **Called by normal commit on a feature branch:** end here. Recommend `/cobb commit finalise` when every story, acceptance criterion, and task in the active PRD is checked; otherwise list the open items and recommend `/cobb implement`. Finalise runs only when the user calls it.
- **Called by finalise:** return the new review record to the pending finalise step. Keep any confirmed decision bundle and completed closeout work; finalise resumes at its pending step.
- **Called by normal commit on a base branch:** conclude the review without offering finalise. Publishing remains a separate, explicitly approved action.
- **Called by hotfix:** return to its pre-commit snapshot checks with the index holding the reviewed tree.

## Recurring Findings

When the same finding class appears in more than one pass, or matches a class already recorded in `tasks/context.md` from an earlier session, propose a guardrail instead of relying on the next review to catch it again.

- A mechanical rule (a fixed syntactic pattern, a banned API, an import shape, a file-location rule) gets a deterministic check. Pick the strongest mechanism the situation allows: a type that makes the wrong state unrepresentable, then a lint rule or banned API that fails CI, then a canonical helper, then a runtime check. Agents copy whatever the surrounding code does, so a weaker guard becomes the next template.
- A judgement call (cross-file consistency, matching surrounding style) stays a review rule under Repo conventions in `tasks/context.md`.

List the proposal in the completion report as a recommended follow-up. Adding the check is its own commit or PRD, outside this repair loop, so the caller's own choice block stays the only one.
