#!/usr/bin/env python3
"""agentcy: team config, worker prompts, the herdr-core (hc) and T3 Code backends, and image and video generation.

Standard library only. Run from the project root (the folder that holds agentcy/agentcy.json after init).
"""
from __future__ import annotations  # so macOS's system python3 (3.9) accepts annotations such as str | None
import argparse
import base64
from contextlib import contextmanager
import fcntl
import functools
import json
import mimetypes
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import urllib.error
import urllib.request
import uuid

SKILL = Path(__file__).resolve().parents[1]
HOME = "agentcy"  # the visible team folder at the project root
CONFIG = "agentcy.json"  # inside HOME
ROLES = ("orchestrator", "worker", "reviewer", "researcher", "learner", "image", "video")
LESSON_LIMIT = 1500  # characters per agent file, so lessons stay a small part of each starting prompt
FEEDBACK = "feedback.md"  # inside HOME: feedback waiting for the learner
RESERVED = ("init", "learn")  # command words, so no agent can take them
LAUNCH = ("harness", "model", "effort", "approve", "args")
SETTING = ("harness", "model", "effort")  # what the user picks per agent; approve and args keep the template's
NAME = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,47}$")
DEFAULT = ("", "default")
POLL_SECONDS = 2
START_SECONDS = 30  # how long spawn waits for a new agent to report that it is ready

# Model and effort flags per harness. Other harnesses take their launch flags from "args" only.
FLAGS = {
    "claude": lambda model, effort: ["--model", model] * bool(model) + ["--effort", effort] * bool(effort),
    "codex": lambda model, effort: ["--model", model] * bool(model) + ["-c", f"model_reasoning_effort={effort}"] * bool(effort),
    "pi": lambda model, effort: ["--model", model] * bool(model) + ["--thinking", effort] * bool(effort),
}
FLAGS["agy"] = FLAGS["claude"]  # Antigravity CLI: --model and --effort (low|medium|high|xhigh|max)
# "approve": "auto" starts the harness in its own reviewed auto mode; "ask" (the default) adds no flag.
AUTO = {
    "claude": ["--permission-mode", "auto"],
    "codex": ["--approve-for-me"],
    "agy": ["--mode", "auto"],
    "pi": [],  # pi has no approval prompts
}
APPROVE = ("ask", "auto")
# Thinking levels per harness, from each one's --help. Codex takes its levels from its model cache.
EFFORTS = {
    "claude": ("low", "medium", "high", "xhigh", "max"),
    "codex": ("low", "medium", "high", "xhigh"),
    "pi": ("off", "minimal", "low", "medium", "high", "xhigh", "max"),
    "agy": ("low", "medium", "high", "xhigh", "max"),
}
# Claude Code cannot list its models without a network call; add new models here.
CLAUDE_MODELS = ("claude-fable-5-2", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5")
# Flags a harness always needs under hc. Codex's shared daemon would run its commands outside hc.
ALWAYS = {"codex": ["--no-daemon"]}
BACKENDS = ("auto", "hc", "t3")  # auto: t3 inside a T3 Code thread, hc otherwise
# T3 Code provider instance and effort option per harness. T3 Code starts the harness itself,
# so launch flags in "args" do not reach it.
PROVIDERS = {"claude": "claudeAgent", "codex": "codex", "pi": "pi", "agy": "antigravity"}
EFFORT_OPTION = {"claudeAgent": "effort", "codex": "reasoningEffort", "pi": "thinking", "antigravity": "thinking_level"}
T3_NOT_APPLIED = ["args"]
GREETING = "You are an agentcy agent. Your briefs arrive as messages in this thread. For now, reply with the single word: ready"
MEDIA_KEYS = {"gemini": "GEMINI_API_KEY", "openai": "OPENAI_API_KEY"}
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
OPENAI_URL = "https://api.openai.com/v1/images/"


class Fail(Exception):
    """A user-facing error: printed to stderr, exit status 1."""


# ---------------------------------------------------------------- config

def find_root(start: Path) -> Path:
    """The folder that holds the team config; without init, the folder the command runs in."""
    for folder in [start, *start.parents]:
        if (folder / HOME / CONFIG).is_file():
            return folder
    return start


def initialized(root: Path) -> bool:
    return (root / HOME / CONFIG).is_file()


def make_home(root: Path) -> Path:
    """The team folder and its .gitignore. Without init, it holds only runs and state."""
    home = root / HOME
    home.mkdir(exist_ok=True)
    if not (home / ".gitignore").exists():
        (home / ".gitignore").write_text("runs/\nstate.json\nstate.tmp\n")
    return home


@functools.cache
def pi_models() -> tuple[str, ...] | None:
    """`pi --offline --list-models` prints a table of provider and model; None when pi cannot list them."""
    if not shutil.which("pi"):
        return None
    done = subprocess.run(["pi", "--offline", "--list-models"], capture_output=True, text=True)
    if done.returncode:
        return None
    rows = [line.split()[:2] for line in done.stdout.splitlines()[1:] if len(line.split()) > 1]
    return tuple(f"{provider}/{model}" for provider, model in rows)


@functools.cache
def listed_models(harness: str) -> frozenset | None:
    """The models a harness lists without a network call; None when it cannot list them. Only pi can."""
    models = pi_models() if harness == "pi" else None
    if models is None:
        return None
    return frozenset([*models, *(model.split("/", 1)[1] for model in models)])


@functools.cache
def codex_models() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The models in the cache that Codex keeps, and their thinking levels; empty without a cache."""
    path = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "models_cache.json"
    try:
        listed = [m for m in json.loads(path.read_text())["models"] if m.get("visibility") != "hide"]
        efforts = dict.fromkeys(level["effort"] for m in listed for level in m.get("supported_reasoning_levels", []))
        return tuple(m["slug"] for m in listed), tuple(efforts)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return (), ()


def choices(harness: str) -> tuple[list[str], list[str]]:
    """The models and thinking levels that the menu numbers for a harness."""
    if harness == "codex":
        models, efforts = codex_models()
        return list(models), list(efforts or EFFORTS["codex"])
    models = {"pi": pi_models() or (), "claude": CLAUDE_MODELS}.get(harness, ())
    return list(models), list(EFFORTS.get(harness, ()))


def harness_menu() -> list[dict]:
    """The installed harnesses that agentcy knows flags for, numbered from 1 in this order."""
    return [{"harness": h, "models": choices(h)[0], "efforts": choices(h)[1]} for h in FLAGS if shutil.which(h)]


def launch_errors(where: str, spec: dict) -> list[str]:
    errors = []
    harness = spec.get("harness")
    if not isinstance(harness, str) or not harness:
        return [f"{where}: harness is missing"]
    args = spec.get("args", [])
    if not isinstance(args, list) or not all(isinstance(x, str) for x in args):
        errors.append(f"{where}: args must be a list of strings")
    for key in ("model", "effort"):
        if not isinstance(spec.get(key, ""), str):
            errors.append(f"{where}: {key} must be a string")
    if harness not in FLAGS and (spec.get("model", "") not in DEFAULT or spec.get("effort", "") not in DEFAULT):
        errors.append(f"{where}: agentcy knows no model/effort flags for {harness}; put them in args")
    approve = spec.get("approve", "ask")
    if approve not in APPROVE:
        errors.append(f"{where}: approve must be one of {', '.join(APPROVE)}")
    elif approve == "auto" and harness not in AUTO:
        errors.append(f"{where}: agentcy knows no auto mode for {harness}; put its flag in args")
    return errors


def validate(cfg) -> list[str]:
    if not isinstance(cfg, dict):
        return ["the config must be a JSON object"]
    errors = []
    if cfg.get("backend", "auto") not in BACKENDS:
        errors.append(f"backend: use one of {', '.join(BACKENDS)}")
    agents = cfg.get("agents")
    if not isinstance(agents, dict) or not agents:
        return errors + ["agents: add at least one agent"]
    roles = []

    for name, agent in agents.items():
        where = f"agents.{name}"
        if not NAME.match(name):
            errors.append(f"{where}: names use a-z, 0-9, - and _, start with a letter, max 32")
        elif name in RESERVED:
            errors.append(f"{where}: {name} is a command word; choose another name")
        if not isinstance(agent, dict):
            errors.append(f"{where}: must be an object")
            continue
        role = agent.get("role")
        roles.append(role)
        if role not in ROLES:
            errors.append(f"{where}: role must be one of {', '.join(ROLES)}")
        if not agent.get("character"):
            errors.append(f"{where}: character is missing")
        if role == "orchestrator":
            if "harness" in agent:
                errors += launch_errors(where, agent)
            continue
        if not agent.get("use"):
            errors.append(f"{where}: use is missing; the orchestrator chooses agents by it")
        if any(key in agent for key in SETTING):  # none of them: the user picks the setting when it is needed
            errors += launch_errors(where, agent)
        tools = agent.get("tools", {})
        if not isinstance(tools, dict):
            errors.append(f"{where}.tools: must be an object")
            continue
        for tool_name, tool in tools.items():
            if not isinstance(tool, dict) or not tool.get("use"):
                errors.append(f"{where}.tools.{tool_name}: use is missing")
            elif any(key in tool for key in LAUNCH):
                errors += launch_errors(f"{where}.tools.{tool_name}", launch(agent, tool_name))
    if roles.count("orchestrator") != 1:
        errors.append("agents: exactly one agent needs role orchestrator")
    if "worker" not in roles:
        errors.append("agents: at least one agent needs role worker")
    return errors


def template() -> dict:
    return json.loads((SKILL / "templates" / CONFIG).read_text())


def cast() -> dict:
    """The template's team without harness, model, or effort. The user picks those for each agent
    when the orchestrator first needs it; the template's own values are the recommended picks."""
    cfg = template()
    for agent in cfg["agents"].values():
        for key in SETTING:
            agent.pop(key, None)
    return cfg


def load(root: Path) -> dict:
    """The project's team; without init, the template's cast with no settings."""
    path = root / HOME / CONFIG
    if not path.is_file():
        return cast()
    try:
        cfg = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise Fail(f"{path}: {error}") from error
    errors = validate(cfg)
    if errors:
        raise Fail(f"{path} is not valid:\n" + "\n".join(f"- {e}" for e in errors))
    return cfg


def launch(agent: dict, tool_name: str | None = None) -> dict:
    """How to start the agent. A tool that names a harness replaces the whole launch;
    one without a harness changes only the fields it sets. The agent's approve carries over either way."""
    tool = agent.get("tools", {}).get(tool_name, {}) if tool_name else {}
    if "harness" in tool:
        spec = {key: tool[key] for key in LAUNCH if key in tool}
        if "approve" in agent:
            spec.setdefault("approve", agent["approve"])
        return spec
    return {**{key: agent[key] for key in LAUNCH if key in agent}, **{key: tool[key] for key in LAUNCH if key in tool}}


def launch_args(spec: dict) -> list[str]:
    model = "" if spec.get("model", "") in DEFAULT else spec["model"]
    effort = "" if spec.get("effort", "") in DEFAULT else spec["effort"]
    flags = FLAGS.get(spec["harness"], lambda m, e: [])(model, effort)
    auto = AUTO[spec["harness"]] if spec.get("approve") == "auto" else []
    return flags + auto + ALWAYS.get(spec["harness"], []) + spec.get("args", [])


def orchestrator(cfg) -> dict:
    return next(a for a in cfg["agents"].values() if a["role"] == "orchestrator")


# ---------------------------------------------------------------- state

def state_path(root: Path) -> Path:
    return root / HOME / "state.json"


def load_state(root: Path) -> dict:
    path = state_path(root)
    try:
        state = json.loads(path.read_text())
    except FileNotFoundError:
        return {"agents": {}}
    except json.JSONDecodeError as error:
        raise Fail(f"{path}: {error}") from error
    if not isinstance(state, dict) or not isinstance(state.get("agents"), dict):
        raise Fail(f"{path}: must be an object with an agents object")
    return state


@contextmanager
def state_lock(root: Path):
    # Commands never replace the team folder, so its inode is a stable per-project lock, with or without init.
    # Hold this from the first state read through the backend call and state save.
    handle = os.open(make_home(root), os.O_RDONLY)
    try:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield
    finally:
        os.close(handle)  # closing the descriptor releases the lock


def save_state(root: Path, state: dict) -> None:
    path = state_path(root)
    make_home(root)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(state, indent=2) + "\n")
    temp.replace(path)


# ---------------------------------------------------------------- hc backend

def login(argv: list[str]) -> list[str]:
    """Run argv through the user's interactive login shell. hc starts programs with the login
    session's environment, which lacks what shell startup files add, such as pnpm and mise
    commands on PATH. Shells other than zsh and bash run argv as it is."""
    shell = os.environ.get("SHELL", "")
    if Path(shell).name not in ("zsh", "bash"):
        return argv
    return [shell, "-lic", 'exec "$0" "$@"', *argv]


class Backend:
    """What every backend shares: `wait` and `require` on top of the backend's own `state`.

    A backend also has problem, session, live_names, spawn, reach, prompt, read, and stop.
    """

    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def require(self, name, address):
        state = self.state(address)
        if state[0] == "gone":
            raise Fail(f"{name!r} is no longer running in {address}; run `spawn` to start a new agent")
        return state

    def wait(self, agents, seconds):
        """Wait until the first of the agents ends a turn after its `after_turn`, or is blocked,
        failed, or gone. `agents` holds (name, address, after_turn). Returns (name, status),
        or (None, "timeout").

        An agent that has not started its new turn is still idle, so the status alone cannot
        tell "finished" from "not started"; the turn can.
        """
        deadline = time.monotonic() + seconds
        while True:
            working = []
            for name, address, after_turn in agents:
                status, turn = self.state(address)
                if status in ("blocked", "error", "gone", "unknown") or (status in ("idle", "done") and turn > after_turn):
                    return name, status
                if status == "working":
                    working.append(address)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None, "timeout"
            self.pause(working if len(agents) == 1 else [], remaining)

    def pause(self, working, remaining):
        """Wait a short time before the next look at the agents."""
        time.sleep(min(POLL_SECONDS, remaining))


class Hc(Backend):
    """Start, prompt, wait for, read, and stop agents in herdr-core terminals through `hc`.

    Each agent is addressed by the terminal address that `hc run` returned, such as `t12`.
    A core never reuses an address, so a saved address cannot reach another program.
    """

    def run(self, command, *args, check=True):
        """(data, error) from one hc command. hc prints JSON, and an error object on stderr."""
        argv = ["hc", command, "--json", *args]
        if self.dry_run:
            print("+ " + shlex.join(argv))
            return {}, None
        try:
            done = subprocess.run(argv, capture_output=True, text=True)
        except FileNotFoundError as error:
            raise Fail("hc is not on PATH; install the Herdr app or herdr-core") from error
        if not done.returncode:
            return (json.loads(done.stdout) if done.stdout.strip() else {}), None
        try:
            error = json.loads(done.stderr)["error"]
        except (json.JSONDecodeError, KeyError, TypeError):
            error = None
        if not isinstance(error, dict):
            error = {"kind": "failed", "message": (done.stderr or done.stdout).strip()}
        if check:
            raise Fail(f"`hc {command}` failed: {error.get('message')}")
        return {}, error

    def problem(self) -> str | None:
        """Why agents cannot start now, or None when they can."""
        if not shutil.which("hc"):
            return "hc is not installed; the Herdr app installs herdr-core (hc)"
        error = self.run("server", "status", check=False)[1]
        return f"the hc server does not answer: {error.get('message')}" if error else None

    def session(self) -> dict:
        """The hc terminal this session runs in: its address, harness, and labels. Empty outside hc."""
        address = os.environ.get("HC_TERMINAL_ID")
        if not address or self.dry_run:
            return {}
        data, error = self.run("get", address, check=False)
        if error:
            return {}
        return {"terminal": address, "harness": (data.get("foreground") or {}).get("name"),
                "labels": data.get("labels") or {}}

    def live_names(self) -> set[str]:
        if self.dry_run:
            return set()
        data, _ = self.run("ls")
        return {t["name"] for t in data.get("terminals", []) if t.get("name")}

    def spawn(self, name, spec, cwd, own_tab=False):
        """Start the harness in a new terminal and wait until the agent reports that it is ready.

        A worker is a child of this session's terminal, so the Herdr app lists it under this
        session's tab. With own_tab, the agent has no parent and gets its own tab in this space.
        """
        options = ["--bg", "--no-notify", "--name", name, "--cwd", str(cwd)]
        if own_tab:
            options.append("--no-parent")
            space = self.session().get("labels", {}).get("herdr.space")
            if space:
                # Herdr shows a terminal with these labels; a tab id it does not know becomes a new tab.
                options += ["--label", f"herdr.space={space}", "--label", f"herdr.tab=tb{uuid.uuid4().hex}"]
        data, _ = self.run("run", *options, "--", *login([spec["harness"], *launch_args(spec)]))
        address = data.get("address") or ("<address>" if self.dry_run else None)
        if not address:
            raise Fail(f"`hc run` returned no address: {data}")
        waited, error = self.run("wait", address, "--timeout", str(START_SECONDS), check=False)
        if error:
            self.run("kill", address, check=False)
            self.run("rm", address, check=False)
            raise Fail(f"`hc wait` failed after starting {name}: {error.get('message')}; the terminal was removed")
        if waited.get("reason") == "exit":
            text = self.run("read", address, check=False)[0].get("text", "")
            self.run("rm", address, check=False)
            raise Fail(f"{name} exited at start (code {waited.get('exit_code')}): {text.strip()[-2000:]}")
        # Claude Code and Codex report no status while a startup question, such as folder trust, is open.
        status = waited.get("status") if waited.get("ended") else None
        return address, {"idle": "ready", "done": "ready", "blocked": "blocked"}.get(status, "starting")

    def reach(self, address):
        return f"hc attach {address}"

    def state(self, address):
        """(status, turn). The status is the agent's own word, "starting" before its first report,
        or "gone" once its program has ended. The turn goes up each time the agent stops working."""
        if self.dry_run:
            return "unknown", -1
        data, error = self.run("get", address, check=False)
        if error:
            # Only not_found proves that the agent is gone. Other errors keep the saved record.
            if error.get("kind") == "not_found":
                return "gone", -1
            raise Fail(f"`hc get` failed: {error.get('message')}")
        if data.get("state") != "live":
            return "gone", -1
        return (data.get("status") or {}).get("state") or "starting", data.get("turn", 0)

    def prompt(self, name, address, text):
        """Type text into the agent and press Enter. Returns the turn when it went in, and whether
        the agent started working. A send that did not start may still arrive: read before resending."""
        self.require(name, address)
        data, error = self.run("send", address, text, check=False)
        if error:
            if error.get("kind") == "blocked":
                raise Fail(f"{name} is waiting on a question in its terminal; run `read {name}`")
            raise Fail(f"`hc send` failed: {error.get('message')}")
        return data.get("turn", -1), data.get("started")

    def pause(self, working, remaining):
        if working:
            # hc returns when the agent stops working, or early when someone messages this session.
            self.run("wait", working[0], "--timeout", str(max(1, round(remaining))), check=False)
        else:
            # hc waits for one terminal only. With several agents, or one that has not
            # started its turn yet, look again shortly.
            super().pause(working, remaining)

    def read(self, name, address, lines):
        self.require(name, address)
        data, _ = self.run("read", address, "--lines", str(lines))
        return data.get("text", "")

    def stop(self, address):
        """End the agent's program and remove its terminal. False when it had already ended."""
        running = self.state(address)[0] != "gone"
        if running:
            self.run("kill", address)
            deadline = time.monotonic() + 10
            while not self.dry_run and self.state(address)[0] != "gone":
                if time.monotonic() >= deadline:
                    raise Fail(f"the agent in {address} did not stop within 10 seconds; retry close")
                time.sleep(0.2)
        _, error = self.run("rm", address, check=False)  # hc removes only a finished terminal
        if error and error.get("kind") != "not_found":
            raise Fail(f"`hc rm` failed: {error.get('message')}")
        return running


# ---------------------------------------------------------------- T3 Code backend

class T3(Backend):
    """Prompt, wait for, read, and stop agents in T3 Code subagent threads through its `t3` command.

    Only the orchestrator's own session can start a subagent, with its `delegate_task` tool:
    `delegate` gives the call, and `adopt` records the child thread it made. Each agent is
    addressed by its thread id. The thread keeps its context, so a follow-up brief goes to it.
    """

    LIVE = ("preparing", "queued", "starting", "running", "waiting")
    FAILED = ("failed", "interrupted", "cancelled", "rolled_back")

    def cli(self) -> str | None:
        return os.environ.get("T3CODE_CLI_PATH") or shutil.which("t3")

    def run(self, command, *args, check=True):
        """(data, error) from one `t3 thread` command. t3 prints JSON, or a message on failure."""
        argv = [self.cli() or "t3", "thread", command, *args, "--json"]
        if self.dry_run:
            print("+ " + shlex.join(argv))
            return {}, None
        try:
            done = subprocess.run(argv, capture_output=True, text=True)
        except FileNotFoundError as error:
            raise Fail("t3 is not on PATH; open T3 Code once so it installs its `t3` command") from error
        try:
            data = json.loads(done.stdout) if not done.returncode else None
        except json.JSONDecodeError:
            data = None  # `t3 thread list` reports an unknown project as text, with exit status 0
        if data is not None:
            return data, None
        message = (done.stderr or done.stdout).strip()
        if check:
            raise Fail(f"`t3 thread {command}` failed: {message}")
        return {}, {"message": message, "gone": "no longer available" in message}

    def problem(self) -> str | None:
        if not self.cli():
            return "t3 is not installed; open T3 Code once so it installs its `t3` command"
        error = self.run("list", "--project", ".", check=False)[1]
        return f"T3 Code cannot start threads here: {error['message']}" if error else None

    def session(self) -> dict:
        """The T3 Code thread this session runs in: its harness and model. Empty outside T3 Code."""
        thread = os.environ.get("T3CODE_THREAD_ID")
        if not thread or self.dry_run:
            return {}
        data, error = self.run("show", thread, "--messages", "0", check=False)
        if error:
            return {}
        info = data.get("thread", {})
        harness = next((h for h, p in PROVIDERS.items() if p == info.get("providerInstanceId")),
                       info.get("providerInstanceId"))
        return {"thread": thread, "harness": harness, "model": info.get("model")}

    def live_names(self) -> set[str]:
        return set()  # thread titles are not addresses, so they cannot clash

    def delegate(self, key, spec) -> dict:
        """The `delegate_task` call that starts the agent as a subagent of this session's thread."""
        provider = PROVIDERS.get(spec["harness"])
        if not provider:
            raise Fail(f"T3 Code runs only {', '.join(PROVIDERS)}; {key} uses {spec['harness']}")
        if spec.get("model", "") in DEFAULT:
            raise Fail(f"T3 Code needs a model to choose the provider; set a model for {key} in {CONFIG}")
        effort = spec.get("effort", "")
        # Empty options clear the orchestrator's own, so the model keeps its default effort.
        options = {} if effort in DEFAULT else {EFFORT_OPTION[provider]: effort}
        call = {"title": f"agentcy: {key}", "task": GREETING, "mode": "wait",
                "target": {"providerInstanceId": provider, "model": spec["model"], "options": options}}
        if spec.get("approve", "ask") == "ask":
            call["runtimeMode"] = "approval-required"  # "auto" keeps the orchestrator's own mode
        return call

    def adopt(self, name, thread):
        """Record a subagent thread that this session's `delegate_task` started."""
        if self.dry_run:
            return thread, "ready"
        info = (self.show(thread, 0) or {}).get("thread")
        if not info:
            raise Fail(f"T3 Code has no thread {thread}")
        if info.get("relationshipToParent") != "subagent" or info.get("parentThreadId") != os.environ.get("T3CODE_THREAD_ID"):
            raise Fail(f"thread {thread} is not a subagent of this session's thread; agentcy records only its own")
        status, _ = self.state(thread)
        if status == "error":
            raise Fail(f"{name} failed at start: {self.read(name, thread, 20).strip()[-2000:]}")
        return thread, {"idle": "ready", "blocked": "blocked"}.get(status, "starting")

    def show(self, address, messages):
        data, error = self.run("show", address, "--messages", str(messages), check=False)
        if error:
            # Only an unknown thread proves that the agent is gone. Other errors keep the saved record.
            if error["gone"]:
                return None
            raise Fail(f"`t3 thread show` failed: {error['message']}")
        return data

    def reach(self, address):
        data = None if self.dry_run else self.show(address, 0)
        return (data or {}).get("thread", {}).get("link") or f"the T3 Code thread {address}"

    def state(self, address):
        """(status, turn) in hc's words. The turn counts the runs that have ended."""
        if self.dry_run:
            return "unknown", -1
        data = self.show(address, 0)
        thread = (data or {}).get("thread")
        if not thread or thread.get("archived"):
            return "gone", -1
        status = thread.get("status")
        ended = thread.get("runCount", 0) - (status in self.LIVE)
        if thread.get("pendingRequestCount"):
            return "blocked", ended
        if status in self.LIVE:
            return "working", ended
        return ("error" if status in self.FAILED else "idle"), ended

    def prompt(self, name, address, text):
        """Send text as the thread's next message. Returns the runs counted before it, so `wait`
        returns once this message's run has ended, and whether the run started at once."""
        status, ended = self.require(name, address)
        if status == "blocked":
            raise Fail(f"{name} is waiting on a question in its T3 Code thread; run `read {name}`")
        data, _ = self.run("send", address, text)
        # A busy thread queues the message behind its current run.
        return ended + (status == "working"), data.get("delivery") == "started"

    def read(self, name, address, lines):
        self.require(name, address)
        data = self.show(address, 10) or {}
        thread = data.get("thread", {})
        head = [f"{thread.get('status')}  {thread.get('providerInstanceId')}/{thread.get('model')}  {thread.get('link')}"]
        if thread.get("pendingRequestCount"):
            head.append(f"Waiting for {thread['pendingRequestCount']} answer(s) in T3 Code.")
        body = "\n".join(f"\n[{m['role']}]\n{m['text']}" for m in data.get("messages", [])).splitlines()
        return "\n".join(head + body[-lines:])

    def stop(self, address):
        """T3 Code keeps the thread for the user. A thread that still works must be stopped in the app."""
        if self.state(address)[0] in ("working", "blocked"):
            raise Fail(f"the agent in {self.reach(address)} is still working; stop it in T3 Code, then close it")
        return False


def backend_name(cfg) -> str:
    """auto: T3 Code inside a T3 Code thread, where the user talks to the orchestrator; hc otherwise."""
    chosen = cfg.get("backend", "auto")
    if chosen == "auto":
        return "t3" if os.environ.get("T3CODE_THREAD_ID") else "hc"
    return chosen


def backend(cfg, dry_run):
    return {"hc": Hc, "t3": T3}[backend_name(cfg)](dry_run)


# ---------------------------------------------------------------- prompts

def role_text(role: str) -> str:
    command = f"python3 {shlex.quote(str(SKILL / 'scripts' / 'agentcy.py'))}"
    return (SKILL / "references" / "roles" / f"{role}.md").read_text().replace("{agentcy}", command)


def rules_text(cfg, key, name, tool_name, root) -> str:
    agent = cfg["agents"][key]
    spec = launch(agent, tool_name)
    lead = orchestrator(cfg)
    source = f" ({agent['from']})" if agent.get("from") else ""
    header = [f"# You are {agent['character']}{source}, the agentcy {agent['role']}",
              f"Your team name is `{name}`. {lead['character']}, the orchestrator, sends your briefs here.",
              f"Harness: {spec['harness']}" + (f", model {spec['model']}" if spec.get("model") else "") + "."]
    if agent.get("voice"):
        header.append(f"Voice: {agent['voice']} Use it when you talk; keep result files plain.")
    if tool_name:
        tool = agent["tools"][tool_name]
        settings = {k: v for k, v in tool.items() if k not in (*LAUNCH, "use")}
        header.append(f"Tool: `{tool_name}` — {tool['use']}." + (f" Settings: {json.dumps(settings)}" if settings else ""))
    parts = ["\n".join(header), (SKILL / "references" / "contract.md").read_text(), role_text(agent["role"])]
    lessons = lesson_text(root, key)
    if lessons:
        parts.append(f"# Your lessons\nFrom earlier work in this project. They refine the rules above; "
                     f"the brief and the user win over a lesson.\n\n{lessons}")
    return "\n\n".join(parts) + "\n"


# ---------------------------------------------------------------- commands

def cmd_init(args):
    root = Path.cwd()
    home = root / HOME
    created = not (home / CONFIG).exists()
    if created and not args.dry_run:
        make_home(root)
        shutil.copyfile(SKILL / "templates" / CONFIG, home / CONFIG)
    print(json.dumps({"config": str(home / CONFIG), "home": str(home), "created": created}))


def setting(spec: dict) -> dict:
    return {key: spec[key] for key in SETTING if key in spec}


def numbered(spec: dict, menu: list[dict]) -> str | None:
    """A setting as the menu's numbers, such as 3:16:7; None when a part is not in the menu."""
    entry = next((i for i, h in enumerate(menu, 1) if h["harness"] == spec.get("harness")), None)
    if entry is None:
        return None
    parts = [str(entry)]
    for key, listed in (("model", menu[entry - 1]["models"]), ("effort", menu[entry - 1]["efforts"])):
        value = spec.get(key, "default")
        if value not in DEFAULT and value not in listed:
            return None
        parts.append("" if value in DEFAULT else str(listed.index(value) + 1))
    return ":".join(parts).rstrip(":")


def shown(spec: dict) -> str:
    return " · ".join([spec["harness"], spec.get("model", "default"), spec.get("effort", "default")])


def packed(label: str, items: list[str]) -> list[str]:
    """Menu items in lines of at most 100 characters; a number stays with its name."""
    rows = [[]]
    for item in items:
        if rows[-1] and len("  ".join(rows[-1] + [item])) > 86:
            rows.append([])
        rows[-1].append(item)
    return [f"    {label if i == 0 else '':<9} " + "  ".join(row) for i, row in enumerate(rows)]


def menu_text(rows: list[dict], menu: list[dict]) -> str:
    if not menu:
        return f"No harness that agentcy knows is installed: {', '.join(FLAGS)}."
    width = max(len(row["name"]) for row in rows)
    lines = ["Pick a harness:model:thinking for each agent by number, such as 1:2:3.", "0 — my picks for all:"]
    for row in rows:
        about = row["role"] + (f": {row['use'].split(':')[0]}" if row.get("use") else "")
        pick = row["recommended"]
        text = f"  {row['name']:<{width}}  {textwrap.shorten(about, 44, placeholder='…'):<44}  "
        if pick:
            number = numbered(pick, menu)
            installed = any(entry["harness"] == pick["harness"] for entry in menu)
            problem = "does not list this model or thinking level" if installed else "is not installed"
            text += shown(pick) + (f"  ({number})" if number else f"  ({pick['harness']} {problem})")
        else:
            text += "no pick: choose one"
        if row["now"]:
            text += f"  — now {shown(row['now'])}"
        lines.append(text)
    lines.append("")
    for number, entry in enumerate(menu, 1):
        lines.append(f"{number} {entry['harness']}")
        for label, listed in (("models:", entry["models"]), ("thinking:", entry["efforts"])):
            lines += packed(label, [f"{i} {value}" for i, value in enumerate(listed, 1)] or ["type a name"])
    lines += ["", 'Reply 0, or one line for each agent you want to change, such as "skyler 1:2:3". '
                  "Leave out a part to keep the harness's own model or thinking, or type a name instead of a number."]
    return "\n".join(lines)


def cmd_options(args):
    root = find_root(Path.cwd())
    cfg = load(root)
    names = list(dict.fromkeys(args.agents)) or list(cfg["agents"])
    unknown = [name for name in names if name not in cfg["agents"]]
    if unknown:
        raise Fail(f"no agent {', '.join(unknown)}; agents: {', '.join(cfg['agents'])}")
    picks = {name: setting(agent) for name, agent in template()["agents"].items()}
    menu = harness_menu()
    rows = [{"name": name, "role": cfg["agents"][name]["role"], "use": cfg["agents"][name].get("use"),
             "now": setting(cfg["agents"][name]) or None, "recommended": picks.get(name) or None}
            for name in names]
    print(json.dumps({"harnesses": menu, "agents": rows, "menu": menu_text(rows, menu)}, indent=2))


def chosen(listed: list[str], text: str, what: str) -> str:
    """A number picks from the menu's list; any other text is a name."""
    if not text.isdigit():
        return text
    if not 1 <= int(text) <= len(listed):
        raise Fail(f"{what} {text} is not in the menu; choose 1 to {len(listed)}" if listed
                   else f"the menu has no numbered {what}s here; type a name")
    return listed[int(text) - 1]


def picked(name: str, answer: str, menu: list[dict]) -> dict:
    """The setting that the user's answer names: 0 for the recommended pick, or harness:model:thinking."""
    if answer == "0":
        pick = setting(template()["agents"].get(name, {}))
        if not pick:
            raise Fail(f"{name} has no recommended pick; choose harness:model:thinking")
        return pick
    parts = answer.split(":")
    if len(parts) > 3 or not parts[0]:
        raise Fail(f"{name}: answer {answer!r} as harness:model:thinking, such as 1:2:3, or 0")
    harness = chosen([h["harness"] for h in menu], parts[0], "harness")
    models, efforts = choices(harness)
    spec = {"harness": harness}
    for key, listed, part in (("model", models, parts[1:2]), ("effort", efforts, parts[2:3])):
        if part and part[0]:
            spec[key] = chosen(listed, part[0], key)
    return spec


def cmd_set(args):
    """Save the user's picks. Without init, this creates agentcy/agentcy.json from the cast,
    so the picks last; agents the user has not picked for stay without a setting."""
    if len(args.pairs) % 2:
        raise Fail("give pairs of agent and answer, such as: set arya 0 skyler 1:2:3")
    root = find_root(Path.cwd())
    path = root / HOME / CONFIG
    created = not path.is_file()
    cfg = load(root)
    menu = harness_menu()
    saved = {}
    for name, answer in zip(args.pairs[::2], args.pairs[1::2]):
        agent = cfg["agents"].get(name)
        if agent is None:
            raise Fail(f"no agent {name}; agents: {', '.join(cfg['agents'])}")
        rest = {key: value for key, value in agent.items() if key not in SETTING}
        head = {key: rest.pop(key) for key in ("role", "use") if key in rest}
        cfg["agents"][name] = agent = {**head, **picked(name, answer, menu), **rest}  # the template's order
        saved[name] = describe(launch(agent))
    errors = validate(cfg)
    if errors:
        raise Fail("\n".join(errors))
    if not args.dry_run:
        make_home(root)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(cfg, indent=2) + "\n")
        temp.replace(path)
    print(json.dumps({"config": str(path), "created": created, "agents": saved}))


def lessons_path(root: Path, agent: str) -> Path:
    return root / HOME / "lessons" / f"{agent}.md"


def lesson_text(root: Path, agent: str) -> str:
    """The agent's lesson lines without headings; empty when there are none."""
    try:
        text = lessons_path(root, agent).read_text()
    except FileNotFoundError:
        return ""
    return "\n".join(line for line in text.splitlines() if line.strip() and not line.startswith("#"))


def lesson_report(root: Path, cfg) -> dict:
    report = {}
    for agent in cfg["agents"]:
        path = lessons_path(root, agent)
        size = len(path.read_text()) if path.exists() else 0
        report[agent] = {"path": str(path), "chars": size, "limit": LESSON_LIMIT, "over_limit": size > LESSON_LIMIT}
    return report


def feedback_report(root: Path) -> dict:
    path = root / HOME / FEEDBACK
    lines = path.read_text().splitlines() if path.exists() else []
    return {"path": str(path), "waiting": sum(line.startswith("- ") for line in lines)}


def describe(spec: dict) -> dict:
    """How an agent or tool starts. model_listed is false when the harness lists its models
    and this one is not among them, and null when the harness cannot list them.
    harness is null without init, until the user picks the setting for spawn."""
    if "harness" not in spec:
        return {"harness": None}
    model = spec.get("model", "default")
    listed = None if model in DEFAULT else listed_models(spec["harness"])
    return {"harness": spec["harness"], "model": model,
            "effort": spec.get("effort", "default"), "approve": spec.get("approve", "ask"),
            "installed": bool(shutil.which(spec["harness"])), "model_listed": None if listed is None else model in listed}


def cmd_check(args):
    root = find_root(Path.cwd())
    cfg = load(root)
    chosen = backend(cfg, False)
    name_of = backend_name(cfg)
    problem = chosen.problem()
    session = chosen.session() if not problem else {}
    rows, warnings = [], []
    for name, agent in cfg["agents"].items():
        row = {"name": name, "role": agent["role"]}
        if agent["role"] == "orchestrator":
            row |= describe(launch(agent)) if "harness" in agent else {"harness": "(this session)"}
        else:
            row |= {"use": agent["use"], **describe(launch(agent))}
            if agent.get("tools"):
                row["tools"] = {tool: {"use": spec["use"], **describe(launch(agent, tool))}
                                for tool, spec in agent["tools"].items()}
        for where, info in [(name, row), *((f"{name}.tools.{t}", i) for t, i in row.get("tools", {}).items())]:
            if info.get("model_listed") is False:
                warnings.append(f"{where}: {info['harness']} does not list model {info['model']}")
            if name_of == "t3" and info["harness"] not in ("(this session)", None):
                if info["harness"] not in PROVIDERS:
                    warnings.append(f"{where}: T3 Code runs only {', '.join(PROVIDERS)}, not {info['harness']}")
                elif info["model"] in DEFAULT:
                    warnings.append(f"{where}: T3 Code needs a model to choose the provider")
        rows.append(row)
    print(json.dumps({
        "root": str(root),
        "initialized": initialized(root),
        "agents": rows,
        "warnings": warnings,
        "backend": {"name": name_of, "ready": not problem, "problem": problem,
                    "not_applied": T3_NOT_APPLIED if name_of == "t3" else []},
        "session": {"harness": session.get("harness"), "model": session.get("model"), "inside": name_of if session else None},
        "api_keys": {key: bool(os.environ.get(key)) for key in MEDIA_KEYS.values()},
        "lessons": lesson_report(root, cfg),
        "feedback": feedback_report(root),
    }, indent=2))


def git(root: Path, *args, env=None) -> bytes:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", **(env or {})})
    if done.returncode:
        raise Fail(f"git {args[0]}: {done.stderr.decode(errors='replace').strip()}")
    return done.stdout


def working_tree(root: Path) -> str:
    """Store tracked and non-ignored untracked files in Git, without changing the user's index.

    Like cobb's worktree helper, use a private index. This writes Git objects, not a commit.
    The team folder is left as the user's index has it: the orchestrator writes feedback
    there during a run, and the reviewer must not count that as a change to the work.
    """
    top = Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip())
    index = Path(os.fsdecode(git(top, "rev-parse", "--git-path", "index")).strip())
    if not index.is_absolute():
        index = top / index
    with tempfile.TemporaryDirectory(prefix="agentcy-index-") as temp:
        private = Path(temp) / "index"
        if index.exists():
            shutil.copyfile(index, private)
        env = {**os.environ, "GIT_INDEX_FILE": str(private), "GIT_OPTIONAL_LOCKS": "0"}
        scope = ("--", ":(top)", f":(exclude){HOME}")
        # These flags can hide edits from git add. Stop rather than certify an incomplete snapshot.
        for entry in git(root, "ls-files", "-v", "-z", *scope, env=env).split(b"\0"):
            if entry[:1].islower() or entry.startswith(b"S "):
                raise Fail(f"cannot snapshot {os.fsdecode(entry[2:])!r}: assume-unchanged or skip-worktree "
                           "flags can hide edits; resolve these flags before retrying review")
        git(root, "add", "-A", *scope, env=env)
        # A tree stores only a submodule's commit, not its staged, unstaged, or new files.
        # Check after add so newly added submodules are covered too. Override ignore settings.
        status = git(root, "status", "--porcelain=v2", "-z", "--no-renames",
                     "--ignore-submodules=none", "--untracked-files=all", *scope, env=env)
        for entry in status.split(b"\0"):
            if entry.startswith(b"1 "):
                fields = entry.split(b" ", 8)  # 1 XY S<c><m><u> mH mI mW hH hI path
                if fields[2].startswith(b"S") and fields[2][2:] != b"..":
                    raise Fail(f"cannot snapshot submodule {os.fsdecode(fields[8])!r}: uncommitted files "
                               "are not stored in the review tree; review that submodule separately")
        return git(top, "write-tree", env=env).decode().strip()


def review_baseline(root: Path) -> dict:
    git(root, "rev-parse", "--git-dir")  # outside a Git repository, Git's own error says so
    try:
        git(root, "rev-parse", "--verify", "-q", "HEAD")
    except Fail as error:
        raise Fail("the project has no commit yet; commit once before a reviewed run") from error
    return {
        "root": str(root),
        "head": git(root, "rev-parse", "HEAD").decode().strip(),
        "tree": working_tree(root),
        "staged_patch": git(root, "diff", "--cached", "--binary", "--no-ext-diff", "--no-textconv").decode(errors="replace"),
        "unstaged_patch": git(root, "diff", "--binary", "--no-ext-diff", "--no-textconv").decode(errors="replace"),
    }


def cmd_changes(args):
    root = find_root(Path.cwd())
    path = Path(args.run).resolve() / "baseline.json"
    if not path.is_file():
        raise Fail(f"no {path}; start with `run <slug> --review` before changing files")
    baseline = json.loads(path.read_text())
    if baseline["root"] != str(root):
        raise Fail("the review baseline belongs to another project")
    if args.dry_run:
        print(json.dumps({"baseline": str(path), "action": "compare current files with the baseline"}))
        return
    current = working_tree(root)
    base = baseline["tree"]
    # Without --no-renames, a moved file lists only its new path.
    plain = ("--no-renames", "--no-color")
    files = git(root, "diff", *plain, "--name-only", "-z", base, current, "--")
    patch = git(root, "diff", *plain, "--binary", "--no-ext-diff", "--no-textconv", base, current, "--")
    print(json.dumps({"base": base, "current": current,
                      "files": [os.fsdecode(p) for p in files.split(b"\0") if p],
                      "patch": patch.decode(errors="replace")}, indent=2))


def cmd_run(args):
    if not SLUG.match(args.slug):
        raise Fail("slug: use a-z, 0-9 and -, max 48")
    root = find_root(Path.cwd())
    stamp = f"{time.strftime('%Y%m%d-%H%M%S')}-{args.slug}"
    folder, number = root / HOME / "runs" / stamp, 1
    while folder.exists():  # two runs in the same second
        number += 1
        folder = folder.with_name(f"{stamp}-{number}")
    if not args.dry_run:
        baseline = review_baseline(root) if args.review else None
        make_home(root)
        folder.mkdir(parents=True)
        if baseline is not None:
            (folder / "baseline.json").write_text(json.dumps(baseline, indent=2) + "\n")
    print(folder)


def cmd_spawn(args):
    root = find_root(Path.cwd())
    cfg = load(root)
    key = args.agent
    agent = cfg["agents"].get(key)
    if not agent:
        raise Fail(f"agent {key!r} is not in {CONFIG}")
    if agent["role"] == "orchestrator" and "harness" not in agent:
        raise Fail(f"{key} has no harness in {CONFIG}; the orchestrator runs in this session")
    if args.tool and args.tool not in agent.get("tools", {}):
        raise Fail(f"{key} has no tool {args.tool!r}; tools: {', '.join(agent.get('tools', {})) or 'none'}")
    spec = launch(agent, args.tool)
    if "harness" not in spec:
        raise Fail(f"{key} has no setting yet; ask the user with `options {key}`, then `set`")
    hc = backend(cfg, args.dry_run)
    t3 = isinstance(hc, T3)
    if args.thread and not t3:
        raise Fail("--thread records a T3 Code subagent; this backend is hc")
    if t3 and agent["role"] == "orchestrator":
        raise Fail(f"in T3 Code, start a new thread with {spec['harness']}, model {spec.get('model', 'default')}, "
                   f"effort {spec.get('effort', 'default')}, and give it the same /agentcy request")
    if t3 and not args.thread:
        # Only this session can start a subagent: it makes this call, then runs spawn with --thread.
        print(json.dumps({"agent": key, "tool": args.tool, "status": "delegate", "delegate_task": hc.delegate(key, spec)}))
        return
    state = load_state(root)
    taken = set(state["agents"]) | hc.live_names()
    name, number = key, 1
    while name in taken:
        number += 1
        name = f"{key}-{number}"
    if not NAME.match(name):
        raise Fail(f"name {name!r} is too long")
    if t3:
        address, status = hc.adopt(name, args.thread)
    else:
        # Workers run under this session; an orchestrator taking a handoff gets its own tab for the user.
        address, status = hc.spawn(name, spec, root, own_tab=agent["role"] == "orchestrator")
    if not args.dry_run:
        state["agents"][name] = {"agent": key, "tool": args.tool, "address": address, "turns": 0, "rules": None}
        save_state(root, state)
    print(json.dumps({"name": name, "tool": args.tool, "harness": spec["harness"], "address": address,
                      "reach": hc.reach(address), "status": status}))


def configured(cfg, worker) -> dict:
    agent = cfg["agents"].get(worker["agent"])
    if not agent:
        raise Fail(f"agent {worker['agent']!r} is no longer in {CONFIG}")
    return agent


def cmd_handoff(args):
    """Give the user's arguments to an orchestrator started in its recorded setting."""
    root = find_root(Path.cwd())
    cfg = load(root)
    worker = owned(root, args.name)["agents"][args.name]
    if configured(cfg, worker)["role"] != "orchestrator":
        raise Fail(f"{args.name} is not the orchestrator; use send")
    text = (f"Read {SKILL / 'SKILL.md'} and follow it with these arguments: {args.text} "
            f"(This session was started with the setting in {HOME}/{CONFIG}; skip the session check.)")
    _, started = backend(cfg, args.dry_run).prompt(args.name, worker["address"], text)
    print(json.dumps({"name": args.name, "handed_off": args.text, "started": started}))


def cmd_send(args):
    root = find_root(Path.cwd())
    cfg = load(root)
    state = load_state(root)
    worker = state["agents"].get(args.name)
    if not worker and not args.dry_run:
        raise Fail(f"{args.name!r} was not spawned by agentcy; run `spawn` first")
    worker = worker or {"agent": args.name, "tool": None, "turns": 0, "rules": None, "address": args.name}
    agent = configured(cfg, worker)
    if agent["role"] == "orchestrator":
        raise Fail(f"{args.name} is the orchestrator; use handoff")
    if worker.get("tool") and worker["tool"] not in agent.get("tools", {}):
        raise Fail(f"tool {worker['tool']!r} is no longer in {CONFIG}")
    brief = Path(args.brief).resolve()
    if not brief.is_file():
        raise Fail(f"brief {brief} does not exist")
    hc = backend(cfg, args.dry_run)
    hc.require(args.name, worker["address"])
    stem = brief.with_suffix("")
    result = stem.with_name(stem.name + ".result.md")
    # The rules stay in a file; the brief goes to the agent, where the user can read it.
    if worker["turns"] == 0:
        rules = brief.with_name(f"{args.name}.rules.md")
        content = rules_text(cfg, worker["agent"], args.name, worker.get("tool"), root)
        if not args.dry_run:
            rules.write_text(content)
        lead = f"Your rules are in `{rules}`. Read them before you start."
    else:
        rules = Path(worker["rules"])
        lead = f"Your rules are in `{rules}`. Read them again if they are no longer in your context."
    text = (f"{lead}\n\n# Brief\n{brief.read_text().strip()}\n\n"
            f"# Result\nWrite your result to `{result}` in the result format from your rules.")
    turn, started = hc.prompt(args.name, worker["address"], text)
    if not args.dry_run:
        worker["turn"] = turn
        worker["sent_at"] = time.time()
        worker["turns"] += 1
        worker["rules"] = str(rules)
        worker["result"] = str(result)
        state["agents"][args.name] = worker
        save_state(root, state)
    print(json.dumps({"name": args.name, "rules": str(rules), "result": str(result), "started": started}))


def owned(root, name):
    state = load_state(root)
    if name not in state["agents"]:
        raise Fail(f"{name!r} was not spawned by agentcy; leave it alone")
    return state


def cmd_wait(args):
    """Wait for the first of the named agents to stop. A settled status means the agent stopped,
    not that it finished: the result file says that. `waiting` lists the agents still at work."""
    root = find_root(Path.cwd())
    names = list(dict.fromkeys(args.names))
    workers = {name: owned(root, name)["agents"][name] for name in names}
    if args.minutes <= 0:
        raise Fail("--minutes must be more than 0")

    def report(name):
        # Measured times, so reports of how long work took come from the clock.
        worker, info = workers[name], {"name": name}
        if worker.get("sent_at"):
            info["seconds_since_send"] = round(time.time() - worker["sent_at"])
        if worker.get("result"):
            info |= {"result": worker["result"], "result_exists": Path(worker["result"]).is_file()}
        return info

    started = time.monotonic()
    agents = [(name, workers[name]["address"], workers[name].get("turn", -1)) for name in names]
    name, status = backend(load(root), args.dry_run).wait(agents, args.minutes * 60)
    outcome = {**(report(name) if name else {}), "status": status,
               "waited_seconds": round(time.monotonic() - started),
               "waiting": [report(other) for other in names if other != name]}
    print(json.dumps(outcome))


def cmd_read(args):
    root = find_root(Path.cwd())
    worker = owned(root, args.name)["agents"][args.name]
    print(backend(load(root), args.dry_run).read(args.name, worker["address"], args.lines))


def cmd_list(args):
    root = find_root(Path.cwd())
    hc = backend(load(root), args.dry_run)
    rows = [{"name": name, **info, "status": hc.state(info["address"])[0]}
            for name, info in load_state(root)["agents"].items()]
    print(json.dumps(rows, indent=2))


def cmd_close(args):
    root = find_root(Path.cwd())
    state = owned(root, args.name)
    worker = state["agents"][args.name]
    stopped = backend(load(root), args.dry_run).stop(worker["address"])
    if not args.dry_run:
        del state["agents"][args.name]
        save_state(root, state)
    print(json.dumps({"closed": args.name, "stopped": stopped}))


# ---------------------------------------------------------------- images

def mime(path: Path) -> str:
    kind = mimetypes.guess_type(path.name)[0]
    if kind not in ("image/png", "image/jpeg", "image/webp"):
        raise Fail(f"{path}: use a .png, .jpg, or .webp input image")
    return kind


def gemini_request(model, prompt, inputs, aspect, size, kind="image"):
    """One Interactions request for nano banana images or Gemini Omni videos. Input images come first."""
    images = [{"type": "image", "mime_type": mime(p), "data": base64.b64encode(p.read_bytes()).decode()} for p in inputs]
    body = {"model": model, "input": images + [{"type": "text", "text": prompt}]}
    if aspect or size or kind == "video":
        size_key = "image_size" if kind == "image" else "resolution"
        body["response_format"] = {"type": kind, **({"aspect_ratio": aspect} if aspect else {}),
                                   **({size_key: size} if size else {})}
    return GEMINI_URL, "application/json", json.dumps(body).encode()


def openai_request(model, prompt, inputs, size, quality):
    fields = {"model": model, "prompt": prompt, **({"size": size} if size else {}),
              **({"quality": quality} if quality else {})}
    if not inputs:
        return OPENAI_URL + "generations", "application/json", json.dumps(fields).encode()
    boundary = uuid.uuid4().hex
    chunks = []
    for name, value in fields.items():
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for path in inputs:
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="{path.name}"\r\n'
                      f"Content-Type: {mime(path)}\r\n\r\n".encode() + path.read_bytes() + b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return OPENAI_URL + "edits", f"multipart/form-data; boundary={boundary}", b"".join(chunks)


def gemini_media(data, kind="image") -> list[bytes]:
    """Media blocks of `kind` from model_output steps, base64 in `data`."""
    scope = [s for s in data.get("steps", []) if s.get("type") == "model_output"]
    found = []

    def walk(value):
        if isinstance(value, dict):
            if value.get("type") == kind and isinstance(value.get("data"), str):
                found.append(base64.b64decode(value["data"]))
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(scope)
    if kind == "image" and not found and isinstance(data.get("output_image"), dict) and data["output_image"].get("data"):
        found.append(base64.b64decode(data["output_image"]["data"]))
    return found


def openai_images(data) -> list[bytes]:
    return [base64.b64decode(item["b64_json"]) for item in data.get("data", []) if item.get("b64_json")]


def cmd_media(args):
    kind, provider, model = args.command, args.provider, args.model
    prompt = Path(args.prompt_file).read_text().strip()
    inputs = [Path(p) for p in args.input]
    if provider == "gemini":
        url, content_type, body = gemini_request(model, prompt, inputs, args.aspect, args.size, kind)
    else:
        if args.aspect:
            raise Fail("openai takes --size WIDTHxHEIGHT, not --aspect")
        url, content_type, body = openai_request(model, prompt, inputs, args.size, args.quality)
    if args.dry_run:
        print(json.dumps({"url": url, "content_type": content_type.split(";")[0], "bytes": len(body), "model": model}))
        return
    key = os.environ.get(MEDIA_KEYS[provider])
    if not key:
        raise Fail(f"{MEDIA_KEYS[provider]} is not set in this environment")
    auth = {"x-goog-api-key": key} if provider == "gemini" else {"Authorization": f"Bearer {key}"}
    request = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": content_type, **auth})
    try:
        with urllib.request.urlopen(request, timeout=900) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as error:
        raise Fail(f"{provider} returned HTTP {error.code}: {error.read()[:2000].decode(errors='replace')}") from error
    except urllib.error.URLError as error:
        raise Fail(f"cannot reach {provider}: {error.reason}") from error
    found = gemini_media(data, kind) if provider == "gemini" else openai_images(data)
    if not found:
        raise Fail(f"{provider} returned no {kind}: {json.dumps(data)[:2000]}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    files = []
    for number, content in enumerate(found, 1):
        path = out if number == 1 else out.with_name(f"{out.stem}-{number}{out.suffix}")
        path.write_bytes(content)
        files.append(str(path.resolve()))
    print(json.dumps({"provider": provider, "model": model, "files": files}))


# ---------------------------------------------------------------- CLI

def parser():
    top = argparse.ArgumentParser(prog="agentcy.py", description=__doc__.splitlines()[0])
    top.add_argument("--dry-run", action="store_true", help="print backend commands or the image request; change nothing")
    sub = top.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help=f"create {HOME}/{CONFIG} in this folder").set_defaults(func=cmd_init)
    sub.add_parser("check", help="validate the config and show the team").set_defaults(func=cmd_check)
    p = sub.add_parser("options", help="print the numbered harness, model, and thinking choices for agents")
    p.add_argument("agents", nargs="*", metavar="agent", help="default: every agent")
    p.set_defaults(func=cmd_options)
    p = sub.add_parser("set", help=f"save the user's picks in {HOME}/{CONFIG}, creating it when missing")
    p.add_argument("pairs", nargs="+", metavar="agent answer", help="0, harness:model:thinking numbers, or names")
    p.set_defaults(func=cmd_set)
    p = sub.add_parser("run", help="create a run folder and print its path")
    p.add_argument("slug")
    p.add_argument("--review", action="store_true", help="save the current files as the review baseline")
    p.set_defaults(func=cmd_run)
    p = sub.add_parser("changes", help="compare current files, including new files, with a run's baseline")
    p.add_argument("run", help="the run folder created with --review")
    p.set_defaults(func=cmd_changes)
    p = sub.add_parser("spawn", help="start an agent in a new hc terminal, or give the T3 Code delegate_task call")
    p.add_argument("agent")
    p.add_argument("--tool", help="start the agent with one of its tools, for example an image tool")
    p.add_argument("--thread", help="T3 Code: record the subagent thread that delegate_task started")
    p.set_defaults(func=cmd_spawn)
    p = sub.add_parser("send", help="send a brief to an agent; the first one also writes its rules file")
    p.add_argument("name")
    p.add_argument("brief")
    p.set_defaults(func=cmd_send)
    p = sub.add_parser("handoff", help="give the user's request to an orchestrator spawned in its recorded setting")
    p.add_argument("name")
    p.add_argument("text", help="the user's arguments to /agentcy, unchanged")
    p.set_defaults(func=cmd_handoff)
    p = sub.add_parser("wait", help="wait until the first of the named agents settles")
    p.add_argument("names", nargs="+", metavar="name")
    p.add_argument("--minutes", type=float, default=8, help="how long to wait, in minutes (default 8)")
    p.set_defaults(func=cmd_wait)
    p = sub.add_parser("read", help="read an agent's recent terminal output or thread messages")
    p.add_argument("name")
    p.add_argument("--lines", type=int, default=80)
    p.set_defaults(func=cmd_read)
    sub.add_parser("list", help="list agents agentcy started").set_defaults(func=cmd_list)
    p = sub.add_parser("close", help="stop an agent agentcy started and forget it")
    p.add_argument("name")
    p.set_defaults(func=cmd_close)
    for kind, providers, size in (("image", sorted(MEDIA_KEYS), "gemini: 1K, 2K, 4K; openai: WIDTHxHEIGHT"),
                                  ("video", ["gemini"], "360p, 720p, 1080p, 4k")):
        p = sub.add_parser(kind, help=f"generate a {kind} through an API, paid per call")
        p.add_argument("--provider", required=True, choices=providers)
        p.add_argument("--model", required=True, help="from the agent's api tool settings in agentcy.json")
        p.add_argument("--prompt-file", required=True)
        p.add_argument("--out", required=True)
        p.add_argument("--input", action="append", default=[], help="input image (.png, .jpg, .webp); repeatable")
        p.add_argument("--aspect", help="gemini only: for example 16:9 or 9:16")
        p.add_argument("--size", help=size)
        if kind == "image":
            p.add_argument("--quality", help="openai only: low, medium, high, auto")
        p.set_defaults(func=cmd_media)
    return top


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if not args.dry_run and args.command in ("set", "spawn", "send", "handoff", "close"):
            with state_lock(find_root(Path.cwd())):
                args.func(args)
        else:
            args.func(args)
    except Fail as error:
        print(f"agentcy: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
