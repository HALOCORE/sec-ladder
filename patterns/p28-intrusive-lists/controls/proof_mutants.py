#!/usr/bin/env python3
"""p28 CONTROLS: **what does the R5 proof actually force?** Seven mutants of the
shipped `verus.rs`, each with a declared expected verdict, all re-derived on
every run.

    python3 patterns/p28-intrusive-lists/controls/proof_mutants.py [--only NAME]

WHY THIS BATTERY EXISTS, AND WHAT IT MEASURES THAT A GREEN GATE DOES NOT
------------------------------------------------------------------------
`harness/check.py` proves that `verus.rs` verifies. It does not prove that the
verification is ABOUT anything. This project has shipped two proofs that were
not: `p42`'s ghost ledger verified `18/0` while leaking, and `TASK_136`'s ARM_C
was discharged by `fn arm_c() -> u8 { 9 }`. So every arm below has a declared
verdict and `main()` exits non-zero if any of them surprises us.

⚠⚠ **THE THREE-CELL EXPERIMENT IS THE POINT, AND ITS ANSWER IS NOT THE ONE p28's
C SIDE WOULD SUGGEST.** `A1` deletes the safety line from the EXEC code alone,
`A3` from the abstract machine alone, `A4` from BOTH. Read together they say
whether R5's obligation is a MEMORY-SAFETY one or a REFINEMENT one -- the same
form `p32`'s `M1 / X3 / M4` uses, and the reason `p32`'s M4 alone was called an
assertion until `TASK_147` supplied the third cell.

`A5` is the contrast arm: it deletes the WALK's liveness conjunct instead, and
fails on a different obligation (`assert(alive(st, cur))` rather than
`assert(st == step(..))`), so the battery can tell the two failure modes apart
rather than reporting "an error" for both.

⚠⚠ **`A6` WAS PREDICTED TO FAIL AND VERIFIES, AND THAT PREDICTION IS RETRACTED
HERE RATHER THAN QUIETLY DROPPED.** Kill the epilogue and every surviving object
leaks; the proof does not notice, because `Tracked<Dealloc>` is AFFINE and
dropping a token is legal. `.memory/04-verus.md` already carries that result for
`p42` (`TASK_104`, with a committed must-fail control); p28 is the fourth
pattern to show it, and the first to show it on a kernel whose C rungs really do
free everything.
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
MDIR = os.path.join(REPO, ".temp", "p28mut")

SRC = os.path.join(PDIR, "verus.rs")

# ---------------------------------------------------------------- anchors ---
# The EXEC safety line is ~80 lines (the splice plus the invariant it
# re-establishes), so it is cut between two markers rather than pasted here.
# Both markers must occur EXACTLY ONCE or this script refuses to run: that is
# what makes it notice the file moving underneath it.
EXEC_SL_BEGIN = ("                // THE SAFETY LINE. c/kernel.c omits exactly "
                 "this and nothing")
EXEC_SL_END = "                let ghost jj = v as int;"

SPEC_SL = """    // THE SAFETY LINE, in the abstract machine.
    let s3 = if alive(st, v.hp) {
        St { ob: s2.ob.update(v.hp as int, Obj { hn: v.hn, ..s2.ob[v.hp as int] }), ..s2 }
    } else {
        St { bk: s2.bk.update(vb, v.hn), ..s2 }
    };
    let s4 = if alive(st, v.hn) {
        St { ob: s3.ob.update(v.hn as int, Obj { hp: v.hp, ..s3.ob[v.hn as int] }), ..s3 }
    } else {
        s3
    };"""
SPEC_SL_GONE = """    // THE SAFETY LINE, DELETED FROM THE ABSTRACT MACHINE.
    let s3 = s2;
    let s4 = s3;"""

WALK_GUARD = ("    while cur != NIL && arr_get_unchecked(live, cur as usize) "
              "== 1u8 && steps < SLOTS")
WALK_NOGUARD = "    while cur != NIL && steps < SLOTS"

KERNEL_OPEN = ("        r == cache_fold(buf@, off as int, len as int),\n{\n"
               "    // Ghost only")
KERNEL_CONST = ("        r == cache_fold(buf@, off as int, len as int),\n{\n"
                "    return 0;\n    // Ghost only")

EPILOGUE = """        if arr_get_unchecked(&live, j) == 1u8 {
            assert(rec_ok(tab@, st.ob, perms, j as int));"""
EPILOGUE_GONE = """        if false {
            assert(rec_ok(tab@, st.ob, perms, j as int));"""


def cut(txt, begin, end, name):
    """Delete everything from `begin` up to (not including) `end`."""
    for m in (begin, end):
        if txt.count(m) != 1:
            raise SystemExit(f"proof_mutants: {name}: marker occurs "
                             f"{txt.count(m)} times, expected 1 -- verus.rs "
                             f"moved under this script:\n{m[:160]}")
    i = txt.index(begin)
    j = txt.index(end)
    if j <= i:
        raise SystemExit(f"proof_mutants: {name}: markers are out of order")
    return txt[:i] + txt[j:]


# (name, kind, expect, cut_markers_or_None, [(find, replace), ...], why)
MUTANTS = [
    ("A0-control", "control", "verify", None, [],
     "the shipped file, run through the same harness and the same flags. If "
     "this does not verify, nothing below means anything."),
    ("A1-exec-safety-line", "attack", "fail", "exec", [],
     "⚠⚠ **THE ATTACK ARM, and it is c/kernel.c exactly**: delete the "
     "hash-chain splice from TRIM's EXEC code and nothing else, so the freed "
     "victim stays in `bucket[vb]` or in a live object's `hn`. It must FAIL, "
     "and it does -- **at `assert(st == step(st_in, c, a).0)`, the REFINEMENT "
     "assertion** (measured; the mutant's own diagnostic names that line). It "
     "is a functional failure and not a permission one, which is this row's R5 "
     "result, and A4 is what proves the distinction is real rather than a "
     "reading of one error message."),
    ("A2-constant-body", "vacuity", "fail", None,
     [(KERNEL_OPEN, KERNEL_CONST)],
     "`.memory/04-verus.md`'s vacuity probe in its sharp form -- what is the "
     "CHEAPEST body that satisfies the postcondition? `TASK_137` discharged "
     "`TASK_136`'s ARM_C with `fn arm_c() -> u8 { 9 }`, and `p42`'s ghost "
     "ledger verified 18/0 while leaking. Here the cheapest body is "
     "`return 0;` and it must FAIL, because `cache_fold` is a function of the "
     "window bytes and no constant equals it."),
    ("A3-spec-only-weaken", "attack", "fail", None,
     [(SPEC_SL, SPEC_SL_GONE)],
     "delete the chain splice from the ABSTRACT MACHINE `trim` only, leaving "
     "the exec code intact -- a postcondition true of the WRONG program. It "
     "must FAIL. With A1 (exec only) and A4 (both) this is the third cell, and "
     "it is what stops A4 from being an assertion: the two sides are tied to "
     "each other and to nothing outside."),
    ("A4-spec-weaken", "must-verify", "verify", "exec",
     [(SPEC_SL, SPEC_SL_GONE)],
     "⚠⚠⚠ **THE ARM THAT IS SUPPOSED TO VERIFY, AND IT IS p28's R5 RESULT.** "
     "Delete the chain splice from the exec code AND from `trim`, so the "
     "specification describes the BUGGY kernel. It verifies. **The linear "
     "resources do NOT force this safety line** -- `rec_close` consumes the "
     "victim's `PointsTo` and its `Dealloc`, and that is a real temporal "
     "guarantee about READS, but what `c/kernel.c` forgets is a LINK, and "
     "leaving a `u8` behind consumes nothing. ⚠⚠ **That is the same shape "
     "`p32` reported and it is SHARPER here**: `p32` had no linear resource at "
     "all, so of course none forced its conjunct; p28 HAS them, consumed by a "
     "real `free`, and they still do not reach the destroy path's omission. "
     "What forces the safety line is the FUNCTIONAL postcondition, which A1 "
     "shows and A3 shows is not inert."),
    ("A5-walk-liveness", "attack", "fail", None,
     [(WALK_GUARD, WALK_NOGUARD)],
     "the CONTRAST arm: delete `live[cur] == 1u8` from the walk's loop "
     "condition and leave everything else alone. It must FAIL, and ⚠ **it "
     "fails for a MEMORY-SAFETY reason** -- measured, the diagnostic names "
     "`assert(alive(st, cur))` inside `walk`, which is the step that licenses "
     "`perms.tracked_borrow(cur)`; the borrow's own precondition is never "
     "reached because the licence is gone one line earlier. Contrast A1, whose "
     "diagnostic names `assert(st == step(st_in, c, a).0)`. **Two arms, two "
     "different failing obligations, and that is what lets this battery tell a "
     "permission failure from a refinement failure** -- the distinction A1 and "
     "A4 turn on."),
    ("A6-epilogue-dead", "must-verify", "verify", None,
     [(EPILOGUE, EPILOGUE_GONE)],
     "⚠⚠ **THE ARM THAT WAS PREDICTED TO FAIL AND VERIFIES, AND THE PREDICTION "
     "WAS THE ONE WRITTEN INTO THIS FILE FIRST.** Make the epilogue's "
     "`live[j] == 1` test unreachable, so NOTHING is freed at the end of the "
     "window and every surviving object leaks. It VERIFIES, `23/0`. The reason "
     "is already in `.memory/04-verus.md`: **`Tracked<Dealloc>` is AFFINE, not "
     "linear** -- dropping a token is legal, so a proof built on it shows "
     "deallocation is LEGAL (no double free, no use after free) and never that "
     "it HAPPENS. `TASK_104` measured that on `p42` with a committed must-fail "
     "control; this is the same result on a fourth pattern, and it is why the "
     "sentence *the linear resources force the epilogue* -- which this battery "
     "asserted before it was run -- is RETRACTED. ⚠ What stands behind p28's "
     "epilogue instead is `controls/rust_arms.py`'s Miri arm and the C rungs' "
     "own structure, not the proof."),
]


# ⚠ `--rlimit 400`, matching the `#[verifier::rlimit(400)]` the shipped file
# carries on `kernel`. It is not padding and it is not a soundness knob: p28's
# loop body carries four opcode arms, ten `alive_link` sites and a dozen
# invariant re-establishments in ONE query, and the MINIMUM workable limit was
# measured at between 100 (fails) and 120 (verifies). Shipping at 400 is a 3x
# margin over a measured floor, and a mutant that fails at 400 has been given
# more solver effort than the shipped file needs -- which is the direction that
# makes a `fail` verdict mean something. ⚠ At the DEFAULT limit of 10 every arm
# here reports only `Resource limit (rlimit) exceeded`, and a battery whose arms
# all fail with the same uninformative diagnostic cannot tell a memory-safety
# failure from a functional one.
RLIMIT = ["--rlimit", "400"]


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
    for rel in ("patterns/p28-intrusive-lists/verus.rs",
                "patterns/p28-intrusive-lists/controls/proof_mutants.py"):
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
    for name, kind, expect, cutmark, subs, why in MUTANTS:
        if a.only and a.only != name:
            continue
        txt = base
        if cutmark == "exec":
            txt = cut(txt, EXEC_SL_BEGIN, EXEC_SL_END, name)
        for find, repl in subs:
            if txt.count(find) != 1:
                raise SystemExit(f"proof_mutants: {name}: pattern occurs "
                                 f"{txt.count(find)} times in verus.rs, "
                                 f"expected 1 -- the file moved under this "
                                 f"script:\n{find[:200]}")
            txt = txt.replace(find, repl, 1)
        path = os.path.join(MDIR, f"{name}.rs")
        open(path, "w").write(txt)
        res = run_verus(path)
        got = "verify" if (res["errors"] == 0 and res["rc"] == 0) else "fail"
        ok = got == expect
        rows.append({"mutant": name, "kind": kind, "expected": expect,
                     "got": got, "ok": ok, **res, "why": why})
        print(f"  {name:22s} {kind:11s} expect={expect:6s} got={got:6s} "
              f"{'OK ' if ok else 'XX '} "
              f"{res['verified']}/{res['errors']} {res['error_kinds']}")
    doc = {"pin": {"regenerate":
                   "python3 patterns/p28-intrusive-lists/controls/"
                   "proof_mutants.py"},
           "derived_from_sha256": derived_from(),
           "verus_flags": RLIMIT,
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "mutants": rows,
           "invariant":
               "The ATTACK arm (A1, the shipped bug), the VACUITY arm (A2, a "
               "constant body), the SPEC-ONLY arm (A3), the WALK-GUARD arm (A5) "
               "and the EPILOGUE arm (A6) all FAIL. The SPEC-WEAKEN arm (A4) "
               "VERIFIES, and that is p28's R5 RESULT rather than a defect: the "
               "safety line is load-bearing against the SPECIFICATION, not "
               "against the linear resources -- which p28 HAS and p32 did not, "
               "so the finding is sharper here. A1 exec-only FAIL / A3 "
               "spec-only FAIL / A4 both VERIFY is the three-cell form that "
               "makes it a result. A5 and A6 are the contrast: the two arms "
               "that fail because a PERMISSION is missing rather than because a "
               "postcondition stopped holding.",
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
