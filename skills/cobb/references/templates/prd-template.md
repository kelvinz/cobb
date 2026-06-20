# PRD Template Reference

## Table of Contents

- [Template](#template)
- [Writing Rules](#writing-rules)
- [Acceptance Criteria Example](#acceptance-criteria-example)
- [Readiness Checklist](#readiness-checklist)

## Template

Use this structure for new PRDs. Keep every major numbered section. When a concern does not apply, write `Not applicable` and give a short reason.

````markdown
# PRD: <Feature name>

## 0. Summary

- **Feature ID**: f-##
- **Type**: feat | fix | chore
- **Status**: draft | ready
- **Priority**: P0 | P1 | P2 | P3
- **Dependencies**: none | f-02, f-10
- **Outcome**: <one observable user or operational outcome>
- **Why now**: <reason and evidence>
- **Primary user**: <specific user or caller>
- **Success signal**: <measurable or directly verifiable result>
- **Implementation shape**: <one-paragraph technical summary grounded in the repository>
- **Unresolved blockers**: none | numbered Q-### items

## 1. Problem and Evidence

Describe the current pain or opportunity, its impact, and the evidence available.

For `Type: fix`, include:

- **Current behaviour**: ...
- **Expected behaviour**: ...
- **Reproduction**: exact steps, inputs, environment, and frequency
- **Root cause**: confirmed cause, or bounded hypotheses and how to distinguish them
- **Regression surface**: related paths that must remain unchanged

## 2. Goals and Non-Goals

### Goals

- G-001: <measurable outcome>

### Non-goals

- NG-001: <explicit exclusion and why>

## 3. Users, Permissions, and Scenarios

- **Primary user**: ...
- **Secondary users/callers**: ...
- **Roles and permissions**: ...
- **Assumptions about user state**: ...

### Scenarios

- SC-001: <happy-path scenario>
- SC-002: <failure, recovery, or boundary scenario>

## 4. Scope and Behaviour

### User stories

- [ ] US-001: <title>
  - **As a** ...
  - **I want** ...
  - **So that** ...
  - **Covers scenarios**: SC-001
  - **Acceptance criteria**: AC-001, AC-002

### Acceptance criteria

- [ ] AC-001: Given <state>, when <action>, then <observable result>.
- [ ] AC-002: Given <failure or boundary>, when <action>, then <observable recovery/error result>.

### Business rules

- BR-001: <unambiguous rule, precedence, and boundary values>

## 5. Experience and State Model

### Primary flow

1. ...
2. ...

### States

- Initial/empty: ...
- Loading/in progress: ...
- Success: ...
- Partial success: ...
- Error: ...
- Retry/recovery: ...

### Accessibility

- Keyboard/focus behaviour: ...
- Semantic labels and announcements: ...
- Contrast, motion, and non-visual alternatives: ...

## 6. Technical Design

### Existing architecture

- Relevant files and symbols: `path/to/file` — <current responsibility>
- Existing conventions to preserve: ...
- Installed/target versions that constrain the design: ...

### Chosen approach

Describe control flow, ownership boundaries, and why this is the smallest maintainable design.

### Files and symbols

- `path/to/file`
  - Change `<symbol>` to ...
  - Add `<symbol>` with input/output contract ...
- `path/to/new-file`
  - Purpose and public surface ...

### Interfaces and contracts

```ts
// Include exact types, signatures, request/response examples, or pseudocode
// when they remove ambiguity. Omit routine implementation syntax.
```

### Data and persistence

- Schema/model changes: ...
- Validation and invariants: ...
- Migration/backfill: ...
- Compatibility and rollback: ...

### External integrations and sources

- System/API and boundary adapter: ...
- Failure, timeout, retry, and idempotency behaviour: ...
- Authoritative source: <versioned documentation link and resulting constraint>

## 7. Quality Attributes

- **Security/privacy**: validation, authorisation, sensitive data, abuse cases
- **Performance**: workload, limits, latency/budget, measurement method
- **Reliability**: failure containment, retries, consistency, recovery
- **Observability**: structured logs, metrics, traces, alerts; exclude secrets/PII
- **Accessibility**: applicable standard and verification

## 8. Implementation Plan

Execute in dependency order. Each slice must produce an independently verifiable behaviour and an atomic commit group.

### SL-001: <behavioural tracer slice>

- **Requirements**: US-001, AC-001, BR-001
- **Depends on**: none
- **Files/symbols**: `path/to/file#symbol`
- **RED**: add `<test name>` in `path/to/test`; expected failure is ...
- **GREEN**: implement the minimum behaviour by ...
- **REFACTOR**: permitted cleanup within touched scope ...
- **Edge cases**: ...
- **Commands**: `<focused test command>`
- **Completion evidence**: exact passing assertion/output and manual observation, if any
- [ ] Slice complete

### SL-002: <next behaviour>

- **Requirements**: ...
- **Depends on**: SL-001
- **Files/symbols**: ...
- **RED**: ...
- **GREEN**: ...
- **REFACTOR**: ...
- **Edge cases**: ...
- **Commands**: ...
- **Completion evidence**: ...
- [ ] Slice complete

## 9. Testing and Verification

This section is the approved TDD contract for behavioural `feat` and `fix` work; implementation should execute it without a second planning interview.

### Test strategy

- Public interfaces under test: ...
- Integration tests: ...
- Focused unit tests for complex pure logic: ...
- Real controlled dependencies: ...
- Mocked system boundaries and why: ...
- Fixtures/data setup and cleanup: ...

### Behaviour coverage

- AC-001 -> `<test name>` in `path/to/test` -> automated command/evidence
- AC-002 -> `<test name or manual case>` -> evidence

### Commands

- Focused test: ...
- Full regression suite: ...
- Typecheck/lint/build: ...
- Manual QA: exact steps and expected results

### TDD exception, if any

- Behaviour without practical automation: ...
- Justification: ...
- Risk: ...
- Repeatable manual verification: ...
- Testability follow-up: none | ...

## 10. Rollout, Migration, and Recovery

- Feature flag or compatibility strategy: ...
- Deployment/migration order: ...
- Progressive rollout and monitoring: ...
- Rollback trigger and exact rollback steps: ...
- Data recovery implications: ...

## 11. Analytics and Success Evaluation

- Metric/event and owner: ...
- Baseline and target: ...
- Evaluation window: ...
- How to distinguish success from unrelated effects: ...

## 12. Risks and Mitigations

- R-001: <risk>
  - Likelihood/impact: ...
  - Prevention: ...
  - Detection: ...
  - Recovery: ...

## 13. Decisions and Alternatives

- D-001: <decision>
  - **Chosen**: ...
  - **Why**: ...
  - **Alternatives rejected**: ...
  - **Trade-offs/consequences**: ...
  - **Source/evidence**: repository finding or authoritative versioned link

## 14. Open Questions

- Q-001: <blocking question>
  - `0` **Recommended:** ...
  - `1` ...
  - `2` Custom answer
  - **Blocks**: status ready | SL-### | rollout | other

Use `None` when all questions are resolved. A PRD with a high-risk or irreversible unresolved question cannot be `ready`.

## 15. Readiness Record

- **Interview confirmation**: confirmed | pending
- **Interview progress**: <answered>/<total> questions resolved
- **Codebase exploration**: files/areas inspected
- **External research**: none | sources and versions checked
- **Requirement-to-slice traceability**: complete | gaps
- **Verification coverage**: complete | justified gaps
- **Ready rationale**: why a less-capable agent can implement without product/design decisions
````

## Writing Rules

- Use stable IDs consistently; do not renumber existing IDs during updates.
- Map every acceptance criterion to at least one implementation slice and verification item.
- Name verified repository paths and symbols. Do not invent line numbers or structures.
- Include exact contracts or reusable snippets for difficult logic, not full routine production files.
- Preserve material decision rationale, not the interview transcript.
- Keep existing checked items checked when updating a PRD.

## Acceptance Criteria Example

- Weak: "Export works correctly."
- Strong: `AC-003: Given zero matching rows, when the user selects Export CSV, then the app downloads a UTF-8 CSV containing the configured headers in order and no data rows; an export failure leaves the page usable and exposes one retry action.`

## Readiness Checklist

- [ ] Summary includes unique `Feature ID`, `Type`, `Status`, `Priority`, dependencies, outcome, and success signal.
- [ ] Scope represents one independently verifiable outcome; child PRDs and dependencies cover independent work.
- [ ] Every major design branch is specified or marked non-applicable with a reason.
- [ ] No high-risk or irreversible question remains unresolved or provisional.
- [ ] Existing architecture, files, symbols, versions, and commands were verified rather than guessed.
- [ ] Difficult contracts and algorithms include usable types, examples, pseudocode, or snippets.
- [ ] Every story and acceptance criterion has stable traceability to an ordered implementation slice and evidence.
- [ ] Behavioural work has vertical RED/GREEN/REFACTOR instructions conforming to `references/tdd.md`.
- [ ] Mocks are limited to system boundaries; exceptions are explained.
- [ ] Security, privacy, permissions, performance, reliability, observability, accessibility, migration, rollout, and rollback are addressed.
- [ ] Automated and manual commands, fixtures, expected failures, and completion evidence are explicit.
- [ ] Material decisions include rationale and relevant rejected alternatives.
- [ ] Existing checklist state and settled decisions were preserved during updates.
- [ ] `Status: ready` appears only when every item above passes or has a documented non-blocking exception.
