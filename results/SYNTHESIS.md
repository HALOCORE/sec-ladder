# What 26 kernels say about the cost of memory safety

*A cross-pattern synthesis of `sec-ladder`. Written at TASK_108 against 26 built
patterns and (at the time) 39 recorded findings; reviewed at TASK_111 and corrected at
TASK_112, which restored nine reviewed results the first pass had dropped and
fixed two blockers, nine majors and twelve minors. §7 says which, and which way
they pointed.*

> **This file is the argument. `results/synthesis.md` (lower case) is the
> numbers** — the kernel-exclusive `Ir` matrix, every pair difference with its
> licence, proof burden, trusted base, static shape and provenance. That file is
> generated from committed records by `synthesis/synthesize.py`; this one is
> hand-written and cites it. Where a table is wanted, open that file.

---

## 0. What this is, and what it can be used for

If you are deciding whether to rewrite C in Rust, or whether to put a verifier
behind the `unsafe` you already have, the question you actually want answered is
*"what does that cost?"* — and the honest answer this project reached is that
**"the cost of memory safety" is not a quantity.** It is a quantity of a **pair
of programs**, and about half the time the number you measure is not paid for by
safety at all.

That sounds like a dodge. It is not: it is the most replicated result here, it
has a mechanism every time, and it is what makes the rest worth reading.
Twenty-six kernels were built five ways each, at two optimisation levels and two
inline modes, gated, and reviewed adversarially; nineteen published claims were
retracted along the way, and **the retraction list is the most transferable
thing the project produced** (§6).

⚠ **A NOTE ON THE COUNT, so the title and the corpus can be reconciled.** The
four Results below were drawn from **26** kernels. A twenty-seventh, `p29`
(BST delete), landed afterwards and is **not** folded into Results 1–4 or into
the idiom census, which genuinely ran over 26. It appears in §7, where it
changes the corpus composition — the temporal axis goes from one row to two.
**Where this document says "26 kernels" it means the analysed set, and that is
the honest scope; the tree has 27.** Run `harness/tools/composition.py` for the
current composition rather than trusting any count printed here.

**Four results and a method.** That compression is itself a finding: twenty-six
patterns do not give twenty-six independent lessons about safety cost. The
headlines collapse; what varies pattern to pattern is the *exception*.
⚠ **It also cost this document nine reviewed results on its first pass, and the
five largest all pointed the same way — see §7.** Compression is where coverage
bias enters, and it leaves no trace in the arithmetic.

---

## 1. The apparatus, in one page

**The ladder.** Every pattern is a small C kernel — a TLV walker, a bounded
stack, a `strncpy` truncation, a bignum multiply-accumulate — implemented at five
rungs that must be semantically equivalent on well-formed input and differ only
in what enforces memory safety:

| | | |
|---|---|---|
| **R1** | C | idiomatic C99, no bounds checks, *including* the bug class the pattern models |
| **R2** | safe Rust, naive | the mechanical port: `for i in 0..n { v[i] }`. Zero `unsafe` |
| **R3** | safe Rust, tuned | same semantics, rewritten to help LLVM elide checks: iterators, reslicing, `chunks_exact`, hoisted assertions. Still zero `unsafe` |
| **R4** | unsafe Rust | `get_unchecked`, raw pointers. ⚠ **Not "correct, just unverified": at this pin an R4 must have a byte-identical R5 twin that Verus verifies** — `identity: exact` on 25 of 26 patterns and `norel` on the 26th |
| **R5** | unsafe Rust + Verus | R4's executable code, plus specifications and proofs discharging every unsafe precondition |

⚠⚠ **That R4 row is a constraint, not a definition, and it governs every
`R3 − R4` below.** Because the gate pins R4 ≡ R5, **R4 is bounded by what the
pinned vstd can express and R3 is bounded by nothing: the two classes are
incomparable, not nested.** The measured instance is p11, where the R4-side
candidate `r4_cstr` would be **−17 526 `Ir` per call (−35%)** and is rejected
with four `is not supported` errors, so the safe class reaches
`core::slice::memchr` at zero trusted items and the unsafe class cannot reach it
at all; on p16 the same mechanism runs the other way — `chunks_exact(32)` is
admissible as R3 at **zero** trusted items and needs **five** as R4. ⚠ **The
constraint holds R4 above its true floor, so every `R3 − R4` printed here is
measured against an inflated unsafe rung and reads more favourably to safe Rust
than the pattern warrants.** This is not a claim that safe Rust is cheaper; it
is a statement that the comparison is not a language fact in either direction.

Most patterns also ship **R1h**, C plus the bounds check a careful C programmer
writes, which is what separates *"C is faster"* from *"C skipped the check"*.
Those labels are used throughout, here and in the generated tables; a difference
written `R3 − R4` is *tuned safe Rust minus unsafe Rust*.

**Why `Ir` and not seconds.** The primary metric is `Ir` — executed instructions,
counted by valgrind's callgrind, reported per kernel call. It is deterministic and
reproducible to the instruction; wall clock on this box is not. Two consequences
you must carry: this project's `ns` floor is a *session* property, so **there is
no cross-pattern timing column at all**, and `Ir` and time can disagree in
*direction* (§6, trap 7). Every figure below is `-O3`, inline mode `isolated`,
kernel-exclusive `Ir` per call, unless it says otherwise.

**The two `Ir` conventions.** *Kernel-exclusive* counts instructions inside the
kernel symbol only. *Whole-program marginal* is a difference of two run lengths
and therefore includes the callees. They answer different questions and disagree
whenever the rungs dispatch different work outside the kernel symbol — ⚠ **which
is broader than "different library routines", and the two largest measured
disagreements in the tree are neither.** On p27 the `+120.33 / +130.95` gap is
the **safe side's out-of-line `drop_glue::<[Option<Box<u8>>; 32]>`**, Rust drop
glue and not a library call. On p36 the *kernel's own indirect callees* run
**512 (gcc) / 384 (clang, rustc) / 0** `Ir` per call, which **reverses** the
`match` control from dearer to cheaper and vanishes the gcc-vs-clang C gap — on
the one pattern whose kernel *is* a call. A pattern with no libc calls is not
therefore safe to difference. `results/synthesis.md` §2 prints
both and tags every row with a **licence** saying whether the two cells dispatch
the same work outside the kernel. A row tagged `NOT-LIC` is *known* to be wrong
as a kernel-exclusive difference. Four of the 26 `R3−R4` rows are not licensed.

**gcc's column carries a mitigation clang's does not.** gcc on this box defaults
to `-fcf-protection=full`, so every gcc-compiled function opens with an
`endbr64` IBT landing pad and clang and rustc emit none. It is measured, on p36,
by rebuilding with `-fcf-protection=none`: **`1.00000·nrw + 1` `Ir` per call**,
gcc's column only. **This project has been pricing a CFI mitigation all along
and did not say so.** It is one pad per call where the kernel is a single
function and `O(dispatches)` wherever control leaves the kernel, so it is small
against most of the figures below and it is never zero. ⚠ **Name it before
attributing any gcc-vs-clang gap to codegen** — including the `+5` (gcc) versus
`+12` (clang) hardening figures below, which are safe only because each is a
difference taken *within* one compiler.

**The gate.** `harness/check.py` is an 8 434-line adversarial checker each pattern
must pass: rung equivalence on committed inputs against an independent Python
model, sanitizer and Miri rows, Verus obligation counts, byte-level identity
between R4 and R5, and a hashed contract in the pattern's `spec.md` naming the
tokens each rung must spell. The tree today is 24 `PASS` + 2
`PASS-WITH-BLOCKED-ROWS`, 0 failures, 52 measurement records with 0 stale.

**The contract, and why it exists.** Early on the project published *"safe Rust
beats unsafe Rust"* three times and retracted it three times, each time because
someone wrote a cheaper spelling of one rung. The fix is a per-pattern declared
idiom, hashed into the record; what it buys is **decidability, not
singularity** — the admissible class is settleable by `grep`, and it is still a
class. Hence *"cheapest found"* below, and never *"minimum"*.

**One box.** Everything here is one container on a 2× Xeon Gold 6230 host (80
logical CPUs), glibc 2.39
(`_FORTIFY_SOURCE=3` by gcc default), gcc 13.3.0, clang/LLVM 22.1.6, rustc
1.97.1 (whose LLVM is bit-for-bit that clang), Verus `0.2026.08.09.92f466f` with
a pinned vstd. §7 says what that costs you.

---

## 2. Result 1 — the safety tax is a property of a *pair of spellings*, and the check is rarely the biggest term

### The distribution

Over the 22 patterns whose `R3−R4` row is licensed for differencing
(`results/synthesis.md` §2; re-derivable with `python3 synthesis/census.py`,
which reads that one committed file), **shipped spellings**, `-O3 isolated`,
kernel-exclusive `Ir` per call:

- **9 of 22** sit within **±32 `Ir` per call on both blobs** — p01, p02, p04,
  p08, p12, p17, p18, p22, p38. Flat in the size of the data, not a percentage.
- **4 of 22** are **negative on both blobs** — p10, p13, p18, p46: safe Rust is
  *cheaper* than the unsafe rung. Three of the four have been investigated
  (p10, p13, p46) and in each, **none of the margin is safety**; p18's search
  state is undeclared.
- **9 of 22** exceed 100 `Ir` per call on at least one blob — p03, p05, p06,
  p07, p09, p14, p19, p23, p47. These are the interesting ones, and the table
  below says what each is actually paying for.

⚠ **`9 + 4 + 9 = 22` is a coincidence, not a partition.** **p18** is in two
buckets (within ±32 *and* negative on both) and **p16** (`27 / 77`) is in none.
The sum landing exactly on the row count is what makes that easy to miss.

⚠⚠ **AND THE WORD "SHIPPED" IN THAT HEADER IS DOING MORE WORK THAN A READER
WILL GIVE IT. Four of the 22 rows have a measured, verifying, in-contract
counterpart on the R4 side, and applying the record moves three of them out of
their buckets — every one of the four against safe Rust:**

| row | shipped | against the cheapest admissible R4 found | bucket |
|---|---|---|---|
| **p22** | `+2.00 / +2.00` | **`+125.00 / +1021.00`** — `r4_reslice`, in contract, `20 verified, 0 errors`, byte-identical to its own R5 at `-O3`. **510× on the large band** | flat → **>100** |
| **p13** | `−177 / −1054` | **`+44.00 / +77.00`** — a bounded unchecked consumer, `19 verified, 0 errors`, no new trusted item. **Sign flip** | negative → **no bucket** |
| **p12** | `+3.00 / −26.00` | **`+20.00 / +66.00`** — route A, `15/0`, twin `18/0`, `identity exact`, 17.00 / 92.00 cheaper. **Sign flip on `large`** | flat → **no bucket** |
| **p10** | `−323 / −603` | **`−129.00 / −241.00`** — `u_win`, `10/0`, no new trusted item: **60% of the margin was R4 spelling** | negative (unchanged) |

**So the distribution at the searched values is `7 / 3 / 10`, with p12 and p13
joining p16 in no bucket at all** (`synthesis/census.py` arm C). ⚠ **p22's is
the sharpest, and this document already carried it 400 lines away without
noticing**: §6, trap 1 gives the 510× as one of five headlines published in the
flattering direction, while §2 went on quoting the figure it corrects.
⚠ **Neither number is the "true" one.**
The project's rule is *never re-ship a rung because a cheaper in-contract
spelling was found*, so the shipped cell is published as a **fixed-R4 bound**
and the counterpart beside it; a reader who wants one number is asking a
question the record declines to answer.

⚠ **The two rows that move the other way are both R3-side, and that asymmetry is
the point.** p17's in-contract R3 respelling is **−19.00** flat against the
shipped R4 (byte-identical to a row an earlier task had excluded), and p06's
`c_idx` is `+80 / +187` against a shipped `+334 / +172`. **The R3-side levers
cost zero trusted items and are easy to find; the R4-side levers have to clear
the prover** (§1). That is why the unsearched side is systematically the unsafe
one, and why the errors run systematically one way.

⚠ **p17 stays in the flat bucket and its label still needs one qualification.**
`+32 / +32` is literally what p17's two shipped blobs measure. What is retracted
is `+32` **as a law**: both shipped bands happen to sit at `nsuf = 3`, and swept
over `nsuf` 1–8 the same difference runs **18…63**. "Flat across p17's two
blobs" is true; "flat in the size of the data" is what a reader takes from the
bucket, and for p17 that is the retracted sentence.

**Always quote R3.** The naive rung R2 is dearer than the tuned one by a median
of **7.26×** across the 17 licensed rows whose `R3 − R4` is positive on `large`
(p05 is the 9th of 17), running from **−1.37×** (p47) to **3 536×** (p08, a
`memmove` idiom R2's indexing defeats) with 3 323× on p04. ⚠ **Three of the
seventeen are not overstatements at all** — p47 (−1.37×), p09 (0.74×) and p14
(0.86×) have R2 *cheaper* than R3, and on p09 that is the documented
reslice/load-merge hazard rather than noise. ⚠ **The `1.05×` low this document
used to print is p27**, a `NOT-LIC` row this section's own licence rule
excludes — the range and the median were being taken over two different
populations. ✅ **And the median is the robust half of this, measured**: apply
all four searched R4s from the table above and p22's own ratio collapses from
1 033× to **2.02×** while p12 and p13 enter the population, and the median does
not move — still **7.26×**, now the 10th of 19. **Quote the median, not the
range**, and do not quote any single row's ratio without its search state. What
survives: a benchmark that ships R2 as "safe Rust" is not measuring safety, it
is measuring whether anyone tuned it.

### Where the number is ~0, the mechanism is always visible

That claim is stronger than it sounds, so here are the mechanisms, including for
two rows this document previously listed in the flat bucket and left unexplained.

- **p16** (TLV walker, data-dependent bound, nothing hoistable): the per-byte
  safety tax is **0.00000 `Ir`/folded byte** — a *matched-spelling* difference
  swept over 127 consecutive record lengths at six fold spellings, slope
  `0.0000000`, max residual 0.00. The mechanism is why it cannot be otherwise:
  the reslice (R3) and the `get_unchecked` (R4) both sit **outside** the fold
  loop, so the chunk body is mnemonic-identical at K = 4, 8, 16, 32, 64.
  ⚠ Only the *matched* difference is a property of the kernel: p16's bare rate
  ranges 5.04688…6.62500 in contract, one exact-string substitution apart.
- **p46** (bignum multiply-accumulate) is the sharpest instance, because the
  boundary did not shrink — it **vanished**. `n` and `m` are `u8`-derived and
  `n + m <= OUTCAP` is tested, which is everything LLVM needs to discharge
  `i + j < 96` itself: it deletes **all three** bounds checks, and the safe
  multiply-accumulate loop contains no conditional branch but its own `jne`. The
  ordering is `safe_naive` **6241 / 23341** < `safe_tuned` 6287 / 23435 <
  `unsafe` **6406 / 24250** (kernel-exclusive, small = *n*=*m*=24, large =
  48,48). Rolled against rolled, shipped sources unedited,
  `R2 − R4 = +2.00000·n·m` exactly over five shapes — **against** safe Rust. So
  "safe beats unsafe" here is **100% an unroll decision** and 0% a check.
  ⚠ PROVISIONAL (TASK_092, unreviewed), and contingent on p46's byte-identity pin
  and trusted-base count: relax either and it inverts.
- **p01 / p02**, the calibration pair: tuned safe Rust is **+4…+5** instructions
  per call on p01 and **+11** on p02 against unsafe, flat in the size of the
  data. Hardened C's own check is **+5** (gcc) / **+12** (clang), also flat —
  which is the comparison that matters, and it says safety costs about the same
  in both languages, with Rust making it non-optional. (⚠ p02's figure reads
  `+10` in `RECAP.md`. That is a **whole-program marginal at 61 B / 4092 B**, a
  different convention *and* a different input pair; kernel-exclusive on the
  shipped blobs it is `11.00 / 11.00`.)
- **And on p01 `large` the two backends land on the same instruction count
  exactly.** `c-clang` and `unsafe` Rust both execute **143 740 000** kernel
  instructions — not approximately, the same integer, from
  `results/p01-array-sum.json` — which is the cleanest *"Rust codegen is C
  codegen"* datapoint in the tree and the reason every C-vs-Rust claim here
  needs a clang column. ⚠ **Two conditions.** It is `large`-only: on `small` the
  same pair reads 180 000 000 against 180 200 000. And it is a statement about
  *one backend*, because rustc 1.97.1's LLVM is bit-for-bit clang 22.1.6's;
  `c-gcc` on the same row is 205 180 000, and gcc's column additionally carries
  the `endbr64` term §1 names, which neither of the other two pays.
- **p04** (ring buffer, `+5.00 / +5.00`) is flat for a reason that is an
  *operator* property and not a safe-Rust one: `urem x, C` gives LLVM
  `x < next_pow2(C)`, and **`next_pow2(CAP) ≤ ARR_LEN` is necessary for elision**
  — sufficient too, absent a cursor-relating guard. Zero fitted parameters, and
  it reproduces on capacities p04 never built (`% 32` into `[u64;64]`, `% 64`
  into `[u64;96]`: both elide). ⚠ **Turn the dial and the row stops being flat:**
  at `RING_CAP = 60` the same `R3 − R4` goes **+5 → +479**, p03's dead clamp
  takes it back exactly, and three middle-ends agree in both directions. **The
  operator, not the language** — and the qualifier is load-bearing, because
  `% 60` into `[u64;64]` *with* p04's two guards keeps the load check.
- **p12** (fixed-size `strcat`, `+3.00 / −26.00`) is flat because the bulk-copy
  lowering survives, and the rule is sharper than "use `copy_from_slice`": a safe
  byte loop with **no bulk call anywhere in its source** also lowers to `memcpy`,
  and checking only the *source* per byte kills it just as dead as checking the
  destination. **Both ends of the copy must be free of a per-iteration check.** A
  consequence worth carrying: `R2 − R4` has no per-byte law here at all — R2
  alone is exactly linear at 24.75 `Ir` per copied byte, and the non-law is
  entirely R4's `memcpy` size dispatch. ⚠ **And p12's `−26.00` is a fixed-R4
  figure**: the review built a cheaper admissible R4 (verifies 15/0, twin 18/0,
  `identity exact`) that is 17.00 / 92.00 cheaper, which **flips the sign on
  `large`** to R3 being +66.00 dearer.

### Where the number is large, name what you are paying for

**"The bounds check costs X" is almost never the right sentence.** Pattern by
pattern, for the nine licensed rows above 100 `Ir`/call — plus **p22**, which
joins them at the searched value above and would otherwise never get a mechanism
at all:

| pattern | `R3−R4`, small / large | what it is actually paying for |
|---|---|---|
| p03 bounded stack | 359 / 626 | the check — **and a one-line dead clamp deletes 100% of it** on both sides |
| p05 index flatten | 123 / 399 | a hoisted per-row trip count and a scalar epilogue; blocked by **nonlinearity** |
| p06 rotate | 334 / 172 | **none of it is a bounds check** — `zip`/`Rev` adaptor exhaustion tests |
| p07 binary search | 3 015 / 10 025 | the check, genuinely, with **no axis along which it amortises** |
| p09 bitset | 13 756 / 48 885 | **the checks, and it is the one row where that is established rather than assumed** — see below |
| p14 field split | 638 / 425 | R4's foreclosed unroll: the tax moves 6.456 → 3.506 `Ir`/line byte at constant input size |
| p19 state machine | 260 / 4 100 | `1.00 Ir`/byte is **one `and $0x7,%edi`** — a mask, not a check |
| p22 hash probe | 125 / 1 021 | **the unsafe rung's missing reslice.** `R3 − R4ship` is `+2.00` flat; the whole `1·nkw` term appears only because the shipped R4 addresses keys off `buf` at `off + p` where both R3 and the admissible `r4_reslice` address them off `w`. **None of it is a bounds check** |
| p23 partition | 306 / 444 | the **data's shape** — see the rank note below — and ≥150 `Ir`/call of the safe side is spelling |
| p47 constant-time compare | 90 / 142 | the constant-time discipline; R2 is *cheaper* precisely because it leaks |

⚠ **p23's two numbers ship without their domain, which is p23's own rule.** Band
K holds *every* size regressor fixed — `m = 32`, `nrec = 8`, 256 copied bytes
per call — and sweeps only the pivot's rank, while the size-based law predicts
416.32 for all seven points. `306 / 444` are two draws from that curve.

⚠⚠ **AND THE SWING ITSELF WAS OVERSTATED BY 9×, CORRECTED AT TASK_117 AND
RE-MEASURED BY THE MANAGER.** Between the **shipped** spellings `R3 − R4` runs
`706.37` at rank 0.03 down to `227.00` at rank 0.97 — a `3.11×` swing — **but
against the cheapest IN-CONTRACT safe rung the same shipped unsafe rung gives
`172.64 … 227.00`, a `1.315×` swing.** The difference is a spelling term of
**exactly `2·dn − 2·recs`**, which runs `480.00 → 0.00` across the band and is
therefore **collinear with the very axis being measured**. ⚠ **Quote `1.315×`
and a `54.36 Ir`/call swing.** ⚠⚠ **The mechanism attribution inverts with it:
regressed against the shipped pair the swing tracks the cursor split (`R² 0.987`)
and not the swap count (`0.013`); against the in-contract pair the two SWAP
PLACES (`0.0001` and `0.993`).** **The shape effect is real at fixed size; its
size and its cause were both properties of one spelling.**

**p09 is the counter-case, and it is the one to lean on.** Its `R3 − R4`
decomposes over **three checks with zero free parameters** — every coefficient is
a loop-body instruction count read off the listing — and out of sample it
predicts `large` to within 1.13 `Ir` of 73 404, with `R3 − R4` **predicted
48 885.00 against measured 48 885.00**. ⚠ **This document previously said *"half
is a lost 8-byte load-merge idiom, not deleted checks"* and that attached a real
number to the wrong quantity.** p09 has two "half" statements and neither is
`R3 − R4`: one is half of the *`m_clampb` control's* win (the p03-style seeding
probe, 49% on `small` and 47% on `large`), and the other is the `+21 lost merge
/ +1 spill / −5 cheaper query checks = +17 net` decomposition of the **R3-vs-R2
inversion**. p09 is the largest `R3 − R4` in the tree and it is the row where the
checks *do* account for it.

Four mechanisms in this neighbourhood generalise past their own pattern, and
p11's is here even though its row is `NOT-LIC` and negative.

**p03 — the tax is the price of the optimiser failing the invariant the proof
proves.** Take the tuned safe rung and add a *dead* `if sp > STACK_CAP { return
0; }` — R5's own invariant, handed to LLVM as unreachable code. Safe goes 17 → 13
`Ir` per executed pop, unsafe 14 → 13: **gap exactly zero on both sides, zero
fitted parameters**. It is the invariant specifically and not range propagation
(`sp > 1000` changes nothing; `sp > 65` leaves the check standing *and* is
dearer). And it is **not Rust-specific**: clang and gcc each keep a manual C
bounds check at 4.00000 `Ir` per executed pop and *both* delete 100% of it given
the identical clamp, byte-identically. LLVM does eventually derive the fact, so
this is analysis **seeding**, not inability.

**p11 — the same check costs a different amount depending on what the loop
already holds.** A NUL scan decomposes three ways off the listing: **12.0× is the
library** (C's `strlen` reaches an IFUNC-dispatched AVX2 routine at 0.078125
`Ir`/byte against `core::slice::memchr`'s SWAR 0.937500), **5.3× is which Rust
spelling**, and **3.00000 `Ir`/byte is the bounds check** — where the naive report
would have been one ratio. The 3.00000 is the finding, and the control that
isolates it is **inside p11**, one loop at a time: p11's own fold measures
4.25000 and p11's own scan 3.00000, both exact, residual a constant. A bounds
check costs **2.00 `Ir`/byte when the loop's induction variable already holds the
address being checked and 3.00 when it does not**, and which one you get is
decided by the loop's *other* exit test — the fold hoists `add %rdx,%rax` out, so
its bound test is `cmp; jae`; the scan must keep `%rbx` window-relative because
its own exit test is `q < len`, so the check has to `lea` first. (p16 and p17
reproduce the 4.25 and its 2.00 + 2.25 split; they are not what separates 2 from
3.)

**The check's second half, on five kernels.** Where a per-element check does
cost, the split is stable: **4.25 `Ir`/element = 2.00 check + 2.25 foreclosed
unroll**, with zero residual on p16, p17, p05, p11 and p14, and on p19 as
`6.25 = 3.00 + 3.25`. A rolled-vs-rolled control (`-unroll-count=1`, a
bit-for-bit no-op on the safe rung) isolates the halves. ⚠ **The counterfactual
is not what it looks like**: forcing LLVM to unroll the *checked* loop recovers
**0.50, not 2.25**, because four copies need four exit tests. So the right
sentence is the stronger one — **the check does not merely cost 2.00, it
forecloses an optimisation worth 2.25 that it could not have amortised anyway.**

**p07 is the honest counterexample and should be quoted as one.** Binary search:
`Θ(log n)` probes, no inner loop, nothing to hoist and nothing to vectorise. The
tuned safe rung costs **6.0000 `Ir` per probe** more than the unsafe one, with
`probes = nq·⌈log₂ n⌉`, so its share of kernel `Ir` *rises* in both the array
size and the query count — 42.53% →
46.63% over `n` = 7…16 385, with an asymptote in **[46.15%, 50.00%]**, confirmed
across six deliberately different query distributions. Every other pattern's tax
amortises along *some* axis. p07's amortises along nothing. If you want one
number for "safe indexing where the optimiser cannot help you", it is this one,
and it is roughly half the kernel.

### The three results that are easy to get backwards

**A percentage can be wrong in SIGN at the other input (p19).** Safe Rust's
bounds check and C's validation pass are the *same predicate at different
asymptotics*: LLVM lowers the `tbl[…]` slice check to `cmp $0x8`, a state-range
test on `st` before the index is even built, while the C rung emits
`cmpb $0x7,…; ja` four times in a validation loop. Validation is `O(table)`
**once per call**; the bounds check is `O(message)`. So the buggy C rung is
**5 071 `Ir`/call cheaper than unsafe Rust at `small` (m = 256)** and **3 569
dearer at `large` (m = 4096)** — `2.25·m − 5647`, crossing zero at
m ≈ 2 510, between the two shipped blobs. ⚠ **Any percentage quoted at either
input is wrong in sign at the other, and nothing in that reversal is safety.**
(Both figures are `c-gcc` minus `unsafe` off `results/synthesis.md` §1:
`2831 − 7902` and `45071 − 41502`. gcc's side additionally carries the `endbr64`
term of §1, which is small here and not zero.)

⚠ **This is the trap a decision-maker walks into**, because a benchmark
publishes the input it happened to build and a reader generalises the ratio.
Ask for the crossing point, or for two inputs on opposite sides of it.

**A bound is worth more than the check costs (p13).** `strncpy` truncation:
72% (`small`) and 90% (`large`) of the published safe-beats-unsafe gap is the
downstream *consumer scan*, and its direction is the reverse of the obvious one —
**a consumer whose bound LLVM can see fully unrolls to 2 `Ir`/byte; an unbounded
walk stays a 4-instruction loop at 4**. ⚠ **The discriminator is the BOUND, not
the check**: an *unchecked but bounded* scan costs exactly what safe `position()`
costs, to the instruction. A bounds check is one way of supplying a bound and is
not what is paid for. And the sign does not survive symmetry — allow the unsafe
rung a bounded unchecked consumer, which verifies `19 verified, 0 errors` with no
new trusted item and is excluded by nothing but the pattern's own English, and
the shipped difference becomes **+44.00 / +77.00**.

**The lifetime guarantee costs zero (p27).** The first temporal bug here: a
handle table over per-record `malloc`/`free`, with C omitting one conjunct on the
read path. ⚠ **This one pair is quoted in the other convention and the document
says so here rather than letting the reader assume:**
`R3 − R4 = +230.07 / +792.75` is a **whole-program marginal**, because the
decomposition below is a whole-program one; **kernel-exclusive, the same pair
reads `+109.98 / +661.82`**, so the marginal is 2.09× the figure §1's banner
otherwise promises. **None of it is temporal safety** either way —
a decomposition closed over *every* function gives `230.07 = 109.65 kernel +
120.42 drop glue + 0.00 allocator`, with `malloc`, `free`, `_int_malloc`,
`_int_free` and all three `__rust_*` equal to the last digit between the rungs.
The spatial tax even runs backwards: an unsafe rung that *keeps* safe Rust's
bounds checks costs +153.51 against safe Rust's +109.65. **`allocator = 0.00` is
three-for-three** across the patterns that measured it, and on one probe the safe
drop glue is *cheaper* than a hand-written recursive free. ⚠ This pair is
`NOT-LIC` in `results/synthesis.md` §2; the decomposition is p27's own, from
callgrind's caller→callee edges, not read off that column.

> **The lifetime guarantee's cost is zero and its shape is structural: the free
> and the invalidation are ONE operation in safe Rust and TWO in C, and the bug
> is neither of them going wrong — it is the THIRD, the *asking*, going missing.**

### The caveat that governs this whole section

**Two caveats, and they are different things.** The first is *search depth*:
`R3 − R4` differences two rungs **searched to wildly different depths**, and
every time a side has been searched properly the number moved a long way. In
`results/synthesis.md` §2's own search-state column, **14 of 26 patterns print
`undeclared`**, three more owe a span, and **nine** report a real search on at
least one side. Of the nine: p10's −323/−603 became −129/−241 against a
verifying R4 candidate; p13's −177/−1054 became +44/+77, a sign flip; p12's
−26.00 became +66.00, another; p22's `+2.00` became `+125/+1021`; p17's
`+32/+32` has an in-contract R3 respelling at **−19.00** flat; p36 refuses to
publish a single number at all. **So part of
what that column measures is search effort**, and any single row should be read
as a bound with one endpoint held fixed by fiat, not as a property of the
pattern.

The second is **§1's R4 constraint, and it is stronger**. Search depth says
nobody looked hard enough; the R4 ≡ R5 pin says **one side is not allowed to
look** — p11's `r4_cstr` was found, measured at −17 526 `Ir`/call, and refused
because the prover cannot type it. A reader who corrects for search effort has
still not corrected for that.

---

## 3. Result 2 — where safe Rust does not help

This is the section a reader deciding anything needs most, and it is the one the
project itself under-told. Memory safety is a *specific* property. Here are the
measured places where the safe rungs buy nothing, arranged by why.

**The bug is in bounds.** p09's bitset indexes `words[q >> 6]`. Change it to
`q >> 5` and memory safety alone catches it on every input. Change it to
`q >> 7` — one character, in the same position — and **nothing catches it**: no
bounds check, no ASan, no UBSan, no Miri, no memory-safety proof. `q >> 7` is
`q/128 ≤ q/64`, so under the pattern's own guard it is always a legal word index.
The memory-safety-only proof gives `19 verified, 0 errors`; it costs **zero
instructions** (6691.70 against 6692.30); the whole 368-byte unsafe kernel differs
in **one byte**; all five builds print the same wrong answer on the pattern's
headline blob. It is a **class of at least nine**, not an instance. p04 repeats it
on a *container* — drop the ring buffer's fullness check and a push overwrites the
oldest element with **no out-of-bounds access at all**, verifying `9/0` against
five positive controls that correctly fail — and the memory-safety-only
configuration turns out blind to *every* functional change, not just that one.
p06 adds the write case: for one regime of the rotate amount, C, safe Rust,
unsafe Rust and the *proved* rung all print the same wrong answer, ASan and
UBSan clean.

**The bug is a read the program is entitled to make.** p17 ports CVE-2017-7529,
a suffix-range parser missing `start >= 0`. Guard the *slice*-relative index —
exactly what a bounds check buys, no more — and Verus gives `9 verified, 1
error`, the single error being the *functional* invariant; **every access
obligation discharges** (`10/0` with the functional spec stripped). The program
then reads a neighbouring window's bytes: output tracks the victim's secret, no
panic, no `unsafe`. **A provably memory-safe program that leaks.** Memory safety
and correctness are different properties, and this is the measurement.

**The bug is UB that is not memory-unsafety.** p18 removes a LEB128 decoder's
shift bound. It touches no memory and **ASan is silent**. Safe Rust with the
guard deleted — zero `unsafe` — at `-O3 -C debug-assertions=off` is
**bit-identical to C on every adversarial blob**. Four things do catch it — UBSan,
`-C debug-assertions`, Miri and Verus — and **every one is outside the measured
matrix**. (Miri reports it as a *panic*, not as a `Undefined Behavior` finding,
so a gate keying on the UB flag calls it clean.)

**The bug is non-termination.** p22, an open-addressing probe loop that never
terminates on a full table: memory-safe, ASan and UBSan silent, Miri silent for
90 s. No bounds check, no lifetime, no `unsafe` to point at. **The safe rungs are
not better; only R5 sees it.** Stated at its honest width: *nothing on this
ladder emits the capacity check — five rungs write it by hand*, and the bounded
spelling that terminates is measurably a **different function**.

**The bug is in the trace, not the value.** p47, constant-time compare. Take the
verified rung and add an early exit: `14 verified, 0 errors`, the kernel's
obligation count **unchanged**, identical checksums on all 32 cells, and
**+7088.000 `Ir`** of leak. The diff touches no `requires` and no `ensures` — the
contracts are *identical*. **A property of the trace is invisible to a logic
about the value.**

**The structure recycles its own storage.** This one is a rule, not a pattern,
and it is reviewed and independently re-run:

> **Safe Rust's temporal guarantee is a guarantee about the ALLOCATOR. A
> structure that RECYCLES ITS OWN STORAGE gets no guarantee at all.**

A slot free list owns its storage throughout, so nothing is freed and there is
nothing for the guarantee to attach to. Under `#![forbid(unsafe_code)]`, zero
`unsafe` tokens: use-after-recycle reads the recycled node's value, and a slot
double-free yields two aliased handles — both silently wrong, both **Miri-clean
in all three modes**. A generation tag does **not** rescue it, because the bump
is a hand-written second store: exactly the one C omits.

**One safe spelling leaks where an equally safe one does not, and there is no C
side to compare it against.** ⚠ PROVISIONAL, from a refused row: `Rc` in both
directions of a doubly linked list is a cycle and leaks (Miri: five
`memory leaked` lines); `Weak` for the back pointer does not (zero). Both are
safe, both compile, and the leaking one is the spelling a hurried programmer
reaches for. ⚠⚠ **The obvious headline — *"safe Rust can be worse than C"* —
is a refused claim and is not made here.** It was refused because `Weak` is
equally idiomatic and measured leak-free, so the headline would survive only if
`Rc`-both-ways were pinned as *the* safe spelling, and it is not; and because
**no C rung was ever built and no cost axis was ever measured** — the entire
evidence base is two *Rust* spellings under Miri. Read it as a warning about a
spelling.

### The other side of the ledger, and one of the three is measured

A reader who stops at the paragraphs above has the wrong impression, and the
correction is owed in the same units.

**The measured one: p02, the one-byte heap overflow.** The kernel copies a
record into a fixed destination; `adversarial-cap1.bin` sets `len = cap + 1 =
65`, so the destination bound is the only thing violated, by one byte. Idiomatic
C prints `198979479034752` and exits 0 in **seven of eight builds** — the
overflow lands inside glibc's chunk rounding, a 64-byte request having 72 usable
bytes, so nothing is corrupted and nothing is detected. The eighth build aborts,
and **that abort is the distribution's `_FORTIFY_SOURCE 3` default rather than
the program**: as hardening it catches *1 of 8 builds of 1 of 3 attacks* here.
Every Rust rung and hardened C returns `0`. **The control is what makes it a
measurement rather than an assertion**: delete the bound test from
`patterns/p02-buffer-copy/safe_naive.rs`
and nothing else, and the rung prints C's checksum bit-for-bit on well-formed
input — the same program — while on the adversarial blob it exits 101 with
`index out of bounds: the len is 64 but the index is 64`. So *"Rust makes the
check non-optional"* is measured, not assumed.

⚠ **Its scope, which the sentence above needs.** R2–R5 all carry the same
three-term rejection test hardened C does, so **no shipped Rust rung ever
reaches its own bounds check on any p02 input** — the panic belongs to the
deleted-check control, not to the matrix. And of p02's three adversarial blobs
this is the one that behaves this way: the 65 535-byte overflow aborts loudly
because it destroys the next chunk header, and a third blob is silently wrong on
**eight** of eight builds in C. The one-byte case is the realistic one and it is
the invisible one; that is the whole of the result.

**And two that are real and unpriceable.** p08's overlapping `memcpy` is a bug
safe Rust **cannot express** — the borrow checker rejects it at compile time, so
there is no runtime check and nothing to measure. And p38's strict-aliasing
miscompile is the first bug class in the tree that **unsafe Rust does not
reintroduce either**: Rust has no type-based aliasing rule at any rung. Both are
unambiguous wins, and **neither is visible in any `Ir` column** — which is §5's
point arriving early.

**p38 does have a price, and it runs the opposite way to the usual story.** Seven
one-line neighbours of the shipped C kernel were built and measured beside it in
one invocation, at `-O3 isolated`, whole-program marginal `Ir` per call on
`small.bin`: **the undefined spelling is the dearest of its defined neighbours on
gcc.** Six defined spellings are cheaper — **five by exactly 6.00 `Ir`/call**
(`c_symset`, `c_once`, `c_nosa`, `c_memcpy`, `c_union`, all at 1037.72 against
the shipped 1043.72) and one by 2.00 (`c_noback`) — and three of them
(`c_symset`, `c_once`, `c_noback`) each remove a *different* one of the four
conjunctive conditions the miscompile needs. On clang it is not a win
either: `c_once` is 8.00 cheaper, `c_noback` 7.00, and the other four are
**byte-identical** to it. **The undefined behaviour buys nothing and costs 6, so
no optimising programmer arrives here by optimising** — which is also why p38
ships labelled a *demonstration kernel* rather than a claim about prevalent code.
⚠ **The one defined spelling that costs more is `c_halves` at `+12.00` (gcc) /
`+32.00` (clang) — the two-half read the Rust rungs are forced into.** So the
sentence is *"the UB is not a speed win"*, not *"safety is free here"*.

⚠ **The count, said plainly, because the shape of this section is itself a
finding.** Seven entries above where the safe rungs buy nothing, one measured
case where they buy the whole bug, and two wins with no cost axis at all. That
ratio is a property of *which patterns were built* — the catalogue was written
around bug classes a five-rung ladder can price, and a bug class safety prevents
outright has nothing to price — so it is not a score. Read the entries, not the
tally. **This document dropped the p02 entry entirely in its first version**, and
that omission ran the same way as every other one it made (§7).

⚠⚠ **AND ONE MORE PLACE, MEASURED LATE AND ARRIVING FROM OUTSIDE THE CATALOGUE:
SAFE RUST'S IDIOMATIC ESCAPE IS OFTEN `Vec::push`, WHICH DELETES THE BOUND
RATHER THAN CHECKING IT.** **Found while triaging a CVE candidate whose safe
rung appeared to come out not merely *safe* but *CORRECT* where C was
exploitable.** ⚠ **It was an artefact, and the arm that proved it is worth
copying: perturb the term you are pricing and ask whose behaviour MOVES.**
**Six of eight arms changed — C from an ASan heap write to silent, the panicking
safe rung to correct, the unsafe rung from Miri UB to clean — and BOTH
`Vec::push` arms were UNCHANGED, because the `Vec` simply reallocated from
capacity 4 to 8.** ✅ **A fill-controlled variant grows too, so it is the idiom
and not `with_capacity`.**

⚠ **The consequence for a reader is not that `Vec::push` is wrong — it is
usually right, and it is genuinely why the bug cannot occur.** **It is that a
rung which grows its destination IS NO LONGER RUNNING THE SAME PROGRAM, so any
number taken across that boundary prices a REPRESENTATION CHANGE and not a
safety property.** **This is the same trap as `p27`'s forced `(slot, gen)`
handles, where it was the pattern's whole point rather than a defect** — ⚠ **the
difference is whether the representation change is FORCED by the language or
CHOSEN by the porter, and only the first is a result.**

---

## 4. Result 3 — a proof discharges exactly what it says, and the numbers beside it say less than you think

### What a proof costs: zero

**`R5 − R4 = 0.00` on 26 of 26 patterns × both blobs** (`results/synthesis.md`
§2). ⚠ Do not cite that column as the evidence: at `-O3` the gate pins
`identity: unsafe ≡ verus, exact` on 25 patterns, meaning the machine code is
byte-identical, so the `Ir` zero is *entailed* and is a tautology. **The evidence
is the raw-byte digest**, checked at both optimisation levels since the pilot.

One scope clause, measured on p36: a `spec fn` declared in a **trait** is
codegenned as a stub and occupies a vtable slot in every implementing type. The
proved binary's vtables are 40 bytes to the unproved one's 32, and all eight
slot-4 entries point at one 26-byte emitted stub. **Zero executed instructions
and zero in the kernel symbol still hold** — but *"ghost code fully erases"* and
*"the proven binary is byte-identical"* are false there, and the *declaration
position* is part of the vtable ABI.

### What a proof buys: only if it licenses unsafe code

Proving *safe* Rust panic-free leaves every bounds check in place — rustc never
learns what the solver knew. The payoff arrives only when the proof licenses
`unsafe`, which is what R5 is: R4's machine code with the obligations
discharged. This is the whole reason the ladder has five rungs and not four.

### What a proof forbids, and it is priced

§1's R4 constraint has a cost, and on p36 it is measured to five decimals.
**Verus at this pin cannot type `fn(u64) -> u64` at all** — the error is on the
*declaration*, not on the call — so C's own dispatch mechanism has no admissible
Rust rung, and all four Rust rungs use `[&'static dyn Op; NOPS]` instead. The
difference is **exactly `3.00000` `Ir` per dispatch**, same intercept, zero
residual over twelve swept points, with a mechanism read off the two listings and
no fitted parameter. ⚠ **Finding 14's other instances exclude a *spelling*; this
one excludes a *mechanism***, and it is the reason p36's `R3 − R4` is not a
statement about bounds checking at all. A second, smaller instance sits on p47:
`u_win` is 24.000 `Ir` cheaper on both blobs, verifies with no new trusted item
and no lemma, and is excluded **by the identity level alone** — `md5_raw`
differs where `md5_raw_norel` matches.

**So the honest form of "what a proof costs" is two numbers, not one:** zero
instructions for the proof itself, and whatever the pin's expressiveness costs
you in the rung you are then allowed to write. This document can only price the
second where somebody built the excluded rung and measured it, which has happened
on three patterns.

### What a proof does not buy: a family of three

> **The proof discharges exactly what it says, and the program is still broken.**

1. **p47** — the proof certifies a **leaking** kernel, under an *identical*
   contract, with the obligation count unchanged.
2. **A termination proof does not bound the stack.** A recursive kernel with
   `decreases buf.len() - i` verifies `3 verified, 0 errors`; the compiled binary
   at depth 10⁶ prints `fatal runtime error: stack overflow, aborting`, `rc=134`.
   ✅ TASK_102 has since been reviewed (TASK_113), which disputed Result 4's
   criterion but did NOT attack this limb; it stands.
3. **p42** — an affine deallocation token does not force deallocation. An R5 that
   forgets the error path's `deallocate` verifies with 0 errors, because
   `Tracked<Dealloc>` is **affine, not linear**: a proof may simply drop it.

⚠⚠ **p42's membership is UNCONDITIONAL, and its REASON has now been retracted
TWICE. It is the most instructive item in this document and the least safe to
paraphrase.**

**The sequence, because the sequence is the result:**

1. Published: *"the first pattern whose R5 does not cover its own bug class —
   Verus at the pin cannot state leak-freedom."* Landed in the authoritative
   layer. **Refuted by its own review within hours.**
2. Replaced by: *"escrow the token into a tracked `Map<int, Dealloc>` whose
   domain must return empty and the property is stated exactly"* — `18 verified,
   0 errors`, zero new trusted items, machine code identical to the shipped rung.
3. ⚠⚠ **REFUTED IN TURN (TASK_116, and re-run independently by the manager). THE
   LEDGER'S `ensures` IS SATISFIED BY A LEAKING PROGRAM.** Substitute
   `proof { let tracked _dl = led.tracked_remove(0int); }` for the error path's
   release and it still verifies **`18 verified, 0 errors`** (`21/0` under the
   twin) with **obligations, twin count and axioms all unchanged**, while leaking
   exactly `n_err × win_len`. ⚠⚠ **Its `-O3` kernel is byte-identical to the
   shipped unsafe rung with p42's own bug planted in it.**

**The mechanism is one sentence: `Map::tracked_remove` is the call the release
itself makes, so wrapping an affine resource in a map does not make it linear —
it makes the drop take one more line.**

⚠ **What this does NOT say.** It does **not** reinstate (1). **One encoding is
refuted; inexpressibility is not proven and remains open**, with privacy-scoping
the live lead — a module-local receipt is forgeable in proof mode, a
privacy-scoped one is not. ⚠ **Do not cite p42 as evidence that a prover cannot
express a resource property, and do not cite it as evidence that a ghost ledger
can.** (Clean negative that survived: there is **no linear must-consume tracked
mode at this pin** — 22 verifier attributes, none of them one. So the repair
cannot come from an attribute; it has to come from Rust-level privacy.)

⚠⚠ **AND THE PART THAT GENERALISES BEYOND p42: NOTHING IN THIS PROJECT'S GATE
CHECKS THAT AN `ensures` MEANS WHAT ITS PROSE SAYS.** The gate was green, the
record reproduced, the obligation count was pinned and matched, the twin count
matched, the byte-identity pin held — **and the central positive claim was
false.** ✅ **The shipped tree was safe regardless, and the reason is worth
stating plainly: the identity pin catches the attacked R5. The pin protected the
pattern, not the proof.**

The rule that survives all three: **before claiming a proof covers a bug class,
ask which resource its obligations quantify over — and then ask whether a
different encoding would.**

### The obligation count does not tell a reader what the proof covers

This is the sharpest and least comfortable finding in the section, because the
count is the number every paper reports. Delete the p42 ledger's leak-freedom
`ensures` and it **still** gives `18 verified, 0 errors`. p47's leaking kernel
leaves the obligation count at 3. **The obligation is load-bearing for the
program and not for the count** — which is exactly the gap a reader assumes the
count closes. Only a textual pin in the pattern's contract catches its removal.

### The trusted base is the number to look at, and it needs prose beside it

Across all 26 patterns: **108 trusted items, 230 trusted lines, 0 pattern-local
axioms** (`results/synthesis.md` §3, counted as distinct `(source, name, line)`
triples, not as a column sum). Four things a reader must know before using that:

- **A `0` in the axiom column does not mean the tree rests on no hand-written
  axiom.** All 26 verified sources carry `broadcast use`, and
  `vstd::slice::group_slice_axioms` alone is six `broadcast axiom fn`s in the
  pinned standard library. Every number here rests on hand-written axioms; they
  are vstd's, they are pinned, and they are outside the column by construction.
- **A proof of a `requires` is not a proof that the trusted body honours it, and
  the gap is invisible.** Substitute `copy_nonoverlapping` for `copy` inside
  p08's trusted `move_right` — a body whose entire safety contract *is* the
  non-overlap, and which then commits the pattern's own undefined behaviour — and
  it verifies `11 verified, 0 errors` shipped and `15/0` under the verified twin.
  Invisible to Verus, to the twin, and to the textual contract pin. What catches
  it is **Miri** and the R4/R5 byte-identity check.
- **The verifier's own escape hatch is vacuous.** The `assume_specification` form
  Verus prints for you to paste on a rejection carries **no `requires` and no
  `ensures` at all**, and will verify a 1 MiB out-of-bounds read and a null
  dereference at `4 verified, 0 errors`.
- **The column is not gameable retrospectively and IS gameable prospectively.**
  Measured exposure across the built tree is now `0`. But a pattern built on
  `vstd::raw_ptr` needs **zero** project-local trusted items and would publish a
  smaller number than the array sum, while reaching memory more directly. Ship
  one number plus a three-way classification of what each item is — **U-license**
  (the author is asserting an operation's safety), **V-gap** (the verifier cannot
  express something), **infra** (driver plumbing, which deletes call-site
  obligations wholesale) — and say in words how the rung reaches memory.

---

## 5. Result 4 — what this instrument can and cannot price

⚠⚠ **DISPUTED — DO NOT QUOTE THE CLAIM BELOW.** TASK_102 has now been reviewed
(TASK_113) and **both halves of the "if and only if" fail.** The sentence is
preserved rather than struck, and the evidence against it is stated immediately
after it. **RECAP finding 37 carries the same dispute.**
⚠⚠ **AND BOTH REPLACEMENTS WRITTEN FOR IT HAVE SINCE DIED TOO — see §7. Three
generalisations over this refusal set, three failures. The standing conclusion is
to keep the classification and publish no generalisation, so DO NOT read the
dispute below as a gap somebody still needs to fill with a better law.**

> **This benchmark can price a safety property IF AND ONLY IF some rung emits it
> as a compare-and-branch and another rung omits it.** A property enforced by
> **the type system**, by **a library contract**, by **an absent operation**, by
> **a resource limit no rung emits**, or by **a compiler diagnostic** has **no
> machine-code footprint at all**.

⚠⚠ **The ONLY-IF half is refuted by a pattern this document already cites.**
**`p38` prices a type-based aliasing property at exactly `6.00 Ir`/call** — five
independent one-line fixes agreeing to the unit, **none of them a compare or a
branch, and one of them a compiler flag** (`patterns/p38-alias-pun/NOTES.md`).
⚠ **And the counterexample is inside TASK_102's own report, which lists
*"`p06`'s division instead of a compare"* sixty-four lines after asserting the
fourteen are "all compare-and-branch".** **The IF half is unsupported:** two of
the eight candidates satisfy the antecedent (division-by-zero, and gcc's default
stack-clash probe) and **were refused anyway**, so nothing in the evidence shows
a compare-and-branch is *sufficient*. **Two of the quote's quantifiers are also
false** — probe 2 was the kill in **three of eight**, not "every single time",
and "no machine-code footprint at all" fails on the clang column and on the
format-string candidate's `+162 Ir`/call.

✅ **What survives: the eight refusals themselves.** Every load-bearing kill
re-ran and reproduced, and **no refused row comes back.** ⚠ **So this is *right
verdict, wrong reason*** — and in this project a refusal's reason is what gets
reused on the next row, which is why the generalisation mattered more than the
verdicts did.

⚠⚠ **AND THE SECTION'S TITLE QUESTION NOW HAS A MEASURED ANSWER FOR ONE COLUMN
NOBODY HAD TESTED — THE PROOF COLUMN, WHICH DOES NOT PRICE MECHANISMS AT ALL.**
**TASK_128 and TASK_130 held a kernel fixed and changed only where a bound comes
from. At the kernel boundary a real pattern would draw, the mechanism costs
`+208` bytes and `+329.00 Ir`/call — while `obligations` reads `5` for a
DEAD-CODE arm against `4` for the MECHANISM arm.** ⚠ **`obligations` is
`verified` out of the gate record, i.e. a count of SMT query units — one per
function body, one per loop — and across the built tree it correlates `0.894`
with syntactic size and `0.795` with `verus.rs` source lines.** ⚠⚠ **The
operational test, and it is cheap enough to apply to any column before quoting
it: a column's SPELLING SPREAD against its PRESENCE GAP. `Ir` measures
`8519 : 1` — invariant under re-spelling, moving under presence.
`obligations` measures `1 : 1`.** ✅ **So the proof-burden column is a size proxy
and must not be read as evidence that a mechanism is or is not present** — which
synthesize.py's own note half-said already, warning that a seven-line reviewed
wrapper trades against a zero-line axiom *"at par"*.

This is measured, not argued. The 48-row catalogue was written before the project
started — ⚠ **with one exception that weakens the "so the refusals are not
selection bias" argument by exactly one row: `p48` was added mid-project by the
manager at TASK_066 and refused at TASK_074.** ⚠⚠ ~~**15 rows are refused, each
on a measurement**~~ — **CORRECTED TWICE. At TASK_113 the true figure was 13; at TASK_115 it became
17, because the six rows that still read the bare word `planned` were finally
adjudicated and landed.** ✅ **The catalogue now decomposes as `48 = 26 BUILT +
17 REFUSED + 3 DEFERRED + 2 OTHER`, with ZERO rows left unadjudicated** —
`p24` (probed, live, needs a new reason) and `p35` (blocked, not refused) are the
two; `p20`/`p21`/`p25` are the deferrals. ⚠ **`p25` is the one row in the whole
catalogue on which this project has run NOTHING, and its cell now says so.** Eight further
candidates proposed later were probed and **all eight refused** — ⚠ **but they
were all selected for BUG-CLASS NOVELTY, the criterion this project's own
admission bar says "predicts neither way", and none was an `index >= len`
row; `p23`, the fifteenth `index >= len`, shipped a real result (⚠ **published as `3.11×`, corrected to `1.315×` at TASK_117**).** ⚠ **So
"two independent lists, both at a hit rate of zero" is one list plus a
differently-selected second list, and the zero is not evidence of structure.** Recursion depth: three rungs `call` the
same ICF-merged symbol, so there is one rung, not three. Unaligned load: the cast
and the `memcpy` spelling compile to the same 19 instructions. `qsort`
comparator: 80 cells, zero ASan reports, because glibc's `qsort` is mergesort plus
heapsort and all its bounds are counts.

⚠ **One of the fifteen does not survive its own reason, and a hit rate of zero is
exactly the claim a skeptic will test at its weakest row.** `p37` (callback with
`void*` userdata) is recorded in the catalogue as **REFUSED-REASON-REFUTED at
TASK_100**: the first limb reproduces (`the verifier does not yet support …
function pointer types`), but the second — *"R5 must use `dyn Trait`, so the
erasure that is the bug disappears"* — was an argument with nothing run, and it
is measurably false. A `dyn Op` with an **erased** `u64` userdata verifies
`4 verified, 0 errors`, and with a raw-pointer userdata read through
`vstd::raw_ptr::ptr_ref` it verifies `3 verified, 0 errors`, both at **zero
`unsafe`, zero `external_body`, zero `assume`**, with the anti-vacuity control
firing. ⚠ **That does not overturn the refusal** — no C rung, no cost axis, no
harm matrix and no full R5 were ever established — **but the row is flagged
"re-triage, do not rubber-stamp", and the count of fifteen should be read with it
named.**

⚠⚠ **AND `TASK_120` SPOT-CHECKED THREE MORE REFUSAL REASONS AGAINST THEIR
ARTEFACTS AND BROKE TWO OF THEM, SO *"one of the fifteen"* IS AN UNDERSTATEMENT
AND THE PARAGRAPH ABOVE IS THE WEAKER FORM OF ITS OWN ARGUMENT.** ✅ **Both
verdicts survive; both REASONS do not** — and a reason is what the next row gets
judged against.

- **`p20`** — the cell says the check is *"six instructions"* and costs
  **`+10.00 Ir`/call**. ⚠ **It is SEVEN** (the list omits the leading
  `mov %rcx,%rax` computing `off+len`; the disassembly diff is a clean 7-line
  insertion) **and it costs `+6.00` marginal / `+7.00` kernel-exclusive.**
  ✅ **The corrected mechanism predicts the corrected number to the instruction;
  the published pair did not.**
- **`p43`** — the cell says *"`+3.00 Ir`/call flat … i.e. `p16` verbatim"*.
  ⚠⚠ **`p43` is FLAT and `p16` is `O(nrec)` — they differ in ORDER, and `p16`'s
  own `NOTES.md` opens with a BOLD WARNING against exactly this conflation. The
  measurement offered as CONFIRMATION of p16-likeness is the measurement that
  DISTINGUISHES them.** ⚠ **The `+3.00` is `lea; cmp; jbe` hoisted — `p20`'s
  phenomenon, and `p20` is the citation this cell had already STRUCK as
  circular.**
- ✅ **`p39` survives, and better than written** — its `0.00 Ir` reproduces in the
  never-measured `k39_unpack_*` wire-format spelling too.

⚠ **So the honest figure is that OF FOUR REFUSAL REASONS EVER CHECKED AGAINST
THEIR ARTEFACTS, THREE DID NOT SURVIVE.** ⚠⚠ **That is a small sample and it is
the sample that exists; it should not be read as *"the refusals are wrong"* —
every verdict has held — but it is strong evidence that this project's REASONS
were held to a lower standard than its FINDINGS, which is exactly the asymmetry
`p28` predicted.**

Two consequences, and they are the ones to carry away.

**For a reader.** What this project measured is the **bounds-check family** —
fourteen of its patterns carry an `index >= len` axis. It says a great deal about
what a bounds check costs and very little about the cost of the parts of a safe
rewrite that are enforced by the *type system*, because those parts have nothing
to measure. That is not a gap in the method; it is the answer. Where safe Rust's
guarantee is compile-time, its runtime cost is **zero by construction** and no
benchmark will ever say otherwise.

**For a benchmark author.** The admissibility bar that came out of this is worth
stealing: **a new pattern is worth building when it brings a new *mechanism* — a
new operator on the safety line, a new source of the bound, or a new reason the
check is or is not elided.** *"Another `index >= len`"* is not the question;
*"another `cmp`/`jbe` in the same place for the same reason"* is. And a limb that
claims a new *reason* owes an **isolation**, not just a measurement: p23 cleared
its first two limbs and its third shipped a phenomenon whose stated cause failed
three separate isolations. A measurement shows *that*; only an isolation shows
*why*.

---

## 6. What this measurement will do to you

Nineteen published claims were retracted here. They are not confessions; every one
is a trap in the apparatus, they are transferable to any benchmark of this shape,
and collecting them in one place is deliberate — the alternative is scattering one
coherent result across twenty-six unrelated pattern write-ups.

**1. Search both sides, or you are publishing search effort.** Five patterns
published a headline in the *flattering* direction and passed a fully green gate
doing it. p10: *"safe Rust cheaper than unsafe"*, of which 60% was an unsearched
unsafe side. p38: `+21/+25` published against a true `+24/+32`. p22: **`+2.00`
published against `+125/+1021` — 510×** on the large band. And then p36 fell into
the *mirror image*, which is the newer lesson: it searched the unsafe side
carefully, left the safe side one lever, and that lever moved the safe side the
wrong way — published `+15.00 flat`, and the review's first in-contract respelling
made it `+7`. **Count the levers on each side and name the weaker-searched
endpoint. A difference is only as honest as its weaker endpoint.**

**2. Your out-of-sample test is probably fake, in one of two ways.** *Fake by
residue*: p23 produced **three mutually inconsistent "exact" laws, each with zero
in-sample residual**, and the published one mispredicted the *shipped* inputs by
up to **152 `Ir`/call** despite a `0.0000` holdout inside its own band. The
missing term was invisible because every band sat at the same residue — `m = 32`
and `m = 16`, both `≡ 0 (mod 4)`, with the sweep sampling seven of eight multiples
of four. **Third instance**: p38's additivity failure was the first, p46's
two-band fit the second, and the progression is instructive — p46 showed a
two-band fit can be *underdetermined* with no in-sample residual, p23 that a
one-band fit can be *confidently wrong* with a perfect in-band holdout. Only
out-of-band prediction caught either. *Fake by rank*: if the fit set is rank `n`
in an `n`-column design its rows span ℝⁿ, so **no** blob is out of sample in
regressor space and the hold-out cannot fail arithmetically. p14's
leave-one-length-out reported `max|residual| = 0.0` over 29 hold-outs on a design
that stays rank 4 after dropping any band; p13's held-out band is a verified
linear combination of the fit set's own extremes for all 17 of its values, with
residuals *smaller* than in-sample. **Ship one off-axis point in every band,
report the post-drop rank beside any hold-out, and treat a residual of exactly
zero as the signature of a test that could not fail.**
✅ **And the positive control, because a trap list with no worked success is not
a method.** p02's `R2 − R4` is a **sawtooth**: amplitude 179 `Ir`, resetting at
`len ≡ 1 (mod 16)`, riding a 0.21 `Ir`/byte linear term. It was fitted, then
**re-derived at seven unsampled lengths and at 8× the scale** — 178.9 and 0.2125
— which is the one model in this project tested by *prediction* rather than by
re-measurement. That is what the traps above are asking for, and it is one
pattern out of twenty-six.

**3. Before believing a check, ask what would make it FAIL — then make that
happen.** Six controls here could not have fired (`.memory/03-measurement.md`
entries 1, 2, 3, 4, 6 and 7 — entry 5 is struck, having been a control-shaped
error *about* a control, and the "three within three tasks" cluster the record
names includes that struck member). The sharpest: after adding a field to 22 gate records, the
manager regenerated the published tables, got a byte-identical file, and quoted
that as *"the change moved no published number"* — it is byte-identical because
the generator reads a different key and the new field's name appears **zero
times** in the generator at all. Another: a probe built to test whether the
launching method mattered had **both arms identical by construction**, and a
blocker that struck a *true* sentence out of the authoritative layer rested on
it. **A control with no demonstrated failing arm is not evidence.** And a test
split across two artefacts tests neither seam: ask which single command carries a
change from the source all the way to the number a reader quotes.

**4. A tool that reports nothing may be a tool that cannot see.** ASan is silent
on p08's overlap not because there is none but because fortification rewrote the
call to `__memcpy_chk`, and the check lives in the interceptor. A `head -4` in a
probe script hid ASan's banner for four catalogue rows, because gcc's UBSan
report is exactly four lines. On this box a hand-run dynamically-linked ASan
binary refuses to start behind an inherited `LD_PRELOAD` and **exits 1 either
way**, so an exit-code check cannot tell "clean" from "never ran". *A detector
that is not running looks exactly like a detector that found nothing.*

**5. A declared pin is self-certifying, and freezing it does not make it true.**
This project hashes each pattern's contract before any cell is built, so a
reviewer can tell a declaration edited *after* measuring from one that was not.
It works — and it does **nothing** about a declaration that measurement has since
*falsified*: p46's hash verified perfectly, which is exactly why the frozen text
still described the pre-build probe's world, asserting two numbers that appear
nowhere in the pattern's own notes. Two mechanical traps in the same family. A
pinned entry **with no backticks pins nothing**, while **every backtick in one
IS a pin, including inside explanatory prose** — p42 shipped a contract claiming
three things were pinned when none of the three was enforced, including the idiom
the pattern is named for. And a pinned spelling can be satisfied by a
**tautological conjunct the compiler deletes**: on p23 that moved an in-contract
floor 150 `Ir`/call and made two spans overlap.

**6. A published span's endpoints are what somebody thought to write.** p23's
floor moved 150 `Ir`/call; p42's unsafe-side endpoint moved 210 / 8707 **and
reversed the sign**, turning a comparative headline into *"the two admissible
classes are not separated"*. **Two overlapping spans do not become a difference
by choosing an endpoint.** And never difference two minima: `min(R3) − min(R4)`
is the difference of two *upper bounds* and bounds nothing in either direction —
measured, the same source edit moves one side −2 and the other +1.

**7. Deterministic does not mean invariant, and `Ir` is not time.** Three
independent things. (a) **`-O3 isolated` is not invariant**: ±7 `Ir` per rung is
decided by the **length of the environment block**, and *content* matters more
than length — one allocator-tuning variable moves **+486.00 `Ir`/call at an
identical 3332-byte block**, 69× the term the pin was built to diagnose. So
*"re-run the gate and compare"* is **not** a reproduction test for a marginal.
(b) **The `Ir` column can be sign-wrong**: p06 was designed to make `Ir`
*understate* a safety tax and does worse — on clang the hardened rung executes
45–108 **fewer** instructions and runs **10–20% slower**. (c) **Code layout moves
wall clock by up to 27% at an unchanged instruction stream** and can flip the sign
of a rung-to-rung comparison. The mechanism is static and parameter-free — a loop
body straddling one more 32-byte instruction-fetch window, or a loop branch
crossing a 32-byte boundary on a core carrying Intel's JCC erratum — confirmed out
of sample on 20 pre-registered layouts whose predictions were hashed before
timing, and it hits front-end-bound loops and nothing else. **Interleave by cell,
never by block, and measure the noise floor with byte-identical copies before
believing any timing effect.**

**8. Publish the invariant, not the number, when only a rebuild can produce it.**
Four gate runs gave 7, 7, 8, 8 distinct adversarial checksums, because the
pattern's own notes file is inside the gate record's `source_sha256` — so
recording the count forces a run and the run moves it.

---

## 7. What this project does not know

**Unreviewed work.** The project's own rule is that a finding is not authoritative
until a different agent has attacked it. ⚠⚠ **THIS SECTION LISTED FIFTEEN
UNREVIEWED TASKS AS OF TASK_108. THE DEBT HAS SINCE BEEN TRIAGED AND CLEARED, AND
CLEARING IT COST THIS DOCUMENT FOUR PUBLISHED CLAIMS** — which is the strongest
available argument for the rule.

**TASK_113 triaged the fifteen** (⚠ *fifteen, not fourteen — one was missing from
the manager's own list*) **to three worth reviewing, closing nine as superseded
or self-checking with a stated reason for each.** All three were then reviewed:

- **TASK_102** → reviewed by **TASK_113**: ⚠⚠ **Result 4's "if and only if" does
  not survive. See §5, which now carries the dispute.**
- **TASK_107** → reviewed by **TASK_114**: the environment pin's rule is false
  (the lossy term is the byte count, which omits the `envp` pointer array), and
  `MIRIFLAGS` was never the variable behind the Miri slowdown. ⚠ **No published
  `Ir` in this document is affected; the defects are in reproducibility metadata
  and in latent detectors.**
- **TASK_106** → reviewed by **TASK_117**: §2's `p23` swing was overstated 9×.
  **Corrected in place.** ✅ **The exact law itself survived a serious attack —
  design matrix rank 8 of 8, and twelve out-of-band predictions registered before
  measurement at max error 0.00.**
- **TASK_109 + TASK_110** → reviewed by **TASK_116**: ⚠⚠ **§4's ghost-ledger
  claim is refuted — the `ensures` is satisfied by a leaking program. Corrected
  in place.**

⚠ **What remains PROVISIONAL is now narrower and is marked where it is used**:
`p46`'s headline ground (TASK_092) and `p19`'s re-fitted laws (TASK_088).
✅ **The `p42` retraction has since reached that pattern's files (TASK_118), and
a THIRD encoding was built and also admits a verifying leaker — so `p42`'s R5
still does not cover its own bug class, and expressibility at the pin remains
OPEN rather than refuted.** ⚠ **A review is not self-certifying, and this list
has twice omitted reviewers who were themselves unreviewed.**

⚠⚠ **AND THE REPLACEMENT FOR THE DISPUTED RESULT 4 HAS NOW BEEN ATTACKED TWICE
AND DIED TWICE, WHICH IS ITSELF THE RESULT.** RECAP finding 40 (*"the remaining
rows fail because they RE-DERIVE A MECHANISM"*) was reviewed at TASK_120: the
tally is **6 of 22, not 7**, its membership was wrong three ways, and
*"duplication"* turned out to be **four different relations wearing one word**.
Its own replacement, finding 41 (*"the five-rung ladder has nothing to price on
them"*), was reviewed at TASK_122 and **failed harder** — it merged four
categories, and it had **no control arm**: run its criterion against the BUILT
tree and **8 of the 26 built patterns publish a zero on their own headline
axis**, `p46` most sharply, which ships `0.00000` *and* *"the boundary vanished"*
**as its published result**.

> ⚠⚠ **THREE GENERALISATIONS HAVE NOW BEEN OFFERED OVER THIS REFUSAL SET AND ALL
> THREE HAVE DIED. THE STANDING CONCLUSION IS TO KEEP THE 22-ROW CLASSIFICATION
> AND PUBLISH NO GENERALISATION OVER IT.** **The rows fail for many individually
> sound reasons, and that is the honest answer.**

**Which leaves the question this document cannot dodge: is the DOMAIN worked
out, or only this CATALOGUE?** ⚠ **The 47 rows are `git`-verified pre-project —
first commit, empty `patterns/` — so a pre-project list running out after 26
builds says little.** **TASK_123 therefore ran the enumeration nobody had run:
20 worked CVEs from nginx, OpenSSL, libxml2 and PHP, against the reviewed
admission bar, probe 1 first.** **Nineteen die on a `grep`, a run, or a
load-bearing citation.** ✅ **The logical seven die MEASURED, not assumed — strip
the incidental array index from CVE-2021-3450's decision and safe-naive,
safe-tuned and unsafe are byte-identical at 108 B and `37.00 Ir`/call each.**
**One survives: CVE-2021-23017, where a *sizing* pass under-counts a separator
the *writing* pass emits, so the bound comes from an earlier pass over the same
input — and a census of all 26 built kernels finds 14 destination buffers,
13 `#define` capacities plus one input extent, and ZERO prior-pass counts.**
⚠ **It is not built and not scheduled: only limb 2 of the bar is met, and its own
engineer disclosed that the row's spatial character depends on an allocation
choice that is the porter's and not the CVE's.**

⚠⚠ **AND THE RESULT THAT OUTRANKS THE SURVIVOR: A CVE CORPUS ANSWERS *"which
mechanisms are missing"* AND CANNOT ANSWER *"which idioms matter"*.** Eight of
the twenty are pure decision bugs — a distribution no idiom census would produce
— **because CVEs select for exploitability, not for frequency.** **That half
stands and is this section's result.**

⚠⚠⚠ **WHAT FOLLOWED IT HERE IS RETRACTED. This paragraph published:**

> ~~*"the idiom census that would answer it CANNOT BE RUN ON THE MACHINE THIS
> PROJECT LIVES ON: there is no independent C corpus present"*~~ — ~~*"so the
> admission bar stays MECHANISM-based, not by preference but because the
> frequency-based alternative has no instrument here … the honest reason this
> project's generality claims stop where they do."*~~

**It rested on one command carrying `-maxdepth 6`. Without the depth limit the
same machine holds an upstream PHP 4.0.2 tree entire — 301 `.c` files, 186 805
lines, with 324 `goto`s, 145 `strcat`s, 235 `memcpy`s and 579 counted index
loops — and a GNU coreutils tree beside it.** ⚠ **Both live in other projects'
directories and one is under a `.temp/`, so a census over them must record a
sha256 manifest of what it read; neither is a reason it cannot be run.**

⚠⚠ **The failure was the instrument's: a depth-limited `find` reports an empty
world exactly as an empty world does — the same class as this project's `head -4`
and its whitelist-grep-called-a-census.**

✅✅ **AND THE CENSUS HAS SINCE BEEN RUN.** ⚠ **UNREVIEWED engineer work
(TASK_129) at the time of writing; the corpus figures, the coverage zero and the
per-category precision table were re-derived by the manager.**
**49 898 bound sites over 991 147 deduplicated lines of C in 22 programs — PHP
4.0.2, GNU coreutils, and 24 upstream GNU packages — each site classified by
operator, by the source of its bound, and by where it is checked.**

⚠⚠ **THE ANSWER IS PARTIAL, AND THE PARTIALITY IS THE RESULT: THE ORDINAL TOP IS
A PROPERTY OF C AND THE DISTRIBUTION IS A PROPERTY OF THE PROGRAM.** `index` is
the top operator in **21 of 22** programs and `const` the top bound source in
**19 of 22** — but the shares swing **42–50 percentage points** and second place
flips between four categories. ✅ **So a frequency-argued admission bar gets a
first place and nothing below it. The mechanism-based bar stands, and now for a
measured reason rather than for want of an instrument.**

⚠⚠⚠ **AND THE CENSUS FOUND A COVERAGE GAP IN THIS PROJECT'S OWN CORPUS, STATED
AS COVERAGE AND NOT AS QUALITY: `ptr_offset` — a pointer cursor walking memory —
is `0` of the built tree's 255 bound sites. It occurs in all 22 programs, ranks
second or third in 15 of them, and its share runs 0.4 %–26.1 % with a median of
6.9 %.** **Every built kernel indexes; none walks.** ⚠ **Confirmed by three
independent instruments, including a classifier-free regex that returns `0`
across all 26 kernels.**

⚠⚠ **TWO CAVEATS THAT BELONG WITH THE NUMBER, both from the review (TASK_131).**
*(1)* **`0 of 255` is not 255 independent draws: the sites sit in 30
site-carrying functions across 26 files cloned from one template. Size-matched
to the ladder's own function-size distribution, the honest figure at the function
unit is `p ≈ 0.06` against the largest corpus — suggestive, not decisive.**
*(2)* ⚠ **An earlier draft of this paragraph said `ptr_offset` was a top-3
operator in *every* one of the 22 programs. It is 15 of 22; seven put it fourth.**

✅ **The obvious deflationary explanation was tested and refuted: this is not an
artefact of the harness handing every kernel an explicit length. In real C,
functions that receive a pointer *and* a length walk with a cursor at the same
rate as those that do not (9.2 % vs 9.8 %) or a higher rate (22.4 % vs 15.6 %).**
✅ **And nothing in the ladder forbids a walking C rung: no `identity` pin
involves the C rung, rung equivalence is defined semantically, no `forbidden`
entry in 26 patterns excludes a pointer cursor, and a checksum-equivalent
pointer-cursor respelling of `p11` violates none of them.** ⚠⚠ **This is still
not a proposal. Safe Rust's answer to a pointer walk is an ITERATOR — a different
representation, not "R4 plus a check" — which is the trap that killed
CVE-2021-23017 when `Vec::push` deleted the bound rather than checking it.**

⚠ **One field was measured and WITHHELD rather than published: *where the bound
is checked* scored 45/60 against hand labels, with its `earlier` label right 3 of
10 and its errors directional. The bound-source field's top categories carry the
headline — `const` 25/25, `none` 11/11, `field` 9/9 — and no disagreement moved
a site into or out of either.**

**Mechanisms that are recorded and not explained.** Cite these; do not explain
them. (a) **p23's elision cause failed three isolations**: the phenomenon
reproduces to the instruction under an independent probe, but *"the direction of
the cursor is the whole tax"* does not survive — making the induction variable
ascend costs +816…+1614 instead of recovering the elision. (b) **`τ`**, the
per-record periodic term in p23's exact law with values `{0, 2, 3, 4}`, has never
been disassembled. (c) **Why LLVM diverges on two textually identical executable
bodies**: p46's rejected variant and its verified twin have identical exec source
and measure `R5 − R4 = 15n + 1` exactly. The instruction accounting is complete;
the pass-level cause is not, and no compiler flag was bisected. (d) The
**environment-length-versus-content** question is open in one specific way: the
list of variables whose *content* changes codegen paths was derived from a single
measurement and is not proved complete.

⚠⚠ **AND THE CONTROL ARM THIS DOCUMENT NEVER HAD, FOUND LATE AND WORTH STATING
PLAINLY: ACROSS ALL 26 PATTERNS AND EVERY ADVERSARIAL INPUT, THE FOUR RUST RUNGS
HAVE NEVER ONCE DISAGREED WITH EACH OTHER.**

```
129  adversarial (pattern, input) pairs in results/gate/*.json
 58  with ANY cell divergence
  0  where safe_naive / safe_tuned / unsafe / verus differ from one another
```

**Every behavioural divergence in this tree is among the C variants.** ✅ **It is
the cheapest check in the project — one pass over committed gate records, no
build and no callgrind — and it took 124 tasks to run.** ⚠ **Its immediate use
is defensive: a proposed pattern whose headline is *"the safe rung panics, the
tuned rung is correct, the unsafe rung is silently wrong"* is claiming something
that has never happened here, which is a reason to distrust the port rather than
to celebrate the row.** **That is exactly how the one surviving CVE candidate
was refused.**

⚠⚠ **The obvious second reading — *"then the harm inputs are not adversarial
enough"* — WAS TESTED AND IS WRONG, and the reason is worth more than the
census.** **13 449 fresh candidate inputs across all 26 patterns produced 600
rung splits and STILL ZERO Rust-rung splits, and so did the same corpus built
with `debug-assertions=ON`.** **The cause is in the contracts:** `requires` is a
**length** bound in **26 of 26 patterns and never mentions buffer CONTENTS**,
`ensures` is a single **total** value clause, and the pinned driver loop makes
the window bound a **theorem**. **So an adversarial input can only change bytes
inside a window every Rust rung is contractually total on.**

> ⚠⚠ **NO INPUT CAN BE ADVERSARIAL TO A RUST RUNG IN THIS TREE. MORE ADVERSARIAL
> INPUTS IS NOT THE FIX — THERE IS NOTHING FOR THEM TO BE ADVERSARIAL TO.**

✅ **Blunt corroboration: NO RUST RUNG HAS EVER PANICKED** — 107 592 fuzz runs
plus 516 gate rows, zero exits outside `{0, EXIT_TRUNCATED, EXIT_CAP}`, and five
of the seven are the *shared driver* refusing a malformed file rather than a
kernel. **The C rungs on the same inputs: 29 SIGSEGVs, 8 aborts, 2 hangs.**
⚠ **That is the single most direct statement of the safety half of this
project's subject, and it went unmeasured for 125 tasks.**

⚠ **A real weakness DOES exist and it is elsewhere: 36 of the 129 adversarial
inputs (27.9%) make ZERO kernel calls**, and the `adversarial-strideN.bin`
template is 0-call in **22 of 26 patterns** — a template copied forward without
being re-aimed. **`p42` carries 10 adversarial inputs of which 7 are zero-call.**
**Those inputs are doing no work, and no per-pattern number in this document
would have shown it.**

**Structural gaps.** The unsafe side is unsearched on most patterns: **14 of 26**
print `undeclared` in the search-state column and **nine** report a real search on
at least one side. There is **no cross-pattern wall-clock column**, because the
timing floor is a per-session property and these measurements span 22 sessions.
And the whole kernel-exclusive matrix speaks for one inline mode: of 414 `-O3`
whole-mode cell/input pairs, 394 have no kernel symbol at all — the kernel
inlined into `main`. ⚠ **The 20 survivors are gcc-only but they are not all
partial-inlining remnants**: 16 are `kernel.part.0` and **four are the whole
`kernel` symbol**, p46's `c-gcc` and `c-gcc-h` cells on both blobs. So *"there is
not one `whole`-mode row where the kernel column means what it means in
`isolated`"* is false for those four. The isolated-only decision survives —
p46 is one pattern, gcc-only, C-only, so no rung comparison is available from
those rows — but the justification needed correcting, and
`results/synthesis.md` printed the four `kernel` rows four lines above the
sentence that denied them.

**A gap in this document rather than in the project, disclosed because it is the
kind that repeats.** The first version of this file compressed twenty-six
patterns into four results, and **every significant omission ran one way**: it
dropped p02's security result (now §3), the R4-chained-to-the-prover constraint
(§1), p01's exact C/Rust instruction match (§2), p38's price for the undefined
spelling (§3) and p19's sign flip (§2) — five reviewed, quotable results, all of
them flattering to safe Rust, none of them awkward. Four smaller ones went with
them: p36's `3.00000 Ir`/dispatch (§4), p02's predicted sawtooth (§6), p04's
`next_pow2(CAP) ≤ ARR_LEN` and p12's both-ends rule (both §2). Nineteen
retractions had trained this project to distrust *"safety is cheap"*, and the
reflex removed the evidence for it; the brief that commissioned the compression
asked for *"where safe Rust does not help"* and had no counterpart item. All nine
were restored at TASK_112 after `TASK_111` found them. ⚠ **A coverage bias has no
arithmetic signature — every figure in the first version reproduced against the
record on the pass that found this — so the only check for it is to ask, of a
finished document, which way its gaps point.**

**What the corpus is made of, and it bounds the generality more than the
toolchain pin does.** The 28 kernels classify, by the safety line each one's
`c/kernel.c` omits, like this — derived and drift-checked by
`harness/tools/composition.py`:

```
spatial          15   p02 p03 p05 p07 p09 p10 p11 p12 p13 p14 p16 p17 p23 p36 p46
logical           3   p04 p06 p19
temporal          3   p27 p29 p32
type              1   p38
resource          1   p42
side-channel      1   p47
UB, not memory    1   p18
non-termination   1   p22
aliasing          1   p08
calibration       1   p01
```

⚠⚠ **Fifteen of twenty-eight are spatial, and every claim this document makes
about the type axis rests on ONE pattern.** `p38` is the only type-confusion.
A result drawn from a single row is a result about that row until a second one
agrees with it, and **§5's `6.00 Ir`/call for a type-based aliasing property is
in exactly that position** — a one-row result stated as a law.

✅ **The temporal axis is the one place this improved: `p29` (BST delete) joined
`p27` at TASK_139**, and the two are **not** the same shape. `p29`'s
in-order-successor splice **overwrites its victim in place and frees the
successor**, so one source line carries **two bug classes selected by the
input** — a use-after-*free* on leaf victims and an in-bounds
use-after-*recycle* on two-child ones.

⚠⚠ **The recycle half is what four independent mechanisms miss**: ASan is silent
on it; Verus's linear `PointsTo` does not object to it (only the *functional*
postcondition rejects it); safe Rust's `Option<Box<_>>` reproduces it; and the
buggy rung's checksum is *reproducible* there while it is **not** on the
use-after-free half — so the half every detector sees is the half that cannot be
gated.

⚠ **A sharper claim was published here and retracted at TASK_140:**
~~*"`p27`'s safety line needs ONE conjunct, `p29`'s needs TWO"*~~. **One
conjunct suffices** — widening the liveness array from a bit to the occupant tag
is exact and adds no state. **The row stands on the two-bug-class mechanism, not
on a conjunct count.**

**§3's *"safe Rust's temporal guarantee is a guarantee about the allocator"* now
has a second row under it rather than one.**
⚠ **This does not weaken the spatial results — those are the fifteen — it says
where the document's confidence should stop.**

⚠ **The table counts safety lines, not bugs.** `p09` ships two and only the
omitted `q < nbits` is spatial.

⚠⚠ **And there is a measured coverage gap inside the spatial fifteen.** An idiom
census over 49,898 bound sites in 991,147 deduplicated lines of real C in 22
programs (PHP 4.0.2, GNU coreutils, and upstream GNU packages) found
`ptr_offset` — walking memory with a pointer cursor rather than an index — in
**all 22 programs, ranking second or third in 15 of them**, share 0.4%–26.1%,
median 6.9%. **It is zero in all 26 kernels here.** No kernel in this tree walks
memory with a pointer cursor.

⚠ **Do not quote that zero as `0 of 255` and call it decisive.** The 255 sites
sit in 30 site-carrying functions across 26 files cloned from one template, so
the draws are not independent; size-matched against the ladder's own function
length distribution, the honest figure is **p ≈ 0.06 — suggestive, not
decisive**, and the `0 of 255` framing overstated it by roughly 5000× in
p-value. ⚠ **The zero is also a property of the regex guard that measured it.**
Figures and caveats are finding 45's.

**And the scope that bounds every number above.** One box, one libc, one gcc, one
clang, one rustc, one Verus and one vstd pin, `-O3 isolated`, two blobs per
pattern out of a committed sweep. Where a claim is about the *verifier* rather
than about Rust, it is a claim about `0.2026.08.09.92f466f` and its pinned
standard library, not about verification: this project twice published *"no
specification exists"* for a function whose specification was one directory away.
Every number here should be read as *"on this configuration, with these
spellings"* — which is, in the end, the same sentence as the one at the top:
**the cost of memory safety is a property of a pair of programs, and you have to
say which pair.**

---

*Sources: `results/synthesis.md` (generated tables and provenance), `RECAP.md`
findings 1–39, `.memory/01-ladder.md` (rung definitions and per-pattern
findings, authoritative), `.memory/03-measurement.md` (measurement rules),
`.memory/04-verus.md` (proof burden and trusted base), `.memory/06-catalogue.md`
(the pattern catalogue and its refusals). Census counts and bucket lists in §2
are re-derivable from a clone with `python3 synthesis/census.py`, which reads
`results/synthesis.md` and nothing else.*
