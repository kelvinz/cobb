# UI Examples

Use this reference for concrete UI implementation examples.
Keep `references/ui.md` as the rule source of truth and use these snippets as starting points.

## Table of Contents

1. Tier Set Keys
2. Tailwind Config Example (3 Tiers)
3. Tailwind Config Example (5 Tiers)
4. Tailwind Config Example (7 Tiers)
5. Button Primitive Example (Tier-Agnostic)
6. State Coverage Example

## Tier Set Keys

Use one tier set per token family:

1. `3` tiers: `sm`, `md`, `lg`.
2. `5` tiers: `xs`, `sm`, `md`, `lg`, `xl`.
3. `7` tiers: `2xs`, `xs`, `sm`, `md`, `lg`, `xl`, `2xl`.

Never exceed `7` tiers.

## Tailwind Config Example (3 Tiers)

```ts
import colors from "tailwindcss/colors";

export default {
  theme: {
    extend: {
      colors: {
        brand: { sm: colors.sky[400], md: colors.sky[500], lg: colors.sky[600] },
        bg: { sm: colors.zinc[50], md: colors.zinc[100], lg: colors.zinc[200] },
        fg: { sm: colors.zinc[500], md: colors.zinc[700], lg: colors.zinc[900] },
      },
      spacing: { sm: "0.5rem", md: "1rem", lg: "2rem" },
      borderRadius: { sm: "0.125rem", md: "0.375rem", lg: "0.5rem" },
      opacity: { sm: "0.6", md: "0.8", lg: "1" },
      transitionDuration: { sm: "150ms", md: "250ms", lg: "400ms" },
      transitionTimingFunction: {
        sm: "cubic-bezier(0.16, 1, 0.3, 1)",
        md: "cubic-bezier(0.65, 0, 0.35, 1)",
        lg: "cubic-bezier(0.55, 0, 1, 0.45)",
      },
    },
  },
};
```

## Tailwind Config Example (5 Tiers)

```ts
import colors from "tailwindcss/colors";

export default {
  theme: {
    extend: {
      colors: {
        brand: {
          xs: colors.sky[300],
          sm: colors.sky[400],
          md: colors.sky[500],
          lg: colors.sky[600],
          xl: colors.sky[700],
        },
        bg: {
          xs: colors.zinc[50],
          sm: colors.zinc[100],
          md: colors.zinc[200],
          lg: colors.zinc[300],
          xl: colors.zinc[400],
        },
        fg: {
          xs: colors.zinc[500],
          sm: colors.zinc[600],
          md: colors.zinc[700],
          lg: colors.zinc[800],
          xl: colors.zinc[900],
        },
      },
      spacing: { xs: "0.25rem", sm: "0.5rem", md: "1rem", lg: "1.5rem", xl: "2rem" },
      borderRadius: { xs: "0.125rem", sm: "0.25rem", md: "0.375rem", lg: "0.5rem", xl: "0.75rem" },
      opacity: { xs: "0.5", sm: "0.65", md: "0.8", lg: "0.9", xl: "1" },
      transitionDuration: { xs: "120ms", sm: "180ms", md: "250ms", lg: "320ms", xl: "420ms" },
    },
  },
};
```

## Tailwind Config Example (7 Tiers)

```ts
import colors from "tailwindcss/colors";

export default {
  theme: {
    extend: {
      colors: {
        brand: {
          "2xs": colors.sky[200],
          xs: colors.sky[300],
          sm: colors.sky[400],
          md: colors.sky[500],
          lg: colors.sky[600],
          xl: colors.sky[700],
          "2xl": colors.sky[800],
        },
      },
      spacing: {
        "2xs": "0.125rem",
        xs: "0.25rem",
        sm: "0.5rem",
        md: "0.75rem",
        lg: "1rem",
        xl: "1.5rem",
        "2xl": "2rem",
      },
      borderRadius: {
        "2xs": "0.0625rem",
        xs: "0.125rem",
        sm: "0.25rem",
        md: "0.375rem",
        lg: "0.5rem",
        xl: "0.75rem",
        "2xl": "1rem",
      },
      transitionDuration: {
        "2xs": "90ms",
        xs: "120ms",
        sm: "160ms",
        md: "220ms",
        lg: "300ms",
        xl: "380ms",
        "2xl": "460ms",
      },
    },
  },
};
```

## Button Primitive Example (Tier-Agnostic)

Map `sizeClasses` keys to the active tier set (`3`, `5`, or `7`) instead of duplicating separate component snippets.

```tsx
const sizeClasses = {
  sm: "h-8 rounded-sm px-3 text-sm",
  md: "h-10 rounded-md px-4 text-base",
  lg: "h-12 rounded-lg px-6 text-lg",
};

export const Button = ({ size = "md", className = "", ...props }) => (
  <button
    className={`inline-flex items-center justify-center gap-2 font-medium
      transition-colors duration-md
      bg-brand-md text-white hover:bg-brand-lg active:bg-brand-lg
      focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-md focus-visible:ring-offset-1
      disabled:pointer-events-none disabled:opacity-sm ${sizeClasses[size]} ${className}`}
    {...props}
  />
);
```

## State Coverage Example

```tsx
export const Input = ({ invalid = false, className = "", ...props }) => (
  <input
    aria-invalid={invalid || undefined}
    className={`w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm
      placeholder:text-zinc-500
      focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-md
      aria-invalid:border-red-500 aria-invalid:ring-red-500
      disabled:pointer-events-none disabled:opacity-sm ${className}`}
    {...props}
  />
);
```
