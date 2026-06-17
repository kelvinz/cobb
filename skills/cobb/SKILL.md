---
name: cobb
description: "Product-development workflow toolkit. Subcommands: prd, design, implement, review, commit, context, compact. Use to create/update/list PRDs, design UI/UX/motion/imagery, implement a PRD in code, review a branch for correctness/security/scope, create atomic commits and finalise a branch, maintain tasks/context.md, and compact it. Triggers: cobb, write prd, plan feature, create spec, list prds, design ui, improve ux, add transitions, implement prd, build feature from prd, review branch, readiness check, commit changes, split commits, finalise branch, update context, decision log, compact context."
---

# cobb

A single skill for ongoing product development. Route a request to the right phase, then execute that phase under the shared guardrails below.

The full flow is: `prd` → `design` (optional, UI/UX-heavy work) → `implement` → `review` (when needed) → `commit` (`commit` mode) → `review` (when needed) → `commit` (`finalise` mode) → `compact` (periodic). `context` is captured inline throughout, not as a separate step.

---

## Progressive Disclosure Contract

This file is navigation, not the full operating manual. On activation:

1. Do not preload every file listed in References.
2. Load only the selected phase reference from Dispatch.
3. For nested routers, load the router first, then only the selected child reference.
4. Load templates, examples, and secondary references only when the selected reference explicitly requires them for the current task.
5. For multi-phase requests, complete one phase at a time and load the next phase reference only when that phase begins.

---

## Dispatch

Parse the first token of the args and route to the matching phase. Load **only** that phase's reference file, then execute it.

| First token              | Phase            | Load reference                  |
|--------------------------|------------------|---------------------------------|
| _(none)_                 | orchestrate      | (no file — see "Bare `/cobb`")  |
| `prd`                    | PRD create/update/list | `references/prd.md`       |
| `design`                 | design sub-router (ui/ux/motion/imagery) | `references/design.md` |
| `implement`              | implement a PRD  | `references/implement.md`       |
| `review`                 | branch review    | `references/review.md`          |
| `commit`                 | atomic commit    | `references/commit.md`          |
| `commit finalise` / `finalise` | finalise branch | `references/commit.md` (finalise mode) |
| `commit hotfix` / `hotfix` | hotfix commit  | `references/commit.md` (hotfix mode) |
| `context`                | maintain context.md | `references/context.md`      |
| `compact`                | compact context.md | `references/compact.md`       |

### Routing rules

1. If the first token matches a phase, load that reference and execute it; pass the rest of the args through as the phase's input.
2. If no token matches but intent is clear from the request (e.g. "write a prd for X" → `prd`, "review my branch" → `review`), infer the phase, state which phase you picked in one line, then proceed.
3. If intent is ambiguous, fall back to the bare `/cobb` behaviour below.
4. `design` is itself a router: `/cobb design ui` selects the `ui` mode inside `references/design.md`.

### Bare `/cobb` (no subcommand)

Do not execute any phase. Instead:

1. Read `tasks/` — list active PRDs (`f-##`, name, `Status`, `Priority`) and check git branch/commit state.
2. Print the subcommand menu (the dispatch table above) so the user sees the options.
3. Recommend the single next phase based on state, for example:
   - no `tasks/context.md` or no PRDs → "start with `/cobb prd`"
   - a `Status: ready` PRD with no feature branch → "`/cobb implement <prd>`"
   - feature branch ahead of base with uncommitted changes → "`/cobb review`, then `/cobb commit`"
   - all commits done on a feature branch → "`/cobb review`, then `/cobb commit finalise`"
   - `tasks/context.md` long/noisy → "`/cobb compact`"
4. Wait for an explicit subcommand before acting.

---

## Shared Guardrails (apply to every phase)

- **Numbered short-reply options.** When asking the user for any decision or confirmation, present numbered options with low-keystroke replies (e.g. `1`, `2`, `3`). Some phases define richer codes (PRD: `1A, 2C`; commit finalise: `1A 2B …`, `0`/`default`).
- **Context capture is built-in.** Update `tasks/context.md` inline whenever durable decisions, risks, or gotchas emerge — never defer to a separate pass. See `references/context.md` for what/where to record.
- **Handoff-friendly.** Assume a junior dev (or another AI) picks this up later. Plain language, explicit edge cases, no hidden assumptions.
- **Never claim untested success.** Do not say tests/checks/builds passed unless you actually ran them; if you didn't run it, say so.
- **Status block.** End every standalone phase reply with:
  - **Files changed**: created/updated files
  - **Key decisions**: assumptions or choices made (if any)
  - **Next step**: recommended next phase or action

---

## Files cobb manages

- `tasks/f-##-<slug>.md` — one PRD per feature, with `Status` (draft | ready), `Priority` (P0–P3), `Type` (feat | fix | chore), and a progress checklist.
- `tasks/context.md` — durable project state, key decisions, milestones, gotchas (handoff record).
- `tasks/archive/` — completed PRDs moved here during `commit` finalise (same filename, no rename).

---

## References

Phase bodies (loaded on dispatch only):

- `references/prd.md` — create, update, or list PRDs.
- `references/design.md` — design sub-router (ui / ux / motion / imagery); selects one child reference.
- `references/implement.md` — implement a PRD and check off progress.
- `references/review.md` — branch review with a go/no-go decision.
- `references/commit.md` — atomic commits, finalise, and hotfix modes.
- `references/context.md` — maintain `tasks/context.md` (inline or standalone).
- `references/compact.md` — compact `tasks/context.md`.

Templates and rubrics (loaded only when the active phase asks for them):

- `references/templates/prd-template.md`
- `references/templates/report-template.md`
- `references/templates/context-template.md`
- `references/templates/compact-templates.md`
- `references/templates/commit-rules.md`
- `references/templates/finalise-policy.md`
