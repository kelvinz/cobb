# diagnose

Find the cause of a bug whose cause is unknown, and hand `prd` the evidence a fix PRD needs. Use it for the bug that resists a first look, the intermittent flake, or the regression that crept in between two known-good states. A bug with an obvious cause skips this phase.

Shared guardrails from the cobb router apply; the rules below are diagnose-specific.

## Callers

- `prd` (usual path): loaded automatically when a fix PRD has no confirmed root cause and no bounded hypotheses. Return the Diagnosis Report to `prd`, which writes the fix PRD from it.
- `implement`: loaded automatically when a fix PRD's RED test fails to reproduce the bug. Return the report to `implement`, which updates the PRD through `prd` and resumes.
- `standalone` (`/cobb diagnose`): the user wants the cause without a PRD yet. End with the report and recommend `/cobb prd`.

A called run skips the standalone closing recommendation and returns control with the report.

## Guardrails

- Leave product code, tests, and tracking files as you found them. Temporary instrumentation and throwaway harnesses are allowed while the phase runs and are removed before it ends.
- Commit nothing. The fix itself belongs to `implement`, under a fix PRD.
- Redact every secret before showing a command, output, or captured artifact: write `<REDACTED>` in its place, build loops against environment variables so credentials stay out of what you show, and quote only the lines of a captured artifact that carry the signal. If the redacted output is too thin to diagnose, say so and ask the user.
- Work the phases in order. Skip a phase only with a stated reason.

## Workflow

### Starting State

**Baseline.** Before experiments, save the original branch, HEAD, index entries (`git ls-files --stage -z`), staged/unstaged binary diffs, untracked path list, and contents/modes/existence of every path the experiment can touch. Use private scratch storage outside the repo; the baseline may contain secrets.

**Isolation.** Prefer a disposable copy that includes relevant user edits, with isolated test data. Run instrumentation, bisection, and tests there. Leave the original index and branch unchanged.

**In-place exception.** If a copy cannot reproduce the environment, ask before experimenting in place. Save each path before touching it. Restore only your experiment changes from the baseline, never from HEAD or with a blanket reset/clean. If a path differs from your last written version, preserve the concurrent edit and pause.

### 1. Build a feedback loop

This is the phase that matters. A **tight** loop is one command that goes **red** on this exact bug and green once it is fixed. With one, the remaining phases are mechanical; without one, code-reading produces theories, not causes. Spend disproportionate effort here.

Ways to build one, roughly in order:

1. A failing test at whichever seam reaches the bug: unit, integration, or end-to-end.
2. A curl or HTTP script against a running dev server.
3. A CLI invocation with a fixture input, diffing stdout against a known-good snapshot.
4. A headless browser script that drives the UI and asserts on DOM, console, or network.
5. Replaying a captured trace (request, payload, event log) through the code path in isolation.
6. A throwaway harness: a minimal subset of the system exercising the bug path with one call.
7. A property or fuzz loop when the symptom is "sometimes wrong output".
8. A bisection harness when the bug appeared between two known states, so `git bisect run` can drive it.
9. A differential loop: the same input through two versions or configs, diffing the outputs.
10. A human-in-the-loop script, last resort, that drives the person through the steps and captures what they observe.

Then tighten it: faster (cache setup, skip unrelated init), sharper (assert the exact symptom, not "didn't crash"), and deterministic (pin time, seed randomness, isolate the filesystem, freeze the network). For a flaky bug, raise the reproduction rate instead of chasing a clean repro: loop the trigger many times, parallelise, add stress, narrow timing windows.

Phase 1 is complete when you can name one command you have already run at least once (show the redacted invocation and output) that is red-capable, deterministic, fast, and agent-runnable. If no loop is possible, stop and say so: list what you tried and ask the user for a reproducing environment, a redacted captured artifact, or permission to add temporary instrumentation. Phase 2 starts only with a red loop.

### 2. Reproduce and minimise

Run the loop and watch it go red. Confirm it fails the way the user described, not a nearby failure, and that the failure repeats across runs. Capture the exact symptom for later verification.

Then shrink the repro to the smallest scenario that still goes red. Cut inputs, callers, config, data, and steps one at a time, rerunning after each cut. Done when every remaining element is load-bearing: removing any one turns the loop green. The minimal repro shrinks the hypothesis space and becomes the regression test.

### 3. Hypothesise

Write three to five ranked hypotheses before testing any. Each states a falsifiable prediction: "If X is the cause, then changing Y makes the bug disappear, or changing Z makes it worse." A hypothesis without a prediction is discarded or sharpened.

Show the ranked list to the user before testing; they often re-rank it instantly or rule some out. Continue with your own ranking if they are away.

### 4. Instrument

Each probe maps to one prediction from phase 3. Change one variable at a time. Prefer a debugger or REPL inspection, then targeted logs at the boundaries that separate hypotheses. Tag every debug log with one unique prefix such as `[DEBUG-a4f2]` so cleanup is a single grep.

For a performance regression, measure first: establish a baseline (timing harness, profiler, query plan), then bisect.

### 5. Confirm and locate the seam

Confirm the cause by turning the loop green with the smallest possible change, then revert that change. The fix that ships later is the smallest change the evidence justifies; a change motivated by a hypothesis the loop refuted is dropped, and a guard that merely silences the symptom is not a cause. Search for siblings of the same pattern and list them in the report. For a bug that appears only after a restart, suspect stale persistent state (config, caches, lock files, serialised state) before code. Identify the correct seam for a regression test: one where the test exercises the real bug pattern as it occurs at the call site. If the only seam available is too shallow to lock the bug down, that is itself a finding for the PRD.

### 6. Clean up and report

Before ending:

- remove all tagged instrumentation (grep the prefix) and restore any in-place experiment changes under Starting State
- delete throwaway harnesses, or move them to a clearly marked scratch location outside the repo
- compare every value in the Starting State baseline with the original repo; all must match, not only `git status --short`
- if a comparison fails, report the changed paths without claiming cleanup succeeded; preserve concurrent user work and retain the private baseline until the difference is resolved
- after successful cleanup, remove private backups that are not needed for the redacted repro

Then produce the Diagnosis Report and recommend `/cobb prd` to write the fix PRD from it.

## Diagnosis Report

```text
Diagnosis Report

Symptom: <the user's exact reported behaviour>
Loop: <one command> (red-capable, deterministic, ~<n>s)
Minimal repro: <the load-bearing inputs, state, and steps>
Hypotheses tested: <ranked list with the prediction and verdict for each>
Confirmed cause: <the hypothesis that held, with the evidence>
Regression seam: <where the regression test belongs, or why no correct seam exists>
Regression surface: <related paths the fix must leave unchanged>
Sibling instances: <other sites with the same pattern, or none>
Cleanup: <instrumentation removed, harness location or deleted, baseline comparisons and any unresolved differences>
```

The report maps directly onto the fix PRD: Symptom and Minimal repro feed Reproduction, Confirmed cause feeds Root cause, Regression seam feeds the first RED slice, and the confirmed hypothesis is recorded in the fix commit body.

## Output

- No file changes.
- The Diagnosis Report, redacted.
- Called: return the report to the caller. Standalone: recommend `/cobb prd` for the fix PRD.
- When no loop could be built: the list of attempts and the environment or artifact request, returned the same way.
