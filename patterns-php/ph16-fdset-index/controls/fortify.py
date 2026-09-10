#!/usr/bin/env python3
"""ph16 -- WHAT THE TOOLCHAIN ALREADY DOES ABOUT THIS ROW'S BOUND, MEASURED.

    python3 patterns-php/ph16-fdset-index/controls/fortify.py

`c/kernel.c` and `c/kernel_hardened.c` open with

    #undef _FORTIFY_SOURCE
    #define _FORTIFY_SOURCE 0

and `../spec.md`'s `provenance.divergences` calls that a SUBSTITUTION.
`PROTOCOL_PHP.md` §A1(c) says a substitution in a non-`modelled` tier must be
**demonstrated** behaviour-preserving over the reachable domain by a
differential with a must-fire control, not asserted. This file is that
differential -- and it is also where the row's most surprising number lives.

**Why it matters, in one sentence.** Ubuntu 24.04's gcc spec adds
`-D_FORTIFY_SOURCE=3` whenever it is optimising; glibc's fortified `FD_SET` is
`__FD_ELT` -> `__fdelt_chk`, which tests `d < FD_SETSIZE` -- **the exact bound
`streamsfuncs.c:541` is missing**. Without the `#undef`, `c-gcc-O3` would be a
HARDENED rung wearing R1's label: it would abort on the adversarial inputs and
would charge every benign `FD_SET` for a check `c-clang-O3` does not perform,
which a reader would attribute to C-versus-Rust.

FOUR QUESTIONS:

  Q1  what is `_FORTIFY_SOURCE` in each (compiler x -O) cell, and does the
      `#undef` in the kernels actually reach it?
  Q2  does an out-of-range `FD_SET` survive, or abort, in each?
  Q3  what does the check cost on BENIGN, in-range indices? (callgrind, two
      point measurement, so the one-shot terms cancel)
  Q4  the substitution's own obligation: is the BENIGN answer identical with
      and without the `#undef`? (it must be -- otherwise this is a `modelled`
      tier, `PROTOCOL_PHP.md` §A2)

CONTROLS (`PROTOCOL_PHP.md` §H -- a validator lands with its negatives):

  must-fire      `--mutate fortify-on` builds the row's own kernel WITHOUT the
                 `#undef` at -O3 and asserts the adversarial input ABORTS. If
                 that does not fire, this file is not measuring fortification
                 and Q2's "the #undef is load-bearing" verdict is unsupported.
  must-NOT-fire  the same build on the BENIGN input must produce the row's
                 checksum and exit 0. A fortified build that broke benign
                 behaviour would mean the substitution changes semantics.
  must-fire #2   `--mutate stub-check` replaces the `#undef` with a hand-written
                 `if (this_fd < FD_SETSIZE)` in `c/kernel.c` and asserts Q2's
                 verdict MOVES -- i.e. the verdict tracks the presence of a
                 bound and not the spelling of a `#define`.

A run that cannot evaluate says so and exits non-zero.
"""

import argparse
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
SCRATCH = os.path.join(REPO, ".temp", "php25", "fortify")
GCC = "/usr/bin/gcc"
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
COMMON = os.path.join(REPO, "common")

ENV = {k: v for k, v in os.environ.items() if k != "LD_PRELOAD"}


def build(cc, opt, kernel_src, out, extra=()):
    """One cell, exactly as `harness/build.py::build_c` spells it."""
    cmd = ([cc, "-std=c99", "-Wall", "-Wextra", f"-O{opt}", "-DSLB_ISOLATED",
            "-I", COMMON, "-I", os.path.join(ROW, "c")]
           + list(extra)
           + [os.path.join(COMMON, "driver.c"), kernel_src,
              os.path.join(ROW, "c", "main.c"), "-o", out])
    r = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def run(binary, inp, timeout=600):
    r = subprocess.run([binary, inp], capture_output=True, text=True,
                       env=ENV, timeout=timeout)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def kernel_without_undef(dst):
    """`c/kernel.c` with the two `_FORTIFY_SOURCE` lines removed, so the
    toolchain default applies. Everything else byte-identical."""
    src = open(os.path.join(ROW, "c", "kernel.c")).read()
    out = src.replace("#undef _FORTIFY_SOURCE\n#define _FORTIFY_SOURCE 0\n", "", 1)
    if out == src:
        return None
    open(dst, "w").write(out)
    return dst


def kernel_with_hand_guard(dst):
    """`c/kernel.c` with the `#undef` kept AND a hand-written bound at the
    write. The must-fire #2 control: Q2's verdict must move for this, which is
    what says the verdict tracks a BOUND rather than a `#define`."""
    src = open(os.path.join(ROW, "c", "kernel.c")).read()
    out = src.replace("\t\t\tFD_SET(this_fd, fds);             /* :541 -- THE DEFECT */",
                      "\t\t\tif (this_fd < FD_SETSIZE) FD_SET(this_fd, fds);",
                      1)
    if out == src:
        return None
    open(dst, "w").write(out)
    return dst


def ir_of(binary, inp):
    """Whole-program Ir under callgrind."""
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        "--callgrind-out-file=/dev/null", binary, inp],
                       capture_output=True, text=True, env=ENV, timeout=3600)
    m = re.search(r"I\s+refs:\s+([\d,]+)", r.stdout + r.stderr)
    return int(m.group(1).replace(",", "")) if m else None


def fdset_calls(inp):
    """How many `FD_SET`s the driver performs on one input, counted from
    `model.py`'s own decode of the same bytes. ⚠ ESTIMATING it -- "about 272
    entries a call" -- would put an arbitrary constant in the denominator of the
    number this control exists to report."""
    spec = importlib.util.spec_from_file_location(
        "ph16model", os.path.join(ROW, "model.py"))
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    m = M.build(inp)
    if not m.entered:
        return 0
    per = []
    for k in range(m.nwin):
        win = m.buf[k * m.stride:(k + 1) * m.stride]
        ctl, n_r, n_w, n_e, es = M.Model._unpack(win)
        n, pos = 0, 0
        for b, cnt in enumerate((n_r, n_w, n_e)):
            run = es[pos:pos + cnt]
            pos += cnt
            if (ctl & (1 << b)) or (ctl & (8 << b)):
                continue
            n += sum(1 for e in run if (e >> 14) >= 2)
        per.append(n)
    total, acc = 0, 0
    for _ in range(m.n_iters):
        k = (acc * m.nwin) >> 64
        total += per[k]
        acc = (acc * 31 + m._win[k][0]) & ((1 << 64) - 1)
    return total


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mutate", choices=("fortify-on", "stub-check"),
                    help="run one control only")
    args = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    for tool, path in (("gcc", GCC), ("clang", CLANG), ("valgrind", VALGRIND)):
        if not os.path.exists(path):
            print(f"CANNOT EVALUATE: {tool} not at {path}")
            return 2
    ind = os.path.join(ROW, "inputs")
    benign = os.path.join(ind, "small.bin")
    adv = os.path.join(ind, "adversarial-silent.bin")
    for p in (benign, adv):
        if not os.path.exists(p):
            print(f"CANNOT EVALUATE: {p} missing -- run inputs/gen.py")
            return 2

    kern = os.path.join(ROW, "c", "kernel.c")
    plain = kernel_without_undef(os.path.join(SCRATCH, "kernel_nofix.c"))
    if plain is None:
        print("CANNOT EVALUATE: c/kernel.c does not carry the two "
              "`_FORTIFY_SOURCE` lines this control exists to remove -- either "
              "the row changed or this control is stale")
        return 2

    bad = 0

    # ---- the must-fire / must-NOT-fire pair, always run ------------------
    ok, log = build(GCC, 3, plain, os.path.join(SCRATCH, "b_nofix_O3"))
    if not ok:
        print(f"CANNOT EVALUATE: the no-#undef build failed:\n{log}")
        return 2
    rc_adv, so_adv, se_adv = run(os.path.join(SCRATCH, "b_nofix_O3"), adv)
    rc_ben, so_ben, _ = run(os.path.join(SCRATCH, "b_nofix_O3"), benign)
    fired = "bit out of range" in se_adv
    print("== CONTROL must-fire: gcc -O3 WITHOUT the #undef, adversarial input")
    print(f"   exit={rc_adv} stderr={se_adv[:90]!r}")
    if fired:
        print("   PASS  the toolchain's own check fired -- the #undef in "
              "c/kernel.c is load-bearing")
    else:
        print("   FAIL  no diagnostic. This control is not measuring "
              "fortification, so every verdict below is unsupported.")
        bad += 1

    ok2, _ = build(GCC, 3, kern, os.path.join(SCRATCH, "b_fix_O3"))
    rc_ref, so_ref, _ = run(os.path.join(SCRATCH, "b_fix_O3"), benign)
    print("== CONTROL must-NOT-fire: the same build on the BENIGN corpus")
    print(f"   with #undef    exit={rc_ref} stdout={so_ref}")
    print(f"   without #undef exit={rc_ben} stdout={so_ben}")
    if rc_ben == rc_ref == 0 and so_ben == so_ref:
        print("   PASS  the substitution changes NO benign answer "
              "(PROTOCOL_PHP.md A1(c), A2)")
    else:
        print("   FAIL  the benign answer moved -- the `#undef` is not "
              "behaviour-preserving and the tier is `modelled`")
        bad += 1

    if args.mutate == "fortify-on":
        return 1 if bad else 0

    # ---- must-fire #2: the verdict tracks a BOUND, not a `#define` -------
    stub = kernel_with_hand_guard(os.path.join(SCRATCH, "kernel_stub.c"))
    if stub is None:
        print("CANNOT EVALUATE: could not plant the hand-written bound")
        return 2
    ok3, log3 = build(GCC, 3, stub, os.path.join(SCRATCH, "b_stub_O3"))
    if not ok3:
        print(f"CANNOT EVALUATE: the hand-guard build failed:\n{log3}")
        return 2
    rc_s, so_s, se_s = run(os.path.join(SCRATCH, "b_stub_O3"), adv)
    rc_r1, so_r1, se_r1 = run(os.path.join(SCRATCH, "b_fix_O3"), adv)
    print("== CONTROL must-fire #2: a HAND-WRITTEN bound, #undef kept")
    print(f"   R1 as shipped        exit={rc_r1} stdout={so_r1}")
    print(f"   R1 + hand-written    exit={rc_s} stdout={so_s}")
    if so_s != so_r1 and rc_s == 0 and not se_s:
        print("   PASS  the verdict MOVES with the bound and not with the "
              "`#define`, so F52's 'the setup encodes the answer' does not "
              "apply here")
    else:
        print("   FAIL  planting a bound did not move the answer")
        bad += 1
    if args.mutate == "stub-check":
        return 1 if bad else 0

    # ---- Q1/Q2: the whole (compiler x -O) grid ---------------------------
    print("\n== Q1/Q2  _FORTIFY_SOURCE, and what an out-of-range FD_SET does")
    print(f"   {'cell':22s} {'#undef?':9s} {'adversarial exit':17s} diagnostic")
    for name, cc in (("gcc", GCC), ("clang", CLANG)):
        for opt in (0, 3):
            for undef, ksrc in (("yes", kern), ("no", plain)):
                out = os.path.join(SCRATCH, f"g_{name}_O{opt}_{undef}")
                okb, logb = build(cc, opt, ksrc, out)
                if not okb:
                    print(f"   {name}-O{opt:<19d} {undef:9s} CANNOT EVALUATE "
                          f"(build failed)")
                    bad += 1
                    continue
                rc, so, se = run(out, adv)
                diag = "bit out of range" if "bit out of range" in se else (
                    se[:40] if se else "-")
                print(f"   {name}-O{opt:<19d} {undef:9s} {str(rc):17s} {diag}")

    # ---- Q3: what the check costs on BENIGN input ------------------------
    print("\n== Q3  the cost of the toolchain's check on BENIGN indices "
          "(callgrind, whole-program Ir on small.bin)")
    rows = []
    for name, cc in (("gcc", GCC), ("clang", CLANG)):
        for undef, ksrc in (("yes", kern), ("no", plain)):
            out = os.path.join(SCRATCH, f"ir_{name}_{undef}")
            okb, _ = build(cc, 3, ksrc, out)
            ir = ir_of(out, benign) if okb else None
            rows.append((name, undef, ir))
            print(f"   {name}-O3 #undef={undef:3s} Ir = "
                  f"{ir if ir is not None else 'CANNOT EVALUATE'}")
    n_fdset = fdset_calls(benign)
    print(f"   benign FD_SET calls on small.bin = {n_fdset} "
          f"(counted from model.py's own decode, not estimated)")
    d = {(n, u): v for n, u, v in rows}
    if all(d.get(k) for k in (("gcc", "yes"), ("gcc", "no"),
                              ("clang", "yes"), ("clang", "no"))):
        # small.bin: 25 000 calls; entries per call = (550 - 6) / 2 = 272; the
        # number of FD_SETs is the number of tag>=2 entries actually walked,
        # which the model knows. Reported as a total and per call, and the
        # per-FD_SET figure is left to NOTES.md, which has the model's count.
        dg = d[("gcc", "no")] - d[("gcc", "yes")]
        dc = d[("clang", "no")] - d[("clang", "yes")]
        print(f"   gcc   delta = {dg:>12,d} Ir  = {dg / 25000:.2f} Ir/call "
              f"= {dg / n_fdset:.2f} Ir per BENIGN FD_SET"
              if n_fdset else f"   gcc   delta = {dg:>12,d} Ir")
        print(f"   clang delta = {dc:>12,d} Ir  = {dc / 25000:.2f} Ir/call "
              f"= {dc / n_fdset:.4f} Ir per BENIGN FD_SET"
              if n_fdset else f"   clang delta = {dc:>12,d} Ir")
        if dg <= 0:
            print("   ⚠ gcc's fortified build is not DEARER -- either the "
                  "spec no longer injects -D_FORTIFY_SOURCE or the check is "
                  "free, and either way NOTES.md §2's number is stale")
            bad += 1
        if abs(dc) > 1000:
            print("   ⚠ clang moved too: this control's 'only gcc fortifies' "
                  "claim needs re-reading")
            bad += 1
    else:
        print("   CANNOT EVALUATE: a callgrind run produced no Ir")
        bad += 1

    print("\nRESULT:", "FAIL" if bad else "PASS", f"({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
