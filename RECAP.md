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

47 patterns are catalogued in `.memory/06-catalogue.md`. **Two exist: p01
(calibration), p02 (first real bug).**

## The findings so far — this is the actual output

1. **A Verus proof costs exactly zero instructions.** The proven binary is
   byte-identical to the unproven one; ghost code fully erases. Verified on raw
   machine code on both patterns, at both opt levels.
2. **A proof alone buys nothing.** Proving safe Rust panic-free leaves every bounds
   check in place — rustc never learns what the prover knew. The payoff arrives
   only when the proof *licenses unsafe code*: R5 is R4's machine code with the
   obligations discharged.
3. **Safety is cheap when the optimiser can see the loop.** Tuned safe Rust is
   **+8…+10 instructions per call** versus unsafe — flat in the size of the data,
   not a percentage. Hardened C's check is +5 (gcc) / +12 (clang), also flat.
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

## Retracted — do not reinstate

- **"Safe Rust pays an O(n) bounds-check tax"** (p02). The indexed fold's bounds
  checks cost *zero*; the whole delta was one spelling of an overflow check
  defeating LLVM's `memcpy` idiom recognition. Restated as a **codegen fragility**
  finding: one spelling loses the idiom, three others are +10 flat.
- **"C beats Rust"** (pilot). A **gcc-only** measurement generalised to "C"; the
  sign was backwards. The clang result was never affected.
- **"gcc's byte loop beats glibc `memcpy`"** — mislabelled; it beats R4, not gcc's
  own memcpy build.

## Working method

See `.tasks/PROTOCOL.md` for the full rules. The short version: manager writes
specs and `.memory/`, one subagent at a time alternating engineer → reviewer,
manager lands `.memory/` corrections and commits.

**Ask to be corrected, not obeyed.** Engineers have contradicted written
instructions **seven times** with measurements and were right all seven. Two were
prescriptions that could not have worked at all.

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

**Ten tasks in, 2 of 47 patterns exist**, because six tasks went to gate
hardening. The user has called this: the gate's threat model is **honest mistake,
not malicious author** (`.memory/02-bench-rules.md`, top section, with the list of
residuals we are deliberately leaving open). New gate work must pass "could this
happen by accident?" first.

**Spend the coming tasks producing patterns.** Review each pattern once; do not
review each fix to each check.

## Immediate queue

1. **TASK_010 is done and unreviewed.** It closed the twin's perimeter and tied the
   driver region to code that actually executes. A review is owed — and it must
   note that the manager designed the twin mechanism and finished part of TASK_009.
2. **TASK_007 — p16, the TLV record walker.** Fully specified, unblocked once
   TASK_010's review closes. First pattern with a **data-dependent loop bound** —
   the case `.memory/01-ladder.md` says not to generalise "safety is cheap" to. Its
   security argument rests entirely on the trusted accessor's `requires`, which is
   why it waited for the twin. Decomposition is mandatory *before* any claim.
3. **p17** (HTTP `Range`, mirrors CVE-2017-7529, LearnVeri port to lift from).
   Needs harness work: a struct result cannot pass through a C out-parameter, and
   `build.py` hard-codes three C TUs.
4. Then Wave 2 (p03–p10, bounds breadth). Open cross-cutting issues are listed at
   the top of `.memory/06-catalogue.md`.

## State

- `harness/` — `check.py` (now ~13 stages incl. clause deletion, `requires`
  strength, the verified twin, and region-actually-runs), `asm.py`, `dloop.py`,
  `vparse.py`, `build.py`, `measure.py`, `report.py`, `fixture.py`.
- p02 gate `PASS`; **p01 `PASS-WITH-BLOCKED-ROWS`** — Miri is now mandatory for any
  pattern with a trusted item and cannot finish p01's `large.bin` in 180 s. 8 of 9
  inputs checked, ninth documented. Policy working, not a regression.
- `results/p02-buffer-copy.json` is stale (5 commits back). Re-run `measure.py p02`
  **once**, with p16's `common/head1_u64_bytes` already in place, when p16 is
  published — see `.memory/06-catalogue.md` for why the ordering matters.
- Toolchain: Verus `0.2026.08.09.92f466f`, rustc 1.97.1, clang/LLVM 22.1.6,
  valgrind 3.27.1, nightly+Miri, all in `~/tools`, no root. `TOOLCHAIN.md`.
- Commits run through `98da583`. Tree clean.

## Decisions

- **Proof-effort budget**: one engineer session per R5 cell, then stop and report
  where the proof stuck — that report *is* the deliverable for that row. Set by the
  manager, pending a user override.
- **`perf_event_paranoid ≤ 1` needs root and is still owed by the user.** It is the
  only way to explain *why* gcc's shorter loop runs slower. Nothing works around it.
