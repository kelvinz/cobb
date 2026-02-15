---
name: commit
description: "Create atomic user-approved commits with `feat`/`fix`/`chore` titles. Include inline PRD checklist and memory updates per atomic commit. Finalise branch merge/cleanup when requested. Triggers: commit changes, split commits, finalise branch, commit message."
---

# commit

Commit changes in atomic steps, then finalise and clean up the feature branch when requested.

---

## Guardrails

- Require user confirmation before every commit.
- For every atomic commit proposal, provide a proposed title.
- Provide a proposed body before asking for approval.
- Keep commits atomic; if a title needs "and", split the change set.
- Never mix unrelated files in one commit.
- Determine commit `type` from the actual diff intent, not from branch name, file paths, or habit.
- Never use `chore` for behaviour changes (flow, API/data semantics, bug fixes, or security fixes).
- If a change group contains multiple intents, split it before proposing.
- Examples: `feat` + `fix`, `fix` + `chore`.
- Never add AI attribution or `Co-authored-by` trailers unless the user explicitly asks.
- Do not push to remote without explicit user confirmation.
- Ask for the merge target branch during finalise mode.
- Do not assume `main`; it may be `dev` or another branch.
- Use `review` as a quality gate before commit/finalise when needed.
- Capture memory inline: update `tasks/memory.md` during commit/finalise when durable info appears.
- Do not add a separate memory-only step.
- Keep PRD checklist updates inside the atomic commit that completes that work.
- Never make a trailing commit only to catch up PRD checklist or memory updates.
- In finalise, bundle tracking updates into one pre-merge commit.
- Include PRD archive and memory updates as needed.
- If no tracking changes are needed, skip the finalise commit and state why.
- Use finalise tracking for closeout only.
- Do not retroactively log completed atomic work unless the user explicitly asks.
- Follow the merge strategy resolution order in `references/finalise-policy.md`.
- Never delete the base/default branch.
- Never delete the currently checked-out branch.
- Require explicit user confirmation before deleting local or remote branches.
- Do not claim tests passed or checks succeeded without actually running them; if you didn't run it, say so.

---

## Commit Message Rules

### Title format (required)

`<emoji> <type>: <imperative summary>`

- `type` must be one of: `feat`, `fix`, `chore`
- Summary must be short, specific, and imperative (e.g., "add", "fix", "remove", "refactor")
- Avoid vague summaries like "update code" or "fix stuff"

### Finalise title (required)

For a finalise commit, require:

`🧹 chore: finalise f-## <short-summary>`

Keep the summary short and imperative.

### Emoji mapping (default)

- `feat` → `✨`
- `fix` → `🐛`
- `chore` → `🧹`

Use a different emoji only if it more precisely matches the change.

### Type and body guidance (required)

Use the detailed rubric and templates in `references/commit-rules.md` for:

- selecting `feat` vs `fix` vs `chore`
- classifying mixed-intent diffs
- writing standard commit bodies
- writing finalise commit bodies

Read this reference before proposing the first commit in a session, and revisit it whenever classification is ambiguous.

---

## Modes

- `commit` mode: propose and execute one atomic commit at a time.
- `finalise` mode: merge/close the completed branch and delete feature branches.
- `hotfix` mode: for urgent fixes committed directly to the default branch.
- Requires `review` approval and a `tasks/memory.md` hotfix rationale update.

---

## Workflow

1. Inspect current changes (`git status --short`, `git diff`, `git diff --staged`).
   Identify the active feature PRD when applicable.
2. Partition changes into atomic commit groups and map each group to:
   - PRD checklist/user-story items completed by that group (if any)
   - memory-worthy outcomes produced by that group (if any)
3. For the next group, propose:
   - files/hunks included
   - type rationale (why this is `feat` / `fix` / `chore`, citing concrete diff intent)
   - PRD checklist lines to update in this same commit (or explicit `none` with reason)
   - memory updates to include in this same commit (or explicit `none` with reason)
   - commit title (emoji + type + imperative summary)
   - commit body (Summary/Why/Context/Alternatives/Trade-offs/Consequences)
4. Ask for a decision:
   - `yes`: stage only that group and commit
   - `edit`: revise message/scope and ask again
   - `skip`: leave group uncommitted and move on
   - `split`: break the group into smaller commits and repropose
5. After each accepted commit:
   - commit immediately
   - report commit hash + title + short "what changed" summary
   - propose the next atomic group until done
6. During commit mode, ensure tracking is coupled to the atomic change:
   - include PRD checklist updates for completed stories in that same commit
   - include memory updates only when durable rationale/gotchas emerge from that same commit
   - if no PRD/memory updates are needed for a group, explicitly mark them as `none` with reason

---

## Finalise Mode

Use after all intended commits are done.

1. Confirm preconditions:
   - working tree clean
   - on feature branch (not base)
2. Determine the feature PRD path to finalise:
   - prefer active feature PRD files in `tasks/` matching the feature ID (`tasks/f-##-*.md`)
   - if multiple matches exist or feature ID is unclear, ask the user for the exact path
3. Before merge, prepare tracking updates:
   - if the PRD path matches `tasks/f-##-<slug>.md`, ensure `tasks/archive/` exists
   - move the PRD to `tasks/archive/f-##-<slug>.md` (same filename); if already archived, skip
   - if `tasks/memory.md` exists (or should exist), update it when durable state changed:
     - add completed milestone entry for the finalised feature
     - update "Current state" (next up / blockers) if it changed
     - capture any key decisions or gotchas discovered during completion
   - stage all resulting tracking changes together
   - propose exactly one `🧹 chore: finalise f-## ...` commit (use short finalise body)
   - ask for user confirmation before committing (same yes/edit/skip options as commit mode)
   - if no tracking changes are needed, explicitly state why and skip the finalise commit
   - do not use this finalise commit to catch up missed atomic PRD/memory updates
   - only do that if the user explicitly approves
4. Ask the user to confirm the target branch for merge (for example: `main`, `dev`, `release/*`).
5. Confirm finalise gate before merging:
   - require `review: Good to commit: Yes`; if missing, run `review` before merging
6. Resolve the merge strategy per `references/finalise-policy.md`.
   Present the resolved strategy as a suggestion and let the user confirm or override before merging.
7. Apply branch safety checks before deletion:
   - confirm `<feature-branch>` is not the target branch
   - confirm `<feature-branch>` is not the default branch
   - confirm current HEAD is not `<feature-branch>` when deleting it
8. Delete completed feature branch only after explicit user confirmation:
   - local: `git branch -d <feature-branch>`
   - remote: `git push origin --delete <feature-branch>`

---

## Hotfix Mode

Use for urgent fixes committed directly to the default branch without a feature branch.

1. Confirm on the default branch (not a feature branch).
2. Require `review` approval before committing.
3. Follow the standard atomic commit workflow (steps 1-6 above).
   - PRD checklist: mark as `none` — hotfixes typically have no PRD.
   - Type: use `fix` unless the change is purely non-behavioural (`chore`).
4. Record hotfix rationale in `tasks/memory.md` (what broke, why the hotfix was necessary, follow-up actions).
5. No finalise step needed — already on the default branch.

---

## Output

For each proposed commit, provide:

- atomic scope (files/hunks)
- short "what changed" summary
- type rationale (1-2 lines; evidence-based)
- proposed title
- proposed body
- explicit confirmation prompt (`Commit this change now?`)

After execution, provide:

- created commit hash/title
- short "what changed" summary
- remaining uncommitted groups
- finalise recommendation when all groups are complete
- PRD checklist sync status (`updated` or `none` with reason)
- memory sync status (`updated` or `skipped` with reason)
- End with a short status block:
  - **Files changed**: list of created/updated files
  - **Key decisions**: any assumptions or choices made (if any)
  - **Next step**: recommended next skill or action
