# Pattern catalogue — master tracker

The C patterns the benchmark aims to cover. **This file is the single source of
truth for what exists and what state it is in.** The manager updates `Status`
after each task closes; agents read it to know what is already done.

Status values: `planned` · `wip` · `done` · `partial` (some rungs missing, documented)
· `blocked` (with a note). R5 column records the Verus outcome specifically, since
"R5 defeated" is itself a result worth publishing.

## Wave 0 — infrastructure

| ID | Item | Status |
|---|---|---|
| T001 | clang 22.1.6 + valgrind 3.27.1 into `~/tools`; pilot re-measured | **done**, reviewed |
| T002 | `harness/` + `common/` + p01 as the template | **done**, reviewed |
| T003 | harden the gate against the six demonstrated bypasses | **done**, reviewed |
| T005 | derive the pins; unblock p02; the barrier swap | **done**, unreviewed |
| T004 | p02 buffer copy — first real bug, first adversarial table | **done**, reviewed (perf headline refuted) |
| T006 | retract p02's perf claim; close the reopened bypass; fix the floor | **done**, reviewed |
| T008 | close the two bypasses T006_REVIEW demonstrated; harden 5c and the floor | **done**, reviewed |
| T009 | judge the *strength* of a trusted `requires` (the verified twin); close the paren-`&&` hole | **done**, reviewed |
| T010 | fix the twin's perimeter (3 bypasses); tie the driver region to code that runs | **done**, reviewed |
| T007 | p16 TLV walker — the first data-dependent loop bound | **done**, gate PASS first run, **reviewed** (headline overclaimed, corrected) |
| T011 | p17 HTTP suffix-range (CVE-2017-7529) — the limit of memory safety | **done**, gate PASS first run, **reviewed** (leak claim refuted; real artefact found one token away) |
| T012 | ship p17's slice-relative guard — the artefact T011 claimed | **done**, reproduced independently; gate PASS, no measured number moved |
| T013 | p05 2-D index flattening — the first **vectorisable** kernel | **done**, gate PASS first run, **reviewed**; every number reproduced, four framing claims corrected |
| T014 | p08 overlapping move — the bug safe Rust cannot express | **done**, gate PASS first run, **reviewed**; six manager prescriptions refuted, and the review's blocker landed on **p05**, not p08 |
| T015 | the R3 audit across p05/p16/p17 | **done**, **reviewed**; the manager's specced cell swap was **declined and the decline was right**; produced **RECAP finding 14** (*"every rung is a spelling"* — `01-ladder.md`'s 14 is p13) |
| T016 | the declared-idiom key, hashed and required | **done**, all six green, **reviewed**; its advertised mechanism was disproved by experiment |
| T017 | say what the key actually does; three declaration defects | **done**, all six green, **unreviewed** — the p16 `required[0]` reading is a judgement and needs one |

**T010's review closed the gate-hardening arc.** It was deliberately shaped as
the opposite of the previous six — not a bypass hunt but "will this gate *accept*
the next pattern?" — and answered **PASS on all four** of the checks p16 would be
first to exercise, overturning three of the manager's premises with measurements.
Two findings are folded into T007 Part 0: a `rep.ok` that fires over an empty set
when the kernel symbol does not fullmatch (a gcc IPA clone silences the
decoy-catching limb), and `MAX_TWIN_JUSTIFICATIONS`, deleted as a redundant
manager-invented round number that could hard-fail an honest pattern. It also
adjudicated the verified twin — the manager's own design — as **worth keeping**,
on the ground that Miri never opens `verus.rs` and so is not a partial backstop
for a too-weak trusted `requires` but *none*.

**Priority shift, decided by the user after T010.** Six of ten tasks went to
gate hardening and 2 of 47 patterns existed. **It worked**: the two tasks since
produced p16 and p17, each green on a complete run first try, each reviewed or
awaiting one review — and p17 delivered the programme's first *negative* result
about memory safety, and p05 the first causal link from proof to performance.
**5 of 47 existed at that point; the current count is in the tables below and in
`RECAP.md`, not here** — this paragraph is the T010 snapshot and its "now" is
2026's earlier one. The gate's threat model is now
explicitly *honest mistake, not malicious author* (`.memory/02-bench-rules.md`,
top section, with the residuals we are deliberately leaving open). New gate work
must pass "could this happen by accident?" first. **Produce patterns; review each
pattern once, not each fix to each check.**

p01 is now `PASS-WITH-BLOCKED-ROWS` rather than `PASS`: TASK_010 made Miri
mandatory whenever a pattern has any trusted item, and Miri does not finish p01's
`large.bin` within 180 s. 8 of 9 inputs are checked; the ninth is a documented
blocked row. That is the policy working as intended, not a regression — but it
means the headline verdict string changed, so do not read an old `PASS` as
equivalent.

Each task has been reviewed adversarially and each review found real defects. The
cumulative lesson, worth reading before adding a pattern: **a green gate is
evidence about the gate, not about the work.** T001's review found the identity
oracle could not detect difference (a collision was constructed) and that the
pilot's proof had no verified call site. T002's review got six defects past a
28/28 PASS, including the pilot's exact fatal defect. T003 fixed those and its own
engineer then found a seventh defect in its own delivery after reporting.

Findings are folded into `.memory/01`–`05`; those files supersede the pilot and
supersede any earlier task report they contradict.

## Open cross-cutting issues

- **THE DECIDED QUESTION: every rung is a spelling — the ladder reports a
  matched-pair delta under a *declared* idiom, and nothing else can.**
  (TASK_015 + TASK_015_REVIEW.) The audit found all three shipped R3s beaten,
  each beater also cheaper than its own R4; the R4′ control then put unsafe back
  on top. **Both halves used spellings p05's `spec.md:69-73` explicitly
  forbids**, and neither task cited it — the pin is prose at line 69 while the
  hashed block starts at 309, so `contract_sha256` is blind to it. `spec.md` was
  right both times it was tested and failed only by being **invisible**.

  Two results settle the reporting question:
  1. **"Same idiom" has no fixed point.** R3′/R4′ were matched under the audit's
     own criterion; R4″ satisfies it too and is `nrow + 2` cheaper; R4‴ — the
     safe program with only its checked slice constructions replaced — lands on
     R4″. The class members differ by `O(nrow)`, so no gate check can pick one.
  2. **A published spread cannot carry a safety number at all.** R4 is defined by
     *permission*, so every safe program is textually an admissible R4 and
     ~~`inf(R4) <= inf(R3)` **by construction**~~. Publishing two intervals tells
     a reader a theorem, not a measurement.
     ⚠ **The by-construction half is REFUTED (TASK_025_REVIEW).** All six
     patterns pin `identity: unsafe ≡ verus, O3 exact`, so an R4 must have a
     byte-identical R5 that **Verus verifies** — R4 is bounded by what vstd can
     express and R3 is bounded by nothing. The classes are **incomparable**.
     Measured on p16: the `chunks_exact(32)` fold is admissible as R3 at zero TCB
     and inadmissible as R4 at five new trusted items. The rest of item 2 stands
     — a spread still cannot carry a safety number — but it now stands on the
     measurement in item 1, not on a theorem. See `.memory/01-ladder.md`.

  **IMPLEMENTED at TASK_016 — and its advertised mechanism is FALSE, proved by
  experiment at TASK_016_REVIEW.** The key is required and hashed (`check.py`
  stage `0b`, +145 lines, 8 selftests, nothing semantic); all six patterns
  declare; all six gates green, `contract_sha256` moved in all six, invariant
  confirmed (**28/28 `md5_fn`, 564/564 `marginal_ir_per_call` cells unchanged**).
  Spelling-spread sections shipped for p05 (§13), p16 (§10), p17 (§10).

  **What it does not do.** `check.py`, `TASK_016.md` and this file all claimed
  *"changing a rung's idiom must move `contract_sha256`"*. It must not:
  `read_contract()` hashes `spec.md`'s fenced block and nothing else. The review
  forked p05, swapped `safe_tuned.rs` for the **forbidden** `chunks_exact`
  variant, and got **`PASS`, `complete_run: true`, `failures: []`, with
  `contract_sha256` byte-identical to the shipped one** — the gate certifying
  `R3 − R4 = −12/−58`, the retracted "safe beats unsafe", as green p05. The
  declaration was printed three lines above the PASS and changed nothing.

  **What it actually buys**, which is narrower and still worth having:
  *weakening the declaration* moves the hash, and the declaration is visible in
  the verdict. The rung sources are covered by `source_sha256`, not by this key.
  Nothing here prevents a forbidden respelling and nothing can without semantic
  checking, which the threat model forbids. **Say that, rather than the false
  mechanism sentence** — which this file itself carried until TASK_018. **Fixed at TASK_017**, which is the change that
  addresses the failure actually observed: `report.py` now prints the
  declaration — required, FORBIDDEN, why — **above every table** in
  `results/tables/*.md`, read from `spec.md` rather than the gate record, and
  `check.py` reprints the `forbidden` list beside any failures. The observed
  failure was a reader quoting a number without opening `spec.md`; this is the
  only mechanism that touches it.

  The manager's objection to putting the key in the contract block was
  separately **wrong**: `contract_sha256` has already moved 3× on p01 and 4× on
  p02, so "unchanged since TASK_013" was recency, not an invariant.

  **CLOSED at TASK_018, and not as TASK_017 left it.** TASK_017 read p16's
  `required[0]` as naming tokens and applied that standard to p16 while refusing
  it for p17 *in the same commit* — the blocker TASK_017_REVIEW found. TASK_018
  adopted the named-spelling standard **uniformly across all six**, labelled as a
  policy adopted after measuring, restored the disclosure TASK_017 had deleted,
  and then measured the consequence: p16 has **three** admissible respellings
  (two cheaper) and p17 **two** (both cheaper), so "the shipped R3 is the
  cheapest admissible spelling" is **FALSE, not unestablished**, in both. Neither
  cell was swapped; both `NOTES.md` now carry an in-contract spelling spread and
  state their published R3 figures as **one-sided bounds** — R3-side only, R4 held
  at the shipped cell. TASK_023 measured that "upper bound on the safety tax" is
  **false** for p16 as well as p05; p17, p02, p01 and p08 are *unverified* on the
  R4 side, not verified fixed. The adjudication that got
  there: p17's cheaper spelling is genuinely admissible under its
  declaration — but it also beats **its own R4** by 19.00, so swapping R3 alone
  would re-commit TASK_014/015's unmatched-pair defect *as a shipped cell*, and
  ~~`inf(R4) <= inf(R3)` means no swap ever terminates~~ (refuted above at
  TASK_025_REVIEW — the classes are incomparable, so the non-termination argument
  is void; the swap is still refused, on the unmatched-pair ground, which is the
  measured one). p16's case is **not even
  well-posed**: its hashed block contradicts itself, requiring `end - p >= 3`
  and `vlen > end - (p+3)` "in every rung" at `spec.md:289` while asserting at
  `:60` that `split_first_chunk::<3>()` — which contains **neither**
  comparison — is admissible. Disambiguate `required[0]` before deciding
  anything downstream of it.

  Declining to add a p16 restriction that would have excluded the cheaper
  spelling retroactively was **right**, and the reason generalises: **a
  `forbidden` entry chosen after seeing which spelling is cheaper is
  self-certification in its purest form.**

  **Superseded design notes (kept because the argument matters):**
  a declared canonical idiom per pattern, with two amendments that answer the
  self-certification objection — **move the declaration into the hashed
  `slb-contract` block** as a required `"idiom": {"required": [...],
  "forbidden": [...], "why": "..."}` key, so changing a rung's idiom must move
  `contract_sha256`; and require a **spelling-spread section** in every
  `NOTES.md`, published as a result about method and never as the headline.
  The gate checks presence and hashes it; it does not try to check semantically
  ("could this happen by accident?" says no).

  Retrofit: p05 and p17 already have the prose and need it moved; p01, p02, p08,
  p16 need a paragraph each. **No cell source changes, so no measured column can
  move** — but `contract_sha256` moves in all six, so all six gates re-run
  (~12–15 min of machine time).

  **The p05 R3 swap was specced and declined, and review confirmed the decision
  for a stronger reason than the four given: the replacement was out of
  contract.** p05's shipped `safe_tuned.rs` *is* the contract-conformant R3 and
  stays. Variants are in `.temp/p05r3/` and `.temp/review015/`; none is
  gate-ready.
- **`harness/check.py` stage 7 is structurally blind to `_chk`-rewritten
  `mem*`/`str*` misuse**, because it builds gcc-only at this box's fortify-3
  default and ASan's checks live in the interceptors, not in `__memcpy_chk`.
  Identified at T014, confirmed and *strengthened* at review (clang with
  `-D_FORTIFY_SOURCE=3` is blind too, so the discriminator is `_chk`, not the
  compiler). Fix is `-U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0` and/or a clang
  column. **p02 was checked and is not affected.** Not fixed; general, not
  p08-specific.
- **A gate row can record "sanitiser clean" for two opposite reasons** and the
  record cannot tell them apart. `results/gate/p08-overlap-move.json` shows
  `adversarial-overlap expect=clean fired=False exit=0` with empty
  `notes`/`blocked` — identical in shape to p17's genuinely-clean row, though
  p08's means "the tool cannot see this". **`build_models`** admits only
  `clean`/`fires` (`check.py:1433`). The reason survives only in `model.py`'s docstring.
  ⚠ **This one citation has now drifted TWICE** — `:566` until TASK_058,
  `:1247-1249` until TASK_066, where it pointed at an `idiom_problems` selftest.
  **Cite the function.**

- ~~**Miri is not installable**~~ — **closed at T005.** `nightly` +
  `cargo miri setup` alongside the pinned toolchain; R4 has no vstd dependency,
  and Miri checks source for UB rather than measuring codegen, so the toolchain
  difference is not a confound. `TOOLCHAIN.md` has the arrangement. The gate now
  runs it. Residual: a *big payload* is unchecked, because `n_iters` can be
  clamped from the file header and the payload cannot — p01's `large.bin` times
  out and is recorded as a blocked row.
- ~~**The barrier swap to multiply-shift is deferred**~~ — **closed at T005.**
  Swapped to `(acc * nwin) >> 64` in 128-bit arithmetic, p01 re-measured. Cost:
  three lines of ghost proof in R5 (`lemma_u128_shr_is_div` plus two
  `nonlinear_arith` steps) and the obligation count 5 → 7. R4's `-O3` driver loop
  went 18 → 13 instructions, because the high half of `mul` lands in `%rdx`,
  which is already the kernel's third argument register.
- **A width change applied to every rung at once is invisible to the driver
  diff.** `harness/dloop.py` must erase casts for the C/Rust reconciliation to
  work at all. Not fixed; recorded in `.memory/02-bench-rules.md`.
- **`results/gate/<pattern>.json` is the last complete run, pass or fail**, so a
  red run replaces a green record. Mitigated at T005 by hashing the contract
  block and every source into it, so a stale record is detectable. Whether the
  directory should be tracked at all is still open.
- **18 of 28 wall-clock cells exceed the 10% spread threshold** and are marked
  discarded. No claim rests on them. Fixing needs a quieter box.
- **Running the gate on a mirror writes into the tracked `results/gate/`.**
  `*.partial.json` is gitignored; full-run records are not. TASK_008 moved 11
  such files out by hand. A gate run whose pattern dir is outside `patterns/`
  should write its record under `.temp/`; not fixed.
- **`work_per_call` is unbounded.** Shrinking p02's 16× still passes the floor
  (margin 576.7×, shout only). See `.memory/02-bench-rules.md` for why bounding
  it mechanically is harder than it looks.
- **Nothing pins the `SLB-DRIVER` region to the *measured* code path — and this
  is the sixth demonstrated bypass of the driver diff.** Raised at
  TASK_008_REVIEW from reading; **built and confirmed at TASK_009.** Move
  `safe_naive.rs`'s markers into a dead `fn slb_decoy` whose body is the
  canonical loop, leave the real loop in `main` unmarked, and put
  `_mm_prefetch` in it: **full gate PASS, `complete_run: true`, 0 failures**,
  with stage 6 reporting *"5 driver loops … all normalise to the pinned
  13-statement token sequence"* — one of them from a function that never runs.
  The payload is live (`prefetcht0` in both O3 and O0 disassembly, 0 in the
  control; marginal Ir/call O0 6838 → 6852). Confirmed at TASK_009_REVIEW to work
  against the **C** rung too, so it was one mechanism, not two.
  **Closed at TASK_010, both ways**: the kernel must be called exactly once per
  rung source and that call must be inside the region (structural), *and* the
  region's enclosing function must have non-zero exclusive `Ir` and be the
  kernel's only caller, read from the callgrind profiles stage 3b already writes
  (dynamic). See `.memory/02-bench-rules.md`.
- **p17's `spec.md` `obligations_note` is arithmetically wrong** (found at
  TASK_013). It says `main` = body + driver loop + one per `by`-block, which
  predicts 6 for its four `by`-blocks; the measured value is 5, and p05's
  character-identical driver also measures 5. The note already says the
  rule-of-thumb gives 7 and is not the derivation, so it is internally
  inconsistent. Fix is one JSON string, **but it is inside the hashed contract
  block**, so it needs a `check.py p17` re-run to refresh the gate record. Folded
  into the next engineer task's Part 0; not urgent, nothing rests on it.
- **p05's `inputs/` holds 144 sweep `.bin`, ~189 MB.** Gitignored and regenerable
  by `gen.py --sweep`; left in place because `rm` outside `.temp/` stalls on
  review. Delete by hand if the box gets tight (`df -h /`).
- **`measure.py` cannot record the commit it will be committed in**, so a fresh
  results JSON always names HEAD~1 with `dirty_files` set. Structural; say so in
  the schema rather than chasing it.
- ~~**`measure.py p02` has not been re-run since TASK_005**~~ — **closed at
  TASK_011**, in the order TASK_008_REVIEW prescribed: once, with p16's
  `common/head1_u64_bytes` already in place. `binary_text_bytes` moved in 10 of
  32 cells, all C (see `.memory/03-measurement.md` for why the asymmetry is
  structural, not noise); kernel columns and every Rust `md5_fn` unchanged. The
  §3a "with `memcpy`" row was re-quoted from the new run. Residual: the "with the
  byte loop" column is a hand-built variant `measure.py` structurally cannot
  supply, because its `Ir` is kernel-exclusive and excludes libc `memcpy`.
- **`perf_event_paranoid = 3`** — no hardware counters without root. This is the
  only way to explain *why* gcc's shorter loop runs 43% slower. **Owed by the
  user**; nothing works around it.
- **Proof-effort budget per R5 cell — set by the manager at TASK_008, pending a
  user override.** The budget is **one engineer session per R5 cell**. If the
  proof has not converged by the end of it, the engineer stops and reports the
  exact Verus error, the obligation it could not discharge, and what it tried.
  That report *is* the deliverable for that row — `.memory/02-bench-rules.md`
  already says a documented R5 failure is a finding, not a gap. Rationale: the
  alternative is an open-ended stall on p28/p30, which the catalogue already
  expects to defeat R5, and a stuck proof is most informative *early*. Raise the
  budget for a specific pattern when the sticking point looks like the finding.

## Family A — buffers & bounds (spatial safety core)

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p01 | array reduce / prefix scan | none (calibration) | trivial | **done** (T002/T003/T005), gate green, R5 == R4 byte-identical at O3 |
| p02 | length-prefixed buffer copy (`memcpy` w/ attacker length) | spatial OOB write | easy | **done** (T004), reviewed (perf headline refuted at T006), re-measured T011; gate `PASS`, R5 == R4 `exact` at O3 / `norel` at O0; **the project's strongest security result** — idiomatic C prints a plausible answer and exits 0 in 7 of 8 builds on a one-byte overflow, the 8th aborting only on this box's `_FORTIFY_SOURCE 3` default |
| p03 | bounded stack over an attacker-chosen opcode stream | index underflow on empty pop — `sp−1` at 0 wraps to `stack−1`, **inside the kernel's own frame** | easy | **done** (T036), gate `PASS` first complete run, R5 **9/0 first run**, R4 == R5 `exact`, **reviewed** (T036_REVIEW). First kernel whose *control flow* is attacker-chosen; first whose safety law is per *executed* operation; **and the first pattern with an admissible R4 that MOVES**, retiring "nobody has, on any pattern" |
| p04 | ring buffer with wraparound | **a wrap that stays IN BOUNDS** — drop the fullness check and a push overwrites the oldest element; every index still `< CAP`, no OOB access, and **both** guards are invisible to a memory-safety proof | moderate | **done** (T042), gate `PASS` complete run, R5 **9/0 first try**, R4 == R5 `exact`, **reviewed** (T042_REVIEW: headline confirmed by a stronger test than was asked for, its stated mechanism refuted; 1 blocker + 3 majors, corrections at T044). Third operator in the bound-propagation series (multiply → shift → **modulus**) |
| p05 | 2-D index flattening / matmul (`i*n+j`) | dimensions trusted vs buffer; overflow in the check | moderate | **done** (T013), gate PASS first run, R5 == R4 `exact` at O3; safety moves from per-element to **per-row**, and gets *worse* with wider lanes |
| p06 | in-place rotate (three reverses) over a fixed `[u8; 64]` scratch | **an unreduced attacker rotate amount** — the omitted `r %= m`. ⚠ The catalogue's guess, *"aliasing, permutation invariant"*, was **not** the bug that got built: aliasing turned out to be an expressiveness/TCB story, and the permutation invariant is why the fold must be **order-sensitive** (three reverses compose to a permutation, so a sum- or xor-fold cannot see the bug) | moderate | **done** (T047), gate `PASS` first complete run, R5 **17/0 first attempt** (twin 22/0, then 18/0 & 23/0 after T048), `R4 ≡ R5 exact` at O3 / `norel` at O0, **reviewed** (T047_REVIEW: 2 blockers + 3 majors + 5 minors, **14 clean negatives**, headline confirmed by a layout population the review built itself; corrections at T048). **The first safety line that is a division rather than a compare-and-branch, and the first pattern where the `Ir` column is SIGN-WRONG** — clang's hardened rung executes 45–108 *fewer* instructions and takes 10–20% *longer* |
| p07 | binary search | **unsigned underflow of an inclusive upper bound** (`hi = mid − 1` at `mid == 0`, reached by any key below `elements[0]` — on *well-formed* input) + **32-bit overflow of the length check** `4·n + 4·nq`, fooled at an 88-byte window. ~~midpoint overflow~~ — see below | moderate | **done** (T026), **reviewed** (T026_REVIEW: headline confirmed, 2 majors + 5 minors against the prose); gate `PASS` first complete run, R5 10/0 first try, R5 == R4 `exact` at O3; **the first pattern where R3's tax has no axis along which it amortises** — `6.0000` Ir/probe, fraction rising in both `n` and `nq`, confirmed across six workloads |
| p08 | memmove with overlapping regions | overlap UB | moderate | **done** (T014), reviewed; gate PASS first run, R4 == R5 `exact` at **both** O0 and O3; the UB **executes and is unobservable** (glibc `memcpy` *is* `memmove`), so p08 is a tooling-and-expressiveness result, not a performance one |
| p09 | bit vector / bitset ops (test + popcount) | **two bugs**: the omitted `q < nbits` guard (spatial, caught everywhere) and `q & 31` (**invisible to a memory-safety proof, and invisible entirely once the spec moves with it**) | easy–moderate | **done** (T038), gate `PASS` first complete run, R5 18/0, R4 == R5 `exact`, **reviewed** (T038_REVIEW: invisibility confirmed against four vacuity attacks; 1 blocker + 5 majors against the prose, two of them project-wide). First kernel whose guard is not a bounds check; first where **R3 is dearer than R2**; first trusted item modelling a **CPU instruction** |
| p10 | **weighted FIR / sliding-window stencil** (delivered as `p10-fir-stencil`) | **off-by-one at the boundary — ✅ the catalogue's guess UPHELD, the second row in six settled to survive its own guess** (T057 §0, five alternatives rejected — **on argument, not measurement**, and the manager's task file wrongly said four and said measured). `last > len` where the hardened rung writes `last >= len`: **one character**, one byte of overread, conditional on attacker data | moderate | **done** (T057), gate `PASS` first complete run, R5 **10/0** (twin 11/0), `R4 ≡ R5` `exact` at O3 / `norel` at O0, **TCB 3, no `assume`**, **reviewed** (T057_REVIEW: 1 blocker + 5 majors + 5 minors, **21 clean negatives**; corrections at T059). **The first kernel with more than one indexed read per iteration**, and the pattern whose headline was wrong in the FLATTERING direction: published as *"safe Rust cheaper than unsafe"* and corrected to an **index-expression** result — 60% of the margin was R4 spelling, the rest is induction-variable bookkeeping, and `c-clang` with the same index expression is dearer than both Rust rungs. Safety's own cost is **0.00 `Ir` per vectorised tap / +3.00 per scalar-epilogue tap** |

**p07's bug class was WRONG in this table for the whole life of the project**
(TASK_026), and the correction is **CONFIRMED** (TASK_026_REVIEW — it is one of
that review's two confirmed extras; the row's bug column above already carries
it). "Midpoint overflow
`(lo+hi)/2`" is not merely hard to reach, it is unreachable **by a factor of
2.1e9 for any input p07's wire format can express** — and the binding constraint
is not RAM, which is what the manager guessed, but the **`u32` header field**:
`n ≤ 2³²−2` ⇒ `lo+hi ≤ 8 589 934 588 ≪ 2⁶⁴`. Measured thresholds by index type:
`uint32_t` needs 8 GiB of `u32` elements, `int` (the JDK bug) 4 GiB, `size_t`
3.7e19 B.
**The overflow that IS reachable sits in the other multiplication**: the length
check `4·n + 4·nq` needs 36 bits, so a 32-bit check is fooled at a window of
**88 bytes** — and it ships as `adversarial-width.bin`, on which the 32-bit-check
cells SIGSEGV. The second bug, the one that fires on well-formed input, is
**unsigned underflow of an inclusive upper bound** (`hi = mid − 1` at `mid == 0`,
reached by any key below `elements[0]`). The argument and the arithmetic are
`p07/NOTES.md` §0.

**The lesson generalises past p07 and is why this paragraph stays:** a catalogue
bug class is a *guess written before the pattern was built*, and it survived
unchallenged until an engineer measured it. **Every remaining `planned` row's bug
column is that same kind of guess.** Check it against the wire format before
building on it — p07's was wrong by a factor of 2.1e9, and the binding constraint
was not the one the manager named.

⚠ **Three consecutive patterns have now overturned their own catalogue row**
(p07, p06, p14), and p14's task made settling the bug class its **first
deliverable** rather than an afterthought. **Do that on every remaining pattern.**
p14 rejected all four candidates it was handed — the manager's three plus the
catalogue's — and shipped a fifth.

⚠ **And do NOT record that in-place mutation is "excluded by the harness".** That
claim was p14's §0 headline, it is **false**, and it is not in this file only
because rule 9 held the write until the review landed. **Nothing in `harness/`
enforces purity**; `check.py` compares against `model.py`'s own simulation. What
actually happens is that the driver's repeat protocol drives a payload-mutating
kernel into a **one-call steady state** (`mutate` = 9044.0000 `Ir`/call, zero
residual, against `cap` 9779.0180), and after call 1 every delimiter is already
NUL — **so it measures an already-tokenised buffer, a different workload from the
one the pattern names.** Two repairs exist: simulate the mutation in `model.py`,
or declare the steady state. **An in-place tokenizer is still buildable here.**

## Family B — strings & NUL-termination

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p11 | NUL-terminated string scan (`strlen`-shaped) | missing terminator → OOB read; **the loop simply does not stop** | moderate | **done** (T033), gate `PASS` first complete run, R5 12/0, R4 == R5 `exact`, **reviewed** (T033_REVIEW: headline confirmed by independent re-measurement; 2 majors + 6 minors, no blockers). Family B's first pattern; first kernel whose loop bound is not known before the loop, and first where C's rung calls a SIMD libc routine |
| p12 | `strcat` into a fixed stack buffer | classic stack overflow — **and the failure mode depends on the overflow MAGNITUDE and the compiler**: +1…+8 B silent and wrong on both, +16…+48 B gcc canary / clang corrupts `main`'s locals, +64…+128 B gcc canary / clang SIGSEGV | moderate | **done** (T040), gate `PASS` first complete run, R5 15/0, R4 == R5 `exact`, **reviewed** (T040_REVIEW: headline confirmed and sharpened; 2 blockers + 3 majors, both blockers landed at T041 — the structural claim was too strong and `−26.00` is a fixed-R4 figure). First bug here that is a **WRITE** safe Rust cannot express; first time `c-gcc` and `c-clang` differ in **behaviour** |
| p13 | `strncpy`/`snprintf` truncation semantics | **the first bug here that is a CORRECTLY-CALLED library function** — `strncpy(dst, src, sizeof dst)` is textbook C and still does not terminate on truncation; and **the harm lands at a different site from the bug** (memory-safe truncation at the copy, OOB read later in the consumer) | moderate | **done** (T043), gate `PASS`, R5 **17/0 first attempt** (twin 20/0), R4 == R5 `exact`, **reviewed** (T045_REVIEW: 3 blockers + 6 majors — headline sign survives, magnitude and stated mechanism do not; corrections at T046). First pattern whose rungs call **different libc routines**, and the only one where the optimiser reintroduces a `forbidden` spelling |
| p14 | **field split into a fixed descriptor table** (delivered as `p14-field-split`, not as a `strtok`-style in-place tokenizer) | **an unbounded FIELD COUNT against a fixed descriptor table** — the first bound here that is a **count of a byte value** rather than a length. ⚠ The guessed class *"in-place mutation + aliasing"* was **rejected by measurement** (T049 §0) — see below | hard | **done** (T049), gate `PASS` first complete run, R5 **19/0** (twin 23/0), `R4 ≡ R5 exact` at O3 / `norel` at O0, Miri 8/8, TCB 6 items = **4 U-license + 2 infra** (first use of the T048 classification on a new pattern), **reviewed** (T049_REVIEW: 2 blockers + 3 majors + 4 minors, **17 clean negatives**; corrections at T050). Its `strtok`/`strsep` delimiter-run split is the **trigger**, not the bug |
| p15 | UTF-8 validation + decode | malformed continuation bytes | moderate–hard | planned |

## Family C — parsing & protocol decoding

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p16 | TLV / length-prefixed record walker | length field vs remaining buffer | easy–moderate | **done** (T007), reviewed; gate PASS first run, R5 == R4 `exact` at O3; **first O(n) cost of a *spelling* — R3 is still 0/byte** |
| p17 | HTTP `Range:` style header parser | int overflow → OOB (cf. CVE-2017-7529) | moderate | **done** (T011), reviewed; gate PASS first run, R5 == R4 `exact` at O3; **memory-safe but functionally wrong**; the *leaking* slice-guard variant reproduced at T012 (`.temp/` artefact + committed generator — see `.memory/05-layout.md` item 11 for why it cannot live in the pattern dir) |
| p18 | varint / LEB128 decoder | **unbounded shift** — ✅ **the catalogue's guess UPHELD, the first row in five patterns to survive its own guess** (T049 §0, four alternatives rejected with measurements). **The first bug here that is UB but NOT a memory-safety bug**: it touches no memory and **ASan is silent** | easy–moderate | **done** (T051), gate `PASS` first complete run, R5 **12/0** (twin 13/0), `R4 ≡ R5 exact`, Miri 9/9, **TCB 3, no `assume`**, **reviewed** (T051_REVIEW: 1 blocker + 7 majors + 5 minors, **15 clean negatives**; corrections at T052). **Four catchers — UBSan, `debug-assertions`, Miri, Verus — all outside the 24-cell matrix**, and Miri catches it as a **panic**, not a `ub` report |
| p19 | protocol state machine (byte-at-a-time) | state confusion | moderate | planned |
| p20 | length/offset pair validation (heartbeat-style) | trusted length field (cf. CVE-2014-0160) | moderate | planned |
| p21 | CSV/field splitter with escapes | quote-state off-by-one | moderate | planned |

## Family D — data structures, array-backed

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p22 | open-addressing hash table (linear probe) | capacity mask, probe termination | moderate–hard | planned |
| p23 | in-place quicksort partition | aliasing, permutation invariant | hard | planned |
| p24 | binary heap (sift up/down) | parent/child index arithmetic | moderate–hard | planned |
| p25 | dynamic array with `realloc` growth | growth overflow, stale pointer | moderate–hard | planned |
| p26 | run-length encode/decode | expansion overflow on decode | moderate | planned |

## Family E — data structures, pointer-backed (Verus stress tests)

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p27 | **handle table over per-record `malloc`/`free`** (delivered as `p27-handle-table`; the *singly linked list* SHAPE is retracted -- where `next` sits decides observability and that is a glibc detail, and the bug would fire on **every** input, which the adversarial-only constraint forbids) | **use-after-free -- the class UPHELD, and the project's FIRST TEMPORAL bug.** R1 omits one conjunct (`&& live[h] == 1`) on the READ path | hard (`vstd::raw_ptr`) | **done** (T060), gate `PASS` first complete run, R5 **15/0 first run** with a functional postcondition (twin 20/0), `R4 == R5` `exact` at O3 / `norel` at O0, **TCB 7 (forced -- see below)**, **reviewed** (T060_REVIEW: **no blocker**, 3 majors, 8 minors, **28 clean negatives**; corrections at T061). **Not one instruction of `R3 - R4` is the lifetime guarantee** -- a closed decomposition over *every* function gives `230.07 = 109.65 kernel + 120.42 drop glue + 0.00 allocator`, and an R4 keeping R3's bounds checks costs **+153.51**, so safe Rust pays **43.86 LESS** of the spatial tax. The lifetime guarantee itself costs **zero**, and its shape is structural: **the free and the invalidation are one operation in safe Rust and two in C, and the bug is the third -- the ASKING -- going missing** |
| p28 | intrusive doubly linked list | aliasing, ownership | research-grade | planned |
| p29 | binary search tree insert/lookup | recursive ownership | hard | planned |
| p30 | chained hash table (buckets of lists) | combines p22 + p27 | research-grade | planned |

Expect p28/p30 to defeat R5 within budget. **Document where the proof got stuck —
that is the deliverable for these rows**, not a green checkmark.

## Family F — memory management

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p31 | bump / arena allocator | alignment, exhaustion, provenance | hard | planned |
| p32 | free-list allocator | double free, corruption | research-grade | planned |
| p33 | object pool with recycling | use-after-recycle | hard | planned |
| p34 | reference counting | leak, premature free | hard | planned |

## Family G — systems idioms & representation

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p35 | tagged union / discriminated dispatch | tag-payload mismatch | moderate | planned |
| p36 | function-pointer table dispatch (vtable-like) | index out of table | moderate | planned |
| p37 | callback with `void*` userdata | type confusion | moderate–hard | planned |
| p38 | **record parser that clamps a length in place and re-reads it through a pun** (delivered as `p38-alias-pun`). ⚠ **The catalogue's own spelling — *"endian conversion, `memcpy` vs union"* on a byte buffer — is the BENIGN aliasing direction and was retracted before the build**: neither compiler exploits it, 8 of 8 cells. Only two incompatible **non-char** types move | **strict-aliasing UB — the class UPHELD** (unusual: three of the previous five were overturned), and the harm is a **MISCOMPILE**, not a wrong answer | moderate | **done** (T066), gate `PASS` first complete run, R5 **13/0** (twin 16/0), `R4 ≡ R5` `exact` at O3 / `norel` at O0, TCB 5, Miri 8/8, **reviewed** (T066_REVIEW: **no blocker**, 3 majors, 8 minors, **35 clean negatives**; corrections at T067, which refuted three of the *review's* own numbers). **Ships labelled a DEMONSTRATION KERNEL** — the harm needs four conjunctive conditions and **six neighbouring one-line spellings each remove it**. ⚠ **The quotable result is the price: on gcc the undefined spelling is the DEAREST of the six, and every fix saves exactly 6.00 `Ir`/call.** **The first bug class here that unsafe Rust does not reintroduce** — Rust has no type-based aliasing rule at any rung. Also the project's **first additivity-extrapolation failure**, which turned out **100% attributable** to three missing columns, none of them the one named |
| p39 | bitfield pack/unpack into wire format | shift/mask off-by-one | moderate | planned |
| p40 | struct-of-arrays vs array-of-structs traversal | none — pure perf axis | easy | planned |
| p41 | flexible array member struct | size computation overflow | moderate–hard | planned |
| p42 | `goto cleanup` error handling | leak on error path | moderate | planned |

## Family H — numeric & crypto-adjacent

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p43 | checksum / CRC over untrusted length | loop bound from input | easy | planned |
| p44 | fixed-point arithmetic | overflow, rounding | moderate | planned |
| p45 | saturating / wrapping arithmetic helpers | signed overflow UB | easy–moderate | planned |
| p46 | bignum limb add/mul (schoolbook) | carry propagation, limb bounds | hard | planned |
| p47 | constant-time compare / select | **timing side channel.** ⚠ **The catalogue's guess -- *"compiler may reintroduce a branch"* -- is REFUTED** (T064 + T064_REVIEW: 5 accumulate spellings, gcc 13.3 and clang 22.1 at five opt levels, rustc at five, **LTO, PGO trained 100% on mismatch-at-byte-0, AVX2, AVX-512, `__builtin_expect` in three placements, a branching caller** -- `Ir(k=0) - Ir(k=n-1) = 0` **exactly**, with a detector control that fires). **The adversary is the IDIOM, not the optimiser**; the leaking rung is safe Rust's own `a == b` | moderate | **done** (T064), gate `PASS` first complete run, R5 **12/0 first run, no lemma** (twin 13/0), `R4 == R5` `exact` at O3 / `norel` at O0, **TCB 3**, Miri 7/7, additivity extrapolation **80/80 exact**, **reviewed** (T064_REVIEW: 3 majors, 6 minors, **32 clean negatives**; corrections at T065). **The proof certifies a LEAKING kernel**: `m_leak` verifies 14/0 with `kernel`'s obligation count unchanged at 3 and leaks **+7088 `Ir`**, under an **identical contract** -- a property of the TRACE is invisible to a logic about the VALUE |

| p48 | **partially-filled buffer / struct with padding, written out wholesale** | **uninitialised-memory INFO LEAK** — in bounds, live, owned, never written | moderate | **proposed at TASK_066 (manager), UNREVIEWED** — see the triage below |

⚠ **`p48` is NEW and it makes this a 48-row catalogue.** `CLAUDE.md` describes
`.memory/06-catalogue.md` as *"the 47-pattern catalogue"*; that phrase is now one
short. Numbers `p01`–`p47` are all used with **no gaps** (checked), so a seventh
axis cannot reuse one.

### p48 — the seventh axis, and why the manager is proposing it against the slate

**This is a manager proposal written while p38's engineer was running, from
source reads and `vstd` greps only — no compile, no measurement.** ⚠ **The
catalogue's own record on bug-class guesses is three overturned against two
upheld, and p47 overturned its own row.** Treat this the same way: a prior.

**Why it is not one of the six.** The harm is an **information leak of heap
residue**: every access is *in bounds* (not spatial), the allocation is *live and
owned* (not temporal), and the leak is in the *value*, not the trace (not
timing). p17 leaks by returning the wrong in-bounds slice and p47 leaks by
timing; **neither leaks memory that was simply never written.**

**The ladder story, and it is unusually sharp:**

- **R1 (C)** — `malloc` a record, fill some fields, write the whole record out.
  Utterly ordinary C. ⚠ **And the killer sub-case is PADDING**: initialise every
  field of a `struct` and the padding bytes are *still* uninitialised, so the
  obvious fix does not work and only a whole-object `memset` does. That is the
  real CVE shape (kernel `copy_to_user` infoleaks).
- **R2/R3 (safe Rust)** — **cannot express it.** `Vec::with_capacity(n)` has
  `len 0`; reaching the residue needs `set_len`, which is `unsafe`. So the safe
  answer is **total**, like p08 — and unlike p08, the C bug is not exotic.
- **R4 (unsafe Rust)** — `MaybeUninit` + `assume_init` reintroduces it exactly.
- **R5 (Verus)** — ✅ **the prover WINS here, and this is the load-bearing
  check, already done.** The pinned `~/tools/verus/vstd/raw_ptr.rs` has
  `ghost enum MemContents<T> { Init(T), Uninit }` (`:162-164`),
  `PointsTo::is_init()` (`:250`), `leak_contents` (`:284`) — and **both readers
  require initialisation**: `ptr_mut_read` (`:602-605`) and `ptr_ref`
  (`:620-623`) each carry `requires ... is_init()`. `layout.rs:375-382` supplies
  the `MaybeUninit<T>` size/align axioms. **p27 already ships `vstd::raw_ptr`
  code**, so this is not new machinery for the project.

> ⚠ **The manager first wrote here that this is "the first axis where R5 WINS"
> and that is FALSE — self-caught before review.** **p27's R5 already catches
> its use-after-free**, as an ordinary `precondition not satisfied`
> (`patterns/p27-handle-table/NOTES.md:1421-1447`). p48 is not the first
> non-null R5 and must not be sold as one.
>
> **What is actually distinctive is the KIND of obligation.** p27's precondition
> is about **ownership** — do you hold the permission at all? `is_init` is about
> the **contents of memory you already own and are entitled to touch**. No
> pattern in the tree exercises that, and it is the obligation the C bug walks
> straight through. Alongside p09 (the proof cannot *see* the bug) and p47 (the
> proof cannot *state* the property), that gives a three-way contrast worth
> having — but the contrast is the shape of the obligation, **not** a first.

**Harness feasibility — mostly already answered**, by the same source read that
re-triaged p36 (above):

- The leak's observable is **non-deterministic** (whatever residue the allocator
  hands back). `check_checksums` (stage 2) runs on **non-adversarial inputs
  only**, and stage 7 tolerates a non-deterministic exit under
  `sanitizer_expect: "fires"`. **So a non-deterministic adversarial row is
  already legal** — this is exactly p36's re-triage, reused.
- ⚠ **The residue must be RELIABLY non-zero, or the pattern shows nothing.**
  Fresh `mmap` pages are zero-filled by the kernel, so a first-touch `malloc`
  leaks zeros and the harm is invisible. **The kernel must therefore allocate,
  fill, free, and re-allocate** — which is p27's shape, and p27 already paid for
  the knowledge: `.memory/03-measurement.md:807-833` establishes that a freed
  chunk's **first 16 bytes are glibc tcache metadata** and that reading past them
  is deterministic run-to-run, **but varies across `-O` LEVEL** (dead-store
  elimination changes what was stored before the free), which puts two values in
  one matrix.

  > ✅ **That variation is designed around, and cheaply.** Do not read raw
  > residue. **Have the program write a KNOWN SENTINEL into record A, free it,
  > allocate record B, fill B only partially, and emit B** — then the harm is
  > *"A's sentinel appears in B's output"*, which is program-controlled and
  > therefore deterministic across allocator state **and** opt level. It sidesteps
  > the DSE problem that the offset-16 rule only half-solved.
  > ⚠ **One hazard to check first**: the store of the sentinel into A must not
  > itself be dead. A must be genuinely read before the free, or DSE removes the
  > very thing the pattern detects. **Settle reproducibility FIRST**, the way
  > TASK_055 had to — but the route is known, which is why this reads *moderate*
  > and not *hard*.
- **Catcher: MSan (`-fsanitize=memory`)** — a third sanitizer this project has
  never used, and valgrind's `--track-origins=yes` is a second. ⚠ **MSan
  requires every dependency be instrumented** and is clang-only.
  **UNVERIFIED — availability needs a compile probe**, deferred because an
  engineer was running. TySan turned out to be present when the catalogue
  assumed nothing; do not assume either way.

**Where it sits on the slate.** The manager would build it **before p36** and
argue it against p22, on the grounds that it is the only remaining axis with a
*positive* R5 result and the only one whose safe-Rust answer is total. ⚠ **This
is a recommendation from the agent that also wrote the slate it is displacing —
PROTOCOL rule 3. A different agent should attack it before it is scheduled.**

p47 is special: the "security" axis is timing, not memory safety, and the threat is
the *optimiser*. Worth doing precisely because it inverts the usual story.

**Feasibility, settled before scheduling it — and it comes out BETTER than for
most patterns, not worse.** The obvious objection is that this box cannot measure
timing: `perf_event_paranoid = 3` means **no hardware counters**
(`.memory/00-environment.md`), and the wall-clock noise floor is wide enough that
two published `ns` rows are withdrawn and p06's own layout floor is **±4.6%**. A
timing pattern measured in wall clock here would be unpublishable.

**It does not need wall clock.** The leak is a *data-dependent instruction
count*, and this project's primary metric is a **deterministic** one:

- **`Ir` as a function of the input IS the side channel**, exactly and with zero
  noise. An early-exit compare executes fewer instructions when the mismatch is
  at byte 0 than at byte 31; a constant-time accumulate executes the same number
  for both. So the finding is *"`Ir(mismatch at k)` is constant in `k`"* versus
  *"it is linear in `k`"* — a slope, measured by callgrind, reproducible to the
  instruction. **No other pattern here has a metric that is literally the harm.**
- **"Did the optimiser reintroduce a branch" is a STATIC question**, and
  `harness/asm.py` answers it exactly. That is the pattern's other half and it
  costs no measurement at all.
- **Verus is the punchline, not a gap**: R5 can prove the comparison *correct*
  and has no vocabulary for the timing property, so the ladder's top rung
  certifies a leaking kernel. That mirrors p17 (*provably memory-safe and still
  leaking*) one level up, and it is a **clean negative that the project can state
  precisely** rather than a stall.

⚠ **Two hazards to settle in its `§0`, both from things already measured here.**
(1) `Ir` is not time — callgrind **prices a hardware `div` at 1 `Ir`**
(`.memory/03-measurement.md:434`) and **counts a `rep`-string instruction once
per repetition** (`:411`), so a `memcmp` lowered to `repe cmpsb` and one lowered
to a SIMD loop are not comparable in this metric. Name the routine
(`.memory/03-measurement.md:551`) and check the lowering before reading the
slope. (2) The constant-time rung must survive the optimiser *in the shipped
build*, not in a probe — that is the whole pattern, and it is exactly the
`forbidden`-spelling-reintroduced-by-the-optimiser problem p13 already hit, where
**a text pin binds the source and not the object**.

## Sequencing

Depth-first, template-first. Do not start a wave until the previous one's patterns
are green in `harness/check.py`.

**Wave 1 is complete and green** (p01, p02, p16, p17). Wave 2 is open.

**Order within a wave is now chosen by which axis is untested, not by number.**
p05 was taken first because every fold measured so far — p16's and p17's alike —
is a *serial Horner chain*, so the safe-vs-unsafe gap has only ever been measured
on a scalar loop on both sides. p16 quantified a bounds check blocking a 4×
unroll (2.25 of 4.25 Ir/byte); nothing has yet measured one blocking
**vectorisation**, which is a far wider lane. That is the largest untested claim
in the programme. Pick the next pattern the same way: **what would change a
conclusion?**

High-value out-of-order candidates noted for later:
- **p08** (overlapping `memmove`) — safe Rust *cannot express* the bug; the
  borrow checker rejects it at compile time. A structural Rust win to set against
  p17's structural Rust loss. Awkward for the ladder (R2/R3 must use
  `copy_within`, a different algorithm) — design carefully.
  **Done at T014.** Both claims in this entry's original wording were **wrong**
  and are corrected here so nobody inherits them: *"overlap UB is not caught by
  ASan"* — it **is**, by the `memcpy-param-overlap` interceptor, unless the call
  site was fortified to `__memcpy_chk`, which blinds ASan under **clang as well
  as gcc** (`.memory/00-environment.md`); and *"the different algorithm is a flaw
  to design around"* — it is the finding.
- **p47** (constant-time compare) — the adversary is the *optimiser*, a third
  security axis after spatial safety and functional correctness. Likely defeats
  R5 in an interesting way: Verus cannot state a timing property at all.

- **Wave 1** (template + core): p01, p02, p16, p17 — establishes the pattern
  template, the adversarial-input protocol, and one real-CVE mirror.
- **Wave 2** (bounds breadth): p03–p10.
- **Wave 3** (strings + parsing): p11–p15, p18–p21.
- **Wave 4** (array structures): p22–p26, p43–p45.
- **Wave 5** (representation/idioms): p35–p42.
- **Wave 6** (pointers, the hard wall): p27–p34, p46, p47.
- **Wave 7**: cross-pattern analysis and writeup.

## ⚠ The waves order by FAMILY, and after 16 patterns that is the wrong axis

**Manager decision, 2026-08-21, recorded with its argument so it can be
attacked.** The wave list above is a *pre-project* grouping by topic. It is still
a fine map of the territory and nothing below retires it — but it is no longer a
good work order, for a reason that only became visible once 16 patterns existed:

**Ten of the sixteen are bounds bugs.** p02, p03, p05, p07, p11, p12, p13, p14,
p16 and p17 all resolve to *"an index or length is not checked against a
buffer"*. They differ in the mechanism that makes the check cheap or dear, and
that was worth measuring ten times — findings 3, 9, 12 and p13's sign reversal
all came out of it. **It is not obviously worth measuring an eleventh time.**
(p10 is in flight and its bug class is unsettled by design — its §0 decides it,
and four catalogue guesses have been overturned, so it is deliberately not
counted here either way.) Waves 2–4 are largely more of it: p43 (CRC over an untrusted length) is
p16's shape, p21 (CSV with escapes) is p14's, p24 (heap sift index arithmetic) is
p04's, p26 (RLE expansion) is p12/p13's.

**What the tree does not have is AXES, and they are almost all in waves 5 and 6
— i.e. last.** The missing ones, with the pattern that opens each. ⚠ **This said
"six" and listed six; a SEVENTH was found at TASK_066 and it was not in the
catalogue at all** — see the `p48` row and its triage below.

| missing axis | why nothing here covers it | opens with |
|---|---|---|
| **temporal / lifetime** | every bug here is spatial or logical. This is the one class safe Rust rejects at *compile* time. ⚠ The *"R5 catches it by linearity, not SMT"* claim that used to sit here is **RETRACTED** — it was an artefact of a two-element probe; with a real permission map it is an ordinary `precondition not satisfied` (TASK_055_REVIEW) | **p27 / p33** |
| **timing side channel** | the adversary is the **optimiser**, and **Verus cannot state the property at all** — the first security property the whole ladder is blind to | **p47** |
| **UB the optimiser WEAPONISES** | p18's UB is masked by hardware (`shl` truncates the count) and the program limps on. Strict-aliasing UB is the opposite: the compiler *deletes code* on the strength of it | **p38** |
| **control-flow integrity** | every harm here is data. An out-of-table indirect call is a different harm class, and R1h has a real answer (`-fsanitize=cfi`) that no pattern has priced | **p36** |
| **termination as the obligation** | every R5 so far proves *safety*. None proves the loop **ends** — and an open-addressing probe that never terminates is a real, shipped C bug | **p22** |
| **provenance** | the property Miri checks and nothing else does; untested here | **p31** |
| **INITIALISATION** ⚠ *new at TASK_066, and it was uncatalogued* | every harm here is out-of-bounds, out-of-lifetime, or a trace. **Reading memory that is in bounds, live, owned — and never written** is none of those. The Verus obligation is a **new KIND** — not "do you own this?" (p27) but "is what you own INITIALISED?": `vstd::raw_ptr`'s `ptr_ref`/`ptr_mut_read` both `requires perm.is_init()`. ⚠ **Not** the first non-null R5; p27 is | **p48** (proposed) |

**Recommended order after p10**, by marginal finding value rather than family:

1. **p27 or p33** (lifetime) — **blocked on `TASK_055_REVIEW`**, and on the TCB
   decision that review is asked to attack. Biggest single gap.
2. **p47** (constant-time compare) — orthogonal to everything, `moderate`, and
   the R5 story writes itself: the prover has nothing to say. Mirrors p17
   (*provably memory-safe and still leaking*) one level up.
3. **p38** (type punning) — cheap, and it pairs with p18 as the second half of
   *"what UB actually does"*.
4. **p22** (hash probe) — ⚠ **"the first termination obligation" was FALSE and
   is retracted** (TASK_070_REVIEW). **73 exec-loop `decreases` measures already
   existed across the tree**, because **Verus demands one on every exec loop by
   default**. The true claim is narrower and was counted: p22 carries the tree's
   **only exec-loop measure not expressible in the loop's own exec variables**
   (`i0 as int + d - u`, where `i` wraps and appears nowhere in it) — 1 of 73.
5. **p36** (vtable dispatch) — first non-data harm.

### Feasibility triage for that slate — done before scheduling, not after

p47's is above. The other four, each with the thing most likely to kill it. **None
of these is a measurement; they are the questions each `§0` must answer first.**

- **p38 (type punning) — cheapest on the list, and the risk is a NULL result.**
  The Rust side is a gift: safe Rust has no strict-aliasing UB to have, and
  `u32::from_ne_bytes` is the punning idiom, so the expected result is *"C's UB
  idiom and its defined replacement compile to the same thing"* — measurable
  exactly in `Ir` and in `asm.py`. ⚠ **But strict-aliasing miscompiles are
  version-dependent**, and if clang 22.1.6 / gcc **13.3.0** (not 14 — this line
  said 14, and p47's review had it right) simply do not exploit it, the
  pattern's headline collapses to a clean negative. Decide in `§0` whether that
  is worth building. **Check whether `-fsanitize=type` (TySan) exists in
  `~/tools/llvm`** — if it does, it is a catcher this project has never used, and
  it would sit in the same "outside the measured matrix" box as p18's four.

  > ✅ **LANDED AND REVIEWED at TASK_067** (was PROVISIONAL; sources in
  > `.temp/p38probe/`). Three of these moved this row:
  > **(a)** TySan **exists and fires**. ⚠ **The manager's mechanism here was
  > WRONG and is retracted**: it read *"the blind spot is inlining, not
  > optimisation level"*. It is neither — **TySan checks only accesses that
  > survive to the end of the pipeline**, and promotion is the case that removes
  > all of them. One TU *plus `noinline`* fires at every level; inlined builds
  > with a heap or escaped object fire at every level. Inlining mattered only
  > because a cross-TU call forces the object into memory
  > (`.memory/03-measurement.md`).
  > **(b)** The bug class **is** exploited here — both compilers, `-O1/-O2/-O3`,
  > 12 of 12 cells flip on `-fstrict-aliasing`. The null-result risk above is
  > refuted **for the two-non-char-type shape**.
  > **(c)** ⚠ **But this row's own spelling is the benign one.** *"Read a
  > `uint32_t` out of an `unsigned char` array"* is UB by 6.5p7 and **neither
  > compiler exploits it** — 8 of 8 cells give the defined answer with and
  > without the flag. A pattern built on `memcpy`-vs-cast-on-a-byte-buffer
  > returns a null result **for the wrong reason**. p38 must pick its shape from
  > the weaponised direction; TASK_066 §0 owns that decision.
- **p22 (hash probe) — the strongest result on the list and the most likely to
  need harness work.** The bug is a probe loop that never terminates on a full
  table: **memory-safe, a real DoS, and safe Rust does not prevent it either** —
  R2, R3 and R4 all hang, and **only R5 catches it, as a `decreases` obligation**.
  That is the exact mirror of p09 (invisible to the proof) and no pattern here
  has it. ⚠ **An adversarial input that HANGS is not in the gate's vocabulary** —
  stage 4 records per-rung behaviour, and a non-terminating cell is a new
  behaviour class. Settle that before writing rungs, and **STOP and report if
  `harness/` needs a change.**

  > ⚠ **PROVISIONAL — manager read of the harness, not yet reviewed, and rule 3
  > applies: a DIFFERENT agent must attack this before p22 is scheduled.**
  > Read at TASK_066 time, source-only, no gate run. **The vocabulary already
  > exists; the COST is what kills it.**
  >
  > - `check.py::run_bin` (`:464-470`) already returns `(None, "", "<timeout
  >   after Ns>")`, and `check_adversarial` (`:2006`) folds that into an ordinary
  >   behaviour row — `exit=None`, `signal=None`, `diverges` computed against the
  >   model. **It does not crash and it does not fail**; stage 4 records rather
  >   than requires. A hang is already representable.
  > - The checksum stage excludes `adversarial-*` from agreement (`:4786`), so a
  >   hanging cell cannot false-fail there.
  > - **`measure.py` never EXECUTES an adversarial input.** All three of its
  >   execution paths — checksums (`:528`), `CG_PLAN` (`:56-61`) and `wall`
  >   (`:558`) — are hardcoded to `small.bin`/`large.bin`. The loop that does
  >   iterate every blob (`:483`) only calls `slb.read` and `model.build().describe()`.
  >   ⚠ Note `SKIP_INPUT_PREFIX = "sweep-"` does **not** cover `adversarial-`, so
  >   this holds by the hardcoded input lists, not by a filter — **a future edit
  >   that generalises those lists would reintroduce the problem silently.**
  > - **The killer is `RUN_TIMEOUT = 900` (`:169`).** p22's premise is that R2,
  >   R3 and R4 all hang, so **12 to 20 cells × 900 s = 3 to 5 hours** added to
  >   every `check.py p22` run — and a doc edit makes the record STALE, so that
  >   is paid repeatedly. Not viable.
  >
  > **So p22 DOES need a `check.py` change**, and a small one: a per-input
  > timeout the contract can declare (a probe loop that never terminates is
  > detectable in ~5 s, not 900). ⚠ **Batch it with the open `forbidden_hits`
  > fail-vs-print decision** (`.memory/02-bench-rules.md`, TASK_065 outcome 3) —
  > both are `check.py` edits, and `check.py` costs **one gate re-run**, not the
  > full re-measure a `build.py` edit costs (RECAP, settled answer 4). Two
  > separate sweeps is the thing to avoid.

  ⚠ Also `.memory/04-verus.md`: `decreases b - a`
  fails on two-cursor loops, and a probe sequence's measure is *unvisited slots*,
  which needs a ghost set — budget more than one session.
- **p36 (vtable dispatch) — likeliest to hit p55's wall.** An out-of-table
  indirect call jumps to whatever is adjacent, so **the harm is not
  reproducible**, and there is no equivalent of the fold-from-offset-16 trick
  that rescued the UAF. Settle reproducibility **first**, the way TASK_055 had to.

  > ⚠ **PROVISIONAL — manager read of the harness, not yet reviewed; rule 3
  > applies.** Read at TASK_066 time, source-only. **This row's own citation was
  > wrong and its risk is overstated.**
  >
  > - **`check.py:1249` is not the checksum rule** — it is a selftest for
  >   `idiom_problems` ("a bare string is not a declaration"). The real rule is
  >   **`check_checksums`, stage 2, `:1440-1476`**. A line number written against
  >   a file that grew from ~5100 to ~5460 lines drifted, which is the ordinary
  >   failure mode here: **cite the function, not the line.**
  > - **And stage 2 runs on NON-ADVERSARIAL inputs only** (`models` vs
  >   `adv_models`). p36's harm lives on the adversarial input, which stage 2
  >   never executes — **so non-reproducible harm does not bite stage 2 at all.**
  > - Stage 4 records without requiring; several distinct behaviours produce a
  >   `rep.note`, not a failure (`:2044`).
  > - Stage 7's exit-code check (`:4783`) **is** unscoped — but it is
  >   short-circuited by the `expect == "fires"` branch (`:4769`), which requires
  >   only that a sanitizer **fired**, not that the exit code matched. So an
  >   adversarial input declared `"fires"` **tolerates a non-deterministic exit.**
  >
  > **So the binding requirement is not "the harm is identical" but "a sanitizer
  > fires DETERMINISTICALLY".** That is a much weaker bar and it reopens p36.
  > ⚠ **The real open question is instead: does anything in the gate's sanitizer
  > set see an out-of-table indirect call?** Stage 7 builds `gcc -O1
  > -fsanitize=address,undefined` (`:4738-4739`) — **no CFI**. `-fsanitize=cfi`
  > needs `-flto`, is clang-only, and is a **`build.py`** change, i.e. a full
  > re-measure (RECAP settled answer 4) — do not reach for it lightly. UBSan's
  > `-fsanitize=function` (indirect call through a wrong function type) may
  > already reach it and is *not* a matrix change. **UNVERIFIED — it needs a
  > compile probe, deferred because an engineer was running.** Settle it before
  > p36 is scheduled.
  ⚠ And R1h's real answer is `-fsanitize=cfi`, which needs `-flto` and is
  clang-only — a build-flag change, so **harness territory: report, do not make
  it.**
- **p31 (provenance) — demote it.** Miri is the only checker, which is fine (it
  is already gate stage 8), but the expected shipped-compiler behaviour is
  *nothing observable*, which makes it **p08's shape** — a tooling-and-
  expressiveness result the tree already has one of. Build it for provenance
  only if a pattern is wanted whose whole finding is a tooling claim.

⚠ **This is a judgement call, not a measurement, and it is the manager's own** —
PROTOCOL rule 3. Two honest objections to it, neither answered here: **(a)** the
user's standing goal names *breadth over realistic C patterns*, and axis-first
ordering trades breadth for depth; **(b)** "eleven of sixteen are bounds bugs"
counts *bug classes*, and the project's actual findings are about **cost
mechanisms**, which have been much less repetitive — p12's lost bulk lowering and
p07's never-amortising tax came from two patterns this argument would call
duplicates. **Push back on it with the pattern you would rather build.**
