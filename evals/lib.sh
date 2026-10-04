# Shared helpers for the cobb eval scenarios. run.sh sources this file, then one scenario.
# A scenario defines PROMPT, setup() (builds the fixture in the current directory), and checks().

# ---- fixtures -----------------------------------------------------------------

init_repo() {  # empty repo on main with a local identity, no hooks, and no signing
  git init -q -b main
  git config user.name "Eval Bot"
  git config user.email "eval@example.invalid"
  git config commit.gpgsign false
  git config core.hooksPath /dev/null
}

base_project() {  # tiny Python library with one passing test, committed on main
  init_repo
  mkdir -p app tests tasks
  printf '__pycache__/\n' > .gitignore
  : > app/__init__.py
  : > tests/__init__.py
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


if __name__ == "__main__":
    unittest.main()
EOF
  write_context "none declared"
  git add -A
  git commit -q -m "chore: initial project"
}

write_context() {  # $1: the Repo conventions line
  cat > tasks/context.md <<EOF
# Project Context: greeter

## Project
- One-liner: A tiny Python library that greets people.
- Target users: Developers who embed greetings in their apps.
- Problem: Each app writes its own greeting text, so the wording drifts.
- Success metrics: All greeting tests pass.
- Repo conventions (optional): $1
- Verification recipe (optional): run \`python3 -m unittest -v\` from the repo root; a passing run ends with OK. The library has no running app; call functions with \`python3 -c\` to check real output.

## Language
- **Greeting**: The text the library returns for one person. _Avoid_: message, salutation

## Current state
- Where we are: first release of the library
- Next up: see \`tasks/\`
- Blockers / risks: none

## Key decisions

## Completed

## Notes / gotchas
EOF
}

add_remote() {  # bare remote beside the repo; push the named branches; origin/HEAD -> main
  git init -q --bare ../remote.git
  git --git-dir=../remote.git symbolic-ref HEAD refs/heads/main
  git remote add origin ../remote.git
  git push -q origin "$@"
  git remote set-head origin main > /dev/null
}

# ---- state --------------------------------------------------------------------

snapshot() {  # branch, HEAD, index, and the content hash of every tracked or untracked file
  echo "branch $(git branch --show-current)"
  echo "head $(git rev-parse HEAD)"
  echo "index $(git diff --cached --binary | git hash-object --stdin)"
  git ls-files -co --exclude-standard | sort -u | while IFS= read -r f; do
    if [ -f "$f" ]; then echo "file $f $(git hash-object -- "$f")"; else echo "file $f missing"; fi
  done
}

# ---- checks -------------------------------------------------------------------
# Each check prints PASS or FAIL with its label. BEFORE and REPLY are set by run.sh.

expect() {  # expect <label> <command...>
  local label=$1
  shift
  if "$@" > /dev/null 2>&1; then echo "PASS  $label"; else echo "FAIL  $label"; fi
}

same_state() { diff <(snapshot) "$BEFORE" > /dev/null; }
same_head() { [ "$(git rev-parse HEAD)" = "$(awk '$1 == "head" {print $2}' "$BEFORE")" ]; }
same_index() { [ "$(git diff --cached --binary | git hash-object --stdin)" = "$(awk '$1 == "index" {print $2}' "$BEFORE")" ]; }

same_files() {  # same_files <path-prefix>...: those files have the same content as before
  local p re=""
  for p in "$@"; do re="$re|^file $p"; done
  re=${re#|}
  diff <(snapshot | grep -E "$re") <(grep -E "$re" "$BEFORE") > /dev/null
}

staged() { git diff --cached --name-only | grep -qx -- "$1"; }
not_staged() { ! staged "$1"; }
reply_has() { grep -Eiq -- "$1" "$REPLY"; }
no_debug_tags() { ! grep -rIq --exclude-dir=.git '\[DEBUG-' .; }

blocker_mentions() {  # a numbered blocker line (B1, B2, ...) matches the pattern
  grep -Ei '^[[:space:]>*|-]*\**B[0-9]+\**[:.)| ]' "$REPLY" | grep -Eiq -- "$1"
}

zero_line_has() {  # the "0 — Recommended" line matches the pattern
  grep -Ei '^[[:space:]>*-]*\**0\**[[:space:]]*[—–-]+[[:space:]]*\**Recommended' "$REPLY" | grep -Eiq -- "$1"
}

ends_with_choices() { python3 "$EVALS_DIR/choices.py" "$REPLY"; }
canonical_choices() { python3 "$EVALS_DIR/choices.py" --canonical "$REPLY"; }

slice_box() {  # slice_box <prd-file> <SL-id>: print the slice's "Slice complete" checkbox state
  awk -v id="$2" '
    $0 ~ "^### " id "[:[:space:]]" { inside = 1; next }
    inside && /^##/ { exit }
    inside && /Slice complete/ { print ($0 ~ /\[[xX]\]/) ? "checked" : "open"; exit }
  ' "$1"
}
slice_checked() { [ "$(slice_box "$1" "$2")" = checked ]; }
slice_open() { [ "$(slice_box "$1" "$2")" = open ]; }
