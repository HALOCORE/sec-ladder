/* p25 rung R1 -- driver. Its own translation unit so that `isolated` builds put
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
 * in nothing else.
 *
 * **The driver allocates nothing from an attacker-controlled size.** p25's
 * payload has one head word (`stride`) and a byte blob, so there is no
 * `slb_zeroed`, no `SLB_MAX_CAP` and no exit 7 here -- p27's, p29's, p32's and
 * p34's shape. The allocations p25 is about are the TWO GROWABLE VECTORS, they
 * are made, grown and freed *inside the kernel*, and their sizes are bounded by
 * the compile-time constant `P25_MAXCAP`. What the file controls is how many
 * pushes there are, when a saved interior pointer is taken, and whether a growth
 * falls between that pointer and the read of it.
 *
 * ⚠ **The driver's own two allocations are load-bearing for the topology and
 * that is disclosed rather than incidental.** `slb_load` allocates the payload
 * and `slb_head1_u64_bytes` allocates the body copy, both BEFORE the kernel
 * runs, so both are older than either vector; the vector that cannot extend in
 * place is the token one, and what blocks it is the STRING vector allocated
 * after it inside the kernel. `../controls/reloc_probe.py` measures which growth
 * relocates under exactly this driver rather than under a hand-rolled one, which
 * is the mistake `TASK_134` made.
 *
 * `stride_w >= 4` is the guard, because p25's window header is the 4-byte `nops`
 * field. `adversarial-stride3.bin` attacks it.
 *
 * There are TWO conjuncts here and not p17's three: p25's cursor guard is
 * written subtraction-first and maintains `p <= len` itself, so no precondition
 * about `len` is needed to keep the cursor arithmetic overflow-free.
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
    if (stride_w >= 4 && stride_w <= (uint64_t)n_blob) {
        size_t stride = (size_t)stride_w;
        uint64_t nwin = (uint64_t)(n_blob / stride);
        uint64_t it = 0;
        while (it < inp.n_iters) {
            size_t k = (size_t)(((unsigned __int128)acc * (unsigned __int128)nwin) >> 64);
            uint64_t r = kernel(buf, n_blob, k * stride, stride);
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
