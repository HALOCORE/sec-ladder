#!/usr/bin/env python3
"""ph52 control: THE BLOB `inputs/` IS NOT ALLOWED TO CARRY.

    python3 patterns-php/ph52-concat-copy-uninit/controls/firstcall.py

⚠⚠ **WHY THIS FILE EXISTS.** `inputs/gen.py` carries, in the comment that explains the
one adversarial blob the row does NOT ship:

    "It lives in `controls/firstcall.py`, which runs it across all 16 cells and
     reports the spread."

and **`inputs/gen.py` IS IN THE MEASUREMENT DIGEST**, so correcting that pointer costs a
32-cell re-measure (`.memory-php/04-process.md` law 14). The arm itself is implemented
as `controls/negatives.py --firstcall`, which is where the blob generator, the 16-cell
build matrix and the R1-vs-R1h observable live. ▶ **`controls/*` is gate-only, so
writing the named file as the documented entry point costs ONE re-gate.**
`TASK_PHP_045_REPORT.md` §17 records it with the other three.

⚠ It is NOT a second implementation: two copies of a measurement is how they disagree.

**What the arm measures, restated so this file is readable on its own:** a window whose
op 0 carries the faulting arm makes `Zend/zend.c:243` read whatever the C runtime's own
startup left at that stack offset — measured as `0` in 12 of 16 build cells and as
`235` / `94` / `113` / `82` in the other four. ▶ That is a blob whose u64 is **not a
function of the blob**, so it cannot be an `inputs/` file in a tree whose gate compares
six rungs' checksums — which is `inputs/gen.py`'s rule **R1**. ⭐ The observable that
says whether the residue was one of the 12 freeing tag values is **R1 against R1h**:
R1h has no `:243` at all, so they agree iff `zval_dtor` no-opped.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import negatives  # noqa: E402

if __name__ == "__main__":
    fails = negatives.arm_firstcall()
    for f in fails:
        print(f"  FAIL {f}")
    print("  AS EXPECTED" if not fails else f"  {len(fails)} FAILURE(S)")
    sys.exit(1 if fails else 0)
