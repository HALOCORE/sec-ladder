#!/usr/bin/env python3
"""p04's swept laws: kernel-exclusive Ir per call against the four regressors.

    xpush  a push the fullness guard accepts
    dpush  a push the fullness guard REJECTS  (only band F has any)
    xpop   a pop the emptiness guard accepts
    epop   a pop that finds the ring empty    (only band E has any)

Counts are **visit-weighted over the calls the driver actually makes**, replayed
from `model.py`'s own driver loop, because the Lemire index does not visit the 8
windows of a sweep blob equally.

    python3 patterns/p04-ring-buffer/inputs/gen.py --sweep   # the 99 blobs
    python3 harness/build.py p04 --all                      # the cells
    python3 patterns/p04-ring-buffer/controls/sweepfit.py   # measure + fit
    python3 .../sweepfit.py --only N          # one band at a time (each < 5 min)
    python3 .../sweepfit.py --fit             # re-fit from the cached kir.json

It ships in `controls/` rather than under `.temp/` because
`.memory/01-ladder.md` records an OPEN reproduction gap of exactly this shape on
p16 -- twelve probes whose numbers are published and which exist only in
gitignored scratch. `controls/*.py` is inside `check.py`'s `source_sha256` and
outside `measure.py`'s 18 files, so landing it costs a gate re-run and no
re-measure.

⚠ The design's RANK is printed, per band and pooled, over the exact rationals.
p03 measured that every PAIR of its bands is rank-deficient and only the pooled
fit identifies the terms; a rank-deficient least squares returns garbage at zero
residual, so the rank is part of the result and not a footnote.
"""
import argparse
import glob
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(ROOT, "harness"))
sys.path.insert(0, PDIR)
import measure  # noqa: E402
import model as M  # noqa: E402

IN = os.path.join(PDIR, "inputs")
BUILD = os.path.join(ROOT, ".temp", "build", "p04")
SCRATCH = os.path.join(ROOT, ".temp", "p04", "cg")
OUT = os.path.join(ROOT, ".temp", "p04", "kir.json")  # scratch: data, not evidence
# `verus` is omitted: it is byte-identical to `unsafe` at O3 (`md5_raw`
# equal, gate stage 3c), so measuring it would cost 99 more callgrind runs
# to re-derive a row the identity pin already fixes. The MATRIX numbers in
# results/p04-ring-buffer.json do include it, at 0.00 against `unsafe`.
CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe"]
REG = ("xpush", "dpush", "xpop", "epop")


def band_of(stem):
    if stem.startswith("sweep-n"):
        return "N"
    if stem.startswith("sweep-d"):
        return "D"
    if stem.startswith("sweep-f"):
        return "F"
    if stem.startswith("sweep-e"):
        return "E"
    return "matrix"


def regressors(path):
    """Mean per-call counts over the calls the driver actually makes."""
    m = M.build(path)
    tot = dict.fromkeys(REG, 0)
    n = 0
    for c in m.iter_calls():
        w = m.op_counts(c["off"])
        for k in REG:
            tot[k] += w[k]
        n += 1
    return {k: Fraction(tot[k], n) for k in REG}, n


def rank(rows):
    """Exact rational rank of the design matrix (regressors + intercept)."""
    A = [[Fraction(x) for x in r] + [Fraction(1)] for r in rows]
    r = 0
    ncol = len(A[0])
    for c in range(ncol):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
    return r


def lstsq(rows, ys):
    """Exact least squares via normal equations over Fractions."""
    X = [[Fraction(x) for x in r] + [Fraction(1)] for r in rows]
    y = [Fraction(v) for v in ys]
    n = len(X[0])
    A = [[sum(X[k][i] * X[k][j] for k in range(len(X))) for j in range(n)]
         + [sum(X[k][i] * y[k] for k in range(len(X)))] for i in range(n)]
    # gaussian elimination
    for c in range(n):
        p = next((i for i in range(c, n) if A[i][c] != 0), None)
        if p is None:
            return None
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for i in range(n):
            if i != c and A[i][c] != 0:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[c])]
    return [A[i][n] for i in range(n)]


def measure_all(only=None):
    os.makedirs(SCRATCH, exist_ok=True)
    stems = sorted(os.path.basename(p)[:-4]
                   for p in glob.glob(os.path.join(IN, "sweep-*.bin")))
    stems += ["small", "large"]
    rec = json.load(open(OUT)) if os.path.exists(OUT) else {}
    if only:
        stems = [s for s in stems if band_of(s) in only]
    for s in stems:
        path = os.path.join(IN, s + ".bin")
        reg, ncalls = regressors(path)
        row = {"band": band_of(s), "n_calls": ncalls,
               "reg": {k: [reg[k].numerator, reg[k].denominator] for k in REG},
               "ir": {}}
        for cell in CELLS:
            b = os.path.join(BUILD, f"{cell}-O3-isolated")
            cg = measure.callgrind_ir(b, path, SCRATCH, f"{cell}-{s}")
            k = cg.get("kernel_exclusive_ir")
            row["ir"][cell] = None if k is None else k / ncalls
        rec[s] = row
        print(f"{s:16s} {row['band']} calls={ncalls:5d} "
              + " ".join(f"{k}={float(reg[k]):.2f}" for k in REG)
              + "  " + " ".join(f"{c}={row['ir'][c]}" for c in ("safe_tuned",
                                                               "unsafe")))
    with open(OUT, "w") as fh:
        json.dump(rec, fh, indent=1)
    return rec


def fit(rec, cells=CELLS, bands=("N", "D", "F", "E"), label=""):
    stems = [s for s, r in rec.items() if r["band"] in bands]
    rows = [[Fraction(*rec[s]["reg"][k]) for k in REG] for s in stems]
    print(f"\n--- fit over {len(stems)} blob(s), bands {bands} {label}")
    print(f"    design rank {rank(rows)}/5")
    for cell in cells:
        ys = [rec[s]["ir"][cell] for s in stems]
        if any(v is None for v in ys):
            print(f"    {cell:12s} -- missing rows, skipped")
            continue
        co = lstsq(rows, ys)
        if co is None:
            print(f"    {cell:12s} -- singular normal equations (RANK "
                  f"DEFICIENT: the fit is not identified)")
            continue
        res = max(abs(float(sum(c * x for c, x in zip(co, r + [Fraction(1)]))
                            - Fraction(y).limit_denominator(10 ** 9)))
                  for r, y in zip(rows, ys))
        terms = " + ".join(f"{float(c):.5f}*{k}" for c, k in zip(co, REG))
        print(f"    {cell:12s} = {terms} + {float(co[4]):.5f}"
              f"      max|resid| {res:.4f}")
    return stems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", action="store_true", help="re-fit from kir.json")
    ap.add_argument("--only", default=None, help="comma-separated bands N,D,F,E,matrix")
    a = ap.parse_args()
    rec = json.load(open(OUT)) if a.fit else measure_all(
        a.only.split(",") if a.only else None)
    if a.only:
        return 0
    for b in ("N", "D", "F", "E"):
        rows = [[Fraction(*r["reg"][k]) for k in REG]
                for r in rec.values() if r["band"] == b]
        print(f"band {b}: {len(rows)} blob(s), rank {rank(rows)}/5")
    for pair in (("N", "D"), ("N", "F"), ("N", "E"), ("D", "F"), ("D", "E"),
                 ("F", "E")):
        rows = [[Fraction(*r["reg"][k]) for k in REG]
                for r in rec.values() if r["band"] in pair]
        print(f"bands {pair}: rank {rank(rows)}/5")
    fit(rec, bands=("N", "D", "F", "E"), label="(pooled, all four)")
    fit(rec, bands=("N", "D", "E"), label="(no band F -- the R1 rungs' domain)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
