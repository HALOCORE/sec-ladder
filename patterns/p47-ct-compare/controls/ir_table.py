#!/usr/bin/env python3
"""p47's Ir table for the SHIPPED cells and the CONTROL variants, plus the
closed per-function decomposition.

    python3 patterns/p47-ct-compare/controls/ir_table.py --mode isolated \\
        --inputs small.bin,large.bin,adversarial-k000.bin,adversarial-klast.bin
    python3 patterns/p47-ct-compare/controls/ir_table.py --mode isolated \\
        --leak-controls
    python3 patterns/p47-ct-compare/controls/ir_table.py --closed \\
        --a safe_tuned --b unsafe --input large.bin --mode isolated

Every figure is a **whole-program marginal** `(Ir(n2) - Ir(n1)) / (n2 - n1)`,
which differences `measure.py`'s per-process level away exactly
(`.memory/03-measurement.md` finding 20a), and every figure names its inline
mode, because p10's regressors swapped between modes.

`--closed` is p27's decomposition (`.memory/03-measurement.md`, "close a
decomposition over EVERY function"): it parses the WHOLE callgrind function
table for two cells and prints every function whose per-call Ir differs, with
the sum checked against the whole-program delta. Four named needles cannot see
a fifth; a closed table can.

`--leak-controls` runs the pattern's central claim on the CONTROL binaries:
`adversarial-k000` against `adversarial-klast` -- two files with identical
checksums and different first-mismatch positions -- so that *"this variant
leaks"* is a measurement on that variant's own object code.
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

INDIR = os.path.join(PD, "inputs")
BUILD = os.path.join(REPO, ".temp", "build", "p47")
CTLBIN = os.path.join(REPO, ".temp", "p47", "ctlbin")
VG = os.path.expanduser("~/tools/valgrind/bin/valgrind")
ANN = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")

CELLS = ["c-gcc", "c-clang", "c-gcc-h", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]
CONTROLS = ["t_split", "t_win", "t_iter", "u_base", "u_win", "u_ptr",
            "n_early", "m_leak"]
C_CONTROLS = ["h_vol-gcc", "h_vol-clang"]
#: what `--leak-controls` measures by DEFAULT: exactly the twelve rows
#: ../NOTES.md 6 publishes. Before TASK_065 the default was `CELLS`, so
#: ../README.md's documented reproduction line printed eight rows against a
#: twelve-row published table (TASK_064_REVIEW major 1, second adjacent defect).
LEAK_CELLS = CELLS + ["m_leak", "n_early", "h_vol-clang", "h_vol-gcc"]


def binary(name, mode):
    """The object for `name` at `-O3 <mode>`, or None.

    ⚠ **No cross-MODE fallback.** Until TASK_065 this fell back to
    `CTLBIN/{name}-O3-isolated` when a `whole` build was absent, so `--mode
    whole` on a control built only isolated printed an ISOLATED figure under a
    `whole` heading -- a silent wrong answer in the tool that produced this
    pattern's tables (TASK_064_REVIEW major 1, third adjacent defect). No
    published figure was affected: every `h_vol` number in ../NOTES.md 8c is
    isolated. `gen_controls.py --build` now writes both modes for every kind,
    so the fallback has nothing left to rescue and a genuine gap prints
    MISSING."""
    for cand in (os.path.join(BUILD, f"{name}-O3-{mode}"),
                 os.path.join(CTLBIN, f"{name}-O3-{mode}")):
        if os.path.exists(cand):
            return cand
    return None


def rewrite_iters(src, dst, n):
    b = bytearray(open(src, "rb").read())
    b[0:8] = struct.pack("<Q", n)
    open(dst, "wb").write(bytes(b))


def run_cg(binpath, arg, out):
    r = subprocess.run([VG, "--tool=callgrind", f"--callgrind-out-file={out}",
                        binpath, arg], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"ir_table.py: callgrind exit {r.returncode} on "
                         f"{binpath}: {r.stderr[-300:]}")
    for line in open(out):
        if line.startswith("totals:"):
            return int(line.split()[1])
    raise SystemExit("ir_table.py: no totals: line")


def marginal(binpath, inp, scr, n1=100, n2=200):
    vals = {}
    for n in (n1, n2):
        p = os.path.join(scr, f"in.{n}.bin")
        rewrite_iters(inp, p, n)
        o = os.path.join(scr, f"cg.{n}")
        vals[n] = run_cg(binpath, p, o)
        os.unlink(o)
    return (vals[n2] - vals[n1]) / float(n2 - n1)


def fn_table(binpath, inp, scr, n, tag):
    """{function -> Ir} from callgrind_annotate over the WHOLE program."""
    p = os.path.join(scr, f"in.{n}.bin")
    rewrite_iters(inp, p, n)
    o = os.path.join(scr, f"cg.{tag}.{n}")
    run_cg(binpath, p, o)
    r = subprocess.run([ANN, "--threshold=100", o], capture_output=True,
                       text=True)
    tab = {}
    for line in r.stdout.splitlines():
        m = re.match(r"^\s*([\d,]+)\s+\(\s*[\d.]+%\)\s+(\S.*)$", line)
        if not m:
            m = re.match(r"^\s*([\d,]+)\s+(\S.*)$", line)
        if not m:
            continue
        try:
            v = int(m.group(1).replace(",", ""))
        except ValueError:
            continue
        name = m.group(2).strip()
        if name.startswith("PROGRAM TOTALS") or name.startswith("--"):
            continue
        tab[name] = tab.get(name, 0) + v
    os.unlink(o)
    return tab


def cmd_table(a, scr):
    names = a.cells.split(",")
    inputs = a.inputs.split(",")
    print(f"# p47 whole-program marginal Ir/call  [-O3 {a.mode}, "
          f"{a.n1}->{a.n2}]")
    print(f"{'cell':16s}" + "".join(f"{i:>26s}" for i in inputs))
    for c in names:
        b = binary(c, a.mode)
        if not b:
            print(f"{c:16s} MISSING")
            continue
        row = []
        for i in inputs:
            row.append(marginal(b, os.path.join(INDIR, i), scr, a.n1, a.n2))
        print(f"{c:16s}" + "".join(f"{v:26.3f}" for v in row))
    return 0


def cmd_leak_controls(a, scr):
    """The pattern's claim, run on each named binary: k=0 vs k=last, at an
    identical checksum."""
    k0 = os.path.join(INDIR, "adversarial-k000.bin")
    kl = os.path.join(INDIR, "adversarial-klast.bin")
    eq = os.path.join(INDIR, "adversarial-equal.bin")
    print(f"# p47 LEAK on the CONTROL objects  [-O3 {a.mode}, "
          f"{a.n1}->{a.n2}, whole-program marginal]")
    print("# adversarial-k000 and adversarial-klast print the SAME checksum on "
          "every cell;\n# they differ only in where the first mismatching byte "
          "is (0 vs 127 of a 128-byte tag).")
    print(f"{'binary':16s} {'k=0':>12s} {'k=127':>12s} {'equal':>12s} "
          f"{'klast-k000':>12s}  verdict")
    for c in a.cells.split(","):
        b = binary(c, a.mode)
        if not b:
            print(f"{c:16s} MISSING")
            continue
        v0 = marginal(b, k0, scr, a.n1, a.n2)
        vl = marginal(b, kl, scr, a.n1, a.n2)
        ve = marginal(b, eq, scr, a.n1, a.n2)
        d = vl - v0
        print(f"{c:16s} {v0:12.3f} {vl:12.3f} {ve:12.3f} {d:+12.3f}  "
              + ("LEAKS" if abs(d) > 1e-9 else "constant in k"))
    return 0


def cmd_closed(a, scr):
    ta = fn_table(binary(a.a, a.mode), os.path.join(INDIR, a.input), scr,
                  a.n2, "a2")
    ta1 = fn_table(binary(a.a, a.mode), os.path.join(INDIR, a.input), scr,
                   a.n1, "a1")
    tb = fn_table(binary(a.b, a.mode), os.path.join(INDIR, a.input), scr,
                  a.n2, "b2")
    tb1 = fn_table(binary(a.b, a.mode), os.path.join(INDIR, a.input), scr,
                   a.n1, "b1")
    per = float(a.n2 - a.n1)
    ma = {k: (ta.get(k, 0) - ta1.get(k, 0)) / per for k in set(ta) | set(ta1)}
    mb = {k: (tb.get(k, 0) - tb1.get(k, 0)) / per for k in set(tb) | set(tb1)}
    keys = sorted(set(ma) | set(mb),
                  key=lambda k: -abs(ma.get(k, 0) - mb.get(k, 0)))
    tot = 0.0
    print(f"# CLOSED decomposition of ({a.a}) - ({a.b}) on {a.input} "
          f"[-O3 {a.mode}, marginal {a.n1}->{a.n2}]")
    print(f"{'function':70s} {a.a:>12s} {a.b:>12s} {'delta':>12s}")
    for k in keys:
        d = ma.get(k, 0) - mb.get(k, 0)
        tot += d
        if abs(d) > 1e-9:
            print(f"{k[:70]:70s} {ma.get(k, 0):12.4f} {mb.get(k, 0):12.4f} "
                  f"{d:+12.4f}")
    whole_a = marginal(binary(a.a, a.mode), os.path.join(INDIR, a.input), scr,
                       a.n1, a.n2)
    whole_b = marginal(binary(a.b, a.mode), os.path.join(INDIR, a.input), scr,
                       a.n1, a.n2)
    print(f"\nSUM OVER EVERY FUNCTION = {tot:.4f}")
    print(f"whole-program delta     = {whole_a - whole_b:.4f}")
    print(f"closed? {'YES' if abs(tot - (whole_a - whole_b)) < 0.01 else 'NO'}")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cells", default=None,
                    help="default: the 8 shipped cells, or the 12 rows of "
                         "NOTES.md 6 under --leak-controls")
    ap.add_argument("--inputs", default="small.bin,large.bin")
    ap.add_argument("--mode", required=True, choices=["isolated", "whole"])
    ap.add_argument("--n1", type=int, default=100)
    ap.add_argument("--n2", type=int, default=200)
    ap.add_argument("--leak-controls", action="store_true")
    ap.add_argument("--closed", action="store_true")
    ap.add_argument("--a")
    ap.add_argument("--b")
    ap.add_argument("--input", default="large.bin")
    a = ap.parse_args()
    if a.cells is None:
        a.cells = ",".join(LEAK_CELLS if a.leak_controls else CELLS)
    scr = os.path.join(REPO, ".temp", "p47", f"irt{os.getpid()}")
    os.makedirs(scr, exist_ok=True)
    try:
        if a.closed:
            return cmd_closed(a, scr)
        if a.leak_controls:
            return cmd_leak_controls(a, scr)
        return cmd_table(a, scr)
    finally:
        subprocess.run(["rm", "-rf", scr])


if __name__ == "__main__":
    sys.exit(main())
