/* p13 rung R1 -- idiomatic C99 `strncpy` into a fixed buffer. THE BUG.
 *
 * CWE-170 (improper null termination) leading to CWE-125 (out-of-bounds read).
 * The window declares a count of packed, NUL-terminated strings; this rung
 * copies each of them into a 32-byte local with exact `strncpy(dst, src,
 * sizeof dst)` semantics and then reads `dst` back as a C string.
 *
 * **What this rung KEEPS is as important as what it drops.** It keeps the
 * window bound on the SOURCE scan, both outer bounds (`if (q >= len) break;`
 * and `if (p >= len) break;`), the `n = min(slen, DST_CAP)` cap on the copy and
 * the whole zero-fill. So every index into `buf` is correct, every write into
 * `dst` is in bounds, and the copy is memory-safe. The only thing missing is
 * `dst[DST_CAP - 1] = 0;` -- the line `strncpy` does not write for you. That is
 * what makes R1-vs-R1h the cost of the termination store and nothing else.
 *
 * **The copy is spelled out rather than calling `strncpy` itself**, and both C
 * rungs spell it the same way, so the R1-vs-R1h difference carries no library
 * term. `strncpy(`, `strlcpy(` and `snprintf(` are in ../spec.md's
 * `idiom.forbidden` for that reason, and the library axis is measured
 * separately as a CONTROL (`../controls/library_axis.py`, ../NOTES.md 3) where
 * the routine can be named beside every rate -- `.memory/01-ladder.md`
 * finding 9's rule.
 *
 * The undefined behaviour this rung executes is the out-of-bounds READ of
 * `dst` performed by the consumer scan, and nothing else. It fires exactly when
 * some string has `slen >= DST_CAP`, because the scan stops at the first zero
 * byte and therefore every one of the `n` copied bytes is non-zero: `dst`
 * contains a NUL if and only if the zero-fill ran.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). */
#include "kernel.h"

#define DST_CAP 32

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t dst[DST_CAP];
    size_t nstr, s, p, q, i, slen, n, d;
    uint64_t acc = 0;

    (void)buf_len; /* p13's bound is not this one -- it is sizeof dst. */

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
        /* strncpy(dst, buf + off + p, DST_CAP), spelled out: copy at most
         * DST_CAP bytes, then zero-fill the remainder of DST_CAP. */
        n = slen < DST_CAP ? slen : DST_CAP;
        for (i = 0; i < n; i++)
            dst[i] = buf[off + p + i];
        for (i = n; i < DST_CAP; i++)
            dst[i] = 0;
        /* >>> THE TERMINATION. R1h writes `dst[DST_CAP - 1] = 0;` here and
         * this rung omits exactly that line and nothing else. <<< */
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
