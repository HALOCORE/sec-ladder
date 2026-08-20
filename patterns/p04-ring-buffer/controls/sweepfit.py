#!/usr/bin/env python3
"""p04's swept laws: kernel-exclusive Ir per call against the four regressors.

    xpush  a push the fullness guard accepts
    dpush  a push the fullness guard REJECTS  (only band F has any)
    xpop   a pop the emptiness guard accepts
    epop   a pop that finds the ring empty    (only band E has any)

Counts are **visit-weighted over the calls the driver actually makes**, replayed
from `model.py`'s own driver loop, because the Lemire index does not visit the 8
windows of a sweep blob equally.

    python3 patterns/p04-ring-buffer/inputs/gen.py --sweep   # the 102 blobs
    python3 harness/build.py p04 --all                      # the cells
    python3 patterns/p04-ring-buffer/controls/sweepfit.py   # measure + fit
    python3 .../sweepfit.py --only N          # one band at a time (each < 5 min)
    python3 .../sweepfit.py --fit             # re-fit from the cached kir.json

⚠ **Band X is measured and NEVER fitted** (TASK_044, from TASK_042_REVIEW
MAJOR 2). Bands N/D/F/E are built to ISOLATE regressors, and that is what made
them blind: `inputs/gen.py::walk` asserts `dpush == 0 and epop == 0`, band F
fills the ring but never drains it and band E drains it but never fills it, so
no blob among the 99 -- and neither matrix input -- has `dpush` and `epop` both
non-zero. On band X they are, and the two R1 rows MISS, because they are laws
of R1's OWN execution counts and not of `model.py`'s. `predict()` prints both
count vectors side by side; `r1_counts()` is the replay that produces the
second one. See ../NOTES.md 4c.

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
    if stem.startswith("sweep-x"):
        return "X"
    return "matrix"


def r1_counts(m, off):
    """R1's OWN execution counts for the window at `off` -- the rung with no
    fullness test.

    This is deliberately NOT `model.py::op_counts`, and the duplication is the
    point (TASK_042_REVIEW MAJOR 2). `op_counts` counts what the *model's*
    program does; a push the model REJECTS, R1 accepts, and from that point the
    two programs' cursors disagree, so the two count vectors are different
    quantities. `model.py` is the reference implementation of the CHECKED
    kernel and must not grow a second program; the R1 replay lives here, beside
    the fit that needs it.

    `dpush` is identically 0: R1 has no fullness guard, so no push is ever
    dropped. That is exactly why R1's law cannot have a `dpush` term."""
    buf, ln = m.buf, m.stride
    c = dict.fromkeys(REG, 0)
    if ln < 4:
        return c
    nops = int.from_bytes(buf[off:off + 4], "little")
    if nops == 0 or 5 * nops > ln - 4:
        return c
    head = tail = 0
    for k in range(nops):
        if buf[off + 4 + 5 * k] == 0:
            tail = (tail + 1) % 64                     # NO FULLNESS TEST
            c["xpush"] += 1
        elif head != tail:
            head = (head + 1) % 64
            c["xpop"] += 1
        else:
            c["epop"] += 1
    return c


def regressors(path, own=False):
    """Mean per-call counts over the calls the driver actually makes.

    `own=True` gives **R1's** counts instead of the model's. On every blob in
    bands N/D/E and on both matrix inputs the two agree; on band F they agree
    only up to the `xpush`/`dpush` split (which is why R1's two fitted
    coefficients came out equal); on band X they do not agree at all."""
    m = M.build(path)
    tot = dict.fromkeys(REG, 0)
    n = 0
    for c in m.iter_calls():
        w = r1_counts(m, c["off"]) if own else m.op_counts(c["off"])
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
        own, _ = regressors(path, own=True)
        row = {"band": band_of(s), "n_calls": ncalls,
               "reg": {k: [reg[k].numerator, reg[k].denominator] for k in REG},
               "r1reg": {k: [own[k].numerator, own[k].denominator] for k in REG},
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
    out = {}
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
        out[cell] = co
    return out


def predict(rec, co, bands=("X",)):
    """Evaluate a fit on blobs it was NOT fitted on, in BOTH count vectors.

    TASK_042_REVIEW MAJOR 2: five of p04's seven rows are laws of the model's
    execution counts and the two R1 rows are laws of R1's OWN counts. The two
    coincide on every blob in bands N/D/F/E and on both matrix inputs, so the
    99-blob fit could not tell them apart. Band X is the blob where they come
    apart, and this is the print that says so."""
    stems = sorted(s for s, r in rec.items() if r["band"] in bands)
    print(f"\n--- HELD-OUT PREDICTION on bands {bands} "
          f"({len(stems)} blob(s), fitted on NONE of them)")
    print("      cell          model-count law   R1-own-count law        measured")
    for s in stems:
        r = rec[s]
        if "r1reg" not in r:      # a kir.json row cached before TASK_044
            own, _ = regressors(os.path.join(IN, s + ".bin"), own=True)
            r["r1reg"] = {k: [own[k].numerator, own[k].denominator] for k in REG}
        xm = [Fraction(*r["reg"][k]) for k in REG] + [Fraction(1)]
        xo = [Fraction(*r["r1reg"][k]) for k in REG] + [Fraction(1)]
        print(f"    {s}  model {' '.join(f'{k}={float(v):g}' for k, v in zip(REG, xm))}"
              f"\n    {' ' * len(s)}  R1's  "
              f"{' '.join(f'{k}={float(v):g}' for k, v in zip(REG, xo))}")
        for cell in CELLS:
            y = r["ir"].get(cell)
            if y is None or cell not in co:
                continue
            pm = sum(c * v for c, v in zip(co[cell], xm))
            po = sum(c * v for c, v in zip(co[cell], xo))
            yq = Fraction(y).limit_denominator(10 ** 9)
            mark = "  <-- MISS" if pm != yq else ""
            omark = " EXACT" if po == yq else ""
            print(f"      {cell:12s} {float(pm):12.2f}  ({float(pm - yq):+8.2f})"
                  f"   {float(po):12.2f}{omark:6s}   {float(yq):10.2f}{mark}")
    return stems


# The two R1 rows, restated in R1's OWN counts. There is no `dpush` term
# because R1 has no fullness guard and therefore never drops a push.
R1_OWN_LAW = {"c-gcc": (18, 14, 7, 48), "c-clang": (9, 15, 9, 31)}


def r1law(rec):
    """Check the two R1 rows in R1's own counts over EVERY measured blob.

    The model-count form of these two rows fits the 99 fitting blobs at zero
    residual and misses on band X; this form misses nowhere. Printing the count
    of blobs on which the two vectors differ is the point -- it is 2 out of 104,
    and both are band X, which is why 99 in-sample blobs could not see it."""
    print("\n--- the two R1 rows in R1's OWN counts, over every measured blob")
    for cell, (a, b, c, e) in R1_OWN_LAW.items():
        print(f"    {cell:9s} = {a}*xpush_R1 + {b}*xpop_R1 + {c}*epop_R1 + {e}")
    n = bad = ndiff = 0
    for s in sorted(rec):
        r = rec[s]
        if "r1reg" not in r:
            own, _ = regressors(os.path.join(IN, s + ".bin"), own=True)
            r["r1reg"] = {k: [own[k].numerator, own[k].denominator] for k in REG}
        o = {k: Fraction(*r["r1reg"][k]) for k in REG}
        m = {k: Fraction(*r["reg"][k]) for k in REG}
        assert o["dpush"] == 0, (s, o)
        if not (o["xpush"] == m["xpush"] + m["dpush"] and o["xpop"] == m["xpop"]
                and o["epop"] == m["epop"]):
            ndiff += 1
            print(f"    {s}: R1's count vector differs from the model's")
        for cell, (a, b, c, e) in R1_OWN_LAW.items():
            y = r["ir"].get(cell)
            if y is None:
                continue
            n += 1
            pred = a * o["xpush"] + b * o["xpop"] + c * o["epop"] + e
            if pred != Fraction(y).limit_denominator(10 ** 9):
                bad += 1
                print(f"    MISS {s:14s} {cell:9s} pred {float(pred):.2f} "
                      f"meas {y}")
    print(f"    checked {n} (blob, cell) rows over {len(rec)} blobs: "
          f"{bad} mismatch(es)")
    print(f"    blobs where R1's count vector differs from the model's "
          f"(beyond the xpush/dpush split): {ndiff}")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", action="store_true", help="re-fit from kir.json")
    ap.add_argument("--only", default=None,
                    help="comma-separated bands N,D,F,E,X,matrix")
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
    co = fit(rec, bands=("N", "D", "F", "E"), label="(pooled, all four)")
    fit(rec, bands=("N", "D", "E"), label="(no band F -- the R1 rungs' domain)")
    # Band X is NEVER fitted -- it is the held-out adversarial blob.
    if any(r["band"] == "X" for r in rec.values()):
        predict(rec, co, bands=("X",))
    r1law(rec)
    return 0


if __name__ == "__main__":
    sys.exit(main())
