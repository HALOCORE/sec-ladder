#!/usr/bin/env python3
"""p35 CONTROLS: **can RUST reproduce `c/kernel.c`'s bug, and does any
Rust-side instrument see it?**

    python3 patterns/p35-tagged-union/controls/rust_bug.py

The two arms beside this file are `c/kernel.c`'s ordering written in Rust:

    controls/arm_unsafe_bug.rs   a real `union`, `unsafe` reads, buggy order
    controls/arm_safe_bug.rs     `#![forbid(unsafe_code)]`, a tag array beside
                                 a `u64` payload array, `f64::from_bits` for
                                 the reinterpretation, buggy order

and the SHIPPED safe rungs are the third cell of the experiment: they hold a
`Cell` ENUM, where the mismatch is **unrepresentable** and no arm can be
written at all.

WHAT IS MEASURED, per input, against the C rung's own output
------------------------------------------------------------
  * does the arm reproduce `c/kernel.c`'s answer EXACTLY?
  * what does the arm do -- exit code, panic, signal?
  * what does **Miri** say about the unsafe arm?

⚠⚠ **THE EXPECTED SHAPE, and every cell of it is asserted below.**

    input                     C R1        unsafe arm            safe arm
    ----------------------------------------------------------------------
    benign (small/large)      correct     == C, Miri clean      == C
    adversarial-dbl-*         silent      == C bit for bit,     == C bit for
                              wrong       Miri CLEAN            bit
    adversarial-exhaust       silent      == C bit for bit,     == C bit for
                              wrong       Miri REPORTS IT       bit
    adversarial-ptr-*         SIGSEGV     OOB `get_unchecked`,  PANIC, index
                                          Miri REPORTS it       out of bounds

**Three findings live in that table.** (1) Reading a union member other than the
one last stored is NOT undefined behaviour in Rust when the bytes are a valid
value of the field's type **and were all written**, so the SILENT harm survives
into `unsafe` Rust with Miri saying nothing -- and survives into SAFE Rust too,
through `from_bits`, which is exactly why `../spec.md` forbids that spelling in
a rung. (2) The LOUD harm does NOT survive, and the reason is the
OFFSET-for-POINTER substitution `../spec.md` documents: what follows the
confused read is an out-of-bounds index rather than a wild pointer, which Miri
catches in the unsafe arm and the bounds check catches in the safe one.

⚠⚠ **(3) ADDED AT TASK_153, AND IT NARROWS (1). VALIDITY IS NOT THE WHOLE
CONDITION -- INITIALISEDNESS IS THE OTHER HALF, AND THIS ORDERING REACHES IT ON
A SHIPPED INPUT.** `adversarial-exhaust.bin` produces `tag DBL over a cell whose
live member is PTR`. In **C** that is another 8-byte-over-8-byte
reinterpretation and is silent, because `uint8_t *` is 8 bytes and C's union has
no narrow member. In the **Rust** arms it is not: they carry `o: u32` instead of
a pointer -- `../spec.md`'s disclosed substitution -- so `pays[idx].d` reads 8
bytes where 4 were written, and **Miri reports `reading memory ... but memory is
uninitialized`**. ⚠ The NATIVE run still reproduces C bit for bit
(`1705852038987163136`), because the bytes left in the slot are the previous
`Pay { i: .. }` initialiser's, which is exactly what C's stale union holds. **So
the substitution changes which instrument fires on the SILENT harm too, and not
only on the loud one** -- and this control did not see it until TASK_153,
because it ran Miri on the DBL and PTR inputs only.

⚠ Miri runs with a REDUCED `n_iters` (the file's header is rewritten in a
scratch copy) because Miri is an interpreter; the checksum then differs from the
native one by construction and is compared against a native run of the SAME
reduced input, never against the shipped one.
"""

import collections
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
COMMON = os.path.join(REPO, "common")
INPUTS = os.path.join(PDIR, "inputs")
OUT = os.path.join(REPO, ".temp", "p35ctl", "rustbug")

RUSTC = os.environ.get("SLB_RUSTC", os.path.expanduser("~/.cargo/bin/rustc"))
CARGO = os.environ.get("SLB_CARGO", os.path.expanduser("~/.cargo/bin/cargo"))
NIGHTLY = os.environ.get("SLB_NIGHTLY",
                         "nightly-x86_64-unknown-linux-gnu")
MIRI_BIN = os.path.expanduser(f"~/.rustup/toolchains/{NIGHTLY}/bin/miri")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")

MIRI_ITERS = 4
NAMES = ("small.bin", "adversarial-dbl-confusion.bin",
         "adversarial-exhaust.bin", "adversarial-ptr-confusion.bin",
         "adversarial-ptr-deep.bin")

#: The two inputs that reach the LOUD harm.
PTR_NAMES = ("adversarial-ptr-confusion.bin", "adversarial-ptr-deep.bin")

SIGSEGV, SIGBUS = -11, -7

#: ⚠⚠ THE UNSAFE ARM'S SIGNAL IS A DRAW, NOT A CONSTANT (TASK_170 items H /
#: RECAP queue items 39 and 41; measured at TASK_168).
#:
#: This control RECORDED `unsafe_reproduces_c` for these two inputs and NEVER
#: ASSERTED it -- `.memory/03-measurement.md` entry 19's family: a control that
#: records a claim it does not check. Meanwhile FIVE documents, one of them a
#: `contract_sha256`-hashed `why`, asserted a single `rc=-11` *"exactly as
#: c/kernel.c does"*, and the committed sidecar said `rc=-7,
#: unsafe_reproduces_c: false` on one of them. That contradiction shipped.
#:
#: ⚠ **THE HONEST FIX IS NOT TO RE-ROLL FOR THE PUBLISHED DRAW.** It is to
#: measure the distribution and assert what is actually invariant. Both signals
#: mean the same thing about the ROW -- the wrong-variant read produces an
#: out-of-bounds `get_unchecked` whose address is unmapped -- and WHICH one the
#: kernel delivers depends on where the faulting address lands relative to the
#: mapping, which ASLR re-rolls per process. C is deterministic here because
#: its wild pointer is an attacker-derived INTEGER and lands in the same place
#: every run; the Rust arm's is an arena-relative OFFSET, which is the
#: disclosed `*p` -> `arena[o]` substitution `../spec.md` documents. **So the
#: stochasticity is a consequence of the substitution, not noise.**
#:
#: ⚠ **THE STATED TOLERANCE.** Asserted per draw: the arm dies on a SIGNAL, and
#: the signal is one of the two. Asserted over the draws: the SIGSEGV share
#: clears `SIGSEGV_FLOOR`. The floor is 0.50 against a measured ~0.93 -- loose
#: on purpose, because this control must fail on *"the arm stopped crashing"*
#: and must NOT fail on a different machine's ASLR landing the other way more
#: often. A tight band would be a re-roll dressed as an assertion.
SIGNAL_DRAWS = 40
SIGSEGV_FLOOR = 0.50



def mask(txt):
    """Strip everything from a diagnostic that is not evidence.

    ⚠ A committed file that cites an absolute `.temp/` path costs the manager a
    `harness/tools/temp_citations.py` baseline entry for a file a fresh clone
    will not have, and that tool reads `git ls-files`, so the cost only shows
    up after the commit. ASan pids and pointer values are pure churn for the
    same reason `p23`'s `controls.log` is declared un-hashable
    (`.memory/05-layout.md`). The DIAGNOSTIC TEXT is what this control is
    evidence for; the path, the pid and the address are not."""
    txt = re.sub(re.escape(REPO) + r"/\.temp/\S*", "<scratch>", txt)
    txt = txt.replace(REPO + "/", "")
    txt = re.sub(r"==\d+==", "==<pid>==", txt)
    txt = re.sub(r"0x[0-9a-f]{6,}", "0x<addr>", txt)
    return txt

def sh(cmd, timeout=1800, env_extra=None):
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(cmd, capture_output=True, text=True, env=env,
                          timeout=timeout, cwd=REPO)


def build_rust(src, out, extra=()):
    r = sh([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
            "-C", "opt-level=3", "-C", "debug-assertions=off",
            *extra, os.path.join(HERE, src), "-o", out])
    if r.returncode != 0:
        raise SystemExit(f"rust_bug.py: build failed for {src}:\n"
                         f"{(r.stdout + r.stderr)[-2000:]}")
    return out


def build_c():
    out = os.path.join(OUT, "c-r1")
    r = sh([GCC, "-std=c99", "-Wall", "-Wextra", "-O3", "-DSLB_ISOLATED",
            "-I", COMMON, "-I", os.path.join(PDIR, "c"),
            os.path.join(COMMON, "driver.c"),
            os.path.join(PDIR, "c", "kernel.c"),
            os.path.join(PDIR, "c", "main.c"), "-o", out])
    if r.returncode != 0:
        raise SystemExit(f"rust_bug.py: C build failed:\n"
                         f"{(r.stdout + r.stderr)[-2000:]}")
    return out


def run(path, arg):
    r = sh([path, arg], timeout=600)
    return {"rc": r.returncode, "stdout": r.stdout.strip(),
            "stderr": mask(re.sub(r"\s+", " ", r.stderr.strip()))[:200]}


def reduced_input(name, n_iters):
    """A copy of the input whose `n_iters` header word is `n_iters`."""
    src = os.path.join(INPUTS, name)
    dst = os.path.join(OUT, f"mini-{name}")
    blob = open(src, "rb").read()
    open(dst, "wb").write(struct.pack("<Q", n_iters) + blob[8:])
    return dst


def miri(src, arg, sysroot):
    """Miri on one control arm, with **the same command line
    `harness/check.py`'s stage 8 uses** (`check.py::check_miri`): the binary from the
    pinned nightly, `--sysroot`, `--edition 2021`, `-Zmiri-disable-isolation`,
    the source, `--`, and the program's argument. ⚠ The `--` is load-bearing:
    without it Miri reads the input path as a second input FILENAME and exits 1
    with `multiple input filenames provided`, which is not a UB verdict and
    must never be read as one."""
    r = sh([MIRI_BIN, "--sysroot", sysroot, "--edition", "2021",
            "-Zmiri-disable-isolation", os.path.join(HERE, src), "--", arg],
           timeout=3600)
    txt = r.stdout + r.stderr
    return {"rc": r.returncode, "stdout": r.stdout.strip(),
            "ub": "Undefined Behavior" in txt,
            "ran": "multiple input filenames" not in txt,
            "diagnostic": mask(re.sub(r"\s+", " ", r.stderr.strip()))[:400]}


def miri_sysroot():
    r = sh([CARGO, "+nightly", "miri", "setup", "--print-sysroot"],
           timeout=1800)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def derived_from():
    out = {}
    for rel in ("patterns/p35-tagged-union/c/kernel.c",
                "patterns/p35-tagged-union/c/kernel.h",
                "patterns/p35-tagged-union/c/main.c",
                "patterns/p35-tagged-union/controls/arm_unsafe_bug.rs",
                "patterns/p35-tagged-union/controls/arm_safe_bug.rs",
                "patterns/p35-tagged-union/controls/rust_bug.py",
                "patterns/p35-tagged-union/inputs/gen.py",
                "common/driver.rs", "common/driver.c"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)

    cbin = build_c()
    ubin = build_rust("arm_unsafe_bug.rs", os.path.join(OUT, "arm-unsafe"))
    sbin = build_rust("arm_safe_bug.rs", os.path.join(OUT, "arm-safe"))

    rows, problems = {}, []
    print(f"{'input':32s} {'C R1':>22s} {'unsafe arm':>22s} {'safe arm':>22s}")
    for n in NAMES:
        arg = os.path.join(INPUTS, n)
        c = run(cbin, arg)
        u = run(ubin, arg)
        s = run(sbin, arg)
        rows[n] = {"c_r1": c, "unsafe_arm": u, "safe_arm": s,
                   "unsafe_reproduces_c": u["stdout"] == c["stdout"]
                   and u["rc"] == c["rc"],
                   "safe_reproduces_c": s["stdout"] == c["stdout"]
                   and s["rc"] == c["rc"]}
        print(f"{n:32s} {(c['stdout'] or 'rc=%d' % c['rc']):>22s} "
              f"{(u['stdout'] or 'rc=%d' % u['rc']):>22s} "
              f"{(s['stdout'] or 'rc=%d' % s['rc']):>22s}")

    # ---- the assertions ---------------------------------------------------
    for n in ("small.bin", "adversarial-dbl-confusion.bin",
              "adversarial-exhaust.bin"):
        if not rows[n]["unsafe_reproduces_c"]:
            problems.append(f"{n}: the UNSAFE arm does not reproduce C's "
                            f"answer ({rows[n]['unsafe_arm']['stdout']!r} vs "
                            f"{rows[n]['c_r1']['stdout']!r}) -- the union "
                            f"punning was supposed to be the same "
                            f"reinterpretation of the same bytes")
        if not rows[n]["safe_reproduces_c"]:
            problems.append(f"{n}: the SAFE arm does not reproduce C's answer "
                            f"({rows[n]['safe_arm']['stdout']!r} vs "
                            f"{rows[n]['c_r1']['stdout']!r}) -- `from_bits` was "
                            f"supposed to be the same total reinterpretation")
    for n in ("adversarial-ptr-confusion.bin", "adversarial-ptr-deep.bin"):
        if rows[n]["c_r1"]["rc"] >= 0:
            problems.append(f"{n}: C R1 did not die on a signal (rc="
                            f"{rows[n]['c_r1']['rc']}), so the LOUD harm is not "
                            f"being exercised")
        if rows[n]["safe_arm"]["rc"] == 0:
            problems.append(f"{n}: the SAFE arm exited 0 -- it was expected to "
                            f"PANIC on the bounds check that replaces C's wild "
                            f"dereference")
        if rows[n]["safe_reproduces_c"]:
            problems.append(f"{n}: the SAFE arm reproduced C's behaviour, which "
                            f"contradicts this control's own claim that the "
                            f"LOUD harm does not survive into Rust")

    # ---- the SIGNAL is a DRAW, and it is now ASSERTED (TASK_170 item H) -----
    # ⚠ The single-draw rows above are LEFT AS THEY FELL: `unsafe_arm.rc` is one
    # sample and this block is what says so. Re-running until it read -11 would
    # be the dishonest fix (RECAP item 39: *"the engineer kept the honest draw
    # rather than re-rolling for the published one, and that is the right
    # call"*).
    draws = {}
    for n in PTR_NAMES:
        arg = os.path.join(INPUTS, n)
        cs, us = collections.Counter(), collections.Counter()
        for _ in range(SIGNAL_DRAWS):
            cs[run(cbin, arg)["rc"]] += 1
            us[run(ubin, arg)["rc"]] += 1
        share = us[SIGSEGV] / SIGNAL_DRAWS
        draws[n] = {"draws": SIGNAL_DRAWS,
                    "c_r1_rc": {str(k): v for k, v in sorted(cs.items())},
                    "unsafe_arm_rc": {str(k): v for k, v in sorted(us.items())},
                    "unsafe_sigsegv_share": share,
                    "unsafe_died_on_a_signal": all(k < 0 for k in us)}
        print(f"  {n:32s} {SIGNAL_DRAWS} draws   C {dict(cs)}   "
              f"unsafe {dict(us)}   SIGSEGV share {share:.3f}")
        # (a) C is DETERMINISTIC -- the control the stochastic claim needs.
        if set(cs) != {SIGSEGV}:
            problems.append(
                f"{n}: C R1 is NOT 40/40 SIGSEGV over {SIGNAL_DRAWS} draws "
                f"({dict(cs)}). The claim that the RUST arm's signal is the "
                f"stochastic one depends on C's being fixed; without this, "
                f"`{n}`'s row says nothing about the substitution.")
        # (b) the arm always dies LOUDLY -- the invariant that is actually true.
        if not draws[n]["unsafe_died_on_a_signal"]:
            problems.append(
                f"{n}: the UNSAFE arm did not die on a signal in "
                f"{SIGNAL_DRAWS - sum(v for k, v in us.items() if k < 0)} of "
                f"{SIGNAL_DRAWS} draws ({dict(us)}). The LOUD harm is supposed "
                f"to survive into unsafe Rust as a CRASH -- what the "
                f"substitution changes is the CLASS, not the presence.")
        # (c) and only in the two ways the mechanism allows.
        bad = {k: v for k, v in us.items() if k not in (SIGSEGV, SIGBUS)}
        if bad:
            problems.append(
                f"{n}: the UNSAFE arm produced an unexpected exit state {bad}. "
                f"Only SIGSEGV ({SIGSEGV}) and SIGBUS ({SIGBUS}) are accounted "
                f"for by an unmapped-address fault; anything else is a "
                f"different failure and must be read before it is blessed.")
        # (d) the STATED TOLERANCE. See SIGSEGV_FLOOR's comment for why it is
        #     this loose and what a tight band would actually be measuring.
        if share < SIGSEGV_FLOOR:
            problems.append(
                f"{n}: SIGSEGV share {share:.3f} is below SIGSEGV_FLOOR "
                f"{SIGSEGV_FLOOR}. Measured ~0.93 at TASK_168 and TASK_170. "
                f"This is a TOLERANCE, not a fingerprint: read the "
                f"distribution before changing either number.")

    # ---- Miri, on the unsafe arm ------------------------------------------
    sysroot = miri_sysroot()
    mir = {}
    if not sysroot:
        mir["blocked"] = ("miri sysroot unavailable; see TOOLCHAIN.md. The "
                          "Miri half of this control is BLOCKED, not failed.")
        print("\nMiri: BLOCKED (no sysroot)")
    else:
        print("\nMiri on arm_unsafe_bug.rs "
              f"(n_iters reduced to {MIRI_ITERS}):")
        for n in ("adversarial-dbl-confusion.bin",
                  "adversarial-exhaust.bin",
                  "adversarial-ptr-confusion.bin"):
            m = miri("arm_unsafe_bug.rs", reduced_input(n, MIRI_ITERS), sysroot)
            mir[n] = m
            print(f"  {n:32s} rc={m['rc']:<5d} UB={m['ub']}  "
                  f"{m['diagnostic'][:80]}")
        for n, m in mir.items():
            if isinstance(m, dict) and not m.get("ran", True):
                problems.append(
                    f"Miri never ran on {n}: {m['diagnostic'][:120]}. A Miri "
                    f"that did not start says nothing about UB, and this "
                    f"control's whole point is that a SILENCE is "
                    f"interpretable.")
        if mir.get("adversarial-dbl-confusion.bin", {}).get("ub"):
            problems.append(
                "Miri reported UB on the DBL confusion. This control's claim is "
                "that a wrong-variant union READ is not UB in Rust when the "
                "bytes read are a valid value of the field's type AND WERE ALL "
                "WRITTEN -- read the diagnostic before believing either half.")
        # ⚠ ADDED AT TASK_153. `adversarial-exhaust.bin` reaches the OTHER
        # confusion this ordering produces -- tag DBL over a cell whose live
        # member is `o: u32` -- and that reads 8 bytes where 4 were written.
        # VALIDITY is satisfied (every bit pattern is a valid f64);
        # INITIALISEDNESS is not, and Miri reports it. This is the must-fire
        # arm for the initialisedness half of the claim, and it is the arm the
        # first version of this control did not have: it ran Miri on the DBL
        # and PTR inputs only, so the one input that could refute the
        # generalisation was the one input Miri never saw.
        if not mir.get("adversarial-exhaust.bin", {}).get("ub"):
            problems.append(
                "Miri did NOT report UB on adversarial-exhaust, where the arm "
                "reads `pays[idx].d` (8 bytes) from a cell whose live member is "
                "`o: u32` (4 bytes). Without this firing, the DBL row's silence "
                "cannot be read as `validity is the whole condition` -- it "
                "would be indistinguishable from Miri not modelling union "
                "initialisedness at all.")
        if not mir.get("adversarial-ptr-confusion.bin", {}).get("ub"):
            problems.append(
                "Miri did NOT report UB on the PTR confusion, where the arm "
                "does an out-of-bounds `get_unchecked` into a 4-byte array. "
                "That is a must-fire arm for the Miri half of this control: "
                "without it, the DBL row's silence is uninterpretable.")

    doc = {"pin": {"regenerate": "python3 patterns/p35-tagged-union/controls/"
                                 "rust_bug.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "miri_iters": MIRI_ITERS,
           "native": rows,
           "signal_draws": draws,
           "signal_draws_note":
               "TASK_170 item H. `native.<ptr input>.unsafe_arm.rc` above is "
               "ONE DRAW and must not be quoted as a constant: the unsafe "
               "arm's signal is stochastic, SIGSEGV (-11) most of the time and "
               "SIGBUS (-7) otherwise, while C is deterministic SIGSEGV. The "
               "mechanism is `../spec.md`'s disclosed `*p` -> `arena[o]` "
               "substitution -- C dereferences an attacker-derived INTEGER "
               "that lands in the same place every run, the Rust arm indexes "
               "an ARENA-RELATIVE offset whose faulting address moves with "
               "ASLR. `unsafe_reproduces_c` is therefore FALSE on a draw that "
               "came up SIGBUS, and that is NOT a defect: what is asserted is "
               "that the arm dies on a signal, that the signal is one of those "
               "two, and that the SIGSEGV share clears SIGSEGV_FLOOR.",
           "miri": mir,
           "problems": problems,
           "invariant": "Both Rust arms reproduce c/kernel.c's SILENT wrong "
                        "value bit for bit, on EVERY silent input including "
                        "adversarial-exhaust. Miri is silent on the DBL "
                        "confusion -- a wrong-variant union read whose bytes "
                        "were all written is not UB in Rust -- and REPORTS the "
                        "exhaust one, where the read is 8 bytes wide over a "
                        "4-byte `o: u32` payload, so the condition is validity "
                        "AND initialisedness. Neither arm reproduces the LOUD "
                        "harm: the unsafe arm turns it into an out-of-bounds "
                        "`get_unchecked` that Miri DOES report, and the safe "
                        "arm turns it into a panic. The two firing rows are the "
                        "must-fire arms for the one silent row. The shipped "
                        "safe rungs cannot express any of it, because their "
                        "`Cell` enum makes the mismatch unrepresentable."}
    out = os.path.join(HERE, "rust_bug.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
