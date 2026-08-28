#!/usr/bin/env python3
"""p42 control 7 -- THE REGRESSION CHECK FOR `harness/check.py`'s MIRI `leak`
KEY (TASK_116 MINOR 6, fixed at TASK_118).

    python3 patterns/p42-goto-cleanup/controls/miri_leak_key.py
    python3 patterns/p42-goto-cleanup/controls/miri_leak_key.py --old-rev HEAD

**The defect.** `check.py`'s Miri stage recorded

    ub = "Undefined Behavior" in r.stderr or "error: unsupported" in r.stderr

and **a Miri LEAK is neither.**  So a leaking rung was recorded with
`ub: False` and caught only by the *next* branch, on the exit code, with the
message *"miri exited 1, model expects 0"*.  The gate's VERDICT was correct
throughout; what was wrong is the RECORD.  A reader auditing
`results/gate/*.json` by the `ub` key -- the key you would search for -- **saw
nothing**, on the one pattern in this tree whose entire subject is a leak and
whose Miri run is the only mechanical leak check either of its top two rungs
has (`../NOTES.md` 6, `../spec.md`'s `miri.reason`).

**The fix** records `leak` on every Miri row, unconditionally, and gives it its
own failure branch above the exit-code branch.

**What this script does**, in the shape `p18-varint-shift/controls/
miri_exit_hole.py` established:

  1. writes MUTANT-A: the shipped `../unsafe.rs` with the ERROR PATH's
     `dig_free` deleted -- **p42's own bug class**, the same substitution
     `controls/miri_seeds.sh` uses for its positive control, so the two cannot
     drift apart in what they mean;
  2. writes CONTROL-B: the shipped `../unsafe.rs`, unmodified;
  3. runs `harness/check.py`'s own `check_miri()` on both, over
     `adversarial-notag.bin` -- the input whose every call takes the error path
     -- and asserts, on MUTANT-A:

         leak is True   AND   ub is False

     ⚠ **Both halves.**  `leak is True` says the new key works; `ub is False`
     says the key was NEEDED, i.e. that this really is the blind spot and not a
     case the old code already covered.  On CONTROL-B both must be False and
     the row must pass, so the failure above is the leak and not the fixture;
  4. ⚠ **THE ARM THAT MUST FIRE ON THE OLD CODE.**  `git show
     <rev>:harness/check.py`, load it, run *its* `check_miri()` on the same
     mutant, and show that its record has **no `leak` key at all** while its
     `ub` reads `False`.  Without step 4 this script would only show that the
     new code works, which is not the claim.  Read-only git; skipped with a
     printed reason if the object is gone.

Nothing here touches the pattern's inputs, cells or gate record: everything is
written under `.temp/p42-leakkey/pid<PID>/`, and the pattern dir handed to
`check_miri` is that scratch dir.
"""

import argparse
import importlib.util
import os
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
SCRATCH = os.path.join(REPO, ".temp", "p42-leakkey", f"pid{os.getpid()}")

# The revision whose `check.py` had the blind spot. `HEAD` is right while
# TASK_118 is uncommitted; once it lands, pass the commit BEFORE it. Step 4
# skips itself, with a reason, if the loaded file already has the fix -- so a
# wrong `--old-rev` reports "skipped", never a false pass.
PRE_FIX_REV = "HEAD"

PROBE = "unsafe_probe.rs"
CONTRACT = {"miri": {"pair": ["unsafe", "verus"], "required": True,
                     "sources": [PROBE],
                     "reason": "TASK_118 regression fixture"}}
IDENTITY = [{"pair": "unsafe vs verus", "opt": "O3", "level": "exact"}]

# The error path and its release, verbatim from the shipped rung. Same anchor
# `controls/miri_seeds.sh` uses.
OLD = """        // The error path, and the hand-written release the C rung is missing.
        dig_free(p, len, 1);
        return 0;"""
NEW = """        // MUTANT: the release deleted -- this rung now has the C rung's bug.
        return 0;"""

STEM = "probe-notag.bin"


def load(path, name, repo):
    """Import a `check.py` by path, then repoint its `REPO` at the real tree."""
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.REPO = repo
    return m


def write_sources():
    src = open(os.path.join(PDIR, "unsafe.rs")).read()
    assert src.count(OLD) == 1, (
        "unsafe.rs no longer contains exactly one copy of the error path this "
        "control deletes -- fix the anchor here, not the assert")
    assert '#[path = "../../common/driver.rs"]' in src
    drv = open(os.path.join(REPO, "common", "driver.rs")).read()
    blob = open(os.path.join(PDIR, "inputs", "adversarial-notag.bin"), "rb").read()
    out = {}
    for tag, text in (("mutant", src.replace(OLD, NEW)), ("control", src)):
        d = os.path.join(SCRATCH, tag)
        os.makedirs(os.path.join(d, "inputs"), exist_ok=True)
        open(os.path.join(d, "driver_copy.rs"), "w").write(drv)
        open(os.path.join(d, PROBE), "w").write(
            text.replace('#[path = "../../common/driver.rs"]',
                         '#[path = "driver_copy.rs"]'))
        # `check_miri` clamps n_iters itself; the blob is copied verbatim so
        # the mutant and the control see exactly the pattern's own input.
        open(os.path.join(d, "inputs", STEM), "wb").write(blob)
        out[tag] = d
    return out


def run_stage(mod, pdir, modmod, label):
    rep = mod.Report()
    print(f"\n---- {label} ----")
    out = mod.check_miri(pdir, rep, CONTRACT, IDENTITY, modmod,
                         os.path.join(pdir, "inputs"), [STEM])
    runs = [r for r in (out.get("runs") or []) if "blocked" not in r]
    return rep, runs


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old-rev", default=PRE_FIX_REV)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()

    sys.path.insert(0, os.path.join(REPO, "common"))
    sys.path.insert(0, os.path.join(REPO, "harness"))
    check = load(os.path.join(REPO, "harness", "check.py"), "check_now", REPO)
    modmod = load(os.path.join(PDIR, "model.py"), "p42model", REPO)

    dirs = write_sources()
    m = modmod.build(os.path.join(dirs["mutant"], "inputs", STEM))
    print(f"blob: {STEM}  model.py: expected_exit={m.expected_exit} "
          f"leak_bytes={m.leak_bytes} n_err={getattr(m, 'n_err', '?')}")
    if not m.leak_bytes:
        raise SystemExit("the probe blob does not reach the error path, so the "
                         "mutant cannot leak; the fixture is broken")

    bad = 0
    rep_a, runs_a = run_stage(check, dirs["mutant"], modmod,
                              "MUTANT-A (error-path dig_free deleted)")
    rep_b, runs_b = run_stage(check, dirs["control"], modmod,
                              "CONTROL-B (shipped rung)")
    if not runs_a or not runs_b:
        raise SystemExit("miri produced no run (blocked or missing) -- this "
                         "check needs a working miri; see TOOLCHAIN.md")
    A, B = runs_a[0], runs_b[0]

    print("\n==== verdict ====")
    print(f"  MUTANT-A   exit={A['exit']}  ub={A['ub']}  leak={A.get('leak')}")
    print(f"  CONTROL-B  exit={B['exit']}  ub={B['ub']}  leak={B.get('leak')}")

    if A.get("leak") is True:
        print("  ok    the RECORD says leak=True on the leaking rung")
    else:
        print("  FAIL  the record does not say leak=True -- TASK_116 MINOR 6 "
              "is open again")
        bad += 1
    if A["ub"] is False:
        print("  ok    ub=False on the same row, so the `leak` key is NEEDED "
              "and not redundant with `ub`")
    else:
        print("  FAIL  ub is True here, so this fixture is not exercising the "
              "blind spot it claims to")
        bad += 1
    if rep_a.failures:
        print(f"  ok    the gate FAILS the mutant: {rep_a.failures[0][1][:150]}")
    else:
        print("  FAIL  the gate reported the leaking mutant GREEN")
        bad += 1
    if B.get("leak") is False and B["ub"] is False and not rep_b.failures:
        print("  ok    the shipped rung passes with leak=False, so the failure "
              "above is the deleted release and not the fixture")
    else:
        print(f"  FAIL  the CONTROL is not clean: leak={B.get('leak')} "
              f"ub={B['ub']} failures={[f[1][:100] for f in rep_b.failures]}")
        bad += 1

    # ---- the arm that must fire on the OLD code ---------------------------
    r = subprocess.run(["git", "show", f"{a.old_rev}:harness/check.py"],
                       capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        print(f"  --    OLD-CODE ARM SKIPPED: `git show "
              f"{a.old_rev}:harness/check.py` failed "
              f"({r.stderr.strip()[:120]})")
    elif "leak = \"memory leaked\" in r.stderr" in r.stdout:
        print(f"  --    OLD-CODE ARM SKIPPED: {a.old_rev}'s check.py ALREADY "
              f"has the fix, so it cannot demonstrate the blind spot. Pass "
              f"--old-rev <the commit before TASK_118 landed>.")
    else:
        oldp = os.path.join(SCRATCH, "check_prefix.py")
        open(oldp, "w").write(r.stdout)
        old = load(oldp, "check_old", REPO)
        rep_o, runs_o = run_stage(old, dirs["mutant"], modmod,
                                  f"OLD CODE ({a.old_rev}) on MUTANT-A")
        O = runs_o[0]
        print(f"\n  OLD-CODE   exit={O['exit']}  ub={O['ub']}  "
              f"leak={O.get('leak', '<KEY ABSENT>')}")
        if "leak" not in O and O["ub"] is False:
            print("  ok    the old record has NO leak key and ub=False: a "
                  "reader auditing results/gate/*.json by `ub` saw nothing")
        else:
            print("  FAIL  the old code already recorded the leak, so the "
                  "defect this file documents did not exist as described")
            bad += 1
        if rep_o.failures:
            print(f"  ok    ...and the old gate still FAILED, on the exit "
                  f"code: {rep_o.failures[0][1][:120]}")
        else:
            print("  FAIL  the old gate passed the leaking mutant, which is a "
                  "BIGGER defect than the one this file is about")
            bad += 1

    if not a.keep:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("\n" + ("*** SOMETHING IS WRONG ***" if bad else
                  "ALL ARMS BEHAVE: the leak is recorded, the key is needed, "
                  "the control is clean,\nand the old code showed nothing."))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
