# Visual Verification

Load for UI work in `implement` (Verify step), in `review` when a diff changes a user-facing surface, and in `design` implementation or audit delivery. A capture is evidence; a description of the page is not.

## Captures

1. Settle or disable entrance motion first, so an element hidden by animation timing does not read as missing.
2. Capture full pages from the document top at desktop width (1440px) and mobile width (390px). When the tool captures only the viewport, scroll and capture segments until the page is covered. Add the user's real viewport width when known, and any breakpoint the change targets.
3. Capture each state the change touches, such as empty, error, and loading, not only the default.
4. Save captures outside the repository, for example in the system temp directory, named by viewport and state: `desktop.png`, `mobile-error.png`. When the environment's screenshot tool returns images inline rather than as files, name each image's viewport and state in the report instead.
5. Open every capture before using it and confirm it shows what its name claims: no blank or black regions, the right section, a fully loaded state. Recapture an invalid file; never judge from one.

Use the browser automation the environment provides. For touch and gesture behaviour, real hardware is the evidence; emulation proves layout only.

## Rounds

1. Inspect all captures together against the request, the PRD's acceptance criteria, state inventory, and copy matrix, the chosen direction, and the Quality Checks in `references/design/ui.md`. Judge function first: the task completes, states render, focus is visible, and text fits. Then judge hierarchy, spacing, and visual quality.
2. Fix everything found in one batch, recapture the same files, and confirm.
3. Stop after the second round. Report what remains as open findings instead of starting a third pass.

## When the App Cannot Run

Use committed visual-regression goldens or screenshot fixtures when they exist, and state how current they are. Otherwise report the captures as missing evidence, with the exact command or steps that produce them.
