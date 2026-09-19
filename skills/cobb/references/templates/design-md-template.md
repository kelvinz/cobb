# DESIGN.md Template

Use when creating or refreshing the root `DESIGN.md`. The format follows the portable DESIGN.md convention: YAML frontmatter carries machine-readable tokens, and the markdown body explains how to apply them. Tokens are normative; prose gives context.

## Rules

- Record the system as built, from token files, theme configuration, components, and rendered output. Never write rules for a system that does not exist yet.
- Include only tokens the project uses. Omit empty scales and irrelevant sections rather than inventing them.
- Keep one source of truth. When a token file exists (CSS custom properties, a Tailwind theme, token JSON), mirror its values and name the file; the token file wins on conflict.
- Frontmatter keys mirror the token file's names: `--color-accent` becomes `accent`. Never rename a key, whether to a framework's default or to a descriptive name; descriptive names go in the prose, such as "Accent (Fern)".
- Component entries may reference primitives, such as `{colors.primary}`; primitives never reference each other.
- Never overwrite an existing `DESIGN.md` silently. Show it and offer refresh, overwrite, or merge as a numbered choice.

## Frontmatter

```yaml
---
name: <project>
description: <one line>
colors:
  primary: "#1f6feb"
  surface: "#ffffff"
typography:
  body:
    fontFamily: "<stack>"
    fontSize: "1rem"
    lineHeight: 1.5
rounded:
  sm: "4px"
spacing:
  sm: "8px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
---
```

## Body Sections

Keep this order and omit what does not apply:

1. `## Overview`: the system's character in two or three sentences, the visitor modes it serves, and confirmed anti-references.
2. `## Colors`: roles, the colour strategy, and the light or dark decision with its reason.
3. `## Typography`: families, the role scale, measure, and numeral style.
4. `## Layout`: grid, containers, breakpoints, spacing rhythm, and density.
5. `## Elevation & Depth`: the shadow or tonal-layering vocabulary, or "flat" stated explicitly.
6. `## Shapes`: radius, borders, focus ring, and recurring forms.
7. `## Components`: for each component, its shape, colour assignment, states (hover, focus, active, disabled, loading, error), padding, and any motion or focus detail the frontmatter cannot carry.
8. `## Do's and Don'ts`: rules that keep new work on-system, including the Calibration defaults this project rejects.

## Record Mode Scan

Search in this order:

1. CSS custom properties: `--color-*`, `--font-*`, `--space-*`, `--radius-*`, `--shadow-*`, `--ease-*`, and `--duration-*`.
2. Tailwind or other theme configuration.
3. CSS-in-JS themes and token files.
4. The main components: button, input, card, navigation, and dialog.
5. The global stylesheet.
6. Rendered output, when the app can run: computed styles of the body, headings, links, and buttons.

Ask the user only for what the code cannot show, in one round: the system's character, descriptive names for key colours (used in prose, not as keys), and the feel of its components.
