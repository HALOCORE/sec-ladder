# TASK_001_REVIEW — adversarial review of the measurement tooling

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md` (reviewer checklist + severity), `.tasks/TASK_001.md`
(what was asked), then the changed files.

## What was done (engineer's claims, to be verified — not trusted)

TASK_001 installed valgrind 3.27.1 and clang/LLVM 22.1.6 into `~/tools`, then
re-measured the pilot. It made **five claims that overturn previously published
numbers**, and those numbers have already been written into `.memory/`. If any
claim is wrong, it is now load-bearing for the whole project. Verify each
independently — re-derive, do not re-read.

**Claim 1 — the old asm pipeline was wrong in three ways**, so every published
count (33 / 58 / 38 in `pilot/README.md` and `PLAN.md`) is one too high; the real
counts are 32 / 57 / 37. The three defects alleged: (a) the `<addr> <sym>:` header
line survives the sed and gets counted; (b) objdump prints bare-hex branch targets
with no `0x` prefix so they were never stripped, meaning "identical" was only ever
a count comparison; (c) `int3`/nop padding inside the symbol size is counted as
instructions. **Verify all three by construction**, and confirm the new pipeline in
`.memory/03-measurement.md` actually fixes them without introducing a new defect
(e.g. does `s/\b[0-9a-f]{4,}\b//g` eat legitimate immediates or register names?
`0xdeadbeef` immediates, `movabs`, `%r10`-style operands — check).

**Claim 2 — R5's kernel is md5-identical to R4's** (`fc3741857e5f…`), and R2v to R2
(`570d91b9a9ff…`). Re-derive the md5s yourself. This is the project's headline
structural finding; it must be exactly right.

**Claim 3 — the gcc-vs-LLVM gap inverts the old framing.** gcc 13.3.0 emits 32
static instructions but executes 125,019 Ir at n=50 000, while clang 22.1.6 emits
33 and executes 87,518 — i.e. gcc is ~43% *worse* dynamically, and clang emits the
same 7-instruction loop body as rustc. The old "C 33 beats Rust 38" framing
allegedly had the sign backwards. Verify the Ir numbers and the loop-shape claim.

**Claim 4 — callgrind `Ir` is deterministic per-function but the whole-program
`summary:` line is environment-sensitive** (moves with env block size, argv size,
what stdout is connected to). Verify both halves; this is why the metric
definition in `.memory/03-measurement.md` changed.

**Claim 5 — safe Rust's bounds check costs +20 static instructions but only +22
executed instructions per call, total, independent of n** (LLVM hoists it out of
the vector loop). Verify at a fresh n. Then assess: is the hedge in
`.memory/01-ladder.md` finding 3 strong enough, or does the phrasing invite
over-generalisation to patterns where LLVM cannot hoist?

## The soundness question I most want answered

The headline table was measured at **n = 50 000**, but `pilot/k_unsafe_verus.rs`
carries `requires n < 1000`. So the R5 cell's *proof does not cover the input that
was measured*. The engineer argues the measurement is still valid (`main` is
`#[verifier::external_body]`, Verus emits no runtime precondition check, and the
compiled kernel is md5-identical to R4's) and separately re-ran everything at
n = 999, same conclusions.

Assess this properly:
- Is the argument technically correct?
- Is it *presentable*? A results table whose "verified" cell was measured outside
  its verified domain is exactly the kind of thing that sinks a paper.
- Should the n=999 table be the headline instead, or should the pilot's
  precondition be widened, or is a footnote enough?
- **Generalise it**: should `.memory/02-bench-rules.md` gain a hard rule that a
  proof's preconditions must cover every measured input, and that
  `harness/check.py` must enforce it? Draft the rule if so.

## Also check

- **Scope/hygiene**: `pilot/` genuinely untouched (`git diff -- pilot/`), nothing
  staged or committed, no writes outside `.temp/` and `~/tools/` and the named docs.
- **Doc accuracy**: `TOOLCHAIN.md`, `.memory/00-environment.md`,
  `.memory/01-ladder.md`, `.memory/03-measurement.md` — do they say what was
  actually measured? Any claim stronger than its evidence? Any stale text left
  behind that now contradicts the new numbers?
- **Reproduction commands** in `TOOLCHAIN.md`: run them. Do they work from a clean
  output dir, exactly as written?
- **Disk**: LLVM is 12 GB. Confirm free space is genuinely fine, and whether the
  untrimmed install is defensible.
- **The gaps the engineer self-reported** — no wall-clock column, no `results/*.json`,
  no R3 (safe-tuned) cell in the pilot, only `-O3`/`isolated` measured. Are these
  correctly out of scope for TASK_001, or does one of them undermine a stated
  conclusion?
- `PLAN.md` and `pilot/README.md` still publish the old 33/58/38 and the old
  gcc-vs-LLVM framing. The manager will fix these — **tell me precisely which
  lines are now false**, so the correction is complete rather than approximate.

## Deliverable

Findings ranked `blocker` / `major` / `minor` per `.tasks/PROTOCOL.md`, each with
file:line and a concrete failure scenario. Include a short "verified correct"
list — the claims you checked and found sound — so I know what has actually been
independently confirmed rather than merely unchallenged. Do not fix anything.
