#!/usr/bin/env python3
"""p36's CATCHER controls: what, if anything, sees the CONTROL TRANSFER?

The measured matrix's only checker for this bug is `harness/check.py` stage 7's
`gcc -O1 -fsanitize=address,undefined`, and `../NOTES.md` 0b measures that every
diagnostic it produces names the ARRAY READ. This script prices the two things
that could name the *call*, both of which are **outside the matrix on purpose**:

  `-fsanitize=function`   clang-only. gcc 13.3.0 rejects the flag outright.
                          Catches an indirect call through a mismatched
                          function type, by reading a signature word placed
                          before the callee's entry.
  `-fsanitize=cfi-icall`  clang-only, needs `-flto` and `-fvisibility=hidden`.
                          THE real-world answer for this bug class. ⚠ It also
                          needs `-fuse-ld=lld` on this box: `-flto` through the
                          system `/usr/bin/ld` wants `LLVMgold.so`, which the
                          LLVM 22.1.6 distribution does not ship (upstream
                          dropped the gold plugin), and the link fails with
                          `error loading plugin: .../LLVMgold.so: cannot open
                          shared object file`. That is a second reason CFI could
                          not be a matrix flag without a `build.py` change.

⚠ **NEITHER IS A RUNG AND NEITHER MAY BECOME ONE.** Both are `harness/build.py`
flag changes, and `build.py` is hashed into the MEASUREMENT records, so one flag
costs a full re-measure of every pattern in the tree (RECAP, settled answer 4).
CFI is additionally a WHOLE-PROGRAM property, which an `isolated` build cannot
express at all. p36 prices the source-level range test (R1h) and reports these
two as controls, with their numbers, and claims nothing about what CFI would
cost inside the matrix.

    python3 patterns/p36-vtable-dispatch/controls/cfi_probe.py
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p36", "cfi")
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
GCC = "/usr/bin/gcc"

BUILDS = [
    ("gcc-fnsan", GCC, ["-O1", "-g", "-fsanitize=function"],
     "gcc + -fsanitize=function -- expected to be REJECTED by the driver"),
    ("clang-fnsan", CLANG, ["-O1", "-g", "-fsanitize=function"],
     "clang + -fsanitize=function"),
    ("clang-cfi", CLANG,
     ["-O1", "-g", "-flto", "-fuse-ld=lld", "-fvisibility=hidden",
      "-fsanitize=cfi-icall", "-fno-sanitize-trap=cfi-icall",
      "-fsanitize-recover=cfi-icall"],
     "clang + -fsanitize=cfi-icall (needs -flto and -fvisibility=hidden)"),
    ("clang-cfi-O3", CLANG,
     ["-O3", "-flto", "-fuse-ld=lld", "-fvisibility=hidden",
      "-fsanitize=cfi-icall", "-fno-sanitize-trap=cfi-icall",
      "-fsanitize-recover=cfi-icall"],
     "the same at -O3, for the Ir price"),
    ("clang-plain-O3", CLANG, ["-O3"],
     "the same compiler and flags WITHOUT cfi -- the baseline the price is "
     "measured against"),
]

INPUTS = ["small.bin", "adversarial-oob.bin", "adversarial-oobmax.bin"]

# What CFI COSTS, measured the same way every other number here is: per-function
# exclusive `Ir` for the kernel symbol, against the same compiler and the same
# `-O3` without the flag. `../NOTES.md` 0b quotes it.
PRICE = [("clang-cfi-O3", "clang-plain-O3")]
PRICE_INPUTS = [("small.bin", 20000), ("large.bin", 20000)]
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANN = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
sys.path.insert(0, os.path.join(REPO, "harness"))
import measure as measuremod  # noqa: E402


def ir_per_call(binary, blob, ncalls):
    out = os.path.join(OUT, "cg.out")
    subprocess.run([VALGRIND, "--tool=callgrind", f"--callgrind-out-file={out}",
                    binary, blob], capture_output=True, text=True, check=True)
    ann = subprocess.run([CG_ANN, "--threshold=100", out],
                         capture_output=True, text=True, check=True).stdout
    tot, _ = measuremod._sum_rows(ann, "kernel")
    return None if tot is None else tot / ncalls


def build(tag, cc, flags, kernel="kernel.c"):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"{tag}.{kernel[:-2]}")
    cmd = [cc, "-std=c99", *flags, "-DSLB_ISOLATED",
           "-I", os.path.join(REPO, "common"), "-I", os.path.join(PDIR, "c"),
           os.path.join(REPO, "common", "driver.c"),
           os.path.join(PDIR, "c", kernel),
           os.path.join(PDIR, "c", "main.c"), "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return out, r


def main():
    for tag, cc, flags, desc in BUILDS:
        print(f"=== {tag}: {desc}")
        print(f"    flags: {' '.join(flags)}")
        out, r = build(tag, cc, flags)
        if r.returncode != 0:
            head = (r.stdout + r.stderr).strip().splitlines()[:3]
            for line in head:
                print(f"    BUILD FAILED: {line}")
            continue
        for name in INPUTS:
            p = os.path.join(PDIR, "inputs", name)
            rr = subprocess.run([out, p], capture_output=True, text=True,
                                timeout=300)
            so = rr.stdout.strip()
            se = " | ".join(l for l in rr.stderr.strip().splitlines()[:3])
            print(f"    {name:24s} rc={rr.returncode:<5d} out={so:22s} {se[:180]}")
    print()
    print("=== WHAT CFI COSTS (kernel-exclusive Ir per call, -O3, isolated)")
    for a, b in PRICE:
        pa = os.path.join(OUT, f"{a}.kernel")
        pb = os.path.join(OUT, f"{b}.kernel")
        if not (os.path.exists(pa) and os.path.exists(pb)):
            print("    (one of the builds is missing; skipped)")
            continue
        for blob, nc in PRICE_INPUTS:
            p = os.path.join(PDIR, "inputs", blob)
            ia, ib = ir_per_call(pa, p, nc), ir_per_call(pb, p, nc)
            print(f"    {blob:12s} {a}={ia:10.4f}  {b}={ib:10.4f}  "
                  f"delta={ia - ib:+10.4f}  ({100 * (ia - ib) / ib:+.2f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
