# The small-change path: a fix made without any cobb phase or PRD, on the default branch, then
# /cobb commit. It proposes a commit without asking for a PRD, and commits nothing before approval.
PROMPT="/cobbtest:cobb commit"

setup() {
  base_project
  cat > app/greeting.py <<'EOF'
def greet(name):
    return f"Hello, {name.title()}!"
EOF
  git commit -q -am "feat: tidy names in greetings"
  add_remote main
  cat > app/greeting.py <<'EOF'
def greet(name):
    return f"Hello, {name}!"
EOF
  cat > tests/test_greeting.py <<'EOF'
import unittest

from app.greeting import greet


class GreetTest(unittest.TestCase):
    def test_greets_by_name(self):
        self.assertEqual(greet("Ada"), "Hello, Ada!")

    def test_keeps_the_casing_of_names(self):
        self.assertEqual(greet("McDonald"), "Hello, McDonald!")


if __name__ == "__main__":
    unittest.main()
EOF
}

checks() {
  expect "no commit before approval" same_head
  expect "nothing staged before approval" same_index
  expect "code and tests unchanged" same_files app/ tests/
  expect "no PRD created" eval '! ls tasks/f-*.md'
  expect "proposal shows a fix title" reply_has 'fix:'
  expect "recommendation is to commit, not to write a PRD" eval "zero_line_has 'commit' && ! zero_line_has 'prd'"
  expect "reply ends with one choice block" ends_with_choices
  expect "choice block uses the canonical 0 — Recommended form" canonical_choices
}
