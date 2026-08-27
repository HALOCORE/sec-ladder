#ifndef P42_KERNEL_H
#define P42_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p42 -- decode one record window into a heap digest buffer and checksum it
 * backwards. Contract in ../spec.md.
 *
 * The low byte of the window's first word is the record TAG. A window whose tag
 * is wrong is malformed and the kernel returns 0 -- that is the ERROR PATH, and
 * the whole subject of this pattern is what happens to the digest buffer on it.
 *
 * `len` is the window length in u64 elements AND the digest length in bytes.
 * The caller promises `1 <= len` and `off + len <= v_len`; C has no way to state
 * either, which is the usual asymmetry (../spec.md "Kernel signature"). */
#define P42_TAG 0xA7u
#define P42_MIX 0x9E3779B97F4A7C15ull

/* The driver's ceiling on the window length, and therefore on the digest
 * allocation: one byte per window element, so at most 64 KiB per call. An
 * allocation whose size comes from an untrusted header needs a ceiling; this is
 * the driver's, it sits outside the measured loop, and every rung carries it.
 * R5 needs it as well -- `vstd::layout::valid_layout(size, 1)` is
 * `size <= isize::MAX` and the pinned vstd bounds no slice length below
 * `usize::MAX`. See ../verus.rs's module comment. */
#define P42_MAXWIN 65536

SLB_NOINLINE uint64_t kernel(const uint64_t *v, size_t off, size_t len);

#endif /* P42_KERNEL_H */
