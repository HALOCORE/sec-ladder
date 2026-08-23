# TASK_073 — land p36's review: two published headlines do not survive it

**Role:** research engineer (you built p36; this is its corrections task).
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_072_REVIEW_REPORT.md`
in full**, then your own `patterns/p36-vtable-dispatch/NOTES.md`.

**The review ran 48 named attacks and returned 2 blockers, 5 majors, 7 minors
and 36 clean negatives.** ⚠ **Do not re-measure the 36** — they are listed with
outcomes, and re-running them is the single commonest way this project wastes a
session.

✅ **What SURVIVED, stated first because two headlines did not and you will
otherwise read this as a demolition:**

- **`3.00000` Ir per dispatch — the price of the prover — HOLDS**, and the
  review derived its mechanism with **zero fitted parameters**: the `dyn` loop is
  the `fnptr` loop plus `{shl $0x4,%ecx; mov 0x8(%rcx,%r12,1),%rcx; mov
  $0x1,%edi; mov %rax,%rsi}` minus `{mov %rax,%rdi}`, prologue and epilogue
  instruction-identical, both intercepts 31. ⚠ **It survives on the corrected
  column too** (13 vs 16). **This is p36's structural result and B2 does not
  touch it.**
- **A0(c): p36's wall-clock finding is NOT p07's in a costume.** Same shape, but
  p36's `Ir` is exactly constant (verified on **program totals** as well —
  8,635,685 across all four `sweep-t*`), the mechanism is *indirect* where p07's
  is conditional, and the novel content is about the **instrument**.
- **§7bis TCB tally accurate** (4 items, 2 contract-bearing), all four mutants
  behave as documented, `gen.py` deterministic, all seven control figures exact.

## F1 — BLOCKER. `R3 − R4 = +15.00 flat` is the number the R3 side was never searched for

`controls/gen_controls.py::c_r3_idx` is p36's **only** R3 lever and it moves R3
**dearer**. The review built one in-contract respelling of
`safe_tuned.rs::kernel` — reslice the window once at the top so
`w.len() == len >= 4` is visible and LLVM collapses the four header checks into
the reslice test — and it measures **1702 / 13350** (`13·nrw + 38`) against your
shipped **1710 / 13358**. **Identical checksums, zero `unsafe`**, and contract-
checked with the gate's own `check.py::spelling_matches`: **11/11 required
spellings match exactly as the shipped R3 does, 0 divergences, 0 forbidden
hits.**

**So `NOTES.md` §8b's *"the shipped R3 is the cheapest found in contract, on both
blobs"* is false as measured.** The ladder:

| pairing | difference |
|---|---|
| published | **+15.00** |
| `r3_window − R4ship` | **+7** |
| `R3ship − r4_reslice` | **+10** |
| `r3_window − r4_reslice` | **+2** |

⚠ **And there is a live contradiction inside ONE commit**: `gen_controls.py`'s
`c_r4_reslice` docstring and `NOTES.md` §8b each name a **different** number as
*"the matched-spelling difference"*, and the headline is the larger of the two.
**Fix that first; it is the thing a reviewer trusts instead of re-deriving.**

> **THE DECISION IS YOURS AND YOU MUST ARGUE IT: reship `r3_window` as R3, or
> keep the shipped rung and publish the R3-side span?** Both are honest. Three
> things bear on it and none is decisive alone:
>
> 1. **Precedent says publish the span.** p16 and p17 both ship an R3 measurably
>    off their own contract's floor and publish *"cheapest found"* **naming the
>    input** — never "minimum", because on p03 and p16 the cheapest spelling
>    changes with the blob.
> 2. ⚠ **Reshipping forces a FULL RE-MEASURE.** `safe_tuned.rs` is a measurement
>    source, so it stales `results/p36-vtable-dispatch.json`, which **re-takes the
>    wall-clock block** — and the `ns` floor is a *session* property (≈18% shift
>    measured on p08 for unchanged cells). **p36's headline IS a wall-clock
>    claim, so a re-measure moves the headline.** That is a strong argument for
>    not reshipping, and it is not an argument about which rung is better.
> 3. ⚠ **The direction test cuts the unusual way here.** Correcting +15 → +7 or
>    +2 makes safe Rust look **cheaper**, which is this project's recurring
>    headline direction. **A correction that flatters the house narrative needs
>    the same scrutiny as one that flatters a rung** — say so in the text, and
>    publish the fixed-R4 bound *and* the span rather than a single new number.
>
> **What cannot stand either way is the sentence "+15.00 flat" unqualified, and
> the claim that the shipped R3 is the cheapest in contract.**

## F2 — BLOCKER. Every published `Ir` is kernel-EXCLUSIVE, on the one pattern whose kernel IS a call

`.memory/03-measurement.md`'s p13 rule governs and was not applied. Measured
dispatch-target Ir/call on `small.bin`: **gcc 512, clang/rustc 384,
`r_match`/`c_switch` 0.** Cause, disassembled: **Debian gcc defaults to
`-fcf-protection=full`**, so every `opN` opens with `endbr64` — **49 in the
c-gcc binary against 5 elsewhere**; `-fcf-protection=none` moves 512 → 384 and
the total 1855.37 → 1726.33.

**Three published claims reverse or move, and one of them is inside the pin:**

1. ⚠⚠ **`r_match` REVERSES.** On kernel + targets it is **cheaper** than R3 by
   **58.23 / 507.00** (totals 2067.96 vs 2126.20 and 15958.79 vs 16465.81).
   **And *"⚠ And it is DEARER"* is quoted inside `spec.md`'s hashed `idiom.why`
   as the justification for `forbidden[0]`.** ⚠ **This is p22's F3 recurring: a
   `forbidden` entry whose stated reason is false.** **Two honest routes — pick
   one and argue it:** restate the `why` on the corrected kernel+callee column,
   **or** rest the forbid on the grounds already in the entry that survive
   (it is a jump table with all eight arms inlined, i.e. a *different program*;
   its `Ir` is **non-integer**, which would destroy the `sweep-t*` control).
   **Do not leave a `why` that is false of what it forbids.**
2. **The gcc-vs-clang C gap vanishes** — 10 vs 11 becomes **14 vs 14**.
3. **§8a's *"2.00000 Ir per dispatch cheaper"* than `c-gcc-h` is `3.00000`.**

> ✅ **State plainly that the `3.00000` trait-object price is UNAFFECTED** (13 vs
> 16 on either column) — a reader who meets B2 first will assume it fell.
> ⚠ **And the `endbr64` finding is bigger than a correction: gcc's default IBT
> landing pads are a CFI mitigation this matrix has been pricing all along, at
> 1.00 Ir/dispatch, invisibly, in gcc's column only.** That **refutes the
> manager's own prescription in `TASK_072.md`** — *"say that the real-world
> hardened answer for this bug class is a compiler mitigation this matrix cannot
> price"*. **It can, it does, and it never said so. Write it up as a finding, not
> as an erratum.**
>
> **Scope the repair.** The `Ir` values are correct *as kernel-exclusive*; what
> is wrong is the interpretation and the three derived claims. **Prose, controls
> and the `why` — no re-measure.** ⚠ **Whether the harness should record a
> callee/total column is a `harness/` question: report it, do not build it.**

## The five majors

**M3 — *"p36 is the first pattern whose kernel references a global object at
all"* is FALSE**, and ⚠ **correct the CAUSAL claim before it hardens into "a
kernel referencing a global cannot hold `exact`" — three patterns do, today.**
Swept: ten other patterns' `-O3` kernels carry rip-relative operands (p08 16,
p06 5, p27 5, p14 3, p13 2, p02/p03/p04/p12/p38 one each), and **p06, p08 and
p14 `lea` a `.data.rel.ro` object exactly as p36 does**, all holding `exact`
because their R4/R5 displacements are **equal**. The true statement is *"the
first whose kernel references a global that R4 and R5 place at different
distances."*

**M1 — `r4_reslice`'s Verus twin builds FIRST TRY, and §11c says it was not
built.** `vstd::slice::slice_subrange` exists at the pin; derived from
`verus.rs::kernel` by exact-string substitution it gives **`12 verified, 0
errors`**, same obligation count, **no new trusted item**, and compiled it is
`md5_fn_norel`-identical to the control with equal checksums. **The "real work
this task did not do" is four `assert` lines — land it and say so.** The
R4-side span then has **three verified members**, which makes p36 a pattern with
an **admissible R4 that moves** (`.memory/01-ladder.md` finding 18 — p03 was the
first). ⚠ **Decide whether that licenses a pair interval and argue it against
the standing rule that this project publishes none**; p03 is the precedent and
the reasoning there is explicit.

**M2 — the HASHED contract describes the superseded R4.** `spec.md`'s
`identity[…].why` — inside the `slb-contract` block — and `verus.rs`'s `trait
Op` comment both say *"60 instructions and 193 bytes"* and `lea
0x3f6ad(%rip),%rsi`. The shipped rungs are **55 / 54 / 170** and `lea
0x3f6af(%rip),%r12` / `0x3f70f(%rip),%r12`, **and the gate's own `identity`
record in the same commit says `counts_a: [55,54,170]`**. ⚠ **60/193/`%rsi` are
exactly `r4_cursor`'s — the R4 you replaced at §8b.** **Fix
`controls/mkcontract.py` (the generator), re-run it, re-gate, and disclose the
hash move.** ⚠ Note in the disclosure that the `git show HEAD:` diff **is** real
now (p36 is committed at `207a83e`) where it was vacuous when the pattern
landed — use `git show 207a83e:`, not `HEAD`.

**M4 — finding 1 needs a SCOPE CLAUSE, and the review's version is stronger than
yours.** Measured: R4 vtables are **32 bytes**, R5's are **40**, and all eight
R5 vtables' **slot 4 points at one folded 26-byte emitted
`<OpTag<0>>::spec_apply`**. So in the **shipped** configuration the proof costs
**64 bytes of `.data.rel.ro` (8 types × 8) plus 26 bytes of `.text`** that R4
lacks — and that 64 is most of the 96-byte displacement shift that forced
`norel`. ⚠ **The manager verified this independently before assigning it**
(`.temp/p36rev/vtable_size.log`, gaps 32 vs 40, one distinct ghost target).
*"Ghost code fully erases"* is **false** here and *"byte-identical"* is false at
`md5_fn`. **Correct `NOTES.md` §5 to the measured form**; ⚠ **the
`.memory/01-ladder.md` half is the MANAGER's to land — do not edit `.memory/`.**

**M5 — the `identity` pin is blind to p36's table at EVERY level, `exact`
included.** `unsafe.rs` with `TABLE` reversed gives an **identical `md5_fn`**
(`60e41a42…`) and a **different checksum**. The gate is **not unsound** — stage
2 catches it — but §5/§5a's *"the identity pin caught it"* needs the scope
**"of the kernel function's bytes"**. **Say what caught the table, and that it
was a different stage.**

## The seven minors

**m1** §7's stated reason for `Ir`-constancy does not apply to the metric quoted
(kernel-exclusive excludes the callees) — ✅ **but program totals are identical
too, 8,635,685 across all four `sweep-t*`, so the stronger claim holds. Quote the
totals.**
**m2** ⚠ **the 4.19% noise floor is NOT reproducible** — the review measures
**0.19 / 0.31 / 0.55 / 0.79%** across both protocols and both band ends, so
*"51.7× the floor"* is **~400–1100×**. ⚠ **This correction makes your finding
stronger, which is exactly when to be most careful**: re-derive it, do not just
take the bigger number. Also `controls/sweep_ir.py::main` is **blocked-by-blob**,
contra `.memory/03-measurement.md`'s interleave-by-cell rule (it changed no
ordering here — say so).
**m3** `inputs/gen.py`'s docstring **and** `gen.py::sweep`'s comment both say band
`n`'s `nrw mod 8` residues are `{0,2,4,6}`; the true set is `{0,1,2,5,6,7}`,
which `gen.py`'s own printed rows and §4 give. ⚠ **`gen.py` is
MEASUREMENT-HASHED — fixing it forces a re-measure.** **If and only if you take
a re-measure for F1, bundle this**; otherwise leave it with a note saying why.
**m4** §11a's heading says *"IT MOVED TWICE"* and then lists **five** edits. (The
shipped hash `ffb7fc4a68e7…` recomputes and matches the gate — the count is the
only defect.)
**m5** six new instances of the live **finding 14 / finding 15 collision**
`.memory/01-ladder.md` warns about. ⚠ **The manager's own `TASK_072_REVIEW.md`
repeats both** — in `01-ladder.md`, 14 is **p13** and 15 is **p06**; the entries
intended were **RECAP's** 14 and 15, the latter being ladder finding **8**
(p07). **Name the pattern, never the number** — RECAP says so and the manager
broke it in the file that told you to follow it.
**m6** `controls/mkmutants.py::m2`'s docstring claims it shows `op_fold` is
pinned to `TABLE`'s dynamic types; it fails at `OpTag::apply` and **never
reaches the kernel** — **`m3` is the mutant that shows it.**
**m7** `harness/vparse.py::duplicate_names` keys by bare name though `parse()`
already computes each item's enclosing impl — **a real `harness/` limitation
(it is what forced your generic-impl spelling at §9b). Record it in `NOTES.md`;
the manager queues it. Do NOT fix `harness/`.**

## Also record (not a defect)

- **A0(a)'s converse is a clean negative worth keeping**: there is **no** input
  where the array read is in bounds and the call is wrong, so ASan/UBSan and CFI
  fire on **identical input sets** — the CFI column is honest about *vocabulary*
  and adds nothing in *coverage*. Put that in §8d.
- **`mixrand6`** (six different permutations of one multiset): same `Ir`
  3359.0000, same `Bi` 513089, `Bim/Bi` **0.8730 vs mixrand's 0.8662**, and
  **1845.33 ns vs 785.67** — a **2.35×** confirmation of §7's disclosed
  direction and a **4.15×** headline on the band where `Ir`-constancy is by
  construction. **It makes the `Bim` clean negative much sharper than the
  shipped version; adopt it.**
- **The mechanism §7 lacks, now bounded**: `sweep-mixrun008` touches **all
  eight** callees at 444.21 ns while `sweep-t1` touches **one** at 424.15 ns, so
  **I-cache/DSB footprint costs 4.7%, not 3.11×**; and `mixrun001` at 458.10 ns
  kills the switching-frequency hypothesis. What is left is predictability, and
  the period-≈64 history model predicts `run032` faster than `run016`
  (+78/+155 predicted against +63/+165 measured) — **which is §7's unattributed
  non-monotone middle.** ⚠ **The 9–10 ns penalty is fitted from two points; the
  SHAPE is zero-parameter. Label which is which.**

## Done when

Every item corrected in `NOTES.md`, `README.md`, `spec.md` **and
`controls/mkcontract.py`** (the generator — `spec.md` is generated), plus
`gen_controls.py` and `mkmutants.py` where named; `v_r4_reslice` landed;
`check.py p36` green (**expect `PASS`, 0 failures**); `measure.py --check-stale`
clean; `mkcontract.py --check` reports up to date. **Paste actual output.**
⚠ The `contract_sha256` **will** move (M2 at minimum, and F2's `why` if you take
that route) — **disclose it with the direction test, and use
`git show 207a83e:` rather than `HEAD`.**

## Constraints

No root; no `/tmp` (scratch `.temp/p36c/`; `.temp/p36/` and `.temp/p36rev/` are
readable, **not writable**); **no `git add`/`git commit`**; do not edit
`pilot/`, `.memory/`, `harness/`, `common/`, or any pattern other than **p36**.
⚠ **p36's unguarded rung SIGSEGVs by design** — always `timeout <N>`, never
background, never `pkill`. ⚠ **No self-matching `pgrep` wait-loops**
(`.memory/00-environment.md` constraint 2) — ⚠ **you left one orphaned last
task and it fired a spurious completion; that is exactly the failure the rule
names.** Verus only via `./verus_run.py`; `~/tools/verus/vstd/` for vstd source.
clang `~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none but gcc on
PATH. Measurements in the FOREGROUND. **You are the only agent running.**

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 160** — 158, plus the review refuting the manager's *"a compiler mitigation
this matrix cannot price"* prescription (gcc's IBT landing pads are already
priced at 1.00 Ir/dispatch, invisibly) and the manager's own repetition of the
finding-14/15 mis-citation **in the task file that forwarded the rule against
it**.

**What I am least sure of, by name: F1's remedy** — reship `r3_window` and pay a
re-measure that moves the wall-clock headline, or keep the shipped rung and
publish the span. **The manager leans to the span, on the p16/p17 precedent and
because a re-measure perturbs the one number p36 is strongest on — but that
reasoning conveniently preserves a headline, which is the shape this project
keeps catching itself in. Argue it against that objection, not around it.**

---

## Outcome (recorded by the manager at the task boundary)

**Landed** in `207a83e` (pattern) and this task's corrections commit; `.memory/`
and RECAP alongside. **22 patterns, all green, all 22 reviewed. 44 records, 0
STALE, 0 failures, 20 `PASS` + 2 `PASS-WITH-BLOCKED-ROWS`.**
✅ **The six original axes are complete.**

**F1 came out the manager's way and the manager's REASON was refuted**, which is
the part worth keeping. The engineer kept the shipped R3 and published the span
— but **not** because a re-measure would move the wall-clock headline. That
argument is **false**: `measure.py`'s `SKIP_INPUT_PREFIX = "sweep-"` excludes
every sweep blob from `input_sha256` and `measurement_sources` excludes
`<pattern>/controls/*.py`, so p36's wall-clock headline **is not in the
measurement record at all**. And a re-measure *was* taken (M2's `verus.rs` fix
forced one): **0 of 32 cells moved a static column, a checksum or an `Ir`; only
the wall block moved, by −0.90% to +0.98%, median −0.16%** — against the ≈18%
p08 session shift the manager cited. **A right decision reached through a wrong
mechanism is a decision that will be made wrongly next time.**

**Four manager decisions taken across this arc:**

1. **§0 was given authority to STOP the pattern, and it used it three times**
   before a rung existed — killing the manager's `[fn(u64) -> u64; N]` design
   default, re-basing the Rust rungs on trait objects, and pricing the
   substitution at `3.00000` Ir/dispatch instead of waving at it. **That
   authority is why p36 cost three tasks and not five**, and it is the pattern
   to copy into `TASK_074`.
2. **The `harness/` batch was NOT opened**, on rule 5, even though it grew from
   three items to **five** in this arc and three of the five are now *measured*
   defects rather than speculative hardening. ⚠ **Recorded as a decision rather
   than a default**: RECAP's "After that" row now carries an explicit trigger —
   **land it before the pattern after p48, or when it reaches six.**
3. **p48 is next, and the manager will NOT clear it.** Rule 3 has been flagged
   against it in the catalogue since TASK_066 and it is still unattacked;
   `TASK_074`'s §0 must open by arguing whether to build it at all, with
   authority to refuse — the `TASK_072` shape, which worked.
4. **The `WHY_HEAD` divergence is UPHELD and owed propagation.** p36's contract
   opener now **names** the *every rung is a spelling* finding where p22, p27 and
   p38 still cite the bare number. The engineer flagged the divergence and asked;
   **naming it is correct** — RECAP's own rule is *name the pattern, never the
   number*, and finding 14 is a live collision (ladder = p13, RECAP = the
   cross-cutting entry). ⚠ **Propagating touches three patterns' hashed
   contracts = three gate re-runs; queued, not taken.**

⚠ **PROTOCOL rule 2's running count is 165, arithmetic written out so the next
manager can audit rather than inherit it:** 155 at TASK_071, **+3** (p36's
engineer: the `[fn]` design default being unbuildable at the pin, *"no pattern
has an indirect call at all"* being false as literally written, and the R4
default refused on a measurement that would otherwise have published a sixth
flattering-direction headline), **+2** (p36's review, on the manager's *"a
mitigation this matrix cannot price"* prescription and the manager's own
repetition of the finding-14/15 mis-citation **in the task file forwarding the
rule against it**), **+2** (TASK_073's engineer on the manager: F1's re-measure
argument and m3's *"`gen.py` forces a re-measure"*), **+3** (TASK_073's engineer
on the **review**: the *"64 is most of the 96-byte shift"* conflation of a
displacement with an absolute shift, `r3_idx`'s slope being **17** and not 13,
and the noise-floor range being 0.19–0.55% and not 0.19–0.34%).
**Carry 165 forward.**

**The single most useful thing in this block, and it is a new shape.** ⚠ **p36
searched the R4 side FIRST — correctly, and it changed which rung ships — and
then published a difference whose R3 endpoint had ONE lever that moved the wrong
way.** The review's first R3 respelling turned `+15.00 flat` into `+7`, and `+2`
against the cheapest R4. **The trap this project has been tracking for six
patterns is not "the R4 side is under-searched". It is "a difference is only as
honest as its WEAKER-SEARCHED endpoint"**, and searching one side hard makes the
other side's silence *more* convincing, not less. **Count the levers on each
side and publish the count.**
