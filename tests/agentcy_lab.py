"""Open a live agentcy lab: a fresh copy of tests/agentcy-lab/ in a temp folder, with claude running there in hc.

The lab sits outside this repository, so its session loads no cobb instructions. Run it in the Herdr app,
where the lab opens as a new tab, or in any terminal and reach it with `hc attach`:
    python3 tests/agentcy_lab.py [--harness claude]
Then answer any startup question there and run `/agentcy init`. Starts a model session.
"""
import argparse
import importlib.util
import json
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
        address, status = hc.spawn(name, {"harness": args.harness}, lab, own_tab=True)
    except agentcy.Fail as error:
        shutil.rmtree(lab)  # removes the skill link, not the skill
        sys.exit(f"agentcy_lab: {error}")
    print(json.dumps({"lab": str(lab), "name": name, "address": address, "status": status,
                      "next": f"in the new tab, or with `hc attach {address}`: answer any startup question, "
                              "then run /agentcy init",
                      "cleanup": f"when you finish, close the tab, then run: rm -rf {shlex.quote(str(lab))}"}, indent=2))


if __name__ == "__main__":
    main()
