/* ⚠ `_GNU_SOURCE` MUST BE LINE 1, BEFORE ANY HEADER.  `harness/build.py` passes
 * `-std=c99`, which defines `__STRICT_ANSI__`, and glibc's <features.h> then
 * hides BOTH `MAP_32BIT` and `MAP_FIXED_NOREPLACE`.  Every libc header pulls
 * <features.h> in, so this cannot move below one.  Verified under all eight
 * {gcc,clang} x {-O0,-O3} x {-DSLB_ISOLATED,-flto} combinations. */
#define _GNU_SOURCE

/* ph45 rung R1h -- `c/kernel.c` PLUS `e8901dc17087` AND NOTHING ELSE.
 *
 *   `diff c/kernel.c c/kernel_hardened.c` is the commit, and only the commit:
 *   one added struct member and five `filter->cache` -> `filter->opaque`
 *   rewrites, plus this header and the comments that name them.
 *
 *   e8901dc17087075645dc867a9b6d7d534673482b
 *   Moriyoshi Koizumi <moriyoshi@php.net>, Mon 21 Feb 2005 10:12:43 +0000
 *   "- Fix bug #30573 (compiler warning due to invalid type cast)"
 *   2 files, 8 insertions, 7 deletions.  `patch -p1` onto the PRISTINE 5.0.0
 *   tarball: rc=0, NO FUZZ, NO OFFSET -- the commit's pre-image IS 5.0.0.
 *   Absent at php-5.0.0/.1/.2/.3, present at php-5.0.4 and at every tag through
 *   master, 21 years, never reverted; the only later change is
 *   `mbfl_malloc` -> `emalloc`.  Patch bytes: `controls/e8901dc17087.patch`.
 *
 * ⚠⚠ THE SUBJECT LINE IS NOT EVIDENCE ABOUT WHAT THE COMMIT DOES.  It calls
 * this a compiler-warning fix; the patch CHANGES THE STORAGE.  It does not cast
 * at the use site and it does not silence anything: it adds `void *opaque;` to
 * `struct _mbfl_convert_filter` and moves every decode-half use of
 * `filter->cache` onto it, so the truncation is REMOVED.  ⭐ And the sharper
 * reading is that there is no "warning fix vs real fix" distinction to draw
 * here at all: `-Wpointer-to-int-cast` and `-Wint-to-pointer-cast` fire at
 * exactly the four sites the patch rewrites, so the warning and the
 * memory-safety defect are the SAME EVENT.  `controls/warnings.py` measures it.
 *
 * ⚠ `int cache;` STAYS.  The commit does not touch `mbfl_convert.h:49` -- 26
 * other filters use `cache` as a genuine integer accumulator and it is still an
 * `int` in master.  The fix gives the POINTER a pointer-typed home instead.
 *
 * ⚠ ONE OF THE COMMIT'S SIX `mbfilter_htmlent.c` REWRITES IS OUT OF THIS ROW'S
 * SCOPE: `:148`, `filter->cache = 0` in `mbfl_filt_conv_html_enc_flush`, is in
 * the ENCODE half, which this row must not lift (`c/kernel.c`'s ⛔ note).  The
 * five that are in scope -- `:161`, `:167`, `:169`, `:178`, `:249` -- are all
 * here.  The `mbfl_convert.h` hunk is here too.
 *
 * The rest of this file is `c/kernel.c` verbatim, including its provenance.
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
 * WHAT `e8901dc17087` CHANGES, AND WHAT IT LEAVES ALONE
 * ============================================================================
 *   * `int cache;` IS STILL THERE and is still an `int`.  The fix does not
 *     widen the field; it stops using it for a pointer.
 *   * the three `(char*)` / `(void*)` casts at `:169`, `:178` and `:249` are
 *     still written, and are now casts FROM A `void *` -- which is exactly why
 *     they stop being casts of a different size and why the four gcc warnings
 *     go to zero (`controls/warnings.py`).
 *   * `mbfl_filt_conv_html_dec_dtor`'s free is still UNCONDITIONAL on a
 *     non-NULL value -- `if (filter->opaque)` guards NULL and nothing else.
 *     The fix does not add a check; it makes the value trustworthy.
 *   * `_dec_flush`'s own read at `:249` is rewritten too, and it is the site
 *     the catalogue's five lines miss.
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
	void *opaque;                  /* + e8901dc17087, mbfl_convert.h @@ -51,6 +51,7 @@ */
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

/* ================= mbfilter_htmlent.c:158-162, PATCHED ===================
 * ⭐ O1 IS DISCHARGED BY TYPING.  `mbfl_malloc` returns `void *`, `opaque` is
 * `void *`, and there is no conversion step to lose anything -- so
 * `pointer-value-integrity` holds here for the same reason it holds in every
 * other filter: nobody ever narrowed the value.  gcc's `-Wpointer-to-int-cast`
 * at this line goes away with the truncation, which is the whole of bug
 * #30573. */
static void mbfl_filt_conv_html_dec_ctor(mbfl_convert_filter *filter)
{
	filter->status = 0;
	filter->opaque = mbfl_malloc(html_enc_buffer_size+1);
}

/* ================= mbfilter_htmlent.c:164-172, PATCHED ===================
 * ⭐ O3 IS DISCHARGED.  `:169` now frees the value `mbfl_malloc` returned, on
 * every placement and for every input -- so `n_dfree`, `n_wfree` and the leak
 * count are ZERO in both regions, where R1's are not.  ⚠ Note the GUARD is
 * unchanged: `if (filter->opaque)` still rejects only the null case.  The fix
 * is entirely in the type. */
static void mbfl_filt_conv_html_dec_dtor(mbfl_convert_filter *filter)
{
	filter->status = 0;
	if (filter->opaque)
	{
		mbfl_free((void*)filter->opaque);
	}
	filter->opaque = NULL;
}

/* ================= mbfilter_htmlent.c:174-242, PATCHED ===================
 * ⭐ O2 IS DISCHARGED AT `:178`.  `(char*)filter->opaque` is a pointer-to-
 * pointer conversion, so the ten dereferences below -- `:183 :189 :190 :193
 * :202 :215 :216 :223 :230 :236` -- land inside the 17 bytes `mbfl_malloc`
 * returned, at either placement.  `:183` is the corpus's cited faulting frame
 * and this rung does not fault there on any input.
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
	char *buffer = (char*)filter->opaque;

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

/* ================= mbfilter_htmlent.c:244-257, PATCHED ===================
 * ⚠⚠ `:249` IS CAST-BACK #2 AND IT IS CITED NOWHERE -- not by `index.csv`, not
 * by `CATALOGUE.md`, not by `ADJUDICATION_001.md`.  It is nevertheless one of
 * the four sites this commit rewrites, which is why a row built to the
 * catalogue's five lines would not be a faithful PRE-IMAGE for its own R1h:
 * the patch would not apply to it. */
static int mbfl_filt_conv_html_dec_flush(mbfl_convert_filter *filter)
{
	int status, pos = 0;
	char *buffer;

	buffer = (char*)filter->opaque;
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
