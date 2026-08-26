/* p23 rung R1h -- c/kernel.c plus TWO CONJUNCTS, and nothing else.
 *
 * Diff this file against c/kernel.c: the only differences are the two `i < j &&`
 * conjuncts on the inner scan conditions, and the comments that say so. Same
 * signature, same clamp, same cursor guards, same outer loop, same swap, same
 * fold, same return expression. So `c-gcc-h` minus `c-gcc` is the price of the
 * scan guard and of nothing else.
 *
 * **The guard is `i < j`, and the alternative `i < m` / `j > 0` is EQUIVALENT,
 * not weaker.** An earlier draft of this comment said the alternative was
 * *"safe, and wrong"* -- that the upward cursor could pass the downward one and
 * return a partition point outside the live prefix. ⚠ **That was FALSE and
 * `controls/guard_equiv.py` refuted it before this file was measured**: the two
 * spellings agree on 800 000 randomised records, over a full and a narrow
 * alphabet. The invariant the draft missed is one line -- after an exchange
 * `scr[j] > pv`, because that is the element the exchange just put there, so
 * the next upward scan stops at or before `j` whatever its guard says, and
 * symmetrically `scr[i-1] < pv` stops the downward scan at or above `i`. The
 * cursors cannot cross. So `../spec.md` pins a SPELLING here and not a
 * semantics, and it says so; `../NOTES.md 8` has the measurement and the price.
 *
 * **What is NOT equivalent is having no guard at all**, which is c/kernel.c.
 *
 * **This is a READ guard that also stops a WRITE.** The scans only read; the
 * swap writes, and it is already guarded by `if (i < j)`. What makes R1's swap
 * dangerous is that R1 can reach it with `j` WRAPPED -- the downward scan
 * decrements past 0 and `i < j` is then true for a wild `j` -- so the write is
 * out of bounds because the READ guard was missing, one loop earlier. That is
 * why `.memory/02-bench-rules.md`'s write rule reaches p23: the threshold the
 * scan guard enforces IS the scratch's live extent.
 *
 * Everything else about this cell -- and the comment above every line of it --
 * is c/kernel.c's. Read that file for why the kernel is shaped this way. */
#include <string.h>

#include "kernel.h"

#define SCR 64

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t scr[SCR];
    size_t nrec, rec, p, q, i, j, nelem, m;
    uint64_t acc = 0;
    uint8_t pv, t;

    (void)buf_len; /* p23's bound is not this one -- it is the two cursors. */

    if (len < 4)
        return 0;
    nrec = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nrec == 0)
        return 0;

    memset(scr, 0, sizeof scr);
    p = 4;
    for (rec = 0; rec < nrec; rec++) {
        if (len - p < 8)
            break;
        nelem = (size_t)buf[off + p] + 256 * (size_t)buf[off + p + 1]
            + 65536 * (size_t)buf[off + p + 2]
            + 16777216 * (size_t)buf[off + p + 3];
        pv = buf[off + p + 4];
        p += 8;
        m = nelem < SCR ? nelem : SCR;
        if (len - p < nelem)
            break;
        memcpy(scr, buf + off + p, m);
        p += nelem;
        i = 0;
        j = m;
        while (i < j) {
            /* THE SAFETY LINE, half 1. c/kernel.c omits the `i < j &&`. */
            while (i < j && scr[i] <= pv)
                i++;
            /* THE SAFETY LINE, half 2. c/kernel.c omits the `i < j &&`. */
            while (i < j && scr[j - 1] >= pv)
                j--;
            if (i < j) {
                t = scr[i];
                scr[i] = scr[j - 1];
                scr[j - 1] = t;
                i++;
                j--;
            }
        }
        for (q = 0; q < m; q++)
            acc = acc * 31 + (uint64_t)scr[q];
        acc = acc * 31 + (uint64_t)i;
    }
    return acc * 31 + (uint64_t)nrec;
}
