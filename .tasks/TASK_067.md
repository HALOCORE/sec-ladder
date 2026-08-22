# TASK_067 — land p38's review: the additivity law is repairable, and the harm needs four conditions

**Role:** research engineer (you built p38; this is its corrections task).
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_066_REVIEW_REPORT.md` in
full**, then your own `patterns/p38-alias-pun/NOTES.md`.

**The review returned NO BLOCKER, 3 majors, 8 minors and 35 clean negatives, and
ALL SIX of your refutations of the manager hold.** Do not re-measure what
reproduced — 35 attacks are listed with outcomes precisely so you don't.

⚠ **It also refuted four premises in the task files, three of them the
manager's.** Take these as given; they are measured:

1. **A5's direction was inverted — and it is p10's defect, not its opposite.**
   The manager wrote that an unsearched-cheaper R4 flatters *unsafe*. It flatters
   **safe**: `r4_slice` is −3.00/−7.00, so `R3 − inf(R4 found)` is **+24/+32**
   while `README.md` publishes **+21/+25**. **A smaller published tax makes safe
   look closer to unsafe** — `.memory/01-ladder.md` finding 18's direction
   verbatim, at 14%/28% of the headline.
2. **"Add `nw` and refit" makes it WORSE** (OOS 86.66 → 102.74). The manager
   prescribed it as the thing that would settle A3. It does not.
3. **Your stated A3 cause is measured false.** `R2 − R4` is *exactly constant* in
   `nw` — `115.00` at `nw` ∈ {128,160,200,240,248,256} for `(nrec,rlen)=(2,4)`.
   `nw` is not the missing regressor.
4. **"A UB class that exists only at `-O2` and above" is false — it is
   FLAG-gated, not LEVEL-gated.** `gcc -O1 -fstrict-aliasing` already prints the
   wrong checksum and ASan already reports `stack-buffer-overflow READ of size 2`.

## The three majors

**M1 — the additivity failure is REAL, its published cause is FALSE, and the law
is EXACTLY repairable.** `NOTES.md:309-324`, `README.md:66-72`, and **§4c
publishes the misspecified fit as an equation — those three coefficients are
artefacts, not p38 results.** The manager asked "real non-additivity or bad
band?" and the answer is **both, and neither is `nw`**:

- **(a) a genuine `nrec × rlen` interaction, through the PARITY of `rlen`** —
  `s(rlen) = 6.5·rlen − 8` for even, `− 18.5` for odd; odd records cost 10.5
  **less** each. Invisible to your design because band `r` fixes `rlen = 4`.
- **(b) a band-design defect whose column is `nw mod 8`** — band `r` (240) and
  band `x` (256) are both `0 mod 8`, while **band `w` sits entirely at 244
  (`4 mod 8`)**, a flat −22.
- **(c) the repaired law**, which the review states and validates:
  ```
  R2 - R4 = A(nw mod 8) - 8*nrec + 6.5*nrec*rlen - 10.5*nrec*(rlen mod 2)
            A(0) = 79 ;  A(m) = 33 + 6m  for m = 1..7
  ```
  **max abs residual 0.00000** on band `x` out of sample (6 rows), on an
  independent 49-cell `(nrec × rlen)` grid never measured before, and **0.00 on
  both matrix blobs** (small 257, large 711). In-sample exact except
  `sweep-w01`, already disclosed.

> **Rewrite §4c around the repaired law and DELETE the misspecified equation**
> (or keep it explicitly labelled as the artefact it is). **Re-state the headline
> honestly**: *"the first failure of this project's additivity test"* survives
> **as an event but not as written** — it is **100% attributable**, half a real
> interaction and half a band sitting on an anomalous `nw` residue, and the model
> was missing **two** columns, **neither of them the one named**. ⚠ **That is a
> better finding than the one you published**, because it is the DOMAIN rule
> landing on a real case: the domain was a missing column, twice over.
> **Re-run the fitter and paste the residual tables.**

**M2 — "structurally blind" is wrong, and as written it misdirects the queued
gate fix.** `NOTES.md:371`, `model.py:228-248`, `README.md:79`. The hole is real
but it is **one flag wide, not one optimisation level wide**: adding
`-fstrict-aliasing` at `check.py:4738` makes stage 7 see p38 **at `-O1`**. Read
literally, your text says the repair is to raise stage 7's opt level, **which
would perturb 20 patterns**.

> ✅ **And the review measured the blast radius the manager asked for, across all
> 20 gate records: EXACTLY ONE PATTERN.** 16 patterns declare ≥1 `fires` input
> and **every one fires at `-O1`** (including p18, the other UB pattern, on all
> four rows). Of the four with none — p01, p08, p47, p38 — p01/p08 model no
> memory bug and p47's harm is timing. **p38 is the only pattern whose
> declared-clean adversarial row is clean because of the gate's BUILD FLAGS
> rather than its kernel.** Say exactly that, in those terms.
> ⚠ **Do not change `harness/`.** It is queued to be batched (RECAP "Owed" 12).

**M3 — idiomaticity is asserted, not evidenced, and the strongest honest sentence
in the pattern is unwritten.** `c/kernel.c:7` claims *"the pair is written this
way in real parsers"* with **no citation**, and `:19-23` says the pun *"is the
whole of p38"*. It is one of **four conjunctive conditions**, and the review
found **five neighbouring one-line spellings that each remove the harm** —
symmetric punning accessors, one getter call, no write-back, `-fno-strict-aliasing`,
and a two-pass sanitise-then-walk.

> **State the four conditions explicitly**: (i) getter and setter disagree about
> type, (ii) a *second* getter call after the setter, (iii) the write-back has no
> consumer but that second read, (iv) both accessors in one optimisable region.
> ⚠ **Condition (iii) is structural here** — `sc[i]`/`sc[i+1]` are read by
> nothing else, so **the clamp store exists only to be re-read three lines
> later**, and the realistic reason to write a clamp back (a later pass) is the
> shape your own `harm4.c` found does **not** reproduce.
> **Drop the uncited "real parsers" claim** or cite it. The bug class is real and
> ASan-confirmed; that claim is not.
>
> ✅ **Then write the sentence the review says is missing, because it is p38's
> best result and it is fully measured:** *on gcc the undefined spelling is the
> **dearest** of the five neighbouring spellings — three independent one-line
> fixes each save exactly **6.00 `Ir`/call**.* ⚠ **And fix §8c's attribution**:
> it frames that 6.00 as a property of the **flag**; it is a property of **not
> doing the double read**.

## The eight minors

**m1** `README.md:97-98` publishes `R3 − R4 = +21.0/+25.0` and `NOTES.md:306`
says *"O(1) per record"* with **no R4-side disclosure** — it exists only in §8b/§10d.
**Put it in the README**, with premise 1's direction stated: the gap flatters safe.
**m2** `NOTES.md:328` says **6 of 32** O3 wall cells discarded;
`results/tables/p38-alias-pun.md:194` says **4** and lists four. Recount says
**four** (11.09/11.66/10.92/10.25). Fix `NOTES.md`.
**m3** **The ASLR attribution is wrong for the row the headline uses.**
`adversarial-stale` *is* ASLR-deterministic (4/4 identical under `setarch -R env -i`);
**`adversarial-oob` varies 4/4 with ASLR disabled**, and again with
`-fno-stack-protector`. Correct `NOTES.md:211-218` and `README.md:52`. ⚠ **The
review could not find the true cause either — say "cause not established", do not
substitute a second guess.**
**m4** the "clang declines" mechanism is **narrower than the mechanism**. The
discriminator is **whether BasicAA can compute the offset**, not "the same
address": `opaque_off` (one base, opaque offset) is **exploited** by clang, and
`one_base_partial` is **never** MustAlias yet is declined. **p38's own kernel is
the partial case** (two 2-byte stores vs one 4-byte load), which your wording
does not cover. Also add: **clang merges the two `uint16_t` clamp stores into one
32-bit store** where gcc emits two — a second reason its forward is
type-consistent. Conclusion (*"clang is safe" is false*) is **upheld**.
**m5** TySan §6a: "promotion" is right for the **object**, incomplete for the
**count**. Add the review's **M4** control (one TU, inlined, stack, no escape,
dynamic index ⇒ unpromotable; fires at every level) — it isolates promotability
from inlining/escape/heap and **strengthens** your claim. But M2's 2→1 at `-O2`
is **not** promotion (a dead `store i32`, after which the report changes
direction), and p38's own kernel halves 160000→80000 at `-O2` on an array that is
never promoted. **Accurate wording: *TySan checks only accesses that survive to
the end of the pipeline; promotion is the case that removes all of them.***
**m6** `c/kernel.h:22` documents the hardened spelling as `| ((uint32_t)r[1] << 16)`
— it is `+ 65536 *`, and the contract's `why` says it is written with `+`/`*` and
**never** with `|`/`<<`. `:36` writes the guard subtraction-first, the form
`required[3]` exists to forbid. Comments are blanked so no stage sees either —
**fix both anyway**; they are the next reader's mental model.
**m7** ⚠ **`s_asan_O3` is cited in THREE committed files and does not exist** —
`NOTES.md:371`, `model.py:242`, `spec.md:200` (hence `mkcontract.py:635`). The
`-O3` ASan build is anonymous inside `do_sanitizers()` and **cannot be selected
by name**. This is PROTOCOL rule 10's class **inside the hashed layer**. Either
give it a real name in `gen_controls.py --list` or fix all three citations; ⚠ **and
the fix must go in the GENERATOR too** — `spec.md` is generated.
**m8** ⚠ **`NOTES.md:653` (§10a row 3) is not self-consistent, and it is the only
snapshot that exists.** It says **six** spans were de-backticked and that
`required_pins_nothing` went **"4 → 0"**; six such spans move it by six. And one
of the six, `nw - i >= 2`, **is not in the shipped block at all** — so that entry
was rewritten, not de-backticked. ✅ The **final sha256 checks out**
(`9a413347f333…`, 9 `required`, 10 `forbidden`, both counters 0), so the contract
is fine — **the narrative is what does not add up.** Correct it, or state plainly
that the third edit's account cannot be reconstructed. **A wrong disclosure
removes the check it exists to enable.** Related: `required[1].rust` pins
`` `[u16; 256]` `` while its English says "all four Rust rungs" — it occurs only
in `verus.rs`; the other three write `[u16; SCRATCH_W]` (3 unread pairs).
**m9** §4b/§4c **name neither the inline mode nor the `Ir` convention**, against
`.memory/03-measurement.md` and TASK_066's own instruction. §4a is
kernel-exclusive; §4b/§4c are whole-program marginals from `-O3 isolated`.
Harmless here (verified) — **but by luck, not disclosure.** Label them.

## Done when

Every item above is corrected in `NOTES.md`, `README.md`, `c/kernel.h`,
`model.py`, `spec.md`, the controls and `results/tables/p38-alias-pun.md`;
`check.py p38` green; `measure.py --check-stale` clean; `mkcontract.py --check`
still reports up to date. **Paste actual output.** ⚠ Doc edits make a gate record
STALE — re-run **after** editing. ⚠ If `spec.md` moves, **fix the generator and
re-run it**, and **verify your disclosure with
`git show HEAD:patterns/p38-alias-pun/spec.md | diff - patterns/p38-alias-pun/spec.md`**
— which **is** possible now that p38 is committed, unlike at TASK_066.

## Constraints

No root; no `/tmp` (scratch `.temp/p38c/` — **your own subdirectory**; leave
`.temp/p38/`, `.temp/p38rev/`, `.temp/p38probe/` alone); **no `git add`/`git
commit`**; do not edit `pilot/`, `.memory/`, `harness/`, `common/`, or any
pattern other than **p38**. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc` (13.3.0), valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none but gcc on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**.
Measurements in the FOREGROUND, per-PID scratch paths. **You are the only agent
running.**

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 140** — 136, plus the review refuting four premises: the manager's inverted
A5 direction, the manager's "add `nw` and refit" prescription (it makes OOS
worse), the manager's "`-O2` and above" framing of the stage-7 hole (it is
flag-gated), and your own `nw` attribution, which the manager endorsed in writing.

**What I am least sure of, by name: M3's remedy.** I do not know whether p38's
shape, once its four conditions are stated honestly, still reads as a *security*
pattern or as a carefully-built demonstration — and I would rather ship it
labelled accurately as the latter than defended as the former. **The five
neighbouring spellings are the most interesting measurement in this pattern.
Lead with them.**
