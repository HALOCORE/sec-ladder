/* p19 rung R1h -- the same C kernel WITH the validation pass.
 *
 * `.memory/01-ladder.md`: ship this for every pattern that models a bug, or
 * *"C is faster"* and *"C is unsafe"* become the same sentence. Here that
 * warning is unusually sharp, because R1 does not merely skip a per-byte test:
 * it skips **2048 byte comparisons per call** that every other rung pays. Any
 * C-vs-Rust comparison on this pattern must use `c-gcc-h` / `c-clang-h`.
 *
 * The diff against c/kernel.c is the eight lines below and nothing else.
 *
 * This is `verify_dfa()` from `security/apparmor/match.c`, reduced to the one
 * table this pattern has:
 *
 *     for (i = 0; i < trans_count; i++)
 *         if (NEXT_TABLE(dfa)[i] >= state_count) goto out;
 *
 * ⚠ **The hardened rung's cost is O(table) ONCE PER CALL, while safe Rust's
 * per-access check is O(message) PER BYTE.** That asymmetry is p19's second
 * result and it is why the two hardening strategies are not interchangeable:
 * validation amortises in the message length and a bounds check does not.
 */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    const uint8_t *w = buf + off;
    uint64_t acc = 0;
    size_t p;
    size_t st = 0;

    if (len <= SLB_P19_TBL)
        return 0;

    /* >>> THE SAFETY LINE. Every transition entry must name a state that
     * exists; after this loop `st < SLB_P19_NST` is an invariant of the fold
     * below, which is exactly what ../verus.rs proves. <<< */
    for (p = 0; p < SLB_P19_TBL; p++) {
        if (w[p] >= SLB_P19_NST)
            return SLB_P19_REJ;
    }

    for (p = SLB_P19_TBL; p < len; p++) {
        st = w[st * 256 + w[p]];
        acc = acc * 31 + st;
    }
    return acc * 31 + st;
}
