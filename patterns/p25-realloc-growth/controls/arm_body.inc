/* p25 CONTROLS -- THE INCLUDE-TWICE CONSTRUCTION.
 *
 * ONE kernel body, included with `SLB_HARDEN` 0 and 1. `TASK_143` used this
 * shape to make *"the hardened cell is the buggy cell plus the safety line"*
 * true by construction; ⚠ **it is not available to a SHIPPED rung**, because
 * `harness/check.py`'s `forbidden` audit reads the rung sources as TEXT
 * (`rung_sources` -> `exec_code` -> `spelling_matches`) and a `forbidden` hit is
 * one of the few things in stage 0b that can FAIL the gate: a kernel body moved
 * into an `.inc` would be in neither C rung's text, so a forbidden spelling
 * could sit in it unseen.
 *
 * So `../c/kernel.c` and `../c/kernel_hardened.c` are written out in full, and
 * this file is what `safety_line.py` uses to prove that writing them out did not
 * let them drift: it preprocesses THIS body at both `SLB_HARDEN` values and
 * requires each result to equal the corresponding SHIPPED file's preprocessed
 * text **exactly**. That is strictly stronger than either construction alone --
 * the include-twice form cannot fail, and a diff of two hand-written files
 * cannot say that the difference is the *intended* one.
 *
 * Kept byte-parallel with the shipped files: any edit there needs the same edit
 * here, and `safety_line.py` FAILS loudly if one is made without the other.
 */
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

    (void)buf_len;

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
            if (ntok > 0) {
                curi = (size_t)a % ntok;
                cur = &toks[curi];
                curbase = toks;
                v = 2;
            } else {
                v = P25_SENT;
            }
        } else {
            if (cur == NULL) {
                v = P25_SENT;
#if SLB_HARDEN
            } else if (curbase == toks) {
                v = (uint64_t)*cur;
            } else {
                v = (uint64_t)toks[curi];
            }
#else
            } else {
                v = (uint64_t)*cur;
            }
#endif
        }
        (void)curbase;
        (void)curi;
        acc = acc * 31 + v;
    }

    free(toks);
    free(strs);
    return acc * 31 + (uint64_t)(ntok + nstr);
}
