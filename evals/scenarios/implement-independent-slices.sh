# /cobb implement on a ready PRD with two independent slices that touch different files.
# Both get built, nothing is committed, and no extra checkout is left behind.
PROMPT="/cobbtest:cobb implement tasks/f-05-polite-phrases.md"

setup() {
  base_project
  add_remote main
  git switch -q -c feat/f-05-polite-phrases
  prd_f05 > tasks/f-05-polite-phrases.md
}

checks() {
  local prd=tasks/f-05-polite-phrases.md
  expect "no commits made" same_head
  expect "thank-you works" eval "python3 -c 'from app.thanks import thank; assert thank(\"Ada\") == \"Thank you, Ada!\"'"
  expect "farewell works" eval "python3 -c 'from app.farewell import farewell; assert farewell(\"Ada\") == \"Goodbye, Ada!\"'"
  expect "tests pass" python3 -m unittest -q
  expect "SL-001 is checked" slice_checked "$prd" SL-001
  expect "SL-002 is checked" slice_checked "$prd" SL-002
  expect "no extra checkout left behind" eval '[ "$(git worktree list | wc -l)" -eq 1 ]'
  expect "reply recommends /cobb commit" reply_has 'cobb commit'
}
