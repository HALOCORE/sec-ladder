/* ph03 control -- ⚠⚠⚠ THE 2004 UPSTREAM FIX IS INCOMPLETE, AND HERE IS THE RUN.
 *
 * ============================================================================
 * WHY THIS IS A CONTROL AND NOT AN `inputs/adversarial-*.bin`
 * ============================================================================
 * `PROTOCOL_PHP.md` §C: *"An upstream fix is not automatically correct ... That
 * is a result, and one of the strongest a row can carry. Report it; do not
 * repair it."*
 *
 * ⚠ **`harness/check.py` cannot hold that result.** Stage `7h`
 * (`check_sanitizers_hardened`) hard-fails the gate on **any** ASan/UBSan
 * diagnostic from the R1h arm, on **any** input, and says so in terms: *"R1h is
 * the rung that does NOT have the bug, so the expectation is `clean` on EVERY
 * input"*. So a row whose finding is *"the shipped fix still faults"* cannot
 * ship the demonstrating blob under `inputs/`; putting it there turns the
 * project's strongest available php result into a red gate. It lives here
 * instead, is run by hand, and its output is pasted into ../NOTES.md §5.
 * TASK_PHP_013 reports the tension as a finding.
 *
 * ============================================================================
 * WHAT IT SHOWS
 * ============================================================================
 * `f95c1df58349` adds `if (ee > e) { goto err; }`. `ee` bounds where the inner
 * loop TESTS; the body reads `*(s+1)`, `*(s+2)`, `*(s+3)`. So whenever
 * `ee - s` is not a multiple of 4 -- i.e. for almost every `len` other than 45
 * -- the loop reads up to 3 bytes past `ee`, and when `ee == e` those are past
 * the end of the source.
 *
 * The smallest instance is `src_len = 2`, `len = 1`: `fl = 1`, `ee = s + 1 == e`.
 * PHP's own 2014 reproducer (`ext/standard/tests/strings/bug67252.phpt`, in
 * ../controls/1e2818b14376.patch) is the same shape one line down: 60 characters,
 * a newline, then `"a."` -- `PHP_UU_DEC('a') == 1`.
 *
 * ============================================================================
 * BUILD AND RUN  (⚠ `env -u LD_PRELOAD`: PLAN_PHP.md §7 rule 14)
 * ============================================================================
 *   gcc -std=c99 -Wall -Wextra -O1 -g -fsanitize=address,undefined \
 *       -fstrict-aliasing -static-libasan -static-libubsan \
 *       patterns-php/ph03-uudecode-bound/controls/fix_incomplete.c \
 *       -o .temp/php13/fixctl
 *   env -u LD_PRELOAD .temp/php13/fixctl control   # MUST fire   (the detector is live)
 *   env -u LD_PRELOAD .temp/php13/fixctl benign    # MUST be silent
 *   env -u LD_PRELOAD .temp/php13/fixctl fixed     # FIRES -- the finding
 *   env -u LD_PRELOAD .temp/php13/fixctl fixed2014 # silent -- the 2014 fix closes it
 *
 * The source buffer is `malloc`ed at EXACTLY `src_len` bytes, deliberately: a
 * stack array or an over-allocated buffer gives the over-read slack to land in
 * and the control reports nothing, which is how this defect stayed invisible.
 * Grep for `AddressSanitizer`, never `ASan`.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PHP_UU_DEC(c) (((c) - ' ') & 077)
#define PHP_UU_ENC(c) ((c) ? ((c) & 077) + ' ' : '`')

static double php_uu_floor(double x) { double t = (double)(long)x; return t > x ? t - 1.0 : t; }
static double php_uu_ceil(double x)  { double t = (double)(long)x; return t < x ? t + 1.0 : t; }

/* uuencode.c:126-171 + f95c1df58349 (2004), and optionally + 1e2818b14376
 * (2014). `y2014 == 0` is exactly c/kernel_hardened.c's decoder. */
static int php_uudecode(char *src, int src_len, char **dest, int y2014)
{
	int len, total_len = 0;
	char *s, *e, *p, *ee;

	p = *dest = malloc((size_t)(php_uu_ceil(src_len * 0.75) + 1));
	s = src;
	e = src + src_len;

	while (s < e) {
		if ((len = PHP_UU_DEC(*s++)) <= 0) {
			break;
		}
		if (len > src_len) {              /* f95c1df58349 hunk 1 */
			goto err;
		}
		total_len += len;
		ee = s + (len == 45 ? 60 : (int) php_uu_floor(len * 1.33));
		if (ee > e) {                     /* f95c1df58349 hunk 2 */
			goto err;
		}
		while (s < ee) {
			if (y2014 && s + 4 > e) { /* 1e2818b14376, 2014 */
				goto err;
			}
			*p++ = PHP_UU_DEC(*s) << 2 | PHP_UU_DEC(*(s + 1)) >> 4;
			*p++ = PHP_UU_DEC(*(s + 1)) << 4 | PHP_UU_DEC(*(s + 2)) >> 2;
			*p++ = PHP_UU_DEC(*(s + 2)) << 6 | PHP_UU_DEC(*(s + 3));
			s += 4;
		}
		if (len < 45) {
			break;
		}
		s++;
	}
	*(*dest + total_len) = '\0';
	return total_len;
err:
	free(*dest);
	return -1;
}

/* An exactly-sized source. No slack: that is the whole point. */
static char *exact(const char *bytes, int n)
{
	char *b = malloc((size_t)n);
	memcpy(b, bytes, (size_t)n);
	return b;
}

int main(int argc, char **argv)
{
	const char *mode = argc > 1 ? argv[1] : "control";
	char *dst = NULL, *src;
	int n;

	if (!strcmp(mode, "control")) {
		/* MUST FIRE. If this is silent the detector is not live and every
		 * other line of output below is worthless. */
		char *b = malloc(8);
		printf("CONTROL  reading b[8] of an 8-byte malloc\n");
		fflush(stdout);
		printf("CONTROL  read %d -- NO DETECTOR FIRED (the detector is NOT live)\n",
		       (int)(unsigned char)b[8]);
		free(b);
		return 0;
	}

	if (!strcmp(mode, "benign")) {
		/* MUST BE SILENT: one well-formed 45-byte line + terminator. */
		char enc[80];
		int i, k = 0;
		enc[k++] = (char)PHP_UU_ENC(45);
		for (i = 0; i < 60; i++)
			enc[k++] = (char)PHP_UU_ENC(i);
		enc[k++] = '\n';
		enc[k++] = (char)PHP_UU_ENC(0);
		src = exact(enc, k);
		n = php_uudecode(src, k, &dst, 0);
		printf("BENIGN   src_len=%d -> total_len=%d (expect 45)\n", k, n);
		if (n >= 0) free(dst);
		free(src);
		return 0;
	}

	/* `fixed` / `fixed2014`: src_len = 2, len = 1 -> fl = 1, ee = s+1 == e.
	 * Hunk 2 does not fire; the body reads *(s+1), *(s+2), *(s+3), i.e. three
	 * bytes past a two-byte allocation. */
	{
		char two[2];
		int y2014 = !strcmp(mode, "fixed2014");
		two[0] = (char)PHP_UU_ENC(1);
		two[1] = (char)PHP_UU_ENC(0);
		src = exact(two, 2);
		printf("%-9s src_len=2, len byte declares 1, fl=1, ee == e "
		       "(2014 fix %s)\n", mode, y2014 ? "APPLIED" : "ABSENT");
		fflush(stdout);
		n = php_uudecode(src, 2, &dst, y2014);
		printf("%-9s returned %d -- no detector fired\n", mode, n);
		if (n >= 0) free(dst);
		free(src);
	}
	return 0;
}
