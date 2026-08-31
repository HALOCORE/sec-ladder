#!/usr/bin/env python3
"""p34 CONTROLS: **BOTH BRANCHES OF `.memory/01-ladder.md`'s TEMPORAL LAW, IN ONE
ROW, SELECTED BY THE PORT.**

    python3 patterns/p34-refcount-stack/controls/safe_arms.py

THE LAW AND WHY p34 IS THE ROW THAT SETTLES IT
----------------------------------------------
`.memory/01-ladder.md`: *safe Rust's temporal guarantee is a guarantee about the
ALLOCATOR; a structure that recycles its own storage gets no guarantee at all.*
Outcome 3 had three demonstrations and they disagreed -- `p32`'s safe Rust
reproduces the buggy C bit for bit, `p28`'s cannot reproduce it at all, and `p35`
shows both shapes in one row on a non-temporal axis. **p34 puts both TEMPORAL
branches in one row and the selector is the PORT, not the pattern:**

  branch A, `Rc`            the shipped R2/R3. **The bug is NOT EXPRESSIBLE.**
                            `Rc::clone` publishes the second reference and
                            increments in ONE operation, and the two ways to get
                            a second reference without it DO NOT COMPILE:
                            `arm_safe_rc_move.rs` -> `error[E0507]`,
                            `arm_safe_rc_borrow.rs` -> `error[E0502]`. p28's
                            shape.
  branch B, INDEX ARENA     `arm_safe_arena.rs`, equally safe Rust under
                            `#![forbid(unsafe_code)]`. **REPRODUCES `c/kernel.c`
                            BIT FOR BIT on every input**, the recycle-divergent
                            one included, because the arena recycles its own
                            storage and the allocator is never asked. p32's
                            shape.

⚠⚠ **The two must-fail arms are what make branch A a measurement rather than an
assertion.** A file that does not compile is the only evidence that a spelling is
unavailable, and this script asserts the FAILURE and records the error code --
a build that succeeded would refute this row's safe-Rust finding and is a louder
result than the failure. `.memory/02-bench-rules.md`'s rule about controls that
have never been shown capable of failing applies in the mirror here: these two
have never been shown capable of PASSING, so the script also builds the shipped
`safe_naive.rs` on the same command line to prove the compiler and the driver
path are working.

⚠⚠⚠ **AND THAT WAS NOT ENOUGH, WHICH IS WHY THE `negative_controls` SECTION
EXISTS** (`TASK_155_REPORT` B1, landed at `TASK_156`). *"This file does not
compile"* is evidence about safe Rust only if the thing that stops it compiling
is **the bug**. It was not checked, and on one of the two arms it is not:

  * ⚠ **The error CODE carries no information about reference counting.** A
    12-line program with no `Rc`, no container and no count prints the same
    `E0507`; a `Vec` push past a live `&v[0]` prints the same `E0502`. So
    `want_code` below pins a spelling, not a finding. **Third time on this
    project** (`p25`'s `E0502`, `p28`'s `E0382`/`E0499`).
  * ✅ **The attribution test is the `_nodup` twin**, generated mechanically
    from the arm itself: replace the WHOLE `c % 4 == 1` arm with the `SENT`
    fold the same file already writes when its guard fails. That program
    publishes no second reference and therefore **cannot have p34's bug**, so
    it must NOT print the same error.
  * **Measured:** `arm_safe_rc_move.rs`'s twin **COMPILES** -- its `E0507` is
    attributable to the DUP body. `arm_safe_rc_borrow.rs`'s twin **fails with
    the identical `E0502` at the identical line** -- the `objs.push` on the
    **NEW** path, against the live `&objs[..]` borrows -- so that arm's error
    is not about the duplication. Both outcomes are asserted; either one moving
    is a problem. ⚠ The identity is asserted RELATIVELY (arm line == twin
    line), never against a fixed number: this arm's `E0502` moved from line 68
    to line 98 when `TASK_156` extended its own header comment, and a pinned
    number would have started lying at that moment.
  * ✅ **`arm_safe_rc_borrow_frozen.rs`** completes the attribution: the DUP
    line itself, character for character, over a pre-built owner, **compiles
    and runs**. What safe Rust refuses on the borrow route is mutating the
    owner while the borrows are live -- and a `free` IS an owner mutation, so
    the route is closed at the DESTRUCTION rather than at the duplication.

⚠ **Branch B's arena arm has both cfgs**, `--cfg slb_arm_retain` and without, so
the arm is a two-cell experiment and not one: with the retain it must equal
`../model.py`, without it it must equal `c/kernel.c`. One file, one `#[cfg]`, and
the `#[cfg]` is the safety line.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * `safe_naive.rs` COMPILES on the same command line (the sanity arm);
  * `arm_safe_rc_move.rs` FAILS with `E0507`;
  * `arm_safe_rc_borrow.rs` FAILS with a borrow-checker error;
  * **NEGATIVE CONTROLS**: `arm_safe_rc_move.rs`'s `_nodup` twin COMPILES;
    `arm_safe_rc_borrow.rs`'s `_nodup` twin does NOT (and that is the published
    reading of that arm, so a change either way is a problem);
    `arm_safe_rc_borrow_frozen.rs` COMPILES and prints `201`;
  * **the arena high-water mark is MEASURED**, from an instrumented copy of
    `arm_safe_arena.rs`, and never exceeds `CAP` = 16 of `ARENA` = 32;
  * `arm_safe_arena.rs --cfg slb_arm_retain` equals `../model.py` on every input;
  * `arm_safe_arena.rs` without it equals **`c/kernel.c`** on every input,
    including the two on which C's own two rungs AGREE and the two on which they
    DIVERGE;
  * Miri finds NOTHING in the arena arm on any input -- the p32 half of the
    detector-coverage result, and the reason the storage choice is load-bearing.
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
COMMON = os.path.join(REPO, "common")
INPUTS = os.path.join(PDIR, "inputs")
OUT = os.path.join(REPO, ".temp", "p34ctl")
# ⚠ Generated arm sources go HERE and not in OUT itself: every arm carries
# `#[path = "../../../common/driver.rs"]`, which rustc resolves against the
# SOURCE file's directory, so a generated copy must sit exactly THREE levels
# below the repo root the way `patterns/pNN/controls/` does. Measured: with the
# twins written to `.temp/p34ctl/` the negative controls failed on
# `couldn't read .../common/driver.rs` and said nothing about borrow checking.
GEN = os.path.join(OUT, "gen")

GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
RUSTC = os.environ.get("SLB_RUSTC", os.path.expanduser("~/.cargo/bin/rustc"))
CARGO = os.environ.get("SLB_CARGO", os.path.expanduser("~/.cargo/bin/cargo"))
NIGHTLY = "nightly-x86_64-unknown-linux-gnu"
MIRI_BIN = os.path.expanduser(f"~/.rustup/toolchains/{NIGHTLY}/bin/miri")

RFLAGS = ["-C", "opt-level=3", "-C", "debug-assertions=off",
          "-C", "codegen-units=1"]
MIRI_ITERS = 4


def sh(cmd, **kw):
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    return subprocess.run(cmd, capture_output=True, text=True, env=env,
                          timeout=1800, **kw)


def rustc(src, out, cfgs=()):
    cmd = [RUSTC] + RFLAGS
    for c in cfgs:
        cmd += ["--cfg", c]
    cmd += [src, "-o", out]
    r = sh(cmd)
    codes = sorted(set(re.findall(r"error\[(E\d+)\]", r.stderr)))
    first = ""
    for ln in r.stderr.splitlines():
        if ln.startswith("error"):
            first = ln.strip()
            break
    # The line rustc points its FIRST primary span at. Without it "the arm
    # fails" cannot be told from "the arm fails on the line it exists for" --
    # which is exactly the gap TASK_155 B1 found (`E0502` on the NEW path).
    m = re.search(r"\n\s*-->\s*\S+:(\d+):\d+", r.stderr)
    return {"ok": r.returncode == 0, "error_codes": codes,
            "error_line": int(m.group(1)) if m else None,
            "first_error": first[:200]}


# --------------------------------------------------------- negative controls --
#: The `c % 4 == 1` (DUP) arm of a p34 safe-Rust arm, and what replaces it in
#: the `_nodup` twin: the SENT fold the same file already writes when the DUP
#: guard fails. The twin publishes NO second reference and therefore CANNOT
#: have p34's bug, so it must not print the same error the arm does.
DUP_OPEN = "        } else if c % 4 == 1 {\n"
DUP_CLOSE = "        } else if c % 4 == 2 {\n"
NODUP_BODY = ("            // NEGATIVE CONTROL (safe_arms.py): the whole DUP arm\n"
              "            // replaced by the SENT fold this file already writes\n"
              "            // when the guard fails. No second reference is ever\n"
              "            // published, so this program CANNOT have p34's bug.\n"
              "            acc = acc.wrapping_mul(31).wrapping_add(SENT);\n")


def make_nodup(src, dst):
    """`src` with its whole DUP arm replaced by the SENT fold. Asserted, not
    assumed: a rewrite of either marker makes this raise rather than silently
    produce a twin that is not one."""
    t = open(src).read()
    if t.count(DUP_OPEN) != 1 or t.count(DUP_CLOSE) != 1:
        raise SystemExit(f"safe_arms.py: cannot locate the DUP arm in {src} "
                         f"({t.count(DUP_OPEN)} / {t.count(DUP_CLOSE)} markers). "
                         f"The `_nodup` negative control cannot be generated, so "
                         f"branch A's attribution is UNMEASURED.")
    i = t.index(DUP_OPEN) + len(DUP_OPEN)
    j = t.index(DUP_CLOSE, i)
    open(dst, "w").write(t[:i] + NODUP_BODY + t[j:])
    return dst


# ------------------------------------------------------- arena high-water ----
#: Five substitutions that turn `arm_safe_arena.rs` into a high-water probe:
#: a running `hw`, updated after every successful `NEW`; a print of it per
#: window; and a driver that sweeps EVERY window exactly once instead of the
#: shipped pseudo-random sampling -- which makes the bound stronger, not weaker.
#: Each is asserted to match exactly once.
HW_SUBS = [
    ("    let mut nfree: usize = ARENA;\n",
     "    let mut nfree: usize = ARENA;\n    let mut hw: usize = 0;\n"),
    ("                nnew = nnew + 1;\n",
     "                nnew = nnew + 1;\n"
     "                if ARENA - nfree > hw { hw = ARENA - nfree; }\n"),
    ("    acc.wrapping_mul(31).wrapping_add(nnew as u64)\n}",
     "    println!(\"HW {}\", hw);\n"
     "    acc.wrapping_mul(31).wrapping_add(nnew as u64)\n}"),
    ("        while it < n_iters {\n", "        while it < nwin {\n"),
    ("            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;\n",
     "            let k: usize = it as usize;\n"),
]


def make_hw_probe(src, dst):
    t = open(src).read()
    for old, new in HW_SUBS:
        if t.count(old) != 1:
            raise SystemExit(
                f"safe_arms.py: the arena high-water probe cannot be generated "
                f"-- {old.strip()[:60]!r} occurs {t.count(old)} times in {src}, "
                f"not once. The headroom claim in that file's header would then "
                f"be UNMEASURED, which is the defect TASK_156 repaired.")
        t = t.replace(old, new)
    open(dst, "w").write(t)
    return dst


def run(path, arg):
    r = sh([path, arg])
    return {"rc": r.returncode, "stdout": r.stdout.strip(),
            "stderr": r.stderr.strip()[:200]}


def build_c(kernel, tag):
    out = os.path.join(OUT, f"safearms-{tag}")
    cmd = [GCC, "-std=c99", "-Wall", "-Wextra", "-O3", "-g", "-DSLB_ISOLATED",
           "-I", COMMON, "-I", os.path.join(PDIR, "c"),
           os.path.join(COMMON, "driver.c"),
           os.path.join(PDIR, "c", kernel),
           os.path.join(PDIR, "c", "main.c"), "-o", out]
    r = sh(cmd)
    if r.returncode != 0:
        raise SystemExit(f"safe_arms.py: C build failed ({kernel}):\n"
                         f"{(r.stdout + r.stderr)[-2000:]}")
    return out


def reduced_input(name, iters):
    """A copy of an input with `n_iters` rewritten, for Miri -- which is ~1000x
    slower than native, so 200 000 iterations would never finish. Written under
    `.temp/` (`CLAUDE.md` rule 1)."""
    sys.path.insert(0, COMMON)
    import slb  # noqa: E402
    f = slb.read(os.path.join(INPUTS, name))
    out = os.path.join(OUT, f"miri-{iters}-{name}")
    slb.write(out, iters, f.payload[: f.declared_len], f.declared_len)
    return out


def miri(src, arg, sysroot):
    r = sh([MIRI_BIN, "--sysroot", sysroot, "--edition", "2021",
            "-Zmiri-disable-isolation", src, "--", arg])
    ub = "Undefined Behavior" in r.stderr or "error: unsupported" in r.stderr
    return {"rc": r.returncode, "stdout": r.stdout.strip(),
            "ub": ub,
            "stderr": re.sub(r"\s+", " ", r.stderr.strip())[:300]}


def miri_sysroot():
    r = sh([CARGO, "+nightly", "miri", "setup", "--print-sysroot"])
    return r.stdout.strip() if r.returncode == 0 else None


def derived_from():
    out = {}
    for rel in ("patterns/p34-refcount-stack/c/kernel.c",
                "patterns/p34-refcount-stack/c/kernel_hardened.c",
                "patterns/p34-refcount-stack/safe_naive.rs",
                "patterns/p34-refcount-stack/controls/arm_safe_arena.rs",
                "patterns/p34-refcount-stack/controls/arm_safe_rc_move.rs",
                "patterns/p34-refcount-stack/controls/arm_safe_rc_borrow.rs",
                "patterns/p34-refcount-stack/controls/arm_safe_rc_borrow_frozen.rs",
                "patterns/p34-refcount-stack/controls/safe_arms.py",
                "patterns/p34-refcount-stack/inputs/gen.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(GEN, exist_ok=True)
    sys.path.insert(0, PDIR)
    import model as M  # noqa: E402

    names = sorted(f for f in os.listdir(INPUTS)
                   if f.endswith(".bin") and not f.startswith("sweep-"))
    expect = {n: M.build(os.path.join(INPUTS, n)) for n in names}
    problems = []

    # ---- BRANCH A: is the bug expressible in safe Rust at all? ------------
    print("BRANCH A -- the `Rc` port: is the SEPARATION available?")
    compiles = {}
    for src, want_ok, want_code in (
            ("../safe_naive.rs", True, None),          # the sanity arm
            ("arm_safe_rc_move.rs", False, "E0507"),
            ("arm_safe_rc_borrow.rs", False, None)):
        path = os.path.normpath(os.path.join(HERE, src))
        tag = os.path.basename(src)[:-3]
        res = rustc(path, os.path.join(OUT, f"safearms-{tag}"))
        compiles[os.path.basename(src)] = res
        print(f"  {os.path.basename(src):24s} "
              f"{'COMPILES' if res['ok'] else 'REJECTED'} "
              f"{','.join(res['error_codes']) or '-':10s} "
              f"line {str(res['error_line'] or '-'):>4s}  "
              f"{res['first_error'][:60]}")
        if res["ok"] != want_ok:
            if want_ok:
                problems.append(
                    f"{src} did NOT compile, so the two must-fail arms below "
                    f"are not evidence about safe Rust -- the compiler or the "
                    f"command line is broken: {res['first_error']}")
            else:
                problems.append(
                    f"⚠⚠ {src} COMPILED. That REFUTES this row's safe-Rust "
                    f"finding: safe Rust would then offer the separation of "
                    f"*publish a reference* from *count it* that c/kernel.c's "
                    f"bug rests on. This is a louder result than the failure "
                    f"and belongs in NOTES.md before anything else.")
        if want_code and want_code not in res["error_codes"]:
            problems.append(
                f"{src} was rejected but not with {want_code}: "
                f"{res['error_codes']}. The arm may now be failing for a "
                f"scaffolding reason rather than for the reason it exists.")

    # ---- NEGATIVE CONTROLS: is the arm's error caused by the BUG? ---------
    # TASK_156, from TASK_155_REPORT B1. Without these, "it does not compile"
    # is not evidence about reference counting -- and on one of the two arms it
    # measurably is not.
    print("\nNEGATIVE CONTROLS -- a program that CANNOT have the bug must not "
          "print the same error")
    nc = {}
    NC_EXPECT = {
        # arm -> (twin must compile?, what the answer means)
        "arm_safe_rc_move.rs": (
            True,
            "the E0507 IS attributable to the DUP body: delete it and the same "
            "file compiles."),
        "arm_safe_rc_borrow.rs": (
            False,
            "the E0502 is NOT attributable to the DUP body -- it is raised on "
            "the NEW path (`objs.push` against live borrows) and survives the "
            "DUP body's deletion. That is this row's PUBLISHED reading of the "
            "arm, so a twin that started compiling would falsify it."),
    }
    for arm, (want_ok, meaning) in NC_EXPECT.items():
        twin = make_nodup(os.path.join(HERE, arm),
                          os.path.join(GEN, arm.replace(".rs", "_nodup.rs")))
        res = rustc(twin, os.path.join(OUT, "safearms-nodup"))
        same_line = (not res["ok"] and not compiles[arm]["ok"]
                     and res["error_line"] == compiles[arm]["error_line"]
                     and res["error_codes"] == compiles[arm]["error_codes"])
        nc[arm + " _nodup twin"] = dict(
            res, expected_ok=want_ok, as_expected=res["ok"] == want_ok,
            arm_error_line=compiles[arm]["error_line"],
            arm_error_codes=compiles[arm]["error_codes"],
            same_error_as_arm=same_line, meaning=meaning)
        print(f"  {arm + ' _nodup':32s} "
              f"{'COMPILES' if res['ok'] else 'REJECTED'} "
              f"{','.join(res['error_codes']) or '-':8s} "
              f"line {str(res['error_line'] or '-'):>4s}  "
              f"{'as expected' if res['ok'] == want_ok else '*** MOVED ***'}"
              f"{'  SAME ERROR AS THE ARM' if same_line else ''}")
        if res["ok"] != want_ok:
            problems.append(
                f"NEGATIVE CONTROL MOVED: {arm}'s `_nodup` twin -- the same "
                f"file with its whole DUP arm replaced by the SENT fold, a "
                f"program that CANNOT have p34's bug -- now "
                f"{'COMPILES' if res['ok'] else 'FAILS ' + str(res['error_codes'])}"
                f", and the row publishes the opposite. {meaning} Fix the "
                f"published reading in ../NOTES.md 8, ../spec.md's `why` and "
                f"{arm}'s header, not this assertion.")
        if not want_ok and not same_line:
            problems.append(
                f"{arm}'s `_nodup` twin still fails, but no longer with the "
                f"arm's own error ({res['error_codes']} at line "
                f"{res['error_line']} against the arm's "
                f"{compiles[arm]['error_codes']} at line "
                f"{compiles[arm]['error_line']}). The published reading -- that "
                f"this arm's error is raised on the NEW path and is unchanged "
                f"by deleting the DUP body -- rests on the two being the SAME "
                f"error at the SAME line.")

    frozen = rustc(os.path.join(HERE, "arm_safe_rc_borrow_frozen.rs"),
                   os.path.join(OUT, "safearms-frozen"))
    fout = (run(os.path.join(OUT, "safearms-frozen"), "")["stdout"]
            if frozen["ok"] else "")
    nc["arm_safe_rc_borrow_frozen.rs"] = dict(frozen, stdout=fout,
                                              expected_ok=True,
                                              expected_stdout="201")
    print(f"  {'arm_safe_rc_borrow_frozen.rs':32s} "
          f"{'COMPILES' if frozen['ok'] else 'REJECTED'} "
          f"{','.join(frozen['error_codes']) or '-':8s} stdout={fout!r}")
    if not frozen["ok"] or fout != "201":
        problems.append(
            f"⚠⚠ arm_safe_rc_borrow_frozen.rs did not compile-and-print `201` "
            f"({frozen['first_error'] or fout!r}). It stores a SECOND `&Obj` "
            f"into the stack array over a frozen owner, and the row's corrected "
            f"sentence -- *the borrow route is closed at the OWNER MUTATION, "
            f"not at the duplication* -- rests on it compiling. Until TASK_156 "
            f"spec.md's hashed `why` said the opposite (`a borrow cannot be "
            f"stored in the stack array`); do not restore that sentence, "
            f"re-derive this one.")

    # ---- the arena's headroom: MEASURED, not argued -----------------------
    print("\nARENA HIGH-WATER -- an instrumented copy of arm_safe_arena.rs, "
          "every window swept")
    hw = {}
    hwsrc = make_hw_probe(os.path.join(HERE, "arm_safe_arena.rs"),
                          os.path.join(GEN, "arm_arena_hw.rs"))
    hwres = rustc(hwsrc, os.path.join(OUT, "safearms-hw"))
    if not hwres["ok"]:
        problems.append(f"the arena high-water probe does not build "
                        f"({hwres['first_error']}), so ARENA's headroom is "
                        f"UNMEASURED and arm_safe_arena.rs's header claims a "
                        f"measurement that does not exist.")
    else:
        worst = 0
        for n in names:
            r = sh([os.path.join(OUT, "safearms-hw"), os.path.join(INPUTS, n)])
            marks = [int(x) for x in re.findall(r"^HW (\d+)$", r.stdout, re.M)]
            m = max(marks) if marks else 0
            worst = max(worst, m)
            hw[n] = {"windows": len(marks), "max_slots_in_use": m}
            print(f"  {n:28s} windows={len(marks):5d} "
                  f"max slots in use={m:3d}  of ARENA=32")
        hw["worst_case"] = worst
        hw["ARENA"] = 32
        hw["CAP"] = 16
        print(f"  worst case over every window of every input: {worst} of 32 "
              f"(= CAP), margin {32 - worst}")
        if worst >= 32:
            problems.append(
                f"the arena free list CAN underflow: {worst} of 32 slots in "
                f"use. arm_safe_arena.rs's headroom claim is false and the arm "
                f"would panic on some input.")

    # ---- BRANCH B: the index arena, two cells ----------------------------
    print("\nBRANCH B -- the INDEX-ARENA port: does it reproduce c/kernel.c?")
    arena = {}
    for tag, cfgs in (("arena_retain", ("slb_arm_retain",)), ("arena_bug", ())):
        res = rustc(os.path.join(HERE, "arm_safe_arena.rs"),
                    os.path.join(OUT, f"safearms-{tag}"), cfgs)
        if not res["ok"]:
            raise SystemExit(f"safe_arms.py: arena arm ({tag}) failed to "
                             f"build: {res['first_error']}")
        arena[tag] = os.path.join(OUT, f"safearms-{tag}")

    c_bug = build_c("kernel.c", "c-bug")
    c_fix = build_c("kernel_hardened.c", "c-fix")

    rows = {}
    print(f"  {'input':28s} {'arena_bug':>22s} {'c/kernel.c':>22s} "
          f"{'arena_retain':>22s} {'model':>22s}")
    for n in names:
        arg = os.path.join(INPUTS, n)
        ab = run(arena["arena_bug"], arg)["stdout"]
        ar = run(arena["arena_retain"], arg)["stdout"]
        cb = run(c_bug, arg)["stdout"]
        cf = run(c_fix, arg)["stdout"]
        mm = str(expect[n].checksum)
        rows[n] = {"arena_bug": ab, "arena_retain": ar, "c_kernel": cb,
                   "c_kernel_hardened": cf, "model": mm,
                   "arena_bug_eq_c_bug": ab == cb,
                   "arena_retain_eq_model": ar == mm,
                   "c_rungs_agree": cb == cf}
        print(f"  {n:28s} {ab:>22s} {cb:>22s} {ar:>22s} {mm:>22s}"
              f"  {'==' if ab == cb else 'DIFFERS'}")
        if ab != cb:
            problems.append(
                f"{n}: the safe index-arena arm ({ab}) does NOT reproduce "
                f"c/kernel.c ({cb}). Branch B of the law is what this file "
                f"exists to measure, so a mismatch either retracts it or means "
                f"the arena's free list has stopped matching glibc's tcache "
                f"discipline (LIFO).")
        if ar != mm:
            problems.append(
                f"{n}: the safe index-arena arm WITH the retain ({ar}) does "
                f"not equal model.py ({mm}), so the arena port is not a "
                f"faithful port and branch B's agreement means nothing.")

    # ---- Miri on the arena arm: the detector-coverage half ----------------
    print("\nMiri on the ARENA arm -- the p32 half of the coverage result")
    mir = {}
    sysroot = miri_sysroot()
    if not sysroot or not os.path.exists(MIRI_BIN):
        mir["blocked"] = ("miri sysroot unavailable; see TOOLCHAIN.md. The "
                          "arena arm's Miri row is blocked, not failed.")
        print(f"  {mir['blocked']}")
    else:
        for n in names:
            arg = reduced_input(n, MIRI_ITERS)
            m = miri(os.path.join(HERE, "arm_safe_arena.rs"), arg, sysroot)
            mir[n] = m
            print(f"  {n:28s} rc={m['rc']:<4d} "
                  f"{'UB REPORTED' if m['ub'] else 'no UB'}  "
                  f"stdout={m['stdout'][:22]}")
            if m["ub"]:
                problems.append(
                    f"miri/{n}: the SAFE arena arm reported Undefined "
                    f"Behaviour. It is `#![forbid(unsafe_code)]`, so this "
                    f"would be a Miri or toolchain problem rather than a "
                    f"pattern one: {m['stderr']}")

    doc = {"pin": {"regenerate": "python3 patterns/p34-refcount-stack/controls/"
                                 "safe_arms.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "branch_a_compiles": compiles,
           "negative_controls": nc,
           "arena_high_water": hw,
           "branch_b_checksums": rows,
           "miri_iters": MIRI_ITERS,
           "miri": mir,
           "problems": problems,
           "invariant": "Branch A: the two safe-Rust attempts to publish a "
                        "second reference without counting it do NOT compile, "
                        "while the shipped safe_naive.rs on the same command "
                        "line does. NEGATIVE CONTROLS (TASK_156): the "
                        "attribution is measured rather than assumed -- "
                        "arm_safe_rc_move.rs's `_nodup` twin COMPILES, so its "
                        "E0507 is caused by the DUP body; "
                        "arm_safe_rc_borrow.rs's twin FAILS identically, so "
                        "that arm's E0502 is about mutating the owner and NOT "
                        "about duplicating a borrow; and "
                        "arm_safe_rc_borrow_frozen.rs stores a second &Obj in "
                        "the stack array over a frozen owner and COMPILES. The "
                        "arena high-water mark is MEASURED at 16 of 32. "
                        "Branch B: the safe INDEX-ARENA arm without "
                        "the retain reproduces c/kernel.c bit for bit on every "
                        "input, and with the retain it equals model.py. Both "
                        "branches of .memory/01-ladder.md's temporal law, in "
                        "one row, selected by the port."}
    out = os.path.join(HERE, "safe_arms.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
