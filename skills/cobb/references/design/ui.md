# UI Mode

Design or refine interactive interfaces and component systems.

## Delivery and References

Follow the delivery kind and preflight rule in `references/design.md`:

- **Direction:** provide the layout, component/state specification, token choices, and implementation handoff.
- **Implementation:** deliver working code for the requested surface after preflight.
- **Audit:** report findings, evidence, and proposed changes without applying them.

For each kind, cover relevant states, responsive behaviour, accessibility, and a brief hierarchy rationale tied to the user's task.

Load `references/design/ux.md` for a selected secondary mode or deeper flow/accessibility/audit needs. Load `references/design/motion.md` for a selected secondary mode or requested transition detail. Load the conditional UI references only under the rules in `references/design.md`; routine UI work uses the compact baseline below.

## Repository Fit

1. Identify the framework, styling system, component library, and existing theme/token files.
2. Follow those systems. Use Tailwind only when already present, or when no styling system exists and it is the smallest fit. Changing an established system needs explicit scope.
3. Reuse or compose existing library components, following their APIs and naming. Build a custom component only when no suitable primitive exists.
4. Keep component styles local. Reserve global files for tokens, base defaults, themes, and necessary third-party/browser overrides.
5. Extract reusable primitives when repetition or a stable shared contract justifies them.
6. Check installed dependencies and versions before importing packages or using their APIs. Include an install command only for a missing, needed dependency.

## Design Plan

Before defining a new design or changing an existing one:

1. State the subject, audience, primary task, design language, and implementation approach in one line.
2. Identify domain objects, vocabulary, data shapes, constraints, and visual cues that can guide the design.
3. Choose a signature element specific to the brief. Explain the visual risk it takes and how it helps the task, brand, or comprehension; keep supporting UI disciplined.
4. Define palette roles, type roles, layout, and component density. Map values to existing tokens or the established scale.
5. Apply the variance, motion, and density settings from `references/design.md`. Prioritise clarity for utility tasks; add expression only when it supports comprehension, meaning, or brand intent.
6. Name three generic defaults to replace and what replaces them. Use numbered markers only for genuinely sequential content.
7. Use active labels, consistent action words, and specific empty/error guidance.
8. Run the swap test: if generic fonts, stock cards, and trend colours could replace the plan's major choices without weakening it, revise the weakest part.

Before each major component, check that its intent, palette, depth, surface hierarchy, typography, and spacing have clear reasons. Show that checkpoint to the user only when it explains an important decision.

## Visual Rules

### Surface and Depth

1. Use subtle elevation steps, low-noise borders, and one consistent depth strategy per screen.
2. Place popovers and dropdowns one elevation above parent surfaces.
3. Use inset text-entry surfaces when that improves clarity. Use cards when their boundaries communicate grouping, hierarchy, or action.
4. Tint shadows to the background hue rather than using generic black shadows on light surfaces.
5. Keep one page-level theme; alternate light and dark sections only when that switch is part of the concept.
6. When translucency fits, use floating `backdrop-filter` layers with content beneath them. Let material weight show hierarchy, and keep adjacent light translucent surfaces distinct.
7. Over translucent surfaces, use sufficient contrast, slightly heavier text, and a small tracking increase; keep saturated colours on solid layers.
8. Prefer a faded blur/gradient scroll edge over a hard divider where content meets floating chrome.
9. When glass/blur surfaces enter or exit, animate blur and scale together rather than using only opacity.

### Spacing, Radius, and Typography

1. Start spacing, radius, and type-size families with three tiers (`sm`/`md`/`lg`). Expand to five or seven only for a documented need.
2. Keep padding consistent by component type. Build hierarchy with weight and letter spacing before adding size variants.
3. Use monospace with `tabular-nums` for dense numeric data.
4. Keep readable prose near a 65-character measure. Use `text-wrap: balance` or `pretty` for headings and short display copy where supported.
5. Keep the established font stack; otherwise choose for the audience and constraints rather than reflexively using Inter, system UI, or generic serif fonts.
6. Use serif display type when the brief supports editorial, heritage, luxury, or publication cues.
7. Track by size: slightly negative for large display text, near zero for body text, slightly positive for very small text.
8. Use tighter line height for large headings (around `1.05–1.2`) and looser line height for body copy; tighten further only for dense operational UI.
9. Use `rem`/`em` for spacing near text so larger text settings preserve the layout.

### Colour and Theme

1. Derive the palette from domain or brand context. Use the repository's colour tokens; use Tailwind families only in Tailwind work.
2. Keep structural colours neutral and reserve saturation for meaning. Prefer one dominant accent.
3. Define dark surfaces with borders more than heavy shadows.
4. Keep one grey temperature per surface. Use purple/blue glows or beige/brass palettes only when the brief supports them.
5. Keep action, status, and highlight colour meanings consistent across the surface.
6. Give gradients and other decoration an informational, compositional, or brand purpose.

### Layout and Controls

1. Design component internals for their content. Keep related surfaces coherent and preserve navigation/location context.
2. Vary density, asymmetry, and emphasis intentionally.
3. Use `min-height: 100dvh` or equivalent for full-viewport sections; avoid mobile `100vh` sizing errors.
4. Prefer CSS Grid for multi-column layouts. Keep widths bounded for the surface, usually around `1200px–1440px`, and make mobile collapse explicit.
5. Match grid cell count to real content rather than adding blank filler cells.
6. Use native controls by default. Custom controls must preserve semantics, keyboard behaviour, and focus management.
7. Place input labels above the controls; placeholders are not labels.
8. Use the same label for the same action. Keep button text readable in default, hover, active, disabled, and image-overlay states.

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

Cover every relevant state:

- default, hover, active, focus-visible, and disabled
- loading, empty, error, and in-place saving/syncing feedback
- optimistic updates with rollback on failure
- partial data, including loaded and pending fields

Use task-specific progress and success feedback rather than generic circular spinners or static-only success states. Keep sample data, copy, and visuals consistent with the same product story.

## Compact Accessibility Baseline

Keep these checks available for routine UI work:

1. Focus: visible `focus-visible` styles, using more than colour alone where possible.
2. Keyboard: logical tab order and expected `Enter`, `Space`, `Escape`, and arrow-key behaviour.
3. Naming: visible labels or accessible names through `aria-label` / `aria-labelledby`.
4. State semantics: expose disabled, invalid, required, expanded/collapsed, selected, loading, and busy states correctly.
5. Feedback: clear validation, async status, empty-state, and error text; use semantic roles where useful.
6. Contrast: readable text, icons, focus rings, and states, including hover, disabled, and error states.
7. Motion safety: respect `prefers-reduced-motion` and provide non-motion feedback for critical changes.
8. Preferences: honour `prefers-reduced-transparency` and `prefers-contrast: more` when using translucent or low-contrast surfaces; increase opacity, remove blur, and define borders as needed.

## Quality Checks

For direction, check the specification. For implementation or an audit of working UI, inspect the actual surface and report any runtime checks that could not be completed.

1. **Distinctiveness:** the swap test weakens the design; the signature element appears in at least five concrete choices.
2. **Hierarchy:** the squint test shows clear emphasis without dominant noise.
3. **Tokens:** visual values map to the chosen token system.
4. **States:** all relevant interaction and data states are accounted for.
5. **Accessibility:** the compact baseline is satisfied.
6. **Responsiveness:** layout and type remain intentional on mobile and desktop.
7. **Performance:** effects use efficient rendering paths.
8. **Content:** copy is grammatical, specific, and coherent; facts are supported, sample data is labelled, and assets are real/supplied/generated or clearly marked as missing.
