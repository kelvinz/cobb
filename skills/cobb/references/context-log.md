# context

Maintain `tasks/context.md` as shared work state: what was decided, where the work stands, and what affects the next step.

Apply this workflow inline during file-writing phases or directly for `/cobb context` backfill/cleanup. Read-only review proposes entries for the repair/finalise workflow.

Shared guardrails from the cobb router apply; the rules below are context-specific.

---

## Guardrails

- Secrets (API keys, tokens, credentials) stay out of this file.
- Keep entries short and durable; reference PRDs and code instead of copying them.
- Update `tasks/context.md` in place, section by section.
- During `review`, report proposed entries and associate each with a blocker, suggestion, or finalise candidate; review leaves this file unchanged.

## Task Records and Agent Memory

- PRDs hold the requirements and progress for each feature.
- `tasks/context.md` holds shared work facts: current state, agreed product/technical decisions, repository conventions, milestones, and technical constraints. Reference PRDs rather than copying their contents.
- Agent memory holds learned user preferences and corrections about how the agent should work. The repo-root `AGENTS.md` says whether and where that memory may be saved; when it is absent or silent, save no agent memory. Task files are never a memory store.

For example, an API's UTC-only date contract belongs in task context. A repeated correction about the agent's reply style belongs under the memory policy, not in task context. Keep work decisions, not chat transcripts or agent self-improvement notes. If `AGENTS.md` also restricts task records, follow that restriction.

---

## What to Record

- Project gist (what it is, who it's for, success measures) → `## Project`
- Repo conventions the skill reads back (default base, base branches beyond the defaults, merge preference) → `## Project`, on the `Repo conventions` line
- Project language: one canonical term per concept specific to this project, a one or two sentence definition of what it is, and the synonyms to avoid → `## Language`. Be opinionated: pick the best word and retire the others. General programming concepts stay out. Every phase names symbols, tests, and messages from this section.
- Current state (what's done, what's next, what's blocked) → `## Current state`
- Key decisions and durable design decisions (what we chose + why + tradeoffs) → `## Key decisions`
- Completed work (feature IDs and notable outcomes) → `## Completed`
- Notes/gotchas (constraints, pitfalls, conventions, sharp edges) → `## Notes / gotchas`
- Optional context links (canonical docs, API specs, repos) → `## Links (optional)`

Avoid:

- raw meeting transcripts
- verbose day-by-day logs
- duplicate content that already lives in PRDs or code

---

## Links Format

- Only add `## Links (optional)` when links materially improve handoff context.
- Format: `[Label](path-or-url) — why this helps future context`
- Prefer durable references (design docs, API specs, runbooks, repos); avoid ephemeral links (temp chats, preview URLs).
- De-duplicate by updating existing entries instead of adding near-identical links.

---

## Workflow

1. Ensure `tasks/` exists; create `tasks/context.md` if missing.
   - Use `references/templates/context-template.md` as the default file template when creating it.
2. Add short entries (1–3 lines) in the most relevant section.
3. Prepend new entries at the top of each section (newest-first order).
4. Prefer referencing stable feature IDs (`f-##`) over PRD file paths (PRD paths change after archiving/compaction). Durable non-PRD links belong in `## Links (optional)`.
5. If a link materially improves context, add or update entries in `## Links (optional)` using the links format.
6. Check README freshness: if the change affects setup, commands, workflows, structure, or scope documented in the root or a touched directory's `README.md`, update the affected sections in the same pass. Review proposes these updates instead. Skip when nothing applies.
7. If an important work decision remains unclear, ask for that decision; otherwise omit information that does not meet the recording rules.

---

## References

- `references/templates/context-template.md`: default structure for creating `tasks/context.md`.

---

## Output

- Create or update `tasks/context.md`.
- Note any README sections updated (or proposed, during `review`) alongside the context update.
- **Inline** (from another phase): reply with a short summary of what was added/updated. Let the calling phase's output format take precedence.
- **Standalone** (`/cobb context`): report the file path and a short summary.
