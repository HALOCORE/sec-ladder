//! ph07 rung R3 -- safe-tuned.
//!
//! ⚠⚠ **READ THE THIRD PARAGRAPH BEFORE READING THIS RUNG'S NUMBER.** R3 is
//! usually where a row recovers most of R2's gap; here it recovers what it can
//! reach, and **what it cannot reach is the row**.
//!
//! **What is tuned.** The copy and the fold stop indexing: `zip` over two
//! iterators has no per-element bounds check, where `out[i] = s[start + i]`
//! has two. That is `cnt` elements' worth of checks removed from the part of
//! the kernel that is a bulk copy.
//!
//! ⚠⚠ **WHAT IS NOT, AND I LOOKED.** The two walks keep `s[n]`, checked, once
//! per character. A variable-stride cursor is not an iterator: `n` advances by
//! `MBTAB[s[n]]`, a value read out of the byte the cursor is standing on, so
//! there is no `Iterator` in the language whose `next()` is this step, and no
//! reslice makes the check discharge -- `n <= from` is a fact about a sum of
//! table entries, not about a slice length. **The check R2 pays on the walk is
//! a check safe Rust keeps**, and the R3-vs-R4 difference on this row is
//! therefore concentrated where R2's is not. NOTES.md §8.
//!
//! ⚠ `MBTAB[s[n] as usize]` carries no check of its own in any rung: the index
//! is a `u8` widened to `usize` and the table is `[u8; 256]`, so LLVM discharges
//! it statically. Confirmed in the disassembly -- NOTES.md §8.
//!
//! Everything else is `safe_naive.rs`'s text, deliberately: ../spec.md's
//! `idiom.required` pins the walk shape, and a tuned rung that rewrote the walk
//! would be measuring a different program rather than a different spelling.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py. See ../spec.md for why each is what it is.

/// `mblen_table_utf8` -- ext/mbstring/libmbfl/filters/mbfilter_utf8.c:39-56,
/// the same 256 numbers `c/kernel.c` carries.
///
/// ⚠ **STATIC DATA, NOT INPUT.** In PHP this is a field of a
/// `const mbfl_encoding` and an attacker cannot choose it. Putting it in the
/// blob would invent a defect PHP does not have: a zero entry makes the start
/// walk spin forever. `model.py::selfcheck` check 4 asserts every entry is
/// >= 1 and check 5 asserts these numbers still equal `c/kernel.c`'s.
static MBTAB: [u8; 256] = [
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 1, 1,
];

/// One `mblen_table_utf8` lookup. Identical text in all four Rust rungs;
/// `verus.rs` adds an `ensures` tying it to the closed form its spec functions
/// use, which is what keeps the 256-element `array_view` out of the kernel's
/// SMT context (NOTES.md §10).
#[inline(always)]
fn mbtab(b: u8) -> u8 {
    MBTAB[b as usize]
}

/// `php_shim_tally()` after the one `reset` + `emalloc(cap)` + `efree` a kernel
/// call makes. ⚠ The Rust rungs do not link `common-php/emalloc_shim.h`; this
/// reproduces the value ARITHMETICALLY so that the allocation SIZE is pinned
/// across every rung by the checksum the gate compares. It is not evidence that
/// any Rust rung ran PHP's allocator. ../spec.md and NOTES.md §7.
///
/// ⚠ `wrapping_add(7)`, not `+ 7`. `PHP_SHIM_REAL_SIZE` is
/// `((size) + 7) & ~(size_t)0x7` on an unsigned `size_t`, so the C wraps here
/// and a checked `+` would be a rung that panics where the C does not. It is
/// also what makes this function TOTAL, which is what verus.rs needs -- vstd
/// exposes no `slice.len() <= isize::MAX` fact, so `cap + 7` is not provably
/// in range however small `cap` really is. NOTES.md §10.
#[inline(always)]
fn tally(cap: usize) -> u64 {
    let real_size: u64 = (cap as u64).wrapping_add(7) & !7u64;
    1000003u64 ^ 1000033u64 ^ real_size.wrapping_mul(1000039)
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    // The window: two little-endian 32-bit head words, then the zval buffer
    // (the string, then its NUL terminator).
    let fw: u32 = (buf[off] as u32) | ((buf[off + 1] as u32) << 8)
        | ((buf[off + 2] as u32) << 16) | ((buf[off + 3] as u32) << 24);
    let lw: u32 = (buf[off + 4] as u32) | ((buf[off + 5] as u32) << 8)
        | ((buf[off + 6] as u32) << 16) | ((buf[off + 7] as u32) << 24);
    let s: &[u8] = &buf[off + 8..off + len];
    let slen: usize = s.len() - 1;

    // ⚠ mbstring.c:1787-1805 -- the CALLER's two clamps, BOTH FROM BELOW, and
    // this is the row's guard site (`.memory-php/01` F1). `fw`/`lw` are the
    // raw bits of the `long`s `mb_strcut` read out of its zvals; a set top bit
    // is a negative offset, which counts from the end of the string and floors
    // at zero. **Nothing clamps `from` from ABOVE**, which is CRASH-124.
    //
    // ⚠ Spelled in `usize` with `saturating_sub` where the C spells it in
    // `int`. Same function on every (slen, from, length) an `int` can hold --
    // demonstrated exhaustively against a build of the C itself, with a
    // must-fire control, in controls/guard_equiv.py -- and total, which is
    // what lets verus.rs state it without an `isize::MAX` axiom vstd does not
    // have. Declared in ../spec.md's `provenance.divergences`.
    let frm: usize = if fw < 0x8000_0000 {
        fw as usize
    } else {
        slen.saturating_sub((0u32.wrapping_sub(fw)) as usize)
    };
    let length: usize = if lw < 0x8000_0000 {
        lw as usize
    } else {
        slen.saturating_sub(frm)
            .saturating_sub((0u32.wrapping_sub(lw)) as usize)
    };
    // ⚠⚠ R1h -- THE GUARD CONFIGURATION UPSTREAM CONVERGED ON, and it lives
    // HERE, in the caller, not in `mbfl_strcut`. Pinned as
    // `php-5.2.12 .. php-5.2.17`, `PHP_FUNCTION(mb_strcut)` body sha256
    // 26e2099e33433c74. TWO commits produce it:
    //   cb3cca21b345  Ilia Alshanetsky, 2005-12-15, "Fixed possible memory
    //                 corruption inside mb_strcut()", first in php-5.1.2. TWO
    //                 guards:
    //     hunk (a)  if (from > Z_STRLEN_PP(arg1)) { RETURN_FALSE; }
    //     hunk (b)  if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1))
    //                   { len = Z_STRLEN_PP(arg1) - from; }
    //   c2471b495009  Moriyoshi Koizumi, 2009-09-23, "Fixed bug #49354
    //                 (mb_strcut() cuts wrong length when offset is within a
    //                 multibyte character)" -- REMOVES hunk (b), and ships
    //                 ext/mbstring/tests/bug49354.phpt with it.
    // (a) is the memory-safety half and (b) is not: with `from <= slen` the
    // start walk reads only at `n <= from <= slen`, and `s` is `slen + 1`
    // bytes, so every index in this rung is in bounds BECAUSE OF (a). Hunk (b)
    // removes no out-of-bounds read at all and changes the answer on 13.5 % of
    // benign calls (controls/fix_scope.py Q1/Q2, controls/bug49354.py).
    // ⚠⚠⚠ **THIS RUNG CARRIED HUNK (b) UNTIL `TASK_PHP_018`.** It is gone from
    // all four Rust rungs, from `verus.rs`'s SPEC as well as its exec code,
    // from `model.py`'s three implementations and from `c/kernel_hardened.c` --
    // because R2-R5 are ports of R1h and R1h no longer has it.
    // c/kernel_hardened.c has this same guard in the same place; c/kernel.c has
    // neither. controls/guard_equiv.py compares BOTH configurations.
    if frm > slen {
        // RETVAL_FALSE (mbstring.c:1812). Nothing was allocated, so the tally
        // the C xors in is the post-reset zero and this is the same u64 the
        // `mbfl_malloc` NULL arm produces.
        return 0xFFFF_FFFFu64;
    }
    // ⚠ **HUNK (b) WAS HERE.** It read
    //     `let length = if frm.saturating_add(length) > slen { slen - frm }
    //      else { length };`
    // -- `saturating_add` where the C writes `(unsigned) from + (unsigned)
    // len`. `c2471b495009` removed it upstream as bug #49354 and
    // `TASK_PHP_018` removed it here. `controls/guard_equiv.py` still compares
    // that spelling against a build of the C, so the equivalence claim it
    // carried is not lost with it -- and it now also reports how far the two
    // configurations are apart (1 134 of 5 122 triples).

    // mbfilter.c:1202-1210 -- the start walk, ROTATED.
    // ⚠ The C is `for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from)
    // break; start = n; }` -- it reads once before its first test. Rotating
    // that into "read once, then `while n <= from`" performs exactly the same
    // reads in the same order and assigns exactly the same `start`; it is the
    // shape rustc and LLVM produce from either spelling, and it is the one
    // Verus can carry an invariant across. All four Rust rungs use it; both C
    // rungs keep the `for (;;)` verbatim.
    let mut n: usize = mbtab(s[0]) as usize;
    let mut start: usize = 0;
    while n <= frm {
        start = n;
        let m: usize = mbtab(s[n]) as usize;
        n = n + m;
    }
    // mbfilter.c:1212-1223 -- the end walk, which IS bounded.
    // ⚠ `saturating_add`: `mbfilter.c:1212` is `k = start + length` on two
    // `int`s and CAN overflow -- that is bug #71906, fixed upstream in 2016 and
    // out of this row's scope (inputs/gen.py asserts the corpus never reaches
    // it). A checked `+` here would panic where the C does not; saturation
    // agrees with `+` on the whole domain, because it only ever caps at
    // `usize::MAX` and `k >= slen` is already true there.
    let k: usize = start.saturating_add(length);
    let mut end: usize;
    if k >= slen {
        end = slen;
    } else {
        end = start;
        while n <= k {
            end = n;
            let m: usize = mbtab(s[n]) as usize;
            n = n + m;
        }
    }
    // mbfilter.c:1227-1241 -- the clamps. The two `< 0` arms cannot fire on a
    // `usize`; they cannot fire in the C either, because `start` and `end` are
    // sums of table entries. model.py would report it if one could.
    if start > slen {
        start = slen;
    }
    if end > slen {
        end = slen;
    }
    if start > end {
        start = end;
    }
    // mbfilter.c:1243-1256 -- `mbfl_malloc((n + 8))`, copy `n` bytes, then four
    // '\0'. ⚠ `vec![0u8; cap]` ZEROES where `emalloc` does not, so the four
    // trailing NULs the C writes are already there and `cap` bytes of zeroing
    // are added that the C does not do. All four Rust rungs pay it identically,
    // so it cancels in every safe-vs-unsafe delta and does NOT cancel in the
    // C-vs-Rust one; ph03 makes the same choice for the same reason and
    // NOTES.md §8 prices it rather than burying it.
    let cnt: usize = end - start;
    let cap: usize = cnt + 8;
    let mut out: Vec<u8> = vec![0u8; cap];
    for (d, v) in out[..cnt].iter_mut().zip(s[start..end].iter()) {
        *d = *v;
    }
    let mut acc: u64 = out[..cnt]
        .iter()
        .fold(0u64, |a, v| a.wrapping_mul(31).wrapping_add(*v as u64));
    acc = acc.wrapping_mul(31).wrapping_add(cnt as u64);
    acc ^ tally(cap)
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
    if stride_w >= 9 && stride_w <= n_blob as u64 {
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
