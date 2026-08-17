# RECAP — state of the research programme

For a manager picking this up cold. Read this, then `.memory/` 00–06, then
`.tasks/PROTOCOL.md`. **The `.memory/` files are authoritative and supersede any
task report they contradict** — several reports contain claims that were later
refuted, and the refutations live in `.memory/`.

## What this is

A micro-benchmark for the performance ↔ memory-safety tension. Each common C
pattern is built at five rungs — C, safe Rust (naive), safe Rust (tuned), unsafe
Rust, unsafe Rust + Verus proof — plus a sixth **R1h** hardened-C cell, across two
optimisation levels and two inline modes, and compared on assembly, executed
instructions, timing, proof burden and trusted-base size.

47 patterns are catalogued in `.memory/06-catalogue.md`. **Two exist.**

That ratio is the thing to understand before judging the pace. Eight tasks have
run; four were harness or gate work with no new pattern, because four separate
reviews demonstrated that the gate was certifying nothing. The infrastructure is
now load-bearing in a way it demonstrably was not at task 3.

## Working method

Manager (me) writes specs into `.tasks/TASK_NNN.md` and durable context into
`.memory/`. One subagent runs at a time, alternating **research engineer** (does
the work) and **research reviewer** (adversarial, reports but never fixes). The
manager applies `.memory/` corrections, commits at task boundaries, never pushes.

**This alternation is the thing producing the quality. Do not skip the review.**
Every review has found real defects in work that had already reported success —
four times in work certified by a *fully green gate*, twice with a `contract
sha256` identical to the shipped pattern.

**Engineers have contradicted my written instructions six times, with
measurements, and were right all six.** The most recent is the sharpest: I
specified a `requires` mutation test as "delete it and confirm some call site
fails". That is impossible for a trusted item — deleting a precondition only
*removes* obligations from callers, so nothing fails — and had it shipped it
would have reported every trusted precondition in the project as
not-load-bearing. **Ask to be corrected, not obeyed**, and say so in the task
file; it is why this keeps working.

Reviewers are also asked to report **clean negatives** on named attacks, so the
next agent does not re-run them. Several of the most useful results are negatives.

## Established results (survived adversarial review)

1. **A Verus proof costs exactly zero instructions.** Ghost code erases; R5's
   kernel is byte-identical to the equivalent plain-rustc build, on both p01 and
   p02, verified on raw machine-code bytes.
2. **A proof buys nothing on its own.** Proving safe Rust panic-free leaves every
   bounds check in place. The win arrives only when the proof *licenses unsafe
   code*: R5 = R4's machine code with the obligations discharged by the verifier.
3. **p02's security result.** On a one-byte overflow, idiomatic C prints a
   plausible answer and exits 0 in **seven of eight builds** — silent heap
   corruption absorbed by glibc's chunk rounding; the eighth aborts only because
   Ubuntu defaults `_FORTIFY_SOURCE 3`. Every hardened-C and Rust cell handles it.
   Control: delete the check from safe Rust and it panics at exit 101 — so "Rust
   makes the check non-optional" is a measurement, not a slogan.
4. **Safety is cheap when the optimiser can see the loop.** Tuned safe Rust is
   +10 Ir/call vs unsafe on p02 (**+8 at `len ≡ 0 (mod 8)`**) and ~+6 on p01 —
   three patterns running. The hardened-C check costs +5 (gcc) / +12 (clang), flat.
5. **Static instruction counts are not a cost model.** Twice the static ranking
   inverted the dynamic one. gcc emits fewer instructions than clang and executes
   43% more; tuned safe Rust is the *largest* cell in p01's ladder.
6. **`Ir` and wall clock can disagree in direction** — gcc beat clang by 10% on
   `Ir` and lost by 23% on wall clock (p02). Report both.
7. **p02's residue curve predicts.** R2−R4 is a sawtooth of amplitude 179 Ir
   resetting at `len ≡ 1 (mod 16)` on a 0.21 Ir/byte linear term. Re-derived
   independently at seven lengths the sweep never sampled and at 8× the scale:
   amplitude 178.9, slope 0.2125. This is the only model in the project that has
   been tested by prediction rather than by re-measurement.

## Retracted (do not reinstate)

- **"Safe-naive Rust pays an O(n) bounds-check tax"** (p02). Refuted by
  decomposition: the indexed fold's bounds checks cost *zero*; the whole delta was
  a subtraction-first bounds check defeating LLVM's memcpy idiom recognition. Real
  finding: **codegen fragility** — one spelling loses the idiom, three others,
  including the reslice a competent programmer writes, are +10 flat.
- **"C beats Rust"** (pilot). A gcc-vs-LLVM artefact with the sign reversed.
- **"gcc's byte loop beats glibc `memcpy`"** — a mislabelled comparison. It beats
  R4, not gcc's own memcpy build; within one compiler the byte loop is dearer.
- Various digest/count errors; see `.memory/01-ladder.md` and `/03-measurement.md`.

## The recurring traps

- **A green gate is evidence about the gate.** Four reviews now. The two most
  recent bypasses both passed with the contract hash unchanged, which is the
  artefact a human reviewer would have checked.
- **Declared pins are self-certifying.** Anything the pattern author writes in
  `spec.md` or `model.py` moves with the code it constrains. `work_per_call` is
  still an unbounded knob — a 16× shrink passes with only a shout.
- **Verus verifying is not evidence the spec says anything.** Vacuity has three
  distinct modes, and *weakening a trusted `requires` produces no verification
  signature at all* — the file verifies identically. Only the parameter-coverage
  rule catches a missing one. Still open: a `requires` that is non-trivial,
  mentions every parameter and is nonetheless too weak.
- **Fixes that add a regex get bypassed by the next spelling.** `verus!` with
  braces was caught; `verus!` with round brackets was not, and one character
  between two regexes reopened the M9 payload. The fix that held asks Verus.
- **Residues.** p01 tripped mod 4 three times; p02's real modulus was 16. Sweep
  two full cycles; never sample two points.
- **Attribute nothing without decomposing.** Change one loop at a time.
- **Say which columns a staleness argument covers.** "The kernels are
  byte-identical so the numbers stand" was right about every kernel column and
  wrong about `binary_text_bytes` in five cells.

## Where things stand

- `harness/` — `check.py` (10 stages incl. clause deletion 5c and `requires`
  strength 5c-req), `asm.py`, `dloop.py`, `vparse.py`, `build.py`, `measure.py`,
  `report.py`, `fixture.py`. Both patterns green on complete runs.
- `patterns/p01-array-sum` (calibration), `patterns/p02-buffer-copy` (first real
  bug). `pilot/` is frozen evidence — do not build on it.
- Toolchain: Verus `0.2026.08.09.92f466f`, rustc 1.97.1, clang/LLVM 22.1.6 (bit-for-bit
  rustc's LLVM), valgrind 3.27.1, nightly+Miri. All in `~/tools`, no root. See
  `TOOLCHAIN.md`.

## Immediate queue

1. **TASK_008_REVIEW is in flight** — reviewing the two blocker fixes, the new
   mutation stages and the floor bounds. It is also asked to verify the
   engineer's contradiction of my spec *before* it hardens into doctrine.
2. **TASK_007 — p16, the TLV record walker.** Spec written and unblocked. It is
   the first pattern with a **data-dependent loop bound**, which is the case
   `.memory/01-ladder.md` explicitly says not to generalise the "safety is cheap"
   result to. Designed to clear all four of the harness hard stops the reviewer
   identified for parser kernels; the decomposition is mandatory *before* any
   claim, because that is how p02's headline got published and retracted.
3. Then p17 (HTTP `Range`, mirrors CVE-2017-7529, LearnVeri port to lift from).
   It will need harness work: a struct result cannot pass through a C
   out-parameter today.
4. Open cross-cutting issues are listed at the top of `.memory/06-catalogue.md`.

## Decisions

- **Proof-effort budget — set by me at TASK_008, pending user override.** One
  engineer session per R5 cell; then stop and report where the proof stuck, which
  *is* the deliverable for that row. Recorded in `.memory/06-catalogue.md`.
- **`perf_event_paranoid ≤ 1` still needs root, and is still owed by the user.**
  It is the only way to explain *why* gcc's shorter loop runs slower — no IPC,
  branch-miss or cache-miss data without it. Nothing works around it.
