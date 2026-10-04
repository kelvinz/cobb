"""Summarise cobb eval results.

Usage: report.py <results-dir> [<results-dir> ...]

One directory: each scenario's checks, cost, turns, and minutes.
Several directories (for example baseline and candidate): the checks side by side.
Exit 1 if any run has failed or missing checks; exit 0 only when all checks pass.
"""

import json
import sys
from pathlib import Path
sys.dont_write_bytecode = True
from timing import read_timing


def total_cost(costs):
    return sum(costs) if costs and all(cost is not None for cost in costs) else None


def cost_text(cost):
    return f"${cost:.2f}" if cost is not None else "cost unavailable"


def load(run_dir, only=None):
    run_dir = Path(run_dir)
    directories = {p.name for p in run_dir.iterdir() if p.is_dir() and p.name not in ("plugin", "skills")}
    if only is not None:
        directories = set(only)
    else:
        try:
            selected = json.loads((run_dir / 'run.json').read_text()).get('selected_scenarios', [])
            if isinstance(selected, list) and all(isinstance(n, str) for n in selected):
                directories.update(selected)
        except (OSError, ValueError, AttributeError):
            pass
    run = {}
    for name in sorted(directories):
        scenario = run_dir / name
        checks = {}
        checks_file = scenario / "checks.txt"
        if checks_file.exists():
            for line in checks_file.read_text().splitlines():
                if line[:4] in ("PASS", "FAIL"):
                    checks[line[6:].strip()] = line[:4]
        if not checks:
            checks["missing check results"] = "FAIL"
        metas = []
        for out in sorted(scenario.glob("out*.json")):  # out.json plus out-turnN.json for follow-up turns
            try:
                meta = json.loads(out.read_text())
                if not isinstance(meta, dict) or not isinstance(meta.get('result'), str):
                    raise ValueError('invalid adapter result')
                metas.append(meta)
                if meta.get('is_error'):
                    checks[f'execution error in {out.name}'] = 'FAIL'
            except (OSError, ValueError):
                checks[f'execution result unreadable or invalid: {out.name}'] = 'FAIL'
        if (scenario / '.timing-state.json').exists():
            checks['execution incomplete'] = 'FAIL'
        if (run_dir / 'run.json').exists() and not (scenario / 'out.json').exists():
            checks['execution result missing'] = 'FAIL'
        timing = None
        if (scenario / 'timing.json').exists():
            try:
                timing = read_timing(scenario / 'timing.json')
            except (OSError, ValueError, TypeError, KeyError) as error:
                print(f'WARNING: timing unavailable for {scenario.name}: {error}', file=sys.stderr)
        if timing is not None:
            if timing['status'] in ('agent_error', 'scenario_error'):
                checks['execution failed: ' + timing['status']] = 'FAIL'
            if any(call['exit_code'] != 0 for call in timing['adapter_calls']):
                checks['execution adapter call failed'] = 'FAIL'
        run[scenario.name] = {
            "timing": timing,
            "checks": checks,
            "cost": total_cost([m.get("total_cost_usd") for m in metas]),
            "turns": sum(m.get("num_turns") or 0 for m in metas),
            "minutes": sum(m.get("duration_ms") or 0 for m in metas) / 60000,
        }
    return run


arguments = sys.argv[1:]
only = None
if '--only' in arguments:
    index = arguments.index('--only')
    if index + 1 >= len(arguments) or not arguments[index + 1].split():
        sys.exit('ERROR: --only needs scenarios')
    only = arguments[index + 1].split()
    del arguments[index:index + 2]
    if '--only' in arguments:
        sys.exit('ERROR: use --only once')
if not arguments:
    sys.exit("usage: report.py <results-dir> [<results-dir> ...] [--only '<scenarios>']")
runs = [(Path(d).name, load(d, only)) for d in arguments]
names = sorted({name for _, run in runs for name in run})
labels = [label for label, _ in runs]

for name in names:
    print(f"\n{name}")
    check_labels = []
    for _, run in runs:
        for check in run.get(name, {}).get("checks", {}):
            if check not in check_labels:
                check_labels.append(check)
    width = max([len(c) for c in check_labels] + [30]) + 2
    print("  " + "check".ljust(width) + "".join(label.ljust(12) for label in labels))
    for check in check_labels:
        cells = [run.get(name, {}).get("checks", {}).get(check, "-") for _, run in runs]
        print("  " + check.ljust(width) + "".join(cell.ljust(12) for cell in cells))
    stats = [run.get(name) for _, run in runs]
    print("  " + "cost / turns / minutes".ljust(width) + "".join(
        (f"{cost_text(s['cost'])}/{s['turns']}/{s['minutes']:.0f}" if s else "-").ljust(24) for s in stats))
    timing_cells = []
    for s in stats:
        timing = s.get('timing') if s else None
        if timing is None:
            timing_cells.append('timing unavailable')
        else:
            adapter_ms = sum(call['wall_ms'] for call in timing['adapter_calls'])
            timing_cells.append(f"{timing['wall_ms'] / 1000:.1f}/{adapter_ms / 1000:.1f}")
    print('  ' + 'wall / adapter wall seconds'.ljust(width) + ''.join(cell.ljust(24) for cell in timing_cells))

print()
for label, run in runs:
    total = total_cost([s["cost"] for s in run.values()])
    passed = sum(v == "PASS" for s in run.values() for v in s["checks"].values())
    count = sum(len(s["checks"]) for s in run.values())
    print(f"{label}: {passed}/{count} checks passed, {cost_text(total)}")

sys.exit(0 if all(run and all(v == "PASS" for s in run.values()
                             for v in s["checks"].values()) for _, run in runs) else 1)
