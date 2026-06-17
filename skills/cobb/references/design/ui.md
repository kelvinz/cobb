# UI Mode

Use this mode to design or refine interactive interfaces and component systems.

## Table of Contents

1. Output Contract
2. Reference Loading Rules
3. Project Constraint Detection
4. Official Design System Fit
5. Subject-Specific Design Pass
6. Project Component Library
7. Tailwind-First Implementation
8. Styling Topology
9. Global Token System
10. Example Library
11. Shadcn State Pattern Extraction
12. Intent and Anti-Default Checklist
13. Per-Component Checkpoint
14. Visual Rules
15. Microinteraction Details
16. Landing and Marketing Guardrails
17. Interaction and Data State Coverage
18. Compact Accessibility Baseline
19. Expression vs Clarity Scaling
20. Anti-Patterns
21. Quality Checks

## Output Contract

Deliver all of the following for UI work:

1. Ship working code for the requested surface or component.
2. Map color, spacing, and type decisions to an explicit token system.
3. Cover relevant interaction and data states.
4. Include a brief hierarchy rationale tied to task goals.
5. Preserve responsive behavior on mobile and desktop when applicable.
6. Use Tailwind CSS for examples and implementation when project constraints allow.
7. Default component styling to inline Tailwind utilities.
8. Apply the compact accessibility baseline in this file for routine UI work.

## Reference Loading Rules

Start with this file only.

1. Do not read `references/design/ux.md` by default.
2. Load `references/design/ux.md` only when UX is a selected secondary mode, the request asks for accessibility/flow/audit depth, or this file's compact accessibility baseline is not enough.
3. Load `references/design/ui-examples.md` only when concrete Tailwind config or component snippets are needed.
4. Load `references/design/motion.md` only when motion is a selected secondary mode or the request explicitly asks for transition implementation details.
5. Keep routine UI implementation self-contained in this file.

## Project Constraint Detection

Before writing code, detect the project's existing conventions:

1. Identify the framework (React/Next, Vue, Svelte, Astro, etc.).
2. Identify the styling system (Tailwind, CSS modules, styled-components, vanilla CSS).
3. Identify existing component primitives (shadcn/ui, Radix, MUI, Headless UI, etc.).
4. Locate existing theme/token files if present.
5. Prefer Tailwind when the project already uses it or has no established styling system.
6. When a non-Tailwind styling system is established, follow the repo pattern instead of introducing Tailwind.
7. Before importing any third-party package, check the dependency manifest and add the install command only when the package is missing.

## Official Design System Fit

When the brief clearly maps to an official product ecosystem, use the established design system instead of recreating its look by hand.

1. Microsoft or enterprise productivity: use Fluent UI if the project can support it.
2. Google or Material-flavoured products: use Material components/tokens when already present or appropriate.
3. IBM enterprise analytics: use Carbon where the project already has or expects it.
4. Shopify admin surfaces: use Polaris where applicable.
5. Atlassian-style product work: use Atlassian primitives/tokens when present.
6. GitHub-style developer surfaces: use Primer where present or explicitly requested.
7. UK/US public-sector services: prefer GOV.UK Frontend or USWDS rather than custom approximations.

Use one system per surface. If the project already uses a different established system, follow the project unless the task explicitly asks for migration.

## Subject-Specific Design Pass

Before writing code, define a compact design plan tied to the actual product instead of a reusable template.

1. If the brief is thin, state a concrete subject, audience, and single job for the screen.
2. State the design read in one line: subject, audience, design language, and implementation leaning.
3. Define the product-world source material: domain objects, language, data shapes, rituals, constraints, and visual cues that can drive design choices.
4. Choose one signature element that could only belong to this brief. Spend expressive risk there; keep supporting UI disciplined.
5. Define a compact token plan: palette roles, type roles, layout thesis, and component density. Use named colour roles and map implementation values to existing tokens or Tailwind scale values where possible.
6. Tune the `variance`, `motion`, and `density` dials from `references/design.md` and let them gate layout, animation, and information density.
7. Name three generic defaults to reject and what replaces them. Reject numbered markers unless the content is truly sequential.
8. Treat copy as interface material: use active labels, consistent action vocabulary, and specific empty/error guidance.
9. Critique the plan before implementation. If it still works after swapping in generic fonts, stock cards, and trend colours, revise the weakest part.

## Project Component Library

1. Identify and follow any component library the project already uses (e.g. shadcn/ui, Radix, Headless UI, Chakra, MUI).
2. Before creating a new component, check if the library already provides an existing pattern or primitive that fits the need.
3. Extend or compose library components instead of building from scratch when a suitable base exists.
4. Follow the library's established API conventions, naming patterns, and composition model.
5. Only create a fully custom component when no library primitive can reasonably serve the requirement.

## Tailwind-First Implementation

1. Default to inline Tailwind utility classes in JSX/TSX/HTML for component styling.
2. Treat inline Tailwind as the first-choice pattern, not a fallback pattern.
3. Extract the smallest reusable primitives when class sets repeat, such as `Button`, `Input`, `Badge`, and `CardShell`.
4. Keep Tailwind utility strings inside those primitives so reuse stays local and explicit.
5. Avoid global component CSS for styling primitives.
6. Use examples in Tailwind first; provide raw CSS only when necessary for selectors/utilities that Tailwind cannot express cleanly.

## Styling Topology

Apply this styling hierarchy in order:

1. Component layer (default): inline Tailwind classes inside the smallest reusable components.
2. System layer (global): Tailwind-enabled global stylesheet for token variables, base element defaults, and theme scopes.
3. Exception layer: targeted global rules only for third-party overrides, complex selectors, or browser-specific limitations.

Global CSS still should be Tailwind-first even though it is not inline:

1. Use `@tailwind base`, `@tailwind components`, and `@tailwind utilities`.
2. Use `@layer base` to define token variables and baseline element styling.
3. Use `@layer components` with `@apply` sparingly when a pattern cannot be cleanly expressed through a reusable primitive.
4. Avoid plain hand-written global CSS when Tailwind directives or utilities can express the rule.

## Global Token System

Define one shared Tailwind-first token contract and apply it consistently across all components.
Prefer three options (`sm`, `md`, `lg`) for most token families. Allow five or seven when needed, and never exceed seven.

### Comprehensive Coverage Model

Include all token families below in the system:

1. Color tokens:
structure (`bg`, `fg`, `border`) plus semantic (`brand`, `success`, `warning`, `destructive`, `info`) in Tailwind scale steps.
2. Interaction state tokens:
`default`, `hover`, `active`, `focus-visible`, `disabled`, `invalid`.
3. Typography tokens:
`fontFamily`, `fontSize`, `lineHeight`, `fontWeight`, `letterSpacing`.
4. Spacing and sizing tokens:
layout gaps/padding, control heights, icon sizes.
5. Shape and edge tokens:
radius, border width, ring width, ring offset.
6. Depth tokens:
shadow levels and surface emphasis.
7. Opacity tokens:
use the selected tier set (3, 5, or 7) with three-tier as the default.
8. Motion tokens:
duration and easing tiers aligned with `references/design/motion.md`.
9. Content width tokens:
use the selected tier set (3, 5, or 7) with three-tier as the default.

### Tier Count Rule

Use this default mapping:

1. Spacing keys:
`sm -> 2`, `md -> 4`, `lg -> 8` (for example `gap-2`, `p-4`, `px-8`).
2. Radius keys:
`sm -> rounded-sm`, `md -> rounded-md`, `lg -> rounded-lg`.
3. Type-size keys:
`sm -> text-sm`, `md -> text-base`, `lg -> text-lg`.
4. Control-height keys:
`sm -> h-8`, `md -> h-10`, `lg -> h-12`.
5. Icon-size keys:
`sm -> size-4`, `md -> size-5`, `lg -> size-6`.
6. Opacity keys:
`sm -> opacity-60`, `md -> opacity-80`, `lg -> opacity-100`.
7. Color intensity keys:
`sm -> 400`, `md -> 500`, `lg -> 600` in a single Tailwind color family.

Then apply these tier-count constraints:

1. Use exactly one of these tier counts per token family: `3`, `5`, or `7`.
2. Use `3` tiers by default: `sm`, `md`, `lg`.
3. Use `5` tiers only when finer control is required: `xs`, `sm`, `md`, `lg`, `xl`.
4. Use `7` tiers only for dense systems with proven need: `2xs`, `xs`, `sm`, `md`, `lg`, `xl`, `2xl`.
5. Never exceed `7` tiers.
6. Document why a family uses `5` or `7` instead of `3`.

### Opacity Guide

Treat opacity as a first-class token family:

1. `opacity-sm` (`opacity-60`):
muted icons, supporting labels, subtle separators.
2. `opacity-md` (`opacity-80`):
secondary text/surfaces that still require strong readability.
3. `opacity-lg` (`opacity-100`):
primary text, key actions, and critical affordances.

Avoid ad hoc opacity percentages in reusable components.

### Tailwind Scale Discipline

Anchor all canonical values to Tailwind scales:

1. Colors:
select from Tailwind families (`zinc`, `sky`, `emerald`, `amber`, `red`, `blue`) with scale steps.
2. Spacing and sizing:
use Tailwind keys (`2`, `4`, `8`, `h-8`, `h-10`, `h-12`, `size-4`, `size-5`, `size-6`).
3. Radius and boundaries:
use Tailwind keys (`rounded-sm`, `rounded-md`, `rounded-lg`, `border`, `border-2`, `ring-1`, `ring-2`, `ring-4`).
4. Typography:
use Tailwind utilities (`font-sans`, `text-sm`, `text-base`, `text-lg`, `leading-5`, `leading-6`, `leading-7`).

Avoid arbitrary hex/oklch values and one-off spacing/radius in reusable primitives.

### Tailwind Config Pattern

Apply one consistent tier pattern per token family across all `theme.extend` keys: `colors`, `spacing`, `borderRadius`, `boxShadow`, `opacity`, `fontSize`, `transitionDuration`, `transitionTimingFunction`, etc. Default to three-tier `sm`/`md`/`lg`; use five-tier or seven-tier only when justified. Anchor all values to Tailwind scale families and defaults.

Load `references/design/ui-examples.md` only when concrete Tailwind config and component examples are required.

## Example Library

Load rules for `references/design/ui-examples.md` are defined in `references/design.md` under the `ui` mode entry.

## Shadcn State Pattern Extraction

Use these patterns as baseline state coverage for reusable components. These are extracted from shadcn/ui component source. Preserve the state semantics and normalize raw values into your token system.

1. `Button`
States and semantics: `hover`, `disabled`, `focus-visible`, `aria-invalid`.
Patterns: `disabled:pointer-events-none`, `disabled:opacity-sm`, `focus-visible:ring-2`.
2. `Input`
States and semantics: `placeholder`, `selection`, `disabled`, `focus-visible`, `aria-invalid`.
Patterns: invalid border/ring via `aria-invalid:*` utilities.
3. `TabsTrigger`
States and semantics: `data-[state=active]`, `disabled`, orientation variants, `focus-visible`.
Patterns: active visuals via `data-[state=active]` and orientation-aware styling via group data attributes.
4. `Dialog`
States and semantics: open/closed animation states, close control affordance, focus ring on close button.
Patterns: `data-[state=open|closed]` on overlay/content, close button with `sr-only` label and ring styles.
5. `DropdownMenu`
States and semantics: item focus, disabled items, sub-menu open state, side-based motion.
Patterns: `focus:*`, `data-[disabled]:*`, `data-[state=open]:*`, `data-[side=*]:*`.

Adopt state attributes consistently across your own primitives (`data-state`, `aria-*`, `disabled`) so style logic remains predictable.

## Intent and Anti-Default Checklist

Before writing code:

1. Define who the human is.
2. Define what task they must accomplish fastest.
3. Define how the interface should feel in practical terms.
4. Define one signature element that is specific to this problem.
5. Define three default patterns to reject and what replaces them.
6. Define one aesthetic risk and why it improves the task, brand, or comprehension.

If the concept still works unchanged after swapping to generic fonts, spacing, and card templates, refine further.

## Per-Component Checkpoint

Before each major component, check:

```text
Intent:
Palette and why it fits:
Depth strategy:
Surface hierarchy:
Typography and why it fits:
Spacing unit and scale:
```

Revise before implementation if any line lacks clear rationale. Include this checkpoint in the user-facing output only when it explains an important design decision.


## Visual Rules

### Surface and Depth

1. Build subtle elevation steps and avoid dramatic depth jumps.
2. Keep borders low-noise so structure is clear without visual harshness.
3. Pick one depth strategy per screen and stay consistent.
4. Place popovers and dropdowns one elevation above parent surfaces.
5. Style text-entry controls as inset surfaces when that improves affordance.
6. Use cards only when the surface boundary communicates hierarchy, grouping, or actionability.
7. Tint shadows to the background hue; avoid generic black shadows on light surfaces.
8. Keep one page-level theme direction. Do not alternate unrelated light and dark sections unless the theme switch is the concept.

### Spacing, Radius, and Typography

1. Keep spacing, radius, and type-size on three-tier defaults (`sm`/`md`/`lg`). Expand to five or seven tiers only when a documented requirement justifies it.
2. Keep padding patterns consistent by component type.
3. Build hierarchy with weight and letter spacing before adding extra size variants.
4. Use monospace with `tabular-nums` for dense numeric data.
5. Keep body copy near a 65-character measure where prose readability matters.
6. Use `text-wrap: balance` or `text-wrap: pretty` where supported for headings and short display copy.
7. Do not use Inter, system UI, or generic serif fonts as a reflex. Use the project font stack when established; otherwise choose typefaces that fit the product's audience and constraints.
8. Use serif display type only when the brief, brand, or content genuinely supports editorial, heritage, luxury, or publication cues.

### Color and Theme

1. Derive palette from domain or brand context, not trend defaults.
2. Pick colors from Tailwind scale families instead of arbitrary values.
3. Use neutral structure colors and reserve saturation for meaning.
4. Prefer one dominant accent over disconnected accents.
5. In dark surfaces, rely on border definition more than heavy shadows.
6. Keep one grey temperature per surface; do not mix warm and cool neutrals accidentally.
7. Avoid automatic purple/blue glow aesthetics and automatic beige/brass premium palettes unless the brief explicitly earns them.
8. Lock accent semantics across the page so CTA, status, and highlight colours do not drift section by section.

### Layout and Composition

1. Design component internals by content type instead of repeating one template.
2. Keep surface treatment coherent across related components.
3. Preserve navigation and location context for app-like interfaces.
4. Vary density, asymmetry, and emphasis intentionally.
5. Use `min-height: 100dvh` or equivalent for full-viewport sections; avoid `h-screen`/`100vh` hero bugs on mobile browsers.
6. Prefer CSS Grid for multi-column layout. Avoid fragile flexbox percentage math and `calc()` width hacks.
7. Constrain wide layouts with a max-width appropriate to the surface, usually around `1200px-1440px`.
8. Make mobile collapse explicit for every multi-column or asymmetric layout.
9. Avoid repeating the same section layout family more than once on long marketing pages.
10. Match bento/grid cell count to real content. Do not create blank filler cells.

### Control Semantics

1. Use native controls by default for semantics and accessibility.
2. Use custom controls only when native rendering blocks required behavior or styling.
3. Preserve semantics, keyboard behavior, and focus management in custom controls.
4. For focus, keyboard, labeling, and state semantics, follow the compact accessibility baseline in this file. Load `references/design/ux.md` only when deeper UX/accessibility guidance is required.
5. Label inputs above the control. Never use placeholder text as the only label.
6. Primary CTA text must remain one line on desktop. Shorten the label or widen the button when it wraps.
7. Use one label for one action intent across the same surface; avoid duplicate CTA intent with different wording.
8. Verify button text contrast for default, hover, active, disabled, and image-overlay states.

## Microinteraction Details

Apply these by default for reusable interactive components, even when `motion` mode is not loaded:

1. Pressable elements should have subtle press feedback, usually `scale(0.97)` with a `100-160ms` transform transition.
2. Do not animate entry from `scale(0)`. Start from roughly `scale(0.95)` with opacity when scale is needed.
3. Popovers, menus, and anchored overlays should transform from their trigger origin. Modals stay centered.
4. Tooltips should have an initial delay, then adjacent tooltips may appear instantly while one tooltip is already open.
5. Use explicit transitioned properties, not `transition: all`.
6. Use transitions for rapidly toggled UI so state changes can retarget smoothly.
7. For destructive hold-to-confirm actions, make the hold progress deliberate and the release/cancel feedback fast.
8. Use subtle blur only to smooth state crossfades when other timing adjustments fail; keep blur small and avoid it on large scrolling surfaces.

## Landing and Marketing Guardrails

Apply this section to landing pages, portfolios, and marketing surfaces. For dense product apps, prefer task efficiency over campaign drama.

1. The hero must fit the initial viewport: concise headline, subtext under roughly 20 words, one primary CTA and at most one secondary CTA.
2. Avoid stuffing trust logos, feature bullets, pricing teasers, or social proof into the hero. Move them to dedicated sections below.
3. Keep desktop navigation on one line with a practical height, usually `64px-80px`.
4. Avoid generic three-equal-card feature rows. Use asymmetric grids, grouped lists, media-led sections, or focused single-feature sections.
5. Use real, generated, or project-provided visuals for public-facing websites. Do not ship fake screenshot rectangles or div-based mock product art as the primary visual.
6. When no visual asset is available, create explicit image slots and list the needed placements instead of pretending decorative CSS is a real asset.
7. Use logo walls only for actual logos. Do not add category labels under logos.
8. Remove decorative scroll cues, atmospheric city/time/weather strips, and fake status dots unless they convey real state or navigation.
9. Do not invent precise metrics, dimensions, or performance numbers unless they come from the brief, product data, or are clearly marked as sample data.
10. Re-read visible copy before shipping. Replace unclear wordplay, forced metaphors, AI-sounding phrases, and mixed registers with plain useful text.

## Interaction and Data State Coverage

Cover every relevant state:

1. Default
2. Hover
3. Active
4. Focus-visible
5. Disabled
6. Loading
7. Empty
8. Error
9. Saving / syncing (in-place async feedback)
10. Optimistic update with rollback on failure
11. Partial data (some fields loaded, some pending)

Apply the compact accessibility baseline below. Load `references/design/ux.md` only for deeper UX/accessibility work.

## Compact Accessibility Baseline

Use this baseline for routine UI implementation without loading the full UX reference:

1. Focus: every interactive control has visible `focus-visible` styling with non-color-only indication where possible.
2. Keyboard: controls are reachable in logical order and support expected keys (`Enter`, `Space`, `Escape`, arrows where applicable).
3. Naming: controls have visible labels or accessible names via `aria-label` / `aria-labelledby`.
4. State semantics: expose disabled, invalid, required, expanded/collapsed, selected, loading, and busy states correctly.
5. Feedback: validation, async status, empty states, and errors use clear text and semantic roles where useful.
6. Contrast: text, icons, focus rings, and semantic states stay readable in default, hover, active, disabled, and error states.
7. Motion safety: respect `prefers-reduced-motion` and provide non-motion feedback for critical state changes.

## Expression vs Clarity Scaling

1. Prioritize clarity and low-noise hierarchy when task efficiency is dominant.
2. Increase expressive typography and atmosphere only when it supports comprehension or brand intent.
3. Scale motion and ornament to context so utility tasks remain fast.
4. Allow decoration only when it supports hierarchy, emphasis, meaning, or story.

## Anti-Patterns

Avoid these unless explicitly justified:

1. Harsh borders or noisy dividers.
2. Inconsistent spacing scales.
3. Mixed depth strategies without intent.
4. Decorative gradients with no informational or brand role.
5. Missing focus states or reduced-motion support.
6. Floating content with no navigation or context.
7. Incoherent placeholder content that breaks story continuity.
8. Centered hero, three-card feature row, eyebrow label on every section, and repeated split-image sections as automatic defaults.
9. Placeholder-as-label forms, generic circular spinners, static-only success states, and unhandled empty/error/loading states.
10. Pure text marketing pages where the subject needs product, people, place, or brand imagery.

## Quality Checks

Run these checks before final output:

1. `Swap test`: replacing major choices with defaults clearly weakens the concept.
2. `Squint test`: hierarchy remains clear with no dominant noise.
3. `Signature test`: signature element appears in at least five concrete choices.
4. `Token test`: visual values map cleanly to the token system.
5. `Content coherence`: copy, data, and visuals read as one believable product story.
6. `State completeness`: interaction and data states are fully covered.
7. `Accessibility`: satisfy the compact accessibility baseline; load `references/design/ux.md` only when the task requires deeper audit or flow/accessibility guidance.
8. `Responsiveness`: layout and type remain intentional on mobile and desktop.
9. `Performance`: interactive effects rely on efficient rendering paths.
10. `Hero and CTA`: marketing heroes fit the first viewport, CTA labels do not wrap on desktop, and CTA intent is consistent.
11. `Asset honesty`: visuals are real/generated/project-provided or clearly marked as needed placeholders.
12. `Copy audit`: visible strings are grammatical, specific, non-generic, and free of invented precision.
