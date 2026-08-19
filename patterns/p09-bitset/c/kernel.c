/* p09 rung R1 -- idiomatic C99 bitset probe. THE BUG.
 *
 * CWE-125 via a missing range check on the bit index. The window declares a bit
 * count and a query count; each query is a bit index and the kernel reports the
 * word it lives in. This rung checks the *shape* of the window -- the length
 * check `8*nwords + 4*nq > avail` is here, and it is right -- and does not
 * check the *bit index* against `nbits`.
 *
 * That asymmetry is not a strawman, it is the shape the mistake actually takes.
 * The programmer validates the buffer, because the buffer is what the API hands
 * them, and then trusts the index because "the queries came from the same
 * file". `q` is a `uint32_t`, so `q >> 6` is a word index up to 67 108 863 and
 * `words + 8*(q>>6)` reaches half a gigabyte past the blob. It faults or it
 * reads a neighbour, depending on the value -- ../NOTES.md 7 measures both.
 *
 * **What is NOT wrong here is the buffer arithmetic.** Every index this file
 * forms is derived correctly from the header it read; `(void)buf_len` is half
 * the finding, as it is in p03 and p11. The check that is missing is on a value
 * the *file* supplies, and the access it protects is two operators away from
 * it: the guard would be on `q` and the access is on `q >> 6`.
 *
 * R1h (kernel_hardened.c) is this file with `if (q < nbits) { ... }` around the
 * probe body and nothing else -- same signature, same calling convention, same
 * `len < 8` test, same zero tests, same length check, same popcount pass, same
 * return -- so R1-vs-R1h is the cost of the range check and nothing else.
 * ../NOTES.md 3 measures it per guarded query.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9), so `acc * 31 + w` and
 * `(acc * 31 + nbits) * 31 + nq` are the wrapping operations ../spec.md asks
 * for. The only undefined behaviour this rung can execute is the out-of-bounds
 * read itself.
 *
 * `__builtin_popcountll` is the intrinsic ../NOTES.md 3d prices against Rust's
 * `u64::count_ones()`. Whether it lowers to a `popcnt` instruction or to a
 * libgcc call depends on `-march`, which this repo does not set -- so that
 * comparison is a LIBRARY/ISA comparison and ../NOTES.md 3d keeps it separate
 * from every safety number (`.memory/03-measurement.md`, p11's rule). */
#include "kernel.h"

#define SLB_AI __attribute__((always_inline)) static inline

/* The little-endian decoders, shared by both loops and by both C rungs.
 * `always_inline` so that the kernel-exclusive `Ir` column does not silently
 * lose the loads at `-O0` (`.memory/03-measurement.md`). */
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

    (void)buf_len; /* the size is right here ... and it is not the problem. */

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
        /* THE GUARD `if (q < nbits)` is missing here, and that is the whole
         * diff against kernel_hardened.c. */
        uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 6)));
        if (w & ((uint64_t)1 << (q & 63)))
            hits = hits + 1;
        acc = acc * 31 + w;
    }
    acc = acc * 31 + hits;
    /* THE POPCOUNT PASS. Its index is linear in `i`; the query loop's came
     * through a shift. Same array, same decoder, same fold. */
    for (i = 0; i < nwords; i++)
        acc = acc * 31
            + (uint64_t)__builtin_popcountll(load_u64(buf, ws + (size_t)(8 * i)));
    return (acc * 31 + nbits) * 31 + nq;
}
