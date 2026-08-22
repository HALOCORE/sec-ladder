#ifndef P47_KERNEL_H
#define P47_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p47: constant-time tag comparison. **The one pattern in this project whose
 * bug is not in the VALUE domain at all** -- every other `c/kernel.c` here
 * either reads outside an allocation or returns a wrong answer on some input,
 * and something in `harness/check.py` can see it. This one returns the right
 * answer on every input, is ASan-, UBSan- and Miri-clean, and satisfies the
 * `ensures` that rung 5 proves. Its defect is that the number of instructions
 * it executes is a function of the secret it is comparing.
 *
 *   window = buf[off .. off+len)
 *   ntag        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   tlen        = u32 LE at window byte 4        DECLARED. ATTACKER DATA.
 *   data_start  = 8
 *   comparison t occupies 2*tlen bytes: secret[tlen] then candidate[tlen]
 *   MATCH = 7      what an equal comparison folds     a compile-time constant
 *   MISS  = 251    what an unequal comparison folds   a compile-time constant
 *
 *   acc = 0 ; p = 8 ; o = 0
 *   while o < ntag && len - p >= 2*tlen:
 *       eq = COMPARE(buf+off+p, buf+off+p+tlen, tlen)   <<< THE TIMING LINE
 *       acc = acc*31 + (eq ? MATCH : MISS)
 *       p += 2*tlen ; o += 1
 *   return acc*31 + o
 *
 * **THE FOLD CANNOT SEE THE TAG BYTES.** It folds the VERDICT and the number
 * of comparisons performed, and nothing else. That is deliberate and it is
 * what makes the pattern's adversarial row possible: two windows with the
 * same verdict sequence and different first-mismatch positions produce the
 * *same checksum in every rung* and a *different instruction count in the
 * leaking ones*. A fold that mixed in the tag bytes would turn a timing row
 * into a correctness row and the pattern would be measuring something else.
 *
 * **THE BOUND IS IN EVERY RUNG, R1 INCLUDED.** `len - p >= 2*tlen` is written
 * subtraction-first (the additive `p + 2*tlen <= len` can overflow and Verus
 * rejects it) and `p <= len` is maintained by the guard itself, so the
 * subtraction cannot wrap. p47 models NO spatial bug: ten of the eighteen
 * patterns in this tree already do, and adding an eleventh here would confound
 * the axis p47 exists to measure.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- `memcmp(...) == 0`. THE BUG: memcmp stops at
 *                               the first differing byte, so the time it takes
 *                               is a function of where that byte is.
 *   c/kernel_hardened.c  R1h -- the or-accumulate `d |= sec[i] ^ cand[i]` over
 *                               every byte, then `d == 0`. Reads all `tlen`
 *                               bytes on every call whatever the data says.
 *
 * **AND THE MEASUREMENT SAYS THE OPTIMISER IS NOT THE ADVERSARY.**
 * `.memory/06-catalogue.md` predicted *"compiler may reintroduce a branch"*.
 * On this toolchain it does not: five accumulate spellings, gcc 13.3 and
 * clang 22.1.6, `-O1/-O2/-O3/-Os/-Oz`, inlined into a branching caller and
 * not, fixed length and runtime length -- not one grew a data-dependent exit.
 * ../NOTES.md 0 has the probes. The leak in `c/kernel.c` needs no optimiser
 * action at all; it is what `memcmp` means.
 *
 * Both take `buf_len` and both ignore it: p47's bound is the window's, not
 * the blob's. p12's, p06's, p14's, p10's and p27's shape.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + x` is the
 * wrapping operation ../spec.md asks for with no special spelling. **Neither C
 * rung executes any undefined behaviour on any input**, which is a first here.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `ntag`, `tlen` and every tag byte are attacker data and
 * are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P47_KERNEL_H */
