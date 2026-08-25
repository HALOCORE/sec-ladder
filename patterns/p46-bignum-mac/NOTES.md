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
cells measure `−0.39`.** In the shipped kernel `n = w[0] as usize` and
`m = w[1] as usize` are `u8`-derived and `n + m <= OUTCAP` is tested, which is
everything LLVM needs to discharge `i + j < 96` itself. **The probe's kernels
took `n` and `m` as parameters, so they had none of that.**

⚠ **THE MECHANISM THIS SECTION GAVE UNTIL TASK_092 WAS THE WRONG ONE, AND IT
HAD ALREADY REACHED `.memory/`** (TASK_089_REVIEW B2). It blamed `black_box`.
It is not `black_box`: every probe kernel in `.temp/t89/cost.rs` is
`#[no_mangle] #[inline(never)] pub fn`, i.e. **external linkage, so a
caller-side `black_box` cannot reach the callee's codegen at all** — and the
review rebuilt the probes with and without it and got **byte-identical
binaries** (`k46_checked` 296 B `a73eda77…`, `k46_unchecked` 126 B `daca171e…`,
both unchanged). The real cause is one level up:

> **A PROBE WHOSE KERNEL *SIGNATURE* DIFFERS FROM THE SHIPPED KERNEL'S LOSES
> THE RANGE FACTS THE SHIPPED KERNEL DERIVES FROM ITS INPUT HEADER.** Isolated
> by compiling p46's *shipped* body beside the probe's `k46_checked` in one
> binary, both called through `black_box`: `k46_checked` keeps **10 conditional
> branches**; the shipped body loses every bounds check.

⚠ **The retraction has teeth in the other direction too**: a probe author who
drops `black_box` *"so as not to hide range facts"* re-enables the constant
folding `black_box` exists to prevent, while the real cause goes unfixed. Give
the probe the **shipped signature** — fixed-capacity scratch, dimensions derived
from an input header — and keep the `black_box`.

**This is `.memory/03-measurement.md`'s rule landing on a new case.** That
section says a probe's *intercept* does not transfer; here the probe's **slope**
did not transfer either.

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

### 0c. ⚠⚠ The cheapest unsafe spelling found is NOT A RUNG — and the reason this section gave until TASK_092 was FALSE

`identity: unsafe == verus` chains R4 to the pinned vstd. The cheapest unsafe
spelling found takes a **mutable** sub-slice of the product scratch,
`&mut out[i..i + m + 1]`, and indexes *that* unchecked. Measured on the shipped
shape (`controls/mkvariants.py --write`, variant `r4_mutreslice`; whole-program
marginal, **`-C codegen-units=1` — see the flag warning below**):

| blob | `R4` shipped | `r4_mutreslice` | Δ | `R3` shipped |
|---|---|---|---|---|
| `sweep-n024m024` | 6618.00 | **5923.00** | −695.00 | 6499.00 |
| `sweep-n048m024` | 12708.00 | **11317.00** | −1391.00 | 12469.00 |
| `sweep-n024m048` | 12611.70 | **11052.70** | −1559.00 | 12204.70 |
| `sweep-n044m044` | 20687.70 | **18092.70** | −2595.00 | 20028.70 |
| `sweep-n010m010` | 1529.00 | **1450.00** | −79.00 | 1550.00 |

**and it is below every safe spelling on every one of these blobs.** Exact over
all 48 sweep blobs with `m >= 2`, zero residual, re-fitted at TASK_092 with the
shipped flag set. **Re-derivable by three commands from the committed tree**,
which is the standard `.memory/05-layout.md` step 11's corollary sets — a
mechanism cited to a `.temp/` path is cited to nothing, because `.gitignore`
contains `.temp/`:

```
controls/mkvariants.py --write DIR
~/.cargo/bin/rustc --edition 2021 -C codegen-units=1 -C opt-level=3 \
    -C debug-assertions=off --cfg slb_isolated DIR/r4_mutreslice.rs -o r4m
# then the marginal of `r4m` against .temp/build/p46/unsafe-O3-isolated,
# by controls/sweep_ir.py's convention, on each sweep blob
```


```
r4_mutreslice - R4ship  =  1 + 7n - 1.5*n*m - 2.5*n*[m odd]
```

(It read `-1 + 7n - ...` until TASK_092; only the constant moved, so the
`1.5` Ir/MAC coefficient this pattern quotes is unchanged.)

⚠ **THE FLAG WARNING, because it moved every number in this section and in 8b.**
Until TASK_092 the table above read `5921 / 11315 / 11050.70 / 18090.70 / 1448`,
Δ `−697 … −2597`. Those variants were built by `controls/mkvariants.py`'s
documented command, which **omitted `-C codegen-units=1`** — a flag
`harness/build.py::rust_flags` passes to *every* measured cell. Unlike 8a's
rolled-vs-rolled control, where both sides were rebuilt and the shift cancelled
(TASK_089_REVIEW m3), here only the variant side moved, so it did **not**
cancel: every variant is 1 to 2 Ir/call off. Re-measured with the shipped flag
set — rebuild each variant with and without `-C codegen-units=1` and the
`default` build reproduces the old table exactly while the `codegen-units=1`
build gives the table above. **The generator's docstring now carries the flag**,
so the command a reader runs is the right one.

#### The stated reason was false. The pinned vstd DOES specify a mutable sub-slice.

Until TASK_092 this section said a mutable sub-slice at the pinned vstd is
*"sound but valueless"* — that you can prove what did **not** change and not
what did. **That is wrong** (TASK_089_REVIEW B1). The engineer read
`vstd/slice.rs`'s `ExSliceIndex` **trait declaration**, which does carry a
`requires` and no `ensures`, and mistook it for the specification.
`~/tools/verus/vstd/std_specs/slice.rs` ships

```rust
pub assume_specification<T>[ <Range<usize> as SliceIndex<[T]>>::index_mut ]
    (i: Range<usize>, slice: &mut [T]) -> (r: &mut [T])
    ensures  r@ == old(slice)@.subrange(i.start as int, i.end as int),
             final(r)@ == final(slice)@.subrange(i.start as int, i.end as int),
             forall|j: int| !(i.start <= j < i.end) ==> final(slice)@[j] == old(slice)@[j],
```

— a full **value-level** specification. This is the `copy_from_slice` failure
mode recurring, and `CLAUDE.md` now names `std_specs/` for that reason.

#### And the FULL R5 closes. `21 verified, 0 errors`.

Built at TASK_092 as `controls/mkvariants.py`'s `v46_mutreslice`, derived from
the shipped `verus.rs` by exact-string substitution:

```
controls/mkvariants.py --write DIR
./verus_run.py DIR/v46_mutreslice.rs --multiple-errors 12
verification results:: 21 verified, 0 errors
```

Same count as the shipped `verus.rs`, same postcondition
`r == bn_fold(buf@, off as int, len as int)`, **no `assume`, no `admit`, no
`assume_specification`**. Three ingredients close it, and all three are cheap:

1. a ghost mirror `gout: Seq<u64>` of the array, taken **before** the borrow —
   `out` cannot be named while it is mutably borrowed, so the invariant is
   carried on the mirror;
2. the invariant `row@ == gout.subrange(i, i + m + 1)` plus a frame clause
   `forall q outside [i, i+m+1) ==> gout[q] == out0[q]`;
3. `vstd::seq::lemma_seq_subrange_index` at each use, and once more **after the
   borrow ends** to turn `index_mut`'s `final(r)@ == final(slice)@.subrange(..)`
   into `out@ =~= gout`.

**Mutation-tested, so it is not vacuous** (`controls/census.py --mutsub` runs
both):

| mutation | result |
|---|---|
| delete the safety line `if n + m > OUTCAP { return REJ; }` | **`20 verified, 1 errors`**, *invariant not satisfied before loop* on `n + m <= OUTCAP` |
| write `lo ^ 1` instead of `lo` | **`20 verified, 1 errors`**, *assertion failed* |

#### What DOES disqualify it — two measured reasons, neither of them the one this section used to give

**(a) It costs TWO NEW TRUSTED ITEMS.** The win comes from
`row.get_unchecked(j)` / `row.get_unchecked_mut(j)` on a `&mut [u64]`, and the
pinned vstd has **zero** occurrences of `get_unchecked` anywhere:

```
grep -rn "get_unchecked" ~/tools/verus/vstd/     ->  0 hits
```

so R5 must add `slice_get_unchecked` and `slice_set_unchecked` as
`external_body` items with hand-written contracts. p46's TCB goes **5
`external_body` / 3 contracted → 7 / 5**. That is the same disqualifier
`spec.md`'s own named-spelling paragraph records for p16's `r4_hdr`: *"shipping
either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on
p16."*

**(b) The R4/R5 pair is `differ` at `-O3`, and the gap is `15n + 1` Ir/call.**
This pattern pins `identity: unsafe == verus, O0 norel / O3 exact`. The
mutreslice pair does not meet it — and this is the first spelling in this tree
where the same exec source compiles **differently** at the two rungs:

| blob | `r4_mutreslice` | `v46_mutreslice` | `R5 − R4` | `15n + 1` |
|---|---|---|---|---|
| `sweep-n024m024` | 5923.00 | 6284.00 | **+361.00** | 361 |
| `sweep-n048m024` | 11317.00 | 12038.00 | **+721.00** | 721 |
| `sweep-n024m048` | 11052.70 | 11413.70 | **+361.00** | 361 |
| `sweep-n044m044` | 18092.70 | 18753.70 | **+661.00** | 661 |
| `sweep-n010m010` | 1450.00 | 1601.00 | **+151.00** | 151 |

**MECHANISM, FROM THE DISASSEMBLY**, and it is two effects that sum to 15 per
outer-loop iteration:

```
harness/asm.py diff <r4_mutreslice> <v46_mutreslice>
  identical by raw machine-code bytes : False
  identical with pc-rel fields masked : False        -> identity level `differ`

conditional branches (harness/asm.py show | grep '^j'):
  r4_mutreslice  ja:2 jae:2 jb:1 jbe:1 je:6 jne:5
  v46_mutreslice ja:3 jae:2 jb:1 jbe:1 je:6 jne:5    <- ONE extra `ja`
```

1. **The per-row reslice bound test survives in R5 and not in R4**:
   `lea (%r8,%rbx,1),%rsi ; cmp $0x60,%rsi ; ja <panic>` — **+3 per row**.
2. **R5 does not fold `load_u64`'s eight byte reads into one 8-byte load.**
   R4 emits `mov (%r12,%r13,8),%rcx`, one instruction; R5 emits a 4-byte `mov`,
   four `movzbl`, four `shl` and four `or` — **+12 per row**. `movzbl` count in
   the kernel: R4 3, R5 7; shipped `unsafe` 3, shipped `verus` 3.

`3 + 12 = 15`, and the `+1` is one-time. Static: `n_nopad` 169 against 189.

⚠ **The exec source of the two is textually identical** (ghost-stripped diff:
brace placement only), and the shipped nest does **not** diverge — shipped
`verus` and `unsafe` are `O3 exact`. **Why LLVM diverges on this spelling and
not on the shipped one is NOT established.** Flagged, not explained, the same
way 8d is.

#### What this does and does not license, said plainly

> **The exclusion stands, the reason has changed, and the headline is now
> contingent on things that could be relaxed.** Under the pinned
> `identity` and the TCB rule, `r4_mutreslice` is out, both in-contract spans
> stay degenerate (8b) and *safe beats unsafe* survives. **If either were
> relaxed the headline would invert**: `r4_mutreslice` at 5923 and even
> `v46_mutreslice` at 6284 are below `safe_naive`'s 6453 and `safe_tuned`'s
> 6499 at `(24,24)`, and below both on 4 of the 5 shapes above.

So this is still `.memory/01-ladder.md` finding 14's shape — *the safe class can
reach spellings the unsafe class cannot, because the unsafe class is chained to
the prover* — but **the chain is the trusted base and the identity pin, not a
missing specification**, and that is a weaker and more specific claim than the
one this section shipped.

⚠ **What it does NOT license.** It does not make p46's `R3 − R4` a safety
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
| R3 | `safe_tuned.rs` | `out[i..i+m].iter_mut().zip(` | the language checks it — and LLVM removed that too | **`0.00`; the measured `2n − 2` is ADDRESS ARITHMETIC (§8e)** |
| R4 | `unsafe.rs` | `arr_get_unchecked(&out, i + j)` | the author asserts it | 0 |
| R5 | `verus.rs` | the same, verbatim | **Verus proves it** | 0 instructions |

⚠ **The R3 row said *"one reslice check per row"*, cost `O(n)`, until TASK_092.
There is no such check in the machine code** (TASK_089_REVIEW M2, re-derived
here). `safe_tuned` and `safe_naive` have the **identical** conditional-branch
multiset — `ja:2 jae:2 jb:1 jbe:1 je:6 jne:5` — so R3 does not add a check, it
removes none, and the `2n − 2` it is dearer by is a hoisted `lea`/`add` pair.
**There are THREE hardening strategies in this pattern, not four** (§8e).

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
R1h - R1, gcc    =  +4.00 flat, WITH ONE MEASURED EXCEPTION AT +3.00 (see 8d)
```

⚠ **NAME THE CONVENTION AT THE EXCEPTION, because there are two and this line
is under a header declaring one of them** (TASK_089_REVIEW m1). Under **this
section's convention — whole-program marginal, the 49 sweep blobs — there is
exactly ONE exception**, `sweep-n024m048`. §8d's *second* exception is real but
belongs to the **kernel-exclusive** convention on the matrix inputs
(`8275 − 8271 = +4` on `small`, `28869 − 28866 = +3` on `large`). Neither prose
nor tool was wrong; the summary line was counting across both conventions
without saying so.

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
controls/mkvariants.py --check     # 8 substitutions, each applying exactly once
controls/mkvariants.py --write <dir>
```

⚠⚠ **BUILD THE VARIANTS WITH `-C codegen-units=1`.** `harness/build.py` passes
it to every measured cell; the generator's documented command omitted it until
TASK_092, and every number in this table moved by 1–2 Ir/call as a result
(§0c's flag warning has the before/after). Unlike 8a's control, where both sides
were rebuilt and the shift cancelled, here only the variant side had moved.

| side | lever | Δ vs shipped |
|---|---|---|
| **R4** | `r4_inline` — the `mac` helper written out in the loop body | **0.00 flat** |
| **R4** | `r4_runidx` — a running output index `oi` instead of `i + j` | **−2.00 flat** |
| **R3** | `r3_reslice` — reslice the row, index it with a `while` | **0.00 flat** |
| **R3** | `r3_rangefor` — reslice the row, index it with `for j in 0..m` | **0.00 flat** |
| **R2** | `r2_rangefor` — the same body with `for` loops | **0.00 flat** |

(The same table under the *old*, wrong flag set read −1.00 / −3.00 / −2.00 /
−2.00 / −2.00; rebuilding each variant without `-C codegen-units=1` reproduces
it exactly, which is how the flag was identified as the cause.)

**Three levers on the R4 side and three on the R3 side, and BOTH SIDES ARE
DEGENERATE** — every lever is flat in `n` and in `m`, R4's span is **2** Ir/call
and R3's is **0**. So the pair interval collapses onto the R3-side span
(`.tasks/TASK_026.md` §0 item 4), which is itself zero, and the published
`R3 − R4` law does not depend on which of the three is shipped.

⚠ **The exception is `r4_mutreslice` (§0c), which is NOT flat and NOT
degenerate — `1 + 7n − 1.5nm − 2.5n[m odd]`, i.e. −695 to −2595 Ir/call over
these five shapes — and it is NOT A RUNG.** It is the reason this pattern's R4
is knowingly off the floor of its own class. ⚠ **The reason is NOT the one this
file gave until TASK_092:** its full R5 verifies, `21 verified, 0 errors`. What
excludes it is two new trusted items and an R4/R5 pair that is `differ` at
`-O3` by `15n + 1` Ir/call. §0c has all of it, including what happens to the
headline if either constraint is relaxed.

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
**`+3.00` on `sweep-n024m048`** — that is **one** exception, and it is the only
one this section's *whole-program marginal* convention has. **Under the
kernel-exclusive convention on the matrix inputs** it is `+4` on `small.bin`
(24,24) and `+3` on `large.bin` (48,48) — a second, *different* exception, in a
*different* convention (TASK_089_REVIEW m1; §8's summary line used to add them
up without saying so). Both sit at `m = 48`. **No mechanism is offered**: a static diff would bound it and not
measure it, and nobody has run a per-instruction callgrind on it. Most likely
code alignment. Flagged rather than explained.

### 8e. ⚠ THREE hardening strategies, not four — and the retracted fourth is R3's

Until TASK_092 this section, `README.md` and `spec.md`'s `why` all said **four
hardening strategies with four different asymptotics** — `0`, `O(1)`,
`O(n·m)`-that-vanishes and R3's `O(n)`. **R3's does not exist**
(TASK_089_REVIEW M2), and it was called *"the pattern's cleanest positive
result"*, so this is the correction that costs the most.

| how `i + j < OUTCAP` is established | cost |
|---|---|
| R5, statically, by proof | **0 instructions** |
| R1h, one compare on `n + m` before the loops | **+2.00 (clang) / +4.00 (gcc) per call, flat in n and m** |
| R2/R3, per access, by the language | **0.00** — LLVM discharges it and deletes them, in **both** safe rungs |
| R4, by assertion | 0, and it is the DEAREST Rust rung anyway (§8a) |

**RE-DERIVED HERE FROM BOTH SIDES, not taken from the review.**

```
harness/asm.py show .temp/build/p46/<cell>-O3-isolated | grep -oE '^j[a-z]+' | sort | uniq -c

safe_naive :  ja:2  jae:2  jb:1  jbe:1  je:6  jne:5      (jmp:6)
safe_tuned :  ja:2  jae:2  jb:1  jbe:1  je:6  jne:5      (jmp:6)   <- IDENTICAL
unsafe     :  ja:2  jae:2  jb:1  jbe:1  je:4  jne:5      (jmp:4)
```

**The two safe rungs have the identical conditional-branch multiset.** R3
therefore adds no check and removes none; the whole of `R3 − R2` is address
arithmetic, and `harness/asm.py diff safe_naive safe_tuned` shows exactly where:

```
row header, once per row            safe_naive        safe_tuned
  mov (%r12,%r13,8),%rcx               yes               yes
  lea (%rsp,%r13,8),%r8                 -                yes   <- +1
  add $0x8,%r8                          -                yes   <- +1
                                                       ------------
                                                        +2 per row

odd-m remainder block, once per row when m is ODD
  lea (%rsp,%r13,8),%rcx               yes                -    <- -1
  add $0x8,%rcx                        yes                -    <- -1
                                                       ------------
                                                        -2 per row, m odd only

call preamble, once per call
  lea (%rsp,%r14,8),%rsi               yes                -    <- -1
  add $0x8,%rsi                        yes                -    <- -1
                                                       ------------
                                                        -2 per call
```

`safe_tuned` hoists the row base into the row header; `safe_naive` computes the
**same** base inside the block that handles the odd-`m` remainder step. **That
is why the law has two branches on `m` parity** — when `m` is odd the two
cancel and only the preamble term survives; when `m` is even `safe_naive` never
executes the remainder block and `safe_tuned`'s `+2` per row stands:

```
R3 - R2  =  2n - 2  (m even)  /  -2  (m odd)
```

Confirmed on the shipped binaries at TASK_092, residual 0 on all five:
`n024m024 +46`, `n048m024 +94`, `n024m048 +46`, `n044m044 +86`, `n010m010 +18`
(all `m` even, `2n − 2`), and `n024m023 −2.00`, `n024m011 −2.00` (`m` odd).

> **So R3's `2n` is a SPELLING cost, not a hardening strategy.** The three that
> remain are `0` (proof), `O(1)` (C's pre-loop compare) and `0` (the language's
> checks, deleted). Two of the three are zero, which is a duller result than the
> one this section shipped and is the one the machine code supports.

⚠ **C's fix is the cheapest NON-ZERO one and it is `O(1)`, not `O(table)`**:
because the limb counts are two bytes in the header, C can test the *whole*
obligation once, before it starts. p19's hardened rung had to walk 2048 bytes.
**That contrast with p19 survives intact** — it never involved R3.

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
| `controls/mkvariants.py --check` | all 8 variants still derive from the shipped sources by an exact-string substitution that applies **exactly once** | one command |
| `controls/mkvariants.py --write D` | emits the 6 spelling levers of 8b/0c, the **verifying** `v46_mutreslice` R5 of 0c, and the deliberately-broken Verus control of 6a | one command |
| `controls/census.py --mutsub` | 0c: the pinned vstd **does** specify a value-level mutable sub-slice, the mutreslice R5 verifies `21/0`, and the two disqualifiers are the TCB and the identity pin | one command, ~4 min |
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
- **The `black_box` finding in §0b is p46's own measurement, and TASK_089_REVIEW
  B2 replaced its mechanism.** The cause is not `black_box` — every probe kernel
  had external linkage, so a caller-side `black_box` could not reach its
  codegen, and the binaries are byte-identical with and without it. The cause is
  that **the probe kernel's SIGNATURE differed from the shipped kernel's**, so
  it lost the range facts the shipped kernel derives from its input header.
- **Why LLVM keeps the reslice bound test and the byte-wise limb load in
  `v46_mutreslice` but not in `r4_mutreslice`, from a textually identical exec
  source, is NOT established** (§0c). The *instruction* accounting is complete —
  `3 + 12 = 15` per row — but the pass-level cause is not, and no `-C` flag was
  bisected. Flagged, like §8d.
- **`r4_mutreslice` was not put through Miri, `check.py`, or the twin regime**,
  because it is a control and not a rung. Its R5 was verified and mutation
  tested, and nothing else.
