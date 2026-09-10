#ifndef PH16_KERNEL_H
#define PH16_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph16: run one `stream_select()` frame's worth of `stream_array_to_fd_set`
 * and fold the three `fd_set`s it filled.
 *
 *   window = [u16 ctl][u16 split_r][u16 split_w][u16 e[m]]   m = (len - 6) / 2
 *
 *   stream_select's frame        fd_set rfds, wfds, efds;  int max_fd = 0;
 *   three calls                  stream_array_to_fd_set(<run>, &Xfds, &max_fd)
 *   the u64                      fold(sets, max_fd, rfds, wfds, efds)
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0 narrowed. THE BUG (CRASH-098).
 *   c/kernel_hardened.c   R1h -- the same file plus the POSIX branch of
 *                                99e290f882c9 (Wez Furlong, 2004-09-17,
 *                                "Bug #24189: possibly unsafe select(2)
 *                                usage"), which is THREE guards and not one:
 *                                  (a) `&& this_fd >= 0` at the call site
 *                                  (b) PHP_SAFE_FD_SET's `if (fd < FD_SETSIZE)`
 *                                  (c) PHP_SAFE_MAX_FD's clamp of `max_fd`,
 *                                      in the CALLER's frame
 *                                See kernel_hardened.c:1-120 and ../spec.md
 *                                `idiom.required[3]`.
 *
 * ============================================================================
 * ⚠⚠⚠ `_FORTIFY_SOURCE` IS TURNED OFF HERE AND THAT IS NOT HOUSEKEEPING
 * ============================================================================
 * Ubuntu 24.04's gcc spec adds `-D_FORTIFY_SOURCE=3` whenever it is
 * optimising, and glibc's fortified `FD_SET` is `__FD_ELT` -> `__fdelt_chk`,
 * which is **the exact bound this row is about**. Measured
 * (`.tasks-php/TASK_PHP_025_REPORT.md` §3, `.temp/php25/fortify_probe.c`):
 *
 *     gcc -O0            _FORTIFY_SOURCE undefined   FD_SET(2048) survives
 *     gcc -O3            _FORTIFY_SOURCE = 3         *** bit out of range
 *                                                    0 - FD_SETSIZE on fd_set
 *                                                    ***: terminated
 *     gcc -O3 + #undef   _FORTIFY_SOURCE = 0         FD_SET(2048) survives
 *     clang -O0/-O3      undefined                   FD_SET(2048) survives
 *
 * and on BENIGN, in-range indices the check costs **14.87 Ir per `FD_SET`** --
 * measured ON THIS ROW, `controls/fortify.py`: 92 605 764 -> 148 709 085 Ir on
 * `small.bin` over 3 773 157 `FD_SET`s, i.e. +60.6 % whole-program.
 * ⚠ A standalone probe (`.temp/php25/fortify_probe.c`, a tight loop over a
 * stack `fd_set` and nothing else) gives **7.01**, and the first draft of this
 * comment quoted THAT. It is a different code shape and it is not this row's
 * number; the row's own is the one above. So without the `#undef`
 * the `c-gcc-O3` cells would be a HARDENED rung wearing R1's label, carrying a
 * bounds-check tax a reader would attribute to C-versus-Rust, while
 * `c-clang-O3` carried none. PHP 5.0.0 (2004) was built with no such thing.
 * `controls/fortify.py` measures both configurations rather than asserting
 * this; ../spec.md `provenance.divergences` itemises it.
 *
 * ============================================================================
 * ⚠⚠ WHAT THE KERNEL DOES *NOT* TAKE, AND WHY THAT IS THE ROW
 * ============================================================================
 * `stream_array_to_fd_set` receives `fd_set *fds` and NOTHING that says how
 * big it is: the bound is `FD_SETSIZE`, a compile-time constant of the
 * platform, and `:541` simply never mentions it. Handing this kernel a
 * separate capacity would be modelling a different bug. The three `fd_set`s
 * live in the CALLER's frame (`streamsfuncs.c:658`) and that is why an
 * over-write lands in a live neighbouring object rather than in a redzone --
 * see `../NOTES.md` §3, the row's oracle.
 *
 * The caller must guarantee `off + len <= buf_len` and `len >= 8`; that is the
 * structural precondition every rung shares and no rung checks (R5 proves it
 * at the call site instead). Everything else -- the split of the window into
 * three arrays, every entry's tag and every index -- is attacker data and is
 * the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* PH16_KERNEL_H */
