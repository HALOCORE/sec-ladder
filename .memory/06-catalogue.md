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
| p15 | UTF-8 validation + decode | malformed continuation bytes | moderate–hard | ⚠ **REFUSED at TASK_085/TASK_085_REVIEW — CONDITIONALLY, and the condition is NAMED.** Unlike p48/p31/p45 the justification was not false a priori: **all three probes PASSED** and the named kill-risk **closed** (a verified UTF-8 validator, `ensures res == valid_utf8(b@)` bidirectional, **5/0, zero trusted items**). It is refused because **all three of the row's justifications were then measured away in one session** *and* because the shape worth building is the shape the gate cannot audit. ⚠ **It becomes buildable the day `_axiom_items` learns to see a USED vstd `assume_specification`** (RECAP "Owed" 0, sixth route). See the refusal block below |

## Family C — parsing & protocol decoding

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p16 | TLV / length-prefixed record walker | length field vs remaining buffer | easy–moderate | **done** (T007), reviewed; gate PASS first run, R5 == R4 `exact` at O3; **first O(n) cost of a *spelling* — R3 is still 0/byte** |
| p17 | HTTP `Range:` style header parser | int overflow → OOB (cf. CVE-2017-7529) | moderate | **done** (T011), reviewed; gate PASS first run, R5 == R4 `exact` at O3; **memory-safe but functionally wrong**; the *leaking* slice-guard variant reproduced at T012 (`.temp/` artefact + committed generator — see `.memory/05-layout.md` item 11 for why it cannot live in the pattern dir) |
| p18 | varint / LEB128 decoder | **unbounded shift** — ✅ **the catalogue's guess UPHELD, the first row in five patterns to survive its own guess** (T049 §0, four alternatives rejected with measurements). **The first bug here that is UB but NOT a memory-safety bug**: it touches no memory and **ASan is silent** | easy–moderate | **done** (T051), gate `PASS` first complete run, R5 **12/0** (twin 13/0), `R4 ≡ R5 exact`, Miri 9/9, **TCB 3, no `assume`**, **reviewed** (T051_REVIEW: 1 blocker + 7 majors + 5 minors, **15 clean negatives**; corrections at T052). **Four catchers — UBSan, `debug-assertions`, Miri, Verus — all outside the 24-cell matrix**, and Miri catches it as a **panic**, not a `ub` report |
| p19 | protocol state machine (byte-at-a-time) | state confusion | moderate | ✅ **BUILT at TASK_087 as `p19-state-machine` — the 23rd pattern.** Gate `PASS`, **0 failures / 0 loud / 0 blocked**, Verus **12/0** (twin 13/0), TCB 3, `identity` **O0 `norel` / O3 `exact`**. **`Ir` per message byte: R2 15.00 · R3 9.75 · R4/R5 8.75 · c-gcc 11.00 · c-clang 8.75** (whole-program marginal, `-O3`, **inline mode `isolated`**). **`R2−R4 = 6.25 = 3.00 check + 3.25 foreclosed 4x unroll`**, and the third rolled instruction is a `mov` — **the checked spelling must keep `st` live for the compare and cannot destroy it with the shift.** ⚠ **The result to quote: LLVM lowers the bounds check to `cmp $0x8`, a STATE-RANGE check — safe Rust's automatic check and the validation pass C omits are THE SAME PREDICATE**, enforced once per access versus once per call. **The bug class is the tree's THIRTEENTH `index >= len`** (nearest sibling p36) and the pattern says so in four files. **The framing is CONDITIONAL and the conditions are PINNED**: the table must be loaded *data* and dispatch must be by *indexing*, not `switch` — the only `forbidden` entries in the tree that forbid a spelling **for being safe**. Precedent, source fetched and manager-verified real: Linux `security/apparmor/match.c`'s `aa_dfa_match_until()` indexes four tables with **no test at all**, licensed by `verify_dfa()` at policy load. ⚠ **The two CVE IDs the pattern cites are NOT verified — confirm or strike them before quoting.** **Second result, not about Rust:** validation is **O(table) once** and the bounds check is **O(message)**, so the buggy C rung is **5071 `Ir`/call cheaper than unsafe Rust at `small` and 3569 dearer at `large`** — a sign flip that is not about safety. ⚠⚠ **THREE NUMBERS THE MANAGER PUT IN THIS ROW FROM `TASK_086`'s PROBE WERE WRONG, and the first is the one to remember:** ~~`gcc -O2` **exit 139 SIGSEGV**~~ — **the harm is SILENT**; the SIGSEGV was a **STORAGE-CLASS ARTEFACT** of the probe's `static uint8_t TBL[8][256]` in `.bss`, and the same read from the **heap exits 0**. ~~naive `+5.25 Ir/byte`~~ is **+6.25** (the probe folded with `wrapping_add`; p19 folds `acc*31+st`, which needs `st` in a register the check also needs). ~~the 2-D rows `+4.25` spelling~~ **does not exist in contract** — the probe's `k19_rows` got its `&[[u8;256];8]` from an `unsafe` cast **in its driver**. **Harm ships instead as THREE INPUTS ONE BYTE APART** — entry 8 in-bounds/ASan-clean, entry 10 `heap-buffer-overflow`, entry 255 `SEGV on unknown address`; all three silent at plain `-O2` on 8/8 C cells. See `.tasks/TASK_087_REPORT.md`. |
| p20 | length/offset pair validation (heartbeat-style) | trusted length field (cf. CVE-2014-0160) | moderate | planned |
| p21 | CSV/field splitter with escapes | quote-state off-by-one | moderate | planned |

## Family D — data structures, array-backed

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p22 | **open-addressing probe over a full table** (delivered as `p22-hash-probe`) | **non-termination — the class UPHELD, and reframed in §0.** Memory-safe, ASan/UBSan silent, Miri silent 90 s. ⚠ *"R2/R3/R4 all hang"* is true of a **mechanical port** and false of the shipped ladder, which puts the bug in **R1 only**; the published claim is *"nothing on this ladder EMITS the capacity check"* | hard | **done** (T070), gate `PASS-WITH-BLOCKED-ROWS` (a declared-hang input blocks a Miri row) first complete run, 0 failures, R5 **20/0** (twin 23/0), `R4 ≡ R5` `exact` at O3, TCB 5, **reviewed** (T070_REVIEW: **1 blocker, 3 majors, 4 minors, 54 named attacks**; corrections at T071, which refuted the review twice). **First user of the hang machinery.** ⚠ **"The first termination obligation" was FALSE** — 73 exec-loop measures already existed. The counted claim: **the tree's only exec-loop measure not expressible in the loop's own exec variables, 1 of 73** |
| p23 | in-place quicksort partition | aliasing, permutation invariant | hard | planned |
| p24 | binary heap (sift up/down) | parent/child index arithmetic | moderate–hard | ⚠ **PROBED at TASK_086 (ranked 4) and TASK_090 (R5). PROVISIONAL — unreviewed.** ✅ **R5 CLOSES and the manager's prediction that `heapify`'s loop was the sticking point is WRONG — nothing stalls.** `heapify(v: &mut [u64])` **requires NOTHING about heap order** and ensures, unconditionally and in the **positive** direction, `final(v)@.to_multiset() =~= old(v)@.to_multiset()` **and `is_heap(final(v)@)` over the WHOLE ARRAY** — `6 verified, 0 errors`, and at the R5 rung with trusted accessors **`6/0` shipped, `8/0` twin**. ⚠ **The real content is in `sift_down`, not `heapify`:** the invariant `forall j != i ==> heap_at` is **not inductive** (the swap raises `v[i]` and can break `heap_at(parent(i))`) and needs a **parent-dominance conjunct** — proved load-bearing by mutation. **7 of 8 mutants fail**, including p24's own `2*i+2 <= n` bug. ⚠⚠ **The 8th is the vacuity control and it PASSES: with the multiset clause deleted, a body that ZEROES THE ARRAY still satisfies `is_heap`** — the multiset clause carries the anti-vacuity weight. Twin teeth verified: three separate weakenings pass ordinary Verus and **only** the twin config moves. ⚠⚠ **COST RETRACTED — ~~`≈7.9 ± 0.1 Ir`/element~~ IS A PROBE-SHAPE NUMBER, AND AT SHIPPED SHAPE THE TAX IS `0.00`** (TASK_092, measured). Given a fixed-capacity scratch and a header-derived count, **`ship_safe` and `ship_unsafe` are BYTE-IDENTICAL** — *"identical by raw machine-code bytes: True"*, `md5_fn 3d37ca7b…` both, `n_nopad 133` both, **no panic edge in either** — and it stays byte-identical with the count read as a `u16`. The probe's 7.9 reproduces only because its sift takes `i` as an opaque parameter and `n` as an ABI value, leaving **five bounds branches per sift** (`jae:6` safe vs `jae:1` unsafe). ⚠ **The 18-length residue work behind the 7.9 was sound; it was measuring the wrong SHAPE.** ⚠ **So p24 has no measured safety tax and needs a new reason to be built** — its R5 result and its temporal-adjacent index arithmetic stand, the cost axis does not. ⚠⚠ **TWO NUMBERS FROM TASK_086's PROBE ARE WRONG, AND THE FIRST IS A REPORTING BUG THAT AFFECTS FOUR ROWS:** ~~*"silent at `gcc -O2`, and only UBSan sees it — ASan did NOT report a heap-buffer-overflow"*~~ — **ASan reports it in ALL THREE storage classes on BOTH compilers**, and **UBSan alone reports nothing anywhere**. The cause is `head -4` in `.temp/t86/harms.sh`: gcc's UBSan report is exactly 4 lines and ASan's banner is on lines 5–6. **Re-running TASK_086's own unmodified binary gives exit 1 and one ASan `heap-buffer-overflow`.** ⚠ **Rows `p21`, `p24`, `p26` and `p41` each fire BOTH detectors, so that table could only ever show the UBSan half for four rows — treat every harm cell in it as half-shown until re-run with `grep` instead of `head`.** And ~~`+22.1%`~~ is **not a constant of the row**: it steps 27.5% → 22.2% at n=1024/1025, and **the step is in the DENOMINATOR** — the probe's `cost.rs` clones inside the measured loop and glibc `memcpy` switches to `rep movsb` at **8192 bytes**, which callgrind charges **≈1 `Ir` per byte moved**. ⚠ **Not free to ship:** `heapify` needs `len <= usize::MAX/2 - 2` for the `2*i+2` overflow, so a driver conjunct is owed (the p17 route). Evidence: `.tasks/TASK_090_REPORT.md`, `.temp/t90/`. |
| p25 | dynamic array with `realloc` growth | growth overflow, stale pointer | moderate–hard | planned |
| p26 | run-length encode/decode | expansion overflow on decode | moderate | planned |

## Family E — data structures, pointer-backed (Verus stress tests)

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p27 | **handle table over per-record `malloc`/`free`** (delivered as `p27-handle-table`; the *singly linked list* SHAPE is retracted -- where `next` sits decides observability and that is a glibc detail, and the bug would fire on **every** input, which the adversarial-only constraint forbids) | **use-after-free -- the class UPHELD, and the project's FIRST TEMPORAL bug.** R1 omits one conjunct (`&& live[h] == 1`) on the READ path | hard (`vstd::raw_ptr`) | **done** (T060), gate `PASS` first complete run, R5 **15/0 first run** with a functional postcondition (twin 20/0), `R4 == R5` `exact` at O3 / `norel` at O0, **TCB 7 (forced -- see below)**, **reviewed** (T060_REVIEW: **no blocker**, 3 majors, 8 minors, **28 clean negatives**; corrections at T061). **Not one instruction of `R3 - R4` is the lifetime guarantee** -- a closed decomposition over *every* function gives `230.07 = 109.65 kernel + 120.42 drop glue + 0.00 allocator`, and an R4 keeping R3's bounds checks costs **+153.51**, so safe Rust pays **43.86 LESS** of the spatial tax. The lifetime guarantee itself costs **zero**, and its shape is structural: **the free and the invalidation are one operation in safe Rust and two in C, and the bug is the third -- the ASKING -- going missing** |
| p28 | intrusive doubly linked list | aliasing, ownership | research-grade | ⚠⚠ **REFUSED at TASK_093 / TASK_093_REVIEW — the verdict is REVIEWED, and its FIRST STATED REASON WAS REJECTED BY THE REVIEW.** ⚠ **Read `.memory/01-ladder.md`'s allocator-guarantee section before rescheduling; do not reuse TASK_093's `E0382`/`E0499` argument, which is false.** The reusable reason: **safe Rust's temporal guarantee is a guarantee about the ALLOCATOR**, and p28's two safe spellings that free per node both catch the bug by **p27's runtime mechanism** — `Rc`/`Weak` reproduces p27's published sentence verbatim (`bwd=32127`, the backward walk truncating at `upgrade() -> None`), while the index arena **never frees** (`0` heap blocks released by unlink, measured). ⚠⚠ **AND THE NEAR MISS IS THE VALUABLE HALF: a p28 with R3 = safe arena and R4 = raw-pointer DLL would have published *"safe Rust is 6.02× CHEAPER than unsafe"* with `321/296 = 108.4%` OF THE GAP IN THE ALLOCATOR** — the bounds check is `9.00`, **3.0% of the magnitude and the opposite sign**. Sixth instance of the flattering-direction trap and **the first caught BEFORE a pattern was built.** ⚠ **The cost half of the refusal does NOT follow, though** (TASK_093_REVIEW blocker 2): `box_arena` vs `box_arena_unchecked` — same program, one `Box` alloc + one free per node on **both** sides — gives a closed decomposition **`+24.00 = 12.00 bounds check + 11.00 THE ASKING + 1.00 interaction, and `0.00` ALLOCATOR**, which is exactly the form p27 published. **p28 CAN do what p27 did**; it is still p27's *mechanism*, which is why the row is refused. ✅ **Clean negatives from the review, do not re-run:** `rawptr`'s `+321` is a **real** allocator price (`k_alloc_pair24` = `340.823 Ir`/node), **not** p31's malloc-elision artefact; the C detector table reproduces exactly under the **gate's** flags; and `p01` really is inside the count of 14, so **14 patterns carry the `index >= len` axis and 13 model a bug on it** (three tracked files assert an ordinal built on that list). **Superseded material follows.** ⚠⚠ **THE *"expect R5 to be defeated"* PREDICTION BELOW IS CONTRADICTED TWICE OVER** (TASK_086 #241, TASK_091; **PROVISIONAL — unreviewed**). ✅ **`wf` is PRESERVED by `unlink` (`4/0`) AND ESTABLISHABLE (`8/0`, FIRST ATTEMPT)** — `new()` → `push_front`×3 → `unlink` on the **MIDDLE** node, with `unlink`'s three `requires` discharged **from `push_front`'s postcondition alone**. Compiles and runs correctly. **Zero TCB — no `assume`, no `external_body`, no `assume_specification`.** ⚠⚠ **THE LOAD-BEARING CLAUSE IS ADDRESS INJECTIVITY, and without it `fake3` passes: ONE node with `prev = next = itself`, declared `len = 3`, `ptrs@ = [p,p,p]`, discharging `unlink`'s ENTIRE precondition.** ⚠ **The difficulty is NOT where anyone predicted:** injectivity cost one 8-line `proof fn`; the real costs were **(1) `Dll` needing EXEC fields it had only in ghost — a CONTRACT change, budget it in `spec.md`** — and **(2) `is_disjoint` taking `&mut self`, so it CANNOT be called inside `assert forall|i| … by`**, which is a goal-reformulation problem no proof hint fixes. ✅ **Probes 2 and 3 now exist (TASK_086 ran neither), from LINKED binaries, zero-parameter — each `Ir`/victim IS the static loop-body count to three decimals, at N = 1024/4096/8192:** `k28_checked` 138 B **20.003**, `k28_unchecked` 202 B **11.503**, `k28_rawptr` 129 B **7.507**, `k28_rawptr_rmw` 129 B **7.507**. ⚠⚠ **THE WHOLE-STRUCT READ-MODIFY-WRITE VERUS FORCES IS FREE** — `raw_ptr` has no field-level mutator, so R5 must rewrite the whole 24-byte `Node`, and that costs **1.00 `Ir` per CALL out of 50 232**, with a driver swap-test flipping the sign to −3.00. **So R5 needs NO local `external_body` field-store wrapper to stay identical to R4** — the feasibility question p28's R4/R5 pair turns on. ⚠ **Do NOT publish *"the bounds check costs 8.5"***: of the 8.5 `Ir`/victim safe tax, **6 are the three `cmp/jbe`, ~1 the foreclosed unroll, ~1.5 register pressure** — p35/p05's shape. ⚠ **And the CHECKED kernel is SMALLER (138 B vs 202 B)** because the unchecked one is 2× unrolled; **do not read size as cost** (p19 showed 76 B vs 173 B). ⚠ **Design warning: 4.0 of the 12.5 R3→R4b gap is INDEX SCALING, not checking** — three `shl $0x4` a pointer list does not pay — **so a p28 whose R3 is a safe index arena would misattribute it.** ⚠⚠ **THE REMAINING RISK, and it is not `unlink`: there is NO `deallocate`.** The probe drops `Tracked<Dealloc>` and **leaks**; a shipped p28 must thread it like p27, **and that is where p28's TEMPORAL bug class actually lives.** Untested. Bug class **temporal**, shares with **p27** — the only temporal pattern in the tree. Evidence: `.tasks/TASK_091_REPORT.md`, `.temp/t91/`.
| p29 | binary search tree insert/lookup | recursive ownership | hard | ⚠⚠ **REFUSED at TASK_095 — PROVISIONAL, UNREVIEWED.** It was TASK_094's one BUILD and the last live row in Family E; **§0 killed it.** ✅ **Limb (a) SURVIVES** — the safe representation really frees (`allocs=2001 frees=2000`, `remove_leaf` releases one 24-byte block, against p28's `0`). ⚠⚠ **LIMB (b) IS REFUTED THREE WAYS, manager-verified:** *(1)* the `E0502` is **generic borrowck** — a `struct S { v: u32 }` with **no data structure at all** prints the identical error with the identical message, **and so does `p27`'s own `Vec<Option<Box<Rec>>>`**; *(2)* **key-addressed, the same BST compiles, runs, and exhibits p27's published sentence verbatim** (`*cur = None` frees and invalidates in one operation; the second `find` — the ASKING — gets `None` at run time); *(3)* **key-addressed, the C rung has NO BUG AT ALL** (ASan silent, positive controls firing) — **p29's UAF REQUIRES a saved raw pointer and p27's does not**, because C's `tab[h]` retains the dangling pointer after `free`. ⚠ **And 22 of 24 patterns take their payload from a file blob, so the shipped kernel cannot host a pointer** — p27's own hashed `why` says exactly that. So a shipped p29 is **outcome 2** (p27's `Option<Box<T>>` discriminant, same type, same `*slot = None`) or **outcome 3** (silent, Miri-clean = p04's class). ⚠⚠ **AND ITS DECLARED COST ZERO WAS FALSE:** the `−0.00024 Ir`/lookup reproduces **exactly**, but it is a zero about the **WALK** — with the alloc/free in the pair it is **`+48.01 Ir`/key** (the `remove` term alone `+18.95`). **The manager's task file instructed that zero be written into `spec.md` §0 before measuring; that would have shipped a false declaration.** ✅ **THE ARTEFACT SURVIVES THE ROW and is EMBEDDED VERBATIM in `.tasks/TASK_095_REPORT.md`** (`sha256 90a338c7…`, 232 lines, the p15 precedent): a fully verified BST — recursive `Box<Tree>`, `Set`-valued `keys()`, `bst()`, `contains`, `insert`, `remove_min`, and a **three-case `remove` with the in-order successor** carrying `ensures res.bst() && res.keys() =~= self.keys().remove(key)` — **`9 verified, 0 errors`, TCB 0, no lemma, no `decreases_by`, manager-re-run.** Non-vacuous: a call site discharging `bst()` from `insert`'s own postcondition and removing a **two-child** key, plus a mutant battery where **3 of 4 valid mutants fail** (the 4th disclosed as invalid — it does not typecheck). ⚠ **This contradicts the catalogue's `hard` rating and its retracted *'expect R5 defeated'* for the MUTATING operations, not just `contains`.** Evidence: `.tasks/TASK_095_REPORT.md`, `.temp/t95/`. |
| p30 | chained hash table (buckets of lists) | ⚠ **the column *"combines p22 + p27"* is HALF FALSE** (TASK_094 #267) | research-grade | ⚠ **REFUSE — PROVISIONAL, UNREVIEWED.** **A chained table CANNOT FILL**, so p22's non-termination is **structurally absent**: measured `maxchain=4096 of 4096 keys in 1024 buckets`, terminates. What remains is p27's half alone. |

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
| p32 | free-list allocator | double free, corruption | research-grade | ⚠ **REFUSE — `p32` AND `p33` ARE ONE ROW. PROVISIONAL, UNREVIEWED.** See `p33`. |
| p33 | object pool with recycling | use-after-recycle | hard | ⚠ **REFUSE, WITH `p32`, AS ONE ROW — PROVISIONAL, UNREVIEWED.** ✅ **The interesting half is REAL and REVIEWED** (`.memory/01-ladder.md` outcome 3): a slot free list recycles storage the program owns throughout, so **safe Rust's temporal guarantee has nothing to attach to** — under `#![forbid(unsafe_code)]`, **use-after-recycle reads the recycled node's value (`9999` for an expected `1002`) and a slot double-free yields two ALIASED handles, both silently wrong and Miri-clean (0 UB in all three modes)**, ✅ **manager-re-run**. ⚠ **A generation tag does not rescue it** — the bump is the hand-written second store C omits (`gbug get(stale) = Some(val=7777) <- NOT CAUGHT`). ⚠⚠ **But that makes the class `p04`'s** (*"stays in bounds, invisible to a memory-safety proof"*) **and the harm framing `p48`'s** (*"in bounds, live, owned"*), which is refused. ⚠ **AND PROBE 1 KILLS BOTH INDEPENDENTLY: the bug compiles identically at C, safe naive, safe tuned and unsafe — no boundary ANYWHERE, which is `p31`'s death.** ⚠ **One instrument note (TASK_094 #266): the manager's *"does the safe rung FREE?"* test is sound for CONTAINERS and VACUOUS for ALLOCATORS** — a C free-list allocator also calls `free()` once at teardown, so *"released heap blocks"* reads `0` on both sides. |
| p34 | reference counting | leak, premature free | hard | ⚠ **REFUSE — PROVISIONAL, UNREVIEWED — but ONE HALF IS REAL AND SHOULD NOT BE LOST.** `.memory/01-ladder.md` outcome 4: **the safe rung is WORSE than C.** `Rc` in both directions is a cycle and leaks; `Weak` for `prev` does not. ✅ **Manager-re-run: `miri cycle` → 5 `memory leaked` lines, `miri weak` → 0**, same checksum both; TASK_094 measured `3 allocs / 0 frees / 324 bytes` under `#![forbid(unsafe_code)]`. **An inversion the tree does not have, and `p27` explicitly does NOT model a leak.** ⚠⚠ **NAMED KILL, and it is an ENVIRONMENT fact, not a design one: there is NO WORKING LEAK DETECTOR FOR THE C RUNGS ON THIS BOX** — LeakSanitizer is live under `-static-libasan` but **silent at `-O1`/`-O2` on a leaked linked list, and the gate builds stage 7 at `-O1`**; valgrind memcheck cannot run at all (needs `libc6-dbg`, needs root). **Miri is the only leak detector here and it covers the Rust rungs only.** See `.memory/00-environment.md`. **Fold the measured leak into `p42`'s triage rather than losing it.** |

## Family G — systems idioms & representation

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p35 | tagged union / discriminated dispatch | tag-payload mismatch | moderate | ⚠⚠ **BLOCKED, AND THE MANAGER HAS NOW DECIDED NOT TO UNBLOCK IT THAT WAY (TASK_096 / TASK_096_REVIEW, REVIEWED).** `_scan_unsafe_sites` **stays as it is** — see `.memory/02-bench-rules.md`'s decision block. ⚠ **The premise this row was scheduled on is REFUTED: `p35` is blocked by TWO rules and the second is RUST.** There is no safe union read (`error[E0133]`), and `_TWIN_BANNED` forbids the `unsafe` keyword in a twin, so the twin must be justified away — which is `n_twins == 0` → **hard FAIL. Executed on a synthetic pdir, not read: `p35` has NO LEGAL CONFIGURATION.** So narrowing `_scan_unsafe_sites` would have bought **exactly one row** (this one; `p15` is refused on grounds the rule does not touch) — **and the first narrowed predicate anyone wrote was UNSOUND**, admitting a `#[verifier::external]` fn nested in a verified body that Verus reports `2 verified, 0 errors` for and whose binary **reads out of bounds**. ⚠⚠ **~~THE ONE THING STILL OPEN IS `_TWIN_BANNED`~~ — PROBED AT TASK_097 AND THE ANSWER IS NO. `p35` IS DEAD AND THE CATALOGUE CLOSES.** ✅ **Manager-verified:** `_is_trusted` returns `False` unless the item is `#[verifier::external_body]`, and **a twin may not be `external_body`** by three independent rules — so **a twin is STRUCTURALLY never `_is_trusted`** and `_scan_unsafe_sites` hard-fails all four routes (twin-holds-unsafe, verified helper, `cfg`-gated helper, macro helper). **Isolated: delete `unsafe` from `_TWIN_BANNED` and `FAIL [tcb-unsafe]` is UNCHANGED — the twin rule was never what fired.** ⚠ **This refutes two sentences the manager wrote into `.memory/` one task earlier.** **The row's own measurements stand and are worth keeping:** ✅ **Verus supports the Rust `union` NATIVELY**: the correct-variant obligation is **first class in the type system** — declared inside `verus!` it is `error: requirement not met: to access this field, the union must be in the correct variant` (`1 verified, 1 errors`), and `requires v is i` gives **`2 verified, 0 errors`**. **No vstd spec is involved**, which is why probe 4's grep MISSES it and the row is blocked anyway: the read is still `unsafe { v.i }` in a **verified** fn. Boundary is **compile-time, p08's shape** — safe Rust's `enum` makes the mismatch unrepresentable. Cost **+0.829 `Ir`/element (+6.5%)**, ⚠ **and the mechanism is UNROLLING, not the check — both rungs execute the same tag test.** Bug class **type confusion, ABSENT from the built tree**. Harm has a magnitude axis: the `double` arm is a **silent wrong value with NO detector firing at all**; the pointer arm is **exit 139 SIGSEGV**. Traps: declare the union **inside** `verus!` (outside, Verus prints `external_type_specification`); `#[derive(Clone, Copy)]` fails; use `v is i`, not `v->i`. |
| p36 | function-pointer table dispatch (vtable-like) (delivered as `p36-vtable-dispatch`). ⚠ **The catalogue's *"the harm is not reproducible"* worry is REFUTED — 24/24 SIGSEGV** across gcc/clang × O0–O3 × 3 opcodes; and the *"likeliest to hit p55's wall"* triage was wrong twice over | **index out of table — the class UPHELD, but it is the tree's TWELFTH `index >= len` and the pattern says so.** What is not twelfth: ⚠ **Verus at the pin cannot type `fn(u64) -> u64` AT ALL** (error on the *declaration*), so C's own dispatch mechanism is **not an admissible rung** and the Rust rungs use `[&'static dyn Op; NOPS]` — **priced at exactly `3.00000` Ir/dispatch, finding 14's sharpest instance because it excludes the MECHANISM, not a spelling** | moderate | **done** (T072), gate `PASS` first complete run, R5 **19/0**, `R4 ≡ R5` **`norel` at O3 — the first pattern in the tree not `exact`**, TCB 4 (2 contract-bearing), **reviewed** (T072_REVIEW: **2 blockers, 5 majors, 7 minors, 36 clean negatives**; corrections at T073, which refuted **three** prescriptions — two the manager's, one the review's). ⚠ **Both published headlines moved.** `R3 − R4 = +15.00 flat` was fitted against an R3 side **never searched** (one lever, and it moved R3 *dearer*): p36 now publishes **`+7.00` (fixed-R4 bound, cheapest R3 found) and `+10.00` (matched pair), never one number and no pair interval.** And every `Ir` was **kernel-exclusive on the one pattern whose kernel IS a call** — dispatch targets are 512/384/0 Ir per call, which **reverses** the `match` control and vanishes the gcc-vs-clang gap. **`Ir` exactly constant while wall clock moves 3.13×**, verified on program totals; ⚠ **not p07's finding in a costume** — p07's `Ir` moves and its branch is conditional. Catchers: ASan/UBSan name the **array read**, never the call; `-fsanitize=function` is **gcc-absent and clang-defeated**; only `-fsanitize=cfi-icall` names the transfer, and it is a control (needs `-flto` + `-fuse-ld=lld`), not a rung |
| p37 | callback with `void*` userdata | type confusion | moderate–hard | ⚠ **REFUSE — PROVISIONAL, UNREVIEWED.** **Strictly worse than `p35`, and blocked by VERUS ITSELF rather than by a gate policy** — `p36`'s *"Verus at the pin cannot type `fn(u64) -> u64` at all"* re-verified at the pin, so ⚠⚠ **fixing `_scan_unsafe_sites` does NOT unblock it, unlike `p15` and `p35`.** |
| p38 | **record parser that clamps a length in place and re-reads it through a pun** (delivered as `p38-alias-pun`). ⚠ **The catalogue's own spelling — *"endian conversion, `memcpy` vs union"* on a byte buffer — is the BENIGN aliasing direction and was retracted before the build**: neither compiler exploits it, 8 of 8 cells. Only two incompatible **non-char** types move | **strict-aliasing UB — the class UPHELD** (unusual: three of the previous five were overturned), and the harm is a **MISCOMPILE**, not a wrong answer | moderate | **done** (T066), gate `PASS` first complete run, R5 **13/0** (twin 16/0), `R4 ≡ R5` `exact` at O3 / `norel` at O0, TCB 5, Miri 8/8, **reviewed** (T066_REVIEW: **no blocker**, 3 majors, 8 minors, **35 clean negatives**; corrections at T067, which refuted three of the *review's* own numbers). **Ships labelled a DEMONSTRATION KERNEL** — the harm needs four conjunctive conditions and **six neighbouring one-line spellings each remove it**. ⚠ **The quotable result is the price: on gcc the undefined spelling is the DEAREST of the six, and every fix saves exactly 6.00 `Ir`/call.** **The first bug class here that unsafe Rust does not reintroduce** — Rust has no type-based aliasing rule at any rung. Also the project's **first additivity-extrapolation failure**, which turned out **100% attributable** to three missing columns, none of them the one named |
| p39 | bitfield pack/unpack into wire format | shift/mask off-by-one | moderate | ⚠ **REFUSE — PROVISIONAL, UNREVIEWED.** **It is `p09`'s sentence with the mask on the other side**: the bug is **one immediate**, `$0x1ff` → `$0x3ff`, worth **`0.00 Ir`** — and `p09` already ships *"one character between a bug everything catches and one nothing does"*. ✅ **What it did contribute is a third instance of a real rule** (`.memory/03-measurement.md`): of the `4.25` check tax, `2.00` is the `cmp/jbe` and `≈2.25` is the unroll the panic exit edge forecloses — **after `p35` and `p28`, that is a rule, not a coincidence.** |
| p40 | struct-of-arrays vs array-of-structs traversal | none — pure perf axis | easy | planned |
| p41 | flexible array member struct | size computation overflow | moderate–hard | planned |
| p42 | `goto cleanup` error handling | leak on error path | moderate | planned |

## Family H — numeric & crypto-adjacent

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p43 | checksum / CRC over untrusted length | loop bound from input | easy | ⚠ **REFUSE — PROVISIONAL, UNREVIEWED. The catalogue's OWN claim (*"p43 is p16's shape"*) is CONFIRMED WITH A MEASUREMENT** — `+3.00 Ir`/call **flat**, the hoisted check visible in `objdump`, i.e. `p16`/`p20` verbatim. ⚠ **And the safe TUNED rung beats unsafe by `0.749 Ir`/byte**, which is the flattering-direction trap again. |
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
