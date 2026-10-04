"""Resolve a user-supplied agent choice. No paid calls and no default harness."""
import re
import shlex
import subprocess
import sys


def model_id(words):
    name = " ".join(words)
    family = re.fullmatch(r"(opus|sonnet|haiku)[ -]?(\d+(?:\.\d+)*)", name, re.I)
    if family:
        return "claude-" + family[1].lower() + "-" + family[2].replace(".", "-")
    family = re.fullmatch(r"(gpt|glm)[ -]?(\d+(?:\.\d+)*)(?:[ -]?(sol|flash|highspeed|turbo))?", name, re.I)
    if family:
        return "-".join(part.lower() for part in family.groups() if part)
    if len(words) != 1 or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._:/-]*", name):
        raise ValueError("unclear model name; use its exact ID instead of guessing")
    return name


def resolve(choice):
    choice = choice.strip()
    if choice.lower().startswith("i want "):
        choice = choice[len("i want "):]
    words = shlex.split(choice)
    if len(words) == 1 and " " in words[0]:
        words = shlex.split(words[0])
    if not words or words[0].lower() not in ("pi", "claude", "codex"):
        raise ValueError("name the harness: pi, claude, or codex; then name the model and effort")
    harness = words.pop(0).lower()
    if len(words) < 2:
        raise ValueError("include a model and effort; neither is selected automatically")
    effort = words.pop().lower()
    levels = {"default", "low", "medium", "high", "xhigh", "max"}
    if harness == "pi":
        levels.update(("off", "minimal"))
    if harness == "codex":
        levels.update(("none", "minimal", "ultra"))
    if effort not in levels:
        raise ValueError(f"unsupported {harness} effort: {effort}")
    provider = ""
    # The optional provider-qualified form remains available for ambiguous catalog matches.
    if harness == "pi" and len(words) > 1 and words[0].lower() not in ("gpt", "glm", "opus", "sonnet", "haiku"):
        provider = words.pop(0).lower()
        provider = {"codex": "openai-codex"}.get(provider, provider)
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", provider):
            raise ValueError("use a provider ID, for example zai or openai-codex")
    return dict(EVAL_HARNESS=harness, EVAL_PROVIDER=provider, EVAL_MODEL=model_id(words), EVAL_EFFORT=effort)


def pi_model(model):
    if model == "default":
        raise ValueError("Pi needs an explicit provider when its model is default")
    args = ["pi", "--offline", "--no-extensions", "--no-skills", "--no-prompt-templates",
            "--no-themes", "--no-approve", "--list-models"]
    try:
        result = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True,
                                text=True, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError) as error:
        raise ValueError("cannot read Pi's configured model catalog; give an explicit provider") from error
    lines = [line.split() for line in result.stdout.splitlines() if line.strip()]
    if not lines or lines[0][:2] != ["provider", "model"]:
        raise ValueError("cannot read Pi's model table; give an explicit provider")
    key = lambda text: re.sub(r"[-_ ]", "", text).lower()
    matches = sorted({(row[0], row[1]) for row in lines[1:] if len(row) >= 2 and key(row[1]) == key(model)})
    if len(matches) != 1:
        candidates = ", ".join(f"{provider}/{name}" for provider, name in matches) or "none"
        raise ValueError(f"Pi model/provider match is not unique ({candidates}); use pi <provider> <exact-model-id> <effort>")
    provider, model = matches[0]
    return dict(EVAL_PROVIDER=provider, EVAL_MODEL=model)


if __name__ == "__main__":
    try:
        if len(sys.argv) == 2:
            settings = resolve(sys.argv[1])
        elif len(sys.argv) == 3 and sys.argv[1] == "--pi-model":
            settings = pi_model(sys.argv[2])
        else:
            raise ValueError("usage: settings.py '<harness> [provider] <model> <effort>'")
        for key, value in settings.items():
            print(f"{key}={value}")
    except ValueError as error:
        sys.exit(f"ERROR: {error}")
