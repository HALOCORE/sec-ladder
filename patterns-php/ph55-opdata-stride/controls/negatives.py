#!/usr/bin/env python3
"""ph55 control -- **THE MUTANTS THAT MUST FAIL TO VERIFY.**

    python3 patterns-php/ph55-opdata-stride/controls/negatives.py
    python3 patterns-php/ph55-opdata-stride/controls/negatives.py --emit nofixup
    python3 patterns-php/ph55-opdata-stride/controls/negatives.py --selftest

⚠⚠ **A GREEN `verus.rs` IS NOT EVIDENCE THAT ITS `requires` ARE LOAD-BEARING.**
`PROTOCOL_PHP.md` §H: a gate run EXERCISES a validator on the things that pass;
it does not ATTACK it. Every mutant below removes something the row claims is
necessary, and **each must FAIL** — if one verifies, the claim it defends was
decoration.

| mutant | what it removes | what it defends |
|---|---|---|
| `nofixup` | the `emit_from(&mut ops, nops, 0);` call | ⭐⭐ **`ok_from`** — the invariant `4f68f3774c34` restores. Without the emitter pass nothing establishes that the PC lands on an instruction word, so `hunwrap`'s `requires t.is_some()` cannot be discharged and the row's central `unsafe` is unlicensed |
| `nostride` | `4f68f3774c34`'s three lines from the error exit | the VALUE postcondition. R1's stride is a different function from `ph55_fold`, so `r == ph55_fold(...)` must stop holding |
| `notail` | the `ops[nops-2/1].opcode = RETURN` writes | ⭐ `emit_from`'s `requires`, and through it §4(a)'s two-terminator argument — the only thing keeping the PC inside the op_array |
| `noprecond` | `16 <= len` from the kernel's `requires` | `nops >= 2`, and therefore every `nops - 2` in the decoder |

⭐ **AND ONE MUTANT THAT IS NOT A MUTANT AT ALL**: `controls/fnptr.rs` is a
standalone file whose whole point is that Verus refuses its TYPE. `--verus` runs
it and fails if Verus ever ACCEPTS it, because the day Verus grows function
pointers is the day four of this row's files should be rewritten and a stale
comment is how that gets missed.

⚠ `--emit <name>` writes the mutant and prints its path without running Verus,
so a reader can look at one.

§H: the verdict function is a function so it can be attacked, and `--selftest`
drives it over synthetic outcomes -- six must-FIRE and three must-NOT-fire.
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

#: ⚠ TWO LEVELS BELOW THE REPO ROOT, and that is load-bearing: `verus.rs` reaches
#: the shared driver with `#[path = "../../common/driver.rs"]`, which resolves
#: relative to the SOURCE FILE. A mutant at any other depth does not compile and
#: the "must fail" would be the script's failure, not the mutant's.
SCRATCH = os.path.join(ROOT, ".temp", "php55neg")
VERUS_RUN = os.path.join(ROOT, "verus_run.py")

#: `(needle, replacement, expected hit count)`. The hit count is asserted, so a
#: mutant that did not bite -- because the rung was respelled -- is REFUSED
#: rather than reported as a pass.
MUTANTS = {
    "nofixup": (
        """    emit_from(&mut ops, nops, 0);""",
        """    // MUTANT `nofixup`: the emitter pass is GONE. Nothing establishes
    // ok_from, so `hunwrap`'s `requires t.is_some()` cannot be discharged.""",
        1),
    "nostride": (
                """                if inc {
                    pc = pc + 1;
                }
                pc = pc + 1;
            } else {""",
                """                pc = pc + 1;   // MUTANT `nostride`: R1's stride
            } else {""",
                1),
    "notail": (
        """        let mut e: Op = oget(&ops, nops - 2);
        e.opcode = RETURN;
        oset(&mut ops, nops - 2, e);
        let mut e2: Op = oget(&ops, nops - 1);
        e2.opcode = RETURN;
        oset(&mut ops, nops - 1, e2);""",
        """        // MUTANT `notail`: PHP's own ZEND_RETURN / ZEND_HANDLE_EXCEPTION
        // tail is GONE, so emit_from's `requires` is unmet.""",
        1),
    "noprecond": (
        """        off + len <= buf@.len(),
        16 <= len,""",
        """        off + len <= buf@.len(),
        // MUTANT `noprecond`: `16 <= len` is GONE.""",
        1),
}

#: What Verus must say. ⚠ READ THE ERROR TEXT, NOT THE EXIT CODE
#: (`.memory/04-verus.md`): `is not supported` forces a new trusted item where
#: `postcondition not satisfied` forces only a proof.
FNPTR_EXPECT = "function pointer types"


def run_verus(path, extra=()):
    r = subprocess.run([sys.executable, VERUS_RUN, path, *extra],
                       capture_output=True, text=True, timeout=3600)
    txt = r.stdout + r.stderr
    m = re.search(r"verification results:: (\d+) verified, (\d+) errors", txt)
    return {"rc": r.returncode,
            "verified": int(m.group(1)) if m else None,
            "errors": int(m.group(2)) if m else None,
            "text": txt[-1500:]}


def materialise(name):
    src = os.path.join(PDIR, "verus.rs")
    txt = open(src, encoding="utf-8").read()
    old, new, want = MUTANTS[name]
    n = txt.count(old)
    if n != want:
        raise AssertionError(
            f"mutant `{name}`: the anchor matched {n} times, want {want} -- "
            f"verus.rs has been respelled and this mutant does not bite, so a "
            f"'must fail' verdict from it would mean nothing")
    os.makedirs(SCRATCH, exist_ok=True)
    out = os.path.join(SCRATCH, f"{name}.rs")
    open(out, "w", encoding="utf-8").write(txt.replace(old, new))
    return out


# ---- the verdict, factored so it can be ATTACKED ----------------------------

def negative_problems(results, fnptr):
    """`results` is `{mutant: {"errors": n|None, "rc": int}}`.

    1. ⛔ a mutant that VERIFIES is the failure this file exists to catch: the
       thing it removed was not load-bearing and the row's claim about it is
       decoration.
    2. a mutant Verus could not evaluate at all (no `verification results` line)
       is NOT a pass -- a probe that cannot evaluate must say so.
    3. ⭐ `controls/fnptr.rs` must still be REFUSED, and refused for the RIGHT
       REASON: the error text must name function pointer types. A different
       error means the probe has rotted into testing something else.
    4. `fnptr.rs` VERIFYING is the biggest finding this file can produce and it
       fails loudly, because it would mean four of this row's files should be
       rewritten.
    """
    p = []
    for name, r in sorted(results.items()):
        if r.get("skipped"):
            continue
        if r.get("errors") is None:
            p.append(f"2. mutant `{name}`: Verus printed no verification results "
                     f"(rc {r.get('rc')}) -- it could not be evaluated, which is "
                     f"not the same as failing")
        elif r["errors"] == 0:
            p.append(f"1. mutant `{name}` VERIFIES with 0 errors. It removes "
                     f"something this row claims is necessary, so either the "
                     f"claim is wrong or the mutant no longer bites")
    if fnptr is not None:
        if fnptr.get("errors") == 0 or fnptr.get("rc") == 0:
            p.append("4. ⭐ controls/fnptr.rs VERIFIES. Verus now supports "
                     "function pointer types, so this row's whole Rust-side "
                     "representation argument (NOTES.md §7) is obsolete and the "
                     "four rungs should be rebuilt with Option<fn>")
        elif FNPTR_EXPECT not in fnptr.get("text", ""):
            p.append(f"3. controls/fnptr.rs is refused, but NOT for the reason "
                     f"this row cites: the output does not contain "
                     f"{FNPTR_EXPECT!r}. The probe has rotted into testing "
                     f"something else")
    return p


def selftest():
    ok = {"errors": 3, "rc": 1}
    bad = []
    good_res = {k: dict(ok) for k in MUTANTS}
    good_fn = {"rc": 1, "errors": None,
               "text": "error: The verifier does not yet support the following "
                       "Rust feature: function pointer types"}
    cases = [
        ("P1 the shipped shape", good_res, good_fn, False, None),
        ("N1 a mutant verifies",
         {**good_res, "nofixup": {"errors": 0, "rc": 0}}, good_fn, True, "1."),
        ("N2 a second mutant verifies",
         {**good_res, "nostride": {"errors": 0, "rc": 0}}, good_fn, True, "1."),
        ("N3 a mutant could not be evaluated",
         {**good_res, "notail": {"errors": None, "rc": 2}}, good_fn, True, "2."),
        ("N4 fnptr is refused for the wrong reason",
         good_res, {"rc": 1, "errors": 1, "text": "error: postcondition not satisfied"},
         True, "3."),
        ("N5 fnptr VERIFIES",
         good_res, {"rc": 0, "errors": 0, "text": "verified"}, True, "4."),
        ("N6 fnptr exits 0 with no errors line",
         good_res, {"rc": 0, "errors": None, "text": "nothing"}, True, "4."),
        ("P2 mutants failing with different error counts",
         {k: {"errors": i + 1, "rc": 1} for i, k in enumerate(MUTANTS)},
         good_fn, False, None),
        ("P3 fnptr skipped entirely (no --verus)", good_res, None, False, None),
    ]
    for label, res, fn, must_fire, arm in cases:
        got = negative_problems(res, fn)
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
    ap.add_argument("--verus", action="store_true", default=True,
                    help="run controls/fnptr.rs too (default on)")
    ap.add_argument("--no-verus", dest="verus", action="store_false")
    args = ap.parse_args()

    if args.emit:
        print(materialise(args.emit))
        return 0

    problems = list(selftest())
    print("0. §H -- THE VERDICT ARM, ATTACKED OVER SYNTHETIC OUTCOMES")
    print(f"   selftest {'PASS' if not problems else 'FAIL'}   "
          f"9 arms (6 must-FIRE, 3 must-NOT-fire)")
    for p in problems:
        print(f"     *** {p}")
    if args.selftest:
        return 1 if problems else 0

    print("\n1. THE MUTANTS -- each removes something this row claims is "
          "necessary, and each MUST FAIL")
    results = {}
    for name in sorted(MUTANTS):
        try:
            path = materialise(name)
        except AssertionError as e:
            problems.append(str(e))
            results[name] = {"skipped": True, "error": str(e)}
            print(f"   {name:12s} MUTANT REFUSED -- {e}")
            continue
        r = run_verus(path)
        results[name] = r
        verdict = ("FAILS as required" if r["errors"] else
                   "⛔ VERIFIES -- see problems")
        print(f"   {name:12s} {str(r['verified']):>4s} verified / "
              f"{str(r['errors']):>3s} errors   {verdict}")

    fn = None
    if args.verus:
        print("\n2. ⭐ controls/fnptr.rs -- Verus must still REFUSE the TYPE")
        fn = run_verus(os.path.join(HERE, "fnptr.rs"))
        line = next((l for l in fn["text"].splitlines() if l.startswith("error:")),
                    "(no error line)")
        print(f"   rc={fn['rc']}   {line}")

    problems.extend(negative_problems(results, fn))
    out = {"mutants": results, "fnptr": fn, "problems": problems}
    dst = os.path.join(HERE, "negatives.json")
    out.update(_pin.pin(
        ['verus.rs', 'controls/fnptr.rs', 'controls/negatives.py'],
        'python3 patterns-php/ph55-opdata-stride/controls/negatives.py',
        'verus.rs (every mutant is a substitution ON it, and the hit counts are asserted), controls/fnptr.rs (the must-fire type-level negative) and this script. NOT inputs/: no mutant is RUN, only verified.'))
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
