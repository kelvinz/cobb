# cobb

A single skill for ongoing product development, split into phases you call as subcommands.

`cobb` routes each request to a phase, then runs that phase under shared guardrails. Everything lives in one skill (`skills/cobb/`) — the phases are reference files loaded on demand, not separate skills.

## Subcommands

- `/cobb` — show the subcommand menu and recommend the next phase based on `tasks/` state (read-only; never runs a phase on its own).
- `/cobb prd` — explore the codebase, interview in rounds until every design decision is resolved, and create implementation-ready PRDs (`tasks/f-##-*.md`) with status, priority, technical design, confirmed test seams, traceability, and TDD instructions. Also `/cobb list` to summarise active PRDs.
- `/cobb diagnose` — find the cause of a bug whose cause is unknown: build a loop that goes red on the bug, minimise the repro, test ranked hypotheses, and return a diagnosis report. `prd` runs it automatically for a fix with an unknown cause, and `implement` runs it when a RED test fails to reproduce the bug; call it directly only when you want the cause before any PRD exists. Read-only on the repo; commits nothing.
- `/cobb design` — design with function before form: UX (flow, states, copy, accessibility) is settled before UI, motion, or imagery. Planning produces design direction, recorded in a PRD: design runs `prd` first when none covers the surface. Audits stay read-only; `record` writes the root `DESIGN.md` from existing code. Explicit requests for working code run implement's preflight first (PRD, ready scope, branch). Requested imagery exports are produced directly. Design guidance is still being refined and has not been fully tested through agent runs.
- `/cobb implement` — implement a ready PRD as vertical behavioural slices, using red-green-refactor where practical, verify each acceptance criterion on the real surface (graded verified, not verified, or inconclusive), and check off completed stories/tasks. Restructuring chores pin current behaviour first and prove it unchanged.
- `/cobb review` — read-only branch review for correctness, security, tests, spec fidelity against the PRD, root cause versus symptom, and design and code-smell baselines, with numbered findings, dismissed candidates with reasons, a clear go/no-go decision, and an exact state fingerprint. It uses an explicit base, the branch upstream, or one clear repository default. Pass `/cobb review <base-ref>` when the base is unclear or to review a fully pushed branch against its merge target.
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
   Function before form: the PRD settles flow, states, copy, and accessibility; design adds the visual layer after.
   Context: capture durable decisions and project language inline as each step executes.
2. `/cobb commit` (`commit` mode): propose atomic commits with full template messages and wait for user approval. The command itself, or permission to edit files, does not approve a commit. Once all intended groups are committed and the worktree is clean, `/cobb review` runs automatically.
3. Post-review loop: automatically fix blockers and suggestions, run checks, fold each repair into its original unpublished commit where safe, and review again, for at most three passes. Pause only for a real decision, unavailable required evidence, or an unsafe history change. The session ends here; repeat steps 1 to 3 until the PRD is fully checked.
4. `/cobb commit finalise`: run it yourself once the PRD is fully checked and the last repair loop passed. Confirm the target and strategy; sync or safely rebase before review against that target. Then approve the tracking-only closeout and merge. An unfinished PRD needs explicit partial-delivery scope and stays active with its open items. Only completed PRDs are archived. Squash delivery also needs approval of its combined scope/message.
5. `/cobb compact` (periodic): summarise older context entries to keep tracking files easy to scan.

The default is **implement -> commit -> review/repair -> finalise**. Review checks stable commits; each repair or preparatory history rewrite ends with another review. Finalise also re-reviews when the target or delivery scope changes, but not for its verified tracking-only closeout commit. It checks the final merge tree before push or branch cleanup. On a pushed branch the automatic commit review covers the unpushed changes; finalise reviews against the merge target, including a fully pushed branch.

Incremental reviews check delivered behaviour without demanding unfinished future slices. An archived PRD on an unmerged feature branch is not proof that a dependency is available.

Routine review repairs need no extra approval. Automatic folding is limited to private, unpublished feature-branch history; if that cannot be established, the skill asks for a safe alternative such as new atomic fix commits. Standalone `/cobb review` stays read-only. Initial commits and finalise's closeout, merge, push, and deletion choices still need approval.

Hotfix mode prepares and stages one approved change, including tests and tracking notes, then reviews that exact staged snapshot before committing. The same repair loop runs on the staged change, restaging repairs instead of folding commits. The default branch may be fully up to date with its upstream; the pending change is what gets reviewed. The final commit must match the reviewed parent and staged tree.

### Session boundaries

Each phase can run in a fresh chat session or the same one. A fresh session is safe between `prd` (or `design`) and `implement`, because the PRD is the handoff document. Stay in one session from `commit` through review, repairs, and finalise: the repair loop depends on the session-start hash and the review record. Compact or clear only at a phase boundary, never mid-phase.

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
  - The optional verification recipe (launch, drive, capture evidence, tear down) tells `implement` and `review` how to verify on the real surface.
  - Agent preferences and self-improvement notes follow `AGENTS.md`'s memory policy instead; task files are not an alternative memory store.

- `tasks/archive/`
  - Archived completed PRDs, moved during `commit` finalise.

- `DESIGN.md` (repository root, projects with a UI)
  - The durable visual system in a portable format: token frontmatter and eight fixed sections.
  - Recorded as built, and updated in the same commit as any change to the visual system. A PRD's visual direction overrides it for that feature only.

## Layout

```
skills/cobb/
  SKILL.md                    # router: dispatch table, shared guardrails, bare-/cobb behaviour
  references/
    prd.md  diagnose.md  design.md  implement.md  tdd.md  review.md  commit.md
    review-hotfix.md  review-smells.md  design-principles.md  commit-review.md
    finalise.md  context-log.md  compact.md
    design/                   # ui / ux / motion / imagery; product and marketing surfaces,
                              # visual verification, dark-pattern check, tokens, examples,
                              # shadcn states, and official design systems
    templates/                # PRD, report, context, compact, commit, finalise, DESIGN.md templates
```
