#!/usr/bin/env python3
"""p42 control 6 -- THE GHOST LEDGER, AND THE TWO ARMS THAT MUST FIRE.

`controls/affine_leak.rs` is the negative half of p42's Verus result: a bare
`Tracked<Dealloc>` is AFFINE, so a proof may drop it and a leaking R5 verifies
clean.  **This file is the positive half, and it is the one that decides whether
the shipped R5 covers p42's own bug class.**  Landed at TASK_110, from
TASK_109 §A.

The encoding, in one sentence: `verus.rs` never holds a bare
`Tracked<Dealloc>` -- `led_alloc` escrows it into a tracked `Map<int, Dealloc>`
under a ghost key, `led_free` withdraws it and spends it, and `kbody`'s
postcondition says the map's domain comes back EMPTY.  Verus checks a
postcondition on EVERY exit, so the early `return 0` on the error path -- which
is exactly the C rung's bug -- is checked too.

⚠ **THE ARMS ARE THE POINT.**  A proof obligation nobody has seen fail is
indistinguishable from a decoration (`.memory/03-measurement.md`'s list of
controls that could not have fired).  So this script deletes each of the two
`led_free` calls in turn, from the SHIPPED `verus.rs`, by substitution here --
nothing is a hand-written fork -- and requires Verus to reject each one and to
NAME THE EXIT it rejects:

    base       the shipped file                       MUST give 18 verified, 0 errors
    leak_err   the ERROR path's release deleted       MUST give 17 verified, 1 errors
    leak_ok    the SUCCESS path's release deleted     MUST give 17 verified, 1 errors

⚠ **Keying the ledger by ADDRESS does not work, and that is the one non-obvious
step.**  `dig_alloc` promises nothing about the returned address being absent
from the ledger, so `dom.insert(a).remove(a) =~= dom` is unprovable and the
postcondition fails on BOTH exits -- i.e. the arms fire for the wrong reason and
the base does not verify at all.  A ghost key with
`!old(led).dom().contains(k)` is discharged by the caller for free.  Measured
both ways at TASK_109 A2.

⚠ **What the ledger does NOT buy:** the obligation binds allocations that go
through `led_alloc`.  A direct call to `dig_alloc`, or to
`vstd::raw_ptr::allocate`, still drops its token silently.  That is a
module-level discipline, not a global guarantee, and ../NOTES.md 6 says so.

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
# anchor cannot match the other one.  `sub` asserts presence: an anchor that has
# drifted must be fixed here rather than silently measuring a stale variant.
ERR_ARM = ("""        led_free(p, len, 1, Tracked(raw), Ghost(0int), Tracked(&mut *led));
        return 0;""",
           """        return 0;""")
OK_ARM = ("""    led_free(p, len, 1, Tracked(rest), Ghost(0int), Tracked(&mut *led));
    acc
}""",
          """    acc
}""")

# `verus_run.py` compiles ONE file; a copy under .temp/ cannot resolve the
# relative `#[path]` to the shared driver, so it is made absolute.  That is the
# only difference between what this script runs and what ships.
PATH_ATTR = '#[path = "../../common/driver.rs"]'


def variant(src, arm, tag):
    old, new = arm
    assert src.count(old) == 1, (
        f"{tag}: verus.rs no longer contains exactly one copy of this "
        f"release -- fix the anchor, not the assert")
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

    arms = [("base", src, (18, 0)),
            ("leak_err", variant(src, ERR_ARM, "leak_err"), (17, 1)),
            ("leak_ok", variant(src, OK_ARM, "leak_ok"), (17, 1))]
    fail = 0
    for name, text, want in arms:
        p = os.path.join(OUT, f"{name}.rs")
        open(p, "w").write(text)
        got, exits, out = run(p)
        st = "OK" if got == want else f"*** WRONG (want {want[0]}/{want[1]}) ***"
        if got != want:
            fail = 1
            open(os.path.join(OUT, f"{name}.log"), "w").write(out)
        where = "; ".join(f"{a.strip()} [{b}]" for a, b in exits) or "-"
        print(f"  {name:9s} {str(got[0]):>3s} verified, {str(got[1]):>2s} errors  "
              f"{st}")
        if name != "base":
            print(f"            Verus names the exit: {where}")
            if not exits:
                fail = 1
                print("            *** NO EXIT NAMED -- the arm fired for some "
                      "other reason, which is not the claim ***")
    print()
    if fail:
        print("*** SOMETHING IS WRONG -- read the rows above and the .log files ***")
    else:
        print("BOTH ARMS FIRE, each naming its own exit: the shipped R5 states "
              "leak-freedom\nand a deleted release is caught, on the error path "
              "and on the success path alike.")
    return fail


if __name__ == "__main__":
    sys.exit(main())
