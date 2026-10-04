# Bare /cobb shows the menu, stays read-only, and recommends implementing the one ready PRD.
PROMPT="/cobbtest:cobb"

setup() {
  base_project
  prd_f01 "[ ]" > tasks/f-01-greet-by-time-of-day.md
  git add -A
  git commit -q -m "chore: add the f-01 PRD"
}

checks() {
  expect "menu leaves the repo unchanged" same_state
  expect "reply ends with one choice block" ends_with_choices
  expect "choice block uses the canonical 0 — Recommended form" canonical_choices
  expect "recommendation is to implement f-01" zero_line_has 'implement'
}
