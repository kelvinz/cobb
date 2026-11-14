"""Deterministic tests for skills/agentcy/scripts/agentcy.py. A fake hc, t3, and pi; no agent or API calls."""
import base64
from concurrent.futures import ThreadPoolExecutor
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

sys.dont_write_bytecode = True  # keep the skill folder free of caches
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/agentcy/scripts/agentcy.py"
spec = importlib.util.spec_from_file_location("agentcy", SCRIPT)
agentcy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agentcy)

# A fake hc. It logs each call and rebuilds its terminals from the log: each `run` makes t1, t2, ...
FAKE_HC = textwrap.dedent("""\
    #!/usr/bin/env python3
    import json, os, sys, time
    args = sys.argv[1:]
    env = os.environ.get
    log = env("FAKE_HC_LOG")
    with open(log, "a") as handle:
        handle.write(json.dumps(args) + "\\n")
    command = args[0]
    target = args[2] if len(args) > 2 else None

    def fail(kind, code=1):
        error = {"kind": kind, "message": env("FAKE_HC_MESSAGE", kind), "hint": ""}
        print(json.dumps({"error": error}), file=sys.stderr)
        sys.exit(code)

    if command == "run":
        time.sleep(float(env("FAKE_HC_RUN_DELAY", "0")))
    if command == env("FAKE_HC_FAIL"):
        fail(env("FAKE_HC_KIND", "failed"))
    calls = [json.loads(line) for line in open(log)]
    terminals = {}
    for call in calls:
        if call[0] == "run":
            address = f"t{len(terminals) + 1}"
            terminals[address] = {"address": address, "name": call[call.index("--name") + 1], "state": "live"}
        elif call[0] == "kill" and call[2] in terminals:
            terminals[call[2]]["state"] = "finished"
        elif call[0] == "rm":
            terminals.pop(call[2], None)
    for address in (env("FAKE_HC_GONE") or "").split():
        terminals.pop(address, None)
    for address in (env("FAKE_HC_FINISHED") or "").split():
        if address in terminals:
            terminals[address]["state"] = "finished"
    terminal = next((t for t in terminals.values() if target in (t["address"], t["name"])), None)
    status = env(f"FAKE_HC_STATUS_{target}", env("FAKE_HC_STATUS", "idle"))
    sends = sum(call[0] == "send" and call[2] == target for call in calls)
    if command == "get" and target == "t0":  # the session's own terminal
        out = {"address": "t0", "state": "live", "foreground": {"name": "claude"}, "labels": {"herdr.space": "sp1"}}
    elif command in ("get", "send", "wait", "read") and terminal is None:
        fail("not_found", 3)
    elif command == "get":
        out = {**terminal, "status": None if status == "none" else {"state": status},
               "turn": max(0, sends - int(env("FAKE_HC_LAG", "0")))}
    elif command == "send":
        if status == "blocked":
            fail("blocked", 9)
        out = {"turn": sends - 1, "started": env("FAKE_HC_STARTED", "1") == "1", "status": "idle"}
    elif command == "wait":
        if env("FAKE_HC_EXIT"):
            out = {"ended": True, "reason": "exit", "exit_code": 1, "status": None}
        elif status == "none":
            out = {"ended": False, "reason": "timeout", "status": None}
        else:
            out = {"ended": True, "reason": "status", "status": status}
    elif command == "run":
        out = list(terminals.values())[-1]
    elif command == "ls":
        out = {"terminals": list(terminals.values()) + json.loads(env("FAKE_HC_LIVE", "[]"))}
    elif command == "read":
        out = {"text": "screen text", "complete": True, "how": "history"}
    else:
        out = {}
    print(json.dumps(out))
""")

# A fake `t3`. It logs each call and rebuilds its threads from the log. The subagent threads child1 and
# child2 of mcp:self exist with one run each; each send adds a run. FAKE_T3_STATUS sets every status.
FAKE_T3 = textwrap.dedent("""\
    #!/usr/bin/env python3
    import json, os, sys
    args = sys.argv[2:]  # after "thread"
    env = os.environ.get
    log = env("FAKE_T3_LOG")
    with open(log, "a") as handle:
        handle.write(json.dumps(args) + "\\n")
    command, target = args[0], args[1] if len(args) > 1 else None
    if command == env("FAKE_T3_FAIL"):
        print("Could not reach the T3 Code server.", file=sys.stderr)
        sys.exit(1)
    calls = [json.loads(line) for line in open(log)]
    runs = {"child1": 1, "child2": 1}
    for call in calls:
        if call[0] == "send" and call[1] in runs:
            runs[call[1]] += 1
    for thread in (env("FAKE_T3_GONE") or "").split():
        runs.pop(thread, None)

    def thread(thread_id, provider="pi", model="zai/glm-5.3-flash"):
        return {"threadId": thread_id, "status": env("FAKE_T3_STATUS", "completed"), "runCount": runs.get(thread_id, 1),
                "pendingRequestCount": int(env("FAKE_T3_PENDING", "0")), "archived": False,
                "parentThreadId": env("FAKE_T3_PARENT", "mcp:self"), "relationshipToParent": "subagent",
                "providerInstanceId": provider, "model": model, "link": f"https://t3.test/{thread_id}"}

    if command == "list":
        if env("FAKE_T3_NO_PROJECT"):
            print("No T3 Code project matches '.'. Pass a project id or a path inside a project.")
            sys.exit(0)
        out = []
    elif command == "show" and target == "mcp:self":  # the session's own thread
        out = {"thread": thread(target, "claudeAgent", "claude-opus-5-5"), "messages": []}
    elif command in ("show", "send") and target not in runs:
        print(f"Thread {target} is no longer available.", file=sys.stderr)
        sys.exit(1)
    elif command == "show":
        out = {"thread": thread(target), "messages": [{"role": "assistant", "text": "result written"}]}
    else:
        out = {"threadId": target, "status": "starting", "delivery": env("FAKE_T3_DELIVERY", "started")}
    print(json.dumps(out))
""")

# A fake pi that lists its models offline, as `pi --offline --list-models` does.
FAKE_PI = textwrap.dedent("""\
    #!/bin/sh
    printf 'provider      model           context\\n'
    for model in openai-codex/gpt-6-astra openai-codex/gpt-6-luna openai-codex/gpt-6.1-sol zai/glm-5.3-flash; do
      printf '%s  %s  272K\\n' "${model%%/*}" "${model#*/}"
    done
""")


class Project(unittest.TestCase):
    """A temporary project with agentcy initialised, and a fake hc and pi first on PATH."""
    INIT = True

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agentcy-test-")
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        bin_dir = Path(self.temp.name) / "bin"
        bin_dir.mkdir()
        for name, text in (("hc", FAKE_HC), ("pi", FAKE_PI), ("t3", FAKE_T3)):
            (bin_dir / name).write_text(text)
            (bin_dir / name).chmod(0o755)
        self.log = Path(self.temp.name) / "hc.log"
        self.t3_log = Path(self.temp.name) / "t3.log"
        self.env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                    "FAKE_HC_LOG": str(self.log), "SHELL": "/bin/sh"}  # agents start as given; see test_login
        for key in ([k for k in self.env if k.startswith(("FAKE_HC_", "FAKE_T3_", "HC_", "T3CODE_"))]
                    + ["GEMINI_API_KEY", "OPENAI_API_KEY"]):
            if key != "FAKE_HC_LOG":
                self.env.pop(key, None)
        self.env["FAKE_T3_LOG"] = str(self.t3_log)
        self.env["CODEX_HOME"] = str(Path(self.temp.name) / "codex-home")  # never the user's model cache
        (Path(self.temp.name) / "codex-home").mkdir()
        if self.INIT:
            self.assertEqual(self.cli("init").returncode, 0)
            # Runtime tests use an already-configured team; setup tests below start without settings.
            self.config(lambda cfg: cfg.update(agentcy.template()))

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, *args, env=None):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], cwd=self.root,
                              env={**self.env, **(env or {})}, capture_output=True, text=True)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def started(self):
        """The argv after `--` of each `hc run`: the harness and its flags."""
        return [c[c.index("--") + 1:] for c in self.calls() if c[0] == "run"]

    def state(self):
        return json.loads((self.root / "agentcy/state.json").read_text())

    def config(self, change):
        path = self.root / "agentcy/agentcy.json"
        cfg = json.loads(path.read_text())
        change(cfg)
        path.write_text(json.dumps(cfg))

    def check(self, env=None):
        done = self.cli("check", env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)


class Discovery(unittest.TestCase):
    def test_pi_discovery_failure_is_bounded_and_leaves_models_unknown(self):
        for error in (OSError("cannot start pi"), subprocess.TimeoutExpired("pi", 10)):
            with self.subTest(error=type(error).__name__):
                agentcy.pi_models.cache_clear()
                try:
                    with mock.patch.object(agentcy.shutil, "which", return_value="pi"), \
                            mock.patch.object(agentcy.subprocess, "run", side_effect=error) as run:
                        self.assertIsNone(agentcy.pi_models())
                        run.assert_called_once_with(["pi", "--offline", "--list-models"],
                                                    capture_output=True, text=True, timeout=10)
                finally:
                    agentcy.pi_models.cache_clear()


class LabLauncher(unittest.TestCase):
    def test_lab_launch_passes_harness_settings(self):
        spec = importlib.util.spec_from_file_location("agentcy_lab", ROOT / "tests/agentcy_lab.py")
        lab_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lab_module)
        with tempfile.TemporaryDirectory() as temp:
            hc = mock.Mock()
            hc.live_names.return_value = set()
            hc.spawn.return_value = ("t1", "ready")
            with mock.patch.object(sys, "argv", ["agentcy_lab.py", "--harness", "pi"]), \
                    mock.patch.object(lab_module.tempfile, "mkdtemp", return_value=temp), \
                    mock.patch.object(lab_module, "make_lab"), \
                    mock.patch.object(lab_module.agentcy, "Hc", return_value=hc), \
                    contextlib.redirect_stdout(io.StringIO()):
                lab_module.main()
            hc.spawn.assert_called_once_with("lab-1", {"harness": "pi"}, Path(temp).resolve(), own_tab=True)


class InitAndCheck(Project):
    def test_init_creates_config_and_home_once(self):
        self.assertTrue((self.root / "agentcy/agentcy.json").is_file())
        self.assertEqual((self.root / "agentcy/.gitignore").read_text(), "runs/\nstate.json\nstate.tmp\n")
        self.assertEqual(sorted(p.name for p in (self.root / "agentcy").iterdir()), [".gitignore", "agentcy.json"])
        before = (self.root / "agentcy/agentcy.json").read_bytes()
        again = self.cli("init")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertFalse(json.loads(again.stdout)["created"])
        self.assertEqual((self.root / "agentcy/agentcy.json").read_bytes(), before)

    def test_check_shows_the_default_cast(self):
        report = self.check()
        names = {row["name"]: row for row in report["agents"]}
        self.assertEqual(set(names), {"donna", "arya", "trinity", "skyler", "amy", "hermione", "edna", "robin"})
        self.assertEqual(names["robin"]["role"], "video")
        self.assertEqual(set(report["lessons"]), set(names))
        self.assertEqual((names["trinity"]["harness"], names["trinity"]["model"], names["trinity"]["effort"]),
                         ("pi", "openai-codex/gpt-6.1-sol", "high"))
        self.assertEqual((names["donna"]["harness"], names["donna"]["model"]), ("pi", "openai-codex/gpt-6-astra"))
        self.assertEqual(set(names["edna"]["tools"]), {"codex", "antigravity", "api"})
        self.assertEqual(names["edna"]["tools"]["antigravity"]["harness"], "agy")
        self.assertIsInstance(names["edna"]["tools"]["antigravity"]["installed"], bool)
        self.assertEqual(report["api_keys"], {"GEMINI_API_KEY": False, "OPENAI_API_KEY": False})
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["backend"], {"name": "hc", "ready": True, "problem": None, "not_applied": []})
        self.assertEqual(report["session"], {"harness": None, "model": None, "inside": None})
        self.assertEqual(self.check({"HC_TERMINAL_ID": "t0"})["session"],
                         {"harness": "claude", "model": None, "inside": "hc"})
        down = self.check({"HC_TERMINAL_ID": "t0", "FAKE_HC_FAIL": "server"})
        self.assertEqual((down["backend"]["ready"], down["session"]["harness"]), (False, None))

    def test_check_finds_the_root_from_a_subfolder(self):
        (self.root / "src").mkdir()
        done = subprocess.run([sys.executable, "-I", str(SCRIPT), "check"], cwd=self.root / "src",
                              env=self.env, capture_output=True, text=True)
        self.assertEqual(json.loads(done.stdout)["root"], str(self.root.resolve()))

    def test_invalid_config_lists_every_error(self):
        def break_it(cfg):
            cfg["backend"] = "herdr"
            cfg["agents"]["odd"] = {"role": "worker", "use": "x", "harness": "gemini", "model": "m", "character": "X"}
            cfg["agents"]["Bad Name"] = {"role": "worker", "use": "x", "harness": "claude", "character": "X"}
            del cfg["agents"]["arya"]["harness"]
            del cfg["agents"]["amy"]["use"]
            cfg["agents"]["edna"]["tools"]["broken"] = {"harness": "codex"}
            cfg["agents"]["boss"] = {"role": "orchestrator", "character": "Y"}
            cfg["agents"]["trinity"]["model"] = 5
            cfg["agents"]["edna"]["tools"]["codex"]["effort"] = ["medium"]
        self.config(break_it)
        done = self.cli("check")
        self.assertEqual(done.returncode, 1)
        for text in ("backend: use one of auto, hc, t3", "agents.odd: agentcy knows no model/effort flags for gemini",
                     "agents.Bad Name: names use", "agents.arya: harness is missing", "agents.amy: use is missing",
                     "agents.edna.tools.broken: use is missing", "exactly one agent needs role orchestrator",
                     "agents.trinity: model must be a string", "agents.edna.tools.codex: effort must be a string"):
            self.assertIn(text, done.stderr)


    def test_check_warns_about_models_pi_does_not_list(self):
        self.config(lambda cfg: [cfg["agents"][name].update(model="zai/glm-9") for name in ("arya", "amy")])
        report = self.check()
        rows = {row["name"]: row for row in report["agents"]}
        self.assertFalse(rows["arya"]["model_listed"])
        self.assertTrue(rows["trinity"]["model_listed"])
        self.assertIsNone(rows["skyler"]["model_listed"])  # claude cannot list its models offline
        self.assertEqual(report["warnings"], ["arya: pi does not list model zai/glm-9",
                                              "amy: pi does not list model zai/glm-9"])


class LaunchArgs(unittest.TestCase):
    def test_flags_per_harness(self):
        self.assertEqual(agentcy.launch_args({"harness": "claude", "model": "opus", "effort": "high"}),
                         ["--model", "opus", "--effort", "high"])
        self.assertEqual(agentcy.launch_args({"harness": "codex", "model": "gpt-6", "effort": "low"}),
                         ["--model", "gpt-6", "-c", "model_reasoning_effort=low", "--no-daemon"])
        self.assertEqual(agentcy.launch_args({"harness": "pi", "model": "glm", "effort": "max", "args": ["--x"]}),
                         ["--model", "glm", "--thinking", "max", "--x"])
        self.assertEqual(agentcy.launch_args({"harness": "agy", "model": "gemini-3.8-flash-high", "effort": "high"}),
                         ["--model", "gemini-3.8-flash-high", "--effort", "high"])

    def test_auto_approve_adds_each_harness_mode(self):
        def auto(harness):
            return agentcy.launch_args({"harness": harness, "approve": "auto", "args": ["--x"]})
        self.assertEqual(auto("claude"), ["--permission-mode", "auto", "--x"])
        self.assertEqual(auto("codex"), ["--approve-for-me", "--no-daemon", "--x"])
        self.assertEqual(auto("agy"), ["--mode", "auto", "--x"])
        self.assertEqual(auto("pi"), ["--x"])
        self.assertEqual(agentcy.launch_args({"harness": "claude", "approve": "ask"}), [])
        self.assertEqual(agentcy.launch_errors("a", {"harness": "claude", "approve": "yes"}), ["a: approve must be one of ask, auto"])
        self.assertEqual(agentcy.launch_errors("a", {"harness": "omp", "approve": "auto"}),
                         ["a: agentcy knows no auto mode for omp; put its flag in args"])

    def test_a_tool_with_a_harness_replaces_the_launch(self):
        agent = {"harness": "claude", "model": "sonnet", "effort": "medium", "args": ["--x"],
                 "tools": {"codex": {"use": "u", "harness": "codex", "effort": "low"},
                           "deep": {"use": "u", "effort": "high"},
                           "api": {"use": "u", "provider": "gemini"}}}
        self.assertEqual(agentcy.launch(agent, "codex"), {"harness": "codex", "effort": "low"})
        self.assertEqual(agentcy.launch(agent, "deep"), {"harness": "claude", "model": "sonnet", "effort": "high", "args": ["--x"]})
        self.assertEqual(agentcy.launch(agent, "api"), agentcy.launch(agent))
        agent["approve"] = "auto"
        self.assertEqual(agentcy.launch(agent, "codex"), {"harness": "codex", "effort": "low", "approve": "auto"})
        agent["tools"]["codex"]["approve"] = "ask"
        self.assertEqual(agentcy.launch(agent, "codex")["approve"], "ask")

    def test_default_values_leave_the_harness_setting(self):
        self.assertEqual(agentcy.launch_args({"harness": "claude", "model": "default", "effort": ""}), [])
        self.assertEqual(agentcy.launch_args({"harness": "omp", "args": ["--model", "m"]}), ["--model", "m"])


class SpawnSendClose(Project):
    def brief(self, name="brief.md", text="Do the work.\n"):
        path = self.root / name
        path.write_text(text)
        return str(path)

    def test_spawn_starts_the_harness_under_this_session(self):
        done = self.cli("spawn", "arya")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)["status"], "ready")
        run, wait = self.calls()[-2:]
        self.assertEqual(run, ["run", "--json", "--bg", "--no-notify", "--name", "arya", "--cwd", str(self.root.resolve()),
                               "--", "pi", "--model", "zai/glm-5.3-flash", "--thinking", "max"])
        self.assertEqual(wait, ["wait", "--json", "t1", "--timeout", str(agentcy.START_SECONDS)])
        self.assertEqual(self.state()["agents"]["arya"]["address"], "t1")

    def test_image_tools_choose_the_harness(self):
        def start(*args):
            done = self.cli("spawn", "edna", *args)
            self.assertEqual(done.returncode, 0, done.stderr)
            return json.loads(done.stdout), self.started()[-1]
        self.assertEqual(start("--tool", "codex")[1],
                         ["codex", "-c", "model_reasoning_effort=medium", "--approve-for-me", "--no-daemon"])
        out, argv = start("--tool", "antigravity")
        self.assertEqual((out["name"], out["tool"], argv), ("edna2", "antigravity", ["agy", "--mode", "auto"]))
        self.assertEqual(start("--tool", "api")[1], ["codex", "--model", "gpt-6-luna", "-c", "model_reasoning_effort=max",
                                                  "--approve-for-me", "--no-daemon"])
        run = Path(self.cli("run", "art").stdout.strip())
        (run / "edna3-1.md").write_text("Make a hero image.\n")
        prompt = Path(json.loads(self.cli("send", "edna3", str(run / "edna3-1.md")).stdout)["rules"]).read_text()
        self.assertIn("Tool: `api` — Gemini or OpenAI image API, paid per image with an API key. Settings: "
                      '{"provider": "gemini", "models": {"gemini": "gemini-nano-banana-2.1", "openai": "gpt-image-2.6-flare"}}', prompt)
        self.assertIn("Harness: codex, model gpt-6-luna.", prompt)

    def test_login_shells_start_agents_with_the_user_environment(self):
        # hc gives programs the login session's PATH; zsh and bash add the rest from their startup files.
        for shell in ("/bin/zsh", "/usr/local/bin/bash"):
            with self.subTest(shell=shell):
                done = self.cli("spawn", "arya", env={"SHELL": shell})
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertEqual(self.started()[-1], [shell, "-lic", 'exec "$0" "$@"',
                                                      "pi", "--model", "zai/glm-5.3-flash", "--thinking", "max"])
        for shell in ("/usr/bin/fish", ""):
            with self.subTest(shell=shell), mock.patch.dict(os.environ, {"SHELL": shell}):
                self.assertEqual(agentcy.login(["pi", "--x"]), ["pi", "--x"])

    def test_unknown_tool_is_refused_before_any_call(self):
        done = self.cli("spawn", "edna", "--tool", "video")
        self.assertEqual(done.returncode, 1)
        self.assertIn("edna has no tool 'video'; tools: codex, antigravity, api", done.stderr)
        self.assertEqual(self.calls(), [])

    def test_a_second_spawn_gets_a_numbered_name(self):
        self.cli("spawn", "arya")
        done = self.cli("spawn", "arya")
        self.assertEqual((json.loads(done.stdout)["name"], self.state()["agents"]["arya2"]["address"]), ("arya2", "t2"))

    def test_a_live_hc_name_is_not_reused(self):
        done = self.cli("spawn", "arya", env={"FAKE_HC_LIVE": json.dumps([{"name": "arya", "address": "t9"}])})
        self.assertEqual(json.loads(done.stdout)["name"], "arya2")

    def test_a_copy_skips_the_name_of_another_agent(self):
        self.config(lambda cfg: cfg["agents"].__setitem__("arya2", dict(cfg["agents"]["arya"])))
        self.cli("spawn", "arya")
        self.assertEqual(json.loads(self.cli("spawn", "arya").stdout)["name"], "arya3")

    def test_a_copy_of_a_name_that_ends_in_a_digit_gets_an_underscore(self):
        self.config(lambda cfg: cfg["agents"].__setitem__("gpt5", dict(cfg["agents"]["arya"])))
        self.assertEqual([json.loads(self.cli("spawn", "gpt5").stdout)["name"] for _ in range(3)],
                         ["gpt5", "gpt5_2", "gpt5_3"])

    def test_a_copy_stops_when_its_name_becomes_another_agent(self):
        for _ in range(2):
            self.cli("spawn", "arya")
        self.config(lambda cfg: cfg["agents"].__setitem__("arya2", dict(cfg["agents"]["trinity"])))
        done = self.cli("send", "arya2", self.brief())
        self.assertEqual(done.returncode, 1)
        self.assertIn("arya2 is a copy of arya, but agentcy.json now has an agent named arya2", done.stderr)
        self.assertNotIn("send", [c[0] for c in self.calls()])
        self.assertEqual(self.cli("send", "arya", self.brief()).returncode, 0)
        self.assertEqual(self.cli("close", "arya2").returncode, 0)
        self.assertEqual(json.loads(self.cli("spawn", "arya2").stdout)["name"], "arya2")
        self.assertEqual(self.started()[-1][:3], ["pi", "--model", "openai-codex/gpt-6.1-sol"])

    def test_copies_of_one_agent_work_in_parallel(self):
        run = Path(self.cli("run", "copies").stdout.strip())
        sent = {}
        for name in ("arya", "arya2"):
            self.assertEqual(json.loads(self.cli("spawn", "arya").stdout)["name"], name)
            (run / f"{name}-1.md").write_text(f"Work for {name}.\n")
            sent[name] = json.loads(self.cli("send", name, str(run / f"{name}-1.md")).stdout)
        self.assertEqual({n: Path(s["rules"]).name for n, s in sent.items()},
                         {"arya": "arya.rules.md", "arya2": "arya2.rules.md"})
        self.assertEqual({n: Path(s["result"]).name for n, s in sent.items()},
                         {"arya": "arya-1.result.md", "arya2": "arya2-1.result.md"})
        self.assertIn("Your team name is `arya2`.", Path(sent["arya2"]["rules"]).read_text())
        self.assertEqual({a["agent"] for a in self.state()["agents"].values()}, {"arya"})
        # Arya (t1) still works; her copy (t2) has finished.
        waited = json.loads(self.cli("wait", "arya", "arya2", env={"FAKE_HC_STATUS_t1": "working"}).stdout)
        self.assertEqual((waited["name"], [w["name"] for w in waited["waiting"]]), ("arya2", ["arya"]))

    def test_a_startup_question_keeps_the_agent_for_the_user(self):
        # agy reports blocked at its trust question; Claude Code and Codex report nothing until it is answered.
        for status, shown in (("blocked", "blocked"), ("none", "starting")):
            with self.subTest(status=status):
                done = self.cli("spawn", "skyler", env={"FAKE_HC_STATUS": status})
                self.assertEqual(done.returncode, 0, done.stderr)
                out = json.loads(done.stdout)
                self.assertEqual(out["status"], shown)
                self.assertIn(out["name"], self.state()["agents"])
        self.assertNotIn("kill", [c[0] for c in self.calls()])

    def test_failed_start_records_nothing(self):
        done = self.cli("spawn", "trinity", env={"FAKE_HC_FAIL": "run", "FAKE_HC_MESSAGE": "spawn_failed: no such program"})
        self.assertEqual(done.returncode, 1)
        self.assertIn("spawn_failed: no such program", done.stderr)
        self.assertFalse((self.root / "agentcy/state.json").exists())

    def test_a_damaged_state_file_is_a_clear_error(self):
        for text in ("{", "[]"):
            with self.subTest(text=text):
                (self.root / "agentcy/state.json").write_text(text)
                done = self.cli("list")
                self.assertEqual(done.returncode, 1)
                self.assertIn("agentcy/state.json: ", done.stderr)
                self.assertNotIn("Traceback", done.stderr)

    def test_an_agent_that_exits_at_start_is_removed(self):
        done = self.cli("spawn", "trinity", env={"FAKE_HC_EXIT": "1"})
        self.assertEqual(done.returncode, 1)
        self.assertIn("trinity exited at start (code 1): screen text", done.stderr)
        self.assertEqual(self.calls()[-1], ["rm", "--json", "t1"])
        self.assertFalse((self.root / "agentcy/state.json").exists())

    def test_a_failed_wait_at_start_removes_the_terminal(self):
        done = self.cli("spawn", "arya", env={"FAKE_HC_FAIL": "wait", "FAKE_HC_KIND": "unavailable"})
        self.assertEqual(done.returncode, 1)
        self.assertIn("hc wait", done.stderr)
        self.assertEqual([c[0] for c in self.calls()][-2:], ["kill", "rm"])
        self.assertFalse((self.root / "agentcy/state.json").exists())

    def test_an_orchestrator_without_a_launch_is_this_session(self):
        self.config(lambda cfg: [cfg["agents"]["donna"].pop(key) for key in agentcy.LAUNCH])
        done = self.cli("spawn", "donna")
        self.assertEqual(done.returncode, 1)
        self.assertIn("the orchestrator runs in this session", done.stderr)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.check()["agents"][0]["harness"], "(this session)")

    def test_handoff_starts_the_orchestrator_in_its_own_tab(self):
        done = self.cli("spawn", "donna", env={"HC_TERMINAL_ID": "t0"})
        self.assertEqual(done.returncode, 0, done.stderr)
        run = next(c for c in self.calls() if c[0] == "run")
        self.assertIn("--no-parent", run)
        labels = [run[i + 1] for i, arg in enumerate(run) if arg == "--label"]
        self.assertEqual(labels[0], "herdr.space=sp1")
        self.assertRegex(labels[1], r"^herdr\.tab=tb[0-9a-f]{32}$")
        self.assertEqual(run[run.index("--") + 1:], ["pi", "--model", "openai-codex/gpt-6-astra", "--thinking", "medium"])
        done = self.cli("handoff", "donna", "add a cart to the page")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(json.loads(done.stdout)["started"])
        send = self.calls()[-1]
        self.assertEqual(send[:3], ["send", "--json", "t1"])
        self.assertIn(f"Read {agentcy.SKILL / 'SKILL.md'} and follow it with these arguments: add a cart to the page", send[3])
        self.assertIn("skip the session check", send[3])
        self.cli("spawn", "arya")
        refused = self.cli("handoff", "arya", "x")
        self.assertEqual(refused.returncode, 1)
        self.assertIn("arya is not the orchestrator", refused.stderr)

    def test_a_worker_outside_hc_gets_no_labels(self):
        self.cli("spawn", "arya", env={"HC_TERMINAL_ID": "t0"})
        self.cli("spawn", "donna")
        for call in (c for c in self.calls() if c[0] == "run"):
            self.assertNotIn("--label", call)

    def test_handoff_refuses_an_agent_removed_from_the_config(self):
        self.cli("spawn", "donna")
        self.config(lambda cfg: cfg["agents"].update(harvey=cfg["agents"].pop("donna")))
        done = self.cli("handoff", "donna", "add a cart")
        self.assertEqual(done.returncode, 1)
        self.assertIn("agent 'donna' is no longer in agentcy.json", done.stderr)

    def test_send_refuses_the_orchestrator(self):
        self.assertEqual(self.cli("spawn", "donna").returncode, 0)
        brief = self.root / "brief.md"
        brief.write_text("# Goal\nx\n")
        done = self.cli("send", "donna", str(brief))
        self.assertEqual(done.returncode, 1)
        self.assertIn("use handoff", done.stderr)

    def test_send_puts_the_brief_in_the_terminal_and_the_rules_in_a_file(self):
        self.cli("spawn", "arya")
        run = Path(self.cli("run", "rename").stdout.strip())
        (run / "arya-1.md").write_text("# Goal\nRename foo to bar.\n")
        first = json.loads(self.cli("send", "arya", str(run / "arya-1.md")).stdout)
        rules = run / "arya.rules.md"
        self.assertEqual((first["rules"], first["started"]), (str(rules), True))
        for text in ("# You are Arya Stark (Game of Thrones), the agentcy worker",
                     "Donna Paulsen, the orchestrator, sends your briefs here",
                     "# Team rules", "# Role: worker"):
            self.assertIn(text, rules.read_text())
        call = self.calls()[-1]
        self.assertEqual((call[:3], len(call)), (["send", "--json", "t1"], 4))
        for text in (f"Your rules are in `{rules}`. Read them before you start.", "# Brief\n# Goal\nRename foo to bar.",
                     str(run / "arya-1.result.md")):
            self.assertIn(text, call[3])
        self.assertNotIn("# Team rules", call[3])

        (run / "arya-2.md").write_text("# Goal\nNow the tests.\n")
        second = json.loads(self.cli("send", "arya", str(run / "arya-2.md"), env={"FAKE_HC_STARTED": "0"}).stdout)
        self.assertFalse(second["started"])
        text = self.calls()[-1][3]
        self.assertIn("Now the tests.", text)
        self.assertIn(f"`{rules}`. Read them again", text)
        self.assertNotIn("# Team rules", text)
        self.assertNotIn("Rename foo", rules.read_text())
        self.assertEqual((self.state()["agents"]["arya"]["turns"], self.state()["agents"]["arya"]["turn"]), (2, 1))

    def test_send_refuses_an_agent_waiting_on_a_question(self):
        self.cli("spawn", "arya")
        saved = (self.root / "agentcy/state.json").read_bytes()
        done = self.cli("send", "arya", self.brief(), env={"FAKE_HC_STATUS": "blocked"})
        self.assertEqual(done.returncode, 1)
        self.assertIn("arya is waiting on a question in its terminal; run `read arya`", done.stderr)
        self.assertEqual((self.root / "agentcy/state.json").read_bytes(), saved)

    def test_agent_lessons_join_the_rules_and_check_flags_size(self):
        lessons = self.root / "agentcy/lessons/arya.md"
        lessons.parent.mkdir()
        lessons.write_text("# Arya Stark lessons\n\n- Name the schema file in api briefs (run-1)\n")
        run = Path(self.cli("run", "x").stdout.strip())
        def first(agent):
            self.cli("spawn", agent)
            (run / f"{agent}-1.md").write_text("Do it.\n")
            return Path(json.loads(self.cli("send", agent, str(run / f"{agent}-1.md")).stdout)["rules"]).read_text()
        prompt = first("arya")
        self.assertIn("# Your lessons", prompt)
        self.assertIn("- Name the schema file in api briefs (run-1)", prompt)
        self.assertNotIn("# Arya Stark lessons", prompt)
        self.assertLess(prompt.index("# Role: worker"), prompt.index("# Your lessons"))
        self.assertNotIn("# Your lessons", first("trinity"))  # same role, own lessons
        lessons.write_text("x" * (agentcy.LESSON_LIMIT + 1))
        report = self.check()["lessons"]
        self.assertTrue(report["arya"]["over_limit"])
        self.assertEqual(report["donna"]["chars"], 0)

    def test_check_counts_feedback_waiting_for_the_learner(self):
        self.assertEqual(self.check()["feedback"]["waiting"], 0)
        (self.root / "agentcy/feedback.md").write_text("# Feedback\n\n- a\n- b\n")
        self.assertEqual(self.check()["feedback"]["waiting"], 2)

    def test_command_words_are_not_agent_names(self):
        self.config(lambda cfg: cfg["agents"].update(learn={"role": "worker", "use": "x", "harness": "claude", "character": "X"}))
        self.assertIn("agents.learn: learn is a command word", self.cli("check").stderr)

    def test_image_role_gets_the_script_command(self):
        self.cli("spawn", "edna")
        run = Path(self.cli("run", "hero").stdout.strip())
        (run / "edna-1.md").write_text("A hero image.\n")
        prompt = Path(json.loads(self.cli("send", "edna", str(run / "edna-1.md")).stdout)["rules"]).read_text()
        self.assertIn(f"python3 {SCRIPT} image --provider <provider>", prompt)
        self.assertNotIn("{agentcy}", prompt)

    def test_role_commands_quote_a_path_with_a_space(self):
        with tempfile.TemporaryDirectory(prefix="agentcy test ") as temp:
            skill = Path(temp) / "My Site" / "agentcy"
            shutil.copytree(agentcy.SKILL / "references", skill / "references")
            with mock.patch.object(agentcy, "SKILL", skill):
                text = agentcy.role_text("image")
        line = next(line for line in text.splitlines() if " image --provider" in line)
        self.assertEqual(shlex.split(line)[:3], ["python3", str(skill / "scripts/agentcy.py"), "image"])

    def test_commands_refuse_agents_agentcy_did_not_start(self):
        for command in (["close", "stranger"], ["wait", "stranger"], ["read", "stranger"]):
            done = self.cli(*command)
            self.assertEqual(done.returncode, 1)
            self.assertIn("not spawned by agentcy", done.stderr)
        self.assertEqual(self.calls(), [])

    def test_an_ended_agent_cannot_receive_commands(self):
        for name in ("arya", "donna"):
            self.assertEqual(self.cli("spawn", name).returncode, 0)
        state = (self.root / "agentcy/state.json").read_bytes()
        for key in ("FAKE_HC_GONE", "FAKE_HC_FINISHED"):  # removed from hc, or its program ended
            for command in (("send", "arya", self.brief()), ("handoff", "donna", "do the work"), ("read", "arya")):
                with self.subTest(key=key, command=command[0]):
                    before = len(self.calls())
                    done = self.cli(*command, env={key: "t1 t2"})
                    self.assertEqual(done.returncode, 1, done.stdout)
                    self.assertIn("is no longer running in t", done.stderr)
                    self.assertTrue(all(c[0] == "get" for c in self.calls()[before:]))
                    self.assertEqual((self.root / "agentcy/state.json").read_bytes(), state)
            self.assertEqual(json.loads(self.cli("wait", "arya", env={key: "t1"}).stdout)["status"], "gone")
            listed = json.loads(self.cli("list", env={key: "t1"}).stdout)
            self.assertEqual({row["name"]: row["status"] for row in listed}, {"arya": "gone", "donna": "idle"})
        self.assertFalse((self.root / "arya.rules.md").exists())

    def test_agent_commands_target_the_recorded_address(self):
        self.cli("spawn", "skyler")
        self.assertEqual(self.cli("spawn", "arya").returncode, 0)
        before = len(self.calls())
        for command in (("send", "arya", self.brief()), ("read", "arya"), ("wait", "arya"), ("close", "arya")):
            done = self.cli(*command)
            self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual({c[2] for c in self.calls()[before:]}, {"t2"})

    def test_read_prints_the_terminal_text(self):
        self.cli("spawn", "arya")
        done = self.cli("read", "arya", "--lines", "40")
        self.assertEqual(done.stdout.strip(), "screen text")
        self.assertEqual(self.calls()[-1], ["read", "--json", "t1", "--lines", "40"])

    def test_close_stops_and_removes_the_agent_and_forgets_it(self):
        self.cli("spawn", "skyler")
        before = len(self.calls())
        done = self.cli("close", "skyler")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout), {"closed": "skyler", "stopped": True})
        calls = [c[:3] for c in self.calls()[before:]]
        self.assertEqual((calls[0], calls[1], calls[-1]), (["get", "--json", "t1"], ["kill", "--json", "t1"], ["rm", "--json", "t1"]))
        self.assertEqual(self.state()["agents"], {})

    def test_close_preserves_record_when_shutdown_fails(self):
        self.cli("spawn", "arya")
        saved = (self.root / "agentcy/state.json").read_bytes()
        for failure in ("kill", "rm", "timeout"):
            with self.subTest(failure=failure):
                (self.root / "agentcy/state.json").write_bytes(saved)
                hc = agentcy.Hc()
                def run(command, *args, check=True):
                    error = {"kind": "unavailable", "message": "temporary IPC failure"}
                    if command == failure:
                        if check:
                            raise agentcy.Fail(error["message"])
                        return {}, error
                    return {}, None
                states = [("working", 1), ("gone", 1)] if failure == "rm" else [("working", 1)] * 3
                with mock.patch.object(Path, "cwd", return_value=self.root), \
                        mock.patch.object(agentcy, "backend", return_value=hc), \
                        mock.patch.object(hc, "state", side_effect=states), \
                        mock.patch.object(hc, "run", side_effect=run), \
                        mock.patch.object(agentcy.time, "monotonic", side_effect=[0, 11]), \
                        contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(agentcy.main(["close", "arya"]), 1)
                self.assertEqual((self.root / "agentcy/state.json").read_bytes(), saved)

    def test_close_forgets_an_ended_agent(self):
        self.cli("spawn", "arya")
        done = self.cli("close", "arya", env={"FAKE_HC_FINISHED": "t1"})
        self.assertEqual(json.loads(done.stdout), {"closed": "arya", "stopped": False})
        self.assertNotIn("kill", [c[0] for c in self.calls()])
        self.assertEqual(self.calls()[-1], ["rm", "--json", "t1"])
        self.assertEqual(self.state()["agents"], {})
        self.assertEqual(json.loads(self.cli("spawn", "arya").stdout)["name"], "arya")

    def test_backend_failure_preserves_worker_records(self):
        for name in ("arya", "donna"):
            self.assertEqual(self.cli("spawn", name).returncode, 0)
        saved = (self.root / "agentcy/state.json").read_bytes()
        for command in (("close", "arya"), ("read", "arya"), ("wait", "arya"), ("list",),
                        ("send", "arya", self.brief()), ("handoff", "donna", "do the work")):
            with self.subTest(command=command[0]):
                before = len(self.calls())
                done = self.cli(*command, env={"FAKE_HC_FAIL": "get", "FAKE_HC_KIND": "unavailable",
                                              "FAKE_HC_MESSAGE": "temporary IPC failure"})
                self.assertEqual(done.returncode, 1, done.stdout)
                self.assertIn("temporary IPC failure", done.stderr)
                self.assertEqual((self.root / "agentcy/state.json").read_bytes(), saved)
                self.assertTrue(all(c[0] == "get" for c in self.calls()[before:]))
        self.assertEqual(self.cli("read", "arya").returncode, 0)
        self.assertEqual(self.cli("close", "arya").returncode, 0)

    def test_state_recognises_only_not_found_as_gone(self):
        hc = agentcy.Hc()
        cases = [(({}, {"kind": "not_found", "message": "no terminal"}), ("gone", -1)),
                 (({"state": "finished", "turn": 3}, None), ("gone", -1)),
                 (({"state": "live", "status": None, "turn": 2}, None), ("starting", 2)),
                 (({"state": "live", "status": {"state": "working"}, "turn": 4}, None), ("working", 4))]
        for response, expected in cases:
            with self.subTest(response=response), mock.patch.object(hc, "run", return_value=response):
                self.assertEqual(hc.state("t1"), expected)
        for error in ({"kind": "unavailable", "message": "connection refused"}, {"kind": "failed", "message": "x"}):
            with self.subTest(error=error), mock.patch.object(hc, "run", return_value=({}, error)):
                with self.assertRaises(agentcy.Fail):
                    hc.state("t1")

    def test_run_folders_stay_distinct_within_one_second(self):
        folders = []
        with mock.patch.object(agentcy.time, "strftime", return_value="20261023-120000"), \
                mock.patch.object(agentcy.Path, "cwd", return_value=self.root):
            for _ in range(2):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    self.assertEqual(agentcy.main(["run", "fix"]), 0)
                folders.append(Path(out.getvalue().strip()).name)
        self.assertEqual(folders, ["20261023-120000-fix", "20261023-120000-fix-2"])

    def test_wait_needs_a_finished_turn_after_the_send(self):
        self.cli("spawn", "arya")
        run = Path(self.cli("run", "w").stdout.strip())
        (run / "arya-1.md").write_text("Do it.\n")
        self.cli("send", "arya", str(run / "arya-1.md"))
        self.assertEqual(self.state()["agents"]["arya"]["turn"], 0)
        # Idle but no turn finished since the send: the agent has not started yet.
        waited = json.loads(self.cli("wait", "arya", "--minutes", "0.001", env={"FAKE_HC_LAG": "1"}).stdout)
        self.assertEqual(waited["status"], "timeout")
        self.assertEqual(waited["waited_seconds"], 0)
        self.assertEqual(waited["waiting"][0]["name"], "arya")
        self.assertGreaterEqual(waited["waiting"][0]["seconds_since_send"], 0)
        self.assertIn("--minutes must be more than 0", self.cli("wait", "arya", "--minutes", "0").stderr)
        waited = json.loads(self.cli("wait", "arya").stdout)
        self.assertEqual((waited["name"], waited["status"], waited["result_exists"], waited["waiting"]),
                         ("arya", "idle", False, []))
        (run / "arya-1.result.md").write_text("Status: done\n")
        self.assertTrue(json.loads(self.cli("wait", "arya").stdout)["result_exists"])

    def test_wait_returns_the_first_of_several_agents(self):
        run = Path(self.cli("run", "w").stdout.strip())
        for name in ("arya", "trinity"):
            self.cli("spawn", name)
            (run / f"{name}-1.md").write_text("Do it.\n")
            self.cli("send", name, str(run / f"{name}-1.md"))
        # Arya (t1) still works; Trinity (t2) has finished the turn her brief started.
        done = self.cli("wait", "arya", "trinity", "arya", env={"FAKE_HC_STATUS_t1": "working"})
        self.assertEqual(done.returncode, 0, done.stderr)
        waited = json.loads(done.stdout)
        self.assertEqual((waited["name"], waited["status"]), ("trinity", "idle"))
        self.assertEqual([w["name"] for w in waited["waiting"]], ["arya"])
        self.assertIn("result", waited["waiting"][0])
        before = len(self.calls())
        waited = json.loads(self.cli("wait", "arya", "trinity", "--minutes", "0.001",
                                     env={"FAKE_HC_STATUS": "working"}).stdout)
        self.assertEqual((waited["status"], [w["name"] for w in waited["waiting"]]), ("timeout", ["arya", "trinity"]))
        self.assertNotIn("name", waited)
        self.assertNotIn("wait", [c[0] for c in self.calls()[before:]])  # hc waits for one terminal only
        refused = self.cli("wait", "arya", "stranger")
        self.assertEqual(refused.returncode, 1)
        self.assertIn("'stranger' was not spawned by agentcy", refused.stderr)

    def test_wait_lets_hc_wait_while_the_agent_works(self):
        self.cli("spawn", "arya")
        before = len(self.calls())
        waited = json.loads(self.cli("wait", "arya", "--minutes", "0.001", env={"FAKE_HC_STATUS": "working"}).stdout)
        self.assertEqual(waited["status"], "timeout")
        self.assertIn(["wait", "--json", "t1", "--timeout", "1"], self.calls()[before:])

    def test_wait_returns_at_once_when_blocked_failed_or_gone(self):
        self.cli("spawn", "arya")
        for env, status in (({"FAKE_HC_STATUS": "blocked", "FAKE_HC_LAG": "5"}, "blocked"),
                            ({"FAKE_HC_STATUS": "error"}, "error"), ({"FAKE_HC_GONE": "t1"}, "gone")):
            with self.subTest(status=status):
                waited = json.loads(self.cli("wait", "arya", "--minutes", "1", env=env).stdout)
                self.assertEqual(waited["status"], status)

    def test_parallel_spawns_keep_both_records(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [pool.submit(self.cli, "spawn", name, env={"FAKE_HC_RUN_DELAY": "0.3"})
                    for name in ("arya", "trinity")]
            for job in jobs:
                done = job.result(timeout=10)
                self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(set(self.state()["agents"]), {"arya", "trinity"})

    def test_parallel_spawns_allocate_distinct_names(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [pool.submit(self.cli, "spawn", "arya", env={"FAKE_HC_RUN_DELAY": "0.3"})
                    for _ in range(2)]
            for job in jobs:
                done = job.result(timeout=10)
                self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(set(self.state()["agents"]), {"arya", "arya2"})
        self.assertEqual({c[c.index("--name") + 1] for c in self.calls() if c[0] == "run"}, {"arya", "arya2"})

    def test_dry_run_run_and_send_leave_files_unchanged(self):
        brief = self.root / "brief.md"
        brief.write_text("Check the code.\n")
        rules = self.root / "arya.rules.md"
        rules.write_text("keep this\n")
        before = {str(p.relative_to(self.root)): p.read_bytes() if p.is_file() else None
                  for p in self.root.rglob("*")}
        for args in (("run", "preview"), ("run", "preview", "--review"),
                     ("send", "arya", str(brief))):
            done = self.cli("--dry-run", *args)
            self.assertEqual(done.returncode, 0, done.stderr)
        after = {str(p.relative_to(self.root)): p.read_bytes() if p.is_file() else None
                 for p in self.root.rglob("*")}
        self.assertEqual(before, after)
        self.assertEqual(self.calls(), [])

    def test_dry_run_init_creates_nothing(self):
        empty = self.root / "empty"
        empty.mkdir()
        done = subprocess.run([sys.executable, str(SCRIPT), "--dry-run", "init"],
                              cwd=empty, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(list(empty.iterdir()), [])

    def test_dry_run_prints_commands_and_changes_nothing(self):
        done = self.cli("--dry-run", "spawn", "arya")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("+ hc run --json --bg --no-notify --name arya", done.stdout)
        self.assertIn("-- pi --model zai/glm-5.3-flash --thinking max", done.stdout)
        self.assertEqual(self.calls(), [])
        self.assertFalse((self.root / "agentcy/state.json").exists())


class WithoutInit(Project):
    """Before init the team is the template's cast without settings. The user picks a setting from
    the numbered menu when an agent is first needed, and set saves it, which creates the config."""
    INIT = False

    def setUp(self):
        super().setUp()
        bin_dir = Path(self.temp.name) / "bin"
        for name in ("claude", "codex"):  # so the menu numbers claude 1, codex 2, pi 3 on every computer
            (bin_dir / name).write_text("#!/bin/sh\n")
            (bin_dir / name).chmod(0o755)
        self.no_agy = f"{bin_dir}{os.pathsep}/usr/bin{os.pathsep}/bin"  # a PATH without the user's harnesses

    def options(self, *agents):
        done = self.cli("options", *agents)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    def test_check_shows_the_cast_without_settings_and_writes_nothing(self):
        report = self.check()
        rows = {row["name"]: row for row in report["agents"]}
        self.assertFalse(report["initialized"])
        self.assertEqual(report["root"], str(self.root.resolve()))
        self.assertEqual((rows["donna"]["harness"], rows["arya"]["harness"]), ("(this session)", None))
        self.assertEqual(rows["edna"]["tools"]["codex"]["harness"], "codex")  # a tool keeps its own harness
        self.assertEqual(rows["edna"]["tools"]["api"]["harness"], None)
        self.assertEqual(report["warnings"], [])
        self.assertFalse((self.root / "agentcy").exists())

    def test_spawn_needs_a_setting(self):
        done = self.cli("spawn", "arya")
        self.assertEqual(done.returncode, 1)
        self.assertIn("arya has no setting yet; ask the user with `options arya`, then `set`", done.stderr)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.cli("spawn", "edna", "--tool", "codex").returncode, 0)  # the tool has its own harness

    def test_options_number_the_installed_harnesses_and_recommend(self):
        self.assertIsNone(self.options("arya")["agents"][0]["recommended"])
        report = self.options("arya", "skyler", "--recommend", "arya", "3:4:7",
                              "--recommend", "skyler", "1:2:3")
        self.assertEqual([h["harness"] for h in report["harnesses"]][:3], ["claude", "codex", "pi"])
        pi = report["harnesses"][2]
        self.assertEqual(pi["models"][3], "zai/glm-5.3-flash")
        self.assertEqual(pi["efforts"], list(agentcy.EFFORTS["pi"]))
        self.assertEqual(report["harnesses"][1]["models"], [])
        self.assertEqual(report["harnesses"][1]["model_source"], "unavailable")  # no cache to read
        self.assertEqual(report["harnesses"][0]["model_source"], "built-in list")
        self.assertEqual(pi["model_source"], "offline catalog")
        self.assertFalse(any(h["access_verified"] for h in report["harnesses"]))
        self.assertEqual([row["name"] for row in report["agents"]], ["arya", "skyler"])
        menu = report["menu"]
        self.assertIn("pi · zai/glm-5.3-flash · max  (3:4:7)", menu)
        self.assertIn("claude · claude-opus-5-5 · high  (1:2:3)", menu)
        self.assertIn("    models:   1 claude-fable-5-2  2 claude-opus-5-5", menu)
        self.assertIn("    models:   type a name", menu)  # codex without a model cache
        self.assertNotIn("trinity", menu)
        self.assertEqual(len(self.options()["agents"]), 8)  # init asks about every agent
        self.assertIn("no agent nobody", self.cli("options", "nobody").stderr)

    def test_options_read_the_codex_model_cache(self):
        cache = {"models": [{"slug": "gpt-a", "visibility": "list", "supported_reasoning_levels": [{"effort": "low"}]},
                            {"slug": "gpt-hidden", "visibility": "hide", "supported_reasoning_levels": [{"effort": "max"}]},
                            {"slug": "gpt-b", "visibility": "list", "supported_reasoning_levels": [{"effort": "low"}, {"effort": "ultra"}]}]}
        (Path(self.temp.name) / "codex-home/models_cache.json").write_text(json.dumps(cache))
        codex = self.options("arya")["harnesses"][1]
        self.assertEqual((codex["models"], codex["efforts"]), (["gpt-a", "gpt-b"], ["low", "ultra"]))
        self.assertEqual(codex["model_source"], "local cache")

    def test_options_flag_saved_settings_without_replacing_them(self):
        self.cli("set", "donna", "pi:openai-codex/gpt-6-astra:medium")
        path = self.root / "agentcy/agentcy.json"
        before = path.read_bytes()
        bin_dir = Path(self.temp.name) / "bin"
        (bin_dir / "pi").write_text("#!/bin/sh\nprintf 'provider  model\\nzai  glm-5.3-flash\\n'\n")
        report = self.options("donna")
        self.assertIsNone(report["agents"][0]["recommended"])
        self.assertIn("saved setting: pi does not list model openai-codex/gpt-6-astra; keep it or change it",
                      report["menu"])
        (bin_dir / "pi").unlink()
        done = self.cli("options", "donna", env={"PATH": f"{bin_dir}{os.pathsep}/usr/bin{os.pathsep}/bin"})
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertNotIn("pi", [h["harness"] for h in json.loads(done.stdout)["harnesses"]])
        self.assertEqual(path.read_bytes(), before)

    def test_set_saves_the_picks_and_creates_the_config(self):
        done = self.cli("set", "arya", "3:4:7", "skyler", "1:3:2")
        self.assertEqual(done.returncode, 0, done.stderr)
        saved = json.loads(done.stdout)
        self.assertTrue(saved["created"])
        self.assertEqual({name: (a["harness"], a["model"], a["effort"]) for name, a in saved["agents"].items()},
                         {"arya": ("pi", "zai/glm-5.3-flash", "max"), "skyler": ("claude", "claude-sonnet-5-5", "medium")})
        cfg = json.loads((self.root / "agentcy/agentcy.json").read_text())
        self.assertEqual(list(cfg["agents"]["skyler"])[:5], ["role", "use", "harness", "model", "effort"])
        self.assertEqual(cfg["agents"]["skyler"]["approve"], "auto")
        self.assertEqual((self.root / "agentcy/.gitignore").read_text(), "runs/\nstate.json\nstate.tmp\n")
        report = self.check()
        rows = {row["name"]: row for row in report["agents"]}
        self.assertTrue(report["initialized"])
        self.assertEqual((rows["arya"]["harness"], rows["trinity"]["harness"]), ("pi", None))
        self.assertIn("— now claude · claude-sonnet-5-5 · medium", self.options("skyler")["menu"])

        self.assertEqual(self.cli("spawn", "arya").returncode, 0)
        self.assertEqual(self.started()[-1], ["pi", "--model", "zai/glm-5.3-flash", "--thinking", "max"])
        self.assertIn("trinity has no setting yet", self.cli("spawn", "trinity").stderr)

        again = json.loads(self.cli("set", "trinity", "2:gpt-6.1-sol:high", "amy", "3").stdout)
        self.assertFalse(again["created"])
        self.assertEqual((again["agents"]["trinity"]["model"], again["agents"]["amy"]["model"]), ("gpt-6.1-sol", "default"))

    def test_set_refuses_a_bad_answer_and_saves_nothing(self):
        for args, text in ((("arya", "3:9"), "model 9 is not in the menu; choose 1 to 4"),
                           (("arya", "9"), "harness 9 is not in the menu"),
                           (("arya", "2:1"), "the menu has no numbered models here; type a name"),
                           (("arya", "1:2:3:4"), "answer '1:2:3:4' as harness:model:thinking"),
                           (("arya",), "give pairs of agent and answer"),
                           (("nobody", "0"), "no agent nobody"),
                           (("arya", "0"), "expand the approved recommendation to harness:model:thinking"),
                           (("arya", "gemini:m"), "agentcy knows no model/effort flags for gemini")):
            with self.subTest(args=args):
                done = self.cli("set", *args)
                self.assertEqual(done.returncode, 1)
                self.assertIn(text, done.stderr)
        self.assertFalse((self.root / "agentcy/agentcy.json").exists())

    def test_init_waits_for_choices_and_preserves_existing_settings(self):
        self.assertEqual(self.cli("init").returncode, 0)
        rows = {row["name"]: row for row in self.check()["agents"]}
        self.assertIsNone(rows["arya"]["harness"])
        self.assertEqual(self.cli("set", "arya", "claude:claude-haiku-5-5:low").returncode, 0)
        path = self.root / "agentcy/agentcy.json"
        before = path.read_bytes()
        self.assertFalse(json.loads(self.cli("init").stdout)["created"])
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.options("arya")["agents"][0]["recommended"],
                         {"harness": "claude", "model": "claude-haiku-5-5", "effort": "low"})

    def test_recommendations_are_read_only_and_save_exact_named_choices(self):
        report = self.options("arya", "--recommend", "arya", "claude:claude-haiku-5-5:low")
        pick = report["agents"][0]["recommended"]
        self.assertFalse((self.root / "agentcy").exists())
        self.assertIn("claude · claude-haiku-5-5 · low", report["menu"])
        answer = ":".join(pick.get(key, "") for key in agentcy.SETTING)
        self.assertEqual(self.cli("set", "arya", answer).returncode, 0)
        cfg = json.loads((self.root / "agentcy/agentcy.json").read_text())
        self.assertEqual(agentcy.setting(cfg["agents"]["arya"]), pick)

    def test_recommendations_and_set_refuse_undetected_choices(self):
        for answer, text in (("agy:model:high", "harness agy is not installed"),
                             ("pi:missing:high", "pi does not list model missing"),
                             ("pi:zai/glm-5.3-flash:ultra", "pi has no thinking level ultra"),
                             ("claude:opus:turbo", "claude has no thinking level turbo")):
            for command in (("options", "arya", "--recommend"), ("set",)):
                with self.subTest(answer=answer, command=command[0]):
                    done = self.cli(*command, "arya", answer, env={"PATH": self.no_agy})
                    self.assertEqual(done.returncode, 1)
                    self.assertIn(f"arya: {text}", done.stderr)
        self.assertFalse((self.root / "agentcy/agentcy.json").exists())

    def test_a_typed_model_name_passes_where_the_harness_has_no_catalog(self):
        # codex has no model cache here, and claude's built-in list is not the account's catalog.
        picks = {"arya": "codex:gpt-x:high", "skyler": "claude:opus:high", "amy": "pi:glm-5.3-flash"}
        recommend = [part for name, answer in picks.items() for part in ("--recommend", name, answer)]
        report = self.options(*picks, *recommend)
        self.assertEqual([row["recommended"].get("model") for row in report["agents"]], ["gpt-x", "opus", "glm-5.3-flash"])
        for text in ("codex · gpt-x · high  (2:gpt-x:3)", "claude · opus · high  (1:opus:3)", "0 — my picks for all:"):
            self.assertIn(text, report["menu"])
        self.assertEqual(self.cli("set", *(part for pair in picks.items() for part in pair)).returncode, 0)
        report = self.options(*picks)  # the saved names stay the picks, with no warning
        self.assertEqual([(row["recommended"], row["warning"]) for row in report["agents"]],
                         [(row["now"], None) for row in report["agents"]])
        self.assertIn("Reply 0 to accept", report["menu"])

    def test_agent_names_can_follow_a_recommendation(self):
        report = self.options("arya", "--recommend", "arya", "claude", "skyler", "amy")
        self.assertEqual([row["name"] for row in report["agents"]], ["arya", "skyler", "amy"])
        done = self.cli("options", "arya", "--recommend", "arya", "claude", "--bogus")
        self.assertEqual(done.returncode, 2)
        self.assertIn("unrecognized arguments: --bogus", done.stderr)
        self.assertIn("unrecognized arguments: extra", self.cli("check", "extra").stderr)

    def test_an_orchestrator_without_a_setting_needs_no_pick(self):
        menu = self.options("donna", "arya", "--recommend", "arya", "claude")["menu"]
        self.assertIn("no pick: runs in this session", menu)
        self.assertIn("0 — my picks for all:", menu)
        self.assertNotIn("0 —", self.options("donna")["menu"])  # nothing to accept
        self.assertIn("no pick: choose one", self.options("donna", "arya")["menu"])
        self.cli("set", "donna", "pi:openai-codex/gpt-6-astra")
        (Path(self.temp.name) / "bin/pi").write_text("#!/bin/sh\nprintf 'provider  model\\nzai  glm-5.3-flash\\n'\n")
        menu = self.options("donna", "arya", "--recommend", "arya", "claude")["menu"]
        self.assertNotIn("0 —", menu)  # her saved setting cannot be used, so she needs a choice

    def test_codex_recommendation_checks_the_selected_models_effort(self):
        cache = {"models": [{"slug": "small", "supported_reasoning_levels": [{"effort": "low"}]},
                            {"slug": "large", "supported_reasoning_levels": [{"effort": "high"}]}]}
        (Path(self.temp.name) / "codex-home/models_cache.json").write_text(json.dumps(cache))
        for command in (("options", "arya", "--recommend"), ("set",)):
            done = self.cli(*command, "arya", "codex:small:high")
            self.assertEqual(done.returncode, 1)
            self.assertIn("arya: codex has no thinking level high for model small", done.stderr)
            self.assertIn("codex does not list model gpt-x", self.cli(*command, "arya", "codex:gpt-x").stderr)
        self.assertFalse((self.root / "agentcy/agentcy.json").exists())
        self.assertEqual(self.options("arya", "--recommend", "arya", "codex:small:low")
                         ["agents"][0]["recommended"]["model"], "small")

    def test_no_installed_harness_produces_no_recommendation(self):
        done = self.cli("options", "arya", env={"PATH": ""})
        self.assertEqual(done.returncode, 0, done.stderr)
        report = json.loads(done.stdout)
        self.assertEqual(report["harnesses"], [])
        self.assertIsNone(report["agents"][0]["recommended"])
        self.assertIn("No harness", report["menu"])
        self.assertNotIn("0 —", report["menu"])
        self.assertFalse((self.root / "agentcy").exists())

    def test_custom_agents_can_have_recommendations_and_keep_other_fields(self):
        self.cli("init")
        self.config(lambda cfg: cfg["agents"].__setitem__("helper", {
            **cfg["agents"]["arya"], "approve": "ask", "args": ["--extra"], "character": "Helper"}))
        report = self.options("helper", "--recommend", "helper", "claude:claude-haiku-5-5:low")
        self.assertEqual(report["agents"][0]["recommended"]["model"], "claude-haiku-5-5")
        done = self.cli("set", "helper", "claude:claude-haiku-5-5:low")
        self.assertEqual(done.returncode, 0, done.stderr)
        helper = json.loads((self.root / "agentcy/agentcy.json").read_text())["agents"]["helper"]
        self.assertEqual((helper["approve"], helper["args"], helper["character"]), ("ask", ["--extra"], "Helper"))

    def test_recommendations_reject_duplicates_and_agents_outside_the_menu(self):
        for args, error in (
                (("arya", "--recommend", "skyler", "claude"), "not among the requested agents"),
                (("arya", "--recommend", "arya", "claude", "--recommend", "arya", "pi"), "duplicate recommendation")):
            with self.subTest(error=error):
                done = self.cli("options", *args)
                self.assertEqual(done.returncode, 1)
                self.assertIn(error, done.stderr)
        self.assertFalse((self.root / "agentcy").exists())

    def test_unknown_catalog_can_offer_harness_default_but_not_for_t3(self):
        report = self.options("arya", "--recommend", "arya", "codex")
        self.assertEqual(report["agents"][0]["recommended"], {"harness": "codex"})
        self.assertIn("access is not verified", report["menu"])
        done = self.cli("options", "arya", "--recommend", "arya", "codex", env={"T3CODE_THREAD_ID": "self"})
        self.assertEqual(done.returncode, 1)
        self.assertIn("arya: T3 Code needs a model to choose the provider", done.stderr)
        done = self.cli("set", "arya", "codex", env={"T3CODE_THREAD_ID": "self"})
        self.assertIn("arya: T3 Code needs a model to choose the provider", done.stderr)
        self.assertFalse((self.root / "agentcy/agentcy.json").exists())


class T3Code(Project):
    """The T3 Code backend, chosen by auto inside a T3 Code thread."""

    def setUp(self):
        super().setUp()
        self.env |= {"T3CODE_THREAD_ID": "mcp:self", "T3CODE_CLI_PATH": str(Path(self.temp.name) / "bin/t3")}

    def t3_calls(self):
        return [json.loads(line) for line in self.t3_log.read_text().splitlines()] if self.t3_log.exists() else []

    def spawn(self, agent="arya", thread="child1", env=None):
        done = self.cli("spawn", agent, "--thread", thread, env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    def brief(self, text="Do the work.\n"):
        run = Path(self.cli("run", "t3").stdout.strip())
        (run / "arya-1.md").write_text(text)
        return str(run / "arya-1.md")

    def test_auto_chooses_t3_inside_a_t3_thread(self):
        report = self.check()
        self.assertEqual(report["backend"], {"name": "t3", "ready": True, "problem": None, "not_applied": ["args"]})
        self.assertEqual(report["session"], {"harness": "claude", "model": "claude-opus-5-5", "inside": "t3"})
        # Edna's codex and antigravity tools keep their harness's own model, which T3 Code cannot choose.
        self.assertEqual(report["warnings"], ["edna.tools.codex: T3 Code needs a model to choose the provider",
                                              "edna.tools.antigravity: T3 Code needs a model to choose the provider"])
        self.config(lambda cfg: cfg.update(backend="hc"))
        self.assertEqual(self.check()["backend"]["name"], "hc")

    def test_a_folder_outside_a_t3_project_is_not_ready(self):
        report = self.check({"FAKE_T3_NO_PROJECT": "1"})
        self.assertFalse(report["backend"]["ready"])
        self.assertIn("No T3 Code project matches", report["backend"]["problem"])

    def test_spawn_gives_the_delegate_task_call(self):
        done = self.cli("spawn", "arya")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout), {"agent": "arya", "tool": None, "status": "delegate", "delegate_task": {
            "title": "agentcy: arya", "task": agentcy.GREETING, "mode": "wait",
            "target": {"providerInstanceId": "pi", "model": "zai/glm-5.3-flash", "options": {"thinking": "max"}}}})
        self.config(lambda cfg: cfg["agents"]["skyler"].update(approve="ask", effort="default"))
        call = json.loads(self.cli("spawn", "skyler").stdout)["delegate_task"]
        self.assertEqual((call["target"]["providerInstanceId"], call["target"]["options"], call["runtimeMode"]),
                         ("claudeAgent", {}, "approval-required"))
        self.assertEqual((self.t3_calls(), self.calls()), ([], []))
        self.assertFalse((self.root / "agentcy/state.json").exists())
        for args, text in ((("edna", "--tool", "codex"), "T3 Code needs a model"),
                           (("donna",), "in T3 Code, start a new thread with pi, model openai-codex/gpt-6-astra")):
            with self.subTest(args=args):
                refused = self.cli("spawn", *args)
                self.assertEqual(refused.returncode, 1)
                self.assertIn(text, refused.stderr)

    def test_spawn_with_a_thread_records_this_sessions_subagent(self):
        self.assertEqual(self.spawn(), {"name": "arya", "tool": None, "harness": "pi", "address": "child1",
                                        "reach": "https://t3.test/child1", "status": "ready"})
        self.assertEqual(self.state()["agents"]["arya"]["address"], "child1")
        self.assertEqual(self.spawn(thread="child2")["name"], "arya2")
        for thread, env, text in (("child9", {}, "T3 Code has no thread child9"),
                                  ("child1", {"FAKE_T3_PARENT": "mcp:other"}, "not a subagent of this session's thread")):
            with self.subTest(text=text):
                refused = self.cli("spawn", "arya", "--thread", thread, env=env)
                self.assertEqual(refused.returncode, 1)
                self.assertIn(text, refused.stderr)
        self.assertEqual(set(self.state()["agents"]), {"arya", "arya2"})
        hc = self.cli("spawn", "arya", "--thread", "child1", env={"T3CODE_THREAD_ID": ""})
        self.assertIn("--thread records a T3 Code subagent; this backend is hc", hc.stderr)

    def test_a_failed_start_records_nothing(self):
        done = self.cli("spawn", "arya", "--thread", "child1", env={"FAKE_T3_STATUS": "failed"})
        self.assertEqual(done.returncode, 1)
        self.assertIn("arya failed at start", done.stderr)
        self.assertFalse((self.root / "agentcy/state.json").exists())

    def test_send_and_wait_follow_the_thread_runs(self):
        self.spawn()
        sent = self.cli("send", "arya", self.brief())
        self.assertEqual(sent.returncode, 0, sent.stderr)
        self.assertTrue(json.loads(sent.stdout)["started"])
        send = self.t3_calls()[-1]
        self.assertEqual(send[:2], ["send", "child1"])
        self.assertIn("# Brief\nDo the work.", send[2])
        self.assertEqual(self.state()["agents"]["arya"]["turn"], 1)  # the greeting run had ended
        self.assertEqual(json.loads(self.cli("wait", "arya").stdout)["status"], "idle")
        waited = json.loads(self.cli("wait", "arya", "--minutes", "0.001", env={"FAKE_T3_STATUS": "running"}).stdout)
        self.assertEqual(waited["status"], "timeout")
        for env, status in (({"FAKE_T3_PENDING": "1", "FAKE_T3_STATUS": "running"}, "blocked"),
                            ({"FAKE_T3_STATUS": "failed"}, "error"), ({"FAKE_T3_GONE": "child1"}, "gone")):
            with self.subTest(status=status):
                self.assertEqual(json.loads(self.cli("wait", "arya", env=env).stdout)["status"], status)

    def test_a_message_to_a_busy_thread_waits_for_its_own_run(self):
        self.spawn()
        self.cli("send", "arya", self.brief())
        done = self.cli("send", "arya", self.brief(), env={"FAKE_T3_STATUS": "running", "FAKE_T3_DELIVERY": "queued"})
        self.assertFalse(json.loads(done.stdout)["started"])
        # Two runs exist and the second is still live, so one has ended; this message's run is the third.
        self.assertEqual(self.state()["agents"]["arya"]["turn"], 2)

    def test_send_refuses_a_thread_waiting_on_a_question(self):
        self.spawn()
        done = self.cli("send", "arya", self.brief(), env={"FAKE_T3_PENDING": "1"})
        self.assertEqual(done.returncode, 1)
        self.assertIn("arya is waiting on a question in its T3 Code thread", done.stderr)
        self.assertNotIn("send", [c[0] for c in self.t3_calls()])

    def test_read_shows_the_thread_state_and_messages(self):
        self.spawn()
        text = self.cli("read", "arya", env={"FAKE_T3_PENDING": "1"}).stdout
        for part in ("completed  pi/zai/glm-5.3-flash  https://t3.test/child1",
                     "Waiting for 1 answer(s) in T3 Code.", "[assistant]\nresult written"):
            self.assertIn(part, text)

    def test_close_forgets_a_finished_thread_and_refuses_a_busy_one(self):
        self.spawn()
        busy = self.cli("close", "arya", env={"FAKE_T3_STATUS": "running"})
        self.assertEqual(busy.returncode, 1)
        self.assertIn("stop it in T3 Code", busy.stderr)
        self.assertIn("arya", self.state()["agents"])
        done = self.cli("close", "arya")
        self.assertEqual(json.loads(done.stdout), {"closed": "arya", "stopped": False})
        self.assertEqual(self.state()["agents"], {})

    def test_backend_failure_preserves_worker_records(self):
        self.spawn()
        saved = (self.root / "agentcy/state.json").read_bytes()
        for command in (("close", "arya"), ("read", "arya"), ("wait", "arya"), ("send", "arya", self.brief())):
            with self.subTest(command=command[0]):
                done = self.cli(*command, env={"FAKE_T3_FAIL": "show"})
                self.assertEqual(done.returncode, 1, done.stdout)
                self.assertIn("Could not reach the T3 Code server", done.stderr)
                self.assertEqual((self.root / "agentcy/state.json").read_bytes(), saved)


class ReviewBaseline(Project):
    def git(self, *args):
        done = subprocess.run(["git", *args], cwd=self.root, capture_output=True, check=True)
        return done.stdout

    def test_review_compares_with_existing_work_and_includes_new_files(self):
        self.git("init", "-q")
        source = self.root / "source.txt"
        source.write_text("committed\n")
        self.git("add", "source.txt")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "commit", "-qm", "fixture")
        source.write_text("staged user work\n")
        self.git("add", "source.txt")
        source.write_text("unstaged user work\n")
        untracked = self.root / "user file.txt"
        untracked.write_text("existing untracked work\n")
        index = (self.root / ".git/index").read_bytes()
        done = self.cli("run", "review", "--review")
        self.assertEqual(done.returncode, 0, done.stderr)
        run = Path(done.stdout.strip())
        baseline = json.loads((run / "baseline.json").read_text())
        self.assertIn("staged user work", baseline["staged_patch"])
        self.assertIn("unstaged user work", baseline["unstaged_patch"])
        self.assertEqual((self.root / ".git/index").read_bytes(), index)
        self.assertEqual(source.read_text(), "unstaged user work\n")
        unchanged = self.cli("changes", str(run))
        self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
        self.assertEqual(json.loads(unchanged.stdout)["files"], [])
        source.write_text("agent change\n")
        untracked.unlink()
        # The orchestrator's own notes during the run are not changes to the work.
        (self.root / "agentcy/feedback.md").write_text("# Feedback\n- run — donna — corrected — x\n")
        (self.root / "agentcy/lessons").mkdir()
        (self.root / "agentcy/lessons/arya.md").write_text("# Arya Stark lessons\n- x\n")
        (self.root / "new file.txt").write_text("new agent file\n")
        done = self.cli("changes", str(run))
        self.assertEqual(done.returncode, 0, done.stderr)
        report = json.loads(done.stdout)
        self.assertEqual(set(report["files"]), {"source.txt", "user file.txt", "new file.txt"})
        self.assertIn("-unstaged user work", report["patch"])
        self.assertNotIn("-committed", report["patch"])
        self.assertEqual((self.root / ".git/index").read_bytes(), index)
        self.assertEqual(json.loads((run / "baseline.json").read_text()), baseline)
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        dry = self.cli("--dry-run", "changes", str(run))
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_changes_lists_both_paths_of_a_moved_file(self):
        self.git("init", "-q")
        (self.root / "cart.js").write_text("export const cart = [];\n" * 10)
        self.git("add", "cart.js")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture")
        run = Path(self.cli("run", "move", "--review").stdout.strip())
        self.git("mv", "cart.js", "basket.js")
        done = self.cli("changes", str(run))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(set(json.loads(done.stdout)["files"]), {"cart.js", "basket.js"})

    def test_review_refuses_index_flags_that_hide_edits(self):
        self.git("init", "-q")
        source = self.root / "source file.txt"
        source.write_text("committed\n")
        (self.root / "control.txt").write_text("unchanged\n")
        self.git("add", source.name, "control.txt")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "commit", "-qm", "fixture")
        for flag in ("assume-unchanged", "skip-worktree"):
            with self.subTest(flag=flag):
                self.git("update-index", "--no-assume-unchanged", "--no-skip-worktree", source.name)
                self.git("update-index", f"--{flag}", source.name)
                source.write_text("hidden user edit\n")
                index = (self.root / ".git/index").read_bytes()
                done = self.cli("run", f"review-{flag}", "--review")
                self.assertEqual(done.returncode, 1, done.stdout)
                self.assertIn("assume-unchanged or skip-worktree", done.stderr)
                self.assertIn(source.name, done.stderr)
                self.assertFalse((self.root / "agentcy/runs").exists())
                self.assertEqual((self.root / ".git/index").read_bytes(), index)
                self.assertEqual(source.read_text(), "hidden user edit\n")
                self.git("update-index", f"--no-{flag}", source.name)

    def test_changes_refuses_flags_added_after_the_baseline(self):
        self.git("init", "-q")
        source = self.root / "source.txt"
        source.write_text("committed\n")
        (self.root / "control.txt").write_text("unchanged\n")
        self.git("add", source.name, "control.txt")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "commit", "-qm", "fixture")
        run = Path(self.cli("run", "review", "--review").stdout.strip())
        baseline = (run / "baseline.json").read_bytes()
        for flag in ("assume-unchanged", "skip-worktree"):
            with self.subTest(flag=flag):
                self.git("update-index", "--no-assume-unchanged", "--no-skip-worktree", source.name)
                self.git("update-index", f"--{flag}", source.name)
                source.write_text("hidden worker edit\n")
                index = (self.root / ".git/index").read_bytes()
                done = self.cli("changes", str(run))
                self.assertEqual(done.returncode, 1, done.stdout)
                self.assertIn("assume-unchanged or skip-worktree", done.stderr)
                self.assertEqual((self.root / ".git/index").read_bytes(), index)
                self.assertEqual((run / "baseline.json").read_bytes(), baseline)
                self.assertEqual(source.read_text(), "hidden worker edit\n")
                self.git("update-index", f"--no-{flag}", source.name)

    def test_review_refuses_dirty_submodules_without_changing_indexes(self):
        self.git("init", "-q")
        origin = Path(self.temp.name) / "library-origin"
        self.git("init", "-q", str(origin))
        (origin / "source.txt").write_text("committed\n")
        self.git("-C", str(origin), "add", ".")
        self.git("-C", str(origin), "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "commit", "-qm", "library")
        self.git("-c", "protocol.file.allow=always", "submodule", "add", str(origin), "library space")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture")
        # User ignore settings must not hide changes from the review guard.
        self.git("config", "submodule.library space.ignore", "all")
        run_result = self.cli("run", "clean", "--review")
        self.assertEqual(run_result.returncode, 0, run_result.stderr)
        run = Path(run_result.stdout.strip())
        baseline = (run / "baseline.json").read_bytes()
        self.assertEqual(json.loads(self.cli("changes", str(run)).stdout)["files"], [])
        library = self.root / "library space"
        source = library / "source.txt"
        new = library / "new.txt"
        indexes = [self.root / ".git/index", self.root / ".git/modules/library space/index"]
        for change in ("unstaged", "staged", "untracked"):
            with self.subTest(change=change):
                if change == "untracked":
                    new.write_text("new work\n")
                else:
                    source.write_text("changed\n")
                    if change == "staged":
                        self.git("-C", str(library), "add", "source.txt")
                saved = [path.read_bytes() for path in indexes]
                for command in (("run", "dirty", "--review"), ("changes", str(run))):
                    done = self.cli(*command)
                    self.assertEqual(done.returncode, 1, done.stdout)
                    self.assertIn("submodule", done.stderr)
                    self.assertIn("library space", done.stderr)
                    self.assertEqual([path.read_bytes() for path in indexes], saved)
                    self.assertEqual((run / "baseline.json").read_bytes(), baseline)
                self.assertEqual(len(list((self.root / "agentcy/runs").iterdir())), 1)
                self.git("-C", str(library), "reset", "--hard", "HEAD")
                if new.exists():
                    new.unlink()

    def test_review_needs_a_first_commit(self):
        self.git("init", "-q")
        done = self.cli("run", "review", "--review")
        self.assertEqual(done.returncode, 1)
        self.assertIn("commit once before a reviewed run", done.stderr)
        self.assertFalse((self.root / "agentcy/runs").exists())

    def test_missing_baseline_stops_review(self):
        done = self.cli("changes", str(self.root))
        self.assertEqual(done.returncode, 1)
        self.assertIn("before changing files", done.stderr)
        self.assertEqual(self.calls(), [])


class Images(Project):
    def setUp(self):
        super().setUp()
        self.prompt = self.root / "prompt.txt"
        self.prompt.write_text("A red bicycle.\n")
        self.photo = self.root / "in.png"
        self.photo.write_bytes(b"\x89PNG fake")

    def test_gemini_request_shape(self):
        url, kind, body = agentcy.gemini_request("m", "draw", [self.photo], "16:9", "2K")
        self.assertEqual(url, "https://generativelanguage.googleapis.com/v1beta/interactions")
        data = json.loads(body)
        self.assertEqual(data["input"][1], {"type": "text", "text": "draw"})
        self.assertEqual(data["input"][0]["mime_type"], "image/png")
        self.assertEqual(base64.b64decode(data["input"][0]["data"]), b"\x89PNG fake")
        self.assertEqual(data["response_format"], {"type": "image", "aspect_ratio": "16:9", "image_size": "2K"})
        self.assertNotIn("response_format", json.loads(agentcy.gemini_request("m", "draw", [], None, None)[2]))

    def test_openai_generation_and_edit_requests(self):
        url, kind, body = agentcy.openai_request("gpt-image", "draw", [], "1536x1024", None)
        self.assertEqual((url, kind), ("https://api.openai.com/v1/images/generations", "application/json"))
        self.assertEqual(json.loads(body), {"model": "gpt-image", "prompt": "draw", "size": "1536x1024"})
        url, kind, body = agentcy.openai_request("gpt-image", "edit it", [self.photo], None, "high")
        self.assertEqual(url, "https://api.openai.com/v1/images/edits")
        self.assertTrue(kind.startswith("multipart/form-data; boundary="))
        self.assertIn(b'name="image[]"; filename="in.png"', body)
        self.assertIn(b"\x89PNG fake", body)
        self.assertIn(b'name="quality"\r\n\r\nhigh', body)

    def test_gemini_video_request_and_response(self):
        url, kind, body = agentcy.gemini_request("gemini-omni-1.2-flash", "a marble run", [self.photo], "9:16", "1080p", "video")
        data = json.loads(body)
        self.assertEqual(url, "https://generativelanguage.googleapis.com/v1beta/interactions")
        self.assertEqual([item["type"] for item in data["input"]], ["image", "text"])
        self.assertEqual(data["response_format"], {"type": "video", "aspect_ratio": "9:16", "resolution": "1080p"})
        plain = json.loads(agentcy.gemini_request("m", "x", [], None, None, "video")[2])
        self.assertEqual(plain["response_format"], {"type": "video"})
        clip = base64.b64encode(b"mp4").decode()
        response = {"steps": [{"type": "model_output", "content": [{"type": "video", "mime_type": "video/mp4", "data": clip},
                                                                   {"type": "image", "data": clip}]}]}
        self.assertEqual(agentcy.gemini_media(response, "video"), [b"mp4"])

    def test_video_cli_takes_only_gemini(self):
        done = self.cli("--dry-run", "video", "--provider", "gemini", "--model", "gemini-omni-1.2-flash",
                        "--prompt-file", str(self.prompt), "--out", "clip.mp4")
        self.assertEqual(json.loads(done.stdout)["model"], "gemini-omni-1.2-flash")
        done = self.cli("--dry-run", "video", "--provider", "openai", "--model", "sora-2",
                        "--prompt-file", str(self.prompt), "--out", "clip.mp4")
        self.assertEqual(done.returncode, 2)
        self.assertIn("invalid choice: 'openai'", done.stderr)

    def test_gemini_images_come_from_model_output_only(self):
        image = base64.b64encode(b"out").decode()
        echoed = base64.b64encode(b"input").decode()
        data = {"steps": [{"type": "user_input", "content": [{"type": "image", "data": echoed}]},
                          {"type": "model_output", "content": [{"type": "text", "text": "ok"}, {"type": "image", "data": image}]}],
                "output_image": {"type": "image", "data": image}}
        self.assertEqual(agentcy.gemini_media(data), [b"out"])
        self.assertEqual(agentcy.gemini_media({"output_image": {"data": image}}), [b"out"])

    def test_gemini_input_media_is_never_output(self):
        for kind in ("image", "video"):
            echoed = {"type": kind, "data": base64.b64encode(b"input").decode()}
            for data in ({"steps": [{"type": "user_input", "content": [echoed]}]},
                         {"input": [echoed]}):
                self.assertEqual(agentcy.gemini_media(data, kind), [])

    def test_openai_images(self):
        data = {"data": [{"b64_json": base64.b64encode(b"one").decode()}, {"url": "x"}]}
        self.assertEqual(agentcy.openai_images(data), [b"one"])

    def test_missing_key_is_a_clear_error_and_dry_run_needs_none(self):
        done = self.cli("image", "--provider", "gemini", "--model", "m", "--prompt-file", str(self.prompt), "--out", "out.png")
        self.assertEqual(done.returncode, 1)
        self.assertIn("GEMINI_API_KEY is not set", done.stderr)
        done = self.cli("--dry-run", "image", "--prompt-file", str(self.prompt), "--out", "out.png",
                        "--provider", "openai", "--model", "gpt-image")
        self.assertEqual(json.loads(done.stdout)["url"], "https://api.openai.com/v1/images/generations")
        self.assertFalse((self.root / "out.png").exists())

    def test_openai_rejects_aspect(self):
        done = self.cli("--dry-run", "image", "--prompt-file", str(self.prompt), "--out", "o.png",
                        "--provider", "openai", "--model", "gpt-image", "--aspect", "16:9")
        self.assertEqual(done.returncode, 1)
        self.assertIn("--size WIDTHxHEIGHT", done.stderr)


if __name__ == "__main__":
    unittest.main()
