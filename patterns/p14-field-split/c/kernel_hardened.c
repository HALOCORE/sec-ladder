/* p14 rung R1h -- the hardened C cell. R1's kernel plus THE SAFETY LINE.
 *
 * `.memory/01-ladder.md`: ship R1h for every pattern that models a bug, because
 * with only R1 "C is faster" and "C is unsafe" are the same sentence. Same
 * signature, same calling convention, same driver, same scan and same fold --
 * the only difference from c/kernel.c is the one line marked below.
 *
 * **THE LINE BOUNDS A COUNT, NOT A LENGTH.** `nt == MAXTOK` compares a field
 * counter against a compile-time constant; it does not consult `llen`, `m`,
 * `len` or `buf_len`, because none of those bounds the number of delimiters an
 * attacker can put in a line. That is what makes p14's guard different in kind
 * from p02's, p16's and p17's, all of which compare a declared length against a
 * buffer extent.
 *
 * **TRUNCATION IS THE HARDENED BEHAVIOUR, and it is a real design decision
 * rather than an evasion.** Once the table is full this rung stops recording
 * fields and folds the 16 it has. That is `strtok`'s own answer to the same
 * problem in every fixed-table parser ever written, it is what `getopt`,
 * `argv`-splitters and CSV readers do, and it is p13's shape one level up: the
 * hardened cell is memory-safe and LOSES DATA. `spec.md` pins the truncation as
 * the answer so that the checked rungs cannot disagree about it.
 *
 * **This is the textbook spelling and it is not the only one in contract.**
 * `while (i <= m && nt < MAXTOK)` computes the same table; so does hoisting the
 * test to the top of the scan. `.memory/02-bench-rules.md` forbids re-shipping
 * a rung because a cheaper in-contract spelling was found, so the textbook line
 * ships and the alternatives are controls with their prices published beside
 * them (`controls/gen_controls.py`, ../NOTES.md 8).
 */
#include <string.h>

#include "kernel.h"

#define SCR 64
#define MAXTOK 16
#define DELIM ','

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t scr[SCR];
    size_t tl[MAXTOK];
    size_t nline, ln, p, llen, m, nt, s, i, j, q, cur, tj, flen;
    uint64_t acc = 0;

    (void)buf_len; /* p14's bound is not this one -- it is MAXTOK. */

    if (len < 4)
        return 0;
    nline = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nline == 0)
        return 0;

    memset(scr, 0, sizeof scr);
    memset(tl, 0, sizeof tl);
    p = 4;
    for (ln = 0; ln < nline; ln++) {
        if (len - p < 4)
            break;
        llen = (size_t)buf[off + p] + 256 * (size_t)buf[off + p + 1]
            + 65536 * (size_t)buf[off + p + 2]
            + 16777216 * (size_t)buf[off + p + 3];
        p += 4;
        m = llen < SCR ? llen : SCR;
        if (len - p < llen)
            break;
        memcpy(scr, buf + off + p, m);
        p += llen;
        nt = 0;
        s = 0;
        i = 0;
        while (i <= m) {
            if (i == m || scr[i] == DELIM) {
                /* >>> THE SAFETY LINE. c/kernel.c omits exactly this and
                 * nothing else. The table is fixed and the field count is a
                 * count of delimiters in attacker data. <<< */
                if (nt == MAXTOK)
                    break;
                flen = i - s;
                tl[nt] = flen;
                nt++;
                s = i + 1;
            }
            i++;
        }
        cur = 0;
        for (j = 0; j < nt; j++) {
            tj = tl[j];
            acc = acc * 31 + (uint64_t)tj;
            for (q = 0; q < tj; q++)
                acc = acc * 31 + (uint64_t)scr[cur + q];
            cur = cur + tj + 1;
        }
        acc = acc * 31 + (uint64_t)nt;
    }
    return acc * 31 + (uint64_t)nline;
}
