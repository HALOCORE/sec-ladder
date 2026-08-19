/* p07 rung R1 -- idiomatic C99 binary search. THE BUG.
 *
 * CWE-129: the declared element count is trusted against the buffer that
 * actually arrived. A header says the window holds `n` sorted u32s and `nq`
 * queries; this rung searches `n` of them without checking that `4*n + 4*nq`
 * bytes are present.
 *
 * The single `(void)` cast is half the finding: the size is *right there* in
 * the signature. R1 has it and does not look; R1h (kernel_hardened.c) is this
 * file plus one line. Everything else about the two cells -- signature, calling
 * convention, the `n == 0 || nq == 0` test, the search, the fold, the return --
 * is identical, so R1-vs-R1h is the cost of the check and nothing else.
 *
 * Note what this rung *keeps*: `len < 8` and `n == 0 || nq == 0`. The first is
 * what makes reading the header itself defined; the second is dead in the
 * half-open spelling and kept anyway (see ../spec.md, "The zero guard is dead
 * here, and that is the result"). What it drops is the one line marked below.
 *
 * **Why the search is a jump and not a walk.** p16's and p05's missing checks
 * produce a *forward sequential* overrun -- the first byte read out of bounds
 * is one past the end, and the walk escalates. Binary search's first probe is
 * at element `n/2`, so R1's first out-of-bounds access is `2*n` bytes past the
 * window with nothing touched in between. It is the wildest single read this
 * project has modelled, and ../NOTES.md 7 records whether that made it easier
 * for a sanitiser to catch than p02's one-byte overflow (p02's whole result is
 * that a small overrun usually goes unnoticed).
 *
 * **Why the bounds are half-open.** `hi = n`, `while (lo < hi)`, `hi = mid` --
 * not the textbook `hi = n - 1`, `while (lo <= hi)`, `hi = mid - 1`. The
 * inclusive form underflows `size_t` at `mid == 0`, which is reached by any key
 * below `elements[0]`, i.e. on *well-formed* input with an ordinary miss
 * workload -- not adversarially. ../NOTES.md 6 derives that variant from this
 * file mechanically and measures what it does. The half-open form has no
 * subtraction anywhere that can underflow: `hi - lo > 0` inside the loop by the
 * loop condition, and nothing else subtracts.
 *
 * `mid = lo + (hi - lo) / 2` rather than `(lo + hi) / 2`: the overflow-safe
 * spelling, pinned as `idiom.required` in ../spec.md. With `size_t` indices and
 * a u32 count field the difference is unobservable at every representable input
 * (../NOTES.md 0 has the arithmetic), but it is the spelling this pattern is
 * about and a grep is what settles it.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + (found+1)`
 * and `n*nq` are the wrapping operations ../spec.md asks for with no special
 * spelling; `found + 1` with `found == UINT64_MAX` is 0, which is how "not
 * found" folds. Nothing here can overflow *signed*. The only undefined
 * behaviour this rung can execute is the out-of-bounds read itself. */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t n, nq, avail, q;
    uint64_t acc = 0;

    (void)buf_len; /* the size is right here ... and this rung never looks. */

    if (len < 8)
        return 0;
    n = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    nq = (size_t)buf[off + 4] + 256 * (size_t)buf[off + 5]
        + 65536 * (size_t)buf[off + 6] + 16777216 * (size_t)buf[off + 7];
    if (n == 0 || nq == 0)
        return 0;
    avail = len - 8;
    /* R1h has `if (4 * n + 4 * nq > avail) return 0;` here, and this rung does
     * not. That one line, in 64-bit arithmetic, is the whole difference.
     * `avail` is computed in both cells and consumed in only one, which is the
     * sharper version of the finding: this rung worked out how many bytes it
     * had and then indexed as if the header were true. (The dead store is
     * eliminated by every -O3 build, so the codegen delta is exactly the
     * comparison; the `(void)` is only to keep -Wextra quiet.) */
    (void)avail;

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
