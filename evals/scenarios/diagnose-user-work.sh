# /cobb diagnose finds the cause and leaves the user's staged, unstaged, and untracked work exactly
# as it was, with no debug tags, stashes, or extra worktrees left behind.
PROMPT='/cobbtest:cobb diagnose parse_price("1,000.50") returns 1.0 instead of 1000.5'

setup() {
  base_project
  cat > app/price.py <<'EOF'
def parse_price(text):
    """Turn a price such as "12.50" or "1,000.50" into a float."""
    whole = text.split(",")[0]
    return float(whole)
EOF
  cat > tests/test_price.py <<'EOF'
import unittest

from app.price import parse_price


class ParsePriceTest(unittest.TestCase):
    def test_plain_price(self):
        self.assertEqual(parse_price("12.50"), 12.5)


if __name__ == "__main__":
    unittest.main()
EOF
  echo "# greeter" > README.md
  git add -A
  git commit -q -m "feat: parse prices"
  printf '\n\ndef farewell(name):\n    return f"Goodbye, {name}!"\n' >> app/greeting.py
  echo "Greets people and parses prices." >> README.md
  git add README.md
  echo "remember: ask about currency symbols" > notes.txt
}

confirmed_price_cause() {
  awk '
    tolower($0) ~ /not verified|inconclusive|unconfirmed/ { if (inside) exit; next }
    tolower($0) ~ /(^|[^[:alnum:]_])confirmed[[:space:]]+cause|cause.*verified/ { inside = 1; print; next }
    inside && tolower($0) ~ /loop|symptom|repro|confirmation|regression|hypothes|cleanup|evidence/ { exit }
    inside { print }
  ' "$REPLY" | grep -Eiq 'split|first.*comma|comma.*first|discard.*(rest|after)|truncat'
}

checks() {
  expect "user work, index, branch, and HEAD unchanged" same_state
  expect "no debug tags left behind" no_debug_tags
  expect "no stash left behind" eval '[ -z "$(git stash list)" ]'
  expect "no extra worktrees left behind" eval '[ "$(git worktree list | wc -l)" -eq 1 ]'
  expect "reply contains a Diagnosis Report" reply_has 'Diagnosis Report'
  expect "report identifies confirmed comma truncation, not just a heading" confirmed_price_cause
}
