# TASK_072_REVIEW — p36, where the bug class is admittedly the tree's twelfth

**Role:** research reviewer. **Adversarial by design.** You do **not** fix; you
report. A review that says "looks good" without having tried to break something
is a failed review.

**Read first:** `.tasks/PROTOCOL.md` (roles, reviewer checklist, severity), then
`.tasks/TASK_072.md`, then **`patterns/p36-vtable-dispatch/NOTES.md` in full**,
then `.memory/04-verus.md`, `.memory/03-measurement.md` (**the two `Ir`
conventions, the INLINE-MODE rule, the DOMAIN rule, the RESIDUE-CLASS rule**) and
`.memory/01-ladder.md` — **findings 1 (a proof costs zero instructions), 14 (the
prover bounds the unsafe class) and 15 (p07's `Ir`-vs-`ns` divergence)**. All
three are load-bearing here and p36 claims to extend or sharpen each.

p36 is **gate-green**: `PASS`, **0 failures**, complete run, `forbidden_hits`
0/11, `required_pins_nothing` 0, **44 records 0 STALE**, committed at `207a83e`.
**PROTOCOL rule 9 holds everything out of `.memory/` until you land.**

⚠ **The engineer refuted the manager twice and changed a rung on its own
measurement.** Those are dead — do not re-run them. **Attack what replaced
them.**

- **§0a**: the task's design default (*"all rungs dispatch through
  `[fn(u64) -> u64; N]`"*) is **unbuildable** — Verus at the pin errors on the
  **declaration**, not the call. Fourteen probes; the route that works is
  `const TABLE: [&'static dyn Op; NOPS]`.
- **§0d**: the task's *"no pattern has an indirect call at all"* is **false as
  written** — 1297 `call *(%rip)` GOT-indirect calls exist across 534 kernels.
  It is true only of **computed-target** calls, 0 of 534.
- **§8b**: the engineer **changed which R4 ships** after searching the R4 side.

## A0 — the bug class is the tree's TWELFTH `index >= len`. What is left?

`NOTES.md` concedes this. The task file asked whether p36 is *"a bounds pattern
in a costume"* and the answer to the **bug-class** half is yes. **So the pattern
stands or falls on four replacement claims, and your first job is to say which
survive.** Rank them yourself; do not accept the engineer's ranking.

**(a) The catcher names the ARRAY READ, never the CALL.** Stage 7 fires
`index 8 out of bounds` (UBSan) and `global-buffer-overflow ... after global
variable 'TABLE'` (ASan) — both on the load. `-fsanitize=function` is **absent
in gcc 13.3**, present in clang, and **defeated here** (`SEGV on unknown address
0xfffffffffffffff9` — it dereferences the signature word). Only
`-fsanitize=cfi-icall` names the transfer, at `9.00000·nrw − 2` Ir.

> **Verify all four legs, and then ask the question the write-up may not have
> asked: is this a finding about p36, or about the CHECKER SET?** If the latter,
> it is worth more and belongs stated that way. **And check the converse**: is
> there any input on which the array read is in bounds and the *call* is still
> wrong? If not, say so — that is what makes the CFI column honest rather than
> decorative.

**(b) `3.00000` Ir per dispatch is what the PROVER costs, claimed as finding
14's "sixth and sharpest" instance.** `r_fnptr` = `10·nrw + 31`, shipped `dyn`
rung = `13·nrw + 31` — same intercept, and `r_fnptr` is inadmissible
(`is not supported` ×3).

> ✅ **This is the strongest structural claim in the delivery and it is the one
> to test hardest**, because finding 14's prior instances are about *spellings*
> and this one claims a **mechanism**. **Is `r_fnptr` genuinely the same
> program otherwise** — same op set, same fold, same header decode — or does it
> differ somewhere that also costs 3? Build the difference yourself.
> ⚠ **And check the intercept claim**: "same intercept" is doing real work. If
> the intercepts differed, `3.00000/dispatch` would be a fitted artefact.

**(c) `Ir` exactly constant, wall clock 3.17×.** ⚠⚠ **THIS IS THE ATTACK THE
MANAGER MOST WANTS RUN, and it is a novelty question, not a correctness one.**
`.memory/01-ladder.md` **finding 15 already carries a workload-driven
`Ir`-vs-`ns` divergence on p07**: *"changing only the workload makes the same
binary execute +7.84% more instructions in 71.75% less time."* Same shape — one
binary, vary the input, `ns` and `Ir` disagree.

> **So: is p36's headline NEW, or is it p07's result in a new costume?** The
> candidate differences, and each needs checking rather than asserting:
> p07's `Ir` **moves** (+7.84%) where p36's is claimed **exactly constant to the
> instruction in all eight cells**; p07's mechanism is a **conditional** branch
> and p36's would be an **indirect** one. **If "exactly constant" is the novel
> part, verify it is exact** — re-measure at least two cells independently and
> check `sweep-t*` really holds everything but target count fixed.
> ⚠ **If p36's headline is p07's finding restated, say so plainly.** That is a
> legitimate review outcome and this project has taken worse news.

**(d) A `spec fn` declared in a trait occupies a vtable slot.** With `spec_apply`
before `apply`, R5's dispatch is `call *0x20(%rcx)` where R4's is `*0x18(%rcx)`
— *"the first time in this project that a ghost declaration moved a byte of the
object code"*.

> ⚠ **This touches finding 1, the project's number-one result** (*"a Verus proof
> costs exactly zero instructions; the proven binary is byte-identical to the
> unproven one"*). The engineer says finding 1 survives because it claims zero
> **instructions**. **Test that reading.** Reproduce the control `v_specfirst`,
> confirm the instruction and byte counts really are equal while the offset
> differs, and then decide: **does finding 1 need a scope clause, or is
> declaration order simply a hazard to document?** ⚠ **A wrong answer here
> propagates further than anything else in this pattern**, because finding 1 is
> quoted in the abstract of every write-up.

## A1 — the wall-clock half has NO MECHANISM, and the tool that should give one says the opposite

`NOTES.md` §7 reports **3.17× (Rust) / 3.16× (C)** against a **4.19%** noise
floor on byte-identical copies, and then reports a **clean negative**: callgrind
`--branch-sim`'s indirect half does **not** order wall clock — `mixrun001` at
**99.87%** simulated mispredict is among the *fastest*, `mixrand` at 86.6% the
slowest.

> **PROTOCOL rule 12: ask the review for the MECHANISM, not the number.** A 3.17×
> effect whose only instrument disagrees with it is *"it vanished"* pointing the
> other way.
> - **Is `Bim` wrong, or is the effect not branch prediction?** `.memory/` should
>   end up saying which. Callgrind's indirect predictor is **last-value**; a real
>   BTB is not. **Can you separate the two hypotheses without hardware counters?**
>   `sweep-t*` (vary distinct targets, hold `Ir` fixed) is evidence for a
>   target-buffer effect — **is the obvious alternative excluded?** Eight targets
>   occupy more I-cache/DSB footprint than one, and that is a different mechanism
>   with the same sign. ⚠ **The project has been here before**: finding 16's
>   layout modes are `win32`/`jcc32`, both **computable from the disassembly with
>   zero fitted parameters**. Try that route.
> - ⚠ **`sweep-mix*`'s middle is non-monotone and reproducible** (`run016` slower
>   than `run032`), **unattributed**. Is it real, and does it survive the
>   alternating protocol? Finding 16's methodological result is *interleave by
>   CELL, never by block* — **check which protocol §7 used**, because a blocked
>   round-robin manufactured every reading once attributed to p05's layout.
> - **No layout population was run** — the engineer says so. Their argument is
>   that one binary on several inputs holds layout constant **by construction**,
>   which would make the 4.19% identical-copy floor the *right* control and
>   stronger than a population. **Is that argument sound?** If it is, say so
>   loudly — it would be a reusable result. If it is not, the headline needs a
>   population and the delivery does not have one.
> - ⚠ **`sweep-mix*`'s six windows share one opcode sequence while `sweep-t*`'s
>   do not** — disclosed, and said to make the mix band **understate** the effect.
>   **Check the direction of that understatement is what they claim.**

## A2 — the R4 change flatters UNSAFE, and the R3 side may not have been searched as hard

**§8b, and it is disclosed honestly**: the R2-shaped unsafe rung — *what every
other pattern in this tree ships as its R4* — **verifies** (`12 verified, 0
errors`, no new trusted item) and is **1022 / 8190 dearer**. Shipping it would
have published *"safe Rust beats unsafe by 1007 / 8175"*. So the engineer
shipped R3's loop structure minus the checks, giving `R3 − R4 = +15.00 flat`,
and published both numbers plus the span `1695…2717 / 13343…21533`.

> ✅ **This is the trap being caught before publication for the second pattern
> running, and it is the behaviour the project wants.** ⚠ **Now apply the
> direction test to the choice itself.** The R4 side was **minimised after
> measuring**; the chosen R4 makes the published `R3 − R4` **positive** — i.e.
> it flatters the *"safety costs something"* reading.
> **So: was the R3 side searched as hard as the R4 side?** If R4 was minimised
> and R3 was not, `+15.00 flat` is a **biased difference**, and the bias points
> the way p36's story wants. **Count the levers pulled on each side and say
> whether they are comparable.** p47's standard is six levers on the R4 side,
> each measured *and* run through Verus.
> **And check the span is complete**: ⚠ **`r4_reslice`'s Verus twin was NOT
> built** (needs `vstd::slice::slice_subrange`), so its number 1700/13348 is
> reported and **not counted**. **Build the twin, or establish it cannot be
> built at the pin with the error text.** An uncounted cheaper R4 is exactly the
> shape of the five prior misses.

## A3 — five contract moves, and an `identity` level no other pattern uses

- **`contract_sha256` moved FIVE times**: first written `f8d00370…` → shipped
  `ffb7fc4a…`, each disclosed with a direction test in `NOTES.md` §11a.
  ⚠ **Verify every one.** The `git show HEAD:` diff is **vacuous on a new
  pattern** (working tree vs HEAD, not first-written vs shipped) — **the
  recorded first hash is the only evidence, so check §11a records it as written
  BEFORE any cell was built and that each move's direction test is honest.** A
  false disclosure is worse than the stale thing it describes: it removes the
  check it was meant to enable.
- **`identity` is `norel` at O3 — the first of 22 patterns**; every other pins
  `exact`. Claimed cause: exactly one instruction of sixty differs, a
  `lea (%rip)` to `TABLE`, and `md5_fn_norel` is equal.
  > ⚠ **`norel` is a WEAKER pin, and the pattern that needed it also wrote the
  > justification for it.** **Try to construct an R5 that differs from R4 in a
  > way `norel` accepts and `exact` would have caught, and see whether the gate
  > still passes.** If you can, that is a blocker about the pin, not about p36.
  > If you cannot, it is a clean negative worth recording. **Also check whether
  > any OTHER pattern could have used `norel` to hide drift** — the answer scopes
  > how much this matters.

## Also in scope

- **§9b — eight `impl Op for OpN` blocks verify (19/0) and
  `vparse.duplicate_names` REFUSES them**, so the shipped shape is one generic
  `impl<const K: u8> Op for OpTag<K>` with 8 monomorphisations. **Is the gate's
  refusal right, or is it a gate defect that forced a spelling?** Say which; if
  it is a defect, scope it (it would be a `harness/` item, reported not fixed).
- **Mutants: 4, all fail, `--multiple-errors 20`.** ⚠ **m1 fails on TWO errors
  including `precondition not satisfied: i < NOPS` at the dispatch, so it does
  not isolate memory safety** — `NOTES.md` says so. **Confirm the honesty and
  check m4 (the twin-only mutant, `12 verified 0 errors` shipped vs `precondition
  not met` under `--cfg slb_twin`) is genuinely twin-only.** Is `m2` a live
  mutant or a no-op?
- **`required_absent 2`, both said to be genuine** — recount, and check the two
  are not the *"backticks the replacement"* or substring false-positive shapes.
- **The C-vs-Rust comparison now carries a MECHANISM difference** (one dependent
  load vs two). **Check no figure in `NOTES.md` or `README.md` quotes a
  C-vs-Rust difference without naming it.** `.memory/03-measurement.md` requires
  a clang column for every C-vs-Rust claim; this needs one more clause.
- **`r_match` and `c_switch` are DEARER than the table** — the opposite of the
  expected direction — and `r_match`'s `Ir` is **non-integer**. Verify both, and
  verify the claim that a non-integer `Ir` would have destroyed the `sweep-t*`
  control.
- **The `Ir` floor, `min_ir_per_work`, and the `work_per_call` note** (`spec.md`
  says the estimate over-counts on `degenerate.bin`'s fourth window). Check the
  default 0.25 floor is not vacuous here.
- **Inline mode**: is every published figure labelled? Cross-pattern `Ir` is
  `isolated`-only.
- ⚠ **The engineer ran an out-of-scope MSan probe for p48** at
  `.temp/p48probe/`, concluding **MSan exists and works** on this box. **Spot-check
  it** — the manager intends to land it against p48's UNVERIFIED item, and it was
  not part of this task.

## Clean negatives are wanted

PROTOCOL rule 6. Recent reviews returned 28, 32, 35, 38 and **54** named
attacks. **List every attack you ran with its outcome.** A named attack that did
not land stops the next agent re-running it.

## Constraints

No root; no `/tmp` (scratch **`.temp/p36rev/`** — your own subdirectory; read
`.temp/p36/` but do not modify it); **no `git add`/`git commit`**; do not edit
`pilot/`, `.memory/`, `harness/`, `common/`, or **any** file under `patterns/`.
You may re-run `harness/check.py p36`; **a gate run rewrites
`results/gate/p36-vtable-dispatch.json`, so restore it with `git checkout --`
and say that you did.** ⚠ p36's unguarded rung **SIGSEGVs by design** — run it
under `timeout <N>`, never in the background, never `pkill`. Verus only via
`./verus_run.py`; `~/tools/verus/vstd/` for vstd source — **never**
`../LearnVeri/_VERUS_DOC_/vstd/`, which is an older snapshot. clang
`~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — **none but gcc on
PATH**. **You are the only agent running.**

**Write `.tasks/TASK_072_REVIEW_REPORT.md` before you finish** (rule 10), then
return the same content in the report format. Rank findings `blocker` · `major` ·
`minor`, with **file:function** (⚠ **not `file:line`** — the line-as-a-hint
convention was retracted at TASK_071 after every hint rotted inside one session)
and a concrete failure scenario. **Do not pad.**

**If a premise here is wrong, say so with the measurement.** ⚠ **Running count
158** — 155, plus the three above: the `[fn]` design default being unbuildable at
the pin, *"no pattern has an indirect call at all"* being false as literally
written, and the R4 default being refused on a measurement that would otherwise
have published a sixth flattering-direction headline.

**What I am least sure of, by name: A0(c) and A2, and they are connected.**
p36's strongest half is a wall-clock finding whose mechanism its own instrument
contradicts, and whose *shape* p07 may already own. Its structural half rests on
an `R3 − R4` whose R4 endpoint was minimised after measuring while the R3
endpoint may not have been. **Both could be right. p36 could also be the tree's
twelfth bounds pattern with two numbers that do not mean what they say.** Settle
them before anything reaches `.memory/`.
