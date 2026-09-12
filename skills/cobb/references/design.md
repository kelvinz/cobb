# design

Route a design request to one primary mode and, only when necessary, one secondary mode.

Shared guardrails from the cobb router apply; the rules below are design-specific.

## Workflow

1. Honour a recognised first mode argument (`ui`, `ux`, `motion`, or `imagery`) and remove only that word from the mode's input. Otherwise infer the mode from the request and repository evidence.
2. Add one secondary mode only when essential to the requested outcome.
3. If routing remains ambiguous, ask which mode to use.
4. Complete the routing brief, including Delivery. Find discoverable inputs in the repository; ask about remaining choices one at a time.
5. Complete preflight (see Delivery) before editing application files.
6. Load only the selected mode reference and conditional child references below.
7. Deliver the primary contract completely, then add only necessary secondary-mode details.

## Mode Selection

Use the reference for an explicit mode. Only when no explicit mode was supplied, apply the first matching rule:

1. `imagery`: non-interactive `.png`/`.pdf`/animated `.svg`, poster, cover, or editorial composition.
   - Load `references/design/imagery.md`.
2. `ux`: information architecture, usability, accessibility, flow planning, or audits.
   - Load `references/design/ux.md`.
3. `motion`: transitions, microfeedback, choreography, gestures, or reduced-motion behaviour are the core task.
   - Load `references/design/motion.md`.
4. `ui`: interface code, components, layout, visual hierarchy, or design-system work.
   - Load `references/design/ui.md`.

Secondary-mode rules:

- Add `ux` to `ui` when task flow or accessibility structure materially changes.
- Add `motion` to `ui` or `ux` only when motion is explicitly in scope.
- Keep `imagery` standalone unless the user asks for an interactive adaptation.

Conditional UI references (canonical load conditions — other files defer here):

- Load `references/design/ui-tokens.md` only when creating or materially changing a Tailwind/token system.
- Load `references/design/ui-examples.md` only when concrete token, config, or component snippets are needed.
- Load `references/design/ui-shadcn.md` only when creating or changing shadcn/ui components.
- Load `references/design/ui-marketing.md` only for landing pages, portfolios, or marketing surfaces.
- Load `references/design/ui-systems.md` only when the brief maps to an official product ecosystem and a design-system choice is needed.

## Delivery

- **Direction:** default for design planning and handoffs before implementation. Deliver specifications and design documents; keep application code unchanged.
- **Audit:** return findings and proposed changes read-only, unless implementation is explicitly requested.
- **Implementation:** use only when the user or calling implementation workflow explicitly requests working code. First complete **preflight**: the Identify the PRD and Preflight steps in `references/implement.md`, including ready scope and branch confirmation. Reuse valid checks already completed by the caller; do not restart its optional design handoff. For an authorised review repair, use that file's Review-Repair Mode instead.
- **Artifact:** create requested non-interactive imagery exports under imagery mode. This permits the requested artifact files, not unrelated application changes.

The delivery kind takes precedence over a child reference's examples or code suggestions. A pre-implementation design handoff always uses `direction`.

## Complexity And Calibration

Choose one complexity budget:

1. `baseline`: practical, concise, low risk. Recommended for internal, regulated, accessibility-critical, or time-constrained work.
2. `expressive`: controlled personality. Recommended for most public-facing work.
3. `maximal`: high visual/motion complexity. Use only when spectacle is explicit and the performance/accessibility budget supports it.

Set three 1-10 dials:

- `variance`: layout experimentation; `1-3` predictable, `4-7` composed, `8-10` art-directed.
- `motion`: animation intensity; `1-3` feedback only, `4-7` purposeful transitions, `8-10` choreography-heavy.
- `density`: information per viewport; `1-3` airy/editorial, `4-7` normal product UI, `8-10` operational/dense.

Defaults:

- `baseline`: variance `3-5`, motion `1-3`, density `5-7`.
- `expressive`: variance `5-7`, motion `3-5`, density `4-6`.
- `maximal`: variance `7-9`, motion `6-8`, density `3-5`.

Lower variance/motion for regulated or accessibility-critical software. Raise density only when scan speed matters.

## Routing Brief

Complete before solution design:

```text
Primary mode:
Secondary mode (optional):
Delivery (direction | audit | implementation | artifact):
New design or refinement:
Human and audience:
Primary task:
Constraints:
Complexity budget:
Calibration dials (variance / motion / density):
Required artifacts:
Success criteria:
```

Use explicit assumptions for low-risk reversible gaps instead of unnecessary questions.

## Global Requirements

1. Preserve contrast, keyboard access, visible focus, and reduced-motion support.
2. Preserve responsive intent across relevant viewport sizes.
3. Prefer efficient rendering and animation primitives.
4. Cover required interaction, data, empty, loading, error, and recovery states.
5. Tie decisions to the request, repository conventions, and constraints.
6. Tolerate longer copy, dynamic data, and localisation.
