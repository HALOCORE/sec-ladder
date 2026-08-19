# RECAP — state of the research programme

For a manager picking this up cold. Read this, then `.tasks/PROTOCOL.md` (which
now carries **the manager's own rules**), then `.memory/` 00–06.

**The `.memory/` files are authoritative and supersede any task report they
contradict** — several reports contain claims that were later refuted, and the
refutations live in `.memory/`.

## What this is

A micro-benchmark for the performance ↔ memory-safety tension. Each common C
pattern is built at five rungs — C, safe Rust (naive), safe Rust (tuned), unsafe
Rust, unsafe Rust + Verus proof — plus a sixth **R1h** hardened-C cell, across two
optimisation levels and two inline modes, and compared on assembly, executed
instructions, timing, proof burden and trusted-base size.

47 patterns are catalogued in `.memory/06-catalogue.md`. **Seven exist and all are
green. Six are reviewed:** p01 (calibration), p02 (first real bug), p16 (first
data-dependent bound), p17 (the limit of memory safety), p05 (the first
vectorised kernel), p08 (the first structural Rust win). **p07 (binary search) is
built, green and UNREVIEWED** — per `PROTOCOL.md` rule 9 its findings are in
`patterns/p07-binary-search/NOTES.md` and deliberately **not** in `.memory/` yet.
Read them as provisional; the review is the next task.

**p07 changes the headline of this document, in a narrower way than it was first
written.** It is the first kernel here that is not a linear fold — `Θ(log n)`
probes, no inner loop to amortise a per-call constant over — and it is **the first
pattern where R3's tax has no axis along which it amortises at all**: `6.0000` Ir
per probe with `probes = nq·⌈log2 n⌉`, so the fraction rises in *both* `n` and
`nq`. Survives six deliberately different query distributions, monotone in every
one. See finding 15.
⚠ It is **not** "the first counterexample to safety is cheap" — that sentence was
the manager's and it was refuted at TASK_026_REVIEW against this project's own
`.memory/`, which already records p16/p17's **R2** tax of 4.25 Ir/folded byte
(rising, toward 73.9%) and p05's `O(nrow)` **R3** tax. The R3 scoping is the whole
claim.

## The findings so far — this is the actual output

**Numbering warning, because it has already cost an agent time.** The list below
is **RECAP's own digest** and is numbered 1–15. `.memory/01-ladder.md` has a
*different* list, numbered 1–7, one entry per pattern, and **that one is
authoritative**. "Finding 12" means different things in the two files. When
writing a task file, name the pattern (*"p05's causal claim"*), never the number.

1. **A Verus proof costs exactly zero instructions.** The proven binary is
   byte-identical to the unproven one; ghost code fully erases. Verified on raw
   machine code on all three patterns, at both opt levels.
2. **A proof alone buys nothing.** Proving safe Rust panic-free leaves every bounds
   check in place — rustc never learns what the prover knew. The payoff arrives
   only when the proof *licenses unsafe code*: R5 is R4's machine code with the
   obligations discharged.
3. **Safety is cheap — and finding 9 says it stays cheap even when the optimiser
   *cannot* see the loop.** Tuned safe Rust is **+8…+10 instructions per call**
   versus unsafe on p01/p02 — flat in the size of the data, not a percentage.
   Hardened C's check is +5 (gcc) / +12 (clang), also flat. **Always quote R3;
   R2 alone overstates safe Rust by 3.7× on p01 and by ~75× on p16.**
4. **The security result (p02), the strongest thing here.** On a one-byte
   overflow, idiomatic C prints a plausible answer and exits 0 in **seven of eight
   builds** — silent heap corruption absorbed by glibc's chunk rounding. The eighth
   aborts only because Ubuntu defaults `_FORTIFY_SOURCE 3`. Every Rust and
   hardened-C cell handles it. Control: delete the check from safe Rust and it
   panics rather than corrupting, so "Rust makes the check non-optional" is a
   measurement.
5. **Static instruction counts are not a cost model.** The ranking inverted twice.
   gcc emits fewer instructions than clang and executes 43% more.
6. **`Ir` and wall clock can disagree in direction** — gcc 10% fewer instructions,
   23% slower (p02).
7. **The same-backend comparison, which is the one that counts.** clang 22.1.6 is
   bit-for-bit rustc 1.97.1's LLVM. On p01 `large`, C-clang and unsafe Rust execute
   **exactly 143,740,000** kernel instructions. Static gap +2, an
   induction-variable choice, not an ABI cost. **Every C-vs-Rust claim needs the
   clang column**; gcc stays as the "what a distro ships" baseline.
8. **p02's residue curve predicts.** R2−R4 is a sawtooth, amplitude 179 Ir,
   resetting at `len ≡ 1 (mod 16)`, on a 0.21 Ir/byte linear term — re-derived at
   seven unsampled lengths and 8× the scale (178.9, 0.2125). The only model here
   tested by prediction rather than re-measurement.
9. **p16 — safety is cheap *even where it should not be*, and the one place it
   isn't, the check is only half the reason.** A TLV walker with a
   data-dependent bound, nothing hoistable, no bulk idiom to lose: the case p01
   said not to generalise to. **R3 idiomatic safe Rust is 5.7500 Ir/folded byte —
   R4's rate exactly, zero per byte**, its whole cost O(1) per call and shrinking
   with size. **The null is the result and it is now SWEPT** (TASK_025_REVIEW):
   fold both rungs the same way and safe−unsafe is a *single integer per call* at
   every length — over **127 consecutive `vlen`**, slope of the difference
   `0.0000000` Ir/byte, max residual 0.00, at six spellings. The mechanism is why
   it cannot be otherwise: the reslice (R3) and the `get_unchecked` (R4) both sit
   **outside** the fold loop, so the chunk body is mnemonic-identical at
   K = 4, 8, 16, 32 and 64. **p16's per-byte safety tax is 0.00000, and that is
   the sentence to quote.**
   ⚠ **What must NOT be quoted is a bare rate, or a difference of rates across
   unmatched folds.** In contract, one exact-string substitution apart, p16's rate
   ranges **5.04688 … 6.62500** (5.7500 shipped; 6.50000 and 6.62500 for
   `chunks_exact(4)` / `(8)`; a seventh spelling at 5.37500) — a 31% spread — and
   the measured rates carry ±0.01 Ir/byte from the driver's `println` term, which
   does not cancel within a binary and is 20× the gap between two published rates.
   The cross-spelling figure that reached four files as a headline was
   ~~−0.5625~~ and is **−0.65625**: the published value was the K=16 number left
   pointing at the K=32 rung when the sentence was re-aimed. It is a codegen
   difference between two folds and was never a safety cost. "O(1) per call" is
   separately corrected to `7 + 5·nrec` / `7 + 7·nrec` (TASK_015_REVIEW). See
   `patterns/p16-tlv-walk/NOTES.md` §10a.2 and `.tasks/TASK_025_REVIEW_REPORT.md`.
   Only the *naive indexed spelling* is O(n): +4.25 Ir/byte, +69/+72%.
   Of that 4.25, a rolled-vs-rolled control (`-unroll-count=1`, a bit-for-bit
   no-op on R2) shows **exactly 2.00 is the check and 2.25 is the 4× unroll it
   forecloses**, zero residual. And it costs **+0.27% wall clock** — the fold is
   latency-bound at 3.03 cycles/byte, identical on L1- and L3-resident inputs, so
   memory bandwidth is ruled out rather than merely unconsidered.
   **Fourth pattern in a row where R3 is the honest number.**

10. **p17 — the limit, and the most important artefact here.** A suffix-range
   parser (CVE-2017-7529). One missing `start >= 0`; the served range is the last
   `s` bytes, so one attacker `u16` picks the harm. For `content_len < s <= len`
   the bad read is **inside the allocation** — ASan clean, exit 0, and **safe Rust
   with the check deleted prints C's value bit-for-bit**. Only for `s > len` does
   it leave the allocation and Rust panic.
   Then the artefact. Guard the **slice**-relative index —
   `start >= -((off + body_start) as i64)`, which is exactly what a bounds check
   buys, no more — and Verus gives **9 verified, 1 error, the single error being
   the *functional* invariant; every access obligation discharges** (10/0 with the
   functional spec stripped). It reads a **neighbouring window's** bytes: output
   tracks the victim's secret, no panic, no `unsafe`. **A provably memory-safe
   program that leaks.** Memory safety and correctness are different properties
   and this is the measurement.
   **Two corrections are baked in above, both from TASK_011_REVIEW** — the
   shipped `adversarial-leak` row discloses only the *attacker's own* request
   table, so it shows memory-safe-but-wrong, not disclosure; and the delivered
   `start >= -(body_start as i64)` guard is strictly *stronger* than a bounds
   check, which is what made its leak vacuous. The distinction is one token and
   it is the whole finding: write "what a bounds check buys" **slice**-relative.
11. **4.25 Ir/element is a property of rustc, not of a pattern — and so is its
   2.00 + 2.25 split.** p17 reproduced p16's swept constant exactly (10.0000 /
   5.7500 once the driver's `println!` digit-count term is differenced out); p05
   reproduced it a third time on a non-Horner fold, *and* reproduced the
   decomposition — 2.00 check + 2.25 foreclosed unroll — from its own no-op
   control. ~~R3 is free for five patterns and then stops.~~ **The second
   sentence is retracted** — see finding 13. **No pattern has yet shown safe
   Rust paying an unavoidable per-element price.**
12. **p05 — safety on a vectorised loop, and the first causal link from proof to
   performance.** Per element inside the vector body the check is free (1.375000,
   five rungs identical). But it is hoisted into a 22-instruction per-row
   trip-count computation and survives in the scalar epilogue, so the cost is
   `O(nrow)`, not zero — and **wider lanes make it worse**: at AVX2 the gap is
   4.58× against SSE2's 1.42×, with safe Rust absolutely slower. `ncol ≡ 0 mod 8`
   pays a *full extra vector iteration*, so every power-of-two dimension is the
   worst case.
   The cause: the kernel already checks `nrow*ncol <= avail`, so R2's panic is
   dead on every run — but LLVM cannot eliminate it, because
   `nrow*ncol <= avail ⟹ i*ncol+j < avail` is **nonlinear**, which is exactly the
   obligation R5 discharges with `lemma_mul_inequality`. Linearising the guard in
   an isolated compilation deletes the whole per-row apparatus, so nonlinearity
   **is** the blocker for this kernel — confirmed at TASK_014_REVIEW against the
   manager's suspicion that p08 refuted it. But it is **not a general law** (p08
   keeps a dead *linear* check for a *relational* reason), and
   ~~"the safety cost is the price of the optimiser failing the lemma the proof
   proves"~~ is **retracted as written**: what those instructions price is two
   *spellings*, not safety. See finding 13.

   **REINSTATED at TASK_021_REVIEW, restricted to the row-scaled term**, in
   exactly these words: *"On p05, the `O(nrow)` part of the in-contract safety
   tax is the price of the optimiser failing the lemma the proof proves."* The
   in-contract respelling removes exactly one instruction per row — the `add`
   that makes the row base buffer-absolute — and the five that survive are the
   reslice's bounds check, whose deletion needs `(i+1)·ncol <= nrow·ncol`, the
   nonlinear fact `lemma_mul_inequality` discharges. Not true of the constants,
   not a statement about safety in general.
   **But p05 has no minimum, and neither does any pattern.** Three were
   published and all three refuted, each by the first lever the next agent
   pulled: `5·nrow + 6` → `5·nrow + 11` (respell the header) → `5·nrow + 13`
   (delete a redundant zero-check). Each had been reached by several independent
   machine-code bodies, so **"reached by many spellings" is not evidence of a
   floor**. And the quantity is unsound, not just unlucky: **`min(R3) − min(R4)`
   is the difference of two upper bounds and bounds nothing in either
   direction** — measured, the same edit is −2 on R4 and +1 on R3, and
   `5·nrow + 13` *exceeds* the published `6·nrow + 9` for `nrow < 4`.
   ~~Publish the in-contract **pair interval** (`36…134 / 128…410`, with the
   published 123/399 inside it)~~ and, if one number is wanted, the fixed-R4
   bound. ~~**An admissible pair has a tax of exactly 0.00**, so p05 does not
   support "safety costs something here" over free pairings.~~
   **Both struck at TASK_028** — the interval's endpoints and the `0.00`
   pairing are `r4_dataslice` and `c4_hu16_nz`, neither of which is a rung.
   Publish the **fixed-R4 bound** and the **R3-side span** (`5·nrow + 6` …
   `6·nrow + 13` = 101…127 / 331…403); see item 1 of "Priority" below, and note
   that this paragraph is the site that survived the first correction sweep.

13. **p08, and the retraction it forced — safe Rust beat unsafe Rust on p05.**
   p08's own result is structural: overlapping `memcpy` is UB that safe Rust
   **cannot express** (borrow checker, compile time, no runtime check and so
   nothing to measure), `unsafe` re-opens it via `copy_nonoverlapping`, and
   **R5 does not close it** — substituting `copy_nonoverlapping` into the trusted
   body verifies 11/0 and 15/0 under the twin, invisible to Verus, the twin and
   the contract pins; only Miri and the O3 identity pin catch it. On this libc
   the UB **executes and is unobservable**: glibc 2.39 `memcpy` *is* `memmove`,
   so R1 ≡ R1h at **0.00 Ir/call** — a *libc* property, never to be quoted as
   "memmove is free". ASan sees the overlap, but **`_FORTIFY_SOURCE` blinds it**
   under clang as well as gcc, because the check lives in the `memcpy`
   interceptor and not in `__memcpy_chk`.
   Then the blocker, which is about **p05**: `data.chunks_exact(ncol)` — one
   idiomatic safe expression, zero `unsafe`, no proof — is **`nrow − 7`
   instructions per call cheaper than the unsafe rung**, exactly, on every input,
   with identical output on all 150 committed p05 inputs. p05's shipped R3
   reslices by hand and pays `6·nrow + 9`. **Three patterns have now priced a
   spelling as safety's cost** (p02, p16, p05).

14. **Every rung is a spelling, the gap does not converge, and "safe beats
   unsafe" was never available as a language fact.** (TASK_015 +
   TASK_015_REVIEW. The programme's central methodological result, and the one
   that shapes the writeup.)
   The audit found **all three shipped R3s beaten**, each beater also cheaper
   than **its own R4**. The control that answered it — apply the same
   consumed-slice idiom to the *unsafe* rung — put unsafe back on top at
   **+11.00 Ir/call flat**. Then the review ran **one more round on each side**:
   replace the unsafe loop counter with the canonical C test `while rp < end`
   and it becomes **`nrow + 9`** — swept exactly over all 144 blobs, zero
   residual, with a second unrelated unsafe spelling landing on the identical
   figure. **`O(1)` became `O(nrow)` and the sign of the conclusion flipped on
   the first thing a reader would try. The gap does not converge.**
   ~~And it never could, for a reason available without measuring: R4 is defined
   by *permission*, not obligation, so every safe program is an admissible R4 and
   `inf(R4) <= inf(R3)` **by construction**.~~
   ⚠ **THAT ARGUMENT IS REFUTED — TASK_025_REVIEW, and it is the most consequential
   correction in this file.** The "reason available without measuring" was wrong
   *because* nobody measured it. **All six patterns pin
   `identity: unsafe ≡ verus, O3 exact`**, so an R4 is not a program that *may*
   use `unsafe` — it is a program that **must have a byte-identical R5 twin that
   Verus verifies**. R4 is bounded by what vstd can express; R3 is bounded by
   nothing. The classes are **incomparable, not nested**, and the inclusion runs
   the opposite way from the one that was published.
   Measured instance: p16's `chunks_exact(32)` fold is admissible as R3 at **zero
   TCB** and inadmissible as R4 — `chunks_exact`, `ChunksExact`, `by_ref`,
   `TryFromSliceError` and `get_unchecked` are each unsupported at the pin, so
   shipping it needs **five** new trusted items on a pattern whose whole claim
   rests on *one*. So "safe Rust beats unsafe Rust" is **not** disposed of by the
   definitions, and on p16 it has a mechanism instead: **the safe class can reach
   spellings the unsafe class cannot, because the unsafe class is chained to the
   prover.** Whether the infimum gap is positive is open on every pattern.
   What *is* still available a priori is nothing at all — which is the lesson.
   **Both spellings that drove this were out of contract.** p05's `spec.md`
   forbids `chunks_exact` and the running row pointer by name — either deletes
   the `i*ncol + j` multiply, which *is* the pattern — and **two consecutive
   tasks measured them and reported them as p05's numbers**, the manager's own
   retraction among them. The declaration was right both times and failed only
   by being **invisible**: it is prose, and the hashed block starts 240 lines
   later. So p05's `6·nrow + 9` **stands as a contract-relative number**, and the
   retraction of it is itself retracted.
   **And that contract-relative number bounds `inf(in-contract R3) − R4ship`
   and nothing else** — a bound only because R4 is held fixed by fiat, and the
   search for what it bounds has now failed three times
   (`patterns/p05-index-flatten/NOTES.md` §14). TASK_021 reported a *two-sided*
   floor, `5·nrow + 6`, on the ground that six in-contract unsafe spellings gave
   one instruction count. They had all decoded the header the shipped way, so it
   measured the header. TASK_021_REVIEW respelled that and got `5·nrow + 11`
   from 13 unsafe spellings; TASK_022 deleted a semantically redundant
   zero-guard and got `5·nrow + 13` from 46. **Each value had been reached by
   4–10 independent machine-code bodies, and two of the three were broken
   anyway** — so "reached by many spellings" is not evidence of a floor, and
   nothing here should ever again be published as one. See finding 12.
   TASK_021's companion claim — that the *unsafe* side "does not
   move at all" (six spellings, four distinct machine-code bodies, zero
   difference) — was **refuted** at TASK_022 on the ground that respelling the
   header moves R4 by 7 flat. ⚠ **That refutation is itself refuted**
   (TASK_027_REVIEW): the respelling needs `read_unaligned` and is not an
   admissible rung at the pinned vstd, and every alternative route to it is
   unsupported too. **TASK_021's claim was right for the wrong reason** — the
   unsafe side does not move, not because six agents happened to spell the header
   the same way, but because the `identity` pin leaves them nothing else to
   spell it with. Its
   functional form, its sign
   and its `O(nrow)` conclusion all survive under that stated pairing, but the
   "21%/18% of the tax lives in unpinned spelling" figure is the **R3 side
   alone**; over free pairs the interval is 80%/71% of the published tax. (That
   was then called "the loosest of the set"; the comparison put a *pair*
   interval next to p16's **R3-only** span. TASK_023's replacement — "p16's
   own pair interval is 111%/109%, wider" — is refuted in turn: measured, p16's
   is −239…+236 / −2449…+2244, i.e. 1759%/6095%, negative at the bottom on all
   24 blobs. **Both are withdrawn and neither is re-pointed** — a 2-lever p16
   search is not the peer of a 46-spelling p05 one.) The `nrow` axis it is swept on
   ships too: `inputs/gen.py` band D, 33 blobs, and `source_sha256` covers
   `gen.py` from TASK_021 so the law is re-derivable from a hashed file.
   **The policy, decided and implemented (TASK_016–018).** "Compare idiom-matched
   rungs" **does not work** — "same idiom" has no fixed point, its members
   differing by `O(nrow)` — and a published spread **cannot carry a safety number
   at all**, per the theorem above. What ships is a **named-spelling standard**:
   every pattern's hashed contract block carries an `idiom` object naming the
   tokens each rung must spell literally, uniform across all six, **labelled as a
   policy adopted after measuring**, with one measured clause — a rung spells the
   same operands the way its language forces — without which eight shipped cells
   fall out of contract.

   **What the pin buys is decidability, not attributability, and that was
   measured.** On p17 the excluded and an admissible spelling compile to the
   **same 478 bytes**; on p16, 42 of 77 Ir/call sit inside the unpinned part.
   What it does buy is a contract a `grep` can settle instead of one only an
   argument can settle — and a *boundary*, without which the spread is unbounded
   below on both sides.

   **The conclusion that follows, and it governs every number this project
   publishes: `R3ship − R4ship` bounds `inf(in-contract R3) − R4ship` and
   nothing else — a bound only because R4 is held fixed BY FIAT rather than
   minimised. It is NOT an upper bound on the in-contract safety tax**, which is
   what this line said until TASK_023. p16's `+27/+77` has a cheapest-found
   in-contract R3 of **−199 at `small` and −2545 at `large`** against the shipped
   R4 — the value having moved four times (~~`+19/+45`~~ TASK_023,
   ~~`−199/−2365`~~ TASK_024, ~~`−127/−2545`~~ the manager at TASK_025_REVIEW,
   who paired one rung at both inputs), and **no single spelling is cheapest on
   both blobs**: `chunks_exact(64)` is 72 Ir/call *dearer* than `(32)` at `small`
   and 180 cheaper at `large`, because a larger `K` leaves a longer scalar
   remainder tail. **A cheapest-found figure must name its input as well as its
   spelling**, which is why the word is "cheapest found" and never
   "minimum"; p17's `+32` has an in-contract respelling measuring
   **−19** against
   the shipped R4, byte-identical to the row an earlier task had excluded. Both
   patterns ship an R3 measurably off the floor of their own contract, so "the
   shipped R3 is the cheapest admissible spelling" is **false, not
   unestablished**. ⚠ **But "the unsafe rung is a spelling too" is now REFUTED on
   both of the two patterns that were said to show it** (TASK_027_REVIEW).
   ~~p05's R4 moves 7 flat (TASK_022)~~ and ~~p16's R4 moves `4·nrec` via
   `r4_hdr`~~ are **the same lever and it is not admissible on either**: at the
   pinned vstd, `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`,
   `TryFromSliceError` and `from_le_bytes` are each `is not supported`, so every
   route to respelling a header read needs a **new trusted item** — and the
   `identity` pin makes a rung without a verifying twin not a rung. **Neither
   pattern's R4 side has ever moved by a single admissible instruction**, while
   the R3-side levers cost zero TCB and are large. Report the fixed-R4 bound —
   **`R3ship − R4ship` bounding `inf(in-contract R3) − R4ship`, R4 held by
   fiat** — and **do not report a pair interval until someone has built an
   admissible R4 that moves**; both published ones were built from rungs that do
   not exist. And **never a per-byte difference across unmatched fold
   spellings**.

15. **p07 — the first pattern where R3's tax has NO axis along which it
   amortises.** (TASK_026, reviewed at TASK_026_REVIEW: headline **confirmed**,
   two majors and five minors against the surrounding prose.)
   Binary search: `Θ(log n)` probes, no inner loop. **R3 costs `6.0000` Ir per
   probe with `probes = nq·⌈log2 n⌉`, so its share of kernel `Ir` rises in both
   `n` and `nq`** — 42.53% → 46.63% over `n` = 7 … 16 385. The asymptote is
   `6/(12 + f_lo)` ∈ **[46.15%, 50.00%]**, 47.99% on the shipped 50/50 workload:
   fixed by the kernel *and* the query distribution, not by the kernel alone.
   **Confirmed across six deliberately different workloads** — all-hit, all-miss,
   all-below, all-above, clustered, shipped — monotone rising in every one, so it
   is not an artefact of the query mix. The laws are exact integers verified
   **out of sample** on 30 fresh blobs with an independent probe-count
   implementation: `R3 − R4 = 9 + 4·nq + 6·probes`,
   `R2 − R4 = 36 + 11·nq + 11·probes`, 30/30 exact.
   ⚠ **What this is NOT: "the first counterexample to safety is cheap".** That was
   the manager's sentence and `.memory/01-ladder.md` already refuted it — p16/p17
   carry a swept **R2** tax of 4.25 Ir/folded byte whose fraction also rises
   (toward 73.9%), and p05 an `O(nrow)` **R3** tax. What is new is the *R3*
   scoping and the *no axis* part: p16/p17's R3 tax is a per-**call** constant
   (0.00000 Ir/byte, the reslice sits outside the fold loop) and p05's is
   `O(nrow)`, which vanishes along `ncol`. p07's vanishes along nothing.
   **The `Ir`-vs-`ns` half is real and was tightened, not broken.** Disabling
   LLVM's `X86CmovConverterPass` on unchanged source gives +10.07% `Ir` → −18.13%
   `ns`, and the review closed both of the delivery's own caveats: a
   symbol-by-symbol diff of the two whole binaries found **559 symbols, exactly
   one different**, and `--cache-sim` showed the lever locality-neutral (`D1mr`
   1076.82 on both). **Branch misprediction is measurable on this box after all**
   — `callgrind --branch-sim=yes` — see `.memory/00-environment.md`.
   Sharper still, with no compiler flag: changing only the *workload* makes the
   same binary execute **+7.84% more instructions in 71.75% less time**.
   ⚠ **Do not quote p07's R2 `ns` numbers.** `safe_naive`'s layout band is
   **28.47%** — the widest single-rung band this project has measured — so the
   "+28.0% small / +3.5% large, an 8× conversion factor" claim has **no
   established sign** and is withdrawn pending a bracketed re-measurement. R3's
   counterweight (+13.0% / +1.6%) *does* survive: bands disjoint on both inputs,
   in two independent runs.
   Two more, both confirmed: p07's R4 side is **degenerate, third pattern
   running** (`r4_ptr` measures −460/−1605 and its twin dies on *"dereferencing a
   raw pointer is not supported"*); and the catalogue's stated bug was **wrong** —
   midpoint overflow is unreachable by 2.1e9 because the `u32` header field binds
   long before RAM, while the reachable overflow is in the length check.

## Retracted — do not reinstate

- **"Safe Rust pays an O(n) bounds-check tax"** (p02). The indexed fold's bounds
  checks cost *zero*; the whole delta was one spelling of an overflow check
  defeating LLVM's `memcpy` idiom recognition. Restated as a **codegen fragility**
  finding: one spelling loses the idiom, three others are +10 flat.
- **"C beats Rust"** (pilot). A **gcc-only** measurement generalised to "C"; the
  sign was backwards. The clang result was never affected.
- **"gcc's byte loop beats glibc `memcpy`"** — mislabelled; it beats R4, not gcc's
  own memcpy build.
- **"p16 is the first true O(n) *safety* cost"** — written by the manager from an
  engineer's report **without re-measuring**, and corrected at TASK_007_REVIEW.
  R3's per-byte rate equals R4's exactly, so the O(n) cost belongs to one
  *spelling*, not to safety. This file's own rule — *never publish a safety-cost
  claim without R3* — was broken by the person who wrote it, one pattern later.
- **"gcc is 36% behind clang on p16"** — a flag default, not a codegen limit.
  With `-funroll-loops` gcc reaches 2823 and **beats** clang's 2993. Reproduced on
  p17: 7065 → 4813, past clang again.
- **"The cost of the check is the conversion, not the comparison"** (manager's
  prediction for p17). False: `i128` index arithmetic costs +4.0000 Ir/byte, but
  **signedness itself is 4 Ir per call, flat — 0.17% of the gap.**
- **"The twin's value accrues from p17 on"** — p17's accessor is single-clause
  too, and for a structural reason: its interesting harm is not a memory error.
  The twin's value starts at the first *multi-clause trusted accessor*, a property
  of the wrapped intrinsic (p27+), not of the pattern number.
- **"p17's leak is an information disclosure"** — as shipped it is not; the excess
  bytes are the attacker's own request table. Corrected to a *slice*-relative
  guard, which does disclose a neighbour window. See finding 10.
- **"`scaling_cur_freq` shows the clock"** — it reported 800 MHz for six seconds
  while the core ran at 3.80–3.89 GHz. Measure the clock with a dependent chain,
  interleaved — and even then it spans ±15% within one session.
- **"On a vectorised loop the bounds check costs 0.0000 Ir/element"** and **"the
  wider the lane, the cheaper safety gets"** (p05, manager). The first is true
  only of the vector steady state — the check is hoisted into a per-row
  trip-count computation and survives in the scalar epilogue, an `O(nrow)` cost.
  The second is **refuted**: at AVX2 the gap is 4.58× against SSE2's 1.42×.
- **"`chunks_exact` refutes p05's R3 cost"** (TASK_014_REVIEW's blocker, which
  the manager landed as a retraction). **The retraction is itself retracted**:
  `chunks_exact` is forbidden by p05's own `spec.md`, so it measures a different
  kernel. p05's `6·nrow + 9` stands **as a contract-relative number**. What does
  not stand is reading it as "what safe Rust costs" — finding 14.
- **"Safe Rust beat unsafe Rust"**, and its repair **"p05's idiom-matched safety
  number is +11.00 Ir/call, flat, `O(1)`"**. One more unsafe round makes it
  `nrow + 9`. Both spellings were out of contract. (This entry used to add "and
  `inf(R4) <= inf(R3)` holds by construction anyway" — **that half is itself
  retracted at TASK_025_REVIEW**; see finding 14. The retraction of "safe beats
  unsafe" stands on the out-of-contract ground, which is the measured one.)
- **"`inf(R4) ≤ inf(R3)` by construction, so safe-beats-unsafe is never available
  as a language fact"** (manager, offered as "a reason available without
  measuring", carried for six patterns in three files). **All six patterns pin
  `identity: unsafe ≡ verus, O3 exact`**, so an R4 must have a byte-identical R5
  that Verus verifies: R4 is bounded by what vstd can express and R3 by nothing.
  The classes are **incomparable**. Measured on p16 — the same fold is admissible
  as R3 at zero TCB and needs five trusted items as R4. See finding 14.
- **"Compare idiom-matched rungs"** (manager, one turn after inventing it).
  "Same idiom" has no fixed point; its members differ by `O(nrow)`.
- **"p17's R3 costs +32 Ir/call, flat"** — flat *per byte*, not per call. Both
  published bands happen to have `nsuf = 3`; swept, `R3ship − R4` runs 18…63.
  p17 ships no sweep inputs, which is how a two-point constant became a law.
- **"p16's R3 cost is O(1) per call"** — `7 + 5·nrec` at `vlen ≡ 0 (mod 4)`,
  `7 + 7·nrec` otherwise. `O(nrec)`, and the two published points were nrec 4
  and 10.
- **"Overlap UB is not caught by ASan"** (manager, in the catalogue since it was
  written). It is caught — `memcpy-param-overlap`, exact to the byte — unless
  the call site is fortified to `__memcpy_chk`, which blinds ASan under clang as
  well as gcc.
- **"The bug is not expressible at R5"** (p08's own README). It is, and it
  verifies clean: a proof of a `requires` is not a proof that the trusted body
  honours it.
- **"p08 undermines p05's nonlinearity claim"** (manager, TASK_014_REVIEW Part 3).
  Refuted with disassembly: p08's retained check is blocked by a *relational*
  deduction, not a nonlinear one, and p05's linearisation counterfactual goes the
  manager's way. p05's cost claim fell for an unrelated reason.

## Working method

See `.tasks/PROTOCOL.md` for the full rules. The short version: manager writes
specs and `.memory/`, one subagent at a time alternating engineer → reviewer,
manager lands `.memory/` corrections and commits.

**Do not write a finding into `.memory/` before its review lands** —
`.tasks/PROTOCOL.md` rule 9. Four consecutive reviews caught the manager
overclaiming, every time from the same cause. Engineer writes `NOTES.md`, manager
commits it, reviewer attacks it, *then* `.memory/`.

**Ask to be corrected, not obeyed.** Agents have contradicted the manager's
written instructions **thirteen times** with measurements and were right all
thirteen.
Two were prescriptions that could not have worked at all; one overturned three
premises in a single review; the latest caught the manager overclaiming a
headline. Say so in every task file.

## The recurring traps

- **A green gate is evidence about the gate.** Four reviews found defects past a
  fully green run, twice with an unchanged contract hash.
- **A vacuous truth in a log reads like a discharged obligation.** Six instances of
  "every X is Y" printed over an empty collection. Now a rule: a count-bearing
  success line prints its `n`, and `n == 0` fails.
- **Checks fail open.** Three times a malformed mutant that failed to *compile* was
  read as "the check passed".
- **Declared pins are self-certifying** — they move in the same commit as the code
  they constrain. Derive where possible; the Miri cross-check and the new
  callgrind "did this code run" check are the models.
- **Residues.** p01 tripped mod 4 three times; p02's real modulus was 16. Sweep two
  full cycles; never sample two points.
- **Attribute nothing without decomposing.** Change one loop at a time. This is
  what killed the O(n) claim.
- **Say which columns a staleness argument covers.** "The kernels are identical so
  the numbers stand" was right about kernel columns, wrong about whole-binary ones.
- **Residues bite at whatever width the codegen chose, and the round numbers are
  the worst case.** p01 mod 4, p02 mod 16, p16 mod 4, p05 mod 8 with **residue 0
  the outlier** — so every power-of-two dimension pays a full extra vector
  iteration. The size a benchmark author reaches for first is the trap.
- **`ns` is a measurement on this box; `cycles` is an inference.** The clock is
  set by other tenants and spans ±15% even measured interleaved in one session.
- **A finding needs a mechanism, not just a number.** "It vanished" was p05's
  first answer; the real one was a hoisted trip-count computation and a surviving
  scalar epilogue, and it changed the conclusion.
- **You are measuring a spelling until you have written two — and then you are
  still measuring a spelling.** Three retractions (p02, p16, p05) came from one
  plausible R3 published as what *safe Rust* costs. Writing a second spelling
  does not fix it: on p05 the spread across eleven exceeds the safe-vs-unsafe
  gap, and the unsafe rung has spellings too. Only a matched pair under a
  **declared, pre-registered** idiom carries a safety number (finding 14).
- **Read the pattern's `spec.md` before believing a cross-pattern rule.** Two
  consecutive tasks measured spellings p05's `spec.md` forbids **by name**, in a
  section titled "Load-bearing, do not improve", and neither cited it — because
  `.memory/01-ladder.md`'s R3 definition listed the forbidden spelling as a
  technique. A general file and a pattern file disagreed and the general one
  won twice.
- **A tool that reports nothing may be a tool that cannot see.** ASan is silent
  on p08's overlap not because there is none but because fortify rewrote the call
  to `__memcpy_chk`. A gate row records `clean` for both reasons identically.
- **Two files, two numbering schemes.** RECAP's findings are numbered 1–15,
  `.memory/01-ladder.md`'s are 1–7. Name the pattern, never the number.
  **And one task file is misnumbered**: `.tasks/TASK_025_REVIEW.md` reviews
  **TASK_024**, not TASK_025 (there is no TASK_025). Every other
  `TASK_NNN_REVIEW` reviews `TASK_NNN`; `TASK_027_REVIEW` restores the
  convention. Cite reviews by what they *found*, not by their number.
  (This file also *shipped findings 13 and 14 twice*, with divergent text, from
  an insert-where-a-replace-was-meant. One copy asserted p05's `5·nrow + 6`
  floor as a narrowing result while the other recorded its refutation. Deduped
  and merged 2026-08-18. When you edit a finding, `grep` its opening words first.)
- **Never publish a bare per-byte rate, or a difference of rates across unmatched
  spellings. Publish only matched-spelling differences.** (TASK_024,
  TASK_025_REVIEW — the answer to "is K-dependence a finding or a surrender" is
  *both*, split.) A bare rate is **not a property of the kernel**: p16's ranges
  5.04688 … 6.62500 in contract, one exact-string substitution apart, and is not
  even measurable past ±0.01 because the driver's `println` term does not cancel
  within a binary. So p16's 5.7500, p17's 10.0000/5.7500, p05's 1.375000 and
  finding 11's 4.25 are all quoting a free parameter. A **cross-spelling
  difference** of two such rates is worse — that is exactly what −0.65625 is, and
  it reached four files as a headline with the wrong arithmetic on top. But the
  **matched-spelling difference is a property of the kernel**: 0.0000000 Ir/byte
  over 127 consecutive lengths × 6 spellings, with the mechanism visible. Note
  what this means: **the rule TASK_024 adopted — "name the fold beside the rate" —
  does not catch its own headline figure.** A mechanical backstop was costed at
  ~90 lines (`spec.md` pins the shipped fold's chunk-body instruction count;
  `check.py` asserts `body_len / K` equals the published rate) and is **not yet
  proposed as gate work** — it would have to pass "could this happen by
  accident?" first, and it has happened by accident twice.
- **A cited artefact can refute the claim it is cited for.** `.temp/p24/foldbody.py`
  is named in p16's `NOTES.md` as the evidence for mnemonic identity; re-run as
  committed it prints `identical=False` at every `K`. The claim is *true* — a
  reviewer re-derived it — but for a year nobody would have known which. Re-run
  the artefact, do not cite it.
- **Run `./verus_run.py` on an R5 twin BEFORE differencing any unsafe-side
  variant.** Every `identity`-pinned rung is chained to the prover, so an
  unsafe-side "cheaper spelling" that vstd cannot express is not a rung and its
  number means nothing. This one check would have caught p16's `u_c32`, p16's
  `r4_hdr`, p05's `c4_hu16_nz`, p05's `r4_dataslice` and both endpoints of p05's
  published pair interval — five published figures, across two patterns, over
  four tasks. It costs about eleven minutes.
  **And read the error text, not the exit code**: `is not supported` disqualifies
  (it forces a new *trusted* item); *"postcondition not satisfied"* disqualifies
  nothing — measured on p05, the same exec code went from `11 verified, 1 errors`
  to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB.

## Priority — read this before planning

**Twenty-eight tasks in, 7 of 47 patterns exist.** Six tasks went to gate
hardening before the user called it; **TASK_015–028 — thirteen consecutive tasks —
went to the *spelling* problem** and produced no new pattern. That arc paid (the
named-spelling standard, four refuted floors, p16's sign error, and the
R4-is-chained-to-the-prover result that retired two published intervals), and p07
was built to its rules natively rather than corrected into them. **It is closed.
Alternate build → review from here, and do not reopen it without a measurement
that forces it.** The gate's
threat model is **honest mistake, not
malicious author** (`.memory/02-bench-rules.md`, top section, with the list of
residuals we are deliberately leaving open). New gate work must pass "could this
happen by accident?" first.

**Spend the coming tasks producing patterns.** Review each pattern once; do not
review each fix to each check. p16 is the proof this works: built, measured,
proved and reviewed inside two tasks, and the review still found a real
overclaim — which is the *right* place for review effort.

## Immediate queue

The gate-hardening arc is **closed**. Five pattern tasks since have each gone
green on the first complete run. The working mode is: **build a pattern, review
it once, land the corrections, repeat** — and per `PROTOCOL.md` rule 9, write
`.memory/` only *after* the review.

**THE NEXT TASK IS `TASK_026_REVIEW` — p07 is built, green and unreviewed**, and
per rule 9 nothing of it is in `.memory/` yet. It reports the **first
counterexample to "safety is cheap" in seven patterns**, so it is the highest-value
thing in the project to attack. Its engineer named the target itself: it shipped a
defective input generator (every miss drawn as `element + 1`, so no key ever fell
below `elements[0]`, which made its own inclusive-`hi` control print the *correct*
checksum), caught it with its own control, and says the workload — not the kernel
— is what a reviewer should go after. Attack the workload, the layout band, the
`Ir`→`ns` inference, and the exact-integer laws.

**Items 1–2a below are the closed spelling arc, kept for the history.** That arc
ran TASK_015–028, thirteen tasks; it is finished and its rules are distilled in
`.tasks/TASK_026.md` §0, which is the shortest statement of what this project
learned about reporting spellings.

1. ~~**TASK_023 — the `idiom.why` sentence is false in all six patterns.**~~
   **Done.** The sentence is replaced byte-identically in all six `idiom.why`
   blocks; both ride-alongs done. The probe TASK_023 asked for — *is the
   sentence false for the other patterns or merely unverified?* — came back
   **false, not unverified**: p16's unsafe rung moves in contract by
   `R4ship − r4_hdr = 4·nrec` Ir/call (the two length bytes as one unaligned
   `u16`, the same lever that moved p05's R4), zero residual over 24 blobs, and
   the admissible pair `(r3_hdrarray, r4_hdr)` **exceeds** the published
   `+27/+77` by `5·nrec`. ⚠ **The pair interval TASK_023 published from that —
   `nrec + 13` … `7 + 10·nrec` / `3·nrec + 13` … `7 + 12·nrec`, "111%/109%
   wide" — is REFUTED** (TASK_023_REVIEW): it was a 2-lever search on a
   declaration that also licenses **unrolling**, which is the only lever of the
   three that acts *per byte*. Measured, the interval is **−239…+236 (1759%) /
   −2449…+2244 (6095%)** and its **bottom is negative on all 24 blobs**; the
   in-contract minimum against the shipped R4 is **−199 / −2365**, not
   `+19 / +45`. `r4_hdr` also **cannot be a p16 rung** — vstd cannot verify
   `read_unaligned` and the `identity` pin needs R5 ≡ R4, so it would need a
   fourth trusted item — while the R3-side levers cost zero TCB. **What survives
   and is now the statement to quote: fold both rungs the same way and the
   per-byte rates are equal to five decimal places at all six spellings
   measured, and the unsafe rung is cheaper per *record* on every point.** The
   three R4 controls ship in
   `patterns/p16-tlv-walk/controls/gen_controls.py`; the write-up is that
   pattern's `NOTES.md` §10a.1 and §10a.2. **p17, p02, p01 and p08 remain
   unverified on the R4 side** — their published figures are one-sided bounds,
   not upper bounds on a tax, and p17's `−19.00` is the same shape of claim that
   the unroll lever manufactured on p16.

   **TASK_024 landed the corrections and contradicted the paragraph above;
   TASK_025_REVIEW then attacked TASK_024 and found a blocker and four majors**
   (`.tasks/TASK_025_REVIEW_REPORT.md`). What survives, what died, and what is
   still owed:

   **Survives, and is now stronger than published.** The matched-spelling null —
   the *only* thing this arc leaves standing as p16's per-byte number — was
   re-derived over **127 consecutive `vlen`** where TASK_024 had three pairs at
   one residue offset: safe−unsafe is a single integer per call at every point,
   slope `0.0000000`, max residual 0.00. Mnemonic identity holds at K=4 and 8 too
   (TASK_024 under-claimed); all twelve probes honour **all four** `required`
   entries, not just the two the matcher checks; the band-A offset is the
   `println` term, now controlled; 1140 equivalence comparisons, 0 mismatches;
   Miri clean; tree green.

   **Died.** (i) `u_c32` **cannot be a p16 R4 rung** — the `identity` pin needs a
   verifying byte-identical R5 and vstd supports none of `chunks_exact`,
   `ChunksExact`, `by_ref`, `TryFromSliceError`, `get_unchecked`; shipping it
   needs *five* new trusted items where `r4_hdr` was disqualified for needing one.
   So "at matched spelling the unsafe rung is cheaper" has no rung behind it —
   and see finding 14, which this overturned project-wide. (ii) `−0.5625` is
   arithmetically wrong for the rung it names: **−0.65625**. (iii) `−199/−2365` is
   not the minimum — `chunks_exact(64)` gives **−127/−2545**, the fifth published
   minimum overturned by the next search. (iv) "`chunks_exact(4)` is dearer,
   therefore the free parameter is not a dial that flatters the safe rung" is an
   artefact of `try_into`: drop it and K=4 measures 5.37500 and is **1509 Ir/call
   cheaper** than shipped R4 at `large`. (v) The **direction test is stated with
   its sign inverted relative to its own cited precedent**, so TASK_024's
   load-bearing "we are not allowed to pin it" argues from a rule that decides
   nothing — and the exclusion would not have restored `+19` anyway, because
   manual unrolling is licensed by name and manual 32× is 5.18750 < 5.75. **The
   decision not to pin stands; every stated reason for it is withdrawn.**

   **Still owed — TASK_027.** The pattern-file corrections for (ii)–(v), and the
   reproduction gap: §10a.2's twelve probes exist only in gitignored
   `.temp/p24/*.py`, where `controls/*.py` is inside `source_sha256` precisely so
   that cannot happen. Note `.temp/p24/foldbody.py`, which §10a.2 cites as its
   evidence for mnemonic identity, **prints `identical=False` at every K when
   re-run as committed** — the claim is true and its cited artefact refutes it.
   **TASK_027 landed all of it and the gate is green; TASK_027_REVIEW then found
   the R4-expressibility step VALID and used it to break p05.** See the new item
   1a. What p16 still owes is small: `NOTES.md:1535` says "reproduce the whole
   table" and `foldcmp.py` reproduces 8 of 10 rows (the two manual-unroll rows
   are not derivable from the tree), and `gen_controls.py`'s docstring says both
   "eighteen" and "sixteen" variants — 18 is right.

1a. **THE CORRECTION SWEEP — TASK_028, and it is next.** The sentence *"it moves
   the UNSAFE rung too, by the same lever: p16's by `4·nrec`, p05's by 7 flat"*
   is inside the hashed `why` of **all six patterns**, and **both instances are
   now refuted** — the lever is a header respelling and at the pinned vstd every
   route to it (`read_unaligned`, `as_ptr`, `add`, `from_raw_parts`,
   `TryFromSliceError`, `from_le_bytes`) is `is not supported`, so it needs a new
   trusted item and is not a rung. p05's published pair interval
   `2·nrow − 2 … 6·nrow + 20` has **both** endpoints set by inadmissible R4s; the
   admissible substitution is `5·nrow + 6 … 6·nrow + 13`, i.e. back to the
   R3-only span it was introduced to replace. "An admissible pair has a tax of
   exactly 0.00" is withdrawn — that pairing's R4 is `r4_dataslice`.
   Six hashed blocks, six gate runs. It is a **deletion of refuted text**, not a
   new investigation, and it is owed before p07 adds results on top of it — which
   is the same argument that opened this arc at TASK_014_REVIEW.
   Ride-alongs: `harness/check.py:56` and `:1723` call the identity pin *"a
   RESULT, not a gate condition"*, which is **false** (`rep.fail` at `:1763` →
   `verdict = "FAIL"` at `:4826`) and is the one sentence in the tree arguing
   against the step; and `spec.md`'s new R4-expressibility sentence needs **"at
   the pinned vstd"**, which the `r4_hdr` instance beside it already carries.
2. **p01 and p08 still owe an in-contract spelling spread** — and after p05,
   what they owe is an *R3-side* span with R4 held by fiat. **Do not let either
   publish a pair interval**: both that have been published were built from R4s
   that are not rungs. And do not let either publish a "floor"; four have been
   published across the project and four were refuted.
2a. **The unbuilt spelling, on two patterns, and it is the open question.**
   Nobody has built an admissible R4 that moves — p05's `−2` residue (delete the
   redundant zero-guard, keep the shipped header) verifies at **zero TCB**,
   `13 verified, 0 errors`, but all 26 of TASK_022's round-3 variants pair that
   deletion with `read_unaligned`, so it has never been compiled; and p16's
   hand-unrolled 32× fold with explicit indices was never tried. **Until one of
   them is built, "does the admissible R4 class move at all?" is open on every
   pattern**, and the honest answer to "is the unsafe rung a spelling too?" is
   *unknown*, not *yes*. Both are cheap. Either would settle it.
3. **A shipped p17 sweep.** p17 has **no sweep inputs at all**, which is how its
   "+32 Ir/call flat" got published from two bands that both happen to have
   `nsuf = 3`. `.memory`'s own residue rule applied and was not followed. The
   review's `nsuf` 1–8 inputs are generated under `.temp/` and are not shipped.
4. **p07 binary search** — `O(log n)`, almost pure per-call overhead with no
   inner loop to amortise over, so any R3 cost shows up as a large *fraction*
   rather than a flat constant. Midpoint overflow `(lo+hi)/2` is p17's shape
   again: an arithmetic bug giving a wrong-but-in-bounds index.
5. **p47 constant-time compare** — a third security axis, where the adversary is
   the **optimiser** and Verus cannot state the property at all. Expect it to
   defeat R5 in an interesting way; a documented R5 failure is a finding here.
6. **p27+ raw pointers.** No longer "the only place the twin can earn its keep"
   — p08 did that (mutant M2, the weakened `requires`, caught by the twin and by
   nothing else). p27 is now just the next hard proof.

**Two harness items, both identified and deliberately not fixed**, because the
"could this happen by accident?" test applies and neither blocks a pattern:
stage 7 builds gcc-only at this box's fortify-3 default and is therefore blind
to `_chk`-rewritten `mem*` misuse; and a gate row cannot distinguish "sanitiser
clean" from "sanitiser cannot see". Both are in `.memory/06-catalogue.md`.

## State

- `harness/` — `check.py` (17 stages: `0b` is the declared-idiom key and its
  reporting-only spelling audit, added at TASK_016/020; plus clause deletion,
  `requires` strength, the verified twin, and region-actually-runs), `asm.py`,
  `dloop.py`, `vparse.py`, `build.py`, `measure.py`, `report.py`, `fixture.py`.
  **`check.py` is 4905 lines against six patterns** (9083 across all of
  `harness/`). It was 4251 at p08 and frozen through it; **TASK_016–020 added
  654 lines, all of it the idiom mechanism** — a 15% growth in the gate for one
  concept, which is the largest single-arc increase since the hardening tasks.
  Each increment passed the "could this happen by accident?" test with a
  *measured count of accidents* rather than an argument, which is the standard
  this file sets and the first arc to meet it with numbers. Note the ratio
  anyway: the next gate proposal should have to beat it.
- **Gate: all six re-run at TASK_016 and green** — p02, p16, p17, p05, p08
  `PASS` — each green on
  its first full run. **p01 is `PASS-WITH-BLOCKED-ROWS`**: Miri is mandatory for
  any pattern with a trusted item and cannot finish p01's `large.bin` in 180 s,
  so 8 of 9 inputs are checked and the ninth is documented. Policy working, not a
  regression — do not read an old `PASS` as equivalent.
- `results/p02-buffer-copy.json` was re-measured at TASK_011; **that debt is
  closed.** `binary_text_bytes` moved in 10 of 32 cells, all C, for a structural
  reason worth knowing (`.memory/03-measurement.md`).
- Toolchain: Verus `0.2026.08.09.92f466f`, rustc 1.97.1, clang/LLVM 22.1.6,
  valgrind 3.27.1, nightly+Miri, all in `~/tools`, no root. `TOOLCHAIN.md`.
- **p05's `inputs/` holds ~189 MB of gitignored sweep blobs**, regenerable with
  `gen.py --sweep`. Left in place because `rm` outside `.temp/` stalls on review;
  delete by hand if the box gets tight (`df -h /`).
- **p08's `inputs/` holds gitignored blobs too** — ~33 MB, of which only the
  generators are tracked.
- **`.temp/` was swept 2026-08-18: 12 GB → 574 MB**, and the rule that produced
  it is now `.memory/00-environment.md` constraint 6 (**keep the generator,
  delete the artefact**) and `CLAUDE.md`'s Don't-1. What was deleted: 10,567
  files — 6.4 GB of compiled cell binaries, 4.9 GB of generated `.bin` blobs,
  0.2 GB of `.o`/`.pyc` — inventoried by path and size in
  `.temp/CLEANUP-MANIFEST-2026-08-18.txt`. What was kept: every text artefact,
  36 MB, which is what the evidence always was. Verified afterwards by
  `harness/fixture.py --check`, which rebuilt the pilot fixture from source and
  reproduced all six `md5_fn`/`md5_raw` pins and both identity levels — `PASS`,
  so the sweep cost nothing. The rule generalises: an agent deletes **its own**
  task's binaries when its gates are green and reports anything older to the
  manager.
- **Gate: all seven green.** p07 `PASS` on its first complete run (R5 10/0 first
  try, `unsafe ≡ verus` exact at O3, Miri clean on all seven inputs including a
  12 MB `large.bin` in 1.9 s of a 180 s budget). The shared named-spelling
  paragraph is **byte-identical across all seven** `idiom.why` blocks
  (`len=11003 sha=59748cce2db5c572`).
- **p07's `idiom` is the first that pins anything mechanically.** Backticked
  spellings by pattern: p01 **0**, p05 **0**, p08 8, p16 12, p17 12, p02 21,
  **p07 34** (102 spelling×rung pairs). p01 and p05 backtick *nothing*, so the
  standard's own audit has never fired on them — which is worth knowing before
  quoting either as "in contract".
- **`patterns/p07-binary-search/inputs/` holds 17 MB of gitignored blobs**,
  regenerable in ~40 s from `inputs/gen.py --sweep`, verified deterministic
  (120/120 byte-identical across two regenerations).
- Commits run through the **p07 landing**. Tree clean. TASK_024's
  engineer died to an API 529 after finishing its work and before reporting, and
  the manager reconstructed and committed it; TASK_025_REVIEW then attacked it
  (PROTOCOL rule 3) and found a blocker and four majors. **p16's pattern files
  still carry the four refuted figures — that is TASK_027**, and until it lands,
  `patterns/p16-tlv-walk/` disagrees with `.memory/` and `.memory/` is the one to
  believe.
- **Background `nohup` jobs on this box report "completed" while still running.**
  Two concurrent measurement runs shared a scratch path and produced one wrong
  data point, caught only because the column was otherwise a constant. Run
  measurements in the **foreground**, and give any scratch file a per-PID path.

## Decisions

- **Proof-effort budget**: one engineer session per R5 cell, then stop and report
  where the proof stuck — that report *is* the deliverable for that row. Set by the
  manager, pending a user override.
- **`perf_event_paranoid ≤ 1` needs root and is still owed by the user.** It is the
  only way to explain *why* gcc's shorter loop runs slower. Nothing works around it.
