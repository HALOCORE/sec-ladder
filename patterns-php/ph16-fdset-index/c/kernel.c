/* ph16 rung R1 -- PHP 5.0.0's `stream_array_to_fd_set`, NARROWED. THE BUG.
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/ext/standard/streamsfuncs.c | sed -n '518,548p'
 *   -> 930 bytes, sha256 e3fbdff6d5e63f8e68f34884375d9256c84167858759563ca06a
 *                        7aabe68f9ff1
 *   plus the caller frame, PHP_FUNCTION(stream_select), at :653-718
 *   -> 2007 bytes, sha256 bad87d1ad43233f1f6dd8b643e30b5c418e69206f2b6062496fa
 *                         44d5e00b1cf8
 *   Corpus row CRASH-098.  Tier `narrowed`: the WRAPPER comes off (the
 *   `Z_TYPE_P`/`IS_ARRAY` test, the `zend_hash` cursor triple,
 *   `php_stream_from_zval_no_verify` and `php_stream_cast`); THE BODY IS
 *   UNCHANGED. Every divergence is itemised in ../spec.md's
 *   `provenance.divergences`, individually and with a line citation.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE
 * ============================================================================
 * `:540` tests one thing and `:541` writes with the other:
 *
 *     if (SUCCESS == php_stream_cast(stream, ..., (void*)&this_fd, 1)) {
 *         FD_SET(this_fd, fds);              <- :541.  NOTHING tests
 *         if (this_fd > *max_fd) {              this_fd < FD_SETSIZE
 *             *max_fd = this_fd;
 *         }
 *     }
 *
 * `FD_SET(d, s)` is a pure bit-set macro -- `s->__fds_bits[d/64] |= 1UL <<
 * (d%64)` -- and consults no file-descriptor table, so an index of 2048 writes
 * at byte offset 256 of a 128-byte object. ⭐ MEASURED, not reasoned:
 * `.temp/php11/fdset_probe.c` and `.temp/mgr166/fdfacts.c`.
 *
 * ⭐⭐ AND `fds` IS THE **CALLER's** OBJECT. `PHP_FUNCTION(stream_select)`
 * (`:653-718`) declares
 *
 *     fd_set  rfds, wfds, efds;                              :658
 *
 * and passes `&rfds`, `&wfds`, `&efds` in turn, then reads all three back
 * (`php_select(max_fd+1, &rfds, &wfds, &efds, tv_p)`, `:706`). So the bytes an
 * over-index reaches are not padding and not a redzone: they are the other two
 * `fd_set`s, live, and the function's own result depends on them. That is this
 * row's oracle and it needs no scaffolding -- ../NOTES.md §3.
 *
 * ⚠ THERE IS EXACTLY ONE LIMB HERE AND IT IS A WRITE. Nothing in this kernel
 * READS out of bounds: the fold walks the three `fd_set`s at their declared
 * size. ph03 had to ship two adversarial blobs because its read and its write
 * raced; this row's single limb is why the corrupted value is deterministic.
 *
 * ============================================================================
 * WHAT NARROWING REMOVED, AND WHY NONE OF IT IS A SEMANTIC CHANGE
 * ============================================================================
 * 1. `TSRMLS_DC` / `TSRMLS_CC` (`:518`, `:670-672`). Thread plumbing.
 *
 * 2. The `zend_hash` cursor triple at `:527-529`
 *    (`zend_hash_internal_pointer_reset` / `zend_hash_get_current_data` /
 *    `zend_hash_move_forward`) becomes an index walk over a flat run of
 *    entries. It is the CONTAINER, not the defect: `.memory-php/01`'s rule is
 *    that extraction cost is priced at the DEFECT site, and four rows have
 *    already been killed by pricing an adjacent frame's machinery.
 *
 * 3. `php_stream_from_zval_no_verify(stream, elem)` and its `stream == NULL`
 *    test (`:531-534`) become entry tag 0. The arm is kept; only the way the
 *    zval is turned into a `php_stream *` is gone.
 *
 * 4. `php_stream_cast(..., (void*)&this_fd, 1) == SUCCESS` (`:540`) becomes
 *    entry tags 1 (FAILURE) and 2/3 (SUCCESS, `this_fd` = the entry's index).
 *    `php_stream_cast` lives in main/streams/streams.c and dispatches on the
 *    stream's ops; what reaches `:541` is an `int` the caller does not bound,
 *    and that is what the entry carries.
 *
 * 5. `Z_TYPE_P(stream_array) != IS_ARRAY -> return 0` (`:524-526`) becomes a
 *    `ctl` bit. The arm is kept and `inputs/gen.py` asserts the corpus reaches
 *    it.
 *
 * 6. `stream_select`'s zval unpacking (`zend_parse_parameters`, `:663`), the
 *    timeout construction (`:678-693`), the read-buffer emulation (`:695-703`),
 *    `php_select` itself (`:706`) and the three `stream_array_from_fd_set`
 *    calls (`:714-716`) are outside this row: the first is argument parsing,
 *    the rest are downstream of the write and one of them -- `FD_ISSET` at
 *    `:577` -- is a DIFFERENT uncatalogued site (see ../NOTES.md §9).
 *    What is kept from that frame is exactly what decides this kernel's
 *    domain: the three `fd_set`s, `FD_ZERO` on each, `max_fd`, the `sets`
 *    accumulation and the `if (!sets) RETURN_FALSE` arm.
 *
 * ============================================================================
 * WHAT IS *NOT* CHANGED, AND MUST NOT BE
 * ============================================================================
 *   * `FD_SET(this_fd, fds)` stays the platform macro. An extraction that
 *     open-coded it as `bits[i >> 6] |= ...` would be re-implementing the very
 *     thing whose bound is at issue, and would lose the `_FORTIFY_SOURCE`
 *     interaction this row measures.
 *   * the three `fd_set`s stay THREE SEPARATE LOCALS in one frame, in
 *     upstream's declaration order. Packing them into an array or a struct
 *     changes what an over-write lands in, which is the row.
 *   * `int max_fd` stays an `int` and stays shared across the three calls.
 *   * `if (this_fd > *max_fd)` stays inside the `SUCCESS ==` arm.
 */

/* ⚠⚠⚠ FIRST, BEFORE ANY SYSTEM HEADER. See kernel.h's `_FORTIFY_SOURCE` block:
 * Ubuntu's gcc adds -D_FORTIFY_SOURCE=3 at -O2+, which turns FD_SET into
 * __fdelt_chk -- the row's own bound, inserted by the toolchain. PHP 5.0.0's
 * build had none. `controls/fortify.py` measures both configurations. */
#undef _FORTIFY_SOURCE
#define _FORTIFY_SOURCE 0

#include <stdint.h>
#include <stddef.h>
#include <sys/select.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* `fd_set` is `long int __fds_bits[FD_SETSIZE / NFDBITS]` on this platform, so
 * the fold below reads the object at its own granularity rather than byte by
 * byte, and the four Rust rungs' `[u64; 16]` is the same object. A C99
 * compile-time assertion, because a platform where this is false would make
 * every number in this row mean something else. */
typedef char ph16_fd_set_is_16_words[
    (sizeof(fd_set) == 16 * sizeof(unsigned long)
     && FD_SETSIZE == 1024) ? 1 : -1];

#define PH16_NWORDS 16

/* One entry of a stream array, as the blob carries it. `tag` stands in for
 * what the zval loop decides and `idx` for what `php_stream_cast` writes
 * through its `void*` out-parameter. */
#define PH16_TAG(e) ((unsigned)(e) >> 14)
#define PH16_IDX(e) ((int)((unsigned)(e) & 0x3FFFu))

/* ============ NARROWED: streamsfuncs.c:518-548 ============================ */
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
			FD_SET(this_fd, fds);             /* :541 -- THE DEFECT */
			if (this_fd > *max_fd) {
				*max_fd = this_fd;
			}
		}
	}
	return 1;
}
/* ========== end narrowed: streamsfuncs.c:518-548 ========================== */

/* One `fd_set`, folded at its own word granularity. Not part of PHP: it stands
 * in for `php_select(max_fd + 1, &rfds, &wfds, &efds, tv_p)` (`:706`), which is
 * what makes all three objects live across the call and is why an over-write
 * into one of them is observable at all. */
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

/* The benchmark wrapper. It plays the part of `PHP_FUNCTION(stream_select)`
 * (streamsfuncs.c:653-718): declare the three `fd_set`s and `max_fd`, zero
 * them, call in three times, and consume all three.
 *
 * ⚠⚠ THE THREE `fd_set`s ARE THE ROW. They are upstream's, in upstream's
 * order, in one frame -- and they are why this row does not need the
 * `volatile` canary `.temp/mgr166/asan_reach.c` had to invent. Measured:
 * under gcc they sit at +0/+128/+256 and under clang at +0/-128/-256, so
 * WHICH neighbour absorbs the over-write is a stack-layout fact the two
 * compilers disagree about, and the row states the range over which its oracle
 * is complete rather than assuming one (../NOTES.md §3).
 *
 * ⚠ No `php_shim_reset()` and no `php_shim_tally()`: this path allocates
 * nothing. `PROTOCOL_PHP.md` §B1.2/§B1.3 govern allocating rows;
 * `provenance.uses_allocator` is `false` and says so. The `c/emalloc_shim.h`
 * symlink is carried anyway, because that rule is UNCONDITIONAL. */
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

    /* How the window's entries divide between the three stream arrays. In PHP
     * this is three separate zval arrays with three separate counts; here the
     * split is derived so that it is TOTAL by construction and the kernel
     * never trusts a length out of the blob. */
    m   = (unsigned)((len - 6) / 2);
    n_r = split_r % (m + 1);
    rem = m - n_r;
    n_w = split_w % (rem + 1);
    n_e = rem - n_w;

    FD_ZERO(&rfds);
    FD_ZERO(&wfds);
    FD_ZERO(&efds);

    /* streamsfuncs.c:670-672 */
    if (!(ctl & 1u))
        sets += ph16_stream_array_to_fd_set(win, 0, n_r, (int)(ctl & 8u),
                                            &rfds, &max_fd);
    if (!(ctl & 2u))
        sets += ph16_stream_array_to_fd_set(win, n_r, n_w, (int)(ctl & 16u),
                                            &wfds, &max_fd);
    if (!(ctl & 4u))
        sets += ph16_stream_array_to_fd_set(win, n_r + n_w, n_e, (int)(ctl & 32u),
                                            &efds, &max_fd);

    /* ⚠ streamsfuncs.c:686 IS THE NEXT LINE IN THE FIXED SOURCE, AND THAT IS
     * THE THIRD GUARD. `c/kernel_hardened.c` has, between here and the
     * `if (!sets)` below, `PHP_SAFE_MAX_FD(max_fd, max_set_count)`, whose
     * POSIX arm clamps `max_fd` to `FD_SETSIZE - 1` so that `php_select` is
     * not handed an out-of-range `nfds`. This rung is PHP 5.0.0 and has
     * neither it nor the other two. */

    /* streamsfuncs.c:674-677 */
    if (!sets) {
        return 0xFFFFFFFFu;                   /* php_error_docref + RETURN_FALSE */
    }

    /* streamsfuncs.c:706 -- `php_select(max_fd + 1, &rfds, &wfds, &efds, tv_p)`
     * consumes `max_fd` and all three sets; :718 returns its result. The fold
     * is this row's stand-in for that consumption and nothing else. */
    acc = acc * 31u + (uint64_t)sets;
    acc = acc * 31u + (uint64_t)(uint32_t)max_fd;
    acc = acc * 31u + ph16_fold_set(&rfds);
    acc = acc * 31u + ph16_fold_set(&wfds);
    acc = acc * 31u + ph16_fold_set(&efds);
    return acc;
}
