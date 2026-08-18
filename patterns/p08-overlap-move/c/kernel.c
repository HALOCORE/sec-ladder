/* p08 rung R1 -- idiomatic C99 buffer shift. THE BUG: `memcpy` where `memmove`
 * is required.
 *
 * A fixed read buffer is shifted right to make room at the front, once per
 * framing layer. `memmove(scr + dr, scr, m - dr)` is correct; `memcpy` is
 * undefined behaviour whenever the ranges overlap, and on a forward-copying
 * implementation it replicates the first `dr` bytes instead of shifting.
 *
 * **This rung is NOT missing a bounds check.** `m < 2 || d == 0 || d + nrep > m`
 * is present here and in every other rung, so every index this file forms is
 * inside `scr[0..SCR)` and inside `buf[off .. off+len)`. Nothing leaves an
 * allocation. The harm is silent corruption inside a buffer the program owns --
 * which is why p08 is in the catalogue: every other pattern in this project
 * models a *spatial* error, and this one cannot be found by looking for one.
 *
 * The single-token difference against c/kernel_hardened.c is marked below.
 *
 * **The scratch is zero-initialised here even though C need not do it**, so that
 * the memset is a uniform per-call constant in all six rungs and cancels in
 * every rung-to-rung comparison. Safe Rust cannot construct `[u8; 4096]`
 * without initialising it; letting C skip the memset would price a language
 * difference that has nothing to do with the pattern. NOTES.md 2 reports the
 * memset's measured share of the call.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc * 31 + scr[j]`
 * is the wrapping operation ../spec.md asks for with no special spelling.
 * Nothing here can overflow signed. The only undefined behaviour this rung can
 * execute is the overlapping `memcpy` itself.
 *
 * Note `nrep = 1 + nrep_w % 4` is a MASK, not a check (`% 4` rather than `& 3`
 * because the two are the same function on unsigned values and the same
 * `and $0x3` instruction, but only `%` is linear arithmetic in the proof; see
 * ../spec.md, "Load-bearing"): every 16-bit value the
 * attacker can write yields a legal round count, so there is no rejection path
 * to get wrong. The rounds use `dr = d + r`, not a fixed `d`, on purpose --
 * with a fixed `d` and `d >= m/2` every round after the first would rewrite the
 * same bytes with the same values, the checksum would stop depending on `nrep`,
 * and a rung that skipped rounds 2..n would still pass. See ../spec.md. */
#include <string.h>

#include "kernel.h"

#define P08_SCR 4096u

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t scr[P08_SCR];
    size_t d, nrep_w, nrep, avail, m, r, j;
    uint64_t acc = 0;

    (void)buf_len; /* the kernel reads nothing outside buf[off .. off+len). */

    if (len < 4)
        return 0;
    d = (size_t)buf[off] + 256 * (size_t)buf[off + 1];
    nrep_w = (size_t)buf[off + 2] + 256 * (size_t)buf[off + 3];
    avail = len - 4;
    m = avail < P08_SCR ? avail : P08_SCR;
    nrep = 1 + nrep_w % 4;
    if (m < 2 || d == 0 || d + nrep > m)
        return 0;

    memset(scr, 0, P08_SCR);
    memcpy(scr, buf + off + 4, m);

    for (r = 0; r < nrep; r++) {
        size_t dr = d + r;
        /* >>> THE OPERATION. This rung spells it `memcpy`; c/kernel_hardened.c
         * spells it `memmove` and is otherwise character-identical. The source
         * [0, m-dr) and the destination [dr, m) overlap iff 2*dr < m, and `d`
         * comes from the file. <<< */
        memcpy(scr + dr, scr, m - dr);
    }

    for (j = 0; j < m; j++)
        acc = acc * 31 + scr[j];
    return acc * 31 + (uint64_t)m;
}
