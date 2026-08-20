/* p13 rung R1h -- kernel.c with the line `strncpy` does not write for you.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 trusts that `strncpy` terminated the destination because
 * that is the bug being modelled, and this cell does not, so that "C is faster"
 * and "C is unsafe" stop being confounded. R1-vs-R1h is what the termination
 * costs *within one language*, with the signature, the calling convention, the
 * header test, the scan, the copy, the zero-fill, the consumer, the fold, the
 * cursor and the return all held fixed. The diff against kernel.c is one
 * statement.
 *
 * **This is the first safety tax in this project that is not a
 * compare-and-branch.** It is one unconditional STORE per string. Whether that
 * is measurable at all was settled BEFORE the rungs were written
 * (`.temp/p13/phase0/`, ../NOTES.md 0): the answer is **+1 instruction in every
 * build and exactly +1.0000 Ir per string on both compilers**, including on the
 * path where the zero-fill runs and could have absorbed it by dead-store
 * elimination. Neither gcc nor clang sinks it into the fill.
 *
 * **What this cell does NOT add: a bound on the consumer.** `d = 0; while
 * (dst[d] != 0) d++;` is unchanged, and it is safe here *because* of the store
 * above it, not because it was rewritten -- which is the point of the pattern:
 * the obligation is at the read and what discharges it is an invariant
 * established at the write. A rung that bounded the consumer instead would be
 * modelling a different (and easier) fix, and it would also stop being a
 * matched spelling against R1.
 *
 * **And what it does NOT fix: the truncation.** `n = min(slen, DST_CAP)` is
 * unchanged, so this cell still silently discards everything past `DST_CAP`
 * and still reports `d == DST_CAP - 1` for a 32-byte string and for a
 * 4096-byte one alike. `adversarial-exact` (31-byte strings),
 * `adversarial-truncate` (32) and `adversarial-truncate-alt` (40) print the
 * **same checksum** in this cell and in every checked rung. That is the second
 * harm, it is memory-safe, and no rung of this ladder is free of it. */
#include "kernel.h"

#define DST_CAP 32

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t dst[DST_CAP];
    size_t nstr, s, p, q, i, slen, n, d;
    uint64_t acc = 0;

    (void)buf_len;

    if (len < 4)
        return 0;
    nstr = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nstr == 0)
        return 0;

    p = 4;
    for (s = 0; s < nstr; s++) {
        q = p;
        while (q < len) {
            if (buf[off + q] == 0)
                break;
            q = q + 1;
        }
        slen = q - p;
        n = slen < DST_CAP ? slen : DST_CAP;
        for (i = 0; i < n; i++)
            dst[i] = buf[off + p + i];
        for (i = n; i < DST_CAP; i++)
            dst[i] = 0;
        /* THE TERMINATION. One unconditional store, and the whole diff. */
        dst[DST_CAP - 1] = 0;
        d = 0;
        while (dst[d] != 0)
            d = d + 1;
        acc = acc * 31 + (uint64_t)d;
        for (i = 0; i < DST_CAP; i++)
            acc = acc * 31 + (uint64_t)dst[i];
        if (q >= len)
            break;
        p = q + 1;
        if (p >= len)
            break;
    }
    return acc * 31 + (uint64_t)nstr;
}
