/* p28 rung R1h -- the same idiomatic C99 object cache, WITH the safety line.
 *
 * This file is `c/kernel.c` plus ONE BLOCK and nothing else. The block is in the
 * `c % 4 == 3` arm -- TRIM -- and it is marked THE SAFETY LINE below.
 * `controls/safety_line.py` preprocesses both files with `cc -E -P` and diffs
 * them, so *"differs by the safety line and nothing else"* is a MEASUREMENT
 * (a pure `+9 / -0`) rather than an assertion.
 *
 * **WHY THIS RUNG IS CORRECT, and admission question 1 needs it to be.** The
 * invariant it restores is:
 *
 *   > every object reachable from `bucket[0..NB)` by following `hn`, and every
 *   > object reachable from `head` by following `ln`, is an object this kernel
 *   > has allocated and not yet freed
 *
 * -- i.e. **MEMBERSHIP OF EITHER LIST IMPLIES OWNERSHIP**, which is the property
 * the intrusive spelling makes so easy to break. PUT pushes a fresh object onto
 * both lists; DEL splices out of both and then frees; TRIM splices out of both
 * and then frees. Nothing else touches a link. So no link ever names storage the
 * kernel has returned, and the epilogue frees each live object exactly once
 * through the eviction list.
 *
 * (⚠ The invariant is stated for the reader. **No rung EVALUATES it** -- it is
 * not a runtime test, it is what the nine lines below maintain. R5 does not
 * prove it either; ../NOTES.md 6 says what R5 proves instead, and it is a
 * measured result rather than an omission.)
 *
 * ⚠ **The block is a SPLICE, not a SEARCH, and that is why it is nine lines and
 * not fifteen.** The hash chain is DOUBLY linked, so TRIM can leave it in O(1)
 * from the victim alone. With a SINGLY linked chain the same repair is a walk of
 * bucket `victim->key % P28_NB` looking for the victim, which preprocesses to
 * FIFTEEN lines. ../NOTES.md 1b measures both spellings: the doubly linked one
 * costs THREE shared lines in PUT (`n->hp = NULL;` and the two that maintain the
 * old chain head's `hp`) and saves six in the safety line.
 *
 * Everything else in this file -- every comment about the bug included -- is
 * c/kernel.c's, unchanged, so that a reader diffing the two sees the block and
 * nothing else. c/kernel.h carries the contract. */
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
             * THE SAFETY LINE IS BELOW. c/kernel.c has everything in this arm
             * except the marked block, and those nine preprocessed lines are the
             * whole difference between the two cells. */
            if (tail != NULL) {
                victim = tail;
                if (victim->lp != NULL)
                    victim->lp->ln = NULL;
                else
                    head = NULL;
                tail = victim->lp;
                /* ===================== THE SAFETY LINE =====================
                 * The victim is on TWO lists. Leave the hash chain as well as
                 * the eviction list before destroying it. c/kernel.c omits
                 * exactly this block and nothing else. */
                {
                    size_t vb = (size_t)(victim->key % P28_NB);
                    if (victim->hp != NULL)
                        victim->hp->hn = victim->hn;
                    else
                        bucket[vb] = victim->hn;
                    if (victim->hn != NULL)
                        victim->hn->hp = victim->hp;
                }
                /* ========================================================== */
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
