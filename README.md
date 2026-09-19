# cobb

A single skill for ongoing product development, split into phases you call as subcommands.

`cobb` routes each request to a phase, then runs that phase under shared guardrails. Everything lives in one skill (`skills/cobb/`) — the phases are reference files loaded on demand, not separate skills.

## Subcommands

- `/cobb` — show the subcommand menu and recommend the next phase based on `tasks/` state (read-only; never runs a phase on its own).
- `/cobb prd` — explore the codebase, interview in rounds until every design decision is resolved, and create implementation-ready PRDs (`tasks/f-##-*.md`) with status, priority, technical design, traceability, and TDD instructions. Also `/cobb list` to summarise active PRDs.
- `/cobb diagnose` — find the cause of a bug whose cause is unknown: build a loop that goes red on the bug, minimise the repro, test ranked hypotheses, and return a diagnosis report. `prd` runs it automatically for a fix with an unknown cause, and `implement` runs it when a RED test fails to reproduce the bug; call it directly only when you want the cause before any PRD exists. Read-only on the repo; commits nothing.
- `/cobb design` — choose UI, UX, motion, or imagery. Planning produces design direction; audits stay read-only. Explicit requests for working code run implement's preflight first (PRD, ready scope, branch). Requested imagery exports are produced directly. Design guidance is still being refined and has not been fully tested through agent runs.
- `/cobb implement` — implement a ready PRD as vertical behavioural slices, using red-green-refactor where practical, and check off completed stories/tasks.
- `/cobb review` — read-only branch review for correctness, security, tests, and scope, with numbered findings, a clear go/no-go decision, and an exact state fingerprint. It uses an explicit base, the branch upstream, or one clear repository default. Pass `/cobb review <base-ref>` when the base is unclear or to review a fully pushed branch against its merge target.
- `/cobb commit` — propose atomic, user-approved commits (one at a time, or approve a multi-commit plan in one go), then automatically review, repair clear findings, and fold repairs into the appropriate unpublished commits. Also `/cobb commit finalise` (merge/branch cleanup) and `/cobb commit hotfix`.
- `/cobb context` — maintain `tasks/context.md` (project language, decisions, state) inline or via explicit backfill.
- `/cobb compact` — compact `tasks/context.md` by summarising older entries when it gets noisy.

`cobb` is user-invoked only: it runs when you type `/cobb`, never on its own. Commands match the longest complete prefix: `commit finalise`, `commit hotfix`, and `prd list` take precedence over `commit` and `prd`. An explicit design mode also wins over inferred intent.

These phases are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## Interaction contract

- Every bounded user choice is numbered so a reply can be only the option number.
- All options appear together in one uninterrupted block at the end of the message, after context and status information. The block starts with `0 — Recommended` and a brief reason, immediately followed by alternatives `1..N`, including confirmations and finalise. Replying `0` (or `default`) selects the recommendation; silence does not approve it. An interview round is the one exception: the block holds every question of the round, each with its own `0 — Recommended`.
- Open-ended input is used only when useful answers cannot be represented honestly as options.
- Interviews run in rounds. Each round asks every question whose prerequisites are settled, numbered `Question X of Y` with its own recommendation, so a reply can be `3:0 4:1 5:2`. Questions that depend on an open answer wait for the next round. Facts are looked up, not asked. If an answer changes the dependency tree, the skill announces the revised total and reason.

## Recommended workflow: idea → merged

1. `/cobb prd` (for a bug with an unknown cause, prd runs `diagnose` first and writes the fix PRD from its report) → `/cobb design` (optional, UI/UX-heavy features) → `/cobb implement`
   Context: capture durable decisions and project language inline as each step executes.
2. `/cobb commit` (`commit` mode): atomic commits with user approval, followed automatically by `/cobb review` once all intended groups are committed and the worktree is clean.
3. Post-review loop: automatically fix blockers and suggestions, run checks, fold each repair into its original unpublished commit where safe, and review again, for at most three passes. Pause only for a real decision, unavailable required evidence, or an unsafe history change. The session ends here; repeat steps 1 to 3 until the PRD is fully checked.
4. `/cobb commit finalise`: run it yourself once the PRD is fully checked and the last repair loop passed; it refuses an unfinished PRD unless you confirm a partial merge. Confirm the closeout commit, archive the completed PRD, and update `tasks/context.md` if needed. Then merge and clean up branches using the confirmed choices.
5. `/cobb compact` (periodic): summarise older context entries to keep tracking files easy to scan.

The default is **implement -> commit -> review/repair -> finalise**. Review checks stable commits; each repair or history rewrite ends with another review. Finalise also re-reviews when the target changes or advances, but not for its tracking-only closeout commit. On a pushed branch the automatic review covers the unpushed changes, so finalise re-reviews against the merge target.

Routine review repairs need no extra approval. Automatic folding is limited to private, unpublished feature-branch history; if that cannot be established, the skill asks for a safe alternative such as new atomic fix commits. Standalone `/cobb review` stays read-only. Initial commits and finalise's closeout, merge, push, and deletion choices still need approval.

Hotfix mode prepares and stages one approved change, including tests and tracking notes, then reviews that exact staged snapshot before committing. The same repair loop runs on the staged change, restaging repairs instead of folding commits. The default branch may be fully up to date with its upstream; the pending change is what gets reviewed. The final commit must match the reviewed parent and staged tree.

## Files the skill manages

- `tasks/f-##-<slug>.md`
  - One PRD per feature, named with feature ID (e.g. `f-01-invite-teammates.md`).
  - Self-contained, codebase-grounded spec with `Status:` (draft | ready), `Priority:` (P0–P3), and `Type:` (feat | fix | chore).
  - Maps stable story and acceptance-criterion IDs to ordered implementation slices and verification evidence.
  - Includes a TDD contract for behavioural work or a justified, repeatable exception.
  - Readiness is recalculated after updates. Completed items stay checked only while their requirements and evidence remain valid; affected items reopen without losing unaffected progress.
  - During finalise, completed PRDs move to `tasks/archive/` (same filename, no rename).

- `tasks/context.md`
  - Shared work state, project language (one canonical term per concept, with synonyms to avoid), agreed decisions, milestones, and technical constraints. Every phase names symbols, tests, and messages from the language section.
  - Agent preferences and self-improvement notes follow `AGENTS.md`'s memory policy instead; task files are not an alternative memory store.

- `tasks/archive/`
  - Archived completed PRDs, moved during `commit` finalise.

## Layout

```
skills/cobb/
  SKILL.md                    # router: dispatch table, shared guardrails, bare-/cobb behaviour
  references/
    prd.md  diagnose.md  design.md  implement.md  tdd.md  review.md  commit.md
    review-hotfix.md  commit-review.md  finalise.md  context-log.md  compact.md
    design/                   # ui / ux / motion / imagery; conditional tokens, examples,
                              # shadcn states, marketing rules, and official design systems
    templates/                # PRD, report, context, compact, commit, finalise templates
```
