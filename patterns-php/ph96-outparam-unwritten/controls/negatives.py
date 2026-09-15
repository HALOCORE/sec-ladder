#!/usr/bin/env python3
"""ph96 -- the Verus MUTANTS: is the proof about the row, or about arithmetic?

    python3 patterns-php/ph96-outparam-unwritten/controls/negatives.py
    python3 .../negatives.py --emit r1 > /dev/null    # print one mutant

⭐⭐⭐ **THE OBLIGATION THE ROW IS ABOUT IS ONE CONJUNCT** -- `opt_get`'s
`requires t.is_some()`, which is `I12/O1` word for word -- **and this file is
what shows it is load-bearing rather than decorative.** Four mutants:

  `r1`         delete the `:385` NULL test at the READ shape (upstream's own)
  `r1exists`   delete the same test at the EXISTS shape (the one upstream does
               NOT have, which is the second limb as a proof obligation)
  `status_ok`  STRENGTHEN `call_method`'s postcondition to what a caller of
               `zend_object_handlers.c:513` evidently assumed -- *SUCCESS means
               the out-parameter was written*
  `shipped`    the file as it is -- MUST-NOT-FIRE

⛔⛔ **`status_ok` IS THE ROW, RESTATED AS A PROOF OBLIGATION.** It must fail
**inside `call_method`** and not at a call site: the callee really does return
SUCCESS having written nothing, so no strengthening of the status could ever
discharge the consumer's precondition. *The status answers a different question*
and *the status's postcondition cannot discharge the release's precondition* are
the same sentence in two languages.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

SCRATCH = os.path.join(REPO, ".temp", "php96", "neg")
VERUS = os.path.join(REPO, "verus_run.py")

READ_GUARD = """    let retval: Option<&mut Zval> = if wrote_out { Some(slot) } else { None };
    if retval.is_none() {
        // :385-389. With EG(exception) set -- which is the state that put the
        // sentinel here -- the E_ERROR at :387 is NOT raised.
        return acc.wrapping_mul(31).wrapping_add(TAG_UNDEF);
    }
"""
EXISTS_GUARD = """    let retval: Option<&mut Zval> = if wrote_out { Some(slot) } else { None };
    if retval.is_none() {
        return acc.wrapping_mul(31).wrapping_add(TAG_UNDEF);
    }
"""
STATUS_WEAK = "        *final(wrote_out) == (!s_core(b@) && want_output && s_wrote(b@)),"
STATUS_STRONG = "        *final(wrote_out) == (!s_core(b@) && want_output),"


def mutate(kind):
    s = open(os.path.join(PDIR, "verus.rs")).read()
    if kind == "shipped":
        return s
    if kind == "r1":
        assert s.count(READ_GUARD) == 1, "the read shape's guard has moved"
        return s.replace(READ_GUARD,
                         "    let retval: Option<&mut Zval> = "
                         "if wrote_out { Some(slot) } else { None };\n", 1)
    if kind == "r1exists":
        assert s.count(EXISTS_GUARD) == 1, "the exists shape's guard has moved"
        return s.replace(EXISTS_GUARD,
                         "    let retval: Option<&mut Zval> = "
                         "if wrote_out { Some(slot) } else { None };\n", 1)
    if kind == "status_ok":
        assert s.count(STATUS_WEAK) == 1, "call_method's ensures has moved"
        return s.replace(STATUS_WEAK, STATUS_STRONG, 1)
    raise SystemExit(f"unknown mutant {kind}")


def verify(src, tag):
    os.makedirs(SCRATCH, exist_ok=True)
    p = os.path.join(SCRATCH, f"{tag}.rs")
    open(p, "w").write(src)
    r = subprocess.run([sys.executable, VERUS, p], capture_output=True,
                       text=True, cwd=REPO, timeout=3600)
    out = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"(\d+) verified, (\d+) errors", out)
    errs = [l.strip() for l in out.splitlines()
            if l.strip().startswith("error:")][:4]
    return {"verified": int(m.group(1)) if m else None,
            "errors": int(m.group(2)) if m else None,
            "exit": r.returncode, "error_lines": errs}


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--emit":
        sys.stdout.write(mutate(sys.argv[2]))
        return 0
    problems = []
    rec = {"problems": problems, "mutants": {}}
    plan = [("shipped", False, "the file as it is"),
            ("r1", True, "delete the :385 NULL test at the READ shape"),
            ("r1exists", True, "delete the same test at the EXISTS shape"),
            ("status_ok", True,
             "strengthen call_method's postcondition to *SUCCESS means the "
             "out-parameter was written*")]
    print(f"{'mutant':12s}{'must':10s}{'verified':>10s}{'errors':>8s}  first error")
    for kind, must_fail, what in plan:
        v = verify(mutate(kind), kind)
        v["what"] = what
        v["must_fail"] = must_fail
        rec["mutants"][kind] = v
        first = (v["error_lines"] or [""])[0][:74]
        print(f"{kind:12s}{'FAIL' if must_fail else 'verify':10s}"
              f"{str(v['verified']):>10s}{str(v['errors']):>8s}  {first}")
        failed = bool(v["errors"])
        if must_fail and not failed:
            problems.append(f"MUST-FIRE `{kind}` ({what}) VERIFIES. The "
                            f"obligation it removes is not load-bearing, so the "
                            f"proof is not about what the row says it is about.")
        if (not must_fail) and failed:
            problems.append(f"MUST-NOT-FIRE `{kind}` does not verify; the "
                            f"instrument is broken, not the row")

    # ⭐ WHERE `status_ok` fails is the whole point.
    so = rec["mutants"]["status_ok"]
    inside = any("call_method" in e or "postcondition" in e
                 for e in so["error_lines"])
    rec["status_ok_fails_in_the_callee"] = inside
    print(f"\n⭐ `status_ok` fails with a POSTCONDITION error in the callee: "
          f"{inside}")
    print("   → the status's contract cannot be strengthened to say the "
          "output is there,")
    print("     because the callee really does return SUCCESS having written "
          "nothing.")
    if so["errors"] and not inside:
        problems.append("`status_ok` fails somewhere other than in the callee's "
                        "own postcondition; the row's claim is that the CALLEE "
                        "cannot promise it, not that a caller mis-uses it")

    rec.update(_pin.pin(["verus.rs"], "python3 controls/negatives.py",
                        "four Verus runs; a few minutes"))
    with open(os.path.join(HERE, "negatives.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/negatives.json -- {len(problems)} problem(s)")
    for p in problems:
        print("  ⛔ " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
