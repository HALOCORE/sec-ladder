/* p46 rung R1 -- idiomatic C, and it carries the bug.
 *
 * THE BUG, in one sentence: the kernel checks that the declared operands FIT IN
 * THE INPUT and never checks that their product fits in the OUTPUT, so
 * `out[i + j]` writes past a 96-limb automatic array.
 *
 * That is the classic bignum miscount. OpenSSL's `bn_mul_normal()` writes
 * `na + nb` words into `r` and the caller is responsible for having sized `r`;
 * getting that sizing wrong is CVE-2021-3712's neighbour class, and it is why
 * `BN_mul()` calls `bn_wexpand(rr, top)` before it multiplies. This kernel is
 * that program with the expand removed.
 *
 * ⚠ **THE HARM IS LOUD HERE, AND THAT IS ITSELF THE MEASUREMENT.** p02's
 * result is that idiomatic C absorbs a one-byte HEAP overflow silently in seven
 * of eight builds. Move the same bug class onto the STACK and the distribution
 * inverts: on this box (Ubuntu, `gcc -Q --help=common` reports
 * `-fstack-protector-strong [enabled]` by default) five of six plain builds
 * abort or fault, and only one is silent (../NOTES.md 0a):
 *
 *     gcc   -O0/-O2/-O3   exit 134   *** stack smashing detected ***
 *     clang -O2/-O3       exit 139   SIGSEGV
 *     clang -O0, (n,m) = (97,1)   exit 0, WRONG ANSWER      <- the silent cell
 *
 * The canary fires AFTER the out-of-bounds writes have happened; it protects
 * the return address, not the object. ASan calls it what it is:
 * `stack-buffer-overflow`, `WRITE of size 8`.
 *
 * ⚠ **AND THE MEMORY-UNSAFE FRAMING IS CONDITIONAL** (kernel.h, ../NOTES.md
 * 0a). The identical miscount with a CLAMPED index -- `out[(i + j) % 96]` -- is
 * exit 0 with ASan and UBSan both silent: a wrong answer and no memory event.
 * The clamp is `forbidden` by name in ../spec.md for that reason.
 *
 * Idiomatic-C check (the reviewer checklist asks): this is how a schoolbook
 * limb multiply is written -- a `unsigned __int128` accumulator, a `uint64_t`
 * carry, one indexed read-modify-write per step. It is not Rust-in-C-syntax and
 * it is not pessimised: it is `bn_mul_add_words()`'s loop with the assembly
 * specialisation removed.
 */
#include <string.h>

#include "kernel.h"

/* Little-endian limb decode. The ADDITIVE spelling, not shift-or, because
 * ../verus.rs's spec function is additive and Verus would need a bit-vector
 * detour to relate a shift to it -- and a decoder that differs between rungs is
 * a rung difference in the wrong place. p09 spells it the same way in all six
 * of its rungs for the same reason; LLVM emits the same code for either. */
static uint64_t slb_p46_ld64(const uint8_t *p)
{
    return (uint64_t)p[0] + 256 * (uint64_t)p[1]
        + 65536 * (uint64_t)p[2] + 16777216 * (uint64_t)p[3]
        + 4294967296ULL * (uint64_t)p[4]
        + 1099511627776ULL * (uint64_t)p[5]
        + 281474976710656ULL * (uint64_t)p[6]
        + 72057594037927936ULL * (uint64_t)p[7];
}

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    const uint8_t *w = buf + off;
    uint64_t out[SLB_P46_OUTCAP];
    uint64_t bl[SLB_P46_BCAP];
    uint64_t acc = 0;
    size_t n, m, i, j, k;

    if (len < 8)
        return 0;
    n = w[0];
    m = w[1];
    if (n == 0 || m == 0)
        return 0;
    if (8 + 8 * (n + m) > len)
        return 0;

    /* >>> THE SAFETY LINE. c/kernel_hardened.c has the output-side bound
     * here and this file does not. That omission is the whole of the bug. <<< */

    for (j = 0; j < m; j++)
        bl[j] = slb_p46_ld64(w + 8 + 8 * (n + j));
    memset(out, 0, sizeof out);
    for (i = 0; i < n; i++) {
        uint64_t ai = slb_p46_ld64(w + 8 + 8 * i);
        uint64_t carry = 0;
        for (j = 0; j < m; j++) {
            unsigned __int128 t = (unsigned __int128)ai * bl[j] + out[i + j] + carry;
            out[i + j] = (uint64_t)t;
            carry = (uint64_t)(t >> 64);
        }
        out[i + m] = carry;
    }
    for (k = 0; k < n + m; k++)
        acc = acc * 31 + out[k];
    return (acc * 31 + n) * 31 + m;
}
