/* p42 rung R1 -- driver. Its own translation unit so that `isolated` builds put
 * the kernel behind a real call. The marked region below is the C copy of the
 * shared driver loop in ../spec.md; harness/check.py normalises it and diffs it
 * against the canonical token sequence pinned there.
 *
 * The two marker comments are delimiters, not prose: harness/dloop.py raises if
 * a file carries more than one of either, because a second pair lets a decoy
 * region be diffed while the real loop goes unchecked. Do not mention them
 * anywhere else in this file.
 *
 * NOTE ON THE LEAK DETECTOR: this file defines no `__lsan_default_options`
 * hook, deliberately. `.memory/00-environment.md` offers one for leaks whose
 * root stays live in a stale stack slot; p42's does not need it -- its digest
 * pointer is dead by the time the kernel returns and every leaked block but
 * possibly the last is unreachable from any frame. Measured through the gate's
 * own stage 7, both with and without the hook. Adding one would be `Ir`-neutral
 * but would also be an unvalidated instrument on a pattern that does not need
 * it. See ../NOTES.md 3.
 *
 * `main` releases `vals` and `inp.payload` on the way out, as every pattern's
 * does, so a leak reported by LeakSanitizer on this program is the kernel's. */
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
    if (win_len_w > 0 && win_len_w <= P42_MAXWIN && win_len_w <= (uint64_t)n_vals) {
        size_t win_len = (size_t)win_len_w;
        uint64_t nwin = (uint64_t)(n_vals - win_len + 1);
        uint64_t it = 0;
        while (it < inp.n_iters) {
            size_t off = (size_t)(((unsigned __int128)acc * (unsigned __int128)nwin) >> 64);
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
