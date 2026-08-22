#!/usr/bin/env python3
"""p38's swept laws, fitted on two bands and tested OUT OF SAMPLE on a third.

Two structural parameters vary independently in `inputs/gen.py --sweep`:
`nrec` (records per window, band `sweep-r*`) and `rlen` (32-bit units per
record, band `sweep-w*`). Band `sweep-x*` contains pairs neither band has, so a
law fitted on `r` and `w` can be *predicted* on `x` rather than re-fitted --
which is the only out-of-sample test this project has that can fail
(`.memory/03-measurement.md`).

What is fitted is a **matched-spelling difference** between two cells on the
same blob, never a bare rate: the driver's per-call constant, the decode loop
and the payload fold are all identical between the two cells and cancel
exactly.

    python3 patterns/p38-alias-pun/controls/fit.py
    python3 patterns/p38-alias-pun/controls/fit.py --pairs r1h_r1 r3_r4
"""

import argparse
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p38", "fit")
assert OUT.endswith(os.path.join("p38", "fit")), OUT
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
BUILD = os.path.join(REPO, ".temp", "build", "p38")
INPUTS = os.path.join(PDIR, "inputs")

PAIRS = {
    # R1h - R1: the price of the DEFINED two-half read against the UB one.
    "r1h_r1": ("c-gcc-h-O3-isolated", "c-gcc-O3-isolated",
               "gcc: defined two-half read minus the pun"),
    "r1h_r1_clang": ("c-clang-h-O3-isolated", "c-clang-O3-isolated",
                     "clang: defined two-half read minus the pun"),
    # R3 - R4: p38's fixed-R4 safety bound.
    "r3_r4": ("safe_tuned-O3-isolated", "unsafe-O3-isolated",
              "safe tuned minus unsafe"),
    "r2_r4": ("safe_naive-O3-isolated", "unsafe-O3-isolated",
              "safe naive minus unsafe"),
}


def shape(name):
    """(nrec, rlen) from the blob name, or None for a heterogeneous band."""
    m = re.match(r"sweep-r(\d+)\.bin$", name)
    if m:
        return int(m.group(1)), 4
    m = re.match(r"sweep-w(\d+)\.bin$", name)
    if m:
        return 2, int(m.group(1))
    m = re.match(r"sweep-x(\d+)u(\d+)\.bin$", name)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def probe(blob, n):
    b = open(os.path.join(INPUTS, blob), "rb").read()
    os.makedirs(OUT, exist_ok=True)
    o = os.path.join(OUT, f"probe-{n}-{blob}")
    open(o, "wb").write(struct.pack("<Q", n) + b[8:])
    return o


def ir(exe, arg):
    o = os.path.join(OUT, f"cg.{os.getpid()}")
    r = subprocess.run([VALGRIND, "--tool=callgrind", f"--callgrind-out-file={o}",
                        exe, arg], capture_output=True, text=True, timeout=1800)
    if r.returncode:
        return None
    for line in open(o):
        if line.startswith(("summary:", "totals:")):
            return int(line.split()[1])
    return None


def marginal(exe, blob, lo=100, hi=200):
    a, b = ir(exe, probe(blob, lo)), ir(exe, probe(blob, hi))
    return None if a is None or b is None else (b - a) / (hi - lo)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pairs", nargs="*", default=list(PAIRS))
    a = ap.parse_args()

    blobs = sorted(f for f in os.listdir(INPUTS)
                   if f.startswith("sweep-") and shape(f))
    fitset = [b for b in blobs if not b.startswith("sweep-x")]
    oos = [b for b in blobs if b.startswith("sweep-x")]

    for pair in a.pairs:
        hi_c, lo_c, why = PAIRS[pair]
        hi_p, lo_p = os.path.join(BUILD, hi_c), os.path.join(BUILD, lo_c)
        if not (os.path.exists(hi_p) and os.path.exists(lo_p)):
            print(f"{pair}: build the matrix first (harness/build.py p38)")
            continue
        print(f"\n=== {pair}: {why} ===")
        rows = []
        for b in fitset + oos:
            nrec, rlen = shape(b)
            d = marginal(hi_p, b) - marginal(lo_p, b)
            rows.append((b, nrec, rlen, d))
        # least squares on the FIT set only: d = a0 + a1*nrec + a2*nrec*rlen
        import itertools
        fit = [r for r in rows if not r[0].startswith("sweep-x")]
        n = len(fit)
        X = [[1.0, float(r[1]), float(r[1] * r[2])] for r in fit]
        y = [r[3] for r in fit]
        # normal equations, 3x3, solved by Gaussian elimination
        A = [[sum(X[k][i] * X[k][j] for k in range(n)) for j in range(3)]
             + [sum(X[k][i] * y[k] for k in range(n))] for i in range(3)]
        for i in range(3):
            p = max(range(i, 3), key=lambda t: abs(A[t][i]))
            A[i], A[p] = A[p], A[i]
            if abs(A[i][i]) < 1e-12:
                continue
            for j in range(i + 1, 3):
                f = A[j][i] / A[i][i]
                for kk in range(i, 4):
                    A[j][kk] -= f * A[i][kk]
        c = [0.0, 0.0, 0.0]
        for i in reversed(range(3)):
            if abs(A[i][i]) < 1e-12:
                continue
            c[i] = (A[i][3] - sum(A[i][j] * c[j] for j in range(i + 1, 3))) / A[i][i]
        print(f"    fitted on {n} blobs (bands r and w): "
              f"d = {c[0]:.5f} + {c[1]:.5f}*nrec + {c[2]:.5f}*nrec*rlen")
        worst_in = max(abs(r[3] - (c[0] + c[1] * r[1] + c[2] * r[1] * r[2]))
                       for r in fit)
        print(f"    max in-sample residual  {worst_in:.5f}")
        print(f"    {'blob':20s} {'nrec':>5s} {'rlen':>5s} {'measured':>10s} "
              f"{'predicted':>10s} {'resid':>8s}")
        worst_out = 0.0
        for b, nrec, rlen, d in rows:
            if not b.startswith("sweep-x"):
                continue
            pred = c[0] + c[1] * nrec + c[2] * nrec * rlen
            worst_out = max(worst_out, abs(d - pred))
            print(f"    {b:20s} {nrec:5d} {rlen:5d} {d:10.2f} {pred:10.2f} "
                  f"{d - pred:8.2f}")
        print(f"    max OUT-OF-SAMPLE residual {worst_out:.5f}")
        for b, nrec, rlen, d in rows:
            if b.startswith("sweep-x"):
                continue
            print(f"      fit {b:20s} nrec={nrec:3d} rlen={rlen:3d} d={d:9.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
