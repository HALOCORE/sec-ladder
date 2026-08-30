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

⚠⚠ **THE NEGATIVE CONTROL, ADDED AT TASK_147, AND WITHOUT IT NOTHING ABOVE IS
EVIDENCE.** *"Every cell is 1 distinct value in 20 runs"* is **vacuous if this
box cannot produce more than one** -- ASLR off, a runner that collapses the
outputs, twenty runs that are not twenty processes. Until `TASK_147` this script
never checked (`TASK_145_REPORT` §6a), and the manager had demanded exactly this
arm for `p28` in `.memory/06-catalogue.md`: *"against a NEGATIVE CONTROL that
gives 20 distinct values, so the test is not blind and ASLR is on"*.

`arm_aslr.c` is that arm, run through **the same twenty-run counter** as every
cell above. It frees a chunk and reads user offset 0 -- the word glibc's tcache
overwrites with a safe-linked `next` derived from the heap base -- so it MUST
give more than one value, and `main()` below exits non-zero if it gives one.
⚠ It is deliberately p32's own `c-malloc` failure mode rather than an unrelated
source of entropy, so the same run also exhibits the contrast this pattern
publishes: reading freed heap is not reproducible, reading a live pool is.
`/proc/sys/kernel/randomize_va_space` is recorded beside it.
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

# ⚠ NOT `.temp/build/p32-arms`, which is `storage_arms.py`'s and `forgeable.py`'s.
# `storage_arms.py` enumerates the binaries in its own build directory and
# demands that every one of them fire its positive control, so dropping an
# unrelated executable in there makes THAT control report a dead build. Own
# directory, own arm. (`storage_arms.py::build` was also changed at TASK_147 to
# return the names it made rather than to list the directory, so the trap is
# closed from both ends.)
BIN = os.path.join(REPO, ".temp", "build", "p32-repro")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")

INPUTS = ["adversarial-stale-read.bin", "adversarial-recycle.bin",
          "adversarial-doublefree.bin", "adversarial-alias.bin",
          "adversarial-many.bin", "degenerate.bin", "small.bin"]
CELLS = [("c-gcc", "R1"), ("c-gcc-h", "R1h")]


def one(binpath, path, runs):
    vals, codes = set(), set()
    argv = [binpath] if path is None else [binpath, path]
    for _ in range(runs):
        r = subprocess.run(argv, capture_output=True, text=True, timeout=600)
        codes.add(r.returncode)
        vals.add(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "")
    return len(vals), sorted(codes), sorted(vals)[0] if len(vals) == 1 else None


def negative_control(runs):
    """Build and run `arm_aslr.c` through `one()` -- the SAME counter every cell
    above uses -- and require MORE than one distinct value.

    ⚠ `-Wno-use-after-free`: the read of the freed chunk is the mechanism, not
    an accident, and gcc is right to warn. The warning is silenced here and
    nowhere else in this pattern, and `arm_aslr.c`'s header says why."""
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
            "what": "reads user offset 0 of a freed tcache chunk, which holds a "
                    "safe-linked next pointer derived from the heap base. It "
                    "MUST give more than one distinct value in N runs; if it "
                    "gives one, the 20-run instrument above is blind and p32's "
                    "1-of-20 claim proves nothing."}


def derived_from():
    out = {}
    for rel in ("patterns/p32-free-list-pool/c/kernel.c",
                "patterns/p32-free-list-pool/c/kernel_hardened.c",
                "patterns/p32-free-list-pool/c/main.c",
                "patterns/p32-free-list-pool/inputs/gen.py",
                "patterns/p32-free-list-pool/controls/repro.py",
                "patterns/p32-free-list-pool/controls/arm_aslr.c",
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
    neg = negative_control(a.runs)
    print(f"\n  NEGATIVE CONTROL  arm_aslr.c   {neg['distinct']:>2d}/{a.runs} "
          f"distinct   randomize_va_space={neg['randomize_va_space']}   "
          + ("FIRED -- the 20-run instrument can report >1"
             if neg["fired"] else "*** DEAD -- every count above is vacuous"))
    doc = {"pin": {"regenerate":
                   "python3 patterns/p32-free-list-pool/controls/repro.py"},
           "derived_from_sha256": derived_from(),
           "runs": a.runs,
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "rows": rows,
           "negative_control": neg,
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
               "stable. ⚠⚠ AND THE INVARIANT IS ONLY EVIDENCE BESIDE THE "
               "NEGATIVE CONTROL: `negative_control` above runs arm_aslr.c "
               "through the SAME counter and must report MORE than one "
               "distinct value, or this instrument is blind and nothing here "
               "means anything. Added at TASK_147; TASK_145_REPORT 6a is where "
               "the gap was found."}
    out = os.path.join(HERE, "repro.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    if unstable:
        print(f"  *** UNSTABLE CELLS: {unstable} -- p32's whole reproducibility "
              f"claim is that there are none", file=sys.stderr)
    if not neg["fired"]:
        print(f"  *** THE NEGATIVE CONTROL IS DEAD: arm_aslr.c gave "
              f"{neg['distinct']} distinct value(s) in {a.runs} runs at "
              f"randomize_va_space={neg['randomize_va_space']}. A 20-run "
              f"reproducibility test that cannot report >1 proves nothing, so "
              f"every count above is vacuous.", file=sys.stderr)
    return 1 if (unstable or not neg["fired"]) else 0


if __name__ == "__main__":
    sys.exit(main())
