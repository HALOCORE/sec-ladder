//! p28 rung R4 -- unsafe.
//!
//! R2's algorithm with the safe representation replaced by the one the proof can
//! carry: a raw pointer per object in a slot table, a separate liveness byte, and
//! the two link sets as `u8` slot numbers inside the object. Allocated and freed
//! by hand.
//!
//! ⚠⚠ **WHAT THIS RUNG IS NOT, STATED FIRST BECAUSE IT IS THE THING A REVIEWER
//! SHOULD ATTACK.** It is **not** a transliteration of `c/kernel.c`. The C rungs
//! put four RAW POINTERS inside every object, so R1's dangling pointer physically
//! sits in another heap object's `hn`. Here the links are SLOT NUMBERS and the
//! pointers live in a stack table, so the same omission would leave a dangling
//! *index*. **That divergence is deliberate, it is disclosed, and it is measured
//! rather than argued**: `controls/arm_rawptr.rs` is the faithful raw-pointer
//! port of both C arms, it agrees with these rungs on every shipped input, and
//! Miri reports its use-after-free. ../NOTES.md 5 says what the divergence costs
//! and what it buys, and ../spec.md's `why` pins it. The reason is `TASK_091`'s:
//! an address-keyed permission map needs the FULL doubly-linked-list
//! well-formedness -- `hn[hp[i]] == i`, `hp[hn[i]] == i`, and the same pair for
//! the eviction list -- before a walk can be licensed, and this row did not buy
//! that. **What it buys instead is stated as a result in ../NOTES.md 6.**
//!
//! **What does NOT go away is the safety line.** TRIM still has to splice the
//! victim out of the hash chain before `rec_close`, and this rung writes it out
//! exactly as C's hardened rung does. That is not a bounds check, it is the
//! kernel's semantics -- the hardened cell folds the checked answer and
//! ../spec.md pins it -- and a rung without it would be R1's bug written in Rust
//! rather than an unsafe rung. This rung is correct; it just has nothing checking
//! that it is. R5 (verus.rs) is this exec code with the SAFETY comments below
//! turned into obligations a verifier discharges.
//!
//! **The walk carries `live[cur] == 1u8` and a `steps < SLOTS` bound.** Neither
//! can fire -- a correct chain holds only live objects and at most `SLOTS` are
//! ever made, so no chain is longer than the fuel -- and they are here because
//! verus.rs needs them:
//! the first licenses the object read through `live[i] == 1 <==>
//! perms.dom().contains(i)`, and the second is the `decreases` measure. ⚠ **The C
//! rungs carry the step bound and CANNOT carry the liveness test** (they have no
//! slot and no `live[]`), which is the one place where this rung's shape is not
//! also C's; ../NOTES.md 5 counts it. Every rung's answer is the same on every
//! input regardless, because neither conjunct fires.
//!
//! **The table and the bucket array are indexed UNCHECKED**, through
//! `arr_get_unchecked` / `arr_set_unchecked`, for p27's and p29's reason: on p27
//! an earlier draft indexed checked on the argument that `h < ntab <= TABCAP`
//! already deletes rustc's bounds check, and that argument measured FALSE.
//! ⚠ **Inherited, not re-measured here** -- this pattern publishes no cost of any
//! kind (../NOTES.md 8).
//!
//! **The splices are WHOLE-STRUCT read-modify-write** -- `rec_read`, rebuild all
//! six fields, `rec_write` -- because `vstd::raw_ptr` has no field-level mutator
//! and R5 must be able to spell what R4 spells. `TASK_091` measured that cost at
//! **1.00 `Ir` per CALL out of 50 232**, with a driver swap test flipping the
//! sign, so it is free; it is why R5 needs no local `external_body` field-store
//! wrapper. ⚠ **Each splice site RE-READS its neighbour rather than reusing an
//! earlier read, and that is load-bearing rather than naive**: the victim's chain
//! predecessor and its eviction predecessor can be THE SAME OBJECT, so a stale
//! copy would drop one of the two writes.
//!
//! **`rec_alloc` and `rec_free` are `vstd::raw_ptr::allocate` / `deallocate`**
//! with the ghost returns and arguments deleted and `alloc::alloc::` respelled
//! `std::alloc::`; verus.rs carries the same two bodies as trusted items with
//! vstd's own API as their verified twins. Both sides are `#[inline(always)]`,
//! which is what keeps R4 and R5 the same instructions at `-O3`.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site in verus.rs.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): every `rec_read`/`rec_write` of slot `i` runs under
//!   `live[i] == 1u8`, and `live[i] == 1u8` holds exactly for the slots whose
//!   object has been allocated and not yet freed.
//! SAFETY (5): every slot number this kernel forms -- `bucket[b]`, `head`,
//!   `tail`, and every `lp`/`ln`/`hn`/`hp` it reads out of an object -- is `NIL`
//!   or is below `nmade <= SLOTS`, because the only slot number ever STORED into
//!   any of them is `nmade` at the moment it is allocated. That is what licenses
//!   `arr_get_unchecked(&live, cur as usize)`.
//! SAFETY (6): `rec_close` is called at most once per object -- DEL and TRIM
//!   each clear `live[cur]` before anything can reach the slot again, and the
//!   epilogue frees only slots still marked alive -- so there is no double free,
//!   and every slot alive at the end is freed, so there is no leak.
//! SAFETY (7): **THE SAFETY LINE.** After `rec_close(v)` no live object's `hn`
//!   or `hp` names `v` and no `bucket[b]` names `v`, because TRIM splices `v` out
//!   of its chain first. **`c/kernel.c` is exactly this rung minus that
//!   sentence.**

#[path = "../../common/driver.rs"]
mod driver;

const NB: usize = 8;
const SLOTS: usize = 48;
const OBJSZ: usize = 6;
const NIL: u8 = 255;
const SENT: u64 = 251;

/// One cache object: six bytes, one allocation. `#[repr(C)]` for a stable
/// layout; verus.rs declares that layout to Verus with `global layout Obj is
/// size == 6, align == 1;`.
#[repr(C)]
#[derive(Clone, Copy)]
pub struct Obj {
    pub key: u8,
    pub val: u8,
    pub lp: u8,
    pub ln: u8,
    pub hn: u8,
    pub hp: u8,
}

// The unchecked window read. Same accessor every unsafe rung in this project
// ships; in verus.rs it is trusted item 1 of 7.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// The unchecked ARRAY read and store, generic over the element type so that the
// pointer table, the liveness array and the bucket array share one accessor.
// verus.rs's trusted items 2 and 3.
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
// would leave the stale walk inside a live allocation and the bug would be
// p32's class instead of this one.
#[inline(always)]
fn rec_free(p: *mut u8, size: usize, align: usize) {
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    unsafe {
        std::alloc::dealloc(p, layout);
    }
}

// The four object operations. verus.rs's are the same four bodies with the
// permissions threaded through them.
#[inline(always)]
fn rec_open(v: Obj) -> *mut Obj {
    let base = rec_alloc(OBJSZ, 1);
    let q: *mut Obj = base as *mut Obj;
    // `*q = v` and not `core::ptr::write(q, v)`: the two are the same operation
    // for a `Copy` struct with no `Drop`, but `core::ptr::write` is `#[inline]`
    // rather than `#[inline(always)]`, so at `-O0` it survives as a CALL here
    // while vstd's `ptr_mut_write` -- which R5 uses and which IS
    // `#[inline(always)]` over a precompiled vstd -- inlines to a bare store.
    // p27's measured result, inherited through p29.
    unsafe {
        *q = v;
    }
    q
}

#[inline(always)]
fn rec_close(p: *mut Obj) {
    let base: *mut u8 = p as *mut u8;
    rec_free(base, OBJSZ, 1);
}

#[inline(always)]
fn rec_read(p: *mut Obj) -> Obj {
    unsafe { *p }
}

#[inline(always)]
fn rec_write(p: *mut Obj, v: Obj) {
    unsafe {
        *p = v;
    }
}

/// **THE LIVENESS HALF OF A LINK TEST, and the one exec conjunct in this rung
/// that the C rungs cannot spell.** C writes `x != NULL`; this rung writes
/// `alive_link(&live, x)`, which is `x != NIL && live[x] == 1u8`. The second
/// half CANNOT FIRE in a correct rung -- every link names a live object -- and
/// it is here because verus.rs needs it: it is what licenses
/// `perms.tracked_borrow_mut(x)` at the TEN splice sites. The alternative is to
/// prove the two link sets are well-formed doubly linked lists. ../NOTES.md 5.
#[inline(always)]
fn alive_link(live: &[u8; SLOTS], x: u8) -> bool {
    x != NIL && arr_get_unchecked(live, x as usize) == 1u8
}

// THE CHAIN WALK, shared by PUT, GET and DEL, and written once because all
// three spell it identically in every rung.
#[inline(always)]
fn walk(tab: &[*mut Obj; SLOTS], live: &[u8; SLOTS], start: u8, k: u8) -> (u8, bool) {
    let mut cur: u8 = start;
    let mut found: bool = false;
    let mut steps: usize = 0;
    while cur != NIL && arr_get_unchecked(live, cur as usize) == 1u8 && steps < SLOTS {
        let ob: Obj = rec_read(arr_get_unchecked(tab, cur as usize));
        steps = steps + 1;
        if ob.key == k {
            found = true;
            break;
        }
        cur = ob.hn;
    }
    (cur, found)
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
    let mut tab: [*mut Obj; SLOTS] = [core::ptr::null_mut(); SLOTS];
    let mut live: [u8; SLOTS] = [0u8; SLOTS];
    let mut bucket: [u8; NB] = [NIL; NB];
    let mut head: u8 = NIL;
    let mut tail: u8 = NIL;
    let mut nmade: usize = 0;
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
        let b: usize = (a % NB as u8) as usize;
        if c % 4 == 0 {
            // PUT. Walk the hash chain; a hit updates the object in place.
            let bh: u8 = arr_get_unchecked(&bucket, b);
            let (cur, found) = walk(&tab, &live, bh, a);
            if found {
                let cb = arr_get_unchecked(&tab, cur as usize);
                let co = rec_read(cb);
                rec_write(
                    cb,
                    Obj {
                        key: co.key,
                        val: a.wrapping_mul(7).wrapping_add(1),
                        lp: co.lp,
                        ln: co.ln,
                        hn: co.hn,
                        hp: co.hp,
                    },
                );
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else if nmade < SLOTS {
                let s: u8 = nmade as u8;
                let q = rec_open(
                    Obj {
                        key: a,
                        val: a.wrapping_mul(7).wrapping_add(1),
                        lp: NIL,
                        ln: head,
                        hn: bh,
                        hp: NIL,
                    },
                );
                arr_set_unchecked(&mut tab, nmade, q);
                arr_set_unchecked(&mut live, nmade, 1u8);
                nmade = nmade + 1;
                if alive_link(&live, head) {
                    let pb = arr_get_unchecked(&tab, head as usize);
                    let po = rec_read(pb);
                    rec_write(
                        pb,
                        Obj { key: po.key, val: po.val, lp: s, ln: po.ln, hn: po.hn, hp: po.hp },
                    );
                } else {
                    tail = s;
                }
                head = s;
                if alive_link(&live, bh) {
                    let hb = arr_get_unchecked(&tab, bh as usize);
                    let ho = rec_read(hb);
                    rec_write(
                        hb,
                        Obj { key: ho.key, val: ho.val, lp: ho.lp, ln: ho.ln, hn: ho.hn, hp: s },
                    );
                }
                arr_set_unchecked(&mut bucket, b, s);
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            // GET. The same walk, then read the object's payload.
            let bh: u8 = arr_get_unchecked(&bucket, b);
            let (cur, found) = walk(&tab, &live, bh, a);
            if found {
                let co = rec_read(arr_get_unchecked(&tab, cur as usize));
                acc = acc.wrapping_mul(31).wrapping_add(co.val as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            // DEL. The same walk, then a SPLICE out of BOTH lists, then the
            // free. DEL arrives ALONG the hash chain, so it holds a chain
            // cursor when it frees -- which is why DEL is not the path that
            // forgets.
            let bh: u8 = arr_get_unchecked(&bucket, b);
            let (cur, found) = walk(&tab, &live, bh, a);
            if found {
                let cb = arr_get_unchecked(&tab, cur as usize);
                let co = rec_read(cb);
                if alive_link(&live, co.hp) {
                    let pb = arr_get_unchecked(&tab, co.hp as usize);
                    let po = rec_read(pb);
                    rec_write(
                        pb,
                        Obj {
                            key: po.key,
                            val: po.val,
                            lp: po.lp,
                            ln: po.ln,
                            hn: co.hn,
                            hp: po.hp,
                        },
                    );
                } else {
                    arr_set_unchecked(&mut bucket, b, co.hn);
                }
                if alive_link(&live, co.hn) {
                    let nb = arr_get_unchecked(&tab, co.hn as usize);
                    let no = rec_read(nb);
                    rec_write(
                        nb,
                        Obj {
                            key: no.key,
                            val: no.val,
                            lp: no.lp,
                            ln: no.ln,
                            hn: no.hn,
                            hp: co.hp,
                        },
                    );
                }
                if alive_link(&live, co.lp) {
                    let pb = arr_get_unchecked(&tab, co.lp as usize);
                    let po = rec_read(pb);
                    rec_write(
                        pb,
                        Obj {
                            key: po.key,
                            val: po.val,
                            lp: po.lp,
                            ln: co.ln,
                            hn: po.hn,
                            hp: po.hp,
                        },
                    );
                } else {
                    head = co.ln;
                }
                if alive_link(&live, co.ln) {
                    let nb = arr_get_unchecked(&tab, co.ln as usize);
                    let no = rec_read(nb);
                    rec_write(
                        nb,
                        Obj {
                            key: no.key,
                            val: no.val,
                            lp: co.lp,
                            ln: no.ln,
                            hn: no.hn,
                            hp: no.hp,
                        },
                    );
                } else {
                    tail = co.lp;
                }
                rec_close(cb);
                arr_set_unchecked(&mut live, cur as usize, 0u8);
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // TRIM. Reclaim the OLDEST object. It arrives here through the
            // EVICTION list and therefore holds no hash-chain cursor.
            if alive_link(&live, tail) {
                let v: u8 = tail;
                let vp = arr_get_unchecked(&tab, v as usize);
                let vo = rec_read(vp);
                if alive_link(&live, vo.lp) {
                    let pb = arr_get_unchecked(&tab, vo.lp as usize);
                    let po = rec_read(pb);
                    rec_write(
                        pb,
                        Obj { key: po.key, val: po.val, lp: po.lp, ln: NIL, hn: po.hn, hp: po.hp },
                    );
                } else {
                    head = NIL;
                }
                tail = vo.lp;
                // THE SAFETY LINE. c/kernel.c omits exactly this and nothing
                // else. Without it, `bucket[vb]` or some live object's `hn`
                // still names `v` after `rec_close(vp)` below.
                let vb: usize = (vo.key % NB as u8) as usize;
                if alive_link(&live, vo.hp) {
                    let pb = arr_get_unchecked(&tab, vo.hp as usize);
                    let po = rec_read(pb);
                    rec_write(
                        pb,
                        Obj {
                            key: po.key,
                            val: po.val,
                            lp: po.lp,
                            ln: po.ln,
                            hn: vo.hn,
                            hp: po.hp,
                        },
                    );
                } else {
                    arr_set_unchecked(&mut bucket, vb, vo.hn);
                }
                if alive_link(&live, vo.hn) {
                    let nb = arr_get_unchecked(&tab, vo.hn as usize);
                    let no = rec_read(nb);
                    rec_write(
                        nb,
                        Obj {
                            key: no.key,
                            val: no.val,
                            lp: no.lp,
                            ln: no.ln,
                            hn: no.hn,
                            hp: vo.hp,
                        },
                    );
                }
                rec_close(vp);
                arr_set_unchecked(&mut live, v as usize, 0u8);
                acc = acc.wrapping_mul(31).wrapping_add(3);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    // The epilogue. R2 and R3 do not have it: dropping the table IS this loop,
    // written by the language. There is deliberately NO liveness store here --
    // it would be a dead store (p27's measured `r4_epiclear` result).
    let mut j: usize = 0;
    while j < nmade {
        if arr_get_unchecked(&live, j) == 1u8 {
            rec_close(arr_get_unchecked(&tab, j));
        }
        j = j + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nmade as u64)
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
