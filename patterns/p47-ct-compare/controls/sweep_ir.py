#!/usr/bin/env python3
"""p47's sweep. **`Ir` under callgrind IS the side channel**, so this script is
not a diagnostic for the pattern -- it is the pattern's instrument.

    python3 patterns/p47-ct-compare/inputs/gen.py --sweep
    python3 patterns/p47-ct-compare/controls/sweep_ir.py --measure --out .temp/p47/sweep.json
    python3 patterns/p47-ct-compare/controls/sweep_ir.py --fit .temp/p47/sweep.json
    python3 patterns/p47-ct-compare/controls/sweep_ir.py --leak .temp/p47/sweep.json

MARGINAL, NOT LEVEL. `.memory/03-measurement.md`: `measure.py`'s callgrind
columns are whole-run LEVELS and carry a per-process constant. Every number
here is `(Ir(n2) - Ir(n1)) / (n2 - n1)` over the same binary and the same input,
which differences that constant away exactly -- including the driver's own
`println!` digit-count term, because the two runs print the same checksum.

WHOLE-PROGRAM, NOT KERNEL-EXCLUSIVE, and on p47 that is load-bearing rather
than conventional: **the leaking rungs do their comparing inside glibc's
`bcmp`/`memcmp`**, which is outside every symbol a kernel-exclusive column
matches. A kernel-exclusive law for `c-gcc`, `c-clang` or `safe_naive` would be
a law about the part of the comparison that is not the comparison.
`.memory/03-measurement.md`'s p08 row is the same failure with the sign
reversed.

INTERLEAVED BY CELL, NEVER BY BLOCK, and in the FOREGROUND. Scratch is per-PID.

INLINE MODE IS NAMED AT EVERY FIGURE and is not defaulted silently: `--mode` has
no default value here, because `.memory/03-measurement.md` records that p10's
regressors SWAPPED between modes while both fits stayed rank-full and exact.

THE REGRESSORS, all four derived from the FILE and none from any rung:

  ncmp     comparisons the window guard admits, per call
  cbytes   bytes actually compared per call, `ncmp * tlen` -- what the
           CONSTANT-TIME rungs read
  kbytes   sum over comparisons of `min(k+1, tlen)` for a mismatching
           comparison and `tlen` for an equal one -- what an ideal
           BYTE-GRANULAR early-exit rung would read. **This is the leak
           regressor**, and it is the only one that distinguishes the rungs.
  kblocks  the same sum rounded up to 32-byte blocks -- what glibc's AVX2
           `bcmp` actually reads, measured at 32-byte granularity in NOTES.md 4
  neq      comparisons that are EQUAL, i.e. that force a full scan in every
           rung including the leaking ones
  kblk_mis the 32-byte blocks read by the MISMATCHING comparisons alone

  `neq` and `kblk_mis` are the pair that makes the additivity test possible:
  band k moves `kblk_mis` at `neq == 0` and band m moves `neq` at the minimum
  `kblk_mis`, so the two NEVER co-occur in the fit set. Band x is where they
  do.

  band k   tlen 256, every comparison mismatching, k stepped 0..255.
           `cbytes` is CONSTANT across the whole band and `kbytes` sweeps
           1..1024, so this band alone separates the leak term from everything
           else.
  band m   tlen 256, k = 0, the number of EQUAL comparisons stepped 0..8.
           `kbytes` rises with `nmatch` while `k` never moves.
  band t   the tag-length axis, k = 0, nmatch = 0.
  band g   the comparison-count axis.
  band x   ADDITIVITY EXTRAPOLATION: `k > 0` AND `nmatch > 0` together, which
           no other band contains. Held out of every fit by default.
  band h   length-heterogeneous within a blob.

⚠ A LAW OWES ITS DOMAIN, and p47's is a list of MISSING COLUMNS, not a caveat
(`.memory/03-measurement.md`; p10 went 3 -> 4 -> 6 parameters). `--fit` prints
them every run. The list is NOT claimed closed.
"""
import argparse
import json
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PD))
sys.path.insert(0, os.path.join(REPO, "common"))
import slb  # noqa: E402

INDIR = os.path.join(PD, "inputs")
BUILD = os.path.join(REPO, ".temp", "build", "p47")
HDR = 8
VG = os.path.expanduser("~/tools/valgrind/bin/valgrind")

ALL_CELLS = ["c-gcc", "c-clang", "c-gcc-h", "c-clang-h",
             "safe_naive", "safe_tuned", "unsafe", "verus"]
#: the rungs whose comparison stops early -- the ones a leak term must be
#: non-zero on. Named here so `--leak` cannot silently re-classify a rung.
LEAKY = ["c-gcc", "c-clang", "safe_naive"]

DOMAIN_MISSING = [
    "ALIGNMENT of the tags relative to a 32-byte boundary: every blob puts the "
    "first tag at window byte 8 and the driver places windows at multiples of "
    "`stride`, so the sweep never varies it independently. glibc's bcmp is "
    "alignment-sensitive.",
    "the WIDTH of the mismatching difference: gen.py always flips 4 bits "
    "(`^= 0x5A`) of the byte at k. A single-bit flip cannot change a byte-wise "
    "compare's result, but it is unswept and so is unmeasured.",
    "the DISTRIBUTION of k across the comparisons of one window: every "
    "comparison in a sweep window has the SAME k. A window mixing k values is "
    "band h's shape only, and h moves three parameters at once.",
    "glibc's IFUNC choice: one machine, one libc, one dispatch. The 32-byte "
    "granularity in NOTES.md 4 is this box's `bcmp`, not `bcmp`'s.",
    "the number of DISTINCT windows a blob has (nwin is 4 or 2 throughout the "
    "sweep bands), so cache residency of the tag data is not varied.",
]


def regressors(path):
    """(ncmp, cbytes, kbytes, kblocks, neq, kblk_mis) per call, from the FILE.

    Every window of a sweep blob has the same shape by construction except in
    band h, and the driver's Lemire index visits windows pseudo-randomly, so
    the per-call figure is the MEAN over the blob's windows -- computed exactly
    here rather than sampled."""
    f = slb.read(path)
    stride, buf = slb.head1_u64_bytes(f.payload[: f.declared_len])
    nwin = len(buf) // stride if stride else 0
    tot = [0, 0, 0, 0, 0, 0]
    for w in range(nwin):
        off = w * stride
        if stride < HDR:
            continue
        ntag = int.from_bytes(buf[off:off + 4], "little")
        tlen = int.from_bytes(buf[off + 4:off + 8], "little")
        if ntag == 0 or tlen == 0:
            continue
        p, o = HDR, 0
        while o < ntag and stride - p >= 2 * tlen:
            a = buf[off + p:off + p + tlen]
            b = buf[off + p + tlen:off + p + 2 * tlen]
            k = next((i for i in range(tlen) if a[i] != b[i]), None)
            touched = tlen if k is None else k + 1
            blocks = ((touched + 31) // 32) * 32
            tot[0] += 1
            tot[1] += tlen
            tot[2] += touched
            tot[3] += blocks
            if k is None:
                tot[4] += 1
            else:
                tot[5] += blocks
            p += 2 * tlen
            o += 1
    n = float(nwin) if nwin else 1.0
    return [t / n for t in tot], stride, nwin


def rewrite_iters(src, dst, n_iters):
    b = bytearray(open(src, "rb").read())
    b[0:8] = struct.pack("<Q", n_iters)
    open(dst, "wb").write(bytes(b))


def total_ir(binary, arg, scr, tag):
    o = os.path.join(scr, f"cg.{tag}")
    r = subprocess.run([VG, "--tool=callgrind", f"--callgrind-out-file={o}",
                        binary, arg], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"sweep_ir.py: callgrind exit {r.returncode} on "
                         f"{binary}: {r.stderr[-300:]}")
    for line in open(o):
        if line.startswith("totals:"):
            v = int(line.split()[1])
            os.unlink(o)
            return v
    raise SystemExit("sweep_ir.py: no `totals:` line in the callgrind output")


def marginal(binary, inp, scr, n1, n2):
    out = {}
    for n in (n1, n2):
        p = os.path.join(scr, f"in.{n}.bin")
        rewrite_iters(inp, p, n)
        out[n] = total_ir(binary, p, scr, f"{os.path.basename(binary)}.{n}")
    return (out[n2] - out[n1]) / float(n2 - n1)


def cmd_measure(a):
    scr = os.path.join(REPO, ".temp", "p47", f"sweep{os.getpid()}")
    os.makedirs(scr, exist_ok=True)
    pre = tuple(a.bands.split(",")) if a.bands else ("",)
    blobs = sorted(f for f in os.listdir(INDIR)
                   if f.startswith("sweep-") and f.endswith(".bin")
                   and any(f.startswith("sweep-" + p) for p in pre))
    if not blobs:
        raise SystemExit("sweep_ir.py: no sweep-* blobs; run inputs/gen.py --sweep")
    cells = a.cells.split(",")
    rows = []
    for b in blobs:                      # blob outer, CELL inner: interleaved
        reg, stride, nwin = regressors(os.path.join(INDIR, b))
        rec = {"blob": b, "stride": stride, "nwin": nwin, "ncmp": reg[0],
               "cbytes": reg[1], "kbytes": reg[2], "kblocks": reg[3],
               "neq": reg[4], "kblk_mis": reg[5]}
        for c in cells:
            binary = os.path.join(BUILD, f"{c}-{a.opt}-{a.mode}")
            rec[c] = marginal(binary, os.path.join(INDIR, b), scr, a.n1, a.n2)
        rows.append(rec)
        print(f"  {b:20s} ncmp={reg[0]:5.1f} cby={reg[1]:7.1f} "
              f"kby={reg[2]:7.1f} kblk={reg[3]:7.1f} neq={reg[4]:4.1f} "
              f"kbm={reg[5]:7.1f}  "
              + " ".join(f"{c}={rec[c]:9.3f}" for c in cells), flush=True)
    json.dump({"opt": a.opt, "mode": a.mode, "n1": a.n1, "n2": a.n2,
               "cells": cells, "rows": rows,
               "domain_missing": DOMAIN_MISSING}, open(a.out, "w"), indent=1)
    subprocess.run(["rm", "-rf", scr])
    print(f"sweep_ir.py: {len(rows)} blobs -> {a.out}  "
          f"[{a.opt} {a.mode}, marginal {a.n1}->{a.n2}, WHOLE PROGRAM]")
    return 0


def cmd_recompute(a):
    """Refresh every row's regressor columns from its blob. NO measurement.

    Exists so that adding a regressor costs a re-read of the input files and
    not 1200 callgrind runs. The `Ir` columns are never touched."""
    d = json.load(open(a.path))
    for r in d["rows"]:
        reg, stride, nwin = regressors(os.path.join(INDIR, r["blob"]))
        r.update(ncmp=reg[0], cbytes=reg[1], kbytes=reg[2], kblocks=reg[3],
                 neq=reg[4], kblk_mis=reg[5], stride=stride, nwin=nwin)
    d["domain_missing"] = DOMAIN_MISSING
    json.dump(d, open(a.path, "w"), indent=1)
    print(f"sweep_ir.py: recomputed regressors for {len(d['rows'])} rows "
          f"in {a.path} (no measurement)")
    return 0


def cmd_merge(a):
    files = a.merge.split(",")
    base = json.load(open(files[0]))
    seen = {r["blob"] for r in base["rows"]}
    for f in files[1:]:
        d = json.load(open(f))
        for key in ("opt", "mode", "n1", "n2"):
            if d[key] != base[key]:
                raise SystemExit(f"sweep_ir.py --merge: {key} differs "
                                 f"({base[key]} vs {d[key]}) -- refusing to "
                                 f"merge measurements from different "
                                 f"configurations")
        for r in d["rows"]:
            if r["blob"] not in seen:
                base["rows"].append(r)
                seen.add(r["blob"])
    base["rows"].sort(key=lambda r: r["blob"])
    json.dump(base, open(a.out, "w"), indent=1)
    print(f"sweep_ir.py: merged {len(files)} file(s) -> {a.out}, "
          f"{len(base['rows'])} rows [{base['opt']} {base['mode']}]")
    return 0


def lstsq(X, y):
    """OLS by Gaussian elimination on the normal equations -- no numpy on this
    box (`.memory/00-environment.md`)."""
    k = len(X[0])
    A = [[sum(X[r][i] * X[r][j] for r in range(len(X))) for j in range(k)]
         + [sum(X[r][i] * y[r] for r in range(len(X)))] for i in range(k)]
    for i in range(k):
        piv = max(range(i, k), key=lambda r: abs(A[r][i]))
        A[i], A[piv] = A[piv], A[i]
        if abs(A[i][i]) < 1e-9:
            return None
        for r in range(k):
            if r == i:
                continue
            f = A[r][i] / A[i][i]
            for c in range(i, k + 1):
                A[r][c] -= f * A[i][c]
    return [A[i][k] / A[i][i] for i in range(k)]


def rank(X):
    """Rank by Gaussian elimination, so `--fit` can say whether a held-out row
    is really outside the fit set's row space rather than assuming it."""
    M = [row[:] for row in X]
    rows, cols, r = len(M), len(M[0]), 0
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if abs(M[i][c]) > 1e-9:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        for i in range(rows):
            if i != r and abs(M[i][c]) > 1e-12:
                f = M[i][c] / M[r][c]
                for j in range(c, cols):
                    M[i][j] -= f * M[r][j]
        r += 1
    return r


def design(rows, names):
    return [[float(r[n]) if n != "const" else 1.0 for n in names] for r in rows]


def cmd_fit(a):
    d = json.load(open(a.path))
    names = a.regressors.split(",")
    fit_rows = [r for r in d["rows"] if not r["blob"].startswith("sweep-x")]
    oos_rows = [r for r in d["rows"] if r["blob"].startswith("sweep-x")]
    print(f"# p47 sweep fit  [{d['opt']} {d['mode']}, whole-program marginal "
          f"{d['n1']}->{d['n2']}]")
    print(f"# regressors: {names}")
    print(f"# fit set {len(fit_rows)} rows, HELD OUT {len(oos_rows)} "
          f"(band x: k > 0 AND nmatch > 0)")
    Xf = design(fit_rows, names)
    rk = rank(Xf)
    print(f"# design rank {rk} of {len(names)} columns")
    if oos_rows:
        Xo = design(oos_rows, names)
        rk_all = rank(Xf + Xo)
        print(f"# rank(fit) = {rk}, rank(fit + held-out) = {rk_all} -- "
              + ("the held-out rows are INSIDE the fit set's row space, so this "
                 "is an interpolation check and cannot fail in the strong sense"
                 if rk_all == rk and rk == len(names) else
                 "the held-out rows add no new direction only if these agree; "
                 "see .memory/03-measurement.md on band T"))
    for c in d["cells"]:
        y = [r[c] for r in fit_rows]
        b = lstsq(Xf, y)
        if b is None:
            print(f"{c:12s} SINGULAR")
            continue
        res = [y[i] - sum(Xf[i][j] * b[j] for j in range(len(names)))
               for i in range(len(y))]
        line = "  ".join(f"{n}={b[j]:+.5f}" for j, n in enumerate(names))
        print(f"{c:12s} {line}   max|resid|={max(abs(r) for r in res):.4f}")
        if oos_rows:
            worst, wb = 0.0, ""
            for i, r in enumerate(oos_rows):
                pred = sum(design([r], names)[0][j] * b[j]
                           for j in range(len(names)))
                e = abs(r[c] - pred)
                if e > worst:
                    worst, wb = e, r["blob"]
                print(f"             OOS {r['blob']:22s} pred={pred:10.3f} "
                      f"meas={r[c]:10.3f} resid={r[c] - pred:+9.3f}")
            print(f"             OOS max|resid| = {worst:.4f} at {wb}")
    print("\n# DOMAIN -- parameters this sweep does NOT vary. The list is not "
          "claimed closed (.memory/03-measurement.md).")
    for i, m in enumerate(d.get("domain_missing", DOMAIN_MISSING), 1):
        print(f"#  {i}. {m}")
    return 0


def cmd_leak(a):
    """The pattern's headline, printed as a verdict per rung.

    For the `k` band -- where `cbytes`, `ncmp` and every other regressor are
    held CONSTANT and only the first-mismatch position moves -- report the
    slope of Ir against k and the total spread. A constant-time rung must read
    0.000 and 0; a leaking one must not."""
    d = json.load(open(a.path))
    rows = sorted((r for r in d["rows"] if r["blob"].startswith("sweep-k")),
                  key=lambda r: r["kbytes"])
    if not rows:
        raise SystemExit("sweep_ir.py --leak: no sweep-k* rows in that file")
    cb = set(round(r["cbytes"], 6) for r in rows)
    nc = set(round(r["ncmp"], 6) for r in rows)
    print(f"# p47 LEAK VERDICT  [{d['opt']} {d['mode']}, whole-program "
          f"marginal {d['n1']}->{d['n2']}]")
    print(f"# {len(rows)} `sweep-k*` blobs. cbytes constant across the band: "
          f"{cb}  ncmp: {nc}")
    if len(cb) != 1 or len(nc) != 1:
        print("# ⚠ the band is NOT held constant in cbytes/ncmp -- the slope "
              "below is not a pure leak measurement")
    print(f"{'rung':12s} {'Ir@k=0':>11s} {'Ir@k=max':>11s} {'spread':>10s} "
          f"{'Ir/kbyte':>10s}  verdict")
    for c in d["cells"]:
        lo, hi = rows[0][c], rows[-1][c]
        span = hi - lo
        dk = rows[-1]["kbytes"] - rows[0]["kbytes"]
        slope = span / dk if dk else 0.0
        vals = [r[c] for r in rows]
        spread = max(vals) - min(vals)
        leaks = spread > 0.5
        expect = c in LEAKY
        mark = "" if leaks == expect else "   <-- NOT the declared class!"
        print(f"{c:12s} {lo:11.3f} {hi:11.3f} {spread:10.3f} {slope:10.5f}  "
              + ("LEAKS" if leaks else "constant in k") + mark)
    print("\n# `spread` is max-min over the whole band, in Ir per kernel call. "
          "A constant-time rung reads EXACTLY 0.000 here -- not 'small'.")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    m = ap.add_argument_group()
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--fit")
    ap.add_argument("--leak")
    ap.add_argument("--recompute")
    ap.add_argument("--merge")
    ap.add_argument("--cells", default=",".join(ALL_CELLS))
    ap.add_argument("--bands", default="", help="comma-separated band prefixes")
    ap.add_argument("--opt", default="O3", choices=["O0", "O3"])
    # NO DEFAULT: .memory/03-measurement.md, "a sweep's default mode is a
    # silent choice" -- p10's regressors swapped between modes.
    ap.add_argument("--mode", choices=["isolated", "whole"])
    ap.add_argument("--n1", type=int, default=100)
    ap.add_argument("--n2", type=int, default=200)
    ap.add_argument("--out", default=os.path.join(REPO, ".temp", "p47",
                                                  "sweep.json"))
    ap.add_argument("--regressors", default="ncmp,cbytes,neq,kblk_mis,const")
    del sub, m
    a = ap.parse_args()
    if a.measure:
        if not a.mode:
            raise SystemExit("sweep_ir.py: --mode is required for --measure; "
                             "a default inline mode is a silent choice")
        return cmd_measure(a)
    if a.fit:
        a.path = a.fit
        return cmd_fit(a)
    if a.leak:
        a.path = a.leak
        return cmd_leak(a)
    if a.recompute:
        a.path = a.recompute
        return cmd_recompute(a)
    if a.merge:
        return cmd_merge(a)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
