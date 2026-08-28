#!/usr/bin/env python3
"""p42 control 6 -- THE GHOST LEDGER: WHAT IT CATCHES, AND WHAT IT DOES NOT.

⚠⚠ **THIS FILE'S HEADLINE IS RETRACTED AND REPLACED, AT TASK_118.**  From
TASK_110 to TASK_118 it opened *"THE GHOST LEDGER, AND THE TWO ARMS THAT MUST
FIRE"* and closed by printing *"the shipped R5 states leak-freedom"*.  **It does
not.**  TASK_116 substituted one proof line for the error path's release and got
`18 verified, 0 errors` out of a program that leaks exactly
`model.py::leak_bytes`; TASK_118 reproduced it and killed a third encoding too.

**So this script now runs FIVE arms in two groups, and both groups are the
point:**

    base            the shipped file                      MUST give 18 verified, 0 errors

  -- deletions.  These FAIL, and Verus names the exit.  This is the half the
     ledger really does buy: you cannot simply delete a release.
    leak_err        the ERROR path's release deleted      MUST give 17 verified, 1 errors
    leak_ok         the SUCCESS path's release deleted    MUST give 17 verified, 1 errors

  -- ⚠⚠ ATTACKS.  These VERIFY, and they leak.  They are pinned here as
     ACCEPTANCE arms so the hole cannot rot back into a claim: if a future
     encoding rejects one of them, this script FAILS and says so, and whoever
     changed it has to come and update the retraction rather than inherit it.
    atk_remove_err  withdraw the escrowed token and drop it   MUST give 18 verified, 0 errors
    atk_assign_err  assign a fresh empty map over the ledger  MUST give 18 verified, 0 errors

`Map::tracked_remove` is not an escape hatch invented for this probe -- it is
the call `led_free` itself makes, and the one `kbody`'s fold makes on `perms`.
`atk_assign_err` is worse: it discards the whole map without mentioning the key,
which is what the `spec.md` `idiom.why` sentence *"a proof cannot drop the MAP
that holds it if a postcondition names that map"* asserted was impossible.

**What the ledger's postcondition therefore certifies** is that the proof author
wrote SOMETHING on every exit that empties a map the proof author controls.
That is strictly weaker than leak-freedom, by exactly one proof line.

⚠ **Keying the ledger by ADDRESS does not work, and that is the one non-obvious
step.**  `dig_alloc` promises nothing about the returned address being absent
from the ledger, so `dom.insert(a).remove(a) =~= dom` is unprovable and the
postcondition fails on BOTH exits -- i.e. the arms fire for the wrong reason and
the base does not verify at all.  A ghost key with
`!old(led).dom().contains(k)` is discharged by the caller for free.  Measured
both ways at TASK_109 A2.

⚠ **What the ledger does NOT buy, and it is WIDER than this file used to say:**
the obligation binds only what is escrowed in the ledger the caller handed in.
A direct call to `dig_alloc`, or to `vstd::raw_ptr::allocate`, still drops its
token silently; a proof may empty the ledger without freeing (the two attack
arms); and a body may escrow into a ledger it mints for itself -- which is what
kills the privacy-scoped encoding TASK_118 built.  Module-level discipline, not
a global guarantee.  ../NOTES.md 6.

⚠ **THE ANCHOR ASSERTS ARE PART OF THE CONTROL AND USED TO BE HALF A
TRIPWIRE** (TASK_116 §A.2, MINOR 7).  Each substitution used to assert only its
OWN anchor, so a tree whose ERROR-path release had been tampered with tripped
`leak_err`'s assert and sailed past `leak_ok`'s.  `check_anchors` below now
asserts BOTH releases are present, exactly once each, BEFORE any arm runs.

  python3 patterns/p42-goto-cleanup/controls/ledger_leak.py

Sources land in .temp/t110/ledgerctl/ and are re-derivable from this file.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "t110", "ledgerctl")
VERUS_RUN = os.path.join(REPO, "verus_run.py")

# The two releases, each anchored on the statement that follows it so that the
# anchor cannot match the other one.
ERR_REL = """        led_free(p, len, 1, Tracked(raw), Ghost(0int), Tracked(&mut *led));
        return 0;"""
OK_REL = """    led_free(p, len, 1, Tracked(rest), Ghost(0int), Tracked(&mut *led));
    acc
}"""

ERR_ARM = (ERR_REL, """        return 0;""")
OK_ARM = (OK_REL, """    acc
}""")

# ⚠ The two attacks.  Same anchor as `leak_err`, so they replace the SAME
# release the C rung is missing -- which is what makes them p42's own bug class
# rather than a contrived leak.
ATK_REMOVE = (ERR_REL, """        proof { let tracked _dl = led.tracked_remove(0int); }
        return 0;""")
ATK_ASSIGN = (ERR_REL, """        proof { *led = Map::<int, Dealloc>::tracked_empty(); }
        return 0;""")

# `verus_run.py` compiles ONE file; a copy under .temp/ cannot resolve the
# relative `#[path]` to the shared driver, so it is made absolute.  That is the
# only difference between what this script runs and what ships.
PATH_ATTR = '#[path = "../../common/driver.rs"]'


def check_anchors(src):
    """⚠ BOTH releases, before ANY arm runs. See the module docstring."""
    for tag, (old, _) in (("error path", ERR_ARM), ("success path", OK_ARM)):
        n = src.count(old)
        assert n == 1, (
            f"anchor check: verus.rs contains {n} copies of the {tag} release, "
            f"not exactly 1 -- fix the anchor here, not the assert. Every arm "
            f"below is measuring something other than the shipped tree until "
            f"you do.")


def variant(src, arm, tag):
    old, new = arm
    assert src.count(old) == 1, f"{tag}: anchor not unique"
    return src.replace(old, new)


def run(path):
    r = subprocess.run([sys.executable, VERUS_RUN, path],
                       capture_output=True, text=True, timeout=1800)
    out = r.stdout + r.stderr
    m = re.search(r"(\d+) verified, (\d+) errors", out)
    exits = re.findall(r"^\s*\d+ \|(.*)$\n\s+\|\s+-+ (at this exit|at the end "
                       r"of the function body)", out, re.M)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None), exits, out


def main():
    os.makedirs(OUT, exist_ok=True)
    src = open(os.path.join(PDIR, "verus.rs")).read()
    assert PATH_ATTR in src, "verus.rs's #[path] attribute has moved"
    src = src.replace(PATH_ATTR, f'#[path = "{os.path.join(REPO, "common", "driver.rs")}"]')
    check_anchors(src)

    arms = [("base", src, (18, 0), "must verify", False),
            ("leak_err", variant(src, ERR_ARM, "leak_err"), (17, 1),
             "DELETION -- must fail, naming the exit", True),
            ("leak_ok", variant(src, OK_ARM, "leak_ok"), (17, 1),
             "DELETION -- must fail, naming the exit", True),
            ("atk_remove_err", variant(src, ATK_REMOVE, "atk_remove_err"), (18, 0),
             "ATTACK -- must VERIFY (the hole, pinned)", False),
            ("atk_assign_err", variant(src, ATK_ASSIGN, "atk_assign_err"), (18, 0),
             "ATTACK -- must VERIFY (the hole, pinned)", False)]
    fail = 0
    for name, text, want, note, want_exit_named in arms:
        p = os.path.join(OUT, f"{name}.rs")
        open(p, "w").write(text)
        got, exits, out = run(p)
        st = "OK" if got == want else f"*** WRONG (want {want[0]}/{want[1]}) ***"
        if got != want:
            fail = 1
            open(os.path.join(OUT, f"{name}.log"), "w").write(out)
        where = "; ".join(f"{a.strip()} [{b}]" for a, b in exits) or "-"
        print(f"  {name:15s} {str(got[0]):>3s} verified, {str(got[1]):>2s} errors  "
              f"{st:12s} {note}")
        if want_exit_named:
            print(f"                  Verus names the exit: {where}")
            if not exits:
                fail = 1
                print("                  *** NO EXIT NAMED -- the arm fired for "
                      "some other reason, which is not the claim ***")
    print()
    if fail:
        print("*** SOMETHING IS WRONG -- read the rows above and the .log files ***")
        print("⚠ If an ATTACK arm stopped verifying, the encoding has CHANGED and")
        print("  ../NOTES.md 6, ../spec.md's idiom.why and this file's docstring")
        print("  all need re-deriving. That is a good problem; do not just edit")
        print("  the expected numbers.")
    else:
        print("BOTH DELETION ARMS FIRE, each naming its own exit: a release that is")
        print("simply DELETED is caught, on the error path and on the success path.")
        print("⚠⚠ AND BOTH ATTACK ARMS VERIFY: a release that is REPLACED by a proof")
        print("line that empties the ledger is NOT caught. The postcondition says the")
        print("ledger is empty, not that the block was freed. ../NOTES.md 6.")
    return fail


if __name__ == "__main__":
    sys.exit(main())
