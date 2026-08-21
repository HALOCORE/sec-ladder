#!/usr/bin/env python3
"""p27's Ir tables: whole-program marginal per call, the control comparisons,
and the PER-FUNCTION decomposition that 5e of ../NOTES.md rests on.

    harness/build.py p27                                    # the shipped cells
    sh patterns/p27-handle-table/controls/build_controls.sh  # the controls
    python3 patterns/p27-handle-table/controls/ir_table.py --marginal
    python3 patterns/p27-handle-table/controls/ir_table.py --functions

**WHY WHOLE-PROGRAM AND NOT KERNEL-EXCLUSIVE.** p27's kernel calls `malloc` and
`free` once per record and those bodies live in glibc, inside no symbol
`harness/measure.py`'s `_sum_rows` matches -- measured, 58-62% of the work. And
rustc emits the safe rungs' table drop as an out-of-line
`core::ptr::drop_glue::<[Option<Box<u8>>; 32]>`, which is likewise invisible to
the kernel column while the unsafe rungs' epilogue is inline in theirs.

⚠ **The two denominators disagree in SIGN on one comparison in this pattern.**
Kernel-exclusive, the vstd-pure control looks 30 Ir/call *cheaper* than the
shipped R5; whole-program it is 130 Ir/call *dearer*. The first reading is an
attribution artefact -- the work left the `kernel` symbol -- and publishing it
would have said the opposite of what the measurement says. `--marginal` prints
both columns for exactly that reason.

MARGINAL, NOT LEVEL: every figure is `(Ir(2N) - Ir(N)) / N` on one binary and
one input, which differences out the per-process constant
(`.memory/03-measurement.md` finding 20a). Interleaved by cell (input outer,
cell inner), foreground, per-PID scratch.
"""
import argparse
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PD))
sys.path.insert(0, os.path.join(REPO, "harness"))
import measure as M  # noqa: E402

VG = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CGA = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
IND = os.path.join(PD, "inputs")
BUILD = os.path.join(REPO, ".temp", "build", "p27")
CTRL = os.path.join(REPO, ".temp", "p27", "controls")

SHIPPED = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
           "safe_naive", "safe_tuned", "unsafe", "verus"]
CONTROLS = ["r5_vstdpure", "r4_tabchecked", "r3_issome", "r2_epilogue"]


def path_of(cell, opt, mode):
    p = os.path.join(BUILD, f"{cell}-{opt}-{mode}")
    return p if os.path.exists(p) else os.path.join(CTRL, f"{cell}-{opt}-{mode}")


def with_iters(src, n, scr):
    b = bytearray(open(src, "rb").read())
    b[0:8] = struct.pack("<Q", n)
    p = os.path.join(scr, f"in{n}.bin")
    open(p, "wb").write(bytes(b))
    return p


def total_ir(binary, arg, scr, tag):
    o = os.path.join(scr, f"cg.{tag}")
    r = subprocess.run([VG, "--tool=callgrind", f"--callgrind-out-file={o}",
                        binary, arg], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"ir_table.py: callgrind exit {r.returncode}")
    for line in open(o):
        if line.startswith("totals:"):
            return int(line.split()[1]), o
    raise SystemExit("ir_table.py: no `totals:` line")


def cmd_marginal(a):
    scr = os.path.join(REPO, ".temp", "p27", f"irt{os.getpid()}")
    os.makedirs(scr, exist_ok=True)
    cells = SHIPPED + (CONTROLS if a.controls else [])
    out = {}
    for inp, n1, n2 in (("small.bin", 20000, 40000), ("large.bin", 5000, 10000)):
        for c in cells:                       # input outer, CELL inner
            b = path_of(c, a.opt, a.mode)
            if not os.path.exists(b):
                continue
            t1, _ = total_ir(b, with_iters(os.path.join(IND, inp), n1, scr), scr, f"{c}.{inp}.1")
            t2, _ = total_ir(b, with_iters(os.path.join(IND, inp), n2, scr), scr, f"{c}.{inp}.2")
            k = M.callgrind_ir(b, with_iters(os.path.join(IND, inp), n2, scr), scr, f"{c}.{inp}.k")
            n = n2
            out[(c, inp)] = ((t2 - t1) / float(n2 - n1),
                             (k.get("kernel_exclusive_ir") or 0) / n)
            print(f"  {c:16s} {inp:11s} whole={out[(c,inp)][0]:11.4f} "
                  f"kernel~={out[(c,inp)][1]:11.4f}", flush=True)
    print()
    print(f"{'cell':16s} {'whole small':>13s} {'whole large':>13s}   "
          f"({a.opt} {a.mode})")
    for c in cells:
        if (c, "small.bin") in out:
            print(f"{c:16s} {out[(c,'small.bin')][0]:13.4f} {out[(c,'large.bin')][0]:13.4f}")
    subprocess.run(["rm", "-rf", scr])
    return 0


def cmd_functions(a):
    """The per-function marginal that ../NOTES.md 5e publishes: `malloc`, `free`
    and `drop_glue` priced separately from the kernel, which is what shows that
    the ALLOCATOR contributes exactly zero to the safe-vs-unsafe gap."""
    scr = os.path.join(REPO, ".temp", "p27", f"irf{os.getpid()}")
    os.makedirs(scr, exist_ok=True)
    needles = ("kernel", "malloc", "free", "drop_glue")
    tot = {}
    for c in a.cells.split(","):
        b = path_of(c, a.opt, a.mode)
        rows = {}
        for n in (a.n1, a.n2):
            _, o = total_ir(b, with_iters(os.path.join(IND, a.input), n, scr), scr, f"{c}.{n}")
            ann = subprocess.run([CGA, "--threshold=99", o],
                                 capture_output=True, text=True).stdout
            for line in ann.splitlines():
                for nd in needles:
                    if nd in line and "PROGRAM TOTALS" not in line:
                        try:
                            v = int(line.split()[0].replace(",", ""))
                        except (ValueError, IndexError):
                            continue
                        rows.setdefault((nd, n), 0)
                        rows[(nd, n)] = max(rows[(nd, n)], v)
        tot[c] = {nd: (rows.get((nd, a.n2), 0) - rows.get((nd, a.n1), 0))
                  / float(a.n2 - a.n1) for nd in needles}
        print(f"  {c:16s} " + "  ".join(f"{nd}={tot[c][nd]:10.4f}" for nd in needles),
              flush=True)
    subprocess.run(["rm", "-rf", scr])
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marginal", action="store_true")
    ap.add_argument("--functions", action="store_true")
    ap.add_argument("--controls", action="store_true", default=True)
    ap.add_argument("--opt", default="O3")
    ap.add_argument("--mode", default="isolated")
    ap.add_argument("--input", default="small.bin")
    ap.add_argument("--cells", default="safe_tuned,unsafe")
    ap.add_argument("--n1", type=int, default=20000)
    ap.add_argument("--n2", type=int, default=40000)
    a = ap.parse_args()
    if a.functions:
        return cmd_functions(a)
    return cmd_marginal(a)


if __name__ == "__main__":
    sys.exit(main())
