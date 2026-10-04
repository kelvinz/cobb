"""Own the eval runner's process group so cancellation also stops its work."""
import os
import signal
import subprocess
import sys
import threading
import time


def stop_group(child):
    # The runner can exit before its workers. Signal the group even then.
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    # JSONL adapters need up to three seconds to stop their own CLI groups.
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        child.poll()
        try:
            os.killpg(child.pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.05)
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def main():
    child = None

    def interrupted(signum, _frame):
        raise SystemExit(128 + signum)

    signals = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
    for sig in signals:
        signal.signal(sig, interrupted)
    try:
        interactive = sys.stdin.isatty()
        child = subprocess.Popen(["bash", *sys.argv[1:]],
                                 env=dict(os.environ, COBB_EVAL_SUPERVISED="1",
                                          COBB_EVAL_TTY="1" if interactive else "0"),
                                 stdin=subprocess.PIPE if interactive else None,
                                 start_new_session=True)
        if interactive:
            # Keep the terminal in this session. A new-session shell must not
            # acquire it as a controlling terminal (which can stall exit on macOS).
            def forward_input():
                try:
                    while data := os.read(sys.stdin.fileno(), 4096):
                        while data:
                            data = data[os.write(child.stdin.fileno(), data):]
                except (BrokenPipeError, OSError):
                    pass
                finally:
                    try: child.stdin.close()
                    except OSError: pass
            threading.Thread(target=forward_input, daemon=True).start()
        return child.wait()
    finally:
        # A second cancellation must not interrupt cleanup.
        for sig in signals:
            signal.signal(sig, signal.SIG_IGN)
        if child is not None:
            stop_group(child)
            child.wait()


if __name__ == "__main__":
    sys.exit(main())
