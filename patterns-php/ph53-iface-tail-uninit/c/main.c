/* ph53 rung R1 -- driver.  Its own translation unit so that `isolated` builds
 * put the kernel behind a real call.  The marked region below is the C copy of
 * the shared driver loop in ../spec.md; harness/check.py normalises it and
 * diffs it against the canonical token sequence pinned there.
 *
 * The two marker comments are delimiters, not prose: harness/dloop.py raises if
 * a file carries more than one of either, because a second pair lets a decoy
 * region be diffed while the real loop goes unchecked.  Do not mention them
 * anywhere else in this file.
 *
 * Both C cells -- c-gcc/c-clang (R1) and c-gcc-h/c-clang-h (R1h) -- link this
 * same driver against a different kernel TU, so the two differ in the kernel
 * and in nothing else.
 *
 * The driver allocates nothing from an attacker-controlled size: ph53's
 * payload is one head word (`stride`) and a blob whose length is the file's.
 * The only allocation an attacker reaches is INSIDE the kernel -- exactly one
 * `erealloc` per call, and none at all when `n_decl == 0` -- so there is no
 * `slb_zeroed`, no `SLB_MAX_CAP` and no exit 7 here.
 *
 * ⭐⭐ THAT O(1) ALLOCATION COUNT IS WHY THIS ROW NEEDS NO ALLOCATOR CAVEAT ON
 * ITS CROSS-LANGUAGE COLUMN.  `PROTOCOL_PHP.md` §B1a says §B1.2's "fold the
 * tally into the u64" is free only at O(1) allocations per kernel call, and
 * `ph64` -- at `2n+2` -- is where it stops being free.  ph53 is the exception
 * §B1a says is worth remarking on: one `erealloc` per class declaration, and
 * `FILL`/`QUERY` allocate nothing.  ../spec.md declares the order anyway
 * (§B1a.2), so a reader does not have to re-derive it from `c/kernel.c`.
 *
 * `stride_w >= 76` rather than ph16's `>= 8`: a window is three u32 head words
 * (12 B) plus the eight-entry interface pool (64 B), i.e. `PH53_OPS_OFF`, and a
 * window that short simply carries zero ops.  The guard also keeps
 * `nwin = n_blob / stride` from dividing by zero and makes
 * `adversarial-nowin.bin` skip the loop entirely rather than enter it and
 * break out, which would put a branch inside the measured loop.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

#include "driver.h"
#include "kernel.h"

int main(int argc, char **argv)
{
    const char *path = slb_arg_path(argc, argv);
    slb_input inp;
    uint64_t stride_w;
    size_t n_body;
    unsigned char *bytes;

    slb_load(path, &inp);
    bytes = slb_head1_u64_bytes(&inp, &stride_w, &n_body);

    /* SLB-DRIVER-BEGIN */
    size_t n_blob = n_body;
    const uint8_t *buf = bytes;
    uint64_t acc = 0;
    if (stride_w >= 76 && stride_w <= (uint64_t)n_blob) {
        size_t stride = (size_t)stride_w;
        uint64_t nwin = (uint64_t)(n_blob / stride);
        uint64_t it = 0;
        while (it < inp.n_iters) {
            size_t k = (size_t)(((unsigned __int128)acc * (unsigned __int128)nwin) >> 64);
            uint64_t r = kernel(buf, k * stride, stride);
            acc = acc * 31 + r;
            it = it + 1;
        }
    }
    /* SLB-DRIVER-END */

    slb_emit(acc);
    free(bytes);
    free(inp.payload);
    return 0;
}
