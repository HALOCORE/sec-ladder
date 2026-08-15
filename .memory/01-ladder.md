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

## The structural findings (established by `pilot/`, do not re-litigate)

1. **A Verus proof costs zero instructions.** Ghost code, `requires`, `ensures`,
   invariants, `decreases` all erase. Established at the pilot, corrected at
   TASK_001, and independently re-derived at TASK_001_REVIEW **on the raw
   machine-code bytes** — the only oracle that can establish this (normalised text
   collides; see `.memory/03-measurement.md`):

   | | static raw | static padding-excl | raw-byte md5 |
   |---|---|---|---|
   | R2 safe / R2 verified-safe | 57 / 57 | 46 / 46 | `935221a8…` both |
   | R4 unsafe / R5 verified-unsafe | 37 / 37 | 33 / 33 | `98e4a665…` both |

   Executed instructions (`Ir`) equal too. *(The pilot's published 58/38/33 are
   each one too high — the old pipeline counted the symbol header line.)*

   **Two digest conventions exist; always say which.** `935221a8…`/`98e4a665…`
   are `harness/asm.py`'s `md5_raw`, which includes trailing alignment padding;
   `e5310297…`/`a23e076c…` are the `nm --print-size` extent, i.e. the function
   proper. Both are reproducible (TASK_002 claimed the latter was not — it was
   wrong, TASK_002_REVIEW re-derived them first try). The counts and the
   equalities are unaffected either way. See `.memory/03-measurement.md`.

   Reproduced independently on p01 (TASK_002), `-O3 isolated`:
   R4 ≡ R5 `fb90a96c…` (39 raw / 34 padding-excluded) and
   R2 ≡ R2v `6c85987d…` (59 / 47), both bit-exact.
2. **A proof buys nothing on its own.** Proving R2 panic-free leaves every bounds
   check in place — rustc never learns what Z3 knew. The win only materialises
   when the proof *licenses unsafe code* (R5 = R4 codegen + discharged obligations).

3. **The static safe-vs-unsafe gap is mostly not a dynamic gap, and the tuned safe
   rung nearly closes it.** (TASK_001, corrected at TASK_001_REVIEW.) On the pilot
   kernel at `-O3`, LLVM hoists the bounds check clean out of the vectorised loop,
   so the safety tax is **O(1) per call, not O(n)** — confirmed across
   n = 999 … 100 000. The static delta is prologue, panic landing pad and padding.

   Magnitudes, per call, versus unsafe R4:

   | rung | static raw | static padding-excl | executed `Ir` delta |
   |---|---|---|---|
   | R2 safe-naive (`v[i]`) | +20 | +13 | **+7 … +22** |
   | R3 safe-tuned (iterator) | +24 (largest of *all* rungs) | +16 | **+6 … +8** |

   Three traps here, all of which bit the first write-up:

   - **The delta is not a constant.** It varies with `n mod 4`: 22 / 7 / 9 / 11 for
     residues 0 / 1 / 2 / 3. R2's vectoriser peels a 4-element scalar epilogue when
     `n % 4 == 0`; R4 does not. The original "+22, independent of n" came from three
     data points that were all ≡ 0 (mod 4). Quote a range, or state the residue.
   - **Quote the padding-excluded static number**, or say which you are quoting.
     `.memory/03-measurement.md` calls the raw count overstated; do not then
     headline the raw gap.
   - **R3 is the honest comparison for "what safe Rust costs."** Idiomatic
     iterator code lands within ~6 instructions per call of unsafe while being
     *statically the largest cell in the ladder* — a sharper refutation of
     static-count-as-proxy than the gcc/clang one. Reporting R2 alone overstates
     safe Rust's cost by ~3.7×. **Never publish a safety-cost claim without R3.**

   Reproduced on p01 at TASK_002, with the residue effect measured properly this
   time (16 window lengths, `inputs/gen.py --sweep`), `-O3 isolated`, per call:

   | rung | res 0 | res 1 | res 2 | res 3 |
   |---|---:|---:|---:|---:|
   | R2 safe-naive | **+29** | +11 | +13 | +15 |
   | R3 safe-tuned | +5 | +4 | +4 | +4 |
   | R5 verus | 0 | 0 | 0 | 0 |
   | R1 gcc | +368 … +384 (≈ +41%) | | | |

   Constant in `win_len` within a residue class (+29 at 500, 504, 508 *and* 512),
   so the tax is per call, not per element. **Give every pattern's `small` and
   `large` inputs different residues mod 4** — p01's first draft used 500 and
   4096, both ≡ 0, which is the single worst residue for R2 and would have
   overstated it 2.4×. That is the third time this trap has been stepped in.

   One new caveat: the +29 is the *out-of-line* figure. In `whole` mode on
   `large`, R2's inlined kernel costs ≈ **+340** per call — its scalar epilogue
   keeps a live per-element bounds check and the driver's `div` is
   rematerialised. R3 and R5 show no such amplification. Derived from a
   difference of two builds, so: an observation, not a settled result.

   Do **not** generalise any of this to patterns with data-dependent indices — the
   interesting patterns are precisely the ones where LLVM cannot hoist, and that is
   where the ladder earns its keep.

So the research question is **not** "does verification cost performance" (it
doesn't). It is: *what must move into the trusted base to reach C's assembly, how
much proof keeps that base sound, and which C patterns resist this treatment.*

## Build matrix

Primary, per pattern: **6 cells × 2 opt levels × 2 inline modes = 24 builds** —
the 5 rungs, with R1 built twice (gcc and clang).

| Axis | Values |
|---|---|
| opt | `O0` (non-opt, for reading the lowering) and `O3` (for perf claims) |
| inline mode | `isolated` (kernel in own TU, `#[inline(never)]` / `-fno-inline`, no LTO — this is what we read the assembly of) and `whole` (inlining + LTO on — this is what we time) |

Flags:

- **C**: `-std=c99 -Wall -Wextra` + `-O0` / `-O3`. Build with **both** `/usr/bin/gcc`
  (13.3.0) and `~/tools/llvm/bin/clang` (22.1.6) — clang is the same-backend
  baseline and is mandatory for any C-vs-Rust claim; gcc is the "what a distro
  ships" baseline.
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
- **gcc ≠ LLVM — confirmed, and it is large.** TASK_001 settled the pilot's
  C-vs-unsafe-Rust gap: it is a *backend* artefact. Same `pilot/k.c`, same `-O3`:

  | compiler | static raw | static padding-excl | kernel `Ir` @ n=50 000 | loop shape |
  |---|---|---|---|---|
  | gcc 13.3.0 | 32 | 30 | **125,019** | SSE2, 2 elems/iter, 5 instrs, no unroll |
  | clang 22.1.6 | 33 | 31 | **87,518** | SSE2, 4 elems/iter, 7 instrs, 2× unroll |
  | rustc 1.97.1 unsafe | 37 | 33 | **87,520** | *the same 7-instruction loop body* |

  clang and rustc emit the identical loop body (modulo register allocation and
  addressing-mode scale). The real clang→rustc static delta is **+2 instructions**
  (`lea (,%rdx,8),%rax` + `and $-32,%rax`), not 4 — the other 2 are padding slots.
  And the cause is **not** an `&Vec<u64>` ptr+len reload (LLVM promotes the `&Vec`
  argument in both rungs): rustc's vector loop uses scale-1 *byte* addressing where
  clang uses scale-8 index addressing, so it computes a byte-count bound. An
  induction-variable choice, not an ABI cost. Worth exactly +2 executed
  instructions per call, measured at n = 999 / 4001 / 12345 / 50000.

  **Always report a clang column.** A gcc-only C baseline overstates C's dynamic
  cost here by 43% — gcc emits *fewer* instructions and executes 42.9% *more*.
