# Build only the assigned SL-001, leave SL-002 open, and return its evidence.
PROMPT="/cobbtest:cobb implement tasks/f-03-greeting-styles.md"

setup() {
  base_project
  printf 'Do only the scope assigned by the user.\n' > AGENTS.md
  git add AGENTS.md
  git commit -qm "chore: set user assignment instructions"
  add_remote main
  git switch -q -c feat/f-03-greeting-styles
  prd_f03 > tasks/f-03-greeting-styles.md
  PROMPT="$PROMPT
Assignment from my workflow: implement only SL-001. Leave SL-002 and its acceptance criterion AC-002 open, and leave casual style unsupported. Use the working directory $PWD at starting revision $(git rev-parse HEAD). Read $PWD/AGENTS.md, $PWD/tasks/context.md, and $PWD/tasks/f-03-greeting-styles.md, plus the selected cobb skill and its implement/TDD references. You may update code, tests, and tracking for SL-001 only. Return its verification evidence and blockers to me; do not start the next phase, stage changes, or commit."
}

casual_unsupported() {
  python3 - <<'PY'
from app.greeting import greet
try:
    greet("Ada", style="casual")
except ValueError:
    pass
else:
    raise AssertionError("SL-002 is outside the assignment")
PY
}

checks() {
  local prd=tasks/f-03-greeting-styles.md
  expect "no commits made" same_head
  expect "nothing staged" same_index
  expect "user instructions unchanged" same_files AGENTS.md
  expect "formal style works" eval "python3 -c 'from app.greeting import greet; assert greet(\"Ada\", style=\"formal\") == \"Good day, Ada.\"'"
  expect "plain greeting unchanged" eval "python3 -c 'from app.greeting import greet; assert greet(\"Ada\") == \"Hello, Ada!\"'"
  expect "unassigned casual style is unsupported (new rule)" casual_unsupported
  expect "tests pass" python3 -m unittest -q
  expect "SL-001 is checked" slice_checked "$prd" SL-001
  expect "SL-002 stays open (new rule)" slice_open "$prd" SL-002
  expect "AC-002 stays open (new rule)" eval "grep -Eq '^[-*] \[ \] AC-002:' '$prd'"
}
