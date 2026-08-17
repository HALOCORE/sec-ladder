#ifndef P17_KERNEL_H
#define P17_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p17: serve a list of HTTP suffix ranges (`Range: bytes=-N`) out of one window
 * of `buf`, folding every byte served into a checksum. CVE-2017-7529.
 *
 *   window = buf[off .. off+len)
 *   nsuf        = u16 LE at window byte 0
 *   suffixes    = nsuf u16 LE values from window byte 2
 *   body_start  = 2 + 2*nsuf
 *   content_len = len - body_start          (the real body length, derived)
 *
 *   for each suffix s:
 *       start = content_len - s             SIGNED. May be negative.
 *       end   = content_len
 *       if start < end (and, in R1h, start >= 0):
 *           fold buf[off + body_start + start .. off + len)
 *           nserved++
 *   return the fold, with the served count mixed in
 *
 * The identity that makes this pattern work: `body_start + start == len - s`
 * and `end - start == s`, so a request for the last `s` bytes serves exactly
 * `[len - s, len)`. The read never runs *past* the window -- it runs
 * **backwards**, and how far back is one attacker-controlled `u16`.
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no `start >= 0`. THE BUG (CWE-191 -> CWE-125).
 *   c/kernel_hardened.c  R1h -- the same code plus `&& start >= 0`.
 *
 * Both take `buf_len`, and that is the point: this API *has* the size. R1 is
 * not C being unable to check, it is C code that had what it needed and did not
 * look. R1-vs-R1h is therefore what the check costs inside one language, with
 * the calling convention, the argument count and the register allocation all
 * held fixed (`.memory/02-bench-rules.md`, "The precondition must be
 * structural").
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). Every suffix value the wire can express -- all 65 536 of
 * them -- is attacker data and is the kernel's problem.
 *
 * Note also what `buf_len` CANNOT buy back here, and it is the reason p17 is in
 * the catalogue. A bounds check against `buf_len` rejects `s > len`, which
 * reads before the allocation. It does **not** reject `content_len < s <= len`,
 * which reads the window's own suffix table: that read is inside the buffer,
 * so no bounds check anywhere -- C's, Rust's, or a proof of memory safety --
 * can see it. Only `start >= 0` can. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P17_KERNEL_H */
