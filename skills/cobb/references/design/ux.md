# UX Mode

Use this mode to shape task flows, information architecture, copy, usability, accessibility, and audit quality. UX comes before UI under Function Before Form in `references/design.md`. Follow the Delivery contract there before applying changes.

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
6. Define empty, error, and recovery paths as first-class flows, using the state inventory in the PRD template.
7. Answer wayfinding on every screen: where am I, where can I go, what will I find there, and how do I get out. Never trap the user.

## Wireframes and Prototypes

Use these under Artifacts by Decision in `references/design.md`:

1. **Idea sketches** answer which mechanism solves the problem. Build several structurally different fragments of real UI, each at natural size with a one-line caption. Many quick sketches beat one full screen while the mechanism is open.
2. **Grayscale wireframes** answer what a screen holds and how it is weighted. Every element that will exist is present, with real labels, hierarchy through size, weight, and placement, and working controls. Use a grayscale ramp, one accent on primary actions and selection, one neutral font, and grey boxes for images. A text wireframe in the PRD is enough when layout, not interaction, is in question.
3. **Clickable prototypes** answer whether a sequence works as a task. Link the wireframes' real trigger elements along the flow.

Call each artifact a wireframe in its title and in the reply. It looks real so the structure can be judged; the styling does not exist yet.

## Content Hierarchy and Clarity Heuristics

1. Make the primary task visually and semantically obvious within seconds.
2. Keep one dominant focus per view whenever possible.
3. Make status, feedback, and next action explicit after each key action.
4. Place controls near what they affect and arrange them to mirror what they change; if a control needs a label to explain what it does, the mapping is weak.
5. Cover four feedback kinds — status, completion, warning, and error — and validate inline rather than only on submit.

## UX Copy

Copy is part of the function: it tells people what happened and what to do next. Use the `## Language` section of `tasks/context.md` for every product term.

1. For each state, decide the one fact the user needs now, the next action, the context that changes the decision, and the tone for the moment. Say each idea once.
2. Labels name the outcome with a verb and an object ("Save changes", not "Submit"). An action keeps its name through the flow: a "Publish" button leads to a "Published" confirmation.
3. Use the same noun and verb for the same concept everywhere, and name things by what users understand ("notifications", not "webhook config").
4. Errors say what happened and how to recover, in the interface's voice, without apology or vagueness. Place each error next to the field or action it concerns.
5. Empty states say what will appear and offer the first action.
6. Use sentence case, plain verbs, and active voice. Give each text element one job.

**Copy self-audit.** Before shipping, re-read every visible string, including labels, errors, empty states, alt text, and captions. Rewrite any string that:

- is grammatically broken or has an unclear referent
- uses cute wordplay, forced metaphors, or filler verbs such as "elevate", "seamless", or "unleash"
- shows precise-looking numbers that are not sourced from the brief or product evidence and not labelled as sample data
- uses placeholder names such as "John Doe" or "Acme"
- mixes registers the brand voice does not call for

## Accessibility Option Set for UI Components

Use this section as the deeper accessibility reference for `ui` mode; the compact baseline in `references/design/ui.md` covers routine UI work, and this fuller set applies when more UX/accessibility depth is needed. Target WCAG 2.2 AA unless the PRD names another level.

1. Focus: include visible `focus-visible` styles with strong contrast and non-color-only indication.
2. Keyboard: support tab order, Enter/Space activation, Escape handling where applicable, and no keyboard traps.
3. Naming: provide accessible names via visible labels, `aria-label`, or `aria-labelledby`.
4. State semantics: expose `disabled`, `invalid`, `required`, expanded/collapsed, and selected states correctly.
5. Feedback: announce validation and async status with clear text and semantic roles where needed.
6. Contrast: maintain readable text/icon contrast for default, hover, active, focus, and disabled states.
7. Motion safety: provide reduced-motion-safe behavior for transitions and feedback animations.
8. Responsiveness: preserve comprehension and actionability across viewport and text sizes.
9. Target size: at least 24×24 CSS px, and 44×44 for primary touch targets with 8px between targets. Measure the hit area, not the glyph; inline text links are exempt.
10. Focus not obscured: sticky headers, toasts, and overlays never hide the focused element.
11. Dragging: every drag interaction has a single-pointer alternative, such as move up and move down buttons.
12. Redundant entry: never ask again for information given earlier in the same process; offer "same as" options and autocomplete.
13. Accessible authentication: allow paste in password and code fields, support password managers and passkeys, and offer an alternative to puzzles.
14. Time limits: warn before a session or timed action expires and let the user extend it; let users pause auto-updating content.

## Audit Workflow and Axes

Use this workflow when auditing existing UI code or built interfaces. Evaluate function before form: steps 2 to 9 come before any visual finding.

1. Confirm the files, routes, or components in scope, the target surface, and known constraints.
2. Run a cognitive walkthrough of each key task. At every step, ask four questions:
   - Motivation: will the user try to achieve the right effect?
   - Visibility: will the user notice that the correct action is available?
   - Understanding: will the user connect that action with the outcome they want?
   - Feedback: after acting, will the user see progress?
   Rate each step pass (all yes), hesitation (one no), or failure (two or more). A no on motivation is the most severe: the user will not even try.
3. Walk the key tasks through two or three persona lenses chosen for the surface, and name the exact element and step that fails each one:
   - power user: keyboard paths, repeated actions, and efficiency
   - first-timer: jargon, discoverability, and where to start
   - accessibility-dependent user: screen reader order, keyboard only, and zoom to 200 percent
   - stress tester: extreme inputs, errors, double submits, and interrupted flows
   - distracted mobile user: one hand, interruptions, and a slow network
4. Evaluate information architecture, wayfinding, and cognitive load. Flag decision points with more than four visible options and flows that rely on memory from earlier screens.
5. Evaluate states and feedback against the state inventory.
6. Evaluate accessibility against the option set above.
7. Evaluate copy against UX Copy.
8. Run the dark-pattern check in `references/design/ethics.md` when the surface is in its scope.
9. Evaluate responsive behaviour and the mobile web baseline in `references/design/ui.md`.
10. Then evaluate form: hierarchy, spacing and layout consistency, typography, colour and contrast, and motion quality with reduced-motion compliance.
11. Evaluate implementation risks and maintainability.

For redesigns, confirm the change kind under Extend, Refine, and Redesign in `references/design.md` first, then run `scan -> diagnose`; apply `fix` only for implementation delivery after preflight:

1. `scan`: identify framework, styling method, component primitives, routes, and current design patterns.
2. `diagnose`: list broken tasks, missing states, accessibility failures, weak hierarchy, generic patterns, and implementation risks before changing files.
3. `fix` (implementation only): apply focused upgrades inside the existing stack in the Redesign Fix Priority order. Direction and audit delivery describe these upgrades without changing application code. Rewrite from scratch only when the existing structure blocks the requested outcome.

## Redesign Fix Priority

Fix function before form, and bring the whole path to the same bar before perfecting one corner:

1. Broken or blocked tasks, data loss, misleading state, and inaccessible paths.
2. Missing states and feedback: loading, empty, error, success, disabled, and permission.
3. Flow, information architecture, and copy clarity: vague labels, invented precision, placeholder copy, and mixed voice.
4. Layout and responsive behaviour: max-widths, grids, mobile collapse, alignment, and repeated section patterns.
5. Typography: default fonts, weak headings, line length, hierarchy weights, and tabular numbers.
6. Colour and surfaces: clashing accents, inconsistent grey families, low contrast, and generic shadows.
7. Generic components: cliché cards, fake screenshots, decorative labels, and redundant calls to action.
8. Polish: spacing, motion, depth, and responsive edge cases.

## Severity Scale

Use one severity level per finding:

1. `Critical`: blocks task completion, creates severe accessibility failures, or introduces high-impact risk.
2. `High`: creates serious friction or likely failure in core flows.
3. `Medium`: creates noticeable friction or confusion with moderate impact.
4. `Low`: creates polish or clarity issues with limited impact.

## Findings Format

List findings first, ordered by severity, and within one severity put functional findings before visual ones. For each finding include:

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

## Polish Review Table

For design-polish reviews where the user asks for refinement guidance rather than a bug/risk audit, use a compact markdown table:

| Before | After | Why |
| --- | --- | --- |
| Current pattern or code | Recommended change | Practical design reason |

Use one row per issue. Keep severity-ordered findings first when the request is a branch review, accessibility audit, correctness review, or risk review.

## Guideline-Driven Audit Procedure

When asked to audit against web interface guidelines:

1. Fetch fresh rules from:
`https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`
2. Apply all relevant rules to reviewed files.
3. Output findings in the exact format required by that guideline.
4. Follow terse `file:line` formatting exactly when required.
5. Do not skip applicable rules silently.
6. If the fetch fails or the content does not look like interface guidelines, fall back to the Audit Workflow and Axes above and note in the output that the external guideline set was unavailable.

## UX Output Contracts

For UX design requests, deliver:

1. Updated task flow and IA rationale.
2. The state inventory and the copy for key states.
3. Prioritized UX changes with expected outcome.
4. Accessibility and usability risk notes.
5. Explicit assumptions and open risks.

For UX audit requests, deliver:

1. Walkthrough ratings per task step and persona red flags.
2. Severity-ordered findings, function before form.
3. Evidence with file/line references where possible.
4. Clear, actionable fixes.
5. Residual risks and testing gaps.
