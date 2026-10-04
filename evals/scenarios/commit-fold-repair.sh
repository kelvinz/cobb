# /cobb commit, then the reply "0" approves the proposal. The commit lands, review runs, and each
# repair is folded into that same commit: one commit, no fixup commits, nothing pushed, a clean
# worktree. The PRD says evening is 18-22, but the code also greets hour 23 with "Good evening",
# and the tests skip the PRD's edge-case hours, so the review has something to repair.
PROMPT="/cobbtest:cobb commit"
FOLLOW_UPS=("0")

setup() {
  base_project
  add_remote main
  git ls-remote origin > ../remote-before.txt
  git switch -q -c feat/f-01-greet-by-time-of-day
  prd_f01 "[x]" > tasks/f-01-greet-by-time-of-day.md
  cat > app/greeting.py <<'EOF'
def greet(name, hour=None):
    if hour is not None and 5 <= hour <= 11:
        return f"Good morning, {name}!"
    if hour is not None and 12 <= hour <= 17:
        return f"Good afternoon, {name}!"
    if hour is not None and 18 <= hour <= 23:
        return f"Good evening, {name}!"
    return f"Hello, {name}!"
EOF
  cat > tests/test_greeting.py <<'EOF'
import unittest

from app.greeting import greet


class GreetTest(unittest.TestCase):
    def test_greets_by_name(self):
        self.assertEqual(greet("Ada"), "Hello, Ada!")

    def test_greets_by_time_of_day(self):
        self.assertEqual(greet("Ada", hour=9), "Good morning, Ada!")
        self.assertEqual(greet("Ada", hour=20), "Good evening, Ada!")


if __name__ == "__main__":
    unittest.main()
EOF
}

checks() {
  expect "one commit: repairs folded, no extra commits" eval '[ "$(git rev-list --count main..HEAD)" -eq 1 ]'
  expect "no fixup commits left" eval '! git log --format=%s main..HEAD | grep -q "^fixup!"'
  expect "worktree clean" eval '[ -z "$(git status --porcelain)" ]'
  expect "still on the feature branch" eval '[ "$(git branch --show-current)" = feat/f-01-greet-by-time-of-day ]'
  expect "nothing pushed" eval 'diff <(git ls-remote origin) ../remote-before.txt'
  expect "tests pass" python3 -m unittest -q
  expect "final review passed" reply_has 'Good to commit:[*_ ]*Yes|final review[^.]*(passed|good to commit)'
  expect "hour 23 fixed in the commit (needs review to catch it)" eval "python3 -c 'from app.greeting import greet; assert greet(\"Ada\", hour=23) == \"Hello, Ada!\"'"
}
