# TASK_042_REVIEW — report

Reviewer's return message, recorded verbatim in substance. p04 (ring buffer),
reviewed against `.tasks/TASK_042_REVIEW.md`. **One blocker, three majors, four
minors, and a long list of clean negatives** — several of which are worth more
than the findings, because they close attacks nobody needs to run again.

Scratch, generators and evidence: `.temp/r42/` (`NOTES.md`, 328 lines; all
binaries and blobs deleted, 848 KB of `.py`/`.rs`/`.json`/`.log` kept).

## What was built

- `.temp/r42/probe1/{gen,gen2,gen3}.py` — **48 standalone kernels** separating
  the phi, the operator, the capacity, the array length and the guards.
- `.temp/r42/r3search/{gen_r3,run_r3}.py` — 16 in-contract R3 candidates derived
  from the shipped `safe_tuned.rs` by asserted-count substitution, measured with
  `harness/measure.py`, verdicted with `check.spelling_matches` **and**
  `model.py` on all five matrix inputs.
- `.temp/r42/vmut/gen_vmut.py` — 10 reviewer-authored Verus mutants.
- `.temp/r42/sweep/redo.py` — independent regressor replay, the reviewer's own
  callgrind runs, an **exact rational 5×5 solve** (not least squares), and a
  fresh out-of-sample blob.
- `.temp/r42/layout/` — the 30-layout population `NOTES.md` §11d records as not
  run.

`harness/check.py p04` → `PASS`. `measure.py --check-stale` → 24 records, 0 stale.

## BLOCKER 1 — the shipped R3 is not the cheapest found, and the number is `+4.00`

`patterns/p04-ring-buffer/NOTES.md:871`, `:1076`; `RECAP.md:779`.

**Six in-contract spellings, five distinct machine codes, all at `3367 / 11666`**
against the shipped `3368 / 11667`:

```
safe_tuned (shipped)  84 b5040cb5d805  3368 / 11667   +5.00
q_get2   `buf.get(off..).unwrap().get(..len).unwrap()`   81 e8e3049f31e7  +4.00
q_splitat/q_sp6 `buf.split_at(off).1.split_at(len).0`    86 82f66e591fb0  +4.00
q_sp2    `buf.get(off..).unwrap().split_at(len).0`       83 beab7d0f4d5b  +4.00
q_sp3    `let (_,t)=buf.split_at(off); &t[..len]`        88 f15cd24ff662  +4.00
q_sp4    `buf.split_at(off).1.get(..len).unwrap()`       83 6af2cf628d2c  +4.00
all: required_miss=0  forbidden_hits=0  model checksum OK on all 5 inputs
```

**Mechanism, off the listing** — same two checks, one fewer instruction, and it
is *register allocation* rather than bounds-check removal:

```
shipped entry block:  mov %rcx,%rax ; add %rdx,%rax ; jb ; cmp %rsi,%rax ; ja  = 5
two-step entry block: sub %rdx,%rsi ; jb            ; cmp %rsi,%rcx ; ja      = 4
```

`off + len` needs a scratch register; `buf_len − off` is computed in place in
`%rsi`, which is dead afterwards.

**Failure scenario.** A reader takes `+5.00` and *"the first pattern whose
shipped R3 is the cheapest found — a first"* as p04's result. The R3-side span's
cheap endpoint is `+4`, the `+5` is beaten by the next lever exactly as on p03,
and the "a first" claim is false. `R2 − R3` becomes `20·ops + 12` against the
cheapest. `.memory/01-ladder.md` already names `split_at` as the form that keeps
winning; p04 tried `chunks_exact` on the **record** and never tried a two-step
reslice on the **window**.

⚠ **The `idiom` block pins no reslice spelling at all**, which is why all six
candidates are in contract by construction — so it is the *cheapest-found* claim
that fails, not the declaration. §13's direction test is unaffected and holds.

## MAJOR 2 — the two R1 laws are laws of R1's OWN counts, and they fail out of sample

`NOTES.md:449-459`, `:466-467`.

The licence for fitting the R1 cells over band F states three conditions
(`pushes = xpush + dpush`, `xpop = xpop`, `epop = epop`) but verifies them only
on band F — **where `epop == 0` by construction**. On a fresh blob with both
`dpush` and `epop` non-zero, a combination **no shipped blob has**:

```
.temp/r42/sweep/oos.bin  nops=1500  model: xpush 616 dpush 137 xpop 590 epop 157
  c-gcc-h 24329 OK | c-clang-h 18945 OK | R2 49409 OK | R3 19398 OK | R4 19393 OK
  c-gcc   predicted 22961   measured 22576   MISS -385
  c-clang predicted 17071   measured 16741   MISS -330
  R1's OWN counts there: 753 / 0 / 535 / 212
  -> the same law at R1's own counts lands EXACTLY on 22576 and 16741
```

Knock-on: `R1h − R1 (gcc) = +4·xpush − 8·dpush` predicts `+1368` there; measured
`+1753`.

**Failure scenario.** Anyone applying §4's table to a workload where the ring
collapses and later pops find it empty gets a 2% (gcc) error, while the file says
*"max residual 0.0000, seven exact integer cost models"*. **The fix is one
sentence**: state the two R1 rows in R1's own counts, or restrict them to
`epop == 0`.

## MAJOR 3 — "`% 60` fixes NO bits" is false; the dichotomy is quantitative

`NOTES.md:194-196`, `:49-51`; `README.md:37-39`; `safe_naive.rs:26-31`;
`RECAP.md:754-756`.

`computeKnownBits(urem x, 60)` sets the high 58 bits zero — i.e. `x % 60 < 64` —
and **that fact does survive the loop-carried phi**. `% 60` into a `[u64; 64]`
array elides both ring checks in a one-cursor kernel (both arm orders) and in a
two-cursor kernel with no guards (`T_noguard_60_a64`, 1 pad).

**The rule the measurements actually support, zero fitted parameters:**

> `urem x, C` ⟹ `x < next_pow2(C)`, and the access check is elided exactly when
> **`next_pow2(CAP) ≤ ARR_LEN`**.

It reproduces every capacity p04 predicts *and* the mixed cases p04 never built:

```
L_mod64   86  1 pad     L_mod128    86 1     L_mod32_a64 86 1   L_mod64_a96 86 1
L_mod60  105  3 pads    L_mod48/96 106 3     L_mod33_a33 107 3
one-armed: %33,%48,%60,%64 into [u64;64], both arm orders -> 1 pad (elided)
           %60 into [u64;60], %33 into [u64;33]           -> 2 pads
```

**Two further measured refinements:**

- **(a) `L_br64`.** Spelling the CAP=64 wrap as a *source branch* — same `[0,63]`
  cursor, no division, no `cmov` — brings **both** ring checks back (86 → 101
  instructions, 1 → 3 pads). So at a power of two the elision is a property of
  the `%`/`&` **spelling**, not of the cursor's provable range.
- **(b) A guard destroys the surviving fact for `urem` and not for `and`.** At
  `% 60` into `[u64; 64]`, adding the emptiness guard alone takes it from 1 pad
  to 3; at CAP=64 no guard does.

**⚠ Read (a) carefully — it CONFIRMS the headline while refuting the
explanation.** `L_br64` and `L_br60` both keep the checks at the identical
provable range, so **the range is never what carries**; what carries is always
known bits contributed by the operator. *"Known bits, not a range"* survives and
is strengthened. What is false is the sub-claim that `% 60` supplies **no** bits:
it supplies `< 64`, which is exactly why it elides into a 64-slot array and not
into a 60-slot one.

## MAJOR 4 — §12c mis-attributes the invisibility to the modulus

`NOTES.md:1049-1059`.

Remove the modulus entirely — wrap with a source branch reached under the guard
(`x_guardwrap*`) — and the memory-safety obligation is **still** two independent
one-variable clauses (`9 verified, 0 errors`), and the missing fullness check is
**still** invisible (`x_guardwrap_nofull_msonly`, `9/0`).

**The property is that the index bound is the array's own fixed capacity, not
that the update is modular.** Failure scenario: the sentence reaches `.memory/`
as a claim about `%`, and the next pattern with a non-modular fixed-capacity
container gets written as if it were a different class.

## MINOR 5 — the invisibility is not specific to the cursor relation

`x_swaphead_msonly` — read `ring[tail]` instead of `ring[head]`; memory-safe,
functionally wrong, **no guard touched** — is `9 verified, 0 errors`. So *"the
relation between `head` and `tail` is exactly the part of the state the
memory-safety obligation does not need"* is **true but is not a
characterisation**: the memory-safety-only configuration is blind to *every*
functional change.

Also stronger than shipped: `x_bothguards_msonly` (**both** guards deleted at
once) is `9/0`.

## MINOR 6 — `NOTES.md:205-206`

"at 60 it rejects 2.27 pushes per call" on `large`; reviewer gets **2.23067**
driver-weighted and 2.25 unweighted over all 2000 windows. Nothing rests on it.

## MINOR 7 — a loose citation on a correct number

`verus.rs:24` and `spec.md`'s `note` cite *"NOTES.md 6 measures `nofull_msonly`
at 12 verified"* while NOTES §6 prints 9. Measured `m_nofull_msonly --cfg
slb_twin` → **12 verified, 0 errors**, so **the number is right and only the
citation is loose**. Flagged so nobody "fixes" a correct number.

## MINOR 8 — `small`'s R2 layout population is bimodal at 1.42× and is unexplained

27 layouts at 6.43–7.17 ms, **four** at 9.30–9.88 ms, reproducible across both
passes. `analyze.py` finds no `(loop, property)` pair that separates it and
`addr%32` does not either. All four are `order|*` builds (the lever that permutes
all 582 text symbols including startup) and they are among the *fastest* on
`large`, so it is plausibly a startup-side effect on a run that is mostly process
startup — but it is unexplained, and the population is not unimodal.

## Mechanism contributions for two rows `NOTES.md` left unattributed

```
gcc +717 at CAP=60 = +4/OPERATION (four value-byte movzbl SUNK out of the push
   arm into the shared dispatch block) -3/accepted push +1/executed pop +8/call
   = 4*237 - 3*119 + 118 + 8 = 717 EXACT on `small`
clang R1h 14 vs R1 15 Ir/executed pop = the two builds SWAP which arm falls
   through; the out-of-line arm pays one unconditional `jmp`. Exactly 1.00000.
```

## Clean negatives — named attacks that did NOT land

- **§1 experiment 1 (the phi): the headline is EARNED, by a stronger test than
  asked.** At CAP=60 the ring check is deleted in straight-line code **and across
  a non-loop phi** (`S_direct60`, `S_phi60`, 1 pad each) and kept in the loop
  (`L_mod60`, 3 pads). *"Does not survive the **loop-carried** phi"* is measured,
  not asserted.
- **§1 experiment 2 as specified: the claim survives.** The branch-wrap at CAP=60
  keeps both checks (`L_br60`, 3 pads, same as `L_mod60`) — the 60-vs-64 gap is
  **not** merely the lowering.
- **§1 experiment 3: every capacity prediction holds** — 48 and 96 behave like
  60; 128 behaves like 64; `% 32` into `[u64;64]` and `% 64` into `[u64;96]`
  both elide.
- **The arithmetic checks out.** `small`'s counts are unchanged by the CAP edit
  (119/0/118/0 at 64 **and** at 60, replayed independently), `237 = 119 + 118`,
  and `479 − 5 = 474 = 2.00000 × 237` exactly.
- **The pads were re-decoded, not re-counted** (`pads.py --source`):
  `ring[tail]`/`ring[head]` contribute zero pads in every shipped rung; R3's
  single pad is `safe_tuned.rs:51:24`, the window reslice. Also **`q_sp5` has 0
  pads and costs `+7`** — pad count is not the tax.
- **`p1_weak_requires` is real and the twin is the only catcher.** Reproduced
  9/0 shipped, 11/1 twin. `harness/check.py:3208-3209` says deletion is not
  applied to trusted items; `i <= v@.len()` is not a tautology (false at
  `i = 65`); both parameters appear, so parameter coverage cannot fire.
- **`ring_set_unchecked`'s whole-sequence `ensures` is load-bearing.** Weakened
  to `final(v)@.len() == old(v)@.len() && final(v)@[i] == x` in the item *and*
  its twin: the shipped configuration **fails**; `_msonly` still passes.
- **TCB 10 lines / 5 items recounted against the gate's own `tcb_items`** —
  matches (`1+1+3+4+1 = 10`).
- **§13's direction test holds.** `m_mask` and `cap64_r3_clamp` are both
  `md5_fn_norel b5040cb5d805` = shipped R3; both exclusions move the figure by
  0.00.
- **§7.3's reproducibility claim is right, three ways.** (a) Exhaustive
  simulation: R1 reads a never-written ring slot **0 times** across every window
  of all five inputs. (b) **memcheck runs here on a static build** — zero
  diagnostics inside `kernel` on three inputs. (c) **880 runs with randomised
  environment size**: one distinct stdout per cell/input.
- **R2 is a fair naive port.** `r2_forloop` is **byte-identical** to shipped R2
  (`n_fn 132`, `805c3851ce68`, 8119 / 28278, checksums OK).
- **The `xpush`/`dpush` equality self-check is a real test** — the pooled design
  is rank 5, so the coefficient vector is unique, and R1h comes out **unequal**
  (22/10 gcc, 13/9 clang) on the identical design. It just tests only the first
  of the three licence conditions (MAJOR 2).
- **§11's `ns` figures survive a real layout population.** `+25.7%` (small) and
  `+9.7%` (large) reproduce mode-matched at `+25.1…+26.0%` and `+9.3…+10.2%`,
  `P(A>B) = 100%`. The `R3 − R4` null holds under mode-matching **with the sign
  flipping between modes**, which is what a null looks like.
- **§4's rank table reproduced exactly** with independent exact-rational code,
  including the corollary the engineer used to contradict the task file:
  `(sweep-n*, sweep-f*)` is 4/5 and would not have identified the design.
- **The p03 reproduction boundary, named.** `R2 − R3 = 20·(all four) + 11` is the
  **opcode-stream** half — both patterns walk the identical 5-byte record with
  the identical written-out LE decode. p03's extra `3.00000·xpop` in `R2 − R4` is
  the **container** half: p03's pop guard supplies only the lower bound `sp > 0`,
  so the upper bound must cross the attacker branch and LLVM drops it. p04 has no
  container check to keep, because `%` supplies both cursors' upper bounds
  unconditionally. **The law reproduces for the stream and not for the
  container.**

## Reviewer's own "unsure / not done"

- Did **not** disassemble LLVM IR to confirm the `and`-recurrence attribution
  behind MAJOR 3(b). The *measured* rule (`next_pow2(CAP) ≤ ARR_LEN`, and a guard
  defeats it for `urem` but not for `and`) is what the reviewer stands behind;
  the named LLVM mechanism is a reading, not a measurement.
- Did **not** search below `+4.00` exhaustively — *"cheapest found"*, never
  *"minimum"*. Ten further spellings measured `+5.00` or worse.
- Did not run the branch/cache simulators; nothing needed them.
- MINOR 8's 42% layout mode is characterised but not explained.
- `verus.rs`'s `--verify-function` decomposition (`RING_CAP 1 + run 1 + kernel 2
  + main 5`) was not re-measured term by term; the totals 9 and 12 and the gate's
  `pinned: 9` were confirmed.
- Nothing under `patterns/`, `.memory/`, `harness/`, `common/`, `pilot/` was
  edited; no `git add`/`git commit`.
