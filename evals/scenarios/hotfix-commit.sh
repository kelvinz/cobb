# /cobb commit hotfix, then the reply "0" approves it. The staged fix is reviewed and committed
# straight to main: one new commit whose parent is the old HEAD, the fix in it, a clean worktree,
# and nothing pushed.
PROMPT='/cobbtest:cobb commit hotfix greet() title-cases names, so "McDonald" becomes "Mcdonald". Urgent: the live signup page greets customers with the wrong name. The fix and its test are already staged. Follow-up: none.'
FOLLOW_UPS=("0")

setup() {
  base_project
  cat > app/greeting.py <<'EOF'
def greet(name):
    return f"Hello, {name.title()}!"
EOF
  git commit -q -am "feat: tidy names in greetings"
  add_remote main
  git rev-parse HEAD > ../head-before.txt
  git ls-remote origin > ../remote-before.txt
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
  git add app/greeting.py tests/test_greeting.py
}

checks() {
  expect "one new commit on main" eval '[ "$(git rev-list --count "$(cat ../head-before.txt)..HEAD")" -eq 1 ]'
  expect "its parent is the old HEAD" eval '[ "$(git rev-parse HEAD^)" = "$(cat ../head-before.txt)" ]'
  expect "still on main" eval '[ "$(git branch --show-current)" = main ]'
  expect "the fix is in the commit" eval "git show HEAD:app/greeting.py | grep -qF 'Hello, {name}!'"
  expect "the commit title is a fix" eval 'git log -1 --format=%s | grep -q "fix:"'
  expect "worktree clean" eval '[ -z "$(git status --porcelain)" ]'
  expect "nothing pushed" eval 'diff <(git ls-remote origin) ../remote-before.txt'
  expect "tests pass" python3 -m unittest -q
}
