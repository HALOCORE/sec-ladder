/* p19 rung R1 -- idiomatic C, and it carries the bug.
 *
 * THE BUG, in one sentence: the decoder trusts the transition table it was
 * handed. There is no validation pass, so an entry naming a state that does not
 * exist becomes the next row index and `w[st*256 + b]` reads outside the blob.
 *
 * That is CVE-2026-23269's shape -- the AppArmor fix titled *"unpack_pdb DFA
 * bounds validation hardening"* -- and c/kernel_hardened.c is this file with
 * the pass that closes it, and nothing else.
 *
 * ⚠ **THE HARM IS SILENT ON A PLAIN BUILD.** The table lives in the driver's
 * heap payload buffer, so a bad entry reads other heap bytes and the program
 * exits 0 with a plausible checksum; only ASan and UBSan see it. A `.bss` table
 * would SIGSEGV instead, and that difference is a storage class, not a
 * property of the bug (../NOTES.md 0b -- the measurement that corrected
 * TASK_086's `exit 139` for this row).
 *
 * ⚠ **AND ONE ATTACKER BYTE DECIDES WHICH.** An entry of 8 -- the NEAREST
 * out-of-table state -- indexes row 8, which lands inside the window's own
 * message region: defined behaviour, no diagnostic, wrong answer. An entry of
 * 255 indexes 65 280 bytes past the window and leaves the allocation. Both are
 * shipped as inputs (`adversarial-confuse.bin`, `adversarial-oob.bin`) and the
 * pair is the pattern's sharpest row: **the same bug is a logic bug or a
 * memory-safety bug depending on one byte the attacker chooses.**
 *
 * Idiomatic-C check (the reviewer checklist asks): this is how a table-driven
 * decoder is written -- a `const uint8_t *` into the message, a `size_t` state,
 * one indexed load per byte. It is not Rust-in-C-syntax and it is not
 * pessimised: it is exactly `aa_dfa_match`'s inner loop with the compressed
 * base/check indirection removed.
 */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    const uint8_t *w = buf + off;
    uint64_t acc = 0;
    size_t p;
    size_t st = 0;

    if (len <= SLB_P19_TBL)
        return 0;

    /* >>> THE SAFETY LINE. c/kernel_hardened.c has the validation pass here
     * and this file does not. That omission is the whole of the bug. <<< */

    for (p = SLB_P19_TBL; p < len; p++) {
        st = w[st * 256 + w[p]];
        acc = acc * 31 + st;
    }
    return acc * 31 + st;
}
