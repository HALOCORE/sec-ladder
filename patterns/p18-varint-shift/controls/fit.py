#!/usr/bin/env python3
"""Fit `Ir/call = a*bytes + b*varints + c` per cell over p18's sweep, and report
the things `.memory/03-measurement.md` says a fitted law owes.

    python3 patterns/p18-varint-shift/controls/sweep_ir.py --band all --cells all \
        --json .temp/p18/sweep_all_O3.json
    python3 patterns/p18-varint-shift/controls/fit.py .temp/p18/sweep_all_O3.json

What it prints, and why each line is there:

  * the exact rational solution and the max |residual| over the whole sweep;
  * **the RANK of the design after dropping each band** -- the test
    `.memory/03-measurement.md` added after p13 and p14 both shipped a
    leave-one-out that was arithmetically incapable of failing. p18's pooled
    design is rank 3; band b holds `nv` fixed and band v holds `bytes/nv` fixed,
    so **dropping either takes it to rank 2 and the hold-out CAN fail**. Dropping
    band x leaves rank 3 and the hold-out there is an interpolation check, which
    is said rather than hidden;
  * the leave-one-band-out prediction error for each band, with the post-drop
    rank beside it;
  * an OUT-OF-SAMPLE prediction for `small.bin` and `large.bin` if their rows
    are supplied -- neither is in any band, both are length-heterogeneous, and
    `small` is 1.45x outside the largest sweep byte count.

No numpy on this box, so the solve is exact rational arithmetic over
`fractions.Fraction` (3x3 Gaussian elimination with the normal equations, or
exact interpolation when the design is square). That also means "max residual
0.0000" here is really zero and not a float artefact -- which matters, because
an exactly-zero residual is the signature `.memory/03-measurement.md` warns
about.
"""

import argparse
import itertools
import json
import os
import sys
from fractions import Fraction as F

COLS = ("bytes", "nv", "one")


def row_vec(r):
    return [F(r["bytes"]), F(r["nv"]), F(1)]


def rank(rows):
    """Exact rank of a list of rational row vectors."""
    m = [list(r) for r in rows]
    n, piv = len(m), 0
    if not n:
        return 0
    ncol = len(m[0])
    for c in range(ncol):
        p = None
        for i in range(piv, n):
            if m[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        m[piv], m[p] = m[p], m[piv]
        inv = m[piv][c]
        m[piv] = [x / inv for x in m[piv]]
        for i in range(n):
            if i != piv and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[piv])]
        piv += 1
        if piv == n:
            break
    return piv


def solve_ls(rows, ys):
    """Least squares by exact normal equations. Returns None if singular."""
    k = len(rows[0])
    a = [[sum(r[i] * r[j] for r in rows) for j in range(k)] + [F(0)]
         for i in range(k)]
    for i in range(k):
        a[i][k] = sum(r[i] * y for r, y in zip(rows, ys))
    # Gaussian elimination
    for c in range(k):
        p = None
        for i in range(c, k):
            if a[i][c] != 0:
                p = i
                break
        if p is None:
            return None
        a[c], a[p] = a[p], a[c]
        inv = a[c][c]
        a[c] = [x / inv for x in a[c]]
        for i in range(k):
            if i != c and a[i][c] != 0:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[c])]
    return [a[i][k] for i in range(k)]


def band_of(name):
    b = name.replace("sweep-", "")
    return b[0] if b[:1] in ("b", "v", "x") else "?"


def fmt(x):
    f = float(x)
    return f"{f:.4f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json", nargs="+", help="sweep_ir.py --json output(s)")
    ap.add_argument("--oos", help="a second sweep_ir.py --json holding the "
                                  "small/large rows, measured with --blobs")
    a = ap.parse_args()
    rows, cells = [], None
    for p in a.json:
        d = json.load(open(p))
        rows += [r for r in d["rows"] if r["blob"].startswith("sweep-")]
        cells = d["cells"] if cells is None else cells
    if not rows:
        raise SystemExit("no sweep-* rows in the input json")
    bands = sorted({band_of(r["blob"]) for r in rows})
    X = [row_vec(r) for r in rows]
    print(f"  {len(rows)} sweep row(s), bands {bands}, "
          f"pooled design rank {rank(X)} of {len(COLS)} column(s) {COLS}")
    for b in bands:
        sub = [row_vec(r) for r in rows if band_of(r["blob"]) != b]
        only = [row_vec(r) for r in rows if band_of(r["blob"]) == b]
        print(f"    drop band {b}: {len(sub)} row(s) left, rank {rank(sub)}"
              f"   (band {b} alone: {len(only)} row(s), rank {rank(only)})"
              + ("   <-- hold-out CANNOT fail (design stays full rank)"
                 if rank(sub) == len(COLS) else
                 "   <-- hold-out CAN fail"))
    print()
    hdr = (f"  {'cell':14s} {'a (per byte)':>14s} {'b (per varint)':>16s} "
           f"{'c (per call)':>14s} {'max|resid|':>11s}")
    print(hdr)
    sols = {}
    for c in cells:
        ys = [F(r["ir"][c]).limit_denominator(10 ** 6) for r in rows
              if r["ir"].get(c) is not None]
        xs = [row_vec(r) for r in rows if r["ir"].get(c) is not None]
        if len(ys) != len(rows):
            continue
        s = solve_ls(xs, ys)
        if s is None:
            print(f"  {c:14s} SINGULAR")
            continue
        sols[c] = s
        res = max(abs(float(sum(si * xi for si, xi in zip(s, x)) - y))
                  for x, y in zip(xs, ys))
        print(f"  {c:14s} {fmt(s[0]):>14s} {fmt(s[1]):>16s} {fmt(s[2]):>14s} "
              f"{res:11.4f}")
    print()
    print("  leave-one-band-out: fit on the other bands, predict this one")
    print(f"  {'cell':14s} " + " ".join(f"{'band ' + b:>18s}" for b in bands))
    for c in cells:
        if c not in sols:
            continue
        line = f"  {c:14s} "
        for b in bands:
            fitr = [r for r in rows if band_of(r["blob"]) != b]
            outr = [r for r in rows if band_of(r["blob"]) == b]
            xs = [row_vec(r) for r in fitr]
            ys = [F(r["ir"][c]).limit_denominator(10 ** 6) for r in fitr]
            s = solve_ls(xs, ys)
            if s is None:
                line += f" {'SINGULAR':>18s}"
                continue
            err = max(abs(float(sum(si * xi for si, xi in
                                    zip(s, row_vec(r))) - F(r["ir"][c])
                                .limit_denominator(10 ** 6)))
                      for r in outr)
            line += f" {err:18.4f}"
        print(line)
    if a.oos:
        d = json.load(open(a.oos))
        print()
        print("  OUT OF SAMPLE (no band contains these blobs)")
        print(f"  {'cell':14s} " +
              " ".join(f"{r['blob'][:-4]:>26s}" for r in d["rows"]))
        for c in cells:
            if c not in sols:
                continue
            line = f"  {c:14s} "
            for r in d["rows"]:
                if r["ir"].get(c) is None:
                    line += f" {'--':>26s}"
                    continue
                pred = float(sum(si * xi for si, xi in
                                 zip(sols[c], row_vec(r))))
                line += f" {pred:11.2f} vs {r['ir'][c]:10.2f}"
            print(line)
        for r in d["rows"]:
            print(f"    {r['blob']}: bytes={r['bytes']} nv={r['nv']}, "
                  f"in the fit set's row space: "
                  f"{rank(X) == rank(X + [row_vec(r)])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
