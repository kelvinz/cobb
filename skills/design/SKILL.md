---
name: design
description: "Router-first workflow for high-craft design execution across four modes: ui, ux, motion, and imagery. Use when designing or refining interfaces, structuring and auditing UX/usability/accessibility, implementing or specifying interaction motion, or producing static visual artifacts (.png/.pdf) with a matching philosophy note. Triggers: design ui, improve ux flow, run design audit, add transitions, reduce motion issues, create visual imagery, craft poster composition."
---

# Design

Route each design request to the correct mode, then execute that mode's output contract with shared quality constraints.

## Core Workflow

1. Select a primary mode from the mode map in this file.
2. Select one secondary mode only when the request clearly spans multiple concerns.
3. Fill the mandatory routing brief before producing output. If inputs are missing, state explicit assumptions.
4. Load only the reference files required for the chosen mode(s).
5. Deliver the primary mode contract completely; add secondary mode deltas without diluting the primary outcome.

## Mode Map

Select one primary mode before work starts. Add one secondary mode only when needed.

1. `ui`
Typical request patterns: build or refine screens, components, dashboards, landing pages, settings, and app flows.
Primary goal: ship clear and distinctive interfaces.
Expected deliverables: working UI code, token mapping, full state coverage, concise hierarchy rationale.
Load reference: `references/ui.md`.
Load `references/ui-examples.md` only when concrete code examples are needed, especially for `5` or `7` tier token sets.

2. `ux`
Typical request patterns: plan or improve flows, IA, usability, accessibility, or run design audits.
Primary goal: improve task success, comprehension, and evidence-based quality.
Expected deliverables: UX structure outputs or severity-ordered audit findings with concrete fixes.
Load reference: `references/ux.md`.

3. `motion`
Typical request patterns: define or implement transitions, microfeedback, loading, and continuity behavior.
Primary goal: communicate state change and preserve orientation without friction.
Expected deliverables: motion spec or code, timing/easing choices, reduced-motion fallback.
Load reference: `references/motion.md`.

4. `imagery`
Typical request patterns: produce posters, editorial visuals, and static compositions.
Primary goal: deliver high-impact static visual artifacts.
Expected deliverables: philosophy `.md` plus `.png` or `.pdf` artifact (single page unless requested).
Load reference: `references/imagery.md`.

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

### Complexity Budget

Choose one level early and stay consistent:

1. `baseline`: practical, concise, low-risk execution.
2. `expressive`: clear personality with controlled complexity.
3. `maximal`: high visual and motion complexity with strict quality control.

Default to `baseline` for internal or time-constrained work. Default to `expressive` for most public-facing work. Use `maximal` only when the brief explicitly rewards spectacle and budget supports it.

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

- `references/ui.md`: interface craft system, tokens, component rules, output contract, and quality checks.
- `references/ui-examples.md`: concrete Tailwind and component examples for 3/5/7 tier token systems.
- `references/ux.md`: UX structure, usability/accessibility checks, and audit workflow/report format.
- `references/motion.md`: motion purpose, timing/easing, performance, accessibility, and motion delivery contract.
- `references/imagery.md`: static visual artifact workflow and required output format.
