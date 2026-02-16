---
name: compact
description: "Compact `tasks/memory.md` by summarising older completed history while preserving active context. Triggers: compact memory, prune memory log, trim memory."
---

# compact

Keep `tasks/memory.md` short and scannable by consolidating older entries into readable summaries.

---

## Guardrails

- Do not change product scope or implementation code.
- Do not move or rename PRDs here; completed PRDs are archived during `commit` finalise.
- Do not create separate memory archive files.
- Ask for explicit confirmation before applying consolidation edits.
- Always propose retention/consolidation counts first; let the user choose the final numbers.
- When asking for user decisions, provide numbered short-reply options.

---

## Workflow

1. Preflight:
   - Ensure `tasks/` exists.
   - Inspect `tasks/memory.md`.
   - Count items to compact:
     - `memory`: entries in `Key decisions`, `Completed`, `Notes / gotchas`
2. Propose consolidation options and ask for a decision:
   - Suggest how many entries to keep in full detail vs consolidate into summary.
   - Provide recommended defaults, then allow user override (more or fewer).
3. Compact `tasks/memory.md` in place:
   - Preserve `Project` and `Current state` sections.
   - Keep the user-selected number of most recent detailed entries (entries are newest-first, so keep from the top).
   - Before consolidating, extract still-relevant risks, open questions, or gotchas
     from older entries (bottom of each section).
   - Move them into `Notes / gotchas` or `Current state: Blockers` so they are not lost.
   - Replace older entries with a concise historical summary block appended at the bottom of each section.
4. Report results:
   - Show retained vs consolidated counts.
   - Call out any sections intentionally left untouched.

---

## Suggested Defaults

Use these as initial recommendations, then ask the user to confirm or adjust:

- `tasks/memory.md`:
  - Keep the latest 10 entries in detail across historical sections.
  - Consolidate older entries into summary.

---

## Prompt Format for Threshold Choice

Use a short choice prompt before edits:

```text
Proposed compact plan:
- Memory detailed entries to keep: 15 (consolidate: 41)

Reply with:
- `1` for "use defaults", or
- `2 <n>` for custom number (for example: `2 20`), or
- `3` for "less", `4` for "more".
```

---

## Summary Patterns

### `tasks/memory.md` historical-summary example

```markdown
## Historical summary
- Earlier phase focused on onboarding, auth hardening, and export reliability.
- Main recurring risk was cross-feature dependency ordering; mitigated by stricter finalise discipline.
- Key tradeoff pattern: shipped simpler defaults first, then expanded configurability.
```

---

## Output

- Update only `tasks/memory.md`.
- Return:
  - proposed numbers and user-selected numbers
  - retained vs consolidated counts
  - concise summary of what changed
- End with a short status block:
  - **Files changed**: list of created/updated files
  - **Key decisions**: any assumptions or choices made (if any)
  - **Next step**: recommended next skill or action
