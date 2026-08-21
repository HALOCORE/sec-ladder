/* p27 rung R1 -- idiomatic C99 handle table. THE BUG.
 *
 * CWE-416 (use after free), reached through CWE-672 (operation on a resource
 * after expiration). The READ path checks that the slot number is in range and
 * does not check that the record behind it is still alive; `tab[h]` is a
 * dangling pointer for every slot a CLOSE has retired, and this rung
 * dereferences it.
 *
 * **The missing conjunct is `&& live[h] == 1`**, on line 92 below, and it is the
 * only difference between this file and c/kernel_hardened.c.
 *
 * **What this rung KEEPS.** `h < ntab`, so the table read itself is in bounds --
 * the bug is not spatial. `live[]`, maintained exactly as the hardened rung
 * maintains it, so CLOSE is idempotent and there is no double free. The capacity
 * guard `ntab < TABCAP`. The epilogue, so nothing leaks. **The whole of the bug
 * is that the READ does not ask.**
 *
 * **Why the liveness bit cannot be "the pointer is NULL".** The handle in the op
 * stream is a slot NUMBER -- it comes out of a file and a file cannot name a
 * pointer. So the read has an index and must consult something to learn whether
 * the record is there; nulling `tab[h]` on close would turn the stale read into
 * a NULL dereference, which is a *crash*, not a use-after-free, and a different
 * bug class. Real handle tables carry a generation counter for exactly this
 * reason; `live[]` is that counter with slot reuse removed, which reduces it to
 * one bit. ../spec.md and c/kernel.h argue this at length.
 *
 * **RECSZ is 1.** A record is one byte, individually `malloc`'d. The unit of
 * this pattern is the ALLOCATION, not the payload: a wider record multiplies the
 * proof obligation by RECSZ and moves nothing else, and a one-byte record keeps
 * the fold identical to every other pattern's (`acc = acc*31 + byte`).
 *
 * `malloc` failure aborts. That is what Rust's global allocator does on OOM and
 * what `vstd::raw_ptr::allocate` does (`raw_ptr.rs:933`), so all seven rungs
 * agree; it is unreachable at RECSZ = 1 on this box and is present so that they
 * agree, not because it fires.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). The undefined behaviour
 * this rung executes is the LOAD through the dangling `tab[h]`. */
#include <stdlib.h>
#include <string.h>

#include "kernel.h"

#define TABCAP 32
#define RECSZ 1
#define SENT 251

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t *tab[TABCAP];
    uint8_t live[TABCAP];
    size_t nops, o, p, ntab, h, j;
    uint8_t c, a;
    uint64_t acc = 0;

    (void)buf_len; /* p27's bound is not this one -- it is the record's life. */

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    memset(tab, 0, sizeof tab);
    memset(live, 0, sizeof live);
    ntab = 0;
    p = 4;
    for (o = 0; o < nops; o++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        h = (size_t)a;
        if (c % 4 == 0) {
            if (ntab < TABCAP) {
                uint8_t *q = (uint8_t *)malloc(RECSZ);
                if (q == NULL)
                    abort();
                *q = a;
                tab[ntab] = q;
                live[ntab] = 1;
                ntab++;
                acc = acc * 31 + (uint64_t)a;
            } else {
                acc = acc * 31 + SENT;
            }
        } else if (c % 4 == 1) {
            if (h < ntab && live[h] == 1) {
                free(tab[h]);
                live[h] = 0;
                acc = acc * 31 + 1;
            } else {
                acc = acc * 31 + SENT;
            }
        } else {
            /* THE SAFETY LINE. c/kernel_hardened.c writes
             *     if (h < ntab && live[h] == 1)
             * here and that one conjunct is the whole difference between the
             * two cells. This rung omits it and nothing else. */
            if (h < ntab) {
                acc = acc * 31 + (uint64_t)*tab[h];
            } else {
                acc = acc * 31 + SENT;
            }
        }
    }
    for (j = 0; j < ntab; j++) {
        if (live[j] == 1) {
            free(tab[j]);
            live[j] = 0;
        }
    }
    return acc * 31 + (uint64_t)ntab;
}
