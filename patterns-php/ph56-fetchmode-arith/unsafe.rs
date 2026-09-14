//! ph56 rung R4 -- unsafe.
//!
//! ⭐⭐⭐ **R4 IS R3 WITH THE CHECKS REMOVED THROUGH TEN TRUSTED ACCESSORS, AND
//! THE TENTH IS THE ROW.** Nine of them are ordinary unchecked indexing --
//! `oget`/`oset` on the op_array, `sget`/`sset` on the zval store, `tget`/`tset`
//! on the temp vector, `nget`/`nset` on the next-free indices, and `bget` on the
//! input window. The tenth, `zunwrap`, is `Option::unwrap_unchecked` on the
//! OPERAND, and it is the exact operation `zend_isset_isempty_dim_prop_obj_handler`
//! performs at `zend_execute.c:3973` when it writes `switch (offset->type)`
//! without testing `offset`.
//!
//! ⚠⚠ **SO THE R3 -> R4 STEP ON THIS ROW IS NOT A GENERIC BOUNDS-CHECK STORY:
//! ONE OF THE TEN CHECKS IT DELETES IS THE CHECK WHOSE ABSENCE IS CRASH-041.**
//! `zunwrap`'s `requires t.is_some()` is a proof obligation that is DISCHARGED
//! BY THE COMPILER PASS -- an opcode that reads op2 is only ever emitted with
//! op2 present -- and that is exactly the invariant `1e708a5aeb30` restores.
//! `../NOTES.md` §9.
//!
//! Everything else is `safe_tuned.rs` unchanged: same algorithm, same order of operations, same answer on every
//! input, still zero `unsafe`. Three levers, and each is a bounds check the
//! naive rung pays that the optimiser cannot always remove for it:
//!
//!   1. **the record decoder** takes ONE subslice per statement --
//!      `let p: &[u8; 8] = win[8*i..8*i+8].try_into().unwrap()` -- instead of
//!      eight independent `win[8*i + k]` indexings. The `try_into` on a
//!      fixed-size array turns eight checks into one, and the compiler then
//!      knows every `p[k]` is in range from the TYPE.
//!   2. **the container zval is read once** into a local at the top of
//!      `fetch_dimension_address` instead of being re-indexed for each of the
//!      four type tests, which is what the C does anyway (`container` is a
//!      pointer, read once at `:898`).
//!   3. **the UNINIT refcount** is held in a local across the append arm's two
//!      writes, so the `+1` and the conditional `-1` are one load and one
//!      store rather than two of each.
//!
//! ⚠⚠ **THE `unwrap()` STAYS, AND THAT IS THE POINT OF THE RUNG.** R3 is what a
//! performance-minded programmer writes while still refusing `unsafe`; the
//! operand `Option` is opened by a CHECKED unwrap here and by an unchecked one
//! in R4, and the R3 -> R4 step is the price of that one check. Nothing else
//! differs between them. `../NOTES.md` §9.
//!
//! ⚠⚠ **READ THIS BEFORE COMPARING THIS RUNG TO R1h.** The four Rust rungs
//! implement **exactly** what `c/kernel_hardened.c` implements -- PHP 5.0.0's
//! compiler plus the three lines of `1e708a5aeb30` (Marcus Boerger,
//! 2004-08-29, *"Bugfix #29882 isset crashes on arrays"*) -- because that fix
//! is COMPLETE for the defect: it removes both of this row's harms and changes
//! no benign answer (`controls/fix_scope.py`). The ladder reads:
//!
//!     R1    zend_compile.c:736-780 as shipped 5.0.0 -- CRASH-041
//!     R1h   + 1e708a5aeb30's three lines
//!     R2-5  the same function, in Rust
//!
//! ⭐⭐ **WHERE THE ROW LIVES IN THIS FILE IS ONE `unwrap()`.**
//! `zend_isset_isempty_dim_prop_obj_handler` reads `opline->op2` through
//! `get_zval_ptr`, which has an explicit `case IS_UNUSED: return NULL;`
//! (zend_execute.c:118-121), and then dereferences the result at
//! `switch (offset->type)` (:3973) with nothing in between. In C that is a read
//! of address `0x14` -- `offsetof(zval, type)` is 20, and a pristine 5.0.0 CLI
//! faults at exactly that, as does `c/kernel.c`. **In safe Rust the `Option`
//! cannot be dereferenced without being opened**, so the same wrong program is
//! a panic with a message instead of a jump into the zero page.
//!
//! ⚠ **THAT IS A DIFFERENT OUTCOME, NOT A DIFFERENT PROGRAM.** The compiler
//! still emits `ZEND_ISSET_ISEMPTY_DIM_OBJ` with an absent operand; what
//! changes is only what happens when the executor reads it. `../NOTES.md` §6
//! prices the pair, and `controls/unused_operand.py` runs both languages on the
//! same bytes.
//!
//! ⭐ **AND THE ROW'S SECOND HARM IS NOT CAUGHT BY ANYTHING, IN EITHER
//! LANGUAGE.** `inputs/adversarial-chain.bin` sets one bit -- the chain bit of
//! one record, which is `isset($a[][0])` rather than `isset($a[])` -- and the
//! `[]` opline then survives as `ZEND_FETCH_DIM_IS`, reaches
//! `zend_fetch_dimension_address`'s append arm (:935-943), and **grows the
//! array**. Exit 0, a plausible answer, and no diagnostic from any detector in
//! this tree. Measured on the pristine CLI as well: `count($a)` goes 3 -> 4.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py. See ../spec.md for why each is what it is.

/// Statement records per window. `c/main.c`'s `stride_w <= 512` is the same
/// bound in the driver, outside every measured loop.
const MAX_STMT: usize = 64;
/// A chained statement (`$a[][d]`) emits two oplines, so the op_array is twice
/// the record count.
const MAX_OPS: usize = 2 * MAX_STMT;

const NVAR: usize = 8; // CV slots
const DIM: usize = 4; // elements per array

const UNINIT: u16 = 0; // EG(uninitialized_zval) -- THE GLOBAL THE APPEND TAKES
const ERR: u16 = 1; // EG(error_zval)
const VAR_BASE: usize = 2;
const ARR_BASE: usize = VAR_BASE + NVAR;
const NSLOT: usize = ARR_BASE + NVAR * DIM;

const IS_NULL: u8 = 0;
const IS_LONG: u8 = 1;
const IS_ARRAY: u8 = 2;
const IS_STRING: u8 = 3;

// `znode.op_type` -- zend_compile.h:285-288, upstream's own bit values, because
// `IS_UNUSED` is the value the guard this row is about tests for.
const T_CONST: u8 = 1; // IS_CONST  (1<<0)
const T_VAR: u8 = 4; // IS_VAR    (1<<2)
const T_UNUSED: u8 = 8; // IS_UNUSED (1<<3)

// The six access modes -- zend_compile.h:756-762, upstream's own values.
const BP_R: u8 = 0;
const BP_W: u8 = 1;
const BP_RW: u8 = 2;
const BP_IS: u8 = 3;
const BP_FUNC_ARG: u8 = 5;
const BP_UNSET: u8 = 6;

// ⭐⭐ THE REAL OPCODE NUMBERS, AND THEY ARE LOAD-BEARING. zend_compile.h:636-638
// says, in upstream's own words and exclamation mark: *the following 18 opcodes
// are 6 groups of 3 opcodes each, and must remain in that order!* The compiler
// selects a mode by ARITHMETIC over exactly that layout, so keeping the literal
// values means this row's arithmetic is upstream's arithmetic.
const FETCH_DIM_R: u8 = 81;
const FETCH_W: u8 = 83;
const FETCH_DIM_W: u8 = 84;
const FETCH_OBJ_W: u8 = 85;
const FETCH_DIM_RW: u8 = 87;
const FETCH_IS: u8 = 89;
const FETCH_DIM_IS: u8 = 90;
const FETCH_OBJ_IS: u8 = 91;
const FETCH_DIM_FUNC_ARG: u8 = 93;
const FETCH_DIM_UNSET: u8 = 96;
const ISSET_ISEMPTY_VAR: u8 = 114;
const ISSET_ISEMPTY_DIM_OBJ: u8 = 115;
const ISSET_ISEMPTY_PROP_OBJ: u8 = 148;

const MODES: [u8; 6] = [BP_R, BP_W, BP_RW, BP_IS, BP_FUNC_ARG, BP_UNSET];
const BASES: [u8; 3] = [FETCH_W, FETCH_DIM_W, FETCH_OBJ_W];
const OP2T: [u8; 3] = [T_UNUSED, T_CONST, T_VAR];

/// `zend_op`, narrowed.
#[derive(Clone, Copy)]
struct Op {
    opcode: u8,
    op1_type: u8,
    op2_type: u8,
    ext: u8,
    op1: u16,
    op2: u16,
    result: u16,
}

const ZERO_OP: Op =
    Op { opcode: 0, op1_type: 0, op2_type: 0, ext: 0, op1: 0, op2: 0, result: 0 };

/// `zval`. ⚠ The FIELD ORDER is upstream's so that `c/kernel.c`'s fault lands
/// on upstream's own offset; Rust has no pointer to fault through, but the two
/// rungs must fold the same fields in the same order or the gate's cross-rung
/// checksum would be comparing different functions.
#[derive(Clone, Copy)]
struct Zv {
    lval: u64,
    value_hi: u64,
    refcount: u32,
    ty: u8,
    is_ref: u8,
}

const ZERO_ZV: Zv = Zv { lval: 0, value_hi: 0, refcount: 0, ty: 0, is_ref: 0 };

// ------------------------------------------------- the trusted accessors ---
// ⚠⚠ TEN ITEMS, AND EACH ONE IS A LINE OF TRUSTED BASE. They are written as
// wrappers rather than inline `unsafe` blocks because R5 must be able to give
// each a `requires`/`ensures` pair: Verus cannot see through `get_unchecked`,
// so the obligation has to live on a signature. `../spec.md`'s
// `unsafe_justifications` carries one entry per item.

/// `win[i]`. SAFETY: `i < v.len()`, which every caller establishes from the
/// driver's `off + len <= buf_len` and its own loop bound.
#[inline(always)]
fn bget(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

/// `ops[i]`. SAFETY: `i < MAX_OPS`. The array's length is in its TYPE, so the
/// index is the only quantity that can make this undefined.
#[inline(always)]
fn oget(a: &[Op; MAX_OPS], i: usize) -> Op {
    unsafe { *a.get_unchecked(i) }
}

/// `ops[i] = x`. SAFETY: `i < MAX_OPS`. `x: Op` is a PURE VALUE and needs no
/// precondition -- every inhabitant of `Op` is a legal store into a slot that
/// is already initialised (`[ZERO_OP; MAX_OPS]` initialises the whole array
/// before the first call site is reached).
#[inline(always)]
fn oset(a: &mut [Op; MAX_OPS], i: usize, x: Op) {
    unsafe { *a.get_unchecked_mut(i) = x }
}

/// `slots[i]`. SAFETY: `i < NSLOT`.
#[inline(always)]
fn sget(a: &[Zv; NSLOT], i: usize) -> Zv {
    unsafe { *a.get_unchecked(i) }
}

/// `slots[i] = x`. SAFETY: `i < NSLOT`; `x: Zv` is a pure value.
#[inline(always)]
fn sset(a: &mut [Zv; NSLOT], i: usize, x: Zv) {
    unsafe { *a.get_unchecked_mut(i) = x }
}

/// `ts[i]`. SAFETY: `i < MAX_STMT`, which `tmp_of` establishes by `% MAX_STMT`.
#[inline(always)]
fn tget(a: &[u16; MAX_STMT], i: usize) -> u16 {
    unsafe { *a.get_unchecked(i) }
}

/// `ts[i] = x`. SAFETY: `i < MAX_STMT`; `x: u16` is a pure value.
#[inline(always)]
fn tset(a: &mut [u16; MAX_STMT], i: usize, x: u16) {
    unsafe { *a.get_unchecked_mut(i) = x }
}

/// `anext[i]`. SAFETY: `i < NVAR`, established by `% NVAR`.
#[inline(always)]
fn nget(a: &[u16; NVAR], i: usize) -> u16 {
    unsafe { *a.get_unchecked(i) }
}

/// `anext[i] = x`. SAFETY: `i < NVAR`; `x: u16` is a pure value.
#[inline(always)]
fn nset(a: &mut [u16; NVAR], i: usize, x: u16) {
    unsafe { *a.get_unchecked_mut(i) = x }
}

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
/// as a precondition.**
#[inline(always)]
fn zunwrap(t: Option<usize>) -> usize {
    unsafe { t.unwrap_unchecked() }
}

#[inline(always)]
fn var_of(o: u16) -> usize {
    VAR_BASE + (o as usize) % NVAR
}

#[inline(always)]
fn tmp_of(o: u16) -> usize {
    (o as usize) % MAX_STMT
}

/// `_get_zval_ptr` -- zend_execute.c:88-125. ⭐⭐ THE `IS_UNUSED` ARM IS AN
/// EXPLICIT `return NULL;` (:118-121), and in Rust it is an explicit `None`.
/// It is correct: an operand that is not there has no zval. Every caller that
/// can be handed an IS_UNUSED operand is supposed to know it cannot be.
#[inline(always)]
fn get_zval_ptr(ts: &[u16; MAX_STMT], op_type: u8, op: u16) -> Option<usize> {
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
fn do_end_variable_parse(o: &mut Op, ty: u8) -> bool {
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
fn do_isset_or_isempty(o: &mut Op) {
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
) -> u16 {
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

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];
    let mut nstmt: usize = len / 8;
    if nstmt > MAX_STMT {
        nstmt = MAX_STMT;
    }

    let mut ops: [Op; MAX_OPS] = [ZERO_OP; MAX_OPS];
    let mut slots: [Zv; NSLOT] = [ZERO_ZV; NSLOT];
    let mut anext: [u16; NVAR] = [0u16; NVAR];
    let mut ts: [u16; MAX_STMT] = [0u16; MAX_STMT];
    let mut acc: u64 = 0;
    let mut bailout: u8 = 0;

    // The two process-global singletons, and the refcount PHP starts them at.
    sset(&mut slots, UNINIT as usize, Zv { ty: IS_NULL, refcount: 1, ..ZERO_ZV });
    sset(&mut slots, ERR as usize, Zv { ty: IS_NULL, refcount: 1, ..ZERO_ZV });
    let mut i: usize = 0;
    while i < NVAR {
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
    while i < NVAR * DIM {
        sset(&mut slots, ARR_BASE + i, Zv { ty: IS_NULL, refcount: 1, ..ZERO_ZV });
        i = i + 1;
    }

    // -- THE COMPILER'S ONE PASS. `while (le)` at :748-779 runs the mode switch
    // once per fetch-list element; `zend_do_isset_or_isempty` then rewrites the
    // LAST element only.
    let mut nops: usize = 0;
    let mut i: usize = 0;
    while i < nstmt {
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

        if nops + 1 + chain > MAX_OPS {
            break;
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

        let mut k: usize = first;
        while k < nops {
            let mut o: Op = oget(&ops, k);
            if !do_end_variable_parse(&mut o, mode) {
                bailout = 1; // zend_bailout() -- nothing runs
                nops = 0;
                break;
            }
            oset(&mut ops, k, o);
            acc = acc.wrapping_mul(31).wrapping_add(o.opcode as u64);
            k = k + 1;
        }
        if bailout != 0 {
            break;
        }
        if mode == BP_IS {
            let mut o: Op = oget(&ops, nops - 1);
            do_isset_or_isempty(&mut o); // :3223 -- the LAST opline only
            oset(&mut ops, nops - 1, o);
            acc = acc.wrapping_mul(31).wrapping_add(o.opcode as u64);
        }
        i = i + 1;
    }

    // -- execute()'s dispatch loop, zend_execute.c:1383-1396.
    if bailout == 0 {
        let mut pc: usize = 0;
        while pc < nops {
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
            pc = pc + 1;
        }
    }

    // What `php_execute_script` observes: the store the program left behind,
    // the refcounts, and the arrays' next-free indices. ⭐ Slot 0's refcount --
    // `EG(uninitialized_zval)` -- is in here on purpose: it is how the row
    // answers "does the append leave the global's refcount unbalanced?" with a
    // number instead of an argument.
    acc = acc.wrapping_mul(31).wrapping_add(bailout as u64);
    let mut i: usize = 0;
    while i < NSLOT {
        let z: Zv = sget(&slots, i);
        acc = acc.wrapping_mul(31).wrapping_add(z.ty as u64);
        acc = acc.wrapping_mul(31).wrapping_add(z.lval);
        acc = acc.wrapping_mul(31).wrapping_add(z.refcount as u64);
        i = i + 1;
    }
    let mut i: usize = 0;
    while i < NVAR {
        acc = acc.wrapping_mul(31).wrapping_add(nget(&anext, i) as u64);
        i = i + 1;
    }
    acc
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
