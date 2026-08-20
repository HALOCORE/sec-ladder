#!/usr/bin/env python3
"""p18's sweep fitter: marginal `Ir` per kernel call over the `sweep-*` bands.

`.memory/05-layout.md` says a pattern owes the sweep its laws are derived from,
and `.memory/03-measurement.md` says the only honest use of a whole-program `Ir`
figure is a SLOPE. So every number this script prints is

    ( Ir(n_iters = N2) - Ir(n_iters = N1) ) / (N2 - N1)

i.e. a marginal, differenced over `n_iters` on the SAME blob and the SAME binary,
with the file rewritten in `.temp/` rather than in `inputs/`. That cancels
process start-up, the payload load, the driver's `println!` digit-count term and
the fixed part of every call.

**On p18 the marginal and the kernel-exclusive column measure the same thing**,
which is not true on p14 or p13 and is worth stating: p18's kernel calls NO libc
routine at all -- no `memcpy`, no `memchr`, no `strlen` -- in any of the eight
cells, so nothing the kernel does leaves its own symbol. `.memory/03-measurement.md`'s
"name the routine beside every kernel-exclusive figure" is discharged by naming
the empty set, and ../NOTES.md 3 shows the `bulk` column of gate stage 3a where
every isolated cell reads `-`.

    python3 patterns/p18-varint-shift/controls/sweep_ir.py --band b --cells c-gcc,c-gcc-h
    python3 patterns/p18-varint-shift/controls/sweep_ir.py --band all --cells all --json out.json

Bands (`inputs/gen.py`):

    b   varint byte-length 1..10 at nv = 8      the per-BYTE term, at FIXED
                                                varint count
    v   nv 1..16 at varint length 4             both regressors together
    x   five heterogeneous shapes               every regressor non-zero at
                                                once and length-HETEROGENEOUS
                                                WITHIN a window, plus `x08b`, a
                                                WITHIN-BAND NEGATIVE CONTROL
                                                whose regressors equal `x08a`'s
                                                and whose bytes differ
    y   three EXTRAPOLATION shapes             bytes 160..320, nv 16..64 --
                                                outside the CONVEX HULL of
                                                b/v/x in both regressors, and
                                                predicted before being measured
                                                (controls/predict.py)

The pooled design is `[bytes, nv, 1]`, rank 3. **Dropping band b or band v
takes it to rank 2 -- **but band x alone is already rank 3, so the pooled design
stays rank 3 after dropping ANY single band and the leave-one-band-out test is
arithmetically incapable of failing.** That is measured, printed by `fit.py`,
and reported in ../NOTES.md 8 as a FAILED design goal rather than quoted as a
pass. What replaces it is band `y`: an extrapolation whose predictions are
registered and hashed before measurement (`controls/predict.py`).
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
BUILD = os.path.join(REPO, ".temp", "build", "p18")
SCRATCH = os.path.join(REPO, ".temp", "p18", "sweep", f"pid{os.getpid()}")
# PER-PID (TASK_026 §0 item 7, and TASK_051 repeats it). Two concurrent runs of
# this script sharing one scratch dir race on `a.bin`/`b.bin` and BOTH produce
# silent nonsense -- it happened on p14 (byte-identical `unsafe` and `verus`
# kernels read 3654 and 11550 Ir/call), and the numbers look plausible enough
# to publish.
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]

BANDS = {
    "b": "sweep-b*.bin",
    "v": "sweep-v*.bin",
    "x": "sweep-x*.bin",
    "y": "sweep-y*.bin",
    "all": "sweep-*.bin",
}

HDR = 4
VBITS = 64


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
        if not m:
            return None
        return int(m.group(1).replace(",", ""))


def marginal(binary, blob, n1, n2):
    a = rewrite_iters(blob, n1, os.path.join(SCRATCH, "a.bin"))
    b = rewrite_iters(blob, n2, os.path.join(SCRATCH, "b.bin"))
    ia, ib = total_ir(binary, a), total_ir(binary, b)
    if ia is None or ib is None:
        return None
    return (ib - ia) / (n2 - n1)


def shape(blob):
    """The regressors, read back out of the BLOB rather than out of `gen.py`'s
    constants, so they are a property of the file the measurement used.

      nv       varints the kernel actually walks   the per-VARINT regressor
      bytes    inner-loop iterations, i.e. varint bytes consumed
      term     varints that ended on a terminator (as opposed to on window
               exhaustion) -- a diagnostic, NOT a fit column
      over     bytes shifted at shift >= VBITS: **zero on every sweep blob by
               construction**, and checked here so that a band can never
               silently acquire an undefined shift and turn its R1 column into
               one legal outcome of UB (`.memory/02-bench-rules.md`)

    ⚠ `bytes` and `nv` are the only two columns the fit uses, with an intercept.
    `term` equals `nv` on every blob where no varint is cut off by the window
    end, i.e. on every sweep blob, so including it would make the design
    singular; `fit.py` refuses a singular design rather than reporting a huge
    condition number.
    """
    f = slb.read(blob)
    stride, body = slb.head1_u64_bytes(f.payload[: f.declared_len])
    win = body[:stride]
    nv = int.from_bytes(win[:4], "little")
    p, nb, walked, term, over = HDR, 0, 0, 0, 0
    for _ in range(nv):
        if p == stride:
            break
        shift, n = 0, 0
        ended = False
        while p < stride:
            c = win[p]
            p += 1
            n += 1
            if shift >= VBITS:
                over += 1
            shift += 7
            if not (c & 0x80):
                ended = True
                break
        nb += n
        term += 1 if ended else 0
        walked += 1
    return {"nv": walked, "bytes": nb, "term": term, "over": over,
            "stride": stride}


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
                                   "how the controls in .temp/p18/ctlbin are "
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
    hdr = f"{'blob':22s} {'nv':>4s} {'byte':>5s} {'term':>4s} {'over':>4s}"
    for c in cells:
        hdr += f" {c:>12s}"
    for b in extra:
        hdr += f" {os.path.basename(b):>20s}"
    print(hdr)
    for b in blobs:
        sh = shape(b)
        row = {"blob": os.path.basename(b), **sh, "ir": {}}
        line = (f"{os.path.basename(b):22s} {sh['nv']:4d} {sh['bytes']:5d} "
                f"{sh['term']:4d} {sh['over']:4d}")
        for c in cells:
            binp = os.path.join(BUILD, f"{c}-{a.opt}-{a.mode}")
            v = marginal(binp, b, a.n1, a.n2)
            row["ir"][c] = v
            line += f" {v:12.4f}" if v is not None else f" {'--':>12s}"
        for xb in extra:
            v = marginal(xb, b, a.n1, a.n2)
            row["ir"][os.path.basename(xb)] = v
            line += f" {v:20.4f}" if v is not None else f" {'--':>20s}"
        print(line)
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
