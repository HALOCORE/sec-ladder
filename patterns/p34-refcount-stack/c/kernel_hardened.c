/* p34 rung R1h -- c/kernel.c plus THE SAFETY LINE and nothing else.
 *
 * The safety line is `t->rc = t->rc + 1;` on the `DUP` path: a new reference is
 * being published, so the object must be retained. `../controls/safety_line.py`
 * preprocesses this file and c/kernel.c with `cc -E -P` and diffs them -- the
 * difference is a pure ADDITION of ONE line, `+1 / -0`, which is the smallest
 * safety line in this tree.
 *
 * **This rung is CORRECT, not merely better.** The invariant is
 *
 *   for every live object o, `o->rc` == the number of stack entries naming o
 *
 * established by NEW (one entry, `rc = 1`), preserved by DUP (one entry, one
 * increment), by POP and by the epilogue (one entry removed, one decrement, and
 * `free` exactly at zero). So this rung never frees an object a live stack entry
 * names, never frees one twice, and leaves nothing allocated when the call
 * returns. c/kernel.h has the argument in full.
 *
 * ⚠⚠ **AND IT IS FREE ON EVERY MEASURED INPUT, BY CONSTRUCTION RATHER THAN BY
 * LUCK.** The line executes only on a `DUP`, and a `DUP` in R1 always leads to a
 * use-after-free (c/kernel.h's two-line proof), so no input on which R1 and R1h
 * agree can contain one -- and `inputs/gen.py` enforces exactly that on every
 * matrix blob it writes. The R1-vs-R1h benign gradient is `0.00` because the
 * added statement is never executed, and ../NOTES.md 4 reports the MEASURED
 * instruction delta beside the prediction rather than leaving the zero implied.
 *
 * Everything else in this file is character-identical to c/kernel.c, including
 * the layout note and the reasons the guards are where they are. */
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

    (void)buf_len; /* p34's bound is not this one -- it is the object's lifetime. */

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
            /* NEW: one object, one reference. */
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
            /* DUP: publish a SECOND reference to the top object. */
            if (ntop > 0 && ntop < P34_CAP) {
                t = stk[ntop - 1];
                /* THE SAFETY LINE. c/kernel.c omits exactly this statement and
                 * nothing else. */
                t->rc = t->rc + 1;
                stk[ntop] = t;
                ntop = ntop + 1;
                v = 1;
            } else {
                v = P34_SENT;
            }
        } else if (c % 4 == 2) {
            /* POP: release one reference; free at zero. Correct in both rungs. */
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
            /* READ through the a-th reference on the stack. Correct in both
             * rungs: a refcounted reference is valid by construction. */
            if (ntop > 0) {
                v = (uint64_t)stk[(size_t)a % ntop]->data[0];
            } else {
                v = P34_SENT;
            }
        }
        acc = acc * 31 + v;
    }

    /* The epilogue: release every reference still on the stack. R2 and R3 do
     * not have it -- dropping the stack IS this loop, written by the language. */
    while (ntop > 0) {
        ntop = ntop - 1;
        o = stk[ntop];
        o->rc = o->rc - 1;
        if (o->rc == 0)
            free(o);
    }
    return acc * 31 + (uint64_t)nnew;
}
