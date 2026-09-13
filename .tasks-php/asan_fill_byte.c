/* asan_fill_byte.c -- WHOSE pattern is `0xbe`?
 *
 * Build + run:
 *   ~/tools/llvm/bin/clang -O1 -fsanitize=address .tasks-php/asan_fill_byte.c \
 *       -o .temp/asan_fill_byte && .temp/asan_fill_byte
 *   ~/tools/llvm/bin/clang -O1 .tasks-php/asan_fill_byte.c \
 *       -o .temp/asan_fill_byte_plain && .temp/asan_fill_byte_plain
 *
 * WHY THIS IS COMMITTED RATHER THAN LEFT IN `.temp/`, which is where it was
 * written: it is the only evidence behind two published claims, and
 * `RECAP_PHP.md` open item 86 is the finding that a published claim whose only
 * evidence is a gitignored probe will not survive a clean checkout.
 * `.memory-php/04-process.md` law 11. `.tasks-php/` is in NO digest, so this
 * costs nothing.
 *
 * WHAT IT SETTLES, measured on this box 2026-09-13:
 *
 *     with ASan     heap[0..7] = be be be be be be be be
 *                   stack[0..7] = 00 00 00 00 00 00 00 00
 *     without       heap[0..7] = 00 00 00 00 00 00 00 00
 *                   stack[0..7] = 00 00 00 00 00 00 00 00
 *
 * (1) `ph53`'s R1 faults on `0xbebebebebebebebe`, and `0xbe` is ASan's MALLOC
 *     FILL BYTE -- not the row's and not the shim's. So that `cwe_note`
 *     describes a detector-dependent observation as a row property
 *     (RECAP_PHP.md item 96, F102).
 *
 *     !! AND IT IS WEAKER THAN A COMPILE-TIME PROPERTY: `malloc_fill_byte` is a
 *     RUNTIME ASAN OPTION whose default is 0xbe, so
 *     `ASAN_OPTIONS=malloc_fill_byte=0` gives zeros from the same binary. The
 *     third arm below measures that.
 *
 *     !!! AND THE FIRST VERSION OF THIS HEADER GOT THE REASON WRONG, in the
 *     sentence that was supposed to be the correction. It read "NOT
 *     `common-php/emalloc_shim.h`'s, which ZEROES fresh blocks and poisons
 *     `0x5a` ON FREE". BOTH HALVES ARE FALSE and the file says so itself:
 *     the `memset(p, 0, ...)` at `emalloc_shim.h:573` is inside
 *     `php_shim_ecalloc`, where zeroing is the CONTRACT -- `emalloc` does not
 *     zero, it is plain `malloc` -- and `0x5a` appears in that header's own
 *     "WHAT IS DELIBERATELY NOT MODELLED" list, as a ZEND_DEBUG behaviour the
 *     shim omits ON PURPOSE ("modelling it would ADD a poison-on-free that
 *     pristine PHP does not do"). I had read one function's body as the general
 *     allocation path, and a list of what a file does NOT do as what it does.
 *     Caught by TASK_PHP_044 7.2, which checked a task-file premise instead of
 *     inheriting it. `.memory-php/04-process.md` law 15.
 *
 * (2) ASan does NOT fill the stack, and a fresh stack slot reads ZERO. For
 *     `ph52` -- whose uninitialised datum is a zval TAG BYTE on the caller's
 *     stack -- zero is `IS_NULL` (Zend/zend.h:387) and `_zval_dtor`
 *     (Zend/zend_variables.c:36-57) has NO `case IS_NULL`, so THE DEFECT IS
 *     SILENT ON A CLEAN STACK. Its adversarial input is therefore a
 *     CALL-HISTORY property, not a blob property (F102, TASK_PHP_045 2.3).
 *
 * The binaries are re-derivable and are deleted; this file is the evidence
 * (CLAUDE.md "Don't" rule 1: keep the generator, delete the artefact).
 */
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    unsigned char *p = (unsigned char *)malloc(64);
    printf("heap[0..7]  =");
    for (int i = 0; i < 8; i++) printf(" %02x", p[i]);
    printf("\n");
    { /* un-initialised automatic storage, for the ph52 question */
        volatile unsigned char s[64];
        printf("stack[0..7] =");
        for (int i = 0; i < 8; i++) printf(" %02x", s[i]);
        printf("\n");
    }
    free(p);
    return 0;
}

/* THE THIRD ARM, which is what makes the claim a RUNTIME one:
 *
 *   ASAN_OPTIONS=malloc_fill_byte=0 .temp/asan_fill_byte
 *     -> heap[0..7] = 00 00 00 00 00 00 00 00
 *
 * Same binary, same source, no rebuild. So `0xbe` is an ASan OPTION DEFAULT and
 * not a property of the program, the row, or the allocator shim -- which is why
 * `ph53`'s `cwe_note` quoting it as the faulting value needs the clause naming
 * whose pattern it is. Measured 2026-09-13; TASK_PHP_044 7.1 measured four arms
 * of this same source independently and agreed.
 */
