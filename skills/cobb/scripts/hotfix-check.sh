#!/usr/bin/env bash
# Pin and recheck the staged snapshot of a cobb hotfix: Staged Review and Commit Check in
# references/hotfix.md.
#
#   hotfix-check.sh pin <default-branch>     # Staged Review steps 1-3; save the output outside the repository
#   hotfix-check.sh verify <pin-file>        # Staged Review step 5, before reporting and before committing
#   hotfix-check.sh commit-check <pin-file>  # Commit Check, after committing
#
# Prints KEY=value facts and one PASS or FAIL line per check, and exits 1 when a check fails.
# pin and verify list untracked files as UNTRACKED lines: you decide whether any of them sits under
# source or test paths. It never stages, commits, or changes files; pin and verify write only the
# staged tree object, through `git write-tree`.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

usage() {
  echo "usage: hotfix-check.sh pin <default-branch> | verify <pin-file> | commit-check <pin-file>" >&2
  exit 2
}

failed=0
pass() { echo "PASS $*"; }
fail() { echo "FAIL $*"; failed=1; }
field() { sed -n "s/^$1=//p" "$pin_file"; }

upstream_now() {  # <upstream>@<hash>, or none
  local up
  if up=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2> /dev/null) \
    && git rev-parse --verify --quiet "$up^{commit}" > /dev/null; then
    echo "$up@$(git rev-parse "$up")"
  else
    echo none
  fi
}

worktree_checks() {  # Staged Review step 2
  if git diff --quiet --ignore-submodules=none; then
    pass "worktree: no unstaged tracked changes"
  else
    fail "worktree: unstaged tracked changes; report them as a blocker and leave them untouched"
  fi
  git ls-files --others --exclude-standard | sed 's/^/UNTRACKED /'
}

case ${1:-} in
  pin)
    [ $# -eq 2 ] || usage
    default=$2
    if [ -z "$(git remote)" ]; then
      freshness=no-remotes
    elif git fetch --all --prune --quiet > /dev/null 2>&1; then
      freshness=refreshed
    else
      freshness="unverified (fetch failed)"
    fi
    branch=$(git branch --show-current)
    head=$(git rev-parse HEAD)
    echo "REMOTE_FRESHNESS=$freshness"
    echo "BRANCH=$branch"
    echo "BRANCH_KIND=base"
    echo "HEAD=$head"
    if [ "$branch" = "$default" ]; then pass "branch: on the default branch $default"; else fail "branch: on '$branch', not the default branch $default"; fi
    busy=""
    for marker in MERGE_HEAD CHERRY_PICK_HEAD rebase-merge rebase-apply; do
      if [ -e "$(git rev-parse --git-path "$marker")" ]; then busy="$busy $marker"; fi
    done
    if [ -z "$busy" ]; then pass "no merge, rebase, or cherry-pick in progress"; else fail "in progress:$busy"; fi
    if [ -z "$(git ls-files -u)" ]; then pass "no unresolved index entries"; else fail "unresolved index entries"; fi
    up=$(upstream_now)
    echo "UPSTREAM=$up"
    if [ "$up" != none ]; then
      if git merge-base --is-ancestor "${up##*@}" "$head"; then
        pass "upstream: ${up%@*} is an ancestor of HEAD"
      else
        fail "upstream: the branch is behind or diverged from ${up%@*}; sync before review"
      fi
    fi
    worktree_checks
    if staged=$(git write-tree 2> /dev/null); then
      echo "STAGED_TREE=$staged"
      if [ "$staged" = "$(git rev-parse 'HEAD^{tree}')" ]; then
        fail "staged tree: same as HEAD's tree, so there is no hotfix to review"
      else
        pass "staged tree: pinned"
      fi
    else
      fail "staged tree: git write-tree failed"
    fi
    ;;
  verify)
    [ $# -eq 2 ] && [ -f "$2" ] || usage
    pin_file=$2
    if [ "$(git branch --show-current)" = "$(field BRANCH)" ]; then pass "branch unchanged"; else fail "branch changed"; fi
    if [ "$(git rev-parse HEAD)" = "$(field HEAD)" ]; then pass "HEAD unchanged"; else fail "HEAD changed"; fi
    if [ "$(git write-tree 2> /dev/null || true)" = "$(field STAGED_TREE)" ]; then pass "staged tree unchanged"; else fail "staged tree changed"; fi
    if [ "$(upstream_now)" = "$(field UPSTREAM)" ]; then pass "upstream unchanged"; else fail "upstream changed"; fi
    worktree_checks
    ;;
  commit-check)
    [ $# -eq 2 ] && [ -f "$2" ] || usage
    pin_file=$2
    if [ "$(git branch --show-current)" = "$(field BRANCH)" ]; then pass "branch unchanged"; else fail "branch changed"; fi
    if [ "$(git rev-parse --verify --quiet 'HEAD^' || true)" = "$(field HEAD)" ]; then
      pass "the new commit's parent is the reviewed HEAD"
    else
      fail "the new commit's parent is not the reviewed HEAD"
    fi
    if [ "$(git rev-parse 'HEAD^{tree}')" = "$(field STAGED_TREE)" ]; then
      pass "the new commit's tree is the reviewed staged tree"
    else
      fail "the new commit's tree differs from the reviewed staged tree"
    fi
    ;;
  *) usage ;;
esac
exit $failed
