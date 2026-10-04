#!/usr/bin/env bash
# Deterministic tests for skills/cobb/scripts. Each case builds a throwaway git repo and checks one
# rule from the skill's text: the expected facts, the PASS or FAIL lines, and the exit code.
#
#   bash tests/scripts.sh
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
S=${COBB_SCRIPTS:-$ROOT/skills/cobb/scripts}  # COBB_SCRIPTS lets a fault check test a modified copy
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1  # keep the user's git config out of the tests
passed=0 failed=0

check() {  # check <label> <expected-exit> <expected-output-regex> <command...>
  local label=$1 want=$2 pattern=$3 out code=0
  shift 3
  out=$("$@" 2>&1) || code=$?
  if [ "$code" = "$want" ] && printf '%s\n' "$out" | grep -Eq -- "$pattern"; then
    echo "ok    $label"
    passed=$((passed + 1))
  else
    echo "FAIL  $label (exit $code, expected $want)"
    printf '%s\n' "$out" | sed 's/^/        /'
    failed=$((failed + 1))
  fi
}

new_repo() {  # new_repo <name>: a repo with one commit on main; cd into it
  mkdir -p "$T/$1"
  cd "$T/$1"
  git init -q -b main
  git config user.name test
  git config user.email test@example.invalid
  echo one > file.txt
  git add file.txt
  git commit -q -m one
}

add_remote() {  # add_remote <remote> <branch>...: a bare remote with the branches pushed; its HEAD is the first branch
  local name=$1 bare
  shift
  bare=$T/$name-$(basename "$PWD").git
  git init -q --bare "$bare"
  git --git-dir="$bare" symbolic-ref HEAD "refs/heads/$1"
  git remote add "$name" "$bare"
  git push -q "$name" "$@"
  git remote set-head "$name" "$1" > /dev/null
}

commit() {  # commit <message>: append a line to file.txt and commit it
  echo "$1" >> file.txt
  git commit -q -am "$1"
}

echo "repo-default.sh"
new_repo rd1
check "a declared default wins" 0 "SOURCE=repo-convention" bash "$S/repo-default.sh" --declared develop
add_remote origin main
check "one remote HEAD gives the default" 0 "DEFAULT_REF=origin/main" bash "$S/repo-default.sh"
git branch -q develop
add_remote upstream develop
check "remote HEADs that disagree are unclear" 1 "UNCLEAR=remote HEADs disagree" bash "$S/repo-default.sh"
new_repo rd2
add_remote origin main
add_remote upstream main
check "remote HEADs that agree give the default" 0 "SOURCE=remote-head" bash "$S/repo-default.sh"
new_repo rd3
check "no remote: the one local base branch" 0 "SOURCE=local-fallback" bash "$S/repo-default.sh"
git branch -q develop
check "no remote: several local base branches are unclear" 1 "UNCLEAR=.*several local base branches" bash "$S/repo-default.sh"
new_repo rd4
git branch -q -m main work
check "no remote and no base branch is unclear" 1 "UNCLEAR=.*no local base branch" bash "$S/repo-default.sh"
git branch -q release
check "--base adds a base branch" 0 "DEFAULT_BRANCH=release" bash "$S/repo-default.sh" --base release

echo "review-pin.sh"
new_repo rp1
add_remote origin main
git switch -q -c feat/x
commit two
git push -q -u origin feat/x
commit three
check "the upstream is the base" 0 "BASE_SOURCE=upstream" bash "$S/review-pin.sh" pin
check "an explicit argument wins" 0 "BASE_SOURCE=argument" bash "$S/review-pin.sh" pin --arg main
check "a finalise target comes next" 0 "BASE_SOURCE=finalise-target" bash "$S/review-pin.sh" pin --target main
check "a feature branch is classified as feature" 0 "BRANCH_KIND=feature" bash "$S/review-pin.sh" pin
git switch -q -c feat/y main
commit four
check "no upstream: the remote HEAD default" 0 "BASE_REF=origin/main" bash "$S/review-pin.sh" pin
git branch -q develop main
check "no upstream: a declared default" 0 "BASE_SOURCE=repo-convention" bash "$S/review-pin.sh" pin --declared develop
check "a base that does not resolve is an error" 1 "ERROR=the base ref does not resolve" bash "$S/review-pin.sh" pin --declared nosuch
git switch -q main
start=$(git rev-parse HEAD)
check "base branch without upstream: the session start" 0 "BASE_SOURCE=session-start" bash "$S/review-pin.sh" pin --session-start "$start"
git branch -q --set-upstream-to=origin/main main
commit five
check "base branch ahead of its upstream: the upstream" 0 "BASE_SOURCE=upstream" bash "$S/review-pin.sh" pin --session-start "$start"
check "a base branch is classified as base" 0 "BRANCH_KIND=base" bash "$S/review-pin.sh" pin --session-start "$start"
check "HEAD equal to the base is an empty range" 0 "RANGE_EMPTY=yes" bash "$S/review-pin.sh" pin --arg HEAD
git switch -q feat/y
check "a base that is not an ancestor is reported" 0 "BASE_IS_ANCESTOR=no" bash "$S/review-pin.sh" pin --arg main
git switch -q --detach HEAD
check "a detached HEAD is an error" 1 "ERROR=HEAD is detached" bash "$S/review-pin.sh" pin
git switch -q feat/y
bash "$S/review-pin.sh" pin --arg origin/main > "$T/review.pin"
check "verify passes when nothing moved" 0 "PASS HEAD unchanged" bash "$S/review-pin.sh" verify "$T/review.pin"
commit six
check "verify fails after a new commit" 1 "FAIL HEAD changed" bash "$S/review-pin.sh" verify "$T/review.pin"
new_repo rp2
git branch -q develop
git switch -q -c feat/z
commit two
check "an unclear default is reported" 1 "UNCLEAR=" bash "$S/review-pin.sh" pin
git switch -q -c release
check "--base marks a base branch" 0 "BRANCH_KIND=base" bash "$S/review-pin.sh" pin --arg main --base release

echo "rewrite-check.sh"
new_repo rw1
add_remote origin main
git switch -q -c feat/a
commit two
commit three
oldest=$(git rev-list --reverse main..HEAD | head -n 1)
check "an unpublished linear range is safe" 0 "^SAFE$" bash "$S/rewrite-check.sh" "$oldest"
check "the range's commits are listed" 0 "^COMMIT [0-9a-f]+ three$" bash "$S/rewrite-check.sh" "$oldest"
git push -q origin feat/a
check "pushed commits are unsafe" 1 "is also on refs/remotes/origin/feat/a" bash "$S/rewrite-check.sh" "$oldest"
git push -q origin --delete feat/a
git branch -q copy
check "a commit on another local branch is unsafe" 1 "is also on refs/heads/copy" bash "$S/rewrite-check.sh" "$oldest"
git branch -q -D copy
git tag v1 HEAD~1
check "a tagged commit is unsafe" 1 "is tagged v1" bash "$S/rewrite-check.sh" "$oldest"
git tag -d v1 > /dev/null
check "the range is safe again after cleanup" 0 "^SAFE$" bash "$S/rewrite-check.sh" "$oldest"
git switch -q -c side main
echo side > side.txt
git add side.txt
git commit -q -m side
git switch -q feat/a
git merge -q --no-edit side
check "a merge commit in the range is unsafe" 1 "FAIL linear: merge commits" bash "$S/rewrite-check.sh" "$oldest"
git switch -q -c elsewhere main
commit elsewhere
elsewhere=$(git rev-parse HEAD)
git switch -q feat/a
check "a commit outside the branch is refused" 1 "is not in the current branch's history" bash "$S/rewrite-check.sh" "$elsewhere"
new_repo rw2
commit two
check "a base branch is unsafe" 1 "FAIL feature branch: main is a base branch" bash "$S/rewrite-check.sh" HEAD
git switch -q -c feat/b
commit three
check "no remotes counts as fetched" 0 "PASS fetch: no remotes" bash "$S/rewrite-check.sh" HEAD
check "--base marks a base branch" 1 "feat/b is a base branch" bash "$S/rewrite-check.sh" HEAD --base feat/b
git remote add broken "$T/missing.git"
check "a failed fetch is unsafe" 1 "FAIL fetch: failed" bash "$S/rewrite-check.sh" HEAD
git remote remove broken
check "a root commit has no parent" 1 "has no parent" bash "$S/rewrite-check.sh" "$(git rev-list --max-parents=0 HEAD)"

echo "hotfix-check.sh"
new_repo hf1
add_remote origin main
git branch -q --set-upstream-to=origin/main main
echo fix > fix.txt
git add fix.txt
check "pin a staged fix" 0 "PASS staged tree: pinned" bash "$S/hotfix-check.sh" pin main
check "pin records the upstream" 0 "UPSTREAM=origin/main@[0-9a-f]+" bash "$S/hotfix-check.sh" pin main
check "pin refuses another branch" 1 "not the default branch develop" bash "$S/hotfix-check.sh" pin develop
bash "$S/hotfix-check.sh" pin main > "$T/hotfix.pin"
check "verify passes when nothing moved" 0 "PASS staged tree unchanged" bash "$S/hotfix-check.sh" verify "$T/hotfix.pin"
echo more >> fix.txt
git add fix.txt
check "verify fails after restaging" 1 "FAIL staged tree changed" bash "$S/hotfix-check.sh" verify "$T/hotfix.pin"
bash "$S/hotfix-check.sh" pin main > "$T/hotfix.pin"
echo dirty >> file.txt
check "an unstaged tracked change fails" 1 "FAIL worktree: unstaged tracked changes" bash "$S/hotfix-check.sh" pin main
check "verify repeats the worktree checks" 1 "FAIL worktree: unstaged tracked changes" bash "$S/hotfix-check.sh" verify "$T/hotfix.pin"
git checkout -q -- file.txt
echo note > notes.txt
check "untracked files are listed for you to judge" 0 "UNTRACKED notes.txt" bash "$S/hotfix-check.sh" pin main
rm notes.txt
git commit -q -m "fix: hotfix"
check "the commit check passes for the reviewed snapshot" 0 "PASS the new commit's tree is the reviewed staged tree" bash "$S/hotfix-check.sh" commit-check "$T/hotfix.pin"
echo hook >> fix.txt
git commit -q -a --amend --no-edit
check "the commit check fails when the commit differs" 1 "FAIL the new commit's tree differs" bash "$S/hotfix-check.sh" commit-check "$T/hotfix.pin"
new_repo hf2
check "nothing staged means no hotfix" 1 "no hotfix to review" bash "$S/hotfix-check.sh" pin main
new_repo hf3
add_remote origin main
git branch -q --set-upstream-to=origin/main main
git clone -q "$T/origin-hf3.git" "$T/hf3-other"
(cd "$T/hf3-other" && git config user.name test && git config user.email test@example.invalid && commit other && git push -q origin main)
echo fix > fix.txt
git add fix.txt
check "a branch behind its upstream fails" 1 "behind or diverged" bash "$S/hotfix-check.sh" pin main
new_repo hf4
git switch -q -c other
echo other > file.txt
git commit -q -am other
git switch -q main
echo main > file.txt
git commit -q -am main
git merge -q other > /dev/null 2>&1 || true
check "a merge in progress fails" 1 "FAIL in progress: MERGE_HEAD" bash "$S/hotfix-check.sh" pin main

echo "baseline.sh"
new_repo bl1
printf 'ignored/\n' > .gitignore
git add .gitignore
git commit -q -m ignore
echo staged > staged.txt
git add staged.txt
echo unstaged >> file.txt
echo untracked > untracked.txt
base=$T/baseline-bl1
check "save outside the repository" 0 "^SAVED=" bash "$S/baseline.sh" save "$base"
check "an unchanged repository compares the same" 0 "^SAME$" bash "$S/baseline.sh" compare "$base"
mkdir -p ignored
echo ignored > ignored/x.txt
check "ignored files do not count" 0 "^SAME$" bash "$S/baseline.sh" compare "$base"
echo more >> file.txt
check "an edited tracked file is a change" 1 "^CHANGED (now|was): " bash "$S/baseline.sh" compare "$base"
printf 'one\nunstaged\n' > file.txt
check "restoring the content compares the same" 0 "^SAME$" bash "$S/baseline.sh" compare "$base"
git add file.txt
check "staging a change is a change" 1 "^CHANGED" bash "$S/baseline.sh" compare "$base"
git reset -q file.txt
check "unstaging it compares the same" 0 "^SAME$" bash "$S/baseline.sh" compare "$base"
echo new > new.txt
check "a new untracked file is a change" 1 "CHANGED now: untracked new.txt" bash "$S/baseline.sh" compare "$base"
rm new.txt
chmod +x untracked.txt
check "a changed executable bit is a change" 1 "CHANGED now: file untracked.txt exec" bash "$S/baseline.sh" compare "$base"
chmod -x untracked.txt
rm staged.txt
check "a deleted file is a change" 1 "CHANGED now: file staged.txt missing" bash "$S/baseline.sh" compare "$base"
echo staged > staged.txt

new_repo bl-paths
for name in $'with\ttab' $'with\nnewline' 'with"quote' 'with\\slash' 'with space'; do
  printf before > "$name"
done
bash "$S/baseline.sh" save "$T/bl-paths-state" > /dev/null
for name in $'with\ttab' $'with\nnewline' 'with"quote' 'with\\slash' 'with space'; do
  printf after > "$name"
  check "detect untracked content change in $(printf %q "$name")" 1 '^CHANGED' bash "$S/baseline.sh" compare "$T/bl-paths-state"
  printf before > "$name"
done
check "restored unusual paths match" 0 '^SAME$' bash "$S/baseline.sh" compare "$T/bl-paths-state"
check "refuse internal baseline before creating it" 2 'outside the repository' bash "$S/baseline.sh" save "$PWD/must-not-exist"
check "refusal leaves no directory" 0 '' test ! -e "$PWD/must-not-exist"

echo "worktree.sh"
new_repo wt1
echo staged > staged.txt
git add staged.txt
echo unstaged >> file.txt
echo untracked > untracked.txt
bash "$S/baseline.sh" save "$T/wt1-before" > /dev/null
work=$T/wt1-copy
check "create a worktree outside the repository" 0 "^SNAPSHOT=[0-9a-f]+" bash "$S/worktree.sh" create "$work"
check "the snapshot holds uncommitted and untracked work" 0 "^untracked$" cat "$work/untracked.txt"
check "the snapshot holds unstaged edits" 0 "^unstaged$" cat "$work/file.txt"
check "creating it leaves your files and index unchanged" 0 "^SAME$" bash "$S/baseline.sh" compare "$T/wt1-before"
echo copy >> "$work/untracked.txt"
echo new > "$work/new.txt"
bash "$S/worktree.sh" patch "$work" > "$T/wt1.patch"
check "the patch holds the private copy's edit" 0 "new.txt" cat "$T/wt1.patch"
check "the patch applies to the main checkout" 0 "" git apply --binary "$T/wt1.patch"
check "the applied change matches the private copy's files" 0 "^new$" cat new.txt
check "remove the worktree" 0 "^REMOVED=" bash "$S/worktree.sh" remove "$work"
check "no extra worktree is left" 0 "^1$" sh -c 'git worktree list | wc -l | tr -d " "'
check "a folder inside the repository is refused" 2 "outside the repository" bash "$S/worktree.sh" create "$PWD/inside"

new_repo wt-safety
printf dirty >> file.txt
bash "$S/baseline.sh" save "$T/wt-safety-before" > /dev/null
ln -s "$PWD" "$T/main-alias"
check "patch refuses a symlink to main" 2 'ERROR=' bash "$S/worktree.sh" patch "$T/main-alias"
check "main index stays unchanged" 0 '^SAME$' bash "$S/baseline.sh" compare "$T/wt-safety-before"
check "patch refuses parent traversal to main" 2 'ERROR=' bash "$S/worktree.sh" patch "$T/wt-safety/../wt-safety"
check "traversal leaves main index unchanged" 0 '^SAME$' bash "$S/baseline.sh" compare "$T/wt-safety-before"
other=$T/unowned-copy
git worktree add --quiet --detach "$other" HEAD
printf user-work > "$other/user.txt"
check "patch refuses an unowned worktree" 2 'ERROR=' bash "$S/worktree.sh" patch "$other"
check "remove refuses an unowned worktree" 2 'ERROR=' bash "$S/worktree.sh" remove "$other"
check "unowned work survives" 0 '' test -f "$other/user.txt"
work=$T/owned-copy
bash "$S/worktree.sh" create "$work" > /dev/null
ln -s "$work" "$T/copy-alias"
check "remove refuses a symlink to an owned copy" 2 'ERROR=' bash "$S/worktree.sh" remove "$T/copy-alias"
check "owned copy survives alias removal" 0 '' test -d "$work"
git -C "$work" -c user.name=test -c user.email=test@example.invalid commit --allow-empty -qm unexpected
check "patch refuses a changed copy HEAD" 2 'ERROR=' bash "$S/worktree.sh" patch "$work"
check "remove preserves unexpected copy commits" 2 'ERROR=' bash "$S/worktree.sh" remove "$work"

echo "repair folding: earlier blocker plus latest suggestion"
new_repo fold-prior
git switch -q -c feat/fold
printf wrong > first.txt
git add first.txt
git commit -qm 'feat: first intent'
first=$(git rev-parse HEAD)
printf undocumented > second.txt
git add second.txt
git commit -qm 'feat: second intent'
check "prior approved range is eligible" 0 '^SAFE$' bash "$S/rewrite-check.sh" "$first"
printf documented > second.txt
git add second.txt
expected=$(git write-tree)
git commit -q --amend --no-edit
check "latest suggestion amend keeps the staged tree" 0 '' test "$(git rev-parse 'HEAD^{tree}')" = "$expected"
printf correct > first.txt
git add first.txt
git commit -q --fixup="$first"
expected=$(git rev-parse 'HEAD^{tree}')
GIT_SEQUENCE_EDITOR=true GIT_EDITOR=true git -c rebase.autoStash=false rebase -q -i --autosquash "$first^"
check "folding preserves the verified final tree" 0 '' test "$(git rev-parse 'HEAD^{tree}')" = "$expected"
check "both original intents remain, without follow-ups" 0 '' test "$(git rev-list --count main..HEAD)" = 2
check "blocker is in the earlier commit" 0 '^correct$' git show HEAD~1:first.txt
check "suggestion is in the later commit" 0 '^documented$' git show HEAD:second.txt
check "earlier commit does not include later intent" 0 '' bash -c '! git cat-file -e HEAD~1:second.txt 2>/dev/null'
check "repaired range stays eligible" 0 '^SAFE$' bash "$S/rewrite-check.sh" HEAD~1
check "repair worktree is clean" 0 '' test -z "$(git status --porcelain)"

echo
echo "$passed passed, $failed failed"
[ "$failed" -eq 0 ]
