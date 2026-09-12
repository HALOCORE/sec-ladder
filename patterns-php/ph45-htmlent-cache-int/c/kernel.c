/* ⚠ `_GNU_SOURCE` MUST BE LINE 1, BEFORE ANY HEADER.  `harness/build.py` passes
 * `-std=c99`, which defines `__STRICT_ANSI__`, and glibc's <features.h> then
 * hides BOTH `MAP_32BIT` and `MAP_FIXED_NOREPLACE`.  Every libc header pulls
 * <features.h> in, so this cannot move below one.  Verified under all eight
 * {gcc,clang} x {-O0,-O3} x {-DSLB_ISOLATED,-flto} combinations. */
#define _GNU_SOURCE

/* ph45 rung R1 -- PHP 5.0.0's HTML-ENTITIES decode filter, NARROWED.
 * THE BUG (corpus row CRASH-123 / V5C-123, bug #30573).
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/filters/\
 *       mbfilter_htmlent.c | sed -n '155,258p'
 *   -> sha256 6aad722d2b6cf73ec987a7ced3bf590ac04821454eb52377edfcdf1c7acaf8b9
 *   plus ELEVEN more spans, every one pinned in ../spec.md's
 *   `provenance.extra_spans` and hashed the same way:
 *     mbfl/mbfl_convert.h      :40-54    <- `int cache;` IS THE DEFECT, :49
 *     filters/html_entities.h  :33-36    filters/html_entities.c  :37-290
 *     mbfl/mbfl_allocators.h   :36-54    ext/mbstring/mbstring.c  :240-283 :762-765
 *     mbfl/mbfl_convert.c      :216-256  :259-266  :299-317
 *     mbfl/mbfilter.c          :243-271  filters/mbfilter_htmlent.c :85-91
 *
 *   Tier `narrowed`.  The four decode functions at `[155,258]` lift CHARACTER
 *   FOR CHARACTER -- nothing is deleted from any body.  What forces `narrowed`
 *   rather than `verbatim` is that `mbfl_malloc`'s table entry is rebound at an
 *   allocator whose RETURNED ADDRESS the row chooses, and the returned address
 *   IS the mechanism, so that substitution's `why` cannot end in "no
 *   semantics"; plus two wrappers come off (`mbfl_buffer_converter_feed`'s
 *   memory device and `mbfl_convert_filter_new`'s vtable dispatch), which is
 *   §A1's definition of `narrowed`.  Every divergence is itemised in
 *   ../spec.md's `provenance.divergences`, individually, with a line citation.
 *
 * ⛔ THE ENCODE HALF OF THIS FILE IS DELIBERATELY NOT LIFTED.
 * `mbfilter_htmlent.c:101` declares `int tmp[64]` and `:123` is
 * `int *p = tmp + sizeof(tmp);` -- `tmp + 256`, i.e. 192 `int`s past the end --
 * and `:129` writes through `--p`.  That is a SEPARATE, UNCATALOGUED stack OOB
 * write, fixed in the php-5.0.3 -> php-5.0.4 window by a DIFFERENT commit that
 * nobody has identified.  Lifting `:99-150` would put a second memory-safety
 * defect inside a row whose contract names one.  `../NOTES.md` §12.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE
 * ============================================================================
 * A 64-bit heap pointer is stored into a 32-bit `int` field, read back out
 * through `(char*)` -- which SIGN-EXTENDS -- and then dereferenced ten times
 * and freed.  `c/kernel.h` has the five lines and the map onto the corpus
 * invariant's three obligations; `c/arena.h` has why the row must place its
 * work buffer at all.
 *
 * ============================================================================
 * WHAT NARROWING REMOVED, AND WHY ALL BUT ONE OF IT IS SEMANTICS-FREE
 * ============================================================================
 * 1. ⚠⚠ `mbfl_malloc`'s TABLE ENTRY -> `ph45_pl_malloc`, a PLACED arena.
 *    This one is a `projection` and its `why` CANNOT end in "no semantics":
 *    the address it returns is the whole mechanism.  `c/arena.h`.
 * 2. The other five `mbfl_allocators` entries (`realloc`, `calloc`, `pmalloc`,
 *    `prealloc`, `pfree`) are NULL: unreachable from the decode path.
 * 3. `mbfl_convert_filter_new`'s vtable dispatch (`mbfl_convert.c:252`,
 *    `mbfl_convert_filter_reset_vtbl`).  The kernel is compiled for ONE
 *    conversion, `HTML-ENTITIES -> wchar`, whose vtbl is the compile-time
 *    constant `vtbl_html_wchar` (`mbfilter_htmlent.c:85-91`).
 * 4. The FILTER STRUCT comes from `php_shim_emalloc` rather than from
 *    `mbfl_malloc`, so the row's placement projection is confined to the
 *    17-byte work buffer -- which is the only allocation the defect reads.
 *    `mbfl_convert.c:226` really is `mbfl_malloc(sizeof(mbfl_convert_filter))`
 *    upstream; `common-php/emalloc_shim.h` IS 5.0.0's own `_emalloc`/`_efree`,
 *    so this is the FAITHFUL half and the arena is the projected half.
 * 5. `mbfl_buffer_converter_feed`'s `mbfl_memory_device_realloc` and its
 *    `mbfl_filter_output_pipe` output function (`mbfilter.c:255`, `:263`) ->
 *    the fold.  The FEED LOOP itself (`mbfilter.c:262-267`) is kept: it IS the
 *    driver loop shape, `while (n > 0) { (*filter_function)(*p++, filter); n--; }`.
 * 6. `mbfl_no2encoding`, `mbfl_encoding_pass` and the `from`/`to` lookup
 *    (`mbfl_convert.c:232-239`).  All 13 struct members are kept and
 *    `mbfl_encoding` is forward-declared, so the STRUCT is unchanged and its
 *    `int cache;` sits exactly where 5.0.0 puts it.
 * 7. `TSRMLS_*`.  Thread plumbing.
 *
 * ============================================================================
 * WHAT IS *NOT* CHANGED, AND MUST NOT BE
 * ============================================================================
 *   * `filter->cache` stays an `int` and the three casts stay exactly as
 *     written.  Giving the buffer a pointer-typed home IS `e8901dc17087`, i.e.
 *     R1h; a rung that did it would be R1h wearing R1's name.  ../spec.md's
 *     `forbidden` pins `void *opaque` absent from this file.
 *   * `mbfl_filt_conv_html_dec_dtor`'s free is UNCONDITIONAL on the truncated
 *     value -- `if (filter->cache)` guards zero and nothing else.
 *   * `_dec_flush` reads the buffer through its OWN cast at `:249`.  That is
 *     the site the catalogue's five lines miss.
 *   * the `while (entity->name)` linear scan and `strcmp(buffer+1, ...)`.  The
 *     scan reads a C STRING out of the wild buffer; it is one of the ten
 *     dereferences and it is unbounded in a way indexing is not.
 */
#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

#include "arena.h"                 /* the placed arena AND mbfl_allocators */
#include "mbfl__html_entities.h"   /* html_entities.{h,c}, 251 entries */

struct mbfl_encoding;              /* forward-declared: see narrowing note 6 */

/* ======================= mbfl_convert.h:40-54 ============================
 * ⚠⚠⚠ `:49 int cache;` IS THE DEFECT.  All 13 members are lifted; the field's
 * offset and width are exactly 5.0.0's.  `e8901dc17087` does NOT remove it --
 * 26 other filters use `cache` as a genuine integer accumulator, and it is
 * still an `int` in master today.  The fix ADDS `void *opaque;` after `:53`.
 */
typedef struct _mbfl_convert_filter mbfl_convert_filter;

struct _mbfl_convert_filter {
	void (*filter_ctor)(mbfl_convert_filter *filter);
	void (*filter_dtor)(mbfl_convert_filter *filter);
	int (*filter_function)(int c, mbfl_convert_filter *filter);
	int (*filter_flush)(mbfl_convert_filter *filter);
	int (*output_function)(int c, void *data);
	int (*flush_function)(void *data);
	void *data;
	int status;
	int cache;                     /* <== :49  THE FIELD.  32 bits. */
	const struct mbfl_encoding *from;
	const struct mbfl_encoding *to;
	int illegal_mode;
	int illegal_substchar;
};

/* ⚠⚠ THE LAYOUT IS LOAD-BEARING AND IT IS ASSERTED, NOT COMMENTED.  The row is
 * about a field NARROWER THAN A POINTER; if `int` ever stopped being 4 bytes,
 * or a pointer 8, the row would measure something else and say nothing about
 * it. */
typedef char ph45_layout_assert[
	(sizeof(int) == 4 && sizeof(void *) == 8
	 && sizeof(((mbfl_convert_filter *)0)->cache) == 4) ? 1 : -1];

/* ====================== mbfilter_htmlent.c:94 ============================ */
#define CK(statement)	do { if ((statement) < 0) return (-1); } while (0)

/* ========================================================================= */
/* The projected output device and the per-call state.  All of it is reset by
 * `ph45_reset()` at the top of every kernel call, beside `php_shim_reset()` and
 * `ph45_arena_reset()` (PROTOCOL_PHP.md B1 rule 3). */
static uint64_t ph45_out;         /* the fold of every emitted wchar, in order */
static uint64_t ph45_emitted;

static void ph45_reset(void)
{
	ph45_out = 0;
	ph45_emitted = 0;
}

/* PROJECTS `mbfl_filter_output_pipe` (mbfilter.c:263's `output_function`).
 * Upstream the wchars go into an `mbfl_memory_device`; here they go into the
 * `u64` the gate compares across rungs. */
static int ph45_output(int c, void *data)
{
	(void)data;
	ph45_out = ph45_out * 31u + (uint64_t)(uint32_t)c;
	ph45_emitted++;
	return 0;
}

static uint32_t ph45_rd32(const uint8_t *p)
{
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8)
	     | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

/* ====================== mbfilter_htmlent.c:155-156 ======================= */
#define html_enc_buffer_size	16
static const char html_entity_chars[] = "#0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

static int mbfl_filt_conv_html_dec_flush(mbfl_convert_filter *filter);

/* ====================== mbfilter_htmlent.c:158-162 =======================
 * ⚠⚠⚠ `:161` IS THE TRUNCATING STORE -- obligation O1 of the corpus's
 * `pointer-value-integrity` invariant.  gcc says so, at `-Wall -Wextra`:
 * `warning: cast from pointer to integer of different size
 * [-Wpointer-to-int-cast]`.  That warning IS bug #30573, and `e8901dc17087`'s
 * subject line is that warning.  `controls/warnings.py` counts them. */
static void mbfl_filt_conv_html_dec_ctor(mbfl_convert_filter *filter)
{
	filter->status = 0;
	filter->cache = (int)mbfl_malloc(html_enc_buffer_size+1);
}

/* ====================== mbfilter_htmlent.c:164-172 =======================
 * ⚠⚠⚠ `:169` IS THE WILD FREE -- obligation O3.  `if (filter->cache)` at
 * `:167` rejects only the value ZERO, so on any heap above 2^32 this hands the
 * deallocator a value it never returned, ON EVERY FILTER DESTRUCTION, for ANY
 * input.  That is why this row has no benign corpus without `c/arena.h`. */
static void mbfl_filt_conv_html_dec_dtor(mbfl_convert_filter *filter)
{
	filter->status = 0;
	if (filter->cache)
	{
		mbfl_free((void*)filter->cache);
	}
	filter->cache = 0;
}

/* ====================== mbfilter_htmlent.c:174-242 =======================
 * ⚠⚠⚠ `:178` IS CAST-BACK #1 -- obligation O2 -- and it SIGN-EXTENDS: a
 * truncation with bit 31 set comes back as `0xFFFFFFFF_xxxxxxxx`, i.e. kernel
 * space, while one with bit 31 clear comes back as a low address that is
 * unmapped in a PIE process.  BOTH regimes fault, for different reasons, and
 * both were measured faulting (`_034` §5.3).
 * `:183` is the corpus's cited faulting frame: `SEGV ... WRITE`, frame #0
 * `mbfl_filt_conv_html_dec`.
 *
 * ⚠ `:193`'s `ent = ent*10 + (buffer[pos] - '0')` is a SIGNED OVERFLOW on any
 * entity of the form `&#` followed by more than ~9 non-digit body characters --
 * `html_entity_chars` admits letters, so `&#abcdefghijkl;` reaches ~7.4e12.
 * That is a SECOND, UNCATALOGUED defect in this function; it is REPORTED, NOT
 * PURSUED (`../NOTES.md` §12), and `inputs/gen.py` asserts no shipped window
 * reaches it on EITHER rung so that the row's numbers are not taken over it. */
static int mbfl_filt_conv_html_dec(int c, mbfl_convert_filter *filter)
{
	int  pos, ent = 0;
	mbfl_html_entity_entry *entity;
	char *buffer = (char*)filter->cache;

	if (!filter->status) {
		if (c == '&' ) {
			filter->status = 1;
			buffer[0] = '&';
		} else {
			CK((*filter->output_function)(c, filter->data));
		}
	} else {
		if (c == ';') {
			buffer[filter->status] = 0;
			if (buffer[1]=='#') {
				/* numeric entity */
				for (pos=2; pos<filter->status; pos++) {
					ent = ent*10 + (buffer[pos] - '0');
				}
				CK((*filter->output_function)(ent, filter->data));
				filter->status = 0;
				/*php_error_docref("ref.mbstring" TSRMLS_CC, E_NOTICE, "mbstring decoded '%s'=%d", buffer, ent);*/
			} else {
				/* named entity */
			        entity = (mbfl_html_entity_entry *)mbfl_html_entity_list;
				while (entity->name) {
					if (!strcmp(buffer+1, entity->name))	{
						ent = entity->code;
						break;
					}
					entity++;
				}
				if (ent) {
					/* decoded */
					CK((*filter->output_function)(ent, filter->data));
					filter->status = 0;
					/*php_error_docref("ref.mbstring" TSRMLS_CC, E_NOTICE,"mbstring decoded '%s'=%d", buffer, ent);*/
				} else {
					/* failure */
					buffer[filter->status++] = ';';
					buffer[filter->status] = 0;
					/* php_error_docref("ref.mbstring" TSRMLS_CC, E_WARNING, "mbstring cannot decode '%s'", buffer); */
					mbfl_filt_conv_html_dec_flush(filter);
				}
			}
		} else {
			/* add character */
			buffer[filter->status++] = c;
			/* add character and check */
			if (!strchr(html_entity_chars, c) || filter->status+1==html_enc_buffer_size || (c=='#' && filter->status>2))
			{
				/* illegal character or end of buffer */
				if (c=='&')
					filter->status--;
				buffer[filter->status] = 0;
				/* php_error_docref("ref.mbstring" TSRMLS_CC, E_WARNING, "mbstring cannot decode '%s'", buffer)l */
				mbfl_filt_conv_html_dec_flush(filter);
				if (c=='&')
				{
					filter->status = 1;
					buffer[0] = '&';
				}
			}
		}
	}
	return c;
}

/* ====================== mbfilter_htmlent.c:244-257 =======================
 * ⚠⚠ `:249` IS CAST-BACK #2, AND IT IS CITED NOWHERE -- not by `index.csv`,
 * not by `CATALOGUE.md`, not by `ADJUDICATION_001.md`.  It is one of the four
 * sites `e8901dc17087` rewrites, so a row built to the catalogue's five lines
 * would not be a faithful pre-image for its own R1h. */
static int mbfl_filt_conv_html_dec_flush(mbfl_convert_filter *filter)
{
	int status, pos = 0;
	char *buffer;

	buffer = (char*)filter->cache;
	status = filter->status;
	/* flush fragments */
	while (status--) {
		CK((*filter->output_function)(buffer[pos++], filter->data));
	}
	filter->status = 0;
	/*filter->buffer = 0; of cause NOT*/
	return 0;
}

/* ====================== mbfl_convert.c:216-258 ===========================
 * NARROWED: the `mbfl_no2encoding` lookup and `mbfl_convert_filter_reset_vtbl`
 * come off (narrowing notes 3 and 6), and the struct itself comes from
 * `php_shim_emalloc` (note 4).  `region` selects which heap the CTOR's
 * `mbfl_malloc` serves -- see `c/arena.h` on why that is allocator state and
 * not a parameter. */
static mbfl_convert_filter *mbfl_convert_filter_new(int region)
{
	mbfl_convert_filter * filter;

	/* allocate */
	filter = (mbfl_convert_filter *)php_shim_emalloc(sizeof(mbfl_convert_filter));
	if (filter == NULL) {
		return NULL;
	}

	filter->from = NULL;
	filter->to = NULL;
	filter->output_function = ph45_output;
	filter->flush_function = NULL;
	filter->data = NULL;
	filter->illegal_mode = 1;                 /* ILLEGAL_MODE_CHAR, :248 */
	filter->illegal_substchar = 0x3f;         /* '?'                 :249 */

	/* the function table -- `vtbl_html_wchar`, mbfilter_htmlent.c:85-91 */
	filter->filter_ctor = mbfl_filt_conv_html_dec_ctor;
	filter->filter_dtor = mbfl_filt_conv_html_dec_dtor;
	filter->filter_function = mbfl_filt_conv_html_dec;
	filter->filter_flush = mbfl_filt_conv_html_dec_flush;

	/* constructor */
	ph45_region = region;
	(*filter->filter_ctor)(filter);           /* :255 */

	return filter;
}

/* ====================== mbfl_convert.c:260-266 =========================== */
static void mbfl_convert_filter_delete(mbfl_convert_filter *filter)
{
	if (filter) {
		(*filter->filter_dtor)(filter);
		php_shim_efree((void *)filter);       /* :265 mbfl_free((void*)filter) */
	}
}

/* ========================================================================= */
/* The benchmark wrapper.  It plays the part of one `mb_convert_encoding($s,
 * 'UTF-8', 'HTML-ENTITIES')` over two live converters, which is what
 * `mbfl_strimwidth` and `mbfl_convert_encoding`'s length-detection loop really
 * do (`mbfilter.c:1309-1331`, `:1434-1539`).
 *
 * `php_shim_reset()` at the top is PROTOCOL_PHP.md B1 rule 3.  `php_shim_tally()`
 * at the bottom is B1 rule 2 -- but on THIS row the allocator half of the
 * oracle is the ARENA's five counters, because the work buffer is what the
 * defect reads and the shim serves only the two filter structs. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
	const uint8_t *win = buf + off;
	const uint8_t *text;
	size_t ntext, i;
	uint32_t place, order;
	mbfl_convert_filter *fa, *fb, *f;
	uint64_t acc;

	php_shim_reset();
	ph45_arena_reset();
	ph45_reset();

	place = ph45_rd32(win + 0) & 3u;
	order = ph45_rd32(win + 4) & 1u;
	text  = win + 8;
	ntext = len - 8;

	fa = mbfl_convert_filter_new((int)(place & 1u));
	fb = mbfl_convert_filter_new((int)((place >> 1) & 1u));

	/* `mbfl_buffer_converter_feed`, mbfilter.c:262-267, over two converters.
	 * ⚠ The vtable dispatch is gone (narrowing note 3) but the LOOP is the
	 * upstream one: one byte at a time, no look-ahead, no length passed to the
	 * filter.  Handing the filter a bound would be modelling a different bug. */
	for (i = 0; i < ntext; i++) {
		f = (i & 1u) ? fb : fa;
		if ((*f->filter_function)((int)text[i], f) < 0)
			break;
	}
	(*fa->filter_flush)(fa);
	(*fb->filter_flush)(fb);

	acc = ph45_out;
	acc = acc * 31u + ph45_emitted;

	if (order) {
		mbfl_convert_filter_delete(fb);
		mbfl_convert_filter_delete(fa);
	} else {
		mbfl_convert_filter_delete(fa);
		mbfl_convert_filter_delete(fb);
	}

	/* the arena's five counters -- `n_free`, `n_dfree`, `n_wfree` and the leak
	 * are O3's evidence, and they are the half of the oracle that moves on the
	 * HI placement while the emitted fold moves on the ALIASING one. */
	acc = acc * 31u + ph45_n_alloc;
	acc = acc * 31u + ph45_n_free;
	acc = acc * 31u + ph45_n_dfree;
	acc = acc * 31u + ph45_n_wfree;
	acc = acc * 31u + ph45_live_at_end();
	acc = acc * 31u + ph45_bytes;

	/* ⚠⚠ THE SHIM'S THREE *COUNT* FIELDS, AND DELIBERATELY NOT ITS BYTE TOTAL.
	 * `PROTOCOL_PHP.md` §B1 rule 2 says fold `php_shim_tally()`, which mixes
	 * `n_alloc`, `n_free`, `n_cache_hit` AND `bytes_mallocked`.  On THIS row the
	 * last of those is a property of `sizeof(mbfl_convert_filter)` -- and
	 * `e8901dc17087` legitimately GROWS that struct by 8 bytes (88 -> 96) when
	 * it adds `void *opaque;`.  Folding it would make R1h differ from R1 on
	 * EVERY benign input for a reason that has nothing to do with the defect,
	 * and `check.py` stage 7h would refuse the row -- CORRECTLY.  ⭐ A gate stage
	 * that refuses your row is a hypothesis about your row
	 * (`.memory-php/02-ladder.md`), and the hypothesis is right: a `u64` that
	 * moves with `sizeof` is not measuring this defect.
	 * The three counts are folded, they are `2 / 2 / 0` on every call of every
	 * rung, and the row's real allocator oracle is `c/arena.h`'s five counters
	 * above -- which are about the 17-byte WORK BUFFER, i.e. the one allocation
	 * the defect reads.  The 88-vs-96 measurement is `../NOTES.md` §8; it is a
	 * genuine cost of the upstream fix and the row REPORTS it rather than
	 * burying it in a number nobody can decompose. */
	acc = acc * 31u + php_shim_ag.n_alloc;
	acc = acc * 31u + php_shim_ag.n_free;
	acc = acc * 31u + php_shim_ag.n_cache_hit;

	return acc;
}
