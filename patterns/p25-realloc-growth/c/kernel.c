/* p25 rung R1 -- idiomatic C99 dynamic array grown with `realloc`, with an
 * interior pointer held across the growth. THE BUG.
 *
 * CWE-416 (use after free) reached through CWE-825 (expired pointer
 * dereference). The kernel saves `cur = &toks[curi]`, keeps parsing, and a later
 * `PUSHT` grows the token vector with `realloc`. When the block relocates the
 * old one is retired -- **the program never calls `free` on it, `realloc` does**
 * -- and the next `READ` dereferences a pointer into storage the allocator has
 * taken back.
 *
 * **The missing conjunct is `curbase == toks`**, at the ONE site marked below,
 * and it is the only difference between this file and c/kernel_hardened.c.
 * `../controls/safety_line.py` preprocesses both and diffs them, so that claim
 * is measured rather than asserted.
 *
 * ⚠⚠ **THIS RUNG EXECUTES NO SPATIAL UNDEFINED BEHAVIOUR.** `toks[ntok]` is
 * written only after the block has been grown to hold it, `&toks[a % ntok]` is
 * formed only under `ntok > 0`, and the cursor guard is subtraction-first. Its
 * undefined behaviour is entirely TEMPORAL, which is why ASan reports it and
 * **UBSan says nothing at all** (../NOTES.md 2; ../controls/detectors.py ships a
 * UBSan-specific positive control, because a positive control licenses only the
 * detector it fires in).
 *
 * ⚠ **What this rung KEEPS.** The `ntok < MAXCAP` and `nstr < MAXCAP` guards, so
 * a push past the capacity folds SENT in both rungs and the bug is not "write
 * out of bounds". The `cur == NULL` guard, so a READ before any SAVE folds SENT
 * in both rungs and the bug is not "read an uninitialised pointer". The saved
 * base and the saved index, MAINTAINED AND NEVER CONSULTED -- that is the bug,
 * written out, and the `(void)` casts below keep both rungs warning-free under
 * `-Wall -Wextra` so the two differ by the safety line and nothing else.
 *
 * ⚠ **THE HARM WINDOW IS ONE GROWTH WIDE.** glibc extends the token block in
 * place at `4 -> 8` and `8 -> 16`; it is `16 -> 32` that must move, because by
 * then the string vector sits behind it. c/kernel.h has the measurement and
 * ../controls/reloc_probe.py re-derives it on this file.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9), so `acc*31 + v` needs no
 * special spelling. */
#include <stdlib.h>
#include <string.h>

#include "kernel.h"

#define P25_SEED 4
#define P25_MAXCAP 64
#define P25_SENT 251

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t *toks = NULL, *strs = NULL;
    const uint8_t *cur = NULL, *curbase = NULL;
    size_t ntok = 0, tcap = 0, nstr = 0, scap = 0, curi = 0;
    size_t nops, i, p;
    uint8_t c, a;
    uint64_t acc = 0, v;

    (void)buf_len; /* p25's bound is not this one -- it is the block's lifetime. */

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    p = 4;

    for (i = 0; i < nops; i++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        if (c % 4 == 0) {
            /* PUSHT: append to the token vector, doubling with realloc. */
            if (ntok < P25_MAXCAP) {
                if (ntok == tcap) {
                    size_t nc = tcap ? tcap * 2 : P25_SEED;
                    uint8_t *nt = (uint8_t *)realloc(toks, nc);
                    if (nt == NULL)
                        abort();
                    toks = nt;
                    tcap = nc;
                }
                toks[ntok] = a;
                ntok = ntok + 1;
                v = (uint64_t)a;
            } else {
                v = P25_SENT;
            }
        } else if (c % 4 == 1) {
            /* PUSHS: append to the string vector. A SECOND live growable
             * allocation, which is what stops the first extending in place. */
            if (nstr < P25_MAXCAP) {
                if (nstr == scap) {
                    size_t nc = scap ? scap * 2 : P25_SEED;
                    uint8_t *ns = (uint8_t *)realloc(strs, nc);
                    if (ns == NULL)
                        abort();
                    strs = ns;
                    scap = nc;
                }
                strs[nstr] = a;
                nstr = nstr + 1;
                v = (uint64_t)a;
            } else {
                v = P25_SENT;
            }
        } else if (c % 4 == 2) {
            /* SAVE an interior pointer into the token vector, and the base and
             * index it was derived from. Both rungs record all three. */
            if (ntok > 0) {
                curi = (size_t)a % ntok;
                cur = &toks[curi];
                curbase = toks;
                v = 2;
            } else {
                v = P25_SENT;
            }
        } else {
            /* READ through the saved interior pointer. */
            if (cur == NULL) {
                v = P25_SENT;
            } else {
                /* THE SAFETY LINE. c/kernel_hardened.c writes
                 *     } else if (curbase == toks) {
                 *         v = (uint64_t)*cur;
                 *     } else {
                 *         v = (uint64_t)toks[curi];
                 * here -- the container may have RELOCATED since the pointer was
                 * taken, so ask, and re-derive from the current base when it
                 * has. This rung omits exactly that conjunct and nothing else. */
                v = (uint64_t)*cur;
            }
        }
        (void)curbase; /* R1 maintains the base and consults it nowhere. */
        (void)curi;    /* R1 maintains the index and consults it nowhere. */
        acc = acc * 31 + v;
    }

    free(toks);
    free(strs);
    return acc * 31 + (uint64_t)(ntok + nstr);
}
