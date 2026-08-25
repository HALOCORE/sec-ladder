//! p46 rung R2 -- safe Rust, naive. The obvious port of `c/kernel_hardened.c`:
//! index the scratch arrays, let the language check the index.
//!
//! **What the language's checks ARE here, and why there are THREE of them IN
//! THE SOURCE.** The MAC step reads `bl[j]`, reads `out[i + j]` and writes
//! `out[i + j]`, so one schoolbook step is written with three bounds checks --
//! the densest check site in this tree.
//!
//! ⚠⚠ **AND ALL THREE ARE GONE FROM THE MACHINE CODE. THIS RUNG'S MEASURED
//! SAFETY TAX IS `0.00` PER MAC STEP** (../NOTES.md 0b, 8a). `i + j < OUTCAP`
//! follows from `i < n`, `j < m` and `n + m <= OUTCAP` by purely LINEAR
//! reasoning -- there is no `lemma_mul_inequality` in it, which is exactly what
//! makes p46 not p05 -- and LLVM *does* do it. The MAC loop of this rung
//! contains **no conditional branch but its own `jne`**, and its
//! conditional-branch multiset is identical to ../unsafe.rs's outside the loop.
//!
//! ⚠ **THREE FIGURES THAT USED TO BE IN THIS COMMENT WERE THE PRE-BUILD
//! PROBE'S AND ARE RETRACTED** (TASK_089_REVIEW M1). It said the checks cost
//! `7.00` instructions per MAC step, that they are *"NOT hoistable"* and that
//! *"LLVM still cannot remove them"*, and that *"this rung's kernel body is 186
//! instructions against the unsafe rung's 111"*. All four come from
//! `.temp/t89/cost.rs`, the probe whose slope ../NOTES.md 0b retracts, and no
//! pipeline on the shipped binaries yields 111: `harness/asm.py stat` gives
//! **179 / 150** (`n_fn`), 174 / 147 without padding, 184 / 155 raw objdump.
//! The shipped `R2 - R4` law is `3 + 5n - n*floor(m/2)` and is NEGATIVE for
//! all but the smallest shapes -- safe Rust is *cheaper* here, and ../NOTES.md
//! 8a shows instruction by instruction that none of that is safety either.
//!
//! This rung keeps the output-side bound as well, so that all six rungs compute
//! the same function on every input including the adversarial ones. That is a
//! deliberate choice, and on p46 it costs nothing: R2's per-access checks are
//! *provably redundant* on every call the benchmark makes and **LLVM works
//! that out on its own.** `.memory/01-ladder.md` finding 2 -- *a proof buys
//! nothing on its own, because rustc never learns what Z3 knew* -- is not
//! contradicted and does not bite here: nothing had to teach rustc anything,
//! so on p46 there is no check left for a proof to have removed.

#[path = "../../common/driver.rs"]
mod driver;

/// The product scratch capacity, in 64-bit limbs. Must equal
/// `SLB_P46_OUTCAP` in c/kernel.h and `OUTCAP` in model.py.
const OUTCAP: usize = 96;

/// The b-operand scratch, in 64-bit limbs. Sized for the DECLARED TYPE's full
/// range (`m` is a byte), so the pre-decode below can never leave it.
const BCAP: usize = 256;

/// What an over-long product folds to.
const REJ: u64 = 0x9e37_79b9_7f4a_7c15;

/// Little-endian limb decode. Checked, like every other read in this rung.
#[inline(always)]
fn ld64(w: &[u8], p: usize) -> u64 {
    w[p] as u64 + 256 * (w[p + 1] as u64) + 65536 * (w[p + 2] as u64)
        + 16777216 * (w[p + 3] as u64) + 4294967296 * (w[p + 4] as u64)
        + 1099511627776 * (w[p + 5] as u64) + 281474976710656 * (w[p + 6] as u64)
        + 72057594037927936 * (w[p + 7] as u64)
}

/// p46's kernel. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let w: &[u8] = &buf[off..off + len];
    let n: usize = w[0] as usize;
    let m: usize = w[1] as usize;
    if n == 0 || m == 0 {
        return 0;
    }
    if 8 + 8 * (n + m) > len {
        return 0;
    }
    // >>> THE SAFETY LINE. c/kernel.c omits this test. <<<
    if n + m > OUTCAP {
        return REJ;
    }
    let mut bl: [u64; BCAP] = [0u64; BCAP];
    let mut jd: usize = 0;
    while jd < m {
        bl[jd] = ld64(w, 8 + 8 * (n + jd));
        jd = jd + 1;
    }
    let mut out: [u64; OUTCAP] = [0u64; OUTCAP];
    let mut i: usize = 0;
    while i < n {
        let ai: u64 = ld64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m {
            let bj: u64 = bl[j];
            let t: u128 =
                (ai as u128) * (bj as u128) + (out[i + j] as u128) + (carry as u128);
            out[i + j] = t as u64;
            carry = (t >> 64) as u64;
            j = j + 1;
        }
        out[i + m] = carry;
        i = i + 1;
    }
    let mut acc: u64 = 0;
    let mut k: usize = 0;
    while k < n + m {
        acc = acc.wrapping_mul(31).wrapping_add(out[k]);
        k = k + 1;
    }
    acc.wrapping_mul(31).wrapping_add(n as u64).wrapping_mul(31).wrapping_add(m as u64)
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
    if stride_w > 0 && stride_w <= n_blob as u64 {
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
