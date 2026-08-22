#!/usr/bin/env python3
"""p38 proof mutants: edits to `verus.rs`'s EXEC code that Verus must reject.

`harness/check.py` mutates the *clauses* (5c, 5c-req, 5c-twin). This mutates the
**program**, which is the other half: a proof that verifies a broken kernel is a
proof of nothing.

⚠ **BOTH MUTANTS HERE ARE SPATIAL, AND THAT IS p38'S POINT RATHER THAN A GAP.**
p38's own defect -- a C compiler answering a `uint32_t` load from before a
`uint16_t` store -- has no Rust analogue to mutate, because Rust has no
type-based aliasing rule. What R5 buys on p38 is exactly what these two mutants
show: every unchecked read and the one unchecked write stay inside their
objects. ../NOTES.md 9 states that precisely.

    python3 patterns/p38-alias-pun/controls/proof_mutants.py
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p38", "mutants")
assert OUT.endswith(os.path.join("p38", "mutants")), OUT
VERUS_RUN = os.path.join(REPO, "verus_run.py")
SRC = os.path.join(PDIR, "verus.rs")

# name -> (list of (old, new) substitutions, why)
MUTANTS = {
    # A clamp that leaves room for ONE more 32-bit unit than the scratch holds.
    # Four characters. The payload fold then reads up to `nw + 2` and, on a
    # window that fills the scratch, past `SCRATCH_W`.
    #
    # The ghost `assert(n <= room)` is deleted WITH it, deliberately: that line
    # is a STEP in the proof of the bound, not a second check, so leaving it in
    # makes the mutant fail on `assertion failed` and a reader cannot tell
    # whether the memory-safety fact was ever at risk. Deleted, the mutant fails
    # on `invariant not satisfied before loop` -- the fold loop's
    # `i + 2 + 2 * n <= nw`, which IS the spatial fact.
    "m_clamp_off": (
        [("        if d > room {", "        if d > room + 1 {"),
         ("        assert(n <= room);\n", "")],
        "the clamp is one 32-bit unit too generous",
    ),
    # Delete the truncation of the record stream to the scratch. `nw` is then
    # `(len-4)/2`, which a long window makes larger than SCRATCH_W, and every
    # scratch access is out of the array.
    "m_no_trunc": (
        [("    if nw > SCRATCH_W {\n        nw = SCRATCH_W;\n    }\n", "")],
        "the record stream is not truncated to the scratch",
    ),
}


def run(name):
    subs, why = MUTANTS[name]
    src = open(SRC).read()
    for old, new in subs:
        if old not in src:
            raise SystemExit(f"proof_mutants.py: {name}: a substitution no "
                             f"longer matches verus.rs -- the mutant is stale")
        src = src.replace(old, new, 1)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{name}.rs")
    open(p, "w").write(src)
    r = subprocess.run([sys.executable, VERUS_RUN, p],
                       capture_output=True, text=True, timeout=1800)
    txt = r.stdout + r.stderr
    m = re.search(r"verification results:: (\d+) verified, (\d+) error", txt)
    verified, errors = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    kinds = sorted({ln.split("error: ")[1].strip()[:70]
                    for ln in txt.splitlines() if ln.startswith("error: ")})
    return verified, errors, kinds, why


def main():
    print("p38 proof mutants -- Verus must REJECT each of these\n")
    bad = 0
    for name in MUTANTS:
        v, e, kinds, why = run(name)
        ok = e is not None and e > 0
        print(f"{name:14s} {v} verified, {e} errors   "
              f"{'REJECTED (as required)' if ok else '*** VERIFIED -- BAD ***'}")
        print(f"               why: {why}")
        for k in kinds[:4]:
            print(f"               error: {k}")
        if not ok:
            bad += 1
    print(f"\nbaseline: the shipped verus.rs is 13 verified, 0 errors.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
