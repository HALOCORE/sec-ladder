/* p11 rung R1 -- idiomatic C99 NUL scan. THE BUG.
 *
 * CWE-125 via a missing sentinel. The window declares a count of packed,
 * NUL-terminated strings; this rung measures each one with `strlen`, which is
 * bounded by the terminator and by nothing else. If a terminator is absent the
 * scan runs off the end of the record, off the end of the window, and off the
 * end of the allocation.
 *
 * `strlen` is not a strawman here, it is the point: it is what a competent C
 * programmer writes for exactly this job, it is what the header format invites,
 * and it is a hand-written AVX2 routine inside glibc. R1-vs-R3 is therefore a
 * *library* comparison as much as a safety one, and ../NOTES.md 2 separates the
 * two terms instead of quoting the ratio.
 *
 * The single `(void)` cast is half the finding: the size is right there in the
 * signature. R1 has it and does not look; R1h (kernel_hardened.c) is this file
 * with `strlen` replaced by `memchr` over `len - p` remaining bytes. Everything
 * else about the two cells -- signature, calling convention, the `len < 4` test,
 * the `nstr == 0` test, the fold, the cursor, the return -- is identical, so
 * R1-vs-R1h is the cost of the bound and nothing else.
 *
 * **What this rung KEEPS is as important as what it drops.** It keeps both
 * outer bounds -- `if (q >= len) break;` and `if (p >= len) break;` -- so the
 * *cursor* is bounded by the window even though the *scan* is not. That is
 * deliberate and it is what makes the bug realistic: the programmer did bound
 * the outer walk, and then trusted the sentinel for the inner one. It also means
 * R1 overruns at most once per call -- the string that has no terminator --
 * rather than running away for ever the way p16's walker does. See
 * ../NOTES.md 7. (`q >= len` is unreachable in THIS rung, because `strlen` never
 * stops at the window end; it is kept so that R1 and R1h differ in the scan and
 * in nothing else, which is what makes R1-vs-R1h the cost of the bound.)
 *
 * **The scan and the fold are separate loops in every rung** (../spec.md,
 * `idiom.required`). Fusing them deletes the pattern: `slen` would never
 * materialise and `strlen` would be unavailable. ../NOTES.md 1 shows on the
 * disassembly that -O3 keeps them separate in all six rungs -- and that clang
 * rewrites the *hand-written* byte scan into a `strlen` call anyway, so the
 * libcall is not something this rung was given by being written a special way.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9), so `h*31 + b`,
 * `acc*31 + (h ^ slen)` and `acc*31 + nstr` are the wrapping operations
 * ../spec.md asks for. The only undefined behaviour this rung can execute is the
 * out-of-bounds read itself. */
#include <string.h>

#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t nstr, s, p, q, i, slen;
    uint64_t acc = 0;

    (void)buf_len; /* the size is right here ... and this rung never looks. */

    if (len < 4)
        return 0;
    nstr = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nstr == 0)
        return 0;

    p = 4;
    for (s = 0; s < nstr; s++) {
        uint64_t h = 0;
        /* THE SCAN. Bounded by the sentinel. R1h bounds it by the window
         * instead, and that one expression is the whole difference. */
        q = p + strlen((const char *)(buf + off + p));
        slen = q - p;
        for (i = p; i < q; i++)
            h = h * 31 + (uint64_t)buf[off + i];
        acc = acc * 31 + (h ^ (uint64_t)slen);
        if (q >= len)
            break;
        p = q + 1;
        if (p >= len)
            break;
    }
    return acc * 31 + (uint64_t)nstr;
}
