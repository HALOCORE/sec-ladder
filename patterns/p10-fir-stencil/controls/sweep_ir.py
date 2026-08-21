#!/usr/bin/env python3
"""p10's sweep fitter: marginal `Ir` per kernel call over the `sweep-*` bands.

`.memory/05-layout.md` says a pattern owes the sweep its laws are derived from,
and `.memory/03-measurement.md` says the only honest use of a whole-program `Ir`
figure is a SLOPE. So every number this script prints is

    ( Ir(n_iters = N2) - Ir(n_iters = N1) ) / (N2 - N1)

i.e. a marginal, differenced over `n_iters` on the SAME blob and the SAME binary,
with the file rewritten in `.temp/` rather than in `inputs/`. That cancels
process start-up, the payload load, the driver's `println!` digit-count term and
the fixed part of every call.

**On p10 the marginal and the kernel-exclusive column measure the same thing** at
`-O3 isolated`: p10's kernel calls NO libc routine at all -- no `memcpy`, no
`memchr`, no `strlen` -- in any of the eight cells, so nothing the kernel does
leaves its own symbol. `.memory/03-measurement.md`'s "name the routine beside
every kernel-exclusive figure" is discharged by naming the empty set, and gate
stage 3a's `bulk` column reads `-` on every isolated cell.

    python3 patterns/p10-fir-stencil/controls/sweep_ir.py --band r --cells unsafe
    python3 patterns/p10-fir-stencil/controls/sweep_ir.py --band all --cells all --json out.json

Bands (`inputs/gen.py`):

    r   radius 1..16 at nout = 32       the TAP-COUNT axis, at FIXED output count
    o   nout 8..192 at r = 4            the OUTPUT-COUNT axis, at FIXED radius
    e   four EXTRAPOLATION shapes       both parameters outside the convex hull
                                        of r/o/h, predicted before measurement
                                        (controls/predict.py)
    h   three HETEROGENEOUS shapes      windows of DIFFERENT (n, r) inside ONE
                                        blob, so a band is not a scalar multiple
                                        of another and the leave-one-band-out
                                        rank test is not vacuous

The regressors are read back out of the BLOB, never out of `gen.py`'s constants,
so they are a property of the file the measurement used:

    nout    outputs the kernel emits, summed over the windows the driver visits
    taps    2r+1
    vecit   floor(taps/W) * nout   -- VECTOR iterations at vector width W
            (default 8; `--width` on controls/fit.py). p10's tap loop is
            vectorised SSE2 at -O3, 8 samples per iteration, in EVERY spelling
            including the naive indexed one, so `taps` is NOT the regressor and
            a fit in it is a fit of the wrong model.
    scaltap (taps mod 8) * nout    -- SCALAR-EPILOGUE taps, which is where the
            whole safe-vs-unsafe difference lives (../NOTES.md 8)
    novec   1 iff floor(taps/8) == 0, i.e. the vector loop is never entered at
            all -- a separate REGIME, not a point on the same line
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "common"))
import slb  # noqa: E402

INPUTS = os.path.join(PDIR, "inputs")
BUILD = os.path.join(REPO, ".temp", "build", "p10")
SCRATCH = os.path.join(REPO, ".temp", "p10", "sweep", f"pid{os.getpid()}")
# PER-PID (TASK_026 §0 item 7, and TASK_057 repeats it). Two concurrent runs of
# this script sharing one scratch dir race on `a.bin`/`b.bin` and BOTH produce
# silent nonsense -- it happened on p14 (byte-identical `unsafe` and `verus`
# kernels read 3654 and 11550 Ir/call), and the numbers look plausible enough to
# publish.
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]

BANDS = {"r": "sweep-r*.bin", "o": "sweep-o*.bin", "e": "sweep-e*.bin",
         "h": "sweep-h*.bin", "all": "sweep-*.bin"}

HDR = 8


def rewrite_iters(path, n_iters, out):
    f = slb.read(path)
    slb.write(out, n_iters, f.payload[: f.declared_len])
    return out


def total_ir(binary, blob):
    """Whole-program `Ir` from callgrind's own summary line."""
    with tempfile.TemporaryDirectory(dir=SCRATCH) as td:
        r = subprocess.run(
            [VALGRIND, "--tool=callgrind",
             f"--callgrind-out-file={os.path.join(td, 'cg.out')}", binary, blob],
            capture_output=True, text=True)
        m = re.search(r"refs:\s+([\d,]+)", r.stderr)
        return int(m.group(1).replace(",", "")) if m else None


def marginal(binary, blob, n1, n2):
    a = rewrite_iters(blob, n1, os.path.join(SCRATCH, "a.bin"))
    b = rewrite_iters(blob, n2, os.path.join(SCRATCH, "b.bin"))
    ia, ib = total_ir(binary, a), total_ir(binary, b)
    if ia is None or ib is None:
        return None
    return (ib - ia) / (n2 - n1)


def _win_shape(blob, off, stride):
    n = int.from_bytes(blob[off:off + 4], "little")
    r = int.from_bytes(blob[off + 4:off + 8], "little")
    taps = 2 * r + 1
    if n < taps or 8 + taps + n - 1 >= stride:
        return 0, taps
    return n - 2 * r, taps


def shape(blob_path, n1=None, n2=None, width=8):
    """The regressors, averaged over the windows the driver actually visits.

    p10's driver picks `k = (acc * nwin) >> 64`, so on a heterogeneous blob the
    per-call regressors differ between calls. The marginal is a per-call MEAN,
    so the regressors have to be the same mean over the same visit sequence --
    which this replays exactly rather than assuming uniformity. Band `h` is the
    only band where it matters, and it is the band that exists to make the fit
    non-vacuous."""
    f = slb.read(blob_path)
    stride, body = slb.head1_u64_bytes(f.payload[: f.declared_len])
    n_blob = len(body)
    n1 = 0 if n1 is None else n1
    n2 = f.n_iters if n2 is None else n2
    if not (HDR <= stride <= n_blob):
        return {"nout": 0, "taps": 0, "vecit": 0, "scaltap": 0, "novec": 0,
                "stride": stride, "nwin": 0}
    nwin = n_blob // stride
    sh = [_win_shape(body, k * stride, stride) for k in range(nwin)]
    acc = 0
    keys = ("nout", "taps", "vecit", "scaltap", "novec", "novecout",
            "v16", "h8", "t8", "nov16out")
    tot = {k: 0 for k in keys}
    at_n1 = None
    MASK = (1 << 64) - 1
    M32 = (1 << 32) - 1
    vals = [None] * nwin
    for it in range(n2):
        if it == n1:
            at_n1 = dict(tot)
        k = (acc * nwin) >> 64
        nout, taps = sh[k]
        tot["nout"] += nout
        tot["taps"] += taps if nout else 0
        tot["vecit"] += (taps // width) * nout
        tot["scaltap"] += (taps % width) * nout
        tot["novec"] += 1 if (nout and taps // width == 0) else 0
        # NOVECOUT is the regressor that WORKS and `novec` is the one that does
        # not; both are printed because the difference is the finding. When
        # `taps < 8` LLVM's vector loop is never entered, so its setup and its
        # horizontal reduce are skipped ONCE PER OUTPUT and not once per call --
        # a call-counted regressor fits band `r` (where every no-vector window
        # has the same `nout`) and misses band `h` by up to 15.6 Ir.
        tot["novecout"] += nout if (nout and taps // width == 0) else 0
        # gcc's lowering is NOT LLVM's and needs its own columns. gcc
        # vectorises this loop 16 SAMPLES WIDE (`movdqu` + punpckh/punpckl)
        # and then emits an EIGHT-wide half-block (`movq` + punpcklbw) before
        # the scalar tail, so it has THREE regimes where LLVM has two -- which
        # is why the five-column LLVM design does not fit c-gcc at any single
        # vector width (max |resid| 387.8 at 8, 816.0 at 4, 521.6 at 16;
        # ../NOTES.md 8b). These four columns are gcc's shape, measured off the
        # listing exactly as the LLVM ones were.
        tot["v16"] += (taps // 16) * nout
        tot["h8"] += ((taps % 16) // 8) * nout
        tot["t8"] += (taps % 8) * nout
        tot["nov16out"] += nout if (nout and taps < 16) else 0
        if vals[k] is None:
            vals[k] = _win_value(body, k * stride, stride, MASK, M32)
        acc = (acc * 31 + vals[k]) & MASK
    if at_n1 is None:
        at_n1 = {k: 0 for k in keys}
        n1 = 0
    d = n2 - n1
    return {k: (tot[k] - at_n1[k]) / d for k in keys} | {"stride": stride,
                                                         "nwin": nwin}


def _win_value(blob, off, ln, MASK, M32):
    n = int.from_bytes(blob[off:off + 4], "little")
    r = int.from_bytes(blob[off + 4:off + 8], "little")
    taps = 2 * r + 1
    if n < taps or 8 + taps + n - 1 >= ln:
        return 0
    coef = blob[off + 8:off + 8 + taps]
    samp = blob[off + 8 + taps:off + 8 + taps + n]
    acc = 0
    for i in range(n - 2 * r):
        s = sum(a * c for a, c in zip(samp[i:i + taps], coef)) & M32
        acc = (acc * 31 + s) & MASK
    return (acc * 31 + (n - 2 * r)) & MASK


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--band", choices=sorted(BANDS))
    ap.add_argument("--blobs", help="comma-separated blob names in inputs/, "
                                    "instead of a band -- for putting the "
                                    "shipped small/large rows on the same "
                                    "differenced-marginal axis as the bands")
    ap.add_argument("--cells", default="unsafe")
    ap.add_argument("--bins", help="comma-separated extra binaries, by PATH, "
                                   "measured beside the named cells; this is "
                                   "how the controls in .temp/p10/ctlbin are "
                                   "put on the same axis as the shipped cells")
    ap.add_argument("--opt", default="O3")
    ap.add_argument("--mode", default="isolated")
    ap.add_argument("--n1", type=int, default=2000)
    ap.add_argument("--n2", type=int, default=6000)
    ap.add_argument("--json")
    a = ap.parse_args()
    os.makedirs(SCRATCH, exist_ok=True)
    cells = CELLS if a.cells == "all" else ([] if a.cells == "none"
                                            else a.cells.split(","))
    extra = a.bins.split(",") if a.bins else []
    if a.blobs:
        blobs = [os.path.join(INPUTS, b) for b in a.blobs.split(",")]
    elif a.band:
        blobs = sorted(glob.glob(os.path.join(INPUTS, BANDS[a.band])))
    else:
        raise SystemExit("give --band or --blobs")
    if not blobs:
        raise SystemExit(f"no blobs for band {a.band}; run inputs/gen.py --sweep")
    out = []
    hdr = (f"{'blob':20s} {'nout':>7s} {'taps':>6s} {'vecit':>8s} "
           f"{'scaltap':>8s} {'novec':>5s} {'novecout':>8s}")
    for c in cells:
        hdr += f" {c:>12s}"
    for b in extra:
        hdr += f" {os.path.basename(b):>22s}"
    print(hdr)
    for b in blobs:
        # THE REGRESSORS ARE DIFFERENCED THE SAME WAY THE `Ir` IS. The marginal
        # is (Ir(n2) - Ir(n1)) / (n2 - n1), i.e. a mean over calls n1..n2 and
        # NOT over 0..n2, so the regressors must be that same differenced mean.
        # On a homogeneous blob the two agree exactly; on band `h` -- the
        # heterogeneous band, the one that makes the leave-one-band-out test
        # non-vacuous -- they do not, and using the undifferenced mean left an
        # 11.26 Ir residual on `sweep-h1` that looked like a missing model term.
        sh = shape(b, a.n1, a.n2)
        row = {"blob": os.path.basename(b), **sh, "ir": {}}
        line = (f"{os.path.basename(b):20s} {sh['nout']:7.2f} {sh['taps']:6.2f} "
                f"{sh['vecit']:8.2f} {sh['scaltap']:8.2f} {sh['novec']:5.2f} "
                f"{sh['novecout']:8.2f}")
        for c in cells:
            binp = os.path.join(BUILD, f"{c}-{a.opt}-{a.mode}")
            v = marginal(binp, b, a.n1, a.n2)
            row["ir"][c] = v
            line += f" {v:12.4f}" if v is not None else f" {'--':>12s}"
        for xb in extra:
            v = marginal(xb, b, a.n1, a.n2)
            row["ir"][os.path.basename(xb)] = v
            line += f" {v:22.4f}" if v is not None else f" {'--':>22s}"
        print(line, flush=True)
        out.append(row)
    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"band": a.band or a.blobs,
                       "cells": cells + [os.path.basename(x) for x in extra],
                       "opt": a.opt, "mode": a.mode,
                       "n1": a.n1, "n2": a.n2, "rows": out}, fh, indent=1)
        print("wrote", a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
