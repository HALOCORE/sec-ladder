/* p12 rung R1 -- idiomatic C99 `strcat` into a fixed buffer. THE BUG.
 *
 * CWE-787 / CWE-121. The window declares a count of packed, NUL-terminated
 * strings; this rung appends each of them to a 128-byte local array without
 * ever asking whether the next one fits. It is the single most-cited
 * memory-safety bug in C and it is the one this project was missing: every
 * other bug here is a read, and p02's write is a bulk `memcpy` into a
 * caller-supplied buffer.
 *
 * **What this rung KEEPS is as important as what it drops.** It keeps the
 * window bound on the SCAN -- `memchr(..., len - p)` -- and both outer bounds,
 * `if (q >= len) break;` and `if (p >= len) break;`. So every index into `buf`
 * is correct and every read of the source is in bounds; the only thing missing
 * is the one line that asks whether the destination has room. That is what
 * makes R1-vs-R1h the cost of the capacity check and nothing else, and it is
 * why p11's bug is not smuggled in here as a second one.
 *
 * `memchr` rather than `strlen` for exactly that reason, and because `strnlen`
 * is POSIX rather than C99 and `harness/build.py` compiles with `-std=c99` and
 * no feature-test macro (measured on p11: clang `call to undeclared function
 * 'strnlen'`, gcc `-Wimplicit-function-declaration`). Both C rungs call the
 * same routine, so the R1-vs-R1h difference carries no library term.
 *
 * The `dst[dlen++] = ...` loop is a BYTE LOOP and not a `memcpy`, in this rung
 * and in R2, because p02's retraction is the precedent: one operator flips
 * `bulk_calls` and 100% of the delta. R3 and R4 are free to spell the copy in
 * bulk and ../NOTES.md reports that as a spelling difference rather than a
 * safety one. Whether -O3 turns this loop back into a `memcpy` anyway is
 * measured on the disassembly (../NOTES.md 1), not assumed.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). The undefined behaviour
 * this rung executes is the out-of-bounds STORE, plus the out-of-bounds read of
 * `dst` that the destination fold performs afterwards when `dlen > DST_CAP`. */
#include <string.h>

#include "kernel.h"

#define DST_CAP 128

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t dst[DST_CAP];
    size_t nstr, s, p, q, i, slen, dlen = 0;
    uint64_t acc = 0;

    (void)buf_len; /* p12's bound is not this one -- it is sizeof dst. */

    if (len < 4)
        return 0;
    nstr = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nstr == 0)
        return 0;

    p = 4;
    for (s = 0; s < nstr; s++) {
        const void *z = memchr(buf + off + p, 0, len - p);
        q = (z == NULL) ? len : (size_t)((const unsigned char *)z - (buf + off));
        slen = q - p;
        /* THE COPY. R1h guards this with `if (dlen + slen <= DST_CAP)` and
         * that one expression is the whole difference between the two cells. */
        for (i = p; i < q; i++)
            dst[dlen++] = buf[off + i];
        acc = acc * 31 + (uint64_t)slen;
        if (q >= len)
            break;
        p = q + 1;
        if (p >= len)
            break;
    }
    for (i = 0; i < dlen; i++)
        acc = acc * 31 + (uint64_t)dst[i];
    return (acc * 31 + (uint64_t)dlen) * 31 + (uint64_t)nstr;
}
