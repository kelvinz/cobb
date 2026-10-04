# /cobb commit proposes the commit and waits: nothing is staged or committed before approval.
PROMPT="/cobbtest:cobb commit"

setup() {
  base_project
  add_remote main
  git switch -q -c feat/f-01-greet-by-time-of-day
  prd_f01 "[x]" > tasks/f-01-greet-by-time-of-day.md
  cat > app/greeting.py <<'EOF'
def greet(name, hour=None):
    if hour is not None and 5 <= hour <= 11:
        return f"Good morning, {name}!"
    if hour is not None and 12 <= hour <= 17:
        return f"Good afternoon, {name}!"
    if hour is not None and 18 <= hour <= 22:
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
        cases = {4: "Hello", 5: "Good morning", 11: "Good morning", 12: "Good afternoon",
                 17: "Good afternoon", 18: "Good evening", 22: "Good evening", 23: "Hello"}
        for hour, opening in cases.items():
            self.assertEqual(greet("Ada", hour=hour), f"{opening}, Ada!")


if __name__ == "__main__":
    unittest.main()
EOF
}

checks() {
  expect "no commit before approval" same_head
  expect "nothing staged before approval" same_index
  expect "code and tests unchanged" same_files app/ tests/
  expect "no stash left behind" eval '[ -z "$(git stash list)" ]'
  expect "proposal shows a feat title" reply_has 'feat:'
  expect "reply ends with one choice block" ends_with_choices
  expect "choice block uses the canonical 0 — Recommended form" canonical_choices
}
