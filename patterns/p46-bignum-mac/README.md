# p46 — schoolbook bignum multiply-accumulate into a fixed-capacity scratch

Two bignums whose **limb counts arrive in the input**, multiplied schoolbook
into a product buffer of **fixed** capacity. The kernel checks that the declared
operands fit in the *window* and — in the buggy C rung — never checks that their
product fits in the *buffer*.

```c
if (8 + 8 * (n + m) > len)   return 0;      /* the INPUT bound: every rung has it */
if (n + m > OUTCAP)          return REJ;    /* c/kernel.c omits exactly this line  */
for (i = 0; i < n; i++) { carry = 0;
    for (j = 0; j < m; j++) {
        t = (unsigned __int128)a[i] * b[j] + out[i + j] + carry;
        out[i + j] = (uint64_t)t;  carry = (uint64_t)(t >> 64); }
    out[i + m] = carry; }
```

The real thing this models: OpenSSL's `BN_mul()` calls `bn_wexpand(rr, top)`
before `bn_mul_normal()` writes `na + nb` words into `r`, and
`bn_mul_add_words()` then indexes `rp[]` and `ap[]` with no test at all. The
word counts come from the `BIGNUM`s the caller was handed. Getting the expand
wrong is the classic bignum miscount.

## The unflattering sentence first

**p46's bug class is this tree's FOURTEENTH `index >= len`.** Its nearest
sibling is `p05`. What is *not* p05's:

- **p05's INDEX arithmetic is nonlinear (`i*ncol + j`) and its DATA arithmetic
  is trivial. p46 is the mirror.** The index is `i + j`, purely linear; the
  nonlinear obligation is about the *value* — `a*b + c + carry <= 2^128 − 1`,
  exactly — and the values are the attacker's.
- **The out-of-bounds access is a WRITE.** p05's is a read.
- It is the tree's first `by (bit_vector)` and first `by (compute)` in
  executable position (0 hits across the 23 pre-existing `verus.rs` files).

**And the memory-unsafe framing is conditional.** The identical miscount with a
clamped index — `out[(i + j) % OUTCAP]` — is exit 0 with ASan and UBSan both
silent: a wrong answer and no memory event, which is `p31`'s death. The clamp is
`forbidden` in the hashed contract, and so is a run-time-sized product buffer.
Both were settled by runs before any cell was built (`NOTES.md` 0a).

## The four results

1. **The harm is SILENT in 6 of the 8 plain C cells, and the mechanism is the
   ORDER OF TWO AUTOMATIC ARRAYS.** The kernel has a second scratch, `bl[256]`;
   where the compiler places it immediately above `out`, the overflow lands
   *inside it* — no fault, no canary, exit 0, wrong answer. gcc does that at
   `-O0` and `-O3`, clang at `-O3` only, and at `-O0` clang puts the arrays the
   other way round and the program SIGSEGVs. This is **p02's finding moved from
   the heap to the stack**, and it is why the box's default
   `-fstack-protector-strong` does not help: the canary is not what gets
   written. ASan and UBSan see it on every cell.

2. **p46's per-MAC safety tax is 0.00000.** LLVM discharges `i + j < OUTCAP`
   itself — from `n, m <= 255` and the one test `c/kernel.c` omits — and
   **deletes all three bounds checks**: the safe rung's MAC loop contains no
   conditional branch but its own `jne`. That is the exact contrast p05 could
   not have: p05's obligation is nonlinear and LLVM fails it, which is why p05
   pays `O(nrow)` and p46 pays nothing.

3. **SAFE RUST IS CHEAPER THAN UNSAFE RUST HERE, AND NONE OF IT IS SAFETY.**
   Having removed the checks, LLVM unrolls the safe loop 2× and not the unsafe
   one. The rolled-vs-rolled control puts the underlying spelling difference at
   **+2.00 Ir per MAC step AGAINST safe Rust**, exactly, five shapes, zero
   residual — a carry-materialisation difference derived instruction by
   instruction in `NOTES.md` 8a. Do not read `R3 − R4` as a safety number.

4. **The cheapest unsafe spelling found is not a rung, and the reason is the
   prover.** It takes a mutable sub-slice of the product scratch; at the pinned
   vstd `slice_subrange` covers `&[T]` only and `ExSliceIndex::index_mut`
   carries a `requires` and **no `ensures`**, so a write through it is sound but
   valueless — you can prove what did not change and not what did. It is
   **−697 to −2597 Ir/call** below the shipped R4 and below every safe spelling.
   `.memory/01-ladder.md` finding 14's mechanism with a number on it
   (`NOTES.md` 0c).

## The rungs

| rung | file | how `i + j < OUTCAP` is known | what it costs |
|---|---|---|---|
| R1 | `c/kernel.c` | **it is not** — the bug | — |
| R1h | `c/kernel_hardened.c` | one compare before the loops | **+2.00 (clang) / +4.00 (gcc) per call, flat** |
| R2 | `safe_naive.rs` | the language checks per access | **0.00 — LLVM removes them** |
| R3 | `safe_tuned.rs` | one reslice check per row | `O(n)` |
| R4 | `unsafe.rs` | the author asserts it | 0, and it is the dearest Rust rung |
| R5 | `verus.rs` | **Verus proves it** | 0 instructions; byte-identical to R4 at `-O3` |

**Four hardening strategies with four different asymptotics** — `0`, `O(1)`,
`O(n·m)`-that-vanishes, `O(n)` — priced side by side in `NOTES.md` 8e. C's fix
is the cheapest non-zero one *and* it is `O(1)`: the limb counts are two bytes
in the header, so C can test the whole obligation once before it starts, where
p19's hardened rung had to walk 2048 bytes.

## What is proved, and what is not

`verus.rs` is `21 verified, 0 errors` (`24` under `--cfg slb_twin`) with no
`assume`, no `admit` and no hand-written axiom. The postcondition is
`r == bn_fold(buf@, off, len)` — a full functional postcondition of the
schoolbook **algorithm**, the same shape every kernel in this tree carries.

⚠ **It is NOT a proof that the algorithm computes `a × b`.** That needs a
limbs-to-`nat` valuation and a nested partial-sum induction and was deliberately
not attempted (`NOTES.md` 6b). The gap is closed by *testing* instead:
`model.py` computes each window a second way, with one Python big-integer
multiply, and the gate diffs the two on every window of every committed input.

⚠ **The `ensures` is not "stronger than any in the tree".** `TASK_086` claimed
that; counted (`controls/census.py --ensures`), all 23 kernels already carry a
full functional postcondition and **151** of the tree's 159 `ensures` conjuncts
are equalities, not bounds (`NOTES.md` 6d). What is new is the proof *mode*, not
the strength.

## Files

`spec.md` is the contract and the pins. `NOTES.md` carries every measurement,
both corrections the shipped cells forced on the pre-build probes, the
instruction-by-instruction derivation, the spelling spread on both sides, and
an explicit list of what was not done. `inputs/gen.py` writes the matrix and the
three sweep bands the laws are fitted from — two axis bands and, because a
two-parameter law fitted on two axis-aligned bands has never been tested off the
axes, **ten off-axis blobs that are genuinely out of sample.**
