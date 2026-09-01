/* p49 POSITIVE CONTROL 2 of 3: the **ASan stack** column, and it is the one
 * that is row-specific.
 *
 * ⚠⚠ **WHAT THIS FILE BUYS THAT `ctl_asan.c` DOES NOT.** p49's pool is a LOCAL
 * ARRAY, `uint8_t mem[P49_MEM]`, and the kernel's harm is the store
 * `mem[roff[t]] = 0` -- a store that stays inside that array in every run of
 * both rungs. `ctl_asan.c` proves ASan is linked and speaking about the HEAP;
 * it says nothing about whether ASan would see a stray store to a STACK array,
 * which is the object this pattern's write actually lives in. Without this
 * control, *"ASan is silent on p49"* would be compatible with *"ASan cannot see
 * this class of object at all"*.
 *
 * So this file is `c/kernel.c`'s write, one byte outside the pool: the same
 * array of the same extent in the same storage class, indexed one past the end.
 * The index is laundered through a `volatile` so it cannot be folded, and the
 * array escapes through a sink so it cannot be deleted.
 *
 * ✅ **Read the pair together: p49's write is IN BOUNDS and ASan says nothing;
 * the SAME write one byte out is reported. The silence is therefore a fact
 * about the program, not about the instrument.**
 *
 * ⚠ It licenses the ASan column only -- `-fsanitize=undefined` has no
 * stack-buffer-overflow check either, so a UBSan-only build of this file is
 * silent. `ctl_ubsan.c` is the third control.
 *
 * Expected: ASan reports `stack-buffer-overflow`; the plain build prints a byte
 * and exits 0 (or does something unspecified -- the point is only that ASan
 * fires).
 */
#include <stdio.h>

#define CTL_MEM 64

/* `volatile` so the index is not a compile-time constant and the store is not
 * folded away or diagnosed at compile time. */
static volatile int slb_off49 = CTL_MEM; /* one past the end */
static volatile unsigned char *slb_sink49s;

int main(int argc, char **argv)
{
    unsigned char mem[CTL_MEM];
    int i;
    (void)argv;
    for (i = 0; i < CTL_MEM; i++)
        mem[i] = (unsigned char)(i + argc);
    slb_sink49s = mem;
    /* THE HARM: c/kernel.c's store, one byte outside the pool.
     * MUST be reported by ASan. */
    mem[slb_off49] = 0;
    printf("%u\n", (unsigned)slb_sink49s[0]);
    return 0;
}
