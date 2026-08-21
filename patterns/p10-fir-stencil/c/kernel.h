#ifndef P10_KERNEL_H
#define P10_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p10: a weighted FIR / sliding-window stencil. One window holds a declared
 * sample count, a declared radius, `2r+1` coefficients and the samples; the
 * kernel emits one dot product per valid window position. See ../README.md,
 * ../spec.md and ../NOTES.md 0.
 *
 *   window     = buf[off .. off+len)
 *   n          = u32 LE at window byte 0    DECLARED sample count. ATTACKER DATA.
 *   r          = u32 LE at window byte 4    DECLARED radius.       ATTACKER DATA.
 *   data_start = 8
 *   taps       = 2*r + 1                    64-bit in every rung
 *   coeffs     = buf[off+8 .. off+8+taps)                          ATTACKER DATA
 *   samples    = buf[off+8+taps .. off+8+taps+n)                   ATTACKER DATA
 *
 *   if (len < 8)      return 0;
 *   if (n < taps)     return 0;          <<< present in EVERY rung
 *   last = 8 + taps + n - 1;             <<< the offset of the LAST sample byte
 *   if (last >= len)  return 0;          <<< THE SAFETY LINE. R1 writes `>`.
 *   nout = n - 2*r;
 *   acc = 0;
 *   for i in 0..nout:
 *       s = 0;                                                  (uint32_t)
 *       for j in 0..taps:
 *           s += (uint32_t)samples[i+j] * (uint32_t)coeffs[j];
 *       acc = acc*31 + s;
 *   return acc*31 + nout;
 *
 * **THE BUG IS ONE CHARACTER, IN A COMPARISON BOTH C RUNGS ALREADY PERFORM.**
 * `last` is an INDEX -- the window offset of the last sample byte the kernel
 * will read -- so the test that keeps it inside the window is `last >= len`.
 * c/kernel.c writes `last > len`, which admits `last == len`: exactly one byte
 * past the window and not a byte more. Every other line of the two cells is
 * character for character identical.
 *
 * That is a different shape from every earlier pattern in this project. p02's,
 * p07's, p16's, p17's and p18's R1 OMITS A LINE, so hardening ADDS instructions
 * (+5 gcc / +12 clang on p02, +2.00 per executed pop on p03, once per input
 * byte on p18). p10's R1 already executes the comparison and merely relates its
 * two operands wrongly, so R1h is expected to be the same instruction stream
 * with one opcode byte changed (`ja` -> `jae`) and the hardening cost is
 * expected to be ZERO. ../NOTES.md 4 measures it rather than assuming it.
 *
 * **THE BUG IS CONDITIONAL, AND THE GATE FORCES THAT.** harness/check.py stage
 * 2 requires every cell INCLUDING R1 to print model.py's checksum on every
 * non-adversarial input, so a bug that fired on a well-formed window could not
 * be shipped. inputs/gen.py packs every benign window exactly full
 * (`stride == 8 + taps + n`, so `last == len - 1`) and the two rungs are then
 * behaviourally identical on every benign input -- which is also what makes the
 * R1-vs-R1h COST comparison legal here where `.memory/02-bench-rules.md`'s
 * first rule forbids it on p12 and p13.
 *
 * **WHAT THIS RUNG KEEPS is as important as what it gets wrong.** The window
 * guard `n < taps` is present in both C rungs, so `nout = n - 2*r` cannot
 * underflow and p10 has NO wild index to model on any input; `taps` is computed
 * at 64 bits, so a declared radius near 2^32 cannot wrap it into a small one.
 * The whole of the bug is the relation in one comparison.
 *
 * **THE ALGORITHM IS A WEIGHTED FIR AND NOT A BOX FILTER**, deliberately: a box
 * filter has an O(n) running-accumulator form and an O(n*r) tap-loop form, and
 * a ladder in which any rung reached for the first would be comparing two
 * different algorithms. A per-tap coefficient makes the incremental form
 * impossible in every language at once. ../NOTES.md 0.
 *
 * **THERE IS NO DIVISION ON THE OUTPUT PATH.** A FIR is normally normalised by
 * the coefficient sum; callgrind prices a hardware `div` at ONE `Ir`
 * (`.memory/03-measurement.md`), so a per-output division would be nearly free
 * in the column this project publishes and expensive in the one it cannot
 * measure well, and it would sit inside every per-tap law p10 fits.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- `last > len`. THE BUG.
 *   c/kernel_hardened.c  R1h -- `last >= len`, and that one character is the
 *                               whole difference.
 *
 * Both take `buf_len`, and both ignore it: p10's bound is the WINDOW's extent,
 * `len`, which is already an argument. p06's, p12's, p14's and p18's shape.
 *
 * **The kernel does not mutate `buf`, writes nothing anywhere, and holds no
 * state between calls.** There is no destination buffer, no scratch and no
 * table -- `s`, `acc`, `i` and `j` are scalars -- so the driver's repeat
 * protocol has nothing to corrupt (../NOTES.md 0c measures that rather than
 * asserting it).
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `s += a*w`,
 * `acc*31 + s` and the return expression are the wrapping operations ../spec.md
 * asks for with no special spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `n`, `r` and every byte of the window are attacker data
 * and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P10_KERNEL_H */
