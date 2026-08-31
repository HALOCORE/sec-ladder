/* p34 CONTROLS -- THE INCLUDE-TWICE CONSTRUCTION.
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

#define P34_CAP 16
#define P34_DLEN 8
#define P34_SENT 251

struct p34_obj {
    size_t rc;              /* offset 0  -- glibc's tcache `next` when freed */
    size_t len;             /* offset 8  -- glibc's tcache `key`  when freed */
    uint8_t data[P34_DLEN]; /* offset 16 -- survives a free */
};

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    struct p34_obj *stk[P34_CAP];
    struct p34_obj *o, *t;
    size_t nops, i, p, ntop, nnew;
    uint8_t c, a;
    uint64_t acc = 0, v;

    (void)buf_len;

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    ntop = 0;
    nnew = 0;
    p = 4;

    for (i = 0; i < nops; i++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        if (c % 4 == 0) {
            if (ntop < P34_CAP) {
                o = (struct p34_obj *)malloc(sizeof *o);
                if (o == NULL)
                    abort();
                o->rc = 1;
                o->len = P34_DLEN;
                memset(o->data, 0, P34_DLEN);
                o->data[0] = (uint8_t)(a * 7u + 1u);
                stk[ntop] = o;
                ntop = ntop + 1;
                nnew = nnew + 1;
                v = (uint64_t)a;
            } else {
                v = P34_SENT;
            }
        } else if (c % 4 == 1) {
            if (ntop > 0 && ntop < P34_CAP) {
                t = stk[ntop - 1];
#if SLB_HARDEN
                /* ===================== THE SAFETY LINE ======================
                 * A new reference is being created, so the object must be
                 * retained. `../c/kernel.c` omits exactly this statement. */
                t->rc = t->rc + 1;
                /* ========================================================== */
#endif
                stk[ntop] = t;
                ntop = ntop + 1;
                v = 1;
            } else {
                v = P34_SENT;
            }
        } else if (c % 4 == 2) {
            if (ntop > 0) {
                ntop = ntop - 1;
                o = stk[ntop];
                o->rc = o->rc - 1;
                if (o->rc == 0)
                    free(o);
                v = 2;
            } else {
                v = P34_SENT;
            }
        } else {
            if (ntop > 0) {
                v = (uint64_t)stk[(size_t)a % ntop]->data[0];
            } else {
                v = P34_SENT;
            }
        }
        acc = acc * 31 + v;
    }

    while (ntop > 0) {
        ntop = ntop - 1;
        o = stk[ntop];
        o->rc = o->rc - 1;
        if (o->rc == 0)
            free(o);
    }
    return acc * 31 + (uint64_t)nnew;
}
