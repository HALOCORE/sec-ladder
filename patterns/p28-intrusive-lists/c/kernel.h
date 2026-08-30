#ifndef P28_KERNEL_H
#define P28_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p28: a bounded object cache whose objects carry **TWO INTRUSIVE LINK SETS** -- a doubly
 * linked EVICTION list (`lp`/`ln`) and a doubly linked hash chain (`hn`/`hp`) -- and
 * a DESTROY path that leaves only one of them. The FOURTH temporal row in this
 * project, and it is the INVERSION of the other three: `p27`, `p29` and `p32`
 * all keep a correct free discipline and put the missing check on the READ.
 * Here the read path is correct and the DESTROY path is incomplete.
 *
 *   window = buf[off .. off+len)
 *   nops        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   op          = 2 bytes: c = opcode byte, a = operand byte   ALL ATTACKER DATA
 *   P28_NB    = 8    hash buckets                a compile-time constant
 *   P28_SLOTS = 48   objects per window, and      a compile-time constant
 *                    also the chain walk's fuel
 *   NIL       = 255  the null slot link           a compile-time constant
 *   SENT      = 251  what a rejected op folds     a compile-time constant
 *
 * AN OBJECT is one `malloc`, and the LINKS ARE INSIDE IT:
 *
 *   struct p28_obj { p28_obj *lp, *ln, *hn, *hp; uint8_t key, val; };
 *                    \_ evict list _/  \_ chain _/
 *
 * **THE OBJECT IS ALIASED BY TWO LISTS AT ONCE AND MEMBERSHIP IS NOT
 * OWNERSHIP.** That is the whole reason intrusive lists exist -- one allocation,
 * no per-list node, O(1) removal from either list given the object -- and the
 * whole reason they go wrong. `bucket[b]` is the head of chain `b`; `head`/`tail`
 * are the eviction list's ends and the eviction list is the OWNERSHIP list, so the
 * epilogue frees through it.
 *
 *   bucket[0..NB) = NULL ; head = tail = NULL ; nmade = 0 ; acc = 0 ; p = 4
 *   for o in 0 .. nops:
 *       if len - p < 2: break
 *       c = buf[off+p] ; a = buf[off+p+1] ; p += 2 ; b = a % NB
 *       switch c % 4:
 *         0 PUT : walk chain b for key a; a hit updates `val` in place;
 *                 otherwise, if nmade < SLOTS, malloc an object and push it on
 *                 BOTH lists
 *                 acc = acc*31 + a       (acc*31 + SENT if the budget is spent)
 *         1 GET : walk chain b for key a
 *                 if found: acc = acc*31 + n->val   else: acc = acc*31 + SENT
 *         2 DEL : walk chain b for key a; if found, SPLICE out of BOTH lists,
 *                 then free
 *                 acc = acc*31 + 2       (acc*31 + SENT if absent)
 *         3 TRIM: reclaim the OLDEST object -- `tail`
 *                 splice it out of the eviction list
 *                 <<< THE SAFETY LINE: splice it out of the HASH CHAIN too.
 *                     c/kernel.c omits exactly this and nothing else. >>>
 *                 free it
 *                 acc = acc*31 + 3       (acc*31 + SENT if the cache is empty)
 *   n = head ; while n: nx = n->ln ; free(n) ; n = nx      the epilogue
 *   return acc*31 + nmade
 *
 * **WHY TRIM AND NOT DEL IS THE ONE THAT FORGETS, AND IT IS NOT AN ARBITRARY
 * CHOICE.** DEL reaches its victim BY WALKING THE HASH CHAIN, so it is holding a
 * chain cursor when it frees and unlinking is one more line of the code it is
 * already in. TRIM reaches its victim through the EVICTION LIST -- that is what "oldest" means -- so it holds NO chain cursor and has to go and get one.
 * **The one path that arrives from the other list is the one that forgets.** That
 * is the shape of this bug in real code and it is why the row is about two link
 * sets rather than about one list being doubly linked.
 *
 * **THE DANGLING POINTER ENDS UP INSIDE ANOTHER HEAP OBJECT** -- the freed
 * victim's chain predecessor still has `hn == victim` -- **or in `bucket[]`** when
 * the victim was the chain head. It is NOT in a stack table (`p27`'s `tab[]`),
 * NOT in a stack local (`p29`'s `g_saved`) and NOT in a program-owned pool
 * (`p32`, which frees nothing).
 *
 * **AND THERE IS NOTHING THE INPUT CAN INDEX.** The input names an object only by
 * KEY, and the program finds it by walking. `p27`'s `h < ntab && live[h] == 1`
 * has no analogue here BECAUSE THERE IS NO `h`. There is no slot number, no
 * liveness bit and no generation anywhere in either C rung.
 *
 * ONE OMITTED BLOCK, TWO HARM SHAPES, SELECTED BY THE INPUT:
 *
 *   a later GET on the victim's bucket     walks the chain into the freed object
 *                                          and reads `n->key` / `n->val`
 *                                          -> heap-use-after-free READ. ASan
 *                                             reports it; the value is stable
 *                                             (see the layout note below)
 *   a later DEL on the victim's bucket     the same walk, then a SPLICE that
 *                                          WRITES through `n->hp`/`n->hn`/
 *                                          `n->lp`/`n->ln` read out of a freed
 *                                          chunk -- and the write lands on a
 *                                          THIRD object
 *                                          -> heap-use-after-free WRITE. In a
 *                                             plain build it SIGSEGVs.
 *
 * **LAYOUT NOTE, DISCLOSED, because it decides whether the row is reproducible.**
 * The links come FIRST in the struct -- the Linux `list_head`-embedded-first
 * layout. glibc's tcache overwrites user offsets 0 and 8 of a freed chunk with
 * its `next` and `key` words, so with the links first it clobbers `lp` and `ln`
 * and leaves `hn`, `hp`, `key` and `val` intact: **R1's stale READ is
 * reproducible in a plain build, 20 distinct-value runs give 1.** With the
 * payload first it would be ASLR-dependent instead, which is `p27`'s situation
 * and how `p27` ships. ../NOTES.md 2c states what that buys and -- narrower than
 * an earlier claim -- what it does not.
 *
 * **THE ALLOCATION BUDGET `nmade < P28_SLOTS` IS THE CACHE'S ONLY SIZE LIMIT, AND
 * IT IS A BUDGET PER WINDOW RATHER THAN A LIVE CAPACITY.** It is spelled this way
 * because R2-R5 hold their objects in a FIXED-SIZE TABLE with slots never
 * recycled -- safe Rust cannot hold an intrusive pointer list, so every Rust rung
 * indexes a slot table instead -- and all seven rungs must agree on every window.
 * `p29`'s C rungs carry `ntab < TABCAP` for exactly the same reason and say so.
 * ../spec.md pins it in all seven rungs; ../NOTES.md 3 records which shipped
 * inputs make it fire (`degenerate.bin`, on purpose, and no other).
 *
 * **THE WALK'S FUEL IS `P28_SLOTS` TOO, AND IT CANNOT FIRE IN A CORRECT RUNG:**
 * a chain holds only live objects and at most `P28_SLOTS` objects are ever made,
 * so no chain is longer than the fuel. It is here because R5's `decreases`
 * measure needs it. ⚠ **In R1 it CAN fire** -- a chain that has accumulated stale
 * entries can be walked past its live length -- and that is R1's behaviour,
 * recorded and not required.
 *
 * `c/kernel.c`           R1  -- TRIM frees the victim without leaving the hash
 *                               chain. THE BUG.
 * `c/kernel_hardened.c`  R1h -- the same file plus the nine-line splice, and that
 *                               block is the whole difference.
 *                               `controls/safety_line.py` preprocesses both and
 *                               diffs them, so the claim is measured.
 *
 * Both take `buf_len` and both ignore it: p28's bound is not the source buffer's
 * length, it is the object's life. p12's, p06's, p14's, p27's and p29's shape.
 *
 * **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
 * every call must return the same value; every allocation this kernel makes is
 * also freed by it before it returns, so call *i+1* starts from the same
 * allocator state call *i* did. ⚠ **In R1 that is true of the ALLOCATION COUNT
 * but not of the CONTENT of the freed chunks it reads** -- which is why the
 * layout note above is load-bearing rather than decorative.
 *
 * `malloc` failure aborts -- what Rust's global allocator does on OOM and what
 * `vstd::raw_ptr::allocate` does, so all seven rungs agree.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + x` is the
 * wrapping operation ../spec.md asks for with no special spelling. The only
 * undefined behaviour R1 can execute is the load or store through a link left
 * pointing at a freed object.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nops`, every opcode byte and every operand byte are
 * attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P28_KERNEL_H */
