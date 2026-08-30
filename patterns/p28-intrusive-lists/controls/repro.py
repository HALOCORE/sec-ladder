#!/usr/bin/env python3
"""p28 CONTROLS: **R1 reads FREED HEAP and its checksum is still reproducible.**
That is the property `p27` and `p29` do not have, and it is the only thing the
row's reproducibility actually buys.

    python3 patterns/p28-intrusive-lists/controls/repro.py [--runs 20]

WHAT IS BEING CLAIMED, AND -- ⚠ **NARROWER THAN THE CATALOGUE ONCE SAID** -- WHAT
IS NOT
--------------------------------------------------------------------------------
`TASK_143_REPORT` 2.2 and `.memory/06-catalogue.md` said p28's reproducibility
makes it *"GATABLE against `model.py` on its adversarial inputs where `p27` and
`p29` are NOT"*. ⚠⚠ **That is FALSE, and `TASK_146` settled it with a run.**
`harness/check.py`'s `inputs_of` splits the matrix on the `adversarial` prefix,
stage 2 (`check_checksums`) is handed `good_models` ONLY, and stage 4
(`check_adversarial`) *records* per-rung behaviour -- its docstring says so in
terms and its only `rep.fail` is about a declared `expected_hang`. Across the
three built temporal rows' committed gate records, **54 adversarial rows carry
`diverges: true` inside a `PASS` verdict with 0 failures**. No pattern gates an
adversarial cell against `model.py`, and no amount of reproducibility could
change that.

✅ **What it DOES buy, and it is real and new:** the recorded adversarial row is
STABLE, so it can be quoted as an exact number. `p29`'s cannot -- its own
`controls/repro.json` publishes an invariant and no pinned count -- and `p29`'s
committed gate record shows the same input giving `13261590098807716864` at
`O3/isolated` and `13757854543850195968` at `O0/isolated`. **p28 is the first
temporal row whose adversarial evidence can carry a figure.**

⚠ **AND THE FIGURE HAS A DOMAIN, which this script measures rather than
assumes.** It runs every (compiler x opt) cell, so the JSON says whether the
value is one number or four. What makes it stable at all is the LAYOUT
(`c/kernel.h`): the four links come first, so glibc's tcache writes its `next`
and `key` words over `lp` and `ln` and leaves `key`, `val`, `hn` and `hp`
untouched -- and those are the only fields R1's stale walk reads. It is a fact
about **this allocator and this struct order**, not about use-after-free in
general, and `controls/arm_aslr.c` reads the word that does NOT survive to show
the difference inside one run.

⚠ **THE NEGATIVE CONTROL IS WHAT MAKES ANY OF IT EVIDENCE.** *"One distinct
value in twenty runs"* is vacuous if this box cannot produce more than one.
`arm_aslr.c` goes through the SAME counter and must report more than one;
`main()` exits non-zero if it does not. `/proc/sys/kernel/randomize_va_space` is
recorded beside it.

⚠ **The `adv-uaf-write` row is a stable CRASH, not a stable value**, and only
the first kind can carry a checksum. It is recorded as `exit_codes` and its
`value` is `null`.
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

BIN = os.path.join(REPO, ".temp", "build", "p28-repro")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")

INPUTS = ["adversarial-uaf-read.bin", "adversarial-uaf-head.bin",
          "adversarial-uaf-write.bin", "adversarial-many.bin",
          "degenerate.bin", "small.bin"]
# Every (compiler x opt) cell, because the QUESTION is whether the pinnable
# figure is one number or four.
CELLS = [("c-gcc", "O0"), ("c-gcc", "O3"), ("c-clang", "O0"), ("c-clang", "O3")]


def one(binpath, path, runs):
    vals, codes = set(), set()
    argv = [binpath] if path is None else [binpath, path]
    for _ in range(runs):
        r = subprocess.run(argv, capture_output=True, text=True, timeout=600)
        codes.add(r.returncode)
        vals.add(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "")
    val = sorted(vals)[0] if len(vals) == 1 else None
    return len(vals), sorted(codes), (val if val else None)


def negative_control(runs):
    exe = os.path.join(BIN, "arm_aslr")
    os.makedirs(BIN, exist_ok=True)
    b = subprocess.run([GCC, "-std=c99", "-Wall", "-Wextra", "-O1",
                        "-Wno-use-after-free", "-o", exe,
                        os.path.join(HERE, "arm_aslr.c")],
                       capture_output=True, text=True, timeout=300)
    if b.returncode != 0:
        raise SystemExit("repro.py: negative control failed to build:\n"
                         + b.stdout + b.stderr)
    n, codes, _v = one(exe, None, runs)
    try:
        aslr = open("/proc/sys/kernel/randomize_va_space").read().strip()
    except OSError:
        aslr = "unreadable"
    return {"arm": "controls/arm_aslr.c", "distinct": n, "runs": runs,
            "exit_codes": codes, "randomize_va_space": aslr,
            "fired": n > 1,
            "what": "reads user offset 0 of a freed tcache chunk -- the word "
                    "glibc overwrites with a safe-linked next derived from the "
                    "heap base, and the word p28's LAYOUT deliberately keeps R1 "
                    "away from. It MUST give more than one distinct value in N "
                    "runs; if it gives one, the counter is blind and every "
                    "figure above is vacuous."}


def derived_from():
    out = {}
    for rel in ("patterns/p28-intrusive-lists/c/kernel.c",
                "patterns/p28-intrusive-lists/c/kernel_hardened.c",
                "patterns/p28-intrusive-lists/c/main.c",
                "patterns/p28-intrusive-lists/inputs/gen.py",
                "patterns/p28-intrusive-lists/controls/repro.py",
                "patterns/p28-intrusive-lists/controls/arm_aslr.c",
                "common/driver.c"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=20)
    a = ap.parse_args()
    bins = {}
    for cell, opt in CELLS:
        ok, out, log = B.build_cell(PDIR, cell, opt, "isolated", quiet=True)
        if not ok:
            raise SystemExit(f"repro.py: build failed for {cell} {opt}:\n{log}")
        bins[(cell, opt)] = out
    rows, unstable = [], []
    for name in INPUTS:
        path = os.path.join(PDIR, "inputs", name)
        if not os.path.exists(path):
            continue
        row = {"input": name, "cells": {}}
        for cell, opt in CELLS:
            n, codes, val = one(bins[(cell, opt)], path, a.runs)
            row["cells"][f"{cell}/{opt}"] = {"distinct": n, "exit_codes": codes,
                                             "value": val}
            if n != 1:
                unstable.append(f"{name}/{cell}/{opt}")
        # ⚠ Compare the (value, exit codes) PAIR, not the value alone: the
        # `adv-uaf-write` row's value is `null` in every cell because R1 crashes
        # there, and comparing `null` to `null` would report agreement about a
        # number that does not exist. The pair says what actually agrees.
        vals = {(c["value"], tuple(c["exit_codes"]))
                for c in row["cells"].values()}
        row["same_across_cells"] = len(vals) == 1
        row["distinct_behaviours_across_cells"] = len(vals)
        row["is_a_value"] = all(c["value"] is not None
                                for c in row["cells"].values())
        rows.append(row)
        print(f"  {name:28s} "
              + "  ".join(f"{c}/{o}={row['cells'][f'{c}/{o}']['distinct']}"
                          for c, o in CELLS)
              + ("   ONE behaviour across all four cells"
                 + ("" if row["is_a_value"] else " (a stable CRASH, not a value)")
                 if row["same_across_cells"]
                 else f"   {len(vals)} distinct behaviours across cells"))
    neg = negative_control(a.runs)
    print(f"\n  NEGATIVE CONTROL  arm_aslr.c   {neg['distinct']:>2d}/{a.runs} "
          f"distinct   randomize_va_space={neg['randomize_va_space']}   "
          + ("FIRED -- the counter can report >1"
             if neg["fired"] else "*** DEAD -- every count above is vacuous"))
    doc = {"pin": {"regenerate":
                   "python3 patterns/p28-intrusive-lists/controls/repro.py"},
           "derived_from_sha256": derived_from(),
           "runs": a.runs,
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "rows": rows,
           "negative_control": neg,
           "unstable_cells": unstable,
           "invariant":
               "EVERY cell is stable at 1 distinct value in N runs, on every "
               "input including the four adversarial ones -- although R1 READS "
               "FREED HEAP on all four. The layout is why (c/kernel.h): the "
               "links come first, so glibc's tcache clobbers `lp` and `ln` and "
               "leaves the `key`/`val`/`hn`/`hp` R1's walk reads intact. "
               "⚠ WHAT THIS BUYS IS A PINNABLE FIGURE AND NOT A GATE: "
               "harness/check.py records adversarial behaviour and never "
               "requires it to agree with model.py, in any pattern (TASK_146 "
               "deliverable 0, measured). ⚠⚠ AND IT IS ONLY EVIDENCE BESIDE THE "
               "NEGATIVE CONTROL: arm_aslr.c goes through the SAME counter and "
               "must report MORE than one distinct value. `adv-uaf-write` is a "
               "stable SIGSEGV rather than a stable value, so its `value` is "
               "null and its stability lives in `exit_codes`."}
    out = os.path.join(HERE, "repro.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    if unstable:
        print(f"  *** UNSTABLE CELLS: {unstable} -- p28's whole reproducibility "
              f"claim is that there are none", file=sys.stderr)
    if not neg["fired"]:
        print(f"  *** THE NEGATIVE CONTROL IS DEAD: arm_aslr.c gave "
              f"{neg['distinct']} distinct value(s) in {a.runs} runs at "
              f"randomize_va_space={neg['randomize_va_space']}. A twenty-run "
              f"reproducibility test that cannot report >1 proves nothing, so "
              f"every figure above is vacuous.", file=sys.stderr)
    return 1 if (unstable or not neg["fired"]) else 0


if __name__ == "__main__":
    sys.exit(main())
