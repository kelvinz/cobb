#!/usr/bin/env bash
# Pin what a cobb branch review inspects (review.md Workflow step 1), or recheck it before the
# review fingerprint (step 8).
#
#   review-pin.sh pin [--arg <ref>] [--target <ref>] [--session-start <hash>] [--declared <branch>] [--base <branch>]...
#   review-pin.sh verify <pin-file>
#
# pin refreshes remote refs (best-effort), records the branch and HEAD, classifies the branch,
# resolves the comparison base by the review ladder, pins its hash, and prints KEY=value facts.
# Save its output to a file outside the repository for verify. pin exits 1 with ERROR= or UNCLEAR=
# when it cannot pin a base. verify prints PASS or FAIL for the branch, HEAD, and base hash, and
# exits 1 when any of them changed. Neither changes files, the index, or branches.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
cd "$(git rev-parse --show-toplevel)"

usage() {
  echo "usage: review-pin.sh pin [--arg <ref>] [--target <ref>] [--session-start <hash>] [--declared <branch>] [--base <branch>]..." >&2
  echo "       review-pin.sh verify <pin-file>" >&2
  exit 2
}

pin() {
  local arg="" target="" session="" default_args="" bases="main master dev develop trunk"
  while [ $# -gt 0 ]; do
    case $1 in
      --arg) [ $# -ge 2 ] || usage; arg=$2; shift 2 ;;
      --target) [ $# -ge 2 ] || usage; target=$2; shift 2 ;;
      --session-start) [ $# -ge 2 ] || usage; session=$2; shift 2 ;;
      --declared) [ $# -ge 2 ] || usage; default_args="$default_args --declared $2"; shift 2 ;;
      --base) [ $# -ge 2 ] || usage; default_args="$default_args --base $2"; bases="$bases $2"; shift 2 ;;
      *) usage ;;
    esac
  done

  local freshness branch head kind upstream base_ref source base_hash out
  if [ -z "$(git remote)" ]; then
    freshness=no-remotes
  elif git fetch --all --prune --quiet > /dev/null 2>&1; then
    freshness=refreshed
  else
    freshness="unverified (fetch failed)"
  fi
  echo "REMOTE_FRESHNESS=$freshness"

  branch=$(git branch --show-current)
  if [ -z "$branch" ]; then
    echo "ERROR=HEAD is detached; check out or create a branch"
    exit 1
  fi
  head=$(git rev-parse HEAD)
  kind=feature
  case " $bases " in *" $branch "*) kind=base ;; esac
  echo "BRANCH=$branch"
  echo "BRANCH_KIND=$kind"
  echo "HEAD=$head"

  upstream=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2> /dev/null || true)
  if [ -n "$upstream" ] && ! git rev-parse --verify --quiet "$upstream^{commit}" > /dev/null; then upstream=""; fi
  if [ -n "$arg" ]; then
    base_ref=$arg source=argument
  elif [ -n "$target" ]; then
    base_ref=$target source=finalise-target
  elif [ "$kind" = base ] && [ -n "$session" ]; then
    if [ -n "$upstream" ] && [ "$(git rev-parse "$upstream")" != "$head" ]; then
      base_ref=$upstream source=upstream
    else
      base_ref=$session source=session-start
    fi
  elif [ -n "$upstream" ]; then
    base_ref=$upstream source=upstream
  elif out=$(bash "$here/repo-default.sh" $default_args); then
    base_ref=$(printf '%s\n' "$out" | sed -n 's/^DEFAULT_REF=//p')
    source=$(printf '%s\n' "$out" | sed -n 's/^SOURCE=//p')
  else
    printf '%s\n' "$out"
    exit 1
  fi
  if ! base_hash=$(git rev-parse --verify --quiet "$base_ref^{commit}"); then
    echo "ERROR=the base ref does not resolve to a commit: $base_ref"
    exit 1
  fi
  echo "BASE_REF=$base_ref"
  echo "BASE_SOURCE=$source"
  echo "BASE_HASH=$base_hash"
  echo "MERGE_BASE=$(git merge-base "$base_hash" "$head" 2> /dev/null || echo none)"
  if git merge-base --is-ancestor "$base_hash" "$head"; then echo "BASE_IS_ANCESTOR=yes"; else echo "BASE_IS_ANCESTOR=no"; fi
  if [ "$head" = "$base_hash" ]; then echo "RANGE_EMPTY=yes"; else echo "RANGE_EMPTY=no"; fi
  if [ -z "$(git status --porcelain)" ]; then echo "WORKTREE_CLEAN=yes"; else echo "WORKTREE_CLEAN=no"; fi
}

verify() {
  local file=${1:-} failed=0 base_ref now
  [ -f "$file" ] || usage
  field() { sed -n "s/^$1=//p" "$file"; }
  if [ "$(git branch --show-current)" = "$(field BRANCH)" ]; then echo "PASS branch unchanged"; else echo "FAIL branch changed"; failed=1; fi
  if [ "$(git rev-parse HEAD)" = "$(field HEAD)" ]; then echo "PASS HEAD unchanged"; else echo "FAIL HEAD changed"; failed=1; fi
  base_ref=$(field BASE_REF)
  now=$(git rev-parse --verify --quiet "$base_ref^{commit}" || true)
  if [ "$now" = "$(field BASE_HASH)" ]; then echo "PASS base $base_ref unchanged"; else echo "FAIL base $base_ref moved"; failed=1; fi
  if [ -z "$(git status --porcelain)" ]; then echo "WORKTREE_CLEAN=yes"; else echo "WORKTREE_CLEAN=no"; fi
  exit $failed
}

case ${1:-} in
  pin) shift; pin "$@" ;;
  verify) shift; verify "$@" ;;
  *) usage ;;
esac
