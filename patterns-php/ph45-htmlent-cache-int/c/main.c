/* ph45 rung R1 -- driver.  Its own translation unit so that `isolated` builds
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
 * ⚠⚠ `ph45_arena_init()` IS CALLED HERE, ONCE, BEFORE THE MEASURED REGION, and
 * that placement is a requirement rather than a tidiness: the arena is two
 * `mmap` calls, and a per-call `mmap` would put a syscall inside the
 * marginal-`Ir` subtraction every number in `results-php/` rests on
 * (`TASK_PHP_034_REPORT` §6.3(3)).  The four Rust rungs have no counterpart --
 * they own a `Vec<u8>` arena and never ask the kernel for an address -- which
 * is this row's ladder result and not an asymmetry in the driver.
 *
 * The driver allocates nothing from an attacker-controlled size: ph45's payload
 * is one head word (`stride`) and a blob whose length is the file's length.
 * Every allocation an attacker reaches is INSIDE the kernel -- two 17-byte work
 * buffers from `c/arena.h` and two filter structs from
 * `common-php/emalloc_shim.h`, both a fixed count per call -- so there is no
 * `slb_zeroed`, no `SLB_MAX_CAP` and no exit 7 here.
 *
 * `stride_w >= 16` rather than ph03's `>= 1`: a window is two u32 head words
 * plus at least eight text bytes, four for each of the two filters.  The guard
 * also keeps `nwin = n_blob / stride` from dividing by zero and makes
 * `adversarial-nowin.bin` skip the loop entirely rather than enter it and break
 * out, which would put a branch inside the measured loop.
 *
 * ⚠⚠ `stride_w <= 268435456` (256 MiB) IS THE THIRD CONJUNCT AND IT IS NOT
 * COSMETIC.  C stores the work buffer's ADDRESS in an `int`; the four Rust
 * rungs store an INDEX into a `Vec<u8>` the kernel owns, in the same `i32`
 * field -- and an index round-trips through `i32` exactly while the arena holds
 * fewer than 2^31 bytes.  A 256 MiB ceiling on the window is what discharges
 * that, it is stated as `verus.rs`'s third `requires`, and this line is where
 * it is discharged.  All six rungs carry it, so no rung is measured over a
 * domain another rung refuses.
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
    ph45_arena_init();

    /* SLB-DRIVER-BEGIN */
    size_t n_blob = n_body;
    const uint8_t *buf = bytes;
    uint64_t acc = 0;
    if (stride_w >= 16 && stride_w <= 268435456 && stride_w <= (uint64_t)n_blob) {
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
