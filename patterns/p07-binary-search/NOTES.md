# p07 — binary search: findings, proof notes, TCB tally

Built at TASK_026. **The first pattern built to the named-spelling standard
natively** rather than retrofitted with it, and the first whose kernel is not a
linear fold.

Read `spec.md` first for the contract; this file is what was measured. Two of
TASK_026's prescriptions were contradicted by measurement and both corrections
are §0 and §1.

---

## 0. The catalogue row is wrong, and here is the arithmetic

`.memory/06-catalogue.md:291` lists p07's bug as **midpoint overflow
`(lo+hi)/2`**. TASK_026 asked for this to be settled before anything was built.
**It is unreachable at every size this wire format can express, and RAM is not
the binding constraint — the header field width is.**

`n` is a `u32` header field, so `n <= 2^32 - 1`, and the length check
`4*n + 4*nq > avail` forbids declaring an `n` whose elements are not present.
With `size_t`/`usize` indices:

```
lo <= hi <= n - 1 <= 2^32 - 2
lo + hi           <= 2*(2^32 - 2)  =          8 589 934 588
2^64              =                 18 446 744 073 709 551 616
                                    ------------------------
                                    2 147 483 649x short
```

The smallest input that would reach the overflow, per index type, computed by
simulating the search exactly rather than by bounding it
(`.temp/p07/midpoint_probe.py`, output verbatim):

```
index type                                       limit         min n        u32 bytes
size_t / usize (shipped)         18,446,744,073,709,551,616 9,223,372,036,854,775,809 36,893,488,147,419,103,236
uint32_t                                 4,294,967,296 2,147,483,649    8,589,934,596
int (the historical JDK bug)             2,147,483,648 1,073,741,825    4,294,967,300   (UB: signed overflow)
uint16_t                                        65,536        32,769          131,076
```

Three things follow, and the third is the useful one:

1. **The shipped spelling cannot overflow at all.** Not "not on this box" — not
   at any `n` a u32 field can hold, by a factor of 2.1e9.
2. **The cheapest reachable spelling is `int`, at 4 GiB of u32 elements.** That
   cannot be a benchmark input: the gate builds 32 cells and runs every one on
   every input under callgrind (~100x) and Miri (~1000x), and signed overflow is
   UB so at `-O3` the demonstration would be a statement about the optimiser
   rather than about the program. Note also that the *first* probe never
   overflows in any width — at `lo == 0`, `lo + hi == hi <= n-1`, which is
   representable by construction — so the overflow needs `lo` and `hi` both
   large, i.e. a key near the top, and the threshold is `2*(n-1) >= LIMIT`.
3. **The overflow that IS reachable in a binary search over this format is in
   the OTHER multiplication.** The length check `4*n + 4*nq` reaches
   `4*(2^32-1)*2 = 34 359 738 360` and needs 36 bits. In unsigned 32-bit it
   wraps: at `n = 2^30, nq = 1` the left-hand side is `4`, the test passes on
   any window over 12 bytes, and the first probe is 2 GiB out.
   `adversarial-width.bin` is that input, at a window of **88 bytes**, and §6
   builds the narrow cell and measures it: **SIGSEGV, where the shipped 64-bit
   check returns 0.**

So the catalogue names the right CWE pair (190 feeding 125) on the wrong
multiplication. **Proposed replacement for the catalogue row:**

> | p07 | binary search | declared element count vs buffer, reached by a
> *jump* rather than a walk; overflow in the **length check** (`4*n + 4*nq`),
> **not** in the midpoint — see p07 NOTES §0 | moderate | done |

### The contrast with p05 is exact, and it runs the other way

Both patterns model "a multiplication in the check is too narrow". They sit on
**opposite sides** of the `uint32_t` boundary, which is why "do the check in 64
bits" is advice whose force depends on the header field width:

| | header fields | the product | fits `uint32_t`? | which spelling breaks |
|---|---|---|---|---|
| p05 | `nrow`, `ncol` u16 | `nrow*ncol <= 4 294 836 225` | **yes** (by 131 071) | signed 32-bit only |
| p07 | `n`, `nq` u32 | `4*n + 4*nq <= 34 359 738 360` | **no** (by 8x) | signed **and unsigned** 32-bit |

Measured, §6: on `adversarial-width.bin` the signed *and* the unsigned 32-bit
cells both SIGSEGV. On p05 the unsigned one is sound.

---

## 1. The second correction: the loop-bound spelling — and a defect it exposed in my own generator

TASK_026's pseudocode is the textbook inclusive form and names two underflow
sites: `hi = n - 1` at `n == 0`, and `hi = mid - 1` at `mid == 0`. **The second
is not an adversarial case**: `mid == 0` requires only `lo == 0 && hi <= 1`, so
any query key below `elements[0]` reaches it, on well-formed input. Built as a
p07 rung it would make the C cells SIGSEGV and the safe Rust cells panic on
`small.bin`, so no checksum could agree and `sanitizer_expect` for
`small`/`large` could not be `"clean"`. And it cannot coexist with "R1 omits
exactly the length check and nothing else" either, because the *other*
underflow site is guarded in every rung by the pseudocode's own
`if n == 0 || nq == 0: return 0`.

**Shipped instead:** half-open bounds in every rung — `hi = n`, `while lo < hi`,
`hi = mid` — no subtraction anywhere that can underflow, `mid = lo + (hi-lo)/2`
kept verbatim, and a `decreases hi - lo` with no side condition.

### The measurement that made this section honest, and it corrected me

The first draft of `inputs/gen.py` drew every miss as `element + 1`. That draws
**every key from `[elems[0] + 1, elems[n-1] + 1]`, so no key is ever below
`elems[0]`** — and the inclusive spelling therefore never reaches `mid == 0`
with `v > key`. Built and run, the inclusive C variant printed the **correct
checksum** on `small.bin`. The claim in this section was true of the spelling
and false of my own workload, which is the same shape of error
`.memory/01-ladder.md` records for p05's residues and p17's two-point law: the
input that would have falsified it was not in the set.

`query_list` now emits, per window with `nq >= 4`, exactly **one key below the
minimum and one above the maximum**; the ratio of hits to misses is still
exactly 1/2. With that fix (§6):

```
k_incl on small.bin              exit=-11 (SIGSEGV)
k_incl on adversarial-unsorted   exit=-11 (SIGSEGV)
c-gcc-h (half-open) on both      exit=0, model's checksum
```

so the textbook spelling of binary search **crashes on p07's own well-formed
input, with the length check present and no attacker in sight**.

---

## 2. What is new about this kernel

Two things, and they are the deliverable rather than the pattern count.

**(a) It is the first kernel here that is not a linear fold.** p01, p02, p05,
p08, p16 and p17 are all `for each byte: acc = f(acc, b)`, so a per-call safety
constant divided by `n` bytes goes to zero — which is *why* "safety is cheap"
keeps coming out. Binary search does `ceil(log2(n+1))` probes per query over a
`4n`-byte array. On `large.bin` that is **6428 bytes probed out of a 1 048 916
byte window**, 0.61%. §3 measures what happens to R3's cost as `n` grows: it
does **not** go to zero.

**(b) It is the canonical unpredictable-branch kernel**, so it tests
`.memory/01-ladder.md`'s "static `Ir` is not a cost model" and "`Ir` and ns can
disagree in direction" on a kernel *designed* to make them disagree. This box
has `perf_event_paranoid = 3` and no branch-miss counter, so the branchless
control in §11 is **mandatory rather than optional** — and §11 confirms `cmov`
in the disassembly, and controls for code layout before drawing any inference.

---

## 3. Performance — and the answer to "does R3's cost amortise?" is NO

`-O3 isolated`, `panic=unwind`. **Two `Ir` conventions are in shipped patterns
and this section says which**: the table below is **callgrind kernel-exclusive
`Ir`** (p16's convention), and every *law* in §3b is the **whole-program
marginal** (p05's and p17's, and `check.py` stage 3b's). Wall clock is
`taskset -c 3`, interleaved round-robin, min of 30 reps; frequency scaling is on
and cannot be disabled without root; the box is shared.

| rung | static `n_fn` | `Ir` small | /call | /query | `Ir` large | /call | /query | ns small | ns large |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R1 c-gcc | 105 | 93 127 510 | 11 640.9 | 200.7 | 45 772 727 | 38 143.9 | 414.6 | 21.037 ms | 25.460 ms |
| R1h c-gcc-h | 115 | 93 183 510 | 11 647.9 | 200.8 | 45 781 127 | 38 150.9 | 414.7 | 20.486 ms | 25.414 ms |
| R1 c-clang | 66 | 48 043 926 | 6 005.5 | 103.5 | 23 506 615 | 19 588.9 | 212.9 | 14.795 ms | 21.543 ms |
| R1h c-clang-h | 71 | 48 083 926 | 6 010.5 | 103.6 | 23 512 615 | 19 593.9 | 213.0 | 12.164 ms | 21.194 ms |
| **R2 safe-naive** | 172 | 98 569 648 | 12 321.2 | 212.4 | 48 106 714 | 40 088.9 | 435.8 | 17.717 ms | 22.543 ms |
| **R3 safe-tuned** | 99 | 76 614 958 | 9 576.9 | 165.1 | 37 653 579 | 31 378.0 | 341.1 | 15.642 ms | 22.116 ms |
| **R4 unsafe** | 66 | 52 498 130 | 6 562.3 | 113.1 | 25 623 657 | 21 353.1 | 232.1 | 13.846 ms | 21.774 ms |
| **R5 verus** | 66 | 52 498 130 | 6 562.3 | 113.1 | 25 623 657 | 21 353.1 | 232.1 | 13.843 ms | 21.846 ms |

Against R4, in percent:

| rung | `Ir` small | ns small | `Ir` large | ns large |
|---|---:|---:|---:|---:|
| c-gcc | +77.4% | +51.9% | +78.6% | +16.9% |
| c-clang | −8.5% | +6.9% | −8.3% | −1.1% |
| R2 | **+87.8%** | **+28.0%** | **+87.7%** | **+3.5%** |
| R3 | **+45.9%** | **+13.0%** | **+47.0%** | **+1.6%** |
| R5 | 0.0% | −0.0% | 0.0% | +0.3% |

**Read the R2 row twice. The same +87.8% instruction gap converts to +28.0% of
wall clock on the L1-resident input and +3.5% on the memory-bound one** — an 8x
difference in the conversion factor, from the *input*, with the program held
fixed. That is `.memory/01-ladder.md`'s "static counts are not a cost model" in
its sharpest form to date: here the *dynamic* count is not a cost model either.

`c-clang` executes 8.5% **fewer** instructions than R4 on `small` and takes
6.9% **longer** — `Ir` and ns disagreeing in direction inside one input, on the
same LLVM backend. §11 has the layout control that says how much of that is
real; the honest version is "the two are within the layout band and the ns
column cannot rank them". **The instruction half is real and unexplained**:
swept, `c-clang − R4` is `−1.0050` Ir per probe, i.e. clang's probe body is one
instruction shorter than rustc's on semantically identical code with the same
backend version (`.memory/00-environment.md`: clang 22.1.6 == rustc 1.97.1's
LLVM). p01 found a +2 instruction rustc-over-clang delta from an
induction-variable choice; this is the same family with the sign flipped, and I
did not chase it to the register allocator.

### 3a. The mechanism, derived from the listings with zero fitted parameters

Every rung's search loop is one basic-block chain; the numbers below are counted
off `harness/asm.py`'s normalised listing, not fitted.

**R4 (`unsafe`), the branchy shipped loop** — two paths, because the `hi = mid`
arm re-enters above the loop test:

```
   mov %r11,%r10          <- hi = mid arm re-enters here
   cmp %r10,%rbx ; jae    <- lo < hi
   mov %r10,%r11 ; sub %rbx,%r11 ; shr $1,%r11 ; add %rbx,%r11    <- mid
   lea (%rdx,%r11,4),%r14                                          <- ep
   mov (%rdi,%r14,1),%ebp   <<< the WHOLE u32 decode, ONE instruction
   cmp %r9d,%ebp ; je       <- v == key, break
   jae                      <- v < key ?
   inc %r11 ; mov %r11,%rbx ; cmp %r10,%rbx ; jb                   <- lo = mid+1
```

`lo` path = 13 instructions, `hi` path = 12. At the 50/50 branch split the
workload produces that is **12.5 Ir/probe**, and the swept fit in §3b measures
**12.5035**.

**LLVM merges the written-out little-endian decode into a single 32-bit `mov`**
— in R1-clang, R2, R3, R4 and R5 alike. So `idiom.required`'s "written out with
`+` and `*`" costs nothing on the LLVM side; it is a *proof* convenience
(`.memory/04-verus.md`: `+` is linear arithmetic, `|`/`<<` drags in
`by (bit_vector)`) that the optimiser undoes for free.

**R3 (`safe_tuned`) adds exactly 6 instructions per probe**, and they are the
slice reslice `&buf[ep..ep + 4]`:

```
   lea (%rsi,%r15,4),%rdx   <- ep again (the range's end operand)
   add $,%rdx               <- ep + 4
   cmp $,%rax ; ja          <- start <= end
   cmp %r8,%rdx ; ja        <- end <= buf.len()
```

**R2 (`safe_naive`) adds exactly 11**, and they are four separate index checks:

```
   cmp %rsi,%rax ; jae                      <- ep      (2)
   lea (%rax),%rcx ; cmp %rsi,%rcx ; jae    <- ep+1    (3)
   lea (%rax),%rcx ; cmp %rsi,%rcx ; jae    <- ep+2    (3)
   lea (%rax),%rcx ; cmp %rsi,%rcx ; jae    <- ep+3    (3)
```

so the **per-probe safety tax is the bounds check and nothing else**: 6 for one
two-sided range check, 11 for four one-sided index checks. Note what R2 does
*not* lose: LLVM still merges its four byte loads into one `mov` (line 101 of
its listing). **Safe Rust keeps the four checks and loses none of the loads** —
which is why R2's static count is 172 against R4's 66 while its dynamic gap is
only 11 Ir/probe.

`c-gcc` adds **10 per probe**, and the mechanism is different in kind: gcc does
*not* merge the little-endian byte loads. Its probe body carries four `movzbl`
plus three `shl` plus three `add` where clang emits one `mov`.
**And it is a capability limit, not a flag default**, which `.memory` requires
to be established before any gcc-vs-clang gap is reported: `-O2`, `-O3`,
`-funroll-loops`, `-fno-strict-aliasing` and even `-march=native` all give 16
`movzbl` in the kernel and 11 667.49 Ir/call, identical to four decimal places
(the one exception, `-funroll-loops`, moves it to 11 665.49 — 2 Ir/call, from
outside the probe body). p16's gcc deficit *was* a flag default; p07's is not.

### 3b. The swept laws — exact integers, zero residual over 113 blobs

`inputs/gen.py --sweep` emits 113 blobs in three bands (band A: `2^k-1, 2^k,
2^k+1` for k = 3..14 minus k=8; band B: 64 consecutive `n` = 224..287; band C:
`nq` = 4..34 at `n` = 312). All three are needed: A and B hold `nq` at 58 so the
per-call and per-query terms are inseparable there, and C holds `n` at 312 so
the per-query and per-probe terms are inseparable there.

**The x-axis is the exact probe count, not `ceil(log2(n+1))`.** Fitting against
the ceiling gives max residuals of 600–1250 Ir/call, because the trip count is
*data*: a hit exits early at a data-dependent depth and a miss walks a path
whose length depends on where `n` sits inside its octave. The measured ratio of
actual to maximum probes runs 0.72 … 0.97 across band A.
`.temp/p07/sweep_ir.py` replays the driver's own Lemire index over calls
101..200 — exactly the calls the marginal differences — and counts probes.

Model `Ir/call = a + b*nq + c*probes`, ordinary least squares over all 113
blobs (`.temp/p07/fit3.py`):

| cell | a (per call) | b (per query) | c (per **probe**) | max residual |
|---|---:|---:|---:|---:|
| c-clang | 43.51 | 11.5275 | 11.4985 | 10.53 |
| c-gcc | 61.15 | 20.7278 | 22.5036 | 10.59 |
| safe_naive | 75.40 | 24.2240 | 23.5035 | 10.57 |
| safe_tuned | 48.40 | 17.2240 | 18.5035 | 10.57 |
| unsafe | 39.40 | 13.2240 | 12.5035 | 10.57 |
| unsafe (branchless, §11) | 42.85 | 12.5027 | **14.0000** | **0.41** |

and the **matched-spelling differences**, which are the publishable quantity
(TASK_026 §0 item 1: never a bare rate, only a matched difference — every
per-call term the two rungs share, the driver's `println!` digit term included,
cancels identically):

| difference | law | max residual over 113 blobs |
|---|---|---:|
| **R2 − R4** | `36 + 11.0000*nq + 11.0000*probes` | **0.00** |
| **R3 − R4** | `9 + 4.0000*nq + 6.0000*probes` | **0.00** |
| c-gcc − R4 | `21.75 + 7.5038*nq + 10.0001*probes` | 1.17 |
| c-clang − R4 | `4.11 − 1.6965*nq − 1.0050*probes` | 2.80 |

**Zero residual on both Rust laws, over 113 blobs spanning n = 7 … 16 385 and
nq = 4 … 58**, and the coefficients are the integers §3a counts off the
listings. Measured, not fitted-and-rounded.

Out of sample: the fit is on the 113 *sweep* blobs and predicts the two
*shipped* inputs (`small` n=312 nq=58; `large` n=262 135 nq=92, neither shape in
any band) to within **0.13%** on every cell.

**What fraction of kernel `Ir` is the search loop?** Derived from the fit rather
than asserted: `c*probes / (a + b*nq + c*probes)` = **87.8 – 89.4% on `small`
and 94.1 – 95.0% on `large`**, using the exact probe counts 462.69 and 1607.07
per call. So `nq` per window does what TASK_026 designed it to do — the driver's
own overhead is not what is being measured.

### 3c. Does R3's cost amortise? **No — and this is the first pattern where it does not.**

Every prior pattern's answer was "yes, to zero, per byte". p07's, stated as a
function of `n` over band A (nq = 58 throughout):

| n | probes/call | R3 − R4 | per probe | (R3 − R4)/R4 |
|---:|---:|---:|---:|---:|
| 7 | 155.56 | 1 174.36 | 7.5492 | 42.53% |
| 63 | 319.46 | 2 157.76 | 6.7544 | 44.88% |
| 511 | 493.77 | 3 203.62 | 6.4881 | 45.86% |
| 4 095 | 669.15 | 4 255.90 | 6.3602 | 46.36% |
| 16 385 | 786.51 | 4 960.06 | 6.3064 | **46.63%** |

- **per call** it *grows*, as `Θ(log n)`;
- **per probe** it converges to the constant 6 (from above; the excess at small
  `n` is the per-query term `4*nq` spread over fewer probes);
- **as a fraction of the kernel** it is **46.63% at n = 16 385 and still rising
  monotonically**, toward the asymptote the two per-probe constants fix:
  `6.0000 / 12.5035 = 47.99%`. It does not tend to zero and it never will,
  because both rungs' per-probe costs are constants and the per-call and
  per-query terms — the only things that could dilute the ratio — are `O(1)`
  and `O(nq)` while the probe count is `O(nq · log n)`.

So: **on p07 the safe rung's tax is a fixed fraction of the kernel, and making
the input bigger makes it slightly worse.** Every earlier pattern in this
project could amortise the check away by folding more bytes; a search cannot,
because there are no more bytes to fold — there are only more levels, and each
level pays again. That is the finding p07 was built for, and it is the first
honest counterexample to "safety is cheap" this project has produced.

**The counterweight, and it must ship with the claim: in wall clock the same
tax is +13.0% on `small` and +1.6% on `large`** (§3, and §11 shows both survive
the layout control). A 46% instruction tax that is worth 1.6% of time on the
input where the kernel actually spends its time is not the same statement as a
46% *cost*, and neither number may be quoted without the other.

---

## 4. The anti-collapse floor: probes, not bytes

**p07 is the first pattern in this project that cannot be denominated in
bytes**, and `model.py`'s `work_per_call` docstring carries the argument. Binary
search reads `4*ceil(log2 n)` bytes out of a `4n`-byte array, so on `large.bin`
a byte-denominated unit would put the derived floor at
`0.25 * 1 048 916 = 262 229` Ir/call against a kernel that legitimately executes
21 353 — the gate would fail a healthy pattern, which is the shape
`MIN_DECLARABLE_IR_PER_WORK` had when it forbade p09's bit-denominated model
(`.memory/02-bench-rules.md`).

`work_per_call = nq * ceil(log2(n+1))` probes, `work_unit = "probe"`,
`work_unit_bits = 32`. No `min_ir_per_work` is declared, so the harness default
of **0.25 Ir per probe** applies unchanged, and the argument for it is easier
than any earlier pattern's: probe *i+1*'s **address** is not known until probe
*i*'s comparison retires, so there is no vector form and no unrolled form of a
dependent search step at any `-march`. The cheapest imaginable correct
implementation is several instructions per probe, and the measured cheapest here
is 11.4985 (c-clang), 46x above the floor.

**Which way the estimate errs: STRICT**, which `.memory/02-bench-rules.md` asks
every pattern to state. `ceil(log2(n+1))` is the *maximum* trip count; measured,
the actual is 0.72–0.97 of it (0.886 on `small`, 0.971 on `large`). p16's and
p05's err strict too; p17's errs loose.

Gate stage 3b, as run: derived floor 130.5 Ir/call on `small` and 414.0 on
`large`; **64 cell/probe pairs, marginal Ir 5 993 … 215 957, tightest margin
45.9x, `d(Ir)/d(work)` 11.97 … 132.14.** No shout.

---

## 5. The proof — 10 obligations, verified first try, and zero nonlinear steps

```
$ ./verus_run.py patterns/p07-binary-search/verus.rs
verification results:: 10 verified, 0 errors

$ ./verus_run.py patterns/p07-binary-search/verus.rs --cfg slb_twin
verification results:: 11 verified, 0 errors
```

**First try, no stalls.** The one-session R5 budget went unused, as it did on
p16. Decomposition, each term measured with
`--verify-function <name> --verify-root` (this is how the `spec.md` pin was
obtained, not a formula):

| item | queries | what they are |
|---|---:|---|
| `u32_at`, `n_at`, `nq_at`, `elem_at`, `key_at`, `search_fold` | 0 each | non-recursive `spec fn` |
| `get_unchecked`, `load_input`, `emit` | 0 each | `external_body` |
| `bsearch` | 1 | recursive `spec fn`: one termination query |
| `query_walk` | 1 | recursive `spec fn`: one termination query |
| `kernel` | 3 | body + 2 loop bodies |
| `main` | 5 | quoted as measured |
| **total** | **10** | |

`.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule of thumb
predicts **7**, so it is not the derivation — the same conclusion p16, p17 and
p05 reached. `main`'s 5 carries the identical off-by-one p05's and p17's
`spec.md` record for the identical driver.

### `kernel` costs 3 and p05's costs 5, and the missing two are the finding

p05's kernel needs two `by (nonlinear_arith)` sub-proofs and one
`lemma_mul_inequality`, because its index is `i*ncol + j` — a product of two
*variables*. **Every multiplication in p07's kernel is by the literal 4**, so
every index obligation is linear:

```
q  < nq   and  4*n + 4*nq <= avail   =>  4*n + 4*q + 4 <= avail      (key)
mid < hi <= n and 4*n <= avail       =>  4*mid + 4     <= avail      (probe)
```

and Z3 takes both for free. The only ghost line inside the kernel's loops is one
`assert` naming the byte quadruple as `elem_at(mid)`, and it is there to line
the three exec arms up with `bsearch`'s three arms, not to do arithmetic.

**What p07 pays instead is the control flow.** The search exits two ways, so the
inner loop needs `invariant_except_break` plus a loop `ensures` (p16's shape),
and the invariant cannot be a closed form — there is no formula for where a
binary search is after `i` steps, because the path *is* the data. The invariant
that works is p16's *"the search from here is the whole search"*:

```rust
bsearch(buf@, off as int, key as int, lo as int, hi as int)
    == bsearch(buf@, off as int, key as int, 0, n as int)
```

with the loop `ensures` `found == bsearch(..., 0, n as int)` discharging both
exits: on `break`, `bsearch(lo,hi)` unfolds to `mid` because
`elem_at(mid) == key`; on the normal exit `lo == hi` so it unfolds to
`u64::MAX`, which is what `found` still holds. **Verus unfolds both at fuel 1
with no `reveal` and no `decreases_by`.**

**TASK_026 predicted the sticking point would be "the `usize` underflow
reasoning at `mid = 0`, which is also the bug", and that "the proof is hard
exactly where the bug is" would be a finding. It is not what happened, and the
converse is the stronger statement**: the half-open spelling *removes* that
reasoning rather than discharging it — there is no `mid - 1` to underflow, so
there is no obligation about it. **The spelling that makes the proof trivial is
the same spelling that makes the bug impossible, and choosing it cost nothing:**
no extra instruction (R4's loop is 13/12 either way), no extra obligation, no
extra TCB.

### The specification deliberately does not mention sortedness

`bsearch` specifies what the *program* returns — the half-open descent, probe by
probe — not "the position of `key` in a sorted array". Three consequences, all
deliberate:

* no `requires` about the contents of a file, which is the precondition
  `.memory/02-bench-rules.md` says no honest loader can discharge;
* `adversarial-unsorted.bin` is **inside** the verified domain, so the gate
  evaluates the contract on it like any other input and every rung agrees with
  `model.py` there (measured: all 8 cells print `6484670710166908416`);
* the row that shows correctness-violation-without-safety-violation survives. A
  stronger `ensures` would have deleted it.

The `ensures` is still load-bearing: it pins which bytes the answer is a
function of, gate stage 5c reports it as load-bearing when deleted
(`9 verified, 1 errors`), and the driver consumes it with a ghost
`assert(r == search_fold(buf@, (k * stride) as int, stride as int))`.

---

## 6. The three bugs, measured

`controls/gen_controls.py` derives four C variants from the shipped kernels by
exact-string substitution with an asserted hit count, into `.temp/p07/controls/`
(`.memory/05-layout.md` item 11's shape: a variant that must not live in the
pattern dir ships as a committed generator plus a measured section here).
Built and run by `.temp/p07/build_controls.py`.

| cell | small | adversarial-count | adversarial-width | adversarial-zero | adversarial-unsorted |
|---|---|---|---|---|---|
| R1 `c-gcc` (no length check) | ok | **exit 0, WRONG checksum** | **SIGSEGV** | ok | ok |
| R1h `c-gcc-h` (shipped, 64-bit) | ok | ok | ok | ok | ok |
| `k_u32` (check in u32) | ok | ok | **SIGSEGV** | ok | ok |
| `k_i32` (check in int) | ok | ok | **SIGSEGV** | ok | ok |
| `k_incl` (inclusive `hi`) | **SIGSEGV** | ok | ok | ok | **SIGSEGV** |
| `k_incl_nozero` (inclusive, no zero guard) | **SIGSEGV** | ok | ok | **SIGSEGV** | **SIGSEGV** |

Three separate bugs, three separate inputs, and each is invisible to the other
two's input. Reading the table:

**(1) The missing length check — and its two regimes.** `adversarial-count`
declares 4096 elements in an 88-byte window; R1's first probe is ~16 KiB past
the allocation, which is still inside the process heap, so it **exits 0 and
prints a plausible wrong number** (`250787114008174592` against the model's
`0`). `adversarial-width` declares 2^30 and lands 4 GiB out, which nothing
survives. **p02's headline result reproduces here** — idiomatic C reads memory
it does not own, prints an answer and exits 0 — *and* p07 adds the far case
beside it, on the same 88-byte window shape, so the two are not confounded with
size.

**TASK_026 predicted that a wildly out-of-bounds index would be "the easiest bug
in the project for a sanitiser to catch". Measured, and the answer is: yes, but
only because of ASan's redzones, not because of the distance.** Both inputs
fire, with *different* diagnostics: `heap-buffer-overflow` on `count` (16 KiB
out, inside ASan's poisoned heap) and `SEGV on unknown address` on `width`
(4 GiB out, unmapped shadow). Distance helps the *plain* build fail loudly and
does not change what ASan sees.

**(2) The narrow length check.** Both 32-bit spellings SIGSEGV on
`adversarial-width` where every 64-bit check returns 0, and both are correct on
`adversarial-count` — so p07 separates the width question onto its own input,
exactly as p05's `dims`/`ovf` pair does, and unlike p05 the **unsigned** 32-bit
spelling breaks too (§0).

**(3) The inclusive loop bound.** `k_incl` is `c/kernel_hardened.c` with
`hi = n`/`while lo < hi`/`hi = mid` replaced by `hi = n - 1`/`while lo <= hi`/
`hi = mid - 1` and *nothing else* — the length check is present, the zero guard
is present. It **SIGSEGVs on `small.bin`**: a query key below `elements[0]`
drives the search to `lo == hi == 0`, `mid == 0`, `hi = (size_t)-1`, and the
next probe is at index `2^63 - 1`. No attacker, no malformed header. This is
the underflow TASK_026 named, demonstrated where it actually lives.

**And `adversarial-zero` is what separates the two underflow sites.** `k_incl`
survives it (the `n == 0` guard catches it) and `k_incl_nozero` does not. So in
the *inclusive* spelling that guard is load-bearing memory safety; in the
shipped *half-open* spelling it is dead (§9). **The loop-bound spelling, not the
guard, is what makes `n == 0` safe** — and one input shows both halves.

---

## 7. Security half, per rung

Gate stage 4, all eight cells (transcript in the gate record):

| input | R1 c-gcc / c-clang | R1h both | R2 | R3 | R4 | R5 |
|---|---|---|---|---|---|---|
| `adversarial-count` | exit 0, `250787114008174592` | 0 | 0 | 0 | 0 | 0 |
| `adversarial-width` | **exit −11 (SIGSEGV)** | 0 | 0 | 0 | 0 | 0 |
| `adversarial-zero` | 0 | 0 | 0 | 0 | 0 | 0 |
| `adversarial-unsorted` | `6484670710166908416` | same | same | same | same | same |
| `adversarial-stride7` | 0 (zero kernel calls) | 0 | 0 | 0 | 0 | 0 |

ASan+UBSan (gate stage 7), `model.py` deriving the expectation rather than
tabulating it:

```
ok   adversarial-count.bin   sanitizer fired as declared (exit=1):
     AddressSanitizer: heap-buffer-overflow on address 0x508000...
ok   adversarial-width.bin   sanitizer fired as declared (exit=1):
     AddressSanitizer:DEADLYSIGNAL ... AddressSanitizer: SEGV on unknown address
ok   adversarial-stride7.bin / adversarial-unsorted.bin / adversarial-zero.bin
     / large.bin / small.bin   clean, exit=0
```

**`adversarial-unsorted` is the row worth reading.** The file breaks the
algorithm's *assumption* and nothing else: every rung stays in bounds (the
search only ever forms indices `< n`), every rung agrees with `model.py`, ASan
is silent, and the answer is simply not the answer a sorted array would have
given. It is p07's correctness-versus-safety row, and it exists because
`verus.rs` specifies what the search returns rather than where the key is (§5).
Contrast p17, whose analogous row is memory-safe *and* a disclosure.

**The cost of the check, inside one language** (R1 vs R1h, marginal Ir/call):
**+7.00 with gcc and +5.00 with clang, flat on both inputs** — 0.06% / 0.08% of
the call on `small` and 0.02% / 0.03% on `large`. So on p07, as on p02, "C is
faster" and "C is unsafe" come apart cleanly: the check is free and R1 simply
does not have it.

---

## 8. TCB, the twin, and the trusted argument

**TCB: 6 body lines across 3 items** — every `external_body` item, not just the
interesting one (`.memory/04-verus.md`: the pilot was published as "one 3-line
wrapper" and the true tally was three items, one of which was `main`).

| item | body lines | contains `unsafe`? | in the twin regime? |
|---|---:|---|---|
| `get_unchecked` | 1 | yes | **yes** — non-empty `ensures` and `unsafe` |
| `load_input` | 4 | no | no — no `ensures`, no `unsafe` |
| `emit` | 1 | no | no |

`main` is **not** `external_body` here — it is verified (5 queries), which is
what makes the kernel's `requires` discharged at a real call site
(`.memory/02-bench-rules.md` rule 2). The `#[path]`-included `common/driver.rs`
is external-by-default and reachable only through `load_input`/`emit`.

### The twin is idle again — for the fifth pattern running

`.memory/04-verus.md` records that what the verified twin uniquely catches is a
*missing conjunct* in a multi-clause trusted `requires`, and that its value
accrues from the first pattern needing a multi-clause trusted accessor — a
property of the *intrinsic being wrapped*, not of the pattern number. **p07
wraps the same single-clause `<[u8]>::get_unchecked` that p01, p02, p16, p17 and
p05 wrap, so its twin is idle too**, and a green 5c-twin here is not evidence
that anything hard was checked. It is not *nothing*: the gate re-runs the
deletion probe every time and it fails at `10 verified, 1 errors`. But that is
the demonstration p01 could have given. Manufacturing a multi-clause accessor
would be gaming the gate; the mechanism first earns its keep at p27+.

### SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

**(a) Is the twin's body the right checked stand-in for the unchecked
operation?** Yes. The trusted body is `unsafe { *v.get_unchecked(i) }` and the
twin's is `v[i]`. These are the *same* operation modulo the check: the standard
library documents `get_unchecked(i)` as equivalent to
`*v.get(i).unwrap_unchecked()` and states that calling it with `i >= len` is
undefined behaviour, so `v[i]` is its checked counterpart by construction and
not by resemblance. The twin does not reach for `get_unchecked` itself (which
would re-use the axiom it exists to check), does not loop, and is not empty —
the three toothless shapes `.memory/04-verus.md` enumerates. The gate re-derives
the substantive half on every run: with `i < v@.len()` deleted from the trusted
item's `requires`, the twin fails at `10 verified, 1 errors`, so the checked
implementation genuinely needs the conjunct rather than merely coexisting with
it.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes, and the body is one expression, which is the only reason
this can be asserted rather than argued. `unsafe { *v.get_unchecked(i) }`
performs exactly one unchecked operation — a single-byte read at index `i` — and
the postcondition `r == v@[i as int]` names exactly that byte. There is no
second read, no write, no aliasing obligation, no arithmetic on `i` inside the
body, and no interior mutability (`&[u8]`). This is the blind spot
TASK_009_REVIEW demonstrated with `let _peek = *v.get_unchecked(i + 1)`, which
passes the contract pin, the twin and the `--cfg slb_twin` run unchanged because
nothing in the `ensures` mentions the extra read; the defence here is that the
body is one line long and a reviewer can see all of it at once, plus Miri on R4
across all seven inputs (§9), plus stage 3c byte-identity, which catches R5-only
drift. **p07 raises the stakes on this in a way p05 does not**: the index handed
to this accessor is `off + 8 + 4*mid` where `mid` is computed from the *data*,
so an off-by-one in the trusted contract would not show up as a fixed shift the
way p16's and p17's would — it would fire on some queries and not others, i.e.
on a subset of the inputs Miri happens to run. That argues for re-reading these
three lines, not for a different mechanism.

**(c) Does each clause mean the same thing in the shipped configuration as in
the twin's?** Yes, and it is checked mechanically rather than asserted. The only
`#[cfg]` in `verus.rs` is the twin's own `#[cfg(slb_twin)]`, and gate stage
5c-twin verifies this before it runs Verus at all: the token `slb_twin` occurs
nowhere but on the twin's own attribute, so the shipped configuration and the
`--cfg slb_twin` one differ in nothing but the twin items themselves. That
closes TASK_009_REVIEW's `#[cfg]`-varying-`const` bypass, where
`requires in_bounds(v, i)` meant `i < len + 0` in one configuration and
`i < len + 1` in the other. Both clauses here are also literal — `i < v@.len()`
and `r == v@[i as int]` — with no named constant, no macro and no `const fn` in
either, so there is nothing for a configuration to change even if one could. The
obligation counts are pinned in **both** configurations (10 and 11), so an item
that exists only under the cfg, or a twin that quietly lost its body, moves a
pinned number.

---

## 9. Identity, Miri, dead code, and the gate

**R4 ≡ R5, byte-identical at `-O3`.** `md5_fn = 4f8c443684e1` for both,
`md5_raw` equal too, 66/64 instructions each, 4 bytes of padding each. At `O0`
the level is `norel` — the crate names differ in length so call displacements
differ, which is link layout and not codegen (`.memory/03-measurement.md`).
**This is the first time the byte-identity result covers a loop with a `break`,
an `invariant_except_break` and a loop `ensures`** — and the ghost `assert`
inside the innermost search loop erases with everything else.

**Miri: 7 of 7 inputs, no UB, and nothing is close to blocking.** Measured wall
times at `MIRI_PROBE_ITERS = 4` against the 180 s budget: `small.bin` **0.6 s**,
`large.bin` (12.0 MB) **1.9 s**, the adversarial inputs 0.1 s each — a 95x
margin on the worst row. p07 probes only `4 * work_per_call` bytes per call
(2088 on `small`, 6624 on `large`), so the entire cost is the payload `to_vec`,
which is a bulk copy (`head1_u64_bytes`). p01's `large.bin` remains the only
blocked row in the project, and it blocks for the reason
`.memory/02-bench-rules.md` records — an element-by-element payload decoder, not
size.

**Two guards are dead and both stay.**

* **`len < 8`** is unreachable given the driver's `stride_w >= 8`. Kept so the
  kernel is *total* and its `requires` stays purely structural; a `len >= 8`
  precondition would be a precondition about the driver's own guard rather than
  about the buffer. p05's `len < 4` and p17's `len < 2` are dead for the same
  reason.
* **`n == 0 || nq == 0`** changes no answer and prevents no access *in the
  half-open spelling*: with `n == 0` the loop does not run, every query folds
  `NOT_FOUND + 1 == 0`, and `n*nq == 0`. Unlike p05's zero guard it is not even
  a *work* guard, because `nq` is bounded by `avail/4`. **Its deadness is the
  result**, and §6 measures both halves: in the inclusive spelling the same line
  is the only thing between `n == 0` and `hi = SIZE_MAX`.

**`harness/check.py p07`: complete green run, first try** — 32/32 cells, 9232
kernel calls with the `requires` evaluated on every one and the `ensures`
re-derived independently on 288 of them, 5 driver loops normalising to the
pinned 12-statement sequence, and the idiom audit below.

---

## 10. The spelling spread

`.memory/05-layout.md` item 13 makes this section mandatory for any pattern with
more than one measured spelling, and `.memory/01-ladder.md` finding 3 requires
**at least two independent in-contract R3 spellings, with the cheaper quoted**.
All numbers are the whole-program marginal Ir/call.

### 10a. The R3 side — four in-contract spellings and one out

| spelling | small − R4 | large − R4 | in contract? |
|---|---:|---:|---|
| `safe_tuned` (**shipped**) `&buf[ep..ep+4]` | +3017.14 | +10019.42 | yes |
| `r3_getunwrap` `buf.get(ep..ep+4).unwrap()` | +3017.14 | +10019.42 | yes — **identical Ir** |
| `r3_prefix` `&buf[ep..][..4]` | **+2554.45** | **+8412.35** | yes — cheapest found |
| `r3_splitat` `buf[ep..].split_at(4)` | **+2554.45** | **+8412.35** | yes — identical to prefix |
| `r3_win` window resliced once per call | +2608.45 | +8500.35 | **no** — deletes `off + 8 + 4*mid` |

* **fixed-R4 bound** (`R3ship − R4ship`, R4 held by fiat — the only sound
  quantity per `.memory/01-ladder.md`): **+3017.14 / +10019.42**.
* **R3-side span**, cheapest-found to dearest-found in contract:
  **2554.45 … 3017.14 / 8412.35 … 10019.42**, width 462.69 / 1607.07 — which is
  *exactly the probe count per call*, i.e. the two spellings differ by
  **1.0000 Ir per probe** and nothing else. `r3_prefix`/`r3_splitat` drop one of
  the two `lea`s that materialise the range end.
* Write **"cheapest found"**, never "minimum": four p05/p16 minima have been
  published and all four were refuted by the next agent's first lever.
* The out-of-contract window hoist is **dearer** than the cheapest in-contract
  spelling, which is worth recording: on p05 and p16 the excluded spellings were
  cheaper, so the declaration looked like it might be protecting a number. Here
  it is not.

### 10b. The R4 side — degenerate, and the Verus verdict is why

TASK_026 §0 item 3 and `.memory/01-ladder.md`: **a rung covered by an `identity`
pin is chained to the prover**, so an R4 candidate must be put through Verus
before its number means anything. Both candidates were.

| spelling | small − R4 | large − R4 | Verus verdict |
|---|---:|---:|---|
| `r4_for` — query loop as `for q in 0..nq` | +58.00 | +92.00 | admissible (no new feature); **dearer** |
| `r4_ptr` — `as_ptr()` / `add()` / `*p` | −460.69 | −1605.07 | **DISQUALIFIED** |

```
$ ./verus_run.py .temp/p07/twin/r4_ptr_twin.rs
error: The verifier does not yet support the following Rust feature:
dereferencing a raw pointer. Currently, Verus only supports raw pointers
through the permissioned raw_ptr interface
```

That is the `is not supported` class, which is what forces a **new trusted
item** and therefore disqualifies (`postcondition not satisfied` would not).
Shipping `r4_ptr` would cost p07 a `vstd::raw_ptr` permission model on a pattern
whose entire memory-safety claim is one trusted `requires`.

**So p07's pair interval is DEGENERATE, not unavailable** — the phrasing
`.memory/01-ladder.md` requires, because it is falsifiable: the only admissible
R4 spellings measured are the shipped cell (0) and `r4_for` (+58/+92, dearer),
so the R4 endpoint has zero measured width in the cheaper direction and the
interval collapses onto §10a's R3-side span. **Third pattern in a row** — p05's
and p16's R4 sides have not moved by a single admissible instruction either, and
p07's does not either. It stops being degenerate the day somebody builds an
admissible R4 that moves.

### 10c. What the declaration actually pins — and p07 is the first that pins anything

Gate stage 0b, as run:

```
audit  34 backticked spelling(s) over 6 rung(s) -> 102 (spelling, rung) pair(s),
       71 present
audit  forbidden: 10 spelling(s), 0 hit(s)
audit  required : 0 pin nothing, 1 scoped-absent pair(s)
audit    absent  required[6]  c  c/kernel.c  `if (4 * n + 4 * nq > avail)`
```

against the six patterns that existed before it:

| pattern | backticked spellings | pairs | forbidden hits | pins nothing | scoped-absent |
|---|---:|---:|---:|---:|---:|
| p01 | **0** | 0 | 0 | 0 | 0 |
| p05 | **0** | 0 | 0 | 0 | 0 |
| p08 | 8 | 24 | 0 | 1 | 0 |
| p16 | 12 | 36 | 0 | 2 | 1 |
| p17 | 12 | 36 | 0 | 2 | 2 |
| p02 | 21 | 62 | 0 | 6 | 4 |
| **p07** | **34** | **102** | **0** | **0** | **1** |

p01's and p05's declarations backtick nothing at all, so the standard's own
audit never fires on them and their rungs are matched by prose only
(`.memory/01-ladder.md` records this). p07 pins 1.6x more spellings than the
next-best pattern with **zero** `pins_nothing` entries and exactly one
scoped-absent pair — the length check on `c/kernel.c`, which omits it by design
and whose entry's English says so. That is what "built to the standard natively"
buys, and it is a count rather than an adjective.

**Two clean negatives worth recording so nobody re-runs them.** (i) The
`forbidden` grep is doing real work here rather than passing vacuously:
`safe_tuned.rs`'s doc comment names `from_le_bytes` and `try_into` in the
sentence explaining why it does not use them, and `c/kernel.h` names
`(lo + hi) / 2`; all of them are blanked by `check.spelling_matches`'s
comment rule, which is the third shipped instance of the case that rule exists
for. (ii) `idiom_problems` accepts the 7 per-language entries; a mistyped
language key would have failed stage 0b outright.

---

## 11. The branch control — mandatory here, and it lands

This box has `perf_event_paranoid = 3` and no branch-miss counter, so any claim
about branch misprediction has to be **inferred by construction**. TASK_026 asks
for a branchless variant with `cmov` confirmed in the disassembly rather than
assumed. Confirming it turned out to be the finding.

### 11a. Every source-level branchless spelling is converted back to a branch

Three were built and measured (`controls/gen_controls.py` for the first two):

| variant | how the ordering test is written | `cmov` in `kernel` | Ir/call vs shipped |
|---|---|---:|---:|
| `u_cmov` | `lo = if lt { mid+1 } else { lo }` | **0** | **0.00 / 0.00** |
| `s_cmov` | the same on R3 | **0** | **0.00 / 0.00** |
| mask | `lo = (lo & !m) \| ((mid+1) & m)` | **0** | 0.00 / 0.00 |

All three emit a *different* `md5_fn` from the shipped rung, the same
instruction count, and **exactly the same marginal Ir**. LLVM's
`X86CmovConverterPass` exists precisely to convert `cmov` back to a branch on a
loop-carried critical path, and binary search is its canonical target.

### 11b. The control that works needs no source change at all

```
rustc ... -C llvm-args=-x86-cmov-converter=false patterns/p07-binary-search/unsafe.rs
```

on the **unchanged shipped source**. `kernel` goes 66 instructions / 0 `cmov` /
8 conditional jumps → **63 / 2 / 6**, and the search loop becomes a
straight-line 14-instruction body with one loop-closing branch and one
predictable `je` for the early exit:

```
   mov %rbx,%r10 ; sub %r11,%r10 ; shr $1,%r10 ; add %r11,%r10   <- mid
   lea (%rdx,%r10,4),%r14 ; mov (%rdi,%r14,1),%ebp               <- ep, load
   cmp %r9d,%ebp ; je            <- v == key (predictable, ~1 in 8/18)
   cmp %r9d,%ebp
   cmovae %r10,%rbx              <- hi = mid
   lea (%r10),%r10
   cmovb %r10,%r11               <- lo = mid + 1
   cmp %rbx,%r11 ; jb            <- loop
```

**14 instructions counted off the listing; the swept fit measures 14.0000
Ir/probe with max residual 0.41 over 113 blobs** — a zero-parameter derivation
matching a measurement to four decimals, and the branchless loop is
path-independent where the branchy one is not (12.5035 = the 13/12 two-path
average). This is a same-source, one-pass control, the shape
`.memory/01-ladder.md` praises for p16's `-unroll-count=1`.

### 11c. The layout control, run first, because ns is not trustworthy here

Two p07 controls with **identical** marginal Ir (`r3_prefix` and `r3_splitat`,
both 9137.43) differ by **32%** in wall clock on `small.bin`, and `c-clang` vs
`c-clang-h` differ by 21% on a 5 Ir/call difference. So before any ns inference,
`.temp/p07/layout_control.py` builds the same source at seven code alignments
(`-C llvm-args=-align-all-functions=K`, K = 0..6) — which cannot change what the
program does, and for `unsafe` does not even change the kernel bytes
(`md5_fn 4f8c443684e1` at all seven).

```
                   small.bin                        large.bin
unsafe branchy     13.457 .. 14.261 ms (5.98%)      21.595 .. 21.721 ms (0.59%)
unsafe branchless  10.668 .. 11.469 ms (7.51%)      19.362 .. 19.584 ms (1.15%)
safe_tuned branchy 15.434 .. 16.995 ms (10.12%)     21.830 .. 22.269 ms (2.01%)
safe_tuned brless  12.830 .. 14.968 ms (16.66%)     20.270 .. 20.816 ms (2.69%)
```

**Same machine code at a different address moves p07's wall clock by 6% on
`small` and 0.6% on `large`.** That is a first-class caveat and it is why the ns
column of §3 must not be read below ~6%.

### 11d. The inference, and exactly what it rests on

**On all four (rung × input) combinations the branchy and branchless bands do
not overlap:**

| | Ir | ns, worst branchless vs best branchy |
|---|---:|---:|
| `unsafe`, small | **+10.07%** | **−14.78%** |
| `unsafe`, large | **+10.94%** | **−9.31%** |
| `safe_tuned`, small | +6.90% | −3.02% |
| `safe_tuned`, large | +7.44% | −4.65% |

**`Ir` and ns disagree in DIRECTION, on the same source, with one LLVM pass
toggled**: the branchless build executes ~10% more instructions and finishes
9–18% sooner. Taking the best of each band, removing the unpredictable branch is
worth **−18.1% / −10.0%** of p07's wall clock at a cost of **+1.4965 Ir/probe**
(14.0000 − 12.5035).

**This is an inference, not a measurement, and here is exactly what it rests
on.** (i) That the wall-clock difference is *branch misprediction* and not
something else is not measured — this box has no counter, and nothing here rules
out, say, a front-end effect from the shorter loop body. What is measured is
that removing the data-dependent branch, and nothing else, is worth that much
time. (ii) `-x86-cmov-converter=false` is a whole-program flag; the driver is
inside it too. The kernel disassembly shows exactly two `cmov` appearing and two
conditional jumps disappearing, and the driver loop has no data-dependent branch
for the pass to touch, so the change is localised — but that is a reading of the
listing, not an isolation experiment. (iii) The effect is bracketed by the
layout control above rather than compared against a single build.

**What this says about `.memory/01-ladder.md` findings 5 and 6.** They were
established on p01/p02 (gcc fewer instructions, more time) and p08 (`rep`
strings). p07 adds a case where the mechanism is *the branch itself*, the
control is same-source, and the disagreement is 10 percentage points wide in one
direction and 18 in the other. It also adds the sharper corollary: **the
conversion factor from `Ir` to ns is a property of the INPUT** — R2's identical
+87.8% instruction gap is worth 28.0% of time on `small` and 3.5% on `large`.
