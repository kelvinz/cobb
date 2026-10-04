#!/usr/bin/env bash
# Resolve the repository default branch: the Repository default rule in the cobb router (SKILL.md).
#
#   repo-default.sh [--declared <branch>] [--base <branch>]...
#
# --declared: the default base declared under Repo conventions in tasks/context.md, if any.
# --base: each extra base branch declared there (main, master, dev, develop, and trunk are built in).
#
# Prints DEFAULT_BRANCH, DEFAULT_REF, and SOURCE (repo-convention | remote-head | local-fallback) and
# exits 0, or prints UNCLEAR=<reason> and exits 1. It reads local refs only and never fetches.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

usage() {
  echo "usage: repo-default.sh [--declared <branch>] [--base <branch>]..." >&2
  exit 2
}

declared="" bases="main master dev develop trunk"
while [ $# -gt 0 ]; do
  case $1 in
    --declared) [ $# -ge 2 ] || usage; declared=$2; shift 2 ;;
    --base) [ $# -ge 2 ] || usage; bases="$bases $2"; shift 2 ;;
    *) usage ;;
  esac
done

found() {  # found <branch> <ref> <source>
  printf 'DEFAULT_BRANCH=%s\nDEFAULT_REF=%s\nSOURCE=%s\n' "$1" "$2" "$3"
  exit 0
}

if [ -n "$declared" ]; then found "$declared" "$declared" repo-convention; fi

targets="" target_ref=""
for remote in $(git remote); do
  if ref=$(git symbolic-ref --quiet --short "refs/remotes/$remote/HEAD" 2> /dev/null); then
    target=${ref#"$remote/"}
    case " $targets " in *" $target "*) ;; *) targets="$targets $target" ;; esac
    if [ -z "$target_ref" ] || [ "$remote" = origin ]; then target_ref=$ref; fi
  fi
done
set -- $targets
if [ $# -eq 1 ]; then found "$1" "$target_ref" remote-head; fi
if [ $# -gt 1 ]; then
  echo "UNCLEAR=remote HEADs disagree:$targets"
  exit 1
fi

locals=""
for branch in $bases; do
  if git show-ref --verify --quiet "refs/heads/$branch"; then
    case " $locals " in *" $branch "*) ;; *) locals="$locals $branch" ;; esac
  fi
done
set -- $locals
if [ $# -eq 1 ]; then found "$1" "$1" local-fallback; fi
if [ $# -gt 1 ]; then
  echo "UNCLEAR=no remote declares a default, and several local base branches exist:$locals"
else
  echo "UNCLEAR=no remote declares a default, and no local base branch exists"
fi
exit 1
