//! ph55 rung R5 -- unsafe + Verus.
//!
//! Same exec code as `unsafe.rs`, plus the proof that licenses it. What is
//! proved, and it is a VALUE postcondition rather than a memory-safety-only
//! retreat:
//!
//!     requires  off + len <= buf@.len(),  16 <= len,  len <= 8 * MAX_OPS
//!     ensures   r == ph55_fold(buf@, off as int, len as int)
//!
//! `ph55_fold` is PHP 5.0.0's executor with `4f68f3774c34` applied, spelled as
//! six recursive spec functions -- `decoded`, `emitted`, `passed`, `step`,
//! `run`, `fold_*` -- and `model.py` re-derives the same `u64` from a different
//! decomposition.
//!
//! ⚠⚠⚠ **THE OBLIGATION THIS ROW IS ABOUT IS `ok_from`, AND IT IS ABOUT THE
//! PC AND NOT ABOUT THE TABLE.**
//!
//!     ok_from(ops, n, p)  ==  "starting at p and striding by each
//!                              instruction's own width, every word the PC
//!                              lands on is an INSTRUCTION word -- never a
//!                              ZEND_OP_DATA word"
//!
//! It is the loop invariant of `execute()`'s dispatch loop, it is what
//! discharges `hunwrap`'s `requires t.is_some()`, and **it is exactly the
//! invariant `zend_binary_assign_op_helper`'s error exit breaks**. ⭐ Note what
//! it is NOT: it is not `handler != NULL`. The NULL is how the broken PC
//! MANIFESTS, and `inputs/adversarial-opdatalive.bin` is the input that shows
//! the difference -- there the PC is just as wrong and there is no NULL
//! anywhere.
//!
//! ⭐⭐ **AND IT IS ESTABLISHED BY THE EMITTER, NOT BY THE EXECUTOR.**
//! `emit_from` is the compiler's guarantee (`zend_compile` emits ZEND_OP_DATA
//! only as the trailing word of a two-word instruction), written as TAIL
//! RECURSION so that its postcondition is `ok_from`'s own unfolding. That is
//! the whole proof of the interesting half: two `assert ... by
//! reveal_with_fuel` and no lemma. Written as a `while` loop it would need an
//! invariant quantified over instruction starts plus a glue lemma; the shape
//! of the property decided the shape of the code, in every Rust rung.
//! `../NOTES.md` §10.
//!
//! ⚠⚠⚠ **WHAT VERUS COULD NOT BE MADE TO EXPRESS AT ALL, AND IT IS THE ROW'S
//! OWN DISPATCH MECHANISM.** `c/kernel.c` calls through a function pointer
//! stored in each instruction. Verus answers `error: The verifier does not yet
//! support the following Rust feature: function pointer types` -- measured,
//! `controls/fnptr.rs` is the probe and it is run by
//! `controls/negatives.py --verus`. So every Rust rung stores an
//! `Option<u8>` handler ID and dispatches with a `match`, and
//! `controls/fnptr_dispatch.rs` + `controls/fnptr_cost.py` price the
//! substitution. The proof forced a representation change on the exact
//! construct the defect is about.
//!
//! The unchecked classes rest on four independent facts, and `../NOTES.md` §10
//! keeps them apart:
//!
//!   * `hunwrap(o.handler)` rests on `ok_from` -- the 2004 patch's own
//!     invariant. `controls/negatives.py --emit nofixup` deletes the emitter
//!     pass and that mutant must FAIL to verify.
//!   * `bget(win, ..)` rests on the driver's `off + len <= buf@.len()`.
//!   * `oget/oset(ops, ..)` rests on `nops <= MAX_OPS`, i.e. on `c/main.c`'s
//!     `stride_w <= 512`.
//!   * `kget/kset/vget/vset(.., s)` rests on `all_slots(ts@)` -- every value
//!     ever written into a temp slot is a slot index. That is an invariant of
//!     the interpreter and of nothing else.

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
pub const MAX_OPS: usize = 64;

pub const NVAR: usize = 8;
pub const DIM: usize = 4;
pub const NT: usize = 4;

pub const UNINIT: u16 = 0;
pub const ERR: u16 = 1;
pub const VAR_BASE: usize = 2;
pub const ARR_BASE: usize = 10;   // VAR_BASE + NVAR
pub const NSLOT: usize = 42;      // ARR_BASE + NVAR * DIM

pub const IS_NULL: u8 = 0;
pub const IS_LONG: u8 = 1;
pub const IS_ARRAY: u8 = 2;

pub const NOP: u8 = 0;
pub const ASSIGN: u8 = 1;
pub const INIT_ARRAY: u8 = 2;
pub const ADD: u8 = 3;
pub const FETCH_DIM_RW: u8 = 4;
pub const ASSIGN_DIM: u8 = 5;
pub const ASSIGN_ADD: u8 = 6;
/// ⭐ `zend_opcode_handlers[ZEND_OP_DATA] = NULL;` -- zend_execute.c:4427.
pub const OP_DATA: u8 = 7;
pub const ECHO: u8 = 8;
pub const RETURN: u8 = 9;
pub const N_OPCODES: u8 = 10;

pub const X_DIM: u8 = 1;

/// `zend_op`, narrowed. `handler` is what `pass_two` writes -- zend_opcode.c:363.
#[derive(Clone, Copy)]
pub struct Op {
    pub opcode: u8,
    pub ext: u8,
    pub op1: u16,
    pub op2: u16,
    pub result: u16,
    pub handler: Option<u8>,
}

pub const ZERO_OP: Op = Op { opcode: 0, ext: 0, op1: 0, op2: 0, result: 0, handler: None };

// ------------------------------------------------------------------ spec ----

/// How wide an instruction is. ⚠ `ASSIGN_DIM` is two words for EVERY instance
/// (`zend_assign_dim_handler`, :2198-2226, one exit, no flag); `ASSIGN_ADD` is
/// two words only when its `extended_value` says so (:1734, :1749). **That
/// difference is the row**: a static width needs no flag, a data-dependent one
/// does, and the flag is what the error exit forgets.
pub open spec fn two_word_s(o: Op) -> bool {
    o.opcode == ASSIGN_DIM || (o.opcode == ASSIGN_ADD && o.ext == X_DIM)
}

pub open spec fn width_s(o: Op) -> int {
    if two_word_s(o) { 2int } else { 1int }
}

/// ⭐⭐⭐ **THE ROW'S OBLIGATION.** Starting at `p` and striding by each
/// instruction's own width, every word the PC lands on is an instruction word
/// and not a `ZEND_OP_DATA` word -- and every stride stays inside the
/// op_array.
pub open spec fn ok_from(ops: Seq<Op>, n: int, p: int) -> bool
    decreases n - p,
{
    if p >= n || p < 0 {
        true
    } else {
        &&& ops[p].opcode != OP_DATA
        &&& {
            let q = p + width_s(ops[p]);
            if q > p && q <= n {
                ok_from(ops, n, q)
            } else {
                false
            }
        }
    }
}

/// `pass_two`'s own postcondition -- zend_opcode.c:363. The table is copied
/// into EVERY instruction, which is how a NULL entry becomes reachable from a
/// PC at all.
pub open spec fn handlers_ok(ops: Seq<Op>, nops: int) -> bool {
    forall|j: int| 0 <= j < nops ==> #[trigger] ops[j] == with_handler(ops[j])
}

/// Every value ever written into a temp slot is a slot index. An invariant of
/// the interpreter, and what licenses `kget`/`vget`/`kset`/`vset`.
pub open spec fn all_slots(ts: Seq<u16>) -> bool {
    forall|j: int| 0 <= j < ts.len() ==> (#[trigger] ts[j]) < NSLOT
}

pub open spec fn s_is_tmp(o: u16) -> bool {
    (o & 0x8000) != 0
}

pub open spec fn s_var_of(o: u16) -> int {
    VAR_BASE + ((o & 0x7FFF) as int) % (NVAR as int)
}

pub open spec fn s_tmp_of(o: u16) -> int {
    ((o & 0x7FFF) as int) % (NT as int)
}

/// The machine, as a value. `EX(Ts)`, the zval store, the checksum and the PC.
pub struct St {
    pub kind: Seq<u8>,
    pub val: Seq<u64>,
    pub ts: Seq<u16>,
    pub acc: u64,
    pub pc: int,
    pub done: bool,
}

/// `get_zval_ptr_ptr` -- an operand names a CV slot unless its top bit is set.
pub open spec fn s_gzpp(s: St, op: u16) -> int {
    if s_is_tmp(op) { s.ts[s_tmp_of(op)] as int } else { s_var_of(op) }
}

/// `get_zval_ptr`.
pub open spec fn s_gzp(s: St, op: u16) -> u64 {
    let i = s_gzpp(s, op);
    if s.kind[i] == IS_LONG { s.val[i] } else { 0u64 }
}

/// `zend_fetch_dimension_address(..., BP_VAR_RW)` -- :1744. ⭐ On a non-array
/// base it yields `EG(error_zval_ptr)`: `$x = 1; $x[0] += 1;`, the corpus's own
/// trigger for CRASH-023.
pub open spec fn s_fetch(s: St, base: u16, dim: u16) -> int {
    let b = s_var_of(base);
    if s.kind[b] != IS_ARRAY {
        ERR as int
    } else {
        ARR_BASE + ((s.val[b] % (NVAR as u64)) as int) * (DIM as int) + ((dim as int) % (DIM as int))
    }
}

/// One dispatch. ⚠ `OP_DATA` has no arm here and needs none: the executor can
/// only reach it by dispatching a word with no handler, which `ok_from` rules
/// out. The final `else` is `ZEND_RETURN` and nothing else.
pub open spec fn step(ops: Seq<Op>, s: St) -> St {
    let o = ops[s.pc];
    let a = s.acc.wrapping_mul(31).wrapping_add(o.opcode as u64);
    if o.opcode == NOP {
        St { kind: s.kind, val: s.val, ts: s.ts, acc: a, pc: s.pc + 1, done: false }
    } else if o.opcode == ASSIGN {
        let d = s_var_of(o.op1);
        St {
            kind: s.kind.update(d, IS_LONG),
            val: s.val.update(d, o.op2 as u64),
            ts: s.ts.update(s_tmp_of(o.result), d as u16),
            acc: a,
            pc: s.pc + 1,
            done: false,
        }
    } else if o.opcode == INIT_ARRAY {
        let d = s_var_of(o.op1);
        St {
            kind: s.kind.update(d, IS_ARRAY),
            val: s.val.update(d, ((o.op2 as int) % (NVAR as int)) as u64),
            ts: s.ts.update(s_tmp_of(o.result), d as u16),
            acc: a,
            pc: s.pc + 1,
            done: false,
        }
    } else if o.opcode == ADD {
        // ⚠ BOTH OPERANDS BEFORE THE DESTINATION -- `result` may name the same
        // slot as `op1`. model.py's synthetic sweep caught exactly that.
        let x = s_gzp(s, o.op1);
        let y = s_gzp(s, o.op2);
        let d = s_var_of(o.result);
        St {
            kind: s.kind.update(d, IS_LONG),
            val: s.val.update(d, x.wrapping_add(y)),
            ts: s.ts,
            acc: a,
            pc: s.pc + 1,
            done: false,
        }
    } else if o.opcode == FETCH_DIM_RW {
        St {
            kind: s.kind,
            val: s.val,
            ts: s.ts.update(s_tmp_of(o.result), s_fetch(s, o.op1, o.op2) as u16),
            acc: a,
            pc: s.pc + 1,
            done: false,
        }
    } else if o.opcode == ASSIGN_DIM {
        // zend_assign_dim_handler, :2198-2226 -- THE CLEAN SIBLING.
        let od = ops[s.pc + 1];
        let dst = s_fetch(s, o.op1, o.op2);
        let ts1 = s.ts.update(s_tmp_of(od.op2), dst as u16);
        let s1 = St { kind: s.kind, val: s.val, ts: ts1, acc: a, pc: s.pc, done: false };
        let value = s_gzp(s1, od.op1);
        let k2 = if dst != ERR as int { s.kind.update(dst, IS_LONG) } else { s.kind };
        let v2 = if dst != ERR as int { s.val.update(dst, value) } else { s.val };
        St {
            kind: k2,
            val: v2,
            ts: ts1.update(s_tmp_of(o.result), dst as u16),
            acc: a,
            pc: s.pc + 2,
            done: false,
        }
    } else if o.opcode == ASSIGN_ADD {
        // zend_binary_assign_op_helper, :1724-1796 -- THE DEFECT'S SITE, with
        // 4f68f3774c34 applied.
        let od = ops[s.pc + 1];
        let inc = o.ext == X_DIM;
        let ts1 = if inc {
            s.ts.update(s_tmp_of(od.op2), s_fetch(s, o.op1, o.op2) as u16)
        } else {
            s.ts
        };
        let s1 = St { kind: s.kind, val: s.val, ts: ts1, acc: a, pc: s.pc, done: false };
        let value = if inc { s_gzp(s1, od.op1) } else { s_gzp(s1, o.op2) };
        let var_ptr = if inc { s_gzpp(s1, od.op2) } else { s_gzpp(s1, o.op1) };
        if var_ptr == ERR as int {
            // :1765.  ⭐ R1h: `if (increment_opline) { INC_OPCODE(); }` FIRST,
            // then NEXT_OPCODE(). R1 has only the second.
            St {
                kind: s.kind,
                val: s.val,
                ts: ts1.update(s_tmp_of(o.result), UNINIT),
                acc: a,
                pc: s.pc + 1 + (if inc { 1int } else { 0int }),
                done: false,
            }
        } else {
            let k2 = s.kind.update(var_ptr, IS_LONG);
            let cur = if s.kind[var_ptr] == IS_LONG { s.val[var_ptr] } else { 0u64 };
            let v2 = s.val.update(var_ptr, cur.wrapping_add(value));
            St {
                kind: k2,
                val: v2,
                ts: ts1.update(s_tmp_of(o.result), var_ptr as u16),
                acc: a,
                pc: s.pc + 1 + (if inc { 1int } else { 0int }),
                done: false,
            }
        }
    } else if o.opcode == ECHO {
        let i = s_gzpp(s, o.op1);
        St {
            kind: s.kind,
            val: s.val,
            ts: s.ts,
            acc: a.wrapping_mul(31).wrapping_add(s.kind[i] as u64).wrapping_mul(31).wrapping_add(
                s.val[i],
            ),
            pc: s.pc + 1,
            done: false,
        }
    } else {
        // ZEND_RETURN -- the handler returns 1, :1392.
        St { kind: s.kind, val: s.val, ts: s.ts, acc: a, pc: s.pc, done: true }
    }
}

/// `execute()`'s loop, :1383-1394, driven to its fixpoint. ⚠ The guards on the
/// recursive call are what make the `decreases` syntactic; `ok_from` is what
/// makes them never taken.
pub open spec fn run(ops: Seq<Op>, n: int, s: St) -> St
    decreases n - s.pc,
{
    if s.done || s.pc >= n || s.pc < 0 {
        s
    } else {
        let s2 = step(ops, s);
        if s2.done {
            s2
        } else if s2.pc > s.pc && s2.pc <= n {
            run(ops, n, s2)
        } else {
            s2
        }
    }
}

/// One decoded `zend_op`. The blob IS the instruction stream.
pub open spec fn dec_word(win: Seq<u8>, i: int) -> Op {
    Op {
        opcode: (win[8 * i] % N_OPCODES),
        ext: win[8 * i + 1],
        op1: (win[8 * i + 2] as u16) | ((win[8 * i + 3] as u16) << 8),
        op2: (win[8 * i + 4] as u16) | ((win[8 * i + 5] as u16) << 8),
        result: (win[8 * i + 6] as u16) | ((win[8 * i + 7] as u16) << 8),
        handler: None,
    }
}

pub open spec fn with_opcode(o: Op, oc: u8) -> Op {
    Op { opcode: oc, ext: o.ext, op1: o.op1, op2: o.op2, result: o.result, handler: o.handler }
}

/// The decoder, plus PHP's own tail: `zend_do_end_function_declaration` emits
/// `zend_do_return` then `zend_do_handle_exception`
/// (Zend/zend_compile.c:1091-1092). Two terminators and a maximum stride of
/// two is what keeps the PC inside the op_array -- ../NOTES.md §4.
pub open spec fn decoded(win: Seq<u8>, nops: int) -> Seq<Op> {
    let base = Seq::new(
        MAX_OPS as nat,
        |i: int| if 0 <= i < nops { dec_word(win, i) } else { ZERO_OP },
    );
    base.update(nops - 2, with_opcode(base[nops - 2], RETURN)).update(
        nops - 1,
        with_opcode(base[nops - 1], RETURN),
    )
}

/// THE EMITTER'S GUARANTEE, as a sequence transformation. `zend_compile` emits
/// `ZEND_OP_DATA` only as the trailing word of a two-word instruction, so no
/// instruction START is a data word. ⭐ It touches ONLY the words a correct
/// executor visits, which is what lets `adversarial-opdatalive.bin` exist.
pub open spec fn emitted(ops: Seq<Op>, n: int, p: int) -> Seq<Op>
    decreases n - p,
{
    if p + 2 >= n || p < 0 {
        ops
    } else {
        let o = if ops[p].opcode == OP_DATA { with_opcode(ops[p], NOP) } else { ops[p] };
        let ops2 = ops.update(p, o);
        let q = p + width_s(o);
        if q > p && q <= n {
            emitted(ops2, n, q)
        } else {
            ops2
        }
    }
}

/// `pass_two` -- zend_opcode.c:363.
pub open spec fn with_handler(o: Op) -> Op {
    Op {
        opcode: o.opcode,
        ext: o.ext,
        op1: o.op1,
        op2: o.op2,
        result: o.result,
        handler: if o.opcode == OP_DATA { None::<u8> } else { Some(o.opcode) },
    }
}

pub open spec fn passed(ops: Seq<Op>, nops: int) -> Seq<Op> {
    Seq::new(ops.len(), |i: int| if 0 <= i < nops { with_handler(ops[i]) } else { ops[i] })
}

/// The frame `execute()` builds -- :1345-1363.
pub open spec fn init_kind() -> Seq<u8> {
    Seq::new(NSLOT as nat, |i: int| if i < VAR_BASE { IS_NULL } else { IS_LONG })
}

pub open spec fn init_st() -> St {
    St {
        kind: init_kind(),
        val: Seq::new(NSLOT as nat, |i: int| 0u64),
        ts: Seq::new(NT as nat, |i: int| 0u16),
        acc: 0,
        pc: 0,
        done: false,
    }
}

/// What `php_execute_script` observes: the store the program left behind.
pub open spec fn fold_slots(kind: Seq<u8>, val: Seq<u64>, acc: u64, i: int) -> u64
    decreases NSLOT - i,
{
    if i >= NSLOT as int || i < 0 {
        acc
    } else {
        fold_slots(
            kind,
            val,
            acc.wrapping_mul(31).wrapping_add(kind[i] as u64).wrapping_mul(31).wrapping_add(val[i]),
            i + 1,
        )
    }
}

pub open spec fn fold_ts(ts: Seq<u16>, acc: u64, i: int) -> u64
    decreases NT - i,
{
    if i >= NT as int || i < 0 {
        acc
    } else {
        fold_ts(ts, acc.wrapping_mul(31).wrapping_add(ts[i] as u64), i + 1)
    }
}

/// What the kernel must return. `model.py::ph55_run` re-derives it.
pub open spec fn ph55_fold(buf: Seq<u8>, off: int, ln: int) -> u64 {
    let win = buf.subrange(off, off + ln);
    let nops = ln / 8;
    let ops = passed(emitted(decoded(win, nops), nops, 0), nops);
    let s = run(ops, nops, init_st());
    fold_ts(s.ts, fold_slots(s.kind, s.val, s.acc, 0), 0)
}

// ------------------------------------------------------- TRUSTED, item 1/8 --
// `v[i]` with no bounds check. Sound iff `i < v.len()`. ../NOTES.md §10 argues
// each of the eight.
#[verifier::external_body]
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

// ------------------------------------------------------- TRUSTED, item 2/8 --
#[verifier::external_body]
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

// ------------------------------------------------------- TRUSTED, item 3/8 --
#[verifier::external_body]
fn oset(a: &mut [Op; MAX_OPS], i: usize, x: Op)
    requires
        i < MAX_OPS,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    unsafe { *a.get_unchecked_mut(i) = x };
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

// ------------------------------------------------------- TRUSTED, item 4/8 --
#[verifier::external_body]
fn kget(a: &[u8; NSLOT], i: usize) -> (r: u8)
    requires
        i < NSLOT,
    ensures
        r == a@[i as int],
{
    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_kget(a: &[u8; NSLOT], i: usize) -> (r: u8)
    requires
        i < NSLOT,
    ensures
        r == a@[i as int],
{
    a[i]
}

// ------------------------------------------------------- TRUSTED, item 5/8 --
#[verifier::external_body]
fn kset(a: &mut [u8; NSLOT], i: usize, x: u8)
    requires
        i < NSLOT,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    unsafe { *a.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
fn slb_twin_kset(a: &mut [u8; NSLOT], i: usize, x: u8)
    requires
        i < NSLOT,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    a[i] = x;
}

// ------------------------------------------------------- TRUSTED, item 6/8 --
#[verifier::external_body]
fn vget(a: &[u64; NSLOT], i: usize) -> (r: u64)
    requires
        i < NSLOT,
    ensures
        r == a@[i as int],
{
    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_vget(a: &[u64; NSLOT], i: usize) -> (r: u64)
    requires
        i < NSLOT,
    ensures
        r == a@[i as int],
{
    a[i]
}

// ------------------------------------------------------- TRUSTED, item 7/8 --
#[verifier::external_body]
fn vset(a: &mut [u64; NSLOT], i: usize, x: u64)
    requires
        i < NSLOT,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    unsafe { *a.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
fn slb_twin_vset(a: &mut [u64; NSLOT], i: usize, x: u64)
    requires
        i < NSLOT,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    a[i] = x;
}

// ------------------------------------------------------- TRUSTED, item 8/8 --
// ⭐⭐ THE ROW'S OWN TRUSTED ITEM. `t.unwrap()` with no `None` test -- the exact
// operation C performs when it calls through `opline->handler` without testing
// it (zend_execute.c:1391). ⚠ The `requires` is what makes it sound and the
// `ensures` is what makes it useful, and the `requires` is discharged by
// `ok_from`, which is the 2004 patch's own invariant.
#[verifier::external_body]
fn hunwrap(t: Option<u8>) -> (r: u8)
    requires
        t.is_some(),
    ensures
        r == t.unwrap(),
{
    unsafe { t.unwrap_unchecked() }
}

#[cfg(slb_twin)]
fn slb_twin_hunwrap(t: Option<u8>) -> (r: u8)
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

// `println!` is not verifiable; no `ensures`. Counted with the eight above --
// every `external_body` item is TCB, not just the interesting ones
// (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----

#[inline(always)]
fn two_word(o: Op) -> (r: bool)
    ensures
        r == two_word_s(o),
{
    o.opcode == ASSIGN_DIM || (o.opcode == ASSIGN_ADD && o.ext == X_DIM)
}

#[inline(always)]
fn is_tmp(o: u16) -> (r: bool)
    ensures
        r == s_is_tmp(o),
{
    (o & 0x8000) != 0
}

#[inline(always)]
fn var_of(o: u16) -> (r: usize)
    ensures
        r == s_var_of(o),
        r < NSLOT,
{
    VAR_BASE + ((o & 0x7FFF) as usize) % NVAR
}

#[inline(always)]
fn tmp_of(o: u16) -> (r: usize)
    ensures
        r == s_tmp_of(o),
        r < NT,
{
    ((o & 0x7FFF) as usize) % NT
}

/// THE EMITTER'S GUARANTEE, AND IT IS THE COMPILER'S -- ../NOTES.md §4.
///
/// ⭐⭐ TAIL RECURSION, so the postcondition IS `ok_from`'s own unfolding: two
/// `reveal_with_fuel` asserts and no lemma. A `while` loop would need an
/// invariant quantified over instruction starts plus a glue lemma. The shape of
/// the property decided the shape of the code, in EVERY Rust rung.
fn emit_from(ops: &mut [Op; MAX_OPS], n: usize, p: usize)
    requires
        old(ops)@.len() == MAX_OPS,
        n <= MAX_OPS,
        n >= 2,
        p <= n,
        old(ops)@[n as int - 2].opcode == RETURN,
        old(ops)@[n as int - 1].opcode == RETURN,
    ensures
        final(ops)@.len() == MAX_OPS,
        ok_from(final(ops)@, n as int, p as int),
        forall|j: int| 0 <= j < p && j < MAX_OPS ==> final(ops)@[j] == old(ops)@[j],
        forall|j: int| n <= j < MAX_OPS ==> final(ops)@[j] == old(ops)@[j],
        final(ops)@[n as int - 2] == old(ops)@[n as int - 2],
        final(ops)@[n as int - 1] == old(ops)@[n as int - 1],
        final(ops)@ == emitted(old(ops)@, n as int, p as int),
    decreases n - p,
{
    if p + 2 >= n {
        assert(ok_from(ops@, n as int, p as int)) by {
            reveal_with_fuel(ok_from, 4);
        }
        assert(ops@ == emitted(ops@, n as int, p as int)) by {
            reveal_with_fuel(emitted, 2);
        }
        return ;
    }
    let ghost pre = ops@;
    let mut o: Op = oget(ops, p);
    if o.opcode == OP_DATA {
        o.opcode = NOP;
        oset(ops, p, o);
    }
    let ghost mid = pre.update(p as int, o);
    assert(ops@ =~= mid);
    let q: usize = p + if two_word(o) { 2 } else { 1 };
    assert(q == p + width_s(o));
    emit_from(ops, n, q);
    assert(ops@[p as int] == o);
    assert(ok_from(ops@, n as int, p as int)) by {
        reveal_with_fuel(ok_from, 2);
    }
    assert(emitted(pre, n as int, p as int) == emitted(mid, n as int, q as int)) by {
        reveal_with_fuel(emitted, 2);
    }
}

#[inline(always)]
fn gzpp(kind: &[u8; NSLOT], val: &[u64; NSLOT], ts: &[u16; NT], op: u16) -> (r: u16)
    requires
        all_slots(ts@),
        ts@.len() == NT,
        kind@.len() == NSLOT,
        val@.len() == NSLOT,
    ensures
        r < NSLOT,
        r as int == s_gzpp(
            St { kind: kind@, val: val@, ts: ts@, acc: 0, pc: 0, done: false },
            op,
        ),
{
    if is_tmp(op) {
        ts[tmp_of(op)]
    } else {
        var_of(op) as u16
    }
}

#[inline(always)]
fn gzp(kind: &[u8; NSLOT], val: &[u64; NSLOT], ts: &[u16; NT], op: u16) -> (r: u64)
    requires
        all_slots(ts@),
        ts@.len() == NT,
        kind@.len() == NSLOT,
        val@.len() == NSLOT,
    ensures
        r == s_gzp(St { kind: kind@, val: val@, ts: ts@, acc: 0, pc: 0, done: false }, op),
{
    let s = gzpp(kind, val, ts, op) as usize;
    if kget(kind, s) == IS_LONG {
        vget(val, s)
    } else {
        0
    }
}

#[inline(always)]
fn fetch_dim(kind: &[u8; NSLOT], val: &[u64; NSLOT], ts: &[u16; NT], base: u16, dim: u16) -> (r: u16)
    requires
        kind@.len() == NSLOT,
        val@.len() == NSLOT,
        ts@.len() == NT,
    ensures
        r < NSLOT,
        r as int == s_fetch(
            St { kind: kind@, val: val@, ts: ts@, acc: 0, pc: 0, done: false },
            base,
            dim,
        ),
{
    let b = var_of(base);
    if kget(kind, b) != IS_ARRAY {
        return ERR;
    }
    let x: usize = (vget(val, b) % (NVAR as u64)) as usize;
    let y: usize = (dim as usize) % DIM;
    (ARR_BASE + x * DIM + y) as u16
}

// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// One `ensures`, and it is the VALUE, not the safety property. What makes it
// worth having: it is what stops the proof being vacuous, it is what `model.py`
// re-derives independently, and it is what forces the invariants to describe the
// whole machine rather than merely bound the PC. A kernel that returned 0
// unconditionally would satisfy every bounds obligation in this file.
//
// ⭐⭐⭐ **NO `#[verifier::rlimit]`, AND THAT IS A MEASUREMENT.** Verus's default
// is 10. Bisected on this box (`controls/rlimit_bisect.sh`, log in
// `../NOTES.md` §10):
//
//     rlimit  1   53 verified / 0 errors plain,  60 / 1 under --cfg slb_twin
//     rlimit  2   53 / 0 plain,                  61 / 0 twin
//     rlimit 30   53 / 0 plain,                  61 / 0 twin
//
// So the whole proof -- an interpreter, ten handlers, a value postcondition
// over the entire machine state, and EIGHT verified twins -- needs **2**, and
// the default is 5x that. ⚠ Compare `ph16`, whose obligation is a single index
// bound with no loop in it and which had to ship `#[verifier::rlimit(30)]`
// because its twin build FAILED at 8. ▶ The reason is structural and it is this
// row's Verus finding: every obligation here is ONE unfolding of a recursive
// definition that the exec code's own shape mirrors, so Z3 never searches.
// `../NOTES.md` §10.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
        16 <= len,
        len <= 8 * MAX_OPS,
    ensures
        r == ph55_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = &buf[off..off + len];
    assert(win@.len() == vstd::slice::spec_slice_len(win));
    assert(win@ =~= buf@.subrange(off as int, off + len));
    let nops: usize = len / 8;
    assert(2 <= nops <= MAX_OPS);

    // -- the decoder -------------------------------------------------------
    let mut ops: [Op; MAX_OPS] = [ZERO_OP; MAX_OPS];
    let mut i: usize = 0;
    while i < nops
        invariant
            i <= nops,
            nops <= MAX_OPS,
            8 * nops <= win@.len(),
            ops@.len() == MAX_OPS,
            forall|j: int| 0 <= j < i ==> #[trigger] ops@[j] == dec_word(win@, j),
            forall|j: int| i <= j < MAX_OPS ==> #[trigger] ops@[j] == ZERO_OP,
        decreases nops - i,
    {
        oset(&mut ops, i, Op {
            opcode: bget(win, 8 * i) % N_OPCODES,
            ext: bget(win, 8 * i + 1),
            op1: (bget(win, 8 * i + 2) as u16) | ((bget(win, 8 * i + 3) as u16) << 8),
            op2: (bget(win, 8 * i + 4) as u16) | ((bget(win, 8 * i + 5) as u16) << 8),
            result: (bget(win, 8 * i + 6) as u16) | ((bget(win, 8 * i + 7) as u16) << 8),
            handler: None,
        });
        i = i + 1;
    }
    let ghost base = Seq::new(
        MAX_OPS as nat,
        |j: int| if 0 <= j < nops as int { dec_word(win@, j) } else { ZERO_OP },
    );
    assert(ops@ =~= base);
    // `zend_do_return` then `zend_do_handle_exception` -- zend_compile.c:1091-1092.
        // ⚠⚠ THE KERNEL'S OWN PRECONDITION, STATED WHERE THE LANGUAGE CAN STATE
        // IT. `verus.rs` says `requires 16 <= len` in ONE LINE; C has no
        // signature to say it in and pays a run-time compare, and without it
        // gcc's `-Wstringop-overflow` fires on the C kernel in every inlined
        // cell. Carried in EVERY rung so the compare is on both sides of the
        // cross-language column. `../NOTES.md` §8.
    if nops >= 2 {
        let mut e: Op = oget(&ops, nops - 2);
        e.opcode = RETURN;
        oset(&mut ops, nops - 2, e);
        let mut e2: Op = oget(&ops, nops - 1);
        e2.opcode = RETURN;
        oset(&mut ops, nops - 1, e2);
    }
    assert(ops@ =~= decoded(win@, nops as int));

    // -- THE EMITTER'S GUARANTEE ------------------------------------------
    let ghost dec = ops@;
    emit_from(&mut ops, nops, 0);
    assert(ops@ == emitted(dec, nops as int, 0));
    assert(ok_from(ops@, nops as int, 0));

    // -- pass_two -- zend_opcode.c:363 ------------------------------------
    let ghost em = ops@;
    let mut i: usize = 0;
    while i < nops
        invariant
            i <= nops,
            nops <= MAX_OPS,
            ops@.len() == MAX_OPS,
            forall|j: int|
                0 <= j < i ==> #[trigger] ops@[j] == with_handler(em[j]),
            forall|j: int| i <= j < MAX_OPS ==> #[trigger] ops@[j] == em[j],
        decreases nops - i,
    {
        let mut o: Op = oget(&ops, i);
        o.handler = if o.opcode == OP_DATA { None } else { Some(o.opcode) };
        oset(&mut ops, i, o);
        i = i + 1;
    }
    assert(ops@ =~= passed(em, nops as int));
    // ⭐ `pass_two` does not change any opcode, so the emitter's guarantee
    // survives it -- and that is why a NULL handler can only be reached by a
    // PC that is not an instruction start.
    assert(ok_from(ops@, nops as int, 0)) by {
        assert(forall|j: int| 0 <= j < MAX_OPS ==> #[trigger] ops@[j].opcode == em[j].opcode);
        lemma_ok_from_opcodes(em, ops@, nops as int, 0);
    }
    assert(handlers_ok(ops@, nops as int));

    // -- the frame, :1345-1363 --------------------------------------------
    let mut kind: [u8; NSLOT] = [IS_NULL; NSLOT];
    let mut val: [u64; NSLOT] = [0u64; NSLOT];
    let mut ts: [u16; NT] = [0u16; NT];
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    while i < NVAR
        invariant
            i <= NVAR,
            kind@.len() == NSLOT,
            forall|j: int| 0 <= j < VAR_BASE ==> #[trigger] kind@[j] == IS_NULL,
            forall|j: int| VAR_BASE <= j < VAR_BASE + i ==> #[trigger] kind@[j] == IS_LONG,
            forall|j: int| VAR_BASE + i <= j < NSLOT ==> #[trigger] kind@[j] == IS_NULL,
        decreases NVAR - i,
    {
        kset(&mut kind, VAR_BASE + i, IS_LONG);
        i = i + 1;
    }
    let mut i: usize = 0;
    while i < NVAR * DIM
        invariant
            i <= NVAR * DIM,
            kind@.len() == NSLOT,
            forall|j: int| 0 <= j < VAR_BASE ==> #[trigger] kind@[j] == IS_NULL,
            forall|j: int| VAR_BASE <= j < ARR_BASE + i ==> #[trigger] kind@[j] == IS_LONG,
            forall|j: int| ARR_BASE + i <= j < NSLOT ==> #[trigger] kind@[j] == IS_NULL,
        decreases NVAR * DIM - i,
    {
        kset(&mut kind, ARR_BASE + i, IS_LONG);
        i = i + 1;
    }
    assert(kind@ =~= init_kind());
    assert(val@ =~= init_st().val);
    assert(ts@ =~= init_st().ts);

    // -- execute()'s dispatch loop, :1383-1394 ----------------------------
    let ghost target = run(ops@, nops as int, init_st());
    let mut pc: usize = 0;
    loop
        invariant_except_break
            // ⚠ EXCEPT AT THE BREAK, and that is not a technicality: the
            // opcode fold happens BEFORE the dispatch (`zend_clean_garbage` is
            // at :1390 and the call at :1391), so at the `ZEND_RETURN` break
            // `acc` has already absorbed the terminator and one more `step`
            // would absorb it twice. The `ensures` below is what the loop
            // leaves behind instead.
            run(
                ops@,
                nops as int,
                St { kind: kind@, val: val@, ts: ts@, acc, pc: pc as int, done: false },
            ) == target,
        invariant
            ops@.len() == MAX_OPS,
            kind@.len() == NSLOT,
            val@.len() == NSLOT,
            ts@.len() == NT,
            nops <= MAX_OPS,
            nops >= 2,
            pc < nops,
            all_slots(ts@),
            handlers_ok(ops@, nops as int),
            ok_from(ops@, nops as int, pc as int),
            ops@[nops as int - 2].opcode == RETURN,
            ops@[nops as int - 1].opcode == RETURN,
        ensures
            kind@ == target.kind,
            val@ == target.val,
            ts@ == target.ts,
            acc == target.acc,
            kind@.len() == NSLOT,
            val@.len() == NSLOT,
            ts@.len() == NT,
        decreases nops - pc,
    {
        let ghost cur = St { kind: kind@, val: val@, ts: ts@, acc, pc: pc as int, done: false };
        let o: Op = oget(&ops, pc);
        assert(o.opcode != OP_DATA);
        assert(o.handler.is_some());
        acc = acc.wrapping_mul(31).wrapping_add(o.opcode as u64);
        // ⭐⭐ THE ROW. In C this is `EX(opline)->handler(...)` with nothing in
        // between. `hunwrap`'s `requires t.is_some()` is discharged by
        // `ok_from`: the PC is on an instruction word.
        let h: u8 = hunwrap(o.handler);
        assert(h == o.opcode);
        // ⚠ PHP's own tail is what bounds the PC: the last two words are
        // ZEND_RETURN, so any word the executor does NOT stop on is at least
        // two from the end and both `opline + 1` and `opline + width` are
        // inside the op_array. ../NOTES.md §4.
        assert(h != RETURN ==> pc + 2 < nops);
        if h == NOP {
            pc = pc + 1;
        } else if h == ASSIGN {
            let d = var_of(o.op1);
            kset(&mut kind, d, IS_LONG);
            vset(&mut val, d, o.op2 as u64);
            let t = tmp_of(o.result);
            ts[t] = d as u16;
            pc = pc + 1;
        } else if h == INIT_ARRAY {
            let d = var_of(o.op1);
            kset(&mut kind, d, IS_ARRAY);
            let m: usize = (o.op2 as usize) % NVAR;
            vset(&mut val, d, m as u64);
            let t = tmp_of(o.result);
            ts[t] = d as u16;
            pc = pc + 1;
        } else if h == ADD {
            let a = gzp(&kind, &val, &ts, o.op1);
            let b = gzp(&kind, &val, &ts, o.op2);
            let d = var_of(o.result);
            kset(&mut kind, d, IS_LONG);
            vset(&mut val, d, a.wrapping_add(b));
            pc = pc + 1;
        } else if h == FETCH_DIM_RW {
            let s = fetch_dim(&kind, &val, &ts, o.op1, o.op2);
            let t = tmp_of(o.result);
            ts[t] = s;
            pc = pc + 1;
        } else if h == ASSIGN_DIM {
            assert(pc + 1 < nops);
            let od: Op = oget(&ops, pc + 1);
            let dst = fetch_dim(&kind, &val, &ts, o.op1, o.op2);
            let t1 = tmp_of(od.op2);
            ts[t1] = dst;
            let value = gzp(&kind, &val, &ts, od.op1);
            if dst != ERR {
                kset(&mut kind, dst as usize, IS_LONG);
                vset(&mut val, dst as usize, value);
            }
            let t2 = tmp_of(o.result);
            ts[t2] = dst;
            pc = pc + 2;
        } else if h == ASSIGN_ADD {
            assert(pc + 1 < nops);
            let od: Op = oget(&ops, pc + 1);
            let inc: bool = o.ext == X_DIM;
            let value: u64;
            let var_ptr: u16;
            if inc {
                let s = fetch_dim(&kind, &val, &ts, o.op1, o.op2);
                let t1 = tmp_of(od.op2);
                ts[t1] = s;
                value = gzp(&kind, &val, &ts, od.op1);
                var_ptr = gzpp(&kind, &val, &ts, od.op2);
            } else {
                value = gzp(&kind, &val, &ts, o.op2);
                var_ptr = gzpp(&kind, &val, &ts, o.op1);
            }
            if var_ptr == ERR {
                let t2 = tmp_of(o.result);
                ts[t2] = UNINIT;
                if inc {
                    pc = pc + 1;
                }
                pc = pc + 1;
            } else {
                let d = var_ptr as usize;
                let cur0: u64 = if kget(&kind, d) == IS_LONG { vget(&val, d) } else { 0 };
                kset(&mut kind, d, IS_LONG);
                vset(&mut val, d, cur0.wrapping_add(value));
                let t2 = tmp_of(o.result);
                ts[t2] = var_ptr;
                if inc {
                    pc = pc + 1;
                }
                pc = pc + 1;
            }
        } else if h == ECHO {
            let s = gzpp(&kind, &val, &ts, o.op1) as usize;
            acc = acc.wrapping_mul(31).wrapping_add(kget(&kind, s) as u64);
            acc = acc.wrapping_mul(31).wrapping_add(vget(&val, s));
            pc = pc + 1;
        } else {
            // ZEND_RETURN -- the handler returns 1, :1392, and `execute()`
            // returns. This is the ONLY exit from the loop.
            assert(step(ops@, cur).done);
            assert(run(ops@, nops as int, cur) == step(ops@, cur)) by {
                reveal_with_fuel(run, 2);
            }
            assert(kind@ == target.kind);
            assert(val@ == target.val);
            assert(ts@ == target.ts);
            assert(acc == target.acc);
            break ;
        }
        let ghost cur2 = St { kind: kind@, val: val@, ts: ts@, acc, pc: pc as int, done: false };
        assert(cur2 == step(ops@, cur));
        assert(cur2.pc > cur.pc);
        assert(cur2.pc <= nops as int);
        assert(run(ops@, nops as int, cur) == run(ops@, nops as int, cur2)) by {
            reveal_with_fuel(run, 2);
        }
    }

    // -- the fold ----------------------------------------------------------
    let ghost fin = target;
    assert(kind@ == fin.kind && val@ == fin.val && ts@ == fin.ts && acc == fin.acc);
    let ghost tgt2 = fold_slots(kind@, val@, acc, 0);
    let mut i: usize = 0;
    while i < NSLOT
        invariant
            i <= NSLOT,
            kind@.len() == NSLOT,
            val@.len() == NSLOT,
            fold_slots(kind@, val@, acc, i as int) == tgt2,
        decreases NSLOT - i,
    {
        acc = acc.wrapping_mul(31).wrapping_add(kget(&kind, i) as u64);
        acc = acc.wrapping_mul(31).wrapping_add(vget(&val, i));
        i = i + 1;
    }
    let ghost tgt3 = fold_ts(ts@, acc, 0);
    let mut i: usize = 0;
    while i < NT
        invariant
            i <= NT,
            ts@.len() == NT,
            fold_ts(ts@, acc, i as int) == tgt3,
        decreases NT - i,
    {
        acc = acc.wrapping_mul(31).wrapping_add(ts[i] as u64);
        i = i + 1;
    }
    acc
}

/// `ok_from` depends on `opcode` and `ext` only, so `pass_two` -- which writes
/// `handler` and nothing else -- cannot disturb it.
pub proof fn lemma_ok_from_opcodes(a: Seq<Op>, b: Seq<Op>, n: int, p: int)
    requires
        a.len() == b.len(),
        n <= a.len(),
        0 <= p,
        forall|j: int| 0 <= j < a.len() ==> #[trigger] b[j].opcode == a[j].opcode,
        forall|j: int| 0 <= j < a.len() ==> #[trigger] b[j].ext == a[j].ext,
        ok_from(a, n, p),
    ensures
        ok_from(b, n, p),
    decreases n - p,
{
    if p >= n {
    } else {
        let q = p + width_s(a[p]);
        assert(width_s(b[p]) == width_s(a[p]));
        if q > p && q <= n {
            lemma_ok_from_opcodes(a, b, n, q);
        }
    }
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
            assert(r == ph55_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
