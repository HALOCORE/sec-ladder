#ifndef PH07_KERNEL_H
#define PH07_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph07: cut one window's zval string with `mbfl_strcut`'s mblen_table arm and
 * fold the substring it returns.
 *
 *   window = [u32 from][u32 length][slen bytes of string][one NUL]
 *   string = {val = buf + off + 8, len = slen}      <- a zval string, exactly
 *   mbfl_strcut(&string, &result, from, length)     <- mbfilter.c:1179-1259
 *   fold result.val[0 .. result.len) into a u64, mix in result.len,
 *   mbfl_free(result.val), xor in php_shim_tally()
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0 narrowed. THE BUG (CRASH-124).
 *   c/kernel_hardened.c   R1h -- the same file plus the prologue hunk of the
 *                                real upstream fix
 *                                d9dda48f8a7e182ed8c0f56e5fde9e367131a07a
 *                                (Moriyoshi Koizumi, 2010-03-12), and nothing
 *                                else.
 *
 * ⚠⚠ THE WINDOW'S LAST BYTE IS A NUL AND THAT IS NOT PADDING -- IT IS THE ZVAL
 * TERMINATOR AND IT IS LOAD-BEARING TWICE OVER. `mb_strcut`'s `string.val` is
 * `Z_STRVAL_PP(arg1)` (mbstring.c:1775), i.e. a PHP string, and every PHP
 * string is `emalloc(len + 1)` with `val[len] == '\0'`. So:
 *
 *   * `mblen_table_utf8[0] == 1`, so a walk that reaches `val[len]` advances by
 *     one and stops -- which is exactly why the upstream fix clamps `from` to
 *     `string->len` and not to `string->len - 1`. A kernel handed a source with
 *     no terminator would make the fix look wrong;
 *   * a kernel that made the terminator implicit (by pointing `val` straight at
 *     the blob and letting the walk run into the NEXT window) would hide the
 *     over-read from every detector. `inputs/gen.py` therefore writes the NUL
 *     into the window, and the adversarial inputs have exactly one window and
 *     no slack, so the first byte past the terminator is also the first byte
 *     past the heap block.
 *
 * The kernel does NOT take `buf_len`, and that is not an omission: PHP's own
 * `mbfl_strcut(mbfl_string *string, mbfl_string *result, int from, int length)`
 * carries its bound INSIDE `string->len`, and the defect is that the start walk
 * never consults it (mbfilter.c:1202-1210). Handing the kernel a separate
 * length would be modelling a different bug.
 *
 * The caller must guarantee `off + len <= buf_len` and `len >= 9`; that is the
 * structural precondition every rung shares and no rung checks (R5 proves it at
 * the call site instead). Everything else -- `from`, `length` and every byte of
 * the string, and therefore the cursor, the trip count and every address
 * touched -- is attacker data and is the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* PH07_KERNEL_H */
