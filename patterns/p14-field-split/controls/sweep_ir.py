#!/usr/bin/env python3
"""p14's sweep fitter: marginal `Ir` per kernel call over the `sweep-*` bands.

`.memory/05-layout.md` says a pattern owes the sweep its laws are derived from,
and `.memory/03-measurement.md` says the only honest use of a whole-program `Ir`
figure is a SLOPE. So every number this script prints is

    ( Ir(n_iters = N2) - Ir(n_iters = N1) ) / (N2 - N1)

i.e. a marginal, differenced over `n_iters` on the SAME blob and the SAME binary,
with the file rewritten in `.temp/` rather than in `inputs/`. That cancels
process start-up, the payload load, the driver's `println!` digit-count term and
the fixed part of every call, and -- unlike the `results/*.json` column -- it
INCLUDES the `memcpy` body, which is outside the kernel symbol. p13's blocker 3
says name the routine beside every kernel-exclusive figure; ../NOTES.md 3 has the
per-rung libc call list and it is NOT uniform across compilers here.

    python3 patterns/p14-field-split/controls/sweep_ir.py --band t --cells unsafe,safe_naive
    python3 patterns/p14-field-split/controls/sweep_ir.py --band m --cells c-gcc,c-gcc-h
    python3 patterns/p14-field-split/controls/sweep_ir.py --band all --cells all --json out.json

Bands (`inputs/gen.py`):

    m   llen 4..60 step 2 at 4 fields, nline 8      the per-BYTE terms
    t   fields 1..16 at llen 60, nline 8            **the per-FIELD term, at
                                                    FIXED TOTAL BYTES** -- the
                                                    amortisation denominator
                                                    swept on its own, which is
                                                    the axis no earlier pattern
                                                    has
    l   nline 1..16 at llen 32, 4 fields            the per-LINE constant
    x   five heterogeneous shapes                   every regressor non-zero at
                                                    once, plus `x08b`, a
                                                    WITHIN-BAND NEGATIVE CONTROL
                                                    whose regressors equal
                                                    `x08a`'s and whose bytes
                                                    differ
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
BUILD = os.path.join(REPO, ".temp", "build", "p14")
SCRATCH = os.path.join(REPO, ".temp", "p14", "sweep", f"pid{os.getpid()}")
# PER-PID (TASK_026 §0 item 7). Two concurrent runs of this script sharing one
# scratch dir race on `a.bin`/`b.bin` and BOTH produce silent nonsense -- it
# happened here first (byte-identical `unsafe` and `verus` kernels read 3654
# and 11550 Ir/call), and the numbers look plausible enough to publish.
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]

BANDS = {
    "m": "sweep-m*.bin",
    "t": "sweep-t*.bin",
    "l": "sweep-l*.bin",
    "x": "sweep-x*.bin",
    "all": "sweep-*.bin",
}

SCR = 64
MAXTOK = 16
DELIM = 0x2C
HDR, LINE_HDR = 4, 4


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

      nline    lines the kernel actually walks
      bytes    sum of m = min(llen, SCR)          the per-BYTE regressor
      scan     sum of (m + 1)                     the SCAN's trip count
      fields   sum of min(ndelim + 1, MAXTOK)     the per-FIELD regressor
      content  sum over recorded fields of tl[j]  the bytes the FOLD reads
      empties  recorded fields of length 0        the probe's -5.00 correction
      res4     sum over recorded fields of tj % 4 the FOLD's unroll residue
      nz4      recorded fields with tj % 4 != 0   its indicator
      res2     sum over recorded fields of tj % 2

    ⚠ `scan == bytes + nline` and, whenever no line is truncated,
    `content == bytes - fields + nline`. **Both are EXACT linear combinations of
    the others**, so a design that includes them is singular; `fit.py` refuses
    it rather than reporting a huge condition number. The residue columns are
    NOT collinear and they are what the fold's unroll needs -- p06's
    `fold(m mod 4)` term, arriving on a second pattern.
    """
    f = slb.read(blob)
    stride, body = slb.head1_u64_bytes(f.payload[: f.declared_len])
    win = body[:stride]
    nline = int.from_bytes(win[:4], "little")
    p, nb, nsc, nf, nc, ne, walked = HDR, 0, 0, 0, 0, 0, 0
    r4 = z4 = r2 = 0
    for _ in range(nline):
        if stride - p < LINE_HDR:
            break
        llen = int.from_bytes(win[p:p + 4], "little")
        p += LINE_HDR
        m = min(llen, SCR)
        if stride - p < llen:
            break
        scr = bytes(win[p:p + m])
        p += llen
        flds = scr.split(bytes([DELIM]))[:MAXTOK]
        nb += m
        nsc += m + 1
        nf += len(flds)
        nc += sum(len(x) for x in flds)
        ne += sum(1 for x in flds if len(x) == 0)
        r4 += sum(len(x) % 4 for x in flds)
        z4 += sum(1 for x in flds if len(x) % 4)
        r2 += sum(len(x) % 2 for x in flds)
        walked += 1
    return {"nline": walked, "bytes": nb, "scan": nsc, "fields": nf,
            "content": nc, "empties": ne, "res4": r4, "nz4": z4, "res2": r2,
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
                                   "how the controls in .temp/p14/ctlbin are "
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
    hdr = (f"{'blob':22s} {'nlin':>4s} {'byte':>5s} {'scan':>5s} {'fld':>4s} "
           f"{'cont':>5s} {'emp':>4s}")
    for c in cells:
        hdr += f" {c:>12s}"
    for b in extra:
        hdr += f" {os.path.basename(b):>20s}"
    print(hdr)
    for b in blobs:
        sh = shape(b)
        row = {"blob": os.path.basename(b), **sh, "ir": {}}
        line = (f"{os.path.basename(b):22s} {sh['nline']:4d} {sh['bytes']:5d} "
                f"{sh['scan']:5d} {sh['fields']:4d} {sh['content']:5d} "
                f"{sh['empties']:4d}")
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
            json.dump({"band": a.band or a.blobs,
                       "cells": cells + [os.path.basename(x) for x in extra],
                       "n1": a.n1, "n2": a.n2, "rows": out}, fh, indent=1)
        print("wrote", a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
