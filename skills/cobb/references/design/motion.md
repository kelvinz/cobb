# Motion Mode

Use motion to communicate state, orientation, focus, and continuity.

## Table of Contents

1. Mode Contract
2. Frequency Gate
3. Purpose Rules
4. Timing Scale
5. Easing Tokens
6. Spring and Gesture Rules
7. Dependency and State Rules
8. Performance Rules
9. Accessibility Rules
10. Motion Spec Template
11. High-Value Interaction Patterns
12. Scroll Animation Rules
13. Debugging Animations
14. Common Failure Modes
15. Quality Checks

## Mode Contract

When `motion` is primary:

1. Ship working code or precise implementation spec.
2. Define timing scale and easing token usage.
3. Define reduced-motion behavior for all critical interactions.
4. Document performance-sensitive implementation choices.

When `motion` is secondary:

1. Keep the host mode deliverable primary.
2. Provide motion deltas only for interactions in scope.
3. Avoid introducing decorative transitions that dilute task clarity.

## Frequency Gate

Decide whether motion belongs before choosing duration or easing:

1. `100+ times/day`: remove animation. Keyboard shortcuts, command palettes, and repeated navigation should feel instant.
2. `Tens of times/day`: remove, shorten, or reduce to tiny feedback such as colour, opacity, or press scale.
3. `Occasional`: use standard transitions for modals, drawers, toasts, menus, and state changes.
4. `Rare / first-time`: allow more character for onboarding, celebrations, and explanatory marketing motion.

Never animate keyboard-initiated actions unless the animation is essential state feedback and does not delay the action.

## Purpose Rules

Motion should answer at least one of these:

1. Confirm an action happened.
2. Show where an element came from or went.
3. Direct attention to important change.
4. Preserve context during transitions.

If none apply, remove the motion.

## Timing Scale

Use these defaults and adjust intentionally:

1. 100-160ms: button press, hover, and tiny feedback.
2. 125-200ms: tooltips and small popovers.
3. 150-250ms: dropdowns, selects, compact menus.
4. 200-500ms: modals, drawers, toasts, route shifts.
5. 500ms+: rare explanatory or deliberate interactions only.

Keep routine UI animation under 300ms. A faster transition often improves perceived performance even when actual load time is unchanged.

## Easing Tokens

Use strong, consistent easing tokens:

```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

Use `--ease-out` for entries and immediate feedback. Use `--ease-in-out` for movement already on screen. Use `--ease-drawer` for sheet/drawer movement. Avoid `ease-in` for UI actions because it delays the first visible response.

Use `--ease-spring` only for playful or direct-manipulation moments.

When working alongside Tailwind/token-system UI work, load `references/design/ui-tokens.md`. Default mapping uses `sm: 150ms`, `md: 250ms`, `lg: 400ms` and matching easing tokens.

## Spring and Gesture Rules

Use springs when fixed-duration timing is the wrong model:

1. Drag interactions with momentum.
2. Interruptible gestures that may reverse mid-flight.
3. Direct-manipulation surfaces that should feel alive.
4. Decorative pointer-following effects where lag improves feel.

Keep bounce subtle (`0.1-0.3`) and avoid bounce in serious product workflows. For drag dismissal, consider both distance and velocity so a quick flick can dismiss without a long drag. Apply damping when users drag past natural boundaries instead of creating hard stops.

For drag interactions, capture the pointer after drag start and ignore extra touch points until the gesture ends.

## Dependency and State Rules

1. Before importing a motion library, check the dependency manifest. Use the project's existing animation library when one is present.
2. Prefer CSS transitions and keyframes for simple hover, focus, loading, and disclosure motion.
3. Use Motion, GSAP, or another runtime animation library only when CSS cannot express the required choreography cleanly.
4. Isolate pointer, scroll, and animation-heavy code in client-side leaf components when the framework separates server and client components.
5. Do not store continuous pointer or scroll values in React state. Use motion values, refs, CSS variables, or requestAnimationFrame-managed values.
6. If the design claims a higher motion dial, ship visible motion on the interactions in scope. If scope or dependencies do not support it, lower the motion dial and ship polished static UI.
7. Use CSS transitions rather than keyframes for rapidly triggered dynamic UI because transitions retarget smoothly when interrupted.
8. Use `@starting-style` for modern CSS entry transitions when browser support allows; otherwise use explicit mounted/data-state attributes.
9. Gate hover-only motion behind `@media (hover: hover) and (pointer: fine)` so touch devices do not trigger hover animation on tap.

## Performance Rules

1. Animate `transform` and `opacity` first.
2. Avoid animating `top`, `left`, `width`, `height` unless required.
3. Use `will-change` sparingly.
4. Keep animations interruptible and input-responsive.
5. Test on real devices, not only desktop simulators.
6. Avoid backdrop blur on large scrolling containers; restrict expensive blur/noise layers to fixed, sticky, or small surfaces.
7. Keep decorative loops rare. Continuous animation must serve status, attention, or ambient brand purpose.
8. Prefer percentage transforms for self-sized movement (`translateY(100%)`) instead of hardcoded pixel offsets when entering/exiting drawers, sheets, and toasts.
9. Avoid updating inherited CSS variables every frame on containers with many children; update the animated element's transform directly.
10. Use CSS or WAAPI for predetermined animations under load; use JavaScript animation libraries for dynamic, interruptible interactions.

## Accessibility Rules

1. Respect `prefers-reduced-motion`.
2. Provide non-motion feedback for critical interactions.
3. Avoid mandatory animation that blocks task completion.
4. Keep a safe motion envelope: avoid large-scale screen movement, aggressive parallax, and continuous looping motion.
5. Prefer opacity and small transforms over full-viewport slides or rapid directional shifts.
6. Never auto-play motion that covers more than roughly one-third of the viewport.

Use Tailwind motion variants when possible:

```html
<button class="transition duration-200 ease-out motion-reduce:transition-none motion-reduce:transform-none">
  Save
</button>
```

Use a CSS fallback when a system-wide override is required:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Motion Spec Template

Use this structure when the output is a motion specification:

1. `Interaction`: which UI event or state transition is being defined.
2. `Trigger`: user/system action that starts the transition.
3. `Frequency`: expected frequency and whether animation is justified.
4. `Start state`: visual state before motion.
5. `End state`: visual state after motion.
6. `Animated properties`: prefer `transform` and `opacity`; justify exceptions.
7. `Timing`: duration tier key from the current token set (default `sm` | `md` | `lg`) and easing token.
8. `Reduced motion`: explicit fallback behavior.
9. `Performance note`: implementation constraints, interruption behavior, and device considerations.

## High-Value Interaction Patterns

Prioritize these patterns:

1. Loading skeletons and determinate progress bars.
2. Form submit transitions: idle -> loading -> success/error.
3. Page and panel transitions that preserve orientation.
4. Microfeedback for hover, press, selection, and validation.
5. Toasts and confirmations with clear entry/exit timing.
6. Drag, swipe, and reorder patterns with predictable thresholds.
7. Optimistic updates with rollback when operations fail.
8. Scroll progress indicators for long-form pages.
9. Reveal-on-scroll only when it improves hierarchy or comprehension.
10. Origin-aware popovers and menus that scale from their trigger; keep modal origins centered.
11. Instant subsequent tooltips after one tooltip is already open.
12. Staggered entrance for grouped content with short `30-80ms` offsets; never block interaction while staggering.
13. Asymmetric deliberate actions: slow while confirming, fast on release/cancel.

## Scroll Animation Rules

1. Prefer Intersection Observer for reveal triggers.
2. Keep parallax subtle and readable.
3. Avoid coupling too many properties to scroll progress.
4. Preserve text readability during scroll-linked effects.
5. Disable non-essential scroll effects in reduced-motion mode.
6. Avoid raw `window` scroll listeners for reveal effects unless throttled, cleaned up, and justified.
7. For pinned, scrubbed, stacked, or horizontal-scroll choreography, use a proven library already present or explicitly add the dependency.

## Debugging Animations

Before shipping motion-heavy work:

1. Play the animation at `2x-5x` slower speed or use browser animation tooling.
2. Check whether easing starts or stops abruptly.
3. Check whether opacity, colour, blur, and transform are synchronised.
4. Check transform origins for popovers, menus, drawers, and anchored surfaces.
5. Test touch gestures on real hardware when drag, swipe, or pointer capture is involved.

## Common Failure Modes

1. Over-animation that causes fatigue.
2. Blocking interactions during long transitions.
3. Jank from layout-thrashing properties.
4. Memory leaks from uncleaned animation listeners.
5. Decorative motion with no informational value.
6. `transition: all` instead of named properties.
7. `scale(0)` entry states that make elements appear from nowhere.
8. Same-speed enter and exit when the exit should feel faster.
9. Hover animation on touch devices.
10. Animation on high-frequency keyboard actions.

## Quality Checks

1. Motion explains what changed and why.
2. Motion improves comprehension and does not slow tasks.
3. Repeated use remains comfortable.
4. Reduced-motion mode remains complete and polished.
5. Claimed motion intensity matches what is actually implemented.
6. Animation code avoids continuous re-render loops and layout-thrashing properties.
7. Dynamic UI animations remain interruptible.
8. Slow-motion inspection reveals no wrong origin, delayed response, or mismatched timing.
