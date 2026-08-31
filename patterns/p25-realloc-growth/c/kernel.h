#ifndef P25_KERNEL_H
#define P25_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p25: A DYNAMIC ARRAY GROWN WITH `realloc`, AND AN INTERIOR POINTER HELD
 * ACROSS THE GROWTH. ../spec.md and ../README.md say the same thing for a
 * reader who has not read this one.
 *
 *   window = buf[off .. off+len)
 *   nops        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   op          = 2 bytes: c = opcode byte, a = operand byte   ALL ATTACKER DATA
 *   SEED   = 4     first capacity of either vector    a compile-time constant
 *   MAXCAP = 64    largest capacity of either vector  a compile-time constant
 *   SENT   = 251   what a rejected op folds           a compile-time constant
 *
 * Four operations, `c % 4`:
 *
 *   0 PUSHT  append the operand byte to the TOKEN vector, growing by doubling
 *   1 PUSHS  append the operand byte to the STRING vector, the same way
 *   2 SAVE   remember an INTERIOR POINTER into the token vector, `&toks[a%ntok]`
 *   3 READ   fold the byte that pointer names
 *
 * THE C MECHANISM, AND WHY IT IS NOT `p27`, `p29`, `p32` OR `p34`
 * ---------------------------------------------------------------
 * **THIS PROGRAM NEVER CALLS `free` ON THE OBJECT IT LATER READS.** `realloc`
 * RELOCATES the token vector and retires the old block as a side effect of
 * GROWTH, and the stale reference is an INTERIOR POINTER into the middle of a
 * container rather than a pointer to a whole object.
 *
 *   p27  individually malloc'd records; an explicit `free`; the READ does not
 *        ask whether the record is still live.                  Fix the READ.
 *   p29  an explicit `free` of a whole record and a stale ADDRESS held across
 *        it; the READ does not revalidate the occupant.          Fix the READ.
 *   p32  nothing is allocated at all; a handle is not revalidated against the
 *        block's incarnation.                                    Fix the READ.
 *   p34  an explicit `free` driven by a reference count that the ACQUIRE failed
 *        to raise; the read path is correct.                     Fix the ACQUIRE.
 *   p25  NO `free` ANYWHERE IN THE KERNEL EXCEPT THE EPILOGUE. The block is
 *        retired by `realloc` as a SIDE EFFECT OF GROWTH, and what is stale is
 *        an INTERIOR pointer, `toks + curi`.                     Fix the READ.
 *
 * ⚠ **`p34` is the sharpest attack on that distinction and it is worth stating
 * where it lands.** Both rows read a retired block. `p34`'s block is retired by
 * an explicit `free(o)` that a refcount reaching zero selected, and its repair
 * site is the ACQUIRE; `p25` calls `free` on nothing but the two vectors at the
 * end, the retirement is `realloc`'s and is not a decision the program makes at
 * all, and its repair site is the READ. ✅ Measured, not asserted:
 * over every pattern's `c/` directory, with comments and string literals blanked
 * first, `realloc` is called by EXACTLY ONE pattern and it is this one (1 of 32),
 * and only 5 of the 32 call `malloc` at all (p27, p28, p29, p34, p42).
 * ⚠ `.temp/mgr155/NOTES.md` §6 published *"p10 p27 p28 p29 p32 p42, 6 of 30"*
 * from a raw grep; p10's and p32's hits are PROSE -- `p32/c/kernel.h` says
 * *"neither `malloc`'d nor `free`d per use"* -- and p34, which really does
 * allocate, is missing from it. The load-bearing half is unaffected.
 * **So no built row has an allocation that MOVES while logically live, and none
 * has a stale INTERIOR pointer.** ../controls/no_reloc.py re-derives the whole
 * census every run, and it also prints the `free` column, which is 32 of 32 --
 * every `c/main.c` frees the driver payload -- so "calls `free`" is NOT a
 * distinguishing token and this row's distinction is stated about the KERNEL.
 *
 *   c/kernel.c           R1  -- reads `*cur` unconditionally.  THE BUG.
 *   c/kernel_hardened.c  R1h -- the same file plus the conjunct `curbase == toks`
 *                               and a RE-DERIVE when it is false.
 *
 * THE SAFETY LINE, AND WHY ITS `else` BRANCH RE-DERIVES RATHER THAN FOLDING
 * A SENTINEL
 * -------------------------------------------------------------------------
 * ⚠⚠ **THE `else` BRANCH IS NOT A FREE CHOICE AND THE OBVIOUS SPELLING DOES NOT
 * WORK.** A hardened rung that folded `SENT` when the container had moved would
 * make the kernel's ANSWER a function of the ALLOCATOR: whether `realloc`
 * relocates is a heap-topology fact, so `model.py` could not derive the
 * checksum without simulating glibc, and the four Rust rungs -- whose `Vec`
 * grows on a different schedule -- would disagree with the C ones. Re-deriving
 * `toks[curi]` makes the answer ALLOCATOR-INDEPENDENT, because `realloc`
 * COPIES: `toks[curi]` after the move is the byte `*cur` named before it.
 * ../NOTES.md 3 has the measurement.
 *
 * ⚠ **So the conjunct buys MEMORY SAFETY and buys NOTHING ELSE.** Both branches
 * of the hardened READ compute the same value in every terminating execution.
 * That is the row's thesis, and it is why the cost of the safety line is a
 * clean read of the price of memory safety alone.
 *
 * ⚠⚠ **AND THE CONJUNCT IS NOT SUFFICIENT UNDER THE C STANDARD, WHICH IS THIS
 * ROW'S SHARPEST C-SIDE FINDING.** C99 7.20.3.4p4 / C11 7.22.3.5p4 and DR 400
 * make the OLD pointer value indeterminate after `realloc` returns, **whether or
 * not the block moved** -- so `curbase == toks` being true does not restore
 * `cur`. The idiomatic guard that every C programmer writes is a REAL check (it
 * is what makes ASan and every relocating allocator safe) and it is still not
 * the standard-clean repair; only re-deriving is. ../controls/rederive.py prices
 * the unconditional re-derive, which is the standard-clean rung, and ../NOTES.md
 * 3c reports both.
 *
 * ⚠⚠ **THE HARM WINDOW IS ONE GROWTH WIDE, AND SAYING OTHERWISE MISLEADS.**
 * glibc extends a small block IN PLACE until it runs out of the chunk it already
 * has: measured on this box, `4 -> 8` and `8 -> 16` do not move, `16 -> 32`
 * MOVES when a second live allocation sits behind the token vector, and
 * `32 -> 64` does not. So the adversarial input is TUNED to the `16 -> 32`
 * growth; *"`realloc` moves"* is NOT a general property of this kernel.
 * ../controls/reloc_probe.py measures it on the shipped kernel.
 *
 * ⚠ **ASan IS A BIASED INSTRUMENT HERE AND THE ROW DOES NOT REST ON IT.**
 * ASan's allocator moves on EVERY `realloc`, so the ASan column would fire even
 * under a topology in which glibc never relocated. The unbiased evidence is the
 * PLAIN-build divergence between R1 and R1h, and ../NOTES.md 2 reports both
 * separately. ⚠ It also means the gate's `sanitizer_expect` column is ASan's
 * semantics, not glibc's: `model.py` derives `fires` from *the token vector was
 * REALLOCATED while a saved pointer was live*, which is exactly when ASan's
 * pointer is dead and is a conservative over-approximation of when glibc's is.
 *
 * WHY THERE ARE TWO VECTORS
 * -------------------------
 * `TASK_134` refused this row on `moved = 0/12`. With ONE growable vector and a
 * driver that allocates the blob first, the vector is the newest allocation,
 * glibc extends it in place and the undefined behaviour is unobservable. **That
 * is a heap-topology fact about that driver, not a fact about C.** A parser that
 * accumulates a token list AND a string table in the same pass -- which is what
 * parsers do -- puts a second live allocation behind the first, and then the
 * first cannot extend.
 *
 * WHY R1h IS CORRECT
 * ------------------
 * Admission question 1 asks the C kernel to be correct on benign inputs. R1h
 * reads the element the saved index names, through the current base whenever the
 * base has changed, so its answer is the one `model.py` computes on EVERY input;
 * and it dereferences `cur` only when the container has not moved. **No matrix
 * input's benign windows grow the token vector while a saved pointer is live**
 * -- `inputs/gen.py` refuses to write one, `model.py::stale_free_problems`
 * re-derives it from the shipped blob every gate run, and
 * ../controls/no_stale.py censuses the directory -- so on every benign input the
 * two rungs execute the same reads and agree bit for bit.
 *
 * WHY R1 IS SPATIALLY CLEAN
 * -------------------------
 * `toks[ntok]` is written only under `ntok < MAXCAP` with `ntok == tcap`
 * having just grown the block, `&toks[a % ntok]` is formed only under
 * `ntok > 0`, and the cursor guard is subtraction-first. **Every index either
 * rung forms is inside the block it names at the moment it is formed**, so R1's
 * undefined behaviour is entirely TEMPORAL and UBSan says nothing at all --
 * which is why ../controls/detectors.py ships a UBSan-specific positive control
 * rather than reusing the ASan one (a positive control licenses only the
 * detector it fires in).
 *
 * Two C rungs share this declaration, and both take `buf_len` and ignore it:
 * p25's bound is not the source buffer's length, it is the token vector's
 * lifetime. p12's, p06's, p14's, p27's, p29's, p32's and p34's shape.
 *
 * **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
 * every call must return the same value; both vectors are locals and both are
 * freed before the call returns, so call *i+1* starts from the same state call
 * *i* did.
 *
 * The cursor guard is written subtraction-first (`len - p < 2`) rather than
 * additively (`p + 2 > len`) in all seven rungs, for p07's, p14's, p13's, p27's,
 * p29's, p32's and p34's reason: `p <= len` is maintained by the guard itself so
 * the subtraction cannot wrap, while the additive form can overflow and Verus
 * rejects it.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + v` is the
 * wrapping operation ../spec.md asks for with no special spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nops`, every opcode byte and every operand byte are
 * attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P25_KERNEL_H */
