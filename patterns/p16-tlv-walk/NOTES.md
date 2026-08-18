# p16 — findings, adversarial behaviour, TCB tally, sticking points

> **Read §0 first.** This pattern's headline is a perf claim, and the last time
> this project published one from a whole-kernel delta it had to retract it. §3
> is the decomposition; §2 is the number; §0 is what the number is *of*.

**The one-line result.** *(Corrected at TASK_007_REVIEW — the original wording,
"the first true O(n) safety cost this project has measured", **overclaimed**, and
broke this project's own standing rule that no safety-cost claim ships without
R3. What follows is the corrected statement.)*

**One *spelling* of safe Rust pays an O(n) tax here. Idiomatic safe Rust does
not.** R3's marginal rate is **5.7500 Ir per folded byte — R4's exactly**: zero
per byte. R3's whole cost is **`7 + 5·nrec` when the value length is ≡ 0 (mod 4)
and `7 + 7·nrec` otherwise** — the two shipped points, +27 and +77, are `nrec` 4
and 10 — so it is **O(records) and not O(1) per call**, while still being 0 per
*byte*, and it shrinks as a fraction of the call as the records grow (0.90% on
`small`, 0.32% on `large`).

⚠ **"O(1) per call" is what this paragraph said until TASK_016, and it was
wrong.** §2 and §3b below have carried `7 + 7·nrec` since TASK_007 — the
headline contradicted its own decomposition four sections down, which is this
project's most repeated defect (`.memory/01-ladder.md` finding 5 has the same
shape on p17). TASK_015_REVIEW M1 is what caught it, by running the 68 sweep
blobs p16 already ships against both rungs; the same review also refuted a
`nrec + 3` figure that had been fitted to three points, all of which sat at the
one residue class where the slope is invisible. **Sweep, do not sample**, and
when a headline and a decomposition disagree, the decomposition is the one that
was measured.

⚠ **And `+27 / +77` bounds nothing except against the shipped R4 (TASK_018 and
TASK_023, §10a).** Three alternate R3 spellings that keep **both** of
`spec.md`'s named comparisons literally, and change only the header read and the
value fold — the two things the declaration says it does *not* restrict — span
**42 `Ir`/call at `large` against the published 77**, the cheapest sitting at
`+45`. **TASK_023 then searched the R4 side and it moves too**, by the same
lever: `R4ship − r4_hdr = 4·nrec`, zero residual over 24 blobs. So the
admissible **pair** `(r3_hdrarray, r4_hdr)` **exceeds** the published tax by
`5·nrec` — 47 against 27 at `small`, 127 against 77 at `large` — and `+27 / +77`
is not an upper bound on p16's in-contract safety tax either. Pinning the
comparison tokens narrows the admissible class; it does not
pick a point in it, and the claim that it "makes `R3 − R4` a difference in
safety rather than in representation" is withdrawn.

What is O(n) is the **naive indexed spelling**, R2: +4.25 Ir per folded byte,
+69% / +72% over unsafe. The decomposition (§3) puts all of it in the *value
fold* and none in the walk, and — confirmed by construction with a
rolled-vs-rolled control (§3.4) — **only 2.00 of the 4.25 is the bounds check;
2.25 is a 4× unroll the check forecloses.**

It costs **nothing in wall clock**: +72% `Ir` → **+0.27%** time, spreads
0.96–2.31%, because the fold is latency-bound on a serial Horner chain. The
per-byte *time* is identical on L1-resident `small` and L3-resident `large`,
which rules out the memory-bandwidth explanation.

⚠ **The "~3.03 cycles/byte" this section used to quote is an inference, not a
measurement, and it is now qualified (TASK_012; landed here at TASK_013).** It
converts a wall time measured at TASK_007 with a clock measured at
TASK_007_REVIEW — *different sessions* — and this box's clock is set by other
tenants: the same dependent-chain probe read 3.80–3.89 GHz in one session and
2.55–2.86 GHz in another (`.memory/00-environment.md`). At all-core turbo the
same ns figure is ~2.2 cycles/byte. **The ns figures and the null result above
stand** — they are ratios and levels taken inside one session — and so does the
Horner-chain mechanism, which has a hard 3-cycle serial latency floor
independent of the clock. Only the cycles/byte conversion is withdrawn as a
measurement. See §2.

All four claims are the result; quoting any one alone would misrepresent it —
and the first of them is the one that matters, because it is the one that says
the first three patterns' conclusion still stands.

## 0. What p16 is for, and what its numbers are of

Every perf result on this project so far says the same thing: **safety is cheap
when the optimiser can see the loop.** p01's R3 lands +4…+5 Ir/call of unsafe,
flat; p02's R3 lands +10, flat; p02 *looked* like the exception and was not —
its R2 delta turned out to be a lost `memcpy` idiom rather than a bounds-check
tax, and `.memory/01-ladder.md` carries the retraction.

`.memory/01-ladder.md` also says, in as many words: *do not generalise any of
this to patterns with data-dependent indices — the interesting patterns are
precisely the ones where LLVM cannot hoist.*

**p16 is the first honest test of that sentence.** Its kernel walks a chain of
length-prefixed records inside a window: the trip count comes from the data,
each record's position depends on every previous record's length field, and the
fold index is loop-carried through a value the attacker wrote. There is no
loop-invariant bound for LLVM to hoist and no `memcpy` idiom to lose.

Two things this file is careful about, both because of p02:

- the perf claim in §2 **names a loop**, and §3 is the decomposition that
  earns it — five variants, one loop changed at a time, built under `.temp/`
  and never shipped as rungs;
- the `Ir` numbers are **per kernel call**, taken from callgrind's
  per-function **exclusive** `Ir` for the `kernel` symbol divided by the call
  count — never a whole-program total, which moves with the size of the
  environment block (`.memory/03-measurement.md`). In `isolated` mode the kernel
  is its own symbol, so no differencing is needed; where a `whole`-mode figure is
  quoted it is `main` exclusive and is compared only against `isolated`'s
  `kernel + main`, which is stated where it happens.

## 1. The adversarial behaviour table

Recorded, not required to agree — `.memory/02-bench-rules.md` makes the
adversarial rows a *behaviour* table. Every row below was produced by
`harness/check.py p16` (stage 4 for the plain builds, stage 7 for ASan+UBSan)
over all 32 cells; where the opt/mode variants of a rung differed, the gate says
so and it did not on any row here.

| input | shape | R1 (c-gcc, c-clang) | R1h + R2 + R3 + R4 + R5 | ASan+UBSan on R1 |
|---|---|---|---|---|
| `adversarial-overrun.bin` | **one window**, `n_blob == stride == 3072`. 47 well-formed 64-byte records fill 3008 bytes; the 48th has 61 bytes of room after its header and declares `vlen = 4096` | **exit −11 (SIGSEGV), no stdout, no stderr**, all 8 builds | exit 0, `8267139675305953920`, identical in all 24 | **fires**: `heap-buffer-overflow`, `READ of size 1`, *"0 bytes after 3072-byte region"* allocated in `slb_head1_u64_bytes`, at `c/kernel.c:56` |
| `adversarial-trunc.bin` | every window ends in a 2-byte tail — a header that does not fit | exit 0, `3988538283260473009` | the same, everywhere | clean, exit 0 |
| `adversarial-stride2.bin` | `stride_w == 2`, below the driver guard | exit 0, `0`; zero kernel calls | the same, everywhere | clean, exit 0 |
| `small.bin`, `large.bin` | well-formed | exit 0, agree with `model.py` | the same | clean, exit 0 |

Three things in that table are worth reading twice.

**R1 does not merely read one record too far — it never stops.** Delete
`vlen > end - (p + 3)` and `p` advances past `end`; the *other* comparison,
`end - p >= 3`, then underflows `size_t` to a colossal value and stays true, so
the walk carries on parsing whatever is in memory after the blob until it hits
an unmapped page. That is why R1 segfaults rather than printing a plausible
wrong number. The two tests are not independent obligations: the second is what
keeps `p <= end`, which is what makes the first sound. A chained parser
compounds a single missing check into an unbounded walk, and that is the
difference between this pattern and p02, where the damage was bounded by one
`memcpy` length.

**The same omission in each language.** This is the ladder's actual point, so it
is measured rather than asserted. Each rung below is the shipped rung with the
single line `if vlen > end - (p + 3) { break; }` deleted and nothing else
changed (built under `.temp/p16/decomp/`, never shipped):

| language | the same omission, on `adversarial-overrun.bin` |
|---|---|
| C (`c/kernel.c` — this **is** R1, shipped) | exit −11, SIGSEGV, silent |
| unsafe Rust (`unsafe.rs` minus the line) | exit −11, SIGSEGV, silent — identical to C, which is the honest statement of what `unsafe` buys and costs |
| safe Rust (`safe_naive.rs` minus the line) | **exit 101**, `index out of bounds: the len is 3072 but the index is 3072` — it stops at the *first* byte past the blob and names it |
| Verus R5 (`verus.rs` minus the line) | **cannot be built.** `error: invariant not satisfied before loop: p + 3 + vlen <= end`, 9 verified / 1 errors. The obligation the deleted line discharges is named in the diagnostic, with no input and no run |

All four still print the correct checksum on `small`, `large` and
`adversarial-trunc`: the bug is invisible on the happy path, in every language.
That is the whole difficulty of CWE-125 and it is why the adversarial input has
to be constructed rather than sampled.

**`adversarial-trunc.bin` is the control for `adversarial-overrun.bin`**, and it
is declared `clean` on purpose. It is the same "the chain ran out" shape with
the length field innocent: the walk stops on `end - p >= 3`, the test **R1
keeps**, so all six rungs agree and the sanitizer must stay silent. Without it,
"ASan fires on the adversarial input" would not distinguish *the length field
was trusted* from *the walker fell off the end of a window*.

## 2. Performance

`-O3`, `isolated`, marginal `Ir` per kernel call (callgrind per-function
exclusive `Ir` for the `kernel` symbol ÷ calls; `results/p16-tlv-walk.json`).
`small` is a 508-byte window of 4 × 127-byte records (500 bytes folded per
call); `large` is a 4090-byte window of 10 × 409-byte records (4070 bytes
folded). Strides and value lengths differ mod 4, 8 and 16 — `inputs/gen.py`
asserts it before writing a byte, because quoting one residue as a constant has
been the mistake three times (`.memory/01-ladder.md`).

| rung | small | large | Δ vs R4 (small) | Δ vs R4 (large) |
|---|---:|---:|---:|---:|
| R1 `c-gcc` | 4062.0 | 32694.0 | +1052 | +8896 |
| R1h `c-gcc-h` | 4079.0 | 32735.0 | +1069 | +8937 |
| R1 `c-clang` | **2993.0** | **23761.0** | −17 | −37 |
| R1h `c-clang-h` | 3017.0 | 23815.0 | +7 | +17 |
| **R2 safe-naive** | **5095.0** | **40921.0** | **+2085 (+69.3%)** | **+17123 (+71.9%)** |
| R3 safe-tuned | 3037.0 | 23875.0 | +27 (+0.90%) | +77 (+0.32%) |
| R4 unsafe | 3010.0 | 23798.0 | — | — |
| R5 verus | 3010.0 | 23798.0 | **0** | **0** |

Read per unit of the thing each rung is doing:

- **R2 is O(bytes folded):** +2085/500 = **+4.17 Ir per folded byte** on `small`,
  +17123/4070 = **+4.21** on `large` (averages). The *marginal* rate, swept over
  68 consecutive record lengths in two bands 18× apart, is **exactly 4.2500
  Ir/byte in both** (§3b), which is also what the two fold loops' instruction
  counts predict. This is the first genuine O(n) safety cost measured on this
  project, and §3 is what earns the right to say so.
- **R3 is O(records), not O(bytes):** +27 over 4 records, +77 over 10. §3b fits
  it, over two swept bands and without using these two points, to
  **`7 + 7·nrec`** instructions per call (`7 + 5·nrec` when the value length is
  a multiple of 4) — a fixed prologue plus the two reslice bounds checks per
  record, and **nothing per byte**. That is the p16 analogue of p01's and p02's
  "+10 per call, flat": those kernels did one unit of work per call, this one
  does `nrec`. So `.memory/01-ladder.md`'s R3 finding **survives** the
  data-dependent loop, correctly re-denominated.

  ⚠ **`+27 / +77` is the shipped pair's difference and is an upper bound on
  nothing but `inf(in-contract R3) − R4ship`. Read §10a with this bullet — it is
  900 lines below and it is the one that
  was measured.** "The shipped R3 is the cheapest admissible spelling" is
  **FALSE**, not unestablished: TASK_018 measured three admissible respellings
  keeping *both* named comparisons literally, two of them cheaper than the
  shipped R3 (`R3ship − r3_endslice = 2·nrec − 2`, `R3ship − r3_window =
  4·nrec − 8`, `r3_hdrarray − R3ship = nrec`), and TASK_018_REVIEW swept the
  `nrec` axis to confirm them. The measured in-contract minimum against the
  shipped R4 is **+19 (`small`) / +45 (`large`)** — and that one-sided figure is
  all that survives TASK_023, which measured the **R4** side moving by `4·nrec`
  and an admissible pair exceeding `+27 / +77` by `5·nrec` (§10a). Everything in the two
  paragraphs below is about *out-of-contract* spellings and was written before
  §10a existed; it is kept because the reasoning is still the record of what
  TASK_017 excluded, but it must not be read as "nobody has measured an
  admissible alternate".

  Two cheaper *out-of-contract* R3 spellings exist and were measured at TASK_015
  (`.temp/p05r3/v16/tuned_split.rs`, `…/tuned_splitat.rs`): **49 (`small`) /
  109 (`large`) Ir/call below the shipped R3**, i.e. `10·nrec + 9` in both
  residue classes (§10, **whole-program marginal** convention on both sides —
  the variants were never measured kernel-exclusive, and §10 now records that
  the driver offset is *not* uniform, so do not assume this delta carries into
  §2's convention unchanged). Both consume the slice — one
  window reslice, then `split_first_chunk::<3>()`/`split_at_checked` or plain
  `split_at` — and therefore contain **neither** of the two comparisons
  `spec.md`'s `idiom.required[0]` names. TASK_017 disambiguated that entry as
  naming **tokens**, so both are **out of contract**: they are not admissible
  p16 R3s and their numbers are not p16's. The matching consuming *R4*
  (`…/unsafe_consume.rs`, 29/49 below the shipped R4) is out of contract for the
  same reason, which is the point — the reading excludes a *representation*, on
  both sides of the pair, not one rung's competitor.

  What that left, *as of TASK_017*, was honest and weaker than it sounded:
  nobody had yet searched p16's in-contract spelling space, so `+27 / +77` was
  the cost of *this* cursor-walk R3 against the cursor-walk R4 it ships beside,
  with the value fold, the header read and the unrolling unpinned. **TASK_018
  searched it (§10a) and the sentence that stood here — "the shipped R3 is the
  cheapest admissible spelling is unestablished" — is now FALSE, not
  unestablished:** three admissible respellings, two cheaper, laws swept at
  TASK_018_REVIEW. What survives from this paragraph is only that the unpinned
  part of the spelling is where the movement is: 42 of the 77 Ir/call at `large`
  sit inside it. Nothing is
  swapped: the cheaper rungs are out of contract, and even if they were not,
  `R3′ − R4 = −22 / −32` means swapping R3 alone would publish "safe beats
  unsafe" from an unmatched pair (TASK_014/TASK_015's defect, re-committed as a
  shipped cell), while `inf(R4) ≤ inf(R3)` by construction
  (`.memory/01-ladder.md` finding 14) means no swap terminates. Adjudicated at
  TASK_016_REVIEW Part 5: **state the limitation, swap neither cell.**
- **R5 is free**, as on every pattern: byte-identical to R4 at `-O3`
  (`md5_fn 852405e0fa43` both, `md5_raw` equal, padding 12/12 B), `norel` at
  `O0` where the crate names differ in length.
- **R1h − R1, the cost of the check inside C:** gcc +17 (small) / +41 (large),
  clang +24 / +54. Per record that is gcc +4.25 / +4.1 and clang +6.0 / +5.4 —
  **flat in the size of the record, ~4–6 instructions per record.** The check
  that prevents an unbounded out-of-bounds walk costs 0.4% of the call.
- **gcc is 36% dearer than clang here**, and for a nameable reason: gcc does not
  unroll the value fold (three `shl $0x5` sites in its kernel against clang's
  seven), so its fold runs 8 Ir/byte against clang's 5.75. p02 measured gcc
  *cheaper* than clang in instructions; neither compiler is reliably ahead, and
  a gcc-only C baseline would have made safe Rust look 25% *better* here than a
  same-backend comparison does.

### Wall clock says the O(n) tax costs nothing

30 interleaved repetitions, pinned to CPU 5, minimum of each cell (never mean),
`.memory/03-measurement.md`:

| rung | small min (ms) | large min (ms) |
|---|---:|---:|
| R1 c-gcc | 12.73 | 74.07 |
| R1 c-clang | 12.73 | 73.88 |
| R2 safe-naive | 12.79 | 73.90 |
| R3 safe-tuned | 12.84 | 74.23 |
| R4 unsafe | 12.85 | 74.07 |
| R5 verus | 12.82 | 74.15 |

All 16 `-O3` cells fall in 12.69…12.85 ms and 73.56…74.23 ms — a 1.3% and 0.9%
spread against a measured run-to-run spread of 1.2–1.3%. **R2 executes 70% more
instructions than R4 and is, if anything, marginally faster.**

The mechanism is not mysterious and it is worth stating because it bounds the
claim: the fold is `acc = acc*31 + b`, a **serial dependence chain**. Each byte's
result is the next byte's input, so the loop is latency-bound at roughly 3
cycles per byte (`shl`+`sub` for ×31, then `add`) and the extra bounds-check
instructions issue into slots that were idle anyway.

*(Corrected at TASK_007_REVIEW. The arithmetic originally written here —
4070 bytes × 3 cycles × 20 000 calls ≈ 244 M cycles ≈ 74 ms — reconciled only
because two errors cancelled: it implies a 3.30 GHz clock, but CPU 5 measured
**3.85 GHz** in that session — a figure now known not to hold across sessions,
see the ⚠ below — and 13% / 21% of the quoted 74 ms / 12.7 ms is fixed
overhead outside the kernel (measured at `n_iters = 0`: 9.4 ms / 2.7 ms). The
correct method is to **difference `n_iters`**, never to divide a total wall time
by a byte count.)*

**What differencing `n_iters` actually measures is a *time* per byte, and that
is the figure this pattern may quote.** It is the same on the L1-resident and
the L3-resident input, which is what rules out a memory-bandwidth explanation —
that argument needs only the equality, not a clock.

⚠ **The conversion of that time into "3.027–3.055 cycles/byte on `large`, and
3.03–3.08 on `small`" is withdrawn as a measurement (TASK_012; landed here at
TASK_013).** It multiplies a wall time measured at TASK_007 by a clock measured
at TASK_007_REVIEW, and those are *different sessions* on a shared, containerised
box whose clock is set by other tenants: the identical dependent-chain probe, on
the identical cores, read **3.80–3.89 GHz** in one session and **2.55–2.86 GHz**
in another (`.memory/00-environment.md`). The same ns figure is therefore ~3.0 or
~2.2 cycles/byte depending on when you ask, and **`ns` is a measurement on this
box while `cycles` is an inference**. `.memory/00-environment.md`'s rule: never
quote cycles from a clock measured in a different session — measure the clock
*interleaved* with the wall-clock reps, or report ns and stop.

What survives independently of any clock: the Horner step `(acc<<5) - acc + b`
has a **hard 3-cycle serial latency floor**, so *if* the chain is the limiter
then the clock during the TASK_007 run must have been ≥ ~3.8 GHz. That is a
consistency argument — it is why 3.03 looked so clean — and not an independent
confirmation. **Do not publish a cycles/byte figure for p16 without re-measuring
the clock interleaved with the reps.** The null result (+72% `Ir` → +0.27% time)
and the ns figures are unaffected: both are taken inside one session.

So the honest headline is **two sentences, not one**: *safe-naive Rust pays a
real O(n) instruction tax on a walk LLVM cannot hoist — and on this kernel it
buys back nothing, because the kernel was never throughput-bound.* A pattern
whose inner loop has independent iterations would convert the same 4.2 Ir/byte
into time; p16 cannot show that and does not claim it. `.memory/01-ladder.md`
already records that `Ir` and wall clock disagreed in *direction* on p02; here
they disagree in *magnitude*, and reporting either column alone would mislead in
opposite directions.

### `whole` mode: R2 is the only rung that gets worse when inlined

Comparing like with like — `isolated` (kernel + main exclusive `Ir`) against
`whole` (main alone, the kernel having been inlined into it):

| rung | small isolated → whole | large isolated → whole |
|---|---|---|
| R2 safe-naive | 5109 → 5630 (**+521**) | 40935 → 45068 (**+4133**) |
| R3 safe-tuned | 3051 → 3032 (−19) | 23889 → 23886 (−3) |
| R4 unsafe | 3024 → 3009 (−15) | 23812 → 23797 (−15) |
| R5 verus | 3023 → 3009 (−14) | 23811 → 23797 (−14) |
| R1 c-gcc | 4077 → 4064 (−13) | 32709 → 32696 (−13) |

Every rung but R2 saves the call and return and nothing else. R2 costs **+10%
more** once inlined, on both inputs. `.memory/01-ladder.md` records the same
amplification for p01's R2 in `whole` mode on `large` and labels it an
observation rather than a settled result; p16 reproduces it on a completely
different kernel, so it is now two patterns. Note in particular that inlining is
the one situation in which LLVM *can* see the caller's
`off + len <= buf.len()`, and it still does not help — so "the bound is not
visible" is not a sufficient explanation for R2's cost. See §3.

### `O0`, recorded and never quoted as a perf claim

`.memory/02-bench-rules.md`: never report a perf number from an `O0` row. For
the record, `small`, marginal Ir/call: c-clang 7585, c-gcc 9621, unsafe/verus
10652, safe-naive 11696, safe-tuned 11956. The *ordering* inverts against `-O3`
— safe-tuned is the most expensive unoptimised cell and among the cheapest
optimised ones — which is exactly why the rule exists.

## 3. The decomposition

**This section comes before the claim in §2, not after it.** p02's headline was
published and then retracted because a whole-kernel delta was attributed to
bounds checking without changing one loop at a time. Every variant below is
built under `.temp/p16/decomp/` from `safe_naive.rs` with **only the kernel body
swapped** — same driver, same inputs, same checksum (all eight print
`71049275114976110` and `16533539788217857060`, so they are semantically
equivalent on well-formed input and only the codegen differs).

| # | variant | small | large | Δ vs R4 small | Δ vs R4 large |
|---|---|---:|---:|---:|---:|
| 1 | **R2 as shipped** — indexed walk, indexed fold | 5095.0 | 40921.0 | +2085 | +17123 |
| 2 | fold → iterator over `&buf[p+3..p+3+vlen]`; walk indexed | 3053.0 | 23915.0 | +43 | +117 |
| 3 | walk → `let rest = &buf[p..end];`; fold indexed on `rest` | 3016.0 | 23814.0 | +6 | +16 |
| 4 | both | 3020.0 | 23828.0 | +10 | +30 |
| 5 | R2 with the check written **additively** (unsound; measurement only) | 5082.0 | 40884.0 | +2072 | +17086 |
| 6 | R4's walk (unchecked) + R2's indexed fold | 5063.0 | 40841.0 | +2053 | +17043 |
| 7 | R2's walk (indexed) + R4's unchecked fold | 3048.0 | 23884.0 | +38 | +86 |
| 8 | **R4 as shipped** | 3010.0 | 23798.0 | — | — |

Variants 1–5 are the table `.memory/01-ladder.md` demands; 6 and 7 were added
because they attribute the cost *directly* rather than by subtraction — each
makes exactly one of the two loops unchecked and leaves the other alone.

**The delta lives in the value fold.**

- Changing **only the fold** (1 → 2) removes **2042 of 2085 = 98.0%** on `small`
  and **17006 of 17123 = 99.3%** on `large`.
- Changing **only the walk** (1 → 6) removes **32 of 2085 = 1.5%** and
  **80 of 17123 = 0.5%**.
- The direct attribution agrees: variant 7 says the safe *walk* costs
  **+38 / +86**, i.e. ≈ **+9 Ir per record, flat**; variant 6 says the safe
  *fold* costs **+2053 / +17043**, i.e. **4.11 / 4.19 Ir per folded byte**. The
  two add to 2091 against variant 1's measured 2085 — additive to within 6
  instructions, so there is no interaction term hiding anywhere.

**It is not p02's mechanism, and that was measured rather than assumed.**
Variant 5 writes the check additively — the unsound spelling `spec.md` forbids,
and the one whose *sound* counterpart cost p02 its entire published delta. Here
it moves the number by **−13 (0.26%)** on `small` and **−37 (0.09%)** on
`large`. There is no bulk-memory idiom to lose, because the fold is a serial
Horner chain, so the subtraction-first rule is free on this pattern. p02's
finding was real and specific to a byte-copy loop; it does not generalise, and
p16 is the counter-example.

**And more than half of the tax is not the check.** From the disassembly
(`harness/asm.py show --raw --sym kernel`), the two fold loops are:

```
R4 / clang / R3 : 4x unrolled, 4 x (mov, shl $0x5, sub, movzbl, add)
                  + add, cmp, jne             = 23 insns / 4 bytes = 5.75 Ir/byte
R2 (variant 1)  : rolled,  cmp, je <panic>                          <- the check
                          mov, shl $0x5, sub, movzbl, add
                          inc, dec, jne       = 10 insns / 1 byte   = 10.0 Ir/byte
```

10.00 − 5.75 = **4.25 Ir/byte** — and §3b's swept *marginal* rate is 4.2500 in
both bands, i.e. the static reading and the dynamic measurement agree to four
decimal places. Splitting it:

| component | Ir/byte | share |
|---|---:|---:|
| the bounds check itself (`cmp`, `je`) | 2.00 | 47% |
| the 4× unroll the check forecloses | 2.25 | 53% |

*(Both rows confirmed by construction at TASK_007_REVIEW — see §3.4. The second
row originally read "loop overhead the 4× unroll **would have amortised**", and
that counterfactual is **false**: forcing LLVM to unroll the *checked* loop
(`-unroll-runtime-multi-exit -unroll-count=4`) gives **9.50**, not 7.75, because
four copies need four exit tests — `mov,or,cmp,je`, 15 insns, 3.75/byte. So
unrolling R2 would recover **0.50, not 2.25**. The arithmetic 4.25 = 2.00 + 2.25
is exact, but the two terms are not independently recoverable. "Forecloses" is
the correct and stronger word: the check costs 2.00 **and** denies an
optimisation worth 2.25 that it could never have amortised.)*

The check makes the fold a **multiple-exit loop** — it leaves either on the trip
count or through the panic edge — and LLVM does not unroll it. That is
corroborated by a count that is independent of the timing: the number of
`shl $0x5` sites (the ×31 multiply) in each kernel is **3** for exactly the
variants that are expensive ({1, 5, 6}: walk + rolled fold + epilogue) and **7**
for exactly the variants that are cheap ({2, 3, 4, 7, 8}: walk + 4 unrolled
copies + remainder + epilogue). Eight variants, no exceptions.

*(TASK_007_REVIEW's correction: this is **not independent corroboration of the
2.00/2.25 split**, because the site count and the instructions-per-byte are both
consequences of the same unroll factor — it is one observation stated twice. It
does independently confirm **which variants are unrolled**, which is all it
should be cited for. The split's real confirmation is §3.4.)*

### §3.4 — the rolled-vs-rolled control (TASK_007_REVIEW)

The split above was originally inferred from reading two disassemblies. It was
then **confirmed by construction**. `-C llvm-args=-unroll-count=1` rolls R4's
fold, and is a **bit-for-bit no-op on R2** — so it is not quietly changing both
sides of the comparison. Rolled R4 and rolled R2 then differ by exactly
`cmp %rax,%rsi ; je <panic>`:

| fold | band A | band B |
|---|---:|---:|
| R2, rolled + checked | 10.0000 | 10.0000 |
| R4 shipped, 4×unrolled + unchecked | 5.7500 | 5.7500 |
| **R4, rolled + unchecked** | **8.0000** | **8.0000** |
| **R2 − R4-rolled = the check, alone** | **2.0000** | **2.0000** |

4.2500 = 2.0000 + 2.2500, zero residual. The 8.00 rolled-unchecked constant has
four independent sightings, and the cheapest is already in the shipped binary:
**R4's own remainder loop** runs at 8 insns/byte — R2's body minus exactly
`cmp`+`je`. gcc's `-O3` fold body and R4's mod-4 sawtooth are the other two.

Variant 3 is the sharpest form of the point: it is still an *indexed* fold
(`rest[3 + j]`), and it costs +6. Indexing is not what is expensive — an index
whose bound LLVM **cannot prove** is. One reslice, `&buf[p..end]`, moves the
bound into `rest.len()` where the optimiser can see it, and everything after it
is free. This is the same shape as p02's finding (an unprovable bound loses an
optimisation) with a different optimisation lost, which is why the two must not
be reported as one result.

**Does the fold vectorise in any rung? No — in none of them, and that bounds
the comparison.** `vector_regs` is `[]` for **23 of the 32 cells** in
`results/p16-tlv-walk.json`, and no `%xmm`/`%ymm`/`%zmm` register appears in any
**kernel**. *(Corrected at TASK_007_REVIEW: the original sentence said all 32,
which is false. The 9 exceptions are `['xmm']` and are all `whole`-mode `main` —
the driver, not the fold. The claim this section rests on is about the fold and
is unaffected; quote 23/32.)* `acc = acc*31 + b` is a serial reduction, so there is nothing to
vectorise; the best any rung achieves is a 4× *unroll*, which shortens the loop
overhead but not the dependence chain. The safe-vs-unsafe gap here is therefore
measured on a scalar loop on both sides — it is not "safe Rust lost the
vectoriser", which is what p01's residue effect was about.

### 3b. The sweep: is it a line, or one residue wearing the label of a constant?

`.memory/01-ladder.md` records that residues have bitten this project three
times and that the modulus which mattered on p02 was **16**. So the delta above
was swept rather than sampled, over **two full mod-16 cycles plus the endpoints
in each of two bands** — 34 consecutive value lengths at 56…89 (4 records per
window, L1-resident) and 34 at 2040…2073 (2 records per window, ~4 KiB windows),
`inputs/gen.py --sweep`, marginal `Ir` per call, `-O3 isolated`. Full data in
`.temp/p16/sweep/sweep.json` and `sweepB.json`.

**Marginal rate, taken at lag 32 so the two points share a residue mod 4, 8 and
16** — the comparison p02's sweep design was rebuilt to make possible:

| band | R2 | R3 | R4 | **R2 − R4** |
|---|---:|---:|---:|---:|
| A: vlen 56…89, 4 recs/window (228…360 B folded) | **10.0000** | 5.7500 | 5.7500 | **4.2500** |
| B: vlen 2040…2073, 2 recs/window (4082…4148 B folded) | **10.0000** | 5.7500 | 5.7500 | **4.2500** |

Ir per folded byte. Two bands 18× apart in record length and 2× apart in records
per window give **the same four numbers to four decimal places**, and all four
are exactly what the disassembly predicts: 10 instructions in R2's rolled fold
body, 23/4 = 5.75 in R4's 4×-unrolled one, difference 4.25. This is the tightest
agreement between a static reading and a dynamic measurement anywhere in this
project, and it is what licenses calling the tax O(n) rather than "large".

Note also **R3's marginal rate equals R4's exactly**: idiomatic safe Rust costs
nothing per byte. Its whole cost is the per-record term below.

**R2's tax is a line, not a residue.** Averaged rather than differenced, the
delta runs 4.07 (band A) to 4.24 (band B) — the drift is R4's *unroll setup*
(`and $0x3`, `cmp $0x3`, `jae`, remainder loop) being amortised over longer
records, not a change in the tax — and the shipped inputs sit inside it at 4.17
(`small`) and 4.21 (`large`). Within a band the average is flat to 0.1%. There
is no sawtooth in R2 at either scale. So the O(n) claim in §2 is not one residue
mislabelled as a constant, which is the specific error this project has made
three times.

**The residue that exists is R4's, its modulus is 4, and it is negligible.**
Every value length ≡ 0 (mod 4) makes R4 ~20 Ir/call cheaper in band A and ~34 in
band B, because the 4× unrolled fold's remainder loop is then empty. That is
0.06 Ir/byte against a 4.2 Ir/byte effect — 1.5%. **The modulus that matters on
p16 is 4, not p02's 16**, and it is 4 because that is the unroll factor, which
is a much more legible reason than p02's vectoriser epilogue. `inputs/gen.py`
pins mod 4, 8 *and* 16 anyway for both the strides and the value lengths, since
checking a modulus that turns out not to matter costs nothing.

**R3's cost has a closed form.** Fitting the four band points
(2 bands × 2 residue classes) gives

```
R3 − R4  =  7 + 7 · nrec        (or 7 + 5 · nrec when vlen ≡ 0 mod 4)
```

which predicts the two *shipped* inputs exactly and without being fitted to
them: `small` has nrec = 4 and vlen = 124 ≡ 0, so 7 + 5·4 = **27** (measured 27);
`large` has nrec = 10 and vlen = 406 ≡ 2, so 7 + 7·10 = **77** (measured 77).
So idiomatic safe Rust costs a fixed ~7 instructions per call plus ~7 per
record, and **nothing per byte** — the per-record term is the two reslice bounds
checks, and the constant is the prologue. That is the p16 form of
`.memory/01-ladder.md`'s "+10 per call, flat", correctly re-denominated for a
kernel that does `nrec` units of work per call rather than one.

**Static instruction count is anti-correlated with cost on this pattern.**
Padding-excluded static counts of the kernel: variant 6 is the *smallest* Rust
kernel in the whole experiment at **46** instructions and the second most
expensive at 5063 Ir/call; R2 as shipped is **64** and the most expensive; R4 is
**88**, variant 7 is **112**, variant 2 is **121** and they are the cheap ones.
`.memory/01-ladder.md` already refutes static count as a proxy for dynamic cost
using p01's R3; p16 inverts the relationship outright.

## 4. TCB tally

**TCB: 6 lines across 3 items**, counted per `.memory/04-verus.md` — *every*
`external_body` item individually, not just the interesting one, because
under-counting is how the pilot's fatal defect hid in plain sight.

| # | item | lines | `requires` | `ensures` | in the regime? | why it is trusted |
|---|---|---:|---|---|---|---|
| 1 | `get_unchecked` | 1 | `i < v@.len()` | `r == v@[i as int]` | **yes** (`external_body` + `unsafe` + non-empty `ensures`) | vstd ships no spec for `<[T]>::get_unchecked`. This is **the whole of p16's security argument** — see §5 |
| 2 | `load_input` | 4 | — | — | no (`external_body`, no `ensures`, no `unsafe`) | argv, file I/O, little-endian decoding, delegated to `common/driver.rs` |
| 3 | `emit` | 1 | — | — | no | `println!` is not verifiable |

Zero `assume(...)`, zero `assume_specification`, zero `external_fn_specification`,
and exactly **one `unsafe` token in the whole file**, inside item 1's body — the
gate reports *"scanned for `unsafe` outside a trusted body: ['verus.rs'] +
['common/driver.rs'] (1 token(s) inside a trusted body)"*. `common/driver.rs` is
scanned too, because `unsafe` moved there was a demonstrated bypass
(TASK_009_REVIEW).

That is **smaller than p02's** (4 items, 10 lines) and the same size as p01's,
and it should not be read as p16 being safer. p02's tally is bigger because it
has a second trusted item — the `copy_nonoverlapping` wrapper — that carries a
security `ensures` a reviewer can attack. p16 has *nothing* behind its one
trusted `requires`; the smaller number is a smaller surface **and** a thinner
argument. §5 is the paragraph that matters, not this table.

Obligations: **10** shipped, **11** under `--cfg slb_twin`. Both are pinned in
`spec.md` with the arithmetic beside them, and every term is measured rather
than asserted — `./verus_run.py patterns/p16-tlv-walk/verus.rs
--verify-function <name> --verify-root`:

| item | queries | why |
|---|---:|---|
| `vlen_at` | 0 | non-recursive `spec fn` |
| `fold_bytes` | 1 | recursive → a termination query |
| `tlv_walk` | 1 | recursive → a termination query |
| `tlv_fold` | 0 | non-recursive `spec fn` |
| `get_unchecked`, `load_input`, `emit` | 0 each | `external_body` — trusted, not verified |
| `kernel` | 3 | the body + one per loop body, and there are two loops |
| `main` | 5 | the body + the driver loop + one per `by (nonlinear_arith)` / `by { .. }` sub-proof in the two ghost blocks |
| **total** | **10** | |
| `slb_twin_get_unchecked` (`--cfg slb_twin`) | +1 | one function, no loop, no `by`-block → **11** |

**A correction worth carrying forward.** `.memory/04-verus.md` derives the
obligation count as *"one Verus query per function, plus one per loop body"*.
On p16 that rule gives **7** and the true count is **10**: it does not know
about `by (nonlinear_arith)` / `by { .. }` sub-proofs, which p16's driver has
four of (p01 and p02 have fewer, so the discrepancy never showed). The rule is
still the right *characterisation* — a skeleton checksum, invariant under
exactly the semantic weakenings it was introduced to catch — but it is not a
formula, and a pattern author should obtain each term by asking Verus rather
than by counting `fn` and `while`.

### What `work_per_call` is, and how much slack the floor leaves

`work_per_call` is the **window in bytes** (`stride`): 508 on `small`, 4090 on
`large`. The two differ deliberately, because `check.py`'s `d(Ir)/d(work)`
assertion needs two probe shapes with different `work_per_call` and cannot run
otherwise. `model.py` declares **no** `min_ir_per_work`, so the harness default
of 0.25 Ir/byte applies unchanged — legitimate here where it was not for p02,
because p16's fold has no bulk-memory form that could undercut it.

The gate reports: *64 cell/probe pairs, marginal Ir per call 2993…220141, all
above the derived floor, tightest margin **23.2×**; d(Ir)/d(work) 5.80…53.87.*
So this stage tolerates a ~96% loss of work before it objects, and — as
`.memory/02-bench-rules.md` insists — it is a **NOT-COLLAPSED smoke test**, not
an anti-collapse gate. What certifies that the walk happened is step 2, the
model checksum, which folds every byte the walk visits *and* the record count.

## 5. Why the `ensures` is not the security property here

**This is the one structural difference from p02 and it is the reason p16 was
worth building beyond the perf question.**

p02 *writes*, so its security property is statable as a postcondition: an
equality on the whole destination sequence says "the record landed where it
should" and "not one byte outside it moved" in a single clause, and R1 violates
that clause.

p16 writes nothing. The harm it models is CWE-125, an out-of-bounds **read** —
Heartbleed's class, the one that leaks rather than corrupts and that no
allocator rounding absorbs. And

> "no byte outside `buf[off .. off+len)` was read"

**is not a property of the return value.** A kernel could read out of bounds and
discard the byte; the `ensures` would still hold. There is no postcondition over
`(buf, off, len, result)` that says it, and adding a ghost read-set would be
adding a mechanism, not stating the property the code has.

So for this pattern **R5's memory-safety claim rests entirely on the discharged
`requires` of the trusted accessor.** Every `buf[i]` in verified exec code
carries the obligation `i < buf@.len()`; `get_unchecked`'s
`requires i < v@.len()` is what every call site must prove, and *that* is the
security property. It is discharged at four call sites in `kernel`:

| call | index | discharged from |
|---|---|---|
| the tag | `p` | `end - p >= 3` and `end <= buf@.len()` |
| the length lo byte | `p + 1` | the same |
| the length hi byte | `p + 2` | the same |
| the value fold | `p + 3 + j`, `j < vlen` | **the fit test** `vlen > end - (p+3)`, i.e. the line `c/kernel.c` deletes |

The kernel's `ensures` exists to make the proof non-vacuous, to force the loop
invariants to describe the walk rather than merely bound the indices, and to tie
the value to `model.py`. A kernel returning 0 unconditionally satisfies every
bounds obligation in the file; it is the `ensures` that stops that being a
proof. But it is **not** the safety argument and this file does not present it
as one.

Three consequences worth stating plainly.

1. **The TCB story is the whole result on p16.** On p01 and p02 a reader who
   distrusted the trusted base still had a security `ensures` to fall back on.
   Here there is nothing behind it. `harness/check.py`'s clause-deletion (5c),
   tautology (5c-req) and verified-twin (5c-twin) stages therefore matter more
   on this pattern than on any earlier one, and they matter on the **accessor's
   `requires`** specifically rather than on the kernel's `ensures`.
2. **The twin is idle on p16, and a green 5c-twin is not evidence that anything
   hard was checked.** p16's accessor is the same single-clause `i < v@.len()`
   that p01 and p02 ship. `.memory/04-verus.md` records what the twin uniquely
   catches — a *missing conjunct* in a multi-clause trusted `requires` — and p16
   has one conjunct, so there is nothing for it to find. Its value accrues from
   p17 on. What p16 can supply is the negative control, and §7 does: the twin
   *failing* on `i <= v@.len()`, for this pattern's own accessor, which is
   exactly the off-by-one OOB read the pattern models.
3. **What is machine-judged and what is a human reading.** Of p16's trusted
   clauses:

   | clause | judged by | what that judgement is worth |
   |---|---|---|
   | `get_unchecked` `requires i < v@.len()` | 5a (mentions every parameter its body uses), 5c-req (not a tautology), 5c-twin (strong enough to license `v[i]`) | 5c-twin is the only one that judges *strength*. `.memory/02-bench-rules.md` is explicit that 5c-req's guarantee is "this precondition is not `true`", **not** "this precondition is strong enough". |
   | `get_unchecked` `ensures r == v@[i as int]` | 5c (deleting it must break the file), identity, Miri | **Completeness** of this `ensures` with respect to the body's operations is judged by **no oracle at all** — see §6 (b). |
   | `load_input` / `emit` — no clauses | nothing | Nothing to judge: they state no facts, so they cannot axiomatise a falsehood. They are still TCB and still counted in §4. |

   There is also **no recorded accidental instance** of a too-weak trusted
   `requires` anywhere on this project — both known forms were reviewer-built.
   That is worth saying beside the machinery that exists to catch them.

## 6. Trusted items — the arguments no oracle can make

SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked(i)`; the twin's body is `v[i]`. The standard
library documents `get_unchecked(i)` as `index(i)` with the bounds check
removed, so `v[i]` is the same operation on the same slice at the same index,
and Verus checks the bound that `v[i]` needs against the same `requires`. It is
not a different operation, not a copy of the slice, and not defensive — a
defensive twin `if i < v.len() { v[i] } else { 0 }` cannot satisfy the `ensures`
and fails the stage rather than passing it.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes *as the body stands*, and this is the label that carries
the most weight on p16, because §5 has just argued that the accessor is the
whole security argument. The body is a single expression performing exactly one
unchecked read, at index `i` of slice `v`. `ensures r == v@[i as int]` names
that index and that slice, so a twin cannot satisfy the postcondition without
performing the same read, and the `requires` is therefore forced to be strong
enough for it. It is complete **only because the body is one line**, and
*nothing mechanical enforces that*: a second unchecked read the `ensures` never
mentions — the classic `let _peek = *v.get_unchecked(i + 1);` — is invisible to
5a, 5c, 5c-req and 5c-twin alike, because the twin only has to satisfy the
`ensures` and the `ensures` does not mention it. Two backstops exist and both
are tests rather than proofs (`.memory/02-bench-rules.md`, measured at
TASK_010): stage 3c identity catches the case where the extra read is added to
`verus.rs` alone, because R5's machine code then differs from R4's and the pin
here is `exact`; and step 8 Miri catches the case where the same read is added
to `unsafe.rs` too, but **only on inputs that actually reach the boundary**. On
p16 the input that reaches it is `adversarial-overrun.bin`, where the walk
stops with a record header three bytes from the end of the blob. Neither
backstop is a proof of completeness. Read the body, every time; on this pattern
there is nothing else.

(c) **Does the clause mean the same in both configurations?** Yes. `i < v@.len()`
mentions only `i`, `v` and vstd's `@`/`len()`; there is no pattern-defined name
in it that a `#[cfg]` could redefine, and `v: &[u8]` / `i: usize` are concrete
types with no generic or associated item that could differ. Since TASK_010 the
gate also forbids the token `slb_twin` anywhere in the file except the twin's
own `#[cfg(slb_twin)]` attribute, so no item — `const`, `use`, `type` or `fn` —
can differ between the shipped compilation and the twin's. That rule exists
because `#[cfg(slb_twin)] const SLACK: usize = 0;` / `#[cfg(not(slb_twin))] … =
1;` behind a shared `spec fn in_bounds` passed the whole gate while shipping
`i < v@.len() + 1`.

SLB-TRUSTED-ARGUMENT verus.rs load_input

(a) **Is the twin's body the right checked stand-in?** There is no twin and none
is required: `load_input` is `external_body` with **no `ensures` and no
`unsafe`**, so it falls outside the trusted-item regime, which
`.memory/04-verus.md` keys on `external_body` + (a non-empty `ensures` **or**
`unsafe`). That is the correct boundary rather than a loophole: an item that
asserts nothing cannot axiomatise a falsehood, and there would be nothing for a
twin's body to be forced to do.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** Vacuously, because there is no `ensures` — and that is
deliberate. Any postcondition here would be an axiom about the *contents of a
file*, which nothing can justify: it would say that the bytes the driver read
are the bytes the benchmark meant to run on, and no verifier can know that.
Every fact the proof needs is instead re-derived at run time inside verified
code, from `bytes.len()` and the guard `stride_w >= 3 && stride_w <= n_blob`.
The body performs no unsafe operation at all — it is argv handling, `fopen`,
`read_to_end` and a `to_vec` — so there is no unchecked operation for an
`ensures` to be incomplete about. What it *does* mean is that the proof knows
nothing about the payload, which is exactly right for a benchmark whose
adversarial inputs are the point.

(c) **Does the clause mean the same in both configurations?** No clauses, so
trivially yes, and the `slb_twin` token scan (which covers the file and
everything it `#[path]`-includes, `common/driver.rs` among them) is what makes
that statement checkable rather than assumed.

SLB-TRUSTED-ARGUMENT verus.rs emit

(a) **Is the twin's body the right checked stand-in?** No twin, for the same
reason as `load_input`: `external_body`, no `ensures`, no `unsafe`, therefore
outside the regime. `println!` is not verifiable in Verus and there is no
checked stand-in for writing to a file descriptor.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** There is no `ensures` and no unchecked operation. The body is
one `println!`. It is counted as TCB anyway, and listed individually in §4,
because `.memory/04-verus.md` records that the pilot was published as "TCB: one
3-line `get_unchecked` wrapper" when the true tally was three items — and the
one that mattered was the *driver*, whose `external_body` deleted every
call-site obligation in the file. Under-counting the boring items is how the
interesting one hides.

(c) **Does the clause mean the same in both configurations?** No clauses. The
item is identical under `--cfg slb_twin`, and the token scan enforces that
nothing in this file varies with that cfg except the twin itself.

## 7. Mutation testing — I broke my own proof and the gate caught it

`.memory/05-layout.md` step 5: *a pattern whose `spec.md` pins are copied
without being re-derived is a pattern whose gate certifies the pattern it was
copied from.* Three mutants, built as full repo-layout mirrors under
`.temp/p16/mut/` and never in `patterns/`.

### M1 — the trusted accessor's `requires` weakened by one character

`i < v@.len()` → **`i <= v@.len()`**, in the item, in the twin (so the
signature comparison still passes) *and* in `spec.md`'s pin, all in one edit.
This is the off-by-one that passed the entire gate at TASK_008_REVIEW, and it is
**exactly the bug class p16 exists to model** — an out-of-bounds read of one
byte, promoted to an axiom.

| oracle | verdict |
|---|---|
| Verus alone | `10 verified, 0 errors` — **no diagnostic at all** |
| stage 5a (structural: trusted item must demand something, mentioning every parameter its body uses) | **PASSES, approvingly**: *"trusted item `get_unchecked` demands `['i <= v@.len()']` of every caller, constraining every parameter its body uses"* |
| stage 5c-req (tautology probe, bare Z3 + `nonlinear_arith` + `bit_vector`) | **PASSES**: *"`i <= v@.len()` is not a tautology"* — and it is not |
| **stage 5c-twin (verified twin)** | **FAILS**: `with --cfg slb_twin Verus reports 10 verified, 1 errors` … `error: precondition not met: index in bounds for this access --> verus.rs:181:5  \|  v[i]` |

And the mutant's trusted base really does axiomatise the bug: adding
`fn slb_probe_offbyone(v: &[u8]) -> u8 { get_unchecked(v, v.len()) }` to the
mutated file gives **`11 verified, 0 errors`** — reading one byte past the end
of a slice is now *provably defined*. In the shipped file the same probe cannot
verify.

So on this pattern the twin is the **only** oracle standing between the gate and
a green run certifying CWE-125 as an axiom. That is the requirement
TASK_008_REVIEW set for p16 specifically — the mechanism shown failing on
`i <= v@.len()` for *this* pattern's accessor, not p02's — and it is met. §5.2
still applies: this is the twin working as a **negative control**, not the twin
finding a missing conjunct, because there is only one conjunct to have.

### M2 — the kernel's `ensures` made trivial

`r == tlv_fold(buf@, off, len)` → **`r == r`**, with the driver's consuming
`assert` deleted (otherwise Verus itself objects, and the point is to test the
gate) and the `spec.md` pins moved to match.

| oracle | verdict |
|---|---|
| Verus alone | `10 verified, 0 errors` |
| stage 5a (contract pin) | **PASSES** — the pin was moved in the same commit, which is precisely TASK_003_REVIEW's self-certification finding |
| **stage 5c (clause deletion)** | **FAILS**: *"`verus.rs` kernel ensures[0] is NOT load-bearing: deleting `r == r` still gives 10 verified, 0 errors. Nothing consumes this postcondition, so it is decoration."* |

Note which oracle did *not* catch it: the pin. A declared pin moves with the
code it constrains. What caught it is derived — delete the clause, re-run Verus,
fail if the file still verifies.

### M3 — the fit test deleted from R5

`if vlen > end - (p + 3) { break; }` removed from `verus.rs` and nothing else:

```
error: invariant not satisfied before loop
   --> .temp/p16/mut/m3-verus-nocheck.rs:272:17
    |
272 |                 p + 3 + vlen <= end,
verification results:: 9 verified, 1 errors
```

The diagnostic names the exact obligation the deleted line discharges — the one
whose absence in `c/kernel.c` produces the SIGSEGV in §1.

## 8. What the proof catches that a test suite does not

A walker written **`p += vlen`** instead of `p += 3 + vlen` is a real and common
form of this bug: it forgets that the header is part of the record. On
`vlen == 0` it makes no progress and **never terminates**.

Verus rejects it with no input and no run:

```
error: decreases not satisfied at end of loop
   --> .temp/p16/mut/m0-p-plus-vlen.rs:239:5
    |
239 |     while end - p >= 3
error: invariant not satisfied at end of loop body   (the tlv_walk invariant)
verification results:: 9 verified, 1 errors
```

The `decreases` clause is `end - p`, and the argument that discharges it in the
shipped kernel is that a record occupies `3 + vlen >= 3` bytes — **progress is
guaranteed by the header, not by the length field.** A walker that advances by
the length field alone has surrendered its own termination argument to the
attacker.

**And p16's own five inputs do not catch the non-termination.** They catch the
*mis-parse*: `p += vlen` gives `16938693215723205161` on `small.bin` against the
model's `71049275114976110`, so the checksum stage fails. But that is a
different defect. Build a one-window input whose **first** record declares
`vlen == 0` — perfectly well-formed, the shipped kernel walks it and prints
`14879631210601875648`, matching `model.py` — and the `p += vlen` build **hangs**
(killed by `timeout 15`, exit 124). Nothing in the shipped corpus contains a
zero-length record, and there is no reason a pattern author would think to add
one; the closely-related variant in which the length field *includes* the header
would parse every well-formed input correctly and hang only on that input.

That is a cheap, honest statement of what a proof buys over a test suite: not
"the tests would have missed the bug" — here they caught a symptom of it — but
**the termination obligation is discharged for all inputs, by an argument, and
the verifier names the clause that fails when the argument does.** It costs one
`decreases` line. This variant is deliberately *not* built as a rung.

## 9. Proof sticking points

R5 verified on the **first attempt**, `10 verified, 0 errors`, which was not
expected — the task budgeted a full engineer session for this cell. Four things
made it cheap, and they are the transferable part:

1. **`break` needs `invariant_except_break` + `ensures` on the loop, and Verus
   supports both.** A `while` with a `break` cannot assume its condition is false
   afterwards, so invariants that hold only at the top go in
   `invariant_except_break` and what survives *either* exit goes in the loop's
   own `ensures`. `_VERUS_DOC_/guide/src/break.md` has the pattern; the working
   example is `examples/guide/recursion.rs:loop_break`. This was the one thing I
   expected to fight and it took no iterations.
2. **The loop invariant has to be "the walk from here is the whole walk."**
   `tlv_walk(buf@, p, end, acc, nrec) == tlv_walk(buf@, off, end, 0, 0)`. There
   is no closed form for where the walk will be after *i* steps — the positions
   *are* the data — so the usual "acc equals the fold of the prefix" shape is not
   available. Threading the recursive spec function's own state through the
   invariant is the shape that works, and it generalises to any parser loop.
3. **Two ghost snapshots, `a0` and `a1`.** At the `break` the accumulator has
   already absorbed the tag byte, so the invariant is stated about a value no
   program variable holds any more; `let ghost a0 = acc;` before the update gives
   it a name. `a1` (after the tag, before the value) is what `fold_bytes` starts
   from in the inner loop's invariant. Both erase — R4 and R5 are byte-identical.
4. **Wrapping everywhere removes every arithmetic obligation but the pointer
   ones.** `acc.wrapping_mul(31).wrapping_add(..)` and `nrec.wrapping_add(1)`
   have full vstd specs and are usable in `spec fn` bodies, so the proof is left
   with exactly the memory-safety obligations and nothing else. `nrec + 1` would
   have needed a bound on the number of records — an extra invariant for no
   scientific gain.

The two ghost blocks in the driver (`k < nwin` and
`k * stride + stride <= n_blob`) are p02's three lemmas with `+2` changed to
`+ stride`: `lemma_div_non_zero`, `lemma_fundamental_div_mod`,
`lemma_mul_inequality` and one `by (nonlinear_arith)`. They lifted verbatim, as
`.memory/04-verus.md` says they would. `assert(buf@.len() ==
vstd::slice::spec_slice_len(buf));` once at the top of the kernel is what makes
`off + len` provably non-overflowing.

Total Verus wall time for the shipped file: ~2 s.


## 10. The spelling spread — five spellings, and which two are p16

**Not the headline.** A result about *method*. p16's number is the matched pair
under the idiom `spec.md` declares — **R3 `safe_tuned.rs` − R4 `unsafe.rs` =
`7 + 5·nrec` (`vlen ≡ 0 mod 4`) / `7 + 7·nrec`** — and the other rows below are
measurements of kernels p16 does not ship. Required for every pattern by
TASK_016 for every pattern that has spellings.

**Read the convention line before comparing with §2.** These are **whole-program
marginal** `Ir`/call — (`Ir` at `n_iters` 200 − at 100) ÷ 100, `harness/check.py`
step 3b's probe — where §2's table is **callgrind's kernel-exclusive `Ir` ÷
calls**. The two differ by the driver's own per-iteration work, which is
**+14.30 on the three rungs in this table** (R2 5095.0 → 5109.30, R3 3037.0 →
3051.30, R4 3010.0 → 3024.30), so every difference *here* is identical under
both conventions and no absolute here contradicts §2.

**That offset is NOT uniform across the pattern, and the earlier claim that "no
published delta moves" was false** (TASK_016_REVIEW M1; re-measured at TASK_017
from `results/gate/p16-tlv-walk.json` against §2). The driver's per-iteration
work outside the kernel symbol is compiled by a different compiler per rung:
**c-gcc/c-gcc-h +15.72, c-clang/c-clang-h +14.72, R2/R3/R4 +14.30, R5 +13.30**,
on both inputs. Every delta that crosses a *compiler* boundary therefore moves.
Writing every difference consistently as **row − R4** (small / large):

| delta | §2, kernel-exclusive | marginal | moves by |
|---|---:|---:|---:|
| `c-gcc − R4` | +1052 / +8896 | +1053.42 / +8897.42 | +1.42 |
| `c-gcc-h − R4` | +1069 / +8937 | +1070.42 / +8938.42 | +1.42 |
| `c-clang − R4` | −17 / −37 | −16.58 / −36.58 | +0.42 |
| `c-clang-h − R4` | +7 / +17 | +7.42 / +17.42 | +0.42 |
| `R5 − R4` | **0 / 0** | **−1.00 / −1.00** | −1.00 |
| `R3 − R4`, `R2 − R4`, `R1h − R1` in one compiler | — | — | **0** |

**No sign flips.** TASK_016_REVIEW M1 and `.memory/03-measurement.md` report
these two C rows as "the sign flips"; re-measured at TASK_017 they do not — that
reading comes from labelling the values `R4 − c-clang` / `R4 − c-gcc` while
quoting `c-clang − R4` / `c-gcc − R4`, i.e. from switching sign convention
mid-sentence. The magnitudes move by 0.42 and 1.42 and the signs stand. What is
true, and is M1's real content, is that the offset is **not** uniform and five of
§2's eight rows' deltas move; the earlier "+14.30 on every rung, no published
delta moves" was false. **The R4 ≡ R5 finding does not rest on that −1.00**: it
rests on `md5_fn` byte-identity (§2), which is a property of the kernel and not
of the driver. Rule: say which convention a number is in — and which direction
the subtraction goes — every time (`.memory/03-measurement.md`).

**The three shipped rows are the gate's own
numbers**: `results/gate/p16-tlv-walk.json`'s `marginal_ir_per_call` reads
5109.3 / 3051.3 / 3024.3 on `small` and 40935.3 / 23889.3 / 23812.3 on `large`,
which is where the +14.30 is checkable rather than asserted. p05 and p17 quote the marginal convention
in their own §2; p16 is the pattern that does not, and that is worth knowing
before differencing across files.

`small` = 4 records × 127-byte values (`vlen ≡ 0 mod 4`); `large` = 10 × 409
(`vlen ≡ 2`). Sources under `.temp/p05r3/v16/`; **none is a p16 cell.**

| # | rung | spelling | file | small | large | − R4 shipped |
|---|---|---|---|---:|---:|---|
| 1 | R2 | indexed `buf[p+3+j]` | **`safe_naive.rs` (SHIPPED CELL)** | 5109.30 | 40935.30 | +2085 / +17123 — the O(n) row, 4.25 Ir per folded byte (§3b) |
| 2 | R3 | reslice header + iterator fold | **`safe_tuned.rs` (SHIPPED CELL)** | **3051.30** | **23889.30** | **+27 / +77** |
| 3 | R3 | `split_first_chunk::<3>()` + `split_at` | `v16-tuned_split.rs` | 3002.30 | 23780.30 | −22 / −32 |
| 4 | R3 | `split_at` only | `v16-tuned_splitat.rs` | 3002.30 | 23780.30 | −22 / −32 |
| 5 | R4 | `get_unchecked` on an index `p` | **`unsafe.rs` (SHIPPED CELL)** | **3024.30** | **23812.30** | **0** |
| 6 | R4 | consumed cursor, `get_unchecked` | `v16-unsafe_consume.rs` | 2995.30 | 23763.30 | −29 / −49 |

**Rows 3, 4 and 6 do NOT satisfy p16's declared idiom.** Rows 3, 4 and 6 keep a
consumed slice and a running remainder and contain neither `end - p >= 3` nor
`vlen > end - (p + 3)`, so under the **named-spelling standard** they are
different benchmarks.

**Say when that became true, because it was not always true.** Until TASK_017
this section said all six rows were admissible, and it said so because the
pre-TASK_017 `idiom` block said so in as many words: *"A consuming spelling
(`split_first_chunk::<3>()` plus `split_at`) **is admissible under this
declaration**"* (`git show fd91ae7:patterns/p16-tlv-walk/spec.md`). TASK_017
read `required[0]` as naming tokens and deleted that sentence.
**TASK_018 adopted the named-spelling standard as a *policy*, for all six
patterns, after the alternate spellings had been measured** — it is not a
disambiguation of what `required[0]` always meant, and `spec.md`'s `idiom.why`
now carries both the deleted sentences and the date they stopped applying. Rows
3 and 4 were admissible when TASK_015 measured them (`ad661ed`) and stopped
being admissible at `89f6598`, four tasks later. Nobody may read `+27 / +77` as
a pre-registered matched pair.

**And the argument TASK_017 gave for the pin does not survive measurement.** Its
short version was that the two tokens *are* the cursor-and-end traversal, so
pinning them "is what makes `R3 − R4` a difference in safety rather than in
representation". §10a measures that and it is **false**: three respellings that
keep both named comparisons literally, and change only the header read and the
value fold, span 42 `Ir`/call at `large` against a published `R3 − R4` of 77.
The pin makes the admissible class *decidable*; it does not make it *singular*.

The exclusion is **symmetric in existence** — row 6 is an *unsafe* rung and goes
out with rows 3 and 4 — and **asymmetric in effect**, which is the number this
paragraph used to omit (TASK_017_REVIEW M4): the published pair is `+27 / +77`
and the excluded matched consuming pair is `+7 / +17`, so the reading makes
p16's published safety tax **3.9× / 4.5× larger**, removing 49 / 109 `Ir`/call
of headroom from the **safe** side against 29 / 49 from the unsafe side. Quote
those numbers, not the word "symmetric".

So the marking here is *shipped and admissible* (rows 1, 2, 5) versus *out of
contract* (rows 3, 4, 6). Between TASK_017 and TASK_018 that left p16 with **no
admissible alternate spelling measured at all**, which was the honest and
uncomfortable statement of the time; §10a closes it with three.

Rows 3 and 4 are **indistinguishable in `Ir` on every input where both were
measured** — both shipped inputs and four sweep blobs (`sw56`, `sw60`,
`sw2040`, `sw2044`), six points, equal to the hundredth — while being textually
unrelated: what does the work is consuming a cursor, not the method that
consumes it. (The 68-blob sweep below measures row 3 and not row 4.)

**The laws, swept over all 68 committed sweep blobs** (two `nrec` bands × 34
consecutive value lengths, i.e. ≥2 full cycles of the mod-4 residue), each an
*exact* constant per (residue, band) with **zero residual**
(`.temp/review015/sweep-p16.json`, re-derived at TASK_016):

| difference | `vlen ≡ 0 (mod 4)` | otherwise |
|---|---|---|
| R3ship − R4ship (**the pair p16 publishes**) | `7 + 5·nrec` | `7 + 7·nrec` |
| R3ship − R3′ | `10·nrec + 9` | `10·nrec + 9` |
| R4ship − R4′ | `5·nrec + 9` | `4·nrec + 9` |
| R3′ − R4′ (matched, both consuming) | `7` **flat** | `7 + nrec` |
| R3′ − R4ship | `−(5·nrec + 2)` | `−(3·nrec + 2)` |

The sweep bands have `nrec` 2 and 4. **The two shipped inputs are out-of-sample
at `nrec` 4 and 10 and every law predicts them to the instruction** — including
`nrec = 10`, which is 2.5× outside the swept range: R3ship − R4ship 77 (`7+7·10`),
R3ship − R3′ 109 (`10·10+9`), R4ship − R4′ 49 (`4·10+9`), R3′ − R4′ 17 (`7+10`).
That is what makes them laws rather than fits.

Three things follow.

1. **The safe side is again the spelling-sensitive one**, and by a margin that
   swamps the pair: rows 1–4 span 2107 `Ir` on `small` (69%), rows 5–6 span 29
   (1.0%).
2. **p16's published R3 cost is still a spelling's cost, and pinning the
   comparisons did not stop it being one.** `required[0]` pins the two
   comparisons as tokens, i.e. the cursor-and-end traversal, in every rung; what
   it still does **not** pin is the value fold, the header read or unrolling, so
   `+27 / +77` remains *this* R3's number rather than safe Rust's. The honest
   statement is: *R3 costs `7 + 7·nrec` as written; a consuming R3 costs
   `10·nrec + 9` less but is not a p16 rung; against the matching consuming R4 —
   also not a p16 rung — the residual is 7 flat at one residue and `7 + nrec` at
   the others.* `.memory/01-ladder.md`'s "quote the cheapest spelling you can
   find" does **not** bite on rows 3/4/6 — but §10a shows it bites anyway, from
   inside the contract: **the shipped R3 is measurably not the cheapest
   admissible one.** Between TASK_017 and TASK_018 the statement here was "no
   admissible alternate R3 has ever been measured, so 'cheapest admissible' is
   unestablished"; after §10a it is **false**, not unestablished. Landing a
   cheaper admissible R3 is a cell swap and a different task; TASK_016, TASK_017
   and TASK_018 changed no cell source.
3. **`nrec + 3` was never p16's law.** TASK_015's audit fitted three points, two
   of which sat at `vlen ≡ 0 (mod 4)` where the slope is invisible, and the third
   used a record count its own table contradicts. Swept, the same quantity is
   `7` / `7 + nrec`. **Sweep, do not sample** — the rule this file's §3b already
   states, violated one section later by the same project.

## 10a. The **in-contract** spelling spread (TASK_018)

§10's rows 3, 4 and 6 are out of contract under the named-spelling standard, so
they cannot answer "is the shipped R3 the cheapest admissible one?". This
section answers it. **The answer is no.**

Three alternate R3 spellings, all under `.temp/p18/v16/`, **none a p16 cell**.
Each keeps **both named comparisons literally** — `while end - p >= 3` and
`if vlen > end - (p + 3)` — keeps `p`/`end` as the cursor-and-end pair, keeps
`p = p + 3 + vlen`, folds the tag before the fit test, folds `nrec`, and
contains zero `unsafe`. The **only** thing respelled is what `spec.md`'s
`idiom.why` says is deliberately *not* restricted: which slice the header read
and the value fold index into.

| variant | what changed | in contract? |
|---|---|---|
| `r3_endslice.rs` | one added line: the two reslices come out of `&buf[..end]` instead of out of `buf`. `p` still absolute, `end` still `off + len`. | **yes**, on the tokens *and* on `idiom.why` ground (ii)'s gloss ("`p` indexing the whole blob") |
| `r3_window.rs` | window resliced once before the loop; `p` window-relative, `end = len` | yes on the tokens; ground (ii)'s gloss arguably excludes it — reported separately for that reason |
| `r3_hdrarray.rs` | header read as `[u8; 3]` via `try_into()` instead of a runtime-length reslice | **yes** |

**Equivalence:** all three print byte-identical stdout and exit status to
shipped R3 on **73/73** committed inputs (and shipped R3 matches shipped R4 on
all 73). One semantic note, because it is the first thing to attack:
`r3_endslice`'s `&buf[..end]` moves a bound check *earlier* than shipped R3's
first `&buf[p..p+3]`. Under the kernel's `requires off + len <= buf_len` — which
is structural and holds on every input this benchmark runs — the two are the
same function; on a call that violated the `requires` they would panic at
different points. That is what "hoisted length assertion" in the R3 rung
definition (`.memory/01-ladder.md`) licenses, and it is why this is an R3 move
and not a semantics change.

**Whole-program marginal `Ir`/call**, `-O3 isolated`, `n_iters` 100→200 — the
same convention as §10's table, so these are directly comparable with it:

| input | `nrec` | `vlen%4` | R4 ship | **R3 ship** | `r3_endslice` | `r3_window` | `r3_hdrarray` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `sweep-v2040` | 2 | 0 | 23561.70 | 23578.70 | 23576.70 | 23578.70 | 23580.70 |
| `sweep-v2041` | 2 | 1 | 23586.00 | 23607.00 | 23605.00 | 23607.00 | — |
| `sweep-v2042` | 2 | 2 | 23602.30 | 23623.30 | 23621.30 | 23623.30 | — |
| `sweep-v2043` | 2 | 3 | 23618.00 | 23639.00 | 23637.00 | 23639.00 | — |
| `sweep-v2044` | 2 | 0 | 23608.00 | 23625.00 | 23623.00 | 23625.00 | 23627.00 |
| `small` | 4 | 0 | 3024.30 | **3051.30** | 3045.30 | 3043.30 | 3055.30 |
| `sweep-v56` | 4 | 0 | 1459.70 | 1486.70 | 1480.70 | 1478.70 | 1490.70 |
| `sweep-v57` | 4 | 1 | 1508.00 | 1543.00 | 1537.00 | 1535.00 | — |
| `sweep-v58` | 4 | 2 | 1540.00 | 1575.00 | 1569.00 | 1567.00 | — |
| `sweep-v59` | 4 | 3 | 1572.30 | 1607.30 | 1601.30 | 1599.30 | — |
| `sweep-v60` | 4 | 0 | 1552.00 | 1579.00 | 1573.00 | 1571.00 | 1583.00 |
| `large` | 10 | 2 | 23812.30 | **23889.30** | 23871.30 | 23857.30 | 23899.30 |

| difference | value | residual |
|---|---|---|
| `R3ship − r3_endslice` | `2·nrec − 2` | **0** on all 12 points, all four residue classes |
| `R3ship − r3_window` | `4·nrec − 8` | **0** on all 12 points |
| `r3_hdrarray − R3ship` | `nrec` | **0** on the 6 points measured |

**The `nrec` forms are LAWS, not fits — swept at TASK_018_REVIEW.** As delivered
this block carried a ⚠ saying the residue axis was swept and the `nrec` axis was
a three-point fit (`nrec ∈ {2, 4, 10}`), that §3b's own rule — *sweep, do not
sample* — was therefore not satisfied for `nrec`, and that `nrec + 3` (§10
point 3) is what a three-point `nrec` fit did to this pattern last time. The
review ran the sweep the caveat asked for: **11 `nrec` values (1, 2, 3, 4, 5, 6,
7, 8, 9, 12, 16) × 2 residue classes (`vlen` 124 ≡ 0 and 126 ≡ 2 mod 4), 22
generated inputs, all five binaries on each = 110 marginals, all six rungs
printing identical checksums on every input, and ZERO residual** on all four
forms:

| difference | law | residual over the 22 points |
|---|---|---|
| `R3ship − r3_endslice` | `2·nrec − 2` | **0** |
| `R3ship − r3_window` | `4·nrec − 8` | **0** |
| `r3_hdrarray − R3ship` | `nrec` | **0** |
| `R3ship − R4ship` | `7 + 5·nrec` (`vlen ≡ 0 mod 4`) / `7 + 7·nrec` | **0** |

So this is **not** a repeat of `nrec + 3`, and the `nrec` forms may be quoted.
Two consequences follow with them: at `nrec` 10 the in-contract span is
`10 − (−32)` = **42** against `R3 − R4 = 77`, cheapest admissible **+45**; at
`nrec` 4, **12** against 27, cheapest **+19**.

**The `nrec` axis now ships, and the laws were re-derived from it (TASK_020).**
As delivered this block carried a ⚠: the 68 committed sweep blobs could not have
tested this axis at all, because `inputs/gen.py`'s two `SWEEP_BANDS` sit at
`nrec` 4 and 2, so the committed sweep moved the *residue* and held `nrec`
almost fixed. The law rested entirely on 22 inputs under `.temp/review018/in16/`
that were not in the tree — the tree stated a law it could not reproduce, which
is the shape of defect `nrec + 3` (§10 point 3) already cost this pattern once.

TASK_020 added a **third band** to `inputs/gen.py`: `sweep-n{nrec}v{vlen}.bin`
over `nrec ∈ {1…9, 12, 16}` × `vlen ∈ {124, 126}` — 22 blobs, nine *consecutive*
`nrec` values plus two distant ones for lever arm, and **both** residue classes,
because `R3ship − R4ship` is the one law of the four that is residue-dependent
and a single class would silently turn it back into a fit. Appending the band
leaves all 68 earlier `sweep-v*.bin` **byte-identical** (the RNG is drawn
sequentially and the new band is drawn last; verified by md5 over all 73 files
before and after). The blobs are gitignored like every other input; the
generator is what is committed.

Re-measured on those blobs, `-O3 isolated`, `n_iters` 100→200, one session
(`.temp/p20/p16nrec.log`) — **zero residual on all 22 points, on all four
laws**:

| difference | law | residual over the 22 committed-generator points |
|---|---|---|
| `R3ship − R4ship` | `7 + 5·nrec` (`vlen ≡ 0 mod 4`) / `7 + 7·nrec` | **0** |
| `R3ship − r3_endslice` | `2·nrec − 2` | **0** |
| `R3ship − r3_window` | `4·nrec − 8` | **0** |
| `r3_hdrarray − R3ship` | `nrec` | **0** |

The first row is the clean one: both binaries come from the same build. The
other three use the TASK_018 variant binaries under `.temp/p18/`, built in an
earlier session — §10b says a marginal is exact only within a build, so those
three rows carried a cross-build risk and it did not materialise; every
difference is the same exact integer the reviewer measured.

~~⚠ Residual gap, smaller than the one it replaces: the *variants* are still
uncommitted, so rows 2–4 remain reproducible only by rebuilding
`.temp/p18/v16/`.~~ **Closed at TASK_021.** What TASK_020 shipped was the
**input axis**; what ships now is the **variants**, behind
`patterns/p16-tlv-walk/controls/gen_controls.py` — p08's committed-generator
shape (`.memory/05-layout.md` demand 11: a source that is not a pinned, cleanly
verifying cell cannot live in the pattern dir). Each control is `safe_tuned.rs`
with two or four **exact-string substitutions, each asserted to hit exactly
once**, so a control cannot drift from the rung it respells: edit
`safe_tuned.rs` and either the control moves with it or the generator fails
loudly. That is the property the `.temp/p18/v16/` copies did not have.

It reproduces TASK_018's binaries **byte for byte** — `md5_fn` `34a618f8`
(`r3_endslice`, 117 insns), `c7f697a8` (`r3_window`, 119), `999fb677`
(`r3_hdrarray`, 118), against shipped `07b07f1a` (117) and R4 `852405e0` (92),
which is the digest table five paragraphs below — and all four laws re-derive
from it with **zero residual on all 22 committed `sweep-n*` blobs**:

```
$ python3 patterns/p16-tlv-walk/controls/gen_controls.py --build
$ ... marginal Ir/call, n_iters 100 -> 200, -O3 isolated       (.temp/p21/p16laws.json)
  R3ship - R4ship = 7 + 5*nrec / 7 + 7*nrec     22 points, NONZERO residual on 0
  R3ship - r3_endslice = 2*nrec - 2             22 points, NONZERO residual on 0
  R3ship - r3_window   = 4*nrec - 8             22 points, NONZERO residual on 0
  r3_hdrarray - R3ship = nrec                   22 points, NONZERO residual on 0
```

So §10a is now reproducible end to end from the committed tree: the generator,
the input band and — since TASK_021 — both of them inside `source_sha256`.
One difference from p08's generator, and it *was* a fix p08 needed until
TASK_022 landed it there too: p08's controls used to keep the shipped
`#[path = "../../common/driver.rs"]`, which from
`.temp/p08/controls/` resolves to `.temp/common/driver.rs`, a **gitignored
copy** of `common/` that happens to exist on this box; both generators now
rewrite the path to the real, hashed `common/driver.rs`.

**What this establishes.**

1. **"The shipped R3 is the cheapest admissible spelling" is FALSE**, not
   unestablished. `r3_endslice` is admissible on the strictest available reading
   and is **6 `Ir`/call cheaper on `small`, 18 on `large`**. This is also what
   discharges `.memory/05-layout.md` finding 13's "at least two alternates per
   rung" for p16's R3, which §10's rows 3 and 4 stopped discharging the moment
   they went out of contract.
2. **The in-contract spread is 42 `Ir`/call at `large` (−32 … +10) against a
   published `R3 − R4` of 77, and 12 at `small` against 27** — 55% and 44% of
   the published safety tax lives in spelling the declaration does not pin.
3. Therefore **`R3ship − R4ship = +27 / +77` is not the tax.** The measured
   in-contract minimum is **+19 / +45** (`r3_window`) or **+21 / +59**
   (`r3_endslice`) against the shipped R4 — and that pairing, R4 held fixed by
   fiat, is the **only** thing `+27 / +77` bounds. **The *R4* side has now been
   searched (TASK_023, §10a.1) and it moves by `4·nrec`**, so `+27 / +77` is not
   an upper bound on p16's in-contract safety tax: the admissible pair
   `(r3_hdrarray, r4_hdr)` exceeds it by `5·nrec`
   (`.memory/01-ladder.md` finding 14).
4. **`spec.md` ground (ii) is withdrawn.** Pinning `end - p >= 3` and
   `vlen > end - (p + 3)` does **not** make `R3 − R4` "a difference in safety
   rather than a difference in representation". It narrows the class of
   representations; it does not collapse it to one.
5. Unlike p17 (`patterns/p17-http-range/NOTES.md` §10), **no identity collapse
   here**: `md5_fn` is `07b07f1a…` (shipped, 117 insns), `34a618f8…`
   (`r3_endslice`, 117), `c7f697a8…` (`r3_window`, 119), `999fb677…`
   (`r3_hdrarray`, 118), `852405e0…` (R4, 92). On p16 the pin excludes genuinely
   different codegen. It still does not pick a point.

**Method.** `.temp/p18/measure.py` and `.temp/p18/measure2.py`, both calling
`.temp/p05r3/mir.py`, which is `harness/check.py`'s own `_probe_input` plus a
whole-program `Ir` difference. Binaries built with `harness/build.py`'s exact
`-O3 isolated` rustc flags (`--edition 2021 -C codegen-units=1 -C opt-level=3
-C debug-assertions=off --cfg slb_isolated`). **No pattern source was edited.**

## 10a.1. The **R4** side, and item 3 above is refuted (TASK_023)

§10a searched the safe side and left the unsafe side alone, and said so — item
3's own words were *"since the R4 side has not been searched in contract
either"*. TASK_023 searched it, on the question *"is `R3ship − R4ship` an upper
bound on the in-contract safety tax a p05 fact, or a ladder fact?"* **It is a
ladder fact, and p16 is the second pattern to measure it.**

Three respellings of `unsafe.rs`, derived by exact-string substitution asserted
to hit exactly once (`controls/gen_controls.py`, the same discipline as the R3
controls), each keeping **both** named comparisons literally, keeping `p`/`end`
as the cursor-and-end pair, keeping `p = p + 3 + vlen`, folding the tag before
the fit test and folding `nrec`. They change only what this declaration's `why`
says is *"deliberately NOT restricted: the R2/R3/R4 spelling of the value fold
and of the header read"* — which is the identical licence `r3_hdrarray` and
`r3_window` run on.

| variant | what changed | `md5_fn` | `n_fn` | `R4ship − this` |
|---|---|---|---:|---|
| `r4_hdr` | the two value-length bytes read as **one unaligned `u16`** (`(buf.as_ptr().add(p + 1) as *const u16).read_unaligned()`, `u16::from_le`) instead of two `get_unchecked` byte loads | `4b800e6d0d47` | 88 | **`4·nrec`** |
| `r4_window` | window resliced once (`buf.get_unchecked(off..off + len)`), `p` window-relative, `end = len` — the exact edit that makes `r3_window` `4·nrec − 8` cheaper | `f99559928bb6` | 94 | **−2** (*dearer*) |
| `r4_window_hdr` | both | `cd404bbbfec3` | 90 | `4·nrec − 2` |

**Zero residual on all 24 points** — `nrec ∈ {1…9, 12, 16}` × `vlen ∈ {124, 126}`
(both residue classes), plus `small` (`nrec` 4) and `large` (`nrec` 10).
Equivalence: **95 committed inputs × 3 variants = 285 comparisons, 0
mismatches** on stdout and exit status against the shipped R4 binary.

**One build, so the interval is a difference of numbers from one session.** §10b
says a marginal is exact only within a build, and §10a's own note flags that its
rows 2–4 carried a cross-build risk. This section re-measured shipped R3, the
three committed R3 controls *and* shipped R4 alongside the new variants, and
every digest reproduces §10a's table byte for byte: `07b07f1a8055` (R3 ship,
117), `34a618f837f2` (117), `c7f697a8d9ec` (119), `999fb67758ff` (118),
`852405e0fa43` (R4 ship, 92). All four §10a laws re-derive with **zero
residual on the same 24 points**, including the residue-dependent
`R3ship − R4ship = 7 + 5·nrec` (`vlen ≡ 0 mod 4`) / `7 + 7·nrec`.

**What it refutes.** `R3ship − R4ship` is not an upper bound on the in-contract
safety tax, because both rungs are spellings and the admissible **pairs** form
an interval:

| endpoint | pairing (`nrec ≥ 3`) | law (`vlen ≡ 0 mod 4` / else) | `small` / `large` |
|---|---|---|---|
| bottom | cheapest R3 `r3_window` vs dearest R4 `r4_window` | `nrec + 13` / `3·nrec + 13` | 17 / 43 |
| — | **shipped pair, published** | `7 + 5·nrec` / `7 + 7·nrec` | **27 / 77** |
| top | dearest R3 `r3_hdrarray` vs cheapest R4 `r4_hdr` | `7 + 10·nrec` / `7 + 12·nrec` | 47 / 127 |

Zero residual on both endpoint laws over the 20 points with `nrec ≥ 3`. The
domain is not decoration: at `nrec ∈ {1, 2}` the *ordering* flips, because
`4·nrec − 8` is negative there and `r3_window` is then the **dearest** R3 rather
than the cheapest; the endpoints become 10…20 / 12…22 at `nrec` 1 and 13…27 /
17…31 at `nrec` 2. **The published pair sits inside the interval on all 24
points**, and the pair `(r3_hdrarray, r4_hdr)` exceeds it by exactly `5·nrec`
(`nrec` from the safe side + `4·nrec` from the unsafe side) with **zero residual
on all 24** — that pair is the interval's top only for `nrec ≥ 3`, but it
exceeds the published figure everywhere. The interval is **111% / 109% of the
published tax** wide at `small` / `large`, rising to 159% at `nrec` 16.

**Three things this does *not* touch, stated so nobody re-runs them.**

- **The per-byte null survives.** `4·nrec` is per *record*: it is the same
  integer at `vlen` 124, 126 and at `small`'s and `large`'s quite different
  value lengths. So `.memory/01-ladder.md` finding 4's *"R3's marginal rate is
  5.7500 Ir per folded byte, which is R4's exactly"* is untouched, and so is
  R2's 10.00.
- **The one-sided bound survives**, and it is the only thing that does: hold R4
  at the shipped cell and `+27 / +77` bounds `inf(in-contract R3) − R4ship`
  above, with `+19 / +45` tighter.
- **This is not a minimum.** `r4_hdr` is the *first* lever tried on p16's R4 and
  it moved `4·nrec`; p05 published three successive R4-side "minima" and the
  next search overturned each (`.memory/01-ladder.md` finding 6). Nothing here
  is offered as `min(R4)`, and `min(R3 found) − min(R4 found)` is not a bound in
  either direction.

**The difference from p05 is the shape, and it is the sharper half.** p05's R4
side moved by a **constant** (7 flat); p16's moves by a **coefficient**
(`4·nrec`). So on p16 the pairing convention does not merely shift the intercept
of the published law — it changes the `nrec` coefficient from 1 to 10 (`vlen ≡ 0
mod 4`) or 3 to 12, i.e. across the whole interval. p05's §14h.6 found the same
thing on its own axis (coefficient 2…6 over free pairings). **The `O(nrec)`
*shape* of p16's headline survives; its coefficient is a property of the pairing
convention, not of the pattern.**

**Method.** `.temp/p23/probe.py` (R4 side, generation + build + token grep +
digests + equivalence + marginals) and `.temp/p23/probe2.py` (R3 side, same
build), logs `.temp/p23/probe{,2}.log`, data `.temp/p23/v16/probe{,2}.json`.
Marginal `Ir`/call by `harness/check.py`'s own probe — whole-program `Ir` at
`n_iters` 200 minus at 100, over 100 — re-implemented independently and agreeing
to the instruction with §10a on all five shared baselines. `harness/build.py`'s
exact `-O3 isolated` rustc flags. **No pattern source was edited**; the three R4
variants ship in `controls/gen_controls.py` so this section is reproducible from
the tree.
