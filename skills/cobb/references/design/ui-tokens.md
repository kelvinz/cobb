# UI Token Systems

Load this reference only when creating or materially changing a Tailwind/token system.

## Styling Topology

Use three layers:

1. Component: local utilities or styles inside the smallest reusable component.
2. System: global tokens, base element defaults, and theme scopes.
3. Exception: narrowly targeted third-party, complex-selector, or browser-specific overrides.

For Tailwind projects, prefer existing utilities and theme configuration. Use `@layer base` for tokens/baselines and `@layer components` with `@apply` only when a reusable component cannot express the pattern more clearly.

## Token Coverage

Define only families the product uses, but check each category:

- structure and semantic colour: background, foreground, border, brand, success, warning, destructive, info
- interaction states: default, hover, active, focus-visible, disabled, invalid
- typography: family, size, line height, weight, tracking
- spacing and sizing: layout gaps, padding, controls, icons, content widths
- shape and edge: radius, border, focus ring, ring offset
- depth and opacity: surface emphasis, shadows, muted/secondary/primary opacity
- motion: durations and easing aligned with `references/design/motion.md`

## Tier Rules

Use one tier count per family:

1. Three tiers by default: `sm`, `md`, `lg`.
2. Five tiers only when real product variation needs `xs` through `xl`.
3. Seven tiers only for proven dense-system needs, `2xs` through `2xl`.
4. Never exceed seven; document why five or seven is necessary.

Practical three-tier Tailwind defaults:

- spacing: `2`, `4`, `8`
- radius: `rounded-sm`, `rounded-md`, `rounded-lg`
- type: `text-sm`, `text-base`, `text-lg`
- control height: `h-8`, `h-10`, `h-12`
- icon size: `size-4`, `size-5`, `size-6`
- opacity: `opacity-60`, `opacity-80`, `opacity-100`
- colour intensity: `400`, `500`, `600` within one family

## Discipline

- Anchor canonical values to the existing framework scale and repository tokens.
- Avoid one-off spacing, radius, opacity, and colour values in reusable primitives.
- Give semantic tokens stable roles instead of encoding component names.
- Ensure every interactive state remains distinguishable and accessible.
- Keep motion tiers consistent with the motion reference.

Load `references/design/ui-examples.md` only when concrete 3/5/7-tier config or component examples are needed.
