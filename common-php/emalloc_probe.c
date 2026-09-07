/* emalloc_probe.c -- the evidence that `emalloc_shim.h` reproduces PHP
 * 5.0.0's allocator truncations, WITH POSITIVE CONTROLS.
 *
 * TASK_PHP_002 §2 test T6. A green run is evidence about the CHECK, not about
 * the world, so every arm below states what would make it fail and every
 * finding has a control that must ALSO fire.
 *
 *   cc -O1 -Wall -Wextra -I common-php common-php/emalloc_probe.c \
 *      common-php/emalloc_shim.c -o .temp/php0/emalloc_probe
 *   .temp/php0/emalloc_probe            # the truncation arms, no sanitizer
 *   .temp/php0/emalloc_probe uaf-cached # deliberate UAF on a CACHED block
 *   .temp/php0/emalloc_probe uaf-plain  # deliberate UAF on an UNCACHED block
 *   .temp/php0/emalloc_probe overflow   # deliberate write past a T1 block
 *
 * ⚠ THE LAST THREE MUST BE RUN UNDER ASan, AND `env -u LD_PRELOAD` IS NOT
 * OPTIONAL ON THIS BOX. The shell inherits
 * `LD_PRELOAD=/usr/libexec/coreutils/libstdbuf.so`; a dynamically linked ASan
 * binary refuses to start behind it AND STILL EXITS 1, so an exit-code check
 * cannot tell "blind" from "found nothing". Grep for `AddressSanitizer`, never
 * for `ASan`. (`PLAN_PHP.md` §7 rule 14.)
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

#include "emalloc_shim.h"

static int failures;
static int checks;

static void ck(const char *name, int ok, const char *detail)
{
    checks++;
    if (!ok)
        failures++;
    printf("  %-4s %-46s %s\n", ok ? "ok" : "FAIL", name, detail ? detail : "");
}

/* A truncation-FREE allocator with otherwise identical arithmetic. This is
 * the control that separates "the truncation did it" from "overcommit did
 * it": the same request through this must FAIL. */
static void *honest_alloc(size_t size)
{
    size_t real = (size + 7) & ~(size_t)0x7;   /* no 32-bit store */
    return malloc(sizeof(php_shim_mem_header) + PHP_SHIM_HEADER_PADDING + real);
}

/* ---------------------------------------------------------------- T1 ---- */
/* THE HEADLINE: an 18-exabyte request becomes a ~2 GiB allocation that
 * SUCCEEDS, because `zend_alloc.c:129`'s `real_size` is `unsigned int`.
 *
 * WHAT WOULD MAKE THIS FAIL: if `real_size` were `size_t`, `malloc` would be
 * asked for 18 EiB and return NULL, and arm (a) would print FAIL. If the box
 * simply could not give us 2 GiB, (a) would also FAIL -- which is why (c)
 * exists and must NOT be reachable by the same accident. */
static void t1_truncation(void)
{
    /* 0xFFFFFFFF80000000 = 18446744071562067968 = 18.45 exabytes.
     * (size+7)&~7 = 0xFFFFFFFF80000000; stored in 32 bits -> 0x80000000. */
    const size_t req = 0xFFFFFFFF80000000ULL;
    unsigned int rs = php_shim_real_size(req);
    char buf[160];
    void *p;

    puts("T1  zend_alloc.c:129/:135 -- `unsigned int real_size`");
    snprintf(buf, sizeof buf,
             "request %" PRIu64 " B (%.2f EB) -> real_size %u B (%.2f GiB)",
             (uint64_t)req, (double)req / 1e18, rs, rs / 1073741824.0);
    ck("a) the 64-bit request truncates to 2 GiB", rs == 0x80000000u, buf);

    p = php_shim_emalloc(req);
    ck("b) ... and the allocation SUCCEEDS", p != NULL,
       p ? "emalloc returned non-NULL for an 18-EB request" : "emalloc gave NULL");

    if (p) {
        /* Prove the 2 GiB is really there: touch both ends. If only a
         * placeholder had been returned this would segfault. */
        volatile char *c = (volatile char *)p;
        c[0] = 'A';
        c[(size_t)rs - 1] = 'Z';
        ck("c) ... and 2 GiB of it is really mapped",
           c[0] == 'A' && c[(size_t)rs - 1] == 'Z',
           "wrote and read back byte 0 and byte real_size-1");
        php_shim_efree(p);
    } else {
        ck("c) ... and 2 GiB of it is really mapped", 0, "skipped: (b) failed");
    }

    /* POSITIVE CONTROL, and it MUST fire. Same request, no 32-bit store. */
    p = honest_alloc(req);
    snprintf(buf, sizeof buf, "malloc(%" PRIu64 ") returned %s",
             (uint64_t)req, p ? "NON-NULL -- CONTROL DID NOT FIRE" : "NULL");
    ck("CONTROL: without the truncation it FAILS", p == NULL, buf);
    free(p);
}

/* ---------------------------------------------------------------- T2 ---- */
/* The SECOND truncation, `zend_alloc.h:53`'s `unsigned int size:31`, has a
 * DIFFERENT MODULUS from T1 (2^31 vs 2^32). At the request above they
 * disagree maximally: T1 says 2 GiB, T2 records 0.
 *
 * WHAT WOULD MAKE THIS FAIL: declaring the field `size_t`, or `unsigned int
 * size` without `:31` -- either makes `recorded` equal 0x80000000 and (a)
 * prints FAIL. */
static void t2_bitfield(void)
{
    const size_t req = 0xFFFFFFFF80000000ULL;
    void *p;
    char buf[160];

    puts("T2  zend_alloc.h:53 -- `unsigned int size:31`");
    p = php_shim_emalloc(req);
    if (!p) {
        ck("a) the recorded size truncates to 31 bits", 0, "emalloc failed");
        return;
    }
    {
        unsigned int recorded = php_shim_recorded_size(p);
        snprintf(buf, sizeof buf,
                 "T1 real_size = %u, T2 recorded size = %u -- DIFFERENT FIELDS",
                 php_shim_real_size(req), recorded);
        ck("a) recorded size is (size & 0x7fffffff) = 0", recorded == 0u, buf);
    }
    php_shim_efree(p);

    /* A request where the two truncations disagree by a readable amount:
     * 4 GiB + 24 bytes. T1 -> 24 (a 24-byte block!), T2 -> 24. */
    p = php_shim_emalloc(0x100000018ULL);
    if (p) {
        snprintf(buf, sizeof buf,
                 "emalloc(0x100000018 = 4 GiB + 24) -> real_size %u B",
                 php_shim_real_size(0x100000018ULL));
        ck("b) a 4-GiB request allocates 24 bytes",
           php_shim_real_size(0x100000018ULL) == 24u, buf);
        php_shim_efree(p);
    } else {
        ck("b) a 4-GiB request allocates 24 bytes", 0, "emalloc failed");
    }

    /* CONTROL: a small, ordinary request must record itself EXACTLY. If T2
     * mangled every size the arms above would be vacuous. */
    p = php_shim_emalloc(40);
    if (p) {
        unsigned int recorded = php_shim_recorded_size(p);
        snprintf(buf, sizeof buf, "emalloc(40) records %u", recorded);
        ck("CONTROL: an in-range size records exactly", recorded == 40u, buf);
        php_shim_efree(p);
    } else {
        ck("CONTROL: an in-range size records exactly", 0, "emalloc failed");
    }
}

/* ---------------------------------------------------------------- T3 ---- */
/* `zend_alloc.c:295  int final_size = size*nmemb;` -- SIGNED 32-bit. Not in
 * PLAN_PHP.md §4.3; found at TASK_PHP_002.
 *
 * WHAT WOULD MAKE THIS FAIL: `size_t final_size` -- then `_ecalloc` would ask
 * for the full product and get NULL. */
static void t3_ecalloc(void)
{
    /* 0x40000000 * 4 = 0x100000000 -> int 0. ecalloc of a 4 GiB array
     * allocates the header and nothing else, then memsets 0 bytes. */
    void *p;
    char buf[160];
    puts("T3  zend_alloc.c:295 -- `int final_size = size*nmemb`");
    p = php_shim_ecalloc(0x40000000ULL, 4);
    snprintf(buf, sizeof buf,
             "ecalloc(0x40000000, 4) = 4 GiB requested, final_size = %d",
             (int)(0x40000000ULL * 4));
    ck("a) a 4-GiB ecalloc succeeds with 0 bytes", p != NULL, buf);
    if (p) {
        ck("b) ... and records 0", php_shim_recorded_size(p) == 0u, "");
        php_shim_efree(p);
    }
    /* CONTROL: an ordinary ecalloc must actually allocate and zero. */
    p = php_shim_ecalloc(8, 8);
    if (p) {
        int zeroed = 1, i;
        for (i = 0; i < 64; i++)
            if (((char *)p)[i] != 0)
                zeroed = 0;
        ck("CONTROL: ecalloc(8,8) allocates 64 zeroed bytes",
           zeroed && php_shim_recorded_size(p) == 64u, "");
        php_shim_efree(p);
    } else {
        ck("CONTROL: ecalloc(8,8) allocates 64 zeroed bytes", 0, "ecalloc NULL");
    }
}

/* ------------------------------------------------------- safe_emalloc ---- */
/* `_safe_emalloc` checks in 64-bit `long` (zend_alloc.c:224-237) and then
 * calls the truncating `_emalloc` (:238), so it protects against neither T1
 * nor T2.
 *
 * WHAT WOULD MAKE THIS FAIL: if `_safe_emalloc` clamped to UINT_MAX, or
 * called a non-truncating allocator, (a) would return NULL. */
static void t_safe_emalloc(void)
{
    void *p;
    char buf[160];
    puts("SE  zend_alloc.c:221-244 -- `_safe_emalloc` protects against neither");
    /* 0x20000000 * 8 + 0 = 0x100000000 -- passes every LONG_MAX test, then
     * truncates to 0 inside _emalloc. */
    p = php_shim_safe_emalloc(0x20000000ULL, 8, 0);
    snprintf(buf, sizeof buf,
             "safe_emalloc(0x20000000, 8, 0) = 4 GiB, real_size %u",
             php_shim_real_size(0x100000000ULL));
    ck("a) 4 GiB passes the 64-bit guard, then truncates",
       p != NULL && php_shim_real_size(0x100000000ULL) == 0u, buf);
    if (p)
        php_shim_efree(p);

    /* CONTROL: the guard is not dead -- a product that really overflows
     * `long` MUST be refused. */
    p = php_shim_safe_emalloc((size_t)1 << 62, 8, 0);
    ck("CONTROL: a true 64-bit overflow IS refused", p == NULL,
       p ? "safe_emalloc returned NON-NULL -- CONTROL DID NOT FIRE"
         : "safe_emalloc returned NULL as PHP's E_ERROR path does");
    free(p);
}

/* ------------------------------------------------------------- cache ---- */
/* zend_alloc.c:150-168 / :263-279 -- the size-class cache. This is why
 * `crashes_pristine_5_0_0 = False` is not evidence of absence
 * (PLAN_PHP.md §4.3, RECAP_PHP F3).
 *
 * WHAT WOULD MAKE THIS FAIL: dropping the cache and calling free() in
 * `php_shim_efree` -- then (b) would almost certainly still pass by glibc
 * tcache accident, which is why (a) checks the COUNTER and not just the
 * pointer, and why (c) uses a class the cache cannot hold. */
static void t_cache(void)
{
    void *a, *b, *c, *d;
    char buf[160];
    puts("CA  zend_alloc.c:150-168,:263-279 -- the size-class cache");

    php_shim_reset();
    a = php_shim_emalloc(24);
    php_shim_efree(a);
    b = php_shim_emalloc(24);
    snprintf(buf, sizeof buf,
             "n_cache_push=%" PRIu64 " n_cache_hit=%" PRIu64 " same ptr=%s",
             php_shim_ag.n_cache_push, php_shim_ag.n_cache_hit,
             a == b ? "yes" : "NO");
    ck("a) a freed 24-byte block is CACHED, not freed",
       php_shim_ag.n_cache_push == 1 && php_shim_ag.n_cache_hit == 1 && a == b,
       buf);

    /* real_size 96 -> cache_index 12 >= MAX_CACHED_MEMORY(11): not cacheable.
     * CONTROL: the cache has a ceiling and it is the one PHP declares. */
    php_shim_reset();
    c = php_shim_emalloc(96);
    php_shim_efree(c);
    d = php_shim_emalloc(96);
    snprintf(buf, sizeof buf,
             "real_size %u -> cache_index %u >= %d; n_cache_push=%" PRIu64,
             php_shim_real_size(96), php_shim_real_size(96) >> 3,
             PHP_SHIM_MAX_CACHED_MEMORY, php_shim_ag.n_cache_push);
    ck("CONTROL: a 96-byte block is NOT cached (index 12 >= 11)",
       php_shim_ag.n_cache_push == 0 && php_shim_ag.n_cache_hit == 0, buf);
    php_shim_efree(d);

    /* The boundary, both sides, so the ceiling is measured and not asserted:
     * real_size 80 -> index 10 (cached); real_size 88 -> index 11 (not). */
    php_shim_reset();
    a = php_shim_emalloc(80);
    php_shim_efree(a);
    ck("b) the LAST cached class is real_size 80 (index 10)",
       php_shim_ag.n_cache_push == 1, "");
    php_shim_reset();
    a = php_shim_emalloc(88);
    php_shim_efree(a);
    ck("c) the FIRST uncached class is real_size 88 (index 11)",
       php_shim_ag.n_cache_push == 0, "");
    php_shim_reset();
}

/* ------------------------------------------------ deliberate-fault arms -- */
/* Each of these is a MUST-FIRE ASan control. If ASan is silent on `uaf-plain`
 * or `overflow`, ASan is blind and every other ASan result in this programme
 * is worthless. `uaf-cached` is the FINDING: the same bug, silent, because
 * PHP's own allocator handed the block straight back. */
static int arm_uaf_cached(void)
{
    char *p = (char *)php_shim_emalloc(24);   /* real_size 24, index 3 */
    php_shim_efree(p);                        /* -> cache, NOT free() */
    p[0] = 'X';                               /* USE AFTER FREE */
    printf("uaf-cached: wrote '%c' to a freed block; n_cache_push=%" PRIu64 "\n",
           p[0], php_shim_ag.n_cache_push);
    return 0;
}

static int arm_uaf_plain(void)
{
    char *p = (char *)php_shim_emalloc(96);   /* real_size 96, index 12 */
    php_shim_efree(p);                        /* -> real free() */
    p[0] = 'X';                               /* USE AFTER FREE */
    printf("uaf-plain: wrote '%c' to a freed block; n_cache_push=%" PRIu64 "\n",
           p[0], php_shim_ag.n_cache_push);
    return 0;
}

static int arm_overflow(void)
{
    /* T1: a 4 GiB + 24 request allocates 24 bytes. Writing the 25th is a
     * heap-buffer-overflow, and it is exactly the shape of the real defect. */
    char *p = (char *)php_shim_emalloc(0x100000018ULL);
    memset(p, 'X', 4096);
    printf("overflow: memset 4096 into a %u-byte block\n",
           php_shim_real_size(0x100000018ULL));
    return 0;
}

int main(int argc, char **argv)
{
    if (argc > 1 && !strcmp(argv[1], "uaf-cached"))
        return arm_uaf_cached();
    if (argc > 1 && !strcmp(argv[1], "uaf-plain"))
        return arm_uaf_plain();
    if (argc > 1 && !strcmp(argv[1], "overflow"))
        return arm_overflow();

    printf("php-5.0.0 emalloc shim probe -- sizeof(header)=%zu padding=%zu\n\n",
           sizeof(php_shim_mem_header), (size_t)PHP_SHIM_HEADER_PADDING);
    php_shim_reset();
    t1_truncation();
    putchar('\n');
    t2_bitfield();
    putchar('\n');
    t3_ecalloc();
    putchar('\n');
    t_safe_emalloc();
    putchar('\n');
    t_cache();
    printf("\n%d checks, %d FAILED\n", checks, failures);
    return failures != 0;
}
