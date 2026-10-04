#!/usr/bin/env bash
# Check that the commits from <oldest-commit> through HEAD are safe to rewrite: History Rewrite
# Safety in references/commit-review.md.
#
#   rewrite-check.sh <oldest-commit> [--base <branch>]...
#
# --base: each extra base branch declared under Repo conventions in tasks/context.md (main, master,
# dev, develop, and trunk are built in).
#
# Runs `git fetch --all --prune`, then checks that a feature branch is checked out, the fetch
# succeeded or there are no remotes, no other branch or tag contains a commit in the range, and the
# range is linear. Prints ORIGINAL_HEAD, one PASS or FAIL line per check, and one COMMIT line per
# commit in the range, for the approved-work check you make yourself. Ends with SAFE (exit 0) or
# UNSAFE (exit 1). It never rewrites anything.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

usage() {
  echo "usage: rewrite-check.sh <oldest-commit> [--base <branch>]..." >&2
  exit 2
}

oldest=${1:-}
[ -n "$oldest" ] || usage
shift
bases="main master dev develop trunk"
while [ $# -gt 0 ]; do
  case $1 in
    --base) [ $# -ge 2 ] || usage; bases="$bases $2"; shift 2 ;;
    *) usage ;;
  esac
done

failed=0
pass() { echo "PASS $*"; }
fail() { echo "FAIL $*"; failed=1; }

branch=$(git branch --show-current)
echo "ORIGINAL_HEAD=$(git rev-parse HEAD)"
if [ -z "$branch" ]; then
  fail "feature branch: HEAD is detached"
else
  case " $bases " in
    *" $branch "*) fail "feature branch: $branch is a base branch" ;;
    *) pass "feature branch: $branch" ;;
  esac
fi

if [ -z "$(git remote)" ]; then
  pass "fetch: no remotes"
elif git fetch --all --prune --quiet > /dev/null 2>&1; then
  pass "fetch: remote refs refreshed"
else
  fail "fetch: failed, so the commits may already be published"
fi

if ! git rev-parse --verify --quiet "$oldest^{commit}" > /dev/null; then
  fail "range: $oldest is not a commit"
elif ! git merge-base --is-ancestor "$oldest" HEAD; then
  fail "range: $oldest is not in the current branch's history"
elif ! git rev-parse --verify --quiet "$oldest^" > /dev/null; then
  fail "linear: $oldest has no parent"
else
  range="$oldest^..HEAD"
  merges=$(git rev-list --merges "$range")
  if [ -z "$merges" ]; then pass "linear: no merge commits in $range"; else fail "linear: merge commits in $range: $(echo $merges)"; fi
  published=0
  for commit in $(git rev-list --reverse "$range"); do
    short=$(git rev-parse --short "$commit")
    others=$(git for-each-ref --contains "$commit" --format='%(refname)' refs/heads refs/remotes | grep -vxF "refs/heads/$branch" || true)
    tags=$(git tag --contains "$commit")
    if [ -n "$others" ]; then fail "unpublished: $short is also on $(echo $others)"; published=1; fi
    if [ -n "$tags" ]; then fail "unpublished: $short is tagged $(echo $tags)"; published=1; fi
    echo "COMMIT $(git log -1 --format='%H %s' "$commit")"
  done
  if [ $published -eq 0 ]; then pass "unpublished: only $branch contains the commits in $range"; fi
fi

if [ $failed -eq 0 ]; then
  echo SAFE
else
  echo UNSAFE
  exit 1
fi
