# p10 — weighted FIR / sliding-window stencil

**The first kernel here with more than one indexed read per iteration at a fixed
offset from the cursor** — a `2r+1`-tap dot product, with the radius read out of
the input file at run time — and therefore the first that can ask whether safe
Rust's tax is proportional to the **number of indexing operations** or flat.

**The answer is neither.** At `-O3` the tap loop vectorises in *every* spelling,
including the naive indexed one, to the same seventeen-instruction SSE2 body
(same mnemonic sequence, different register allocation — not byte-identical).
The per-tap bounds checks survive only in the scalar epilogue that runs
`taps mod 8` times per output:

> **0.00 Ir on every tap the vectoriser reached, +3.00 Ir on every tap it did
> not**, plus a 41.00 Ir per-output constant whose largest identified component is a
> 24-instruction `cmp`/`cmov` chain computing how many taps may be vectorised
> safely. `-O3 isolated`, on inputs where every visited window is accepted.

The two per-iteration coefficients are loop-body counts off the shipped
listing with **zero alignment `nop`s inside either loop** (`controls/loops.py`);
the per-output ones are not, and `NOTES.md` 8c says so rather than naming them
after a mechanism.

That bounds `.memory/01-ladder.md` finding 3's domain by naming a *mechanism*
rather than a data size, and it reproduces p05's `O(nrow)` hoisted-guard result
on a kernel whose obligation is **linear** where p05's excuse was that its own
was nonlinear.

⚠ **Every figure in this file names its `-O3` MODE and its DOMAIN, and if one
does not that is a defect.** `isolated` builds the kernel behind a real call;
`whole` lets LLVM inline it, and the two do not agree about the mechanism. The
domain is "every visited window is accepted": a *rejected* call is a fifth and
sixth model parameter, not a caveat (`NOTES.md` 8b2). p10 was reviewed at
`.tasks/TASK_057_REVIEW_REPORT.md` and **fourteen interpretive claims were
retracted** — `NOTES.md` 14 lists all of them.

## The bug: one character, and exactly one byte

`.memory/06-catalogue.md`'s guess — *off-by-one at boundaries* — is **upheld**,
and it is not an omitted line:

```c
size_t last = 8 + taps + n - 1;   /* window offset of the LAST sample byte */
if (last >  len) return 0;        /* c/kernel.c            THE BUG */
if (last >= len) return 0;        /* c/kernel_hardened.c   correct  */
```

`last` is an **index**, so `last == len` is already one past the window. Every
other line of the two C cells is character for character identical.

**Three consequences, all measured:**

1. **Hardening costs at most one branch, and it is not the price of a check** —
   both C rungs already perform the comparison, where every earlier R1 in this
   project omits a *line*. The two kernels differ in a swapped `cmp` and an
   inverted `jcc` (gcc) or one tail-merge `jmp` (clang). ⚠ **The figure is
   mode- and domain-dependent and all four cells are published**
   (`NOTES.md` 4):

   | `-O3`, Ir/call | gcc | clang |
   |---|---:|---:|
   | `isolated`, every call accepted | **0.00** | **+1.00** |
   | `whole`, every call accepted | **−1.00** (hardened *cheaper*) | **0.00** |
   | `isolated`, every call rejected | 0.00 | **−1.00** (hardened *cheaper*) |
   | `whole`, every call rejected | 0.00 | 0.00 |

   So *"`R1h − R1` (clang) = +1.00 flat"* is true only at `-O3 isolated` and only
   on the accepting domain — of the seven other cells **five are 0.00 and two
   have the opposite sign**. **And on the domain where the bug actually fires,
   hardening is not free at all — it saves 1880 Ir/call**: on a blob where every
   call hits the fencepost, `c-gcc` reads **1942.00** against `c-gcc-h`'s
   **62.00**, and `c-clang` **1800.00** against **46.00**. That is the work the
   bug does.
2. **The harm is exactly one byte.** `adversarial-farover.bin` declares `n`
   far beyond the window and **R1 and R1h reject it alike** — an off-by-one
   buys one byte and nothing more.
3. **Whether that byte is observable is a property of the ALLOCATION.**
   `adversarial-fencepost.bin` puts the window at the end of the payload and
   ASan reports `heap-buffer-overflow ... READ of size 1`;
   `adversarial-fenceslack.bin` is the **same window** with three trailing
   payload bytes and the identical off-by-one is ASan-clean, UBSan-clean,
   exit 0 and wrong. p02's result on the read side, at the smallest possible
   magnitude.

## The iterator form beats the four-term-index form — in every language, and it is not a bounds-check result

This is p10's headline, and it is **not** the one TASK_057 published. That one
said *"safe Rust beats unsafe Rust"* and attributed it to the panic-pad decode;
`.tasks/TASK_057_REVIEW_REPORT.md` B3 showed the pads can only explain the
`scaltap` coefficient of `R3 − R4`, **and that coefficient is exactly 0.00**.

Per output, `-O3 isolated`, all four LLVM cells, **counted off the shipped
listing with zero fitted parameters**:

| cell | index expression | Ir per output |
|---|---|---:|
| `safe_tuned` (R3) | `windows()` + `zip` — one advancing pointer | **24.00** |
| `unsafe` (R4) | `buf[off + sb + i + j]`, unchecked | 29.00 |
| **`c-clang`** (R1) | the same four-term index, **no checks at all** | **30.00** |
| `safe_naive` (R2) | the same index, checked | 70.00 |

**The cheapest per-output cell in the pattern is the safe one, and the dearest
of the three check-free ones is C.** R4's two four-term indices force LLVM to
four outer induction variables and two stack reloads per output; at `-O3 whole`
that outer-loop penalty vanishes (all three read **26.00**/output) and the same
cause reappears in the scalar epilogue as two `lea`s — 9 instructions against
R3's and `c-clang`'s 7. `NOTES.md` 8c has it mnemonic by mnemonic.

So the transferable claim is *prefer the spelling that hands LLVM one induction
variable, in any language; in Rust that spelling happens to be the safe one* —
and **the safety tax proper is the other axis**, the `0.00` / `+3.00` split above.

**The margin, quoted as a pair because a point would be a fiat** (`-O3`,
`small` / `large`):

| | `isolated` | `whole` |
|---|---:|---:|
| `R3ship − R4ship` — the fixed-R4 bound | **−323.00 / −603.00** | **−127.00 / −239.00** |
| `R3ship − u_win` — against the cheapest R4 **found** | **−129.00 / −241.00** | — |

A 24-layout population puts `safe_tuned` at 207.55–215.39 ns/call against
`unsafe`'s 229.38–233.59 — **disjoint bands**, −8.4% at the medians, re-taken on
a quiet box at −8.25% with tighter spreads. That is a `-O3 isolated`, fixed-R4
statement.

⚠ **RETRACTED: the R4 side is NOT degenerate.** TASK_057 reported that `u_win`
(reslice once, then `get_unchecked` into the window) could not be a rung because
its Verus twin does not verify. **It verifies — 10 verified, 0 errors, one
invariant clause, no new trusted item and no lemma** — so **60% of the published
margin was R4 spelling**. What actually excludes it is the **identity pin**:
`u_win`'s reslice leaves one surviving panic landing pad, the pad holds a
pc-relative `&core::panic::Location`, and that displacement cannot match across
an R4/R5 pair — so it meets `norel` and p10 pins `exact`. **The pin is not
relaxed.** The general consequence — *an `exact` identity pin excludes every
candidate R4 carrying a panic pad, on every pattern* — is in `NOTES.md` 8e2.

## Firsts

- **`slice::windows()` — the first use in this project.**
  `grep -rn "windows(" patterns/*/*.rs` returned nothing before p10. It takes a
  **runtime** size (verified, not assumed) and costs **no `div`**, where
  `chunks_exact` with a runtime chunk size does.
- **`global size_of usize == 8;`** — the first pattern that has to say this.
  Verus treats `usize` as architecture-independent, so `2 * r + 1` on a `usize`
  built from four header bytes is `possible arithmetic underflow/overflow`
  without it. p07 dodged the same obligation by computing in `u64`; p10 cannot,
  because its contract pins the spelling. It is **checked, not assumed** — a
  probe declaring `== 4` fails to *compile* (`E0080`), so it adds nothing to the
  TCB and a 32-bit target could not be built at all. `NOTES.md` 6b.
- **The first hardening in this project whose cost is zero BECAUSE R1 ALREADY
  PERFORMS THE COMPARISON** — structural rather than a libc property. Quote it
  with the four cells above, never as "hardening is free".
- **The first byte-identical R4/R5 pair whose whole-program marginals differ.**
  At `-O3 isolated` by 1.00 Ir/call, in `main`, not in the kernel — the
  kernel-exclusive column is identical, and that is the column to quote for an
  identity claim. At `-O3 whole` the pair is equal on every accepted call and
  differs by 2.00 Ir on a rejected one. `NOTES.md` 7c.
- **An `identity: exact` pin excludes every candidate R4 that carries a
  surviving panic pad** — a bound on the R4 search space of *every* pattern
  here, and the reason p10's R4-side span exists. `NOTES.md` 8e2.

## The registered predictions, scored

`.tasks/TASK_057.md` §2 was committed before any measurement. **P1 false, P2
true with the opposite sign, P3 false** — `NOTES.md` 13.

And a genuinely out-of-sample test: 40 predictions for sweep band `e`, hashed
(`da05048c…`) before band `e` was measured. **40/40 hold, worst |error| 0.0200,
and all 20 difference predictions exact to 0.0000.** `NOTES.md` 8f states
precisely what that test can and cannot fail on — and `NOTES.md` 8b2 adds the
thing it *could not* fail on: band `e` is entirely inside the accepting domain,
so it could not have found the rejected-call columns.

## The domain, which is a set of columns and not a caveat

Every law above was first published over inputs where the kernel accepts every
window it visits. It does not: a call the guards reject is a row of the design
with its own price, and *which* guard rejected changes that price by +3…+5 Ir.
`controls/gen_domain.py` builds the band, `NOTES.md` 8b2 refits with three new
columns — and **every original coefficient survives to the integer**, at
max |resid| 0.0000 in sample and out. Refitting the *old* columns over the new
rows instead takes the residual from 0.0000 to **9.19 … 1606.73** and knocks
every coefficient off its integer, which is what a caveat would have hidden.
Parameters established so far: `nout`, `scaltap`, `vecit`, `novecout`, `rejwin`,
`rejfar`/`fence` — **the list has gone 3 → 4 → 6 and is still not closed.**

## Files

```
spec.md          the contract, incl. the hashed `slb-contract` block
NOTES.md         the evidence
model.py         the independent reference model (two implementations)
inputs/gen.py    the generator; deterministic, verified by regenerating twice
c/               R1 (kernel.c), R1h (kernel_hardened.c), the shared driver
safe_naive.rs    R2 -- index every tap
safe_tuned.rs    R3 -- `windows(taps)` + `iter().zip()`
unsafe.rs        R4 -- `get_unchecked`
verus.rs         R5 -- R4 plus the proof; 10 verified, 0 errors
controls/        mkcontract.py, gen_controls.py, gen_domain.py, sweep_ir.py,
                 fit.py, predict.py, loops.py, clayout.py
```

Reproduce: `harness/check.py p10`, then `harness/measure.py p10`, then
`harness/report.py p10-fir-stencil`. The domain refit:

```
python3 patterns/p10-fir-stencil/controls/gen_domain.py
python3 patterns/p10-fir-stencil/controls/sweep_ir.py --band d --cells all \
    --inputs .temp/p10/domain --json .temp/p10/sweep_d.json
python3 patterns/p10-fir-stencil/controls/fit.py \
    --json .temp/p10/sweep_r.json,.temp/p10/sweep_o.json,.temp/p10/sweep_d.json \
    --holdout .temp/p10/sweep_h.json,.temp/p10/sweep_e.json \
    --pair safe_tuned,unsafe --cols 1,nout,scaltap,novecout,rejwin,rejfar,fence
```

and the closing proof of the `u_win` control (`NOTES.md` 8e):

```
python3 patterns/p10-fir-stencil/controls/gen_controls.py
./verus_run.py .temp/p10/ctl/u_win_verus.rs        # 10 verified, 0 errors
```
