#!/usr/bin/env bash
# Claude Code adapter for evals/run.sh. Other adapters use the same contract:
#   adapter <prompt> <session-id-or-empty>
# cwd is the fixture repo. EVAL_SKILL_DIR, EVAL_MODEL, EVAL_EFFORT, and
# EVAL_KEEP_SESSION (0 or 1) are provided. Print one JSON object with result and,
# when follow-ups are needed, session_id. Optional cost/turn/duration fields feed report.py.
set -euo pipefail

[ $# -eq 2 ] || { echo "usage: claude.sh <prompt> <session-id-or-empty>" >&2; exit 2; }
case "$EVAL_EFFORT" in
  default|low|medium|high|xhigh|max) ;;
  *) echo "ERROR: unsupported Claude effort: $EVAL_EFFORT" >&2; exit 2 ;;
esac
prompt=$1
case "$prompt" in '/cobb'|'/cobb '*) prompt="/cobbtest:cobb${prompt#/cobb}" ;; esac
session=$2
# Keep harness-specific files beside this fixture, outside its tracked working tree.
plugin=$(cd .. && pwd)/claude-plugin
mkdir -p "$plugin/.claude-plugin" "$plugin/skills"
printf '%s\n' '{"name":"cobbtest","version":"0.0.0","description":"cobb under evaluation"}' > "$plugin/.claude-plugin/plugin.json"
cp -R "$EVAL_SKILL_DIR" "$plugin/skills/"
args=(-p "$prompt" --plugin-dir "$plugin" --add-dir "$plugin"
  --output-format json --strict-mcp-config --setting-sources project,local
  --permission-mode acceptEdits
  --settings '{"sandbox":{"enabled":true,"autoAllowBashIfSandboxed":true}}')
if [ "$EVAL_MODEL" != default ]; then args+=(--model "$EVAL_MODEL"); fi
if [ "$EVAL_EFFORT" != default ]; then args+=(--effort "$EVAL_EFFORT"); fi
if [ -n "$session" ]; then args+=(--resume "$session"); fi
if [ "$EVAL_KEEP_SESSION" = 0 ]; then args+=(--no-session-persistence); fi
exec env -u CLAUDECODE claude "${args[@]}"
