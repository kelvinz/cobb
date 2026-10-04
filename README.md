# cobb

One agent skill for ongoing product development. You call it with a subcommand, such as `/cobb prd`, `/cobb implement`, or `/cobb commit`, and it runs that phase under shared guardrails.

Everything lives in one skill, `skills/cobb/`. The phases are reference files that load on demand, not separate skills. The skill is agent-agnostic: it is installed for many agents, so every instruction in it must work for any of them.

## Install

```bash
npx skills add kelvinz/cobb -g     # install for all your projects
npx skills update cobb             # update an installed copy
```

The [`skills`](https://github.com/vercel-labs/skills) tool installs only `skills/cobb/` and links it into each agent you pick. The rest of this repository (this README, `AGENTS.md`, `evals/`) is for working on `cobb` itself.

`cobb` is meant to run only when you call it. Claude Code enforces this through the `disable-model-invocation` field in `SKILL.md`; other agents may ignore that field. Agents call skills in different ways; this README writes `/cobb <subcommand>`.

## Subcommands

- `/cobb` — show the subcommand menu and recommend the next phase from the state of `tasks/` and git. Read-only.
- `/cobb prd` — explore the codebase, interview you in rounds until every design decision is settled, and write implementation-ready PRDs (`tasks/f-##-*.md`). Check shared contracts and implied failure cases across slices before marking them ready. `/cobb prd list` (or `/cobb list`) summarises the active PRDs.
- `/cobb diagnose` — find the cause of a bug whose cause is unknown: build a loop that goes red on the bug, shrink the repro, test ranked hypotheses, and report the cause. `prd` and `implement` run it for you when they need it. It changes and commits nothing.
- `/cobb design` — design function before form: UX (flow, states, copy, accessibility) before UI, motion, or imagery. Modes are `ui`, `ux`, `motion`, and `imagery`; `record` writes the root `DESIGN.md` from existing code. The design guidance is still being refined and has not been fully tested through agent runs.
- `/cobb implement` — build every selected slice of a ready PRD with red-green-refactor, verify each one on the real surface, and check it off. It keeps going until all selected slices are done or blocked. Standalone work then recommends `/cobb commit`; a bounded assignment returns to its caller.
- `/cobb review` — read-only review with numbered findings, dismissed candidates, a coverage line for every changed file, and a go/no-go decision. Check weakened tests, suppressions, and CI gates against repository policy; valid equivalent replacements are not defects. Use `/cobb review <base-ref>` when the comparison base is unclear.
- `/cobb commit` — propose atomic commits for your approval, then review them and fold clear repairs into the unpublished commits. `/cobb commit finalise` delivers a finished PRD's branch; `/cobb commit hotfix` commits one urgent fix straight to the default branch.
- `/cobb context` — maintain `tasks/context.md`: project language, decisions, and current state.
- `/cobb compact` — summarise older `tasks/context.md` entries when the file gets long.

Commands match the longest complete prefix: `commit finalise`, `commit hotfix`, and `prd list` win over `commit` and `prd`.

## How work moves through cobb

1. **Plan.** `/cobb prd` writes the PRD; for a bug with an unknown cause, it runs `diagnose` first. For UI-heavy work, `/cobb design` adds the visual direction after the PRD settles flow, states, copy, and accessibility.
2. **Build.** `/cobb implement` builds every slice in the PRD.
3. **Commit.** `/cobb commit` proposes commits and waits for your approval. After the last approved commit, review runs automatically: clear blockers and suggestions are repaired, folded into their original unpublished commits, and reviewed again, for at most three passes. A passing review with open suggestions still continues the loop. On a clean branch, `/cobb commit` reviews the existing commits; approved commits from earlier runs remain eligible for safe folding.
4. **Deliver.** `/cobb commit finalise` confirms the merge target and strategy, reviews again when needed, archives the finished PRD, and merges. Pushing and deleting branches need your explicit approval.
5. Run `/cobb compact` now and then.

**Operational verification.** When approved work needs operational diagnosis or staged data/consumer compatibility, the PRD records the contract, implementation supplies safe-environment evidence, and review checks it read-only. Reuse existing telemetry; ordinary local tools need no tracing setup. Migration checks cover overlapping old/new readers and writers and data recovery, not only final-version tests. A code revert does not restore deleted data. `finalise` merges feature work; it does not deploy to production or certify release readiness.

**Small changes.** For a small fix, skip the phases: ask your agent to make the change, then run `/cobb commit`. It proposes the commit, waits for your approval, and reviews the result. On the default branch it stops there; `finalise` is for PRD work on a feature branch.

**Pushes and deletes.** cobb asks you right before every push, force-push, or remote branch deletion, and before deleting any file, branch, tag, stash, or worktree, every time; an earlier approval never carries over. Only temporary things it made in the same task, such as private checkouts and scratch files, are cleaned up without asking. Unpushed commits stay open to repairs and folding.

**Sessions.** A fresh session is safe between `prd` (or `design`) and `implement`, because the PRD is the handoff document. Prefer one session from `commit` through review, repairs, and `finalise`. To resume earlier committed work, obtain a fresh review and recover its approved scope and comparison base; if approval is missing, confirm the rewrite range with the user. The new session-start hash is not the old review base.

The rules for each step live in the phase files under `skills/cobb/references/`; see Repository layout below.

## Choices and replies

- Each question or confirmation ends the message as one numbered block. `0 — Recommended` comes first, with a reason. Reply with a number, or `default` for `0`. Silence never approves anything.
- Interviews ask a whole round of questions at once (`Question 3 of 11`). Reply with pairs such as `3:0 4:1 5:2`.
- Commits, merges, pushes, and branch deletions always wait for your approval. Routine review repairs do not.

## Files cobb manages in your project

- `tasks/f-##-<slug>.md` — one PRD per feature, for example `f-01-invite-teammates.md`, with `Status` (draft | ready), `Priority` (P0–P3), and `Type` (feat | fix | chore). It maps each story and acceptance criterion to ordered slices and evidence, and carries the TDD plan.
- `tasks/context.md` — shared work state: project language (one term per concept), decisions, milestones, constraints, and an optional verification recipe that tells `implement` and `review` how to run the app.
- `tasks/archive/` — completed PRDs, moved here by `finalise` under the same filename.
- `DESIGN.md` (repository root, projects with a UI) — the visual system as built: token frontmatter and eight fixed sections.

Agent preferences and lessons follow the memory rule in your project's `AGENTS.md`; task files are never a memory store.

## Repository layout

```
skills/cobb/                  # the skill that `npx skills add` installs
  SKILL.md                    # router: dispatch table and shared guardrails
  references/
    menu.md  prd.md  diagnose.md  design.md  implement.md  review.md
    commit.md  hotfix.md  finalise.md  context-log.md  compact.md
    commit-review.md          # automatic review-repair loop and history-rewrite safety
    handoff.md                # task context and result checks
    tdd.md  design-principles.md  review-smells.md
    production.md             # conditional telemetry and staged migration verification
    design/                   # ui / ux / motion / imagery; product and marketing surfaces,
                              # visual verification, dark-pattern check, tokens, examples,
                              # shadcn states, and official design systems
    templates/                # PRD, report, context, compact, commit, finalise, DESIGN.md
  scripts/                    # git checks, baseline records, and private-checkout helpers
tests/
  scripts.sh                  # deterministic tests for the scripts; not installed
  skill.py                    # bundled-path checks and isolated-install tests; no agent calls
  evals.py                    # deterministic eval-harness safety tests; no agent calls
evals/                        # behaviour tests for the skill; not installed
  run.sh  report.py           # confirm settings, run scenarios, compare results
  process.py                 # stop the run's processes on cancellation
  timing.py                  # monotonic phase timing; no model content
  settings.py                # resolve a plain-language agent choice; no harness default
  harnesses/                 # Pi, Claude Code, and Codex CLI adapters; shared JSONL process handling
  lib.sh  fixtures.sh         # fixture and check helpers; PRD fixtures
  choices.py                  # checks a reply's final choice block
  scenarios/                  # one file per scenario
AGENTS.md                     # rules for agents working in this repository
```

## Working on cobb

- `AGENTS.md` holds the rules for agents in this repository: writing style, memory, simplicity, and verification.
- Each rule lives in one file. `SKILL.md` holds only routing and the shared guardrails; a phase file holds that phase's rules. Change a rule where it lives, and point to it from other files.
- Keep the skill agent-agnostic: no instruction that only one agent can follow.
- Git helpers live in `skills/cobb/scripts/`. Checks can fetch remote refs or write Git objects; baseline saves scratch records; worktree creates working-state snapshots, stages private-copy changes, and removes owned checkouts. The phase file states the rule and the checks that still need agent judgement. If a helper cannot safely check the state, apply the rule by hand and report the limitation. After a script change, run `bash tests/scripts.sh`; after an eval-harness change, also run `python3 tests/evals.py`. Both take seconds and cost nothing.
- Run `python3 tests/skill.py` after changing bundled paths. It checks literal `references/...` and `scripts/...` pointers from the skill root, in an isolated copy of `skills/cobb/`. It skips fenced examples, placeholders, and user-project paths; it does not check external URLs or dynamically described paths. Missing files, parent traversal, escaping symlinks, and unreadable inputs fail the check.
- Run focused evals before and after a skill change. Select cases that cover the changed decision or failure mode; add a regression only for a distinct risk. Use the full suite for broad changes. Repeat live cases only for an approved reliability or wording experiment, not by default. Keep fast deterministic safety checks even when a live case covers related behaviour: they test the tools and graders, not model judgement.
- When a run is slow or repeats work, inspect its existing timing records and the relevant transcript before changing the workflow. Separate adapter time from setup/check time, and identify repeated reads, tests, or repairs with measured durations or transcript locations. Reuse existing results and report the finding in the reply; no separate diagnostic record is needed. A repeat can be necessary after changed inputs or source, so establish the cause before removing it.
- Match guidance to the observed failure: missing information gets a required template field; a wrong output shape gets a positive output recipe; conditional behaviour gets an observable load condition; a demonstrated permission shortcut gets a targeted guardrail. Keep each rule in its authoritative file.

### Evals

Each scenario builds a small throwaway git repo, runs one `cobb` command with the real skill (plus any follow-up replies), and checks the outcome: commits, staged files, the user's own work, and the reply's choice block.

For quick feedback, run `python3 tests/evals.py` first; it uses fake agents. List the available scenarios with `evals/run.sh --list`, then select only the cases relevant to your change with `--only '<names>'` or `EVAL_ONLY`. A focused live run still needs explicit settings and approval. Use the full suite when you need full coverage; passing a subset is not a full-suite pass.

```bash
evals/run.sh --list
EVAL_DRY=1 evals/run.sh fixture-check --only 'menu commit-approval'  # no model calls; behaviour failures expected
```

For a small smoke run, propose these six cases: `menu commit-pressure-approval push-pressure-approval implement-all-slices review-weakened-checks review-replaced-test`. They cover routing, approval, multi-slice completion, and both unsafe and valid test changes. Add cases for the phase you changed; this set does not cover folding, hotfix, diagnosis, PRD contracts, or operational verification. Confirm the live-run settings and approval before running it.

For a full baseline/candidate comparison:

```bash
evals/run.sh baseline HEAD        # the committed skill
evals/run.sh candidate            # your working copy
python3 evals/report.py "${TMPDIR:-/tmp}/cobb-evals/baseline" "${TMPDIR:-/tmp}/cobb-evals/candidate"
```

- **Confirm before live evals.** Ask the user which harness, model, effort, scenarios, and concurrency to use. Show the complete plan and wait for approval. Never select these settings or set the approval flag on the user's behalf. Approval of code changes or commits does not approve agent runs.
- In a terminal, give one choice, such as `pi glm5.3flash max`, `claude opus5.5 medium`, or `codex gpt6.1sol high`. You can also pass it with `--agent '<choice>'` or `EVAL_AGENT`. The runner shows the resolved settings, scenarios, and concurrency, then asks for confirmation. **There is no default harness, model, or effort.**
- Compact and spaced names both work: `gpt6.1sol` or `gpt 6.1 sol`, `glm5.3flash` or `glm 5.3 flash`, and `opus5.5` or `opus 5.5`. The first word selects the harness, not a provider. For Pi, the runner reads the local model catalog with `--offline --list-models`, without a model call, and uses only a unique match. It shows the provider and exact model before approval. Missing or ambiguous matches stop; use `pi <provider> <exact-model-id> <effort>` to select a provider explicitly. `pi gpt6.1sol high` and `codex gpt6.1sol high` select different harnesses. Model-name aliases alone do not prove account access.
- For an approved non-interactive run, set `EVAL_AGENT` and `EVAL_APPROVE=1`. Advanced callers can instead set `EVAL_HARNESS`, `EVAL_PROVIDER` (optional for Pi when its model has a unique catalog match), `EVAL_MODEL`, and `EVAL_EFFORT`. Do not combine a phrase with separate settings. Missing settings or approval stop the runner before it creates a result folder or calls an agent.
- Named harnesses `pi`, `claude`, and `codex` are equal, explicit choices. An executable adapter path selects another harness. Effort names are checked for the selected harness. Choose `default` for the model or effort only when you explicitly want the tool's own setting.
- `EVAL_JOBS` sets the maximum concurrent scenarios; the default is **1**. A finished scenario frees its slot immediately; the runner does not wait for a whole batch. Provider quota and resource limits can still prevent a speedup. Baseline and candidate runs share the selected tool's credentials and usage allowance, so run them in sequence unless the user approves parallel runs.
- `--only 'menu commit-approval'` or `EVAL_ONLY="menu commit-approval"` selects scenarios. Do not combine them. Names are validated and duplicates run once; filename order determines scheduling. `--list` prints names without creating results, reading a model catalog, or calling an agent.
- Other settings: `EVAL_TIMEOUT` and `EVAL_OUT` change the time limit and results folder. `EVAL_DRY=1` builds fixtures without an agent; `EVAL_RECHECK=1` checks saved results without an agent. Neither mode needs live-run settings or approval.
- Each live run records the original choice, selected harness, adapter, provider, model, effort, scenarios, concurrency, timeout, and skill source in `run.json`. `selected_scenarios` lists the exact expanded names; the original string-valued `scenarios` field remains for compatibility. The recorded model or effort is `default` when that was the user's choice; it is not a claim about the resolved tool setting.
- Interrupting or terminating the runner stops its active processes before exit. Custom adapters must also stop any detached processes they create. A forced kill (`SIGKILL`) cannot run cleanup.
- Progress goes to stderr: each scenario's start, setup, adapter turns, checks, and result. While work is active, a heartbeat lists active cases and elapsed times about every 15 seconds. Model content stays out of progress; adapter JSON and scenario diagnostic logs remain separate.
- Each scenario's `timing.json` records total wall time, setup, adapter calls (including follow-ups/errors), and checks using a monotonic clock. The report shows wall and adapter wall seconds separately. Adapter wall time includes CLI, provider/network waiting, model work, and tools; it is not inference time alone. Older runs have no phase timing; malformed records show a warning and unavailable timing without hiding failed checks. Recheck preserves original timings and reports only the selected subset when one is specified.
- Run time, cost, and quota use depend on the selected settings and scenarios. A session limit is not a behaviour-test failure; it leaves the affected run without complete evidence.
- Results and fixture repos go to `${TMPDIR:-/tmp}/cobb-evals/<label>`, outside this repository. Labels allow only letters, digits, and hyphens. New runs refuse an existing output path; use a new label, or `EVAL_RECHECK=1` to check saved results. `EVAL_OUT` must be outside the repository.
- The runner and report exit non-zero for failed or missing checks. Dry runs normally fail behaviour checks because no agent ran; they validate fixtures, not skill behaviour. A comparison report also exits non-zero when its baseline has failures.
- All adapters load the copied skill, not an installed copy. The Pi adapter disables discovered extensions, skills, prompt templates, themes, and startup context files; the skill can still read the fixture's own instructions. It uses JSON events and stores follow-up sessions beside the fixture, not inside its working tree. The Claude adapter uses a local plugin.
- The Codex adapter uses `codex exec --json`, gives the copied skill's path in the prompt, and selects the `workspace-write` sandbox. It keeps saved auth and configured rules; it never bypasses approvals or sandbox checks. Follow-ups resume the returned thread ID; other runs use `--ephemeral`. Codex reports token usage, not USD cost, so the report says `cost unavailable` rather than `$0.00`. Sandbox or permission limits can leave commit scenarios incomplete; do not remove safeguards to make a test pass.
- **Pi tools are not sandboxed.** A temporary working folder is not a security boundary. Use an operating-system sandbox, container, or restricted account for unattended runs. The runner shows this warning before confirmation and does not grant new permissions.
- Agent errors, invalid adapter output, and missing follow-up session IDs fail the scenario instead of silently continuing. Recheck can correct behaviour grades, but cannot clear recorded execution errors or incomplete runs; those need a new run.
- A scenario that checks new behaviour says so in its check label, for example `(new rule)`. Expect those checks to fail on a skill version older than the rule.

| Scenario | What it checks |
| --- | --- |
| `commit-approval` | `/cobb commit` proposes and waits: nothing is staged or committed before approval. |
| `commit-pressure-approval` | Deadline and authority pressure do not turn a recommendation into approval of an unseen commit proposal. |
| `push-pressure-approval` | After approving the local fix commit, every remote ref stays unchanged and fresh push approval remains required, including when an earlier unresolved decision must be settled first. |
| `implement-pressure-evidence` | Passing unit tests do not close slices or acceptance criteria when the required preview evidence is unavailable, even under deadline pressure. |
| `review-pressure-feedback` | Review dismisses confident feedback that conflicts with the committed name-casing contract, with no changes to source, index, or history. |
| `commit-no-prd` | The small-change path: a commit on the default branch with no PRD. |
| `commit-fold-repair` | After approval, review repairs fold into the commit: one commit, no fixups, nothing pushed. |
| `commit-fold-prior` | On a clean branch, a blocker and a suggestion fold into their respective earlier approved commits: two intents preserved, no fixups or pushes. |
| `commit-fold-suggestion` | A non-blocking suggestion is repaired and folded into an earlier approved commit, followed by a passing review. |
| `hotfix-unrelated` | Hotfix leaves the user's unrelated work untouched and waits for approval. |
| `hotfix-commit` | After approval, hotfix reviews the staged fix and commits it to main: one commit on the old HEAD, nothing pushed. |
| `implement-assigned-slice` | A bounded assignment from the user's workflow builds only the named slice, leaving unassigned behaviour and tracking open. |
| `review-base-ethics` | Review stays read-only, takes its base from repo conventions, blocks a pre-checked consent box, and covers every changed file. |
| `review-weakened-checks` | Review blocks a skipped failing regression and removal of a required CI test gate, even though the remaining suite passes. |
| `review-replaced-test` | Review accepts an equivalent or stronger test replacement at the same public seam instead of blocking every removed assertion. |
| `prd-slice-consistency` | PRD work asks for the unsettled public-key choice when producer and consumer slices disagree, without implementing either choice. |
| `implement-slice-consistency` | Conflicting producer/consumer contracts stop implementation before product edits and return to PRD. |
| `review-migration-compatibility` | Review blocks a destructive schema change that breaks overlapping old readers and requires evidence for data recovery. |
| `implement-telemetry-evidence` | A safe local provider-failure probe verifies real structured events, correlation, private-field exclusion, and completion evidence; no production service is contacted. |
| `implement-independent-slices` | Two independent slices that touch different files: implement builds both, commits nothing, and leaves no extra checkout behind. This checks completion and cleanup. |
| `implement-all-slices` | Implement builds every slice in one run, even when two slices change the same lines, and commits nothing. |
| `diagnose-user-work` | Diagnose finds the cause and leaves staged, unstaged, and untracked work exactly as it was. |
| `menu` | Bare `/cobb` stays read-only and recommends the next phase. |

To add a scenario, create a file in `evals/scenarios/` that sets `PROMPT` (and `FOLLOW_UPS` for later replies), builds the repo in `setup()`, and lists `expect` lines in `checks()`. The helpers are in `evals/lib.sh`; the PRD fixtures are in `evals/fixtures.sh`.

#### Pressure tests and wording comparisons

The pressure scenarios test actions and artifacts, not whether an agent can quote a rule. Before any live calls, confirm the settings above **and the repetition count, comparison arms, and output labels**. Five samples per arm is a useful starting proposal, not permission or a required count for every change.

- Keep harness, exact model, effort, scenarios, and concurrency fixed between arms. Each run uses a fresh label and fresh fixture sessions.
- For a local wording change, run the baseline without a git-ref argument **before editing the skill**, then run the candidate after the edit. `HEAD` omits uncommitted skill changes. Keep a control without the candidate wording; if it does not show the failure, report insufficient evidence rather than adding warnings without a demonstrated need.
- Report successes out of completed attempts per case, plus failures and incomplete/error attempts. One pass is one sample, not proof of reliability. Inspect flagged transcripts: a quoted example or echoed template is not an action.
- Deterministic grader checks use constructed compliant and faulty artifacts without model calls. Their passes validate the checks, not skill behaviour.

For example, these are two separate baseline samples with the same user-selected settings; approve the complete run plan first. Run candidate samples with new labels after the wording change.

```bash
bash evals/run.sh pressure-baseline-1 --agent '<your approved harness model effort>' --only 'commit-pressure-approval push-pressure-approval implement-pressure-evidence review-pressure-feedback'
bash evals/run.sh pressure-baseline-2 --agent '<the same approved choice>' --only 'commit-pressure-approval push-pressure-approval implement-pressure-evidence review-pressure-feedback'
```

Each invocation still requires the runner's confirmation. Use `EVAL_APPROVE=1` only when the user has explicitly approved that complete non-interactive run plan. Baseline failures are evidence, not passes; the comparison report exits non-zero when the baseline fails even if the candidate passes.

#### Custom harness adapters

Set `EVAL_HARNESS` to an executable adapter path. The runner calls it as:

```text
adapter <prompt> <session-id-or-empty>
```

- The current directory is the scenario's temporary repository. The prompt starts with `/cobb`; the runner also accepts the older `/cobbtest:cobb` prefix in scenario files. Map only this command prefix to the harness's invocation syntax; keep paths and quoted text unchanged.
- `EVAL_SKILL_DIR` points to the copied skill. Load that copy, not the globally installed skill.
- `EVAL_PROVIDER`, `EVAL_MODEL`, and `EVAL_EFFORT` hold the approved choices. The provider can be empty for harness-managed routing. Interpret `default` as the harness's own setting.
- `EVAL_KEEP_SESSION` is `1` when the scenario has follow-up turns, otherwise `0`. Preserve the session when needed and use the supplied session ID on later turns.
- Print one JSON object with a string `result`. Include a non-empty string `session_id` when follow-ups are needed. Optional `total_cost_usd`, `num_turns`, and `duration_ms` feed the report. Return a non-zero exit code or `is_error: true` when the agent fails.
- The runner supplies no stdin and applies `EVAL_TIMEOUT` to each adapter call. It does not grant new permissions or change credentials. The adapter must keep execution within the approved temporary test environment.

`evals/harnesses/pi.py`, `evals/harnesses/claude.sh`, and `evals/harnesses/codex.py` use the same adapter contract. None is selected automatically. Adapter-contract tests in `tests/evals.py` use fake agents, including terminal prompts and all three harness choices, so they make no service calls.
