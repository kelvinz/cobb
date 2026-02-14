---
name: memory
description: "Maintain durable project memory in `tasks/memory.md` (state, decisions, milestones, gotchas), inline during other workflows or standalone for cleanup/backfill. Triggers: update memory.md, decision log, record project context."
---

# memory

Maintain `tasks/memory.md` as a living, durable "what matters" record for the project.
Write it for someone taking over the project (or you returning later).
Explain where things are, what was decided, and what to watch before proceeding.
Treat this as shared behaviour embedded in other skills, not a mandatory standalone step in normal workflows.

---

## Guardrails

- Do not store secrets (API keys, tokens, credentials).
- Keep entries short and durable; avoid duplicating long PRDs or code.
- Update `tasks/memory.md` in place; do not rewrite the whole file.
- Write in plain language so a junior dev (or another AI) can take over without extra context.
- Prefer inline updates during active skills (`new`, `plan`, `design`, `implement`, `review`, `commit`).
- Update when worthwhile information emerges.

### What goes where
- `tasks/todo.md` = what we intend to do
- PRD (`tasks/f-##-*.md`) = the spec + progress checklist for one feature
- `tasks/memory.md` = project-specific: durable decisions, milestones, gotchas, and "where we are now"

---

## What to Record

- Project gist (what it is, who it's for, success measures)
- Current state (what's done, what's next, what's blocked)
- Key decisions (what we chose + why + tradeoffs)
- Durable design decisions (tokens, interaction patterns, UX constraints) that future implementation/review depends on
- Completed work (feature IDs and notable outcomes)
- Notes/gotchas (constraints, pitfalls, conventions, sharp edges)

Avoid:

- raw meeting transcripts
- verbose day-by-day logs
- duplicate content that already lives in PRDs or code

---

## Workflow

1. Ensure `tasks/` exists; create `tasks/memory.md` if missing.
2. Determine invocation style:
   - Inline call (from another skill): apply this workflow as part of that skill's execution.
   - Direct call: use for explicit backfill/repair/cleanup requests.
3. Update `tasks/memory.md` in place; do not rewrite the whole file.
4. Add short entries (1–3 lines) in the most relevant section.
5. All dated sections are oldest-first (append new entries at the bottom).
6. Prefer referencing stable feature IDs (`f-##`) and avoid file paths (paths can change after archiving/compaction).
7. If it's unclear what to record, ask one clarifying question.

---

## `tasks/memory.md` Template (Markdown)

If `tasks/memory.md` does not exist, create it with this structure:

```markdown
# Project Memory: <project name>

## Project
- One-liner: …
- Target users: …
- Success metrics: …
- Constraints (optional): …
- Non-goals (optional): …

## Current state
- Where we are: …
- Next up: f-##
- Blockers / risks: …

## Key decisions
- YYYY-MM-DD: <decision>
  - Why: …
  - Tradeoffs: …

## Completed
- YYYY-MM-DD: f-## <feature name> — Completed and archived
  - Notes: …

## Notes / gotchas
- YYYY-MM-DD: …

## Links (optional)
- `tasks/todo.md`
```

---

## Output

- Create or update `tasks/memory.md`.
- Reply with the file path and a short summary of what was added/updated (or why memory update was skipped).
- End with a short status block:
  - **Files changed**: list of created/updated files
  - **Key decisions**: any assumptions or choices made (if any)
  - **Next step**: recommended next skill or action
