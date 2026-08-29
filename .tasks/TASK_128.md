# TASK_128 — the admission bar has three limbs. One is now known unpriceable. Test the other two.

**Role: research engineer.** ⚠ **Deliverable is a MEASUREMENT and a verdict on
the BAR'S TEXT. Do not build a pattern. Do not add a catalogue row. Do not
propose one.**

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` findings 40, 41 and
42 in full** (the bar's history — it has already replaced one bar and buried
three generalisations), then **`.tasks/TASK_124_REPORT.md`'s perturbation-contrast
section in full**, then `.memory/06-catalogue.md`'s `p23` cell (⚠ **the ONLY row
ever admitted under this bar, and it claims ALL THREE limbs**).

Scratch in **`.temp/t128/`**.

⚠⚠ **A CONCURRENT TASK (`TASK_127`) IS EDITING `harness/` AND REGENERATING
`results/tables/` AND `results/gate/`. READ NOTHING OUT OF `results/` FROM THE
WORKING TREE.** ✅ **Use `git show HEAD:<path>` for every committed artefact you
need — it is read-only, it is immune to the other task's sweep, and it makes your
numbers reproducible.** ⚠ **DO NOT RUN `harness/check.py`, `build.py` or
`measure.py`. Build your probes with direct `clang`/`gcc`/`rustc` under
`.temp/t128/`.**

---

## The bar, verbatim, and the one thing that has changed under it

**Finding 37's second limb, which survived review and replaced bug-class novelty:**

> **A row is admissible whenever it brings a new MECHANISM — *(1)* a new
> **operator on the safety line**, *(2)* a new **source of the bound**, or
> *(3)* a new **reason the check is or is not elided**.**

**`TASK_124` built the control nobody had built and pointed it at limb 2:** hold
the kernel fixed, change ONLY the bound's PROVENANCE (a prior-pass count → an
input extent).

```
all six decode kernels: THE SAME INSTRUCTIONS   (0 mnemonic diffs; R4 byte-identical;
                        relocation-normalised 0 diffs, with two planted-difference
                        arms proving the normaliser still SEES a 0xC0 -> 0xE0)
every published difference moved by EXACTLY  +0.00
```

✅ **So limb 2 names a distinction this ladder cannot price.** ⚠⚠ **AND NOBODY
HAS ASKED THE OBVIOUS NEXT QUESTION, WHICH IS WHY THIS TASK EXISTS: DO LIMBS 1
AND 3 SURVIVE THE SAME CONTROL?**

## §A — ⚠⚠ FIRST, CHECK WHAT `TASK_124` ACTUALLY MEASURED. IT MAY NOT BE WHAT I JUST SAID.

⚠⚠ **"EVERY PUBLISHED DIFFERENCE" IS A PHRASE I COPIED, AND THIS PROJECT
PUBLISHES SIX COLUMNS, NOT ONE:** **assembly / instruction count / timing / proof
burden / trusted-base size / the harm matrix.**

> ⚠⚠⚠ **IF `TASK_124`'s CONTRAST MEASURED ONLY THE `Ir` AND ASSEMBLY HALF, THEN
> *"THE LADDER CANNOT PRICE LIMB 2"* IS OVERSTATED AND SO IS THIS ENTIRE TASK'S
> PREMISE — AND SAYING SO WOULD BE THE MOST VALUABLE OUTCOME AVAILABLE HERE.**

**`p42` is the standing counter-example and it is a BUILT row: its whole result
is PROOF BURDEN and HARM, and its `Ir` story is two points and no rate.** **So a
mechanism can be worth a row while moving `Ir` by nothing.**

✅ **Deliverable of §A, and do it before anything else: a table of the six
published columns × {did `TASK_124`'s contrast move it / was it measured at all /
could it have moved}.** ⚠ **Read its report and its scripts, not its summary
sentence.** ⚠ **`.temp/t124/` may still hold the artefacts; if a script is gone,
say so rather than inferring.**

## §B — the control, run on limb 3, which is the one I expect to fall

**Limb 3 is *a new REASON the check is or is not elided*.** ⚠⚠ **My guess, and
attack it: THE LADDER PRICES THE OUTCOME, NOT THE REASON. Two different reasons
that produce the same elision produce the same `Ir`, the same assembly and the
same everything — which is limb 2's disease exactly.**

**Pose it as `TASK_124` did: hold the kernel's WORK fixed and change ONLY why the
bound-check goes away.** ✅ **The tree already contains at least three distinct
elision reasons, so you do not have to invent them** — read them out of the
built patterns rather than from this list, which is from memory and may be wrong:

- ⚠ **`p03`** — the proof's own invariant, handed to LLVM, closes the gap.
- ⚠ **`p04`** — known **bits** survive a loop-carried phi where a range does not.
- ⚠ **`p13`** — a bound the optimiser can **SEE** outweighs the check that
  supplies it.
- ⚠ **`p46`** — the shipped kernel proves `i+j < 96` from its input header and
  deletes all three checks; the PROBE kernel's signature loses the range facts.

⚠ **Two reasons, one kernel, same elision → if the columns do not move, limb 3
falls with limb 2.** ⚠⚠ **BUT BE CAREFUL WHAT THAT WOULD MEAN: it would NOT mean
elision is unpriceable — the elision itself is obviously priceable and half this
project's findings rest on it. It would mean the BAR IS WRITTEN IN TERMS OF
PROVENANCE WHERE THE INSTRUMENT SEES OUTCOMES.** **State it that precisely or not
at all.**

## §C — limb 1, and the trap is that it will look like a PASS

**Limb 1 is *a new operator on the safety line*.** ⚠⚠ **It will price, trivially,
because the operator IS part of the kernel — you cannot hold the kernel fixed and
change the operator. ⚠ AND THAT IS NOT A PASS, IT IS AN UNPOSEABLE CONTROL.**

> ⚠ **A limb whose control cannot be posed is in a THIRD state, and this project
> has a name for the mistake of collapsing it into "passes": a detector that is
> not running looks exactly like a detector that found nothing.**

**So for limb 1, answer a different and answerable question:** ⚠ **does a new
operator, holding the AXIS fixed, move the columns by more than the layout floor?**
✅ **The floor is measured and it is `±4.6%` on `p06`, from the source-path-length
artefact** (`RECAP.md`'s four settled answers) — **so a limb-1 change that moves
less than the floor is not distinguishable from moving the source tree.**
⚠ **Use the built tree for this, not a new probe, and `git show HEAD:` for the
records.**

## §D — the verdict you owe, and the three shapes it can take

⚠ **State which, with the measurement, and do not reason your way to it:**

1. ⚠⚠ **§A inverts the premise** — `TASK_124` measured one column of six, limb 2
   is NOT known-unpriceable, and the bar is intact. ✅ **Then say so, close the
   task in two pages, and the standing correction is to RECAP finding 42's
   sentence, not to the bar.**
2. **Limbs 1 and 3 price and limb 2 does not** → **the bar becomes two limbs,
   and limb 2 is struck or restated.** ⚠ **If restated, the honest restatement is
   probably *"a new source of the bound THAT CHANGES THE CHECK'S COST"* — which
   ⚠⚠ **is limb 3 in different words, so say whether the bar then has TWO limbs
   or ONE.**
3. ⚠⚠ **Limbs 2 AND 3 both fail and only limb 1 prices** → **the finding is
   large: *the project has been writing its admission bar in terms of what the
   PROGRAMMER MEANS, while its instrument sees only what the MACHINE DOES.*** ⚠
   **Do not reach for this. It is the conclusion I find most interesting, which is
   exactly why it needs the most hostile evidence.**

✅ **In ALL THREE shapes, one clean negative is worth having and is cheap:
`p23` is the only row ever admitted under this bar and its cell claims ALL THREE
limbs. ⚠ Check that claim against `p23`'s own published numbers. If a row that
claims three limbs only demonstrably exhibits one, the bar's problem is not its
text.**

## §E — ⚠ what this task must NOT do

- ⚠⚠ **It must not conclude *"so build more patterns"* or *"so stop"*.**
  **THREE successive generalisations over the refusal set (findings 37, 40, 41)
  were all attacked and all died, and the standing conclusion is *keep the 22-row
  classification, publish no generalisation over it*.** **This task is about the
  BAR'S TEXT, which is a different object.**
- ⚠ **It must not re-open `CVE-2021-23017` or any refused row.**
- ⚠ **It must not propose a 27th pattern.** **If your work suggests one, write
  the suggestion in one paragraph at the end, marked as OUT OF SCOPE and
  UNPROBED, and let the manager decide.**

---

## Constraints

- **`.temp/t128/` only. No `/tmp`.** **Notes in `.temp/t128/NOTES.md` AS YOU GO.**
  **Keep the generator, delete the artefact.**
- ⚠⚠ **THE TREE IS SHARED RIGHT NOW.** **Write NOTHING outside `.temp/t128/` and
  `.tasks/TASK_128_REPORT.md`.** **Do not edit `harness/`, `patterns/`,
  `results/`, `synthesis/`, `common/`, `.memory/`, `RECAP.md` — ANY of them.**
  ✅ **Read committed state with `git show HEAD:<path>`.**
- ⚠⚠ **DO NOT RUN `harness/check.py`, `harness/build.py` or `harness/measure.py`.**
  **Direct `clang`/`gcc`/`rustc` under `.temp/t128/` only.**
- **No `git add` / `git commit`.** Read-only git is fine and you will need it.
- ⚠ **`../LearnVeri/` IS ANOTHER PROJECT'S REPOSITORY — READ ONLY.**
- **Verus via `./verus_run.py` only, single-file mode, never `--cargo`.** Do not
  bump the pin. ⚠ **Only if a limb genuinely needs a proof-burden measurement.**
- ⚠ **Every probe needs an arm that MUST FIRE.** ⚠⚠ **In THIS task the must-fire
  arm is the whole game: a contrast that moves NOTHING is the expected result on
  two of three limbs, and *"nothing moved"* is indistinguishable from *"my probe
  measures nothing"*. `TASK_124` hit this exactly and caught it with a planted
  `0xC0 → 0xE0` that its normaliser had to SEE. Plant an equivalent.**
- ⚠ **Read the failure-class list at the end of `.memory/03-measurement.md` —
  it carries no usable count; read the list.** ⚠⚠ **Entry 8: *a control that
  FIRED and whose firing did not support its printed sentence*.**
- ⚠⚠ **Probe 2 has SIX known defects and `.temp/t104/probe2.py` carries the
  sixth (it truncates at the last `ret`).** **Take the symbol extent from the ELF
  symbol table.**
- **Hand-run ASan needs `env -u LD_PRELOAD`; never truncate a sanitiser log with
  `head`.**
- ⚠ **A whole-program total is not a measurement below ~100 `Ir`**
  (`.memory/03-measurement.md`). **Kernel-exclusive, per call.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_128_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 583** (`TASK_126` carried 566 → 583;
⚠ **a rigour signal, not a ledger — do not re-add it. `TASK_127` is running
concurrently and will carry its own; the manager reconciles**). The calls I am
least sure of:

1. ⚠⚠ **That §A does not simply end the task.** **I copied *"every published
   difference"* out of `RECAP.md` without checking which columns `TASK_124`'s
   contrast could move, and `p42` — a BUILT row whose entire result is proof
   burden and harm, with two `Ir` points and no rate — is a standing
   counter-example to the premise.** **If §A shows the contrast was `Ir`-only, I
   am wrong about limb 2 and this whole file is built on a summary sentence.**
   **That is the outcome I would most like you to find if it is true.**
2. ⚠⚠ **That limb 3 falls.** **It is my guess, it is the interesting answer, and
   my guesses on this exact class have been wrong repeatedly** — most recently
   mapping a CVE onto `p12` (refuted by one census) and asserting `p16`/`p14`
   already carry a two-pass bound (false). ⚠ **`p13`'s finding — *a bound the
   optimiser can SEE outweighs the check that supplies it* — reads like a REASON
   that priced, which would refute me directly. Check it first.**
3. ⚠ **That the bar's text is worth a task at all.** ⚠ **The argument FOR: the
   bar is the only surviving instrument for admitting a row, the catalogue is
   closed, the domain is enumerated, and if the bar is broken then the project's
   stopping point rests on a criterion nobody has tested. The argument AGAINST:
   nothing is queued that would USE the bar, so a correction to it changes no
   published number.** ⚠ **If after §A you judge it a footnote, say so and close
   it in one page — that is a legitimate and cheap outcome, and `TASK_124` took
   it on a smaller question.**

Carry **583** forward, incremented by what you find.
