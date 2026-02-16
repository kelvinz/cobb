# PRD Template Reference

## Table of contents
- [Template](#template)
- [Acceptance criteria examples](#acceptance-criteria-examples)
- [Quality checklist](#quality-checklist)

## Template

Use this as the default structure for new PRDs. Drop sections only when they truly do not apply.

```markdown
# PRD: <Feature name>

## 0. Summary
- **Feature ID**: f-##
- **Type**: feat | fix | chore
- **Status**: draft | ready
- **Priority**: P0 | P1 | P2 | P3
- **Dependencies**: <none> | f-02, f-10
- **What**: …
- **Why**: …
- **Who**: …
- **Success looks like**: …
- **Assumptions** (if any): …

## 1. Problem / Opportunity
Describe the user pain / opportunity and why now.

### For `Type: fix` items, also include:
- **Current behaviour**: what happens now
- **Expected behaviour**: what should happen
- **Repro steps** (if known): step-by-step to reproduce
- **Suspected root cause** (if known): …
- **Minimal fix approach**: smallest change to resolve
- **Regression tests to add**: what to test to prevent recurrence

## 2. Goals
- G-1: …
- G-2: …

## 3. Non-goals
- NG-1: …
- NG-2: … (may revisit later)

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
Make each story a checklist item so `implement` can execute in pieces and check things off.

- [ ] US-001: <Title>
  - **Description:** As a <user>, I want <capability> so that <benefit>.
  - **Acceptance criteria:**
    - [ ] Specific, verifiable criterion (avoid "works", "correctly", "fast" without numbers)
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
- Feature dependencies: <none> | f-02, f-10
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
For unresolved decisions that need user input, prefer numbered/lettered options so replies can be short (for example: `Q-1` options `A/B/C` and reply `Q1A`).

## 14. Appendix (optional)
- Alternatives considered: …
- Links to mockups/designs: …
```

## Acceptance criteria examples

- Bad: "Export works."
- Good: "When a user clicks **Export CSV**, the app downloads a CSV that includes columns A/B/C in that order; if there are 0 rows, download still occurs with headers only; errors show a non-blocking toast with retry."

## Quality checklist

Before saving the PRD:

- [ ] If a PRD already existed, it was updated in place (no duplicates).
- [ ] If updating an existing PRD, keep existing story/task checkboxes (do not reset them).
- [ ] PRD Summary includes `Type:`, `Status:`, and `Priority:`.
- [ ] If the feature has dependencies, they are referenced by ID and included in "Dependencies & Constraints".
- [ ] PRD is consistent with `tasks/memory.md` (or `tasks/memory.md` was updated in this run).
- [ ] Goals are measurable and directly tied to success metrics.
- [ ] Non-goals are explicit (prevent scope creep).
- [ ] User stories are checklist items with verifiable acceptance criteria.
- [ ] Requirements are numbered (FR/NFR) and unambiguous.
- [ ] Edge cases, error states, and permissions are specified.
- [ ] Open questions that require user decisions use short-reply option formats (for example: `Q1A`).
- [ ] Rollout plan and rollback plan exist (if risk warrants it).
- [ ] Saved/updated at the chosen PRD path.
