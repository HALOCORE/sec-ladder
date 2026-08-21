#!/usr/bin/env python3
"""Fit `Ir/call = a*bytes + b*varints [+ d*cut + e*brk] + c` per cell over p18's
sweep, and report the things `.memory/03-measurement.md` says a fitted law owes.

    python3 patterns/p18-varint-shift/controls/sweep_ir.py --band all --cells all \
        --json .temp/p18/sweep_all_O3.json
    python3 patterns/p18-varint-shift/controls/fit.py .temp/p18/sweep_all_O3.json

⚠ **EVERY LAW HAS A DOMAIN, AND UNTIL TASK_052 THIS FILE DID NOT PRINT IT.**
Bands b, v, x and y all have `cut == 0` and `brk == 0` -- every varint
terminates inside its window and the declared count equals the walked count --
so `[bytes, nv, 1]` was the only identifiable design and the laws it produced
were laws of that one regime. `inputs/degenerate.bin`, a **committed matrix
input**, has `cut = brk = 1`, misses the published laws by +2.00 / +5.00 /
+8.00, and takes `R3 - R4` the wrong way round (TASK_051_REVIEW blocker 1).
Band `t` (TASK_052) varies the two parameters independently; `--cols auto`
includes a column exactly when the supplied rows actually vary it, so an
invocation on b/v/x reproduces the three-column fit unchanged and one that also
has band `t` gets the domain terms.

What it prints, and why each line is there:

  * the columns the design actually supports, and which of `cut`/`brk` were
    dropped for being identically zero -- i.e. **the domain of the law printed
    below it**;
  * the exact rational solution and the max |residual| over the whole sweep;
  * **the RANK of the design after dropping each band** -- the test
    `.memory/03-measurement.md` added after p13 and p14 both shipped a
    leave-one-out that was arithmetically incapable of failing. The criterion is
    RANK AFTER THE DROP, not column count: p18's pooled b/v/x design is rank 3
    and **band x alone is already rank 3**, so dropping any single band leaves
    it full rank and the hold-out cannot fail. (A three-column design with two
    rank-2 bands pools to rank 3 and its hold-out CAN fail, so "3 columns" is
    not the diagnosis -- TASK_051_REVIEW M5.);
  * the leave-one-band-out prediction error for each band, with the post-drop
    rank beside it;
  * an OUT-OF-SAMPLE prediction for `small.bin` and `large.bin` if their rows
    are supplied -- neither is in any band, both are length-heterogeneous, and
    `small` is 1.45x outside the largest sweep byte count.

No numpy on this box, so the solve is exact rational arithmetic over
`fractions.Fraction` (Gaussian elimination on the normal equations). That also
means "max residual 0.0000" here is really zero and not a float artefact --
which matters, because an exactly-zero residual is the signature
`.memory/03-measurement.md` warns about.
"""

import argparse
import itertools
import json
import os
import sys
from fractions import Fraction as F

ALL_COLS = ("bytes", "nv", "cut", "brk", "one")
BASE_COLS = ("bytes", "nv", "one")


def pick_cols(rows, spec):
    """`--cols auto`: `bytes`, `nv`, an intercept, plus `cut` and/or `brk`
    whenever the supplied rows actually vary them. A column that is identically
    zero carries no information and makes the normal equations singular, so
    including it would turn a stated domain into a `SINGULAR` line."""
    if spec != "auto":
        cols = tuple(c.strip() for c in spec.split(",") if c.strip())
        bad = [c for c in cols if c not in ALL_COLS]
        if bad:
            raise SystemExit(f"unknown column(s) {bad}; pick from {ALL_COLS}")
        return cols
    cols = ["bytes", "nv"]
    for c in ("cut", "brk"):
        if any(r.get(c) for r in rows):
            cols.append(c)
    cols.append("one")
    return tuple(cols)


def row_vec(r, cols=BASE_COLS):
    return [F(1) if c == "one" else F(r.get(c, 0)) for c in cols]


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
    return b[0] if b[:1] in ("b", "v", "x", "y", "t") else "?"


def fmt(x):
    f = float(x)
    return f"{f:.4f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json", nargs="+", help="sweep_ir.py --json output(s)")
    ap.add_argument("--oos", help="a second sweep_ir.py --json holding the "
                                  "small/large rows, measured with --blobs")
    ap.add_argument("--cols", default="auto",
                    help="'auto' (default: bytes,nv,one plus cut and/or brk "
                         "wherever the rows vary them) or an explicit "
                         "comma-separated subset of " + ",".join(ALL_COLS))
    ap.add_argument("--holdout-blobs",
                    help="comma-separated sweep blob names REMOVED from the fit "
                         "and predicted instead. This is how ../NOTES.md 4a2's "
                         "additivity test is run: hold out every row where BOTH "
                         "`cut` and `brk` fire, fit the two columns on rows "
                         "where each fires alone, and see whether the sum "
                         "predicts the product. A `cut x brk` interaction shows "
                         "up here and nowhere else.")
    a = ap.parse_args()
    rows, cells = [], None
    for p in a.json:
        d = json.load(open(p))
        rows += [r for r in d["rows"] if r["blob"].startswith("sweep-")]
        cells = d["cells"] if cells is None else cells
    if not rows:
        raise SystemExit("no sweep-* rows in the input json")
    held = []
    if a.holdout_blobs:
        want = {b.strip() for b in a.holdout_blobs.split(",") if b.strip()}
        missing = want - {r["blob"] for r in rows}
        if missing:
            raise SystemExit(f"--holdout-blobs names {sorted(missing)}, which "
                             f"is not in the supplied json")
        held = [r for r in rows if r["blob"] in want]
        rows = [r for r in rows if r["blob"] not in want]
        print(f"  HELD OUT of the fit: {sorted(want)}")
    bands = sorted({band_of(r["blob"]) for r in rows})
    COLS = pick_cols(rows, a.cols)
    dropped = [c for c in ("cut", "brk") if c not in COLS]
    X = [row_vec(r, COLS) for r in rows]
    print(f"  {len(rows)} sweep row(s), bands {bands}, "
          f"pooled design rank {rank(X)} of {len(COLS)} column(s) {COLS}")
    if dropped:
        absent = [c for c in dropped if not all(c in r for r in rows)]
        # ⚠ Only claim "== 0 on every row" when it IS zero on every row. With an
        # explicit `--cols` a caller can drop a column the rows DO vary, and the
        # honest thing is then to say the fit is misspecified rather than to
        # print a domain that the fit set itself violates.
        violated = sorted({c for c in dropped for r in rows if r.get(c)})
        print(f"    DOMAIN: the law below has no {' or '.join(dropped)} term, "
              f"so it is stated ONLY for windows where "
              f"{' and '.join(dropped)} is 0"
              + "  (cut: some varint ended on window exhaustion; "
                "brk: the outer loop exited on `p == len`)")
        if violated:
            print(f"    !! {violated} is NON-ZERO on "
                  f"{sum(1 for r in rows if any(r.get(c) for c in violated))} "
                  f"of the {len(rows)} fit row(s) -- you dropped a column the "
                  f"data varies (explicit --cols), so this fit is MISSPECIFIED "
                  f"and its residual is not a model error bound.")
        else:
            print(f"    ...which every one of the {len(rows)} fit row(s) "
                  f"satisfies.")
        if absent:
            print(f"    !! {absent} is ABSENT from at least one row, i.e. the "
                  f"json predates TASK_052's sweep_ir.py. Treated as 0, which "
                  f"is right for bands b/v/x/y and wrong for band t -- "
                  f"re-measure rather than trust it.")
    for b in bands:
        sub = [row_vec(r, COLS) for r in rows if band_of(r["blob"]) != b]
        only = [row_vec(r, COLS) for r in rows if band_of(r["blob"]) == b]
        print(f"    drop band {b}: {len(sub)} row(s) left, rank {rank(sub)}"
              f"   (band {b} alone: {len(only)} row(s), rank {rank(only)})"
              + ("   <-- hold-out CANNOT fail (design stays full rank)"
                 if rank(sub) == len(COLS) else
                 "   <-- hold-out CAN fail"))
    print()
    names = {"bytes": "a (per byte)", "nv": "b (per varint)",
             "cut": "d (per cut)", "brk": "e (per brk)",
             "one": "c (per call)"}
    hdr = f"  {'cell':14s} " + " ".join(f"{names[c]:>16s}" for c in COLS)
    print(hdr + f" {'max|resid|':>11s}")
    sols = {}
    for c in cells:
        ys = [F(r["ir"][c]).limit_denominator(10 ** 6) for r in rows
              if r["ir"].get(c) is not None]
        xs = [row_vec(r, COLS) for r in rows if r["ir"].get(c) is not None]
        if len(ys) != len(rows):
            continue
        s = solve_ls(xs, ys)
        if s is None:
            print(f"  {c:14s} SINGULAR")
            continue
        sols[c] = s
        res = max(abs(float(sum(si * xi for si, xi in zip(s, x)) - y))
                  for x, y in zip(xs, ys))
        print(f"  {c:14s} " + " ".join(f"{fmt(v):>16s}" for v in s)
              + f" {res:11.4f}")
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
            xs = [row_vec(r, COLS) for r in fitr]
            ys = [F(r["ir"][c]).limit_denominator(10 ** 6) for r in fitr]
            s = solve_ls(xs, ys)
            if s is None:
                line += f" {'SINGULAR':>18s}"
                continue
            err = max(abs(float(sum(si * xi for si, xi in
                                    zip(s, row_vec(r, COLS))) - F(r["ir"][c])
                                .limit_denominator(10 ** 6)))
                      for r in outr)
            line += f" {err:18.4f}"
        print(line)
    blocks = []
    if held:
        blocks.append(("HELD OUT of the fit and predicted "
                       "(--holdout-blobs)", held))
    if a.oos:
        blocks.append(("OUT OF SAMPLE (no band contains these blobs)",
                       json.load(open(a.oos))["rows"]))
    for title, drows in blocks:
        print()
        print("  " + title)
        print(f"  {'cell':14s} " +
              " ".join(f"{r['blob'][:-4]:>26s}" for r in drows))
        worst = 0.0
        for c in cells:
            if c not in sols:
                continue
            line = f"  {c:14s} "
            for r in drows:
                if r["ir"].get(c) is None:
                    line += f" {'--':>26s}"
                    continue
                pred = float(sum(si * xi for si, xi in
                                 zip(sols[c], row_vec(r, COLS))))
                worst = max(worst, abs(pred - float(r["ir"][c])))
                line += f" {pred:11.2f} vs {r['ir'][c]:10.2f}"
            print(line)
        n = sum(1 for c in cells if c in sols) * len(drows)
        print(f"    worst |error| over {n} prediction(s): {worst:.4f}")
        for r in drows:
            out_of_domain = [c for c in ("cut", "brk")
                             if r.get(c) and c not in COLS]
            print(f"    {r['blob']}: bytes={r['bytes']} nv={r['nv']} "
                  f"cut={r.get('cut', '?')} brk={r.get('brk', '?')}, "
                  f"in the fit set's row space: "
                  f"{rank(X) == rank(X + [row_vec(r, COLS)])}"
                  + (f"   <-- OUT OF DOMAIN: {out_of_domain} is non-zero and "
                     f"the law has no such term" if out_of_domain else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
