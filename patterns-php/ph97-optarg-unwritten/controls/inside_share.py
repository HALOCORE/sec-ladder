#!/usr/bin/env python3
"""ph97 — `inside_share` for EVERY cell, as a matrix, before the statistic is chosen.

    python3 patterns-php/ph97-optarg-unwritten/controls/inside_share.py

=============================================================================
WHY A MATRIX AND NOT A NUMBER
=============================================================================
⭐⭐⭐ **`inside_share` IS PER-CELL, NOT PER-ROW** (`.memory-php/03-numbers.md`,
from `TASK_PHP_045`): `ph52` measures **22.24 %** on its C rungs and **≈98.6 %**
on its Rust ones, and publishes its R1-vs-R1h column in W1 while a respelling
search of its Rust rungs lands where A1 resolves. A row that quoted one number
would have been wrong about half its own cells.

**It is what decides which family can resolve a difference**, and it has to be
computed BEFORE the statistic is chosen rather than after the search disagrees.

⛔ **AND A HIGH SHARE IS NOT A CERTIFICATE** (F109): `ph55`'s C cells sit at
74–83 % and A1 still read `0.000 %` on that row's own defect site, because the
defect lived in an uninlinable callee. What matters is whether **the
DIFFERENCE** lands inside the symbol, not the level.

`inside_share = 100 × (callgrind exclusive Ir of the `kernel` symbol)
                    / (callgrind `summary:` total Ir for the same run)`

— defined here rather than inherited, because a percentage owes its denominator
a name (`.memory-php/03-numbers.md`, F88).

⚠ It measures the binaries `harness-php/gate.py --tool build` already produced,
in the shim's build root, and builds nothing itself — so the numbers are about
the cells the measurement record describes and not about a scratch copy.

⚠ `whole` cells are NOT in the matrix: at `O3` the kernel is inlined into `main`
and there is no `kernel` symbol to be exclusive of, so the ratio is undefined
rather than 100 %.
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

BUILD = os.path.join(REPO, ".temp", "php-scratch", "build", "ph97")
SCRATCH = os.path.join(REPO, ".temp", "php97", "ishare")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANNOTATE = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")

CELLS = ["c-gcc", "c-clang", "c-gcc-h", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]
INPUTS = ["small.bin", "large.bin"]
#: calls the driver makes -- from the payload header, not guessed.
CALLS = {"small.bin": 20000, "large.bin": 3000}

_CG_ROW = re.compile(r"^\s*([\d,]+)\s+(.*)$")


def cg(exe, inp, tag):
    os.makedirs(SCRATCH, exist_ok=True)
    out = os.path.join(SCRATCH, f"cg.{tag}.out")
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={out}", exe, inp],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        return {"error": f"callgrind exit {r.returncode}"}
    total = None
    for line in open(out):
        if line.startswith("summary:") or line.startswith("totals:"):
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
    return {"kernel_exclusive_ir": kern or None, "whole_program_ir": total,
            "inside_share_pct": (100.0 * kern / total) if (kern and total) else None}


def main():
    rec = {"cell_spec": "O3 / isolated",
           "definition": "100 * callgrind exclusive Ir of the `kernel` symbol / "
                         "callgrind `summary:` total Ir for the same run",
           "matrix": {}, "problems": []}
    missing = [c for c in CELLS
               if not os.path.exists(os.path.join(BUILD, f"{c}-O3-isolated"))]
    if missing:
        rec["problems"].append(
            f"binaries missing for {missing} -- run "
            f"`harness-php/gate.py --tool build ph97-optarg-unwritten --all`")
        json.dump(rec, open(os.path.join(HERE, "inside_share.json"), "w"), indent=1)
        print(f"⛔ {rec['problems'][0]}")
        return 1

    print(f"{'cell':12s}" + "".join(f"{i:>26s}" for i in INPUTS))
    print(f"{'':12s}" + "".join(f"{'A1/call   share':>26s}" for _ in INPUTS))
    for c in CELLS:
        rec["matrix"][c] = {}
        line = f"{c:12s}"
        for inp in INPUTS:
            r = cg(os.path.join(BUILD, f"{c}-O3-isolated"),
                   os.path.join(PDIR, "inputs", inp), f"{c}-{inp}")
            r["ir_per_call"] = (r["kernel_exclusive_ir"] / CALLS[inp]
                                if r.get("kernel_exclusive_ir") else None)
            rec["matrix"][c][inp] = r
            line += f"{r['ir_per_call']:>17.2f}{r['inside_share_pct']:>8.2f}%"
            if r.get("inside_share_pct") is None:
                rec["problems"].append(
                    f"{c}/{inp}: no `kernel` symbol or no callgrind total, so "
                    f"`inside_share` is undefined and the statistic for this "
                    f"cell cannot be chosen from it")
        print(line)

    # ⚠ BOTH C COLUMNS ARE PRESENT BY CONSTRUCTION -- F108. A matrix that named
    # only one would be the exact defect this row's NOTES quotes against itself.
    have = {c for c in rec["matrix"]}
    for want in ("c-gcc", "c-clang"):
        if want not in have:
            rec["problems"].append(
                f"{want} is absent from the matrix; a cross-language reading "
                f"needs BOTH C columns (F108)")

    print("\n  ⛔ A HIGH SHARE IS NOT A CERTIFICATE (F109). What matters is "
          "whether the DIFFERENCE lands inside the symbol, not the level.")
    print("  ⚠ `whole` cells are deliberately absent: at O3 the kernel is "
          "inlined into `main` and the ratio is undefined, not 100 %.")

    rec.update(_pin.pin(["c/kernel.c", "c/kernel_hardened.c", "safe_naive.rs",
                         "safe_tuned.rs", "unsafe.rs", "verus.rs",
                         "inputs/small.bin", "inputs/large.bin"],
                        "python3 controls/inside_share.py",
                        "16 callgrind runs over the already-built O3/isolated "
                        "cells; minutes"))
    with open(os.path.join(HERE, "inside_share.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/inside_share.json -- "
          f"{len(rec['problems'])} problem(s)")
    for p in rec["problems"]:
        print("  ⛔ " + p)
    return 1 if rec["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
