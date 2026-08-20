#!/usr/bin/env python3
"""p13 control: the swept cost laws, their design RANK, and an out-of-sample test.

`.memory/03-measurement.md`, "A fitted law is a law in SOMEBODY's counts":

  1. state the regressor set PER ROW, not per table;
  2. a self-consistency check a rank-deficient design cannot fail is not a check;
  3. build one out-of-sample blob that turns on EVERY regressor at once and
     predict it BEFORE measuring.

p13's regressors, per kernel call:

    1     the per-call constant
    K     strings walked
    S     source bytes the scan reads (string bytes + the terminators it lands on)
    C     bytes copied, `sum min(slen, DST_CAP)`
    T     strings TRUNCATED, `#{slen >= DST_CAP}`

**`F`, the zero-filled bytes, is NOT an independent regressor**: `strncpy` writes
exactly `DST_CAP` bytes per string, so `C + F == DST_CAP * K` identically. Nor is
`D`, the consumer's bytes: `D == C - T + K`. Both are checked here rather than
asserted -- `--rank` prints the rank of the pooled design **and** of every pair
of bands, and it needs no measurement at all, which is the point: p04 measured
seven laws across 99 blobs before discovering that no pair of its four bands
identified its four regressors.

    python3 patterns/p13-strncpy-trunc/controls/sweep_fit.py --rank   # design only
    python3 patterns/p13-strncpy-trunc/controls/sweep_fit.py          # + measure + fit

Fit on bands **N and L**, predict band **T** out of sample. Band T is the only
place in the pattern where truncating and non-truncating strings are live in the
same call, which is exactly the combination p04's in-sample blobs lacked.

⚠ **R1 (`c-gcc`, `c-clang`) is excluded from every blob with `T > 0`** -- its
consumer reads past `dst[31]` there, and on some builds the value it reads is
not stable across runs of the same binary (../NOTES.md 0b and 7), so an `Ir`
measured on it is not a number.
That exclusion is the price of the bug being an overread; it is stated, not
worked around, and it is the direct analogue of R1's absence from p12's
`sweep-a*`.
"""

import argparse
import json
import os
import re
import struct
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(PDIR, "inputs"))
SCRATCH = os.path.join(REPO, ".temp", "p13", "sweep")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
BUILD = os.path.join(REPO, ".temp", "build", "p13")

DST_CAP = 32
HDR = 4
CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]
R1_CELLS = {"c-gcc", "c-clang"}
LO, HI = 100, 200


# ---------------------------------------------------------------- design ----
def counts(lens):
    """(1, K, S, C, T) for one window holding `lens`, all strings terminated."""
    K = len(lens)
    S = sum(lens) + K                      # every string ends on a terminator
    C = sum(min(l, DST_CAP) for l in lens)
    T = sum(1 for l in lens if l >= DST_CAP)
    return (1, K, S, C, T)


def bands():
    """The three bands, exactly as inputs/gen.py emits them."""
    import gen
    b = {"N": [], "L": [], "T": []}
    for k in gen.SWEEP_N_KS:
        b["N"].append((f"sweep-n{k:02d}L{gen.SWEEP_N_LEN:02d}.bin",
                       [gen.SWEEP_N_LEN] * k))
    for n in gen.SWEEP_L_LENS:
        b["L"].append((f"sweep-l{gen.SWEEP_L_NSTR:02d}L{n:02d}.bin",
                       [n] * gen.SWEEP_L_NSTR))
    for t in gen.SWEEP_T_TS:
        b["T"].append((f"sweep-t{gen.SWEEP_T_NSTR:02d}T{t:02d}.bin",
                       [gen.SWEEP_T_LONG] * t
                       + [gen.SWEEP_T_SHORT] * (gen.SWEEP_T_NSTR - t)))
    return b


def rank(rows):
    """Exact rational rank of a list of integer row vectors."""
    m = [[Fraction(x) for x in r] for r in rows]
    r = 0
    ncol = len(m[0]) if m else 0
    for c in range(ncol):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        pv = m[r][c]
        m[r] = [x / pv for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
    return r


def show_rank():
    b = bands()
    names = ["1", "K", "S", "C", "T"]
    print("regressors:", names)
    print("            F = DST_CAP*K - C and D = C - T + K are DEPENDENT; "
          "checked below.")
    allrows = []
    for k, v in b.items():
        rows = [counts(l) for _, l in v]
        allrows += rows
        # the dependence claims, verified per row
        for (name, lens), row in zip(v, rows):
            K, S, C, T = row[1:]
            F = sum(DST_CAP - min(l, DST_CAP) for l in lens)
            D = sum(min(l, DST_CAP - 1) + 1 for l in lens)
            assert F == DST_CAP * K - C, (name, F, DST_CAP * K - C)
            assert D == C - T + K, (name, D, C - T + K)
        print(f"  band {k}: {len(rows):3d} blobs, rank {rank(rows)}/5")
    print(f"  POOLED : {len(allrows):3d} blobs, rank {rank(allrows)}/5")
    for x in ("N", "L", "T"):
        for y in ("N", "L", "T"):
            if x < y:
                rows = [counts(l) for _, l in b[x]] + [counts(l) for _, l in b[y]]
                print(f"  pair {x}+{y}: rank {rank(rows)}/5")
    fit = [counts(l) for _, l in b["N"]] + [counts(l) for _, l in b["L"]]
    print(f"  FIT SET (N+L): rank {rank(fit)}/5  <- must be 5 or the fit is "
          f"not identified")
    # R1's own view: it never sees a T>0 blob
    r1 = [counts(l) for _, l in b["N"]] + \
         [counts(l) for _, l in b["L"] if counts(l)[4] == 0]
    print(f"  FIT SET as R1 SEES IT (T == 0 only): rank {rank(r1)}/5  "
          f"<- T is unidentifiable for R1 by construction")
    return b


# ------------------------------------------------------------- measurement --
def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def probe(src, n_iters, out):
    blob = open(src, "rb").read()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n_iters) + blob[8:])
    return out


def cg_ir(binary, arg, tag):
    out = os.path.join(SCRATCH, f"cg.{tag}.out")
    rc, o, e = sh([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + out,
                   "-q", binary, arg])
    if rc != 0:
        raise SystemExit(f"callgrind rc={rc} on {binary} {arg}: {e[:300]}")
    tot = None
    with open(out) as f:
        for ln in f:
            if ln.startswith(("summary:", "totals:")):
                tot = int(ln.split()[1])
    os.remove(out)
    return tot


def measure(b, cells, opt="O3", mode="isolated"):
    os.makedirs(SCRATCH, exist_ok=True)
    indir = os.path.join(PDIR, "inputs")
    data = {}
    for band, entries in b.items():
        for name, lens in entries:
            c = counts(lens)
            lo = probe(os.path.join(indir, name), LO,
                       os.path.join(SCRATCH, f"p.{name}.{LO}.bin"))
            hi = probe(os.path.join(indir, name), HI,
                       os.path.join(SCRATCH, f"p.{name}.{HI}.bin"))
            for cell in cells:
                if cell in R1_CELLS and c[4] > 0:
                    continue          # R1 reads OOB here; see the docstring
                binary = os.path.join(BUILD, f"{cell}-{opt}-{mode}")
                if not os.path.exists(binary):
                    raise SystemExit(f"missing build {binary} -- run "
                                     f"harness/build.py p13")
                a = cg_ir(binary, lo, f"{cell}.{name}.lo")
                z = cg_ir(binary, hi, f"{cell}.{name}.hi")
                data.setdefault(cell, {})[name] = {
                    "band": band, "counts": c, "ir": (z - a) / float(HI - LO)}
            os.remove(lo)
            os.remove(hi)
        print(f"  band {band} done")
    return data


# -------------------------------------------------------------- exact fit ---
def solve(rows, ys):
    """Exact least-norm solve of an over-determined EXACT system.

    Every row here is an integer count vector and every `y` an Ir marginal that
    is a dyadic rational, so if a linear law holds it holds EXACTLY. Pick 5
    independent rows, solve, then check the residual on ALL rows. If any
    residual is non-zero the law is reported as approximate with its worst
    residual -- never silently least-squares'd."""
    idx, basis = [], []
    for i, r in enumerate(rows):
        if rank(basis + [r]) > len(basis):
            basis.append(list(r))
            idx.append(i)
        if len(basis) == 5:
            break
    if len(basis) < 5:
        return None, None, len(basis)
    m = [[Fraction(x) for x in basis[i]] + [Fraction(ys[idx[i]]).limit_denominator(10**6)]
         for i in range(5)]
    n = 5
    for c in range(n):
        piv = next(i for i in range(c, n) if m[i][c] != 0)
        m[c], m[piv] = m[piv], m[c]
        pv = m[c][c]
        m[c] = [x / pv for x in m[c]]
        for i in range(n):
            if i != c and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[c])]
    beta = [m[i][n] for i in range(n)]
    worst = max(abs(sum(Fraction(x) * bb for x, bb in zip(r, beta))
                    - Fraction(y).limit_denominator(10**6))
                for r, y in zip(rows, ys))
    return beta, worst, 5


def fmt(beta):
    names = ["", "*K", "*S", "*C", "*T"]
    parts = []
    for b, n in zip(beta, names):
        if b == 0:
            continue
        parts.append(f"{float(b):+.5g}{n}")
    return " ".join(parts) or "0"


def regimes(data):
    """The honest model: p13's cost is PIECEWISE-LINEAR, not linear.

    The 5-regressor fit above is reported and it does NOT close (worst in-sample
    residual 115...888 Ir depending on the cell). That is the result, not a
    failure of the fitter: `strncpy`'s two halves are compiled to size-dispatched
    vector code, so the per-string cost is a STEP function of the fill length,
    and there is a large discontinuity at `slen == DST_CAP` where the copy
    saturates, the zero-fill disappears entirely and the consumer stops growing.

    What IS exact is the slope inside each regime of band L. Above the
    threshold the copy, the fill and the consumer are all constant per string,
    so the slope is **the source scan alone** -- and that is a matched-spelling
    quantity across the rungs, which is the one thing this project is allowed to
    publish to five decimals.
    """
    import re
    K = 8                                   # band L holds SWEEP_L_NSTR strings
    print("\n" + "=" * 74)
    print("REGIMES on band L (K = 8): the 5-regressor law does not close, but "
          "each\nregime's slope does. Ir per call per unit L, and per SOURCE "
          "BYTE (/K).")
    print("=" * 74)
    rows = {}
    for cell, d in data.items():
        for name, v in d.items():
            if v["band"] != "L":
                continue
            L = int(re.search(r"L(\d+)\.bin", name).group(1))
            rows.setdefault(cell, {})[L] = v["ir"]
    print(f"  {'cell':12s} {'L in 33..48 (SCAN ONLY)':>26s} "
          f"{'L in 2..31':>22s}   step at L=31->32")
    out = {}
    for cell in CELLS:
        if cell not in rows:
            continue
        r = rows[cell]
        hi = sorted(l for l in r if l >= 33)
        lo = sorted(l for l in r if 2 <= l <= 31)
        def slope(ls):
            if len(ls) < 2:
                return None, None
            ds = [Fraction(r[b]).limit_denominator(10**6)
                  - Fraction(r[a]).limit_denominator(10**6)
                  for a, b in zip(ls, ls[1:])]
            m = sum(ds) / len(ds)
            spread = max(ds) - min(ds)
            return m, spread
        mh, sh_ = slope(hi)
        ml, sl_ = slope(lo)
        step = (Fraction(r[32]).limit_denominator(10**6)
                - Fraction(r[31]).limit_denominator(10**6)) if 32 in r and 31 in r else None
        f = lambda m, s: (f"{float(m):+8.3f} (+-{float(s):5.2f}) "
                          f"= {float(m)/K:5.3f}/B" if m is not None else " " * 26)
        print(f"  {cell:12s} {f(mh, sh_):>26s} {f(ml, sl_):>22s}   "
              f"{('%+.2f' % float(step)) if step is not None else '-':>10s}")
        out[cell] = {"scan_slope_per_call": float(mh) if mh is not None else None,
                     "scan_slope_per_source_byte": float(mh) / K if mh is not None else None,
                     "scan_slope_spread": float(sh_) if sh_ is not None else None,
                     "below_slope_per_call": float(ml) if ml is not None else None,
                     "below_slope_spread": float(sl_) if sl_ is not None else None,
                     "cliff_31_to_32": float(step) if step is not None else None}
    print("\n  The 33..48 column is the SOURCE SCAN's per-byte rate with the "
          "copy, the\n  zero-fill and the consumer all saturated -- a matched "
          "spelling across the\n  four Rust rungs (the same indexed byte loop) "
          "and across the two C rungs.")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rank", action="store_true",
                    help="print the design rank and stop -- no measurement")
    ap.add_argument("--cells", default=",".join(CELLS))
    ap.add_argument("--refit", action="store_true",
                    help="re-fit from the accumulated JSON without measuring")
    ap.add_argument("--opt", default="O3")
    ap.add_argument("--mode", default="isolated")
    a = ap.parse_args()

    print("=" * 74)
    print("DESIGN RANK -- computed from inputs/gen.py alone, before any measuring")
    print("=" * 74)
    b = show_rank()
    if a.rank:
        return 0

    print("\n" + "=" * 74)
    print(f"MEASURING  Ir marginal per call, {a.opt} {a.mode}, "
          f"n_iters {LO} -> {HI}")
    print("=" * 74)
    cells = a.cells.split(",")
    data = measure(b, cells, a.opt, a.mode) if not a.refit else {}

    # MERGE rather than overwrite: the Bash tool this project is driven through
    # caps a foreground command at 10 minutes, and the full 8-cell sweep is
    # longer than that. `--cells` splits it; the accumulated JSON is the record,
    # and every run re-fits from everything measured so far.
    out = os.path.join(SCRATCH, f"sweep_ir.{a.opt}.{a.mode}.json")
    if os.path.exists(out):
        with open(out) as f:
            prev = json.load(f)
        prev.update(data)
        data = prev
    with open(out, "w") as f:
        json.dump(data, f, indent=1)
    print(f"wrote {out} ({len(data)} cell(s) accumulated)")
    cells = [c for c in CELLS if c in data]

    print("\n" + "=" * 74)
    print("FIT on bands N+L (exact rational), PREDICT band T out of sample")
    print("=" * 74)
    print(f"  {'cell':12s} {'law (Ir per call)':52s} {'in-sample':>10s} "
          f"{'band T':>10s}")
    summary = {}
    for cell in cells:
        d = data.get(cell, {})
        fit_rows = [(v["counts"], v["ir"]) for v in d.values()
                    if v["band"] in ("N", "L")]
        if not fit_rows:
            continue
        beta, worst, r = solve([r for r, _ in fit_rows], [y for _, y in fit_rows])
        if beta is None:
            print(f"  {cell:12s} design rank {r}/5 -- NOT IDENTIFIED")
            continue
        oos = [(v["counts"], v["ir"]) for v in d.values() if v["band"] == "T"]
        oworst = max((abs(sum(Fraction(x) * bb for x, bb in zip(rr, beta))
                          - Fraction(y).limit_denominator(10**6))
                      for rr, y in oos), default=None)
        print(f"  {cell:12s} {fmt(beta):52s} {float(worst):10.4f} "
              f"{(float(oworst) if oworst is not None else float('nan')):10.4f}")
        summary[cell] = {"beta": [str(x) for x in beta],
                         "in_sample_worst_residual": float(worst),
                         "band_T_worst_residual":
                             float(oworst) if oworst is not None else None,
                         "n_fit": len(fit_rows), "n_oos": len(oos)}
    reg = regimes(data)
    sout = os.path.join(SCRATCH, f"sweep_fit.{a.opt}.{a.mode}.json")
    with open(sout, "w") as f:
        json.dump({"global_linear_fit": summary, "regimes": reg}, f, indent=1)
    print(f"\nwrote {sout}")
    print("\n  A non-zero `band T` residual means the law is a law in the FIT "
          "SET's\n  counts and not in the kernel's -- which is exactly what "
          "p04's two wrong\n  rows were, and no in-sample blob could have shown "
          "it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
