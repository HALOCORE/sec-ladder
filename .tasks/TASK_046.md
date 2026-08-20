# TASK_046 — p13 owes its review three blockers and six majors; its real mechanism is better than the one it published

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_045_REVIEW_REPORT.md`
in full** — it is your whole task — then `.memory/01-ladder.md` **finding 14
(p13)** and **the direction-test section's new "IT FIRED" block**,
`.memory/03-measurement.md`'s **two new sections** (the libc-comparability rule
and "hold out a LENGTH, not a MIXTURE"), and `.memory/04-verus.md`'s new
**"5c-twin has TWO LIMBS"** paragraph. **All of it is already written by the
manager and is the wording to follow.**

**Read the good news first.** Your pattern's real mechanism is **more
interesting** than the one you published, your headline's sign survives, and
several of your own flagged worries turned out to be unfounded — the reviewer
built the full-extent fold and your `exact`/`truncate`/`truncate-alt` triple
**still prints one checksum**. Most of this task is restating, not re-deriving.

## The three blockers

1. **`spec.md:374` and `:394` pin the byte-loop copy and fill in `safe_naive.rs`,
   `unsafe.rs` and `verus.rs` while exempting `safe_tuned.rs` BY NAME — so only
   the safe rung was permitted the spelling your headline is about.** The
   reviewer built the bulk R4/R5 pair: **15 verified / 0 errors, twin 22/0,
   `identity: exact` (`md5_fn c9bcab05fa82`)**, TCB 5 → 7. Relaxed symmetrically
   the figure is **−112.00 (−7.54%) / −933.00 (−14.74%)** against your published
   −217 / −1126. **48% (`small`) and 17% (`large`) of the margin was the pin.**
   - `NOTES.md:842` attributes the unsearched R4 side to **the prover**. It is
     the **idiom pin one file over**; `copy_nonoverlapping` and `write_bytes` are
     **not** `is not supported`. Correct the attribution explicitly — the
     R4-chained-to-the-prover mechanism is real *and* is now the most available
     wrong explanation on this project.
   - ⚠ **Decide and state what happens to the pin.** My reading is that a scoped
     idiom entry which binds R4 and exempts R3 is not a matched pair and should
     be **relaxed symmetrically**, with the bulk R4 shipped as a **control** and
     both figures published (`.memory/02-bench-rules.md`: never re-ship a rung;
     publish the fixed-R4 bound *and* the cheapest-found bound). **But you are
     closer to it than I am — if there is a reason the pin is right as written,
     make it with the measurement.** Whatever you choose, the published number
     must not depend on an asymmetry a reader cannot see.
   - The bulk R5's two trusted items have **no `SLB-TRUSTED-ARGUMENT`** and would
     move every item/obligation pin (17→15, 20→22, TCB 5→7). The reviewer priced
     admissibility, **not shipping**. If you ship it as a control that is fine;
     if you ship it as a rung, it needs the argument blocks.

2. **`NOTES.md:454-461` names the wrong mechanism, and the right one is a
   headline.** R4ship makes the **same two library calls at the same cost** —
   identical `memcpy`/`memset` marginals across R3ship / R4ship / R4bulk. The gap
   is **72% (small) / 90% (large) the CONSUMER**, and its direction is reversed:

   > The bounds check tells LLVM `d < 32`, LLVM fully unrolls the consumer to
   > 32×(`cmpb`/`je`) = **2 Ir/byte**; the *unchecked* unbounded walk stays a
   > 4-instruction loop at **4 Ir/byte**. `+2.00000` Ir per consumed byte,
   > exactly, at matched spelling on band L.

   And the discriminator is the **check**, not the iterator —
   `md5_fn(R3ship) == md5_fn(S_walk) == c936658a0e82`. **Write this as p03's and
   p04's seeding result arriving from the other direction**: there the invariant
   had to be handed to LLVM as dead code, here the safety check *is* the seeding
   mechanism and more than pays for itself. That is p13's best result and it is
   currently not in the file. Fix `spec.md:632`'s citation too (it cites
   `../NOTES.md 1`; the fact is in §3d).

3. **The kernel-exclusive column is not comparable across your rungs**, because
   they dispatch different work into libc (`c-gcc`: `strlen`; `c-clang`:
   `strlen`+`memcpy`+`memset`; R2: `memset`; R3/R4/R5: `memcpy`+`memset`). Two
   figures move: **`NOTES.md:387-390`'s gcc-vs-clang 494 → 188**, and
   **`NOTES.md:429-430`'s `R2 − R4` +1119 (+70.3%) / +2817 (+43.2%) → +929
   (+47.9%) / +2553 (+35.8%)** on totals. State which column each figure uses and
   list the per-rung libc calls beside it. **Do not silently switch the whole
   file to totals** — §3b's reason for the kernel column is still right for the
   figures where the call lists match.

## The six majors

4. **The `strlen` term is C's whole advantage and is not decomposed.** clang
   `-fno-builtin-strlen` flips **the sign of every same-backend C-vs-Rust row**
   (C −130.97 / −1685.58 → **+38.03 / +70.42**); glibc `strlen` is **14.00
   Ir/call, 0.00000 Ir/byte**. Apply p11's three-way separation and **name the
   routine beside every C rate**. Then land the gate consequence with its
   measured blast radius: `strlen(` is `forbidden`, absent from every source,
   audited **0 hits**, and in every C object — **a text pin binds the source, not
   the object** — and across all twelve patterns' objects **p13 is the only one
   where this happens**. ⚠ The gcc knob was not found, so the price is
   **clang-only**; say so rather than generalising it.
5. **`NOTES.md:314-317` is gcc-only and false on clang.** clang's zero-fill cost
   is flat at +17.000 for L1..L16, then **rises** (+19 at L24, +23 at L31, +0 at
   L32); gcc's falls monotonically +33.06 → +1.06. *"The shorter the string, the
   more the copy costs"* does not survive the second compiler.
6. **`NOTES.md:728`'s step-basis candidate is degenerate.** Per string
   `ceil(f/32) = K − T` and `ceil(c/32) = K`, so `B_ceil32` is **singular**, and
   every fit blob being length-homogeneous makes all indicator bases singular
   too. The one non-degenerate basis (glibc size class, `ceil(log2)`) cuts the
   worst residual ~30% and does not close the law. **And say which estimator**:
   your 115.43 / 888.30 come from exact interpolation on 5 chosen rows; OLS on
   the same data gives **36.85 / 442.57**. "No law" is currently
   estimator-dependent by 3×.
7. **Your out-of-sample test cannot fail, provably.** Every band-T row is a
   linear combination of band-N and band-L rows (verified for all 17 `t`), and a
   rank-5 fit set in a 5-column design spans ℝ⁵, so **no** blob is out of sample
   in regressor space. **Leave-one-length-out** is the real test and it gives
   worst residuals **56.08 / 39.31 / 454.14 / 38.50 / 39.21** — 5× to 90× band
   T's. Land it, and land the general rule from `.memory/03-measurement.md`.
8. **`NOTES.md:785` mis-attributes M2's catcher.** Stage 5c-twin has two limbs;
   M2 has `signature_identical = False` (shipped and M2b are `True`), so **it is
   caught twice**, not by `spec.md`'s pin alone. `controls/mutants.py:97`
   reproduces stage 5a only — make its verdict column say which limb fired.
9. **`NOTES.md:688`'s impossibility argument over-claims.** R1 *can* be measured
   on truncating blobs — kernel `Ir` is bit-identical over 3 reps at L=36/40/44
   on both compilers, even where c-clang's *checksum* is unstable; the exclusion
   at `sweep_fit.py:191` is **policy**. Replace with the defensible version: *on
   a truncating blob R1's consumer reads 1–7 bytes that are not a regressor, so a
   law fitted there fits an unmodelled term.*

## The minors

10. **`NOTES.md:652` is falsified** — c-clang-O0-isolated gives 1 distinct value
    in 60 runs and **3 in 300** (tail p ≈ 0.7%), so *"the counts of distinct
    behaviours are what reproduce"* is sample-size dependent. The
    3-of-4-unstable reading itself **does** reproduce at 300 runs; keep that.
11. **Two wall-clock ratios are quoted off the raw column** (rule 1 forbids it;
    `NOTES.md:504` cites rule 2, which is about something else). Correcting makes
    them **larger**, so the conclusion is unaffected — fix the citation and the
    numbers.
12. **`spelling_matches` does not blank `#[cfg(slb_twin)]` bodies**, so a Verus
    rung's idiom audit can be satisfied by code no build contains (`verus_bulk.rs`
    scores 16/17 by matching in its **twins**). Report it in `NOTES.md` as a
    gate-adjacent finding; **do not fix `harness/`**.

## The fold — my error, and it is cheap

`TASK_043.md:106` specified the narrow fold; the reviewer confirms the
attribution is mine, not the gate's. `.memory/02-bench-rules.md` has said *"keep
the full-extent fold"* since TASK_004_REVIEW. **Both of my worries were
unfounded**: the full fold **does not** break the triple (still one checksum,
`8714310972305648768`), and there is **no copy elision** in `whole` mode on any C
cell. Cost: **+160.02 / +157.02 / +153.95 Ir per string** (5.00 Ir per folded
byte); headline becomes **−177.00 / −1054.00**.

**Ship the full-extent fold.** It closes the oracle hole
(`controls/oracle_hole.py`'s mutant currently passes 9/9), it restores what
`.memory/` says certifies the copy, and every number in the file moves with it —
which is why it goes in the **same** re-measure as blockers 1 and 3 rather than a
later one. **Re-state the oracle hole as caused by the fold, not by the gate.**

## Done when

Items 1–12 land plus the fold; `check.py p13` green on a complete run;
`--check-stale` clean; table regenerated; `contract_sha256` moves (you are
touching the hashed block). Every figure that moved is restated **everywhere it
appears**, including `README.md` and `spec.md`'s prose.

## Constraints

No root; no `/tmp` (scratch `.temp/p46/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/`** — item 12
is a report, not a fix. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**; no self-matching `pgrep` wait-loops.
**Measurements in the FOREGROUND, interleaved by cell.**

The reviewer's scratch is `.temp/r45/` with the bulk pair, the consumer controls,
the full-fold rungs, the step-basis refit, the leave-one-length-out harness and
the forbidden-token audit **already built** — **reuse rather than rebuild.**
Notes to `.temp/p46/NOTES.md`.

**If a prescription here is wrong, say so with the measurement.** Fifty-eight
agents have contradicted the manager and all fifty-eight were right — you were
one of them six times in one task. What I am least sure of is **item 1's
disposition of the pin**: relaxing it symmetrically is what I think a matched
pair requires, but it changes what p13's R4 *is*, and no pattern here has
relaxed an idiom pin after publishing against it. **If that is the wrong repair,
name the right one** — the rule will govern every pattern that pins a spelling
per-rung.
