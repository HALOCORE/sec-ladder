#ifndef P16_KERNEL_H
#define P16_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p16: walk a chain of length-prefixed (TLV) records inside one window of
 * `buf` and fold every byte it visits into a checksum.
 *
 *   p = off; end = off + len
 *   while a 3-byte header fits:
 *       fold the tag byte
 *       vlen = buf[p+1] + 256 * buf[p+2]        (little-endian u16)
 *       if the value does not fit -> stop
 *       fold vlen value bytes
 *       p += 3 + vlen; nrec++
 *   return the fold, with the record count mixed in
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- trusts `vlen`. THE BUG (CWE-125, OOB read).
 *   c/kernel_hardened.c  R1h -- same code plus `vlen > end - (p + 3)`.
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
 * call site instead). Everything else -- every `vlen` the wire can express, and
 * therefore the number of iterations and the position of every record -- is
 * attacker data and is the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P16_KERNEL_H */
