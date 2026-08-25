# p46 — schoolbook bignum multiply-accumulate: per-rung findings

Everything here was **run**. Where a number came from a pre-build probe and the
shipped binaries disagreed, **the shipped binaries win and the correction is
written out in full** — that happened twice on this pattern and both are §0a and
§0b below.

Conventions, stated once and repeated at every figure that needs them:

- **`Ir`, `-O3`, inline mode `isolated`, unless a line says otherwise.**
  Cross-mode comparison is not available: at `-O3 whole` the kernel is inlined
  and has no symbol in 10 of the 16 measured cells.
- **Two `Ir` conventions appear here and they are NOT interchangeable.**
  *kernel-exclusive* = `results/p46-bignum-mac.json`'s `kernel_exclusive_ir`
  divided by the call count — the per-call cost of the kernel symbol alone.
  *whole-program marginal* = `(Ir at 200 iterations − Ir at 100) / 100`, which
  includes the driver-loop body. Every LAW below is a **difference of two cells
  on one input**, where both conventions agree exactly and the driver's
  `println!` digit-count term cancels (`.tasks/TASK_026.md` §0 item 2).
- **Cheapest FOUND, never "minimum"**, and the input is always named.

---

## 0. The bug class, settled by runs before any cell was built

p46's bug class is this tree's **fourteenth `index >= len`** (p01, p02, p03,
p05, p07, p11, p12, p13, p14, p16, p17, p19, p36 are the other thirteen), and
`spec.md` and `c/kernel.h` say so first. Its nearest sibling is **p05**; what is
not p05's is in `spec.md`'s opening table and, in one line: **p05's index is
nonlinear and its data arithmetic is trivial; p46 is the mirror.**

### 0a. The harm — and the pre-build probe was WRONG about it

⚠⚠ **A standalone probe (`.temp/t89/harms.c`) said the harm was LOUD: 5 of 6
plain builds aborting with `*** stack smashing detected ***` or faulting. The
shipped cells say the opposite, and the shipped cells win.**

Gate stage 4, all four (opt × mode) variants of each cell:

| input | cell | exit | stdout |
|---|---|---|---|
| `adversarial-nearmiss` | `c-gcc` ×4 | **0** | `9209029040447465374` — **wrong** |
| `adversarial-nearmiss` | `c-clang` ×4 | **0** | `9209029040447465374` — **wrong** |
| `adversarial-oob` | `c-gcc` ×4 | **0** | `17767805309180046146` — **wrong** |
| `adversarial-oob` | `c-clang` **O0**/isolated, **O0**/whole | **−11 SIGSEGV** | — |
| `adversarial-oob` | `c-clang` **O3**/isolated, **O3**/whole | **0** | `17767805309180046146` — **wrong** |

**6 of the 8 plain C cells are SILENT with a wrong answer; 2 fault.** All four
hardened C cells and all four Rust rungs return `REJ` on both rows.

**The mechanism, measured rather than argued** — and it is reproducible from a
CLONE, because `.gitignore` contains `.temp/` and a mechanism cited to a scratch
path is cited to nothing (`.memory/05-layout.md` step 11's corollary):

```
controls/harm_layout.py --layout
```

The shipped kernel has a *second* automatic array, `bl[256]`, that the probe did
not, and the compiler's choice of frame order decides everything:

```
gcc   -O0 and -O3 : bl - out = +768 bytes = +96 limbs -> out[96] IS bl[0]
clang -O3         : bl - out = +768 bytes = +96 limbs -> out[96] IS bl[0]
clang -O0         : bl - out = -2048 bytes            -> out[96] is past the frame
```

> **THE ORDER OF TWO AUTOMATIC ARRAYS DECIDES WHETHER A STACK OVERFLOW IS
> SILENT OR FATAL, AND GCC AND CLANG DISAGREE ABOUT IT AT `-O0` AND AGREE AT
> `-O3`.** Where the two arrays are adjacent the overflow lands *inside the
> b-operand scratch*: no fault, no canary, a corrupted intermediate, exit 0.
> That is **p02's "absorbed by glibc chunk rounding" moved from the heap to the
> stack** — and it is why `-fstack-protector-strong`, which is on by default on
> this box (`gcc -O2 -Q --help=common` prints `-fstack-protector-strong
> [enabled]`), does not save this kernel: the canary is not what gets written.

⚠ **The bug is real on every cell regardless**, and the gate proves it. Stage 7,
both adversarial rows, exit 1:

```
patterns/p46-bignum-mac/c/kernel.c:89:12: runtime error: index 96 out of bounds
    for type 'uint64_t [96]'
```

and ASan calls it `stack-buffer-overflow`, **`WRITE of size 8`** — p46's
out-of-bounds access is a **write**, where p05's is a read.

### 0a run D — THE CONTROL THAT KEEPS THE ROW ALIVE

The identical miscount with the index **clamped** — `out[(i + j) % OUTCAP]` — is
**exit 0 with ASan and UBSan both silent** and a wrong answer, at
`(n, m) = (48,48)`, `(120,120)` and `(200,55)`:

```
controls/harm_layout.py --clamp
  gcc -O1 ASan+UBSan  n=120 m=120  exit=0
    clamped n=120 m=120 n+m=240 OUTCAP=96 -> 5199169214093434441
```

A wrong answer with no memory
event is `p31`'s death. **p46 escapes it only because the index is not clamped,
and the clamp is `forbidden` in the hashed block for exactly that reason.** So
is a product buffer sized from `n + m` at run time, which makes the bug
unreachable by construction.

### 0b. The rung boundary — and the pre-build probe was wrong about that too

⚠⚠ **`.temp/t89/cost.rs` measured `R2 − R4 = +7 Ir per MAC step`. The shipped
cells measure `−0.39`. The probe passed `n` and `m` through `black_box`, so LLVM
had no range for them; in the shipped kernel `n = w[0] as usize` and
`m = w[1] as usize` are `u8`-derived and `n + m <= OUTCAP` is tested, which is
everything LLVM needs to discharge `i + j < 96` itself.**

**This is `.memory/03-measurement.md`'s rule landing on a new case.** That
section says a probe's *intercept* does not transfer; here the probe's **slope**
did not transfer either, and the reason is not the binary — it is that the probe
withheld a range fact the shipped kernel supplies. **A `black_box` on a value
the real kernel derives from the input changes what the optimiser can prove, and
therefore changes which rung boundary exists.**

Shipped, `-O3`, `isolated`, **kernel-exclusive `Ir` per call**
(`results/p46-bignum-mac.json`):

| cell | `small` (n=m=24, 576 MACs) | `large` (n=m=48, 2304 MACs) |
|---|---|---|
| `c-gcc` | 8271.00 | 28866.00 |
| `c-gcc-h` | 8275.00 | 28869.00 |
| `c-clang` | 6108.00 | 23088.00 |
| `c-clang-h` | 6110.00 | 23090.00 |
| **`safe_naive`** | **6241.00** | **23341.00** |
| `safe_tuned` | 6287.00 | 23435.00 |
| `unsafe` | 6406.00 | 24250.00 |
| `verus` | 6406.00 | 24250.00 |

**`safe_naive < safe_tuned < unsafe` at both sizes**, and `verus == unsafe` to
the instruction.

**MECHANISM, FROM THE DISASSEMBLY** (`.temp/build/p46/*-O3-isolated`):

1. **`safe_naive`'s MAC loop contains no conditional branch except its own
   `jne`.** All three bounds checks — `bl[j]`, `out[i+j]` read, `out[i+j]`
   write — are **absent from the machine code**. **p46's safety tax is 0.00.**
2. Having removed them, LLVM **unrolls the safe loop 2×** and does **not**
   unroll the unsafe one. `safe_naive`'s kernel carries 3 `mulq`, `unsafe`'s
   carries 1.

> **So the sign of `R3 − R4` on p46 is an UNROLL DECISION, not a safety cost.**
> §8's rolled-vs-rolled control puts a number on that and §8a derives it
> instruction by instruction.

### 0c. ⚠ The cheapest unsafe spelling found is NOT A RUNG, and the reason is the prover

`identity: unsafe == verus` chains R4 to the pinned vstd. The cheapest unsafe
spelling found takes a **mutable** sub-slice of the product scratch,
`&mut out[i..i + m + 1]`, and indexes *that* unchecked. Measured on the shipped
shape (`controls/mkvariants.py --write`, variant `r4_mutreslice`; whole-program marginal):

| blob | `R4` shipped | `r4_mutreslice` | Δ | `R3` shipped |
|---|---|---|---|---|
| `sweep-n024m024` | 6618.00 | **5921.00** | −697.00 | 6499.00 |
| `sweep-n048m024` | 12708.00 | **11315.00** | −1393.00 | 12469.00 |
| `sweep-n024m048` | 12611.70 | **11050.70** | −1561.00 | 12204.70 |
| `sweep-n044m044` | 20687.70 | **18090.70** | −2597.00 | 20028.70 |
| `sweep-n010m010` | 1529.00 | **1448.00** | −81.00 | 1550.00 |

Exact over all 48 sweep blobs with `m >= 2`, zero residual:

```
r4_mutreslice - R4ship  =  -1 + 7n - 1.5*n*m - 2.5*n*[m odd]
```

**and it is below every safe spelling on every one of the 49 blobs.**

**It is inadmissible.** At the pinned vstd
(`~/tools/verus/vstd/{slice,array}.rs`):

- `slice_subrange` exists for **`&[T]` only**; there is no mutable counterpart.
- `ExSliceIndex::index_mut` carries a `requires` and **no `ensures` at all**.
- `array.rs` has `ref_mut_array_unsizing_coercion` (whole array) and no
  subrange.

Measured, four ways, and **re-runnable from the committed tree** —
`controls/census.py --mutsub` writes the four probes, runs them, and **exits
non-zero unless three verify and the fourth fails**:

| probe | result |
|---|---|
| `&mut out[i..j]` type-checks; `assert(row@.len() == m + 1)` | **verifies** |
| the frame survives: `ensures final(out)@[0] == old(out)@[0]` with `i >= 1` | **verifies** |
| the write does not vanish: `ensures final(out)@ =~= old(out)@` | **FAILS**, correctly |
| **the value is unreachable**: `row[0] = 7` then `ensures final(out)@[i as int] == 7` | **FAILS — `postcondition not satisfied`** |

So a mutable sub-slice at this pin is *sound but valueless*: you can prove what
did **not** change and not what did, and R5 therefore cannot discharge
`r == bn_fold(...)` through one.

> **This is `.memory/01-ladder.md` finding 14's mechanism with a number on it —
> *the safe class can reach spellings the unsafe class cannot, because the
> unsafe class is chained to the prover* — and it is the second measured
> instance after p16's, the first on a WRITE, and the first where the size of
> the gap is priced rather than argued.**

⚠ **What that does NOT license.** It does not make p46's `R3 − R4` a safety
number: §0b already showed the safe rung has no checks left to pay for. p46
supports *"the admissible-unsafe class is bounded above the safe class here"*
and nothing stronger.

---

## 1. What the rungs are

| rung | file | inner step | how `i + j < OUTCAP` is known | its cost |
|---|---|---|---|---|
| R1 | `c/kernel.c` | `out[i + j]` | **it is not** | — |
| R1h | `c/kernel_hardened.c` | `out[i + j]` | one compare, before the loops | **`O(1)` per call** |
| R2 | `safe_naive.rs` | `out[i + j]`, `bl[j]` | the language checks per access | **`0.00` — LLVM removed them** |
| R3 | `safe_tuned.rs` | `out[i..i+m].iter_mut().zip(` | one reslice check per row | `O(n)` |
| R4 | `unsafe.rs` | `arr_get_unchecked(&out, i + j)` | the author asserts it | 0 |
| R5 | `verus.rs` | the same, verbatim | **Verus proves it** | 0 instructions |

---

## 5. R4 == R5, and it is byte-identical

Gate stage 3c:

```
ok   unsafe vs verus O0: norel (md5_fn 28dee7775395; md5_raw equal=False, padding 4/4 B)
ok   unsafe vs verus O3: exact (md5_fn dc8e3fa87d6d; md5_raw equal=True, padding 5/5 B)
```

and dynamically, `verus − unsafe = 0.00` on **all 49 sweep blobs and both matrix
blobs**, to the instruction. `.memory/01-ladder.md` finding 1 for the
twenty-fourth time; nothing new, recorded because the pattern owes it.

The `O0` level is `norel` and not `exact` for the reason p19 measured:
`unsafe.rs` takes its window through an out-of-line `subrange` function
specifically so that it matches `verus.rs`'s `vstd::slice::slice_subrange`,
which is an ordinary call at `O0`. Written as the inline expression `&v[i..j]`,
the pair lands at `differ`.

---

## 6. The proof, and the obligation that costs nothing to run

**`verus.rs`: `21 verified, 0 errors`** at the pinned Verus/vstd
(`./verus_run.py patterns/p46-bignum-mac/verus.rs`), and **`24 verified, 0
errors`** under `--cfg slb_twin`. No `assume`, no `admit`, no
`assume_specification`, no hand-written axiom; five `external_body` items, three
of them contracted.

**The postcondition is `r == bn_fold(buf@, off, len)`** — the same full
functional shape as every other kernel in this tree.

### 6a. The safety line is load-bearing, demonstrated

Delete the three lines `if n + m > OUTCAP { return REJ; }` from a copy of
`verus.rs` — i.e. write `c/kernel.c` in Verus — and it does not verify. The
control is **derived from the shipped `verus.rs` by a committed generator**
(`.memory/05-layout.md` step 11), because a Verus file that reports `n_err > 0`
cannot live in a pattern dir at all:

```
controls/mkvariants.py --write .temp/t89/genvar
./verus_run.py .temp/t89/genvar/v46_nosafety.rs --multiple-errors 12
```

```
error: invariant not satisfied before loop
   |             n + m <= OUTCAP,
verification results:: 20 verified, 1 errors
```

**There is no Verus spelling of `c/kernel.c` that verifies**, and the failure is
on the exact invariant that licenses the unchecked write.

### 6b. ⚠ WHAT IS NOT PROVED, said plainly

`bn_fold` is a recursive specification of the schoolbook **algorithm** — `row`
walks the inner loop, `rows` the outer, `ofold` the checksum — and the proof
shows the exec code implements it. **It does not prove that the algorithm
computes `a × b`**: relating the limb sequence to `Σ a_i b_j 2^(64(i+j))` needs
a limbs-to-`nat` valuation and a nested partial-sum induction, and **that was
deliberately not attempted here.** `TASK_089` §3 warned it might not close in
one session; it was not tried, so **that warning is neither confirmed nor
refuted** and this NOTES does not pretend otherwise.

What IS proved at the value level is the single MAC step, exactly:

```
ensures (r.0 as nat) + (r.1 as nat) * 2^64 == (ai as nat)*(bj as nat) + c + carry
```

And the gap is closed by **testing** instead: `model.py::_fold_bigint` computes
each window with **one Python big-integer multiply** and `selfcheck()` diffs it
against the limb-by-limb fold on every window of every committed input. Gate
stage 2 runs it; 0 disagreements.

### 6c. The nonlinear obligation, and what makes it p46's

`lemma_mac_fits` proves `a*b + c + d <= u128::MAX` for `u64 a, b, c, d`. It is
**tight**: `(2^64−1)^2 + 2(2^64−1) == 2^128 − 1` exactly, so one more `+ 1`
anywhere and the schoolbook step would need a third limb.

⚠ **NO RUNG CHECKS THAT, in either language, at any rung, at any optimisation
level.** It is a proof obligation with **no runtime counterpart**. Beside it
sits `i + j < OUTCAP`, which is trivial to prove — purely linear — and which is
what every bounds check in the safe rungs would have cost money for if LLVM had
not removed them.

> **p46 separates the proof-burden column from the instruction column inside one
> kernel:** the expensive obligation is free to run, and the free obligation is
> the one the rungs are about.

**Two proof modes that no other pattern in this tree uses.** Counted, not
asserted (`controls/census.py --ensures`, which prints both): across all 23
pre-existing `patterns/*/verus.rs` there are **0** occurrences of `by
(bit_vector)` and **0** of `by (compute)` in executable position, and **ten**
patterns carry a comment saying they deliberately avoid `bit_vector` (p03, p04,
p07, p10, p11, p18, p22, p36, p38, p47). p46 uses both.

### 6d. ⚠⚠ THE NOVELTY CLAIM `TASK_086` MADE ABOUT THIS `ensures` IS FALSE

`TASK_086_REPORT` reported p46's `mac` postcondition as *"stronger than any
`ensures` currently in the tree, **all of which are bounds facts**"*, and
`TASK_089` §2 asked for it to be counted before shipping. **Counted, it is
false, and it is not shipped anywhere in this pattern.**

Census by `harness/vparse.py::parse` + `clause_spans` over all 23 pre-existing
`patterns/*/verus.rs`, re-runnable from the committed tree:

```
controls/census.py --ensures
```

- **159 `ensures` conjuncts**, of which **151 are equalities** (`==` or `=~=`).
  The other **8** are **five pure inequalities**, all in p09, and **three
  predicate clauses** in p27 (`is_range` twice, `is_init` once). So *"all of
  which are bounds facts"* is wrong by **151 of 159**.
  ⚠ This paragraph said `154 / 5` until `controls/census.py` was written and
  run; the hand count had put p27's three predicates on the wrong side. **The
  script is committed and the number is whatever it prints.**
- **All 23 kernels** already carry a *full functional* postcondition: 24 kernel
  `ensures` conjuncts, **21** of them literally
  `r == <name>_fold(buf@, off as int, len as int)`, the other three p02's, which
  name `src@` and `dst` because its kernel writes.
- p46's `mac` clause is a divmod-split identity, and **p09 already ships that
  shape one width down**: `lemma_shr6_is_div64: (x >> 6) == x as int / 64` and
  `lemma_and63_is_mod64: (q & 63) == q % 64`.
- The widening multiply and `>> 64` split is in **every** pattern's driver loop
  already — `let k = ((acc as u128 * nwin as u128) >> 64) as usize` — with its
  own `by (nonlinear_arith)` no-overflow proof.

**What survives counting is the weaker true sentence** in §6c: it is the proof
*mode* and the *nonlinearity on data rather than on an address* that are new,
not the strength of the postcondition.

---

## 7. TCB tally

**5 `external_body` items in `verus.rs`, 3 with a contract, 3 verified twins.**
Recounted from the gate's own inventory rather than from this file:

| item | body lines | `requires` | `ensures` | twin |
|---|---|---|---|---|
| `buf_get_unchecked` | 1 | `i < v@.len()` | `r == v@[i as int]` | yes |
| `arr_get_unchecked` | 1 | `i < v@.len()` | `r == v@[i as int]` | yes |
| `arr_set_unchecked` | 3 | `i < old(v)@.len()` | `final(v)@ == old(v)@.update(i as int, x)` | yes |
| `load_input` | 4 | — | — | n/a (no `unsafe`, no `ensures`) |
| `emit` | 1 | — | — | n/a |

⚠ `vstd::slice::slice_subrange` is a **vstd** `external_body` item, not an
author-written one. It does not enter this tally, which counts project-local
trusted items (`.memory/04-verus.md`, where the second *"vstd relied upon"*
column was refuted with a 402-site census and must not be reinstated).

⚠ `arr_set_unchecked`'s `requires` constrains `v` and `i` and says nothing about
`x`, which gate stage 5a flags. The declaration
`verus.unsafe_justifications["verus.rs"]["arr_set_unchecked"]` in `spec.md` is
the answer and the verdict shouts it every run. **It is the same generic item as
p22's, character for character**, and p03/p12/p06/p14/p27/p38/p22 are the seven
patterns before this one to exercise the same false positive.

SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) The twin body is `v[i]`. That is the right checked stand-in: the trusted
body is `*v.get_unchecked(i)` on a `&[u8]`, and the only difference between the
two expressions is the panicking bounds test, so a `requires` too weak to
license the unchecked read is too weak to license the checked one, and Verus can
see the second. `i < v@.len()` is exactly `<[T]>::get_unchecked`'s documented
safety condition; nothing else about `v` or `i` is used.
(b) The `ensures` is COMPLETE with respect to every unchecked operation the body
performs, because the body performs exactly one: a single element read at index
`i`. It reads no other index — in particular no `i + 1`, which is TASK_009_REVIEW
x4's counterexample — it writes nothing, it retains no reference beyond the
returned `u8`, and it has no side effect. `r == v@[i as int]` therefore pins the
whole of the body's observable behaviour, and there is no unchecked operation
left over for which the contract is silent.
(c) Each clause means the same in both configurations. `v@` is the sequence view
of the same `&[u8]` in both, `i` is the same `usize`, and `v@.len()` is the
slice length in both — `#[cfg(slb_twin)]` changes which body is compiled and
changes neither type nor view. The token `slb_twin` appears in this file only
inside the twins' own `#[cfg]` attributes, so no `const` and no clause varies
with the configuration.

SLB-TRUSTED-ARGUMENT verus.rs arr_get_unchecked

(a) The twin body is `v[i]`. The trusted body is `*v.get_unchecked(i)` on a
`&[T; N]` for `T: Copy`; the checked `v[i]` is the same read with the panicking
test restored, and it is the strongest stand-in available because it is the same
operation. `i < v@.len()` — which for a `[T; N]` reads `i < N`, supplied by
vstd's `group_array_axioms` — is precisely the safety condition the standard
library documents for `get_unchecked`.
(b) The `ensures` is COMPLETE with respect to every unchecked operation the body
performs. The body performs exactly one unchecked operation, an element read at
`i`, and the postcondition fixes its value to `v@[i as int]`. It reads no
neighbouring index, writes nothing, takes no address that outlives the call and
returns a `Copy` value; the array itself is `&`-borrowed, so no mutation is
expressible. There is no operation the clause fails to describe.
(c) Each clause means the same in both configurations. The item is generic over
`T: Copy` and `const N: usize` in both, `v@` is the same `Seq<T>` view, and
`v@.len() == N` holds identically in both because it comes from vstd's array
axioms and not from anything this file declares. `#[cfg(slb_twin)]` swaps only
the body.

SLB-TRUSTED-ARGUMENT verus.rs arr_set_unchecked

(a) The twin body is `v[i] = x`. The trusted body is
`*v.get_unchecked_mut(i) = x` on a `&mut [T; N]`; the twin is the same store
with the panicking bounds test restored, which is the right stand-in for exactly
the reason the read wrappers' is — the two differ in the test and in nothing
else. This is the item that licenses p46's out-of-bounds WRITE if its
precondition is wrong, so it is the one that matters most on this pattern.
(b) The `ensures` is COMPLETE with respect to every unchecked operation the body
performs. The body performs exactly one: a single element store at index `i`.
`final(v)@ == old(v)@.update(i as int, x)` fixes both halves of that — the new
value at `i`, and, by the definition of `Seq::update`, that **every other index
is unchanged**. A body that also wrote `i + 1` would satisfy neither half, which
is the case TASK_009_REVIEW x4 names and the reason the frame is stated as an
`update` rather than as a value at `i`. The body allocates nothing, reads no
other index and retains no reference.
(c) Each clause means the same in both configurations. `old(v)@` and `final(v)@`
are the pre- and post-views of the same `&mut [T; N]` in both, `Seq::update` is
vstd's, and `i < old(v)@.len()` is `i < N` in both. The parameter `x` is a pure
VALUE — it is stored and never used as an address, an index or a length — which
is why the `requires` constrains only `v` and `i`; that is declared in
`spec.md`'s `verus.unsafe_justifications` and printed by the gate on every run.

---

## 8. The cost laws, fitted FROM THE SHIPPED BINARIES

⚠ **Every law here is re-fitted against `.temp/build/p46/<cell>-O3-isolated`.**
`.memory/03-measurement.md`: a probe measures a slope and its intercept is a
property of the probe. On p46 even the slope did not transfer (§0b), so nothing
from `.temp/t89/cost.rs` is quoted as a p46 number.

**Convention: whole-program marginal `Ir` per kernel call,
`(Ir @ 200 iters − Ir @ 100) / 100`, `-O3`, inline mode `isolated`.** Every law
is a *difference of two cells on one input*, so the driver's `println!`
digit-count term cancels exactly and every value below is an integer.

**Domain: `m >= 2`.** `m = 1` is off it — see §8c.

```
R5 - R4  =  0                                     exact, 49/49 sweep blobs + both matrix blobs

R2 - R4  =  3 + 5n - n*floor(m/2)                 48 blobs, max |residual| 0.00000
R3 - R2  =  2n - 2   (m even)                     48 blobs, max |residual| 0.00000
            -2       (m odd)
R3 - R4  =  1 + 7n - n*floor(m/2)   (m even)
            1 + 5n - n*floor(m/2)   (m odd)

R1h - R1, clang  =  +2.00 flat                    exact, 49/49
R1h - R1, gcc    =  +4.00 flat, WITH TWO MEASURED EXCEPTIONS AT +3.00 (see 8d)
```

### 8a. ⚠ THE SIGN OF `R3 − R4` IS AN UNROLL, AND HERE IS THE CONTROL

`R2 − R4` is **negative** for all but the smallest shapes — safe Rust is cheaper
than unsafe Rust. **None of it is safety.** Rolled-vs-rolled control (p16's
shape): rebuild **the shipped sources, unedited**, with
`-C llvm-args=-unroll-count=1`:

```
rustc -C opt-level=3 -C debug-assertions=off -C panic=unwind --edition 2021 \
      --cfg slb_isolated safe_naive.rs -C llvm-args=-unroll-count=1 -o sn_rolled
rustc ... unsafe.rs -C llvm-args=-unroll-count=1 -o un_rolled
```

| blob | `safe_naive` rolled | `unsafe` rolled | Δ | `n*m` |
|---|---|---|---|---|
| `sweep-n024m024` | 7916.00 | 6764.00 | **+1152.00** | 576 |
| `sweep-n048m024` | 15236.00 | 12932.00 | **+2304.00** | 1152 |
| `sweep-n024m048` | 15139.70 | 12835.70 | **+2304.00** | 1152 |
| `sweep-n044m044` | 24835.70 | 20963.70 | **+3872.00** | 1936 |
| `sweep-n010m010` | 1784.00 | 1584.00 | **+200.00** | 100 |

```
R2 - R4, both rolled  =  +2.00000 * n * m       exact, 5 shapes, zero residual
```

**So the whole of p46's "safe beats unsafe" is LLVM's decision to unroll one
loop 2× and not the other**, and the underlying spelling difference is a flat
`+2.00` per MAC step *against* safe Rust.

**Derived per instruction, not presumed** (`.memory/03-measurement.md`: a static
diff bounds a change, it does not measure it — so here is the whole loop body
from both rolled binaries):

```
safe_naive, rolled          unsafe, rolled
  mov  %rcx,%rax              mov  %rcx,%rax
  mulq bl[j]                  mulq bl[j]
  xor  %r9d,%r9d          <-- (+1)
  add  out[i+j],%r8           add  %r8,%rax
  setb %r9b               <-- (+1)      adc  $0x0,%rdx
  add  %rax,%r8               add  %rax,out[i+j]   <-- read-modify-write, ONE insn
  mov  %r8,out[i+j]       <-- separate store
  mov  %r9,%r8                mov  %rdx,%r8
  adc  %rdx,%r8               adc  $0x0,%r8
  inc  %rdi                   inc  %rdi
  cmp  %rdi,%r15              cmp  %rdi,%r15
  jne                         jne
  = 12 instructions           = 10 instructions
```

Safe pays `xor` + `setb` (materialising the carry out of the accumulator add)
and a *separate* store where unsafe folds the accumulator update into one
`add %rax,(mem)`; unsafe pays one extra `adc $0x0,%rdx`. Net **+2**, which is
the measured coefficient exactly.

⚠ **NEITHER LOOP CONTAINS A BOUNDS CHECK.** There is no `jae`, no `jb` and no
panic edge in either body. **p46's per-MAC safety tax is 0.00000 and that is the
sentence to quote** — the `+2.00` is a carry-materialisation spelling and the
`−0.5·n` is an unroll.

### 8b. The in-contract spread, BOTH SIDES, on the shipped shape

`.memory/01-ladder.md`: *searching one side is not searching.* Measured on the
same five shapes, whole-program marginal, all differences against the shipped
cell of the same rung:

Every lever is derived from a **shipped** rung source by exact-string
substitution, by the committed generator `controls/mkvariants.py`, which asserts
each substitution applies exactly once and **fails closed** if a rung moves:

```
controls/mkvariants.py --check     # 7 substitutions, each applying exactly once
controls/mkvariants.py --write <dir>
```

| side | lever | Δ vs shipped |
|---|---|---|
| **R4** | `r4_inline` — the `mac` helper written out in the loop body | **−1.00 flat** |
| **R4** | `r4_runidx` — a running output index `oi` instead of `i + j` | **−3.00 flat** |
| **R3** | `r3_reslice` — reslice the row, index it with a `while` | **−2.00 flat** |
| **R3** | `r3_rangefor` — reslice the row, index it with `for j in 0..m` | **−2.00 flat** |
| **R2** | `r2_rangefor` — the same body with `for` loops | **−2.00 flat** |

**Three levers on the R4 side and three on the R3 side, and BOTH SIDES ARE
DEGENERATE** — every lever is flat in `n` and in `m`, R4's span is 3 Ir/call and
R3's is 2. So the pair interval collapses onto the R3-side span
(`.tasks/TASK_026.md` §0 item 4), and the published `R3 − R4` law does not
depend on which of the three is shipped.

⚠ **The exception is `r4_mutreslice` (§0c), which is NOT flat and NOT
degenerate — `−1 + 7n − 1.5nm − 2.5n[m odd]`, i.e. −697 to −2597 Ir/call over
these five shapes — and it is NOT A RUNG.** It is the reason this pattern's R4
is knowingly off the floor of its own class, and the reason is a property of the
prover.

### 8c. `m = 1` is off the laws' domain, and only one blob is there

`sweep-n024m001` measures `R2 − R4 = 51.00` where the law says `123`, and
`R3 − R4 = 49.00` where the law says `121`. `R3 − R2 = −2.00` is on the law.
**One blob is not a term** — `.memory/03-measurement.md` records p38's `rlen==1`
turning out to be a law term rather than an anomaly, and settling that here would
need a band this pattern does not ship. **Stated as a domain restriction, not
explained.**

### 8d. `R1h − R1` for gcc is +4.00 with two exceptions, and the mechanism is a presumption

clang's is exactly `+2.00` on all 49 sweep blobs — one `cmp` and one `ja`,
executed once per call, and nothing else. gcc's is `+4.00` on 48 of the 49 and
**`+3.00` on `sweep-n024m048`**; by the kernel-exclusive convention it is `+4`
on `small.bin` (24,24) and `+3` on `large.bin` (48,48). Both exceptions sit at
`m = 48`. **No mechanism is offered**: a static diff would bound it and not
measure it, and nobody has run a per-instruction callgrind on it. Most likely
code alignment. Flagged rather than explained.

### 8e. The four hardening strategies, priced side by side

This is p19's *"the two hardening strategies have different asymptotics"* with
four terms instead of two, and it is the pattern's cleanest positive result:

| how `i + j < OUTCAP` is established | cost |
|---|---|
| R5, statically, by proof | **0 instructions** |
| R1h, one compare on `n + m` before the loops | **+2.00 (clang) / +4.00 (gcc) per call, flat in n and m** |
| R2/R3, per access, by the language | **0.00** — LLVM discharges it and deletes them |
| R4, by assertion | 0, and it is the DEAREST Rust rung anyway (§8a) |

⚠ **C's fix is the cheapest non-zero one and it is `O(1)`, not `O(table)`**:
because the limb counts are two bytes in the header, C can test the *whole*
obligation once, before it starts. p19's hardened rung had to walk 2048 bytes.

---

## 8f. Every law above is re-derivable by ONE command from committed files

`.memory/05-layout.md` and `RECAP`: *ask which single command carries a change
from the source all the way to the number a reader quotes.* On p46 that command
is

```
harness/build.py p46 --all --opt O3 --mode isolated
controls/sweep_ir.py --measure --out sweep.json
controls/sweep_ir.py --check   --data sweep.json     # exits 1 on any residual
```

`--check` re-derives §8's laws from the marginals and **exits non-zero if a
single residual is non-zero**. It also asserts the thing the arithmetic rests
on — that every rung *difference* is an exact integer, because the driver's
`println!` digit-count term cancels within a difference and does not within an
absolute marginal. Its output on the shipped tree:

```
ok   R5 - R4  =  0                                  49 blob(s), m >= 1, max |residual| = 0.00000
ok   R2 - R4  =  3 + 5n - n*floor(m/2)              48 blob(s), m >= 2, max |residual| = 0.00000
ok   R3 - R2  =  2n - 2 (m even) / -2 (m odd)       48 blob(s), m >= 2, max |residual| = 0.00000
ok   R3 - R4  =  (R2-R4) + (R3-R2)                  48 blob(s), m >= 2, max |residual| = 0.00000
note R1h - R1, gcc  : +3.00 on 1, +4.00 on 48   exception(s) at ['24,48']
note R1h - R1, clang: +2.00 on 49
note m = 1 is OFF the laws' domain (../NOTES.md 8c): R2-R4 measured 51.00, law would say 123
```

⚠ **The laws are checked, not fitted, by that command.** They were fitted once,
from bands N and M plus band D, and §8g records why band D was necessary.

### 8g. ⚠ THE TWO AXIS BANDS ALONE DO NOT DETERMINE THE LAW

Fitting `A + B*n + C*floor(m/2) + D*n*floor(m/2)` to band N (`m = 24` held) and
band M (`n = 24` held) gives **four equations in four unknowns of which only
three are independent** — the fourth is an identity, and the family
`A = 291 + 288D, B = -7 - 12D, C = -24 - 24D` fits both axis bands exactly for
**every** `D`. **One off-axis point pins it** — `sweep-n010m010` gives `D = -1`
— and the remaining **nine** band-D blobs then have **zero residual** without
having been fitted to.

> **That is the residue/missing-column rule of `.memory/03-measurement.md` in
> its sharpest form: a two-parameter law fitted on two axis-aligned bands is not
> merely at risk of a missing term, it is UNDERDETERMINED, and no in-sample
> residual can show it.** p38's additivity failure was this shape. Band D is
> shipped for exactly this reason and `inputs/gen.py` says so.

---

## 9. `Ir` versus the clock

p46's inner loop is a **serial dependency chain through `carry`**: step `j+1`'s
`add` needs step `j`'s `adc`, so the loop neither vectorises nor unrolls
usefully and every added instruction is an issue slot rather than a stall. That
makes it a good place to ask whether `Ir` and `ns` agree — findings 5 and 6.

**NOT ANSWERED HERE, and saying so is the point.** The `ns` column in
`results/p46-bignum-mac.json` is a 30-rep interleaved block on one pinned core;
`.memory/03-measurement.md` records that this box's timing floor and its
sensitivity to concurrent load make a sub-5% wall-clock claim unsafe, and the
differences this pattern is about are **0.4% to 3%** of the kernel. **No
wall-clock claim is made for p46 and none should be quoted from its table.**

---

## 9a. The controls, and where they live

| control | what it settles | how to run it |
|---|---|---|
| `controls/harm_layout.py --clamp` | the clamped spelling is exit 0 with both sanitizers silent — the row's memory-unsafe framing is conditional (0a run D) | one command |
| `controls/harm_layout.py --layout` | the frame order of the two automatic arrays, which is why the shipped C rung is silent (0a) | one command |
| `controls/mkvariants.py --check` | all 7 variants still derive from the shipped sources by an exact-string substitution that applies **exactly once** | one command |
| `controls/mkvariants.py --write D` | emits the 6 spelling levers of 8b/0c and the deliberately-broken Verus control of 6a | one command |
| `controls/sweep_ir.py --measure/--check` | re-derives §8's laws from the shipped binaries and **exits 1 on any residual** | two commands |

⚠ **The pre-build probes are NOT here and should not be re-run as if they were
p46 numbers.** `.temp/t89/{harms.c,cost.rs}` are the two artefacts whose
conclusions the shipped cells overturned (0a, 0b); they are kept in the task's
scratch as the record of the correction and nothing in this file quotes them as
a p46 measurement.

---

## 10. What was NOT done

- **The mathematical product is not proved** (§6b). It was not attempted.
- **`m = 1` is a documented domain restriction**, not an explained term (§8c).
- **gcc's `R1h − R1` exceptions have no mechanism** (§8d).
- **No wall-clock claim** (§9).
- **No cross-inline-mode comparison**: at `-O3 whole` the kernel is inlined and
  `kernel_exclusive_ir` is `None` in 10 of 16 cells.
- **The `black_box` finding in §0b is p46's own measurement and has not been
  checked against any other pattern's probe.** It may or may not generalise.
