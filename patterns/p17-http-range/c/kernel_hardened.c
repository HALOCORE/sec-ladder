/* p17 rung R1h -- kernel.c plus the one bounds check a careful C programmer
 * writes. This is nginx commit d289616b0, "Range filter: avoid negative range
 * start", expressed as a rejection rather than as a clamp.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 omits the check because that is the bug being modelled,
 * and this cell includes it, so that "C is faster" and "C is unsafe" stop being
 * confounded. R1-vs-R1h is what the check costs *within one language*, with the
 * signature, the calling convention, the header test, the fold and the return
 * all held fixed. The diff against kernel.c is one conjunct.
 *
 * **This conjunct is the only thing in the whole ladder that fixes both harms.**
 * A bounds check -- C's, safe Rust's, or a Verus proof that every access is in
 * bounds -- rejects `s > len`, which reads before the allocation. None of them
 * rejects `content_len < s <= len`, which reads the window's own suffix table
 * from an index that is perfectly inside the buffer. `start >= 0` is what
 * separates "the request names bytes of the body" from "the request names bytes
 * of something else", and that is a *functional* property, not a memory-safety
 * one. It is identical in C and in Rust, and it costs the same in both.
 *
 * `start >= 0` rather than `start >= 0L` or a clamp: `start` is already
 * `int64_t`, the comparison is exact, and it cannot overflow. Compare p16 and
 * p02, where the check had to be written subtraction-first to keep an *unsigned*
 * expression from wrapping; there is no such subtlety here, because the whole
 * point of this pattern is that the arithmetic is signed and the danger is a
 * value that is representable, negative, and never tested. */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t nsuf, body_start, i;
    int64_t content_len;
    uint64_t acc = 0;
    uint64_t nserved = 0;

    (void)buf_len;

    if (len < 2)
        return 0;
    nsuf = (size_t)buf[off] + 256 * (size_t)buf[off + 1];
    if (2 + 2 * nsuf > len)
        return 0;
    body_start = 2 + 2 * nsuf;
    content_len = (int64_t)(len - body_start);

    for (i = 0; i < nsuf; i++) {
        int64_t s, start, end, base, n, j;
        s = (int64_t)buf[off + 2 + 2 * i] + 256 * (int64_t)buf[off + 3 + 2 * i];
        start = content_len - s;
        end = content_len;
        if (start < end && start >= 0) {
            base = (int64_t)(off + body_start) + start;
            n = end - start;
            for (j = 0; j < n; j++)
                acc = acc * 31 + buf[base + j];
            nserved = nserved + 1;
        }
    }
    return acc * 31 + nserved;
}
