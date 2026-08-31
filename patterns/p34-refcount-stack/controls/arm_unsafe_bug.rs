//! p34 CONTROL ARM: **`unsafe.rs` with the retain DELETED, and nothing else.**
//! Not a rung -- a control. Driven by `controls/rust_bug.py`.
//!
//! ⚠⚠ **THIS IS THE MUST-FIRE ARM FOR THE MIRI ROW.** ../spec.md's
//! `miri.reason` says that what Miri finds on the SHIPPED `unsafe.rs` is
//! NOTHING, on every input including all five adversarial ones. A claim about
//! silence needs a control that can break it (`.memory/03-measurement.md` entry
//! 14; RECAP trap 5), and this file is it: the same rung with `obj_retain(t);`
//! removed from the DUP arm, which is exactly the line `c/kernel.c` omits.
//!
//! **Miri MUST report Undefined Behaviour here**, on the inputs whose windows
//! execute a DUP. If it does not, `unsafe.rs`'s silence is unsupported and the
//! Miri row means nothing.
//!
//! ⚠ **It is generated from `unsafe.rs` by deleting one line, and
//! `controls/rust_bug.py` RE-DERIVES that at every run** -- it reads both files,
//! removes the retain from `unsafe.rs` and requires the result to equal this
//! file below the header. So the two cannot drift, and a future edit to the rung
//! that is not mirrored here FAILS the control instead of quietly making it a
//! test of something else.

#[path = "../../../common/driver.rs"]
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
                // THE LINE THE C RUNG FORGOT -- DELETED IN THIS ARM.
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
