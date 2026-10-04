#!/usr/bin/env bash
# Run the cobb eval scenarios against one version of the skill, with bounded concurrency.
#
#   evals/run.sh --list
#   evals/run.sh <label> [git-ref] [--only '<scenarios>'] [--agent '<choice>']
#
# With a git ref (for example HEAD), the skill comes from that commit. Without one, it comes
# from the working tree. Results go to $EVAL_OUT/<label>, outside the repo, so this repo's
# AGENTS.md cannot leak into the runs.
#
# Choose the harness, provider, model, and effort in one phrase before a live run.
# There is no default harness. Pi, Claude Code, and Codex CLI have adapters; custom adapters use
# the same copied-skill and JSON result contract.
#
# Environment:
#   EVAL_OUT      results root (default: $TMPDIR/cobb-evals)
#   EVAL_ONLY     space-separated scenario names to run (default: all)
#   EVAL_AGENT    e.g. 'pi glm5.3flash max', 'claude opus5.5 medium', 'codex gpt6.1sol high'
#   EVAL_HARNESS  advanced: pi, claude, codex, or an adapter executable path (no default)
#   EVAL_PROVIDER advanced: provider ID for Pi (codex is also accepted)
#   EVAL_MODEL    model chosen for the run, or default to use the harness setting (no default)
#   EVAL_EFFORT   effort chosen for the run, or default to use the harness setting (no default)
#   EVAL_JOBS     maximum concurrent scenarios (default: 1)
#   EVAL_APPROVE=1  explicit approval for a non-interactive live run
#   EVAL_TIMEOUT  seconds before one run is stopped (default: 1800)
#   EVAL_DRY=1    build the fixtures and run the checks without an agent
#   EVAL_RECHECK=1  rerun only the checks on <label>'s saved repos and replies (after you fix a check)
set -euo pipefail

EVALS_DIR=$(cd "$(dirname "$0")" && pwd)
if [ "${COBB_EVAL_SUPERVISED:-}" != 1 ]; then
  exec python3 "$EVALS_DIR/process.py" "$0" "$@"
fi
unset COBB_EVAL_SUPERVISED
REPO_DIR=$(cd "$EVALS_DIR/.." && pwd)
if [ "${1:-}" = --list ]; then
  [ $# -eq 1 ] || { echo "ERROR: --list must be used alone" >&2; exit 2; }
  for file in "$EVALS_DIR"/scenarios/*.sh; do basename "$file" .sh; done
  exit 0
fi
LABEL=${1:?usage: evals/run.sh <label> [git-ref] [--only '<scenarios>'] [--agent '<choice>']}
shift
REF=""
only_seen=0
while [ $# -gt 0 ]; do
  case "$1" in
    --only)
      [ $# -ge 2 ] && [ -n "$2" ] || { echo "ERROR: --only needs scenarios" >&2; exit 2; }
      [ "$only_seen" = 0 ] && [ -z "${EVAL_ONLY:-}" ] || { echo "ERROR: use --only or EVAL_ONLY once, not both" >&2; exit 2; }
      EVAL_ONLY=$2; only_seen=1; shift 2 ;;
    --agent) [ $# -ge 2 ] || { echo "ERROR: --agent needs a choice" >&2; exit 2; }; EVAL_AGENT=$2; shift 2 ;;
    --*) echo "ERROR: unknown option: $1" >&2; exit 2 ;;
    *) [ -z "$REF" ] || { echo "ERROR: only one git ref is allowed" >&2; exit 2; }; REF=$1; shift ;;
  esac
done
case "$LABEL" in
  *[!a-zA-Z0-9-]*|'') echo "ERROR: label must contain only letters, digits, and hyphens" >&2; exit 2 ;;
esac
OUT=$(python3 - "$REPO_DIR" "${EVAL_OUT:-${TMPDIR:-/tmp}/cobb-evals}" "$LABEL" <<'PY'
from pathlib import Path
import sys
repo, root = (Path(p).resolve() for p in sys.argv[1:3])
out = root / sys.argv[3]
if root == repo or repo in root.parents:
    sys.exit("ERROR: EVAL_OUT must be outside the repository")
if out.is_symlink():
    sys.exit("ERROR: the output path must not be a symlink")
print(out)
PY
)
for name in ${EVAL_ONLY:-}; do
  case "$name" in *[!a-zA-Z0-9-]*) echo "ERROR: invalid scenario: $name" >&2; exit 2 ;; esac
  [ -f "$EVALS_DIR/scenarios/$name.sh" ] || { echo "ERROR: unknown scenario: $name" >&2; exit 2; }
done
files=()
names=()
for file in "$EVALS_DIR"/scenarios/*.sh; do
  name=$(basename "$file" .sh)
  if [ -n "${EVAL_ONLY:-}" ] && [[ " $EVAL_ONLY " != *" $name "* ]]; then continue; fi
  files+=("$file")
  names+=("$name")
done
[ "${#files[@]}" -gt 0 ] || { echo "ERROR: selection contains no scenarios" >&2; exit 2; }
SELECTED="${names[*]}"
TIMEOUT=${EVAL_TIMEOUT:-1800}
JOBS=${EVAL_JOBS:-1}
for value in "$TIMEOUT" "$JOBS"; do
  case "$value" in *[!0-9]*|''|0|0*) echo "ERROR: EVAL_TIMEOUT and EVAL_JOBS must be positive integers" >&2; exit 2 ;; esac
done
export EVALS_DIR

if [ "${EVAL_RECHECK:-}" = 1 ]; then
  [ -d "$OUT" ] || { echo "ERROR: no saved run at $OUT" >&2; exit 2; }
  for file in "${files[@]}"; do
    name=$(basename "$file" .sh)
    [ -d "$OUT/$name/repo" ] || continue
    (
      source "$EVALS_DIR/lib.sh"
      source "$EVALS_DIR/fixtures.sh"
      FOLLOW_UPS=()
      source "$file"
      cd "$OUT/$name/repo"
      export BEFORE=$OUT/$name/before.txt REPLY=$OUT/$name/reply.md
      checks > "$OUT/$name/checks.txt"
    )
  done
  if [ -n "${EVAL_ONLY:-}" ]; then
    python3 "$EVALS_DIR/report.py" "$OUT" --only "$SELECTED"
  else
    python3 "$EVALS_DIR/report.py" "$OUT"
  fi
  exit
fi

if [ "${EVAL_DRY:-}" != 1 ]; then
  if [ -z "${EVAL_AGENT:-}" ] && { [ -z "${EVAL_HARNESS:-}" ] || [ -z "${EVAL_MODEL:-}" ] || [ -z "${EVAL_EFFORT:-}" ]; }; then
    [ "${COBB_EVAL_TTY:-0}" = 1 ] || { echo "ERROR: choose an agent explicitly with --agent or EVAL_AGENT; there is no default harness" >&2; exit 2; }
    printf 'Agent choice (for example pi glm5.3flash max): ' >&2
    read -r EVAL_AGENT || exit 2
    [ -n "$EVAL_AGENT" ] || { echo "ERROR: an agent choice is required; there is no default harness" >&2; exit 2; }
  fi
  if [ -n "${EVAL_AGENT:-}" ]; then
    [ -z "${EVAL_HARNESS:-}${EVAL_PROVIDER:-}${EVAL_MODEL:-}${EVAL_EFFORT:-}" ] || { echo "ERROR: use an agent phrase or separate settings, not both" >&2; exit 2; }
    resolved=$(python3 "$EVALS_DIR/settings.py" "$EVAL_AGENT") || exit 2
    while IFS='=' read -r key value; do printf -v "$key" '%s' "$value"; done <<< "$resolved"
  fi
  case "$EVAL_HARNESS" in
    pi)
      if [ -z "${EVAL_PROVIDER:-}" ]; then
        resolved=$(python3 "$EVALS_DIR/settings.py" --pi-model "$EVAL_MODEL") || exit 2
        while IFS='=' read -r key value; do printf -v "$key" '%s' "$value"; done <<< "$resolved"
      fi
      if [ "$EVAL_PROVIDER" = codex ]; then EVAL_PROVIDER=openai-codex; fi
      ADAPTER=$EVALS_DIR/harnesses/pi.py ;;
    claude) ADAPTER=$EVALS_DIR/harnesses/claude.sh ;;
    codex) ADAPTER=$EVALS_DIR/harnesses/codex.py ;;
    *) ADAPTER=$(python3 - "$EVAL_HARNESS" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).resolve())
PY
) ;;
  esac
  [ -f "$ADAPTER" ] && [ -x "$ADAPTER" ] || { echo "ERROR: adapter must be an executable file" >&2; exit 2; }
  case "$EVAL_HARNESS" in pi|claude|codex) command -v "$EVAL_HARNESS" > /dev/null || { echo "ERROR: $EVAL_HARNESS is not installed" >&2; exit 2; } ;; esac
  printf 'Live eval plan\nHarness: %s\nProvider: %s\nModel: %s\nEffort: %s\nConcurrent scenarios: %s\nScenarios: %s\nSkill: %s\nResults: %s\n' \
    "$EVAL_HARNESS" "${EVAL_PROVIDER:-harness-managed}" "$EVAL_MODEL" "$EVAL_EFFORT" "$JOBS" "$SELECTED" "${REF:-working copy}" "$OUT"
  if [ "$EVAL_HARNESS" = pi ]; then
    echo 'Safety: Pi tools are not sandboxed. Use a restricted environment; a temporary working folder is not a security boundary.'
  fi
  if [ "${EVAL_APPROVE:-}" != 1 ]; then
    [ "${COBB_EVAL_TTY:-0}" = 1 ] || { echo "ERROR: live evals require explicit approval; set EVAL_APPROVE=1 only for an approved plan" >&2; exit 2; }
    printf '\n0 — Recommended: Run this plan — settings are explicit and concurrency is bounded\n1 — Stop without calling an agent\n'
    read -r choice || exit 2
    case "$choice" in 0|default) ;; 1) exit 0 ;; *) echo "ERROR: choose 0 or 1" >&2; exit 2 ;; esac
  fi
  export EVAL_PROVIDER=${EVAL_PROVIDER:-}
  export EVAL_MODEL EVAL_EFFORT
fi

# Never delete a prior run. Atomic mkdir also refuses an existing output symlink.
mkdir -p "$(dirname "$OUT")"
mkdir "$OUT" || { echo "ERROR: choose a new label; $OUT already exists or cannot be created" >&2; exit 2; }
mkdir -p "$OUT/skills"
if [ -n "$REF" ]; then
  git -C "$REPO_DIR" archive "$REF" skills/cobb | tar -x -C "$OUT"
else
  cp -R "$REPO_DIR/skills/cobb" "$OUT/skills/"
fi

export EVAL_SKILL_DIR=$OUT/skills/cobb
if [ "${EVAL_DRY:-}" != 1 ]; then
  python3 - "$OUT/run.json" "${EVAL_AGENT:-}" "$EVAL_HARNESS" "$ADAPTER" "$EVAL_PROVIDER" "$EVAL_MODEL" "$EVAL_EFFORT" "$JOBS" "$TIMEOUT" "${REF:-working copy}" "${EVAL_ONLY:-all}" "$SELECTED" <<'PY'
import json
import sys
path, choice, harness, adapter, provider, model, effort, jobs, timeout, skill, scenarios, selected = sys.argv[1:]
with open(path, 'w') as f:
    json.dump(dict(choice=choice, harness=harness, adapter=adapter, provider=provider,
                   model=model, effort=effort, jobs=int(jobs), timeout=int(timeout),
                   skill=skill, scenarios=scenarios, selected_scenarios=selected.split()), f, indent=2)
PY
fi

run_agent() {  # run_agent <out-json> <prompt> [session-id]: one adapter call in the fixture repo
  local out=$1 prompt=$2 session=${3:-} code=0
  export EVAL_KEEP_SESSION=0
  if [ "${#FOLLOW_UPS[@]}" -ne 0 ]; then export EVAL_KEEP_SESSION=1; fi
  # Normalise only the command prefix, not paths or quoted commands inside the prompt.
  case "$prompt" in '/cobbtest:cobb'|'/cobbtest:cobb '*) prompt="/cobb${prompt#/cobbtest:cobb}" ;; esac
  perl -e 'alarm shift @ARGV; exec @ARGV' "$TIMEOUT" "$ADAPTER" "$prompt" "$session" \
    < /dev/null > "$out" 2>> "$dir/stderr.txt" || code=$?
  if [ "$code" -ne 0 ]; then
    echo "agent exited with $code" >> "$dir/stderr.txt"
    return "$code"
  fi
  python3 - "$out" 2>> "$dir/stderr.txt" <<'PY'
import json
import os
import sys
try:
    data = json.load(open(sys.argv[1]))
    if not isinstance(data, dict) or not isinstance(data.get('result'), str):
        raise ValueError('adapter must return a JSON object with a string result')
    if data.get('is_error'):
        raise ValueError('adapter reported an agent error')
    if os.environ['EVAL_KEEP_SESSION'] == '1':
        session = data.get('session_id')
        if not isinstance(session, str) or not session.strip():
            raise ValueError('adapter must return a non-empty string session_id for follow-up')
except (OSError, ValueError) as error:
    sys.exit(f'ERROR: {error}')
PY
}

# Keep progress out of adapter JSON and each scenario's diagnostic log.
exec 3>&2
progress() { printf '[%s] %s\n' "$name" "$*" >&3; }
timer() { python3 "$EVALS_DIR/timing.py" "$dir" "$@"; }

run_timed_agent() {
  local code=0
  timer call-start "$turn"
  progress "AGENT turn $turn"
  if run_agent "$@"; then code=0; else code=$?; fi
  timer call-end "$code"
  progress "AGENT turn $turn ended (exit $code)"
  return "$code"
}

run_one() {  # one sequential task, including follow-ups, in its own fixture
  local file=$1 name dir status=scenario_error turn=1 duration mode=live
  name=$(basename "$file" .sh)
  dir=$OUT/$name
  mkdir -p "$dir/repo"
  if [ "${EVAL_DRY:-}" = 1 ]; then mode=dry; fi
  progress START
  timer start "$mode"
  finish_case() {
    local code=$?
    trap - EXIT
    if [ "$status" = scenario_error ]; then
      echo 'FAIL  scenario crashed (see log.txt)' >> "$dir/checks.txt"
    fi
    duration=$(timer finish "$status") || duration='timing unavailable'
    case "$status" in
      passed) progress "PASSED ($duration)" ;;
      checks_failed) progress "FAILED checks ($duration)" ;;
      *) progress "ERROR $status ($duration)" ;;
    esac
    exit "$code"
  }
  trap finish_case EXIT
  source "$EVALS_DIR/lib.sh"
  source "$EVALS_DIR/fixtures.sh"
  FOLLOW_UPS=()
  source "$file"
  cd "$dir/repo"
  setup
  timer setup-end
  progress 'SETUP complete'
  snapshot > "$dir/before.txt"
  if [ "$mode" = dry ]; then
    echo '{"result": ""}' > "$dir/out.json"
  else
    if ! run_timed_agent "$dir/out.json" "$PROMPT"; then
      status=agent_error
      echo 'FAIL  agent run failed (see out.json and stderr.txt)' > "$dir/checks.txt"
      exit 1
    fi
    for reply in ${FOLLOW_UPS[@]+"${FOLLOW_UPS[@]}"}; do
      session=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1])).get("session_id", ""))' "$dir/out.json")
      mv "$dir/out.json" "$dir/out-turn$turn.json"
      turn=$((turn + 1))
      if ! run_timed_agent "$dir/out.json" "$reply" "$session"; then
        status=agent_error
        echo 'FAIL  agent follow-up failed (see out.json and stderr.txt)' > "$dir/checks.txt"
        exit 1
      fi
    done
  fi
  python3 -c 'import json, sys; print(json.load(open(sys.argv[1])).get("result") or "")' \
    "$dir/out.json" > "$dir/reply.md" 2> /dev/null || : > "$dir/reply.md"
  export BEFORE=$dir/before.txt REPLY=$dir/reply.md
  timer checks-start
  progress CHECKS
  checks > "$dir/checks.txt"
  status=passed
  if ! grep -q '^PASS  ' "$dir/checks.txt" || grep -q '^FAIL  ' "$dir/checks.txt"; then status=checks_failed; fi
  exit 0  # Keep task-local state available to its EXIT trap.
}

pids=()
active_names=()
starts=()
next=0
last_heartbeat=$SECONDS
while [ "$next" -lt "${#files[@]}" ] || [ "${#pids[@]}" -gt 0 ]; do
  # Reap every completed child, not just the oldest child in a batch.
  kept_pids=(); kept_names=(); kept_starts=()
  for ((i=0; i<${#pids[@]}; i++)); do
    if kill -0 "${pids[$i]}" 2> /dev/null; then
      kept_pids+=("${pids[$i]}"); kept_names+=("${active_names[$i]}"); kept_starts+=("${starts[$i]}")
    else
      if ! wait "${pids[$i]}"; then
        dir=$OUT/${active_names[$i]}
        if ! grep -q '^FAIL  ' "$dir/checks.txt" 2> /dev/null; then
          printf 'FAIL  scenario worker exited unexpectedly\n' >> "$dir/checks.txt"
        fi
      fi
    fi
  done
  pids=(${kept_pids[@]+"${kept_pids[@]}"})
  active_names=(${kept_names[@]+"${kept_names[@]}"})
  starts=(${kept_starts[@]+"${kept_starts[@]}"})
  while [ "$next" -lt "${#files[@]}" ] && [ "${#pids[@]}" -lt "$JOBS" ]; do
    mkdir -p "$OUT/${names[$next]}"
    run_one "${files[$next]}" > "$OUT/${names[$next]}/log.txt" 2>&1 &
    pids+=("$!"); active_names+=("${names[$next]}"); starts+=("$SECONDS")
    next=$((next + 1))
  done
  if [ "$((SECONDS - last_heartbeat))" -ge 15 ]; then
    for ((i=0; i<${#pids[@]}; i++)); do
      printf '[%s] RUNNING (%ss elapsed)\n' "${active_names[$i]}" "$((SECONDS - starts[$i]))" >&3
    done
    last_heartbeat=$SECONDS
  fi
  if [ "${#pids[@]}" -gt 0 ]; then sleep 0.05; fi
done
python3 "$EVALS_DIR/report.py" "$OUT" --only "$SELECTED"
