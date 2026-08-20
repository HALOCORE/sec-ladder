# p04 — findings

Written by the engineer who measured them (TASK_042). Every number here is
either pasted from a command's output or derived from a disassembly listing; a
five-decimal rate in this file always comes from the listing and never from a
two-point marginal (`.memory/03-measurement.md`, TASK_026 §0 item 2). Where a
rate is quoted, **the spelling that produced it is named beside it**; where two
rates are differenced, they are at **matched spelling**.

**Which `Ir` convention: the kernel-exclusive column**, p03's, for p03's reason —
p04's Rust rungs call `memset` for `[0u64; RING_CAP]` and its path length moves
with the stack array's alignment, so the whole-program marginal carries an
alignment term the kernel column does not. §3b measures it here rather than
inheriting it.

## 0. What was checked before five rungs were built on it

TASK_042 named two things it was least sure of and asked for both to be settled
first. Both were, with `.temp/p04/probe0/` (codegen) and `.temp/p04/probe1/`
(Verus), before any rung, input file or `model.py` existed. **Both came back
against the task file**, and one of them changes what the pattern demonstrates.

### 0a. "Does the bound survive `%`?" — YES at a power of two, and the safe and unsafe accesses are BYTE-IDENTICAL

p05 asked this of a **multiply**, p09 of a **shift**. `.temp/p04/probe0/gen_probe.py`
builds the same standalone kernel with the ring access spelled two ways and the
opcode stream held fixed, `rustc -C opt-level=3 -C debug-assertions=off
-C codegen-units=1`, and decodes the surviving panic pads with
`patterns/p12-strcat-fixed/controls/pads.py`:

| variant | opcode stream | ring access | CAP | `n_fn` | `md5_fn_norel` | pads |
|---|---|---|---:|---:|---|---:|
| `r3_64` | reslice | **safe `ring[tail]`** | 64 | 86 | `d0f2150795bb` | 1 |
| `r3_64_ur` | reslice | `get_unchecked` | 64 | 86 | `d0f2150795bb` | 1 |
| `r4_64` | `get_unchecked` | `get_unchecked` | 64 | 78 | `5d348507c3de` | 0 |
| `r3_60` | reslice | **safe** | 60 | 105 | `1f8184194daf` | **3** |
| `r3_60_ur` | reslice | `get_unchecked` | 60 | 93 | `11ffca224bf2` | 1 |
| `r4_60` | `get_unchecked` | `get_unchecked` | 60 | 85 | `04cc865e84d5` | 0 |

**`r3_64` and `r3_64_ur` are byte-identical.** One indexes the ring and one does
not, and they are the same 86 instructions. So at `RING_CAP = 64` the ring's
bounds check costs **exactly zero**, and the three pads that appear at 60 decode
to `ring[tail] = val` and `ring[head]`. `safe64m` — the same source with
`& (RING_CAP - 1)` in place of `%` — is byte-identical to `safe64` too.

**The mechanism, off the listing.** At 64 the update is
`inc %r14d ; and $0x3f,%r14d`: a mask fixes the high bits, and *known bits*
propagate through the loop-carried phi. At 60 the fact is a *range* (`[0,59]`)
and the range does not survive the phi. Stated as a rule, and it is the thing
the three-operator series was built to find:

> **What LLVM carries around a loop-carried phi is known BITS, not a range.**
> p05's multiply and p09's `q >> 6` both fix bits; p09's failing case is the
> *composition* through a multiply, which fixes none.

A second asymmetry at 60, in **both** the safe and the unsafe rung: the pop's
`(head + 1) % 60` is strength-reduced to `inc ; cmp $0x3c ; mov $0 ; cmovne`,
while the push's `(tail + 1) % 60` is a full magic-number division
(`mul ; shr ; imul $0x3c ; sub`). `%` by a non-power-of-two is not one cost.

### 0b. p03's `m_clamp` seeding control transplants — and only at 60

Dead test `if tail >= RING_CAP || head >= RING_CAP { return 0; }`:

| placement | CAP | `n_fn` | pads |
|---|---:|---:|---:|
| before the loop | 60 | 105 (byte-identical to `r3_60`) | 3 |
| top of the **loop body** | 60 | **90** | **1** |
| the loop's **back edge** | 60 | 93 | **1** |
| top of the loop body | 64 | 86 (byte-identical to `r3_64`) | 1 |
| top of the loop body, on R4 | 60 | 82 (against `r4_60`'s 85) | 0 |

So p03's control deletes 100% of the CAP=60 ring check, and at CAP=64 there is
nothing left for it to delete. Placed *before* the loop it is a no-op —
`head == tail == 0` there, so it seeds nothing — which is the p03 placement
lesson reproduced on a second pattern. Note the head placement at 90 is
**cheaper than `r3_60_ur` at 93**: seeding the range also lets LLVM
strength-reduce the push's magic division, so the clamp buys more than the check
it deletes.

### 0c. "Is the wrap bug invisible to a memory-safety proof?" — YES, against five positive controls

`.temp/p04/probe1/ring.rs` is a standalone Verus kernel (no driver, no
`common/`); `.temp/p04/probe1/probe.py` generates every mutant from it by
exact-string substitution with an asserted hit count. The probe verifies
**`5 verified, 0 errors` first try**.

```
control                verification results:: 5 verified, 0 error
control_msonly         verification results:: 5 verified, 0 error
nofull                 verification results:: 4 verified, 1 error invariant not satisfied at end of loop body
nofull_msonly          verification results:: 5 verified, 0 error
noempty                verification results:: 4 verified, 1 error invariant not satisfied at end of loop body
noempty_msonly         verification results:: 5 verified, 0 error
nomod_msonly           verification results:: 4 verified, 1 error invariant not satisfied at end of loop body
offby1_msonly          verification results:: 4 verified, 1 error precondition not satisfied
false_a_msonly         verification results:: 4 verified, 1 error assertion failed
false_b_msonly         verification results:: 4 verified, 1 error assertion failed
false_c_msonly         verification results:: 4 verified, 1 error assertion failed
```

`--multiple-errors 20` on `nofull_msonly` and `noempty_msonly`: still 5/0, so
nothing is hidden behind a first failure (`.memory/04-verus.md` 2b). §6 repeats
all of this on the *shipped* `verus.rs`, which is what the numbers in this file
are quoted from; this subsection is the phase-0 record.

**Two answers, both against the task file.**

1. The bug is invisible to memory safety, and the functional `ensures` is what
   catches it. `_msonly` is not blind: it fails on `assert(false)` in three
   places, on `ring[tail + 1]`, and on the same guard-free push with the `%`
   deleted.
2. **The R5 invariant is not the work, and it is not relational.** TASK_042
   predicted *"`head < CAP && tail < CAP` plus whatever relates them"*. Nothing
   relates them. The memory-safety half is two **independent** one-variable
   clauses, each maintained by its own `% RING_CAP` and by no guard at all.
   **That is not a coincidence, it is the same fact as (1)**: the relation
   between the cursors is exactly the part of the state the memory-safety
   obligation does not need, which is why deleting either guard is invisible to
   it. §5 states it as the pattern's mechanism.

### 0d. Does folding both cursors make the bug visible without breaking the perf rows? YES

The p12 interaction, checked in the direction p12 learned it the hard way in,
before the rungs existed (`model.py`'s `r1_result` against its `ring_fold`):

```
small                      nwin=   12 windows_checked=12 R1_diverges_on=0
large                      nwin= 2000 windows_checked=2000 R1_diverges_on=0
adversarial-overwrite: win0 checked=2153 R1=448
adversarial-overwrite      nwin=    1 windows_checked=1 R1_diverges_on=1
adversarial-wrap           nwin=    1 windows_checked=1 R1_diverges_on=0
adversarial-count          nwin=    1 windows_checked=1 R1_diverges_on=0
```

`((acc*31 + head)*31 + tail)*31 + nops`: on the adversarial window the checked
rungs end at `head = 0, tail = 63` and R1 at `head = 0, tail = 8`, because R1's
200 unguarded pushes advance `tail` 200 times and `200 % 64 == 8`. So the fold
separates them **on the bug and on nothing else**, and `small`/`large` keep
their eight-way checksum agreement. That is what makes
`adversarial-overwrite.bin` a checksum row rather than a sanitiser row.

## 1. Where the bound falls — `%` is the third operator, and it carries

`harness/asm.py`, `-O3 isolated`, kernel symbol only; pads decoded with
`patterns/p12-strcat-fixed/controls/pads.py`, never counted
(`.memory/03-measurement.md`: *always decode before attributing*).

| cell | `n_fn` / nopad | loops | `vector_regs` | `bulk_calls` | pads |
|---|---|---:|---|---|---:|
| `c-gcc` (R1) | 83 / 81 | 4 | `[]` | `[]` | n/a |
| `c-gcc-h` (R1h) | 87 / 85 | 4 | `[]` | `[]` | n/a |
| `c-clang` (R1) | 56 / 54 | 3 | `[]` | `[]` | n/a |
| `c-clang-h` (R1h) | 59 / 57 | 4 | `[]` | `[]` | n/a |
| `safe_naive` (R2) | 132 / 131 | 4 | `[]` | `memset` | **9** |
| `safe_tuned` (R3) | 84 / 82 | 4 | `[]` | `memset` | **1** |
| `unsafe` / `verus` | 74 / 72 | 4 | `[]` | `memset` | **0** |

`vector_regs` is empty in 8 of 8 kernels: no rung reaches SIMD, and nothing
here could — the loop is a data-dependent two-way branch followed by a serial
dependence through `head`, `tail` and `acc`.

**R3's single surviving pad is the window reslice, and there is no ring pad in
any rung.** Decoded with `--source`:

```
safe_tuned-O3-isolated         pads=1  51:24
    51:24  let w: &[u8] = &buf[off..off + len];
                              ^
```

R2's nine are the nine `buf[...]` reads of the header and the operation record;
`ring[tail]` and `ring[head]` contribute **zero pads in every rung**. So:

> **The bound survives `%`.** `tail = (tail + 1) % RING_CAP` at a power-of-two
> `RING_CAP` lowers to `inc %r14d ; and $0x3f,%r14d`, the mask fixes the high
> bits, and LLVM's known-bits analysis carries `tail < 64` around the
> loop-carried phi with no help at all. The safe indexed access and
> `get_unchecked` compile to the same bytes (§0a: `md5_fn_norel d0f2150795bb`,
> `n_fn 86`, both).

**Placed in the series this project built without meaning to:**

| pattern | operator | does the bound survive? |
|---|---|---|
| p05 | **multiply** `i*ncol + j` | no — the implication is nonlinear, and the check is `O(nrow)` |
| p09 | **shift** `q >> 6` | yes on the shift alone; **no through the composition with a multiply** (`4 * (q >> 6)`) |
| **p04** | **modulus `% CAP`** | **yes, completely — at a power of two** |

and the unifying statement, which is new and is what the third data point buys:

> **What LLVM carries around a loop-carried phi is known BITS, not a range.**
> `% 64` fixes six low bits and nothing else, and that is enough. `% 60` fixes
> *no* bits — its fact is the range `[0, 59]` — and §1a measures that the range
> does not survive the phi. p09's failing case is the composition through a
> multiply, which likewise fixes no bits.

### 1a. The non-power-of-two lever — the largest single effect in this pattern

`controls/gen_controls.py` builds the identical sources at `RING_CAP = 60`.
**`small`'s execution counts are unchanged by the edit** — 119 accepted pushes,
118 executed pops, zero rejections, zero empty pops at 60 as at 64, checked by
replaying `model.py`'s driver loop with a 60-slot ring — so `small` is a
matched-count comparison and the only thing that moves is the operator's
lowering. (`large` is *not*: at 60 it rejects 2.27 pushes per call, which is why
its Ir/call stops being an integer. Every CAP=60 figure below is `small`.)

| cell | `n_fn` | pads | Ir/call `small` | `md5_fn_norel` |
|---|---:|---:|---:|---|
| `safe_naive` @64 (shipped R2) | 132 | 9 | 8119 | `805c3851ce68` |
| `cap60_r2` | 155 | **11** | 9423 | `4b2e9f995fb3` |
| `safe_tuned` @64 (shipped R3) | 84 | 1 | 3368 | `b5040cb5d805` |
| `cap60_r3` | 103 | **3** | 4673 | `229f09d4c466` |
| `unsafe` @64 (shipped R4) | 74 | 0 | 3363 | `931607a74611` |
| `cap60_r4` | 81 | 0 | 4194 | `b1c5281df02d` |
| `cap60_r3_clamp` | 88 | **1** | 4315 | `2011cec1dcbc` |
| `cap60_r4_clamp` | 78 | 0 | 4310 | `bcd3a49822e2` |

⚠ **The CAP=60 cells are a DIFFERENT PROGRAM and do not agree on checksum with
the shipped rungs** — a 60-slot ring rejects pushes the 64-slot one accepts, so
`.temp/p04/run_controls.py` reports all four as failing the `model.py`
equivalence check, correctly. Every CAP=60 figure below is therefore either a
comparison *among the CAP=60 cells* or a cross-capacity comparison **at matched
execution counts on `small`**, which is what the count check above licenses and
is why `small` is the only blob used.

Two extra pads at 60, decoded to `ring[tail] = val` (line 72) and `ring[head]`
(line 77) — **both ring accesses**. And:

```
R3 - R4  at RING_CAP = 64 :    +5      (per operation: 0.00000)
R3 - R4  at RING_CAP = 60 :  +479      (per RING ACCESS: 2.00000)
```

**479 − 5 = 474 = 2.00000 × 237**, and 237 is exactly the number of ring
accesses per call (119 writes + 118 reads). The 2 is off the listing, not
fitted: each guarded access is `cmp $0x3c,%r?? ; ja <panic>`. So

> **the ring's bounds check costs `0.00000` Ir per access at `RING_CAP = 64` and
> `2.00000` at `RING_CAP = 60`** — a 96× move in the pattern's whole safety
> tax (+5 → +479 per call) produced by one edit to one constant.

**The modulus itself is the other half, and it is not one cost.** `cap60_r4 −
unsafe = +831` Ir/call on `small` with the counts held fixed. Off the listing
that splits **+4 per push** — `(tail+1) % 60` is a full magic-number division,
`lea ; mov ; mul ; shr ; imul $0x3c ; sub`, against `lea ; and` — and **+3 per
pop**, where LLVM *does* strength-reduce to `mov ; inc ; cmp $0x3c ; mov $0 ;
cmovne` against `inc ; and`. `4·119 + 3·118 = 830` of the measured 831, the
remaining 1 being a per-call term. The asymmetry is present in the safe rung
too, and it is worth naming: **a non-power-of-two `%` is a division on one
cursor and a compare-and-select on the other, in the same loop.**

### 1b. p03's `m_clamp` seeding control transplants — and only where there is something to seed

The dead test `if tail >= RING_CAP || head >= RING_CAP { return 0; }`, at the
top of the loop body (p03 measured that the placement is what decides; §0b
reproduces that — placed *before* the loop, where both cursors are 0, it seeds
nothing and is byte-identical to the unclamped build).

```
RING_CAP = 60:   cap60_r3        4673   3 pads
                 cap60_r3_clamp  4315   1 pad     -358, the ring checks GONE
                 cap60_r4        4194   0 pads
                 cap60_r4_clamp  4310   0 pads    +116, the dead test's own cost
                 cap60_r3_clamp - cap60_r4_clamp = +5.00   <-- the CAP=64 gap
RING_CAP = 64:   cap64_r3_clamp is BYTE-IDENTICAL to shipped R3
                 (md5_fn_norel b5040cb5d805, n_fn 84, 3368 / 11667)
```

**Handed the invariant, the CAP=60 safe-versus-unsafe gap collapses from +479 to
+5.00 — exactly the CAP=64 figure, with zero fitted parameters.** That is p03's
result reproduced on a second pattern and on a *modular* index; and at
`RING_CAP = 64` the same control is a byte-identical no-op, because there is
nothing left to seed. p09 measured that p03's clamp does **not** transplant to a
shift-derived word index; p04 measures that it does transplant to a
non-power-of-two modulus. **The discriminator is whether LLVM is missing the
fact at all, not what the operator is.**

### 1c. It is not a fact about Rust — and here BOTH directions are measured in C

p03's qualification 1 says to write *"any compiler asked to prove this"*, never
*"safe Rust"*. `controls/gen_controls.py` builds the C rung with the bounds
check a careful C programmer writes on the ring read
(`if (head >= RING_CAP) __builtin_trap();`, inside the emptiness guard):

```
              RING_CAP = 64                    RING_CAP = 60
  gcc    c-gcc-h        4318            c_cap60-gcc         6216
         c_ringcheck    4318   +0.00    c_ringcheck60-gcc   6933   +717
         md5_fn_norel 38a0f7d88163, IDENTICAL to c-gcc-h
  clang  c-clang-h      3230            c_cap60-clang       4301
         c_ringcheck    3230   +0.00    c_ringcheck60-clang 4419   +118
         md5_fn_norel adf2ea8231fe, IDENTICAL to c-clang-h
```

At a power-of-two capacity **both compilers delete the manual check outright,
byte-for-byte**; at 60 **both keep it** — clang at exactly `1.00000` Ir per
executed pop (118 over 118 pops), gcc at 717 Ir/call, which is not a clean
per-pop rate and is not attributed further here. gcc shares no middle-end with
rustc, so this is three independent middle-ends agreeing in both directions. It
is the strongest form p03's sentence has been given: **the fact is carried by
the operator, not by the language, and no compiler needs to be taught it while
the capacity is a power of two.**

### 1d. The dispatch stays a real branch in all eight cells

`n_backward_branches` 3–4 and **zero** `cmov`/`set*` on the op dispatch in every
shipped cell. `spec.md` pins `if op == 0` because `.memory/01-ladder.md` records
LLVM's `X86CmovConverterPass` moving p07 in the *opposite* direction; checked
here rather than assumed.

## 2. Where the instructions go — and gcc does not fold the little-endian decode

Read off the shipped listings, `-O3 isolated`. Same finding as p03, reproduced:

| what | c-clang | c-gcc | rustc (R4) |
|---|---|---|---|
| the `val` u32 decode, written out as `b0 + 256*b1 + 65536*b2 + 16777216*b3` | **one** unaligned `mov` | **ten**: 4×`movzbl`, 3×`shl`, 3×`add` | **one** unaligned `mov` |
| the ring slot | `(%rsp,%r??,8)` | `(%rsp,%r??,8)` | `(%rsp,%r??,8)` |

§4's swept laws price it exactly: `c-gcc = 18·xpush + …` against
`c-clang = 9·xpush + …`, i.e. **`c-gcc − c-clang = 9.00000 Ir per accepted push,
exactly, over 99 blobs** — the nine extra decode instructions, on the arm where
the value load lives. (p03 measured 8.00000 on the same source shape; the
difference is p04's extra cursor arithmetic.) It is neither a flag default nor a
fortify artefact but a missing load-widening in gcc's own middle end on
identical source.

Nothing in this pattern calls a library routine except the Rust rungs' `memset`
for `[0u64; RING_CAP]` (§3c), so p11's library-versus-safety decomposition has
no analogue here and the C-vs-Rust comparison is a plain codegen one.

## 3. Performance — the column, the memset, and the two inputs

`-O3 isolated`, `panic=unwind`, **kernel-exclusive** Ir per call (§3b says why).
`small` is 237 operations per call (119 accepted pushes, 118 executed pops, no
rejections, no empty pops, mean ring occupancy 9.0% of the 63 usable slots);
`large` is 830 (417 / 413, occupancy **76.9%** — 8.5× `small`'s fill ratio and
still four slots short of rejecting a push).

| rung | `n_fn`/nopad | Ir small | Ir large | vs R4 small | vs R4 large |
|---|---|---:|---:|---:|---:|
| R1 c-gcc | 83/81 | 3842 | 13336 | +14.24% | +14.35% |
| R1h c-gcc-h | 87/85 | 4318 | 15004 | +28.40% | +28.66% |
| R1 c-clang | 56/54 | 2872 | 9979 | −14.60% | −14.42% |
| R1h c-clang-h | 59/57 | 3230 | 11234 | −3.95% | −3.67% |
| **R2 safe-naive** | 132/131 | **8119** | **28278** | **+141.42%** | **+142.48%** |
| **R3 safe-tuned** | 84/82 | **3368** | **11667** | **+0.149%** | **+0.043%** |
| **R4 unsafe** | 74/72 | **3363** | **11662** | 0 | 0 |
| **R5 verus** | 74/72 | **3363** | **11662** | **0.00%** | **0.00%** |

**R5 − R4 = 0.00 on both inputs**, and the kernels are byte-identical
(`md5_fn c0573f691c95`, `md5_raw 1be5994704b2`, 74 instructions and 15 B of
padding each), so finding 1 holds on a kernel with two live cursors, a modular
index and three trusted accessors.

### 3b. Which `Ir` column, and why it is p03's answer and not p11's

p04's Rust rungs call exactly one library routine — glibc `memset`, for
`[0u64; RING_CAP]` — and its path length depends on the stack array's
alignment, which moves with the build path. So the whole-program marginal
carries an alignment term the kernel column does not, exactly as on p03, and
**every rate in §1, §4 and §10 is kernel-exclusive**. The gate's own
whole-program marginals are in `results/gate/p04-ring-buffer.json` beside them.
(The discriminator is p03's: not *"does the kernel call out"* but *"does the
callee have a data-dependent path length"*.)

### 3c. What safe Rust's uninitialised array costs

All four Rust rungs write `[0u64; RING_CAP]` and C's `uint64_t ring[64];` is not
initialised. That is a **language** difference, not a bounds check, and
`spec.md` forbids `MaybeUninit` so that it cannot be deleted on the unsafe side
alone. It is a `memset` of 512 bytes per call, it lives **outside** the kernel
symbol, and it is therefore **excluded from every kernel-exclusive figure in
this file, including the C-vs-Rust rows in §3**. A reader who wants the
C-vs-Rust gap *with* it has to add it back; p03 §3c prices the identical
construct at ~60 Ir/call, and p04 ships no separate `m_uninit` control because
the fill is character-for-character p03's.

## 4. The swept laws — seven exact integer cost models, zero residual

`inputs/gen.py --sweep` emits four bands (99 blobs, all skipped by the gate and
by `measure.py` on the `sweep-` prefix):

* **band N** `sweep-n008 … sweep-n071` — 64 consecutive operation counts,
  balanced, every operation executing, low occupancy;
* **band D** `sweep-d096 … sweep-d120` — 9 push:pop ratios at a fixed 240
  operations, every operation still executing. Band N moves the count and holds
  the ratio, so it cannot separate `xpush` from `xpop`;
* **band F** `sweep-f000 … sweep-f120` — 13 **fill ratios**: 63 pushes fill the
  ring, `q` more are REJECTED, then POP/PUSH alternation at the cap. This is the
  only band on which the fullness check ever fires;
* **band E** `sweep-e000 … sweep-e120` — 13 counts of POPs against an **empty**
  ring. This is what makes `epop` identifiable at all: every other band and both
  matrix inputs have `epop == 0`.

The fitter **ships**, in `controls/sweepfit.py`, so these laws are re-derivable
from the committed tree rather than from gitignored scratch — the open
reproduction gap `.memory/01-ladder.md` records against p16's twelve probes.

⚠ **The rank, because a rank-deficient least squares returns garbage at zero
residual** (`controls/sweepfit.py`, exact rational rank over the four
regressors plus the intercept):

```
band N: 64 blob(s), rank 3/5      bands ('N','D'): 3/5    bands ('D','F'): 3/5
band D:  9 blob(s), rank 2/5      bands ('N','F'): 4/5    bands ('D','E'): 4/5
band F: 13 blob(s), rank 2/5      bands ('N','E'): 4/5    bands ('F','E'): 4/5
band E: 13 blob(s), rank 2/5
POOLED (all four):  rank 5/5
```

**No single band and no PAIR of bands identifies these terms; only the pooled
four-band design does.** p03 measured the same thing with three bands, and this
is the second pattern where the pooling is load-bearing rather than decorative.
TASK_042's input table named `sweep-n*` and `sweep-f*` only; those two are
rank 4/5 together and the fit is not identified from them — bands D and E are
why there is a law here at all, and that is the contradiction this section
reports.

```
kernel-exclusive Ir per call, -O3 isolated       MAX RESIDUAL 0.0000, 99 blobs

  c-gcc      (R1)  = 18·xpush + 18·dpush + 14·xpop +  7·epop + 48
  c-gcc-h    (R1h) = 22·xpush + 10·dpush + 14·xpop +  7·epop + 48
  c-clang    (R1)  =  9·xpush +  9·dpush + 15·xpop +  9·epop + 31
  c-clang-h  (R1h) = 13·xpush +  9·dpush + 14·xpop +  9·epop + 31
  safe_naive (R2)  = 33·xpush + 29·dpush + 35·xpop + 28·epop + 62
  safe_tuned (R3)  = 13·xpush +  9·dpush + 15·xpop +  8·epop + 51
  unsafe     (R4)  = 13·xpush +  9·dpush + 15·xpop +  8·epop + 46
```

**Out of sample**: no band goes past 240 operations, and `large` is 830 — 3.5×
outside every band. The laws reproduce it to the instruction:
`13·417 + 15·413 + 46 = 11662` against a measured 11662, and all seven rows
land exactly on both shipped inputs.

**Reproduced across two independent measurement sessions.** The whole 99-blob ×
7-cell matrix was measured twice, hours apart, on a rebuilt binary set: every
coefficient, every rank and every `max|resid| 0.0000` above is **bit-identical**
between the two runs, as is every row of §10's control table. That is the
deterministic-column claim `.memory/03-measurement.md` makes, exercised rather
than assumed.

⚠ **The `verus` row is not fitted and is not claimed.** `.temp/p04/kir.json` has
no `verus` column: R5 is byte-identical to R4 at `-O3` (§8), so it is *entitled*
to the same law — but that is an inference from the identity pin, not a sweep,
and p03's `NOTES.md` was corrected for exactly this mislabelling.

⚠ **The two R1 cells are fitted over all 99 blobs including band F, and that
needs its own justification, which p03's did not have.** On band F an R1 cell
does not run the model's program — it has no fullness test, so what the model
counts as `dpush` it *accepts*. It is legitimate here for a measured reason:
R1's own execution counts satisfy `pushes = xpush + dpush`, `xpop = xpop`,
`epop = epop` on **all 104 band-F windows** (checked by simulating R1's cursors
directly), because R1's collapse never brings `head` onto `tail` again in this
band. And the fit says so by itself: **R1's coefficients on `xpush` and `dpush`
are EQUAL** — 18/18 for gcc, 9/9 for clang — while R1h's are 22/10 and 13/9.
**That equality is the missing check, measured rather than asserted.**

### 4a. The four numbers

| quantity | law | what it is |
|---|---|---|
| `R3ship − R4ship` | **`5.00000`, FLAT** — `0.00000` on all four regressors | the whole in-contract safety tax: **one reslice check per call and nothing else** |
| `R1h − R1` (gcc) | `+4.00000·xpush − 8.00000·dpush` | the **fullness check**, inside one language |
| `R1h − R1` (clang) | `+4.00000·xpush + 0·dpush − 1.00000·xpop` | the same check, other compiler |
| `R2 − R3` | **`20.00000·(xpush + dpush + xpop + epop) + 11`** | the opcode-stream bounds checks, which one reslice removes |
| `R2 − R4` | `20.00000·nops + 16` | the sum |

**The fullness check costs `+4.00000` Ir on every accepted push in BOTH
compilers.** What it *saves* on a rejected push differs — 8 under gcc, 0 under
clang — and that is §2's decode difference, not a difference in the check: gcc's
push arm is 18 against clang's 9, so skipping it saves more.

⚠ **One row is measured and not explained: clang's R1h is `1.00000` Ir per
executed pop CHEAPER than clang's R1** (14 against 15), on the arm the check
does not touch. It is exact and it is small; it is recorded rather than
attributed, and no claim here rests on it.

⚠ **`R2 − R3 = 20.00000 per operation + 11` is p03's law, on a different
kernel** — p03 measured `20.00000·(xpush + dpush + xpop + epop) + 11` for the
identical quantity. The two patterns share the 5-byte opcode-stream layout and
the one-reslice R3, and nothing else; the constant reproducing to the
instruction, including the `+11`, is a cross-pattern reproduction rather than a
coincidence.

**And the emptiness check cannot be differenced**, because it is in every rung —
which is the point of putting it there. What band E gives instead is that an
executed pop costs 7 more than one the guard rejects (15 against 8 in R4), so
p04's per-operation figures are per **executed** operation, exactly as p03's
were.

### 4b. The mechanism, stated as the pattern's result

> **On p04 the per-operation safety tax is `0.00000` because the OPERATOR
> carries the invariant the proof carries.** `head < RING_CAP` and
> `tail < RING_CAP` are what the two accessors need; `(x + 1) % RING_CAP`
> establishes each of them unconditionally; and at a power-of-two `RING_CAP`
> that fact is a set of KNOWN BITS, which is what LLVM propagates around a
> loop-carried phi. Change the constant to 60 and the same fact becomes a
> RANGE, LLVM loses it at the phi, and the tax jumps from `+5` per call to
> `+479` (§1a) — which the dead-clamp control then takes back to `+5` (§1b).

p05's sentence — *"the safety tax is the price of the optimiser failing the
lemma the proof proves"* — is therefore **true of p04's CAP=60 control and
vacuous for p04 as shipped**: at 64 the optimiser does not fail the lemma. p03
generalised that sentence from a nonlinear fact to a linear one; p04 adds the
other end of the axis, a fact the optimiser gets for free, and the discriminator
between the two is `bits` versus `range`.

## 5. The proof obligations and the TCB tally

```
$ grep -c 'assume('              patterns/p04-ring-buffer/verus.rs   -> 0
$ grep -c 'assume_specification' patterns/p04-ring-buffer/verus.rs   -> 0
$ grep -c 'verifier::external\]' patterns/p04-ring-buffer/verus.rs   -> 0
$ grep -c 'verifier::external_body' patterns/p04-ring-buffer/verus.rs -> 5
```

**TCB: 10 lines across 5 items, THREE of them `unsafe`** — p03's shape, for
p03's reason: the kernel has two buffers and one of them is written. The
declared figure is the **gate's own `tcb_items` total**, re-read from
`results/gate/p04-ring-buffer.json` after the run rather than counted by hand
(p09 declared 12 where the gate said 7).

| item | lines | `unsafe`? | `requires` | `ensures` |
|---|---:|---|---|---|
| `buf_get_unchecked` | 1 | yes | `i < v@.len()` | `r == v@[i as int]` |
| `ring_get_unchecked` | 1 | yes | `i < v@.len()` | `r == v@[i as int]` |
| `ring_set_unchecked` | 3 | yes | `i < old(v)@.len()` | `final(v)@ == old(v)@.update(i as int, x)` |
| `load_input` | 4 | no | — | — (deliberately: an `ensures` here would be an axiom about a file's contents) |
| `emit` | 1 | no | — | — |

**Neither stack accessor carries `v@.len() == 64`**, and that is deliberate
rather than an omission: p03 shipped a draft with that conjunct and the gate
refused it as a **tautology** — vstd's `array_len_matches_n` discharges it from
the `&[u64; 64]` parameter type alone, so it demanded nothing of any caller —
with stage 5c-req's tautology probe and stage 5c-twin's per-conjunct deletion
probe both firing. p04 was written knowing that and states the single conjunct.

### SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked(i) }` and the twin's is `v[i]`. Those are the same
operation with and without the bounds check that `<[T]>::get_unchecked`'s
documented contract makes the caller's responsibility, so a `requires` too weak
to license the first is too weak to license the second, and Verus can see the
second. Nothing else is in either body: no arithmetic, no second read, no side
effect. This is the accessor p01, p02, p03, p05, p07, p11, p16 and p17 all ship,
character for character.

(b) *Is the `ensures` complete with respect to every unchecked operation the
body performs?* The body performs exactly one unchecked operation — a read of
`v` at index `i` — and the single `ensures` clause `r == v@[i as int]` names it
and its result. There is no second index, no write, no aliasing and no
provenance step for a clause to be missing. This is the labelled blind spot in
`.memory/04-verus.md` (a body that also read `i + 1` would pass every mechanical
check), and the only backstop for it is Miri on `unsafe.rs`, which this pattern
runs on all five inputs (§8).

(c) *Does each clause mean the same in both configurations?* Yes, and it is
checkable rather than asserted. Counted the way the gate counts it — over
`vparse.blank_noncode(...)`, i.e. the token stream with comments and string
literals blanked — the token `slb_twin` occurs only on the three twins' own
`#[cfg(slb_twin)]` attributes and nowhere else in `verus.rs`, and `verus.rs`
includes nothing but `common/driver.rs`, which is outside `verus!` and carries
no `slb_twin`. `i`, `v` and `v@.len()` denote the same values in both
configurations; there is no `#[cfg]`-varying `const`, `type` or `use` anywhere
in the file.

### SLB-TRUSTED-ARGUMENT verus.rs ring_get_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u64; 64]` and the twin's is `v[i]` on
the same type. Verus's own array support (`vstd::array`, `array_index_get`, and
the `a[i]` index form its docs recommend) gives the checked form a specification
with the identical `0 <= i < N` obligation, so the twin is the same operation
with the check that `get_unchecked` moves onto the caller. The two bodies differ
in nothing else.

(b) *Is the `ensures` complete with respect to every unchecked operation the
body performs?* The body performs exactly one unchecked operation — a read of
the array at index `i` — and `r == v@[i as int]` names it and its result. There
is no write here, no second index, no aliasing and no provenance step. The
`requires` is **one** conjunct, `i < v@.len()`, which for a `&[u64; 64]` reads
`i < 64`; a second conjunct `v@.len() == 64` would be a tautology (§5b). **What
is worth stating about this item, because it is p04's whole result, is what its
precondition does NOT need**: the caller discharges `head < 64` from
`head = (head + 1) % RING_CAP` alone — not from the emptiness guard beside it,
not from any relation to `tail`. §6 measures that deleting either guard leaves
this precondition discharged. The blind spot of `.memory/04-verus.md` applies
unchanged and Miri on `unsafe.rs` is the backstop.

(c) *Does each clause mean the same in both configurations?* Yes. `i < v@.len()`
mentions only the two parameters and no constant at all, which closes the bypass
`.memory/04-verus.md` records at TASK_009_REVIEW by construction rather than by
inspection (a `#[cfg(slb_twin)] const SLACK` made p01's twin check
`i < v@.len() + 0` while the shipped file used `+ 1`). The array's *type* carries
a `64`, and it is the same `64` in both configurations because it is in the
signature the gate lifts and compares. The gate's token scan reports `slb_twin`
only on the three twins' own attributes.

### SLB-TRUSTED-ARGUMENT verus.rs ring_set_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked_mut(i) = x; }` and the twin's is `v[i] = x;`. Verus
specifies the checked indexed store on an array with the same `0 <= i < N`
obligation, so a `requires` too weak to license the unchecked store is too weak
to license the checked one, and the gate's per-conjunct deletion probe confirms
the twin *uses* the precondition rather than merely carrying it. This is the
second trusted item in this project that writes through an unchecked index,
after p03's.

(b) *Is the `ensures` complete with respect to every unchecked operation the
body performs?* The `requires` is one conjunct, `i < old(v)@.len()`. The body
performs exactly one unchecked operation — a store of `x` into slot `i` — and
the single `ensures` clause states it as a **whole-sequence equality**,
`final(v)@ == old(v)@.update(i as int, x)`, not as a property of slot `i` alone.
That is deliberate and on p04 it is load-bearing in a way it was not on p03:
**R1's bug IS a store to a slot the checked kernel does not write**, so a
slot-`i`-only `ensures` would have been silent about the very thing this pattern
models, in the twin as well as in the proof. As written, one clause says both
*"slot `i` became `x`"* and *"nothing else moved"*. It is not closed — a write
*outside* `v` would still be invisible — so Miri on `unsafe.rs` remains the
backstop and is why `miri.required` is true.

(c) *Does each clause mean the same in both configurations?* Yes, on the same
grounds as the accessor above: the `requires` is the single conjunct
`i < old(v)@.len()` and mentions no constant, `old(v)` and `final(v)` are
Verus's own `&mut` spellings and are not configuration-dependent, and the gate's
token scan reports `slb_twin` only on the three twins' own attributes. The one
asymmetry worth naming is that this item's `requires` does **not** constrain `x`,
and that is declared in `spec.md`'s `verus.unsafe_justifications` and shouted by
the gate on every run rather than left for a reader to notice.

## 6. The proof, its mutants, and the invisibility probe

`./verus_run.py patterns/p04-ring-buffer/verus.rs` → **`9 verified, 0 errors`,
first run**; `--cfg slb_twin` → **`12 verified, 0 errors`**.

```
RING_CAP 1 + run 1 + kernel 2 + main 5 = 9        (each --verify-function measured)
```

**The invariant, and it is the whole result.** p04's kernel has ONE loop and
ZERO nonlinear arithmetic. The memory-safety obligation is

```
head < RING_CAP,
tail < RING_CAP,
```

— **two independent one-variable clauses**, each discharged from its own
`% RING_CAP`. TASK_042 predicted *"`head < CAP && tail < CAP` plus whatever
relates them"* and budgeted a session for it. **Nothing relates them.** Both
guards — `head != tail` and `(tail + 1) % RING_CAP != head`, the two places
where the cursors meet — are absent from the memory-safety argument entirely.

### 6a. Every mutant, and the positive controls that make the probe non-blind

`.memory/05-layout.md` item 11: a Verus file that does not verify cleanly cannot
live in the pattern directory, so every mutant is generated into `.temp/` from
the **shipped** `verus.rs` by exact-string substitution with an asserted hit
count (`controls/gen_controls.py`), and this section carries the commands and
the output.

```
$ python3 patterns/p04-ring-buffer/controls/gen_controls.py
$ python3 .temp/p04/run_verus_controls.py

p1_weak_requires       verification results:: 9 verified, 0 error
p2_nofullguard         verification results:: 8 verified, 1 error invariant not satisfied at end of loop body
p3_weak_invariant      verification results:: 8 verified, 1 error precondition not satisfied
p4_noemptyguard        verification results:: 8 verified, 1 error invariant not satisfied at end of loop body
m_control_msonly       verification results:: 9 verified, 0 error
m_nofull_msonly        verification results:: 9 verified, 0 error
m_noempty_msonly       verification results:: 9 verified, 0 error
m_nomod_msonly         verification results:: 8 verified, 1 error invariant not satisfied at end of loop body
m_offby1_msonly        verification results:: 8 verified, 1 error precondition not satisfied
m_false_a_msonly       verification results:: 8 verified, 1 error assertion failed
m_false_b_msonly       verification results:: 8 verified, 1 error assertion failed
m_false_c_msonly       verification results:: 8 verified, 1 error assertion failed

-- the same four under --cfg slb_twin --
p1_weak_requires       verification results:: 11 verified, 1 error precondition not met: index in bounds for this access
p2_nofullguard         verification results:: 11 verified, 1 error invariant not satisfied at end of loop body
p3_weak_invariant      verification results:: 11 verified, 1 error precondition not satisfied
p4_noemptyguard        verification results:: 11 verified, 1 error invariant not satisfied at end of loop body
```

Every run above is `--multiple-errors 20`, so no failure is hiding another
(`.memory/04-verus.md` 2b).

**`_msonly` strips the FUNCTIONAL specification and nothing else**: the kernel's
`ensures`, the relational loop invariant that carries it, and the driver's
consuming `assert`. Nothing about `head`, `tail` or either accessor's
precondition is touched.

- **`m_nofull_msonly` — R1's bug transplanted into R5, with the functional
  specification stripped — is `9 verified, 0 errors`.** The missing fullness
  check is **invisible to memory safety**. Second instance of p09's result, and
  the first where the *mechanism* is visible in the invariant rather than
  inferred from a probe.
- **`m_noempty_msonly` is `9 verified, 0 errors` too**, which p09 did not have:
  *both* of p04's guards are invisible, because neither appears in the
  memory-safety argument.
- **The probe is not blind, five ways.** `m_nomod_msonly` (delete the `%` from
  the write cursor's update) fails on the very invariant the two above satisfy;
  `m_offby1_msonly` (`ring[tail + 1]`) fails at an accessor precondition; and
  `assert(false)` in three separate places fails in all three.
- **With the specification in place the bug IS caught**: `p2_nofullguard` fails
  the relational invariant. So the obligation that catches R1's bug is the
  functional `ensures`, and never an access obligation.

**And the two facts are the same fact**, which is the sentence to quote:

> **The relation between `head` and `tail` is exactly the part of the state the
> memory-safety obligation does not need — which is precisely why deleting
> either guard is invisible to it.** A ring buffer's indices cannot run away;
> that is why it is the data structure you reach for, and it is why memory
> safety has nothing to say about it going wrong.

### 6b. The four `p_*` mutants each fail for a different reason

- **`p1_weak_requires`** — `i < v@.len()` → `i <= v@.len()` in
  `ring_get_unchecked` **and** its twin, so the signatures still match and the
  contract pin does not move. **The shipped configuration PASSES (9/0)** and only
  `--cfg slb_twin` catches it (*precondition not met: index in bounds*). The
  tautology probe cannot see it, parameter coverage cannot see it, and deletion
  is not applied to trusted items. **The verified twin is the only mechanism in
  this project that catches it**, and this is the second pattern (after p03)
  where it has been exercised on an accessor that is not the slice one.
- **`p2_nofullguard`** — R1's bug in the exec code, functional spec in place:
  *invariant not satisfied at end of loop body*, i.e. the relational clause.
  **Not** a memory error, which is the whole point (contrast p03, whose same
  mutant fails at `possible arithmetic underflow/overflow`, and p16's, which
  fails `decreases`).
- **`p3_weak_invariant`** — `tail < RING_CAP` → `tail <= RING_CAP`, one past
  what is true: *precondition not satisfied*, at `ring_set_unchecked`'s
  `i < old(v)@.len()`. So the invariant is load-bearing **for the access**, and
  it is load-bearing for the *same* fact `%` supplies for free at 64 and does
  not supply at 60 (§1a). That pairing is established from two directions.
- **`p4_noemptyguard`** — the other guard deleted. It is here because `spec.md`
  claims *"the emptiness check is in every rung and only the fullness check is
  the variable"*, and a claim about which of two guards is the variable needs
  the other one shown to matter.

All four fail under `--cfg slb_twin` as well, so none is passing by skipping a
configuration.

## 7. The adversarial table, per rung

`-O3 isolated`, gate stages 4 and 7 (`.temp/p04/gate1.log`). `=` means "agrees
with `model.py`".

| input | model's answer | R1 (c-gcc / c-clang) | R1h ×2, R2, R3, R4, R5 | sanitiser on R1 |
|---|---|---|---|---|
| `adversarial-overwrite` | 61209146786944 | **12736506159104 — differs** | = | **clean, exit 0** |
| `adversarial-wrap` | 1291274053164148224 | = | = | clean, exit 0 |
| `adversarial-count` | 0 | = | = | clean, exit 0 |
| `small` / `large` | — | = | = | clean, exit 0 |

**1. Nothing fires, anywhere, and that is the finding.** ASan + UBSan at the
gate's own flags (`-fsanitize=address,undefined -O1`, static runtimes) are
silent on **every** input including the one the pattern exists for; Miri is
`no UB` on all five (§8); safe Rust's bounds check never trips; and §6 measures
that the memory-safety half of the proof discharges the mutant. `model.py`'s
`sanitizer_expect` is **derived** from *"does any rung form a ring index outside
`[0, RING_CAP)`"* and returns `"clean"` identically, which is arithmetic and not
a tabulation: every index either rung forms is `head` or `tail`, both start at 0
and every update is `(x + 1) % RING_CAP`.

**2. What R1 actually does.** 63 pushes fill the ring; the 64th stores into the
one slot the checked kernel keeps reserved and advances `tail` onto `head`, so
the ring **reads empty and 63 live elements become unreachable**. The remaining
136 pushes then refill it from scratch. The checked rungs end at
`head = 0, tail = 63` and R1 at `head = 0, tail = 8` — because R1 advances
`tail` 200 times and `200 % 64 == 8` — so `((acc*31 + head)*31 + tail)*31 + nops`
separates them: **2153 against 448** on window 0.

**3. R1's answer IS reproducible across runs**, unlike p03's. Nothing it reads
depends on an address: the ring is fully initialised by the pushes before any
pop reads it, in R1 as much as in R1h, so there is no uninitialised read and no
ASLR dependence. p03's checksum was a pointer-disclosure oracle; p04's is a
deterministic wrong answer, which is *harder* to notice, not easier.

**4. The two controls do their job.** `adversarial-wrap` (520 operations at low
occupancy, so each cursor crosses the wrap point **four** times) attacks the
modular arithmetic and `adversarial-count` (`5·4096 > 200`) the length check —
**both of which R1 has** — and all eight cells agree on both, byte for byte.
Without them, "R1 omits exactly one line" would be a claim about the source.

## 8. Identity, Miri, and the twin

**R4 ≡ R5, `-O3 isolated`, `exact`:** `md5_fn c0573f691c95`, `md5_raw
1be5994704b2` equal, 74 instructions and 15 B of padding each; kernel-exclusive
`Ir` **3363.00 both on `small` and 11662.00 both on `large`**. At `O0` it is
`norel` — the crate names differ in length so the `call` displacements do.

**Miri: 5 of 5 inputs, no UB, no blocked rows.**

```
ok miri unsafe.rs on adversarial-count.bin      n_iters=4: no UB, stdout '0'
ok miri unsafe.rs on adversarial-overwrite.bin  n_iters=4: no UB, stdout '66277952'
ok miri unsafe.rs on adversarial-wrap.bin       n_iters=4: no UB, stdout '7455164802910147328'
ok miri unsafe.rs on large.bin                  n_iters=4: no UB, stdout '1412079219607546856'
ok miri unsafe.rs on small.bin                  n_iters=4: no UB, stdout '12975787801841186814'
```

⚠ **Read that as a finding and not as a pass.** Every p04 Miri row is clean
*by construction*: R4 has both guards, and even the rung that does not (R1) is
in bounds. Miri is here because the pattern has three trusted items whose
`ensures` need not be complete, not because it can see this bug — and it cannot.

**The twin is not idle** in the sense that matters: §6b's `p1_weak_requires`
passes the shipped configuration at 9/0 and fails only under `--cfg slb_twin`.
All three accessors are single-clause, so p04 still does not supply the
multi-clause case `.memory/04-verus.md` says the mechanism was built for; it is
the second pattern to exercise it on a non-slice accessor.

### 8b. What the anti-collapse stage certifies here

```
probe small.bin   work_per_call=1189 byte(s)  => derived floor  297.2 Ir/call
probe large.bin   work_per_call=4154 byte(s)  => derived floor 1038.5 Ir/call
ok 64 cell/probe pairs: marginal Ir per call 2886...150859, all above the derived
   floor (tightest margin 9.6x over a declared 0.25 Ir/byte);
   d(Ir)/d(work) 2.40...36.30 (rate 0.25)
```

Margin 9.6×, i.e. this stage tolerates an ~90% loss of work before it objects.
It is a NOT-COLLAPSED smoke test and nothing finer; what certifies the work
happened is stage 2's model checksum.

## 9. Dead code that is kept on purpose

`if len < 4 { return 0; }` is unreachable in this benchmark, because the driver
guard is `stride_w >= 4` and `len` is always `stride`. It is kept so the kernel
is **total** and its `requires` stays purely structural. It costs one compare
per call. The `nops == 0` guard is *not* dead in the same way: it is reachable
from the wire format and no shipped input takes it.

## 10. The spelling spread

`.memory/05-layout.md` item 13 makes this section mandatory, and
`.memory/01-ladder.md` finding 3 requires **at least two independent in-contract
R3 spellings with the cheaper quoted**. All numbers kernel-exclusive Ir/call,
built by `controls/gen_controls.py` and measured by `.temp/p04/run_controls.py`,
which also **checks every control against `harness/check.py::spelling_matches`
and against `model.py`'s checksum on all five matrix inputs** before any of its
numbers is quoted.

### 10a. The R3 side — the shipped spelling IS the cheapest found, and four spellings are ONE machine code

| spelling | small | −R4 | large | −R4 | `md5_fn_norel` | in contract? |
|---|---:|---:|---:|---:|---|---|
| `safe_tuned` (**shipped**) — window reslice, `w[4 + 5*k]` | 3368 | **+5** | 11667 | **+5** | `b5040cb5d805` | yes |
| `r3_forloop` — `for k in 0..nops` | 3368 | +5 | 11667 | +5 | `b5040cb5d805` | yes |
| `r3_assert_head` — `assert!(head < RING_CAP && tail < RING_CAP)` at the loop head | 3368 | +5 | 11667 | +5 | `b5040cb5d805` | yes |
| `r3_chunks` — `w[4..4+5*nops].chunks_exact(5)` | 3602 | +239 | 12494 | +832 | `7cc78eee6776` | yes — **dearest found** apart from R2 |
| `safe_naive` (R2, shipped) | 8119 | +4756 | 28278 | +16616 | `805c3851ce68` | yes |
| `m_mask` — `& (RING_CAP - 1)` for `%` | 3368 | +5 | 11667 | +5 | `b5040cb5d805` | **no** — `forbidden[0]`, 4 required misses |
| `cap64_r3_clamp` — R3 + a dead `if tail >= RING_CAP \|\| head >= RING_CAP` | 3368 | +5 | 11667 | +5 | `b5040cb5d805` | **no** — dead code inserted to move a number |

* **fixed-R4 bound** (`R3ship − R4ship`, R4 held by fiat — the only sound
  quantity per `.memory/01-ladder.md`): **+5.00 on `small` and +5.00 on
  `large`**, and as a law `0.00000` on every regressor `+ 5`.
* **R3-side span**, cheapest-found to dearest-found in contract: **+5 … +4756 on
  `small`** and **+5 … +16616 on `large`**; excluding the R2 rung, **+5 … +239 /
  +5 … +832**. **Cheapest found: +5.00, on BOTH blobs** — and this is the first
  pattern in this project whose *shipped* R3 is the cheapest found rather than
  being beaten by the next lever. Write "cheapest found", never "minimum": p03's
  was refuted twice, once after a review had confirmed it.
* ⚠ **Four in-contract spellings land on the same number because they land on
  the same MACHINE CODE** — `md5_fn_norel b5040cb5d805`, `n_fn 84`, all four.
  `.memory/01-ladder.md` warns that *"reached by many spellings is not evidence
  of a floor"*; here it is not even four points, it is **one point written four
  ways**. Two of the four are out of contract (`m_mask`, `cap64_r3_clamp`) and
  are byte-identical to the two that are in it, so **neither exclusion removes a
  single instruction from the admissible class** — the same shape
  `.memory/01-ladder.md` records for p17.
* **The `m_mask` exclusion is therefore not protecting a number, and its
  direction is neutral rather than against interest**: forbidding the mask moves
  p04's published figure by **0.00**. It is forbidden because a mask answers
  p09's question and not p04's — the whole pattern is whether the optimiser
  carries a bound through `%`, and writing the mask by hand assumes the answer.
* **`r3_assert_head` is the lever that was p03's cheapest and here buys nothing**
  — byte-identical to the shipped rung. There is no invariant left to hand the
  optimiser at `RING_CAP = 64`. §1b measures the same assertion-shaped control
  at 60, where it is worth −358 Ir/call.

### 10b. The R4 side — DEGENERATE, and for the pattern's own reason

TASK_026 §0 item 3: **a rung covered by an `identity` pin is chained to the
prover**, so an R4 candidate is not a rung until its R5 twin verifies. Every
candidate has a twin in `controls/gen_controls.py` and **every twin was run
before any of its numbers was differenced.**

| spelling | small − R4 | large − R4 | Verus verdict |
|---|---:|---:|---|
| `r4_forloop` — `for k in 0..nops` | **0.00** | **0.00** | **`9 verified, 0 errors`** — admissible, does not move |
| `m_clamp_unsafe` — R4 + the dead clamp | **0.00** | **0.00** | **`9 verified, 0 errors`** — admissible, does not move |
| `r4_ptr` — `as_ptr()` / `as_mut_ptr()` / `add()` | 0.00 | 0.00 | **DISQUALIFIED** — *"The verifier does not yet support the following Rust feature: dereferencing a raw pointer"* |

All three are **byte-identical to the shipped R4** (`md5_fn_norel
931607a74611`, `n_fn 74`). So:

> **p04's pair interval is DEGENERATE: the R4 endpoint has ZERO measured width,
> and the interval collapses onto the R3-side span.**

⚠ **That is the opposite of p03, on the same lever, and the reason is p04's
headline.** p03's `m_clamp_unsafe` was the project's first admissible R4 that
*moved* (−118 / +497). p04's is a byte-identical no-op — because the clamp seeds
a fact LLVM already has. The lever is not weaker here; the fact is already
free. §1b shows the same lever moving −358 on p04's own `RING_CAP = 60` control,
which is the control that keeps this from being a statement about the lever.

⚠ **And `min(R3) − min(R4)` is not p04's safety tax.** Both class minima are the
shipped cells, 3368 and 3363, five apart — which is the same +5 as the fixed-R4
bound only because both searches have converged on the shipped code.
`.memory/01-ladder.md` is explicit that differencing two upper bounds bounds
nothing; the sound number is the fixed-R4 bound.

## 11. Wall clock — the noise floor first, one large conversion factor, one clean null

`.memory/03-measurement.md`: run `common/layout/order.py` **before** believing
any `ns` number. It was run, on both inputs, two passes, three schedules.

⚠ **A defect in my own first run, recorded because it is a two-character trap:**
`order.py` appends `.bin` to `--input`, so `--input small.bin` silently times a
file that does not exist and every rung reads ~4.5 ms of process startup with
**R2 − R4 = +0.15%**. The corrected run is below. *A wall-clock null that costs
nothing to produce is exactly the shape that should be checked against the
`Ir` column before it is believed.*

### 11a. Identical-copy noise floor — p04 is protocol-INSENSITIVE

`order.py --copies 31 --reps 31 --passes 2 --cpu 3` on `small`, 31
**byte-identical** copies at the shipped layout:

| pass | schedule | R2 floor | R3 floor | R4 floor | R2 − R4 | R3 − R4 |
|---|---|---:|---:|---:|---:|---:|
| 0 | alternating | 15.50% | 15.86% | 15.84% | +25.18% | −0.11% |
| 0 | blocked (the bug) | 15.46% | 14.70% | 15.38% | **+9.74%** | −0.79% |
| 0 | `round_robin` (shipped) | 5.50% | 5.14% | 6.03% | +25.93% | +0.12% |
| 1 | alternating | 6.92% | 4.30% | 9.97% | +26.09% | +0.27% |
| 1 | blocked (the bug) | 14.81% | 12.98% | 16.11% | **+9.74%** | −2.95% |
| 1 | `round_robin` | 5.92% | 4.37% | 4.17% | +25.67% | +0.71% |

On `large` (15 copies, 21 reps): floor **0.64…1.14%** in the quiet passes,
`R2 − R4` **+9.45…+9.94%** across all six readings *including* blocked, and
`R3 − R4` **−0.30…+0.14%**.

**p04 is protocol-insensitive on `large` and protocol-sensitive on `small`** —
blocking pulls `small`'s `R2 − R4` from +25.7% to +9.7%, a third independent
reproduction of TASK_031's artefact (after p05 and p03). The four
correct-protocol readings agree to 0.9 points.

### 11b. What converts and what does not

**Raw levels, `min` of 31, interleaved by cell, `taskset -c 3`, `-O3
isolated`** (`.temp/p04/nsprobe.py`). The raw level is quoted first because
`.memory/03-measurement.md` places the ±9-point bar in the *correction*:

| rung | small min (ms) | large min (ms) |
|---|---:|---:|
| c-gcc | 5.098 | 11.683 |
| c-gcc-h | 5.237 | 11.877 |
| c-clang | 6.573 | 11.576 |
| c-clang-h | 7.146 | 11.770 |
| **R2 safe-naive** | **7.288** | **13.037** |
| **R3 safe-tuned** | **5.575** | **11.837** |
| **R4 unsafe** | **5.418** | **11.820** |
| **R5 verus** | **5.544** | **11.775** |

Four of the eight `small` cells exceed the 10% min-to-median spread threshold
(8.68…13.28%), so **the single-layout `small` row is discarded** and §11a's
population is what `small`'s numbers come from. `large`'s spreads are
1.24…2.75% and it is quoted.

**Two readings:**

**(1) R2 is slower than R4 everywhere, and the conversion factor is large.**
`+141.4% / +142.5%` of instructions becomes `+25.7%` (`small`, population
median) and `+9.7%` (`large`), i.e. **5.5× on `small` and 14.7× on `large`** —
the great majority of R2's instruction gap is free. Same shape as p03's
10.7×/17.3× and p16's +72% → +0.27%.

**(2) `R3 − R4` is a clean null in wall clock, and it must be**: R3 executes
`+0.149%` more instructions, and the population reads `−0.30…+0.71%` across ten
correct-protocol readings on two inputs against a 0.64…6.03% floor. This is a
null the `Ir` column *predicts*, which is the rarer and better kind.

### 11c. The `t(n_iters = 1)` correction, and why only `large`'s is quotable

| pair | `Ir` | raw `ns` level | corrected (`− t(1)`) |
|---|---|---|---|
| R2 − R4, `large` | +142.48% | +10.30% | **+23.69%** |
| R3 − R4, `large` | +0.043% | +0.14% | +0.43% |
| **R5 − R4, `large`** (must be 0) | **0.00%** | −0.38% | **−0.64%** |
| R5 − R4, `small` (must be 0) | 0.00% | +2.33% | **+6.03%** |

**`R5 − R4` is the error bar, because the kernels are byte-identical.** On
`large` the correction's residual is 0.64 points and the corrected R2 figure
(+23.69%) clears it by 37×, so it is quotable. On `small` the residual is **6.03
points** — the `t(1)` pass subtracts ~55% of a 5.4 ms level there — and the
corrected `small` column is **not quoted at all**: it reads `c-clang` as +78.86%
slower than R4 when `c-clang` executes 14.6% *fewer* instructions. That is
`.memory/03-measurement.md`'s rule earning its keep rather than being obeyed.

### 11d. What is NOT here

- **No cycles/byte and no cycles/operation.** ns is a measurement on this box,
  cycles is an inference spanning ±15% within one session, and the clock was not
  measured interleaved with these reps.
- **No branch-simulation row.** p03 built the `sweep-bpred`/`sweep-brand` pair
  and measured 0.5002 mispredicts per operation on a random op stream; p04's
  dispatch is the same shape and nothing here needs the number, so it was not
  re-run. Reported as not done rather than inherited.
- **No layout population** beyond the identical-copy control. `order.py` gives
  the floor and the schedule check; `layout_gen.py`'s 30-layout population was
  not run, so p04 has **no mode-matched verdict** and its `ns` figures are
  single-layout populations of byte-identical copies. Stated as a gap.
- **`O0` rows are built and gate-checked but no number here comes from one.**

## 12. What p04 answers that no earlier pattern could

### 12a. Does the safety cost amortise?

p07's answer was *"no axis along which it amortises"*; p11's *"it crosses
zero"*; p16's and p17's *"to zero, per byte"*; p05's *"O(nrow)"*; p03's *"along
one axis and not the other, and the attacker picks which"*. **p04's is a sixth
answer and the sharpest: there is nothing to amortise.** `R3ship − R4ship` is
`5.00000` per *call*, `0.00000` on every one of the four regressors, at every
fill ratio and every operation count over 99 blobs. The tax is one reslice
check, and the ring — the thing the pattern is named for — is free in safe Rust.

### 12b. Is the obligation the same one the optimiser fails?

**No, and p04 is the first pattern where the answer is no.** §6b shows
`tail < RING_CAP` is exactly what `ring_set_unchecked`'s precondition needs;
§1 shows LLVM has it already. p05 and p03 both measured *"the tax is the price
of the optimiser failing the lemma the proof proves"*; p04 measures the
complement — **the same lemma, supplied for free by the operator** — and §1a's
`RING_CAP = 60` control is the same kernel with the fact taken away, where the
tax reappears at `+479` and p03's clamp takes it back to `+5`.

### 12c. What memory safety is not for

`.memory/01-ladder.md` finding 11 (p09) established that a bug can be invisible
to every memory-safety mechanism. p04 is the second instance and adds the
mechanism: **p09's invisible index is invisible because `q >> 7 <= q >> 6`;
p04's invisible write is invisible because the ring's invariant is
`head, tail < RING_CAP` and the bug is about a RELATION between them.** The
memory-safety obligation is one-variable; the correctness obligation is
relational; and a container whose indices are modular puts every interesting
bug in the second class. That is a statement about the *data structure*, not
about one substitution.

## 13. The declaration, and when it was written

`spec.md`'s `idiom` block was written **after** the phase-0 probes of §0 and
**before** any rung, input file or `model.py` existed. What was known when it
was written is the whole of §0 — the byte-identity at 64, the 12-instruction
gap at 60, that p03's clamp deletes the 60 check, that the memory-safety-only
proof discharges the missing guard against five positive controls, and that the
two folded cursors separate R1 from the checked rungs on the adversarial window
and on no matrix window. What was **not** known is any figure in §3, §4, §10 or
§11.

`.memory/01-ladder.md`'s direction test is what a reviewer should apply. p04's
two exclusions move the published figure by **exactly 0.00** (§10a): `m_mask`
and `cap64_r3_clamp` are byte-identical to the shipped R3. So no exclusion here
is protecting a number, and what keeps `+5.00` in place is the choice of shipped
spelling — which, uniquely on this project so far, is also the cheapest found.

### 13a. The shared paragraph is byte-identical

The `NAMED-SPELLING STANDARD` paragraph in `idiom.why` is **11 004 characters**,
identical to all ten other patterns' — it was read out of p03's own hashed block
by `.temp/p04/make_spec.py` rather than retyped, and
`python3 .temp/p04/make_spec.py --check` re-derives `spec.md` and diffs it
(`spec.md re-derives byte-identically`). p04 is the third pattern (after p11 and
p03) whose `spec.md` has a build script; the committed `spec.md` is
self-contained and the byte-identity is re-checkable from the tree alone.

### 13b. The stage-0b audit

```
audit  36 backticked spelling(s) over 6 rung(s) -> 110 (spelling, rung) pair(s), 73 present
audit  forbidden: 12 spelling(s), 0 hit(s)   (decidable)
audit  required : 0 pin nothing, 1 scoped-absent pair(s)
audit    absent  required[1]  c  c/kernel.c  `if ((tail + 1) % RING_CAP != head) {`
```

`pins_nothing = 0` is the signal that matters. **There is exactly ONE
scoped-absent pair in the whole pattern, and it IS the bug**: `required[1]`'s
`if ((tail + 1) % RING_CAP != head) {`, absent from `c/kernel.c` and present in
`c/kernel_hardened.c`. Every backticked entry was checked against
`harness/check.py::spelling_matches` (`.temp/p04/pins.py`) **before** any of it
was quoted, and the only miss is that one.

