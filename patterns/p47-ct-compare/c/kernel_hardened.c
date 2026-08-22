/* p47 rung R1h -- hardened C. The constant-time comparison.
 *
 * Character-identical to c/kernel.c except for the comparison expression:
 * where that file calls `memcmp` and stops at the first differing byte, this
 * one or-accumulates the byte-wise xor across **every** byte of the tag and
 * tests the accumulator once at the end. The number of instructions it
 * executes is a function of `tlen` alone -- never of where, or whether, the
 * two tags first differ.
 *
 * **THE ACCUMULATOR IS NOT `volatile`, AND THAT IS A MEASUREMENT, NOT A
 * SHORTCUT.** The received advice for this idiom is to force the accumulator
 * into memory so the optimiser cannot reason about it. On this toolchain that
 * is unnecessary and expensive:
 *
 *   - the plain accumulator below is already constant in the first-mismatch
 *     position -- 291 770 Ir at k = 0 and 291 779 at k = 200 over 1000 calls,
 *     the 9 being the probe's own `atol` digit count and not the kernel
 *     (../NOTES.md 0);
 *   - `volatile uint8_t d` costs **6.35x** -- 1 852 772 Ir for the same 1000
 *     calls -- because it defeats vectorisation entirely and turns the loop
 *     into a load/xor/or/store through a stack slot, one byte at a time, in
 *     both gcc and clang.
 *
 * The volatile spelling ships as a control (`controls/gen_controls.py`,
 * `h_vol`) so the 6.35x is checkable rather than asserted, and ../spec.md
 * FORBIDS `volatile` in the measured cells so that the two are never confused.
 *
 * **WHAT THE OPTIMISER ACTUALLY DOES TO THIS LOOP**, on the shipped binary and
 * not in a probe (`.memory/06-catalogue.md` hazard 2: a text pin binds the
 * source and not the object): clang vectorises it to SSE2 -- `movdqu ; movdqu
 * ; pxor ; por` -- and gcc likewise, and neither emits a data-dependent branch
 * anywhere inside it. ../NOTES.md 1 has the disassembly of the cell that
 * ships. There is no `repe cmpsb` in any p47 cell, so
 * `.memory/03-measurement.md`'s `rep`-string counting hazard does not arise;
 * `bulk_calls` in the gate record names `bcmp`/`memcmp` for the R1 cells and
 * nothing for these.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). This rung, like R1,
 * executes no undefined behaviour on any input -- the difference between the
 * two files is not in the value domain. */
#include <string.h>

#include "kernel.h"

#define MATCH 7
#define MISS 251

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t ntag, tlen, o, p, i;
    uint64_t acc = 0;
    uint8_t d;

    (void)buf_len; /* p47's bound is the window's, not the blob's. */

    if (len < 8)
        return 0;
    ntag = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    tlen = (size_t)buf[off + 4] + 256 * (size_t)buf[off + 5]
        + 65536 * (size_t)buf[off + 6] + 16777216 * (size_t)buf[off + 7];
    if (ntag == 0 || tlen == 0)
        return 0;

    p = 8;
    o = 0;
    while (o < ntag && len - p >= 2 * tlen) {
        /* THE TIMING LINE. c/kernel.c writes
         *     if (memcmp(buf + off + p, buf + off + p + tlen, tlen) == 0)
         * here, and that expression is the whole difference between the two
         * cells. This one reads every byte, always. */
        d = 0;
        for (i = 0; i < tlen; i++)
            d |= (uint8_t)(buf[off + p + i] ^ buf[off + p + tlen + i]);
        if (d == 0)
            acc = acc * 31 + MATCH;
        else
            acc = acc * 31 + MISS;
        p += 2 * tlen;
        o += 1;
    }
    return acc * 31 + (uint64_t)o;
}
