/* ph52 control: HOW MANY OF THE 256 TAG BYTES MAKE `zval_dtor` TEAR ANYTHING
 * DOWN?  The answer is why this defect survived from 2004 to 2006 and why the
 * corpus records it `uninit-read-silent`.
 *
 *   gcc -std=c99 -Wall -Wextra -O1 tag_sweep.c -o tag_sweep && ./tag_sweep
 *   python3 tag_sweep.py            # the checker, with its negatives
 *
 * A VERBATIM transcription of `Zend/zend_variables.c:36-80` over the WHOLE byte,
 * including the two arms `c/kernel.c` does not lift (`IS_OBJECT`'s `del_ref` at
 * `:61` and `IS_RESOURCE`'s `zend_list_delete` at `:69`), so the published number
 * is about UPSTREAM and not about the kernel.
 *
 * ⚠ `RECAP_PHP.md` F102 said *"five named cases out of a byte, widened by the
 * `& ~IS_CONSTANT_INDEX` mask"*, explicitly UNTESTED.  ../NOTES.md §6 reports what
 * this program measures instead, and it differs in three ways. */
#include <stdio.h>
#define IS_NULL 0
#define IS_LONG 1
#define IS_DOUBLE 2
#define IS_STRING 3
#define IS_ARRAY 4
#define IS_OBJECT 5
#define IS_BOOL 6
#define IS_RESOURCE 7
#define IS_CONSTANT 8
#define IS_CONSTANT_ARRAY 9
#define IS_CONSTANT_INDEX 0x80
/* 0 = no-op, 1 = STR_FREE, 2 = hash destroy, 3 = object del_ref, 4 = list delete */
static int arm(unsigned char type)
{
    if (type == IS_LONG) return 0;                        /* :38-40 */
    switch (type & ~IS_CONSTANT_INDEX) {                  /* :41 */
        case IS_STRING: case IS_CONSTANT:          return 1;  /* :42-46 */
        case IS_ARRAY:  case IS_CONSTANT_ARRAY:    return 2;  /* :47-56 */
        case IS_OBJECT:                            return 3;  /* :57-63 */
        case IS_RESOURCE:                          return 4;  /* :64-71 */
        case IS_LONG: case IS_DOUBLE: case IS_BOOL: case IS_NULL:
        default:                                   return 0;  /* :72-78 */
    }
}
int main(void)
{
    int t, n[5] = {0,0,0,0,0}, tearing = 0;
    const char *nm[5] = {"no-op","STR_FREE(efree)","hash destroy+FREE_HASHTABLE",
                         "object del_ref","zend_list_delete"};
    printf("tag  arm\n");
    for (t = 0; t < 256; t++) { int a = arm((unsigned char)t); n[a]++; if (a) { tearing++;
        printf("%3d (0x%02x) -> %s\n", t, t, nm[a]); } }
    printf("\n");
    for (t = 0; t < 5; t++) printf("%-32s %3d / 256  (%6.3f %%)\n", nm[t], n[t], 100.0*n[t]/256.0);
    printf("%-32s %3d / 256  (%6.3f %%)\n", "TOTAL TEARING", tearing, 100.0*tearing/256.0);
    /* and the sub-count that FREES A POINTER READ OUT OF THE SLOT */
    printf("%-32s %3d / 256  (%6.3f %%)\n", "of which reach efree/free", n[1]+n[2], 100.0*(n[1]+n[2])/256.0);
    return 0;
}
