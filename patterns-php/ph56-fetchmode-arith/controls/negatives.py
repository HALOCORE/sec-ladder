#!/usr/bin/env python3
"""ph56 control -- **THE MUTANTS THAT MUST FAIL TO VERIFY.**

    python3 patterns-php/ph56-fetchmode-arith/controls/negatives.py
    python3 patterns-php/ph56-fetchmode-arith/controls/negatives.py --emit r1
    python3 patterns-php/ph56-fetchmode-arith/controls/negatives.py --selftest

⚠⚠ **A GREEN `verus.rs` IS NOT EVIDENCE THAT ITS `requires` ARE LOAD-BEARING.**
`PROTOCOL_PHP.md` §H: a gate run EXERCISES a validator on the things that pass;
it does not ATTACK it. Every mutant below removes something the row claims is
necessary, and **each must FAIL** -- if one verifies, the claim it defends was
decoration.

| mutant | what it removes | what it defends |
|---|---|---|
| `r1` | ⭐⭐⭐ `1e708a5aeb30`'s three lines -- the `BP_VAR_IS` guard, from the exec arm AND from `s_parse_ok` together, i.e. the file becomes R1 | **`operand_present`**, the row's whole obligation. Without the guard the compile pass can emit `ZEND_ISSET_ISEMPTY_DIM_OBJ` with an `IS_UNUSED` op2, so `zunwrap`'s `requires t.is_some()` cannot be discharged and this row's central `unsafe` is unlicensed. **It must fail on the assert that re-establishes `operand_present`, and WHERE it fails is checked, not just THAT it fails** |
| `noinv` | `operand_present` from the EXECUTOR loop's invariant | that the invariant is CONSUMED rather than merely established. A property proved and never used is decoration, and this is the mutant that tells the two apart |
| `nocap` | the `nops + 1 + chain > MAX_OPS` break | `oset`'s `requires i < MAX_OPS`, i.e. the frame-array bound that `c/main.c`'s `stride_w <= 512` puts in the DRIVER rather than in either pass |
| `noclamp` | the `if nstmt > MAX_STMT { nstmt = MAX_STMT; }` clamp | ⭐ the kernel's ONLY defence against a window bigger than the op_array, now that the `len <= 8 * MAX_STMT` precondition is gone. `ph55` puts that bound in a `requires`; this row ESTABLISHES it in the code, and this mutant is what says the code really does |
| `nobuf` | `off + len <= buf@.len()` -- the kernel's **one remaining** precondition | `bget`'s `requires i < v@.len()`, i.e. the driver's own contract with the kernel. ⚠ It is the only `requires` the kernel has: the first draft carried `ph55`'s other two and the gate's `req-mut` stage measured both NOT load-bearing, so they were deleted rather than kept |

⭐ **AND ONE CONTROL THAT IS NOT A MUTANT**: `pristine` re-verifies the SHIPPED
`verus.rs`, plain and under `--cfg slb_twin`, and fails if either moves off
66/0 or 76/0. Without it a run in which Verus was broken for every input would
report five mutants failing and look like a pass.

⚠ `--emit <name>` writes the mutant and prints its path without running Verus,
so a reader can look at one.

§H: the verdict function is a function so it can be attacked, and `--selftest`
drives it over synthetic outcomes -- **ten must-FIRE and five must-NOT-fire**.
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))

sys.path.insert(0, HERE)
import _pin  # noqa: E402

#: ⚠ TWO LEVELS BELOW THE REPO ROOT, and that is load-bearing: `verus.rs`
#: reaches the shared driver with `#[path = "../../common/driver.rs"]`, which
#: resolves relative to the SOURCE FILE. A mutant at any other depth does not
#: compile and the "must fail" would be the script's failure, not the mutant's.
SCRATCH = os.path.join(ROOT, ".temp", "php56neg")
VERUS_RUN = os.path.join(ROOT, "verus_run.py")

#: What the SHIPPED file must say, so that a broken toolchain cannot look like a
#: clean sweep of failing mutants.
PRISTINE_PLAIN = (66, 0)
PRISTINE_TWIN = (76, 0)

#: `name -> [(needle, replacement, expected hit count), ...]`. The hit count is
#: asserted, so a mutant that did not bite -- because `verus.rs` was respelled --
#: is REFUSED rather than reported as a pass.
MUTANTS = {
    # ⭐⭐⭐ THE ROW. `1e708a5aeb30` is three lines and this deletes them from
    # BOTH sides at once: the spec predicate that says which arms ask the
    # question, and the exec arm that asks it. Deleting only one would fail for
    # the boring reason (the exec code stops matching its own `ensures`).
    "r1": [
        ("    if ty == BP_R || ty == BP_IS || ty == BP_UNSET {",
         "    if ty == BP_R || ty == BP_UNSET {   // MUTANT `r1`: BP_VAR_IS no longer asks",
         1),
        ("""        if o.opcode == FETCH_DIM_W && o.op2_type == T_UNUSED {
            return false;
        }
        o.opcode = o.opcode.wrapping_add(6); // :764  /* 3+3 */""",
         """        // MUTANT `r1`: 1e708a5aeb30's three lines are GONE. This is
        // `case BP_VAR_IS:` exactly as PHP 5.0.0 ships it.
        o.opcode = o.opcode.wrapping_add(6); // :764  /* 3+3 */""",
         1),
    ],
    # The invariant is ESTABLISHED by the compile loop and CONSUMED here. Remove
    # the consumption point and `zunwrap` loses its precondition.
    "noinv": [
        ("""                ts@.len() == MAX_STMT,
                operand_present(ops@, nops as int),
                e_run(""",
         """                ts@.len() == MAX_STMT,
                // MUTANT `noinv`: the executor no longer carries the compile
                // pass's guarantee, so nothing discharges zunwrap.
                e_run(""",
         1),
    ],
    "nocap": [
        ("""        if nops + 1 + chain > MAX_OPS {""",
         """        if false {   // MUTANT `nocap`: the frame array's bound is GONE""",
         1),
    ],
    "noclamp": [
        ("""    let mut nstmt: usize = len / 8;
    if nstmt > MAX_STMT {
        nstmt = MAX_STMT;
    }""",
         """    let nstmt: usize = len / 8;   // MUTANT `noclamp`: the clamp is GONE""",
         1),
    ],
    "nobuf": [
        ("""        off + len <= buf@.len(),
    ensures""",
         """        // MUTANT `nobuf`: the kernel's ONE precondition is GONE.
    ensures""",
         1),
    ],
}

#: Mutants that are expected to VERIFY. ⭐ EMPTY ON THIS ROW, AND THAT IS A
#: MEASUREMENT: the first draft of `verus.rs` carried `ph55`'s three
#: preconditions and the gate's own `req-mut` stage deleted `16 <= len` and
#: `len <= 8 * MAX_STMT` and found the file still verified 66/0. They were
#: REMOVED rather than kept as expected-to-verify mutants, so the kernel now
#: has exactly one precondition and every mutant here must fail. The arm that
#: checks a declared-to-verify mutant stays in `negative_problems` and is
#: exercised synthetically, because the day a row declares one is the day it
#: needs checking. `../NOTES.md` §11.8.
EXPECT_VERIFIES = set()

#: ⭐ WHERE `r1` must fail, and not merely THAT it fails. A mutant that failed
#: somewhere else would mean the deletion broke something other than the row's
#: obligation, and the verdict would be worth nothing.
R1_EXPECT = "ISSET_ISEMPTY_DIM_OBJ"


def run_verus(path, extra=()):
    r = subprocess.run([sys.executable, VERUS_RUN, path, *extra],
                       capture_output=True, text=True, timeout=3600)
    txt = r.stdout + r.stderr
    m = re.search(r"verification results:: (\d+) verified, (\d+) errors", txt)
    return {"rc": r.returncode,
            "verified": int(m.group(1)) if m else None,
            "errors": int(m.group(2)) if m else None,
            "text": txt[-2500:]}


def materialise(name):
    src = os.path.join(PDIR, "verus.rs")
    txt = open(src, encoding="utf-8").read()
    for old, new, want in MUTANTS[name]:
        n = txt.count(old)
        if n != want:
            raise AssertionError(
                f"mutant `{name}`: the anchor {old[:48]!r} matched {n} times, "
                f"want {want} -- verus.rs has been respelled and this mutant "
                f"does not bite, so a 'must fail' verdict from it would mean "
                f"nothing")
        txt = txt.replace(old, new)
    os.makedirs(SCRATCH, exist_ok=True)
    out = os.path.join(SCRATCH, f"{name}.rs")
    open(out, "w", encoding="utf-8").write(txt)
    return out


# ---- the verdict, factored so it can be ATTACKED ----------------------------

def negative_problems(results, pristine, expect_ok=None):
    """`results` is `{mutant: {"errors": n|None, "rc": int, "text": str}}` and
    `pristine` is `{"plain": (v, e), "twin": (v, e)}` or `None`.

    1. ⛔ a mutant that VERIFIES when it must not is the failure this file
       exists to catch: the thing it removed was not load-bearing and the row's
       claim about it is decoration.
    2. a mutant Verus could not evaluate at all (no `verification results` line)
       is NOT a pass -- a probe that cannot evaluate must say so.
    3. ⭐ `r1` must fail ON THE ROW'S OBLIGATION. If it fails somewhere else the
       deletion broke something other than `operand_present` and the verdict is
       about a different claim.
    4. ⛔ a mutant declared EXPECT_VERIFIES that FAILS is also a finding: the
       row wrote down an expectation and measurement refuted it.
    5. the shipped file must still verify, plain and twin, at the pinned
       counts. Without this a broken Verus reads as a clean sweep.
    """
    expect_ok_set = EXPECT_VERIFIES if expect_ok is None else expect_ok
    p = []
    for name, r in sorted(results.items()):
        if r.get("skipped"):
            continue
        expect_ok = name in expect_ok_set
        if r.get("errors") is None:
            p.append(f"2. mutant `{name}`: Verus printed no verification results "
                     f"(rc {r.get('rc')}) -- it could not be evaluated, which is "
                     f"not the same as failing")
            continue
        if r["errors"] == 0 and not expect_ok:
            p.append(f"1. mutant `{name}` VERIFIES with 0 errors. It removes "
                     f"something this row claims is necessary, so either the "
                     f"claim is wrong or the mutant no longer bites")
        if r["errors"] != 0 and expect_ok:
            p.append(f"4. mutant `{name}` FAILS, and this row declared that it "
                     f"would verify. The declaration is refuted and the reason "
                     f"has to be read, not patched")
        if name == "r1" and r["errors"] and R1_EXPECT not in r.get("text", ""):
            p.append(f"3. mutant `r1` fails, but NOT on the row's obligation: "
                     f"the diagnostic does not mention {R1_EXPECT!r}. Deleting "
                     f"1e708a5aeb30 broke something other than "
                     f"`operand_present`")
    if pristine is not None:
        if tuple(pristine.get("plain") or ()) != PRISTINE_PLAIN:
            p.append(f"5. the SHIPPED verus.rs reports {pristine.get('plain')} "
                     f"plain, pinned {PRISTINE_PLAIN}. Every mutant verdict in "
                     f"this run is about a different file from the one the "
                     f"gate measured")
        if tuple(pristine.get("twin") or ()) != PRISTINE_TWIN:
            p.append(f"5. the SHIPPED verus.rs reports {pristine.get('twin')} "
                     f"under --cfg slb_twin, pinned {PRISTINE_TWIN}")
    return p


def selftest():
    fail = {"errors": 1, "rc": 1, "text": "assertion failed ... ISSET_ISEMPTY_DIM_OBJ"}
    verifies = {"errors": 0, "rc": 0, "text": "verified"}
    good = {k: dict(fail) for k in MUTANTS}
    good_pr = {"plain": PRISTINE_PLAIN, "twin": PRISTINE_TWIN}
    #: `(label, results, pristine, expect_ok_override, must_fire, arm)`.
    #: ⚠ `expect_ok_override` is what lets arm 4 be exercised at all now that
    #: `EXPECT_VERIFIES` is empty on the shipped tree: the arm is real, the row
    #: simply has no mutant that uses it, and a verdict arm nobody can attack is
    #: the thing §H exists to stop.
    cases = [
        ("P1 the shipped shape", good, good_pr, None, False, None),
        ("N1 the row's own mutant verifies",
         {**good, "r1": dict(verifies)}, good_pr, None, True, "1."),
        ("N2 the consumption mutant verifies",
         {**good, "noinv": dict(verifies)}, good_pr, None, True, "1."),
        ("N3 the capacity mutant verifies",
         {**good, "nocap": dict(verifies)}, good_pr, None, True, "1."),
        ("N4 the clamp mutant verifies",
         {**good, "noclamp": dict(verifies)}, good_pr, None, True, "1."),
        ("N5 the precondition mutant verifies",
         {**good, "nobuf": dict(verifies)}, good_pr, None, True, "1."),
        ("N6 a mutant could not be evaluated",
         {**good, "nocap": {"errors": None, "rc": 2, "text": ""}}, good_pr,
         None, True, "2."),
        ("N7 r1 fails for the wrong reason",
         {**good, "r1": {"errors": 1, "rc": 1,
                         "text": "error: precondition not satisfied"}},
         good_pr, None, True, "3."),
        ("N8 a mutant DECLARED to verify fails",
         good, good_pr, {"nobuf"}, True, "4."),
        ("N9 the shipped file moved, plain",
         good, {"plain": (65, 1), "twin": PRISTINE_TWIN}, None, True, "5."),
        ("N10 the shipped file moved, twin",
         good, {"plain": PRISTINE_PLAIN, "twin": (75, 1)}, None, True, "5."),
        ("P2 mutants failing with different error counts",
         {k: {"errors": i + 1, "rc": 1, "text": R1_EXPECT}
          for i, k in enumerate(MUTANTS)}, good_pr, None, False, None),
        ("P3 pristine not measured (skipped)", good, None, None, False, None),
        ("P4 a mutant refused by its own anchor check",
         {**good, "nocap": {"skipped": True}}, good_pr, None, False, None),
        ("P5 a DECLARED-to-verify mutant that verifies",
         {**good, "nobuf": dict(verifies)}, good_pr, {"nobuf"}, False, None),
    ]
    bad = []
    for label, res, pr, expect_ok, must_fire, arm in cases:
        got = negative_problems(res, pr, expect_ok)
        if bool(got) != must_fire:
            bad.append(f"selftest {label}: fired={bool(got)}, want {must_fire} ({got})")
        elif must_fire and arm and not any(g.startswith(arm) for g in got):
            bad.append(f"selftest {label}: fired on {[g[:2] for g in got]}, want {arm}")
    return bad


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--emit", choices=sorted(MUTANTS),
                    help="write one mutant and print its path; do not run Verus")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--pristine", action="store_true", default=True,
                    help="re-verify the SHIPPED verus.rs too (default on)")
    ap.add_argument("--no-pristine", dest="pristine", action="store_false")
    args = ap.parse_args()

    if args.emit:
        print(materialise(args.emit))
        return 0

    problems = list(selftest())
    print("0. §H -- THE VERDICT ARM, ATTACKED OVER SYNTHETIC OUTCOMES")
    print(f"   selftest {'PASS' if not problems else 'FAIL'}   "
          f"15 arms (10 must-FIRE, 5 must-NOT-fire)")
    for p in problems:
        print(f"     *** {p}")
    if args.selftest:
        return 1 if problems else 0

    pristine = None
    if args.pristine:
        print("\n1. THE SHIPPED FILE -- the must-NOT-fire control that makes "
              "every verdict below worth something")
        shipped = os.path.join(PDIR, "verus.rs")
        a = run_verus(shipped)
        b = run_verus(shipped, ("--cfg", "slb_twin"))
        pristine = {"plain": (a["verified"], a["errors"]),
                    "twin": (b["verified"], b["errors"])}
        print(f"   verus.rs     {a['verified']} verified / {a['errors']} errors"
              f"   (pinned {PRISTINE_PLAIN[0]}/{PRISTINE_PLAIN[1]})")
        print(f"   --cfg twin   {b['verified']} verified / {b['errors']} errors"
              f"   (pinned {PRISTINE_TWIN[0]}/{PRISTINE_TWIN[1]})")

    print("\n2. THE MUTANTS -- each removes something, and the row says in "
          "advance which must fail")
    results = {}
    for name in sorted(MUTANTS):
        try:
            path = materialise(name)
        except AssertionError as e:
            problems.append(str(e))
            results[name] = {"skipped": True, "error": str(e)}
            print(f"   {name:11s} MUTANT REFUSED -- {e}")
            continue
        r = run_verus(path)
        results[name] = r
        want = "verify" if name in EXPECT_VERIFIES else "FAIL"
        got = "verifies" if r["errors"] == 0 else "fails"
        mark = "as declared" if (got.startswith(want.lower()[:4])
                                 or (want == "FAIL" and got == "fails")) else "⛔"
        print(f"   {name:11s} {str(r['verified']):>4s} verified / "
              f"{str(r['errors']):>3s} errors   must {want:6s} -> {got}  {mark}")
        if name == "r1" and r["errors"]:
            line = next((l for l in r["text"].splitlines()
                         if l.startswith("error:")), "(no error line)")
            print(f"                 and it fails HERE: {line}")

    problems.extend(negative_problems(results, pristine))
    out = {"mutants": results, "pristine": pristine, "problems": problems,
           "expect_verifies": sorted(EXPECT_VERIFIES)}
    dst = os.path.join(HERE, "negatives.json")
    out.update(_pin.pin(
        ['verus.rs', 'controls/negatives.py'],
        'python3 patterns-php/ph56-fetchmode-arith/controls/negatives.py',
        'verus.rs (every mutant is a substitution ON it, and the hit counts are '
        'asserted) and this script. NOT inputs/: no mutant is RUN, only verified.'))
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
