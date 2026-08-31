/* p25 rung R1h -- c/kernel.c plus THE SAFETY LINE and nothing else.
 *
 * The safety line is the conjunct `curbase == toks` on the READ path, with a
 * RE-DERIVE from the current base when it fails: the container may have moved
 * since the interior pointer was taken, so ask, and recompute the address when
 * the answer is no. `../controls/safety_line.py` preprocesses this file and
 * c/kernel.c with `cc -E -P` and diffs them, so the size of the line is
 * measured rather than asserted.
 *
 * ⚠⚠ **THE `else` BRANCH RE-DERIVES RATHER THAN FOLDING A SENTINEL, AND THAT IS
 * A CORRECTNESS REQUIREMENT AND NOT A STYLE CHOICE.** A rung that folded `SENT`
 * on relocation would make this kernel's ANSWER a function of the ALLOCATOR --
 * `model.py` could not derive the checksum without simulating glibc, and the
 * four Rust rungs, whose `Vec` grows on a different schedule, could not agree
 * with the C ones on the adversarial input. Re-deriving is allocator-independent
 * because `realloc` COPIES: `toks[curi]` after the move is the byte `*cur` named
 * before it. ../NOTES.md 3 measures the alternative and reports what it costs.
 *
 * ⚠ **So this conjunct buys MEMORY SAFETY and buys nothing else** -- both
 * branches compute the same value in every terminating execution -- which makes
 * the R1-vs-R1h gradient a clean price for memory safety alone.
 *
 * ⚠⚠ **AND IT IS NOT THE STANDARD-CLEAN REPAIR.** C11 7.22.3.5p4 with DR 400
 * makes `cur` indeterminate the moment `realloc` returns, **whether or not the
 * block moved**, so the surviving `*cur` in the true branch is a use of an
 * indeterminate value under the abstract machine even though no relocating
 * allocator can observe it. The standard-clean rung is the UNCONDITIONAL
 * re-derive; ../controls/rederive.py builds it and prices it, and ../NOTES.md 3c
 * reports both. This file ships the conjunct because it is what a C programmer
 * writes and because it is the form that lets the row measure a CHECK rather
 * than an addressing mode.
 *
 * **This rung is CORRECT, not merely better.** `curi < ntok` holds from the
 * moment the SAVE records it -- `ntok` never shrinks -- so `toks[curi]` is in
 * bounds at every later READ, and it names the element the saved pointer named,
 * because `realloc` copies the old contents forward. So this rung agrees with
 * `model.py` on EVERY input, benign and adversarial, and dereferences `cur` only
 * when the block has not moved.
 *
 * Everything else in this file is character-identical to c/kernel.c, including
 * the guards and the reasons they are where they are. */
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
            } else if (curbase == toks) {
                /* THE SAFETY LINE. c/kernel.c omits exactly this conjunct and
                 * the re-derive it guards, and nothing else. */
                v = (uint64_t)*cur;
            } else {
                v = (uint64_t)toks[curi];
            }
        }
        (void)curbase; /* character-identical to c/kernel.c; a no-op here. */
        (void)curi;    /* character-identical to c/kernel.c; a no-op here. */
        acc = acc * 31 + v;
    }

    free(toks);
    free(strs);
    return acc * 31 + (uint64_t)(ntok + nstr);
}
