#!/usr/bin/env python3
"""What do callgrind's simulators see across a layout mode boundary?

`.memory/00-environment.md` once said "the simulators are blind to code
layout".  They are not blind: with `--cache-sim=yes --branch-sim=yes` every
cache counter and `Bcm` MOVES across a mode boundary.  They are blind to the
FRONT END -- no model of instruction fetch, the uop cache or the JCC
mitigation, which is where 100% of the effect lives -- so they move by <=6
events in 10^8 across a 27% wall-clock mode.

Use them to attribute a cache or branch mechanism; never to detect or rank a
layout effect.  This builds a minimal pair per entry in `PAIRS` (same source,
two `-align-all-functions` values, `md5_fn_norel` identical) and diffs the
whole-program totals.

    python3 common/layout/modesim2.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import loopfit  # noqa: E402

RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VG = os.path.expanduser("~/tools/valgrind/bin/valgrind")
BASE = ["--edition", "2021", "-C", "codegen-units=1", "-C", "opt-level=3",
        "-C", "debug-assertions=off", "--cfg", "slb_isolated"]

# (pattern, cell, alignK-slow, alignK-fast) -- residues verified with loopfit
PAIRS = [("p07-binary-search", "safe_naive", 1, 2),
         ("p01-array-sum", "safe_tuned", 1, 3),
         ("p01-array-sum", "unsafe", 1, 3)]


def counters(binary, inp, scr):
    out = os.path.join(scr, "cg.out")
    subprocess.run([VG, "--tool=callgrind", "--cache-sim=yes",
                    "--branch-sim=yes", f"--callgrind-out-file={out}",
                    binary, inp], capture_output=True, cwd=REPO)
    ev, tot = None, None
    for line in open(out):
        if line.startswith("events:"):
            ev = line.split()[1:]
        if line.startswith(("summary:", "totals:")):
            tot = [int(x) for x in line.split()[1:]]
    return dict(zip(ev, tot))


def main():
    scr = os.path.join(REPO, ".temp", "layout", f"ms.{os.getpid()}")
    os.makedirs(scr, exist_ok=True)
    for pattern, cell, kslow, kfast in PAIRS:
        pdir = os.path.join(REPO, "patterns", pattern)
        inp = os.path.join(pdir, "inputs", "small.bin")
        got = {}
        for tag, k in (("A", kslow), ("B", kfast)):
            dst = os.path.join(scr, f"{cell}.{tag}")
            r = subprocess.run(
                [RUSTC] + BASE + ["-C", f"llvm-args=-align-all-functions={k}",
                                  os.path.join(pdir, cell + ".rs"), "-o", dst],
                capture_output=True, text=True, cwd=REPO)
            if r.returncode:
                print((r.stdout + r.stderr)[-300:])
                return 1
            got[tag] = (dst, loopfit.kernel_report(dst))
        (ba, ra), (bb, rb) = got["A"], got["B"]
        print(f"\n### {pattern} {cell}   -align-all-functions={kslow} vs "
              f"={kfast}")
        for tag, r in (("A", ra), ("B", rb)):
            geo = " ".join(f"loop{i}(w{L['win32']},j{L['jcc32']})"
                           for i, L in enumerate(r["loops"]))
            print(f"  {tag}: {r['addr']:#x} %32={r['addr']%32} "
                  f"n_fn={r['n_fn']} md5_fn_norel={r['md5_fn_norel']}  {geo}")
        print(f"  same machine code (md5_fn_norel): "
              f"{ra['md5_fn_norel'] == rb['md5_fn_norel']}   "
              f"kernel moved {rb['addr']-ra['addr']:+d} bytes")
        ca, cb = counters(ba, inp, scr), counters(bb, inp, scr)
        print(f"  {'event':6s} {'A (whole prog)':>16s} {'B':>16s} "
              f"{'delta':>12s} {'rel':>9s}")
        for e in ca:
            d = cb[e] - ca[e]
            rel = 100.0 * d / ca[e] if ca[e] else 0.0
            flag = "   <-- MOVES" if abs(rel) > 0.05 else ""
            print(f"  {e:6s} {ca[e]:16d} {cb[e]:16d} {d:+12d} "
                  f"{rel:+8.4f}%{flag}")
    subprocess.run(["rm", "-rf", scr])
    return 0


if __name__ == "__main__":
    sys.exit(main())
