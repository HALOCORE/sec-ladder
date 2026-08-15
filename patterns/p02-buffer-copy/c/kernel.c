/* p02 rung R1 -- idiomatic C99 length-prefixed record copy. THE BUG.
 *
 * This is CWE-787 as it is actually written: the wire says how many bytes
 * follow, the code believes it, and `memcpy` does what it is told. Nothing here
 * is contrived -- it is the shortest correct-looking way to write "copy the
 * record at src_off into my buffer", and it is wrong for exactly one reason:
 * `len` is attacker data and `dst_cap` is never consulted.
 *
 * The two `(void)` casts are the whole finding in two lines. The sizes are
 * *right there* in the signature. R1 has them and does not look; R1h
 * (kernel_hardened.c) is this file plus the three-term check. Everything else
 * about the two cells -- signature, calling convention, memcpy, the fold --
 * is identical, so R1-vs-R1h is the cost of the check and nothing else.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so the fold is the
 * wrapping sum ../spec.md asks for with no special spelling. */
#include "kernel.h"

#include <string.h>

SLB_NOINLINE uint64_t kernel(const uint8_t *src, size_t src_len, size_t src_off,
                             uint8_t *dst, size_t dst_cap)
{
    size_t len = (size_t)src[src_off] + 256 * (size_t)src[src_off + 1];
    uint64_t acc = 0;
    size_t i;

    (void)src_len; /* the sizes are right here ... */
    (void)dst_cap; /* ... and this rung never looks at them. That is the bug. */

    memcpy(dst, src + src_off + 2, len);
    for (i = 0; i < len; i++)
        acc += dst[i];
    return acc;
}
