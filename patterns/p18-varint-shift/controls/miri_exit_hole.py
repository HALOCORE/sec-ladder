#!/usr/bin/env python3
"""THE REGRESSION CHECK FOR `harness/check.py`'s MIRI EXIT-CODE HOLE
(TASK_051_REVIEW M6, fixed at TASK_052).

    python3 patterns/p18-varint-shift/controls/miri_exit_hole.py
    python3 patterns/p18-varint-shift/controls/miri_exit_hole.py --old-rev 676f685

**The hole.** `check.py`'s Miri stage used to decide a row with

    ub = "Undefined Behavior" in r.stderr or "error: unsupported" in r.stderr
    if   ub:                                        fail
    elif r.returncode != 0 and expected_exit == 0:  fail
    elif r.returncode == 0 and got != want:         fail
    else:                                           ok("... no UB, stdout {got!r} matches the model")

so on any input whose `model.py` declares a **non-zero** `expected_exit`,
**neither the exit code nor stdout was ever compared** -- and the `ok` line
asserted that stdout matched. A rung that panicked for the wrong reason, died of
a signal, or exited with a different non-zero code was recorded green. Miri runs
with `debug-assertions` ON, so an arithmetic overflow that every measured cell
of this benchmark masks is a *panic* under Miri -- which is p18's own bug class,
and is why the reproduction lives here.

It is an honest-mistake failure, not an adversarial one, which is the standard
`.memory/02-bench-rules.md`'s threat model sets for gate work: the exposure was
`p01-array-sum/adversarial-shortlen.bin` (`expected_exit` 5),
`p02-buffer-copy/adversarial-capbig.bin` (7) and `.../adversarial-shortlen.bin`
(5) -- three rows, all Miri-stage inputs, on two patterns.

**What this script does.** It reproduces the hole end to end, against the real
`check.py`, and the real `miri`:

  1. writes a p18 blob whose header declares a `payload_len` larger than the
     file -- `model.py`'s only non-zero exit (`expected_exit == 5`,
     `expected_stdout == ""`), so the hole's precondition is met by p18's own
     committed model rather than by a fixture;
  2. writes MUTANT-A: `../unsafe.rs` verbatim against a copy of
     `common/driver.rs` whose `die()` **panics instead of exiting**. Miri then
     reports `rc=101`, empty stdout and NO `Undefined Behavior`;
  3. writes CONTROL-B: the same rung against an unmodified copy of the driver,
     which exits 5 as the model says;
  4. calls `harness/check.py`'s own `check_miri()` on both, and asserts
     **A fails and B passes**. A regression that reopens the hole makes step 4's
     A-half pass and this script exit 1;
  5. if the pre-fix revision is reachable, `git show <rev>:harness/check.py`,
     loads it, and runs *its* `check_miri()` on MUTANT-A to show it reported
     `ok`. Read-only git; skipped with a printed reason if the object is gone.

Nothing here touches the pattern's own inputs, cells or gate record: the blob
and both mutants are written under `.temp/p18/mirihole/pid<PID>/` and the
pattern dir handed to `check_miri` is that scratch dir, not
`patterns/p18-varint-shift/`.
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
SCRATCH = os.path.join(REPO, ".temp", "p18", "mirihole", f"pid{os.getpid()}")

# `1b41c85` (TASK_032) is the LAST commit that touched `harness/check.py` before
# TASK_052 fixed this, so `git show 1b41c85:harness/check.py` is exactly the code
# that reported the mutant green. Pinned rather than derived, because
# `git log -1 -- harness/check.py` points at the FIX once the fix is committed.
# Step 5 skips itself, with a reason, if the object is not in the clone.
PRE_FIX_REV = "1b41c85"

CONTRACT = {"miri": {"pair": ["unsafe", "verus"], "required": True,
                     "sources": ["unsafe_probe.rs"],
                     "reason": "TASK_052 regression fixture"}}
IDENTITY = [{"pair": "unsafe vs verus", "opt": "O3", "level": "exact"}]


def load(path, name, repo):
    """Import a `check.py` by path, then repoint its `REPO` at the real tree.

    `check.py` derives `REPO` from its own `__file__`, so a copy living
    somewhere else computes the wrong root; `sys.path` is already primed with
    the real `common/` and `harness/` below, and every later use of `REPO` is a
    scratch path or a tool path."""
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.REPO = repo
    return m


def write_sources():
    """MUTANT-A and CONTROL-B, each in its own directory so `check_miri`'s
    `cwd=pdir` and the `#[path]` include cannot cross."""
    src = open(os.path.join(PDIR, "unsafe.rs")).read()
    assert '#[path = "../../common/driver.rs"]' in src, \
        "unsafe.rs no longer includes the driver by that path"
    drv = open(os.path.join(REPO, "common", "driver.rs")).read()
    old = ("fn die(code: i32, msg: &str) -> ! {\n"
           "    eprintln!(\"{}\", msg);\n"
           "    std::process::exit(code)\n"
           "}")
    assert drv.count(old) == 1, "common/driver.rs's die() is not the pinned text"
    mut = ("fn die(code: i32, msg: &str) -> ! {\n"
           "    eprintln!(\"{}\", msg);\n"
           "    let _ = code;\n"
           "    panic!(\"TASK_052 MUTANT: this rung panics instead of exiting "
           "{}\", code)\n"
           "}")
    out = {}
    for tag, driver in (("mutant", drv.replace(old, mut)), ("control", drv)):
        d = os.path.join(SCRATCH, tag)
        os.makedirs(os.path.join(d, "inputs"), exist_ok=True)
        open(os.path.join(d, "driver_mut.rs"), "w").write(driver)
        open(os.path.join(d, "unsafe_probe.rs"), "w").write(
            src.replace('#[path = "../../common/driver.rs"]',
                        '#[path = "driver_mut.rs"]'))
        out[tag] = d
    return out


def write_truncated_blob(path):
    """A p18 input whose declared `payload_len` exceeds the file.

    `common/driver.rs` rejects it with `die(EXIT_OPEN + 1, ...)` -- exit 5 --
    and `../model.py`'s `expected_exit` returns 5 for exactly this shape
    (`truncated`), with `expected_stdout` empty. That is the only non-zero exit
    p18's driver can produce, and it is what puts the row on the branch the
    hole lived in."""
    body = open(os.path.join(PDIR, "inputs", "small.bin"), "rb").read()
    payload = body[16:16 + 64]                 # 64 real payload bytes
    with open(path, "wb") as f:
        f.write(struct.pack("<QQ", 4, len(payload) + 4096) + payload)
    return path


def run_stage(mod, pdir, modmod, indir, label):
    rep = mod.Report()
    print(f"\n---- {label}: {os.path.basename(os.path.dirname(pdir))}/"
          f"{os.path.basename(pdir)} ----")
    out = mod.check_miri(pdir, rep, CONTRACT, IDENTITY, modmod, indir,
                         ["probe-truncated.bin"])
    runs = [r for r in (out.get("runs") or []) if "blocked" not in r]
    return rep, out, runs


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old-rev", default=PRE_FIX_REV,
                    help="revision whose harness/check.py had the hole")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()

    sys.path.insert(0, os.path.join(REPO, "common"))
    sys.path.insert(0, os.path.join(REPO, "harness"))
    check = load(os.path.join(REPO, "harness", "check.py"), "check_now", REPO)
    modmod = load(os.path.join(PDIR, "model.py"), "p18model", REPO)

    dirs = write_sources()
    for d in dirs.values():
        write_truncated_blob(os.path.join(d, "inputs", "probe-truncated.bin"))
    probe = os.path.join(dirs["mutant"], "inputs", "probe-truncated.bin")
    m = modmod.build(probe)
    print(f"blob: {probe}")
    print(f"      model.py: expected_exit={m.expected_exit} "
          f"expected_stdout={m.expected_stdout!r} truncated={m.truncated}")
    if m.expected_exit == 0:
        raise SystemExit("the probe blob does not reach a non-zero "
                         "expected_exit; the fixture is broken")

    bad = 0
    rep_a, _, runs_a = run_stage(check, dirs["mutant"], modmod,
                                 os.path.join(dirs["mutant"], "inputs"),
                                 "MUTANT-A (die() panics)")
    rep_b, _, runs_b = run_stage(check, dirs["control"], modmod,
                                 os.path.join(dirs["control"], "inputs"),
                                 "CONTROL-B (shipped driver)")
    if not runs_a or not runs_b:
        raise SystemExit("miri produced no run (blocked or missing) -- this "
                         "check needs a working miri; see TOOLCHAIN.md")

    print("\n==== verdict ====")
    print(f"  MUTANT-A   miri exit={runs_a[0]['exit']} "
          f"ub={runs_a[0]['ub']} stdout={runs_a[0]['stdout']!r} "
          f"model_exit={m.expected_exit}")
    print(f"  CONTROL-B  miri exit={runs_b[0]['exit']} "
          f"ub={runs_b[0]['ub']} stdout={runs_b[0]['stdout']!r} "
          f"model_exit={m.expected_exit}")
    if rep_a.failures:
        print(f"  ok    the fixed gate FAILS the mutant: "
              f"{rep_a.failures[0][1][:150]}")
    else:
        print("  FAIL  the fixed gate reported the mutant GREEN -- the "
              "TASK_051_REVIEW M6 hole is open again")
        bad += 1
    if rep_b.failures:
        print(f"  FAIL  the fixed gate also fails the CONTROL, so it is not "
              f"discriminating: {rep_b.failures[0][1][:150]}")
        bad += 1
    else:
        print("  ok    the fixed gate PASSES the unmutated rung on the same "
              "blob, so the failure above is the panic and not the exit code "
              "being non-zero")

    # ---- step 5: the pre-fix code, from git, on the same mutant ------------
    r = subprocess.run(["git", "show", f"{a.old_rev}:harness/check.py"],
                       capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        print(f"  --    step 5 SKIPPED: `git show {a.old_rev}:harness/check.py`"
              f" failed ({r.stderr.strip()[:120]}), so the 'and it passed the "
              f"old gate' half is not re-measured here")
    else:
        oldp = os.path.join(SCRATCH, "check_prefix.py")
        open(oldp, "w").write(r.stdout)
        old = load(oldp, "check_old", REPO)
        rep_o, _, runs_o = run_stage(old, dirs["mutant"], modmod,
                                     os.path.join(dirs["mutant"], "inputs"),
                                     f"MUTANT-A under harness/check.py@"
                                     f"{a.old_rev}")
        if rep_o.failures:
            print(f"  --    the pre-fix gate ALSO failed the mutant "
                  f"({rep_o.failures[0][1][:100]}) -- then {a.old_rev} is not "
                  f"the revision with the hole")
        else:
            print(f"  ok    harness/check.py@{a.old_rev} reported the same "
                  f"mutant GREEN (0 failures), which is the regression this "
                  f"fixture exists to catch")

    if not a.keep:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("\nmiri_exit_hole.py: " + ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
