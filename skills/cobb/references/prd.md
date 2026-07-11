# prd

Create, update, or list implementation-ready PRDs. Each PRD must let a less-capable implementation agent execute the work without rediscovering product or technical decisions.

Shared guardrails from the cobb router apply; the rules below are PRD-specific.

---

## Guardrails

- Do not implement code.
- Keep features PRD-sized by independently verifiable user outcome and dependency boundary.
- Allow a coherent cross-layer vertical slice when the outcome requires UI, API, and data changes together.
- Fully understand an oversized idea, then propose a dependency-ordered PRD breakdown before writing files.
- For new PRDs, interview exhaustively until every material branch of the design tree is resolved.
- For updates, audit completeness and interview only implementation-critical gaps.
- Ask one question at a time. Do not batch questions.
- After exploration, state the planned total and label every prompt `Question X of Y`.
- If an answer changes the dependency tree, announce the revised total and reason before the next question.
- Explore the codebase instead of asking questions it can answer. Consult authoritative, version-relevant documentation when external APIs, libraries, or standards constrain the design.
- For each user question, provide a recommended answer with reasoning.
- Use `0` for the recommendation, `1..N` for alternatives, and a final numbered custom-answer option.
- Maintain the full dependency tree internally. Show a short resolved/current/remaining summary only when moving to a major branch.
- If an earlier answer changes, invalidate and revisit only downstream decisions that depend on it.
- Use plain language, explicit edge cases, and verifiable acceptance criteria.
- Do not use Markdown tables (use checklists + bullets).
- If durable decisions are made, update `tasks/context.md` in this step (do not defer to a separate pass).
- Do not preserve the interview transcript. Preserve material decisions, rationale, trade-offs, and rejected alternatives.

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
   - Establish `(max existing f-##) + 1` as the next available ID, but do not assign all new IDs until any multi-PRD breakdown is confirmed.
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
   - Build the initial question queue, state its total, and track progress as `Question X of Y`.
   - Ask one question at a time using the `0`-recommended numeric format.
   - If the user cannot decide, apply a labelled provisional recommendation only when the choice is reversible and low-risk.
   - Keep high-risk or irreversible unresolved choices open and leave the PRD in `draft`.
6. **Split oversized ideas when needed:**
   - Split by independently verifiable outcomes and dependency boundaries, not arbitrary file, subsystem, or duration limits.
   - Resolve shared decisions once, then interview only child-specific gaps.
   - Present the numbered breakdown and dependency order for confirmation.
   - Assign consecutive new feature IDs in dependency order after confirmation.
   - Create all approved child PRDs by repeating the path, write, readiness, and context steps for each; do not hide independent work inside one oversized PRD.
7. **Confirm shared understanding:**
   - Present a concise scope, decisions, assumptions, PRD breakdown, and unresolved-items summary.
   - Require numbered user confirmation before writing or materially rewriting PRDs:
     - `0` **Recommended:** write the confirmed PRD set
     - `1`: revise a specific decision
     - `2`: stop without writing
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
   - For UI/UX-heavy features, include expected design inputs and state whether `design` should run before `implement`.
10. **Run the readiness gate:**
   - Audit the written PRD against the Quality Checklist and template traceability rules.
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
5. No file modifications in list mode.

---

## Interview Protocol

Ask as many high-value questions as needed for shared understanding, but exactly one per turn. Derive and announce the initial total after codebase exploration; do not invent a total before dependencies are understood.

Focus on ambiguity around:

- target user + primary use case
- the problem + desired outcome
- constraints (platforms, timeline, integrations)
- success metrics / how we know it worked
- scope boundaries (what's explicitly in vs out)
- whether this is `Type: feat` vs `fix` vs `chore`
- priority (P0 / P1 / P2 / P3)
- dependencies between features (by ID)

Do not ask about repository facts that can be discovered locally. Do not ask the user to choose between technically invalid or unsafe options.

### Question format

```text
Question 3 of 11: What outcome should this change optimise for?

0. **Recommended:** Reduce checkout abandonment; this matches the stated user problem and existing funnel metrics.
1. Reduce support workload.
2. Increase average order value.
3. Custom answer: describe the outcome.
```

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

- If a PRD already exists at that path, update it in place.
- Do not create a duplicate PRD unless the user asks.
- Do not reset existing checklist items inside the PRD.
- Preserve existing `Status:` and `Priority:` unless the user explicitly asks to change them.
- Keep feature IDs stable; IDs must be globally unique across `tasks/` and `tasks/archive/`.
- When adding a new feature, use the next ID as `(max existing f-##) + 1` (never reuse old IDs).

---

## PRD Template

Use `references/templates/prd-template.md` as the default PRD template and checklist.

- Read it before drafting a new PRD.
- For updates to an existing PRD, audit the whole document for implementation-critical gaps, edit the affected sections, and preserve existing checkbox state and settled decisions.
- Keep acceptance criteria concrete and verifiable; examples are in the reference file.

---

## Output

- Create or reuse `tasks/`.
- Save/update the PRD at the chosen path.
- Update `tasks/context.md` when durable decisions or project scope changes warrant it.
- For UI/UX-heavy PRDs, recommend `/cobb design` (optional) before `/cobb implement`.
- Suggest the next action:
  - If `Status: draft`, recommend refining to `ready` and provide numbered continue/stop choices.
  - If `Status: ready`, recommend `design` or `implement` from the PRD's needs and provide numbered choices.
- End with the shared status block (Files changed / Key decisions / Next step).

---

## Quality Checklist

Before saving:

- [ ] PRD Summary includes `Feature ID`, `Type`, `Status`, and `Priority`.
- [ ] Feature ID is unique and stable (checked against existing PRDs in `tasks/` and `tasks/archive/`).
- [ ] If updating an existing PRD, existing story/task checkboxes were preserved (not reset).
- [ ] If a PRD already existed, it was updated in place (no duplicates).
- [ ] Each feature has a user-visible outcome and explicit scope boundaries (goals + non-goals).
- [ ] Dependencies reference valid feature IDs.
- [ ] Acceptance criteria are concrete and verifiable.
- [ ] Every major design-tree concern was addressed or marked non-applicable with a reason.
- [ ] Technical guidance names verified files/symbols/contracts and does not guess repository structure.
- [ ] Difficult logic includes usable pseudocode or code where it reduces implementation ambiguity.
- [ ] Stable IDs trace stories and criteria through implementation slices and verification evidence.
- [ ] Behavioural work includes the complete `references/tdd.md` contract or a justified exception.
- [ ] No high-risk or irreversible decision remains provisional.
- [ ] `Status: ready` is used only when all implementation blockers are resolved.
- [ ] PRD is consistent with `tasks/context.md` (or `tasks/context.md` was updated in this run).
