/* p09 rung R1h -- kernel.c with the range check on the bit index.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 probes a bit index it never bounded because that is the
 * bug being modelled, and this cell does not, so that "C is faster" and "C is
 * unsafe" stop being confounded. R1-vs-R1h is what the check costs *within one
 * language*, with the signature, the calling convention, the header tests, the
 * length check, the decoders, the popcount pass and the return all held fixed.
 *
 * The diff against kernel.c is one `if` and its braces:
 *
 *     -        uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 6)));
 *     -        if (w & ((uint64_t)1 << (q & 63)))
 *     -            hits = hits + 1;
 *     -        acc = acc * 31 + w;
 *     +        if (q < nbits) {
 *     +            uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 6)));
 *     +            if (w & ((uint64_t)1 << (q & 63)))
 *     +                hits = hits + 1;
 *     +            acc = acc * 31 + w;
 *     +        }
 *
 * **What this cell does NOT add is a check on the buffer.** The length check
 * `8*nwords + 4*nq > avail` is in kernel.c too and is correct there;
 * `adversarial-count.bin` is the row that shows it fires in every rung. What
 * this cell adds is a check on a *value*, and the access it protects is two
 * operators away from that value -- the guard is `q < nbits` and the access is
 * `words[q >> 6]`. Whether a middle-end can connect the two is the whole of
 * ../NOTES.md 4.
 *
 * There is no subtraction-first subtlety of the kind p02 and p16 needed:
 * `len - 8` cannot underflow because `len >= 8` is tested above it.
 *
 * The decoders and the popcount pass are byte-identical to kernel.c's, so the
 * intrinsic comparison in ../NOTES.md 3d is unaffected by which C cell it is
 * read on. */
#include "kernel.h"

#define SLB_AI __attribute__((always_inline)) static inline

SLB_AI uint64_t load_u32(const uint8_t *b, size_t p)
{
    return (uint64_t)b[p] + 256 * (uint64_t)b[p + 1]
        + 65536 * (uint64_t)b[p + 2] + 16777216 * (uint64_t)b[p + 3];
}

SLB_AI uint64_t load_u64(const uint8_t *b, size_t p)
{
    return (uint64_t)b[p] + 256 * (uint64_t)b[p + 1]
        + 65536 * (uint64_t)b[p + 2] + 16777216 * (uint64_t)b[p + 3]
        + 4294967296ULL * (uint64_t)b[p + 4]
        + 1099511627776ULL * (uint64_t)b[p + 5]
        + 281474976710656ULL * (uint64_t)b[p + 6]
        + 72057594037927936ULL * (uint64_t)b[p + 7];
}

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint64_t nbits, nq, nwords, acc = 0, hits = 0, k, i;
    size_t ws, qs;

    (void)buf_len;

    if (len < 8)
        return 0;
    nbits = load_u32(buf, off);
    nq = load_u32(buf, off + 4);
    if (nbits == 0 || nq == 0)
        return 0;
    nwords = (nbits + 63) >> 6;
    if (8 * nwords + 4 * nq > (uint64_t)(len - 8))
        return 0;

    ws = off + 8;
    qs = ws + (size_t)(8 * nwords);
    for (k = 0; k < nq; k++) {
        uint64_t q = load_u32(buf, qs + (size_t)(4 * k));
        /* THE GUARD. A range check on a VALUE, not a bound on an index. */
        if (q < nbits) {
            uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 6)));
            if (w & ((uint64_t)1 << (q & 63)))
                hits = hits + 1;
            acc = acc * 31 + w;
        }
    }
    acc = acc * 31 + hits;
    for (i = 0; i < nwords; i++)
        acc = acc * 31
            + (uint64_t)__builtin_popcountll(load_u64(buf, ws + (size_t)(8 * i)));
    return (acc * 31 + nbits) * 31 + nq;
}
