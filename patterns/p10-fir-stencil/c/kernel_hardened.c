/* p10 rung R1h -- the same C kernel with the fencepost RIGHT.
 *
 * `if (last >= len)` is what c/kernel.c writes as `if (last > len)`. That one
 * character is the whole difference between the two cells: every other line of
 * this file is character for character what R1 does, so `c-gcc-h` minus
 * `c-gcc` is the price of that character and of nothing else
 * (`.memory/02-bench-rules.md`, "The precondition must be structural").
 *
 * **AND THAT IS WHY THE COST IS EXPECTED TO BE ZERO.** Every earlier hardened
 * cell in this project ADDS a comparison the unhardened one does not perform.
 * This one performs the same comparison between the same two operands and
 * merely relates them correctly, so the two instruction streams should differ
 * in one opcode byte (`ja` -> `jae`) and in nothing else. ../NOTES.md 4
 * measures it, at both optimisation levels and on both compilers, rather than
 * asserting it -- and a zero there is a RESULT and not an absence of one: it is
 * the first hardening in this project that is free, and the reason is
 * structural rather than a property of this box (contrast p08's
 * `R1 == R1h at 0.00 Ir/call`, which is a glibc property and must never be
 * quoted as "memmove is free").
 *
 * **THE COMPARISON IS LEGAL ON EVERY INPUT IT IS MEASURED ON.**
 * `.memory/02-bench-rules.md`'s first rule -- never compare cost on an input
 * where the unhardened rung commits UB or refuses work -- rules out the
 * R1-vs-R1h cost row on p12 and p13. Here `inputs/gen.py` packs every benign
 * window exactly full, so `last == len - 1` and both rungs take the identical
 * path through the identical loop over the identical bytes. The only inputs on
 * which they differ at all are `adversarial-fencepost.bin` and
 * `adversarial-fenceslack.bin`, and no cost is read off either.
 *
 * The declaration, the window layout and the full argument are in kernel.h;
 * this file carries only what is different. */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint64_t acc = 0;
    size_t n, r, taps, last, nout, sb, i, j;
    uint32_t s;

    (void)buf_len; /* p10's bound is the WINDOW's extent, `len`. */

    if (len < 8)
        return 0;
    n = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    r = (size_t)buf[off + 4] + 256 * (size_t)buf[off + 5]
        + 65536 * (size_t)buf[off + 6] + 16777216 * (size_t)buf[off + 7];
    taps = 2 * r + 1;
    /* THE WINDOW GUARD, present in c/kernel.c too: without it `n - 2*r`
     * underflows and p10 would be modelling a wild index instead of a
     * fencepost. */
    if (n < taps)
        return 0;
    last = 8 + taps + n - 1;
    /* THE SAFETY LINE, and the only thing c/kernel.c gets wrong. `last` is an
     * INDEX, so `last == len` is already one byte past the window. */
    if (last >= len)
        return 0;

    nout = n - 2 * r;
    sb = 8 + taps;
    for (i = 0; i < nout; i++) {
        s = 0;
        for (j = 0; j < taps; j++)
            s = s + (uint32_t)buf[off + sb + i + j] * (uint32_t)buf[off + 8 + j];
        acc = acc * 31 + (uint64_t)s;
    }
    return acc * 31 + (uint64_t)nout;
}
