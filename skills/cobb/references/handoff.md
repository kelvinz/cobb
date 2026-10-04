# Task handoff

Use this contract when the user's workflow passes a bounded task to another person or agent. It defines the context needed to do that task. Prepare the brief from current facts; the recipient does not inherit the caller's conversation.

## Task context

Include:

- **Scope:** the calling phase, assigned slice IDs, hypothesis, survey area, variant, or review scope; acceptance criteria and non-goals.
- **Source:** the physical working directory and expected revision or working-state snapshot. Include the comparison base, staged snapshot, session-start hash, and delivery scope when the phase needs them.
- **Inputs:** absolute paths to the exact `SKILL.md` in use, needed phase files, project instructions and their required references, and the relevant PRD, `tasks/context.md`, and design artifacts when present. Map project paths to the assigned checkout, not the caller's checkout. Check that required inputs are accessible, including ignored inputs handled separately under Isolated work.
- **Decisions:** relevant user answers, approved interfaces, constraints not yet recorded in those files, accepted prerequisite results, and remaining blockers. For a review, give requirements and facts, not the caller's verdict or expected findings.
- **Authority and return:** allowed file changes, who owns tracking updates and later phase handoffs, verification commands or recipe, required evidence, and the phase's result format. A review stays read-only.

Pass only relevant context, without credentials. Keep permission and sandbox limits unchanged. Refresh source and context after prerequisite work is accepted; an earlier snapshot is not the next task's starting state.

## Receipt and verification

The recipient reads the named inputs and checks its working directory, revision, and scope before work. Missing inputs, conflicting constraints, or a source mismatch are blockers to return, not permission to guess or expand scope.

Do only the assigned work. Return required decisions and deletion questions to the caller for user approval. Return the task ID or scope, checkout and starting revision, changed files, verification grades and evidence, and blockers. Start another phase or update tracking only when the assignment includes it.

The caller checks the result against the brief and current state before applying it or recording completion.
