#ifndef P11_KERNEL_H
#define P11_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p11: NUL-terminated string scan. One window holds a declared count of
 * packed, NUL-terminated strings; the kernel measures each one and folds its
 * bytes. CWE-125 via a MISSING SENTINEL -- the first pattern in this project
 * whose loop bound is not known before the loop runs. See ../README.md and
 * ../NOTES.md 0.
 *
 *   window = buf[off .. off+len)
 *   nstr        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   avail       = len - 4                        what actually ARRIVED
 *   strings follow, packed, each terminated by one 0 byte
 *
 *   acc = 0 ; p = 4
 *   for s in 0 .. nstr:
 *       q = p
 *       while q < len and buf[off + q] != 0: q += 1
 *                                           <<< THE SCAN. R1 omits `q < len`.
 *       slen = q - p
 *       h = 0
 *       for i in p .. q: h = h*31 + buf[off + i]
 *       acc = acc*31 + (h ^ slen)           u64, wrapping
 *       if q >= len: break                  <<< no terminator: the last string
 *       p = q + 1
 *       if p >= len: break
 *   return acc*31 + nstr
 *
 * **The bug is a loop that does not stop, and NOTHING IS COMPUTED WRONGLY.**
 * Every other bug this project models is an arithmetic mistake that produces a
 * bad index: p16 walks one step past a *length* whose subtraction wrapped, p17
 * computes a wrong-but-in-bounds *index* in signed arithmetic, p07 underflows an
 * *inclusive bound*. Here every index is correct, every subtraction is safe, and
 * the loop simply has no upper bound: it runs until it finds a sentinel, and if
 * the sentinel is not there it leaves the record, leaves the window, and leaves
 * the allocation.
 *
 * **The scan and the fold are two loops on purpose.** Fusing them
 * (`while (b != 0) h = h*31 + b;`) would delete the pattern: the length would
 * never materialise and the `strlen`/`memchr` idiom that R1 and R3 both want
 * would be foreclosed. `slen` is folded into the result, so a rung that finds a
 * different terminator cannot produce the same checksum.
 * `../NOTES.md` 1 measures that the split survives -O3 in every rung -- it is
 * checked on the disassembly, not assumed.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- `strlen()`. Bounded by the SENTINEL. THE BUG.
 *   c/kernel_hardened.c  R1h -- `memchr()` over the rest of the window.
 *                               Bounded by the WINDOW.
 *
 * **Why `memchr` and not `strnlen`.** `strnlen` is POSIX, not C99, and
 * `harness/build.py` compiles with `-std=c99` and defines no feature-test macro,
 * so `strnlen` is not declared and the file does not build (measured: clang
 * `call to undeclared function 'strnlen'`, gcc `-Wimplicit-function-declaration`).
 * `memchr` is C99 <string.h> and needs nothing. It is also the *closer* mirror of
 * what the Rust rungs do -- return the position of the terminator inside a span
 * of known length -- so R1h and R3 differ in library and not in shape.
 *
 * Both take `buf_len`, and that is the point: this API *has* the size. R1 is not
 * C being unable to stop, it is C code that had what it needed and trusted the
 * data instead. R1-vs-R1h is therefore what the bound costs inside one language
 * with the calling convention, the argument count and the register allocation all
 * held fixed (`.memory/02-bench-rules.md`, "The precondition must be
 * structural").
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `h*31 + b`,
 * `acc*31 + (h ^ slen)` and `acc*31 + nstr` are the wrapping operations
 * ../spec.md asks for with no special spelling. The only undefined behaviour
 * this rung can execute is the out-of-bounds read itself.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nstr` -- all 2^32 values of it -- and every byte of the
 * window are attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P11_KERNEL_H */
