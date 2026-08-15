# sec-ladder — prototype plan

A micro-benchmark for the **performance ↔ memory-safety tension** in systems
languages. For each common C pattern we build the same program at five points on
a "security ladder", compile each at two optimisation levels, and study the
resulting assembly, instruction counts and wall-clock time.

| # | Rung | What it represents |
|---|------|--------------------|
| 1 | **C** | the baseline: no language-level safety |
| 2 | **safe Rust, naive** | the mechanical/idiomatic port a working programmer writes first |
| 3 | **safe Rust, tuned** | the same, rewritten to help LLVM elide checks (iterators, slices, `chunks_exact`) |
| 4 | **unsafe Rust** | `get_unchecked` / raw pointers — C performance, C-level (un)safety |
| 5 | **unsafe Rust + Verus** | rung 4's machine code, with an SMT proof that the unsafe preconditions hold |

× {non-opt, opt} = **10 cells per pattern**.

The thesis to test: *rung 5 gives you rung 4's assembly with rung 2's safety
guarantee, paid for at compile time in proof effort rather than at run time.*

---

## Status: feasible — pilot confirms the core claim

Before planning further I built the ladder for one trivial kernel
(`acc += v[i]` over a run-time-sized `Vec<u64>`/array). Sources in `pilot/`,
method in `TOOLCHAIN.md`. Kernel body at `-O3` / `opt-level=3`, `#[inline(never)]`,
x86-64:

| Cell | Static instrs (raw / padding-excl) | Executed `Ir` @ n=50 000 | Notes |
|---|---|---|---|
| C, gcc 13.3.0 `-O3` | 32 / 30 | **125,019** | SSE2, 2 elems/iter, no unroll |
| C, clang 22.1.6 `-O3` | 33 / 31 | **87,518** | SSE2, 4 elems/iter, 2× unroll |
| safe Rust (`v[i]`) | 57 / 46 | 87,542 | bounds check hoisted out of the loop; panic pad |
| safe Rust *verified in Verus* | 57 / 46 | 87,542 | **byte-identical to plain rustc** |
| safe Rust, tuned (iterator) | 61 / 49 | 87,526 | statically the largest cell in the ladder |
| unsafe Rust (`get_unchecked`) | 37 / 33 | 87,520 | same 7-instruction loop body as clang |
| unsafe Rust **+ Verus proof** | 37 / 33 | 87,520 | **byte-identical to plain unsafe Rust** |

All cells produce the same answer. Numbers independently re-derived at
TASK_001_REVIEW; identity established on **raw machine-code bytes**, since the
normalised-text digest can collide (`.memory/03-measurement.md`).

Two results fall out immediately, and they are the backbone of the whole study:

1. **A Verus proof costs exactly zero instructions.** Ghost code, `requires`,
   `ensures`, invariants and `decreases` are erased; the emitted code is
   byte-for-byte what rustc emits for the same exec code. Verified-safe-Rust ==
   safe-Rust, verified-unsafe-Rust == unsafe-Rust.
2. **A Verus proof also buys you nothing on its own.** Proving the safe version
   panic-free does *not* remove the bounds check — rustc never learns what the
   SMT solver knew (57 instrs either way). The performance only arrives when the
   proof is used to *license unsafe code*: rung 5 = rung 4's assembly, with
   `i < v.len()` discharged at every access by the verifier instead of by the CPU.

3. **On this kernel, safety is nearly free anyway — which is a warning about the
   method, not a conclusion about Rust.** LLVM hoists the bounds check clean out of
   the vectorised loop, so safe-vs-unsafe costs 7–22 executed instructions *per
   call* regardless of `n`, and the tuned safe rung cuts that to ~6 while being
   statically the *largest* cell in the ladder. Static instruction counts are not a
   cost model. The patterns that matter are the ones where LLVM **cannot** hoist —
   data-dependent indices, aliasing, pointer chasing — and that is where the
   catalogue is aimed.

So the interesting axis is not "does verification slow things down" (it doesn't)
but **what you must move into the trusted base to get C's assembly, and how much
proof it takes to keep that base sound.** In the pilot the entire unsafe TCB is
one 3-line wrapper:

```rust
#[verifier::external_body]                    // body trusted, not verified
fn get_unchecked(v: &Vec<u64>, i: usize) -> (r: u64)
    requires i < v.len(),                     // ...but every caller must prove this
    ensures  r == v[i as int],
{ unsafe { *v.get_unchecked(i) } }
```

**"TCB lines" and "proof lines per exec line" therefore become first-class
metrics**, alongside cycles. That is the measurement the perf-vs-security
literature is usually missing, and it is what makes this benchmark worth building.

The pilot's own TCB tally was wrong in the first write-up — three `external_body`
items (`get_unchecked`, `out`, `main`), not one — and that under-count concealed a
fatal defect: with `main` external, **no call site ever had to satisfy the kernel's
precondition**, so the proof constrained nothing and the published run printed a
value its own `ensures` forbids. The machine code was fine; the label was not. The
rules that now prevent this are in `.memory/02-bench-rules.md` ("Proof domain must
cover the measured domain"), and `harness/check.py` enforces them. p01 supersedes
the pilot.

The C-vs-Rust gap is *not* a language cost — it is **gcc vs LLVM**, and the first
framing had the sign backwards. gcc emits *fewer* static instructions (32 vs 37)
and executes **42.9% more** (125,019 vs 87,520). clang, which shares rustc's exact
LLVM 22.1.6, emits the identical 7-instruction loop body as unsafe Rust; the whole
residual static gap is +2 instructions from an induction-variable choice. Every
C-vs-Rust claim needs a clang column. See "Threats to validity".

---

## Benchmark program design

Each pattern is one program with a hard split:

```
inputs/<case>.bin  →  driver (reads file, loops, folds result)  →  kernel (the pattern)
```

Rules, so that nothing is optimised away and the ladder stays comparable:

- **All data and all loop bounds come from a file named in `argv`.** Nothing is a
  compile-time constant, so no cell can be partially evaluated to its answer.
- **The result is consumed**: fold every kernel return into a checksum and print
  it. Cross-check that all 10 cells print the same checksum for the same input —
  this is the correctness gate for the port, and it catches silent UB in rung 1/4.
- **Two build modes per cell**, measured separately, because they answer
  different questions:
  - *isolated* — kernel in its own TU, `#[inline(never)]` / `-fno-inline`, no LTO.
    This is what we read the assembly of.
  - *whole-program* — inlining and LTO on. This is what we time; it is what a real
    program gets, and it is where safe Rust sometimes wins back the check.
- **Input set per pattern**: `small` (fits L1), `large` (streams from memory),
  and `adversarial` — the input that triggers the C bug (overflow, OOB, wrap).
  The adversarial case is where the ladder stops being about speed: rung 1
  corrupts memory, rung 2 panics, rung 5 is proven not to reach either.

---

## Proposed pattern catalogue

Ordered by expected Verus difficulty. Start with the first three end-to-end
before widening — the aim is depth on a few, not shallow coverage of ten.

| # | Pattern | C bug class it models | Verus difficulty |
|---|---------|----------------------|------------------|
| 1 | array reduce / prefix scan | none (calibration) | trivial |
| 2 | length-prefixed buffer copy (`memcpy` with attacker length) | spatial OOB | easy |
| 3 | byte parser — `Range:` style header with integer arithmetic | int overflow → OOB (cf. CVE-2017-7529) | easy–moderate |
| 4 | binary search | midpoint overflow | moderate |
| 5 | ring buffer with wraparound | modular arithmetic, aliasing | moderate |
| 6 | 2-D index flattening / matmul (`i*n+j`) | overflow in index math | moderate |
| 7 | open-addressing hash table | capacity mask, probe termination | moderate–hard |
| 8 | in-place partition / quicksort | swaps, aliasing, permutation invariant | hard |
| 9 | arena allocator with interior pointers | provenance, lifetimes | hard (`vstd::raw_ptr`) |
| 10 | intrusive linked list | aliasing, ownership | research-grade — expect to document failure |

Cells 9–10 may not be provable within a sane budget. **That is a result, not a
setback** — "which C patterns resist verification" is exactly what a paper on
this landscape should report. Every pattern gets a proof-effort budget; when it
is exhausted we record where the proof got stuck and move on.

LearnVeri's `microbench/` already has 20 CVE ports with security proofs; patterns
2, 3 and 7 can lift their kernels rather than starting from scratch.

---

## Measurement methodology

This box constrains us (see `TOOLCHAIN.md`): shared 80-core Xeon, `powersave`
governor, `perf` not installed and `perf_event_paranoid=3`, so **hardware
counters are unavailable**. Plan around that:

- **Primary (deterministic): static kernel instruction count + assembly diff.**
  Works today, zero noise, and it is the artifact we actually want to read.
- **Primary (dynamic, recommended): executed-instruction count via callgrind.**
  Deterministic, immune to a noisy neighbour. Valgrind isn't installed but builds
  from source into `~/tools` without root — *pending your go-ahead*.
- **Secondary: wall clock**, `taskset`-pinned to one core, ≥ 30 reps, report min
  and median (not mean), interleaving cells to spread drift. Treat as a sanity
  check on the instruction counts, not as the headline number.
- Hardware counters (IPC, branch misses, cache misses) would need
  `perf_event_paranoid ≤ 1` — root. Worth asking for; the branch-miss column is
  genuinely interesting for the bounds-check cells.

**Per-cell metrics recorded**: kernel instruction count · executed instructions ·
wall time (min/median) · binary size · exec LOC · proof+spec LOC · TCB lines
(`unsafe` + `external_body`) · Verus verification time · qualitative asm notes
(bounds check present? panic landing pad? vectorised? unrolled?).

---

## Threats to validity (and what we do about them)

1. **gcc vs LLVM is not a language comparison.** ✅ **Resolved (TASK_001).** clang
   22.1.6 — the exact LLVM rustc 1.97.1 uses — is installed. The pilot's apparent
   C-beats-Rust gap was entirely backend, with the sign backwards: gcc emits fewer
   instructions and runs 42.9% *slower*. A clang column is now mandatory on every
   C-vs-Rust claim; gcc stays as the "what a distro ships" baseline.
2. **"Non-opt" C and "non-opt" Rust are not the same experiment.** Debug Rust
   inserts *overflow checks*, a semantic difference, not just an unoptimised
   lowering. → Build non-opt cells both with and without `-C debug-assertions`,
   and say plainly that the non-opt row is for *reading the lowering*, not for
   perf claims.
3. **Kernel-isolated numbers overstate the cost of safety.** Real programs inline;
   LLVM often hoists a bounds check out of a loop it can see whole. → Hence the
   two build modes; report both.
4. **One trivial kernel proves nothing about the general case.** The pilot is a
   calibration point, not evidence. → Depth-first on patterns 2–5.
5. **The trusted base is where the safety actually goes.** An `external_body`
   wrapper can silently be *wrong* (a bad `ensures` axiomatises a falsehood). →
   TCB lines are reported per cell, and every `external_body` gets a written
   justification. A rung-5 cell with a 200-line TCB is not a win and must not be
   presented as one.
6. **Noise.** Shared box, frequency scaling. → Pinning, min-of-N, and
   instruction counts as the primary metric.
7. **Static instruction counts are not a cost model.** Twice now the static ranking
   has inverted the dynamic one: gcc is smaller and slower than clang, and the
   tuned safe Rust rung is the *largest* cell in the ladder while being within ~6
   executed instructions of unsafe. → Never publish a static count without a
   paired `Ir`, and always report both raw and padding-excluded counts.
8. **"Identical machine code" needs the right oracle.** The normalised-text digest
   erases every immediate and displacement — TASK_001_REVIEW built two kernels with
   different *answers* and the same normalised md5. → Identity claims cite the raw
   machine-code bytes; normalised text is for reading diffs only.
9. **A verified cell can be measured outside its proof.** The pilot's R5 had no
   verified call site and its published run falsified its own postcondition. →
   `.memory/02-bench-rules.md` "Proof domain must cover the measured domain",
   enforced by `harness/check.py`.
10. **Reporting only the naive safe rung inflates safety's cost.** R2-vs-R4 on the
   pilot overstates it ~3.7× versus R3-vs-R4. → No safety-cost claim ships without
   the R3 column.

---

## Repo layout

Authoritative version: `.memory/05-layout.md`. Operational context for agents lives
in `.memory/` (environment, ladder definition, bench rules, measurement protocol,
Verus notes, layout, pattern catalogue); task specs and reviews in `.tasks/`.

## Phases

- **P0 — toolchain + pilot.** ✅ Done. Verus 0.2026.08.09, clang 22.1.6, valgrind
  3.27.1 installed; ladder validated; pilot measured, reviewed, and its defects
  turned into rules.
- **P1 — harness + p01 (TASK_002).** `harness/{asm,build,check,measure,report}.py`
  plus the first real pattern as the template all 47 clone from.
- **P2 — Wave 1 patterns**: p02 buffer copy, p16 TLV walker, p17 HTTP Range parser.
  First results table; first adversarial-behaviour table.
- **P3 — Waves 2–5**, breadth across families A–D and G.
- **P4 — Wave 6**, the pointer-heavy patterns where R5 is expected to fail; record
  where the proofs get stuck.
- **P5 — cross-pattern analysis and writeup.**

Full pattern list, difficulty and status: `.memory/06-catalogue.md`.

## Open decisions

1. ~~clang as a second C baseline~~ — done, and it changed the headline result.
2. ~~valgrind for callgrind~~ — done; `Ir` is now the primary dynamic metric.
3. **Ask for `perf_event_paranoid ≤ 1`?** Still open, still needs root. Without it
   there is no IPC, branch-miss or cache-miss data — which is the one thing that
   could explain *why* gcc's shorter loop runs slower. Everything else is covered.
4. **Proof-effort budget per cell** — proposed: a hard cap per R5 cell, past which
   we record the sticking point and move on. Needs a number from you.
