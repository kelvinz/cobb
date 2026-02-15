---
name: new
description: "Create or update `tasks/todo.md` as the prioritised project backlog with clear `feat`/`fix`/`chore` items and ordering. Triggers: new backlog, update todo.md, add backlog item, reprioritise roadmap."
---

# new

Create or update `tasks/todo.md` as the source of truth for what the project is and what features will be built.

---

## Guardrails

- Do not implement code.
- Do not write individual feature PRDs (use `plan` for that).
- Keep features "PRD-sized": one feature = one PRD.
- Split the feature if it spans >2 subsystems, >1 UI surface + backend, or >~1 day of work.
- Prefer a stable `todo.md` structure; edit in place rather than rewriting.
- Write `tasks/todo.md` so a junior dev (or another AI) can pick it up without extra context.
- Do not use Markdown tables (use checklists + bullets).
- Do not check feature boxes unless the PRD actually exists (typically updated by `plan`).
- Treat memory capture as built-in.
- If durable decisions are made, update `tasks/memory.md` in this step.
- Do not defer to a separate memory pass.

---

## Workflow

1. Determine intent:
   - **New project** → initialise `tasks/todo.md`.
   - **Add/update features** → edit the existing `tasks/todo.md`.
2. If `tasks/memory.md` exists, skim relevant sections first.
   - project
   - key decisions
   - notes / gotchas
   - avoid conflicts with prior decisions
3. Ask clarifying questions only when needed (use A/B/C/D options).
4. Update `tasks/todo.md` using `references/todo-template.md`:
   - **New project**: write a crisp Project section.
   - Propose an initial prioritised feature list (highest priority first).
   - **Add/update**: add, merge, re-scope, and/or re-order features.
     - If adding a new `Type: fix` item and placement is not specified, ask if it should move up the list.
     - Priority is determined by list order.
5. Ensure each feature has clear in-scope vs out-of-scope boundaries and dependencies (if any).
6. Evaluate memory-worthy outcomes and update `tasks/memory.md` inline when needed:
   - project definition changes
   - scope boundaries or constraints that affect future features
   - priority decisions with durable rationale
7. Reply with updated file paths and a short change summary (what you added/changed).

---

## Clarifying Questions (Only If Needed)

Ask up to ~7 high-value questions. Keep them answerable via `1A, 2C, 3B`.

Focus on ambiguity around:

- target user + primary use case
- the problem + desired outcome
- constraints (platforms, timeline, integrations)
- success metrics / how we know it worked
- scope boundaries (what's explicitly in vs out)
- priority order (what should be done first)
- whether an item should be `Type: feat` vs `fix` vs `chore` (and where it should sit in priority order)
- dependencies between features (by ID)

### Example question format

```text
1. What are we doing right now?
   A. Start a brand new project
   B. Add new features to an existing plan
   C. Refine/re-scope existing planned features
   D. Other: [describe]
```

---

## Update Rules (When `tasks/todo.md` Exists)

- Preserve existing content and wording unless the user asks to change it.
- Avoid duplicates.
- If a new feature overlaps an existing one, merge it or propose a rename.
- Keep IDs stable; IDs must be globally unique within `tasks/todo.md`.
- When adding a new feature, use the next ID as `(max existing f-##) + 1` (never reuse old IDs).
- If duplicate IDs already exist, renumber newer or less-referenced items.
- Update any `Dependencies:` references after renumbering.
- Keep the list prioritised top-to-bottom; if placement is unclear, ask where to insert (or add to the bottom).
- If a feature depends on another feature, list the dependency above it.
- If not, explicitly confirm the ordering.
- Keep checkbox meaning consistent: checked means "PRD exists".
- Ensure each feature entry includes:
  - a type (feat/fix/chore)
  - a clear user-visible outcome
  - in scope / out of scope boundaries
  - dependencies by ID (if any)

---

## Feature Writing Guidelines

- Prefer feature names as verb phrases (e.g., "Invite teammates", "Export CSV").
- For fix items, name them clearly (e.g., "Fix <problem>") and set `Type: fix`. Include minimal bug info:
  - Current behaviour: …
  - Expected behaviour: …
  - Repro steps (if known): …
- For chores, keep them crisp and outcome-oriented (e.g., "Chore: remove dead code") and set `Type: chore`.
- Ensure each feature has a crisp outcome (what changes for the user).
- Avoid implementation tasks ("refactor", "set up DB") unless they are truly user-facing requirements.
- If a feature is too large, split by user goal or workflow step until each item could reasonably become a single PRD.

---

## Output

- Create or reuse `tasks/`.
- Create or update `tasks/todo.md`.
- After updating, suggest the next feature to spec with `plan` (by ID/name).
- Suggest the highest-priority unchecked feature (checked = PRD exists).
- When a PRD is created via `plan`, ensure the matching feature checkbox is checked in `tasks/todo.md`.
- If you made a durable project decision, update `tasks/memory.md` in the same run.
- Examples: scope boundary, constraint, key choice.
- End with a short status block:
  - **Files changed**: list of created/updated files
  - **Key decisions**: any assumptions or choices made (if any)
  - **Next step**: recommended next skill or action

---

## Quality Checklist

Before finalising `tasks/todo.md`:

- [ ] Project section explains what the project is and who it serves.
- [ ] Feature list is prioritised and reasonably sized (avoid 30 "must-haves").
- [ ] Feature IDs are unique and stable (no duplicates).
- [ ] No feature is checked unless its PRD exists.
- [ ] Each feature has a `Type:` (`feat` / `fix` / `chore`).
- [ ] Each feature has a user-visible outcome and explicit scope boundaries.
- [ ] Dependencies (if any) reference valid feature IDs.
- [ ] Duplicates/overlaps are merged or clearly distinguished.
