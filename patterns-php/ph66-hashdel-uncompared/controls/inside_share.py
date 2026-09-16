#!/usr/bin/env python3
"""ph66 -- `inside_share` PER CELL, BEFORE the statistic is chosen.

    python3 patterns-php/ph66-hashdel-uncompared/controls/inside_share.py

⛔⛔⛔ **WHICH `inside_share`.** Two quantities wear that name in this programme
(`RECAP_PHP.md` F129) and this file computes **the `W` one**:

    inside_share_W = 100 x (kernel exclusive Ir) / (callgrind's own summary total)

and NOT `F74`'s `(kernel_exclusive_ir / n_iters) / marginal_ir_per_call`, which
is arithmetic over two committed records and needs no callgrind run. Both are
printed here -- F74's is computed from `results-php/<row>.json` -- because the
gap between them is a MEASUREMENT and never a constant (8.9 pp on `ph29`, 0.01 pp
on `ph45`).

⛔⛔ **A HIGH SHARE IS NOT A CERTIFICATE AND F74's TWO-CONDITION BAR IS NOT A
GATE.** `TASK_PHP_059` settled that, and `.memory-php/02-ladder.md` carries the
counterexample: on `ph55`'s `c-gcc` vs `c-gcc-h` pair the bar ADMITS a
comparison whose A1 reads exactly `+0.0000 %` against a 66.14 Ir/call
whole-program difference. ▶ **Use the share to EXPLAIN a disagreement between
the two columns. Never to withhold a column.**

▶ Eight cells x two inputs x **TWO OPTIMISATION LEVELS**, both C columns.

⛔⛔ **THE SECOND LEVEL IS NOT DECORATION AND ph96 IS WHY.** That row published
its 16-cell matrix at `O3/isolated` ONLY, and `TASK_PHP_061` refuted its headline
at `O0`, where `A1` reads `+0.0000` while the whole-program figure moves
`-2.24 .. -19.58 Ir/call`. ⭐ ON THIS ROW THE O0 HALF IS WORSE THAN ph96's AND
IT IS STRUCTURAL: at `O0` the C rungs do not inline `zend_hash_del_key_or_index`
into `kernel`, so the row's ENTIRE DEFECT lives in a callee and `A1` --
kernel-EXCLUSIVE Ir -- cannot see it at all. `c-gcc` and `c-gcc-h` report the
same 33,968,756 and the same `md5_fn`. ▶ That is the `results/tables/*.md`
caveat (*"whatever a rung calls out to lands in no column of this table"*) firing
LIVE, and it is why this file sweeps both levels rather than one.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

ROW = os.path.basename(PDIR)
BUILD = os.path.join(REPO, ".temp", "php-scratch", "build", ROW.split("-")[0])
RESULT = os.path.join(REPO, "results-php", ROW + ".json")
GATE = os.path.join(REPO, "results-php", "gate", ROW + ".json")
SCRATCH = os.path.join(REPO, ".temp", "php66", "share")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANNOTATE = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")

CELLS = ["c-gcc", "c-clang", "c-gcc-h", "c-clang-h", "safe_naive",
         "safe_tuned", "unsafe", "verus"]
#: BOTH levels. See the docstring: on this row the O0 half is the one that
#: shows `A1` measuring a different thing from the whole-program figure.
OPTS = ["O3", "O0"]
CALLS = {"small.bin": 20000, "large.bin": 2500}
_CG_ROW = re.compile(r"^\s*([\d,]+)\s+(.*)$")


def _cg(exe, inp, tag):
    out = os.path.join(SCRATCH, f"cg.{tag}.out")
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={out}", exe, inp],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        return None
    total = None
    for line in open(out):
        if line.startswith(("summary:", "totals:")):
            total = int(line.split(":", 1)[1].strip().split()[0])
    ann = subprocess.run([CG_ANNOTATE, "--threshold=100", out],
                         capture_output=True, text=True).stdout
    kern = 0
    for line in ann.splitlines():
        m = _CG_ROW.match(line)
        if not m or ":" not in m.group(2):
            continue
        func = m.group(2).split(":", 1)[1].split(" [")[0].strip()
        if re.search(r"(?:^|::)kernel(?:$|[^A-Za-z0-9_])", func):
            kern += int(m.group(1).replace(",", ""))
    return {"A1": kern or None, "W": total,
            "inside_share_W_pct": (100.0 * kern / total)
                                  if (kern and total) else None}


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    problems = []
    rec = {"problems": problems, "definition_used": "W",
           "definition_note": ("inside_share_W = kernel exclusive Ir / "
                               "callgrind summary total. NOT F74's "
                               "(A1/n_iters)/marginal_ir_per_call -- F129."),
           "build_root": BUILD, "cells": {}}
    if not os.path.isdir(BUILD):
        problems.append(f"no build root at {BUILD}; run "
                        f"`harness-php/gate.py --tool build {ROW} --all` first")
        return _finish(rec, problems)

    # F74's share, from the two COMMITTED records -- no callgrind needed.
    # A1 lives in the measurement record and `marginal_ir_per_call` in the gate
    # record, which is why F74's form is arithmetic over two files rather than
    # one.
    f74 = {}
    if os.path.exists(RESULT) and os.path.exists(GATE):
        d = json.load(open(RESULT))
        marg = json.load(open(GATE)).get("marginal_ir_per_call") or {}
        for c in d.get("cells", []):
            if c.get("mode") != "isolated":
                continue
            pass
        for c in d.get("cells", []):
            if c.get("mode") != "isolated" or c.get("opt") not in OPTS:
                continue
            for inp, n in CALLS.items():
                a = (c.get("ir") or {}).get(inp, {}).get("kernel_exclusive_ir")
                b = marg.get(f"{c['cell']}/{c['opt']}/isolated/{inp}")
                if a and b:
                    f74[f"{c['cell']}/{c['opt']}/{inp}"] = (a / n) / b
    rec["inside_share_F74"] = f74

    print(f"{'cell':13s}{'opt':5s}{'input':12s}{'A1':>12s}{'A1/call':>11s}"
          f"{'W':>12s}{'share_W':>10s}{'share_F74':>11s}")
    for opt in OPTS:
        for cell in CELLS:
            rec["cells"].setdefault(f"{cell}/{opt}", {})
            for inp, n in CALLS.items():
                exe = os.path.join(BUILD, f"{cell}-{opt}-isolated")
                if not os.path.exists(exe):
                    problems.append(f"missing binary {exe}")
                    continue
                c = _cg(exe, os.path.join(PDIR, "inputs", inp),
                        f"{cell}-{opt}-{inp}")
                if c is None:
                    problems.append(f"callgrind failed on {cell}/{opt}/{inp}")
                    continue
                c["ir_per_call"] = c["A1"] / n if c["A1"] else None
                c["inside_share_F74"] = f74.get(f"{cell}/{opt}/{inp}")
                rec["cells"][f"{cell}/{opt}"][inp] = c
                f74s = c["inside_share_F74"]
                f74txt = f"{f74s * 100:>10.2f}%" if f74s else f"{'n/a':>11s}"
                print(f"{cell:13s}{opt:5s}{inp:12s}{c['A1']:>12d}"
                      f"{c['ir_per_call']:>11.3f}"
                      f"{c['W']:>12d}{c['inside_share_W_pct']:>9.2f}%" + f74txt)

    vals = [v["inside_share_W_pct"] for c in rec["cells"].values()
            for v in c.values() if v.get("inside_share_W_pct")]
    rec["W_range_pct"] = [min(vals), max(vals)] if vals else None
    print(f"\n{len(vals)} independent per-cell ratios, NOT a comparison. W range: "
          f"{min(vals):.2f}% .. {max(vals):.2f}%")
    print("⛔ A HIGH SHARE IS NOT A CERTIFICATE. What decides whether A1 "
          "resolves a difference is whether THE DIFFERENCE lands inside the "
          "symbol, not how much of the cell does.")
    if len(vals) != 32:
        problems.append(f"{len(vals)} of 32 (cell x opt x input) triples "
                        f"produced a share; a matrix with a hole is not a matrix")

    rec.update(_pin.pin(["inputs/small.bin", "inputs/large.bin"],
                        "python3 controls/inside_share.py",
                        "32 callgrind runs off the gate's own build root; "
                        "minutes"))
    return _finish(rec, problems)


def _finish(rec, problems):
    with open(os.path.join(HERE, "inside_share.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/inside_share.json -- {len(problems)} problem(s)")
    for p in problems:
        print("  ⛔ " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
