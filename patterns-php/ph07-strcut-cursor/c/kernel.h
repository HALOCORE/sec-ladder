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
 *   c/kernel_hardened.c   R1h -- the same file plus ONE guard, in the CALLER's
 *                                frame: `if (from > str_len) RETURN_FALSE`,
 *                                which is
 *                                cb3cca21b34518caf45852ed90597052e99294c3
 *                                (Ilia Alshanetsky, 2005-12-15) hunk (a) after
 *                                c2471b4950091c71da5e3f686d6d455e8e3092ea
 *                                (2009-09-23, bug #49354) removed hunk (b).
 *                                That is the configuration php-5.2.12 ..
 *                                php-5.2.17 shipped and kept,
 *                                PHP_FUNCTION(mb_strcut) body sha256
 *                                26e2099e33433c74. See kernel_hardened.c:1-95
 *                                and ../spec.md idiom.required[4].
 *
 * ⚠⚠ THIS BLOCK NAMED `d9dda48f8a7e182ed8c0f56e5fde9e367131a07a` (2010) AS R1h
 * UNTIL TASK_PHP_024, AND THAT IS A DIFFERENT PROGRAM (TASK_PHP_022 M2). The
 * 2010 commit is an unlabelled 64-file libmbfl re-sync whose prologue CLAMPS
 * `from` to `string->len`; cb3cca21b345 hunk (a) RETURNS FALSE instead, and
 * ../spec.md's own `idiom.forbidden[2]` pins the 2010 clamp ABSENT precisely
 * because "cb3cca21b345 returns FALSE where the clamp returns a cut". So this
 * header described R1h as the very thing the contract forbids the Rust rungs
 * from being; controls/fix_scope.py measures the 2010 clamp separately as
 * `R1_2010` and it moves 5 717 answers. It was wrong from the day the row was
 * built -- it survived TASK_PHP_016, TASK_PHP_017 and the TASK_PHP_018 rebuild
 * -- and it is a rung-source doc comment, i.e. exactly what NOTES.md §0's
 * rule-6-addendum sentence claimed had been re-read. The 2010 commit is still
 * cited, correctly, at controls/d9dda48f8a7e-mbfilter.patch and NOTES.md §4c.
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
