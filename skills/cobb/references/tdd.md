# TDD Contract

Use this reference for behavioural `feat` and `fix` work during `prd` and `implement`.

## Core Rules

- Test observable behaviour through public interfaces, not private methods or internal call patterns.
- Prefer integration-style tests that exercise real code paths.
- Use focused unit tests for complex pure logic when they give clearer failure localisation.
- Mock only system boundaries such as external APIs, time, randomness, and occasionally databases or filesystems.
- Prefer real controlled dependencies, such as a test database, when they are practical and deterministic.
- Do not mock project-owned collaborators merely to expose their implementation structure.
- Use dependency injection or narrow SDK-style adapters at boundaries when testability requires it.

## Vertical Cycle

Work one behaviour at a time:

1. **RED:** add one test for one observable behaviour and run it to confirm the expected failure.
2. **GREEN:** add the smallest production change that makes that test pass, then run the relevant tests.
3. **REFACTOR:** while green, remove duplication or improve design only within the touched scope; rerun tests after each refactor.
4. Repeat for the next prioritised behaviour.

Do not write all tests first and all implementation second. Do not add speculative production code for future cycles.

For a bug, first reproduce the regression with a failing test whenever a practical automated harness exists.

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

Do not split RED and GREEN into separate commits. A deliberately failing regression test may be shown during implementation, but the committed group must be green unless the user explicitly approves a diagnostic-only commit.
