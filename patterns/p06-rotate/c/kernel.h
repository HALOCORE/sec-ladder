#ifndef P06_KERNEL_H
#define P06_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p06: in-place rotate of a fixed scratch buffer. One window holds a declared
 * count of records; each record declares an element count and a ROTATE AMOUNT,
 * and the kernel copies the elements into a fixed-size local `scr[SCR]` and
 * rotates the live prefix left by that amount, spelled as the classic three
 * in-place reverses. See ../README.md and ../NOTES.md 0.
 *
 *   window = buf[off .. off+len)
 *   nrec        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   record      = u32 LE nelem ; u32 LE r ; nelem bytes    ALL ATTACKER DATA
 *   SCR = 64                                     a compile-time constant
 *
 *   scr[SCR] = {0} ; acc = 0 ; p = 4
 *   for rec in 0 .. nrec:
 *       if len - p < 8: break
 *       nelem = u32le(buf[off+p]) ; r = u32le(buf[off+p+4]) ; p += 8
 *       m = min(nelem, SCR)             <<< the CLAMP, present in EVERY rung
 *       if len - p < nelem: break
 *       memcpy(scr, buf + off + p, m)   <<< bulk, in EVERY rung
 *       p += nelem
 *       if (m != 0) r %= m; else r = 0; <<< THE SAFETY LINE. R1 omits THIS.
 *       reverse(scr, 0, r) ; reverse(scr, r, m) ; reverse(scr, 0, m)
 *       for i in 0 .. m: acc = acc*31 + scr[i]     u64, wrapping
 *       acc = acc*31 + m
 *   return acc*31 + nrec
 *
 * **THE SAFETY LINE IS A DIVISION, and that is why this pattern exists.** Every
 * safety line this project has measured so far is a compare-and-branch worth 1
 * or 2 instructions; `r %= m` is a hardware `div` on a runtime divisor, which
 * callgrind prices at exactly **1 Ir** (`.memory/03-measurement.md`) and the
 * hardware at tens of cycles. So p06 is the pattern where the project's primary
 * metric and its clock disagree by construction rather than by accident.
 * ../NOTES.md 0 has the measurement, and its headline is not the one that was
 * predicted: on clang **R1h executes FEWER instructions than R1** (-11.00 per
 * record) while taking MORE time, because narrowing `r` to `[0, m)` also lets
 * LLVM merge the four-byte little-endian decode of `r` into one load.
 *
 * **TWO REGIMES, SEPARATED BY SCR, AND ONLY ONE IS A MEMORY-SAFETY EVENT.**
 * `reverse(scr, 0, r)` swaps `scr[i]` with `scr[r-1-i]`, so its highest index
 * is `r - 1`:
 *
 *   m <= r <= SCR   the unreduced rotate stays INSIDE the array. Wrong answer,
 *                   exit 0, ASan+UBSan clean, and no safe Rust rung panics --
 *                   not even with the reduction deleted. `adversarial-inarray`.
 *   r > SCR         the first reverse leaves the fixed local. Magnitude- and
 *                   compiler-dependent, p12's ladder: `adversarial-past1`,
 *                   `-past48`, `-pastfar`.
 *
 * The boundary is `r > SCR` and not `r >= SCR`; `adversarial-inarray`'s third
 * record sits exactly at `r == SCR == 64` and is the boundary from the safe
 * side, p12's `adversarial-exact` analogue.
 *
 * **What this rung KEEPS is as important as what it drops.** It keeps the clamp
 * `m = min(nelem, SCR)`, so the *copy* is bounded and every read of the source
 * is in bounds; it keeps both cursor guards, so `p` never leaves the window.
 * The only thing missing is the one line that asks whether the rotate amount is
 * in range. That is what makes R1-vs-R1h the cost of the reduction and nothing
 * else.
 *
 * The guards are written subtraction-first (`len - p < 8`) rather than
 * additively (`p + 8 > len`) in all seven rungs. `p <= len` is maintained by
 * the guards themselves, so the subtraction cannot wrap; the additive form can
 * overflow `usize` for a window at the top of the address space and Verus
 * rejects it. p07's lesson: the spelling that makes the proof trivial is the
 * one that makes the bug impossible.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no reduction. THE BUG.
 *   c/kernel_hardened.c  R1h -- `if (m != 0) r %= m; else r = 0;`, and that one
 *                               line is the whole difference. `m == 0` would be
 *                               a DIVISION BY ZERO, so the contract pins the
 *                               answer rather than leaving it to the rung.
 *
 * Both take `buf_len`, and both ignore it: p06's bound is not the source
 * buffer's length, it is the SCRATCH's extent, which is a compile-time constant
 * in every rung. That is the contrast with p02, p16 and p17, where the check
 * the C rung skips is against a length it was handed, and it is p12's shape.
 *
 * **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
 * every call must return the same value; the scratch copy is what makes an
 * in-place pattern legal in this benchmark at all. `scr` is zero-initialised on
 * every call in every rung, which is what makes regime 1 deterministic and
 * identical across rungs.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + scr[i]`,
 * `acc*31 + m` and the return expression are the wrapping operations ../spec.md
 * asks for with no special spelling. The only undefined behaviour this rung can
 * execute is the out-of-bounds access the first reverse performs when
 * `r > SCR`, and it is both a READ and a WRITE of `scr`.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nrec`, `nelem`, `r` -- all 2^32 values of each -- and
 * every byte of the window are attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P06_KERNEL_H */
