#!/usr/bin/env python3
"""p32 CONTROLS: the R5 mutation battery, including THE ATTACK ARM, a VACUITY
arm, and **an arm that is supposed to VERIFY and whose verifying is the
finding**.

`.memory/02-bench-rules.md`: *"Every temporal R5 owes an ATTACK arm that must
FAIL to verify, not just a deletion arm."* Two instances in this project's own
history say why: `p42`'s ghost ledger verified `18/0` while leaking, and
`TASK_136`'s ARM_C was discharged by `fn arm_c() -> u8 { 9 }`. So:

  * **ATTACK arms** put `c/kernel.c`'s ACTUAL BUG into the R5 and require the
    proof to reject it. `M1` is the one the row is about: it deletes the
    generation conjunct and nothing else, so the surviving program IS
    `c/kernel.c`.
  * **VACUITY arms** ask what the CHEAPEST body satisfying the postcondition is.
    `M2` is `return 0;`, i.e. `TASK_136`'s `fn arm_c() -> u8 { 9 }` in this
    file's terms, and it must FAIL.
  * **DELETION arms** ask whether a line the rung ships is load-bearing.
  * ⚠⚠ **`M4-spec-weaken` MUST VERIFY, AND THAT IS THE POINT OF THE
    BATTERY.** It deletes the generation conjunct from the exec code AND from
    the abstract machine `step`, so the two agree again. It verifies `15/0`.
    **That is the honest measurement of what this R5 buys: the safety line is
    load-bearing against the SPECIFICATION and against nothing else.** Nothing
    in the proof system forces it -- there is no allocation, so there is no
    `PointsTo` to consume and no precondition to discharge -- which is the
    opposite of `p29`, where deleting `live[cur] = 0` makes the invariant
    unprovable no matter what the spec says. ../NOTES.md 6b.
  * ⚠⚠⚠ **AND `M4` IS ONLY A RESULT BESIDE `M1` AND `X3-spec-only-weaken`.**
    Three cells of one experiment: **exec-only -> FAIL** (`M1`), **spec-only ->
    FAIL** (`X3`), **both -> VERIFY** (`M4`). Until `TASK_147` the battery
    shipped the first and the third and asserted the conclusion; `X3` is the one
    that rules out *"`step`'s conjunct is inert"*, and it was found by
    `TASK_145`'s review, not by this file.
  * **MUST-VERIFY controls** (`M0`) make sure a failure is caused by the
    mutation and not by an unachievable postcondition or a broken harness.

    python3 patterns/p32-free-list-pool/controls/proof_mutants.py

⚠ Each arm is a full Verus run; budget a few minutes. Mutant sources are written
under `.temp/p32mut/` and deleted on success (`.memory/00-environment.md`
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
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
VERUS_RUN = os.path.join(REPO, "verus_run.py")
MDIR = os.path.join(REPO, ".temp", "p32mut")

SRC = os.path.join(PDIR, "verus.rs")

# ---------------------------------------------------------------- mutants ---
EXEC_GUARD = """            if h == NIL {
                SENT
            } else if arr_get_unchecked(&gen, h as usize) != g {
                SENT
            } else if c % 4 == 1 {"""
EXEC_NOGUARD = """            if h == NIL {
                SENT
            } else if c % 4 == 1 {"""
SPEC_GUARD = """        if h == NIL {
            (st, SENT)
        } else if st.gen[h as int] != g {
            (st, SENT)
        } else if c % 4 == 1 {"""
SPEC_NOGUARD = """        if h == NIL {
            (st, SENT)
        } else if c % 4 == 1 {"""
NIL_TEST = """            if h == NIL {
                SENT
            } else if arr_get_unchecked(&gen, h as usize) != g {"""
NIL_TEST_GONE = """            if false {
                SENT
            } else if arr_get_unchecked(&gen, h as usize) != g {"""
KERNEL_OPEN = ("        r == pool_fold(buf@, off as int, len as int),\n{\n"
               "    // Ghost only")
KERNEL_CONST = ("        r == pool_fold(buf@, off as int, len as int),\n{\n"
                "    return 0;\n    // Ghost only")
NX_INIT = ("        arr_set_unchecked(&mut nx, j, if j + 1 < SLOTS "
           "{ (j + 1) as u8 } else { NIL });")
FREEHEAD_INV = ("            wf_ranges(\n"
                "                St {\n"
                "                    pool: pool@,\n"
                "                    nx: nx@,\n"
                "                    gen: gen@,\n"
                "                    rs: regs@,\n"
                "                    rg: regg@,\n"
                "                    head: freehead,\n"
                "                    nalloc: nalloc as int,\n"
                "                },\n"
                "            ),\n")

# (name, kind, expect, [(find, replace), ...], why)
MUTANTS = [
    ("M0-control", "control", "verify", [],
     "the shipped file, run through the same harness. If this does not verify, "
     "nothing below means anything."),
    ("M1-generation-conjunct", "attack", "fail",
     [(EXEC_GUARD, EXEC_NOGUARD)],
     "THE ATTACK ARM, and it is the row's bug exactly: delete `gen[h] != g` "
     "from the exec code and nothing else. What survives is `c/kernel.c` -- a "
     "kernel that double-frees a recycled block, self-loops its own free list "
     "and hands out two aliased handles. It must FAIL, and it fails on the "
     "POSTCONDITION: the loop stops computing `run`."),
    ("M2-constant-body", "vacuity", "fail", [(KERNEL_OPEN, KERNEL_CONST)],
     "`.memory/04-verus.md`'s vacuity probe in its sharp form -- **what is the "
     "CHEAPEST body that satisfies the postcondition?** `TASK_137` discharged "
     "`TASK_136`'s ARM_C with `fn arm_c() -> u8 { 9 }`. Here the cheapest body "
     "is `return 0;` and it must FAIL, because `pool_fold` is a function of the "
     "window bytes and no constant equals it."),
    ("M3-nil-test", "attack", "fail", [(NIL_TEST, NIL_TEST_GONE)],
     "the OTHER half of the guard: make `h == NIL` unreachable, so an empty "
     "handle register is decoded as slot 255. It must FAIL, and ⚠ **it "
     "is the one arm here that fails for a MEMORY-SAFETY reason** -- `gen[255]` "
     "is out of an 8-element array and `wf_ranges` is what the unchecked read "
     "needs. Kept precisely to show the contrast with M1, which fails for a "
     "functional one."),
    ("M4-spec-weaken", "must-verify", "verify",
     [(EXEC_GUARD, EXEC_NOGUARD), (SPEC_GUARD, SPEC_NOGUARD)],
     "⚠⚠⚠ **THE ARM THAT IS SUPPOSED TO VERIFY.** Delete the "
     "generation conjunct from the exec code AND from `step`, so the "
     "specification describes the BUGGY kernel. It verifies. **That is the "
     "honest statement of what this R5 buys**: the safety line is load-bearing "
     "against the SPECIFICATION and against nothing else, because p32 allocates "
     "nothing and therefore has no linear resource whose consumption could "
     "force it. Compare p29, whose `live[cur] = 0` cannot be deleted at any "
     "price -- `rec_free` has consumed the permission and no spec change brings "
     "it back. `p42` is the precedent for shipping this as a finding. ⚠ Read "
     "it with X3-spec-only-weaken below: M1, X3 and M4 are three cells of ONE "
     "experiment and M4 alone is an assertion."),
    ("X3-spec-only-weaken", "attack", "fail", [(SPEC_GUARD, SPEC_NOGUARD)],
     "⚠⚠ **THE THIRD CELL, and it is what turns M4 from an assertion into a "
     "result.** Delete `st.gen[h] != g` from the abstract machine `step` ONLY, "
     "leaving the exec code intact -- a postcondition true of the WRONG "
     "program. It must FAIL, and it does. With M1 (exec only -> fail) and M4 "
     "(both -> verify) that gives EXEC-ONLY FAIL / SPEC-ONLY FAIL / BOTH "
     "VERIFY, which is the difference between *the proof does not care about "
     "the safety line* -- false -- and *the safety line is load-bearing "
     "against the specification and against nothing else* -- true. `step`'s "
     "conjunct is NOT inert; the two sides are tied to each other and to "
     "nothing outside. ⚠ This arm is `TASK_145_REPORT` §3's `X3`, kept under "
     "the reviewer's name so that citation resolves; the shipped battery "
     "lacked it, and its verdict here is RE-DERIVED by this script rather "
     "than quoted from that report."),
    ("M5-freehead-range", "deletion", "fail", [(FREEHEAD_INV, "")],
     "delete the whole range invariant from the loop. `freehead`, `nx[]` and "
     "`regs[]` are then unconstrained and every unchecked index loses its "
     "licence. This is the invariant that makes R1 memory-safe too, which is "
     "why ASan says nothing about the shipped bug."),
    ("M6-nx-init", "deletion", "fail", [(NX_INIT + "\n", "")],
     "delete the free-list initialisation. `nx` stays all-zero, so the list "
     "self-loops at slot 0 from the start -- and note WHAT FAILS: not memory "
     "safety (0 is a real slot) but the postcondition and the loop invariant "
     "that `nx@` equals `st0().nx`. The free list's SHAPE is only ever a "
     "functional property here."),
]


# ⚠ `--rlimit 200`, and it is not padding. At the default limit a mutant
# whose real failure is a PRECONDITION reports only `Resource limit (rlimit)
# exceeded` on the enclosing loop -- measured on M3, which says
# `precondition not satisfied ... i < v@.len()` at 200 and says nothing useful
# at the default. A battery whose arms all fail with the same uninformative
# diagnostic cannot tell a memory-safety failure from a functional one, which is
# exactly the distinction this pattern's whole R5 finding turns on. The SHIPPED
# file verifies at the default limit (`M0` here is run with the same flag; the
# gate runs it without one).
RLIMIT = ["--rlimit", "200"]


def run_verus(path):
    r = subprocess.run([sys.executable, VERUS_RUN, path] + RLIMIT,
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
    for rel in ("patterns/p32-free-list-pool/verus.rs",
                "patterns/p32-free-list-pool/controls/proof_mutants.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    os.makedirs(MDIR, exist_ok=True)
    base = open(SRC).read()
    rows = []
    for name, kind, expect, subs, why in MUTANTS:
        if a.only and a.only != name:
            continue
        txt = base
        for find, repl in subs:
            if find not in txt:
                raise SystemExit(f"proof_mutants: {name}: pattern not found in "
                                 f"verus.rs -- the file moved under this "
                                 f"script:\n{find[:200]}")
            txt = txt.replace(find, repl, 1)
        path = os.path.join(MDIR, f"{name}.rs")
        open(path, "w").write(txt)
        res = run_verus(path)
        got = "verify" if (res["errors"] == 0 and res["rc"] == 0) else "fail"
        ok = got == expect
        rows.append({"mutant": name, "kind": kind, "expected": expect,
                     "got": got, "ok": ok, **res, "why": why})
        print(f"  {name:24s} {kind:11s} expect={expect:6s} got={got:6s} "
              f"{'OK ' if ok else 'XX '} "
              f"{res['verified']}/{res['errors']} {res['error_kinds']}")
    doc = {"pin": {"regenerate":
                   "python3 patterns/p32-free-list-pool/controls/"
                   "proof_mutants.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "mutants": rows,
           "invariant":
               "The ATTACK arm (M1, the shipped bug) and the VACUITY arm (M2, a "
               "constant body) both FAIL. The SPEC-WEAKEN arm (M4) VERIFIES, "
               "and that is the finding rather than a defect: p32's safety line "
               "is load-bearing against the specification alone, because the "
               "pattern allocates nothing and has no linear resource to "
               "consume. THE THREE-CELL FORM IS WHAT MAKES THAT A RESULT: "
               "M1 exec-only FAIL, X3-spec-only-weaken spec-only FAIL, M4 both "
               "VERIFY -- so `step`'s conjunct is not inert and the two sides "
               "are tied to each other. M3 is the contrast case -- the one arm "
               "that fails for a memory-safety reason.",
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
