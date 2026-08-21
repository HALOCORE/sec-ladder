# TASK_055 report — two prover-capability probes

**Role:** research engineer. **Status:** both probes complete. **Nothing landed**
— no file outside `.temp/p55/` was modified; `patterns/`, `.memory/`,
`harness/`, `common/`, `pilot/` untouched. Working notes and every probe source:
`.temp/p55/NOTES.md`, `.temp/p55/w1755898/`.

Running count of agents that contradicted the manager with a measurement: **81**.
(This task adds one: TASK_055's probe-2 framing was wrong in both directions —
`raw_ptr` works, and the thing that actually constrains the pattern is
reproducibility, which nobody named.)

Every number below was produced at the pinned toolchain — Verus
`0.2026.08.09.92f466f`, rustc `1.97.1`, gcc `/usr/bin/gcc`, clang
`~/tools/llvm/bin/clang` — with the gate's own build flags
(`harness/build.py::rust_flags`) and the gate's own oracles
(`harness/asm.py::identity_level`, `harness/measure.py::callgrind_ir`).
**No wall-clock measurement was taken**, per the task's constraint.

---

# Probe 1 — p08's `copy_in`

## §1.1 What R4 spells — established BEFORE measuring

`patterns/p08-overlap-move/unsafe.rs:33-36`, character-identical in
`safe_naive.rs:39`, `safe_tuned.rs:29` and in `verus.rs:332` (the trusted body):

```rust
#[inline(always)]
fn copy_in(dst: &mut [u8], src: &[u8], from: usize, n: usize) {
    dst[..n].copy_from_slice(&src[from..from + n]);
}
```

**p08 is the p06 row of the task's table, not the p02 row: R4 spells
`copy_from_slice`.** (`move_right`/`core::ptr::copy` is a *different* trusted
item and is out of scope; it stays.)

**But there is a wrinkle p06 also hit and the task's table does not carry.**
`dst[..n]` is `RangeTo<usize>`, and the only `SliceIndexSpecImpl<[T]>` impls at
the pinned vstd are `usize` (`std_specs/slice.rs:14`) and `Range<usize>` (`:31`).
Checked in `~/tools/verus/vstd/`, not assumed. So the *shipped spelling itself*
is unverifiable and the body must change.

**Predictions written before measuring** (`.temp/p55/NOTES.md`, §"Prediction,
written BEFORE measuring"):

- P1 the contract discharges with `split_at_mut` — HIGH confidence.
- P2 obligations 11 → 12, twin 15 → 16.
- P3 codegen — flagged as the coin-flip, with the note that **p06's
  "byte-identical" does not settle it**, because p06 edited `unsafe.rs` to the
  same `split_at_mut` spelling, so p06 compared `split_at_mut` against
  `split_at_mut`. p08's real question is `dst[..n]` (shipped R4) vs
  `split_at_mut` (candidate R5).

P1 and P2 confirmed. **P3 confirmed at `-O3` and REFUTED at `-O0`.**

## §1.2 The shipped spelling cannot be verified — reproduced on p08's own contract

`.temp/p55/w1755898/probe_keepspell.rs` — p08's `copy_in` `requires`/`ensures`
verbatim, `external_body` dropped, body unchanged:

```
error: precondition not satisfied    (vstd/std_specs/core.rs:69   index_req)
error: precondition not satisfied    (vstd/std_specs/slice.rs:207 copy_from_slice)
error: postcondition not satisfied
verification results:: 1 verified, 1 errors
```

`dst[0..n]` (`Range<usize>`, which *is* specified) — `probe_range.rs`:

```
error: postcondition not satisfied
verification results:: 1 verified, 1 errors
```

`index_mut`'s `call_ensures` is never instantiated, so the write-back is not
available. `split_at_mut` is the only route — the same conclusion TASK_048
reached on p06, here reproduced independently on p08's contract.

## §1.3 The contract DOES discharge without the wrapper

`probe_copyin.rs`, contract copied character-for-character from
`verus.rs:322-333`:

```rust
assert(src@.len() == vstd::slice::spec_slice_len(src));   // +1 ghost line; without it:
                                                          // "possible arithmetic underflow/overflow" on `from + n`
let (a, _b) = dst.split_at_mut(n);
a.copy_from_slice(&src[from..from + n]);
```
```
verification results:: 2 verified, 0 errors
```

Whole file, `copy_in` no longer `external_body`
(`.temp/p55/w1755898/patterns/p08nw/verus.rs`):

```
shipped        : 12 verified, 0 errors     (baseline re-measured: 11)
--cfg slb_twin : 16 verified, 0 errors     (baseline re-measured: 15)
```

Pins that would move: `verus.items.verus.rs.copy_in.external` →`null`,
`verus.obligations` 11→12, `verus.twin_obligations` 15→16, `contract_sha256`.
**`idiom.required` is NOT among them** — p08's six `required` entries pin the
memmove spelling, the guard, `dr = d + r`, `%` vs `&` and the scratch, and
**none of them mentions the copy**. This is the one place p08 is cheaper than
p06, whose `required[5]` pinned `dst[..n].copy_from_slice(...)` verbatim and
forced a declaration edit.

## §1.4 Codegen — byte-identical at `-O3`, +2 instructions at `-O0`

`-O3 isolated`, gate flags:

| binary | `n_fn` / nopad / bytes | `md5_fn` | `md5_raw` | pads |
|---|---|---|---|---|
| shipped R4 (`dst[..n]`) | 168 / 166 / 625 | `9259612a652d` | `44b63d20ccf1` | 5 |
| shipped R5 (trusted `dst[..n]`) | 168 / 166 / 625 | `9259612a652d` | `44b63d20ccf1` | 5 |
| **candidate R5 (verified `split_at_mut`)** | **168 / 166 / 625** | **`9259612a652d`** | **`44b63d20ccf1`** | **5** |
| R4 respelled `split_at_mut` | 168 / 166 / 625 | `9259612a652d` | `44b63d20ccf1` | 5 |

`-O0 isolated`:

| binary | `n_fn` / nopad / bytes | `md5_fn` |
|---|---|---|
| shipped R4 | 206 / 206 / 1159 | `7bbb6ae949ad` |
| shipped R5 | 206 / 206 / 1159 | `7bbb6ae949ad` |
| **candidate R5** | **208 / 208 / 1180** | **`b7842f19a14e`** |
| R4 respelled | 208 / 208 / 1180 | `b7842f19a14e` |

Identity levels from `asm.identity_level`, the gate's own oracle:

```
O3  R4(shipped)  vs R5(candidate)  -> exact
O0  R4(shipped)  vs R5(candidate)  -> differ     <-- spec.md pins `norel`
O0  R4(respelled) vs R5(candidate) -> exact
O3  R4(shipped)  vs R4(respelled)  -> exact
O0  R4(shipped)  vs R4(respelled)  -> differ  (206 vs 208)
```

`IDENTITY_LEVELS = ["differ","counts","norel","exact"]` and
`check.py::check_identity` fails when `got_i < want_i`.
p08 pins `{"a":"unsafe","b":"verus","O0":"norel","O3":"exact"}`.
**So editing `verus.rs` alone FAILS gate stage 3c at `-O0`.**

**Mechanism of the +2**, from `asm.py diff` at `-O0`: `<[T]>::split_at_mut`
returns a two-slice tuple — four words — so it is returned through the hidden
`sret` pointer (`lea (%rsp),%rdi` appears in the callee-argument setup) where
`<[T] as IndexMut<Range>>::index_mut` returns a two-word slice in `rax:rdx`.
Two extra `mov`s of ABI shuffle. **It is not a check**: both spellings keep
exactly one bounds check and both produce the same 5 panic pads at the same
source sites (`patterns/p12-strcat-fixed/controls/pads.py`).

The ghost `assert` is free: `r4_splitat-O0` (plain rustc, no ghost) is
`exact`-identical to `r5_nowrap-O0` (Verus, with the ghost).

## §1.5 The price, in Ir

`harness/measure.py::callgrind_ir`, per-function exclusive Ir on the `kernel`
symbol, `isolated`:

| | `small` (25 000 calls) | `large` (8 000 calls) | Δ per call |
|---|---:|---:|---:|
| `-O3` shipped | 74 600 000 | 189 040 000 | — |
| `-O3` candidate | 74 600 000 | 189 040 000 | **+0.00** |
| `-O0` shipped | 229 325 000 | 590 488 000 | — |
| `-O0` candidate | 229 375 000 | 590 504 000 | **+2.00 flat** |

Checksums agree across all four variants on all six inputs
(`adversarial-dbig` 0, `dzero` 0, `overlap` 17006177784580028288, `stride3` 0,
`large` 16961355432730674521, `small` 5963384295905503290).

The respelling costs the same +2 on **every** Rust rung, and nothing at `-O3`:

```
O3 safe_naive  ship vs split_at_mut -> exact   269/263 both
O0 safe_naive  ship vs split_at_mut -> differ  241/241 -> 243/243
O3 safe_tuned  ship vs split_at_mut -> exact   205/204 both
O0 safe_tuned  ship vs split_at_mut -> differ  207/207 -> 209/209
O3 unsafe      ship vs split_at_mut -> exact   168/166 both
O0 unsafe      ship vs split_at_mut -> differ  206/206 -> 208/208
```

## §1.6 U-license / V-gap / infra, before and after — the trust RELOCATES

| | class | what is trusted | p08 TCB |
|---|---|---|---|
| before | **V-gap** | author-written `external_body fn copy_in`; its `ensures` was invented in this pattern and is read by no one else | **4 items / 10 lines** |
| after | *(item gone)* | vstd `assume_specification` for `<[T]>::split_at_mut` (`std_specs/slice.rs:185`) and `<[T]>::copy_from_slice` (`:205`) | **3 items / 9 lines** |

After the edit p08 is **1 U-license (`move_right`) + 0 V-gap + 2 infra
(`load_input`, `emit`)**.

**The trust does not disappear; it relocates into vstd.** Two things sharper
than p06's case:

1. **p08's relocation is smaller than p06's.** p06's `scr_load` took
   `&mut [u8; 64]`, so removing its wrapper newly relied on
   `vstd/array.rs:175 ref_mut_array_unsizing_coercion` — itself `external_body`
   *inside* vstd. p08's `copy_in` already takes `&mut [u8]`, so the
   `&mut [u8; 4096] → &mut [u8]` coercion happens at the **call site** inside
   the verified `kernel` and is **already relied upon by the shipped 11/0**.
   The only *new* vstd axioms are the two `assume_specification`s.

2. ⚠ **The recorded reason for the V-gap is FALSE, and that is true whichever
   route is taken.** Four places in p08 still say *"vstd ships no specification
   for `copy_from_slice`"* — `verus.rs:304`, `NOTES.md:995` (the TCB table's
   `why` cell), `NOTES.md:1008` and `NOTES.md:1133`. It ships one at
   `std_specs/slice.rs:205`. The real gap is **`RangeTo<usize>` has no
   `SliceIndexSpecImpl`** — the unverifiable thing is the index type `..n`, not
   the copy. This is the same false sentence TASK_048 corrected in
   `.memory/04-verus.md` and on p06, still standing in p08's four places.

**p08's OTHER trusted item is irreducible, and I checked rather than assumed.**
`move_right`'s stated reason (`verus.rs:220`, *"vstd ships no specification for
`core::ptr::copy`"*) is **TRUE**: the only copy-family spec in the pinned vstd is
`<[T]>::copy_within` (`std_specs/slice.rs:235`), the safe slice method — and
p08's `idiom.required[1]` *requires* R4/R5 to spell the move `core::ptr::copy`
(R3 is the rung that uses `copy_within`). So `move_right` cannot be de-trusted
without deleting the pattern, and it is p08's own declaration that says so.
**p08 cannot go below 3 items.**

**Census consequence.** TASK_048 measured exposure 2/58 → 1/57 after p06. If
p08's goes it is **0 of 56**. p09's `popcount64` is a real V-gap
(`u64::count_ones` is `is not supported`); the 25 U-license items wrap
operations that are all `is not supported`; infra items have nothing upstream to
relocate into. **The relocatable set is exhausted.** Durable form: *only a V-gap
item can ever relocate, and after p08 there is no relocatable V-gap left in the
tree.* — but see §2.5, which shows this is a fact about the fourteen patterns
already built, and is **false for the pointer family**.

## §1.7 Recommendation, with the price

**p06 has already solved this exact problem and the solution is written into its
own declaration — I missed it on the first pass and found it while checking a
citation.** `patterns/p06-rotate/spec.md`'s `idiom.required[5].rust` says:

> THE RECEIVER IS SCOPED 2-AND-2 AND THE SCOPE IS TASK_048'S … `dst[..n]` is the
> receiver in `safe_naive.rs` and `safe_tuned.rs`, and `s.split_at_mut(n)` is the
> receiver in `unsafe.rs` and `verus.rs` … THE PRICE IS MEASURED: at O3 it is
> ZERO in every rung …, and at O0 it costs `unsafe.rs` **+3 static instructions
> (416/416 → 419/419)**, which is what keeps identity at `norel` there.

So p06 hit the same `-O0` cost, and its resolution was **respell only the two
rungs the identity pin binds together** — R4 and R5 — and leave R2 and R3 on
`dst[..n]`. That is a third route, and it is strictly better than the one I
first enumerated. p08's numbers for it are already in §1.4: `r4_splitat-O0` vs
`r5_nowrap-O0` is **`exact`**.

| route | TCB | `-O3` | `-O0` | gate |
|---|---|---|---|---|
| **A** — edit `verus.rs` only | 4 → 3 | identity `exact`, 0.00 Ir | identity **`differ`** vs pinned `norel` | **FAILS stage 3c** |
| **B′** — respell `copy_in` in **`unsafe.rs` + `verus.rs` only** (p06's shipped route) | 4 → 3 | identity `exact`, 0.00 Ir, R2/R3/R4/R5 all byte-identical to today | identity **`exact`** (stronger than the pinned `norel`); **R4 and R5 move +2 insns / +2.00 Ir per call; R2 and R3 do not move at all** | passes; re-ship confined to **two** rungs at `-O0` |
| **B** — respell in all four Rust rungs | 4 → 3 | identity `exact`, 0.00 Ir | identity `exact`; **all four rungs move +2 insns / +2.00 Ir per call** | passes; re-ship of four rungs at `-O0` |
| **C** — keep the wrapper, record the price | 4 | — | — | passes (p02's precedent) |

**My recommendation: route B′, with the price published; land the §1.6
correction whichever route is taken.**

Reasoning:

- **The false reason must be corrected in all three places regardless** —
  `verus.rs:305`, `NOTES.md:994`, `unsafe.rs`'s header. That is a documentation
  fix with no measurement attached, and it is the same sentence TASK_048 already
  corrected twice elsewhere.
- **B′ has a direct precedent that is already reviewed and shipped.** p06 chose
  it, published its price inside its own `idiom` entry, and the reasoning
  transfers verbatim: the `identity` pin makes R4 and R5 one program, so they
  respell together; nothing chains R2/R3 to the prover, so they do not.
- **The price is confined to `-O0` and to two rungs.**
  `results/tables/p08-overlap-move.md:86` already carries *"`O0` rows exist to
  read the lowering. No performance claim may rest on one"*, so no published
  p08 *claim* moves. What moves is two static `-O0` rows and their `Ir(kernel)`
  columns, and `.memory/02-bench-rules.md`'s two-number treatment applies:
  *"shipped `dst[..n]` 206/206, respelled `split_at_mut` 208/208, +2.00 Ir/call,
  `-O0` only; `-O3` byte-identical, `md5_raw 44b63d20ccf1`"*.
- **p08 gets a strictly better `-O0` identity than p06 did.** p06's `scr_load`
  takes `&mut [u8; 64]`, so it needs the extra `let s: &mut [u8] = dst;`
  reborrow and lands at +3 with identity `norel`. p08's `copy_in` already takes
  `&mut [u8]`, so it is +2 and identity measures **`exact`** — i.e. p08 would
  *keep* the "stronger than pinned" note it has today.
- **Three comments become false and must be fixed with it**, exactly as on p06:
  `unsafe.rs:31-32` (*"Identical in all four Rust rungs"*), `safe_tuned.rs:9` and
  `safe_naive.rs:23` (*"same `copy_in`"*) — plus the four false-reason sites
  listed in §1.6.
- **The direction test.** Removing a trusted item makes the trusted base smaller,
  which flatters the thesis. p08's `idiom.required` pins no copy spelling
  (§1.3), so B′ touches no declaration and is a measurement, not a declaration
  edit — the same category as p06's landing. ⚠ But note the asymmetry that
  creates: **p06's 2-and-2 split is documented because p06's declaration pinned
  the spelling; p08's would be undocumented because p08's does not.** If the
  manager wants it in `idiom.required`, adding the entry *is* a declaration edit
  and the direction test governs it. My recommendation is to document the split
  in `NOTES.md` and in the three source comments, and to leave `idiom.required`
  alone.
- **What is bought is small, and route C remains defensible.** The item removed
  carries the least weight in the tree: no `unsafe`, cannot license an unchecked
  access, and `copy_from_slice` panics rather than misbehaving if its `ensures`
  is wrong. p08's headline is about `move_right`, which stays either way. A
  manager who does not want to re-ship two `-O0` rows for a 4→3 can stop at
  route C with the corrected reason, which is exactly what p02 did.

⚠ **Do not describe the outcome as "free".** It is free at `-O3` — genuinely,
`md5_raw` unchanged — and it costs **+2.00 Ir/call at `-O0` on R4 and R5**.
p06's own declaration already states its version of that sentence
(*"at O0 it costs unsafe.rs +3 static instructions"*), and TASK_048's landing
report is the place where the `-O0` half went unquoted. Quote both halves.

---

# Probe 2 — `vstd::raw_ptr`, and the missing bug class

## §2.1 Can a stack local supply a `PointsTo`? **No** — measured

Complete enumeration of `raw_ptr::PointsTo<T>` producers at the pinned vstd:

| producer | origin |
|---|---|
| `PointsToRaw::into_typed<V>(start)` (`raw_ptr.rs:832`) | a `PointsToRaw` |
| `allocate(size, align)` (`raw_ptr.rs:908`) | **the global allocator** |
| `PointsToRaw::empty(prov)` (`:791`) | empty domain — ZSTs only |
| `PointsTo::into_raw` (`:849`) | round-trip; needs one already |
| `SharedReference::points_to()` (`:1023`) | **an ordinary `&'a T`** |
| `cell::PCell::new`, `simple_pptr::PPtr::new` | *different* `PointsTo` types; `PPtr` is itself `allocate` |

`SharedReference` is the only route that starts from a plain reference — i.e.
from a stack local — and **its constructor is private**
(`.temp/p55/w1755898/p2a_stacklocal.rs`):

```
error[E0624]: associated function `new` is private
  --> p2a_stacklocal.rs:11:31   |  let sr = SharedReference::new(&x);
  --> vstd/raw_ptr.rs:1000:4    |  = note: private associated function defined here
error[E0624]: method `as_ptr` is private
  --> p2a_stacklocal.rs:13:28   |  let p: *const u64 = sr.as_ptr();
  --> vstd/raw_ptr.rs:1016:4
```

Only `points_to`, `value` and `ptr` are `pub`; the sole public way to get a
`SharedReference` is `ptr_ref2`, which already needs a `PointsTo`. Circular.
vstd's own comment calls `SharedReference` *"a stop-gap"* (`raw_ptr.rs:975`).

**p14's reviewer predicted this and was right — but for a mechanical reason (a
missing `pub`), not a semantic one, and that matters: it can be lifted by an
upstream one-word change.** There is also **no `Vec` → `PointsToRaw` bridge
anywhere in vstd**; `allocate` is the sole origin of raw-pointer permission.

## §2.2 Heap: `raw_ptr` does hold a pointer array, deref it, and verify

`.temp/p55/w1755898/p2b_heap.rs` — two descriptors into one `allocate(2,1)`:

```
verification results:: 2 verified, 0 errors
```

`allocate` → `PointsToRaw::split(Set::range(..))` → `into_typed::<u8>(addr)` →
`ptr_mut_write` → `ptr_ref` → `into_raw().join()` → `deallocate`.
Two gotchas worth keeping:

- `into_typed`'s second precondition is `start % align_of::<V>() == 0` and needs
  `broadcast use vstd::layout::group_layout_axioms, vstd::layout::align_of_u8;`.
  `align_of_u8` is **deliberately outside** the alignment broadcast group
  (*"not part of the alignment broadcast group due to proof time-out"*,
  `layout.rs:266`), so the group alone is not enough.
- `Set::new` returns `Option<Set<A>>` at this vstd (`set.rs:133`); the splitter
  wants `Set::range(lo, hi)` (`set_lib.rs:780`).

## §2.3 p14's stated rejection reason is REFUTED

p14 §0 rejected the lifetime candidate because *"`as_ptr` / `add` /
`from_raw_parts` are unsupported at the pinned vstd — so R4 would not be a
rung."* `add`/`offset` are indeed unspecified. **But `<*mut T>::addr` and
`<*mut T>::with_addr` ARE specified** (`raw_ptr.rs:664`, `:675`), and
`with_addr` preserves provenance by construction. `base.with_addr(base.addr() + i)`
is a supported, strict-provenance spelling of pointer arithmetic, and
`allocate()` hands you the base pointer with no `as_ptr` anywhere. The route
p14 said did not exist, exists.

## §2.4 Is it R4-shaped? **Byte-identical** — the decisive measurement

`p2c_verus.rs` vs `p2c_plain.rs`, same `#[inline(never)] fn kernel`, Verus side
`ptr_ref(p, Tracked(perm))`, plain side `unsafe { &*p }`:

```
O3 verus vs plain -> exact   counts [4,4,12] both   md5_fn 23e454f4f601 both
O0 verus vs plain -> exact   counts [4,4,10] both   md5_fn 73986da896d6 both
both print 7
```

A **loop-shaped** kernel — `p2d_loop.rs` vs `p2d_plain.rs`, folding 64 bytes
through a `&[*mut u8]` descriptor slice, R5 carrying
`Tracked<&Map<int, PointsTo<u8>>>` and calling `perms.tracked_borrow(i as int)`
inside the loop:

```
verification results:: 3 verified, 0 errors
O3 verus vs plain -> exact   counts [65,64,206] both   md5_fn 20be44aa70de both   pads 2/2
O0 verus vs plain -> norel   counts [32,32,149] both   md5_fn bf2e77403da6/211f72a4dd0f  pads 11/11
both print 13944237674083663871
```

**`exact` at `-O3` and `norel` at `-O0` — exactly p08's own pinned identity
levels.** `Tracked` arguments erase from the ABI as well as from the body.
Per-item obligations: `kernel` 2 (body + loop body), `fold_perms` 1
(termination), `wf` 0.

## §2.5 Cost — and a finding that reopens TASK_048's PROVISIONAL conclusion

`grep -c unsafe p2d_loop.rs` = **1**, and that one token is inside the
`external_body main` written purely as codegen scaffolding (labelled as such in
the file). **A rung doing genuine raw-pointer work contains no `unsafe` token
and no project-local `external_body` at all**: `allocate`, `deallocate`,
`ptr_ref`, `ptr_mut_write`, `ptr_mut_read` are `external_body` *inside vstd*,
and `split`, `join`, `into_typed`, `into_raw`, `tracked_borrow` are vstd
`axiom fn`s.

⚠ **This contradicts TASK_048's PROVISIONAL *"the TCB column is NOT gameable,
because the relocation almost never exists"*.** That census ran over the
fourteen patterns already built, whose accessors (`get_unchecked`,
`count_ones`, `copy_nonoverlapping`, `as_ptr`, `ptr::add`) are all
`is not supported`. It is right retrospectively and **wrong prospectively**: for
the pointer family the relocation is **total**. Two consequences:

1. An arena/pointer pattern would publish **`tcb_items = 2`** (`load_input` +
   `emit`) — **fewer than p01's array-sum 3** — while doing manual allocation
   and raw-pointer reads. The TCB column would rank a raw-pointer kernel
   *safer* than a bounds-checked one. That is the exact failure the rejected
   two-number proposal was worried about, arriving from the direction nobody
   checked.
2. **The verified-twin regime goes idle.** `_is_trusted` keys on `external_body`
   + (`ensures` or `unsafe`); with no such item `check.py` 5a prints *"no trusted
   `unsafe` item, so no twin is required"* — **the same sentence the macro
   bypass produces** (`.memory/04-verus.md`, TASK_009_REVIEW). A legitimate
   `raw_ptr` pattern and the known bypass become indistinguishable in the
   verdict. **Fix this before building the pattern, not after.**

## §2.6 Does it model the bug? Yes — and the catcher is not the SMT solver

`p2b_uaf.rs`: `deallocate` consumes the `PointsToRaw`, so a read through a stale
descriptor afterwards is rejected:

```
error[E0382]: borrow of moved value: `p0`
  40 |  let tracked back = p0.into_raw().join(p1.into_raw());
     |                        ---------- `p0` moved due to this method call
  43 |  let v2: &u8 = ptr_ref(d[0], Tracked(&p0));
     |                                      ^^^ value borrowed here after move
```

**That is rustc's own move checker acting on a ghost token.** No Verus
obligation fails; the permission is an affine resource and `deallocate` takes
ownership of it. So the lifetime class is ruled out at R5 by **linearity** — the
same mechanism safe Rust uses at R2, applied to a proof object instead of to the
data. Every existing R5 in this tree fails an SMT obligation instead; this is a
structurally different R5 story and deserves its own paragraph wherever it lands.

R4 side, Miri on `p2e_uaf_plain.rs`:

```
error: Undefined Behavior: memory access failed: alloc312 has been freed, so this pointer is dangling
  --> p2e_uaf_plain.rs:16:64  |  ... .wrapping_add(*d[j] as u64) ...
help: alloc312 was allocated here:   let base = std::alloc::alloc(layout);
help: alloc312 was deallocated here: std::alloc::dealloc(base, layout);
```

## §2.7 The blocker nobody named, and how it is solved

A naked use-after-free is **not reproducible**, and `check.py:1249
check_checksums` requires every cell's stdout to equal `model.py`'s checksum on
every non-adversarial input *and* all cells to agree.

`free()` writes glibc's tcache `next` pointer and `key` into the **first 16
bytes** of the freed chunk, and both are ASLR-dependent. Measured on the same
slab, free-then-`malloc`-the-same-size, `p2g_uaf.c` (fold from offset 0) vs
`p2h_uaf16.c` (identical but the fold starts at offset 16):

| build | fold from offset 0 | fold from offset 16 |
|---|---|---|
| gcc `-O0` | `7994361797249294304` ×3 — stable | — |
| clang `-O0` | `7994361797249294304` ×3 — stable | — |
| gcc `-O3` | 3 runs, **3 different** values | **`6789584477807083544` ×4** |
| clang `-O3` | 3 runs, **3 different** values | **`6789584477807083544` ×4** |
| rustc `-O3` (`p2h_rust.rs`) | 5 runs, **5 different** values | **`6789584477807083544` ×4** |

**gcc, clang and rustc all agree at `-O3` on the same wrong answer**, which is
what stage 2 needs. Two caveats a `spec.md` would have to carry as fiats:

- the constraint (*the stale read window must begin at least 16 bytes into the
  freed chunk*) is a **glibc implementation detail**, not a property of C;
- **`same_chunk` itself is not portable** — for the same addresses gcc prints
  `1` while clang and rustc print `0`, because the pointer comparison folds
  differently under UB. A pattern must never print or branch on it.

(An earlier note in `.temp/p55/NOTES.md` §P2-7 blamed `Vec` growth for the
non-determinism; that was wrong and is withdrawn in §P2-9 with the measurement.)

## §2.8 Verdict, and a formulation the manager did not name

**A lifetime bug CAN have a full six-rung ladder at the pinned toolchain.**
Nothing that was predicted to block it does.

| predicted blocker | source | measured |
|---|---|---|
| "a stack local cannot supply a `PointsTo`" | p14 reviewer, UNTESTED | **TRUE** — `SharedReference::new` is private (E0624). Use `allocate()`. |
| "`as_ptr`/`add`/`from_raw_parts` unsupported, so R4 is not a rung" | p14 §0 | **FALSE** — `addr`/`with_addr` are specified; R4 == R5 `exact` at O3, `norel` at O0 |
| "`raw_ptr` will fail" | p14 reviewer | **FALSE** — 3 verified / 0 errors on a loop kernel |
| *(unforeseen)* reproducibility | — | **REAL, and solvable** — §2.7 |
| *(unforeseen)* R2/R3 need a different representation | — | **REAL, and it is the pattern's whole point** |
| *(unforeseen)* the TCB column and the twin regime both go blind | — | **REAL** — §2.5, fix first |

**The formulation.** The manager offered "indices + a generation counter" and "a
`Vec` dropped and reallocated". There is a third and it is the one that keeps
the ladder honest:

> **A slab of records with a handle table, where "free" is a real
> `deallocate` and the handle is a POINTER at R4/R5 and a `(slot, generation)`
> pair at R1h/R2/R3.**

- **R1 (C)** `malloc` slab, `char*` handles, `free`, read → UAF.
  **R1h** handles become `(slot, gen)` and each read compares the generation.
- **R2/R3 (safe Rust)** cannot hold the pointer at all, so the `(slot, gen)`
  representation is *forced*. Safe Rust's lifetime guarantee is paid for by a
  **representation change plus a per-access compare**, not by a bounds check.
- **R4** raw pointers, no generation.
- **R5** the same exec code with `PointsTo` permissions; the stale read is
  **unprovable** (§2.6) at **byte-identical codegen** (§2.4).

**What that measures is new to this project: the price of a LIFETIME guarantee,
which safe Rust charges as a REPRESENTATION rather than as a check.** Every
existing pattern's safe rung pays a comparison; this one pays a wider handle, an
extra indirection and a generation compare, and the proof pays zero.

⚠ **Two structural caveats, both measured or derived, not guessed:**

1. **If the slab is one allocation and "free" is a freelist push, the stale read
   is in bounds of a live allocation.** Miri does not flag it, `PointsTo`
   licenses it, and the bug is *logical*, not a lifetime bug — the same class as
   p17, which the tree already has. Only a **real `deallocate`** makes it the
   missing class, and a real `deallocate` drags in §2.7.
2. **R2/R3 are not "R4 plus a check", they are a different data structure.**
   The `driver.call_args` and `idiom` machinery assumes the rungs differ in one
   spelling; a representation split is a larger declaration surface than any
   shipped pattern has needed, and `.memory/02-bench-rules.md`'s
   "are the rungs semantically equivalent" question would have to be answered
   with a functional-equivalence argument rather than a diff.

---

# What I did NOT do

- **No pattern was edited.** `git status` shows no modified tracked file; p08 is
  byte-identical to what I found. Routes A/B/B′ were measured on copies under
  `.temp/p55/w1755898/patterns/`.
- **No wall-clock measurement**, per the constraint. Every perf number here is
  `Ir` or static.
- **`harness/check.py p08` was not run.** It rewrites `results/gate/p08-*.json`
  and other agents are working concurrently; nothing I did could change its
  result, since the tree is unmodified. Route B′ therefore has **not** been
  through a full gate — I measured stage 3c's oracle directly, not the gate.
- **The `--cfg slb_twin` baseline of 15 was re-measured**, not quoted from
  `spec.md`.
- Probe 2 built no `model.py`, no six-rung matrix and no gate run. It is a
  feasibility probe; the arena pattern §2.8 recommends is unbuilt, and **R1,
  R1h, R2 and R3 of it were never written** — I measured R4/R5 and the C
  reproducibility question only.
- **The permission map in `p2d_loop.rs` is populated by scaffolding, not by a
  proved loop.** `kernel` verifies against a `Map<int, PointsTo<u8>>` whose
  well-formedness is a `requires`; the `external_body main` supplies it with
  `Tracked::assume_new()`. A real pattern needs a ghost loop that splits the
  `PointsToRaw` `n` times under an invariant. I believe that is routine — the
  two-element version in `p2b_heap.rs` does it by hand and verifies — but **I
  did not write it, and the SMT cost of a 4096-slot map is unmeasured.**
- **I did not check whether `check.py` would actually accept a pattern with zero
  trusted items** (§2.5). I read `_is_trusted`'s key and the 5a message; I did
  not build a pattern to see the verdict.

## Reproducing this

`bash .temp/p55/repro.sh [all|probe1|probe2]` rebuilds every binary and
regenerates every number above from the probe sources in
`.temp/p55/w1755898/`. Both halves were run end to end; the outputs are
`.temp/p55/repro-probe1.log` and `.temp/p55/repro-probe2.log`, and every figure
in this report matches them. The binaries and callgrind blobs (237 MB) were
deleted afterwards per `CLAUDE.md` constraint 6; the sources, notes and logs
stay (`.temp/p55` is now 264 KB).
