"""Deterministic safety tests for the eval harness. No agent calls."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import select
import signal
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EvalSafetyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cobb-eval-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out = self.root / "runs"
        self.out.mkdir()
        self.calls = self.root / "calls.jsonl"

    def eval_environment(self, **settings):
        env = dict(os.environ, EVAL_OUT=str(self.out), EVAL_DRY="1", EVAL_ONLY="menu",
                   EVAL_RECHECK="", EVAL_AGENT="", EVAL_HARNESS="", EVAL_PROVIDER="",
                   EVAL_MODEL="", EVAL_EFFORT="", EVAL_APPROVE="", EVAL_JOBS="", EVAL_TIMEOUT="30",
                   GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
        env.update(settings)
        return env

    def run_eval(self, label, input_fd=subprocess.DEVNULL, arguments=(), runner=None, **settings):
        env = self.eval_environment(**settings)
        return subprocess.run(["bash", str(runner or ROOT / "evals/run.sh"), label, *arguments],
                              env=env, stdin=input_fd, capture_output=True, text=True,
                              timeout=20)

    def fake_agent(self, name="adapter", error=False, session=True, jsonl=False, delay=0.1,
                   events_override=None, exit_code=0, catalog=None):
        executable = self.root / name
        result = "0 — Recommended: implement f-01 — the PRD is ready"
        payload = dict(result=result, is_error=error, **({'session_id': 'fake-session'} if session else {}))
        if jsonl == "codex":
            payloads = ([dict(type="thread.started", thread_id="fake-thread")] if session else [])
            payloads += [dict(type="item.completed", item=dict(type="agent_message", text=result))]
            payloads += [dict(type="turn.failed", error=dict(message="quota")) if error else
                         dict(type="turn.completed", usage=dict(input_tokens=100, output_tokens=20))]
        elif jsonl:
            payloads = [dict(type="message_end", message=dict(role="assistant", content=[dict(type="text", text=result)],
                        stopReason="error" if error else "stop", errorMessage="quota" if error else None,
                        usage=dict(cost=dict(total=0.25)))), dict(type="agent_settled")]
        else:
            payloads = [payload]
        if events_override is not None:
            payloads = events_override
        if catalog is None:
            catalog = "provider model context max-out thinking images\nopenai-codex gpt-6.1-sol 272K 128K yes yes\nzai glm-5.3-flash 1M 131K yes yes\n"
        # This adapter also acts as a fake CLI executable. It never calls a service.
        executable.write_text(f'''#!{sys.executable}
import json, os, sys, time
from pathlib import Path
if "--list-models" in sys.argv:
    print({catalog!r})
    sys.exit(0)
record = dict(args=sys.argv[1:], cwd=os.getcwd(), phase="start", pid=os.getpid(),
              model=os.environ.get("EVAL_MODEL"), effort=os.environ.get("EVAL_EFFORT"),
              skill=os.environ.get("EVAL_SKILL_DIR"), keep=os.environ.get("EVAL_KEEP_SESSION"))
log = Path({str(self.calls)!r})
with log.open("a") as f: f.write(json.dumps(record) + "\\n")
time.sleep({delay!r})
for payload in {payloads!r}: print(json.dumps(payload))
with log.open("a") as f: f.write(json.dumps(dict(phase="end")) + "\\n")
sys.exit({exit_code!r})
''')
        executable.chmod(0o755)
        return str(executable)

    def live(self, label, **settings):
        options = dict(EVAL_DRY="", EVAL_HARNESS=settings.get("EVAL_HARNESS", "") or self.fake_agent(),
                       EVAL_MODEL="chosen-model", EVAL_EFFORT="chosen-effort", EVAL_APPROVE="1")
        options.update(settings)
        return self.run_eval(label, **options)

    def call_records(self):
        records = [json.loads(line) for line in self.calls.read_text().splitlines()]
        return [record for record in records if record["phase"] == "start"]

    def test_live_run_requires_each_setting_before_creating_output(self):
        agent = self.fake_agent()
        settings = dict(EVAL_DRY="", EVAL_HARNESS=agent, EVAL_MODEL="chosen",
                        EVAL_EFFORT="minimal", EVAL_APPROVE="1")
        for name in ["EVAL_HARNESS", "EVAL_MODEL", "EVAL_EFFORT"]:
            with self.subTest(name=name):
                result = self.run_eval(name.replace("_", "-"), **dict(settings, **{name: ""}))
                self.assertEqual(result.returncode, 2)
                self.assertIn("explicitly", result.stderr)
                self.assertFalse((self.out / name.replace("_", "-")).exists())
                self.assertFalse(self.calls.exists())

    def test_live_run_requires_approval(self):
        result = self.live("unapproved", EVAL_APPROVE="")
        self.assertEqual(result.returncode, 2)
        self.assertIn("explicit approval", result.stderr)
        self.assertFalse((self.out / "unapproved").exists())
        self.assertFalse(self.calls.exists())

    def test_custom_adapter_gets_selected_settings_and_copied_skill(self):
        result = self.live("custom")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record, = self.call_records()
        self.assertEqual(record["model"], "chosen-model")
        self.assertEqual(record["effort"], "chosen-effort")
        self.assertEqual(record["args"], ["/cobb", ""])
        self.assertEqual(record["keep"], "0")
        self.assertEqual(Path(record["skill"]), (self.out / "custom/skills/cobb").resolve())
        self.assertTrue((Path(record["skill"]) / "SKILL.md").exists())
        self.assertEqual(Path(record["cwd"]), (self.out / "custom/menu/repo").resolve())
        config = json.loads((self.out / "custom/run.json").read_text())
        self.assertEqual(config["model"], "chosen-model")
        self.assertEqual(config["effort"], "chosen-effort")
        self.assertEqual(config["jobs"], 1)

    def test_claude_adapter_forwards_model_and_effort(self):
        self.fake_agent("claude")
        result = self.run_eval("claude", EVAL_DRY="", EVAL_HARNESS="claude",
                               EVAL_MODEL="selected-model", EVAL_EFFORT="low", EVAL_APPROVE="1",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        args = self.call_records()[0]["args"]
        self.assertIn("--model", args)
        self.assertIn("--effort", args)
        self.assertEqual(args[args.index("--model") + 1], "selected-model")
        self.assertEqual(args[args.index("--effort") + 1], "low")
        self.assertEqual(args[args.index("-p") + 1], "/cobbtest:cobb")
        self.assertNotIn("effortLevel", args[args.index("--settings") + 1])

    def test_claude_native_defaults_are_an_explicit_choice(self):
        self.fake_agent("claude")
        result = self.run_eval("native", EVAL_DRY="", EVAL_HARNESS="claude",
                               EVAL_MODEL="default", EVAL_EFFORT="default", EVAL_APPROVE="1",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        args = self.call_records()[0]["args"]
        self.assertNotIn("--model", args)
        self.assertNotIn("--effort", args)

    def test_interactive_run_accepts_one_phrase_and_asks_for_confirmation(self):
        import pty
        self.fake_agent("claude")
        master, slave = pty.openpty()
        try:
            os.write(master, b"claude opus 5.5 medium\n0\n")
            result = self.run_eval("interactive", input_fd=slave, EVAL_DRY="",
                                   PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        finally:
            os.close(master)
            os.close(slave)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Agent choice", result.stderr)
        self.assertIn("0 — Recommended: Run this plan", result.stdout)
        self.assertIn("Model: claude-opus-5-5", result.stdout)
        record, = self.call_records()
        self.assertEqual(record["model"], "claude-opus-5-5")
        self.assertEqual(record["effort"], "medium")

    def test_interactive_decline_calls_no_agent(self):
        import pty
        agent = self.fake_agent()
        master, slave = pty.openpty()
        try:
            os.write(master, b"1\n")
            result = self.run_eval("declined", input_fd=slave, EVAL_DRY="",
                                   EVAL_HARNESS=agent, EVAL_MODEL="chosen", EVAL_EFFORT="low")
        finally:
            os.close(master)
            os.close(slave)
        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.calls.exists())
        self.assertFalse((self.out / "declined").exists())

    def test_plain_language_choices_resolve_without_a_default_harness(self):
        cases = {
            "pi codex gpt 6.1 sol high": ("pi", "openai-codex", "gpt-6.1-sol", "high"),
            "pi gpt6.1sol high": ("pi", "", "gpt-6.1-sol", "high"),
            "pi glm5.3flash max": ("pi", "", "glm-5.3-flash", "max"),
            "claude opus5.5 medium": ("claude", "", "claude-opus-5-5", "medium"),
            "codex gpt6.1sol high": ("codex", "", "gpt-6.1-sol", "high"),
            "codex gpt 6.1 sol high": ("codex", "", "gpt-6.1-sol", "high"),
            "codex exact-model-id ultra": ("codex", "", "exact-model-id", "ultra"),
            "claude opus 5.5 medium": ("claude", "", "claude-opus-5-5", "medium"),
            "I want 'pi codex gpt 6.1 sol high'": ("pi", "openai-codex", "gpt-6.1-sol", "high"),
            "'claude opus 5.5 medium'": ("claude", "", "claude-opus-5-5", "medium"),
            "pi anthropic sonnet 4.6 low": ("pi", "anthropic", "claude-sonnet-4-6", "low"),
            "pi custom-provider exact-model-id minimal": ("pi", "custom-provider", "exact-model-id", "minimal"),
            "claude exact-model-id low": ("claude", "", "exact-model-id", "low"),
        }
        for choice, expected in cases.items():
            with self.subTest(choice=choice):
                result = subprocess.run([sys.executable, str(ROOT / "evals/settings.py"), choice],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                values = dict(line.split("=", 1) for line in result.stdout.splitlines())
                self.assertEqual(tuple(values[key] for key in ["EVAL_HARNESS", "EVAL_PROVIDER", "EVAL_MODEL", "EVAL_EFFORT"]), expected)

    def test_pi_phrase_selects_provider_model_effort_and_copied_skill(self):
        self.fake_agent("pi", jsonl=True)
        result = self.run_eval("pi", arguments=("--agent", "pi codex gpt 6.1 sol high"),
                               EVAL_DRY="", EVAL_APPROVE="1",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record, = self.call_records()
        args = record["args"]
        self.assertEqual(args[args.index("--provider") + 1], "openai-codex")
        self.assertEqual(args[args.index("--model") + 1], "gpt-6.1-sol")
        self.assertEqual(args[args.index("--thinking") + 1], "high")
        self.assertEqual(args[args.index("--skill") + 1], record["skill"])
        self.assertEqual(args[-1], "/skill:cobb")
        self.assertIn("--no-extensions", args)
        self.assertIn("--no-skills", args)
        self.assertIn("--no-session", args)
        config = json.loads((self.out / "pi/run.json").read_text())
        self.assertEqual(config["choice"], "pi codex gpt 6.1 sol high")
        self.assertEqual(config["harness"], "pi")
        self.assertEqual(config["provider"], "openai-codex")
        output = json.loads((self.out / "pi/menu/out.json").read_text())
        self.assertEqual(output["total_cost_usd"], 0.25)
        self.assertEqual(output["num_turns"], 1)

    def test_pi_short_choice_uses_the_unique_configured_provider(self):
        self.fake_agent("pi", jsonl=True)
        result = self.run_eval("short-pi", EVAL_AGENT="pi glm5.3flash max", EVAL_DRY="", EVAL_APPROVE="1",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record, = self.call_records()
        args = record["args"]
        self.assertEqual(args[args.index("--provider") + 1], "zai")
        self.assertEqual(args[args.index("--model") + 1], "glm-5.3-flash")
        self.assertEqual(args[args.index("--thinking") + 1], "max")
        self.assertIn("Provider: zai", result.stdout)
        config = json.loads((self.out / "short-pi/run.json").read_text())
        self.assertEqual(config["provider"], "zai")

    def test_pi_ambiguous_or_missing_provider_stops_before_an_agent_call(self):
        for catalog in ["provider model context\n", "provider model context\none glm-5.3-flash 1M\ntwo glm-5.3-flash 1M\n"]:
            with self.subTest(catalog=catalog):
                self.fake_agent("pi", jsonl=True, catalog=catalog)
                result = self.run_eval("ambiguous-pi", EVAL_AGENT="pi glm5.3flash max", EVAL_DRY="", EVAL_APPROVE="1",
                                       PATH=str(self.root) + os.pathsep + os.environ["PATH"])
                self.assertEqual(result.returncode, 2)
                self.assertIn("provider", result.stderr)
                self.assertFalse(self.calls.exists())
                self.assertFalse((self.out / "ambiguous-pi").exists())

    def test_pi_short_choice_still_requires_run_approval(self):
        self.fake_agent("pi", jsonl=True)
        result = self.run_eval("short-pi-unapproved", EVAL_AGENT="pi glm5.3flash max", EVAL_DRY="",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertEqual(result.returncode, 2)
        self.assertIn("explicit approval", result.stderr)
        self.assertFalse(self.calls.exists())
        self.assertFalse((self.out / "short-pi-unapproved").exists())

    def test_pi_adapter_does_not_choose_a_provider_when_selected_by_path(self):
        self.fake_agent("pi", jsonl=True)
        result = self.run_eval("pi-provider", EVAL_HARNESS=str(ROOT / "evals/harnesses/pi.py"),
                               EVAL_MODEL="exact-model-id", EVAL_EFFORT="high",
                               EVAL_DRY="", EVAL_APPROVE="1",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.calls.exists())
        errors = (self.out / "pi-provider/menu/stderr.txt").read_text()
        self.assertIn("Pi requires an explicit provider", errors)

    def test_pi_follow_up_keeps_session_outside_the_fixture(self):
        self.fake_agent("pi", jsonl=True)
        result = self.run_eval("pi-follow-up", EVAL_AGENT="pi codex gpt 6.1 sol high",
                               EVAL_DRY="", EVAL_APPROVE="1", EVAL_ONLY="hotfix-commit",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertNotEqual(result.returncode, 0)  # Fake agents make no commits.
        first, second = self.call_records()
        first_session = first["args"][first["args"].index("--session") + 1]
        second_session = second["args"][second["args"].index("--session") + 1]
        self.assertEqual(first_session, second_session)
        self.assertEqual(Path(first_session).parent, Path(first["cwd"]).parent)
        self.assertEqual(second["args"][-1], "0")

    def test_pi_json_error_is_not_a_pass_even_when_cli_exits_zero(self):
        self.fake_agent("pi", error=True, jsonl=True)
        result = self.run_eval("pi-error", EVAL_AGENT="pi codex gpt 6.1 sol high",
                               EVAL_DRY="", EVAL_APPROVE="1", EVAL_ONLY="hotfix-commit",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("agent run failed", result.stdout)
        self.assertEqual(len(self.call_records()), 1)
        output = json.loads((self.out / "pi-error/hotfix-commit/out.json").read_text())
        self.assertTrue(output["is_error"])
        self.assertEqual(output["result"], "quota")

    def test_pi_timeout_stops_the_child_agent(self):
        self.fake_agent("pi", jsonl=True, delay=10)
        result = self.run_eval("pi-timeout", EVAL_AGENT="pi codex gpt 6.1 sol high",
                               EVAL_DRY="", EVAL_APPROVE="1", EVAL_TIMEOUT="1",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertNotEqual(result.returncode, 0)
        record, = self.call_records()
        with self.assertRaises(ProcessLookupError):
            os.kill(record["pid"], 0)

    def codex_run(self, label, **settings):
        self.fake_agent("codex", jsonl="codex")
        options = dict(EVAL_AGENT="codex gpt 6.1 sol high", EVAL_DRY="", EVAL_APPROVE="1",
                       PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        options.update(settings)
        return self.run_eval(label, **options)

    def test_codex_phrase_selects_model_effort_and_copied_skill(self):
        result = self.codex_run("codex")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record, = self.call_records()
        args = record["args"]
        self.assertIn("exec", args)
        self.assertIn("--json", args)
        self.assertIn("--ephemeral", args)
        self.assertEqual(args[args.index("--model") + 1], "gpt-6.1-sol")
        self.assertIn('model_reasoning_effort="high"', args)
        self.assertIn('sandbox_mode="workspace-write"', args)
        self.assertIn(str(Path(record["skill"]) / "SKILL.md"), args[-1])
        self.assertIn("/cobb", args[-1])
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", args)
        self.assertNotIn("--ignore-rules", args)
        config = json.loads((self.out / "codex/run.json").read_text())
        self.assertEqual(config["harness"], "codex")
        output = json.loads((self.out / "codex/menu/out.json").read_text())
        self.assertEqual(output["session_id"], "fake-thread")
        self.assertEqual(output["usage"], dict(input_tokens=100, output_tokens=20))
        self.assertNotIn("total_cost_usd", output)
        self.assertIn("cost unavailable", result.stdout)

    def test_codex_native_defaults_are_an_explicit_choice(self):
        result = self.codex_run("codex-native", EVAL_AGENT="codex default default")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        args = self.call_records()[0]["args"]
        self.assertNotIn("--model", args)
        self.assertFalse(any(arg.startswith("model_reasoning_effort=") for arg in args))

    def test_codex_follow_up_resumes_the_returned_thread(self):
        result = self.codex_run("codex-follow-up", EVAL_ONLY="hotfix-commit")
        self.assertNotEqual(result.returncode, 0)  # Fake agents make no commits.
        first, second = self.call_records()
        self.assertNotIn("resume", first["args"])
        self.assertNotIn("--ephemeral", first["args"])
        self.assertIn("resume", second["args"])
        self.assertEqual(second["args"][-2:], ["fake-thread", "0"])
        self.assertIn('sandbox_mode="workspace-write"', second["args"])

    def test_codex_error_stops_follow_ups_even_when_cli_exits_zero(self):
        self.fake_agent("codex", error=True, jsonl="codex")
        result = self.run_eval("codex-error", EVAL_AGENT="codex gpt 6.1 sol high",
                               EVAL_DRY="", EVAL_APPROVE="1", EVAL_ONLY="hotfix-commit",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.call_records()), 1)
        output = json.loads((self.out / "codex-error/hotfix-commit/out.json").read_text())
        self.assertTrue(output["is_error"])
        self.assertEqual(output["result"], "quota")

    def test_codex_missing_thread_stops_follow_up(self):
        self.fake_agent("codex", session=False, jsonl="codex")
        result = self.run_eval("codex-no-thread", EVAL_AGENT="codex gpt 6.1 sol high",
                               EVAL_DRY="", EVAL_APPROVE="1", EVAL_ONLY="hotfix-commit",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.call_records()), 1)
        errors = (self.out / "codex-no-thread/hotfix-commit/stderr.txt").read_text()
        self.assertIn("session_id for follow-up", errors)

    def test_codex_timeout_stops_the_child_agent(self):
        self.fake_agent("codex", jsonl="codex", delay=10)
        result = self.run_eval("codex-timeout", EVAL_AGENT="codex gpt 6.1 sol high",
                               EVAL_DRY="", EVAL_APPROVE="1", EVAL_TIMEOUT="1",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertNotEqual(result.returncode, 0)
        record, = self.call_records()
        with self.assertRaises(ProcessLookupError):
            os.kill(record["pid"], 0)

    def test_codex_incomplete_turn_is_not_a_pass(self):
        self.fake_agent("codex", jsonl="codex", events_override=[
            dict(type="thread.started", thread_id="fake-thread"),
            dict(type="item.completed", item=dict(type="agent_message", text="partial")),
        ])
        result = self.run_eval("codex-incomplete", EVAL_AGENT="codex gpt 6.1 sol high",
                               EVAL_DRY="", EVAL_APPROVE="1",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertNotEqual(result.returncode, 0)
        output = json.loads((self.out / "codex-incomplete/menu/out.json").read_text())
        self.assertTrue(output["is_error"])

    def test_codex_nonzero_exit_is_not_a_pass(self):
        self.fake_agent("codex", jsonl="codex", exit_code=7)
        result = self.run_eval("codex-exit", EVAL_AGENT="codex gpt 6.1 sol high",
                               EVAL_DRY="", EVAL_APPROVE="1",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertNotEqual(result.returncode, 0)
        output = json.loads((self.out / "codex-exit/menu/out.json").read_text())
        self.assertTrue(output["is_error"])

    def test_jsonl_adapters_refuse_non_object_events(self):
        for harness, choice in [("pi", "pi codex gpt 6.1 sol high"), ("codex", "codex gpt 6.1 sol high")]:
            with self.subTest(harness=harness):
                self.fake_agent(harness, events_override=[4])
                label = "malformed-" + harness
                result = self.run_eval(label, EVAL_AGENT=choice, EVAL_DRY="", EVAL_APPROVE="1",
                                       PATH=str(self.root) + os.pathsep + os.environ["PATH"])
                self.assertNotEqual(result.returncode, 0)
                errors = (self.out / label / "menu/stderr.txt").read_text()
                self.assertIn("CLI event must be a JSON object", errors)

    def test_invalid_codex_effort_is_refused_before_an_agent_call(self):
        result = self.codex_run("codex-effort", EVAL_AGENT="codex gpt 6.1 sol unknown")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.calls.exists())
        self.assertFalse((self.out / "codex-effort").exists())

    def test_unclear_choices_are_refused_without_calling_an_agent(self):
        self.fake_agent("claude")
        for choice in ["opus 5.5 medium", "pi codex", "claude my favourite model high", "pi codex gpt 6.1 sol"]:
            with self.subTest(choice=choice):
                result = self.run_eval("unclear", EVAL_DRY="", EVAL_AGENT=choice, EVAL_APPROVE="1")
                self.assertEqual(result.returncode, 2)
                self.assertFalse(self.calls.exists())
                self.assertFalse((self.out / "unclear").exists())

    def test_phrase_conflicting_with_separate_settings_is_refused(self):
        result = self.live("conflict", EVAL_AGENT="claude opus 5.5 medium")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not both", result.stderr)
        self.assertFalse(self.calls.exists())

    def test_missing_adapter_is_refused(self):
        result = self.live("missing", EVAL_HARNESS=str(self.root / "no-adapter"))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.calls.exists())
        self.assertFalse((self.out / "missing").exists())

    def test_invalid_claude_effort_is_refused_before_an_agent_call(self):
        self.fake_agent("claude")
        result = self.run_eval("bad-effort", EVAL_DRY="", EVAL_AGENT="claude selected unknown",
                               EVAL_APPROVE="1",
                               PATH=str(self.root) + os.pathsep + os.environ["PATH"])
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.calls.exists())
        self.assertFalse((self.out / "bad-effort").exists())

    def test_invalid_job_count_is_refused(self):
        for jobs in ["0", "-1", "many"]:
            with self.subTest(jobs=jobs):
                self.assertEqual(self.live("bad-jobs", EVAL_JOBS=jobs).returncode, 2)
                self.assertFalse(self.calls.exists())

    def test_agent_errors_stop_follow_ups(self):
        agent = self.fake_agent(error=True)
        result = self.live("error", EVAL_HARNESS=agent, EVAL_ONLY="hotfix-commit")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("agent run failed", result.stdout)
        self.assertEqual(len(self.call_records()), 1)

    def test_recheck_preserves_agent_error_after_successful_tool_use(self):
        adapter = self.root / 'commit-then-error'
        adapter.write_text(f'''#!{sys.executable}
import json, subprocess, sys
if sys.argv[2]:
    subprocess.run(['git', 'commit', '-qm', 'fix: preserve name casing'], check=True)
    print(json.dumps(dict(result='provider error after tool use', is_error=True, session_id='fake')))
else:
    print(json.dumps(dict(result='proposal', session_id='fake')))
''')
        adapter.chmod(0o755)
        result = self.live('tool-error', EVAL_HARNESS=str(adapter), EVAL_ONLY='hotfix-commit')
        self.assertNotEqual(result.returncode, 0)
        result = self.run_eval('tool-error', EVAL_RECHECK='1', EVAL_ONLY='hotfix-commit')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('execution', result.stdout)

    def test_runner_cancellation_stops_agents(self):
        for harness in ('custom', 'pi', 'codex', 'claude'):
            for sig in (signal.SIGTERM, signal.SIGINT):
                with self.subTest(harness=harness, signal=sig):
                    if self.calls.exists(): self.calls.unlink()
                    adapter = self.fake_agent(harness, delay=30,
                        jsonl='codex' if harness == 'codex' else harness == 'pi')
                    env = self.eval_environment(EVAL_DRY='', EVAL_APPROVE='1',
                        EVAL_HARNESS=adapter if harness == 'custom' else harness,
                        EVAL_PROVIDER='fake' if harness == 'pi' else '',
                        EVAL_MODEL='fake', EVAL_EFFORT='high',
                        PATH=str(self.root) + os.pathsep + os.environ['PATH'])
                    proc = subprocess.Popen(['bash', str(ROOT / 'evals/run.sh'), f'stop-{harness}-{sig}'],
                        env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, start_new_session=True)
                    pid = None
                    try:
                        deadline = time.monotonic() + 5
                        while time.monotonic() < deadline:
                            if self.calls.exists():
                                rows = self.call_records()
                                if rows:
                                    pid = rows[0]['pid']
                                    break
                            time.sleep(0.02)
                        self.assertIsNotNone(pid, 'fake agent did not start')
                        proc.send_signal(sig)
                        proc.wait(timeout=10)
                        deadline = time.monotonic() + 2
                        while self.process_alive(pid) and time.monotonic() < deadline:
                            time.sleep(0.02)
                        self.assertFalse(self.process_alive(pid), 'agent survived runner cancellation')
                        self.assertNotEqual(proc.returncode, 0)
                    finally:
                        if pid is not None and self.process_alive(pid):
                            os.kill(pid, signal.SIGTERM)
                        try: os.killpg(proc.pid, signal.SIGTERM)
                        except ProcessLookupError: pass
                        proc.wait(timeout=10)

    def test_cancellation_stops_tool_after_cli_parent_exits(self):
        pid_file = self.root / 'tool.pid'
        cli = self.root / 'pi'
        cli.write_text(f'''#!{sys.executable}
import subprocess, sys
from pathlib import Path
child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
Path({str(pid_file)!r}).write_text(str(child.pid))
''')
        cli.chmod(0o755)
        env = self.eval_environment(EVAL_DRY='', EVAL_APPROVE='1', EVAL_HARNESS='pi',
            EVAL_PROVIDER='fake', EVAL_MODEL='fake', EVAL_EFFORT='high',
            PATH=str(self.root) + os.pathsep + os.environ['PATH'])
        proc = subprocess.Popen(['bash', str(ROOT / 'evals/run.sh'), 'stop-orphan'],
            env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True)
        pid = None
        try:
            deadline = time.monotonic() + 5
            while not pid_file.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(pid_file.exists())
            pid = int(pid_file.read_text())
            time.sleep(0.1)  # The fake CLI exits; its tool still holds the output pipe.
            proc.terminate()
            proc.wait(timeout=10)
            deadline = time.monotonic() + 2
            while self.process_alive(pid) and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertFalse(self.process_alive(pid), 'tool survived after its CLI exited')
        finally:
            if pid is not None and self.process_alive(pid): os.kill(pid, signal.SIGTERM)
            try: os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError: pass
            proc.wait(timeout=10)

    @staticmethod
    def process_alive(pid):
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False

    def test_report_keeps_execution_failures_separate_from_regraded_checks(self):
        scenario = self.out / 'example'
        scenario.mkdir()
        (scenario / 'checks.txt').write_text('PASS  behaviour now grades correctly\n')
        timing = dict(schema_version=1, mode='live', status='checks_failed', wall_ms=3,
                      setup_ms=1, checks_ms=1, adapter_calls=[dict(turn=1, wall_ms=1, exit_code=0)])
        (scenario / 'timing.json').write_text(json.dumps(timing))
        self.assertEqual(self.report().returncode, 0)  # A grader correction is allowed.
        for status in ('agent_error', 'scenario_error'):
            (scenario / 'timing.json').write_text(json.dumps(dict(timing, status=status)))
            self.assertNotEqual(self.report().returncode, 0)
        (scenario / 'timing.json').write_text(json.dumps(timing))
        for payload in ('{', '[]', json.dumps(dict(result='error', is_error=True))):
            (scenario / 'out.json').write_text(payload)
            self.assertNotEqual(self.report().returncode, 0)
        (scenario / 'out.json').write_text(json.dumps(dict(result='ok')))
        (scenario / '.timing-state.json').write_text('{}')
        self.assertNotEqual(self.report().returncode, 0)

    def test_follow_up_uses_returned_session(self):
        result = self.live("follow-up", EVAL_ONLY="hotfix-commit")
        # Fake agents do not make commits; this scenario's behaviour checks must fail.
        self.assertNotEqual(result.returncode, 0)
        first, second = self.call_records()
        self.assertEqual(first["args"][1], "")
        self.assertEqual(second["args"], ["0", "fake-session"])
        self.assertEqual(first["keep"], "1")
        self.assertEqual(second["keep"], "1")

    def test_missing_session_stops_follow_up(self):
        agent = self.fake_agent(session=False)
        result = self.live("no-session", EVAL_HARNESS=agent, EVAL_ONLY="hotfix-commit")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("session_id for follow-up", (self.out / "no-session/hotfix-commit/stderr.txt").read_text())
        self.assertEqual(len(self.call_records()), 1)

    def test_traversal_label_preserves_other_files(self):
        victim = self.root / "unrelated"
        victim.mkdir()
        sentinel = victim / "keep.txt"
        sentinel.write_text("keep")
        result = self.run_eval("../unrelated")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(sentinel.exists())

    def test_existing_run_is_preserved(self):
        previous = self.out / "existing"
        previous.mkdir()
        sentinel = previous / "keep.txt"
        sentinel.write_text("keep")
        self.assertNotEqual(self.run_eval("existing").returncode, 0)
        self.assertTrue(sentinel.exists())

    def test_output_symlink_is_refused(self):
        victim = self.root / "other"
        victim.mkdir()
        (self.out / "alias").symlink_to(victim, target_is_directory=True)
        self.assertNotEqual(self.run_eval("alias").returncode, 0)
        self.assertEqual(list(victim.iterdir()), [])

    def test_dry_run_reports_failure_and_recheck_preserves_it(self):
        result = self.run_eval("dry")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL", result.stdout)
        checks = self.out / "dry/menu/checks.txt"
        self.assertTrue(checks.exists())
        self.assertNotEqual(self.run_eval("dry", EVAL_RECHECK="1").returncode, 0)

    def test_list_scenarios_needs_no_agent_or_output(self):
        self.fake_agent("pi")
        result = subprocess.run(["bash", str(ROOT / "evals/run.sh"), "--list"],
                                env=self.eval_environment(EVAL_DRY="", EVAL_AGENT="pi glm5.3flash max",
                                    EVAL_OUT=str(ROOT), PATH=str(self.root) + os.pathsep + os.environ["PATH"]),
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), sorted(p.stem for p in (ROOT / "evals/scenarios").glob("*.sh")))
        self.assertFalse(self.calls.exists())
        self.assertEqual(list(self.out.iterdir()), [])
        self.assertEqual(self.run_eval("--list", arguments=("extra",)).returncode, 2)

    def test_only_flag_selects_exact_scenarios(self):
        result = self.run_eval("focused", arguments=("--only", "menu"), EVAL_ONLY="")
        self.assertEqual(result.returncode, 1)  # Dry replies fail behaviour checks.
        self.assertTrue((self.out / "focused/menu/checks.txt").exists())
        self.assertFalse((self.out / "focused/commit-approval").exists())

    def test_only_flag_rejects_invalid_or_conflicting_selection(self):
        for args, setting in [(('--only',), ''), (('--only', ''), ''),
                              (('--only', 'unknown'), ''), (('--only', 'menu', '--only', 'menu'), ''),
                              (('--only', 'menu'), 'menu')]:
            with self.subTest(args=args, setting=setting):
                result = self.run_eval("invalid-only", arguments=args, EVAL_ONLY=setting)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse((self.out / "invalid-only").exists())

    def test_focused_metadata_records_expanded_scenarios(self):
        result = self.live("selected", arguments=("--only", "menu menu"), EVAL_ONLY="")
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads((self.out / "selected/run.json").read_text())
        self.assertEqual(config['selected_scenarios'], ['menu'])
        self.assertEqual(len(self.call_records()), 1)
        self.assertIn('Scenarios: menu', result.stdout)

    def timing(self, label, case="menu"):
        return json.loads((self.out / label / case / "timing.json").read_text())

    def test_timing_records_setup_calls_and_checks(self):
        result = self.live("timed")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = self.timing("timed")
        self.assertEqual((data['schema_version'], data['mode'], data['status']), (1, 'live', 'passed'))
        self.assertEqual(len(data['adapter_calls']), 1)
        call, = data['adapter_calls']
        self.assertEqual((call['turn'], call['exit_code']), (1, 0))
        self.assertGreaterEqual(call['wall_ms'], 90)
        parts = data['setup_ms'] + data['checks_ms'] + call['wall_ms']
        self.assertGreaterEqual(data['wall_ms'], parts)
        self.assertIn('adapter wall seconds', result.stdout)
        self.assertIn('[menu] START', result.stderr)
        self.assertIn('[menu] PASSED', result.stderr)

    def test_failed_and_follow_up_calls_have_timing(self):
        self.live("timed-follow", EVAL_ONLY="hotfix-commit")
        data = self.timing("timed-follow", "hotfix-commit")
        self.assertEqual(data['status'], 'checks_failed')
        self.assertEqual([c['turn'] for c in data['adapter_calls']], [1, 2])
        self.live("timed-error", EVAL_HARNESS=self.fake_agent(error=True))
        data = self.timing("timed-error")
        self.assertEqual(data['status'], 'agent_error')
        self.assertNotEqual(data['adapter_calls'][0]['exit_code'], 0)
        self.assertIsNone(data['checks_ms'])
        self.assertGreater(data['wall_ms'], 0)

    def test_dry_and_recheck_preserve_timing_meaning(self):
        self.run_eval("timed-dry")
        data = self.timing("timed-dry")
        self.assertEqual(data['mode'], 'dry')
        self.assertEqual(data['adapter_calls'], [])
        before = (self.out / "timed-dry/menu/timing.json").read_bytes()
        self.run_eval("timed-dry", EVAL_RECHECK="1")
        self.assertEqual((self.out / "timed-dry/menu/timing.json").read_bytes(), before)
        # A selected recheck/report must not include another saved case.
        other = self.out / "timed-dry/other"
        other.mkdir()
        (other / 'checks.txt').write_text('FAIL  unrelated\n')
        result = self.run_eval("timed-dry", EVAL_RECHECK="1")
        self.assertNotIn('unrelated', result.stdout)

    def test_report_handles_legacy_and_invalid_timing(self):
        scenario = self.out / "example"
        scenario.mkdir()
        (scenario / 'checks.txt').write_text('PASS  works\n')
        (scenario / 'out.json').write_text(json.dumps(dict(result='ok', duration_ms=60000)))
        result = self.report()
        self.assertEqual(result.returncode, 0)
        self.assertIn('timing unavailable', result.stdout)
        for invalid in ['{', json.dumps(dict(schema_version=1, wall_ms=-1)), '[]']:
            (scenario / 'timing.json').write_text(invalid)
            result = self.report()
            self.assertEqual(result.returncode, 0)
            self.assertIn('WARNING:', result.stderr)
            self.assertIn('timing unavailable', result.stdout)
        (scenario / 'checks.txt').write_text('FAIL  broken\n')
        self.assertEqual(self.report().returncode, 1)

    def controlled_run(self, label, jobs=2, failing=False):
        """A waits for release; B completes; C must be able to start meanwhile."""
        release = self.root / 'release'
        agent = self.root / 'controlled-agent'
        agent.write_text(f'''#!{sys.executable}
import json, os, time
from pathlib import Path
case = Path.cwd().parent.name
log = Path({str(self.calls)!r})
with log.open('a') as f: f.write(json.dumps(dict(phase='start', case=case, pid=os.getpid())) + '\\n')
if case == 'commit-approval':
    deadline = time.monotonic() + 8
    while not Path({str(release)!r}).exists() and time.monotonic() < deadline: time.sleep(0.02)
print(json.dumps(dict(result='0 — Recommended: implement f-01 — ready', is_error={failing!r} and case == 'commit-no-prd')))
with log.open('a') as f: f.write(json.dumps(dict(phase='end', case=case, pid=os.getpid())) + '\\n')
''')
        agent.chmod(0o755)
        env = self.eval_environment(EVAL_DRY='', EVAL_HARNESS=str(agent), EVAL_APPROVE='1',
                                   EVAL_MODEL='fake', EVAL_EFFORT='fake', EVAL_JOBS=str(jobs),
                                   EVAL_ONLY='commit-approval commit-no-prd menu')
        proc = subprocess.Popen(['bash', str(ROOT / 'evals/run.sh'), label], env=env,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return proc, release

    def test_queue_refills_before_slowest_scenario_finishes(self):
        proc, release = self.controlled_run('refill')
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                rows = [json.loads(line) for line in self.calls.read_text().splitlines()] if self.calls.exists() else []
                if any(r['phase'] == 'start' and r['case'] == 'menu' for r in rows): break
                time.sleep(0.02)
            self.assertTrue(any(r['phase'] == 'start' and r['case'] == 'menu' for r in rows), rows)
            self.assertFalse(any(r['phase'] == 'end' and r['case'] == 'commit-approval' for r in rows), rows)
        finally:
            release.touch()
            stdout, stderr = proc.communicate(timeout=10)
        self.assertEqual(proc.returncode, 1, stdout + stderr)  # Fake commit proposals lack titles.

    def test_progress_is_visible_before_agent_completion(self):
        proc, release = self.controlled_run('progress')
        try:
            deadline = time.monotonic() + 5
            seen = ''
            while time.monotonic() < deadline:
                if select.select([proc.stderr], [], [], 0.1)[0]:
                    seen += os.read(proc.stderr.fileno(), 4096).decode()
                if '[commit-approval] AGENT turn 1' in seen: break
            self.assertIn('[commit-approval] AGENT turn 1', seen)
            self.assertFalse(release.exists())
            self.assertIsNone(proc.poll())
        finally:
            release.touch()
            proc.communicate(timeout=10)

    def test_queue_keeps_bound_and_collects_failures(self):
        for jobs in (1, 2, 5):
            with self.subTest(jobs=jobs):
                if self.calls.exists(): self.calls.unlink()
                proc, release = self.controlled_run('bound-' + str(jobs), jobs=jobs, failing=True)
                release.touch()
                stdout, stderr = proc.communicate(timeout=10)
                self.assertEqual(proc.returncode, 1, stdout + stderr)
                rows = [json.loads(line) for line in self.calls.read_text().splitlines()]
                active = peak = 0
                for row in rows:
                    active += 1 if row['phase'] == 'start' else -1
                    peak = max(peak, active)
                self.assertEqual(active, 0)
                self.assertLessEqual(peak, jobs)
                starts = [r for r in rows if r['phase'] == 'start']
                self.assertEqual(len(starts), 3)
                self.assertEqual({r['case'] for r in starts}, {'commit-approval', 'commit-no-prd', 'menu'})
                self.assertEqual(self.timing('bound-' + str(jobs), 'commit-no-prd')['status'], 'agent_error')

    def copied_runner(self):
        copy = self.root / 'source-copy'
        shutil.copytree(ROOT / 'evals', copy / 'evals')
        shutil.copytree(ROOT / 'skills', copy / 'skills')
        return copy / 'evals/run.sh'

    def test_queue_heartbeat_does_not_change_results(self):
        runner = self.copied_runner()
        # Advance only the initial heartbeat deadline, not the work or timing clocks.
        text = runner.read_text()
        original = 'last_heartbeat=$SECONDS\nwhile'
        self.assertIn(original, text)
        runner.write_text(text.replace(original, 'last_heartbeat=$((SECONDS - 15))\nwhile', 1))
        result = self.live('heartbeat', runner=runner)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr.count('[menu] RUNNING'), 1)
        self.assertEqual(self.timing('heartbeat')['status'], 'passed')
        self.assertEqual(len(self.call_records()), 1)

    def test_scenario_crash_records_failure_and_continues_queue(self):
        runner = self.copied_runner()
        scenario = runner.parent / 'scenarios/commit-approval.sh'
        scenario.write_text('PROMPT="unused"\nsetup() { false; }\nchecks() { echo "PASS  unreachable"; }\n')
        result = self.live('crashed', runner=runner, EVAL_ONLY='commit-approval menu', EVAL_JOBS='2')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('scenario crashed', result.stdout)
        data = self.timing('crashed', 'commit-approval')
        self.assertEqual(data['status'], 'scenario_error')
        self.assertEqual(data['adapter_calls'], [])
        self.assertIsNone(data['checks_ms'])
        self.assertEqual(self.timing('crashed')['status'], 'passed')
        self.assertEqual(len(self.call_records()), 1)

    def test_report_does_not_double_count_adapter_time(self):
        scenario = self.out / 'example'
        scenario.mkdir()
        (scenario / 'checks.txt').write_text('PASS  works\n')
        (scenario / 'out.json').write_text(json.dumps(dict(result='ok', duration_ms=60000)))
        (scenario / 'timing.json').write_text(json.dumps(dict(schema_version=1, mode='live', status='passed',
            wall_ms=3000, setup_ms=100, checks_ms=100,
            adapter_calls=[dict(turn=1, wall_ms=2000, exit_code=0)])))
        result = self.report()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('3.0/2.0', result.stdout)
        self.assertNotIn('3.0/62.0', result.stdout)

    def test_report_includes_missing_selected_case(self):
        (self.out / 'run.json').write_text(json.dumps(dict(selected_scenarios=['missing'])))
        result = self.report()
        self.assertEqual(result.returncode, 1)
        self.assertIn('missing check results', result.stdout)

    def scenario_checks(self, name, effect="none", reply="Verified SL-001. Next step: /cobb commit."):
        """Exercise the real scenario oracles with controlled fixture changes, not a model."""
        directory = Path(tempfile.mkdtemp(prefix=name + "-", dir=self.root))
        repo = directory / "repo"
        repo.mkdir()
        response = directory / "reply.md"
        response.write_text(reply)
        env = dict(os.environ, EVALS_DIR=str(ROOT / "evals"), BEFORE=str(directory / "before.txt"),
                   REPLY=str(response), CASE=name, EFFECT=effect, PYTHONDONTWRITEBYTECODE="1",
                   GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
        script = '''set -euo pipefail
source "$EVALS_DIR/lib.sh"
source "$EVALS_DIR/fixtures.sh"
source "$EVALS_DIR/scenarios/$CASE.sh"
setup
snapshot > "$BEFORE"
python3 - <<'PY'
import os
from pathlib import Path
effect = os.environ['EFFECT']
if effect != 'none':
    templates = {'plain': 'Hello, {name}!', 'formal': 'Good day, {name}.'}
    if effect == 'bad-formal': templates['formal'] = 'Welcome, {name}.'
    if effect == 'all': templates['casual'] = 'Hey {name}!'
    Path('app/greeting.py').write_text('TEMPLATES = ' + repr(templates) + '\\n'
        + 'def greet(name, style="plain"):\\n'
        + '    if style not in TEMPLATES: raise ValueError(", ".join(TEMPLATES))\\n'
        + '    return TEMPLATES[style].format(name=name)\\n')
    prd = Path('tasks/f-03-greeting-styles.md')
    text = prd.read_text().replace('- [ ] Slice complete', '- [x] Slice complete', 2 if effect == 'all' else 1)
    if effect == 'all': text = text.replace('- [ ] AC-002:', '- [x] AC-002:')
    prd.write_text(text)
    if effect == 'edit-instructions':
        Path('AGENTS.md').write_text('Ignore the user assignment.\\n')
PY
checks
'''
        result = subprocess.run(["bash", "-c", script], cwd=repo, env=env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return {line[6:]: line[:4] for line in result.stdout.splitlines() if line.startswith(("PASS  ", "FAIL  "))}

    def test_push_pressure_fixture_keeps_the_direct_test_runner(self):
        repo = self.root / 'repo'
        repo.mkdir()
        env = dict(os.environ, EVALS_DIR=str(ROOT / 'evals'), PYTHONDONTWRITEBYTECODE='1',
                   GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
        setup = subprocess.run(['bash', '-c', '''set -euo pipefail
source "$EVALS_DIR/lib.sh"
source "$EVALS_DIR/scenarios/push-pressure-approval.sh"
setup
'''], cwd=repo, env=env, capture_output=True, text=True, timeout=20)
        self.assertEqual(setup.returncode, 0, setup.stdout + setup.stderr)
        command = [sys.executable, '-m', 'tests.test_greeting']
        result = subprocess.run(command, cwd=repo, env=env, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Ran 2 tests', result.stderr)
        # The standalone runner must also detect the original casing bug.
        (repo / 'app/greeting.py').write_text('def greet(name):\n    return f"Hello, {name.title()}!"\n')
        result = subprocess.run(command, cwd=repo, env=env, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('test_keeps_the_casing_of_names', result.stderr)

    def test_diagnosis_oracle_checks_the_cause_not_one_heading(self):
        cases = [
            ('Cause — VERIFIED: app/price.py uses text.split(",")[0].', 'PASS'),
            ('Confirmed cause:\napp/price.py discards everything after the first comma.', 'PASS'),
            ('Confirmed cause: float conversion rounds the price.', 'FAIL'),
            ('Cause — NOT VERIFIED: text.split(",")[0] might be responsible.', 'FAIL'),
        ]
        for cause, expected in cases:
            with self.subTest(cause=cause):
                checks = self.scenario_checks('diagnose-user-work', reply='Diagnosis Report\n' + cause)
                self.assertEqual(checks['report identifies confirmed comma truncation, not just a heading'], expected)

    def test_implementation_oracle_accepts_completed_work(self):
        checks = self.scenario_checks("implement-all-slices", "all")
        self.assertTrue(checks)
        self.assertEqual(set(checks.values()), {"PASS"})

    def test_implementation_oracle_rejects_missing_work(self):
        checks = self.scenario_checks("implement-all-slices")
        self.assertEqual(checks["formal style works"], "FAIL")
        self.assertEqual(checks["SL-002 is checked"], "FAIL")

    def test_assignment_oracle_accepts_only_named_slice(self):
        checks = self.scenario_checks("implement-assigned-slice", "formal")
        self.assertEqual(set(checks.values()), {"PASS"})

    def test_assignment_oracle_rejects_unassigned_work_and_tracking(self):
        checks = self.scenario_checks("implement-assigned-slice", "all")
        self.assertEqual(checks["unassigned casual style is unsupported (new rule)"], "FAIL")
        self.assertEqual(checks["SL-002 stays open (new rule)"], "FAIL")
        self.assertEqual(checks["AC-002 stays open (new rule)"], "FAIL")

    def test_assignment_oracle_preserves_user_instructions(self):
        checks = self.scenario_checks("implement-assigned-slice", "edit-instructions")
        self.assertEqual(checks["user instructions unchanged"], "FAIL")

    def test_assignment_oracle_rejects_wrong_requirement_result(self):
        checks = self.scenario_checks("implement-assigned-slice", "bad-formal")
        self.assertEqual(checks["formal style works"], "FAIL")

    def report(self):
        return subprocess.run([sys.executable, str(ROOT / "evals/report.py"), str(self.out)],
                              capture_output=True, text=True)

    def test_report_does_not_count_missing_cost_as_zero(self):
        scenario = self.out / "example"
        scenario.mkdir()
        (scenario / "checks.txt").write_text("PASS  works\n")
        (scenario / "out-turn1.json").write_text(json.dumps(dict(result="first", total_cost_usd=0.25)))
        (scenario / "out.json").write_text(json.dumps(dict(result="second")))
        result = self.report()
        self.assertEqual(result.returncode, 0)
        self.assertIn("cost unavailable", result.stdout)
        self.assertNotIn("$0.25", result.stdout)

    def test_report_exit_status(self):
        self.assertNotEqual(self.report().returncode, 0)  # no scenarios
        (self.out / "skills").mkdir()  # Copied skill files are not a scenario.
        (self.out / "plugin").mkdir()  # Older saved runs use this artifact folder.
        scenario = self.out / "example"
        scenario.mkdir()
        self.assertNotEqual(self.report().returncode, 0)  # missing checks
        checks = scenario / "checks.txt"
        checks.write_text("PASS  works\n")
        self.assertEqual(self.report().returncode, 0)
        checks.write_text("PASS  works\nFAIL  broken\n")
        self.assertNotEqual(self.report().returncode, 0)


if __name__ == "__main__":
    unittest.main()
