"""Check that a reply ends with one choice block led by a `0 — Recommended` line.

Usage: choices.py [--canonical] <reply-file>

Exits 0 when the last `0 ... Recommended` line starts a block that holds only option
lines (and indented continuation lines) up to the end of the reply. With --canonical,
the 0 line must also use the router's exact form: `0 — Recommended: <action> — <reason>`.
"""

import re
import sys

args = sys.argv[1:]
canonical = "--canonical" in args
path = next(a for a in args if a != "--canonical")
lines = [line.rstrip() for line in open(path, encoding="utf-8")]

marker = r"(?:[—–-]+|[.):])"
zero = re.compile(rf"^[\s>*-]*\**0\**\s*{marker}\s*\**Recommended", re.I)
option = re.compile(rf"^[\s>*-]*\**\d+\**\s*{marker}\s*\S")

starts = [i for i, line in enumerate(lines) if zero.match(line)]
if not starts:
    sys.exit("no `0 — Recommended` line")
start = starts[-1]
for line in lines[start:]:
    if not line.strip() or line.strip().startswith("```") or line.startswith("  "):
        continue
    if not option.match(line):
        sys.exit(f"content inside or after the final choice block: {line!r}")
if canonical and not re.match(r"^0 — Recommended: .+ — .+", lines[start].strip()):
    sys.exit(f"0 line is not in the canonical form: {lines[start]!r}")
