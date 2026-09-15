//! ph97 rung R3 -- safe-tuned.
//!
//! R2 with its three per-byte walks rewritten as iterator pipelines -- the
//! compare, the frame copy and the name fold -- so that each carries no index
//! and nothing for LLVM to check. Same function, same early exits, same answer,
//! still zero `unsafe`. The accessors are R2's, unchanged: see
//! `.temp`-independent note in `../NOTES.md` §8 for why inventing a difference
//! there would have been a difference in the LADDER and not in the PROGRAM.
//!
//! ⚠⚠ **READ THIS BEFORE COMPARING THIS RUNG TO R1h.** The four Rust rungs
//! implement **exactly** what `c/kernel_hardened.c` implements -- PHP 5.0.0's
//! `mb_get_info` plus the one line of `f7326d627962` (Antony Dovgal,
//! 2005-01-28, *"MFB: fix #31732"*) -- because that fix is COMPLETE for this
//! defect: it removes the only dereference of the unwritten out-parameter and
//! changes no benign answer. The ladder reads:
//!
//!     R1    mbstring.c:3209-3252 as shipped 5.0.0 -- CRASH-126
//!     R1h   + f7326d627962: ONE LINE, `if (!typ || !strcasecmp("all", typ))`
//!     R2-5  the same function, in Rust
//!
//! ⭐⭐⭐ **AND `!typ ||` IS NOT SCENERY IN THESE RUNGS -- IT IS WHAT MAKES THEM
//! COMPILE THE WAY THEY DO.** `typ` is an `Option<&[u8; NTYP]>`, so the four
//! later compare sites are reachable only when the first arm's
//! `typ.is_none() ||` was false. In R2 and R3 that is why `.unwrap()` cannot
//! panic; in R4 it is why `unwrap_unchecked` is sound; in R5 it is the
//! `requires` Verus discharges. **The 2005 patch and the R5 proof obligation
//! are the same sentence** -- delete the `typ.is_none() ||` from `verus.rs` and
//! the file stops verifying (`controls/negatives.py --emit r1`).
//!
//! ⭐⭐ **WHAT THIS ROW IS ABOUT, IN ONE LINE OF RUST.** C says *absent* with a
//! NULL `char *` and has no way to make the reader check; Rust says it with
//! `Option<&[u8; NTYP]>`, which the const assertion below measures at **the same
//! 8 bytes** and which cannot be read without being opened. The safety is a
//! TYPE, not a test, and the type costs nothing to carry.
//!
//! ⚠ **WHAT THE RUST RUNGS THEREFORE CANNOT SHOW, AND IT IS A FINDING RATHER
//! THAN A GAP** (`CLAUDE.md` rule 6): no rung here reproduces the defect,
//! because in C the bug is an OMISSION -- a test that is not written -- and in
//! Rust reproducing it would take a COMMISSION, an `unwrap` or an
//! `unwrap_unchecked` on an unguarded `typ`. `controls/rust_bug.py` builds both
//! of those on purpose and records what they do. `../NOTES.md` §7.
//!
//! **Do not read this rung's number as an unwrap tax without the decomposition
//! in `../NOTES.md` §8.** A ph97 call does four different things -- decode 24
//! bytes per record, run the spec scanner and the count test, materialise a
//! NUL-terminated frame, and walk up to five 21-byte compares -- and only the
//! last two carry checks R4 removes.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py. See ../spec.md for why each is what it is.

/// One call record: `ZEND_NUM_ARGS()`, `Z_TYPE_PP`, `Z_STRLEN_PP`, `Z_LVAL_PP`
/// and 20 bytes of `Z_STRVAL_PP`.
const REC: usize = 24;
/// The largest `Z_STRLEN` a record can carry.
const STRMAX: usize = 20;
/// One more than `STRMAX`: the NUL `convert_to_string_ex` materialises.
const NTYP: usize = 21;

// Z_TYPE_PP(arg) -- the four the "|s" arm of `zend_parse_arg` distinguishes,
// zend_API.c:301-331.
const IS_NULL: u8 = 0;
const IS_BOOL: u8 = 1;
const IS_STRING: u8 = 2;

const TAG_FALSE: u64 = 0x0F;
const TAG_ALL: u64 = 0x0A;
const TAG_SEL1: u64 = 0x10;
const TAG_SEL2: u64 = 0x11;
const TAG_SEL3: u64 = 0x12;
const TAG_SEL4: u64 = 0x13;

/// `mb_get_info`'s own type spec -- mbstring.c:3215. ⛔ THE `|` IS FIRST AND
/// THAT IS THE WHOLE DEFECT: `zend_API.c:486` sets `min_num_args` from a
/// `max_num_args` that is still ZERO, so a call with no arguments passes the
/// count test at `:511` and the write loop at `:537` runs zero times.
const SPEC: [u8; 2] = [b'|', b's'];

/// ⭐⭐⭐ **P1, AS A COMPILE-TIME ASSERTION RATHER THAN A CLAIM.** `Option<&T>`
/// is the null-pointer-optimised layout: the discriminant lives in the
/// reference's own null niche, so an optional thin reference occupies exactly
/// the bytes of `char *`. If this ever stopped holding, every Rust rung in this
/// row would fail to BUILD rather than quietly measure something else.
const _: () = assert!(
    core::mem::size_of::<Option<&[u8; NTYP]>>() == core::mem::size_of::<&[u8; NTYP]>()
);
const _: () = assert!(core::mem::size_of::<Option<&[u8; NTYP]>>() == 8);

/// `MBSTRG(...)`, as PHP 5.0.0 initialises them (mbstring.c:726 and the globals
/// ctor) and as the measured 5.0.0 CLI reports them.
const ENC_INVALID: usize = 0;
const ENC_PASS: usize = 1;
const ENC_8859_1: usize = 2;
const NENC: usize = 3;

const G_INTERNAL: usize = ENC_8859_1;
const G_HTTP_IN: usize = ENC_INVALID;
const G_HTTP_OUT: usize = ENC_PASS;
const G_OVERLOAD: usize = ENC_PASS;

/// `mbfl_no2encoding` composed with `mbfl_no_encoding2name` --
/// mbfl_encoding.c:253-265. Index 0 IS the `return "";` at `:261`, which is
/// what an unknown encoding number gets.
///
/// ⚠ **`mbfl_no_encoding2name` NEVER RETURNS NULL**, and that is what makes
/// `mb_get_info`'s four `!= NULL` tests dead -- in upstream as well as here.
/// `../NOTES.md` §4.
const NAMES: [[u8; NTYP]; NENC] = [
    *b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0",
    *b"pass\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0",
    *b"ISO-8859-1\0\0\0\0\0\0\0\0\0\0\0",
];

/// The five selectors, in `mb_get_info`'s own chain order -- which is
/// load-bearing, because the arms are tried one at a time and the first match
/// wins. mbstring.c:3219, :3233, :3237, :3241, :3245. The same five strings are
/// also the four KEYS `add_assoc_string` writes at `:3222`, `:3225`, `:3228`
/// and `:3231`, so the table is used twice and spelled once.
const NSEL: usize = 5;
const SELS: [[u8; NTYP]; NSEL] = [
    *b"all\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0",
    *b"internal_encoding\0\0\0\0",
    *b"http_input\0\0\0\0\0\0\0\0\0\0\0",
    *b"http_output\0\0\0\0\0\0\0\0\0\0",
    *b"func_overload\0\0\0\0\0\0\0\0",
];

/// R2/R3 spelling: a bounds-checked index into the selector table. (R3 ==
/// R2 here; the lever is in the three walks.)
#[inline(always)]
fn sel_get(k: usize) -> &'static [u8; NTYP] {
    &SELS[k]
}

/// R2/R3 spelling: a bounds-checked index into the encoding-name table.
#[inline(always)]
fn name_get(k: usize) -> &'static [u8; NTYP] {
    &NAMES[k]
}

/// R2/R3 spelling: the CHECKED open of the optional.
///
/// ⭐⭐ It cannot panic, and the reason is `f7326d627962`: every call site is
/// guarded by the `typ.is_none() ||` the 2005 patch adds. R4 and R5 write
/// `unwrap_unchecked` here, and R5 PROVES exactly that guard.
#[inline(always)]
fn opt_get(t: Option<&[u8; NTYP]>) -> &[u8; NTYP] {
    t.unwrap()
}

/// R2/R3 spelling: a bounds-checked sub-slice.
#[inline(always)]
fn wsub(v: &[u8], o: usize, n: usize) -> &[u8] {
    &v[o..o + n]
}

/// R2/R3 spelling: a bounds-checked slice index.
#[inline(always)]
fn sget(v: &[u8], i: usize) -> u8 {
    v[i]
}

#[inline(always)]
fn lower(c: u8) -> u8 {
    if c >= b'A' && c <= b'Z' {
        c + 32
    } else {
        c
    }
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.

/// `strcasecmp(3)`, C locale -- IN THE KERNEL, not in libc.
///
/// ⛔ That is a MEASUREMENT decision as much as a fidelity one: family A1 is
/// symbol-scoped and structurally excludes callee work, so a row whose work sat
/// inside libc would read ~0 in the statistic this programme publishes.
/// `controls/libc_compare.py` prices the alternative. `../NOTES.md` §6.
///
/// R3 spelling: one zip over two iterators.
#[inline(always)]
fn strcasecmp(a: &[u8; NTYP], b: &[u8; NTYP]) -> i32 {
    for (x, y) in a.iter().zip(b.iter()) {
        let ca: u8 = lower(*x);
        let cb: u8 = lower(*y);
        if ca != cb {
            return ca as i32 - cb as i32;
        }
        if ca == 0 {
            return 0;
        }
    }
    0
}

/// Fold one NUL-terminated name into the checksum. The terminator is folded
/// too, so `"a"` and `"a\0b"` differ.
///
/// R3 spelling: one walk over an iterator.
#[inline(always)]
fn fold_str(acc: u64, s: &[u8; NTYP]) -> u64 {
    let mut a: u64 = acc;
    for c in s.iter() {
        if *c == 0 {
            return a.wrapping_mul(31).wrapping_add(1);
        }
        a = a.wrapping_mul(31).wrapping_add(*c as u64);
    }
    a.wrapping_mul(31).wrapping_add(1)
}

/// One argument, as `zend_parse_arg` sees it.
struct Zval<'a> {
    ty: u8,
    lval: u8,
    len: usize,
    val: &'a [u8],
}

/// `zend_parse_arg`, the `'s'` arm -- zend_API.c:297-333.
///
/// ⭐ The `IS_NULL` fall-through is upstream's and it is load-bearing: `*p =
/// NULL; *pl = 0;` at `:304-305` happens only `if (return_null)`, which the `!`
/// modifier sets and `"|s"` does not carry, so IS_NULL becomes the EMPTY STRING.
/// Upstream's own comment on the missing break is *break omitted intentionally*.
/// Measured on the 5.0.0 CLI: `mb_get_info(null)` answers `bool(false)` and
/// `mb_get_info()` faults. `../NOTES.md` §1.
///
/// R3 spelling: one zip over two iterators, truncated by `take`.
#[inline(always)]
fn parse_arg(arg: &Zval, frame: &mut [u8; NTYP], n_out: &mut usize) -> bool {
    let mut n: usize = 0;
    if arg.ty == IS_STRING {
        // convert_to_string_ex, zend_API.c:314
        for (d, s) in frame.iter_mut().zip(arg.val.iter()).take(arg.len) {
            *d = *s;
            n = n + 1;
        }
    } else if arg.ty == IS_BOOL {
        if arg.lval % 2 == 1 {
            frame[0] = b'1';
            n = 1;
        }
    } else if arg.ty != IS_NULL {
        return false; // zend_API.c:330 -- "string", then E_WARNING, then FAILURE
    }
    frame[n] = 0;
    *n_out = n;
    true
}

/// `zend_parse_va_args` -- zend_API.c:463-549. `false` is FAILURE.
///
/// ⛔⛔ THE SPEC SCANNER AND THE COUNT TEST ARE UPSTREAM'S, CHARACTER FOR
/// CHARACTER, BECAUSE THEY ARE THE MECHANISM: `'|'` FIRST sets `min_num_args`
/// from a `max_num_args` that is still 0, `:511` then admits `num_args == 0`,
/// and `:537`'s loop runs zero times -- so this function returns SUCCESS having
/// written NOTHING, and `*wrote` stays `false`.
#[inline(always)]
fn parse_va_args(num_args: usize, type_spec: &[u8], arg: &Zval,
                 frame: &mut [u8; NTYP], wrote: &mut bool, typ_len: &mut i32) -> bool {
    let mut min_num_args: i32 = -1; // :467
    let mut max_num_args: i32 = 0;  // :468

    let mut s: usize = 0;
    while s < type_spec.len() {
        // :474
        let c: u8 = sget(type_spec, s);
        if c == b'l' || c == b'd' || c == b's' || c == b'b' || c == b'r'
            || c == b'a' || c == b'o' || c == b'O' || c == b'z' || c == b'Z'
        {
            max_num_args = max_num_args + 1; // :482
        } else if c == b'|' {
            min_num_args = max_num_args; // :486
        } else if c == b'/' || c == b'!' {
            // Pass -- :489-492
        } else {
            return false; // :503
        }
        s = s + 1;
    }

    if min_num_args < 0 {
        // :507
        min_num_args = max_num_args;
    }

    if (num_args as i32) < min_num_args || (num_args as i32) > max_num_args {
        return false; // :511 -> :524
    }

    let mut n: usize = 0;
    let mut na: usize = num_args;
    let mut sp: usize = 0;
    while na > 0 {
        // :537
        na = na - 1;
        if sp < type_spec.len() && sget(type_spec, sp) == b'|' {
            // :539
            sp = sp + 1;
        }
        if !parse_arg(arg, frame, &mut n) {
            return false; // :543
        }
        *wrote = true;
        *typ_len = n as i32; // :316
        sp = sp + 1;
    }

    true // :548
}

/// `PHP_FUNCTION(mb_get_info)` -- mbstring.c:3209-3252, plus `f7326d627962`.
#[inline(always)]
fn get_info(b: &[u8], acc: u64, falses: &mut u64) -> u64 {
    // ⭐⭐ TWO INDEPENDENT BYTES. `num_args` is *was an argument supplied?*;
    // `ty` is *is it well-typed?*. A kernel that derived one from the other
    // would have deleted the mechanism.
    let num_args: usize = (sget(b, 0) % 3) as usize;
    let arg = Zval {
        ty: sget(b, 1) % 4,
        len: (sget(b, 2) % ((STRMAX + 1) as u8)) as usize,
        lval: sget(b, 3),
        val: wsub(b, 4, STRMAX),
    };

    let mut frame: [u8; NTYP] = [0u8; NTYP];
    // :3211 `char *typ = NULL;` -- in Rust the absence is in the TYPE, and
    // `wrote` is the one bit `typ = NULL` encodes: *did the write loop run?*
    let mut wrote: bool = false;
    // :3212 `int typ_len;`. Upstream leaves it UNINITIALISED and never reads
    // it; Rust has no uninitialised `i32` without `MaybeUninit`, so it is 0
    // here and is never read either. ../NOTES.md §3 records the observation
    // with its own "not load-bearing" qualifier; it is `ph96`'s mechanism, one
    // row over.
    let mut typ_len: i32 = 0;
    let spec_str: &[u8] = &SPEC;

    if !parse_va_args(num_args, spec_str, &arg, &mut frame, &mut wrote, &mut typ_len) {
        // :3215 -> :3216
        *falses = falses.wrapping_add(1);
        return acc.wrapping_mul(31).wrapping_add(TAG_FALSE);
    }
    let typ: Option<&[u8; NTYP]> = if wrote { Some(&frame) } else { None };

    let mut a: u64 = acc;

    // ⭐⭐ :3219 WITH f7326d627962. `typ.is_none() ||` is the 2005 patch; the
    // four `else if` arms below are reachable only when it was FALSE, which is
    // what makes every `opt_get` here provably infallible.
    if typ.is_none() || strcasecmp(sel_get(0), opt_get(typ)) == 0 {
        a = a.wrapping_mul(31).wrapping_add(TAG_ALL); // :3220 array_init
        // :3221-3231. The four `!= NULL` tests are upstream's and are DEAD --
        // `mbfl_no_encoding2name` returns "" and never NULL (../NOTES.md §4).
        a = fold_str(a.wrapping_mul(31).wrapping_add(1), sel_get(1));
        a = fold_str(a, name_get(G_INTERNAL));
        a = fold_str(a.wrapping_mul(31).wrapping_add(2), sel_get(2));
        a = fold_str(a, name_get(G_HTTP_IN));
        a = fold_str(a.wrapping_mul(31).wrapping_add(3), sel_get(3));
        a = fold_str(a, name_get(G_HTTP_OUT));
        a = fold_str(a.wrapping_mul(31).wrapping_add(4), sel_get(4));
        a = fold_str(a, name_get(G_OVERLOAD));
    } else if strcasecmp(sel_get(1), opt_get(typ)) == 0 {
        // :3233
        a = fold_str(a.wrapping_mul(31).wrapping_add(TAG_SEL1), name_get(G_INTERNAL));
    } else if strcasecmp(sel_get(2), opt_get(typ)) == 0 {
        // :3237
        a = fold_str(a.wrapping_mul(31).wrapping_add(TAG_SEL2), name_get(G_HTTP_IN));
    } else if strcasecmp(sel_get(3), opt_get(typ)) == 0 {
        // :3241
        a = fold_str(a.wrapping_mul(31).wrapping_add(TAG_SEL3), name_get(G_HTTP_OUT));
    } else if strcasecmp(sel_get(4), opt_get(typ)) == 0 {
        // :3245
        a = fold_str(a.wrapping_mul(31).wrapping_add(TAG_SEL4), name_get(G_OVERLOAD));
    } else {
        // :3249-3250
        *falses = falses.wrapping_add(1);
        return acc.wrapping_mul(31).wrapping_add(TAG_FALSE);
    }
    a
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];
    let nrec: usize = len / REC;
    let mut acc: u64 = 0;
    let mut falses: u64 = 0;

    let mut r: usize = 0;
    while r < nrec {
        acc = get_info(wsub(win, r * REC, REC), acc, &mut falses);
        r = r + 1;
    }

    acc.wrapping_mul(31).wrapping_add(falses)
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
    if stride_w >= 24 && stride_w <= n_blob as u64 {
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
