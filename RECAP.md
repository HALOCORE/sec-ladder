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

47 patterns are catalogued in `.memory/06-catalogue.md`. **Three exist: p01
(calibration), p02 (first real bug), p16 (first data-dependent bound).**

## The findings so far — this is the actual output

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
  With `-funroll-loops` gcc reaches 2823 and **beats** clang's 2993.

## Working method

See `.tasks/PROTOCOL.md` for the full rules. The short version: manager writes
specs and `.memory/`, one subagent at a time alternating engineer → reviewer,
manager lands `.memory/` corrections and commits.

**Ask to be corrected, not obeyed.** Agents have contradicted the manager's
written instructions **nine times** with measurements and were right all nine.
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

## Priority — read this before planning

**Twelve tasks in, 3 of 47 patterns exist** — six tasks went to gate hardening
before the user called it. The gate's threat model is **honest mistake, not
malicious author** (`.memory/02-bench-rules.md`, top section, with the list of
residuals we are deliberately leaving open). New gate work must pass "could this
happen by accident?" first.

**Spend the coming tasks producing patterns.** Review each pattern once; do not
review each fix to each check. p16 is the proof this works: built, measured,
proved and reviewed inside two tasks, and the review still found a real
overclaim — which is the *right* place for review effort.

## Immediate queue

The gate-hardening arc is **closed**. T010's review confirmed the gate accepts
new patterns; T007 built one and it passed on the first complete run. The mode
now is: build a pattern, review it once, land the corrections, repeat.

1. **p17** (HTTP `Range`, mirrors CVE-2017-7529; LearnVeri port at
   `../LearnVeri/microbench/CVE-2017-7529` to lift from). Needs harness work
   before it can start: a struct result cannot pass through a C out-parameter
   (`dloop._apply_call_args`), and `build.py` hard-codes three C TUs. **Also the
   first pattern where the verified twin stops being idle** — p16's accessor was
   single-clause, so its green twin check proved nothing; a multi-clause accessor
   is where the mechanism earns its keep, and `.memory/02-bench-rules.md` records
   that the twin has never been tested against a generic/method-shaped one.
2. **Re-run `measure.py p02` once**, now that p16's `common/head1_u64_bytes` is
   in place — the ordering condition in `.memory/06-catalogue.md` is satisfied.
3. Then Wave 2 (p03–p10, bounds breadth). Open cross-cutting issues are listed at
   the top of `.memory/06-catalogue.md`.

Carry-overs from p16 worth landing opportunistically: its `inputs/gen.py
--sweep` blobs were never added to the pattern dir (the sweep evidence lives in
`.temp/`), and eight minor findings from TASK_007_REVIEW are listed in
`.tasks/TASK_007_REVIEW_REPORT.md` §F3–F10.

## State

- `harness/` — `check.py` (16 stages incl. clause deletion, `requires` strength,
  the verified twin, and region-actually-runs), `asm.py`, `dloop.py`, `vparse.py`,
  `build.py`, `measure.py`, `report.py`, `fixture.py`. **4200 lines against three
  patterns** — that ratio is why gate work now needs the "could this happen by
  accident?" test.
- p16 gate `PASS`, complete, first run. p02 `PASS`; **p01 `PASS-WITH-BLOCKED-ROWS`** — Miri is now mandatory for any
  pattern with a trusted item and cannot finish p01's `large.bin` in 180 s. 8 of 9
  inputs checked, ninth documented. Policy working, not a regression.
- `results/p02-buffer-copy.json` is stale. Its precondition is now **met** —
  p16's `common/head1_u64_bytes` has landed — so the single re-run is owed; see
  `.memory/06-catalogue.md` for why the ordering mattered.
- Toolchain: Verus `0.2026.08.09.92f466f`, rustc 1.97.1, clang/LLVM 22.1.6,
  valgrind 3.27.1, nightly+Miri, all in `~/tools`, no root. `TOOLCHAIN.md`.
- Commits run through `c623b22`+. Tree clean.

## Decisions

- **Proof-effort budget**: one engineer session per R5 cell, then stop and report
  where the proof stuck — that report *is* the deliverable for that row. Set by the
  manager, pending a user override.
- **`perf_event_paranoid ≤ 1` needs root and is still owed by the user.** It is the
  only way to explain *why* gcc's shorter loop runs slower. Nothing works around it.
