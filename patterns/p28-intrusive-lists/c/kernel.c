/* p28 rung R1 -- idiomatic C99 object cache with TWO intrusive link sets.
 * THE BUG.
 *
 * CWE-416 (use after free), reached through CWE-672 (operation on a resource
 * after expiration). TRIM reclaims the oldest object. It reaches
 * that object through the EVICTION LIST, unlinks it from the eviction list, and frees it.
 * **It never leaves the HASH CHAIN.** The freed object's chain predecessor keeps
 * `hn == victim`, or `bucket[b]` does, and the next walk of that bucket reads
 * through it.
 *
 * **The missing safety line is in the `c % 4 == 3` arm** -- the TRIM path, the
 * last of the four -- and it is the only difference between this file and
 * c/kernel_hardened.c, which writes
 *
 *     vb = (size_t)(victim->key % P28_NB);
 *     if (victim->hp != NULL) victim->hp->hn = victim->hn;
 *     else                    bucket[vb]     = victim->hn;
 *     if (victim->hn != NULL) victim->hn->hp = victim->hp;
 *
 * there. Nine preprocessed lines, and they are the whole difference between the
 * two cells (controls/safety_line.py measures it).
 *
 * **THE READ PATH IS CORRECT AND THE DESTROY PATH IS INCOMPLETE.** Nothing in
 * PUT, GET or DEL is missing a test: they walk a chain and use the object they
 * reach, which is what a hash chain is for. That is the INVERSION of p27, p29
 * and p32, all three of which keep a correct free discipline and put the
 * missing check on the READ. There is no test to add on this rung's read path;
 * the object it reaches is one this rung's DESTROY path should never have left
 * reachable.
 *
 * **ONE OMISSION, TWO HARM SHAPES, SELECTED BY THE INPUT** -- a later GET on the
 * victim's bucket is a use-after-free READ, a later DEL is a use-after-free
 * WRITE that lands on a THIRD object. c/kernel.h tabulates both.
 *
 * **What this rung KEEPS.** The eviction-list unlink in TRIM, so that list --
 * which is the OWNERSHIP list -- stays exact and the epilogue frees each live
 * object exactly once: **neither rung leaks and neither double-frees.** The full
 * two-list splice in DEL. The allocation budget `nmade < P28_SLOTS` and the walk
 * fuel `steps < P28_SLOTS`. **The whole of the bug is that one of the two lists
 * is left holding a pointer to storage the program has returned to the
 * allocator.**
 *
 * **`bucket[b]` and the predecessor's `hn` are deliberately NOT cleared** -- they
 * are not cleared because nothing on this path knows they exist. That is the
 * point: p27 and p29 have a stale reference IN A VARIABLE THE FREEING CODE CAN
 * SEE; here it is in a field of a different heap object.
 *
 * The links come FIRST in the struct -- the Linux `list_head`-embedded-first
 * layout -- which is what makes R1's stale read reproducible. c/kernel.h's
 * LAYOUT NOTE says why and what it costs.
 *
 * `malloc` failure aborts. That is what Rust's global allocator does on OOM and
 * what `vstd::raw_ptr::allocate` does, so all seven rungs agree.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). The undefined behaviour
 * this rung executes is the load or the store through a link that names a freed
 * object. */
#include <stdlib.h>
#include <string.h>

#include "kernel.h"

#define P28_NB 8
#define P28_SLOTS 48
#define SENT 251

struct p28_obj {
    struct p28_obj *lp, *ln; /* intrusive doubly linked eviction list   */
    struct p28_obj *hn, *hp; /* intrusive doubly linked hash chain */
    uint8_t key, val;
};

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    struct p28_obj *bucket[P28_NB];
    struct p28_obj *head, *tail, *n, *victim;
    size_t nops, o, p, nmade, b, steps;
    uint8_t c, a;
    int found;
    uint64_t acc = 0;

    (void)buf_len; /* p28's bound is not this one -- it is the object's life. */

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    for (b = 0; b < P28_NB; b++)
        bucket[b] = NULL;
    head = NULL;
    tail = NULL;
    nmade = 0;
    p = 4;

    for (o = 0; o < nops; o++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        b = (size_t)(a % P28_NB);

        if (c % 4 == 0) {
            /* PUT. Walk the hash chain; a hit updates the object in place. */
            n = bucket[b];
            steps = 0;
            found = 0;
            while (n != NULL && steps < P28_SLOTS) {
                steps++;
                if (n->key == a) {
                    found = 1;
                    break;
                }
                n = n->hn;
            }
            if (found) {
                n->val = (uint8_t)(a * 7u + 1u);
                acc = acc * 31 + (uint64_t)a;
            } else if (nmade < P28_SLOTS) {
                n = (struct p28_obj *)malloc(sizeof *n);
                if (n == NULL)
                    abort();
                n->key = a;
                n->val = (uint8_t)(a * 7u + 1u);
                n->lp = NULL;
                n->ln = head;
                if (head != NULL)
                    head->lp = n;
                else
                    tail = n;
                head = n;
                n->hp = NULL;
                n->hn = bucket[b];
                if (bucket[b] != NULL)
                    bucket[b]->hp = n;
                bucket[b] = n;
                nmade++;
                acc = acc * 31 + (uint64_t)a;
            } else {
                acc = acc * 31 + SENT;
            }
        } else if (c % 4 == 1) {
            /* GET. Walks the hash chain. In R1 the chain can still contain a
             * FREED object, and `n->key` / `n->val` is then a use-after-free
             * READ. Nothing on this path is wrong: it is the destroy path that
             * left the pointer here. */
            n = bucket[b];
            steps = 0;
            found = 0;
            while (n != NULL && steps < P28_SLOTS) {
                steps++;
                if (n->key == a) {
                    found = 1;
                    break;
                }
                n = n->hn;
            }
            if (found)
                acc = acc * 31 + (uint64_t)n->val;
            else
                acc = acc * 31 + SENT;
        } else if (c % 4 == 2) {
            /* DEL. The same walk, then a SPLICE out of BOTH lists. DEL arrives
             * along the hash chain, so it is holding a chain cursor when it
             * frees -- which is exactly why DEL is not the path that forgets.
             * In R1 the walk can reach a freed object, and the splice then
             * WRITES through `n->hp`/`n->hn`/`n->lp`/`n->ln` read out of a freed
             * chunk -- the second harm shape of the one omission, and it lands
             * on a THIRD object. */
            n = bucket[b];
            steps = 0;
            found = 0;
            while (n != NULL && steps < P28_SLOTS) {
                steps++;
                if (n->key == a) {
                    found = 1;
                    break;
                }
                n = n->hn;
            }
            if (found) {
                if (n->hp != NULL)
                    n->hp->hn = n->hn;
                else
                    bucket[b] = n->hn;
                if (n->hn != NULL)
                    n->hn->hp = n->hp;
                if (n->lp != NULL)
                    n->lp->ln = n->ln;
                else
                    head = n->ln;
                if (n->ln != NULL)
                    n->ln->lp = n->lp;
                else
                    tail = n->lp;
                free(n);
                acc = acc * 31 + 2;
            } else {
                acc = acc * 31 + SENT;
            }
        } else {
            /* TRIM. Reclaim the oldest object. It arrives here
             * through the EVICTION LIST and therefore holds no hash-chain cursor.
             *
             * THE SAFETY LINE GOES HERE. c/kernel_hardened.c writes the
             * nine-line chain splice between `tail = victim->lp;` and
             * `free(victim);` and those nine lines are the whole difference
             * between the two cells. This rung omits them and nothing else. */
            if (tail != NULL) {
                victim = tail;
                if (victim->lp != NULL)
                    victim->lp->ln = NULL;
                else
                    head = NULL;
                tail = victim->lp;
                free(victim);
                acc = acc * 31 + 3;
            } else {
                acc = acc * 31 + SENT;
            }
        }
    }

    /* The epilogue. The eviction list is the OWNERSHIP list, so this frees each live
     * object exactly once in BOTH rungs -- the victim TRIM freed is not on it,
     * because TRIM unlinked it from the eviction list before freeing. Neither rung
     * leaks and neither double-frees here; the whole of the bug is the stale
     * hash-chain entry. */
    n = head;
    while (n != NULL) {
        struct p28_obj *nx = n->ln;
        free(n);
        n = nx;
    }
    return acc * 31 + (uint64_t)nmade;
}
