#!/usr/bin/env python3
"""p10's fitter: exact-rational least squares over the sweep bands, with the
rank diagnostics `.memory/03-measurement.md` requires.

    python3 patterns/p10-fir-stencil/controls/fit.py \
        --json .temp/p10/sweep_r.json,.temp/p10/sweep_o.json \
        --pair safe_naive,unsafe

What it prints, in the order the project's rules ask for them:

  1. the DESIGN's rank, and **the rank after dropping each band**. A residual of
     exactly zero is the signature of a test that could not fail, and the test
     is the RANK AFTER THE DROP, not the column count (`.memory/03-measurement.md`:
     p13's band T was a hold-out that was provably incapable of failing).
  2. the exact-rational coefficients, and the max |residual| in sample.
  3. the residuals on any bands named with `--holdout`.

The regressors are recomputed here from the BLOBS (through `sweep_ir.shape`),
not read out of the JSON, so a fit is reproducible from `inputs/gen.py` plus the
`Ir` column alone.

REGRESSORS -- and the two that were WRONG first are named, because that is the
useful part:

    nout       outputs the call emits (differenced mean over the marginal's own
               call range)
    scaltap    (taps mod 8) * nout -- SCALAR-EPILOGUE taps
    vecit      floor(taps/8) * nout -- VECTOR iterations
    novecout   nout on calls where floor(taps/8) == 0, i.e. where the vector
               loop is never entered at all

  * `taps` is NOT a regressor. p10's tap loop VECTORISES at -O3 in every
    spelling including the naive indexed one, so a per-tap law is a fit of the
    wrong model: the tap count enters only through `taps mod 8` and
    `floor(taps/8)`, which have different coefficients.
  * `novec` (a per-CALL indicator) is not the regressor either; `novecout` (a
    per-OUTPUT one) is. The vector setup and the horizontal reduce are skipped
    once per OUTPUT, not once per call. `novec` fits band `r` exactly -- every
    no-vector window there has the same `nout` -- and misses band `h` by up to
    15.6 Ir. That correction was made because band `h` refused the model, and
    it is the reason band `h` exists.

THE DOMAIN COLUMNS -- `--cols` `1,nout,scaltap,novecout,rejwin,rejfar,fence`,
added at TASK_059 from TASK_057_REVIEW's M4. Bands `r`/`o`/`h`/`e` accept every
window they visit, so the four columns above were fitted where the three below
are identically zero, and `.memory/03-measurement.md` says to test whether a
domain is a missing column rather than to write it as a caveat:

    rejwin   calls the window guard `n < taps` rejected
    rejfar   calls the safety line rejected with `last > len`
    fence    calls with `last == len` -- p10's BUG. The six guarded cells
             reject; R1 accepts and runs the whole tap loop. Drop these rows
             from any c-gcc/c-clang pair (`--exclude`), and note that the
             fitted `fence` and `rejfar` coefficients coincide on every Rust
             pair, which is the check that the two really are the same
             rejection in the six cells that make it.

    python3 controls/fit.py --json .temp/p10/sweep_r.json,.temp/p10/sweep_o.json,\\
        .temp/p10/sweep_d.json --pair safe_tuned,unsafe --cols \\
        1,nout,scaltap,novecout,rejwin,rejfar,fence
"""
import argparse
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import sweep_ir  # noqa: E402

INPUTS = os.path.join(PDIR, "inputs")
DEFAULT_COLS = ["1", "nout", "scaltap", "novecout"]
# The DOMAIN design (../NOTES.md 8b2). The four columns above are exact only
# where every visited window is accepted; these three say what a REJECTED call
# costs and which guard rejected it. `fence` must be dropped from any pair
# involving c-gcc/c-clang -- there R1 accepts and R1h does not, which is p10's
# bug and not a cost row (`.memory/02-bench-rules.md` rule 1).
DOMAIN_COLS = DEFAULT_COLS + ["rejwin", "rejfar", "fence"]


def load_rows(paths, n1=None, n2=None, width=8):
    rows = []
    for p in paths:
        d = json.load(open(p))
        a1 = d["n1"] if n1 is None else n1
        a2 = d["n2"] if n2 is None else n2
        # A sweep JSON written after TASK_059 records the directory it measured;
        # older ones predate the domain band and always mean inputs/.
        indir = os.path.join(REPO, d["inputs"]) if "inputs" in d else INPUTS
        for r in d["rows"]:
            sh = sweep_ir.shape(os.path.join(indir, r["blob"]), a1, a2, width)
            # Band letter: `sweep-r01.bin` -> 'r', `d-allfar.bin` -> 'd'.
            band = r["blob"][6] if r["blob"].startswith("sweep-") else r["blob"][0]
            rows.append({"blob": r["blob"], "band": band,
                         "ir": r["ir"], **sh})
    return rows


def design(rows, cols):
    return [[F(1) if c == "1" else F(str(r[c])) for c in cols] for r in rows]


def rank(m):
    m = [row[:] for row in m]
    nr, nc, rk = len(m), len(m[0]) if m else 0, 0
    for c in range(nc):
        piv = next((i for i in range(rk, nr) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[rk], m[piv] = m[piv], m[rk]
        pv = m[rk][c]
        m[rk] = [x / pv for x in m[rk]]
        for i in range(nr):
            if i != rk and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[rk])]
        rk += 1
    return rk


def solve(A, y):
    """Exact-rational normal equations. Returns None if singular."""
    n = len(A[0])
    M = [[sum(A[k][i] * A[k][j] for k in range(len(A))) for j in range(n)]
         + [sum(A[k][i] * y[k] for k in range(len(A)))] for i in range(n)]
    for c in range(n):
        piv = next((i for i in range(c, n) if M[i][c] != 0), None)
        if piv is None:
            return None
        M[c], M[piv] = M[piv], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for i in range(n):
            if i != c and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[c])]
    return [M[i][n] for i in range(n)]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", required=True, help="comma-separated sweep JSONs")
    ap.add_argument("--pair", required=True,
                    help="cellA,cellB -- the fit is on Ir(A) - Ir(B); give one "
                         "cell to fit its LEVEL instead")
    ap.add_argument("--cols", default=",".join(DEFAULT_COLS))
    ap.add_argument("--holdout", default="", help="comma-separated sweep JSONs "
                                                  "NOT in the fit, predicted")
    ap.add_argument("--width", type=int, default=8,
                    help="the VECTOR WIDTH the `vecit`/`scaltap`/`novecout` "
                         "columns are computed at. 8 is LLVM's on this kernel "
                         "(17-instruction SSE2 body, 8 samples per iteration, "
                         "read off the listing). gcc's is NOT 8 and its level "
                         "law does not fit at width 8 -- max |resid| 387.8 -- "
                         "which is a fact about the compiler and not about the "
                         "kernel. The width is a MEASUREMENT from the "
                         "disassembly, not a fitted parameter.")
    ap.add_argument("--exclude", default="",
                    help="comma-separated substrings; any blob whose name "
                         "contains one is dropped from BOTH the fit and the "
                         "hold-out. Used to drop the `fence` blobs from a "
                         "c-gcc/c-clang pair, where R1 accepts the call and "
                         "R1h refuses it -- a behaviour difference, not a cost "
                         "row (`.memory/02-bench-rules.md` rule 1).")
    ap.add_argument("--out")
    a = ap.parse_args()
    cols = a.cols.split(",")
    cells = a.pair.split(",")
    rows = load_rows(a.json.split(","), width=a.width)
    hold = load_rows(a.holdout.split(","), width=a.width) if a.holdout else []
    if a.exclude:
        pats = a.exclude.split(",")
        drop = [r["blob"] for r in rows + hold
                if any(p in r["blob"] for p in pats)]
        rows = [r for r in rows if not any(p in r["blob"] for p in pats)]
        hold = [r for r in hold if not any(p in r["blob"] for p in pats)]
        print(f"  excluded {len(drop)} row(s): {', '.join(sorted(set(drop)))}")
    rows = [r for r in rows if r["ir"].get(cells[0]) is not None
            and (len(cells) < 2 or r["ir"].get(cells[1]) is not None)]
    hold = [r for r in hold if r["ir"].get(cells[0]) is not None
            and (len(cells) < 2 or r["ir"].get(cells[1]) is not None)]

    def target(r):
        v = r["ir"][cells[0]]
        if len(cells) > 1:
            v -= r["ir"][cells[1]]
        return F(str(round(v, 6)))

    A, y = design(rows, cols), [target(r) for r in rows]
    print(f"fit  {a.pair}  cols={cols}  rows={len(rows)}  width={a.width}")
    print(f"  design rank {rank(A)} of {len(cols)} column(s)")
    bands = sorted({r["band"] for r in rows})
    for b in bands:
        keep = [i for i, r in enumerate(rows) if r["band"] != b]
        if keep:
            print(f"  rank after dropping band '{b}' "
                  f"({len(rows) - len(keep)} row(s)): "
                  f"{rank([A[i] for i in keep])}")
    beta = solve(A, y)
    if beta is None:
        print("  SINGULAR -- the fit set does not determine these columns")
        return 1
    print("  coefficients:")
    for c, b in zip(cols, beta):
        print(f"    {c:10s} {float(b):+14.6f}   ({b})")
    worst = 0.0
    for r, Ar, yr in zip(rows, A, y):
        pred = sum(bi * ai for bi, ai in zip(beta, Ar))
        res = float(yr - pred)
        worst = max(worst, abs(res))
        print(f"    in   {r['blob']:20s} measured {float(yr):12.4f} "
              f"pred {float(pred):12.4f} resid {res:+9.4f}")
    print(f"  max |resid| IN SAMPLE  {worst:.4f}")
    hw = 0.0
    for r in hold:
        Ar = design([r], cols)[0]
        yr = target(r)
        pred = sum(bi * ai for bi, ai in zip(beta, Ar))
        res = float(yr - pred)
        hw = max(hw, abs(res))
        print(f"    OUT  {r['blob']:20s} measured {float(yr):12.4f} "
              f"pred {float(pred):12.4f} resid {res:+9.4f}")
    if hold:
        print(f"  max |resid| OUT OF SAMPLE  {hw:.4f}")
    if a.out:
        json.dump({"pair": cells, "cols": cols,
                   "beta": [str(b) for b in beta],
                   "max_resid_in": worst, "max_resid_out": hw},
                  open(a.out, "w"), indent=1)
        print("wrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
