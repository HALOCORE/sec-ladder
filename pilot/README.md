# Pilot — calibration kernel

The simplest possible kernel (`acc += v[i]` over a run-time-sized array) built at
all five rungs of the ladder. Its job is not to be interesting; it is to check
that the ladder is buildable and that the two structural claims in `PLAN.md`
hold. Reproduction commands are in `TOOLCHAIN.md`.

| File | Rung | Kernel instructions (`-O3`) |
|---|---|---|
| `k.c` | C (gcc) | 33 |
| `k_rust.rs` | safe Rust, `v[i]` | 58 |
| `k_verus.rs` | safe Rust, verified | 58 — *identical to `k_rust`* |
| `k_unsafe.rs` | unsafe Rust, `get_unchecked` | 38 |
| `k_unsafe_verus.rs` | unsafe Rust + Verus proof | 38 — *identical to `k_unsafe`* |

All five print `100` for input `10 20 30 40`.

## What it establishes

1. **Proofs are free at run time.** Verus erases ghost code, `requires`,
   `ensures`, invariants and `decreases`; the emitted kernel is instruction-for-
   instruction what rustc emits for the same exec code. Verifying does not cost
   a cycle.
2. **Proofs are also not, by themselves, an optimisation.** Proving the safe
   version panic-free leaves all 58 instructions in place — rustc never learns
   what Z3 knew. The 20-instruction win arrives only when the proof is spent on
   *licensing unsafe code* (`k_unsafe_verus.rs`), which lands on plain unsafe
   Rust's exact assembly with `i < v.len()` discharged by the verifier at every
   access.

So rung 5 is not "safe Rust, but faster" — it is "unsafe Rust, but with the
obligation moved from the CPU to the SMT solver at compile time." The cost shows
up as proof effort and as whatever must be trusted.

## The trusted base

Here it is three lines, and it is the whole unsafe surface of `k_unsafe_verus.rs`:

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
`ensures` here axiomatises a falsehood and the proof above it means nothing —
which is why `PLAN.md` makes TCB size a reported metric.

## Caveats

- gcc's 33 vs LLVM's 38 is a codegen difference (vectorisation prologue), not a
  cost of Rust. Comparing like with like needs clang — see `PLAN.md`.
- The driver reads its data from `argv`, which is enough to stop constant folding
  here, but real patterns take input from a file (`PLAN.md`, "Benchmark program
  design").
- `#[inline(never)]` on the kernel makes the assembly readable and the counts
  comparable; it is not how a real program is compiled. Both modes get measured
  in the real harness.
