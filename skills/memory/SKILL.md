---
name: memory
description: "Update `tasks/memory.md` with durable project memory (project gist, key decisions, completed milestones, and important notes/gotchas). Use when capturing decisions, constraints, lessons learned, release notes, or anything that should be remembered across sessions. Triggers: memory, remember, add to memory, project notes, decision log, lessons learned."
---

# memory

Maintain `tasks/memory.md` as a living, durable “what matters” record for the project.
Write it for someone taking over the project (or you returning later): it should explain where things are, what was decided, and what to watch out for before proceeding.

---

## Guardrails

- Do not store secrets (API keys, tokens, credentials).
- Keep entries short and durable; avoid duplicating long prds or code.
- Update `tasks/memory.md` in place; do not rewrite the whole file.
- Write in plain language so a junior dev (or another AI) can take over without extra context.

---

## What to Record

- Project gist (what it is, who it’s for, success measures)
- Current state (what’s done, what’s next, what’s blocked)
- Key decisions (what we chose + why + tradeoffs)
- Completed work (feature IDs, prds, notable outcomes)
- Notes/gotchas (constraints, pitfalls, conventions, sharp edges)

Avoid:

- raw meeting transcripts
- verbose day-by-day logs
- duplicate content that already lives in prds or code

---

## Workflow

1. Ensure `tasks/` exists; create `tasks/memory.md` if missing.
2. Update `tasks/memory.md` in place; do not rewrite the whole file.
3. Add short entries (1–3 lines) in the most relevant section.
4. Prefer referencing feature IDs (`f-##`) and prd paths when relevant.
5. If it’s unclear what to record, ask one clarifying question.

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
- YYYY-MM-DD: f-## <feature name> — Completed and finalised
  - prd: `tasks/done-f-##-<slug>.md`
  - Notes: …

## Notes / gotchas
- YYYY-MM-DD: …

## Links (optional)
- `tasks/todo.md`
```

---

## When to Use This

- During `new`: when the project definition changes or a major planning decision is made.
- During `plan`: when a prd introduces a key decision, constraint, or cross-cutting behaviour worth remembering.
- During `implement`:
  - When you discover an important gotcha or finalise a major implementation decision.
- During `review`:
  - When you complete a review and want to capture durable notes, risks, and follow-ups.
- During `commit` (finalise mode):
  - When a prd is merged—update "Current state" and "Completed" sections.

---

## Output

- Create or update `tasks/memory.md`.
- Reply with the file path and a short summary of what was added/updated.
