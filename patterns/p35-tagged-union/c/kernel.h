#ifndef P35_KERNEL_H
#define P35_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p35: a TAGGED UNION with DISCRIMINATED DISPATCH, driven by an op stream from
 * the file. CWE-843, access of a resource using an incompatible type.
 *
 * ⚠ **NOT A TEMPORAL ROW.** Nothing here is allocated, freed, recycled or
 * aliased. The storage is three local arrays that live for the whole call.
 * p35 was carried in `TASK_143`'s temporal re-adjudication list only because
 * its old refusal was VERUS-side; the axis is TYPE.
 *
 *   window = buf[off .. off+len)
 *   nops        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   op          = 2 bytes: c = opcode byte, a = operand byte   ALL ATTACKER DATA
 *   CELLS  = 8     tagged cells                  a compile-time constant
 *   BUDGET = 4     arena bytes, i.e. how many    a compile-time constant
 *                  pointer/double payloads can
 *                  be issued before the store
 *                  starts FAILING
 *   SENT   = 251   what a rejected op folds      a compile-time constant
 *   T_INT/T_PTR/T_DBL = 1/2/3                    the tag alphabet; 0 is UNSET
 *
 * THE C MECHANISM, AND WHY IT DUPLICATES NOTHING IN THE BUILT TREE
 * ---------------------------------------------------------------
 * A cell is a TAG plus a UNION:
 *
 *     struct p35_cell { uint8_t tag; union { uint64_t i; double d;
 *                                            uint8_t *p; } u; };
 *
 * `SET_INT` cannot fail. `SET_PTR` and `SET_DBL` take a byte out of a BUDGET
 * that can run out, so **the store has a FAILURE PATH** -- and `c/kernel.c`
 * publishes the TAG BEFORE THE PAYLOAD LANDS. When the budget is exhausted the
 * cell claims to hold a pointer (or a double) while the union still holds the
 * integer a previous `SET_INT` put there. `GET` then reads it AT THE CLAIMED
 * TYPE.
 *
 * **THE SAFETY LINE IS A STATEMENT ORDERING, AND THAT IS A THIRD SHAPE FOR THIS
 * TREE.** p27's safety line is a CONJUNCT, p13's is a STORE, p35's is a
 * SEQUENCING CONSTRAINT: `cells[idx].tag = ...;` moves from *before* the
 * `if (navail > 0)` to *inside* it, after the payload store, at TWO sites and
 * nowhere else. `../controls/safety_line.py` preprocesses the two shipped
 * kernels and measures that the difference is `+2 / -2` lines and a PURE
 * REORDER.
 *
 * TWO BUG CLASSES, ONE ORDERING, SELECTED BY THE INPUT
 * ---------------------------------------------------
 *   tag says PTR, payload is an int   `GET` DEREFERENCES an attacker-derived
 *                                     integer -> SIGSEGV; ASan reports it.
 *   tag says DBL, payload is an int   `GET` compares a garbage double -> a
 *                                     SILENT WRONG VALUE. Nothing reports it:
 *                                     not ASan, not UBSan, not gcc, not clang.
 *
 * That magnitude axis -- one ordering, one loud harm and one silent one -- is
 * the row. `../controls/detectors.py` licenses BOTH columns with a POSITIVE
 * CONTROL PER DETECTOR, because a control that fires only in ASan says nothing
 * about a UBSan column (`.memory/03-measurement.md` entry 14, one level down;
 * `.temp/mgr147/NOTES.md`).
 *
 * The nearest built rows are p19 (a state machine: no union, no reinterpretation
 * of one object's bytes at a second type), p16 (a TLV walk whose selector bounds
 * a LENGTH rather than choosing a TYPE) and p38 (the other TYPE row, whose bug
 * is C99 6.5p7 EFFECTIVE TYPE and whose harm is a MISCOMPILE; p35 executes no
 * aliasing violation at all -- reading a union member other than the last one
 * stored is defined in C99 6.2.6.1p7 / 6.5.2.3, and the shipped kernels are
 * built `-fstrict-aliasing` in the sanitizer stage without a word from either
 * compiler).
 *
 * WHAT EACH RUNG SPELLS, AND THE ONE PLACE THE RUNGS ARE NOT ISOMORPHIC
 * --------------------------------------------------------------------
 * ⚠⚠ **THE C UNION HOLDS A POINTER; THE FOUR RUST RUNGS HOLD THE ARENA
 * OFFSET.** This is disclosed rather than hidden, and the reason is
 * `.memory/01-ladder.md`'s own rule -- *a rung covered by an `identity` pin is
 * CHAINED TO THE PROVER*. R5 cannot hold a `*const u8` and dereference it
 * without `vstd::raw_ptr`'s `PointsTo` machinery, which is p27's and p29's row
 * and would put an allocation proof inside a type-confusion pattern; ../spec.md
 * pins `identity: unsafe == verus`, so R4 inherits the constraint and R2/R3
 * follow R4 so that all four Rust rungs are one algorithm. The value folded is
 * the same byte in every rung -- `*p` and `arena[o]` name the same object --
 * so every checksum agrees; what differs is the addressing mode. ../NOTES.md 5
 * measures it.
 *
 * The DBL payload is `(a % 2 == 0) ? 0.25 : 2.5` -- two LITERALS -- and not
 * `(double)a + 0.5`, for a reason that is also a measurement: at the pinned
 * Verus/vstd, `f64` ARITHMETIC and `f64` CASTS have no usable specification
 * (`vstd/std_specs/ops.rs`'s `add_req`; `vstd/float.rs`'s `float_cast_spec`,
 * *"(possibly) non-deterministic Rust cast"*), while an `f64` LITERAL verifies.
 * ../NOTES.md 6c has the four probes.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9), so `acc*31 + v` and
 * `a * 2654435761u` need no special spelling. */

#define P35_CELLS 8
#define P35_BUDGET 4
#define P35_SENT 251
#define P35_T_INT 1
#define P35_T_PTR 2
#define P35_T_DBL 3

struct p35_cell {
    uint8_t tag;
    union {
        uint64_t i;
        double d;
        uint8_t *p;
    } u;
};

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif
