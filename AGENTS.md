# PHILOSOPHY

This codebase should get easier to change over time.
Prefer maintainability and clarity over short-term speed.
Leave it better than you found it.

---

# SELF IMPROVEMENT LOOP

## Learn From Every Session
- Track mistakes and my preferences so future turns improve.
- Capture only substantive, reusable lessons.
- Keep entries short, specific, and actionable.
- Treat my correction as ground truth.
- Apply lessons immediately.
- Merge duplicates and replace stale/conflicting lessons.
- Never store secrets, tokens, credentials, or private data.
- Store lessons in `LESSONS.md` at the repo root. Create it if missing; append if it exists.

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
- For trivial changes (typo, docs-only, single-line fix), skip the full new → plan pipeline if the user confirms; commit directly.
- If `tasks/` is missing and the work is feature-scoped, create it; if `tasks/todo.md` is also missing, run `new` first unless the user explicitly opts out.

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
4. DRY / functional patterns — only when it reduces complexity

- Always default to industry-standard best practices unless there's a compelling reason not to
- Simplicity first: smallest change that fully solves the problem
- Prefer functional programming patterns over imperative/OOP
- Write pure functions when possible (no side effects, deterministic outputs)
- Favor immutability - avoid mutating data directly

## JavaScript Standards
- Use modern ES6+ syntax exclusively
- Arrow functions for anonymous functions and callbacks
- Destructuring for cleaner variable assignments
- Template literals for string interpolation
- async/await over promise chains for async operations
- Follow established conventions (ESLint recommended rules, Airbnb style guide)

## Code Organisation
- Split functionality into small, single-purpose functions
- One component/module per file
- Group related functions into modules
- Clear, descriptive naming (variables: what they are, functions: what they do)
- Use conventional project structures (e.g., components/, utils/, hooks/)

## Comments & Documentation
- Goal: Make code understandable for the next developer (or your future self)
- Complex logic: Explain the "why" behind non-obvious decisions
- Business rules: Document requirements that drove implementation choices
- Flow overview: Add high-level comments describing the sequence of operations
- Gotchas and edge cases: Call out tricky scenarios or limitations
- External dependencies: Note why specific libraries/APIs are used
- TODO/FIXME: Mark incomplete or temporary solutions
- Update comments when updating code (stale comments are worse than no comments)
- Keep comments concise - aim for clarity, not verbosity

## Best Practices
- Early returns to reduce nesting
- Guard clauses at function start
- Explicit error handling
- Add JSDoc comments for complex functions
- Never claim tests passed or checks succeeded without actually running them; if you didn't run it, say so

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
- Add defensive programming checks even for "impossible" scenarios
- Test security measures in isolation before deployment
- Create attack scenarios and verify defenses work

---

# UI/UX PRINCIPLES

## Design Philosophy
- Clean and minimal - remove unnecessary elements
- Intuitive - users shouldn't need instructions
- Consistent - similar actions should work similarly everywhere
- Responsive - works seamlessly across all device sizes
- Follow established UX patterns - don't reinvent the wheel

## Implementation
- Accessibility first (WCAG guidelines, ARIA labels, keyboard navigation, semantic HTML)
- Performance matters - lazy load when appropriate
- Clear visual hierarchy
- Meaningful feedback for user actions
- Graceful error states with helpful messages
- Test UI functionality independently, not just design
- Verify all interactive elements work as expected
- Test error states and recovery paths
- Ensure accessibility features are functional, not just present

---

# TESTING & VERIFICATION

## Closed-Loop Testing
- Build self-contained test environments
- Test features end-to-end without user involvement
- For backend: Run locally, send own requests, verify logs independently
- For frontend: Test full functionality, not just visual design
- Iterate internally until feature is production-ready

## Independence Principle
- For bug reports: reproduce → isolate → fix root cause → add/adjust tests → verify
- Don't make the user run commands unless environment-specific
- Don't rely on user feedback for debugging
- Create comprehensive test scenarios
- Verify all paths through the code
- Document test coverage and edge cases tested

---
