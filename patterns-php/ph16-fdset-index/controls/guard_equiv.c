/* ph16 -- the two spellings of `99e290f882c9` guard (b), IN C, against
 * a real `fd_set` and the platform's real `FD_SET` macro.
 *
 * Driven by controls/guard_equiv.py, which compares this output with the Rust
 * rungs' spelling and with the model's. Prints one line per `this_fd`:
 *
 *     <this_fd> <upstream-verdict> <wordindex-verdict> <word> <bit>
 *
 * where the two verdicts are `1` if that spelling performs the write:
 *
 *     upstream    `if (fd < FD_SETSIZE)`      -- c/kernel_hardened.c, safe_naive.rs
 *     wordindex   `if (fd / 64 < NW)`         -- safe_tuned.rs, unsafe.rs, verus.rs
 *
 * and `word`/`bit` are what `FD_SET` actually touched, read back out of the
 * object rather than recomputed -- so the C's own macro decides, not this
 * file's arithmetic. A `this_fd` the upstream spelling admits writes into a
 * real `fd_set` here and the word it moved is found by scanning it.
 *
 * ⚠ `_FORTIFY_SOURCE` is turned off for the same reason c/kernel.c turns it
 * off: with the toolchain default at -O2+ the unguarded arm would abort instead
 * of writing, and this probe would measure the toolchain rather than the
 * spellings. NOTES.md §2.
 *
 * The unguarded arm is NEVER exercised here: both spellings are asked, and only
 * where one of them says yes is a write performed. So this probe stays in
 * bounds even though the row it belongs to does not.
 */
#undef _FORTIFY_SOURCE
#define _FORTIFY_SOURCE 0

#include <stdio.h>
#include <string.h>
#include <sys/select.h>

#define NW (FD_SETSIZE / (8 * (int)sizeof(unsigned long)))

int main(void)
{
    int fd;
    if (sizeof(fd_set) != (size_t)NW * sizeof(unsigned long)) {
        printf("CANNOT EVALUATE: fd_set is not %d words\n", NW);
        return 2;
    }
    printf("# this_fd upstream wordindex word bit\n");
    for (fd = 0; fd < 16384; fd++) {
        int up = (fd < FD_SETSIZE);
        int wi = ((fd / 64) < NW);
        int word = -1, bit = -1;
        if (up || wi) {
            fd_set s;
            const unsigned long *b = (const unsigned long *)(const void *)&s;
            int i;
            FD_ZERO(&s);
            FD_SET(fd, &s);                 /* the platform's own macro */
            for (i = 0; i < NW; i++) {
                if (b[i]) {
                    int k;
                    word = i;
                    for (k = 0; k < 64; k++)
                        if (b[i] & (1UL << k)) { bit = k; break; }
                    break;
                }
            }
        }
        printf("%d %d %d %d %d\n", fd, up, wi, word, bit);
    }
    return 0;
}
