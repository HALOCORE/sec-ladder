/* p06 rung R1h -- the hardened C cell. R1's kernel plus THE SAFETY LINE.
 *
 * `.memory/01-ladder.md`: ship R1h for every pattern that models a bug, because
 * with only R1 "C is faster" and "C is unsafe" are the same sentence. Same
 * signature, same calling convention, same driver, same three reverses -- the
 * only difference from c/kernel.c is the one line marked below.
 *
 * **THE LINE IS A DIVISION AND THAT IS THE POINT.** Every earlier pattern's
 * hardened cell adds a compare and a branch. This one adds a hardware `div` on
 * a runtime divisor, which callgrind prices at exactly 1 Ir
 * (`.memory/03-measurement.md`) and Cascade Lake at tens of cycles. ../NOTES.md
 * 0 measures both columns and they disagree in SIGN on clang.
 *
 * **`m == 0` would be a division by zero**, so the guard is part of the pinned
 * contract rather than a matter of taste: `if (m != 0) r %= m; else r = 0;`.
 * `degenerate.bin`'s first record is `nelem == 0`, so the guard is exercised on
 * a shipped input and not only argued about. In C a division by zero is
 * undefined behaviour, so a hardened rung without the guard would introduce a
 * SECOND bug while removing the first -- which is exactly the trap this pattern
 * is about.
 *
 * **This is the TEXTBOOK spelling and it is not the cheapest one in contract.**
 * `if (m == 0) r = 0; else if (r >= m) r %= m;` computes the same function --
 * the divide is redundant when `r < m` -- and on the perf inputs, where `r < m`
 * always, it is measurably cheaper in wall clock on BOTH compilers while being
 * dearer in `Ir` on gcc. `.memory/02-bench-rules.md` forbids re-shipping a rung
 * because a cheaper in-contract spelling was found, so the textbook line ships
 * and the cheaper one is a control with its price published beside it
 * (`controls/gen_controls.py`, ../NOTES.md 8). Both numbers, both labelled,
 * with the input named.
 */
#include <string.h>

#include "kernel.h"

#define SCR 64

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t scr[SCR];
    size_t nrec, rec, p, i, nelem, m, r, a, b;
    uint64_t acc = 0;
    uint8_t t, u;

    (void)buf_len; /* p06's bound is not this one -- it is sizeof scr. */

    if (len < 4)
        return 0;
    nrec = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nrec == 0)
        return 0;

    memset(scr, 0, sizeof scr);
    p = 4;
    for (rec = 0; rec < nrec; rec++) {
        if (len - p < 8)
            break;
        nelem = (size_t)buf[off + p] + 256 * (size_t)buf[off + p + 1]
            + 65536 * (size_t)buf[off + p + 2]
            + 16777216 * (size_t)buf[off + p + 3];
        r = (size_t)buf[off + p + 4] + 256 * (size_t)buf[off + p + 5]
            + 65536 * (size_t)buf[off + p + 6]
            + 16777216 * (size_t)buf[off + p + 7];
        p += 8;
        m = nelem < SCR ? nelem : SCR;
        if (len - p < nelem)
            break;
        memcpy(scr, buf + off + p, m);
        p += nelem;
        /* >>> THE SAFETY LINE. c/kernel.c omits exactly this and nothing
         * else. The `m != 0` arm is not decoration: `r %= 0` is undefined
         * behaviour in C, and `degenerate.bin` declares a record with
         * `nelem == 0`. <<< */
        if (m != 0)
            r %= m;
        else
            r = 0;
        a = 0;
        b = r;
        while (a < b) {
            t = scr[a];
            u = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a++;
            b--;
        }
        a = r;
        b = m;
        while (a < b) {
            t = scr[a];
            u = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a++;
            b--;
        }
        a = 0;
        b = m;
        while (a < b) {
            t = scr[a];
            u = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a++;
            b--;
        }
        for (i = 0; i < m; i++)
            acc = acc * 31 + (uint64_t)scr[i];
        acc = acc * 31 + (uint64_t)m;
    }
    return acc * 31 + (uint64_t)nrec;
}
