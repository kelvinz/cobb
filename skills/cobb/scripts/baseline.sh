#!/usr/bin/env bash
# Save/compare diagnose's branch, HEAD, index, diffs, and file fingerprints.
# baseline.sh save <dir> | compare <dir>
# <dir> must be outside the repository. This is a comparison record, not a backup:
# untracked contents and ignored files are not saved. See diagnose.md Starting State.
set -euo pipefail
umask 077
cd "$(git rev-parse --show-toplevel)"
top=$(pwd -P)

usage() {
  echo "usage: baseline.sh save <dir> | compare <dir>" >&2
  exit 2
}

[ $# -eq 2 ] || usage
mode=$1 dir=$2
case $mode in save|compare) ;; *) usage ;; esac
# Resolve before creating anything, including when an existing parent is a symlink.
if [ -d "$dir" ]; then
  dir=$(cd "$dir" && pwd -P)
else
  parent=$(cd "$(dirname "$dir")" && pwd -P) || exit 2
  dir=$parent/$(basename "$dir")
fi
case "$dir/" in
  "$top/"*) echo "ERROR=the baseline folder must be outside the repository" >&2; exit 2 ;;
esac
case $mode in
  save) mkdir -p "$dir" ;;
  compare) [ -f "$dir/state.txt" ] || { echo "ERROR=no saved baseline in $dir" >&2; exit 2; } ;;
esac

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

state() {
  local f name hash branch head
  branch=$(git branch --show-current)
  head=$(git rev-parse HEAD)
  echo "branch $branch"
  echo "head $head"
  hash=$(git ls-files --stage -z | git hash-object --stdin)
  echo "index $hash"
  hash=$(git diff --cached --binary | git hash-object --stdin)
  echo "staged-diff $hash"
  hash=$(git diff --binary | git hash-object --stdin)
  echo "unstaged-diff $hash"
  git ls-files --others --exclude-standard -z > "$scratch/untracked"
  while IFS= read -r -d '' f; do printf 'untracked %q\n' "$f"; done < "$scratch/untracked"
  git ls-files -co --exclude-standard -z > "$scratch/paths"
  while IFS= read -r -d '' f; do
    printf -v name '%q' "$f"
    if [ -L "$f" ]; then
      hash=$(readlink "./$f" | git hash-object --stdin)
      echo "file $name symlink $hash"
    elif [ -f "$f" ]; then
      hash=$(git hash-object --no-filters -- "$f")
      if [ -x "$f" ]; then echo "file $name exec $hash"; else echo "file $name plain $hash"; fi
    elif [ ! -e "$f" ]; then
      echo "file $name missing"
    else
      echo "file $name directory-or-special"
    fi
  done < "$scratch/paths"
}

# Run state directly so a failed Git read cannot be hidden by process substitution.
state > "$scratch/state.txt"
if [ "$mode" = save ]; then
  cp "$scratch/state.txt" "$dir/state.txt"
  git diff --cached --binary > "$dir/staged.patch"
  git diff --binary > "$dir/unstaged.patch"
  echo "SAVED=$dir"
else
  if diff "$scratch/state.txt" "$dir/state.txt" > "$scratch/differences"; then
    echo SAME
  else
    sed -n -e 's/^< /CHANGED now: /p' -e 's/^> /CHANGED was: /p' "$scratch/differences"
    exit 1
  fi
fi
