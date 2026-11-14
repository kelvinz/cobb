# agentcy.json

`init` creates the `agentcy/` folder in the project root with the template's cast, without agent harness, model, or effort settings. It leaves an existing config unchanged; `/agentcy init` then goes through every agent's setting again with the user, from what is installed now. Without init, agentcy uses the same unset cast. The orchestrator discovers local choices and recommends settings for the user to confirm (`SKILL.md`, **Settings**). `set` saves the answers and creates `agentcy/agentcy.json` when it is missing. `agentcy/agentcy.json` records the user's choices for this project, starting from the template with the default cast. Later, `feedback.md` collects the user's feedback and `lessons/` holds one file per agent; commit them with `agentcy.json`. `runs/` and `state.json` are ignored by `agentcy/.gitignore`.

## Shape

```json
{
  "backend": "auto",
  "agents": {
    "donna": {
      "role": "orchestrator",
      "harness": "pi", "model": "<provider/model>", "effort": "medium", "approve": "auto", "args": [],
      "character": "Donna Paulsen", "from": "Suits", "voice": "…"
    },
    "arya": {
      "role": "worker", "use": "mechanical, well-specified work",
      "harness": "pi", "model": "<provider/model>", "effort": "max", "approve": "auto", "args": [],
      "character": "Arya Stark", "from": "Game of Thrones", "voice": "…"
    },
    "edna": {
      "role": "image", "use": "makes and judges images with the tool the user chooses",
      "harness": "pi", "model": "<provider/model>", "effort": "max", "approve": "auto", "args": [],
      "character": "Edna Mode", "from": "The Incredibles", "voice": "…",
      "tools": {
        "codex": {"use": "GPT Image on the user's ChatGPT plan", "harness": "codex", "effort": "medium"},
        "api": {"use": "image API, paid per image", "provider": "gemini", "models": {"gemini": "…", "openai": "…"}}
      }
    }
  }
}
```

The launch settings in `templates/agentcy.json` are examples, not setup defaults. Setup keeps its cast, tools, approval modes, and extra flags; agent harness, model, and effort come from the user's confirmed choices.

- **backend** — where agents run. `auto` (the default) uses T3 Code subagent threads when the orchestrator runs in a T3 Code thread, and herdr-core (`hc`) terminals otherwise. `hc` or `t3` fixes one. In T3 Code, the orchestrator starts each agent with its `delegate_task` tool: `claude`, `codex`, `pi`, and `agy` map to T3 Code's providers, `effort` maps to each provider's effort option, and every agent and tool needs a `model`. `approve: "ask"` asks T3 Code for a supervised child (`approval-required`); `"auto"` keeps the orchestrator's own mode. `args` does not apply; `check` lists it in `backend.not_applied`, and it warns about each agent or tool that T3 Code cannot start. The orchestrator itself cannot be handed off inside T3 Code: start a new T3 Code thread in its setting instead.

Each key in `agents` is the agent's name in agentcy and in `/agentcy <agent>`, and names its lessons file `agentcy/lessons/<agent>.md`: `a-z`, `0-9`, `-`, and `_`, starting with a letter, at most 32 characters, and not `init` or `learn`.

- **role** — what the agent does: `orchestrator`, `worker`, `reviewer`, `researcher`, `learner`, `image`, or `video`. It selects the prompt in `references/roles/`. Exactly one orchestrator (this session) and at least one worker are required. Several agents can share a role; two workers with different models give a fast and a strong worker.
- **use** — when the orchestrator should pick this agent. The orchestrator chooses among agents with the same role by `use`, so make it specific.
- **harness, model, effort, args** — how the agent starts. `harness` is the command that starts it, such as `claude`, `codex`, `pi`, or `agy`. `model` and `effort` become flags for `claude` and `agy` (`--model`, `--effort`), `codex` (`--model`, `-c model_reasoning_effort=`), and `pi` (`--model`, `--thinking`). For another harness, put its flags in `args`. `args` also carries extra launch flags, such as a permission mode the user chooses. Omit `model` or `effort`, or set `default`, to keep the harness's own setting. Omit all three (`harness`, `model`, `effort`) for an agent that has no setting yet: `check` shows its harness as null, `spawn` refuses it, and the orchestrator asks the user before it needs the agent. Codex always starts with `--no-daemon`, so its commands run inside `hc`. When the user's shell is zsh or bash, the agent starts through that shell as an interactive login shell, so it finds the commands that the shell's startup files add, such as pnpm and mise. For the orchestrator these fields are the recorded setting: the user starts its session, and when a session differs, the orchestrator offers to start itself with this setting in a new tab and hand the task over. Without `harness`, the orchestrator is whatever session runs `/agentcy`.
- **approve** — who answers the harness's permission prompts. `auto` starts the harness in its own reviewed auto mode: `claude --permission-mode auto`, `codex --approve-for-me`, `agy --mode auto`. `ask` (the default) leaves every prompt in the agent's terminal for the user. **pi itself has no permission prompts,** so `approve` changes nothing for pi. A pi extension can add them; its prompts then wait in the agent's terminal for the user. Without such an extension, a pi agent runs every command, deletions included, without asking. When that matters, run pi in an operating-system sandbox, a container, or a restricted account, or choose another harness for that agent. A tool inherits the agent's `approve` unless it sets its own. Startup questions, such as trusting the folder (Claude Code, Codex, agy, and pi all ask it in a folder they do not trust yet), still come to the user.
- **character, from, voice** — the persona. Recast by changing them; the key can stay.
- **tools** — optional ways to run the agent, each with its own `use`. `spawn <agent> --tool <name>` picks one. A tool that sets `harness` starts the agent with its own launch fields only; a tool without `harness` keeps the agent's launch and overrides only the fields it sets. Every other field (such as `provider` and `models` on an image `api` tool) reaches the agent as the tool's settings.

## Setting it up with the user

`options` lists installed harnesses that agentcy knows flags for. Its model lists come from `pi --offline --list-models`, the Codex model cache (`models_cache.json` in `CODEX_HOME`, default `~/.codex`), and `CLAUDE_MODELS` in the script. Each list has a `model_source`; `access_verified` is false because discovery makes no authenticated model call. Pi discovery has a ten-second limit; a failed lookup or missing cache leaves the model list empty, not a guessed list, and its `model_source` is `unavailable`. Claude's list is built in, not an account-access check. Add new Claude models to `CLAUDE_MODELS`. Thinking levels come from the built-in harness tables and Codex's cached per-model levels (`model_efforts`).

Donna makes role-based recommendations from this report; the script does not rank model names. `options <agent>... --recommend <agent> <harness>:<model>:<thinking>` validates each proposed setting against discovery and displays it without saving. The harness must be installed, and the thinking level must be one that the harness, or the chosen Codex model, has. A model name is checked only against the pi catalog or the Codex cache. Any name passes for a harness with an empty list, and for Claude, whose built-in list does not hold every name that Claude Code accepts. Repeat `--recommend` for each agent. Current settings remain the proposed defaults when they pass the same checks; otherwise the report flags them with the reason and leaves the decision to the user. T3 Code requires an explicit model. An orchestrator without a setting needs no pick, because it runs in the session that the user starts.

The user's `0` accepts the displayed recommendations. Donna translates it, or numbered overrides, to explicit names from that report before calling `set`. The CLI rejects a literal `set <agent> 0`, so it cannot silently restore template settings. `set` applies the same checks as `--recommend` before it saves. The persona (character, from, voice), `args`, tools, and `approve` stay unchanged; the template sets `approve` to `auto` for every agent. Commits, pushes, deletions, and installs still need the user's approval through the orchestrator's rules. For pi, `check` confirms each model name and puts each unknown name in `warnings`. Continue only when `check` passes with no `warnings`, or the user accepts each warning.

Put the orchestrator on a different provider from the workers that do the most work when the user can. If the orchestrator hits a usage limit, it cannot ask the user anything.
