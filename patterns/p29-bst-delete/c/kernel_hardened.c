/* p29 rung R1h -- hardened C99 binary search tree with a cached lookup result.
 *
 * c/kernel.c with TWO conjuncts added on the USE path:
 *
 *     if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key)
 *                            ^^^^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^^^^^^^^^^
 *                            is the ALLOCATION     is the OCCUPANT still
 *                            still there?          the one FIND returned?
 *                            (p27's whole line)    (NEW -- p27 has no analogue)
 *
 * That is the whole difference between the two cells, so R1h-vs-R1 is the price
 * of THIS LINE and of nothing else.
 *
 * **THE ORDER IS LOAD-BEARING AND IS NOT A STYLE CHOICE.** `tab[g_slot]` is
 * never reset, so `tab[g_slot][0]` is the same load from the same address as
 * `g_saved[0]`. C's `&&` short-circuits, so on exactly the inputs where the
 * record has been freed the second conjunct is not evaluated. Deleting the
 * liveness conjunct leaves a test that is *itself* a heap-use-after-free: this
 * line fires ASan zero times and the same line without `live[g_slot] == 1`
 * fires it on every use-after-free window.
 *
 * **AND NEITHER CONJUNCT SUBSUMES THE OTHER; THEY FAIL IN DIFFERENT
 * CURRENCIES.** Without the liveness conjunct the harm is memory-unsafety and
 * usually NOT a wrong answer -- the freed bytes still hold the old record often
 * enough that the checksum survives. Without the identity conjunct the harm is
 * a wrong answer and NEVER a memory error -- every recycle window diverges and
 * ASan says nothing at all.
 *
 * ⚠ The counts are in ../NOTES.md 2b and ../controls/arms.json and are
 * deliberately NOT transcribed here: a number only a rebuild can produce must
 * not be written into a file the rebuild re-hashes
 * (`.memory/02-bench-rules.md`).
 *
 * Everything else -- `live[]` and its maintenance, the `live[cur] == 1`
 * conjunct and the `steps` bound on every walk, the capacity guard, the
 * epilogue -- is identical to R1, because R1 already has all of it. R1 consults
 * `live[]` at every step of every walk; the one path it does not consult it on
 * is the one holding a raw pointer. See c/kernel.c and c/kernel.h. */
#include <stdlib.h>
#include <string.h>

#include "kernel.h"

#define TABCAP 32
#define RECSZ 4
#define NIL 255
#define SENT 251

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t *tab[TABCAP];
    uint8_t live[TABCAP];
    uint8_t *g_saved;
    uint8_t g_slot, g_key;
    size_t nops, o, p, ntab, j;
    uint8_t c, a, root;
    uint64_t acc = 0;

    (void)buf_len; /* p29's bound is not this one -- it is the record's life. */

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    memset(tab, 0, sizeof tab);
    memset(live, 0, sizeof live);
    ntab = 0;
    root = NIL;
    g_saved = NULL;
    g_slot = 0;
    g_key = 0;
    p = 4;
    /* R1 MAINTAINS the cached binding's bookkeeping and never consults it --
     * that is the bug, written out. The casts are here, in both C rungs, so
     * that R1 compiles warning-free under -Wall -Wextra and the two files
     * differ by the safety line and nothing else. */
    (void)g_slot;
    (void)g_key;

    for (o = 0; o < nops; o++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        if (c % 4 == 0) {
            uint8_t cur = root, par = NIL;
            unsigned steps = 0;
            int goleft = 0, dup = 0;
            while (cur != NIL && live[cur] == 1 && steps < TABCAP) {
                steps++;
                if (a < tab[cur][0]) {
                    par = cur; goleft = 1; cur = tab[cur][2];
                } else if (a > tab[cur][0]) {
                    par = cur; goleft = 0; cur = tab[cur][3];
                } else {
                    tab[cur][1] = (uint8_t)(a * 7u + 1u); dup = 1; break;
                }
            }
            if (dup) {
                acc = acc * 31 + (uint64_t)a;
            } else if (ntab < TABCAP) {
                uint8_t *q = (uint8_t *)malloc(RECSZ);
                if (q == NULL)
                    abort();
                q[0] = a;
                q[1] = (uint8_t)(a * 7u + 1u);
                q[2] = NIL;
                q[3] = NIL;
                tab[ntab] = q;
                live[ntab] = 1;
                if (par == NIL) root = (uint8_t)ntab;
                else if (goleft) tab[par][2] = (uint8_t)ntab;
                else tab[par][3] = (uint8_t)ntab;
                ntab++;
                acc = acc * 31 + (uint64_t)a;
            } else {
                acc = acc * 31 + SENT;
            }
        } else if (c % 4 == 1) {
            uint8_t cur = root;
            unsigned steps = 0;
            int found = 0;
            while (cur != NIL && live[cur] == 1 && steps < TABCAP) {
                steps++;
                if (a < tab[cur][0]) cur = tab[cur][2];
                else if (a > tab[cur][0]) cur = tab[cur][3];
                else { found = 1; break; }
            }
            if (found) {
                g_saved = tab[cur];
                g_slot = cur;
                g_key = a;
                acc = acc * 31 + 1;
            } else {
                acc = acc * 31 + SENT;
            }
        } else if (c % 4 == 2) {
            uint8_t cur = root, par = NIL;
            unsigned steps = 0, guard = 0;
            int goleft = 0, found = 0;
            while (cur != NIL && live[cur] == 1 && steps < TABCAP) {
                steps++;
                if (a < tab[cur][0]) {
                    par = cur; goleft = 1; cur = tab[cur][2];
                } else if (a > tab[cur][0]) {
                    par = cur; goleft = 0; cur = tab[cur][3];
                } else {
                    found = 1; break;
                }
            }
            if (found) {
                while (guard < TABCAP) {
                    guard++;
                    if (tab[cur][2] != NIL && live[tab[cur][2]] == 1
                        && tab[cur][3] != NIL && live[tab[cur][3]] == 1) {
                        uint8_t sp = cur, s = tab[cur][3];
                        unsigned sst = 0;
                        int sgoleft = 0;
                        while (tab[s][2] != NIL && live[tab[s][2]] == 1
                               && sst < TABCAP) {
                            sst++; sp = s; s = tab[s][2]; sgoleft = 1;
                        }
                        tab[cur][0] = tab[s][0];
                        tab[cur][1] = tab[s][1];
                        cur = s; par = sp; goleft = sgoleft;
                        continue;
                    }
                    {
                        uint8_t ch = (tab[cur][2] != NIL) ? tab[cur][2]
                                                          : tab[cur][3];
                        if (par == NIL) root = ch;
                        else if (goleft) tab[par][2] = ch;
                        else tab[par][3] = ch;
                        free(tab[cur]);
                        live[cur] = 0;
                    }
                    break;
                }
                acc = acc * 31 + 2;
            } else {
                acc = acc * 31 + SENT;
            }
        } else {
            /* THE SAFETY LINE. c/kernel.c writes
             *     if (g_saved != NULL)
             * here and those two conjuncts are the whole difference between the
             * two cells. This rung spells them and adds nothing else. */
            if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key) {
                acc = acc * 31 + (uint64_t)g_saved[1];
            } else {
                acc = acc * 31 + SENT;
            }
        }
    }
    for (j = 0; j < TABCAP; j++) {
        if (live[j] == 1) {
            free(tab[j]);
            live[j] = 0;
        }
    }
    return acc * 31 + (uint64_t)ntab;
}
