# design

Route each design request to the correct mode, then execute that mode's output contract with shared quality constraints.

This is a nested router: `/cobb design <mode>` selects a design mode (`ui`, `ux`, `motion`, `imagery`). If no mode is given, infer the primary mode from the request using the routing decision tree below.

## Core Workflow

1. Select a primary mode from the mode map in this file.
2. Select one secondary mode only when the request clearly spans multiple concerns.
3. Fill the mandatory routing brief before producing output. If inputs are missing, state explicit assumptions.
4. Load only the reference files required for the chosen mode(s); never preload every `references/design/*.md` file.
5. Deliver the primary mode contract completely; add secondary mode deltas without diluting the primary outcome.

## Mode Map

Select one primary mode before work starts. Add one secondary mode only when needed.

1. `ui`
Typical request patterns: build or refine screens, components, dashboards, landing pages, settings, and app flows.
Primary goal: ship clear and distinctive interfaces.
Expected deliverables: working UI code, token mapping, full state coverage, concise hierarchy rationale.
Load reference: `references/design/ui.md`.
Load `references/design/ui-examples.md` only when concrete config/component snippets are needed, especially for `5` or `7` tier token sets.
Load `references/design/ux.md` only when UX is selected as a secondary mode, the request asks for accessibility/flow audit depth, or the UI reference explicitly says the compact baseline is insufficient.

2. `ux`
Typical request patterns: plan or improve flows, IA, usability, accessibility, or run design audits.
Primary goal: improve task success, comprehension, and evidence-based quality.
Expected deliverables: UX structure outputs or severity-ordered audit findings with concrete fixes.
Load reference: `references/design/ux.md`.

3. `motion`
Typical request patterns: define or implement transitions, microfeedback, loading, and continuity behavior.
Primary goal: communicate state change and preserve orientation without friction.
Expected deliverables: motion spec or code, timing/easing choices, reduced-motion fallback.
Load reference: `references/design/motion.md`.

4. `imagery`
Typical request patterns: produce posters, editorial visuals, and static compositions.
Primary goal: deliver high-impact static visual artifacts.
Expected deliverables: philosophy `.md` plus `.png` or `.pdf` artifact (single page unless requested).
Load reference: `references/design/imagery.md`.

### Selection Rules

1. Select `ui` for implementation-heavy interface design and visual system decisions.
2. Select `ux` for information architecture, usability, accessibility, or audit-heavy requests.
3. Select `motion` when behavior choreography is the core task.
4. Select `imagery` for non-interactive visual composition outputs.
5. When requests blend concerns, keep one primary mode and one secondary mode.

### Routing Decision Tree

Use this sequence to select the primary mode:

1. If the request is for a non-interactive visual artifact (`.png`, `.pdf`, poster, editorial composition), select `imagery`.
2. If the request is primarily about IA, usability, accessibility, or audits, select `ux`.
3. If the request is primarily about transitions, microfeedback, choreography, or reduced-motion behavior, select `motion`.
4. If the request is primarily about building/refining interface code, components, layout, or visual systems, select `ui`.

Then add one secondary mode only when required:

1. Use `ux` as secondary to `ui` when task flow or accessibility structure changes are a core part of the implementation.
2. Use `motion` as secondary to `ui` when animation behavior is explicitly in scope.
3. Use `motion` as secondary to `ux` when motion quality or reduced-motion compliance is a key audit axis.
4. Keep `imagery` standalone by default; add a secondary mode only when the user explicitly asks for a companion interactive adaptation.

Do not read secondary-mode references speculatively. Decide the mode(s), state the routing choice, then read only those files.

### Complexity Budget

Choose one level early and stay consistent:

1. `baseline`: practical, concise, low-risk execution.
2. `expressive`: clear personality with controlled complexity.
3. `maximal`: high visual and motion complexity with strict quality control.

Default to `baseline` for internal or time-constrained work. Default to `expressive` for most public-facing work. Use `maximal` only when the brief explicitly rewards spectacle and budget supports it.

### Calibration Dials

Set these 1-10 dials after the routing brief when designing UI, UX, or motion. They tune choices without loading extra references.

1. `variance`: layout experimentation and visual surprise.
   - `1-3`: predictable, symmetric, compliance-heavy.
   - `4-7`: offset, composed, recognisable but not generic.
   - `8-10`: highly asymmetric, editorial, art-directed.
2. `motion`: amount of animation and choreography.
   - `1-3`: static or basic hover/focus feedback.
   - `4-7`: purposeful transitions and staged reveals.
   - `8-10`: cinematic or physics-heavy motion with strict performance checks.
3. `density`: information per viewport.
   - `1-3`: airy, campaign, portfolio, editorial.
   - `4-7`: normal product app or landing page.
   - `8-10`: dashboards, monitoring, admin, operational tools.

Default mapping:

1. `baseline`: `variance 3-5`, `motion 1-3`, `density 5-7`.
2. `expressive`: `variance 5-7`, `motion 3-5`, `density 4-6`.
3. `maximal`: `variance 7-9`, `motion 6-8`, `density 3-5`.

Override the defaults for regulated, accessibility-critical, or operational software: lower `variance` and `motion`, raise `density` only when scan speed matters.

## Mandatory Routing Brief

Complete this brief before solution design:

```text
Primary mode:
Secondary mode (optional):
Request type (new design, refinement, audit, artifact):
Human and audience:
Primary task to enable:
Context and constraints:
Complexity budget (baseline | expressive | maximal):
Calibration dials (variance / motion / density):
Output artifact(s) required:
Success criteria:
```

## Global Non-Negotiables

Apply these across all modes:

1. Preserve accessibility fundamentals (contrast, keyboard reachability, visible focus, reduced-motion support).
2. Preserve responsive intent across mobile and desktop where screens are involved.
3. Preserve performance by preferring efficient rendering and animation primitives.
4. Cover required interaction and data states for any interactive surface.
5. Keep decisions explainable with concrete rationale tied to the request and constraints.
6. Layouts must tolerate longer copy, dynamic data, and localisation (wrapping, truncation rules, min/max widths).

## References

- `references/design/ui.md`: interface craft system, tokens, component rules, output contract, and quality checks.
- `references/design/ui-examples.md`: concrete Tailwind and component examples for 3/5/7 tier token systems.
- `references/design/ux.md`: UX structure, usability/accessibility checks, and audit workflow/report format.
- `references/design/motion.md`: motion purpose, timing/easing, performance, accessibility, and motion delivery contract.
- `references/design/imagery.md`: static visual artifact workflow and required output format.
