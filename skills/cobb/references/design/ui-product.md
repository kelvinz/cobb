# Product and Reading UI

Use for Operate surfaces (app UI, dashboards, editors, admin, settings, tools) and Read surfaces (docs, articles, guides, help, changelogs), under the load conditions in `references/design.md`.

Familiarity is a feature here. The test: can a user fluent in this category trust every control at a glance, or must they pause at controls that are subtly unfamiliar? The failure is strangeness without purpose, not plainness: over-decorated buttons, mismatched controls, display fonts in labels, and invented affordances for standard tasks.

## Typography

1. One well-tuned family usually carries headings, labels, body, and data.
2. Use a fixed rem scale with a tight ratio, about 1.125 to 1.2 between steps. Fluid `clamp()` headings do not suit product UI.
3. Keep prose within 65 to 75 characters; tables and dense data may run wider.
4. Use tabular numerals for data that aligns or changes.
5. Keep display faces out of labels, buttons, and data.

## Colour

1. Restrained is the default strategy: neutrals plus one accent.
2. Reserve the accent for primary actions, current selection, and state. Never use it for decoration or on inactive states.
3. Standardise the state vocabulary: hover, focus, active, disabled, selected, loading, error, warning, success, and info.
4. Use a second neutral layer, slightly warmer or cooler than the content surface, for sidebars, toolbars, and panels.

## Layout and Components

1. Make responsive behaviour structural: collapse the sidebar, reflow tables, and change column counts at breakpoints.
2. Give every interactive component default, hover, focus-visible, active, disabled, loading, and error states.
3. Use skeletons for loading content, not spinners in the middle of it.
4. Make empty states teach the interface: what will appear here and the first action to take.
5. Keep one affordance vocabulary: the same button shape, form controls, and icon style everywhere. A save button that looks different in two places is a defect.
6. Let overlays escape clipping containers: use `<dialog>`, the popover API, `position: fixed`, or a portal.
7. Try inline and progressive alternatives before a modal.
8. Keep standard patterns: a top bar with side navigation, breadcrumbs, tabs, and command palettes. Density is allowed when users need it.

## Motion

1. Keep most transitions at 150 to 250ms. Motion conveys state, feedback, loading, and reveal only.
2. Avoid orchestrated page-load sequences: the product loads into a task.

## Read Surfaces

1. Structure for the reader's question: descriptive headings in a real hierarchy, a table of contents for long pages, and anchor links.
2. Answer wayfinding: where the reader is, what comes next, and how to search.
3. Make code samples copyable, name their language, and handle long lines deliberately.

## Charts and Data

1. Choose the chart by the question it answers:
   - trend over time: a line; an area only for cumulative totals
   - comparing categories: a bar sorted by value, horizontal when labels are long; a table beyond about fifteen categories
   - part of a whole: a single stacked or proportion bar; a pie only for two to five parts
   - distribution: a histogram or box plot
   - relationship: a scatter plot
   - one metric: a number with its comparison and trend, not a chart; fewer than four data points is a number too
2. Never encode meaning by colour alone: label series directly and vary line style or pattern.
3. Give every chart a text fallback: a visible or toggleable data table and a one-sentence summary. Make values reachable by keyboard.
4. Start bar axes at zero, label units, and use tabular numerals.
5. Render SVG up to about a thousand points. Above that, use canvas with downsampling, and aggregate beyond about ten thousand.
