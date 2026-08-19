# TASK_036_REVIEW — report

Reviewer's return message, recorded by the manager. Scratch `.temp/r36/`:
`NOTES.md`, `order.log`, `gen_r36.py`, `probe.py`, `kirany.py`, `sweepfit.py`,
22 controls under `controls/` and `c/`.

**Verdict: `m_clamp` survives the attack. Two blockers and two majors against the
prose; the causal claim itself is confirmed and generalised.**

## 1. `m_clamp` measures the invariant, exactly — confirmed

Kernel-exclusive Ir/call, `-O3 isolated`, all agreeing with `model.py` on 6 inputs.

```
  safe_tuned      popchk=1  n_fn=82  small= 3361.00  large= 9010.00  equiv=OK
  unsafe          popchk=0  n_fn=66  small= 3002.00  large= 8384.00  equiv=OK
  x_clamp   sp>64 popchk=0  n_fn=78  small= 2889.00  large= 8886.00  equiv=OK
  x_clamp_p1 sp>65 popchk=1 n_fn=81  small= 3716.00  large=10462.00  equiv=OK
  x_clamp_big sp>1000 popchk=1 n=82  small= 3361.00  large= 9010.00  equiv=OK
  x_deadret acc==K popchk=1 n_fn=88  small= 3835.00  large=10670.00  equiv=OK
```

`sp > 1000` is **byte-identical to shipped R3**; one past the invariant (`sp > 65`)
leaves the check standing *and* is dearer; a non-dead early return saying nothing
about `sp` is dearer with the check standing. Swept exactly (19 blobs, rank 4/4):

```
  safe_tuned      11 xpush + 7 dpush + 17 xpop + 46   maxres 0.000000
  unsafe          11       + 7       + 14      + 41   maxres 0.000000
  x_clamp         11       + 9       + 13      + 46   maxres 0.000000
  x_clamp_unsafe  11       + 9       + 13      + 41   maxres 0.000000
```

**Mechanism, which `NOTES.md` does not have.** In `x_clamp`'s kernel there is
exactly **one** `cmp $0x40` and it is the *push* guard, respelled
`cmp $0x40,%r15 ; jne` (equality, because `sp<64 ⟺ sp≠64` once the range is
known). **The clamp itself is gone**, and its `return 0` semantics is not
preserved on the `sp>64` path — LLVM concluded that path unreachable, i.e. it
**did** derive `sp ≤ STACK_CAP`. What it cannot do is find the fact *unseeded*.
Analysis **seeding / phase ordering**, not an inability to prove the lemma — a
different failure from p05's, where the fact itself is nonlinear.

## 2. BLOCKER — the same machine code is reachable IN CONTRACT, so the span is wrong

`assert!(sp <= STACK_CAP);` at the top of the loop — one line, zero `unsafe`,
zero TCB:

```
  x_assert  n_fn=78  md5_fn 7ad05dbef1b7e2350031cdb6113d4ac4  small=2889 large=8886
  m_clamp   n_fn=78  md5_fn 7ad05dbef1b7e2350031cdb6113d4ac4  (shipped control)
```

Byte-identical. Against the gate's own ruler (`check.py::spelling_matches`):

```
safe_tuned(ship)  FORBIDDEN-HITS=[]  REQUIRED-MISSES=[]
x_assert          FORBIDDEN-HITS=[]  REQUIRED-MISSES=[]
m_mask(ship ctl)  FORBIDDEN-HITS=['& (STACK_CAP - 1)']  REQUIRED-MISSES=[]
```

A second in-contract placement, `x_assert_pop` (assert inside the pop arm), sweeps
to `11 xpush + 7 dpush + **15** xpop + 46` — **+1.00000 per pop**, 3125/8596.

- `NOTES.md:915` "cheapest found, both blobs" — **false**.
- `NOTES.md:927` span `+359 … +5110` / `+626 … +17237` — lower endpoints wrong; in
  contract it is **−113 … +5110** and **+212 … +17237**.
- `NOTES.md:942` "the cheapest spelling is the same on both blobs" — **false**:
  `x_assert` wins `small`, `x_assert_pop` wins `large`.
- The published **`3.00000` Ir per executed pop is the shipped spelling's rate**,
  not the class's. The class reaches 1.00000 and −1.00000. The fixed-R4 bound
  survives as an *upper* bound; it now bounds a **negative** number on `small`.

*Failure scenario:* a reader takes `+359 … +5110` as the in-contract search and
concludes the tax is at least +359 Ir/call. It is at most −113.

## 3. BLOCKER — §10b is wrong twice, and p03 closes an open question

**(a) `r4_slicestack` is not borrow-checker-blocked.** The shipped control's
`E0502 ×2` come from ghost clauses `controls/gen_controls.py:198-202` itself adds;
the `E0596` is a missing `mut` on the control's own `let`. A third spelling
(`let mut stack: &mut [u64] = &mut stack_arr;` — the unsizing coercion vstd
supports — plus reborrows and the ghost assert after the borrow, accessors retyped
over `&[u64]` at the **same 1+3 TCB lines and the same `requires`**):

```
$ ./verus_run.py .temp/r36/controls/r4_slicestack_v4.rs
verification results:: 9 verified, 0 errors
```

The exec side is byte-identical to shipped R4 (`md5_fn 52432361a348`, 3002/8384).
`NOTES.md:996-1003`'s *"does not borrow-check"* / *"the unsafe class is bounded by
Rust's borrow checker"* must be **withdrawn**.

**(b) There is an admissible R4 that MOVES — the first in this project.**

```
$ ./verus_run.py .temp/r36/controls/m_clamp_unsafe_twin.rs
verification results:: 9 verified, 0 errors                 # zero new trusted items

m_clamp_unsafe        md5_raw 8037413581827249d16b69a6b75f13cd  md5_fn 40d374bfb669805e32128d48c88ae6d7
m_clamp_unsafe_verus  md5_raw 8037413581827249d16b69a6b75f13cd  md5_fn 40d374bfb669805e32128d48c88ae6d7
```

In contract by the ruler, identity pin byte-for-byte, **−118 on `small` / +497 on
`large`** against `R4ship`. `NOTES.md:985` "the pair interval is DEGENERATE" and
`:1010` "the first pattern where searching it turned up nothing at all" are
**refuted**, and `.memory/01-ladder.md`'s standing *"nobody has, on any pattern"*
is answered.

**And the asymmetry is measured.** `assert!` is available to R3 and not to R4:

```
$ ./verus_run.py .temp/r36/controls/x_assert_unsafe_twin.rs
error: panic is not supported (if you used Rust's `assert!` macro, you may have
       meant to use Verus's `assert` function)
```

Third measured instance of R4-by-permission, and the first where the safe-side
lever is a one-line assertion.

## 4. MAJOR — the C rung admits the same edit, on BOTH compilers

`c/kernel_hardened.c` plus a manual bounds check on the pop read, ± the identical
clamp:

```
  c-clang-h (shipped)     small=2869  large= 8162   n_fn 51
  k_bchk-clang  (+check)  small=3341  large= 8990   n_fn 56  check SURVIVES (cmp $0x3f, ud2)
  k_bchk_clamp-clang      small=2869  large= 8866   n_fn 53  md5_fn e5fd25a089b2…
  k_clamp-clang (no chk)  small=2869  large= 8866   n_fn 53  md5_fn e5fd25a089b2…  <- IDENTICAL
  c-gcc-h   (shipped)     small=3836  large=10345   n_fn 76
  k_bchk-gcc    (+check)  small=4546  large=12997   n_fn 80  check SURVIVES (2x cmp $0x3f)
  k_bchk_clamp-gcc        small=3838  large=10347   n_fn 78  md5_fn d88f71dc501a…
  k_clamp-gcc   (no chk)  small=3838  large=10347   n_fn 78  md5_fn d88f71dc501a…  <- IDENTICAL
```

clang's manual check is **4.00000 Ir per executed pop exactly**; the clamp deletes
100% of it in both compilers, byte-identically. **Two independent middle-ends fail
the same lemma the same way**, and gcc shares none with rustc. `NOTES.md:353-356`
is true of p03 but its natural reading — a fact about *safe Rust* — is
contradicted.

## 5. MAJOR — the "same basic block" mechanism is refuted

`x_pushhoist` computes `let can_push = sp < STACK_CAP;` in the loop head and
branches on it in the push arm — guard and write in different basic blocks.
Result: `md5_fn a5a47dba3129…`, `n_fn 82`, 3361/9010 — **byte-identical to shipped
R3**. LLVM normalises the hoist away and still deletes the push check.
`NOTES.md:297` / `README.md:79` do not describe what happens. **The real
discriminator: the push guard supplies the UPPER bound the access needs, locally;
the pop guard supplies only the LOWER bound and the upper must come from the
loop-carried invariant.** Two in-contract controls confirm it (`if sp > 0 && sp <=
STACK_CAP`, and the assert in the pop arm) — both go to 13–15, check deleted.

## 6. Confirmations — do not re-run

**Pooled design is identified, and more strongly than claimed.** Exact rational
rank: `A 3/5, B 3/5, C 3/5; A+B 4/5, A+C 4/5, B+C 4/5; A+B+C 5/5` — **every pair
is deficient**, only the pooled fit identifies the terms. Every coefficient
refits at `maxres 0.000000`. Caveat: `epop>0` on 12 of 89 blobs and `dpush>0` on 9
of 89 — thin support carried by the zero residual, not by the design.

**Verus.** `9 verified, 0 errors`; twin `12, 0`. Per-function:
`STACK_CAP=1, run=1, kernel=2, main=5` → 9. TCB `1+1+3+4+1 = 10` across 5 items.
All four mutants reproduce and all four fail under the twin.
**Tautology repair complete** — all three trusted conjuncts `"not a tautology"`,
per-conjunct deletion `load_bearing 1 of 1` on each.

**Mask decomposition — 1.00000 of 3, confirmed on the listing.** Note
`x_popidx` (`if sp > 0 && sp - 1 < STACK_CAP`) lands on `m_mask`'s exact numbers
**in contract**, which undercuts §10a's "forbidding `m_mask` raises the figure,
against interest".

**Noise floor, run first** (`order.py`, 31 copies × 31 reps × 2 passes):

| pass/order | R2 floor | R3 floor | R4 floor | R2−R4 | R3−R4 |
|---|---|---|---|---|---|
| 0 alt | 3.46 | 13.78 | 6.57 | +6.33 | **−10.77** |
| 0 blk | 3.74 | 10.44 | 10.97 | +4.19 | −4.22 |
| 0 gen | 4.20 | 4.71 | 4.65 | +5.65 | **−10.72** |
| 1 alt | 4.04 | 3.44 | 4.68 | +5.96 | **−10.86** |
| 1 gen | 6.47 | 4.48 | 6.30 | +5.98 | **−10.70** |

⚠ **Contradicting the manager: the `Ir`-vs-`ns` direction on `small` is RESOLVED.**
Four correct-protocol readings today at −10.70…−10.86% against a 3.4–6.5% floor,
plus the engineer's three yesterday at −10.63…−11.04% — seven independent
readings, spread 0.4 points. The hedge was too weak; what should stay hedged is
the **magnitude** (7–15% across layout modes), not the sign.

**Also reproduced**: §11b's `small` discard (four cells over 10%), §3b's memset ±7
(same binary, two probe directories, 3059 vs 3066 whole-program, 3002.00
kernel-exclusive in every configuration), the ASLR oracle (three runs, three
values; `addr-no-randomize` gives the same value `NOTES.md` §7 quotes).

**Clean negative on the "worth ten minutes" item**: `results/p03`, `p11` and `p16`
carry the *identical* protocol string — `measure.py`'s hardcoded one. There is no
p03-vs-p11 rule conflict at the record level.

## Problems — minor, all documentation

- `NOTES.md:1198` says §5b tallies **8** TCB lines; §5b's table and the gate both
  say **10**.
- `NOTES.md:231-232` claims the memset cost "is part of the C-vs-Rust rows in §3";
  §3 is kernel-exclusive and therefore **excludes** the 43–50 Ir only the Rust
  rungs pay (`c-clang` −12.29% kernel-exclusive vs −13.47% whole-program).
- `.temp/p03/kir-band-*.json` has no `verus` row; §4 labels the row
  `unsafe/verus`. Defensible at O3, but it overstates what was run.
- `controls/gen_controls.py:186-203` ships two generation defects, both reported
  as language verdicts.

## Unsure / not done

- Whether `assert!` counts as an admissible R3 spelling is a **judgement the
  manager owns**. Evidence: the decidable ruler admits it (0 forbidden hits, 0
  required misses); `.memory/01-ladder.md`'s R3 definition names *"hoisted length
  assertions"*; and it is a runtime check, not a semantic change on an unreachable
  path, so the "dead code inserted to move a number" argument that excludes
  `m_clamp` does not reach it. **If ruled out, finding 2's span correction stands
  down but finding 3's admissible-R4-that-moves does not** — `m_clamp_unsafe` is
  excluded by the same prose and its Verus twin is unaffected.
- Did not search for an in-contract R3 cheaper than `x_assert`. Given "six
  published minima, six refuted", assume one exists.
- Did not re-run the full gate (`--check-stale` reports the record `FRESH` over 35
  sources and nothing tracked was changed), `m_branchless`, the `Bcm` table, Miri,
  the sanitizer builds, or §11c's 31-layout population.

## Memory updates

None — reviewers do not write `.memory/`. Landed by the manager: finding 10
(p03) with the two qualifications, the retirement of *"nobody has, on any
pattern"*, the corrected span and its `assert!` lever, the refuted basic-block
mechanism, the withdrawn borrow-checker claim, the resolved `ns` direction, and
the p03-vs-p11 non-conflict.
