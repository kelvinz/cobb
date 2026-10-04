# Resume a clean feature branch with two previously approved commits. Repair an
# accepted blocker in the first and a suggestion in the second, preserving intent.
PROMPT='/cobbtest:cobb commit
The two commits on this feature branch are approved work from an earlier run. I authorise in-scope review repairs and safe folding into both commits. Review the whole branch against main and continue the repair loop, including suggestions even when Good to commit is Yes.
Accepted findings to verify and repair: B1 — greet(name, hour=23) must return Hello, not Good evening (the approved evening range is 18–22). S1 — add a public docstring to farewell stating that it preserves the supplied name and returns Goodbye, <name>!; this documentation improvement belongs in the farewell commit. No other product changes. Leave the two original commit intents separate, with nothing pushed.'

setup() {
  base_project
  write_context "default base main"
  git commit -q -am "chore: set review conventions"
  add_remote main
  git ls-remote origin > ../remote-before.txt
  git switch -q -c feat/prior-greetings
  cat > app/greeting.py <<'EOF'
def greet(name, hour=None):
    if hour is not None and 18 <= hour <= 23:
        return f"Good evening, {name}!"
    return f"Hello, {name}!"
EOF
  git add app/greeting.py
  git commit -qm "feat: greet people in the evening"
  cat > app/farewell.py <<'EOF'
def farewell(name):
    return f"Goodbye, {name}!"
EOF
  git add app/farewell.py
  git commit -qm "feat: say goodbye"
  git rev-list --reverse main..HEAD > ../commits-before.txt
  git log --format=%s main..HEAD > ../subjects-before.txt
}

first_commit_fixed() {
  git show HEAD~1:app/greeting.py | python3 -c 'import sys; scope = {}; exec(sys.stdin.read(), scope); assert scope["greet"]("Ada", hour=23) == "Hello, Ada!"; assert scope["greet"]("Ada", hour=22) == "Good evening, Ada!"'
}

checks() {
  expect "still two commits, not follow-ups" eval '[ "$(git rev-list --count main..HEAD)" -eq 2 ]'
  expect "original commit intents preserved" eval 'diff <(git log --format=%s main..HEAD) ../subjects-before.txt'
  expect "both prior commit hashes changed" eval '[ "$(git rev-parse HEAD~1)" != "$(head -n 1 ../commits-before.txt)" ] && [ "$(git rev-parse HEAD)" != "$(tail -n 1 ../commits-before.txt)" ]'
  expect "blocker folded into first commit" first_commit_fixed
  expect "suggestion folded into second commit" eval 'python3 -c "from app.farewell import farewell; assert farewell.__doc__; assert farewell(\"McDonald\") == \"Goodbye, McDonald!\""'
  expect "first commit has no farewell changes" eval '! git cat-file -e HEAD~1:app/farewell.py'
  expect "no fixup commits left" eval '! git log --format=%s main..HEAD | grep -q "^fixup!"'
  expect "worktree clean" eval '[ -z "$(git status --porcelain)" ]'
  expect "nothing pushed" eval 'diff <(git ls-remote origin) ../remote-before.txt'
  expect "tests pass" python3 -m unittest -q
  expect "final review passed" reply_has 'Good to commit:[*_ ]*Yes|final review[^.]*(passed|good to commit)'
}
