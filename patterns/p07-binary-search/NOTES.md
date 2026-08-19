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
   `4*(2^32-1)*2 = 34 359 738 360` and needs **35** bits
   (`2^34 = 17 179 869 184 < 34 359 738 360 < 34 359 738 368 = 2^35`; the
   "36 bits" this file, `README.md`, `verus.rs`, `c/kernel_hardened.c`,
   `inputs/gen.py`, `controls/gen_controls.py` and the hashed `idiom.why` in
   `spec.md` all carried until TASK_029 was off by one and changed no
   conclusion). In unsigned 32-bit it
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
`4n`-byte array. On `large.bin` (`n = 262 135`, `nq = 92`, so `92 * 18 = 1656`
probes) that is **6624 bytes probed out of a 1 048 916 byte window**, 0.63%.
§3 measures what happens to R3's cost as `n` grows: it does **not** go to zero.

**(b) It is the canonical unpredictable-branch kernel**, so it tests
`.memory/01-ladder.md`'s "static `Ir` is not a cost model" and "`Ir` and ns can
disagree in direction" on a kernel *designed* to make them disagree. This box
has `perf_event_paranoid = 3` and no branch-miss *hardware* counter, so the
branchless control in §11 is **mandatory rather than optional** — and §11
confirms `cmov` in the disassembly, and controls for code layout before drawing
any inference. It also has `callgrind --branch-sim`/`--cache-sim`, which p07
did not use and §11d now does.

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
| c-gcc | +77.4% | +51.9% ⚠ | +78.6% | +16.9% ⚠ |
| c-clang | −8.5% | +6.9% ⚠ | −8.3% | −1.1% ⚠ |
| R2 | **+87.8%** | ~~+28.0%~~ **withdrawn** | **+87.7%** | ~~+3.5%~~ **withdrawn** |
| R3 | **+45.9%** | **+13.0%** | **+47.0%** | **+1.6%** |
| R5 | 0.0% | −0.0% ⚠ | 0.0% | +0.3% ⚠ |

**The `Ir` columns are the result. Every `ns` cell in that table is one build at
one code layout, and §11c/§11e measure that that is not enough to carry a sign.**
Three separate qualifications, in decreasing order of how much they cost:

**(1) R2's two `ns` cells are WITHDRAWN.** They were published as *"the same
+87.8% instruction gap converts to +28.0% of wall clock on the L1-resident input
and +3.5% on the memory-bound one — an 8x difference in the conversion factor"*,
and TASK_026_REVIEW showed the sentence rested on a rung `§11c` had never built
at more than one alignment. Built at 30 layouts (§11e) `safe_naive`'s wall clock
is **bimodal**: 17.708 ms or 13.931 ms on `small`, selected by **where its
73-byte inner loop sits on the 32-byte instruction-fetch grid** — 3 windows or 4
— against R4's 14.007 / 14.062 in the same two modes. So
**R2-vs-R4 is +26.42% in one mode and −0.93% in the other**: the *sign* is a
property of where the linker put the function, and +28.0% is one of two answers.
Do not quote either number, and do not quote the `8x` ratio, which is a ratio of
two withdrawn ones. What the withdrawal does **not** touch is the `Ir` half:
+87.8% / +87.7% are exact and swept (§3b).

**(2) R3's two `ns` cells survive, and they are the ones to quote.** +13.0% and
+1.6% hold under mode-matching (+11.12% / +17.37% on `small`, +0.85% / +2.52% on
`large`) and `safe_tuned` is slower than `unsafe` at **30 of 30** layouts on
`small`. §3c's counterweight rests on these and is unaffected.

**(3) The six `ns` cells marked ⚠ — both C rungs and R5 — have no layout bracket
at all**, and the lever that produced one for the Rust rungs cannot produce one
for C:
`-align-all-functions` is an LLVM knob, so it reaches `c-clang` but not
`c-gcc`, and a `c-gcc`-vs-`rustc` comparison needs both endpoints bracketed by
the *same* lever or it is not a bracket. **`c-gcc +51.9%` is therefore an
unbracketed single-layout number exactly as R2's was**, and it is the largest
`ns` claim in the table. The symbol-ordering lever of §11e is linker-side and
would reach every rung including gcc's; nobody has run it on the C cells. Until
somebody does, read the C `ns` column as "not ranked".

**And one more, which is about `Ir` and not about layout: R5's `0.0%` is
kernel-exclusive, and whole-program it is `−1.00` Ir/call on both inputs.** R4
and R5 are byte-identical binaries in the kernel (`md5_raw` equal, §9), so their
kernel-exclusive counts *cannot* differ and the 0.0% here is the strongest form
of the claim. The −1.00 is outside the kernel, in the driver. This matters
because §3b's laws are **whole-program marginals** and this table is
**kernel-exclusive**: a reader who differences across the two conventions can
derive a contradiction that is not there (`.memory/03-measurement.md`: say which
convention a number is in, every time).

`c-clang` executes 8.5% **fewer** instructions than R4 on `small` and takes
6.9% **longer** — `Ir` and ns disagreeing in direction inside one input, on the
same LLVM backend. §11 has the layout control that says how much of that is
real; the honest version is "the two are within the layout band and the ns
column cannot rank them", and per (3) above the `c-gcc`/`c-clang` half of it has
no measured band of its own at all. **The instruction half is real and
unexplained**:
swept, `c-clang − R4` is `−1.0050` Ir per probe, i.e. clang's probe body is one
instruction shorter than rustc's on semantically identical code with the same
backend version (`.memory/00-environment.md`: clang 22.1.6 == rustc 1.97.1's
LLVM). p01 found a +2 instruction rustc-over-clang delta from an
induction-variable choice; this is the same family with the sign flipped, and I
did not chase it to the register allocator.

### 3a. The mechanism, derived from the listings with zero fitted per-probe parameters

Every rung's search loop is one basic-block chain; the per-probe numbers below
are counted off `harness/asm.py`'s normalised listing, not fitted.

**R4 (`unsafe`), the branchy shipped loop — THREE paths, not two.** LLVM rotates
the loop and duplicates the `lo < hi` test, so the `while` has **two** exit
sites and the `break` is a third. Addresses are from the `-O3 isolated` build,
instructions grouped by role with the group's first address on the left:

```
   15698  mov %r10,%r11 ; sub %rbx,%r11 ; shr $1,%r11 ; add %rbx,%r11  <- mid   (4)
   156a4  lea (%rdx,%r11,4),%r14                                       <- ep    (1)
   156a8  mov (%rdi,%r14,1),%ebp   <<< the WHOLE u32 decode, ONE instruction    (1)
   156ac  cmp %r9d,%ebp ; je 15660   <- v == key: BREAK, and that is EXIT 1     (2)
   ---- shared prefix ends: 8 instructions, every probe pays them ----
   156b1  jae 15690                  <- v > key ?                              (1)
   156b3  inc %r11 ; mov %r11,%rbx   <- lo = mid + 1                           (2)
   156b9  cmp %r10,%rbx ; jb 15698   <- lo < hi; not taken = EXIT 2            (2)
   15690  mov %r11,%r10              <- hi = mid                              (1)
   15693  cmp %r10,%rbx ; jae 156be  <- lo < hi; taken     = EXIT 3            (2)
```

so the three arms are **8 + 1 + 2 + 2 (loop test) = 13** for `lo = mid + 1`,
**8 + 1 + 1 + 2 = 12** for `hi = mid`, and **8** for the `break`. The
per-*query* constant is **16** — `1567b`'s 6-instruction head, the
8-instruction accumulate at `15663`, and the 2-instruction not-found tail at
`156be` — and a query that breaks does not execute the tail but does execute the
`inc %r11` at `15660`, so a break probe is charged `8 + 1 − 2 = ` **7**.

**What this file used to say, and why it was wrong** (TASK_026_REVIEW major 3).
It said *"`lo` path = 13, `hi` path = 12; at the 50/50 branch split the workload
produces that is 12.5 Ir/probe, and the swept fit in §3b measures 12.5035"*.
Three errors in one sentence: the workload's 50/50 is the **hit/miss** ratio and
not the branch split (measured over the sweep: `lo` **0.4591**, `hi` **0.4764**,
`break` **0.0645**); the loop has **three** exits; and 12.5035 is not a per-probe
constant at all but an **OLS slope** over blobs whose break fraction falls
0.19 → 0.037, so it is partly absorbing the changing path mix. Neither
hand-derivation at the real split reproduces it — two-path gives 12.4591,
three-path 12.1367. **A right-looking number can be a wrong derivation, and the
agreement to four decimals is what stopped anybody checking.**

**The replacement, pinned rather than fitted** (`.temp/r26/sweep_pathfit.py`, on
the same 113 sweep blobs and the same cached callgrind numbers, with an
independent per-arm probe counter that reproduces §3b's probe total on every
blob):

```
Ir/call = a + b*nq + 13*P_lo + 12*P_hi + 7*P_break        (2 free, not 3)

  unsafe       lo/hi/eq=13/12/7   a= 42.852  b= 16.0026   max|res| = 0.4127
  safe_tuned   lo/hi/eq=19/18/13  a= 51.852  b= 20.0026   max|res| = 0.4127
  safe_naive   lo/hi/eq=24/23/18  a= 78.852  b= 27.0026   max|res| = 0.4127
```

against §3b's three-free-parameter `a + b*nq + c*probes`, whose max residual is
**10.566** on all three. **A 25x better fit with one fewer free parameter and
the per-probe cost no longer fitted at all**, and `b` lands on 16.0026 against a
listing count of exactly 16.

**And it confirms the published differences instead of disturbing them**, which
is the point: the deltas come out `9 + 4*nq` with `+6` on **all three** arms for
R3, and `36 + 11*nq` with `+11` on **all three** arms for R2. The safety tax is
*path-independent* where the level is not — which is exactly why §3b's
matched-spelling differences have zero residual while its levels do not.

The residual floor of **0.4127** is identical for all three rungs and identical
to §11b's branchless row, i.e. it is a per-call term this model does not carry
and that cancels in every difference; the driver's `println!` digit term
(`.memory/03-measurement.md`: 0.2263 Ir per call per decimal digit) is the right
size for it, but I did not isolate it here.

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

**The residual column is the tell, and it was in this table before anybody read
it.** The branchless row's 0.41 and the branchy rows' 10.57 differ by 25x on the
same blobs, the same driver and the same probe counts. That is not measurement
noise — the branchless loop has **one** path, so `c*probes` is exact for it,
while the branchy ones have three and `c` is absorbing a path mix that moves
across the sweep. §3a's three-path model drops the branchy rows to the same
0.4127 floor, so this table's `c` column is a *slope*, not a per-probe cost, and
only the difference table below should be quoted.

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

### 3c. Does R3's cost amortise? **No — and p07 is the first pattern where R3's tax has no axis along which it does.**

**Scope the claim to R3, and do not write "the first counterexample to safety is
cheap".** That sentence stood here until TASK_029 and it is refuted by
`.memory/01-ladder.md` itself: finding 4 carries p16's swept **R2** tax of
**4.25 Ir per folded byte**, whose fraction also rises — toward `4.25/5.75` =
73.9% — mechanism-attributed (2.00 check + 2.25 foreclosed unroll), confirmed by
construction with `-unroll-count=1` and reproduced on p17's different kernel;
finding 6 carries p05's `O(nrow)` **R3** tax, of which that file says in its own
words *"the cost is `O(nrow)`, **not** zero"*. p16's R2 story is structurally
identical to the one below, one rung down and measured first.

**What is a first, stated precisely: p07 is the first pattern where R3's tax has
no axis along which it amortises.**

| pattern | R3 − R4 | the axis it amortises along |
|---|---|---|
| p16 / p17 | a per-**call** constant, **0.00000 Ir/byte** swept | any — the reslice sits *outside* the fold loop |
| p05 | `6*nrow + 9`, i.e. `O(nrow)` | `ncol`: it vanishes as rows get wider |
| **p07** | **6.0000 Ir per probe**, `probes = nq·⌈log2 n⌉` | **none** — there is no inner loop to hoist it out of, so the fraction rises in **both** `n` and `nq` |

That, and not "safety is expensive here", is the finding — and it says the six
earlier answers were a property of the **loop shape** those kernels shared.

p07's, stated as a function of `n` over band A (nq = 58 throughout):

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
  monotonically**. It does not tend to zero and it never will, because both
  rungs' per-probe costs are constants and the per-call and per-query terms —
  the only things that could dilute the ratio — are `O(1)` and `O(nq)` while the
  probe count is `O(nq · log n)`.

**The asymptote is a property of the kernel AND the query distribution, so quote
it with the workload.** §3a's three-path form makes R4's per-probe cost
`12 + f_lo` where `f_lo` is the fraction of probes taking the `lo = mid + 1`
arm, so the asymptote is `6 / (12 + f_lo)` — and `f_lo` is *data*. Measured
marginals per probe on two degenerate workloads: **12.0017** on all-below-min
keys (pure `hi = mid` arm, `f_lo = 0`) and **13.0026** on all-above-max keys
(pure `lo` arm, `f_lo = 1`), so

```
asymptote  =  6 / (12 + f_lo)  in  [46.15%, 50.00%]
                                    47.99% on the shipped 50/50-hit workload
```

Until TASK_029 this file quoted `6.0000 / 12.5035 = 47.99%` as if the kernel
fixed it; 12.5035 was §3b's OLS slope on the shipped workload (§3a), so 47.99%
was a property of `inputs/gen.py` quoted as a property of binary search.

**Confirmed across six deliberately different workloads** (TASK_026_REVIEW,
`.temp/r26/altwork.py`, 30 blobs × 6 distributions, same element arrays, nq = 58):

| workload | probes/call at n=16 385 | R4 `Ir`/probe ¹ | (R3−R4)/R4 |
|---|---:|---:|---:|
| shipped (50% hit) | 781.52 | 13.5396 | 46.59% |
| all-miss | 812.08 | 13.6893 | 46.00% |
| all-hit | 754.34 | 13.3639 | 47.29% |
| all-below-min | 870.00 | 13.1164 | 47.86% |
| all-above-max | 812.00 | 14.1962 | 44.36% |
| clustered | 782.75 | 13.2975 | 47.44% |

¹ whole kernel divided by probes, so it carries the per-call and per-query terms
too — it is not the per-probe *marginal*, which is the `12 + f_lo` above. That is
why `allbelow`'s 13.1164 sits above its own marginal of 12.0017.

**Monotone rising in `n` in all six.** No workload flattens it and none reverses
it; what the workload moves is *where inside [46.15%, 50.00%]* it is heading.
And the exact-integer laws of §3b were re-verified **out of sample** on those 30
fresh blobs with an independent probe counter, to the integer, 30/30.

So: **on p07 the safe rung's tax is a fixed fraction of the kernel, and making
the input bigger makes it slightly worse.** Every earlier pattern in this
project could amortise the *R3* check away by folding more bytes; a search
cannot, because there are no more bytes to fold — there are only more levels,
and each level pays again.

**The counterweight, and it must ship with the claim: in wall clock the same
tax is +13.0% on `small` and +1.6% on `large`** (§3). Those are the two `ns`
cells that survive bracketing — §11e shows `safe_tuned` slower than `unsafe` at
30 of 30 code layouts on `small`, and mode-matched at +11.12% / +17.37% — while
R2's, on the same table, do not (§3 (1)). A 46% instruction tax that is worth
1.6% of time on the input where the kernel actually spends its time is not the
same statement as a 46% *cost*, and neither number may be quoted without the
other.

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
`large`; **64 cell/probe pairs, marginal Ir 6 021 … 216 053, tightest margin
46.1x, `d(Ir)/d(work)` 11.96 … 131.97.** No shout.

⚠ **Those figures were wrong here until TASK_029, and the way they were wrong is
worth one sentence** (TASK_026_REVIEW minor 5). Until then this paragraph quoted
`5 993 … 215 957 / 45.9x / 11.97 … 132.14`, which came from `gate1.log` and
`gate2.log` — both run at 07:07 and 07:10, *before* `inputs/` was regenerated at
07:30 for the §1 workload fix. `gate3`–`gate6` and the review's independent run
all give the values above. §1 already records that the miss-drawing defect made a
section's claim false; what it did **not** record is that the fix silently
invalidated every number measured off the old blobs, and one of them survived the
sweep into §4. **When an input generator changes, re-derive every measured number
in the file, not just the ones the change was about.**

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
before its number means anything. Both candidates now have a twin in
`controls/gen_controls.py` and both have been run.

| spelling | small − R4 | large − R4 | Verus verdict |
|---|---:|---:|---|
| `r4_for` — query loop as `for q in 0..nq` | +58.00 | +92.00 | **`10 verified, 0 errors`** — admissible, and **dearer** |
| `r4_ptr` — `as_ptr()` / `add()` / `*p` | −460.69 | −1605.07 | **DISQUALIFIED** |

```
$ ./verus_run.py .temp/p07/controls/r4_for_twin.rs
verification results:: 10 verified, 0 errors

$ ./verus_run.py .temp/p07/controls/r4_ptr_twin.rs
error: The verifier does not yet support the following Rust feature:
dereferencing a raw pointer. Currently, Verus only supports raw pointers
through the permissioned raw_ptr interface
```

⚠ **This paragraph said "Both candidates were" before TASK_029 and it was
false** (TASK_026_REVIEW minor 4). `gen_controls.py` generated `r4_ptr_twin`
only, so `r4_for`'s "admissible (no new feature)" was an *inspection* standing
beside somebody else's Verus run, in the one place on the R4 side where an
inspection is exactly what the rule forbids. The reviewer built the missing twin
and it verifies — the verdict was right and the claim of having checked it was
not — and `r4_for_twin` is now generated here so the next reader does not have
to take it on trust. The same review also found that this block cited
`.temp/p07/twin/r4_ptr_twin.rs`, a path that never existed; the generator writes
to `.temp/p07/controls/`. **A wrong path and an unrun check look identical from
outside, which is the argument for the generator over the prose.** Also worth
recording: the `for` spelling costs **no obligations** either — 10, the same as
the shipped `while` — because Verus derives `q <= nq` and the `decreases` for a
range `for`, so the two Verus-only edits the twin needs are deletions.

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

This box has `perf_event_paranoid = 3` and no branch-miss **hardware** counter,
so TASK_026 asked for the claim to be **inferred by construction**: a branchless
variant with `cmov` confirmed in the disassembly rather than assumed. Confirming
it turned out to be the finding.

⚠ **"No counter" was over-read, and it cost this section a whole control.**
`valgrind --tool=callgrind --branch-sim=yes` reports simulated `Bc`/`Bcm` and
runs here; §11d now uses it, and it answers directly what §11a–§11c were built
to establish by construction. The `cmov` control keeps its value — it is a
*causal* lever where the simulator is an *observation*, and §11a's result that
LLVM converts every source-level branchless spelling back to a branch is not
something a counter could have found — but it was not the only instrument
available, and the section was written as if it were
(`.memory/00-environment.md`).

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
path-independent where the branchy one is not — which is why 14.0000 is a real
per-probe constant and the branchy 12.5035 is not (§3a: the branchy loop's three
arms cost 13 / 12 / 7 and 12.5035 is an OLS slope over a moving path mix). This
is a same-source, one-pass control, the shape `.memory/01-ladder.md` praises for
p16's `-unroll-count=1`.

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

⚠ **This control was run on `unsafe` and `safe_tuned` only, and the rung it did
not cover is the one §3's bolded headline rested on.** `safe_naive` was never
built at more than one alignment here. TASK_026_REVIEW built it at seven
(`.temp/r26/layout_r2.py`, identical marginal `Ir/call` 12346.57 at every one)
and got a **28.47%** band on `small.bin` — **the widest single-rung band this
project has measured**, and of the same order as the 21% and 32% figures this
section opens with, which are across *different programs* rather than one
program at seven addresses:

```
-- small.bin, 31 reps interleaved, taskset -c 3
   >> safe_naive: layout band 14.038..18.034 ms  spread 28.47%
   >> safe_tuned: layout band 15.378..16.999 ms  spread 10.54%
   >> unsafe:     layout band 13.450..14.139 ms  spread  5.12%
```

§11e is what that band turns out to be made of, and it is not a band.

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

**This section said "this is an inference, not a measurement" and named two
caveats. Both are now closed, and by a flag that was available the whole
time.** `.memory/00-environment.md`'s "no hardware counters" was read across this
project for 28 tasks as *branch misprediction is unmeasurable here*, which is why
the `cmov` control above was built to infer by construction what one flag
reports directly:

```
valgrind --tool=callgrind --branch-sim=yes   ->  Bc, Bcm, Bi, Bim
valgrind --tool=callgrind --cache-sim=yes    ->  D1mr, DLmr, I1mr, ...
```

Both run on this box (valgrind 3.27.1). Measured on the branchy/branchless pair
(`.temp/r26/branchsim.py`), marginal per call:

| build | input | `Ir` | `Bc` | `Bcm` | `Bcm/Bc` | `Bcm`/probe |
|---|---|---:|---:|---:|---:|---:|
| unsafe branchy | small | 6582.98 | 1392.09 | 271.16 | 0.1948 | **0.5861** |
| unsafe branchless | small | 7245.77 | 958.40 | 59.45 | 0.0620 | 0.1285 |
| unsafe branchy | large | 21356.70 | 4825.21 | 853.98 | 0.1770 | **0.5314** |
| unsafe branchless | large | 23691.98 | 3264.14 | 93.07 | 0.0285 | 0.0579 |

**+10.07% `Ir` buys −78.1% simulated mispredicts on `small` and −89.1% on
`large`**, and **0.586 mispredicts per probe is what a coin-flip branch should
give** — which is the sanity check that the simulator is modelling the right
thing rather than the claim itself.

**Caveat (i), the front end and locality, is narrowed rather than argued.**
`--cache-sim=yes` (`.temp/r26/cachesim.py`) says the lever is
**locality-neutral**: `D1mr` is **1076.82 on `large` for both builds** and `DLmr`
is equal too. Only the branch counters move. What is still *not* excluded is a
decode/uop-throughput effect from the shorter body — simulation cannot see the
front end — so the data-cache explanation is dead and the front-end one is not.

**Caveat (ii), the whole-program flag, is now an isolation experiment.** A
symbol-by-symbol instruction-stream diff of the two whole binaries finds **559
symbols and exactly one different**: `kernel`, 70 → 68 raw instructions. The
driver, libstd and the startup path are bit-identical, so the flag changed the
kernel and nothing else — measured, not read off a listing.

**Say what the simulator is, every time you quote it.** Callgrind's predictor is
a generic two-level scheme, **not this CPU's**; `Bcm` is *simulated* and must
never be converted to cycles without saying so. It is strong evidence about
**direction and ratio**, weak about **magnitude**
(`.memory/00-environment.md`). Both simulators also slow callgrind down
substantially, so they are for a named question on a few cells, not for a matrix.

**And a lever that needs no flag and no simulator at all: the workload.** Same
binary, same alignment, same element arrays — only the query distribution
changes (`.temp/r26/worklever.py`, n = 16 385):

| workload | probes/call | `Ir`/call | `D1mr` | `Bcm` | ns/call | ns/probe |
|---|---:|---:|---:|---:|---:|---:|
| shipped | 781.52 | 10581.50 | 300.52 | 422.78 | 2817.3 | 3.6049 |
| clustered | 782.75 | 10408.58 | 1.60 | 273.35 | 1653.2 | 2.1121 |
| all-below-min | 870.00 | 11411.30 | 0.13 | 59.02 | 795.9 | 0.9148 |

**`allbelow` executes +7.84% more instructions and takes 71.75% less time than
the shipped workload on a byte-identical program** — a sharper `Ir`-vs-ns
direction reversal than the compiler flag produced, and available on any
data-dependent kernel. `cluster` separates locality from branches: with `D1mr`
at ~0 for both, the extra 214.3 mispredicts/call cost 857.3 ns/call ≈ **4.0 ns ≈
14 cycles per simulated mispredict**, the textbook penalty. That last figure is
an *attribution*, not an isolation — the predictable workload also gains
cross-probe speculation.

Caveat (iii) stands unchanged: the effect is bracketed by the layout control
above rather than compared against a single build.

**What this says about `.memory/01-ladder.md` findings 5 and 6.** They were
established on p01/p02 (gcc fewer instructions, more time) and p08 (`rep`
strings). p07 adds a case where the mechanism is *the branch itself*, the
control is same-source, and the disagreement is 10 percentage points wide in one
direction and 18 in the other. The sharper corollary this section used to draw —
*"the conversion factor from `Ir` to ns is a property of the INPUT: R2's
identical +87.8% instruction gap is worth 28.0% of time on `small` and 3.5% on
`large`"* — **is withdrawn with the numbers it rests on** (§3 (1)). The corollary
survives on better evidence: the workload table above makes the same point on a
**byte-identical** program, where R2-vs-R4 changed the program.

### 11e. What the layout band is MADE OF: one address bit, and no counter sees it

TASK_029. §11c brackets an `ns` claim by taking the *range* over seven
alignments. Two things were never checked about that: whether the range is a
converging statistic, and what the spread is made of. Both are now measured
(`.temp/p29/layout_wide.py`, `layout_shape.py`, `modesim.py`).

**A second layout lever, and it is much stronger than alignment.** rust-lld
takes `--symbol-ordering-file`, so the same source can be built with the binary's
582 text symbols in a pseudo-random order:

```
rustc ... -C link-arg=-Wl,--symbol-ordering-file=<permutation of the 582 symbols>
```

Nine alignments (`-align-all-functions=0..8`) plus 21 random orderings is 30
layouts per rung; they put `unsafe`'s `kernel` at 28 distinct addresses spanning
`0x15600 … 0x518f0`, where alignment alone moves it inside `0x300`. `n_fn` and
the executed instruction stream are unchanged. **Control, and it must be run
before anything else**: the marginal `Ir/call` is *exactly* invariant over all 30
layouts of each rung — 12346.57 (R2) / 9600.12 (R3) / 6582.98 (R4), one value
each, not a range.

⚠ **A correction to the recipe while we are here.** `md5_fn` is invariant across
layouts for `unsafe` **only**. R2's and R3's kernels contain a `call` to the
panic path, so their `md5_fn` moves with the call displacement — 28 distinct
digests over the 30 layouts — while `n_fn` (172, 99) does not. `md5_fn_norel`,
which zeroes the pc-relative displacement fields, *is* invariant; measured on the
minimal pair used below:

```
safe_naive -align-all-functions=1   n_fn=172  md5_fn 13f8c1575bec  md5_fn_norel bf70816958ed
safe_naive -align-all-functions=2   n_fn=172  md5_fn f7463bbc1d17  md5_fn_norel bf70816958ed
```

So any "byte-identical machine code at a different address" check on a rung that
can panic must use `md5_fn_norel`; `md5_fn` will fail it for the right reason and
the wrong conclusion.

**The band is not a band. It is two modes, and the property that selects them is
the loop's position on the 32-byte instruction-fetch grid.** Grouping the 30
layouts by `kernel_addr % 32` on `small.bin` — which is a *proxy* for that
property, see the box below — gives:

| rung | `%32 == 0` | `%32 == 16` | mode gap |
|---|---:|---:|---:|
| `safe_naive` (R2) | **17.708 ms** (n=18) | **13.931 ms** (n=12) | **27.1%** |
| `safe_tuned` (R3) | 15.563 ms (n=15) | 16.505 ms (n=15) | 6.1%, opposite sign |
| `unsafe` (R4) | 14.007 ms (n=15) | 14.062 ms (n=15) | 0.4% |

For R2 the separation is **perfect**: the fastest slow-mode layout is 16.993 ms
and the slowest fast-mode one is 14.766 ms, so the largest-gap clustering of the
30 timings and the bit-4 partition are **the same partition**, 30 of 30. It is
not noise and it is not a gradient — and which residue is fast depends on the
rung's own loop geometry rather than on a universal rule.

⚠ **"Bit 4 of the kernel's entry address" is a PROXY, and this section used to
publish it as the law** (corrected at TASK_030_REVIEW, landed TASK_031). Every
kernel here is 16-byte aligned, so any 32-byte-granular property of the code can
only take two values and *looks* like one address bit. It is not the entry
address that matters — p01's mode is set by a loop at `+0x40`, and p07's by one
at `+0x148` — and a toolchain that aligned functions to 32 bytes would erase the
proxy while leaving the effect untouched. Partition by the geometry computed
from the listing, never by an address bit.

**The mechanism is the 32-byte instruction-fetch / DSB window grid**, in two
forms, both computed from the recorded addresses with **zero fitted parameters**
(`.temp/r30/loopfit.py`; `.memory/03-measurement.md`, "Code layout: the 32-byte
fetch grid"):

- **`win32`** — the loop body occupies one more 32-byte fetch window in one
  layout than in the other;
- **`jcc32`** — a branch in the loop crosses or ends on a 32-byte boundary, so
  its chunk is not cached in the DSB. This box is **Cascade Lake, family 6 model
  85 stepping 7, microcode `0x5000024`** — the mitigated microcode for the Jump
  Conditional Code erratum, **Intel SKX102**.

On p07, enumerating **every** loop in the kernel rather than guessing one:

```
safe_naive loop3 [kernel+0x148,+0x191)  73 B  win32[3,4]  small x0.7863 / x0.7825 / x0.7865  PERFECT (3 passes)
                                                          large x0.9700 / x0.9686 / x0.9707  PERFECT
safe_naive loop2 [kernel+0x140,+0x186)  70 B  jcc32[0,1]  small x1.2718 / x1.2780 / x1.2714  PERFECT
safe_tuned loop2 [kernel+0xa0, +0xd4)   52 B  win32[2,3]  small x1.0605 … x1.0657
```

**§11e's own geometric negative used the wrong loop and the wrong property, and
the geometry points the right way once both are fixed.** The retracted sentence
read: *"`.temp/p29/fetchwin.py` counts the loop geometry off both listings and
R2's innermost search loop (70 bytes, 23 instructions) spans 3 32-byte fetch
windows and 2 64-byte lines in both modes … the one geometric difference there
points the wrong way."* Two errors:

- the 70-byte loop `[+0x140,+0x186)` does span 3 windows in both modes — but its
  fused `cmp;je` crosses a 32-byte boundary in **exactly one** mode, which is the
  `jcc32` form and which that count never looked at;
- there is a **second back-edge**, `[+0x148,+0x191)`, 73 bytes, and it *does* go
  **3 → 4 windows**. That is the loop the mode is on.

**Record why the wrong loop was picked, because it will happen again**: a
"tightest backward branch" heuristic (`.temp/r30/jcc.py`) finds the smallest
back-edge, and on any vectorised kernel that is the **scalar tail**, not the hot
body — on p01 it picks the 12-byte scalar tail instead of the 30-byte SSE loop.
`.temp/r30/loopfit.py` exists because of this and enumerates all of them.

**No counter this box can produce ranks it.** The minimal pair is
`-align-all-functions=1` vs `=2`, which moves R2's kernel by exactly 16 bytes and
changes nothing else (`md5_fn_norel` equal, `n_fn` 172 both). Per-call marginals
on that pair:

```
event      align1(%32=0)  align2(%32=16)      delta
Ir             12346.57       12346.57         0.00
Dr               530.71         530.71         0.00
Dw                 6.01           6.01         0.00
I1mr / D1mr / D1mw / ILmr / DLmr / DLmw   all 0.00 both     0.00
Bc              3482.85        3482.85         0.00
Bcm              273.93         273.92        -0.01
Bi / Bim               0              0         0.00
```

⚠ **Those zeros are per-call marginals rounded to two decimals, and this
section previously over-read them as "the simulators are blind to code layout".**
They are not blind; they are blind to the *front end*. Whole-program absolute
totals on the same pair (`.temp/r30/modesim2.py`):

```
Ir 99054451 both (+0.0000%)   Dr, Dw, Bc, Bi, Bim  all +0.0000%
I1mr 1875 -> 1881 (+6)   ILmr 1830 -> 1835 (+5)   D1mr 2608 -> 2603 (-5)
D1mw 1184 -> 1182 (-2)   DLmr 1808 -> 1807 (-1)   DLmw 1101 -> 1102 (+1)
Bcm  2184897 -> 2184900 (+3)
```

Callgrind's cache model is address-indexed and its branch predictor
address-hashed, so both register the move — by **≤ 6 events in 10⁸**, across a
27% wall-clock mode. **A 27% mode, and the executed instruction stream, the data
reads and every simulated cache and predictor counter are the same to six
events.** Use the simulators to attribute a cache or branch mechanism; never to
detect or rank a layout effect. That is still the sharpest form of §11d's
surviving caveat — the *only* instrument on this box that sees the effect is the
wall clock — but the reason is the missing front-end model, not blindness to
addresses.

**Out of sample, pre-registered.** Predictions written and SHA-256'd
(`5fd5ebdce09bef14113dab07abc42d8e1e18696b2503b4a27c9e100b12fdc678`) **before
any timing**, on 20 fresh symbol orderings the hypothesis had never seen:
`safe_naive`'s `jcc32` rule **held with perfect separation on both passes**
(×1.2932 / ×1.2896); `safe_tuned`'s overlapped by one pair (×1.0767 / ×1.0784).
Building with `-C llvm-args=-x86-branches-within-32B-boundaries` collapses R3's
band from **17.12% to 4.00%** and makes it **18.6% faster overall** (median
15.75 → 12.82 ms), R2's from 31.76% to 13.82% — evidence, not proof, because the
flag also forces 32-byte function alignment (so bit 4 is pinned by construction)
and it does not touch the `win32` form.

**Consequence 1 — R2's `ns` sign is a property of the linker, and that is why §3
withdraws it.** Mode-matched against R4:

| | `%32 == 0` | `%32 == 16` | |
|---|---:|---:|---|
| R2 vs R4, `small` | **+26.42%** | **−0.93%** | **SIGN FLIPS** |
| R3 vs R4, `small` | +11.12% | +17.37% | same sign |
| R2 vs R4, `large` | +3.34% | +0.47% | same sign |
| R3 vs R4, `large` | +0.85% | +2.52% | same sign |

R2 is faster than the *worst* R4 layout at 11 of its 30 layouts on `small`; R3 at
**0 of 30**. So R3's counterweight is not merely "bands disjoint" — it is
dominance, at every layout measured, in both modes.

**Consequence 2, and it is a methodological one: the worst-vs-best RANGE is not a
converging statistic, so a rule phrased on it is a rule about sample size.**
Adding layout samples can only widen a range, never narrow it:

| | 7 alignments (§11c's lever) | 30 layouts |
|---|---|---|
| `safe_naive` band, `small` | 28.91% | **30.78%** |
| R2 vs R4 interval, `small` | [−1.84%, +33.65%] OVERLAP | [−4.67%, +33.80%] OVERLAP |
| **R3 vs R4 interval, `large`** | **[+0.72%, +3.12%] DISJOINT** | **[−0.14%, +4.42%] OVERLAP** |

The last row is the one to notice: **the R3 `large` comparison passes the
disjoint-bands test at seven layouts and fails it at thirty, with no
disagreement between the two measurements.** It is the same rung, the same
binaries, the same machine — only the number of layouts sampled changed. So
"bands must be disjoint before a sign is asserted" retracts a true claim as soon
as somebody is more thorough. One statistic does *not* move that way:

* **mode-matching** — group by the 32-byte geometry (`win32` / `jcc32`; the
  address bit is the proxy for it) and compare inside a mode. Keeps R3's sign on
  both inputs (`small` +11.12% / +17.37%, `large` +0.85% / +2.52%) and correctly
  refuses R2's on `small`. Subsampled 400 times per size, its medians are **flat
  in `N`** with spread ~1/√N — it converges.

⚠ **A second statistic this section proposed — "dominance", *slower than the
worst layout of the other rung at k of N* — is RETRACTED** (TASK_030_REVIEW
major 3, landed TASK_031). It was offered here as a proportion rather than an
extreme, and it is not: it is defined against `max(B)`, an **extremum of B**, so
it inherits the exact defect of the range it was introduced to replace.
Subsampled, it **drifts** — p01's R2 goes 28.7% at `N = 4` to 13.3% at `N = 30`,
sd **±26 points** at `N = 4`; p07's R3 on `large` 94.8% → 90.0%. The replacement
that does converge is **pairwise `P(A > B)`** over all `N²` layout pairs, a
genuine proportion, flat at every `N` (58.1 → 58.4, 97.4 → 97.3, 73.9 → 74.7
across `N` = 4…30). The dominance figures already published in this file
(R3 slower than the worst R4 layout at 30 of 30 on `small`, 29 of 30 on `large`;
R2 at 19 and 23 of 30) are **measurements at `N = 30` and are true as such** —
they are simply not a statistic to state a rule on.

Publish the range as a *worst case* if you like; do not publish it as *the*
interval, and do not let a rule stated on it decide what may be claimed.

Numbers reproduce `.temp/r26/layout_r2.py` closely: 28.91% here against 28.47%
there, `safe_naive` 13.977…18.017 against 14.038…18.034.

### 11f. The R4 rung has an 8% layout band that nothing here explains — OPEN

**TASK_030_REVIEW minor 8, measured further at TASK_031. This is an open
problem, recorded because it is larger than several published gaps.**

§11e's table records `unsafe` as *"14.007 / 14.062 ms, 0.4%, no mode"*. That is
the **bit-4 mode gap**, not the band. The band is:

```
unsafe, small.bin, 30 layouts:  13.453..14.540 ms  spread  8.08%   (pass 0, cpu 3)
                                13.443..14.530     spread  8.09%   (pass 1, cpu 3)
                                13.422..14.452     spread  7.68%   (pass 2, cpu 5)
cross-pass reproducibility:     spearman rho +0.922 / +0.960 / +0.931
```

**It is reproducible, it is not explained, and it is not noise.** What has been
ruled out:

- **any address bit** — the best is `bit5` at ×0.9809, and it *overlaps*; no bit
  gives a perfect split, unlike R2's ×0.7863;
- **`jcc32`** — it flips on R4 (`%32=0` → 0 hits, `%32=16` → 1 hit) and buys
  **+0.5%**. On this rung a JCC hit is necessary but nowhere near sufficient;
- **measurement noise.** TASK_031 timed **31 byte-identical copies** of the
  shipped `unsafe` binary (distinct inodes, one layout) in the same harness, two
  passes × two round-robin orders: the spread is **1.10 / 1.14 / 1.24 / 1.54%**
  (all three rungs together, 0.83 … 2.24% — `.temp/p31/order.py`,
  `order_p07.log`). The 8% band is ~5–6× that floor, and
  the per-layout ranking reproduces across passes at ρ ≈ +0.93 while identical
  copies do not rank at all.
- **the round-robin's order**, which is a real artefact elsewhere (it is what
  p05's `NOTES.md` §4b is about): p07's R2-vs-R4 and R3-vs-R4 medians on
  identical copies are +27.46 / +27.67 / +27.67 / +27.77% and +12.42 / +12.65 /
  +12.42 / +12.60% — **identical under alternating and blocked ordering**, so
  p07's timing is protocol-insensitive and this band is not a harness artefact.

So R4 spans 8% across layouts with no mode, no bit, no geometric predictor and a
1.5% noise floor. Two consequences worth stating plainly: **(a)** it is larger
than R3's published `large` gap (+1.6%) and than most C-vs-Rust `ns` differences
in this table, so it is a live threat to any *un*bracketed `ns` claim on this
pattern; and **(b)** it is why R2's mode is quoted mode-matched rather than
against R4's minimum — R4's own minimum is a draw from an 8%-wide distribution
that nobody can predict.
