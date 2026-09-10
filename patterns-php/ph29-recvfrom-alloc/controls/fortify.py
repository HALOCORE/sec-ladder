#!/usr/bin/env python3
"""ph29 -- DOES `_FORTIFY_SOURCE` PUT THIS ROW'S OWN BOUND IN? Measured, not
inherited.

    python3 patterns-php/ph29-recvfrom-alloc/controls/fortify.py

⚠⚠⚠ **`RECAP_PHP.md` F56 IS ONE ROW OLD AND IT SAYS EXPLICITLY NOT TO
INHERIT ITS ANSWER.** Ubuntu 24.04's gcc spec adds `-D_FORTIFY_SOURCE=3`
whenever it is optimising; on `ph16` that turned `FD_SET` into `__fdelt_chk`
-- **the exact bound that row is about** -- and charged +60.6 % whole-program.
`ph03` and `ph07` were measured clean. **ph29 is NEW and allocation-shaped, and
level 3 uses `__builtin_dynamic_object_size`, which tracks allocation sizes
level 2 cannot.** So this file asks the question again, on THIS row's kernel.

Four arms, and the middle two are what make the answer believable:

    A  is `_FORTIFY_SOURCE` injected at all, per (compiler x -O level)?
    B  does THIS ROW's kernel object carry a fortify `_chk` symbol, in all
       eight (compiler x opt x mode) configurations `build.py` compiles?
    C  MUST-FIRE: does the same detector, same compiler, same flags, see a
       `__memcpy_chk` in a probe where gcc CAN bound the destination?
       ⚠ Without C, arm B's silence is indistinguishable from a broken
       detector -- which is `PROTOCOL_PHP.md` §H exactly.
    D  WHY NOT: a two-variant differential isolating the mechanism.

⚠ **Every probe uses a RUNTIME length, never a literal** (`F52`): a constant
lets the compiler prove the bound and elide the check, which is a setup that
encodes the answer.

⭐ **THE ANSWER, AND IT IS A FINDING ABOUT PHP RATHER THAN ABOUT GCC:**
`php_shim_emalloc` has TWO return paths -- the size-class cache
(`zend_alloc.c:150-168`) and `malloc` (`:182`) -- so the pointer reaching
`memcpy` is a PHI of two allocations and `__builtin_dynamic_object_size` of
that is unknown. Delete the cache arm and gcc emits `__memcpy_chk`. **PHP
5.0.0's own size-class cache defeats a 2024 compiler mitigation**, and it is
the same feature that makes `crashes_pristine_5_0_0 = False` unreliable
(`PROTOCOL_PHP.md` §B1.1). Neither C rung needs `#undef _FORTIFY_SOURCE`,
which is why `../spec.md` FORBIDS one.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
SCRATCH = os.path.join(REPO, ".temp", "php27", "fortify")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
CLANG = os.environ.get("SLB_CLANG", os.path.expanduser("~/tools/llvm/bin/clang"))

FDEF = """#include <string.h>
#ifdef _FORTIFY_SOURCE
#error FORTIFY_IS_DEFINED
#else
#error FORTIFY_IS_NOT_DEFINED
#endif
"""

# Arm C, the must-fire control: a heap destination whose size __bdos CAN see,
# ONE allocation site, and a RUNTIME length.
MUSTFIRE = """#include <stdlib.h>
#include <string.h>
char *sink;
void probe(unsigned long n, const char *s)
{
    char *d = (char *)malloc(64);
    memcpy(d, s, n);
    sink = d;
}
"""

# Arm D: the mechanism, isolated. V=1 has php_shim_emalloc's shape (a cache arm
# plus a malloc arm); V=0 is the same function with the cache arm deleted.
MECH = """#include <stdlib.h>
#include <string.h>
char *sink;
static char *cache[11];
static unsigned ccount[11];
static char *shim_emalloc(unsigned long size)
{
    unsigned rs = (unsigned)((size + 7) & ~7UL);
#if V
    unsigned ci = rs >> 3;
    if (ci < 11 && ccount[ci] > 0) { char *c = cache[ci]; ccount[ci]--; return c + 24; }
#endif
    { char *p = (char *)malloc(24 + rs); return p ? p + 24 : (char *)0; }
}
void probe(unsigned long n, const char *s)
{
    char *d = shim_emalloc(n + 1);
    if (d) { memcpy(d, s, n); }
    sink = d;
}
"""


def write(name, text):
    p = os.path.join(SCRATCH, name)
    open(p, "w").write(text)
    return p


def chk_syms(obj):
    """Fortify symbols only. ⚠ `__stack_chk_fail` IS NOT ONE -- it is the stack
    protector, it is present at gcc -O0 where fortify is OFF, and a grep for
    `_chk` that counts it reports the opposite of the truth."""
    r = subprocess.run(["nm", "-u", obj], capture_output=True, text=True)
    return [s.split()[-1] for s in r.stdout.splitlines()
            if "_chk" in s and "__stack_chk_fail" not in s]


def compile_obj(cc, src, out, opt, mode, extra=()):
    cmd = [cc, "-std=c99", "-Wall", "-Wextra", opt]
    cmd += ["-DSLB_ISOLATED"] if mode == "isolated" else ["-flto"]
    cmd += list(extra) + ["-c", src, "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    return r.returncode, (r.stdout + r.stderr)


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    print(__doc__.split("\n\n")[0])
    print()
    bad = 0
    ccs = [("gcc", GCC), ("clang", CLANG)]

    print("== A  is -D_FORTIFY_SOURCE injected, with build.py's own flags?")
    fdef = write("fdef.c", FDEF)
    inject = {}
    for name, cc in ccs:
        for opt in ("-O0", "-O3"):
            rc, log = compile_obj(cc, fdef, "/dev/null", opt, "isolated")
            m = re.search(r"FORTIFY_IS_[A-Z_]+", log)
            inject[(name, opt)] = (m.group(0) == "FORTIFY_IS_DEFINED") if m else None
            print(f"   {name:6s} {opt:4s} -> {m.group(0) if m else 'UNKNOWN'}")
    print()

    print("== B  does ph29's OWN kernel object carry a fortify _chk symbol?")
    ker = os.path.join(ROW, "c", "kernel.c")
    total = 0
    for name, cc in ccs:
        for opt in ("-O0", "-O3"):
            for mode in ("isolated", "whole"):
                obj = os.path.join(SCRATCH, f"k-{name}-{opt}-{mode}.o")
                rc, log = compile_obj(cc, ker, obj, opt, mode,
                                      ["-I", os.path.join(REPO, "common"),
                                       "-I", os.path.join(ROW, "c")])
                if rc != 0:
                    print(f"   {name:6s} {opt:4s} {mode:9s} BUILD FAILED\n"
                          f"{log[:300]}")
                    bad += 1
                    continue
                syms = chk_syms(obj)
                total += len(syms)
                print(f"   {name:6s} {opt:4s} {mode:9s} fortify _chk: "
                      f"{syms if syms else 'NONE'}")
    print(f"   -> {total} fortify check(s) across all 8 configurations")
    print()

    print("== C  MUST-FIRE: the same detector on a destination gcc CAN bound")
    mf = write("mustfire.c", MUSTFIRE)
    fired_any = False
    for name, cc in ccs:
        for opt in ("-O0", "-O3"):
            obj = os.path.join(SCRATCH, f"mf-{name}-{opt}.o")
            rc, log = compile_obj(cc, mf, obj, opt, "isolated")
            if rc != 0:
                print(f"   {name:6s} {opt:4s} BUILD FAILED")
                bad += 1
                continue
            syms = chk_syms(obj)
            fired_any |= bool(syms)
            expect = " <- MUST FIRE" if (name, opt) == ("gcc", "-O3") else ""
            print(f"   {name:6s} {opt:4s} fortify _chk: "
                  f"{syms if syms else 'NONE'}{expect}")
    if not fired_any:
        print("   FAIL: the detector never fired on ANY configuration, so arm "
              "B's silence proves nothing")
        bad += 1
    print()

    print("== D  WHY: the mechanism, isolated. Two variants, one difference.")
    got = {}
    for v in (1, 0):
        src = write(f"mech{v}.c", MECH)
        obj = os.path.join(SCRATCH, f"mech-{v}.o")
        rc, log = compile_obj(GCC, src, obj, "-O3", "isolated", [f"-DV={v}"])
        if rc != 0:
            print(f"   V={v} BUILD FAILED\n{log[:300]}")
            bad += 1
            continue
        got[v] = chk_syms(obj)
        what = ("php_shim_emalloc's shape: a size-class CACHE arm AND a malloc arm"
                if v else "the same function with the CACHE ARM DELETED")
        print(f"   gcc -O3  V={v}  ({what})")
        print(f"            fortify _chk: {got[v] if got[v] else 'NONE'}")
    if got.get(1) or not got.get(0):
        print("   FAIL: the two variants do not differ in the expected "
              "direction, so the stated mechanism is not supported")
        bad += 1
    else:
        print("   -> the ONLY difference is the cache arm, and it is what "
              "makes __builtin_dynamic_object_size unknown.")
        print("      PHP 5.0.0's size-class cache defeats -D_FORTIFY_SOURCE=3.")
    print()

    ok_b = (total == 0)
    print(f"VERDICT: ph29's kernel carries {total} fortify check(s) -- "
          f"{'NO #undef is needed' if ok_b else 'A RUNG MUST #undef IT'}")
    print("RESULT:", "FAIL" if bad else "PASS", f"({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
