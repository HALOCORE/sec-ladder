/* p12 rung R1h -- kernel.c with the capacity check a careful C programmer
 * writes.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 trusts that the strings fit because that is the bug being
 * modelled, and this cell does not, so that "C is faster" and "C is unsafe"
 * stop being confounded. R1-vs-R1h is what the check costs *within one
 * language*, with the signature, the calling convention, the header test, the
 * scan routine, the fold, the cursor and the return all held fixed. The diff
 * against kernel.c is one `if`.
 *
 * **The check is written in `size_t` and that is load-bearing.** `dlen` is at
 * most `DST_CAP` in this cell and `slen` is at most `len`, so `dlen + slen`
 * cannot overflow a 64-bit unsigned. Write the same test in a narrower type --
 * `unsigned char sum = dlen + slen; if (sum <= DST_CAP)` -- and a string of
 * exactly 256 bytes wraps the sum to 0, passes the test, and is copied in full:
 * the check is present, looks right, and waves the attack through. That variant
 * is built and measured as a CONTROL in ../controls/gen_controls.py rather than
 * shipped, because it is a *third* rung and not this one; ../NOTES.md 8 has the
 * measurement. It is the answer to "R1h is the safe cell, so what is left to
 * get wrong?" -- and it is exactly p05's precedent for what makes an R1h cell
 * worth having.
 *
 * **What this cell does NOT add: a check on `nstr`, and a truncation.** The
 * declared count is still trusted and it still bounds nothing -- the terminator
 * and `p >= len` are what stop the walk, exactly as in p11. And a rejected
 * string is *skipped*, not truncated to fit: `dst` never receives a partial
 * string. Both choices are in `../spec.md`'s `idiom.required` because a rung
 * that truncates produces a different `dlen`, and `dlen` is folded.
 *
 * The rejected string's LENGTH is still folded into `acc`, in this cell and in
 * every other. So the checksum records that the string was seen; what it does
 * not record is any of its bytes. That is what makes `adversarial-off1` a
 * one-byte difference in the destination rather than a whole-window one. */
#include <string.h>

#include "kernel.h"

#define DST_CAP 128

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t dst[DST_CAP];
    size_t nstr, s, p, q, i, slen, dlen = 0;
    uint64_t acc = 0;

    (void)buf_len;

    if (len < 4)
        return 0;
    nstr = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nstr == 0)
        return 0;

    p = 4;
    for (s = 0; s < nstr; s++) {
        const void *z = memchr(buf + off + p, 0, len - p);
        q = (z == NULL) ? len : (size_t)((const unsigned char *)z - (buf + off));
        slen = q - p;
        /* THE CHECK. In `size_t`, so it cannot itself overflow. */
        if (dlen + slen <= DST_CAP) {
            for (i = p; i < q; i++)
                dst[dlen++] = buf[off + i];
        }
        acc = acc * 31 + (uint64_t)slen;
        if (q >= len)
            break;
        p = q + 1;
        if (p >= len)
            break;
    }
    for (i = 0; i < dlen; i++)
        acc = acc * 31 + (uint64_t)dst[i];
    return (acc * 31 + (uint64_t)dlen) * 31 + (uint64_t)nstr;
}
