#ifndef PH03_KERNEL_H
#define PH03_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph03: uudecode one window of `buf` and fold the plaintext it produces.
 *
 *   src = buf + off;  src_len = len
 *   php_uudecode(src, src_len, &dest)          <- ext/standard/uuencode.c:126-171
 *   fold dest[0 .. total_len) into a u64, mix in total_len,
 *   efree(dest), xor in php_shim_tally()
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0 verbatim. THE BUG (CRASH-115).
 *   c/kernel_hardened.c   R1h -- the same file plus the three hunks of the real
 *                                upstream fix f95c1df583490814b0501c56f5967119
 *                                3a57507b (Ilia Alshanetsky, 2004-08-24, bug
 *                                #29821), and nothing else.
 *
 * The kernel does NOT take `buf_len`, and that is not an omission: PHP's own
 * `php_uudecode(char *src, int src_len, char **dest)` does not take one either.
 * The bound the defect is about is INSIDE the function -- `e = src + src_len`
 * at `:133`, computed and then never consulted by the inner loop at `:143` --
 * so giving the kernel an extra length would be modelling p16's defect ("the
 * size was in the signature and the code did not look") instead of this one
 * ("the size was in a local and the inner loop used a different one").
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (R5 proves it at the call
 * site instead). Everything else -- every value the length byte at `:136` can
 * take, and therefore `ee`, the trip count and every address touched -- is
 * attacker data and is the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* PH03_KERNEL_H */
