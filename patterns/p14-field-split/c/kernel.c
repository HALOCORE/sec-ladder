/* p14 rung R1 -- idiomatic C99 field splitter. THE BUG.
 *
 * CWE-787 / CWE-121 / CWE-1284. The line is split on a delimiter and one
 * descriptor per field is appended to a fixed table; this rung never asks
 * whether the table is full. `if (nt == MAXTOK) break;` is the missing line and
 * it is the only missing line.
 *
 * **What this rung KEEPS.** The clamp `m = min(llen, SCR)`, so the copy is
 * bounded; both cursor guards, so `p` never leaves the window; the scan bound
 * `i <= m`, so every read of `scr` is in bounds. The whole of the bug is the
 * unbounded FIELD COUNT.
 *
 * **The overflowing loop's bound is a count of a byte value.** `nt` is one more
 * than the number of delimiters in `scr[0 .. m)`, so a 64-byte line can produce
 * anywhere from 1 to 65 descriptors against a 16-entry table -- up to 49
 * `size_t` stores, 392 bytes, past the end. Nothing in the wire format declares
 * that count and no length bounds it.
 *
 * The scan and the fold are written out as their own loops rather than called
 * through a helper, so that the `kernel` symbol contains all of them and
 * `harness/asm.py`'s kernel-exclusive `Ir` column is comparable across rungs
 * (`.memory/03-measurement.md`: a helper that survives at `-O0` would silently
 * move work out of the symbol).
 *
 * `memcpy` rather than a byte loop, in this rung and in every other, because
 * p02's retraction is the precedent: one operator flips `bulk_calls` and 100%
 * of the delta, and p14's measured difference must be the SPLIT.
 *
 * The scan is spelled `while (i <= m)` with `i == m` standing in for a virtual
 * delimiter at the end of the line, so that the tail field is appended at the
 * SAME call site as every other field. That is what keeps the safety line to
 * one line: a spelling with a separate tail-append needs the guard twice.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). The undefined behaviour
 * this rung executes is the out-of-bounds STORE into `tl`, and the
 * out-of-bounds LOAD the fold then performs through it. */
#include <string.h>

#include "kernel.h"

#define SCR 64
#define MAXTOK 16
#define DELIM ','

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t scr[SCR];
    size_t tl[MAXTOK];
    size_t nline, ln, p, llen, m, nt, s, i, j, q, cur, tj, flen;
    uint64_t acc = 0;

    (void)buf_len; /* p14's bound is not this one -- it is MAXTOK. */

    if (len < 4)
        return 0;
    nline = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nline == 0)
        return 0;

    memset(scr, 0, sizeof scr);
    memset(tl, 0, sizeof tl);
    p = 4;
    for (ln = 0; ln < nline; ln++) {
        if (len - p < 4)
            break;
        llen = (size_t)buf[off + p] + 256 * (size_t)buf[off + p + 1]
            + 65536 * (size_t)buf[off + p + 2]
            + 16777216 * (size_t)buf[off + p + 3];
        p += 4;
        m = llen < SCR ? llen : SCR;
        if (len - p < llen)
            break;
        memcpy(scr, buf + off + p, m);
        p += llen;
        nt = 0;
        s = 0;
        i = 0;
        while (i <= m) {
            if (i == m || scr[i] == DELIM) {
                /* THE SAFETY LINE. c/kernel_hardened.c writes
                 *     if (nt == MAXTOK) break;
                 * here and that one line is the whole difference between the
                 * two cells. This rung omits it and nothing else. */
                flen = i - s;
                tl[nt] = flen;
                nt++;
                s = i + 1;
            }
            i++;
        }
        cur = 0;
        for (j = 0; j < nt; j++) {
            tj = tl[j];
            acc = acc * 31 + (uint64_t)tj;
            for (q = 0; q < tj; q++)
                acc = acc * 31 + (uint64_t)scr[cur + q];
            cur = cur + tj + 1;
        }
        acc = acc * 31 + (uint64_t)nt;
    }
    return acc * 31 + (uint64_t)nline;
}
