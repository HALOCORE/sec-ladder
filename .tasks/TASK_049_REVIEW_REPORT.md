# TASK_049_REVIEW — p14's null is a 64-byte alignment mode, and the exact law's domain excludes every input the pattern models

**Role:** research reviewer. **Verdict:** the pattern is sound and its gate
reproduces; **two claims destined for `.memory/` are wrong, measured**, and
three published framings are misleading. No shipped p14 *number* falls — every
one I re-measured reproduced to four decimals.

Everything below was measured on this box during this review. Scripts and logs
are under `.temp/r49/` (`nullx.py`, `laynull.py`, `sweep_ir_r49.py`, `NOTES.md`,
`laynull1.log`, `laynull2.log`, `nullx_pass1.log`, `gate_p14.log`,
`probe.1525364/`, `flen/`, `mut/`, `vprobe/`). All scratch is per-PID.
`results/gate/p14-field-split.json` was rewritten by my own `check.py` run
(ASLR addresses only, 4 lines) and **restored with `git checkout --`**; the tree
is clean.

Running count of agents that contradicted the manager with a measurement: **76.**

---

## BLOCKERS

### B1 — the R4/R5 pair is not a null control. It is one biased draw from a 64-byte alignment mode, and on p14 it UNDER-states the layout floor it claims to bound.

**Where:** `patterns/p14-field-split/NOTES.md:1080-1084`;
`patterns/p14-field-split/README.md:71-77`; `.tasks/TASK_049_REPORT.md:86-88`
and its **memory-update item 5** (*"the R4/R5 identity pair is a free wall-clock
null control; 8.97% on p14, 8× the identical-copy floor"*).

The claim under attack, verbatim (`NOTES.md:1081-1084`): *"It costs nothing …
and it varies the **binary** rather than only the inode, **so it bounds layout
and link effects that an identical-copy floor cannot see.**"*

**First, the manager's own stated doubt is refuted.** `p06/controls/wall_span.py`
and `p14/controls/wall_span.py` are **byte-identical below the docstring except
for two path constants** (`diff` of both files from `import argparse` onward: 4
lines, `BUILD` and `SCRATCH`). Same protocol. And run **interleaved, one
session, one core, cpu 5, 11 reps × 5 copies** (`.temp/r49/nullx.py`), both
published numbers reproduce and the per-call scales are the same:

```
p06/unsafe  235.67 ns/call     p06 verus-unsafe = +2.81%   (published +3.00%)
p14/unsafe  249.30 ns/call     p14 verus-unsafe = +9.04%   (published +8.97%)
1 ns = 0.424% on p06, 0.401% on p14
```

So they *are* comparable measurements of the same quantity. The "different
kernels, different binaries, different protocols" escape is closed.

**Then the layout population settles it.** `.temp/r49/laynull.py` built **24
layouts per cell per pattern** (`-C llvm-args=-align-all-functions=0..8`, 14
`--symbol-ordering-file` permutations, plus the shipped build; `verus` built
through `verus_run.py --compile` with the same flags). CONTROL 1 holds on all
96 binaries: `n_fn` and `md5_fn_norel` single-valued per cell, 21 distinct
kernel addresses spanning both `addr % 32` residues, one stdout per pattern, and
**`verus`'s `md5_fn_norel` equals `unsafe`'s** on both patterns.

| | within-cell layout spread | R5−R4, shipped pair | R5−R4 over the population | median |
|---|---:|---:|---|---:|
| p06 `unsafe` / `verus` | 4.02% / 5.10% | **+2.29%** | −3.73% … +3.61% | **+0.27%** |
| p14 `unsafe` / `verus` | 13.22% / 13.75% | **+9.17%** | −10.28% … +10.98% | **+0.10%** |

(min-of-reps, 13 reps; the median-of-reps estimator gives +0.33% / −0.16%.)

**The R4/R5 gap has median ≈ 0 on both patterns.** The shipped figure is a
sample of size one whose magnitude is the *pattern's own alignment sensitivity*.

**And the mechanism, not asserted (PROTOCOL rule 11).** Sorting p14's 48 builds
by kernel address residue:

```
addr % 64 == 16  ->  264 .. 277 ns   (SLOW)
addr % 64 == 48  ->  244 .. 248 ns   (FAST)
addr % 64 == 0/32->  248 .. 255 ns
SHIPPED p14 unsafe  kernel @ 0x156b0  (%64 = 48)  245.19 ns
SHIPPED p14 verus   kernel @ 0x15690  (%64 = 16)  267.67 ns   => +9.2%, all of it
```

p06's shipped pair lands at **exactly the same two addresses** — `unsafe`
0x156b0, `verus` 0x15690 — with the same sign and only +2.29%, because p06's
kernel is 4% alignment-sensitive where p14's is 13%. The `verus` build's kernel
sits 0x20 below the `unsafe` build's on *both* patterns, so **the pair measures
the same fixed alignment contrast every time.** That is why p14's two "passes on
two different cores" agreed to 0.06 pp: it is a systematic bias, not a
reproducible effect and not a random draw.

**Concrete failure scenario.** The manager lands memory item 5 into
`.memory/03-measurement.md`. The next pattern measures its own R4/R5 pair, gets
(say) 1.2% because its two binaries happened to land in the same residue class,
publishes a 4% `ns` claim as "3× the null", and is wrong: that pattern's real
layout spread was never measured. The failure is not hypothetical — it is p14's
own numbers with the sign reversed. On p14 the pair reports **9.2%** where the
measured within-cell layout spread is **13.2%**, so the proposed control
under-states the very quantity the sentence says it bounds.

**What the honest floor is:** the layout population, which p06 has
(`p06/controls/clayout.py`, C cells) and p14 does not. The R4/R5 pair is worth
keeping as a *cheap smoke alarm* — a large value says "measure the layout
population" — but it is not a floor and it does not bound layout.

### B2 — §0a's "EXCLUDED BY THE HARNESS" is false, and it is aimed at `.memory/06-catalogue.md`.

**Where:** `patterns/p14-field-split/NOTES.md:37-72` (esp. `:60-65`);
`README.md:101-107`; `spec.md`'s `why` (*"which the driver's repeat protocol
forbids"*); `.tasks/TASK_049_REPORT.md:11-16` and **memory-update item 1**
(*"the guessed row is **excluded by the driver's repeat protocol**, measured"*).

The sentence at `NOTES.md:60-65`: *"So a rung that mutates `buf` cannot be
measured at all: the checksum is a function of `n_iters`, `harness/check.py`'s
checksum stage cannot pass, and `harness/measure.py`'s marginal is
meaningless."*

**The probe reproduces exactly.** I rebuilt `probe1-gcc` and `probe1-clang` from
the committed generators into `.temp/r49/probe.1525364/` and re-ran
`probe1_repeat.py`: the six-row table is byte-for-byte identical to
`NOTES.md:51-57`, on **both** compilers, `mutate` `False` and the other five
`True`. That part stands.

**The inference does not.** Three measurements:

1. **The mutating kernel reaches a steady state after exactly one call.** From
   the probe's own numbers, `r1 = 13685950752790025653` and
   `r2 = acc(2) − 31·r1 = 2990672519692479941`; substituting
   `r3 = r4 = r2` reproduces `acc(4) = 8033375426539182928` **exactly**. So
   `acc(n)` is a closed form in `(r1, r2, n)` — deterministic and predictable.
2. **`measure.py`'s marginal is exactly defined, not meaningless.** gcc,
   one-window blob, `(Ir(6000) − Ir(2000))/4000`:
   `cap 9779.0180 · bug 9265.0180 · strtok 10356.0180 · **mutate 9044.0000**`.
   The mutating kernel's marginal is *integral, with zero residual* — cleaner
   than the three "legal" ones.
3. **Nothing in `harness/` enforces purity.** `check.py`'s checksum stage
   (`harness/check.py:1249-1278`) compares each cell's stdout against
   `model.py`'s own simulation and against the other cells; the identity
   `acc(n) = r·Σ31^j` appears nowhere in `harness/` — it lives only in the
   engineer's `probe1_repeat.py`. `grep -rn 'repeat\|idempot\|purity' harness/`
   returns nothing relevant. The only obstacle is **p14's own `model.py:143-147`
   memoising `self._win[k]`**, which is a p14 design choice, not a harness
   constraint.

**The real objection is different and better, and it is missing.** After call 1
every delimiter has been overwritten with NUL, so calls 2…n scan a line with
**zero delimiters: one field of length `m` instead of four.** The steady state
measures *tokenising an already-tokenised buffer* — 9044 against `cap`'s 9779
Ir/call. That is the honest structural reason to reject an in-place tokenizer:
**the repeat protocol measures the wrong workload, not an unmeasurable one.**

**Concrete failure scenario.** The manager writes *"in-place mutation is
excluded by the driver's repeat protocol, measured"* into
`.memory/06-catalogue.md`. A later pattern (p18's `strsep`, p22's in-place
unescape, anything CWE-787-shaped that writes into its input) is rejected before
it is designed, on a constraint the harness does not have. The rejection would
have been correct for a different reason, and the reason matters, because the
repair for *this* reason (write a `model.py` that simulates the mutation, or
declare the steady state as the measured workload) is available and the repair
for the stated one is not.

---

## MAJOR

### M1 — the exact gcc hardening law was fitted entirely inside the regime where the safety line never executes, and on every input p14 exists to model it breaks with an inverted sign.

**Where:** `NOTES.md:391-411` (*"3a. gcc: `R1h − R1 = 1.00·bytes + 2.00·fields −
3.00`, exact on 66 blobs"*, under the heading *"3. What the safety line costs —
the headline, and it is a LAW"*); `README.md:55-60`.

All 66 sweep blobs have **≤ MAXTOK fields per line** (band `t` sweeps fields
1…16 at 8 lines; `sweep_ir.shape` caps `fields` at `MAXTOK` by construction), so
`if (nt == MAXTOK) break;` **never executes anywhere in the fit set**, nor on
`small` or `large`. Re-measured with my own copy of `sweep_ir.py`
(`.temp/r49/sweep_ir_r49.py`, per-PID scratch), gcc, whole-program marginal:

| blob | bytes | fields | law predicts | measured `c-gcc-h − c-gcc` | error |
|---|---:|---:|---:|---:|---:|
| `small` | 179 | 31 | +238.00 | **+238.000** | 0.000 |
| `large` | 52 | 21 | +91.00 | **+91.000** | 0.000 |
| `degenerate` | 92 | 25 | +139.00 | **+139.000** | 0.000 |
| `adversarial-run17` | 18 | 16 | +47.00 | **+16.036** | 30.96 |
| `adversarial-alt33` | 64 | 16 | +93.00 | **−551.036** | 644.04 |
| `adversarial-full65` | 64 | 16 | +93.00 | **−823.000** | 916.00 |
| `adversarial-many` | 176 | 128 | +429.00 | **−610.982** | 1039.98 |

(`degenerate` is a *new* out-of-sample confirmation — it is in no callgrind plan
and the engineer never used it. The law holds there, because its guard never
fires either.)

**So the pattern's headline law is the cost of a never-taken branch.** On all
four inputs where the guard does fire, **hardening is cheaper than the bug** — by
up to 823 Ir/call — because R1 goes on recording and folding the extra fields.
That is a *better* result than the one published and it is the one a reader of a
memory-safety benchmark wants: p14's safety line is free-or-negative exactly
where it matters.

**Failure scenario.** A reader quotes "+238 Ir/call, exact, out-of-sample" as
the cost of p14's bounds check. It is the cost on inputs where the check does
nothing. The paper sentence *"the safety line costs 1.00 per byte and 2.00 per
field"* is false on every adversarial row in p14's own §7 table.

**Fix:** state the domain (`nt ≤ MAXTOK` on every line) beside the law, and
publish the four adversarial rows as the complementary result.

### M2 — the leave-one-length-out test cannot fail, provably. p13's mistake in a new costume, exactly as the task suspected.

**Where:** `NOTES.md:398-402`, `README.md:56-58`, `.tasks/TASK_049_REPORT.md:57-59`
(*"leave-one-length-out worst error 0.0000 over 29 hold-outs"*, offered as
evidence for the law).

The law's max |residual| over `.temp/p14/sweep_all.json` is **0.0 exactly** (I
recomputed it), and the 4-regressor design `[const, nline, bytes, fields]` keeps
**rank 4 after dropping any whole band**:

```
full design rank 4;  drop all sweep-l* -> n=50 rank 4;  sweep-t* -> n=50 rank 4
                     drop all sweep-m* -> n=37 rank 4;  sweep-x* -> n=61 rank 4
```

An exact fit plus full rank means every hold-out's least-squares solution is the
*same* exact solution, which predicts the held-out rows exactly. **The LOLO
result is a corollary of the exactness, not independent evidence**, and it
cannot distinguish a real law from an over-parameterised one.

§9c's *"⚠ This test CAN fail"* paragraph does not rescue it: it demonstrates
failure on a **different fit** (`safe_tuned`'s own four-regressor model, rms
168.68 in sample). That shows the *procedure* can fail on a bad model; it does
not show that *this* hold-out could have failed. Compare p06, whose LOLO did
fail (−48.000 at `m=3`) precisely because its law was not exact.

**What does carry weight** is the out-of-sample perf-row prediction (+238.00 /
+91.00), which could have failed and did not — and which I extended with
`degenerate` (+139.00 predicted, +139.000 measured). Quote that, drop the LOLO,
or say what the LOLO adds.

### M3 — *"the first time both halves are readable in ONE listing"* is false, and it is contradicted by the file p14 cites for the constant.

**Where:** `NOTES.md:509-514`; `README.md:66-70`;
`.tasks/TASK_049_REPORT.md:66-68`.

p14 claims: *"p14 is the fourth kernel, and the first where the split is visible
in one listing: the same R4 executes the unchecked un-unrolled body (8.00) in
its epilogue and the unchecked unrolled body (5.75) in its main loop."*

`patterns/p16-tlv-walk/NOTES.md:563-568` already says, of the same constant:

> *"The 8.00 rolled-unchecked constant has four independent sightings, and **the
> cheapest is already in the shipped binary: R4's own remainder loop runs at 8
> insns/byte** — R2's body minus exactly `cmp`+`je`."*

beside p16's own 5.75 unrolled body (`p16/NOTES.md:505-515`, `:603-609`). p16
had both halves in one shipped listing at TASK_007_REVIEW. The reproduction on a
fourth kernel is real and worth having; the **"first"** is not.

(Secondary imprecision: p14's own sentence claims *both halves of the constant*
are readable off one function, but the 2.00 half needs R2's 10.00, which is a
different function. What is readable off R4 alone is the 2.25 unroll half.)

---

## MINOR

- **m1 — `pm3_msonly`'s error quote is incomplete.** `NOTES.md:1019-1021` shows
  `pm3_msonly: error: precondition not satisfied` and `:1043-1046` concludes
  *"it still fails, **at the same obligation**"*. I regenerated the mutant from
  the shipped `verus.rs` by the same substitutions and re-ran it: it emits
  **two** errors — `invariant not satisfied at end of loop body` at
  `nt <= MAXTOK` (mutant line 586) **and** `precondition not satisfied` at
  `tl_set_unchecked` — identical to `pm1_nocap`, whose row in the same table
  *does* list both. Both failing obligations are memory-safety obligations, so
  the conclusion **"memory safety alone suffices on p14"** survives; the
  wording *"the same obligation"* should be *"the same two obligations"*.
  Also worth stating: `pm3` is not literally a memory-safety-only spec — only
  the kernel's `ensures` is weakened, and the functional loop invariants
  (`tkg`/`stg`/`toks`) remain. The claim it actually tests is *"weakening the
  postcondition to `true` does not rescue the mutant"*, which is what it says
  everywhere except the `.memory/`-facing summary.
- **m2 — p06's ±3% floor is a slight under-estimate (a p06 correction, not a
  p14 one).** `patterns/p06-rotate/NOTES.md:353` says *"Take ±3% as the honest
  inter-binary floor for every `ns` figure in this file."* p06's own measured
  layout spread is **4.02% (`unsafe`) / 5.10% (`verus`)** and its R5−R4
  cross-pair range is **−4.31% … +4.61%**. p06's clang column (+9.78% / +10.56%)
  still clears **±4.6%** at ~2.1×, and p06's 30-layout C population defends the
  headline independently, so **nothing of p06's falls** — but the number in the
  text should be ±4.6%.
- **m3 — "the omitted line is literally `i < m`" is not what `k_unbnd` does.**
  `NOTES.md:123` and `spec.md:130`. `.temp/p14/probe1_kernel.c:~230` replaces
  `while (i <= m)` with `for (;;)` **and adds** `if (scr[i] == 0) break;`. The
  added NUL sentinel is exactly what makes it p11, so the *conclusion* is right
  and the *sentence* is not.
- **m4 — the `flen` entry's price is published for R4/R5 only.** `NOTES.md:719-727`
  gives the −O0 identity effect on `unsafe`/`verus`. Measured on all eight
  cells (below): −O3 price **zero everywhere**; −O0 price **+3 static
  instructions** on `safe_naive` (349→352), `safe_tuned` (347→350) and `unsafe`
  (286→289), 0 on `verus`. The R2/R3 half is not in the text.

---

## CLEAN NEGATIVES — attacks I ran that did NOT land

Named so nobody re-runs them.

**CN1 — "p06's 3.00% and p14's 8.97% are not comparable" (the manager's own
stated doubt).** Refuted twice: the two `wall_span.py` files are byte-identical
below the docstring except two path constants, and measured interleaved in one
session the per-call scales are 235.67 ns (p06) vs 249.30 ns (p14). Same
protocol, same scale, comparable.

**CN2 — "p14's 8.97% is an artefact of its own protocol" (item 1, option 3).**
Refuted. It reproduces at +9.04% in a session that simultaneously reproduces
p06's at +2.81%, and it has a named deterministic mechanism (`addr % 64`).

**CN3 — "p06's null was under-measured and its clang column does not clear it"
(item 1, option 2).** Refuted. p06's whole layout population spans 4.02–5.10%
and its cross-pair R5−R4 range is −4.31…+4.61%; the clang column (+9.78/+10.56%)
clears that, and p06's own 30-layout C population already showed clang `large`
+11.60% with no sign flip at any layout. **p06's headline stands intact.** (The
one correction is m2: the stated floor should be ±4.6%, not ±3%.)

**CN4 — §0a's probe table might not reproduce.** It does, byte-for-byte, on both
compilers, rebuilt from the committed generators (`probe1_gen.py`,
`probe1_kernel.c`, `probe1_main.c`, `probe1_repeat.py`) into fresh scratch. The
*measurement* in §0a is sound; only the inference is not (B2).

**CN5 — §0c's rejection of the lifetime candidate might be the "R4 is chained to
the prover" wrong explanation (the task's flagged risk, and p13's precedent).**
It is **not**. Run through `./verus_run.py` (`.temp/r49/vprobe/`):
`<[T]>::as_ptr` → `` is not supported ``; `core::slice::from_raw_parts` → `` is
not supported ``; `*p` and `*p.add(i)` → *"The verifier does not yet support …
dereferencing a raw pointer."* All three spellings the engineer names really are
unavailable, so a pointer-descriptor R4 has no verifying R5 twin without a new
`assume_specification` — i.e. a **new trusted item**, which the project's own
rule (p16's `r4_hdr`) disqualifies. Unlike p13's, this invocation of the
mechanism holds. *(One route was not tried and I flag it as open, not as a
defect: the error text points at `vstd::raw_ptr`'s permissioned interface; it
needs a `PointsTo` token, which a stack local `[u8; 64]` cannot supply, so I do
not expect it to change the answer.)*

**CN6 — §0c's "not observably wrong at -O3" refutes the manager's ranking.**
Confirmed. `k_life` prints byte-identical answers to `k_cap` at n = 1, 2 and 4
on both compilers in my rebuild. The engineer's refutation of the manager's
stated reason for ranking candidate 3 second is correct.

**CN7 — the corrupted sweep might have left survivors (item 5).** It did not. I
re-measured **8 cells × 8 sweep blobs** and **8 cells × 2 perf blobs**
independently with a `.temp/r49` copy of `sweep_ir.py` on per-PID scratch. Every
value matches `.temp/p14/sweep_all.json` and the published tables **to four
decimals**, including the `x08a`/`x08b` within-band negative control (+0.0360 on
the four C cells, +0.0103 on the four Rust ones) and `verus == unsafe` exactly.
The corrupt run reported "3654 and 11550"; the correct value is
**3653.9898 for both**, so the corrupt run's `unsafe` reading was the good one
and its `verus` reading was the bad one — and the re-measure agrees with neither
survivor. Spot values reproduced: R2−R4 +908.00/+364.00, R3−R4 +638.00/+425.00,
R5−R4 0.00/0.00, `c-gcc-h − c-gcc` +238/+91, `c-clang-h − c-clang` +663/+237,
R3−R2 +61.00 on `large`, band-`t` endpoints 3099.00 → 1683.00 (6.456 → 3.506 per
line byte).

**CN8 — the gate might not reproduce.** It does. `harness/check.py p14`:
`verdict PASS`, `complete_run true`, `failures []`, `contract_sha256
91b88dd83c9b…` (matches the report), `verus.rs: 19 verified, 0 errors` +
`23 verified, 0 errors` under `--cfg slb_twin`, 4 verified twins, sanitizer
`fires` on the four overflow inputs, **Miri 8/8 no UB**. Only the four ASLR
addresses in the sanitizer diagnostics changed in the gate JSON; restored.

**CN9 — the TCB tally might be wrong or the classification might not survive.**
Recounted: `#[verifier::external_body]` occurs exactly **6** times in
`verus.rs` (309, 343, 367, 404, 471, 483); body lines 1+1+1+3+4+1 = **11**;
matches the gate's `tcb_items` and `NOTES.md:649-662`. No `assume`, no
`assume_specification`, no bare `#[verifier::external]`. Classification 4
U-license + 2 infra is consistent with `.memory/04-verus.md`. `scr_load`
(`verus.rs:448-461`) genuinely carries no `external_body` — **verified, not
trusted**, confirmed. And the non-removability claim is measured, not assumed:
`grep -rn 'get_unchecked' ~/tools/verus/vstd/` returns **zero** hits, and Verus
answers `` `core::slice::impl&%0::get_unchecked` is not supported ``. The three
getters' `ensures` (`r == v@[i]`) and the setter's (`final(v)@ ==
old(v)@.update(i, x)`) match real Rust semantics; none axiomatises a falsehood.

**CN10 — the `flen` idiom entry might be self-certification (item 3).** It is
not, and the disclosure is adequate. I built the excluded spelling
(`tl[nt] = i - s;` direct) on **all seven rungs** (`.temp/r49/flen/`):

```
-O3 md5_fn_norel, shipped vs no-flen:  IDENTICAL on all eight cells
    safe_naive 2a992db908f4   safe_tuned 25d6577d1e72   unsafe/verus 9bdc8469333f
    c-gcc 1ec5fb96b686  c-gcc-h 75520cc35378  c-clang 225c9010d85e  c-clang-h ff0e2147f37c
    (unsafe and verus md5_raw 3cfea50590f84bad both, with and without)
-O0 without flen: unsafe n_fn 289 / 9641ed816dbccb53 vs verus 286 / aca735c40ab62961
-O0 with    flen: both 286 / d962daf7ed40a505
```

— reproducing `NOTES.md:713-727` exactly, including the published digests.
`verus_noflen.rs` **verifies 19/0**, so the entry is a **fiat the prover does
not force**, and its price on every published figure is **0.0000**. Direction
test: the entry moves p14's published safety tax by exactly zero, so it cannot
be self-certification under `.memory/01-ladder.md`'s PROVISIONAL repair. It is
also **whole-pattern, not scoped**, which is the shape p13's blocker was not.
Disclosure is sufficient; the entry stays. (Only m4 above: publish the R2/R3
−O0 half of the price too.)

**CN11 — the two out-of-contract fiats might be thumbs on the scale (item 3,
second half).** Direction test run in writing on both, and both go **against**
interest:

| fiat | if it were admitted | published figure | direction |
|---|---|---|---|
| `c_hcond` | R1h `small` 4244.96 (gcc, dearer) / `large` 2171.98 (cheaper) | tax +238.00 / +91.00 | excluding it **raises** the gcc `large` tax by 8.00 and lowers nothing |
| `t_pos` | R3 `small` 3953.99 / `large` 2521.99 | R3−R4 +638.00 / +425.00 | excluding it **raises** the published safe-side tax from +300.00 → +638.00 and +340.00 → +425.00 |

For a safety-tax number the flattering direction is *down*; both exclusions push
*up*. Both are legitimate fiats, both are priced beside the number they protect
(`NOTES.md:475-499`, `:793-830`), and the engineer's *"a judgement I made, not a
measurement"* is now a measurement and it comes out in the pattern's disfavour.
Nothing to fix.

**CN12 — the band-`t` axis mechanism might be asserted rather than controlled
(PROTOCOL rule 11).** It is controlled. R2's +18.00/field and R4's +29.80/field
are read off the shipped marginals (I reproduced both endpoints), and §9b's
**zero-parameter** fold law — read off `objdump`, no fitted constants — predicts
R4's non-linearity forward across the band at worst residual 0.0177. That law
*can* fail: the engineer demonstrates that dropping the `xchg %ax,%ax` from the
derivation makes it wrong by exactly 1.00 per field. This is the strongest
mechanism claim in the delivery.

**CN13 — a published p14 figure might depend on the missing layout population.**
None does: p14 publishes no `ns` claim (the only `ns` figures in the tree are
the withdrawn table at `NOTES.md:1066-1072`). And the `win32`/`jcc32` question
is now **asked and answered** by my population: p14's kernel has **two** 32-byte
loop geometries over 24 layouts, and the slow class (`addr%64 == 16`) costs
6–9% more than the fast one (`%64 == 48`). p14 is a strongly layout-sensitive
kernel; that is worth recording.

**CN14 — a claim might rest on an `-O0` row.** None does.
`results/tables/p14-field-split.md:144,172` carry the standard banner and
`NOTES.md:1102-1105` says explicitly that nobody looked. Confirmed by reading
every `-O0` mention.

**CN15 — R1 vs R1h might differ by more than one line.** It does not.
`diff` of `c/kernel.c` against `c/kernel_hardened.c` with comments stripped:
the only code difference is `if (nt == MAXTOK) break;`.

**CN16 — the `vec` column might mean a vectorised split (`NOTES.md:289-300`).**
It does not. `harness/asm.py show --sym kernel`: gcc's kernel has `pxor` ×1 +
`movaps` ×4 and clang's/Rust's `xorps` ×1 + `movaps` ×12, and every store is to
`(%rsp)` — 12 × 16 = 192 bytes = `scr[64]` + `tl[16]×8`. All zero-fill; the
delimiter search is scalar in all eight cells, as claimed.

**CN17 — candidate 1 might not really be p11.** It is close enough that the
rejection stands: `k_unbnd`'s scan is p11's sentinel-bounded `strlen` shape
(NUL exit) with a `DELIM` exit added, the harm is an OOB read, and p11's finding
9 already owns the constant. Only the *sentence* is wrong (m3).

---

## What I did not do

- Did **not** build a Rust layout population for `safe_naive` / `safe_tuned`, so
  p14's `+13.05%` and `+9.93%` rung comparisons are bounded only by the `unsafe`
  and `verus` spreads I measured (13.2% / 13.8%) — which is already enough to
  withdraw them, as p14 does.
- Did **not** try `vstd::raw_ptr` as an alternative route for candidate 3's R4
  (CN5). I do not expect it to change the answer, but it is untested.
- Did **not** re-derive clang's `+663.00` mnemonic table (`NOTES.md:446-474`) or
  re-run `attr.py`; I re-measured the *totals* only (+663.00 / +237.00, both
  exact).
- Did **not** independently re-implement `model.py`; I relied on the gate's
  checksum stage plus Miri 8/8.
- Did **not** touch `pilot/`, `.memory/`, `harness/`, `common/`, or any pattern
  directory. The only tree change was `results/gate/p14-field-split.json`
  (ASLR addresses, from my own `check.py` run), restored with `git checkout --`.

## Suggested `.memory/` disposition (for the manager, who applies these)

- **Do not land report memory item 5 as written.** Replace with: *the R4/R5 pair
  varies one fixed alignment contrast (the `verus` build's kernel sits 0x20
  below the `unsafe` build's on p06 and p14 alike), so it is a biased sample of
  size one; its median over a layout population is ≈0 on both patterns and its
  magnitude is the pattern's alignment sensitivity. Use it as a smoke alarm, not
  as a floor. The floor is the layout population.*
- **Do not land report memory item 1 as written.** The harness does not exclude
  an in-place tokenizer; the repeat protocol drives it into a one-call steady
  state that measures a different workload. Say that.
- Items 2, 3, 4, 6 and 7 are unattacked by this review except where noted and
  look landable; item 4's trap-3 instances I did not re-derive.
- The p06 correction (m2) belongs in `patterns/p06-rotate/NOTES.md:353`, not in
  `.memory/`.
