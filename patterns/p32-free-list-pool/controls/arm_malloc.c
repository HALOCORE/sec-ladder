/* p32 CONTROLS -- the storage experiment. ONE source, TWO storage arms, and the
 * kernel body included TWICE so the buggy and hardened arms of each differ by
 * the safety line alone.
 *
 *   cc arm_malloc.c            ->  per-block malloc/free storage
 *   cc -DP32_ARENA arm_malloc.c ->  the pool storage the pattern ships
 *
 *   ./a.out <bug|fix|ctl> <hex-op-stream>
 *
 * `controls/storage_arms.py` builds all of it and writes `storage_arms.json`.
 * ⚠ This is a CONTROL, not a rung: see `arm_body.inc`'s header for why the
 * include-twice construction lives here and not in `c/`.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define SLOTS 8
#define BLK 4
#define NREG 8
#define NIL 255
#define SENT 251

#ifdef P32_ARENA
#define P32_PAY(h) (&pool[(size_t)(h) * BLK])
#else
#define P32_PAY(h) (blk[h])
#endif

#define KNAME k_bug
#define P32_HARDEN 0
#include "arm_body.inc"
#undef KNAME
#undef P32_HARDEN

#define KNAME k_fix
#define P32_HARDEN 1
#include "arm_body.inc"
#undef KNAME
#undef P32_HARDEN

/* THE POSITIVE CONTROL: a real double free of a real heap block, i.e. the exact
 * detector the ARENA arm is being tested for the absence of. If this is silent
 * under ASan then the detector never started and a silent `bug` arm proves
 * nothing.
 *
 * ⚠⚠ **`slb_sink` IS LOAD-BEARING AND THE REASON IS AN INSTRUMENT DEFECT
 * THIS PROJECT HAS HIT TWICE.** clang eliminates a `malloc`/`free`/`free`
 * sequence whose pointer never escapes -- `p31`'s malloc-elision artefact -- so
 * the first spelling of this control at TASK_143 printed `rc=0, DID NOT FIRE`
 * under clang while reading as evidence. A control that cannot fire proves
 * nothing. `storage_arms.py` exits non-zero if any build's control is silent. */
static volatile void *slb_sink;

static uint64_t k_ctl(const uint8_t *buf, size_t off, size_t len)
{
    uint8_t *q;
    uint64_t acc = 0;
    (void)off;
    (void)len;
    q = (uint8_t *)malloc(BLK);
    if (q == NULL)
        abort();
    slb_sink = q;
    q[0] = buf[0];
    acc = acc * 31 + (uint64_t)q[0];
    free(q);
    slb_sink = q;
    free(q); /* <- MUST be reported */
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
    static uint8_t buf[65536];
    size_t n = 0;
    const char *h;
    if (argc != 3) {
        fprintf(stderr, "usage: arm_malloc <bug|fix|ctl> <hex>\n");
        return 2;
    }
    h = argv[2];
    while (h[0] && h[1] && n < sizeof buf) {
        int x = hexval(h[0]), y = hexval(h[1]);
        if (x < 0 || y < 0) break;
        buf[n++] = (uint8_t)(x * 16 + y);
        h += 2;
    }
    if (strcmp(argv[1], "bug") == 0)
        printf("bug %llu\n", (unsigned long long)k_bug(buf, 0, n));
    else if (strcmp(argv[1], "fix") == 0)
        printf("fix %llu\n", (unsigned long long)k_fix(buf, 0, n));
    else
        printf("ctl %llu\n", (unsigned long long)k_ctl(buf, 0, n));
    return 0;
}
