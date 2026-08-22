#ifndef P38_KERNEL_H
#define P38_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p38: strict aliasing / type punning. **The first bug class in this tree that
 * unsafe Rust does not reintroduce** -- Rust has no type-based aliasing rule at
 * all, so R2, R3, R4 and R5 are immune *by construction*, not by checking.
 *
 * The wire format is WORD-ORIENTED: the record stream is a sequence of 16-bit
 * words, and it is decoded into a `uint16_t` scratch before it is walked. A
 * record's 32-bit length field is stored on the wire as two 16-bit halves, and
 * the parser reads it back with the fast combined load
 *
 *     *(const uint32_t *)r          <<< THE PUN, in c/kernel.c
 *
 * which is undefined behaviour by C99 6.5p7: the object is an array of
 * `uint16_t` and the lvalue has type `uint32_t`, and neither is a character
 * type. `c/kernel_hardened.c` writes `(uint32_t)r[0] + 65536 * (uint32_t)r[1]`
 * instead and is otherwise character-identical. ⚠ It is spelled with `+` and
 * `*` and NEVER with `|` and `<<`, so the whole specification stays inside
 * linear arithmetic (.memory/04-verus.md) -- ../spec.md's `why` says so, and
 * this line said `|`/`<<` until TASK_067 (TASK_066_REVIEW m6).
 *
 *   window = buf[off .. off+len)
 *   nrec        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   the record stream is (len-4)/2 little-endian 16-bit words, truncated to
 *   SCRATCH_W, decoded one word at a time into `sc`
 *
 *   record at word index i:
 *     words i, i+1   the 32-bit length `rlen`, low half first
 *     words i+2 ..   2*rlen payload words   (`rlen` counts 32-bit units)
 *
 *   acc = 0 ; i = 0 ; o = 0
 *   while o < nrec && i + 2 <= nw:          <<< ADDITIVE, and pinned that way
 *       room = (nw - i - 2) / 2
 *       if REC_LEN(sc+i) > room:  REC_SET_LEN(sc+i, room)     <<< THE CLAMP
 *       n = REC_LEN(sc+i)                                     <<< re-read
 *       for k in 0 .. 2*n:  acc = acc*31 + sc[i+2+k]
 *       i += 2 + 2*n ; o += 1
 *   return acc*31 + o
 *
 * **THE CLAMP IS THE BOUNDS ENFORCEMENT AND IT IS PRESENT IN BOTH C RUNGS.**
 * p38's C rung does not omit a check -- that is the shape ten other patterns
 * here already have. It writes the check, and the compiler is entitled to
 * ignore it: the clamp stores through `uint16_t` lvalues, the re-read loads
 * through a `uint32_t` lvalue, and under the type rule those cannot alias, so
 * the load may be answered from the value read *before* the clamp. The stale,
 * unclamped, attacker-controlled length then bounds the fold.
 *
 * Measured on this box (../NOTES.md 0), and it is the pattern's spine:
 *
 *   gcc 13.3.0  -O3     the clamp has no effect; the fold reads past `sc`
 *   clang 22.1.6 -O3    the clamp works; no out-of-bounds read
 *   either, -fno-strict-aliasing   the clamp works
 *
 * The compiler difference is not luck and it is not a version accident, and
 * the discriminator is narrower than "the same address": LLVM declines to
 * apply TBAA when **BasicAA can compute the OFFSET between the two accesses**
 * -- MustAlias is sufficient but not necessary. Measured on five variants of
 * one function (`x_mustalias`, ../NOTES.md 0d): a partial overlap that is
 * never MustAlias is still declined, and hiding only the offset behind an
 * opaque value -- same single base pointer -- makes clang exploit the
 * violation at every level from -O1. p38's own kernel is the PARTIAL case:
 * two 2-byte stores against one 4-byte load. Hand clang two pointers it
 * cannot relate and it exploits it too. (Second reason, from the shipped
 * listing: clang MERGES the two `uint16_t` clamp stores into one 32-bit store
 * where gcc emits two, so the value it forwards is type-consistent anyway.)
 *
 * Both C rungs take `buf_len` and both ignore it: p38's bound is the window's
 * and the scratch's, not the blob's. p47's, p12's, p06's, p14's, p10's and
 * p27's shape.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + x` is the
 * wrapping operation ../spec.md asks for with no special spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nrec` and every record byte are attacker data and are
 * the kernel's problem. */

/* The decode scratch, in WORDS. The record stream is truncated to this length,
 * which is a property of the parser and is in every rung and in model.py. */
#define SLB_P38_SCRATCH_W 256

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P38_KERNEL_H */
