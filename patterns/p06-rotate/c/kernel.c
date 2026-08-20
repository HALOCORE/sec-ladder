/* p06 rung R1 -- idiomatic C99 in-place rotate. THE BUG.
 *
 * CWE-787 / CWE-125 / CWE-129. The window declares a rotate amount per record;
 * this rung rotates a 64-byte local scratch buffer left by that amount without
 * ever reducing it modulo the live extent. `r %= m` is the missing line and it
 * is the only missing line.
 *
 * **What this rung KEEPS.** The clamp `m = min(nelem, SCR)`, so the copy is
 * bounded; both cursor guards, so `p` never leaves the window; every source
 * index is correct. The whole of the bug is in the ROTATE.
 *
 * The rotate is spelled as three in-place reverses -- the standard C idiom,
 * `2m` element visits and no temporary buffer -- and each reverse is written
 * out as its own loop rather than called through a helper, so that the `kernel`
 * symbol contains all of it and `harness/asm.py`'s kernel-exclusive `Ir` column
 * is comparable across rungs (`.memory/03-measurement.md`: a helper that
 * survives at `-O0` would silently move work out of the symbol).
 *
 * **The second reverse is a no-op when `r > m`**, in this rung and in every
 * other, because `a < b` is false. That is not defensive coding, it is what
 * makes regime 1 well defined: with `m <= r <= SCR` the triple composes to
 * `scr[i] = old[r - m + i]`, a rotation of a window of the scratch the record
 * never wrote, which is a wrong answer and not a memory error.
 *
 * `memcpy` rather than a byte loop, in this rung and in every other, because
 * p02's retraction is the precedent: one operator flips `bulk_calls` and 100%
 * of the delta, and p06's measured difference must be the ROTATE. Whether -O3
 * turns any of the three reverse loops back into something else is measured on
 * the disassembly (../NOTES.md 1), not assumed -- it does not: three scalar
 * swap loops survive in both compilers.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). The undefined behaviour
 * this rung executes is the out-of-bounds read AND write that the first reverse
 * performs when `r > SCR`. */
#include <string.h>

#include "kernel.h"

#define SCR 64

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t scr[SCR];
    size_t nrec, rec, p, i, nelem, m, r, a, b;
    uint64_t acc = 0;
    uint8_t t, u;

    (void)buf_len; /* p06's bound is not this one -- it is sizeof scr. */

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
        r = (size_t)buf[off + p + 4] + 256 * (size_t)buf[off + p + 5]
            + 65536 * (size_t)buf[off + p + 6]
            + 16777216 * (size_t)buf[off + p + 7];
        p += 8;
        m = nelem < SCR ? nelem : SCR;
        if (len - p < nelem)
            break;
        memcpy(scr, buf + off + p, m);
        p += nelem;
        /* THE SAFETY LINE. c/kernel_hardened.c writes
         *     if (m != 0) r %= m; else r = 0;
         * here and that one line is the whole difference between the two
         * cells. This rung omits it and nothing else. */
        a = 0;
        b = r;
        while (a < b) {
            t = scr[a];
            u = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a++;
            b--;
        }
        a = r;
        b = m;
        while (a < b) {
            t = scr[a];
            u = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a++;
            b--;
        }
        a = 0;
        b = m;
        while (a < b) {
            t = scr[a];
            u = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a++;
            b--;
        }
        for (i = 0; i < m; i++)
            acc = acc * 31 + (uint64_t)scr[i];
        acc = acc * 31 + (uint64_t)m;
    }
    return acc * 31 + (uint64_t)nrec;
}
