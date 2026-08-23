/* p36 rung R1h -- THE FIX: one source-level range test on the opcode.
 *
 * Character-identical to c/kernel.c except for the three lines around the
 * dispatch:
 *
 *     c/kernel.c            acc = TABLE[op](acc ^ (uint64_t)arg);
 *     c/kernel_hardened.c   if (op < SLB_P36_NOPS)
 *                               acc = TABLE[op](acc ^ (uint64_t)arg);
 *                           else
 *                               acc = acc * 31 + SLB_P36_SENT;
 *
 * `diff c/kernel.c c/kernel_hardened.c` shows that hunk and the comments, and
 * nothing else.
 *
 * ⚠ **THE REAL-WORLD HARDENED ANSWER FOR THIS BUG CLASS IS A COMPILER
 * MITIGATION THIS MATRIX CANNOT PRICE, AND SAYING SO IS PART OF THE RESULT.**
 * What actually ships against forged indirect calls is control-flow integrity
 * -- `-fsanitize=cfi-icall` on clang, `-mbranch-protection`/IBT in hardware --
 * and none of it is available as a rung here:
 *
 *   * `-fsanitize=cfi` needs `-flto` and is clang-only, so it is a
 *     `harness/build.py` change, and `build.py` is hashed into the MEASUREMENT
 *     records, not merely the gate records: one flag would cost a full
 *     re-measure of all 22 patterns (RECAP, settled answer 4);
 *   * it is a *whole-program* property, so an `isolated` build -- half this
 *     project's matrix -- cannot express it at all;
 *   * gcc 13.3.0 on this box does not implement `-fsanitize=cfi` and does not
 *     even accept `-fsanitize=function` (measured: `gcc: error: unrecognized
 *     argument to '-fsanitize=' option: 'function'`).
 *
 * So R1h is the *source-level* answer -- the check a programmer writes -- and
 * the compiler-level answer is measured in `controls/` and reported there, not
 * folded into the ladder. p36 therefore prices what a range test costs and
 * makes no claim at all about what CFI costs.
 *
 * Everything else about this file -- the op set, the table, the header decode,
 * the cursor guard and the fold -- is c/kernel.c's. */
#include "kernel.h"

/* THE OP SET, byte-identical to c/kernel.c's. */
static uint64_t op0(uint64_t x) { return x ^ 0x9e3779b97f4a7c15ULL; }
static uint64_t op1(uint64_t x) { return x ^ 0xff51afd7ed558ccdULL; }
static uint64_t op2(uint64_t x) { return x + 0x2545f4914f6cdd1dULL; }
static uint64_t op3(uint64_t x) { return x + 0xc4ceb9fe1a85ec53ULL; }
static uint64_t op4(uint64_t x) { return x - 0x61c8864680b583ebULL; }
static uint64_t op5(uint64_t x) { return x - 0xbf58476d1ce4e5b9ULL; }
static uint64_t op6(uint64_t x) { return x ^ 0x94d049bb133111ebULL; }
static uint64_t op7(uint64_t x) { return x + 0x9e6c63d0676a9a99ULL; }

/* THE TABLE, byte-identical to c/kernel.c's. */
static uint64_t (*const TABLE[SLB_P36_NOPS])(uint64_t) = {
    op0, op1, op2, op3, op4, op5, op6, op7,
};

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t nrec, p, t;
    uint64_t acc = 0;
    uint8_t op, arg;

    (void)buf_len; /* p36's bound is the window's and the table's. */

    if (len < 4)
        return 0;
    nrec = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nrec == 0)
        return 0;

    p = 4;
    t = 0;
    while (t < nrec) {
        if (len - p < 2)
            break;
        op = buf[off + p];
        arg = buf[off + p + 1];
        p = p + 2;
        /* >>> THE SAFETY LINE. This is the whole of what c/kernel.c omits. <<< */
        if (op < SLB_P36_NOPS)
            acc = TABLE[op](acc ^ (uint64_t)arg);
        else
            acc = acc * 31 + SLB_P36_SENT;
        t = t + 1;
    }
    return acc * 31 + (uint64_t)t;
}
