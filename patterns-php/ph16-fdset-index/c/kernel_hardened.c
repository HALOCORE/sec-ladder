/* ph16 rung R1h -- the same kernel plus THE REAL UPSTREAM FIX.
 *
 * ============================================================================
 * THE COMMIT, AND WHICH PART OF IT THIS IS
 * ============================================================================
 * `99e290f882c9` -- Wez Furlong, 2004-09-17, *"Bug #24189: possibly unsafe
 * select(2) usage. Where possible we avoid it by using poll(2)."* -- first
 * shipped in php-5.1.0; php-5.0.x never received it. The patch bytes are at
 * `controls/99e290f882c9.patch` (27 368 B, sha256 in ../spec.md).
 *
 * ⚠ **CITE THE HUNK, NOT THE COMMIT** (`PROTOCOL_PHP.md` §F). The commit
 * touches TEN files and introduces `php_poll2`, an IPv6 `configure` probe and
 * an OpenSSL socket rework. What this rung carries is the POSIX branch of the
 * three `main/php_network.h` macros it adds, applied at the two sites in
 * `stream_array_to_fd_set`'s frame:
 *
 *   #ifdef PHP_WIN32
 *   # define PHP_SAFE_FD_SET(fd, set)    FD_SET(fd, set)                      // NO CHECK
 *   # define PHP_SAFE_MAX_FD(m, n)       do { if (n + 1 >= FD_SETSIZE) { _php_emit_fd_setsize_warning(n); }} while(0)
 *   #else
 *   # define PHP_SAFE_FD_SET(fd, set)    do { if (fd < FD_SETSIZE) FD_SET(fd, set); } while(0)
 *   # define PHP_SAFE_MAX_FD(m, n)       do { if (m >= FD_SETSIZE) { _php_emit_fd_setsize_warning(m); m = FD_SETSIZE - 1; }} while(0)
 *   #endif
 *
 * ⭐ **A MACRO NAMED `PHP_SAFE_…` WHOSE SAFETY IS `#ifdef`-CONDITIONAL, AND THE
 * WIN32 COMMENT IS CORRECT.** Win32's `fd_set` is `{ u_int fd_count; SOCKET
 * fd_array[FD_SETSIZE]; }` -- a COUNTED ARRAY, whose `FD_SET` stops at
 * `fd_count == FD_SETSIZE` -- so on that platform the bound lives in the data
 * structure rather than in the code and there is nothing for the macro to add.
 * **WE BUILD POSIX, SO THIS RUNG COMPILES THE GUARDED BRANCH**, and that is
 * stated here because a reader who greps the macro name will find a spelling
 * that checks nothing. Settled at `.tasks-php/UPSTREAM_001.md:147-170`,
 * re-confirmed from the patch at `.temp/mgr166/`.
 *
 * ============================================================================
 * ⚠⚠⚠ THE FIX IS **THREE** GUARDS ON POSIX, NOT ONE, AND NOT TWO
 * ============================================================================
 * `TASK_PHP_025` §2 named two. The patch has three, and the third is in the
 * CALLER's frame -- the frame this row's `kernel()` wrapper lifts:
 *
 *   (a) `&& this_fd >= 0` appended to the `php_stream_cast` test    (:540)
 *   (b) `FD_SET(this_fd, fds)` -> `PHP_SAFE_FD_SET(this_fd, fds)`   (:541)
 *   (c) `PHP_SAFE_MAX_FD(max_fd, max_set_count);` inserted in
 *       PHP_FUNCTION(stream_select) after the `if (!sets)` test     (:686 fixed)
 *
 * (b) is the memory-safety half. (c) is not about the write at all: it stops
 * `php_select(max_fd + 1, …)` being handed an `nfds` past `FD_SETSIZE`, which
 * (b) alone leaves possible -- `*max_fd = this_fd` is INSIDE the guarded arm
 * but is NOT itself bounded by the macro. **Both are carried here**, because
 * both are the shipped POSIX configuration and this row's `u64` folds
 * `max_fd`; `controls/fix_scope.py` prices each of the three separately.
 *
 * ⚠ **(a) IS DEAD IN THIS KERNEL AND THE ROW SAYS SO RATHER THAN SILENTLY
 * BANKING IT.** `this_fd` comes from `PH16_IDX(e)`, a 14-bit field, so it is
 * in `0 ..= 16383` and can never be negative. A kernel that admitted negative
 * indices would be modelling `FD_SET(-1, …)` = `1UL << -1`, which is a shift by
 * a negative count -- undefined behaviour in the SHIFT rather than the
 * out-of-bounds WRITE this row is about, and a different row
 * (`PLAN_PHP.md` §3.1 admits it as a variation). ../spec.md
 * `provenance.divergences` and `controls/fix_scope.py` Q3 measure the deadness
 * instead of asserting it.
 *
 * ⚠ `_php_emit_fd_setsize_warning(m)` is NOT carried: it is a diagnostic on
 * PHP's error handler, returns void, and this kernel has no error handler. The
 * CLAMP it precedes is carried. Declared as a `projection`.
 *
 * ⚠ `max_set_count` is NOT carried: the POSIX arm of `PHP_SAFE_MAX_FD` ignores
 * its second argument entirely (it is the Win32 arm that reads it), so the
 * `set_count` / `max_set_count` bookkeeping the patch adds to
 * `PHP_FUNCTION(stream_select)` is dead on this platform. Declared as a
 * `deletion`.
 *
 * ⚠⚠ **GUARD (a) IS A NESTED `if` HERE AND UPSTREAM WRITES `&&`, AND THE
 * REASON IS `PLAN_PHP.md` §3 CRITERION 4.** Upstream's line is
 * `if (SUCCESS == php_stream_cast(..., &this_fd, 1) && this_fd >= 0)`, one
 * condition with two conjuncts -- but writing it that way here would need
 * `this_fd` assigned BEFORE the cast test, which `c/kernel.c` does not do, and
 * the two files would then differ by an assignment as well as by the safety
 * lines. Nesting is the same predicate with the same short-circuit and it makes
 * the `diff` against `c/kernel.c` exactly: this `if` and its brace, `FD_SET` ->
 * `PHP_SAFE_FD_SET`, the `PHP_SAFE_MAX_FD` line and the two `#define`s.
 * ⚠ It was NOT nested when the row was first measured, and the difference is
 * REAL and is disclosed in `../NOTES.md` §8: the first spelling computed
 * `PH16_IDX(e)` for entries the tag test rejects, which is work `c/kernel.c`
 * does not do, and it put ~1 point of the R1-vs-R1h gap in the wrong place.
 *
 * ============================================================================
 * EVERYTHING ELSE IS `c/kernel.c` VERBATIM
 * ============================================================================
 * The two files differ in this header comment, in the two `#define`s below and
 * in the guards named above. `../NOTES.md` §4 has the `diff`.
 */

#undef _FORTIFY_SOURCE
#define _FORTIFY_SOURCE 0

#include <stdint.h>
#include <stddef.h>
#include <sys/select.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* main/php_network.h, as 99e290f882c9 adds it. THE POSIX BRANCH -- see the
 * header comment for why the Win32 spelling is unguarded and correct. */
#define PHP_SAFE_FD_SET(fd, set)   do { if (fd < FD_SETSIZE) FD_SET(fd, set); } while(0)
#define PHP_SAFE_MAX_FD(m, n)      do { if (m >= FD_SETSIZE) { m = FD_SETSIZE - 1; } } while(0)

typedef char ph16_fd_set_is_16_words[
    (sizeof(fd_set) == 16 * sizeof(unsigned long)
     && FD_SETSIZE == 1024) ? 1 : -1];

#define PH16_NWORDS 16

#define PH16_TAG(e) ((unsigned)(e) >> 14)
#define PH16_IDX(e) ((int)((unsigned)(e) & 0x3FFFu))

/* ============ NARROWED: streamsfuncs.c:518-548, + 99e290f882c9 ============ */
static int
ph16_stream_array_to_fd_set(
    const uint8_t *win,
    unsigned base,
    unsigned n,
    int not_an_array,
    fd_set *fds,
    int *max_fd)
{
	unsigned i;
	int this_fd;
	unsigned e;

	if (not_an_array) {                       /* Z_TYPE_P(...) != IS_ARRAY */
		return 0;
	}
	for (i = 0; i < n; i++) {
		e = (unsigned)win[6 + 2 * (base + i)]
		    | ((unsigned)win[7 + 2 * (base + i)] << 8);

		if (PH16_TAG(e) == 0) {               /* stream == NULL */
			continue;
		}
		/* get the fd.
		 * NB: Most other code will NOT use the PHP_STREAM_CAST_INTERNAL flag
		 * when casting.  It is only used here so that the buffered data warning
		 * is not displayed.
		 * */
		if (PH16_TAG(e) != 1) {               /* SUCCESS == php_stream_cast() */
			this_fd = PH16_IDX(e);
			if (this_fd >= 0) {               /* guard (a) */
				PHP_SAFE_FD_SET(this_fd, fds);    /* guard (b) -- :541 */
				if (this_fd > *max_fd) {
					*max_fd = this_fd;
				}
			}
		}
	}
	return 1;
}
/* ===== end narrowed: streamsfuncs.c:518-548, + 99e290f882c9 =============== */

static uint64_t ph16_fold_set(const fd_set *s)
{
    const unsigned long *b = (const unsigned long *)(const void *)s;
    uint64_t h = 0;
    int i;
    for (i = 0; i < PH16_NWORDS; i++) {
        h = h * 31u + (uint64_t)b[i];
    }
    return h;
}

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    const uint8_t *win = buf + off;
    fd_set rfds, wfds, efds;
    int max_fd = 0;
    int sets = 0;
    uint64_t acc = 0;
    unsigned ctl, split_r, split_w, m, n_r, n_w, n_e, rem;

    ctl     = (unsigned)win[0] | ((unsigned)win[1] << 8);
    split_r = (unsigned)win[2] | ((unsigned)win[3] << 8);
    split_w = (unsigned)win[4] | ((unsigned)win[5] << 8);

    m   = (unsigned)((len - 6) / 2);
    n_r = split_r % (m + 1);
    rem = m - n_r;
    n_w = split_w % (rem + 1);
    n_e = rem - n_w;

    FD_ZERO(&rfds);
    FD_ZERO(&wfds);
    FD_ZERO(&efds);

    if (!(ctl & 1u))
        sets += ph16_stream_array_to_fd_set(win, 0, n_r, (int)(ctl & 8u),
                                            &rfds, &max_fd);
    if (!(ctl & 2u))
        sets += ph16_stream_array_to_fd_set(win, n_r, n_w, (int)(ctl & 16u),
                                            &wfds, &max_fd);
    if (!(ctl & 4u))
        sets += ph16_stream_array_to_fd_set(win, n_r + n_w, n_e, (int)(ctl & 32u),
                                            &efds, &max_fd);

    PHP_SAFE_MAX_FD(max_fd, 0);               /* guard (c) -- the CALLER's */

    if (!sets) {
        return 0xFFFFFFFFu;                   /* php_error_docref + RETURN_FALSE */
    }

    acc = acc * 31u + (uint64_t)sets;
    acc = acc * 31u + (uint64_t)(uint32_t)max_fd;
    acc = acc * 31u + ph16_fold_set(&rfds);
    acc = acc * 31u + ph16_fold_set(&wfds);
    acc = acc * 31u + ph16_fold_set(&efds);
    return acc;
}
