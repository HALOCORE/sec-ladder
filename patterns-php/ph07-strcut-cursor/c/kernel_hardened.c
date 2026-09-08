/* ph07 rung R1h -- c/kernel.c plus the REAL upstream fix, and nothing else.
 *
 * ============================================================================
 * THE FIX COMMIT
 * ============================================================================
 *   cb3cca21b34518caf45852ed90597052e99294c3
 *   Ilia Alshanetsky, 2005-12-15
 *   "Fixed possible memory corruption inside mb_strcut()."
 *   ext/mbstring/mbstring.c, +7 lines, ONE hunk, two guards.
 *   First shipped in php-5.1.2 (2006-01-12); php-5.0.x never received it.
 *   Patch bytes at controls/cb3cca21b345.patch, 829 B,
 *   sha256 14dbafc9a3b970d048e0a24347c503b436c51d15e5fb382427be2bece5353b64.
 *   The corpus's own `index.csv` names this commit in its `fix_commit` column.
 *
 * ⚠⚠⚠ **THE FIX IS IN THE CALLER, IN ANOTHER FILE.** It is in
 * `PHP_FUNCTION(mb_strcut)` in `ext/mbstring/mbstring.c`, not in `mbfl_strcut`
 * in `mbfilter.c` -- which is why `mbfl_strcut`'s body is BYTE-FOR-BYTE
 * IDENTICAL from php-5.0.0 to php-5.3.2 (sha256 613648930a3d2551... at six
 * release tags). **The bound was restored one function up and one file away.**
 * `.memory-php/01-extraction.md` F1 says the defect site, the guard site and
 * the faulting site can be three different places; this row adds the fourth:
 * ⭐ **THE REPAIR SITE IS A FOURTH FRAME, AND IT IS THE GUARD SITE.**
 *
 * ⚠ **WHY THAT IS NOT A FIDELITY PROBLEM HERE, STATED RATHER THAN SMOOTHED
 * OVER.** This row's kernel is two frames, not one: `ph07_strcut` is
 * `mbfl_strcut`'s mblen_table arm and the `kernel()` wrapper below **is**
 * `PHP_FUNCTION(mb_strcut)` -- it already carries that function's two negative
 * clamps (mbstring.c:1787-1805) because they decide the kernel's domain. The
 * fix's seven lines therefore land in the wrapper at exactly the position
 * upstream put them: after the two negative clamps and immediately before
 * `ret = mbfl_strcut(&string, &result, from, len);` (mbstring.c:1807). **The
 * diff below is upstream's diff, in upstream's place, against upstream's
 * neighbouring lines.** NOTES.md §4 states the residual question -- an R1h
 * whose citation is a different function from the extracted one -- rather than
 * hiding it.
 *
 * ============================================================================
 * THE TWO GUARDS, AND WHAT EACH ONE DOES
 * ============================================================================
 *   hunk a  `if (from > Z_STRLEN_PP(arg1)) { RETURN_FALSE; }`
 *   hunk b  `if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1)) {
 *               len = Z_STRLEN_PP(arg1) - from; }`
 *
 * **(a) is the memory-safety half and (b) is not.** With `from <= string->len`
 * the start walk reads only at `n <= from <= len`, and `string->val[len]` is
 * the zval terminator, so every read is inside the `emalloc(len + 1)`.
 * Measured: (a) alone removes **all 15 333** out-of-bounds reads over the
 * 133 932 interpreted calls in controls/fix_scope.py, and (b) removes none.
 *
 * ⚠ **(b) CHANGES BENIGN OUTPUT**, and this row's corpus is built so that it
 * cannot: `inputs/gen.py::_check_span` refuses to write a window with
 * `from + length > string->len`, so neither guard fires on `small.bin` or
 * `large.bin` and R1h is byte-identical to R1 there. Where (b) does fire it
 * shortens `length`, which moves `k = start + length` from the
 * `k >= string->len` shortcut into the BOUNDED end walk and can therefore
 * return a shorter cut than 5.0.0 does -- on an input that never crashed.
 * controls/fix_scope.py counts it.
 * ⭐ **Upstream itself dropped (b) later**: php-5.2.17 carries (a) and not (b),
 * and php-5.3.29 carries `(unsigned int)from > string.len` alone. So the half
 * that changed benign behaviour did not survive and the half that closed the
 * read did.
 *
 * ⚠ **THE `(unsigned)` CASTS IN (b) ARE THE FIX'S OWN OVERFLOW HANDLING AND
 * THEY ARE NOT OBVIOUSLY RIGHT.** `from` and `len` are `long`s cast to a
 * 32-bit `unsigned`, so the sum wraps mod 2^32 and a large `len` can wrap under
 * `Z_STRLEN_PP(arg1)` and skip the clamp entirely. It does not matter for
 * memory safety, because (a) has already bounded `from` and `mbfl_strcut`'s
 * end walk is guarded; it matters for what (b) claims to do. Kept verbatim,
 * not repaired -- `PROTOCOL_PHP.md` §C: report it, do not repair it.
 *
 * ⚠ **THIS IS NOT THE ONLY TIME THE BOUND WAS RESTORED.** `d9dda48f8a7e`
 * (2010-03-12, "Update the bundled libmbfl to the latest on upstream", 64
 * files, +3435 -4164, no security label) rewrote `mbfl_strcut` and gave it a
 * PROLOGUE clamp of its own, `if (from >= string->len) { from = string->len; }`
 * -- first shipped in php-5.3.3. So `mbfl_strcut` remained unsafe FOR ANY
 * OTHER CALLER for four years and three months after `mb_strcut` was fixed.
 * That patch's mbfilter.c half is at controls/d9dda48f8a7e-mbfilter.patch and
 * controls/fix_scope.py measures it as an alternative R1h. NOTES.md §4.
 *
 * ⚠ **THE `> str_len` COMPARISON WARNS AND IS KEPT.** `-Wall -Wextra` reports
 * `comparison of integer expressions of different signedness: unsigned int and
 * int32_t` on hunk (b), because upstream compares an `unsigned` sum against an
 * `int` `Z_STRLEN_PP(arg1)`. Casting it away would be a divergence from the
 * shipped fix for a cosmetic gain; the warning is upstream's own and it stays.
 * `str_len >= 0` here, so the promotion is value-preserving and the two
 * spellings compute the same predicate on this kernel's domain.
 *
 * Everything below this comment is byte-identical to c/kernel.c except for the
 * lines marked `<-- cb3cca21b345` and this header. `diff` proves it; NOTES.md
 * §4 records the diff.
 */
#include <stdint.h>
#include <stddef.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

#define mbfl_malloc(n) php_shim_emalloc(n)
#define mbfl_free(p) php_shim_efree(p)

/* mbfl_string.h:41-46, narrowed to the two fields `:1179-1259` reads. */
typedef struct _mbfl_string {
    unsigned char *val;
    unsigned int len;
} mbfl_string;

/* ext/mbstring/libmbfl/filters/mbfilter_utf8.c:39-56, VERBATIM.
 *
 * ⚠ This is STATIC DATA in PHP and it is static data here. It is not part of
 * the blob and an attacker cannot choose it: `encoding->mblen_table` is a field
 * of a `const mbfl_encoding` (mbfilter_utf8.c:58-65). Putting it in the input
 * would invent a defect PHP does not have -- a table with a zero entry makes
 * the start walk spin forever -- and every entry of every shipped table is >= 1.
 * ../spec.md `provenance.divergences`; NOTES.md §3. */
static const unsigned char mblen_table_utf8[] = {
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
  4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 1, 1
};

/* ============ NARROWED: mbfilter.c:1179-1259, the mblen_table arm ========== */
static mbfl_string *
ph07_strcut(
    mbfl_string *string,
    mbfl_string *result,
    int from,
    int length)
{
	int n, m, k, len, start, end;
	unsigned char *p, *w;
	const unsigned char *mbtab;

	result->val = NULL;                 /* mbfl_string_init(result), :1173 */
	result->len = 0;

		len = string->len;
		start = from;
		end = from + length;
		{
			mbtab = mblen_table_utf8;   /* encoding->mblen_table, :1195 */
			start = 0;
			end = 0;
			n = 0;
			p = string->val;
			if (p != NULL) {
				/* search start position */
				for (;;) {
					m = mbtab[*p];
					n += m;
					p += m;
					if (n > from) {
						break;
					}
					start = n;
				}
				/* search end position */
				k = start + length;
				if (k >= (int)string->len) {
					end = string->len;
				} else {
					end = start;
					while (n <= k) {
						end = n;
						m = mbtab[*p];
						n += m;
						p += m;
					}
				}
			}
		}

		if (start > len) {
			start = len;
		}
		if (start < 0) {
			start = 0;
		}
		if (end > len) {
			end = len;
		}
		if (end < 0) {
			end = 0;
		}
		if (start > end) {
			start = end;
		}
		/* allocate memory and copy string */
		n = end - start;
		result->len = 0;
		result->val = w = (unsigned char*)mbfl_malloc((n + 8)*sizeof(unsigned char));
		if (w != NULL) {
			result->len = n;
			p = &(string->val[start]);
			while (n > 0) {
				*w++ = *p++;
				n--;
			}
			*w++ = '\0';
			*w++ = '\0';
			*w++ = '\0';
			*w = '\0';
		} else {
			result = NULL;
		}
	return result;
}
/* ========== end narrowed: mbfilter.c:1179-1259, mblen_table arm =========== */

/* The benchmark wrapper. It plays the part of `PHP_FUNCTION(mb_strcut)`
 * (mbstring.c:1737-1813): unpack the zval string and the two `long`s, apply the
 * CALLER's clamps, call in, then consume the result as a zval string of exactly
 * `ret->len` bytes (`:1810 RETVAL_STRINGL(ret->val, ret->len, 0)`).
 *
 * ⚠⚠ THE TWO CLAMPS BELOW ARE THE GUARD SITE AND THEY ARE HERE ON PURPOSE.
 * mbstring.c:1787-1805 clamps `from` FROM BELOW (a negative offset counts from
 * the end and then floors at 0) and clamps `len` FROM BELOW, and it never
 * clamps `from` from ABOVE against `Z_STRLEN_PP(arg1)`. Lifting the kernel
 * without them would let a negative `from` reach the walk, which mb_strcut
 * cannot produce, and would invent a difference between R1 and R1h that PHP
 * does not have (`d9dda48f8a7e`'s `from < 0 || length < 0` hunk would go live).
 * `.memory-php/01-extraction.md` F1: the defect site, the guard site and the
 * faulting site are three different places, and the guard belongs in the notes
 * -- here it belongs in the wrapper, because it is what decides the kernel's
 * domain.
 *
 * `php_shim_reset()` at the top is `PROTOCOL_PHP.md` §B1.3 and is NOT optional:
 * the driver loop calls this thousands of times and a size-class cache that
 * survived across calls would make call N depend on call N-1 and destroy the
 * marginal-Ir subtraction every number in this row rests on. `php_shim_tally()`
 * at the bottom is §B1.2 -- the allocator's own (n_alloc, n_free, n_cache_hit,
 * bytes_mallocked) lands in the checksum the gate compares across rungs, so a
 * rung that sized `mbfl_malloc((n + 8))` differently cannot agree by accident.
 *
 * ⚠ The Rust rungs do not link the shim; they reproduce this tally
 * ARITHMETICALLY from the same `n + 8`. That is a pin on the ALLOCATION SIZE
 * across rungs and it is NOT evidence that any Rust rung ran PHP's allocator.
 * ../spec.md and NOTES.md §7 say so in terms. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    mbfl_string string, result;
    const uint8_t *win = buf + off;
    uint64_t acc = 0;
    int32_t from, length, str_len;
    unsigned int slen;
    unsigned int i;

    php_shim_reset();

    from = (int32_t)((uint32_t)win[0] | ((uint32_t)win[1] << 8)
                     | ((uint32_t)win[2] << 16) | ((uint32_t)win[3] << 24));
    length = (int32_t)((uint32_t)win[4] | ((uint32_t)win[5] << 8)
                       | ((uint32_t)win[6] << 16) | ((uint32_t)win[7] << 24));

    /* mbstring.c:1774-1776 -- the zval string. `len - 9` is the window minus the
     * two head words and the terminator; `string.val[slen]` is that terminator
     * and is inside the blob.
     *
     * ⚠ TWO TYPES FOR ONE LENGTH, AND THEY ARE PHP'S, NOT OURS.
     * `Z_STRLEN_PP(arg1)` is an `int` (`zend.h`'s zval string `len`), which is
     * what mbstring.c compares `from` against; `mbfl_string.len` is an
     * `unsigned int` (mbfl_string.h:45), which is what mbfilter.c casts back to
     * `int` at `:1213`. Keeping both is what makes the guard below a
     * signed/signed comparison, exactly as upstream wrote it. */
    slen = (unsigned int)(len - 9);
    str_len = (int32_t)slen;
    string.val = (unsigned char *)(uintptr_t)(win + 8);
    string.len = slen;

    /* mbstring.c:1787-1793 -- a negative `from` counts from the end. */
    if (from < 0) {
        from = str_len + from;
        if (from < 0) {
            from = 0;
        }
    }
    /* mbstring.c:1795-1801 -- a negative `len` stops that many from the end. */
    if (length < 0) {
        length = (str_len - from) + length;
        if (length < 0) {
            length = 0;
        }
    }
    /* ⚠ mbstring.c:1807 IS THE NEXT LINE, AND THAT IS THE ROW.
     * `c/kernel_hardened.c` has, between here and the call, the two lines of
     * cb3cca21b34518caf45852ed90597052e99294c3 (Ilia Alshanetsky, 2005-12-15,
     * "Fixed possible memory corruption inside mb_strcut()"). This rung is
     * PHP 5.0.0 and does not. */

    /* ---- cb3cca21b345, backported verbatim, in upstream's own position ---- */
    if (from > str_len) {
        return 0xFFFFFFFFu ^ php_shim_tally();   /* <-- cb3cca21b345 hunk (a)
                                                  * RETURN_FALSE. No allocation
                                                  * was made, so the tally is
                                                  * the post-reset zero and this
                                                  * is the same value the NULL
                                                  * arm below produces. */
    }
    if (((unsigned)from + (unsigned)length) > str_len) {
        length = str_len - from;                 /* <-- cb3cca21b345 hunk (b) */
    }

    if (ph07_strcut(&string, &result, from, length) != NULL) {
        for (i = 0; i < result.len; i++)
            acc = acc * 31 + (uint64_t)result.val[i];
        acc = acc * 31 + (uint64_t)result.len;
        mbfl_free(result.val);
    } else {
        acc = 0xFFFFFFFFu;              /* mbstring.c:1812 RETVAL_FALSE */
    }
    return acc ^ php_shim_tally();
}
