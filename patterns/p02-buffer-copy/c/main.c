/* p02 rung R1 -- driver. Its own translation unit so that `isolated` builds put
 * the kernel behind a real call. The marked region below is the C copy of the
 * shared driver loop in ../spec.md; harness/check.py normalises it and diffs it
 * against the canonical token sequence pinned there.
 *
 * The two marker comments are delimiters, not prose: harness/dloop.py raises if
 * a file carries more than one of either, because a second pair lets a decoy
 * region be diffed while the real loop goes unchecked. Do not mention them
 * anywhere else in this file.
 *
 * Both C cells -- c-gcc/c-clang (R1) and c-gcc-h/c-clang-h (R1h) -- link this
 * same driver against a different kernel.c, so the two differ in the kernel and
 * in nothing else. */
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

#include "driver.h"
#include "kernel.h"

int main(int argc, char **argv)
{
    const char *path = slb_arg_path(argc, argv);
    slb_input inp;
    uint64_t cap_w, stride_w;
    size_t n_body, dst_cap;
    unsigned char *bytes, *dbuf;

    slb_load(path, &inp);
    bytes = slb_head2_u64_bytes(&inp, &cap_w, &stride_w, &n_body);
    dbuf = slb_zeroed(cap_w);
    dst_cap = (size_t)cap_w;

    /* SLB-DRIVER-BEGIN */
    size_t n_src = n_body;
    const uint8_t *src = bytes;
    uint8_t *dst = dbuf;
    uint64_t acc = 0;
    if (stride_w >= 2 && stride_w <= (uint64_t)n_src) {
        size_t stride = (size_t)stride_w;
        uint64_t nrec = (uint64_t)(n_src / stride);
        uint64_t it = 0;
        while (it < inp.n_iters) {
            size_t k = (size_t)(((unsigned __int128)acc * (unsigned __int128)nrec) >> 64);
            uint64_t r = kernel(src, n_src, k * stride, dst, dst_cap);
            acc = acc * 31 + r;
            it = it + 1;
        }
    }
    /* SLB-DRIVER-END */

    slb_emit(acc);
    free(dbuf);
    free(bytes);
    free(inp.payload);
    return 0;
}
