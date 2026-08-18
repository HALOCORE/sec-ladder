#ifndef P08_KERNEL_H
#define P08_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p08: shift a fixed scratch buffer right to make room for a framing header --
 * the nested-encapsulation idiom, where each layer prepends its own header.
 * CWE-1341-adjacent, and in practice the plain one: **`memcpy` where `memmove`
 * is required.**
 *
 *   SCR    = 4096                                 a compile-time CAPACITY
 *   window = buf[off .. off+len)
 *   d      = u16 LE at window byte 0     the shift distance   ATTACKER DATA
 *   nrep_w = u16 LE at window byte 2     how many layers      ATTACKER DATA
 *   data   = window byte 4 onwards
 *   avail  = len - 4                     what actually ARRIVED
 *   m      = min(avail, SCR)
 *   nrep   = 1 + nrep_w % 4             1..=4, a MASK, not a check
 *
 *   if (m < 2 || d == 0 || d + nrep > m) return 0;   <<< the BOUNDS guard,
 *                                                         in EVERY rung
 *   scr[0..SCR] = 0
 *   scr[0..m]   = buf[off+4 .. off+4+m]
 *   for r in 0..nrep:
 *       dr = d + r
 *       scr[dr..m] <- scr[0..m-dr]       <<< THE OPERATION
 *   acc = 0
 *   for j in 0..m: acc = acc*31 + scr[j]
 *   return acc*31 + m
 *
 * **This is not a bounds bug and that is the point.** Every rung, R1 included,
 * carries the same guard, so `off + 4 + m <= buf_len` and every index into
 * `scr` is below `SCR`. Nothing leaves any allocation in any rung. The two C
 * cells differ in exactly one token:
 *
 *   c/kernel.c           R1  -- `memcpy(scr + dr, scr, m - dr)`.  THE BUG.
 *   c/kernel_hardened.c  R1h -- `memmove(...)`. One token apart.
 *
 * The move's source `[0, m-dr)` and destination `[dr, m)` overlap exactly when
 * `dr < m - dr`, i.e. `2*dr < m`, and `d` comes from the file -- so the overlap
 * is ATTACKER-CONTROLLED. `small` and `large` choose `d >= m/2` so no round
 * overlaps and every rung agrees; `adversarial-overlap` chooses `d = 3` and only
 * R1 executes undefined behaviour.
 *
 * `buf_len` is taken and ignored by both C cells, exactly as in p05 -- it keeps
 * the signature, the calling convention and the register allocation fixed
 * between R1 and R1h so that the only difference is the one token. Here it is
 * ignored for a *different* reason than in p05: p05's R1 needed the size and did
 * not look, p08's rungs genuinely do not need it, because `off + len <= buf_len`
 * is the caller's structural precondition and the kernel reads nothing outside
 * `buf[off .. off+len)`.
 *
 * Contract in ../spec.md. The caller must guarantee `off + len <= buf_len`. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P08_KERNEL_H */
