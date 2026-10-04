"""Monotonic phase timing for the eval runner; no model content or settings."""
import json
import os
from pathlib import Path
import sys
import time


def atomic_json(path, data):
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    try:
        temporary.write_text(json.dumps(data, indent=2) + "\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def elapsed(start, end):
    return max(0, (end - start) // 1_000_000)


def read_timing(path):
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("unsupported timing schema")
    if data.get("mode") not in ("live", "dry") or data.get("status") not in (
            "passed", "checks_failed", "agent_error", "scenario_error"):
        raise ValueError("invalid timing mode or status")

    def milliseconds(value, nullable=False):
        if nullable and value is None:
            return
        if type(value) is not int or value < 0:
            raise ValueError("invalid timing milliseconds")

    milliseconds(data.get("wall_ms"))
    for field in ("setup_ms", "checks_ms"):
        if field not in data:
            raise ValueError("missing phase timing")
        milliseconds(data[field], nullable=True)
    calls = data.get("adapter_calls")
    if not isinstance(calls, list) or (data["mode"] == "dry" and calls):
        raise ValueError("invalid adapter timings")
    for turn, call in enumerate(calls, 1):
        if not isinstance(call, dict) or type(call.get("turn")) is not int or call["turn"] != turn:
            raise ValueError("invalid adapter turn")
        if type(call.get("exit_code")) is not int:
            raise ValueError("invalid adapter exit code")
        milliseconds(call.get("wall_ms"))
    return data


def record(directory, event, arguments):
    now = time.monotonic_ns()
    state_path = directory / ".timing-state.json"
    if event == "start":
        mode, = arguments
        state = dict(started=now, setup_started=now, mode=mode, setup_ms=None,
                     checks_ms=None, adapter_calls=[])
    else:
        state = json.loads(state_path.read_text())
        if event == "setup-end":
            state["setup_ms"] = elapsed(state.pop("setup_started"), now)
        elif event == "call-start":
            turn, = arguments
            state["adapter_calls"].append(dict(turn=int(turn), started=now))
        elif event == "call-end":
            code, = arguments
            call = state["adapter_calls"][-1]
            call.update(wall_ms=elapsed(call.pop("started"), now), exit_code=int(code))
        elif event == "checks-start":
            state["checks_started"] = now
        elif event == "finish":
            status, = arguments
            if "setup_started" in state:
                state["setup_ms"] = elapsed(state.pop("setup_started"), now)
            if "checks_started" in state:
                state["checks_ms"] = elapsed(state.pop("checks_started"), now)
            # An interrupted call has no observed exit or complete wall time.
            if any("started" in call for call in state["adapter_calls"]):
                raise ValueError("adapter timing is incomplete")
            data = dict(schema_version=1, mode=state["mode"], status=status,
                        wall_ms=elapsed(state["started"], now), setup_ms=state["setup_ms"],
                        adapter_calls=state["adapter_calls"], checks_ms=state["checks_ms"])
            atomic_json(directory / "timing.json", data)
            state_path.unlink()
            print(f"{data['wall_ms'] / 1000:.1f}s")
            return
        else:
            raise ValueError("unknown timing event")
    atomic_json(state_path, state)


if __name__ == "__main__":
    try:
        directory, event, *arguments = sys.argv[1:]
        record(Path(directory), event, arguments)
    except (OSError, ValueError, KeyError, TypeError) as error:
        sys.exit(f"ERROR: timing record failed: {error}")
