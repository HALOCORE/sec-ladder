/* ph29 rung R1 -- PHP 5.0.0's `stream_socket_recvfrom`, NARROWED. THE BUG.
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/ext/standard/streamsfuncs.c | sed -n '300,345p'
 *   -> 1231 bytes, sha256 (see ../spec.md provenance.extract_sha256)
 *   plus the transport frame, php_stream_xport_recvfrom, at
 *   main/streams/transports.c:381-392 -- the `flags == 0 && addr == NULL` arm,
 *   which is the one `stream_socket_recvfrom($s, $n)` takes.
 *   Corpus row CRASH-097.  Tier `narrowed`: the WRAPPER comes off
 *   (`zend_parse_parameters`, `php_stream_from_zval`, the `zval`s); THE BODY IS
 *   UNCHANGED. Every divergence is itemised in ../spec.md's
 *   `provenance.divergences`, individually and with a line citation.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE
 * ============================================================================
 * `:321` asks for a size the allocator cannot represent, and `:323` writes
 * with the size it ASKED for rather than the size it GOT:
 *
 *     long to_read = 0;                                          :304
 *     zend_parse_parameters(... "rl|lz" ..., &to_read, ...)       :309
 *     read_buf = emalloc(to_read + 1);                            :321  <- HERE
 *     recvd = php_stream_xport_recvfrom(stream, read_buf,
 *                                       to_read, ...);            :323
 *     read_buf[recvd] = '\0';                                     :332
 *
 * `to_read` comes from USERLAND, not from the socket -- that is the whole
 * reason this row is buildable from a blob (CATALOGUE.md, Part C, CRASH-097).
 * `emalloc` takes a `size_t` and truncates nothing at its signature; the
 * truncation is one frame down, at `Zend/zend_alloc.c:129`'s
 * `unsigned int real_size` and `:135`'s `real_size = REAL_SIZE(size)`.
 * ⭐ MEASURED, not reasoned: `.temp/php20/ph29_probe.c` (which settled it,
 * RECAP_PHP.md F46) and `controls/allocator.py` (which re-derives it here).
 *
 * ⚠⚠ THE ROW IS 64-BIT-ONLY. On a 32-bit build `long`, `size_t` and
 * `unsigned int` are all 32 bits, `REAL_SIZE` truncates nothing, and
 * `malloc(~2 GiB)` fails into `zend_alloc.c:189-194`'s `exit(1)`. We build
 * 64-bit, and `c/kernel.c` asserts the widths at compile time below.
 *
 * ⚠ THERE ARE TWO LIMBS HERE, A WRITE AND A READ, AND BOTH ARE UPSTREAM'S.
 * The write is the receive at `:323` plus the NUL at `:332`; the read is
 * `RETURN_STRINGL(read_buf, recvd, 0)` at `:340`, which hands the engine a
 * zval string of length `recvd` over a block that is not that long. ph16 had
 * exactly one limb; this row has ph03's shape.
 *
 * ============================================================================
 * WHAT NARROWING REMOVED, AND WHY NONE OF IT IS A SEMANTIC CHANGE
 * ============================================================================
 * 1. `TSRMLS_CC` (`:309`, `:326`). Thread plumbing.
 *
 * 2. `zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "rl|lz", &zstream,
 *    &to_read, &flags, &zremote)` (`:309`) becomes the window's first eight
 *    bytes. ⚠ THIS IS THE WRAPPER THE TIER NAMES: `PROTOCOL_PHP.md` §A1 makes
 *    `narrowed` exactly "a wrapper comes off (zval unpacking, argument
 *    parsing)". The defect is "a `long` from userland reaches `emalloc`", and
 *    the parse is HOW it gets there, not WHAT is wrong with it -- the parse
 *    itself is correct, and `"l"` on a 64-bit build yields a full `long`
 *    (`Zend/zend_API.c`'s `case 'l': convert_to_long_ex(arg)`), which is what
 *    the blob supplies. ../NOTES.md §2 argues this at length because it is the
 *    one place a reader could reasonably think the extraction changed the
 *    defect.
 *
 * 3. `php_stream_from_zval(stream, &zstream)` (`:313`) is gone: the stream is
 *    the window's payload bytes. `:323`'s call takes the `flags == 0 &&
 *    addr == NULL` arm (`main/streams/transports.c:390-392`), which is
 *    `php_stream_read(stream, buf, buflen)` with `buflen` a `size_t` -- so
 *    what the transport writes is `min(available, to_read)`, which is what
 *    `ph29_stream_read` below does.
 *
 * 4. `zval_dtor(zremote); ZVAL_NULL(zremote); Z_STRLEN_P(zremote) = 0;`
 *    (`:316-318`) and `Z_TYPE_P(zremote) = IS_STRING` (`:330`) become a `ctl`
 *    bit and two scalars. The ARMS ARE KEPT and `inputs/gen.py` asserts the
 *    corpus reaches both.
 *
 * 5. `if (PG(magic_quotes_runtime))` (`:334`) is deleted. It is a `php.ini`
 *    setting, not attacker data, and its shipped 5.0.0 default is 0
 *    (`main/main.c`'s `PHP_INI_ENTRY` for `magic_quotes_runtime`), so the
 *    measured arm is the `else` at `:339-341`. ⚠ Modelling it would ADD a
 *    second defect this row is not about -- that arm addslashes
 *    `Z_STRVAL_P(return_value)`, which nothing has set.
 *
 * 6. `RETURN_STRINGL(read_buf, recvd, 0)` (`:340`) becomes the fold over
 *    `read_buf[0 .. recvd)`. The `0` is `duplicate = 0`, i.e. the engine takes
 *    ownership of `read_buf` and its zval destructor `efree`s it later; that
 *    is the `php_shim_efree` below, and the `RETURN_FALSE` arm at `:344`
 *    reaches no `efree` at all -- 5.0.0 LEAKS `read_buf` there, which
 *    `php_shim_shutdown()` (the request boundary) reclaims exactly as PHP's
 *    own `shutdown_memory_manager` does.
 *
 * ============================================================================
 * WHAT IS *NOT* CHANGED, AND MUST NOT BE
 * ============================================================================
 *   * `emalloc(to_read + 1)` stays the shim's `php_shim_emalloc`, which is
 *     `_emalloc` line for line. An extraction that used `malloc` would report
 *     this defect as unreachable -- that is `PLAN_PHP.md` §4.3's documented
 *     failure, and this row is where it is finally tested.
 *   * `to_read` stays a `long` and the addition stays `to_read + 1`, in that
 *     order, with no widening. ⚠ That expression is SIGNED-OVERFLOW UB at
 *     `to_read == LONG_MAX`; the UB is PHP's and it is kept. `inputs/gen.py`
 *     REFUSES to emit `LONG_MAX`, so the measured corpus never evaluates it --
 *     RECAP_PHP.md F46's UB-free-trigger strengthening, applied to the
 *     negative side as well.
 *   * the buffer length passed to the transport stays `to_read`, NOT the
 *     block's real size. That gap IS the defect.
 *   * `int recvd` stays an `int` while the transport's `buflen` is a `size_t`.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
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

/* A C99 compile-time assertion that this really is the 64-bit build the row is
 * about. On a platform where `long`, `size_t` and `unsigned int` are the same
 * width, `REAL_SIZE` truncates nothing and every number in this row means
 * something else. */
typedef char ph29_is_64_bit[
    (sizeof(long) == 8 && sizeof(size_t) == 8 && sizeof(unsigned int) == 4)
    ? 1 : -1];

/* The window's head, in bytes. `payload` starts here. */
#define PH29_HEAD 12

/* What the kernel returns when `emalloc` hands back NULL. PHP prints to stderr
 * and `exit(1)`s (zend_alloc.c:189-198); a kernel must not exit or the driver
 * loop reports a build failure instead of a measurement, so the projection is a
 * sentinel. ../spec.md `provenance.divergences` itemises it as a `projection`.
 * ⚠ It is reachable: `emalloc(2^63)` fails under the shim too, because the
 * shim's `malloc` is the platform's. */
#define PH29_EALLOC 0xFFFFFFFEu

/* ============ NARROWED: transports.c:381-392, the flags==0 && addr==NULL arm
 * ============ `php_stream_xport_recvfrom` -> `php_stream_read(stream, buf,
 * buflen)`. The transport delivers what the socket has, capped by the caller's
 * `buflen` -- and `buflen` is the `size_t` widening of `to_read`, which is
 * exactly the quantity the allocation failed to honour. */
static int
ph29_stream_read(char *buf, size_t buflen, const uint8_t *pay, unsigned navail,
                 unsigned ctl, unsigned *textaddrlen)
{
	size_t n;

	if (ctl & 2u) {
		return -1;                        /* a failed recv; :328 takes `else` */
	}
	n = (size_t)navail;
	if (buflen < n) {
		n = buflen;                       /* transports.c:406-407's clamp */
	}
	memcpy(buf, pay, n);                  /* php_stream_read into read_buf */
	if (ctl & 1u) {
		/* transports.c:438-441 -- the transport fills `*textaddr` and
		 * `*textaddrlen` only when the caller asked for them, i.e. only when
		 * `zremote` was passed (streamsfuncs.c:324-325). */
		*textaddrlen = (unsigned)(n % 32u);
	}
	return (int)n;
}
/* ========== end narrowed: transports.c:381-392 ============================ */

/* ============ NARROWED: streamsfuncs.c:300-345 ============================ */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
	const uint8_t *win = buf + off;
	long to_read = 0;                          /* :304 */
	char *read_buf;                            /* :305 */
	int recvd;                                 /* :307 */
	unsigned ctl, want, navail, n_pay;
	unsigned remote_len = 0;                   /* Z_STRLEN_P(zremote) */
	unsigned remote_is_string = 0;             /* Z_TYPE_P(zremote) == IS_STRING */
	unsigned recorded;
	uint64_t h = 0;
	uint64_t acc = 0;
	int i;

	/* PROTOCOL_PHP.md §B1.3 -- one request per kernel call, so call N does not
	 * depend on call N-1's size-class cache. */
	php_shim_reset();

	/* :309 zend_parse_parameters(..., "rl|lz", &zstream, &to_read, &flags,
	 * &zremote) -- the wrapper, narrowed to the window's head. */
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

	/* How many bytes the socket has to give. Derived rather than trusted: the
	 * kernel never takes a length out of the blob, exactly as PHP never takes
	 * one -- a datagram knows its own length. */
	n_pay = (unsigned)(len - PH29_HEAD);
	navail = want % (n_pay + 1u);

	/* :315-319  if (zremote) { zval_dtor(zremote); ZVAL_NULL(zremote);
	 *                          Z_STRLEN_P(zremote) = 0; } */
	if (ctl & 1u) {
		remote_len = 0;
	}

	read_buf = emalloc(to_read + 1);           /* :321 */
	if (read_buf == (char *)0) {
		php_shim_shutdown();
		return PH29_EALLOC;                    /* zend_alloc.c:189, projected */
	}

	/* :323-326 */
	recvd = ph29_stream_read(read_buf, (size_t)to_read, win + PH29_HEAD,
	                         navail, ctl, &remote_len);

	/* zend_alloc.h:53's `unsigned int size:31` -- truncation T2, and the ONLY
	 * size the block itself records. `_efree` recomputes the cache class from
	 * it (zend_alloc.c:263), so it is what decides where this block goes next.
	 * Not part of PHP's own control flow; folded in because it is the second
	 * of the three truncations and it moves when T1 does, DIFFERENTLY. */
	recorded = php_shim_recorded_size(read_buf);

	if (recvd >= 0) {                          /* :328 */
		if ((ctl & 1u) && remote_len) {        /* :329 */
			remote_is_string = 1;              /* :330 Z_TYPE_P = IS_STRING */
		}
		read_buf[recvd] = '\0';                /* :332  <- THE FAULT */
		/* :340 RETURN_STRINGL(read_buf, recvd, 0) -- the engine takes a zval
		 * string of length `recvd` over this block and reads it. */
		for (i = 0; i < recvd; i++) {
			h = h * 31u + (uint64_t)(unsigned char)read_buf[i];
		}
		/* `duplicate = 0`: the zval owns `read_buf` and its destructor efrees
		 * it at the end of the statement. */
		efree(read_buf);
	}
	/* else :344 RETURN_FALSE -- `read_buf` is NOT freed. 5.0.0 leaks it. */

	/* zend_alloc.c:469-569 `shutdown_memory_manager`, the REQUEST boundary.
	 * It is what reclaims the leak above, and it is why a driver loop of
	 * 25 000 requests is bounded by instruction count and not by RSS. */
	php_shim_shutdown();

	acc = acc * 31u + h;
	acc = acc * 31u + (uint64_t)(uint32_t)recvd;
	acc = acc * 31u + (uint64_t)remote_len;
	acc = acc * 31u + (uint64_t)remote_is_string;
	acc = acc * 31u + (uint64_t)recorded;
	/* PROTOCOL_PHP.md §B1.2 -- the allocator's behaviour lands in the checksum
	 * the gate compares across rungs, not only in a sanitizer. */
	acc = acc * 31u + php_shim_tally();
	return acc;
}
/* ========== end narrowed: streamsfuncs.c:300-345 ========================== */
