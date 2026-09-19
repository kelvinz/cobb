# design

Route a design request to one primary mode and, only when necessary, one secondary mode.

Shared guardrails from the cobb router apply; the rules below are design-specific.

## Function Before Form

Get the function right before the form. For work that creates or changes a surface, settle the UX layer first: task flow, information architecture, content and copy, states, and accessibility structure. Set the UI layer after it: layout, visual system, and motion.

- When a request needs both `ux` and `ui`, run `ux` first, whatever the order of the request's words.
- The UX layer is settled when the PRD or an approved artifact records it, or when the change extends an existing surface without changing its flow. Otherwise a UI decision waits for the UX decision it depends on.
- Audits report functional findings before visual ones, and fix plans repair function before form.
- In implementation, make it work before making it look right: structure, semantics, states, keyboard access, and copy first, then the visual layer.

## Workflow

1. Honour a recognised first argument: a mode (`ui`, `ux`, `motion`, or `imagery`), or `record` for Record delivery. Remove only that word from the input. Otherwise infer the mode and delivery from the request and repository evidence.
2. Add one secondary mode only when essential to the requested outcome.
3. If routing remains ambiguous, ask which mode to use.
4. Complete the routing brief, including Delivery. Find discoverable inputs in the repository; ask the remaining choices in rounds under the shared interview rule.
5. Complete preflight (see Delivery) before editing application files.
6. Load only the selected mode reference and conditional child references below.
7. Deliver the primary contract completely, then only the necessary secondary-mode details. When `ux` is one of the two modes, deliver it first.

## Mode Selection

Use the reference for an explicit mode. Only when no explicit mode was supplied, apply the first matching rule:

1. `imagery`: non-interactive `.png`/`.pdf`/animated `.svg`, poster, cover, or editorial composition.
   - Load `references/design/imagery.md`.
2. `ux`: information architecture, usability, accessibility, flow planning, copy, or audits.
   - Load `references/design/ux.md`.
3. `motion`: transitions, microfeedback, choreography, gestures, or reduced-motion behaviour are the core task.
   - Load `references/design/motion.md`.
4. `ui`: interface code, components, layout, visual hierarchy, or design-system work.
   - Load `references/design/ui.md`.

Secondary-mode rules:

- When a `ui` request changes task flow, information architecture, states, copy, or accessibility structure and the UX layer is not settled, run `ux` first and `ui` second.
- Add `motion` to `ui` or `ux` only when motion is explicitly in scope.
- Keep `imagery` standalone unless the user asks for an interactive adaptation.

Conditional references (canonical load conditions; other files defer here):

- Load `references/design/ui-product.md` for Operate and Read surfaces.
- Load `references/design/ui-marketing.md` for Persuade and Experience surfaces.
- Load `references/design/ui-tokens.md` only when creating or materially changing a Tailwind/token system.
- Load `references/design/ui-examples.md` only when concrete token, config, or component snippets are needed.
- Load `references/design/ui-shadcn.md` only when creating or changing shadcn/ui components.
- Load `references/design/ui-systems.md` only when the brief maps to an official product ecosystem and a design-system choice is needed.
- Load `references/design/ethics.md` when the surface touches consent, pricing or checkout, subscriptions or trials, cancellation or account deletion, notifications, data collection or sharing, AI decisions that affect users, or products for children.
- Load `references/design/visual-verification.md` for implementation or audit of working UI.
- Load `references/templates/design-md-template.md` when creating or refreshing the root `DESIGN.md`.

## Delivery

- **Direction:** default for design planning and handoffs before implementation. Deliver the UX specification (flow, information architecture, state inventory, copy) before the UI specification (layout, visual system, motion). Record feature-level direction in the PRD's experience section and keep application code unchanged. Direction needs a PRD to record into: when none covers the surface, load `references/prd.md` with caller `design` and run it now, without a separate prompt. Its interview settles the UX layer. Then continue here and fill the PRD's visual direction block.
- **Audit:** return findings and proposed changes read-only, unless implementation is explicitly requested.
- **Implementation:** use only when the user or calling implementation workflow explicitly requests working code. First complete **preflight**: the Identify the PRD and Preflight steps in `references/implement.md`, including ready scope and branch confirmation. Reuse valid checks already completed by the caller, including its optional design handoff. For an authorised review repair, use that file's Review-Repair Mode instead.
- **Artifact:** create requested non-interactive imagery exports under imagery mode. This permits the requested artifact files, not unrelated application changes.
- **Record:** create or refresh the root `DESIGN.md` from the existing codebase under Design Record below. This permits writing `DESIGN.md` only. It needs no PRD and no mode reference: load only the template. `/cobb commit` commits the result.

The delivery kind takes precedence over a child reference's examples or code suggestions. A pre-implementation design handoff always uses `direction`.

## Visitor Mode

Choose the mode from the surface, not the product. It names what success looks like for the visitor:

- **Persuade:** the visitor decides and acts. Landing, marketing, campaign, and pricing pages.
- **Operate:** the visitor completes a task. App UI, dashboards, editors, admin, settings, and tools.
- **Read:** the visitor understands something. Docs, articles, guides, help, and changelogs.
- **Experience:** the visitor is inside the work. Portfolios, galleries, and showcases.

A tool's landing page is Persuade, its settings page is Operate, and a docs index is Read.

## Scale to the Change

Match the design effort to the change kind in the routing brief:

1. **Extend or refine** an existing surface: inherit its look and composition. Resolve only the new purpose, content, hierarchy, states, and interaction. No exploration, and no `DESIGN.md` change unless the user approves a system change.
2. **New surface** inside an established system: keep the visual system fixed and explore structure only. Compare two or three layouts as text wireframes before building.
3. **New identity or redesign:** settle the UX layer, then run the Direction Round in `references/design/ui.md`.

## Extend, Refine, and Redesign

Classify every change to an existing surface before designing it:

- **Extend** adds a section, component, state, or feature inside the surface and inherits its look.
- **Refine** preserves identity, behaviour, copy, and everything outside scope. Ask before replacing factual copy or adding claims. If the concept itself is wrong, say so and recommend a redesign instead of changing the concept quietly.
- **Redesign** keeps product truth, content, function, information architecture, and constraints, but replaces the look. Treat the old look as evidence, not authority, and never polish the discarded look.

**Protected items.** Every kind leaves these unchanged unless the PRD scopes them: URL structure and route slugs, primary navigation labels, form field names and order, analytics event names and the element IDs they depend on, the logo or wordmark, and legal, consent, or cookie copy. Before redesigning public pages, record the SEO baseline: titles, meta descriptions, structured data, and social cards.

## Artifacts by Decision

Match the artifact to the decision on the table, in function-first order. Never present more fidelity than the decision needs: a styled artifact draws styling feedback and stalls structural questions.

1. **Which mechanism solves the problem:** several idea sketches, each a focused fragment of real UI with a one-line caption.
2. **What a screen holds and how it is weighted:** a text wireframe in the PRD, or a grayscale HTML wireframe when text cannot show the structure.
3. **Whether a sequence works as a task:** a clickable prototype that links those wireframes along the flow.
4. **How it looks and feels:** working variants behind a picker.

A later rung starts only after the decision it depends on is settled. Rules for rungs 1 to 3 are in `references/design/ux.md` and for rung 4 in `references/design/ui.md`. Prototypes live outside product code; the verdict goes into the PRD as a `D-###` decision.

## Design Record

The root `DESIGN.md` records the durable visual system in the portable format of `references/templates/design-md-template.md`: token frontmatter and eight fixed sections.

- Read it before any UI work. With the repository's token files, it is the visual authority; a PRD's visual direction overrides it for that feature only.
- Record the system as built, never as planned. Write a new or replaced system after the build. A UI change that alters tokens, type roles, or component styles updates it in the same commit, under the freshness rule in `references/context-log.md`.
- Use Record delivery for a project that already has a coherent look but no record.

## Complexity And Calibration

Choose one complexity budget:

1. `baseline`: practical, concise, low risk. The default for Operate and Read surfaces, and recommended for internal, regulated, accessibility-critical, or time-constrained work.
2. `expressive`: controlled personality. The default for Persuade and Experience surfaces.
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
Delivery (direction | audit | implementation | artifact | record):
Visitor mode (persuade | operate | read | experience):
Change kind (extend | refine | new surface | new identity | redesign):
UX layer (settled, and where recorded | open):
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

1. Cover every reachable state in the PRD's state inventory, with its recovery path.
2. Preserve contrast, keyboard access, visible focus, and reduced-motion support; target WCAG 2.2 AA unless the PRD names another level.
3. Tolerate longer copy, dynamic data, and localisation.
4. Preserve responsive intent across relevant viewport sizes.
5. Tie decisions to the request, repository conventions, `DESIGN.md`, and constraints.
6. Prefer efficient rendering and animation primitives.
