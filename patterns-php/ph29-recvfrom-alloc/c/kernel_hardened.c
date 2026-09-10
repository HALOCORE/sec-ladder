/* ph29 rung R1h -- `c/kernel.c` plus THE REAL UPSTREAM FIX, backported and
 * sha-pinned. `PROTOCOL_PHP.md` §C, `PLAN_PHP.md` §4.4.
 *
 * ============================================================================
 * THE COMMIT, AND IT IS THE CORPUS INDEX'S OWN `fix_commit`
 * ============================================================================
 *   445daac3ab1aa26ad95f9c75177f1ae604f75d1d
 *   Ilia Alshanetsky <iliaa@php.net>, Wed 28 Jul 2004 23:21:54 +0000
 *   "Fixed possible crash in stream_socket_recvfrom() when length parameter
 *    has a negative value."
 *   ext/standard/streamsfuncs.c | 5 +++++     1 file changed, 5 insertions(+)
 *
 *   +	if (to_read <= 0) {
 *   +		php_error_docref(NULL TSRMLS_CC, E_WARNING,
 *   +		                 "Length parameter must be greater than 0.");
 *   +		RETURN_FALSE;
 *   +	}
 *
 * The patch bytes are under `../controls/445daac3ab1a.patch` (807 B, sha256
 * 48ac72d125ac39d200271013d1743fd3a87113db444c0697113483cbf8c1c1c2) so the
 * citation survives without network. Verified AT THE COMMIT and not at the
 * column (`PROTOCOL_PHP.md` §F5(iii)); the fetched bytes are byte-identical to
 * the manager's independently cached copy.
 *
 * ============================================================================
 * ⚠⚠⚠ THIS FIX DOES NOT REMOVE THIS ROW'S DEFECT, AND THAT IS THE RESULT
 * ============================================================================
 * `PLAN_PHP.md` §4.4: *"an upstream fix is not automatically correct ... That
 * is a result, and one of the strongest a row can carry. Report it; do not
 * repair it."* Measured, `../controls/fix_scope.py`:
 *
 *   to_read < 0        REFUSED by the guard. The defect is removed.
 *   to_read == 0       REFUSED by the guard -- and it was never a defect.
 *                      `emalloc(1)` is honoured, `recvd` is 0 and
 *                      `read_buf[0] = '\0'` is in bounds. So the guard is
 *                      OVER-broad on the safe side: 5.0.0 returned "" where
 *                      5.1.0 returns false and raises E_WARNING.
 *   to_read == 4294967295   PASSES the guard. `emalloc(2^32)` truncates to
 *                      `real_size = 0` and the receive overflows a
 *                      header-sized block. THE DEFECT SURVIVES.
 *
 * There is a SECOND upstream change, `6ac8ffdfea108696fe32b4738b779a00d2d4328c`
 * (Antony Dovgal, 2006-12-25, one line: `emalloc(to_read + 1)` ->
 * `safe_emalloc(1, to_read, 1)`, in the 5.2.0 -> 5.3.0 window), and it does not
 * remove it either -- `_safe_emalloc` checks in 64-bit `long` and then calls
 * the truncating `_emalloc` (`zend_alloc.c:238`, `PROTOCOL_PHP.md` §B).
 * `../controls/fix_scope.py` measures both, separately and together, and
 * ../spec.md `idiom.required[4]` and ../NOTES.md §4 say which this rung is and
 * what the other one costs.
 *
 * ⚠ R1h IS STAGE 1 ALONE. It is the whole of the commit the corpus names, it
 * is one file and five lines, and it is what shipped in 5.1.0 through 5.2.x.
 * That choice is defended in ../NOTES.md §4 and it is NOT `ph07`'s
 * subset-of-a-fix situation: this is a whole commit, not a hunk of one.
 *
 * Everything below this line is `c/kernel.c` verbatim except the five lines
 * marked `445daac3ab1a`.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include "kernel.h"

/* ⚠ `build.py:163-165` compiles EXACTLY THREE TUs -- common/driver.c, the
 * chosen kernel and c/main.c -- and for an `-h` cell the chosen kernel is THIS
 * file, not `c/kernel.c`. So this TU is the one that must define the allocator
 * state in an R1h build; `c/kernel.c` is never linked beside it. */
#define PHP_SHIM_IMPL
#include "emalloc_shim.h"

/* ⚠ `ph03`'s spelling, and it is why the two most-cited lines below are
 * upstream's own text rather than a paraphrase. `common-php/emalloc_shim.h`
 * is `_emalloc`/`_efree` transcribed line for line (see its own PROVENANCE
 * block), so redirecting the two names at it is a RENAME and not a change of
 * behaviour; `../spec.md`'s `provenance.divergences` itemises it as a
 * `substitution` and `../controls/allocator.py` + `../controls/oracle.py` are
 * the differential rather than this comment.
 * ⚠⚠ IT IS ALSO WHAT MAKES `read_buf = emalloc(to_read + 1);` MATCH THE
 * CITED LINE CHARACTER FOR CHARACTER. Before it, `provenance.py`'s kernel
 * overlap scored the row's OWN DEFECT LINE as a miss. */
#define emalloc(n)  php_shim_emalloc((size_t)(n))
#define efree(p)    php_shim_efree(p)

typedef char ph29_is_64_bit[
    (sizeof(long) == 8 && sizeof(size_t) == 8 && sizeof(unsigned int) == 4)
    ? 1 : -1];

#define PH29_HEAD 12
#define PH29_EALLOC 0xFFFFFFFEu

/* 445daac3ab1a -- what `RETURN_FALSE` at the new guard produces. R1 has no
 * such value because R1 has no such arm. */
#define PH29_LENGTH_REFUSED 0xFFFFFFFDu

static int
ph29_stream_read(char *buf, size_t buflen, const uint8_t *pay, unsigned navail,
                 unsigned ctl, unsigned *textaddrlen)
{
	size_t n;

	if (ctl & 2u) {
		return -1;
	}
	n = (size_t)navail;
	if (buflen < n) {
		n = buflen;
	}
	memcpy(buf, pay, n);
	if (ctl & 1u) {
		*textaddrlen = (unsigned)(n % 32u);
	}
	return (int)n;
}

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
	const uint8_t *win = buf + off;
	long to_read = 0;
	char *read_buf;
	int recvd;
	unsigned ctl, want, navail, n_pay;
	unsigned remote_len = 0;
	unsigned remote_is_string = 0;
	unsigned recorded;
	uint64_t h = 0;
	uint64_t acc = 0;
	int i;

	php_shim_reset();

	to_read = (long)((uint64_t)win[0]
	                 | ((uint64_t)win[1] << 8)
	                 | ((uint64_t)win[2] << 16)
	                 | ((uint64_t)win[3] << 24)
	                 | ((uint64_t)win[4] << 32)
	                 | ((uint64_t)win[5] << 40)
	                 | ((uint64_t)win[6] << 48)
	                 | ((uint64_t)win[7] << 56));
	ctl  = (unsigned)win[8]  | ((unsigned)win[9] << 8);
	want = (unsigned)win[10] | ((unsigned)win[11] << 8);

	n_pay = (unsigned)(len - PH29_HEAD);
	navail = want % (n_pay + 1u);

	if (ctl & 1u) {
		remote_len = 0;
	}

	/* ---- 445daac3ab1a, ext/standard/streamsfuncs.c, +5 lines ------------- */
	if (to_read <= 0) {
		/* php_error_docref(NULL TSRMLS_CC, E_WARNING,
		 *                  "Length parameter must be greater than 0."); */
		php_shim_shutdown();
		return PH29_LENGTH_REFUSED;            /* RETURN_FALSE */
	}
	/* ---- end 445daac3ab1a ------------------------------------------------ */

	read_buf = emalloc(to_read + 1);
	if (read_buf == (char *)0) {
		php_shim_shutdown();
		return PH29_EALLOC;
	}

	recvd = ph29_stream_read(read_buf, (size_t)to_read, win + PH29_HEAD,
	                         navail, ctl, &remote_len);

	recorded = php_shim_recorded_size(read_buf);

	if (recvd >= 0) {
		if ((ctl & 1u) && remote_len) {
			remote_is_string = 1;
		}
		read_buf[recvd] = '\0';
		for (i = 0; i < recvd; i++) {
			h = h * 31u + (uint64_t)(unsigned char)read_buf[i];
		}
		efree(read_buf);
	}

	php_shim_shutdown();

	acc = acc * 31u + h;
	acc = acc * 31u + (uint64_t)(uint32_t)recvd;
	acc = acc * 31u + (uint64_t)remote_len;
	acc = acc * 31u + (uint64_t)remote_is_string;
	acc = acc * 31u + (uint64_t)recorded;
	acc = acc * 31u + php_shim_tally();
	return acc;
}
