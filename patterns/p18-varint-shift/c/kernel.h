#ifndef P18_KERNEL_H
#define P18_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p18: a LEB128 / protobuf-style varint decoder. One window holds a declared
 * count of varints; each varint is a run of bytes whose low seven bits are the
 * payload and whose top bit says "another byte follows". See ../README.md,
 * ../spec.md and ../NOTES.md 0.
 *
 *   window = buf[off .. off+len)
 *   nv          = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   varint      = bytes, low 7 bits payload, bit 7 = continue. ATTACKER DATA.
 *   VBITS  = 64    the accumulator's width       a compile-time constant
 *
 *   acc = 0 ; p = 4
 *   for v in 0 .. nv:
 *       if p == len: break
 *       val = 0 ; shift = 0 ; nb = 0
 *       while p < len:
 *           c = buf[off+p] ; p++ ; nb++
 *           if (shift < VBITS)            <<< THE SAFETY LINE. R1 omits THIS.
 *               val |= (uint64_t)(c & 0x7f) << shift;
 *           shift += 7
 *           if !(c & 0x80): break
 *       acc = acc*31 + val
 *       acc = acc*31 + nb
 *   return acc*31 + nv
 *
 * **THE BUG IS UNDEFINED BEHAVIOUR THAT TOUCHES NO MEMORY, AND THAT IS WHAT IS
 * NEW HERE.** Every earlier bug in this project is spatial (an out-of-bounds
 * read or write) or logical-but-in-bounds. A shift whose count is at or above
 * the promoted operand's width is undefined by C99 6.5.7p3 -- but it addresses
 * nothing, allocates nothing and stores nothing. On x86-64 `shlq %cl` masks the
 * count to its low six bits, so the program ORs the attacker's payload into the
 * WRONG BIT POSITION of the accumulator and keeps going with a silently wrong
 * integer. Nothing in this project's usual toolkit sees that: not ASan, not a
 * bounds check, not a memory-safety proof. **UBSan does** -- measured at the
 * gate's own flags, ../NOTES.md 0.2 -- and that is the whole of the C side's
 * safety net.
 *
 * **The overflowing quantity is a SHIFT COUNT, and no length bounds it.**
 * `shift` is 7 times the number of bytes consumed so far, and the number of
 * bytes in one varint is decided by the attacker's continue bits, not by any
 * declared length. A canonical encoding of a `uint64_t` is at most ten bytes and
 * its last shift is exactly 63 -- in range. The ELEVENTH byte is the first one
 * that is not, and nothing in the wire format forbids an eleventh byte. That is
 * why the guard cannot be hoisted, folded into a length check, or derived from
 * the header: it has to be tested once per byte, inside the scan.
 *
 * **What this rung KEEPS is as important as what it drops.** The scan is
 * bounded by `p < len` in every rung, R1 included, so every read of `buf` is in
 * bounds in every rung -- p18 is not p11 and not p16. The outer cursor guard
 * `p == len` is present in every rung, so a dishonest `nv` cannot spin. `nb`
 * and `val` are per-varint locals reset on every varint in every rung. The only
 * thing missing from this rung is the one line that asks whether the shift
 * count still fits the accumulator.
 *
 * **The guard's two lowerings differ, and one of them still executes the
 * offending instruction.** gcc emits a branch (`cmpl $0x3f,%ecx ; ja`); clang
 * emits `cmpl $0x40,%ecx ; cmovaeq`, which performs `shlq %cl` FIRST and then
 * discards the result. Both cost exactly 2 instructions per varint byte
 * (../NOTES.md 4). Read that as the answer to "is the hardened rung actually
 * check-free, or did it just move the check?" -- on clang it moved it past the
 * shift.
 *
 * `shift` is `unsigned` and `shift += 7` wraps by definition (C99 6.2.5p9),
 * matching `wrapping_add` in the four Rust rungs. That is deliberate and it is
 * load-bearing for the measurement, not only for the semantics: it means the
 * ONLY arithmetic in this kernel that a Rust `debug-assertions=on` build could
 * fire on is the SHIFT itself, plus the two cursor increments. ../NOTES.md 5.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no shift bound. THE BUG.
 *   c/kernel_hardened.c  R1h -- `if (shift < VBITS)`, and that one line is the
 *                               whole difference.
 *
 * Both take `buf_len`, and both ignore it: p18's bound is not the source
 * buffer's length, it is the ACCUMULATOR's width, a compile-time constant in
 * every rung. p06's, p12's and p14's shape.
 *
 * **The kernel does not mutate `buf` and holds no state between calls.** The
 * driver calls it `n_iters` times and every call must return the same value.
 * There is no scratch buffer at all here -- `val`, `shift`, `nb`, `p` and `acc`
 * are locals initialised inside the call -- so p14's per-call scratch discipline
 * degenerates to "nothing crosses a call boundary", which ../NOTES.md 0c
 * measures rather than asserts.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + val`,
 * `acc*31 + nb` and the return expression are the wrapping operations ../spec.md
 * asks for with no special spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nv` and every byte of the window -- including every
 * continue bit in it -- are attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P18_KERNEL_H */
