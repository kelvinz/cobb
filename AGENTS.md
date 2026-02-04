# PHILOSOPHY

This codebase should get easier to change over time.
Prefer maintainability and clarity over short-term speed.
Leave it better than you found it.

---

# SELF IMPROVEMENT LOOP

## When Corrected
- Substantive only: recurring or costly corrections.
- Treat corrections as ground truth for this AGENTS.md (and future copies).
- Add/update lessons (prefer 1–2; merge when possible).
- Apply lessons immediately.
- Promote durable lessons into the relevant section below.
- Remove lessons once promoted.

## Lessons Learned
### Rules
- Max **10** entries (newest first). Merge duplicates; delete stale items.
- Format: `Mistake → Rule → Prevention`.
- Never store secrets, tokens, credentials, or private data.

### Entries
<!-- Add new lessons above this line (newest first). -->

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

## Research & Verification
- Check official documentation for the latest syntax and methods
- Research current best practices and recent updates
- Verify assumptions against authoritative sources
- Stay current with security advisories and deprecations
- Test new approaches in isolation before full implementation

---

# CODING GUIDELINES

## Core Principles
- Always default to industry-standard best practices unless there's a compelling reason not to
- Simplicity first: smallest change that fully solves the problem
- Minimal impact: touch only what's necessary; avoid drive-by refactors
- Prefer functional programming patterns over imperative/OOP
- Maintain DRY (Don't Repeat Yourself) - abstract common logic into reusable functions
- Write pure functions when possible (no side effects, deterministic outputs)
- Favor immutability - avoid mutating data directly

## JavaScript Standards
- Use modern ES6+ syntax exclusively
- Arrow functions for anonymous functions and callbacks
- Destructuring for cleaner variable assignments
- Template literals for string interpolation
- async/await over promise chains for async operations
- Follow established conventions (ESLint recommended rules, Airbnb style guide)

## Code Organization
- Split functionality into small, single-purpose functions
- One component/module per file
- Group related functions into modules
- Clear, descriptive naming (variables: what they are, functions: what they do)
- Use conventional project structures (e.g., components/, utils/, hooks/)

## Comments & Documentation
Goal: Make code understandable for the next developer (or your future self)
- Complex logic: Explain the "why" behind non-obvious decisions
- Business rules: Document requirements that drove implementation choices
- Flow overview: Add high-level comments describing the sequence of operations
- Gotchas and edge cases: Call out tricky scenarios or limitations
- External dependencies: Note why specific libraries/APIs are used
- TODO/FIXME: Mark incomplete or temporary solutions
- Update comments when updating code (stale comments are worse than no comments)
- Keep comments concise - aim for clarity, not verbosity

### Examples
#### Basic
```js
// ❌ BAD: States the obvious
// Set user to null
const user = null

// ✅ GOOD: Explains why
// Reset user to trigger re-authentication flow
const user = null

// ✅ GOOD: Explains flow and context
/**
* Processes payment in 3 steps:
* 1. Validate payment method with payment provider
* 2. Create transaction record in our DB (for audit trail)
* 3. Send confirmation email to user
*
* Note: Step 2 must complete before step 3 to include transaction ID in email
*/
async function processPayment ( paymentData ) {
	// Step 1: Validate with Stripe (throws if invalid)
	const validation = await stripe.validatePayment( paymentData )

	// Step 2: Store transaction (includes user_id, amount, timestamp)
	const transaction = await db.createTransaction( {
		userId: paymentData.userId,
		amount: validation.amount,
		stripeId: validation.id
	} )

	// Step 3: Send email with transaction details
	await sendConfirmationEmail( paymentData.userId, transaction )

	return transaction
}
```
#### Function headers: Use JSDoc for complex/public functions
```js
/**
* Calculates discounted price based on user tier and promo codes
*
* @param {number} basePrice - Original price in cents
* @param {string} userTier - One of: 'free', 'premium', 'enterprise'
* @param {string[]} promoCodes - Array of promo code strings
* @returns {number} Final price in cents (never negative)
* @throws {Error} If userTier is invalid
*/
function calculatePrice ( basePrice, userTier, promoCodes ) {
	// Implementation...
}
```
#### File headers: Add brief description for modules
```js
/**
* Authentication utilities
* Handles JWT token generation, validation, and refresh logic
* Used by: auth middleware, login/logout endpoints
*/
```
#### Inline comments: For non-obvious code blocks
```js
// Using reduce instead of filter + map to avoid iterating twice (performance)
const activeUserNames = users.reduce( ( acc, user ) => {
	if ( user.isActive ) acc.push( user.name )
	return acc
}, [] )
```

## Best Practices
- Early returns to reduce nesting
- Guard clauses at function start
- Explicit error handling
- Add JSDoc comments for complex functions

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
- Remove debug code before finalizing

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
