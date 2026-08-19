# p09 — bitset: notes, measurements and proof record

Everything here was measured on this box with the commands quoted. Where a
number is an interpolation rather than a sweep it says so. `spec.md` is the
contract; this file is the evidence.

---

## 0. What p09 is for, in one paragraph

The safety check is **not a bounds check**. The guard is `q < nbits` — a range
check on a *value* — and the access is `words[q >> 6]`, an index. The fact the
access needs is `q >> 6 < nwords`, derived from the guard **through a shift**,
and neither the guard's operand nor the array's length appears in it. That is
p05's question on a different operator, and the third data point after p03
showed the same class of failure is not Rust-specific. The pattern carries its
own **negative control**: the popcount pass reads the same array, with the same
byte-at-a-time decoder, into the same fold, through an index linear in its own
loop counter.

And it carries **two one-character bugs**. Only one of them is a memory error,
and — §6 — **it is not the one the task file predicted**.

---

## 1a. PHASE 0, BEFORE ANY RUNG: `q >> 6` vs `q / 64` compile identically

`.tasks/TASK_038.md` asked whether the two spellings differ to LLVM, and said
that if they do not, the `forbidden` entry pins nothing and must say so.
**They do not.** Probe: `.temp/p09/probe/shiftlib.rs` (rustc, `--crate-type=lib
--emit=obj`), `.temp/p09/probe/shiftlib.c` (clang 22.1.6 and gcc 13.3.0), hashed
per function by `.temp/p09/probe/cmpfns.py`.

```
shiftlib.o        k_shift    n=17  md5_txt=7e5539cfc95a
shiftlib.o        k_div      n=17  md5_txt=7e5539cfc95a    <- identical
shiftlib.o        k_mixed    n=17  md5_txt=7e5539cfc95a    <- identical
shiftlib.o        k_shift32  n=17  md5_txt=4830590744e6
shiftlib.o        k_div32    n=17  md5_txt=4830590744e6    <- identical
shiftlib.o        b_shift    n=40  md5_txt=d436d40ebc35    (byte-addressed)
shiftlib.o        b_div      n=40  md5_txt=d436d40ebc35    <- identical
shiftlib.o        u_div      n=11  -- u_shift is ABSENT from the symbol table,
                                      identical-code-folded into u_div
shiftlib_clang.o  c_shift / c_div      n=11  1426f0587e30 both
shiftlib_clang.o  c_shift32 / c_div32  n=11  734161f3f241 both
shiftlib_gcc.o    c_shift / c_div      n=13  b8afa59c1fd3 both
shiftlib_gcc.o    c_shift32 / c_div32  n=13  b2b123da9864 both
```

Three compilers, `usize` and `u32`, checked and unchecked, direct-`&[u64]` and
byte-addressed: **`q >> 6` ≡ `q / 64` and `q & 63` ≡ `q % 64`, instruction for
instruction.** So p09's `forbidden` entry on `/ 64` **moves no number**, exactly
as p17's excluded spelling compiles to the same 478 bytes as an admissible one
(`.memory/01-ladder.md`). What it does buy is on the **proof** side: `verus.rs`
writes the specification in division and the exec code in shifts, so "the shift
implements the division" is a real obligation (§5) that a rung spelling the exec
side `q / 64` would not have. **A pin whose entire effect is on proof burden and
none of it on instructions is a new shape for this project.**

**A methodological trap, recorded because it invalidated the first attempt.**
The probe was first built as a *binary* whose `main` called each
`#[inline(never)]` function with `q = 1`. rustc constant-propagated **into** the
callees (`cmp $0x2,%edx`, `shr $1`) and every function collapsed to the same 15
instructions — a spurious "identical". `#[inline(never)]` does not stop
interprocedural argument propagation. Build the probe as `--crate-type=lib
--emit=obj`.

Two side observations from the same listings, both load-bearing later:

- `(w >> (q & 63)) & 1` lowers to `bt %rcx,%rdx ; setb`. The hardware masks the
  shift amount mod 64, so **`q & 63` costs zero instructions** — which is why
  `q & 31` cannot be free (§6).
- The byte-addressed probe emits **eight separate bounds checks** for the eight
  bytes of one byte-assembled `u64`, `lea; cmp; jae` each. Nothing merged them.

---

## 1. Does anything unroll or vectorise? No.

`vector_regs` is empty on all eight `-O3 isolated` kernels (`harness/asm.py`),
and no rung unrolls either loop: the query loop's body appears once per rung and
the popcount pass's once. The query loop cannot be unrolled usefully — it is a
data-dependent branch on an attacker word followed by a serial Horner chain
through `acc`. `harness/check.py` reports `loop yes` and `vec -` for all 32
cells.

---

## 2. Which `Ir` column to quote, and why p09 is p11's case

**Quote `marginal_ir_per_call`** (whole-program, `n_iters` 100 → 200) for
anything involving a **gcc** cell, and either column for the rest.

`results/p09-bitset.json` records kernel-exclusive `Ir` like every pattern
(`.memory/03-measurement.md`: it is `measure.py`'s hardcoded protocol). p09 is
a fresh instance of the family p02's `memcpy`, p08's `rep`-strings and p11's
`strlen` established — the column cannot see work that leaves the symbol — and
here the routine has a name:

| cell | kernel-exclusive / call | marginal / call | difference |
|---|---:|---:|---:|
| c-gcc `small` | 12341.00 | 12734.72 | **+393.72** |
| c-gcc-h `small` | 12819.00 | 13212.72 | **+393.72** |
| c-clang `small` | 5019.00 | 5033.72 | +14.72 |
| unsafe `small` | 6678.00 | 6692.30 | +14.30 |

The `+393.72` on the gcc cells is `18 nwords × ~21 Ir` of **`__popcountdi2`**,
which gcc calls and which lives in libgcc, outside the `kernel` symbol (§3d).
The `+14.72 / +14.30` are the per-rung driver offsets `.memory/03-measurement.md`
already tabulates. So a gcc-vs-anything ratio read off the kernel-exclusive
column understates gcc by 3.1%.

---

## 3. The rungs, `-O3 isolated`, per call

Static, `nm --print-size` extent (`n_fn` / padding-excluded):

| rung | `n_fn` | pad-excl | bytes |
|---|---:|---:|---:|
| c-gcc (R1) | 164 | 160 | 596 |
| c-gcc-h (R1h) | 166 | 162 | 596 |
| c-clang (R1) | 110 | 108 | 398 |
| c-clang-h (R1h) | 114 | 112 | 398 |
| safe_naive (R2) | 293 | 291 | 1280 |
| safe_tuned (R3) | 291 | 290 | 1230 |
| **unsafe (R4)** | **102** | **100** | **367** |
| **verus (R5)** | **102** | **100** | **367** |

Marginal `Ir` per call:

| rung | `small` | `large` | vs R4 `small` | vs R4 `large` |
|---|---:|---:|---:|---:|
| c-gcc | 12734.72 | 47257.72 | +6042.42 | +22738.42 |
| c-gcc-h | 13212.72 | 48917.72 | +6520.42 | +24398.42 |
| c-clang | 5033.72 | 18723.72 | −1658.58 | −5795.58 |
| c-clang-h | 5750.72 | 21213.72 | −941.58 | −3305.58 |
| **R2 safe_naive** | **16628.30** | **60928.30** | **+9936.00** | **+36409.00** |
| **R3 safe_tuned** | **20448.30** | **73404.30** | **+13756.00** | **+48885.00** |
| R4 unsafe | 6692.30 | 24519.30 | 0 | 0 |
| R5 verus | 6691.30 | 24518.30 | −1.00 | −1.00 |

`R5 − R4 = −1.00` is the driver's `println` term, not the kernel's: the two
kernels are **byte-identical** (§3b). `.memory/03-measurement.md` records the
same −1.00 on p16.

⚠ **R3 IS DEARER THAN R2 ON THIS PATTERN — the first time in this project.**
20448 against 16628 on `small`, 73404 against 60928 on `large`. The reslice is
not a pessimisation and R2 is not a strawman; §4 decomposes it and §4c gives the
mechanism. Do not read the table above without §4.

### 3b. R4 ≡ R5, byte for byte

| pair | opt | `md5_fn` | `md5_fn_norel` | `md5_raw` | counts |
|---|---|---|---|---|---|
| unsafe vs verus | O3 | **equal** `e17e2e05cac7` | equal | **equal** `efa75ba5` | 102/100 both |
| unsafe vs verus | O0 | differ | **equal** `8f56814121e6` | differ | 443/443 both |

The `O0` row is link layout — the crate names differ in length, so the `call`
displacements do (`.memory/03-measurement.md`). Finding 1 reproduces on the
**tenth** pattern, and this is the first time it covers a kernel whose erased
ghost material includes **two bridge lemmas** rather than only invariants.

### 3c. The C rungs are not comparable to each other without naming the routine

`c-gcc` is 2.53× `c-clang` on `small` (12734.72 vs 5033.72). **That is not a
compiler-quality result**; §3d shows most of it is one library call.

### 3d. THE INTRINSIC: `__builtin_popcountll` vs `u64::count_ones()`

`.tasks/TASK_038.md` asked for the emitted instruction per rung and whether this
box's default `-march` implies `-mpopcnt`. Measured on the disassembly:

| rung | popcount lowering | per-word cost (§4) |
|---|---|---:|
| c-gcc, c-gcc-h | **`call __popcountdi2`** (libgcc) | **51.97** |
| c-clang, c-clang-h | inline SWAR, 23 insns, no call | **22.97** |
| safe_naive, safe_tuned, unsafe, verus | inline SWAR, 23 insns, no call | 55.0 / 42.0 / **22.99** |

- **No rung emits a `popcnt` instruction.** This repo sets no `-march`, so the
  baseline x86-64 ISA has none. Probes (not built by the repo): `clang -mpopcnt`
  emits exactly **1** `popcnt`, and `rustc -C target-feature=+popcnt` emits
  exactly **1**.
- **The intrinsic comparison is a NULL at matched backend.** clang's
  `__builtin_popcountll` and rustc's `u64::count_ones()` lower to the *same*
  23-instruction SWAR body and cost the *same* 22.97 / 22.99 Ir per word. There
  is no Rust-vs-C intrinsic difference here to report.
- **The gcc-vs-clang difference is entirely the library.** `+29.00` Ir per word
  is `__popcountdi2`, and by `.memory/03-measurement.md`'s p11 rule it must be
  named beside every rate and never differenced against a safety number. Note
  the direction: gcc's *default* is a call, not a codegen limit — the same
  family as p16's and p17's `-funroll-loops` finding.

**So p09's three factors, separated (p11's decomposition on a new kernel):**

| factor | what it compares | size |
|---|---|---:|
| **library** | `__popcountdi2` (gcc) vs inline SWAR (clang, rustc) | **+29.00 Ir/word** |
| **spelling** | shipped R3 vs `r3_best`, both in contract, both safe | **+13493 Ir/call** on `small` |
| **safety** | checked vs unchecked at matched spelling | **§4** |

Only the third is a safety number.

---

## 4. THE MEASUREMENT: three checks, three answers, one kernel

### 4a. The design, and its rank

`inputs/gen.py --sweep` ships **90 blobs in three bands** and
`.temp/p09/sweep.py` measures marginal `Ir` per call on each. The model is

```
Ir/call = const + a·nq + b·xguard + c·nwords
```

where `xguard` is the number of queries that take the guard. ⚠ **Every band on
its own is rank 2 of 4** — band N holds `nwords` fixed and locks `xguard` to
`nq`, band D holds `nq` and `nwords`, band W holds `nq` and `xguard`. **Only the
pooled design is rank 4**, and `.memory/01-ladder.md` records that a per-band fit
can return garbage at zero residual, so the rank is reported before any
coefficient:

```
band n: 64 blobs, rank 2/4   nq 8..71   xguard 8..71   nwords 8..8
band d: 13 blobs, rank 2/4   nq 240     xguard 0..240  nwords 8..8
band w: 13 blobs, rank 2/4   nq 120     xguard 120     nwords 3..27
POOLED: 90 blobs, rank 4/4
```

Fitted coefficients (`.temp/p09/fit.py`; max residual **0.2202** over 90 blobs
for the Rust cells, **0.8888** for the C ones, which is the `println!` digit term
`.memory/03-measurement.md` prices at 0.2263 Ir/call/digit):

| cell | const | **/query** | **/guarded query** | **/word** |
|---|---:|---:|---:|---:|
| c-gcc (R1) | 87.24 | 49.00 | **0.00** | 51.97 |
| c-gcc-h (R1h) | 87.24 | 16.00 | 35.00 | 51.97 |
| c-clang (R1) | 78.24 | 19.00 | **0.00** | 22.97 |
| c-clang-h (R1h) | 78.24 | 12.00 | 10.00 | 22.97 |
| R2 safe_naive | 103.08 | 31.00 | 34.00 | 55.00 |
| R3 safe_tuned | 94.08 | 26.00 | 56.00 | 42.00 |
| **R4 unsafe** | **64.08** | **15.00** | **11.00** | **23.00** |
| R5 verus | 63.08 | 15.00 | 11.00 | 23.00 |

R1's `/guarded` is **0.00** because R1 has no guard — its work does not depend on
how many queries are in range. That is the arithmetic statement of the bug.

The R4 coefficients are **exact from the disassembly**, not fitted
(`.memory/01-ladder.md`: a five-decimal rate must come from `body/K`): R4's query
loop is 15 instructions on the not-guarded path and 26 on the guarded one
(`.temp/p09/loops.py unsafe`), so `15.00000` per query and `26 − 15 = 11.00000`
extra per guarded query; the popcount loop body is 23 instructions per word, so
`23.00000`. The fit reproduces all three to 0.0001.

### 4b. THE THREE CHECKS DO NOT BEHAVE THE SAME, and that is the result

All three are bounds checks against a slice length, in the same rung, in the same
call, on the same buffer, through the same `#[inline(always)] load_u32`/
`load_u64`. They differ only in where the index came from.

| access | index | R4 | shipped R3 | tax | cheapest in-contract safe |
|---|---|---:|---:|---:|---:|
| popcount pass | `ws + 8*i`, **linear in the loop counter** | 23.00 | 42.00 | +19.00 | **23.00** → **0.00000** |
| query array | `qs + 4*k`, **linear in the loop counter** | 15.00 | 26.00 | +11.00 | **12.00** → **−3.00000** |
| bitset word | `ws + 8*(q>>6)`, **derived through a shift** | 11.00 | 56.00 | **+45.00** | **15.00** → **+4.00000** |

- **On a linear index the safety tax is 0.00000 per word**, and on the query
  array it is **−3.00000**: the in-contract `chunks_exact(4)` spelling is
  *cheaper than the unsafe rung*, because it hands the optimiser the length that
  `get_unchecked` never needed to know.
- **On the shift-derived index the shipped tax is +45.00000 per guarded query**,
  and the cheapest in-contract safe spelling still pays **+4.00000**.

That is the pattern's headline and it is a matched-spelling difference, per
regressor, over 90 blobs at rank 4, with max residual 0.22.

### 4c. Why the shipped R3 is dearer than the shipped R2 — mechanism

Per term, R3 beats R2 on both linear accesses (26 vs 31 per query; 42 vs 55 per
word) and loses badly on the derived one (56 vs 34). Since `small` and `large`
are 100% guarded, the query and guarded terms add, and 26+56 = 82 loses to
31+34 = 65.

On the listing (`.temp/p09/loops.py`), the difference on the guarded path is that
**R3's reslice lets LLVM hoist the eight byte-address computations above the
eight bounds checks**, which needs eight simultaneously-live registers; R3's
query loop body is 82 instructions and contains a stack reload
(`mov 0x8(%rsp),%r9`), where R2 recomputes each address from one base
(`movzbl -0x2(%r13,%r12,1)`) inside a 65-instruction body. A full
register-allocation attribution was not done; what is measured is the +22.00 per
guarded query and the spill in the listing.

**And in both safe rungs the surviving per-byte check on the derived index costs
more than the check.** LLVM merges the eight byte loads of a little-endian `u64`
into ONE `mov` — it does so in R4's query loop (`mov (%rdi,%r15,1),%r15`), in
R4's popcount pass, and **in R3's popcount pass** (`mov -0x7(%rbx,%rdi,1),%r13`).
It does **not** do so on the shift-derived access in either safe rung, where the
22-instruction `movzbl`/`shl`/`or` chain survives. So the cost of the surviving
check is 8 compares **plus** a lost load idiom — p02's mechanism
(`.memory/01-ladder.md`: "rustc failed to idiom-recognise one spelling") arriving
on a *safety* axis rather than a spelling axis.

### 4d. R1 vs R1h — what the range check costs inside one language

| pair | law | at 100% guarded (`small`, `large`) |
|---|---|---|
| `c-clang-h − c-clang` | `−7.00·nq + 10.00·xguard` | **+3.00 per query** |
| `c-gcc-h − c-gcc` | `−33.00·nq + 35.00·xguard` | **+2.00 per query** |

The check is **+3.00 (clang) / +2.00 (gcc) Ir per always-taken query**, and
**negative** when the guard rejects — it skips a word load. Both C rungs' `/word`
terms are equal to 0.004, so the popcount pass is untouched by the check, which
is the control working.

⚠ **Both C rungs are CHEAPER than R4 on both blobs** (`c-clang` −1658.58 /
−5795.58, `c-clang-h` −941.58 / −3305.58). That is not "C beats unsafe Rust": it
is `/query` 19 vs 15 and `/guarded` 0 vs 11 for R1 — R1 *does less work*, because
it has no guard — plus clang's scale-8 addressing against rustc's byte
addressing, which is `.memory/01-ladder.md`'s p01 finding reproduced. `c-clang-h`
against R4 is the honest C-vs-Rust pair and it is `/query` 12 vs 15,
`/guarded` 10 vs 11, `/word` 22.97 vs 22.99 — i.e. **clang's hardened C and
unsafe Rust are within 0.02 Ir per word and within 3 per query, on the same
backend.**

### 4e. Wall clock

`.memory/03-measurement.md`'s protocol, and the **identical-copy floor first**
(`common/layout/order.py --pattern p09-bitset --copies 15 --reps 15`, two passes,
alternating and blocked):

| pass | protocol | noise floor (byte-identical copies) |
|---|---|---|
| 0 | alternating | 4.92 … 7.83% |
| 1 | alternating | 1.70 … 2.12% |
| 0 | blocked | 1.33 … **17.52%** |
| 1 | blocked | 1.84 … **13.43%** |

**Under the alternating protocol the floor is 1.70–7.83%**, i.e. inside the 10%
rule; the blocked runs trip it and show the classic monotone ramp
(`unsafe` 5.37 → 6.31 ms across the block), which is TASK_031's artefact
reproduced on a ninth pattern.

`harness/measure.py p09 --reps 30 --cpu 3`, `-O3 isolated`, min of 30:

| rung | `small` min | vs R4 | `large` min | vs R4 |
|---|---:|---:|---:|---:|
| unsafe | 5.36 ms | — | 9.41 ms | — |
| verus | 5.40 ms | +0.75% | 9.31 ms | −1.06% |
| safe_naive | 8.47 ms | +58.0% | 11.90 ms | +26.5% |
| safe_tuned | 10.67 ms | +99.1% | 14.13 ms | +50.2% |
| c-clang | 4.66 ms | −13.1% | 8.70 ms | −7.5% |
| c-clang-h | 4.86 ms | −9.3% | 8.81 ms | −6.4% |
| c-gcc-h | 9.65 ms | +80.0% | 12.77 ms | +35.7% |

**The column is resolvable**: the effects (26–99%) are an order of magnitude
above the floor (≤7.8%), and R5-vs-R4 (+0.75% / −1.06%) sits inside it, which is
what byte-identical kernels must do. 2 of 32 cells tripped the 10% rule and are
marked ✗ in `results/tables/p09-bitset.md`; **both are `whole` mode on `small`
and no claim here rests on them.**

⚠ **`Ir` and wall clock agree in direction and disagree in magnitude by 2–4×.**
R3-vs-R4 is +205.6% on `Ir` and +99.1% on ns at `small`; +199.4% and +50.2% at
`large`. The extra instructions are predictable compare-and-branch with high ILP,
so they retire far cheaper than the average instruction. **Quote both columns.**
No cycles figure is quoted: `.memory/00-environment.md` records that this box's
clock is set by other tenants and that ns is a measurement while cycles is an
inference.

---

## 5. The proof

`./verus_run.py patterns/p09-bitset/verus.rs` → **`18 verified, 0 errors`**, and
`--cfg slb_twin` → **`21 verified, 0 errors`**. The one-session budget was not
exhausted; the whole file verified on its first full assembly after two staged
probes (`.temp/p09/probe/v0.rs`, `v1.rs`).

### 5a. The obligation the pattern is about, and what it cost

```rust
pub proof fn lemma_shr6_is_div64(x: u64)
    ensures (x >> 6) == x as int / 64,
{ assert(pow2(6) == 64) by { lemma2_to64(); } }

pub proof fn lemma_guard_bounds_word(q: u64, nbits: u64)
    requires q < nbits,
    ensures  (q >> 6) == word_of(q),
             (q >> 6) < nwords_of(nbits),
{ lemma_shr6_is_div64(q); }
```

with `broadcast use vstd::bits::lemma_u64_shr_is_div;` at file scope. **Three
ghost lines, no `nonlinear_arith`, no new trusted item, and Z3 takes it first
try.** The mask needs one more, because vstd's `lemma_u64_low_bits_mask_is_mod`
is broadcast with trigger `x & (low_bits_mask(n) as u64)` and nothing makes Z3
read the literal `63` as `low_bits_mask(6)`:

```rust
pub proof fn lemma_and63_is_mod64(q: u64)
    ensures (q & 63) == q % 64, (q & 63) == bit_of(q), (q & 63) < 64,
{ assert(low_bits_mask(6) == 0x3f) by { lemma_low_bits_mask_values(); }
  assert(pow2(6) == 64) by { lemma2_to64(); }
  vstd::bits::lemma_u64_low_bits_mask_is_mod(q, 6); }
```

**So the proof side of "the bound is derived through a shift" is cheap and the
codegen side is not.** That is p05's and p03's sentence on a third operator, and
§4b is the size of the gap.

### 5c. Two things that cost real time, recorded so nobody re-derives them

1. **The query loop blew the solver's rlimit** with `u32_at`/`u64_at` transparent
   — `error: while loop: Resource limit (rlimit) exceeded`, and `--profile`
   showed only 4–5 quantifier instantiations, so it was arithmetic and not a
   trigger loop. `#[verifier::opaque]` on the two byte decoders plus `reveal()`
   inside `load_u32`/`load_u64` fixed it outright. An eight-term LE decode with
   coefficients up to 7.2e16 is expensive to carry through a relational loop
   invariant; hide it.
2. **`broadcast use` at FILE scope is not free.** With
   `lemma_u128_shr_is_div` and `lemma_mul_inequality` broadcast at file scope
   (p03's arrangement), the kernel's query loop hit the rlimit even after (1).
   They are the *driver's* lemmas; moving them into `proof { broadcast use ... }`
   blocks **inside the driver's loop body** fixed the kernel and kept the driver.
   Note the intermediate state that misled: `broadcast use` inside `fn main`'s
   body did **not** reach the loop-body queries.
3. `popcnt(x) <= 64` is **not** provable by the obvious induction (it needs the
   bit width as a parameter). `popcnt(x) <= x` is, in two lines, and is all the
   twin needs to rule out its counter overflowing.

### 5b. TCB tally — 4 trusted items, ONE of them `unsafe`

`TCB: 12 lines across 4 items.`

| item | `unsafe`? | lines | why trusted | twin |
|---|---|---:|---|---|
| `buf_get_unchecked` | **yes** | 3 | vstd ships no spec for `<[T]>::get_unchecked` | `slb_twin_buf_get_unchecked` |
| `popcount64` | **no** | 3 | vstd ships no spec for `u64::count_ones` | `slb_twin_popcount64` |
| `load_input` | no | 4 | file I/O and argv | — (no `ensures`, no `unsafe`) |
| `emit` | no | 2 | `println!` | — |

**p09 is the first pattern in this project whose trusted item models a CPU
INSTRUCTION rather than a memory operation.** p08's `copy_in` is the precedent
for a trusted item with no `unsafe` (`.memory/04-verus.md`: "trusted means
unchecked by the verifier, not unsafe"), but that one wraps a memory move. Grep
of `vstd/std_specs/bits.rs` finds `trailing_zeros` and `leading_zeros` and
nothing else, so `count_ones` has to be axiomatised or hand-written; a
hand-written SWAR fold would have deleted the intrinsic comparison §3d exists
for.

The gate's stage-5a message for `popcount64` ("it is therefore an axiom that the
unchecked operation is always defined") is written for the memory case and is
answered in `spec.md`'s `verus.unsafe_justifications`: this item has no
parameter a caller could usefully be constrained on, so any `requires` would be
a tautology — the shape `.memory/04-verus.md` warns reads as strength and is
not. What guards it is the twin.

SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) **Is the twin's body the right checked stand-in?** Yes, and it is the same
one p01, p02, p03, p05, p07, p11, p16 and p17 ship: `v[i]` is exactly
`*v.get_unchecked(i)` with the bound check restored, so a `requires` too weak to
license the unchecked read is too weak to license the checked one, and Verus can
see the second. Nothing else in the twin can satisfy the `ensures`
`r == v@[i as int]` without performing the read. (b) **Is the `ensures` complete
with respect to every unchecked operation the body performs?** The body performs
exactly one unchecked operation, a single-byte read at `i`, and the `ensures`
constrains exactly that byte's value; there is no second index, no write, no
length change and no aliasing. This is the blind spot `.memory/04-verus.md`
records — a body that also read `i + 1` would pass the contract pin, the twin
and the `--cfg slb_twin` run unchanged — and the only backstop is Miri on R4,
which is mandatory here and clean on all five inputs (§7). p09 raises the stakes
on (b) relative to earlier patterns, because its unchecked index is `q >> 6`, a
function of an attacker word two operators away from the guard: an off-by-one in
the derivation would show up only on queries near a word boundary rather than as
a fixed shift, which is why `adversarial-edge.bin` is built to sit exactly there.
(c) **Does each clause mean the same thing in both configurations?** Yes: the
contract is one `requires` and one `ensures` over `v` and `i` with no constant,
no `cfg`-varying term and no macro; the token `slb_twin` appears in this file
only inside the twins' own `#[cfg(slb_twin)]` attributes, which the gate checks
before any Verus call.

SLB-TRUSTED-ARGUMENT verus.rs popcount64

(a) **Is the twin's body the right checked stand-in?** The unchecked operation
here is not a memory access but an *unspecified* one: `u64::count_ones()` has no
vstd specification, so the axiom introduced is "it returns the population
count". The twin is written with `/ 2` and `% 2` — the same operations the spec
function `popcnt` recurses on — so it is a direct implementation of the claim
rather than a second bit-twiddling program that would need its own bridge, and it
verifies against the *identical* `ensures`. That is the strongest available
stand-in: it demonstrates the axiom is *satisfiable by a checked program*, which
is what a twin can show and all it can show. (b) **Is the `ensures` complete with
respect to every operation the body performs?** Yes, and this item is unusually
easy to judge on that question: the body is a single total function call on a
by-value `u64` returning a `u32` widened to `u64`. There is no memory operand, no
index, no length, no lifetime and no side effect, so there is no operation the
`ensures` could fail to mention — the completeness risk `.memory/04-verus.md`
describes (a body that also reads `i + 1`) has no analogue. What remains is
whether the axiom is *true*: `u64::count_ones` is documented to return the number
of set bits and `popcnt` is defined as the base-2 digit sum, and those are the
same function; `lemma_popcnt_le` and `lemma_popcnt_pos` are proved about
`popcnt` and used only by the twin. (c) **Does each clause mean the same thing in
both configurations?** Yes: the single `ensures` is `r == popcnt(x)` in both, and
`popcnt` is a `pub open spec fn` with no `cfg`-varying constant anywhere in its
definition. `#[cfg(slb_twin)]` gates the twin item and nothing else; the twin's
extra obligation count (2, one for the body and one for its loop) is pinned in
`spec.md` so a twin that quietly lost its body would fail the count rather than
pass silently.

### 5d. Obligation decomposition (measured, not derived from the rule of thumb)

`./verus_run.py verus.rs --verify-function <name> --verify-root`:

```
popcnt 1   wrun 1   qrun 1                       (the three RECURSIVE spec fns)
lemma_and63_is_mod64 1   lemma_shr6_is_div64 1
lemma_guard_bounds_word 1   lemma_popcnt_le 1   lemma_popcnt_pos 1
load_u32 1   load_u64 1
kernel 3    (body + TWO loop bodies)
main 5
--------------------------------------------------- 18
u32_at / u64_at / nwords_of / word_of / bit_of / bitset_fold  0  (non-recursive spec fns)
buf_get_unchecked / popcount64 / load_input / emit            0  (external_body)
```

`.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule predicts
**15** and Verus reports 18; the three extra are the recursive spec functions'
termination queries. `main`'s 5 is quoted as measured — the by-block rule would
predict 6 — the identical off-by-one p03, p05, p07, p11 and p17 record for the
identical driver. **Five proof fns is the largest lemma count of any kernel in
this project**, and every one of them is arithmetic about `>>` and `&`; the
kernel has **zero nonlinear arithmetic**.

Twin: 21 = 18 + `slb_twin_buf_get_unchecked` 1 + `slb_twin_popcount64` **2**.
p09 is the first pattern whose twin count moves by more than the number of
twins, because its second twin has to *implement* the trusted contract with a
loop rather than restate it with one indexed read.

---

## 6. THE TWO BUGS — and the task file's premise about `q >> 5` is measured FALSE

`.tasks/TASK_038.md` predicted "every rung catches the first, no rung catches the
second, and the `ensures` catches the second only because `model.py` disagrees",
with `q >> 5` and `q & 31` as two spellings of one arithmetic bug. **They are not
the same bug and only one of them is arithmetic.**

`q >> 5` is `q / 32`, which is **larger** than `q / 64`, so under the guard
`q < nbits` it names word indices up to roughly `2·nwords` — off the end of the
bitset. It is a **second spatial bug**. `q & 31` is the genuine arithmetic one:
the index is untouched, the wrong *bit* is tested, and the answer is wrong.

### 6a. What R5 says — seven mutants, all from `controls/gen_controls.py`

| variant | exec | functional spec | Verus |
|---|---|---|---|
| control | `>>6`, `&63` | as shipped | **18 verified, 0 errors** |
| control, ms-only | `>>6`, `&63` | **stripped** | **18 verified, 0 errors** ← positive control: the probe is not blind |
| `m_shift5` | `q >> 5` | as shipped | 17 verified, **1 errors** — *possible arithmetic underflow/overflow* on the index |
| **`m_shift5_msonly`** | `q >> 5` | **stripped** | 17 verified, **1 errors** — ***precondition not satisfied***. **Memory safety alone catches it.** |
| `m_shift5_spec` | `q >> 5` | `word_of = /32` | 16 verified, **2 errors** — moving the spec does not help |
| `m_mask31_fixshift` | `q & 31` | as shipped | 18 verified, **1 errors** — *invariant not satisfied*, **functional only** |
| **`m_mask31_msonly`** | `q & 31` | **stripped** | **19 verified, 0 errors** — **invisible to memory safety** |
| **`m_mask31_spec`** | `q & 31` | `bit_of = %32` | **20 verified, 0 errors** — **invisible entirely** |

`.memory/04-verus.md` requires the positive control and it is row 2: stripping
the functional spec does not blind the probe. All seven rows are regenerated by
the committed `controls/gen_controls.py` (which asserts its own substitution hit
counts off the shipped `verus.rs`) and re-verified from that generator: the
counts above are the second, reproduced run, not the exploratory one. The two
that carry the result, in full:

```
$ ./verus_run.py .temp/p09/controls/m_shift5_msonly.rs --multiple-errors 20
error: precondition not satisfied        <- the ACCESSOR's, with no functional spec
error: possible arithmetic underflow/overflow
verification results:: 17 verified, 1 errors

$ ./verus_run.py .temp/p09/controls/m_mask31_fixshift.rs --multiple-errors 20
error: invariant not satisfied at end of loop body    <- and nothing else
verification results:: 18 verified, 1 errors
```

⚠ **Honest caveat.** `q & 31` without help also fails a *second*,
non-substantive obligation — `possible bit shift underflow/overflow` on
`1u64 << (q & 31)` — because the supporting lemma names the constant 63 and
nothing then proves `(q & 31) < 64`. `m_mask31_fixshift` supplies
`assert((q & 31) < 64) by (bit_vector)` so the single remaining error is the
substantive one. **Quote the `fixshift` row, never the bare one.**

**So the answer to "which rungs catch which bug, and with what":**

- **The mask bug `q & 31`** is caught by **nothing** except a functional
  specification written independently of the code — and if the author's
  misunderstanding reaches the specification (`bit_of = q % 32`), R5 verifies
  cleanly. `20 verified, 0 errors` is a program proved to meet its
  specification, whose specification is the bug. **That is the manager's
  designed result and it stands.**
- **The shift bug `q >> 5`** is caught by R5 through the **accessor's
  precondition**, with the functional `ensures` deleted, and moving the
  specification to match it does not help — because the spatial obligation does
  not come from the `ensures` at all. **That is a better result than the one
  designed for, and it is the pattern's lead.**

### 6b. What everything else says — cost, sanitisers and where the bounds check is

`.temp/p09/ctlmeasure.py`, marginal Ir/call, `-O3 isolated`, and equivalence
against `model.py` on all five shipped inputs (`=` matches):

| control | `n_fn` | `small` | `large` | equiv (small/large/oob/edge/count) |
|---|---:|---:|---:|---|
| `safe_naive` | 293 | 16628.30 | 60928.30 | `=====` |
| `x_shift5_n` | 293 | 16628.00 | 60928.00 | `XXXX=` |
| `x_mask31_n` | 312 | 20455.30 | 74210.70 | `XXXX=` |
| `safe_tuned` | 291 | 20448.30 | 73404.30 | `=====` |
| `x_shift5_t` | 291 | 20448.00 | 73404.00 | `XXXX=` |
| `x_mask31_t` | 291 | 20448.30 | 73403.70 | `XXXX=` |
| `unsafe` | 102 | 6692.30 | 24519.30 | `=====` |
| `x_shift5_u` | 102 | 6692.00 | 24519.00 | `XXXX=` |
| **`x_mask31_u`** | **113** | **8845.30** | **31990.70** | `XXXX=` |

⚠ **"The same machine code shape at a different constant" is FALSE, measured.**
`q & 63` is free — the hardware masks `bt`'s shift amount mod 64 — so the wrong
constant needs a real `and`: **`x_mask31_u` costs R4 +2153.00 Ir/call on `small`
(+32.2%) and +9.00 per guarded query** (fit: `/guarded` 20.00 against 11.00).
The mask bug is free on the *safe* rungs (`x_mask31_t` is +0.00 on `small`)
because they already spend 45 instructions per guarded query that the extra
`and` hides inside. **The arithmetic bug's cost is not zero and it is not the
same on every rung.**

`q >> 5` **is** free: 0.00 on every rung, and `n_fn` unchanged on R3 and R4.

**Sanitisers, gcc `-O1 -g -fsanitize=address,undefined -static-libasan
-static-libubsan`, the gate's own flags, on `small.bin`:**

| build | exit | stdout | diagnostic |
|---|---|---|---|
| shipped `kernel_hardened.c` | 0 | `12759648911969524195` (= model) | none |
| `x_mask31.c` | 0 | `16409156155243397307` | **none** |
| `x_shift5.c` | 0 | `1713513234165324099` | **none** |

**Both bugs are silent under ASan+UBSan on the shipped inputs, and both are
wrong.** For the mask bug that is the whole point. For the shift bug it is
because the overshoot lands **inside the same allocation**: the query array
follows the word array, so `words[q >> 5]` reads query bytes. That is p17's
finding — *the language's bound is the slice it was given* — reproduced on a
pattern where the wrong index is produced by arithmetic rather than by a signed
subtraction.

**And here is the input that shows R5 was right to reject it.**
`.temp/p09/thin.py` builds `thin.bin`: `nbits = 1024` (16 words, 128 B) with only
`nq = 4` queries (16 B), so the overshoot leaves the 152-byte blob.

| build | `thin.bin` |
|---|---|
| shipped R2, R3, R4 | `5701745240651788480` = model, exit 0 |
| `x_shift5_u` (unsafe) | `6437231379592215552` — **wrong, silent, exit 0**, 112 B past the blob |
| `x_shift5_t`, `x_shift5_n` (safe) | **panic: index out of bounds** |
| `x_shift5.c` under ASan | **`heap-buffer-overflow` READ of size 1**, exit 1 |

So: **the bounds check and the sanitiser catch `q >> 5` on an input nobody would
think to write, and never on the five shipped ones; the proof catches it on
every input, because its obligation is universally quantified.** `thin.bin` is a
`.temp/` probe with a committed generator rather than a matrix input, because no
*shipped* rung behaves differently on it.

---

## 7. Adversarial behaviour, per rung

| input | R1 (c-gcc/c-clang) | R1h | R2 | R3 | R4 | R5 | model | ASan |
|---|---|---|---|---|---|---|---|---|
| `adversarial-count` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | clean |
| `adversarial-oob` | **SEGV** | 12484296500425563648 | ✓ | ✓ | ✓ | ✓ | 12484296500425563648 | **fires** |
| `adversarial-edge` | **wrong answer, exit 0** | 14961857398943250048 | ✓ | ✓ | ✓ | ✓ | 14961857398943250048 | **clean** |
| `small`, `large` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | clean |

The gate's own line for the firing row:

```
ok  adversarial-oob.bin  sanitizer fired as declared (exit=1):
    AddressSanitizer:DEADLYSIGNAL ... ERROR: AddressSanitizer: SEGV on unknown address
```

**`adversarial-edge` is the sharper row and it is why `model.py` derives
`sanitizer_expect` from "does R1 leave the blob" rather than from "does R1
disagree".** Its queries are 99, 100, 127 and 128 against `nbits = 100`,
`nwords = 2`: R1 reads words 1, 1, 1 and 2, and word 2 is one past the bitset but
**inside the same allocation**, because the query array follows it. R1 returns a
different answer with no diagnostic from any sanitiser. p09 is the first pattern
here that ships an input on which "R1 is wrong" and "ASan fires" come apart, and
`model.py`'s predicate is written for that.

`adversarial-count` is the control: `nq = 4096` against a window holding 20, so
`8*nwords + 4*nq = 16400 > avail = 96` and the length check — which **is** in R1
— rejects in every rung. It is the row that shows the missing check is the range
one and not the length one.

---

## 8. THE SEEDING EXPERIMENT — p03's control transplanted, and it does NOT reproduce

p03 (`.memory/01-ladder.md` finding 10) measured that LLVM keeps a provably-dead
bounds check because it cannot find the invariant **unseeded**, and that handing
it the fact as a dead test deletes the check outright — in Rust *and* in C.
p09 asks the same question about a bound derived through `>>`.

`controls/gen_controls.py`, all in contract by `check.py::spelling_matches`
(`.temp/p09/ctlpins.py`), all `=====` equivalent to `model.py` on all five inputs:

| control | what it hands LLVM | `n_fn` | `small` | vs shipped R3 | `/guarded` |
|---|---|---:|---:|---:|---:|
| R3 shipped | — | 291 | 20448.30 | — | 56.00 |
| `m_clamp` | dead `if (q >> 6) >= nwords` — **the WORD INDEX**, p03's shape | 294 | 20909.30 | **+461 DEARER** | 58.00 |
| `m_clamp_hi` | ...`> nwords`, one past | 294 | 20909.30 | +461 | — |
| `m_clamp_far` | ...`>= 0x1000000`, true but useless | 295 | 21148.30 | +700 | — |
| **`m_clampb`** | dead `if ws + (8*(q>>6)) as usize + 8 > len` — **the BYTE OFFSET** | **218** | **10444.30** | **−10004** | **14.00** |
| `m_clampb_lo` | ...`+ 7`, one byte short | 221 | 10443.30 | −10005 | 14.00 |
| `m_clampb_far` | ...`> 0x7fffffff`, true but useless | **291** | **20448.30** | **0** | 56.00 |

**Three results, and the middle one is the finding:**

1. **`m_clampb_far` is BYTE-IDENTICAL to shipped R3** — `md5_fn_norel
   fb5dcbfc2a47` both, marginal identical to the instruction. A dead test that
   says nothing about this address is free and changes nothing. That is p03's
   `sp > 1000` negative control reproduced exactly, and it is what makes the rest
   attributable to the *content* of the clamp rather than to an extra branch.
2. **Seeding the WORD INDEX does nothing.** `m_clamp` — the faithful transplant
   of p03's control, stating exactly the fact `lemma_guard_bounds_word` proves —
   leaves every check standing and costs +2.00 per guarded query. `m_clamp_hi`,
   one past the invariant, is identical to it.
3. **Seeding the BYTE OFFSET deletes them.** `m_clampb` takes `/guarded` from
   56.00 to **14.00** and the kernel from 291 to 218 instructions — **49% of the
   marginal on `small`, 47% on `large`.**

**So p09 localises the seeding boundary that p03 could only demonstrate.** The
inference LLVM will not make is not `q < nbits ⟹ q >> 6 < nwords` (giving it
that for free changes nothing); it is the *composition*
`q >> 6 < nwords ∧ 8·nwords + 4·nq ≤ len − 8 ⟹ ws + 8·(q>>6) + 8 ≤ len`, which
needs the length check and a multiply. **The fact has to be seeded at the level
of the address, not at the level of the index the guard is about** — and the
proof states it at the index.

Two qualifications, both measured:

- ⚠ **`m_clampb_lo`, one byte short of what the access needs, behaves like
  `m_clampb`** (same three slopes, +3 instructions statically, −1.00 Ir). p03's
  `sp > 65` separated cleanly; p09's does not, and the 3-instruction static
  difference is unexplained. Do not quote a one-instruction win here
  (`.memory/03-measurement.md`).
- ⚠ **Seeding only works after the reslice.** On R2, `m_clampb_n` moves
  `/guarded` 34.00 → 37.00 — it does **not** delete anything. Mechanism: R2
  indexes `buf` absolutely and nothing in R2 ever establishes
  `off + len ≤ buf.len()` (it is the caller's structural precondition, which
  safe Rust has no way to state), so there is no length for the clamp to be
  useful against. **R3's `&buf[off..off + len]` is what converts the caller's
  precondition into a fact the optimiser holds**, and that is a second, separate
  thing the reslice buys beyond `win.len() == len`.

### 8a. …and it is not Rust-specific, on p09 as on p03

R1h has no bounds check at all — its only check is the range check on `q` — so
p03's cross-language experiment needs a C rung that *has* one. `c_check` is R1h
plus an explicit `if (ws + (size_t)(8 * (q >> 6)) + 8 > buf_len) return 0;`:

| build | `small` | `large` | vs the cell above |
|---|---:|---:|---:|
| `c-clang-h` (no bounds check) | 5750.72 | 21213.72 | — |
| `c_check-clang` | 6709.72 | 24536.72 | **+959 / +3323** = +4.01 per guarded query |
| `c_check_clamp-clang` (+ the word-index clamp) | 7426.72 | 27026.72 | **+717 DEARER** |
| `c-gcc-h` | 13212.72 | 48917.72 | — |
| `c_check-gcc` | 13934.72 | 51412.72 | +722 / +2495 = +3.02 per guarded query |
| `c_check_clamp-gcc` | 14414.72 | 53074.72 | **+480 DEARER** |

**Two independent middle-ends fail the same inference the same way**, and gcc
shares none with rustc. p03's rule — write it as *"any compiler asked to prove
this"*, never as *"safe Rust"* — holds on p09 with the **opposite sign on the
clamp**: on p03 the word-index clamp deleted the check in both languages, on p09
it deletes it in neither.

### 8b. Anti-collapse margin

The gate reports `64 cell/probe pairs: marginal Ir per call 5019...319629, all
above the derived floor (tightest margin 17.3x over a declared 0.25 Ir/byte);
d(Ir)/d(work) 4.25...71.91`. `model.py` errs **loose** by one term (a guarded
query re-reads its word's eight bytes), so the true visit count is
`stride + 8·xguard` = 2.73× the declared figure on `small`; the floor is
therefore one the kernel must clear with room, which is the only direction that
matters.

### 5e. Two proof mutants, and the gate fails on both

`.memory/05-layout.md` step 5: mutate your own proof and check the gate fails,
including one that makes a **trusted postcondition inconsistent** rather than
merely weaker. Both were applied to the shipped tree, the gate re-run in full,
and the tree restored (`check.py p09` is `PASS` again afterwards).

**M1 — the trusted `requires` weakened by ONE CHARACTER**, in the item, its twin
*and* the `spec.md` pin: `i < v@.len()` -> `i <= v@.len()`. Shipped Verus is
unmoved (`18 verified, 0 errors`); the pin is unmoved because it was edited in
the same commit, which is TASK_003_REVIEW's attack. What fails:

```
FAIL [twin] verus.rs: with `--cfg slb_twin` Verus reports 20 verified, 1 errors
  (18 verified without the twins). At least one trusted precondition is not
  strong enough to license the checked equivalent of the operation its body
  performs
```

**Only the verified twin catches it**, which is exactly what
`.memory/04-verus.md` says is the *only* backstop for this class. p09 is the
ninth pattern to ship a twin and the second (after p08's M2) on which one has
earned its keep against a mutant rather than sitting idle.

**M2 — an INCONSISTENT trusted `ensures`**: `popcount64` gains `r <= 63`, which
is **false** at `x = u64::MAX` (population count 64) while reading as a harmless
bound. Run twice, because which stages fire depends on whether the pin moves too:

| | pin left alone | pin moved in the same edit |
|---|---|---|
| `[proof-pin]` item drifted from `spec.md` | **FAIL** | passes |
| `[clause-mut]` `ensures[1]` is NOT load-bearing (deleting it still gives 18/0) | **FAIL** | **FAIL** |
| `[twin]` twin signature is no longer the trusted item's | **FAIL** | **FAIL** |

So the mutant is caught **three ways** when the pin is left alone and **two**
when it is moved — and the surviving pair are the derived checks, not the
declared one, which is the property `.memory/02-bench-rules.md` asks declared
pins to be backed by. Note what the clause-deletion stage is actually saying: a
false axiom that nothing depends on is *detectable precisely because* nothing
depends on it. It would not have caught a false axiom the proof used.

---

## 9. Dead code kept on purpose

The `len < 8` guard is unreachable given the driver's `stride_w >= 8`. It stays
so the kernel is **total** and its `requires` stays purely structural; the
alternative — a `len >= 8` precondition — would be a precondition about the
driver's own guard rather than about the buffer. The `nbits == 0 || nq == 0`
guard is *not* dead in the same way: it is reachable from the wire format and no
shipped input takes it.

---

## 10a. THE IN-CONTRACT SPREAD, and the R3-side span

`.memory/01-ladder.md` requires at least two independent in-contract R3
spellings with the cheaper quoted, and a **cheapest-found** figure that names its
spelling **and its input**. Every row below is in contract by
`check.py::spelling_matches` (`.temp/p09/ctlpins.py`) and `=====` equivalent to
`model.py` on all five inputs.

| safe spelling | `n_fn` | `small` | `large` | vs R4ship `small` | vs R4ship `large` |
|---|---:|---:|---:|---:|---:|
| **`r3_best`** — `chunks_exact(4)` queries + byte-offset clamp | **132** | **6955.30** | **25373.30** | **+263.00** | **+854.00** |
| `r3_qchunks` — `chunks_exact(4)` queries only | 221 | 18199.30 | 64394.30 | +11507.00 | +39875.00 |
| **R2 shipped** (absolute indexing) | 293 | 16628.30 | 60928.30 | +9936.00 | +36409.00 |
| **R3 shipped** (window reslice) | 291 | 20448.30 | 73404.30 | **+13756.00** | **+48885.00** |
| `r3_wordslice` — a second reslice of the word region | 248 | 23684.30 | 83472.30 | +16992.00 | +58953.00 |

- **fixed-R4 bound** (the one sound quantity, R4 held by fiat):
  `R3ship − R4ship` = `30 + 11·nq + 45·xguard + 19·nwords` = **+13756 / +48885**.
- **R3-side span**, cheapest-found to dearest-found in contract:
  **+263 … +16992** on `small`, **+854 … +58953** on `large`. That is a **65×**
  span, and it is the sharpest illustration this project has of why a published
  spread cannot carry a safety claim.
- **The same spelling is cheapest on both blobs** (`r3_best`), unlike p16 where
  no spelling was — but the figure still names both, per TASK_027.

⚠ **`r3_wordchunks` measured 22722.30 / 80146.30 and is EXCLUDED**: it replaces
`while i < nwords {` with `for c in wr.chunks_exact(8)`, which fails
`required[5]`. It was caught by `.temp/p09/ctlpins.py` *before* being quoted —
which is the check `.tasks/TASK_038.md` asked for after p03 shipped two
out-of-contract controls.

**The R4 side is DEGENERATE, and it was searched.** `m_clamp_u` (+241 on `small`)
and `m_clampb_u` (+721) both *raise* R4, and no unsafe respelling that lowers it
was found: R4 already carries no check to delete, its byte decode is already
idiom-recognised into one `mov`, and every route to a wider load
(`from_le_bytes`, `align_to`, `from_raw_parts`) is `is not supported` at the
pinned vstd *and* `idiom.forbidden`. So the pair interval collapses onto the
R3-side span and **must not be published as a third quantity**
(`.memory/01-ladder.md`, TASK_028).

⚠ **One honest asymmetry, and it is the R4-by-permission result again.**
`r3_best`'s cheapness comes from `chunks_exact(4)`, which is
`is not supported` at the pinned vstd — so **the safe class reaches a spelling
the unsafe class cannot**, and `+263` is not a number any R4 could answer with.
Fourth measured instance after p16, p05, p11 and p03.

---

## 11. What p09 adds to the ladder

1. **The first pattern whose safety check is not a bounds check**, and the answer
   is that it matters: on a **linear** index the safety tax is `0.00000` per word
   and `−3.00000` per query; on the **shift-derived** index it is `+45.00000` per
   guarded query as shipped and `+4.00000` at best. Same rung, same call, same
   buffer, same decoder — three checks, three answers.
2. **p03's seeding result does not transplant, and p09 says where the boundary
   is.** Handing LLVM the fact at the *word index* — exactly what the proof
   proves — changes nothing in Rust or in C; handing it at the *byte offset*
   deletes 49% of the kernel. The failed inference is the composition, not the
   shift.
3. **Two one-character bugs whose obligations are different.** `q & 31` is caught
   only by a functional specification written independently of the code, and not
   even by that if the misunderstanding reaches the spec (`20 verified, 0
   errors`). `q >> 5` is caught by the accessor's **precondition** with the
   functional spec deleted — and by nothing else on any shipped input, in any
   rung, under any sanitiser, at zero instruction cost.
4. **The intrinsic comparison is a null and the library difference is not.**
   `__builtin_popcountll` (clang) and `u64::count_ones()` (rustc) lower to the
   same 23-instruction SWAR body; gcc calls `__popcountdi2` and pays +29.00 per
   word. No rung emits `popcnt` at this box's default `-march`.
5. **The first trusted item in this project that models a CPU instruction**
   rather than a memory operation, and the first twin that has to *implement* a
   contract with a loop rather than restate it with one indexed read.
