#ifndef P01_KERNEL_H
#define P01_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p01 rung R1: sum v[off .. off+len), wrapping modulo 2^64.
 * Contract in ../spec.md. No length is passed, and no bound is checked -- that
 * is the point of the C rung. */
SLB_NOINLINE uint64_t kernel(const uint64_t *v, size_t off, size_t len);

#endif /* P01_KERNEL_H */
