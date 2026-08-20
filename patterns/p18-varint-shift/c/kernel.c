/* p18 rung R1 -- idiomatic C99 LEB128 varint decoder. THE BUG.
 *
 * CWE-1335 / CWE-758 (undefined shift), with CWE-681 downstream. Each byte's
 * seven payload bits are shifted into place and OR'd into the accumulator; this
 * rung never asks whether the shift count still fits a `uint64_t`.
 * `if (shift < VBITS)` is the missing line and it is the only missing line.
 *
 * **What this rung KEEPS.** The scan bound `p < len`, so every read of `buf` is
 * in bounds; the outer cursor guard `p == len`, so a dishonest `nv` cannot spin;
 * the per-varint reset of `val`, `shift` and `nb`. The whole of the bug is the
 * unbounded SHIFT COUNT.
 *
 * **The undefined behaviour touches no memory.** C99 6.5.7p3 makes `E1 << E2`
 * undefined when `E2 >= width(E1)`, and that is the only undefined operation
 * this rung can execute -- there is no out-of-bounds access anywhere in it, on
 * any input. On x86-64 the realised behaviour is a masked shift (`shlq %cl`
 * takes the count mod 64), so the payload lands in the wrong bit position and
 * the decoder returns a silently wrong integer. Measured identical on
 * gcc -O0/-O3 and clang -O0/-O3 (../NOTES.md 0.4); it is one legal outcome of
 * UB and not a guarantee, which is why ../NOTES.md reports it as four builds
 * agreeing rather than as a rule.
 *
 * **The eleventh byte is the first bad one.** `shift` is `7 * nb`, so the
 * canonical ten-byte encoding of a `uint64_t` ends at shift 63 -- in range. An
 * eleventh continuation byte makes it 70. Nothing in the wire format forbids
 * one, and no length in the window bounds it.
 *
 * The scan and the fold are written out as their own loops rather than called
 * through a helper, so that the `kernel` symbol contains all of them and
 * `harness/asm.py`'s kernel-exclusive `Ir` column is comparable across rungs
 * (`.memory/03-measurement.md`: a helper that survives at `-O0` would silently
 * move work out of the symbol).
 *
 * `shift` is `unsigned` and `shift += 7` wraps by definition (6.2.5p9), which is
 * what the four Rust rungs spell `wrapping_add`. */
#include "kernel.h"

#define VBITS 64

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint64_t acc = 0, val;
    size_t nv, v, p, nb;
    unsigned shift;
    uint8_t c;

    (void)buf_len; /* p18's bound is not this one -- it is VBITS. */

    if (len < 4)
        return 0;
    nv = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nv == 0)
        return 0;

    p = 4;
    for (v = 0; v < nv; v++) {
        if (p == len)
            break;
        val = 0;
        shift = 0;
        nb = 0;
        while (p < len) {
            c = buf[off + p];
            p = p + 1;
            nb = nb + 1;
            /* THE SAFETY LINE. c/kernel_hardened.c writes
             *     if (shift < VBITS)
             * here and that one line is the whole difference between the two
             * cells. This rung omits it and nothing else. */
            val |= (uint64_t)(c & 0x7f) << shift;
            shift += 7;
            if (!(c & 0x80))
                break;
        }
        acc = acc * 31 + val;
        acc = acc * 31 + (uint64_t)nb;
    }
    return acc * 31 + (uint64_t)nv;
}
