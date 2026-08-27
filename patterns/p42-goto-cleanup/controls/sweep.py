#!/usr/bin/env python3
"""p42 control 5 -- the per-element rate, FITTED ON ONE BAND AND TESTED ON ANOTHER.

`.tasks/PROTOCOL.md`'s newest lesson, from p23: **a law owes an OUT-OF-BAND
prediction, not a within-band holdout.**  p23 published three mutually
inconsistent "exact" laws, each with zero in-sample residual, and the one that
shipped mispredicted its own two committed inputs by up to 152 Ir/call.  Two
points and a slope through them is not a law; it is a slope through two points.

So this script fits `Ir/call = a + b*win_len` on **band A (win_len 64..79)** and
then PREDICTS:

  * **band B (win_len 512..527)** -- 448 away, all four residues mod 4;
  * **`small.bin`** (win_len 97), a SHIPPED input, on the same 4096-word array;
  * **`large.bin`** (win_len 4096), the other shipped input -- ⚠ on a DIFFERENT
    array (1 000 000 words instead of 4096), so a miss there is a statement
    about the memory system, not about the model, and this script says so.

The residuals are the result.  If band A predicts band B and `small` to within
a couple of instructions, the rate is a rate.  If it does not, the intercept is
not a constant of this row -- and there is a specific reason to expect it might
not be: the kernel calls `malloc`/`free` once per call with a size that IS the
window length, so the allocator's size class changes underneath the fit.

  python3 patterns/p42-goto-cleanup/controls/sweep.py [cell ...]

Cells default to the six measured ones.  Binaries come from `.temp/build/p42`,
so run `harness/build.py p42` first.
"""

import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
BUILD = os.path.join(REPO, ".temp", "build", "p42")
OUT = os.path.join(REPO, ".temp", "t104", "sweep")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CELLS = ["c-gcc", "c-gcc-h", "c-clang", "safe_naive", "safe_tuned", "unsafe", "verus"]
BAND_A = list(range(64, 80))
BAND_B = list(range(512, 528))


def marginal(binary, inp):
    """(Ir at 200 iters - Ir at 100 iters) / 100 -- the project's convention."""
    tot = []
    for n in (100, 200):
        f = os.path.join(OUT, f"it{n}.bin")
        b = bytearray(open(inp, "rb").read())
        struct.pack_into("<Q", b, 0, n)
        open(f, "wb").write(bytes(b))
        cg = os.path.join(OUT, "cg.out")
        subprocess.run([VALGRIND, "--tool=callgrind", f"--callgrind-out-file={cg}",
                        binary, f], capture_output=True, timeout=3600)
        tot.append(int([l for l in open(cg) if l.startswith("summary:")][0].split()[1]))
        os.remove(cg)
    return (tot[1] - tot[0]) / 100.0


def fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    return my - b * mx, b


def main():
    os.makedirs(OUT, exist_ok=True)
    cells = sys.argv[1:] or CELLS
    for cell in cells:
        binary = os.path.join(BUILD, f"{cell}-O3-isolated")
        if not os.path.exists(binary):
            print(f"{cell}: no {binary}; run harness/build.py p42")
            continue
        a_pts = [(w, marginal(binary, os.path.join(PDIR, "inputs", f"sweep-w{w}.bin")))
                 for w in BAND_A]
        a, b = fit([w for w, _ in a_pts], [y for _, y in a_pts])
        res_a = max(abs(y - (a + b * w)) for w, y in a_pts)
        print(f"\n== {cell} ==  -O3, inline mode `isolated`, whole-program marginal")
        print(f"   band A fit (win 64..79):  Ir/call = {a:.3f} + {b:.5f} * win_len"
              f"   max |in-sample residual| = {res_a:.3f}")
        worst = 0.0
        for w in BAND_B:
            y = marginal(binary, os.path.join(PDIR, "inputs", f"sweep-w{w}.bin"))
            r = y - (a + b * w)
            worst = max(worst, abs(r))
            print(f"   band B  win={w:5d}  measured {y:12.2f}  predicted "
                  f"{a + b * w:12.2f}  residual {r:+10.2f}")
        for nm, w, note in (("small.bin", 97, "same 4096-word array"),
                            ("large.bin", 4096, "DIFFERENT array: 1 000 000 words")):
            y = marginal(binary, os.path.join(PDIR, "inputs", nm))
            r = y - (a + b * w)
            print(f"   SHIPPED {nm:10s} win={w:5d}  measured {y:12.2f}  predicted "
                  f"{a + b * w:12.2f}  residual {r:+10.2f}   ({note})")
        print(f"   worst band-B residual: {worst:.2f} Ir/call")
    return 0


if __name__ == "__main__":
    sys.exit(main())
