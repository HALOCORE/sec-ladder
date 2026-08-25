#ifndef P19_KERNEL_H
#define P19_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p19: a byte-at-a-time protocol decoder driven by a transition table that
 * arrives IN THE INPUT.
 *
 * ⚠ **SAY THE UNFLATTERING THING FIRST: the BUG CLASS is this tree's
 * THIRTEENTH `index >= len`.** p01, p02, p03, p05, p07, p11, p12, p13, p14,
 * p16, p17 and p36 are all *"an index or a length is not checked against a
 * buffer"*, and so is this. p36 shipped the twelfth and said so; this is the
 * thirteenth and says so.
 *
 * ⚠⚠ **AND THE MEMORY-UNSAFE FRAMING IS CONDITIONAL. THE CONDITION IS NAMED
 * AND IT IS PART OF THE CONTRACT** (../NOTES.md 0). A textbook "state
 * confusion" bug is a LOGIC bug with no out-of-bounds access at all, and p19
 * escapes that only because BOTH of the following hold, each settled by a run
 * rather than by argument:
 *
 *   1. **the transition table is LOADED DATA, not a program constant.** With a
 *      tool-generated table (flex/ragel/re2c) every entry is in range by
 *      construction, so `st` can never leave `[0, NST)` -- exhaustively over
 *      all 2048 (state, byte) pairs and over 1e6 adversarial bytes
 *      (../NOTES.md 0a, run A). The OOB is UNREACHABLE and the row would die.
 *   2. **the decoder dispatches by INDEXING the table, not by `switch`.** The
 *      identical bug written as a `switch (st)` falls to `default`: a wrong
 *      answer, no memory event, ASan and UBSan clean (../NOTES.md 0a, run C).
 *
 * Both hold of real DFA decoders. The precedent this pattern is modelled on is
 * the Linux kernel's AppArmor policy engine, `security/apparmor/match.c`, whose
 * hot loop is
 *
 *     pos = base_idx(base[state]) + (u8) *str++;
 *     if (check[pos] == state) state = next[pos]; else state = def[state];
 *
 * -- four unchecked loads -- licensed by `verify_dfa()` having walked the whole
 * unpacked table ONCE at policy load:
 *
 *     for (i = 0; i < state_count; i++)
 *         if (DEFAULT_TABLE(dfa)[i] >= state_count) { pr_err(...); goto out; }
 *     for (i = 0; i < trans_count; i++) {
 *         if (NEXT_TABLE(dfa)[i]  >= state_count) goto out;
 *         if (CHECK_TABLE(dfa)[i] >= state_count) goto out;
 *     }
 *
 * The tables come from a userspace-supplied binary policy blob, and getting
 * that validator wrong is a live CVE class. THE ONE THIS PATTERN MODELS is
 * CVE-2026-23407 *"apparmor: fix missing bounds check on DEFAULT table in
 * verify_dfa()"*, whose description is p19's bug verbatim: an unvalidated
 * DEFAULT_TABLE entry used as an array index, which "causes both out-of-bounds
 * reads and writes".
 *
 * A neighbouring CVE in the same file and the same validator, cited for the
 * CLASS and expressly NOT for the shape: CVE-2026-23269 *"apparmor: validate
 * DFA start states are in bounds in unpack_pdb"* -- an untrusted START state,
 * which p19 does not model at all because its walk starts at st = 0 by
 * construction. An earlier version of this comment gave that CVE a PARAPHRASED
 * title inside quotation marks; the title above is the real one
 * (TASK_087_REVIEW major 3).
 *
 * **So "validate the whole table once, then index it unchecked" is not a
 * benchmark contrivance -- it is the shipped kernel idiom, and it is exactly
 * this pattern's R4/R5 rung.**
 *
 * `c/kernel.c` omits the validation pass entirely: the "trusted table"
 * assumption. `c/kernel_hardened.c` is byte-for-byte the same file with the
 * pass restored, and it is the only difference between them.
 *
 * Window layout (../spec.md):
 *
 *     byte 0    .. 2048   the transition table, NST rows of 256   ATTACKER DATA
 *     byte 2048 .. len    the message                             ATTACKER DATA
 *
 *     NST = 8       the decoder's FIXED table capacity, a compile-time
 *                   constant in every rung -- the array the loaded table has to
 *                   fit into, exactly as AppArmor's `state_count` bounds its
 *                   unpacked tables
 *     TBL = NST*256 = 2048
 *     REJ           what an invalid table folds to
 *
 *     if len <= TBL:                       return 0
 *     for i in 0 .. TBL:                            <<< THE SAFETY LINE
 *         if w[i] >= NST:   return REJ              <<< c/kernel.c omits this
 *     st = 0 ; acc = 0
 *     for p in TBL .. len:
 *         st  = w[st*256 + w[p]]                    <<< THE TRANSITION
 *         acc = acc*31 + st
 *     return acc*31 + st
 *
 * **THE FOLD IS ONE MULTIPLY AND ONE ADD PER BYTE, ON PURPOSE.** The finding is
 * the table lookup and the invariant that licenses it, not the arithmetic
 * around it; a heavier fold would drown the one instruction that separates
 * safe-tuned from unsafe.
 *
 * `st` is LOOP-CARRIED AND DATA-DEPENDENT, and that is the whole cost
 * mechanism: no bounds check on `w[st*256 + b]` can be hoisted out of the
 * loop, and the check's exit edge forecloses the 4x unroll the unchecked
 * spelling gets. Measured: the checked fold body is 15 instructions for one
 * byte, the unchecked one 35 for four (../NOTES.md 8).
 *
 * Both C rungs take `(buf, off, len)` and have no blob length to check --
 * p01's asymmetry: the length is the thing C does not have. Do not "fix" it
 * with a dead `buf_len`; that would be Rust-in-C-syntax.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + st` is the
 * wrapping operation ../spec.md asks for with no special spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). Every byte of the table and of the message is attacker
 * data and is the kernel's problem. */

/* The decoder's table capacity. A compile-time constant in every rung and in
 * model.py: the decoder has a fixed number of states, and the loaded table has
 * to fit in them. */
#define SLB_P19_NST 8

/* Bytes of transition table: NST rows of 256 columns, one per input byte. */
#define SLB_P19_TBL (SLB_P19_NST * 256)

/* What an invalid table folds to. A compile-time constant in every rung. */
#define SLB_P19_REJ 0xD1B54A32D192ED03ULL

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* P19_KERNEL_H */
