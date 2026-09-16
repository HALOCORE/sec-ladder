#!/usr/bin/env python3
"""ph66 control -- ⭐⭐⭐ THE ROW'S HEADLINE, MEASURED: what every rung returns
on every input, side by side.

    python3 patterns-php/ph66-hashdel-uncompared/controls/ladder.py
    python3 patterns-php/ph66-hashdel-uncompared/controls/ladder.py --selftest

============================================================================
WHY A TABLE AND NOT A SENTENCE
============================================================================
The gate's stage 2 requires every cell to agree with `model.py` on the
NON-adversarial inputs, and its stage 4 RECORDS adversarial behaviour per rung
without requiring agreement. Neither prints the one thing this row exists to
show:

  ⭐ **R1 = R2 = R3 = R4 = R5 on the ADVERSARIAL inputs too, and only R1h
  differs.**

That is prediction P1, and `CLAUDE.md` Don't 6 makes it a FINDING rather than a
kill: a wrong boolean is expressible in safe Rust, in `unsafe` Rust and in
Verus, so no safety rung addresses it and the whole stack is blind. A ladder
whose every rung buys safety is a ladder that has never measured a defect the
rungs do not address.

⚠ It reads the GATE'S OWN BINARIES out of the shim build root rather than
building its own, so the table is about the cells the measurement record was
taken from and not about a second compilation with different flags. Run
`python3 harness-php/gate.py --tool build ph66-hashdel-uncompared --all` first.

⛔ `--selftest` is the half that makes it evidence (`§H`): it requires the five
defective rungs to AGREE on every input, requires R1h to DIFFER on at least one
adversarial input, and requires R1h to AGREE on every measured one -- the last
being exactly what the gate's stage 7h enforces from the other side, so a
silent corpus drift shows up here as well as there.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

BUILD = os.path.join(REPO, ".temp", "php-scratch", "build", "ph66")
#: rung -> the build.py cell name. The two C cells are the SAME kernel through
#: two compilers; `c-gcc` is the one the table names R1.
RUNGS = [("R1  c/kernel.c (gcc)", "c-gcc"),
         ("R1  c/kernel.c (clang)", "c-clang"),
         ("R2  safe_naive.rs", "safe_naive"),
         ("R3  safe_tuned.rs", "safe_tuned"),
         ("R4  unsafe.rs", "unsafe"),
         ("R5  verus.rs", "verus"),
         ("R1h c/kernel_hardened.c (gcc)", "c-gcc-h"),
         ("R1h c/kernel_hardened.c (clang)", "c-clang-h")]
DEFECTIVE = [c for _, c in RUNGS if not c.endswith("-h")]
HARDENED = [c for _, c in RUNGS if c.endswith("-h")]


def inputs():
    d = os.path.join(ROW, "inputs")
    return sorted(f for f in os.listdir(d) if f.endswith(".bin"))


def run(cell, inp, opt="O3", mode="isolated"):
    exe = os.path.join(BUILD, f"{cell}-{opt}-{mode}")
    if not os.path.exists(exe):
        raise SystemExit(f"no binary at {exe} -- run `python3 harness-php/"
                         f"gate.py --tool build ph66-hashdel-uncompared --all`")
    r = subprocess.run([exe, os.path.join(ROW, "inputs", inp)],
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout.strip()


def table(opt="O3", mode="isolated"):
    out = {}
    for inp in inputs():
        out[inp] = {}
        for _, cell in RUNGS:
            out[inp][cell] = run(cell, inp, opt, mode)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--opt", default="O3")
    ap.add_argument("--mode", default="isolated")
    a = ap.parse_args()

    t = table(a.opt, a.mode)
    ins = inputs()
    print(f"  cells built at {a.opt}/{a.mode}; every value is the u64 on stdout, "
          f"every rc is 0\n")
    w = max(len(n) for n, _ in RUNGS)
    print(f"  {'rung':<{w}} " + "".join(f"{i.replace('.bin',''):>22}" for i in ins))
    for name, cell in RUNGS:
        row = "".join(f"{t[i][cell][1]:>22}" for i in ins)
        print(f"  {name:<{w}} {row}")

    problems = []
    for i in ins:
        rcs = {t[i][c][0] for _, c in RUNGS}
        if rcs != {0}:
            problems.append(f"{i}: some cell exited non-zero ({sorted(rcs)}) -- "
                            f"this row's target error is a VALUE and every cell "
                            f"must exit 0 on every input")
        vals = {t[i][c][1] for c in DEFECTIVE}
        if len(vals) != 1:
            problems.append(f"{i}: the five DEFECTIVE rungs disagree: "
                            f"{sorted(vals)} -- P1 says they must not")
        hv = {t[i][c][1] for c in HARDENED}
        if len(hv) != 1:
            problems.append(f"{i}: the two R1h cells disagree: {sorted(hv)}")
    adv = [i for i in ins if i.startswith("adversarial")]
    ben = [i for i in ins if not i.startswith("adversarial")]
    moved = [i for i in adv
             if t[i][DEFECTIVE[0]][1] != t[i][HARDENED[0]][1]]
    if not moved:
        problems.append("NO adversarial input separates R1 from R1h -- the row "
                        "would be measuring nothing")
    same = [i for i in ben if t[i][DEFECTIVE[0]][1] == t[i][HARDENED[0]][1]]
    if len(same) != len(ben):
        problems.append("R1 and R1h disagree on a MEASURED input, which stage "
                        "7h fails and which makes the R1-vs-R1h cost comparison "
                        "a comparison of two different programs")

    print(f"\n  five defective rungs agree on {len(ins)} of {len(ins)} inputs: "
          f"{'YES' if not any('DEFECTIVE' in p or 'disagree' in p for p in problems) else 'NO'}")
    print(f"  R1h differs on {len(moved)} of {len(adv)} adversarial inputs: "
          f"{[m.replace('.bin','') for m in moved]}")
    print(f"  R1h agrees on {len(same)} of {len(ben)} measured inputs")

    if a.selftest:
        print()
        for n, ok, why in (
            ("N1", not problems,
             "the five defective rungs agree everywhere, R1h separates on at "
             "least one adversarial input, and R1h agrees on every measured one"),
            ("N2", len(moved) >= 3,
             f"at least three adversarial inputs separate the two C rungs "
             f"({len(moved)}), so the separation is not one lucky window"),
            ("N3", len(set(t[i][DEFECTIVE[0]][1] for i in adv)) == len(adv),
             "every adversarial input produces a DISTINCT u64, so no two of "
             "them are the same draw under different names (F119/M4)"),
        ):
            print(f"  {'PASS' if ok else 'FAIL'}  {n}: {why}")
            if not ok:
                problems.append(f"{n} failed")
        print("\nSELFTEST " + ("FAIL" if problems else "PASS"))

    rec = {"opt": a.opt, "mode": a.mode,
           "table": {i: {c: t[i][c][1] for _, c in RUNGS} for i in ins},
           "defective_rungs_agree_on": len(ins) - sum(
               1 for i in ins if len({t[i][c][1] for c in DEFECTIVE}) != 1),
           "inputs": len(ins),
           "adversarial_separating": [m for m in moved],
           "problems": problems}
    rec.update(_pin.pin(["spec.md", "c/kernel.c", "c/kernel_hardened.c",
                         "safe_naive.rs", "safe_tuned.rs", "unsafe.rs",
                         "verus.rs", "model.py"],
                        "python3 controls/ladder.py --selftest",
                        "needs `gate.py --tool build <row> --all` first; seconds"))
    with open(os.path.join(HERE, "ladder.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"wrote controls/ladder.json -- {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
