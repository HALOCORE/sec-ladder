#!/usr/bin/env python3
"""p35 CONTROLS: **the proof-mutant battery. What does R5's proof actually
force?**

    python3 patterns/p35-tagged-union/controls/proof_mutants.py

WHY THIS EXISTS
---------------
A green `N verified, 0 errors` is not evidence that a proof forces anything.
Three measured instances on this project: `p42`'s ghost ledger verified `18/0`
**while leaking**; `TASK_136`'s ARM_C was discharged by `fn arm_c() -> u8 { 9 }`;
and `p32`'s `assume(false)` verifies at its shipped obligation count. So every
claim about what this R5 buys is an ARM here, each with the outcome it must
have, and the script exits non-zero if any of them stops holding.

⚠⚠ **THE HEADLINE, AND IT IS THE OPPOSITE OF `p32`'s.** `p32`'s spec-weaken arm
-- delete the safety conjunct from the exec code AND from the abstract machine
-- **VERIFIES** `15/0`, because nothing linear forces the conjunct and the proof
is a purely functional one. **p35's does NOT**, and the reason is structural:
the correct-variant obligation is a PRECONDITION OF THE READ, not merely a term
in the postcondition, so weakening the specification does not rescue the
mutant -- the `pay_*` call site simply stops verifying. `M3` below is that
measurement.

⚠⚠⚠ **AND THE CONCLUSION THIS FILE USED TO DRAW FROM IT IS RETRACTED
(TASK_152 M3, landed TASK_153). ORIGINAL STRUCK, NOT DELETED.** It read
~~weakening the specification does not rescue the mutant ... the correct-variant
obligation cannot be specified away~~ **as a statement about the SHIPPED
configuration**, and that is false. `M3` and `M6` weaken the ABSTRACT MACHINE
(`step`, `wf_cell`) and they reproduce exactly; **they do not touch the trusted
readers' own `requires`, which is where the obligation actually lives in
configuration A.** New arm **`X1`** deletes `v@[i as int] is {i,o,d}` from all
THREE trusted readers and the file reports **`16 verified, 0 errors` at the
shipped obligation count** -- nothing moves.

✅ **SO THE ROW'S HEADLINE IS SHARPER, NOT WEAKER.** The correct-variant
obligation cannot be weakened by editing the abstract machine (`M3`/`M6`, and
that IS `p32`'s opposite). It CAN be **deleted outright** from the trusted
readers' `requires`, and the only thing that catches it is `../spec.md`'s item
pin -- **a declaration the author writes** -- while every soundness stage stays
green (verus `16/0`, identity `exact`, Miri `0 UB`) and the gate stage that
judges STRENGTH rather than triviality, `5c-twin`, is BLOCKED for exactly these
three items. **Configuration B RESISTS the same deletion** -- Verus fails AT THE
READ, `../controls/union_oracle.py` arm `B2`. So the gate does not merely force
the weaker of two proofs: **it forces the one whose central obligation can be
deleted without the gate noticing.** *"Imposed by the type system at the
operation"* is true of configuration B only; in A, Verus never sees the read.

THE ARMS
--------
  M1-drop-tag-test    the GET arm reads `pay_i` without testing the tag.
                      MUST FAIL: `precondition not satisfied`.
  M2-bug-order-exec   R1's bug, in R5's exec code: the tag store moves OUT of
                      the `navail > 0` test. MUST FAIL.
  M3-bug-order-both   M2 **plus the same reorder in the abstract machine**, so
                      the specification agrees with the buggy code. This is the
                      arm `p32` calls `M4-spec-weaken` and where `p32` verifies.
                      MUST FAIL here, and that difference is the row's result.
  M6-weaken-invariant M3 taken one step further: `wf_cell` is weakened to
                      `true`, so NOTHING in the specification says a tag names
                      the union member its payload is. MUST FAIL, at the union
                      read's own precondition.
  X1-delete-variant-requires
                      ⚠⚠ the arm M3/M6 do NOT cover: delete
                      `v@[i as int] is {i,o,d}` from ALL THREE trusted readers'
                      OWN `requires`. **MUST VERIFY**, at the shipped
                      obligation count -- and that is the finding, not a pass.
                      Nothing in the PROOF holds the obligation up once the
                      declaration stops asking for it; the catcher is
                      `../spec.md`'s item pin, which is `proof-pin` and not a
                      proof. TASK_152 M3 planted it into the tree and ran the
                      real gate: FAIL on `proof-pin` (3 items) and `tables`
                      only, with verus `16/0`, identity `exact` and Miri `0 UB`
                      all still green.
  M4-constant-body    the kernel returns `0`. MUST FAIL: the `ensures` is not
                      satisfiable by a constant. (`TASK_136`'s ARM_C shape.)
  M5-assume-false     `assume(false);` at the top of the kernel. **VERIFIES**,
                      at the shipped obligation count -- reproducing the vacuity
                      hole `TASK_145` and `TASK_149` both planted -- and then
                      `check._assume_keyword_hits` is run on the same text to
                      show that `TASK_151`'s repair SEES it, and that `spec.md`
                      declares no `verus.assumptions`, so the shipped gate would
                      now FAIL such a file.

⚠⚠ **TWO PREDICTIONS IN THIS FILE WERE WRONG ABOUT THE DIAGNOSTIC AND RIGHT
ABOUT THE OUTCOME, AND THEY ARE CORRECTED RATHER THAN QUIETLY REFITTED.** M2 and
M3 were written expecting `precondition not satisfied`. Measured, M2 fails at
`assert(st_out =~= step(st_in, c, a).0)` -- *assertion failed* -- because the
exec code stops agreeing with the abstract machine BEFORE anything reaches a
union read; and M3 fails with **`invariant not satisfied at end of loop body`
naming `wf_cells` itself**, which is the sharper statement of the two: with the
specification weakened to match the buggy code, **the correct-variant invariant
is what stops being maintainable.** The expectations in the arms below are the
measured diagnostics and the original predictions are recorded beside them.
M6 -- written after that correction -- predicted `precondition not satisfied`
and got it.

⚠ Each mutant is written to a mirror of the repo layout under `.temp/`, never
into `patterns/` -- a crashed run must not be able to leave a mutated source in
the tree (`check.py::_mutant_path`'s rule, reimplemented here so that a
concurrent gate run and this script cannot collide on one scratch directory).

⚠ A cell that RAISES is reported as a failed cell with its exception text and
never allowed to crash the script.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
ROOT = os.path.join(REPO, ".temp", "p35ctl", "mut")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
SRC = os.path.join(PDIR, "verus.rs")

sys.path.insert(0, os.path.join(REPO, "harness"))

SHIPPED_OBLIGATIONS = 16



def mask(txt):
    """Strip everything from a diagnostic that is not evidence.

    ⚠ A committed file that cites an absolute `.temp/` path costs the manager a
    `harness/tools/temp_citations.py` baseline entry for a file a fresh clone
    will not have, and that tool reads `git ls-files`, so the cost only shows
    up after the commit. ASan pids and pointer values are pure churn for the
    same reason `p23`'s `controls.log` is declared un-hashable
    (`.memory/05-layout.md`). The DIAGNOSTIC TEXT is what this control is
    evidence for; the path, the pid and the address are not."""
    txt = re.sub(re.escape(REPO) + r"/\.temp/\S*", "<scratch>", txt)
    txt = txt.replace(REPO + "/", "")
    txt = re.sub(r"==\d+==", "==<pid>==", txt)
    txt = re.sub(r"0x[0-9a-f]{6,}", "0x<addr>", txt)
    return txt

def mutant_path():
    d = os.path.join(ROOT, "patterns", os.path.basename(PDIR))
    os.makedirs(d, exist_ok=True)
    link = os.path.join(ROOT, "common")
    if not os.path.islink(link) and not os.path.exists(link):
        os.symlink(os.path.join(REPO, "common"), link)
    return os.path.join(d, "verus.rs")


def verus(text):
    path = mutant_path()
    open(path, "w").write(text)
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    r = subprocess.run([sys.executable, VERUS_RUN, path], capture_output=True,
                       text=True, env=env, timeout=1800, cwd=REPO)
    txt = r.stdout + r.stderr
    m = re.search(r"(\d+) verified, (\d+) errors", txt)
    return {"verified": int(m.group(1)) if m else None,
            "errors": int(m.group(2)) if m else None,
            "diagnostic": mask(re.sub(r"\s+", " ", txt.strip()))[:700]}


def sub(txt, old, new, label):
    if old not in txt:
        raise ValueError(f"{label}: the anchor text is not in verus.rs -- the "
                         f"file moved under this control and the mutation would "
                         f"have been a no-op, which would have read as a PASS")
    if txt.count(old) != 1:
        raise ValueError(f"{label}: the anchor text appears {txt.count(old)} "
                         f"times, expected exactly 1")
    return txt.replace(old, new)


# ---- the anchors, each verified to occur exactly once ---------------------
GET_TAG_TEST = """            let t: u8 = arr_get_unchecked(&tags, idx);
            if t == T_INT {"""

EXEC_PTR_ORDER = """            if navail > 0 {
                pay_set_unchecked(&mut pays, idx, Pay { o: (BUDGET - navail) as u32 });
                arr_set_unchecked(&mut tags, idx, T_PTR);"""

EXEC_PTR_BUGGY = """            arr_set_unchecked(&mut tags, idx, T_PTR);
            if navail > 0 {
                pay_set_unchecked(&mut pays, idx, Pay { o: (BUDGET - navail) as u32 });"""

SPEC_PTR_ORDER = """                    navail: st.navail - 1,
                },
                1u64,
            )
        } else {
            (st, SENT)
        }"""

SPEC_PTR_BUGGY = """                    navail: st.navail - 1,
                },
                1u64,
            )
        } else {
            (St { tags: st.tags.update(k, T_PTR), ..st }, SENT)
        }"""

RETURN_EXPR = """    // No epilogue: nothing was ever acquired.
    acc.wrapping_mul(31).wrapping_add(navail as u64)"""

SLICE_LEN_ASSERT = """    assert(buf@.len() == vstd::slice::spec_slice_len(buf));"""

WF_CELL_BODY = """pub open spec fn wf_cell(t: u8, p: Pay) -> bool {
    &&& (t == T_INT ==> p is i)
    &&& (t == T_PTR ==> p is o && pay_off(p) < BUDGET as u32)
    &&& (t == T_DBL ==> p is d)
}"""

WF_CELL_TRUE = """pub open spec fn wf_cell(t: u8, p: Pay) -> bool {
    true
}"""


def derived_from():
    out = {}
    for rel in ("patterns/p35-tagged-union/verus.rs",
                "patterns/p35-tagged-union/controls/proof_mutants.py",
                "harness/check.py", "verus_run.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    base = open(SRC).read()
    cells, rows = [], {}

    def arm(name, build, want, why):
        try:
            text = build(base)
            got = verus(text)
        except Exception as e:                              # noqa: BLE001
            got = {"RAISED": f"{type(e).__name__}: {e}", "verified": None,
                   "errors": None, "diagnostic": ""}
        ok = want(got)
        rows[name] = dict(got, expectation=why, as_designed=bool(ok))
        cells.append((name, ok, got, why))
        return got

    must_fail = lambda frag: (lambda r: (r.get("errors") or 0) > 0            # noqa: E731
                              and frag in (r.get("diagnostic") or ""))

    # M0 -- the unmutated file, so a mutation that silently did nothing cannot
    # read as a pass.
    arm("M0-unmutated", lambda t: t,
        lambda r: r.get("errors") == 0 and r.get("verified") == SHIPPED_OBLIGATIONS,
        f"the shipped file verifies at exactly {SHIPPED_OBLIGATIONS} "
        f"obligations; every arm below is a diff against THIS run")

    arm("M1-drop-tag-test",
        lambda t: sub(t, GET_TAG_TEST,
                      GET_TAG_TEST.replace("if t == T_INT {", "if true {"),
                      "M1"),
        must_fail("precondition not satisfied"),
        "reading `pay_i` without testing the tag must FAIL with `precondition "
        "not satisfied` -- this is what proves the tag/variant agreement is "
        "CHECKED at the call site and not merely asserted in spec.md")

    arm("M2-bug-order-exec",
        lambda t: sub(t, EXEC_PTR_ORDER, EXEC_PTR_BUGGY, "M2"),
        must_fail("assertion failed"),
        "R1's bug in R5's exec code -- the tag store moves out of the budget "
        "test -- must FAIL. ⚠ MEASURED diagnostic: `assertion failed` at "
        "`assert(st_out =~= step(st_in, c, a).0)`, i.e. the exec code stops "
        "agreeing with the abstract machine before anything reaches a union "
        "read. The prediction written for this arm was `precondition not "
        "satisfied` and it was WRONG about the diagnostic, right about the "
        "outcome")

    arm("M3-bug-order-both",
        lambda t: sub(sub(t, EXEC_PTR_ORDER, EXEC_PTR_BUGGY, "M3-exec"),
                      SPEC_PTR_ORDER, SPEC_PTR_BUGGY, "M3-spec"),
        lambda r: (r.get("errors") or 0) > 0
        and "invariant not satisfied" in (r.get("diagnostic") or "")
        and "wf_cells" in (r.get("diagnostic") or ""),
        "THE SPEC-WEAKEN ARM, and p35's answer is the OPPOSITE of p32's. "
        "Making the abstract machine agree with the buggy code does NOT rescue "
        "the mutant. ⚠ MEASURED diagnostic: `invariant not satisfied at end of "
        "loop body`, naming `wf_cells` -- so what stops being maintainable is "
        "the CORRECT-VARIANT INVARIANT itself, which is a sharper result than "
        "the `precondition not satisfied` this arm was written expecting. "
        "p32's equivalent arm VERIFIES 15/0")

    arm("M6-weaken-invariant",
        lambda t: sub(sub(sub(t, EXEC_PTR_ORDER, EXEC_PTR_BUGGY, "M6-exec"),
                          SPEC_PTR_ORDER, SPEC_PTR_BUGGY, "M6-spec"),
                      WF_CELL_BODY, WF_CELL_TRUE, "M6-wf"),
        must_fail("precondition not satisfied"),
        "M3 taken one step further, and it is the TRUE analogue of p32's "
        "`M4-spec-weaken`: with `wf_cell` weakened to `true`, NOTHING in the "
        "specification says a tag names the union member its payload is. The "
        "proof still fails, now at the union read's own `requires` -- "
        "`precondition not satisfied` -- because that obligation is imposed by "
        "the TYPE SYSTEM at the operation and cannot be specified away. **This "
        "is the cell that p32 has no counterpart for.**")

    # ⚠⚠ X1 -- the arm M3 and M6 do NOT cover, and the one that decides what
    # the row's headline may say. M3/M6 weaken the ABSTRACT MACHINE; X1 deletes
    # the correct-variant conjunct from the three TRUSTED READERS' own
    # `requires`, which is where the obligation lives in the shipped
    # configuration. Added at TASK_153 from TASK_152 M3.
    def _x1(t):
        for member in ("i", "o", "d"):
            t = sub(t,
                    f"        i < v@.len(),\n"
                    f"        v@[i as int] is {member},\n",
                    "        i < v@.len(),\n", f"X1/{member}")
        return t

    arm("X1-delete-variant-requires", _x1,
        lambda r: r.get("errors") == 0
        and r.get("verified") == SHIPPED_OBLIGATIONS,
        "⚠⚠ THIS ONE VERIFIES AT THE SHIPPED OBLIGATION COUNT AND THAT IS THE "
        "RESULT. Deleting the correct-variant conjunct from all three trusted "
        "readers' `requires` removes the obligation from every call site and "
        "nothing in the PROOF objects -- M3 and M6 cannot see this because "
        "they weaken the abstract machine, not the trusted contract. The only "
        "catcher is spec.md's item pin (`proof-pin`), a declaration the author "
        "writes, and the stage that judges clause STRENGTH (5c-twin) is "
        "BLOCKED for exactly these three items. Configuration B RESISTS the "
        "same deletion -- union_oracle.py arm B2 fails AT THE READ -- so the "
        "two configurations differ in resistance to a `requires` deletion and "
        "not only in axiom-versus-check")

    arm("M4-constant-body",
        lambda t: sub(t, RETURN_EXPR,
                      "    // No epilogue: nothing was ever acquired.\n    0",
                      "M4"),
        must_fail("postcondition not satisfied"),
        "TASK_136's ARM_C shape: a constant body must not discharge the "
        "`ensures`")

    m5 = arm("M5-assume-false",
             lambda t: sub(t, SLICE_LEN_ASSERT,
                           SLICE_LEN_ASSERT + "\n    assume(false);", "M5"),
             lambda r: r.get("errors") == 0,
             "⚠ THIS ONE VERIFIES, and that is the finding: `assume(false)` in "
             "the kernel body is invisible to the obligation count, the clause "
             "pin and the identity pin. TASK_145 and TASK_149 both planted it. "
             "The gate-side half is measured below")

    # ---- M5b: does TASK_151's repair SEE the mutant? ----------------------
    try:
        import check
        import vparse
        mutant = sub(base, SLICE_LEN_ASSERT,
                     SLICE_LEN_ASSERT + "\n    assume(false);", "M5b")
        hits = check._assume_keyword_hits(vparse.blank_noncode(mutant))
        shipped_hits = check._assume_keyword_hits(vparse.blank_noncode(base))
        declared = ((check.read_contract(PDIR)[0].get("verus") or {})
                    .get("assumptions") or {}).get("verus.rs", 0)
        m5b = {"hits_in_mutant": {k: v for k, v in hits.items()},
               "hits_in_shipped": {k: v for k, v in shipped_hits.items()},
               "spec_md_verus_assumptions": declared}
        ok5b = bool(hits) and not shipped_hits and declared == 0
    except Exception as e:                                  # noqa: BLE001
        m5b = {"RAISED": f"{type(e).__name__}: {e}"}
        ok5b = False
    rows["M5b-gate-sees-it"] = dict(m5b, as_designed=bool(ok5b))
    cells.append(("M5b-gate-sees-it", ok5b, m5b,
                  "`check._assume_keyword_hits` (TASK_151) reports the planted "
                  "`assume(` with its line number, reports NOTHING on the "
                  "shipped file, and `spec.md` declares "
                  "`verus.assumptions = 0` -- so the shipped gate would FAIL "
                  "the mutant M5 verifies"))

    print("p35 proof mutants -- what does R5's proof force?\n")
    nok = 0
    for name, ok, got, why in cells:
        nok += bool(ok)
        ev = {k: v for k, v in got.items() if k != "diagnostic"}
        print(f"  {'ok  ' if ok else 'FAIL'} {name:20s} {ev}")
        if got.get("diagnostic"):
            print(f"         | {got['diagnostic'][:170]}")
    print(f"\n{nok}/{len(cells)} arm(s) as designed")

    doc = {"pin": {"regenerate": "python3 patterns/p35-tagged-union/controls/"
                                 "proof_mutants.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "shipped_obligations": SHIPPED_OBLIGATIONS,
           "arms": rows,
           "arms_as_designed": nok,
           "arms_total": len(cells),
           "invariant": "M0 verifies at the shipped obligation count; M1, M2, "
                        "M3, M6 and M4 each FAIL with the named diagnostic; M5 "
                        "and X1 VERIFY, and M5b shows the gate's "
                        "assume-detector seeing M5. ⚠ M3 is the arm that "
                        "separates p35 from p32: making the ABSTRACT MACHINE "
                        "agree with the buggy code rescues p32's mutant and "
                        "does NOT rescue p35's -- it fails at `wf_cells` -- and "
                        "M6 shows why: with the invariant itself weakened to "
                        "`true` the proof fails at the union read's own "
                        "precondition. ⚠⚠ X1 is the arm that bounds how far "
                        "that may be pushed, and it RETRACTS the sentence this "
                        "control used to draw from M3/M6: delete the "
                        "correct-variant conjunct from the three trusted "
                        "readers' OWN `requires` and the file still verifies "
                        "16/0. So the obligation cannot be specified away by "
                        "editing the abstract machine, and CAN be deleted "
                        "outright from the trusted contract -- caught only by "
                        "spec.md's item pin, while configuration B fails AT "
                        "THE READ."}
    out = os.path.join(HERE, "proof_mutants.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    return 0 if nok == len(cells) else 1


if __name__ == "__main__":
    sys.exit(main())
