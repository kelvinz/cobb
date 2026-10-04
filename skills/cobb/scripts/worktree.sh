#!/usr/bin/env bash
# Create a private working-state checkout: Isolated work in the cobb router (SKILL.md).
#
#   worktree.sh create <dir>   # a detached worktree at a snapshot of the current state
#   worktree.sh patch <dir>    # print the copy's change against that snapshot as a binary patch
#   worktree.sh remove <dir>   # remove the worktree
#
# <dir> must be outside the repository. The snapshot holds every tracked and untracked (not ignored)
# file as it is now, including uncommitted work; it is built in a temporary index, so your files,
# index, and branches stay unchanged. The only other writes are git's worktree records and objects.
# Apply a patch in the main checkout with `git apply --binary <file>`.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
top=$(pwd -P)

usage() {
  echo "usage: worktree.sh create <dir> | patch <dir> | remove <dir>" >&2
  exit 2
}

[ $# -eq 2 ] || usage
mode=$1 dir=$2
case "$dir" in /*) ;; *) dir="$PWD/$dir" ;; esac
reject() { echo "ERROR=$*" >&2; exit 2; }
# Canonicalise the full target, not just its parent. Refuse a final symlink even
# when it leads to an owned checkout: callers must use the recorded physical path.
[ ! -L "${dir%/}" ] || reject "the checkout path must not be a symlink"
if [ -d "$dir" ]; then
  dir=$(cd "$dir" && pwd -P)
else
  parent=$(cd "$(dirname "$dir")" 2> /dev/null && pwd -P) || reject "the parent folder must exist"
  dir=$parent/$(basename "$dir")
fi
case "$dir/" in
  "$top/"*) reject "the worktree folder must be outside the repository" ;;
esac
owner=$(cd "$(git rev-parse --absolute-git-dir)" && pwd -P)
common=$(cd "$(git rev-parse --git-common-dir)" && pwd -P)

owned_checkout() {
  [ -d "$dir" ] || reject "no private checkout at $dir"
  checkout_top=$(git -C "$dir" rev-parse --show-toplevel 2> /dev/null) || reject "not a checkout"
  [ "$(cd "$checkout_top" && pwd -P)" = "$dir" ] || reject "not a checkout root"
  checkout_git=$(git -C "$dir" rev-parse --absolute-git-dir)
  checkout_git=$(cd "$checkout_git" && pwd -P)
  case "$checkout_git" in "$common/worktrees/"*) ;; *) reject "not a linked checkout in this repository" ;; esac
  marker=$checkout_git/cobb-checkout
  [ -f "$marker" ] || reject "worktree was not created by this helper"
  [ "$(sed -n '1p' "$marker")" = "$owner" ] || reject "worktree belongs to another checkout"
  [ "$(sed -n '2p' "$marker")" = "$dir" ] || reject "checkout path changed"
  snapshot=$(sed -n '3p' "$marker")
  [ "$(git -C "$dir" rev-parse HEAD)" = "$snapshot" ] || reject "checkout HEAD changed; preserve and inspect its commits"
  [ -z "$(git -C "$dir" branch --show-current)" ] || reject "checkout is no longer detached"
}

case $mode in
  create)
    [ ! -e "$dir" ] || { echo "ERROR=$dir already exists" >&2; exit 2; }
    index=$(mktemp)
    trap 'rm -f "$index"' EXIT
    real_index=$(git rev-parse --git-path index)
    if [ -f "$real_index" ]; then cp "$real_index" "$index"; else rm -f "$index"; fi
    GIT_INDEX_FILE=$index git add -A
    tree=$(GIT_INDEX_FILE=$index git write-tree)
    rm -f "$index"
    snapshot=$(git commit-tree "$tree" -p HEAD -m "cobb isolated snapshot")
    git worktree add --quiet --detach "$dir" "$snapshot"
    checkout_git=$(git -C "$dir" rev-parse --absolute-git-dir)
    printf '%s\n' "$owner" "$dir" "$snapshot" > "$checkout_git/cobb-checkout"
    echo "WORKTREE=$dir"
    echo "SNAPSHOT=$snapshot"
    ;;
  patch)
    owned_checkout
    git -C "$dir" add -A
    git -C "$dir" diff --cached --binary HEAD
    ;;
  remove)
    owned_checkout
    git worktree remove --force "$dir"
    echo "REMOVED=$dir"
    ;;
  *) usage ;;
esac
