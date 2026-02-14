# Motion System

Use motion to communicate state, orientation, focus, and continuity.

## Purpose Rules

Motion should answer at least one of these:

1. confirm an action happened
2. show where an element came from or went
3. direct attention to important change
4. preserve context during transitions

If none apply, remove the motion.

## Timing Scale

Use these defaults and adjust intentionally:

1. 100-150ms: hover, press, tiny feedback
2. 200-300ms: toggles, dropdowns, compact state shifts
3. 300-500ms: modals, route shifts, medium transitions
4. 500ms+: multi-step choreographed sequences

## Easing Tokens

Use consistent easing tokens:

```css
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ease-in: cubic-bezier(0.55, 0, 1, 0.45);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

Use `--ease-spring` only for playful or direct-manipulation moments.

## Performance Rules

1. animate `transform` and `opacity` first
2. avoid animating `top`, `left`, `width`, `height` unless required
3. use `will-change` sparingly
4. keep animations interruptible and input-responsive
5. test performance on real devices, not only desktop simulators

## Accessibility Rules

1. respect `prefers-reduced-motion`
2. provide non-motion feedback for critical interactions
3. avoid mandatory animation that blocks task completion

Use a reduced-motion fallback:

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

## High-Value Interaction Patterns

Prioritize these patterns:

1. loading skeletons and determinate progress bars
2. form submit transitions: idle -> loading -> success/error
3. page and panel transitions that preserve orientation
4. microfeedback for hover, press, selection, and validation
5. toasts and confirmations with clear entry/exit timing
6. drag, swipe, and reorder patterns with predictable thresholds
7. optimistic updates with rollback when operations fail
8. scroll progress indicators for long-form pages
9. reveal-on-scroll only when it improves hierarchy or comprehension

## Scroll Animation Rules

1. prefer Intersection Observer for reveal triggers
2. keep parallax subtle and readable
3. avoid coupling too many properties to scroll progress
4. preserve text readability during scroll-linked effects
5. disable non-essential scroll effects in reduced-motion mode

## Common Failure Modes

1. over-animation that causes fatigue
2. blocking interactions during long transitions
3. jank from layout-thrashing properties
4. memory leaks from uncleaned animation listeners
5. decorative motion with no informational value

## Quality Checks

1. motion explains what changed and why
2. motion improves comprehension and does not slow tasks
3. repeated use remains comfortable
4. reduced-motion mode remains complete and polished
