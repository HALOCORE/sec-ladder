# TASK_038_REVIEW — report

Reviewer's return message, recorded by the manager. Scratch `.temp/r38/`:
`NOTES.md`, `gen_probes.py`, `gen_exec.py`, `marg.py`, `wall.py`, `equiv.sh`,
`probes/`, `controls/`, `gate.log`.

**The invisibility claim HOLDS. One blocker, five majors, one minor — and two of
them generalise past p09 to every pattern's published numbers.**

## The claim survives four vacuity attacks

```
m_control_msonly + assert(false) in kernel body / query loop / popcount loop -> 17/1 assertion failed (x3)
m_mask31_msonly  + assert(false) in the same three places                    -> 18/1 assertion failed (x3)
m_control_msonly with `if q < nbits` DELETED                                 -> 17/1 precondition not satisfied
m_mask31_msonly  with `if q < nbits` DELETED                                 -> 18/1 precondition not satisfied
```

**A memory-safety-only proof that still catches R1's spatial bug on the same file
discharges `q & 31` at `19 verified, 0 errors`.** That is real.

## B1 — BLOCKER. There *is* an arithmetic index bug, it is one character, and `q >> 7` is it

`NOTES.md:551-552,906-911`, `spec.md:116-121,346,389` (the last two **hashed**)
conclude from `q >> 5` that index errors on a bitset degenerate to spatial, so
`q & 31` is the only arithmetic bug. **Measured false.** `q >> 7` = `q/128 ≤ q/64`,
so under `q < nbits` it is *always* a legal word index, and Verus proves it
universally with one extra ghost line — the exact analogue of
`m_mask31_fixshift`'s:

```
m_shift7_bare     17 verified, 1 errors  precondition   (proof-weakness, cf. bare `q & 31`)
m_shift7          18 verified, 1 errors  invariant only -- FUNCTIONAL
m_shift7_msonly   19 verified, 0 errors  -- INVISIBLE to memory safety
m_shift7_spec2    20 verified, 0 errors  -- INVISIBLE entirely (spec moved to /128)
```

And it beats `q & 31` on every other axis:

| | edit distance | R4 marginal Ir | `n_fn` | guarded body |
|---|---|---|---|---|
| shipped | — | 6692.30 | 102 | 26 insns |
| **`q >> 7`** | **1** (`6`→`7`) | **6691.70** | **102** | **26, identical but `shr $0x7`** |
| `q & 31` | **2** (`63`→`31`) | 8845.30 (+2153) | 113 | 35 |
| `q >> 5` | 1 | 6692.00 | 102 | 26 |

Behaviour — gcc `-O1 -g -fsanitize=address,undefined` (the gate's own flags):
`x_shift5` fires `heap-buffer-overflow` on `thin.bin`; **`x_shift7` is silent on
`small.bin` and on `thin.bin`**. Miri on `x_shift7_u`: `exit=0 UB=0`, wrong
answer. All five builds print the identical wrong `3393155352413092229`.

**The sentence p09 should publish is one character sharper than the one it has**:
`q >> 5` and `q >> 7` differ in one character *in the same position*; the first is
caught by memory safety alone on every input, by rustc's bounds check, by ASan and
by the proof — the second by **nothing at all**, at zero instruction cost, on
machine code identical to the shipped rung but for one immediate. `q & 31` is a
*two*-character substitution costing +32% on R4, so "two one-character bugs"
(`NOTES.md:21,906`, `spec.md:211,346`, `README.md:56`) is wrong on both counts and
the pattern is holding the weaker example.

## B2 — MAJOR. The clause that catches `q >> 5` is `load_u64`'s, not the trusted accessor's

`NOTES.md:576` annotates the pasted output `<- the ACCESSOR's`. It is not:

```
error: precondition not satisfied
   --> .temp/p09/controls/m_shift5_msonly.rs:499:26
427 |         p + 8 <= buf@.len(),
    |         ------------------- failed precondition
```

`load_u64` is a **verified** item. Deletion probes:

```
v_ship_noacc           shipped, buf_get_unchecked `requires` deleted   -> 18/0  UNCHANGED
v_m31_noacc            m_mask31_msonly, ditto                          -> 19/0  UNCHANGED
v_shift5_msonly_noacc  m_shift5_msonly, ditto                          -> 17/1  UNCHANGED
v_ctl_noguard_nol64    decoders' requires deleted, accessor's KEPT     -> fires inside load_u32/load_u64
```

The trusted `requires` is **shadowed**, not dead (last row). p09 is the **only**
pattern with decoder wrappers carrying their own `requires` (0 in all nine
others) — so this is a genuine structural first and a *better* result than
claimed: **the security obligation sits in verified code rather than at the TCB
boundary.** It is currently mislabelled in the layer the gate hashes
(`spec.md:346`).

## B3 — MAJOR, and it is project-wide. 55–73% of every published `ns` figure is the per-process constant

`measure.py` times whole process invocations. `.temp/r38/wall.py` runs its exact
protocol plus the same blob with `n_iters` rewritten to 1:

```
small, 60 reps       t(full)  t(1)   kernel   vs R4 full  vs R4 kernel
  unsafe              5.324   2.865   2.459     +0.0%        +0.0%
  safe_naive          8.304   2.755   5.548    +56.0%      +125.6%
  safe_tuned         10.672   2.916   7.756   +100.5%      +215.4%
large, 15 reps
  unsafe              9.754   7.150   2.604     +0.0%        +0.0%
  safe_tuned         14.546   7.176   7.370    +49.1%      +183.1%
```

| pair | `Ir` | `ns` published | `ns` kernel-only |
|---|---|---|---|
| R3−R4 small | +205.6% | +99.1% | **+215.4%** |
| R3−R4 large | +199.4% | +50.2% | **+183.1%** |
| R2−R4 small | +148.5% | +58.0% | **+125.6%** |
| R2−R4 large | +148.5% | +26.5% | **+100.0%** |

`NOTES.md:362-368` attributes the gap to ILP. **For R3 the corrected `ns` penalty
EXCEEDS the `Ir` penalty — the ILP claim is refuted there**; it survives only for
R2, at 1.2–1.5×, not 2–4×. On `large`, 7.15 ms of R4's 9.75 ms is the 8.2 MB
payload read. **This affects `measure.py`'s protocol generally, not just p09.**

## M1 — MAJOR. NOTES 4c's mechanism is wrong, and the true one is better

`NOTES.md:294-302` says LLVM does not merge the eight byte loads on the
shift-derived access "in either safe rung". False for R2. Complete 2×2:

| | linear index (popcount pass) | shift-derived index (query loop) |
|---|---|---|
| absolute (R2) | merged | **merged** — `mov (%rdi,%rax,1),%rax` |
| reslice (R3) | merged | **NOT merged** — 22-insn `movzbl/shl/or` chain |
| unchecked (R4) | merged | merged |

The merge fails in exactly **one** of the eight loops measured, and that single
failure is the whole inversion:

```
+21  lost 8-byte load merge (22 insns vs 1)
 +1  spill reload `mov 0x8(%rsp),%r9`
 -5  cheaper query-array checks the reslice buys
-------------------------------------------------
+17 net  ==  (/query -5) + (/guarded +22)
```

**The hazard is `reslice` + a data-derived index + a multi-byte decode at it** —
p09 is the first pattern with all three, so the answer to "p09 fact or general
reslice hazard" is **conditional, and the condition is checkable**. Consequence
for §8: **half of the seeding win is the restored load idiom, not deleted
checks** (`m_clampb` 82→40: −20 checks, **−21 restored merge**, −1 spill).

## M2 — MAJOR. `q & 31`'s +9 on R4 is not "a real `and`" — there is no `and`

`q & 31` lets LLVM prove the tested bit is in the low 32 bits, so it **narrows the
load**; the merged 8-byte `mov` splits into a 4+2+1+1 reassembly and the test
becomes a 32-bit `bt`. Same mechanism as M1 — which **unifies p09's two cost
stories** instead of leaving them unrelated.

## M3 — MAJOR. TCB tally is 7; NOTES says 12

`results/gate/p09-bitset.json` `tcb_items`: `buf_get_unchecked 1, popcount64 1,
load_input 4, emit 1` = **7**. `NOTES.md:431-433` and `README.md:99` declare 12
across 4 items with a per-item column matching no item but `load_input`. **Every
other pattern's declared figure equals the gate total exactly** (p01 6, p02 10,
p03 10, p05 6, p07 6, p08 10, p11 6, p16 6, p17 6). Corrected, p09 has the
**second-smallest TCB in the project**, not one of the largest.

## M4 — MAJOR, and general. A `forbidden` entry without backticks is audited zero times

`check.py:929` audits only backticked tokens (`_TICK.findall`). p09's `forbidden`
entries are bare strings:

```
gate-audited forbidden tokens for p09: []
line 189:  ok   idiom declared: 11 required, 5 forbidden spelling(s), ...
line 192:  audit  forbidden: 0 spelling(s), 0 hit(s)
```

**The verdict line two lines above still counts them.** p09 is the only pattern
with a non-empty `forbidden` list and 0 audited spellings. `spec.md:389` cites
"forbidden: 0 hits on all six" — for p09 **the 0 was kept by auditing nothing**.
The disclosed `_blank_ghost` trap is real and the avoidance works
(`spelling_matches('q / 64', verus.rs)` is `False` as shipped, `True` if `word_of`
is respelled), but **the gate could never have sprung it here**, and no other
pattern's declaration trips it (all forbidden × all rungs, with and without
`_blank_ghost`: zero hits).

## m1 — minor. `m_clampb_lo` explained

LLVM does not delete the 8th byte's check; it **fuses it into the clamp** by
splitting the comparison three ways — `cmp ; ja <return 0> ; jb <loop top>`, with
`==` falling through to the panic block. Zero extra hot instructions; +3 static for
the landing block. The −1.00 Ir is one `mov` in `m_clampb`'s *prologue*. **So
p03's "one past the invariant" control does separate on p09** — by 3 static and 0
dynamic, because the extra obligation rides a branch that was already there.

## Clean negatives — do not re-run

- **`_msonly` vacuity: dead.** Four probes above.
- **"The design carries the rank-4 result": dead, decisively.** Bands reproduce at
  2/4, pooled 4/4; dropping band `d` or `w` drops rank to 3, dropping `n` leaves
  4; condition number 355. **But the fit has ZERO free parameters** — every
  coefficient is a loop-body instruction count off the listing, reproduced to
  1e-4. Out of sample it predicts `large` (`nq` 830, `nwords` 125 — 3.5× and 4.6×
  outside every band) to within **1.13 Ir of 73404**, with `R3−R4` predicted
  **48885.00** against measured **48885.00**.
- **Gate**: `check.py p09` re-run in full → `PASS`, record byte-identical but for
  the ASan PID.
- **Proof mutants**: M1 caught by **the twin alone** (`20 verified, 1 errors`);
  M2 base 18/0, twin-mismatch 21/0, clause-on-twin `20/1 postcondition not
  satisfied`.
- **Obligations**: `kernel 3, main 5, popcnt 1, lemma_and63 1, load_u64 1,
  bitset_fold 0, buf_get_unchecked 0`; twin `21 = 18 + 1 + 2`.
- **`q >> 6` ≡ `q / 64`**: reproduced on rustc/clang/gcc, `usize`/`u32`, checked
  and unchecked; `u_shift` ICF-folded into `u_div`.
- **Intrinsic row**: `popcnt = 0` in all eight `-O3 isolated` kernels;
  `__popcountdi2` gcc only.
- **Every marginal `Ir`** in NOTES 3/6b/8/8a/10a reproduced to 0.01.
- **Adversarial per rung**: R1 SEGV on `adversarial-oob` under both compilers;
  wrong-and-silent on `adversarial-edge`; 0 on `adversarial-count`.
- **`spelling_matches` on every control**: all seeding and R3-span controls in
  contract; `r3_wordchunks` out, as NOTES says.
- **Shared `why` paragraph** byte-identical to p03's.

## Unsure / not done

- Could not apply the proof mutants to the shipped tree and re-run the gate stages
  (forbidden to edit `patterns/`); verified the Verus-level facts those stages
  rest on instead. "M2 is caught three ways with the pin left alone" is
  **unverified end-to-end**.
- Reused `.temp/p09/sweep_all.json` rather than re-running the 90-blob × 8-cell
  sweep; its provenance is validated indirectly, by the fit reproducing
  disassembly counts and predicting fresh `small`/`large` marginals.
- Did not re-run `order.py`'s identical-copy floor. The kernel-only `ns` column
  subtracts two noisy minima (R5−R4 reads +2.7% / +4.1% where it must be 0); the
  R2/R3 effects are 25–80× that.
- Did not build a Verus mutant for the one-character *mask* deletion `q & 3` (exec
  cost measured: +3825.70 on R4).
- Did not attempt an in-contract R3 cheaper than `r3_best`, nor re-search R4.

## Memory updates

None — reviewers do not write `.memory/`. Recommended:

1. **Lead p09's finding with `q >> 7`, not `q & 31`.**
2. The obligation that fires is `load_u64`'s — a **verified** item's precondition;
   p09 is the only pattern with a decoder wrapper, and this is the first time the
   memory-safety obligation sits **outside** the TCB boundary.
3. **Generalisable:** `measure.py`'s `ns` column is a whole-process *level*, never
   a difference — 55% / 73% constant on p09. Subtract `t(n_iters=1)` before
   quoting a ratio; p09's R3 "ILP" mechanism dies when you do.
4. **Generalisable:** a `forbidden` entry without backticks is audited **zero**
   times while the verdict line still counts it.
5. p09's TCB is **7 lines / 4 items**, per the project's own rule and its own gate
   record.
6. **Reslice hazard, conditional and checkable**: reslice + data-derived index +
   multi-byte decode ⇒ LLVM loses the 8-byte load-merge idiom. It is the whole of
   p09's R3 > R2 inversion, half of the `m_clampb` seeding win, and all of
   `q & 31`'s R4 cost.
