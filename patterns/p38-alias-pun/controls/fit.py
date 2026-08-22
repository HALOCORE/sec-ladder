#!/usr/bin/env python3
"""p38's swept laws, fitted on two bands and tested OUT OF SAMPLE on a third.

⚠ **INLINE MODE AND `Ir` CONVENTION, named once here because every figure this
file prints inherits them** (`.memory/03-measurement.md`): every cell in `PAIRS`
is an **`-O3 isolated`** binary and every number is a **whole-program marginal**
`Ir` per call -- the `n_iters` difference, not the callgrind kernel-exclusive
column `results/*.json` carries. A law fitted in one inline mode is not the law
in the other (p10), so the mode is part of the statement.

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

⚠ **A THIRD structural parameter exists and neither shipped band varies it:
`nw`, the decoded window length in words** -- 240 in band `r`, 244 in band `w`,
256 in band `x`. `--law` is the mode that handles it. `R1h - R1` and `R3 - R4`
are exactly independent of `nw` and the two-regressor fit is the law for them;
`R2 - R4` is not, and the default `--pairs` fit of `r2_r4` is **MISSPECIFIED --
its three coefficients are artefacts and none of them is a p38 result**
(TASK_066_REVIEW M1). `--law` states the repaired five-column law with ZERO
free parameters and prints its residuals.

    python3 patterns/p38-alias-pun/controls/fit.py
    python3 patterns/p38-alias-pun/controls/fit.py --pairs r1h_r1 r3_r4
    python3 patterns/p38-alias-pun/controls/fit.py --law            # R2-R4, repaired
    python3 patterns/p38-alias-pun/controls/fit.py --law --nwsweep --grid
"""

import argparse
import json
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
    m = re.match(r"law-n(\d+)u(\d+)w(\d+)\.bin$", name)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


SCRATCH_W = 256          # must equal SLB_P38_SCRATCH_W and inputs/gen.py's


def nw_of(path):
    """`nw`, the decoded window length in WORDS, read out of the blob itself.

    The blob's payload begins with a u64 `stride`; the kernel decodes
    `min((stride - 4) // 2, SCRATCH_W)` words. Read rather than tabulated so a
    band added to `inputs/gen.py` cannot silently get the wrong `nw` here."""
    with open(path, "rb") as fh:
        stride = struct.unpack("<Q", fh.read(24)[16:24])[0]
    return min(max(stride - 4, 0) // 2, SCRATCH_W)


def law_r2_r4(nrec, rlen, nw):
    """The REPAIRED law for `R2 - R4`, whole-program marginal `Ir`/call,
    `-O3 isolated`, gcc/rustc as shipped. **Zero free parameters.**

        R2 - R4 = A(nw mod 8) - 8*nrec + 6.5*nrec*rlen
                              - 10.5*nrec*(rlen mod 2) + 6*nrec*[rlen == 1]
        A(0) = 79 ;  A(m) = 33 + 6m   for m = 1..7

    THREE columns the shipped band design cannot see, and NONE of them is a
    linear `nw` term (TASK_066_REVIEW M1, which refuted the `nw` attribution
    published at TASK_066: `R2 - R4` is EXACTLY CONSTANT in `nw` at fixed
    residue):

      * `A(nw mod 8)` -- a step in the RESIDUE of `nw`, worth up to 22 Ir/call.
        Bands `r` (240) and `x` (256) are both `0 mod 8`; band `w` sits
        entirely at 244, `4 mod 8`, a flat -22 against them. Measured over
        `nw` = 238..256 at `--nwsweep`, exact at all 19.
      * `nrec * (rlen mod 2)` -- a genuine `nrec x rlen` interaction through
        the PARITY of `rlen`; an odd record costs 10.5 LESS. Band `r` fixes
        `rlen = 4`, so the shipped design is blind to it.
      * `nrec * [rlen == 1]` -- the boundary term, +6 per record, and it is
        what the TASK_066 write-up disclosed as the unexplained `sweep-w01`
        exception. It is NOT an anomaly: at `rlen = 1` the residual against
        the parity law alone is EXACTLY `6*nrec` at every `nrec` 1..7
        (`--grid`) and EXACTLY `12` at `nrec = 2` for every one of the eight
        `nw` residues 240..247, so it is additive against `A()` rather than
        interacting with it.

    The mechanism behind any of the three is NOT established -- `--nwsweep`
    and `--grid` measure the shapes; nobody has read the vector epilogue."""
    m = nw % 8
    a = 79.0 if m == 0 else 33.0 + 6.0 * m
    return (a - 8.0 * nrec + 6.5 * nrec * rlen - 10.5 * nrec * (rlen % 2)
            + 6.0 * nrec * (rlen == 1))


def law_r3_r4(nrec, rlen, nw):
    """`R3 - R4`, p38's fixed-R4 safety bound, with the SAME boundary term.

        R3 - R4 = 17 + 1.00*nrec + 1.00*nrec*[rlen == 1]      (independent of nw)

    TASK_066 published `17 + 1.00*nrec` with `sweep-w01` disclosed as a lone
    exception measuring 21 against a predicted 19, explained as *"at that size
    the reslice's setup has nothing to amortise over"*. That explanation is
    WITHDRAWN: the exception is `+1.00*nrec`, exact at `nrec` = 1..7 on the
    `rlen = 1` column of `--grid` and exactly 0.00 on the `rlen = 2` column
    beside it. p38's two laws therefore share one boundary, at the record
    whose payload fold runs `2*rlen = 2` iterations, and NEITHER of them has
    an unexplained residual left."""
    return 17.0 + 1.0 * nrec + 1.0 * nrec * (rlen == 1)


LAWS = {"r2_r4": law_r2_r4, "r3_r4": law_r3_r4}


def blob_path(blob):
    """A shipped `inputs/` blob by name, or a generated one by path."""
    return blob if os.sep in blob else os.path.join(INPUTS, blob)


def probe(blob, n):
    src = blob_path(blob)
    b = open(src, "rb").read()
    os.makedirs(OUT, exist_ok=True)
    o = os.path.join(OUT, f"probe-{n}-{os.path.basename(src)}")
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


# ------------------------------------------------------- the repaired law ----
def gen_law_blob(nrec, rlen, nw, nwin=6):
    """One `law-*.bin` at an EXACT `(nrec, rlen, nw)`, built with
    `inputs/gen.py`'s own record writer so no second wire format exists.

    `nw` is set through the stride, which is what the kernel derives it from.
    Written under `--out` and re-derivable; the generator is the evidence."""
    sys.path.insert(0, INPUTS)
    import gen as geninp                                    # noqa: E402
    stride = 4 + 2 * nw
    if 4 + nrec * (4 + 4 * rlen) > stride:
        return None                    # would not fit; caller skips the cell
    blob = b"".join(geninp.uniform(nrec, rlen, stride, seed0=5 * w)
                    for w in range(nwin))
    if geninp.sim(blob, 0, stride)[0] == 0:
        return None                    # absorbing window 0 -- not measurable
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"law-n{nrec:02d}u{rlen:02d}w{nw:03d}.bin")
    geninp.emit(p, 2000, blob, stride)
    return p


def law_rows(hi_p, lo_p, blobs, law):
    """[(label, nrec, rlen, nw, measured, predicted, residual)]."""
    out = []
    for b in blobs:
        nrec, rlen = shape(os.path.basename(b))
        nw = nw_of(blob_path(b))
        d = marginal(hi_p, b) - marginal(lo_p, b)
        p = law(nrec, rlen, nw)
        out.append((os.path.basename(b), nrec, rlen, nw, d, p, d - p))
    return out


def print_law_rows(title, rows, note=""):
    print(f"\n  -- {title} ({len(rows)} rows){note}")
    print(f"    {'blob':22s} {'nrec':>4s} {'rlen':>4s} {'nw':>4s} {'nw%8':>4s} "
          f"{'measured':>9s} {'law':>9s} {'resid':>8s}")
    worst = 0.0
    for name, nrec, rlen, nw, d, p, r in rows:
        worst = max(worst, abs(r))
        print(f"    {name:22s} {nrec:4d} {rlen:4d} {nw:4d} {nw % 8:4d} "
              f"{d:9.2f} {p:9.2f} {r:8.2f}")
    print(f"    max abs residual {worst:.5f}")
    return worst


LAW_TEXT = {
    "r2_r4": ["R2-R4 = A(nw mod 8) - 8*nrec + 6.5*nrec*rlen "
              "- 10.5*nrec*(rlen mod 2) + 6*nrec*[rlen==1]",
              "        A(0) = 79 ;  A(m) = 33 + 6m  for m = 1..7"],
    "r3_r4": ["R3-R4 = 17 + 1.00*nrec + 1.00*nrec*[rlen==1]   "
              "(no nw column: exactly independent of nw)"],
}


def do_law(pair, want_nwsweep, want_grid):
    """One pair against its law, with ZERO free parameters."""
    law = LAWS[pair]
    hi_p = os.path.join(BUILD, PAIRS[pair][0])
    lo_p = os.path.join(BUILD, PAIRS[pair][1])
    if not (os.path.exists(hi_p) and os.path.exists(lo_p)):
        print("--law: build the matrix first (harness/build.py p38)")
        return
    print(f"\n=== {pair} vs its LAW (zero free parameters) ===")
    for line in LAW_TEXT[pair]:
        print("    " + line)
    print("    whole-program marginal Ir/call, -O3 isolated")

    ship = sorted(f for f in os.listdir(INPUTS)
                  if f.startswith("sweep-") and shape(f))
    print_law_rows("shipped bands r + w (nw 240 and 244)",
                   law_rows(hi_p, lo_p,
                            [b for b in ship if not b.startswith("sweep-x")],
                            law))
    print_law_rows("shipped band x -- OUT OF SAMPLE (nw 256)",
                   law_rows(hi_p, lo_p,
                            [b for b in ship if b.startswith("sweep-x")], law))

    if want_nwsweep:
        bs = [p for p in (gen_law_blob(2, 4, nw) for nw in range(238, 257))
              if p]
        print_law_rows("nw sweep at (nrec, rlen) = (2, 4) -- identifies A()",
                       law_rows(hi_p, lo_p, bs, law))
        bs = [p for p in (gen_law_blob(2, 1, nw) for nw in range(240, 248))
              if p]
        print_law_rows("nw sweep at (nrec, rlen) = (2, 1) -- is the rlen==1 "
                       "term ADDITIVE against A()?",
                       law_rows(hi_p, lo_p, bs, law))
    if want_grid:
        bs = [p for p in (gen_law_blob(n, r, 256)
                          for n in range(1, 8) for r in range(1, 8)) if p]
        print_law_rows("(nrec x rlen) grid at nw = 256 -- identifies the "
                       "parity and rlen==1 terms",
                       law_rows(hi_p, lo_p, bs, law))

    # The two MATRIX blobs, whose kernel-exclusive figures NOTES.md 4a quotes.
    print("\n  -- the two measured matrix blobs, kernel-exclusive Ir/call "
          "(results/p38-alias-pun.json), a DIFFERENT convention from the rows "
          "above")
    try:
        rec = json.load(open(os.path.join(REPO, "results",
                                          "p38-alias-pun.json")))
    except OSError:
        print("    (no results record yet)")
        return
    calls = {n: int(re.search(r"calls=(\d+)", v["model"]).group(1))
             for n, v in rec["inputs"].items() if "calls=" in v.get("model", "")}
    hi_cell, lo_cell = (PAIRS[pair][0].split("-O3")[0],
                        PAIRS[pair][1].split("-O3")[0])
    ke = {}
    for c in rec.get("cells", []):
        if c.get("opt") == "O3" and c.get("mode") == "isolated":
            for name, v in (c.get("ir") or {}).items():
                if v and v.get("kernel_exclusive_ir") is not None:
                    ke[(c["cell"], name)] = v["kernel_exclusive_ir"] / calls[name]
    for name, (nrec, rlen) in (("small.bin", (4, 11)), ("large.bin", (8, 15))):
        nw = nw_of(os.path.join(INPUTS, name))
        d = ke[(hi_cell, name)] - ke[(lo_cell, name)]
        pr = law(nrec, rlen, nw)
        print(f"    {name:22s} nrec={nrec:2d} rlen={rlen:2d} nw={nw:3d} "
              f"(nw%8={nw % 8}) measured {d:8.2f}  law {pr:8.2f}  "
              f"resid {d - pr:6.2f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pairs", nargs="*", default=list(PAIRS))
    ap.add_argument("--law", nargs="*", default=None, choices=list(LAWS),
                    help="evaluate the zero-parameter laws (default: both)")
    ap.add_argument("--nwsweep", action="store_true",
                    help="with --law: generate and measure the nw sweep")
    ap.add_argument("--grid", action="store_true",
                    help="with --law: generate and measure the (nrec x rlen) grid")
    ap.add_argument("--out", default=OUT,
                    help="scratch dir (must be under .temp/)")
    a = ap.parse_args()
    globals()["OUT"] = os.path.abspath(a.out)
    assert OUT.startswith(os.path.join(REPO, ".temp") + os.sep), OUT

    if a.law is not None:
        for pair in (a.law or list(LAWS)):
            do_law(pair, a.nwsweep, a.grid)
        if a.pairs == list(PAIRS):
            return 0

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
        print("    whole-program marginal Ir/call, -O3 isolated")
        if pair == "r2_r4":
            print("    ⚠ MISSPECIFIED: this two-regressor form has no column "
                  "for nw mod 8 or for")
            print("      rlen parity, so its coefficients are ARTEFACTS and "
                  "none of them is a p38")
            print("      result. It is kept only to show the failure that "
                  "found them. Use --law.")
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
