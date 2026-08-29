#ifndef P29_KERNEL_H
#define P29_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p29: a binary search tree of individually allocated records, driven by an op
 * stream from the file, with **a pointer to one record cached across
 * operations**. The SECOND temporal row in this project, and it is `p27`'s row
 * with one term added to the safety line -- see ../spec.md.
 *
 *   window = buf[off .. off+len)
 *   nops        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   op          = 2 bytes: c = opcode byte, a = operand byte   ALL ATTACKER DATA
 *   TABCAP = 32    the slot table's extent       a compile-time constant
 *   RECSZ  = 4     one record, one allocation    a compile-time constant
 *   NIL    = 255   the null link                 a compile-time constant
 *   SENT   = 251   what a rejected op folds      a compile-time constant
 *
 * A RECORD is four bytes and one `malloc`:
 *
 *   tab[i][0]  key      tab[i][1]  val      tab[i][2]  left     tab[i][3]  right
 *
 * so the tree's LINKS live inside the record, which is what a textbook BST node
 * is and what makes delete-by-substitution the algorithm it is. `tab[i]` is the
 * address of slot i's record and `live[i]` says whether that record is still
 * allocated. **Slots are never recycled** (`ntab` only grows), exactly as in
 * `p27`, so `live[]` is a generation counter degenerated to one bit.
 *
 *   uint8_t *tab[TABCAP] = {0} ; uint8_t live[TABCAP] = {0}
 *   ntab = 0 ; root = NIL ; acc = 0 ; p = 4
 *   g_saved = NULL ; g_slot = 0 ; g_key = 0        THE CACHED LOOKUP RESULT
 *   for o in 0 .. nops:
 *       if len - p < 2: break
 *       c = buf[off+p] ; a = buf[off+p+1] ; p += 2
 *       switch c % 4:
 *         0 INSERT: walk from root by key; a duplicate updates val in place;
 *                   otherwise, if ntab < TABCAP, malloc a record and link it
 *                   acc = acc*31 + a          (acc*31 + SENT if the table is full)
 *         1 FIND  : walk from root by key
 *                   if found: g_saved = tab[cur] ; g_slot = cur ; g_key = a
 *                             acc = acc*31 + 1
 *                   else:     acc = acc*31 + SENT
 *         2 REMOVE: walk from root by key; if found, delete by substitution
 *                   acc = acc*31 + 2          (acc*31 + SENT if not found)
 *         3 USE   : if g_saved != NULL                <<< THE SAFETY LINE. R1
 *                   && live[g_slot] == 1                  omits the second and
 *                   && tab[g_slot][0] == g_key:           third conjuncts.
 *                             acc = acc*31 + g_saved[1]
 *                   else:     acc = acc*31 + SENT
 *   for j in 0 .. TABCAP: if live[j]: free(tab[j]) ; live[j] = 0
 *   return acc*31 + ntab
 *
 * **ONE OMITTED SOURCE LINE CARRIES TWO BUG CLASSES, SELECTED BY THE INPUT.
 * THAT IS THE ROW.**
 *
 *   victim with 0 or 1 child   unlinked and FREED         use-after-FREE
 *   victim with 2 children     successor's key/val copied  in-bounds
 *                              INTO it, the SUCCESSOR      use-after-RECYCLE
 *                              freed
 *
 * The recycle half never touches the allocation: the victim's record stays
 * live, at the same address, holding somebody else's data. A liveness bit
 * cannot see that, and neither can ASan, neither can Miri, neither can safe
 * Rust's `Option` discriminant, and neither can a linear `PointsTo`.
 * ../NOTES.md 2 measures all of them.
 *
 * ⚠⚠ **AND THE HALF EVERY DETECTOR SEES IS THE HALF THAT CANNOT BE GATED.**
 * R1's checksum is NOT reproducible on the use-after-free windows and IS
 * reproducible on the recycle one (../controls/repro.json, which publishes the
 * invariant and no pinned count). So the class the instruments catch is the
 * class a gate cannot pin, and the class the gate pins is the class no
 * instrument sees.
 *
 * ⚠⚠⚠ **WHAT THIS FILE SAID HERE AND IT WAS FALSE -- MEASURED AND RETRACTED
 * AT TASK_140:** ~~*"the safety line has TWO conjuncts and `p27`'s has ONE,
 * and that is the row"*~~. **ONE CONJUNCT IS ENOUGH.** Two single-conjunct
 * spellings built from c/kernel.c by substitution score `0 wrong / 0 ASan
 * lines` with the ASan positive control firing, and one of them adds **no
 * state**: it widens `live[]` from a bit to the occupant tag, which `p27`'s
 * own kernel calls a generation counter with slot reuse removed. The
 * two-conjunct line below is a CHOICE -- it buys a free `wf` at R5
 * (../NOTES.md 6c) -- and the row stands on the two bug classes above, which
 * the conjunct count was never evidence for.
 *
 * **GIVEN THIS SPELLING THE ORDER IS LOAD-BEARING, WHICH IS WHY THESE TWO
 * CONJUNCTS ARE NOT INTERCHANGEABLE.** `tab[g_slot]` is never reset (see below), so
 * `tab[g_slot][0]` and `g_saved[0]` are *the same load from the same address*.
 * With the liveness conjunct in front of it, that load is short-circuited away
 * on exactly the inputs where the record has been freed; without it, the
 * identity test is itself a `heap-use-after-free`. Measured, on one corpus: the
 * line as written fires ASan **zero** times and the same line with the liveness
 * conjunct deleted fires it on **every use-after-free window**. ⚠ The counts
 * live in ../NOTES.md 2b and ../controls/arms.json and are deliberately NOT
 * transcribed here -- a number a rebuild produces must not sit in a file the
 * rebuild re-hashes (`.memory/02-bench-rules.md`).
 *
 * **Why `tab[h]` is NOT set to NULL on free, and it is `p27`'s reason.**
 * `p27`'s `c/kernel.c` argues it at length: nulling the table slot would turn a
 * stale read into a NULL dereference, *a crash, not a use-after-free, and a
 * different bug class*. p29 keeps the convention and now has a measurement for
 * it -- with `tab[cur] = NULL` added on the free, the one-conjunct control above
 * stops reporting `heap-use-after-free` and starts reporting `SEGV`
 * (../NOTES.md 2c). It also keeps `tab[]` WRITE-ONCE PER SLOT, which is what
 * lets rung 5 know that `g_saved` is slot `g_slot`'s record without any
 * invariant that a mutation has to re-establish.
 *
 * **THE WALKS TEST `live[cur] == 1`, IN EVERY RUNG INCLUDING R1.** A correct
 * tree never links to a retired slot, so the conjunct never fires; it is there
 * because rung 5 must license the read of `tab[cur]` and `live[i] == 1 <=>
 * perms.dom().contains(i)` is a per-slot fact, while *"every link points at a
 * live slot"* is the whole tree invariant (unique parents, acyclic) and is not.
 * ../spec.md pins it in every rung and ../NOTES.md 4 counts every such term.
 * **Note what it means for R1: this kernel
 * consults `live[]` at every step of every walk and does not consult it on the
 * one path that holds a raw pointer.** That is the bug stated exactly.
 *
 * **THE WALKS ALSO CARRY AN EXPLICIT STEP BOUND**, `steps < TABCAP`, in every
 * rung. At most TABCAP records exist, so no path is longer than TABCAP and the
 * bound never fires; it is what gives rung 5 a `decreases` measure without the
 * tree invariant. Same reason, same cost.
 *
 * **THE FREE IS A REAL `free`.** Not a freelist push into a slab: after a
 * 0-or-1-child splice `g_saved` points into no live allocation at all, so R1's
 * stale read is a genuine use-after-free -- ASan aborts, Miri reports UB
 * (../NOTES.md 2a) and `PointsTo` cannot license it. A slab-and-freelist
 * spelling would put that read inside a live allocation, which is p17's LOGICAL
 * class and not this one; `p27`'s `spec.md` pins the same thing for the same
 * reason. ⚠⚠ **After a TWO-CHILD splice it points into a live allocation
 * ANYWAY** -- nothing was freed -- **and that is the other half of this row,
 * and the reason the safety line has to notice something the ALLOCATOR does
 * not know.** ⚠ It is not a reason the line needs a SECOND conjunct: one
 * conjunct over a wider `live[]` notices it too (TASK_140, measured).
 *
 * **THE HANDLE THE FILE NAMES IS A KEY, AND THE POINTER IS THE KERNEL'S OWN.**
 * A file cannot name a pointer -- but it can name an operation that saves one,
 * and FIND is that operation. This is the corrected form of the sentence that
 * stood under three refusals (RECAP finding 49).
 *
 * The guard is written subtraction-first (`len - p < 2`) rather than additively
 * (`p + 2 > len`) in all seven rungs, for p07's, p14's, p13's and p27's reason:
 * `p <= len` is maintained by the guard itself so the subtraction cannot wrap,
 * while the additive form can overflow and Verus rejects it.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- `if (g_saved != NULL)` on the USE path. THE BUG.
 *   c/kernel_hardened.c  R1h -- the same test plus the two conjuncts above, and
 *                               that one line is the whole difference.
 *
 * Both take `buf_len` and both ignore it: p29's bound is not the source
 * buffer's length. p12's, p06's, p14's and p27's shape.
 *
 * **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
 * every call must return the same value; every allocation this kernel makes is
 * also freed by it before it returns, so call *i+1* starts from the same
 * allocator state call *i* did.
 *
 * `malloc` failure aborts -- what Rust's global allocator does on OOM and what
 * `vstd::raw_ptr::allocate` does, so all seven rungs agree.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + x` is the
 * wrapping operation ../spec.md asks for with no special spelling. The only
 * undefined behaviour R1 can execute is the LOAD through a dangling `g_saved`.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nops`, every opcode byte and every operand byte are
 * attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P29_KERNEL_H */
