/* ph03 rung R1 -- PHP 5.0.0's `php_uudecode`, lifted VERBATIM. THE BUG.
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/ext/standard/uuencode.c | sed -n '126,171p'
 *   -> 939 bytes, sha256 9f68d3cfb639cb62a3ec7b685da1a8e4cec828085791e200c23f
 *                        fa8eb12778fe
 *   plus PHP_UU_DEC at `:66`.  Corpus row CRASH-115 (merged with V5C-116).
 *   Tier `verbatim`; every substitution below is itemised in ../spec.md's
 *   `provenance.deletions`, individually and with a line citation.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE
 * ============================================================================
 * `:133` computes the true end of the input, `e = src + src_len`, and the OUTER
 * loop at `:135` is the only thing that ever looks at it. The INNER loop's
 * bound is a different quantity computed at `:141`
 *
 *     ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));
 *
 * from `len`, which came out of the DATA one line earlier (`:136`,
 * `PHP_UU_DEC(*s++)`). A line whose length byte claims 45 while fewer than 60
 * characters remain makes `ee > e`, and the inner loop then
 *
 *   * READS  `*s, *(s+1), *(s+2), *(s+3)` past the end of the source, and
 *   * WRITES `*p++` three times per iteration past the end of
 *     `emalloc(ceil(src_len * 0.75) + 1)` at `:131`.
 *
 * ⚠ BOTH LIMBS ARE REAL AND WHICH ONE A DETECTOR SEES FIRST IS DECIDED BY THE
 * SOURCE BUFFER, NOT BY THE DEFECT. On an exactly-sized source the read leaves
 * the allocation first; give the source 60 bytes of slack and the read is
 * silent and the write is what fires. `inputs/gen.py` ships BOTH -- they differ
 * in nothing but that slack -- because the corpus labels this row `CWE-125`
 * (read) while its own `root_cause_id` says "writes past emalloc", and both
 * labels are right about a different buffer. NOTES.md §4.
 *
 * ============================================================================
 * THE THREE SUBSTITUTIONS, AND WHY NONE OF THEM IS A SEMANTIC CHANGE
 * ============================================================================
 * 1. `emalloc` -> `php_shim_emalloc`, `efree` -> `php_shim_efree`. That is the
 *    whole point of `common-php/emalloc_shim.h`: a substituted allocator is not
 *    neutral (`PLAN_PHP.md` §4.3). The shim is PHP 5.0.0's own `_emalloc` /
 *    `_efree`, line-cited to the same tarball.
 *
 * 2. `TSRMLS`/`PHPAPI` -- neither appears in `:126-171`. `php_uudecode`'s
 *    signature is already pure C. Nothing was removed for this.
 *
 * 3. ⚠⚠ `floor` and `ceil` -> `php_uu_floor` and `php_uu_ceil`, AND THIS IS
 *    FORCED BY THE HARNESS RATHER THAN CHOSEN. `harness/build.py:161-165`
 *    compiles exactly three translation units and links with NO `-lm`, and
 *    `build.py` is frozen (`PLAN_PHP.md` §2.1: editing it costs a 33-pattern
 *    re-measure). Measured, `.temp/php13/01b-floor-runtime.log`: a kernel
 *    calling libm's `floor`/`ceil` FAILS TO LINK in 6 of the 8 C cells --
 *    `gcc -O0` x{isolated,whole}, `clang -O0` x{isolated,whole} (undefined
 *    `floor`) and `clang -O3` x{isolated,whole} (undefined `ceil`). Only
 *    `gcc -O3` folds both away.
 *
 *    ⚠ THE FLOATING POINT IS THE MECHANISM AND IS NOT TIDIED AWAY. The
 *    substitutes take and return `double` and are called on exactly the same
 *    `double` expressions, so `len * 1.33` is still evaluated in binary64 and
 *    still truncated by `(int)`. What changes is only where the rounding
 *    instruction comes from. Differential, `.temp/php13/02-reach.log` Q1, with
 *    a must-fire control:
 *        php_uu_floor vs libm floor, len 0..63    : 0 disagreements
 *        php_uu_ceil  vs libm ceil,  n 0..10^6    : 0 disagreements
 *        CONTROL (truncate vs round-half-up)      : 38 disagreements
 *    `len` cannot leave `0..63` -- `PHP_UU_DEC` masks with `077` -- and
 *    `src_len` is the window, so those two ranges are the whole reachable
 *    domain. `PROTOCOL_PHP.md` §B2's rule ("modelled by an equivalent builtin
 *    is a claim that needs a DIFFERENTIAL TEST, not a comment") is why this
 *    paragraph carries numbers.
 *
 * ============================================================================
 * WHAT IS *NOT* CHANGED, AND MUST NOT BE
 * ============================================================================
 *   * `(int) floor(len * 1.33)` stays floating point (above).
 *   * `:158`'s `if ((len = total_len > (p - *dest)))` keeps its precedence bug.
 *     `>` binds tighter than `=`, so `len` receives 0 or 1 and `:160`/`:162`
 *     are dead. ⚠ MEASURED: the whole block is dead -- over 12 600
 *     (src_len, len) single-line documents the condition was true ZERO times,
 *     `.temp/php13/02-reach.log` Q2. Lifting it "fixed" to
 *     `len = total_len - (p - *dest)` would build a different program.
 *   * `while (s < ee)` reading `*(s+3)`: the loop tests `s` and reads `s+3`, so
 *     it overshoots `ee` by up to 3 whenever `ee - s` is not a multiple of 4.
 *     That is a SECOND, DISTINCT defect and the 2004 fix does not close it --
 *     see c/kernel_hardened.c and NOTES.md §5.
 */
#include <stdint.h>
#include <stddef.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* --- substitution 3: libm-free `floor`/`ceil`. See the header comment. ---
 * Correct for every non-negative finite argument: (double)(long)x truncates
 * toward zero, which is floor for x >= 0, and the guards make them correct for
 * negative arguments too. The kernel only ever passes `len * 1.33` with
 * len in 0..63 and `src_len * 0.75` with src_len >= 0. */
static double php_uu_floor(double x)
{
    double t = (double)(long)x;
    return t > x ? t - 1.0 : t;
}

static double php_uu_ceil(double x)
{
    double t = (double)(long)x;
    return t < x ? t + 1.0 : t;
}

#define floor(x) php_uu_floor(x)
#define ceil(x) php_uu_ceil(x)
#define emalloc(n) php_shim_emalloc(n)
#define efree(p) php_shim_efree(p)

/* ext/standard/uuencode.c:66 */
#define PHP_UU_DEC(c) (((c) - ' ') & 077)

/* ===================== VERBATIM: uuencode.c:126-171 ====================== */
static int php_uudecode(char *src, int src_len, char **dest)
{
	int len, total_len=0;
	char *s, *e, *p, *ee;

	p = *dest = emalloc(ceil(src_len * 0.75) + 1);
	s = src;
	e = src + src_len;

	while (s < e) {
		if ((len = PHP_UU_DEC(*s++)) <= 0) {
			break;
		}
		total_len += len;

		ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));

		while (s < ee) {
			*p++ = PHP_UU_DEC(*s) << 2 | PHP_UU_DEC(*(s + 1)) >> 4;
			*p++ = PHP_UU_DEC(*(s + 1)) << 4 | PHP_UU_DEC(*(s + 2)) >> 2;
			*p++ = PHP_UU_DEC(*(s + 2)) << 6 | PHP_UU_DEC(*(s + 3));
			s += 4;
		}

		if (len < 45) {
			break;
		}

		/* skip \n */
		s++;
	}

	if ((len = total_len > (p - *dest))) {
		*p++ = PHP_UU_DEC(*s) << 2 | PHP_UU_DEC(*(s + 1)) >> 4;
		if (len > 1) {
			*p++ = PHP_UU_DEC(*(s + 1)) << 4 | PHP_UU_DEC(*(s + 2)) >> 2;
			if (len > 2) {
				*p++ = PHP_UU_DEC(*(s + 2)) << 6 | PHP_UU_DEC(*(s + 3));
			}
		}
	}

	*(*dest + total_len) = '\0';

	return total_len;
}
/* =================== end verbatim: uuencode.c:126-171 ==================== */

/* The benchmark wrapper. It plays the part of `PHP_FUNCTION(convert_uudecode)`
 * (`:192-205`): call the decoder, then consume the result as a zval string of
 * exactly `dst_len` bytes (`:202 RETURN_STRINGL(dst, dst_len, 0)`). Folding
 * `total_len` bytes is therefore what PHP itself exposes to the caller, not an
 * extra read this benchmark invented.
 *
 * `php_shim_reset()` at the top is `PROTOCOL_PHP.md` §B1.3 and is NOT optional:
 * the driver loop calls this thousands of times and a size-class cache that
 * survived across calls would make call N depend on call N-1 and destroy the
 * marginal-Ir subtraction every number in this row rests on. `php_shim_tally()`
 * at the bottom is §B1.2 -- the allocator's own (n_alloc, n_free, n_cache_hit,
 * bytes_mallocked) lands in the checksum the gate compares across rungs, so a
 * rung that sized its destination differently cannot agree by accident.
 *
 * ⚠ The Rust rungs do not link the shim; they reproduce this tally
 * ARITHMETICALLY from the same `cap`. That is a pin on the ALLOCATION SIZE
 * across rungs and it is NOT evidence that any Rust rung ran PHP's allocator.
 * ../spec.md and NOTES.md §7 say so in terms. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    char *dest = NULL;
    uint64_t acc = 0;
    int n, i;

    php_shim_reset();
    n = php_uudecode((char *)(uintptr_t)(buf + off), (int)len, &dest);
    /* c/kernel_hardened.c has, and this rung does not (the third hunk of
     * f95c1df58349, at `:215-218` of the patched file):
     *     if (n < 0) {
     *         acc = acc * 31 + (uint64_t)(unsigned int)n;
     *         return acc ^ php_shim_tally();
     *     }
     */
    for (i = 0; i < n; i++)
        acc = acc * 31 + (uint64_t)(unsigned char)dest[i];
    acc = acc * 31 + (uint64_t)(unsigned int)n;
    efree(dest);
    return acc ^ php_shim_tally();
}
