//! ph55 rung R3 -- safe-tuned.
//!
//! R2 respelled, still 100 % safe and still `unwrap()`. **Three levers, and all
//! three are about how often the SAME fact is re-established**:
//!
//!   1. ⭐ **`let o = ops[pc];` ONCE per dispatch.** `Op` is 16 bytes and
//!      `Copy`, so this is one load and one bounds check where R2 pays one per
//!      field -- and the C pays NONE, because `opline` is a pointer it already
//!      holds (`opline->op1`, `opline->op2`, `opline->result` are offsets off a
//!      register). ⚠ THIS IS THE LEVER THAT IS ABOUT THE ROW: a dispatch loop
//!      reads its current instruction four or five times, so a re-index per
//!      field is a per-field bounds check in the hottest loop in the program.
//!   2. `let od = ops[pc + 1];` once in each two-word arm, for the same reason.
//!   3. the decoder binds the eight payload bytes through ONE slice
//!      (`&win[8 * i..8 * i + 8]`) instead of eight independent index
//!      expressions.
//!
//! ⚠ NOTHING ELSE MOVES. Same algorithm, same arrays, same `unwrap()`, same
//! answer on every input -- the gate's stage 3 checksum comparison is what says
//! so. `../NOTES.md` §8 reads the gradient off the disassembly rather than
//! asserting it, and §11 records what it did and did not buy.
//!
//! ⚠⚠ **THE `ts` READS ARE DELIBERATELY LEFT ALONE, AND THAT IS A MEASUREMENT
//! AND NOT AN OVERSIGHT**: `tmp_of` is `(op & 0x7FFF) % NT` with `NT` a
//! constant, so LLVM already proves `0 <= i < NT` and emits no check. A lever
//! that buys nothing is worth naming as one that was tried.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py. See ../spec.md for why each is what it is.

/// The op_array's capacity. `c/main.c`'s `stride_w <= 512` is the same bound
/// in the driver, outside every measured loop.
const MAX_OPS: usize = 64;

const NVAR: usize = 8; // CV slots
const DIM: usize = 4; // elements per array
const NT: usize = 4; // temp_variable slots

const UNINIT: u16 = 0; // EG(uninitialized_zval_ptr)
const ERR: u16 = 1; // EG(error_zval_ptr)
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
/// ⭐ `zend_opcode_handlers[ZEND_OP_DATA] = NULL;` -- zend_execute.c:4427. The
/// one opcode with no handler.
const OP_DATA: u8 = 7;
const ECHO: u8 = 8;
const RETURN: u8 = 9;
const N_OPCODES: u8 = 10;

const X_DIM: u8 = 1; // ZEND_ASSIGN_DIM, as `opline->extended_value`

/// `zend_op`, narrowed. `handler` is what `pass_two` writes -- zend_opcode.c:363.
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

/// How wide an instruction is. ⚠ `ASSIGN_DIM` is two words for EVERY instance
/// (`zend_assign_dim_handler`, :2198-2226, one exit, no flag); `ASSIGN_ADD` is
/// two words only when its `extended_value` says so (:1734, :1749). That
/// difference is the row.
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
    let mut o: Op = ops[p];
    if o.opcode == OP_DATA {
        o.opcode = NOP;
        ops[p] = o;
    }
    let q: usize = p + if two_word(o) { 2 } else { 1 };
    emit_from(ops, n, q);
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];
    let nops: usize = len / 8;

    // -- the decoder. The blob IS the instruction stream, one zend_op per
    // little-endian u64. The last two words are ZEND_RETURN, which is PHP's
    // own tail (zend_compile.c:1091-1092) and what keeps the PC inside the
    // op_array -- ../NOTES.md §4.
    let mut ops: [Op; MAX_OPS] = [ZERO_OP; MAX_OPS];
    let mut i: usize = 0;
    while i < nops {
        let b: &[u8] = &win[8 * i..8 * i + 8]; // LEVER 3
        ops[i] = Op {
            opcode: b[0] % N_OPCODES,
            ext: b[1],
            op1: (b[2] as u16) | ((b[3] as u16) << 8),
            op2: (b[4] as u16) | ((b[5] as u16) << 8),
            result: (b[6] as u16) | ((b[7] as u16) << 8),
            handler: None,
        };
        i = i + 1;
    }
        // ⚠⚠ THE KERNEL'S OWN PRECONDITION, STATED WHERE THE LANGUAGE CAN STATE
        // IT. `verus.rs` says `requires 16 <= len` in ONE LINE; C has no
        // signature to say it in and pays a run-time compare, and without it
        // gcc's `-Wstringop-overflow` fires on the C kernel in every inlined
        // cell. Carried in EVERY rung so the compare is on both sides of the
        // cross-language column. `../NOTES.md` §8.
    if nops >= 2 {
        ops[nops - 2].opcode = RETURN; // zend_do_return
        ops[nops - 1].opcode = RETURN; // zend_do_handle_exception
    }

    // -- THE EMITTER'S GUARANTEE, AND IT IS THE COMPILER'S. `zend_compile`
    // emits ZEND_OP_DATA only as the trailing word of a two-word instruction,
    // so no instruction START is a data word -- which is why `execute()` may
    // dispatch through `opline->handler` without testing it. The compiler is
    // outside this row, so this walk stands in for it; it touches only the
    // words a CORRECT executor visits. ../NOTES.md §4.
    emit_from(&mut ops, nops, 0);

    // -- pass_two: `opline->handler = zend_opcode_handlers[opline->opcode];`
    // zend_opcode.c:363. The table is copied into EVERY instruction, which is
    // how a NULL entry becomes reachable from a PC.
    let mut i: usize = 0;
    while i < nops {
        ops[i].handler = if ops[i].opcode == OP_DATA { None } else { Some(ops[i].opcode) };
        i = i + 1;
    }

    // -- the frame. `execute()` :1345-1363.
    let mut kind: [u8; NSLOT] = [IS_NULL; NSLOT];
    let mut val: [u64; NSLOT] = [0u64; NSLOT];
    let mut ts: [u16; NT] = [0u16; NT];
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    while i < NVAR {
        kind[VAR_BASE + i] = IS_LONG;
        i = i + 1;
    }
    let mut i: usize = 0;
    while i < NVAR * DIM {
        kind[ARR_BASE + i] = IS_LONG;
        i = i + 1;
    }

    // -- execute()'s dispatch loop, :1383-1394.
    let mut pc: usize = 0;
    loop {
        // ⭐ LEVER 1: ONE load, ONE bounds check, for the whole dispatch.
        let o: Op = ops[pc];
        acc = acc.wrapping_mul(31).wrapping_add(o.opcode as u64);
        // `if (EX(opline)->handler(&execute_data, EX(opline), op_array))`.
        // ⭐ In C there is nothing between the field and the call. In safe Rust
        // the `Option` CANNOT be called without being opened, so this is where
        // a NULL handler becomes a panic instead of a jump to address zero.
        let h: u8 = o.handler.unwrap();
        if h == NOP {
            pc = pc + 1;
        } else if h == ASSIGN {
            let d = var_of(o.op1);
            kind[d] = IS_LONG;
            val[d] = o.op2 as u64;
            ts[tmp_of(o.result)] = d as u16;
            pc = pc + 1;
        } else if h == INIT_ARRAY {
            let d = var_of(o.op1);
            kind[d] = IS_ARRAY;
            val[d] = (o.op2 as usize % NVAR) as u64;
            ts[tmp_of(o.result)] = d as u16;
            pc = pc + 1;
        } else if h == ADD {
            // ⚠ BOTH OPERANDS BEFORE THE DESTINATION -- `result` may name the
            // same slot as `op1`. model.py's synthetic sweep caught exactly
            // that in this row's first draft.
            let a = gzp(&kind, &val, &ts, o.op1);
            let b = gzp(&kind, &val, &ts, o.op2);
            let d = var_of(o.result);
            kind[d] = IS_LONG;
            val[d] = a.wrapping_add(b);
            pc = pc + 1;
        } else if h == FETCH_DIM_RW {
            let s = fetch_dim(&kind, &val, o.op1, o.op2);
            ts[tmp_of(o.result)] = s;
            pc = pc + 1;
        } else if h == ASSIGN_DIM {
            // zend_assign_dim_handler, :2198-2226 -- THE CLEAN SIBLING. Two
            // words STATICALLY, one exit, `assign_dim has two opcodes!`.
            let od: Op = ops[pc + 1]; // LEVER 2
            let dst = fetch_dim(&kind, &val, o.op1, o.op2);
            ts[tmp_of(od.op2)] = dst;
            let value = gzp(&kind, &val, &ts, od.op1);
            if dst != ERR {
                kind[dst as usize] = IS_LONG;
                val[dst as usize] = value;
            }
            ts[tmp_of(o.result)] = dst;
            pc = pc + 2; // INC_OPCODE(); NEXT_OPCODE();
        } else if h == ASSIGN_ADD {
            // zend_binary_assign_op_helper, :1724-1796 -- THE DEFECT'S SITE,
            // with 4f68f3774c34 applied.
            let mut increment_opline: bool = false; // :1728
            let value: u64;
            let var_ptr: u16;
            if o.ext == X_DIM {
                // case ZEND_ASSIGN_DIM: :1734.  op_data = opline + 1, :1742
                let od: Op = ops[pc + 1]; // LEVER 2.  op_data = opline + 1, :1742
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
                // :1765 -- `*var_ptr == EG(error_zval_ptr)`
                ts[tmp_of(o.result)] = UNINIT; // :1766
                // 4f68f3774c34: the normal exit's own three lines, here.
                if increment_opline {
                    pc = pc + 1;
                }
                pc = pc + 1; // NEXT_OPCODE(), :1769
            } else {
                let d = var_ptr as usize; // :1783 binary_op(...)
                if kind[d] != IS_LONG {
                    kind[d] = IS_LONG;
                    val[d] = 0;
                }
                val[d] = val[d].wrapping_add(value);
                ts[tmp_of(o.result)] = var_ptr; // :1786
                if increment_opline {
                    // :1792
                    pc = pc + 1; // :1793
                }
                pc = pc + 1; // :1795
            }
        } else if h == ECHO {
            let s = gzpp(&ts, o.op1) as usize;
            acc = acc.wrapping_mul(31).wrapping_add(kind[s] as u64);
            acc = acc.wrapping_mul(31).wrapping_add(val[s]);
            pc = pc + 1;
        } else {
            break; // RETURN -- the handler returns 1, :1392
        }
    }

    // What `php_execute_script` observes: the store the program left behind.
    let mut i: usize = 0;
    while i < NSLOT {
        acc = acc.wrapping_mul(31).wrapping_add(kind[i] as u64);
        acc = acc.wrapping_mul(31).wrapping_add(val[i]);
        i = i + 1;
    }
    let mut i: usize = 0;
    while i < NT {
        acc = acc.wrapping_mul(31).wrapping_add(ts[i] as u64);
        i = i + 1;
    }
    acc
}

/// `get_zval_ptr_ptr` -- an operand names a CV slot unless its top bit is set,
/// in which case it names a temp (`IS_VAR`).
#[inline(always)]
fn gzpp(ts: &[u16; NT], op: u16) -> u16 {
    if is_tmp(op) {
        ts[tmp_of(op)]
    } else {
        var_of(op) as u16
    }
}

/// `get_zval_ptr`.
#[inline(always)]
fn gzp(kind: &[u8; NSLOT], val: &[u64; NSLOT], ts: &[u16; NT], op: u16) -> u64 {
    let s = gzpp(ts, op) as usize;
    if kind[s] == IS_LONG {
        val[s]
    } else {
        0
    }
}

/// `zend_fetch_dimension_address(..., BP_VAR_RW)` -- :1744. ⭐ On a non-array
/// base it yields `EG(error_zval_ptr)`, which is `$x = 1; $x[0] += 1;` -- the
/// corpus's own trigger for CRASH-023.
#[inline(always)]
fn fetch_dim(kind: &[u8; NSLOT], val: &[u64; NSLOT], base: u16, dim: u16) -> u16 {
    let b = var_of(base);
    if kind[b] != IS_ARRAY {
        return ERR;
    }
    (ARR_BASE + ((val[b] as usize) % NVAR) * DIM + ((dim as usize) % DIM)) as u16
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
