#!/usr/bin/env python3
"""p27's Ir tables: whole-program marginal per call, the control comparisons,
and the PER-FUNCTION decomposition that 5e of ../NOTES.md rests on.

    harness/build.py p27                                    # the shipped cells
    sh patterns/p27-handle-table/controls/build_controls.sh  # the controls
    python3 patterns/p27-handle-table/controls/ir_table.py --marginal
    python3 patterns/p27-handle-table/controls/ir_table.py --functions
    python3 .../ir_table.py --closed --cells safe_tuned,unsafe   # the CLOSED one

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
import re
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
CONTROLS = ["r5_vstdpure", "r4_tabchecked", "r4_bufchecked", "r4_allchecked",
            "r4_epiclear", "r3_issome", "r2_epilogue"]


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


def cmd_closed(a):
    """The CLOSED per-function decomposition ../NOTES.md 5e publishes.

    `--functions` above substring-matches four needles and takes a `max` over
    the matching `callgrind_annotate` lines, so it can only ever confirm the
    terms it was told to look for -- it cannot answer *is anything else
    moving?*. This mode parses the WHOLE annotate table, prints every function
    whose marginal moved, and prints the SUM of the per-function deltas beside
    the whole-program delta. When the two agree, the decomposition is closed:
    nothing outside the printed terms moved. Ported from TASK_060_REVIEW's
    `fndelta.py`, which is where the closure was first measured."""
    scr = os.path.join(REPO, ".temp", "p27", f"irc{os.getpid()}")
    os.makedirs(scr, exist_ok=True)
    res = {}
    cells = a.cells.split(",")
    for c in cells:
        b = path_of(c, a.opt, a.mode)
        per = {}
        tots = {}
        for n in (a.n1, a.n2):
            tots[n], o = total_ir(b, with_iters(os.path.join(IND, a.input), n, scr),
                                  scr, f"{c}.{n}")
            ann = subprocess.run([CGA, "--threshold=100", o],
                                 capture_output=True, text=True).stdout
            for line in ann.splitlines():
                m = re.match(r"^([\d,]+)\s*(\([^)]*\))?\s+(.*)$", line.strip())
                if not m:
                    continue
                v = m.group(1).replace(",", "")
                name = m.group(3).strip()
                if not v.isdigit() or not name or "PROGRAM TOTALS" in name:
                    continue
                # Normalise so the SAME function in two different binaries is
                # ONE row: callgrind qualifies every symbol with the object
                # path it came from and rustc mangles the crate name in, so
                # `safe_tuned::kernel` and `unsafe::kernel` would otherwise be
                # two rows with a zero in the other column and the reader would
                # have to match them by eye.
                name = re.sub(r"\s*\[[^\]]*\]\s*$", "", name)
                name = re.sub(r"^\?\?\?:", "", name)
                name = re.sub(r"^/rustc/[0-9a-f]+/library/", "", name)
                name = name.replace(f"{c}::", "")
                per.setdefault(name, {}).setdefault(n, 0)
                per[name][n] += int(v)
        d = float(a.n2 - a.n1)
        res[c] = ((tots[a.n2] - tots[a.n1]) / d,
                  {k: (v.get(a.n2, 0) - v.get(a.n1, 0)) / d for k, v in per.items()})
        print(f"  {c:16s} whole={res[c][0]:12.4f}   "
              f"({a.input} {a.opt} {a.mode} n {a.n1}->{a.n2})", flush=True)
    if len(cells) == 2:
        (ta, pa), (tb, pb) = res[cells[0]], res[cells[1]]
        print(f"\n{'function':62s} {cells[0]:>12s} {cells[1]:>12s} {'delta':>12s}")
        tot_d = 0.0
        for k in sorted(set(pa) | set(pb),
                        key=lambda k: -abs(pa.get(k, 0.0) - pb.get(k, 0.0))):
            dv = pa.get(k, 0.0) - pb.get(k, 0.0)
            tot_d += dv
            if abs(dv) > 0.0005 or max(pa.get(k, 0.0), pb.get(k, 0.0)) > 1.0:
                print(f"{k[:62]:62s} {pa.get(k,0.0):12.4f} {pb.get(k,0.0):12.4f} {dv:12.4f}")
        print(f"\n{'SUM over EVERY function':62s} {'':12s} {'':12s} {tot_d:12.4f}")
        print(f"{'whole-program delta':62s} {ta:12.4f} {tb:12.4f} {ta - tb:12.4f}")
        print(f"{'closed?':62s} {'':12s} {'':12s} "
              f"{'YES' if abs(tot_d - (ta - tb)) < 0.001 else 'NO':>12s}")
    subprocess.run(["rm", "-rf", scr])
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marginal", action="store_true")
    ap.add_argument("--functions", action="store_true")
    ap.add_argument("--closed", action="store_true")
    ap.add_argument("--controls", action="store_true", default=True)
    ap.add_argument("--opt", default="O3")
    ap.add_argument("--mode", default="isolated")
    ap.add_argument("--input", default="small.bin")
    ap.add_argument("--cells", default="safe_tuned,unsafe")
    ap.add_argument("--n1", type=int, default=20000)
    ap.add_argument("--n2", type=int, default=40000)
    a = ap.parse_args()
    if a.closed:
        return cmd_closed(a)
    if a.functions:
        return cmd_functions(a)
    return cmd_marginal(a)


if __name__ == "__main__":
    sys.exit(main())
