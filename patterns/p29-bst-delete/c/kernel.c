/* p29 rung R1 -- idiomatic C99 binary search tree with a cached lookup result.
 * THE BUG.
 *
 * CWE-416 (use after free), reached through CWE-672 (operation on a resource
 * after expiration). A FIND saves the address of the record it found; a later
 * USE reads through that address and asks only whether a FIND ever succeeded.
 * It never asks whether the record is still there, and it never asks whether
 * the record still holds the key it was found under.
 *
 * **The missing safety line is in the `c % 4 == 3` arm** -- the USE path, the
 * last of the four -- and it is the only difference between this file and
 * c/kernel_hardened.c, which writes
 *
 *     if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key)
 *
 * there. One line, and it is the whole difference between the two cells.
 * ⚠ This line used to add *"TWO conjuncts, where p27's hardened cell adds
 * ONE"* and invite the reader to draw the row from that count. The count is
 * accurate about what the two files SPELL and it is not the row: p29's line
 * can be spelled with one conjunct too (TASK_140, measured). See c/kernel.h.
 *
 * **ONE OMISSION, TWO BUG CLASSES, SELECTED BY THE INPUT.**
 *
 *   the saved record has 0 or 1 children  the splice FREES it
 *                                         -> a genuine heap-use-after-free,
 *                                            ASan aborts, and what the read
 *                                            returns is not reproducible
 *   the saved record has 2 children       the splice copies the in-order
 *                                         successor's key and val INTO it and
 *                                         frees the SUCCESSOR
 *                                         -> the read is in bounds of a LIVE
 *                                            allocation whose occupant changed:
 *                                            ASan is silent, the wrong answer
 *                                            is stable, and no allocation-
 *                                            shaped instrument sees it
 *
 * **What this rung KEEPS.** The `live[cur] == 1` conjunct and the `steps`
 * bound on every walk, so no walk can follow a link into a retired slot and
 * none can run away -- the bug is not spatial and not a hang. `live[]`,
 * maintained exactly as the hardened rung maintains it, so the epilogue frees
 * each record once and neither rung can double-free. The capacity guard
 * `ntab < TABCAP`. The epilogue, so nothing leaks. **The whole of the bug is
 * that the one path holding a raw pointer does not consult the table.**
 *
 * **`tab[cur]` is deliberately NOT set to NULL after the free** -- p27's
 * argument, restated in c/kernel.h with a measurement behind it.
 *
 * **RECSZ is 4.** A record is `key, val, left, right`, individually `malloc`'d.
 * The links are inside the record because that is what makes the two-child
 * delete copy the payload rather than move a pointer, and the copy is the
 * second bug class.
 *
 * `malloc` failure aborts. That is what Rust's global allocator does on OOM and
 * what `vstd::raw_ptr::allocate` does, so all seven rungs agree.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). The undefined behaviour
 * this rung executes is the LOAD through the dangling `g_saved`. */
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
            /* THE SAFETY LINE. c/kernel_hardened.c writes
             *     if (g_saved != NULL && live[g_slot] == 1
             *         && tab[g_slot][0] == g_key)
             * here and those two conjuncts are the whole difference between the
             * two cells. This rung omits them and nothing else. */
            if (g_saved != NULL) {
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
