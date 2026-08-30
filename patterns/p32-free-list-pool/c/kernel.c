/* p32 rung R1 -- idiomatic C99 free-list allocator / object pool with
 * recycling. THE BUG.
 *
 * CWE-416 (use after free) and CWE-415 (double free), both reached through
 * CWE-672 (operation on a resource after expiration). Every handle-consuming
 * path -- FREE, READ and WRITE -- asks whether the handle register holds a
 * handle at all, and does not ask whether that handle names the CURRENT
 * incarnation of the block.
 *
 * **The missing conjunct is `else if (gen[h] != g)`**, at the ONE site marked
 * below, and it is the only difference between this file and
 * c/kernel_hardened.c. `../controls/safety_line.py` preprocesses both and diffs
 * them, so that claim is measured rather than asserted.
 *
 * FREE, READ and WRITE all consume the handle in register `r`, so they share
 * its decode and they share one guard -- which is why the omission is ONE
 * source line and not three. ../spec.md makes the same point the other way
 * round: **one omitted line, two bug classes, selected by the input**, which is
 * `p29`'s shipped shape.
 *
 * **ONE OMITTED CONJUNCT, TWO BUG CLASSES, SELECTED BY THE INPUT.**
 *
 *   FREE with a stale handle   the block is pushed a SECOND time. `nx[h] =
 *                              freehead` with `freehead == h` SELF-LOOPS the
 *                              list, so every later ALLOC returns the SAME
 *                              slot: two live handles ALIAS one block and the
 *                              rest of the free list is lost.
 *   READ with a stale handle   the block was recycled, so the read returns the
 *                              NEW OCCUPANT's payload.
 *
 * **What this rung KEEPS.** The `h == NIL` test, so a register that never held
 * a handle folds SENT in both rungs and the bug is not "read uninitialised".
 * `gen[]`, maintained exactly as the hardened rung maintains it -- this rung
 * BUMPS the generation on every free and never consults it, which is the bug
 * written out. `regs[]`/`regg[]`, written only by ALLOC. The pool, whose extent
 * is a compile-time constant. **The whole of the bug is that the three paths
 * holding a handle do not ask whether it is still current.**
 *
 * ⚠⚠ **THIS RUNG EXECUTES NO UNDEFINED BEHAVIOUR.** `regs[r]` is NIL or a real
 * slot, `freehead` is NIL or a real slot, and `nx[]` only ever holds values
 * drawn from those two, so every `pool[h*BLK+1]`, `nx[h]` and `gen[h]` is in
 * bounds in every run. The storage is a pool the program owns from start to
 * finish and nothing is ever `free`d, so **ASan, UBSan and Miri are silent on
 * every input this pattern ships, adversarial ones included.** That is the
 * row's detector-coverage result and not an oversight; `../controls/
 * storage_arms.py` rebuilds the same algorithm with per-block `malloc`/`free`
 * storage and shows exactly which of the harms become visible when it does.
 *
 * **`regs[r]` is deliberately NOT cleared on the free** -- p27's and p29's
 * argument, restated in c/kernel.h: clearing it would turn a stale use into the
 * `h == NIL` case, which folds SENT in BOTH rungs, and that is a different bug
 * class.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9), so `acc*31 + x` and
 * `gen[h] + 1` need no special spelling. */
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
            /* THE SAFETY LINE. c/kernel_hardened.c writes
             *     } else if (gen[h] != g) {
             *         v = SENT;
             * here and that ONE conjunct, at this ONE site, is the whole
             * difference between the two cells. This rung omits it and nothing
             * else. */
            if (h == NIL) {
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
