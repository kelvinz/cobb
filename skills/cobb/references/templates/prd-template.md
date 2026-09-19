# PRD Template Reference

## Table of Contents

- [Template](#template)
- [Writing Rules](#writing-rules)
- [Progress Updates](#progress-updates)
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
- **Diagnosis source**: `/cobb diagnose` report (loop command and minimal repro) | direct

For a `Type: chore` that restructures code, include:

- **Behaviour pin**: the characterisation test, snapshot, or equivalence harness captured before structure moves, and the command that runs it
- **Equivalence proof**: how old-versus-new behaviour is compared on the real artifact
- **Reader-load target**: the layers or hidden state the reshape removes; the change is reverted if it removes neither

## 2. Goals and Non-Goals

### Goals

- G-001: <measurable outcome>

### Non-goals

- NG-001: <explicit exclusion and why>
- NG-002 (UI changes to an existing screen only; omit otherwise): existing routes, navigation labels, form field names and order, analytics events, the logo, and legal or consent copy stay unchanged; new ones this feature adds are in scope.

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

Function before form: settle the flow, states, copy, and accessibility here before any visual direction. Mark the section `Not applicable` with a reason when the feature has no user-facing surface: no screen people interact with.

### Primary flow

1. ...
2. ...

### State inventory

For every state the feature can reach: what the user sees, what they can do, and how they recover or progress. Mark an unreachable state `Not applicable` with a reason.

- Default: sees ... | can ... | recovers or progresses by ...
- Empty: ...
- Loading: ...
- Partial (some data loaded, some pending or failed): ...
- Error (validation, system, network, permission, timeout): ...
- Success (what happened, and what is next): ...
- Offline (what stays usable; what is queued, rejected, or lost): ...
- Disabled (why, and what makes it available): ...
- Overflow (long text, many items, large numbers): ...
- Permission (no access or a limited role): ...

### Hardening inputs

Each applicable input becomes an acceptance criterion or is marked `Not applicable` with a reason:

- Text length: empty, one character, and very long names, titles, and descriptions: ...
- Character sets: emoji, accents, right-to-left, and CJK text: ...
- Volume: very large numbers, 1,000+ list items, and 50+ options: ...
- Errors: 400, 401, 403, 404, 409, 429, 500, offline, and timeout: ...
- Concurrency: double submits, concurrent edits, and interrupted gestures: ...
- Localisation: text 30 to 40 percent longer, and locale formats for dates, numbers, currency, and plurals: ...

### Copy matrix

For each user-facing text element, in the project language:

- <Element>: default "..." | empty "..." | error "..." | long or overflow "..." | translated: notes or Not applicable

### Accessibility

- Target: WCAG 2.2 AA | other level, with why
- Keyboard/focus behaviour: ...
- Semantic labels and announcements: ...
- Contrast, motion, and non-visual alternatives: ...
- Target size, drag alternatives, authentication, and time limits: ...

### Visual direction

Filled after the sections above are settled; it may stay `Pending /cobb design` while the PRD is otherwise ready.

- Visitor mode: persuade | operate | read | experience
- Change kind: extend | refine | new surface | new identity | redesign
- Direction: <the chosen direction, or inherited from DESIGN.md>, and why
- Overrides to DESIGN.md for this feature: none | ...
- DESIGN.md updates to record after the build: none | ...

## 6. Technical Design

### Existing architecture

- Relevant files and symbols: `path/to/file` — <current responsibility>
- Existing conventions to preserve: ...
- Installed/target versions that constrain the design: ...

### Chosen approach

- Data shape and organising structure: <the core types and the structure that holds the rules: state machine | typed model | table or registry | discriminated union | reducer | plain code, with why>
- Boundaries: <where external data is parsed and validated once; what is trusted inside>
- Alternative shape considered (new interfaces only): <the second structurally distinct sketch and why it lost; see D-###>

Describe control flow, ownership boundaries, and why this is the smallest maintainable design. Apply `references/design-principles.md` and name the principles that shaped the choice.

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
- **Accessibility**: applicable standard (WCAG 2.2 AA by default) and verification
- **Ethics**: dark-pattern check from `references/design/ethics.md` when the feature touches consent, pricing or checkout, subscriptions or trials, cancellation or account deletion, notifications, data collection or sharing, AI decisions that affect users, or products for children | Not applicable

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

- Seams under test (confirmed in interview): `<interface>` — why this seam, existing | new
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

- Door: two-way (cheap to roll back) | one-way (destructive or hard to reverse), with why
- Blast radius: <one phrase> — consumers, layouts, data, or integrations affected if it goes wrong
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

- Use stable IDs consistently; existing IDs keep their numbers across updates.
- Map every acceptance criterion to at least one implementation slice and verification item.
- Name verified repository paths and symbols; line numbers stay out because they go stale.
- Include exact contracts or reusable snippets for difficult logic, not full routine production files.
- Preserve material decision rationale, not the interview transcript.

### Progress Updates

Keep stable IDs and preserve checked items whose requirements, dependencies, and verification evidence remain valid. Reopen items whose requirements changed or whose evidence is no longer valid, along with affected dependent stories/slices. Record why they were reopened; leave unaffected completion intact.

Checklist progress records completed work. `Status` records whether the PRD is ready to implement, not whether implementation is finished. Recalculate it after every update using the Readiness Checklist below; an old `ready` value does not override a newly discovered blocker.

## Acceptance Criteria Example

- Weak: "Export works correctly."
- Strong: `AC-003: Given zero matching rows, when the user selects Export CSV, then the app downloads a UTF-8 CSV containing the configured headers in order and no data rows; an export failure leaves the page usable and exposes one retry action.`

## Readiness Checklist

- [ ] Summary includes a unique `Feature ID` (checked against existing PRDs in `tasks/` and `tasks/archive/`), `Type`, `Status`, `Priority`, dependencies, outcome, and success signal.
- [ ] Scope represents one independently verifiable outcome; child PRDs and dependencies cover independent work.
- [ ] Dependencies reference valid feature IDs.
- [ ] Acceptance criteria are concrete and verifiable.
- [ ] Every major design branch is specified or marked non-applicable with a reason.
- [ ] No high-risk or irreversible question remains unresolved or provisional.
- [ ] Existing architecture, files, symbols, versions, and commands were verified rather than guessed.
- [ ] Difficult contracts and algorithms include usable types, examples, pseudocode, or snippets.
- [ ] Every story and acceptance criterion has stable traceability to an ordered implementation slice and evidence.
- [ ] Behavioural work has vertical RED/GREEN/REFACTOR instructions conforming to `references/tdd.md`.
- [ ] Seams under test are named, user-confirmed, and as few and as high as the behaviour allows.
- [ ] The data shape and its organising structure are named, illegal states are unrepresentable where the design admits variants, and validation sits at the boundary; a new interface has a second structurally distinct sketch recorded as a rejected alternative.
- [ ] A behaviour-preserving `chore` names its behaviour pin, equivalence proof, and reader-load target.
- [ ] A feature with a user-facing surface settles its flow, state inventory, hardening inputs, copy matrix, and accessibility before visual direction; the visual direction block is filled or marked pending `/cobb design`.
- [ ] A change to an existing user-facing surface is classified as extend, refine, or redesign, and its protected items are non-goals unless scoped.
- [ ] Section 7's Ethics line records a passed dark-pattern check, or `Not applicable` with a reason.
- [ ] Each slice fits one fresh agent session; an API replacement migrates callers and deletes the old path in one wave, or, when one wave cannot land green, is sequenced as expand, migrate, contract.
- [ ] Mocks are limited to system boundaries; exceptions are explained.
- [ ] Security, privacy, permissions, performance, reliability, observability, accessibility, migration, rollout, and rollback are addressed.
- [ ] Automated and manual commands, fixtures, expected failures, and completion evidence are explicit.
- [ ] Material decisions include rationale and relevant rejected alternatives.
- [ ] Checked items still have valid evidence; affected items were reopened under Progress Updates, and unaffected completion and settled decisions were preserved.
- [ ] Terms, symbols, and test names use the `## Language` section of `tasks/context.md`; new or sharpened terms were recorded there.
- [ ] PRD is consistent with `tasks/context.md`, or `tasks/context.md` was updated in this run.
- [ ] `Status: ready` appears only when every item above passes or has a documented non-blocking exception.
