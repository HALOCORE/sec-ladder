#ifndef P05_KERNEL_H
#define P05_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p05: fold one window of `buf` as a 2-D matrix whose dimensions the window's
 * own header declares. CWE-129 (improper validation of an array index) turning
 * into CWE-125, with CWE-190 (integer overflow) hiding one width down.
 *
 *   window = buf[off .. off+len)
 *   nrow        = u16 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   ncol        = u16 LE at window byte 2        DECLARED. ATTACKER DATA.
 *   data        = window byte 4 onwards
 *   avail       = len - 4                        what actually ARRIVED
 *
 *   for i in 0 .. nrow:
 *       row = 0                                  u32, wrapping
 *       for j in 0 .. ncol:
 *           row += data[i*ncol + j]              <<< the flattened 2-D index
 *       acc = acc*31 + row                       u64, wrapping
 *   return acc*31 + nrow*ncol
 *
 * The bug is the oldest one in numerical C: the header says the matrix is
 * `nrow x ncol` and the code walks `nrow*ncol` elements without ever asking
 * whether they are there. `a[i*ncols + j]` is what performance-critical C
 * actually looks like, which is why this pattern is in the catalogue.
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no `nrow*ncol > avail`. THE BUG.
 *   c/kernel_hardened.c  R1h -- the same code plus that one line.
 *
 * Both take `buf_len`, and that is the point: this API *has* the size. R1 is
 * not C being unable to check, it is C code that had what it needed and did not
 * look. R1-vs-R1h is therefore what the check costs inside one language, with
 * the calling convention, the argument count and the register allocation all
 * held fixed (`.memory/02-bench-rules.md`, "The precondition must be
 * structural").
 *
 * **The width of the check is half the pattern.** `nrow` and `ncol` are u16, so
 * `nrow*ncol` is at most 65535*65535 = 4 294 836 225. Written in `size_t` (or
 * `uint64_t`) that is exact and the test is sound. Written in `int` it is
 * 2 147 352 577 past `INT_MAX`, so the multiply overflows -- undefined
 * behaviour, in practice wrapping to -131 071 -- and `-131071 > avail` is
 * **false**, so the wrong check waves the whole attack through while looking
 * exactly like the right one. Note the precise boundary, because "int/unsigned"
 * is not the same claim: the product still fits in `uint32_t`
 * (4 294 836 225 < 4 294 967 295), so an *unsigned* 32-bit check is NOT fooled
 * by anything this wire format can express. Only the signed one is.
 * `adversarial-ovf.bin` is that input and NOTES.md 6 builds the wrong-width
 * cell and measures it.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). Both declared dimensions -- all 2^32 pairs of them -- are
 * attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P05_KERNEL_H */
