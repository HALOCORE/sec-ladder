# TASK_089 — build `p46`: report

**Role: research engineer.** **UNREVIEWED** — `TASK_089_REVIEW` attacks it next.

**`patterns/p46-bignum-mac/` is built, gated `PASS`, measured, `0 STALE`.**
17 committed files including **four committed control generators** in
`controls/`. ✅ **Manager-verified: 24 records, `{'PASS': 23,
'PASS-WITH-BLOCKED-ROWS': 1}`, 0 failures, 24 pattern directories.**

**PROTOCOL rule 2 running count: 253 → 256. ⚠⚠ ALL THREE of the manager's named
least-sure calls were contradicted with measurements.**

**Contract:** `requires off + len <= buf_len`,
`ensures result == bn_fold(buf, off, len)` — the tree's standard full functional
postcondition over a recursive spec of the schoolbook **algorithm**. The
**mathematical product** was **not** attempted; `model.py::_fold_bigint` closes
that gap **by testing** (one Python big-integer multiply per window,
gate-checked on every input).

---

## (a) ⚠⚠ THE NOVELTY CLAIM IS FALSE — and the counter is committed

`TASK_086_REPORT` called p46's postcondition *"stronger than any `ensures`
currently in the tree, all of which are bounds facts."* **The task file told the
engineer to COUNT it before shipping it. It counted.** ✅ **Manager-re-ran
`controls/census.py --ensures`:**

```
23 verus.rs, 159 `ensures` conjuncts
  equalities (`==` or `=~=`) : 151
  NOT equalities             : 8      <- five p09 inequalities + three p27 predicates
  kernel postconditions      : 24, of which 21 are `r == <name>_fold(buf@, off, len)`
VERDICT on TASK_086_REPORT's "all of which are bounds facts": FALSE by 151/159.
```

**What survives counting is a weaker, DIFFERENT sentence, and it is what p46
ships:** the **first `by (bit_vector)` and first `by (compute)` in the tree**
(both `0 file(s)` before p46), and **the first kernel-level nonlinear obligation
about DATA rather than an address.** ⚠ *"What is new is the MODE, not the
strength of the postcondition."*

✅ ⚠ **And the engineer caught its own error the same way:** it first
**hand-counted** 154/5 and shipped that into three files; **writing the script
found p27's predicate clauses.** Disclosed in `NOTES.md` 6d. **This is the
instruction working exactly as intended.**

## (b) ⚠⚠ `+5.05 Ir/MAC` DOES NOT REPRODUCE — THE SIGN IS OPPOSITE

Shipped, `-O3 isolated`, **kernel-exclusive** `Ir`/call:

| cell | small (24,24) | large (48,48) |
|---|---|---|
| c-gcc / c-gcc-h | 8271 / 8275 | 28866 / 28869 |
| c-clang / c-clang-h | 6108 / 6110 | 23088 / 23090 |
| **safe_naive** | **6241** | **23341** |
| safe_tuned | 6287 | 23435 |
| unsafe = verus | 6406 | 24250 |

**`safe_naive < safe_tuned < unsafe`.** The probe's `+7 Ir/MAC` was a
**`black_box` ARTEFACT**: it withheld the `u8` range on `n`, `m`, so LLVM could
not prove `i+j < 96`. **In the shipped kernel it can, and deletes all three
bounds checks** — the safe MAC loop has **no conditional branch but its own
`jne`**. ⚠ **p46's per-MAC safety tax is `0.00000`.**

⚠⚠ **THIS EXTENDS `.memory/03-measurement.md`'s NEW RULE: not only the
INTERCEPT but the SLOPE failed to transfer — and the RUNG BOUNDARY ITSELF
vanished** — for a reason the existing rule does not cover.

⚠ **This is the flattering-direction trap's SIXTH appearance, and it is handled
correctly:** both sides searched, **3 levers each, both DEGENERATE** (R4 span 3
flat, R3 span 2 flat), and a **rolled-vs-rolled control gives
`R2 − R4 = +2.00·n·m` exactly** — so **safe Rust's advantage is 100 % an UNROLL
decision**, derived instruction-by-instruction in `NOTES.md` 8a.

## (c) The product postcondition closed FIRST ATTEMPT, before any cell

`15 verified, 0 errors` on the probe; **`21 verified, 0 errors` shipped, `24`
under `--cfg slb_twin`**; no `assume`, no `admit`, no axiom. **The manager's
*"may not close in one session"* is refuted as meant.** ⚠ The **mathematical**
product was not attempted, so the strongest reading is **untested**, and
`NOTES.md` 6b says so.

**Load-bearingness demonstrated:** deleting the safety line gives
`20 verified, 1 errors`, *"invariant not satisfied before loop"* on
`n + m <= OUTCAP`.

---

## Two findings that matter beyond p46

**1. ⚠⚠ THE HARM IS SILENT IN 6 OF 8 PLAIN C CELLS, AND THE MECHANISM IS THE
ORDER OF TWO AUTOMATIC ARRAYS.** gcc at `-O0`/`-O3` and clang at `-O3` place
`bl[256]` **exactly 96 limbs above** `out[96]`, so the overflow lands **inside
the other scratch** — exit 0, wrong answer, **canary untouched**. clang at `-O0`
reverses them and SIGSEGVs. **This is p02's heap result moved to the STACK**, and
it is why the box's default `-fstack-protector-strong` does not help.
⚠ **The engineer's own pre-build probe said the OPPOSITE (5 of 6 loud) because
it had only ONE array.** Corrected in `NOTES.md` 0a.

**2. The cheapest unsafe spelling is NOT A RUNG, and the reason is the prover.**
`r4_mutreslice` is **−697 … −2597 `Ir`/call below the shipped R4 and below every
safe spelling**, exact law `−1 + 7n − 1.5nm − 2.5n[m odd]` over 48 blobs. It
takes a **mutable sub-slice, which the pinned vstd cannot specify** — four probes
(`controls/census.py --mutsub`): length ✓, frame ✓, *"write vanished"* correctly
fails, **and *"the written value is `7`"* FAILS.** ⚠ **`.memory/01-ladder.md`
finding 14's mechanism with a NUMBER on it — second measured instance after p16,
and the FIRST ON A WRITE.**

## The laws — one command re-checks them all

`controls/sweep_ir.py --check`, exits 1 on any residual. ✅ **Manager-re-ran,
exit 0.**

```
R5 - R4  =  0                              49 blobs, max |residual| 0.00000
R2 - R4  =  3 + 5n - n*floor(m/2)          48 blobs, max |residual| 0.00000
R3 - R2  =  2n - 2 (m even) / -2 (m odd)   48 blobs, max |residual| 0.00000
R1h - R1 clang = +2.00 flat (49/49)
```

⚠⚠ **BAND D EARNED ITS PLACE, AND THIS IS SHARPER THAN p38's MISSING COLUMN.**
Fitting on the two **axis-aligned** bands alone leaves the law
**UNDERDETERMINED** — a one-parameter family fits **both exactly**. One
off-axis point pins it and the other **nine are out of sample at zero
residual**. ⚠ **No in-sample residual could have shown it.**

## ⚠ One discrepancy the manager found re-running the checker

The report says gcc's `R1h − R1` has *"two unexplained `+3.00` exceptions (both
`m=48`)"*. **The committed checker prints `+3.00` on ONE blob** — `+3.00 on 1,
+4.00 on 48, exception(s) at ['24,48']`. **One exception, at `n=24, m=48`.**
Minor, but the prose and the tool disagree. **Named for the review.**

## PROTOCOL rule 6

Recorded **before any cell existed**:
`e6b12dc6cbfd52cd396aa13ff119ca7c48626c15087643c4faa7c22cb63c953a`.
Shipped: `bddd7e032a72592a2857678f2a1edc8d04919c358a406825513a716044b1abeb`.
**One edit**, forced by gate stage 5a demanding
`verus.unsafe_justifications['verus.rs']['arr_set_unchecked']` by name, made
**before any p46 number was measured**, changing no `required` / `forbidden` /
`identity` / `why`. ⚠ **The `git show HEAD:` test is vacuous on a new pattern;
the two hashes are the only evidence**, and `NOTES.md` says so.

## Problems

- **The engineer's own pre-build probes were wrong TWICE** (harm loudness, rung
  boundary). Both corrections are in `NOTES.md` with the mechanism measured, and
  **neither probe is quoted as a p46 number anywhere.**
- **Editing a doc comment in `verus.rs` staled the measurement record**;
  re-measured, and **every `Ir` figure came back bit-identical.** Only wall clock
  moved.
- `adversarial-oob` / `c-clang` opt-mode variants disagree (SIGSEGV at O0, silent
  at O3) — the gate notes it; **that IS the finding.**

## Unsure / not done

- **The mathematical product is not proved.** Disclosed in `spec.md`'s `note`,
  `verus.rs`, `README.md` and `NOTES.md` 6b.
- **No wall-clock claim** — the differences are 0.4–3 % of the kernel.
  `NOTES.md` 9 says so **rather than leaving the column to be quoted**.
- `m = 1` is a **domain restriction**, one blob, not an explained term.
- **`synthesis/synthesize.py::SEARCH_REVIEWED` deliberately NOT touched** — its
  own rule is that every entry cites a **reviewed** artefact, and p46 prints
  `undeclared`, **which is its true state**. **Owed after review**; the entry it
  wants is p11's shape.
- `.memory/06-catalogue.md`'s p46 row still says `planned`. ✅ **Landed by the
  manager.**
- ⚠ **The `black_box`-artefact finding is p46's own and has NOT been checked
  against any other pattern's probe. It may not generalise** — and every row in
  `TASK_086`'s queue was measured the same way.

## Memory updates owed (manager applies, AFTER review)

1. ⚠⚠ **A probe can lose the SLOPE, not just the intercept**, when it hides a
   range fact behind `black_box` that the real kernel derives from its input.
   p46: `+7` against `−0.39` `Ir`/MAC, **and the boundary itself vanished.**
2. **At the pin there is NO MUTABLE SUB-SLICE specification** — `slice_subrange`
   is `&[T]`-only, `ExSliceIndex::index_mut` has a `requires` and no `ensures`.
   `&mut v[i..j]` is **sound but VALUELESS**: frame provable, value not. Reusable
   probe committed.
3. `by (bit_vector)` needs the `u128` + `requires` spelling; both narrowing casts
   need `#[verifier::truncate]`; `lemma_fundamental_div_mod_converse` bridges the
   value-level identity to div/mod.
4. **The `ensures` census** — 159 conjuncts, 151 equalities, all 23 kernels
   carrying a full functional postcondition — with the command.
5. **Two automatic arrays' FRAME ORDER decides silent-vs-fatal for a stack
   overflow**, and gcc/clang disagree at `-O0`.
6. **A two-parameter law fitted on two axis-aligned bands can be
   UNDERDETERMINED**, not merely missing a term.
