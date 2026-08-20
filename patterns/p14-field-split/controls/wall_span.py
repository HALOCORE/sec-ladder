#!/usr/bin/env python3
"""p14's wall-clock protocol, in one script, because `.memory/03-measurement.md`
says a bare `ns` number on this box is worth nothing without three controls --
and because p14's `results/*.json` `ns` column contains a worked example of why:
`unsafe` and `verus` have BYTE-IDENTICAL kernels at -O3 (`md5_raw
3cfea50590f84bad0e12ea8aa1970032`) and their `small` minima there differ by
7.2%. That column is a whole-process LEVEL, not a difference.

    python3 patterns/p14-field-split/controls/wall_span.py --input small --reps 15

What it does, in this order:

1. **The identical-copy NOISE FLOOR.** `--copies N` byte-identical copies of
   every named binary, at distinct inodes and one fixed layout. Anything smaller
   than the spread over those copies is not an effect. `common/layout/order.py`
   only knows the three Rust cells, and p14's most interesting clock question is
   C-vs-C (does clang's LOST 2x UNROLL of the scan cost time?), so the control is
   re-implemented here over an arbitrary binary list.
   (`order.py` appends `.bin` to `--input`; this script takes the same
   convention, so pass `small` and not `small.bin`.)
2. **ALTERNATING schedule, one launch per cell per round.** TASK_031 measured
   p05's R3-vs-R4 at `+1.21%` alternating and `-4.16%` blocked on 31 identical
   copies at one layout. Blocked scheduling alone flips signs.
3. **`t(n_iters) - t(1)`**, so the payload load, process start-up and the
   `println!` are differenced out and what is left is the kernel loop.

⚠ **What this script does NOT do is build a LAYOUT POPULATION.** It holds layout
fixed and measures the floor. A sign that survives here can still be a layout
mode (`.memory/03-measurement.md`: p01 and p07 flip sign between `win32`
residues), so any claim made from it must say so -- p14 publishes its clock
figures as SECONDARY and its headline is an `Ir` decomposition.

Reports, per cell: the per-call ns from the differenced pair, the median and min
over reps, and the identical-copy floor beside it.
"""


import argparse
import os
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "common"))
import slb  # noqa: E402

INPUTS = os.path.join(PDIR, "inputs")
BUILD = os.path.join(REPO, ".temp", "build", "p14")
SCRATCH = os.path.join(REPO, ".temp", "p14", "wall")

DEFAULT = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
           "safe_naive", "safe_tuned", "unsafe", "verus"]


def resolve(name):
    p = os.path.join(BUILD, f"{name}-O3-isolated")
    return p if os.path.exists(p) else name


def prep_input(stem, n_iters, out):
    f = slb.read(os.path.join(INPUTS, stem + ".bin"))
    slb.write(out, n_iters, f.payload[: f.declared_len])
    return out


def timed(binary, blob):
    t0 = time.perf_counter()
    r = subprocess.run(["/usr/bin/taskset", "-c", CPU, binary, blob],
                       capture_output=True, text=True)
    t1 = time.perf_counter()
    return t1 - t0, r.stdout.strip()


def main():
    global CPU
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default="small", help="blob STEM, no .bin")
    ap.add_argument("--cells", default=",".join(DEFAULT))
    ap.add_argument("--n-iters", type=int, default=200000)
    ap.add_argument("--reps", type=int, default=15)
    ap.add_argument("--copies", type=int, default=5,
                    help="byte-identical copies per cell: the NOISE FLOOR")
    ap.add_argument("--cpu", default="5")
    a = ap.parse_args()
    CPU = a.cpu
    os.makedirs(SCRATCH, exist_ok=True)
    cells = a.cells.split(",")

    big = prep_input(a.input, a.n_iters, os.path.join(SCRATCH, "big.bin"))
    one = prep_input(a.input, 1, os.path.join(SCRATCH, "one.bin"))

    # byte-identical copies, distinct inodes, one fixed layout
    copies = {}
    for c in cells:
        src = resolve(c)
        copies[c] = []
        for i in range(a.copies):
            dst = os.path.join(SCRATCH, f"{os.path.basename(src)}.copy{i}")
            shutil.copyfile(src, dst)
            os.chmod(dst, 0o755)
            copies[c].append(dst)

    samples = {(c, i): [] for c in cells for i in range(a.copies)}
    csums = {}
    for _ in range(a.reps):
        for i in range(a.copies):          # ALTERNATING, never blocked
            for c in cells:
                b = copies[c][i]
                t1, s1 = timed(b, one)
                tN, sN = timed(b, big)
                csums.setdefault(c, sN)
                samples[(c, i)].append((tN - t1) / (a.n_iters - 1) * 1e9)

    print(f"# input={a.input} n_iters={a.n_iters} reps={a.reps} "
          f"copies={a.copies} cpu={a.cpu} schedule=alternating "
          f"estimator=(t(n_iters)-t(1))/(n_iters-1)")
    print(f"{'cell':12s} {'ns/call med':>12s} {'min':>10s} "
          f"{'copy-spread%':>13s}  checksum")
    base = {}
    for c in cells:
        med = [statistics.median(samples[(c, i)]) for i in range(a.copies)]
        allv = sorted(v for i in range(a.copies) for v in samples[(c, i)])
        floor = (max(med) - min(med)) / statistics.median(med) * 100
        base[c] = statistics.median(med)
        print(f"{c:12s} {statistics.median(med):12.2f} {allv[0]:10.2f} "
              f"{floor:13.2f}  {csums[c]}")
    print("\n# pairwise, median of per-copy medians")
    for x, y in (("c-gcc-h", "c-gcc"), ("c-clang-h", "c-clang"),
                 ("safe_naive", "unsafe"), ("safe_tuned", "unsafe"),
                 ("verus", "unsafe")):
        if x in base and y in base:
            print(f"   {x:12s} - {y:12s} = {base[x] - base[y]:+9.2f} ns "
                  f"({(base[x] / base[y] - 1) * 100:+6.2f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
