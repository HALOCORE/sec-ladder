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
  `clean`/`fires` (`check.py::build_models`). The reason survives only in `model.py`'s docstring.
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
| p15 | UTF-8 validation + decode | malformed continuation bytes | moderate–hard | ⚠ **REFUSED at TASK_085/TASK_085_REVIEW — CONDITIONALLY, and the condition is NAMED.** Unlike p48/p31/p45 the justification was not false a priori: **all three probes PASSED** and the named kill-risk **closed** (a verified UTF-8 validator, `ensures res == valid_utf8(b@)` bidirectional, **5/0, zero trusted items**). It is refused because **all three of the row's justifications were then measured away in one session** *and* because the shape worth building is the shape the gate cannot audit. ⚠⚠ **~~It becomes buildable the day `_axiom_items` learns to see a USED vstd `assume_specification`~~ — THAT CONDITION IS NOW DEAD.** The route it named was **narrowing `check.py::_scan_unsafe_sites`**, and the manager **DECIDED AT TASK_096 / TASK_096_REVIEW THAT THE RULE STAYS** (`.memory/02-bench-rules.md`, with its five reasons) — the narrowing was demonstrated **UNSOUND end to end**, admitting a `#[verifier::external]` fn nested in a verified body that Verus reports `2 verified, 0 errors` for and whose binary **reads out of bounds**. ⚠ **`p15` is therefore refused WITHOUT a live unblocking condition.** ✅ **Its artefact survives the row and must not be lost** — a verified UTF-8 validator, `ensures res == valid_utf8(b@)` bidirectional, `5 verified, 0 errors`, **zero trusted items**, embedded verbatim in `.tasks/TASK_085_REPORT.md`. See the refusal block below |

## Family C — parsing & protocol decoding

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p16 | TLV / length-prefixed record walker | length field vs remaining buffer | easy–moderate | **done** (T007), reviewed; gate PASS first run, R5 == R4 `exact` at O3; **first O(n) cost of a *spelling* — R3 is still 0/byte** |
| p17 | HTTP `Range:` style header parser | int overflow → OOB (cf. CVE-2017-7529) | moderate | **done** (T011), reviewed; gate PASS first run, R5 == R4 `exact` at O3; **memory-safe but functionally wrong**; the *leaking* slice-guard variant reproduced at T012 (`.temp/` artefact + committed generator — see `.memory/05-layout.md` item 11 for why it cannot live in the pattern dir) |
| p18 | varint / LEB128 decoder | **unbounded shift** — ✅ **the catalogue's guess UPHELD, the first row in five patterns to survive its own guess** (T049 §0, four alternatives rejected with measurements). **The first bug here that is UB but NOT a memory-safety bug**: it touches no memory and **ASan is silent** | easy–moderate | **done** (T051), gate `PASS` first complete run, R5 **12/0** (twin 13/0), `R4 ≡ R5 exact`, Miri 9/9, **TCB 3, no `assume`**, **reviewed** (T051_REVIEW: 1 blocker + 7 majors + 5 minors, **15 clean negatives**; corrections at T052). **Four catchers — UBSan, `debug-assertions`, Miri, Verus — all outside the 24-cell matrix**, and Miri catches it as a **panic**, not a `ub` report |
| p19 | protocol state machine (byte-at-a-time) | state confusion | moderate | ✅ **BUILT at TASK_087 as `p19-state-machine` — the 23rd pattern.** Gate `PASS`, **0 failures / 0 loud / 0 blocked**, Verus **12/0** (twin 13/0), TCB 3, `identity` **O0 `norel` / O3 `exact`**. **`Ir` per message byte: R2 15.00 · R3 9.75 · R4/R5 8.75 · c-gcc 11.00 · c-clang 8.75** (whole-program marginal, `-O3`, **inline mode `isolated`**). **`R2−R4 = 6.25 = 3.00 check + 3.25 foreclosed 4x unroll`**, and the third rolled instruction is a `mov` — **the checked spelling must keep `st` live for the compare and cannot destroy it with the shift.** ⚠ **The result to quote: LLVM lowers the bounds check to `cmp $0x8`, a STATE-RANGE check — safe Rust's automatic check and the validation pass C omits are THE SAME PREDICATE**, enforced once per access versus once per call. **The bug class is the tree's THIRTEENTH `index >= len`** (nearest sibling p36) and the pattern says so in four files. **The framing is CONDITIONAL and the conditions are PINNED**: the table must be loaded *data* and dispatch must be by *indexing*, not `switch` — the only `forbidden` entries in the tree that forbid a spelling **for being safe**. Precedent, source fetched and manager-verified real: Linux `security/apparmor/match.c`'s `aa_dfa_match_until()` indexes four tables with **no test at all**, licensed by `verify_dfa()` at policy load. ⚠ **The two CVE IDs the pattern cites are NOT verified — confirm or strike them before quoting.** **Second result, not about Rust:** validation is **O(table) once** and the bounds check is **O(message)**, so the buggy C rung is **5071 `Ir`/call cheaper than unsafe Rust at `small` and 3569 dearer at `large`** — a sign flip that is not about safety. ⚠⚠ **THREE NUMBERS THE MANAGER PUT IN THIS ROW FROM `TASK_086`'s PROBE WERE WRONG, and the first is the one to remember:** ~~`gcc -O2` **exit 139 SIGSEGV**~~ — **the harm is SILENT**; the SIGSEGV was a **STORAGE-CLASS ARTEFACT** of the probe's `static uint8_t TBL[8][256]` in `.bss`, and the same read from the **heap exits 0**. ~~naive `+5.25 Ir/byte`~~ is **+6.25** (the probe folded with `wrapping_add`; p19 folds `acc*31+st`, which needs `st` in a register the check also needs). ~~the 2-D rows `+4.25` spelling~~ **does not exist in contract** — the probe's `k19_rows` got its `&[[u8;256];8]` from an `unsafe` cast **in its driver**. **Harm ships instead as THREE INPUTS ONE BYTE APART** — entry 8 in-bounds/ASan-clean, entry 10 `heap-buffer-overflow`, entry 255 `SEGV on unknown address`; all three silent at plain `-O2` on 8/8 C cells. See `.tasks/TASK_087_REPORT.md`. |
| p20 | length/offset pair validation (heartbeat-style) | trusted length field (cf. CVE-2014-0160) | moderate | **DEFERRED at TASK_086 with a measurement — landed at TASK_115, and the reason is STRONGER than TASK_086 stated.** ⚠⚠ **PROBE 3'S INSTRUCTION LIST AND ITS NUMBER WERE BOTH WRONG, CORRECTED AT TASK_120 — and the corrected mechanism predicts the corrected number TO THE INSTRUCTION, which the published pair did not.** ~~`+10.00 Ir`/call, six instructions (`add;setb;cmp;seta;or;jne`), `0.0024 Ir`/byte~~ → the check is **SEVEN** instructions: the list omitted the leading **`mov %rcx,%rax`** that computes `off+len`, and the disassembly diff is a clean 7-line insertion. Re-measured: **`+6.00 Ir`/call marginal** (`22066.00` vs `22060.00`) and **`+7.00 Ir`/call kernel-exclusive** (`22036.00` vs `22029.00`) — **exactly the seven inserted instructions**; `0.0024 Ir`/byte becomes **`0.00146`**. ⚠ **The UNCHECKED twin re-measures EXACT; only the checked rung moved, by `−4`.** ⚠⚠ **THAT `−4` IS OPEN AND UNATTRIBUTED** — `p21` moves identically, both unchecked twins are exact, and `k39`/`k41`/`k43` ALL reproduce exactly, so it is NARROW and is NOT the 18.9 M whole-program drift (RECAP finding 41). The `.rodata`-alignment hypothesis was RUN AND KILLED (`--remap-path-prefix` to TASK_086's build path gives identical numbers). ⚠ **The same two errors are in `.tasks/TASK_115_REPORT.md` and `.temp/t86/NOTES.md`.** ✅ **The VERDICT is unaffected and in fact STRENGTHENED**; the loop body is the identical 8×-unrolled fold. **A length/offset check is O(1) and does not scale.** Probe 2 clean (`251 B 056e9912…` vs `235 B e6f559dc…`); probe 4 clean (`slice::from_raw_parts` 0 hits). ⚠⚠ **Kill risk, MEASURED: with `secret` malloc'd BEFORE `buf` the identical run leaked 0 bytes** — `p48`'s lesson. ⚠ **`TASK_086`'s own disclosure: `leaked_secret_bytes=1616` counts coincidental `0x53` bytes and is NOT an oracle — do not quote that figure.** ⚠⚠ **AND THE DUPLICATION REASON NAMED TOO FEW PATTERNS: `TASK_086` said *"p16's and p02's"*, but `p17` IS BUILT, REVIEWED, and IS a trusted-length-field OOB (int overflow → OOB, cf. CVE-2017-7529) with the leaking slice-guard variant reproduced at TASK_012. So `p20` duplicates THREE built rows, not two, and the deferral holds a fortiori.** ⚠⚠ **AND TASK_120 CAUGHT THAT CLAUSE AS A SELECTION EFFECT, WITH A TIMESTAMP: `p20`'s OWN stated kill is the MEASUREMENT above (`O(1)`, does not scale). The duplication clause was APPENDED AT TASK_115 by an agent who already knew the built tree, and says so in its own words — *"a fortiori"*. So `p20` is NOT a duplication refusal and RECAP finding 40 was wrong to count it as one.** ⚠ **A reinforcing reason is not the reason; this cell is the project's clearest instance.** |
| p21 | CSV/field splitter with escapes | quote-state off-by-one | moderate | **DEFERRED at TASK_086 with a measurement — landed at TASK_115.** Probe 3: ~~`26862.00` vs `26788.00` = `+74.00 Ir`/call~~ → ⚠ **RE-MEASURED AT TASK_120: `26858.00` vs `26788.00` = `+70.00 Ir`/call.** ✅ **`p21` moves EXACTLY as `p20` does — the checked rung `−4`, the UNCHECKED twin EXACT — and that `−4` is OPEN and unattributed (see `p20`'s cell; the `.rodata`-alignment hypothesis was run and killed).** **The tax is per FIELD, not per byte** — the `buf[i]` check is hoisted and what remains is `nf < 64` on ~74 commas. Probe 2 clean (`210 B fb463072…` vs `213 B 9c45103b…`); probe 4 `::get_unchecked` 0 hits. ⚠ **Kill risk: the quote-state adds a data-dependent branch but NO NEW BOUND — the row is `p14` with a different delimiter rule, and `p14`'s row already says its bug class is the unbounded field count.** ⚠ **Harm cell corrected at TASK_090: `p21` fires BOTH ASan and UBSan; the `head -4` in `.temp/t86/harms.sh` showed only the UBSan half.** |

## Family D — data structures, array-backed

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p22 | **open-addressing probe over a full table** (delivered as `p22-hash-probe`) | **non-termination — the class UPHELD, and reframed in §0.** Memory-safe, ASan/UBSan silent, Miri silent 90 s. ⚠ *"R2/R3/R4 all hang"* is true of a **mechanical port** and false of the shipped ladder, which puts the bug in **R1 only**; the published claim is *"nothing on this ladder EMITS the capacity check"* | hard | **done** (T070), gate `PASS-WITH-BLOCKED-ROWS` (a declared-hang input blocks a Miri row) first complete run, 0 failures, R5 **20/0** (twin 23/0), `R4 ≡ R5` `exact` at O3, TCB 5, **reviewed** (T070_REVIEW: **1 blocker, 3 majors, 4 minors, 54 named attacks**; corrections at T071, which refuted the review twice). **First user of the hang machinery.** ⚠ **"The first termination obligation" was FALSE** — 73 exec-loop measures already existed. The counted claim: **the tree's only exec-loop measure not expressible in the loop's own exec variables, 1 of 73** |
| p23 | in-place quicksort partition | ⚠ **the catalogue's guess *"aliasing, permutation invariant"* is NOT what shipped** — it is the tree's **15th `index >= len`** | hard | ✅ **BUILT at TASK_101 as `p23-partition` — the 25th pattern. Gate `PASS`, 0 failures, both records FRESH. PROVISIONAL — UNREVIEWED.** **R5 `16 verified, 0 errors` FIRST ATTEMPT** (twin 19/0), **zero `proof fn`s**. ⚠⚠ **THE MANAGER'S NAMED KILL RISK WAS IMAGINARY AND THE OPPOSITE IS TRUE.** The task file argued the bug might live in the nested-scan **Hoare** form while only the single-loop two-index form verifies; **the Hoare form verifies `6/0` first attempt too, and the bug lives in the form that verifies MOST EASILY** — because the spec is written in the shape the code moves in, which is why `p06` needs three lemmas for a simpler obligation and `p23` needs none. ⚠ **The multiset novelty claim is TRUE at the pinned-clause level** (0 hits for `multiset`/`permut` across every pinned clause of all 24 prior patterns). ⚠⚠ **BUT *"the multiset is SEPARABLE"* IS STRUCK — TASK_105 showed THE EXPERIMENT THAT ESTABLISHED IT WAS MEASURING A VACUOUS POSTCONDITION.** Both probes do give `6/0`, but the multiset-deleted probe's remaining `ensures` is vacuous in `p24`'s exact sense: a body that **zeroes the live prefix and never looks at the pivot** verifies `4 verified, 0 errors` against it, while the identical body with the multiset **kept** gives `3 verified, 1 errors`, *"postcondition not satisfied"* — **the must-fire arm, and it fires.** ✅ **The CONCLUSION survives on better evidence: the SHIPPED postcondition is an exact value equality (`r == partition_fold(...)`), not a property like `p24`'s `is_heap`, and it refuses all NINE mutants including all four degenerate bodies — 9 of 9 fail, 3 of 3 controls verify, the strongest mutation result in the tree** (against `p24`'s 7/8 and `p29`'s 3/4). ⚠ **A multiset is invariant under permutation and `fold_scr` is not, so the exact fold is STRICTLY STRONGER than the clause that was dropped.** ⚠ **Also corrected: the top-level `contract.requires`/`ensures` are IDENTICAL across all 24 patterns, so "grep the pinned ensures" is trivial at that level — the per-item clauses are the ones that carry content.** **It ships on finding 37's replacement bar, not on its bug class:** new operator (the guard compares **two loop variables**), **new source of the bound — each cursor's bound is the OTHER cursor, and both move**, and a new elision reason. **HEADLINE: the safety tax is a function of the data's SHAPE, not its SIZE** — ⚠⚠ **MAGNITUDE CORRECTED AT TASK_117, MANAGER-RE-MEASURED: ~~`227.00 → 706.37`, a factor of 3.11~~ is the SHIPPED SPELLING PAIR; against the cheapest IN-CONTRACT R3 (`k_u5`) the same shipped R4 gives `172.64 … 227.00`, a factor of `1.3148`.** The spelling term is **exactly `2·dn − 2·recs`** (`480.00` at `nlow=1`, `0.00` at `nlow=31`, residual `0.0000` over 41 points), i.e. **COLLINEAR WITH THE AXIS ITSELF.** ⚠ **Quote `1.3148×` and a `54.36 Ir`/call swing.** The axis is real — `m`, record count and copied bytes **all fixed** and only the **pivot's rank** moving; the extent-band law predicts `416.32` for all seven rows. ✅⚠ **THE PHENOMENON IS CONFIRMED AND THE CAUSE IS OPEN (TASK_105 M4).** ✅ `k_up == k_r3c` and `k_dn == k_r4b`, exactly — **all nine cells independently reproduced to the instruction by the reviewer's own probe.** ⚠⚠ **BUT *"the direction of the cursor is the whole tax"* DOES NOT SURVIVE ISOLATION.** Making the induction variable **ascend** does not recover the elision — it costs **`+816`/`+1614`/`+1313`** — and **removing the unsigned subtraction from the index recovers only `16`/`12`/`20` of a `488`/`184` gap.** **Land the phenomenon; the cause is UNEXPLAINED.** ✅ **Clean negative alongside it: NO in-contract respelling elides the downward check** — audited with `check.py::spelling_matches` itself; a reslice is dearer at every rank and a redundant hint is exactly equal. ~~**The tax is not a spelling cost inside the declaration.**~~ ⚠⚠ **THAT SENTENCE IS FALSE AND THIS ROW CONTAINED ITS OWN REFUTATION FOR THREE TASKS (found at `TASK_117`).** **`k_u5` — the tautological conjunct, in contract, same object code — is `150.00 Ir`/call cheaper at rank 50 and `480.00` cheaper at `nlow=1`**, which is *exactly* a spelling cost inside the declaration; the M5 paragraph further down this same cell says so. ⚠ **The audit that produced the false sentence used `check.py::spelling_matches` and was sound; what it missed is that a REDUNDANT LEADING CONJUNCT satisfies a `required` pin while changing nothing the compiler emits.** **The surviving true statement is the narrow one: no in-contract respelling ELIDES THE DOWNWARD CHECK.** ⚠⚠ **THE LAW WENT THROUGH THREE FORMS, EACH WITH ZERO IN-SAMPLE RESIDUAL, AND THE FIRST TWO ARE WRONG OFF THEIR BAND (TASK_106).** The four-term `242 + 2·dn + 2·sw − 3·rounds` is **band-K-only and mispredicts the two SHIPPED matrix inputs by up to `152.00 Ir`/call** — despite a `0.0000` holdout *inside* band K. ✅ **The form that survives all 109 shipped points: `R3 − R4 = 2 + 30·recs + 2·dn + 2·sw − 3·rounds + Σ τ(m mod 4)`, `τ = {0→0, 1→2, 2→3, 3→4}` — max |residual| `0.0000`, and the real holdout is FIT ON BANDS M+N (71 points) → PREDICT THE 38 NOBODY FITTED → max |error| `0.0000`.** ⚠ **`τ` was invisible to every band: K sits at `m=32` and N at `m=16`, both `≡ 0 (mod 4)`, and `sweep_fit.py` reads band M at `want_m = [2,4,8,16,24,32,40,48]` — SEVEN OF EIGHT MULTIPLES OF FOUR, leaving one non-zero sample.** ⚠ **`τ`'s mechanism is NOT established — cite it, do not explain it.** ✅ **`up + dn == mbytes` exactly at all 109 points** (band K's `256.00` generalised): total cursor work constant, only its split moving. ⚠ **`up + dn = 256.00` exactly at every point — total cursor work is CONSTANT and only its SPLIT moves**, which is what makes the axis clean. ⚠⚠ **SIGN CORRECTED (TASK_105 M2): `R1 − R1h` on gcc is `+39.10`/`+60.34`, POSITIVE — meaning THE HARDENED KERNEL IS CHEAPER by that much**, and it is also **smaller** (157 vs 160 insns); clang is `−3.12`/`+23.14`. ⚠ **This row previously said "NEGATIVE (−39.10/−60.34)". The substance was right and the sign notation was inverted, and the manager copied it from the report's prose — `NOTES.md`'s TABLE had it right all along while `NOTES.md`'s PROSE had it wrong. Rule 9's exact cause: the finding was written from the report instead of from the record.** ⚠⚠ **AND THE gcc GUARD'S PRICE FLIPS SIGN TWICE ACROSS p23's OWN RANK BAND** — `+168.48` at rank 0.03, `−144.59` at 0.50, `+139.87` at 0.97, two zero crossings. **So *"negative price on gcc"* is a property of the two shipped inputs' ranks (0.44 and 0.28, both inside the negative window, and `gen.py::_check_residues` ENFORCES they straddle 0.35), not of the kernel.** ⚠⚠ **AND IT IS ABSENT FROM p23's OWN MIXED BAND — the guard price is POSITIVE at all five band-X points.** The claim survives on two enforced inputs and on **no** mixed input measured. ⚠ **`p23`'s own warning — *"any number quoted without its rank is quoted without its domain"* — was never applied to its own C row.** **Harm:** SIGSEGV in both directions from one omitted pair of conjuncts, and **`m == 1` is structurally adversarial — no crash, exit 0, all wrong.** ⚠⚠ **THE DISTINCT-CHECKSUM COUNT IS NOT A FACT AND CANNOT BE MADE ONE — the correction requested was IMPOSSIBLE AS SPECIFIED (TASK_106).** Four gate runs gave **7, 7, 8, 8**. **`NOTES.md` is in the gate record's `source_sha256`, so editing it to record the count forces a run and the run moves the values being recorded** — a structural regress, not a transcription slip. ✅ **`NOTES.md` now publishes the INVARIANT and no number: exit 0, silent, all rungs diverge, hardened rungs agree, plus a logged-run history table.** ✅ **Clean negative: NOTHING is pinned on those values** (`expected_exit` is 0, R1's adversarial stdout is recorded with `diverges: true` and never required), **so the gate never depended on a layout-dependent number.** ⚠ **The engineer shipped a false claim and its own control caught it before measurement** (`i < m` vs `j > 0` is **equivalent**, not "safe and wrong" — 800 000 randomised records, 0 differences); corrected in three places. ⚠⚠ ~~**THE MANAGER'S SWAP-COUNT CONFOUND IS REFUTED, and the result is stronger for it**~~ — **THIS INVERTS AT TASK_117 AND IS THE SHARPER HALF OF THE CORRECTION.** Against the SHIPPED pair the swap counts are `7.63`/`7.75` at the endpoints and `dn` alone fits **R² `0.987`** against `sw`'s **`0.013`**. ⚠⚠ **Against the cheapest IN-CONTRACT R3 THE TWO SWAP PLACES: `dn` falls to `0.0001` and `sw` rises to `0.9930`.** **So the swap-count refutation is TRUE OF THE SHIPPED PAIR AND FALSE OF THE PATTERN — `sw` was the right regressor all along and the shipped R3's spelling was hiding it.** ✅ **Consistency check that makes both believable: subtracting the spelling term `2·dn − 2·recs` from the published law leaves `2 + 32·recs + 2·sw − 3·rounds + Στ` — NO `dn` TERM — and at `recs=8` its leading part is `258.00`, exactly the flat value the unchecked-downward-read arm measures at all 31 ranks.** ⚠⚠ **M5 IS RESOLVED AND IT WENT AGAINST THE HEADLINE (TASK_106): THE `2991.00` SPELLING IS ADMISSIBLE.** The bare descending mirror `k_u1` is **out** of contract (its guard reads `m - g < j &&`) — **but restoring `i < j &&` as a REDUNDANT LEADING CONJUNCT gives `k_u5`, which matches all 8 `required` including the English, hits no `forbidden`, and COMPILES TO THE SAME OBJECT CODE (`md5_norm da08af26d9b1`, 249 insns, both).** So at rank 50 the cheapest in-contract R3 is **`2991.00`, not `3141.00` — the floor was 150.00 too high — and at `59.00` below `r4b`'s `3050.00` THE R3 AND R4 SPANS OVERLAP.** **`spec.md`'s one real bound is not falsified (it is an upper bound) but loosened: ≥150 of the published safe-side figure is SPELLING, NOT SAFETY.** ⚠ **The correction is itself rank-dependent** — `u5` is `338.00` below `r3d` at rank 0, `150.00` at rank 50, and **`46.00` ABOVE at rank 100.** ⚠ **The span's TOP endpoint was ALSO wrong: `4208.00` is `r3b`, which is `forbidden`.** Corrected span over twelve in-contract spellings: **`2991.00 … 3719.00`.** ✅ **Clean negative and the interesting half: `u2`/`u3`/`u4` are all DEARER than or equal to the shipped shape — only the TAUTOLOGICAL conjunct recovers the saving**, which makes this a finding about the declaration mechanism rather than about `p23` (`.memory/02-bench-rules.md`). ⚠ **Not done: bands N and X shipped unfitted (band M reads 8 of 47, band K 7 of 31).** ⚠ **The missing `-C debug-assertions=on` column DOES hide a sign flip, located: R3−R4 is `+574` at rank 3%, `+1334` at 50%, and `−246` at 97% — R4 DEARER.** **The shipped inputs' ranks are outside the flipping region so the headline survives, but the disclosure must say WHERE.** ⚠ **And `r4dn` becomes EXACTLY EQUAL to `base` under debug-assertions — `assert_unsafe_precondition!` reinstates precisely the check `get_unchecked` was bought to remove.** Evidence: `.tasks/TASK_101_REPORT.md`, `.tasks/TASK_105_REPORT.md`, `.temp/t101/`, `.temp/r105/`. |
| p24 | binary heap (sift up/down) | parent/child index arithmetic | moderate–hard | ⚠ **PROBED at TASK_086 (ranked 4) and TASK_090 (R5). PROVISIONAL — unreviewed.** ✅ **R5 CLOSES and the manager's prediction that `heapify`'s loop was the sticking point is WRONG — nothing stalls.** `heapify(v: &mut [u64])` **requires NOTHING about heap order** and ensures, unconditionally and in the **positive** direction, `final(v)@.to_multiset() =~= old(v)@.to_multiset()` **and `is_heap(final(v)@)` over the WHOLE ARRAY** — `6 verified, 0 errors`, and at the R5 rung with trusted accessors **`6/0` shipped, `8/0` twin**. ⚠ **The real content is in `sift_down`, not `heapify`:** the invariant `forall j != i ==> heap_at` is **not inductive** (the swap raises `v[i]` and can break `heap_at(parent(i))`) and needs a **parent-dominance conjunct** — proved load-bearing by mutation. **7 of 8 mutants fail**, including p24's own `2*i+2 <= n` bug. ⚠⚠ **The 8th is the vacuity control and it PASSES: with the multiset clause deleted, a body that ZEROES THE ARRAY still satisfies `is_heap`** — the multiset clause carries the anti-vacuity weight. Twin teeth verified: three separate weakenings pass ordinary Verus and **only** the twin config moves. ⚠⚠ **COST RETRACTED — ~~`≈7.9 ± 0.1 Ir`/element~~ IS A PROBE-SHAPE NUMBER, AND AT SHIPPED SHAPE THE TAX IS `0.00`** (TASK_092, measured). Given a fixed-capacity scratch and a header-derived count, **`ship_safe` and `ship_unsafe` are BYTE-IDENTICAL** — *"identical by raw machine-code bytes: True"*, `md5_fn 3d37ca7b…` both, `n_nopad 133` both, **no panic edge in either** — and it stays byte-identical with the count read as a `u16`. The probe's 7.9 reproduces only because its sift takes `i` as an opaque parameter and `n` as an ABI value, leaving **five bounds branches per sift** (`jae:6` safe vs `jae:1` unsafe). ⚠ **The 18-length residue work behind the 7.9 was sound; it was measuring the wrong SHAPE.** ⚠ **So p24 has no measured safety tax and needs a new reason to be built** — its R5 result and its temporal-adjacent index arithmetic stand, the cost axis does not. ⚠⚠ **TWO NUMBERS FROM TASK_086's PROBE ARE WRONG, AND THE FIRST IS A REPORTING BUG THAT AFFECTS FOUR ROWS:** ~~*"silent at `gcc -O2`, and only UBSan sees it — ASan did NOT report a heap-buffer-overflow"*~~ — **ASan reports it in ALL THREE storage classes on BOTH compilers**, and **UBSan alone reports nothing anywhere**. The cause is `head -4` in `.temp/t86/harms.sh`: gcc's UBSan report is exactly 4 lines and ASan's banner is on lines 5–6. **Re-running TASK_086's own unmodified binary gives exit 1 and one ASan `heap-buffer-overflow`.** ⚠ **Rows `p21`, `p24`, `p26` and `p41` each fire BOTH detectors, so that table could only ever show the UBSan half for four rows — treat every harm cell in it as half-shown until re-run with `grep` instead of `head`.** And ~~`+22.1%`~~ is **not a constant of the row**: it steps 27.5% → 22.2% at n=1024/1025, and **the step is in the DENOMINATOR** — the probe's `cost.rs` clones inside the measured loop and glibc `memcpy` switches to `rep movsb` at **8192 bytes**, which callgrind charges **≈1 `Ir` per byte moved**. ⚠ **Not free to ship:** `heapify` needs `len <= usize::MAX/2 - 2` for the `2*i+2` overflow, so a driver conjunct is owed (the p17 route). Evidence: `.tasks/TASK_090_REPORT.md`, `.temp/t90/`. |
| p25 | dynamic array with `realloc` growth | growth overflow, stale pointer | moderate–hard | ⚠⚠⚠ **RE-OPENED AS A CANDIDATE — THE BAR CHANGED (finding 53, `.memory/02-bench-rules.md`). ADMISSION IS NOW C-SIDE ONLY, AND THIS ROW'S REFUSAL RESTED ON DRIVER-ARTEFACT GROUNDS THAT THE NEW BAR FORBIDS. DO NOT REUSE THE REASON BELOW. Re-adjudicate at `TASK_143`: is the C program correct on benign inputs, does it exhibit the error on an adversarial input, and is its C MECHANISM distinct from a built row's? Everything the Rust and Verus rungs do is a RESULT to report.** ⚠ **DEFER STANDS — AND IT WAS NEVER PROBED (established at TASK_115).** `TASK_086` recorded it as out of scope, noting only *"nothing found that disturbs p25's defer"*. ⚠⚠ **This row has NO MEASUREMENT OF ITS OWN and must not be quoted as if it did.** Later corroboration is indirect only: `TASK_093` §0.1 reuses *"`p25`'s standard"* (the detector test) to refuse a different row, and `TASK_100` §B5 confirms *"the resize path is `p25`'s row, still planned; verdict unchanged"*. **It is the one remaining row on which this project has run nothing.** ⚠⚠⚠ **PROBED AT LAST (`TASK_134`) — AND REFUSED. IT WAS PROMOTED TO LIVE CANDIDATE UNDER THE USER'S NO-NEW-SPATIAL PRIORITY, IT WAS THE FRONT-RUNNER, AND IT DIED ON FOUR INDEPENDENT MEASUREMENTS. ⚠ Engineer work, UNREVIEWED (rule 9); the manager re-ran the load-bearing arms. Full result: RECAP finding 48.** ⚠⚠ **THE KILL NOBODY PREDICTED: IN `p25`'s SHIPPED HEAP TOPOLOGY `realloc` NEVER MOVES.** The driver `malloc`s the blob before the kernel runs, so the vector is the newest allocation and glibc extends it in place — ✅ **manager-re-run, `moved=0/12` under BOTH compilers**, the buggy rung's answer EQUALS the correct one in 6 of 6 cells, and **ASan fires only because ASan's own allocator moves on every `realloc`.** ⚠ **So the UB executes and is unobservable — `p08`'s published sentence verbatim, and `p08` is built.** ✅ **Three topology-independent kills, any one sufficient:** *(1)* **THERE IS NO SAFETY CONJUNCT TO OMIT** — the safety line here is an ADDRESSING MODE, not a check, so `p27`'s *"R1 omits exactly `&& live[h] == 1`"* has **no analogue**, and a rung that saves `(base, k)` and re-derives on mismatch **IS the index port**; *(2)* the gradient is **`+1.00 Ir` per read — ONE instruction of register allocation**; *(3)* **R1 HAS NO REPRODUCIBLE CHECKSUM** (same binary, same input, two different answers) **and a nondeterministic R1 cannot be gated against `model.py` at all.** ⚠ **The growth-overflow half is a measured `heap-buffer-overflow WRITE` — SPATIAL, refused on sight.** ⚠⚠⚠ **AND THE MANAGER'S OWN PREDICTION IN THIS CELL WAS WRONG.** ~~*"A stale INDEX is not a stale POINTER: if the port uses indices the bug vanishes into `p04`'s class"*~~ — ✅ **manager-re-run: the index port has NO BUG AT ALL.** `realloc` **copies**, so `v[k]` names the same element afterwards and the answer is simply correct. **Not a different bug class; no bug.** The three addressing modes are `&T` across a `push` → `E0502`, `as_ptr()`+deref → `E0133`, index → compiles and is correct. ⚠⚠ **AND THE OTHER HALF OF THIS CELL'S ADVICE DIED TOO:** ~~*"safe Rust's `Vec` makes a stale `&T` across a `push` a COMPILE ERROR, so the safe rung may not be able to EXPRESS the bug"*~~ **is TRUE BUT NOT DISTINGUISHING — seven controls that CANNOT have the bug print the same `E0502`, including a `struct S { v: u32 }` with no container at all. THIRD instance of that failure mode. See finding 48.** ⚠ **The one revival route, recorded so it is not rediscovered as new: a deliberately TWO-VECTOR kernel moves reliably (`9/12`) — but it is a kernel designed to produce its own bug, which is contrived rather than idiomatic, and it was not measured further.** |
| p26 | run-length encode/decode | expansion overflow on decode | moderate | ⚠⚠ **REFUSED at TASK_115 — and `TASK_086`'s third-tier BUILD is withdrawn by its own kill criterion.** `TASK_086`'s `5.33×` is invalid (the pair is not the same function). `TASK_092`'s matched shipped pair reproduces exactly (`7570.30/6837.30`, `24450.30/32837.30`, `55794/44381`) **but its stated mechanism is not the cause, and its *"neither has a panic edge"* is FALSE — BOTH rungs have one, and the GOT-indirect call is why nobody saw it.** Factorial (fill spelling × fold spelling): with the checksum fold unchecked on both sides the inversion **vanishes** (`+1170` at r=200). ⚠⚠ **The `−8387` is the FOLD's bounds check surviving in the *UNSAFE* rung at `2.99 Ir`/output byte, because deleting the FILL's check destroyed `o <= OUTCAP`.** Instruction accounting closes: 5.75 vs 8.75 insns/element, `3.00×3200 = 9600` predicted against `9560` measured. **Null control: `safe` vs `safe_fill` — TWO SAFE SPELLINGS — differ by `+8339`**, and `safe_fill` is **byte-identical to `ptr::write_bytes`** (`5917bd8eec3f`, 114 insns). Symmetric control both directions: deleting the capacity line costs ≤0.7%; `unsafe_guard` is a third codegen dearer than both. ⚠⚠ **IT IS `p13`'s FINDING INCLUDING `p13`'s OWN RETRACTION: give the unsafe rung the bound in one line (`if o > OUTCAP { unreachable_unchecked() }`) and `S−U` is POSITIVE at 253 of 254 run lengths — published `−8387` becomes `+1173`**; `assert!` agrees to 2 `Ir` and costs the safe rung nothing. **And there is no input band to design:** a dense sweep of EVERY `r ∈ [1,254]` (no stride, so no residue trap) gives **four sign changes** (r=4,33,59,65), with `ship_safe` dropping **exactly `−2804.00 Ir` at every `r ≡ 1 (mod 32)`** — the SIMD width of its fill. **The sign is a property of `r mod 32`, not a threshold, and NOT `p19`'s rate crossing.** ✅ **Finding 37 is NOT contradicted here: the compare-and-branch IS present, just in the fold and on the unexpected rung.** Evidence: `.tasks/TASK_115_REPORT.md`, `.temp/t115/`. |

## Family E — data structures, pointer-backed (Verus stress tests)

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p27 | **handle table over per-record `malloc`/`free`** (delivered as `p27-handle-table`; the *singly linked list* SHAPE is retracted -- where `next` sits decides observability and that is a glibc detail, and the bug would fire on **every** input, which the adversarial-only constraint forbids) | **use-after-free -- the class UPHELD, and the project's FIRST TEMPORAL bug.** R1 omits one conjunct (`&& live[h] == 1`) on the READ path | hard (`vstd::raw_ptr`) | **done** (T060), gate `PASS` first complete run, R5 **15/0 first run** with a functional postcondition (twin 20/0), `R4 == R5` `exact` at O3 / `norel` at O0, **TCB 7 (forced -- see below)**, **reviewed** (T060_REVIEW: **no blocker**, 3 majors, 8 minors, **28 clean negatives**; corrections at T061). **Not one instruction of `R3 - R4` is the lifetime guarantee** -- a closed decomposition over *every* function gives `230.07 = 109.65 kernel + 120.42 drop glue + 0.00 allocator`, and an R4 keeping R3's bounds checks costs **+153.51**, so safe Rust pays **43.86 LESS** of the spatial tax. The lifetime guarantee itself costs **zero**, and its shape is structural: **the free and the invalidation are one operation in safe Rust and two in C, and the bug is the third -- the ASKING -- going missing** |
| p28 | intrusive doubly linked list | aliasing, ownership | research-grade | ⚠⚠⚠ **RE-OPENED AS A CANDIDATE — THE BAR CHANGED (finding 53, `.memory/02-bench-rules.md`). ADMISSION IS NOW C-SIDE ONLY, AND THIS ROW'S REFUSAL RESTED ON RUST-SIDE GROUNDS THAT THE NEW BAR FORBIDS. DO NOT REUSE THE REASON BELOW. Re-adjudicate at `TASK_143`: is the C program correct on benign inputs, does it exhibit the error on an adversarial input, and is its C MECHANISM distinct from a built row's? Everything the Rust and Verus rungs do is a RESULT to report.** ⚠⚠ **REFUSED at TASK_093 / TASK_093_REVIEW — the verdict is REVIEWED, and its FIRST STATED REASON WAS REJECTED BY THE REVIEW.** ⚠ **Read `.memory/01-ladder.md`'s allocator-guarantee section before rescheduling; do not reuse TASK_093's `E0382`/`E0499` argument, which is false.** The reusable reason: **safe Rust's temporal guarantee is a guarantee about the ALLOCATOR**, and p28's two safe spellings that free per node both catch the bug by **p27's runtime mechanism** — `Rc`/`Weak` reproduces p27's published sentence verbatim (`bwd=32127`, the backward walk truncating at `upgrade() -> None`), while the index arena **never frees** (`0` heap blocks released by unlink, measured). ⚠⚠ **AND THE NEAR MISS IS THE VALUABLE HALF: a p28 with R3 = safe arena and R4 = raw-pointer DLL would have published *"safe Rust is 6.02× CHEAPER than unsafe"* with `321/296 = 108.4%` OF THE GAP IN THE ALLOCATOR** — the bounds check is `9.00`, **3.0% of the magnitude and the opposite sign**. Sixth instance of the flattering-direction trap and **the first caught BEFORE a pattern was built.** ⚠ **The cost half of the refusal does NOT follow, though** (TASK_093_REVIEW blocker 2): `box_arena` vs `box_arena_unchecked` — same program, one `Box` alloc + one free per node on **both** sides — gives a closed decomposition **`+24.00 = 12.00 bounds check + 11.00 THE ASKING + 1.00 interaction, and `0.00` ALLOCATOR**, which is exactly the form p27 published. **p28 CAN do what p27 did**; it is still p27's *mechanism*, which is why the row is refused. ✅ **Clean negatives from the review, do not re-run:** `rawptr`'s `+321` is a **real** allocator price (`k_alloc_pair24` = `340.823 Ir`/node), **not** p31's malloc-elision artefact; the C detector table reproduces exactly under the **gate's** flags; and `p01` really is inside the count of 14, so **14 patterns carry the `index >= len` axis and 13 model a bug on it** (three tracked files assert an ordinal built on that list). **Superseded material follows.** ⚠⚠ **THE *"expect R5 to be defeated"* PREDICTION BELOW IS CONTRADICTED TWICE OVER** (TASK_086 #241, TASK_091; **PROVISIONAL — unreviewed**). ✅ **`wf` is PRESERVED by `unlink` (`4/0`) AND ESTABLISHABLE (`8/0`, FIRST ATTEMPT)** — `new()` → `push_front`×3 → `unlink` on the **MIDDLE** node, with `unlink`'s three `requires` discharged **from `push_front`'s postcondition alone**. Compiles and runs correctly. **Zero TCB — no `assume`, no `external_body`, no `assume_specification`.** ⚠⚠ **THE LOAD-BEARING CLAUSE IS ADDRESS INJECTIVITY, and without it `fake3` passes: ONE node with `prev = next = itself`, declared `len = 3`, `ptrs@ = [p,p,p]`, discharging `unlink`'s ENTIRE precondition.** ⚠ **The difficulty is NOT where anyone predicted:** injectivity cost one 8-line `proof fn`; the real costs were **(1) `Dll` needing EXEC fields it had only in ghost — a CONTRACT change, budget it in `spec.md`** — and **(2) `is_disjoint` taking `&mut self`, so it CANNOT be called inside `assert forall|i| … by`**, which is a goal-reformulation problem no proof hint fixes. ✅ **Probes 2 and 3 now exist (TASK_086 ran neither), from LINKED binaries, zero-parameter — each `Ir`/victim IS the static loop-body count to three decimals, at N = 1024/4096/8192:** `k28_checked` 138 B **20.003**, `k28_unchecked` 202 B **11.503**, `k28_rawptr` 129 B **7.507**, `k28_rawptr_rmw` 129 B **7.507**. ⚠⚠ **THE WHOLE-STRUCT READ-MODIFY-WRITE VERUS FORCES IS FREE** — `raw_ptr` has no field-level mutator, so R5 must rewrite the whole 24-byte `Node`, and that costs **1.00 `Ir` per CALL out of 50 232**, with a driver swap-test flipping the sign to −3.00. **So R5 needs NO local `external_body` field-store wrapper to stay identical to R4** — the feasibility question p28's R4/R5 pair turns on. ⚠ **Do NOT publish *"the bounds check costs 8.5"***: of the 8.5 `Ir`/victim safe tax, **6 are the three `cmp/jbe`, ~1 the foreclosed unroll, ~1.5 register pressure** — p35/p05's shape. ⚠ **And the CHECKED kernel is SMALLER (138 B vs 202 B)** because the unchecked one is 2× unrolled; **do not read size as cost** (p19 showed 76 B vs 173 B). ⚠ **Design warning: 4.0 of the 12.5 R3→R4b gap is INDEX SCALING, not checking** — three `shl $0x4` a pointer list does not pay — **so a p28 whose R3 is a safe index arena would misattribute it.** ⚠⚠ **THE REMAINING RISK, and it is not `unlink`: there is NO `deallocate`.** The probe drops `Tracked<Dealloc>` and **leaks**; a shipped p28 must thread it like p27, **and that is where p28's TEMPORAL bug class actually lives.** Untested. Bug class **temporal**, shares with **p27** — the only temporal pattern in the tree. Evidence: `.tasks/TASK_091_REPORT.md`, `.temp/t91/`.
| p29 | BST **delete** with a cached lookup, over a slot table of raw pointers (⚠ the pre-build guess was *"insert/lookup"*) | **use-after-free AND use-after-recycle from ONE line, selected by the input** (⚠ the pre-build guess was *"recursive ownership"* and it is NOT what shipped) | hard | ✅✅ **BUILT AT `TASK_139`, REVIEWED AT `TASK_140`, AND GREEN ONLY AFTER THE MANAGER REPAIRED IT — the committed `TASK_139` state was `check.py: FAIL [tables]`, a stage-9c one-run-lag artefact. Now `PASS`, `failures: []`, `blocked: []`.** ✅ **Originally reported at `TASK_139` — `patterns/p29-bst-delete/`, `check.py: PASS`, `failures: []`, `blocked: []`, R5 `25 verified, 0 errors`, twin `30/0`, TCB **7** (the same seven `p27` ships — THE OCCUPANT-IDENTITY TEST COSTS NONE OF THEM). THE PROJECT'S 27th PATTERN AND ITS SECOND TEMPORAL ROW. ⚠ Engineer work, UNREVIEWED (rule 9); the manager re-ran the mutant battery and read the verdict out of the record.** ⚠⚠ **IT SHIPS ON LIMB 1, NOT LIMB 4.** ⚠⚠⚠ **BUT THE SENTENCE IT SHIPPED ON IS FALSE — `TASK_140`, ✅ manager-re-run:** ~~*"`p27`'s read-path line needs ONE conjunct; `p29`'s needs TWO"*~~ — **ONE CONJUNCT IS ENOUGH.** Two single-conjunct arms built out of the shipped `c/kernel.c` by substitution score **0 wrong, 0 ASan lines** with the positive control firing, and one of them **adds NO STATE** (it widens `live[]` from a bit to the OCCUPANT TAG, which `p27`'s own kernel calls a degenerated generation counter). ⚠⚠ **The false sentence is in TEN COMMITTED FILES, two of them HASHED (`spec.md`'s `why`, and `c/*` which is MEASUREMENT-hashed, so the C comments cost a RE-MEASURE). REPAIR QUEUED, NOT DONE.** ✅ **WHAT SURVIVES: the row is NOT a duplicate — the TWO-BUG-CLASS mechanism (one source line, two bug classes selected by the INPUT) and the limb-1 admission both stand. What falls is the COUNTING CLAIM.** ✅ **THE ATTACK ARM IS THE STRONGEST IN THE TREE — 10 mutants, 10 as expected, ✅ manager-re-run: `M6-constant-body` (VACUITY) FAILS, so the R5 is not discharged by a constant; `M2b` fails on a PRECONDITION at `tracked_borrow` — *the identity test cannot be EVALUATED without the liveness test*, C's `&&` ordering as a TYPE-SYSTEM FACT; and `M3b` deletes the occupant-identity conjunct alone, whereupon NOTHING LINEAR OBJECTS and the FUNCTIONAL REFINEMENT is what rejects it** — exactly `TASK_137`'s prediction, and the sharpest confirmation that linearity states *no use after DEALLOCATION* and cannot state *no use after the OCCUPANT CHANGED*. ✅ **`tab[]` is NOT nulled on free, and `p27`'s by-name argument is now a MEASUREMENT: adding `tab[cur] = NULL` moves the control's sanitizer class from `heap-use-after-free` to `SEGV`.** ✅ **`model.py` is written FROM THE CONTRACT — a purely functional BST with a REACHABILITY WALK as the read test, no cursor, no `par`, no `goleft`, no guard, no liveness array — and cross-checked against a second implementation.** ⚠⚠ **FIRST `identity: differ` ROW IN THE TREE (`O0`; `O3` is `norel`) — `.memory/02-bench-rules.md` recorded `differ` as a legal pin NO PATTERN HAD EXERCISED and said one real run was owed. THIS IS THAT RUN, and `p27`'s one-line `-O0` fix provably does NOT transfer to a struct payload.** ⚠ **NO COST AXIS IS PUBLISHED and neither rung's spellings were searched — deliberate, and a reviewer should not read the absence as a zero.** ⚠ **HISTORICAL — how it got here:** **RE-OPENED AT `TASK_133` — ADMISSIBLE ON LIMB 4, AND IT IS THE ONE ROW THAT SURVIVED THE RE-ADJUDICATION OF ALL FIVE TEMPORAL REFUSALS. REVIEWED (rule 9 satisfied: `TASK_133` is reviewer work); the manager re-ran the arms that overturn committed content. FULL RESULT: RECAP finding 49.** ⚠⚠ **IT DID NOT RE-OPEN ON THE MANAGER'S REASON.** The manager wrote *"outcome 5, the only GOOD outcome"* into the task file; `.memory/01-ladder.md` had ALREADY STRUCK the fifth outcome and this cell agreed with it. ✅ **It re-opens on a MEASUREMENT — limb 4 clause 3, *a safe rung that is SILENTLY WRONG*: ONE LINE CARRIES TWO BUG CLASSES SELECTED BY THE INPUT.** Same binary, five inputs differing only in which key is removed: **leaf victims → ASan `heap-use-after-free`; two-child victims → the in-order-successor splice overwrites the victim IN PLACE and frees the SUCCESSOR, an in-bounds USE-AFTER-RECYCLE that ASan CANNOT SEE.** ⚠⚠ **Two independent safe Rust spellings (index arena, `Rc<RefCell>`) agree on all five: BIT-IDENTICAL to buggy C where ASan is silent, and SILENTLY WRONG where C aborts — safe Rust removes the DETECTOR, not the bug.** ⚠⚠⚠ **THAT LAST CLAUSE IS CORRECTED AT `TASK_136` — see below; in the PINNED shape safe Rust is CORRECT where C aborts.** ✅✅ **THE DEGREE SPLIT IS SETTLED (`TASK_136`, ✅ MANAGER-RE-RUN): `H2` — the SAME line moved from the `free` to the LOCATED VICTIM — is EXACT on 1511/1511 measured inputs, agreeing with the re-derive arm on all 11 hand inputs.** ⚠ **`TASK_133`'s candidate failed on its SITE, not its mechanism: `H1` (null at the `free`) and `H2` have DISJOINT blind spots, and the deletion's second phase routes the successor through `H2`'s site.** ⚠⚠⚠ **THAT CLAIM IS FALSE IN THE SHIPPED SHAPE — REFUTED AT `TASK_137`, ✅ MANAGER-RE-RUN.** ~~*"the read-path analogue of `p27`'s `live[h] == 1` CANNOT BE USED, because evaluating it IS the bug"*~~ **was measured on a kernel whose only handle is a BARE POINTER. The shipped shape is `p27`'s SLOT TABLE, which carries `live[]`, and there `&& live[g_slot] == 1 && tab[g_slot][0] == g_key` is O(1), on the READ path, EXACT on 614/614, and touches freed memory ZERO times — against the direct-deref arm's 82 ASan lines and 41 aborts on the same corpus (and that arm is not exact either, 1/600).** ✅ **The check that answers the question does not have to dereference the pointer whose validity IS the question — it has to stop asking the POINTER and ask the TABLE, which is what `p27` does.** ⚠⚠ **So the `H2`-vs-`H3` comparison NEVER CONTAINED THE WINNING CANDIDATE, though `H2` itself SURVIVED a dedicated attack (14 hand inputs, 5 written to break it, 600 fresh windows, 0 disagreements).** ✅✅ **THE ROW CLEARS THE BAR ON LIMB 1, NOT LIMB 4 — AND ON THE TWO-BUG-CLASS MECHANISM, NOT ON A CONJUNCT COUNT.** ⚠ **This clause used to re-assert the very sentence struck nine clauses above it — PROTOCOL RULE 13 INSIDE ONE CELL, caught at `TASK_141`.** ⚠⚠⚠ **AND THE PREMISE THE MANAGER PUT IN THE TASK FILE WAS FALSE, AND `.memory/02-bench-rules.md` CARRIED THE SAME GLOSS: *"every pattern differs by exactly ONE CONJUNCT"* is **4 of 25** (`p17 p22 p23 p27`) — the rest add statements, declarations, loops or a control-flow edge. THAT WIDENING IS WHAT MAKES `H2` ADMISSIBLE.** ⚠ **THE HISTORICAL REFUSAL, kept because a refusal's reason gets reused:** **REFUSED at TASK_095 — was PROVISIONAL, UNREVIEWED.** It was TASK_094's one BUILD and the last live row in Family E; **§0 killed it.** ✅ **Limb (a) SURVIVES** — the safe representation really frees (`allocs=2001 frees=2000`, `remove_leaf` releases one 24-byte block, against p28's `0`). ⚠⚠ **LIMB (b) IS REFUTED THREE WAYS, manager-verified:** *(1)* the `E0502` is **generic borrowck** — a `struct S { v: u32 }` with **no data structure at all** prints the identical error with the identical message, **and so does `p27`'s own `Vec<Option<Box<Rec>>>`**; *(2)* **key-addressed, the same BST compiles, runs, and exhibits p27's published sentence verbatim** (`*cur = None` frees and invalidates in one operation; the second `find` — the ASKING — gets `None` at run time); *(3)* **key-addressed, the C rung has NO BUG AT ALL** (ASan silent, positive controls firing) — **p29's UAF REQUIRES a saved raw pointer and p27's does not**, because C's `tab[h]` retains the dangling pointer after `free`. ⚠ **And 22 of 24 patterns take their payload from a file blob, so the shipped kernel cannot host a pointer** — p27's own hashed `why` says exactly that. So a shipped p29 is **outcome 2** (p27's `Option<Box<T>>` discriminant, same type, same `*slot = None`) or **outcome 3** (silent, Miri-clean = p04's class). ⚠⚠ **AND ITS DECLARED COST ZERO WAS FALSE:** the `−0.00024 Ir`/lookup reproduces **exactly**, but it is a zero about the **WALK** — with the alloc/free in the pair it is **`+48.01 Ir`/key** (the `remove` term alone `+18.95`). **The manager's task file instructed that zero be written into `spec.md` §0 before measuring; that would have shipped a false declaration.** ✅ **THE ARTEFACT SURVIVES THE ROW and is EMBEDDED VERBATIM in `.tasks/TASK_095_REPORT.md`** (`sha256 90a338c7…`, 232 lines, the p15 precedent): a fully verified BST — recursive `Box<Tree>`, `Set`-valued `keys()`, `bst()`, `contains`, `insert`, `remove_min`, and a **three-case `remove` with the in-order successor** carrying `ensures res.bst() && res.keys() =~= self.keys().remove(key)` — **`9 verified, 0 errors`, TCB 0, no lemma, no `decreases_by`, manager-re-run.** Non-vacuous: a call site discharging `bst()` from `insert`'s own postcondition and removing a **two-child** key, plus a mutant battery where **3 of 4 valid mutants fail** (the 4th disclosed as invalid — it does not typecheck). ⚠ **This contradicts the catalogue's `hard` rating and its retracted *'expect R5 defeated'* for the MUTATING operations, not just `contains`.** Evidence: `.tasks/TASK_095_REPORT.md`, `.temp/t95/`. ⚠⚠⚠ **STATE AFTER `TASK_136`: THE ROW IS NOT BUILT, DELIBERATELY, AND THE REASON IS RECORDED SO NOBODY READS IT AS FAILURE.** A half-built `patterns/p29-*/` moves the pattern count the START HERE box tells you to derive and breaks `harness/tools/composition.py --check`; and the dominant remaining cost is unshortened — **all 26/26 contracts pin `ensures result == <fold>(...)`, so `p29`'s R5 owes a FULL FUNCTIONAL REFINEMENT with THREE WALKS where `p27` has none.** ✅ **What IS settled: the degree split, the safety line, the four-mechanism fault line, and four R5 arms.** ⚠⚠ **AND `p25`'s *"nondeterministic R1"* KILL DOES NOT TRANSFER — it is INPUT-CLASS-SPECIFIC. ✅ Manager-re-run, same binary, 20 runs: the use-after-FREE inputs give **19 distinct values of 20**, the use-after-RECYCLE input gives **1**. A `p29` whose adversarial inputs are the RECYCLE class HAS a reproducible R1. Reusing that kill by name would refuse a buildable row.** ⚠⚠⚠ **VERDICT AFTER THE REVIEW (`TASK_137`): BUILD `p29` — IT CLEARS THE BAR AND CLEARS IT ON A BETTER SENTENCE THAN THE ONE COMMITTED — BUT NOT ON `TASK_136`'s DESIGN AS WRITTEN, AND NOT FROM A TASK FILE THAT QUOTES RECAP 47/49/51 AS THEY STOOD.** ✅ **FOUR THINGS TO RE-SETTLE FIRST:** *(1)* **the SAFETY-LINE SITE, on a stated criterion** — the read-path candidate was never in the comparison; *(2)* **the SAFE RUNG, which is a THREE-WAY choice whose third option reproduces `p32`/`p33`'s REFUSED result** — so picking it wrong retires the row; *(3)* **whether `tab[]` is nulled on free, against `p27`'s own reasoned argument by name that nulling turns the bug into a different class**; *(4)* **`model.py` must be written FROM THE CONTRACT, not transliterated** — `TASK_136`'s `p29c/model.py` REMOVE is a line-by-line transliteration of `kernel.c`'s (same variable names, same `guard < CAP + 1`, same cursor move), which satisfies the model-sandbox rule mechanically and defeats it in substance. ⚠ **That is `p23`'s hazard and the engineer's own disclosed defect is one instance of it: their first delete-by-substitution and the model MIRRORED THE SAME ERROR and agreed. No published number inherits it; the CLASS is live in the artefact a build would inherit.** |
| p30 | chained hash table (buckets of lists) | ⚠ **the column *"combines p22 + p27"* is HALF FALSE** (TASK_094 #267) | research-grade | ✅ **REFUSAL STANDS, REASON UPGRADED — REVIEWED AT `TASK_133` (was PROVISIONAL, UNREVIEWED).** ⚠ **The surviving limb was an ARGUMENT and is now a MEASUREMENT:** *"what remains is `p27`'s half alone"* — a chained table's UAF fires **on an ordinary chain walk with NO saved pointer**, which is `p27`'s retained-pointer sentence with the pointer moved from the table into the chain. **REFUSE —** **A chained table CANNOT FILL**, so p22's non-termination is **structurally absent**: measured `maxchain=4096 of 4096 keys in 1024 buckets`, terminates. What remains is p27's half alone. ✅ **VERDICT STANDS, RE-MEASURED at TASK_100 — the flood reproduces exactly.** ⚠⚠ **BUT ITS SECOND LIMB REUSED THE RETRACTED ARGUMENT AND IS STRUCK:** ~~*"safe Rust cannot express an owned intrusive list (`E0382` + `E0499`)"*~~ is **the exact sentence `TASK_093_REVIEW` rejected**, and this file already says not to reuse it — **it got reused anyway, one row away from the warning.** ✅ **The manager asked whether a chained table offers any OTHER bug class, and the 24-pattern census answers NO, on measured grounds:** an **unreduced bucket index** is not novel — it is `p06`'s exact omitted line (`p06/spec.md:374`) and would be the tree's **15th** `index >= len`; and the **resize path** is not p30's to take, because **no built pattern models realloc/growth at all** (zero exec hits for `realloc|resize|reserve|push|with_capacity`) **precisely because that is already `p25`'s row.** |

~~Expect p28/p30 to defeat R5 within budget.~~ ⚠⚠ **RETRACTED — CONTRADICTED ON
THREE SEPARATE ROWS, EACH ON A FIRST ATTEMPT.** `p28`'s `wf` is preserved
(`4/0`) **and establishable** (`8/0`, **zero TCB**, compiles and runs);
`p24`'s `heapify` closes at `6/0`; and **`p29` closes at `4/0` with TCB 0** on a
recursive `Box<Tree>` with a `Set`-valued functional postcondition. **Family E's
R5s have been CHEAPER than predicted every time anyone ran one — `p31`'s arena
proof was smaller than `p27`'s, and `p29`'s is smaller still.**

⚠ **This prediction is why the whole pointer-backed family was scheduled LAST,
and it was written before anything was run.** The rows that actually died here
died on the **ladder test and duplication**, never on the prover. **Do not defer
a Family E row because of its Verus column; probe the R5 — it is one
`./verus_run.py` — and refuse or build on the boundary and the bug class.**

**Document where the proof got stuck — that is the deliverable for these
rows**, not a green checkmark.

## Family F — memory management

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p31 | **bump / arena allocator** | **provenance / alignment / exhaustion — ALL THREE REFUTED as distinguishing** | hard | ⚠ **REFUSED at TASK_079**, the sixth axis and the second refusal. The demotion below was **right in its verdict and wrong in its reason**, and the real reason is stronger: **the arena's own shape is provenance-clean in 24/24 cells** (sub-objects carved from one allocation legitimately share its provenance), **no gcc flag flips the one shape that IS exploited** — so p38's `-fstrict-aliasing`/`-fno-` control **does not exist for provenance** — and the axis table's own justification (*"the property Miri checks"*) is **false in the gate's configuration**. See the refusal block below |
| p32 | free-list allocator | double free, corruption | research-grade | ⚠⚠⚠ **RE-OPENED AS A CANDIDATE — THE BAR CHANGED (finding 53, `.memory/02-bench-rules.md`). ADMISSION IS NOW C-SIDE ONLY, AND THIS ROW'S REFUSAL RESTED ON RUST-SIDE GROUNDS THAT THE NEW BAR FORBIDS. DO NOT REUSE THE REASON BELOW. Re-adjudicate at `TASK_143`: is the C program correct on benign inputs, does it exhibit the error on an adversarial input, and is its C MECHANISM distinct from a built row's? Everything the Rust and Verus rungs do is a RESULT to report.** ✅ **REFUSAL STANDS, REASON CORRECTED AND MUCH STRONGER — REVIEWED AT `TASK_133`** (was PROVISIONAL, UNREVIEWED). **`p32` AND `p33` ARE ONE ROW.** See `p33`. |
| p33 | object pool with recycling | use-after-recycle | hard | ⚠⚠⚠ **RE-OPENED AS A CANDIDATE — THE BAR CHANGED (finding 53, `.memory/02-bench-rules.md`). ADMISSION IS NOW C-SIDE ONLY, AND THIS ROW'S REFUSAL RESTED ON RUST-SIDE GROUNDS THAT THE NEW BAR FORBIDS. DO NOT REUSE THE REASON BELOW. Re-adjudicate at `TASK_143`: is the C program correct on benign inputs, does it exhibit the error on an adversarial input, and is its C MECHANISM distinct from a built row's? Everything the Rust and Verus rungs do is a RESULT to report.** ✅✅ **REFUSAL STANDS — REVIEWED AT `TASK_133`, AND THE CORRECTED REASON IS MUCH STRONGER THAN THE ONE ON FILE. THIS WAS THE MANAGER'S LEAST-CERTAIN CALL AND THE ANSWER IS NEITHER OPTION IT OFFERED.** The manager asked whether the silence is TEMPORAL (novel) or `p04`'s LOGICAL one (duplicate). ⚠⚠ **It is NEITHER: it is a function of WHERE THE STORAGE LIVES.** One source, four builds: **safe slab `==` BUGGY C bit for bit** (`28173833944553` / `962056`); **safe `Vec<Option<Box<u32>>>` `==` HARDENED C bit for bit WITH NO HARDENING LINE WRITTEN** (`28173841632553` / `1202306`); and C's `MALLOC` arm fires ASan double-free and use-after-free exactly where its `SLAB` arm is silent. ✅ **Both storage choices are ALREADY SHIPPED — `p04` and `p27` — and there is NO THIRD SPELLING.** ⚠ **HISTORICAL: REFUSE, WITH `p32`, AS ONE ROW — was PROVISIONAL, UNREVIEWED.** ✅ **The interesting half is REAL and REVIEWED** (`.memory/01-ladder.md` outcome 3): a slot free list recycles storage the program owns throughout, so **safe Rust's temporal guarantee has nothing to attach to** — under `#![forbid(unsafe_code)]`, **use-after-recycle reads the recycled node's value (`9999` for an expected `1002`) and a slot double-free yields two ALIASED handles, both silently wrong and Miri-clean (0 UB in all three modes)**, ✅ **manager-re-run**. ⚠ **A generation tag does not rescue it** — the bump is the hand-written second store C omits (`gbug get(stale) = Some(val=7777) <- NOT CAUGHT`). ⚠⚠ **But that makes the class `p04`'s** (*"stays in bounds, invisible to a memory-safety proof"*) **and the harm framing `p48`'s** (*"in bounds, live, owned"*), which is refused. ⚠ **AND PROBE 1 KILLS BOTH INDEPENDENTLY: the bug compiles identically at C, safe naive, safe tuned and unsafe — no boundary ANYWHERE, which is `p31`'s death.** ⚠ **One instrument note (TASK_094 #266): the manager's *"does the safe rung FREE?"* test is sound for CONTAINERS and VACUOUS for ALLOCATORS** — a C free-list allocator also calls `free()` once at teardown, so *"released heap blocks"* reads `0` on both sides. |
| p34 | reference counting | leak, premature free | hard | ⚠⚠⚠ **RE-OPENED AS A CANDIDATE — THE BAR CHANGED (finding 53, `.memory/02-bench-rules.md`). ADMISSION IS NOW C-SIDE ONLY, AND THIS ROW'S REFUSAL RESTED ON LADDER-SIDE GROUNDS THAT THE NEW BAR FORBIDS. DO NOT REUSE THE REASON BELOW. Re-adjudicate at `TASK_143`: is the C program correct on benign inputs, does it exhibit the error on an adversarial input, and is its C MECHANISM distinct from a built row's? Everything the Rust and Verus rungs do is a RESULT to report.** ⚠⚠⚠ **REFUSAL STANDS — REVIEWED AT `TASK_133` — AND BOTH THE MANAGER'S REASON AND THIS ROW'S OWN HEADLINE FELL TO ONE MEASUREMENT. THIS EDITED REVIEWED `.memory/01-ladder.md` CONTENT; see outcome 4's scope note there and RECAP finding 49.** ✅ **Manager-re-run, LSan `use_stacks=0`, positive control firing at 4096 B: C's MANUAL REFCOUNT rung LEAKS 2160 B at checksum `6435204519055678286`; C's ARENA rung is CLEAN AT THE SAME CHECKSUM; Rust's `Rc` leaks and Rust's index arena is clean, both at that same checksum.** ⚠⚠ **LEAKING IS SELECTED BY THE OWNERSHIP DISCIPLINE, NOT BY THE LANGUAGE — THERE IS NO INVERSION, SO NO OUTCOME 4 IN THE SHIPPED SHAPE.** ⚠ **`Weak` is not a respelling: it CHANGES THE PUBLISHED CHECKSUM (`749491243298922113`), which the checksum contract excludes. And once the edge set comes out of a FILE, no edge is statically the back edge — which is why the DLL result does not transfer.** ⚠ **HISTORICAL, and the half that IS real is now scoped rather than lost:** `.memory/01-ladder.md` outcome 4: **the safe rung is WORSE than C.** `Rc` in both directions is a cycle and leaks; `Weak` for `prev` does not. ✅ **Manager-re-run: `miri cycle` → 5 `memory leaked` lines, `miri weak` → 0**, same checksum both; ⚠⚠ **THE NAMED KILL IS DEAD (TASK_100, PROVISIONAL) AND THE ROW IS STILL REFUSED — ON A NEW AND BETTER REASON.** ~~*"NAMED KILL, an ENVIRONMENT fact: there is NO WORKING LEAK DETECTOR FOR THE C RUNGS ON THIS BOX."*~~ **There is one, and it costs one line and zero `Ir`** — `__lsan_default_options()` returning `"use_stacks=0"` in the pattern's own `c/main.c`; the `-O1`/`-O2` silence was a **stale STACK root kept alive by inlining the allocating callee**, not a missing instrument (`.memory/00-environment.md`). ⚠ **The detector was never the binding constraint.** **The real reason to refuse: the safe rung leaks ONLY in the `Rc`-both-ways spelling, and `Weak` is equally safe, equally idiomatic and measured LEAK-FREE (`allocs=2 frees=2 delta=+0`).** The headline *"safe Rust is worse than C"* would survive only if `Rc`-both-ways were **pinned as THE safe spelling**, and the tree's one precedent for such a pin (`p19`'s `forbidden` entries) **does not rest its headline on it**. **And no cost axis was ever measured.** ⚠ Note the cyclic shape is the *hardest* case for default LSan, so a build would need the hook rather than luck. ⚠⚠ **AND THE LEAK NUMBER WAS SCOPED TO THE WRONG WINDOW:** ~~`3 allocs / 0 frees / 324 bytes`~~ → **`2 allocs / 0 frees / 240 bytes`** (`size_of::<RcNode>() = 104`, `+16` `Rc` header `= 120`, ×2). TASK_094 returned a `format!` String **from inside** the measured window, and that `format!` is `allocs=1 bytes=44`. **Same class as p29's `−0.00024`-vs-`+48.01`; the verdict is unchanged.** **An inversion the tree does not have, and `p27` explicitly does NOT model a leak. Fold the measured leak into `p42`'s triage rather than losing it.** |

## Family G — systems idioms & representation

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p35 | tagged union / discriminated dispatch | tag-payload mismatch | moderate | ⚠⚠⚠ **RE-OPENED AS A CANDIDATE — THE BAR CHANGED (finding 53, `.memory/02-bench-rules.md`). ADMISSION IS NOW C-SIDE ONLY, AND THIS ROW'S REFUSAL RESTED ON VERUS-SIDE GROUNDS THAT THE NEW BAR FORBIDS. DO NOT REUSE THE REASON BELOW. Re-adjudicate at `TASK_143`: is the C program correct on benign inputs, does it exhibit the error on an adversarial input, and is its C MECHANISM distinct from a built row's? Everything the Rust and Verus rungs do is a RESULT to report.** ⚠⚠ **BLOCKED, AND THE MANAGER HAS NOW DECIDED NOT TO UNBLOCK IT THAT WAY (TASK_096 / TASK_096_REVIEW, REVIEWED).** `_scan_unsafe_sites` **stays as it is** — see `.memory/02-bench-rules.md`'s decision block. ⚠ **The premise this row was scheduled on is REFUTED: `p35` is blocked by TWO rules and the second is RUST.** There is no safe union read (`error[E0133]`), and `_TWIN_BANNED` forbids the `unsafe` keyword in a twin, so the twin must be justified away — which is `n_twins == 0` → **hard FAIL. Executed on a synthetic pdir, not read: `p35` has NO LEGAL CONFIGURATION.** So narrowing `_scan_unsafe_sites` would have bought **exactly one row** (this one; `p15` is refused on grounds the rule does not touch) — **and the first narrowed predicate anyone wrote was UNSOUND**, admitting a `#[verifier::external]` fn nested in a verified body that Verus reports `2 verified, 0 errors` for and whose binary **reads out of bounds**. ⚠⚠ **~~THE ONE THING STILL OPEN IS `_TWIN_BANNED`~~ — PROBED AT TASK_097 AND THE ANSWER IS NO. `p35` IS DEAD AND THE CATALOGUE CLOSES.** ✅ **Manager-verified:** `_is_trusted` returns `False` unless the item is `#[verifier::external_body]`, and **a twin may not be `external_body`** by three independent rules — so **a twin is STRUCTURALLY never `_is_trusted`** and `_scan_unsafe_sites` hard-fails all four routes (twin-holds-unsafe, verified helper, `cfg`-gated helper, macro helper). **Isolated: delete `unsafe` from `_TWIN_BANNED` and `FAIL [tcb-unsafe]` is UNCHANGED — the twin rule was never what fired.** ⚠ **This refutes two sentences the manager wrote into `.memory/` one task earlier.** ⚠⚠ **AND THE REASON IS STILL NOT COMPLETE (TASK_098 §4A, reviewed): a GATE-CLEAN `p35` DOES EXIST.** `include!("h.rs")` outside `verus!{}` verifies `1 verified, 0 errors` with `_scan_unsafe_sites` at **0 failures** and `_path_includes` returning `[]` — **`include!` is a macro, not a `#[path] mod`, so the walk never sees the file** and **TASK_009_REVIEW's blocker x1 is re-opened by a different spelling.** ✅ **The row stays REFUSED on the merits** — such a `p35` has a **precondition checked by NOTHING**, which is the opposite of what a pattern here is for — **but say it correctly: `p35` has no configuration in which its safety obligation is CHECKED, not "no legal configuration."** See `.memory/02-bench-rules.md`. **The row's own measurements stand and are worth keeping:** ✅ **Verus supports the Rust `union` NATIVELY**: the correct-variant obligation is **first class in the type system** — declared inside `verus!` it is `error: requirement not met: to access this field, the union must be in the correct variant` (`1 verified, 1 errors`), and `requires v is i` gives **`2 verified, 0 errors`**. **No vstd spec is involved**, which is why probe 4's grep MISSES it and the row is blocked anyway: the read is still `unsafe { v.i }` in a **verified** fn. Boundary is **compile-time, p08's shape** — safe Rust's `enum` makes the mismatch unrepresentable. Cost **+0.829 `Ir`/element (+6.5%)**, ⚠ **and the mechanism is UNROLLING, not the check — both rungs execute the same tag test.** Bug class **type confusion, ABSENT from the built tree**. Harm has a magnitude axis: the `double` arm is a **silent wrong value with NO detector firing at all**; the pointer arm is **exit 139 SIGSEGV**. Traps: declare the union **inside** `verus!` (outside, Verus prints `external_type_specification`); `#[derive(Clone, Copy)]` fails; use `v is i`, not `v->i`. ⚠⚠⚠ **RE-TRIAGED AT `TASK_134` UNDER THE NO-NEW-SPATIAL PRIORITY (`p35` is the TYPE axis, which has ONE row). IT STAYS BLOCKED — BUT TWO SENTENCES ABOVE ARE WRONG, SO READ THIS BEFORE QUOTING THEM. ⚠ Engineer work, UNREVIEWED (rule 9).** ✅ **CORRECTION 1, MANAGER-VERIFIED AT `harness/check.py:3941`: the *"a GATE-CLEAN `p35` DOES EXIST … `include!` is a macro … so the walk never sees the file"* ROUTE IS CLOSED AT HEAD.** The line now reads `cand += _include_literals(txt)[0]`, so `_path_includes` **does** resolve `include!`, and `_scan_unsafe_sites`' second loop fails any `unsafe` in an include target **with no exemption branch at all**. **The cell advertised a live escape hatch that no longer exists.** ⚠ **CORRECTION 2 — *"`p35` has no configuration in which its safety obligation is CHECKED"* is TOO STRONG for the `external_body` route.** Verus **does** check the correct-variant obligation at the call site (the must-fail arm reports `precondition not satisfied`) and the wrapper **can** carry a full functional `ensures`, spelled `get_union_field::<U, u32>(v, "i")`. ⚠ **Union support is a LANGUAGE BUILTIN, not a vstd spec — which is why probe 4's `std_specs/` grep misses it and why *"no spec exists"* would be the wrong reading for the THIRD time.** ⚠ **NOT re-run by the manager; rests on the engineer's six Verus runs.** ✅✅ **THE REAL BLOCKER, AND IT IS SHARPER THAN ANYTHING ABOVE: the `unsafe` can only live in an `#[verifier::external_body]` body — the ONE allowed branch, `check.py:4178-4180` — which makes it a TRUSTED ITEM, WHICH OWES A TWIN, AND A TWIN MUST BE A SAFE SPELLING OF THE SAME OPERATION.** `p01`'s twin for `get_unchecked` is literally `v[i]`. **Rust has a safe spelling for indexing and NONE for a union read**, so the twin is `error[E0133]`. ✅ **The remaining hatch, `verus.twin_justifications`, is in 0 of 26 shipped contracts (manager-verified) and its only occurrence under `patterns/` is `p17`'s NOTES REJECTING an axiom for this very reason.** ⚠⚠ **THE WEAK LINK, FLAGGED BY THE ENGINEER FIRST: none of this is GATE-CERTIFIED — it rests on reading `check.py`'s predicates plus running Verus, NOT on executing the gate against a synthetic pdir the way `TASK_096`/`097` did. Execute that before treating the twin/`n_twins` interaction as settled.** |
| p36 | function-pointer table dispatch (vtable-like) (delivered as `p36-vtable-dispatch`). ⚠ **The catalogue's *"the harm is not reproducible"* worry is REFUTED — 24/24 SIGSEGV** across gcc/clang × O0–O3 × 3 opcodes; and the *"likeliest to hit p55's wall"* triage was wrong twice over | **index out of table — the class UPHELD, but it is the tree's TWELFTH `index >= len` and the pattern says so.** What is not twelfth: ⚠ **Verus at the pin cannot type `fn(u64) -> u64` AT ALL** (error on the *declaration*), so C's own dispatch mechanism is **not an admissible rung** and the Rust rungs use `[&'static dyn Op; NOPS]` — **priced at exactly `3.00000` Ir/dispatch, finding 14's sharpest instance because it excludes the MECHANISM, not a spelling** | moderate | **done** (T072), gate `PASS` first complete run, R5 **19/0**, `R4 ≡ R5` **`norel` at O3 — the first pattern in the tree not `exact`**, TCB 4 (2 contract-bearing), **reviewed** (T072_REVIEW: **2 blockers, 5 majors, 7 minors, 36 clean negatives**; corrections at T073, which refuted **three** prescriptions — two the manager's, one the review's). ⚠ **Both published headlines moved.** `R3 − R4 = +15.00 flat` was fitted against an R3 side **never searched** (one lever, and it moved R3 *dearer*): p36 now publishes **`+7.00` (fixed-R4 bound, cheapest R3 found) and `+10.00` (matched pair), never one number and no pair interval.** And every `Ir` was **kernel-exclusive on the one pattern whose kernel IS a call** — dispatch targets are 512/384/0 Ir per call, which **reverses** the `match` control and vanishes the gcc-vs-clang gap. **`Ir` exactly constant while wall clock moves 3.13×**, verified on program totals; ⚠ **not p07's finding in a costume** — p07's `Ir` moves and its branch is conditional. Catchers: ASan/UBSan name the **array read**, never the call; `-fsanitize=function` is **gcc-absent and clang-defeated**; only `-fsanitize=cfi-icall` names the transfer, and it is a control (needs `-flto` + `-fuse-ld=lld`), not a rung |
| p37 | callback with `void*` userdata | type confusion | moderate–hard | ⚠⚠ **RE-TRIAGED AND REFUSED at TASK_115, on THREE NEW MEASUREMENTS.** ✅ **`TASK_100`'s correction STANDS — limb (ii) is false and must not be re-quoted.** The row dies anyway. **(1) The confusion is UNREPRESENTABLE — `p08`'s shape, not a checked obligation:** `into_typed` **ensures** `is_uninit()` and `into_raw` **requires** it, so there is no route from an initialised `PointsTo<A>` to a readable `PointsTo<B>` (`2 verified, 1 errors`, positive control `good()` verifies), and `transmute` is `is not supported` at the pin. ⚠ **What `TASK_100`'s R5 actually checks is provenance + init, i.e. `p27`'s validity conjunct, NOT type identity.** **(2) Cost axis, the probe the row was missing: `21.00 / 20.00 / 18.00` `Ir`/record for typed-enum / erased+tag-check / erased-unchecked — the tag check is `+2.00`**, the same order as `p36`'s published `3.00000`. ⚠ **Measure it only with a RUNTIME tag: with a constant tag the CHECKED cell comes out CHEAPER (15.00) because LLVM folds the dispatch.** **(3) Harm: silent, exit 0, plausible answer in 8 of 8 plain cells**; ASan 2/2, control 4/4; clang `-O2` SIGSEGVs only when a neighbour is allocated. ✅ **Type confusion IS absent from the built tree — census of all 26 rows, not a whitelist grep** — nearest is `p38`, ⚠ **which IS a pun; what differs is that `p38`'s harm is a MISCOMPILE.** Evidence: `.tasks/TASK_115_REPORT.md`, `.temp/t115/`. |
| p38 | **record parser that clamps a length in place and re-reads it through a pun** (delivered as `p38-alias-pun`). ⚠ **The catalogue's own spelling — *"endian conversion, `memcpy` vs union"* on a byte buffer — is the BENIGN aliasing direction and was retracted before the build**: neither compiler exploits it, 8 of 8 cells. Only two incompatible **non-char** types move | **strict-aliasing UB — the class UPHELD** (unusual: three of the previous five were overturned), and the harm is a **MISCOMPILE**, not a wrong answer | moderate | **done** (T066), gate `PASS` first complete run, R5 **13/0** (twin 16/0), `R4 ≡ R5` `exact` at O3 / `norel` at O0, TCB 5, Miri 8/8, **reviewed** (T066_REVIEW: **no blocker**, 3 majors, 8 minors, **35 clean negatives**; corrections at T067, which refuted three of the *review's* own numbers). **Ships labelled a DEMONSTRATION KERNEL** — the harm needs four conjunctive conditions and **six neighbouring one-line spellings each remove it**. ⚠ **The quotable result is the price: on gcc the undefined spelling is the DEAREST of the six, and every fix saves exactly 6.00 `Ir`/call.** **The first bug class here that unsafe Rust does not reintroduce** — Rust has no type-based aliasing rule at any rung. Also the project's **first additivity-extrapolation failure**, which turned out **100% attributable** to three missing columns, none of them the one named |
| p39 | bitfield pack/unpack into wire format | shift/mask off-by-one | moderate | ⚠ **REFUSE — PROVISIONAL, UNREVIEWED.** **It is `p09`'s sentence with the mask on the other side**: the bug is **one immediate**, `$0x1ff` → `$0x3ff`, worth **`0.00 Ir`** — and `p09` already ships *"one character between a bug everything catches and one nothing does"*. ✅ **What it did contribute is a further instance of a real rule** — ⚠⚠ **AND BOTH HALVES OF HOW THAT WAS WRITTEN WERE WRONG, CORRECTED AT `TASK_122`.** ~~(`.memory/03-measurement.md`)~~ → **the `4.25` rule lives in `.memory/01-ladder.md`** (13 hits there, ⚠ **ZERO in `03-measurement.md`**), and `p14`'s NOTES cites it correctly — **so this was CITATION ROT, not ambiguity.** ~~*"a third instance … after `p35` and `p28`"*~~ → ⚠ **`p35` and `p28` are BOTH UNBUILT, and the rule already had FIVE instances on BUILT patterns (`p05` `p07` `p11` `p14` `p16`).** **The claim reached *"third"* by counting two unbuilt rows — which is the SAME circularity this file struck from `p43`'s cell.** ✅ **The rule itself stands and is stronger than stated: of the `4.25` check tax, `2.00` is the `cmp/jbe` and `≈2.25` is the unroll the panic exit edge forecloses.** |
| p40 | struct-of-arrays vs array-of-structs traversal | none — pure perf axis | easy | **REFUSED at TASK_086 with the measurement — landed at TASK_115.** N=1048576, 3 iterations, `callgrind --cache-sim=yes`: `k40_aos` **360,114,293** `Ir` / 3,481,161 D1 misses / 1,912,884 LLd read misses; `k40_soa` **360,114,314** / 2,301,516 / 454,953. ⚠⚠ **THE CONCLUSION SURVIVES — THE ROW'S OWN AXIS IS INVISIBLE IN THIS PROJECT'S PRIMARY METRIC — BUT THREE OF THE FOUR FIGURES DID NOT SURVIVE TASK_120. Do not quote the struck ones.** ✅ **`21 Ir` CONFIRMED TWICE**, including by a **zero-iteration control the original lacked**, which makes `k40_aos` and `k40_soa` byte-equal at `374,658,547` — so all 21 belong to the kernel. ⚠ ~~`5.8e-8`~~ → **`4.9e-6`, 84× larger: the 360 M denominator is 98.86% PROGRAM SETUP** and the kernel's own marginal is `1,442,043 Ir`/call. ⚠ ~~`+193 Ir` / `6.4e-5`~~ → **`+114` over 3 calls = `38 Ir`/call / `3.6e-5`: 115 `Ir` of it was `println!` FORMATTING A KERNEL NAME SIX CHARACTERS LONGER**, visible with the kernels never called. ⚠⚠ ~~`LLd read misses differ 4.20×`~~ → **DOES NOT REPRODUCE; re-runs at `3.68×`** — and both are WHOLE-PROGRAM counts dominated by the 67 MB + 16 MB setup allocations, **so neither figure is a property of the kernel at all.** ✅ **The `D1` miss delta reproduces EXACTLY (`1,179,645`), so the kernels are identical and the LLd figures moved with the ENVIRONMENT.** ⚠⚠ **AND `p40`'s ABSOLUTE TOTAL MOVED `360,114,293` → `378,984,676` — 18.9 M, ~5.2% — under a byte-identical pipeline with `rustc 1.97.1 / LLVM 22.1.6` and `valgrind 3.27.1` BOTH UNCHANGED. UNATTRIBUTED AND OPEN; `TASK_122` §B is written for it.** ⚠ **General rule this earned — RECAP finding 41, ⚠⚠ PROVISIONAL AND UNREVIEWED, `TASK_122` §A is its review: a published figure below ~100 `Ir` taken from a WHOLE-PROGRAM TOTAL rather than a DIFFERENCE is at the noise floor.** ⚠ **Wall clock cannot rescue it:** best-of-7 spreads **2.8%–32.7%**, over this project's own 10% discard threshold on **3 of 4** rungs. The catalogue's own bug column is *"none — pure perf axis"*. **`p01`'s axis with `p31`'s problem.** |
| p41 | flexible array member struct | size computation overflow | moderate–hard | **REFUSED at TASK_086 with the measurement — landed at TASK_115.** Probe 3 kills it: `k41_checked 23614.00`, `k41_tuned` **`2387.00`**, `k41_unchecked 2404.00` — ⚠⚠ **the TUNED SAFE rung BEATS the unsafe rung by `17.00 Ir`/call, and the apparent `9.6×` was 100% R3 SPELLING** (byte-at-a-time `from_le_bytes([buf[o],…])` against a `chunks_exact(4)` walk). **That is `p10`'s error exactly, and here it is 100% of the effect.** ⚠ **The bug class is unreachable in the natural spelling:** `sizeof(hdr) + n*sizeof(uint32_t)` in `size_t` does not wrap for any `n` a wire format can express; the harm fires only with the product cast to `uint32_t`, **which is `p07`'s finding verbatim, and `p07` already ships the reachable 32-bit-check version as `adversarial-width.bin`.** ✅ **Probes 1, 2 and 4 all PASS** (285 B / 244 B / 175 B, all distinct) — **the row dies on probe 3 and on duplication, NOT on the ladder test.** ⚠ **Harm cell corrected at TASK_090: `p41` fires BOTH detectors.** |
| p42 | `goto cleanup` error handling | leak on error path | moderate | ✅ **BUILT at TASK_104 as `p42-goto-cleanup` — the 26th pattern. Gate `PASS-WITH-BLOCKED-ROWS`, 0 failures**, the one blocked row being Miri on `large.bin` at the 180 s budget, **declared in advance** in `miri.blocked_reason`. **Verus `15/0`, twin `18/0`, axioms 0, `identity unsafe ≡ verus` `exact` at `-O3` / `norel` at `-O0`.** PROVISIONAL — UNREVIEWED. ⚠⚠ **REVIEWED AT TASK_109 — TWO BLOCKERS, AND BOTH HEADLINES MOVED.** *(1)* ⚠⚠ **BOTH HEADLINES ON THIS AXIS HAVE NOW BEEN RETRACTED — READ THIS WHOLE CLAUSE BEFORE CITING ANY OF IT.** ~~*"Verus at the pin cannot state leak-freedom"*~~ was retracted at TASK_109 in favour of a **ghost ledger** (escrow the token in a tracked `Map<int, Dealloc>`, `ensures` the domain returns empty), reported as stating it at **`18 verified, 0 errors`, ZERO new trusted items, ZERO object-code change**, with the leak arm at `17 verified, 1 errors` and **`verus.obligations` moving 15 → 18.** ⚠⚠ **THE GHOST LEDGER IS ITSELF REFUTED AT TASK_116, MANAGER-VERIFIED: ITS `ensures` IS SATISFIED BY A LEAKING PROGRAM.** Replace the error path's `led_free` with `proof { let tracked _dl = led.tracked_remove(0int); }` and it still gives **`18 verified, 0 errors` / `21 verified, 0 errors` twin, with obligations, twin count and axioms ALL UNCHANGED**, while leaking exactly `n_err × win_len` = `model.py::leak_bytes`; ⚠⚠ **its `-O3` kernel is BYTE-IDENTICAL to the shipped R4 with p42's bug planted (`md5_fn d3f1194cb10bce2057e0e1f3e28c1e21`, `n_fn 128`).** **Mechanism: `Map::tracked_remove` is the call `led_free` itself makes — wrapping an affine resource in a Map does not make it linear, it makes the drop take one more line.** ⚠ **Keying by ADDRESS fails; a ghost `int` key works** (unaffected). ✅ **Clean negative that SURVIVES and is now better evidenced: there is NO linear must-consume tracked mode at the pin — 22 attributes (not 23), `vstd/` and `std_specs/` both checked.** ⚠⚠ **THE STATE OF THE QUESTION: two encodings tried, both admit a verifying leaker; INEXPRESSIBILITY IS NOT PROVEN and is OPEN.** ✅ **Live repair lead, measured: a module-local `Tracked<Freed>` receipt is FORGEABLE in proof mode (`3/0`); a PRIVACY-SCOPED one is not (rustc rejects it). Unbuilt.** ⚠ **The shipped tree is safe because the `identity` pin catches the attacked R5 at both levels — THE PIN, NOT THE PROOF.** ⚠⚠ **RETRACTION SITES STILL OWED IN THE PATTERN (need a gate re-run and a re-measure): 4 hashed `spec.md` fields, `verus.rs`, `unsafe.rs`, `NOTES.md`, `README.md`, 3 `controls/`, and `results/tables/` via its GENERATOR.** *(2)* ⚠⚠ **THE COMPARATIVE HEADLINE IS REFUTED — *"safe-tuned beats unsafe"* does not stand.** `r4_endptr` is genuinely inadmissible (`vstd::raw_ptr::allocate` ensures only `addr + size <= usize::MAX + 1`, so the one-past-the-end pointer is not computable in verified exec code) — **but the search missed an admissible do-while fold that never leaves the allocation**, `15 verified, 0 errors`, `identity exact`, agreeing on all 12 inputs, and **the sign flips: `−36.00`/`−2036.00` published against `+12.00`/`+11.00`.** **The R4 span now OVERLAPS R3 at both ends, and p42's OWN hashed paragraph predicted this verbatim** (*"two upper bounds differenced bound nothing in either direction"*) while `NOTES` 11b calls the two minima *"the two INFIMA"*. ⚠ **MAJOR: `spec.md:63` says three things are pinned and NONE of the three is enforced** — two `required` entries carry **no backticks** so they yield zero spellings, and **the idiom the pattern is NAMED FOR is unenforced**. ⚠ **MAJOR: the clang effect is window PARITY, not size** (`−5` even / `−4` odd, zero size dependence over 32×; three terms isolated). ⚠ **`leak.sh` runs 352 points, not the 88 stated in four places** — but ✅ **it has teeth: a planted non-leak gives exit 1, 12 rows flagged.** ✅ **All four self-corrections verified real, the gcc rungs ARE two rungs (one branch-target field), the rate restraint held everywhere, and the allocator refutation reproduces exactly.** `Tracked<Dealloc>` is **AFFINE, not linear** — a proof may simply drop it, and an R5 that forgets the error path's `deallocate` verifies `2 verified, 0 errors`, with the must-fail arm (use-after-move) correctly rejected (`controls/affine_leak.rs`). **`p27` proves deallocation is LEGAL, never that it HAPPENS.** ⚠⚠ **`p42` IS THE FIRST PATTERN WHOSE R5 PROOF DOES NOT COVER ITS OWN BUG CLASS** — Miri stands behind the Rust side instead, and the deleted-`dig_free` positive control ships and fires. ⚠ **SCOPE: this is the DEFAULT ENCODING, not an exhaustive search — a ghost ledger and Verus's linear mode were NAMED AND NOT BUILT.** ✅ **All three of the manager's least-sure calls came back YES:** the real gate **can** host a leak (settled BEFORE the rungs existed by importing `check.py` and driving `check_sanitizers` itself — 4 arms, 2 of them controls that must fail); the behaviour matrix **is** a finding **and** there is a real cost axis (R3 `1263`, R4 `1461`, R2 `1850`, `c-gcc` `1873` kernel-exclusive `Ir`/call); and the error path **is** drivable from a file blob (a malformed record tag, reachability asserted by simulation in `gen.py` AND `model.py::selfcheck`). ⚠ **`R1 − R1h` is `0.00` on gcc** — the two kernels differ in exactly one branch-target field — **but `−4.00`/`−5.00` on clang**, mechanism isolated: clang merges two early exits into `setne`/`sete`/`or` once both target `cleanup`. ⚠⚠ **p42 PUBLISHES TWO POINTS AND NO RATE**, because it applied `p23`'s out-of-band rule before publishing: fit on windows 64..79 and predict 512..527 and **every rung's out-of-band residual is 3×–25× its in-sample one**, the cheapest rung mispredicting its own shipped `large.bin` by **`−2545 Ir`/call**. **The allocator size class is REFUTED as the mechanism (smooth curvature, not a step); the real one is OPEN.** ⚠ **The first gate run FAILED and all four causes were the engineer's own**, disclosed: backticked words inside prose `forbidden` entries are forbidden *spellings*; `vparse` silently disabled 5c-req on a destructured `Tracked(pt)`; one `ensures` was not load-bearing; three `SLB-TRUSTED-ARGUMENT` sections were missing. ⚠ **`r4_endptr` is `162 Ir`/call cheaper and admissible in principle, ITS R5 WAS NEVER BUILT, R4 was held fixed by fiat — and the published spans OVERLAP**, which is `p23`'s span lesson recurring one pattern later. Evidence: `.tasks/TASK_104_REPORT.md`, `.temp/t104/`. |

## Family H — numeric & crypto-adjacent

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p43 | checksum / CRC over untrusted length | loop bound from input | easy | ⚠ **REFUSE — PROVISIONAL, UNREVIEWED. ⚠⚠ THE VERDICT SURVIVES AND THE REASON DOES NOT — `blocker` at TASK_120.** ~~*"`+3.00 Ir`/call flat, the hoisted check visible in `objdump`, i.e. `p16` verbatim"*~~ ⚠⚠ **`p43` IS FLAT AND `p16` IS `O(nrec)` — they differ in ORDER.** `p16`'s own `NOTES.md` opens with `7 + 5·nrec` / `7 + 7·nrec` **and a BOLD WARNING against exactly this conflation** (*"'O(1) per call' is what this paragraph said until TASK_016, and it was wrong"*). **So the measurement offered as CONFIRMATION of p16-likeness is the measurement that DISTINGUISHES them.** ⚠ **What the `+3.00` actually is, from ELF-extent disassembly: `lea; cmp; jbe` — a whole-slice length check, hoisted, executed once per call, `O(1)`.** ⚠⚠ **THAT IS `p20`'s PHENOMENON — AND `p20` IS THE CITATION THIS CELL STRUCK AS CIRCULAR. The surviving corroboration is the MISMATCHED one and the accurate one is unavailable under the built-rows-only rule.** **`p28`'s shape exactly: right verdict, wrong reason — and a reason is what the next row gets judged against.** ⚠ **The row still refuses; it needs a NEW reason, and *"a hoisted O(1) length check"* is the honest one.** ⚠ **And the safe TUNED rung beats unsafe by `0.749 Ir`/byte**, which is the flattering-direction trap again. ✅ **VERDICT STANDS, re-measured at TASK_100** (`26664.00 / 23593.00 / 26661.00`). ⚠ **ONE CITATION STRUCK: this said *"`p16`/`p20` verbatim"*, and `p20` IS NOT BUILT — it is `planned`, and its `+10.00 flat` traces to an UNREVIEWED PROBE of that unbuilt row.** ⚠⚠ **A refusal must be corroborated against BUILT patterns; corroborating one unbuilt row with another is circular.** `p16` is built and reviewed and carries the refusal alone. ✅ **And p43 was NOT refused on the broken form of probe 2** — nor were `p44` or `p39`; `p44` is where that defect was found, using the only working form (normalised disassembly text). |
| p44 | fixed-point arithmetic | overflow, rounding | moderate | ⚠ **REFUSE — PROVISIONAL, UNREVIEWED. `p45`'s verdict reproduced on a second row.** Under the *"caller guarantees no overflow"* contract there is **ONE RUNG**: `k44_plain`, `k44_wrapping` and `k44_unchecked` are **normalised-identical** (67 instructions, one text) and all three read **`12849.00` marginal `Ir`/call**. Under the *"detect overflow"* contract there is **no admissible R4**, and the idiomatic widening spelling makes the bug class unreachable. ⚠⚠ **This row is also what exposed probe 2's SECOND instrument defect — see the probe block.** |
| p45 | saturating / wrapping arithmetic helpers | signed overflow UB — **the UB class is absent from the tree; the HARM is p18's, second instance** | easy–moderate | ⚠ **REFUSED at TASK_080, and it was refused BY ITS OWN PROPOSER.** It is the **first catalogue row an AGENT argued for** (RECAP invited that from TASK_066 with no taker) and the manager took it **because it arrived with its kill-risk probe already run** — then §0 killed it on a ground neither party had named. ⚠⚠ **`p45` HAS NO UNSAFE RUNG WITH A JOB**, and that is the whole finding: under a *"detect overflow"* contract `unchecked_add` **cannot implement it** (the only admissible R4 would price a *bounds* check, i.e. p01's axis, so the bug class would be absent from the pattern's own unsafe rungs — **p31's finding 2 verbatim**); under a *"caller guarantees no overflow"* contract **R2 = R3 = R4 = R5 byte-identical, 0.00 `Ir` apart — the ladder is ONE RUNG.** Measured: `k_plain` and `k_wrapping` are **two symbols on ONE section**, and `k_unchecked`'s own 155-byte section **md5s identically** to `k_plain`'s. See the refusal block below |
| p46 | bignum limb add/mul | limb bound / carry | hard | ✅ **BUILT at TASK_089 as `p46-bignum-mac` — the 24th pattern.** Gate `PASS`, Verus **21/0** (twin 24), `identity` O3 `exact`. ⚠⚠ **THE PROBE'S COST NUMBER WAS WRONG IN SIGN, AND THE RUNG BOUNDARY VANISHED WITH IT.** ~~`+5.05 Ir` per MAC step, +49.6%~~ — shipped, kernel-exclusive `Ir`/call at `-O3 isolated`, **`safe_naive` (6241/23341) < `safe_tuned` (6287/23435) < `unsafe` (6406/24250)**, and **the per-MAC safety tax is `0.00000`.** ⚠⚠ **The cause is NOT `black_box` — that claim was the manager's and is RETRACTED (TASK_089_REVIEW B2): rebuilt with and without it, every probe kernel is BYTE-IDENTICAL.** ✅ **It is the probe kernel's SIGNATURE**, which loses the range facts the shipped kernel derives from its input header; **the shipped kernel proves `i+j < 96` and deletes all three bounds checks.** ⚠ **So a probe can lose the SLOPE, not just the intercept — and the blast radius is RANKED in `.memory/03-measurement.md`: p24 and p26 HIGH, p35 MEDIUM, p23 LOW and robust, p28 not exposed.** ✅ **Sixth instance of the flattering-direction trap, handled correctly:** 3 levers per side, **both degenerate**, and a rolled-vs-rolled control gives **`R2 − R4 = +2.00·n·m` exactly** — **safe Rust's advantage is 100% an UNROLL decision**, derived instruction-by-instruction. ⚠⚠ **AND THE NOVELTY CLAIM THIS ROW WAS SELECTED ON IS FALSE.** ~~*"a value-level postcondition, stronger than any `ensures` in the tree, all of which are bounds facts"*~~ — **counted: 159 `ensures` conjuncts, 151 equalities, so FALSE by 151/159**, and 21 of 24 kernels already carry a full functional postcondition (`controls/census.py --ensures`, committed). **What is actually new is the MODE, not the strength: the first `by (bit_vector)` and first `by (compute)` in the tree, and the first kernel-level nonlinear obligation about DATA rather than an address.** ⚠⚠ **THE HARM IS SILENT IN 6 OF 8 PLAIN C CELLS, and the mechanism is THE ORDER OF TWO AUTOMATIC ARRAYS** — gcc `-O0`/`-O3` and clang `-O3` place `bl[256]` exactly 96 limbs above `out[96]`, so the overflow lands **inside the other scratch**: exit 0, wrong answer, **canary untouched**, and `-fstack-protector-strong` does not help. clang `-O0` reverses them and SIGSEGVs. **p02's heap result, moved to the STACK.** ⚠⚠ **THE `r4_mutreslice` CLAIM IS RETRACTED — IT IS THE `copy_from_slice` FALSE NEGATIVE RECURRING** (TASK_089_REVIEW B1). ~~*"needs a mutable sub-slice the pinned vstd cannot specify — frame provable, value NOT"*~~ ✅ **MANAGER-VERIFIED FALSE: `~/tools/verus/vstd/std_specs/slice.rs` ships `assume_specification<T>[ <Range<usize> as SliceIndex<[T]>>::index_mut ]` with `final(r)@ == final(slice)@.subrange(i.start, i.end)` — a VALUE-LEVEL mutable sub-slice spec** (plus `<[T]>::split_at_mut` and `ref_mut_array_unsizing_coercion`). The engineer read `vstd/slice.rs`'s **`ExSliceIndex` TRAIT DECLARATION** — which does carry a `requires` and no `ensures` — **and mistook it for the specification.** One added `lemma_seq_subrange_index` line makes the value probe verify **2/0**. ⚠⚠ **CONSEQUENCE: `r4_mutreslice` beats the shipped R4 AND every safe spelling by 697…2597 `Ir`/call, so if it is admissible the R4 span is ~2600, NOT 3, and *"both sides degenerate"* fails.** ⚠ **Nobody has yet shown its full R5 closes** — that is now p46's open question and its central framing depends on it. ✅ **Band D earned its place more sharply than p38's missing column: the two axis-aligned bands leave the law UNDERDETERMINED, a one-parameter family fitting both exactly — no in-sample residual could have shown it.** ⚠ **The MATHEMATICAL product is NOT proved** (the algorithm is; `model.py` closes the gap by testing). Evidence: `.tasks/TASK_089_REPORT.md`. **UNREVIEWED.** |
| p47 | constant-time compare / select | **timing side channel.** ⚠ **The catalogue's guess -- *"compiler may reintroduce a branch"* -- is REFUTED** (T064 + T064_REVIEW: 5 accumulate spellings, gcc 13.3 and clang 22.1 at five opt levels, rustc at five, **LTO, PGO trained 100% on mismatch-at-byte-0, AVX2, AVX-512, `__builtin_expect` in three placements, a branching caller** -- `Ir(k=0) - Ir(k=n-1) = 0` **exactly**, with a detector control that fires). **The adversary is the IDIOM, not the optimiser**; the leaking rung is safe Rust's own `a == b` | moderate | **done** (T064), gate `PASS` first complete run, R5 **12/0 first run, no lemma** (twin 13/0), `R4 == R5` `exact` at O3 / `norel` at O0, **TCB 3**, Miri 7/7, additivity extrapolation **80/80 exact**, **reviewed** (T064_REVIEW: 3 majors, 6 minors, **32 clean negatives**; corrections at T065). **The proof certifies a LEAKING kernel**: `m_leak` verifies 14/0 with `kernel`'s obligation count unchanged at 3 and leaks **+7088 `Ir`**, under an **identical contract** -- a property of the TRACE is invisible to a logic about the VALUE |

| p48 | **partially-filled buffer / struct with padding, written out wholesale** | **uninitialised-memory INFO LEAK** — in bounds, live, owned, never written | moderate | ⚠ **REFUSED at TASK_074 — proposed by the manager at TASK_066, attacked by a different agent under rule 3, and the attack landed.** Its distinguishing Verus claim is false (p27 already exercises `is_init`) and its headline **padding** sub-case is **unbuildable here**. **What survives is real but smaller** — see the triage below |

⚠ **`p48` is NEW and it makes this a 48-row catalogue.** `CLAUDE.md` describes
`.memory/06-catalogue.md` as *"the 47-pattern catalogue"*; that phrase is now one
short. Numbers `p01`–`p47` are all used with **no gaps** (checked), so a seventh
axis cannot reuse one.

### p48 — REFUSED at TASK_074. Rule 3 worked; read the refusal before rescheduling.

⚠⚠ **VERDICT FIRST, because everything below it was written BEFORE the
measurements and is kept as the record of a prior that was wrong.**

**This was a manager proposal written while p38's engineer was running, from
source reads and `vstd` greps only — no compile, no measurement** — and
PROTOCOL rule 3 was flagged against it in this file from the day it was written.
At TASK_074 a different agent was given authority to refuse it and **did**, with
measurements. ⚠ **The catalogue's record on bug-class guesses is now three
overturned against two upheld, plus p47 overturning its own row and this one
being refused outright.**

**The three findings that killed it:**

1. **The axis's sole distinguishing claim is FALSE.** *"No pattern in the tree
   exercises that"* — **p27 exercises `is_init()` in four places, including its
   core invariant `slot_ok` (`verus.rs:267`)**, and calls `ptr_ref` at `:620`
   against the same `raw_ptr.rs:623` precondition. Probe: two `precondition not
   satisfied` errors at that exact vstd line. **Manager-verified.** A new
   *clause*, not a new *kind*.
2. ⚠ **The PADDING sub-case — this row's own "real CVE shape" — is
   UNBUILDABLE here, and the reason is structural.** Measured across **3
   padding layouts × 2 compilers × 4 opt levels × 3 DSE defences**: padding at
   offsets 1–7 differs **every run**; at 17–23 and 41–47 it is stable per-level
   but **splits at `-O1`** because DSE deletes the dirtying store before the
   `free`. Making the dirty store live does not fix it — the split just moves to
   clang `-O2`. **A padding byte cannot be written by the program, so the only
   store that can plant a value in it sits adjacent to a `free()`, and the load
   is a load of `undef`.** The obvious fix does not work *and neither does the
   pattern that would demonstrate it*.
3. **It is p08's shape by this file's own test.** The `p31` row three sections
   down demotes p31 in exactly these words — *"which makes it **p08's shape** — a
   tooling-and-expressiveness result the tree already has one of"*. **p48's safe
   rungs cannot express the bug either.** The stated defence, *"unlike p08, the C
   bug is not exotic"*, is about frequency in the wild, **which no rung
   measures.**

✅ **What SURVIVES, recorded so it is not lost:**

- **The V1 sentinel design WORKS**, and it is the reusable part: allocate A,
  write a sentinel, free, allocate B, fill B **partially**, emit B. Checksum
  `07eb3361a6c0a78b` in **40/40** cells (5 runs × 2 compilers × O0–O3), equal to
  an independent model. ⚠ **Two preconditions nobody had stated: the partial
  fill must be ≥ 16 bytes** (to clear glibc's tcache metadata) **and the warm
  read must be NON-CANCELLING** — an XOR fold over two identical warm reads
  cancels, and it did, silently, at `-C opt-level=3` only.
- **"R4 reintroduces it exactly" is UPHELD, 48/48** — gcc, clang and rustc,
  O0–O3, four variants each, every cell on the modelled leak value.
- **MSan fires through `printf` at O0–O3, exit 1, with working origins.**
  ⚠ **But gcc has no MSan and stage 7 is gcc, so it is a CONTROL, not a rung** —
  p36's `cfi-icall` situation exactly.
- ⚠ **A real cost axis exists and THE PRIMARY METRIC MIS-PRICES IT.** LLVM does
  not eliminate a redundant zero-fill (n=4096: identical to 0.01 `Ir` whether
  `k=n` or `k=16`). But the safe−unsafe delta **jumps 6.46× for a 2× increase in
  `n`, at 2048** — glibc's `__x86_rep_stosb_threshold`, where `__memset_avx2`
  switches to `rep stos`. **Callgrind counts a `rep` instruction once per
  repetition, so `Ir` reports the cost RISING 6.5× at exactly the size the real
  cost FALLS.** See `.memory/03-measurement.md`.
- ⚠ **And the tax is INVISIBLE to `kernel_exclusive_ir` — worse than p13.** The
  kernel symbol is byte-for-byte identical between the rungs (44,239,600 `Ir`
  both); the entire difference is 13,112,237 `Ir` inside `__memset_avx2`. **p13's
  kernel column overstated by 190/264 of ~1100. p48's would report the tax as
  exactly ZERO.** This is the third measured instance of that column reversing or
  erasing a comparison.

**If it is ever rescheduled**: V1 only, `FILLK ≥ 16`, non-cancelling warm read,
**drop the padding sub-case from the pitch**, publish whole-program marginal `Ir`
only with the `rep stosb` domain stated, do not sell the R5 obligation as new —
**and build it only AFTER the callee/total `Ir` column exists**, because that is
what makes its cost axis measurable in the project's primary framework at all.

---

**The original proposal is kept below, unedited, as the record of the prior.**

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
  ✅ **UNVERIFIED ITEM CLOSED at TASK_072/073: MSan EXISTS AND WORKS on this box**
  (clang, **including origin tracking**), and **gcc has no `-fsanitize=memory`**
  at all. Probed out of scope by p36's engineer, spot-checked by p36's reviewer
  — both halves reproduce; `.temp/p48probe/NOTES.md`. ⚠ One recorded omission:
  the probe **exits 1** and that was not written down, so read the exit code
  before building an expectation on it. **So p48's catcher story is settled and
  the axis is no longer blocked on tooling.**

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
| **provenance** | ⚠⚠ **THIS ROW'S JUSTIFICATION IS FALSE AND THE AXIS IS REFUSED (TASK_079).** It read: *"the property Miri checks and nothing else does; untested here."* **Measured in the gate's own configuration — default Stacked Borrows, no `MIRIFLAGS`** — a correct raw bump arena is Miri-**clean**; a `usize` round-trip is a **WARNING that runs to completion with the right answer**; `-Zmiri-strict-provenance` says *"unsupported operation"*, i.e. it **refuses to run rather than diagnosing**; and the only thing Miri **errors** on is **aliasing**, which is **p08's already-shipped Miri class**. **Manager-verified** (all three variants re-run). Same failure mode as the `p48` row: the axis's sole distinguishing claim does not survive a grep-plus-run | **p31 — REFUSED**, see the row and the refusal block |
| **INITIALISATION** ⚠ *new at TASK_066* | ⚠⚠ **THIS ROW'S JUSTIFICATION IS FALSE AND THE AXIS IS REFUSED (TASK_074).** It read: *"The Verus obligation is a **new KIND** … no pattern in the tree exercises that."* **p27 exercises `is_init()` in FOUR places** — `verus.rs:267` (a conjunct of `slot_ok`, i.e. **p27's core invariant**), `:575`, `:616`, `:606` (`leak_contents`) — and calls `ptr_ref` at `:620` against **the same `~/tools/verus/vstd/raw_ptr.rs:623` precondition**, giving the same `precondition not satisfied` diagnostic. **Manager-verified.** A new **clause**, not a new **kind** | **p48 — REFUSED**, see the triage |

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
- ✅ **p36 — BUILT at TASK_072/073. THE TRIAGE BELOW IS SUPERSEDED; it is kept
  only because two of its three predictions were WRONG and the pattern of the
  error is the reusable part.** ⚠ **Its headline worry — *"the harm is not
  reproducible"* — is REFUTED: 24/24 SIGSEGV** across gcc/clang × O0–O3 × 3
  opcodes. Its *"likeliest to hit p55's wall"* ranking was wrong. **What it got
  right was the re-triage** (the bar is *"a sanitizer fires deterministically"*,
  not *"the harm is identical"*), and **the question it left UNVERIFIED was the
  one that mattered** — see the p36 row above for what actually fires.

  **Historical triage, superseded:** *"An out-of-table
  indirect call jumps to whatever is adjacent, so the harm is not
  reproducible, and there is no equivalent of the fold-from-offset-16 trick
  that rescued the UAF. Settle reproducibility first, the way TASK_055 had to."*

  > ⚠ **PROVISIONAL — manager read of the harness, not yet reviewed; rule 3
  > applies.** Read at TASK_066 time, source-only. **This row's own citation was
  > wrong and its risk is overstated.**
  >
  > - **`check.py:1249` is not the checksum rule** — it is a selftest for
  >   `idiom_problems` ("a bare string is not a declaration"). The real rule is
  >   **`check.py::check_checksums`** (stage 2). ⚠ **This bullet originally
  >   pointed at `:1440-1476` and THAT ROTTED TOO** — by TASK_071 those lines
  >   were inside `idiom_lines`. A line number written against a file that has
  >   gone 5100 → 7037 lines drifts every time: **cite the function, and only the
  >   function.** The "line as a hint" compromise was tried at TASK_066 and
  >   **retracted at TASK_071 after every hint rotted inside one session.**
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
- ⚠ **p31 — REFUSED at TASK_079. THE TRIAGE BELOW IS SUPERSEDED**, and it is kept
  because **its verdict was right and every clause of its reason was wrong**,
  which is a more instructive failure than p36's.

  **Historical triage, superseded:** *"**p31 (provenance) — demote it.** Miri is
  the only checker, which is fine (it is already gate stage 8), but the expected
  shipped-compiler behaviour is nothing observable, which makes it **p08's
  shape** — a tooling-and-expressiveness result the tree already has one of.
  Build it for provenance only if a pattern is wanted whose whole finding is a
  tooling claim."*

  **Wrong in three places, each measured:** *"Miri is the only checker"* is false
  (see the axis row — Miri **warns** and does not diagnose); *"nothing
  observable"* is **half false** — gcc 13.3.0 at `-O2`/`-O3` **does** exploit
  provenance, and the mechanism is exact — and the half that is true is true for
  a reason the triage never gave; and *"p08's shape"* understates it, because
  **p08 at least has a harm that executes** and p31's arena shape has none.

  ### p31 — the refusal, in four findings

  ⚠ **Two refusals in a row now share finding 1: the axis's own justification was
  false and one `grep` plus one run settled it.** That is a pattern in the
  *manager's* triage, not in the catalogue's rows.

  1. ⚠ **`PointsToRaw::split`/`join` is a new CLAUSE, not a new KIND** — p48's
     objection 2 verbatim, and p31 fails it identically. This was the call the
     manager named as least certain, and the whole prover half of the pattern
     rested on it. The **full** arena chain — `allocate` → `expose_provenance` →
     loop{`split` → `into_typed` → `with_exposed_provenance` → `ptr_mut_write` →
     `tracked_insert`}, with a 6-conjunct loop invariant — verifies
     **`6 verified, 0 errors`** with **zero lemmas, zero `by(nonlinear_arith)`,
     zero set-theory lemmas**. `split`'s own `range.subset_of(self.dom())` and
     `into_typed`'s `is_range` discharge with **no ghost help at all**.
     ✅ **Manager-verified** (re-ran `./verus_run.py` on the probe).
     **p31's proof is SMALLER than p27's**, which is 15/0 over two Maps.
     ✅ *Clean negative, and it is the honest version of the manager's sentence:*
     the genuinely unused vocabulary is
     **`expose_provenance` / `with_exposed_provenance` / `IsExposed`** (0 hits
     across `patterns/`, `harness/`, `common/`), and it is **forced** — the
     pinned vstd's `raw_ptr` has **no exec pointer-offset function at all**, so
     an exec bump allocator either threads an `IsExposed` token or adds a
     project-local `external_body` offset wrapper (+1 TCB). **But the token
     threads exactly like p27's `Dealloc`.** Same answer.
  2. ⚠ **THE CONTROL DOES NOT EXIST, and this is the finding to carry forward.**
     gcc `-O2`/`-O3` exploits the one-past-end/representation-equal shape — a
     load hoisted **above a store to the identical address**, confirmed in the
     disassembly — but **15 gcc flags all leave it exploited**
     (`-fno-tree-pta`, `-fno-ipa-pta`, `-fipa-pta`, `-fno-strict-aliasing`,
     `-fwrapv`, `-fno-strict-overflow`, `-fno-tree-fre`, `-fno-tree-dse`,
     `-fno-tree-vrp`, `-fno-tree-pre`, `-fno-aggressive-loop-optimizations`, …).
     ✅ **Manager-verified on 9 of the 15.**
     **p38 could ship because `-fstrict-aliasing`/`-fno-` makes its claim
     falsifiable. Provenance has no such lever** — and TASK_079's task file named
     *"the control that shows it is real is missing"* as itself a finding. It is.
  3. **The arena's own shape is CLEAN, 24/24.** Sub-objects carved from one
     allocation legitimately share its provenance; the exploitable shape needs
     **two distinct top-level objects that happen to be adjacent**, which is a
     two-static-`int` demonstration kernel and not an allocator. ✅ Manager-seen
     in the flag sweep (s4 prints the defined answer in every configuration).
     **So the bug class is absent from p31's own kernel.**
  4. **Triple duplicate, confirmed, and worse than the manager's guess.**
     *alignment* → **p18's shape with NO harm at all on x86-64** (16/16 cells
     correct, both compilers emitting unaligned SIMD) — though ⚠ **its catcher
     `-fsanitize=alignment` IS in-matrix**, unlike p18's four, so the manager's
     objection was wrong in that direction too. *exhaustion* → ⚠ **not "the
     thirteenth `index >= len`"** (the manager's armchair claim) but **p12's
     mechanism and p04's harm**: `p12` *is* a bump allocator over a `char` array
     whose `dlen` is a program-computed loop-carried cursor, and `p04` is
     *"the first kernel with two live cursors, and the first whose bug stays in
     bounds"* — p31's exhaustion harm verbatim. ✅ Manager-verified against
     `.memory/01-ladder.md`. **p36's escape hatch does not apply**: p36 shipped
     with a duplicate bug class because its *mechanism*, *catcher* and *prover*
     stories were each new; p31's mechanism is p12's, its prover story is p27's
     minus a Map, and its catcher story is finding 1 of the axis row.

  ✅ **What SURVIVES, and one item is a live trap for any future pattern:**

  - ⚠⚠ **BOTH gcc `-O2` AND clang `-O2` DELETE A NON-ESCAPING `malloc`/`free`
    PAIR ENTIRELY.** Measured `2.00 Ir/object` for a malloc rung whose
    disassembly contains **zero** `malloc`/`free` call sites; with
    `-fno-builtin-malloc -fno-builtin-free` (2 call sites on both compilers) the
    true figure is **140.00**, against the arena's **10.00** — a **14×** saving
    the naive measurement reports as a **7× loss**. ✅ **Manager-verified on both
    compilers.** **Any pattern that puts allocation in the kernel must defeat
    that elision or its C rung measures nothing.** Full entry in
    `.memory/03-measurement.md`; it is the p31 analogue of p48's `rep stosb`
    trap and **cheaper to hit**.
  - **The cost axis is real and large and is NOT a safety number.** `140 → 10` is
    R1-against-R1: the *algorithm* changed, not the safety level. The ladder's
    actual safe-vs-unsafe question here is **+7.00 Ir/object** (safe `Vec<u64>` +
    index against unsafe raw bump), **one lever on each side, unsearched** — a
    bounds check on an index, the thing the tree has measured twelve times.
  - **gcc accepts `-fsanitize=pointer-overflow` and links
    `__ubsan_handle_pointer_overflow`** (✅ manager-verified) — see
    `.memory/00-environment.md` for what it then fails to catch.

⚠ **THE AXIS PROGRAMME IS CLOSED, and this is the state to hand over.** The axis
table has **seven** rows and every one is now resolved: **5 BUILT** (p27
lifetime, p47 timing, p38 weaponised UB, p36 CFI, p22 termination) **+ 2 REFUSED
WITH MEASUREMENTS** (p48 at TASK_074, p31 at TASK_079). ⚠ **So this table is no
longer the thing to consult for what to build next** — it was the reason
axis-first ordering beat family-first ordering, and that argument has now been
spent. **Derive the count rather than trusting this paragraph:** the table rows
are between the *"missing axis"* header and the *"Recommended order"* line, and
`ls -d patterns/p*/` says which exist.

## ⚠⚠ THE LADDER TEST — run it before writing a task file. Three rows in a row died on it.

**Manager rule, adopted at TASK_080 after three consecutive refusals — and
⚠⚠ ITS FIRST HALF WAS RETRACTED AT TASK_081_REVIEW, ONE TASK LATER, AS A
BLOCKER.** `p48`, `p31` and `p45` were each refused, and the refusals were each
*correct and cheap*. They share a cause none of the three triages tested, and it
is **not** *"is the bug class new?"* — that part stands. **The manager's first
attempt to state the cause did not.**

⚠ **RETRACTED, and it is kept because HOW it was wrong is the useful part:**

> ~~**A PATTERN NEEDS A BUG THAT R4 CAN REINTRODUCE AND R3 CANNOT, AND A COST
> THAT DIFFERS BETWEEN THEM.**~~

**It misclassifies two of the project's own reference patterns, in OPPOSITE
directions, and it contradicts the table three lines below it:**

- ⚠ **`p08` SATISFIES it and shipped as finding 7.** Its bug is an overlapping
  `memcpy`: R4 reintroduces it via `copy_nonoverlapping`, and safe Rust **cannot
  express it** — the borrow checker rejects it at compile time. That is the first
  half met exactly, while this block's own table cites *"R3 cannot express it"*
  as `p48`'s **failure**. **The table means the KERNEL; the rule says the BUG.**
- ⚠ **`p47` VIOLATES it and shipped.** Its timing leak **is reintroducible in
  safe Rust** — `safe_naive` is one of the leaking rungs — so *"R3 cannot"* is
  false for p47.
- ⚠⚠ **AND THE MANAGER'S OWN STATED WORRY WAS AIMED AT THE WRONG HALF.** The
  manager predicted p47 would fail the **cost** half. ✅ **Measured, it passes
  comfortably: `R3 − R4 = +90.0 / +142.0 `Ir`/call`** (`safe_tuned` 524.0/747.7
  against `unsafe` 434.0/605.7, O3/isolated, manager-re-run from
  `results/gate/p47-ct-compare.json`). **The half the manager defended is the half
  that was wrong.**
- **The cost half never says WHICH `Ir` CONVENTION**, and both are defined. On
  p08 the level difference is **+26.02/+26.00** (differs) and the slope
  difference is **5.6e-6** (does not) — **opposite verdicts from an unstated
  choice.**

How each row failed, restated against probe 1 below:

| row | what was missing | the measurement that showed it |
|---|---|---|
| `p48` | **no rung boundary in the KERNEL** — safe Rust needs `set_len`, i.e. `unsafe`, to reach the residue at all, so R3 has nothing to build | the padding sub-case is unbuildable across 3 layouts × 2 compilers × 4 opt levels |
| `p31` | **no boundary anywhere** — an arena's carve is *correct* C, so no rung differs | the arena shape is provenance-clean **24/24** |
| `p45` | **the rungs are the same machine code** | `k_plain` and `k_unchecked`, 155 bytes each, both `85bd268b3def0d5e386f1498706a6b2b` |

⚠ **The novelty question is the one the triages DID ask, and it is the less
useful one.** `p36` shipped with the tree's **twelfth** `index >= len` and was
worth building; `p45`'s UB class is **genuinely absent** from the tree and was
not. **Novelty of the bug class predicts neither way. The ladder test does.**

⚠ **And it is cheap — cheaper than the triage prose it replaces.** Each of the
three failures above is one compile plus one `md5sum`/`objdump`/run. **Write the
probe before the row, not before the task**, which is the same lesson RECAP's
time-waster 4 draws about novelty claims: *both* of the manager's axis proposals
were argued from source reads with nothing run.

⚠⚠ **THE HALF OF THE TEST NOBODY HAD, AND IT IS A GATE BLIND SPOT: a pattern
whose rungs are ACCIDENTALLY BYTE-IDENTICAL is indistinguishable from a pattern
where safety is genuinely free.** p45 could have shipped as a green 23rd pattern
by taking the *"caller guarantees no overflow"* contract and never running
`readelf` — every rung agrees on every checksum, the gate passes, and the
published **`R3 − R4 = 0.00`** reads as *"safety is free"* when the truth is
*"there is only one rung here"*.

> **`R5 − R4 = 0.00` is already scoped as a TAUTOLOGY** in `results/synthesis.md`,
> because the `identity` pin forces it. ⚠ **NOTHING scopes `R3 − R4 = 0.00` the
> same way, and no gate stage looks.**

### The three probes. Run them BEFORE the row is written.

**Restated at TASK_081_REVIEW after the first attempt was retracted above.**

**1. A rung boundary must exist somewhere, and the row must NAME it.** ⚠ **Not
necessarily R3-vs-R4** — that assumption is what broke the first version. p08's
boundary runs at **compile time** (R2/R3 cannot express the bug, R4 can); p47's
runs **inside the safe class** (idiom against idiom); p16's is a **slope**, not a
level. **What is fatal is no boundary ANYWHERE**, which is p31.

**2. The rungs must differ AS MACHINE CODE, and this is checked, not argued.**
⚠ **The earlier *"two rung symbols on ONE section index"* form CANNOT FIRE on a
shipped pattern** — in this project **every rung is its own binary**
(`harness/build.py`), so no binary ever holds two rungs' kernels. That form
applies to a **probe object file**, which is what p45's was. The form that
transfers:

```bash
# per rung binary: kernel symbol's Ndx and Size from -sW, section file offset
# from -SW, then md5 the extracted bytes
readelf -sW <bin> ; readelf -SW <bin>     # -> (offset, size) for the kernel
md5sum <extracted kernel bytes>            # collide => the pattern is ONE RUNG
```

**A collision is what would have caught p45.** ⚠ **And it does NOT false-positive
on p16**, which was the worry: p16's shipped kernels are **410 bytes /
`0b8c64b6…` against 324 bytes / `7952ec0b…`** — different, while `unsafe ≡ verus`
collides exactly, as the `identity` pin requires.

⚠⚠ **BUT ON AN OBJECT FILE IT DOES FALSE-POSITIVE, AND IT PRODUCES EXACTLY
p45's VERDICT. LINK FIRST, OR READ `readelf -rW`.** (TASK_086 #238. ✅
**MANAGER-VERIFIED on an independent minimal case**, `.temp/mgr86/reloc.rs` +
`README.md`, which rebuild it.) **A relocated field is ZERO in the object file**,
so two kernels differing *only* in **which function they call** — or in a global
address, or a jump-table base — **md5 identically there and differ once
linked**:

```
 .o     k_calls_a  d96e2a3350186ba3f3e7f13dcde2fe2e
 .o     k_calls_b  d96e2a3350186ba3f3e7f13dcde2fe2e   <- IDENTICAL
linked  k_calls_a  9fd9563c2de5747d7883758f234d8b5c
linked  k_calls_b  9a346d637748fbb3640af34ec205e7ba
```

TASK_086 hit it for real on `k24_heapify_checked`/`_unchecked` (62 B, identical
in the `.o`; 58 B and distinct linked). ⚠ **This matters because probe 2 is a
KILL criterion and the object-file form is what a cheap pre-check reaches for** —
`TASK_083_REVIEW`'s p15 probe said so explicitly.

✅ **What it does NOT disturb, both checked:** **p45's kill stands** — its
`k_plain`/`k_unchecked` are **leaf arithmetic folds over `&[i32]` with no call
and no global**, so they carry no relocations to hide a difference in. And
**p15's refusal stands** — a false-*positive* collision mode cannot turn a PASS
into a FAIL, and p15's probe 2 **passed** (206 B vs 146 B).

⚠ **AND THE FIRST ATTEMPT TO VERIFY THIS WAS WRONG AND LOOKED RIGHT.** In an
object file each `#[inline(never)]` function sits at **address 0 of its OWN
section** (`.text.k_calls_a`, `.text.k_calls_b`), so extracting *by address*
returns the same bytes for both **by construction** and prints a collision that
means nothing. **Extract per SECTION — `objcopy -O binary --only-section=.text.<sym>` —
never by address, in a `.o`.**

⚠⚠ **AND THE LINKED FORM HAS THE OPPOSITE DEFECT. `TASK_086` FIXED ONE END AND
OPENED THE OTHER — PROBE 2 IS NOW KNOWN BROKEN IN BOTH DIRECTIONS.** (TASK_094
#265, **PROVISIONAL — unreviewed**, but the mechanism is structural.) Measured on
three kernels that are **provably the same program** — `a[i] * b[i]` at `-O` with
debug-assertions off **is** `wrapping_mul` by Rust's own definition, and
`unchecked_mul` emits the same `imul`:

```
LINKED binary, the form this block prescribes:
k44_plain     size=270 md5=170cc7c2…
k44_unchecked size=270 md5=5b06d19b…   <- reported "a different rung"
k44_wrapping  size=270 md5=e14bf3de…   <- reported "a different rung"
```

The **complete** list of differing disassembly lines is **7 self-relative jump
targets** (each printing its own kernel's name), one `lea 0x…(%rip)` to a panic
string and one `call *0x…(%rip)`. **67 instructions each, identical mnemonic
multiset.**

> **In a linked binary every kernel sits at its own address, so every `jXX`
> displacement and every `%rip`-relative reference differs BY CONSTRUCTION. ANY
> KERNEL CONTAINING A BRANCH OR A GLOBAL REFERENCE CANNOT COLLIDE, AND PROBE 2
> PASSES VACUOUSLY.**

✅ **`p45`'s kill still stands, for the reason `TASK_086` already gave** — its
`k_plain`/`k_unchecked` are leaf arithmetic folds with **no call, no global and
no branch**, and its md5s were of the **object file**, where per-function
sections start at address 0. ⚠ **That is the ONLY shape the md5 form can catch.**

**THE FORM THAT WORKS IS NORMALISED-DISASSEMBLY TEXT.** Strip the address
column, self-relative targets, `%rip` displacements and `objdump`'s `#`
comments, then compare the *text* (`.temp/t94/knorm.py`):

```
k44_plain     insns=67 mnemonic-multiset=f815d5d3b2f4 normalised-text=fed7c19bd69d
k44_wrapping  insns=67 mnemonic-multiset=f815d5d3b2f4 normalised-text=fed7c19bd69d
k44_unchecked insns=67 mnemonic-multiset=f815d5d3b2f4 normalised-text=fed7c19bd69d
  -> ONE RUNG
```

✅ **Independently corroborated by probe 3**: under a fixed driver all three read
**`12849.00` marginal `Ir`/call, identical to the unit.**

⚠⚠ **AND `knorm.py` ITSELF HAS A DEFECT — THE THIRD ONE FOUND IN PROBE 2, AND
THIS ONE FAILS ON THE KILL SIDE.** (TASK_102, PROVISIONAL.) **It counts
inter-function alignment padding as instructions**, so it reported a pair that is
**literally the same program** (`k_double_fetch` vs `k_single_fetch`, CSE'd to
one load) as **24 vs 22 insns, `!=`.** ⚠ **A FALSE NEGATIVE ON A KILL CRITERION
IS THE DANGEROUS DIRECTION: probe 2 saying "these differ" is what KEEPS a row
alive, so this defect manufactures rungs that do not exist.** The two earlier
defects were false-*positives* on relocations and false-*negatives* on linked
md5; **this is a third, in the form that was supposed to be the one that works.**
✅ **Four-line fix in `.temp/t102/b4_norm.py`** — stop at the function's own
extent instead of running into the next symbol's padding.
⚠ **Every probe-2 result taken with `knorm.py` on a kernel whose symbol is
followed by padding is suspect until re-run with the fix.** `p44`'s numbers above
are **not** affected — all three read `insns=67` and the same normalised text, so
the padding term is common to all three and cancels.

⚠⚠ **AND A FOURTH DEFECT, ALSO IN THE KILL DIRECTION — FOUND AT TASK_104 IN THE
FIX FOR THE THIRD.** Both `.temp/t94/knorm.py` **and** `.temp/t102/b4_norm.py`
rewrite a self-relative branch target `<kernel+0x91>` to **`<SELF>` and DISCARD
THE OFFSET**. So **two kernels that differ only in WHICH OF THEIR OWN LABELS a
branch targets normalise identically** — which is exactly `p42`'s leaking-vs-
hardened C pair, reported as **one rung** when they are two. ✅ **Fix: keep
`<SELF+0xNN>`** (`.temp/t104/probe2.py`).

⚠⚠ **AND A FIFTH DEFECT — FOUND AT `TASK_113`, PROVISIONAL, AND IT IS A
REGRESSION THE TWO SUCCESSOR TOOLS BOTH INTRODUCED.** **A pure
instruction-SCHEDULING permutation reports `!=`**: clang's `k_cast_sum` and
`k_memcpy_sum` are **40 instructions with the same mnemonic multiset and one
`xor` moved**, and normalised-disassembly text calls them different. ⚠ **The
column that catches this — the MNEMONIC MULTISET — existed in `.temp/t94/knorm.py`
and was DROPPED by BOTH `.temp/t102/b4_norm.py` and `.temp/t104/probe2.py`.**
⚠⚠ **So the fix for defect 3 and the fix for defect 4 each silently removed the
check that would have caught defect 5** — the same shape as defect 4, which was
found *inside* the fix for defect 3. **Compare the multiset as well as the text.**

⚠⚠ **AND A SIXTH — IN THE VERY TOOL THIS BLOCK RECOMMENDS.** (`TASK_115`,
PROVISIONAL.) **`.temp/t104/probe2.py` truncates the kernel at the LAST `ret`
in the symbol**, which on `p26`'s kernels **cuts 146 of 177 instructions.**
⚠⚠ **So the fix for defects 3 and 4 — the form this file tells the next agent to
use — is itself a false negative on any kernel with an early return.** **Take
the symbol's own extent from the ELF symbol table; do not scan for a terminator.**

⚠⚠ **PROBE 2 HAS NOW BEEN WRONG SIX TIMES, AND FIVE OF THE SIX WERE
FALSE-NEGATIVES ON THE KILL CRITERION** — object-file md5 false-**positives** on
relocations; linked md5 false-**negatives** on any kernel with a branch or a
global; `knorm.py` counting inter-function padding; `<SELF>` discarding the
offset; a scheduling permutation reading as a real difference; and truncation at
the last `ret`. ⚠ **A false negative here KEEPS A ROW ALIVE that has no rung
boundary, or MERGES two rungs that are genuinely different. Before trusting any
probe-2 "these are the same", disassemble both and look.**
⚠⚠ **THE HONEST SUMMARY IS NOW THIS: EVERY VERSION OF PROBE 2 THAT HAS EVER
BEEN WRITTEN HAS BEEN WRONG, AND THREE OF THE SIX DEFECTS WERE INTRODUCED BY A
FIX FOR AN EARLIER ONE.** ⚠ **It decides whether a candidate row has two rungs or
one, i.e. whether a pattern gets built at all. Treat any single probe-2 reading
as a hypothesis, and confirm a KILL by disassembling both kernels by hand.**
⚠⚠ **AND THE META-FINDING IS NOW THE MORE USEFUL ONE: THREE CONSECUTIVE FIXES TO
THIS PROBE EACH INTRODUCED OR EXPOSED THE NEXT DEFECT.** **A probe that has been
wrong five times, twice inside its own repairs, is not a thing to trust on a
single reading** — and probe 2 is the instrument that decides whether a
candidate row has two rungs or one, i.e. whether it gets built at all.

**4. DOES THE ROW'S UNSAFE OPERATION HAVE A `vstd` SPEC — AND THE GREP IS
NECESSARY, NOT SUFFICIENT.** (Added TASK_086; the caveat is its finding #239,
**PROVISIONAL — unreviewed**.) `check.py::_scan_unsafe_sites` requires every
`unsafe` token in a pinned Verus source to sit inside an `external_body` item, so
a row whose R4 operation vstd *does* spec cannot put the Verus-discharged call in
a **verified** fn — that is exactly why **p15 is refused**. Measured across the
tree: **47 `unsafe` tokens in 22 `patterns/*/verus.rs`, all inside wrappers**,
and `grep -rn "get_unchecked" ~/tools/verus/vstd/` → **0 hits**, so every
existing wrapper was unavoidable.

⚠ **So grep `~/tools/verus/vstd/` — the PINNED one — for the operation, and grep
the INHERENT spelling as well as the free one** (`core::str::from_utf8_unchecked`
is `is not supported` while `str::from_utf8_unchecked` verifies `2/0`).

⚠⚠ **BUT A MISS DOES NOT MEAN "ordinary wrapper route", AND `p35` IS THE
COUNTER-EXAMPLE.** The Rust `union` keyword is **not in vstd at all** — 318 hits
for `union` are every one of them `Set::union` — and p35 is blocked by
`_scan_unsafe_sites` **anyway**, because Verus supports `union` **natively**: the
correct-variant obligation is **first class in the type system** (`requires v is
i` takes it from `1 verified, 1 errors` to **`2 verified, 0 errors`**), and the
read is still `unsafe { v.i }` inside a **verified** fn.

**The test that actually decides it is not the grep. It is: DOES AN `unsafe`
TOKEN END UP INSIDE A VERIFIED BODY?** Run the rule itself —
`.temp/t86/scan_unsafe_probe.py` drives HEAD's `_scan_unsafe_sites` against a
candidate source and prints `host=NONE -> rep.fail(tcb-unsafe)`.

**3. Any published `0.00` must name its AXIS and its CONVENTION in advance.**
Which axis carries the finding when the cost gap is zero — behaviour matrix, TCB,
compile-time expressiveness, or a **slope** rather than a level — and which `Ir`
convention the zero is stated in. **p47 knew that going in; p45 did not**, and
could have shipped `R3 − R4 = 0.00` as *"safety is free"*.

⚠ **A note on p16, because this block previously got it wrong.** p16's headline
zero is a **per-byte rate**; its **level** difference is **+27.0 / +77.0**. And
*"the bodies are mnemonic-identical"* is **not** true of p16's shipped kernels —
p16's own `NOTES.md` says the shipped pair is *"23 instructions on each side, the
same multiset, a different order"*. The mnemonic-identity claim is about the
**chunk-loop body at matched fold spellings**, which is a narrower thing.
**A zero with a named axis and a mechanism is a finding; a zero because two rungs
compiled to the same bytes is an artefact — and only probe 2 tells them apart.**

### p15 — REFUSED at TASK_085 / TASK_085_REVIEW. ⚠ **A DIFFERENT KIND OF REFUSAL, and it names its own unblocking condition.**

⚠⚠ **Do not file this beside p48/p31/p45.** Those three were refused because
their **distinguishing justification was false a priori** and one `grep` plus one
run would have settled it. **p15's probes all PASSED** — a named rung boundary,
non-colliding machine code (206 B vs 146 B), a declared cost axis — and **its
named kill-risk closed.** It is refused because the justifications were
**measured away**, and because the shape worth building is the shape **this gate
cannot audit**.

**✅ WHAT WAS BUILT AND MUST NOT BE LOST — a verified UTF-8 validator at the
pin.** `fn is_valid_utf8(b: &[u8]) -> (res: bool) ensures res ==
valid_utf8(b@)` — the **bidirectional `==`** — **`5 verified, 0 errors`, ~120
lines (~10 proof), ZERO trusted items**, on three vstd lemmas
(`partial_valid_utf8_extend`, `partial_valid_partial_invalid_utf8`, and
`partial_valid_utf8` as the loop invariant). The **end-to-end call site**
verifies **`8 verified, 0 errors`**, discharging `vstd/string.rs`'s
`requires valid_utf8(v@)` **from the validator's postcondition alone**.
⚠ **The source is EMBEDDED VERBATIM in `.tasks/TASK_085_REPORT.md`'s final
section**, `sha256 593b25e0…`, because **`.temp/` is gitignored and a refused row
has no pattern dir to put a generator in** — every `.temp/t85/` path cited
anywhere is absent from a fresh clone. `.temp/t85/rebuild.sh` still re-derives
the binaries **on this box only**.

**Non-vacuous three ways, and the third is the one to copy:**
an unmediated differential oracle against `core::str::from_utf8` —
**18 499 985 cases, 0 mismatches**, plus **316 602** independent reviewer cases
including the `F4 90 80 80` boundary the probe's alphabet missed; a **10-mutant
battery, all 10 failing**, three of which break only the **completeness**
direction; and ⚠⚠ **a measured vacuity control: `ensures res ==> valid_utf8(b@)`
with body `false` verifies `2 verified, 0 errors`.** **The `==` bar is
load-bearing — a one-directional bar certifies a validator that rejects
everything.**

**THE THREE JUSTIFICATIONS, EACH MEASURED AWAY:**

1. ⚠ **The harm row is REFUTED.** `TASK_083_REVIEW` published the truncated-lead
   cell as *"prints nothing, exit 0, no bounds violation"* — *"the optimiser
   deleted the program's own `println!`"*. Measured on a byte-for-byte replica of
   that review's **own** file: **`exit 139` (SIGSEGV)**, 30/30 runs across `-O`,
   `-O1`, `-O2`, `-O3`, `±codegen-units=1`, `±debug-assertions` and nightly; and
   **ASan reports `heap-buffer-overflow READ`**. ✅ **Reproduced independently by
   the reviewer AND by the manager.** So it is an ordinary out-of-bounds read,
   **an `index >= len`** — ⚠ **and it would have been the tree's THIRTEENTH, not
   its fourteenth, because TWELVE BUILT patterns carry that class and p36 is the
   twelfth** (TASK_086 #240; the 13th and 14th an earlier count reached were
   `p45`'s and `p15`'s **own would-be ones, both REFUSED rows that were never
   built**). **Count BUILT patterns.** The new harm class does not
   exist. **Two rows have now claimed that class and neither had it** (p45 was
   the other).
2. **What survives is row 1 — an invalid *continuation* byte gives a silent
   wrong answer, `len=4 fold=100507`, exit 0, Miri CLEAN. That is p18's harm,
   and p18's harm is what killed p45.**
3. **The cost result survives and is real, but it is p11's, a fourth time.** A
   verified validator is **dearer than `core::str::from_utf8` at every
   alphabet — `+57%` on pure ASCII, `+7%` on all-non-ASCII** (73756 vs 46921 and
   87661 vs 81960 marginal `Ir`/call; **whole-program marginal, `-O3`, inline
   mode `isolated`**). Mechanism: std validates ASCII at **0.449 `Ir`/byte**
   against the verified validator's **7.001** — the word-at-a-time fast path.
   ⚠⚠ **DO NOT QUOTE `15.58×`** — it is a **residual ratio dressed as a rung
   ratio**, both terms being differences against a control that is neither rung
   (TASK_085_REVIEW major 3). ⚠ **And do not quote the OLS slopes** (`R3
   +384.78 / A +191.18` `Ir`/call per point): the curve is strongly concave —
   1210 `Ir`/pt over 0→10 against 129 over 75→100 — and the fit is off by
   **−7210 at pct = 0, exactly where the headline lives.**

**⚠⚠ THE REAL REASON, WHICH IS ABOUT THE GATE AND NOT ABOUT p15.**
`check.py::_scan_unsafe_sites` requires every `unsafe` token in a pinned Verus
source to sit inside an `#[verifier::external_body]` item. p15's interesting R5
puts a **Verus-discharged** `str::from_utf8_unchecked` inside a **verified** fn.
The two shapes available are both bad:

- **Comply** → the *proved* call moves into the *trusted* column, and the
  `#[cfg(slb_twin)]` twin is **unwritable** (`grep -rn "from_utf8"
  ~/tools/verus/vstd/` returns **one** line, the unchecked one) ⇒
  `PASS-WITH-BLOCKED-ROWS` **on the row that IS the pattern**, and p15 becomes
  the **23rd instance of a wrapper the tree already has 45 of**.
- **Soften the rule** → the gate certifies `TCB 0`, `axioms 0` and *"Miri not
  required"* over a proof whose executed call rests **entirely on a vstd
  axiom** — because `_axiom_items` matches **declarations** and a *used*
  `assume_specification` declares nothing. **RECAP "Owed" 0's sixth route, on
  the one row that exploits it.**

✅ **Clean negative that makes this a finding rather than a complaint:**
`grep -rn "get_unchecked" ~/tools/verus/vstd/` → **0 hits**, so **all 47 existing
`unsafe` tokens are inside wrappers that were unavoidable, and this rule has cost
the project nothing to date.** **p15 is the first row where vstd actually specs
the operation, which is exactly why it is the first row the rule bites.**

⚠⚠ **THE UNBLOCKING CONDITION, NAMED: reschedule p15 the day `_axiom_items` can
see a USED vstd `assume_specification`.** Until then, softening
`_scan_unsafe_sites` is **not** *"preferring a pattern over hardening the gate"*
(PROTOCOL rule 5) — **it is un-hardening the gate on the one row that exploits
the gap.**

⚠ **And a live precedent for choosing identity over a smaller TCB:**
`patterns/p27-handle-table/NOTES.md:686-705` records a **built, verified,
measured** vstd-pure control (`r5_vstdpure.rs`, `15 verified, 0 errors`) with
**two fewer trusted items**, **rejected because R4-vs-R5 measured `differ`.**

**Full evidence:** `.tasks/TASK_085_REPORT.md` and
`.tasks/TASK_085_REVIEW_REPORT.md`; scratch `.temp/t85/` and `.temp/r85/`, both
with `rebuild.sh`.

### p45 — REFUSED at TASK_080. Read this before rescheduling it.

**The two contracts, and both collapse** (`.temp/p45pat/NOTES.md`, re-runnable
via `repro.sh`):

- *"the kernel detects overflow"* → **`unchecked_add` cannot implement it.** The
  only admissible R4 prices a **bounds** check, which is p01's axis, so p45's own
  bug class would be **absent from p45's own unsafe rungs** — the shape that
  refused `p31`.
- *"the caller guarantees no overflow"* → **R2 = R3 = R4 = R5, byte-identical.**
  `readelf -sW`: `k_plain` and `k_wrapping` are two symbols on **one** section;
  `k_checked`/`k_overflowing` likewise; `k_unchecked` has its own section whose
  155 bytes **md5 identically** to `k_plain`'s. **0.00 `Ir` apart.**

⚠ **AND THE C SIDE IS THE SAME STORY: the UB buys 0.00.** Signed `k_plain` (UB)
against unsigned `k_wrapu` (defined), jump targets normalised, are **identical
instruction-for-instruction** at gcc `-O3`, clang `-O2` and clang `-O3`; gcc
`-O2` differs in **one operand order** at the same `Ir`.

⚠ **The manager's own objection 1 was REFUTED AS STATED, and it owed a
disassembly.** The manager proposed the class was *"the optimiser deleting the
programmer's own check"*. Measured over **six guard spellings in the same fold**:
**gcc never deletes any of them, at any level, with or without `-fwrapv`**;
clang deletes **2 of 4** from `-O1`. The manager-verified
`-2147483645`-at-`-O2`-on-both is a property of the **scalar helper**, not of the
fold p45 would ship. **So the harm is a wrong value, ASan-silent — p18's harm,
second instance** — and it becomes a bounds bug only by bolting an allocation on,
at which point it *is* the thirteenth `index >= len`. **Both branches of the
objection land.**

**p36's three grounds for shipping a duplicate bug class: 0 of 3.** Prover story
weaker than p36's and already owned by p18; catcher ordinary and free (**the
absence of a problem is not a finding**); no `Ir`-structure or non-data-harm
story.

✅ **What SURVIVES, recorded so it is not lost:**

- **The overflow-detection tax, and it does NOT amortise.** Kernel-exclusive
  `Ir`/element at `-O3`: C `k_builtin` (`__builtin_add_overflow`, the correct
  hardened idiom) **7.00 gcc / 5.00 clang** against `k_plain` **1.25 / 0.875**;
  the self-referential guard costs **11.00 on both**. In Rust `k_checked` and
  `k_overflowing` are **7.00** and `k_saturating` **7.50** against
  `k_plain`/`k_wrapping`/`k_unchecked` at **0.875**. ⚠ **PROVISIONAL — one fold,
  n = 2²⁰, no sweep and no fitted law.**
- ⚠ **`checked_add` against `wrapping_add` is 8.0×, i.e. 87.5% of the kernel —
  the largest single fraction this project has measured** — and it is
  **safe-against-safe**, so it is not a safety number at all. **PROVISIONAL, one
  fold, unswept.** It is the strongest reason someone will want to reschedule
  p45; the reason not to is that **no rung boundary runs through it.**
- **Does `nsw` ever pay? Yes — on the INDUCTION VARIABLE, never the
  accumulator.** `nsw_2d` at gcc `-O3` is 75 instructions → **28 with `-fwrapv`**
  (it de-vectorises); clang goes 62 → **112**. And the `size_t` spelling is
  `-fwrapv`-immune and **13 instructions smaller** than the `int` one at clang
  `-O3`. ⚠ **That is p05's kernel and p05's axis**, not a new pattern — but it is
  the first measurement in the tree of what signed-index UB buys the vectoriser.
- ⚠ **A probe hazard worth keeping:** `grep -E "$SYM"` over
  `callgrind_annotate` output **matches the echoed command line** when a kernel
  name is passed as `argv`. It produced a garbage first run. **Parse the table,
  do not grep it.**

⚠ **This is a judgement call, not a measurement, and it is the manager's own** —
PROTOCOL rule 3. Two honest objections to it, neither answered here: **(a)** the
user's standing goal names *breadth over realistic C patterns*, and axis-first
ordering trades breadth for depth; **(b)** "eleven of sixteen are bounds bugs"
counts *bug classes*, and the project's actual findings are about **cost
mechanisms**, which have been much less repetitive — p12's lost bulk lowering and
p07's never-amortising tax came from two patterns this argument would call
duplicates. **Push back on it with the pattern you would rather build.**
