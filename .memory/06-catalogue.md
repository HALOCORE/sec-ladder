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
about memory safety, and p05 the first causal link from proof to performance. 5 of 47 now exist. The gate's threat model is now
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

- **p05's R3 is not the best R3, and the same audit is owed on p16 and p17.**
  TASK_014_REVIEW's blocker: `data.chunks_exact(ncol)` is `nrow − 7`
  instructions per call **cheaper than the unsafe rung**, on every p05 input,
  with identical output on all 150 committed inputs. p05's shipped
  `safe_tuned.rs` reslices by hand and pays `6·nrow + 9`. The variant lives in
  `.temp/review014/p05lin/` and is **not gate-ready** — it needs static
  identity, the `O0`/`whole` cells, and `spec.md` pins. Three patterns have now
  priced a *spelling* as safety's cost, so the audit is not optional: see
  `.memory/01-ladder.md`'s corollary rule (write two independent R3 spellings,
  quote the cheaper).
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
  p08's means "the tool cannot see this". `check.py:566` admits only
  `clean`/`fires`. The reason survives only in `model.py`'s docstring.

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
| p02 | length-prefixed buffer copy (`memcpy` w/ attacker length) | spatial OOB write | easy | planned |
| p03 | bounded queue / stack, array-backed | index underflow on empty pop | easy | planned |
| p04 | ring buffer with wraparound | modular index, aliasing | moderate | planned |
| p05 | 2-D index flattening / matmul (`i*n+j`) | dimensions trusted vs buffer; overflow in the check | moderate | **done** (T013), gate PASS first run, R5 == R4 `exact` at O3; safety moves from per-element to **per-row**, and gets *worse* with wider lanes |
| p06 | in-place reverse / rotate / swap | aliasing, permutation invariant | moderate | planned |
| p07 | binary search | midpoint overflow (`(lo+hi)/2`) | moderate | planned |
| p08 | memmove with overlapping regions | overlap UB | moderate | **done** (T014), reviewed; gate PASS first run, R4 == R5 `exact` at **both** O0 and O3; the UB **executes and is unobservable** (glibc `memcpy` *is* `memmove`), so p08 is a tooling-and-expressiveness result, not a performance one |
| p09 | bit vector / bitset ops (set, test, popcount) | word-index vs bit-index confusion | easy–moderate | planned |
| p10 | sliding-window / stencil over array | off-by-one at boundaries | moderate | planned |

## Family B — strings & NUL-termination

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p11 | `strlen`/`strcpy` over NUL-terminated buffer | missing terminator → OOB read | moderate | planned |
| p12 | `strcat` into fixed stack buffer | classic stack overflow | moderate | planned |
| p13 | `strncpy`/`snprintf` truncation semantics | silent truncation, missing NUL | moderate | planned |
| p14 | tokenizer (`strtok`-style, in-place mutation) | in-place mutation + aliasing | hard | planned |
| p15 | UTF-8 validation + decode | malformed continuation bytes | moderate–hard | planned |

## Family C — parsing & protocol decoding

| ID | Pattern | C bug class modelled | Verus difficulty | Status |
|---|---|---|---|---|
| p16 | TLV / length-prefixed record walker | length field vs remaining buffer | easy–moderate | **done** (T007), reviewed; gate PASS first run, R5 == R4 `exact` at O3; **first O(n) cost of a *spelling* — R3 is still 0/byte** |
| p17 | HTTP `Range:` style header parser | int overflow → OOB (cf. CVE-2017-7529) | moderate | **done** (T011), reviewed; gate PASS first run, R5 == R4 `exact` at O3; **memory-safe but functionally wrong**; the *leaking* slice-guard variant reproduced at T012 (`.temp/` artefact + committed generator — see `.memory/05-layout.md` item 11 for why it cannot live in the pattern dir) |
| p18 | varint / LEB128 decoder | unbounded shift, truncation | easy–moderate | planned |
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
| p27 | singly linked list (build, traverse, free) | use-after-free, leak | hard (`vstd::raw_ptr`) | planned |
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
| p38 | endian conversion / type punning (`memcpy` vs union) | strict-aliasing UB | moderate | planned |
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
| p47 | constant-time compare / select | **timing side channel** — compiler may reintroduce a branch | moderate | planned |

p47 is special: the "security" axis is timing, not memory safety, and the threat is
the *optimiser*. Worth doing precisely because it inverts the usual story.

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
