#!/usr/bin/env python3
"""ph96 -- can Rust reproduce the defect ON PURPOSE?

    python3 patterns-php/ph96-outparam-unwritten/controls/rust_bug.py

No shipped Rust rung reproduces this defect, and `CLAUDE.md` rule 6 makes that a
FINDING and never a problem. ▶ **But the interesting question is what happens to
a rung written DELIBERATELY to reproduce it**, and that is measured here rather
than argued.

Two variants, each `safe_naive.rs` / `unsafe.rs` with the `zend_object_handlers.c
:385` NULL test DELETED from the release path -- i.e. the C's own omission,
transplanted:

  `unwrap`      safe Rust. `Option::unwrap` on `None`.
  `unchecked`   unsafe Rust. `Option::unwrap_unchecked` on `None`.

⚠⚠ **`unwrap_unchecked` ON `None` IS UB AND LLVM MAY EXPLOIT IT RATHER THAN
LOWER IT.** The `None` arm is `unreachable_unchecked()`, so the optimiser may
assume the branch is dead and compile the program into anything. On `ph97` it
compiled it into something that does not terminate; what it does HERE is the
measurement. **The niche layout guarantee is about the BYTES and says nothing
about what a program that reads through the niche will DO.**

⭐ The interesting contrast is with `controls/widened_domain.py`'s opt sweep,
where the C rung's SAME defect gives a SIGSEGV under gcc at every level and a
silent wrong answer under clang above `-O1`. Neither language's failure mode here
is a property of the source alone.

N0 MUST-NOT-FIRE: the SHIPPED `unsafe.rs`, same input, must answer.
"""
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
import second_limb as sl  # noqa: E402

SCRATCH = os.path.join(REPO, ".temp", "php96", "rustbug")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")

GUARD = """    let retval: Option<&mut Zval> = if wrote_out { Some(slot) } else { None };
    if retval.is_none() {
        // :385-389. With EG(exception) set -- which is the state that put the
        // sentinel here -- the E_ERROR at :387 is NOT raised.
        return acc.wrapping_mul(31).wrapping_add(TAG_UNDEF);
    }
"""
NO_GUARD = ("    let retval: Option<&mut Zval> = "
            "if wrote_out { Some(slot) } else { None };\n")


def build(vdir, rung, delete_guard, opt):
    d = os.path.join(SCRATCH, vdir)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    src = open(os.path.join(PDIR, rung + ".rs")).read()
    if delete_guard:
        assert src.count(GUARD) == 1, f"{rung}.rs's read guard has moved"
        src = src.replace(GUARD, NO_GUARD, 1)
    p = os.path.join(d, "k.rs")
    open(p, "w").write(src)
    out = os.path.join(d, "k")
    r = subprocess.run([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                        "-C", f"opt-level={opt}", "-C", "debug-assertions=off",
                        "--cfg", "slb_isolated", p, "-o", out],
                       capture_output=True, text=True)
    return (out if r.returncode == 0 else None), r


def run(exe, inp):
    try:
        r = subprocess.run([exe, inp], capture_output=True, text=True,
                           timeout=60)
    except subprocess.TimeoutExpired:
        return {"exit": "TIMEOUT", "stdout": "", "stderr": ""}
    return {"exit": r.returncode, "stdout": r.stdout.strip(),
            "stderr": re.sub(r"\s+", " ", (r.stderr or "").strip())[:200]}


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    cdir = os.path.join(os.path.dirname(SCRATCH), "common")
    os.makedirs(cdir, exist_ok=True)
    shutil.copy(os.path.join(REPO, "common", "driver.rs"),
                os.path.join(cdir, "driver.rs"))
    problems = []
    # the read shape's sentinel: the state the deleted guard used to catch.
    inp = os.path.join(SCRATCH, "sent-read.bin")
    sl.make_input(inp, "read")
    rec = {"problems": problems, "input": "one window, one SUCCESS-with-nothing-"
           "written record at the READ shape", "variants": {}}

    print(f"{'variant':34s}{'opt':5s}{'exit':>9s}  stdout / diagnostic")
    plan = [("v00", "unwrap (safe, guard deleted)", "safe_naive", True),
            ("v01", "unchecked (unsafe, guard deleted)", "unsafe", True),
            ("v02", "SHIPPED unsafe.rs (N0)", "unsafe", False)]
    for vdir, label, rung, dele in plan:
        rec["variants"][label] = {}
        for opt in (0, 1, 2, 3):
            exe, r = build(vdir, rung, dele, opt)
            if exe is None:
                rec["variants"][label][f"O{opt}"] = {
                    "build_error": r.stderr[:200]}
                print(f"{label:34s}O{opt:<4d}{'BUILD FAIL':>9s}  "
                      f"{r.stderr[:60]}")
                continue
            got = run(exe, inp)
            rec["variants"][label][f"O{opt}"] = got
            txt = got["stdout"] or got["stderr"]
            print(f"{label:34s}O{opt:<4d}{str(got['exit']):>9s}  {txt[:60]}")

    # N0 MUST-NOT-FIRE
    n0 = rec["variants"]["SHIPPED unsafe.rs (N0)"]
    ok0 = all(v.get("exit") == 0 and v.get("stdout") for v in n0.values())
    print(f"\nN0 MUST-NOT-FIRE  the SHIPPED unsafe.rs answers at every opt "
          f"level -> {'ok' if ok0 else 'BAD'}")
    if not ok0:
        problems.append("the SHIPPED unsafe.rs does not answer on this input, "
                        "so the two variants above are not isolating the "
                        "deleted guard")
    # N1 MUST-FIRE: safe Rust with the guard deleted must be DETECTED.
    u = rec["variants"]["unwrap (safe, guard deleted)"]
    detected = all(v.get("exit") in (101, 134, -6) or v.get("exit") == "TIMEOUT"
                   for v in u.values())
    rec["safe_unwrap_detected"] = detected
    print(f"N1 MUST-FIRE  safe Rust + `unwrap`, guard deleted, is DETECTED at "
          f"every opt level -> {'ok' if detected else 'BAD'}")
    if not detected:
        problems.append(f"safe Rust with the guard deleted produced "
                        f"{[v.get('exit') for v in u.values()]}; a panic (101) "
                        f"or an abort is the only outcome `unwrap` on `None` "
                        f"has, and anything else means the mutant is not "
                        f"reaching the None arm")
    # the unsafe one has no required outcome -- it is the measurement.
    rec["unsafe_unchecked_outcomes"] = {
        k: v.get("exit") for k, v in
        rec["variants"]["unchecked (unsafe, guard deleted)"].items()}
    print(f"\n⭐ unsafe + `unwrap_unchecked`, guard deleted: "
          f"{rec['unsafe_unchecked_outcomes']}")
    print("   ⚠ NO required outcome here. UB has none; what LLVM does with "
          "it is the result.")

    rec.update(_pin.pin(["safe_naive.rs", "unsafe.rs"],
                        "python3 controls/rust_bug.py",
                        "twelve rustc builds and twelve runs; a minute"))
    with open(os.path.join(HERE, "rust_bug.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/rust_bug.json -- {len(problems)} problem(s)")
    for p in problems:
        print("  ⛔ " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
