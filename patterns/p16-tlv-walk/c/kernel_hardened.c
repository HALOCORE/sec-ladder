/* p16 rung R1h -- kernel.c plus the one bounds check a careful C programmer
 * writes.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 omits the check because that is the bug being modelled,
 * and this cell includes it, so that "C is faster" and "C is unsafe" stop being
 * confounded. R1-vs-R1h is what the check costs *within one language*, with the
 * signature, the calling convention, the header test, the fold and the return
 * all held fixed. The diff against kernel.c is three lines.
 *
 * Both comparisons are written subtraction-first -- `end - p >= 3` rather than
 * `p + 3 <= end`, and `vlen > end - (p + 3)` rather than `p + 3 + vlen > end`.
 * The additive spellings can overflow `size_t` on an attacker-chosen `vlen`
 * (up to 65535) and wave the attack straight through. Neither subtraction can
 * underflow *in this rung*, because `p <= end` and `p + 3 <= end` are loop
 * invariants that the check below is what maintains -- which is exactly why
 * deleting it (kernel.c) makes the same expression underflow. Every rung spells
 * the identical two tests; see ../spec.md. */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t p = off;
    size_t end = off + len;
    uint64_t acc = 0;
    uint64_t nrec = 0;

    (void)buf_len;

    while (end - p >= 3) {
        size_t vlen, j;
        acc = acc * 31 + buf[p];
        vlen = (size_t)buf[p + 1] + 256 * (size_t)buf[p + 2];
        if (vlen > end - (p + 3))
            break;
        for (j = 0; j < vlen; j++)
            acc = acc * 31 + buf[p + 3 + j];
        p = p + 3 + vlen;
        nrec = nrec + 1;
    }
    return acc * 31 + nrec;
}
