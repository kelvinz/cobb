# design

Route a design request to one primary mode and, only when necessary, one secondary mode.

## Workflow

1. Infer the primary mode from the request and repository evidence.
2. Add one secondary mode only when it is essential to the requested outcome.
3. If routing is genuinely ambiguous, present numbered mode choices and mark one **Recommended** with a short reason.
4. Complete the routing brief. Explore the repository before asking for discoverable inputs.
5. If several user questions remain, build the queue first and label them `Question X of Y`; ask one at a time.
6. Load only the selected mode reference and conditional child references named below.
7. Deliver the primary mode contract completely, then add only the necessary secondary-mode deltas.

## Mode Selection

Apply the first matching rule:

1. `imagery`: non-interactive `.png`/`.pdf`, poster, cover, or editorial composition.
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

Conditional UI references:

- Load `references/design/ui-tokens.md` only when creating or materially changing a Tailwind/token system.
- Load `references/design/ui-examples.md` only when concrete token or component snippets are needed.

Do not load secondary or conditional references speculatively.

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
Request type (new design | refinement | audit | artifact):
Human and audience:
Primary task:
Constraints:
Complexity budget:
Calibration dials (variance / motion / density):
Required artifacts:
Success criteria:
```

If the brief needs user choices, number them, mark one **Recommended**, and show `Question X of Y` for a sequence. Use explicit assumptions for low-risk reversible gaps instead of unnecessary questions.

## Global Requirements

1. Preserve contrast, keyboard access, visible focus, and reduced-motion support.
2. Preserve responsive intent across relevant viewport sizes.
3. Prefer efficient rendering and animation primitives.
4. Cover required interaction, data, empty, loading, error, and recovery states.
5. Tie decisions to the request, repository conventions, and constraints.
6. Tolerate longer copy, dynamic data, and localisation.

## Output

End with the shared status block. If a user decision remains, provide numbered options and mark exactly one **Recommended**.
