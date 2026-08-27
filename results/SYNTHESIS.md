# What 26 kernels say about the cost of memory safety

*A cross-pattern synthesis of `sec-ladder`. Written at TASK_108, against 26 built
patterns and 39 recorded findings.*

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

**Four results and a method.** That compression is itself a finding: twenty-six
patterns do not give twenty-six independent lessons about safety cost. The
headlines collapse; what varies pattern to pattern is the *exception*.

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
| **R4** | unsafe Rust | `get_unchecked`, raw pointers — whatever reaches C's codegen. Correct, just unverified |
| **R5** | unsafe Rust + Verus | R4's executable code, plus specifications and proofs discharging every unsafe precondition |

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
where the rungs call different library routines; `results/synthesis.md` §2 prints
both and tags every row with a **licence** saying whether the two cells dispatch
the same work outside the kernel. A row tagged `NOT-LIC` is *known* to be wrong
as a kernel-exclusive difference. Four of the 26 `R3−R4` rows are not licensed.

**The gate.** `harness/check.py` is a ~5 400-line adversarial checker each pattern
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

**One box.** Everything here is one containerised Xeon Gold 6230, glibc 2.39
(`_FORTIFY_SOURCE=3` by gcc default), gcc 13.3.0, clang/LLVM 22.1.6, rustc
1.97.1 (whose LLVM is bit-for-bit that clang), Verus `0.2026.08.09.92f466f` with
a pinned vstd. §7 says what that costs you.

---

## 2. Result 1 — the safety tax is a property of a *pair of spellings*, and the check is rarely the biggest term

### The distribution

Over the 22 patterns whose `R3−R4` row is licensed for differencing
(`results/synthesis.md` §2; re-derivable with `.temp/t108/census.py`), shipped
spellings, `-O3 isolated`, kernel-exclusive `Ir` per call:

- **9 of 22** sit within **±32 `Ir` per call on both blobs** — p01, p02, p04,
  p08, p12, p17, p18, p22, p38. Flat in the size of the data, not a percentage.
- **4 of 22** are **negative on both blobs** — p10, p13, p18, p46: safe Rust is
  *cheaper* than the unsafe rung. Three of the four have been investigated
  (p10, p13, p46) and in each, **none of the margin is safety**; p18's search
  state is undeclared.
- **9 of 22** exceed 100 `Ir` per call on at least one blob — p03, p05, p06,
  p07, p09, p14, p19, p23, p47. These are the interesting ones, and the table
  below says what each is actually paying for.

**Always quote R3.** The naive rung R2 overstates safe Rust's cost against R4 by
between 1.05× and 3 536× on the `large` blob, median about **7.3×** — 3 536× on
p08 (a `memmove` idiom R2's indexing defeats), 3 323× on p04, 1 033× on p22.
Two patterns invert (p09 and p14: R3 is *dearer* than R2, and on p09 that is the
documented reslice/load-merge hazard, not noise). A benchmark that ships R2 as
"safe Rust" is not measuring safety; it is measuring whether anyone tuned it.

### Where the number is ~0, the mechanism is always visible

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
  per call on p01 and **+10** on p02 against unsafe, flat in the size of the
  data. Hardened C's own check is **+5** (gcc) / **+12** (clang), also flat —
  which is the comparison that matters, and it says safety costs about the same
  in both languages, with Rust making it non-optional.

### Where the number is large, name what you are paying for

**"The bounds check costs X" is almost never the right sentence.** Pattern by
pattern, for the nine licensed rows above 100 `Ir`/call:

| pattern | `R3−R4`, small / large | what it is actually paying for |
|---|---|---|
| p03 bounded stack | 359 / 626 | the check — **and a one-line dead clamp deletes 100% of it** on both sides |
| p05 index flatten | 123 / 399 | a hoisted per-row trip count and a scalar epilogue; blocked by **nonlinearity** |
| p06 rotate | 334 / 172 | **none of it is a bounds check** — `zip`/`Rev` adaptor exhaustion tests |
| p07 binary search | 3 015 / 10 025 | the check, genuinely, with **no axis along which it amortises** |
| p09 bitset | 13 756 / 48 885 | **half is a lost 8-byte load-merge idiom**, not deleted checks |
| p14 field split | 638 / 425 | R4's foreclosed unroll: the tax moves 6.456 → 3.506 `Ir`/line byte at constant input size |
| p19 state machine | 260 / 4 100 | `1.00 Ir`/byte is **one `and $0x7,%edi`** — a mask, not a check |
| p23 partition | 306 / 444 | the **data's shape**, and ≥150 `Ir`/call of the safe side is spelling |
| p47 constant-time compare | 90 / 142 | the constant-time discipline; R2 is *cheaper* precisely because it leaks |

Three of these deserve their mechanism spelled out, because they generalise.

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
would have been one ratio. The 3.00000 is the finding: the *same* check costs one
instruction more here than in p16's fold, because the scan's induction variable is
window-relative where the fold's was hoisted to blob-absolute.

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

### The two results that are easy to get backwards

**A bound is worth more than the check costs (p13).** `strncpy` truncation:
72% (`small`) and 91% (`large`) of the published safe-beats-unsafe gap is the
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
read path. `R3 − R4 = +230.07 / +792.75` and **none of it is temporal safety** —
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

`R3 − R4` differences two rungs **searched to wildly different depths**, and
every time a side has been searched properly the number moved a long way. In
`results/synthesis.md` §2's own search-state column, **18 of 26 patterns print
`undeclared`**, three more owe a span, and only **five** report a real
two-sided or R4-side search. Of the five: p10's −323/−603 became −129/−241
against a verifying R4 candidate; p13's −177/−1054 became +44/+77, a sign flip;
p36 refuses to publish a single number at all. **So part of what that column
measures is search effort**, and any single row should be read as a bound with
one endpoint held fixed by fiat, not as a property of the pattern.

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

**Safe Rust can be worse than C.** ⚠ PROVISIONAL, from a refused row: `Rc` in
both directions of a doubly linked list is a cycle and leaks (Miri: five
`memory leaked` lines); `Weak` for the back pointer does not (zero). Both are
safe, both compile, and the leaking one is the spelling a hurried programmer
reaches for. The row was refused as a *headline* precisely because `Weak` is
equally idiomatic and measured leak-free — so read this as a warning about a
spelling, not a claim about the language.

**And two for the other side of the ledger, because a reader who stops here will
have the wrong impression.** p08's overlapping `memcpy` is a bug safe Rust
**cannot express** — the borrow checker rejects it at compile time, so there is
no runtime check and nothing to measure. And p38's strict-aliasing miscompile is
the first bug class in the tree that **unsafe Rust does not reintroduce either**:
Rust has no type-based aliasing rule at any rung. Both are unambiguous wins, and
**neither is visible in any `Ir` column** — which is §5's point arriving early.

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

### What a proof does not buy: a family of three

> **The proof discharges exactly what it says, and the program is still broken.**

1. **p47** — the proof certifies a **leaking** kernel, under an *identical*
   contract, with the obligation count unchanged.
2. **A termination proof does not bound the stack.** A recursive kernel with
   `decreases buf.len() - i` verifies `3 verified, 0 errors`; the compiled binary
   at depth 10⁶ prints `fatal runtime error: stack overflow, aborting`, `rc=134`.
   ⚠ PROVISIONAL — TASK_102, unreviewed.
3. **p42** — an affine deallocation token does not force deallocation. An R5 that
   forgets the error path's `deallocate` verifies with 0 errors, because
   `Tracked<Dealloc>` is **affine, not linear**: a proof may simply drop it.

⚠⚠ **p42's membership is conditional, and that makes it the most instructive of
the three.** It was published as *"the first pattern whose R5 does not cover its
own bug class — Verus at the pin cannot state leak-freedom"*, landed in the
authoritative layer, and was **refuted by its own review within hours**. Escrow
the token into a tracked `Map<int, Dealloc>` whose domain must return empty and
the property is stated exactly: `18 verified, 0 errors`, the leak arm
`17 verified, 1 errors` at precisely the dropped release, **zero new trusted
items, and machine code identical to the shipped rung**. ⚠ **So p42 is evidence
about an encoding choice, not about the prover — do not cite it as "a prover
cannot express a resource property."** (Clean negative, since it was the other
route named: there is **no linear must-consume tracked mode at this pin.**)

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

⚠ PROVISIONAL — TASK_102, unreviewed. It is nevertheless the finding a reader
deciding whether to build one of these needs first.

> **This benchmark can price a safety property IF AND ONLY IF some rung emits it
> as a compare-and-branch and another rung omits it.** A property enforced by
> **the type system**, by **a library contract**, by **an absent operation**, by
> **a resource limit no rung emits**, or by **a compiler diagnostic** has **no
> machine-code footprint at all**.

This is measured, not argued. The 48-row catalogue was written before the project
started; **15 rows are refused, each on a measurement**, and eight further
candidates proposed later were probed and **all eight refused** — two independent
lists, both at a hit rate of zero, which is what makes it structural rather than
unlucky. Recursion depth: three rungs `call` the same ICF-merged symbol, so there
is one rung, not three. Unaligned load: the cast and the `memcpy` spelling compile
to the same 19 instructions. `qsort` comparator: 80 cells, zero ASan reports,
because glibc's `qsort` is mergesort plus heapsort and all its bounds are counts.

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

**3. Before believing a check, ask what would make it FAIL — then make that
happen.** Six controls here could not have fired, three of them within three
tasks of each other. The sharpest: after adding a field to 22 gate records, the
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
until a different agent has attacked it. As of TASK_108 the following have not
been through a review, and anything resting on them is PROVISIONAL: **TASK_088**
(p19's re-fitted laws, its CVE correction, and the harness changes p19 is gated
under), **090**, **091**, **092** (p46's corrections, on which p46's headline
ground now stands), **095**, **097**, **102** (the instrument-domain result in
§5), **106** (p23's corrections), **107** (three results that changed how this
project measures), and the two most recent reviews and their landings, **109**
and **110**. Four tasks on the list in circulation have since been reviewed —
TASK_094 by TASK_100, TASK_099 by TASK_103, TASK_101 by TASK_105 and TASK_104 by
TASK_109 — and that correction was made while writing this file.

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

**Structural gaps.** The unsafe side is unsearched on most patterns: 18 of 26
print `undeclared` in the search-state column and only five report a real search.
There is **no cross-pattern wall-clock column**, because the timing floor is a
per-session property and these measurements span 22 sessions. And the whole
kernel-exclusive matrix speaks for one inline mode: of 414 `-O3` whole-mode
cell/input pairs, 394 have no kernel symbol at all — the kernel inlined into
`main` — and all 20 survivors are gcc partial-inlining remnants.

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
(the pattern catalogue and its refusals). Census counts in §2 are re-derivable
with `.temp/t108/census.py` against `results/synthesis.md` §1.*
