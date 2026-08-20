#!/usr/bin/env python3
"""p06's fitter: the laws, the pooled design's RANK, and the out-of-sample test.

`.memory/03-measurement.md` asks three things of a cost law and this file does
all three in one place, from the JSON `sweep_ir.py` writes:

1. **Report the rank of the pooled design before believing a coefficient.**
   Each band on its own is rank-deficient by construction -- band N holds `m`,
   band M holds `nrec`, band R holds both -- so a coefficient identified only
   within one band is a coefficient the band cannot see.
2. **Hold out a LENGTH, not a mixture** (p13's out-of-sample test could not
   fail, because every held-out row was a linear combination of the fit rows).
   Here that is **leave-one-`m`-out** on band M: drop every blob at one `m`,
   fit on the rest, predict the dropped one.
3. **A law is a law in SOMEBODY's counts** (p04). Every regressor here is read
   back out of the BLOB by `sweep_ir.shape`, so the counts are the file's and
   not `gen.py`'s.

    python3 patterns/p06-rotate/controls/fit.py .temp/p06/sweep-*.json

Regressors: `1`, `nrec`, `sum_m` (bytes in the live extents), `parity`
(records with `m` even and `r` odd -- the extra swap), `rzero` (records with
`r == 0`, where the first reverse loop is skipped entirely).
"""

import json
import os
import sys
from fractions import Fraction as F

REG = ["one", "nrec", "sum_m", "parity", "rzero"]

# Band M's clean domain. Below this the fold's 4x unroll cannot run and the
# three reverse ranges are degenerate, so `m = 1, 2, 3` are genuinely different
# programs and not points on the same law. MEASURED, not assumed: with MMIN = 3
# the leave-one-m-out test on `R3 - R4` MISSES BY -48 at m = 3 and by +7..+12
# everywhere else in that residue class; with MMIN = 4 it is exact on all 45.
# `.memory/03-measurement.md`: state the DOMAIN of a law.
MMIN = int(os.environ.get("SLB_P06_MMIN", "4"))


def design(rows):
    return [[F(1), F(r["nrec"]), F(r["sum_m"]), F(r["parity"]), F(r["rzero"])]
            for r in rows]


def rank(mat):
    """Exact rational rank -- no floating-point tolerance to argue about."""
    m = [row[:] for row in mat]
    nr, nc, rk = len(m), len(m[0]), 0
    for c in range(nc):
        piv = next((r for r in range(rk, nr) if m[r][c] != 0), None)
        if piv is None:
            continue
        m[rk], m[piv] = m[piv], m[rk]
        pv = m[rk][c]
        m[rk] = [x / pv for x in m[rk]]
        for r in range(nr):
            if r != rk and m[r][c] != 0:
                f = m[r][c]
                m[r] = [a - f * b for a, b in zip(m[r], m[rk])]
        rk += 1
    return rk


def lstsq(A, y):
    """Least squares by exact normal equations over the rationals."""
    n = len(A[0])
    ata = [[sum(A[k][i] * A[k][j] for k in range(len(A))) for j in range(n)]
           for i in range(n)]
    aty = [sum(A[k][i] * y[k] for k in range(len(A))) for i in range(n)]
    # Gauss-Jordan on [ata | aty]
    m = [ata[i][:] + [aty[i]] for i in range(n)]
    for c in range(n):
        piv = next((r for r in range(c, n) if m[r][c] != 0), None)
        if piv is None:
            return None
        m[c], m[piv] = m[piv], m[c]
        pv = m[c][c]
        m[c] = [x / pv for x in m[c]]
        for r in range(n):
            if r != c and m[r][c] != 0:
                f = m[r][c]
                m[r] = [a - f * b for a, b in zip(m[r], m[c])]
    return [m[i][n] for i in range(n)]


def main():
    args = sys.argv[1:]
    diff = None
    if args and args[0].startswith("--diff="):
        diff = args[0].split("=", 1)[1].split(",")
        args = args[1:]
    paths = args
    rows, cells = [], None
    for p in paths:
        d = json.load(open(p))
        cells = d["cells"] if cells is None else [c for c in cells if c in d["cells"]]
        for r in d["rows"]:
            r["band"] = d["band"]
            rows.append(r)
    print(f"{len(rows)} blob(s) over bands {sorted({r['band'] for r in rows})}, "
          f"cells common to all files: {cells}")

    print("\n-- RANK of the design, per band and pooled "
          f"(regressors {REG}) --")
    for b in sorted({r["band"] for r in rows}) + ["POOLED"]:
        sel = rows if b == "POOLED" else [r for r in rows if r["band"] == b]
        print(f"   {b:8s} n={len(sel):3d}  rank={rank(design(sel))} of {len(REG)}")

    if diff:
        a_, b_ = diff
        cells = [f"{a_} - {b_}"]
    for c in cells:
        if diff:
            sel = [r for r in rows
                   if r["ir"].get(diff[0]) is not None
                   and r["ir"].get(diff[1]) is not None]
            y = [F(str(r["ir"][diff[0]])).limit_denominator(10000)
                 - F(str(r["ir"][diff[1]])).limit_denominator(10000) for r in sel]
        else:
            sel = [r for r in rows if r["ir"].get(c) is not None]
            y = [F(str(r["ir"][c])).limit_denominator(10000) for r in sel]
        A = design(sel)
        beta = lstsq(A, y)
        if beta is None:
            print(f"\n-- {c}: normal equations singular (design rank "
                  f"{rank(A)}) --")
            continue
        res = [float(yy - sum(a * b for a, b in zip(row, beta)))
               for row, yy in zip(A, y)]
        print(f"\n-- {c} --")
        print("   " + "  ".join(f"{n}={float(b):+.4f}" for n, b in zip(REG, beta)))
        print(f"   max |residual| = {max(abs(r) for r in res):.4f} over {len(sel)} blobs")
    if diff and any(r["band"] == "m" for r in rows):
        lomo(rows, diff[0], diff[1])


def lomo(rows, a, b):
    """LEAVE-ONE-`m`-OUT on band M, which is the out-of-sample test TASK_047
    asked for and the one p13's could not fail.

    Band M holds `nrec` at 8 and sweeps `m`, so the basis is `1`, `sum_m` and
    one indicator per `m mod 8` residue class -- the residue structure is real
    (`R3 - R4`'s per-record constant takes four distinct values) and a fit that
    ignores it is a fit of the wrong model. Dropping ALL blobs at one `m` leaves
    that `m`'s residue class covered by `m +- 8`, so the held-out point is NOT a
    linear combination of the fit rows in the sense that matters: its `sum_m` is
    outside the convex hull of nothing, but its (residue, sum_m) pair has never
    been seen."""
    sel = [r for r in rows if r["band"] == "m" and r["sum_m"] // 8 >= MMIN
           and r["ir"].get(a) is not None and r["ir"].get(b) is not None]
    ms = sorted({r["sum_m"] // 8 for r in sel})

    def basis(r):
        m = r["sum_m"] // 8
        # NO separate intercept: the eight residue indicators already sum to
        # 1, so adding one makes the normal equations singular.
        v = [F(r["sum_m"])]
        v += [F(1) if m % 8 == k else F(0) for k in range(8)]
        return v

    print(f"\n-- LEAVE-ONE-m-OUT on band M, {a} - {b} "
          f"({len(sel)} blobs, m = {ms[0]}..{ms[-1]}) --")
    worst = 0.0
    for held in ms:
        fit = [r for r in sel if r["sum_m"] // 8 != held]
        test = [r for r in sel if r["sum_m"] // 8 == held]
        A = [basis(r) for r in fit]
        y = [F(str(r["ir"][a])).limit_denominator(10000)
             - F(str(r["ir"][b])).limit_denominator(10000) for r in fit]
        beta = lstsq(A, y)
        if beta is None:
            print(f"   m={held:2d}: singular without it")
            continue
        for r in test:
            pred = float(sum(x * bb for x, bb in zip(basis(r), beta)))
            got = r["ir"][a] - r["ir"][b]
            worst = max(worst, abs(got - pred))
            print(f"   m={held:2d}  predicted {pred:10.3f}  measured {got:10.3f}"
                  f"  miss {got - pred:+8.3f}")
    print(f"   worst out-of-sample miss: {worst:.3f}")


if __name__ == "__main__":
    main()
