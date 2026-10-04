"""Shared JSONL process handling for CLI adapters. No harness or model defaults."""
from contextlib import contextmanager
import json
import os
import signal
import subprocess
import sys


@contextmanager
def agent(args):
    child = None

    def interrupted(signum, _frame):
        sys.exit(128 + signum)

    handlers = {sig: signal.signal(sig, interrupted)
                for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)}
    try:
        child = subprocess.Popen(args, stdout=subprocess.PIPE, text=True,
                                 encoding="utf-8", start_new_session=True)
        yield child
    finally:
        try:
            if child is not None:
                # A CLI can exit while its tools still hold the output pipe.
                # Stop its group even when the direct child has already exited.
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    pass
                finally:
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    child.wait()
                child.stdout.close()
        finally:
            for sig, handler in handlers.items():
                signal.signal(sig, handler)


def events(child):
    # LF framing keeps Unicode separators inside JSON strings intact.
    for line in child.stdout:
        event = json.loads(line)
        if not isinstance(event, dict):
            raise ValueError("CLI event must be a JSON object")
        yield event
