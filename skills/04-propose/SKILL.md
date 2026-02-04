---
name: 04-propose
description: "Push the current feature branch and open/update a best-practice Draft pull request via GitHub CLI (gh), including a high-quality PR title/body linked to the PRD with testing + verification steps. Use when pushing a branch, creating/updating a PR, drafting a PR description, or running gh pr create/edit. Triggers: propose, push, PR, pull request, create PR, open PR, draft PR, pr description, gh pr create, gh pr edit, ready for review."
---

# 04 propose

Publish your work for review by pushing the branch and creating/updating a Draft PR with a strong title + description.

---

## Guardrails

- Do not implement new code here. If changes are needed, go back to `03-implement`.
- Do not merge the PR here. Review/merge happens in `05-review`.
- Prefer Draft PRs by default.

---

## Workflow

1. **Gather inputs**
   - prd path (e.g. `tasks/f-##-<slug>.md`)
   - base branch (default: `main`)
   - PR title seed (default: from prd title / feature ID)

2. **Preflight**
   - Confirm you are on a feature branch (not the base branch).
   - Ensure the working tree is clean (`git status --porcelain` is empty).
   - Ensure there are commits to push (compare `base...HEAD`).
   - Ensure the prd has `## Execution Status` and **Implemented** is checked.
   - Capture test/check commands + results for the PR body (don’t guess).

3. **Push the branch**
   - `git push -u origin HEAD`

4. **Draft PR title + body**
   - Use the template below and include:
     - prd path
     - what changed + why
     - tests run (exact commands + results)
     - how to verify
     - risks / rollout / rollback (if applicable)

5. **Create or update the PR with `gh`**
   - Try to view an existing PR for the current branch:
     - `gh pr view --json url,number,state,isDraft -q .url`
   - If it exists, update:
     - `gh pr edit --title "<title>" --body "<body>"`
   - If it does not exist, create a Draft PR:
     - `gh pr create --draft --base "<base>" --title "<title>" --body "<body>"`
   - Capture the PR URL:
     - `gh pr view --json url -q .url`

6. **Next**
   - Run `05-review` (PR mode).

---

## PR Template

### Title

- Prefer: `f-##: <feature name>`

### Body (Markdown)

```markdown
## Summary
- What: …
- Why: …

## PRD
- `tasks/f-##-<slug>.md`

## Changes
- …

## Testing
- `…` → ✅/❌

## How to verify
1. …
2. …

## Risks / rollout / rollback (if applicable)
- …

## Screenshots (if UI)
- …

## Checklist
- [ ] PRD linked
- [ ] Tests/checks run
- [ ] Edge cases considered
```

---

## Output

- PR URL (or instructions if creation failed).
- Final PR title + body used.
