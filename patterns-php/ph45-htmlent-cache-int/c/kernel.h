#ifndef PH45_KERNEL_H
#define PH45_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph45: run PHP 5.0.0's HTML-ENTITIES -> wchar decode filter over a window of
 * text, through TWO live filters, and fold what they emitted into a u64.
 *
 *   window = [u32 place][u32 order][ text bytes ... ]
 *   place  = place_w & 3   -- bit 0 is filter A's heap region, bit 1 is B's
 *   order  = order_w & 1   -- which filter is destroyed first
 *   text   = win + 8 .. win + len, fed ALTERNATELY: even bytes to A, odd to B
 *
 *   mbfl_convert_filter_new  x2               <- mbfl_convert.c:216-258
 *     -> mbfl_filt_conv_html_dec_ctor         <- mbfilter_htmlent.c:158-162
 *   for each byte: mbfl_filt_conv_html_dec    <- mbfilter_htmlent.c:174-242
 *   mbfl_filt_conv_html_dec_flush x2          <- mbfilter_htmlent.c:244-257
 *   mbfl_convert_filter_delete x2             <- mbfl_convert.c:260-266
 *     -> mbfl_filt_conv_html_dec_dtor         <- mbfilter_htmlent.c:164-172
 *   fold (the emitted wchars, the emit count, and the arena's five counters),
 *   xor `php_shim_tally()`.
 *
 * Contract in ../spec.md.  Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0, narrowed.  THE BUG (CRASH-123).
 *   c/kernel_hardened.c   R1h -- the same file plus `e8901dc17087` WHOLE:
 *                                `void *opaque;` added to
 *                                `struct _mbfl_convert_filter`, and every
 *                                `filter->cache` in the decode half moved onto
 *                                it (Moriyoshi Koizumi, 2005-02-21, "- Fix bug
 *                                #30573 (compiler warning due to invalid type
 *                                cast)").  First shipped in php-5.0.4; still in
 *                                master, 21 years on, with only
 *                                `mbfl_malloc` -> `emalloc` since.
 *
 * ============================================================================
 * ⚠⚠⚠ THE DEFECT IS A TYPE, NOT A BOUND
 * ============================================================================
 * `mbfl_convert.h:49` declares `int cache;` -- 32 bits -- and
 * `mbfilter_htmlent.c:161` stores a HEAP POINTER in it:
 *
 *     filter->cache = (int)mbfl_malloc(html_enc_buffer_size+1);   :161  STORE
 *     char *buffer  = (char*)filter->cache;                       :178  BACK
 *     buffer[0] = '&';                                            :183  WRITE
 *     buffer = (char*)filter->cache;                              :249  BACK
 *     mbfl_free((void*)filter->cache);                            :169  FREE
 *
 * ⚠ The catalogue says "five lines, two functions".  It is FIFTEEN tarball
 * lines across FOUR functions (`_034` §2.1): the declaration, the store, the
 * free, TWO casts back and TEN dereferences -- `:183 :189 :190 :193 :202 :215
 * :216 :223 :230 :236 :253`.  `:249` is one of the four sites the patch
 * rewrites, and a row built to the catalogue's five would not lift it.
 *
 * `corpus invariant pointer-value-integrity` -- the only one of 166 rows with
 * its own -- carries three obligations that map ONE-TO-ONE onto three of those
 * lines: O1 the store (`:161`), O2 the read-back-and-deref (`:178`/`:249`),
 * O3 the free of a value the allocator never returned (`:169`).
 *
 * ⚠⚠ AND THE DEFECT IS NOT INPUT-CONDITIONED.  `:167`'s `if (filter->cache)`
 * is true for every non-zero truncation, so `:169`'s free runs on EVERY filter
 * destruction whether or not the input contains an `&`.  On a 2026 PIE heap
 * that is 60 SIGSEGVs in 60 runs on the string `"hello, world"` (`_034` §5.4).
 * **The row's placed arena (`c/arena.h`) exists to make the BENIGN case work,
 * not the adversarial one.**  Read `c/arena.h`'s header before anything else
 * here.
 *
 * ⚠⚠ ON THE `LO` PLACEMENT R1 AND R1h ARE BIT-IDENTICAL, AND THAT IS CORRECT.
 * `(char*)(int)p == p` exactly, so the measured `u64` carries NO evidence that
 * the defect exists -- it is `check.py` stage 7h's requirement being SATISFIED.
 * The evidence lives in `inputs/adversarial-*.bin` (where stage 4 RECORDS
 * per-rung behaviour) and in `controls/`.  This is `ph64`'s lesson repeating on
 * a second row and ../NOTES.md §5 says so.
 *
 * The kernel does NOT take `buf_len`.  The caller guarantees
 * `off + len <= buf_len` and `16 <= len <= 268435456`; that is the structural
 * precondition every rung shares and no rung checks (R5 proves it at the call
 * site instead).  Every byte of the window past the two head words is attacker
 * data and is the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

/* Maps the two arena regions.  ⚠ Called ONCE, from `main.c`, BEFORE the
 * measured driver loop -- a per-call `mmap` would put a syscall inside the
 * marginal-`Ir` subtraction (`_034` §6.3(3)).  Exits 9 if either mapping does
 * not land where the row needs it; see `c/arena.h`. */
void ph45_arena_init(void);

#endif /* PH45_KERNEL_H */
