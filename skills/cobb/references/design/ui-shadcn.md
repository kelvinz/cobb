# Shadcn Component States

Use for shadcn/ui components under the load conditions in `references/design.md`. Check the installed component source and preserve its state semantics; map raw values to the repository's tokens.

1. `Button`
   - States: `hover`, `disabled`, `focus-visible`, `aria-invalid`.
   - Patterns: `disabled:pointer-events-none`, `disabled:opacity-50` or the token equivalent, `focus-visible:ring-2`.
2. `Input`
   - States: `placeholder`, `selection`, `disabled`, `focus-visible`, `aria-invalid`.
   - Patterns: invalid border/ring via `aria-invalid:*` utilities.
3. `TabsTrigger`
   - States: `data-[state=active]`, `disabled`, orientation variants, `focus-visible`.
   - Patterns: active visuals via `data-[state=active]`; orientation-aware styling via group data attributes.
4. `Dialog`
   - States: open/closed animation states, close control, focus ring on the close button.
   - Patterns: `data-[state=open|closed]` on overlay/content; a close button with an accessible label and ring styles.
5. `DropdownMenu`
   - States: item focus, disabled items, sub-menu open state, side-based motion.
   - Patterns: `focus:*`, `data-[disabled]:*`, `data-[state=open]:*`, `data-[side=*]:*`.

Use `data-state`, `aria-*`, and `disabled` consistently across related components.
