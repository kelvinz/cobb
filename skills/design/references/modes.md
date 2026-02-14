# Mode Map

Choose a primary mode before work starts.

- `product-ui`: Typical requests include dashboards, admin tools, SaaS screens, settings, and data interfaces. Primary goal is clarity, speed, and trust. Visual bias is restrained, structured, and high-signal.
- `marketing-web`: Typical requests include landing pages, brand websites, and campaigns. Primary goal is memorability, conversion, and brand character. Visual bias is expressive, bold, and atmospheric.
- `interaction-motion`: Typical requests include microinteractions, transitions, loading flows, and gestures. Primary goal is feedback and continuity. Visual bias is purposeful, performant, and interruptible.
- `static-canvas`: Typical requests include posters, editorial covers, art sheets, and one-pagers. Primary goal is visual impact through composition. Visual bias is concept-first, text-light, and crafted.
- `design-audit`: Typical requests include UI review, UX checks, and accessibility audits. Primary goal is issue detection and prioritization. Visual bias is evidence-first critique.

## Scope Boundaries

1. use `product-ui` for utility tools and app surfaces
2. use `marketing-web` for promotional storytelling surfaces
3. use `interaction-motion` as a companion mode when behavior polish is required
4. use `static-canvas` for non-interactive outputs
5. use `design-audit` for critique and compliance checks

If unsure between `product-ui` and `marketing-web`, ask which outcome matters most: task efficiency or brand expression.

## Output Contract

Produce mode-specific deliverables:

1. `product-ui`
- ship working code
- include token definitions and key component states
- include brief hierarchy rationale
2. `marketing-web`
- ship working code
- include clear visual direction summary, type pair, and color system
- include responsive behavior notes for mobile and desktop
3. `interaction-motion`
- ship working code or precise implementation spec
- include timing and easing selections
- include reduced-motion fallback
4. `static-canvas`
- ship one `.png` or `.pdf` unless multi-page is requested
- ship a matching philosophy `.md`
- keep text minimal and design-led
5. `design-audit`
- list findings first, ordered by severity
- include file and line references when code is available
- include residual risks and test gaps

## Complexity Budget

Pick one level early, then stay consistent:

1. `baseline`: practical, concise, low-risk implementation
2. `expressive`: visible design personality with controlled complexity
3. `maximal`: heavy visual and motion detail with strict quality control

Use `baseline` by default for internal tools and constrained timelines. Use `expressive` for most public-facing work. Use `maximal` only when the brief explicitly rewards spectacle and the implementation budget supports it.
