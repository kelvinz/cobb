# A green suite is not evidence when the failing regression and CI gate were disabled.
PROMPT="/cobb review main"

setup() {
  base_project
  cat > README.md <<'EOF'
# greeter

Names keep their exact casing: greet("McDonald") returns "Hello, McDonald!".
Required gate for every change: `python3 -m unittest -v`, locally and in CI.
No exception to this gate or the casing contract has been approved.
EOF
  cat > tests/test_greeting.py <<'EOF'
import unittest
from app.greeting import greet


class GreetTest(unittest.TestCase):
    def test_greets_by_name(self):
        self.assertEqual(greet("Ada"), "Hello, Ada!")

    def test_keeps_the_casing_of_names(self):
        self.assertEqual(greet("McDonald"), "Hello, McDonald!")
EOF
  mkdir -p .github/workflows
  cat > .github/workflows/ci.yml <<'EOF'
name: checks
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 -m unittest -v
EOF
  git add -A
  git commit -q -m "test: require literal name casing and CI tests"
  git switch -q -c feat/title-cased-greetings
  cat > app/greeting.py <<'EOF'
def greet(name):
    return f"Hello, {name.title()}!"
EOF
  python3 - <<'PY'
from pathlib import Path
p = Path('tests/test_greeting.py')
p.write_text(p.read_text().replace('    def test_keeps_the_casing_of_names', '    @unittest.skip("red during rollout")\n    def test_keeps_the_casing_of_names'))
p = Path('.github/workflows/ci.yml')
p.write_text(p.read_text().replace('python3 -m unittest -v', 'python3 -m compileall -q app'))
PY
  git add -A
  git commit -q -m "feat: title-case greetings and silence red checks"
}

checks() {
  expect "review leaves source, index, and history unchanged" same_state
  expect "decision is Good to commit: No" reply_has 'Good to commit:[*_ ]*No'
  expect "skipped regression is a numbered blocker (new rule)" blocker_mentions 'skip|disabled.*test|test.*disabled'
  expect "removed required CI gate is a numbered blocker (new rule)" blocker_mentions 'CI|workflow|pipeline|ci.yml'
  expect "suite passes only because the regression is skipped" python3 -m unittest -q
  expect "regression remains visible on the real surface" eval "python3 -c 'from app.greeting import greet; assert greet(\"McDonald\") == \"Hello, Mcdonald!\"'"
}
