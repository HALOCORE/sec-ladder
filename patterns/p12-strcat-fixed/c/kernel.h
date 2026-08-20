#ifndef P12_KERNEL_H
#define P12_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p12: `strcat` into a fixed buffer. One window holds a declared count of
 * packed, NUL-terminated strings; the kernel concatenates them into a
 * fixed-size local `dst[DST_CAP]` and folds the result. CWE-787 / CWE-121 --
 * the classic stack buffer overflow, and the first pattern in this project
 * whose bug is an unbounded WRITE into a fixed local rather than a read.
 * See ../README.md and ../NOTES.md 0.
 *
 *   window = buf[off .. off+len)
 *   nstr        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   strings follow, packed, each terminated by one 0 byte
 *
 *   dst[DST_CAP] ; dlen = 0 ; acc = 0 ; p = 4
 *   for s in 0 .. nstr:
 *       q = first 0 byte at or after p, capped at len     <<< bounded in EVERY
 *       slen = q - p                                          rung: the scan is
 *       if dlen + slen <= DST_CAP:      <<< THE CHECK. R1 omits THIS LINE.
 *           for i in p .. q: dst[dlen++] = buf[off + i]
 *       acc = acc*31 + slen             u64, wrapping
 *       if q >= len: break              <<< no terminator: the last string
 *       p = q + 1
 *       if p >= len: break
 *   for i in 0 .. dlen: acc = acc*31 + dst[i]
 *   return (acc*31 + dlen)*31 + nstr
 *
 * **The bug is a write, and that changes what an input can be.** Every other
 * bug this project models is a read: p11's scan runs off the end looking for a
 * sentinel, p03's pop reads below its array, p17's index goes negative. A read
 * that stays inside the allocation is a silent wrong answer; a read that leaves
 * it faults. A WRITE past a fixed local corrupts whatever the frame put there,
 * so the failure mode is a function of the OVERFLOW MAGNITUDE and of what the
 * compiler laid out -- measured on this box at the gate's own flags:
 *
 *   +1 .. +8    silent under gcc AND clang: wrong answer, exit 0
 *   +16 .. +48  gcc `*** stack smashing detected ***`; clang still silent, and
 *               it corrupts the CALLER's locals
 *   +64 and up  gcc aborts; clang SIGSEGV -- the return address is gone
 *
 * `harness/build.py` passes no `-fstack-prot*` flag either way, so this is each
 * compiler's default: Debian gcc is `-fstack-protector-strong`, the upstream
 * clang tarball is nothing. ../NOTES.md 0 has the table and argues why an
 * `-fno-stack-protector` cell would be a thumb on the scale.
 *
 * **The scan is bounded by the window in every rung, R1 included.** That is
 * deliberate and it is what keeps p12 a write pattern: p11 already measured the
 * unbounded scan, and importing it here would put two bugs in one kernel.
 * `adversarial-nonul` is p11's malformed record arriving through p12's bug --
 * the scan stops correctly at the window end and the *copy* is what overruns.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no capacity check. THE BUG.
 *   c/kernel_hardened.c  R1h -- `if (dlen + slen <= DST_CAP)`, and that one
 *                               line is the whole difference.
 *
 * Both take `buf_len`, and both ignore it: p12's bound is not the source
 * buffer's length, it is the DESTINATION's capacity, which is a compile-time
 * constant in every rung. That is the contrast with p02, p16 and p17, where the
 * check the C rung skips is against a length it was handed. Here the number the
 * programmer needed was in the array declaration three lines up.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + slen`,
 * `acc*31 + dst[i]` and the return expression are the wrapping operations
 * ../spec.md asks for with no special spelling. The only undefined behaviour
 * this rung can execute is the out-of-bounds write itself, and the
 * out-of-bounds read of `dst` that the destination fold then performs.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nstr` -- all 2^32 values of it -- and every byte of the
 * window are attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P12_KERNEL_H */
