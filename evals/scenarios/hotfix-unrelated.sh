# /cobb commit hotfix: the fix is staged, unrelated work sits beside it. Nothing is committed before
# approval, and the unrelated work stays exactly as the user left it.
PROMPT='/cobbtest:cobb commit hotfix greet() title-cases names, so "McDonald" becomes "Mcdonald". Urgent: the live signup page greets customers with the wrong name. The fix and its test are already staged. Follow-up: none.'

setup() {
  base_project
  cat > app/greeting.py <<'EOF'
def greet(name):
    return f"Hello, {name.title()}!"
EOF
  mkdir -p notes
  echo "- tidy the README" > notes/todo.md
  git add -A
  git commit -q -m "feat: tidy names in greetings"
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
  git add app/greeting.py tests/test_greeting.py
  echo "- write the release notes" >> notes/todo.md
  echo "scratch thoughts, not for git" > scratch.txt
}

checks() {
  expect "no commit before approval" same_head
  expect "staged fix is still staged" staged app/greeting.py
  expect "unrelated edit unchanged" same_files notes/
  expect "unrelated edit still unstaged" not_staged notes/todo.md
  expect "untracked scratch file unchanged" same_files scratch.txt
  expect "no stash left behind" eval '[ -z "$(git stash list)" ]'
  expect "reply ends with one choice block" ends_with_choices
  expect "choice block uses the canonical 0 — Recommended form" canonical_choices
}
