#!/usr/bin/env python3
"""ph97 — MUST-FIRE and MUST-NOT-FIRE mutants of `verus.rs`.

    python3 patterns-php/ph97-optarg-unwritten/controls/negatives.py
    python3 .../negatives.py --emit r1        # print one mutant and stop

=============================================================================
WHY THIS CONTROL EXISTS, AND WHAT IT IS THE ONLY EVIDENCE FOR
=============================================================================
`verus.rs` verifies. **That says nothing about what it would REFUSE.** A green
verifier on a file that would also be green with its one load-bearing
precondition deleted has certified nothing — `.memory/04-verus.md`, and
`PROTOCOL_PHP.md` §H: *a gate run EXERCISES a validator on the rows that pass;
it does not ATTACK it.*

⭐⭐⭐ **THE ONE THAT MATTERS IS `r1`.** It deletes `typ.is_none() ||` — the
whole of `f7326d627962`, the 2005 upstream fix — from `get_info`, and the
mutant **must FAIL to verify**, on `opt_get`'s `requires t.is_some()`, at the
FIRST compare site. That is the row's claim reduced to an experiment: *the
obligation the C needs is exactly the one the patch discharges, and nothing
else in the file discharges it.*

⛔ **AND `parse_ok` IS THE CONTROL THAT MAKES `r1` MEAN SOMETHING.** It
STRENGTHENS the parser's postcondition — `r ==> *final(wrote) == (num_args == 1)`
becomes `r ==> *final(wrote)` — i.e. it asserts the thing a reader might expect,
that a successful parse wrote its out-parameter. **That mutant must ALSO fail**,
and it must fail in `parse_va_args` rather than in `get_info`: the parser cannot
promise it, because with zero arguments it really does return SUCCESS having
written nothing. ▶ Together the two say: **the obligation is not discharged
from the parser's postcondition and could not be**, which is the sentence
`NOTES.md` §10 and `spec.md`'s `obligations_note` both make.

⚠ **THE MUTANT DIRECTORIES ARE FIXED-WIDTH (`mNN`) AND ASSERTED EQUAL IN
LENGTH.** `RECAP_PHP.md` F101 / item 109: paths are load-bearing on this
project and have fired live in both directions. Nothing here compares machine
code, but the rule is cheap to keep and expensive to remember.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

SCRATCH = os.path.join(REPO, ".temp", "php97", "neg")
VERUS_RUN = os.path.join(REPO, "verus_run.py")


#: name -> (must_verify, old, new, why[, n_occurrences])
#: ⚠ `n_occurrences` is DECLARED and asserted. A mutant whose anchor matched a
#: different number of times than its author thought would be testing something
#: else, and `spec_order` really does have TWO occurrences -- the `requires` and
#: the loop invariant that restates it -- so reversing only one would be an
#: inconsistency rather than a reversal.
MUTANTS = {
    "r1": (
        False,
        "if typ.is_none() || strcasecmp(sel_get(0), opt_get(typ)) == 0 {",
        "if strcasecmp(sel_get(0), opt_get(typ)) == 0 {",
        "⭐⭐⭐ DELETE f7326d627962 -- the 2005 fix, the whole of it. The file "
        "must STOP VERIFYING, on `opt_get`'s `requires t.is_some()`, at the "
        "first compare site. This is the row's claim as an experiment."),
    "invert": (
        False,
        "if typ.is_none() || strcasecmp(sel_get(0), opt_get(typ)) == 0 {",
        "if typ.is_some() || strcasecmp(sel_get(0), opt_get(typ)) == 0 {",
        "⛔ INVERT the guard. A disjunct is still there and it still "
        "short-circuits, so a proof that merely wanted `something || ...` "
        "would stay green. It must not: the guard has to be the one that "
        "rules `None` OUT."),
    "parse_ok": (
        False,
        "r ==> *final(wrote) == (num_args == 1),",
        "r ==> *final(wrote),",
        "⛔⛔ STRENGTHEN the parser's postcondition to *SUCCESS means the "
        "out-parameter was written* -- what a reader expects and what "
        "zend_parse_parameters does not promise. It must FAIL, and it must "
        "fail in `parse_va_args`: with zero arguments the parser really does "
        "return SUCCESS having written nothing. That is the defect, stated as "
        "a contract the code cannot meet."),
    "spec_order": (
        False,
        "type_spec@ == seq![124u8, 115u8],",
        "type_spec@ == seq![115u8, 124u8],",
        "⛔ REVERSE the type spec -- \"s|\" instead of \"|s\". The scanner's "
        "loop invariant names the minimum and maximum after each character, "
        "and with the marker LAST the minimum is ONE, not zero. The file must "
        "stop verifying, which is the ORDER-DEPENDENCE of the defect as an "
        "experiment.", 2),
    "comment": (
        True,
        "// ---------------------------------------------------------------- kernel ----",
        "// ------------------------------------------------- the kernel follows ------",
        "✅ MUST-NOT-FIRE. A comment-only edit must leave the file verifying. "
        "Without this arm a harness that failed on everything would look like "
        "four successful attacks."),
}


def _mutate(name, mdir):
    entry = MUTANTS[name]
    must, old, new, why = entry[:4]
    want = entry[4] if len(entry) > 4 else 1
    src = open(os.path.join(PDIR, "verus.rs")).read()
    if src.count(old) != want:
        raise SystemExit(f"negatives.py: mutant {name!r} anchors {src.count(old)} "
                         f"times in verus.rs, want exactly {want} -- the mutant "
                         f"has drifted from the file and would be testing "
                         f"something else")
    return src.replace(old, new), must, why


def _run(path, cfg=None):
    cmd = [sys.executable, VERUS_RUN, path] + (["--cfg", cfg] if cfg else [])
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    txt = r.stdout + r.stderr
    m = re.search(r"(\d+) verified, (\d+) errors", txt)
    first = ""
    for line in txt.splitlines():
        if line.startswith("error:") or "not satisfied" in line:
            first = line.strip()
            break
    return {"verified": int(m.group(1)) if m else None,
            "errors": int(m.group(2)) if m else None,
            "rc": r.returncode, "first_error": first[:180]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", metavar="NAME",
                    help="write the named mutant and print its path")
    a = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    # `verus.rs` carries `#[path = "../../common/driver.rs"]`, which from
    # `<SCRATCH>/mNN/verus.rs` resolves to `<SCRATCH>/../common/driver.rs`.
    cdir = os.path.join(os.path.dirname(SCRATCH), "common")
    os.makedirs(cdir, exist_ok=True)
    shutil.copy(os.path.join(REPO, "common", "driver.rs"),
                os.path.join(cdir, "driver.rs"))

    if a.emit:
        txt, must, why = _mutate(a.emit, None)
        d = os.path.join(SCRATCH, "m99")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "verus.rs")
        open(p, "w").write(txt)
        print(p)
        print(why)
        return 0

    rec = {"mutants": {}, "problems": []}
    dirs = []
    for i, name in enumerate(sorted(MUTANTS)):
        d = os.path.join(SCRATCH, f"m{i:02d}")
        os.makedirs(d, exist_ok=True)
        dirs.append(d)
    assert len({len(d) for d in dirs}) == 1, (
        "mutant directories must have EQUAL PATH LENGTHS (F101)")

    for i, name in enumerate(sorted(MUTANTS)):
        txt, must, why = _mutate(name, None)
        p = os.path.join(SCRATCH, f"m{i:02d}", "verus.rs")
        open(p, "w").write(txt)
        res = _run(p)
        verified = res["errors"] == 0 and res["rc"] == 0
        ok = (verified == must)
        rec["mutants"][name] = dict(res, must_verify=must, ok=ok, why=why)
        tag = "MUST-NOT-FIRE" if must else "MUST-FIRE   "
        print(f"  {tag} {name:11s} -> {res['verified']} verified, "
              f"{res['errors']} errors   {'ok' if ok else 'BAD'}")
        if res["first_error"]:
            print(f"                          {res['first_error']}")
        if not ok:
            rec["problems"].append(
                f"{name}: verified={verified}, wanted verify={must} -- {why}")

    rec.update(_pin.pin(["verus.rs"], "python3 controls/negatives.py",
                        "one verus run per mutant; minutes"))
    with open(os.path.join(HERE, "negatives.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/negatives.json -- {len(rec['problems'])} problem(s)")
    for p in rec["problems"]:
        print("  ⛔ " + p)
    return 1 if rec["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
