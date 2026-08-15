#ifndef P02_KERNEL_H
#define P02_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p02: copy a length-prefixed record out of `src` into `dst`.
 *
 *   len  = src[src_off] | src[src_off+1] << 8      (little-endian u16)
 *   copy len bytes from src+src_off+2 into dst, then return the wrapping sum
 *   of the bytes that landed in dst.
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- trusts `len`. THE BUG.
 *   c/kernel_hardened.c  R1h -- same code plus the bounds check.
 *
 * Both take `src_len` and `dst_cap`, and that is the point: this API *has* the
 * sizes. R1 is not C being unable to check, it is C code that had everything it
 * needed and did not. R1-vs-R1h is therefore what the check costs inside one
 * language, with the calling convention held fixed
 * (`.memory/02-bench-rules.md`, "The precondition must be structural").
 *
 * The caller must guarantee `src_off + 2 <= src_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). Everything else -- the value of `len` above all -- is
 * attacker data and is the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *src, size_t src_len, size_t src_off,
                             uint8_t *dst, size_t dst_cap);

#endif /* P02_KERNEL_H */
