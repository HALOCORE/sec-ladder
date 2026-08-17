/* p17 rung R1 -- idiomatic C99 HTTP suffix-range server. THE BUG.
 *
 * CWE-191 (integer underflow) turning into CWE-125 (out-of-bounds read), as
 * nginx actually wrote it. `Range: bytes=-N` asks for the last N bytes, so the
 * parser computes `start = content_length - N` in signed arithmetic and
 * validates it with `if (start < end)`. That is nginx's line 371 verbatim, and
 * it passes for a *negative* start, because a negative number is still less
 * than `end`. There is no `start >= 0`.
 *
 * The single `(void)` cast is half the finding: the size is *right there* in
 * the signature. R1 has it and does not look; R1h (kernel_hardened.c) is this
 * file plus one conjunct. Everything else about the two cells -- signature,
 * calling convention, the `2 + 2*nsuf > len` test, the fold, the return -- is
 * identical, so R1-vs-R1h is the cost of the check and nothing else.
 *
 * Note what this rung *keeps*: `2 + 2*nsuf > len`. Without it the suffix table
 * itself would run off the end on *every* input, well-formed ones included, and
 * the pattern would stop being about the value of a suffix. What it drops is
 * the one conjunct marked below.
 *
 * **The sign is the whole pattern, and it produces two different harms.**
 * `abs = body_start + start == len - s`, so the served range is always
 * `[len - s, len)` and `abs + n == len` exactly: the read never runs past the
 * window, it runs backwards. How far back is one attacker-controlled `u16`:
 *
 *   1. `content_len < s <= len` -- `abs` lands between 0 and `body_start`, i.e.
 *      inside the window's own `nsuf` word and suffix table. That read is
 *      **in bounds of the allocation**. ASan does not fire, safe Rust does not
 *      panic, and a proof that every access is in bounds does not exclude it.
 *      It is Heartbleed's shape: a legal read of the wrong bytes. The only
 *      thing that rejects it is the missing `start >= 0`.
 *   2. `s > len` -- `abs` is negative, and with `off == 0` so is the absolute
 *      index. This one really is out of bounds and ASan reports it as `N bytes
 *      **before**` the region. p16's message said `after`; that difference is
 *      the difference between an unsigned and a signed underflow.
 *
 * Contrast p16 as well: there, deleting the check made the walk **never
 * terminate**, because `end - p` underflowed `size_t` and the loop condition
 * stayed true. Nothing like that happens here. `n = end - start = s <= 65535`,
 * so every served range is bounded and the loop always ends. A signed
 * underflow in an *index* is quieter than an unsigned underflow in a *bound* --
 * which is exactly why this one shipped in nginx and was exploited rather than
 * crashing in testing.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc * 31 + b` and
 * `nserved + 1` are the wrapping operations ../spec.md asks for with no special
 * spelling. Nothing here can overflow *signed*: `content_len` is at most the
 * blob length and `s` at most 65535, so `start`, `base` and `n` all stay far
 * inside `int64_t`. The only undefined behaviour this rung can execute is the
 * out-of-bounds read itself. */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t nsuf, body_start, i;
    int64_t content_len;
    uint64_t acc = 0;
    uint64_t nserved = 0;

    (void)buf_len; /* the size is right here ... and this rung never looks. */

    if (len < 2)
        return 0;
    nsuf = (size_t)buf[off] + 256 * (size_t)buf[off + 1];
    if (2 + 2 * nsuf > len)
        return 0;
    body_start = 2 + 2 * nsuf;
    content_len = (int64_t)(len - body_start);

    for (i = 0; i < nsuf; i++) {
        int64_t s, start, end, base, n, j;
        s = (int64_t)buf[off + 2 + 2 * i] + 256 * (int64_t)buf[off + 3 + 2 * i];
        start = content_len - s;
        end = content_len;
        /* R1h has `&& start >= 0` here, and this rung does not. */
        if (start < end) {
            base = (int64_t)(off + body_start) + start;
            n = end - start;
            for (j = 0; j < n; j++)
                acc = acc * 31 + buf[base + j];
            nserved = nserved + 1;
        }
    }
    return acc * 31 + nserved;
}
