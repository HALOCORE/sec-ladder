/* ph07 rung R1h -- c/kernel.c plus the guard configuration UPSTREAM CONVERGED
 * ON, and nothing else.
 *
 * ============================================================================
 * ⚠⚠⚠ R1h IS A TAGGED CONFIGURATION, NOT A COMMIT, AND THAT IS DELIBERATE
 * ============================================================================
 *   pinned as   php-5.2.12 .. php-5.2.17   (five tags, byte-for-byte)
 *   function    PHP_FUNCTION(mb_strcut), ext/mbstring/mbstring.c
 *   body sha256 26e2099e33433c74            (brace-matched body, 1823 B)
 *   guard       `if (from > Z_STRLEN_PP(arg1)) { RETURN_FALSE; }`   -- and
 *               NOTHING else.
 *
 *   TWO commits produce it, and the row cites BOTH:
 *     cb3cca21b34518caf45852ed90597052e99294c3   Ilia Alshanetsky, 2005-12-15
 *       "Fixed possible memory corruption inside mb_strcut()." +7 lines, ONE
 *       hunk, TWO guards. First shipped php-5.1.2 (2006-01-12); php-5.0.x
 *       never received it. controls/cb3cca21b345.patch, 829 B, sha256
 *       14dbafc9a3b970d048e0a24347c503b436c51d15e5fb382427be2bece5353b64.
 *       The corpus's `index.csv` names this commit in its `fix_commit` column.
 *     c2471b4950091c71da5e3f686d6d455e8e3092ea   Moriyoshi Koizumi, 2009-09-23
 *       "Fixed bug #49354 (mb_strcut() cuts wrong length when offset is within
 *       a multibyte character)." -3 lines: it REMOVES hunk (b) and ADDS
 *       ext/mbstring/tests/bug49354.phpt, a regression test.
 *       controls/c2471b495009.patch.
 *
 * ⚠⚠⚠ **THIS RUNG SHIPPED HUNK (b) UNTIL `TASK_PHP_018`, AND THE ROW'S OWN
 * GATE HAD ALREADY SAID WHY IT SHOULD NOT.** `check.py` stage 7h refuses an
 * R1h that changes benign output; the row read that as a harness limitation and
 * worked round it by keeping hunk (b)'s firing condition out of
 * `inputs/gen.py`. controls/fix_scope.py had the numbers all along: hunk (b)
 * removes **NONE** of the 15 333 out-of-bounds reads and changes the answer on
 * **15 870 of 117 612** benign calls (13.5 %). ⭐ **Upstream reached the same
 * verdict from a bug report and deleted it, four years later.** The gate was
 * right; the workaround was the defect.
 * ⭐ controls/bug49354.py replays upstream's own six expectations: this
 * configuration agrees on all six, and hunk (a)+(b) is wrong on one.
 *
 * ⚠ **WHY A CONFIGURATION AND NOT A COMMIT** -- stated because it is a
 * departure from `PROTOCOL_PHP.md` §C, which says R1h is *"the real upstream
 * `fix_commit`"*. A tag range is a stronger citation than a commit here, not a
 * weaker one: it is what upstream SHIPPED AND KEPT, it is pinnable by
 * `(tag range, function, body sha256)`, five tags carry it byte-for-byte, and
 * `php-5.3.2 .. php-5.3.29` carry the same configuration respelled
 * (`(unsigned int)from > string.len`, body sha256 49ad3ab2796d63e4). The
 * alternative -- ship the whole 2005 commit and disclose the 13.5 % -- is what
 * this row did until `TASK_PHP_018`, and it required a restricted corpus to be
 * measurable at all. ../spec.md `idiom.required[4]` states the choice and the
 * alternative; NOTES.md §4 has the tag sweep.
 *
 * ⚠⚠⚠ **THE FIX IS IN THE CALLER, IN ANOTHER FILE.** It is in
 * `PHP_FUNCTION(mb_strcut)` in `ext/mbstring/mbstring.c`, not in `mbfl_strcut`
 * in `mbfilter.c` -- which is why `mbfl_strcut`'s body is BYTE-FOR-BYTE
 * IDENTICAL from php-5.0.0 to php-5.3.2 (sha256 613648930a3d2551... at NINE
 * release tags -- 5.0.0, 5.0.5, 5.1.0, 5.1.1, 5.1.2, 5.2.17, 5.3.0, 5.3.1,
 * 5.3.2; the row said six until TASK_PHP_017 m3 measured nine).
 * **The bound was restored one function up and one file away.**
 * `.memory-php/01-extraction.md` F1 says the defect site, the guard site and
 * the faulting site can be three different places; this row adds the fourth:
 * ⭐ **THE REPAIR SITE IS A FOURTH FRAME, AND IT IS THE GUARD SITE.**
 *
 * ⚠ **WHY THAT IS NOT A FIDELITY PROBLEM HERE, STATED RATHER THAN SMOOTHED
 * OVER.** This row's kernel is two frames, not one: `ph07_strcut` is
 * `mbfl_strcut`'s mblen_table arm and the `kernel()` wrapper below **is**
 * `PHP_FUNCTION(mb_strcut)` -- it already carries that function's two negative
 * clamps (mbstring.c:1787-1805) because they decide the kernel's domain, and
 * SINCE TASK_PHP_018 that whole frame is pinned in `provenance.extra_spans[1]`
 * (`mbstring.c:1774-1812`) rather than merely lifted. The guard therefore lands
 * in the wrapper at exactly the position upstream put it: after the two
 * negative clamps and immediately before
 * `ret = mbfl_strcut(&string, &result, from, len);` (mbstring.c:1807). **The
 * diff below is upstream's diff, in upstream's place, against upstream's
 * neighbouring lines** -- `TASK_PHP_017` §3 verified that by function diff and
 * turned it into the R1h TRANSPLANT RULE. NOTES.md §4 states the residual
 * question -- an R1h whose citation is a different function from the extracted
 * one, and which is now a SUBSET of a labelled security fix -- rather than
 * hiding it.
 *
 * ============================================================================
 * THE TWO GUARDS THE 2005 COMMIT ADDED, AND WHY ONLY ONE IS HERE
 * ============================================================================
 *   hunk a  `if (from > Z_STRLEN_PP(arg1)) { RETURN_FALSE; }`   <- SHIPPED
 *   hunk b  `if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1)) {
 *               len = Z_STRLEN_PP(arg1) - from; }`              <- WITHDRAWN
 *
 * **(a) is the memory-safety half and (b) is not.** With `from <= string->len`
 * the start walk reads only at `n <= from <= len`, and `string->val[len]` is
 * the zval terminator, so every read is inside the `emalloc(len + 1)`.
 * Measured: (a) alone removes **all 15 333** out-of-bounds reads over the
 * 133 932 interpreted calls in controls/fix_scope.py, and (b) removes none.
 *
 * ⚠ **(b) CHANGES BENIGN OUTPUT -- on 15 870 of 117 612 calls (13.5 %) that
 * never crashed.** Where it fires it shortens `length`, which moves
 * `k = start + length` out of the `k >= string->len` shortcut into the BOUNDED
 * end walk and returns a SHORTER cut than 5.0.0 does. ⭐ **That is bug #49354,
 * and `c2471b495009` removed it with a regression test whose `--EXPECT--`
 * block pins six answers.** controls/bug49354.py runs those six against R1,
 * against this rung, and against the hunk-(a)+(b) variant.
 *
 * ⚠ Because (b) is gone, the corpus no longer has to avoid the region it fired
 * in: `inputs/gen.py` now REQUIRES windows with `from + length > string->len`
 * and asserts that some of them are windows where (b) would have moved the
 * answer. The one guard that must stay dead on a MEASURED input is (a), and
 * that is because a window (a) refuses is a window R1 over-reads on -- i.e. an
 * adversarial one. `inputs/adversarial-*.bin` is where those live.
 *
 * ⚠ **THE `(unsigned)` CASTS IN (b) WERE THE FIX'S OWN OVERFLOW HANDLING AND
 * THEY WERE NOT OBVIOUSLY RIGHT** -- recorded because it is a second, separate
 * defect in the same three lines. `from` and `len` are `long`s cast to a
 * 32-bit `unsigned`, so the sum wraps mod 2^32 and a large `len` can wrap under
 * `Z_STRLEN_PP(arg1)` and skip the clamp entirely. It never mattered for memory
 * safety, because (a) has already bounded `from` and `mbfl_strcut`'s end walk
 * is guarded. controls/ keeps the two-hunk variant, so the observation stays
 * checkable.
 *
 * ⚠ **THIS IS NOT THE ONLY TIME THE BOUND WAS RESTORED.** `d9dda48f8a7e`
 * (2010-03-12, "Update the bundled libmbfl to the latest on upstream", 64
 * files, +3435 -4164, no security label) rewrote `mbfl_strcut` and gave it a
 * PROLOGUE clamp of its own, `if (from >= string->len) { from = string->len; }`
 * -- first shipped in php-5.3.3. So `mbfl_strcut` remained unsafe FOR ANY
 * OTHER CALLER for four years and three months after `mb_strcut` was fixed.
 * That patch's mbfilter.c half is at controls/d9dda48f8a7e-mbfilter.patch and
 * controls/fix_scope.py measures it as an alternative R1h (`R1_2010`).
 * NOTES.md §4.
 *
 * ⚠ **AND THE SIGNEDNESS WARNING WENT WITH IT.** While hunk (b) was here,
 * `-Wall -Wextra` reported `comparison of integer expressions of different
 * signedness: unsigned int and int32_t` on it -- upstream's own warning, kept
 * rather than cast away. Hunk (a) is `int > int` and warns about nothing, so
 * this rung is now warning-clean. That is a consequence of the change, not a
 * reason for it: `PROTOCOL_PHP.md` §C says report an upstream defect, do not
 * repair it, and what removed this one is upstream's own later commit.
 *
 * Everything below this comment is byte-identical to c/kernel.c except for the
 * lines marked `<-- R1h` and this header. `diff` proves it; NOTES.md §4
 * records the diff.
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
     * `c/kernel_hardened.c` has, between here and the call, the ONE guard
     * php-5.2.12 .. php-5.2.17 carries. This rung is PHP 5.0.0 and does not. */

    /* ---- R1h: php-5.2.12 .. php-5.2.17, in upstream's own position -------- */
    if (from > str_len) {
        return 0xFFFFFFFFu ^ php_shim_tally();   /* <-- R1h, cb3cca21b345
                                                  * hunk (a). RETURN_FALSE. No
                                                  * allocation was made, so the
                                                  * tally is the post-reset zero
                                                  * and this is the same value
                                                  * the NULL arm below
                                                  * produces. */
    }
    /* ⚠ cb3cca21b345 hunk (b) WAS HERE and is not any more -- c2471b495009,
     * bug #49354. It stays MEASURABLE in three places under controls/:
     * fix_scope.py's `R1h_ab` variant (Q1/Q2, 133 932 calls), guard_equiv.c's
     * `length_ab` column (5 122 triples against a build of the C), and
     * bug49354.py (upstream's own six expectations). */

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
