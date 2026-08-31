/* p34 rung R1 -- idiomatic C99 manual reference counting over a stack of heap
 * objects. THE BUG.
 *
 * CWE-911 (improper reference count update) reaching CWE-416 (use after free).
 * `DUP` publishes a SECOND reference to the object on the top of the stack and
 * **does not retain it**. Every later release therefore over-decrements, the
 * object is freed while a live stack entry still names it, and the next use of
 * that entry -- a release that reads `o->rc`, or a `READ` that reads
 * `o->data[0]` -- touches a freed block.
 *
 * **The missing line is `t->rc = t->rc + 1;`**, at the ONE site marked below,
 * and it is the only difference between this file and c/kernel_hardened.c.
 * `../controls/safety_line.py` preprocesses both and diffs them, so that claim
 * is measured rather than asserted: `+1 / -0` preprocessed lines.
 *
 * ⚠⚠ **THE READ PATH IS CORRECT IN THIS FILE AND ASKS NOTHING WRONG.** That is
 * what separates p34 from every built temporal row: a refcounted pointer is
 * valid by construction, so there is no test the READ could grow that would
 * repair this program without becoming a liveness table. The free happens EARLY
 * rather than the read happening LATE. c/kernel.h states the distinction against
 * p27, p29 and p32 side by side.
 *
 * **What this rung KEEPS.** The `ntop > 0` and `ntop < CAP` guards, so a `DUP`
 * of an empty stack and a `NEW` past the capacity fold SENT in both rungs and
 * the bug is not "read uninitialised". The decrement and the `rc == 0` test on
 * the release path, spelled exactly as the hardened rung spells them -- this
 * rung RELEASES correctly and never ACQUIRES, which is the bug written out. The
 * epilogue, which releases every entry the window left on the stack. **The whole
 * of the bug is that publishing a second reference does not count it.**
 *
 * ⚠⚠ **THIS RUNG EXECUTES NO SPATIAL UNDEFINED BEHAVIOUR.** `stk[ntop-1]` runs
 * only under `ntop > 0`, `stk[ntop++]` only under `ntop < CAP`, and READ's index
 * is `a % ntop` under `ntop > 0`, so every index is inside `stk[]` in every run
 * of both rungs. Its undefined behaviour is entirely TEMPORAL, which is why ASan
 * reports it and **UBSan says nothing at all, at either optimisation level on
 * either compiler** (../NOTES.md 2; ../controls/detectors.py ships a
 * UBSan-specific positive control, because a positive control licenses only the
 * detector it fires in).
 *
 * ⚠ **LAYOUT NOTE, DISCLOSED, the same way p28 discloses its own.** The refcount
 * header comes first and the payload starts at offset 16, so glibc's tcache
 * `next` and `key` words -- user offsets 0 and 8 -- land on `rc` and `len` and
 * never on `data`. R1's stale READ therefore returns the RIGHT byte in a plain
 * build, and the release path folds a constant that does not depend on `rc`; so
 * on the `DUP POP POP` and `DUP POP READ` shapes **the two rungs' checksums are
 * bit-identical and ASan is the only discriminator.** This is the idiomatic
 * layout for a refcounted buffer, not a layout chosen to hide the harm.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9), so `acc*31 + v` and
 * `o->rc - 1` need no special spelling. */
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
                /* THE SAFETY LINE. c/kernel_hardened.c writes
                 *     t->rc = t->rc + 1;
                 * here -- a new reference is being created, so the object must
                 * be retained -- and that ONE statement, at this ONE site, is
                 * the whole difference between the two cells. This rung omits
                 * it and nothing else. */
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
