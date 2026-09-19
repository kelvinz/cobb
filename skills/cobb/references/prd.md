# prd

Create, update, or list implementation-ready PRDs. Each PRD must let a less-capable implementation agent execute the work without rediscovering product or technical decisions.

Shared guardrails from the cobb router apply; the rules below are PRD-specific.

## Guardrails

- Write PRDs only; implementation belongs to `implement`.
- Keep features PRD-sized by independently verifiable user outcome and dependency boundary.
- Allow a coherent cross-layer vertical slice when the outcome requires UI, API, and data changes together.
- Fully understand an oversized idea, then propose a dependency-ordered PRD breakdown before writing files.
- For new PRDs, interview exhaustively until every material branch of the design tree is resolved.
- For updates, audit completeness and interview only implementation-critical gaps.
- Maintain the full dependency tree internally. Show a short resolved/current/remaining summary only when moving to a major branch.
- If an earlier answer changes, invalidate and revisit only downstream decisions that depend on it.
- Use the project language from `tasks/context.md` for every term, symbol, and test name; sharpen fuzzy terms as they appear (see Interview Protocol).
- Use checklists and bullets for structure; Markdown tables are reserved for the router.
- A user-facing surface means a screen people interact with: web, mobile, or desktop UI. APIs, CLIs, libraries, and background jobs are not surfaces; their PRDs skip the UX-layer steps and mark section 5 `Not applicable`.
- Preserve material decisions, rationale, trade-offs, and rejected alternatives; the interview transcript itself stays out of the PRD.

---

## Modes

- **Create / update** (default): write or revise a single PRD.
- **List**: scan `tasks/` for active (non-archived) PRDs and display a summary of feature ID, name, status, and priority. No file modifications.

---

## Workflow — Create / Update

1. **Determine intent:**
   - **New project** (no `tasks/context.md` or empty): ask project-definition questions, initialise `tasks/context.md` with project gist, then write the first PRD.
   - **New PRD** (project exists): proceed to PRD creation.
   - **Update existing PRD**: locate the existing PRD file and edit in place.
   - **Fix with an unknown cause**: when the bug's root cause is neither confirmed nor reducible to bounded hypotheses, load `references/diagnose.md` with caller `prd` and run it now, without a separate prompt. Its Diagnosis Report supplies the Reproduction, Root cause, Regression surface, and first RED slice. Continue here with that report.
2. **Read context:**
   - If `tasks/context.md` exists, skim project gist, key decisions, and notes/gotchas.
   - Avoid conflicts with prior decisions.
3. **Assign feature ID:**
   - Scan existing PRD files in `tasks/` and `tasks/archive/` for the highest `f-##` number.
   - Establish `(max existing f-##) + 1` as the next available ID, and assign the remaining IDs once any multi-PRD breakdown is confirmed.
   - A single new PRD gets the next available ID.
   - For updates, preserve the existing ID.
4. **Explore before interviewing:**
   - Inspect repository structure, conventions, relevant implementation, tests, configuration, and installed dependency versions.
   - For a feature with a user-facing surface, find how the app runs and is checked. When `tasks/context.md` has no verification recipe, record one under the rules in `references/context-log.md`.
   - Resolve answerable questions from evidence and record the evidence-backed recommendation.
   - Use authoritative documentation for unstable or unfamiliar external contracts; record the relevant version, link, and resulting constraint in the PRD.
5. **Build and walk the design tree:**
   - Cover product outcome, users, scope, flows, states, data, APIs, permissions, security/privacy, accessibility, performance, reliability, observability, migrations, rollout/rollback, seams under test, and verification.
   - Mark a branch non-applicable only with a short reason.
   - Resolve prerequisite decisions before dependent decisions.
   - Build the question tree and ask it in frontier rounds using the shared interview format (see Interview Protocol).
   - Treat the test seams as a decision the user confirms: name the public interfaces the tests will cross, prefer existing seams over new ones, place any new seam as high as it can go, and keep the count small (one is the ideal). Record the confirmed seams in section 9 of the PRD.
   - For a feature with a user-facing surface, settle the UX layer in the interview, function before form: the task flow, the state inventory, the copy for key states, and accessibility. Write the copy under UX Copy in `references/design/ux.md`. Visual direction may stay open for `/cobb design`; the flow may not.
   - When the feature touches consent, pricing or checkout, subscriptions or trials, cancellation or account deletion, notifications, data collection or sharing, AI decisions that affect users, or products for children, run the dark-pattern check in `references/design/ethics.md` and resolve every match before `ready`.
   - When a design question needs a runnable answer (a state model that is hard to reason about on paper, or a UI that must be seen), choose the artifact that matches the decision under Artifacts by Decision in `references/design.md`, build it outside the product code, fold the verdict into a `D-###` entry with the snippet trimmed to the decision, and keep the prototype out of the PRD.
   - If the user cannot decide, apply a labelled provisional recommendation only when the choice is reversible and low-risk.
   - Keep high-risk or irreversible unresolved choices open and leave the PRD in `draft`.
6. **Split oversized ideas when needed:**
   - Split by independently verifiable outcomes and dependency boundaries, not arbitrary file, subsystem, or duration limits.
   - Replace an internal API by migrating every caller and deleting the old path in one wave (see `references/design-principles.md`). The exception is a **wide refactor**: one mechanical change whose blast radius spans the codebase so far that one wave cannot land green, such as renaming a column or retyping a shared symbol. Sequence it as expand, migrate, contract: add the new form beside the old, migrate call sites in batches sized by blast radius with each batch its own slice or PRD, then delete the old form once no caller remains. Every step stays green.
   - Resolve shared decisions once, then interview only child-specific gaps.
   - Present the numbered breakdown and dependency order for confirmation.
   - Assign consecutive new feature IDs in dependency order after confirmation.
   - Create all approved child PRDs by repeating the path, write, readiness, and context steps for each; independent work gets its own PRD.
7. **Confirm shared understanding:**
   - Present a concise scope, decisions, assumptions, PRD breakdown, and unresolved-items summary.
   - Require confirmation before writing or materially rewriting PRDs: write the confirmed PRD set, revise a specific decision, or stop without writing.
8. **Determine PRD file path:**
   - Look for an existing active PRD matching the feature ID in `tasks/` (`tasks/f-##-*.md`).
   - If found, use it (update in place).
   - Otherwise use `tasks/f-##-<feature-slug>.md`.
9. **Write or update the PRD** at the chosen path using `references/templates/prd-template.md`:
   - Set `Status:` and `Priority:` in the Summary section.
   - Set `Status: ready` only when every implementation-blocking decision is resolved and the readiness checklist passes.
   - Otherwise set `Status: draft` and number each unresolved item.
   - `Priority:` uses P0 (critical), P1 (high), P2 (medium), P3 (low).
   - Ensure implementation progress is trackable via checklist items.
   - Ground the technical design in actual files, symbols, interfaces, schemas, and repository commands.
   - Read `references/design-principles.md` before writing section 6; name the data shape and its organising structure first, and sketch a second structurally distinct shape for any new interface before choosing.
   - For a `chore` that restructures code, read the Behaviour-Preserving Changes contract in `references/tdd.md` and fill the behaviour pin, equivalence proof, and reader-load target.
   - Include production-ready snippets or pseudocode for difficult logic, but leave routine syntax to the implementer.
   - Map stable requirement and acceptance-criterion IDs to ordered vertical implementation slices and verification evidence.
   - Size each slice to fit one fresh agent session with room to spare; split a slice that would not.
   - When a small preparatory refactor would make the feature slices simpler, make it the first slice (`prefactor`): make the change easy, then make the easy change. It is behaviour-preserving, covered by existing tests, and lands green on its own.
   - For behavioural `feat` and `fix` work, read `references/tdd.md` and include its complete PRD testing contract.
   - For a feature with a user-facing surface, fill section 5: the state inventory, hardening inputs, copy matrix, and accessibility target. Each applicable hardening input becomes an acceptance criterion or is marked not applicable with a reason.
   - For a change to an existing user-facing surface, classify it as extend, refine, or redesign under `references/design.md`, and add its protected items as non-goals.
   - For UI/UX-heavy features, fill the visual direction block or mark it pending `/cobb design`, and name the expected design inputs.
10. **Run the readiness gate:**
   - Audit the written PRD against the Readiness Checklist in `references/templates/prd-template.md`.
   - Downgrade to `draft` if any blocking detail remains, even if the user previously expected `ready`.
11. **Update context:**
   - Update project gist in `tasks/context.md` if this is the first PRD or project scope changed.
   - Capture any durable decisions or constraints.
12. **Reply** with updated file paths, status, readiness result, and a short change summary. When `design` called this phase, return to it with the PRD path instead of ending the phase.

---

## Workflow — List

1. Scan `tasks/` for files matching `f-##-*.md` (exclude `tasks/archive/`).
2. For each file, extract from the Summary section: Feature ID, name, Type, Status, Priority.
3. Display sorted by priority (P0 first), then by feature ID.
4. Suggest the highest-priority `Status: ready` PRD as the next candidate for `/cobb implement`.

---

## Interview Protocol

Resolve the design-tree gaps from the workflow, including feature type, priority, and dependencies. Finding facts is your job: look up repository facts, versions, and documentation yourself, and ask the user only about decisions with valid, safe alternatives. Classify a fork before asking: if the answer is observable by running something (behaviour, timing, output, layout, performance), it is a fact, and a prototype or a run settles it; reserve questions for product or preference calls no experiment can settle. A recommendation is a judgment, not validation: when the evidence says the feature or a branch of it does not earn its place, `0 — Recommended` may be to drop or defer it, with the reason.

Ask in **rounds**. A round holds the whole frontier: every question whose prerequisites are settled. Each answer reshapes the tree, so recompute the frontier before the next round. A question that depends on another question in the same round belongs to the next round. Announce the total and the revised total after any change.

Keep the project language sharp while you go:

- when the user's term conflicts with the `## Language` section of `tasks/context.md`, say so and ask which meaning holds
- when a term is vague or overloaded ("account" meaning both Customer and User), propose one canonical term and list the others under `_Avoid_`
- when the user states how something works, check whether the code agrees and surface any contradiction
- record each resolved term in `tasks/context.md` as it lands, not at the end

### Round format

```text
Round 2 (Questions 3 to 5 of 11)

Question 3 of 11: What outcome should this change optimise for?
0. **Recommended:** Reduce checkout abandonment; this matches the stated user problem and existing funnel metrics.
1. Reduce support workload.
2. Increase average order value.
3. Custom answer: describe the outcome.

Question 4 of 11: Which seam do the tests cross?
0. **Recommended:** The existing `checkoutService` interface; it already has integration tests and covers the full path.
1. A new HTTP-level seam through the checkout route.
2. Custom answer.

Question 5 of 11: ...
```

Reply with `3:0 4:1 5:2` or one number per line, in question order.

---

## Feature Writing Guidelines

- Prefer feature names as verb phrases (e.g., "Invite teammates", "Export CSV").
- For fix items, name them clearly (e.g., "Fix <problem>") and set `Type: fix`. Include minimal bug info:
  - Current behaviour: …
  - Expected behaviour: …
  - Repro steps (if known): …
- For chores, keep them crisp and outcome-oriented (e.g., "Chore: remove dead code") and set `Type: chore`.
- Ensure each feature has a crisp outcome (what changes for the user).
- Frame each feature as a user-facing requirement; an implementation task ("refactor", "set up DB") becomes a `prefactor` slice or a `chore` only when it stands on its own.
- If a feature is too large, split by user goal or workflow step until each item could reasonably become a single PRD.
- Specify the chosen technical approach and why it fits existing architecture.
- Record a decision in section 13 when it is hard to reverse, surprising without context, or the result of a real trade-off; the obvious choice needs no entry.
- Record rejected approaches only when their trade-offs help prevent implementation drift.
- Prefer exact contracts and examples over adjectives such as "robust", "fast", or "secure".

---

## Update Rules (When a PRD Exists)

- Update the existing PRD in place, retaining its feature ID.
- Preserve `Priority:` unless the user asks to change it.
- Apply Progress Updates and the Readiness Checklist in `references/templates/prd-template.md` to checklist state and `Status:`. Report any reopened items or status change and why.

---

## PRD Template

Use `references/templates/prd-template.md` as the default PRD template and checklist.

- Read it before creating or updating a PRD.
- For updates, audit the whole document for implementation-critical gaps and edit the affected sections under its progress rules.
- Keep acceptance criteria concrete and verifiable; examples are in the reference file.

---

## Output

- Create or reuse `tasks/`.
- Save/update the PRD at the chosen path.
- Update `tasks/context.md` when durable decisions or project scope changes warrant it.
- For UI/UX-heavy PRDs, recommend `/cobb design` (optional) before `/cobb implement`.
- Suggest the next action:
  - If `Status: draft`, recommend resolving its named blockers.
  - If `Status: ready`, recommend design direction or implementation from the PRD's needs.
