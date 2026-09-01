#!/usr/bin/env python3
"""p49 CONTROLS: the R5 mutation battery -- **an ATTACK arm that must FAIL, a
VACUITY arm, the three-cell spec-weaken experiment, and the two arms that show
this row's NEW obligation is real.**

    python3 patterns/p49-interned-pool/controls/proof_mutants.py
    python3 patterns/p49-interned-pool/controls/proof_mutants.py --only M1-safety-line

`.memory/02-bench-rules.md`: *"Every R5 owes an ATTACK arm that must FAIL to
verify, not just a deletion arm."* Two instances in this project's own history
say why: `p42`'s ghost ledger verified `18/0` while leaking, and `TASK_136`'s
`ARM_C` was discharged by `fn arm_c() -> u8 { 9 }`.

WHAT EACH KIND OF ARM IS FOR
----------------------------
  * **ATTACK arms** put `c/kernel.c`'s ACTUAL BUG into the R5 and require the
    proof to reject it. `M1` deletes the copy-on-write block from the exec code
    and nothing else, so what survives IS `c/kernel.c`.
  * **VACUITY arms** ask what the CHEAPEST body satisfying the postcondition is.
    `M2` is `return 0;` and it must FAIL.
  * ⚠⚠ **`M3-spec-weaken` MUST VERIFY, AND THAT IS THE POINT.** It deletes the
    safety line from the exec code AND from the abstract machine `step`, so the
    two agree again -- and it verifies. **That is the honest measurement of what
    this R5 buys: the safety line is load-bearing against the SPECIFICATION and
    against nothing else**, because p49 allocates nothing and there is no linear
    resource whose consumption could force it. `p32`'s finding, on a different
    bug class.
  * ⚠⚠⚠ **AND `M3` IS ONLY A RESULT BESIDE `M1` AND `X1`.** Three cells of one
    experiment: **exec-only -> FAIL** (`M1`), **spec-only -> FAIL** (`X1`),
    **both -> VERIFY** (`M3`). `X1` is what rules out *"`step`'s branch is
    inert"*; `p32`'s battery shipped without its equivalent until `TASK_147`,
    and a review had to find it.

  * ⚠⚠ **`X2` AND `X3` ARE THIS ROW'S OWN PAIR, AND THEY ARE ABOUT THE ONE
    OBLIGATION `TASK_160` §8 PREDICTED NOTHING IN THIS TREE STATES.**
    `copy_bytes` carries `requires src + w <= dst` -- a DISJOINTNESS
    precondition -- discharged out of `wf_prov`'s clause that a SHARED buffer
    lies wholly inside the arena. `X3` deletes the `requires`; `X2` deletes the
    invariant clause that discharges it. **Both must FAIL, and they fail on the
    MEMORY-SAFETY facts rather than on the answer** -- X3 on the copy loop's own
    `src + w <= dst` invariant, X2 on the two memory-safety postconditions
    `lemma_rec_in_pool` exports. That is the contrast this battery exists to
    draw, and it is drawn against X1 (which fails FUNCTIONALLY, on
    `st_out =~= step(..)`) rather than against M1, whose diagnostic at every
    budget tried was the solver's own resource limit. If either of X2/X3
    verified, the disjointness obligation would be decoration.

  * **MUST-VERIFY controls** (`M0`) make sure a failure is caused by the
    mutation and not by an unachievable postcondition or a broken harness.

⚠ Each arm is a full Verus run; budget a few minutes. Mutant sources are written
under `.temp/p49mut/` and deleted on success (`.memory/00-environment.md`
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
MDIR = os.path.join(REPO, ".temp", "p49mut")

SRC = os.path.join(PDIR, "verus.rs")

# ---------------------------------------------------------------- mutants ---
EXEC_COW = """                if arr_get_unchecked(&rshd, t) == 1 {
                    let rl: u8 = arr_get_unchecked(&rlen, t);
                    if pbump + (rl as usize) > MEM {
                        SENT
                    } else {
                        let ro: u8 = arr_get_unchecked(&roff, t);
                        copy_bytes(&mut mem, pbump, ro as usize, rl);
                        arr_set_unchecked(&mut roff, t, pbump as u8);
                        arr_set_unchecked(&mut rshd, t, 0);
                        arr_set_unchecked(&mut mem, pbump, 0);
                        pbump = pbump + rl as usize;
                        2
                    }
                } else {
                    let ro: u8 = arr_get_unchecked(&roff, t);
                    arr_set_unchecked(&mut mem, ro as usize, 0);
                    2
                }"""
EXEC_NOCOW = """                {
                    let ro: u8 = arr_get_unchecked(&roff, t);
                    arr_set_unchecked(&mut mem, ro as usize, 0);
                    2
                }"""

SPEC_COW = """            if st.rshd[t] == 1u8 {
                if st.pbump + (st.rlen[t] as int) > MEM as int {
                    (st, SENT)
                } else {
                    (
                        St {
                            mem: copied(
                                st.mem,
                                st.pbump,
                                st.roff[t] as int,
                                st.rlen[t] as int,
                            ).update(st.pbump, 0u8),
                            roff: st.roff.update(t, st.pbump as u8),
                            rshd: st.rshd.update(t, 0u8),
                            pbump: st.pbump + (st.rlen[t] as int),
                            ..st
                        },
                        2u64,
                    )
                }
            } else {
                (St { mem: st.mem.update(st.roff[t] as int, 0u8), ..st }, 2u64)
            }"""
SPEC_NOCOW = """            (St { mem: st.mem.update(st.roff[t] as int, 0u8), ..st }, 2u64)"""

PROV_CLAUSE = """    &&& forall|t: int|
        0 <= t < st.nrec && (#[trigger] st.rshd[t]) == 1u8 ==> (st.roff[t] as int) + (
        st.rlen[t] as int) <= ARENA as int
"""

COPY_REQ = """    requires
        src + w <= dst,
        dst + w <= MEM,
"""
COPY_REQ_WEAK = """    requires
        dst + w <= MEM,
"""

KERNEL_OPEN = """        r == intern_fold(buf@, off as int, len as int),
{
    // Ghost only"""
KERNEL_CONST = """        r == intern_fold(buf@, off as int, len as int),
{
    return 0;
    // Ghost only"""

LEMMA_CALL = """                proof {
                    lemma_rec_in_pool(st_in, t as int);
                }
"""

#: ⚠⚠ THE TWO SPELLINGS OF `lemma_find`'s SECOND ENSURES, and the pair below is
#: this row's Verus finding. The MERGED form joins two facts with `&&` inside one
#: clause; the SPLIT form states them as two clauses. **They are not the same
#: thing for the solver** -- see M4/M5.
SPLIT_FIND = """pub proof fn lemma_find(ek: Seq<u8>, el: Seq<u8>, k: int, n: int, key: u8, w: u8)
    requires
        0 <= k <= n,
    ensures
        k <= find_from(ek, el, k, n, key, w) <= n,
        find_from(ek, el, k, n, key, w) < n ==> ek[find_from(ek, el, k, n, key, w)] == key,
        find_from(ek, el, k, n, key, w) < n ==> el[find_from(ek, el, k, n, key, w)] == w,
    decreases n - k,
{
    if k < n && !(ek[k] == key && el[k] == w) {
        lemma_find(ek, el, k + 1, n, key, w);
    }
}"""
MERGED_FIND = """pub proof fn lemma_find(ekey: Seq<u8>, elen: Seq<u8>, k: int, nent: int, key: u8, w: u8)
    requires
        0 <= k <= nent,
    ensures
        k <= find_from(ekey, elen, k, nent, key, w) <= nent,
        find_from(ekey, elen, k, nent, key, w) < nent ==> ekey[find_from(
            ekey,
            elen,
            k,
            nent,
            key,
            w,
        )] == key && elen[find_from(ekey, elen, k, nent, key, w)] == w,
    decreases nent - k,
{
    if k < nent && !(ekey[k] == key && elen[k] == w) {
        lemma_find(ekey, elen, k + 1, nent, key, w);
    }
}"""

# (name, kind, expect, [(find, replace), ...], why)
MUTANTS = [
    ("M0-control", "control", "verify", [],
     "the shipped file, run through the same harness and the same flags. If "
     "this does not verify, nothing below means anything."),
    ("M1-safety-line", "attack", "fail", [(EXEC_COW, EXEC_NOCOW)],
     "THE ATTACK ARM, and it is the row's bug exactly: delete the "
     "copy-on-write block from the exec code and nothing else. What survives is "
     "`c/kernel.c` -- a kernel that writes through a buffer another record "
     "owns. It must FAIL, and it does. ⚠⚠ **WHAT IT FAILS ON IS NOT "
     "ESTABLISHED HERE, AND AN EARLIER DRAFT OF THIS TEXT CLAIMED IT WAS.** At "
     "`--rlimit 200` the diagnostic is `while loop: Resource limit (rlimit) "
     "exceeded` on the kernel\'s own op loop -- the solver runs out of budget "
     "before it can name a failing clause -- and a probe at `--rlimit 4000` was "
     "still running after about twenty-five minutes and was terminated without "
     "an answer (`.temp/t161/m1_rlimit4000.log`). **So what is measured is that "
     "the file does not verify, and nothing finer.** ⚠ What IS established "
     "elsewhere is the contrast this arm is for: X1 fails with a FUNCTIONAL "
     "diagnostic and X3 with a memory-safety-shaped one, so a battery that read "
     "M1\'s rlimit message as *the postcondition failed* would be reading a "
     "statement about the solver\'s SEARCH as a statement about the proof. "
     "⚠ And note what the MUTANT does not do -- undefined behaviour. Every "
     "index it forms is still in range, which is why ASan, UBSan and Miri are "
     "all silent on the shipped bug."),
    ("M2-constant-body", "vacuity", "fail", [(KERNEL_OPEN, KERNEL_CONST)],
     "`.memory/04-verus.md`'s vacuity probe in its sharp form -- **what is the "
     "CHEAPEST body that satisfies the postcondition?** `TASK_137` discharged "
     "`TASK_136`'s ARM_C with `fn arm_c() -> u8 { 9 }`. Here the cheapest body "
     "is `return 0;` and it must FAIL, because `intern_fold` is a function of "
     "the window bytes and no constant equals it."),
    ("M3-spec-weaken", "must-verify", "verify",
     [(EXEC_COW, EXEC_NOCOW), (SPEC_COW, SPEC_NOCOW)],
     "⚠⚠⚠ **THE ARM THAT IS SUPPOSED TO VERIFY.** Delete the "
     "copy-on-write from the exec code AND from `step`, so the specification "
     "describes the BUGGY kernel. It verifies. **That is the honest statement "
     "of what this R5 buys**: the safety line is load-bearing against the "
     "SPECIFICATION and against nothing else, because p49 allocates nothing and "
     "has no linear resource whose consumption could force it. Compare p29, "
     "whose `live[cur] = 0` cannot be deleted at any price. `p32` is the "
     "precedent and `p42` the one before it. ⚠ Read it with X1 below: M1, "
     "X1 and M3 are three cells of ONE experiment and M3 alone is an "
     "assertion."),
    ("X1-spec-only-weaken", "attack", "fail", [(SPEC_COW, SPEC_NOCOW)],
     "⚠⚠ **THE THIRD CELL, and it is what turns M3 from an assertion "
     "into a result.** Delete the copy-on-write from the abstract machine "
     "`step` ONLY, leaving the exec code intact -- a postcondition true of the "
     "WRONG program. It must FAIL. With M1 (exec only -> fail) and M3 (both -> "
     "verify) that gives EXEC-ONLY FAIL / SPEC-ONLY FAIL / BOTH VERIFY, which "
     "is the difference between *the proof does not care about the safety line* "
     "-- false -- and *the safety line is load-bearing against the "
     "specification and against nothing else* -- true. ✅ **Measured "
     "diagnostic, and it is the FUNCTIONAL one**: `assertion failed` on "
     "`st_out =~= step(st_in, c, a).0` and on `v == step(st_in, c, a).1`, both "
     "inside the op loop\'s proof block -- the exec state stops being what the "
     "weakened machine says it is."),
    ("X2-provenance-invariant", "deletion", "fail", [(PROV_CLAUSE, "")],
     "⚠⚠ **THIS ROW'S OWN ARM.** Delete `wf_prov`'s clause that a "
     "SHARED record's content lies wholly inside the interning arena. Nothing "
     "then discharges `copy_bytes`'s `src + w <= dst`, so the copy-on-write "
     "loses its licence. It must FAIL -- and it fails on the MEMORY-SAFETY "
     "facts rather than on the answer. **That is what makes the disjointness "
     "obligation real "
     "rather than decorative**, and `TASK_160` §8 predicted that nothing "
     "in this tree states one. ✅ **Measured diagnostic, and it is NOT the "
     "one this arm was written expecting**: the failure lands on "
     "`lemma_rec_in_pool`\'s OWN postconditions -- `roff[t] + rlen[t] <= MEM` "
     "and `rshd[t] == 1 ==> roff[t] + rlen[t] <= ARENA` -- rather than on "
     "`copy_bytes`\'s precondition at the call site. That is the same fact one "
     "step earlier: the lemma is where those two memory-safety facts are "
     "DERIVED from `wf_prov`, so deleting the clause stops them being derivable "
     "before any caller gets to ask. ⚠ **It therefore does NOT, on its own, "
     "demonstrate that `copy_bytes`\'s precondition becomes undischargeable** "
     "-- X3 is the arm that shows that, from the other side."),
    ("X3-copy-disjointness", "deletion", "fail", [(COPY_REQ, COPY_REQ_WEAK)],
     "the same obligation from the other side: delete `src + w <= dst` from "
     "`copy_bytes`'s own `requires`, leaving `dst + w <= MEM`. The body can then "
     "no longer show that the byte it reads out of the pool it is writing to is "
     "the byte the specification names -- `lemma_copied_below` needs "
     "`0 <= i < dst`. It must FAIL. ✅ **Measured diagnostic**: "
     "`invariant not satisfied before loop` on `src + w <= dst` -- the copy "
     "loop\'s own invariant, which the deleted precondition was the only thing "
     "establishing. ⚠ Together with X2 this is the pair "
     "`.memory/04-verus.md` asks for: the precondition demands something, and "
     "something has to discharge it -- X3 shows the demand is real, X2 shows "
     "the discharge is."),
    ("M4-lemma-rec-in-pool", "must-verify", "verify", [(LEMMA_CALL, "", 2)],
     "⚠⚠ **AN ARM THAT IS SUPPOSED TO VERIFY, AND IT SURPRISED THIS "
     "FILE'S AUTHOR.** Delete BOTH `lemma_rec_in_pool` calls -- the BREAK arm's "
     "and the READ arm's. It VERIFIES, so the lemma is NOT load-bearing in the "
     "shipped file: it is a solver HINT. The arm was written expecting `fail` "
     "and the run said `verify`, which is recorded here rather than quietly "
     "relaxed. **The reason is M5**: two independent edits cure the same solver "
     "blow-up and the shipped file carries BOTH, so neither is necessary given "
     "the other."),
    ("M5-both-hints", "attack", "fail",
     [(LEMMA_CALL, "", 2), (SPLIT_FIND, MERGED_FIND)],
     "⚠⚠⚠ **THE ARM THAT MAKES M4 A RESULT, AND IT IS THIS ROW'S "
     "VERUS FINDING.** Delete the `lemma_rec_in_pool` calls AND respell "
     "`lemma_find`'s second `ensures` from TWO CLAUSES back to ONE clause "
     "joined by `&&` -- semantically the same postcondition. It FAILS, with "
     "`while loop: Resource limit (rlimit) exceeded` on the kernel's own op "
     "loop. **So `A && B` in one `ensures` clause and `A`, `B` as two clauses "
     "are NOT the same thing for the solver**, and either that respelling or "
     "the lemma is enough on its own. ⚠ The first complete verus.rs had the "
     "merged spelling and no lemma, and reported exactly this error at the "
     "DEFAULT budget; at `--rlimit 400` the real gap appeared "
     "(`fold_bytes`'s `base + w <= MEM`, undischarged on the READ path). "
     "**The rlimit message is a diagnostic about the solver's SEARCH, not "
     "about the proof's difficulty**, and reading it as the latter would have "
     "sent this build down a much longer road. ../NOTES.md 8c."),
]


# ⚠ `--rlimit 200`, and it is not padding. At the DEFAULT limit a mutant
# whose real failure is a PRECONDITION can report only `Resource limit (rlimit)
# exceeded` on the enclosing loop -- measured here on the shipped file itself
# while it was being written: before `lemma_rec_in_pool` existed, `verus.rs`
# reported the rlimit message and NOT the missing `base + w <= MEM` that was
# actually wrong, and the real diagnostic appeared only at `--rlimit 400`.
# ⚠⚠ **The rlimit exceedance was a MISSING CASE SPLIT, not genuine size**: with
# the lemma in place the SHIPPED file verifies at the DEFAULT limit in about
# four seconds, which is why no `#[verifier::rlimit(..)]` attribute ships (p28
# needs 400 on its kernel; p49 needs none). The flag here is for the MUTANTS'
# diagnostics, and `M0` is run with it so the battery's control sees the same
# budget as its arms.
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
    for rel in ("patterns/p49-interned-pool/verus.rs",
                "patterns/p49-interned-pool/controls/proof_mutants.py"):
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
        for sub in subs:
            find, repl = sub[0], sub[1]
            want = sub[2] if len(sub) > 2 else 1
            got_n = txt.count(find)
            if got_n != want:
                raise SystemExit(f"proof_mutants: {name}: expected exactly "
                                 f"{want} occurrence(s), found {got_n} -- "
                                 f"verus.rs moved under this script:\n"
                                 f"{find[:200]}")
            txt = txt.replace(find, repl, want)
        path = os.path.join(MDIR, f"{name}.rs")
        open(path, "w").write(txt)
        res = run_verus(path)
        got = "verify" if (res["errors"] == 0 and res["rc"] == 0) else "fail"
        ok = got == expect
        rows.append({"mutant": name, "kind": kind, "expected": expect,
                     "got": got, "ok": ok, **res, "why": why})
        print(f"  {name:26s} {kind:11s} expect={expect:6s} got={got:6s} "
              f"{'OK ' if ok else 'XX '} "
              f"{res['verified']}/{res['errors']} {res['error_kinds']}")
    doc = {"pin": {"regenerate":
                   "python3 patterns/p49-interned-pool/controls/"
                   "proof_mutants.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "rlimit": RLIMIT,
           "mutants": rows,
           "invariant":
               "The ATTACK arm (M1, the shipped bug) and the VACUITY arm (M2, a "
               "constant body) both FAIL. The SPEC-WEAKEN arm (M3) VERIFIES, "
               "and that is the finding rather than a defect: p49's safety line "
               "is load-bearing against the specification alone, because the "
               "pattern allocates nothing and has no linear resource to "
               "consume. THE THREE-CELL FORM IS WHAT MAKES THAT A RESULT: M1 "
               "exec-only FAIL, X1 spec-only FAIL, M3 both VERIFY. X2 and X3 "
               "are this row's own pair, on the DISJOINTNESS precondition "
               "`copy_bytes` carries and `wf_prov` discharges: both FAIL, X3 "
               "on the copy loop's own `src + w <= dst` invariant and X2 on the "
               "two memory-safety postconditions lemma_rec_in_pool exports. M4 VERIFIES and M5 FAILS: two independent "
               "edits -- the lemma_rec_in_pool calls, and spelling "
               "lemma_find's second ensures as TWO clauses instead of one "
               "`&&`-joined clause -- each cure the same solver blow-up, so "
               "neither is necessary given the other and the shipped file "
               "carries both.",
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
