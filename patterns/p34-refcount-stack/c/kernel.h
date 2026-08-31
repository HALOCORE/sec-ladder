#ifndef P34_KERNEL_H
#define P34_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p34: MANUAL REFERENCE COUNTING over a stack of heap objects, driven by an op
 * stream from the file. ../spec.md and ../README.md say the same thing for a
 * reader who has not read this one.
 *
 *   window = buf[off .. off+len)
 *   nops        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   op          = 2 bytes: c = opcode byte, a = operand byte   ALL ATTACKER DATA
 *   CAP    = 16    stack entries                a compile-time constant
 *   DLEN   = 8     payload bytes per object     a compile-time constant
 *   SENT   = 251   what a rejected op folds     a compile-time constant
 *
 * THE C MECHANISM, AND WHY IT IS NOT `p27`, `p29` OR `p32`
 * -------------------------------------------------------
 * Every object carries its OWN reference count in its own first word:
 *
 *   struct p34_obj { size_t rc; size_t len; uint8_t data[DLEN]; };
 *
 * `NEW` allocates one with `rc = 1` and pushes it. `DUP` publishes a SECOND
 * reference to the object on the top of the stack. `POP` releases one reference
 * and frees the object when the count reaches zero. `READ` folds a byte through
 * the `a`-th reference on the stack. The epilogue releases every reference the
 * window left behind.
 *
 *   c/kernel_hardened.c  R1h -- `DUP` retains: `t->rc = t->rc + 1;`
 *   c/kernel.c           R1  -- the same file with that ONE LINE ABSENT.
 *                               THE BUG.  ../controls/safety_line.py
 *                               preprocesses both and diffs them, so the claim
 *                               is measured on the shipped files rather than
 *                               asserted: `+1 / -0` preprocessed lines, the
 *                               smallest safety line in this tree.
 *
 * **THE READ IS CORRECT AND ASKS NOTHING WRONG, AND THAT IS THE DISTINCTION.**
 *
 *   p27  the free discipline is correct; the READ does not ask.        Fix the READ.
 *   p29  the free discipline is correct; the READ does not revalidate.  Fix the READ.
 *   p32  the free discipline is correct; the handle is not revalidated. Fix the READ.
 *   p34  A REFCOUNTED POINTER IS VALID BY CONSTRUCTION.  It is the ACQUIRE that
 *        broke the invariant, and the harm lands an unbounded distance away.
 *
 * No check on the read path could repair `p34` without becoming a liveness
 * table, because there is nothing on the read path that is wrong. **The free
 * happens EARLY rather than the read happening LATE** -- a different C program
 * with a different repair site. Nothing in `p27`, `p29` or `p32` computes
 * whether to free from a counter; `p32` allocates nothing at all.
 *
 * ⚠⚠ **THE ACQUIRE IS THE ONLY ZERO-COST REPAIR SITE, NOT THE ONLY REPAIR
 * SITE -- MEASURED, AND THE STRONGER CLAIM IS WITHDRAWN.** `TASK_155` built the
 * counterexample and `TASK_156` re-derived it
 * (`.temp/t156/csite/{make_destroyfix.py,destroy_cost.py}`): leave `DUP`
 * untouched, and decide the free on the RELEASE path by scanning
 * `stk[0..ntop)` for the object instead of trusting `rc`. That is `p28`'s
 * repair site, an ownership test at the free, and it WORKS -- checksum-equal to
 * R1h on 8/8 inputs and ASan-clean where R1 fires. **What it is not is free:**
 *
 *     marginal Ir/call, gcc, isolated, (Ir@200 - Ir@100)/100
 *       small.bin  -O0   R1/R1h 3144.48    destroy-side 3309.18   +164.70  (+5.24 %)
 *       small.bin  -O3   R1/R1h 2207.59    destroy-side 2368.23   +160.64  (+7.28 %)
 *       large.bin  -O0   R1/R1h 15579.69   destroy-side 18532.96  +2953.27 (+18.96 %)
 *       large.bin  -O3   R1/R1h 11106.93   destroy-side 13510.76  +2403.83 (+21.64 %)
 *
 * ⚠ **The cost grows with the INPUT, not with the optimisation level**, because
 * the scan is `O(ntop)` on EVERY release while the retain runs only on a `DUP`
 * -- which no benign input contains. That is *why* the acquire is the idiomatic
 * site, and pricing two repair sites is a better result than asserting one.
 *
 * ⚠⚠ **THERE IS NO BENIGN INPUT THAT EXECUTES THE SAFETY LINE, AND THAT IS
 * PROVED RATHER THAN SEARCHED.** `t->rc = t->rc + 1` is the ONLY increment in
 * the kernel, so in R1 every object's `rc` is permanently 1. Any executed `DUP`
 * therefore leaves TWO stack entries naming a ONE-reference object, and the two
 * releases that must follow -- each entry is released exactly once, by `POP` or
 * by the epilogue -- go `1 -> 0` (*free*) and then `0 -> underflow`, reading
 * `o->rc` out of a freed block. **So `p34`'s benign cost gradient across the
 * safety line is `0.00` BY CONSTRUCTION**, and `inputs/gen.py` enforces the
 * corollary mechanically: NO MATRIX INPUT MAY CONTAIN A `DUP` OP.
 *
 * ⚠ **"BY CONSTRUCTION" IS ABOUT THE STATEMENT, NEVER ABOUT THE NUMBER, AND
 * THAT DISTINCTION IS MEASURED.** The construction proves the safety line is
 * not EXECUTED; the marginal `Ir` is a codegen outcome and R1h is a different
 * compiled function. `TASK_155` planted a *different* never-executed statement
 * on the same dead `DUP` path and moved the `-O3` cell by **-14.22** Ir/call
 * through layout alone. `0.00` is what was MEASURED (../NOTES.md 4b), not what
 * was assumed, and *"`0.00` by construction, NOT by measurement"* is withdrawn.
 *
 * TWO BUG CLASSES, SEPARATED BY WHICH INSTRUMENT SEES THEM
 * -------------------------------------------------------
 *   DUP POP POP        the second release reads `o->rc` out of the freed block.
 *   DUP POP READ       the stale entry reads `o->data[0]` out of the freed block.
 *                      **In BOTH, the checksum is BIT-IDENTICAL between the two
 *                      rungs and ASan is the only discriminator.** The refcount
 *                      header comes first and `data` starts at offset 16, clear
 *                      of glibc's tcache `next`/`key` words at user offsets 0
 *                      and 8, so the stale read returns the RIGHT value -- and
 *                      the release path folds a constant that does not depend on
 *                      `rc` or on whether `free` ran. **Layout disclosed, as
 *                      `p28` discloses its own.**
 *   DUP POP NEW READ   the next `NEW` RECYCLES the freed block, so the stale
 *                      entry reads the NEW OCCUPANT's payload and **the checksum
 *                      DIVERGES**.
 *
 * ⚠ Both classes are reproducible: `n = 1` in 20 runs at every iteration count
 * this pattern ships, on gcc and clang at `-O0`, `-O1` and `-O3`
 * (../NOTES.md 2). p27's `adversarial-noreuse` hazard -- a stale read whose
 * value is ASLR-dependent -- does not reach p34's shipped inputs, because
 * `data` is clear of the tcache words that ASLR moves.
 *
 * WHY R1h IS CORRECT
 * ------------------
 * Admission question 1 asks the C kernel to be correct on benign inputs, so R1h
 * has to be genuinely correct and not merely better. The invariant is
 *
 *   for every live object o, `o->rc` == the number of stack entries naming o
 *
 * preserved because NEW pushes one entry and sets `rc = 1`; DUP pushes one entry
 * and increments; POP and the epilogue each remove one entry and decrement, and
 * free exactly when the count reaches 0. **So R1h never frees an object that is
 * still on the stack, never frees one twice, and leaves none allocated: the
 * epilogue drives every count to zero.**
 *
 * `stk[ntop-1]` on DUP and `stk[a % CAP-bounded]` on READ are always in range:
 * DUP runs only under `ntop > 0 && ntop < CAP`, READ only under `ntop > 0` and
 * its index is `a % ntop`. **R1's undefined behaviour is TEMPORAL and never
 * spatial** -- every index the kernel forms is inside the stack array in both
 * rungs, which is why UBSan says nothing at all (../NOTES.md 2).
 *
 * WHY THE OBJECT IS `malloc`ed AND NOT AN ARENA SLOT
 * --------------------------------------------------
 * The allocation is the pattern: a refcount exists to decide WHEN TO FREE, and a
 * slot that is never freed has nothing to decide. `.memory/01-ladder.md`'s law
 * -- *safe Rust's temporal guarantee is a guarantee about the ALLOCATOR* -- is
 * what makes the storage choice load-bearing rather than incidental, and
 * ../controls/safe_arms.py measures both sides of it: branch A is the `Rc`
 * port, whose two must-fail arms do not compile, and branch B is a safe
 * INDEX-ARENA port that reproduces this file's checksum on 8/8 inputs.
 * ⚠ **This line cited `../controls/storage_arms.py` until `TASK_156`, AND THAT
 * FILE HAS NEVER EXISTED** (`TASK_155_REPORT` M4) -- a citation is what a
 * reader trusts INSTEAD of re-checking, so a dangling one removes the check it
 * was meant to enable.
 *
 * Two C rungs share this declaration, and both take `buf_len` and ignore it:
 * p34's bound is not the source buffer's length. p12's, p06's, p14's, p27's,
 * p29's and p32's shape.
 *
 * **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
 * every call must return the same value; the stack is a local and every object
 * the window allocates is released before the call returns, so call *i+1* starts
 * from the same state call *i* did.
 *
 * The cursor guard is written subtraction-first (`len - p < 2`) rather than
 * additively (`p + 2 > len`) in all seven rungs, for p07's, p14's, p13's, p27's,
 * p29's and p32's reason: `p <= len` is maintained by the guard itself so the
 * subtraction cannot wrap, while the additive form can overflow and Verus
 * rejects it.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + v` and
 * `o->rc - 1` are the wrapping operations ../spec.md asks for with no special
 * spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nops`, every opcode byte and every operand byte are
 * attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P34_KERNEL_H */
