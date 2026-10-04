# /cobb implement on a ready PRD with two slices that change the same lines, already on its feature
# branch. It must build every slice in one run, commit nothing, and recommend /cobb commit.
PROMPT="/cobbtest:cobb implement tasks/f-03-greeting-styles.md"

setup() {
  base_project
  add_remote main
  git switch -q -c feat/f-03-greeting-styles
  prd_f03 > tasks/f-03-greeting-styles.md
}

checks() {
  local prd=tasks/f-03-greeting-styles.md
  expect "no commits made" same_head
  expect "formal style works" eval "python3 -c 'from app.greeting import greet; assert greet(\"Ada\", style=\"formal\") == \"Good day, Ada.\"'"
  expect "casual style works" eval "python3 -c 'from app.greeting import greet; assert greet(\"Ada\", style=\"casual\") == \"Hey Ada!\"'"
  expect "tests pass" python3 -m unittest -q
  expect "SL-001 is checked" slice_checked "$prd" SL-001
  expect "SL-002 is checked" slice_checked "$prd" SL-002
  expect "reply recommends /cobb commit" reply_has 'cobb commit'
}
