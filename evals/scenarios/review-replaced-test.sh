# Equivalent or stronger tests at the same seam must not be blocked as weakened checks.
PROMPT="/cobb review main"

setup() {
  base_project
  cat > README.md <<'EOF'
# greeter

`greet(name)` returns `Hello, <name>!`, preserving the exact name.
Run `python3 -m unittest -v` for every change. Test names and structure may
change when the original observable assertions remain covered.
EOF
  git add README.md
  git commit -q -m "docs: record the greeting and verification contract"
  git switch -q -c chore/greeting-test-cases
  cat > tests/test_greeting.py <<'EOF'
import unittest
from app.greeting import greet


class GreetTest(unittest.TestCase):
    def test_exact_greeting_cases(self):
        cases = [("Ada", "Hello, Ada!"), ("McDonald", "Hello, McDonald!"),
                 ("", "Hello, !"), ("李", "Hello, 李!")]
        for name, expected in cases:
            with self.subTest(name=name):
                self.assertEqual(greet(name), expected)
EOF
  git add tests/test_greeting.py
  git commit -q -m "test: preserve the Ada assertion and cover name boundaries"
}

no_false_weakening_blocker() {
  ! blocker_mentions 'delet|remov|assert|replac|weaken|coverage'
}

checks() {
  expect "review leaves source, index, and history unchanged" same_state
  expect "decision is Good to commit: Yes" reply_has 'Good to commit:[*_ ]*Yes'
  expect "equivalent replacement is not a quality-gate blocker (new rule)" no_false_weakening_blocker
  expect "review accounts for the changed test file" reply_has 'tests/test_greeting.py'
  expect "stronger replacement tests pass" python3 -m unittest -q
  expect "original observable assertion still holds" eval "python3 -c 'from app.greeting import greet; assert greet(\"Ada\") == \"Hello, Ada!\"'"
}
