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
- Use checklists and bullets for structure; Markdown tables are reserved for the router.
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
   - Resolve answerable questions from evidence and record the evidence-backed recommendation.
   - Use authoritative documentation for unstable or unfamiliar external contracts; record the relevant version, link, and resulting constraint in the PRD.
5. **Build and walk the design tree:**
   - Cover product outcome, users, scope, flows, states, data, APIs, permissions, security/privacy, accessibility, performance, reliability, observability, migrations, rollout/rollback, and verification.
   - Mark a branch non-applicable only with a short reason.
   - Resolve prerequisite decisions before dependent decisions.
   - Build the question tree and ask it in frontier rounds using the shared interview format (see Interview Protocol).
   - When a design question needs a runnable answer (a state model that is hard to reason about on paper, or a UI that must be seen), build a throwaway prototype outside the product code, fold the verdict into a `D-###` entry with the snippet trimmed to the decision, and keep the prototype out of the PRD.
   - If the user cannot decide, apply a labelled provisional recommendation only when the choice is reversible and low-risk.
   - Keep high-risk or irreversible unresolved choices open and leave the PRD in `draft`.
6. **Split oversized ideas when needed:**
   - Split by independently verifiable outcomes and dependency boundaries, not arbitrary file, subsystem, or duration limits.
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
   - Include production-ready snippets or pseudocode for difficult logic, but leave routine syntax to the implementer.
   - Map stable requirement and acceptance-criterion IDs to ordered vertical implementation slices and verification evidence.
   - For behavioural `feat` and `fix` work, read `references/tdd.md` and include its complete PRD testing contract.
   - For UI/UX-heavy features, state whether design direction is needed before implementation and name the expected design inputs.
10. **Run the readiness gate:**
   - Audit the written PRD against the Readiness Checklist in `references/templates/prd-template.md`.
   - Downgrade to `draft` if any blocking detail remains, even if the user previously expected `ready`.
11. **Update context:**
   - Update project gist in `tasks/context.md` if this is the first PRD or project scope changed.
   - Capture any durable decisions or constraints.
12. **Reply** with updated file paths, status, readiness result, and a short change summary.

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
- Avoid implementation tasks ("refactor", "set up DB") unless they are truly user-facing requirements.
- If a feature is too large, split by user goal or workflow step until each item could reasonably become a single PRD.
- Specify the chosen technical approach and why it fits existing architecture.
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
