#!/usr/bin/env python3
"""p29 CONTROLS: the R5 mutation battery, including THE ATTACK ARM.

`.memory/02-bench-rules.md`: *"Every temporal R5 owes an ATTACK arm that must
FAIL to verify, not just a deletion arm."* `p42`'s ghost ledger verified `18/0`
while leaking, and `TASK_137` sharpened the rule for `p29` specifically: the
`p42`-shaped risk here is **a fold transliterated from the kernel**, which would
verify `n/0` and prove the bug correct. So the battery below does two different
things:

  * **DELETION arms** ask whether a line the rung ships is load-bearing;
  * **ATTACK arms** put `c/kernel.c`'s ACTUAL BUG into the R5 and require the
    proof to reject it. `M3` is the one the row is about: it deletes the
    OCCUPANT-IDENTITY conjunct and nothing else, so the surviving program is
    exactly `p27`'s safety line applied to `p29`'s kernel.
  * **MUST-VERIFY controls** make sure a failure is caused by the mutation and
    not by an unachievable postcondition.

    python3 patterns/p29-bst-delete/controls/proof_mutants.py

⚠ Each arm is a full Verus run; budget a few minutes. Mutant sources are written
under `.temp/p29mut/` and deleted on success (`.memory/00-environment.md`
constraint 6) -- this file is the generator and it is what is committed.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
VERUS_RUN = os.path.join(REPO, "verus_run.py")
MDIR = os.path.join(REPO, ".temp", "p29mut")

SRC = os.path.join(PDIR, "verus.rs")

# ---------------------------------------------------------------- mutants ---
# (name, kind, expect, [(find, replace), ...], why)
LIVE_STORE = "                    arr_set_unchecked(&mut live, cur as usize, 0u8);"
USE_GUARD = ("            let v: u64 = if g_has && arr_get_unchecked(&live, "
             "g_slot as usize) == 1u8 {")
IDENT_TEST = """                if rr.key == g_key {
                    rr.val as u64
                } else {
                    SENT
                }"""
FOLD_TAIL = "    acc.wrapping_mul(31).wrapping_add(ntab as u64)\n}"

MUTANTS = [
    ("M0-control", "control", "verify", [],
     "the shipped file, run through the same harness. If this does not verify, "
     "nothing below means anything."),
    ("M1-live-store", "deletion", "fail", [(LIVE_STORE + "\n", "")],
     "delete `live[cur] = 0` after the free. `rec_free` has consumed slot "
     "`cur`'s permission and the liveness array would still claim it exists, so "
     "`wf` cannot be re-established. This is p27's M2 and it is the line "
     "c/kernel.c does NOT forget."),
    ("M2-liveness-conjunct", "attack", "fail",
     [(USE_GUARD, "            let v: u64 = if g_has {")],
     "THE ATTACK ARM, half one: delete the LIVENESS conjunct from the safety "
     "line, leaving the occupant-identity test alone. Its C twin is "
     "`controls/arms.py`'s `keyonly`, which fires ASan on every "
     "use-after-free window. ⚠ **The diagnostic here names the localising "
     "ghost assert (`assert(alive(st, g_slot))`), not the real obligation** -- "
     "`M2b` deletes the hint and shows what actually fails."),
    ("M3-identity-conjunct", "attack", "fail",
     [(IDENT_TEST, "                rr.val as u64")],
     "THE ATTACK ARM the row is about: delete the OCCUPANT-IDENTITY conjunct "
     "and nothing else. What survives is EXACTLY p27's safety line -- a "
     "liveness test on the read path -- applied to p29's kernel, and it is "
     "c/kernel.c's second bug class written into the R5. Linearity is "
     "satisfied -- nothing was deallocated -- and the FUNCTIONAL refinement is "
     "what rejects it. ⚠ **The diagnostic names the localising refinement "
     "assert**; `M3b` deletes the hint and shows the `run(..) == run(..)` "
     "equality failing instead."),
    ("M2b-liveness-no-hint", "attack", "fail",
     [(USE_GUARD, "            let v: u64 = if g_has {"),
      ("                assert(alive(st, g_slot));\n"
       "                assert(rec_ok(tab@, st, perms, g_slot as int));\n", "")],
     "`M2` with the two localising ghost asserts deleted, so the diagnostic "
     "names the real obligation rather than a hint. Measured: `precondition "
     "not satisfied` at `perms.tracked_borrow(g_slot as int)`. **The identity "
     "test cannot be EVALUATED without the liveness test** -- C's `&&` "
     "ordering, as a type-system fact."),
    ("M3b-identity-no-hint", "attack", "fail",
     [(IDENT_TEST, "                rr.val as u64"),
      ("            assert(st == step(st_in, c, a).0);\n"
       "            assert(acc == acc_in.wrapping_mul(31)"
       ".wrapping_add(step(st_in, c, a).1));\n", "")],
     "`M3` with the localising refinement asserts deleted. Measured: the "
     "`run(..) == run(..)` refinement equality fails. **Nothing linear "
     "objects** -- the splice deallocated nothing and every permission is "
     "where the invariant says it is; what rejects the program is the "
     "FUNCTIONAL postcondition alone."),
    ("M4-r1-line", "attack", "fail",
     [(USE_GUARD, "            let v: u64 = if g_has {"),
      (IDENT_TEST, "                rr.val as u64")],
     "c/kernel.c's line verbatim: both conjuncts gone. Fails for M2's reason "
     "before it can fail for M3's."),
    ("M5-fold-multiplier", "deletion", "fail",
     [(FOLD_TAIL, "    acc.wrapping_mul(29).wrapping_add(ntab as u64)\n}")],
     "change the fold's multiplier in the exec code only. The postcondition "
     "READS THE BODY -- a `run` that were vacuous would not notice."),
    ("M6-constant-body", "vacuity", "fail",
     [("        r == bst_fold(buf@, off as int, len as int),\n{\n    // Ghost only",
       "        r == bst_fold(buf@, off as int, len as int),\n{\n    return 0;\n    // Ghost only")],
     "`.memory/04-verus.md`'s vacuity probe in its sharp form -- **what is the "
     "CHEAPEST body that satisfies the postcondition?** `TASK_137` discharged "
     "`TASK_136`'s ARM_C with `fn arm_c() -> u8 { 9 }`. Here the cheapest body "
     "is `return 0;` and it must FAIL, because `bst_fold` is a function of the "
     "window bytes and no constant equals it."),
    ("M7-drop-walk-fuel", "deletion", "fail",
     [("    while cur != NIL && arr_get_unchecked(live, cur as usize) == 1u8 "
       "&& steps < TABCAP",
       "    while cur != NIL && arr_get_unchecked(live, cur as usize) == 1u8")],
     "delete the walk's step bound. It never fires at run time; it is the "
     "`decreases` measure, and without it the loop has no termination proof. "
     "This is the measured price of NOT proving the link structure is a tree."),
]


def run_verus(path):
    r = subprocess.run([sys.executable, VERUS_RUN, path],
                       capture_output=True, text=True, cwd=REPO, timeout=3600)
    txt = r.stdout + r.stderr
    m = re.search(r"verification results:: (\d+) verified, (\d+) errors", txt)
    kinds = sorted({ln.split("error:")[1].strip().split("\n")[0][:60]
                    for ln in txt.splitlines() if ln.startswith("error:")})
    if m:
        return {"verified": int(m.group(1)), "errors": int(m.group(2)),
                "rc": r.returncode, "error_kinds": kinds[:4]}
    return {"verified": None, "errors": None, "rc": r.returncode,
            "error_kinds": kinds[:4]}


def derived_from():
    out = {}
    for rel in ("patterns/p29-bst-delete/verus.rs",
                "patterns/p29-bst-delete/controls/proof_mutants.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    os.makedirs(MDIR, exist_ok=True)
    base = open(SRC).read()
    # the mutant lives one directory deeper, so the driver path shifts
    base = base.replace('#[path = "../../common/driver.rs"]',
                        '#[path = "../../common/driver.rs"]')
    rows = []
    for name, kind, expect, subs, why in MUTANTS:
        if a.only and a.only != name:
            continue
        txt = base
        for find, repl in subs:
            if find not in txt:
                raise SystemExit(f"proof_mutants: {name}: pattern not found in "
                                 f"verus.rs -- the file moved under this "
                                 f"script:\n{find[:120]}")
            txt = txt.replace(find, repl, 1)
        path = os.path.join(MDIR, f"{name}.rs")
        open(path, "w").write(txt)
        res = run_verus(path)
        got = "verify" if (res["errors"] == 0 and res["rc"] == 0) else "fail"
        ok = got == expect
        rows.append({"mutant": name, "kind": kind, "expected": expect,
                     "got": got, "ok": ok, **res, "why": why})
        print(f"  {name:22s} {kind:8s} expect={expect:6s} got={got:6s} "
              f"{'OK ' if ok else 'XX '} "
              f"{res['verified']}/{res['errors']} {res['error_kinds']}")
    doc = {"pin": {"regenerate":
                   "python3 patterns/p29-bst-delete/controls/proof_mutants.py"},
           "derived_from_sha256": derived_from(),
           "mutants": rows,
           "summary": {"n": len(rows), "as_expected": sum(r["ok"] for r in rows)}}
    out = os.path.join(HERE, "proof_mutants.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"{doc['summary']['as_expected']} of {doc['summary']['n']} "
          f"behaved as expected -> {out}")
    if all(r["ok"] for r in rows):
        shutil.rmtree(MDIR)
    else:
        print(f"(mutant sources kept in {MDIR} because something surprised us)")
    return 0 if all(r["ok"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
