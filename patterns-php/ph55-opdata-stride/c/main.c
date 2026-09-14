/* ph55 rung R1 -- driver. Its own translation unit so that `isolated` builds
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
 * The driver allocates nothing from an attacker-controlled size: ph55's
 * payload is one head word (`stride`) and a blob whose length is the file's
 * length, and the kernel allocates nothing at all -- the op_array and the
 * execute_data are frame objects of a size the row fixes. So there is no
 * `slb_zeroed`, no `SLB_MAX_CAP` and no exit 7 here.
 *
 * ⚠⚠ THE THREE GUARDS ON `stride_w` ARE STRUCTURAL AND THEY ARE THE
 * KERNEL'S PRECONDITION, NOT A SAFETY CHECK IN THE EXECUTOR:
 *
 *   stride_w >= 16          an op_array has at least two words, because PHP's
 *                           own tail is ZEND_RETURN followed by
 *                           ZEND_HANDLE_EXCEPTION (zend_compile.c:1091-1092)
 *                           and `kernel.c`'s decoder writes both. Two
 *                           terminators and a maximum stride of two is what
 *                           keeps the PC inside the array -- ../NOTES.md §4.
 *   stride_w <= 512         PH55_MAX_OPS * 8. PHP's op_array is heap-grown by
 *                           `get_next_op` and has no such bound; the kernel
 *                           uses a frame array, so the bound lives here, in
 *                           the DRIVER, outside every measured loop and
 *                           outside the executor. Itemised in ../spec.md
 *                           `provenance.divergences`.
 *   stride_w <= n_blob      at least one whole window is present.
 *
 * `stride_w % 8` is deliberately NOT tested: `nops = len / 8` truncates, and a
 * trailing partial word is simply not an instruction. That is one fewer token
 * in the pinned loop and one fewer thing a rung can spell differently.
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
    if (stride_w >= 16 && stride_w <= 512 && stride_w <= (uint64_t)n_blob) {
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
