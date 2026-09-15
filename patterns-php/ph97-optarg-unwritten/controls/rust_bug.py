#!/usr/bin/env python3
"""ph97 — the Rust rungs that DO reproduce the defect, built and run.

    python3 patterns-php/ph97-optarg-unwritten/controls/rust_bug.py
    python3 .../rust_bug.py --emit unwrap      # write one variant and stop

=============================================================================
WHY THIS EXISTS, AND WHY IT IS A CONTROL RATHER THAN A RUNG
=============================================================================
No shipped Rust rung on this row reproduces CRASH-126. ⚠⚠ **That is a FINDING
and never a problem** (`CLAUDE.md` rule 6) — but *"safe Rust cannot express
it"* is only worth reporting if somebody tried, so this file tries, twice, and
records what happened.

**IN C THE BUG IS AN OMISSION AND IN RUST IT WOULD BE A COMMISSION.** `typ` is
an `Option<&[u8; NTYP]>` and cannot be read without being opened, so a rung that
wanted the defect has to ADD an operation:

  * `unwrap`    — safe Rust, `.unwrap()` on an unguarded optional.
  * `unchecked` — `unwrap_unchecked()` on the same unguarded optional.

⭐ Both are built from the SHIPPED rungs by deleting exactly `f7326d627962`'s
disjunct, so neither is a hand-written straw man: the only difference from
`safe_naive.rs` / `unsafe.rs` is the 2005 fix.

=============================================================================
⛔⛔ WHAT THIS CONTROL MEASURED, AND IT REFUTED ITS AUTHOR'S FIRST GUESS
=============================================================================
The guess written here first was: *`Option<&T>` is the null-pointer-optimised
layout, so `None` opened unchecked is a reference whose data pointer is null,
and reading byte zero through it faults at address 0 — the same `si_addr` the
PHP 5.0.0 CLI reports.* **It does not.** Measured on this box, same source, one
flag apart (`opt_sweep` in the sidecar):

    opt-level=0   panic + SIGABRT (exit 134)
    opt-level=1   DOES NOT TERMINATE (killed at 60 s)
    opt-level=2   DOES NOT TERMINATE
    opt-level=3   DOES NOT TERMINATE

⭐⭐ **`unwrap_unchecked()` ON `None` IS UNDEFINED BEHAVIOUR, AND LLVM EXPLOITS
IT RATHER THAN LOWERING IT.** The `None` arm is `unreachable_unchecked()`, so
the optimiser is entitled to assume the branch is dead and to compile the
program into anything; what it compiles it into here is a loop that does not
terminate. **The layout guarantee is about the BYTES and says nothing about
what a program that reads through the niche will DO.**

▶ **So the ladder's *does the defect survive?* column on this row reads:**

    C (R1)              SEGV, si_addr=(nil)      the defect, at the address
    safe Rust + unwrap  panic, exit 101          a DETECTED fault
    unsafe Rust         abort (O0) / hang (O1+)  NEITHER -- UB, exploited
    every shipped rung  answers                  the defect is not expressible

⚠ **The must-conditions below were changed to match the measurement and the
first version is quoted above rather than deleted**, because the wrong guess is
the more useful half: it is what a reader would assume.

⚠ The variant directories are fixed-width (`vNN`) and asserted equal in length
(`RECAP_PHP.md` F101).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

SCRATCH = os.path.join(REPO, ".temp", "php97", "rustbug")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
PROBE = os.path.join(REPO, ".tasks-php", "probes", "segaddr.c")
#: seconds. The shipped rungs answer `small.bin` in well under one.
TIMEOUT = 60
GUARDED = "if typ.is_none() || strcasecmp(sel_get(0), opt_get(typ)) == 0 {"
UNGUARDED = "if strcasecmp(sel_get(0), opt_get(typ)) == 0 {"

VARIANTS = {
    "unwrap": ("safe_naive.rs",
               "safe Rust, `.unwrap()` on an unguarded optional -- the defect "
               "becomes a DETECTED fault"),
    "unchecked": ("unsafe.rs",
                  "`unwrap_unchecked()` on an unguarded optional -- the one "
                  "that reproduces C, at the same address"),
}


class _R:
    """A finished (or timed-out) run, in the shape `subprocess.run` returns."""

    def __init__(self, rc, out, err):
        self.returncode, self.stdout, self.stderr = rc, out, err


def _timed(cmd, env, secs):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env,
                           timeout=secs)
        return _R(r.returncode, r.stdout, r.stderr)
    except subprocess.TimeoutExpired as e:
        return _R("TIMEOUT",
                  (e.stdout or b"").decode("latin-1", "replace"),
                  (e.stderr or b"").decode("latin-1", "replace"))


def variant(name, vdir):
    src_name, why = VARIANTS[name]
    src = open(os.path.join(PDIR, src_name)).read()
    assert src.count(GUARDED) == 1, f"{src_name} no longer carries the 2005 guard"
    src = src.replace(GUARDED, UNGUARDED, 1)
    d = os.path.join(SCRATCH, vdir)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    p = os.path.join(d, "k.rs")
    open(p, "w").write(src)
    return p, why


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", choices=sorted(VARIANTS))
    a = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    # `#[path = "../../common/driver.rs"]` from `<SCRATCH>/vNN/k.rs`
    cdir = os.path.join(os.path.dirname(SCRATCH), "common")
    os.makedirs(cdir, exist_ok=True)
    shutil.copy(os.path.join(REPO, "common", "driver.rs"),
                os.path.join(cdir, "driver.rs"))

    if a.emit:
        p, why = variant(a.emit, "v99")
        print(p)
        print(why)
        return 0

    so = os.path.join(SCRATCH, "segaddr.so")
    subprocess.run(["gcc", "-shared", "-fPIC", "-O0", "-o", so, PROBE],
                   check=True)
    inp = os.path.join(PDIR, "inputs", "adversarial-absent.bin")
    benign = os.path.join(PDIR, "inputs", "small.bin")

    rec = {"variants": {}, "problems": []}
    dirs = []
    for i, name in enumerate(sorted(VARIANTS)):
        dirs.append(os.path.join(SCRATCH, f"v{i:02d}"))
    assert len({len(d) for d in dirs}) == 1, "equal path lengths (F101)"

    for i, name in enumerate(sorted(VARIANTS)):
        p, why = variant(name, f"v{i:02d}")
        exe = os.path.join(os.path.dirname(p), "k")
        r = subprocess.run([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                            "-C", "opt-level=3", "-C", "debug-assertions=off",
                            "--cfg", "slb_isolated", p, "-o", exe],
                           capture_output=True, text=True)
        if r.returncode != 0:
            rec["problems"].append(f"{name}: does not build -- {r.stderr[-300:]}")
            continue
        # ⚠⚠ BOTH RUNS ARE TIMED OUT, AND A TIMEOUT IS A RESULT RATHER THAN A
        # FAILURE OF THE HARNESS. The `unchecked` variant is UNDEFINED
        # BEHAVIOUR by construction: LLVM is entitled to compile a read through
        # an opened `None` into anything at all, including a loop that does not
        # terminate, and that outcome has to be RECORDED rather than waited on.
        env = dict(os.environ, LD_PRELOAD=so)
        adv = _timed([exe, inp], env, TIMEOUT)
        ben = _timed([exe, benign], None, TIMEOUT)
        seg = [l.strip() for l in adv.stderr.splitlines()
               if l.startswith("[segaddr]")]
        msg = [l.strip() for l in adv.stderr.splitlines()
               if "panicked" in l or "Option::unwrap" in l]
        rec["variants"][name] = {
            "why": why, "source": VARIANTS[name][0],
            "adversarial": {"exit": adv.returncode,
                            "stdout": adv.stdout.strip(),
                            "segaddr": seg[0] if seg else None,
                            "panic": msg[0][:160] if msg else None},
            "benign": {"exit": ben.returncode, "stdout": ben.stdout.strip()},
        }
        v = rec["variants"][name]
        print(f"  {name:10s} from {VARIANTS[name][0]:14s} "
              f"adversarial exit={str(v['adversarial']['exit']):>7s}  "
              f"benign exit={v['benign']['exit']}")
        if v["adversarial"]["segaddr"]:
            print(f"             {v['adversarial']['segaddr']}")
        if v["adversarial"]["panic"]:
            print(f"             {v['adversarial']['panic']}")

    # -- the opt-level sweep: the finding, not decoration -----------------
    p, _ = variant("unchecked", "v00")
    sweep = {}
    for lvl in ("0", "1", "2", "3"):
        exe = os.path.join(os.path.dirname(p), "k-O" + lvl)
        subprocess.run([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                        "-C", "opt-level=" + lvl, "-C", "debug-assertions=off",
                        "--cfg", "slb_isolated", p, "-o", exe],
                       capture_output=True, text=True, check=True)
        r = _timed([exe, inp], dict(os.environ, LD_PRELOAD=so), TIMEOUT)
        seg = [l.strip() for l in r.stderr.splitlines()
               if l.startswith("[segaddr]")]
        sweep["O" + lvl] = {"exit": r.returncode, "stdout": r.stdout.strip(),
                            "segaddr": seg[0] if seg else None}
        print(f"  unchecked @ opt-level={lvl}: exit={r.returncode} "
              f"{sweep['O' + lvl]['segaddr'] or ''}")
    rec["opt_sweep_unchecked"] = sweep
    print("  ⭐⭐ UB IS EXPLOITED, NOT LOWERED: the layout guarantee is about "
          "the BYTES and says nothing about what a program reading through the "
          "niche will DO. See the module docstring.")

    # -- what each MUST do, AFTER the measurement corrected the guess ------
    u = rec["variants"].get("unwrap", {}).get("adversarial", {})
    k = rec["variants"].get("unchecked", {}).get("adversarial", {})
    ANSWER = "1265852909175663616"   # what every SHIPPED rung returns
    if u.get("exit") != 101:
        rec["problems"].append(
            f"the `unwrap` variant exits {u.get('exit')}, not 101 -- safe Rust "
            f"must turn the defect into a DETECTED fault, and if it does not "
            f"the ladder's *does the defect survive?* column is wrong")
    if k.get("stdout") == ANSWER or k.get("exit") == 0:
        rec["problems"].append(
            f"the `unchecked` variant ANSWERED ({k.get('stdout')!r}) -- the "
            f"whole point of the variant is that deleting f7326d627962 makes it "
            f"stop being a program, and if it answers, the guard is not "
            f"load-bearing in this rung")
    # ⭐ MUST-NOT-FIRE: the SHIPPED rungs answer the same input. Without this
    # arm a harness that broke every build would look like two attacks landing.
    ship = os.path.join(REPO, ".temp", "php-scratch", "build", "ph97",
                        "unsafe-O3-isolated")
    if os.path.exists(ship):
        s = _timed([ship, inp], None, TIMEOUT)
        rec["shipped_unsafe_on_adversarial"] = {"exit": s.returncode,
                                                "stdout": s.stdout.strip()}
        print(f"  N0 MUST-NOT-FIRE shipped unsafe.rs on the same input: "
              f"exit={s.returncode} {s.stdout.strip()!r}")
        if s.returncode != 0 or s.stdout.strip() != ANSWER:
            rec["problems"].append(
                f"the SHIPPED unsafe rung does not answer {ANSWER} on the "
                f"adversarial input, so the two variants above are not isolating "
                f"the 2005 guard -- they are isolating a broken build")
    else:
        rec["problems"].append(
            "the shipped unsafe-O3-isolated binary is absent, so the "
            "MUST-NOT-FIRE control could not run and the two variants prove "
            "nothing about the guard")
    for name, v in rec["variants"].items():
        if v["benign"]["exit"] != 0:
            rec["problems"].append(
                f"{name} does not answer on the BENIGN input; a variant that is "
                f"broken everywhere proves nothing about the adversarial one")

    rec.update(_pin.pin(["safe_naive.rs", "unsafe.rs",
                         "inputs/adversarial-absent.bin"],
                        "python3 controls/rust_bug.py",
                        "two rustc builds and four runs; under a minute"))
    with open(os.path.join(HERE, "rust_bug.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/rust_bug.json -- {len(rec['problems'])} problem(s)")
    for p in rec["problems"]:
        print("  ⛔ " + p)
    return 1 if rec["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
