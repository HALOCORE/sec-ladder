/* p07 rung R1h -- kernel.c plus the one line a careful C programmer writes.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 omits the check because that is the bug being modelled,
 * and this cell includes it, so that "C is faster" and "C is unsafe" stop being
 * confounded. R1-vs-R1h is what the check costs *within one language*, with the
 * signature, the calling convention, the header tests, the search, the fold and
 * the return all held fixed. The diff against kernel.c is one `if`.
 *
 * **The width is the whole subtlety, and it is NOT p05's width.** `n` and `nq`
 * are u32 header fields, so `4*n + 4*nq` reaches
 *
 *     4 * 4294967295 + 4 * 4294967295 = 34 359 738 360
 *
 * which needs 36 bits. In `size_t` (64-bit here) the line below is exact. Write
 * the same line with 32-bit unsigned dimensions and it becomes
 *
 *     if (4u * (uint32_t)n + 4u * (uint32_t)nq > (uint32_t)avail) return 0;
 *
 * whose left-hand side is 4 for n = 2^30, nq = 1 -- the product wraps to zero,
 * `4 > avail` is false on any window bigger than 12 bytes, and the attack goes
 * straight through a check that *looks* right. `adversarial-width.bin` is that
 * input and NOTES.md 6 builds the wrong-width cell and measures it.
 *
 * Note how this differs from p05, because "do the check in 64 bits" is advice
 * whose force depends on the header field width and the two patterns sit on
 * opposite sides of the boundary:
 *
 *   p05  u16 dimensions, product `nrow*ncol` <= 4 294 836 225
 *        -> FITS uint32_t; only the *signed* 32-bit spelling breaks.
 *   p07  u32 count fields, `4*n + 4*nq` <= 34 359 738 360
 *        -> does NOT fit uint32_t; the *unsigned* 32-bit spelling breaks too.
 *
 * There is no subtraction-first subtlety of the kind p02 and p16 needed.
 * `avail = len - 8` cannot underflow because `len >= 8` was tested two lines
 * above, and the comparison is `need > avail` rather than
 * `need > len - 8 - something`, so nothing wraps. The danger in this pattern is
 * a *multiplication* that is too wide for the type it is done in -- and, one
 * spelling away, a *subtraction* in the loop bound, which the half-open form in
 * kernel.c removes and NOTES.md 6 puts back. */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t n, nq, avail, q;
    uint64_t acc = 0;

    (void)buf_len;

    if (len < 8)
        return 0;
    n = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    nq = (size_t)buf[off + 4] + 256 * (size_t)buf[off + 5]
        + 65536 * (size_t)buf[off + 6] + 16777216 * (size_t)buf[off + 7];
    if (n == 0 || nq == 0)
        return 0;
    avail = len - 8;
    if (4 * n + 4 * nq > avail)
        return 0;

    for (q = 0; q < nq; q++) {
        size_t kp = off + 8 + 4 * n + 4 * q;
        uint32_t key = (uint32_t)buf[kp] + 256 * (uint32_t)buf[kp + 1]
            + 65536 * (uint32_t)buf[kp + 2] + 16777216 * (uint32_t)buf[kp + 3];
        size_t lo = 0;
        size_t hi = n;
        uint64_t found = UINT64_MAX;
        while (lo < hi) {
            size_t mid = lo + (hi - lo) / 2;
            size_t ep = off + 8 + 4 * mid;
            uint32_t v = (uint32_t)buf[ep] + 256 * (uint32_t)buf[ep + 1]
                + 65536 * (uint32_t)buf[ep + 2] + 16777216 * (uint32_t)buf[ep + 3];
            if (v == key) {
                found = (uint64_t)mid;
                break;
            }
            if (v < key)
                lo = mid + 1;
            else
                hi = mid;
        }
        acc = acc * 31 + (found + 1);
    }
    return acc * 31 + (uint64_t)n * (uint64_t)nq;
}
