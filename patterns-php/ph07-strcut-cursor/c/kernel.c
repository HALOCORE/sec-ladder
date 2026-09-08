/* ph07 rung R1 -- PHP 5.0.0's `mbfl_strcut`, mblen_table arm, NARROWED. THE BUG.
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/mbfl/mbfilter.c \
 *       | sed -n '1179,1259p'
 *   -> 1489 bytes, sha256 5edc6c04b7ff5f64255ae6b01d17f0a4e3afe9ec54525f97cbd
 *                         703a91c451f55
 *   plus `mblen_table_utf8` at ext/mbstring/libmbfl/filters/mbfilter_utf8.c:39-56
 *   and the two caller clamps at ext/mbstring/mbstring.c:1787-1805.
 *   Corpus row CRASH-124.  Tier `narrowed`: the WRAPPER comes off (the
 *   `mbfl_no2encoding` lookup, `mbfl_string_init`, the WCS/SBCS sibling arms
 *   and the `else` filter-chain arm); THE BODY IS UNCHANGED. Every divergence
 *   is itemised in ../spec.md's `provenance.divergences`, individually and with
 *   a line citation.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE
 * ============================================================================
 * `:1179` reads the true length, `len = string->len`, and the START WALK at
 * `:1202-1210` never looks at it:
 *
 *     for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }
 *
 * The only exit is `n > from`, `from` is the caller's untrusted offset, and `p`
 * is never compared against `string->val + string->len`. So `mb_strcut($s,
 * strlen($s) + 1, 1)` walks `p` past the end of the zval string and READS
 * there. `len` is used only by the clamps at `:1227-1241` -- AFTER the walk,
 * which is after the over-read has already happened.
 *
 * ⭐⭐ AND THE SAME FUNCTION'S SECOND WALK IS BOUNDED. `:1213` is
 *
 *     k = start + length;
 *     if (k >= (int)string->len) { end = string->len; } else { ... }
 *
 * so the END search runs only while `n <= k < string->len` and every byte it
 * reads is in range. **`mbfl_strcut` guards its end search and not its start
 * search**, in adjacent lines, in one function. That asymmetry is this row's
 * finding; NOTES.md §5.
 *
 * ⚠ THERE IS EXACTLY ONE LIMB HERE, AND IT IS A READ. After the walk the clamps
 * force `0 <= start <= end <= len`, so the copy at `:1248-1252` is always in
 * bounds however wild the walk was. ph03 had to ship two adversarial blobs
 * because its read and its write raced; this row cannot. NOTES.md §6.
 *
 * ============================================================================
 * WHAT NARROWING REMOVED, AND WHY NONE OF IT IS A SEMANTIC CHANGE
 * ============================================================================
 * 1. `encoding = mbfl_no2encoding(string->no_encoding)` (`:1169`) and the
 *    `encoding == NULL` test (`:1170`). The kernel is compiled for ONE
 *    encoding, UTF-8, whose `mbfl_encoding` record is a compile-time constant
 *    (mbfilter_utf8.c:58-65): `mblen_table_utf8`, flag `MBFL_ENCTYPE_MBCS`.
 *    Resolving a constant at build time instead of at run time is a wrapper
 *    removal, which is what `narrowed` means.
 *
 * 2. The `MBFL_ENCTYPE_WCS2*` and `MBFL_ENCTYPE_WCS4*` arms (`:1182-1193`).
 *    They are `else if`s on `encoding->flag`, and UTF-8's flag is
 *    `MBFL_ENCTYPE_MBCS`, so on this kernel's domain they are DEAD. The
 *    surviving `else if (encoding->mblen_table != NULL)` is the arm reached.
 *
 * 3. The `else` arm at `:1260+` -- libmbfl's filter-chain object model, which
 *    is what the corpus's kill sentence was about. It is the `mblen_table ==
 *    NULL` path and this kernel never has a NULL table.
 *
 * 4. `mbfl_string` keeps `{val, len}` and drops `{no_language, no_encoding}`
 *    (mbfl_string.h:41-46), which are inputs to the encoding lookup removed in
 *    (1) and are read nowhere in `:1179-1259`.
 *
 * 5. `mbfl_malloc` / `mbfl_free` -> `php_shim_emalloc` / `php_shim_efree`.
 *    ⚠ These are NOT plain `malloc`: `mbfl_allocators.h:48` defines
 *    `mbfl_malloc` as `(__mbfl_allocators->malloc)`, and `mbstring.c:764`
 *    points `__mbfl_allocators` at `_php_mb_allocators`, whose `malloc` is
 *    `emalloc` (`mbstring.c:240-243`) and whose `free` is `efree`
 *    (`mbstring.c:255-258`). So the allocator on this path IS PHP's, and
 *    `common-php/emalloc_shim.h` is PHP 5.0.0's own `_emalloc`/`_efree`
 *    line-cited to the same tarball (`PLAN_PHP.md` §4.3).
 *
 * 6. `mbfl_string_init(result)` (`:1173`) is inlined as the two stores it makes
 *    to the fields this struct still has. `mbfl_string_init` is in
 *    mbfl_string.c and is outside the cited span.
 *
 * ============================================================================
 * WHAT IS *NOT* CHANGED, AND MUST NOT BE
 * ============================================================================
 *   * `for (;;)` stays a `for (;;)`. An extraction that "tidies" it into
 *     `while (p < string->val + string->len)` deletes the row.
 *   * the dead stores at `:1180-1181` (`start = from; end = from + length;`,
 *     both overwritten at `:1196-1197`) stay. They are in the span.
 *   * `if (p != NULL)` at `:1200` stays, though `p` is never NULL here.
 *   * `if (k >= (int)string->len)` keeps its cast. `string->len` is
 *     `unsigned int` (mbfl_string.h:45) and `k` is `int`; without the cast the
 *     comparison would promote to unsigned and the guard would behave
 *     differently for a negative `k`. Upstream wrote the cast; it stays.
 *   * the four `< 0` clamps at `:1230-1238` stay even though `start` and `end`
 *     cannot be negative on any reachable path.
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
