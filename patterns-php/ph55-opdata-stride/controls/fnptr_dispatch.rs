//! ph55 control -- **WHAT THE ROW'S DISPATCH WOULD LOOK LIKE IF VERUS ALLOWED
//! IT**, so that the substitution `controls/fnptr.rs` forces can be PRICED
//! rather than asserted.
//!
//!     python3 patterns-php/ph55-opdata-stride/controls/fnptr_cost.py
//!
//! This is `../safe_naive.rs`'s algorithm with C's own representation restored:
//! `Op::handler` is an `Option<fn(&mut Ex) -> bool>` -- a REAL function pointer,
//! one per handler, exactly as `zend_op::handler` is -- and the dispatch loop
//! calls through it. It is legal Rust and it compiles; `controls/fnptr.rs`
//! shows that Verus refuses the TYPE, which is why no rung may use it
//! (`../spec.md` `identity` pins R4 == R5).
//!
//! ⚠⚠ **IT IS A CONTROL AND NOT A RUNG.** `controls/fnptr_cost.py` asserts it
//! produces byte-identical checksums to `../safe_naive.rs` on every shipped
//! input before quoting any number from it, because a variant that has drifted
//! is not measuring the substitution.
//!
//! ⭐ **AND IT CHANGES NO BEHAVIOUR, WHICH IS THE POINT.** `Option<fn>` and
//! `Option<u8>` are `None` for exactly the same opcode -- `ZEND_OP_DATA`, whose
//! table entry `zend_execute.c:4427` sets to NULL -- so both spellings turn C's
//! NULL CALL into the same `unwrap()` panic. What moves is instructions.
//!
//! ⚠ The state is a `struct Ex` here where the rungs keep plain locals, and
//! that is FORCED rather than chosen: a function pointer has one signature, so
//! every handler must take the same argument, which in C is
//! `(zend_execute_data *, zend_op *)` and here is `&mut Ex`. `fnptr_cost.py`
//! therefore reports the pair as "representation + frame", not as a clean
//! one-variable difference, and says so.

#![allow(dead_code)]

#[path = "../../../common/driver.rs"]
mod driver;

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

/// `opcode_handler_t` -- Zend/zend_execute.h, and the type Verus refuses.
type Handler = fn(&mut Ex) -> bool;

#[derive(Clone, Copy)]
struct Op {
    opcode: u8,
    ext: u8,
    op1: u16,
    op2: u16,
    result: u16,
    handler: Option<Handler>,
}

const ZERO_OP: Op = Op { opcode: 0, ext: 0, op1: 0, op2: 0, result: 0, handler: None };

/// `zend_execute_data`. ⚠ A struct rather than locals because a function
/// pointer has ONE signature: every handler must take the same argument.
struct Ex {
    ops: [Op; MAX_OPS],
    kind: [u8; NSLOT],
    val: [u64; NSLOT],
    ts: [u16; NT],
    acc: u64,
    pc: usize,
}

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

impl Ex {
    #[inline(always)]
    fn gzpp(&self, op: u16) -> u16 {
        if is_tmp(op) {
            self.ts[tmp_of(op)]
        } else {
            var_of(op) as u16
        }
    }

    #[inline(always)]
    fn gzp(&self, op: u16) -> u64 {
        let s = self.gzpp(op) as usize;
        if self.kind[s] == IS_LONG {
            self.val[s]
        } else {
            0
        }
    }

    #[inline(always)]
    fn fetch_dim(&self, base: u16, dim: u16) -> u16 {
        let b = var_of(base);
        if self.kind[b] != IS_ARRAY {
            return ERR;
        }
        (ARR_BASE + ((self.val[b] % (NVAR as u64)) as usize) * DIM + ((dim as usize) % DIM)) as u16
    }
}

// ---- the handlers, one function each, exactly as zend_execute.c has them ----

fn h_nop(ex: &mut Ex) -> bool {
    ex.pc += 1;
    false
}

fn h_assign(ex: &mut Ex) -> bool {
    let o = ex.ops[ex.pc];
    let d = var_of(o.op1);
    ex.kind[d] = IS_LONG;
    ex.val[d] = o.op2 as u64;
    let t = tmp_of(o.result);
    ex.ts[t] = d as u16;
    ex.pc += 1;
    false
}

fn h_init_array(ex: &mut Ex) -> bool {
    let o = ex.ops[ex.pc];
    let d = var_of(o.op1);
    ex.kind[d] = IS_ARRAY;
    ex.val[d] = (o.op2 as usize % NVAR) as u64;
    let t = tmp_of(o.result);
    ex.ts[t] = d as u16;
    ex.pc += 1;
    false
}

fn h_add(ex: &mut Ex) -> bool {
    let o = ex.ops[ex.pc];
    let a = ex.gzp(o.op1);
    let b = ex.gzp(o.op2);
    let d = var_of(o.result);
    ex.kind[d] = IS_LONG;
    ex.val[d] = a.wrapping_add(b);
    ex.pc += 1;
    false
}

fn h_fetch_dim_rw(ex: &mut Ex) -> bool {
    let o = ex.ops[ex.pc];
    let s = ex.fetch_dim(o.op1, o.op2);
    let t = tmp_of(o.result);
    ex.ts[t] = s;
    ex.pc += 1;
    false
}

/// `zend_assign_dim_handler` -- zend_execute.c:2198-2226, the clean sibling.
fn h_assign_dim(ex: &mut Ex) -> bool {
    let o = ex.ops[ex.pc];
    let od = ex.ops[ex.pc + 1];
    let dst = ex.fetch_dim(o.op1, o.op2);
    let t1 = tmp_of(od.op2);
    ex.ts[t1] = dst;
    let value = ex.gzp(od.op1);
    if dst != ERR {
        ex.kind[dst as usize] = IS_LONG;
        ex.val[dst as usize] = value;
    }
    let t2 = tmp_of(o.result);
    ex.ts[t2] = dst;
    ex.pc += 2; // INC_OPCODE(); NEXT_OPCODE();
    false
}

/// `zend_binary_assign_op_helper` -- zend_execute.c:1724-1796, with
/// `4f68f3774c34` applied, exactly as every shipped rung has it.
fn h_assign_add(ex: &mut Ex) -> bool {
    let o = ex.ops[ex.pc];
    let od = ex.ops[ex.pc + 1];
    let mut increment_opline = false;
    let value: u64;
    let var_ptr: u16;
    if o.ext == X_DIM {
        let s = ex.fetch_dim(o.op1, o.op2);
        let t1 = tmp_of(od.op2);
        ex.ts[t1] = s;
        value = ex.gzp(od.op1);
        var_ptr = ex.gzpp(od.op2);
        increment_opline = true;
    } else {
        value = ex.gzp(o.op2);
        var_ptr = ex.gzpp(o.op1);
    }
    if var_ptr == ERR {
        let t2 = tmp_of(o.result);
        ex.ts[t2] = UNINIT;
        if increment_opline {
            ex.pc += 1;
        }
        ex.pc += 1;
    } else {
        let d = var_ptr as usize;
        if ex.kind[d] != IS_LONG {
            ex.kind[d] = IS_LONG;
            ex.val[d] = 0;
        }
        ex.val[d] = ex.val[d].wrapping_add(value);
        let t2 = tmp_of(o.result);
        ex.ts[t2] = var_ptr;
        if increment_opline {
            ex.pc += 1;
        }
        ex.pc += 1;
    }
    false
}

fn h_echo(ex: &mut Ex) -> bool {
    let o = ex.ops[ex.pc];
    let s = ex.gzpp(o.op1) as usize;
    ex.acc = ex.acc.wrapping_mul(31).wrapping_add(ex.kind[s] as u64);
    ex.acc = ex.acc.wrapping_mul(31).wrapping_add(ex.val[s]);
    ex.pc += 1;
    false
}

/// `ZEND_RETURN` -- the only handler that leaves the loop.
fn h_return(_ex: &mut Ex) -> bool {
    true
}

/// `zend_opcode_handlers[512]` -- zend_execute.c:1338, and the ONE entry this
/// row turns on is `[OP_DATA] = None`, i.e. `:4427`'s `= NULL`.
const HANDLERS: [Option<Handler>; N_OPCODES as usize] = [
    Some(h_nop as Handler),
    Some(h_assign as Handler),
    Some(h_init_array as Handler),
    Some(h_add as Handler),
    Some(h_fetch_dim_rw as Handler),
    Some(h_assign_dim as Handler),
    Some(h_assign_add as Handler),
    None, // ⭐ zend_opcode_handlers[ZEND_OP_DATA] = NULL;  :4427
    Some(h_echo as Handler),
    Some(h_return as Handler),
];

/// THE EMITTER'S GUARANTEE -- ../NOTES.md §4. Same tail recursion as the rungs.
fn emit_from(ops: &mut [Op; MAX_OPS], n: usize, p: usize) {
    if p + 2 >= n {
        return;
    }
    let mut o: Op = ops[p];
    if o.opcode == OP_DATA {
        o.opcode = NOP;
        ops[p] = o;
    }
    let q: usize = p + if two_word(o) { 2 } else { 1 };
    emit_from(ops, n, q);
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];
    let nops: usize = len / 8;

    let mut ops: [Op; MAX_OPS] = [ZERO_OP; MAX_OPS];
    let mut i: usize = 0;
    while i < nops {
        ops[i] = Op {
            opcode: win[8 * i] % N_OPCODES,
            ext: win[8 * i + 1],
            op1: (win[8 * i + 2] as u16) | ((win[8 * i + 3] as u16) << 8),
            op2: (win[8 * i + 4] as u16) | ((win[8 * i + 5] as u16) << 8),
            result: (win[8 * i + 6] as u16) | ((win[8 * i + 7] as u16) << 8),
            handler: None,
        };
        i = i + 1;
    }
    if nops >= 2 {
        ops[nops - 2].opcode = RETURN;
        ops[nops - 1].opcode = RETURN;
    }
    emit_from(&mut ops, nops, 0);

    // pass_two -- zend_opcode.c:363, and here it really does copy a POINTER.
    let mut i: usize = 0;
    while i < nops {
        ops[i].handler = HANDLERS[ops[i].opcode as usize];
        i = i + 1;
    }

    let mut ex = Ex {
        ops,
        kind: [IS_NULL; NSLOT],
        val: [0u64; NSLOT],
        ts: [0u16; NT],
        acc: 0,
        pc: 0,
    };
    let mut i: usize = 0;
    while i < NVAR {
        ex.kind[VAR_BASE + i] = IS_LONG;
        i = i + 1;
    }
    let mut i: usize = 0;
    while i < NVAR * DIM {
        ex.kind[ARR_BASE + i] = IS_LONG;
        i = i + 1;
    }

    // execute()'s dispatch loop, :1383-1394 -- through a real function pointer.
    loop {
        let h = ex.ops[ex.pc].handler;
        ex.acc = ex.acc.wrapping_mul(31).wrapping_add(ex.ops[ex.pc].opcode as u64);
        let f = h.unwrap();
        if f(&mut ex) {
            break;
        }
    }

    let mut acc = ex.acc;
    let mut i: usize = 0;
    while i < NSLOT {
        acc = acc.wrapping_mul(31).wrapping_add(ex.kind[i] as u64);
        acc = acc.wrapping_mul(31).wrapping_add(ex.val[i]);
        i = i + 1;
    }
    let mut i: usize = 0;
    while i < NT {
        acc = acc.wrapping_mul(31).wrapping_add(ex.ts[i] as u64);
        i = i + 1;
    }
    acc
}

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
