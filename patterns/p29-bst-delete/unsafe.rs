//! p29 rung R4 -- unsafe.
//!
//! R2's algorithm with the safe representation replaced by the one C uses: a raw
//! pointer per record, a separate liveness byte, and a CACHED RAW POINTER that a
//! FIND saves and a USE dereferences. Allocated and freed by hand.
//!
//! **What does NOT go away is the safety line**, `live[g_slot] == 1u8` followed
//! by `rr.key == g_key` on the USE path. That is not a bounds check, it is the
//! kernel's semantics -- the hardened cell folds SENT for a cached record that
//! has been freed *or* re-occupied, and ../spec.md pins that answer -- and a
//! rung without it would be R1's bug written in Rust rather than an unsafe rung.
//! This rung is correct; it just has nothing checking that it is. R5 (verus.rs)
//! is this exec code with the SAFETY comments below turned into obligations a
//! verifier discharges.
//!
//! ⚠ **The safety line is spelled as a NESTED `if` here and as one `&&` chain in
//! C, and that is not cosmetic.** In verus.rs the record read needs
//! `perms.tracked_borrow(g_slot)`, whose precondition is discharged only by
//! `live[g_slot] == 1`, so the identity test cannot be written before the
//! liveness test at all. This file ships verus.rs's exec code, so it inherits
//! the shape. ⚠ **NOT byte-identical**: the pair measures `norel` at `-O3` and
//! `differ` at `-O0` (../NOTES.md 5), which is this pattern's own result and not
//! p27's. ../NOTES.md 6c.
//!
//! **The walks carry `live[cur] == 1u8` and a `steps < TABCAP` bound, and the
//! two-child test asks liveness of both children -- six liveness conjuncts and
//! five step bounds across the kernel.** Not one of them can fire -- a correct
//! tree never links to a retired slot and no path is longer than TABCAP -- and
//! they are here because verus.rs needs them: the
//! first licenses the record read through `live[i] == 1 <==>
//! perms.dom().contains(i)`, and the second is the `decreases` measure. The
//! alternative is proving the link structure IS A TREE. ../NOTES.md 4 counts
//! them; every rung including the C rungs carries them, so no rung-to-rung
//! comparison is confounded by them.
//!
//! **The table is indexed UNCHECKED**, through `arr_get_unchecked` /
//! `arr_set_unchecked`, for p27's reason: on p27 an earlier draft indexed it
//! checked on the argument that `h < ntab <= TABCAP` already deletes rustc's
//! bounds check, and that argument measured FALSE. ⚠ **Inherited, not
//! re-measured here** -- this pattern publishes no cost of any kind
//! (../NOTES.md 8).
//!
//! **`rec_alloc` and `rec_free` are `vstd::raw_ptr::allocate` / `deallocate`**
//! with the ghost returns and arguments deleted and `alloc::alloc::` respelled
//! `std::alloc::`; verus.rs carries the same two bodies as trusted items with
//! vstd's own API as their verified twins. Both sides are `#[inline(always)]`,
//! which is what keeps R4 and R5 the same instructions at `-O3` -- calling
//! vstd's `allocate` directly makes the pair `differ` at both levels. ⚠ At
//! `-O0` this pair is `differ` ANYWAY, for a different reason (../NOTES.md 5).
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site in verus.rs.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): every `rec_read(tab[i])` runs under `live[i] == 1u8`, and
//!   `live[i] == 1u8` holds exactly for the slots whose record has been
//!   allocated and not yet freed.
//! SAFETY (5): `rec_read(g_saved)` runs under `live[g_slot] == 1u8`, and
//!   `tab[g_slot]` is written once per slot and never reset, so `g_saved` is
//!   that slot's record. **This is the obligation p29 is about, and ONE SOURCE
//!   LINE CARRIES TWO BUG CLASSES SELECTED BY THE INPUT**: the liveness test
//!   above keeps the read in bounds of a live allocation, which is the
//!   use-after-FREE half on a 0/1-child victim, and `rr.key == g_key` is what
//!   makes the ANSWER right when the two-child splice has re-occupied that
//!   allocation, which is the in-bounds use-after-RECYCLE half. ⚠ **The half
//!   every detector sees is the half that CANNOT BE GATED.**
//!   ⚠⚠ **TWO CONJUNCTS IS WHAT THIS RUNG SPELLS, NOT WHAT THE PROPERTY NEEDS,
//!   and the sentence that used to stand here -- *"it takes TWO conjuncts"* --
//!   IS RETRACTED.** `TASK_140` built two ONE-conjunct spellings out of the
//!   shipped c/kernel.c by substitution; both score `wrong_total 0` and
//!   `asan_lines 0` with the ASan positive control firing, and one of them adds
//!   NO STATE -- it widens `live[]` from a bit to the occupant tag. The
//!   two-conjunct spelling ships because it buys a free `wf` at R5
//!   (../NOTES.md 6c), and the row stands on the two bug classes, which the
//!   conjunct count was never evidence for.
//! SAFETY (6): `rec_close` is called at most once per record -- the splice
//!   clears `live[cur]` before anything can reach the slot again, and the
//!   epilogue frees only slots still marked alive -- so there is no double free,
//!   and every slot alive at the end is freed, so there is no leak.

#[path = "../../common/driver.rs"]
mod driver;

const TABCAP: usize = 32;
const RECSZ: usize = 4;
const NIL: u8 = 255;
const SENT: u64 = 251;

/// A record: four bytes, one allocation. `#[repr(C)]` for a stable layout;
/// verus.rs declares that layout to Verus with `global layout Rec is size == 4,
/// align == 1;`.
#[repr(C)]
#[derive(Clone, Copy)]
pub struct Rec {
    pub key: u8,
    pub val: u8,
    pub l: u8,
    pub r: u8,
}

// The unchecked window read. Same accessor every unsafe rung in this project
// ships; in verus.rs it is trusted item 1 of 7.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// The unchecked ARRAY read and store, generic over the element type so that the
// pointer table and the liveness array share one accessor. verus.rs's trusted
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

// `vstd::raw_ptr::allocate` with the two ghost returns deleted.
#[inline(always)]
fn rec_alloc(size: usize, align: usize) -> *mut u8 {
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    let p = unsafe { std::alloc::alloc(layout) };
    if p == core::ptr::null_mut() {
        std::process::abort();
    }
    p
}

// `vstd::raw_ptr::deallocate` with the two ghost arguments deleted. **A REAL
// `free`** -- ../spec.md pins that it is, because a freelist push into a slab
// would leave the stale read inside a live allocation and the bug would be
// p17's logical class instead of this one.
#[inline(always)]
fn rec_free(p: *mut u8, size: usize, align: usize) {
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    unsafe {
        std::alloc::dealloc(p, layout);
    }
}

// The four record operations. verus.rs's are the same four bodies with the
// permissions threaded through them.
#[inline(always)]
fn rec_open(v: Rec) -> *mut Rec {
    let base = rec_alloc(RECSZ, 1);
    let q: *mut Rec = base as *mut Rec;
    // `*q = v` and not `core::ptr::write(q, v)`: the two are the same operation
    // for a `Copy` struct with no `Drop`, but `core::ptr::write` is `#[inline]`
    // rather than `#[inline(always)]`, so at `-O0` it survives as a CALL here
    // while vstd's `ptr_mut_write` -- which R5 uses and which IS
    // `#[inline(always)]` over a precompiled vstd -- inlines to a bare store.
    // One instruction of difference at `-O0` and the `identity` pin drops from
    // `exact` to `differ`. p27's measured result, inherited.
    unsafe {
        *q = v;
    }
    q
}

#[inline(always)]
fn rec_close(p: *mut Rec) {
    let base: *mut u8 = p as *mut u8;
    rec_free(base, RECSZ, 1);
}

#[inline(always)]
fn rec_read(p: *mut Rec) -> Rec {
    unsafe { *p }
}

#[inline(always)]
fn rec_write(p: *mut Rec, v: Rec) {
    unsafe {
        *p = v;
    }
}

// THE WALK, shared by INSERT, FIND and REMOVE, and written once because all
// three spell it identically in every rung.
#[inline(always)]
fn walk(tab: &[*mut Rec; TABCAP], live: &[u8; TABCAP], root: u8, k: u8) -> (u8, u8, bool, bool) {
    let mut cur: u8 = root;
    let mut par: u8 = NIL;
    let mut gl: bool = false;
    let mut found: bool = false;
    let mut steps: usize = 0;
    while cur != NIL && arr_get_unchecked(live, cur as usize) == 1u8 && steps < TABCAP {
        let rec: Rec = rec_read(arr_get_unchecked(tab, cur as usize));
        steps = steps + 1;
        if k < rec.key {
            par = cur;
            gl = true;
            cur = rec.l;
        } else if k > rec.key {
            par = cur;
            gl = false;
            cur = rec.r;
        } else {
            found = true;
            break;
        }
    }
    (cur, par, gl, found)
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
    let mut tab: [*mut Rec; TABCAP] = [core::ptr::null_mut(); TABCAP];
    let mut live: [u8; TABCAP] = [0u8; TABCAP];
    let mut ntab: usize = 0;
    let mut root: u8 = NIL;
    let mut g_saved: *mut Rec = core::ptr::null_mut();
    let mut g_has: bool = false;
    let mut g_slot: u8 = 0;
    let mut g_key: u8 = 0;
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
            let (cur, par, gl, found) = walk(&tab, &live, root, a);
            if found {
                // A DUPLICATE key updates the record's val IN PLACE.
                let cb = arr_get_unchecked(&tab, cur as usize);
                let co = rec_read(cb);
                rec_write(
                    cb,
                    Rec {
                        key: co.key,
                        val: a.wrapping_mul(7).wrapping_add(1),
                        l: co.l,
                        r: co.r,
                    },
                );
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else if ntab < TABCAP {
                let q = rec_open(
                    Rec { key: a, val: a.wrapping_mul(7).wrapping_add(1), l: NIL, r: NIL },
                );
                arr_set_unchecked(&mut tab, ntab, q);
                arr_set_unchecked(&mut live, ntab, 1u8);
                let newslot: u8 = ntab as u8;
                ntab = ntab + 1;
                if par == NIL {
                    root = newslot;
                } else {
                    let pb = arr_get_unchecked(&tab, par as usize);
                    let po = rec_read(pb);
                    if gl {
                        rec_write(pb, Rec { key: po.key, val: po.val, l: newslot, r: po.r });
                    } else {
                        rec_write(pb, Rec { key: po.key, val: po.val, l: po.l, r: newslot });
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            let (cur, _par, _gl, found) = walk(&tab, &live, root, a);
            if found {
                // THE CACHED POINTER. `tab[cur]` is written once per slot and
                // never reset, so `g_saved` stays slot `g_slot`'s record for the
                // rest of the window -- alive or not.
                g_saved = arr_get_unchecked(&tab, cur as usize);
                g_has = true;
                g_slot = cur;
                g_key = a;
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            let (cur0, par0, gl0, found) = walk(&tab, &live, root, a);
            if found {
                let mut cur: u8 = cur0;
                let mut par: u8 = par0;
                let mut gl: bool = gl0;
                let mut guard: usize = 0;
                while guard < TABCAP {
                    let cb = arr_get_unchecked(&tab, cur as usize);
                    let crec: Rec = rec_read(cb);
                    guard = guard + 1;
                    if crec.l != NIL && arr_get_unchecked(&live, crec.l as usize) == 1u8
                        && crec.r != NIL && arr_get_unchecked(&live, crec.r as usize) == 1u8 {
                        // TWO CHILDREN: the successor's key and val are copied
                        // INTO the victim's record and the SUCCESSOR is what the
                        // next turn frees. **Nothing is deallocated here.**
                        let mut sp: u8 = cur;
                        let mut s: u8 = crec.r;
                        let mut sgl: bool = false;
                        let mut sst: usize = 0;
                        while sst < TABCAP {
                            let sb = arr_get_unchecked(&tab, s as usize);
                            let srec: Rec = rec_read(sb);
                            if srec.l == NIL
                                || arr_get_unchecked(&live, srec.l as usize) != 1u8 {
                                break;
                            }
                            sst = sst + 1;
                            sp = s;
                            s = srec.l;
                            sgl = true;
                        }
                        let sb = arr_get_unchecked(&tab, s as usize);
                        let srec: Rec = rec_read(sb);
                        let cb2 = arr_get_unchecked(&tab, cur as usize);
                        let co = rec_read(cb2);
                        rec_write(cb2, Rec { key: srec.key, val: srec.val, l: co.l, r: co.r });
                        cur = s;
                        par = sp;
                        gl = sgl;
                        continue;
                    }
                    // ZERO OR ONE CHILD: unlink, then FREE.
                    let ch: u8 = if crec.l != NIL { crec.l } else { crec.r };
                    if par == NIL {
                        root = ch;
                    } else {
                        let pb = arr_get_unchecked(&tab, par as usize);
                        let po = rec_read(pb);
                        if gl {
                            rec_write(pb, Rec { key: po.key, val: po.val, l: ch, r: po.r });
                        } else {
                            rec_write(pb, Rec { key: po.key, val: po.val, l: po.l, r: ch });
                        }
                    }
                    rec_close(arr_get_unchecked(&tab, cur as usize));
                    // THE LINE THE C RUNG DOES NOT FORGET, and in verus.rs the
                    // proof forces it.
                    arr_set_unchecked(&mut live, cur as usize, 0u8);
                    break;
                }
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // THE SAFETY LINE. c/kernel.c omits both conjuncts.
            let v: u64 = if g_has && arr_get_unchecked(&live, g_slot as usize) == 1u8 {
                let rr = rec_read(g_saved);
                if rr.key == g_key {
                    rr.val as u64
                } else {
                    SENT
                }
            } else {
                SENT
            };
            acc = acc.wrapping_mul(31).wrapping_add(v);
        }
        o = o + 1;
    }
    // The epilogue. R2 and R3 do not have it: dropping the table IS this loop,
    // written by the language. There is deliberately NO liveness store here --
    // it would be a dead store (p27's measured `r4_epiclear` result).
    let mut j: usize = 0;
    while j < ntab {
        if arr_get_unchecked(&live, j) == 1u8 {
            rec_close(arr_get_unchecked(&tab, j));
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
