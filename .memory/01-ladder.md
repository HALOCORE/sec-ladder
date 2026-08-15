# The ladder — five rungs, precisely defined

Every pattern is implemented five times. The rungs must be **semantically
equivalent on well-formed input** (same checksum) and differ only in what
enforces memory safety.

| Rung | Dir/file stem | Definition |
|---|---|---|
| **R1 C** | `c/` | Idiomatic C99. No bounds checks. Written the way a competent systems programmer writes it — *including* the bug class the pattern is about, if the pattern models one. |
| **R2 safe-naive** | `safe_naive.rs` | The mechanical port a working Rust programmer writes first: `for i in 0..n { ... v[i] ... }`, indexing, `Vec`, no cleverness. Must contain **zero** `unsafe`. |
| **R3 safe-tuned** | `safe_tuned.rs` | Same semantics, rewritten to help LLVM elide checks: iterators, `chunks_exact`, `zip`, slice reslicing, `split_at`, hoisted length assertions. Still **zero** `unsafe`. |
| **R4 unsafe** | `unsafe.rs` | `get_unchecked`, raw pointers, `from_raw_parts` — whatever it takes to reach C's codegen. Unsound-by-inspection is not allowed: it must be *correct*, just unverified. |
| **R5 verus** | `verus.rs` | R4's exec code, plus Verus specs and proofs discharging every unsafe precondition. Ships the same machine code as R4. |

## The two structural findings (established by `pilot/`, do not re-litigate)

1. **A Verus proof costs zero instructions.** Ghost code, `requires`, `ensures`,
   invariants, `decreases` all erase. R5's kernel assembly is byte-identical to
   the equivalent plain-rustc build. Verified once at the pilot: 58 instrs safe
   vs 58 verified-safe; 38 unsafe vs 38 verified-unsafe.
2. **A proof buys nothing on its own.** Proving R2 panic-free leaves every bounds
   check in place — rustc never learns what Z3 knew. The win only materialises
   when the proof *licenses unsafe code* (R5 = R4 codegen + discharged obligations).

So the research question is **not** "does verification cost performance" (it
doesn't). It is: *what must move into the trusted base to reach C's assembly, how
much proof keeps that base sound, and which C patterns resist this treatment.*

## Build matrix

Primary, per pattern: **5 rungs × 2 opt levels × 2 inline modes = 20 builds.**

| Axis | Values |
|---|---|
| opt | `O0` (non-opt, for reading the lowering) and `O3` (for perf claims) |
| inline mode | `isolated` (kernel in own TU, `#[inline(never)]` / `-fno-inline`, no LTO — this is what we read the assembly of) and `whole` (inlining + LTO on — this is what we time) |

Flags:

- **C**: `-std=c99 -Wall -Wextra` + `-O0` / `-O3`. Default gcc; clang as second baseline once available.
- **R2–R4**: `rustc -C opt-level=0 -C debug-assertions=on` / `-C opt-level=3 -C debug-assertions=off`.
- **R5**: `./verus_run.py --compile verus.rs -o <out> -C opt-level=N ...` (same flags as R2–R4).
- `-C codegen-units=1` everywhere for reproducible codegen.
- `panic=unwind` is the default. `panic=abort` is a **secondary axis** (it deletes
  landing pads and is a real safety-cost lever) — build it, report it separately.

### Two traps that invalidate the comparison

- **Debug Rust ≠ C `-O0`.** Debug Rust inserts *integer-overflow checks* — a
  semantic difference, not an unoptimised lowering. So also build R2–R5 at
  `opt-level=0 -C debug-assertions=off` as the semantics-matched `O0` column.
  Never make a perf claim from an `O0` row.
- **gcc ≠ LLVM.** The pilot's C-33 vs unsafe-Rust-38 gap is a vectorisation
  prologue difference, not a cost of Rust. Any C-vs-Rust number without a clang
  column is confounded; label it as such until TASK_001 lands.
