# Craft System

Build a system first, then style it.

## Intent and Anti-Default Checklist

Before writing code:

1. define who the human is
2. define what they must accomplish
3. define how the interface should feel
4. define one signature element
5. define three default patterns to reject

If the concept still works after swapping to generic fonts, generic spacing, and a generic card grid, the design is still defaulted.

## Per-Component Checkpoint

Before each major component, make explicit choices:

1. intent
2. palette and why it fits the domain
3. depth strategy
4. surface hierarchy
5. typography and why it fits
6. spacing unit and scale

## Token Architecture

Map all visual values to primitives:

1. foreground: `primary`, `secondary`, `tertiary`, `muted`
2. background: `base`, `surface-1`, `surface-2`, `overlay`
3. border: `subtle`, `default`, `strong`, `focus`
4. brand: accent and action
5. semantic: success, warning, danger, info
6. control: input/select/button surface and border tokens

Avoid random hex values and one-off spacing numbers.

## Surface, Border, and Depth Rules

1. build subtle elevation steps; avoid dramatic jumps
2. keep borders low-noise so they define structure without dominating
3. pick one depth strategy per screen:
- borders-only for dense utility tools
- subtle shadows for approachable products
- layered shadows for premium card-heavy surfaces
- surface tint shifts for flat depth without shadows
4. keep sidebars and main content in one visual world unless separation is intentional
5. place dropdowns and popovers one elevation above parent surfaces
6. style text-entry controls as inset surfaces (often slightly darker than their surrounding surface)

## Spacing, Padding, and Radius

1. choose a base spacing unit and stay on-grid
2. keep padding consistent and intentional
3. keep corner radius systematic (small for controls, medium for cards, large for overlays)
4. avoid mixing sharp and soft corners without reason

## Typography Rules

1. choose type pairings that match tone and task
2. avoid defaulting to overused generic stacks unless constraints require it
3. build hierarchy with size, weight, and letter spacing together
4. use monospace with `tabular-nums` for dense numeric data
5. keep line lengths readable on desktop and mobile

## Layout and Composition Rules

1. design card internals by content type, not by one repeated template
2. keep surface treatment consistent across card types
3. provide navigation and location context for app-like interfaces
4. vary composition intentionally (density, asymmetry, emphasis, negative space)
5. avoid repeated “same sidebar + same cards + same metric tile” patterns

## Controls and Semantics

1. default to native controls for baseline accessibility
2. use custom controls when native rendering blocks required styling or behavior
3. when using custom controls, preserve semantics, keyboard behavior, and focus management
4. note: native `<select>` and `<input type="date">` are often hard to style consistently across platforms

## Color and Theme Rules

1. derive palette from product/brand domain, not trend defaults
2. use neutral structure colors and reserve saturated color for meaning
3. prefer one dominant accent over many disconnected accents
4. avoid trend-default palettes such as generic purple-on-white gradients unless explicitly requested
5. in dark mode, rely more on border definition than heavy shadows
6. tune semantic colors for dark backgrounds while preserving hierarchy

## State Coverage

Every relevant interaction should include:

1. default
2. hover
3. active
4. focus-visible
5. disabled
6. loading
7. empty
8. error

## Anti-Patterns

Avoid these unless explicitly justified:

1. harsh borders or noisy dividers
2. inconsistent spacing scales
3. mixing depth strategies without intent
4. decorative gradients with no informational or brand purpose
5. missing focus states or reduced-motion behavior
6. floating content with no app/navigation context
7. text/data content that does not tell one coherent story
