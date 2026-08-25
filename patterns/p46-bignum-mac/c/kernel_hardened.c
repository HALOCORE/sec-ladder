/* p46 rung R1h -- the same C kernel WITH the output-side bound.
 *
 * `.memory/01-ladder.md`: ship this for every pattern that models a bug, or
 * *"C is faster"* and *"C is unsafe"* become the same sentence. Any C-vs-Rust
 * comparison on this pattern must use `c-gcc-h` / `c-clang-h`.
 *
 * The diff against c/kernel.c is the two lines below and nothing else.
 *
 * This is `bn_wexpand(rr, top)` from OpenSSL's `BN_mul()`, reduced to the one
 * fixed-capacity buffer this pattern has: refuse the operands whose product
 * cannot fit, rather than growing the buffer, because the buffer here is
 * automatic and cannot grow.
 *
 * ⚠ **The hardened rung's cost is ONE COMPARISON PER CALL, while safe Rust's
 * per-access checks are THREE PER MAC STEP -- O(n*m).** That asymmetry is the
 * same shape as p19's `O(table)`-vs-`O(message)` one and it is sharper here:
 * the C check is O(1), not O(table). The whole of R1h's safety cost is a
 * `cmp`/`ja` pair executed once per kernel call, against `7*n*m + 7*n + 5`
 * instructions for the naive safe rung (../NOTES.md 8).
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

    /* >>> THE SAFETY LINE. The declared product must fit in the scratch;
     * after this test `i + j <= n + m - 2 < SLB_P46_OUTCAP` for every step of
     * the loops below, which is exactly what ../verus.rs proves. <<< */
    if (n + m > SLB_P46_OUTCAP)
        return SLB_P46_REJ;

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
