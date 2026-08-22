# cobb

A single skill for ongoing product development, split into phases you call as subcommands.

`cobb` routes each request to a phase, then runs that phase under shared guardrails. Everything lives in one skill (`skills/cobb/`) — the phases are reference files loaded on demand, not separate skills.

## Subcommands

- `/cobb` — show the subcommand menu and recommend the next phase based on `tasks/` state (read-only; never runs a phase on its own).
- `/cobb prd` — explore the codebase, interview one design decision at a time, and create implementation-ready PRDs (`tasks/f-##-*.md`) with status, priority, technical design, traceability, and TDD instructions. Also `/cobb list` to summarise active PRDs.
- `/cobb design` — optional design router for UI/UX direction, interaction/motion, and imagery, static or animated SVG (`ui` / `ux` / `motion` / `imagery` modes). The mode references are detailed but still being refined and not yet battle-tested; treat their output as a strong starting point and review it before relying on it.
- `/cobb implement` — implement a ready PRD as vertical behavioural slices, using red-green-refactor where practical, and check off completed stories/tasks.
- `/cobb review` — read-only branch review for correctness, security, tests, and scope, with numbered findings, a clear go/no-go decision, and an exact state fingerprint. It uses an explicit base, the branch upstream, or one clear repository default. Pass `/cobb review <base-ref>` when the base is unclear or to review a fully pushed branch against its merge target.
- `/cobb commit` — propose atomic, user-approved commits (one at a time, or approve a multi-commit plan in one go), then run review automatically after the final clean group and route numbered fixes/suggestions. Also `/cobb commit finalise` (merge/branch cleanup) and `/cobb commit hotfix`.
- `/cobb context` — maintain `tasks/context.md` inline or via explicit backfill.
- `/cobb compact` — compact `tasks/context.md` by summarising older entries when it gets noisy.

These phases are written to be handoff-friendly: assume a junior dev (or another AI) may pick up the project later.

## Interaction contract

- Every bounded user choice is numbered so a reply can be only the option number.
- Every choice set marks exactly one **Recommended** option from repository evidence, safety, and best practice; replying `0` (or `default`) selects it.
- Open-ended input is used only when useful answers cannot be represented honestly as options.
- One-at-a-time interviews announce their total first and label each prompt `Question X of Y`. If an answer changes the dependency tree, the skill announces the revised total and reason.

## Recommended workflow: idea → merged

1. `/cobb prd` → `/cobb design` (optional, UI/UX-heavy features) → `/cobb implement`
   Context: capture durable decisions inline as each step executes.
2. `/cobb commit` (`commit` mode): atomic commits with user approval, followed automatically by `/cobb review` once all intended groups are committed and the worktree is clean.
3. Post-review loop: fix numbered blockers, optionally implement numbered suggestions, commit those changes, and re-review automatically. `0` selects the recommended reply.
4. `/cobb commit finalise`: after a valid clean review, archive the completed PRD, update `tasks/context.md` if needed (the tracking-only closeout commit does not trigger re-review), then merge using the confirmed strategy and delete branches safely.
5. `/cobb compact` (periodic): summarise older context entries to keep tracking files easy to scan.

The default is **implement -> commit -> review -> finalise**. Atomic commits give review a stable branch diff and preserve focused history. Reviewing before commit would inspect a moving staged/unstaged worktree and then duplicate the review after commit. Finalise reruns review only when new code would enter the merge — base movement, target change, or code changes beyond the tracking-only closeout commit. On a pushed branch the automatic review is scoped to the unpushed delta, so finalise re-reviews against the merge target; that is expected, not a loop.

## Files the skill manages

- `tasks/f-##-<slug>.md`
  - One PRD per feature, named with feature ID (e.g. `f-01-invite-teammates.md`).
  - Self-contained, codebase-grounded spec with `Status:` (draft | ready), `Priority:` (P0–P3), and `Type:` (feat | fix | chore).
  - Maps stable story and acceptance-criterion IDs to ordered implementation slices and verification evidence.
  - Includes a TDD contract for behavioural work or a justified, repeatable exception.
  - During finalise, completed PRDs move to `tasks/archive/` (same filename, no rename).

- `tasks/context.md`
  - Project state, key decisions, milestones, and gotchas — written for handoff.

- `tasks/archive/`
  - Archived completed PRDs, moved during `commit` finalise.

## Layout

```
skills/cobb/
  SKILL.md                    # router: dispatch table, shared guardrails, bare-/cobb behaviour
  references/
    prd.md  design.md  implement.md  tdd.md  review.md  commit.md
    commit-review.md  finalise.md  context.md  compact.md
    design/                   # ui / ux / motion / imagery plus conditional UI token references
    templates/                # PRD, report, context, compact, commit, finalise templates
```
