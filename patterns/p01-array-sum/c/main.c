/* p01 rung R1 -- driver. Its own translation unit so that `isolated` builds put
 * the kernel behind a real call. The loop between SLB-DRIVER-BEGIN and
 * SLB-DRIVER-END is the C copy of the shared driver loop in ../spec.md;
 * harness/check.py diffs it against the four Rust copies. */
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

#include "driver.h"
#include "kernel.h"

int main(int argc, char **argv)
{
    const char *path = slb_arg_path(argc, argv);
    slb_input inp;
    uint64_t win_len_w;
    size_t n_body;
    uint64_t *vals;

    slb_load(path, &inp);
    vals = slb_head_u64_body(&inp, &win_len_w, &n_body);

    /* SLB-DRIVER-BEGIN */
    size_t n_vals = n_body;
    const uint64_t *vs = vals;
    uint64_t acc = 0;
    if (win_len_w > 0 && win_len_w <= (uint64_t)n_vals) {
        size_t win_len = (size_t)win_len_w;
        uint64_t nwin = (uint64_t)(n_vals - win_len + 1);
        uint64_t it = 0;
        while (it < inp.n_iters) {
            size_t off = (size_t)(acc % nwin);
            uint64_t r = kernel(vs, off, win_len);
            acc = acc * 31 + r;
            it = it + 1;
        }
    }
    /* SLB-DRIVER-END */

    slb_emit(acc);
    free(vals);
    free(inp.payload);
    return 0;
}
