# p10 — weighted FIR / sliding-window stencil: notes

Built at TASK_057. `spec.md` is the contract; this file is the evidence.

**REVIEWED AND CORRECTED.** `.tasks/TASK_057_REVIEW_REPORT.md` is the adversarial
pass; TASK_059 landed it. The measurement layer reproduced **exactly** — every
fitted law, control figure, pad count, loop-body count and the whole Verus layer,
with 21 clean negatives — and **fourteen interpretive claims were retracted.
§14 is the complete list, with what replaced each.** Read §14 before quoting any
figure from an older commit of this file.

---

## 0 — §0: the bug class, the algorithm, and the contract hash

### 0.0 The `slb-contract` sha256, as first written

Recorded before any cell of p10 existed. At that moment the tree held exactly
`spec.md` and `controls/mkcontract.py` — no `.c`, no `.rs`, no `model.py`, no
`inputs/gen.py`:

```
contract_sha256  14667d391a199a47aa671c5255f1dc8276d7d49be3603ea6985a172f826ff5e2
idiom_sha256     066841a95d29c532fb0f980671fed3d9b768d8e7282f4b556cbd65bc590db432
```

Both are printed by `controls/mkcontract.py`; `idiom_sha256` is
`sha256(json.dumps(contract["idiom"], indent=2, ensure_ascii=True, sort_keys=True))`.

**Two entries in this file moved after that, and both are disclosed in §12
with the direction test written out.** The whole-block hash necessarily moved
(the two Verus obligation counts and the `items` map are *measurements* and
cannot precede the proof), which is exactly why the narrower `idiom` hash is
recorded beside it — and that one moved too, once, for a reason §12 states.

### 0.1 `slice::windows` takes a RUNTIME size — verified, not assumed

TASK_057 §3 said *"I believe `slice::windows(size)` takes a **runtime** `size` —
**verify that**, because the whole R3 spelling below depends on it."* It does.
`safe_tuned.rs` compiles with `samp.windows(taps)` where `taps = 2*r + 1` and
`r` is four bytes read out of the input file at run time. There is no
compile-time radius anywhere in p10, so the STOP condition TASK_057 named
("if the fix looks like a compile-time radius, STOP") never arose.

**And `windows` costs no division, where `chunks_exact` would.**
`.memory/03-measurement.md` records that `chunks_exact(n)` with a *runtime* `n`
computes `len − len % n` and lowers to a hardware `div`. `windows` does not:
`grep -c 'div\|idiv'` over the disassembly of all four Rust kernels and both C
kernels at `-O3 isolated` is **0**. That is why `chunks_exact` is `forbidden`
and `windows(` is neither required nor forbidden.

**First use of `windows()` in this project.**
`grep -rn "windows(" patterns/*/*.rs` returned nothing before p10.

### 0.2 The bug class — the catalogue's guess UPHELD, and made conditional

`.memory/06-catalogue.md` says p10's class is *"off-by-one at boundaries"*.
**Upheld**, and it is the second catalogue row to survive (p07's was overturned;
four patterns' have been).

What forced the *shape* of it is the gate, not taste. `harness/check.py` stage 2
(**`check.py::check_checksums`**) requires **every cell including R1** to
print `model.py`'s checksum on every non-`adversarial-*` input; the only
exemption mechanism in the harness is the input filename prefix. So a fencepost
in the output loop — `nout = n − 2r + 1`, the classic width-off-by-one — could
not be shipped: it fires on every well-formed window and R1 would disagree with
the model everywhere.

The bug that survives that constraint, and is still an off-by-one at a boundary:

```c
size_t last = 8 + taps + n - 1;   /* window offset of the LAST sample byte */
if (last >  len) return 0;        /* c/kernel.c            -- THE BUG */
if (last >= len) return 0;        /* c/kernel_hardened.c   -- correct  */
```

`last` is an **index**, so `last == len` is already one past the window. R1
admits exactly that one case and nothing beyond it.

**Rejected candidates, and why. FIVE of them, and they were rejected on
ARGUMENT and not on measurement** — with exactly one exception, and the
exception does not rest on a measurement either: `nout = n − 2r + 1` is ruled
out by a *structural* fact about the harness, **`check.py::check_checksums`**
(it runs every built cell against every non-`adversarial-*`
model input and hard-fails a mismatch), which is checkable by reading the gate
rather than by running it. **TASK_059's own wording — "§0's four rejected
candidates … rejected on measurements" — is wrong on both counts and is
corrected here rather than left standing**; TASK_057_REVIEW m6 found it. The
arguments below are sound and two of them are strong (a clamping bug deletes
`windows()`, hence the whole three-way separation; `hi = n−1` is p07's bug with
a different harm), but none of them was priced.

| candidate | rejected because |
|---|---|
| `nout = n − 2r + 1` (width fencepost in the output loop) | unconditional: fires on every benign input, so R1 disagrees with `model.py` everywhere and gate stage 2 refuses it. |
| edge **clamping** with `if (idx > n) idx = n-1;` (the literal "off-by-one at a boundary") | two branches per tap in every rung. It kills vectorisation, and — fatally — it makes `a.windows(taps)` impossible, which deletes the R2/R3/R4 three-way separation p10 exists for. |
| omitting the length check entirely (p02/p07/p18's shape) | that is a *missing validation*, not an off-by-one, and two patterns already have it. |
| `hi = n − 1` style unsigned underflow | that is p07's bug, and its harm is a wild index rather than one byte. p10 excludes it in **every** rung with the `n < taps` guard, deliberately, so the two C cells stay one character apart. |
| midpoint/`2r+1` **integer overflow** of `taps` | reachable only for `r ≥ 2^31`; every rung computes `taps` at 64 bits and the `n < taps` guard then rejects, so it is unreachable at any window size that fits in RAM. Pinned as `2 * r + 1` in all seven rungs so a `grep` settles it. |

### 0.3 §0's SECOND deliverable: the ALGORITHM

TASK_057: *"if any rung uses a different one, every comparison in the pattern is
void."* **The manager's recommendation — a weighted FIR — is adopted, and I
argue for it rather than merely choosing it.**

A box filter (all coefficients equal) has two forms with different complexity: an
`O(n)` running accumulator (add the entering sample, subtract the leaving one)
and an `O(n·r)` tap loop. Nothing in a *contract* can stop a compiler or a
programmer reaching for the first in one rung and the second in another, and the
`idiom` block cannot pin a complexity. A **per-tap coefficient `w[j]` makes the
incremental form impossible for every rung in every language at once** — there
is no algebraic identity that removes the leaving sample's product from a sum of
differently-weighted terms. So `O(nout · taps)` is honest by construction rather
than by declaration, and the "you pessimised C" objection has no purchase: this
is also the shape real DSP and image code has.

**Checked rather than asserted.** All seven rungs, plus the seven control
variants of `controls/gen_controls.py` that compile (`t_winidx`, `t_1step`,
`t_fold`, `x_sum`, `n_2step`, `u_win`, `b_fence`), agree bit-for-bit with
`model.py` on `small`, `large` and `degenerate`; and gate stage 3b's `d(Ir)/d(work)` runs 2.38…69.90 against a
floor of 0.25, i.e. every cell's `Ir` scales with the tap count. The
disassembly of every cell shows the same `pmullw`-based tap loop
(§1), so no rung found the incremental form.

**The other option — a running accumulator in all five rungs — was rejected for
the reason TASK_057 gave**: it makes the radius stop being a cost parameter,
which deletes §2 and the whole "is the tax proportional to the number of
indexing operations?" question.

**The two hazards TASK_057 asked to be priced before committing:**

1. **No runtime `div` on the output path.** A FIR is normally normalised by the
   coefficient sum; p10 does not normalise at all, sums into a `u32` and folds
   the raw sums. `div`/`idiv` count in every kernel: **0** (§1). The reason is
   `.memory/03-measurement.md:434` — callgrind prices a hardware `div` at **one
   `Ir`**, so a per-output division would be nearly free in the column this
   project publishes and expensive in the one it cannot measure well, and it
   would sit inside every per-tap law p10 fits.
2. **The fold must be able to SEE the bug.** §2.

---

## 1 — the lowering, and the fact that decides the whole pattern

`harness/asm.py stat` on the eight `-O3 isolated` cells reports
`"vector_regs": ["xmm"]` on **all of them**, and
`grep -c 'div\|idiv'` reports **0** on all of them.

**p10's tap loop VECTORISES at `-O3`, in every spelling, including the naive
indexed one.** LLVM's body is seventeen SSE2 instructions covering **eight
samples**, 2× unrolled:

```
movd   -0x4(%r9,%r15,1),%xmm3     movd   (%r9,%r15,1),%xmm4
movd   -0x4(%rcx,%r15,1),%xmm5    movd   (%rcx,%r15,1),%xmm6
punpcklbw %xmm0,%xmm3   punpcklbw %xmm0,%xmm5   pmullw %xmm3,%xmm5
punpcklwd %xmm0,%xmm5   paddd  %xmm5,%xmm2
punpcklbw %xmm0,%xmm4   punpcklbw %xmm0,%xmm6   pmullw %xmm4,%xmm6
punpcklwd %xmm0,%xmm6   paddd  %xmm6,%xmm1
add    $0x8,%r15        cmp    %r15,%rax        jne
```

17 instructions / 8 taps = **2.125 Ir per vectorised tap**, and that number is a
*count off the listing*, not a fitted parameter. It is the `vecit` coefficient
of every LLVM level law in §8 — **17.00, on four cells** — with no free
parameter anywhere.

**And R2's vector loop is the SAME SEVENTEEN INSTRUCTIONS as R4's, in the same
mnemonic sequence**, differing only in register allocation and branch target
(`controls/loops.py`; the full listings are under `.temp/p10/asm/`). ⚠ **Not
byte-identical** — an earlier draft of this file said "byte-identical" and that
was wrong: the register allocation differs. R3's loop is the same seventeen
instructions with the four `movd`s emitted in a different order. The bounds
checks survive only in the **scalar epilogue** that runs `taps mod 8` times per
output.

gcc is different and p10 does not publish a gcc level law: gcc vectorises
**sixteen** samples wide (`movdqu` + `punpckhbw`/`punpcklbw`) and then emits an
**eight**-wide half-block (`movq` + `punpcklbw`) before the scalar tail, so it
has three regimes where LLVM has two. §8b has the five designs tried and the
residuals.

---

## 2 — the fold, and what it can and cannot see

Two quantities are folded and each is load-bearing against a different mutation:

| folded | what it catches |
|---|---|
| the output value `s`, in order (`acc = acc*31 + s`) | a rung that applied the coefficients in the wrong order, dropped a tap, or read the wrong sample |
| `nout`, once at the end | a rung that computed a different **number** of outputs — which is exactly what an off-by-one does |

**How I checked the fold sees p10's own bug**, rather than assuming it (p06's
lesson is that a sum-fold cannot observe a permutation, and the analogue here
would be a fold that could not observe one extra tap):

- **Structurally.** On `adversarial-fencepost.bin` R1h and all four Rust rungs
  return **0** (the guard rejects) while R1 returns a full fold. The difference
  does not depend on the value of the stolen byte at all.
- **By value, with a control.** `b_fence` (`controls/gen_controls.py`) is
  `unsafe.rs` with `last >= len` weakened to `last > len` — the C bug promoted
  into a Rust rung with no bounds check. It reads the same one byte past the
  window, and:

  ```
  adversarial-fencepost   c-gcc 6168683498926031616   b_fence 14981753019345151744
  adversarial-fenceslack  c-gcc 5971305445795263488   b_fence  5971305445795263488
  ```

  On `fenceslack` the stolen byte is a real payload byte and the two agree
  **exactly**; on `fencepost` it is past the allocation and the C `malloc` and
  the Rust `Vec` hold different garbage, so they differ. **That pair is the
  proof that the fold's output is a function of the stolen byte**, not merely
  of the guard's verdict.
- **And `b_fence` agrees with `model.py` on `small`, `large` and
  `degenerate`** — so the divergence really is confined to the boundary case.

---

## 3 — the collapse floor, and why the unit is a TAP

Gate stage 3b, from `results/gate/p10-fir-stencil.json`:

```
probe small.bin  n_iters 100/200 -> +100 kernel calls, work_per_call=576 tap(s)  => derived floor 144.0 Ir/call
probe large.bin  n_iters 100/200 -> +100 kernel calls, work_per_call=2040 tap(s) => derived floor 510.0 Ir/call
ok 64 cell/probe pairs: marginal Ir per call 3253...156022, all above the derived floor
   (tightest margin 14.3x over a declared 0.25 Ir/tap); d(Ir)/d(work) 2.38...69.90
```

**The unit is a tap and not a byte, deliberately.** p10's kernel reads every
sample byte `taps` times and every coefficient byte `nout` times, so a floor
denominated in window bytes would understate the work by a factor of `taps` and
be cleared on every input without testing anything — the "skipping walker
denominated in buffer bytes" shape `check.py` names.

**Which way the estimate errs: EXACT on both probe inputs, LOW elsewhere.**
`model.py` takes the **minimum** over the blob's windows, because the driver's
`k` is pseudo-random and the model cannot know which windows a given `n_iters`
visits. `inputs/gen.py` emits `small.bin` (96 windows, all `n=72, r=4` →
`taps 9`, `nout 64`, **576** taps/call) and `large.bin` (32768 windows, all
`n=136, r=8` → `taps 17`, `nout 120`, **2040** taps/call) with every window
carrying the same `(n, r)`, so the minimum *is* the value for every call. The
two shapes differ in **both** structural parameters, which is what `check.py`'s
`d(Ir)/d(work)` assertion across two probe shapes needs.

`model.py` declares **no** `min_ir_per_work`, so the harness default of
0.25 Ir/tap applies. **The margin is a measurement and not an argument**: p10's
smallest per-tap figure is the 2.125 Ir/tap vectorised body of §1, 8.5× the
floor. That is the *opposite* of p18's justification for the same default —
p18 argued its loop was unvectorisABLE; p10's demonstrably vectorises, and the
floor is cleared anyway.

---

## 4 — R1 vs R1h: what the fencepost costs, measured on both compilers

This is p10's first result and it is a shape no earlier pattern here has.
**Every earlier R1 in this project OMITS a line**, so hardening *adds*
instructions: +5 (gcc) / +12 (clang) per call on p02, `+2.00` per executed pop
on p03, once per input byte on p18. **p10's R1 already executes the comparison
and merely relates its two operands wrongly.**

⚠ **BUT "FREE" IS A MODE- AND DOMAIN-QUALIFIED STATEMENT, AND THE FIRST DRAFT
OF THIS SECTION QUOTED ONE CELL OF A FOUR-CELL TABLE.** `controls/sweep_ir.py`
defaults to `--mode isolated` and TASK_057 published only that column;
TASK_057_REVIEW B2 found it, and the domain half is its M4. **Both are named at
every figure now.** Marginal `Ir` per call (`controls/sweep_ir.py`, differenced
over `n_iters` 2000→6000 on the same blob and the same binary, `-O3`):

Each cell is the **value** of the difference, not a coefficient:

| | `-O3 isolated` | `-O3 whole` |
|---|---|---|
| `c-gcc-h − c-gcc`, every call accepted | **0.00** | **−1.00** — the hardened cell is *cheaper* |
| `c-clang-h − c-clang`, every call accepted | **+1.00** | **0.00** |
| `c-gcc-h − c-gcc`, every call rejected | **0.00** | **0.00** |
| `c-clang-h − c-clang`, every call rejected | **−1.00** — the hardened cell is *cheaper* | **0.00** |

so the swept laws, exact to max |resid| **0.0000** in sample (32 blobs: bands
`r`+`o`+`d`) and **0.0000** out of sample (bands `h`+`e`), are

```
-O3 isolated   c-gcc-h  − c-gcc   = 0
               c-clang-h− c-clang = +1 − 2·rejwin − 2·rejfar
-O3 whole      c-gcc-h  − c-gcc   = −1 + 1·rejwin + 1·rejfar
               c-clang-h− c-clang = 0
```

**On a 100 %-rejecting blob the clang pair therefore reads −1.00 Ir/call at
`-O3 isolated` — the hardened cell is cheaper, not dearer** (`d-allwin.bin`:
c-clang 43, c-clang-h 42). *"`R1h − R1` (clang) = +1.00 flat"* is true only at
`-O3 isolated`, and only where every visited window is accepted. §8b2 has the
column, the design and the refit.

Kernel-exclusive `Ir` (gate stage 3b / `results/p10-fir-stencil.json`,
`-O3 isolated`) agrees with the isolated column: c-gcc and c-gcc-h read
**75,660,000** and **14,782,000** on the two blobs, identically; c-clang and
c-clang-h read 70,280,000 / 70,300,000 and 17,156,000 / 17,158,000, i.e.
**+1.00 Ir/call**. There is no kernel-exclusive column at `-O3 whole` at all —
the kernel is inlined into `main` and has no symbol — which is itself why the
`whole` column can only ever be a whole-program marginal.

**The mechanism, mnemonic by mnemonic** (`harness/asm.py show --raw`, full
kernel diff):

- **gcc — two instructions differ and neither is added.**
  ```
  c-gcc     cmp %rcx,%rax ; jb  <ret0>
  c-gcc-h   cmp %rax,%rcx ; jae <ret0>
  ```
  Same two instructions, operands swapped, condition inverted. **0.00 Ir.**
- **clang — the extra instruction is a `jmp`, not a comparison.** The hardened
  cell's `return 0` path is tail-merged with the normal return, so the success
  path ends `add %rsi,%rax ; jmp <epilogue>` where the unhardened one falls
  straight through into the `pop`s. That `jmp` is the whole of the +1.00.

So: **the fencepost costs at most one unconditional branch on either compiler in
either mode, and no number in the table above is the price of a check** — both
rungs perform the same comparison. The right form of the claim, and the only one
that survives naming the mode and the domain, is:

> **the first hardening in this project whose cost is zero BECAUSE R1 ALREADY
> PERFORMS THE COMPARISON** — 0.00 gcc / +1.00 clang at `-O3 isolated`,
> −1.00 gcc / 0.00 clang at `-O3 whole`, on the accepting domain.

That reason is structural, unlike p08's `R1 ≡ R1h at 0.00 Ir/call`, which is a
**glibc** property and must never be quoted as "memmove is free".

⚠ **And the comparison is LEGAL on every input it is read from.**
`.memory/02-bench-rules.md`'s first rule — never compare cost where the
unhardened rung commits UB or refuses work — rules the R1-vs-R1h cost row out on
p12 and p13. Here `inputs/gen.py` packs every benign window exactly full
(`stride == 8 + taps + n`, so `last == len − 1`), so on every input the cost is
measured on the two rungs take the identical path over the identical bytes. The
only two inputs on which they differ at all are `adversarial-fencepost.bin` and
`adversarial-fenceslack.bin`, and no cost is read off either. **§8b2's `fence`
column is the machine-readable form of that exclusion**: on a call with
`last == len` R1 accepts and every other cell rejects, so no `R1h − R1` law is
fitted there, and the column exists so the boundary is a measured domain rather
than a sentence.

⚠ **THE BUG'S PRICE, ON THE DOMAIN NO p10 INPUT EXERCISES AT SCALE, IS NOT
ZERO** — and it belongs beside "hardening is free" every time that phrase is
used. `controls/gen_domain.py`'s `d-allfp.bin` is crafted so that **every** call
hits the fencepost (`last == len` exactly). Marginal `Ir`/call, `-O3 isolated`:

```
c-gcc   1942.00   against c-gcc-h     62.00
c-clang 1800.00   against c-clang-h   46.00
```

R1 runs the whole tap loop over a stolen byte where R1h returns 0. That is not a
hardening cost, it is the *work the bug does*, and §4's "free" figures are
statements about the benign domain only. (TASK_057_REVIEW measured this first;
reproduced here exactly.)

**No `ns` claim is made for either figure.** §11 has the layout populations: on
`small` the gcc pair reads 254.10 vs 254.47 ns/call at the medians inside
population spreads of 1.9% and 3.1%, and the clang pair 228.97 vs 229.43 inside
1.87% each. Both differences are **inside the noise floor measured on the
population**, which is the honest reading of a +1.00 `Ir` difference on a
~3500 `Ir` call.

---

## 5 — the two guards, and what each one is for

p10 has two guards and they fail in **two different ways**, which is why both
are pinned in every rung including R1:

| guard | what it stops | how it fails without it |
|---|---|---|
| `if (n < taps)` | `nout = n − 2*r` underflowing to `SIZE_MAX` | Verus: `possible arithmetic underflow/overflow`, *before* any index obligation. Mutant `m_nowin`, §10. |
| `if (last >= len)` | the last sample read leaving the window | Verus: the loop invariant `8 + taps + n − 1 < len` fails, and once that is weakened too, `precondition not satisfied` on the trusted accessor's `i < v@.len()`. Mutants `m_fence` / `m_fence3`, §10. |

The first is **not** a memory-safety guard at all — it is an arithmetic one, and
it is what keeps p10 modelling a fencepost rather than p07's wild index. Keeping
it in R1 is what makes the two C cells one character apart.

`taps = 2 * r + 1` is computed at 64 bits in every rung, so a declared radius
near 2³² cannot wrap it into a small one.

---

## 6 — Verus: the proof, the TCB, and one new fact about `usize`

**`10 verified, 0 errors`, on the second attempt.** The first attempt was
`9 verified, 1 errors`; see below.

### 6a — obligations

`10 = u32_at 0 + dotp 1 + fwalk 1 + fir_fold 0 + kernel 3 + main 5`, every term
measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`:

```
u32_at             0 verified   dotp        1 verified   fwalk    1 verified
fir_fold           0 verified   kernel      3 verified   main     5 verified
buf_get_unchecked  0 verified   load_input  0 verified   emit     0 verified
--cfg slb_twin --verify-function slb_twin_buf_get_unchecked  ->  1 verified
```

`kernel`'s 3 is body + **two** loop bodies. **Both p10 loops exit exactly one
way**, so neither needs `invariant_except_break` — a difference from p18, whose
two loops both exit early. `main`'s 5 is quoted as measured and does not
decompose from the command line (the same off-by-one nine other patterns record
for the identical driver).

`twin_obligations = 11` = 10 + 1, one per trusted accessor twin.

### 6b — THE NEW FACT: `global size_of usize == 8;`

**Verus treats `usize` as architecture-independent.** So

```
let taps: usize = 2 * r + 1;
```

with `r` built from four header bytes is

```
error: possible arithmetic underflow/overflow
   --> verus.rs:281:23
    |
281 |     let taps: usize = 2 * r + 1;
    |                       ^^^^^
error: possible arithmetic underflow/overflow      (on `8 + taps + n - 1`)
verification results:: 9 verified, 1 errors
```

— **on a hypothetical 32-bit target**, where `2 · (2³²−1) + 1` really does
overflow. Adding `assert(n <= 0xffff_ffff); assert(r <= 0xffff_ffff);` does
**not** fix it (measured: the asserts themselves verify and the two errors
stand), because the bound that is missing is on `usize::MAX`, not on `n`.

p07 met the identical obligation and dodged it by computing its length check in
`u64` (`4 * (n as u64) + 4 * (nq as u64) > avail as u64`). **p10 cannot take
that route**, because `spec.md` pins the spelling `2 * r + 1` in all seven rungs
and an `(r as u64)` cast would put R5 outside its own pattern's declaration.

One line fixes it:

```rust
global size_of usize == 8;
```

and the file goes to `10 verified, 0 errors`. It is **checked by Verus against
the actual compilation target**, not assumed, so it adds nothing to the TCB —
and the arithmetic above summing to exactly 10 is the check that it carries no
obligation of its own. **This is p10's one genuinely new Verus fact and it is
worth `.memory/04-verus.md`.**

⚠ Once it is in, the two `assert`s above are **dead** — measured both ways,
`10 verified, 0 errors` with and without them — and they were removed. The
surviving comment in `verus.rs` says so rather than leaving a dead line to look
load-bearing.

### 6c — the obligation TASK_057 predicted, and the one that replaced it

TASK_057 said *"the obligations are `r <= i < n - r` plus non-overflow of the
accumulator"*. **The second one does not exist.** `s` is a `u32` accumulated
with `wrapping_add`/`wrapping_mul` and the fold is the project's usual wrapping
Horner chain, so every arithmetic operation on the accumulator is total and
Verus raises nothing. What replaced it is the `n − 2*r` **underflow**, which is
a subtraction obligation discharged by a *guard* rather than by a bound on the
data — and the `usize` width fact above, which nobody predicted.

TASK_057 also warned that *"a runtime radius makes this a nested loop, and
`.memory/04-verus.md` records that `decreases b - a` fails on two-cursor
loops"*. **That hazard did not arise.** p10's loops are not two-cursor: the
outer decreases on `nout − i` and the inner on `taps − j`, each with a single
induction variable and a single exit, and both were accepted on the first try.
The whole proof needs **no lemma**, no `by (bit_vector)`, no `by
(nonlinear_arith)` in the kernel, and two ghost `assert`s that unfold a
recursive spec function at its base case.

### 6d — TCB

**3 `external_body` items, 1 with a `requires`** — the same trusted base as p18,
and the smallest in this project, for the same structural reason: p10's kernel
performs exactly **one** kind of memory access, a byte read of the input window.
There is no scratch, no output buffer, no bulk copy and **no write of any kind**.
The gate's own `tcb_items` for `verus.rs` is **3**; this tally equals it.

**What differs from p18 is that on p10 the one `requires` IS the pattern's bug.**
p18's accessor precondition excluded an out-of-bounds *read* while p18's defect
was an out-of-range *shift*, so the two were about different facts. p10's defect
is an out-of-bounds read and `i < v@.len()` is exactly what excludes it —
demonstrated by mutant `m_fence3` in §10, whose rejection lands on that clause.

```
SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) Is the twin's body the right checked stand-in for the unchecked operation?
    The trusted body is `unsafe { *v.get_unchecked(i) }` and the twin
    `slb_twin_buf_get_unchecked` is `v[i]`, under the identical signature and
    the identical `requires i < v@.len()` / `ensures r == v@[i as int]`. Those
    are the same operation on the same operands, differing only in whether the
    bound is checked at run time: `get_unchecked`'s documented contract in the
    standard library is precisely "if the caller guarantees `i < v.len()`, this
    is `v[i]`". A `requires` too weak to license `*v.get_unchecked(i)` is too
    weak to license `v[i]`, and Verus can see the second one -- which is what
    makes the twin a real test rather than a restatement. It verifies at
    `--cfg slb_twin` (`1 verified`, §6a) and it FAILS when the `requires`
    conjunct is deleted, which gate stage 5c-twin checks by deleting it.

(b) Is the `ensures` COMPLETE with respect to every unchecked operation the
    body performs? The body performs exactly ONE unchecked operation -- a
    single byte load at `i` -- and the `ensures` states the whole of its result,
    `r == v@[i as int]`. There is no second access to leave unspecified, which
    is TASK_009_REVIEW's x4 hazard (a trusted body that also reads `i + 1`
    passes the contract pin, the twin and the `--cfg slb_twin` run unchanged).
    The claim is checkable by reading the three-line body: it contains one `*`,
    one `get_unchecked` and no other expression. p10's kernel writes nothing
    anywhere, so there is also no store to be silent about.

(c) Does each clause mean the same thing in the shipped configuration as in the
    twin's? Both clauses are over `v@` and `i` only -- no `old()`, no `final()`,
    no ghost state, no cfg-dependent name -- and `v@` is `Seq<u8>` in both
    configurations because the parameter type is the same `&[u8]`. `#[cfg(slb_twin)]`
    is a cfg no measured build ever sets, so the twin is stripped by rustc
    before codegen and cannot change the shipped instruction stream; the O3
    `md5_fn` identity between `unsafe` and `verus` (§7) is the evidence that it
    does not.
```

---

## 7 — behaviour: sanitizers, adversarial rows, Miri, identity

### 7a — the adversarial table, per rung

From gate stage 4. All four opt/mode variants of each rung agree, so they are
collapsed here:

| input | c-gcc / c-clang (R1) | c-*-h (R1h) | safe_naive | safe_tuned | unsafe | verus | ASan+UBSan on R1 |
|---|---|---|---|---|---|---|---|
| `adversarial-fencepost` | exit 0, **6168683498926031616** | exit 0, `0` | `0` | `0` | `0` | `0` | **heap-buffer-overflow, READ of size 1** |
| `adversarial-fenceslack` | exit 0, **5971305445795263488** | exit 0, `0` | `0` | `0` | `0` | `0` | **clean** |
| `adversarial-farover` | exit 0, `0` | exit 0, `0` | `0` | `0` | `0` | `0` | clean |
| `adversarial-stride7` | exit 0, `0` | exit 0, `0` | `0` | `0` | `0` | `0` | clean |

**Three distinct harms in three distinct columns:**

1. **`adversarial-fencepost`** — the window is one byte short of the samples it
   declares, and it is the last window in the blob, so the stolen byte is past
   the C driver's `bytes` malloc:
   ```
   ==2144800==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x506000000116
   READ of size 1 at 0x506000000116 thread T0
       #0 ... in kernel patterns/p10-fir-stencil/c/kernel.c:87
   ```
2. **`adversarial-fenceslack`** — the **same window**, with three trailing
   payload bytes that do not form a further window (so `nwin` is still 1 and `k`
   is still 0). The identical off-by-one now reads a byte that is merely the
   *wrong* one. **ASan clean, UBSan clean, exit 0, wrong answer.**
   **Whether a one-byte overread is observable is a property of the ALLOCATION
   and not of the program** — p02's result arriving on the read side at the
   smallest possible magnitude.
3. **`adversarial-farover`** — a window declaring `n = 4000` against 55 bytes.
   **R1 and R1h reject it alike.** An off-by-one buys an attacker exactly one
   byte and nothing more. A clean negative, and it is the row that bounds the
   harm.

UBSan has nothing to report on any p10 input in any rung: every arithmetic
operation is unsigned and wrapping and the two guards make `n − 2*r` and
`8 + taps + n − 1` both well-defined. **p10's sanitizer row is ASan's alone**,
where p18's was UBSan's alone.

### 7b — Miri

`miri.required: true`; the pair is `unsafe`/`verus`, the source `unsafe.rs`.
The gate's stage 8 result is in `results/gate/p10-fir-stencil.json`. Miri is
silent on every p10 input for the shipped rungs — the safety line is present in
all four Rust rungs, so nothing reads out of bounds. `controls/gen_controls.py`'s
`b_fence` is what it looks like when it is not (§2).

### 7c — R4 ≡ R5

| pair | opt | `md5_fn` equal | `md5_fn_norel` | `md5_raw` |
|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** (`norel`) | no |
| unsafe vs verus | O3 | **yes** (`exact`) | yes | yes |

matching the `identity` pin. At O0 the crate names differ in length so call
displacements differ — link layout, not codegen.

⚠ **BUT THE WHOLE-PROGRAM MARGINAL IS NOT EQUAL, AND THE DIFFERENCE IS NOT IN
THE KERNEL.** At **`-O3 isolated`** `verus` reads **1.00 Ir/call less** than
`unsafe` on every blob (`small` 3590 vs 3591, `large` 8710.0075 vs 8711.0075,
band `e` 19749.99 vs 19750.99). The kernel symbols are byte-identical, and the
**kernel-exclusive** column agrees exactly (both 71,540,000 on `small`, both
17,394,000 on `large`). The −1.00 lives in `main`: `Ir(main)` is 280,275 vs
260,274 on `small`, i.e. exactly `−1` per iteration and `−1` fixed. **Quote the
kernel-exclusive column for the identity claim**; a whole-program marginal is
not an identity oracle here, and this is the first pattern in the project where
the two disagree on a byte-identical pair.

⚠ **AND THAT −1.00 IS ITSELF MODE- AND DOMAIN-SPECIFIC**, which is the same
defect one layer down and is corrected here rather than left implicit. Fitted
over bands `r`+`o`+`d` (max |resid| **0.0000** in sample, **0.0000** out on
`h`+`e`):

```
-O3 isolated   R5 − R4 = −1                                    flat, EVERYWHERE
                                                               (rejected calls included)
-O3 whole      R5 − R4 =  0 − 2·rejwin − 2·rejfar − 2·fence
```

So in `whole` mode the pair is **equal on every accepted call** — the gate's
`marginal_ir_per_call` reads `unsafe` 3385.00 and `verus` 3385.00 on `small` —
and differs by 2.00 Ir on a call the guards reject (`d-allwin.bin`: 26 vs 24).
The claim *"the first byte-identical R4/R5 pair whose whole-program marginals
differ"* is therefore true in both modes but for different reasons, and the
figure that goes with it must name the mode. `R5 − R4` at `-O3 isolated` is the
**only one of p10's six laws whose domain did not move** when the rejected-call
columns were added (§8b2).

---

## 8 — the laws

All figures are **differenced marginals** — `(Ir(n₂) − Ir(n₁)) / (n₂ − n₁)` at
`n₁ = 2000, n₂ = 6000` on the same blob and the same binary
(`controls/sweep_ir.py`), which cancels process start-up, the payload load and
the fixed part of every call. Bands from `inputs/gen.py --sweep`:
`r` (16 blobs, `nout` fixed at 32, `r` = 1…16), `o` (10 blobs, `r` fixed at 4,
`nout` = 8…192), `h` (3 heterogeneous blobs), `e` (4 extrapolation blobs), and
`d` (7 blobs from `controls/gen_domain.py`, §8b2 — the REJECTED-CALL band, which
lives outside `inputs/` so it moves no committed record's `input_sha256`).

⚠⚠ **EVERY FIGURE IN THIS SECTION NAMES ITS MODE, AND THE TWO MODES DO NOT AGREE
ABOUT THE MECHANISM.** `controls/sweep_ir.py` defaults to `--mode isolated`;
TASK_057 fitted and published only that column and said so nowhere, and
TASK_057_REVIEW B2 found it. `-O3 isolated` builds the kernel behind a real call
(`#[inline(never)]`, separate TUs in C); `-O3 whole` lets LLVM inline it into the
driver loop, and the kernel then has no symbol at all. **The `R3 − R4` margin
survives in both — −323.00/−603.00 isolated, −127.00/−239.00 whole on
`small`/`large` — but its structure is completely different, and §8b3 is the
whole-mode column.** Where this file says a bare number without a mode, that is
a defect; §14 lists the ones that were.

### 8a — the regressors, and the two that were WRONG first

```
nout       outputs the call emits
scaltap    (taps mod 8) * nout   -- SCALAR-EPILOGUE taps
vecit      floor(taps/8) * nout  -- VECTOR iterations, 8 samples each
novecout   nout on calls where floor(taps/8) == 0
--- added at TASK_059 (§8b2), because a REJECTED call is a row of the design ---
rejwin     calls the window guard `n < taps` rejected
rejfar     calls the safety line rejected with `last > len`
fence      calls with `last == len` -- p10's BUG: R1 accepts, the other six
           cells reject
```

- **`taps` is not a regressor.** The tap loop vectorises (§1), so the tap count
  enters only through `taps mod 8` and `floor(taps/8)`, which have *different*
  coefficients. A per-tap law would be a fit of the wrong model.
- **`novec` (a per-CALL indicator) is not the regressor either; `novecout` (a
  per-OUTPUT one) is.** The vector setup and the horizontal reduce are skipped
  once per **output**, not once per call. `novec` fits bands `r` and `o` at max
  |resid| **0.0000** — and misses band `h` by up to **15.6 Ir**. Band `h` is why
  the model has the column it has, and this is a worked instance of
  `.memory/03-measurement.md`'s *"the parameter list is rarely complete on the
  first pass"*. **I cannot claim the list is closed.**
- ⚠ **AND IT WAS NOT.** TASK_057_REVIEW M4 found a fifth parameter — a REJECTED
  call — and a sixth behind it — *which* guard rejected. §8b2 adds three columns
  and refits. **The list has now gone 3 → 4 → 6, established by measurement each
  time, and it is still not closed.** What is *established* is: `nout`,
  `scaltap`, `vecit`, `novecout`, `rejwin`, `rejfar`/`fence`. What has not been
  searched at all: window strides that straddle a cache line, `nwin` large enough
  that the driver's window choice misses L2, and any input where `len < 8`.

### 8b — the fitted laws at `-O3 isolated` (`controls/fit.py`, exact rational, bands `r` + `o`)

**⚠ These are the `-O3 isolated` laws over the ACCEPTING domain.** §8b2 is the
domain refit — which leaves every coefficient below **unchanged** — and §8b3 is
the `-O3 whole` column, which does not.

**Differences** — max |residual| **0.0000** in sample over 26 blobs, and
**0.0000** out of sample on band `h`:

| quantity | law | |
|---|---|---|
| `R2 − R4` | `65 + 41.00·nout + 3.00·scaltap − 7.00·novecout` | |
| `R3 − R4` | `−3 − 5.00·nout + 0.00·scaltap − 1.00·novecout` | ⚠ `scaltap` coefficient **exactly zero** |
| `R2 − R3` | `68 + 46.00·nout + 3.00·scaltap − 6.00·novecout` | |
| `R1h − R1` (gcc) | `0` — every coefficient zero | |
| `R1h − R1` (clang) | `+1` flat | |

**Levels**, 5 columns `[1, nout, scaltap, vecit, novecout]`. ⚠ **The quoted
max |resid| 0.0096 in sample / 0.0056 out covers the FOUR RUST ROWS, not the
five rows of the table** — `c-clang` is **0.0239 / 0.0121**, re-measured
(TASK_057_REVIEW m2; holdout is band `h`, and on band `e` the same fit reads
0.0175). All of it is the driver's `println!` digit-count term,
`.memory/03-measurement.md` puts it at 0.2263 Ir/call/digit:

| cell | 1 | nout | scaltap | vecit | novecout |
|---|---:|---:|---:|---:|---:|
| `unsafe` (R4) | 71 | 29 | **9** | **17** | −8 |
| `verus` (R5) | 71 | 29 | **9** | **17** | −8 |
| `safe_tuned` (R3) | 68 | 24 | **9** | **17** | −9 |
| `safe_naive` (R2) | 136 | 70 | **12** | **17** | −15 |
| `c-clang` (R1) | 72 | 30 | **7** | **17** | −8 |

**`vecit` is 17.00 on all four LLVM cells and it is the seventeen-instruction
SSE2 body counted off the listing in §1 — zero fitted parameters, and
`controls/loops.py` confirms the body is exactly 17 with zero alignment `nop`s
inside it on every one of them (§8c).**
`scaltap` is 7 (C), 9 (R3 and R4), 12 (R2).

⚠ **NO gcc LEVEL LAW IS PUBLISHED, and that is a clean negative rather than an
omission.** Five designs were tried — the LLVM five columns at vector width 4,
8 and 16, and gcc's own `v16 / h8 / t8` columns with and without a no-vector
regime term — and the best max |residual| in sample was **45.3** (worst 816.0).
The mechanism is §1: gcc has three regimes where LLVM has two. gcc's
**difference** law, `c-gcc-h − c-gcc = 0`, is exact on every blob and needs no
level law.

### 8b2 — the DOMAIN: a rejected call is a missing COLUMN, and the old coefficients survive it exactly

TASK_057 published the laws above with no domain. **Every blob in bands `r`, `o`,
`h` and `e` accepts every window it visits**, so the five laws were fitted where
three regressors are identically zero — and TASK_057_REVIEW M4 showed they break
on any blob that contains a rejected call, with residuals *exactly linear* in the
rejected-call fraction. `.memory/03-measurement.md`: **do not write the domain as
a caveat; test whether it is a missing column.**

`controls/gen_domain.py` writes band `d` — seven blobs that turn the three
rejection columns on, alone and mixed (the shapes are TASK_057_REVIEW's, made
re-derivable from the tree). `controls/sweep_ir.py --band d --inputs …` measures
them on the same differenced-marginal axis; `controls/fit.py` recomputes the
regressors from the blobs, so the fit is reproducible from the generator plus the
`Ir` column alone. **Band `d` lives in `.temp/p10/domain/` and not in `inputs/`**,
deliberately: a blob in `inputs/` moves `input_sha256` on every committed record
(`harness/measure.py`) and would force a re-measure of the whole matrix to add a
diagnostic. It is deterministic like `inputs/gen.py` — generated twice from
scratch, all seven blobs byte-identical (`.temp/p10c/logs/domain_hash_{a,b}.txt`),
and the fit below was re-run against the regenerated blobs and is unchanged.

**A rejected call, priced directly** (`-O3 isolated`, marginal `Ir`/call on the
100 %-rejecting blobs):

| blob | what rejects | c-gcc | c-gcc-h | c-clang | c-clang-h | R2 | R3 | R4 | R5 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `d-allwin` | `n < taps` | 59 | 59 | 43 | 42 | 79 | 47 | 28 | 27 |
| `d-allfar` | `last > len` | 62 | 62 | 47 | 46 | 84 | 51 | 32 | 31 |
| `d-allfp` | `last == len` | **1942** | 62 | **1800** | 46 | 84 | 51 | 32 | 31 |

Three things fall out of that table before any fit:

1. **The sixth parameter is real and it is +3/+4/+5.** Rejecting at the safety
   line costs more than rejecting at the window guard, by exactly the `last`
   computation and a second compare: +3 gcc, +4 clang/R3/R4/R5, +5 R2.
2. **`rejfar` and `fence` are the SAME rejection in the six cells that make it** —
   every guarded cell reads identically on the two blobs (62/46/84/51/32/31). The
   two columns are kept separate anyway, because they are *not* the same in R1.
3. **`fence` is where R1 diverges**, at 1942 and 1800 Ir/call. `.memory/02-bench-rules.md`
   rule 1 forbids costing an R1/R1h pair there, so those rows are excluded from
   the two `R1h − R1` fits (`controls/fit.py --exclude d-allfp`) and from nothing
   else.

**The refit, 33 rows (bands `r`+`o`+`d`), 7 columns, design rank 7 of 7, holdout
bands `h` AND `e`:**

| quantity | law | max abs resid, in / out |
|---|---|---|
| `R2 − R4` | `65 + 41·nout + 3·scaltap − 7·novecout − 14·rejwin − 13·rejfar − 13·fence` | 0.0000 / 0.0000 |
| `R3 − R4` | `−3 − 5·nout + 0·scaltap − 1·novecout + 22·rejwin + 22·rejfar + 22·fence` | 0.0000 / 0.0000 |
| `R2 − R3` | `68 + 46·nout + 3·scaltap − 6·novecout − 36·rejwin − 35·rejfar − 35·fence` | 0.0000 / 0.0000 |
| `R5 − R4` | `−1` — every rejection coefficient **0** | 0.0000 / 0.0000 |
| `R1h − R1` (gcc) | `0` — every coefficient **0**, `fence` excluded | 0.0000 / 0.0000 |
| `R1h − R1` (clang) | `+1 − 2·rejwin − 2·rejfar`, `fence` excluded | 0.0000 / 0.0000 |

> **EVERY ONE OF THE FOUR OLD COEFFICIENTS IS UNCHANGED, TO THE INTEGER, IN
> EVERY LAW.** The published law is exactly the new law's restriction to
> `rejwin = rejfar = fence = 0`. That is p18's corrected-design result reproduced
> on an eighth pattern, and it is the reason `.memory/03-measurement.md` says to
> add the column rather than write the caveat.

**And here is what a caveat would have hidden** — refitting the **old four
columns** over all 33 rows (the p18 diagnostic):

| quantity | old cols over old rows | old cols over ALL rows |
|---|---|---|
| `R2 − R4` | 65 / 41 / 3 / −7, resid **0.0000** | 60.190 / 41.023 / 3.021 / −6.982, resid **9.19** |
| `R3 − R4` | −3 / −5 / 0 / −1, resid **0.0000** | +4.879 / −5.038 / −0.034 / −1.030, resid **14.12** |
| `R2 − R3` | 68 / 46 / 3 / −6, resid **0.0000** | 55.312 / 46.061 / 3.055 / −5.953, resid **23.31** |
| `R1h − R1` (clang) | +1, resid **0.0000** | −147.273 / 0.730 / 0.682 / 0.931, resid **1606.73** |

Every coefficient comes off its integer and the residual moves by three orders of
magnitude. **The levels survive the same way**: `[1, nout, scaltap, vecit,
novecout]` are 71/29/9/17/−8 (R4 and R5), 68/24/9/17/−9 (R3), 136/70/12/17/−15
(R2) and 72/30/7/17/−8 (`c-clang`) **before and after**, at max |resid|
0.0099 in sample against the old 0.0096 — and the three new columns then read
off the rejected-call *levels* directly: a `rejwin` call costs `1 + rejwin`, i.e.
R4 71−43 = **28**, R3 68−21 = **47**, R2 136−57 = **79**, `c-clang` 72−29 = **43**,
each matching the measured table above exactly.

⚠ **Neither the band-`e` registration nor the band-`h` hold-out could have caught
this**, because both are entirely inside the accepting domain — which is exactly
what `.memory/03-measurement.md` warns a hold-out cannot do for you.

### 8b3 — the SAME laws at `-O3 whole`, where the mechanism is different

Bands `r`, `o`, `d` refitted at `--mode whole`, holdout `h`+`e`, same 7 columns,
rank 7 of 7:

| quantity | `-O3 whole` law | in / out |
|---|---|---|
| `R3 − R4` | `+1 + 0.00·nout − 2.00·scaltap + 1·novecout + 4·rejwin + 5·rejfar + 5·fence` | 0.0000 / 0.0000 |
| `R2 − R4` | `39 + 18·nout + 4·scaltap − 5·novecout − 8·rejwin − 8·rejfar − 8·fence` | 0.0000 / 0.0000 |
| `R2 − R3` | `38 + 18·nout + 6·scaltap − 6·novecout − 12·rejwin − 13·rejfar − 13·fence` | 0.0000 / 0.0000 |

**Levels at `-O3 whole`** (max |resid| 0.0099 in / 0.0232 out; `c-clang`
0.0247 / 0.0767):

| cell | 1 | nout | scaltap | vecit | novecout |
|---|---:|---:|---:|---:|---:|
| `unsafe` (R4) | 57 | **26** | **9** | 17 | −10 |
| `verus` (R5) | 57 | **26** | **9** | 17 | −10 |
| `safe_tuned` (R3) | 58 | **26** | **7** | 17 | −9 |
| `safe_naive` (R2) | 96 | **44** | **13** | 17 | −15 |
| `c-clang` (R1) | 53 | **26** | **7** | 17 | −9 |

> ⚠ **THE `nout` COLUMN AND THE `scaltap` COLUMN SWAP ROLES BETWEEN THE MODES,
> AND THAT IS THE POINT.** At `-O3 isolated` `R3 − R4` is `−5.00·nout` with
> `scaltap` exactly **0.00**; at `-O3 whole` it is `−2.00·scaltap` with `nout`
> exactly **0.00**. The published headline `−127.00 / −239.00` at `whole` is
> `1 − 2·64` and `1 − 2·120`, to the instruction.

**Both are counted off the listing, not fitted** (`controls/loops.py` on the
`whole` binaries, where the kernel is inlined so the loops are enumerated inside
`main`): vector body **17 / nops_inside = 0** on all four LLVM cells, and the
scalar epilogue **9** (R4), **7** (R3), **13** (R2), **7** (`c-clang`), each with
**0** nops inside — exactly the fitted `scaltap` coefficients. The mechanism is in
§8c.

Also visible in the whole column, and worth stating because it is what "the
kernel is opaque" buys: `R2 − R4` **halves** (+1447/+2679 against +2881/+5345 on
`small`/`large`), and `R1h − R1` changes sign on gcc (§4).

### 8c — what that says about safety's cost

**FIRST, THE PADDING CHECK**, because TASK_057 asks for it before any
per-iteration coefficient is named after a mechanism (*"executed alignment
padding has landed inside a published law three times"*). `controls/loops.py`
enumerates every backward-branch loop of the kernel symbol and counts the
alignment `nop`s inside each body. ⚠ **`controls/loops.py` is a second objdump
caller, which `CLAUDE.md` used to say there should not be** — TASK_057_REVIEW m4
checked it against `harness/asm.py`'s listing of the same binaries and the two
**agree exactly**, and other patterns' controls (`p08`, `p12`, `p14` ×2, `p16`)
do the same thing, so the stale artefact was the `CLAUDE.md` sentence rather
than this control. **Already fixed by the manager at `c7a7da8`** — the rule is
now *the gate* has one pipeline, not *the tree*. All figures below are
`-O3 isolated` unless the row says `whole`:

```
unsafe      loop 15700..15749  body= 17  nops_inside=0     <- the vector loop
            loop 15780..1579d  body=  9  nops_inside=0     <- the scalar epilogue
            loop 156e0..157c1  body= 59  nops_inside=3     <- the outer loop
safe_naive  loop 159d0..15a19  body= 17  nops_inside=0
            loop 15a70..15a9c  body= 12  nops_inside=0
            loop 15930..15ad6  body=103  nops_inside=3
safe_tuned  loop 15780..157c9  body= 17  nops_inside=0
            loop 157f0..15810        body=  9  nops_inside=0
            loop 15760..1582e  body= 53  nops_inside=2
c-clang     loop 1760..17a9    body= 17  nops_inside=0
            loop 17e0..17f8    body=  7  nops_inside=0
            loop 1740..1818    body= 58  nops_inside=3
c-gcc       loop 1a48..1aa5    body= 23  nops_inside=0     <- gcc's, 16 samples wide
```

**`vecit` and `scaltap` are clean — zero padding instructions in either loop, on
every LLVM cell — so 17.00 and 7/9/9/12 may be named after mechanisms.**

⚠ **The per-OUTPUT coefficients are not clean and are not named after a
mechanism here.** The outer loop's span carries 2–3 alignment `nop`s, and a
`nop` immediately before an inner loop's head is on the **fall-through** path
into that loop, so it retires once per output. **Up to 2 of R4's 29.00 Ir/output
is padding**, and likewise for R3's 24.00 and R2's 70.00. What is claimed about
the `nout` column is the *difference* (41.00 for `R2 − R4`, where the padding
largely cancels) and the largest identified component of it — the 24-instruction
guard chain below. **The whole 41.00 is not decomposed mnemonic by mnemonic and
no claim rests on its composition.**

**Per scalar-epilogue tap the bounds check is +3.00 Ir**, R2 against R4. Read it
mnemonic by mnemonic before calling the 3 a check:

```
R4  (unsafe)      9   movzbl, movzbl, imul, add, dec, inc, inc, cmp, jne
R2  (safe_naive)  12  lea, cmp, jae(panic), cmp, je(panic),
                      movzbl, movzbl, imul, add, inc, cmp, jne
R3  (safe_tuned)  9   movzbl, movzbl, lea, inc, inc, imul, add, cmp, jne
R1  (c-clang)     7   movzbl, movzbl, imul, add, inc, cmp, jne
```

Every one of those is the loop body between a backward branch and its own
target, read off the **shipped** binary by `controls/loops.py`, and every one
equals the fitted `scaltap` coefficient exactly. ⚠ **R3 and R4 both cost 9 and
they are NOT the same nine**: R4 has zero checks and three pointer bumps
(`dec`/`inc`/`inc`), R3 has zero checks and three induction instructions
(`lea`/`inc`/`inc`). C's 7 is the floor here — one induction variable and no
checks.

**AND AT `-O3 whole` R3 REACHES THAT FLOOR AND R4 DOES NOT**, which is where the
whole-mode `−2.00·scaltap` of §8b3 comes from. Same tool, same convention, the
loops enumerated inside the inlined `main`:

```
R4  (unsafe)      9   lea, movzbl, lea, movzbl, imul, add, inc, inc, jne
R3  (safe_tuned)  7   movzbl, movzbl, inc, imul, add, inc, jne
R1  (c-clang)     7   movzbl, movzbl, imul, add, inc, inc, jne
R2  (safe_naive) 13
```

⚠ **The two extra instructions are the two `lea`s, and they are ADDRESS
ARITHMETIC, not checks.** R4 forms two independent four-term indices per tap —
`off + sb + i + j` for the sample and `off + 8 + j` for the coefficient — so
once the kernel is inlined and the outer-loop strength reduction goes away, each
has to be re-formed with a `lea` before its `movzbl`. R3's `windows()` +
`zip` hands the epilogue two base pointers and **one shared index register**
(`(%r8,%r13,1)` and `(%r15,%r13,1)`), so both loads address off the same
induction variable — which is exactly what `c-clang` does, and `c-clang` costs
the same 7. **There is no bounds check in any of the three.**

⚠ **The +3.00 is NOT "the check costs 3".** R2 spends **5** instructions on the
two bounds checks (`lea/cmp/jae` for the sample, `cmp/je` for the coefficient)
and saves **2** because indexed addressing off one induction variable replaces
R4's three pointer bumps. 5 − 2 = 3. This is finding 17's shape
(*"a bounds check costs 2 or 3 Ir/byte depending on what the loop already
holds"*) one level further on: here the loop's *addressing mode* pays back part
of the check.

**Per VECTORISED tap the bounds check is 0.00 Ir**: R2's and R4's `vecit`
coefficients are both 17.00, and their vector loops are the same seventeen
instructions in the same order. What R2 pays instead is a **24-instruction
per-output `cmp`/`cmov` chain** at the outer loop head — the vectoriser's runtime
bounds guard, hoisted out of the tap loop — followed by an 8-instruction block
that rounds the trip count down to a multiple of 8:

```
mov 0x38(%rsp),%rax / cmp %rbp,%rax / mov %rbp,%rcx / cmovb %rax,%rcx
cmp %rbx,%rsi / mov %rbx,%rax / cmova %rsi,%rax / mov %r8,0x60(%rsp)
add %r8,%rax / cmp %rax,%rcx / cmovb %rcx,%rax / mov 0x30(%rsp),%rcx
lea (%rcx,%r11,1),%rdx / cmp %rdx,%rsi / cmova %rsi,%rdx / mov 0x40(%rsp),%rcx
add %r11,%rcx / sub %rcx,%rdx / add $0xfffffffffffffff7,%rdx
mov 0x28(%rsp),%rcx / cmp %rdx,%rcx / cmovb %rcx,%rdx / cmp $0x8,%rdx / jae
```

That is **p05's finding 12 reproduced on a different kernel** — *"hoisted into a
22-instruction per-row trip-count computation and survives in the scalar
epilogue"* — and here the obligation is **linear**, where p05's stated excuse was
that its own was nonlinear. ⚠ p05's chain is 22 and p10's shipped one is **24**;
the shapes match and the counts do not, so the number is p10's own and not a
constant. A standalone day-one probe of the same kernel with a different guard
structure gave 22 (`.temp/p10/probe/`), which is the reminder that this count is
a property of a spelling.

**And the panic pads confirm the attribution rather than leaving it to a count**
(`.memory/03-measurement.md`: decode, never count —
`patterns/p12-strcat-fixed/controls/pads.py`, reused verbatim):

```
safe_naive  pads=10  40:20 40:47 41:20 41:57 42:20 42:51 43:20 43:57  63:18 63:61
              8 of them are the header decode buf[off..off+7]
              63:18  (buf[off + sb + i + j] as u32)...     <- the sample tap
              63:61  ...wrapping_mul(buf[off + 8 + j] ...)  <- the coefficient tap
safe_tuned  pads=2   60:24 60:40   both `buf.split_at(off).1.split_at(len).0`
t_winidx    pads=2   60:24 60:40   the same two
unsafe      pads=0
```

**R3's tap loop contributes ZERO panic pads** — that is *why* `R3 − R4`'s
`scaltap` coefficient is exactly 0.00 — and its two survivors are the window
reslice, once per call. So R3 is genuinely check-free in the loop rather than
having moved the check there.

⚠⚠ **AND THAT IS THE WHOLE OF WHAT THE PAD DECODE CAN EXPLAIN — WHICH IS ZERO
`Ir`.** TASK_057 offered the pad decode as the reason `R3 − R4` is *negative*
(§13, P2). It cannot be: a pad is a bounds check, a bounds check in this kernel
lives in the scalar epilogue, and **the `scaltap` coefficient of `R3 − R4` is
exactly 0.00 at `-O3 isolated`** — worth nothing. TASK_057_REVIEW B3 found it.
The whole isolated margin is the `−5.00·nout` term, and the mechanism is
**induction-variable bookkeeping**. Mnemonic by mnemonic off the shipped
`-O3 isolated` listing, executed path (vector loop entered), per output:

| block | R4 `unsafe` | R3 `safe_tuned` |
|---|---|---|
| outer head | `cmpq $0x7,-0x8(%rsp)` `ja` = **2** | `cmp $0x8,%r9` `jae` = **2** |
| vector preamble | `pxor` `xor` `pxor` = 3 (+1 nop) | `pxor` `xor` `pxor` = 3 (+1 nop) |
| horizontal reduce + epilogue setup | 5×SSE + `movd` + **four** `mov`, two of them **reloads from `-0x18(%rsp)` and `-0x10(%rsp)`** = **10** (+1 nop) | 5×SSE + `movd` + **one** `mov %r11,%r14` = **7** (+1 nop) |
| outer tail | Horner 5 + `mov` + **four** `inc` (`r14`,`r9`,`rdi`,`rbx`) + `cmp`/`jne` = **12** | Horner 5 + `mov` + **`dec %r8` + `inc %rcx`** + `cmp`/`jb` = **10** |
| **executed total** | **27 real + 2 nop = 29** | **22 real + 2 nop = 24** |

29 and 24 are the fitted `nout` coefficients exactly (29.000015 / 24.000015), the
two alignment `nop`s cancel, and **the −5.00 is five real instructions**: R4's
`off + sb + i + j` and `off + 8 + j` force LLVM to strength-reduce to **four**
outer induction variables and to spill two epilogue starting values, reloading
them once per output; `windows()` hands it one advancing pointer plus a trip
counter and `zip` hands the epilogue one index. This is the same cause the
`whole` epilogue shows as two `lea`s (above) — one loop level up, because in
`isolated` the outer loop is where the strength reduction happens.

> ⚠⚠ **AND IT IS NOT A SAFETY EFFECT AT ALL.** `c-clang` — idiomatic C, no
> bounds check anywhere in it, **the same four-term index expression** — fits
> `nout` at **30.00** at `-O3 isolated`, dearer per output than *both* Rust
> rungs, and matches R3 exactly at `-O3 whole` (26.00/output, 7/epilogue tap).
> The per-output figure is a property of the **index expression**, not of the
> language and not of the checks.
>
> The zero-free-parameter check for all four LLVM cells, off the outer-loop spans
> above (outer span − vector body − epilogue body − the 3-instruction no-vector
> path − its `nop` where present): R4 59−17−9−3−1 = **29**, R3 53−17−9−3 = **24**,
> R2 103−17−12−3−1 = **70**, `c-clang` 58−17−7−3−1 = **30**. Nothing in the level
> law is fitted. (TASK_057_REVIEW clean negative 13; §8c's padding caveat still
> stands — up to 2 of each of those is `nop` — which is why the *difference* is
> what is claimed.)

**Stated as the finding, with both modes and the domain named:**

> **On this kernel the iterator form is cheaper than the four-term-index form,
> and the language is not what decides it.** At `-O3 isolated`, per output:
> `safe_tuned` **24**, `unsafe` **29**, `c-clang` **30**, `safe_naive` **70**.
> At `-O3 whole`: `safe_tuned` **26**, `unsafe` **26**, `c-clang` **26**,
> `safe_naive` **44**, and the gap moves entirely into the scalar epilogue
> (7 / 9 / 7 / 13 per tap). The safety tax proper is the other axis and it is
> the `scaltap` split R2 pays: **0.00 Ir on every tap the vectoriser reached,
> +3.00 Ir on every tap it did not.**

**And on the totals, with the input named, because they do not all point one
way.** Kernel-exclusive `Ir`/call at `-O3 isolated` (`results/p10-fir-stencil.json`):

| | `small.bin` | `large.bin` |
|---|---:|---:|
| `safe_tuned` (R3) | **3254.00** | 8094.00 |
| `c-clang` (R1) | 3514.00 | 8578.00 |
| `unsafe` (R4) | 3577.00 | 8697.00 |
| `c-gcc` (R1) | 3783.00 | **7391.00** |
| `safe_naive` (R2) | 6458.00 | 14042.00 |

**Safe Rust is the cheapest cell in the pattern on `small` — ahead of both C
cells — and it beats every LLVM cell on both blobs; it does NOT beat gcc on
`large`,** where gcc's 16-wide vectorisation (§1) is worth more than everything
else on the table. The `whole` column reorders it again (`c-clang` 3253 against
`safe_tuned` 3258 on `small`). Any one-line version of this is wrong; quote the
mode and the input.

⚠ **No `ns` claim accompanies any Rust-vs-C row.** `controls/clayout.py` builds
one language per invocation, so the C and Rust populations are different timing
sessions and `.memory/00-environment.md` forbids quoting across them (§11).

### 8d — the in-contract R3 spread, and the two-step reslice

What `spec.md`'s `idiom` block leaves free on R3 is the **window reslice**
(named nowhere) and the **spelling of the tap loop** (deliberately, since
comparing tap-loop spellings is what p10 is for). Marginal `Ir`/call, every
variant checksum-identical to the shipped cell on `small`, `large` and
`degenerate`:

| spelling | `small` | `large` | vs shipped R3 |
|---|---:|---:|---:|
| **shipped** `windows()` + `iter().zip()` | 3268.00 | 8108.00 | — |
| `t_winidx` `windows()` + indexed inner loop | **3264.00** | **8104.00** | **−4.00 / −4.00** |
| `t_fold` `.fold()` instead of the `for` | 3268.00 | 8108.00 | 0.00 / 0.00 |
| `t_1step` one-step `&buf[off..off+len]` reslice | 3269.00 | 8109.00 | **+1.00 / +1.00** |
| `x_sum` (**out of contract**, `.sum()`) | 3268.00 | 8108.00 | 0.00 / 0.00 |

- **The CHEAPEST FOUND in-contract R3 is `t_winidx`, at 3264.00 on `small.bin`
  and 8104.00 on `large.bin`** — 4.00 Ir/call cheaper than the shipped cell on
  both inputs. The word is "cheapest found", never "minimum", and the input is
  named because on p16 no single spelling was cheapest on both blobs.
- **The R3-side span is 3264.00…3269.00 (`small`) and 8104.00…8109.00
  (`large`), width 5.00 on both.**
- **Which spelling ships was decided before any p10 cell was measured** — the
  `windows() + zip()` one, because that is the library idiom p10 exists to
  exercise — and `.memory/02-bench-rules.md`'s *"NEVER re-ship a rung because a
  cheaper in-contract spelling was found"* is why that order matters. So p10
  ships an R3 measurably off the floor of its own contract, like p16 and p17.

**THE TWO-STEP RESLICE (`.memory/01-ladder.md` finding 3, backlog priority 1) IS
WORTH −1.00 Ir/CALL ON p10, ON BOTH BLOBS** (`-O3 isolated`; 3268 against 3269
and 8108 against 8109). The shipped R3 uses the two-step
`buf.split_at(off).1.split_at(len).0`; `t_1step` is the same cell with the
one-step `&buf[off..off + len]`. That is finding 3's figure reproduced on a
seventh pattern, at zero `unsafe` and zero TCB, and the panic-pad decode above
shows the mechanism is not check removal: both forms contribute the same **two**
pads.

⚠ **BUT THE WIN IS ONE INSTRUCTION WIDE, SO IT IS AN INSTRUCTION-COUNT-ONLY
RESULT AND IT DOES NOT RETIRE THE BACKLOG ITEM.** `.memory/03-measurement.md`,
closing the p08 retraction section: *"a spelling whose win is one instruction
wide cannot be quoted on `Ir` alone, and this box cannot supply the wall-clock
column to rescue it — say the win is instruction-count-only and stop."* p10
quotes it on `Ir` alone; §11's layout populations do not separate the two
spellings and cannot be made to at 1 `Ir` on a ~3300 `Ir` call. **An earlier
draft of this paragraph said "a clean positive, and the standing backlog item
can be retired"; that is retracted** (TASK_057_REVIEW M6, §14). ⚠ And it must
not be levelled with p04's: 1.00 `Ir` here is not the same evidential thing as
p04's figure, and a handoff that called it *"confirmed at −1.00 on a seventh
pattern"* was over-reading it.

The R2 side moves on the same lever and much harder: `n_2step` (R2 with the
two-step reslice, indexing the window instead of the blob) reads 5645.00 /
12557.00 against shipped R2's 6472.00 / 14056.00, i.e. **−827 / −1499**.

### 8e — the R4 side: NOT degenerate. `u_win` VERIFIES, and 60% of the published margin was R4 spelling

⚠⚠ **RETRACTION.** TASK_057 published *"Its twin does not verify … the R4 side
is DEGENERATE as far as this task searched … the −194/−362 figure is a CONTROL
and not a rung."* **That is wrong.** TASK_057_REVIEW B1 closed the proof with a
**single invariant clause**, and I reproduced it from the shipped tree:

```
$ python3 patterns/p10-fir-stencil/controls/gen_controls.py     # regenerates u_win_verus
$ ./verus_run.py .temp/p10/ctl/u_win_verus.rs
verification results:: 10 verified, 0 errors
```

**Same obligation count as the shipped `verus.rs` (10). No new trusted item
(still three `external_body`), no lemma, no `by (nonlinear_arith)`, no
`by (bit_vector)`.** The closing repair, now in `controls/gen_controls.py` so it
is re-derivable from the tree rather than from a `.temp/` directory, is exactly

```rust
w@ == buf@.subrange(off as int, off + len as int)   // in BOTH loop invariants
```

**Both clauses are load-bearing and nothing else is** — measured, one Verus run
each (each takes ~1.5 s, which is worth saying because "the Verus budget" was
the excuse in the retracted paragraph):

| variant | result |
|---|---|
| both invariant clauses, no `assert` after the reslice | **10 verified, 0 errors** |
| both clauses + the `assert` (the reviewer's file) | 10 verified, 0 errors — the `assert` is **dead** |
| drop the INNER loop's clause | `9 verified, 1 errors`, *precondition not satisfied* ×2 |
| drop the OUTER loop's clause | `9 verified, 1 errors`, *invariant not satisfied before loop* |

**Why TASK_057's repair round missed it.** It added `w@.len() == len`, which
constrains the window's *length* and never relates its *contents* to `buf@` — so
the `dotp` invariant, which is written over `buf@`, had nothing to rewrite
`w@[k]` into. vstd does ship a spec for `<[T]>::split_at`
(`~/tools/verus/vstd/std_specs/slice.rs:176`) and it gives the subrange
directly. `.memory/01-ladder.md:320` already says to spend the eleven minutes on
`verus_run.py` before blaming vstd, and this is what happens when it is not spent.

**So the R4 side is NOT degenerate, and here is the span.** `-O3 isolated`,
differenced marginal, `small` / `large`:

| | `small` | `large` |
|---|---:|---:|
| R4ship (`unsafe`) | 3591.00 | 8711.00 |
| **`u_win`** (admissible: twin 10/0) | **3397.00** | **8349.00** |
| R3ship (`safe_tuned`) | 3268.00 | 8108.00 |
| **published** `R3ship − R4ship` (fixed-R4 bound) | **−323.00** | **−603.00** |
| **`R3ship − u_win`** (against the cheapest R4 found) | **−129.00** | **−241.00** |

**60.1% (`small`) / 60.0% (`large`) of the published margin is R4 spelling.**
The sign survives; the magnitude does not. Per `.memory/02-bench-rules.md` both
are published, with the input named, and the word **"minimum" appears nowhere** —
`u_win` is the **cheapest R4 found**, one lever, and a cheaper one may exist.

> **The number to quote is a PAIR, not a point**: `R3ship − R4ship = −323.00 /
> −603.00` is the fixed-R4 bound, `R3ship − u_win = −129.00 / −241.00` is the
> bound against the cheapest admissible R4 found, both at `-O3 isolated` on
> `small`/`large`. This is `.memory/01-ladder.md` finding 14 (p13) repeating:
> **quote the fiat whenever the margin is quoted.**

⚠ **AND STILL NO PAIR INTERVAL.** `spec.md`'s `identity[0].why` — which is this
project's standing ruling, not p10's opinion — says `min(R3 found) − min(R4
found)` is **not** the repair, because two upper bounds differenced bound nothing
in either direction. What p10 publishes is therefore **three separate
quantities**, never their difference:

| quantity | `small` | `large` |
|---|---:|---:|
| the fixed-R4 bound `R3ship − R4ship` | −323.00 | −603.00 |
| the **R3-side span**, cheapest-found to dearest-found in contract (§8d) | 3264.00…3269.00 | 8104.00…8109.00 |
| the **R4-side span**, R4ship down to the cheapest R4 found admissible | 3397.00…3591.00 | 8349.00…8711.00 |

The R4 side now has **measured width 194.00 / 362.00** where TASK_057 reported it
as zero, which is the whole of B1. Against the cheapest-found in-contract R3 the
fixed-R4 bound is `−327.00` / `−607.00`.

**Two independent routes to the same number.** −129/−241 (isolated, against an
admissible R4) lands within **2 Ir** of −127/−239 (`-O3 whole`, against the
shipped R4, §8b3). Most of the isolated margin is LLVM failing to clean up R4's
index arithmetic while the kernel is opaque, and it goes away either by making
the kernel visible or by simplifying the index — which is the same statement
twice.

#### 8e2 — ⚠ WHY `u_win` IS NOT SIMPLY PROMOTED TO R4, and why it bounds every pattern

**It is not the proof. It is the identity pin.** Built under the shipping
filenames — the crate name is part of the symbol, so the pair has to be compiled
as `unsafe.rs` and `verus.rs` for the comparison to be the one the gate makes —
and compared on the declared symbol extent:

```
python3 patterns/p10-fir-stencil/controls/gen_controls.py
mkdir -p .temp/p10c/idty
cp .temp/p10/ctl/u_win.rs       .temp/p10c/idty/unsafe.rs
cp .temp/p10/ctl/u_win_verus.rs .temp/p10c/idty/verus.rs
~/.cargo/bin/rustc --edition 2021 -C codegen-units=1 -C opt-level=3 \
    -C debug-assertions=off --cfg slb_isolated \
    .temp/p10c/idty/unsafe.rs -o .temp/p10c/idty/u_win-O3-isolated
python3 ./verus_run.py --compile .temp/p10c/idty/verus.rs \
    -o .temp/p10c/idty/u_win_verus-O3-isolated \
    -C codegen-units=1 -C opt-level=3 -C debug-assertions=off --cfg slb_isolated
python3 harness/asm.py diff .temp/p10c/idty/u_win-O3-isolated \
                            .temp/p10c/idty/u_win_verus-O3-isolated
```

```
u_win        n_fn 116  md5_fn 769cbb7d…  md5_fn_norel aae0541c08aa18968178777857a80f57
u_win_verus  n_fn 116  md5_fn b92e3e36…  md5_fn_norel aae0541c08aa18968178777857a80f57
sole real difference:  lea -0xc7fd(%rip),%rdi   vs   lea -0xc7dc(%rip),%rdi
```

`harness/asm.py diff`: *identical by raw machine-code bytes: **False**;
identical with pc-rel fields masked: **True***. So the `u_win` pair meets
**`identity: norel`** and **not `exact`**. ⚠ The two `md5_fn` digests above are
**not** the reviewer's — the two `u_win_verus` sources differ in comments, which
moves the read-only data and therefore the displacement — but
**`md5_fn_norel` is `aae0541c08aa18968178777857a80f57` in both derivations**, and
so is `n_fn = 116`. That the *masked* digest is stable across two independently
built pairs while the unmasked one is not is the mechanism stated as a
measurement. `spec.md` pins `exact` at `-O3`, so
`u_win` is out of its own pattern's declaration, and **that is the reason it
cannot ship — not the proof, which closes.**

**The mechanism, and it generalises.** `patterns/p12-strcat-fixed/controls/pads.py
--source` on the same two binaries:

```
u_win-O3-isolated          pads=1   64:40  `buf.split_at(off).1.split_at(len).0`
u_win_verus-O3-isolated    pads=1  322:40  the same reslice
unsafe-O3-isolated  (ships) pads=0
safe_tuned-O3-isolated      pads=2
```

`u_win`'s reslice leaves **one** surviving panic landing pad; rustc materialises
that pad's `&core::panic::Location` with a **rip-relative `lea`**, and the two
crates of an R4/R5 pair never lay their read-only data out identically (different
crate names, and R5 links vstd), so the displacement field differs. `md5_fn`
therefore differs and only `md5_fn_norel` can match.

> ⚠ **THE GENERAL CONSEQUENCE, WHICH IS BIGGER THAN p10: an `identity: exact`
> pin excludes every candidate R4 that carries a surviving panic pad.** A pad
> embeds a `Location` reached pc-relatively; a pc-relative displacement into
> per-crate read-only data cannot be equal across the pair. So on any pattern
> pinning `exact`, the admissible-R4 search space is restricted to spellings
> whose panic pads are all optimised away — which on p10 means `get_unchecked`
> against the *whole* buffer and rules out every window-reslicing R4. **That is
> the reason this span exists at all**, and it bounds the R4 search on every
> pattern in the project, not just this one.
>
> **p10's pin is NOT relaxed**, deliberately: every other pattern pins `exact`
> at `-O3` and p10 should not become the exception to make its own headline
> smaller. The constraint is recorded instead. (Whether `norel` should be the
> project-wide `-O3` pin is a question for `.memory/`, not for one pattern to
> decide unilaterally — and the direction test would flag p10 relaxing its own
> declaration to admit a cheaper R4 after measuring one, because that moves p10's
> published safety-tax number **down**.)

**What was NOT done**: no R4 cheaper than `u_win` was attempted — e.g.
`get_unchecked` over a `Range` rather than an index, which would need a second
trusted item — and `u_win` has not been run through `harness/check.py` as a rung,
so its conformance to every `required` spelling is checked by reading and not by
the gate.

### 8f — band `e`: the registered out-of-sample test

All figures in this section are `-O3 isolated`. `controls/predict.py` was run
with band `e` **not yet measured for any cell**, and its output hashed:

```
predictions sha256: da05048cf06ae7dbe3b304e2f38c74ccd79b14d9b9ce5a85ce7f9f13dba4db8a
4 blob(s) x 10 quantities = 40 predictions, tolerance +/-0.05 Ir
```

⚠ **TASK_059 added four keys to `sweep_ir.shape()`, which `predict.py` imports,
so the registration had to be re-checked rather than assumed.** Re-run against
the edited tooling it prints **`da05048cf06ae7db…` — the same digest, byte for
byte** (`predict.py` selects the five original regressors by name), so the
registration still means what it meant. A tooling edit that moved this hash
would have destroyed the only genuinely pre-registered test p10 has.

Then band `e` was measured. **40 of 40 hold. Worst |error| 0.0200**, and that
worst case is a *level* row (the `println!` digit term); **every one of the 20
difference predictions is exact to 0.0000**:

| blob | `R2−R4` pred / meas | `R3−R4` pred / meas | `R1h−R1` gcc | clang |
|---|---|---|---|---|
| `sweep-e160r20` | 7105 / **7105.0000** | −803 / **−803.0000** | 0 / **0.0000** | 1 / **1.0000** |
| `sweep-e192r24` | 8513 / **8513.0000** | −963 / **−963.0000** | 0 / **0.0000** | 1 / **1.0000** |
| `sweep-e224r18` | 12609 / **12609.0000** | −1123 / **−1123.0000** | 0 / **0.0000** | 1 / **1.0000** |
| `sweep-e256r12` | 11329 / **11329.0000** | −1283 / **−1283.0000** | 0 / **0.0000** | 1 / **1.0000** |

⚠ **STATED PRECISELY, BECAUSE THIS PROJECT HAS PUBLISHED A HOLD-OUT THAT COULD
NOT FAIL.** The pooled `r`+`o` design is **rank 4 of 4** in the difference
model, so a band-`e` regressor vector *is* a linear combination of rows already
fitted and **this test cannot fail from linearity alone**. What it can fail on
is a missing interaction, a missing regime column or a nonlinearity — **and that
failure mode is real here and was observed**: the `novec`-instead-of-`novecout`
model fitted `r` and `o` at max |resid| 0.0000 and missed band `h` by 15.6 Ir.

⚠ **The leave-one-band-out rank IS non-vacuous, which is the other half of the
rule.** `controls/fit.py` prints it: the pooled design is rank 4 of 4, and

```
rank after dropping band 'o' (10 rows): 3
rank after dropping band 'r' (16 rows): 2
```

so **neither band is redundant**. p18's defect was that one band alone was
already full rank, so dropping any other changed nothing.

---

## 9 — the forbidden spellings, priced

Gate stage 0b: **`forbidden: 10 spelling(s), 0 hit(s)`** — no rung spells one.

| forbidden | why, and what it would cost |
|---|---|
| `chunks_exact` | a **runtime** chunk size computes `len − len % chunk_size` and lowers to a hardware `div`, priced at 1 `Ir` by callgrind and tens of cycles by the machine — it would sit inside every per-tap law here and be invisible in the column the law is fitted on. p16 also measured that the chunk width alone moves that pattern's per-byte rate over a 31% range. |
| `from_le_bytes` | deletes the written-out header decode every rung shares, **and is not available to an R4 at all** at the pinned vstd (`is not supported`, measured on five patterns), so a rung using it would compare a safe cell against an unsafe cell that cannot exist. |
| `.sum(` | `Sum for u32` uses `+`, which **panics** under `-C debug-assertions=on` and under Miri. Built anyway as `x_sum`: it measures **3268.00 / 8108.00**, i.e. **byte-for-byte the shipped R3's number** at the twenty-four measured cells' flags — so the exclusion costs **0.00 Ir** and buys behaviour in two of the gate's own configurations. That is the honest price of this entry and it is not zero-value: it is a spelling that is free where p10 measures and different where p10 checks. |
| `step_by(` | would let a rung visit a subset of the taps and still satisfy every other entry. Not built. |
| `copy_from_slice` | p10's kernel writes nothing anywhere; a rung that materialised the window would be measuring an allocation this pattern does not have. Not built. |

---

## 10 — mutants

`controls/gen_controls.py` generates each by exact-string substitution from a
shipped rung, so "differs in exactly this and nothing else" is a property of the
generator.

| mutant | edit | result |
|---|---|---|
| `m_fence` | `verus.rs`: `last >= len` → `last > len` (the C bug, in the proof) | **`9 verified, 1 errors`** — `error: invariant not satisfied before loop` on `8 + taps + n - 1 < len` |
| `m_fence3` | `m_fence` **and both copies** of that invariant weakened to `<=` | **`8 verified, 2 errors`** — `error: precondition not satisfied` on `buf_get_unchecked`'s `i < v@.len()`, plus the kernel postcondition |
| `m_nowin` | `verus.rs`: the window guard `if n < taps { return 0; }` deleted | **`9 verified, 1 errors`** — `error: possible arithmetic underflow/overflow` (on `n - 2 * r`) |
| `b_fence` | `unsafe.rs`: `last >= len` → `last > len` | compiles, agrees with `model.py` on every benign input, and reads one byte past the window on `adversarial-fencepost` (§2) |

⚠ **`m_fence` alone fails one level too early to prove the point, and saying so
is the point.** The rejection lands on the loop invariant, not on the accessor
precondition — so on its own it shows only that *some* obligation notices. The
`m_fence3` round is what shows the obligation that catches p10's bug is the
trusted accessor's `i < v@.len()`, which is what §6d's argument (b) rests on.
An intermediate mutant weakening only ONE of the two invariant copies was also
built and still lands on the other (`8 verified, 2 errors`).

Two of these — `m_fence` and `m_nowin` — are the two proof mutants the task
requires to fail the gate.

---

## 11 — wall clock, and the layout populations

**No `ns` claim in this file rests on a single binary.** `controls/clayout.py`
(ported from p18, itself from p14) builds a layout population per cell —
`-align-all-functions` 0…8 plus symbol-ordering shuffles — and times them
alternating, pinned, with the per-process constant differenced out
(`(t(N) − t(1))/(N − 1)`, `.memory/03-measurement.md` finding 20a).

**Rust population, `small.bin`, 24 layouts per cell, 7 reps, cpu 5:**

```
safe_naive   n=24  min-of-reps ns/call  417.23.. 426.73  spread 2.28%  median 420.53
safe_tuned   n=24  min-of-reps ns/call  207.55.. 215.39  spread 3.78%  median 212.12
unsafe       n=24  min-of-reps ns/call  229.38.. 233.59  spread 1.84%  median 231.59
verus        n=24  min-of-reps ns/call  229.42.. 233.09  spread 1.60%  median 231.23
```

- **`safe_tuned`'s band is DISJOINT from `unsafe`'s** — 215.39 worst against
  229.38 best, over 24 layouts each. **Safe Rust is faster than unsafe Rust
  here in wall clock as well as in `Ir`, and the sign survives the layout
  population.** −8.4% at the medians. This is a *fixed-R4* statement (§8e).
- **`verus` vs `unsafe` is the null control it should be**: medians 231.23 vs
  231.59, bands 229.42–233.09 against 229.38–233.59, essentially coincident, on
  byte-identical kernels. The pair's overlap *is* this measurement's own floor,
  and it is ~1.6–1.8% wide.
- `safe_naive` is +81.6% on the medians against `unsafe`, bands far apart.

**C population, `small.bin`, 30 layouts per cell** (a separate timing run —
`.memory/00-environment.md` forbids quoting across sessions, so these are
compared only to each other):

```
c-clang-h    n=30  227.68.. 231.95  spread 1.87%  median 229.43
c-clang      n=30  226.86.. 231.10  spread 1.87%  median 228.97
c-gcc-h      n=30  250.91.. 258.80  spread 3.14%  median 254.47
c-gcc        n=30  252.23.. 257.00  spread 1.89%  median 254.10
```

**Both hardened/unhardened pairs overlap almost completely**, which is the
honest reading of a `0.00` and a `+1.00` `Ir` difference on a ~3500 `Ir` call:
**the fencepost's wall-clock price is not resolvable on this box, in either
direction, on either compiler.** The gcc pair is the sharper statement — its two
kernels differ by one opcode byte and nothing else, and it reads 254.10 vs
254.47, so that 0.15% *is* a measurement of the floor.

⚠ **CORRECTION, found by the TASK_059 figure sweep and NOT by the review.** An
earlier draft of this paragraph said *"`harness/measure.py`'s own wall rows: 16
of 32 cells exceed the 10% min-to-median spread threshold and are discarded, all
of them `large.bin` rows … (`safe_tuned` 7.18 ms min, `unsafe` 7.60,
`safe_naive` 11.65)"*. **Every number in that sentence was false against the
record it described**, and `results/tables/p10-fir-stencil.md` — generated from
the same JSON — contradicted it in one line. The "16 of 32" was a misreading of
the 16 `O0` cells, which are not timed at all. The record as shipped at TASK_057
had **32 wall measurements at spreads 1.3 %…5.7 % and NONE discarded**.

⚠ **AND `results/p10-fir-stencil.json` WAS RE-MEASURED AT TASK_059, WHICH MUST BE
DISCLOSED BECAUSE THE WALL ROWS MOVED.** TASK_059's C5 sweep edits *comments* in
`safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs` and `c/kernel_hardened.c`; those
four files are in `measure.py`'s `source_sha256`, so the record went STALE and
`harness/measure.py p10` had to be re-run for `--check-stale` to be clean.

**What that re-run changed, diffed cell by cell against the previous record:**

```
static counts, kernel .text bytes, every md5, every checksum,
every callgrind Ir value, all 8 cells x 2 opts x 2 modes:     0 differences
wall clock:                                                   every row moved
```

**Zero deterministic differences and a uniformly ~8 % slower wall column** — the
box was less quiet than at TASK_057 — which is the cleanest illustration this
pattern has of why `.memory/03-measurement.md` ranks the two columns the way it
does. The `-O3 isolated` `small.bin` minima are now

```
safe_tuned  7.01 ms   verus  6.92 ms   unsafe  7.48 ms   safe_naive 11.44 ms
```

— the same ranking, and still the basis of no claim here; the populations above
are. **One cell now exceeds the 10 % spread threshold and is discarded**
(`verus / isolated / small.bin`, 10.9 %), which the regenerated table marks `✗`.
The `verus`-vs-`unsafe` null control is unaffected: it is a `clayout.py`
population, not a `measure.py` row.

**Not done:** no single timing run puts the C cells and the Rust cells in one
population, so **no Rust-vs-C `ns` comparison is made**. `clayout.py` builds one
language per invocation.

---

## 12 — disclosures: every edit to the declaration after a measurement

`PROTOCOL.md` definition-of-done 6 and `.memory/01-ladder.md`'s direction test.
Two edits, both after work had started, both stated with the direction.

**(1) The measured Verus fields.** `verus.obligations` (10),
`verus.twin_obligations` (11), `verus.items`, and the three long `note` strings
(`obligations_note`, `twin_obligations_note`, `collapse.note`) and
`identity[0].why` were placeholders in the first write and were filled in from
`./verus_run.py` and from the gate. This moves `contract_sha256` from
`14667d39…` to `cb1c3c9f…` and **cannot be avoided** — an obligation count is a
measurement and cannot precede the proof. **Direction: none of these fields
constrains a rung's source.** `idiom` was untouched by this edit and its hash
was unchanged across it.

**(2) One `idiom` edit, and it is a WEAKENING.** After the first gate run, the
stage-0b spelling audit reported **5 backticked spellings that pinned nothing**:

```
audit  pins nothing  required[0]  c    0 of 2 rung(s)   `last == len`
audit  pins nothing  required[2]  c    0 of 2 rung(s)   `2r+1`
audit  pins nothing  required[2]  rust 0 of 4 rung(s)   `2r+1`
audit  pins nothing  required[5]  rust 0 of 4 rung(s)   `windows()`
audit  pins nothing  required[6]  c    0 of 2 rung(s)   `.wrapping_mul(`
```

All five were **prose** inside an entry's English — `2r+1` written informally
beside the pinned `2 * r + 1`, `windows()` named in the sentence saying the tap
loop is *not* pinned, and so on. ⚠ **SIX backticked spellings were removed, not
five**, and the prose here used to say "those five" while the audit totals
quoted below require six (TASK_057_REVIEW m1). The sixth is `get_unchecked` in
`required[5]`'s Rust prose — it is the one the audit did **not** list above,
because it matched two rungs rather than none, and it is disclosed on its own
terms three paragraphs down. `idiom_sha256` moved from `066841a9…` to
`22af8747…` across all six.

**The direction test, in writing, in its REPAIRED form.**
`.memory/01-ladder.md`'s original wording is flagged BROKEN and must not be
cited; the repair, which has since been attacked and fired on p13, is:

> *An edit to a declaration is self-certification if it moves the pattern's own
> published figure in the direction that flatters the author's thesis. For a
> safety-tax number that direction is **down**.*

**Scored: it moves p10's published figures by 0.00 in either direction.** No
cell was edited, no binary was rebuilt, no measurement was re-run after it, and
the headline figures — `R2 − R4 = +2881.00 / +5345.00` and
`R3 − R4 = −323.00 / −603.00`, both `-O3 isolated` — are the same numbers before
and after. The edit admitted no new spelling that was then measured and quoted.

⚠ **TASK_059 made NO declaration edit at all.** `spec.md` is byte-identical and
`contract_sha256` is still `cb1c3c9f…` after two full gate runs. That matters
here specifically: TASK_059 *found* an admissible R4 (`u_win`, §8e) that is
cheaper than the shipped one and is excluded only by `identity: exact`, so
relaxing the pin to `norel` would have shrunk p10's own published safety-tax
number — **exactly the direction the repaired test flags**. The pin was left
alone and the constraint recorded instead.

**And on the shape the repaired test now flags** — *an idiom entry whose scope
names some rungs and excludes others is a thumb on the scale* — the edit runs
the **right** way: `get_unchecked` in `required[5]`'s Rust prose matched
`unsafe.rs` and `verus.rs` and **not** `safe_naive.rs` or `safe_tuned.rs`, so
leaving it in would have declared the two safe rungs out of their own contract
for not using `get_unchecked` — an asymmetric pin favouring the unsafe side on a
pattern whose headline is that safe Rust is cheaper. Removing it **deletes** an
accidental asymmetry rather than creating one. The other four matched **zero**
rungs and constrained nothing at all.

**No `forbidden` entry moved, no intended `required` spelling moved.** The
audit's totals move 43 → 37 spellings, 126 → 108 pairs, 78 → 76 present, and
`required: 5 pin nothing` → **`0 pin nothing`**; the two present-pairs lost are
exactly `get_unchecked` against `unsafe.rs` and `verus.rs`.

**The two remaining "scoped-absent" audit rows are intended and are the pattern:**

```
audit  absent  required[0]  c  c/kernel.c           `if (last >= len)`
audit  absent  required[0]  c  c/kernel_hardened.c  `if (last > len)`
```

Each C rung must contain **exactly one** of the two, and the entry backticks
both so a `grep` settles which rung has the bug. p18's `required[0]` has the
same shape with one spelling.

⚠ **`required_absent: 2` in the gate record is that entry WORKING, and nothing
machine-readable says so** — the audit line is indistinguishable from a pin that
missed (p18's `required[0]` reports 0). That is a gap in the audit's vocabulary
and not a defect in p10 (TASK_057_REVIEW m3); it is reported here rather than
fixed, because the fix belongs in `harness/check.py` and in
`.memory/02-bench-rules.md`, neither of which a pattern may edit.

**No entry of `required` or `forbidden` was ADDED in response to a measurement**
— unlike p14, which had to disclose one. p10's `-O0` identity came out `norel`
and its `-O3` identity `exact` on the first build of the pair.

---

## 13 — what TASK_057 predicted, scored

The registered table is `.tasks/TASK_057.md` §2, committed **before** any p10
measurement existed. Scored on the **shipped cells**, over the `r` band's 4×
range in tap count (`taps` 9…33 at fixed `nout`):

**P1 — *"`R2 − R4` grows linearly in the tap count `2r+1`, slope > 0."*
FALSE.**

```
r        4     5     6     7     8     9    10    11    12    13    14    15    16
taps     9    11    13    15    17    19    21    23    25    27    29    31    33
R2-R4 1473  1665  1857  2049  1473  1665  1857  2049  1473  1665  1857  2049  1473
```

Exactly periodic with period 4 in `r` (8 in taps). **Along `taps ≡ 1 (mod 8)`
the tap-count slope is 0.0000 over a 3.7× range in tap count.** The tap-count
dependence is `3.00 · scaltap` with `scaltap = (taps mod 8)·nout`, which is
**bounded by `7·nout` and does not grow**. The growth that is real is in
`nout`, at 41.00 Ir per output.

**P2 — *"`R3 − R4` is flat in `r`."* TRUE at `-O3 isolated` on the accepting
domain, and the SIGN is the surprise.** The fitted `scaltap` coefficient is
**exactly 0.0000** and `vecit`'s is 0.00 too, so the only two `r`-dependent
regressors both vanish: `R3 − R4 = −3 − 5.00·nout − 1.00·novecout`. It is flat
in `r` and **negative** — safe `windows() + zip()` is *cheaper* than
`get_unchecked` by 323.00 Ir/call on `small` and 603.00 on `large`, and the gap
**widens** with the output count.

⚠ **THE PREDICTED *REASON* WAS WRONG, AND SO WAS THE FIRST DRAFT OF THIS
PARAGRAPH.** It said: *"The predicted reason was right too ('the window slice is
one range check however many taps it covers'): the panic-pad decode in §8c shows
R3's tap loop contributes zero pads."* The pad decode is correct and reproduces
exactly — and it **cannot produce this sign**, because pads are checks, checks
in this kernel live in the scalar epilogue, and the `scaltap` coefficient of
`R3 − R4` is exactly **0.00**. A mechanism worth 0.00 `Ir` cannot explain
−323.00. **The real mechanism is induction-variable bookkeeping, it is not a
safety effect, and `c-clang` pays MORE of it than either Rust rung** — §8c has
it mnemonic by mnemonic. TASK_057_REVIEW B3.

⚠ **And P2's flatness is mode-specific.** At `-O3 whole` the same difference is
`+1 − 2.00·scaltap`, i.e. **not** flat in `r` at all — it moves by 2·nout per
residue step (§8b3). P2 is true in the mode it was scored in and false in the
other, which no wording in the original verdict admitted.

⚠ **One caveat against my own P2 verdict.** A day-one probe
(`.temp/p10/probe/`, a five-kernel standalone probe with a *different* guard
structure and no contract) measured `R3 − R4` at 7.00 vs 9.00 Ir per scalar tap
— i.e. **not flat**, varying by −256 Ir/call per residue step. The shipped
cells are flat. The difference is the guard structure alone, and it means
**P2's truth is spelling-sensitive at the level of a hoisted comparison**, which
is exactly the class of thing `.memory/01-ladder.md` finding 14 says never to
generalise from one spelling.

**P3 — *"At `-O3`, R3's inner reduce vectorises and R2's does not."* FALSE.**
Both vectorise. `asm.py stat` reports `vector_regs: ["xmm"]` on all eight cells,
and **R2's vector body is the same seventeen SSE2 instructions as R4's**. The
`vecit` coefficient is 17.00 in all four LLVM level laws.

**The manager's own named failure mode was the right one.** TASK_057 wrote:
*"The most likely way they die is that LLVM hoists every tap's check into a
single `i + r < n` precondition, making R2 flat in `r` too — in which case P1
and P3 are wrong, the finding is a stronger version of finding 3, and it is
still worth publishing."* That is what happened, with one correction: the check
is not hoisted into a *single* precondition but into a **24-instruction
per-output `cmp`/`cmov` chain** (24 on the shipped listing — a day-one probe with
a different guard structure gave 22, and this paragraph said 22 for one commit,
370 lines below the §8c paragraph that corrects it), and it **survives in the
scalar epilogue** at 3.00 Ir per epilogue tap. So the finding is — **and this is
the corrected form; the retracted one is in §14**:

> **THE SAFETY TAX.** Safe Rust's indexing tax, R2 against R4, is **0.00 Ir on
> every tap the vectoriser reached and +3.00 Ir on every tap it did not**, plus a
> 41.00 Ir per-output constant whose largest identified component is the
> vectoriser's 24-instruction runtime bounds guard. `-O3 isolated`, accepting
> domain. That bounds finding 3's domain by naming a mechanism rather than a data
> size.
>
> **AND THE OTHER AXIS IS NOT A SAFETY TAX AT ALL.** `R3 − R4` is negative — safe
> `windows()+zip()` beats `get_unchecked` by −323.00/−603.00 (`-O3 isolated`,
> fixed R4) and by −129.00/−241.00 against the cheapest admissible R4 found
> (§8e), and by −127.00/−239.00 at `-O3 whole`. **None of that is a check.** It
> is the cost of the *index expression*: R4 forms two independent four-term
> indices per tap and pays for them in four outer induction variables and two
> stack reloads (isolated, −5.00/output) or in two `lea`s (whole,
> −2.00/epilogue-tap), while `windows()` + `zip` gives LLVM one advancing pointer
> and one shared index. **`c-clang` — idiomatic C, no bounds check anywhere, the
> same index expression — pays 30.00/output at `-O3 isolated`, more than either
> Rust rung**, and matches R3 exactly at `-O3 whole`.
>
> So p10 measured **an index-expression result in three languages' worth of
> codegen**, and TASK_057 published it as a safe-beats-unsafe result. The
> corrected claim is the stronger one, because it transfers: *prefer the spelling
> that hands LLVM one induction variable, in any language; in Rust that spelling
> happens to be the safe one.*

**And the fourth thing TASK_057 said it was least sure of** — *"if a runtime
radius will not vectorise at all, R3 and R4 both go scalar and P3 is
untestable"* — did not happen either. A runtime radius vectorises fine.

---

## 14 — TASK_059: every claim retracted, and HOW the sweep was done

`.tasks/TASK_057_REVIEW_REPORT.md` confirmed p10's whole measurement layer —
every fitted law, control figure, pad count, loop-body count and the entire
Verus layer reproduced exactly, with **21 clean negatives**. Nothing in this
section is a re-measurement of any of that. **What was wrong was what the numbers
were said to mean**, and this is the complete list.

| # | retracted claim | where it was | what replaces it |
|---|---|---|---|
| 1 | *"the R4 side is DEGENERATE as far as this task searched"* | §8e, README | **`u_win` verifies, 10/0**, one invariant clause. `R3ship − u_win = −129.00 / −241.00`, i.e. **60% of the published margin was R4 spelling**. §8e |
| 2 | *"its Verus twin does not verify, so it is a control and not a rung"* | §8e, README | It is not the proof: `u_win` meets **`norel`, not `exact`**, on one pc-relative panic-`Location` displacement. §8e2, and the general bound it puts on every pattern's R4 search |
| 3 | every headline figure, unqualified | §4, §7c, §8, §13, README | **`-O3 isolated` named at every figure**, and the `-O3 whole` column published beside it (§8b3). `R3−R4` is −323/−603 isolated and −127/−239 whole; `R1h−R1` gcc is 0.00 isolated and **−1.00 whole** |
| 4 | *"the panic-pad decode … is why `R3 − R4` is negative"* | §13 P2 | Pads can only explain `scaltap`, which is **0.00**. The mechanism is induction-variable bookkeeping and **`c-clang` pays more of it than either Rust rung**. §8c |
| 5 | the five laws, published with no domain | §8b | Three **columns**, not a caveat: `rejwin`, `rejfar`, `fence`. Every old coefficient survives unchanged; the old columns over the new rows give residuals 9.19…1606.73. §8b2 |
| 6 | *"`R1h − R1` (clang) = +1 flat"* | §4, README | `+1 − 2·rejwin − 2·rejfar` at `-O3 isolated`; **−1.00 on a fully rejecting blob**; `0` at `-O3 whole` |
| 7 | *"a clean positive, and the standing backlog item can be retired"* | §8d | The win is **1.00 Ir**, so it is instruction-count-only and retires nothing. §8d |
| 8 | *"byte-identical to `unsafe.rs`'s"* (vector body) | `safe_naive.rs:10`, `unsafe.rs:16` | Same seventeen mnemonics, different register allocation — **not** byte-identical. §1 said so; the sources did not |
| 9 | *"22-instruction per-output chain"* | `safe_naive.rs:13`, `unsafe.rs:19`, §13 | **24** on the shipped listing |
| 10 | *"SAFE RUST IS CHEAPER PER SCALAR-EPILOGUE TAP — 7.00 against 9.00"* | `unsafe.rs:22-24`, **undisclosed** | The **day-one probe's** figure. Shipped cells are **9 vs 9** isolated (`scaltap` diff exactly 0.00) and **7 vs 9** whole |
| 11 | *"max |resid| 0.0096 / 0.0056"* over a five-row table | §8b | Covers the **four Rust rows**; `c-clang` is 0.0239 / 0.0121 |
| 12 | *"the backticks were removed from those five"* | §12 | **Six**; the totals quoted twenty lines later already required six |
| 13 | *"§0's four rejected candidates, rejected on measurements"* (TASK_059's own premise) | §0.2 | **Five**, rejected on **argument**; the one exception is structural, not measured |
| 14 | *"16 of 32 wall cells exceed the 10% spread threshold and are discarded"* + three ms figures | §11 | **None were**; the record's own generated table said so. Found by the sweep below, not by the review. §11 also discloses the TASK_059 re-measure the C5 comment edits forced, in which **no deterministic number moved at all** |

**HOW THE SWEEP WAS DONE, so that "I checked" is checkable.** Not by reading:
`.temp/p10c/figures.sh` extracts every quantitative claim from every committed
p10 file — the five rung sources, both C kernels, the C driver and header,
`model.py`, `inputs/gen.py`, all seven `controls/*.py`, `spec.md`, `NOTES.md`
and `README.md` — under four patterns, because a stale figure in this pattern
has taken all four shapes:

```
1.  [-+]?[0-9]+\.[0-9]{2}\b        a marginal or a coefficient   (7.00, -323.00)
2.  [0-9]+[- ](instruction|instrs|insn)   a counted loop body    (22-instruction)
3.  byte-identical|byte for byte   an identity claim
4.  cheaper|dearer|beats|free|flat|degenerate|minimum|first
                                   a superlative that must carry a mode
```

Pattern 1 returned **206 hits** on the pre-correction tree; each was checked against
`results/gate/p10-fir-stencil.json`, `results/p10-fir-stencil.json` or a re-run
fit. Patterns 2 and 3 are what caught items 8 and 9 in the table above; pattern 4
is what caught items 3 and 6; and item 14 came out of the pattern-1 pass, from a
figure the review had not looked at. **The sweep is re-runnable** (`sh
.temp/p10c/figures.sh`) and its before/after output is under `.temp/p10c/logs/`.

⚠ **What the sweep does NOT cover, stated because "I swept everything" is the
claim that gets people into trouble**: it does not check prose *arguments*, only
figures, identity words and superlatives; it does not read `spec.md`'s
`slb-contract` JSON (deliberately — editing `spec.md` moves `contract_sha256`
and none of its numbers is a measured p10 result, they are predictions about
other patterns with `../NOTES.md 4 measures it` beside them); and it cannot see
a figure that is *correct but mode-ambiguous* unless the sentence also contains
one of pattern 4's words.

**Adjacent, not p10 — both already closed by the manager while this task ran, and
re-verified here rather than assumed:**

- TASK_057_REVIEW m5 reported `results/gate/p08-overlap-move.json` STALE. **It is
  not now**: `harness/measure.py --check-stale` reads `FRESH … 36 source(s)` for
  it, fixed at `9fb54af`. The whole tree is **0 STALE**.
- TASK_057_REVIEW m4 reported `CLAUDE.md:27`'s *"the only objdump caller"* stale
  against six patterns' controls. Fixed at `c7a7da8`; the rule is now that the
  *gate* has one pipeline, not the tree. p10's `controls/loops.py` agrees with
  `harness/asm.py` exactly (§8c).

**Not done at TASK_059, and each is a real gap:**

- **No R4 cheaper than `u_win` was attempted.** `get_unchecked` over a `Range`
  would need a second trusted item; a spelling with *no* surviving panic pad
  would be the one that could actually ship under the `exact` pin, and none was
  built. The R4-side span is therefore still a lower bound on the R4-side width.
- **`u_win` has not been through `harness/check.py` as a rung.** Its conformance
  to every `required` spelling is checked by reading, not by the gate.
- **No `ns` measurement was re-taken.** The `clayout.py` populations in §11 are
  TASK_057's and TASK_057_REVIEW's; nothing in TASK_059 touches them, and the
  `measure.py` wall rows moved only because the record had to be regenerated.
- **The `-O3 whole` laws have no registered out-of-sample test.** Band `e` was
  registered for the `isolated` column only; the `whole` fits use band `e` as an
  ordinary hold-out, which is weaker.
- **No `O0`/`O0d` column was fitted in either mode**, and no claim rests on one.
