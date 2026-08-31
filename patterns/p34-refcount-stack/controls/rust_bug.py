#!/usr/bin/env python3
"""p34 CONTROLS: **the MUST-FIRE arm for the Miri row, and what the UNSAFE Rust
port does with the safety line deleted.**

    python3 patterns/p34-refcount-stack/controls/rust_bug.py

WHY THIS EXISTS
---------------
`../spec.md`'s `miri.reason` publishes a claim about SILENCE: what Miri finds on
the shipped `unsafe.rs` is NOTHING, on every input including all five adversarial
ones. `.memory/03-measurement.md` entry 14 and RECAP trap 5: a detector that says
nothing looks exactly like a detector that is not running, so a silence claim
owes a control that can break it.

`arm_unsafe_bug.rs` is that control -- **`unsafe.rs` with `obj_retain(t);`
deleted from the DUP arm and nothing else**, which is exactly the line
`c/kernel.c` omits. Miri MUST report Undefined Behaviour on it, on the inputs
whose windows execute a DUP.

⚠⚠ **THE ARM IS RE-DERIVED FROM THE RUNG AT EVERY RUN.** `p35` ships its
equivalent as a hand-maintained copy; this file instead reads both sources,
deletes the retain from `unsafe.rs`, normalises the two differences that a
control in `controls/` must have -- its own `//!` header and one more `../` in
the `#[path]` -- and requires the result to equal `arm_unsafe_bug.rs` **exactly**.
So the two cannot drift, and an edit to the rung that is not mirrored here FAILS
this control instead of quietly turning it into a test of something else.

WHAT ELSE IT MEASURES, and it is a result rather than scaffolding
----------------------------------------------------------------
The bug arm's CHECKSUMS are compared to `c/kernel.c`'s on every input.
**Unsafe Rust with the retain deleted reproduces the buggy C bit for bit**,
including on the recycle-divergent input -- which is what says the Rust port is
faithful and that the divergence is the allocator's LIFO recycling rather than
anything about C.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * `arm_unsafe_bug.rs` is `unsafe.rs` minus exactly the retain (re-derived);
  * the bug arm's checksum equals `c/kernel.c`'s on every input;
  * Miri REPORTS Undefined Behaviour on the bug arm for every input `model.py`
    derives as `sanitizer_expect: fires`;
  * Miri is SILENT on the bug arm for every input derived as `clean` -- so the
    firing is caused by the DUP and not by the arm being a control;
  * Miri is SILENT on the SHIPPED `unsafe.rs` on every input, which is what
    `../spec.md`'s `miri.reason` claims.
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

#: The retain, exactly as `unsafe.rs` writes it, and the comment line the arm
#: leaves in its place so the deletion is visible where it happened.
RETAIN = ("                // THE LINE THE C RUNG FORGOT.\n"
          "                obj_retain(t);\n")
RETAIN_GONE = "                // THE LINE THE C RUNG FORGOT -- DELETED IN THIS ARM.\n"


def sh(cmd, **kw):
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    return subprocess.run(cmd, capture_output=True, text=True, env=env,
                          timeout=1800, **kw)


def strip_header(text):
    """Everything below the leading `//!` block."""
    lines = text.split("\n")
    i = 0
    while i < len(lines) and lines[i].startswith("//!"):
        i += 1
    return "\n".join(lines[i:])


def derivation_problem():
    """Re-derive the arm from the rung. Returns a message or None."""
    rung = strip_header(open(os.path.join(PDIR, "unsafe.rs")).read())
    arm = strip_header(open(os.path.join(HERE, "arm_unsafe_bug.rs")).read())
    if RETAIN not in rung:
        return ("unsafe.rs no longer contains the retain in the exact spelling "
                "this control deletes, so the arm cannot be re-derived and the "
                "Miri must-fire row is not evidence about the shipped rung")
    want = rung.replace(RETAIN, RETAIN_GONE)
    # The one legitimate difference: a control sits one directory deeper.
    want = want.replace('#[path = "../../common/driver.rs"]',
                        '#[path = "../../../common/driver.rs"]')
    if want != arm:
        d = [i for i, (x, y) in enumerate(zip(want.split("\n"),
                                              arm.split("\n"))) if x != y]
        return (f"arm_unsafe_bug.rs is NOT unsafe.rs minus the retain: they "
                f"differ at {len(d)} line(s), first at index "
                f"{d[0] if d else 'EOF'}. Mirror the rung edit into the arm, or "
                f"this control is testing a file nobody ships.")
    return None


def rustc(src, out):
    r = sh([RUSTC] + RFLAGS + [src, "-o", out])
    if r.returncode != 0:
        raise SystemExit(f"rust_bug.py: build failed on {src}:\n"
                         f"{(r.stdout + r.stderr)[-2000:]}")
    return out


def build_c(kernel, tag):
    out = os.path.join(OUT, f"rustbug-{tag}")
    cmd = [GCC, "-std=c99", "-Wall", "-Wextra", "-O3", "-g", "-DSLB_ISOLATED",
           "-I", COMMON, "-I", os.path.join(PDIR, "c"),
           os.path.join(COMMON, "driver.c"),
           os.path.join(PDIR, "c", kernel),
           os.path.join(PDIR, "c", "main.c"), "-o", out]
    r = sh(cmd)
    if r.returncode != 0:
        raise SystemExit(f"rust_bug.py: C build failed ({kernel}):\n"
                         f"{(r.stdout + r.stderr)[-2000:]}")
    return out


def run(path, arg):
    r = sh([path, arg])
    return {"rc": r.returncode, "stdout": r.stdout.strip()}


def reduced_input(name, iters):
    sys.path.insert(0, COMMON)
    import slb  # noqa: E402
    f = slb.read(os.path.join(INPUTS, name))
    out = os.path.join(OUT, f"miri-{iters}-{name}")
    slb.write(out, iters, f.payload[: f.declared_len], f.declared_len)
    return out


def miri(src, arg, sysroot):
    r = sh([MIRI_BIN, "--sysroot", sysroot, "--edition", "2021",
            "-Zmiri-disable-isolation", src, "--", arg])
    txt = r.stderr
    ub = "Undefined Behavior" in txt
    kind = ""
    m = re.search(r"error: Undefined Behavior: ([^\n]{0,120})", txt)
    if m:
        kind = m.group(1).strip()
    return {"rc": r.returncode, "stdout": r.stdout.strip(), "ub": ub,
            "kind": kind,
            "stderr": re.sub(r"\s+", " ", txt.strip())[:300]}


def miri_sysroot():
    r = sh([CARGO, "+nightly", "miri", "setup", "--print-sysroot"])
    return r.stdout.strip() if r.returncode == 0 else None


def derived_from():
    out = {}
    for rel in ("patterns/p34-refcount-stack/unsafe.rs",
                "patterns/p34-refcount-stack/c/kernel.c",
                "patterns/p34-refcount-stack/controls/arm_unsafe_bug.rs",
                "patterns/p34-refcount-stack/controls/rust_bug.py",
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

    print("DERIVATION -- is the arm the rung minus exactly the retain?")
    dp = derivation_problem()
    print(f"  {'OK' if dp is None else 'BROKEN'}: "
          f"{dp or 'arm_unsafe_bug.rs == unsafe.rs with obj_retain(t); deleted'}")
    if dp:
        problems.append(dp)

    bug = rustc(os.path.join(HERE, "arm_unsafe_bug.rs"),
                os.path.join(OUT, "rustbug-arm"))
    c_bug = build_c("kernel.c", "c-bug")

    print("\nCHECKSUMS -- does UNSAFE Rust with the retain deleted reproduce C?")
    rows = {}
    for n in names:
        arg = os.path.join(INPUTS, n)
        rb = run(bug, arg)["stdout"]
        cb = run(c_bug, arg)["stdout"]
        rows[n] = {"arm_unsafe_bug": rb, "c_kernel": cb, "equal": rb == cb,
                   "model": str(expect[n].checksum)}
        print(f"  {n:28s} arm={rb:>22s} c/kernel.c={cb:>22s} "
              f"{'==' if rb == cb else 'DIFFERS'}")
        if rb != cb:
            problems.append(
                f"{n}: the unsafe Rust bug arm ({rb}) does not reproduce "
                f"c/kernel.c ({cb}), so the Rust port is not faithful to the C "
                f"one on the buggy path")

    print("\nMIRI -- the must-fire arm and the shipped rung's silence")
    mir = {}
    sysroot = miri_sysroot()
    if not sysroot or not os.path.exists(MIRI_BIN):
        mir["blocked"] = ("miri sysroot unavailable; see TOOLCHAIN.md. This row "
                          "is blocked, not failed.")
        print(f"  {mir['blocked']}")
        problems.append("miri unavailable: the Miri silence claim in "
                        "../spec.md is UNSUPPORTED by this run")
    else:
        for src, tag in (("arm_unsafe_bug.rs", "bug"), ("../unsafe.rs", "ship")):
            path = os.path.normpath(os.path.join(HERE, src))
            for n in names:
                arg = reduced_input(n, MIRI_ITERS)
                m = miri(path, arg, sysroot)
                mir[f"{tag}/{n}"] = m
                print(f"  {tag:5s} {n:28s} rc={m['rc']:<4d} "
                      f"{'UB: ' + m['kind'][:40] if m['ub'] else 'no UB'}")
                fires = expect[n].sanitizer_expect == "fires"
                if tag == "bug" and fires and not m["ub"]:
                    problems.append(
                        f"MUST-FIRE ARM DEAD: miri found no UB in "
                        f"arm_unsafe_bug.rs on {n}, which model.py derives as "
                        f"`fires`. ../spec.md's claim that Miri is silent on "
                        f"the SHIPPED rung is then unsupported -- a silent "
                        f"detector and an absent one are indistinguishable.")
                if tag == "bug" and not fires and m["ub"]:
                    problems.append(
                        f"miri reported UB in arm_unsafe_bug.rs on {n}, which "
                        f"model.py derives as `clean` and which executes no "
                        f"DUP -- so the arm is firing on something other than "
                        f"the missing retain: {m['stderr']}")
                if tag == "ship" and m["ub"]:
                    problems.append(
                        f"miri reported UB in the SHIPPED unsafe.rs on {n}: "
                        f"{m['stderr']}")

    doc = {"pin": {"regenerate": "python3 patterns/p34-refcount-stack/controls/"
                                 "rust_bug.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "derivation_ok": dp is None,
           "checksums": rows,
           "miri_iters": MIRI_ITERS,
           "miri": mir,
           "problems": problems,
           "invariant": "arm_unsafe_bug.rs is unsafe.rs with obj_retain(t); "
                        "deleted and nothing else, re-derived at every run; it "
                        "reproduces c/kernel.c bit for bit on every input; Miri "
                        "REPORTS Undefined Behaviour on it for exactly the "
                        "inputs model.py derives as `fires`; and Miri is SILENT "
                        "on the shipped unsafe.rs on every input, which is what "
                        "makes that silence a measurement."}
    out = os.path.join(HERE, "rust_bug.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
