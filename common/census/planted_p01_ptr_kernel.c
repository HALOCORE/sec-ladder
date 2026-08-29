/* TASK_131 §A/§B — PLANTED pointer-cursor C kernel for p01's contract.
 *
 * MUST-FIRE ARM.  finding 45's headline is a ZERO, and a zero is what a broken
 * detector prints.  This file has p01's exact C signature -- a pointer, an
 * offset and an explicit length -- and walks the window with a raw cursor.
 * The raw regex and census.py MUST both label it ptr_offset.  If they do not,
 * the "0 of 255" is a detector failure and nothing else.
 *
 * Semantically identical to patterns/p01-array-sum/c/kernel.c (same wrapping
 * fold, same window).  Checked by compiling both and comparing, see EQUIV.c. */
#include <stddef.h>
#include <stdint.h>

uint64_t kernel_ptr(const uint64_t *v, size_t off, size_t len)
{
    uint64_t acc = 0;
    const uint64_t *p = v + off;
    const uint64_t *e = v + off + len;
    while (p < e)
        acc += *p++;
    return acc;
}

/* the other two cursor spellings the census names, so the arm covers all three */
uint64_t kernel_ptr2(const uint64_t *v, size_t off, size_t len)
{
    uint64_t acc = 0;
    const uint64_t *p = v + off;
    size_t i;
    for (i = 0; i < len; i++)
        acc += *(p + i);
    return acc;
}
