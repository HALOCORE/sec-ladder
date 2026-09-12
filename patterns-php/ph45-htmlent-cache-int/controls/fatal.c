/* ph45 control -- THE FAITHFUL SPELLING, AND IT IS WHY THE ROW HAS AN ARENA.
 *
 * ⚠⚠ THIS IS NOT A RUNG AND IT IS NOT ON ANY BUILD PATH. `harness/build.py`
 * compiles exactly three translation units and this is none of them; it is
 * built and run by `controls/native.py`.
 *
 * It is `mbfilter_htmlent.c:155-258`'s ctor, dtor and `_dec` with `mbfl_malloc`
 * bound to `common-php/emalloc_shim.h` -- i.e. to PHP 5.0.0's own `_emalloc` --
 * and NO placed arena. That is what PHP really does on a 2026 64-bit box, and
 * it is `PROTOCOL_PHP.md` §A4's fidelity evidence for this row:
 *
 *   corpus, php-5.0.0-fullext + ASan, CRASH-123.php
 *       -> SEGV on unknown address 0x14ba8, WRITE,
 *          #0 mbfl_filt_conv_html_dec ... mbfilter_htmlent.c:183
 *   this file, faithful shim, "&#20013;"
 *       -> SIGSEGV at the equivalent of :183, a WRITE
 *   this file, faithful shim, "hello, world"   <- NO `&` AT ALL
 *       -> SIGSEGV in the DESTRUCTOR, i.e. :169's free
 *
 * ⭐ THE THIRD LINE IS THE ONE THAT DECIDES THE ROW'S DESIGN. `:167`'s
 * `if (filter->cache)` rejects only zero, so the wild free is UNCONDITIONAL --
 * there is no benign corpus in this configuration, `check.py` stage 2's
 * checksum agreement can never be reached, and the row could not be measured at
 * all. `TASK_PHP_034_REPORT` §5.4 measured 60 of 60 runs faulting.
 *
 * Each case is FORKED, so a SIGSEGV is a reported outcome rather than the end
 * of the run.
 *
 * ⚠ A PROBE'S CRASH/CLEAN VERDICT IS WRONG UNDER ASan unless
 * `ASAN_OPTIONS=abort_on_error=1` is set: ASan `_exit(1)`s rather than
 * re-raising, so `WIFSIGNALED` is false. `controls/native.py` sets it. THE ASan
 * REPORT IS THE EVIDENCE, NOT THE VERDICT LINE.
 */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

#define PHP_SHIM_IMPL
#include "emalloc_shim.h"

#define mbfl_malloc php_shim_emalloc
#define mbfl_free php_shim_efree

#define html_enc_buffer_size 16
static const char html_entity_chars[] = "#0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

typedef struct _mbfl_convert_filter {
    int status;
    int cache;                       /* mbfl_convert.h:49 -- THE FIELD */
} mbfl_convert_filter;

static volatile int sink;

/* mbfilter_htmlent.c:158-162 */
static void ctor(mbfl_convert_filter *filter)
{
    filter->status = 0;
    filter->cache = (int)mbfl_malloc(html_enc_buffer_size+1);   /* :161 */
}

/* mbfilter_htmlent.c:164-172 */
static void dtor(mbfl_convert_filter *filter)
{
    filter->status = 0;
    if (filter->cache)
    {
        mbfl_free((void*)filter->cache);                        /* :169 */
    }
    filter->cache = 0;
}

/* mbfilter_htmlent.c:174-242, the two arms this control needs */
static void dec(int c, mbfl_convert_filter *filter)
{
    char *buffer = (char*)filter->cache;                        /* :178 */

    if (!filter->status) {
        if (c == '&') {
            filter->status = 1;
            buffer[0] = '&';                                    /* :183 */
        } else {
            sink = c;
        }
    } else {
        buffer[filter->status++] = (char)c;                     /* :223 */
        if (!strchr(html_entity_chars, c)
            || filter->status+1 == html_enc_buffer_size) {
            buffer[filter->status] = 0;                         /* :230 */
            filter->status = 0;
        }
    }
}

static const char *STAGE = "?";

static int run_one(const char *text)
{
    mbfl_convert_filter f;
    const unsigned char *p;

    php_shim_reset();
    STAGE = "ctor";
    ctor(&f);
    fprintf(stderr, "        cache = %#010x  (a %zu-bit value in an int)\n",
            (unsigned)f.cache, sizeof(void *) * 8);
    STAGE = "feed";
    for (p = (const unsigned char *)text; *p; p++)
        dec((int)*p, &f);
    fprintf(stderr, "        stage: FED ok\n");
    STAGE = "dtor";
    dtor(&f);
    fprintf(stderr, "        stage: DESTROYED ok\n");
    return 0;
}

int main(int argc, char **argv)
{
    static const char *cases[] = {
        "hello, world",          /* NO `&` AT ALL -- and it still faults */
        "&#20013;",              /* CRASH-123.php's own input */
        "&amp;",
        "x&amp;y &#65; z",
    };
    unsigned i;
    int nfault = 0;
    unsigned reps = (argc > 1) ? (unsigned)atoi(argv[1]) : 1u;
    unsigned r;

    printf("ph45 control -- the FAITHFUL allocator, no placed arena.\n");
    printf("expectation: EVERY case faults, INCLUDING the one with no `&`.\n");
    for (i = 0; i < sizeof(cases) / sizeof(cases[0]); i++) {
        for (r = 0; r < reps; r++) {
            pid_t pid = fork();
            int st = 0;
            if (pid == 0) {
                if (r == 0)
                    fprintf(stderr, "  [%s]\n", cases[i]);
                _exit(run_one(cases[i]));
            }
            waitpid(pid, &st, 0);
            if (WIFSIGNALED(st)) {
                nfault++;
                if (r == 0)
                    printf("  %-18s -> SIGNAL %d in the %s stage\n",
                           cases[i], WTERMSIG(st), "reported above");
            } else if (r == 0) {
                printf("  %-18s -> CLEAN (exit %d)  ⚠ UNEXPECTED\n",
                       cases[i], WEXITSTATUS(st));
            }
        }
    }
    printf("-> %d of %u runs faulted\n", nfault,
           (unsigned)(sizeof(cases) / sizeof(cases[0])) * reps);
    (void)STAGE;
    return nfault == (int)((sizeof(cases) / sizeof(cases[0])) * reps) ? 0 : 1;
}
