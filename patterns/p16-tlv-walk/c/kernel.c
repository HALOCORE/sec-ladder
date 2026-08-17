/* p16 rung R1 -- idiomatic C99 TLV record walker. THE BUG.
 *
 * This is CWE-125, out-of-bounds READ, as it is actually written: the wire says
 * how long the value is, the walker believes it, and the fold reads that many
 * bytes. Nothing here is contrived -- it is the shortest correct-looking way to
 * write "walk the records in this window", and it is wrong for exactly one
 * reason: `vlen` is attacker data and `end` is never consulted before the fold.
 *
 * The single `(void)` cast is half the finding: the size is *right there* in the
 * signature. R1 has it and does not look; R1h (kernel_hardened.c) is this file
 * plus one `if`. Everything else about the two cells -- signature, calling
 * convention, the header test, the fold, the return -- is identical, so
 * R1-vs-R1h is the cost of the check and nothing else.
 *
 * Note what this rung *keeps*: `end - p >= 3`. Without it the walk reads a
 * header off the end on *every* input, well-formed ones included, and the
 * pattern stops being about the length field. What it drops is the one line
 * marked below.
 *
 * Two consequences of dropping it, and the second is the nastier one:
 *
 *   1. the fold reads `buf[p+3 .. p+3+vlen)`, which can run past `end` and past
 *      the end of the allocation -- the leak;
 *   2. `p` then advances past `end`, so `end - p` UNDERFLOWS `size_t` and the
 *      loop condition `end - p >= 3` stays true. The walk does not stop at the
 *      end of the buffer, it keeps parsing whatever is in memory next. That is
 *      why an OOB read in a chained parser is so much worse than a single
 *      mis-indexed load, and it is not a spelling accident: the subtraction-
 *      first comparison ../spec.md mandates is *sound* precisely because the
 *      check this rung deleted keeps `p <= end` an invariant.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc * 31 + b` and
 * `nrec + 1` are the wrapping operations ../spec.md asks for with no special
 * spelling. */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t p = off;
    size_t end = off + len;
    uint64_t acc = 0;
    uint64_t nrec = 0;

    (void)buf_len; /* the size is right here ... and this rung never looks. */

    while (end - p >= 3) {
        size_t vlen, j;
        acc = acc * 31 + buf[p];
        vlen = (size_t)buf[p + 1] + 256 * (size_t)buf[p + 2];
        /* R1h has, and this rung does not:
         *     if (vlen > end - (p + 3))
         *         break;
         */
        for (j = 0; j < vlen; j++)
            acc = acc * 31 + buf[p + 3 + j];
        p = p + 3 + vlen;
        nrec = nrec + 1;
    }
    return acc * 31 + nrec;
}
