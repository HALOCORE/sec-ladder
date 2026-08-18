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

47 patterns are catalogued in `.memory/06-catalogue.md`. **Six exist, all green
and all reviewed:** p01 (calibration), p02 (first real bug), p16 (first
data-dependent bound), p17 (the limit of memory safety), p05 (the first
vectorised kernel), p08 (the first structural Rust win).

## The findings so far — this is the actual output

**Numbering warning, because it has already cost an agent time.** The list below
is **RECAP's own digest** and is numbered 1–14. `.memory/01-ladder.md` has a
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
   with size. Only the *naive indexed spelling* is O(n): +4.25 Ir/byte, +69/+72%.
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
   And it never could, for a reason available without measuring: **R4 is defined
   by *permission*, not obligation**, so every safe program is an admissible R4
   and `inf(R4) <= inf(R3)` **by construction**. What is *not* available a priori
   is whether that infimum gap is zero or positive — which is exactly the
   quantity that moved from 11 to `nrow + 9` when someone looked.
   **Both spellings that drove this were out of contract.** p05's `spec.md`
   forbids `chunks_exact` and the running row pointer by name — either deletes
   the `i*ncol + j` multiply, which *is* the pattern — and **two consecutive
   tasks measured them and reported them as p05's numbers**, the manager's own
   retraction among them. The declaration was right both times and failed only
   by being **invisible**: it is prose, and the hashed block starts 240 lines
   later. So p05's `6·nrow + 9` **stands as a contract-relative number**, and the
   retraction of it is itself retracted.
   **The policy that follows** (recommended, not yet implemented): "compare
   idiom-matched rungs" **does not work** — "same idiom" has no fixed point, its
   members differing by `O(nrow)` — and a published spread **cannot carry a
   safety number at all**, per the theorem above. What survives is a
   **matched-pair delta under an idiom declared before measuring**, moved into
   the hashed contract block so the gate can see it, plus a spelling-spread
   section published as method and never as headline.

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
  `nrow + 9`. Both spellings were out of contract, and `inf(R4) <= inf(R3)`
  holds by construction anyway.
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
- **Two files, two numbering schemes.** RECAP's findings are numbered 1–13,
  `.memory/01-ladder.md`'s are 1–7. Name the pattern, never the number.

## Priority — read this before planning

**Fifteen tasks in, 6 of 47 patterns exist** — six tasks went to gate hardening
before the user called it; every task since has produced or reviewed a pattern. The gate's threat model is **honest mistake, not
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

**The next task is not a new pattern.** TASK_014_REVIEW's blocker is the third
instance of the same mistake, and the correction is owed across the whole result
set before more results are added to it:

1. **Review TASK_017** — it is landed and all six gates are green, but its
   central act is a **judgement, not a measurement**, and the engineer said so:
   p16's `idiom.required[0]` was disambiguated as naming **tokens**, which puts
   p16's cheaper spelling out of contract. Both readings are true of the shipped
   tree, so no experiment decides it. **The direction of the risk is that the
   chosen reading makes p16's own number look better** — the engineer flagged
   this itself and neutralised it by recording that p16 now has *zero* measured
   admissible alternates, so "cheapest admissible" is unestablished rather than
   established. A different agent should attack the reading and the four grounds
   given for it (house convention; the tokens *being* the traversal; the
   exclusion falling symmetrically on the consuming R4 control; and `inf(R4) <=
   inf(R3)` leaving the semantic reading with no fixed point).
   Also worth a second pair of eyes: `report.py` now prints each pattern's
   declaration above its table — the one mechanism that addresses the failure we
   actually observed twice.
2. **p16 owes a spelling-spread measurement inside its own contract.**
   `.memory/05-layout.md` demand 13 asks for two alternates per rung; after
   TASK_017's reading, p16 has none that are admissible. Cheap, and it closes
   the gap the reading opened.
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

- `harness/` — `check.py` (17 stages: stage `0b` is the declared-idiom key,
  added at TASK_016; plus clause deletion, `requires` strength, the verified
  twin, and region-actually-runs), `asm.py`, `dloop.py`, `vparse.py`,
  `build.py`, `measure.py`, `report.py`, `fixture.py`. **4396 lines against six
  patterns** — that ratio is why gate work needs the "could this happen by
  accident?" test. It was unchanged across the whole of p08; TASK_016 added the
  first 145 lines since the hardening arc closed, and that check passed the
  accident test with the strongest answer any check here has had — the mistake
  it prevents had already happened twice, to two different agents, in
  consecutive tasks.
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
- **p08's `inputs/` and `.temp/review014/` hold gitignored blobs too**; p08's dir
  is ~33 MB, of which only the generators are tracked.
- Commits run through the TASK_014_REVIEW landing. Tree clean.

## Decisions

- **Proof-effort budget**: one engineer session per R5 cell, then stop and report
  where the proof stuck — that report *is* the deliverable for that row. Set by the
  manager, pending a user override.
- **`perf_event_paranoid ≤ 1` needs root and is still owed by the user.** It is the
  only way to explain *why* gcc's shorter loop runs slower. Nothing works around it.
