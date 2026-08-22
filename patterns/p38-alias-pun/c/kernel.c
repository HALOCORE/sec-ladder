/* p38 rung R1 -- a C99 word-oriented record walker BUILT TO EXHIBIT the bug.
 *
 * CWE-843 (access of resource using incompatible type, "type confusion"),
 * reaching CWE-125 (out-of-bounds read). The record's 32-bit length lives on
 * the wire as two 16-bit halves; `rec_len` reads it back with one combined
 * 32-bit load and `rec_set_len` writes it as the two halves it is defined to
 * be. Both are ordinary C. The object is an array of `uint16_t`, the combined
 * load's lvalue has type `uint32_t`, and C99 6.5p7 does not permit that access.
 *
 * ⚠ **WHAT THIS FILE IS, STATED BEFORE ANYTHING ELSE.** It is a DEMONSTRATION
 * KERNEL, not a claim about what parsers in the field write. An earlier draft
 * of this comment asserted that *"the pair is written this way in real
 * parsers"* with no citation; that claim is WITHDRAWN (TASK_066_REVIEW M3).
 * The bug class is real -- ASan reports `stack-buffer-overflow READ of size 2`
 * on the shipped gcc -O3 binary, TySan reports the aliasing violation itself,
 * and the Linux kernel builds -fno-strict-aliasing for exactly this -- but the
 * SHAPE below was constructed to satisfy four conditions at once, and p38
 * measures what the class costs and who catches it, NOT how often it occurs.
 *
 * **THE HARM NEEDS FOUR CONJUNCTIVE CONDITIONS. Remove any one and it goes.**
 *
 *   (i)   the getter and the setter disagree about the access type -- `rec_len`
 *         reads one 32-bit lvalue, `rec_set_len` writes two 16-bit ones;
 *   (ii)  the getter is called a SECOND time after the setter;
 *   (iii) the write-back has no consumer other than that second read;
 *   (iv)  both accessors are visible in one optimisable region.
 *
 * ⚠ **(iii) is structural here and is the least realistic of the four.**
 * `sc[i]` and `sc[i+1]` are read by nothing else in this kernel and the cursor
 * never revisits them, so the clamp store exists ONLY to be re-read three lines
 * later. The realistic reason to write a clamp back into a buffer is a LATER
 * PASS, and that shape -- a sanitise loop followed by a walk loop -- is
 * measured NOT to reproduce, on 12 of 12 cells (../NOTES.md 0c, `harm4.c`) and
 * again on this kernel (TASK_066_REVIEW M3).
 *
 * **AND THE UNDEFINED SPELLING IS THE DEAREST OF FIVE NEIGHBOURING SPELLINGS.**
 * Five one-line variants of this file each remove the harm, and on gcc 13.3.0
 * -O3 THREE OF THEM ARE CHEAPER THAN WHAT SHIPS, by exactly 6.00 Ir per call:
 * making `rec_set_len` pun too (a SYMMETRIC accessor pair), calling `rec_len`
 * once into a local, and building the identical source -fno-strict-aliasing.
 * So there is no speed argument for the shipped spelling -- against the
 * natural single-read spelling the undefined behaviour is not a win, it is a
 * 6.00 Ir/call LOSS. ../NOTES.md 8c has the table and the shipped controls.
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
 * accident and it does not omit a comparison. Replace `*(const uint32_t *)r`
 * with the two-half spelling -- one expression, same function, same file
 * otherwise -- and every out-of-bounds read disappears on both compilers. That
 * is condition (i), and it is the edit the pattern's contract pins; it is not
 * "the whole of p38", because four other single edits do the same job.
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
