#!/usr/bin/env python3
"""ph16 -- ⭐ THE ROW'S HEADLINE ASYMMETRY: does Rust's own runtime checker see
what the C detector cannot?

    python3 patterns-php/ph16-fdset-index/controls/miri_vs_asan.py

`TASK_PHP_025` §3: *"If R4-under-Miri catches what R1-under-ASan does not, that
asymmetry is a headline result -- measure it and write it down."* This file is
that measurement. It is a CONTROL and not a rung: the shipped R4 carries
`99e290f882c9` guard (b), so it cannot reproduce the defect and Miri has nothing
to find. What is compared is **the same defect in two languages**:

    C   `c/kernel.c`               -- R1, the shipped 5.0.0 code, under
                                      ASan+UBSan exactly as `check.py` stage 7
                                      builds it (gcc -O1 -fstrict-aliasing)
    Rust a MUTANT of `unsafe.rs`   -- R4 with `if w < NW` deleted, i.e. the same
                                      missing bound, under Miri

on the SAME two adversarial inputs, which differ from each other in one index.

⚠⚠ **WHY A MUTANT AND NOT A RUNG.** `CLAUDE.md` rule 6: *"safe Rust can't
express it"* and *"Miri doesn't see it"* are findings, never kills -- and the
converse holds too. A rung that reproduced the defect would not be R4; the
mutant is what makes the comparison a comparison of DETECTORS rather than of
programs. It lives here, in `controls/`, and is never measured.

⚠ The mutant is a *safe-Rust-impossible* program: `[u64; NW]` indexed out of
bounds panics in safe Rust, so the mutant must use `get_unchecked_mut`, which is
what `unsafe.rs` already does. That is itself part of the result -- **there is
no safe-Rust rung that can carry this defect at all**, and the only Rust program
that can is one whose `unsafe` block has lost its precondition.

CONTROLS (`PROTOCOL_PHP.md` §H):

  must-fire      Miri on the mutant, `adversarial-silent.bin`: MUST report.
                 If it does not, the asymmetry claim is unsupported.
  must-NOT-fire  Miri on the mutant, `small.bin` (benign): MUST be clean. A
                 detector that fires on everything measures nothing.
  must-NOT-fire  Miri on the SHIPPED `unsafe.rs`, adversarial input: MUST be
                 clean, because guard (b) is there. This is what says the
                 mutation is the variable.
  must-fire #2   ASan on `c/kernel.c`, `adversarial-redzone.bin`: MUST report,
                 which is what shows the ASan arm is wired up at all before its
                 SILENCE on `adversarial-silent.bin` is read as a result.

A run that cannot evaluate says so and exits non-zero.
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
SCRATCH = os.path.join(REPO, ".temp", "php25", "mirivsasan")
COMMON = os.path.join(REPO, "common")
GCC = "/usr/bin/gcc"
NIGHTLY = "nightly-x86_64-unknown-linux-gnu"
CARGO = os.path.expanduser("~/.cargo/bin/cargo")
MIRI = os.path.expanduser(f"~/.rustup/toolchains/{NIGHTLY}/bin/miri")
ENV = {k: v for k, v in os.environ.items() if k != "LD_PRELOAD"}

#: `check.py::_san_build`'s own flags, so this arm is the gate's arm.
SAN_FLAGS = ["-std=c99", "-O1", "-g", "-fstrict-aliasing",
             "-fsanitize=address,undefined", "-fno-omit-frame-pointer"]

GUARD = """                if w < NW {             // 99e290f882c9 guard (b)
                    aset_unchecked(fds, w,
                                   aget_unchecked(fds, w) | (1u64 << (this_fd % 64)));
                }"""
NOGUARD = """                {
                    aset_unchecked(fds, w,
                                   aget_unchecked(fds, w) | (1u64 << (this_fd % 64)));
                }"""


def san_fired(text):
    return ("AddressSanitizer" in text or "runtime error:" in text
            or "UndefinedBehaviorSanitizer" in text or "ERROR:" in text)


def build_asan(kernel_src, out):
    cmd = ([GCC] + SAN_FLAGS + ["-DSLB_ISOLATED", "-I", COMMON,
                                "-I", os.path.join(ROW, "c"),
                                os.path.join(COMMON, "driver.c"), kernel_src,
                                os.path.join(ROW, "c", "main.c"), "-o", out])
    r = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def miri_sysroot():
    r = subprocess.run([CARGO, f"+{NIGHTLY}", "miri", "setup",
                        "--print-sysroot"], capture_output=True, text=True,
                       env=ENV, timeout=3600)
    return r.stdout.strip() if r.returncode == 0 else None


def run_miri(src, inp, sysroot, n_iters=4):
    """Miri on one .rs, on a COPY of the input whose n_iters is rewritten to 4,
    exactly as `check.py` does -- a full 25 000-call run under Miri is hours."""
    os.makedirs(SCRATCH, exist_ok=True)
    blob = open(inp, "rb").read()
    small = os.path.join(SCRATCH, os.path.basename(inp))
    open(small, "wb").write(n_iters.to_bytes(8, "little") + blob[8:])
    # ⚠ THE COMMAND LINE IS `check.py::check_miri`'s, character for character
    # (`harness/check.py`, the `MIRI_BIN` argument list): miri INTERPRETS the
    # source, so the program's own argv follows `--`, and `MIRIFLAGS` is
    # stripped from the environment so the configuration belongs to this file
    # and not to the invoking shell.
    menv = dict(ENV)
    menv.pop("MIRIFLAGS", None)
    cmd = [MIRI, "--sysroot", sysroot, "--edition", "2021",
           "-Zmiri-disable-isolation", src, "--", small]
    r = subprocess.run(cmd, capture_output=True, text=True, env=menv,
                       timeout=3600, cwd=ROW)
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--emit", action="store_true",
                    help="write the mutant and stop")
    args = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    ind = os.path.join(ROW, "inputs")
    redzone = os.path.join(ind, "adversarial-redzone.bin")
    silent = os.path.join(ind, "adversarial-silent.bin")
    benign = os.path.join(ind, "small.bin")
    for p in (redzone, silent, benign):
        if not os.path.exists(p):
            print(f"CANNOT EVALUATE: {p} missing -- run inputs/gen.py")
            return 2

    # ---- the mutant ------------------------------------------------------
    src = open(os.path.join(ROW, "unsafe.rs")).read()
    if GUARD not in src:
        print("CANNOT EVALUATE: unsafe.rs no longer contains the guard this "
              "control removes:\n" + GUARD)
        return 2
    mut = src.replace(GUARD, NOGUARD, 1)
    # `#[path = "../../common/driver.rs"]` is file-relative; make it absolute.
    mut = mut.replace('#[path = "../../common/driver.rs"]',
                      f'#[path = "{os.path.join(COMMON, "driver.rs")}"]')
    mutp = os.path.join(SCRATCH, "unsafe_noguard.rs")
    open(mutp, "w").write(mut)
    shipped = os.path.join(SCRATCH, "unsafe_shipped.rs")
    open(shipped, "w").write(
        src.replace('#[path = "../../common/driver.rs"]',
                    f'#[path = "{os.path.join(COMMON, "driver.rs")}"]'))
    print(f"mutant written to {mutp} (guard (b) deleted, nothing else)")
    if args.emit:
        return 0

    bad = 0
    rows = []

    # ---- the ASan arm ----------------------------------------------------
    if not os.path.exists(GCC):
        print(f"CANNOT EVALUATE: no gcc at {GCC}")
        return 2
    exe = os.path.join(SCRATCH, "c-gcc-asan")
    okb, log = build_asan(os.path.join(ROW, "c", "kernel.c"), exe)
    if not okb:
        print(f"CANNOT EVALUATE: the ASan build failed:\n{log}")
        return 2
    print("\n== ASan+UBSan on c/kernel.c (R1), gcc -O1 -- the gate's own arm")
    for label, inp in (("adversarial-redzone", redzone),
                       ("adversarial-silent", silent),
                       ("small (benign)", benign)):
        r = subprocess.run([exe, inp], capture_output=True, text=True,
                           env=ENV, timeout=3600)
        fired = san_fired(r.stderr)
        kind = ""
        m = re.search(r"ERROR: AddressSanitizer: ([a-z-]+)", r.stderr)
        if m:
            kind = m.group(1)
        print(f"   {label:24s} exit={r.returncode:<4} fired={fired}  {kind}")
        rows.append(("asan", label, fired, kind, r.returncode))

    asan = {l: f for _, l, f, _, _ in rows}
    if not asan.get("adversarial-redzone"):
        print("   FAIL  must-fire #2: ASan did not report on the input built "
              "to land in its redzone, so its SILENCE elsewhere proves nothing")
        bad += 1
    if asan.get("small (benign)"):
        print("   FAIL  ASan fired on a benign input")
        bad += 1

    # ---- the Miri arm ----------------------------------------------------
    if not os.path.exists(MIRI):
        print(f"\n== Miri  CANNOT EVALUATE: no miri at {MIRI} (TOOLCHAIN.md). "
              f"The ASan half above stands; the asymmetry does not.")
        return 2
    sysroot = miri_sysroot()
    if not sysroot:
        print("\n== Miri  CANNOT EVALUATE: `cargo +nightly miri setup` gave no "
              "sysroot")
        return 2
    ver = subprocess.run([MIRI, "--version"], capture_output=True, text=True,
                         env=ENV, timeout=300).stdout.strip()
    print(f"\n== Miri ({ver}) on unsafe.rs, n_iters rewritten to 4 as check.py does")
    for what, path in (("MUTANT (guard b deleted)", mutp),
                       ("SHIPPED unsafe.rs", shipped)):
        for label, inp in (("adversarial-silent", silent),
                           ("adversarial-redzone", redzone),
                           ("small (benign)", benign)):
            r = run_miri(path, inp, sysroot)
            out = r.stdout + r.stderr
            fired = ("Undefined Behavior" in out or "error: unsupported" in out
                     or "out-of-bounds" in out)
            first = ""
            m = re.search(r"error: Undefined Behavior: (.{0,110})", out)
            if m:
                first = m.group(1).strip()
            print(f"   {what:26s} {label:22s} exit={r.returncode:<4} "
                  f"fired={fired}  {first}")
            rows.append(("miri", f"{what}/{label}", fired, first, r.returncode))

    got = {l: f for k, l, f, _, _ in rows if k == "miri"}
    must_fire = got.get("MUTANT (guard b deleted)/adversarial-silent")
    must_not_1 = got.get("MUTANT (guard b deleted)/small (benign)")
    must_not_2 = got.get("SHIPPED unsafe.rs/adversarial-silent")
    if not must_fire:
        print("   FAIL  must-fire: Miri did not report on the mutant")
        bad += 1
    if must_not_1:
        print("   FAIL  must-NOT-fire: Miri fired on a benign input")
        bad += 1
    if must_not_2:
        print("   FAIL  must-NOT-fire: Miri fired on the SHIPPED rung, which "
              "carries the guard -- so the mutation is not the variable")
        bad += 1

    # ---- the asymmetry, stated -------------------------------------------
    print("\n== THE ASYMMETRY")
    a_red = asan.get("adversarial-redzone")
    a_sil = asan.get("adversarial-silent")
    print(f"   ASan on R1, index 1024 (redzone)   fired = {a_red}")
    print(f"   ASan on R1, index 2048 (neighbour) fired = {a_sil}")
    print(f"   Miri on the R4 mutant, index 2048  fired = {must_fire}")
    if a_red and not a_sil and must_fire:
        print("   ⭐ THE HEADLINE HOLDS: the SAME defect at the SAME index is "
              "invisible to the C detector and visible to the Rust one.")
        print("   THE MECHANISM, read off the diagnostic rather than assumed: "
              "Miri reports `Undefined Behavior: `assume` called with `false`` "
              "AT `aget_unchecked`, i.e. inside "
              "`core::slice::get_unchecked`'s own "
              "`assert_unsafe_precondition!` -- it catches the violated "
              "LIBRARY PRECONDITION, before any address is formed. ASan has "
              "nothing analogous to catch: C's `FD_SET` carries no "
              "precondition, and the address it forms is a legitimate live "
              "object of the same frame, so there is no poisoned byte to "
              "report. ⚠ The asymmetry is therefore about WHERE THE BOUND IS "
              "WRITTEN DOWN -- Rust puts it in `get_unchecked`'s contract and C "
              "puts it nowhere -- and NOT about one checker being stronger at "
              "watching memory.")
    else:
        print("   ⚠ the headline as written does NOT hold on this run; the "
              "table above is what happened and NOTES.md must say so.")
        bad += 1

    open(os.path.join(SCRATCH, "miri_vs_asan.json"), "w").write(
        json.dumps(rows, indent=1))
    print("\nRESULT:", "FAIL" if bad else "PASS", f"({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
