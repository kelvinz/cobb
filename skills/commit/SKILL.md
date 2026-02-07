---
name: commit
description: "Create atomic commits with explicit user approval, using emoji-prefixed titles and `feat`/`fix`/`chore` commit types. Use when staging changes, proposing commit batches, writing high-signal commit messages in imperative mood, committing iteratively, and finalising a feature branch by merging/closing/deleting it."
---

# commit

Commit changes in atomic steps, then finalise and clean up the feature branch when requested.

---

## Guardrails

- Require user confirmation before every commit.
- Keep commits atomic; if a title needs "and", split the change set.
- Never mix unrelated files in one commit.
- Never add AI attribution or `Co-authored-by` trailers unless the user explicitly asks.
- Ask for the merge target branch during finalise mode; do not assume `main` (it may be `dev` or another branch).
- Use `review` as a quality gate before commit/finalise when needed.
- During finalise, rename active feature prd to `done-f-##-<slug>.md` and sync `tasks/todo.md` `prd:` path in a dedicated pre-merge commit.
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

### Emoji mapping (default)

- `feat` → `✨`
- `fix` → `🐛`
- `chore` → `🧹`

Use a different emoji only if it more precisely matches the change.

### Body requirements (required)

Write why the change exists, not just what changed. Include:

- problem context a future reader would not have
- alternatives considered
- trade-offs made
- consequences or side effects worth noting

Use this structure:

```text
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
   - commit title (emoji + type + imperative summary)
   - commit body (Why/Context/Alternatives/Trade-offs/Consequences)
4. Ask for a decision:
   - `yes`: stage only that group and commit
   - `edit`: revise message/scope and ask again
   - `skip`: leave group uncommitted and move on
   - `split`: break the group into smaller commits and repropose
5. After each accepted commit:
   - commit immediately
   - report commit hash + title
   - propose the next atomic group until done

---

## Finalise Mode

Use after all intended commits are done.

1. Confirm preconditions:
   - working tree clean
   - on feature branch (not base)
2. Determine the feature prd path to finalise:
   - prefer the feature's `prd:` path from `tasks/todo.md` when available
   - otherwise ask the user for the prd path
3. Before merge, if the prd path matches `tasks/f-##-<slug>.md`:
   - rename it to `tasks/done-f-##-<slug>.md`
   - update the matching feature's `prd:` path in `tasks/todo.md`
   - propose a dedicated atomic tracking commit and require user confirmation
   - if the prd is already `done-f-##-...`, skip rename/path edits
4. Ask the user to confirm the target branch for merge (for example: `main`, `dev`, `release/*`).
5. Choose finalise path:
   - PR path (preferred): merge PR into the confirmed target branch, close it, then clean up branches
   - local path: merge feature branch into the confirmed target branch, then clean up branches
6. Apply branch safety checks before deletion:
   - confirm `<feature-branch>` is not the target branch
   - confirm `<feature-branch>` is not the default branch
   - confirm current HEAD is not `<feature-branch>` when deleting it
7. Delete completed feature branch only after explicit user confirmation:
   - local: `git branch -d <feature-branch>`
   - remote: `git push origin --delete <feature-branch>`

---

## Output

For each proposed commit, provide:

- atomic scope (files/hunks)
- proposed title
- proposed body
- explicit confirmation prompt (`Commit this change now?`)

After execution, provide:

- created commit hash/title
- remaining uncommitted groups
- finalise recommendation when all groups are complete
