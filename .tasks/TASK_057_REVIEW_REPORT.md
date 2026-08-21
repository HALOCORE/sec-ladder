# TASK_057_REVIEW_REPORT — p10-fir-stencil

Reviewer, adversarial. Box was quiet throughout (`load average 0.49` at the start
of the timing runs; no other agent). Scratch, probes, logs and re-measurements
under `.temp/p10rev/`. **No file under `patterns/`, `.memory/`, `harness/`,
`common/` or `pilot/` was edited.** `harness/check.py p10` was re-run once (the
task permits it); no other pattern's gate was touched.

**Verdict: p10 is a good pattern with a correct measurement layer and three
attributions that do not survive.** Every fitted law, every control figure, every
pad count, every loop-body count and the whole Verus layer reproduced exactly. The
defects are all in what the numbers are said to *mean* and in the domain the laws
are published over — plus one exclusion argument that is simply false.

---

## Findings

### B1 — blocker. `u_win` VERIFIES. The R4 side is not degenerate, and ~60% of the headline is R4 spelling.

`patterns/p10-fir-stencil/NOTES.md:754-793` (§8e), `README.md:71-75`.

Published: *"Its twin does not verify … the R4 side is DEGENERATE as far as this
task searched … the −194/−362 figure is a CONTROL and not a rung."*

Adding **one invariant clause** to `.temp/p10/ctl/u_win_verus2.rs` closes it:

```rust
w@ == buf@.subrange(off as int, off + len as int),   // in BOTH loop invariants
assert(w@ == buf@.subrange(off as int, off + len as int));   // after the reslice
```

```
$ ./verus_run.py .temp/p10rev/verus/u_win_verus3.rs
verification results:: 10 verified, 0 errors
```

Same obligation count as the shipped `verus.rs`. **No new trusted item** (still
three `external_body`), no lemma, no `by (nonlinear_arith)`. The engineer's own
repair round added `w@.len() == len` but never related `w@` to `buf@`, so the
`dotp` invariant — which is written over `buf@` — could not close; vstd *does*
ship a spec for `<[T]>::split_at` (`~/tools/verus/vstd/std_specs/slice.rs:176`)
and it gives the subrange directly.

Built under the shipping filenames (`unsafe.rs` / `verus.rs`) the pair is
identical except for **one** pc-relative displacement:

```
unsafe  n_fn 116  md5_fn 278a42aa…  md5_fn_norel aae0541c08aa18968178777857a80f57
verus   n_fn 116  md5_fn 79b86a69…  md5_fn_norel aae0541c08aa18968178777857a80f57
sole real difference:  lea -0xc7fb(%rip),%rdi   vs   lea -0xc7da(%rip),%rdi
                       (the panic Location pointer of the split_at reslice)
```

So `u_win` meets `identity: norel` at O3 but not `exact`. **That — not the proof —
is the real reason it cannot ship as written**, and it is a much sharper statement:
p10's `exact` pin implicitly excludes every R4 that contains a panic landing pad.

Consequence, all re-measured by me (`-O3 isolated`, differenced marginal,
`small` / `large`):

| | small | large |
|---|---:|---:|
| R4ship (`unsafe`) | 3591.00 | 8711.00 |
| `u_win` (admissible, twin 10/0) | 3397.00 | 8349.00 |
| R3ship (`safe_tuned`) | 3268.00 | 8108.00 |
| **published** `R3ship − R4ship` | **−323.00** | **−603.00** |
| **`R3ship − u_win`** | **−129.00** | **−241.00** |

**60.1% / 60.0% of the published margin is R4 spelling.** The sign survives; the
magnitude does not. This is `.memory/01-ladder.md` finding 14 (p13) repeating
exactly — *"safe beats unsafe is the price of a bound, and it reverses the moment
the unsafe rung is allowed one"* — and that entry says to quote the fiat whenever
the margin is quoted.

**Failure scenario:** `.memory/` records "p10: safe Rust is 323/603 Ir/call
cheaper than unsafe, R4 side degenerate". It becomes the project's strongest
safe-beats-unsafe citation. Six patterns later somebody spends eleven minutes on
`verus_run.py` — the thing `.memory/01-ladder.md:320` already tells them to do
before blaming vstd — and 60% of it evaporates.

### B2 — major. The headline is an `isolated`-mode figure. At `-O3 whole` it is −127.00 / −239.00.

`NOTES.md:539-542` (§8 preamble names the flags but not the mode's effect),
`NOTES.md:792-793`, `README.md:62-69`. `controls/sweep_ir.py` defaults
`--mode isolated` and nothing in NOTES or README says the headline is
mode-specific.

p10's **own gate record** carries both columns (`results/gate/p10-fir-stencil.json`,
`marginal_ir_per_call`):

| quantity | `-O3 isolated` (published) | `-O3 whole` |
|---|---:|---:|
| `R3 − R4` small / large | **−323.00 / −603.00** | **−127.00 / −239.00** |
| `R2 − R4` small / large | +2881.00 / +5345.00 | +1447.00 / +2679.00 |
| `R1h − R1` gcc | **0.00** | **−1.00** |
| `R1h − R1` clang | **+1.00** | **0.00** |

Three separate published statements are mode-specific and none says so:

1. the −323/−603 headline is **2.5×** the whole-mode figure;
2. `R2 − R4` halves;
3. *"the first free hardening in this project"* is **0.00 on gcc / +1.00 on clang**
   isolated and **−1.00 on gcc / 0.00 on clang** whole — i.e. in the whole column
   the hardened gcc cell is *cheaper*, and the clang `+1.00` (the one figure
   README:47 calls *"flat"*) is **zero**.

Note the whole-mode gap (−127 / −239) lands within 2 Ir of my B1-corrected
isolated gap (−129 / −241). Two independent routes to the same conclusion: most of
the isolated margin is LLVM failing to clean up R4's index arithmetic while the
kernel is opaque, and it disappears when the kernel is visible.

### B3 — major. The published *mechanism* for the negative sign cannot produce it. Here is the one that can.

`NOTES.md:1033-1041` (§13, P2 verdict), `README.md:62-68`.

Published: the panic-pad decode is offered as the reason `R3 − R4` is negative —
*"The predicted reason was right too ('the window slice is one range check however
many taps it covers'): the panic-pad decode in §8c shows R3's tap loop contributes
zero pads."*

The pads are real (I reproduced them exactly, see clean negative 10) but they can
only explain the `scaltap` coefficient, and **that coefficient is 0.00** — worth
zero Ir. The entire −323/−603 is the `−5.00·nout` term, and it is
induction-variable bookkeeping. Mnemonic by mnemonic, off the shipped `-O3
isolated` listing, executed path (vector loop entered), per output:

| block | R4 `unsafe` | R3 `safe_tuned` |
|---|---|---|
| outer head | `cmpq $0x7,-0x8(%rsp)` `ja` = **2** | `cmp $0x8,%r9` `jae` = **2** |
| vector preamble | `pxor` `xor` `pxor` = 3 (+1 nop) | `pxor` `xor` `pxor` = 3 (+1 nop) |
| horizontal reduce + epilogue setup | 5×SSE + `movd` + **four** `mov`, two of them **reloads from `-0x18(%rsp)` and `-0x10(%rsp)`** = **10** (+1 nop) | 5×SSE + `movd` + **one** `mov %r11,%r14` = **7** (+1 nop) |
| outer tail | Horner 5 + `mov` + **four** `inc` (`r14`,`r9`,`rdi`,`rbx`) + `cmp`/`jne` = **12** | Horner 5 + `mov` + **`dec %r8` + `inc %rcx`** + `cmp`/`jb` = **10** |
| **executed total** | **27 real + 2 nop = 29** | **22 real + 2 nop = 24** |

29 and 24 are *exactly* the fitted `nout` coefficients (I re-fitted:
`29.000015` / `24.000015`), and the 2 alignment `nop`s cancel, so **the −5.00 is
five real instructions**. R4's tap index `off + sb + i + j` and coefficient index
`off + 8 + j` force LLVM to strength-reduce to **four** outer-loop induction
variables and to spill two epilogue starting values, reloading them once per
output; `windows()` hands LLVM one advancing pointer plus a trip counter and `zip`
hands the epilogue one index.

**It is not a safe-vs-unsafe effect.** `c-clang` — idiomatic C, same four-term
index expression — fits `nout` at **30.00**, dearer per output than *both* Rust
rungs. The cheapest per-output cell in the whole pattern is the safe one. The
same measurement, stated the way p10 could have: kernel-exclusive on `small`,
`safe_tuned` **3254.00** vs `c-clang` **3514.00** vs `c-gcc` **3783.00** — the
safe Rust rung beats both C cells by 260 and 529 Ir/call. (No `ns` claim goes
with that: `clayout.py` builds one language per invocation, so the C and Rust
populations are different timing sessions and `.memory/00-environment.md` forbids
quoting across them — NOTES §11 says so and is right.) **p10 measured a
safe-Rust-beats-C result in `Ir` and published a safe-Rust-beats-unsafe-Rust
one.**

The honest headline is *"the iterator form beats the four-term-index form by
5–6 Ir per output in every language, and safe Rust is where the iterator form
lives"*, which is a stronger and more transferable finding than the one shipped.

### M4 — major. The law's fifth parameter is a REJECTED CALL, and the published law is exact only where every visited window is accepted.

`NOTES.md:566-577` (§8b). §8a says *"I cannot claim the list is closed"* — this is
what it was not claiming.

Eight new blobs (`.temp/p10rev/gen_attack.py`, reusing `inputs/gen.py`'s own
`window`/`emit`/`kern`), measured with a repointed copy of `controls/sweep_ir.py`
(`.temp/p10rev/sweep_rev.py`, `INPUTS` → `.temp/p10rev/blobs`).

**What did NOT break** (clean negatives 6–8): `r = 0` (taps 1), `nout = 1`,
`nout = 2`, `taps = 65`, `taps = 97` — all outside every fit band, **all five laws
exact to 0.0000**.

**What broke:** any blob containing a window with `taps > n`. Residuals are
*exactly* linear in the rejected-call fraction:

```
blob        rejfrac      R2-R4       R3-R4       R2-R3   R1h-R1 clang   (residual / rejected call)
x-rej1.bin   0.5205   -14.0000    +22.0000    -36.0000        -2.0000
x-rej2.bin   0.4980   -14.0000    +22.0000    -36.0000        -2.0000
x-mix.bin    0.1685   -14.0000    +22.0000    -36.0000        -2.0000
```

Confirmed directly on a 100%-rejecting blob (`.temp/p10rev/blobs/x-allrej.bin`,
Ir/call): `c-gcc` 59, `c-gcc-h` 59, `c-clang` 43, `c-clang-h` **42**, R2 79,
R3 47, R4 28, R5 27. Every extended law is then exact:
`R2−R4 = 65−14 = 51 = 79−28`; `R3−R4 = −3+22 = 19 = 47−28`;
`R2−R3 = 68−36 = 32`; `R1h−R1 clang = 1−2 = −1 = 42−43`.

So the law needs a `rej` column. **And a sixth parameter behind it:** which guard
rejects. On `x-allrej2.bin` (rejection at `last >= len` instead of `n < taps`) the
same rungs read R2 84, R3 51, R4 32, R5 31 — each +4/+5, so `R2−R4` moves to 52.

Two consequences: (a) *"`R1h − R1` (clang) = +1 flat"* (`README.md:47`,
`NOTES.md:257`) is **false** outside the accepting domain — it is −1 there;
(b) the 40/40 band-`e` registration and the band-`h` hold-out are both entirely
inside the accepting domain, so they could not have caught this.

**Failure scenario:** the law reaches `.memory/` as p10's transferable result; the
next pattern applies it to traffic where most windows are malformed — which is
what a security benchmark's traffic looks like — and the per-call constant is
wrong by 22 Ir with the wrong sign.

**Bonus datum from the same probe, which p10 should want:** on `x-allrej2.bin`,
crafted so *every* call hits the fencepost, `c-gcc` reads **1942.00** Ir/call
against `c-gcc-h`'s **62.00**, and `c-clang` **1800.00** against **46.00**. That
is the bug's actual price and it is not zero. NOTES §4's caveat that no cost is
read off the adversarial inputs is correct and this does not contradict it — but
*"hardening is free"* is a statement about the benign domain only, and no p10
input exercises the other one at scale.

### M5 — major. The two disclosed corrections did not reach the shipped rung sources, and there is an undisclosed third.

Exactly the failure mode PROTOCOL rule 9 exists for: `.memory/` gets written from
`NOTES.md` and the tree keeps contradicting it.

1. `patterns/p10-fir-stencil/safe_naive.rs:10` — still *"an SSE2 body of seventeen
   instructions per eight taps, **byte-identical to `unsafe.rs`'s**"*. Retracted
   at `NOTES.md:156-158`.
2. `patterns/p10-fir-stencil/safe_naive.rs:13` and `unsafe.rs:19` — still
   *"**22-instruction** per-output `cmp`/`cmov` chain"*. Corrected to 24 at
   `NOTES.md:690-692` and `README.md:16`. I counted it on the shipped listing:
   **24** (`mov 0x38(%rsp),%rax` … `cmp $0x8,%rdx` / `jae`).
3. `patterns/p10-fir-stencil/NOTES.md:1063` — the §13 verdict paragraph *still*
   says "22-instruction", 370 lines below the §8c paragraph that corrects it. The
   correction did not reach the same file.
4. **Undisclosed.** `patterns/p10-fir-stencil/unsafe.rs:22-24`:
   *"⚠ **AND SAFE RUST IS CHEAPER PER SCALAR-EPILOGUE TAP THAN THIS RUNG IS** —
   7.00 against 9.00"*. That is the **day-one probe's** number
   (`.temp/p10/NOTES.md:72`). On the shipped cells R3 and R4 both cost **9** per
   epilogue tap (`NOTES.md:646-650`, and `controls/loops.py` on my rebuild:
   `safe_tuned` body=9, `unsafe` body=9) and the fitted `scaltap` coefficient of
   `R3 − R4` is **exactly 0.00**. So the shipped R4's own doc comment states a
   superseded figure, in the direction that flatters the pattern's headline, and
   `NOTES.md:1043-1050` discloses the probe/ship discrepancy without noticing the
   probe figure is still in `unsafe.rs`.

### M6 — minor→major. The backlog item is retired on a one-instruction win, against `.memory/03-measurement.md`'s explicit rule.

`NOTES.md:741-748`: *"THE TWO-STEP RESLICE … IS WORTH −1.00 Ir/CALL ON p10, ON
BOTH BLOBS … a clean positive, and the standing backlog item can be retired."*

Reproduced exactly: shipped R3 **3268.00 / 8108.00**, `t_1step` **3269.00 /
8109.00**. The win is one instruction.

`.memory/03-measurement.md` (the paragraph closing the p08 retraction section):
*"Rule: **a spelling whose win is one instruction wide cannot be quoted on `Ir`
alone, and this box cannot supply the wall-clock column to rescue it** — say the
win is instruction-count-only and stop."* p10 quotes it on `Ir` alone, offers no
`ns` support (§11's populations do not separate the two spellings), and retires a
project-wide backlog item on it. The number is right; the conclusion overreaches
the project's own rule.

### Minors

- **m1 — the disclosure's arithmetic.** `NOTES.md:951-963` says the audit found
  **five** backticked spellings that pinned nothing and *"The backticks were
  removed from those five"*. The audit totals it then quotes at `:990-993`
  (43→37 spellings, 126→108 pairs = 18 pairs) require **six** removals. The sixth
  is `get_unchecked`, disclosed twenty lines later at `:983-988`. The prose and
  the arithmetic disagree at `:963`.
- **m2 — level-law residual.** `NOTES.md:579-581` quotes *"max |resid| 0.0096 in
  sample / 0.0056 out"* over a five-row table that includes `c-clang`. Re-fitted:
  the four Rust rows are 0.0096/0.0056; **`c-clang` is 0.0239 / 0.0121**. Both are
  the `println!` digit term; the number in the text covers four of the five rows.
- **m3 — `required_absent: 2`.** It is the entry doing its job: `required[0].c`
  backticks both `if (last >= len)` and `if (last > len)` so a grep settles which
  C rung has the bug, and each rung contains exactly one. But nothing
  machine-readable marks the row as intended, so the audit line is
  indistinguishable from a pin that missed (p18's `required[0]` reports 0). Not a
  defect in p10; a gap in the audit's vocabulary, and worth one sentence in
  `.memory/02-bench-rules.md` if it recurs.
- **m4 — a second objdump pipeline.** `patterns/p10-fir-stencil/controls/loops.py:28`
  calls `/usr/bin/objdump` directly; `CLAUDE.md:27` says `harness/asm.py` is *"the
  only objdump caller"* and `.memory/03-measurement.md` records what happened last
  time there were two. p10's `vecit = 17.00` and `scaltap = 7/9/9/12` come off that
  second pipeline. I checked it against `asm.py`'s listing and it agrees exactly,
  and four other patterns (`p08`, `p12`, `p14`, `p16` controls) already do the same
  thing — so the stale artefact is the CLAUDE.md sentence, not p10. Reporting, not
  fixing.
- **m5 — adjacent, not p10.** `harness/measure.py --check-stale` reports
  **1 STALE**: `results/gate/p08-overlap-move.json` against
  `patterns/p08-overlap-move/NOTES.md` and `README.md`. The task file and
  `RECAP.md` both say 0 STALE. Doc-only; no measured number is affected; but the
  claim in the task file is currently false.
- **m6 — a premise in the task file.** It says *"`NOTES.md` §0's **four** rejected
  candidates"*; the table at `NOTES.md:80-84` has **five**. And they were rejected
  on **argument**, not on measurement — with one exception: `nout = n − 2r + 1` is
  ruled out by a structural fact about the gate, which I verified by reading
  `harness/check.py:1254-1292` (`check_checksums` runs every built cell against
  every non-`adversarial-*` model input and hard-fails a mismatch). The arguments
  are sound and two of them are strong (a clamping bug deletes `windows()`, hence
  the whole three-way separation; `hi = n−1` is p07's bug with a different harm),
  but *"rejected on measurements"* is not what happened.

---

## Clean negatives — 21 attacks that did NOT land

1. **A2, gcc: the compiler did not delete the check.** `c-gcc` vs `c-gcc-h`
   kernels differ in exactly two lines of a 216-instruction listing, and both are
   the fencepost compare: `cmp %rcx,%rax ; jb` vs `cmp %rax,%rcx ; jae`. Operands
   swapped, condition inverted, instruction count identical (216 = 216, `n_fn`
   from `clayout_rev.py`). Register roles verified from the prologue:
   `rcx = 8+taps+n-1 = last`, `rax = len`. Both cells reject `farover`; only the
   hardened one rejects `fencepost`. **"Free hardening" is real on gcc.**
2. **A2, clang: the +1.00 is a `jmp`, not a check.** Static counts equal
   (120 = 120). In `c-clang` the shared `return 0` block (`xor %eax,%eax ; jmp`)
   sits inline at `kernel+0x4e` and the success path *takes* the `jbe` over it; in
   `c-clang-h` the block is sunk to the tail and the success path falls through,
   then pays `jmp <epilogue>` to skip the `xor`. Both execute exactly one `cmp`
   and one `jcc` for the fencepost. The engineer's tail-merge description is
   accurate.
3. **A1, the convention: the sign is the same in BOTH `Ir` conventions.**
   Kernel-exclusive per call from `results/p10-fir-stencil.json`: `safe_tuned`
   65,080,000/20,000 = **3254.00** vs `unsafe` 71,540,000/20,000 = **3577.00** →
   **−323.00**; `large` 8094.00 vs 8697.00 → **−603.00** — identical to the
   whole-program marginal. `controls/sweep_ir.py`'s docstring claim that the two
   coincide on p10 (no libc call leaves the kernel symbol) is correct. p08's 13×
   divergence does not reproduce here.
4. **A3, Rust `ns`, re-taken on a quiet box** (24 layouts × 7 reps, cpu 5,
   `.temp/p10rev/clayout_rev.py`): `safe_tuned` **209.53–213.77** (median 212.27)
   vs `unsafe` **229.03–232.52** (median 231.36). **Bands still disjoint**,
   −8.25% at the medians. Spreads *tightened* against the contended run
   (safe_tuned 3.78% → 2.02%; unsafe 1.84% → 1.52%). The null control still
   overlaps: `verus` 227.64–231.77 (median 230.55) vs `unsafe` 229.03–232.52. **The
   `ns` half of the headline survives; the manager's prediction was right.**
5. **A3, C `ns`, re-taken** (30 layouts): `c-gcc` 250.74–257.27 (median 253.94) vs
   `c-gcc-h` 251.63–256.94 (median **253.45**) — the *hardened* cell is now
   marginally faster, where the first run had it marginally slower;
   `c-clang` 228.46 vs `c-clang-h` 228.66. Overlapping in both directions across
   two sessions, which is exactly the engineer's "not resolvable on this box".
6. **A4, `r = 0`** (taps 1, below every fit band): all five laws **exact to
   0.0000**.
7. **A4, `nout = 1` and `nout = 2`** (band `o` starts at 8): **0.0000**.
8. **A4, `taps = 65` and `taps = 97`** (band `r` stops at 33, so `vecit` is 4× and
   12× out of hull): **0.0000**. Additivity extrapolation holds well outside the
   registered band `e`.
9. **Semantic equivalence outside the shipped input set.** All eight cells produce
   **bit-identical** checksums on all eight benign attack blobs — `r=0`, `nout=1`,
   `taps=97`, and the three heterogeneous ones with rejected windows. No rung
   quietly changed the algorithm. (And on `x-allrej2.bin`, where every call hits
   the fencepost, `c-gcc`/`c-clang` emit a fold while the other six cells return 0
   — the bug isolated to one line.)
10. **Panic pads reproduce exactly**, decoded (not counted) with
    `patterns/p12-strcat-fixed/controls/pads.py --source`: R2 **10** (eight header
    decode, `63:18` the sample tap, `63:61` the coefficient tap), R3 **2** (both
    `60:24`/`60:40`, `buf.split_at(off).1.split_at(len).0`), R4 **0**, R5 **0**.
    R3's tap loop contributes zero, and `&w[8..8+taps]` / `&w[8+taps..8+taps+n]`
    contribute zero as well. The pad claim in §8c is right; only what is inferred
    from it (B3) is not.
11. **Loop bodies and padding reproduce**: `controls/loops.py` on my rebuild gives
    vector body **17 / nops_inside=0** on all four LLVM cells; scalar epilogue
    **9 / 9 / 12 / 7** with **0** nops inside; outer spans 59 / 53 / 103 / 58 with
    2–3 nops. `vecit = 17.00` and the `scaltap` coefficients are genuinely
    padding-free, and the §8c warning that the per-output ones are not is correct.
12. **Every fitted law reproduces exactly** (`controls/fit.py`, my re-run):
    `R2−R4 = 65 + 41·nout + 3·scaltap − 7·novecout`,
    `R3−R4 = −3 − 5·nout + 0·scaltap − 1·novecout`,
    `R2−R3 = 68 + 46·nout + 3·scaltap − 6·novecout`, gcc `0`, clang `+1` — all at
    **max |resid| 0.0000 in sample (26 blobs) and 0.0000 out of sample on bands
    `h` AND `e`**. Level laws reproduce at `nout` 29 / 24 / 70 / 30 and
    `vecit` 17.00 on all four LLVM cells. Rank diagnostics reproduce: pooled 4 of
    4, **3** after dropping band `o`, **2** after dropping band `r` — neither band
    redundant, exactly as §8f claims, and p18's defect does not repeat.
13. **The level law has zero free parameters, which is stronger than published.**
    29 / 24 / 70 are exactly the *executed* outer-loop instruction counts off the
    listing — outer span minus both inner bodies minus the three-instruction
    no-vector path (and its `nop`): R4 59−17−9−3−1 = **29**, R3 53−17−9−3 = **24**,
    R2 103−17−12−3−1 = **70**. Nothing in the level law is fitted.
14. **`global size_of usize == 8;` is CHECKED, not assumed — verified directly.**
    A probe declaring `global size_of usize == 4;` on this box **fails to
    compile**: `error[E0080] … evaluation of '_' failed here`; `== 8` gives
    `2 verified, 0 errors`. So it is not an axiom, adds nothing to the TCB, needs
    no gate fiat, and a 32-bit build would fail to *compile* rather than verify
    unsoundly. §6b's error text reproduces exactly: deleting the line from the
    shipped `verus.rs` gives `9 verified, 1 errors` with `possible arithmetic
    underflow/overflow` at `:306` (`2 * r + 1`) and `:313` (`8 + taps + n - 1`).
    The claim that p10 cannot take p07's `u64` route also holds — `required[2]`
    pins `2 * r + 1` in all seven rungs and `spelling_matches` deletes whitespace,
    so `2 * (r as u64) + 1` does not match.
15. **Verus layer, re-run.** Shipped `verus.rs` → **`10 verified, 0 errors`**;
    `--cfg slb_twin` → **`11 verified, 0 errors`**. `grep -n
    'assume\|external_body\|external\b\|assume_specification'`: **no `assume`
    anywhere**; three `external_body` items (`buf_get_unchecked:223`,
    `load_input:256`, `emit:268`), matching the gate's `tcb_items` = 3 and the
    NOTES tally. The kernel `ensures` is the full functional spec
    `r == fir_fold(buf@, off, len)`, not memory-safety-only. Gate's
    `clause_deletion` (3 mutants all fire), `requires_strength` (`not a tautology`
    on both clauses, plus deletion) and `verified_twins` (`load_bearing 1 of 1`)
    all fire.
16. **Gate reproducibility.** `harness/check.py p10` re-run by me → **PASS**,
    `complete_run: true`, `failures`/`loud`/`blocked` all empty,
    `contract_sha256` unchanged at `cb1c3c9f…`. The **only** byte that moved in
    `results/gate/p10-fir-stencil.json` is the ASan PID and addresses inside one
    diagnostic string. (That one-line diff is in the working tree now — revert or
    keep, it is inert.)
17. **Every control figure in §8d reproduces on my own rebuild** (`gen_controls.py
    --build` then my `sweep_rev.py`): shipped R3 3268.00/8108.00, `t_winidx`
    3264/8104 (−4.00), `t_1step` 3269/8109 (+1.00), `t_fold` 3268/8108 (0.00),
    `x_sum` 3268/8108 (0.00), `n_2step` 5645/12557, `u_win` 3397/8349,
    `b_fence` 3590/8710. The `.sum(` exclusion really does cost 0.00, and the
    cheapest-found in-contract R3 really is `t_winidx`.
18. **A5 — the R3 spelling was NOT cherry-picked, and the direction test has
    nothing to bite on.** The day-one probe (`.temp/p10/probe/`, mtimes
    11:38–11:43) measured five spellings before `safe_tuned.rs` existed (11:56),
    and `pr_r3c` (`windows()` + indexed inner loop) was **cheaper** than `pr_r3a`
    (`windows()` + `zip`). The engineer shipped `pr_r3a`'s spelling — the *dearer*
    one — and shipped `pr_r3c`'s as the control `t_winidx`, 4.00 Ir/call cheaper
    on both blobs. The `idiom` block pins no tap-loop spelling, so there is no
    declaration edit for the direction test to act on; the `idiom_sha256` move
    (`066841a9…` → `22af8747…`) is the backtick removal alone, and I checked it
    changes no rung's admissibility except to stop excluding the two safe rungs.
    **The disclosure is honest and the scoring is right** — the residual defect is
    M5.4 (the stale probe figure still sitting in `unsafe.rs`), not the choice.
19. **§7c's R4/R5 whole-program −1.00 is real and is in `main`.**
    `main_exclusive_ir` 280,275 (`unsafe`) vs 260,274 (`verus`) on `small` =
    exactly −1 per iteration and −1 fixed; kernel-exclusive identical at
    71,540,000 both, `md5_fn` equal at O3. The instruction to quote the
    kernel-exclusive column for an identity claim is right.
20. **The "no gcc level law" negative is honest.** I reproduced the best design at
    max |resid| **45.2645** in sample / 40.4563 out (`1,nout,v16,h8,t8,nov16out`)
    and tried three designs the engineer did not name: a 7th column makes it
    *worse* in sample (48.2141), a taps-linear design gives 1117.9, and the LLVM
    five-column shape at width 16 gives 521.6. Nothing rescues it; the three-regime
    mechanism in §1 is the right explanation.
21. **Bug class and algorithm hold up.** All seven rungs run the same
    O(nout·taps) tap loop (same 17-instruction SSE2 body); `grep -cE '\b(div|idiv)\b'`
    is **0** on all eight `-O3 isolated` kernels, so the `div` hazard was really
    priced out; the two C kernels differ in exactly one character of code (`diff`
    shows only comment blocks and `if (last > len)` vs `if (last >= len)`); the C
    rung is idiomatic C99, not Rust-in-C-syntax.

---

## Gatekeeping the four `.memory/` candidates

I do not have the engineer's return message, so I am gating by subject. Land only
with these edits:

| candidate | verdict |
|---|---|
| **the per-tap tax law** (0.00 on vectorised taps, +3.00 on epilogue taps, 41.00/output) | **LAND**, with the domain from M4 (`+ rej` column) and B2's mode named. The `+3.00` mechanism decomposition (5 check instructions − 2 saved pointer bumps) is correct and reproduced. |
| **`global size_of usize == 8;`** | **LAND AS IS.** Verified checked-not-assumed by direct experiment (clean negative 14). It is the cleanest new Verus fact on the pattern. Add: *a wrong declaration is an `E0080` at compile time, so a 32-bit target cannot be built at all.* |
| **"the first free hardening in this project"** | **DO NOT LAND as written.** It is `-O3 isolated`-only (B2: gcc −1.00 and clang 0.00 in `whole`), and it is a benign-domain-only statement (M4: −2.00 per rejected call on clang; 1880 Ir/call on the fencepost input). Land as *"the first hardening whose cost is zero on the benign domain **because R1 already performs the comparison** — 0.00 gcc / +1.00 clang isolated, −1.00 gcc / 0.00 clang whole"*. |
| **"the first byte-identical R4/R5 pair whose whole-program marginals differ"** | **LAND AS IS.** Verified (clean negative 19). |
| **(implied) "safe Rust is cheaper than unsafe Rust, −323/−603"** | **DO NOT LAND.** B1 (the R4 side is not degenerate; −129/−241 against an admissible `u_win`), B2 (−127/−239 at `whole`), B3 (the mechanism is the index expression, not the check, and C pays it too). If a number goes in, it should be *"the iterator form beats the four-term-index form by 5 Ir/output in C and in both Rust rungs"*. |

---

## Reproducing this review

Everything under `.temp/p10rev/` is generator + evidence; every binary and blob
was deleted after the numbers were read (CLAUDE.md rule 1), and every one of them
is re-derivable:

```
.temp/p10rev/gen_attack.py     -> all TEN attack blobs (reuses inputs/gen.py's
                                  window/emit/kern, so the wire format is the
                                  shipped one by construction)
.temp/p10rev/sweep_rev.py      -> controls/sweep_ir.py with INPUTS repointed at
                                  .temp/p10rev/blobs and per-PID scratch
.temp/p10rev/clayout_rev.py    -> controls/clayout.py with outdir() repointed
                                  (--lang rust|c --build --time --input small)
.temp/p10rev/verus/u_win_verus3.rs   the closing proof for B1  (10 verified, 0 errors)
.temp/p10rev/verus/g8.rs g4.rs g0.rs the global size_of probe  (clean negative 14)
.temp/p10rev/verus/noglobal.rs       verus.rs minus the global (clean negative 14)
.temp/p10rev/idty/{unsafe,verus}.rs  the u_win pair under shipping filenames
.temp/p10rev/asm/*.txt               the seven -O3 isolated kernel listings
.temp/p10rev/{attack,allrej}.json    the A4 measurements
.temp/p10rev/measurements.log        every layout population and sweep, verbatim
.temp/p10rev/gate_rev.log            my check.py p10 re-run (PASS)
```

## What I did not do

- Did not attempt an R4 cheaper than `u_win` (e.g. `get_unchecked` over a range),
  which would need a second trusted item and is out of a reviewer's scope.
- Did not re-run `harness/measure.py` (wall-clock records); the layout populations
  are the `ns` evidence and I re-took both.
- Did not check whether `u_win`'s exec source satisfies every `required` spelling
  by running the gate on it — I checked by hand (all eleven present; `split_at`
  is not forbidden and the shipped R3 already uses it), but the gate has not seen
  it.
- Did not run `check.py` on any other pattern.
- Did not attempt to reconstruct the engineer's four `.memory/` candidate texts;
  I gated by subject.
