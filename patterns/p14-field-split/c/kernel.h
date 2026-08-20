#ifndef P14_KERNEL_H
#define P14_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p14: delimiter-framed field splitter -- a `strtok`-shaped tokenizer over a
 * fixed scratch, writing one descriptor per field into a FIXED TABLE. One
 * window holds a declared count of lines; each line declares its length and
 * carries its bytes, and the delimiters inside those bytes are what decide how
 * many fields there are. See ../README.md, ../spec.md and ../NOTES.md 0.
 *
 *   window = buf[off .. off+len)
 *   nline       = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   line        = u32 LE llen ; llen bytes       ALL ATTACKER DATA
 *   SCR    = 64    the scratch's extent          a compile-time constant
 *   MAXTOK = 16    the field table's extent      a compile-time constant
 *   DELIM  = ','   the field separator           a compile-time constant
 *
 *   scr[SCR] = {0} ; tl[MAXTOK] = {0} ; acc = 0 ; p = 4
 *   for ln in 0 .. nline:
 *       if len - p < 4: break
 *       llen = u32le(buf[off+p]) ; p += 4
 *       m = min(llen, SCR)             <<< the CLAMP, present in EVERY rung
 *       if len - p < llen: break
 *       memcpy(scr, buf + off + p, m)  <<< bulk, in EVERY rung
 *       p += llen
 *       nt = 0 ; s = 0 ; i = 0
 *       while i <= m:
 *           if i == m || scr[i] == DELIM:
 *               if (nt == MAXTOK) break;   <<< THE SAFETY LINE. R1 omits THIS.
 *               tl[nt] = i - s ; nt++ ; s = i + 1
 *           i++
 *       cur = 0
 *       for j in 0 .. nt:
 *           acc = acc*31 + tl[j]
 *           for q in 0 .. tl[j]: acc = acc*31 + scr[cur+q]
 *           cur = cur + tl[j] + 1
 *       acc = acc*31 + nt
 *   return acc*31 + nline
 *
 * **THE BOUND IS A COUNT OF A BYTE VALUE, and that is what is new here.** Every
 * earlier bound in this project is a LENGTH -- of a buffer, of a record, of a
 * declared field. p14's overflowing loop is bounded by *how many commas the
 * attacker put in the line*, which is not declared anywhere and is not
 * derivable from any length: one 64-byte line can hold anywhere between 1 and
 * 65 fields. Every read and every write of `scr` is in bounds in this rung; the
 * out-of-bounds store is into the METADATA table, and its magnitude is set by
 * delimiter DENSITY.
 *
 * **THE LIBRARY CONTRACT DECIDES WHETHER A GIVEN INPUT IS DANGEROUS.**
 * `strtok(3)` COLLAPSES a run of delimiters into one separator and this rung
 * does not, so on `a,,,,,,,,,,,,,,,,z` the two spellings produce 2 fields and
 * 18 fields against the same 16-entry table. That is not a semantic curiosity:
 * it is the difference between a correct parse and a stack-buffer-overflow
 * WRITE, on byte-identical input. `adversarial-run17` is that input and
 * ../NOTES.md 0 has the measurement. What collapse does NOT do is remove the
 * need for the guard -- an ALTERNATING line, `a,a,a,...`, has no runs at all
 * and produces 32 fields under both spellings (`adversarial-alt33`).
 *
 * **What this rung KEEPS is as important as what it drops.** It keeps the clamp
 * `m = min(llen, SCR)`, so the copy is bounded and every read of the source is
 * in bounds; it keeps both cursor guards, so `p` never leaves the window; the
 * scan is bounded by `i <= m` in every rung, so it is not p11's missing
 * terminator. The only thing missing is the one line that asks whether the
 * field table is full. That is what makes R1-vs-R1h the cost of the field-count
 * bound and nothing else.
 *
 * The guards are written subtraction-first (`len - p < 4`) rather than
 * additively (`p + 4 > len`) in all seven rungs. `p <= len` is maintained by the
 * guards themselves, so the subtraction cannot wrap; the additive form can
 * overflow `usize` for a window at the top of the address space and Verus
 * rejects it. p07's lesson, on a third pattern.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no field-count bound. THE BUG.
 *   c/kernel_hardened.c  R1h -- `if (nt == MAXTOK) break;`, and that one line is
 *                               the whole difference.
 *
 * Both take `buf_len`, and both ignore it: p14's bound is not the source
 * buffer's length, it is the FIELD TABLE's extent, a compile-time constant in
 * every rung. p12's and p06's shape.
 *
 * **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
 * every call must return the same value. That is not a stylistic preference
 * here, it is what excludes the catalogue's guessed bug class: a `strtok`-style
 * IN-PLACE tokenizer writes NUL over the delimiters of the buffer it is handed,
 * so its second call over the same window returns a different answer and it is
 * not a function of its arguments at all. Measured, both compilers,
 * ../NOTES.md 0. The per-call scratch copy is what makes a tokenizer legal in
 * this benchmark, and it deletes the in-place mutation as a side effect.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + scr[...]`,
 * `acc*31 + nt` and the return expression are the wrapping operations ../spec.md
 * asks for with no special spelling. The only undefined behaviour this rung can
 * execute is the out-of-bounds store into `tl`, and the out-of-bounds LOAD from
 * `tl` that the fold then performs through it.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nline`, `llen`, and every byte of the window -- including
 * every delimiter in it -- are attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P14_KERNEL_H */
