#!/usr/bin/env python3
"""p34 CONTROLS: the R5 mutation battery -- **an ATTACK arm, a VACUITY arm, an
X1 arm that strikes the central conjunct out of the invariant itself, and the
two-cell exec/spec pair beside them.**

`.memory/02-bench-rules.md`: *"Every temporal R5 owes an ATTACK arm that must
FAIL to verify, not just a deletion arm."* Two instances in this project's own
history say why: `p42`'s ghost ledger verified `18/0` while leaking, and
`TASK_136`'s ARM_C was discharged by `fn arm_c() -> u8 { 9 }`. So:

  * **ATTACK arms** put `c/kernel.c`'s ACTUAL BUG into the R5 and require the
    proof to reject it. `M1` is the one the row is about: it deletes the retain
    and nothing else, so the surviving program IS `c/kernel.c`.
  * **VACUITY arms** ask what the CHEAPEST body satisfying the postcondition is.
    `M2` is `return 0;`, i.e. `TASK_136`'s `fn arm_c() -> u8 { 9 }` in this
    file's terms.
  * **`X1` strikes the central obligation out of the LOOP INVARIANT** and asks
    whether anything but a hand-written pin notices. The conjunct is
    `perms[k].value().rc == cnt(stk, k)`, the bridge between the count in the
    object's first word and the number of stack entries naming it.

    ⚠⚠ **THIS ARM WAS PUBLISHED AS *"`p35`'s arm, transplanted"* AND THAT WAS A
    WRONG CROSS-ROW COMPARISON (`TASK_155_REPORT` M5, corrected at
    `TASK_156`).** `p35`'s arm that VERIFIES, `X1-delete-variant-requires`,
    deletes the correct-variant conjunct from **three TRUSTED items'
    `requires`** -- a different object from an invariant. Read out of the two
    rows' own committed sidecars and re-derived at `TASK_156`
    (`.temp/t156/zmut.py`):

    | what is weakened | p34 | p35 |
    |---|---|---|
    | the loop invariant / abstract machine | `X1` **22/2 FAILS** | `M6` **15/1 FAILS** |
    | a TRUSTED item's `requires` | `Z1` **24/0 VERIFIES** | `X1` **16/0 VERIFIES** |

    **The two rows behave the SAME**, and the thing that decides whether a
    mutation is caught is WHICH OBJECT it touches, not which row it is on: the
    proof defends the invariant on both, and defends the trusted contract on
    neither. ⚠ The real cross-row difference is a GATE difference -- `p34`'s
    stage `5c-twin` re-derives each trusted `requires` conjunct and each one,
    deleted alone, makes its twin FAIL (`28 verified, 1 error`, three of three
    accessors, read out of `results/gate/p34-refcount-stack.json`), while on
    `p35` that stage is BLOCKED for exactly the three items its `X1` mutates.
  * **`X2` is the two-cell pair**: `M1` and `X1` TOGETHER, i.e. the exec code and
    the invariant weakened to agree with each other. On `p32` the equivalent arm
    VERIFIES, and that is p32's honest statement of what its R5 buys -- the
    safety line is load-bearing against the SPECIFICATION and nothing else.
    ⚠ **Whatever this arm does is p34's answer to the same question and it is
    reported either way.**
    ⚠ **Name the OBJECT, not just the row** (`TASK_155_REPORT` M5): `p32`'s
    `M4-spec-weaken` weakens its exec code and its **abstract machine `step`**,
    i.e. the SPECIFICATION; `p34`'s `X2` weakens its exec code and the **loop
    invariant `wf`**. The conclusion -- `p32` verifies at `15/0`, `p34` fails at
    `22/2` -- is sound and the mechanism is right (`run` has no reference count,
    so no spec weakening can rescue the mutant and the failure is a
    linear-resource one), but *"X2 is p32's arm"* is not literally true.
  * **`M3`** deletes the epilogue, which is what the leak-freedom corollary
    rests on.
  * **MUST-VERIFY controls** (`M0`) make sure a failure is caused by the mutation
    and not by an unachievable postcondition or a broken harness.

    python3 patterns/p34-refcount-stack/controls/proof_mutants.py

⚠ Each arm is a full Verus run; budget several minutes. Mutant sources are
written under `.temp/p34mut/` and deleted on success
(`.memory/00-environment.md` constraint 6) -- this file is the generator and it
is what is committed.
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
MDIR = os.path.join(REPO, ".temp", "p34mut")

SRC = os.path.join(PDIR, "verus.rs")

# ---------------------------------------------------------------- mutants ---
RETAIN = ("                // THE LINE THE C RUNG FORGOT.\n"
          "                obj_retain(t, Tracked(&mut pt));\n")
RETAIN_GONE = "                // THE LINE THE C RUNG FORGOT -- DELETED.\n"

RC_CONJ = "    &&& perms[k].value().rc == cnt(stk, k)\n"

KERNEL_OPEN = ("        r == rc_fold(buf@, off as int, len as int),\n{\n"
               "    // Ghost only")
KERNEL_CONST = ("        r == rc_fold(buf@, off as int, len as int),\n{\n"
                "    return 0;\n    // Ghost only")

EPILOGUE_GUARD = ("    while ntop > 0\n"
                  "        invariant\n"
                  "            wf(stk@, ntop as int, ids, vals, perms, dal),\n"
                  "        decreases ntop,")
EPILOGUE_DEAD = ("    while ntop > CAP\n"
                 "        invariant\n"
                 "            wf(stk@, ntop as int, ids, vals, perms, dal),\n"
                 "        decreases ntop,")

# (name, kind, expect, [(find, replace), ...], why)
MUTANTS = [
    ("M0-control", "control", "verify", [],
     "the shipped file, run through the same harness. If this does not verify, "
     "nothing below means anything."),
    ("M1-delete-retain", "attack", "fail", [(RETAIN, RETAIN_GONE)],
     "THE ATTACK ARM, and it is the row's bug exactly: delete `obj_retain` from "
     "the DUP arm and nothing else. What survives is `c/kernel.c` -- a kernel "
     "that frees an object while a live stack entry still names it. It must "
     "FAIL, and WHERE it fails is the finding: the loop invariant `wf` can no "
     "longer be re-established, because `cnt(ids, k)` has gone up by one and "
     "the count in the object's first word has not."),
    ("M2-constant-body", "vacuity", "fail", [(KERNEL_OPEN, KERNEL_CONST)],
     "`.memory/04-verus.md`'s vacuity probe in its sharp form -- what is the "
     "CHEAPEST body that satisfies the postcondition? `TASK_137` discharged "
     "`TASK_136`'s ARM_C with `fn arm_c() -> u8 { 9 }`. Here the cheapest body "
     "is `return 0;` and it must FAIL, because `rc_fold` is a function of the "
     "window bytes and no constant equals it."),
    ("X1-delete-rc-conjunct", "attack", "fail", [(RC_CONJ, "")],
     "Strike the CENTRAL OBLIGATION out of the LOOP INVARIANT and see whether "
     "anything but a hand-written pin notices. The conjunct is "
     "`perms[k].value().rc == cnt(stk, k)` -- the bridge between the count the "
     "object stores and the number of stack entries naming it. It must FAIL, "
     "and the reason is that this bridge is what discharges `obj_dec`'s "
     "`requires rc > 0` and what licenses `obj_free` at zero: it is a "
     "MEMORY-SAFETY precondition, not a functional one. "
     "⚠⚠ THE CROSS-ROW SENTENCE THIS ENTRY USED TO CARRY IS WITHDRAWN "
     "(TASK_155_REPORT M5, corrected TASK_156). It read `On p35 the equivalent "
     "deletion VERIFIED at the pinned obligation count and only the "
     "verus.items pin caught it`, and that names the wrong p35 arm: p35's "
     "invariant weakenings M3 and M6 both FAIL at 15/1, exactly as this arm "
     "fails at 22/2, and the p35 arm that verifies deletes a TRUSTED item's "
     "`requires` -- on which p34 verifies too, 24/0 (.temp/t156/zmut.py). The "
     "two rows behave the same; the module docstring above carries the table."),
    ("X2-exec-and-spec", "spec-weaken", "fail",
     [(RETAIN, RETAIN_GONE), (RC_CONJ, "")],
     "THE TWO-CELL PAIR. Delete the retain from the exec code AND the bridge "
     "from the invariant, so the two agree with each other again. ⚠ On p32 "
     "the equivalent arm VERIFIES, and p32 publishes that as the honest "
     "statement of what its R5 buys -- its safety line is load-bearing against "
     "the SPECIFICATION alone, because nothing there is allocated and there is "
     "no linear resource to consume. p34 allocates, so the prediction is that "
     "this arm FAILS ANYWAY: without the bridge nothing discharges "
     "`obj_dec`'s `rc > 0`, and `obj_free` consumes a permission a live stack "
     "entry still needs. **Whatever it does is p34's answer and it is reported "
     "either way.**"),
    ("M3-delete-epilogue", "deletion", "fail",
     [(EPILOGUE_GUARD, EPILOGUE_DEAD)],
     "make the epilogue's guard unreachable (`ntop > CAP` is false under the "
     "invariant), so no reference left on the stack is released. It must FAIL, "
     "and the failing obligation is the LEAK-FREEDOM corollary at the end of "
     "the kernel: `obj_ok` requires `cnt(ids, k) > 0` for every key in the "
     "permission map, so the map is empty only once the stack is. That is what "
     "makes leak-freedom a proved property of this rung rather than a remark."),
]


# ⚠ `--rlimit 200`, and it is not padding: at the default limit a mutant whose
# real failure is a PRECONDITION can report only `Resource limit (rlimit)
# exceeded` on the enclosing loop, and a battery whose arms all fail with the
# same uninformative diagnostic cannot tell a memory-safety failure from a
# functional one -- which is exactly the distinction p34's R5 finding turns on.
# The SHIPPED file verifies at the default limit (the gate runs it without one);
# `M0` here is run with the same flag as the rest so the arms are comparable.
RLIMIT = ["--rlimit", "200"]


def run_verus(path):
    r = subprocess.run([sys.executable, VERUS_RUN, path] + RLIMIT,
                       capture_output=True, text=True, cwd=REPO, timeout=3600)
    txt = r.stdout + r.stderr
    m = re.search(r"verification results:: (\d+) verified, (\d+) errors", txt)
    kinds = sorted({ln.split("error:")[1].strip().split("\n")[0][:70]
                    for ln in txt.splitlines() if ln.startswith("error:")})
    if m:
        return {"verified": int(m.group(1)), "errors": int(m.group(2)),
                "rc": r.returncode, "error_kinds": kinds[:4]}
    return {"verified": None, "errors": None, "rc": r.returncode,
            "error_kinds": kinds[:4]}


def derived_from():
    out = {}
    for rel in ("patterns/p34-refcount-stack/verus.rs",
                "patterns/p34-refcount-stack/controls/proof_mutants.py"):
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
        print(f"  {name:24s} {kind:12s} expect={expect:6s} got={got:6s} "
              f"{'OK ' if ok else 'XX '} "
              f"{res['verified']}/{res['errors']} {res['error_kinds']}")
    doc = {"pin": {"regenerate":
                   "python3 patterns/p34-refcount-stack/controls/"
                   "proof_mutants.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "mutants": rows,
           "invariant":
               "The ATTACK arm (M1, the shipped bug), the VACUITY arm (M2, a "
               "constant body), the X1 arm (strike the count/alias bridge out "
               "of the invariant) and the epilogue deletion (M3) all FAIL. "
               "⚠ X2 -- the exec code and the invariant weakened TOGETHER, "
               "which is the arm p32 publishes as VERIFYING -- is the one whose "
               "verdict is the row's R5 result, and it is recorded here rather "
               "than predicted in prose.",
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
