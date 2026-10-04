#!/usr/bin/env python3
"""Run Codex CLI and convert its JSONL events to the eval result contract."""
import json
import os
from pathlib import Path
import sys
import time
sys.dont_write_bytecode = True
from _jsonl import agent, events

if len(sys.argv) != 3:
    sys.exit("usage: codex.py <prompt> <session-id-or-empty>")
prompt, session = sys.argv[1:]
effort = os.environ["EVAL_EFFORT"]
if effort not in ("default", "none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"):
    sys.exit(f"ERROR: unsupported Codex effort: {effort}")
if prompt == "/cobb" or prompt.startswith("/cobb "):
    skill = Path(os.environ["EVAL_SKILL_DIR"]) / "SKILL.md"
    prompt = (f"Read the eval skill at {json.dumps(str(skill))} and follow it for the command below. "
              "Resolve its relative scripts and references from that skill directory. "
              "Use this copied skill, not an installed skill.\n\n" + prompt)
# Keep saved auth and configured policy. Never bypass sandbox, approval, or rule checks.
args = ["codex", "--no-daemon", "exec"]
if session:
    args += ["resume"]
args += ["--json", "-c", 'sandbox_mode="workspace-write"']
if os.environ.get("EVAL_PROVIDER"):
    args += ["-c", "model_provider=" + json.dumps(os.environ["EVAL_PROVIDER"])]
if os.environ["EVAL_MODEL"] != "default":
    args += ["--model", os.environ["EVAL_MODEL"]]
if effort != "default":
    args += ["-c", "model_reasoning_effort=" + json.dumps(effort)]
if os.environ["EVAL_KEEP_SESSION"] == "0":
    args += ["--ephemeral"]
args += ["--"]
if session:
    args += [session]
args += [prompt]
started = time.monotonic()
result = None
completed = False
error = ""
turns = 0
usage = {}
try:
    with agent(args) as child:
        for event in events(child):
            kind = event.get("type")
            if kind == "thread.started":
                session = event.get("thread_id", "")
            elif kind == "item.completed" and event.get("item", {}).get("type") == "agent_message":
                result = event["item"]["text"]
            elif kind == "turn.completed":
                completed = True
                turns += 1
                usage = event.get("usage", {})
            elif kind in ("error", "turn.failed"):
                error = event.get("message") or event.get("error", {}).get("message") or "Codex turn failed"
        code = child.wait()
    failed = code != 0 or bool(error) or not completed or not isinstance(result, str)
    print(json.dumps(dict(result=error or result or "", session_id=session, is_error=failed,
                          usage=usage, num_turns=turns,
                          duration_ms=round((time.monotonic() - started) * 1000))))
    sys.exit(1 if failed else 0)
except (OSError, ValueError, TypeError, KeyError) as error:
    sys.exit(f"ERROR: Codex adapter failed: {error}")
