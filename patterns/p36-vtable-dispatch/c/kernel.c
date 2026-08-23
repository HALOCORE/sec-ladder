/* p36 rung R1 -- a C99 bytecode interpreter with the classic dispatch-table
 * bug: the opcode is not checked against the table's extent.
 *
 * CWE-125 (out-of-bounds read) reaching CWE-691 (incorrect control flow). The
 * read is of a CODE POINTER and the program then calls it, so the attacker
 * picks the branch target rather than a value. This is the shape CFI exists
 * for, and it is the only harm class in this tree that is not a data harm.
 *
 * **WHAT THIS FILE OMITS, EXACTLY.** `c/kernel_hardened.c` writes
 *
 *     if (op < SLB_P36_NOPS)
 *         acc = TABLE[op](acc ^ arg);
 *     else
 *         acc = acc * 31 + SLB_P36_SENT;
 *
 * and this file writes the first arm unconditionally. Nothing else differs
 * between the two files -- `diff` them.
 *
 * ⚠ **A one-byte opcode makes 248 of 256 values out of table**, so the bug is
 * reachable by a single byte edit and `inputs/gen.py` ships exactly that as
 * `adversarial-oob.bin` and `adversarial-oobmax.bin`.
 *
 * **WHAT ACTUALLY HAPPENS, per cell, measured (../NOTES.md 0c).** On this box
 * `TABLE` is a `const` array of relocated pointers, so PIE puts it in
 * `.data.rel.ro`; the bytes after it are the GOT. Loading `TABLE[op]` for
 * `op >= 8` yields a value that is not a code address and the call faults:
 * **SIGSEGV on 8 of 8 plain cells** (gcc and clang, -O0/-O1/-O2/-O3), on both
 * out-of-table opcodes tested. It is deterministic, which is what the
 * catalogue's *"the harm is not reproducible"* triage doubted.
 *
 * ⚠ **It is NOT deterministic ACROSS BUILDS**, and that distinction is the
 * pattern's honest caveat. Under `-fsanitize=address,undefined` the redzones
 * move what is adjacent to `TABLE`, and one of the two adversarial opcodes then
 * **returns normally with a wrong answer and exit 0** while UBSan still
 * reports. So the adversarial row's declaration is `sanitizer_expect: "fires"`
 * -- *a sanitizer fires deterministically* -- and never *the harm is
 * identical*.
 *
 * The eight ops are one arithmetic operation each and uniform in shape; see
 * kernel.h for why. Unsigned overflow wraps by definition (C99 6.2.5p9). */
#include "kernel.h"

/* THE OP SET. One 64-bit constant and one of `^`, `+`, `-` each, so that no op
 * is materially dearer than another and the `sweep-mix*` band can hold the
 * opcode multiset fixed while varying only its order. Identical, constant for
 * constant, in every rung and in model.py. */
static uint64_t op0(uint64_t x) { return x ^ 0x9e3779b97f4a7c15ULL; }
static uint64_t op1(uint64_t x) { return x ^ 0xff51afd7ed558ccdULL; }
static uint64_t op2(uint64_t x) { return x + 0x2545f4914f6cdd1dULL; }
static uint64_t op3(uint64_t x) { return x + 0xc4ceb9fe1a85ec53ULL; }
static uint64_t op4(uint64_t x) { return x - 0x61c8864680b583ebULL; }
static uint64_t op5(uint64_t x) { return x - 0xbf58476d1ce4e5b9ULL; }
static uint64_t op6(uint64_t x) { return x ^ 0x94d049bb133111ebULL; }
static uint64_t op7(uint64_t x) { return x + 0x9e6c63d0676a9a99ULL; }

/* THE TABLE. `static ... (*const TABLE[N])(uint64_t)` is the textbook C
 * dispatch table; the `const` is what puts it in read-only memory, and it is
 * not what bounds the index. */
static uint64_t (*const TABLE[SLB_P36_NOPS])(uint64_t) = {
    op0, op1, op2, op3, op4, op5, op6, op7,
};

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t nrec, p, t;
    uint64_t acc = 0;
    uint8_t op, arg;

    (void)buf_len; /* p36's bound is the window's and the table's. */

    if (len < 4)
        return 0;
    nrec = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nrec == 0)
        return 0;

    p = 4;
    t = 0;
    while (t < nrec) {
        if (len - p < 2)
            break;
        op = buf[off + p];
        arg = buf[off + p + 1];
        p = p + 2;
        /* >>> THE MISSING SAFETY LINE. c/kernel_hardened.c tests
         * `op < SLB_P36_NOPS` here and folds SLB_P36_SENT otherwise. <<< */
        acc = TABLE[op](acc ^ (uint64_t)arg);
        t = t + 1;
    }
    return acc * 31 + (uint64_t)t;
}
