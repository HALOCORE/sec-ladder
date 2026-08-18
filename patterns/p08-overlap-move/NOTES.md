# p08 — findings, adversarial behaviour, TCB tally, sticking points

> **Read §1 first.** p08 was commissioned on the premise that an overlapping
> `memcpy` corrupts. **On this box it never does** — at any size, with either
> compiler, at either optimisation level — and the mechanism is not luck. §1 is
> that measurement; everything after it is written knowing it.

**The one-line result.** *The bug is real, the undefined behaviour is executed on
every call of `adversarial-overlap`, and **nothing observable happens**: on
glibc 2.39 / x86-64 `memcpy` and `memmove` are literally the same function, so
R1 and R1h agree bit for bit on every input and cost **exactly the same number of
instructions**. p08's security axis is therefore not "C computes the wrong
answer" but **"UB that is invisible without a sanitiser"** — and even the
sanitiser is conditional, because this box's gcc default-enables
`_FORTIFY_SOURCE=3`, which rewrites the call to `__memcpy_chk`, which ASan does
not intercept.*

**What Rust buys here is not a runtime check, and that is the first such result
on this project.** The C program **cannot be transliterated into safe Rust at
all** — three spellings, three `E0502`s, zero runtime cost because the program
does not exist (§5a). `copy_within` is the only safe way to say it and it is
`memmove` by definition.

Four numbers, `-O3 isolated`, marginal Ir per call, **R3 first** per
`.memory/01-ladder.md`'s standing rule:

| | **R3 safe-tuned** | R2 safe-naive | R4 unsafe / R5 verus |
|---|---:|---:|---:|
| `small` (m = 498) | **7334.16** | 18264.16 | 7308.16 / 7308.16 |
| `large` (m = 4089) | **29079.56** | 120110.56 | 29053.56 / 29053.54 |
| vs R4 | **+26.00 / +26.00, flat** | +10956.00 / +91057.00 | 0 |
| vs R4, % | **+0.36% / +0.09%** | +149.9% / +313.4% | 0 |
| wall clock vs R4 (`large`) | **−1.3%** | **+130.0%** | — |

**R3 is free again, and here for a stronger reason than usual: it emits the
*same `memmove` call* R4 does.** Stated carefully, because
`.memory/01-ladder.md` records the streak being broken: p01, p02, p16 and p17
had R3 free, **p05 did not** (+16.7% at `ncol = 8`, an `O(nrow)` cost, and the
review's words were *"the R3-free streak ends at five patterns, not six"*). p08
restores it — +0.36% / +0.09% instructions and −1.3% wall clock — and it is a
fifth instance, not a seventh.

**R2 is not free.** The naive reverse byte loop costs **11.26 Ir per moved byte**
against glibc's **0.113**, a 100× rate difference, and §3b attributes **100% of
that gap to the move** by construction, with a residual of −4.00 Ir per call.

**R1 vs R1h — the `memcpy` → `memmove` cost, isolated: `0.00` instructions per
call**, both compilers, both inputs, and the two kernels are the *same machine
code with one different call target* (§2).

---

## 1. The premise, and the measurement that refuted it

The task file's own list of things it was least sure of put first: *"that the
overlapping `memcpy` corrupts at all on glibc 2.39 — if it never does, p08's
security axis is 'UB that is invisible without a sanitiser' and I want that said
early rather than dressed up."* It never does.

### 1a. The sweep

`.temp/p08/probe/ovl.c` fills a buffer with a known pattern, runs
`memcpy(p + d, p, m - d)` and `memmove(p + d, p, m - d)` on two copies of it and
counts differing bytes. `mv_cpy` / `mv_mov` are `noinline` and take the length at
run time, so the compiler cannot expand the call into an overlap-safe
load-all-then-store-all sequence; all four builds contain a real `memcpy@plt`.

**80 (m, d) rows × 4 builds (gcc/clang × `-O0`/`-O3`) = 320 runs: `ndiff = 0`
on every single one.** `m` takes 40 values from 8 to 16 777 216, chosen to
straddle every glibc size regime (the 32/64/128/256-byte register paths, the
vector loop, the ERMS threshold and the non-temporal one); `d` is `m/8` and
`m/64` floored to 1, i.e. overlaps of 87% and 98% of the copy. A finer sweep at
`m = 4092` over 22 values of `d` from 1 to 2045 — a two-byte overlap up to a
half-buffer one — is likewise all zeros, as is a static-buffer variant and six
`GLIBC_TUNABLES` hwcaps combinations (`-ERMS`, `-AVX_Fast_Unaligned_Load`, …).

### 1b. The mechanism, which is why this is not luck

```
$ .temp/p08/probe/which_impl
memcpy  -> 0x7f81c8798940  ?
memmove -> 0x7f81c8798940  ?
same address: YES
```

`dlsym(RTLD_DEFAULT, "memcpy")` and `dlsym(..., "memmove")` return **one
address** — libc + `0x198940`. The symbol is local, so `nm -D` cannot name it;
the disassembly at that offset uses `ymm16`–`ymm23`, which are EVEX-only
registers, so it is the `__memmove_evex_unaligned_erms` family. On x86-64 glibc
the two exported names ifunc-resolve to one implementation, and that
implementation carries a live direction test:

```
198a90:	mov    %rdi,%rcx          # rcx = dst
198a93:	sub    %rsi,%rcx          # rcx = dst - src
198a96:	cmp    %rdx,%rcx          # ... < n ?
198a99:	jb     198b65             # yes -> BACKWARD copy
```

Below 256 bytes it does not even need that: the small-size paths load both ends
into registers *before* storing either, which is overlap-safe by construction.

So `memcpy` **is** `memmove` here, and R1's undefined behaviour is undefined in
the standard and inert in the implementation.

### 1c. What that does and does not license

It does **not** make the bug benign. It makes it *unobservable on this
platform*, which is the worse failure mode for a maintainer: the program passes
its tests, passes its fuzzing, ships, and breaks on the first platform whose
`memcpy` is genuinely forward-only, or under the first compiler that exploits
the UB in the *caller* rather than deferring it to libc. It is p02's headline
shape — silent, plausible, exit 0 — reached from the opposite direction, because
here there is no wrong answer at all.

It also means **`adversarial-overlap` is checksum-clean across all eight
cells** (§7), so p08's gate stays green on step 2 and the security half lives
entirely in the detection table (§5d).

---

## 2. R1 vs R1h — the `memcpy` → `memmove` cost, isolated

`.memory/01-ladder.md` asks R1-vs-R1h to price safety *inside one language* with
the signature, the calling convention and the register allocation held fixed. On
p02 that difference was a bounds comparison (+5 gcc / +12 clang per call); on p05
a size test (+7 / +2). **On p08 it is not a check at all — both cells call a
bulk-memory routine of the same size and the difference is which one.**

### 2a. Static: the same machine code, one different call target

`-O3 isolated`, `harness/asm.py` normalisation:

| cell | n_fn | nopad | normalised diff R1 vs R1h | the call |
|---|---:|---:|---|---|
| c-gcc / c-gcc-h | 118 / 118 | 111 / 111 | **empty** | `__memcpy_chk@plt` vs `__memmove_chk@plt` |
| c-clang / c-clang-h | 131 / 131 | 129 / 129 | **empty** | `memcpy@plt` vs `memmove@plt` |

The two kernels differ in the branch-target *symbol* and in nothing else. The
`md5_fn` differs (`2e75e9df7df1` vs `c64258ddb57f` under gcc); the instruction
stream does not.

Worth noting because it makes the comparison cleaner than it looks: **gcc `-O3`
inlines the memset and the copy-in as `rep stos %rax` and `rep movsq`**, so the
*only* libc call left in the gcc kernel is the move. R1 vs R1h under gcc is one
`__memcpy_chk` against one `__memmove_chk`, with nothing else in the frame.

### 2b. Dynamic: exactly zero

Marginal Ir per call (whole-program Ir at `n_iters=200` minus at 100, over 100 —
`harness/check.py` step 3b's method, which is symbol-independent and therefore
*does* contain the libc call, unlike kernel-exclusive Ir):

| cell | small | large |
|---|---:|---:|
| c-gcc | 4865.72 | 34805.28 |
| c-gcc-h | 4865.72 | 34805.28 |
| c-clang | 7293.60 | 29038.18 |
| c-clang-h | 7293.60 | 29038.18 |

**`R1h − R1 = 0.00` in all four cells.** Not "flat and small" — flat and *zero*,
because the callee is the same function. The task predicted "flat and small
(finding 3's family)"; the measurement is stronger than the prediction, and for
a reason that is a property of glibc rather than of the ladder.

**One caveat on the figures in this table, measured at TASK_017: p08's marginal
`Ir` does not reproduce to the hundredth across *sessions*, and p08 is the only
pattern where that is true.** Re-running all six gates at TASK_017 — no cell
source changed, all 28 `md5_fn` identical — moved **12 of p08's 64
`marginal_ir_per_call` cells** (and the 11 `d_ir_d_work` slopes derived from
them) by **0.02–0.08 Ir/call**, while the other five patterns reproduced
**541/541** of their recorded values exactly. Two runs *inside one shell* agree
on **64/64**, so this is not run-to-run noise.

The cause is the environment block, and it is measured rather than inferred.
With the byte-identical `unsafe-O3-whole` binary and byte-identical 100/200
iteration probe inputs, padding the environment with 0 / 200 / 400 bytes gives
whole-program totals 1 099 559 / 1 099 525 / 1 099 513 at `n_iters = 100` and
marginals of **7292.26 / 7292.24 / 7292.14** per iteration. The identical
experiment on p16 gives **3009.30 / 3009.30 / 3009.30** — invariant to the
hundredth. So the sensitivity is p08's own: its per-iteration work runs through
glibc `memcpy`/`memmove`, whose path length depends on buffer alignment, and the
environment block shifts the stack under it. `.memory/03-measurement.md` already
says whole-program totals move with the environment block; what is new is that
**differencing two of them does not cancel it here**, because the per-iteration
cost itself changes with alignment.

Magnitude: ≤0.08 on figures of 4 800–206 000, i.e. ≤2×10⁻⁵ relative. No claim in
this file rests on a digit that moves — `R1h − R1 = 0.00` is a difference of two
cells measured in the *same* run, and every §3 attribution is likewise a
within-run difference. But **quote p08's marginals to the instruction, not to
the hundredth**, and do not treat "every `marginal_ir_per_call` cell unchanged"
as an invariant for p08 across sessions.

Wall clock agrees, within a noise floor that is itself measured (§4):
`large`, min of 31 pinned interleaved reps — c-gcc 3670.08 ns vs c-gcc-h
3539.37 ns, c-clang 3527.73 vs c-clang-h 3492.81. **Both differences have the
hardened cell *faster***, which is physically meaningless and is how you know
you are inside the noise: R4 and R5, whose machine code is byte-identical,
differ by 1.1% on the same run.

### 2c. Where the call actually goes

The moves cost **922.00 Ir for 8170 moved bytes on `large` = 0.1129 Ir per moved
byte**, which is glibc's bulk rate (`.memory/03-measurement.md` measures `memcpy`
at 0.104 Ir/byte). On `small` the four moves total 157.94 Ir for 982 bytes =
0.1608, the excess being four call overheads on shorter copies.

---

## 3. Decomposition — attribute to a mechanism, never to a comparison

`.memory/01-ladder.md`: *a safety tax must be attributed to a mechanism, never to
a comparison*, and *confirm by construction, do not infer from reading two
disassemblies*. p08 starts from a stronger position than any earlier pattern:

> **R2, R3 and R4 differ in the body of one `#[inline(always)] fn move_right` and
> in nothing else.** Same header decode, same guard, same `copy_in`, same fold,
> same loop forms, same driver. The isolation is by construction rather than by
> an experiment afterwards.

That is a claim about the *source*, and it is checkable in eight lines
(comment-only lines dropped):

```
--- safe_naive.rs        +++ safe_tuned.rs
 fn move_right(v: &mut [u8], dr: usize, m: usize) {
-    for j in (0..m - dr).rev() {
-        v[j + dr] = v[j];
-    }
+    v.copy_within(0..m - dr, dr);
 }
--- safe_tuned.rs        +++ unsafe.rs
 fn move_right(v: &mut [u8], dr: usize, m: usize) {
-    v.copy_within(0..m - dr, dr);
+    unsafe {
+        let p = v.as_mut_ptr();
+        core::ptr::copy(p, p.add(dr), m - dr);
+    }
 }
```

§3b measures whether it survives codegen — it does, to within 4 instructions per
call.

### 3a. What each rung emits

`-O3 isolated`, `harness/check.py` stage 3a's own bulk-call column:

| cell | static n_fn | bulk calls in the kernel |
|---|---:|---|
| c-gcc / c-gcc-h | 118 | `__memcpy_chk@plt` / `__memmove_chk@plt` |
| c-clang / c-clang-h | 131 | `memcpy@plt`, `memset@plt` (+ `memmove@plt` in R1h) |
| **R2 safe-naive** | **269** | `memcpy`, `memset` — **no `memmove`** |
| R3 safe-tuned | 205 | `memcpy`, **`memmove`**, `memset` |
| R4 unsafe / R5 verus | 168 | `memcpy`, **`memmove`**, `memset` |

**R3's `copy_within` and R4's `ptr::copy` both lower to a `memmove` call; R2's
reverse indexed loop does not** — LLVM's loop-idiom recogniser never forms a
`memmove` from it, at any `m`. That is the answer to "R2 vs R3, decided by
disassembly", and it was established independently *before* the pattern was
built: `.temp/p08/probe/idiom.rs` compiles `while`-reverse, `for`-reverse and
slice-typed spellings and **none** produces a bulk call, while `copy_within`
gives a tail `jmp memmove` and `ptr::copy_nonoverlapping` gives `memcpy`. The
same holds in C — gcc keeps a 6-instruction scalar backward loop and clang
*vectorises* it under a runtime dependence-distance guard (32 B/iter when
`dr >= 32`, scalar otherwise) — but neither emits a call.

R2's move loop, four unrolled copies of it, is **10–12 instructions per byte
with two live bounds checks**:

```
cmp    $0x1000,%rcx          # the write index < SCR ?
ja     <panic>
lea    -0x1(%r8),%rax
cmp    $0x1000,%rax          # the read index < SCR ?
jae    <panic>
movzbl (%r9,%r8,1),%eax
mov    %al,0x27(%rsp,%r8,1)
dec    %r8
mov    %rsi,%rax
add    %r8,%rax
jne    <top>                 # 11 instructions / 1 byte
```

### 3b. The gap, attributed by construction — residual −4.00 Ir per call

Each rung built again with **only its move loop deleted**, and again with **only
its fold deleted**, by exact-string substitution with a hit-count assertion
(`.temp/p08/r2decomp.py`); marginal Ir per call by the same differencing method.

```
=== small  m=498 d=251 moved=982 B ===
  safe_naive  total   18264.16   moves  11113.94 (11.3177 Ir/moved byte)   fold  2891.35 (5.8059 Ir/folded byte)
  safe_tuned  total    7334.16   moves    183.94 ( 0.1873 Ir/moved byte)   fold  2890.35 (5.8039 Ir/folded byte)
  unsafe      total    7308.16   moves    157.94 ( 0.1608 Ir/moved byte)   fold  2887.35 (5.7979 Ir/folded byte)
  R2-R4 total   10956.00  = moves   10956.00 + fold  4.00 + residual  -4.00
  R3-R4 total      26.00  = moves      26.00 + fold  3.00 + residual  -3.00
=== large  m=4089 d=2045 moved=8170 B ===
  safe_naive  total  120110.56   moves  91979.00 (11.2581 Ir/moved byte)   fold 23536.68 (5.7561 Ir/folded byte)
  safe_tuned  total   29079.56   moves    948.00 ( 0.1160 Ir/moved byte)   fold 23535.68 (5.7559 Ir/folded byte)
  unsafe      total   29053.56   moves    922.00 ( 0.1129 Ir/moved byte)   fold 23532.68 (5.7551 Ir/folded byte)
  R2-R4 total   91057.00  = moves   91057.00 + fold  4.00 + residual  -4.00
  R3-R4 total      26.00  = moves      26.00 + fold  3.00 + residual  -3.00
```

**Read the per-byte rates as averages, not as the exact constants p16/p17/p05
quote.** `.memory/03-measurement.md` requires a *rate* to come from a
zero-residue lag pair; these come from one input's component total divided by its
byte count, so each carries that component's per-call constant. On `large` that
constant is ~25 Ir out of 23536 (0.1%), on `small` ~25 out of 2891 (0.9%) — which
is exactly why the fold reads 5.7551 on `large` and 5.7979 on `small` where the
true steady-state body is 23 instructions per 4 bytes = **5.75 exactly**. The
*differences* (R2−R4, R3−R4) are not affected, because the constants cancel.

Three things follow, and they are the finding:

1. **100% of R2's gap is the move**, on both bands, with a residual of −4.00 Ir
   per call. There is no interaction term and nothing leaks into the fold: the
   source-level isolation survives codegen. That is a stronger form of
   attribution than p02's, p16's or p05's, all of which had to establish it after
   the fact.
2. **The fold is the same in all three rungs**, 5.7551 Ir per folded byte on
   `large` — which is p16's, p17's and p05's 5.75 constant for rustc's
   4×-unrolled Horner byte fold, reproduced on a fifth kernel. **Safe indexing
   costs zero there**, and for a structural reason rather than an optimiser's
   goodwill: `m = min(avail, SCR)` bounds the index by the scratch's
   *compile-time* length, so the check is provably dead and LLVM removes it.
   c-clang emits the identical fold body.
3. **R2's move rate is 11.26–11.32 Ir per moved byte**, against R4's 0.113–0.161
   and R3's 0.116–0.187. Do **not** round this to the 10.0000 constant p16, p17
   and p05 measured for a checked indexed byte fold — the loop here does a
   checked *read and a checked write* per byte, not a checked read, and the four
   unrolled copies of it are 11, 10, 12 and 12 instructions long. 11.26 is what
   it is.

### 3c. R3 − R4: a provably dead range check per round, and it is LINEAR

R3 and R4 differ by 37 static instructions and **26.00 Ir per call, flat in `m`
and flat in the number of bytes moved** — 6.5 Ir per round. The mechanism is
visible in the normalised diff, once per round:

```
mov  %rbx,%rdx        # rdx = m
sub  %rbp,%rdx        # rdx = m - dr        (the count)
cmp  $,%rdx           # count <= SCR ?
ja   <slice_index_fail>
mov  $,%eax           # eax = SCR
sub  %edx,%eax
cmp  %eax,%ebp        # dr <= SCR - count ?
ja   <panic>
```

`copy_within` re-derives "the source range is inside the slice" and "the
destination range is inside the slice" on **every one of the four rounds**, and
neither can fire: the kernel's own guard gives `d + nrep <= m` hence
`dr <= m − 1`, and `m = min(avail, SCR)` gives `m <= SCR`, so
`dr + (m − dr) = m <= SCR`. The panic is dead on every execution the benchmark
performs, and the checksums prove it.

**That sharpens p05's finding rather than repeating it.** On p05 the implication
the optimiser could not prove was genuinely *nonlinear*
(`nrow*ncol <= avail ⟹ i*ncol + j < avail`), and the conclusion drawn was
"safety's cost is the compiler's incompleteness at nonlinear arithmetic". Here
**every step is linear** — `dr <= m − 1`, `m <= SCR`, therefore
`dr + count <= SCR` — and LLVM still keeps the check. So p05's conclusion is not
the general one: the residual cost here is not the optimiser failing a lemma only
a verifier can prove, it is the optimiser failing a lemma it *could* prove, and
does not, because the facts arrive through a `cmov` (the `min`) and a guard in a
different basic block.

At 26 Ir per call it is 0.36% of `small` and 0.09% of `large`, and **−1.3% in
wall clock**, so this is a mechanism worth naming and not a cost worth worrying
about.

### 3d. What R4 pays over C, and why the trusted base is one item

p08's `unsafe.rs` uses `unsafe` **only for the move**. The header decode is
`buf[off]`, the copy-in is `copy_from_slice`, the fold is `scr[j]` — all safe.
Measured against the same-backend C column:

| | small | large |
|---|---:|---:|
| c-clang | 7293.60 | 29038.18 |
| R4 unsafe | 7308.16 | 29053.56 |
| **R4 − c-clang** | **+14.56** | **+15.38** |

**~15 instructions per call, flat**, is the whole price of writing everything
except the move in safe Rust — 0.2% of `small` and 0.05% of `large`, and below
the wall-clock noise floor. It is why p08's TCB needs no `get_unchecked`: the
element accessor every earlier pattern had to trust buys nothing here.

(gcc's fold is the **rolled** 8-instruction form at exactly 8.00 Ir/byte — the
same gcc default p16 and p17 measured — which is why c-gcc costs 34805 against
c-clang's 29038 on `large`. On `small` the ranking inverts, and §4 explains why
that inversion is an artefact of the measurement rather than of the code.)

---

## 4. Wall clock, and the memset's share

`taskset -c 3`, 31 reps, cells round-robin interleaved, **per-call time obtained
by differencing `n_iters`** (25 000 → 75 000 on `small`, 8 000 → 24 000 on
`large`) so that process start-up, the 32 MiB file read and the payload decode
cancel exactly. `.memory/03-measurement.md`: never divide a total wall time by a
count. Worst min-to-median spread over all 32 sample sets: **2.3%**, well inside
the 10% discard threshold; nothing is discarded.

| rung | `small` ns/call (min) | `large` ns/call (min) | Δ vs R4 (`large`) | Δ Ir vs R4 (`large`) |
|---|---:|---:|---:|---:|
| c-gcc | 452.75 | 3670.08 | +3.8% | +19.8% |
| c-gcc-h | 449.72 | 3539.37 | +0.1% | +19.8% |
| c-clang | 440.01 | 3527.73 | −0.3% | −0.1% |
| c-clang-h | 441.02 | 3492.81 | −1.3% | −0.1% |
| **R2 safe-naive** | **1022.11** | **8136.58** | **+130.0%** | **+313.4%** |
| R3 safe-tuned | 442.07 | 3491.81 | **−1.3%** | +0.09% |
| R4 unsafe | 441.77 | 3537.16 | — | — |
| R5 verus | 442.58 | 3576.07 | +1.1% | 0.0% |

**The noise floor is measured, not asserted: R4 and R5 are byte-identical
machine code and differ by +1.1%.** Every Δ smaller than that in the table —
which is all four C rows and R3 — is noise, and that is the correct reading of
"R1h is faster than R1".

**R2: +313% instructions became +130% time.** `Ir` overstates by 2.4×, because
R2's cost is a rolled byte loop whose two bounds compares are predicted and dual-
issued while the loads and stores are the real work. That is the p16 direction
(+72% Ir → +0.27% time) in a much milder form, and it is the opposite of p05
(+34.4% Ir → +32.9% time). **Three patterns, three conversion ratios — `Ir` is
not a time model and this is the third demonstration.**

### 4a. The memset's share — the manager asked for this one specifically

The task says: *"Report the memset's share of per-call `Ir` — if it is over ~20%
and swamps the move, stop and tell me."* It is over 20% in `Ir` under clang, and
it is **not** over 20% in time, and the gap between those two statements is the
interesting part. Components measured by deleting one at a time
(`.temp/p08/decompose.py`, `.temp/p08/wall_decomp.py`), `small`:

| component (bytes) | c-gcc Ir | c-clang Ir | c-gcc ns | c-clang ns |
|---|---:|---:|---:|---:|
| memset (4096) | 518.00 — **10.7%** | 4121.00 — **56.5%** | 21.10 — **4.7%** | 24.68 — **5.6%** |
| copy-in (498) | 87.44 — 1.8% | 88.32 — 1.2% | — | — |
| **the moves (982)** | 229.00 — 4.7% | 157.98 — 2.2% | 13.74 — **3.1%** | 6.18 — **1.4%** |
| the fold (498) | 3996.44 — 82.1% | 2887.44 — 39.6% | 392.10 — 87.5% | 392.49 — 89.4% |

**The 56.5% is an `Ir` artefact and the cause is nameable.** glibc's `memset`
uses `rep stosb` for 4 KiB, and **callgrind counts a `rep`-string instruction
once per iteration**, i.e. once per byte: 4121 Ir for 4096 bytes = 1.006 Ir/byte.
gcc does not call libc at all — it inlines `rep stos %rax`, 8 bytes per
iteration, 518 Ir = 0.126 Ir/byte. The hardware retires both at tens of bytes per
cycle, so in **time** the memset is 4.7% / 5.6% of the call in both, and the 8×
`Ir` difference is worth **3.6 ns**.

Two consequences, and both are general:

- **The memset does not swamp the move in the currency that matters**, so the
  design stands unchanged. In `Ir` it does, under clang, and a report that quoted
  only `Ir` would have said so.
- **`rep`-string instructions make callgrind `Ir` and wall clock disagree in
  *direction*, not just in magnitude.** On `small`, `Ir` says c-gcc (4865.72) is
  **33% cheaper** than c-clang (7293.60); wall clock says c-gcc is **dearer**.
  **Quote the direction, not this delivery's magnitude.** The delivered figure
  was "2.9% dearer (452.75 vs 440.01 ns)"; TASK_014_REVIEW re-measured it
  independently (21 reps, `taskset -c 3`, differenced `n_iters` 25 000 → 75 000)
  at **448.16 vs 442.44 ns = +1.29%**, against a same-session noise floor of
  **+0.37%** taken from R4 vs R5 (442.76 vs 444.40), which are byte-identical
  kernels and so should read 0. So the direction reproduces and is 3.5× the
  floor; the 2.9% was 2.2× over-precise. A magnitude on this box needs its floor
  printed beside it (`.memory/00-environment.md`: the clock is set by other
  tenants). The entire inversion is `rep stos` +
  `rep movsq` in the gcc kernel being counted at one instruction per iteration.
  `.memory/03-measurement.md` already records one direction-disagreement (p02,
  gcc −10% Ir / +23% time); **this is a second, with a named mechanism, and it is
  a reason to distrust any `Ir`-only comparison between a `rep`-string build and
  a libc-call build.**

`large` time shares, same method:

| component (bytes) | c-gcc Ir | c-clang Ir | c-gcc ns | c-clang ns |
|---|---:|---:|---:|---:|
| memset (4096) | 518.00 — 1.5% | 4121.00 — **14.2%** | 43.68 — 1.2% | −35.93 — **−1.0%** |
| copy-in (4089) | 534.28 — 1.5% | 422.18 — 1.5% | — | — |
| **the moves (8170)** | 993.00 — 2.9% | 921.98 — 3.2% | 79.75 — 2.3% | 10.50 — 0.3% |
| the fold (4089) | 32722.28 — 94.0% | 23531.22 — 81.0% | 3154.70 — 89.4% | 3149.23 — 89.8% |

Same shape, one band larger: the memset is **14.2% of the clang call in `Ir` and
−1.0% in time** (a negative delta is how a component smaller than the noise floor
reads — the spreads here are 0.9–1.8% of ~3500 ns, i.e. ±40 ns, and the memset is
worth about that). The move is **2.9–3.2% in `Ir` and 0.3–2.3% in time** — the
same order in both currencies, and near the resolution of the wall-clock
measurement in both C cells. R2's move is **57.4% of its call in time** on
`large` (57.6% on `small`), which is the only component in this pattern whose
share is large in *both* currencies.

**So the answer to "ns as primary where the move dominates" is that the move
never dominates**, in either currency, in any correctly-written rung: 2–3% of
`Ir` and 0.3–2.7% of ns. It dominates only in R2, where it is not a move at all
but a checked byte loop. What dominates everywhere is the **fold**, at 81–94% of
`Ir` and 89–90% of ns, which is `.memory/02-bench-rules.md`'s "when a pattern's
scaffolding dominates its kernel, say so at the top of `NOTES.md` and quote the
marginal column" — said here, with the marginal column quoted throughout.


### 4b. Cycles are not quoted, and the probe says why

The dependent-`addq` clock probe was made a participant in the same round robin,
one 40 M-iteration window after every rep:

```
clock probe, INTERLEAVED with these reps (dependent addq, 40 M iters, cpu 3, 31 reps):
  min 1300 MHz  median 3730 MHz  max 3807 MHz
```

The median agrees with TASK_013's interleaved measurement (3236 / 3732 / 3816)
and the spread is worse. **No cycles/byte figure is quoted for p08**, per
`.memory/00-environment.md`: ns is a measurement on this box and cycles is an
inference with a ±15% band even when the clock is measured correctly.

*(Recorded because it is the kind of mistake that reproduces: the first version
of this probe used `volatile uint64_t s; s += 1;`, which is a store-to-load round
trip rather than a register chain, and reported **688 MHz**. A "clock probe" that
measures store-forwarding latency looks exactly like a clock probe. The shipped
one is an `addq`/`subq`/`jnz` chain in inline asm.)*

---

## 5. The three controls, and the detection table

All generated by `patterns/p08-overlap-move/controls/gen_controls.py` into
`.temp/p08/controls/` — a committed generator that derives each control from a
shipped source by exact-string substitution and asserts its own hit count, per
`.memory/05-layout.md` demand 11.

### 5a. Control 1 — the borrow-check rejection

Three ways a programmer reaches for `memcpy(scr + dr, scr, m - dr)` in safe
Rust. `rustc --crate-type=lib --edition 2021 borrow_reject.rs` → **exit 1, three
`E0502`s**:

```
error[E0502]: cannot borrow `*scr` as immutable because it is also borrowed as mutable
  --> borrow_reject.rs:27:33
   |
27 |     scr[dr..m].copy_from_slice(&scr[0..m - dr]);
   |     ---        ---------------  ^^^ immutable borrow occurs here
   |     |          |
   |     |          mutable borrow later used by call
   |     mutable borrow occurs here
   |
   = help: use `.split_at_mut(position)` to obtain two mutable non-overlapping sub-slices
```

The other two shapes (naming the two borrows; building them as a tuple) fail the
same way. **rustc's own suggestion is the point and it is worth keeping**:
`split_at_mut` gives two *non-overlapping* halves, which is precisely what an
overlapping move is not. The only safe spelling left is `copy_within` — R3.

This is the one result in this project that costs **zero instructions because the
program does not exist**. No runtime check, no panic path, no landing pad, no
rung.

### 5b. Control 2 — `copy_nonoverlapping` re-opens it, and Miri has teeth

`nonoverlap.rs` is `unsafe.rs` with `core::ptr::copy` →
`core::ptr::copy_nonoverlapping`, one substitution.

- **Native, `-O3`:** prints `17006177784580028288` on `adversarial-overlap` — the
  *correct* answer, same reason as §1. The mutant is undetectable by execution,
  by checksum, and by the gate's step 2.
- **Under Miri:**

```
error: Undefined Behavior: `copy_nonoverlapping` called on overlapping ranges
  --> .temp/p08/controls/nonoverlap.rs:71:9
   |
71 |         core::ptr::copy_nonoverlapping(p, p.add(dr), m - dr);
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Undefined Behavior occurred here
   = note: stack backtrace:
           0: move_right   1: kernel   2: main
```

**This is the first time the gate's Miri stage has been pointed at an *aliasing*
UB rather than a bounds one, and the answer is that it has teeth.** The shipped
`unsafe.rs` is clean on all six inputs (§9); the one-token mutant is caught on
the input where the ranges overlap, and only there. `.memory/02-bench-rules.md`
records Miri as "a UB test, not a proof" — that stands, but on this class it is
the only tool in the box that works on the Rust side.

### 5c. Control 3 — safe, compiles, does not panic, and wrong

`fwd_loop.rs` is `safe_naive.rs` with `for j in (0..m - dr).rev()` →
`for j in 0..m - dr`, one substitution. Zero `unsafe`, zero UB, zero panics:

| input | `fwd_loop` | every shipped rung | model |
|---|---|---|---|
| `adversarial-overlap` (ranges overlap) | **4507432511443086080** | 17006177784580028288 | 17006177784580028288 |
| `small` (`d >= m/2`, no overlap) | 5963384295905503290 | 5963384295905503290 | 5963384295905503290 |

**Safe Rust prevents the undefined behaviour; it does not prevent the bug.**
Write the loop in the wrong direction and the buffer is replicated instead of
shifted — safely, silently, exit 0, and only on inputs the attacker controls. A
write-up that says "Rust fixes this" without this row is overclaiming, and this
project has done that four times already.

Note what the direction costs at R5: the verified twin `slb_twin_move_right`
would **not verify** written forward, because its invariant says indices `[0, j)`
are still original and the read `v[j - dr]` is licensed by exactly that. The
value-level bug and the proof-level obligation are the same fact.

### 5d. The detection table

Which tools can see R1's overlapping `memcpy`, and R4's `copy_nonoverlapping`
mutant. `.temp/p08/controls/detect.sh` builds the first four rows.

| tool | R1 `memcpy` on `adversarial-overlap` | R4 mutant `copy_nonoverlapping` |
|---|---|---|
| plain execution, all 8 cells | **correct answer, exit 0** (§7) | correct answer, exit 0 |
| **gcc ASan+UBSan, `_FORTIFY_SOURCE=3`** (= `check.py` stage 7) | **SILENT, exit 0** | n/a (C only) |
| gcc ASan+UBSan, `-D_FORTIFY_SOURCE=0` | **`memcpy-param-overlap`, exit 1** | n/a |
| clang ASan+UBSan (no default fortify) | **`memcpy-param-overlap`, exit 1** | n/a |
| valgrind memcheck | **cannot run on this box at all** | — |
| **Miri** | n/a (C only) | **`Undefined Behavior: copy_nonoverlapping called on overlapping ranges`** |

Three of those rows are findings rather than table entries.

**(i) ASan catches overlap, and RECAP / `.memory/06-catalogue.md` say it does
not.** They are wrong; the manager suspected as much and asked for it to be
settled. `AddressSanitizer: memcpy-param-overlap` is a real interceptor check and
it is **exact to the byte**: at `m = 4092`, `d = 2045` (a two-byte overlap) it
fires; at `d = 2046` (ranges exactly adjacent) and `d = 2047` it is silent.

**(ii) `_FORTIFY_SOURCE=3` disables it.** Same source, same flags, one
difference:

```
=== (1) gcc, _FORTIFY_SOURCE=3 (this box's default; check.py stage 7) ===
  exit=0
  kernel calls:  1 <__interceptor_memcpy>   1 <__memcpy_chk@plt>
=== (2) gcc, -D_FORTIFY_SOURCE=0 -- the ONLY difference ===
  exit=1
  ==3625209==ERROR: AddressSanitizer: memcpy-param-overlap: memory ranges
      [0x7f69dd800023,0x7f69dd801019) and [0x7f69dd800020, 0x7f69dd801016) overlap
      #0 ... in __interceptor_memcpy
  kernel calls:  2 <__interceptor_memcpy>
```

At fortify level 3 gcc rewrites the move to `__memcpy_chk` (the destination
`scr + dr` has a computable `__builtin_dynamic_object_size` of `4096 − dr`), and
**ASan's overlap check lives in its `memcpy` interceptor, not in
`__memcpy_chk`**. A hardening feature disables a sanitiser check.

Two consequences. For a reader: *do not conclude from a clean ASan run that a
`mem*` call is well-formed unless you know the call was not fortified away.* For
this project: **`harness/check.py` stage 7 builds with gcc only, and this box's
gcc is fortified by default, so stage 7 is structurally blind to any `mem*` /
`str*` misuse whose call site gcc rewrites to a `_chk` form.** That is a harness
observation and it is reported rather than worked around — `model.py`'s
`sanitizer_expect` returns `"clean"` for every p08 input *and its docstring says
exactly why, with the isolating experiment*, and the security evidence lives in
this table. If stage 7 ever gains `-D_FORTIFY_SOURCE=0` or a clang column, that
property must become `"fires" if self.any_overlap else "clean"`; the overlap
predicate is computed and kept in `model.py` for exactly that reason.

**(iii) valgrind memcheck cannot be run on this box.**
`.memory/00-environment.md` lists valgrind as installed, which is true of
**callgrind** and not of memcheck:

```
valgrind:  Fatal error at startup: a function redirection
valgrind:  which is mandatory for this platform-tool combination
valgrind:  cannot be set up.  Details of the redirection are:
valgrind:  A must-be-redirected function
valgrind:  whose name matches the pattern:      memcmp
valgrind:  in an object with soname matching:   ld-linux-x86-64.so.2
valgrind:  ... The package you need to install for fix (1) is called libc6-dbg
```

`libc6-dbg` needs root. A statically linked binary *does* start under memcheck,
but `--trace-redir=yes` then shows **3 vDSO redirections and zero `mem*`/`str*`
redirections**, so memcheck's own "Source and destination overlap in memcpy"
check never runs either. Both routes are closed. Callgrind is unaffected and the
gate's use of it is fine.

---

## 6. The proof: 11 obligations, and what each mutant proves

`./verus_run.py patterns/p08-overlap-move/verus.rs` → **`11 verified, 0
errors`**. With `--cfg slb_twin` → **`15 verified, 0 errors`**. Per item, all
measured with `--verify-function <name> --verify-root`:

| item | obligations | why |
|---|---:|---|
| `d_at`, `nrepw_at`, `init_scr`, `shift_round`, `shift_fold` | 0 | non-recursive `spec fn` |
| `shift_rounds`, `fold_scr` | 1 each | recursive: one termination query |
| `move_right`, `copy_in`, `load_input`, `emit` | 0 | `external_body` |
| **`SCR`** | **1** | **a `const` item is its own Verus query — see below** |
| `kernel` | 3 | body + 2 loop bodies, no `by`-block |
| `main` | 5 | quoted as measured |
| `slb_twin_move_right` (`--cfg slb_twin`) | 2 | body + loop body |
| `slb_twin_copy_in` (`--cfg slb_twin`) | 2 | body + loop body |

**A `const` inside `verus!` carries an obligation, and `.memory/04-verus.md`'s
rule of thumb does not mention it** because no earlier pattern declared one.
Measured two independent ways: `--verify-function SCR --verify-root` reports
`1 verified`, and adding a second unrelated `const` to a mirror copy of the file
takes it from 11 to 12. Without that term the decomposition is one short, and a
reviewer re-deriving the pin from `spec.md` alone would think something was
missing.

**`main`'s 5 is quoted as measured**, exactly as on p05 and p17 (whose drivers
are character-identical to this one): body + driver loop + one per `by`-block
would predict 6 and Verus reports 5. p17's `spec.md` asserted the 6-term
derivation as if it were the count; that is corrected as part of this task.

### 6a. Sticking points — there were almost none, and that is the finding

**The proof verified first try.** Worth recording for the next pattern that wraps
a bulk-memory primitive:

> **The trusted `ensures` is three conjuncts over three disjoint index ranges
> that *partition the buffer*, and the step that turns them into the spec
> function is one `=~=`.** `assert(scr@ =~= shift_round(s0, dr, m))` after the
> call is the whole proof of a round; the loop invariant
> `scr@ == shift_rounds(init, d, m, r)` then unfolds by definition. No lemma, no
> `by (nonlinear_arith)`, no arithmetic difficulty at all — p05's was harder by a
> wide margin, and the reason is that a *move* is a permutation of indices while
> a *flattened 2-D index* is a product.

Three things did cost time, all mechanical rather than mathematical:

- **`&mut [u8; SCR]` fails the gate; `&mut [u8]` does not.** The natural
  signature for a fixed scratch is the array. With it, vstd's
  `array_len_matches_n` gives `v@.len() == SCR` from the type, so there is **no
  non-tautological precondition to state about `v` at all** — and `check.py`
  stage 5a's parameter-coverage rule fails outright: *"trusted item `move_right`
  demands ['0 < dr <= m', 'm <= SCR'] of its callers, which constrains nothing
  about ['v']"*. **This is the first false positive of that rule found in the
  tree.** `.memory/04-verus.md` predicted a different family — "a pure *value*
  parameter legitimately needs no precondition; nothing in the tree exercises it
  yet" — and this is a second: *a parameter whose type already fixes everything
  there is to say about it*. The way past it is to take a slice, which makes
  `m <= old(v)@.len()` a real constraint.

  **That is a workaround, not a fix, and the first draft of this bullet had it
  backwards** (corrected at TASK_014_REVIEW, measured). It said the widening was
  "a fix rather than a workaround because the slice contract is the more general
  one". The generality is exactly what loses a fact: the array type *carries the
  length*, the slice type does not, so the widened contract is the **weaker** of
  the two — a real-`&mut [u8]` caller cannot prove `v@.len()` survived the call
  (`assertion failed`, `1 verified, 1 errors`) where the array signature gives it
  free (`3 verified, 0 errors`). See §8 (b). p08 gets away with it only because
  its single call site passes `&mut scr` with `scr: [u8; SCR]` and Verus's
  unsizing coercion supplies the length from outside the contract. So: the rule
  as written rejects the more natural *and stronger* signature, the repair costs
  a fact, and a future pattern with a fixed-size trusted buffer will hit it
  again. Stage 5a's rejection is a genuine false positive and is recorded in
  `.memory/04-verus.md`.
- **Three `ensures` conjuncts, not four, and the gate decided it.** The
  commissioning sketch asked for four, including `v@.len() == old(v)@.len()`.
  With it present, step 5c reports *"`move_right` ensures[0] is NOT
  load-bearing: deleting `final(v)@.len() == old(v)@.len()` still gives 11
  verified, 0 errors"*. The only caller passes `&mut scr` where `scr` is a
  `[u8; SCR]`, and Verus's array-to-slice unsizing coercion carries
  `final(out)@ === final(r)@` with the array's length fixed by its type, so the
  length is known at the call site whatever the contract says. A trusted
  `ensures` nothing depends on is an unchecked claim about real Rust semantics
  carried for free, which is what `.memory/04-verus.md` says a trusted item must
  not have. **Three is the measured number**, and the fourth clause was in the
  tree until the gate objected.
- **`nrep_w % 4`, not `nrep_w & 3`.** `&` drags in `by (bit_vector)`; `%` is
  linear. Verified they are the same instruction before choosing: `1 + x % 4` and
  `1 + (x & 3)` both compile to `and $0x3` + `lea` in gcc, clang **and** rustc
  (`.temp/p08/probe/mask.c`, `mask.rs`). `.memory/04-verus.md` blesses exactly
  this trade for the `+`-vs-`|` little-endian decode.

### 6b. Mutants — every one run, with its actual verdict

Generated from the shipped `verus.rs` by exact-string substitution with a
hit-count assertion (`.temp/p08/mkmutants.py`) into `.temp/p08/mirror/`, per
`.memory/05-layout.md` demand 11.

| mutant | what it changes | Verus verdict | what it proves |
|---|---|---|---|
| control | — | `11 verified, 0 errors` | — |
| **M0** | functional spec stripped (`ensures r == r`, consuming `assert` deleted) | `11 verified, 0 errors` | the **negative control** for M1b |
| **M1** | **the bounds guard deleted from the exec code**, spec untouched | `10 verified, 1 errors` — *invariant not satisfied before loop*, at `0 < d` and `d + nrep <= m` | deleting the guard fails a **memory-safety** obligation: the trusted `requires` can no longer be discharged |
| **M1b** | M1 **and** the functional spec stripped | `10 verified, 1 errors` — **the same** invariant | the **positive control** `.memory/04-verus.md` §2b demands: nothing was hiding behind a functional failure |
| **M2** | trusted `requires` `0 < dr <= m` → `0 < dr <= m + 1`, on the item **and** its twin | **`11 verified, 0 errors`** shipped; **`14 verified, 1 errors`** under `--cfg slb_twin`, *invariant not satisfied before loop* at `dr <= j <= m` | **Verus alone passes the off-by-one; only the verified twin catches it** |
| **M3** | kernel `ensures` tautologised to `r == r` | `10 verified, 1 errors` at the driver's consuming `assert` | the `ensures` is load-bearing, not decoration |
| **M4** | **the third `ensures` conjunct** (`[m, len)` untouched) deleted from the trusted item **and** its twin | `10 verified, 1 errors` at `assert(scr@ =~= shift_round(s0, dr, m))` | **the multi-clause case**: a *missing conjunct* in a trusted `ensures` is caught — the shape `.memory/04-verus.md` says the twin exists for |
| **M5** | the same conjunct deleted from the trusted item **only** | `10 verified, 1 errors`, same assert | the item, not the twin, is what the kernel proof consumes |

M4 and M5 are what gate step 5c does automatically, per clause, on every run —
and note the shout it emits while doing it, because it bounds the claim:

> `!! [clause-mut] verus.rs move_right ensures[1] carries a top-level` `forall`
> `binder, whose body runs to the end of the clause, so this stage refused to
> split it into conjuncts and deleted it whole. A redundant conjunct inside it
> would be undetectable here.`

So 5c certifies that each of the three *clauses* is load-bearing and says plainly
that it cannot see inside a `forall`. That is the right behaviour and it is the
honest limit of the claim.

### 6c. Two mutants through the whole gate

M2 and M4 swapped into `patterns/p08-overlap-move/verus.rs`, `check.py p08
--no-callgrind` run, tree restored (verified by md5:
`2fe915a1756965b8c03c273069d11b01` before and after). `--no-callgrind` forces
the verdict to `PARTIAL` and writes `*.partial.json` rather than clobbering the
full-run record; the `[collapse-ir]` failure in both logs is that flag, not the
mutant. Full logs: `.temp/p08/gate-m2_offbyone.log`,
`.temp/p08/gate-m4_dropconj3.log`.

**M2** — the trusted `requires` weakened by one, on the item *and* its twin: the
"too weak by one" shape `.memory/04-verus.md` calls the most dangerous hole in
the project. **Verus alone is perfectly happy, and three of the four mechanical
checks approve it:**

```
ok   verus.rs: trusted item `move_right` demands ['0 < dr <= m + 1', 'm <= old(v)@.len()']
     of every caller, constraining every parameter its body uses (['v', 'dr', 'm'])
ok   verus.rs: 11 verified, 0 errors -- matches the pinned obligation count;
     4 TCB items, all contracts identical to spec.md          <- (the count does not move)
ok   verus.rs: move_right requires[0] is not a tautology (bare Z3,
     `by (nonlinear_arith)`, `by (bit_vector)`) -- 0 < dr <= m + 1
ok   5 `ensures` conjunct(s) deleted ... every trusted `ensures` conjunct is load-bearing
```

What fails:

```
FAIL [proof-pin] verus.rs:231 `move_right` drifted from spec.md --
    requires: ['0 < dr <= m + 1', ...] != pinned ['0 < dr <= m', ...]
FAIL [proof-pin] verus.rs:271 `slb_twin_move_right` drifted from spec.md -- (same)
FAIL [twin]      verus.rs: with `--cfg slb_twin` Verus reports 14 verified, 1 errors
                 (11 verified without the twins). At least one trusted precondition is
                 not strong enough to license the checked equivalent ...
  error: invariant not satisfied before loop
     --> patterns/p08-overlap-move/verus.rs:284:13
      |
  284 |             dr <= j <= m,
```

The `spec.md` pin catches it because the mutation is a source diff a reviewer can
read; **the twin catches it semantically**, and the twin is the only mechanism
that would still object if the pin had been edited in the same commit — which is
the self-certification failure TASK_003_REVIEW demonstrated. 5c-req's own log
line says so: *"this stage judges TRIVIALITY, not STRENGTH"*.

**M4** — the third `ensures` conjunct deleted from the trusted item and its twin.
**14 failures**, and note that the *first four* are build failures, because
`verus_run.py --compile` refuses a file Verus reports errors on, so the cell
cannot even be produced:

```
FAIL [build]        verus O0 isolated / O0 whole / O3 isolated / O3 whole
FAIL [proof-pin]    verus.rs:231 `move_right` drifted from spec.md -- ensures: [2 clauses]
                    != pinned [3 clauses]
FAIL [proof-pin]    verus.rs:270 `slb_twin_move_right` drifted -- (same)
FAIL [proof-verify] verus.rs: 10 verified, 1 errors
FAIL [proof-rule2]  `verus --verify-function kernel` reports 2 verified: Verus has no
                    verified body for `kernel`
FAIL [clause-mut]   the UNMUTATED copy does not verify (10 verified, 1 errors)
FAIL [req-mut]      ...same
FAIL [twin]         with `--cfg slb_twin` Verus reports 14 verified, 1 errors
FAIL [driver]       verus.rs: the driver region sits inside something spelled `verus!`,
                    but Verus never verified this file
FAIL [miri]         no identity measurement for the R4/R5 pair ... so the Miri policy
                    cannot be evaluated
```

The `[proof-verify]` failure is the kernel's own `assert(scr@ =~= shift_round(s0,
dr, m))`: without the third conjunct the proof cannot know the bytes above `m`
survived the move, so the whole-sequence equality is unprovable. The
`[driver]`/`[miri]` cascade is the fail-closed design working — a file Verus
refuses gets no ghost-stripping certificate and no identity measurement, so
nothing downstream is evaluated on it.


---

## 7. Adversarial behaviour, per rung — the manifestation table

`n_iters` is 8 on every adversarial input. Every adversarial input is exactly one
window (`n_blob == stride`), so `k` is always 0 and `off` is always 0.

| input | what it declares | c-gcc | c-clang | c-gcc-h | c-clang-h | R2 | R3 | R4 | R5 | model |
|---|---|---|---|---|---|---|---|---|---|---|
| `adversarial-overlap` | `d = 3`, `m = 4089`, `nrep = 4` — every round overlaps by > 4 KiB | `17006177784580028288` | same | same | same | same | same | same | same | `17006177784580028288` |
| `adversarial-dzero` | `d == 0` | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0` |
| `adversarial-dbig` | `d + nrep > m` by exactly one | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0` |
| `adversarial-stride3` | stride 3 < the 4-byte header | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0`, zero kernel calls |

**Every one of the eight builds prints the model's answer on every adversarial
input, exit 0, no diagnostic** — including the two R1 cells on the input where
they execute undefined behaviour on every call, and including all four opt/mode
variants of each. `harness/check.py` prints no "opt/mode variants of this rung
disagree" note for any cell, which on p05 it printed for R1 on two inputs.

That is the manifestation table the task asked for, and the answer is uniform:
**no build of R1 gets it wrong.** Against the three earlier bug patterns:

| | R1's harm | how it shows |
|---|---|---|
| p16 | unbounded walk | SIGSEGV; ASan `heap-buffer-overflow` |
| p17 | signed index runs backwards | in-bounds read of a neighbour's bytes; ASan clean |
| p05 | reads `nrow*ncol` past the end | four *different* wrong answers from four builds |
| **p08** | **overlapping `memcpy`** | **nothing. The right answer, everywhere.** |

The security half of p08 is §5d's detection table, not this one.

---

## 8. The trusted base

**TCB: 10 lines across 4 items.** Every `external_body` item is counted, not just
the interesting one (`.memory/04-verus.md`: the pilot was published as "one
3-line wrapper" and the true tally was three items, one of which was `main`).

| item | lines in body | contains `unsafe` | `requires` | `ensures` | why it is trusted |
|---|---:|---|---|---|---|
| **`move_right`** | 4 | **yes** | 2 conjuncts | **3 conjuncts** | vstd ships no spec for `core::ptr::copy` |
| `copy_in` | 1 | no | 2 conjuncts | 1 clause | vstd ships no spec for `copy_from_slice` |
| `load_input` | 4 | no | — | none | file I/O and argv are not verifiable |
| `emit` | 1 | no | — | none | `println!` is not verifiable |

`main` is **not** `external_body` — `--verify-function main --verify-root`
reports `5 verified`, so the kernel's precondition is discharged at a real,
verified call site (`.memory/02-bench-rules.md` rule 2). `harness/check.py` 5a
confirms *"scanned for `unsafe` outside a trusted body: ['verus.rs'] +
['common/driver.rs'] (1 token(s) inside a trusted body)"* — **p08's whole rung
contains exactly one `unsafe` token, and it is the pattern.**

`copy_in` is worth a sentence because it is a shape this project has not had: an
`external_body` item **with no `unsafe` in it**. It is trusted only because vstd
has no specification for `copy_from_slice`, so a wrong `ensures` there cannot
license an unchecked access — `copy_from_slice` panics rather than misbehaving —
and the worst it can do is make the functional spec wrong, which step 2 catches.
It is still inside the twin regime and still has a twin, because
`.memory/04-verus.md` keys the regime on `external_body` + a non-empty `ensures`
**or** `unsafe`, which is the shape that can axiomatise a falsehood.

### The twin is NOT idle, for the first time in six patterns

`.memory/04-verus.md` records, of the verified twin: *"Five patterns in (p01,
p02, p16, p17, p05 — all single-clause), the mechanism has never been exercised
on the case it was built for"* — that case being a **multi-clause** trusted
contract, where the archetypal honest mistake is a *missing conjunct* rather than
a weakened one. It says the value "accrues from the first pattern that needs a
multi-clause trusted accessor, which is a property of the *intrinsic being
wrapped* — raw-pointer families p27+".

**p08 is that pattern, nineteen numbers early**, because the intrinsic is
`core::ptr::copy` and a move has three regions:

- `move_right`'s `ensures` has **three conjuncts**, and step 5c shows each is
  load-bearing (§6b M4/M5). Every earlier pattern's `get_unchecked` has one.
- `slb_twin_move_right` is **not a one-liner**: a reverse indexed loop with a
  five-conjunct invariant and 2 obligations of its own, and it has something to
  get right — the direction. A *forward* twin does not verify, which is the same
  fact `fwd_loop.rs` (§5c) demonstrates at the value level.
- M2 is the "too weak by one" shape `.memory/04-verus.md` calls the most
  dangerous hole in the project, and on p08 the twin is again **the only**
  mechanism that catches it: Verus alone reports `11 verified, 0 errors`.

So the standing item in `.memory/04-verus.md` — *"if p27+ arrives and the
accessor is still single-clause, reopen the keep/delete question"* — can be
closed the other way. The mechanism has now been exercised on its design case and
it worked.

Honest caveat in the other direction: **M4/M5 are caught by Verus itself, not
only by the twin.** Deleting a region conjunct breaks the kernel's own
`=~=` step, so an ordinary verification run fails. What the twin uniquely adds on
p08 is still M2 — the *precondition* being too weak — which is the same thing it
uniquely added on p02. The multi-clause `ensures` makes the item *worth* the
scrutiny; it is not what the twin catches.

### SLB-TRUSTED-ARGUMENT verus.rs move_right

**(a) Is the twin's body the right checked stand-in for the unchecked
operation?** Yes, and on p08 this is the first time the question has needed more
than one sentence. The trusted body is `core::ptr::copy(p, p.add(dr), m - dr)` on
`p = v.as_mut_ptr()`; the twin's is the reverse indexed loop
`for j = m-1 down to dr { v[j] = v[j - dr] }`. These are the *same* operation
modulo the check: the standard library documents `ptr::copy` as "copies
`count * size_of::<T>()` bytes from `src` to `dst`. The source and destination
**may** overlap", with the destination receiving the values the source held
before the copy — which is exactly what a high-to-low element loop computes, and
the reason it must be high-to-low is exactly that the ranges may overlap. The
twin does not reach for `ptr::copy` or `get_unchecked` itself (which would re-use
the axiom it exists to check), it is not empty, and it does not `loop { }` — the
three toothless shapes `.memory/04-verus.md` enumerates. The gate re-derives the
substantive half on every run: with a conjunct deleted from the trusted
`requires`, the twin fails, so the checked implementation genuinely needs it
rather than merely coexisting with it.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** **Relative to this pattern's one call site, yes. As a contract
on a general `&mut [u8]`, no — and the first draft of this paragraph claimed
otherwise. Corrected at TASK_014_REVIEW, measured.** The body performs one
unchecked operation, a `memmove` of `m - dr` bytes from `[0, m-dr)` to `[dr, m)`.
The postcondition names `[dr, m)`, `[0, dr)` and `[m, old(v)@.len())` — three
regions that partition **`old(v)@.len()`**, the length the slice had *before* the
call. Nothing in the contract pins `final(v)@.len()`. A caller holding a genuine
`&mut [u8]` therefore cannot prove the length survived: with

```
let n = v@.len();  move_right(v, dr, m);  assert(v@.len() == n);
```

Verus reports `assertion failed` (`1 verified, 1 errors`), where the **array**
signature `&mut [u8; SCR]` this pattern abandoned gives it free from the type
(`3 verified, 0 errors`). p08's kernel verifies only because its single call site
passes `&mut scr` with `scr: [u8; SCR]`, so Verus's unsizing coercion carries the
length in from outside the contract. **The trusted item's contract is complete
only relative to one caller** — say so before cloning it.

Two things this does *not* mean. It is not a soundness hole in p08: Rust gives a
`&mut [u8]` callee no way to change the slice's length, so the missing fourth
conjunct is unfalsifiable and gate 5c is right to delete it as not load-bearing
(no wrong body exists that three clauses admit and four would catch — see §6b).
And it does not make the trusted body's *writes* unconstrained: within
`old(v)@.len()` the three regions still cover every index, so a stray write must
land in one of them and contradict a conjunct. That is the property the blind
spot TASK_009_REVIEW demonstrated
(`let _peek = *v.get_unchecked(i + 1)`) exploits: an `ensures` that mentions
*some* of what the body touches licenses the rest by omission. Here omission is
impossible by construction — add a stray write anywhere in the body and it must
land in one of the three named regions and contradict a conjunct. The one thing
the contract still cannot see is a *read* outside the buffer, and that is what
the `requires` `0 < dr <= m, m <= old(v)@.len()` plus Miri on R4 (§5b, §9) are
for. **Note also what is deliberately NOT in the contract: there is no
non-overlap conjunct, because `ptr::copy` is `memmove` and none is required.
Swapping the body for `copy_nonoverlapping` would make the contract unsound with
no textual change to it — which is why `controls/gen_controls.py` builds exactly
that mutant and runs it under Miri.**

**(c) Does each clause mean the same thing in the shipped configuration as in the
twin's?** Yes, and it is checked mechanically rather than asserted. The only
`#[cfg]`s in `verus.rs` are the two twins' own `#[cfg(slb_twin)]`, and gate stage
5c-twin verifies that before it runs Verus at all — the token `slb_twin` occurs
nowhere else in the file or anything it includes, which closes TASK_009_REVIEW's
`#[cfg]`-varying-`const` bypass (a `#[cfg]`-varying `const` made
`requires in_bounds(v, i)` mean `i < len + 0` in one configuration and
`i < len + 1` in the other). **There is no named constant in either clause set at
all** — every clause is built from the parameters `v`, `dr`, `m` and from
`old(v)@.len()`, so there is nothing for a configuration to change even if one
could. `SCR` appears in the *kernel*, not in the contract, is not `#[cfg]`-gated,
and carries its own Verus obligation, so both pinned counts (11 and 15) move if
it changes.

### SLB-TRUSTED-ARGUMENT verus.rs copy_in

**(a) Is the twin's body the right checked stand-in for the unchecked
operation?** Yes. The trusted body is
`dst[..n].copy_from_slice(&src[from..from + n])` and the twin's is the indexed
loop `for j in 0..n { dst[j] = src[from + j] }`. `copy_from_slice` is documented
as an element-wise copy that panics if the two slices differ in length, so the
loop is its checked counterpart by construction. Note the asymmetry with
`move_right` and it is the interesting part: **this item's body contains no
`unsafe` at all**. It is `external_body` only because vstd ships no specification
for `copy_from_slice` (`.memory/04-verus.md`), so the bulk copy every other rung
writes has no verified spelling. That the twin *verifies* is what rules out the
false-failure reading — if it failed for want of a library spec rather than for
want of a precondition, the stage would be worse than useless.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes. The single clause is an equality on the **whole**
destination sequence — `src@.subrange(from, from+n) + old(dst)@.subrange(n,
old(dst)@.len())` — so it constrains every index of the buffer, exactly as
`.memory/02-bench-rules.md`'s worked p02 example prescribes ("stating it over the
prefix only would have proved the easy half"). There is no second write, no read
of `dst` before the write, and no arithmetic on `from` or `n` inside the body.
The bound on what a mistake here could cost is also unusually tight and worth
stating: because the body is safe code, a wrong `ensures` cannot license an
unchecked access — `copy_from_slice` panics rather than misbehaving when the
lengths disagree — so the failure mode is a wrong functional specification, which
the model checksum in gate step 2 would catch on the first input.

**(c) Does each clause mean the same thing in the shipped configuration as in the
twin's?** Yes, for the same mechanically checked reason as `move_right` above:
the token `slb_twin` appears only on the two twins' own attributes, so the two
configurations differ in nothing but the twin items. **There is no named constant
in this clause set either** — every clause is built from the parameters `src`,
`from`, `dst`, `n` and from `old(dst)@.len()`. `subrange`, `+` on `Seq` and `=~=`
are vstd operations with one meaning.

---

## 9. Miri, identity, and the gate

**R4 ≡ R5, byte-identical, at BOTH optimisation levels.** `md5_fn =
9259612a652d` for both at `-O3 isolated` (168 static instructions, 166
padding-excluded, 15 B padding each) and `7bbb6ae949ad` at `-O0`; `md5_raw` equal
in both cases too. The `spec.md` pin says `norel` at `-O0` and the gate reports
*"exact (stronger than pinned)"* — the pin is deliberately the weaker claim,
because `-O0` identity between two crates whose names differ in length rests on
call displacements, and pinning the stronger one would turn a benign relink of
`common/driver.rs` into a red gate reading as "the proof cost something"
(`.memory/03-measurement.md`).

**This is the first time on this project that the byte-identity result covers a
multi-clause trusted contract and a non-trivial verified twin** — three `forall`
conjuncts, a five-conjunct loop invariant in the twin, 4 extra obligations under
`--cfg slb_twin` — and all of it erases.

**Miri: 6 of 6 inputs, no UB.** Required because the pattern has trusted items,
not because R4 ≠ R5. Cost is 4 iterations × ~20 KB of scratch traffic per call,
far inside the ~3 M budget, so nothing blocks — an `inputs/gen.py` decision made
before the build, per `.memory/05-layout.md` demand 8. The one-token
`copy_nonoverlapping` mutant **is** caught (§5b), which is what makes the clean
rows meaningful rather than vacuous.

**`harness/check.py p08`: complete green run**, 32/32 cells, 0 failures,
`results/gate/p08-overlap-move.json` with `complete_run: true`.

The `Ir` floor: derived, **125.5 (small) / 1023.2 (large)** Ir per call from
`work_per_call = stride` × the harness default 0.25, with measured marginal Ir
**4858 … 662986** over 64 cell/probe pairs — *"tightest margin 26.9×"*, i.e. this
stage tolerates a 96% loss of work before it objects, with `d(Ir)/d(work)` 5.68 …
161.19. `model.py` declares no `min_ir_per_work`, and the argument for the
default is p16's and p17's rather than p05's: **the fold is a serial Horner chain
with a 3-cycle loop-carried dependence and no vector form** — measured at 5.755
Ir per folded byte (§3b), 23× the floor. Note the direction of the
`work_per_call` estimate: **loose, p17's direction, by 12.1× on `small` and 5.0×
on `large`**, because the kernel touches its 4 KiB scratch four times over while
the unit counts the window once. `model.py`'s docstring has the table.

---

## 10. What is *not* claimed, and what is left open

- **No claim rests on an `O0` row**, and none on a cycles figure (§4b).
- **The perf rows do not execute the bug.** `small` and `large` choose
  `d >= ceil(m/2)` so no round overlaps; that is deliberate (`spec.md`), it is
  what makes the eight cells comparable, and it means §2's "the fix costs zero"
  is measured where `memcpy` and `memmove` are the same call *semantically* as
  well as the same function. On `adversarial-overlap` they are still the same
  function, which is §1.
- **"R2, R3 and R4 differ in one function body" is a claim about the source, and
  §3b is what makes it a claim about the codegen.** The measured residual is
  −4.00 Ir per call on both bands. It could have failed: inlining R2's byte loops
  could have changed what LLVM did to the shared fold, and it did not (5.798 vs
  5.755 Ir/folded byte across the three rungs).
- **The memset is 56.5% of the clang call in `Ir` and 5.6% in time.** The task's
  ">20% and swamps the move" threshold is crossed in one currency and not the
  other; the design is unchanged and §4a has both numbers and the mechanism.
- **`m = SCR` is never exercised.** Every shipped input has `avail < 4096`, so
  the `min` always takes `avail`. The clamp is in the kernel so the kernel is
  total; no input measures it. Likewise `len < 4` (the driver guarantees
  `stride_w >= 4`) and `m < 2` (with `d >= 1, nrep >= 1`, `m <= 1` already fails
  `d + nrep > m`).
- **Nothing is written into the space the move opens.** A real encoder would
  write the framing header there; that is a second bounded loop and adds nothing
  to the aliasing axis. Recorded rather than silently omitted.
- **The twin's unique catch on p08 is still M2, not M4.** §8 says so explicitly;
  the multi-clause `ensures` is what makes the item worth scrutinising, not what
  the twin uniquely finds.
- **No hardware counters.** IPC, branch misses and cache misses are unmeasurable
  on this box and are not estimated.
- **`work_per_call` is still an author-written knob**, and here it errs loose by
  5–12×. §9, and `.memory/02-bench-rules.md`'s standing residual.
