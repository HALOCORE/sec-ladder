/* ph64 rung R1 -- driver. Its own translation unit so that `isolated` builds
 * put the kernel behind a real call. The marked region below is the C copy of
 * the shared driver loop in ../spec.md; harness/check.py normalises it and
 * diffs it against the canonical token sequence pinned there.
 *
 * The two marker comments are delimiters, not prose: harness/dloop.py raises if
 * a file carries more than one of either, because a second pair lets a decoy
 * region be diffed while the real loop goes unchecked. Do not mention them
 * anywhere else in this file.
 *
 * Both C cells -- c-gcc/c-clang (R1) and c-gcc-h/c-clang-h (R1h) -- link this
 * same driver against a different kernel TU, so the two differ in the kernel
 * and in nothing else.
 *
 * The driver allocates nothing from an attacker-controlled size: ph64's payload
 * is one head word (`stride`) and a blob whose length is the file's length.
 * Every allocation an attacker reaches is INSIDE the kernel -- `2N + 2` blocks
 * of 8 or 39 bytes, bounded by the window because `N <= (stride - 16) / 8` --
 * and they are served by `common-php/emalloc_shim.h` because
 * `register_tick_function:2823` passes `persistent = 0`, which makes
 * `pemalloc`/`pefree` exactly `emalloc`/`efree`. So there is no `slb_zeroed`,
 * no `SLB_MAX_CAP` and no exit 7 here.
 *
 * `stride_w >= 24` rather than ph03's `>= 1`: a window is four u32 head words
 * plus at least one 4-byte tick-function slot, so 24 bytes is the smallest
 * window that describes a one-entry tick list. Below that `nmax = (len - 16)/4`
 * would be zero and `nent_w % nmax` would divide by zero. The guard also keeps
 * `nwin = n_blob / stride` from dividing by zero and makes
 * `adversarial-nowin.bin` skip the loop entirely rather than enter it and break
 * out, which would put a branch inside the measured loop.
 *
 * ⚠⚠ `stride_w <= 268435456` (256 MiB) IS THE THIRD CONJUNCT AND IT IS NOT
 * COSMETIC. `zend_llist` links elements by POINTER; the four Rust rungs link
 * them by a `u32` ARENA INDEX, which is what makes the walk expressible in safe
 * Rust at all (`../safe_naive.rs`). A `u32` index is sound exactly while the
 * arena holds fewer than 2^32 entries, and `n <= (stride - 16) / 4`, so a
 * 256 MiB ceiling on the window gives `n <= 2^26` with 64x to spare. It is a
 * structural precondition of the REPRESENTATION, it is stated as `verus.rs`'s
 * third `requires`, and this line is where it is discharged. All six rungs
 * carry it, so no rung is measured over a domain another rung refuses.
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
    if (stride_w >= 24 && stride_w <= 268435456 && stride_w <= (uint64_t)n_blob) {
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
