#!/usr/bin/env python3
"""Land TASK_PHP_012 M4 on patterns-php/CATALOGUE.md: 12 rows declare `verbatim`
whose defect site sits inside a PHP_FUNCTION / VM-handler / arg-parsing frame,
which PROTOCOL_PHP.md §A1 defines as `narrowed`.

BLOCKED while TASK_PHP_016 is running (PROTOCOL.md rule 11 -- it reads
CATALOGUE.md). Run this after that task reports.

  python3 .tasks-php/land_m4.py --check    # print what would change, touch nothing
  python3 .tasks-php/land_m4.py --apply

Evidence: .temp/php12/tier_check.py (re-run at .temp/mgr/batch/tier_recheck.log),
RECAP_PHP.md F36, .tasks-php/UPSTREAM_001.md §7.
The tier is a COST STATEMENT, never a filter (PLAN_PHP.md §4) -- no row moves,
gains or loses admission here.
"""
import re
import sys

ROWS = "ph05 ph11 ph12 ph21 ph22 ph24 ph35 ph50 ph55 ph59 ph76 ph80".split()
CAT = "patterns-php/CATALOGUE.md"


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        print(__doc__)
        return 2
    apply = sys.argv[1] == "--apply"

    src = open(CAT, encoding="utf-8").read()
    out, hits = [], {r: 0 for r in ROWS}

    for line in src.splitlines(keepends=True):
        row = None
        m = re.match(r"\| (ph\d+) \|", line)          # Part A table
        if m and m.group(1) in ROWS:
            row = m.group(1)
        m = re.match(r"\*\*(ph\d+) ·", line)          # Part B block header
        if m and m.group(1) in ROWS:
            row = m.group(1)
        if row and "verbatim" in line:
            line = line.replace("verbatim", "narrowed")
            hits[row] += 1
            print(f"  {row}: {line.strip()[:110]}")
        out.append(line)

    bad = [r for r, n in hits.items() if n != 2]
    print(f"\n{sum(hits.values())} edits over {len(ROWS)} rows "
          f"(expect 2 each: Part A + Part B)")
    if bad:
        print(f"⚠ REFUSED -- these rows did not have exactly 2: "
              f"{ {r: hits[r] for r in bad} }")
        return 1
    if apply:
        open(CAT, "w", encoding="utf-8").write("".join(out))
        print(f"applied to {CAT}")
    else:
        print("--check only, nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
