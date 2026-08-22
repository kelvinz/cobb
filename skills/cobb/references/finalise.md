# finalise

Load this reference only for `commit finalise` or `finalise` mode.

Shared guardrails from the cobb router apply; the rules below are finalise-specific.

Finalise runs **after** the review phase. In the standard flow (`implement → commit → review → finalise`), `review` runs automatically once all atomic commits are clean and `references/commit-review.md` hands off here on a clean pass — so finalise starts right after a passing review. Finalise trusts that review; the re-review guardrail below is the canonical rule for when a fresh review is required.

## Guardrails

- Require a clean feature branch, never the default/base branch.
- **Re-review rule (canonical).** Trust the review the review phase already produced; re-review only when new code would actually enter the merge — no clean review exists for the current code, the confirmed target differs from the reviewed base, or the target advanced with commits that get synced in. The closeout commit (`tasks/` bookkeeping only) and the merge/push/delete choices never trigger re-review.
  - Expect this to fire on a pushed branch. Review resolves the base upstream-first, so a post-commit pass on a pushed branch is scoped to `<remote>/<branch>..HEAD`, not to the merge target. The target then differs from the reviewed base and a fresh review is required. That re-review uses the confirmed target and terminates. An unpushed branch needs no re-review when its reviewed base is also the confirmed target.
- Confirm the target, then collect merge strategy, push, local deletion, and remote deletion as one coded decision bundle.
- Mark one evidence-based value **Recommended** for every field and show one **Recommended** complete bundle.
- Treat explicit coded choices as confirmation; ask only for missing or conflicting fields.
- Never assume `main`; resolve repository defaults and policy.
- Default push to **no** (`3B`); never present pushing to remote as the recommended default.
- Keep closeout tracking in one approved pre-merge commit; do not use it to catch up missed atomic updates without explicit approval.
- Sync with the confirmed target before merge.
- Never delete the target, default, or currently checked-out branch.
- Require explicit coded confirmation for push and each deletion.

## Workflow

1. Verify the worktree is clean, HEAD is a feature branch, and a clean review already covers the current code. The review phase normally provides this; run `review` once here only if none exists, route the result through `references/commit-review.md`, and continue only on a clean pass.
2. Resolve the active PRD:
   - prefer the PRD matching the branch feature ID
   - if several candidates exist, number them and recommend the strongest ID/name match
   - request an open-ended path only when repository discovery cannot produce candidates
3. Mark the PRD done and archive it (closeout tracking commit):
   - move `tasks/f-##-<slug>.md` to the same filename under `tasks/archive/` when not already archived
   - update `tasks/context.md` completed/current-state sections and applicable review-proposed `Finalise` entries
   - stage only those tracking changes
   - propose one `🧹 chore: finalise f-## <short-summary>` commit with the finalise body from `references/templates/commit-rules.md`
   - present numbered commit/edit/skip choices and mark the safe evidence-based choice **Recommended**
   - tracking-only, so it does not trigger re-review (see the canonical re-review guardrail)
   - skip the commit when no tracking change is needed and state why
4. Collect the finalise bundle. Mark one value **Recommended** in every field and show why it fits repository policy and risk:
   - target: `1A` (resolved default, **Recommended**), `1B`, ...; include `1X` for open custom text
   - strategy: `2A` auto (**Recommended**, resolves via `references/templates/finalise-policy.md` and executes without a second strategy prompt), `2B` merge-commit, `2C` linear-history, `2D` squash, `2E` rebase
   - push: `3A` yes, `3B` no (**Recommended**)
   - delete local: `4A` yes (**Recommended**), `4B` no
   - delete remote: `5A` yes, `5B` no (**Recommended**)
   - `0`/`default` means the displayed **Recommended** complete bundle (here `1A 2A 3B 4A 5B`), not a hardcoded strategy
   - shift a field's recommendation when repository evidence (e.g. a `tasks/context.md` merge preference, an unmerged or shared local branch) clearly favors another value, and say why
5. Sync HEAD with the confirmed target. This is normally a no-op; if sync brings in new commits or the target differs from the reviewed base, apply the canonical re-review guardrail before merging.
6. Resolve strategy using `references/templates/finalise-policy.md`.
   - when the user chose `auto` (`2A`), state the resolved strategy and its policy rationale in one line, then proceed to merge without re-prompting — choosing auto already authorised the policy result
   - prompt only when policy resolution is genuinely conflicting (e.g. contradictory `tasks/context.md` preferences): present numbered strategy choices (merge-commit / linear-history / squash / rebase / stop) and mark one **Recommended**
7. Merge using the confirmed strategy.
8. Push the target only when the bundle confirms push; otherwise state that remote update remains pending.
9. Recheck branch-deletion safety, then apply only the confirmed local/remote deletions.

## Output

Report the closeout commit, the review the merge relied on, merge result, push result, and branch cleanup. If any action remains, provide numbered next-step choices and mark one **Recommended**.
