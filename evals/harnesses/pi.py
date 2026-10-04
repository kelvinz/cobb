#!/usr/bin/env python3
"""Run the selected Pi configuration and convert JSONL events to the eval result contract."""
import json
import os
from pathlib import Path
import sys
import time
sys.dont_write_bytecode = True
from _jsonl import agent, events

if len(sys.argv) != 3:
    sys.exit("usage: pi.py <prompt> <session-id-or-empty>")
if not os.environ.get("EVAL_PROVIDER"):
    sys.exit("ERROR: Pi requires an explicit provider")
prompt, session = sys.argv[1:]
if prompt == "/cobb" or prompt.startswith("/cobb "):
    prompt = "/skill:cobb" + prompt[len("/cobb"):]
args = ["pi", "--mode", "json", "--print", "--offline", "--no-extensions", "--no-skills",
        "--no-prompt-templates", "--no-themes", "--no-approve", "--tools", "read,bash,edit,write",
        "--skill", os.environ["EVAL_SKILL_DIR"]]
# The explicit skill still reads fixture instructions; skip unrelated startup context.
args += ["--no-context-files"]
args += ["--provider", os.environ["EVAL_PROVIDER"]]
for setting, flag in [("EVAL_MODEL", "--model"), ("EVAL_EFFORT", "--thinking")]:
    value = os.environ.get(setting, "")
    if value and value != "default":
        args += [flag, value]
if os.environ["EVAL_KEEP_SESSION"] == "1":
    session = session or str(Path.cwd().parent / "pi-session.jsonl")
    args += ["--session", session]
else:
    args += ["--no-session"]
args += ["--", prompt]
started = time.monotonic()
final = None
settled = False
turns = 0
cost = 0.0
try:
    with agent(args) as child:
        for event in events(child):
            if event.get("type") == "message_end":
                message = event.get("message", {})
                if message.get("role") == "assistant":
                    final = message
                    turns += 1
                cost += message.get("usage", {}).get("cost", {}).get("total", 0.0)
            elif event.get("type") == "agent_settled":
                settled = True
        code = child.wait()
    result = "" if final is None else "".join(block.get("text", "") for block in final.get("content", []) if block.get("type") == "text")
    failed = code != 0 or not settled or final is None or final.get("stopReason") != "stop"
    if failed and final and final.get("errorMessage"):
        result = final["errorMessage"]
    print(json.dumps(dict(result=result, session_id=session, is_error=failed,
                          total_cost_usd=cost, num_turns=turns,
                          duration_ms=round((time.monotonic() - started) * 1000))))
    sys.exit(1 if failed else 0)
except (OSError, ValueError, TypeError) as error:
    sys.exit(f"ERROR: Pi adapter failed: {error}")
