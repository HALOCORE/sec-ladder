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

| Cell | Instructions in kernel | Notes |
|---|---|---|
| C (gcc -O3) | **33** | vectorised, no checks |
| safe Rust (`v[i]`) | **58** | bounds check + panic landing pad, still vectorised |
| safe Rust *verified in Verus* | **58** | **identical, instruction for instruction, to plain rustc** |
| unsafe Rust (`get_unchecked`) | **38** | check gone |
| unsafe Rust **+ Verus proof** | **38** | **identical, instruction for instruction, to plain unsafe Rust** |

All five binaries produce the same answer. Two results fall out immediately, and
they are the backbone of the whole study:

1. **A Verus proof costs exactly zero instructions.** Ghost code, `requires`,
   `ensures`, invariants and `decreases` are erased; the emitted code is
   byte-for-byte what rustc emits for the same exec code. Verified-safe-Rust ==
   safe-Rust, verified-unsafe-Rust == unsafe-Rust.
2. **A Verus proof also buys you nothing on its own.** Proving the safe version
   panic-free does *not* remove the bounds check — rustc never learns what the
   SMT solver knew (58 instrs either way). The performance only arrives when the
   proof is used to *license unsafe code*: rung 5 = rung 4's assembly, with
   `i < v.len()` discharged at every access by the verifier instead of by the CPU.

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

The 33-vs-38 C/Rust gap is *not* a language cost — it is gcc vs LLVM codegen
(different vectorisation prologue). See "Threats to validity".

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

1. **gcc vs LLVM is not a language comparison.** The pilot's 33-vs-38 gap is
   backend, not safety. → Add **clang** as a second C baseline so at least one
   comparison is same-backend. Installable without root from an LLVM release
   tarball; report gcc and clang both.
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

---

## Repo layout (proposed)

```
sec-ladder/
  PLAN.md  TOOLCHAIN.md  verus_run.py
  pilot/                        # the calibration kernel, all 5 rungs
  patterns/pNN-<name>/
    README.md                   # the pattern, the C bug, expected findings
    inputs/{small,large,adversarial}.bin
    c/                          # kernel.c + driver.c + Makefile
    rust-safe-naive/  rust-safe-tuned/  rust-unsafe/  rust-verus/
    expected/checksums.txt
  harness/
    build_all.py                # every cell × both opt levels
    check.py                    # all cells agree on every input
    measure.py                  # instr counts, callgrind, timing → results/*.json
    asm.py                      # extract + normalise + diff kernel assembly
  results/                      # committed JSON + generated tables
```

## Phases

- **P0 — toolchain + pilot** ✅ done (Verus 0.2026.08.09 installed, ladder validated).
- **P1 — harness + pattern 2 end-to-end.** Build the `harness/` scripts against
  the pilot, then do the buffer-copy pattern across all 10 cells with the
  adversarial input. This is the template every later pattern is cloned from.
- **P2 — patterns 3–5.** Widen; refine metrics; first results table.
- **P3 — measurement hardening.** callgrind + clang (pending decisions below).
- **P4 — patterns 6–8, then attempt 9–10** with a fixed proof budget; write up
  what resisted verification.

## Decisions I need from you

1. **clang as a second C baseline?** Strongly recommended — without it we cannot
   separate "safety cost" from "gcc vs LLVM". Extractable into `~/tools`, no root.
2. **Build valgrind for callgrind?** Recommended — it is the only deterministic
   dynamic metric available on this box. ~10 min build, no root.
3. **Ask for `perf_event_paranoid ≤ 1`?** Optional; unlocks IPC/branch-miss data.
4. **Pattern order** — I propose 2 → 3 → 5 → 4. Pattern 3 (the header parser) is
   the one that best mirrors a real CVE and has a LearnVeri port to lift from.
5. **Proof-effort budget per cell** — I suggest a hard cap (say 4 h equivalent);
   past it we record the sticking point and move on.
