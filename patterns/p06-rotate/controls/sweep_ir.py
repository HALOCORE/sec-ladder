#!/usr/bin/env python3
"""p06's sweep fitter: marginal `Ir` per kernel call over the `sweep-*` bands.

`.memory/05-layout.md` says a pattern owes the sweep its laws are derived from,
and `.memory/03-measurement.md` says the only honest use of a whole-program `Ir`
figure is a SLOPE. So every number this script prints is

    ( Ir(n_iters = N2) - Ir(n_iters = N1) ) / (N2 - N1)

i.e. a marginal, differenced over `n_iters` on the SAME blob and the SAME binary,
with the file rewritten in `.temp/` rather than in `inputs/`. That cancels
process start-up, the payload load, the driver's `println!` digit-count term and
the fixed part of every call, and — unlike the `results/*.json` column — it
INCLUDES the `memcpy` body, which is outside the kernel symbol. Both are
reported: p13's blocker 3 says name the routine beside every kernel-exclusive
figure, and p06's rungs all call exactly `memcpy@GLIBC_2.14` and nothing else.

    python3 patterns/p06-rotate/controls/sweep_ir.py --band n --cells unsafe,safe_naive
    python3 patterns/p06-rotate/controls/sweep_ir.py --band r --cells c-gcc,c-gcc-h
    python3 patterns/p06-rotate/controls/sweep_ir.py --band m --cells all --json out.json

Bands (`inputs/gen.py`):

    n   nrec 1..24 at m = 16, r = 2        the per-RECORD constant
    m   m 1..48 at nrec = 8, r = 2         the per-BYTE / per-SWAP terms
    r   r 0..m-1 at m = 32 (even) and 31 (odd), nrec = 8
                                           ITEM 3's falsifier: the `r` term is a
                                           PARITY term at even `m` and absent at
                                           odd `m`, and `r == 0` is a third case
    x   five heterogeneous shapes          every regressor non-zero at once,
                                           plus `x08b`, a WITHIN-BAND NEGATIVE
                                           CONTROL whose regressors equal
                                           `x08a`'s and whose bytes differ
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
BUILD = os.path.join(REPO, ".temp", "build", "p06")
SCRATCH = os.path.join(REPO, ".temp", "p06", "sweep")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]

BANDS = {
    "n": "sweep-n*.bin",
    "m": "sweep-m*.bin",
    "r": "sweep-r*.bin",
    "x": "sweep-x*.bin",
}

SCR = 64
HDR, REC_HDR = 4, 8


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
    """(nrec, sum m, swaps, records with m even and r odd, r == 0 records).

    Read back out of the blob, not out of `gen.py`'s constants, so the
    regressors are a property of the FILE the measurement used."""
    f = slb.read(blob)
    stride, body = slb.head1_u64_bytes(f.payload[: f.declared_len])
    win = body[:stride]
    nrec = int.from_bytes(win[:4], "little")
    p, sm, sw, par, z = HDR, 0, 0, 0, 0
    for _ in range(nrec):
        if stride - p < REC_HDR:
            break
        nelem = int.from_bytes(win[p:p + 4], "little")
        r = int.from_bytes(win[p + 4:p + 8], "little")
        p += REC_HDR
        m = min(nelem, SCR)
        if stride - p < nelem:
            break
        p += nelem
        rr = r % m if m else 0
        sm += m
        sw += m + (1 if (m % 2 == 0 and rr % 2 == 1) else 0)
        par += 1 if (m % 2 == 0 and rr % 2 == 1) else 0
        z += 1 if rr == 0 else 0
    return {"nrec": nrec, "sum_m": sm, "swaps": sw, "parity": par, "rzero": z,
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
                                   "how the controls in .temp/p06/ctlbin are "
                                   "put on the same axis as the shipped cells")
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
    hdr = f"{'blob':22s} {'nrec':>4s} {'sum_m':>5s} {'swaps':>5s} {'par':>3s} {'rz':>3s}"
    for c in cells:
        hdr += f" {c:>12s}"
    for b in extra:
        hdr += f" {os.path.basename(b):>20s}"
    print(hdr)
    for b in blobs:
        sh = shape(b)
        row = {"blob": os.path.basename(b), **sh, "ir": {}}
        line = (f"{os.path.basename(b):22s} {sh['nrec']:4d} {sh['sum_m']:5d} "
                f"{sh['swaps']:5d} {sh['parity']:3d} {sh['rzero']:3d}")
        for c in cells:
            binp = os.path.join(BUILD, f"{c}-O3-isolated")
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
            json.dump({"band": a.band or a.blobs, "cells": cells + [os.path.basename(x) for x in extra],
                       "n1": a.n1, "n2": a.n2,
                       "rows": out}, fh, indent=1)
        print("wrote", a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
