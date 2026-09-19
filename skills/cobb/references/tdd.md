# TDD Contract

Use this reference during `prd` and `implement` for behavioural `feat` and `fix` work, and for `chore` work that restructures code (see Behaviour-Preserving Changes).

## Core Rules

- Test observable behaviour through public interfaces; private methods and internal call patterns stay untested.
- Prefer integration-style tests that exercise real code paths.
- Use focused unit tests for complex pure logic when they give clearer failure localisation.
- Mock only system boundaries such as external APIs, time, randomness, and occasionally databases or filesystems.
- Prefer real controlled dependencies, such as a test database, when they are practical and deterministic.
- Keep project-owned collaborators real; a mock of one only pins the implementation structure.
- Use dependency injection or narrow SDK-style adapters at boundaries when testability requires it.
- Take every expected value from an independent source of truth: a known-good literal, a worked example, or the spec. A test whose expected value is recomputed the way the code computes it (`expect(add(a, b)).toBe(a + b)`) is **tautological**: it passes by construction and can never disagree with the code.
- Before keeping a test, ask whether it would still pass if every function it imports returned `undefined`. If yes, it observes no behaviour: rewrite the assertion or delete the test. Five shapes fail this check:
  - weak or no assertion (`toBeDefined`, `toBeTruthy`, `not.toThrow`, `toBeGreaterThan(0)`)
  - mock or absence only (`toHaveBeenCalled`, `toEqual([])`, `not.toBe(wrongValue)`)
  - self-referential expected values (the tautological case above)
  - constant pins that restate a hand-maintained constant, default, or prompt string
  - fixture asserts fixture: the assertion reads data the test built and the subject never runs
  The fix is one concrete input and a literal expected output or observable effect; for an absence, assert the presence on the other input in the same test; for a mock, assert the payload it received or the state after the call.
- Name tests and fixtures with the project language from `tasks/context.md`.

## Seams

A **seam** is the public boundary a test crosses: the interface where behaviour is observed without reaching inside. Tests live at seams, never against internals.

- In PRD work, tests are written only at seams the user confirmed during `prd`: section 9 (Seams under test) for behavioural work, or the behaviour pin for a restructuring `chore`. A test at an unconfirmed seam is a PRD gap: return to `prd` for that decision. A review repair with no PRD uses the seams the existing tests already cross.
- Prefer existing seams to new ones. Place any new seam as high as it can go while still observing the behaviour, and keep the total small; one seam is the ideal.
- The interface is the test surface. A test that needs to reach past the interface is a signal that the module is the wrong shape, which is a design decision for `prd`, not a reason to test internals.

## Vertical Cycle

Work one behaviour at a time:

1. **RED:** add one test for one observable behaviour and run it to confirm the expected failure.
2. **GREEN:** add the smallest production change that makes that test pass, then run the relevant tests.
3. **REFACTOR:** while green, remove duplication or improve design only within the touched scope; rerun tests after each refactor.
4. Repeat for the next prioritised behaviour.

Work vertically: one test, one implementation, repeat. Production code covers only the behaviour of the current cycle.

For a bug, first reproduce the regression with a failing test whenever a practical automated harness exists. When the PRD came from a Diagnosis Report, the minimal repro is that test and the regression seam is where it lives. If the RED test fails to reproduce the bug, the cause is not yet known: `implement` runs `references/diagnose.md` and updates the PRD before continuing.

## PRD Requirements

For each behavioural slice, the PRD must specify:

- requirement and acceptance-criterion IDs covered
- observable behaviour and public interface under test
- test level, file location, and suggested test name
- fixtures, setup, and controlled data
- real dependencies and mocked system boundaries
- expected RED failure and why it proves the test is meaningful
- minimal GREEN behaviour, without prescribing routine syntax
- permitted refactor scope after green
- exact commands and completion evidence

Include test code or pseudocode when setup, boundary control, concurrency, state transitions, or assertions are non-obvious.

## Behaviour-Preserving Changes

For a `chore` that restructures code (rename, extract, inline, dedupe, move), the contract is that behaviour does not change:

1. **Pin first.** Before any structure moves, capture current behaviour with a characterisation test, a snapshot, or an equivalence harness that replays a recorded baseline. Typecheck and lint are not a pin. If the area has no coverage, write the pin before touching structure.
2. **Subtract, then reshape.** Delete dead code, one-caller wrappers, and redundant validators first, then introduce the new shape in small steps that keep the pin green. When a new internal API replaces an old one, migrate every caller and delete the old path in the same wave; use expand-migrate-contract only when a single wave cannot land green.
3. **Prove equivalence on the real artifact.** Diff old-versus-new outputs, replay the baseline against the new code, or run the surface, not "it compiles".
4. **Keep it only if reader load fell.** The success measure is fewer layers to trace or less hidden state to hold. A reshape that lowers neither is reverted.

A cleanup that reveals a missing feature or a real bug is split out into its own PRD; the structural change ships first against the pin.

## Exceptions

Automated TDD may be impractical for visual-only behaviour, environment-specific integration, unavailable hardware/services, or a repository with no viable harness.

An exception must include:

- specific reason automation is impractical
- regression risk created by the exception
- repeatable manual verification steps and expected results
- follow-up needed to introduce a test seam or harness, when proportionate

Low effort alone is not a sufficient exception.

## Green-State Refactor Check

After the slice is green, inspect touched code for:

- duplication that now has a stable shared concept
- long or mixed-purpose functions
- shallow modules that expose complexity instead of containing it
- logic located away from the data or responsibility it belongs to
- primitive values that repeatedly carry domain invariants

Refactor only when it improves the current slice. Keep tests on public behaviour, and require a focused PRD update before expanding into broader adjacent cleanup.

## Commit Boundary

Keep a completed behavioural slice together as one atomic group:

- test
- minimal implementation
- scoped refactor
- PRD checklist updates
- durable context update, if any

RED and GREEN land together in one commit. A deliberately failing regression test may be shown during implementation, but the committed group must be green unless the user explicitly approves a diagnostic-only commit.
