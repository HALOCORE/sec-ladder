/* p01 rung R1 -- idiomatic C99 array sum over a window.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so this is the wrapping
 * sum ../spec.md asks for with no special spelling. There is no bounds check
 * because there is nothing to check against: the caller's promise that
 * off + len <= v_len is the whole contract, and C has no way to state it. */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint64_t *v, size_t off, size_t len)
{
    uint64_t acc = 0;
    size_t i;
    for (i = 0; i < len; i++)
        acc += v[off + i];
    return acc;
}
