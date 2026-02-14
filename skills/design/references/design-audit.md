# Design Audit Workflow

Use this for reviews of existing UI code or built interfaces.

## Scope and Inputs

1. confirm files, routes, or components to review
2. identify target surface: product UI, marketing web, or mixed
3. identify constraints: accessibility targets, design system, brand rules
4. if files are not provided, ask which files or patterns to review

## Audit Axes

Check each axis:

1. hierarchy and information architecture
2. spacing and layout consistency
3. typography and readability
4. color contrast and semantic clarity
5. interaction states and feedback quality
6. motion quality and reduced-motion compliance
7. responsive behavior
8. implementation risks and maintainability

## Findings Format

List findings first, ordered by severity. For each finding include:

1. issue title
2. impact and risk
3. file and line reference when available
4. concrete fix recommendation

If no issues are found, state that explicitly and list residual risks or test gaps.

## Guideline-Driven Audits

When asked to check against web interface guidelines:

1. fetch fresh rules from:
`https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`
2. apply all relevant rules to the reviewed files
3. output findings exactly in the format required by that guideline
4. if the guideline requires terse `file:line` formatting, follow it strictly
5. do not silently skip rules
