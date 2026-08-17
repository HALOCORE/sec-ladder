# p02 — findings, adversarial behaviour, TCB tally, sticking points

Gate record: `results/gate/p02-buffer-copy.json` (`verdict: PASS`,
`complete_run: true`, invocation `p02`). Dynamic numbers below are the gate's
**marginal executed instructions per kernel call** — whole-program `Ir` at 200
driver iterations minus `Ir` at 100, over the 100 extra calls — unless a table
says "kernel symbol".

---

## 0. Read this before quoting any performance number

### 0a. A retraction

TASK_004 published, as this pattern's performance headline, that **safe-naive
Rust pays an O(n) bounds-check tax on a data-dependent copy** — +178 Ir per call
at 61 bytes and +1025 at 4092. TASK_004_REVIEW refuted it and TASK_006
reproduced the refutation from scratch. Both halves of the claim are wrong:

- it is **not a bounds-check tax**. Changing only the fold moves nothing;
  changing only the copy removes all of it (§3a). R2's and R4's fold loops are
  the same 19 instructions.
- **the two points that established "O(n)" are not on a line.** The delta is a
  sawtooth of *constant* amplitude 179 Ir and period 16 in the record length,
  plus a ~0.21 Ir/byte linear term. Both published lengths sit near the top of
  the sawtooth (61 ≡ 13, 4092 ≡ 12 mod 16). At 61 bytes the delta is +178; at
  **65** bytes it is **+29** — copying four more bytes makes safe-naive Rust 149
  instructions per call *cheaper* (§3b). The linear term is real, but it is the
  cost of an inline byte copy versus a `call memcpy`, and three other spellings
  of the same safe Rust do not pay it at all.

What is true is narrower and, as a result, more interesting: **rustc failed to
idiom-recognise one spelling of a byte-copy loop.** Three other spellings —
including the reslice a competent Rust programmer writes — are +10 per call,
flat. That is a codegen-fragility finding, not a safety-cost finding.

The **security** result of this pattern (§1) was reviewed and stands unchanged.

### 0b. The copy is a small minority of the kernel's work

The kernel is a `memcpy` *and then* a byte-wise checksum of what was copied, and
the checksum is the expensive half. Measured on `large` (4092 bytes per call,
`-O3 isolated`), by subtracting the callgrind per-function exclusive `Ir` of the
`kernel` symbol from the whole-program marginal:

| | c-gcc | c-clang | unsafe |
|---|---:|---:|---:|
| marginal Ir per call (whole program) | 9195.7 | 10192.7 | 10200.8 |
| `kernel` symbol, exclusive | 8765 | 9764 | 9772 |
| difference — driver loop + the `memcpy` in libc | ~431 | ~429 | ~429 |

So the copy is **~4%** of the call and the fold is ~96% (0.104 Ir per byte
copied — re-measured directly at TASK_006, below — against ≈2.3 Ir per byte
folded).

**The fold does not vectorise in rustc. It does in gcc — fully.** An earlier
draft said "barely does in gcc"; the disassembly says otherwise. `c-gcc -O3
isolated`, the fold loop:

```
movdqu (%rax),%xmm1          # 16 bytes at a time
punpckhbw/punpcklbw          # u8  -> u16
punpckhwd/punpcklwd          # u16 -> u32
punpckhdq/punpckldq          # u32 -> u64
paddq x8                     # into 4 independent accumulators
```

rustc and clang both emit a scalar `movzbl` chain instead. That is a
**codegen-grounded hypothesis for the inversion in §3**, where gcc executes 10%
*fewer* instructions than clang and takes 23% *longer*: a 14-instruction
`punpck` ladder to widen 16 bytes is few instructions but all of them are shuffle
work on one or two ports, so instruction count and time need not move together.
This box cannot measure IPC (no `perf`, `perf_event_paranoid=3`, no root), so it
stays a hypothesis.

That the fold dominates is a property of this kernel, not a defect — a real
parser does copy a record and then scan it — but it means the **performance**
numbers here are mostly a byte-checksum measurement, and every one of them is
quoted as a *marginal* delta for that reason.

### 0c. The fold's extent is settled: keep the full fold

The first draft of this file said a narrower fold would let LLVM elide the copy,
and marked it **"Not measured"**. It has now been measured, and the worry is
unfounded:

| variant (4092 bytes copied, `-O3`) | isolated | whole |
|---|---:|---:|
| copy + fold **8 bytes** of `dst` | 483.7 | 472.1 |
| the same with the **copy deleted** | 58.0 | 0.0 |

The `memcpy` call is still present in `main` in `whole` mode with only 8 of 4092
bytes consumed: LLVM will not narrow a copy into a caller-visible `&mut [u8]`.
So the full-extent fold is not needed to keep the copy alive.

It is kept anyway, for a different and better reason: **any fold that reads every
copied byte costs at least what the copy cost to write them**, so the copy can
never exceed ~50% of such a kernel no matter how cheap the fold gets. A
word-wise fold cuts the kernel 10 200 → 1 399 Ir/call and lifts the copy's share
4.2% → ~31%; an `xor` fold measures identically. A cheaper fold is worth doing
for a pattern that wants the copy to dominate — it is not a way to make the copy
dominate *completely*, and it costs a materially harder Verus spec (byte
sequence to `u64`).

That subtraction — 483.7 − 58.0 = 425.7 Ir for 4092 bytes = **0.104 Ir per byte**
— is also this repo's measurement of glibc `memcpy`, and it is what forced the
anti-collapse floor to be fixed at TASK_006 (§9).

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
  not the program.** This box is **Ubuntu 24.04 with gcc 13.3.0
  (`Ubuntu 13.3.0-6ubuntu2~24.04.1`), and its gcc default-enables
  `_FORTIFY_SOURCE` at level 3** — verified directly:
  `gcc -O2 -dM -E - </dev/null | grep -i fortify` prints
  `#define _FORTIFY_SOURCE 3`. (An earlier draft said "Debian's gcc, at `-O`",
  which named the wrong distribution and omitted the level; level 3 is the one
  that uses `__builtin_dynamic_object_size`, so it fires on more shapes than
  level 2 would.) The `memcpy` becomes `__memcpy_chk`; with LTO the
  destination's allocated size is visible at the call and the check fires.
  `harness/build.py` passes no `-D_FORTIFY_SOURCE` either way. clang does not do
  this and is silent in all four builds. So "hardening caught it" here is a
  distro default that catches 1 of 8 builds of 1 of 3 attacks.

  This is also why `harness/asm.py:is_bulk_symbol` had to be fixed at TASK_006:
  `c-gcc -O3 whole` and `c-gcc-h -O3 whole` really do emit `__memcpy_chk@plt`,
  and the old regex could not see it (§8).

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
- either way `final(dst)@.len() == old(dst)@.len()` -- which the clause
  above *entails*, and which is why it is no longer stated separately (§5).

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
story (R3 +11, R2 +57/+532). Residues: 61 ≡ 1 and 4092 ≡ 0 (mod 4), 5 and 4
(mod 8), 13 and 12 (mod 16). **The last pair is the one that matters here and
neither of those two numbers is representative** — see §3b.

**Read the R2 row with §3a and §3b, never alone.** It is a fair naive port — a
real Rust programmer does write that loop, which is why it is the shipped R2 —
but the number it produces is one spelling's codegen accident sampled at one
residue, not the cost of safety.

Four findings:

1. **R3 costs +10 instructions per call and the number does not move with the
   size of the copy.** `copy_from_slice` on a checked subslice plus an iterator
   fold is within 0.1% of raw pointers on `large`. Measured across **68 record
   lengths at two scales** (§3b) it takes exactly two values: **+8 where
   `len ≡ 0 (mod 8)` and +10 everywhere else** — 26/26 lag-8 pairs agree exactly
   in both bands, and re-measured outside them at TASK_008 (+8.0 at 512, 520,
   528, 1000; +10.0 at 513, 521, 1001). This is p01's "the safety tax is O(1) per call"
   reproduced on a pattern with a *data-dependent* copy length — which
   `.memory/01-ladder.md` explicitly warned not to assume — and it is the third
   pattern in a row where R3 is the honest number.
2. ~~**R2 is O(n), and that is new.**~~ **RETRACTED** (§0a, §3a, §3b). One
   missing `memcpy` idiom, sampled at two lengths that both sit near the top of
   a 179-Ir sawtooth. The bounds checks in R2's indexed fold cost **zero** — its
   fold loop is R4's, instruction for instruction.
3. **R5 equals R4 to within 2 instructions per call** (and is byte-identical
   statically — see §4; the ±2 is driver-side noise from a different `main`
   layout, not kernel code).
4. **gcc beats clang by ~10% on `large`, the opposite of p01.** 9195.7 vs
   10192.7 per call, on identical source. p01 found gcc executing 42.9% *more*
   than clang on a `u64` sum; here gcc's byte-fold codegen is the better one —
   and §0b now says *why*: gcc vectorises the fold and clang does not.
   `.memory/01-ladder.md`'s "always report a clang column" holds — the point is
   that neither compiler is reliably ahead, not that clang is.

### 3a. The decomposition that refutes finding 2

One loop changed at a time, everything else byte-for-byte R2, `-O3 isolated`,
marginal Ir per call, every variant checksum-identical to `model.py` on both
inputs.

| # | variant | 61 B | 4092 B | vs R4 | kernel `n_fn` nopad | bulk call |
|---|---|---:|---:|---|---:|---|
| — | **R2 as shipped** | 407.0 | 11226.0 | +178 / +1025 | 118 | **none** |
| n2 | indexed copy kept, **iterator fold** | 407.0 | 11226.0 | +178 / +1025 | — | none |
| n1 | **`copy_from_slice`**, indexed fold kept | 239.0 | 10210.8 | **+10 / +10** | 93 | `memcpy@GLIBC_2.14` |
| n3 | indexed copy kept, **one `&src[a..b]` reslice** added | 239.0 | 10210.8 | **+10 / +10** | 93 | `memcpy@GLIBC_2.14` |
| n4 | R2 verbatim, the check written **additively** | 237.0 | 10208.8 | **+8 / +8** | 87 | `memcpy@GLIBC_2.14` |
| — | R3 `safe_tuned` | 239.0 | 10210.8 | +10 / +10 | 93 | `memcpy@GLIBC_2.14` |
| — | R4 `unsafe` | 229.0 | 10200.8 | 0 | 70 | `memcpy@GLIBC_2.14` |

**The `4092 B` column used to read 11225.9 / 10210.9 / 10208.9 / 10200.9 here
while §3's table, `.memory/01-ladder.md` and two independent re-runs all read
…6.0 / …0.8 / …8.8 / …0.8 — one measurement, two tables, different numbers**
(TASK_006_REVIEW). Corrected at TASK_008 from a fresh run of both: the shipped
rungs come out of `results/gate/p02-buffer-copy.json`
(`safe_naive` 11226.0, `safe_tuned` 10210.84, `unsafe` 10200.84) and the four
variants out of `.temp/review006/variants/` re-measured with the same
two-callgrind-runs difference (n1 10210.8, n2 11226.0, n3 10210.8, n4 10208.8,
r2 11226.0 — all checksum `4856715052625337940`). The `.9` column was a
transcription, and nothing in the gate diffs one table in `NOTES.md` against
another.

Read the first two rows together: **changing only the fold moves nothing.**
Read rows n1 and n3: **changing only the copy removes 100% of it.**

The disassembly says the same thing. R2's fold loop and R4's are the **same
19-instruction unrolled body**, identical instruction for instruction modulo one
base/index register swap — `safe_naive` insns 76…94 against `unsafe` insns
44…62, `-O3 isolated`:

```
movzbl (%rcx,%rdx,1),%esi     |  movzbl (%rdx,%rcx,1),%esi
add    %rax,%rsi              |  add    %rax,%rsi
...  8 bytes per iteration, no compare, no branch except the loop's own ...
add    $0x8,%rdx              |  add    $0x8,%rcx
cmp    %rdx,%r10              |  cmp    %rcx,%rbx
jne    ...                    |  jne    ...
```

**The indexed fold's bounds checks cost zero instructions** — LLVM hoisted every
one of them — which is the opposite of what the retracted finding said.

The cause is in the *check*, not in the copy loop. `spec.md:44-48` mandates the
subtraction-first form

```rust
if len > dst.len() || len > src.len() - (src_off + 2) { return 0; }
```

for sound overflow reasons — the additive form `src_off + 2 + len > src.len()`
can wrap `usize` and wave the attack through. Subtraction-first leaves LLVM
unable to prove `src_off + 2 + i < src.len()` for the loop index, so
loop-idiom recognition never forms a `memcpy`. **One operator flips
`bulk_calls []` → `['memcpy@GLIBC_2.14']` and 118 instructions → 87** (row n4;
that row is a diagnostic, not a rung — it is the overflow bug `spec.md` forbids).

So the comparison was **an inline SSE2 copy against a `call memcpy`** — two
different algorithms, not two different safety regimes. **C written the same way
pays the same or more.** R1h with its `memcpy` replaced by exactly the byte loop
R2 writes (`c/kernel_hardened.c` otherwise verbatim), `large`, marginal Ir per
call:

| | with `memcpy` | with the byte loop | cost of the byte loop |
|---|---:|---:|---:|
| gcc | 9200.3 | 10106.3 | **+906.0** |
| clang | 10204.3 | 10732.3 | **+528.0** |

Both are in the same range as R2's +1025, in a language with no bounds checks at
all. (TASK_004_REVIEW reported this as "gcc's byte loop is 94 Ir *faster* than
glibc's memcpy", which is a comparison against **R4**, not against gcc's own
`memcpy` build: 10106.3 vs R4's 10200.8. Within one compiler the byte loop is
dearer, by the table above. Corrected at TASK_006.)

(The two `with memcpy` figures above, 9200.3 and 10204.3, were measured on
hand-built variant binaries and do **not** reproduce against the gate's own R1h
cells, which come out at 9200.74 and 10204.74 — `results/gate/*.json`,
`c-gcc-h`/`c-clang-h` `/O3/isolated/large.bin`. 0.44 Ir per call is 44
instructions over the 100-call probe, so it is a difference between two builds
and not noise; the *deltas* the table is about are unaffected. Not chased at
TASK_008 — recorded so the next reader does not treat the two as the same
measurement.)

### 3b. The residue curve — `gen.py --sweep`, finally run

`inputs/gen.py --sweep` existed since TASK_004 and had never been run. It now
emits **two complete mod-16 cycles plus the endpoints at each of two scales** —
`SWEEP_BANDS` is `(56, 34)` and `(2040, 34)`, i.e. lengths 56…89 and 2040…2073,
**68 inputs in two runs of 34** — because one cycle cannot tell a period of 16
from a period of 64, and the first draft of this sweep used 16 lengths per band
with both bands straddling a multiple of 64.

**What 34 consecutive lengths per band establishes, and what it does not.**
Earlier drafts of this section and of `gen.py` said "measured over 72
consecutive lengths"; 72 is not a number in this data and never was. What the 34
give is the lag-16 comparison, twice, at each scale. Checked directly against
`results/p02-residue-sweep.json` (TASK_008):

- **R3 − R4 is exactly 16-periodic and in fact 8-periodic**: 26/26 lag-8 pairs
  and 18/18 lag-16 pairs agree exactly, in *both* bands. So a period of 32 or 64
  is excluded outright — a signal of period 32 cannot agree with itself at
  lag 16 for 18 consecutive lengths.
- **R2 − R4 is 16-periodic only in *shape*.** The raw delta disagrees at every
  one of the 18 lag-16 pairs in both bands, by ±5.0 (band 1) / +4.9…+5.1
  (band 2) — a drift of ~5 Ir per 16 bytes riding under the sawtooth, i.e.
  ~0.31 Ir/byte locally against the 0.21 Ir/byte long-range slope taken between
  the two bands' cycle means. "The period is 16" is a claim about the sawtooth,
  not about the delta, and the row below quotes the sawtooth.
- **34 cannot rule out a period longer than 34.** A signal with period 1024
  that happens to look 16-periodic across 34 samples is not excluded by this
  data; what makes that implausible is the second band, 32× larger in copy size,
  showing the same 16-cycle and the same 179 Ir amplitude.

R2 − R4, `-O3 isolated`, marginal Ir per call, one full cycle at each scale:

| `len mod 16` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| len 64…79 | **213** | **29** | 41 | 53 | 65 | 77 | 89 | 101 | 112 | 125 | 137 | 149 | 161 | 173 | 185 | 197 |
| len 2048…2063 | **624** | **450** | 462 | 474 | 486 | 498 | 510 | 522 | 533 | 546 | 558 | 570 | 582 | 594 | 606 | 618 |
| R3 − R4, both | 8 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | **8** | 10 | 10 | 10 | 10 | 10 | 10 | 10 |

Three things to take from it:

- **The peak-to-trough amplitude is 179 Ir at both scales** — 29 … 208 over
  lengths 65…80, and 450 … 629 over 2049…2064. Identical amplitude 32× apart in
  copy size, so the sawtooth is a **fixed epilogue cost, not a per-byte one**,
  and at `small`'s scale it is *larger than the entire delta*. The reset is at
  `len ≡ 1 (mod 16)`, where R2's own cost drops ~167 Ir while R4's rises ~7; a
  second, ~7 Ir drop lands at `len ≡ 0 (mod 8)`. Within a cycle R2 costs ~17 Ir
  more per extra byte against R4's ~5 — a scalar epilogue paid for at both ends
  of an unrolled body.
- **The underlying growth is 0.21 Ir per byte**, from the cycle means: 118.9 at
  len ≈ 72 and 540.0 at len ≈ 2056. Consistent with the two published points
  (0.210 from 61→4092), so the *slope* in TASK_004 was right; the *attribution*
  and the *shape* were not.
- **Copying four more bytes makes safe-naive Rust 149 instructions per call
  cheaper**: +178 at 61 bytes, +29 at 65. Quoting either alone is quoting a
  residue. `.memory/01-ladder.md` has warned about mod 4 three times; the
  modulus that governs this kernel is 16, and `inputs/gen.py` now asserts the
  two measured lengths differ mod 4, 8 **and** 16 before it writes anything.

All seven cells at all 68 lengths, with provenance, are committed as
**`results/p02-residue-sweep.json`** — the two cycles above are an excerpt.
R3 − R4 is the row above at every one of the 68, and no rung except R2 has a
sawtooth of any consequence.

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

### R5 (`verus.rs`) — TCB: 10 lines across 4 items, **2 trusted `ensures` clauses**

| # | item | attribute | body lines | `requires` | `ensures` | `unsafe` |
|---|---|---|---:|---|---|---|
| 1 | `get_unchecked` | `external_body` | 1 | `i < v@.len()` | `r == v@[i as int]` | **yes** |
| 2 | `copy_bytes` | `external_body` | 3 | `from + n <= src@.len()`, `n <= old(dst)@.len()` | `final(dst)@ =~= src[from..from+n] + old(dst)[n..]` — **one clause** | **yes** |
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
- `ensures final(dst)@ =~= src@.subrange(from, from+n) + old(dst)@.subrange(n, len)`:
  `n` bytes land at `dst[0..n)` and **nothing else is written**. If this clause
  were wrong everything above it would be worthless.

**This item carried a second `ensures` until TASK_006** — `final(dst)@.len() ==
old(dst)@.len()`, justified as "`copy_nonoverlapping` does not reallocate". It
was deleted, because the clause above *entails* it (a subrange of length `n`
concatenated with a subrange of length `old(dst).len() − n` has length
`old(dst).len()`), so it was an axiom the tally counted, a reviewer had to judge,
and nothing in the file depended on. `harness/check.py` step 5c is what
established that mechanically: it deletes each `ensures` clause of each
`external_body` item and re-runs Verus, and deleting this one left `9 verified,
0 errors`. The same stage found and removed a third, equally redundant clause on
`kernel` itself. **Prefer one strong clause to several overlapping ones** — an
overlapping pair also lets a later weakening of the strong half hide behind the
weak half.

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
| M7 | **`copy_bytes`'s tail term deleted, injecting a false but *usable* `dst.len() == n`** | **VERIFIES — 9 verified, 0 errors** | gate: the `spec.md` clause pin **only** — still true after TASK_006, see below |

M4 and M7 are the ones to remember, and M7 is new.

**M7 is not vacuity, and the TASK_004 write-up of it above is wrong.** Deleting
`+ old(dst)@.subrange(n, len)` leaves `final(dst)@ =~= src@.subrange(from, from+n)`,
which additionally asserts `dst.len() == n`. TASK_004 concluded from that, plus
the neighbouring length clause, that the postcondition was *contradictory* and
every caller therefore vacuous. TASK_004_REVIEW measured it: with the mutant in
place, `assert(false)` after the call is **still unprovable**, so the callers are
not vacuous. What actually happens is a **silent strengthening** — the trusted
item injects an extra fact (`dst.len() == n`) that is false of
`copy_nonoverlapping`, consistent in context, and *usable*, and it happens to
make the security postcondition provable. **A false axiom that is usable is
worse than one that collapses the context**, because nothing downstream looks
wrong.

Two consequences, both measured:

- **The `assert(false)` reachability probe does not detect this class.** The
  gate runs it anyway (step 5c) because it catches genuine vacuity — an
  unsatisfiable `requires`, a contradictory context — but it is not the detector
  here.
- **Clause deletion is now a gate stage** (`harness/check.py` step 5c,
  TASK_006): for each `ensures` **conjunct** of each `external_body` item,
  delete it, re-run Verus, fail if the file still verifies with 0 errors. It is
  *derived*, not declared, so unlike the `spec.md` clause pin it does not move
  with the code it constrains. Cost on p02: 5 Verus runs plus 2 controls, 1.7 s
  each. Run on p02 as TASK_004 shipped it, it failed **two** clauses (§5).

  *Conjunct, not clause, since TASK_008.* `vparse._clause_split` split on
  top-level commas only, so `ensures a, b` was two deletable units and
  `ensures a && b` was one — re-joining a redundant conjunct with `&&` made the
  stage delete both halves together, the file failed, and the stage certified
  the clause load-bearing. One character. Demonstrated by re-joining
  `final(dst)@.len() == old(dst)@.len()` onto the surviving clause here:
  `ensures[0] load-bearing (8 verified, 1 errors)` and a green gate before,
  `ensures[0].conjunct[1] is NOT load-bearing ... 9 verified, 0 errors` after.
  Clauses whose top level also carries `==>`, `||` or `<==>` are **not** split
  (a conjunct lifted out of an implication is not a deletable unit) and the
  refusal is shouted into the verdict.

- **`requires` gets a different oracle entirely** (step 5c-req, TASK_008).
  Step 5c never touched `requires`, and that is the dangerous half — see §6a
  below.

**Be precise about what step 5c does and does not close.** It deletes whole
conjuncts, so it catches one that is *redundant* (implied by its neighbours,
which is what `copy_bytes`'s length clause was) and one that is
*decorative* (nothing consumes it, which is what `kernel`'s third clause was and
what p01's R2v control turned out to be). It does **not** catch a clause that has
been *rewritten*: apply M7 to p02's single surviving clause today and the file
still verifies, because deleting that clause is not the mutation M7 performs.

So the gap TASK_004 recorded is **narrowed, not closed**. What changed:

- the trusted `ensures` count is down from 3 to 2 across the file and
  `copy_bytes`'s from 2 to 1, so there is exactly **one** sentence a reviewer
  must judge against `copy_nonoverlapping`'s real semantics instead of two;
- overlapping clauses are gone, and an overlapping pair is what let M7's write-up
  be misdiagnosed as vacuity in the first place — and, worse, is what would let a
  later weakening of the strong clause hide behind the weak one;
- a *decorative* postcondition anywhere in the file is now a gate failure rather
  than a thing only mutation testing would find.

What has not changed: **a wrong trusted `ensures` is still an axiom, and the only
things between it and the proof are the declared `spec.md` pin and the written
argument beside the item in `verus.rs`.** That is inherent — no verifier can
check an axiom against the language it is axiomatising.

**One correction to `.memory/04-verus.md`, which the manager should apply.** It
records "Neither of `copy_bytes`'s two `ensures` clauses is individually
load-bearing — deleting *either* one leaves 9 verified / 0 errors." Measured at
TASK_006 with the stage above:

| clause deleted | result |
|---|---|
| `final(dst)@.len() == old(dst)@.len()` (length) | **9 verified, 0 errors** — not load-bearing |
| `final(dst)@ =~= src[from..from+n] + old(dst)[n..]` (tail) | **8 verified, 1 error** — load-bearing |

Only the length clause is redundant, and the stated reason ("the tail clause
implies the length clause") is exactly why: implication runs one way. Deleting
the *tail* clause is not the same mutation as M7, which deletes only the
`+ old(dst)@.subrange(...)` term and leaves a subrange behind.

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

### 6a. The `requires` half, and why it is not the mirror of the `ensures` half

TASK_006_REVIEW found that step 5c iterated `ensures` and nothing else, and that
the `requires` hole is the one this pattern is about. Three mutants, all with
the matching `spec.md` pin moved in the same edit, all giving **9 verified, 0
errors** and the obligation count unmoved at 9:

| mutant | what it leaves the trusted base saying |
|---|---|
| delete `from + n <= src@.len()` from `copy_bytes` | `copy_nonoverlapping` may read from anywhere past `src` |
| `get_unchecked`: `i < v@.len()` → `0 <= i` | reading any index of any slice is defined and yields `v@[i]` |
| `copy_bytes`: both `requires` → `n >= 0` | an arbitrary `copy_nonoverlapping` is defined — the exact CWE-787 |

The third gave a **full gate PASS**, and the structural "a trusted `unsafe` item
must demand something of its callers" rule printed the tautology approvingly:
*"trusted `unsafe` item `copy_bytes` demands `['n >= 0']` of every caller"*.

**The obvious fix does not exist.** TASK_008 was specified as "delete the
`requires`, re-run, fail if the file still verifies". Measured, on this file:

| | verified / errors |
|---|---|
| control | 9 / 0 |
| delete `copy_bytes.requires[0]` | **9 / 0** |
| `get_unchecked` → `0 <= i` | **9 / 0** |
| `copy_bytes` → `n >= 0` | **9 / 0** |
| delete `kernel.requires[0]` (a *verified* item) | **8 / 1** |

Deleting a precondition from an `external_body` item removes an obligation from
its *call sites*, so verification gets strictly easier and nothing can ever
fail. Implementing the prescription literally would have reported every trusted
precondition in the project as "not load-bearing", on every run. The last row is
why the deletion test survives for **verified** items: there the deleted
assumption was one the item's own body was using.

So step 5c-req runs three checks instead, and the third is the only one that
catches all three mutants:

1. **deletion**, verified items only — `kernel requires[0] is load-bearing when
   deleted (8 verified, 1 errors)`;
2. **tautology probe**, every item: a synthesised
   `proof fn p(<the item's parameters verbatim>) ensures <the conjunct>, { }`
   appended inside `verus! { }`. If it verifies, the conjunct is `true` under
   the parameter types alone. All four of this file's `requires` conjuncts fail
   the probe, as they should; `0 <= i` and `n >= 0` verify (10 verified, 0
   errors against a control of 9) and are caught;
3. **parameter coverage** (step 5a): every parameter the trusted body uses must
   appear in the `requires`. `copy_bytes` uses `src`, `from`, `dst`, `n` and
   constrains all four; delete the first precondition and `['src', 'from']` go
   unconstrained, which is the axiom that the copy is defined for every value of
   them. Deliberately **not** `requires ∪ ensures`: `get_unchecked`'s
   `ensures r == v@[i as int]` mentions `v`, so the union reading would pass
   `requires 0 <= i`.

Known limit of (3): a pure *value* parameter (one written, never used as an
address or a length) legitimately needs no precondition, and would have to be
declared in `spec.md`'s `verus.unsafe_justifications`, which the verdict then
shouts on every run. Neither trusted item here has one.

What none of this closes: a `requires` that is non-trivial, mentions every
parameter, and is still **too weak for the operation** — say `from + n <= src@.len() + 1`.
That is a claim about `copy_nonoverlapping`'s real contract, and the only things
between it and the proof are the comment beside the item and a reviewer.

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
  clauses** (two, since TASK_006 removed the redundant one) with no special handling, and accepted `let (a, b, c, mut d) = f();`
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

Two more, added at TASK_006 and driven by p02:

| # | file | change | why |
|---|---|---|---|
| 8 | `harness/dloop.py`, `harness/vparse.py` | ghost stripping gated on **`vparse.verus_span`**, not on `lang == "rust"` | change 2 above applied the exemption to *all* Rust. Plain Rust is not Verus: `assert!` is live code in a release build (`-C debug-assertions=off` removes `debug_assert!` and nothing else) and `let ghost = <expr>;` is an ordinary binding whose initialiser may be an `unsafe` block. TASK_004_REVIEW put three payloads into `safe_naive.rs`'s measured loop through the gap (§8a) |
| 9 | `harness/check.py`, `harness/vparse.py` | **step 5c**, the clause-deletion stage, on `vparse.clause_spans` / `delete_clause` | §6. The M7 class was defended by a declared pin and nothing else |

`asm.py`'s bulk-memory detection needed a **third** spelling at TASK_006, and this
one was a live false-negative rather than a hypothetical one:

- `is_bulk_symbol` returned `False` for `__memcpy_avx_unaligned_erms`,
  `__memcpy_chk`, `__memmove_chk` and `__memset_chk`, because `_BULK_MEM_RE`
  requires a non-word character on both sides and `_` is a word character. The
  module docstring claimed the opposite.
- **Two of p02's own 32 cells emit a symbol it could not see**: `c-gcc -O3 whole`
  and `c-gcc-h -O3 whole` call `__memcpy_chk@plt`, because this box's gcc
  default-enables `_FORTIFY_SOURCE 3` (§1a). They passed only because they also
  have nine backward branches each. A kernel that is *just* a fortified `memcpy`
  — `has_loop=False`, one `call __memcpy_chk@plt` — would have been failed with
  "no backward branch and no bulk-memory call", which is precisely the false-fail
  the escape hatch exists to prevent. Confirmed by compiling a five-line C file
  with the harness's own flags and reading the disassembly.
- Fixed by also matching the routine name as an underscore-delimited *component*
  of the symbol. `__stack_chk_fail` and `__printf_chk` still do not match. 20
  cases in `asm.selftest_bulk_symbols`, run as part of step 0.

Two things the harness got right without being asked, both worth recording — with
one correction:

- `asm.py`'s bulk-memory alternative to "must have a backward branch" was added
  at TASK_005 *speculatively, for p02, before p02 existed*. **The claim that it
  was necessary was overstated.** Of p02's 32 cells, exactly **one** has no
  backward branch at all and therefore actually needs the relaxation:
  `safe_tuned O0 isolated` (`loops = 0`) — an `O0` row, from which no
  performance number is ever quoted. Every other cell has ≥ 1 back edge, gcc
  `-O3 isolated` included (2 for its 153-instruction body). And that one cell is
  matched by the **v0-mangling extension** (change 3), not by the bulk regex the
  relaxation added: its symbol is
  `_RNvMNtCs..._4core5sliceSh15copy_from_sliceCs..._10safe_tuned`. The
  relaxation is still right — see `__memcpy_chk` above — but its load-bearing
  evidence in this pattern is one `O0` cell and a different code path.
- `check.py`'s per-input `sanitizer_expect` (TASK_005) is what makes this
  pattern greenable at all. Under the previous rule — any ASan hit fails the
  gate — p02 could not have existed.

### 8a. The reopened driver-loop bypass, and what closed it

`_GHOST_RE` was applied to every Rust rung. Three payloads inserted into
`safe_naive.rs`'s **measured** loop each normalised to the canonical 13-statement
sequence, printed the correct checksum, and passed step 6:

| payload | marginal Ir per call (baseline 407.0) | after the fix |
|---|---:|---|
| `assert!(k < nrec as usize);` | 409.0 | 14 statements, fails the diff |
| `let ghost = black_box(src[k * stride]);` | 411.0 | 14 statements, fails the diff |
| `let ghost = unsafe { _mm_prefetch(...) };` | **417.0** | 15 statements, fails the diff |

The third is M9 — the prefetch payload TASK_003_REVIEW put into the *C* driver —
back again in the other language. All three now fail; the five real rungs and
`c/main.c` still normalise to the pin (`verus.rs` is the only file whose region
is inside `verus! {}`, and it is the only one where ghost statements erase).

**And it reopened again, because `verus!` is a token.** TASK_006_REVIEW put the
same M9 payload back into `safe_naive.rs`'s measured loop with three lines:

```rust
macro_rules! verus { ($($t:tt)*) => { $($t)* } }
verus!( fn main() { ... SLB-DRIVER-BEGIN ... } );
```

`vparse.verus_span` accepts `verus!\s*[{(\[]`; the guard in step 5a that says "a
file with a `verus!` block must be in `verus.obligations`" matched
`verus!\s*\{`; the round bracket is the entire bypass. Result: 407.0 → 412.0
Ir/call on `small`, `prefetch` in the disassembly, checksums unchanged, a full
green gate and a `contract sha256` **identical** to the shipped pattern.

Closed at TASK_008, and **not with a fourth regex** — the tree already contained
the third and the paren form walked round it. `dloop.normalise_file` now takes a
`verus_verified` certificate and raises `GhostHarbourError` without it, and
`check.py` supplies that certificate only from *Verus's own verdict*: the file
is in `verus.obligations` and verified with 0 errors in step 5a, **and**
`verus --verify-function <the item enclosing the region> --verify-root` reports
a verified body for it. An item Verus never compiled cannot report one, whatever
its file spells its macros. Fails closed: a region that claims the harbour
without the certificate is a hard failure, not a quiet downgrade. All three
bracket forms were rebuilt at TASK_008 with the payload in place — each would
have matched the pinned 13-statement sequence under the old code, and each now
fails step 6 (`.temp/p008/logs/a{1,2,3}*.log`).

### Two harness warts found and *not* fixed

- `check_proof_domain` prints the failing call's bindings minus the key `"v"`,
  which is p01's name for its big array. p02's big values are `src`,
  `dst_before` and `dst_after`; a `requires` violation would print several
  megabytes. Failure path only, so it is cosmetic until it isn't.
- The same function collects an `off` range for the log only if the binding is
  literally named `off`. p02 binds `src_off`, so that line is silently absent.
  Both suggest the model should declare which bindings are large/positional
  rather than the gate guessing from p01's names.

---

## 9. The anti-collapse floor, fixed at TASK_006

`harness/check.py`'s dynamic anti-collapse floor was
`marginal_Ir >= ALPHA * work_per_call` with `ALPHA = 0.25` a harness constant.
ALPHA's justification is written in **64-bit-lane** terms and p02 denominates
`work_per_call` in **bytes**, and those do not mix:

| | Ir per byte | vs ALPHA = 0.25 |
|---|---:|---|
| glibc `memcpy` on this box (§0c) | 0.104 | 0.42× — **would fail** |
| a kernel that copies and folds 8 bytes | 0.118 | 0.47× — **would fail** |
| `c-clang` with a word-wise fold | 0.348 | 1.39× |
| p02 as shipped, `large` | 2.25 … 2.74 | 9 … 11× |

So the floor **forbade the fastest correct implementation of a bulk copy** — the
exact kernel shape the pattern after this one is meant to have. It passed here
only because rustc does not vectorise a byte fold.

The fix is not to lower ALPHA (that moves all 47 patterns and removes the only
thing the stage does). `model.py` may now declare

```python
min_ir_per_work     = 0.0625
min_ir_per_work_why = "..."
```

— the cheapest legitimate Ir per unit of work **for the algorithm**, which is a
claim a reviewer judges by reading the argument rather than by reading a rung,
and is therefore a legitimate declared value under the TASK_005 rule. p02's
0.0625 is the fused AVX-512 lower bound: per 64-byte lane, at least a load, a
store, a `vpsadbw` and a `vpaddq`. Declaring a rate below the harness default
additionally requires the justification string — which the verdict prints on
**every** run, the `verus.unsafe_justifications` design — and two probe shapes,
so the un-gameable assertion `d(Ir)/d(work) >= rate` still runs.

Measured after the change: 64 cell/probe pairs, marginal Ir 206 … 450 248,
tightest margin **35.9×**, `d(Ir)/d(work)` 2.22 … 110.0.

### 9a. …and the knobs, bounded at TASK_008

TASK_006_REVIEW measured how weak the residual risk was: **the only bound on
`min_ir_per_work` was `> 0`.** `min_ir_per_work = 1e-9` with
`min_ir_per_work_why = "see NOTES.md"` passed the whole gate, printing "derived
floor 0.0 Ir/call" and "tightest margin 2246270772.2×" in exactly the words it
prints "35.9×". Nothing inspects `why` — it is free text. `work_per_call` is a
second unbounded knob in the same sandboxed file, and the floor is the
*product*.

Three changes, in decreasing order of how much they actually buy:

- **An absolute bound, `MIN_DECLARABLE_IR_PER_WORK = 0.015625`.** Physical, not
  conventional: the tightest rate anyone has argued for here is p02's 0.0625 —
  four instructions per 64-byte AVX-512 lane — and 1/64 is the same four
  instructions across a vector four times wider than anything that exists.
  Below that, a pattern is not making a claim about an algorithm; it is saying
  the work does not happen. `1e-9` now fails outright with that argument in the
  message.
- **The achieved margin is printed beside the declared floor, in the verdict**,
  with what it implies spelled out: p02 reads "declared floor 3.8…255.8 Ir/call;
  tightest measured margin over it 35.9×, i.e. this stage tolerates a 97.2% loss
  of work before it objects." A margin above 100× additionally shouts that the
  floor "rules out total collapse and essentially nothing else".
- **The stage now says what it certifies in its own log**, so a reader of a
  green run cannot over-read the line.

**What this does *not* fix, measured.** Shrinking `work_per_call` by 16× in
`model.py` (`return max(1, min(...) // 16)`) still **passes** — margin 576.7×,
two loud lines in the verdict, no failure. Bounding the product mechanically
would need the harness to know each pattern's unit of work, which is exactly
what `model.py` exists to supply. The defence against that knob is visibility
plus step 2, not rejection: the margin shout is `rep.shout` rather than
`rep.fail` because a legitimately fast rung on a conservative unit of work has a
large margin honestly (p01's margins run 7×–268×), and failing on it would turn
the floor into a *cap* on how good a rung is allowed to be.

**What this stage does not do, on any setting.** It bounds the kernel's *total*
cost, so it cannot certify that one component of the kernel happened — p02
clears any rate on its fold alone, and TASK_004_REVIEW was right to say so. The
mechanism that certifies the copy is **step 2**: `model.py`'s checksum folds the
bytes the copy is supposed to have moved, so a kernel that skips the copy prints
a different number and fails on all 32 cells. Saying "the floor certifies the
copy" was the error; the floor certifies that the kernel's cost scales with the
model's work.

---

## 10. Known gaps

- **The fold dominates the copy 20:1** (§0). Every performance number here is
  mostly a byte-checksum measurement. Stated up front rather than buried.
- **No R2v control cell.** p01's `safe_naive_verus.rs` holds up
  `.memory/01-ladder.md` finding 2 ("a proof buys nothing on its own"); p02
  ships none, so that finding is not re-tested here. `build.py` now makes the
  cell optional per pattern, so adding one later is a file, not a harness change.
- **M7 (§6) is still caught by a declared pin and nothing else — narrowed at
  TASK_006, not closed.** The derived clause-deletion stage removes *redundant*
  and *decorative* clauses (trusted 3 -> 2, `copy_bytes` 2 -> 1, `kernel` 3 -> 2), which is what made
  M7's original diagnosis wrong and what would let a weakening hide behind an
  overlapping neighbour. It does not catch a clause that has been rewritten
  rather than deleted. A wrong trusted `ensures` is an axiom about real Rust
  semantics; the defences are the `spec.md` pin and the written argument beside
  `copy_bytes` in `verus.rs`, and that is inherent rather than a missing check.
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
