#!/usr/bin/env python3
"""ph97 — every rung on every input: the *does the defect survive?* column, measured.

    python3 patterns-php/ph97-optarg-unwritten/controls/widened_domain.py

=============================================================================
WHAT IT ANSWERS
=============================================================================
1. ⭐⭐ **DOES THE UPSTREAM FIX WIDEN THE BENIGN DOMAIN, AND DOES STAGE 7h HAVE
   ANYTHING TO REFUSE?** `check.py` stage 7h refuses an R1h that CHANGES benign
   output. `f7326d627962` changes the answer on exactly one input — the one R1
   **crashes** on — so the two C rungs must agree on every other input, and this
   control measures that rather than asserting it.
2. ⭐ **WHICH RUNGS REPRODUCE THE DEFECT?** All six, on all seven inputs, with
   exit status and `si_addr` where a fault occurs.

⚠ It runs the binaries `harness-php/gate.py --tool build` already produced. If
they are missing it says so and stops, rather than silently measuring nothing.

⚠ `si_addr` comes from `.tasks-php/probes/segaddr.c`, the committed shim. The
`.so` is built under `.temp/` and is not committed: the generator is the
citation (`PROTOCOL_PHP.md` §F6).
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

ROW = os.path.basename(PDIR)
# ⚠ THE BUILD ROOT IS THE SHIM'S, NOT THE REPO'S. `harness-php/gate.py` runs
# the PAT harness under `.temp/php-root`, where `patterns-php/` is `patterns/`
# and the build root is rebound to `.temp/php-scratch/build/`. A control that
# looked in `.temp/build/` would find nothing and say so -- which is the quietest
# way to measure zero cells.
BUILD = os.path.join(REPO, ".temp", "php-scratch", "build", "ph97")
SCRATCH = os.path.join(REPO, ".temp", "php97", "wd")
PROBE = os.path.join(REPO, ".tasks-php", "probes", "segaddr.c")

CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]
INPUTS = ["small.bin", "large.bin", "adversarial-absent.bin",
          "adversarial-typefail.bin", "adversarial-toomany.bin",
          "adversarial-nullvalue.bin", "adversarial-nowin.bin"]


def build_shim():
    os.makedirs(SCRATCH, exist_ok=True)
    so = os.path.join(SCRATCH, "segaddr.so")
    subprocess.run(["gcc", "-shared", "-fPIC", "-O0", "-o", so, PROBE],
                   check=True)
    return so


def run(exe, inp, so):
    env = dict(os.environ)
    env["LD_PRELOAD"] = so
    r = subprocess.run([exe, inp], capture_output=True, text=True, env=env,
                       timeout=1800)
    out = r.stdout.strip()
    addr = None
    for line in r.stderr.splitlines():
        if line.startswith("[segaddr]"):
            addr = line.strip()
    return {"exit": r.returncode, "stdout": out, "segaddr": addr}


def main():
    so = build_shim()
    rec = {"cells": CELLS, "inputs": INPUTS, "table": {}, "problems": []}
    missing = []
    for c in CELLS:
        p = os.path.join(BUILD, f"{c}-O3-isolated")
        if not os.path.exists(p):
            missing.append(c)
    if missing:
        print(f"⛔ binaries missing for {missing} -- run "
              f"`harness-php/gate.py --tool build {ROW} --all` first")
        rec["problems"].append(f"binaries missing for {missing}")
        json.dump(rec, open(os.path.join(HERE, "widened_domain.json"), "w"),
                  indent=1)
        return 1

    hdr = f"{'input':28s}" + "".join(f"{c[:9]:>11s}" for c in CELLS)
    print(hdr)
    for inp in INPUTS:
        ip = os.path.join(PDIR, "inputs", inp)
        row = {}
        cells = []
        for c in CELLS:
            r = run(os.path.join(BUILD, f"{c}-O3-isolated"), ip, so)
            row[c] = r
            cells.append("SEGV" if r["exit"] == 139
                         else ("PANIC" if r["exit"] == 101
                               else r["stdout"][:10] or "?"))
        rec["table"][inp] = row
        print(f"{inp:28s}" + "".join(f"{x:>11s}" for x in cells))

    # -- 1. the two C rungs agree on every non-faulting input --------------
    dis = []
    for inp, row in rec["table"].items():
        for a, b in (("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h")):
            if row[a]["exit"] == 0 and row[a]["stdout"] != row[b]["stdout"]:
                dis.append((inp, a, b))
    rec["r1_r1h_disagreements"] = dis
    print(f"\n  R1 vs R1h: {len(dis)} disagreement(s) on inputs where R1 does "
          f"not fault -- stage 7h refuses an R1h that CHANGES benign output")
    if dis:
        rec["problems"].append(
            f"R1 and R1h disagree on {dis}, which is what stage 7h refuses")

    # -- 2. exactly one input faults, and only in the two R1 cells ---------
    faults = {(i, c) for i, row in rec["table"].items() for c in CELLS
              if row[c]["exit"] == 139}
    rec["faulting_cells"] = sorted(faults)
    want = {("adversarial-absent.bin", "c-gcc"),
            ("adversarial-absent.bin", "c-clang")}
    print(f"  faulting (input, cell) pairs: {sorted(faults)}")
    if faults != want:
        rec["problems"].append(
            f"the faulting set is {sorted(faults)}, want exactly {sorted(want)} "
            f"-- the defect must survive in the two R1 cells and nowhere else")

    # -- 3. the fault address is ZERO, matching the 5.0.0 CLI --------------
    a = rec["table"]["adversarial-absent.bin"]["c-gcc"]["segaddr"]
    rec["r1_segaddr"] = a
    print(f"  R1 fault: {a}")
    if not a or "si_addr=(nil)" not in a:
        rec["problems"].append(
            f"R1's fault address is {a!r}, not `si_addr=(nil)` -- the row's "
            f"harm claim is a dereference at offset ZERO, which is what the "
            f"PHP 5.0.0 CLI reports for the same trigger (NOTES.md §1)")

    # -- 4. the widening: R1h ANSWERS where R1 faults ----------------------
    h = rec["table"]["adversarial-absent.bin"]["c-gcc-h"]
    rec["r1h_answer_on_absent"] = h
    print(f"  R1h on the same input: exit {h['exit']}, {h['stdout']!r} "
          f"-- the fix WIDENS the benign domain")
    if h["exit"] != 0 or not h["stdout"]:
        rec["problems"].append("R1h does not answer on the input R1 faults on")

    rec.update(_pin.pin(["c/kernel.c", "c/kernel_hardened.c", "safe_naive.rs",
                         "safe_tuned.rs", "unsafe.rs", "verus.rs"],
                        "python3 controls/widened_domain.py",
                        "runs the built O3/isolated binaries; minutes"))
    with open(os.path.join(HERE, "widened_domain.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/widened_domain.json -- "
          f"{len(rec['problems'])} problem(s)")
    for p in rec["problems"]:
        print("  ⛔ " + p)
    return 1 if rec["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
