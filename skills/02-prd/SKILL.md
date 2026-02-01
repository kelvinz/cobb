---
name: 02-prd
description: Create a Product Requirements Document (PRD) / feature spec for a new or existing item (`Type: feat` / `fix` / `chore`). Use when planning scope, writing requirements, defining user stories + acceptance criteria, or turning an idea into an implementable spec. Triggers: PRD, product requirements, feature spec, bugfix spec, fix spec, requirements doc, spec this feature, write requirements, plan this feature.
---

# 02 PRD

Create a clear, implementation-ready PRD for a single feature (not code).

---

## Guardrails

- Do not implement the feature.
- If the user asks to implement, propose writing a PRD first (or ask if they want to skip the PRD).
- Prefer asking a small number of high-value questions; otherwise write a draft PRD with explicit assumptions.
- Write the PRD so a junior dev (or another AI) can implement it without extra context (plain language, explicit edge cases, verifiable acceptance criteria).

---

## Workflow

1. Identify the feature:
   - Prefer a feature ID like `F-001` if available.
   - If `tasks/todo.md` exists, use the matching feature entry as the baseline for outcome + scope.
   - If the feature entry includes `Type:`, carry it into the PRD Summary so `03-exe` can branch and execute appropriately.
   - If `Type:` is missing, assume `Type: feat`.
   - If `tasks/todo.md` is missing or the feature is not in it yet, stop and use `01-new` to add the feature to `tasks/todo.md` first.
   - If `tasks/memory.md` exists, skim relevant key decisions / notes before finalizing requirements.
2. Check priority (if `tasks/todo.md` exists):
   - Priority is determined by list order (higher in the list = higher priority).
   - If there are higher-priority unchecked items above this feature, ask the user to confirm they want to proceed (vs writing a PRD for one of the higher-priority items first). Mention the higher-priority IDs/names.
   - If the user says this item is urgent, recommend switching to `01-new` to move it higher in `tasks/todo.md`, then return to `02-prd`.
3. Determine the PRD file path:
   - If the feature entry in `tasks/todo.md` already has a `PRD:` line, use that path.
   - Otherwise use `tasks/prd-<feature-slug>.md`.
4. If a PRD already exists at that path, update it in place (do not create a duplicate PRD unless the user asks). Do not reset any status checklists inside the PRD.
5. If `tasks/todo.md` lists `Dependencies:` for this feature, ensure the dependency feature PRDs exist (checked items). If any dependency is unchecked or missing, do not write this PRD yet—recommend switching to the dependency PRD first.
6. Ask essential clarifying questions (lettered options) only when needed.
7. Confirm scope boundaries (in-scope vs non-goals) and success metrics.
8. Write or update the PRD at the chosen path (create `tasks/` if missing):
   - Ensure the PRD includes `## Execution Status (03-exe)` (add it if missing; do not reset checkboxes if present).
   - Ensure the PRD explicitly lists feature dependencies (from `tasks/todo.md`) in “Dependencies & Constraints”.
9. If `tasks/todo.md` exists, update it to reflect the PRD:
   - Check the feature checkbox (`- [ ]` → `- [x]`).
   - Add/update a `PRD: \`<path>\`` line under that feature.
10. Reply with the file path and a short summary + open questions.

---

## Clarifying Questions (Only If Needed)

Ask up to ~7 questions. Use numbered questions with A/B/C/D options and an **Other** option so the user can reply like `1B, 2D, 3A`.

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

Write the PRD using this default structure. Drop sections that truly do not apply, but prefer completeness.

```markdown
# PRD: <Feature name>

## Execution Status (03-exe)
- [ ] Implemented
- [ ] Tested
- [ ] Released

## 0. Summary
- **Feature ID**: F-###
- **Type**: feat | fix | chore
- **Dependencies** (feature IDs): <none> | F-002, F-010
- **What**: …
- **Why**: …
- **Who**: …
- **Success looks like**: …
- **Assumptions** (if any): …

## 1. Problem / Opportunity
Describe the user pain / opportunity and why now.
For fix items, include current behavior, expected behavior, and repro steps (if applicable).

## 2. Goals
- G-1: …
- G-2: …

## 3. Non-goals
- NG-1: …
- NG-2: …

## 4. Users & Use Cases
- Primary user: …
- Secondary user(s): …
- Key scenarios: …

## 5. UX / Flows (if applicable)
### 5.1 Primary flow
1. …
2. …

### 5.2 Edge cases & error states
- …

### 5.3 Accessibility (UI)
- …

## 6. Requirements
### 6.1 User stories
Write small stories that can be implemented in a focused session.
Make each story a checklist item so `03-exe` can execute in pieces and check things off.

- [ ] US-001: <Title>
  - **Description:** As a <user>, I want <capability> so that <benefit>.
  - **Acceptance criteria:**
    - [ ] Specific, verifiable criterion (avoid “works”, “correctly”, “fast” without numbers)
    - [ ] Key edge cases + error states are specified (including empty/loading states if applicable)
    - [ ] Permissions/roles are specified (if applicable)
    - [ ] Manual verification steps are listed (if UI)

### 6.2 Functional requirements
- FR-1: …
- FR-2: …

### 6.3 Non-functional requirements
- NFR-1 (performance): …
- NFR-2 (security/privacy): …
- NFR-3 (reliability/observability): …

## 7. Dependencies & Constraints (if applicable)
- Feature dependencies (from `tasks/todo.md`): <none> | F-002, F-010
- External dependencies (if any): …
- Constraints: …

## 8. Data, APIs, and Integrations (if applicable)
- Data model changes: …
- API changes: …
- Backward compatibility / migration: …

## 9. Analytics & Success Metrics
- Metrics: …
- Events/instrumentation: …

## 10. Rollout / Release Plan
- Feature flag: …
- Phases: …
- Rollback plan: …

## 11. Testing & QA Plan (if applicable)
- Test cases (happy path + key edge cases): …
- What is automated vs manual: …
- Environments / data setup needed: …

## 12. Risks & Mitigations
- R-1: …
- R-2: …

## 13. Open Questions
- Q-1: …
- Q-2: …

## 14. Appendix (optional)
- Alternatives considered: …
- Links to mockups/designs: …
```

### Acceptance criteria examples

- Bad: “Export works.”
- Good: “When a user clicks **Export CSV**, the app downloads a CSV that includes columns A/B/C in that order; if there are 0 rows, download still occurs with headers only; errors show a non-blocking toast with retry.”

---

## Output

- Create or reuse `tasks/`.
- Save/update the PRD at the chosen path (prefer existing `PRD:` path in `tasks/todo.md`; otherwise `tasks/prd-<feature-slug>.md`).
- If the slug or scope is ambiguous, ask the user to confirm before saving.
- If `tasks/todo.md` exists, update it (check the feature + link the PRD).
- If the PRD introduces durable decisions/constraints, capture them in `tasks/memory.md` via `04-rem`.

---

## Todo Sync (If `tasks/todo.md` Exists)

- Update `tasks/todo.md` in place; do not reformat the whole file.
- Find the matching feature by ID (preferred) or by feature name.
- Update the feature checklist item to checked (`- [ ]` → `- [x]`). In `tasks/todo.md`, checked means “PRD exists” (not “built”).
- Ensure the feature has a `PRD: \`<path>\`` line; add/update it if missing or wrong.
- Preserve the feature’s `Type:` / `Dependencies:` lines as-is unless the user explicitly asked to change them.
- If the feature is not present in `tasks/todo.md`, do not create a PRD yet—use `01-new` to add the feature first, then return to `02-prd`.

---

## Quality Checklist

Before saving the PRD:

- [ ] If a PRD already existed, it was updated in place (no duplicates).
- [ ] If updating an existing PRD, keep existing execution status checkboxes (do not reset them).
- [ ] PRD includes `## Execution Status (03-exe)`.
- [ ] PRD Summary includes `Type:`.
- [ ] If the feature has dependencies in `tasks/todo.md`, they are referenced by ID and included in “Dependencies & Constraints”.
- [ ] PRD is consistent with `tasks/memory.md` (or the change is captured via `04-rem`).
- [ ] Goals are measurable and directly tied to success metrics.
- [ ] Non-goals are explicit (prevent scope creep).
- [ ] User stories are checklist items with verifiable acceptance criteria.
- [ ] Requirements are numbered (FR/NFR) and unambiguous.
- [ ] Edge cases, error states, and permissions are specified.
- [ ] Rollout plan and rollback plan exist (if risk warrants it).
- [ ] Saved/updated at the chosen PRD path.
- [ ] If `tasks/todo.md` exists, the feature is checked and links to this PRD.
