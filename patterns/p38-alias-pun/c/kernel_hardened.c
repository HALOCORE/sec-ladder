/* p38 rung R1h -- the DEFINED spelling of the same parser. THE FIX.
 *
 * Character-identical to c/kernel.c except for the body of `rec_len`:
 *
 *     c/kernel.c            return *(const uint32_t *)r;                UB
 *     c/kernel_hardened.c   return (uint32_t)r[0] + 65536 * (uint32_t)r[1];
 *
 * The hardened spelling reads the two halves the format is defined in terms of
 * and combines them. It is defined C on every conforming implementation, it is
 * endian-independent where the pun is not, it needs no build flag, and it is
 * **the spelling every Rust rung is forced into** -- `sc` is a `[u16; 256]` and
 * the merged load is `read_unaligned`, which the pinned vstd cannot express --
 * so this is the rung that keeps R1h idiom-matched to R2..R5.
 *
 * ⚠ **AND IT IS NOT FREE, WHICH IS A MEASUREMENT AND NOT THE EXPECTED
 * RESULT** -- and the two compilers get there by different routes. clang (and
 * rustc) MERGE the two 16-bit loads back into one 32-bit load and then FAIL to
 * simplify `(x & 0xffff) + 65536 * (x >> 16)` back to `x`, which costs 10
 * instructions; gcc does not merge at all and pays 6 for two `movzwl`, a `shl`
 * and an `add`. rustc pays clang's 10 in every Rust rung. ../NOTES.md 1 has
 * both listings.
 *
 * **The defined spellings that ARE free are `memcpy(&v, r, 4)` and the union,
 * and they are free to the byte.** On clang both are `md5_fn
 * 366e3be50428933dee85aae05655e7ff`, which is c/kernel.c's own digest -- the
 * UB spelling and the defined spelling are the same machine code. On gcc they
 * are one instruction apart. Neither is the shipped R1h, because neither is a
 * spelling any Rust rung can write, and a C rung spelling the length read a way
 * no Rust rung can would put a codegen difference into p38's safety column.
 * controls/gen_controls.py ships both as `c_memcpy` and `c_union`.
 *
 * A third fix exists and is a build flag rather than a source change:
 * `-fno-strict-aliasing`, which the Linux kernel builds with. It is priced in
 * controls/, not here, because a flag change to the shared matrix would cost a
 * re-measure of every pattern in the tree (RECAP, settled answer 4).
 *
 * Everything else about this file -- the clamp, the guard, the fold, the
 * decode loop, the scratch and its alignment -- is c/kernel.c's. */
#include "kernel.h"

/* The accessor pair. This `rec_len` is the DEFINED spelling; c/kernel.c writes
 * the punning combined load and that expression is the whole difference
 * between the two files. */
static uint32_t rec_len(const uint16_t *r)
{
    return (uint32_t)r[0] + 65536 * (uint32_t)r[1];
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
        /* THE CLAMP. Written, present in both C rungs, and in this one it is
         * also OBSERVED, because the re-read below is a defined access. */
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
