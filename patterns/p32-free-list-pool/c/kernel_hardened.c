/* p32 rung R1h -- hardened C99 free-list allocator / object pool with recycling.
 *
 * c/kernel.c with ONE conjunct added at the ONE site where a handle is
 * consumed:
 *
 *     } else if (gen[h] != g) {
 *         v = SENT;
 *
 * and that is the whole difference between the two cells. FREE, READ and WRITE
 * share the handle decode, so they share the guard; the omission is one source
 * line and it carries both bug classes.
 * `../controls/safety_line.py` PREPROCESSES both files and diffs them, so this
 * sentence is measured on the shipped sources rather than asserted: it reports
 * the `+N / -0` line count and fails if the diff stops being an ADDITION.
 *
 * **WHAT THE CONJUNCT NOTICES, AND WHY NOTHING ELSE CAN.** `h == NIL` asks
 * whether the register ever held a handle. `gen[h] == g` asks whether the block
 * that handle names is still the SAME INCARNATION. The second question is
 * invisible to every allocation-shaped mechanism, because in this pattern the
 * allocator never runs: the pool is a local array the program owns from start
 * to finish, so there is no `free` for ASan to record, no drop for Rust to
 * insert, and no `PointsTo` for a proof to consume. `../NOTES.md` 2 measures
 * all of them.
 *
 * **WHAT IT BUYS, STATED AS AN INVARIANT** (c/kernel.h argues it in full): with
 * this conjunct the free list is always a SET OF DISTINCT SLOTS and no two
 * handle registers ever hold valid handles to one slot, so this rung can
 * neither double-push nor alias. Without it, `nx[h] = freehead` with
 * `freehead == h` SELF-LOOPS the list and every later ALLOC returns the same
 * slot.
 *
 * **THE ORDER IS NOT LOAD-BEARING HERE, AND THAT IS A DIFFERENCE FROM `p29`.**
 * `p29` must test liveness before identity, because the identity test would
 * otherwise itself be a use-after-free; its two conjuncts are not
 * interchangeable and at R5 the ordering is forced by a precondition. Here
 * `gen[h]` is an ordinary in-bounds array read for any `h < SLOTS`, so
 * `h == NIL` and `gen[h] == g` could be written in either order and in one
 * `&&`. They are written as a chain of `else if` because that is what makes the
 * preprocessed diff an ADDITION -- `+N / -0` -- rather than a rewrite.
 *
 * Everything else -- `gen[]` and its maintenance, `regs[]`/`regg[]`, the pool,
 * the `h == NIL` test, the fold -- is identical to R1, because R1 already has
 * all of it. R1 MAINTAINS the generation on every free and consults it nowhere.
 * See c/kernel.c and c/kernel.h. */
#include <string.h>

#include "kernel.h"

#define SLOTS 8
#define BLK 4
#define NREG 8
#define NIL 255
#define SENT 251

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t pool[SLOTS * BLK];
    uint8_t nx[SLOTS];
    uint32_t gen[SLOTS];
    uint8_t regs[NREG];
    uint32_t regg[NREG];
    uint8_t freehead;
    size_t nops, o, p, j, r, nalloc;
    uint8_t c, a, h;
    uint32_t g;
    uint64_t acc = 0, v;

    (void)buf_len; /* p32's bound is not this one -- it is the block's incarnation. */

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    memset(pool, 0, sizeof pool);
    for (j = 0; j < SLOTS; j++) {
        nx[j] = (uint8_t)((j + 1 < SLOTS) ? (j + 1) : NIL);
        gen[j] = 0;
    }
    for (j = 0; j < NREG; j++) {
        regs[j] = NIL;
        regg[j] = 0;
    }
    freehead = 0;
    nalloc = 0;
    p = 4;
    /* R1 DECODES the handle's generation and never consults it -- that is the
     * bug, written out. The cast is here, in both C rungs, so that R1 compiles
     * warning-free under -Wall -Wextra and the two files differ by the safety
     * line and nothing else. (p29/c/kernel.c does the same for `g_slot`.) */
    (void)g;

    for (o = 0; o < nops; o++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        r = (size_t)(a % NREG);
        if (c % 4 == 0) {
            /* ALLOC: pop the free list into handle register r. **Nothing is
             * allocated** -- the block already exists and always did. */
            if (freehead == NIL) {
                v = SENT;
            } else {
                uint8_t s = freehead;
                uint32_t gs;
                freehead = nx[s];
                pool[(size_t)s * BLK] = a;
                pool[(size_t)s * BLK + 1] = (uint8_t)(a * 7u + 1u);
                regs[r] = s;
                gs = gen[s];
                regg[r] = gs;
                nalloc++;
                v = (uint64_t)s + 8 * (uint64_t)gs;
            }
        } else {
            /* FREE, READ and WRITE all consume the handle in register r, so
             * they share its decode and they share the one guard below. */
            h = regs[r];
            g = regg[r];
            /* THE SAFETY LINE. c/kernel.c writes
             *     if (h == NIL) {
             *         v = SENT;
             * and goes straight on to the opcode arms. That ONE conjunct, at
             * this ONE site, is the whole difference between the two cells.
             * This rung spells it and adds nothing else. */
            if (h == NIL) {
                v = SENT;
            } else if (gen[h] != g) {
                v = SENT;
            } else if (c % 4 == 1) {
                gen[h] = gen[h] + 1;
                nx[h] = freehead;
                freehead = h;
                v = 1;
            } else if (c % 4 == 2) {
                v = (uint64_t)pool[(size_t)h * BLK + 1];
            } else {
                pool[(size_t)h * BLK + 1] = (uint8_t)(a * 13u + 3u);
                v = 3;
            }
        }
        acc = acc * 31 + v;
    }
    return acc * 31 + (uint64_t)nalloc;
}
