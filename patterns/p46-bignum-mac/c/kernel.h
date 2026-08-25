#ifndef P46_KERNEL_H
#define P46_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p46: schoolbook bignum multiply-accumulate into a FIXED-CAPACITY limb
 * scratch. The operand limb counts arrive IN THE INPUT.
 *
 * ⚠ **SAY THE UNFLATTERING THING FIRST: the BUG CLASS is this tree's
 * FOURTEENTH `index >= len`.** p01, p02, p03, p05, p07, p11, p12, p13, p14,
 * p16, p17, p19 and p36 are all *"an index or a length is not checked against
 * a buffer"*, and so is this. p19 shipped the thirteenth and said so; this is
 * the fourteenth and says so. Its nearest sibling is **p05** -- both index a
 * scratch with a two-term expression built from two loop counters -- and the
 * row must say what is NOT p05's:
 *
 *   * **p05's index arithmetic is NONLINEAR (`i*ncol + j`) and its data
 *     arithmetic is trivial. p46 is the MIRROR: the index is `i + j`, purely
 *     LINEAR, and the DATA arithmetic is the nonlinear thing.** The proof
 *     obligation p05 needs `lemma_mul_inequality` for is an ADDRESS; the one
 *     p46 needs `by (nonlinear_arith)` for is a VALUE -- that
 *     `a*b + c + carry <= 2^128 - 1`, exactly, for u64 a, b, c, carry.
 *   * p46's out-of-bounds access is a **WRITE**; p05's is a read.
 *
 * ⚠⚠ **AND THE MEMORY-UNSAFE FRAMING IS CONDITIONAL. THE CONDITION IS NAMED,
 * IT IS PINNED IN ../spec.md's HASHED BLOCK, AND IT WAS SETTLED BY A RUN
 * BEFORE ANY CELL WAS BUILT** (../NOTES.md 0a). The identical miscount written
 * with a CLAMPED index -- `out[(i + j) % SLB_P46_OUTCAP]` -- is a wrong answer
 * with **no memory event at all**: exit 0, ASan and UBSan both silent. That is
 * `p31`'s death, and p46 escapes it only because the index is not clamped. The
 * clamp is a `forbidden` entry for exactly that reason.
 *
 * Window layout (../spec.md):
 *
 *     byte 0        u8   n      a-limb count      ATTACKER DATA
 *     byte 1        u8   m      b-limb count      ATTACKER DATA
 *     byte 2 .. 8        unused (keeps the limbs 8-aligned)
 *     byte 8 ..     u64 LE limbs: a[0..n] then b[0..m]   ATTACKER DATA
 *
 *     OUTCAP = 96    the product scratch capacity, in 64-bit limbs. A
 *                    compile-time constant in every rung: the buffer the
 *                    product has to fit into.
 *     BCAP   = 256   the b-operand scratch. Sized for the DECLARED TYPE's full
 *                    range (`m` is a u8, so `m <= 255`), which is why the
 *                    pre-decode below is NOT the bug. `out` is sized for the
 *                    EXPECTED product, which is why it is.
 *     REJ            what an over-long product folds to.
 *
 *     if len < 8:                              return 0
 *     n = w[0] ; m = w[1]
 *     if n == 0 or m == 0:                     return 0
 *     if 8 + 8*(n + m) > len:                  return 0   <<< the INPUT bound;
 *                                                             every rung has it
 *     >>> THE SAFETY LINE. c/kernel.c omits exactly this. <<<
 *     if n + m > OUTCAP:                       return REJ  <<< the OUTPUT bound
 *
 *     for j in 0..m:  bl[j] = ld64(w + 8 + 8*(n + j))
 *     out[0..OUTCAP] = 0
 *     for i in 0..n:
 *         ai = ld64(w + 8 + 8*i) ; carry = 0
 *         for j in 0..m:
 *             t        = ai*bl[j] + out[i+j] + carry     <<< 128-BIT, exact
 *             out[i+j] = (uint64_t)t
 *             carry    = (uint64_t)(t >> 64)
 *         out[i+m] = carry
 *     acc = 0
 *     for k in 0..n+m:  acc = acc*31 + out[k]
 *     return (acc*31 + n)*31 + m
 *
 * **THE MAC IS ONE 128-BIT WIDENING MULTIPLY-ACCUMULATE, ON PURPOSE.** It is
 * the whole kernel: `mulq` + `add` + `adc` + `add`-to-memory + `adc`, ten
 * instructions per step on this box including the loop. A heavier body would
 * drown the three bounds checks that separate safe Rust from unsafe Rust.
 *
 * **AND THE STEP CANNOT OVERFLOW, WHICH IS A PROOF OBLIGATION WITH NO RUNTIME
 * COUNTERPART.** `(2^64-1)^2 + 2*(2^64-1) == 2^128 - 1` exactly, so `t` is
 * always representable and no rung -- C, Rust or hardened C -- ever checks it.
 * ../verus.rs must still discharge it, and it is the one obligation in this
 * kernel that is nonlinear. See ../NOTES.md 6.
 *
 * `st`-style loop-carried state here is `carry`, and the inner loop is a SERIAL
 * dependency chain through it: iteration j+1's `add` needs iteration j's `adc`.
 * The loop therefore does not vectorise and does not unroll usefully, which is
 * why every instruction the bounds checks add is an issue slot and not a
 * pipeline bubble (../NOTES.md 9).
 *
 * `c/kernel.c` omits the output-side bound entirely: the "the caller sized the
 * buffer" assumption. `c/kernel_hardened.c` is byte-for-byte the same file with
 * that one test restored, and it is the only difference between them.
 *
 * Both C rungs take `(buf, off, len)` and have no blob length to check --
 * p01's asymmetry: the length is the thing C does not have. Do not "fix" it
 * with a dead `buf_len`; that would be Rust-in-C-syntax.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + out[k]` is
 * the wrapping operation ../spec.md asks for with no special spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). Every declared limb count and every limb byte is attacker
 * data and is the kernel's problem. */

/* The product scratch capacity, in 64-bit limbs. A compile-time constant in
 * every rung and in model.py. */
#define SLB_P46_OUTCAP 96

/* The b-operand scratch, in 64-bit limbs. `m` is a u8, so this can never
 * overflow and the pre-decode loop is not part of the bug. */
#define SLB_P46_BCAP 256

/* What an over-long product folds to. A compile-time constant in every rung. */
#define SLB_P46_REJ 0x9E3779B97F4A7C15ULL

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* P46_KERNEL_H */
