/* p02 rung R1h -- kernel.c plus the bounds check a careful C programmer writes.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 omits the check because that is the bug being modelled,
 * and this cell includes it, so that "C is faster" and "C is unsafe" stop being
 * confounded. R1-vs-R1h is what the check costs *within one language*, with the
 * signature, the calling convention, the memcpy and the fold all held fixed.
 *
 * The check is written subtraction-first -- `len > src_len - (src_off + 2)`
 * rather than `src_off + 2 + len > src_len` -- because the additive form can
 * itself overflow `size_t` and wave the attack through. The subtraction cannot
 * underflow: `src_off + 2 <= src_len` is the caller's structural precondition,
 * shared by every rung in this pattern and checked by none of them (rung 5
 * proves it at the call site instead of checking it). The Rust rungs spell the
 * identical three-term test; see ../spec.md. */
#include "kernel.h"

#include <string.h>

SLB_NOINLINE uint64_t kernel(const uint8_t *src, size_t src_len, size_t src_off,
                             uint8_t *dst, size_t dst_cap)
{
    size_t len = (size_t)src[src_off] + 256 * (size_t)src[src_off + 1];
    uint64_t acc = 0;
    size_t i;

    if (len > dst_cap || len > src_len - (src_off + 2))
        return 0;

    memcpy(dst, src + src_off + 2, len);
    for (i = 0; i < len; i++)
        acc += dst[i];
    return acc;
}
