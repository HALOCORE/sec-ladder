# p09 — bitset: the safety check that is not a bounds check

A bitset probed by an attacker-chosen list of bit indices. The guard is
`q < nbits`; the access is `words[q >> 6]`. **The bound the access needs is
derived from the guard through a shift**, and neither the guard's operand nor
the array's length appears in it — which is what makes p09 different from every
pattern before it.

- `spec.md` — the contract every rung implements, and the hashed `slb-contract`
  block the gate enforces.
- `NOTES.md` — the measurements, the proof record and the controls.
- `controls/gen_controls.py` — regenerates every control by exact-string
  substitution off the shipped rungs, asserting its own hit counts.

## The C bug

```c
for (k = 0; k < nq; k++) {
    uint64_t q = load_u32(buf, qs + (size_t)(4 * k));
    /* THE GUARD `if (q < nbits)` is missing here. */
    uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 6)));
    ...
}
```

`q` is a `u32`, so `q >> 6` is a word index up to 67 108 863 and the read
reaches half a gigabyte past the blob. `c/kernel_hardened.c` is this file with
`if (q < nbits) { ... }` and nothing else, so R1-vs-R1h is what the range check
costs inside one language: **+3.00 Ir per always-taken query with clang, +2.00
with gcc** (NOTES.md 4d).

## What it measures

**1. Three bounds checks in one rung, and they do not behave the same.** All
three are against a slice length, in the same call, through the same
`#[inline(always)]` decoder; they differ only in where the index came from.

| access | index | R4 | shipped R3 | tax | cheapest in-contract safe |
|---|---|---:|---:|---:|---:|
| popcount pass | `ws + 8*i`, linear | 23.00 | 42.00 | +19.00 | **0.00000** |
| query array | `qs + 4*k`, linear | 15.00 | 26.00 | +11.00 | **−3.00000** |
| bitset word | `ws + 8*(q>>6)`, **through a shift** | 11.00 | 56.00 | **+45.00** | **+4.00000** |

Swept over 90 blobs in three bands, pooled design **rank 4/4** (every band alone
is rank 2/4), max residual 0.22. The popcount pass is the pattern's own negative
control: same array, same decoder, same fold, linear index.

**2. p03's seeding control does not transplant — and p09 says where the boundary
is.** Handing LLVM the fact at the **word index**, exactly what the proof proves,
changes nothing (`m_clamp`: +461 *dearer*), in Rust **and in C**. Handing it at
the **byte offset** deletes 49% of the kernel (`m_clampb`: 20448 → 10444, `n_fn`
291 → 218). The inference that fails is the composition through the multiply and
the length check, not the shift. The negative control `m_clampb_far` — a dead
test that says nothing — is **byte-identical to shipped R3**.

**3. Two one-character bugs, and only one is a memory error** — but not the two
the task file predicted, and the correction is measured (NOTES.md 6):

| bug | in bounds? | costs | caught by |
|---|---|---|---|
| `q & 31` for `q & 63` | yes | **+2153 Ir/call on R4** (+32%), 0 on R3 | the functional `ensures` **only**, and not even that if the specification is written from the same misunderstanding (`20 verified, 0 errors`) |
| `q >> 5` for `q >> 6` | **no** — `q/32 ≥ q/64` | **0.00** everywhere | R5's accessor **precondition**, with the functional spec deleted. Silent in every rung and under ASan on every shipped input |

**4. The intrinsic.** `__builtin_popcountll` (clang) and `u64::count_ones()`
(rustc) lower to the *same* 23-instruction SWAR body and cost the same 22.97 /
22.99 Ir per word — a null. gcc calls `__popcountdi2` and pays **+29.00 per
word**, which is a library difference and is kept out of every safety number. No
rung emits `popcnt`: this repo sets no `-march`.

## The ladder, `-O3 isolated`, marginal Ir per call

| rung | small | large | vs R4 |
|---|---:|---:|---|
| c-gcc / c-gcc-h | 12734.72 / 13212.72 | 47257.72 / 48917.72 | check = +478 / +1660 |
| c-clang / c-clang-h | 5033.72 / 5750.72 | 18723.72 / 21213.72 | check = +717 / +2490 |
| **R2 safe-naive** | 16628.30 | 60928.30 | +9936 / +36409 |
| **R3 safe-tuned** | 20448.30 | 73404.30 | **+13756 / +48885** |
| R4 unsafe / R5 verus | 6692.30 / 6691.30 | 24519.30 / 24518.30 | 0 / −1.00 (the driver's `println`) |

⚠ **R3 is dearer than R2 here** — the first time in this project. The reslice
buys both linear accesses and loses the derived one; NOTES.md 4c has the
mechanism. Read the table with NOTES.md 4, never alone.

Wall clock (min of 30, interleaved, pinned, identical-copy floor 1.70–7.83%):
R3 is **+99.1%** on `small` and **+50.2%** on `large` against R4, where `Ir` says
+205.6% and +199.4% — same direction, **2–4× smaller in magnitude**.

## The proof

`18 verified, 0 errors`; `--cfg slb_twin` `21 verified, 0 errors`. R4 and R5 are
byte-identical at `-O3` (`md5_fn e17e2e05cac7`).

The headline obligation, `q < nbits ⟹ q >> 6 < nwords`, costs **three ghost
lines** and no `nonlinear_arith`. **The specification is written in division and
the code in shifts on purpose**, so "the shift implements the division" is a real
obligation rather than a transliteration — which is what makes the two bug
mutants fail for semantic reasons.

**TCB: 12 lines across 4 items, one of them `unsafe`.** The interesting one is
`popcount64`, which is *safe*: it is trusted because vstd ships no specification
for `u64::count_ones`. p09 is the first pattern here whose trusted item models a
**CPU instruction** rather than a memory operation.
