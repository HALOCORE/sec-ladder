/* p23 rung R1 -- idiomatic C99 in-place Hoare partition. THE BUG.
 *
 * CWE-125 / CWE-787 / CWE-129. Each record declares a pivot byte; this rung
 * partitions a 64-byte local scratch around it with Hoare's two-cursor
 * nested-scan and lets each inner scan run on the sentinel the data is assumed
 * to contain. The two `i < j &&` conjuncts are the missing lines and they are
 * the only missing lines.
 *
 * **Why a real C programmer writes it this way.** Textbook Hoare partition
 * takes its pivot FROM the sub-array -- `pv = a[lo]` -- and that one choice
 * makes both inner scans self-terminating: `a[lo]` itself is an element not
 * less than the pivot, so the upward scan cannot pass it, and symmetrically for
 * the downward one. The scans are then written bare, because a bound test in
 * the innermost loop of a sort is exactly the instruction a sort author is
 * trying not to execute. This kernel is handed a pivot instead of choosing one,
 * so the sentinel it is relying on does not exist -- and the code that relies
 * on it looks identical.
 *
 * **What this rung KEEPS.** The clamp `m = nelem < SCR ? nelem : SCR`, so the
 * copy is bounded; both cursor guards, so `p` never leaves the window; the
 * outer `while (i < j)`; and the `if (i < j)` before the swap. Every source
 * index is correct. The whole of the bug is in the two SCANS.
 *
 * The partition is spelled as two inner scan loops inside an outer loop -- the
 * standard C idiom, one comparison and one increment per element visited, no
 * temporary buffer -- and each loop is written out here rather than called
 * through a helper, so that the `kernel` symbol contains all of it and
 * `harness/asm.py`'s kernel-exclusive `Ir` column is comparable across rungs
 * (`.memory/03-measurement.md`: a helper that survives at `-O0` would silently
 * move work out of the symbol).
 *
 * `memcpy` rather than a byte loop, in this rung and in every other, because
 * p02's retraction is the precedent: one operator flips `bulk_calls` and 100%
 * of the delta, and p23's measured difference must be the PARTITION. Whether
 * -O3 turns either scan into something else is measured on the disassembly
 * (../NOTES.md 1), not assumed.
 *
 * **`<=` and `>=`, not `<` and `>`.** Pinned in ../spec.md for every rung; see
 * kernel.h for why (it is what makes `j - i == 1` collapse instead of letting
 * the cursors cross). It is also what removes the sentinel *even when the pivot
 * IS an array element*, which is the well-known second form of this bug.
 * `controls/guard_variants.c`'s `k_selfpivot` is that variant -- textbook
 * `pv = scr[0]`, unguarded scans, non-strict comparisons -- and on an all-equal
 * record it leaves the scratch exactly as this rung does, `index 64 out of
 * bounds` under UBSan and a `stack-buffer-overflow` under ASan, while the same
 * kernel on a mixed record is clean on both. ../NOTES.md 7 has the log.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9), so `acc*31 + scr[q]`,
 * `acc*31 + i` and the return expression are the wrapping operations ../spec.md
 * asks for. `j - 1` at `j == 0` wraps `size_t`, which is also defined -- the
 * undefined behaviour is the LOAD it then performs. The undefined behaviour
 * this rung executes is the out-of-bounds read either scan performs when its
 * sentinel is absent, and the out-of-bounds write the swap performs afterwards
 * when the downward scan has wrapped `j`. */
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
            /* THE SAFETY LINE, half 1. c/kernel_hardened.c writes
             *     while (i < j && scr[i] <= pv)
             * here. This rung omits the `i < j &&` and nothing else. */
            while (scr[i] <= pv)
                i++;
            /* THE SAFETY LINE, half 2. c/kernel_hardened.c writes
             *     while (i < j && scr[j - 1] >= pv)
             * here. This rung omits the `i < j &&` and nothing else. */
            while (scr[j - 1] >= pv)
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
