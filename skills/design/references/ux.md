# UX Mode

Use this mode to shape task flows, information architecture, usability, accessibility, and audit quality.

## Table of Contents

1. UX Discovery Inputs
2. Task Flow and Information Architecture
3. Content Hierarchy and Clarity Heuristics
4. Accessibility and Usability Checks
5. Accessibility Option Set for UI Components
6. Audit Workflow and Axes
7. Severity Scale
8. Findings Format
9. Guideline-Driven Audit Procedure
10. UX Output Contracts

## UX Discovery Inputs

Collect these inputs before proposing changes:

1. Human profile and context of use.
2. Primary task and success definition.
3. Key constraints: platform, compliance, accessibility target, design-system rules.
4. Current pain points, failure moments, or confusion reports.
5. Existing routes, components, or files in scope.

When context is thin, state explicit assumptions and proceed.

## Task Flow and Information Architecture

1. Map current journey: entry point, decision points, exits, and fallback paths.
2. Reduce unnecessary steps and branch complexity.
3. Group information by user intent, not implementation structure.
4. Keep navigation labels concrete and predictable.
5. Define primary actions and secondary actions with clear separation.
6. Define empty, error, and recovery paths as first-class flows.

## Content Hierarchy and Clarity Heuristics

1. Make the primary task visually and semantically obvious within seconds.
2. Keep one dominant focus per view whenever possible.
3. Make status, feedback, and next action explicit after each key action.
4. Use consistent terminology and domain vocabulary across related surfaces.
5. Keep microcopy specific, short, and consequence-aware.

## Accessibility and Usability Checks

1. Verify keyboard-only reachability for all interactive controls.
2. Verify visible focus and logical tab order.
3. Verify contrast and semantic color usage.
4. Verify labels, instructions, and error messaging clarity.
5. Verify that reduced-motion preference preserves task completion.
6. Verify responsive behavior preserves comprehension and actionability.

## Accessibility Option Set for UI Components

Treat this section as the accessibility source of truth for component design in `ui` mode.

1. Focus: include visible `focus-visible` styles with strong contrast and non-color-only indication.
2. Keyboard: support tab order, Enter/Space activation, Escape handling where applicable, and no keyboard traps.
3. Naming: provide accessible names via visible labels, `aria-label`, or `aria-labelledby`.
4. State semantics: expose `disabled`, `invalid`, `required`, expanded/collapsed, and selected states correctly.
5. Feedback: announce validation and async status with clear text and semantic roles where needed.
6. Contrast: maintain readable text/icon contrast for default, hover, active, focus, and disabled states.
7. Motion safety: provide reduced-motion-safe behavior for transitions and feedback animations.

## Audit Workflow and Axes

Use this workflow when auditing existing UI code or built interfaces.

1. Confirm files, routes, or components in scope.
2. Confirm target surface and known constraints.
3. Evaluate hierarchy and information architecture.
4. Evaluate spacing and layout consistency.
5. Evaluate typography and readability.
6. Evaluate color contrast and semantic clarity.
7. Evaluate interaction states and feedback quality.
8. Evaluate motion quality and reduced-motion compliance.
9. Evaluate responsive behavior.
10. Evaluate microcopy and content clarity (labels, errors, empty states, instructions).
11. Evaluate implementation risks and maintainability.

## Severity Scale

Use one severity level per finding:

1. `Critical`: blocks task completion, creates severe accessibility failures, or introduces high-impact risk.
2. `High`: creates serious friction or likely failure in core flows.
3. `Medium`: creates noticeable friction or confusion with moderate impact.
4. `Low`: creates polish or clarity issues with limited impact.

## Findings Format

List findings first, ordered by severity. For each finding include:

1. Severity (`Critical` | `High` | `Medium` | `Low`).
2. Issue title.
3. Impact and risk.
4. File and line reference when available.
5. Concrete fix recommendation.

Use this default structure unless the user requests another format:

1. `## Findings`
2. `### [Severity] Issue title`
3. `Impact: ...`
4. `Evidence: file:line ...`
5. `Fix: ...`
6. `## Residual Risks / Test Gaps`

If no issues are found, state that explicitly and list residual risks or test gaps.

## Guideline-Driven Audit Procedure

When asked to audit against web interface guidelines:

1. Fetch fresh rules from:
`https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`
2. Apply all relevant rules to reviewed files.
3. Output findings in the exact format required by that guideline.
4. Follow terse `file:line` formatting exactly when required.
5. Do not skip applicable rules silently.

## UX Output Contracts

For UX design requests, deliver:

1. Updated task flow and IA rationale.
2. Prioritized UX changes with expected outcome.
3. Accessibility and usability risk notes.
4. Explicit assumptions and open risks.

For UX audit requests, deliver:

1. Severity-ordered findings first.
2. Evidence with file/line references where possible.
3. Clear, actionable fixes.
4. Residual risks and testing gaps.
