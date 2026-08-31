//! p34 rung R4 -- unsafe.
//!
//! R2's algorithm with the safe representation replaced by the one C uses: a raw
//! pointer per stack entry and **the reference count written into the object's
//! own first word, by hand**. `Rc` is gone, and with it the thing that made R2
//! and R3 unable to express this bug at all.
//!
//! **What does NOT go away is `obj_retain` on the DUP path.** That is not a
//! bounds check and it is not decoration: it is the kernel's ownership
//! discipline, it is the ONE line `c/kernel.c` omits, and a rung without it
//! would be R1's bug written in Rust rather than an unsafe rung. This rung is
//! correct; it just has nothing checking that it is. R5 (verus.rs) is this exec
//! code with the SAFETY comments below turned into obligations a verifier
//! discharges.
//!
//! **The stack is indexed UNCHECKED**, through `arr_get_unchecked` /
//! `arr_set_unchecked`, for p27's measured reason -- `ntop <= CAP` does not
//! delete rustc's bounds check on `stk[i]`, and ../NOTES.md 5 prices the checked
//! spelling on this pattern rather than inheriting p27's figure.
//!
//! **`rec_alloc` and `rec_free` are `vstd::raw_ptr::allocate` / `deallocate`**
//! (`raw_ptr.rs:908`, `:948`) with the ghost returns and arguments deleted and
//! `alloc::alloc::` respelled `std::alloc::`, and verus.rs carries the same two
//! bodies as trusted items with vstd's own API as their verified twins. Both
//! sides are `#[inline(always)]`, which is what makes R4 and R5 the same machine
//! code: vstd carries no `#[inline]`, so an R5 that called vstd's `allocate`
//! directly emits a GOT-indirect cross-crate `call` that R4 cannot produce
//! (p27's TASK_055 measurement, inherited).
//!
//! ⚠ **p34's `rec_alloc` keeps FOUR of vstd's five `ensures` where p27's keeps
//! three.** The one p27 drops and p34 keeps is the ALIGNMENT conjunct: p27
//! allocates a `u8` at `align == 1`, so `pt.0.addr() % align == 0` is trivial
//! there, while p34's object is `align == 8` and `PointsToRaw::into_typed`
//! requires the address to be aligned for the target type. The one BOTH drop is
//! `pt.0.addr() + size <= usize::MAX + 1`, and on p34 the GATE found it not
//! load-bearing rather than the author judging it so. ../NOTES.md 6d.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the window header, so
//!   `off + 3 < off + len <= buf.len()`.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`, so
//!   `off + p + 1 < off + len <= buf.len()`.
//! SAFETY (4): every `stk[i]` this kernel forms has `i < ntop <= CAP`: DUP reads
//!   `ntop - 1` under `ntop > 0` and writes `ntop` under `ntop < CAP`, POP reads
//!   `ntop` after decrementing it under `ntop > 0`, and READ's index is
//!   `a % ntop` under `ntop > 0`.
//! SAFETY (5): **THE TEMPORAL ONE, and it is what p34 is about.** For every live
//!   object `o`, `o.rc` equals the number of stack entries naming `o`.
//!   `obj_new` establishes it (one entry, `rc = 1`); `obj_retain` preserves it
//!   on the DUP path (one entry, one increment); `obj_dec` preserves it on the
//!   release paths (one entry removed, one decrement) and `obj_free` runs
//!   exactly when the count reaches zero, i.e. exactly when no stack entry names
//!   the object. **So no object is freed while a reference to it is live, none
//!   is freed twice, and the epilogue drives every count to zero, so none
//!   leaks.** `c/kernel.c` is precisely a caller that cannot discharge this,
//!   because it publishes a reference without counting it.

#[path = "../../common/driver.rs"]
mod driver;

const CAP: usize = 16;
const DLEN: usize = 8;
const SENT: u64 = 251;

/// One heap object: the reference count in its own first word, a length, and the
/// payload. `#[repr(C)]` so the field order is the one c/kernel.c's disclosed
/// layout note describes -- `rc` at 0, `len` at 8, `data` at 16, clear of
/// glibc's tcache words. verus.rs pins the same layout to Verus with a
/// `global layout` directive, which rustc checks at codegen.
#[repr(C)]
#[derive(Clone, Copy)]
pub struct Obj {
    pub rc: usize,
    pub len: usize,
    pub data: [u8; DLEN],
}

// The unchecked window read. Same accessor every unsafe rung in this project
// ships; in verus.rs it is trusted item 1 of 7.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// The unchecked ARRAY read and store, generic over the element type so that the
// pointer stack and the object payload share one accessor. verus.rs's trusted
// items 2 and 3.
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

// `vstd::raw_ptr::allocate` (raw_ptr.rs:908) with the two ghost returns deleted.
// verus.rs carries the same body as trusted item 4, with vstd's own `allocate`
// as its verified twin.
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
// deleted. **A REAL `free`** -- ../spec.md pins that it is, because a free-list
// push into a slab would leave the stale read inside a live allocation and the
// bug would be p32's row instead of this one.
#[inline(always)]
fn rec_free(p: *mut u8, size: usize, align: usize) {
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    unsafe {
        std::alloc::dealloc(p, layout);
    }
}

// The four object operations. verus.rs's are the same four bodies with the
// permissions threaded through them. They are free functions rather than inline
// expressions because unsafe.rs has to be byte-identical to that file.
#[inline(always)]
fn obj_new(val: u8) -> *mut Obj {
    let size = core::mem::size_of::<Obj>();
    let align = core::mem::align_of::<Obj>();
    let base = rec_alloc(size, align);
    let q: *mut Obj = base as *mut Obj;
    // `[0u8; DLEN]` then one store is C's `memset` + `data[0] =`, and it is one
    // whole-object write rather than three field writes so that R5 can spell it
    // with a single `ptr_mut_write`.
    let mut d: [u8; DLEN] = [0u8; DLEN];
    arr_set_unchecked(&mut d, 0, val);
    // `*q = v` and not `core::ptr::write(q, v)`: the two are the same operation
    // for a `Copy` type, but `core::ptr::write` is `#[inline]` rather than
    // `#[inline(always)]`, so at `-O0` it survives as a CALL here while vstd's
    // `ptr_mut_write` -- which R5 uses and which IS `#[inline(always)]` over a
    // precompiled, already-optimised vstd -- inlines to a bare store. One
    // instruction of difference at `-O0` and the `identity` pin drops from
    // `exact` to `differ`. p27's measurement, inherited; ../NOTES.md 6.
    unsafe {
        *q = Obj { rc: 1, len: DLEN, data: d };
    }
    q
}

// THE SAFETY LINE, and the only increment in this rung. c/kernel.c omits exactly
// the call to this function.
#[inline(always)]
fn obj_retain(p: *mut Obj) {
    let r: &mut Obj = unsafe { &mut *p };
    r.rc = r.rc + 1;
}

// The release half: one decrement, and the caller frees when this returns 0.
// **Correct in both C rungs and in every Rust rung** -- p34's bug is entirely on
// the acquire side.
#[inline(always)]
fn obj_dec(p: *mut Obj) -> usize {
    let r: &mut Obj = unsafe { &mut *p };
    let n = r.rc - 1;
    r.rc = n;
    n
}

#[inline(always)]
fn obj_read(p: *mut Obj) -> u8 {
    let r: &Obj = unsafe { &*p };
    arr_get_unchecked(&r.data, 0)
}

// THE REAL `free`.
#[inline(always)]
fn obj_free(p: *mut Obj) {
    let size = core::mem::size_of::<Obj>();
    let align = core::mem::align_of::<Obj>();
    rec_free(p as *mut u8, size, align);
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
    let mut stk: [*mut Obj; CAP] = [core::ptr::null_mut(); CAP];
    let mut ntop: usize = 0;
    let mut nnew: usize = 0;
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
        if c % 4 == 0 {
            if ntop < CAP {
                let q = obj_new(a.wrapping_mul(7).wrapping_add(1));
                arr_set_unchecked(&mut stk, ntop, q);
                ntop = ntop + 1;
                nnew = nnew + 1;
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if ntop > 0 && ntop < CAP {
                let t = arr_get_unchecked(&stk, ntop - 1);
                // THE LINE THE C RUNG FORGOT.
                obj_retain(t);
                arr_set_unchecked(&mut stk, ntop, t);
                ntop = ntop + 1;
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            if ntop > 0 {
                ntop = ntop - 1;
                let q = arr_get_unchecked(&stk, ntop);
                let n = obj_dec(q);
                if n == 0 {
                    obj_free(q);
                }
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            if ntop > 0 {
                let v: u8 = obj_read(arr_get_unchecked(&stk, (a as usize) % ntop));
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    // The epilogue: release every reference still on the stack. R2 and R3 do not
    // have it -- dropping the stack IS this loop, written by the language.
    // ../NOTES.md 5 prices the difference.
    while ntop > 0 {
        ntop = ntop - 1;
        let q = arr_get_unchecked(&stk, ntop);
        let n = obj_dec(q);
        if n == 0 {
            obj_free(q);
        }
    }
    acc.wrapping_mul(31).wrapping_add(nnew as u64)
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
