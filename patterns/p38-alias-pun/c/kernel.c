/* p38 rung R1 -- idiomatic C99 word-oriented record walker. THE BUG.
 *
 * CWE-843 (access of resource using incompatible type, "type confusion"),
 * reaching CWE-125 (out-of-bounds read). The record's 32-bit length lives on
 * the wire as two 16-bit halves; `rec_len` reads it back with one combined
 * 32-bit load and `rec_set_len` writes it as the two halves it is defined to
 * be. Both are ordinary C and the pair is written this way in real parsers.
 * The object is an array of `uint16_t`, the combined load's lvalue has type
 * `uint32_t`, and C99 6.5p7 does not permit that access.
 *
 * **THE CHECK IS HERE.** This is not a rung with a bounds check missing -- the
 * clamp below is the bounds enforcement, it is written, and it is identical to
 * the one in c/kernel_hardened.c. What the type rule licenses is *ignoring*
 * it: the clamp stores through `uint16_t` lvalues and the re-read loads through
 * a `uint32_t` lvalue, so the compiler may answer the load from the value it
 * read before the clamp. On gcc 13.3.0 at -O3 it does, and the fold then runs
 * off the end of `sc` with an attacker-chosen length.
 *
 * **What this rung does NOT do:** it does not index with an unchecked value by
 * accident, it does not omit a comparison, and it is not a straw man. Replace
 * `*(const uint32_t *)r` with the two-half spelling -- one expression, same
 * function, same file otherwise -- and every out-of-bounds read disappears on
 * both compilers. That single expression is the whole of p38.
 *
 * The decode loop above the walk is deliberately word-at-a-time and identical
 * in all eight rungs: a `memcpy` of the whole block would put a bulk-lowering
 * difference (p12's finding) inside p38's cost column.
 *
 * `sc` is declared 4-byte aligned so that the punning load is *aligned*. The
 * only undefined behaviour in this file is the aliasing violation; misaligned
 * access would be a second, different one and would let UBSan's alignment check
 * take credit for catching p38's bug when it cannot see it at all
 * (../NOTES.md 6).
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). */
#include "kernel.h"

/* The accessor pair. `rec_len` is THE PUN; `rec_len` in c/kernel_hardened.c is
 * the defined spelling and is the only difference between the two files. */
static uint32_t rec_len(const uint16_t *r)
{
    return *(const uint32_t *)r;
}

static void rec_set_len(uint16_t *r, uint32_t v)
{
    r[0] = (uint16_t)(v % 65536);
    r[1] = (uint16_t)(v / 65536);
}

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint16_t sc[SLB_P38_SCRATCH_W] __attribute__((aligned(4)));
    size_t nrec, nw, i, o, j, k, n, room;
    uint64_t acc = 0;

    (void)buf_len; /* p38's bound is the window's and the scratch's. */

    if (len < 4)
        return 0;
    nrec = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nrec == 0)
        return 0;

    nw = (len - 4) / 2;
    if (nw > SLB_P38_SCRATCH_W)
        nw = SLB_P38_SCRATCH_W;
    for (j = 0; j < nw; j++)
        sc[j] = (uint16_t)buf[off + 4 + 2 * j]
            + 256 * (uint16_t)buf[off + 5 + 2 * j];

    i = 0;
    o = 0;
    while (o < nrec && i + 2 <= nw) {
        room = (nw - i - 2) / 2;
        /* THE CLAMP. Written, present in both C rungs, and in this one the
         * compiler is entitled to ignore it. */
        if (rec_len(&sc[i]) > room)
            rec_set_len(&sc[i], (uint32_t)room);
        n = (size_t)rec_len(&sc[i]);
        for (k = 0; k < 2 * n; k++)
            acc = acc * 31 + (uint64_t)sc[i + 2 + k];
        i = i + 2 + 2 * n;
        o = o + 1;
    }
    return acc * 31 + (uint64_t)o;
}
