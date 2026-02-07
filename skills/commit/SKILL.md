---
name: commit
description: "Create atomic commits with explicit user approval, using emoji-prefixed titles and `feat`/`fix`/`chore` commit types. Use when staging changes, proposing commit batches, writing high-signal commit messages in imperative mood, committing iteratively, finalising a feature branch by merging/closing/deleting it, and capturing durable memory updates during commit/finalise decisions."
---

# commit

Commit changes in atomic steps, then finalise and clean up the feature branch when requested.

---

## Guardrails

- Require user confirmation before every commit.
- Keep commits atomic; if a title needs "and", split the change set.
- Never mix unrelated files in one commit.
- Determine commit `type` from the actual diff intent, not from branch name, file paths, or habit.
- Never use `chore` for behavior changes (user-visible flow, API contract, data semantics, bug correction, or security fix).
- If a change group contains multiple intents (`feat` + `fix`, `fix` + `chore`, etc.), split it before proposing.
- Never add AI attribution or `Co-authored-by` trailers unless the user explicitly asks.
- Ask for the merge target branch during finalise mode; do not assume `main` (it may be `dev` or another branch).
- Use `review` as a quality gate before commit/finalise when needed.
- Treat memory capture as built-in: update `tasks/memory.md` during commit/finalise when durable information emerges; do not rely on a separate memory-only step.
- During finalise, move the completed feature prd from `tasks/` to `tasks/archive/` (same filename, no rename) in a dedicated pre-merge commit.
- During finalise, update `tasks/memory.md` when durable state changed (completed milestone, next-up priority, blockers, or key decisions) in a dedicated pre-merge commit.
- Never delete the base/default branch.
- Never delete the currently checked-out branch.
- Require explicit user confirmation before deleting local or remote branches.

---

## Commit Message Rules

### Title format (required)

`<emoji> <type>: <imperative summary>`

- `type` must be one of: `feat`, `fix`, `chore`
- Summary must be short, specific, and imperative (e.g., "add", "fix", "remove", "refactor")
- Avoid vague summaries like "update code" or "fix stuff"

### Finalise title (required)

For finalise commit(s) that archive PRDs and/or sync memory, require:

`🧹 chore: finalise f-##`

Keep the same pattern with the feature ID and a short imperative summary.

### Emoji mapping (default)

- `feat` → `✨`
- `fix` → `🐛`
- `chore` → `🧹`

Use a different emoji only if it more precisely matches the change.

### Type selection rubric (required)

Choose `type` in this order (first match wins):

1. `fix`:
   - Corrects wrong behavior vs expected behavior
   - Resolves a regression, flaky/error path, broken edge case, or failing test tied to a bug
   - Fixes security/privacy behavior
2. `feat`:
   - Adds new user-visible capability
   - Expands existing behavior, workflow, API surface, or output contract in a product-facing way
3. `chore`:
   - No product behavior change
   - Maintenance-only work such as tooling/config cleanup, dependency bumps, refactors that preserve behavior, test-only scaffolding, or docs-only edits

Classification rules:

- Use `tasks/todo.md` / PRD `Type:` as a hint, but do not override the real diff intent.
- If a commit changes behavior and internal maintenance together, split and classify each commit separately.
- If uncertain between `feat` and `fix`, prefer `fix` when correcting expected behavior; otherwise use `feat`.
- If still ambiguous after reviewing diff + context, ask the user before committing.

### Body requirements (required)

Include both a concise change summary and the decision rationale. Include:

- short summary of what changed (2-5 bullets)
- problem context a future reader would not have
- alternatives considered
- trade-offs made
- consequences or side effects worth noting

Use this structure:

```text
Summary:
- ...

Why:
- ...

Context:
- ...

Alternatives considered:
- ...

Trade-offs:
- ...

Consequences:
- ...
```

### Finalise commit body (exception)

For finalise commit(s) that only archive the PRD and/or sync memory, use a short body instead of the full Why/Context/Alternatives/Trade-offs/Consequences template.

Use this structure:

```text
Finalise:
- f-## <feature name>

Actions:
- archived PRD to `tasks/archive/`
- updated `tasks/memory.md` (if applicable)
```

---

## Modes

- `commit` mode: propose and execute one atomic commit at a time.
- `finalise` mode: merge/close the completed branch and delete feature branches.

---

## Workflow

1. Inspect current changes (`git status --short`, `git diff`, `git diff --staged`).
2. Partition changes into atomic commit groups.
3. For the next group, propose:
   - files/hunks included
   - type rationale (why this is `feat` / `fix` / `chore`, citing concrete diff intent)
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
6. During commit mode, evaluate memory-worthy outcomes and update `tasks/memory.md` inline when needed:
   - durable rationale not obvious from code diff alone
   - implementation gotchas that should survive branch lifecycle
   - if no durable memory change is needed, explicitly skip with reason

---

## Finalise Mode

Use after all intended commits are done.

1. Confirm preconditions:
   - working tree clean
   - on feature branch (not base)
2. Determine the feature prd path to finalise:
   - prefer active feature prd files in `tasks/` matching the feature ID (`tasks/f-##-*.md`)
   - if multiple matches exist or feature ID is unclear, ask the user for the exact path
3. Before merge, if the prd path matches `tasks/f-##-<slug>.md`:
   - ensure `tasks/archive/` exists
   - move it to `tasks/archive/f-##-<slug>.md` (same filename)
   - propose a dedicated atomic commit with a `🧹 chore:` title (use short finalise body) and require user confirmation
   - if the prd is already under `tasks/archive/`, skip move
4. Before merge, evaluate memory updates:
   - if `tasks/memory.md` exists (or should exist), update it when durable state changed:
     - add completed milestone entry for the finalised feature
     - update "Current state" (next up / blockers) if it changed
     - capture any key decisions or gotchas discovered during completion
   - propose a dedicated atomic memory commit with a `🧹 chore:` title (use short finalise body) and require user confirmation
   - if no durable memory change is needed, explicitly state why memory was not updated
5. Ask the user to confirm the target branch for merge (for example: `main`, `dev`, `release/*`).
6. Choose finalise path:
   - PR path (preferred): merge PR into the confirmed target branch, close it, then clean up branches
   - local path: merge feature branch into the confirmed target branch, then clean up branches
7. Apply branch safety checks before deletion:
   - confirm `<feature-branch>` is not the target branch
   - confirm `<feature-branch>` is not the default branch
   - confirm current HEAD is not `<feature-branch>` when deleting it
8. Delete completed feature branch only after explicit user confirmation:
   - local: `git branch -d <feature-branch>`
   - remote: `git push origin --delete <feature-branch>`

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
- memory sync status (`updated` or `skipped` with reason)
