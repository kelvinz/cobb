# Read-only /cobb review of a feature branch with no upstream. The base must come from the repo
# conventions (develop, not origin/HEAD's main), and the pre-checked marketing box must be a blocker.
# The coverage check is new: only the edited skill asks for it.
PROMPT="/cobbtest:cobb review"

setup() {
  base_project
  write_context 'default base `develop`; merge preference: merge-commit'
  git commit -q -am "chore: declare develop as the default base"
  git switch -q -c develop
  echo "# greeter" > README.md
  git add README.md
  git commit -q -m "chore: add README"
  add_remote main develop
  git switch -q -c feat/f-02-newsletter-signup
  prd_f02 > tasks/f-02-newsletter-signup.md
  cat > app/signup.py <<'EOF'
def render_signup_form():
    return (
        '<form method="post" action="/signup">'
        '<label for="email">Email</label>'
        '<input id="email" name="email" type="email" required>'
        '<label><input type="checkbox" name="marketing" checked> Send me product news and offers</label>'
        '<button type="submit">Sign up</button>'
        "</form>"
    )
EOF
  cat > tests/test_signup.py <<'EOF'
import unittest

from app.signup import render_signup_form


class SignupFormTest(unittest.TestCase):
    def test_form_has_email_field_and_submit_button(self):
        html = render_signup_form()
        self.assertIn('name="email"', html)
        self.assertIn("Sign up</button>", html)

    def test_form_offers_product_news(self):
        self.assertIn('name="marketing"', render_signup_form())


if __name__ == "__main__":
    unittest.main()
EOF
  git add -A
  git commit -q -m "feat: add the newsletter signup form"
}

consent_blocker() {  # a numbered blocker names the pre-checked (pre-ticked) marketing or consent box
  grep -Ei '^[[:space:]>*|-]*\**B[0-9]+' "$REPLY" | grep -Ei 'checked|ticked|pre-?selected|by default' | grep -Eiq 'consent|marketing|opt|offers|news'
}

coverage_lists_all() {  # after a "Coverage" heading, the reply names every changed file
  local section f
  section=$(awk 'tolower($0) ~ /coverage/ {on = 1} on' "$REPLY")
  [ -n "$section" ] || return 1
  for f in $(git diff --name-only develop...HEAD); do
    grep -Fq -- "$f" <<< "$section" || return 1
  done
}

checks() {
  expect "review leaves the repo unchanged" same_state
  expect "no extra worktrees left behind" eval '[ "$(git worktree list | wc -l)" -eq 1 ]'
  expect "decision is Good to commit: No" reply_has 'Good to commit:[*_ ]*No'
  expect "base is develop, from repo conventions" reply_has 'develop.*repo-convention|repo-convention.*develop'
  expect "pre-checked marketing box is a blocker" consent_blocker
  expect "coverage names every changed file (new rule)" coverage_lists_all
}
