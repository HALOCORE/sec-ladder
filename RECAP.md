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

## Working method

Manager (me) writes specs into `.tasks/TASK_NNN.md` and durable context into
`.memory/`. One subagent runs at a time, alternating **research engineer** (does
the work) and **research reviewer** (adversarial, reports but never fixes). The
manager applies `.memory/` corrections, commits at task boundaries, never pushes.

**This alternation is the thing producing the quality. Do not skip the review.**
Six review cycles, six times real defects were found in work that had already
reported success — including twice that a *green gate* was certifying nothing.
Engineers have pushed back on my instructions with measurements five times and
were right all five. Ask to be corrected, not obeyed.

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
   +10 Ir/call flat vs unsafe on p02 and ~+6 on p01 — three patterns running.
   The hardened-C check costs +5 (gcc) / +12 (clang), flat.
5. **Static instruction counts are not a cost model.** Twice the static ranking
   inverted the dynamic one. gcc emits fewer instructions than clang and executes
   43% more; tuned safe Rust is the *largest* cell in p01's ladder.
6. **`Ir` and wall clock can disagree in direction** — gcc beat clang by 10% on
   `Ir` and lost by 23% on wall clock (p02). Report both.

## Retracted (do not reinstate)

- **"Safe-naive Rust pays an O(n) bounds-check tax"** (p02). Refuted by
  decomposition: the indexed fold's bounds checks cost *zero*; the whole delta was
  a subtraction-first bounds check defeating LLVM's memcpy idiom recognition. Real
  finding: **codegen fragility** — one spelling loses the idiom, three others,
  including the reslice a competent programmer writes, are +10 flat.
- **"C beats Rust"** (pilot). A gcc-vs-LLVM artefact with the sign reversed.
- Various digest/count errors; see `.memory/01-ladder.md` and `/03-measurement.md`.

## The recurring traps

- **A green gate is evidence about the gate.** Two reviews got six and seven
  distinct defects past a fully green run.
- **Declared pins are self-certifying.** Anything the pattern author writes in
  `spec.md` moves with the code it constrains. Derive pins where possible; the
  Miri cross-check (declared value tested against a measured one) is the model.
- **Verus verifying is not evidence the spec says anything.** Three vacuity modes
  found: an `external_body` `requires` whose deletion moves no obligation count; a
  free `ensures` whose deletion changes nothing; a rewritten clause that injects a
  *usable* false fact (not vacuity — worse, because nothing downstream looks
  wrong). Gate step 5c (clause deletion) narrows but does not close this.
- **Residues.** p01 tripped mod 4 three times; p02's real modulus was 16, with a
  constant 179-Ir sawtooth. Sweep two full cycles; never sample two points.
- **Attribute nothing without decomposing.** Change one loop at a time.

## Where things stand

- `harness/` — `check.py` (10 stages), `asm.py`, `dloop.py`, `vparse.py`,
  `build.py`, `measure.py`, `report.py`, `fixture.py`. Both patterns green on
  complete runs.
- `patterns/p01-array-sum` (calibration), `patterns/p02-buffer-copy` (first real
  bug). `pilot/` is frozen evidence — do not build on it.
- Toolchain: Verus `0.2026.08.09.92f466f`, rustc 1.97.1, clang/LLVM 22.1.6 (bit-for-bit
  rustc's LLVM), valgrind 3.27.1, nightly+Miri. All in `~/tools`, no root. See
  `TOOLCHAIN.md`.

## Immediate queue

1. **TASK_006 follow-ups the engineer flagged**: `p01/NOTES.md:137` publishes a
   stale digest (`f8e1fe32…`; actual `12d307f2b9d1` since the barrier swap);
   `measure.py`/`report.py` not re-run since (numbers stand — kernels are
   byte-identical — but a `work/call` label predates a `describe()` change).
2. **Wave 1 continues**: p16 TLV walker, p17 HTTP Range parser (mirrors
   CVE-2017-7529 and has a LearnVeri port to lift from).
3. Open cross-cutting issues are listed at the top of `.memory/06-catalogue.md`.

## Decisions still owed by the user

- **`perf_event_paranoid ≤ 1`** needs root. It is the only way to explain *why*
  gcc's shorter loop runs slower — no IPC, branch-miss or cache-miss data without it.
- **Proof-effort budget per R5 cell.** Wanted: a hard cap, past which we record
  where the proof stuck and move on. The pointer-heavy patterns (p27–p34) will hit it.
