#!/usr/bin/env python3
"""Price the work the kernel DISPATCHES OUTWARD -- the number a licence cannot give.

⚠ **PROTOTYPE, parked here deliberately.**  `.tasks/TASK_075.md` §0 asks whether
the callee column should be *recorded*, computed *on demand*, or replaced by a
*static licence*.  `synthesis/licence.py` is the static check; this is the
on-demand tool, and the two are complements rather than alternatives:

  * the licence says **"this row is quotable"** and costs ~2 s for the tree;
  * it does **not** say what the number would be if you corrected it, and on
    p11 the correction **reverses the sign** (`R3 - R4` on `small`:
    -5768.00 kernel-exclusive, **+4053.15** with the callee).

It is NOT in `harness/`: `check.py` hashes `harness/*.py` into all 22 gate
records and `measure.py` is hashed into all 22 MEASUREMENT records, so putting
it there would force a full re-measure, which re-takes the wall-clock block.

HOW.  It runs callgrind once per cell and parses the raw `callgrind.out`
instead of `callgrind_annotate`, because the raw file carries the caller->callee
edges that the annotation throws away:

    fn=(id) <kernel>
    cfn=(id) <callee>
    calls=<n> <target>
    <line> <cost>            <- INCLUSIVE cost of those calls

    kernel_inclusive = kernel_exclusive + sum(edges out of kernel)

VALIDATION -- it re-derives three separately reviewed published numbers it was
never told:

    p13  R2 outward - R4 outward   = -190.00 small / -264.00 large
         == `.memory/03-measurement.md`: "overstated by 190 / 264 Ir/call,
            entirely because R2 makes no `memcpy` call and R4 does"
    p36  dispatch-target Ir/call   = gcc 512.00, clang/rustc 384.00
         == `.memory/03-measurement.md` (TASK_073), to the instruction
    p36  gcc-vs-clang, kernel col  = -120.00 / -1016.00  ->  +8.00 / +8.00
         == "the gcc-vs-clang C gap vanishes: 10*nrw vs 11*nrw becomes 14 vs 14"

⚠ TWO CAVEATS ON THE COLUMN ITSELF, both measured here and both meaning that
adding callees is not uniformly an improvement:

  * **p03/p04**: glibc `memset`'s path length moves with the stack array's
    alignment, so cells with identical call sets differ by +-7.00 Ir/call.
    On this column p03's `R5 - R4` reads **-7.00** -- "the proof costs -7
    instructions" -- and p04's `R3 - R4` flips sign.  There the
    kernel-EXCLUSIVE column is the correct one.
  * **gcc's PLT thunk**: gcc routes each libc call through `endbr64 ; jmp *GOT`,
    which callgrind attributes as its own function; clang's thunk is a bare
    `jmp` and is folded into the callee.  **+2.00 Ir per libc call, gcc only**,
    and one of the two instructions is the `endbr64` of gcc's default
    `-fcf-protection=full`.  This column therefore carries an IBT term the
    kernel-exclusive column never had.

Usage:
    synthesis/outward_ir.py p13 --input small.bin
    synthesis/outward_ir.py --emit synthesis/outward_ir.json     # whole tree
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "harness"))
import build as bld  # noqa: E402

VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
BUILD = os.path.join(REPO, ".temp", "build")
SCRATCH = os.path.join(REPO, ".temp", "synth-cg")
KERNEL_RE = re.compile(r"(?:^|::)kernel(?:$|[^A-Za-z0-9_])")
PAIRS = [("safe_naive", "unsafe", "R2-R4"),
         ("safe_tuned", "unsafe", "R3-R4"),
         ("verus", "unsafe", "R5-R4"),
         ("c-gcc", "c-clang", "gcc-clang")]


def parse_cg(path):
    """-> (names{id: str}, exclusive{id: Ir}, edges{(caller,callee): Ir})."""
    names, excl, edges = {}, {}, {}
    cur, pend, armed = None, None, False
    for line in open(path, errors="replace"):
        line = line.rstrip("\n")
        m = re.match(r"^(c?fn)=\((\d+)\)(?:\s+(.*))?$", line)
        if m:
            kind, fid, nm = m.group(1), int(m.group(2)), m.group(3)
            if nm:
                names[fid] = nm
            if kind == "fn":
                cur, pend, armed = fid, None, False
            else:
                pend = fid
            continue
        if re.match(r"^(c?ob|c?fl|c?fi|c?fe)=", line):
            continue
        if line.startswith("calls="):
            armed = True
            continue
        m = re.match(r"^([+\-*]?\d+|\*)\s+(\d+)", line)
        if m:
            ir = int(m.group(2))
            if armed and pend is not None and cur is not None:
                edges[(cur, pend)] = edges.get((cur, pend), 0) + ir
                armed, pend = False, None
            elif cur is not None:
                excl[cur] = excl.get(cur, 0) + ir
    return names, excl, edges


def measure(binary, arg, tag, timeout=3600):
    os.makedirs(SCRATCH, exist_ok=True)
    out = os.path.join(SCRATCH, f"cg.{tag}.out")
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={out}", binary, arg],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"callgrind exit {r.returncode}: {r.stderr[-300:]}")
    names, excl, edges = parse_cg(out)
    kids = [i for i, n in names.items() if KERNEL_RE.search(n)]
    kex = sum(excl.get(i, 0) for i in kids)
    by = {}
    for (x, y), ir in edges.items():
        if x in kids:
            n = names.get(y, f"?{y}")
            by[n] = by.get(n, 0) + ir
    return {"kernel_symbols": [names[i] for i in kids],
            "kernel_exclusive_ir": kex,
            "outward_ir": sum(by.values()),
            "outward_by_callee": dict(sorted(by.items(), key=lambda kv: -kv[1])),
            "kernel_inclusive_ir": kex + sum(by.values())}


def record_for(pat):
    """The measurement record with `cells` -- a pattern can own a SIDE record
    too (`results/p02-residue-sweep.json`, whose `inputs` is a string) and
    picking it by prefix alone crashes."""
    for f in sorted(glob.glob(os.path.join(REPO, "results", pat + "-*.json"))):
        d = json.load(open(f))
        if "cells" in d and isinstance(d.get("inputs"), dict):
            return d
    return None


def pattern_dir(pat):
    for d in sorted(os.listdir(os.path.join(REPO, "patterns"))):
        if d.startswith(pat + "-"):
            return os.path.join(REPO, "patterns", d)
    raise KeyError(pat)


def run_pattern(pat, inp, opt="O3", mode="isolated", cells=None, echo=True):
    rec = record_for(pat)
    if rec is None:
        return None
    n = rec["inputs"].get(inp, {}).get("n_iters")
    if not n:
        return None
    pdir = pattern_dir(pat)
    cells = cells or bld.measured_cells(pdir)
    blob = os.path.join(pdir, "inputs", inp)
    out = {"pattern": pat, "input": inp, "opt": opt, "mode": mode,
           "n_iters": n, "cells": {}}
    if echo:
        print(f"# {pat} {opt}/{mode} {inp}  n_iters={n}")
        print(f"{'cell':12s} {'kern.excl/call':>15s} {'outward/call':>13s} "
              f"{'kern.incl/call':>15s}")
    for c in cells:
        p = os.path.join(BUILD, pat, f"{c}-{opt}-{mode}")
        if not os.path.exists(p):
            continue
        r = measure(p, blob, f"{pat}-{c}-{opt}-{mode}-{inp}")
        out["cells"][c] = r
        if echo:
            print(f"{c:12s} {r['kernel_exclusive_ir']/n:15.2f} "
                  f"{r['outward_ir']/n:13.2f} {r['kernel_inclusive_ir']/n:15.2f}"
                  + ("   " + ", ".join(f"{k.split('::')[-1][:26]}={v/n:.2f}"
                                       for k, v in r["outward_by_callee"].items())
                     if r["outward_by_callee"] else ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern", nargs="?")
    ap.add_argument("--input", default="small.bin")
    ap.add_argument("--opt", default="O3")
    ap.add_argument("--mode", default="isolated")
    ap.add_argument("--emit", metavar="PATH")
    a = ap.parse_args()

    if not a.emit:
        run_pattern(a.pattern, a.input, a.opt, a.mode)
        return

    pats = sorted(d for d in os.listdir(BUILD) if re.fullmatch(r"p\d\d", d))
    doc = {}
    for pat in pats:
        doc[pat] = {}
        for inp in ("small.bin", "large.bin"):
            r = run_pattern(pat, inp, a.opt, a.mode)
            if r is None:
                continue
            n = r["n_iters"]
            cells = {c: {"kernel_exclusive_ir_per_call": v["kernel_exclusive_ir"] / n,
                         "outward_ir_per_call": v["outward_ir"] / n,
                         "kernel_inclusive_ir_per_call": v["kernel_inclusive_ir"] / n,
                         "outward_by_callee_per_call":
                             {k: x / n for k, x in v["outward_by_callee"].items()}}
                     for c, v in r["cells"].items()}
            pairs = {}
            for x, y, lab in PAIRS:
                if x in cells and y in cells:
                    de = (cells[x]["kernel_exclusive_ir_per_call"]
                          - cells[y]["kernel_exclusive_ir_per_call"])
                    di = (cells[x]["kernel_inclusive_ir_per_call"]
                          - cells[y]["kernel_inclusive_ir_per_call"])
                    pairs[lab] = {"kernel_exclusive": de,
                                  "kernel_plus_callees": di,
                                  "moves_by": di - de}
            doc[pat][inp] = {"n_iters": n, "cells": cells, "pairs": pairs}
    json.dump(doc, open(a.emit, "w"), indent=1, sort_keys=True)
    print(f"wrote {a.emit}: {len(doc)} patterns")


if __name__ == "__main__":
    main()
