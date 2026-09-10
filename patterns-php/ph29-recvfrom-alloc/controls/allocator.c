/* ph29 -- the allocator control's C half. `controls/allocator.py` builds this
 * four ways and runs it; this file is not on any build path.
 *
 * ============================================================================
 * THE ONE QUESTION
 * ============================================================================
 * `PLAN_PHP.md` §4.3 and `PROTOCOL_PHP.md` §B say a substituted allocator is
 * not neutral and that an earlier effort reported a real defect as unreachable
 * because of one. `RECAP_PHP.md` F6 says the shim itself INVENTED a defect
 * once, in the file written to prevent that. **This row is the one that cannot
 * pass without the shim, so it is where both claims get tested.**
 *
 * The body below is `ext/standard/streamsfuncs.c:300-345` narrowed exactly as
 * `../c/kernel.c` narrows it -- same order, same types, same expressions -- but
 * with the allocator behind a `#define`:
 *
 *     -DUSE_SHIM=1   php_shim_emalloc / php_shim_efree   (PHP 5.0.0's _emalloc)
 *     -DUSE_SHIM=0   malloc / free
 *
 * and with the 2004 guard behind another:
 *
 *     -DGUARD=1      `if (to_read <= 0) RETURN_FALSE;`   (445daac3ab1a)
 *
 * ⚠ `argv[1]` selects ONE case. That is not tidiness: under plain `malloc`
 * `to_read = -1` is `malloc(0)`, which SUCCEEDS and is overflowed anyway, so a
 * must-NOT-fire control that ran every case would fire for a reason that is not
 * the row (`F52`: a probe whose setup encodes the answer evaluates fine and is
 * wrong).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <limits.h>

#ifndef USE_SHIM
#define USE_SHIM 1
#endif
#ifndef GUARD
#define GUARD 0
#endif

#if USE_SHIM
#define PHP_SHIM_IMPL
#include "emalloc_shim.h"
#define ALLOC(n)  php_shim_emalloc((size_t)(n))
#define FREEP(p)  php_shim_efree(p)
#define WHICH     "php_shim_emalloc (PHP 5.0.0 _emalloc, T1 + T2 modelled)"
#else
#define ALLOC(n)  malloc((size_t)(n))
#define FREEP(p)  free(p)
#define WHICH     "plain malloc"
#endif

/* the narrowed body, one call. Returns:
 *   0  ran, wrote `*wrote` bytes into a block of `*block` bytes
 *   1  the allocation FAILED   -- PHP prints and exit(1)s, zend_alloc.c:189
 *   2  445daac3ab1a REFUSED it -- RETURN_FALSE
 */
static int recvfrom_once(long to_read, const unsigned char *payload,
                         size_t navail, size_t *wrote, unsigned long *block)
{
	char *read_buf;
	int recvd;
	size_t n;
	size_t i;
	uint64_t h = 0;

#if GUARD
	if (to_read <= 0) {                    /* 445daac3ab1a */
		*wrote = 0;
		*block = 0;
		return 2;
	}
#endif
	read_buf = (char *)ALLOC(to_read + 1);            /* :321 */
	if (!read_buf) {
		*wrote = 0;
		*block = 0;
		return 1;
	}
#if USE_SHIM
	*block = php_shim_real_size((size_t)(to_read + 1));
#else
	*block = (unsigned long)(size_t)(to_read + 1);
#endif
	/* :323 -> transports.c:391 php_stream_read(stream, buf, (size_t)to_read) */
	n = navail;
	if ((size_t)to_read < n)
		n = (size_t)to_read;
	memcpy(read_buf, payload, n);
	recvd = (int)n;
	if (recvd >= 0) {                                 /* :328 */
		read_buf[recvd] = '\0';                       /* :332 */
		for (i = 0; i < (size_t)recvd; i++)           /* :340 RETURN_STRINGL */
			h = h * 31u + (uint64_t)(unsigned char)read_buf[i];
		FREEP(read_buf);
	}
	(void)h;
	*wrote = n + 1;
	return 0;
}

int main(int argc, char **argv)
{
	static const unsigned char payload[64] = {
		'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P',
		'Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5',
		'6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l',
		'm','n','o','p','q','r','s','t','u','v','w','x','y','z','!','?' };
	/* ⚠ KEEP IN STEP WITH controls/allocator.py's CASES table -- the Python
	 * side names them and this side numbers them. */
	static const struct { long to_read; const char *what; } cases[] = {
		{ 63,          "benign, cached class (real_size 64 <= 87)" },
		{ 4095,        "benign, uncached class -> malloc/free" },
		{ -4294967297L,"SHIPPED adversarial-trunc.bin: to_read + 1 == -2^32" },
		{ -1L,         "SHIPPED adversarial-neg.bin:   to_read + 1 == 0" },
		{ 4294967295L, "THE ROW'S TRIGGER, NOT SHIPPED: to_read + 1 == 2^32" },
		{ 0L,          "to_read == 0 -- NOT a defect, and the guard refuses it" },
	};
	long only = (argc > 1) ? strtol(argv[1], NULL, 10) : -999;
	unsigned navail = (argc > 2) ? (unsigned)strtoul(argv[2], NULL, 10) : 4u;
	unsigned k;

	printf("allocator = %s\n", WHICH);
	printf("guard     = %s\n", GUARD ? "445daac3ab1a APPLIED" : "none (5.0.0)");
	printf("navail    = %u\n\n", navail);
	printf("%-3s %-14s %-22s %-12s %-8s %s\n",
	       "#", "to_read", "size = to_read+1", "block bytes", "wrote", "case");
	for (k = 0; k < sizeof cases / sizeof cases[0]; k++) {
		long tr = cases[k].to_read;
		size_t size = (size_t)(tr + 1);
		size_t wrote = 0;
		unsigned long block = 0;
		int rc;
		if (only != -999 && (unsigned)only != k)
			continue;
#if USE_SHIM
		php_shim_reset();
#endif
		rc = recvfrom_once(tr, payload, navail, &wrote, &block);
		printf("%-3u %-14ld %-22zu %-12lu %-8zu %s\n",
		       k, tr, size, block, wrote, cases[k].what);
		if (rc == 1)
			printf("      ^^ ALLOCATION FAILED -- PHP exit(1)s at "
			       "zend_alloc.c:189. NO DEFECT.\n");
		else if (rc == 2)
			printf("      ^^ REFUSED by 445daac3ab1a. NO DEFECT.\n");
		else if (wrote > block)
			printf("      ^^ WROTE %zu BYTES INTO A %lu-BYTE BLOCK -- "
			       "OUT-OF-BOUNDS WRITE.\n", wrote, block);
		else
			printf("      ^^ in bounds.\n");
#if USE_SHIM
		printf("      tally: n_alloc=%llu n_free=%llu n_cache_push=%llu "
		       "bytes_mallocked=%llu bytes_requested=%llu\n",
		       (unsigned long long)php_shim_ag.n_alloc,
		       (unsigned long long)php_shim_ag.n_free,
		       (unsigned long long)php_shim_ag.n_cache_push,
		       (unsigned long long)php_shim_ag.bytes_mallocked,
		       (unsigned long long)php_shim_ag.bytes_requested);
#endif
	}
	return 0;
}
