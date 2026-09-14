//! ph55 rung R4 -- unsafe.
//!
//! R3 with the checks removed: `get_unchecked` where R3 indexes the window, the
//! op_array and the two slot arrays, and ⭐ **`unwrap_unchecked()` where R3
//! opens the handler `Option`.** Nothing else changes -- same decode, same
//! emitter fixup, same `pass_two`, same handlers, same strides.
//!
//! ⚠⚠⚠ **THE LAST ONE IS THE ROW, AND IT IS THE ONLY UNCHECKED OPERATION HERE
//! WHOSE PRECONDITION IS NOT ARITHMETIC.** `hunwrap(o.handler)` is sound iff
//! `o.handler.is_some()`, i.e. iff `ops[pc].opcode != OP_DATA`, i.e. iff **the
//! PC is on an instruction word and not on a data word.** That is *the*
//! invariant PHP 5.0.0's executor relies on and never tests (`zend_execute.c`
//! `:1391`), and it is exactly what `zend_binary_assign_op_helper`'s error exit
//! breaks. **`verus.rs` proves that implication**, and
//! `controls/negatives.py --emit nofixup` removes the emitter pass that
//! establishes it -- that mutant must FAIL to verify.
//!
//! ⭐ The other unchecked classes rest on DIFFERENT and much duller facts:
//!
//!   * `bget(win, ..)` on `off + len <= buf.len()` plus `nops = len / 8`, from
//!     the driver's own contract -- nothing to do with PHP;
//!   * `oget/oset(ops, ..)` on `nops <= MAX_OPS`, from `c/main.c`'s
//!     `stride_w <= 512`, likewise;
//!   * `kget/vget/kset/vset(.., s)` on `s < NSLOT`, an invariant over the temp
//!     slots: every value ever written into `ts` is a slot index. That one is
//!     a real invariant of the interpreter and `../NOTES.md` §10 keeps it apart
//!     from the PC one, because an editor who deleted the 2004 patch would be
//!     removing the precondition of ONE of these classes and not the others.
//!
//! ⚠ **`ts` IS DELIBERATELY STILL CHECKED.** `tmp_of` is `(op & 0x7FFF) % NT`
//! with `NT` a constant, so LLVM proves the bound itself and emits nothing; an
//! `unsafe` there would add a trusted item and buy zero instructions.
//! `../NOTES.md` §10 has the count.
//!
//! ⚠⚠ **R4 AND R5 DO *NOT* PRODUCE THE SAME MACHINE CODE ON THIS ROW, AND THE
//! FIRST DRAFT OF THIS COMMENT SAID THEY MUST.** `../spec.md`'s `identity` pins
//! `differ` at BOTH levels and the gate record MEASURES `differ` at both -- 876
//! instructions against 872 at `O3/isolated`, and `norel` differs too, so it is
//! not relocation bytes. ⭐ **The EXEC CODE is character-identical**: the only
//! differences are R5's `verus!` block, its spec/proof items and the
//! `requires`/`ensures` on these wrappers. What moves is register allocation
//! and scheduling, for a cause `../NOTES.md` §10d does NOT identify and says so.
//! ⭐⭐ **CONSEQUENCE, AND IT IS NOT A FORMALITY:**
//! `.memory/02-bench-rules.md` makes Miri NON-WAIVABLE when R4 and R5 are not
//! the same machine code, so this row's `miri.required` is load-bearing twice
//! over -- once for the eight trusted items and once for this.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
const MAX_OPS: usize = 64;

const NVAR: usize = 8;
const DIM: usize = 4;
const NT: usize = 4;

const UNINIT: u16 = 0;
const ERR: u16 = 1;
const VAR_BASE: usize = 2;
const ARR_BASE: usize = VAR_BASE + NVAR;
const NSLOT: usize = ARR_BASE + NVAR * DIM;

const IS_NULL: u8 = 0;
const IS_LONG: u8 = 1;
const IS_ARRAY: u8 = 2;

const NOP: u8 = 0;
const ASSIGN: u8 = 1;
const INIT_ARRAY: u8 = 2;
const ADD: u8 = 3;
const FETCH_DIM_RW: u8 = 4;
const ASSIGN_DIM: u8 = 5;
const ASSIGN_ADD: u8 = 6;
const OP_DATA: u8 = 7;
const ECHO: u8 = 8;
const RETURN: u8 = 9;
const N_OPCODES: u8 = 10;

const X_DIM: u8 = 1;

#[derive(Clone, Copy)]
struct Op {
    opcode: u8,
    ext: u8,
    op1: u16,
    op2: u16,
    result: u16,
    handler: Option<u8>,
}

const ZERO_OP: Op = Op { opcode: 0, ext: 0, op1: 0, op2: 0, result: 0, handler: None };

#[inline(always)]
fn two_word(o: Op) -> bool {
    o.opcode == ASSIGN_DIM || (o.opcode == ASSIGN_ADD && o.ext == X_DIM)
}

#[inline(always)]
fn is_tmp(o: u16) -> bool {
    (o & 0x8000) != 0
}

#[inline(always)]
fn var_of(o: u16) -> usize {
    VAR_BASE + ((o & 0x7FFF) as usize) % NVAR
}

#[inline(always)]
fn tmp_of(o: u16) -> usize {
    ((o & 0x7FFF) as usize) % NT
}

// ------------------------------------------------------- unchecked access ---
// The eight operations verus.rs makes TRUSTED. Same names, same signatures,
// same bodies; there they carry a `requires`/`ensures` pair and here they carry
// this comment.

/// `v[i]` with no bounds check. Sound iff `i < v.len()`.
#[inline(always)]
fn bget(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

/// `a[i]` with no bounds check. Sound iff `i < MAX_OPS`.
#[inline(always)]
fn oget(a: &[Op; MAX_OPS], i: usize) -> Op {
    unsafe { *a.get_unchecked(i) }
}

/// `a[i] = x` with no bounds check. Sound iff `i < MAX_OPS`.
#[inline(always)]
fn oset(a: &mut [Op; MAX_OPS], i: usize, x: Op) {
    unsafe { *a.get_unchecked_mut(i) = x };
}

/// `a[i]` with no bounds check. Sound iff `i < NSLOT`.
#[inline(always)]
fn kget(a: &[u8; NSLOT], i: usize) -> u8 {
    unsafe { *a.get_unchecked(i) }
}

/// `a[i] = x` with no bounds check. Sound iff `i < NSLOT`.
#[inline(always)]
fn kset(a: &mut [u8; NSLOT], i: usize, x: u8) {
    unsafe { *a.get_unchecked_mut(i) = x };
}

/// `a[i]` with no bounds check. Sound iff `i < NSLOT`.
#[inline(always)]
fn vget(a: &[u64; NSLOT], i: usize) -> u64 {
    unsafe { *a.get_unchecked(i) }
}

/// `a[i] = x` with no bounds check. Sound iff `i < NSLOT`.
#[inline(always)]
fn vset(a: &mut [u64; NSLOT], i: usize, x: u64) {
    unsafe { *a.get_unchecked_mut(i) = x };
}

/// ⭐⭐ `t.unwrap()` with no `None` test -- the exact operation C performs when
/// it calls through `opline->handler` without testing it. Sound iff
/// `t.is_some()`, i.e. iff the PC is on an instruction word.
#[inline(always)]
fn hunwrap(t: Option<u8>) -> u8 {
    unsafe { t.unwrap_unchecked() }
}


/// THE EMITTER'S GUARANTEE, AND IT IS THE COMPILER'S. `zend_compile` emits
/// `ZEND_OP_DATA` only as the trailing word of a two-word instruction, so no
/// instruction START is a data word -- which is why `execute()` may dispatch
/// through `opline->handler` without testing it (zend_execute.c:1391). The
/// compiler is outside this row, so this walk stands in for it; it touches only
/// the words a CORRECT executor visits, which is what lets
/// `inputs/adversarial-opdatalive.bin` exist at all. `../NOTES.md` §4.
///
/// ⚠⚠ **TAIL RECURSION AND NOT A LOOP, AND THAT IS A VERUS DECISION SHOWING
/// THROUGH INTO EVERY RUST RUNG.** The property it establishes -- `ok_from` in
/// `verus.rs` -- is defined by recursion on the chain, so written this way the
/// postcondition IS the definition's own unfolding and needs no lemma; written
/// as a `while` loop it needs an invariant quantified over instruction starts
/// and a glue lemma. `c/kernel.c` writes the loop, because C has nothing to
/// prove. `../spec.md` `provenance.divergences` itemises it and `../NOTES.md`
/// §10 prices it.
fn emit_from(ops: &mut [Op; MAX_OPS], n: usize, p: usize) {
    if p + 2 >= n {
        return;
    }
    let mut o: Op = oget(ops, p);
    if o.opcode == OP_DATA {
        o.opcode = NOP;
        oset(ops, p, o);
    }
    let q: usize = p + if two_word(o) { 2 } else { 1 };
    emit_from(ops, n, q);
}

// ---------------------------------------------------------------- kernel ----

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];
    let nops: usize = len / 8;

    let mut ops: [Op; MAX_OPS] = [ZERO_OP; MAX_OPS];
    let mut i: usize = 0;
    while i < nops {
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
        // ⚠⚠ THE KERNEL'S OWN PRECONDITION, STATED WHERE THE LANGUAGE CAN STATE
        // IT. `verus.rs` says `requires 16 <= len` in ONE LINE; C has no
        // signature to say it in and pays a run-time compare, and without it
        // gcc's `-Wstringop-overflow` fires on the C kernel in every inlined
        // cell. Carried in EVERY rung so the compare is on both sides of the
        // cross-language column. `../NOTES.md` §8.
    if nops >= 2 {
        let mut e: Op = oget(&ops, nops - 2);
        e.opcode = RETURN; // zend_do_return
        oset(&mut ops, nops - 2, e);
        let mut e2: Op = oget(&ops, nops - 1);
        e2.opcode = RETURN; // zend_do_handle_exception
        oset(&mut ops, nops - 1, e2);
    }

    // THE EMITTER'S GUARANTEE, AND IT IS THE COMPILER'S -- ../NOTES.md §4.
    emit_from(&mut ops, nops, 0);

    // pass_two -- zend_opcode.c:363.
    let mut i: usize = 0;
    while i < nops {
        let mut o: Op = oget(&ops, i);
        o.handler = if o.opcode == OP_DATA { None } else { Some(o.opcode) };
        oset(&mut ops, i, o);
        i = i + 1;
    }

    let mut kind: [u8; NSLOT] = [IS_NULL; NSLOT];
    let mut val: [u64; NSLOT] = [0u64; NSLOT];
    let mut ts: [u16; NT] = [0u16; NT];
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    while i < NVAR {
        kset(&mut kind, VAR_BASE + i, IS_LONG);
        i = i + 1;
    }
    let mut i: usize = 0;
    while i < NVAR * DIM {
        kset(&mut kind, ARR_BASE + i, IS_LONG);
        i = i + 1;
    }

    // execute()'s dispatch loop, :1383-1394.
    let mut pc: usize = 0;
    loop {
        let o: Op = oget(&ops, pc);
        acc = acc.wrapping_mul(31).wrapping_add(o.opcode as u64);
        // ⭐⭐ THE ROW. In C this is `EX(opline)->handler(...)` with nothing in
        // between; here it is the same, and what licenses it is the proof that
        // the PC is on an instruction word.
        let h: u8 = hunwrap(o.handler);
        if h == NOP {
            pc = pc + 1;
        } else if h == ASSIGN {
            let d = var_of(o.op1);
            kset(&mut kind, d, IS_LONG);
            vset(&mut val, d, o.op2 as u64);
            ts[tmp_of(o.result)] = d as u16;
            pc = pc + 1;
        } else if h == INIT_ARRAY {
            let d = var_of(o.op1);
            kset(&mut kind, d, IS_ARRAY);
            vset(&mut val, d, (o.op2 as usize % NVAR) as u64);
            ts[tmp_of(o.result)] = d as u16;
            pc = pc + 1;
        } else if h == ADD {
            let a = gzp(&kind, &val, &ts, o.op1);
            let b = gzp(&kind, &val, &ts, o.op2);
            let d = var_of(o.result);
            kset(&mut kind, d, IS_LONG);
            vset(&mut val, d, a.wrapping_add(b));
            pc = pc + 1;
        } else if h == FETCH_DIM_RW {
            let s = fetch_dim(&kind, &val, o.op1, o.op2);
            ts[tmp_of(o.result)] = s;
            pc = pc + 1;
        } else if h == ASSIGN_DIM {
            let od: Op = oget(&ops, pc + 1);
            let dst = fetch_dim(&kind, &val, o.op1, o.op2);
            ts[tmp_of(od.op2)] = dst;
            let value = gzp(&kind, &val, &ts, od.op1);
            if dst != ERR {
                kset(&mut kind, dst as usize, IS_LONG);
                vset(&mut val, dst as usize, value);
            }
            ts[tmp_of(o.result)] = dst;
            pc = pc + 2;
        } else if h == ASSIGN_ADD {
            let mut increment_opline: bool = false; // :1728
            let value: u64;
            let var_ptr: u16;
            if o.ext == X_DIM {
                let od: Op = oget(&ops, pc + 1); // op_data = opline + 1, :1742
                let s = fetch_dim(&kind, &val, o.op1, o.op2);
                ts[tmp_of(od.op2)] = s; // :1744
                value = gzp(&kind, &val, &ts, od.op1); // :1746
                var_ptr = gzpp(&ts, od.op2); // :1747
                increment_opline = true; // :1749
            } else {
                value = gzp(&kind, &val, &ts, o.op2); // :1754
                var_ptr = gzpp(&ts, o.op1); // :1755
            }
            if var_ptr == ERR {
                // :1765
                ts[tmp_of(o.result)] = UNINIT; // :1766
                if increment_opline {
                    pc = pc + 1; // 4f68f3774c34
                }
                pc = pc + 1; // :1769
            } else {
                let d = var_ptr as usize;
                if kget(&kind, d) != IS_LONG {
                    kset(&mut kind, d, IS_LONG);
                    vset(&mut val, d, 0);
                }
                // ⚠ The read is bound OUT of the call: `vset(&mut val, d,
                // vget(&val, d) ...)` is E0502 -- two borrows of one array in
                // one expression -- and no `unsafe` inside the accessors
                // changes that, because the rule is about the CALL and not
                // about the body. ../NOTES.md §10; the C writes
                // `ex->val[dst] += v` and has nothing to say about it.
                let cur: u64 = vget(&val, d);
                vset(&mut val, d, cur.wrapping_add(value)); // :1783
                ts[tmp_of(o.result)] = var_ptr; // :1786
                if increment_opline {
                    pc = pc + 1; // :1793
                }
                pc = pc + 1; // :1795
            }
        } else if h == ECHO {
            let s = gzpp(&ts, o.op1) as usize;
            acc = acc.wrapping_mul(31).wrapping_add(kget(&kind, s) as u64);
            acc = acc.wrapping_mul(31).wrapping_add(vget(&val, s));
            pc = pc + 1;
        } else {
            break; // RETURN, :1392
        }
    }

    let mut i: usize = 0;
    while i < NSLOT {
        acc = acc.wrapping_mul(31).wrapping_add(kget(&kind, i) as u64);
        acc = acc.wrapping_mul(31).wrapping_add(vget(&val, i));
        i = i + 1;
    }
    let mut i: usize = 0;
    while i < NT {
        acc = acc.wrapping_mul(31).wrapping_add(ts[i] as u64);
        i = i + 1;
    }
    acc
}

#[inline(always)]
fn gzpp(ts: &[u16; NT], op: u16) -> u16 {
    if is_tmp(op) {
        ts[tmp_of(op)]
    } else {
        var_of(op) as u16
    }
}

#[inline(always)]
fn gzp(kind: &[u8; NSLOT], val: &[u64; NSLOT], ts: &[u16; NT], op: u16) -> u64 {
    let s = gzpp(ts, op) as usize;
    if kget(kind, s) == IS_LONG {
        vget(val, s)
    } else {
        0
    }
}

#[inline(always)]
fn fetch_dim(kind: &[u8; NSLOT], val: &[u64; NSLOT], base: u16, dim: u16) -> u16 {
    let b = var_of(base);
    if kget(kind, b) != IS_ARRAY {
        return ERR;
    }
    (ARR_BASE + ((vget(val, b) as usize) % NVAR) * DIM + ((dim as usize) % DIM)) as u16
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 16 && stride_w <= 512 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(buf, k * stride, stride);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
