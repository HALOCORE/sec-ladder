/* ph07 control -- the C spelling of the caller's clamps, standalone.
 *
 * `c/kernel.c`'s wrapper writes mbstring.c:1787-1805 and cb3cca21b345 in `int`,
 * exactly as PHP does. The four Rust rungs write the same function in `usize`
 * with `saturating_sub` / `saturating_add`, because Verus has no `isize::MAX`
 * fact for a slice length and a signed round-trip is not total.
 *
 * `PROTOCOL_PHP.md` §A1(c): *"modelled by an equivalent is a claim that needs a
 * differential and not a comment"*. This program is the C half of that
 * differential; `guard_equiv.py` is the Rust half and the comparison.
 *
 * Reads `slen from length` triples on stdin, prints `from length` after the
 * clamps, or `FALSE`.
 *
 *   cc -std=c99 -Wall -Wextra -O2 guard_equiv.c -o guard_equiv
 */
#include <stdint.h>
#include <stdio.h>

int main(void)
{
    long a, b, c;
    while (scanf("%ld %ld %ld", &a, &b, &c) == 3) {
        int32_t str_len = (int32_t)(unsigned int)a;
        int32_t from = (int32_t)b;
        int32_t length = (int32_t)c;

        /* mbstring.c:1787-1793 */
        if (from < 0) {
            from = str_len + from;
            if (from < 0) {
                from = 0;
            }
        }
        /* mbstring.c:1795-1801 */
        if (length < 0) {
            length = (str_len - from) + length;
            if (length < 0) {
                length = 0;
            }
        }
        /* cb3cca21b345 hunk (a) */
        if (from > str_len) {
            printf("FALSE\n");
            continue;
        }
        /* cb3cca21b345 hunk (b) */
        if (((unsigned)from + (unsigned)length) > str_len) {
            length = str_len - from;
        }
        printf("%d %d\n", from, length);
    }
    return 0;
}
