#!/usr/bin/env python3
"""p25 CONTROLS: **is the R5 proof load-bearing, or is it decoration?**

    python3 patterns/p25-realloc-growth/controls/proof_mutants.py

⚠⚠ **p25's R5 obligation is the SMALLEST in the temporal family, so this battery
matters more here than on p27, p29, p32 or p34, not less.** `../spec.md` says
plainly that the temporal obligation has NO analogue at R5 -- no rung above R1
can hold the stale interior pointer -- and that what survives is the spatial
residue `have ==> curi < toks@.len()`. **A small obligation is exactly the kind
that can be vacuous**, so it gets a four-cell battery in p32's shape, extended
by p35's `X1` and p34's spec-weaken arm.

  ATTACK       delete `have ==> curi < toks@.len()` from the loop invariant.
               `vec_get_unchecked`'s precondition is then unprovable.
               MUST FAIL.
  X1           leave the invariant alone and strike the ONE statement that
               re-establishes it -- `curi = (a as usize) % toks.len();` becomes
               `curi = a as usize;`. MUST FAIL, and it must fail on the
               INVARIANT rather than on the postcondition, which is what says
               the conjunct is doing work rather than being implied.
  VACUITY      a constant kernel body (`return 0;` first). MUST FAIL -- so the
               `ensures` is not discharged by anything a trivial program does.
  SPEC-WEAKEN  replace the kernel's `ensures` with `r == r` and leave `main`
               alone. MUST FAIL **at the call site**, because `main`'s
               `assert(r == parse_fold(...))` is what CONSUMES the postcondition.
               ⚠ Without that assert the postcondition would be decoration and
               deleting it entirely would still verify (`.memory/04-verus.md`);
               this arm is what proves the assert is load-bearing.

⚠ **EVERY SUBSTITUTION ASSERTS ITS COUNT** (`CLAUDE.md` rule 1): `p28d` shipped
an uninitialised pointer because a `str.replace()` silently matched nothing, and
a mutant that was never applied *passes* the battery while proving nothing.

⚠ The BASELINE is run first and must VERIFY. A battery in which every arm fails
because the file no longer compiles certifies nothing at all
(`harness/check.py::check_clause_deletion` learned this the same way).
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
TMP = os.path.join(REPO, ".temp", "p25ctl")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
SRC = os.path.join(PDIR, "verus.rs")

# (name, from, to, expected-to-fail, what it says)
MUTANTS = [
    ("ATTACK",
     "            have ==> curi < toks@.len(),\n", "",
     "deletes SAFETY (5) from the loop invariant, so vec_get_unchecked's "
     "`requires i < v@.len()` is unprovable at the READ"),
    ("X1",
     "                curi = (a as usize) % toks.len();",
     "                curi = a as usize;",
     "leaves the invariant and strikes the ONE statement that re-establishes "
     "it, so the invariant fails at the SAVE rather than at the READ"),
    ("VACUITY",
     "{\n    // Ghost only: mentioning `spec_slice_len` fires vstd's",
     "{\n    return 0;\n    // Ghost only: mentioning `spec_slice_len` fires vstd's",
     "a constant kernel body, so the `ensures` is not discharged by anything a "
     "trivial program does"),
    ("SPEC-WEAKEN",
     "        r == parse_fold(buf@, off as int, len as int),",
     "        r == r,",
     "weakens the kernel's postcondition to a tautology and leaves main alone, "
     "so main's `assert(r == parse_fold(..))` -- the statement that CONSUMES "
     "the postcondition -- can no longer be discharged"),
]

_RES = re.compile(r"(\d+) verified,\s*(\d+) error")


def verus(path):
    r = subprocess.run([sys.executable, VERUS_RUN, path],
                       capture_output=True, text=True, timeout=3600, cwd=REPO)
    out = r.stdout + r.stderr
    m = _RES.search(out)
    verified, errors = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    # The FIRST diagnostic line, which is what says WHERE it failed.
    where = None
    for ln in out.splitlines():
        s = ln.strip()
        if s.startswith("error:"):
            where = " ".join(s.split())[:200]
            break
    return {"exit": r.returncode, "verified": verified, "errors": errors,
            "first_error": where, "tail": " ".join(out.split())[-500:]}


def derived_from():
    out = {}
    for rel in ("patterns/p25-realloc-growth/verus.rs",
                "patterns/p25-realloc-growth/controls/proof_mutants.py",
                "verus_run.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(TMP, exist_ok=True)
    base_src = open(SRC).read()
    problems, rows = [], []

    print("  BASELINE  verus.rs, unmutated")
    base = verus(SRC)
    print(f"     verified={base['verified']} errors={base['errors']} "
          f"exit={base['exit']}")
    if base["errors"] != 0 or base["exit"] != 0:
        problems.append(
            f"the UNMUTATED verus.rs does not verify (verified="
            f"{base['verified']}, errors={base['errors']}). Every arm below "
            f"would then 'fail' for a reason having nothing to do with the "
            f"mutation, and this battery would certify nothing. "
            f"{base['tail'][-200:]}")

    for name, old, new, what in MUTANTS:
        n = base_src.count(old)
        if n != 1:
            problems.append(
                f"{name}: its substitution matched {n} time(s) in verus.rs, "
                f"not 1. REFUSING to run it -- a mutant that was never applied "
                f"PASSES this battery while proving nothing, which is exactly "
                f"how p28d shipped an uninitialised pointer. Anchor: {old!r}")
            rows.append({"mutant": name, "applied": False, "substitutions": n,
                         "what": what})
            continue
        path = os.path.join(TMP, f"mut_{name.lower().replace('-', '_')}.rs")
        open(path, "w").write(base_src.replace(old, new))
        res = verus(path)
        failed = (res["errors"] or 0) > 0 or res["exit"] != 0
        rows.append({"mutant": name, "applied": True, "substitutions": n,
                     "what": what, "failed_as_required": failed, **res})
        print(f"  {name:12s} verified={res['verified']!s:5s} "
              f"errors={res['errors']!s:4s} exit={res['exit']!s:4s} "
              f"{'FAILS (as required)' if failed else 'VERIFIED (!!)'}")
        if res["first_error"]:
            print(f"               {res['first_error']}")
        if not failed:
            problems.append(
                f"{name}: the mutant VERIFIED. {what} -- and Verus did not "
                f"object, so that part of the proof is not load-bearing and "
                f"../spec.md must not claim it is")
        os.unlink(path)

    doc = {"pin": {"regenerate": "python3 patterns/p25-realloc-growth/controls/"
                                 "proof_mutants.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "baseline": base,
           "mutants": rows,
           "problems": problems,
           "invariant": "The unmutated verus.rs verifies, and all four mutants "
                        "FAIL: deleting SAFETY (5) from the loop invariant, "
                        "striking the statement that re-establishes it, a "
                        "constant kernel body, and weakening the kernel's "
                        "postcondition to a tautology. Every substitution "
                        "count is asserted to be exactly 1 before the mutant is "
                        "run."}
    out = os.path.join(HERE, "proof_mutants.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
