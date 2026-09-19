# UI Mode

Design or refine interactive interfaces and component systems. UI follows UX under Function Before Form in `references/design.md`: the visual layer is set only after the flow, states, and copy it serves are settled.

## Delivery and References

Follow the delivery kind and preflight rule in `references/design.md`:

- **Direction:** provide the layout, component/state specification, token choices, and implementation handoff.
- **Implementation:** deliver working code for the requested surface after preflight.
- **Audit:** report findings, evidence, and proposed changes without applying them.

For each kind, cover relevant states, responsive behaviour, accessibility, and a brief hierarchy rationale tied to the user's task.

Load `references/design/ux.md` first when the UX layer is not settled, and for copy rules, deeper accessibility, or audits. Load `references/design/motion.md` for a selected secondary mode or requested transition detail. Load the conditional references only under the rules in `references/design.md`; routine UI work uses the compact baseline below.

## Repository Fit

1. Identify the framework, styling system, component library, existing theme/token files, and the root `DESIGN.md`.
2. Follow those systems. `DESIGN.md` and the token files are the visual authority; a PRD's visual direction overrides them for that feature only. Use Tailwind only when already present, or when no styling system exists and it is the smallest fit. Changing an established system needs explicit scope.
3. Reuse or compose existing library components, following their APIs and naming. Build a custom component only when no suitable primitive exists. A hand-built toast, dialog, dropdown, command menu, or long list without virtualisation is a defect when an accessible primitive is installed or belongs; check the dependency manifest first.
4. Keep component styles local. Reserve global files for tokens, base defaults, themes, and necessary third-party/browser overrides.
5. Extract reusable primitives when repetition or a stable shared contract justifies them.
6. Check installed dependencies and versions before importing packages or using their APIs. Include an install command only for a missing, needed dependency.

## Design Plan

Before defining a new design or changing an existing one:

1. Confirm the UX layer is settled: the task flow, state inventory, and copy exist in the PRD or an approved artifact. If not, resolve them first through `references/design/ux.md`.
2. State the subject, audience, visitor mode, primary task, design language, and implementation approach in one line.
3. Identify domain objects, vocabulary, data shapes, constraints, and visual cues that can guide the design.
4. Scale the work to the change kind under Scale to the Change in `references/design.md`. Extend and refine inherit the look: skip steps 5 to 9, and check instead that the addition matches its neighbours in tokens, spacing, and component patterns. A new surface explores structure only, and a new identity or redesign runs the Direction Round below.
5. Choose a signature element specific to the brief. Explain the visual risk it takes and how it helps the task, brand, or comprehension; keep supporting UI disciplined.
6. Pick the colour strategy, then define palette roles, type roles, layout, and component density. Map values to existing tokens or the established scale.
7. Apply the variance, motion, and density settings from `references/design.md`. Prioritise clarity for utility tasks; add expression only when it supports comprehension, meaning, or brand intent.
8. Name three generic defaults to replace, using Calibration below, and what replaces them. Use numbered markers only for genuinely sequential content.
9. Run the swap test: if generic fonts, stock cards, and trend colours could replace the plan's major choices without weakening it, revise the weakest part.

Before each major component, check that its intent, palette, depth, surface hierarchy, typography, and spacing have clear reasons. Show that checkpoint to the user only when it explains an important decision.

## Calibration

AI-generated interfaces cluster around a few looks whatever the subject. The brief's own words, the repository's established system, and `DESIGN.md` always win; this list binds only the axes they leave free. On Operate and Read surfaces, familiar conventions are a feature: the list targets these looks, not standard patterns.

Default looks:

1. A warm cream ground, a high-contrast serif display, and a terracotta or clay accent.
2. A near-black ground with one neon or acid accent and glowing edges.
3. A broadsheet: hairline rules, zero radius, dense columns, an italic display serif, and small tracked monospace labels.
4. The card kit: identical rounded cards, one radius everywhere, the same soft grey shadow, gradient washes, and an icon tile above every heading.
5. Purple-to-blue gradients and glass over a dark mesh.

Template chrome:

- an uppercase tracked label above every heading
- metadata joined with middle dots, and labels built as "WORD — fragment"
- section numbers on content that is not a sequence
- arrows appended to link and button text
- monospace as a costume for "technical" rather than for code or data
- gradient text, coloured side-stripe borders on cards, and nested cards
- the hero-metric template: a big number, a small label, supporting stats, and a gradient accent
- emoji or Unicode glyphs standing in for an icon set, and decorative status dots
- scroll cues and decorative locale, time, or version strips

Reflex fonts: Fraunces, Playfair Display, Cormorant, Lora, Crimson, Newsreader, Syne, Space Grotesk, Space Mono, IBM Plex, Inter as a display face, DM Sans, DM Serif, Outfit, Plus Jakarta Sans, Instrument Sans, and Instrument Serif. Choosing one needs a reason no other face satisfies. A subject association, such as books wanting a serif or tech wanting a monospace, is never that reason.

## Direction Round

Run only for a new identity or a redesign, after the UX layer is settled.

1. Name the product's distinct mechanism in one sentence, the audience's real scene of use, and what the first surface must prove.
2. Name the rut: the look this category always ships, and its predictable opposite. Both stay off the candidate list.
3. Derive candidates from the audience's own world: the artifacts, publications, places, and interfaces they know well. When most candidates share one material family, keep looking until at least three families appear.
4. Develop three complete directions on named axes. Each states its thesis, colour strategy and palette, type character, first-screen composition, signature element, when it wins, and what it costs.
5. Present them as a numbered choice under the shared Choices rule. Add the category standard, played straight, as a further option for a user who wants the familiar path. Recommend from the brief and evidence, not from taste.
6. Record the chosen direction in the PRD's visual direction block. `DESIGN.md` is written after the build.

## Variant Picker

Use when the open decision is how a piece of UI should look or feel, after its structure is settled.

1. Build in isolation: a separate route in the dev server, or one self-contained HTML file when no project runs. Production code never imports from it.
2. Default to three variants, at most five. Give each a name that describes its direction, such as "Quiet", "Dense", or "Editorial", never "Option A", and a named axis: layout, density, personality, motion, or interaction model. Two variants that differ only in colour or copy are one variant.
3. Every variant fully works with realistic content, uses the project's tokens, and meets the Quality Checks below.
4. Show one variant at a time, full size, in realistic surrounding context. Switching is instant, with keyboard shortcuts. Keep the picker plain and identical across variants; it is not part of the design.
5. Flip through every variant before presenting it, and confirm that each renders with a clean console.
6. Present each variant's axis, when it is the right choice, and its cost, as a numbered choice. The user picks.
7. Integrate the chosen variant under project conventions, then delete the picker unless the user asks to keep it.

## Visual Rules

### Surface and Depth

1. Use subtle elevation steps, low-noise borders, and one consistent depth strategy per screen.
2. Place popovers and dropdowns one elevation above parent surfaces.
3. Use inset text-entry surfaces when that improves clarity. Use cards when their boundaries communicate grouping, hierarchy, or action.
4. Tint shadows to the background hue rather than using generic black shadows on light surfaces, and give them an offset and a soft blur. A zero-offset coloured glow is decoration, not depth.
5. Keep one page-level theme; alternate light and dark sections only when that switch is part of the concept.
6. When translucency fits, use floating `backdrop-filter` layers with content beneath them. Let material weight show hierarchy, and keep adjacent light translucent surfaces distinct.
7. Over translucent surfaces, use sufficient contrast, slightly heavier text, and a small tracking increase; keep saturated colours on solid layers.
8. Prefer a faded blur/gradient scroll edge over a hard divider where content meets floating chrome.
9. When glass/blur surfaces enter or exit, animate blur and scale together rather than using only opacity.

### Spacing, Radius, and Typography

1. Start spacing, radius, and type-size families with three tiers (`sm`/`md`/`lg`). Expand to five or seven only for a documented need.
2. Keep padding consistent by component type. Group related items tightly, separate groups generously, and put more space above a heading than below it. Build hierarchy with weight and letter spacing before adding size variants.
3. Use monospace with `tabular-nums` for dense numeric data.
4. Keep readable prose near a 65-character measure. Use `text-wrap: balance` or `pretty` for headings and short display copy where supported.
5. Keep the established font stack. Otherwise choose faces from the subject's own world, for the audience and constraints, and check the choice against the reflex fonts in Calibration.
6. Track by size: slightly negative for large display text, near zero for body text, slightly positive for very small text.
7. Use tighter line height for large headings (around `1.05–1.2`) and looser line height for body copy; tighten further only for dense operational UI.
8. Use `rem`/`em` for spacing near text so larger text settings preserve the layout.

### Colour and Theme

1. Derive the palette from domain or brand context. Use the repository's colour tokens; use Tailwind families only in Tailwind work.
2. Pick a colour strategy before picking colours:
   - Restrained: neutrals plus one accent. The default for Operate and Read surfaces.
   - Committed: one saturated colour carries 30 to 60 percent of the surface.
   - Full palette: three or four named colour roles.
   - Drenched: the surface is the colour.
   Persuade and Experience surfaces may take a bolder strategy when the brief allows.
3. Choose light or dark from one sentence about the physical scene: who uses the surface, where, and under what light. Never choose it by category habit.
4. Under Restrained, keep structural colours neutral and reserve saturation for meaning.
5. Define dark surfaces with borders more than heavy shadows.
6. Keep one grey temperature per surface. Use purple/blue glows or beige/brass palettes only when the brief supports them.
7. Keep action, status, and highlight colour meanings consistent across the surface.
8. Give gradients and other decoration an informational, compositional, or brand purpose.

### Layout and Controls

1. Design component internals for their content. Keep related surfaces coherent and preserve navigation/location context.
2. Vary density, asymmetry, and emphasis intentionally.
3. Size app shells and bottom-pinned UI with `100dvh`, and full-height marketing heroes with `min-height: 100svh`, so a hero does not resize when the mobile toolbar hides. Avoid `100vh` for either on mobile.
4. Prefer CSS Grid for multi-column layouts. Keep widths bounded for the surface, usually around `1200px–1440px`, and make mobile collapse explicit.
5. Match grid cell count to real content rather than adding blank filler cells.
6. Use native controls by default. Custom controls must preserve semantics, keyboard behaviour, and focus management.
7. Place input labels above the controls; placeholders are not labels.
8. Use the same label for the same action. Keep button text readable in default, hover, active, disabled, and image-overlay states.

## Mobile Web Baseline

Apply to any web surface people use on phones:

1. Set `viewport-fit=cover` in the viewport meta tag, and pad fixed and bottom-pinned UI with `env(safe-area-inset-*)`.
2. Keep input, select, and textarea text at 16px or larger so iOS Safari does not zoom into the field. Never disable zoom with `user-scalable=no` or `maximum-scale=1`.
3. Give controls `touch-action: manipulation` and pressed feedback on pointer-down. Remove the default tap highlight only when a pressed state replaces it.
4. Gate hover styles behind `@media (hover: hover) and (pointer: fine)` so taps do not leave hover stuck. Detect touch with media queries, never user-agent sniffing.
5. Set `theme-color` for each colour scheme.
6. Use `overscroll-behavior` on app shells where pull-to-refresh or scroll chaining is unwanted, and `touch-action: pan-y` on horizontal carousels.
7. Apply `user-select: none` to controls only, never to the whole page.
8. Verify touch behaviour on real hardware. Emulation proves layout, not gestures.

## Microinteractions

Use these for reusable interactive components even without the full motion reference:

1. Give pressable elements subtle feedback, usually `scale(0.97)` with a `100–160ms` transform transition.
2. When entry needs scale, start around `scale(0.95)` with opacity rather than `scale(0)`.
3. Transform anchored overlays from their trigger origin; keep modals centred.
4. Give the first tooltip a delay; adjacent tooltips may appear immediately while one is open.
5. Name transitioned properties explicitly. Use transitions for rapid state changes so they can retarget smoothly.
6. Make destructive hold-to-confirm progress deliberate and release/cancel feedback fast.
7. Use small blur for difficult crossfades only after timing adjustments fail; avoid it on large scrolling surfaces.

## Interaction and Data States

Build every state in the PRD's state inventory: default, empty, loading, partial, error, success, offline, disabled, overflow, and permission. Each state shows what the user sees, what they can do, and how they recover. At component level, cover default, hover, active, focus-visible, disabled with its reason, loading, and error, and roll optimistic updates back on failure.

Use task-specific progress and success feedback rather than generic circular spinners or static-only success states. Keep sample data, copy, and visuals consistent with the same product story.

## Compact Accessibility Baseline

Target WCAG 2.2 AA unless the PRD names another level. Keep these checks available for routine UI work:

1. Focus: visible `focus-visible` styles, using more than colour alone where possible. Sticky headers, toasts, and overlays never hide the focused element.
2. Keyboard: logical tab order and expected `Enter`, `Space`, `Escape`, and arrow-key behaviour.
3. Naming: visible labels or accessible names through `aria-label` / `aria-labelledby`.
4. State semantics: expose disabled, invalid, required, expanded/collapsed, selected, loading, and busy states correctly.
5. Feedback: clear validation, async status, empty-state, and error text; use semantic roles where useful.
6. Contrast: at least 4.5:1 for body and placeholder text, and 3:1 for large text and non-text UI such as icons, control borders, and focus rings, including hover and error states. On coloured surfaces, tint secondary text from the surface hue instead of using grey.
7. Target size: at least 24×24 CSS px, and 44×44 for primary touch targets with 8px between targets.
8. Motion safety: respect `prefers-reduced-motion` and provide non-motion feedback for critical changes.
9. Preferences: honour `prefers-reduced-transparency` and `prefers-contrast: more` when using translucent or low-contrast surfaces; increase opacity, remove blur, and define borders as needed.

The fuller set, including drag alternatives, redundant entry, authentication, and time limits, is in `references/design/ux.md`.

## Quality Checks

For direction, check the specification. For implementation or an audit of working UI, check captures made under `references/design/visual-verification.md`. During extend or refine, a check that fails across the whole app, outside the change, becomes a follow-up suggestion instead of an in-scope fix. Check function first, then form:

1. **Coverage:** every brief and PRD requirement is present and findable within seconds.
2. **States:** every state in the inventory renders, with its recovery path.
3. **Accessibility:** the compact baseline is satisfied.
4. **Content:** copy passes the copy self-audit in `references/design/ux.md`; facts are supported, sample data is labelled, and assets are real, supplied, generated, or clearly marked as missing.
5. **Responsiveness:** layout and type remain intentional on mobile and desktop, and the mobile web baseline holds.
6. **Hierarchy:** the squint test shows clear emphasis without dominant noise.
7. **Tokens:** visual values map to the chosen token system and `DESIGN.md`.
8. **Browser surfaces:** text selection, the caret, custom scrollbars, focus rings, link underline offset, and tabular numerals are styled from the palette, not left at browser defaults.
9. **Distinctiveness** (new surface, new identity, or redesign only): the swap test weakens the design, the signature element appears in at least five concrete choices, and no Calibration default was taken on a free axis.
10. **Motion:** one authored moment rather than the same entrance on every section.
11. **Performance:** effects use efficient rendering paths.
