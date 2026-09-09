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
 * Reads `slen from length` triples on stdin. Prints, per triple, either
 * `FALSE` or `from length_a length_ab` -- ⚠⚠ **TWO lengths since
 * `TASK_PHP_018`**, because there are now two configurations to compare
 * against and only one of them ships:
 *
 *   length_a   R1h as SHIPPED: `cb3cca21b345` hunk (a) alone, which is
 *              php-5.2.12 .. php-5.2.17. Hunk (a) never touches `length`, so
 *              this is just the mbstring.c clamp's output.
 *   length_ab  the WITHDRAWN two-hunk configuration, php-5.1.2 .. php-5.2.11.
 *              `c2471b495009` removed hunk (b) as bug #49354; the row keeps it
 *              measurable here rather than deleting the evidence.
 *
 * ⚠ Hunk (a) is in BOTH, so `FALSE` is a property of the triple and not of the
 * configuration -- which is itself the reason hunk (a) is the memory-safety
 * half: it is the only one of the two whose effect is a refusal.
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
        /* cb3cca21b345 hunk (a) -- in BOTH configurations. */
        if (from > str_len) {
            printf("FALSE\n");
            continue;
        }
        /* R1h AS SHIPPED stops here: hunk (a) does not touch `length`. */
        int32_t length_a = length;
        /* cb3cca21b345 hunk (b) -- WITHDRAWN by c2471b495009 (bug #49354).
         * Kept here so the row can still measure what it used to ship. */
        int32_t length_ab = length;
        if (((unsigned)from + (unsigned)length) > str_len) {
            length_ab = str_len - from;
        }
        printf("%d %d %d\n", from, length_a, length_ab);
    }
    return 0;
}
