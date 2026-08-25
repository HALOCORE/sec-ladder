#!/usr/bin/env python3
"""p46 — the two C controls `../NOTES.md` 0a rests on, and they must survive a clone.

`.memory/05-layout.md` step 11 and its corollary: a control that cannot live in
the pattern dir ships as a **committed generator** plus a `NOTES.md` section
carrying the diff, the commands and the output. `.gitignore` contains `.temp/`,
so a `NOTES.md` that cites `.temp/tNN/foo.c` for a load-bearing mechanism cites
nothing a reader can run. Both controls below were originally written under
`.temp/t89/`; they are here because `../NOTES.md` 0a's *mechanism* depends on
them, not merely its numbers.

    controls/harm_layout.py --clamp     # is the bug a MEMORY event at all?
    controls/harm_layout.py --layout    # WHY the shipped C rung is silent
    controls/harm_layout.py --all

⚠ **These are NOT the shipped kernel.** They are standalone reductions, and one
of them is the reason `../NOTES.md` 0a carries a correction: a reduction that
drops the second scratch array `bl[256]` gets a *different frame layout* and
therefore a *different harm*, loud where the shipped kernel is silent. That is
the finding, and `--layout` is what measures it.

    A. --clamp   THE CONTROL THAT KEEPS THE ROW ALIVE. The identical limb
                 miscount with the product index CLAMPED -- `out[(i+j) % OUTCAP]`
                 -- under ASan + UBSan. If it is exit 0 with both sanitizers
                 silent then p46's memory-unsafe framing is CONDITIONAL on not
                 clamping, the clamp has to be a `forbidden` entry, and a rung
                 that took it would die `p31`'s death. Measured: exit 0, silent,
                 wrong answer.

    B. --layout  WHY THE SHIPPED C RUNG IS SILENT WHERE A ONE-ARRAY REDUCTION
                 FAULTS. Prints the frame offsets of the two automatic arrays
                 the shipped kernel has. Measured: gcc at -O0 and -O3 and clang
                 at -O3 put `bl` exactly 96 limbs above `out`, so `out[96]` IS
                 `bl[0]` and the overflow is absorbed; clang at -O0 puts it
                 2048 bytes below, so the same write leaves the frame.
"""
import argparse
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
CLANG = os.environ.get("SLB_CLANG", os.path.expanduser("~/tools/llvm/bin/clang"))
SCRATCH = os.path.join(REPO, ".temp", "check", "p46-controls")

# The two constants below MUST equal c/kernel.h's. They are repeated rather than
# included because these controls are deliberately standalone: the point of A is
# that it is NOT the shipped kernel, and the point of B is that a reduction with
# a different frame gets a different harm.
OUTCAP, BCAP = 96, 256

CLAMP_C = r"""
/* p46 control A -- the CLAMPED spelling of the identical limb miscount.
 * `../NOTES.md` 0a run D. If this is exit 0 with ASan and UBSan silent, the
 * clamp deletes the pattern and must be `forbidden`. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define OUTCAP %(OUTCAP)d
static uint64_t ld64(const uint8_t *p) {
    return (uint64_t)p[0] | ((uint64_t)p[1] << 8) | ((uint64_t)p[2] << 16)
        | ((uint64_t)p[3] << 24) | ((uint64_t)p[4] << 32) | ((uint64_t)p[5] << 40)
        | ((uint64_t)p[6] << 48) | ((uint64_t)p[7] << 56);
}
__attribute__((noinline))
static uint64_t k_clamped(const uint8_t *w, size_t len) {
    uint64_t out[OUTCAP]; uint64_t acc = 0; size_t n, m, i, j, k;
    if (len < 8) return 0;
    n = w[0]; m = w[1];
    if (n == 0 || m == 0) return 0;
    if (8 + 8 * (n + m) > len) return 0;
    /* NO output-side bound -- and the index is CLAMPED instead. */
    memset(out, 0, sizeof out);
    for (i = 0; i < n; i++) {
        uint64_t ai = ld64(w + 8 + 8 * i), carry = 0;
        for (j = 0; j < m; j++) {
            size_t q = (i + j) %% OUTCAP;                    /* THE CLAMP */
            unsigned __int128 t = (unsigned __int128)ai * ld64(w + 8 + 8 * (n + j))
                + out[q] + carry;
            out[q] = (uint64_t)t; carry = (uint64_t)(t >> 64);
        }
        out[(i + m) %% OUTCAP] = carry;
    }
    for (k = 0; k < n + m; k++) acc = acc * 31 + out[k %% OUTCAP];
    return (acc * 31 + n) * 31 + m;
}
int main(int argc, char **argv) {
    size_t n = argc > 1 ? (size_t)atoi(argv[1]) : 120;
    size_t m = argc > 2 ? (size_t)atoi(argv[2]) : 120;
    size_t len = 8 + 8 * (n + m), t;
    uint8_t *w = calloc(1, len);
    if (!w) return 9;
    w[0] = (uint8_t)n; w[1] = (uint8_t)m;
    for (t = 0; t < (n + m) * 8; t++) w[8 + t] = (uint8_t)(0x9d * (t + 1) + 0x37);
    printf("clamped n=%%zu m=%%zu n+m=%%zu OUTCAP=%%d -> %%llu\n",
           n, m, n + m, OUTCAP, (unsigned long long)k_clamped(w, len));
    free(w); return 0;
}
""" % {"OUTCAP": OUTCAP}

LAYOUT_C = r"""
/* p46 control B -- the frame layout of the shipped kernel's TWO automatic
 * arrays. `../NOTES.md` 0a. */
#include <stdint.h>
#include <stdio.h>
#define OUTCAP %(OUTCAP)d
#define BCAP %(BCAP)d
__attribute__((noinline)) static void two(void) {
    uint64_t out[OUTCAP]; uint64_t bl[BCAP];
    out[0] = 1; bl[0] = 2;
    printf("  two arrays (the SHIPPED shape): out=%%p bl=%%p  bl-out = %%+ld bytes"
           " (%%+ld limbs)\n", (void *)out, (void *)bl,
           (long)((char *)bl - (char *)out), (long)(((char *)bl - (char *)out) / 8));
    printf("    out[%%d] (adversarial-nearmiss' first OOB limb) is %%s bl\n", OUTCAP,
           ((char *)&out[OUTCAP] >= (char *)bl
            && (char *)&out[OUTCAP] < (char *)&bl[BCAP]) ? "INSIDE" : "OUTSIDE");
    printf("    out[179] (adversarial-oob's reach) is %%s bl\n",
           ((char *)&out[179] >= (char *)bl
            && (char *)&out[179] < (char *)&bl[BCAP]) ? "INSIDE" : "OUTSIDE");
}
__attribute__((noinline)) static void one(void) {
    uint64_t out[OUTCAP]; out[0] = 1;
    printf("  one array (a REDUCTION that drops bl): out=%%p, out[%%d] is at +%%d"
           " bytes -- straight into the saved registers, canary and return address\n",
           (void *)out, OUTCAP, OUTCAP * 8);
}
int main(void) { two(); one(); return 0; }
""" % {"OUTCAP": OUTCAP, "BCAP": BCAP}


def build_run(src, name, cc, flags, args=()):
    os.makedirs(SCRATCH, exist_ok=True)
    c = os.path.join(SCRATCH, name + ".c")
    b = os.path.join(SCRATCH, name)
    open(c, "w").write(src)
    r = subprocess.run([cc, "-std=c99"] + flags + [c, "-o", b],
                       capture_output=True, text=True)
    if r.returncode:
        return None, f"BUILD FAIL: {r.stderr.strip()[-300:]}"
    p = subprocess.run([b] + list(args), capture_output=True, text=True)
    for f in (c, b):
        try:
            os.unlink(f)
        except OSError:
            pass
    return p.returncode, (p.stdout + p.stderr).strip()


def do_clamp():
    print("=== A. the CLAMPED spelling under ASan + UBSan "
          "(../NOTES.md 0a run D) ===")
    print("    If this is exit 0 with both sanitizers silent, p46's "
          "memory-unsafe framing")
    print("    is CONDITIONAL and the clamp is `forbidden` for a measured "
          "reason.\n")
    flags = ["-O1", "-g", "-fsanitize=address,undefined",
             "-static-libasan", "-static-libubsan"]
    for (n, m) in ((48, 48), (120, 120), (200, 55)):
        rc, out = build_run(CLAMP_C, "p46_clamp", GCC, flags, (str(n), str(m)))
        print(f"  gcc -O1 ASan+UBSan  n={n} m={m}  exit={rc}")
        for line in out.splitlines()[:8]:
            print("    " + line)


def do_layout():
    print("=== B. frame layout of the shipped kernel's two arrays "
          "(../NOTES.md 0a) ===")
    for cc in (GCC, CLANG):
        for O in ("-O0", "-O3"):
            rc, out = build_run(LAYOUT_C, "p46_layout", cc, [O])
            print(f"  --- {os.path.basename(cc)} {O}   exit={rc}")
            for line in out.splitlines():
                print("  " + line)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clamp", action="store_true")
    ap.add_argument("--layout", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if not (a.clamp or a.layout or a.all):
        ap.print_help()
        return
    if a.clamp or a.all:
        do_clamp()
    if a.layout or a.all:
        if a.clamp or a.all:
            print()
        do_layout()


if __name__ == "__main__":
    main()
