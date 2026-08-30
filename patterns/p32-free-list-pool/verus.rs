//! p32 rung R5 -- unsafe Rust + a Verus proof.
//!
//! This is unsafe.rs's exec code with the SAFETY comments turned into
//! obligations a verifier discharges. **What is new here is what the obligation
//! is NOT.**
//!
//! `p27` proves *at the moment of the read, the record still exists* and one
//! linear `PointsTo` carries the whole of it. `p29` proves that plus *the record
//! is still the one FIND returned*, and its FIRST conjunct is discharged by
//! `perms.dom().contains(g_slot)` -- a precondition of `tracked_borrow` -- so
//! the proof FORCES the line the C rung forgot: delete `live[cur] = 0` after the
//! free and the invariant cannot be re-established.
//!
//! ⚠⚠⚠ **NOTHING OF THAT KIND HAPPENS HERE, AND IT IS THE ROW'S R5 RESULT.**
//! p32's storage is `[u8; POOLSZ]`, a local array alive from the first
//! instruction of the kernel to the last. There is no `allocate`, no
//! `deallocate`, no `PointsTo`, no `Dealloc` token and no `global layout`
//! directive. **The safety line `gen[h] != g` is discharged here as an ORDINARY
//! FUNCTIONAL POSTCONDITION** -- the exec loop must compute what `run` says, and
//! `run`'s handle-consuming arm folds SENT when the generation does not match --
//! and it costs exactly the same kind of proof obligation an arithmetic typo
//! would. **Linearity has nothing to say about this bug, because the bug does
//! not touch an allocation.** ../NOTES.md 6b.
//!
//! ⚠⚠ **AND THE INVARIANT THAT MAKES THE HARDENED KERNEL CORRECT AS AN
//! ALLOCATOR IS NOT PROVED HERE AND IS NOT NEEDED.** *"For every register `r`
//! whose handle `(h, g)` satisfies `gen[h] == g`, slot `h` is not on the free
//! list"* -- which is what rules out the double push, the self-looping list and
//! the two aliased handles -- is stated in c/kernel.h and appears NOWHERE in
//! this file. It is not needed for memory safety (every index is in range
//! without it, and `wf_ranges` below is the whole of what the unchecked accesses
//! require) and it is not needed for the functional `ensures` (the abstract
//! machine models a self-looping list perfectly happily). **So this R5 verifies,
//! and it verifies the rung with the safety line in it, and it would verify a
//! specification that did not have one.** That is the honest statement of what
//! the proof buys, it is `p42`'s finding in a different currency, and
//! ../controls/proof_mutants.py's `spec_weaken` arm demonstrates it rather than
//! asserting it.
//!
//! **TCB: five items** -- `buf_get_unchecked`, `arr_get_unchecked`,
//! `arr_set_unchecked`, `load_input`, `emit`. `p27` and `p29` ship SEVEN; the
//! two p32 does not need are `vstd::raw_ptr::allocate` and `deallocate`, because
//! **p32 allocates nothing**. Every one of the five is an item this project's
//! other unsafe rungs already ship, and three of them carry verified twins.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked in unsafe.rs; discharged at the call site here.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): `r = a % NREG` is `< NREG` for every `a`.
//! SAFETY (5): `freehead` is `NIL` or `< SLOTS`, and every element of `nx` is
//!   `NIL` or `< SLOTS`. That is the first half of `wf_ranges`.
//! SAFETY (6): every element of `regs` is `NIL` or `< SLOTS`, because ALLOC is
//!   the only writer and it stores `freehead` under `freehead != NIL`. That is
//!   the second half of `wf_ranges`, and together they license every unchecked
//!   index in the kernel.
//! SAFETY (7): **there is no temporal obligation, and that is the pattern.**
//!   See the note above.

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::prelude::*;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`. `group_array_axioms` gives `v@.len() == N` and
// the fill axiom for `[0u8; N]`. `lemma_u128_shr_is_div` and
// `lemma_mul_inequality` are the DRIVER's. **No `raw_ptr` and no `layout` group
// here: p32 has no pointers and no allocation.**
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// Blocks in the pool, a compile-time constant in every rung.
pub const SLOTS: usize = 8;

/// Bytes per block, a compile-time constant in every rung.
pub const BLK: usize = 4;

/// The pool's extent. Named rather than written `SLOTS * BLK` at the array type
/// so that unsafe.rs and this file declare the same thing the same way.
pub const POOLSZ: usize = 32;

/// Handle registers, a compile-time constant in every rung.
pub const NREG: usize = 8;

/// The free-list terminator, and the empty handle register. Outside
/// `0 .. SLOTS`, so no `NIL` can be mistaken for a slot.
pub const NIL: u8 = 255;

/// What a rejected operation folds. A compile-time constant in every rung.
pub const SENT: u64 = 251;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it. Spelled with `+` and `*` rather than `|` and `<<` on
/// purpose (`.memory/04-verus.md`): the two are the same function on bytes and
/// compile to the same instruction, but only the first is linear arithmetic.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int) + 16777216 * (
    buf[p + 3] as int)
}

/// How many operations the window at `off` declares. **Declared, and it bounds
/// nothing** -- the cursor guard is what stops the walk.
pub open spec fn nops_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// A block's payload is a function of the operand that allocated it, in every
/// rung. So a READ through a handle whose block has been recycled returns a
/// value no honest read of that handle's own incarnation could produce, which is
/// what puts the use-after-recycle bug class in the checksum at all.
pub open spec fn val_of(a: u8) -> u8 {
    a.wrapping_mul(7).wrapping_add(1)
}

/// What a WRITE stores, in every rung.
pub open spec fn written(a: u8) -> u8 {
    a.wrapping_mul(13).wrapping_add(3)
}

/// THE ABSTRACT MACHINE'S STATE, and it is the exec arrays and nothing else.
/// ⚠ Note what is NOT here and what `p29`'s `St` does have: a liveness sequence.
/// **Nothing in p32 is ever allocated or freed, so there is no liveness to
/// carry.** `gen` is an ordinary counter of how many times each slot has been
/// released, `nx` is the intrusive free list, and `rs`/`rg` are the handles the
/// kernel has issued. A self-looping `nx` is a perfectly well-formed value of
/// this type, which is exactly why the proof below does not rule one out.
pub ghost struct St {
    pub pool: Seq<u8>,
    pub nx: Seq<u8>,
    pub gen: Seq<u32>,
    pub rs: Seq<u8>,
    pub rg: Seq<u32>,
    pub head: u8,
    pub nalloc: int,
}

/// THE RANGE INVARIANT, and it is the WHOLE of what the unchecked accesses
/// need. Every handle is `NIL` or a real slot, every free-list link is `NIL` or
/// a real slot, and the head is `NIL` or a real slot. ⚠ **It says nothing about
/// the free list being acyclic, about a slot appearing on it once, or about two
/// registers not naming one block** -- see the module note. It holds in
/// `c/kernel.c` too, which is why R1 executes no undefined behaviour.
pub open spec fn wf_ranges(st: St) -> bool {
    &&& st.pool.len() == POOLSZ as int
    &&& st.nx.len() == SLOTS as int
    &&& st.gen.len() == SLOTS as int
    &&& st.rs.len() == NREG as int
    &&& st.rg.len() == NREG as int
    &&& (st.head == NIL || (st.head as int) < SLOTS as int)
    &&& forall|k: int|
        0 <= k < SLOTS as int ==> ((#[trigger] st.nx[k]) == NIL || (st.nx[k] as int) < SLOTS as int)
    &&& forall|k: int|
        0 <= k < NREG as int ==> ((#[trigger] st.rs[k]) == NIL || (st.rs[k] as int) < SLOTS as int)
}

/// ONE OPERATION: the new state and what it folds.
///
/// **The `else` branch is the whole pattern.** FREE, READ and WRITE share the
/// handle decode and share ONE guard: `h == NIL` asks whether the register holds
/// a handle at all, and `st.gen[h] != g` asks whether the block that handle
/// names is still the same incarnation. `c/kernel.c` asks only the first, and
/// what it gets for that is a self-looping free list on one input and somebody
/// else's payload on another.
pub open spec fn step(st: St, c: u8, a: u8) -> (St, u64) {
    if c % 4 == 0 {
        if st.head == NIL {
            (st, SENT)
        } else {
            let s = st.head as int;
            let gs = st.gen[s];
            (
                St {
                    pool: st.pool.update(s * (BLK as int), a).update(
                        s * (BLK as int) + 1,
                        val_of(a),
                    ),
                    rs: st.rs.update((a % (NREG as u8)) as int, st.head),
                    rg: st.rg.update((a % (NREG as u8)) as int, gs),
                    head: st.nx[s],
                    nalloc: st.nalloc + 1,
                    ..st
                },
                (st.head as u64).wrapping_add((gs as u64).wrapping_mul(8)),
            )
        }
    } else {
        let h = st.rs[(a % (NREG as u8)) as int];
        let g = st.rg[(a % (NREG as u8)) as int];
        if h == NIL {
            (st, SENT)
        } else if st.gen[h as int] != g {
            (st, SENT)
        } else if c % 4 == 1 {
            (
                St {
                    gen: st.gen.update(h as int, st.gen[h as int].wrapping_add(1)),
                    nx: st.nx.update(h as int, st.head),
                    head: h,
                    ..st
                },
                1u64,
            )
        } else if c % 4 == 2 {
            (st, st.pool[(h as int) * (BLK as int) + 1] as u64)
        } else {
            (St { pool: st.pool.update((h as int) * (BLK as int) + 1, written(a)), ..st }, 3u64)
        }
    }
}

/// The empty machine: a zeroed pool, the free list threaded 0 -> 1 -> ... -> NIL,
/// every generation zero and every handle register empty.
pub open spec fn st0() -> St {
    St {
        pool: Seq::new(POOLSZ as nat, |i: int| 0u8),
        nx: Seq::new(
            SLOTS as nat,
            |i: int| if i + 1 < SLOTS as int { (i + 1) as u8 } else { NIL },
        ),
        gen: Seq::new(SLOTS as nat, |i: int| 0u32),
        rs: Seq::new(NREG as nat, |i: int| NIL),
        rg: Seq::new(NREG as nat, |i: int| 0u32),
        head: 0,
        nalloc: 0,
    }
}

/// THE ABSTRACT MACHINE. It describes the PROGRAM -- stop when the window runs
/// out, fold SENT for an ALLOC from an exhausted pool, fold SENT for an empty
/// handle register, fold SENT for a handle whose generation no longer matches --
/// and it says nothing about `nops` being honest or about the op stream being
/// well formed. Every adversarial input is inside this domain (../spec.md).
pub open spec fn run(
    buf: Seq<u8>,
    off: int,
    len: int,
    o: int,
    nops: int,
    p: int,
    st: St,
    acc: u64,
) -> u64
    decreases nops - o,
{
    if o >= nops || len - p < 2 {
        acc.wrapping_mul(31).wrapping_add(st.nalloc as u64)
    } else {
        let s = step(st, buf[off + p], buf[off + p + 1]);
        run(buf, off, len, o + 1, nops, p + 2, s.0, acc.wrapping_mul(31).wrapping_add(s.1))
    }
}

/// What the kernel must return.
pub open spec fn pool_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nops_at(buf, off) == 0 {
        0
    } else {
        run(buf, off, len, 0, nops_at(buf, off), 4, st0(), 0)
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the window. It is
// sound because the standard library's documented contract for `get_unchecked`
// is exactly this: if the caller guarantees `i < v.len()`, the call is defined
// and returns `v[i]`. Every unsafe rung in this project ships it.
#[inline(always)]
#[verifier::external_body]
fn buf_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 1.
#[cfg(slb_twin)]
fn slb_twin_buf_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 4 of 5: the input loader. Plain Rust I/O, no `unsafe`, no
// `ensures` -- it is outside the memory-safety argument entirely.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 5 of 5: the output. Same shape, same reason.
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// TRUSTED ITEMS 2 and 3 of 5: the unchecked ARRAY read and store, generic over
// the element type so that the pool, the free-list links, the generations and
// both register arrays share one accessor. Same documented `get_unchecked`
// contract as item 1.
#[inline(always)]
#[verifier::external_body]
fn arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> (r: T)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> (r: T)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

#[inline(always)]
#[verifier::external_body]
fn arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

#[cfg(slb_twin)]
fn slb_twin_arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == pool_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
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
    let mut pool: [u8; POOLSZ] = [0u8; POOLSZ];
    let mut nx: [u8; SLOTS] = [0u8; SLOTS];
    let mut gen: [u32; SLOTS] = [0u32; SLOTS];
    let mut regs: [u8; NREG] = [NIL; NREG];
    let mut regg: [u32; NREG] = [0u32; NREG];
    let mut j: usize = 0;
    while j < SLOTS
        invariant
            j <= SLOTS,
            nx@.len() == SLOTS as int,
            forall|k: int|
                0 <= k < j as int ==> (#[trigger] nx@[k]) == (if k + 1 < SLOTS as int {
                    (k + 1) as u8
                } else {
                    NIL
                }),
        decreases SLOTS - j,
    {
        arr_set_unchecked(&mut nx, j, if j + 1 < SLOTS { (j + 1) as u8 } else { NIL });
        j = j + 1;
    }
    let mut freehead: u8 = 0;
    let mut nalloc: usize = 0;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    proof {
        assert(pool@ =~= st0().pool);
        assert(nx@ =~= st0().nx);
        assert(gen@ =~= st0().gen);
        assert(regs@ =~= st0().rs);
        assert(regg@ =~= st0().rg);
        assert(St {
            pool: pool@,
            nx: nx@,
            gen: gen@,
            rs: regs@,
            rg: regg@,
            head: freehead,
            nalloc: nalloc as int,
        } =~= st0());
    }
    while o < nops
        invariant_except_break
            o <= nops,
            nalloc <= o,
            p <= len,
            4 <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            wf_ranges(
                St {
                    pool: pool@,
                    nx: nx@,
                    gen: gen@,
                    rs: regs@,
                    rg: regg@,
                    head: freehead,
                    nalloc: nalloc as int,
                },
            ),
            run(
                buf@,
                off as int,
                len as int,
                o as int,
                nops as int,
                p as int,
                St {
                    pool: pool@,
                    nx: nx@,
                    gen: gen@,
                    rs: regs@,
                    rg: regg@,
                    head: freehead,
                    nalloc: nalloc as int,
                },
                acc,
            ) == run(buf@, off as int, len as int, 0, nops as int, 4, st0(), 0),
        ensures
            acc.wrapping_mul(31).wrapping_add(nalloc as u64) == run(
                buf@,
                off as int,
                len as int,
                0,
                nops as int,
                4,
                st0(),
                0,
            ),
        decreases nops - o,
    {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf_get_unchecked(buf, off + p);
        let a: u8 = buf_get_unchecked(buf, off + p + 1);
        let ghost st_in = St {
            pool: pool@,
            nx: nx@,
            gen: gen@,
            rs: regs@,
            rg: regg@,
            head: freehead,
            nalloc: nalloc as int,
        };
        let ghost acc_in = acc;
        let ghost p_in = p as int;
        let ghost o_in = o as int;
        p = p + 2;
        let r: usize = (a % NREG as u8) as usize;
        let v: u64 = if c % 4 == 0 {
            if freehead == NIL {
                SENT
            } else {
                let s: usize = freehead as usize;
                freehead = arr_get_unchecked(&nx, s);
                arr_set_unchecked(&mut pool, s * BLK, a);
                arr_set_unchecked(&mut pool, s * BLK + 1, a.wrapping_mul(7).wrapping_add(1));
                arr_set_unchecked(&mut regs, r, s as u8);
                let gs: u32 = arr_get_unchecked(&gen, s);
                arr_set_unchecked(&mut regg, r, gs);
                nalloc = nalloc + 1;
                (s as u64).wrapping_add((gs as u64).wrapping_mul(8))
            }
        } else {
            let h: u8 = arr_get_unchecked(&regs, r);
            let g: u32 = arr_get_unchecked(&regg, r);
            // THE SAFETY LINE. c/kernel.c omits the second conjunct.
            //
            // ⚠ Nothing about this `if` is forced by the proof system. Both
            // arms type-check without it, `h as usize` is in range either way,
            // and no permission is consumed anywhere in this function. What
            // fails without it is the POSTCONDITION -- the loop stops computing
            // `run` -- and that is a functional obligation, not a memory-safety
            // one. See the module note and ../NOTES.md 6b.
            if h == NIL {
                SENT
            } else if arr_get_unchecked(&gen, h as usize) != g {
                SENT
            } else if c % 4 == 1 {
                let gh: u32 = arr_get_unchecked(&gen, h as usize).wrapping_add(1);
                arr_set_unchecked(&mut gen, h as usize, gh);
                arr_set_unchecked(&mut nx, h as usize, freehead);
                freehead = h;
                1
            } else if c % 4 == 2 {
                arr_get_unchecked(&pool, h as usize * BLK + 1) as u64
            } else {
                arr_set_unchecked(&mut pool, h as usize * BLK + 1, a.wrapping_mul(13)
                    .wrapping_add(3));
                3
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        proof {
            let st_out = St {
                pool: pool@,
                nx: nx@,
                gen: gen@,
                rs: regs@,
                rg: regg@,
                head: freehead,
                nalloc: nalloc as int,
            };
            assert(st_out =~= step(st_in, c, a).0);
            assert(v == step(st_in, c, a).1);
            assert(run(buf@, off as int, len as int, o_in, nops as int, p_in, st_in, acc_in)
                == run(
                buf@,
                off as int,
                len as int,
                o_in + 1,
                nops as int,
                p_in + 2,
                st_out,
                acc,
            ));
        }
        o = o + 1;
    }
    // No epilogue: nothing was ever acquired.
    acc.wrapping_mul(31).wrapping_add(nalloc as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 4 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole window is present.
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                4 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps, so
            // Z3 needs both spelled out. Erases at compile time.
            proof {
                let pp: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(pp < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        pp == (acc as int) * (nwin as int),
                        acc <= u64::MAX,
                        nwin >= 1,
                ;
            }
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            proof {
                assert(k < nwin);
                vstd::arithmetic::div_mod::lemma_fundamental_div_mod(
                    n_blob as int,
                    stride as int,
                );
                assert((nwin as int) * (stride as int) <= n_blob as int);
                assert((k as int) * (stride as int) <= ((nwin as int) - 1) * (stride as int));
                assert(((nwin as int) - 1) * (stride as int) == (nwin as int) * (stride as int)
                    - (stride as int)) by (nonlinear_arith);
                assert((k as int) * (stride as int) + (stride as int) <= n_blob as int);
            }
            let r: u64 = kernel(buf, k * stride, stride);
            // Ghost only: this is what *consumes* the kernel's `ensures`.
            assert(r == pool_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
