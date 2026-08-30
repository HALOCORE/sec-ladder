#!/usr/bin/env python3
"""p32 CONTROLS: is R1's checksum reproducible? **On p32 it is, on every input,
and that is a property neither built temporal row has.**

    python3 patterns/p32-free-list-pool/controls/repro.py [--runs 20]

WHY THE QUESTION IS ASKED
-------------------------
`p27` and `p29` both read FREED HEAP on their adversarial inputs, so what the
stale read returns depends on the allocator and on ASLR: `p29` ships with **20
distinct values in 20 runs** on three of its inputs (`../../p29-bst-delete/
controls/repro.json`), and `RECAP` finding 48 once used that against `p25`.

p32's storage is a local array. There is no heap address anywhere in the answer
and no allocator call anywhere in the kernel, so **the buggy rung's checksum is a
pure function of the input bytes** -- and `harness/check.py` stage 2 could gate
R1 against `model.py` on the adversarial rows if the pattern wanted it to, which
`p27` and `p29` cannot. It does not: the adversarial rows are excluded because
R1 DISAGREES, not because it is unstable, and `.memory/02-bench-rules.md` says
those rows are recorded rather than required.

⚠⚠ **The `malloc` STORAGE ARM IS THE CONTRAST AND IT IS NOT
REPRODUCIBLE.** `controls/storage_arms.py`'s `adv-stale-read` cell reads freed
heap and its plain-build checksum moves between compilers. So this pattern
contains both behaviours, and which one you get is decided by the storage --
which is the same two-cell experiment the storage arms measure, seen on a
different axis.

⚠ **NO COUNT THIS SCRIPT PRINTS IS A PINNED FACT.** `p23`'s lesson: the
distinct-value count of a nondeterministic checksum is itself
nondeterministic. What is a fact here is the INVARIANT -- every arena cell is
stable at 1 -- and `../NOTES.md` publishes the invariant, never a pinned count.
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

INPUTS = ["adversarial-stale-read.bin", "adversarial-recycle.bin",
          "adversarial-doublefree.bin", "adversarial-alias.bin",
          "adversarial-many.bin", "degenerate.bin", "small.bin"]
CELLS = [("c-gcc", "R1"), ("c-gcc-h", "R1h")]


def one(binpath, path, runs):
    vals, codes = set(), set()
    for _ in range(runs):
        r = subprocess.run([binpath, path], capture_output=True, text=True,
                           timeout=600)
        codes.add(r.returncode)
        vals.add(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "")
    return len(vals), sorted(codes), sorted(vals)[0] if len(vals) == 1 else None


def derived_from():
    out = {}
    for rel in ("patterns/p32-free-list-pool/c/kernel.c",
                "patterns/p32-free-list-pool/c/kernel_hardened.c",
                "patterns/p32-free-list-pool/c/main.c",
                "patterns/p32-free-list-pool/inputs/gen.py",
                "patterns/p32-free-list-pool/controls/repro.py",
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
    rows, unstable = [], []
    for name in INPUTS:
        path = os.path.join(PDIR, "inputs", name)
        if not os.path.exists(path):
            continue
        row = {"input": name}
        for cell, label in CELLS:
            n, codes, val = one(bins[cell], path, a.runs)
            row[label] = {"distinct": n, "exit_codes": codes, "value": val}
            if n != 1:
                unstable.append(f"{name}/{label}")
        row["R1_diverges"] = row["R1"]["value"] != row["R1h"]["value"]
        rows.append(row)
        print(f"  {name:28s} "
              + "  ".join(f"{lab}={row[lab]['distinct']:>2d}/{a.runs}"
                          for _c, lab in CELLS)
              + ("   R1 DIVERGES" if row["R1_diverges"] else "   agree"))
    doc = {"pin": {"regenerate":
                   "python3 patterns/p32-free-list-pool/controls/repro.py"},
           "derived_from_sha256": derived_from(),
           "runs": a.runs,
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "rows": rows,
           "unstable_cells": unstable,
           "invariant":
               "EVERY cell is stable at 1 distinct value in N runs, R1 and R1h "
               "alike, on every input including the five adversarial ones -- "
               "because p32's storage is a local array and no heap address "
               "reaches the answer. R1 nevertheless DIVERGES from R1h on all "
               "five adversarial inputs. ⚠ The COUNTS above are one draw "
               "and are not pinned anywhere; what ../NOTES.md publishes is this "
               "invariant. The CONTRAST is controls/storage_arms.py's `malloc` "
               "arm, whose adv-stale-read cell reads freed heap and is NOT "
               "stable."}
    out = os.path.join(HERE, "repro.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    if unstable:
        print(f"  *** UNSTABLE CELLS: {unstable} -- p32's whole reproducibility "
              f"claim is that there are none", file=sys.stderr)
    return 1 if unstable else 0


if __name__ == "__main__":
    sys.exit(main())
