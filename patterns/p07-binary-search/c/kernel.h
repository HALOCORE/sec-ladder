#ifndef P07_KERNEL_H
#define P07_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p07: binary search. `nq` lookups into one window's sorted u32 array.
 * CWE-129 (improper validation of an array index) turning into CWE-125, with
 * CWE-190 (integer overflow) hiding one width down -- in the LENGTH CHECK, not
 * in the midpoint. See ../README.md and ../NOTES.md 0.
 *
 *   window = buf[off .. off+len)
 *   n           = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   nq          = u32 LE at window byte 4        DECLARED. ATTACKER DATA.
 *   elements    = u32 LE x n   at window byte 8       -- SORTED ASCENDING
 *   queries     = u32 LE x nq  at window byte 8 + 4*n
 *   avail       = len - 8                        what actually ARRIVED
 *
 *   for q in 0 .. nq:
 *       key = queries[q]
 *       lo = 0 ; hi = n                          <<< HALF-OPEN, see below
 *       found = UINT64_MAX
 *       while lo < hi:
 *           mid = lo + (hi - lo) / 2             <<< the overflow-safe midpoint
 *           v   = elements[mid]
 *           if v == key { found = mid; break; }
 *           if v <  key { lo = mid + 1; } else { hi = mid; }
 *       acc = acc*31 + (found + 1)               u64, wrapping
 *   return acc*31 + n*nq
 *
 * **The bug is the missing length check, and its shape is new to this repo.**
 * R1 walks `n` declared elements without asking whether `4*n + 4*nq` of them
 * arrived. Every earlier pattern that models this class reads *forwards, one
 * byte at a time, starting one past the end* (p16, p05) or *backwards but in
 * bounds* (p17). Binary search does neither: its very first probe is at element
 * `n/2`, so the first out-of-bounds access is `2*n` bytes past the buffer and
 * nothing is touched in between. No sequential walk, no gradual escalation --
 * a single wild jump. `adversarial-count.bin` (n = 4096 in an 88-byte window)
 * lands 16 KiB out; `adversarial-width.bin` (n = 2^30) lands 4 GiB out.
 *
 * **The width of the length check is the second half of the pattern, and it is
 * NOT p05's width.** `n` and `nq` are u32, so `4*n + 4*nq` reaches
 * 4*(2^32-1)*2 = 34 359 738 352, which needs 64 bits. Written in `size_t`
 * (64-bit here) or `uint64_t` it is exact. Written in **unsigned 32-bit** it
 * wraps: n = 2^30 gives 4*n = 2^32 = 0 (mod 2^32), the test passes, and the
 * search then probes 2 GiB past the window. Contrast p05, whose u16 dimension
 * fields make `nrow*ncol` at most 4 294 836 225 -- which still FITS
 * `uint32_t`, so only the *signed* spelling breaks there. Here the unsigned
 * 32-bit spelling breaks too. "Do the check in 64 bits" is load-bearing advice
 * on p07 in a way it is not on p05. NOTES.md 6 builds the narrow cell.
 *
 * **What the catalogue said, and why it is wrong.** `.memory/06-catalogue.md`
 * lists p07's bug as midpoint overflow `(lo+hi)/2`. With `n` a u32 header field
 * and `size_t` indices, `lo + hi <= 2*(2^32 - 2) = 8 589 934 588`, which is
 * 2.1e9 times short of `2^64`: the midpoint sum **cannot wrap for any input
 * this wire format can express**, and RAM is not the binding constraint. The
 * cheapest index type that could wrap is `int`, and it needs > 2^30 elements,
 * i.e. 4 GiB of u32 data. NOTES.md 0 has the arithmetic and the probe.
 * `mid = lo + (hi - lo) / 2` is spelled that way in every rung anyway, and
 * `(lo + hi) / 2` is in the pattern's `forbidden` list, so the question is
 * settled by grep rather than by argument.
 *
 * **Why half-open bounds (`hi = n`, `while lo < hi`, `hi = mid`).** The
 * textbook inclusive form -- `hi = n - 1`, `while lo <= hi`, `hi = mid - 1` --
 * has an unsigned underflow that fires on *well-formed* input: `mid == 0`
 * requires only `lo == 0 && hi <= 1`, so any key below `elements[0]` sets
 * `hi = (size_t)-1` and the next probe is at index 2^63 - 1. That is not an
 * adversarial case, it is half of an ordinary miss workload, and it would make
 * every rung -- C, safe Rust, unsafe Rust -- diverge on `small.bin`. The
 * half-open form has no subtraction that can underflow anywhere. NOTES.md 6
 * builds the inclusive variant from this file by exact-string substitution and
 * records what it does on `small.bin` (spoiler: SIGSEGV).
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no `4*n + 4*nq > avail`. THE BUG.
 *   c/kernel_hardened.c  R1h -- the same code plus that one line.
 *
 * Both take `buf_len`, and that is the point: this API *has* the size. R1 is
 * not C being unable to check, it is C code that had what it needed and did
 * not look. R1-vs-R1h is therefore what the check costs inside one language
 * with the calling convention, the argument count and the register allocation
 * all held fixed (`.memory/02-bench-rules.md`, "The precondition must be
 * structural").
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `n`, `nq`, all 2^64 pairs of them, and every element and
 * query value are attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P07_KERNEL_H */
