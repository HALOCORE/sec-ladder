//! p27 rung R4 -- unsafe.
//!
//! R2's algorithm with the safe representation replaced by the one C uses: a
//! raw pointer per slot and a separate liveness byte, allocated and freed by
//! hand. **What does NOT go away is `live[h] == 1u8` on the READ path** -- that
//! is not a bounds check, it is the kernel's semantics (the hardened cell folds
//! SENT for a closed handle and ../spec.md pins that answer), and a rung without
//! it would be R1's bug written in Rust rather than an unsafe rung. This rung is
//! correct; it just has nothing checking that it is. R5 (verus.rs) is this exec
//! code with the SAFETY comments below turned into obligations a verifier
//! discharges.
//!
//! **The table is indexed UNCHECKED here**, through `arr_get_unchecked` /
//! `arr_set_unchecked`. An earlier draft indexed it checked, on the argument
//! that `h < ntab` and `ntab <= TABCAP` already delete rustc's check; that
//! argument is **false**, three `panic_bounds_check` call sites survive at
//! `-O3`, and the checked spelling costs **41.70 Ir/call** on `small`.
//! ../NOTES.md 4 has the control and the disassembly.
//!
//! **`rec_alloc` and `rec_free` are character-for-character
//! `vstd::raw_ptr::allocate` / `deallocate`** (`raw_ptr.rs:908`, `:948`) with
//! the ghost returns deleted, and verus.rs carries the same two bodies as
//! trusted items with vstd's own API as their verified twins. Both sides are
//! `#[inline(always)]`, which is what makes R4 and R5 the same machine code:
//! vstd carries no `#[inline]`, so an R5 that called vstd's `allocate` directly
//! emits a GOT-indirect cross-crate `call` that R4 cannot produce and the pair
//! measures `differ`. ../NOTES.md 5 has both measurements and ../spec.md pins
//! the level.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the window header, so
//!   `off + 3 < off + len <= buf.len()`.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`, so
//!   `off + p + 1 < off + len <= buf.len()`.
//! SAFETY (4): **`rec_read(tab[h])` runs only under `live[h] == 1`, and
//!   `live[h] == 1` holds exactly for the slots whose record has been allocated
//!   and not yet freed.** That is the obligation p27 is about, and it is the one
//!   conjunct c/kernel.c deletes.
//! SAFETY (5): `rec_close` is called at most once per record -- CLOSE clears
//!   `live[h]` before anything else can reach the slot, and the epilogue frees
//!   only slots still marked alive -- so there is no double free; and every slot
//!   alive at the end is freed, so there is no leak.

#[path = "../../common/driver.rs"]
mod driver;

const TABCAP: usize = 32;
const RECSZ: usize = 1;
const SENT: u64 = 251;

// The unchecked window read. Same accessor every unsafe rung in this project
// ships; in verus.rs it is trusted item 1 of 7.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// The unchecked TABLE read and store, generic over the element type so that the
// pointer table and the liveness array share one accessor. verus.rs's trusted
// items 2 and 3. Worth 41.70 Ir/call on `small` against the checked spelling --
// `h < ntab <= TABCAP` does NOT delete rustc's check, and ../NOTES.md 4 has the
// control that measures it.
#[inline(always)]
fn arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> T {
    unsafe { *v.get_unchecked(i) }
}

#[inline(always)]
fn arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T) {
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

// `vstd::raw_ptr::allocate` (raw_ptr.rs:908) with the two ghost returns
// deleted. verus.rs carries the same body as trusted item 4, with vstd's own
// `allocate` as its verified twin; the pair is `#[inline(always)]` on both
// sides so that R4 and R5 emit the same instructions. Calling vstd's `allocate`
// from R5 instead makes the pair `differ` -- vstd carries no `#[inline]`, so
// that call is GOT-indirect and cross-crate and R4 cannot produce it.
// ../NOTES.md 5.
#[inline(always)]
fn rec_alloc(size: usize, align: usize) -> *mut u8 {
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    let p = unsafe { std::alloc::alloc(layout) };
    if p == core::ptr::null_mut() {
        std::process::abort();
    }
    p
}

// `vstd::raw_ptr::deallocate` (raw_ptr.rs:948) with the two ghost arguments
// deleted. **A REAL `free`** -- ../spec.md pins that it is, because a freelist
// push into a slab would leave the stale read inside a live allocation and the
// bug would be p17's logical class instead of this one.
#[inline(always)]
fn rec_free(p: *mut u8, size: usize, align: usize) {
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    unsafe {
        std::alloc::dealloc(p, layout);
    }
}

// The three record operations. verus.rs's are the same three bodies with the
// permissions threaded through them.
#[inline(always)]
fn rec_open(v: u8) -> *mut u8 {
    let base = rec_alloc(RECSZ, 1);
    // `*base = v` and not `core::ptr::write(base, v)`: the two are the same
    // operation for a `u8`, but `core::ptr::write` is `#[inline]` rather than
    // `#[inline(always)]`, so at `-O0` it survives as a CALL here while vstd's
    // `ptr_mut_write` -- which R5 uses and which IS `#[inline(always)]` over a
    // precompiled, already-optimised vstd -- inlines to a bare store. One
    // instruction of difference at `-O0` and the `identity` pin drops from
    // `exact` to `differ`. Measured; ../NOTES.md 5.
    unsafe {
        *base = v;
    }
    base
}

#[inline(always)]
fn rec_close(p: *mut u8) {
    rec_free(p, RECSZ, 1);
}

#[inline(always)]
fn rec_read(p: *mut u8) -> u8 {
    let r: &u8 = unsafe { &*p };
    *r
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    if nops == 0 {
        return 0;
    }
    let mut tab: [*mut u8; TABCAP] = [core::ptr::null_mut(); TABCAP];
    let mut live: [u8; TABCAP] = [0u8; TABCAP];
    let mut ntab: usize = 0;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    while o < nops {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf_get_unchecked(buf, off + p);
        let a: u8 = buf_get_unchecked(buf, off + p + 1);
        p = p + 2;
        let h: usize = a as usize;
        if c % 4 == 0 {
            if ntab < TABCAP {
                let q = rec_open(a);
                arr_set_unchecked(&mut tab, ntab, q);
                arr_set_unchecked(&mut live, ntab, 1u8);
                ntab = ntab + 1;
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if h < ntab && arr_get_unchecked(&live, h) == 1u8 {
                rec_close(arr_get_unchecked(&tab, h));
                // THE LINE THE C RUNG FORGOT.
                arr_set_unchecked(&mut live, h, 0u8);
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // THE SAFETY LINE, and c/kernel.c omits exactly the second conjunct.
            if h < ntab && arr_get_unchecked(&live, h) == 1u8 {
                let v: u8 = rec_read(arr_get_unchecked(&tab, h));
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    // The epilogue. R2 and R3 do not have it: dropping the table IS this loop,
    // written by the language.
    let mut j: usize = 0;
    while j < ntab {
        if arr_get_unchecked(&live, j) == 1u8 {
            rec_close(arr_get_unchecked(&tab, j));
            arr_set_unchecked(&mut live, j, 0u8);
        }
        j = j + 1;
    }
    acc.wrapping_mul(31).wrapping_add(ntab as u64)
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
    if stride_w >= 4 && stride_w <= n_blob as u64 {
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
