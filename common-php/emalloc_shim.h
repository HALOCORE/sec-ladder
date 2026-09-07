/* emalloc_shim.h -- a FAITHFUL model of PHP 5.0.0's Zend allocator.
 *
 * ============================================================================
 * WHY THIS FILE EXISTS  (PLAN_PHP.md §4.3)
 * ============================================================================
 * A substituted allocator is NOT neutral. An earlier effort dropped plain
 * `malloc` in where `emalloc` was, and as a direct result reported a REAL
 * defect as unreachable and then INVENTED an explanation for the upstream fix.
 * Any php row that allocates links this header, or says in its `spec.md` why
 * not.
 *
 * ============================================================================
 * PROVENANCE -- every line below is cited against the PRISTINE MUSEUM TARBALL
 * ============================================================================
 *   php-5.0.0.tar.gz
 *   sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919
 *   read   tar -xzOf <tarball> php-5.0.0/Zend/zend_alloc.c | sed -n 'a,bp'
 *
 * ⚠ NOT against any extracted tree on this box. ⚠⚠ THIS PARAGRAPH USED TO SAY
 * *"`.app-tests/...` and `.temp/san_tests/...` carry modern-gcc AND ALLOCATOR
 * patches -- specifically `REAL_SIZE(size) -> (size)`, which deletes the very
 * truncation this file exists to reproduce"*. BOTH HALVES WERE FALSE. Measured
 * at TASK_PHP_004 over every `php-5.0.0/Zend/zend_alloc.c` on this box
 * (`.temp/php4/trees_500.txt`, 12 trees):
 *
 *     8 of 12   BYTE-IDENTICAL to the pristine tarball (sha256 fb4215f19dc2e68c)
 *               -- including ALL THREE `.app-tests/.temp/oracle/` trees
 *     2 of 12   ZEND_DISABLE_MEMORY_CACHE 0 -> 1 at :40 and :43   (`-nocache`,
 *               `-nocache-asan`)  <- the CONSEQUENTIAL one: it turns off the
 *               size-class cache this file models, and it is the control the
 *               63.5 % figure is derived from
 *     1 of 12   the above PLUS `REAL_SIZE(size) -> (size)` at :132 (NOT :135)
 *               (`-nocache-detect-asan`)
 *     1 of 12   ASAN_{UN,}POISON_MEMORY_REGION annotations at :35-41, :162,
 *               :284 (`-poison-asan`)
 *
 * ⚠ AND `REAL_SIZE(size) -> (size)` DOES NOT DELETE THE TRUNCATION. `real_size`
 * is still `unsigned int` (:129) and `real_size = REAL_SIZE(size)` (:135) still
 * truncates mod 2^32; all the patch removes is the round-up-to-8, so ASan's
 * redzone starts at the requested size. For `emalloc_probe.c:61`'s 18.45 EB
 * request both spellings give real_size = 2147483648 (measured,
 * `.temp/php4/real_size_probe.c`). ⚠ That equality is VALUE-DEPENDENT, not
 * general: at SIZE_MAX they give 0 and 4294967295 -- still both truncating.
 *
 * ✅ THE RULE SURVIVES AND IS UNCHANGED: cite the tarball, never a tree. A
 * corpus where SOME trees are patched is one where you cannot tell by looking
 * which tree you are in, and `build/php-4.0.2/` (the 13th tree, out of scope
 * under `DP-06`) really does carry modern-gcc patches. Only the stated reason
 * was wrong. (`patterns-php/SOURCES.md`; TASK_PHP_003 M3, TASK_PHP_004 §2.7.)
 *
 * ============================================================================
 * THE THREE TRUNCATIONS, AND THEY ARE DISTINCT
 * ============================================================================
 * T1  zend_alloc.c:128-130  `DECLARE_CACHE_VARS()` declares
 *         unsigned int real_size;
 *     and zend_alloc.c:134-136 assigns into it
 *         real_size = REAL_SIZE(size);          <- size is size_t (64-bit)
 *     zend_alloc.c:132        #define REAL_SIZE(size) ((size+7) & ~0x7)
 *     The rounding is done in `size_t` and the result is STORED IN 32 BITS.
 *     zend_alloc.c:182 then allocates `... + SIZE + ...` where `SIZE` is
 *     `real_size` (zend_alloc.c:138), so an 18-exabyte request becomes a
 *     ~2 GiB allocation that SUCCEEDS.
 *
 * T2  zend_alloc.h:53        unsigned int size:31;
 *     The *recorded* size is a 31-BIT BITFIELD -- a different modulus from T1
 *     (2^31, not 2^32) and a different field. zend_alloc.c:167 and :201 do
 *         p->size = size;                       <- size is size_t
 *     so the block's own idea of how big it is truncates AGAIN, and
 *     DIFFERENTLY. Found by TASK_PHP_001's spatial miner; manager-verified.
 *
 * T3  zend_alloc.c:295       int final_size = size*nmemb;
 *     `_ecalloc` multiplies two `size_t` and stores the product in a SIGNED
 *     32-bit `int`, then `_emalloc(final_size)` at :298 and `memset(p, 0,
 *     final_size)` at :303. This is a third, signed truncation, on a different
 *     path, and it is NOT mentioned in `PLAN_PHP.md` §4.3 -- found while
 *     writing this file (TASK_PHP_002). A negative `final_size` sign-extends
 *     to a huge `size_t` in the `_emalloc` call and to a huge `size_t` in the
 *     `memset` length.
 *
 * ⚠ `_safe_emalloc` (zend_alloc.c:221-244) PROTECTS AGAINST NONE OF THEM.
 * It checks `nmemb`, `size` and `offset` against `LONG_MAX` in 64-bit `long`
 * (:224-229, :236-237) and then, at :238, calls
 *     emalloc_rel(lval + offset)
 * which is `_emalloc` -- so a value that passes the 64-bit check is handed
 * straight to T1. A shim that models only `_safe_emalloc` is not faithful.
 *
 * ============================================================================
 * THE SIZE-CLASS CACHE -- the reason `crashes_pristine_5_0_0 = False` is not
 * evidence of absence (PLAN_PHP.md §4.3, RECAP_PHP F3)
 * ============================================================================
 * zend_alloc.c:40-44 defines ZEND_DISABLE_MEMORY_CACHE as 0 in BOTH `#ifdef
 * ZEND_MM` arms, so the cache is unconditionally ON.
 * (⚠ `PLAN_PHP.md` §4.3 cites this as `zend_alloc.c:39-43`; measured against
 * the pristine tarball it is **:40-44**. One-line correction, TASK_PHP_002.)
 *
 *   _efree  (zend_alloc.c:263, :270-279) recomputes the cache index FROM THE
 *           31-BIT RECORDED SIZE and, if it fits, pushes the block onto a
 *           per-size-class LIFO stack and RETURNS WITHOUT CALLING free().
 *   _emalloc(zend_alloc.c:150-168) pops that same block back on the next
 *           request in the same class.
 *
 * MAX_CACHED_MEMORY 11 and MAX_CACHED_ENTRIES 256 (zend_alloc.h:63-64), and
 * `cache_index = real_size >> 3` (zend_alloc.c:136), so every allocation with
 * `real_size <= 87` is cached. `san_tests/REPORT.md` §2 measures 63.5 % of
 * PHP's heap traffic never reaching `malloc` because of this.
 *
 * ⚠⚠ CONSEQUENCE FOR EVERY TEMPORAL ROW: a use-after-free under this
 * allocator is a use of a block that is STILL MAPPED and will be HANDED BACK
 * VERBATIM to the next same-class request. It does not segfault; it type-
 * confuses. A C kernel on plain malloc/free reproduces MORE crashes than
 * pristine PHP does, which is why `crashes_pristine_5_0_0 = False` must never
 * be used as an admission filter.
 *
 * ============================================================================
 * HOW TO USE IT, AND THE ONE THING THAT WILL BITE YOU
 * ============================================================================
 * ⚠⚠ THIS HEADER IS THE WHOLE SHIM. `harness/build.py:163-165` compiles
 * EXACTLY THREE translation units --
 *     common/driver.c, patterns/<row>/c/<kernel>.c, patterns/<row>/c/main.c
 * -- and nothing else, ever. A `common-php/emalloc_shim.c` COULD NOT BE
 * LINKED without editing `build.py`, which costs a 33-pattern re-measure
 * (`PLAN_PHP.md` §2.1). So the implementation is `static inline` here, and
 * the sibling `emalloc_shim.c` is a standalone-probe TU only. Measured, not
 * assumed: TASK_PHP_002 §4.
 *
 * Exactly ONE translation unit must define the mutable state:
 *
 *     #define PHP_SHIM_IMPL
 *     #include "emalloc_shim.h"          // in c/kernel.c
 *
 *     #include "emalloc_shim.h"          // everywhere else
 *
 * `-I common-php` is already on the compile line (`build.py:167`), so the
 * bare `#include "emalloc_shim.h"` resolves with no per-row plumbing.
 *
 * ⚠ CALL `php_shim_reset()` AT THE TOP OF EVERY KERNEL CALL. The driver loop
 * runs the kernel thousands of times; a cache that survives across calls makes
 * call N's behaviour depend on call N-1 and destroys the marginal-Ir
 * subtraction the whole measurement rests on (`.memory/03-measurement.md`).
 *
 * ⚠ FOLD THE TALLY INTO THE CHECKSUM. `php_shim_tally()` mixes
 * (n_alloc, n_free, n_cache_hit, BYTES_MALLOCKED) into one u64 so the defect
 * lands in the kernel's `u64` and not only in a sanitizer (`PLAN_PHP.md`
 * §4.3). ⚠⚠ THE FOURTH FIELD IS `bytes_mallocked` -- WHAT REACHED `malloc`,
 * i.e. the sum of the TRUNCATED `real_size` -- NOT `bytes_requested`. This
 * comment said `bytes_requested_low` until TASK_PHP_004 (TASK_PHP_003 m4) and
 * the two are exactly the two sides of truncation T1: they differ by precisely
 * the amount a truncation defect moves, so a row that folded the wrong one in
 * on the strength of this comment would have folded in the quantity that does
 * NOT move. Both are readable from `php_shim_ag` if a row wants the pair.
 *
 * ============================================================================
 * WHAT IS DELIBERATELY NOT MODELLED
 * ============================================================================
 *   - ZEND_DEBUG (zend_alloc.c:60-65, :153-165, :202-213): magic words, the
 *     filename/lineno fields, `memset(ptr, 0x5a, p->size)` on free. The
 *     shipped 5.0.0 build is NOT a debug build; modelling it would ADD a
 *     poison-on-free that pristine PHP does not do, which is the §4.2
 *     "invented non-defect" failure in the other direction.
 *   - MEMORY_LIMIT (zend_alloc.c:68-99, :176-181): a configured ceiling, not
 *     a memory-safety mechanism. A row that needs it must say so.
 *   - ZTS / TSRMLS_* (zend_alloc.c:146, :254-261): thread plumbing, no
 *     semantics. This is a `deletions` entry in every row's `provenance`.
 *   - ZEND_MM (zend_alloc.c:46-49): the sub-allocator. The `#else` arm at
 *     :54-57 is plain malloc/free and is what this models. A row whose defect
 *     is INSIDE zend_mm must say so and cannot use this shim.
 *   - the pNext/pLast block list (zend_alloc.h:50-51, guarded by
 *     `ZEND_DEBUG || !defined(ZEND_MM)`): the list is present in the arm this
 *     models, and its two pointers ARE in the header size below, because the
 *     header size is what shifts the payload address.
 */

#ifndef PHP_EMALLOC_SHIM_H
#define PHP_EMALLOC_SHIM_H

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ---- zend_alloc.h:32-35 -- the magic words. Kept as named constants even
 * though ZEND_DEBUG is off, because a row that wants to show a heap-metadata
 * overwrite needs something recognisable to overwrite. */
#define PHP_SHIM_BLOCK_START_MAGIC 0x7312F8DCL
#define PHP_SHIM_BLOCK_END_MAGIC   0x2A8FCC84L
#define PHP_SHIM_BLOCK_FREED_MAGIC 0x99954317L
#define PHP_SHIM_BLOCK_CACHED_MAGIC 0xFB8277DCL

/* ---- zend_alloc.h:63-65 */
#define PHP_SHIM_MAX_CACHED_MEMORY 11
#define PHP_SHIM_MAX_CACHED_ENTRIES 256

/* ---- zend_alloc.h:37-55  `zend_mem_header`, the `!ZEND_DEBUG && !ZEND_MM`
 * projection. ⚠ `size:31` at :53 IS TRUNCATION T2 and is reproduced exactly;
 * do not "fix" it to `size_t`. */
typedef struct php_shim_mem_header {
    struct php_shim_mem_header *pNext;  /* zend_alloc.h:50 */
    struct php_shim_mem_header *pLast;  /* zend_alloc.h:51 */
    unsigned int size : 31;             /* zend_alloc.h:53  <-- T2 */
    unsigned int cached : 1;            /* zend_alloc.h:54 */
} php_shim_mem_header;

typedef union php_shim_align_test {     /* zend_alloc.h:57-61 */
    void *ptr;
    double dbl;
    long lng;
} php_shim_align_test;

/* ---- zend_alloc.h:67-73 */
#define PHP_SHIM_PLATFORM_ALIGNMENT (__alignof__(php_shim_align_test))
#define PHP_SHIM_HEADER_PADDING                                               \
    (((PHP_SHIM_PLATFORM_ALIGNMENT - sizeof(php_shim_mem_header))             \
      % PHP_SHIM_PLATFORM_ALIGNMENT + PHP_SHIM_PLATFORM_ALIGNMENT)            \
     % PHP_SHIM_PLATFORM_ALIGNMENT)

/* ---- zend_alloc.c:132  the rounding, and it is done in size_t */
#define PHP_SHIM_REAL_SIZE(size) (((size) + 7) & ~(size_t)0x7)

/* ---- zend_alloc.c:60-65.  END_MAGIC_SIZE is 0 in a non-debug build. */
#define PHP_SHIM_END_MAGIC_SIZE 0

/* The per-"globals" state.  zend_globals.h holds `cache`, `cache_count` and
 * `head` inside `zend_alloc_globals`; here it is one struct so a row can
 * reset it between driver iterations. */
typedef struct php_shim_state {
    php_shim_mem_header *cache[PHP_SHIM_MAX_CACHED_MEMORY]
                              [PHP_SHIM_MAX_CACHED_ENTRIES];
    unsigned int cache_count[PHP_SHIM_MAX_CACHED_MEMORY];
    php_shim_mem_header *head;          /* AG(head), zend_alloc.c:103-126 */
    /* --- instrumentation. NOT part of PHP; it is how the defect reaches the
     * kernel's u64 rather than only a sanitizer (PLAN_PHP.md §4.3). --- */
    uint64_t n_alloc;
    uint64_t n_free;
    uint64_t n_cache_hit;
    uint64_t n_cache_push;
    uint64_t bytes_requested;           /* sum of the UNTRUNCATED size_t */
    uint64_t bytes_mallocked;           /* sum of what actually reached malloc */
} php_shim_state;

#ifdef PHP_SHIM_IMPL
php_shim_state php_shim_ag;
#else
extern php_shim_state php_shim_ag;
#endif

/* Wipe the cache and the tally. ⚠ Frees every cached block first: without
 * this a long driver loop leaks the whole cache and the run's RSS, not its
 * instruction count, becomes the limit.
 *
 * ⚠⚠ IT DOES **NOT** FREE THE LIVE (`head`) LIST, AND THAT IS DELIBERATE --
 * but it is a second RSS hazard and this comment did not name it until
 * TASK_PHP_004 (TASK_PHP_003 m6). Setting `head = NULL` orphans every
 * still-live block. It cannot free them: a kernel may legitimately hold a
 * pointer across the reset, and freeing it here would MANUFACTURE a
 * use-after-free -- `PLAN_PHP.md` §4.2's invented-defect failure, which is the
 * one thing this file exists to avoid.
 *
 * ⚠ SO A ROW THAT LEAKS ON PURPOSE (the corpus has 15 CWE-401 rows) MUST CALL
 * `php_shim_shutdown()` -- not `php_shim_reset()` -- at the end of every kernel
 * call, or the driver loop's thousands of iterations are bounded by RSS rather
 * than by instruction count, which is exactly the hazard the cache note above
 * exists for, one field over. */
static inline void php_shim_reset(void)
{
    int i;
    unsigned int j;
    for (i = 0; i < PHP_SHIM_MAX_CACHED_MEMORY; i++) {
        for (j = 0; j < php_shim_ag.cache_count[i]; j++)
            free(php_shim_ag.cache[i][j]);
        php_shim_ag.cache_count[i] = 0;
    }
    php_shim_ag.head = NULL;
    php_shim_ag.n_alloc = 0;
    php_shim_ag.n_free = 0;
    php_shim_ag.n_cache_hit = 0;
    php_shim_ag.n_cache_push = 0;
    php_shim_ag.bytes_requested = 0;
    php_shim_ag.bytes_mallocked = 0;
}

/* ---- zend_alloc.c:469-569  `shutdown_memory_manager`, the `!ZEND_DEBUG &&
 * !ZEND_MM` projection. This is PHP's REQUEST BOUNDARY, and it is what a
 * leaking row needs so that the leak is a per-call fact rather than a
 * whole-run RSS climb (see the note on `php_shim_reset`).
 *
 *   :478-496  the cache sweep. ⚠ `for (i=1; ...)` -- PHP starts at ONE, so
 *             cache class 0 (real_size 0..7, i.e. `emalloc(0)`) is never
 *             returned to malloc by shutdown. Reproduced, not "fixed".
 *             :490 REMOVE_POINTER_FROM_LIST(ptr) then :491 ZEND_DO_FREE(ptr).
 *   :529-569  the leak sweep: walk `AG(head)` and free every block whose
 *             `cached` bit is 0, skipping the cached ones (they are already
 *             gone above, and their `cached` bit is what says so).
 *
 * The tally is NOT reset here -- shutdown is a PHP event, `php_shim_reset` is
 * the instrumentation event, and collapsing them would make a row unable to
 * measure a request that shuts down mid-loop. */
static inline void php_shim_shutdown(void)
{
    php_shim_mem_header *p, *t;
    int i;
    unsigned int j;

    for (i = 1; i < PHP_SHIM_MAX_CACHED_MEMORY; i++) {   /* :484  i starts at 1 */
        for (j = 0; j < php_shim_ag.cache_count[i]; j++) {
            php_shim_mem_header *ptr = php_shim_ag.cache[i][j];
            if (ptr == php_shim_ag.head)                 /* :490 */
                php_shim_ag.head = ptr->pNext;
            else if (ptr->pLast)
                ptr->pLast->pNext = ptr->pNext;
            if (ptr->pNext)
                ptr->pNext->pLast = ptr->pLast;
            free(ptr);                                   /* :491 */
        }
        php_shim_ag.cache_count[i] = 0;                  /* :493 */
    }

    t = php_shim_ag.head;                                /* :530-531 */
    while (t) {                                          /* :532 */
        if (!t->cached) {
            p = t->pNext;                                /* :562 */
            if (t == php_shim_ag.head)                   /* :563 */
                php_shim_ag.head = t->pNext;
            else if (t->pLast)
                t->pLast->pNext = t->pNext;
            if (t->pNext)
                t->pNext->pLast = t->pLast;
            free(t);                                     /* :564 */
            t = p;
        } else {
            t = t->pNext;                                /* :567 */
        }
    }
}

/* ---- zend_alloc.c:142-217  `_emalloc`.
 *
 * Faithful, in order:
 *   :145  DECLARE_CACHE_VARS()  -> `unsigned int real_size`      T1 LIVES HERE
 *   :148  CALCULATE_REAL_SIZE_AND_CACHE_INDEX(size)              T1 FIRES HERE
 *   :151  the cache-hit arm
 *   :167  p->size = size                                         T2 FIRES HERE
 *   :182  ZEND_DO_MALLOC(hdr + padding + SIZE + END_MAGIC_SIZE)  T1 IS SPENT HERE
 *   :189  the NULL arm: PHP prints and exit(1)s -- see note below
 *   :201  p->size = size                                         T2 FIRES HERE
 */
static inline void *php_shim_emalloc(size_t size)
{
    php_shim_mem_header *p;
    unsigned int real_size;             /* zend_alloc.c:129   <-- T1 */
    unsigned int cache_index;           /* zend_alloc.c:130 */

    real_size = (unsigned int)PHP_SHIM_REAL_SIZE(size);  /* :135  T1 FIRES */
    cache_index = real_size >> 3;                        /* :136 */

    php_shim_ag.n_alloc++;
    php_shim_ag.bytes_requested += (uint64_t)size;

    /* :150-168 -- ZEND_DISABLE_MEMORY_CACHE is 0 (:40-44), so this arm is
     * always compiled in. */
    if (cache_index < PHP_SHIM_MAX_CACHED_MEMORY
        && php_shim_ag.cache_count[cache_index] > 0) {
        p = php_shim_ag.cache[cache_index]
                            [--php_shim_ag.cache_count[cache_index]];
        p->cached = 0;                                   /* :166 */
        p->size = (unsigned int)size;                    /* :167  T2 FIRES */
        php_shim_ag.n_cache_hit++;
        return (void *)((char *)p + sizeof(php_shim_mem_header)
                        + PHP_SHIM_HEADER_PADDING);      /* :168 */
    }

    /* :182 -- and `SIZE` is `real_size` (:138), NOT `size`. */
    p = (php_shim_mem_header *)malloc(sizeof(php_shim_mem_header)
                                      + PHP_SHIM_HEADER_PADDING
                                      + real_size
                                      + PHP_SHIM_END_MAGIC_SIZE);
    if (!p) {
        /* :189-198.  PHP prints to stderr and exit(1)s. A kernel must not
         * exit -- the driver loop would report a build failure instead of a
         * measurement -- so this returns NULL and the caller decides. THIS IS
         * A DELIBERATE DEVIATION and every row that can reach it must say so
         * in its `provenance.deletions`. */
        return NULL;
    }
    php_shim_ag.bytes_mallocked += (uint64_t)real_size;
    p->cached = 0;                                       /* :199 */
    /* :200 ADD_POINTER_TO_LIST(p) -- zend_alloc.c:117-123 */
    p->pNext = php_shim_ag.head;
    if (php_shim_ag.head)
        php_shim_ag.head->pLast = p;
    php_shim_ag.head = p;
    p->pLast = (php_shim_mem_header *)NULL;
    p->size = (unsigned int)size;                        /* :201  T2 FIRES */
    return (void *)((char *)p + sizeof(php_shim_mem_header)
                    + PHP_SHIM_HEADER_PADDING);          /* :216 */
}

/* ---- zend_alloc.c:248-289  `_efree`.
 *
 * ⚠⚠ :263 `CALCULATE_REAL_SIZE_AND_CACHE_INDEX(p->size)` -- the size that
 * decides whether this block is CACHED OR RETURNED TO malloc is the 31-BIT
 * RECORDED one (T2), not the one that was allocated (T1). That is how the two
 * truncations interact, and it is why they must both be modelled.
 */
static inline void php_shim_efree(void *ptr)
{
    php_shim_mem_header *p;
    unsigned int real_size, cache_index;

    if (!ptr)
        return;                          /* not in PHP; PHP would fault. See
                                          * note in `php_shim_emalloc`. */
    p = (php_shim_mem_header *)((char *)ptr - sizeof(php_shim_mem_header)
                               - PHP_SHIM_HEADER_PADDING);   /* :250 */
    real_size = (unsigned int)PHP_SHIM_REAL_SIZE((size_t)p->size); /* :263 */
    cache_index = real_size >> 3;
    php_shim_ag.n_free++;

    /* :270-279 -- the block is NOT returned to malloc. */
    if (cache_index < PHP_SHIM_MAX_CACHED_MEMORY
        && php_shim_ag.cache_count[cache_index] < PHP_SHIM_MAX_CACHED_ENTRIES) {
        php_shim_ag.cache[cache_index]
                         [php_shim_ag.cache_count[cache_index]++] = p;
        p->cached = 1;                                        /* :273 */
        php_shim_ag.n_cache_push++;
        return;                                               /* :277 */
    }
    /* :281 REMOVE_POINTER_FROM_LIST(p) -- zend_alloc.c:103-111 */
    if (p == php_shim_ag.head)
        php_shim_ag.head = p->pNext;
    else if (p->pLast)
        p->pLast->pNext = p->pNext;
    if (p->pNext)
        p->pNext->pLast = p->pLast;
    free(p);                                                  /* :287 */
}

/* ---- Zend/zend_multiply.h:36-45  `ZEND_SIGNED_MULTIPLY_LONG`, THE `#else`
 * ARM, transcribed character for character.
 *
 * ⚠⚠⚠ THE ARM IS THE WHOLE POINT, AND GETTING IT WRONG IS WHAT TASK_PHP_003
 * FOUND (B2). zend_multiply.h:22 guards the exact `imul`/`adc` spelling with
 *
 *     #if defined(__i386__) && defined(__GNUC__)
 *
 * and on x86-64 `__i386__` IS NOT DEFINED, so PHP 5.0.0 on this machine
 * compiles the `#else` at :34 -- a DOUBLE-PRECISION HEURISTIC, not an exact
 * overflow test. `(double)(a)` rounds a 64-bit operand to 53 bits, so for
 * products at or above 2^53 the reconstructed `__dres` can miss `__lres` by
 * more than half an ulp and the test reports overflow on a product that did
 * not overflow.
 *
 * ⚠⚠ THIS IS MODELLED, NOT REPAIRED. The heuristic's INACCURACY IS THE 5.0.0
 * BEHAVIOUR: PHP raises `E_ERROR` on those inputs and returns 0. A shim that
 * used an exact test (`__builtin_mul_overflow`, which is what this file did
 * until TASK_PHP_004) allocates where PHP refuses, and a row at a
 * `safe_emalloc` call site would then show a reachable truncation that
 * pristine PHP's guard actually rejects -- `PLAN_PHP.md` §4.3's own
 * invented-defect failure mode, inside the file written to prevent it.
 * MEASURED: 84,523 disagreements in 20 M samples, 100 % in that direction
 * (TASK_PHP_003; reproduced exactly at TASK_PHP_004,
 * `.temp/php4/mul_probe.c`, which now reports 0 for this spelling on
 * gcc/clang x O0/O3 x {-DSLB_ISOLATED,-flto} and keeps firing on the
 * `__builtin_mul_overflow` control).
 *
 * ⚠ OPERAND TYPE IS PART OF THE PREDICATE. `_safe_emalloc` (:234) invokes the
 * macro on `nmemb` and `size`, which are `size_t`, so `(a)*(b)` is a WRAPPING
 * unsigned 64-bit multiply narrowed to `long`, not a signed overflow. Passing
 * `long` here would be undefined behaviour at exactly the inputs the row is
 * about. Do not "simplify" the parameter types.
 */
#define PHP_SHIM_SIGNED_MULTIPLY_LONG(a, b, lval, dval, usedval) do {         \
    long   __lres  = (a) * (b);                                               \
    double __dres  = (double)(a) * (double)(b);                               \
    double __delta = (double) __lres - __dres;                                \
    if ( ((usedval) = (( __dres + __delta ) != __dres))) {                    \
        (dval) = __dres;                                                      \
    } else {                                                                  \
        (lval) = __lres;                                                      \
    }                                                                         \
} while (0)

/* ---- zend_alloc.c:221-244  `_safe_emalloc`.
 *
 * ⚠ THE POINT OF SHIPPING THIS AT ALL is that it is NOT safe. The 64-bit
 * guard at :224-237 passes, and :238 then hands the value to `_emalloc`,
 * which truncates it (T1). The guard's own multiply is the heuristic above.
 */
static inline void *php_shim_safe_emalloc(size_t nmemb, size_t size,
                                          size_t offset)
{
    /* :224-229. `nmemb >= 0` etc. are vacuous on an unsigned type in the
     * original too -- gcc warns on them; that is a property of PHP, not of
     * this file, so the comparisons are kept and the vacuity is stated. */
    if (nmemb < (size_t)__LONG_MAX__ && size < (size_t)__LONG_MAX__
        && offset < (size_t)__LONG_MAX__) {
        long lval = 0;
        double dval = 0;
        int use_dval;
        /* :234. ⚠ `nmemb`/`size` go in as `size_t`, exactly as PHP passes
         * them; see the macro's note on operand type. */
        PHP_SHIM_SIGNED_MULTIPLY_LONG(nmemb, size, lval, dval, use_dval);
        (void)dval;   /* PHP sets `dval` and never reads it either (:231) */
        /* :236-237. `LONG_MAX - offset` is a size_t subtraction in the
         * original (`offset` is size_t), and `lval + offset` at :238 is a
         * size_t addition -- so neither can overflow a signed long here. */
        if (!use_dval && lval < (long)((size_t)__LONG_MAX__ - offset))
            return php_shim_emalloc((size_t)lval + offset);    /* :238 */
    }
    /* :242-243 -- PHP raises E_ERROR and returns 0. */
    return NULL;
}

/* ---- zend_alloc.c:292-306  `_ecalloc`.
 * ⚠ :295 `int final_size = size*nmemb;` -- TRUNCATION T3, and it is SIGNED. */
static inline void *php_shim_ecalloc(size_t nmemb, size_t size)
{
    void *p;
    int final_size = (int)(size * nmemb);                     /* :295  T3 */
    p = php_shim_emalloc((size_t)final_size);                 /* :298 */
    if (!p)
        return p;                                             /* :299-302 */
    memset(p, 0, (size_t)final_size);                         /* :303 */
    return p;
}

/* ---- zend_alloc.c:309-371  `_erealloc`.
 * :335 truncates via the same `real_size` (T1); :367 `p->size = size` (T2). */
static inline void *php_shim_erealloc(void *ptr, size_t size)
{
    php_shim_mem_header *p, *orig;
    unsigned int real_size;

    if (!ptr)
        return php_shim_emalloc(size);                        /* :316-318 */
    p = orig = (php_shim_mem_header *)((char *)ptr
                                       - sizeof(php_shim_mem_header)
                                       - PHP_SHIM_HEADER_PADDING);  /* :320 */
    real_size = (unsigned int)PHP_SHIM_REAL_SIZE(size);       /* :335  T1 */
    /* :344 REMOVE_POINTER_FROM_LIST(p) */
    if (p == php_shim_ag.head)
        php_shim_ag.head = p->pNext;
    else if (p->pLast)
        p->pLast->pNext = p->pNext;
    if (p->pNext)
        p->pNext->pLast = p->pLast;
    p = (php_shim_mem_header *)realloc(p, sizeof(php_shim_mem_header)
                                       + PHP_SHIM_HEADER_PADDING
                                       + real_size
                                       + PHP_SHIM_END_MAGIC_SIZE);  /* :345 */
    if (!p) {
        /* :346-358. PHP exit(1)s unless `allow_failure`; see the note in
         * `php_shim_emalloc`. */
        p = orig;
        p->pNext = php_shim_ag.head;
        if (php_shim_ag.head)
            php_shim_ag.head->pLast = p;
        php_shim_ag.head = p;
        p->pLast = NULL;
        return NULL;
    }
    /* :359 ADD_POINTER_TO_LIST(p) */
    p->pNext = php_shim_ag.head;
    if (php_shim_ag.head)
        php_shim_ag.head->pLast = p;
    php_shim_ag.head = p;
    p->pLast = NULL;
    p->size = (unsigned int)size;                             /* :367  T2 */
    return (void *)((char *)p + sizeof(php_shim_mem_header)
                    + PHP_SHIM_HEADER_PADDING);               /* :370 */
}

/* ---- zend_alloc.c:392-405  `_estrndup`.  `uint length` is itself a 32-bit
 * parameter in the original, which is a FOURTH narrowing at the API boundary;
 * `length+1` then wraps to 0 at UINT_MAX. */
static inline char *php_shim_estrndup(const char *s, unsigned int length)
{
    char *p = (char *)php_shim_emalloc((size_t)(length + 1u));  /* :397 */
    if (!p)
        return NULL;
    memcpy(p, s, length);
    p[length] = 0;
    return p;
}

/* ---- the instrumentation hook.
 * One u64 that changes if the allocation behaviour changes, so a row can fold
 * it into its checksum and the defect lands in the number the gate compares
 * across rungs, not only in a sanitizer. Deliberately NOT a hash: the mixing
 * is cheap, order-independent per field, and each field is recoverable by a
 * reader who has the other three. */
static inline uint64_t php_shim_tally(void)
{
    return (php_shim_ag.n_alloc * 1000003u)
         ^ (php_shim_ag.n_free * 1000033u)
         ^ (php_shim_ag.n_cache_hit * 1000037u)
         ^ (php_shim_ag.bytes_mallocked * 1000039u);
}

/* Read the RECORDED (31-bit, T2-truncated) size of a live block. A row that
 * wants to show the two truncations disagreeing needs this. */
static inline unsigned int php_shim_recorded_size(void *ptr)
{
    php_shim_mem_header *p =
        (php_shim_mem_header *)((char *)ptr - sizeof(php_shim_mem_header)
                                - PHP_SHIM_HEADER_PADDING);
    return p->size;
}

/* What T1 turned the request into. Not a PHP function -- PHP recomputes it at
 * each site -- but every probe needs it and re-deriving it per row is how a
 * shim drifts from its citation. */
static inline unsigned int php_shim_real_size(size_t size)
{
    return (unsigned int)PHP_SHIM_REAL_SIZE(size);
}

#endif /* PHP_EMALLOC_SHIM_H */
