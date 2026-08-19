# p03 — findings

Written by the engineer who measured them (TASK_036). Every number here is
either pasted from a command's output or derived from a disassembly listing; a
five-decimal rate in this file always comes from the listing and never from a
two-point marginal (`.memory/03-measurement.md`, TASK_026 §0 item 2). Where a
rate is quoted, **the spelling that produced it is named beside it**; where two
rates are differenced, they are at **matched spelling**.

**Which `Ir` convention: the whole-program marginal**, p05's, p17's, p07's,
p11's and `check.py` stage 3b's. §3 measures whether p03 needed it — no rung
here calls out of the `kernel` symbol except through the driver, so unlike p11
the two columns agree, and §3 says by how much rather than asserting it.

## 0. What was checked before five rungs were built on it

TASK_036 named two premises it was least sure of and asked for them to be
settled on the disassembly first. Both were checked before any rung was written,
with `.temp/p03/probe_c.c`, `.temp/p03/probe_rs.rs` and `.temp/p03/probe_ir.py`.
**Both came back against the task file's expectation**, and one of them changes
what the pattern demonstrates.

### 0a. "It may segfault instead of producing ASan's clean diagnostic" — no. It is not a wild address at all.

The task file expected `stack[SIZE_MAX]` to be "a wild address rather than a
heap overread". It is neither. `sp - 1` at `sp == 0` is `SIZE_MAX`; the pointer
arithmetic is `stack + SIZE_MAX`, which wraps modulo 2^64 to **`stack - 1`** —
8 bytes below the array, **inside the kernel's own stack frame**. That is
arithmetic, not luck, and it is what the disassembly shows: gcc's shipped kernel
addresses the array at `(%rsp,%rsi,8)` with the canary at `0x208(%rsp)`, so the
underflow reads `-0x8(%rsp)`, in the red zone below the frame.

| build | `firstpop` (one POP at `sp == 0`) |
|---|---|
| clang `-O3`, plain | no fault, exit 0, **wrong answer** (`18446744073709551593` vs the model's `225`) |
| gcc `-O3`, plain | identical wrong answer |
| clang `-O3` + ASan | `stack-buffer-underflow`, READ of size 8, exit 1 |
| gcc `-O1` + ASan (**the gate's build**) | `stack-buffer-underflow ... [32, 544) 'stack' (line 33) <== Memory access at offset 24 underflows this variable`, exit 1 |

So the prediction that "a sanitiser should catch it every time" holds, and the
worry that it would not is refuted with arithmetic. **What is genuinely new is
that the plain build does not fault**, which is p08's shape — a bug that
executes and is not observable without a sanitiser — arriving on a *spatial*
error rather than an aliasing one.

**Where it DOES fault, measured.** A sustained underflow walks one 8-byte slot
further down the stack per POP:

```
$ ./probe_c_clang allpop 1000000 ; echo $?     ->  exit 0
$ ./probe_c_clang allpop 1050000 ; echo $?     ->  Segmentation fault, 139
$ ulimit -s                                    ->  8192   (KiB)
```

`8192 KiB / 8 B = 1 048 576`, and the threshold sits between 1 000 000 and
1 050 000. The fault is the **stack rlimit**, exactly, and it is a property of
the box rather than of the program — which is why `adversarial-allpop.bin` uses
200 operations and not a million.

### 0b. `STACK_CAP = 64` and a 5-byte operation are both right.

- **The array is real.** clang C emits `sub $0x188,%rsp` plus the 128-byte red
  zone, gcc `sub $0x218,%rsp`, rustc `sub $0x208,%rsp`; the stack slots are
  addressed as `(%rsp,%rsi,8)` in every one. Nothing is register-allocated and
  nothing is sunk. A `SMALL_CAP = 4` control was built and behaves the same way,
  so 64 is not near a threshold — it was kept because it is what a bytecode
  interpreter uses and because the overflow row needs a cap a window can exceed.
- **The 5-byte operation dominates the per-call constant.** At `nops = 200` the
  unsafe rung's marginal is 2546.85 Ir/call against a per-call constant of ~107
  (extrapolating the `nops` slope to 0), i.e. **96% of the call is the opcode
  stream**.
- **The written-out little-endian decode does not dominate either — under
  clang.** clang and rustc fold `b0 + 256*b1 + 65536*b2 + 16777216*b3` back into
  a single unaligned `mov 0x5(%rax,%rcx,1),%esi`. **gcc does not**: its shipped
  kernel emits four `movzbl` plus three `shl $0x8` plus three `add`, ten
  instructions for the same u32. That is a gcc-vs-clang codegen difference on
  the *same source*, it is not a fortify or ssp artefact, and §3 quotes it
  beside the C column rather than letting it read as a language result.

## 1. The dispatch stays a real branch in all eight cells

`harness/asm.py`, `-O3 isolated`, kernel symbol only — plus a direct grep for
`cmov`/`set*` on the dispatch, because `.memory/01-ladder.md` records LLVM's
`X86CmovConverterPass` moving p07 in the *opposite* direction and `spec.md` pins
`if op == 0` for exactly that reason. **This is checked, not assumed.**

| cell | `n_fn` / nopad | loops | `vector_regs` | `cmov`+`set*` |
|---|---|---:|---|---:|
| `c-gcc` | 74 / 72 | 3 | `[]` | **0** |
| `c-gcc-h` | 76 / 74 | 4 | `[]` | **0** |
| `c-clang` | 46 / 45 | 3 | `[]` | **0** |
| `c-clang-h` | 51 / 49 | 4 | `[]` | **0** |
| `safe_naive` | 131 / 129 | 4 | `[]` | **0** |
| `safe_tuned` | 82 / 80 | 4 | `[]` | **0** |
| `unsafe` / `verus` | 66 / 64 | 4 | `[]` | **0** |
| **`m_branchless` (control)** | **95 / 93** | **2** | `[]` | **1** |

`vector_regs` is empty in 8 of 8 kernels: **no rung reaches SIMD**, and there is
nothing here that could — the loop is a data-dependent two-way branch followed
by a serial dependence through `sp` and `acc`, so operation `k+1` cannot even be
routed into the right arm until operation `k`'s effect on `sp` is known.

The falsifier is `m_branchless` (`controls/gen_controls.py`), the deliberately
branchless spelling: it has **two** back edges instead of four, one `cmov`, and
it is **+3559 Ir/call dearer than R4 on `small` and +13 799 on `large`** — and
+3200 / +13 173 dearer than the R3 it is derived from (§10c). So the
branchless form is not something the compiler is being prevented from reaching —
it is a spelling that is much worse here, which is the opposite of p07, where
LLVM applied it unasked. Both facts belong in the same sentence: *whether a
compiler branchifies or cmov-ifies a data-dependent select is not a property of
the pattern, and p03 and p07 are the two directions.*

## 2. Where the instructions go — and gcc does not fold the little-endian decode

Read off the shipped listings, `-O3 isolated`:

| what | c-clang | c-gcc | rustc (R4) |
|---|---|---|---|
| the `val` u32 decode, written out as `b0 + 256*b1 + 65536*b2 + 16777216*b3` | **one** unaligned `mov 0x5(%rax,%rcx,1),%esi` | **ten**: 4×`movzbl`, 3×`shl $0x8`, 3×`add` | **one** unaligned `mov` |
| the stack slot | `-0x88(%rsp,%rcx,8)` | `(%rsp,%rsi,8)` | `(%rsp,%r15,8)` |
| the array | `sub $0x188,%rsp` + the 128 B red zone | `sub $0x218,%rsp`, canary at `0x208(%rsp)` | `sub $0x208,%rsp` |

**The eight-instruction gap is the whole of gcc's deficit and it is per PUSH**,
which is where the value load lives: §4's swept law gives `c-gcc = 19·xpush + …`
against `c-clang = 11·xpush + …`, i.e. **`c-gcc − c-clang = 8.00000 Ir per
executed push, exactly, over 77 blobs**. `.memory/01-ladder.md` says to
establish whether a gcc-vs-clang gap is a *default* or a *capability* before
reporting it; here it is neither a flag nor a fortify artefact but a missing
load-widening in gcc's own middle end on identical source, and it is the third
pattern in this project where the C column is decided by which compiler.

Nothing in this pattern calls a library routine except the Rust rungs' `memset`
(§3c). There is no `strlen`, no `memcpy` and no IFUNC dispatch, so p11's
library-versus-safety decomposition has no analogue here and the C-vs-Rust
comparison is a plain codegen one.

## 3. Performance — the column, the memset, and the two inputs

**Which `Ir` column, and why it is not p11's answer.** p11's rungs call out of
the `kernel` symbol into three different library routines, so its
kernel-exclusive column is wrong for four of eight cells. p03's kernels call
**one** thing and only in the Rust rungs — glibc `memset`, for
`[0u64; STACK_CAP]` — so the two columns differ by a known, attributable term
and §3c prices it. Everything in §4, §10 and §12 is the **kernel-exclusive**
column, which on p03 is **exact**; §3b is the measurement that says why the
whole-program marginal is not.

`-O3 isolated`, `panic=unwind`. `xpop` is the number of POPs that actually pop.

| rung | `n_fn`/nopad | `Ir`(kernel) small | memset | `main` | whole | `Ir`(kernel) large | memset | `main` | whole |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R1 c-gcc | 74/72 | 3600 | 0 | 15 | 3615.00 | 9931 | 0 | 15 | 9946.72 |
| R1h c-gcc-h | 76/74 | 3836 | 0 | 15 | 3851.00 | 10345 | 0 | 15 | 10360.72 |
| R1 c-clang | 46/45 | 2633 | 0 | 14 | 2647.00 | 7748 | 0 | 14 | 7762.72 |
| R1h c-clang-h | 51/49 | 2869 | 0 | 14 | 2883.00 | 8162 | 0 | 14 | 8176.72 |
| **R2 safe-naive** | 131/129 | **8112** | 50 | 14 | 8176.00 | **25621** | 50 | 14 | 25685.30 |
| **R3 safe-tuned** | 82/80 | **3361** | 43 | 14 | 3418.00 | **9010** | 43 | 14 | 9067.30 |
| **R4 unsafe** | 66/64 | **3002** | 43 | 14 | 3059.00 | **8384** | 43 | 14 | 8441.30 |
| **R5 verus** | 66/64 | **3002** | 50 | 13 | 3065.00 | **8384** | 50 | 13 | 8447.30 |

`small` is 237 operations with 118 executed pops (50% POP, stack half full);
`large` is 830 with 207 (25% POP, **stack runs full** — **352** of its 623
pushes are dropped by the guard). Both facts are in the table's arithmetic
through §4's law, and `inputs/gen.py` explains why a density below 50% must
saturate. (Counts per call, replayed from `model.py`'s own driver loop by
`.temp/p37/counts_sl.py`: `small` = 237 ops / 119 xpush / **0** dpush / 118 xpop
/ 0 epop, `large` = 830 / 271 / 352 / 207 / 0. An earlier draft put `large`'s
dropped pushes at 559, which is `dpush + xpop`.)

Against R4, kernel-exclusive:

| rung | small | large |
|---|---:|---:|
| c-gcc | +19.92% | +18.45% |
| c-gcc-h | +27.78% | +23.39% |
| c-clang | −12.29% | −7.59% |
| c-clang-h | −4.43% | −2.65% |
| **R2** | **+170.22%** | **+205.60%** |
| **R3** | **+11.96%** | **+7.47%** |
| **R5** | **0.00%** | **0.00%** |

**R5 − R4 = 0.00 on the kernel column, both inputs**, and the kernels are
byte-identical (`md5_fn 52432361a348`, 66 instructions, `md5_raw` equal), so
finding 1 holds on a pattern with three trusted accessors rather than one.

### 3b. p03 is the SECOND pattern whose `marginal_ir_per_call` does not cancel the environment — and the buffer is on the STACK

`.memory/03-measurement.md` records that p08's whole-program marginal drifts
±0.08 with the environment block, mechanistically, because its per-iteration
work runs through glibc `memcpy`/`memmove` whose path length depends on buffer
alignment. **p03 reproduces that, an order of magnitude larger, on a `memset`
of a STACK array**, and it is worth stating because nothing predicted the stack
would behave like the heap here:

```
kernel-exclusive Ir/call, unsafe vs verus, small.bin :  3002.00  vs  3002.00   <- EQUAL
glibc memset  (libc+0x189480)                       :    43.00  vs    50.00   <- +7
main                                                :    14.00  vs    13.00
whole-program marginal                              :  3059.00  vs  3065.00
```

The two binaries have **byte-identical kernels** and differ by 7 Ir/call inside
libc's `__memset_avx2_unaligned_erms`, because `main`'s frame puts the 512-byte
array at a different alignment. The same term moves when only the *probe file's
path length* changes (measured: `unsafe`/`small` reads 3059.00 through one probe
directory and 3066.00 through another, the two differing in nothing but the
argv string) — which is exactly `.memory`'s *"the build itself moves the level
… 64 bytes of path length change the alignment"*, on a stack buffer.

**Consequence, and it is the rule this pattern adds**: on p03 the
kernel-exclusive column is the exact one and the whole-program marginal carries
a ±7 Ir alignment term. That is the *opposite* of p11, where the marginal is the
honest column, and the discriminator is not "does the kernel call out" but
**"does the thing it calls out to have a data-dependent path length"**. Every
rate in §4 and §10 is therefore kernel-exclusive, and the whole-program column
above is printed beside it rather than instead of it.

### 3c. What safe Rust's uninitialised array costs, priced rather than argued

Safe Rust has no uninitialised array; all four Rust rungs write
`[0u64; STACK_CAP]` and C's `uint64_t stack[64];` is not initialised. That is a
**language** difference, not a bounds check, and `spec.md` forbids `MaybeUninit`
so that it cannot be silently deleted on the unsafe side alone. The control
`m_uninit` (R4 with `MaybeUninit::uninit().assume_init()`) prices it:

```
m_uninit  -  unsafe  =  -17.00000 flat        (swept, zero residual, 19 blobs)
memset term          =   43.00 -> 0.00
                        ------------------
total                =   ~60 Ir per call, independent of `nops`
```

**~60 Ir/call, about 2.0% of R4's `small` cell and 0.7% of its `large` one.** It
amortises along `nops` and is *not* part of any number in §4, because §4 is
kernel-exclusive and rung-to-rung between rungs that all pay it.

⚠ **Nor is it part of the C-vs-Rust rows in §3, and an earlier draft said it
was** (TASK_036_REVIEW). Those rows are **kernel-exclusive** too, and the
`memset` runs in libc, outside the kernel symbol — so the 43–50 Ir/call that
only the Rust rungs pay is **excluded** from them. The size of the difference:
`c-clang` reads **−12.29%** against R4 kernel-exclusive and **−13.47%**
whole-program. The `[0u64; 64]` fill is priced here, in this subsection, and
nowhere else; a reader wanting the C-vs-Rust gap *with* it has to add it back.

## 4. The swept laws — five exact integer cost models, zero residual

`inputs/gen.py --sweep` emits three bands and the branch pair:

* **band A** `sweep-n008 … sweep-n071` — 64 consecutive operation counts at 50%
  POP density, every POP popping;
* **band B** `sweep-d000 … sweep-d120` — 13 POP densities from 0 to 50% at a
  fixed 240 operations, every POP still popping;
* **band C** `sweep-e130 … sweep-e240` — 12 densities from 54% to 100%, **the
  POP guard TAKEN**, which is the axis that decides whether the law is per POP
  *operation* or per POP that actually *pops*. No earlier pattern here had a way
  to ask that.

Bands A and B alone are **not enough**, and that is a trap worth recording: in
band A `xpop = nops/2`, so a two-regressor fit is nearly collinear and its split
is not identified; in band B `nops` is constant, so the design is rank-deficient
outright and least squares returns garbage *with zero residual*. Only the pooled
design separates the terms. `.memory/01-ladder.md` warns about the three-point
fit; this is the same failure with 64 points.

The regressors are the four things an operation can be, counted **visit-weighted
over the calls the driver actually makes** (`.temp/p03/counts.json`, replayed
from `model.py`): `xpush` a push that pushes, `dpush` a push the guard drops,
`xpop` a pop that pops, `epop` a pop that finds the stack empty.

```
kernel-exclusive Ir per call, -O3 isolated       MAX RESIDUAL 0.0000, 89 blobs

  c-clang-h  (R1h) = 11·xpush +  7·dpush + 13·xpop +  9·epop + 26
  c-gcc-h    (R1h) = 19·xpush +  7·dpush + 13·xpop +  7·epop + 41
  safe_naive (R2)  = 31·xpush + 27·dpush + 37·xpop + 28·epop + 57
  safe_tuned (R3)  = 11·xpush +  7·dpush + 17·xpop +  8·epop + 46
  unsafe     (R4)  = 11·xpush +  7·dpush + 14·xpop +  8·epop + 41

                                                 MAX RESIDUAL 0.0000, 77 blobs
                                                 (the 77 with epop == 0; see below)
  c-clang    (R1)  = 11·xpush +  7·dpush + 11·xpop + 26
  c-gcc      (R1)  = 19·xpush +  7·dpush + 11·xpop + 41
```

⚠ **The `R4` row is R4's, and the sweep never measured R5.** It used to be
labelled `unsafe/verus`: `.temp/p03/kir-band-*.json` has no `verus` row, so the
row is `unsafe`'s 89 blobs and nothing else. R5 is *entitled* to the same law
at `-O3` — §8 pins R4 and R5 to the same machine-code bytes (`md5_raw` equal,
`md5_fn 52432361a348`), and finding 1 says a proof costs zero instructions —
but that is an inference from the identity pin, not a sweep, and the label
should not have said otherwise.

⚠ **And the design's support is thin where two of the five terms live**
(TASK_036_REVIEW §6, exact rational rank). The pooled design is rank **5/5**,
but **every pair of bands is rank-deficient** — `A 3/5, B 3/5, C 3/5; A+B 4/5,
A+C 4/5, B+C 4/5` — so no two bands identify these terms and the three-band
pooling is load-bearing rather than decorative. Worse for two coefficients:
`epop > 0` on only **12 of 89** blobs and `dpush > 0` on only **9 of 89**. The
`epop` and `dpush` rates are therefore carried by a handful of points and by
the zero residual, not by a well-spread design, and that is worth saying beside
a law that reports `max residual 0.0000`. (The `small` and `large` cells do not
depend on `epop` at all — both have `epop = 0` — and `large` is where `dpush`
matters: 352 per call.)

**The two R1 cells are fitted on bands A and B only, and that is a result and
not a convenience.** On band C an R1 cell's *own* execution counts stop being
the model's: the first empty POP sets `sp = SIZE_MAX`, so every later PUSH fails
`sp < STACK_CAP` and R1 takes a different path from the one `model.py` counts.
Fitted over all 89 blobs the two R1 rows have residuals of 262 and 785 Ir; over
the 77 where no POP finds an empty stack they are **0.0000**. The residual *is*
the divergence, and it is the cheapest available demonstration that R1 is not
running the same program.

### 4a. The four numbers

| quantity | law | what it is |
|---|---|---|
| `R1h − R1` | **`2.00000 · xpop`**, exactly, **gcc and clang alike**, constant 0 | what the **emptiness check** costs, inside one language |
| `R3ship − R4ship` | **`3.00000 · xpop + 5`** | what the **shipped** safe rung's surviving bounds check costs — a spelling's number, not the class's (§10a) |
| `R2 − R3` | **`20.00000 · (xpush + dpush + xpop + epop) + 11`** | the **opcode-stream** bounds checks, which one reslice removes |
| `R2 − R4` | `20.00000 · nops + 3.00000 · xpop + 16` | the sum |

and the one that is not a number:

| `R3ship − R4ship` on `xpush`, `dpush`, `epop` | **0.00000, 0.00000, 0.00000** | the **push-side** bounds check is deleted outright |

**One array, one compile-time bound of 64, one function, two answers.** The
push's `stack[sp]` sits inside `if sp < STACK_CAP` and LLVM deletes its check;
the pop's `stack[sp]` needs `sp <= STACK_CAP` carried across the
attacker-chosen `if op == 0` branch and the loop back edge, and LLVM does not
carry it. Both safe rungs' push path is **instruction-identical** to R4's: 11
for a push that pushes, 7 for one the guard drops, in R3 and in R4.

⚠ **The discriminator is NOT "the same basic block", and that wording is
refuted** (TASK_036_REVIEW §5). `x_pushhoist` computes `let can_push = sp <
STACK_CAP;` in the loop head and branches on it in the push arm — guard and
write in *different* basic blocks — and it is **byte-identical to shipped R3**
(`md5_fn a5a47dba3129`, `n_fn 82`, 3361 / 9010): LLVM normalises the hoist away
and still deletes the push check. (It is also out of contract by the gate's own
ruler — it misses `required[0]`'s `if sp < STACK_CAP {` — so it refutes the
*mechanism sentence* and is not a spelling of the class; the two facts are
independent.) **What actually separates the two guards is which BOUND each
supplies**: the push guard establishes `sp < STACK_CAP`, which is the upper
bound the write needs, right there and from local information; the pop guard
establishes only `sp > 0`, a *lower* bound, and the upper bound the read needs
has to come from the loop-carried invariant, which is the thing LLVM will not
derive unseeded (§4b).

Two smaller things fall out of the same table:

* **the empty POP costs the same in R3 and R4 (8 both)**, so the safety cost is
  per pop that *pops* and not per POP opcode. That is band C's whole job and it
  is why `adversarial-allpop.bin` — 200 POPs, **zero** of them executing — has
  `R3 − R4 = 5` and not `600`;
* **the safe rungs' extra cost on a DROPPED push is zero too** (7 both), which
  rules out "the array is simply dearer to touch in safe Rust" as an
  explanation. What is dear is exactly the access the optimiser cannot prove.

### 4b. The mechanism, with a zero-parameter control: it is the invariant the proof carries

`.memory/01-ladder.md` reinstates, for p05 and restricted to the row-scaled
term, *"the `O(nrow)` part of the in-contract safety tax is the price of the
optimiser failing the lemma the proof proves"* — and p05's stated excuse is that
its lemma is **nonlinear**. p03's is `sp <= STACK_CAP`, which is linear, so p03
does not have that excuse and the sentence has to be tested rather than
inherited. `m_clamp` is the test: `safe_tuned` with one provably-dead line at
the top of the loop,

```rust
if sp > STACK_CAP { return 0; }
```

which hands LLVM exactly the fact R5's invariant states and nothing else.
`m_clamp_unsafe` is the same line on R4, so the lever is read on both sides
rather than only on the one it flatters. Swept over 19 blobs (band B plus six
band-A points, so the design is not degenerate), zero residual:

```
  safe_tuned (R3)  = 11·xpush + 7·dpush + 17·xpop + 46
  m_clamp          = 11·xpush + 9·dpush + 13·xpop + 46      R3 with the dead test
  unsafe (R4)      = 11·xpush + 7·dpush + 14·xpop + 41
  m_clamp_unsafe   = 11·xpush + 9·dpush + 13·xpop + 41      R4 with the dead test

  m_clamp        - safe_tuned  =  +2·dpush - 4·xpop         MAX RESIDUAL 0.0000
  m_clamp_unsafe - unsafe      =  +2·dpush - 1·xpop         MAX RESIDUAL 0.0000
  m_clamp        - m_clamp_unsafe = 0·xpush + 0·dpush + 0·xpop + 5
```

**Handed the invariant, the safe rung goes 17 → 13 Ir per executed pop and the
unsafe rung 14 → 13, so the safe-versus-unsafe gap goes to EXACTLY ZERO per
pop** and the whole of `R3 − R4` collapses to the same +5 per-call constant it
already had. The dead test costs 2.00000 per *dropped* push, which is why
`m_clamp` is cheaper than R4 on `small` (−113 Ir/call, **zero** dropped pushes)
and dearer on `large` (+502, **352** dropped pushes per call — `.temp/p37/counts_sl.py`
replays `model.py`'s own driver loop: `large` is 830 ops per call, 271 executed
pushes, 352 dropped, 207 executed pops, 0 empty pops. An earlier draft said 559,
which is `dpush + xpop`, the count of operations that are *not* executed pushes.)

⚠ **Where the 2.00000 per dropped push comes from, off the listing** — because
§10a turns on it. In `m_clamp`'s kernel the push guard is respelled
`cmp $0x40,%r15 ; jne <push> ; mov $0x40,%r15d ; jmp <tail>`: knowing
`sp <= STACK_CAP`, LLVM reads the failed guard as `sp == STACK_CAP` and
**materialises the constant** on that edge, which is two instructions more than
the `cmp $0x40,%r15 ; jae <tail>` that R3 and R4 emit. It is not the dead test
executing — the dead test is gone. **Moving the same fact to the loop's back
edge avoids it entirely** (§10a): the header phi is then bounded from below by
the entry value and from above by an asserted back edge, no fixed point is
needed, and the dropped-push edge never learns the equality.

So the sentence survives on a linear fact, and p03 states it in the form the
control licenses:

> **On p03, the entire per-pop safety tax is the price of the optimiser failing
> the invariant the proof proves — measured by handing LLVM that invariant as a
> dead runtime test and watching the gap go to zero, on both sides of the
> comparison, with no fitted parameter.**

⚠ **Two qualifications, both measured, and the sentence is wrong without them.**

**(1) It is not a fact about safe Rust — it is a fact about optimisers, and two
independent middle-ends fail the same lemma the same way** (TASK_036_REVIEW §4).
Give the *C* rung the bounds check a careful C programmer writes on the pop read
(`if (sp >= STACK_CAP) __builtin_trap();` after the decrement, the C analogue of
safe Rust's `if idx >= len { panic }`), ± the identical clamp. Kernel-exclusive
Ir/call, `-O3 isolated`, `.temp/r36/c/k_*.c`:

```
  c-clang-h (shipped R1h)      small=2869  large= 8162   n_fn 51   no check written
  k_bchk-clang    (+check)     small=3341  large= 8990   n_fn 56   check SURVIVES (cmp $0x3f, ud2)
  k_bchk_clamp-clang           small=2869  large= 8866   n_fn 53   md5_fn e5fd25a089b2…
  k_clamp-clang   (no check)   small=2869  large= 8866   n_fn 53   md5_fn e5fd25a089b2…  <- IDENTICAL
  c-gcc-h   (shipped R1h)      small=3836  large=10345   n_fn 76   no check written
  k_bchk-gcc      (+check)     small=4546  large=12997   n_fn 80   check SURVIVES (2x cmp $0x3f)
  k_bchk_clamp-gcc             small=3838  large=10347   n_fn 78   md5_fn d88f71dc501a…
  k_clamp-gcc     (no check)   small=3838  large=10347   n_fn 78   md5_fn d88f71dc501a…  <- IDENTICAL
```

clang keeps the manual C check at **4.00000 Ir per executed pop, exactly**
(+472 / +828 over 118 / 207 pops); gcc keeps it too. Hand either compiler the
identical clamp and **both delete 100% of it**, with the clamped-with-check
binary **byte-identical** to the clamped-without-check one. **gcc shares no
middle-end with rustc**, so this is not an LLVM quirk and not a Rust result:
write it as *"any compiler asked to prove this"*, never as *"safe Rust"*.

**(2) LLVM does eventually DERIVE the fact; what it cannot do is find it
unseeded.** In `m_clamp`'s output the clamp is **gone**, and its `return 0`
semantics is not preserved on the `sp > 64` path — the only `cmp $0x40` left is
the push guard, respelled as an *equality* (see above), which is only sound if
`sp <= 64` is known. So LLVM did derive `sp <= STACK_CAP`; it needed the fact
handed to it once before it would. **That makes this analysis seeding / phase
ordering, not an inability to prove the lemma — a different failure from p05's**,
where the fact itself is nonlinear.

`m_clamp` is `idiom`-legal by the gate's own ruler (0 forbidden hits, 0 required
misses) but it is reported here as a **control and not a rung**: it is dead code
inserted to move a number, which is the shape `.memory/01-ladder.md`'s direction
test exists to catch. ⚠ Note what that exclusion does and does not buy: `m_clamp`
is **byte-identical** to `r3_assert_head`, an in-contract spelling (`md5_fn
7ad05dbef1b7`, both), so **excluding it removes no machine code from the
admissible class** — the same shape `.memory/01-ladder.md` records for p17,
where the excluded spelling and an admissible one compile to the same 478 bytes.

### 4c. Two more levers, priced

```
  m_mask   - safe_tuned  = -1.00000·xpop            `stack[sp & (STACK_CAP - 1)]`
  r3_chunks- safe_tuned  = +1.00000 on EVERY op - 3  `chunks_exact(5)` over the ops
  m_uninit - unsafe      = -17.00000 flat            plus the whole memset (§3c)
```

**Masking removes only 1.00000 of the 3.00000**, which is worth knowing because
`stack[sp & 63]` is the obvious "make the check go away" move and it does not:
it replaces `lea; cmp; ja` with `mov; and`, i.e. three instructions with two.
It is `idiom.forbidden` for a semantic reason (it turns an out-of-range access
into an in-range one, which is the opposite of what this pattern models) and the
measurement says the exclusion is not protecting a number — it would move the
published figure from 3.00000 to 2.00000, i.e. *down*, in the direction that
flatters the thesis. **Forbidding it is against interest.**

**And, stronger, the exclusion protects nothing at all** (TASK_037). The
in-contract R3 class reaches **13.00000 per executed pop** (`r3_assert_tail`,
§10a), which is *below* `m_mask`'s 16.00000 and below R4's own 14.00000 — so a
spelling that violates no entry of the declaration is **cheaper than the
forbidden one**, and the mask is not the cheap thing p03 is refusing to write.
`r3_assert_idx` makes the point exactly: `assert!(sp < STACK_CAP)` stated after
the decrement lands on `m_mask`'s **exact numbers**, 3243 / 8803, in contract
and from a *different* machine code (`md5_fn c7f4d2b8162f` against `a7ea8592ed93`).

### 4d. The branch lever — and it is cleaner than a compiler flag

`sweep-bpred.bin` and `sweep-brand.bin` have the **same operation count (240),
the same POP count (120), the same executed push/pop counts, and the same value
stream by construction** (`inputs/gen.py` draws the values from a second RNG
seeded identically for both files). They differ only in the ORDER of the op
bytes: period-2 alternation against a uniformly random constrained walk. p07 had
to change the *program* to move branch predictability; p03 changes one byte
stream, which is what an attacker actually controls.

`~/tools/valgrind/bin/valgrind --tool=callgrind --branch-sim=yes` and
`--cache-sim=yes`, kernel symbol only, per call of 240 operations
(`.temp/p03/branchsim.py`):

| cell | stream | `Ir` | `Bc` | `Bcm` | `Bcm/Bc` | **`Bcm` per op** | `D1mr` |
|---|---|---:|---:|---:|---:|---:|---:|
| `unsafe` | **pred** | 3041.00 | 722.00 | **1.03** | 0.0014 | **0.0043** | 0.00 |
| `unsafe` | **rand** | 3041.00 | 722.00 | **120.04** | 0.1663 | **0.5002** | 0.00 |
| `safe_tuned` | pred | 3406.00 | 844.00 | 1.04 | 0.0012 | 0.0043 | 0.00 |
| `safe_tuned` | rand | 3406.00 | 844.00 | 120.05 | 0.1422 | 0.5002 | 0.00 |
| `safe_naive` | pred | 8217.00 | 2046.00 | **120.06** | 0.0587 | **0.5002** | 0.00 |
| `safe_naive` | rand | 8217.00 | 2046.00 | 128.71 | 0.0629 | 0.5363 | 0.00 |
| `c-clang` | pred | 2666.00 | 603.00 | 1.03 | 0.0017 | 0.0043 | 0.00 |
| `c-clang` | rand | 2666.00 | 603.00 | 116.61 | 0.1934 | 0.4859 | 0.00 |
| `c-gcc` | pred | 3641.00 | 604.00 | 1.06 | 0.0018 | 0.0044 | 0.00 |
| `c-gcc` | rand | 3641.00 | 604.00 | 118.83 | 0.1967 | 0.4951 | 0.00 |

**`Ir` is identical to the instruction, `Bc` is identical to the branch, `D1mr`
is 0.00 in every cell and both streams — and `Bcm` moves by 116×.** That is as
clean a branch lever as this project can build: nothing about the program, the
workload size or the memory traffic differs, so the locality confound
`.memory/00-environment.md` insists on ruling out is ruled out by construction
rather than by argument. **0.5002 mispredicts per operation on the random stream
is exactly the coin-flip value**, which is the same sanity check `.memory`
records for p07's 0.586 on a binary search.

⚠ **One row is an artefact and it must be labelled as one: `safe_naive` on the
PREDICTABLE stream mispredicts 120.06, the same as everything else does on the
random one.** R2's `Bc` is 2046 against R4's 722 — 1324 extra always-not-taken
bounds-check branches per call — and callgrind's predictor is *"a generic
two-level scheme, not Cascade Lake's"*. The most likely reading is table
aliasing: the extra branches evict the op branch's history. **The honest
statement is that the simulated predictor cannot see p03's lever on R2 at all**,
and no claim in this file rests on that row. `.memory/00-environment.md`'s rule —
strong about direction and ratio, weak about magnitude, and never converted to
cycles — is why this section reports `Bcm` and stops.

⚠ And the second limit is real: **this box cannot turn `Bcm` into time.** The
two blobs are 9632 bytes, they fit L1, and the pair was measured under
callgrind, not on the clock. §11 is where the wall clock is, and it is not
measured on this pair.

## 5. The proof

`./verus_run.py patterns/p03-bounded-stack/verus.rs` → **`9 verified, 0 errors`,
first run, no failed obligation at all.**

Decomposition, each term measured with `--verify-function <name> --verify-root`:

```
STACK_CAP 1 + run 1 + kernel 2 + main 5 = 9
```

`u32_at`, `nops_at`, `zero_stack` and `stack_fold` are non-recursive spec fns
and report 0; the five `external_body` items report 0; `run` is the one
recursive spec fn and carries one termination query. `STACK_CAP` is a `const`
inside `verus!` and is its own query — `.memory/04-verus.md` records that from
p08's `SCR`, and p03 is the second pattern to have one. `--cfg slb_twin` gives
**12**, the +3 being one per twin.

**The invariant, and it is the whole result.** p03's kernel has ONE loop and
ZERO nonlinear arithmetic. The memory-safety obligation is

```
sp <= STACK_CAP
```

maintained across `if op == 0 { if sp < STACK_CAP { sp = sp + 1 } } else { if sp
> 0 { sp = sp - 1 } }`, i.e. **across a two-armed branch whose condition is a
byte of the attacker's file**, and the back edge. Z3 takes it as one invariant
clause with no lemma, no `by (nonlinear_arith)`, no proof block and no ghost
statement beyond the two the driver already needs. **LLVM does not take it at
all**, and §4 is what that costs.

That is p05's sentence — *"the `O(nrow)` part of the in-contract safety tax is
the price of the optimiser failing the lemma the proof proves"* — on a fact that
is **linear**. p05's stated excuse was nonlinearity (`nrow*ncol <= avail ⟹
i*ncol + j < avail`); p03 does not have that excuse, and p08 is the other
precedent: a provably-dead, purely *linear* range check that LLVM keeps because
the fact it needs is relational across the loop.

**The functional half is the more interesting spec.** `run` threads the whole
machine state — a `Seq<u64>` of stack contents, an `int` stack pointer and the
`u64` accumulator — where p16's, p07's and p11's spec functions thread a scalar
accumulator and a cursor. The relational invariant is p16's shape
(*"the run from here is the whole run"*):

```
run(buf, off, k, nops, stack@, sp, acc) == run(buf, off, 0, nops, zero_stack(), 0, 0)
```

and the loop needs no `invariant_except_break` and no loop `ensures`, because
p03's loop has exactly one exit. That is the *simplest* loop structure of any
pattern here (p11 has three loops, two of them two-exit) carrying the *hardest*
LLVM obligation, which is the pairing worth noticing.

### 5b. TCB tally

```
$ grep -c 'assume('              patterns/p03-bounded-stack/verus.rs   -> 0
$ grep -c 'assume_specification' patterns/p03-bounded-stack/verus.rs   -> 0
$ grep -c 'verifier::external\]' patterns/p03-bounded-stack/verus.rs   -> 0
$ grep -n  'verifier::external_body' ...                               -> 5 hits
```

**TCB: 10 lines across 5 items, THREE of them `unsafe`.** Every earlier pattern
in this project (p01, p02, p05, p07, p11, p16, p17) has exactly **one** trusted
`unsafe` accessor. p03 has three, and the reason is structural rather than
sloppy: **the kernel has two buffers and one of them is written.**

| item | lines | `unsafe`? | `requires` | `ensures` |
|---|---:|---|---|---|
| `buf_get_unchecked` | 1 | yes | `i < v@.len()` | `r == v@[i as int]` |
| `stack_get_unchecked` | 1 | yes | `i < v@.len()` | `r == v@[i as int]` |
| `stack_set_unchecked` | 3 | yes | `i < old(v)@.len()` | `final(v)@ == old(v)@.update(i as int, x)` |
| `load_input` | 4 | no | — | — (deliberately: an `ensures` here would be an axiom about a file's contents) |
| `emit` | 1 | no | — | — |

(Body-line counts are the gate's own, printed at stage 5a. Against p11's 6 lines
across 3 items, p03's 10 across 5 is **+4 lines and +2 trusted `unsafe` items**,
and every one of the extra lines is on the second buffer.)

**That is the price of the second array, and it should be quoted as a cost.**
p11's whole memory-safety claim is one trusted `requires`; p03's is three, one
of which licenses a *store*. Two things follow and both are stated rather than
softened: a wrong `ensures` on `stack_set_unchecked` could axiomatise that a
store lands where it does not, which is strictly worse than a wrong read
axiom; and stage 5a's parameter-coverage rule needs its first justification in
this project (below).

**A conjunct the first draft carried, and the gate refused it — worth recording
because it is a TRUSTED item and the shape is the one `.memory/04-verus.md`
warns about.** Both stack accessors were first written
`requires i < v@.len(), v@.len() == 64`, on the reasoning that a caller should
be handed the type-level length rather than re-deriving it. For a `&[u64; 64]`
that second conjunct is a **tautology**: vstd's `array_len_matches_n` discharges
it from the parameter type alone, so it demanded nothing of any caller. Two
independent gate stages said so on the same run and neither is a pin:

```
[req-mut] verus.rs stack_get_unchecked requires[1] is a TAUTOLOGY:
          `v@.len() == 64` is provable from the parameter types alone
          (10 verified, 0 errors -- control 9)
[twin]    verus.rs:255 `slb_twin_stack_get_unchecked` still verifies with the
          single conjunct `v@.len() == 64` DELETED from its `requires`
          (12 verified, 0 errors)
```

Both conjuncts were dropped from both accessors and both twins; `9 verified, 0
errors` and `12 verified, 0 errors` are unchanged either way, which is the
point — **a tautological conjunct on a trusted item is invisible to Verus and
visible only to these two stages**. The per-conjunct form of the twin deletion
probe is what caught the second one, and `.memory/04-verus.md` records that it
was made per-conjunct at TASK_010 *"before a multi-clause accessor arrives"*.
p03 is that arrival, and it is the first time the per-conjunct refinement has
fired on a shipped draft rather than on a constructed mutant.

**p03 is also the first pattern to exercise the documented false positive of the
parameter-coverage rule.** `.memory/04-verus.md` says: *"a pure value parameter
(`fn write(dst, i, v)` — `v` is written, never used as an address) genuinely
needs no precondition. Say so in `spec.md` and the verdict shouts it on every
run"*, and adds *"Nothing in the tree exercises it yet."* `stack_set_unchecked`'s
`x` is exactly that parameter, `spec.md`'s `verus.unsafe_justifications` says so,
and the gate `rep.block`s it every run. It is a **shout, not a hatch around a
real check**: `v` and `i` — the two parameters that decide whether the store is
defined — are both constrained.

### SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked(i) }` and the twin's is `v[i]`. Those are the same
operation with and without the bounds check that `<[T]>::get_unchecked`'s
documented contract makes the caller's responsibility, so a `requires` too weak
to license the first is too weak to license the second, and Verus can see the
second. Nothing else is in either body: no arithmetic, no second read, no side
effect. This is the accessor p01, p02, p05, p07, p11, p16 and p17 all ship,
character for character.

(b) *Is the `ensures` complete with respect to every unchecked operation the
body performs?* The body performs exactly one unchecked operation — a read of
`v` at index `i` — and the single `ensures` clause `r == v@[i as int]` names it
and its result. There is no second index, no write, no aliasing and no
provenance step for a clause to be missing. This is the labelled blind spot in
`.memory/04-verus.md` (a body that also read `i + 1` would pass every mechanical
check), and the only backstop for it is Miri on `unsafe.rs`, which this pattern
runs on all six inputs (§8).

(c) *Does each clause mean the same in both configurations?* Yes, and it is
checkable rather than asserted. Counted the way the gate counts it — over
`vparse.blank_noncode(...)`, i.e. the token stream with comments and string
literals blanked — the token `slb_twin` occurs only on the three twins' own
`#[cfg(slb_twin)]` attributes and nowhere else in `verus.rs`, and `verus.rs`
includes nothing but `common/driver.rs`, which is outside `verus!` and carries
no `slb_twin`. `i`, `v` and `v@.len()` denote the same values in both
configurations; there is no `#[cfg]`-varying `const`, `type` or `use` anywhere
in the file.

### SLB-TRUSTED-ARGUMENT verus.rs stack_get_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u64; 64]` and the twin's is `v[i]` on
the same type. Verus's own array support (`vstd::array`, `array_index_get`, and
the `a[i]` index form its docs recommend) gives the checked form a specification
with the identical `0 <= i < N` obligation, so the twin is the same operation
with the check that `get_unchecked` moves onto the caller. The two bodies differ
in nothing else. **This is the accessor p03's bug is about**: R1's missing
`sp > 0` makes the argument `SIZE_MAX`, and `i < v@.len()` is precisely what
excludes it — §6c is the mutant that shows the obligation fails when the exec
bound is widened, i.e. that it is load-bearing rather than decorative.

(b) *Is the `ensures` complete with respect to every unchecked operation the
body performs?* The body performs exactly one unchecked operation — a read of
the array at index `i` — and `r == v@[i as int]` names it and its result. There
is no write here, no second index, no aliasing and no provenance step. The
`requires` is **one** conjunct: a draft that added `v@.len() == 64` to hand the
caller the type-level length was refused by the gate as a tautology (§5b), and
correctly — for a `&[u64; 64]` the caller gets that fact from vstd's
`array_len_matches_n` for free, so `i < v@.len()` already reads `i < 64`. The
blind spot of `.memory/04-verus.md` applies unchanged and Miri on `unsafe.rs` is
the backstop.

(c) *Does each clause mean the same in both configurations?* Yes, and after the
tautology was dropped there is no constant in the clause at all — `i < v@.len()`
mentions only the two parameters. That closes the bypass `.memory/04-verus.md`
records at TASK_009_REVIEW by construction rather than by inspection, where a
`#[cfg(slb_twin)] const SLACK` made the twin check `i < v@.len() + 0` while the
shipped file used `+ 1`. The array's *type* still carries a `64`, and it is the
same `64` in both configurations because it is in the signature the gate lifts
and compares. The gate's token scan reports `slb_twin` only on the three twins'
own attributes.

### SLB-TRUSTED-ARGUMENT verus.rs stack_set_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked_mut(i) = x; }` and the twin's is `v[i] = x;`. Verus
specifies the checked indexed store on an array with the same `0 <= i < N`
obligation, so a `requires` too weak to license the unchecked store is too weak
to license the checked one, and the gate's deletion probe confirms the twin
*uses* the precondition rather than merely carrying it. **This is the project's
first trusted item that writes through an unchecked index**: p02's `copy_bytes`
writes, but through `copy_nonoverlapping` into a `&mut [u8]` whose length is a
runtime value, so p03's is the first indexed store and the first on a
fixed-size array.

(b) *Is the `ensures` complete with respect to every unchecked operation the
body performs?* The `requires` is one conjunct, `i < old(v)@.len()` — the
`old(v)@.len() == 64` a draft carried was refused as a tautology, §5b. The body
performs exactly one unchecked operation — a store of
`x` into slot `i` — and the single `ensures` clause states it as a **whole-sequence
equality**, `final(v)@ == old(v)@.update(i as int, x)`, not as a property of
slot `i` alone. That is deliberate and it is the shape
`.memory/02-bench-rules.md` argues for in its p02 worked example: one clause
says both *"slot `i` became `x`"* and *"nothing else moved"*, so a body that
also wrote slot `i + 1` would contradict the `ensures` rather than slip past it.
This is the one place in p03 where the blind spot of `.memory/04-verus.md` is
narrower than usual — for a **read**, an extra unlicensed read is invisible to
the `ensures`; for a **write** into a value the `ensures` fully determines, an
extra unlicensed write is not. It is not closed, because a write *outside* `v`
would still be invisible; Miri on `unsafe.rs` remains the backstop and is why
`miri.required` is true.

(c) *Does each clause mean the same in both configurations?* Yes, on the same
grounds as the accessor above: the `requires` is the single conjunct
`i < old(v)@.len()` and mentions no constant at all, `old(v)` and `final(v)` are
Verus's own `&mut` spellings and are not configuration-dependent, and the gate's
token scan reports `slb_twin` only on the three twins' own attributes. The one asymmetry worth
naming is that this item's `requires` does **not** constrain `x`, and that is
declared in `spec.md`'s `verus.unsafe_justifications` and shouted by the gate on
every run rather than being left for a reader to notice.

## 6. The proof mutants — four, and each fails for a different reason

`.memory/05-layout.md` item 11: a Verus file that does not verify cleanly cannot
live in the pattern directory, so each mutant is generated into `.temp/` from
the **shipped** `verus.rs` by exact-string substitution with an asserted hit
count (`controls/gen_controls.py`), and this section carries the commands and
the output.

```
$ python3 patterns/p03-bounded-stack/controls/gen_controls.py
$ ./verus_run.py .temp/p03/controls/p1_weak_requires.rs [--cfg slb_twin]
```

⚠ Line numbers below move with `verus.rs`'s header comment and no gate stage can
see that. Treat a drifted one as a stale citation and re-run the two commands.

### 6a. `p1_weak_requires` — one character, and only the TWIN sees it

`i < v@.len()` → `i <= v@.len()` in `stack_get_unchecked` **and** its twin, so
the signatures still match and the contract pin does not move.

```
$ ./verus_run.py .temp/p03/controls/p1_weak_requires.rs
verification results:: 9 verified, 0 errors                  <-- SHIPPED CONFIG PASSES

$ ./verus_run.py .temp/p03/controls/p1_weak_requires.rs --cfg slb_twin
error: precondition not met: index in bounds for this access
verification results:: 11 verified, 1 errors
```

R5's trusted base would otherwise axiomatise that **reading `stack[64]` — one
`u64` past a 512-byte stack array — is defined and equals `v@[64]`**, which is
the neighbouring-stack-slot read this pattern exists to model. The tautology
probe cannot see it (it is not a tautology), parameter coverage cannot see it
(both parameters appear), and deletion is not applied to trusted items by
construction. **The verified twin is the only mechanism in this project that
catches it** (`.memory/04-verus.md`), and p03 is the first pattern where the
twin has been exercised on an accessor that is *not* the slice one every earlier
pattern ships.

### 6b. `p2_nopopguard` — R1's bug written into R5, and Verus refuses it before it is a memory error

The `if sp > 0 { ... }` deleted from the **exec** code, i.e. `c/kernel.c`'s
kernel transplanted into R5.

```
$ ./verus_run.py .temp/p03/controls/p2_nopopguard.rs
error: possible arithmetic underflow/overflow
   --> .temp/p03/controls/p2_nopopguard.rs:414:18
verification results:: 8 verified, 1 errors
```

**Line 414 is `sp = sp - 1;`, and that is the sharpest statement of what p03's
bug is: it is caught as an ARITHMETIC error, not as a memory error.** The
`usize` subtraction underflows before any index is formed, so Verus never gets
as far as `stack_get_unchecked`'s precondition. That is a structurally different
verdict from p16's (`decreases not satisfied`, a termination failure), p11's
(the same, on a scan with no bound) and p07's (a bounds precondition), and it
matches the C exactly: UBSan reports p03's bug as `index 18446744073709551615
out of bounds`, i.e. as the *value* being absurd rather than the *address*.

### 6c. `p3_weak_invariant` — the invariant is load-bearing for the ACCESS

The loop invariant `sp <= STACK_CAP` weakened to `sp <= STACK_CAP + 1`, which is
one past what is true and is exactly what LLVM would need to be handed (§4b).

```
$ ./verus_run.py .temp/p03/controls/p3_weak_invariant.rs
error: precondition not satisfied
   --> .temp/p03/controls/p3_weak_invariant.rs:416:57
verification results:: 8 verified, 1 errors
```

The failing precondition is `stack_get_unchecked`'s `i < v@.len()` — **the
obligation that carries p03's entire memory-safety claim** — so the invariant is
load-bearing rather than decorative, and it is load-bearing *for the same fact*
whose absence costs 3.00000 Ir per pop in both safe rungs. That is the pairing
§4b is about, established from two directions.

### 6d. `p4_push_offbyone` — the OTHER guard is load-bearing too

`if sp < STACK_CAP` widened to `if sp < STACK_CAP + 1`.

```
$ ./verus_run.py .temp/p03/controls/p4_push_offbyone.rs
error: invariant not satisfied at end of loop body
error: precondition not satisfied
verification results:: 8 verified, 1 errors
```

It fails **twice**: the invariant no longer re-establishes, and
`stack_set_unchecked`'s precondition no longer holds. This mutant is here
because `spec.md` claims *"the push guard is in every rung and only the pop
guard is the variable"*, and a claim about which of two guards is the variable
needs the other one shown to matter. All four mutants fail under `--cfg
slb_twin` too (11 verified, 1 error each), so none of them is passing by
skipping a configuration.

## 7. The adversarial table, per rung

`-O3 isolated`, gate stages 4 and 7 (`.temp/p03/gate2.log`). `=` means "agrees
with `model.py`".

| input | model's answer | R1 (c-gcc / c-clang) | R1h ×2, R2, R3, R4, R5 | sanitiser on R1 |
|---|---|---|---|---|
| `adversarial-underflow` | 7473563764999086208 | **differs, and DIFFERS BETWEEN RUNS** | = | **UBSan `index 18446744073709551615 out of bounds for type 'uint64_t [64]'` AND ASan `stack-buffer-underflow`, exit 1** |
| `adversarial-allpop` | 5685940249600 | **differs, and differs between runs** | = | the same pair |
| `adversarial-overflow` | 2401459682193218816 | = | = | clean, exit 0 |
| `adversarial-count` | 0 | = | = | clean, exit 0 |

Five things, and three of them are new to this project.

**1. BOTH sanitisers fire on one access, and UBSan's diagnostic is the better
one.** The gate builds `-fsanitize=address,undefined -O1`, and stderr is:

```
c/kernel.c:79:35: runtime error: index 18446744073709551615 out of bounds for type 'uint64_t [64]'
==855583==ERROR: AddressSanitizer: stack-buffer-underflow on address 0x... READ of size 8
    #0 in kernel c/kernel.c:79
    #1 in main   c/main.c:59
  This frame has 1 object(s):
    [32, 544) 'stack' (line 48) <== Memory access at offset 24 underflows this variable
```

**UBSan names the index and the type; ASan can only name the frame offset.** The
reason is structural and it is why no earlier pattern in this project got both:
p02's, p16's, p17's and p11's out-of-range accesses are on *heap slices*, where
`-fsanitize=bounds` has no static array type to check against and only ASan's
shadow memory can see anything. p03's array is `uint64_t[64]` with the bound in
the type, so the *static* checker fires first and says more. Carry that to any
later pattern with a fixed-size local.

**2. R1's answer is NOT REPRODUCIBLE ACROSS RUNS, and that is a disclosure
finding.** Three consecutive runs of the same binary on the same file:

```
$ ./c-gcc-O3-isolated adversarial-underflow.bin      14649043958731194496
$ ./c-gcc-O3-isolated adversarial-underflow.bin       8364076687040790656
$ ./c-gcc-O3-isolated adversarial-underflow.bin      17907838162355044480
$ setarch --addr-no-randomize ./c-gcc-... x3         14633419586874196096  (x3, identical)
```

**With ASLR off it is bit-stable; with ASLR on every run differs.** So what the
missing guard puts into the checksum is *derived from a stack address*. p17's
finding is a lawful read of a neighbour's **data**; p03's is a read of a
neighbour's **pointer**, and a checksum that leaks one is an ASLR oracle. It is
also why the gate's behaviour table records four distinct values for
`adversarial-{underflow,allpop}/c-gcc` and notes it: those are four opt/mode
variants each drawing a different stack address, not four different programs.

**3. R1's damage compounds without the walk running away.** One empty POP sets
`sp = SIZE_MAX`, so `sp < STACK_CAP` is false for **every later PUSH in that
call** — a single stray operation disables the stack for the rest of the window
without any further out-of-range access. p16's missing check made the walk run
200 MiB past the window; p11's overran at most once per call; p03's overruns
once and then quietly does nothing for the rest of the call, which is a third
blast radius and arguably the hardest to notice.

**4. Where it DOES fault, and it is the box and not the program.** A sustained
underflow walks one 8-byte slot down the stack per POP:
1 000 000 pops → exit 0; 1 050 000 → SIGSEGV; `ulimit -s` is 8192 KiB and
`8192·1024/8 = 1 048 576`. `adversarial-allpop.bin` uses 200, deliberately,
because a segfault would be a fact about the rlimit.

**5. The two controls do their job.** `adversarial-overflow` (96 pushes into 64
slots, then exactly 64 pops) and `adversarial-count` (`5·4096 > 200`) attack the
push guard and the length check — **both of which R1 has** — and all eight cells
agree on both, byte for byte. Without them, "R1 omits exactly one line" would be
a claim about the source; with them it is a measurement.

## 8. Identity, Miri, and the twin (first pattern with more than one)

**R4 ≡ R5, `-O3 isolated`, `exact`:** `md5_fn 52432361a348`, `md5_raw` equal, 66
instructions and 2 of padding each; kernel-exclusive `Ir` **3002.00 both on
`small` and 8384.00 both on `large`**. At `O0` it is `norel` — the crate names
differ in length so the `call` displacements do, which is link layout and not
codegen. The whole-program marginal differs by −8/+6 depending on the input and
§3b shows that is glibc `memset`'s alignment-dependent path length, not the
kernel.

So the project's headline structural result now covers a kernel with **three
trusted accessors, one of which writes through an unchecked index into a
fixed-size array**, a spec function that threads a whole `Seq<u64>` of machine
state, and a memory-safety obligation that is a loop invariant over an
attacker-chosen branch.

**Miri: 6 of 6 inputs, no UB, no blocked rows.**

```
ok miri unsafe.rs on adversarial-allpop.bin    n_iters=4: no UB, stdout '6156800' matches the model
ok miri unsafe.rs on adversarial-count.bin     n_iters=4: no UB, stdout '0'
ok miri unsafe.rs on adversarial-overflow.bin  n_iters=4: no UB, stdout '17534858048539192960'
ok miri unsafe.rs on adversarial-underflow.bin n_iters=4: no UB, stdout '2952675218101715008'
ok miri unsafe.rs on large.bin                 n_iters=4: no UB, stdout '13026927928058472795'
ok miri unsafe.rs on small.bin                 n_iters=4: no UB, stdout '1899124265390257938'
```

Note `adversarial-underflow` is a **clean** Miri row: R4 has the pop guard, so
the input that is UB in C is ordinary in Rust. The row that would matter is a
mutant, and §6b is its Verus half.

**The twin is NOT idle here, and that is a first in eight patterns.**
`.memory/04-verus.md` records that the twin's value accrues from the first
pattern needing a **multi-clause** trusted accessor and that seven patterns in a
row shipped the same single-clause `<[u8]>::get_unchecked`. p03 does not supply
the multi-clause case either — all three of its accessors are single-clause
after §5b's tautology was dropped — **but the per-conjunct deletion probe, added
at TASK_010 explicitly *"before a multi-clause accessor arrives"*, fired on a
shipped draft for the first time** (§5b), and §6a exercised the strength check
on an accessor that is not the slice one. So the honest status is: still no
multi-clause accessor, and the mechanism moved on real code rather than on a
constructed mutant for the first time.

### 8b. What the anti-collapse stage certifies here

```
probe small.bin   work_per_call=1189 byte(s)  => derived floor  297.2 Ir/call
probe large.bin   work_per_call=4154 byte(s)  => derived floor 1038.5 Ir/call
ok 64 cell/probe pairs: marginal Ir per call 2647...137828, all above the derived
   floor (tightest margin 7.5x over a declared 0.25 Ir/byte);
   d(Ir)/d(work) 1.73...32.14 (rate 0.25)
```

Margin 7.5×, i.e. this stage tolerates an ~87% loss of work before it objects.
It is a NOT-COLLAPSED smoke test and nothing finer; what certifies that the work
happened is stage 2's model checksum.

## 9. Dead code that is kept on purpose

`if len < 4 { return 0; }` is unreachable in this benchmark, because the driver
guard is `stride_w >= 4` and `len` is always `stride`. It is kept so the kernel
is **total** and its `requires` stays purely structural: the alternative — a
`len >= 4` precondition — would be a precondition about the driver's own guard
rather than about the buffer, and `.memory/02-bench-rules.md` is explicit that a
`requires` narrow enough to make the proof easy is a `requires` no caller can
discharge. It costs one compare per call.

The `nops == 0` guard is *not* dead in the same way. It is reachable from the
wire format — any window may declare zero operations — and it is what makes the
`0 < nops` case available to the proof. No shipped input happens to take it.


## 10. The spelling spread

`.memory/05-layout.md` item 13 makes this section mandatory, and
`.memory/01-ladder.md` finding 3 requires **at least two independent in-contract
R3 spellings with the cheaper quoted**. All numbers are kernel-exclusive Ir/call
(§3b says why), built by `controls/gen_controls.py` and measured by
`.temp/p03/run_controls.py` (the TASK_036_REVIEW and TASK_037 rows by
`.temp/r36/probe.py` and `.temp/p37/probe.py`, which use the same two-point
marginal). **Every control prints `model.py`'s answer on all six matrix
inputs**, checked by the same script — including every row added below.

### 10a. The R3 side — the shipped spelling is NOT the cheap end, and the class goes NEGATIVE

⚠ **This subsection was wrong at the bottom through TASK_036 and again at
TASK_036_REVIEW.** The first draft published `safe_tuned` as "cheapest found,
both blobs"; the review found `assert!(sp <= STACK_CAP)` at the loop head, which
is in contract by the gate's own ruler and 472 Ir/call cheaper on `small`; and
TASK_037, told to look for a cheaper one before writing the number down, found
that the **same assertion on the loop's back edge** is cheaper again — by 704
Ir/call on `large`. **Two refutations on one pattern, one of them of a figure
that had already survived a review**, so read the table as a search log and not
as a floor.

| spelling | small | small − R4 | large | large − R4 | `md5_fn` | in contract? |
|---|---:|---:|---:|---:|---|---|
| `r3_assert_tail` — `assert!(sp <= STACK_CAP)` on the **back edge** | 2889 | **−113** | **8182** | **−202** | `cd9855c16fe4` | yes — **cheapest found, both blobs** |
| `r3_assert_head` — the same assertion at the loop **head** | 2889 | **−113** | 8886 | +502 | `7ad05dbef1b7` | yes |
| `r3_assert_pop` — the same assertion inside the **pop arm** | 3125 | +123 | 8596 | +212 | `26e8bbe931c3` ⚠ | yes |
| `r3_assert_idx` — `assert!(sp < STACK_CAP)` **after the decrement** | 3243 | +241 | 8803 | +419 | `c7f4d2b8162f` | yes |
| `safe_tuned` (**shipped**) — window reslice, `w[4 + 5*k]` | 3361 | +359 | 9010 | +626 | `a5a47dba3129` | yes |
| `r3_forloop` — `for k in 0..nops` | 3361 | +359 | 9010 | +626 | `a5a47dba3129` | yes |
| `r3_slicestack` — the stack reached as `&mut stack_arr[..]` | 3361 | +359 | 9010 | +626 | `a5a47dba3129` | yes, by the entry's English (see below) |
| `r3_chunks` — `w[4..4+5*nops].chunks_exact(5)` | 3595 | +593 | 9837 | +1453 | `22c952351220` | yes — **dearest found** apart from R2 |
| `safe_naive` (R2, shipped) | 8112 | +5110 | 25621 | +17237 | `f73287f3ba30` | yes |
| `m_mask` — `stack[sp & (STACK_CAP - 1)]` | 3243 | +241 | 8803 | +419 | `a7ea8592ed93` | **no** — forbidden |
| `m_clamp` — R3 + a dead `if sp > STACK_CAP` | 2889 | −113 | 8886 | +502 | `7ad05dbef1b7` | **no** — dead code inserted to move a number |
| `m_branchless` — the dispatch as a select | 6561 | +3559 | 22183 | +13799 | `9515fe351865` | **no** — `required[4]` |

* **fixed-R4 bound** (`R3ship − R4ship`, R4 held by fiat — the only sound
  quantity per `.memory/01-ladder.md`): **+359 on `small`, +626 on `large`**,
  and as a law `3.00000·xpop + 5`. It survives as an **upper** bound on
  `inf(in-contract R3) − R4ship`, and what it bounds is now **negative on both
  blobs**.
* ⚠ **`3.00000` per executed pop is the SHIPPED SPELLING's rate, not the
  class's.** Swept exactly, 19 blobs, `max residual 0.000000`
  (`.temp/p37/sweepfit.py`), against R4's `11 xpush + 7 dpush + 14 xpop + 41`:

  ```
    safe_tuned      11·xpush + 7·dpush + 17·xpop + 46      +3.00000 per pop
    r3_assert_idx   11       + 7       + 16      + 46      +2.00000
    r3_assert_pop   11       + 7       + 15      + 46      +1.00000
    r3_assert_head  11       + 9       + 13      + 46      −1.00000  (+2 per dropped push)
    r3_assert_tail  11       + 7       + 13      + 46      −1.00000  (and nothing per dropped push)
  ```

  The in-contract class runs from **+3.00000 down to −1.00000 per executed pop**
  on one line of source, and `r3_assert_tail` **dominates every other spelling
  found, on every regressor**.
* **R3-side span**, cheapest-found to dearest-found in contract:
  **−113 … +5110 on `small`** and **−202 … +17237 on `large`**. The dearest end
  is `safe_naive`, which is a *shipped rung* — p03's R2 and R3 differ by one
  reslice and are both in contract, so the span is genuinely the rung ladder and
  not a search artefact. Excluding R2, the span is **−113 … +593 / −202 …
  +1453**, width 706 / 1655.
* Write **"cheapest found"**, never "minimum" — and this subsection is the
  project's cleanest demonstration of why. Six p05/p16/p07/p11 minima had been
  published and every one was refuted by the next agent's first lever; p03's own
  has now been refuted **twice**, the second time after a review had confirmed it.
* ⚠ **Three in-contract spellings land on the same number because they land on
  the same MACHINE CODE** — `md5_fn a5a47dba3129`, identical, `n_fn 82`. That is
  worth stating precisely because `.memory/01-ladder.md` warns that *"reached by
  many spellings is not evidence of a floor"*: here it is not even three points,
  it is **one point written three ways**, and it is evidence of nothing at all
  about a floor. Two more pairs collide the same way: `r3_assert_head` is
  byte-identical to `m_clamp`, and `r3_assert_idx` reaches `m_mask`'s exact
  *numbers* from a different machine code.
* **The cheapest spelling IS the same on both blobs — but the ranking below it
  is not.** `r3_assert_tail` wins or ties both (it ties `r3_assert_head` on
  `small` only because `small` has **zero** dropped pushes, so the head
  placement's +2·dpush costs nothing there). Between the other two, `head` beats
  `pop` on `small` by 236 and `pop` beats `head` on `large` by 290 — the
  same input-dependent reordering p16's `chunks_exact(64)` and p11's
  `take_while` show, one level down. **A cheapest-found figure must name its
  input even when the winner does not change.**
* **Placement is the whole story, and it is worth 2 Ir twice**, read off the
  listing (`harness/asm.py show --raw`):
  * **back edge** (`r3_assert_tail`): every edge into the header phi is bounded
    without a fixed point — the entry value is `0` and the back edge is
    asserted — so LLVM deletes the pop's bounds check *and* the assertion, and
    the pop becomes `add -0x8(%rsp,%r15,8),%rsi ; dec %r15` with the address
    arithmetic folded into the addressing mode. The push guard keeps its
    `cmp $0x40,%r15 ; jae` spelling, exactly as in R3 and R4.
  * **head** (`r3_assert_head`, and `m_clamp`): same 13 per pop, but LLVM now
    knows `sp == STACK_CAP` on the dropped-push edge and materialises it —
    `cmp $0x40,%r15 ; jne ; mov $0x40,%r15d ; jmp` — which is the +2.00000 per
    dropped push, and 704 Ir/call on `large`.
  * **pop arm** (`r3_assert_pop`): the assertion does not dominate the back
    edge, the loop-carried range is never established, and the assertion
    **survives** as `cmp $0x41,%r15 ; jae <panic>` — 2 Ir on every POP
    *operation*. It still deletes the pop's own bounds check. (The 19-blob
    design has `epop = 0` throughout, so the fit attributes those 2 to `xpop`;
    on band C they would split. `small` and `large` both have `epop = 0`.)
  * **after the decrement** (`r3_assert_idx`): the assertion and the check are
    now the same comparison on the same value, LLVM keeps one of them, and the
    saving is 1.00000.
* ⚠ **`r3_assert_pop`'s `md5_fn` is the one digest in this table that moves with
  the SOURCE FILE'S NAME**, and it is worth a line because it is a small trap.
  It is the only row whose assertion survives into the binary, so its kernel
  carries a pc-relative reference to a panic `Location` — and the `Location`
  holds the *source path*, so building the identical bytes from a differently
  named scratch file shifts `.rodata` and with it the displacement:
  `md5_fn 26e8bbe931c3` from `.temp/p03/controls/r3_assert_pop.rs`,
  `18e28795e5fc` from a copy under another name, **same `n_fn 82`, same
  `md5_fn_norel e33533f83a4d`, same `md5_raw_norel aa78cd90afec`, same Ir**.
  Quote `*_norel` for this row, per `harness/asm.py`'s own rule. The other three
  assertion rows are byte-identical across both builds, which is independent
  corroboration that their assertions really are **gone**.
* The **out-of-contract** exclusions cut in both directions and one of them cuts
  against interest: `m_mask` is **cheaper** than the shipped R3 and forbidding it
  raises p03's published tax from 2.00000 to 3.00000 per pop, while
  `m_branchless` is **far dearer** and forbidding it lowers nothing. On p05 and
  p16 the excluded spellings were uniformly cheaper, which made the declaration
  look like it might be protecting a number; here it is not — and §4c gives the
  stronger form: the in-contract class reaches **13** per pop against `m_mask`'s
  16, so the exclusion is not even keeping the cheapest spelling out.
* ⚠ **One row's admission rests on the entry's English rather than on the
  ruler.** `r3_slicestack` renames the array (`let mut stack_arr: [u64;
  STACK_CAP] = [0; STACK_CAP];`) and therefore **misses** `required[2]`'s
  literal span under `check.spelling_matches`, while honouring what the entry
  says — "a fixed-size LOCAL array, never a growable one". That is exactly the
  case `.memory/01-ladder.md` records as *"`required` is NOT decidable — an
  entry's rung scope and polarity live in its English"*, and it is disclosed
  rather than counted silently. It sets no endpoint: it is byte-identical to the
  shipped R3. Every other `r3_*` above is **0 forbidden hits, 0 required misses**
  against the gate's own matcher (`.temp/p37/contract.py`, which calls
  `harness/check.py::spelling_matches`).

### 10b. The R4 side — the project's FIRST admissible R4 that MOVES

TASK_026 §0 item 3 and `.memory/01-ladder.md`: **a rung covered by an `identity`
pin is chained to the prover**, so an R4 candidate is not a rung until its R5
twin verifies. Every candidate has a twin in `controls/gen_controls.py` and
every twin was run **before any of its numbers was differenced**.

| spelling | small − R4 | large − R4 | Verus verdict |
|---|---:|---:|---|
| `r4_forloop` — `for k in 0..nops` | **0.00** | **0.00** | **`9 verified, 0 errors`** — admissible, does not move |
| `r4_slicestack` — the stack as `&mut [u64]` | **0.00** | **0.00** | **`9 verified, 0 errors`** — admissible, does not move |
| `m_clamp_unsafe` — R4 + a dead `if sp > STACK_CAP` at the **head** | **−118** | **+497** | **`9 verified, 0 errors`** — admissible, **and it MOVES** |
| `m_clamp_unsafe_tail` — the same test on the **back edge** | **−118** | **−207** | **`9 verified, 0 errors`** — admissible, moves further |
| `r4_ptr` — `as_ptr()` / `add()` | 0.00 | 0.00 | **DISQUALIFIED** — `does not yet support` |
| `r4_assert` — `assert!(sp <= STACK_CAP)` | — | — | **DISQUALIFIED** — `panic is not supported`; the safe class's own lever, unavailable here |

```
$ ./verus_run.py .temp/p03/controls/r4_forloop_twin.rs
verification results:: 9 verified, 0 errors

$ ./verus_run.py .temp/p03/controls/r4_slicestack_twin.rs
verification results:: 9 verified, 0 errors

$ ./verus_run.py .temp/p03/controls/m_clamp_unsafe_twin.rs
verification results:: 9 verified, 0 errors

$ ./verus_run.py .temp/p03/controls/m_clamp_unsafe_tail_twin.rs
verification results:: 9 verified, 0 errors

$ ./verus_run.py .temp/p03/controls/r4_ptr_twin.rs
error: The verifier does not yet support the following Rust feature: dereferencing
a raw pointer. Currently, Verus only supports raw pointers through the permissioned
raw_ptr interface

$ ./verus_run.py .temp/p03/controls/r4_assert_twin.rs
error: panic is not supported (if you used Rust's `assert!` macro, you may have
       meant to use Verus's `assert` function)
```

⚠ **So p03's pair interval is NOT degenerate, and this is the first pattern on
which it is not** (p05, p16, p07, p11 were all degenerate, and
`.memory/01-ladder.md` carried *"nobody has, on any pattern"* as a standing
statement). `m_clamp_unsafe` and `m_clamp_unsafe_tail` are R4 plus one
provably-dead `if sp > STACK_CAP { return 0; }`; both

* verify **`9 verified, 0 errors`** with **zero new trusted items** — the
  accessors, their `requires`, their `ensures` and the TCB tally are untouched,
  because `sp <= STACK_CAP` is already an invariant clause and the dead test
  needs no ghost support at all;
* hold the `identity` pin **byte-for-byte**: the `rustc` build and the
  `verus --compile` build of the tail variant agree on `md5_raw
  331b95aebf7743b42bb2114a8e733534` and `md5_fn c079bb40d06d832c964ebcffec35334c`,
  `n_fn 66` — the same instruction count as shipped R4;
* are in contract by the gate's own matcher (0 forbidden hits, 0 required
  misses), and out of it only by the **judgement** §4b states — dead code
  inserted to move a number. That judgement is why they are named `m_*`;
* and they **move**: −118 / +497 at the head, −118 / **−207** on the back edge,
  the same ±2·dpush placement effect §10a measures on the safe side.

**The measured asymmetry, on the same pattern.** `assert!` is the safe class's
cheapest lever (§10a) and Verus answers `panic is not supported` — which
`.memory/01-ladder.md`'s qualification 2 makes a disqualification at the pinned
vstd — so **the safe class reaches a spelling the unsafe class cannot**. That is
the third measured instance of R4-by-permission on this project and the first
where the safe-side lever is a one-line assertion. The unsafe side reaches the
same *per-operation rates* by a different route — the dead clamp gives
`11 xpush + 7 dpush + 13 xpop` on both sides, and the two differ only in the
per-call constant (46 against 41, the window-reslice check) — so what is
asymmetric here is the **permission**, not the reachable cost.

⚠ **What the two class minima are, and what they do NOT license.** Cheapest
in-contract R3 is 2889 / 8182 and cheapest admissible R4 is 2884 / 8177 — a
difference of **exactly 5 on both blobs**, i.e. the per-call constant, with
`0.00000` per executed pop. **Do not publish that as p03's safety tax.**
`.memory/01-ladder.md` is explicit: `min(R3) − min(R4)` is the difference of two
*upper* bounds and bounds nothing in either direction. The sound number remains
the fixed-R4 bound (§10a), and what the +5 says is only that the two searches
have so far converged on the same code up to the window-reslice check.

⚠ **`r4_slicestack` is NOT borrow-checker-blocked, and the earlier claim that it
was is WITHDRAWN** (TASK_036_REVIEW §3a). This file used to read the errors
below as a fact about Rust — *"the unsafe class is bounded by Rust's borrow
checker"* — and they were **two defects in `controls/gen_controls.py`**:

```
error[E0502]: cannot borrow `(Verus spec stack_arr)` as immutable because it is
              also borrowed as mutable                      # x2
error[E0596]: cannot borrow `stack` as mutable, as it is not declared as mutable
```

The `E0502`s came from a ghost invariant clause and a ghost `assert` **the
control itself added**, both reading `stack_arr` while it is mutably borrowed
and neither needed by the candidate; the `E0596` came from a generated
`let stack:` with no `mut`. With the ghost assert split across the borrow, the
unsizing coercion `&mut stack_arr` in place of `&mut stack_arr[..]`, and
`&mut *stack` / `&*stack` reborrows at the two call sites — **the same 1 + 3
TCB lines and the same `requires`, only the parameter types moving** — it
verifies `9 verified, 0 errors`, and its exec side is byte-identical to shipped
R4 (`md5_fn 52432361a348`, 3002 / 8384). The generator is repaired, so the
verdict above is re-derivable from the tree.

⚠ **And note how much smaller the excluded gap is here than on p11.** p11's
inadmissible `r4_cstr` was worth 17 526 Ir/call, 35% of the kernel. p03's two
*disqualified* candidates are worth **0.00** — each compiles to R4's own code or
to a permutation of it. What p03 adds is not a large excluded gap but a
**non-zero admissible one**: the R4 endpoint has measured width for the first
time on this project, 2884 … 3002 on `small` and 8177 … 8881 on `large`.

### 10c. The out-of-contract spellings, and what each buys

| control | what it deletes | small − R4 | large − R4 |
|---|---|---:|---:|
| `m_mask` | 1.00000 of the 3.00000 per-pop check | +241 | +419 |
| `m_clamp` | 4.00000 per pop, costs 2.00000 per dropped push | −113 | +502 |
| `m_clamp_unsafe` | 1.00000 per pop off **R4**, same 2.00000 per dropped push | −118 | +497 |
| `m_clamp_unsafe_tail` | 1.00000 per pop off **R4**, and nothing per dropped push | −118 | −207 |
| `m_uninit` | the `[0u64; 64]` fill and its `memset` | −17 (+ the memset) | −17 (+ the memset) |
| `m_branchless` | the two-way branch | +3559 | +13799 |

Only the first and the last are out of contract by `idiom.forbidden`;
`m_uninit` is (`MaybeUninit`) too. The three `m_clamp*` are out by the
**judgement** of §4b and not by the ruler, and §10b treats the unsafe pair as
admissible R4 candidates for exactly that reason — a ruler the gate can run
admits them, so the twin has to be run before their numbers are quoted.

## 11. Wall clock — the noise floor first, one null, and one direction reversal

`.memory/03-measurement.md`: run `common/layout/order.py` **before** believing
any `ns` number, and `layout_gen.py` if a mode shows. Both were run.
`taskset -c 3`, 31 reps, interleaved by cell.

### 11a. Identical-copy noise floor — and p03 IS protocol-sensitive

`python3 common/layout/order.py --pattern p03-bounded-stack --copies 31 --reps 31
--passes 2`, 31 **byte-identical** copies at the shipped layout, `small.bin`:

| pass | schedule | R2 floor | R3 floor | R4 floor | R2 − R4 | R3 − R4 |
|---|---|---:|---:|---:|---:|---:|
| 0 | `round_robin` (shipped) | 3.62% | 3.16% | 4.44% | +5.64% | −11.04% |
| 1 | alternating (`measure.py`) | 3.13% | 4.13% | 4.91% | +6.28% | −10.63% |
| 1 | **blocked (the bug)** | 2.87% | **12.02%** | **11.12%** | **+4.33%** | **−4.39%** |
| 1 | `round_robin` | 3.90% | 3.79% | 5.15% | +6.18% | −10.93% |

**p03 joins p05 as protocol-SENSITIVE**, and it is only the second pattern to.
Blocked scheduling moves `R3 − R4` from −10.6…−11.0% to −4.39% and inflates two
floors to 12%; the per-position dump shows why — under blocking `safe_tuned`
climbs monotonically 5.376 → 6.022 ms across its block and `unsafe` starts at
6.688 and settles, i.e. a warm-up ramp that alternation spreads across all
cells. `round_robin` (the shipped scheduler) agrees with `alt` to 0.1 points,
which is the check `order.py` exists for and it passes.

**The floor is 3.1–5.2% under the correct protocol**, which is why the next two
subsections are needed rather than optional.

### 11b. The single-layout `small` row is DISCARDED

`harness/measure.py`'s own 30-rep run, min→median spread:

| rung | small | large |
|---|---:|---:|
| c-gcc | 8.27% | 1.45% |
| c-gcc-h | 6.96% | 2.48% |
| c-clang | 7.04% | 1.84% |
| c-clang-h | 7.55% | 1.77% |
| safe_naive | 6.66% | 1.73% |
| **safe_tuned** | **11.23%** ⚠ | 1.65% |
| unsafe | 9.20% | 2.11% |
| verus | 9.33% | 2.07% |

**`safe_tuned` on `small` exceeds `.memory/03-measurement.md`'s 10% discard
threshold and three more cells are within one point of it, so the whole `small`
single-layout `ns` row is discarded rather than quoted.** That is the session
property TASK_035 measured — the same class of binaries read a 1.3% between-cell
band three days before that task and 8.2% during it — and p03 was built entirely
inside the noisy regime. `large` (1.45–2.48%) is inside the threshold and is
quoted.

`large`, min of 30, `-O3 isolated`, against R4:

| rung | ns (min) | vs R4 |
|---|---:|---:|
| c-gcc | 8.763 ms | −4.04% ⚠ |
| c-gcc-h | 8.666 ms | −5.09% ⚠ |
| c-clang | 8.534 ms | −6.55% ⚠ |
| c-clang-h | 8.789 ms | −3.75% ⚠ |
| **R2 safe-naive** | 10.080 ms | **+10.39%** |
| **R3 safe-tuned** | 8.981 ms | **−1.65%** |
| R4 unsafe | 9.132 ms | 0 |
| R5 verus | 9.078 ms | −0.59% ⚠ |

⚠ marks a cell with **no layout bracket**: `-align-all-functions` is an LLVM
knob so it reaches `c-clang` and not `c-gcc`, and a `c-gcc`-vs-`rustc`
comparison needs both endpoints bracketed by the same lever (p07's caveat,
unchanged). R5's ⚠ is different and weaker — the kernels are byte-identical, so
the −0.59% is the measurement's own noise.

### 11c. The layout population, mode-matched — and one direction reversal survives

`layout_gen.py --seeds 21 --aligns 9 --reps 31 --passes 2` (31 layouts per rung,
`md5_fn_norel` and `n_fn` invariant across all of them), then `analyze.py`.

**A mode exists and it belongs to R4.** `analyze.py` separates `unsafe`'s
population on `loop0 [+0x60,+0x78) 24B win32[1,2]` and `jcc32[0,1]` — the same
partition read two ways — at ×1.0664 / ×1.0646 on `small` and ×1.0238 / ×1.0196
on `large`. The 24-byte loop is the operation-dispatch head, and one extra
32-byte fetch window on it is worth 6.5% of R4's `small` time. R3's mode is
×1.0176 and R2's ×0.9774, i.e. much weaker. **The band on `small` is 26.36% for
R4 against a 4.4–5.2% identical-copy floor**, so this is a real mode and a
single-layout reading of `small` would have been indefensible even without the
discard.

Mode-matched (`addr%32`) medians, and pairwise `P(A > B)` over all 31² pairs:

| input | pass | rung | pooled | mode 0 | mode 16 | P(A>B) |
|---|---|---|---:|---:|---:|---:|
| small | 0 | R2 | +10.31% | +15.59% | +7.37% | 99.6% |
| small | 1 | R2 | +9.55% | +15.86% | +6.37% | 100.0% |
| small | 0 | **R3** | **−12.44%** | **−7.43%** | **−14.69%** | 19.1% |
| small | 1 | **R3** | **−12.80%** | **−8.76%** | **−14.73%** | 19.5% |
| large | 0 | R2 | +13.92% | +14.14% | +11.25% | 100.0% |
| large | 1 | R2 | +13.60% | +13.98% | +11.92% | 100.0% |
| large | 0 | **R3** | +0.46% | +0.90% | **−2.37%** | 49.8% |
| large | 1 | **R3** | +0.14% | +0.78% | **−1.52%** | 53.6% |

Three readings, in decreasing confidence:

**(1) R2 is slower than R4 in wall clock, everywhere.** Positive in both modes,
both passes, both inputs, `P(A>B)` 99.6–100%. +170%/+206% of instructions
converts to +6.4…+15.9% of time — a conversion factor of **10.7x on `small` and
17.3x on `large`**, i.e. the vast majority of R2's instruction gap is free. Same
shape as p16's (+72% `Ir` -> +0.27% ns), with a much larger residue.

**(2) On `large`, `R3 − R4` FLIPS SIGN between modes** (+0.90 / −2.37 and +0.78
/ −1.52), so `.memory/03-measurement.md` is explicit: **a sign that flips
between modes is not a sign**. `P(A>B)` is 49.8% and 53.6%, i.e. a coin flip.
The `large` R3-vs-R4 wall-clock comparison is a **null**, and the −1.65% in §11b
must not be quoted as an effect.

**(3) On `small`, R3 is FASTER than R4 in every mode and both passes — while
executing 11.96% MORE instructions.** −7.43 / −14.69 / −8.76 / −14.73%, no sign
flip, and `P(A>B)` 19.1%/19.5% (so R3 wins ~81% of layout pairs, not all of
them). **That is an `Ir`-versus-`ns` direction reversal**, and it is p03's
contribution to findings 5/6. The mechanism is visible in the population itself
and is *not* a mystery: R4 is the rung with the mode (×1.066), R3's is ×1.018,
so R4's dispatch loop is the front-end-bound one, and R3's three extra
instructions per pop sit on a path that is not the limiter. The honest statement
is therefore:

> **p03's R3 executes 3.00000 more instructions per executed pop than R4 and is
> 7–15% faster on `small` at matched layout mode. The instruction gap is real
> and exact; the time gap is real and has a range, not a value; and the
> direction is opposite.**

⚠ **The caveat that must travel with it — and it is about the MAGNITUDE, not
the sign.** The effect is 1.5–3× the identical-copy floor and this box is in its
noisy regime (§11b), so the *magnitude* should be read as "7 to 15 percent",
never as a point.

**The DIRECTION is resolved, and an earlier draft hedged it too hard**
(TASK_036_REVIEW's noise-floor rerun). There are now **seven independent
correct-protocol readings across two sessions**, all negative and spread 0.4
points: §11a's three (`round_robin` and `alternating`, −10.63…−11.04%) plus four
more the next day (`alt` and `gen` orders, two passes: −10.70, −10.72, −10.77,
−10.86%), against an identical-copy floor of **3.4–6.5%** in the same runs. The
only readings that do not show it are the **blocked** schedule, which §11a
already identifies as the protocol bug — it inflates two floors to 10–13% and
pulls `R3 − R4` to −3.7…−4.4%, still negative. "A sign that flips between modes
is not a sign" (`.memory/03-measurement.md`) applies to `large`, where it does
flip (§11c reading 2); on `small` nothing flips.

### 11d. What is NOT here

- **No cycles/byte and no cycles/op.** `.memory/00-environment.md`: ns is a
  measurement on this box, cycles is an inference spanning ±15% within one
  session, and the clock was not measured interleaved with these reps.
- **No wall-clock number for the branch pair.** §4d's blobs are 9632 bytes and
  L1-resident, and `Bcm` is *simulated*. Converting 0.5 mispredicts/op into
  time would need either a hardware counter this box does not have or a much
  larger working set, and inventing one would be exactly the estimate
  `.memory/03-measurement.md` forbids.
- **No C layout bracket** — the lever is LLVM-side and cannot reach `c-gcc`.
- **`O0` rows are built and gate-checked but no number here comes from one.**

## 12. What p03 answers that no earlier pattern could

### 12a. Does the safety cost amortise?

p07's answer was *"no axis along which it amortises"*; p11's was *"it crosses
zero"*; p16's and p17's was *"to zero, per byte"*; p05's was *"O(nrow), vanishes
along ncol"*. **p03's is a fourth answer: it amortises along one axis of the
input and not the other, and the attacker picks which.** `R3 − R4` is
`3.00000·xpop + 5`, so

* along `nops` at fixed density it is **linear, share constant** — at 50%
  density half the operations are executed pops, so the tax is 1.5 Ir on an
  operation that costs R4 `(11 + 14)/2 = 12.5`, i.e. **12.0% of the call**
  (measured: +11.96% on `small`), or **3 of 14 = 21.4% of an executed pop**;
* along **pop density** at fixed `nops` it goes from 5 Ir/call (all pushes) to
  `3·nops/2 + 5` (balanced) and back down to 5 (all pops, none executing);
* the maximiser is 50% density, which is also the only density at which every
  operation executes. **The worst case for safe Rust is the well-formed input.**

⚠ **That is the SHIPPED PAIR's answer.** For the in-contract class the question
does not arise in the same form: `r3_assert_tail` is `−1.00000·xpop + 5` against
`R4ship` (§10a), so the *in-contract* cost does not amortise — it is negative on
both blobs and gets more negative as pops get more frequent. The amortisation
result above is about `R3ship` and should always be quoted with the rung named.

### 12b. Is the obligation the same one the optimiser fails?

Yes, and both halves are measured rather than argued: §6c shows the invariant is
what `stack_get_unchecked`'s precondition needs, and §4b shows that handing LLVM
the same invariant as dead code takes the gap to zero. p05 could claim the first
half and had to argue the second; p03 has both, on a **linear** fact — and on a
fact **two independent middle-ends** fail identically (§4b qualification 1), so
the answer is about optimisers and not about a language.

### 12c. What the second buffer costs the trusted base

p01, p02, p05, p07, p11, p16 and p17 each ship **one** trusted `unsafe`
accessor. p03 ships **three**, because the kernel has two buffers and writes one
of them, and §5b tallies **10** TCB lines across 5 `external_body` items
(`1 + 1 + 3 + 4 + 1`, and the gate's record says 10 too) against p11's 6 across
3. **That is a real cost of the pattern and not of the
implementation** — any kernel with a second mutable buffer pays it — and it is
the first data point this project has on how the TCB scales with the number of
buffers rather than with the number of rungs.

## 13. The declaration, and when it was written

`spec.md`'s `idiom` block was written **after** the phase-0 probe of §0 and
**before** any rung, any input file or any `model.py` existed. That is weaker
than p11's claim (written before any cell was measured) and the `idiom.why`
says so in the hashed text rather than in a footnote: what was known when it was
written is the whole of §0 — the underflow's address arithmetic, that
`STACK_CAP = 64` keeps the array real, that a 5-byte operation dominates the
per-call constant, and probe figures for six candidate spellings including
3.00000 Ir per executed pop. What was **not** known is any figure in §3, §4, §10
or §11. TASK_036 required that probe before five rungs were built on the sizes,
so the ordering is a consequence of the task and not a choice.

`.memory/01-ladder.md`'s direction test is what a reviewer should apply, and §10a
records the two exclusions that move p03's published figure: `m_mask` would
lower it from 3.00000 to 2.00000 per pop and is forbidden (**against interest**),
`m_branchless` would raise it and is forbidden (no interest either way). Since
TASK_037 there is a third thing to say and it is the strongest of the three:
**the declaration is not what holds p03's figure up at all.** An in-contract
spelling reaches −1.00000 per pop (§10a), below both forbidden alternatives, so
no exclusion here is protecting a number — what keeps the published 3.00000 in
place is the *choice of shipped spelling*, which is a separate decision and is
the one this file now states explicitly.

### 13a. The shared paragraph is byte-identical

The `NAMED-SPELLING STANDARD` paragraph in `idiom.why` is **11 004 characters**,
identical to the other eight patterns' — it was read out of p11's own hashed
block by `.temp/p03/make_spec.py` rather than retyped, and
`.temp/p03/make_spec.py --check` re-derives `spec.md` and diffs it. p03 is the
second pattern (after p11) whose `spec.md` has a build script, and that script
lives under `.temp/`; the committed `spec.md` is self-contained and the
byte-identity is re-checkable from the tree alone.

### 13b. The stage-0b audit

```
audit  31 backticked spelling(s) over 6 rung(s) -> 94 (spelling, rung) pair(s), 63 present
audit  forbidden: 10 spelling(s), 0 hit(s)   (decidable)
audit  required : 0 pin nothing, 1 scoped-absent pair(s)
```

`pins_nothing = 0` is the signal that matters (`.memory/01-ladder.md`: an entry
matching *no* rung of a language it declares is a bug in the **ruler**). A first
draft scored **1 pin-nothing and 10 scoped-absent**, because two `required`
entries backticked spans quoted *in order to be absent* — `stack[sp - 1]` and
`Vec` — which is the polarity case `.memory` names and which the audit cannot
distinguish from a defect. Both were de-backticked before shipping; that is a
repair to the **ruler** and not to the code, and it lowers no published number.

**After the repair there is exactly ONE scoped-absent pair in the whole pattern,
and it IS the bug**: `required[1]`'s `if (sp > 0) {`, absent from `c/kernel.c`
and present in `c/kernel_hardened.c`. `.memory/01-ladder.md` records 41
scoped-absent misses over 158 obligations on the other patterns, all
non-defects; p03's is 1 of 94, and it is the one the declaration exists to
report.
