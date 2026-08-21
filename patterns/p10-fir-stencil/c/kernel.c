/* p10 rung R1 -- idiomatic C99 weighted FIR / sliding-window stencil. THE BUG.
 *
 * CWE-193 (off-by-one) leading to CWE-125 (out-of-bounds read). The kernel
 * computes the window offset of the LAST sample byte it will read and compares
 * it against the window's length -- and compares it with the wrong relation.
 * `last` is an INDEX, so the test that keeps it inside the window is
 * `last >= len`; this rung writes `last > len`, which admits `last == len`.
 *
 * **THE WHOLE BUG IS ONE CHARACTER, AND IT IS NOT AN OMITTED LINE.** Every
 * earlier R1 in this project drops a check the hardened cell adds. This one
 * performs the check -- it just gets the fencepost wrong. That is what a real
 * off-by-one looks like, and it is why the hardened cell is expected to cost
 * nothing: c/kernel_hardened.c is this file with `>` changed to `>=`.
 *
 * **THE HARM IS EXACTLY ONE BYTE.** An off-by-one at a boundary cannot reach
 * further than one element by definition, and `adversarial-farover.bin` is the
 * row that says so: a window declaring `n` far beyond what it holds is rejected
 * by this rung and by the hardened one ALIKE. This rung's defect buys an
 * attacker one byte and nothing more.
 *
 * **WHETHER THAT BYTE IS OBSERVABLE IS A PROPERTY OF THE ALLOCATION AND NOT OF
 * THIS PROGRAM**, which is p02's result arriving on the read side at the
 * smallest possible magnitude. `adversarial-fencepost.bin` puts the window at
 * the very end of the payload, so the stolen byte is outside the malloc and
 * ASan fires. `adversarial-fenceslack.bin` is the SAME window with three
 * trailing payload bytes that do not form a further window: the identical
 * off-by-one then reads a byte that is merely the wrong one, ASan and UBSan are
 * silent, the exit code is 0, and the answer is wrong. ../NOTES.md 7.
 *
 * **THE BUG IS UNREACHABLE ON EVERY BENIGN INPUT, BY CONSTRUCTION AND NOT BY
 * LUCK.** inputs/gen.py packs every benign window exactly full, so
 * `last == len - 1` and this rung and the hardened one take the identical path.
 * harness/check.py stage 2 enforces it: every cell including this one must
 * print model.py's checksum on every non-adversarial input.
 *
 * **WHAT THIS RUNG KEEPS.** The window guard `n < taps`, so `nout = n - 2*r`
 * cannot underflow -- p10 models a fencepost and not a wild index. `taps`
 * computed at 64 bits, so a declared radius near 2^32 cannot wrap it. The
 * coefficients before the samples, so the overread leaves the window rather
 * than landing on a neighbouring field.
 *
 * The tap loop and the fold are written out as their own loops rather than
 * called through a helper, so that the `kernel` symbol contains all of them and
 * harness/asm.py's kernel-exclusive `Ir` column is comparable across rungs
 * (`.memory/03-measurement.md`: a helper that survives at `-O0` would silently
 * move work out of the symbol).
 *
 * Unsigned overflow wraps by definition (6.2.5p9), which is what the four Rust
 * rungs spell `wrapping_add` / `wrapping_mul`. */
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
    /* THE WINDOW GUARD, present in c/kernel_hardened.c too: without it
     * `n - 2*r` underflows and p10 would be modelling a wild index instead of
     * a fencepost. */
    if (n < taps)
        return 0;
    last = 8 + taps + n - 1;
    /* THE SAFETY LINE, and the only thing this rung gets wrong.
     * c/kernel_hardened.c writes
     *     if (last >= len)
     * here. `last` is an INDEX, so `last == len` is already one byte past the
     * window, and this spelling lets it through. */
    if (last > len)
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
