#!/usr/bin/env python3
"""p29 CONTROLS: is R1's checksum reproducible? `p25`'s kill, asked of p29.

`RECAP` finding 48 refuses `p25` partly on *"R1 has no reproducible checksum ...
and a nondeterministic R1 cannot be gated against `model.py` at all"*. p29's R1
reads freed memory, so the question had to be asked -- and the answer is
**input-class-specific**, which is why the kill does not transfer.

    python3 patterns/p29-bst-delete/controls/repro.py [--runs 20]

⚠⚠ **NO NUMBER THIS SCRIPT PRINTS IS A FACT.** The distinct-value count of a
nondeterministic checksum is itself nondeterministic -- `p23`'s lesson, and
`TASK_136` saw `18` then `20` for one input on one box. **What is a fact is the
INVARIANT**: the use-after-FREE inputs are non-reproducible, the
use-after-RECYCLE input is stable at 1, benign is stable at 1, and R1h is stable
everywhere. ../NOTES.md publishes the invariant and a dated history table, never
a pinned count.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "harness"))
import build as B  # noqa: E402

INPUTS = ["adversarial-uaf.bin", "adversarial-succ.bin",
          "adversarial-recycle.bin", "adversarial-many.bin",
          "degenerate.bin", "small.bin"]
CELLS = [("c-gcc", "R1"), ("c-gcc-h", "R1h")]


def one(binpath, path, runs):
    vals = set()
    codes = set()
    for _ in range(runs):
        r = subprocess.run([binpath, path], capture_output=True, text=True,
                           timeout=300)
        codes.add(r.returncode)
        vals.add(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "")
    return len(vals), sorted(codes)


def derived_from():
    out = {}
    for rel in ("patterns/p29-bst-delete/c/kernel.c",
                "patterns/p29-bst-delete/c/kernel_hardened.c",
                "patterns/p29-bst-delete/c/main.c",
                "patterns/p29-bst-delete/inputs/gen.py",
                "patterns/p29-bst-delete/controls/repro.py",
                "common/driver.c"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=20)
    a = ap.parse_args()
    # The gate's checksum cells are PLAIN builds -- ASan appears only at stage 7
    # -- so this measures the plain `-O3 isolated` cells, which is what the
    # published tables quote.
    bins = {}
    for cell, _n in CELLS:
        ok, out, log = B.build_cell(PDIR, cell, "O3", "isolated", quiet=True)
        if not ok:
            raise SystemExit(f"repro.py: build failed for {cell}:\n{log}")
        bins[cell] = out
    rows = []
    for name in INPUTS:
        path = os.path.join(PDIR, "inputs", name)
        if not os.path.exists(path):
            continue
        row = {"input": name}
        for cell, label in CELLS:
            n, codes = one(bins[cell], path, a.runs)
            row[label] = {"distinct": n, "exit_codes": codes}
        rows.append(row)
        print(f"  {name:26s} "
              + "  ".join(f"{lab}={row[lab]['distinct']:>2d}/{a.runs}"
                          for _c, lab in CELLS))
    doc = {"pin": {"regenerate":
                   "python3 patterns/p29-bst-delete/controls/repro.py"},
           "derived_from_sha256": derived_from(),
           "runs": a.runs,
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "rows": rows,
           "invariant": "The use-after-FREE inputs are NOT reproducible; the "
                        "use-after-RECYCLE input IS, at 1 of N; benign is 1; "
                        "R1h is 1 everywhere. The COUNTS above are one draw and "
                        "are not facts -- see the module docstring."}
    out = os.path.join(HERE, "repro.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
