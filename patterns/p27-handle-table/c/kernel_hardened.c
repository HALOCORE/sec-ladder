/* p27 rung R1h -- hardened C99 handle table.
 *
 * c/kernel.c with one conjunct added: `&& live[h] == 1` on the READ path. That
 * is the whole difference between the two cells, and R1h-vs-R1 is therefore the
 * price of the LIVENESS test and of nothing else.
 *
 * Everything else -- the slot bound `h < ntab`, the capacity guard, the
 * maintenance of `live[]` by CLOSE, the epilogue -- is identical to R1, because
 * R1 already has all of it. See c/kernel.c and c/kernel.h.
 *
 * Note what the added conjunct costs and what it does not: it is one load and
 * one compare on the READ path, and it is `live[]`'s only *reader*. R1 already
 * pays for the array's existence, its zero-initialisation, its store in OPEN,
 * its store in CLOSE and its read in the epilogue; the hardened cell adds one
 * read per READ op. That is a deliberately narrow difference -- widening it to
 * "R1 does not have `live[]` at all" would have made R1 unable to free without
 * double-freeing, and the comparison would then have been between two different
 * programs rather than between one program and its guard. ../NOTES.md 0b. */
#include <stdlib.h>
#include <string.h>

#include "kernel.h"

#define TABCAP 32
#define RECSZ 1
#define SENT 251

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t *tab[TABCAP];
    uint8_t live[TABCAP];
    size_t nops, o, p, ntab, h, j;
    uint8_t c, a;
    uint64_t acc = 0;

    (void)buf_len;

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    memset(tab, 0, sizeof tab);
    memset(live, 0, sizeof live);
    ntab = 0;
    p = 4;
    for (o = 0; o < nops; o++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        h = (size_t)a;
        if (c % 4 == 0) {
            if (ntab < TABCAP) {
                uint8_t *q = (uint8_t *)malloc(RECSZ);
                if (q == NULL)
                    abort();
                *q = a;
                tab[ntab] = q;
                live[ntab] = 1;
                ntab++;
                acc = acc * 31 + (uint64_t)a;
            } else {
                acc = acc * 31 + SENT;
            }
        } else if (c % 4 == 1) {
            if (h < ntab && live[h] == 1) {
                free(tab[h]);
                live[h] = 0;
                acc = acc * 31 + 1;
            } else {
                acc = acc * 31 + SENT;
            }
        } else {
            /* THE SAFETY LINE, and c/kernel.c omits exactly the second
             * conjunct: `live[h] == 1`. */
            if (h < ntab && live[h] == 1) {
                acc = acc * 31 + (uint64_t)*tab[h];
            } else {
                acc = acc * 31 + SENT;
            }
        }
    }
    for (j = 0; j < ntab; j++) {
        if (live[j] == 1) {
            free(tab[j]);
            live[j] = 0;
        }
    }
    return acc * 31 + (uint64_t)ntab;
}
