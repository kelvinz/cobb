"""Open a live agentcy lab: a fresh copy of tests/agentcy-lab/ in a temp folder, with claude running there in hc.

The lab sits outside this repository, so its session loads no cobb instructions. Run it in the Herdr app,
where the lab opens as a new tab, or in any terminal and reach it with `hc attach`:
    python3 tests/agentcy_lab.py [--harness claude]
Then answer any startup question there and run `/agentcy init`. Starts a model session.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/agentcy"
FIXTURE = ROOT / "tests/agentcy-lab"

sys.dont_write_bytecode = True  # keep the skill folder free of caches
spec = importlib.util.spec_from_file_location("agentcy", SKILL / "scripts/agentcy.py")
agentcy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agentcy)


def make_lab(lab: Path) -> None:
    shutil.copytree(FIXTURE, lab, dirs_exist_ok=True)
    # The layout skills.sh uses for a project install; the link keeps the skill live while it is edited here.
    (lab / ".agents/skills").mkdir(parents=True)
    (lab / ".agents/skills/agentcy").symlink_to(SKILL)
    (lab / ".claude/skills").mkdir(parents=True)
    (lab / ".claude/skills/agentcy").symlink_to("../../.agents/skills/agentcy")
    for command in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "start the agentcy lab"]):
        agentcy.git(lab, *command)


def working_copy_only(harness: str, lab: Path) -> list[str]:
    """Launch flags that stop a user-level agentcy install from loading in place of the linked working copy."""
    if harness == "claude":
        return ["--setting-sources", "project,local"]  # no user settings, so no user-level skills
    if harness == "pi":
        return ["--no-skills", "--skill", str(lab / ".agents/skills/agentcy")]
    if harness == "codex":
        # Codex lists every copy under one name. Switch off each installed one, unless it is this working copy.
        homes = (Path.home() / ".agents", Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
        installed = dict.fromkeys((home / "skills/agentcy/SKILL.md").resolve() for home in homes)
        off = [f"{{path={json.dumps(str(path))},enabled=false}}" for path in installed
               if path.is_file() and path != SKILL / "SKILL.md"]
        if off:
            return ["-c", f"skills.config=[{','.join(off)}]"]
    return []  # agy needs no flag: there, the lab's copy wins over a user-level one


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--harness", default="claude", help="the command that plays Donna's session")
    args = parser.parse_args()
    lab = Path(tempfile.mkdtemp(prefix=f"agentcy-lab-{time.strftime('%Y%m%d-%H%M%S')}-")).resolve()
    try:
        hc = agentcy.Hc(dry_run=False)
        live = hc.live_names()
        name = next(f"lab-{n}" for n in range(1, 100) if f"lab-{n}" not in live)
        make_lab(lab)
        spec = {"harness": args.harness, "args": working_copy_only(args.harness, lab)}
        address, status = hc.spawn(name, spec, lab, own_tab=True)
    except agentcy.Fail as error:
        shutil.rmtree(lab)  # removes the skill link, not the skill
        sys.exit(f"agentcy_lab: {error}")
    print(json.dumps({"lab": str(lab), "name": name, "address": address, "status": status,
                      "next": f"in the new tab, or with `hc attach {address}`: answer any startup question, "
                              "then run /agentcy init",
                      "cleanup": f"when you finish, close the tab, then run: rm -rf {shlex.quote(str(lab))}"}, indent=2))


if __name__ == "__main__":
    main()
