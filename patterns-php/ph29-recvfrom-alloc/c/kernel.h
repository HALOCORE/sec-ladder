#ifndef PH29_KERNEL_H
#define PH29_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph29: run one `stream_socket_recvfrom($s, $to_read)` call and fold what it
 * produced together with what the allocator did.
 *
 *   window = [i64 to_read][u16 ctl][u16 want][u8 payload[stride-12]]
 *
 *   the userland argument       long to_read           streamsfuncs.c:304/:309
 *   the allocation              emalloc(to_read + 1)   streamsfuncs.c:321
 *   the receive                 php_stream_read(...)   streamsfuncs.c:323
 *   the u64                     fold(bytes, recvd, remote_len, recorded_size,
 *                                    php_shim_tally())
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0 narrowed. THE BUG (CRASH-097).
 *   c/kernel_hardened.c   R1h -- the same file plus 445daac3ab1a (Ilia
 *                                Alshanetsky, 2004-07-28, "Fixed possible
 *                                crash in stream_socket_recvfrom() when
 *                                length parameter has a negative value"),
 *                                which is ONE guard, `if (to_read <= 0)`,
 *                                and is the corpus index's own `fix_commit`.
 *                                See kernel_hardened.c and ../spec.md
 *                                `idiom.required[4]`.
 *
 * ============================================================================
 * ⚠⚠⚠ THIS ROW CANNOT EXIST WITHOUT `common-php/emalloc_shim.h`
 * ============================================================================
 * `PLAN_PHP.md` §4.3 and `PROTOCOL_PHP.md` §B. `Zend/zend_alloc.c:129` declares
 *
 *     unsigned int real_size;
 *
 * and `:135` assigns `real_size = REAL_SIZE(size)` where `size` is a 64-bit
 * `size_t`. The STORE is the truncation (T1). `:182` then allocates
 * `sizeof(header) + padding + real_size + END_MAGIC_SIZE`, so an 18-exabyte
 * request becomes a HEADER-SIZED block that SUCCEEDS, and the receive at `:323`
 * writes into it.
 *
 * Under plain `malloc` there is no defect at all, and it disappears in TWO
 * different ways depending on the value -- measured, `controls/allocator.py`:
 *
 *     to_read = -4294967297   size = 18446744069414584320   malloc FAILS
 *                             -> PHP prints and exit(1)s at zend_alloc.c:189
 *     to_read =  4294967295   size = 4294967296             malloc SUCCEEDS
 *                             -> a real 4 GiB block; the write is IN BOUNDS
 *
 * The shim reproduces `_emalloc` line by line and the block it hands back is
 * `real_size` bytes; `c/kernel.c` overflows it. ⚠ This is the only row in the
 * corpus whose adversarial input is CLEAN under a substituted allocator, which
 * is why `PLAN_PHP.md` §4.3's warning is tested here and nowhere else.
 *
 * ============================================================================
 * ⚠⚠ WHAT THE KERNEL DOES *NOT* TAKE, AND WHY THAT IS THE ROW
 * ============================================================================
 * `emalloc` receives `to_read + 1` and NOTHING that says how big the block it
 * returns actually is. The block's size is `real_size`, a quantity the caller
 * never sees; the caller then hands `to_read` -- the number it ASKED for -- to
 * `php_stream_xport_recvfrom` as the buffer length. Handing this kernel a
 * capacity alongside the request would be modelling a different bug.
 *
 * The caller must guarantee `off + len <= buf_len` and `len >= 16`; that is the
 * structural precondition every rung shares and no rung checks (R5 proves it at
 * the call site instead). Everything else -- `to_read`, the control bits, the
 * datagram length and its bytes -- is attacker data and is the kernel's
 * problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* PH29_KERNEL_H */
