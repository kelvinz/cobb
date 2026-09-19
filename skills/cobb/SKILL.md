---
name: cobb
description: "Product-development workflow: prd, design, implement, review, commit, finalise, hotfix, context, compact."
disable-model-invocation: true
---

# cobb

A single skill for ongoing product development. Route a request to the right phase, then execute that phase under the shared guardrails below.

The full flow is: `prd` → `design` (optional, UI/UX-heavy work) → `implement` → `commit` → automatic review, repair, and commit folding until resolved → `finalise` → `compact` (periodic). `context` is captured inline throughout, not as a separate step.

Normal delivery reviews stable commits. Hotfix mode instead reviews the exact staged change before committing.

---

## Progressive Disclosure Contract

This file is navigation, not the full operating manual. On activation:

1. If `AGENTS.md` exists in the repo root and has not already been read in this context, read it first and follow the instructions and file references it contains.
2. Load only the selected phase reference from Dispatch.
3. For nested routers, load the router first, then only the selected child reference.
4. Load templates, examples, and secondary references only when the selected reference explicitly requires them for the current task.
5. For multi-phase requests, complete one phase at a time and load the next phase reference only when that phase begins.

---

## Dispatch

Match the longest explicit command prefix, using whole words. Load only its phase reference and pass the remaining arguments through unchanged.

| Command prefix | Phase | Load reference |
|----------------|-------|----------------|
| _(none)_ | show menu | (no file — see "Bare `/cobb`") |
| `commit finalise` / `finalise` | finalise branch | `references/finalise.md` |
| `commit hotfix` / `hotfix` | hotfix commit | `references/commit.md` (hotfix mode) |
| `prd list` / `list` | list PRDs | `references/prd.md` (list mode) |
| `prd` | create/update PRD | `references/prd.md` |
| `design` | select design mode | `references/design.md` |
| `implement` | implement a PRD | `references/implement.md` |
| `review` | branch review | `references/review.md` |
| `commit` | atomic commits | `references/commit.md` |
| `context` | maintain task context | `references/context-log.md` |
| `compact` | compact task context | `references/compact.md` |

### Routing rules

1. Explicit commands win over inferred intent: `commit finalise`, `commit hotfix`, and `prd list` match before `commit` or `prd`.
2. If no prefix matches and intent is clear, infer the phase, state it in one line, and proceed. If intent is ambiguous, use the bare menu.
3. Pass an explicit design mode through to the design router; `/cobb design ui` selects `ui` even when another mode could fit the remaining text.

### Bare `/cobb` (no subcommand)

Stay read-only and show the menu:

1. Read `tasks/` — list active PRDs (`f-##`, name, `Status`, `Priority`) and check git branch/commit state.
2. Print the subcommand menu (the dispatch table above) so the user sees the options.
3. Offer the phases as a numbered choice, recommending the one repository state indicates, so the user can reply with a number instead of a command name.
4. Recommend the single next phase based on state, for example:
   - no `tasks/context.md` or no PRDs → "start with `/cobb prd`"
   - a `Status: ready` PRD with no feature branch → "`/cobb implement <prd>`"
   - feature branch ahead of base with uncommitted changes → "`/cobb commit` (review and repairs run after the final clean commit group)"
   - feature branch committed, repair loop complete, PRD fully checked → "`/cobb commit finalise`"
   - feature branch committed but not yet reviewed → "`/cobb commit finalise` (it runs review and repairs first)"
   - `tasks/context.md` long/noisy → "`/cobb compact`"
5. Wait for the user's option number or explicit subcommand before acting.

---

## Shared Guardrails (apply to every phase)

- **Choices (all phases and follow-up prompts).** For every menu, question with options, confirmation, or next-action choice, put all context, explanations, and status information before the options. End the message with one uninterrupted choice block: exactly one `0 — Recommended: <action> — <brief reason>`, immediately followed by each distinct alternative once as `1..N`. Before sending, check that all options appear together in this final block, with no other content between them or after them. Use this format even for yes/no decisions and finalise. An interview round is the one exception: the final block holds every question of the round in order, each with its own `0 — Recommended` and alternatives, and the reply pairs question numbers with option numbers (`3:0 4:1`). Choose the recommendation from repository evidence and safety; recommend stopping or investigating when proceeding is unsafe or evidence is missing. Accept the number alone, or `default` for `0`, and wait for the user's choice wherever approval is required. A default is a displayed recommendation, not permission to act on silence. Use open input only when fixed options would lose essential information.
- **Interview in rounds.** Before an interview, explore enough context to build the question tree and state the total. Each round asks the whole **frontier**: every question whose prerequisites are already settled. Number the questions `Question X of Y` and give each its own recommendation in the shared Choices format. A question whose answer depends on another question still open in this round waits for the next round. When a fact needs a repository or documentation lookup, look it up (or dispatch a sub-agent) and ask the rest of the frontier now; only the questions downstream of that lookup wait. If an answer creates or removes dependent questions, announce the revised total and why before the next round.
- **Task context.** Before recording or proposing task-state updates, read `references/context-log.md` for the boundary between task records and agent memory, entry placement, and README checks. File-writing phases update context inline; review only proposes entries.
- **Base branches.** The base-branch list is `main`, `master`, `dev`, `develop`, `trunk`, plus names declared under Repo conventions in `tasks/context.md`. Every phase that resolves a comparison base or merge target uses this list.
- **Handoff-friendly.** Assume a junior dev (or another AI) picks this up later. Plain language, explicit edge cases, no hidden assumptions.
- **Never claim untested success.** Do not say tests/checks/builds passed unless you actually ran them; if you didn't run it, say so.
- **Status block.** Put this summary at the end of every standalone phase reply, before any final choice block:
  - **Files changed**: created/updated files
  - **Key decisions**: assumptions or choices made (if any)
  - **Next step**: recommended next phase or action
  - If the next step requires a user decision, follow the shared Choices rule.

---

## Files cobb manages

- `tasks/f-##-<slug>.md` — one PRD per feature, with `Status` (draft | ready), `Priority` (P0–P3), `Type` (feat | fix | chore), and a progress checklist.
- `tasks/context.md` — shared work state, project language (glossary), decisions, milestones, and technical constraints.
- `tasks/archive/` — completed PRDs moved here during `commit` finalise (same filename, no rename).

---

## References

The Dispatch table above is the single routing source for phase files. Two shared references are loaded by phases rather than dispatch:

- `references/tdd.md` — behavioural testing contract; loaded by `prd`/`implement` when applicable.
- `references/commit-review.md` — automatic repair and commit-folding loop; loaded by normal `commit`, `finalise`, or `hotfix` after a review result.

Design child references (`references/design/*.md`) are selected inside `references/design.md`, and templates (`references/templates/*.md`) load only when the active phase explicitly asks for them — each phase file names its own.
