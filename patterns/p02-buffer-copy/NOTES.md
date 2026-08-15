# p02 — findings, adversarial behaviour, TCB tally, sticking points

Gate record: `results/gate/p02-buffer-copy.json` (`verdict: PASS`,
`complete_run: true`, invocation `p02`). Dynamic numbers below are the gate's
**marginal executed instructions per kernel call** — whole-program `Ir` at 200
driver iterations minus `Ir` at 100, over the 100 extra calls — unless a table
says "kernel symbol".

---

## 0. Read this before quoting any performance number

**The copy is a small minority of the kernel's work.** The kernel is a `memcpy`
*and then* a byte-wise checksum of what was copied, and the checksum is the
expensive half. Measured on `large` (4092 bytes per call, `-O3 isolated`), by
subtracting the callgrind per-function exclusive `Ir` of the `kernel` symbol from
the whole-program marginal:

| | c-gcc | c-clang | unsafe |
|---|---:|---:|---:|
| marginal Ir per call (whole program) | 9195.7 | 10192.7 | 10200.8 |
| `kernel` symbol, exclusive | 8765 | 9764 | 9772 |
| difference — driver loop + the `memcpy` in libc | ~431 | ~429 | ~429 |

So the copy is **~4%** of the call and the fold is ~96% (≈0.10 Ir per byte
copied against ≈2.3 Ir per byte folded). The fold does not vectorise in rustc
and barely does in gcc: widening `u8` to `u64` and wrapping-adding is a
`psadbw`-shaped problem that neither backend takes.

That is a property of this kernel, not a defect — a real parser does copy a
record and then scan it — but it means:

- the **security** half of the result is entirely about the copy, and stands;
- the **performance** half is mostly about the fold. "R2 costs +1025 per call"
  (§3) is bounds checks in *two* indexed loops — the copy loop and the fold
  loop — not in the copy alone;
- a future pattern that wants to measure copying specifically should fold over
  `u64` words rather than bytes (~8x cheaper) — at the price of a materially
  harder Verus spec (byte-sequence to `u64` conversion) and of getting close
  enough to the anti-collapse floor to matter. Recorded as a design note, not
  done here.

The fold cannot simply be made cheaper *in extent*: it is what makes the copy
load-bearing, since `dst` is read by nothing else. A fold over only part of
`dst` would leave the rest of the copy dead, and in `whole` mode LLVM can see
that. **Not measured** — stated as the reason the fold covers all of
`dst[0..len)`, not as a result.

---

## 1. The adversarial behaviour table

**This is the security half of the result and the project's first one.** Seven
adversarial inputs, all 32 cells, plus the ASan/UBSan build and the Verus proof.
Rungs R2–R5 and R1h are identical on every input, so they are one column;
divergence is R1's alone.

`sanitizer_expect` is **derived** by `model.py`, not tabulated: an input is
"fires" exactly when the simulated run contains a call the rejection test
rejects, which is exactly a call on which R1 runs off the end of a buffer. On a
"fires" input, sanitizer silence is a gate failure.

### 1a. The three inputs that reach the bug

| input | what it is | R1 (`c-gcc`, `c-clang`) | R1h, R2, R3, R4, R5 | ASan/UBSan on R1 |
|---|---|---|---|---|
| `adversarial.bin` | every record claims `len = 65535`, `cap = 64` | **exit 134 (SIGABRT), no stdout**, `malloc(): invalid size (unsorted)` — or, `gcc -O3 whole`, `*** buffer overflow detected ***` | exit 0, prints `0` | **fires**: `heap-buffer-overflow`, `READ of size 65535`, 0 bytes after the 12600-byte source region |
| `adversarial-cap1.bin` | `len = cap + 1 = 65`; the record's bytes are all present, so the destination bound is the only thing violated, by one byte | **exit 0, prints `198979479034752`** in 7 of 8 builds — a plausible-looking wrong number, no diagnostic, no crash. `gcc -O3 whole` alone aborts | exit 0, prints `0` | **fires**: `heap-buffer-overflow`, **`WRITE of size 65`, 0 bytes after the 64-byte region allocated by `slb_zeroed`** |
| `adversarial-srcend.bin` | `len = 61 <= cap`, but the record's body runs off the end of a 40-byte source blob | **exit 0, prints `144602631418632`** in all 8 builds. Silent | exit 0, prints `0` | **fires**: `heap-buffer-overflow`, `READ of size 61`, 0 bytes after the 40-byte source region |

### 1a′. …and what happens if safe Rust omits the check

R2–R5 all carry the *same* three-term rejection test R1h does, so **no Rust rung
panics on any input** — the language's bounds checks are never reached, because
the code is correct rather than merely safe. That makes "Rust makes the check
non-optional" an assertion rather than a measurement, so it was measured:
`safe_naive.rs` with the `if len > dst.len() || ...` deleted and nothing else
changed (diagnostic build, not a cell in the matrix, kept here rather than in
the tree):

| input | R1 (C, same omission) | R2 with the check deleted |
|---|---|---|
| `small.bin` | `15997819096698035934` | `15997819096698035934` — identical, so it is the same program on well-formed input |
| `adversarial-cap1.bin` | exit 0, wrong answer, silent | **exit 101**, `panicked at safe_naive.rs:23:9: index out of bounds: the len is 64 but the index is 64` |
| `adversarial.bin` | exit 134, heap corruption | **exit 101**, same panic |
| `adversarial-srcend.bin` | exit 0, wrong answer, silent | **exit 101**, `index out of bounds: the len is 40 but the index is 40` — and it names the *source* read, i.e. the language located which of the two bounds was violated |

So the difference between the two languages on this bug is not that one
programmer remembered the check: it is that the **same omission** produces a
one-byte heap write and a plausible wrong answer in C, and a named, immediate,
non-exploitable abort in Rust. That is the whole claim, and it is now a
measurement.

The `adversarial-cap1` row is the one to keep. A **one-byte** heap overflow
lands inside glibc's chunk rounding (a 64-byte request gets 72 usable bytes), so
nothing is corrupted, nothing is detected, and the program returns a wrong
answer with exit 0. The 65 535-byte overflow is loud because it destroys the
next chunk header; the one-byte one is the realistic case and it is invisible.

Two secondary observations, both recorded rather than smoothed over:

- **R1's behaviour is not a function of the source, it is a function of the
  build.** `c-gcc` disagrees with itself across `(opt, mode)`: three builds
  print a wrong number on `adversarial-cap1` and `-O3 whole` aborts. The gate
  reports this as a note ("opt/mode variants of this rung disagree"). It is
  undefined behaviour; there is no "the" behaviour.
- **The one abort at `gcc -O3 whole` is the distribution's `_FORTIFY_SOURCE`,
  not the program.** Debian's gcc enables it at `-O`, so the `memcpy` becomes
  `__memcpy_chk`; with LTO the destination's allocated size is visible at the
  call and the check fires. `harness/build.py` passes no `-D_FORTIFY_SOURCE`
  either way. clang does not do this and is silent in all four builds. So
  "hardening caught it" here is a distro default that catches 1 of 8 builds of
  1 of 3 attacks.

### 1b. Everything else

| input | what it is | all 32 cells |
|---|---|---|
| `adversarial-cap.bin` | `len == cap` exactly — **legal**, the boundary from the safe side | exit 0, `244239563421568`, identical everywhere; ASan clean. A rung that wrote `len >= cap` would diverge here |
| `adversarial-stride1.bin` | `stride = 1`: a record too small to hold its own prefix | exit 0, prints `0`; the driver guard skips the loop, zero kernel calls |
| `adversarial-capbig.bin` | declared `cap = 2^40` | exit 7, message on stderr, in **both languages** — the capacity is range-checked before the allocation, so C's `calloc` returning `NULL` and Rust's allocator aborting never happens |
| `adversarial-shortlen.bin` | `payload_len` declares 4096 bytes more than the file carries | exit 5, message on stderr, everywhere |

### 1c. What R5 rules out, precisely

The proof is not "the program does not crash". It is the postcondition

```
final(dst)@ =~= copy_dst(old(dst)@, src@, src_off as int)
```

which pins the **whole** destination sequence. Unfolding `copy_dst`:

- if the record fits — `dst[0..len)` is the record and **`dst[len..cap)` is
  byte-for-byte what it was before the call**;
- if it does not fit — `dst` is *entirely* unchanged, so `adversarial.bin`,
  `adversarial-cap1.bin` and `adversarial-srcend.bin` cannot write anything at
  all;
- either way `final(dst)@.len() == old(dst)@.len()`.

So what R5 rules out is exactly the R1 rows above: no write outside
`dst[0..len)`, on any of the 65 536 values a `u16` prefix can take, at every one
of the 220 032 kernel calls the benchmark makes. It also rules out the
`adversarial-srcend` read: the copy's source subrange is inside `src@` by the
trusted wrapper's `requires`, discharged from the same test.

What it does **not** rule out: anything about `common/driver.rs` (external, 94
code lines, reachable from `load_input`/`emit`), and anything at all about R1 —
R5 is a different rung, not a fix for the C one.

---

## 2. R1h — what the check costs inside one language

The new cell. Same signature, same calling convention, same `memcpy`, same fold;
the only difference is three lines of bounds check. `-O3`, marginal Ir per
kernel call:

| | `small` (61 B copied) | `large` (4092 B copied) | delta |
|---|---:|---:|---|
| R1 `c-gcc` | 232.0 | 9195.7 | |
| R1h `c-gcc-h` | 237.0 | 9200.7 | **+5.0 both** |
| R1 `c-clang` | 221.0 | 10192.7 | |
| R1h `c-clang-h` | 233.0 | 10204.7 | **+12.0 both** |

**The check costs 5 instructions per call with gcc and 12 with clang, and the
number does not move with the size of the copy** — it is per call, not per byte,
which is what it should be for a check that is hoisted out of everything. On the
`small` input that is 2.2% (gcc) and 5.4% (clang) of the call; on `large`, 0.05%
and 0.12%.

Statically, `-O3 isolated`, `nm` extent: R1 gcc 153 instructions → R1h gcc 153
(same count, different code — gcc restructures the tail: 2 backward branches
become 18); R1 clang 66 → R1h clang 75.

So: **"C is faster" and "C is unsafe" are now separated, and the first one turns
out to be worth 2% here.** R1 buys almost nothing by omitting the check. The
2% is what an attacker gets a heap overflow for.

R1h generalises — it is a plain second C translation unit — and
`harness/build.py` now creates the `c-gcc-h` / `c-clang-h` cells for any pattern
that ships `c/kernel_hardened.c`, and for no other. Added to
`.memory/01-ladder.md` as a standard optional cell.

---

## 3. The ladder, `-O3`, marginal Ir per kernel call

| rung | cell | `small` (61 B) | `large` (4092 B) | vs R4 `small` | vs R4 `large` |
|---|---|---:|---:|---:|---:|
| R1 | c-gcc | 232.0 | 9195.7 | +3.0 | **−1005.1** |
| R1 | c-clang | 221.0 | 10192.7 | −8.0 | −8.1 |
| R1h | c-gcc-h | 237.0 | 9200.7 | +8.0 | **−1000.1** |
| R1h | c-clang-h | 233.0 | 10204.7 | +4.0 | +3.9 |
| R2 | safe_naive | 407.0 | 11226.0 | **+178.0** | **+1025.2** |
| R3 | safe_tuned | 239.0 | 10210.8 | **+10.0** | **+10.0** |
| R4 | unsafe | 229.0 | 10200.8 | 0 | 0 |
| R5 | verus | 227.0 | 10198.8 | −2.0 | −2.0 |

`isolated`; `whole` is in `results/gate/p02-buffer-copy.json` and tells the same
story (R3 +11, R2 +57/+532). Residues: 61 ≡ 1 and 4092 ≡ 0 (mod 4), as
`.memory/01-ladder.md` demands.

Four findings:

1. **R3 costs +10 instructions per call and the number does not move with the
   size of the copy.** `copy_from_slice` on a checked subslice plus an iterator
   fold is within 0.1% of raw pointers on `large`. This is p01's "the safety tax
   is O(1) per call" reproduced on a pattern with a *data-dependent* copy length
   — which `.memory/01-ladder.md` explicitly warned not to assume.
2. **R2 is O(n), and that is new.** +178 on 61 bytes, +1025 on 4092: about
   +0.25 per byte. LLVM does not hoist the bounds checks out of R2's indexed
   copy loop or its indexed fold loop, and at `-O3 isolated` it does not turn
   the loop into a `memcpy` at all (no bulk call in the symbol; it appears only
   in `whole`). p01 measured R2 at +11…+29 *per call*; here the same rung is
   +1025 per call and growing. **The residue trap of p01 is not the failure mode
   here — the shape of the tax changed.** This is the first measurement in the
   project where safe-naive Rust is genuinely expensive, and it is exactly the
   "patterns where LLVM cannot hoist" case `.memory/01-ladder.md` reserved
   judgement on.
3. **R5 equals R4 to within 2 instructions per call** (and is byte-identical
   statically — see §4; the ±2 is driver-side noise from a different `main`
   layout, not kernel code).
4. **gcc beats clang by ~10% on `large`, the opposite of p01.** 9195.7 vs
   10192.7 per call, on identical source. p01 found gcc executing 42.9% *more*
   than clang on a `u64` sum; here gcc's byte-fold codegen is the better one.
   `.memory/01-ladder.md`'s "always report a clang column" holds — the point is
   that neither compiler is reliably ahead, not that clang is.

### The same ladder by the other two metrics

`results/p02-buffer-copy.json`, `-O3 isolated`. `Ir` here is callgrind
**per-function exclusive for the `kernel` symbol**, so it is the *fold plus the
prologue and the check* and **excludes the `memcpy`**, which lives in libc; the
marginal column above includes it. Wall clock is min of 15, `taskset`-pinned,
frequency scaling on.

| rung | cell | static `n_fn`/nopad | `Ir`/call small | `Ir`/call large | wall small | wall large |
|---|---|---:|---:|---:|---:|---:|
| R1 | c-gcc | 153 / 150 | 202 | 8765 | 7.56 ms | 30.82 ms |
| R1h | c-gcc-h | 153 / 151 | 207 | 8770 | 7.61 ms | 30.85 ms |
| R1 | c-clang | 66 / 64 | 193 | 9764 | 6.09 ms | 25.02 ms |
| R1h | c-clang-h | 75 / 73 | 205 | 9776 | 6.15 ms | 25.10 ms |
| R2 | safe_naive | 122 / 118 | 392 | 11211 | 7.72 ms | 25.70 ms |
| R3 | safe_tuned | 95 / 93 | 212 | 9783 | 6.48 ms | 25.22 ms |
| R4 | unsafe | 72 / 70 | 201 | 9772 | 6.67 ms | 25.34 ms |
| R5 | verus | 72 / 70 | **201** | **9772** | 6.54 ms | 25.35 ms |

R5's `Ir` equals R4's to the instruction on both inputs (40,200,000 and
195,440,000 totals) — the dynamic half of §4.

The wall-clock column contains the one thing `Ir` cannot say: **gcc executes 10%
*fewer* instructions than clang on `large` and takes 23% *longer*.** Same source,
same input, gcc's kernel is 8765 Ir against clang's 9764 and 30.8 ms against
25.0 ms. That is an IPC difference and this box cannot measure IPC (`perf`
absent, `perf_event_paranoid=3`, no root — TOOLCHAIN.md), so it is recorded as an
observation and not explained. It is also a standing warning about this
project's primary metric: instruction count is not time, and here they disagree
in *direction*.

One asymmetry a reviewer should know about and that is **not** corrected: the C
kernel's `const uint8_t *src` and `uint8_t *dst` may alias as far as the
compiler knows, while Rust's `&[u8]` and `&mut [u8]` are `noalias` by
construction. `restrict` on the C parameters would remove it, and is not used
because ordinary C does not use it. The asymmetry favours Rust, and on `large`
gcc is 10% *ahead* anyway, so it is not what any conclusion here rests on — but
it is the reason `copy_nonoverlapping` is sound in R4/R5 without a proof
obligation (§5) and `memcpy` is merely conventional in R1.

`O0` rows are recorded in the gate JSON and are **not** quoted here as
performance (`.memory/02-bench-rules.md`). One `O0` observation is worth
keeping as a *codegen* note: R4/R5 at `O0` cost 4110 Ir per call on `small`
against R3's 1553, because `get_unchecked` and `copy_nonoverlapping` are real
function calls until they are inlined. Unsafe code is not faster before the
optimiser runs.

---

## 4. R4 ≡ R5: byte-identical, on a real proof

| pair | O3 `md5_fn` | O0 | counts `n_fn`/pad-excl (+padding) |
|---|---|---|---|
| R4 `unsafe` vs R5 `verus` | **equal**, `0e5b59364bb6…` | `md5_fn` differs; `md5_fn_norel` **equal** | 72 / 70 both (+12 insn, 12 B padding) |

`identity` in `spec.md` pins `exact` at O3 and `norel` at O0, and the gate
measures both. The O0 difference is link layout — the crate names `6unsafe` and
`5verus` are different lengths — exactly as p01 documents.

**TASK_004 predicted R4 ≠ R5 here and it is wrong: they are identical.** That
prediction was reasonable — p01's R5 is one `get_unchecked` and a loop, p02's is
a raw `copy_nonoverlapping`, an induction lemma, a ghost sequence snapshot and
two nonlinear proof blocks in the driver — and identity survived all of it. The
finding is stronger than the prediction: **ghost erasure is not fragile.** Nine
obligations; two `proof {}` blocks, a `let ghost` binding and two consuming
`assert`s inside the measured driver loop; a ghost `assert` and a lemma call
inside the kernel — and the machine code is the same 72 instructions.

Two things made it hold, both learned the hard way on p01 and reconfirmed:

- R5's exec code is *textually* identical to R4's, not merely equivalent (same
  `for i in 0..len`, same `if` shape, same early `return`);
- the `#[inline(always)]` trusted wrappers (`get_unchecked`, `copy_bytes`)
  disappear completely, so R5's `copy_bytes(src, src_off + 2, dst, len)` and
  R4's inline `unsafe { copy_nonoverlapping(...) }` compile to the same call.

Miri is therefore **not required** by `.memory/02-bench-rules.md`. `spec.md`
sets `miri.required: true` anyway and the gate ran it on all nine inputs at
`n_iters = 4`: no UB, and every printed checksum matched `model.py`. R4 here
carries raw pointer arithmetic where p01's carried a single `get_unchecked`;
switching the check off because the identity level happens to permit it would
have been a weakening.

---

## 5. TCB tally

Counted per `.memory/04-verus.md`: every line inside `#[verifier::external_body]`
bodies, `assume_specification`, `assume(...)`, reachable `#[verifier::external]`
items, and `unsafe` blocks. **Every item listed individually.**

### R5 (`verus.rs`) — TCB: 10 lines across 4 items

| # | item | attribute | body lines | `requires` | `ensures` | `unsafe` |
|---|---|---|---:|---|---|---|
| 1 | `get_unchecked` | `external_body` | 1 | `i < v@.len()` | `r == v@[i as int]` | **yes** |
| 2 | `copy_bytes` | `external_body` | 3 | `from + n <= src@.len()`, `n <= old(dst)@.len()` | length preserved; `final(dst)@ =~= src[from..from+n] + old(dst)[n..]` | **yes** |
| 3 | `load_input` | `external_body` | 5 | — | **none** | no |
| 4 | `emit` | `external_body` | 1 | — | **none** | no |

Plus **`common/driver.rs`, 94 code lines**, external-by-default and reachable
from items 3 and 4. Not reachable from the kernel, so the memory-safety claim
does not rest on it. Zero `assume(`, zero `admit(`, zero `assume_specification`
of our own.

Compared with p01 (6 lines across 3 items) the trusted base grew by one item and
four lines, and that item — `copy_bytes` — **is the pattern**. Its contract is
the thing a reviewer should attack first, so the argument for each clause:

- `requires from + n <= src@.len()` and `n <= old(dst)@.len()` are two of
  `copy_nonoverlapping`'s three documented preconditions, and both are
  discharged by the kernel's runtime test at every call site.
- The third — that the regions do not overlap — is discharged by **Rust's
  aliasing rules rather than by the verifier**: `&[u8]` and `&mut [u8]` cannot
  name the same allocation. This is the one obligation in the file that is
  argued in prose rather than proved, and it is why the wrapper takes two
  reference arguments rather than two raw pointers.
- `ensures final(dst)@.len() == old(dst)@.len()`: `copy_nonoverlapping` does not
  reallocate.
- `ensures final(dst)@ =~= src@.subrange(from, from+n) + old(dst)@.subrange(n, len)`:
  `n` bytes land at `dst[0..n)` and **nothing else is written**. If this clause
  were wrong everything above it would be worthless — which is exactly what
  mutant M7 in §6 demonstrates.

`get_unchecked`'s pair is p01's verbatim, retyped to `u8`. The structural rule
from TASK_005 (a trusted `unsafe` item must carry a non-empty `requires`) is
satisfied by both items without a justification string, and the gate prints so.

---

## 6. Mutation testing — the proof was broken on purpose

A green verification is evidence of nothing on its own. Eight mutants, run
against `verus_run.py` (kept in the report, not the tree):

| # | mutation | verifier | caught by |
|---|---|---|---|
| M1 | kernel's `requires` deleted | **fails** — `precondition not satisfied` | the proof itself |
| M2 | security `ensures` → `final(dst)@ =~= final(dst)@` | **fails** — `assertion failed` at the driver's ghost assert | the proof, **because the assert exists** (see below) |
| M3 | value `ensures` → `r == r` | **fails** — `assertion failed` at the driver's ghost assert | the proof |
| M5 | `len > dst.len()` dropped from the runtime test — *this is R1's bug, transplanted into R5* | **fails** — `precondition not satisfied` at `copy_bytes` | the proof |
| M6 | driver guard `stride_w >= 2` → `>= 1` | **fails** — `invariant not satisfied before loop` | the proof |
| M8 | `copy_bytes` claims the wrong (but length-consistent) tail | **fails** — `postcondition not satisfied` in `kernel` | the proof |
| M4 | **`requires` deleted from the trusted `copy_bytes`** | **VERIFIES — 9 verified, 0 errors** | gate: the `spec.md` clause pin **and** the structural `tcb-unsafe` rule, both fired |
| M7 | **`copy_bytes`'s tail clause deleted, leaving an *inconsistent* postcondition** | **VERIFIES — 9 verified, 0 errors** | gate: the `spec.md` clause pin **only** |

M4 and M7 are the ones to remember, and M7 is new.

**M7 is a vacuity mode this project had not recorded.** Deleting
`+ old(dst)@.subrange(n, len)` leaves `final(dst)@ =~= src@.subrange(from, from+n)`,
which additionally asserts `dst.len() == n`. Together with the neighbouring
clause `final(dst)@.len() == old(dst)@.len()` that is *contradictory* whenever
`n < dst.len()` — and a trusted item with a contradictory postcondition makes
every caller verify vacuously. It is not a weakening, it is a false axiom, and
it is indistinguishable from a healthy run at the verifier: 9 verified, 0
errors, no diagnostic. I expected this mutant to fail and it did not; the
measurement changed my mind, and the conclusion is recorded in
`.memory/04-verus.md`.

The structural rule from TASK_005 does **not** catch M7 — `copy_bytes` still has
a non-empty `requires` — so the only thing standing between p02 and a vacuous
proof is the declared `ensures` pin in `spec.md`, which TASK_003_REVIEW showed
moves with the code it constrains. **That is an open gap, not a solved problem.**
The honest statement of p02's assurance is: the proof is sound *given* that
`copy_bytes`'s two `ensures` clauses describe what `copy_nonoverlapping` really
does, and nothing mechanical checks that they do.

**M2 fails only because the driver consumes the security clause.** Before that
line was added, the postcondition this entire pattern exists to state could be
replaced with a tautology and the file still verified — nothing depended on it.
The fix costs one ghost binding and one ghost assert:

```rust
let ghost d0: Seq<u8> = dst@;
let r: u64 = kernel(src, k * stride, dst);
assert(r == copy_sum(src@, (k * stride) as int, dst@.len() as int));
assert(dst@ =~= copy_dst(d0, src@, (k * stride) as int));
```

Both erase, R4 and R5 stay byte-identical, and the driver loop still normalises
to the pinned 13-statement sequence — but `harness/dloop.py` had to learn that
`let ghost` is a ghost statement first (§8). **A postcondition about `&mut`
state cannot be consumed without a pre-state snapshot, and a pre-state snapshot
is a `let ghost`.** `.memory/04-verus.md`'s "do this in every pattern" was not
achievable for such a postcondition before this change.

---

## 7. Proof sticking points

- **`&mut` in a postcondition needs `final(dst)@`, not `dst@`.** This Verus
  (`0.2026.08.09`) rejects a bare dereference of a `&mut` parameter in an
  `ensures` outright: *"to dereference a mutable reference parameter in a
  postcondition, disambiguate by wrapping it in either `old` or `final`"*.
  `.memory/04-verus.md` said "`old(x)` / `*final(x)`, never a bare `*x`" — the
  spelling that works here is `final(x)@`, with no `*`.
- **The record-offset bound needs two nonlinear steps.**
  `k * stride + 2 <= n_src` from `k < nrec` and `nrec == n_src / stride`:
  `vstd::arithmetic::div_mod::lemma_fundamental_div_mod` gives
  `nrec * stride <= n_src`, `lemma_mul_inequality` (broadcast) gives
  `k * stride <= (nrec - 1) * stride`, and the step between them needs
  `by (nonlinear_arith)`. Add `lemma_div_non_zero` for `nrec >= 1` before the
  loop — `stride <= n_src` does not give it to Z3 by itself.
- **The fold accumulates over `dst` and the postcondition is stated over `src`.**
  That gap is one induction (`lemma_sum_congruent`: equal elements give equal
  sums), applied once after the loop. Stating the postcondition over `dst`
  instead would have removed the lemma and also removed the reason the
  postcondition is worth anything — it is the `src`-side statement that forces
  the copy to have been correct.
- **`v@.len() <= usize::MAX` is still not free**, exactly as p01 records: one
  `assert(src@.len() == vstd::slice::spec_slice_len(src));` at the top of the
  kernel, or `src_off + 2` cannot be shown not to overflow.
- **Decoding the prefix with `+` instead of `|` avoided a bit-vector proof
  entirely.** `b0 + 256*b1` and `b0 | (b1 << 8)` are the same function on bytes
  and compile identically; only the first is linear arithmetic. Choosing the
  cheaper *spelling* is legitimate; choosing a weaker *specification* would not
  be.
- **Verus accepted an early `return 0;` inside a function with three `ensures`
  clauses** with no special handling, and accepted `let (a, b, c, mut d) = f();`
  tuple destructuring with a `mut` binder.

---

## 8. Everywhere the harness had to change

TASK_003 argued genericity from code structure; p02 is the first test of it.
Seven changes, in descending order of how much they matter. **None of them is a
pattern-specific special case in the harness** — each is switched on by a file
existing or by a pin in the pattern's own `spec.md`.

| # | file | change | why p02 forced it |
|---|---|---|---|
| 1 | `harness/dloop.py` | **new `driver.call_args` pin**: which argument positions of a named call are the canonical ones, per language | `&[u8]` is a pointer *and* a length, so the C kernel takes 5 arguments where the Rust one takes 3. An alias cannot express that — both sides of an alias are a dotted identifier path. Constrained three ways: it drops arguments of a *named call* only, every dropped argument must be a single bare identifier, and dropping the wrong positions raises rather than matching. 8 new selftest cases |
| 2 | `harness/dloop.py` | `let ghost` / `let tracked` recognised as ghost statements | a postcondition about `&mut` state cannot be consumed without a pre-state snapshot, and the snapshot is a `let ghost`. Without this the security `ensures` was defensible only by mutation testing (§6, M2). Rust-only, like every other rule there |
| 3 | `harness/asm.py` | bulk-memory detection made to see **Rust v0-mangled** symbols | `_BULK_MEM_RE` requires a non-word character on both sides, and v0 mangling writes `...5sliceSh15copy_from_sliceCs86...`. It false-failed `safe_tuned O0 isolated`, whose copy and fold are still out-of-line calls, with "no backward branch and no bulk-memory call". Kept tight: the decimal length prefix must be exactly the routine's length |
| 4 | `harness/build.py` | **R1h cells** `c-gcc-h` / `c-clang-h`, built from `c/kernel_hardened.c`; `measured_cells(pdir)` / `all_cells(pdir)` replace the module-level lists | the whole point of the pattern (§2). Presence of the file is the switch |
| 5 | `harness/build.py` | `all_cells()` includes `safe_naive_verus` only when the source exists | `.memory/05-layout.md` calls R2v OPTIONAL, but `ALL_CELLS` was unconditional, so `check.py --cells all` failed four builds on any pattern without one. This would have hit **every** future pattern, not just p02 |
| 6 | `common/driver.{c,h,rs}`, `common/slb.py` | `head2_u64_bytes` (two head words + a byte blob), `zeroed(cap)` with a shared `SLB_MAX_CAP` range check, exit code 7 | p02's payload is not p01's "one head word then u64s". `zeroed` is range-checked *in both languages* so that a huge declared capacity is not `calloc` returning NULL in C and an allocator abort in Rust — that would read as a rung difference |
| 7 | `harness/measure.py`, `harness/report.py` | the per-input table stopped decoding every pattern's payload with `slb.head_u64_body` and now reports the format-level fields plus `model.py`'s own `describe()` | it was printing `win_len`/`v_len` — p01's payload layout — for p02, where those two numbers are meaningless |

`harness/check.py` itself needed **two** edits, both one-liners: pass
`driver.call_args` through to `dloop`, and use the per-pattern cell list. Its
nine stages, the model API, the sandbox, the contract derivation, the proof-domain
evaluation and the Miri policy all worked unmodified on a pattern with a
different kernel signature, a different payload, a mutable output buffer and a
real bug. **That is the genericity claim actually tested.**

Two things the harness got right without being asked, both worth recording:

- `asm.py`'s bulk-memory alternative to "must have a backward branch" was added
  at TASK_005 *speculatively, for p02, before p02 existed*. It was necessary:
  every C cell's kernel here has `call memcpy@plt` and gcc `-O3 isolated` has
  only 2 backward branches for a 153-instruction body.
- `check.py`'s per-input `sanitizer_expect` (TASK_005) is what makes this
  pattern greenable at all. Under the previous rule — any ASan hit fails the
  gate — p02 could not have existed.

### Two harness warts found and *not* fixed

- `check_proof_domain` prints the failing call's bindings minus the key `"v"`,
  which is p01's name for its big array. p02's big values are `src`,
  `dst_before` and `dst_after`; a `requires` violation would print several
  megabytes. Failure path only, so it is cosmetic until it isn't.
- The same function collects an `off` range for the log only if the binding is
  literally named `off`. p02 binds `src_off`, so that line is silently absent.
  Both suggest the model should declare which bindings are large/positional
  rather than the gate guessing from p01's names.

Adjacent, noticed and not touched: `asm.py`'s docstring claims
`__memcpy_avx_unaligned_erms` matches `_BULK_MEM_RE`. It does not — the
underscore is a word character on both boundaries. No current check depends on
it.

---

## 9. Known gaps

- **The fold dominates the copy 20:1** (§0). Every performance number here is
  mostly a byte-checksum measurement. Stated up front rather than buried.
- **No R2v control cell.** p01's `safe_naive_verus.rs` holds up
  `.memory/01-ladder.md` finding 2 ("a proof buys nothing on its own"); p02
  ships none, so that finding is not re-tested here. `build.py` now makes the
  cell optional per pattern, so adding one later is a file, not a harness change.
- **M7 (§6) is caught by a declared pin and nothing else.** An `external_body`
  item can still be given a contradictory postcondition and every caller then
  verifies vacuously with no diagnostic. The structural rule does not see it
  because the `requires` is still there.
- **`panic=abort` and `O0d` were built but not measured**, as in p01.
- **The `whole`-mode numbers are `main`-exclusive** and are not comparable
  across languages without the subtraction p01's NOTES describes; the marginal-Ir
  column used throughout this file does not have that problem, which is why it is
  the one quoted.
- **`results/p02-buffer-copy.json` records per-function exclusive `Ir` for the
  `kernel` symbol, which *excludes* the `memcpy` in libc.** For this pattern
  that column understates every C rung by ~430 instructions per call on `large`.
  Use the marginal column (this file, and `marginal_ir_per_call` in the gate
  JSON) for anything cross-rung.
