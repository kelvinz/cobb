# A suggestions-only report must trigger repair and re-review, even with a Yes verdict.
PROMPT='/cobbtest:cobb commit
The one feature commit is approved work from an earlier run. I authorise safe folding of in-scope review repairs into it. Review against main and complete the repair loop. There are no known blockers. Accepted non-blocking suggestion S1: add a public docstring to farewell that states it preserves the supplied name and returns Goodbye, <name>!. Process this suggestion even if the review returns Good to commit: Yes. Leave the remote untouched.'

setup() {
  base_project
  write_context "default base main"
  git commit -qam "chore: set review conventions"
  add_remote main
  git ls-remote origin > ../remote-before.txt
  git switch -q -c feat/document-farewell
  cat > app/farewell.py <<'EOF'
def farewell(name):
    return f"Goodbye, {name}!"
EOF
  cat > tests/test_farewell.py <<'EOF'
import unittest
from app.farewell import farewell


class FarewellTest(unittest.TestCase):
    def test_preserves_name(self):
        self.assertEqual(farewell("McDonald"), "Goodbye, McDonald!")
EOF
  git add app/farewell.py tests/test_farewell.py
  git commit -qm "feat: say goodbye"
}

checks() {
  expect "suggestion repaired" eval 'python3 -c "from app.farewell import farewell; assert farewell.__doc__"'
  expect "prior commit amended" eval '! same_head'
  expect "still one commit" eval '[ "$(git rev-list --count main..HEAD)" -eq 1 ]'
  expect "no fixup commits left" eval '! git log --format=%s main..HEAD | grep -q "^fixup!"'
  expect "worktree clean" eval '[ -z "$(git status --porcelain)" ]'
  expect "nothing pushed" eval 'diff <(git ls-remote origin) ../remote-before.txt'
  expect "tests pass" python3 -m unittest -q
  expect "final review passed" reply_has 'Good to commit:[*_ ]*Yes|final review[^.]*(passed|good to commit)'
}
