#!/usr/bin/env python3
"""p46 — measure the sweep band and CHECK the laws published in `../NOTES.md` 8.

Two modes, and the second is the one that matters:

    controls/sweep_ir.py --measure --out sweep.json     # ~8 min, 8 cells x 49 blobs
    controls/sweep_ir.py --check   --data sweep.json    # exits 1 on any residual

`--check` re-derives every published law from the measured marginals and **exits
non-zero if a single residual is non-zero**. That is the one command that
carries a change from the shipped binaries all the way to the numbers a reader
quotes (`RECAP`: *"ask which single command carries a change from the source all
the way to the number a reader quotes"*).

CONVENTION, and it is the whole basis of the arithmetic below: **whole-program
marginal `Ir` per kernel call**, `(Ir @ hi iters - Ir @ lo) / (hi - lo)`, with
`n_iters` rewritten at offset 0 of the input file exactly as
`harness/check.py::_probe_input` does. `-O3`, inline mode **`isolated`**.

The absolute marginals are NOT integers: the driver prints a different checksum
at 100 and at 200 iterations, and `.tasks/TASK_026.md` §0 item 2 measures that
term at 0.2263 Ir per call per digit. **Every law here is a DIFFERENCE of two
cells on ONE input**, where both cells print the same checksum, so the term
cancels exactly and every value the laws are fitted to is an integer. `--check`
asserts that too.

⚠ **A probe measures a SLOPE and its INTERCEPT is a property of the probe**
(`.memory/03-measurement.md`). On p46 not even the slope transferred -- see
`../NOTES.md` 0b -- so this file only ever reads `.temp/build/p46/*-O3-isolated`,
the binaries `harness/build.py` produced.
"""
import argparse
import glob
import json
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
IN = os.path.join(PDIR, "inputs")
BUILD = os.path.join(REPO, ".temp", "build", "p46")
SCRATCH = os.path.join(REPO, ".temp", "check", "p46-sweep")
VG = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CELLS = ["c-gcc", "c-clang", "c-gcc-h", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]


# ----------------------------------------------------------- measurement ----
def probe_input(srcp, n_iters):
    os.makedirs(SCRATCH, exist_ok=True)
    out = os.path.join(SCRATCH, f"{os.path.basename(srcp)}.{n_iters}")
    blob = open(srcp, "rb").read()
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n_iters) + blob[8:])
    return out


def total_ir(binary, arg):
    cg = os.path.join(SCRATCH, f"cg.{os.getpid()}")
    r = subprocess.run([VG, "--tool=callgrind", f"--callgrind-out-file={cg}",
                        binary, arg], capture_output=True, text=True)
    try:
        os.unlink(cg)
    except OSError:
        pass
    m = re.search(r"refs:\s+([\d,]+)", r.stderr)
    if not m:
        sys.exit(f"sweep_ir.py: no Ir for {binary} {arg}:\n{r.stderr[-1200:]}")
    return int(m.group(1).replace(",", ""))


def marginal(binary, srcp, lo=100, hi=200):
    return (total_ir(binary, probe_input(srcp, hi))
            - total_ir(binary, probe_input(srcp, lo))) / (hi - lo)


def nm_of(path):
    m = re.match(r"sweep-n(\d+)m(\d+)\.bin", os.path.basename(path))
    return (int(m.group(1)), int(m.group(2))) if m else None


def measure(cells, out):
    blobs = sorted(glob.glob(os.path.join(IN, "sweep-*.bin")))
    if not blobs:
        sys.exit("sweep_ir.py: no sweep blobs; run `inputs/gen.py --sweep`")
    data = {}
    for cell in cells:
        b = os.path.join(BUILD, f"{cell}-O3-isolated")
        if not os.path.exists(b):
            sys.exit(f"sweep_ir.py: {b} not built; run "
                     f"`harness/build.py p46 --all --opt O3 --mode isolated`")
        data[cell] = {}
        for p in blobs:
            n, m = nm_of(p)
            v = marginal(b, p)
            data[cell][f"{n},{m}"] = v
            print(f"  {cell:11s} n={n:3d} m={m:3d}  {v:12.2f}", flush=True)
    json.dump(data, open(out, "w"), indent=1)
    print(f"wrote {out}")


# ------------------------------------------------------------- the laws ----
#: `../NOTES.md` 8. DOMAIN: m >= 2 (see 8c).
def law_R2_R4(n, m):
    return 3 + 5 * n - n * (m // 2)


def law_R3_R2(n, m):
    return (2 * n - 2) if m % 2 == 0 else -2


def law_R3_R4(n, m):
    return law_R2_R4(n, m) + law_R3_R2(n, m)


def law_R5_R4(n, m):
    return 0


LAWS = [
    ("R5 - R4  =  0",
     "verus", "unsafe", law_R5_R4, 1),
    ("R2 - R4  =  3 + 5n - n*floor(m/2)",
     "safe_naive", "unsafe", law_R2_R4, 2),
    ("R3 - R2  =  2n - 2 (m even) / -2 (m odd)",
     "safe_tuned", "safe_naive", law_R3_R2, 2),
    ("R3 - R4  =  (R2-R4) + (R3-R2)",
     "safe_tuned", "unsafe", law_R3_R4, 2),
]


def check(data):
    bad = 0
    keys = sorted(data["unsafe"], key=lambda s: tuple(int(x) for x in s.split(",")))
    # (i) every difference used below must be an exact integer.
    for _, a, b, _, _ in LAWS:
        for k in keys:
            d = data[a][k] - data[b][k]
            if abs(d - round(d)) > 1e-9:
                print(f"FAIL non-integral difference {a}-{b} at {k}: {d}")
                bad += 1
    # (ii) every law, on its stated domain, with zero residual.
    for label, a, b, f, mmin in LAWS:
        used = worst = 0
        for k in keys:
            n, m = (int(x) for x in k.split(","))
            if m < mmin:
                continue
            used += 1
            r = (data[a][k] - data[b][k]) - f(n, m)
            worst = max(worst, abs(r))
            if abs(r) > 1e-9:
                print(f"FAIL {label}: n={n} m={m} residual {r}")
                bad += 1
        print(f"{'ok  ' if worst == 0 else 'FAIL'} {label:46s} "
              f"{used:2d} blob(s), m >= {mmin}, max |residual| = {worst:.5f}")
    # (iii) the two C rungs' hardening cost, WITH its measured exceptions.
    for cc in ("gcc", "clang"):
        vals = {}
        for k in keys:
            vals.setdefault(round(data[f"c-{cc}-h"][k] - data[f"c-{cc}"][k], 6),
                            []).append(k)
        pretty = ", ".join(f"{v:+.2f} on {len(ks)}"
                           for v, ks in sorted(vals.items()))
        odd = {v: ks for v, ks in vals.items() if len(ks) < len(keys) / 2}
        print(f"note R1h - R1, {cc:5s}: {pretty}"
              + (f"   exception(s) at {sorted(x for ks in odd.values() for x in ks)}"
                 if odd else ""))
    # (iv) the domain restriction is real and is stated, not hidden.
    if "24,1" in keys:
        n, m = 24, 1
        print(f"note m = 1 is OFF the laws' domain (../NOTES.md 8c): "
              f"R2-R4 measured {data['safe_naive']['24,1'] - data['unsafe']['24,1']:.2f}, "
              f"law would say {law_R2_R4(n, m)}")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--cells", nargs="*", default=CELLS)
    ap.add_argument("--out", default=os.path.join(REPO, ".temp", "t89", "sweepfit.json"))
    ap.add_argument("--data", default=os.path.join(REPO, ".temp", "t89", "sweepfit.json"))
    a = ap.parse_args()
    if a.measure:
        measure(a.cells, a.out)
    if a.check:
        if not os.path.exists(a.data):
            sys.exit(f"sweep_ir.py: {a.data} not found; run --measure first")
        bad = check(json.load(open(a.data)))
        if bad:
            sys.exit(f"{bad} residual(s) -- ../NOTES.md 8's laws no longer "
                     f"describe the shipped binaries")
        print("\nevery law in ../NOTES.md 8 reproduces with zero residual.")
    if not (a.measure or a.check):
        ap.print_help()


if __name__ == "__main__":
    main()
