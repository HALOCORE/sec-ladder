#ifndef P32_KERNEL_H
#define P32_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p32: a FREE-LIST ALLOCATOR / OBJECT POOL WITH RECYCLING, driven by an op
 * stream from the file. **`p32` and `p33` of `.memory/06-catalogue.md` are ONE
 * ROW with TWO ARMS** -- `p32`'s double-free/aliasing arm and `p33`'s
 * use-after-recycle arm -- because they are one C mechanism, one omitted
 * conjunct, and the input selects which harm you get. ../spec.md and
 * ../README.md say so too.
 *
 *   window = buf[off .. off+len)
 *   nops        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   op          = 2 bytes: c = opcode byte, a = operand byte   ALL ATTACKER DATA
 *   SLOTS  = 8     blocks in the pool            a compile-time constant
 *   BLK    = 4     bytes per block               a compile-time constant
 *   NREG   = 8     handle registers              a compile-time constant
 *   NIL    = 255   the free-list terminator      a compile-time constant
 *   SENT   = 251   what a rejected op folds      a compile-time constant
 *
 * THE C MECHANISM, AND WHY IT IS NOT `p27` AND NOT `p29`
 * -----------------------------------------------------
 * A pool of `SLOTS` fixed-size blocks with a **LIFO free list**. A block is
 * neither `malloc`'d nor `free`d per use: it is POPPED and PUSHED, so **the
 * storage belongs to the program from the first instruction to the last**. The
 * free list is INTRUSIVE -- `nx[j]` is slot `j`'s successor while `j` is free --
 * and `freehead` is its head.
 *
 * A HANDLE is a `(slot, generation)` pair. `gen[j]` is slot `j`'s INCARNATION
 * counter and every FREE bumps it, so a handle whose generation no longer
 * matches names a block that has been RECYCLED. The pair is held in two
 * parallel arrays rather than packed, so that no rung needs a shift and no rung
 * needs a bound on `gen` to stay in range:
 *
 *   regs[r]  the SLOT handle register r names, or NIL
 *   regg[r]  the GENERATION that handle was issued with
 *
 * **The file names a REGISTER, never a slot and never a pointer.** `p29`'s
 * corrected sentence, verbatim: *a file cannot name a pointer -- but it CAN
 * name an operation that saves one*, and ALLOC is that operation. This is what
 * makes the generation UNFORGEABLE, and it is not decoration: with a
 * file-supplied handle byte the attacker can always name the CURRENT
 * incarnation of a block that is already on the free list, and the hardened
 * kernel double-frees anyway. ../NOTES.md 1b measures that variant.
 *
 *   uint8_t pool[SLOTS*BLK] ; uint8_t nx[SLOTS] ; uint32_t gen[SLOTS]
 *   uint8_t regs[NREG] = NIL ; uint32_t regg[NREG] = 0
 *   nx[j] = j+1 (NIL at the end) ; freehead = 0 ; nalloc = 0 ; acc = 0 ; p = 4
 *   for o in 0 .. nops:
 *       if len - p < 2: break
 *       c = buf[off+p] ; a = buf[off+p+1] ; p += 2 ; r = a % NREG
 *       switch c % 4:
 *         0 ALLOC: if freehead == NIL: acc = acc*31 + SENT
 *                  else: s = freehead ; freehead = nx[s]
 *                        pool[s*BLK]   = a           the OWNER TAG
 *                        pool[s*BLK+1] = a*7+1       the PAYLOAD
 *                        regs[r] = s ; regg[r] = gen[s] ; nalloc += 1
 *                        acc = acc*31 + s + 8*gen[s]
 *         1 FREE : h = regs[r] ; g = regg[r]
 *                  if h == NIL:      acc = acc*31 + SENT
 *                  elif gen[h] != g: acc = acc*31 + SENT    <<< THE SAFETY LINE
 *                  else: gen[h] += 1 ; nx[h] = freehead ; freehead = h
 *                        acc = acc*31 + 1
 *         2 READ : same guard; acc = acc*31 + pool[h*BLK+1]
 *         3 WRITE: same guard; pool[h*BLK+1] = a*13+3 ; acc = acc*31 + 3
 *   return acc*31 + nalloc
 *
 * **ONE OMITTED CONJUNCT, `gen[h] == g`, AT THREE SITES, AND IT CARRIES TWO BUG
 * CLASSES SELECTED BY THE INPUT.** That is `p29`'s shipped shape on unrelated
 * code:
 *
 *   FREE with a stale handle   the block is pushed onto the free list a SECOND
 *                              time.  `nx[h] = freehead` with `freehead == h`
 *                              makes the list SELF-LOOP, so every later ALLOC
 *                              returns the SAME slot: TWO LIVE HANDLES ALIAS ONE
 *                              BLOCK and the rest of the list is LOST.
 *   READ with a stale handle   the block has been recycled to a different owner,
 *                              so the read returns the NEW OCCUPANT's payload.
 *
 * ⚠⚠ **THE ALIASING HARM HAS NO ANALOGUE IN `p27` OR `p29`, AND THAT IS THE
 * C-MECHANISM DISTINCTION THIS ROW RESTS ON.** `p27` cannot double-free -- it
 * consults `live[h]` on the FREE path -- has no free list, no recycling and no
 * generation, and its records are individually `malloc`'d and individually
 * `free`d, so its stale read dereferences a DANGLING POINTER. `p29` frees a
 * record with `free()` and holds a stale ADDRESS. **Here nothing is dangling:
 * in the shipped storage every address the kernel touches is inside one live
 * object for the whole run, and the harm is that two handles NAME THE SAME
 * BLOCK.** Neither built row can produce that.
 *
 * WHY THE HARDENED RUNG IS CORRECT, AND IT IS AN INVARIANT WORTH NAMING
 * --------------------------------------------------------------------
 * With the conjunct in place the free list is always a SET OF DISTINCT SLOTS
 * and no two registers ever hold valid handles to one slot. The invariant is
 *
 *   for every register r with regs[r] = h != NIL and regg[r] == gen[h],
 *   slot h is NOT on the free list
 *
 * and it is preserved because (a) ALLOC removes `s` from the list before
 * issuing `(s, gen[s])`, and no register could already hold that pair -- `s`
 * was on the list, so by the invariant none did; (b) FREE pushes only a slot
 * the invariant says is off the list, and then bumps `gen[h]` to a value that
 * has never been issued, since generations only increase and are copied into a
 * register only at a POP. **So R1h can neither double-push nor alias.**
 * ⚠ Modulo `gen` wrapping at 2^32, which needs 2^32 FREEs of one slot inside
 * ONE window; a window holds `(len-4)/2` operations. ../spec.md pins it.
 * ⚠⚠ **THE R5 DOES NOT PROVE THIS INVARIANT AND DOES NOT NEED TO** -- ../NOTES.md
 * 6b -- which is one of this row's results.
 *
 * WHY `regs[r]` IS NOT CLEARED ON THE FREE
 * ---------------------------------------
 * `p27`'s argument and `p29`'s, unchanged: clearing the register on the free
 * would turn every stale use into the `h == NIL` case, which folds SENT in
 * BOTH rungs -- a defined operation, not a use-after-recycle, and a different
 * bug class. Splitting the release from the invalidation is what makes
 * forgetting possible at all, and the whole of R1's bug is that the three
 * handle-consuming paths do not ask.
 *
 * WHY THE STORAGE IS A POOL AND NOT `malloc`, AND WHAT THE CONTROL MEASURES
 * ------------------------------------------------------------------------
 * The pool is the point: it is what a free-list allocator IS. The consequence
 * is that **R1 executes no undefined behaviour at all** -- `h = regs[r]` is
 * always NIL or a real slot, `pool[h*BLK+1]` is always in bounds, and
 * `freehead` is always NIL or a real slot -- so ASan, UBSan and Miri are
 * silent on every input including the adversarial ones. ../controls/
 * `storage_arms.py` rebuilds the SAME source with per-block `malloc`/`free`
 * storage and measures what changes: two of the three adversarial harms become
 * `heap-use-after-free` and `attempting double-free`, and the third -- the
 * use-after-RECYCLE -- stays bit-identical and silent in both. **That is a
 * controlled two-cell experiment on DETECTOR COVERAGE with everything else held
 * byte-identical.**
 *
 * `blk[h]` is not nulled in the `malloc` arm either, for the reason above:
 * measured, nulling it turns the stale read into a SIGSEGV and the double free
 * into a no-op `free(NULL)`, and both are different bug classes.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- `if (h == NIL)` alone at all three sites. THE BUG.
 *   c/kernel_hardened.c  R1h -- the same, plus `else if (gen[h] != g)`, and that
 *                               is the whole difference between the two cells.
 *                               ../controls/safety_line.py PREPROCESSES both and
 *                               diffs them, so the claim is measured on the
 *                               shipped files rather than asserted.
 *
 * Both take `buf_len` and both ignore it: p32's bound is not the source
 * buffer's length. p12's, p06's, p14's, p27's and p29's shape.
 *
 * **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
 * every call must return the same value; the pool is a local, so call *i+1*
 * starts from the same state call *i* did. **This kernel makes no allocator
 * call in the shipped storage, so all seven rungs agree trivially about
 * allocator traffic: there is none.**
 *
 * The guard is written subtraction-first (`len - p < 2`) rather than additively
 * (`p + 2 > len`) in all seven rungs, for p07's, p14's, p13's, p27's and p29's
 * reason: `p <= len` is maintained by the guard itself so the subtraction cannot
 * wrap, while the additive form can overflow and Verus rejects it.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + x` and
 * `gen[h] + 1` are the wrapping operations ../spec.md asks for with no special
 * spelling. **R1 executes NO undefined behaviour** -- see above -- which is why
 * this pattern's `sanitizer_expect` is `clean` on every input it ships.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nops`, every opcode byte and every operand byte are
 * attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P32_KERNEL_H */
