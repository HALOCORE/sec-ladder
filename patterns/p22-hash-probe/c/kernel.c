/* p22 rung R1 -- an idiomatic C99 open-addressing probe, WITH the bug.
 *
 * CWE-835 (loop with unreachable exit condition, "infinite loop"), reached
 * through CWE-1284 (improper validation of a quantity). The probe loop below is
 * the textbook linear-probe walk and it is correct **as long as the table is
 * never full**; keeping it that way is the job of a capacity check that this
 * file does not have.
 *
 * **WHAT IS AND IS NOT WRONG HERE, stated before anything else.** Nothing in
 * this file is memory-unsafe. `i` is reduced modulo SLB_P22_TABCAP on entry and
 * on every step, so `tab[i]` is in bounds unconditionally; there is no
 * unchecked index, no lifetime, no aliasing violation, no integer overflow.
 * Measured (../NOTES.md 0): ASan+UBSan on this exact file is **silent** and
 * Miri on the equivalent safe Rust is **silent**. The failure is that
 * `kernel()` never returns.
 *
 * **THE OMISSION IS ONE CONJUNCT**, and c/kernel_hardened.c is otherwise
 * character-identical:
 *
 *     if (k != SLB_P22_EMPTY)                                 this file
 *     if (k != SLB_P22_EMPTY && nfill < SLB_P22_TABCAP)        hardened
 *
 * `nfill < TABCAP` is exactly the statement "some slot is still EMPTY", and an
 * EMPTY slot is the only thing that stops the probe. Take it away and a key that
 * is absent from a full table walks the ring for ever.
 *
 * **SAFE RUST DOES NOT SUPPLY IT EITHER, and that is the pattern.** Ten other
 * patterns here omit a bounds check that safe Rust puts back by construction.
 * There is no language on this ladder that emits `nfill < TABCAP`: R2, R3, R4
 * and R5 all write it by hand, exactly as c/kernel_hardened.c does. The
 * mechanical safe-Rust port of THIS file hangs at -O0 and at -O3 with Miri
 * silent (../NOTES.md 0b, `controls/gen_controls.py --run r2_noguard`). The one
 * rung whose TOOLING refuses the omission is R5, where Verus reports
 * `loop must have a decreases clause` before it will look at anything else.
 *
 * **The bug needs a full table, so it lives on `adversarial-full*.bin` only.**
 * `small.bin`, `large.bin` and `degenerate.bin` carry at most 48 distinct
 * non-zero key bytes per window (inputs/gen.py asserts it), so `nfill` never
 * reaches 64, the guard this file lacks would never have fired, and R1 agrees
 * with every other rung and with model.py byte for byte. That is why the
 * checksum stage can see all six rungs at all.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t tab[SLB_P22_TABCAP];
    size_t nkey, nfill, p, t, i, j;
    uint64_t acc = 0;

    (void)buf_len; /* p22's bound is the window's and the table's. */

    if (len < 4)
        return 0;
    nkey = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nkey == 0)
        return 0;

    for (j = 0; j < SLB_P22_TABCAP; j++)
        tab[j] = SLB_P22_EMPTY;
    nfill = 0;
    p = 4;
    for (t = 0; t < nkey; t++) {
        uint8_t k;
        if (len - p < 1)
            break;
        k = buf[off + p];
        p = p + 1;
        /* >>> THE SAFETY LINE. `&& nfill < SLB_P22_TABCAP` belongs here and is
         * the only thing this file omits. <<< */
        if (k != SLB_P22_EMPTY) {
            i = (size_t)k * 2654435761u / 16777216u % SLB_P22_TABCAP;
            /* THE PROBE LOOP. */
            while (tab[i] != SLB_P22_EMPTY && tab[i] != k)
                i = (i + 1) % SLB_P22_TABCAP;
            if (tab[i] == SLB_P22_EMPTY) {
                tab[i] = k;
                nfill = nfill + 1;
            }
            acc = acc * 31 + (uint64_t)i;
        } else {
            acc = acc * 31 + SLB_P22_SENT;
        }
    }
    return acc * 31 + (uint64_t)nfill;
}
