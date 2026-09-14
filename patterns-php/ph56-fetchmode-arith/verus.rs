//! ph56 rung R5 -- unsafe + Verus.
//!
//! Same exec code as `unsafe.rs`, plus the proof that licenses it. What is
//! proved, and it is a VALUE postcondition rather than a memory-safety-only
//! retreat:
//!
//!     requires  off + len <= buf@.len()
//!     ensures   r == ph56_fold(buf@, off as int, len as int)
//!
//! ⭐ **ONE PRECONDITION, AND THAT IS A MEASUREMENT.** `ph55`'s kernel needs
//! three -- `16 <= len` and `len <= 8 * MAX_OPS` as well -- because its decoder
//! writes `nops - 2` and its op_array has no clamp. This one needs NEITHER:
//! `nstmt` is clamped to `MAX_STMT` in the code and the statement loop breaks on
//! `nops + 1 + chain > MAX_OPS`, so the bounds are established rather than
//! assumed. ⚠ It was NOT designed that way: the first draft carried all three,
//! copied from `ph55`, and **the gate's own `req-mut` stage deleted each one and
//! found the file still verified 66/0** -- `[req-mut] kernel requires[1] is NOT
//! load-bearing`, and the same for `requires[2]`. They are gone because
//! measurement said they were decoration. `../NOTES.md` §11.8.
//!
//! `ph56_fold` is PHP 5.0.0's compiler-plus-executor with `1e708a5aeb30`
//! applied, spelled as recursive spec functions -- `c_stmt`, `parsed`,
//! `compiled`, `s_fetch`, `e_step`, `e_run`, `fold_*` -- and `model.py`
//! re-derives the same `u64` from a different decomposition.
//!
//! ⚠⚠⚠ **THE OBLIGATION THIS ROW IS ABOUT IS `operand_present`, AND IT IS ABOUT
//! THE OPERAND AND NOT ABOUT THE DISPATCH TABLE.**
//!
//!     operand_present(ops, n)  ==  "for every j < n, an opline whose opcode is
//!                                   ZEND_ISSET_ISEMPTY_DIM_OBJ carries an op2
//!                                   that is PRESENT -- IS_CONST or IS_VAR, and
//!                                   never IS_UNUSED"
//!
//! It is the loop invariant of the compile pass, it is what discharges
//! `zunwrap`'s `requires t.is_some()`, and **it is exactly the invariant
//! `zend_do_end_variable_parse`'s `case BP_VAR_IS:` arm breaks at 5.0.0**.
//! ⭐ Note what it is NOT: it is not "every opcode has a handler". Every opcode
//! this compiler can emit HAS a handler -- that is `../NOTES.md` §7, and it is
//! the whole difference from `ph55`. What is missing is not the handler but the
//! OPERAND the handler reads.
//!
//! ⭐⭐ **AND IT IS ESTABLISHED BY THE EMITTER, NOT BY THE EXECUTOR.** The
//! executor's `ZEND_ISSET_ISEMPTY_DIM_OBJ` arm reads op2 through `get_zval_ptr`
//! and dereferences the result with nothing in between (`zend_execute.c:3961`
//! then `:3973`); it never tests. `do_end_variable_parse`'s `BP_VAR_IS` guard --
//! `1e708a5aeb30`'s three lines, which are `BP_VAR_R`'s own guard copied across
//! -- is the only thing that makes the read sound. **Delete those three lines
//! and this file does not verify**, which is `controls/negatives.py --emit r1`.
//!
//! ⭐⭐⭐ **THAT IS THE `ph55` PAIRING'S R5 HALF, AND IT MAKES THE FAMILY n = 2.**
//! `ph55`'s `ok_from` and `ph56`'s `operand_present` are the same shape: a
//! property the EMITTER establishes and the EXECUTOR relies on without testing.
//! `ph55`'s is about the PROGRAM COUNTER, `ph56`'s is about the OPERAND
//! CONTRACT. `../NOTES.md` §3 and §11.
//!
//! ⚠ **WHERE `ph55` HIT A TYPE-LEVEL VERUS REFUSAL, THIS ROW DOES NOT.**
//! `ph55`'s dispatch is a call through a function pointer stored in each
//! instruction, and Verus answers `The verifier does not yet support the
//! following Rust feature: function pointer types` -- a refusal no
//! `external_body` wrapper fixes, which forced `Option<u8>` + `match` on all
//! four of that row's Rust rungs. `ph56` dispatches with a `switch` on the
//! opcode, because every opcode it emits has a handler, so no substitution was
//! forced and none was made. **That is a finding about the two rows' costs, not
//! a claim that either is better.** `../NOTES.md` §7.
//!
//! The unchecked classes rest on four independent facts, and `../NOTES.md` §11
//! keeps them apart:
//!
//!   * `zunwrap(offset)` rests on `operand_present` -- the 2004 patch's own
//!     invariant, and the only one of the four that is about PHP.
//!   * `bget(win, ..)` rests on the driver's `off + len <= buf@.len()`.
//!   * `oget/oset(ops, ..)` rests on `nops <= MAX_OPS`, i.e. on `c/main.c`'s
//!     `stride_w <= 512` and on `MAX_OPS == 2 * MAX_STMT`.
//!   * `sget/sset`, `tget/tset`, `nget/nset` rest on arithmetic -- `% NVAR`,
//!     `% MAX_STMT`, `% NSLOT` -- and on nothing about the interpreter.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`, without which `off + len` cannot be shown not
// to overflow. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64` for the
// driver's multiply-shift barrier bound; the mul group is what the window-offset
// bound `k * stride + stride <= n_blob` needs.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py. See ../spec.md for why each is what it is.

/// Statement records per window. `c/main.c`'s `stride_w <= 512` is the same
/// bound in the driver, outside every measured loop.
pub const MAX_STMT: usize = 64;
/// A chained statement (`$a[][d]`) emits two oplines, so the op_array is twice
/// the record count.
pub const MAX_OPS: usize = 128;   // 2 * MAX_STMT

pub const NVAR: usize = 8; // CV slots
pub const DIM: usize = 4; // elements per array

pub const UNINIT: u16 = 0; // EG(uninitialized_zval) -- THE GLOBAL THE APPEND TAKES
pub const ERR: u16 = 1; // EG(error_zval)
pub const VAR_BASE: usize = 2;
pub const ARR_BASE: usize = 10;   // VAR_BASE + NVAR
pub const NSLOT: usize = 42;      // ARR_BASE + NVAR * DIM

pub const IS_NULL: u8 = 0;
pub const IS_LONG: u8 = 1;
pub const IS_ARRAY: u8 = 2;
pub const IS_STRING: u8 = 3;

// `znode.op_type` -- zend_compile.h:285-288, upstream's own bit values, because
// `IS_UNUSED` is the value the guard this row is about tests for.
pub const T_CONST: u8 = 1; // IS_CONST  (1<<0)
pub const T_VAR: u8 = 4; // IS_VAR    (1<<2)
pub const T_UNUSED: u8 = 8; // IS_UNUSED (1<<3)

// The six access modes -- zend_compile.h:756-762, upstream's own values.
pub const BP_R: u8 = 0;
pub const BP_W: u8 = 1;
pub const BP_RW: u8 = 2;
pub const BP_IS: u8 = 3;
pub const BP_FUNC_ARG: u8 = 5;
pub const BP_UNSET: u8 = 6;

// ⭐⭐ THE REAL OPCODE NUMBERS, AND THEY ARE LOAD-BEARING. zend_compile.h:636-638
// says, in upstream's own words and exclamation mark: *the following 18 opcodes
// are 6 groups of 3 opcodes each, and must remain in that order!* The compiler
// selects a mode by ARITHMETIC over exactly that layout, so keeping the literal
// values means this row's arithmetic is upstream's arithmetic.
pub const FETCH_DIM_R: u8 = 81;
pub const FETCH_W: u8 = 83;
pub const FETCH_DIM_W: u8 = 84;
pub const FETCH_OBJ_W: u8 = 85;
pub const FETCH_DIM_RW: u8 = 87;
pub const FETCH_IS: u8 = 89;
pub const FETCH_DIM_IS: u8 = 90;
pub const FETCH_OBJ_IS: u8 = 91;
pub const FETCH_DIM_FUNC_ARG: u8 = 93;
pub const FETCH_DIM_UNSET: u8 = 96;
pub const ISSET_ISEMPTY_VAR: u8 = 114;
pub const ISSET_ISEMPTY_DIM_OBJ: u8 = 115;
pub const ISSET_ISEMPTY_PROP_OBJ: u8 = 148;

pub const MODES: [u8; 6] = [BP_R, BP_W, BP_RW, BP_IS, BP_FUNC_ARG, BP_UNSET];
pub const BASES: [u8; 3] = [FETCH_W, FETCH_DIM_W, FETCH_OBJ_W];
pub const OP2T: [u8; 3] = [T_UNUSED, T_CONST, T_VAR];

/// `zend_op`, narrowed.
#[derive(Clone, Copy)]
pub struct Op {
    pub opcode: u8,
    pub op1_type: u8,
    pub op2_type: u8,
    pub ext: u8,
    pub op1: u16,
    pub op2: u16,
    pub result: u16,
}

pub const ZERO_OP: Op =
    Op { opcode: 0, op1_type: 0, op2_type: 0, ext: 0, op1: 0, op2: 0, result: 0 };

/// `zval`. ⚠ The FIELD ORDER is upstream's so that `c/kernel.c`'s fault lands
/// on upstream's own offset; Rust has no pointer to fault through, but the two
/// rungs must fold the same fields in the same order or the gate's cross-rung
/// checksum would be comparing different functions.
#[derive(Clone, Copy)]
pub struct Zv {
    pub lval: u64,
    pub value_hi: u64,
    pub refcount: u32,
    pub ty: u8,
    pub is_ref: u8,
}

pub const ZERO_ZV: Zv = Zv { lval: 0, value_hi: 0, refcount: 0, ty: 0, is_ref: 0 };

// ------------------------------------------------------------------ spec ----

/// The three decode tables, as functions. Each is the table the exec code
/// indexes, written out, so the exec `MODES[x % 6]` and this `if`-chain are the
/// same value by definition rather than by a lemma.
pub open spec fn s_mode_of(b: u8) -> u8 {
    let m = b % 6;
    if m == 0 { BP_R } else if m == 1 { BP_W } else if m == 2 { BP_RW } else if m == 3 {
        BP_IS
    } else if m == 4 { BP_FUNC_ARG } else { BP_UNSET }
}

pub open spec fn s_base_of(b: u8) -> u8 {
    let m = (b & 0x7F) % 3;
    if m == 0 { FETCH_W } else if m == 1 { FETCH_DIM_W } else { FETCH_OBJ_W }
}

pub open spec fn s_o2t_of(b: u8) -> u8 {
    let m = b % 3;
    if m == 0 { T_UNUSED } else if m == 1 { T_CONST } else { T_VAR }
}

pub open spec fn s_var_of(o: u16) -> int {
    VAR_BASE + (o as int) % (NVAR as int)
}

pub open spec fn s_tmp_of(o: u16) -> int {
    (o as int) % (MAX_STMT as int)
}

/// ⛔⛔ **THE DEFECT SITE, AS A PREDICATE.** `zend_do_end_variable_parse`'s
/// `E_COMPILE_ERROR` test -- `opline->opcode == ZEND_FETCH_DIM_W &&
/// opline->op2.op_type == IS_UNUSED` -- and WHICH ARMS ASK IT.
///
/// ⭐ At 5.0.0 the `BP_VAR_IS` line below is absent and the arm falls straight
/// through to `opline->opcode += 6;`. `1e708a5aeb30` is the three lines that put
/// it there, and they are `BP_VAR_R`'s own guard copied across, character for
/// character. **This one disjunct is R1 -> R1h.**
pub open spec fn s_parse_ok(o: Op, ty: u8) -> bool {
    if ty == BP_R || ty == BP_IS || ty == BP_UNSET {
        !(o.opcode == FETCH_DIM_W && o.op2_type == T_UNUSED)
    } else {
        true
    }
}

/// The mode arithmetic itself -- `zend_compile.c:756-774`, six arms, upstream's
/// own deltas over `zend_compile.h:636-638`'s six-groups-of-three layout.
pub open spec fn s_parse_op(o: Op, ty: u8) -> Op {
    if ty == BP_R {
        Op { opcode: o.opcode.wrapping_sub(3), ..o }
    } else if ty == BP_W {
        o
    } else if ty == BP_RW {
        Op { opcode: o.opcode.wrapping_add(3), ..o }
    } else if ty == BP_IS {
        Op { opcode: o.opcode.wrapping_add(6), ..o }
    } else if ty == BP_FUNC_ARG {
        Op { opcode: o.opcode.wrapping_add(9), ext: 0, ..o }
    } else if ty == BP_UNSET {
        Op { opcode: o.opcode.wrapping_add(12), ..o }
    } else {
        o
    }
}

/// `zend_do_isset_or_isempty` -- zend_compile.c:3225-3239. THE SECOND REWRITE,
/// and it is why reading `:763` alone names the wrong harm.
pub open spec fn s_isset_rewrite(o: Op) -> Op {
    let oc = if o.opcode == FETCH_IS {
        ISSET_ISEMPTY_VAR
    } else if o.opcode == FETCH_DIM_IS {
        ISSET_ISEMPTY_DIM_OBJ
    } else if o.opcode == FETCH_OBJ_IS {
        ISSET_ISEMPTY_PROP_OBJ
    } else {
        o.opcode
    };
    Op { opcode: oc, ext: 1, ..o }
}

/// ⭐⭐⭐ **THE ROW'S OBLIGATION.** An opline whose handler READS op2 is only ever
/// emitted with op2 PRESENT. `zend_isset_isempty_dim_prop_obj_handler` reads it
/// at `zend_execute.c:3961` and dereferences the result at `:3973` with nothing
/// in between, so this is the whole of what makes that read sound.
pub open spec fn operand_present(ops: Seq<Op>, n: int) -> bool {
    forall|j: int|
        0 <= j < n ==> (#[trigger] ops[j]).opcode == ISSET_ISEMPTY_DIM_OBJ ==> (ops[j].op2_type
            == T_CONST || ops[j].op2_type == T_VAR)
}

/// The compiler's state: the op_array, how much of it is live, the checksum and
/// the two ways out (`zend_bailout()` and the frame array's capacity).
pub struct Cs {
    pub ops: Seq<Op>,
    pub nops: int,
    pub acc: u64,
    pub bail: u8,
    pub stop: bool,
}

/// The inner `while (le)` walk of `zend_do_end_variable_parse` -- :748-779. One
/// fetch-list element per turn, and at most two elements per statement.
pub struct Ps {
    pub ops: Seq<Op>,
    pub acc: u64,
    pub bail: u8,
    pub k: int,
}

pub open spec fn parsed(ps: Ps, n: int, ty: u8) -> Ps
    decreases n - ps.k,
{
    if ps.k >= n || ps.k < 0 || ps.bail != 0 {
        ps
    } else {
        let o = ps.ops[ps.k];
        if !s_parse_ok(o, ty) {
            // zend_bailout() -- E_COMPILE_ERROR leaves the whole compile and
            // nothing runs. The exec rung also zeroes `nops`; `compiled` below
            // is what records that.
            Ps { ops: ps.ops, acc: ps.acc, bail: 1, k: ps.k }
        } else {
            let o2 = s_parse_op(o, ty);
            parsed(
                Ps {
                    ops: ps.ops.update(ps.k, o2),
                    acc: ps.acc.wrapping_mul(31).wrapping_add(o2.opcode as u64),
                    bail: 0,
                    k: ps.k + 1,
                },
                n,
                ty,
            )
        }
    }
}

/// One statement record -- decode, emit, run the mode switch over every emitted
/// opline, then rewrite the LAST one if the statement was an `isset()`.
pub open spec fn c_stmt(win: Seq<u8>, cs: Cs, i: int) -> Cs {
    let b0 = 8 * i;
    let mode = s_mode_of(win[b0]);
    let b1 = win[b0 + 1];
    let chain: int = if (b1 & 0x80) != 0 { 1int } else { 0int };
    let base = s_base_of(b1);
    let o2t = s_o2t_of(win[b0 + 2]);
    let op2 = win[b0 + 3] as u16;
    let op1 = (win[b0 + 4] as u16) | ((win[b0 + 5] as u16) << 8);
    let res = (win[b0 + 6] as u16) | ((win[b0 + 7] as u16) << 8);
    let first = cs.nops;
    if first + 1 + chain > MAX_OPS as int {
        Cs { ops: cs.ops, nops: cs.nops, acc: cs.acc, bail: cs.bail, stop: true }
    } else {
        let ops1 = if chain == 1 {
            cs.ops.update(
                first,
                Op {
                    opcode: FETCH_DIM_W,
                    op1_type: T_CONST,
                    op2_type: T_UNUSED,
                    ext: 0,
                    op1: op1,
                    op2: 0,
                    result: res.wrapping_add(1),
                },
            )
        } else {
            cs.ops
        };
        let last = first + chain;
        let ops2 = ops1.update(
            last,
            Op {
                opcode: base,
                op1_type: T_CONST,
                op2_type: if base == FETCH_W { T_UNUSED } else { o2t },
                ext: 0,
                op1: if chain == 1 { res.wrapping_add(1) } else { op1 },
                op2: op2,
                result: res,
            },
        );
        let n2 = last + 1;
        let ps = parsed(Ps { ops: ops2, acc: cs.acc, bail: 0, k: first }, n2, mode);
        if ps.bail != 0 {
            Cs { ops: ps.ops, nops: 0, acc: ps.acc, bail: ps.bail, stop: false }
        } else if mode == BP_IS {
            let o2 = s_isset_rewrite(ps.ops[n2 - 1]);
            Cs {
                ops: ps.ops.update(n2 - 1, o2),
                nops: n2,
                acc: ps.acc.wrapping_mul(31).wrapping_add(o2.opcode as u64),
                bail: 0,
                stop: false,
            }
        } else {
            Cs { ops: ps.ops, nops: n2, acc: ps.acc, bail: 0, stop: false }
        }
    }
}

/// THE COMPILER'S ONE PASS.
pub open spec fn compiled(win: Seq<u8>, nstmt: int, i: int, cs: Cs) -> Cs
    decreases nstmt - i,
{
    if i >= nstmt || i < 0 || cs.stop || cs.bail != 0 {
        cs
    } else {
        compiled(win, nstmt, i + 1, c_stmt(win, cs, i))
    }
}

pub open spec fn init_cs() -> Cs {
    Cs {
        ops: Seq::new(MAX_OPS as nat, |i: int| ZERO_OP),
        nops: 0,
        acc: 0,
        bail: 0,
        stop: false,
    }
}

/// `_get_zval_ptr`'s IS_UNUSED arm -- zend_execute.c:118-121, an explicit
/// `return NULL;`. In Rust it is an explicit `None`, and this predicate is what
/// says which operands have one.
pub open spec fn s_gzp_some(op_type: u8) -> bool {
    op_type == T_CONST || op_type == T_VAR
}

/// `_get_zval_ptr` -- zend_execute.c:88-125. ⚠ The `else` arm returns `0int`
/// and NOT a slot the program can observe: `operand_present` is what makes it
/// unreachable from any opline that reads op2, and `model.py` raises
/// `NullOperand` there instead. The two agree on every reachable call, which is
/// what the gate's `ensures` evaluation measures.
pub open spec fn s_gzp(ts: Seq<u16>, op_type: u8, op: u16) -> int {
    if op_type == T_CONST {
        s_var_of(op)
    } else if op_type == T_VAR {
        (ts[s_tmp_of(op)] as int) % (NSLOT as int)
    } else {
        0int
    }
}

/// `zend_fetch_dimension_address`'s result -- the store, the next-free indices,
/// `zend_bailout()` and the slot.
pub struct Fr {
    pub slots: Seq<Zv>,
    pub anext: Seq<u16>,
    pub bail: u8,
    pub r: u16,
}

/// `zend_fetch_dimension_address` -- zend_execute.c:896-975. The IS_ARRAY arm's
/// `op2->op_type == IS_UNUSED` branch is :935-943 and it is THE APPEND -- which
/// is what `$a[] = 1` is implemented by, so it is not a defect on its own.
/// ⭐ The STRING container IS guarded, at :963-964.
pub open spec fn s_fetch(
    slots: Seq<Zv>,
    anext: Seq<u16>,
    bail: u8,
    op1: u16,
    op2_type: u8,
    op2: u16,
    ty: u8,
) -> Fr {
    let b = s_var_of(op1);
    let cz0 = slots[b];
    let init = cz0.ty == IS_NULL && (ty == BP_W || ty == BP_RW);
    let cz = if init {
        Zv { ty: IS_ARRAY, lval: (b - VAR_BASE) as u64, ..cz0 }
    } else {
        cz0
    };
    let slots1 = if init { slots.update(b, cz) } else { slots };
    let anext1 = if init { anext.update(b - VAR_BASE, 0) } else { anext };
    if cz.ty == IS_ARRAY {
        let a = (cz.lval % (NVAR as u64)) as int;
        if op2_type == T_UNUSED {
            let n = anext1[a];
            let rc = slots1[UNINIT as int].refcount.wrapping_add(1);
            if n as int >= DIM as int {
                let z = Zv { refcount: rc.wrapping_sub(1), ..slots1[UNINIT as int] };
                Fr { slots: slots1.update(UNINIT as int, z), anext: anext1, bail: bail, r: UNINIT }
            } else {
                let z = Zv { refcount: rc, ..slots1[UNINIT as int] };
                let slots2 = slots1.update(UNINIT as int, z);
                let anext2 = anext1.update(a, n.wrapping_add(1));
                let s = ARR_BASE + a * (DIM as int) + n as int;
                let z2 = Zv { ty: IS_NULL, lval: 0, ..slots2[s] };
                Fr { slots: slots2.update(s, z2), anext: anext2, bail: bail, r: s as u16 }
            }
        } else {
            Fr {
                slots: slots1,
                anext: anext1,
                bail: bail,
                r: (ARR_BASE + a * (DIM as int) + (op2 as int) % (DIM as int)) as u16,
            }
        }
    } else if cz.ty == IS_STRING {
        if op2_type == T_UNUSED {
            Fr { slots: slots1, anext: anext1, bail: 2, r: ERR }
        } else {
            Fr { slots: slots1, anext: anext1, bail: bail, r: UNINIT }
        }
    } else if cz.ty == IS_NULL {
        Fr { slots: slots1, anext: anext1, bail: bail, r: UNINIT }
    } else {
        Fr { slots: slots1, anext: anext1, bail: bail, r: ERR }
    }
}

/// The executor's state. `EX(Ts)`, the zval store, the arrays' next-free
/// indices, the checksum and `zend_bailout()`.
pub struct Es {
    pub slots: Seq<Zv>,
    pub anext: Seq<u16>,
    pub ts: Seq<u16>,
    pub acc: u64,
    pub bail: u8,
}

pub open spec fn s_is_dim(oc: u8) -> bool {
    oc == FETCH_DIM_R || oc == FETCH_DIM_W || oc == FETCH_DIM_RW || oc == FETCH_DIM_IS || oc
        == FETCH_DIM_FUNC_ARG || oc == FETCH_DIM_UNSET
}

/// ⚠ `FETCH_DIM_FUNC_ARG` hands down `BP_VAR_R`, not a mode of its own: :2084's
/// `ARG_SHOULD_BE_SENT_BY_REF` picks W or R and by value is what `f($a[])`
/// takes. `../NOTES.md` §2 is the census of what that costs.
pub open spec fn s_dim_mode(oc: u8) -> u8 {
    if oc == FETCH_DIM_R {
        BP_R
    } else if oc == FETCH_DIM_W {
        BP_W
    } else if oc == FETCH_DIM_RW {
        BP_RW
    } else if oc == FETCH_DIM_IS {
        BP_IS
    } else if oc == FETCH_DIM_FUNC_ARG {
        BP_R
    } else {
        BP_UNSET
    }
}

/// `zend_isset_isempty_dim_prop_obj_handler`'s two observations -- :3958-4000.
pub open spec fn s_isset_pair(es: Es, o: Op) -> (u64, u64) {
    let c = s_var_of(o.op1);
    let off = s_gzp(es.ts, o.op2_type, o.op2);
    let cz = es.slots[c];
    if cz.ty == IS_ARRAY {
        let a = (cz.lval % (NVAR as u64)) as int;
        let oz = es.slots[off];
        if oz.ty == IS_LONG {
            let idx = (oz.lval % (DIM as u64)) as int;
            let s = ARR_BASE + a * (DIM as int) + idx;
            if idx < es.anext[a] as int {
                if es.slots[s].ty != IS_NULL {
                    (1u64, 1u64)
                } else {
                    (1u64, 0u64)
                }
            } else {
                (0u64, 0u64)
            }
        } else {
            (0u64, 0u64)
        }
    } else {
        (0u64, 0u64)
    }
}

/// One dispatch of `execute()`'s loop -- zend_execute.c:1383-1396.
pub open spec fn e_step(ops: Seq<Op>, es: Es, pc: int) -> Es {
    let o = ops[pc];
    let a = es.acc.wrapping_mul(31).wrapping_add(o.opcode as u64);
    if s_is_dim(o.opcode) {
        let f = s_fetch(
            es.slots,
            es.anext,
            es.bail,
            o.op1,
            o.op2_type,
            o.op2,
            s_dim_mode(o.opcode),
        );
        Es {
            slots: f.slots,
            anext: f.anext,
            ts: es.ts.update(s_tmp_of(o.result), f.r),
            acc: a,
            bail: f.bail,
        }
    } else if o.opcode == ISSET_ISEMPTY_DIM_OBJ {
        let p = s_isset_pair(Es { acc: a, ..es }, o);
        Es {
            slots: es.slots,
            anext: es.anext,
            ts: es.ts,
            acc: a.wrapping_mul(31).wrapping_add(p.0).wrapping_mul(31).wrapping_add(p.1),
            bail: es.bail,
        }
    } else if o.opcode == ISSET_ISEMPTY_VAR {
        let v = s_var_of(o.op1);
        let live: u64 = if es.slots[v].ty != IS_NULL { 1u64 } else { 0u64 };
        Es {
            slots: es.slots,
            anext: es.anext,
            ts: es.ts,
            acc: a.wrapping_mul(31).wrapping_add(live),
            bail: es.bail,
        }
    } else {
        Es {
            slots: es.slots,
            anext: es.anext,
            ts: es.ts.update(s_tmp_of(o.result), s_var_of(o.op1) as u16),
            acc: a,
            bail: es.bail,
        }
    }
}

pub open spec fn e_run(ops: Seq<Op>, nops: int, pc: int, es: Es) -> Es
    decreases nops - pc,
{
    if pc >= nops || pc < 0 {
        es
    } else if es.bail != 0 {
        es
    } else {
        e_run(ops, nops, pc + 1, e_step(ops, es, pc))
    }
}

/// The frame `execute()` builds. Slots 0 and 1 are `EG(uninitialized_zval)` and
/// `EG(error_zval)`; half the CV slots start as arrays and half as scalars, so
/// that both container arms of `zend_fetch_dimension_address` are live.
pub open spec fn init_zv(i: int) -> Zv {
    if i < VAR_BASE as int {
        Zv { lval: 0, value_hi: 0, refcount: 1, ty: IS_NULL, is_ref: 0 }
    } else if i < ARR_BASE as int {
        let k = i - VAR_BASE as int;
        if k % 2 == 0 {
            Zv { lval: k as u64, value_hi: 0, refcount: 1, ty: IS_ARRAY, is_ref: 0 }
        } else if k == 1 {
            Zv { lval: 0, value_hi: 0, refcount: 1, ty: IS_STRING, is_ref: 0 }
        } else {
            Zv { lval: (k * 7) as u64, value_hi: 0, refcount: 1, ty: IS_LONG, is_ref: 0 }
        }
    } else {
        Zv { lval: 0, value_hi: 0, refcount: 1, ty: IS_NULL, is_ref: 0 }
    }
}

pub open spec fn init_slots() -> Seq<Zv> {
    Seq::new(NSLOT as nat, |i: int| init_zv(i))
}

/// What `php_execute_script` observes: the store the program left behind, the
/// refcounts, and the arrays' next-free indices. ⭐ Slot 0's refcount --
/// `EG(uninitialized_zval)` -- is in here on purpose: it is how the row answers
/// "does the append leave the global's refcount unbalanced?" with a number
/// instead of an argument.
pub open spec fn fold_slots(slots: Seq<Zv>, acc: u64, i: int) -> u64
    decreases NSLOT - i,
{
    if i >= NSLOT as int || i < 0 {
        acc
    } else {
        fold_slots(
            slots,
            acc.wrapping_mul(31).wrapping_add(slots[i].ty as u64).wrapping_mul(31).wrapping_add(
                slots[i].lval,
            ).wrapping_mul(31).wrapping_add(slots[i].refcount as u64),
            i + 1,
        )
    }
}

pub open spec fn fold_anext(anext: Seq<u16>, acc: u64, i: int) -> u64
    decreases NVAR - i,
{
    if i >= NVAR as int || i < 0 {
        acc
    } else {
        fold_anext(anext, acc.wrapping_mul(31).wrapping_add(anext[i] as u64), i + 1)
    }
}

/// What the kernel must return. `model.py::ph56_run` re-derives it.
pub open spec fn ph56_fold(buf: Seq<u8>, off: int, ln: int) -> u64 {
    let win = buf.subrange(off, off + ln);
    let nstmt = if ln / 8 > MAX_STMT as int { MAX_STMT as int } else { ln / 8 };
    let cs = compiled(win, nstmt, 0, init_cs());
    let es0 = Es {
        slots: init_slots(),
        anext: Seq::new(NVAR as nat, |i: int| 0u16),
        ts: Seq::new(MAX_STMT as nat, |i: int| 0u16),
        acc: cs.acc,
        bail: cs.bail,
    };
    let es = if cs.bail == 0 { e_run(cs.ops, cs.nops, 0, es0) } else { es0 };
    fold_anext(
        es.anext,
        fold_slots(es.slots, es.acc.wrapping_mul(31).wrapping_add(es.bail as u64), 0),
        0,
    )
}

// ------------------------------------------------- the trusted accessors ---
// ⚠⚠ TEN ITEMS, AND EACH ONE IS A LINE OF TRUSTED BASE. They are written as
// wrappers rather than inline `unsafe` blocks because R5 must be able to give
// each a `requires`/`ensures` pair: Verus cannot see through `get_unchecked`,
// so the obligation has to live on a signature. `../spec.md`'s
// `unsafe_justifications` carries one entry per item.

// ------------------------------------------------------ TRUSTED, item 1/10 --
/// `win[i]`. SAFETY: `i < v.len()`, which every caller establishes from the
/// driver's `off + len <= buf_len` and its own loop bound.
#[verifier::external_body]
#[inline(always)]
fn bget(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_bget(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// ------------------------------------------------------ TRUSTED, item 2/10 --
/// `ops[i]`. SAFETY: `i < MAX_OPS`. The array's length is in its TYPE, so the
/// index is the only quantity that can make this undefined.
#[verifier::external_body]
#[inline(always)]
fn oget(a: &[Op; MAX_OPS], i: usize) -> (r: Op)
    requires
        i < MAX_OPS,
    ensures
        r == a@[i as int],
{
    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_oget(a: &[Op; MAX_OPS], i: usize) -> (r: Op)
    requires
        i < MAX_OPS,
    ensures
        r == a@[i as int],
{
    a[i]
}

// ------------------------------------------------------ TRUSTED, item 3/10 --
/// `ops[i] = x`. SAFETY: `i < MAX_OPS`. `x: Op` is a PURE VALUE and needs no
/// precondition -- every inhabitant of `Op` is a legal store into a slot that
/// is already initialised (`[ZERO_OP; MAX_OPS]` initialises the whole array
/// before the first call site is reached).
#[verifier::external_body]
#[inline(always)]
fn oset(a: &mut [Op; MAX_OPS], i: usize, x: Op)
    requires
        i < MAX_OPS,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    unsafe { *a.get_unchecked_mut(i) = x }
}

#[cfg(slb_twin)]
fn slb_twin_oset(a: &mut [Op; MAX_OPS], i: usize, x: Op)
    requires
        i < MAX_OPS,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    a[i] = x;
}

// ------------------------------------------------------ TRUSTED, item 4/10 --
/// `slots[i]`. SAFETY: `i < NSLOT`.
#[verifier::external_body]
#[inline(always)]
fn sget(a: &[Zv; NSLOT], i: usize) -> (r: Zv)
    requires
        i < NSLOT,
    ensures
        r == a@[i as int],
{
    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_sget(a: &[Zv; NSLOT], i: usize) -> (r: Zv)
    requires
        i < NSLOT,
    ensures
        r == a@[i as int],
{
    a[i]
}

// ------------------------------------------------------ TRUSTED, item 5/10 --
/// `slots[i] = x`. SAFETY: `i < NSLOT`; `x: Zv` is a pure value.
#[verifier::external_body]
#[inline(always)]
fn sset(a: &mut [Zv; NSLOT], i: usize, x: Zv)
    requires
        i < NSLOT,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    unsafe { *a.get_unchecked_mut(i) = x }
}

#[cfg(slb_twin)]
fn slb_twin_sset(a: &mut [Zv; NSLOT], i: usize, x: Zv)
    requires
        i < NSLOT,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    a[i] = x;
}

// ------------------------------------------------------ TRUSTED, item 6/10 --
/// `ts[i]`. SAFETY: `i < MAX_STMT`, which `tmp_of` establishes by `% MAX_STMT`.
#[verifier::external_body]
#[inline(always)]
fn tget(a: &[u16; MAX_STMT], i: usize) -> (r: u16)
    requires
        i < MAX_STMT,
    ensures
        r == a@[i as int],
{
    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_tget(a: &[u16; MAX_STMT], i: usize) -> (r: u16)
    requires
        i < MAX_STMT,
    ensures
        r == a@[i as int],
{
    a[i]
}

// ------------------------------------------------------ TRUSTED, item 7/10 --
/// `ts[i] = x`. SAFETY: `i < MAX_STMT`; `x: u16` is a pure value.
#[verifier::external_body]
#[inline(always)]
fn tset(a: &mut [u16; MAX_STMT], i: usize, x: u16)
    requires
        i < MAX_STMT,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    unsafe { *a.get_unchecked_mut(i) = x }
}

#[cfg(slb_twin)]
fn slb_twin_tset(a: &mut [u16; MAX_STMT], i: usize, x: u16)
    requires
        i < MAX_STMT,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    a[i] = x;
}

// ------------------------------------------------------ TRUSTED, item 8/10 --
/// `anext[i]`. SAFETY: `i < NVAR`, established by `% NVAR`.
#[verifier::external_body]
#[inline(always)]
fn nget(a: &[u16; NVAR], i: usize) -> (r: u16)
    requires
        i < NVAR,
    ensures
        r == a@[i as int],
{
    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_nget(a: &[u16; NVAR], i: usize) -> (r: u16)
    requires
        i < NVAR,
    ensures
        r == a@[i as int],
{
    a[i]
}

// ------------------------------------------------------ TRUSTED, item 9/10 --
/// `anext[i] = x`. SAFETY: `i < NVAR`; `x: u16` is a pure value.
#[verifier::external_body]
#[inline(always)]
fn nset(a: &mut [u16; NVAR], i: usize, x: u16)
    requires
        i < NVAR,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    unsafe { *a.get_unchecked_mut(i) = x }
}

#[cfg(slb_twin)]
fn slb_twin_nset(a: &mut [u16; NVAR], i: usize, x: u16)
    requires
        i < NVAR,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    a[i] = x;
}

// ----------------------------------------------------- TRUSTED, item 10/10 --
/// ⭐⭐⭐ **THE ROW'S OWN TRUSTED ITEM.** `Option::unwrap_unchecked` on the
/// operand slot. SAFETY: `t.is_some()`.
///
/// ⚠ What makes this entry worth reading is WHERE the precondition comes from.
/// Not from arithmetic and not from the caller's convenience: from the
/// COMPILER. `zend_do_end_variable_parse` is supposed to guarantee that an
/// opcode whose handler reads op2 is only ever emitted with op2 present, and
/// `zend_isset_isempty_dim_prop_obj_handler` relies on exactly that when it
/// writes `switch (offset->type)` with no test (zend_execute.c:3973).
/// ⛔ At PHP 5.0.0 the guarantee is FALSE, because `case BP_VAR_IS:` does not
/// carry the test its two siblings carry -- and `1e708a5aeb30` is the three
/// lines that make it true again. **This one `requires` is CRASH-041, written
/// as a precondition**, and `operand_present` is what discharges it.
#[verifier::external_body]
#[inline(always)]
fn zunwrap(t: Option<usize>) -> (r: usize)
    requires
        t.is_some(),
    ensures
        r == t.unwrap(),
{
    unsafe { t.unwrap_unchecked() }
}

#[cfg(slb_twin)]
fn slb_twin_zunwrap(t: Option<usize>) -> (r: usize)
    requires
        t.is_some(),
    ensures
        r == t.unwrap(),
{
    t.unwrap()
}

// ------------------------------------------------- TRUSTED, I/O 1/2 and 2/2 --
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// `println!` is not verifiable; no `ensures`. Counted with the ten above --
// every `external_body` item is TCB, not just the interesting ones
// (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ------------------------------------------------------------ exec helpers --

#[inline(always)]
fn var_of(o: u16) -> (r: usize)
    ensures
        r == s_var_of(o),
        r < NSLOT,
        VAR_BASE <= r < ARR_BASE,
{
    VAR_BASE + (o as usize) % NVAR
}

#[inline(always)]
fn tmp_of(o: u16) -> (r: usize)
    ensures
        r == s_tmp_of(o),
        r < MAX_STMT,
{
    (o as usize) % MAX_STMT
}

/// `_get_zval_ptr` -- zend_execute.c:88-125. ⭐⭐ THE `IS_UNUSED` ARM IS AN
/// EXPLICIT `return NULL;` (:118-121), and in Rust it is an explicit `None`.
/// It is correct: an operand that is not there has no zval. Every caller that
/// can be handed an IS_UNUSED operand is supposed to know it cannot be.
#[inline(always)]
fn get_zval_ptr(ts: &[u16; MAX_STMT], op_type: u8, op: u16) -> (r: Option<usize>)
    ensures
        r.is_some() == s_gzp_some(op_type),
        r.is_some() ==> r.unwrap() == s_gzp(ts@, op_type, op),
        r.is_some() ==> r.unwrap() < NSLOT,
{
    if op_type == T_CONST {
        Some(var_of(op))
    } else if op_type == T_VAR {
        Some((tget(ts, tmp_of(op)) as usize) % NSLOT)
    } else {
        None // case IS_UNUSED: return NULL; -- :120
    }
}

/// `zend_do_end_variable_parse` -- zend_compile.c:736-780. ⛔⛔ THE DEFECT SITE.
/// Six arms, upstream's order, upstream's deltas, upstream's two guards -- and
/// `1e708a5aeb30`'s three lines on the third. Returns `false` on
/// `E_COMPILE_ERROR`, which in PHP is a `zend_bailout()` out of the whole
/// compile, so nothing runs at all.
fn do_end_variable_parse(o: &mut Op, ty: u8) -> (r: bool)
    ensures
        r == s_parse_ok(*old(o), ty),
        r ==> *final(o) == s_parse_op(*old(o), ty),
        !r ==> *final(o) == *old(o),
{
    if ty == BP_R {
        // :752-757 -- GUARDED at 5.0.0
        if o.opcode == FETCH_DIM_W && o.op2_type == T_UNUSED {
            return false; // :754 "Cannot use [] for reading"
        }
        o.opcode = o.opcode.wrapping_sub(3); // :756
    } else if ty == BP_W {
        // :758-759 -- nothing. `$a[] = 1;` is what [] is FOR.
    } else if ty == BP_RW {
        o.opcode = o.opcode.wrapping_add(3); // :761
    } else if ty == BP_IS {
        // ✅✅ 1e708a5aeb30's three inserted lines -- BP_VAR_R's OWN guard,
        // copied across, same test and same message. At 5.0.0 this arm is the
        // three lines below it and nothing else, which is CRASH-041.
        if o.opcode == FETCH_DIM_W && o.op2_type == T_UNUSED {
            return false;
        }
        o.opcode = o.opcode.wrapping_add(6); // :764  /* 3+3 */
    } else if ty == BP_FUNC_ARG {
        // ⚠ STILL UNGUARDED, IN 5.0.0 AND AFTER THE FIX. `../NOTES.md` §2 is
        // the census: this arm is reachable and silent, and 1e708a5aeb30 does
        // not touch it. That is a result the row reports, not one it repairs.
        o.opcode = o.opcode.wrapping_add(9); // :767  /* 3+3+3 */
        o.ext = 0; // = arg_offset, :768
    } else if ty == BP_UNSET {
        // :770-775 -- GUARDED at 5.0.0
        if o.opcode == FETCH_DIM_W && o.op2_type == T_UNUSED {
            return false; // :772 "Cannot use [] for unsetting"
        }
        o.opcode = o.opcode.wrapping_add(12); // :774  /* 3+3+3+3 */
    }
    true
}

/// `zend_do_isset_or_isempty` -- zend_compile.c:3215-3240. ⭐⭐ THE SECOND
/// REWRITE, and it is why reading `:763` alone names the wrong harm: it runs
/// AFTER the mode switch and rewrites the LAST opline of the fetch list only.
#[inline(always)]
fn do_isset_or_isempty(o: &mut Op)
    ensures
        *final(o) == s_isset_rewrite(*old(o)),
{
    if o.opcode == FETCH_IS {
        o.opcode = ISSET_ISEMPTY_VAR; // :3227
    } else if o.opcode == FETCH_DIM_IS {
        o.opcode = ISSET_ISEMPTY_DIM_OBJ; // :3229
    } else if o.opcode == FETCH_OBJ_IS {
        o.opcode = ISSET_ISEMPTY_PROP_OBJ; // :3231
    }
    o.ext = 1; // = type, i.e. ZEND_ISSET -- :3239
}

/// `zend_fetch_dimension_address` -- zend_execute.c:896-975. The IS_ARRAY arm's
/// `op2->op_type == IS_UNUSED` branch is :935-943 and it is THE APPEND -- which
/// is what `$a[] = 1` is implemented by, so it is not a defect on its own.
/// ⭐ The STRING container IS guarded, at :963-964.
fn fetch_dimension_address(
    slots: &mut [Zv; NSLOT],
    anext: &mut [u16; NVAR],
    bailout: &mut u8,
    op1: u16,
    op2_type: u8,
    op2: u16,
    ty: u8,
) -> (r: u16)
    ensures
        final(slots)@ == s_fetch(
            old(slots)@,
            old(anext)@,
            *old(bailout),
            op1,
            op2_type,
            op2,
            ty,
        ).slots,
        final(anext)@ == s_fetch(
            old(slots)@,
            old(anext)@,
            *old(bailout),
            op1,
            op2_type,
            op2,
            ty,
        ).anext,
        *final(bailout) == s_fetch(
            old(slots)@,
            old(anext)@,
            *old(bailout),
            op1,
            op2_type,
            op2,
            ty,
        ).bail,
        r == s_fetch(old(slots)@, old(anext)@, *old(bailout), op1, op2_type, op2, ty).r,
        r < NSLOT,
{
    let b = var_of(op1);
    // TUNED (2): `container` read ONCE, which is what the C does anyway -- it
    // is a `zval *` loaded at :898 and then tested four times.
    let mut cz: Zv = sget(slots, b);
    let mut cty: u8 = cz.ty;
    if cty == IS_NULL {
        // :914-927 -- array_init on a NULL container, write modes only
        if ty == BP_W || ty == BP_RW {
            cz.ty = IS_ARRAY; // :924
            cz.lval = (b - VAR_BASE) as u64;
            sset(slots, b, cz);
            nset(anext, b - VAR_BASE, 0);
            cty = IS_ARRAY;
        }
    }
    if cty == IS_ARRAY {
        // :930
        let a = (cz.lval % (NVAR as u64)) as usize;
        if op2_type == T_UNUSED {
            // :935 -- THE APPEND
            let n = nget(anext, a);
            // TUNED (3): the global's refcount is one load and one store across
            // both arms, rather than two of each.
            let rc = sget(slots, UNINIT as usize).refcount.wrapping_add(1); // :938
            if n as usize >= DIM {
                // :939 ... == FAILURE, :940 "Cannot add element to the array"
                let mut z = sget(slots, UNINIT as usize);
                z.refcount = rc.wrapping_sub(1); // :942
                sset(slots, UNINIT as usize, z);
                return UNINIT; // :941
            }
            let mut z = sget(slots, UNINIT as usize);
            z.refcount = rc;
            sset(slots, UNINIT as usize, z);
            nset(anext, a, n.wrapping_add(1));
            let s = ARR_BASE + a * DIM + n as usize;
            let mut z = sget(slots, s);
            z.ty = IS_NULL; // the uninitialized zval
            z.lval = 0;
            sset(slots, s, z);
            return s as u16;
        }
        // :944 zend_fetch_dimension_address_inner
        return (ARR_BASE + a * DIM + (op2 as usize) % DIM) as u16;
    } else if cty == IS_STRING {
        // :959
        if op2_type == T_UNUSED {
            // :963-964 E_ERROR "[] operator not supported for strings"
            // ⭐ THE CONTAINER TYPE THAT *IS* GUARDED.
            *bailout = 2;
            return ERR;
        }
        return UNINIT;
    } else if cty == IS_NULL {
        // :949-957 -- read mode
        return UNINIT;
    }
    // a scalar: "Cannot use a scalar value as an array"
    ERR
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
//
// One `ensures`, and it is the VALUE, not the safety property. What makes it
// worth having: it is what stops the proof being vacuous, it is what `model.py`
// re-derives independently, and it is what forces the invariants to describe the
// whole machine rather than merely bound an index. A kernel that returned 0
// unconditionally would satisfy every bounds obligation in this file.

// ⭐⭐⭐ **NO `#[verifier::rlimit]`, AND THAT IS A MEASUREMENT.** Verus's default
// is 10. Bisected on this box (`controls/rlimit_bisect.sh`, table in
// `../NOTES.md` §11):
//
//     rlimit  1   65 verified / 1 error plain,   75 / 1 twin
//     rlimit  2   66 / 0 plain,                  76 / 0 twin
//     rlimit 200  66 / 0 plain,                  76 / 0 twin
//
// So a compiler pass, an interpreter, a value postcondition over the whole
// machine state and TEN verified twins need **2**, and the default is 5x that.
// ⭐ `ph55` bisected to the same **2** on a proof of the same shape, which makes
// the family's Verus result `n = 2` on this axis as well as on the obligation's.
// ⚠ THE FIRST DRAFT OF THIS FILE *DID* EXCEED THE DEFAULT, and the cause was a
// WRONG LOOP INVARIANT rather than proof size: two clauses that cannot hold at a
// `break` were declared `invariant` instead of `invariant_except_break`, and Z3
// spent the budget failing. **An rlimit error is a symptom, not a size.**
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == ph56_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = &buf[off..off + len];
    assert(win@.len() == vstd::slice::spec_slice_len(win));
    assert(win@ =~= buf@.subrange(off as int, off + len));
    let mut nstmt: usize = len / 8;
    if nstmt > MAX_STMT {
        nstmt = MAX_STMT;
    }
    assert(nstmt as int == (if len as int / 8 > MAX_STMT as int {
        MAX_STMT as int
    } else {
        len as int / 8
    }));
    assert(8 * nstmt <= win@.len());

    let mut ops: [Op; MAX_OPS] = [ZERO_OP; MAX_OPS];
    let mut slots: [Zv; NSLOT] = [ZERO_ZV; NSLOT];
    let mut anext: [u16; NVAR] = [0u16; NVAR];
    let mut ts: [u16; MAX_STMT] = [0u16; MAX_STMT];
    let mut acc: u64 = 0;
    let mut bailout: u8 = 0;
    assert(ops@ =~= init_cs().ops);

    // The two process-global singletons, and the refcount PHP starts them at.
    sset(&mut slots, UNINIT as usize, Zv { ty: IS_NULL, refcount: 1, ..ZERO_ZV });
    sset(&mut slots, ERR as usize, Zv { ty: IS_NULL, refcount: 1, ..ZERO_ZV });
    let mut i: usize = 0;
    while i < NVAR
        invariant
            i <= NVAR,
            slots@.len() == NSLOT,
            forall|j: int| 0 <= j < VAR_BASE + i ==> #[trigger] slots@[j] == init_zv(j),
            forall|j: int|
                VAR_BASE + i <= j < NSLOT ==> (#[trigger] slots@[j]).ty == IS_NULL
                    && slots@[j].lval == 0 && slots@[j].value_hi == 0 && slots@[j].is_ref == 0,
        decreases NVAR - i,
    {
        // Half the CV slots start as arrays and half as scalars, so that both
        // container arms of `zend_fetch_dimension_address` are live.
        let s = VAR_BASE + i;
        let mut z = ZERO_ZV;
        z.refcount = 1;
        if i % 2 == 0 {
            z.ty = IS_ARRAY;
            z.lval = i as u64;
        } else if i == 1 {
            z.ty = IS_STRING;
        } else {
            z.ty = IS_LONG;
            z.lval = (i * 7) as u64;
        }
        sset(&mut slots, s, z);
        i = i + 1;
    }
    let mut i: usize = 0;
    while i < NVAR * DIM
        invariant
            i <= NVAR * DIM,
            slots@.len() == NSLOT,
            forall|j: int| 0 <= j < ARR_BASE + i ==> #[trigger] slots@[j] == init_zv(j),
        decreases NVAR * DIM - i,
    {
        sset(&mut slots, ARR_BASE + i, Zv { ty: IS_NULL, refcount: 1, ..ZERO_ZV });
        i = i + 1;
    }
    assert(slots@ =~= init_slots());

    // -- THE COMPILER'S ONE PASS. `while (le)` at :748-779 runs the mode switch
    // once per fetch-list element; `zend_do_isset_or_isempty` then rewrites the
    // LAST element only.
    let ghost ctarget = compiled(win@, nstmt as int, 0, init_cs());
    let mut nops: usize = 0;
    let mut i: usize = 0;
    while i < nstmt
        invariant_except_break
            bailout == 0,
            compiled(
                win@,
                nstmt as int,
                i as int,
                Cs { ops: ops@, nops: nops as int, acc: acc, bail: bailout, stop: false },
            ) == ctarget,
        invariant
            i <= nstmt,
            nstmt <= MAX_STMT,
            8 * nstmt <= win@.len(),
            ops@.len() == MAX_OPS,
            nops <= MAX_OPS,
            operand_present(ops@, nops as int),
        ensures
            ops@.len() == MAX_OPS,
            nops <= MAX_OPS,
            operand_present(ops@, nops as int),
            ops@ == ctarget.ops,
            nops as int == ctarget.nops,
            acc == ctarget.acc,
            bailout == ctarget.bail,
        decreases nstmt - i,
    {
        let ghost cs0 = Cs {
            ops: ops@,
            nops: nops as int,
            acc: acc,
            bail: bailout,
            stop: false,
        };
        assert(compiled(win@, nstmt as int, i as int, cs0) == ctarget);
        assert(compiled(win@, nstmt as int, i as int, cs0) == compiled(
            win@,
            nstmt as int,
            i as int + 1,
            c_stmt(win@, cs0, i as int),
        )) by {
            reveal_with_fuel(compiled, 2);
        }
        // TUNED (1): one subslice, one bounds check, eight reads the compiler
        // knows are in range from the TYPE. R2 pays eight checks here.
        let b0: usize = 8 * i;
        let mode: u8 = MODES[(bget(win, b0) as usize) % 6];
        let b1: u8 = bget(win, b0 + 1);
        let chain: usize = if b1 & 0x80 != 0 { 1 } else { 0 };
        let base: u8 = BASES[((b1 & 0x7F) as usize) % 3];
        let o2t: u8 = OP2T[(bget(win, b0 + 2) as usize) % 3];
        let op2: u16 = bget(win, b0 + 3) as u16;
        let op1: u16 =
            (bget(win, b0 + 4) as u16) | ((bget(win, b0 + 5) as u16) << 8);
        let res: u16 =
            (bget(win, b0 + 6) as u16) | ((bget(win, b0 + 7) as u16) << 8);
        let first: usize = nops;
        // Ghost only: the three decode tables are the three spec functions.
        // Each is a six- or three-way case split over literal opcode values, so
        // Z3 decides it by evaluation rather than by search.
        assert(mode == s_mode_of(win@[b0 as int]));
        assert(base == s_base_of(b1));
        assert(o2t == s_o2t_of(win@[b0 as int + 2]));
        assert(mode == BP_R || mode == BP_W || mode == BP_RW || mode == BP_IS || mode
            == BP_FUNC_ARG || mode == BP_UNSET);
        assert(base == FETCH_W || base == FETCH_DIM_W || base == FETCH_OBJ_W);
        assert(o2t == T_UNUSED || o2t == T_CONST || o2t == T_VAR);

        if nops + 1 + chain > MAX_OPS {
            proof {
                reveal_with_fuel(compiled, 2);
            }
            assert(c_stmt(win@, cs0, i as int) == Cs { stop: true, ..cs0 });
            break ;
        }
        if chain == 1 {
            // `$a[]` as the LEADING element of a chain: a DIM fetch with an
            // absent op2, which `:3223-3231` will NOT rewrite because it is not
            // the last. This is the row's second, silent harm.
            oset(&mut ops, nops, Op {
                opcode: FETCH_DIM_W,
                op1_type: T_CONST,
                op2_type: T_UNUSED,
                ext: 0,
                op1,
                op2: 0,
                result: res.wrapping_add(1),
            });
            nops = nops + 1;
        }
        oset(&mut ops, nops, Op {
            opcode: base,
            op1_type: T_CONST,
            op2_type: if base == FETCH_W { T_UNUSED } else { o2t },
            ext: 0,
            op1: if chain == 1 { res.wrapping_add(1) } else { op1 },
            op2,
            result: res,
        });
        nops = nops + 1;

        let ghost n2 = nops;
        let ghost pre = ops@;
        let ghost ptarget = parsed(
            Ps { ops: pre, acc: acc, bail: 0, k: first as int },
            n2 as int,
            mode,
        );
        let mut k: usize = first;
        while k < nops
            invariant_except_break
                nops == n2,
                bailout == 0,
            invariant
                first <= k <= n2,
                n2 <= MAX_OPS,
                ops@.len() == MAX_OPS,
                forall|j: int|
                    0 <= j < first || n2 <= j < MAX_OPS ==> #[trigger] ops@[j] == pre[j],
                forall|j: int|
                    first <= j < k ==> #[trigger] ops@[j] == s_parse_op(pre[j], mode),
                forall|j: int| first <= j < k ==> s_parse_ok(#[trigger] pre[j], mode),
                forall|j: int| k <= j < n2 ==> #[trigger] ops@[j] == pre[j],
                parsed(Ps { ops: ops@, acc: acc, bail: 0, k: k as int }, n2 as int, mode)
                    == ptarget,
            ensures
                ops@.len() == MAX_OPS,
                ops@ == ptarget.ops,
                acc == ptarget.acc,
                bailout == ptarget.bail,
                bailout == 0 ==> nops == n2,
                bailout != 0 ==> nops == 0,
                bailout == 0 ==> (forall|j: int|
                    0 <= j < first || n2 <= j < MAX_OPS ==> #[trigger] ops@[j] == pre[j]),
                bailout == 0 ==> (forall|j: int|
                    first <= j < n2 ==> #[trigger] ops@[j] == s_parse_op(pre[j], mode)),
                bailout == 0 ==> (forall|j: int|
                    first <= j < n2 ==> s_parse_ok(#[trigger] pre[j], mode)),
            decreases n2 - k,
        {
            let mut o: Op = oget(&ops, k);
            proof {
                reveal_with_fuel(parsed, 2);
            }
            if !do_end_variable_parse(&mut o, mode) {
                bailout = 1; // zend_bailout() -- nothing runs
                nops = 0;
                break ;
            }
            oset(&mut ops, k, o);
            acc = acc.wrapping_mul(31).wrapping_add(o.opcode as u64);
            k = k + 1;
        }
        if bailout != 0 {
            // zend_bailout() out of the whole compile: `nops` is zero, so
            // `operand_present` is vacuous and the executor never runs.
            proof {
                reveal_with_fuel(compiled, 2);
            }
            assert(c_stmt(win@, cs0, i as int) == Cs {
                ops: ops@,
                nops: 0,
                acc: acc,
                bail: bailout,
                stop: false,
            });
            assert(compiled(win@, nstmt as int, i as int + 1, c_stmt(win@, cs0, i as int))
                == c_stmt(win@, cs0, i as int)) by {
                reveal_with_fuel(compiled, 2);
            }
            break ;
        }
        if mode == BP_IS {
            let mut o: Op = oget(&ops, nops - 1);
            do_isset_or_isempty(&mut o); // :3223 -- the LAST opline only
            oset(&mut ops, nops - 1, o);
            acc = acc.wrapping_mul(31).wrapping_add(o.opcode as u64);
        }
        // ⭐⭐⭐ THE ROW'S OBLIGATION, RE-ESTABLISHED FOR THE ONE OR TWO OPLINES
        // THIS STATEMENT EMITTED. Three facts carry it, and the middle one is
        // `1e708a5aeb30`:
        //   (a) `ZEND_ISSET_ISEMPTY_DIM_OBJ` is reachable only through
        //       `zend_do_isset_or_isempty`'s `ZEND_FETCH_DIM_IS` arm (:3229),
        //       and `ZEND_FETCH_DIM_IS` is `ZEND_FETCH_DIM_W + 6` and nothing
        //       else -- that is the six-groups-of-three layout;
        //   (b) `case BP_VAR_IS:` REFUSES `ZEND_FETCH_DIM_W` with an IS_UNUSED
        //       op2. At 5.0.0 it does not, and this assert is what fails;
        //   (c) `zend_do_isset_or_isempty` rewrites the LAST opline only, so a
        //       chain's leading `[]` opline is judged by (b) as well.
        assert forall|j: int|
            0 <= j < nops as int && (#[trigger] ops@[j]).opcode == ISSET_ISEMPTY_DIM_OBJ implies (
        ops@[j].op2_type == T_CONST || ops@[j].op2_type == T_VAR) by {
            if j < first as int {
                assert(ops@[j] == cs0.ops[j]);
            } else {
                assert(first as int <= j < n2 as int);
                assert(ops@[j] == s_parse_op(pre[j], mode) || ops@[j] == s_isset_rewrite(
                    s_parse_op(pre[j], mode),
                ));
                assert(s_parse_ok(pre[j], mode));
            }
        }
        proof {
            reveal_with_fuel(compiled, 2);
        }
        assert(c_stmt(win@, cs0, i as int) == Cs {
            ops: ops@,
            nops: nops as int,
            acc: acc,
            bail: 0,
            stop: false,
        });
        i = i + 1;
    }

    // -- execute()'s dispatch loop, zend_execute.c:1383-1396.
    assert(anext@ =~= Seq::new(NVAR as nat, |i: int| 0u16));
    assert(ts@ =~= Seq::new(MAX_STMT as nat, |i: int| 0u16));
    let ghost es0 = Es {
        slots: slots@,
        anext: anext@,
        ts: ts@,
        acc: acc,
        bail: bailout,
    };
    let ghost etarget = if bailout == 0 {
        e_run(ops@, nops as int, 0, es0)
    } else {
        es0
    };
    if bailout == 0 {
        let mut pc: usize = 0;
        while pc < nops
            invariant
                pc <= nops,
                nops <= MAX_OPS,
                ops@.len() == MAX_OPS,
                slots@.len() == NSLOT,
                anext@.len() == NVAR,
                ts@.len() == MAX_STMT,
                operand_present(ops@, nops as int),
                e_run(
                    ops@,
                    nops as int,
                    pc as int,
                    Es { slots: slots@, anext: anext@, ts: ts@, acc: acc, bail: bailout },
                ) == etarget,
            ensures
                slots@.len() == NSLOT,
                anext@.len() == NVAR,
                ts@.len() == MAX_STMT,
                slots@ == etarget.slots,
                anext@ == etarget.anext,
                ts@ == etarget.ts,
                acc == etarget.acc,
                bailout == etarget.bail,
            decreases nops - pc,
        {
            if bailout != 0 {
                break; // zend_bailout() -- E_ERROR leaves the executor
            }
            let o: Op = oget(&ops, pc);
            acc = acc.wrapping_mul(31).wrapping_add(o.opcode as u64);
            if o.opcode == FETCH_DIM_R {
                let r = fetch_dimension_address(
                    &mut slots, &mut anext, &mut bailout, o.op1, o.op2_type, o.op2, BP_R);
                tset(&mut ts, tmp_of(o.result), r);
            } else if o.opcode == FETCH_DIM_W {
                let r = fetch_dimension_address(
                    &mut slots, &mut anext, &mut bailout, o.op1, o.op2_type, o.op2, BP_W);
                tset(&mut ts, tmp_of(o.result), r);
            } else if o.opcode == FETCH_DIM_RW {
                let r = fetch_dimension_address(
                    &mut slots, &mut anext, &mut bailout, o.op1, o.op2_type, o.op2, BP_RW);
                tset(&mut ts, tmp_of(o.result), r);
            } else if o.opcode == FETCH_DIM_IS {
                // ⭐ REACHABLE, and only through a CHAIN, because :3223-3231
                // rewrites the LAST opline only. THE SILENT HARM.
                let r = fetch_dimension_address(
                    &mut slots, &mut anext, &mut bailout, o.op1, o.op2_type, o.op2, BP_IS);
                tset(&mut ts, tmp_of(o.result), r);
            } else if o.opcode == FETCH_DIM_FUNC_ARG {
                // :2084 -- ARG_SHOULD_BE_SENT_BY_REF picks W or R; by value is
                // the common case and is what `f($a[])` takes.
                let r = fetch_dimension_address(
                    &mut slots, &mut anext, &mut bailout, o.op1, o.op2_type, o.op2, BP_R);
                tset(&mut ts, tmp_of(o.result), r);
            } else if o.opcode == FETCH_DIM_UNSET {
                let r = fetch_dimension_address(
                    &mut slots, &mut anext, &mut bailout, o.op1, o.op2_type, o.op2, BP_UNSET);
                tset(&mut ts, tmp_of(o.result), r);
            } else if o.opcode == ISSET_ISEMPTY_DIM_OBJ {
                // zend_isset_isempty_dim_prop_obj_handler, :3958-4000.
                let c = var_of(o.op1); // :3960
                let offset = get_zval_ptr(&ts, o.op2_type, o.op2); // :3961
                let mut isset: u64 = 0;
                let mut result: u64 = 0;
                let cz: Zv = sget(&slots, c);
                if cz.ty == IS_ARRAY {
                    // :3967
                    let a = (cz.lval % (NVAR as u64)) as usize;
                    // ⛔⛔⛔ :3973 -- `switch (offset->type)`. In C `offset` is
                    // NULL whenever op2 is IS_UNUSED and this is a read of
                    // address 0x14. In safe Rust the Option cannot be opened
                    // without this call, so the SAME wrong program panics.
                    let off = zunwrap(offset);
                    let oz: Zv = sget(&slots, off);
                    if oz.ty == IS_LONG {
                        let idx = (oz.lval % (DIM as u64)) as usize;
                        let s = ARR_BASE + a * DIM + idx;
                        if idx < nget(&anext, a) as usize {
                            isset = 1;
                            if sget(&slots, s).ty != IS_NULL {
                                result = 1; // ZEND_ISSET
                            }
                        }
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(isset);
                acc = acc.wrapping_mul(31).wrapping_add(result);
            } else if o.opcode == ISSET_ISEMPTY_VAR {
                // zend_isset_isempty_var_handler, :4048.
                let v = var_of(o.op1);
                let live: u64 = if sget(&slots, v).ty != IS_NULL { 1 } else { 0 };
                acc = acc.wrapping_mul(31).wrapping_add(live);
            } else {
                tset(&mut ts, tmp_of(o.result), var_of(o.op1) as u16);
            }
            proof {
                reveal_with_fuel(e_run, 2);
            }
            pc = pc + 1;
        }
    }

    // What `php_execute_script` observes: the store the program left behind,
    // the refcounts, and the arrays' next-free indices. ⭐ Slot 0's refcount --
    // `EG(uninitialized_zval)` -- is in here on purpose: it is how the row
    // answers "does the append leave the global's refcount unbalanced?" with a
    // number instead of an argument.
    assert(slots@ == etarget.slots);
    assert(anext@ == etarget.anext);
    assert(ts@ == etarget.ts);
    assert(acc == etarget.acc);
    assert(bailout == etarget.bail);
    acc = acc.wrapping_mul(31).wrapping_add(bailout as u64);
    let ghost tgt2 = fold_slots(slots@, acc, 0);
    let mut i: usize = 0;
    while i < NSLOT
        invariant
            i <= NSLOT,
            slots@.len() == NSLOT,
            fold_slots(slots@, acc, i as int) == tgt2,
        decreases NSLOT - i,
    {
        let z: Zv = sget(&slots, i);
        acc = acc.wrapping_mul(31).wrapping_add(z.ty as u64);
        acc = acc.wrapping_mul(31).wrapping_add(z.lval);
        acc = acc.wrapping_mul(31).wrapping_add(z.refcount as u64);
        i = i + 1;
    }
    let ghost tgt3 = fold_anext(anext@, acc, 0);
    let mut i: usize = 0;
    while i < NVAR
        invariant
            i <= NVAR,
            anext@.len() == NVAR,
            fold_anext(anext@, acc, i as int) == tgt3,
        decreases NVAR - i,
    {
        acc = acc.wrapping_mul(31).wrapping_add(nget(&anext, i) as u64);
        i = i + 1;
    }
    assert(acc == tgt3);
    assert(ph56_fold(buf@, off as int, len as int) == tgt3);
    acc
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 16 && stride_w <= 512 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole window is present.
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                16 <= stride <= n_blob,
                stride <= 512,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps,
            // so Z3 needs both spelled out. Erases at compile time -- R4 and R5
            // stay byte-identical.
            proof {
                let pr: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX as u128))
                    by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(pr < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        pr == (acc as int) * (nwin as int),
                        acc <= u64::MAX,
                        nwin >= 1,
                ;
            }
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            proof {
                assert(k < nwin);
                vstd::arithmetic::div_mod::lemma_fundamental_div_mod(n_blob as int, stride as int);
                assert((nwin as int) * (stride as int) <= n_blob as int);
                assert((k as int) * (stride as int) <= ((nwin as int) - 1) * (stride as int));
                assert(((nwin as int) - 1) * (stride as int) == (nwin as int) * (stride as int)
                    - (stride as int)) by (nonlinear_arith);
                assert((k as int) * (stride as int) + (stride as int) <= n_blob as int);
            }
            let r: u64 = kernel(buf, k * stride, stride);
            // Ghost only: this is what *consumes* the kernel's `ensures`.
            // Without it the postcondition is decoration -- deleting it
            // entirely still verifies, so nothing but mutation testing defends
            // it (`.memory/04-verus.md`).
            assert(r == ph56_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
