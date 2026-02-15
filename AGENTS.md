# PHILOSOPHY

This codebase should get easier to change over time.
Prefer maintainability and clarity over short-term speed.
Leave it better than you found it.

---

# SELF IMPROVEMENT LOOP

## Learn From Every Session
- At the start of every task, check for `LESSONS.md` in the repo root
- If it exists, read it before planning or writing code
- Track mistakes and my preferences so future turns improve
- Capture only substantive, reusable lessons
- Keep entries short, specific, and actionable
- Treat my correction as ground truth
- Apply lessons unless higher-priority instructions override them
- Merge duplicates and replace stale/conflicting lessons
- Never store secrets, tokens, credentials, or private data
- Store lessons in `LESSONS.md` at the repo root; create if missing, append otherwise

---

# PROBLEM EXPLORATION & PLANNING

## Before Writing Code
- Deeply explore the problem space before implementation
- Identify root causes, not just symptoms
- Document clear requirements and success criteria
- Create a strategic implementation plan with milestones
- Consider multiple approaches and choose the most maintainable
- Think through edge cases and failure modes upfront
- For non-trivial changes, check for a simpler design
- Skip this for obvious fixes (don't over-engineer)
- For obvious fixes, run 1-3 root-cause checks, then ship the smallest safe fix

## Research & Verification
- Check official documentation for the latest syntax and methods
- Research current best practices and recent updates
- Verify assumptions against authoritative sources
- Stay current with security advisories and deprecations
- Test new approaches in isolation before full implementation

---

# CODING GUIDELINES

## Core Principles (priority order)
1. Correctness and security — always first
2. Minimal impact — touch only what's necessary; avoid drive-by refactors
3. Clarity — code should be readable and obvious
4. DRY (Don't Repeat Yourself) / functional patterns — only when it reduces complexity

- Always default to industry-standard best practices unless there's a compelling reason not to
- Simplicity first: smallest change that fully solves the problem
- Clarity over brevity — prefer explicit, readable code over dense one-liners or nested ternaries
- Prefer functional programming patterns over imperative/OOP
- Write pure functions when possible (no side effects, deterministic outputs)
- Favor immutability - avoid mutating data directly
- Avoid over-abstraction — don't sacrifice clarity for cleverness or compactness

## Language Strategy
- Be language-agnostic: follow the idioms and tooling of the touched language

## JavaScript / TypeScript Standards
- Apply this section when working in JavaScript/TypeScript files
- Use modern syntax supported by the project's runtime/build target
- Arrow functions for anonymous functions and callbacks
- Destructuring for cleaner variable assignments
- Template literals for string interpolation
- async/await over promise chains for async operations
- Follow project lint and established conventions (ESLint recommended rules, Airbnb style guide)

## Code Organisation
- Split functionality into small, single-purpose functions
- Prefer one primary module per file; colocate only when tightly coupled
- Group related functions into modules
- Clear, descriptive naming (variables: what they are, functions: what they do)
- Use conventional project structures (e.g., components/, utils/, hooks/)

## Comments & Documentation
- Goal: keep code understandable for the next maintainer
- Prefer self-explanatory code first
- Remove comments that state the obvious — they add noise and obscure meaningful comments
- Comment non-obvious intent, tradeoffs, and constraints
- Complex logic: Explain the "why" behind non-obvious decisions
- Business rules: document requirements that drive decisions
- Flow overview: comment sequence only when non-obvious
- Gotchas and edge cases: Call out tricky scenarios or limitations
- External dependencies: Note why specific libraries/APIs are used
- TODO/FIXME: Mark incomplete or temporary solutions
- Update comments with code changes; stale comments are worse than no comments
- Keep comments concise - aim for clarity, not verbosity

## Best Practices
- Early returns to reduce nesting
- Guard clauses at function start
- Explicit error handling
- Add JSDoc comments for complex functions
- Never claim tests/checks passed unless you ran them; if you didn't run it, say so

## Debugging Methodology

### Systematic Approach
- Locate: Identify where the issue manifests
- Isolate: Create minimal reproducible examples
- Resolve: Fix root cause, not symptoms
- Verify: Confirm fix doesn't break other functionality

### Debug Tools
- Use structured logging (not just console.log)
- Create isolation scripts for complex issues
- Add temporary verbose logging when hunting bugs
- Remove debug code before finalising

## Security & Robustness
- Follow OWASP guidelines and industry-standard security practices
- Sanitise and validate all inputs (never trust user data)
- Consider edge cases at every implementation step:
  - Empty states (null, undefined, empty arrays/objects)
  - Boundary conditions (max/min values, string lengths)
  - Concurrent operations and race conditions
  - Network failures and timeout scenarios
- Implement proper authentication/authorisation checks
- Use parameterised queries to prevent injection attacks
- Keep dependencies updated and audit for vulnerabilities
- Add defensive checks for edge and "impossible" scenarios
- Test security measures in isolation before deployment
- Test likely attack scenarios and verify defenses

---

# UI/UX PRINCIPLES

## Design Philosophy
- Clean and minimal - remove unnecessary elements
- Intuitive - users shouldn't need instructions
- Consistent - similar actions should work similarly everywhere
- Responsive - works seamlessly across all device sizes
- Follow established UX patterns - don't reinvent the wheel

## Implementation
- Accessibility first (WCAG, semantic HTML, keyboard nav, ARIA)
- Performance matters - lazy load when appropriate
- Clear visual hierarchy
- Meaningful feedback for user actions
- Graceful error states with helpful messages
- Test UI functionality independently, not just design
- Verify all interactive elements work as expected
- Test error states and recovery paths
- Ensure accessibility features work, not just exist

---

# TESTING & VERIFICATION

## Closed-Loop Testing
- Build self-contained test environments
- Test features end-to-end without user involvement
- For backend: run locally, send requests, verify logs
- For frontend: test behavior, not just visuals
- Iterate internally until feature is production-ready

## Independence Principle
- For bug reports: reproduce → isolate → fix root cause → add/adjust tests → verify
- Don't make the user run commands unless environment-specific
- Don't rely on user feedback for debugging
- Create comprehensive test scenarios
- Verify all paths through the code
- Document test coverage and edge cases tested

---
