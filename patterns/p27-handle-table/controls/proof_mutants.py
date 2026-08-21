#!/usr/bin/env python3
"""p27's proof mutants: two edits to verus.rs that must FAIL to verify.

    python3 patterns/p27-handle-table/controls/proof_mutants.py [--out DIR] [--run]

Both are aimed at the TEMPORAL property rather than at a bound, which is what
makes them p27's rather than a copy of an earlier pattern's:

  M1  delete the liveness conjunct from the READ path -- `&& arr_get_unchecked(
      &live, h) == 1u8`. **This is c/kernel.c's bug, written in the rung that
      has to prove it.** `perms.tracked_borrow(h)` then has no
      `perms.dom().contains(h)` to present.

  M2  delete `arr_set_unchecked(&mut live, h, 0u8);` from the CLOSE path --
      **the line the C programmer forgot.** `rec_free` has consumed slot h's
      permission, the liveness array still claims the record exists, and the
      loop invariant `wf` cannot be re-established. M2 is what makes "the proof
      forces the line C forgot" a fact rather than a slogan.

⚠ The catcher in both is an ordinary Verus obligation -- a failed precondition or
a failed invariant -- and **NOT rustc's move checker**. TASK_055_REPORT §2.6's
`E0382` was an artefact of a hand-unrolled two-element probe and was retracted at
TASK_055_REVIEW M2: with a real permission map the permissions live in a `Map`
and are removed with `tracked_remove`, which is a mutation and not a move.
Linearity still does the work one level down, inside `Map`'s axioms, but it
surfaces as an SMT obligation like every other R5 in this tree.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PD))

M1_OLD = """            if h < ntab && arr_get_unchecked(&live, h) == 1u8 {
                assert(lv[h as int]);
                assert(slot_ok(tab@, vals, perms, dal, h as int));
                let tracked t = perms.tracked_borrow(h as int);"""
M1_NEW = """            if h < ntab {
                let tracked t = perms.tracked_borrow(h as int);"""

M2_OLD = """                // THE LINE THE C RUNG FORGOT. Without it the invariant below
                // cannot be re-established: `deallocate` has consumed slot
                // `h`'s permission and `live[h]` would still claim it exists.
                arr_set_unchecked(&mut live, h, 0u8);"""
M2_NEW = """                // THE LINE THE C RUNG FORGOT -- deleted. (mutant M2)"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO, ".temp", "p27", "mutants"))
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    src = open(os.path.join(PD, "verus.rs")).read()
    src = src.replace('#[path = "../../common/driver.rs"]',
                      '#[path = "%scommon/driver.rs"]'
                      % ("../" * os.path.relpath(REPO, a.out).count("..")))
    bad = 0
    for name, old, new in (("m1_no_liveness_test", M1_OLD, M1_NEW),
                           ("m2_no_invalidation", M2_OLD, M2_NEW)):
        if src.count(old) != 1:
            raise SystemExit(f"proof_mutants.py: {name}: lever matched "
                             f"{src.count(old)}x, expected 1")
        path = os.path.join(a.out, name + ".rs")
        open(path, "w").write(src.replace(old, new))
        print(f"  wrote {name}.rs")
        if a.run:
            r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), path],
                               capture_output=True, text=True, cwd=REPO, timeout=3600)
            out = (r.stdout + r.stderr)
            res = [l for l in out.splitlines() if "verification results" in l]
            errs = [l for l in out.splitlines() if l.startswith("error:")][:3]
            print(f"    {res[0] if res else 'NO RESULT LINE'}")
            for e in errs:
                print(f"    {e}")
            if res and ", 0 errors" in res[0]:
                print(f"    !! {name} VERIFIED -- the mutant is not load-bearing")
                bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
