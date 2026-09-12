/* ph45 -- THE PLACED ARENA.  ⚠⚠⚠ THIS FILE IS THE ROW'S CENTRAL DIVERGENCE AND
 * IT IS NOT LIFTED FROM THE TARBALL.  Everything else under `c/` is PHP 5.0.0;
 * this is the row's own construction, and `../spec.md`'s
 * `provenance.divergences[0]` itemises it with the §A1 formula.
 *
 * ============================================================================
 * WHY A ROW THAT MODELS A TRUNCATED POINTER HAS TO CHOOSE ITS ADDRESSES
 * ============================================================================
 * `mbfilter_htmlent.c:161` is `filter->cache = (int)mbfl_malloc(17);`.  On a
 * 2026 PIE process the heap sits at `0x55..`, so `(int)p` loses 16 bits on
 * EVERY allocation -- measured 40 of 40 by `TASK_PHP_034_REPORT` §5.3 -- and
 * `mbfl_filt_conv_html_dec_dtor`'s `mbfl_free((void*)filter->cache)` at `:169`
 * is UNCONDITIONAL, so the row SIGSEGVs in the destructor on an input with no
 * `&` in it at all: 60 of 60 runs, four inputs, `_034` §5.4.
 *
 * ⚠⚠ **So the forcing mechanism here is needed to make the BENIGN case work,
 * not the adversarial one.**  Without a placed arena there is no benign corpus,
 * `check.py` stage 2's checksum agreement can never be reached, and the row
 * cannot be measured at all.
 *
 * ⭐ AND THE PLACEMENT RESTORES THE PLATFORM THE CODE WAS WRITTEN FOR.  A
 * non-PIE `php` binary's `brk` heap on 2004 64-bit Linux sat below 2^32, so
 * `(int)p` was the IDENTITY -- which is exactly why this shipped, and why
 * bug #30573 was filed as *a compiler warning*.  `LO` is that platform.  `HI`
 * is a 2026 one.  **The row reports at both** (`../NOTES.md` §6).
 *
 * ============================================================================
 * WHAT IT GUARANTEES -- measured under all eight {gcc,clang} x {-O0,-O3} x
 * {-DSLB_ISOLATED,-flto} combinations, `.temp/php36/logs-02-placement.log`
 * ============================================================================
 *   LO = mmap(NULL, 4096, MAP_PRIVATE|MAP_ANONYMOUS|MAP_32BIT)
 *          -> always in [0x40000000, 0x42000000): bit 31 CLEAR, and
 *             `(char*)(int)p == p` EXACTLY.  `(int)` is the identity, so no
 *             implementation-defined conversion is even exercised and UBSan is
 *             silent on both rungs (`_034` §5.6).
 *   HI = mmap(LO + k*(1ULL<<32), 4096, ... |MAP_FIXED_NOREPLACE), smallest
 *        free `k`
 *          -> `(int)HI == (int)LO` for EVERY `k`: the truncation maps HI onto
 *             LO EXACTLY.  `k == 1` in an ordinary build; ⚠ under ASan the
 *             shadow occupies `[0x7fff8000, 0x10007fff7fff]` and swallows every
 *             `k` up to ~4096, which is why the search exists and why a row
 *             that insisted on `k == 1` exited 9 on all eight inputs of both
 *             sanitizer builds.  Nothing the row measures depends on `k`.
 *
 * Each region has its OWN bump offset, both reset at the top of every kernel
 * call, so the k-th block of LO and the k-th block of HI are exactly a multiple
 * of 2^32 apart and ALIAS under truncation.  That is not a construction bolted on for
 * the oracle: it is what two heap arenas whose bases differ by a multiple of
 * 2^32 do, and it is the only way the defect is observable WITHOUT a fault.
 *
 * `ph45_arena_init()` runs ONCE, from `main.c`, BEFORE the measured driver
 * loop -- `_034` §6.3(3): a per-call `mmap` would put a syscall inside the
 * marginal-`Ir` subtraction.
 *
 * ============================================================================
 * ⚠ WHAT `ph45_pl_free` IS, AND WHAT IT IS NOT
 * ============================================================================
 * It is a bump-arena free: it does NOT recycle.  PHP's `_efree` reads a block
 * header at `ptr - 24` and links the block into `AG(cache)[real_size>>3]`, so
 * on a truncated pointer it is a wild WRITE into whatever is at that address --
 * which is the fault `_034` reproduced, and which cannot be measured.  The row
 * PROJECTS that to four COUNTERS:
 *
 *     n_free        the address was one this arena issued and is live
 *     n_dfree       ... and was already dead   <- a double free
 *     n_wfree       ... was never issued       <- a wild free
 *     live_at_end   blocks still live when the call ends <- a leak
 *
 * ⚠ The counting is OBSERVATION and changes no control flow: `pl_free` does the
 * same thing (nothing) whichever arm it counts.  What the projection removes is
 * `efree`'s recycling, not a branch.  `controls/fatal.c` builds the FAITHFUL
 * spelling -- `common-php/emalloc_shim.h`, no arena -- and records the SIGSEGV.
 *
 * The four counters are folded into the kernel's `u64` (`PROTOCOL_PHP.md` §B1
 * rule 2), which is how R1-vs-R1h is visible in the CHECKSUM and not only in a
 * sanitizer.  In the `LO` regime every one of them is identical between the two
 * rungs, because in that regime the truncation is the identity -- and that is
 * `check.py` stage 7h being SATISFIED, not a defect (`../NOTES.md` §5).
 */
#ifndef PH45_ARENA_H
#define PH45_ARENA_H

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/mman.h>

/* `html_enc_buffer_size + 1` is 17; 32 is the 8-aligned slot that holds it with
 * room for a redzone-free neighbour.  Eight slots per region is four times what
 * the kernel's two filters need. */
#define PH45_BLOCK  32u
#define PH45_SLOTS  8u
#define PH45_REGION_BYTES 4096u          /* one page; mmap's granularity */
#define PH45_LO 0
#define PH45_HI 1

/* the two regions, and the bump offset of each.  `base[PH45_HI]` is
 * `base[PH45_LO] + k*2^32` for the smallest free `k`. */
static unsigned char *ph45_base[2];
static size_t ph45_bump[2];

/* Which region the NEXT `mbfl_malloc` serves.  ⚠ It is ALLOCATOR STATE and not
 * a parameter, because `mbfl_allocators.h:37` types the table entry as
 * `void *(*malloc)(unsigned int)` -- there is nowhere to put a parameter, which
 * is exactly the situation a real per-thread-arena allocator is in. */
static int ph45_region;

/* the issued-block ledger -- observation only, see the header comment. */
static struct { unsigned char *p; int live; } ph45_blk[2 * PH45_SLOTS];
static unsigned ph45_nblk;

static uint64_t ph45_n_alloc, ph45_n_free, ph45_n_dfree, ph45_n_wfree,
                ph45_bytes;

/* `mbfl_allocators.h:36-44` -- lifted VERBATIM.  The other five entries are
 * unreachable from the decode path and are NULL (`../spec.md`
 * `provenance.divergences`). */
typedef struct _mbfl_allocators {
	void *(*malloc)(unsigned int);
	void *(*realloc)(void *, unsigned int);
	void *(*calloc)(unsigned int, unsigned int);
	void (*free)(void *);
	void *(*pmalloc)(unsigned int);
	void *(*prealloc)(void *, unsigned int);
	void (*pfree)(void *);
} mbfl_allocators;

/* `mbfl_allocators.h:46` */
static mbfl_allocators *__mbfl_allocators;

/* `mbfl_allocators.h:48`, `:51`.  ⚠⚠ THE MECHANISM IS AN INDIRECTION THROUGH A
 * TABLE, NOT A FUNCTION -- which is what makes the row's substitution a
 * REBINDING of the same table PHP itself rebinds at `mbstring.c:764`, rather
 * than an edit to the extracted code.  `_034` §2.1. */
#define mbfl_malloc (__mbfl_allocators->malloc)
#define mbfl_free (__mbfl_allocators->free)

static void *ph45_pl_malloc(unsigned int n)
{
	int r = ph45_region;
	unsigned char *p;

	ph45_n_alloc++;
	if (n > PH45_BLOCK || ph45_bump[r] + PH45_BLOCK > PH45_REGION_BYTES)
		return NULL;                        /* the ctor's NULL arm, :161 */
	p = ph45_base[r] + ph45_bump[r];
	ph45_bump[r] += PH45_BLOCK;
	ph45_bytes += PH45_BLOCK;
	if (ph45_nblk < 2u * PH45_SLOTS) {
		ph45_blk[ph45_nblk].p = p;
		ph45_blk[ph45_nblk].live = 1;
		ph45_nblk++;
	}
	return p;
}

static void ph45_pl_free(void *q)
{
	unsigned char *p = (unsigned char *)q;
	unsigned i;

	for (i = 0; i < ph45_nblk; i++) {
		if (ph45_blk[i].p == p) {
			if (ph45_blk[i].live) {
				ph45_blk[i].live = 0;
				ph45_n_free++;
			} else {
				ph45_n_dfree++;
			}
			return;
		}
	}
	ph45_n_wfree++;
}

static uint64_t ph45_live_at_end(void)
{
	uint64_t n = 0;
	unsigned i;
	for (i = 0; i < ph45_nblk; i++)
		n += (uint64_t)(ph45_blk[i].live != 0);
	return n;
}

static void ph45_arena_reset(void)
{
	ph45_bump[PH45_LO] = 0;
	ph45_bump[PH45_HI] = 0;
	ph45_nblk = 0;
	ph45_region = PH45_LO;
	ph45_n_alloc = ph45_n_free = ph45_n_dfree = ph45_n_wfree = ph45_bytes = 0;
}

/* ⚠ ONCE, from `main.c`, OUTSIDE the measured region.  Also the row's
 * `mbstring.c:764` -- `__mbfl_allocators = &_php_mb_allocators;` -- which is
 * where PHP binds the same table to `emalloc`/`efree` at MINIT. */
static mbfl_allocators ph45_allocators;

void ph45_arena_init(void)
{
	if (ph45_base[PH45_LO] != NULL)
		return;
	ph45_allocators.malloc = ph45_pl_malloc;
	ph45_allocators.free = ph45_pl_free;
	__mbfl_allocators = &ph45_allocators;             /* mbstring.c:764 */

	ph45_base[PH45_LO] = (unsigned char *)mmap(
		NULL, PH45_REGION_BYTES, PROT_READ | PROT_WRITE,
		MAP_PRIVATE | MAP_ANONYMOUS | MAP_32BIT, -1, 0);
	/* ⚠ EXIT 9, LOUDLY, rather than degrading.  A row whose LO region were not
	 * below 2^32, or whose HI region were not exactly 2^32 above it, would
	 * still RUN and would still print a `u64` -- a different one, for a reason
	 * no gate stage could name.  Both mappings succeeded in 8 of 8 build
	 * configurations on this box; if that ever stops being true the row must
	 * stop, not adapt. */
	if (ph45_base[PH45_LO] == MAP_FAILED
	    || (uintptr_t)ph45_base[PH45_LO] >= 0x80000000ULL)
		exit(9);
	/* ⚠⚠ `LO + 2^32` IS NOT ALWAYS AVAILABLE, AND ASan IS WHY. AddressSanitizer
	 * maps its shadow over `[0x7fff8000, 0x10007fff7fff]` on x86-64, which
	 * swallows EVERY address of the form `LO + k*2^32` for `LO < 2^31` and
	 * `k` up to ~4096 -- so a row that insisted on `k == 1` exited 9 on all
	 * eight inputs of BOTH sanitizer builds, which is exactly what this row's
	 * first gate run reported.
	 * ⭐ THE ROW DOES NOT NEED `k == 1`. It needs `(int)HI == (int)LO`, and
	 * that holds for ANY multiple of 2^32. So search upward for the first `k`
	 * whose page is free: under ASan that is the first address past the shadow,
	 * and under an ordinary build it is `k == 1`. The search is deterministic
	 * given the process layout, it happens ONCE outside the measured loop, and
	 * nothing the row measures depends on which `k` won -- `NOTES.md` §9. */
	{
		unsigned long long k;
		ph45_base[PH45_HI] = NULL;
		for (k = 1; k <= 131072ULL; k++) {
			unsigned char *want = ph45_base[PH45_LO] + (k << 32);
			unsigned char *got = (unsigned char *)mmap(
				want, PH45_REGION_BYTES, PROT_READ | PROT_WRITE,
				MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE, -1, 0);
			if (got == want) {
				ph45_base[PH45_HI] = got;
				break;
			}
			if (got != MAP_FAILED)
				munmap(got, PH45_REGION_BYTES);
		}
		if (ph45_base[PH45_HI] == NULL
		    || (unsigned)(uintptr_t)ph45_base[PH45_HI]
		       != (unsigned)(uintptr_t)ph45_base[PH45_LO])
			exit(9);
	}
	ph45_arena_reset();
}

#endif /* PH45_ARENA_H */
