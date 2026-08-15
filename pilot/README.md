# Pilot — calibration kernel (superseded by `patterns/p01-array-sum/`)

The simplest possible kernel (`acc += v[i]` over a run-time-sized array) built at
all five rungs. Its job was to check that the ladder is buildable and that the two
structural claims in `PLAN.md` hold. It did that — and then a review found three
defects in how it was measured and one in how it was *proved*. Both sets are
recorded below, because they are why the harness and the bench rules look the way
they do.

**The sources are frozen. Do not build on them — `patterns/p01-array-sum/` is the
supported successor.** The numbers here were corrected at TASK_001 and
independently re-derived at TASK_001_REVIEW.

| File | Rung | Static instrs (raw / padding-excl) | Executed `Ir` @ n=50 000 |
|---|---|---|---|
| `k.c` (gcc 13.3.0) | C | 32 / 30 | 125,019 |
| `k.c` (clang 22.1.6) | C, same-backend | 33 / 31 | 87,518 |
| `k_rust.rs` | safe Rust, `v[i]` | 57 / 46 | 87,542 |
| `k_verus.rs` | safe Rust, verified | 57 / 46 — *byte-identical to `k_rust`* | 87,542 |
| `k_unsafe.rs` | unsafe Rust, `get_unchecked` | 37 / 33 | 87,520 |
| `k_unsafe_verus.rs` | unsafe Rust + Verus proof | 37 / 33 — *byte-identical to `k_unsafe`* | 87,520 |

All print `100` for input `10 20 30 40`, and agree on the checksum at every `n`
tested. The pilot has no safe-tuned rung; see `.memory/01-ladder.md` finding 3 for
why that omission mattered.

## What it establishes

1. **Proofs are free at run time.** Verus erases ghost code, `requires`, `ensures`,
   invariants and `decreases`; the emitted kernel is byte-identical to what rustc
   emits for the same exec code — verified on raw machine-code bytes
   (`e5310297…` for the safe pair, `a23e076c…` for the unsafe pair), not on a
   normalised text digest, which can collide.
2. **Proofs are also not, by themselves, an optimisation.** Proving the safe
   version panic-free leaves all 57 instructions in place — rustc never learns what
   Z3 knew. The win arrives only when the proof is spent *licensing unsafe code*,
   which lands on plain unsafe Rust's exact machine code with `i < v.len()`
   discharged by the verifier at every access.

So rung 5 is not "safe Rust, but faster" — it is "unsafe Rust, with the obligation
moved from the CPU to the SMT solver at compile time." The cost shows up as proof
effort and as whatever must be trusted.

## Four defects this pilot taught us

1. **The measured "20-instruction win" is soft.** Raw 57→37 is 20; padding-excluded
   46→33 is 13. Dynamically it is 7–22 executed instructions per call depending on
   `n mod 4`, and an iterator-based safe rung (which the pilot lacks) closes it to
   ~6. LLVM hoists the bounds check out of the vector loop entirely.
2. **"C beats Rust" was a gcc artefact, with the sign backwards.** gcc emits fewer
   static instructions than clang and executes 42.9% more. clang — the same LLVM
   rustc uses — emits the identical 7-instruction loop body as unsafe Rust.
3. **The TCB was under-counted 3×.** Published as "one 3-line `get_unchecked`
   wrapper"; the real tally is **3 `external_body` items**: `get_unchecked`, `out`,
   and `main`.
4. **The proof had no consumer, and the published run falsified it.** Because
   `main` is `#[verifier::external_body]`, the kernel's `requires n < 1000` was
   never discharged by any call site — the proof verified and constrained nothing.
   The headline run at n = 50 000 then printed `24975000`, which the kernel's own
   `ensures r < 1000*1000` declares impossible. The *machine code* was fine, so the
   performance numbers stand; the R5 *label* did not.

Defect 4 is why `.memory/02-bench-rules.md` now requires every R5 cell to have a
verified call site and a proof domain covering every measured input, enforced by
`harness/check.py`.

## The trusted base

The interesting part of the TCB is one wrapper — but it is not the whole TCB (see
defect 3):

```rust
#[verifier::external_body]                    // body trusted, not verified
fn get_unchecked(v: &Vec<u64>, i: usize) -> (r: u64)
    requires i < v.len(),                     // ...but every caller must prove this
    ensures  r == v[i as int],
{ unsafe { *v.get_unchecked(i) } }
```

vstd ships no specification for `<[T]>::get_unchecked`, so this wrapper (or an
`assume_specification`) is unavoidable. It is also the honest accounting: the
`requires` is checked at every call site, the *body* is taken on faith. A wrong
`ensures` here axiomatises a falsehood and the proof above it means nothing — which
is why `PLAN.md` makes TCB size a reported metric, and why an `external_body` on a
*driver* is far more dangerous than one on a leaf helper.

## Reproduction

Commands in `TOOLCHAIN.md` ("Pilot reproduction"). Binaries build to
`.temp/build/pilot/bin/`; this directory stays source-only.
