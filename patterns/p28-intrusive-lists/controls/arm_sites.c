/* p28 CONTROLS -- the harm-site arm. Built and run by
 * `controls/harm_sites.py`; not a rung, not in the matrix, not measured.
 *
 * Three entry points, all from the SAME kernel body (`controls/arm_body.inc`,
 * included twice):
 *
 *   k_bug  R1  -- TRIM frees the victim and leaves the hash chain
 *   k_fix  R1h -- the same, plus the nine-line splice
 *   k_ctl      -- THE POSITIVE CONTROL: an unmistakable heap-use-after-free of
 *                 the same shape (allocate, free, read a field). ⚠ If this arm
 *                 is silent the detector is not running and NO conclusion may be
 *                 drawn from a silent `k_bug`. `TASK_143` had clang ELIMINATE a
 *                 positive control of exactly this shape via malloc elision, and
 *                 `p31` hit the same artefact, so the pointer is laundered
 *                 through a volatile sink below and `harm_sites.py` asserts the
 *                 arm fires.
 *
 * `p28_site_head` / `p28_site_interior` count, in the HARDENED arm and before
 * any free, which of the two sites TRIM's victim occupies -- see
 * `controls/arm_body.inc`'s header for why that is the honest way to ask.
 *
 * usage:  ./arm_sites <bug|fix|ctl> <hex-op-stream>
 *
 * The op stream is hex on the command line so that every input this control
 * uses is reproduced by `harm_sites.py` itself and no `.bin` blob is left
 * behind (`.memory/00-environment.md` constraint 6). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>

#define P28_NB 8
#define P28_SLOTS 48
#define P28_SENT 251

#if defined(__GNUC__)
#define SLB_NOINLINE __attribute__((noinline))
#else
#define SLB_NOINLINE
#endif

struct p28_obj {
    struct p28_obj *lp, *ln;
    struct p28_obj *hn, *hp;
    uint8_t key, val;
};

static unsigned long p28_site_head = 0;
static unsigned long p28_site_interior = 0;

/* LSan needs use_stacks=0 on this box or a stale stack root keeps the last
 * allocation alive at -O1/-O2 (`.memory/00-environment.md`). Costs nothing when
 * LSan is not linked in. */
#if defined(__has_feature)
#if __has_feature(address_sanitizer)
#define SLB_HAVE_ASAN 1
#endif
#endif
#if defined(__SANITIZE_ADDRESS__)
#define SLB_HAVE_ASAN 1
#endif
#if defined(SLB_HAVE_ASAN) || defined(SLB_WANT_LSAN_HOOK)
const char *__lsan_default_options(void);
const char *__lsan_default_options(void) { return "use_stacks=0"; }
#endif

#define KNAME k_bug
#define SLB_HARDEN 0
#define SLB_SITES 0
#include "arm_body.inc"
#undef KNAME
#undef SLB_HARDEN
#undef SLB_SITES

#define KNAME k_fix
#define SLB_HARDEN 1
#define SLB_SITES 1
#include "arm_body.inc"
#undef KNAME
#undef SLB_HARDEN
#undef SLB_SITES

/* THE POSITIVE CONTROL. `sink` is `volatile` so neither compiler can prove the
 * allocation non-escaping and delete the `malloc`/`free` pair
 * (`.memory/03-measurement.md`: both do that at -O2 by default, and it is how
 * `TASK_143` lost a control). */
static struct p28_obj *volatile sink;

SLB_NOINLINE uint64_t k_ctl(const uint8_t *buf, size_t buf_len, size_t off,
                            size_t len)
{
    struct p28_obj *q;
    uint64_t acc = 0;
    (void)buf_len;
    (void)off;
    (void)len;
    q = (struct p28_obj *)malloc(sizeof *q);
    if (q == NULL)
        abort();
    q->key = buf[0];
    q->val = 7;
    q->lp = q->ln = q->hn = q->hp = NULL;
    sink = q;
    free(q);
    q = sink;
    acc = acc * 31 + (uint64_t)q->key; /* <- MUST be reported */
    return acc;
}

static int hexval(int c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

int main(int argc, char **argv)
{
    const char *arm, *hex;
    size_t n, i;
    uint8_t *buf;
    uint64_t r;

    if (argc < 3) {
        fprintf(stderr, "usage: %s <bug|fix|ctl> <hex>\n", argv[0]);
        return 2;
    }
    arm = argv[1];
    hex = argv[2];
    n = strlen(hex) / 2;
    buf = (uint8_t *)malloc(n ? n : 1);
    if (buf == NULL) return 3;
    for (i = 0; i < n; i++) {
        int hi = hexval((unsigned char)hex[2 * i]);
        int lo = hexval((unsigned char)hex[2 * i + 1]);
        if (hi < 0 || lo < 0) { fprintf(stderr, "bad hex\n"); return 2; }
        buf[i] = (uint8_t)(hi * 16 + lo);
    }

    if (strcmp(arm, "bug") == 0)      r = k_bug(buf, n, 0, n);
    else if (strcmp(arm, "fix") == 0) r = k_fix(buf, n, 0, n);
    else if (strcmp(arm, "ctl") == 0) r = k_ctl(buf, n, 0, n);
    else { fprintf(stderr, "bad arm\n"); return 2; }

    printf("%s %llu head=%lu interior=%lu\n", arm, (unsigned long long)r,
           p28_site_head, p28_site_interior);
    free(buf);
    return 0;
}
