---
name: plan
description: "Write or update a single-feature PRD (`Type: feat`/`fix`/`chore`) with scope, user stories, and acceptance criteria. Triggers: plan prd, write feature spec, define acceptance criteria, update prd."
---

# plan

Create a clear, implementation-ready PRD for a single feature (not code).

---

## Guardrails

- Do not implement the feature.
- If the user asks to implement, propose writing a PRD first (or ask if they want to skip the PRD).
- Prefer asking a small number of high-value questions; otherwise write a draft PRD with explicit assumptions.
- Write the PRD so a junior dev (or another AI) can implement it without extra context.
- Use plain language, explicit edge cases, and verifiable acceptance criteria.
- Treat memory capture as built-in.
- If planning introduces durable decisions/constraints, update `tasks/memory.md` in this step.

---

## Workflow

1. Identify the feature:
   - Prefer a feature ID like `f-01` if available.
   - If `tasks/todo.md` exists, use the matching feature entry as the baseline for outcome + scope.
   - If the feature entry includes `Type:`, carry it into the PRD Summary.
   - This lets `implement` branch and execute appropriately.
   - If `Type:` is missing, assume `Type: feat`.
   - If `tasks/todo.md` is missing, or the feature is not in it yet, stop.
   - Use `new` to add the feature to `tasks/todo.md` first.
   - If `tasks/memory.md` exists, skim relevant key decisions / notes before finalising requirements.
2. Check priority (if `tasks/todo.md` exists):
   - Priority is determined by list order (higher in the list = higher priority).
   - If there are higher-priority unchecked items above this feature, ask the user to confirm proceeding.
   - Mention those higher-priority IDs/names.
   - If the user says this item is urgent, recommend switching to `new`.
   - Move it higher in `tasks/todo.md`, then return to `plan`.
3. Determine the PRD file path:
   - First look for an active PRD matching the feature ID in `tasks/` (`tasks/f-##-*.md`).
   - If one exists, use it.
   - Otherwise use `tasks/f-##-<feature-slug>.md` (include the feature ID in the filename).
4. If a PRD already exists at that path, update it in place.
   - Do not create a duplicate PRD unless the user asks.
   - Do not reset existing checklist items inside the PRD.
5. Ask essential clarifying questions (lettered options) only when needed.
6. Confirm scope boundaries (in-scope vs non-goals) and success metrics.
7. Write or update the PRD at the chosen path (create `tasks/` if missing):
   - Ensure implementation progress is trackable via checklist items.
   - Example: user stories and acceptance-criteria checkboxes.
   - If `tasks/todo.md` lists `Dependencies:` for this feature, include them in "Dependencies & Constraints".
   - Dependency validation happens during `implement`.
   - For UI/UX-heavy features, include expected design inputs.
   - Examples: mockups, tokens, interaction notes.
   - State whether `design` should run before `implement`.
8. If `tasks/todo.md` exists, update it to reflect the PRD:
   - Check the feature checkbox (`- [ ]` → `- [x]`).
9. Evaluate memory-worthy outcomes and update `tasks/memory.md` inline when needed:
   - architecture or requirement decisions with durable impact
   - new constraints, non-goals, or rollout assumptions
   - risk decisions likely to affect later implementation/review
10. Reply with updated file paths and a short summary + open questions.

---

## Clarifying Questions (Only If Needed)

Ask up to ~7 questions.
Use numbered questions with A/B/C/D and an **Other** option.
Let the user reply like `1B, 2D, 3A`.

Cover only what is ambiguous:

- which feature this PRD is for (feature ID/name)
- user + use case
- problem + desired outcome
- scope boundaries (in scope vs out of scope)
- whether this is `Type: feat` vs `fix` vs `chore`
- feature dependencies (by feature ID)
- conflicts with existing decisions/constraints (from `tasks/memory.md`)
- platforms/surfaces
- data + permissions
- integrations / external dependencies
- success metrics
- rollout constraints / timeline

### Example question format

```text
1. What is the primary goal?
   A. Enable a new capability
   B. Improve an existing workflow
   C. Reduce cost / time / errors
   D. Other: [describe]
```

---

## PRD Template (Markdown)

Use `references/prd-template.md` as the default PRD template and checklist.

- Read it before drafting a new PRD.
- For updates to an existing PRD, edit only impacted sections and preserve existing checkbox state.
- Keep acceptance criteria concrete and verifiable; examples are in the reference file.

---

## Output

- Create or reuse `tasks/`.
- Save/update the PRD at the chosen path.
- Prefer existing active `tasks/f-##-*.md`; otherwise use `tasks/f-##-<feature-slug>.md`.
- If the slug or scope is ambiguous, ask the user to confirm before saving.
- If `tasks/todo.md` exists, update it (check the feature only; no PRD path field).
- If the PRD introduces durable decisions/constraints, update `tasks/memory.md` in the same run.
- For UI/UX-heavy PRDs, recommend `design` (optional) before `implement`.
- End with a short status block:
  - **Files changed**: list of created/updated files
  - **Key decisions**: any assumptions or choices made (if any)
  - **Next step**: recommended next skill or action

---

## Todo Sync (If `tasks/todo.md` Exists)

- Update `tasks/todo.md` in place; do not reformat the whole file.
- Find the matching feature by ID (preferred) or by feature name.
- Update the feature checklist item to checked (`- [ ]` → `- [x]`).
- In `tasks/todo.md`, checked means "PRD exists" (not "built").
- Preserve the feature's `Type:` / `Dependencies:` lines as-is unless the user explicitly asked to change them.
- If the feature is not present in `tasks/todo.md`, do not create a PRD yet.
- Use `new` to add the feature first, then return to `plan`.

---

## Quality Checklist

Before saving, run the "Quality Checklist" in `references/prd-template.md`.
At minimum confirm:
- existing PRDs were updated in place (no duplicates)
- `tasks/todo.md` checkbox was synced when applicable
- dependencies and `Type:` were preserved/updated correctly
