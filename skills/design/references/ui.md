# UI Mode

Use this mode to design or refine interactive interfaces and component systems.

## Table of Contents

1. Output Contract
2. Project Component Library
3. Tailwind-First Implementation
4. Styling Topology
5. Global Token System
6. Example Library
7. Shadcn State Pattern Extraction
8. Intent and Anti-Default Checklist
9. Per-Component Checkpoint
10. Visual Rules
11. Interaction and Data State Coverage
12. Expression vs Clarity Scaling
13. Anti-Patterns
14. Quality Checks

## Output Contract

Deliver all of the following for UI work:

1. Ship working code for the requested surface or component.
2. Map color, spacing, and type decisions to an explicit token system.
3. Cover relevant interaction and data states.
4. Include a brief hierarchy rationale tied to task goals.
5. Preserve responsive behavior on mobile and desktop when applicable.
6. Use Tailwind CSS for examples and implementation when project constraints allow.
7. Default component styling to inline Tailwind utilities.
8. Apply accessibility options from `references/ux.md` as required component behavior.

## Project Constraint Detection

Before writing code, detect the project's existing conventions:

1. Identify the framework (React/Next, Vue, Svelte, Astro, etc.).
2. Identify the styling system (Tailwind, CSS modules, styled-components, vanilla CSS).
3. Identify existing component primitives (shadcn/ui, Radix, MUI, Headless UI, etc.).
4. Locate existing theme/token files if present.
5. Prefer Tailwind when the project already uses it or has no established styling system.
6. When a non-Tailwind styling system is established, follow the repo pattern instead of introducing Tailwind.

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
duration and easing tiers aligned with `references/motion.md`.
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

Load `references/ui-examples.md` for concrete Tailwind config and component examples.

## Example Library

Load rules for `references/ui-examples.md` are defined in `SKILL.md` under the `ui` mode entry.

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

If the concept still works unchanged after swapping to generic fonts, spacing, and card templates, refine further.

## Per-Component Checkpoint

Before each major component, state:

```text
Intent:
Palette and why it fits:
Depth strategy:
Surface hierarchy:
Typography and why it fits:
Spacing unit and scale:
```

Revise before implementation if any line lacks clear rationale.


## Visual Rules

### Surface and Depth

1. Build subtle elevation steps and avoid dramatic depth jumps.
2. Keep borders low-noise so structure is clear without visual harshness.
3. Pick one depth strategy per screen and stay consistent.
4. Place popovers and dropdowns one elevation above parent surfaces.
5. Style text-entry controls as inset surfaces when that improves affordance.

### Spacing, Radius, and Typography

1. Keep spacing, radius, and type-size on three-tier defaults (`sm`/`md`/`lg`). Expand to five or seven tiers only when a documented requirement justifies it.
2. Keep padding patterns consistent by component type.
3. Build hierarchy with weight and letter spacing before adding extra size variants.
4. Use monospace with `tabular-nums` for dense numeric data.

### Color and Theme

1. Derive palette from domain or brand context, not trend defaults.
2. Pick colors from Tailwind scale families instead of arbitrary values.
3. Use neutral structure colors and reserve saturation for meaning.
4. Prefer one dominant accent over disconnected accents.
5. In dark surfaces, rely on border definition more than heavy shadows.

### Layout and Composition

1. Design component internals by content type instead of repeating one template.
2. Keep surface treatment coherent across related components.
3. Preserve navigation and location context for app-like interfaces.
4. Vary density, asymmetry, and emphasis intentionally.

### Control Semantics

1. Use native controls by default for semantics and accessibility.
2. Use custom controls only when native rendering blocks required behavior or styling.
3. Preserve semantics, keyboard behavior, and focus management in custom controls.
4. For focus, keyboard, labeling, and state semantics, follow `references/ux.md` -> `Accessibility Option Set for UI Components`.

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

Accessibility details for these states are defined in `references/ux.md` and must be applied to every reusable UI primitive.

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

## Quality Checks

Run these checks before final output:

1. `Swap test`: replacing major choices with defaults clearly weakens the concept.
2. `Squint test`: hierarchy remains clear with no dominant noise.
3. `Signature test`: signature element appears in at least five concrete choices.
4. `Token test`: visual values map cleanly to the token system.
5. `Content coherence`: copy, data, and visuals read as one believable product story.
6. `State completeness`: interaction and data states are fully covered.
7. `Accessibility`: satisfy the full `references/ux.md` accessibility option set, including focus visibility, keyboard reachability, naming, semantic states, contrast, and reduced-motion support.
8. `Responsiveness`: layout and type remain intentional on mobile and desktop.
9. `Performance`: interactive effects rely on efficient rendering paths.
