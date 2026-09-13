/* ph52 rung R1 -- driver.  Its own translation unit so that `isolated` builds
 * put the kernel behind a real call.  The marked region below is the C copy of
 * the shared driver loop in ../spec.md; harness/check.py normalises it and diffs
 * it against the canonical token sequence pinned there.
 *
 * The two marker comments are delimiters, not prose: harness/dloop.py raises if
 * a file carries more than one of either, because a second pair lets a decoy
 * region be diffed while the real loop goes unchecked.  Do not mention them
 * anywhere else in this file.
 *
 * Both C cells -- c-gcc/c-clang (R1) and c-gcc-h/c-clang-h (R1h) -- link this
 * same driver against a different kernel TU, so the two differ in the kernel and
 * in nothing else.
 *
 * The driver allocates nothing from an attacker-controlled size: ph52's payload
 * is one head word (`stride`) and a blob whose length is the file's.  Every
 * allocation an attacker reaches is INSIDE the kernel, so there is no
 * `slb_zeroed`, no `SLB_MAX_CAP` and no exit 7 here.
 *
 * ⚠⚠ AND THE ALLOCATION COUNT IS **O(n_ops) PER CALL, NOT O(1)** -- up to five
 * `emalloc`s and three `efree`s per concat operation.  `PROTOCOL_PHP.md` §B1a
 * says §B1.2's "fold the tally into the u64" is free only at O(1) per call, so
 * this row takes §B1a.3: the order is DECLARED in ../spec.md and every
 * CROSS-LANGUAGE figure the row publishes is labelled as including allocator
 * work.  ⭐ The same-language ratios -- R2-vs-R3 and R4-vs-R5 -- are unaffected,
 * because those four rungs allocate identically and the term cancels (§B1a.4).
 * ph53 is the O(1) exception; this row is not it.
 *
 * ⚠⚠⚠ AND THE LOOP IS WHAT MAKES THE DEFECT REACHABLE, WHICH IS NEW.  ph52's
 * uninitialised datum is a STACK slot, so what decides whether `Zend/zend.c:243`
 * frees anything is the CALL HISTORY at that stack offset -- not a blob field.
 * `ph52_concat_function` is `noinline`, so op k+1's `op1_copy` sits exactly where
 * op k's did, and the op stream inside ONE window controls the whole history.
 * That is why ../inputs/gen.py asserts an ADJACENCY property and not only a
 * per-op one, and it is why `stride_w >= 8` rather than `>= 12`: a window that
 * short carries zero ops and exercises the `n_ops == 0` arm.
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
    if (stride_w >= 8 && stride_w <= (uint64_t)n_blob) {
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
