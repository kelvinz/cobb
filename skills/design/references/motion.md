# Motion Mode

Use motion to communicate state, orientation, focus, and continuity.

## Table of Contents

1. Mode Contract
2. Purpose Rules
3. Timing Scale
4. Easing Tokens
5. Performance Rules
6. Accessibility Rules
7. Motion Spec Template
8. High-Value Interaction Patterns
9. Scroll Animation Rules
10. Common Failure Modes
11. Quality Checks

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

## Purpose Rules

Motion should answer at least one of these:

1. Confirm an action happened.
2. Show where an element came from or went.
3. Direct attention to important change.
4. Preserve context during transitions.

If none apply, remove the motion.

## Timing Scale

Use these defaults and adjust intentionally:

1. 100-150ms: hover, press, tiny feedback.
2. 200-300ms: toggles, dropdowns, compact state shifts.
3. 300-500ms: modals, route shifts, medium transitions.
4. 500ms+: multi-step choreographed sequences.

## Easing Tokens

Use consistent easing tokens:

```css
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ease-in: cubic-bezier(0.55, 0, 1, 0.45);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

Use `--ease-spring` only for playful or direct-manipulation moments.

When working alongside `ui` mode, these values map to the Tailwind motion token tier set defined in `references/ui.md` -> `Tailwind Config Pattern`. Default mapping uses `sm: 150ms`, `md: 250ms`, `lg: 400ms` and matching easing tokens.

## Performance Rules

1. Animate `transform` and `opacity` first.
2. Avoid animating `top`, `left`, `width`, `height` unless required.
3. Use `will-change` sparingly.
4. Keep animations interruptible and input-responsive.
5. Test on real devices, not only desktop simulators.

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
3. `Start state`: visual state before motion.
4. `End state`: visual state after motion.
5. `Animated properties`: prefer `transform` and `opacity`; justify exceptions.
6. `Timing`: duration tier key from the current token set (default `sm` | `md` | `lg`) and easing token.
7. `Reduced motion`: explicit fallback behavior.
8. `Performance note`: implementation constraints, interruption behavior, and device considerations.

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

## Scroll Animation Rules

1. Prefer Intersection Observer for reveal triggers.
2. Keep parallax subtle and readable.
3. Avoid coupling too many properties to scroll progress.
4. Preserve text readability during scroll-linked effects.
5. Disable non-essential scroll effects in reduced-motion mode.

## Common Failure Modes

1. Over-animation that causes fatigue.
2. Blocking interactions during long transitions.
3. Jank from layout-thrashing properties.
4. Memory leaks from uncleaned animation listeners.
5. Decorative motion with no informational value.

## Quality Checks

1. Motion explains what changed and why.
2. Motion improves comprehension and does not slow tasks.
3. Repeated use remains comfortable.
4. Reduced-motion mode remains complete and polished.
