#!/usr/bin/env python3
"""p36's swept measurements: `Ir` and the INDIRECT-BRANCH counters over the
`sweep-*` bands, plus wall clock on the band that holds `Ir` fixed.

Three bands (`inputs/gen.py`):

  sweep-n*     records per window. The length axis.
  sweep-mix*   ⚠ **THE OPCODE-ORDER AXIS, and p36's own.** Every blob holds the
               opcode MULTISET fixed -- 32 of each of the eight opcodes per
               window -- and the identical operand stream; only the arrangement
               differs. The eight callees therefore run the same number of times
               in every blob of the band, so `Ir` is identical BY CONSTRUCTION
               while the indirect call goes from one target per run of 32 to a
               target the predictor cannot learn.
  sweep-t*     number of distinct targets. The multiset is NOT held fixed here,
               so this band's `Ir` is measured and reported, never assumed.

⚠ **`Ir` is not time, and on this band that is the point.** Callgrind's
`--branch-sim=yes` gives `Bi` (indirect branches executed) and `Bim` (indirect
branches mispredicted), which are the mechanism, and this box has no hardware
counters at all (`.memory/00-environment.md`). The wall-clock half compares the
**same binary on different inputs**, so code layout is held EXACTLY fixed and no
layout population is needed -- p07's *"changing only the workload"* control,
reused.

    python3 patterns/p36-vtable-dispatch/controls/sweep_ir.py --band mix
    python3 patterns/p36-vtable-dispatch/controls/sweep_ir.py --band n --cell unsafe
    python3 patterns/p36-vtable-dispatch/controls/sweep_ir.py --band mix --wall
"""

import argparse
import glob
import os
import re
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANN = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
CGDIR = os.path.join(REPO, ".temp", "p36", "cg")

sys.path.insert(0, os.path.join(REPO, "common"))
import slb  # noqa: E402


def cell_bin(cell, opt="O3", mode="isolated"):
    return os.path.join(REPO, ".temp", "build", "p36", f"{cell}-{opt}-{mode}")


def n_calls(blob):
    f = slb.read(blob)
    return f.n_iters


def counters(binary, blob, branch=False):
    """Per-function exclusive Ir for the kernel symbol, and (optionally) the
    indirect-branch counters for the WHOLE program.

    ⚠ The `Bi`/`Bim` numbers are whole-program, because callgrind_annotate's
    per-function branch columns are not exposed by the same `--threshold` path;
    the driver's own branches are a per-call constant that cancels in a
    difference across two inputs of the same shape, which is the only way this
    script uses them."""
    os.makedirs(CGDIR, exist_ok=True)
    out = os.path.join(CGDIR, "cg.out")
    cmd = [VALGRIND, "--tool=callgrind", f"--callgrind-out-file={out}"]
    if branch:
        cmd.append("--branch-sim=yes")
    cmd += [binary, blob]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    ann = subprocess.run([CG_ANN, "--threshold=100", out],
                         capture_output=True, text=True, check=True).stdout
    ir = 0
    for line in ann.splitlines():
        if "kernel" in line and re.match(r"^\s*[\d,]+", line):
            ir = int(line.split()[0].replace(",", ""))
            break
    bi = bim = None
    if branch:
        txt = open(out).read()
        ev = re.search(r"^events:\s+(.*)$", txt, re.M).group(1).split()
        tot = [0] * len(ev)
        for line in txt.splitlines():
            if re.match(r"^\d+(\s+\d+)*$", line):
                vals = [int(v) for v in line.split()][1:]
                for i, v in enumerate(vals):
                    if i < len(tot):
                        tot[i] += v
        idx = {n: i for i, n in enumerate(ev)}
        # events line is `Ir Bc Bcm Bi Bim`; the per-line first column is the
        # position, so `tot` is offset by one -- recompute from the summary.
        m = re.search(r"^summary:\s+(.*)$", txt, re.M)
        if m:
            s = [int(v) for v in m.group(1).split()]
            bi = s[idx["Bi"]] if "Bi" in idx and idx["Bi"] < len(s) else None
            bim = s[idx["Bim"]] if "Bim" in idx and idx["Bim"] < len(s) else None
    return ir, bi, bim


def wall(binary, blob, reps=15):
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        subprocess.run(["taskset", "-c", "3", binary, blob],
                       capture_output=True, check=True)
        ts.append(time.perf_counter() - t0)
    return min(ts), statistics.median(ts)


def rescale(blob, n_iters, scr):
    """A copy of `blob` with `n_iters` rewritten, under `scr`.

    ⚠ **The wall-clock half needs this and the reason is a measured project
    defect.** `.memory/03-measurement.md` (finding 20a): `measure.py`'s `ns`
    column is a whole-process LEVEL, and the per-process constant -- argv, file
    I/O, payload decode -- is inside every number. The sweep blobs ship
    `n_iters = 2000`, which on p36 is about 2 ms of kernel against 1-2 ms of
    startup, so half of a raw `ns` reading would be the constant. Rescaling to a
    large `n_iters` pushes it under 1%, and the quantity actually quoted is a
    DIFFERENCE between two blobs of identical shape, in which the constant
    cancels exactly."""
    os.makedirs(scr, exist_ok=True)
    f = slb.read(blob)
    out = os.path.join(scr, f"x{n_iters}." + os.path.basename(blob))
    slb.write(out, n_iters, f.payload, f.declared_len)
    return out


def band_blobs(band):
    pat = os.path.join(PDIR, "inputs", f"sweep-{band}*.bin")
    return sorted(glob.glob(pat))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--band", default="mix")
    ap.add_argument("--cell", default="unsafe")
    ap.add_argument("--bin", default=None,
                    help="an explicit binary (e.g. a controls/ variant) instead "
                         "of a matrix cell")
    ap.add_argument("--opt", default="O3")
    ap.add_argument("--mode", default="isolated")
    ap.add_argument("--wall", action="store_true")
    ap.add_argument("--reps", type=int, default=15)
    ap.add_argument("--floor", type=int, default=0,
                    help="NOISE FLOOR: time N byte-identical copies of the "
                         "first blob of the band under different names, before "
                         "believing any effect (`.memory/03-measurement.md`, "
                         "finding 16's methodology rule)")
    ap.add_argument("--wall-iters", type=int, default=200000,
                    help="rewrite n_iters for the wall-clock half; see rescale()")
    a = ap.parse_args()
    b = a.bin or cell_bin(a.cell, a.opt, a.mode)
    if not os.path.exists(b):
        raise SystemExit(f"{b} not built -- run harness/build.py p36")
    blobs = band_blobs(a.band)
    if not blobs:
        raise SystemExit(f"no sweep-{a.band}* blobs -- run inputs/gen.py --sweep")
    print(f"cell {a.bin or a.cell} {a.opt}/{a.mode}   band sweep-{a.band}*")
    if a.floor:
        scr = os.path.join(REPO, ".temp", "p36", f"floor.{os.getpid()}")
        os.makedirs(scr, exist_ok=True)
        src = slb.read(blobs[0])
        print(f"NOISE FLOOR: {a.floor} byte-identical copies of "
              f"{os.path.basename(blobs[0])}, n_iters={a.wall_iters}, "
              f"{a.reps} reps each")
        vals = []
        for i in range(a.floor):
            cp = os.path.join(scr, f"copy{i}.bin")
            slb.write(cp, a.wall_iters, src.payload, src.declared_len)
            mn, md = wall(b, cp, a.reps)
            vals.append(mn / a.wall_iters * 1e9)
            print(f"  copy{i}  min ns/call={vals[-1]:9.2f}  med={md / a.wall_iters * 1e9:9.2f}")
        print(f"  floor: min={min(vals):.2f} max={max(vals):.2f} "
              f"spread={100 * (max(vals) - min(vals)) / min(vals):.2f}% of min")
        return 0
    hdr = f"{'blob':22s} {'calls':>7s} {'Ir/call':>13s} {'Bi':>12s} {'Bim':>12s} {'Bim/Bi':>8s}"
    if a.wall:
        hdr += f" {'min ns/call':>13s} {'med ns/call':>13s}"
    print(hdr)
    for blob in blobs:
        nc = n_calls(blob)
        ir, bi, bim = counters(b, blob, branch=True)
        row = (f"{os.path.basename(blob):22s} {nc:7d} {ir / nc:13.4f} "
               f"{bi if bi is not None else -1:12d} "
               f"{bim if bim is not None else -1:12d} "
               f"{(bim / bi if bi else 0):8.4f}")
        if a.wall:
            scr = os.path.join(REPO, ".temp", "p36", f"wall.{os.getpid()}")
            big = rescale(blob, a.wall_iters, scr)
            mn, md = wall(b, big, a.reps)
            row += f" {mn / a.wall_iters * 1e9:13.2f} {md / a.wall_iters * 1e9:13.2f}"
        print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
