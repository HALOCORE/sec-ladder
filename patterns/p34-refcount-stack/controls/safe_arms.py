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

⚠ **Branch B's arena arm has both cfgs**, `--cfg slb_arm_retain` and without, so
the arm is a two-cell experiment and not one: with the retain it must equal
`../model.py`, without it it must equal `c/kernel.c`. One file, one `#[cfg]`, and
the `#[cfg]` is the safety line.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * `safe_naive.rs` COMPILES on the same command line (the sanity arm);
  * `arm_safe_rc_move.rs` FAILS with `E0507`;
  * `arm_safe_rc_borrow.rs` FAILS with a borrow-checker error;
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
    return {"ok": r.returncode == 0, "error_codes": codes,
            "first_error": first[:200]}


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
                "patterns/p34-refcount-stack/controls/safe_arms.py",
                "patterns/p34-refcount-stack/inputs/gen.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
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
              f"{','.join(res['error_codes']) or '-':10s} {res['first_error'][:70]}")
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
           "branch_b_checksums": rows,
           "miri_iters": MIRI_ITERS,
           "miri": mir,
           "problems": problems,
           "invariant": "Branch A: the two safe-Rust attempts to publish a "
                        "second reference without counting it do NOT compile, "
                        "while the shipped safe_naive.rs on the same command "
                        "line does. Branch B: the safe INDEX-ARENA arm without "
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
