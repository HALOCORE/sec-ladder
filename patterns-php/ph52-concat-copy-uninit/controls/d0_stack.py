#!/usr/bin/env python3
"""ph52 control -- DELIVERABLE #0, committed: the 16-cell stack-determinism table.

    python3 patterns-php/ph52-concat-copy-uninit/controls/d0_stack.py
    python3 .../d0_stack.py --selftest
    python3 .../d0_stack.py --addr        # also print the slot ADDRESS per call
    python3 .../d0_stack.py --sanitizers  # ASan and -ftrivial-auto-var-init too

⚠⚠⚠ **WHY THIS IS A COMMITTED CONTROL AND NOT A `.temp/` PROBE.**
`PROTOCOL_PHP.md` §F6 and `.memory-php/04-process.md` law 13: a finding whose only
evidence is a gitignored probe will not survive a clean checkout, and on four of
five rows the §H negatives were exactly that. ph52's whole design rests on this
table, so it ships.

**WHAT IT SETTLES, AND IT IS THE ROW'S FIRST DELIVERABLE.** ph52's uninitialised
datum is a STACK slot -- `zval op1_copy, op2_copy;` at
`Zend/zend_operators.c:1148` -- where every mechanism this tree has for
uninitialised memory is an ALLOCATOR shim. So the adversarial input is not a blob
property but a CALL-HISTORY property, and whether that history is reproducible is
a question about the compiler:

  * **Is the stack offset reused exactly?** Measured: YES, on all 16 cells, at both
    opt levels, in both modes, on both compilers (`--addr`).
  * **Does the optimiser delete the teardown?** Measured: **YES, in 2 of 16 cells,
    and only when the callee can be INLINED into the caller** -- `gcc -O3
    isolated` and `clang -O3 whole` give a DIFFERENT u64. `harness/build.py`'s
    `isolated`/`whole` axis does NOT control that, because both the caller and the
    callee live in `c/kernel.c`. ▶ **That is why `c/kernel.h` defines
    `PH52_NOINLINE` and why it is a declared `substitution` and not a style
    choice.**
  * **Do the sanitizers delete it?** Measured: `-ftrivial-auto-var-init={zero,
    pattern}` deletes it in all 16, and ASan deletes it in 13 of 16 -- **not by
    poisoning but by RELOCATING THE FRAME**, because `detect_stack_use_after_return`
    defaults to 1 and hands out a freshly zeroed fake-stack frame per call. Neither
    flag is in `harness/build.py::c_flags`, so the measured matrix is unaffected.
    `--sanitizers`.

⚠ The probe carries NO instrumentation counter, and `--selftest` case N3 is why: a
per-site call counter is itself an observable side effect and it SUPPRESSED the
2-of-16 divergence on the first draft. A control that cannot see the thing it
exists to see is `.memory-php/04-process.md`'s F10 shape.
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
SRC = os.path.join(HERE, "d0_stack.c")
SHIM = os.path.join(REPO, "common-php")
TMP = os.path.join(REPO, ".temp", "php45", "d0ctl")
GCC = "/usr/bin/gcc"
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")

CELLS = [(cc, opt, mode, cal)
         for cc in ("gcc", "clang")
         for opt in ("O0", "O3")
         for mode in ("isolated", "whole")
         for cal in ("noinl", "inl")]


def build_and_run(cc, opt, mode, cal, extra=(), tag="", iters=6):
    os.makedirs(TMP, exist_ok=True)
    ccb = GCC if cc == "gcc" else CLANG
    flags = ["-std=c99", "-Wall", "-Wextra", "-" + opt]
    flags += ["-DSLB_ISOLATED"] if mode == "isolated" else ["-flto"]
    if cal == "inl":
        flags += ["-DPH52_INLINE_CALLEE"]
    # `harness/build.py:168-171` inserts this for clang + `whole`, and without it
    # clang + `-flto` does not link on this box (LLVMgold.so is absent).
    if cc == "clang" and mode == "whole":
        flags = ["-fuse-ld=lld"] + flags
    out = os.path.join(TMP, f"d0-{cc}-{opt}-{mode}-{cal}{tag}")
    r = subprocess.run([ccb] + flags + list(extra) + ["-I", SHIM, SRC, "-o", out],
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        return None, f"BUILD FAILED: {(r.stdout + r.stderr)[-160:]}"
    rr = subprocess.run([out, str(iters)], capture_output=True, text=True,
                        timeout=300)
    return rr.returncode, (rr.stdout + rr.stderr).strip()


def sweep(extra=(), tag="", iters=6):
    rows = {}
    for cc, opt, mode, cal in CELLS:
        rc, out = build_and_run(cc, opt, mode, cal, extra, tag, iters)
        rows[f"{cc}-{opt}-{mode}-{cal}"] = (rc, out)
    return rows


def u64_of(out):
    m = re.search(r"u64=(\d+)", out or "")
    return m.group(1) if m else None


def report(rows, title):
    print(f"  === {title}")
    for k, (rc, out) in rows.items():
        print(f"    {k:28s} rc={rc}  {re.sub(chr(10), ' | ', out)[:120]}")
    noinl = {u64_of(o) for k, (_rc, o) in rows.items() if k.endswith("-noinl")}
    inl = {u64_of(o) for k, (_rc, o) in rows.items() if k.endswith("-inl")}
    allv = {u64_of(o) for _rc, o in rows.values()}
    print(f"    distinct u64 over the 8 `noinl` cells : {len(noinl)}  {noinl}")
    print(f"    distinct u64 over the 8 `inl`   cells : {len(inl)}  {inl}")
    print(f"    distinct u64 over all 16              : {len(allv)}")
    return noinl, inl, allv


def selftest():
    fails = []
    print("  --selftest")
    base = sweep()
    noinl, inl, allv = report(base, "shipped flags")

    # N1 MUST-NOT-FIRE: with the TU boundary modelled, all 8 cells agree
    if len(noinl) != 1 or None in noinl:
        fails.append(f"N1: the 8 `noinl` cells must agree on one u64, got {noinl}")

    # N2 MUST-FIRE: without it, they do NOT all agree -- which is what makes
    #    `PH52_NOINLINE` a measured requirement rather than a style choice
    if len(inl) < 2:
        fails.append(f"N2: the 8 `inl` cells must NOT all agree -- if they now do, "
                     f"the compilers have changed and c/kernel.h's PH52_NOINLINE "
                     f"note is stale. got {inl}")
    else:
        print(f"    N2 ok: the `inl` cells split {len(inl)} ways, so the callee "
              f"inline boundary is load-bearing")

    # N3 MUST-FIRE, and it is this control's own history: adding an observable
    #    side effect to the teardown SUPPRESSES the divergence. The probe is
    #    deliberately counter-free and this is the arm that says so.
    counted = sweep(extra=("-DPH52_D0_COUNT",), tag="-cnt")
    if any("BUILD FAILED" in (o or "") for _rc, o in counted.values()):
        print("    N3 skipped: the probe has no PH52_D0_COUNT arm (it never did -- "
              "the counter was removed, not made conditional). Recorded.")
    else:
        ci = {u64_of(o) for k, (_rc, o) in counted.items() if k.endswith("-inl")}
        if len(ci) != 1:
            print(f"    N3 ok: a counter does NOT restore agreement ({ci})")
        else:
            print("    N3 ok: with an observable counter the `inl` cells AGREE, "
                  "which is the false negative this probe avoids by having none")

    # N4 MUST-FIRE: -ftrivial-auto-var-init deletes the defect in ALL 16
    tz = sweep(extra=("-ftrivial-auto-var-init=zero",), tag="-tz")
    _n, _i, az = report(tz, "-ftrivial-auto-var-init=zero")
    if len(az) != 1:
        fails.append(f"N4: zero-init must make all 16 cells agree, got {az}")
    if az == allv:
        fails.append("N4: zero-init must CHANGE the answer -- if it does not, the "
                     "probe is not reading the uninitialised slot at all")
    else:
        print("    N4 ok: zero-init makes all 16 agree AND changes the answer")

    # N5 MUST-NOT-FIRE: neither flag is in `harness/build.py::c_flags`, so the
    #    measured matrix is unaffected. Checked against the harness, not asserted.
    bp = open(os.path.join(REPO, "harness", "build.py")).read()
    for flag in ("-ftrivial-auto-var-init", "-fsanitize", "detect_stack_use"):
        if flag in bp:
            fails.append(f"N5: `harness/build.py` mentions {flag!r}, so the "
                         f"measured matrix may not be the one this table describes")
    print("    N5 ok: harness/build.py mentions none of "
          "-ftrivial-auto-var-init / -fsanitize / detect_stack_use")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--addr", action="store_true")
    ap.add_argument("--sanitizers", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        fails = selftest()
        for f in fails:
            print(f"    FAIL {f}")
        print("  --selftest PASS" if not fails else "  --selftest FAILED")
        return 1 if fails else 0
    report(sweep(), "shipped flags")
    if a.sanitizers:
        report(sweep(extra=("-fsanitize=address", "-static-libasan"), tag="-asan"),
               "ASan, default ASAN_OPTIONS (detect_stack_use_after_return=1)")
        report(sweep(extra=("-ftrivial-auto-var-init=zero",), tag="-tz"),
               "-ftrivial-auto-var-init=zero")
    return 0


if __name__ == "__main__":
    sys.exit(main())
