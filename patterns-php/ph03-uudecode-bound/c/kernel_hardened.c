/* ph03 rung R1h -- c/kernel.c plus the REAL upstream fix, and nothing else.
 *
 * ============================================================================
 * THE FIX, SHA-PINNED
 * ============================================================================
 *   commit  f95c1df583490814b0501c56f59671193a57507b
 *   author  Ilia Alshanetsky <iliaa@php.net>
 *   date    2004-08-24 15:25:48 +0000
 *   subject Fixed bug #29821 (Fixed possible crashes in convert_uudecode() on
 *           invalid data).
 *   file    ext/standard/uuencode.c, +17 lines, three hunks
 *   patch   controls/f95c1df58349.patch, 1433 bytes,
 *           sha256 fc3ef3c50488d0047b04629fabecb2d89aaa95d5b6f9b0085e6b61703a
 *                  c31a7f
 *           fetched from https://github.com/php/php-src/commit/f95c1df58349.patch
 *           and kept under the row so the citation survives with no network.
 *
 * All three hunks are here and nothing else moved. `PROTOCOL_PHP.md` §C: the
 * PAT programme has to argue its hand-written hardening is fair; here we do
 * not, because this is the patch PHP shipped.
 *
 * The line numbers below are in the PATCHED file and name the statements the
 * commit adds, not the blank lines it adds with them; reproduce them with
 * `patch -p1` on the pinned tarball (`.temp/php15/patchtest/`).
 * ⚠ hunk 2 read `:145-148` until TASK_PHP_015 (TASK_PHP_014 m1) and hunk 3 read
 * `:180-184`, which is `err:`'s preceding blank line through the function's
 * closing brace -- neither of which the commit adds.
 *
 *   hunk 1  `:139-142`  if (len > src_len) { goto err; }
 *   hunk 2  `:147-150`  if (ee > e)        { goto err; }
 *   hunk 3  `:181-183`  err: efree(*dest); return -1;
 *   hunk 3' `:215-218`  the CALLER's `if (dst_len < 0) ... RETURN_FALSE`, which
 *                       in this benchmark is the `if (n < 0)` in `kernel()`
 *                       below. It is part of the same commit and is included
 *                       for the same reason: R1h is the fix as shipped.
 *
 * The diff against c/kernel.c is those four blocks and the two comment blocks
 * that mark them. Signature, calling convention, the wrapper, the fold, the
 * allocator, `php_uu_floor`/`php_uu_ceil`, the dead `:158` tail block and the
 * return are all held fixed, so R1-vs-R1h is the cost of the fix and nothing
 * else (`.memory/02-bench-rules.md`, "The precondition must be structural").
 *
 * ============================================================================
 * ⚠⚠⚠ AND THE FIX IS INCOMPLETE. THIS IS THE ROW'S STRONGEST RESULT.
 * ============================================================================
 * `if (ee > e)` bounds where the inner loop *tests*, not where it *reads*. The
 * body reads `*(s+1)`, `*(s+2)` and `*(s+3)` under a loop condition that only
 * says `s < ee`, so it overshoots `ee` by up to 3 bytes whenever `ee - s` is
 * not a multiple of 4 -- which is every `len` except 45 and the few whose
 * `(int) floor(len * 1.33)` happens to be divisible by 4.
 *
 * MEASURED, `.temp/php13/02-reach.log` Q3, over the same 12 600 single-line
 * documents that give 3 608 over-reads and 3 352 over-writes unfixed:
 *
 *     with f95c1df58349 applied:   write past emalloc     0
 *                                  READ past src end    144   <- still there
 *
 * The smallest surviving case is `src_len = 2, len = 1`: `fl = 1`, so
 * `ee = s + 1 == e`, hunk 2 does not fire, and the body reads to `s + 3`, three
 * bytes past the end.
 *
 * ⚠⚠ AND THE OTHER HALF OF THE FIX IS DEAD. HUNK 1 DECIDES NOTHING.
 * TASK_PHP_014 M5 decomposed `goto err` by hunk over the same 12 600
 * documents: hunk 1 (`len > src_len`) fires 1 953 times and hunk 2 (`ee > e`)
 * would have refused ALL 1 953 of them -- 0 documents are refused by hunk 1
 * alone. Deleting hunk 1 from verus.rs's EXEC still gives `25 verified,
 * 0 errors`, and so does neutralising the matching branch in its SPEC, so the
 * two programs are the same program and Verus says so. The mechanism is one
 * line: `line_len(ln) >= ln` for every `ln` in 1..63, and after `s++` we have
 * `e - s <= src_len - 1`, so `len > src_len` forces `fl > e - s`.
 * `controls/negatives.py --emit no2004a` is the re-derivable form, and it is
 * the first control in either programme whose declared expectation is that the
 * mutant STILL VERIFIES.
 * So of a two-hunk fix, one hunk is dead and the other is incomplete.
 *
 * PHP took another TEN YEARS to close it:
 *
 *   commit  1e2818b143760a79a0887861bd6221b158355073
 *   author  Stanislav Malyshev <stas@php.net>, 2014-05-11
 *   subject Fix bug #67252: convert_uudecode out-of-bounds read
 *   patch   controls/1e2818b14376.patch, 2063 bytes,
 *           sha256 97975e658d67aaade1c24f6f4fb6cfc567abc2516f166cd3126f920e2d
 *                  ab5fff
 *   the fix  inside `while (s < ee)`:  if (s + 4 > e) { goto err; }
 *   and its own .phpt reproducer is exactly this shape -- 60 characters, a
 *   newline, then `"a."`: `PHP_UU_DEC('a') == 1`, so `fl == 1` and `ee == e`.
 *
 * ⚠⚠ THE 2014 FIX IS **NOT** IN THIS FILE, DELIBERATELY. `PROTOCOL_PHP.md` §C:
 * "An upstream fix is not automatically correct ... That is a result, and one
 * of the strongest a row can carry. REPORT IT; DO NOT REPAIR IT." R1h is
 * `fix_commit`, which for CRASH-115 is the 2004 commit. The Rust rungs DO carry
 * the 2014 check, and they have to -- see safe_naive.rs. That asymmetry is the
 * row's headline and it is stated in ../spec.md rather than smoothed over.
 *
 * ⚠ It is not shipped as an `inputs/adversarial-*.bin` either, and that is a
 * HARNESS limitation and not a choice: `harness/check.py::check_sanitizers_
 * hardened` hard-fails the gate if the R1h arm reports on ANY input, so a row
 * cannot carry "the upstream fix is incomplete" as gate evidence. It is
 * `controls/fix_incomplete.c` instead, run by hand with a must-fire control,
 * and the output is pasted into NOTES.md §5. Reported to the manager as a
 * finding.
 */
#include <stdint.h>
#include <stddef.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* --- substitution 3: libm-free `floor`/`ceil`. Identical to c/kernel.c;
 * see that file's header for the differential and the must-fire control. --- */
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

/* ============ uuencode.c:126-171 + f95c1df58349, hunks 1-3 ============== */
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
		/* sanity check */                       /* HUNK 1 */
		if (len > src_len) {
			goto err;
		}

		total_len += len;

		ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));
		/* sanity check */                       /* HUNK 2 */
		if (ee > e) {
			goto err;
		}

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

err:                                             /* HUNK 3 */
	efree(*dest);
	return -1;
}
/* ========================= end R1h kernel =============================== */

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    char *dest = NULL;
    uint64_t acc = 0;
    int n, i;

    php_shim_reset();
    n = php_uudecode((char *)(uintptr_t)(buf + off), (int)len, &dest);
    if (n < 0) {                                 /* HUNK 3' -- the caller's arm */
        acc = acc * 31 + (uint64_t)(unsigned int)n;
        return acc ^ php_shim_tally();           /* dest was efree'd at `err:` */
    }
    for (i = 0; i < n; i++)
        acc = acc * 31 + (uint64_t)(unsigned char)dest[i];
    acc = acc * 31 + (uint64_t)(unsigned int)n;
    efree(dest);
    return acc ^ php_shim_tally();
}
