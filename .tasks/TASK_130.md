# TASK_130 — REVIEW of `TASK_128` and of finding 44, including the manager's own refutation of it

**Role: research reviewer.** ⚠ **Your job is to ATTACK, and there are TWO
targets, not one: the engineer's headline AND the manager's refutation of it.
Both are in `RECAP.md` finding 44 right now, and finding 44 is UNREVIEWED.**

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` finding 44 IN
FULL**, then **`.tasks/TASK_128_REPORT.md` IN FULL**, then `.tasks/TASK_128.md`
(what was asked), then **`.tasks/TASK_124_REPORT.md` §B2** (the *"Verus. NOT
SPENT, deliberately"* section that started all of this).

Scratch in **`.temp/t130/`**. ✅ **`TASK_128`'s artefacts are in `.temp/t128/`
and `BUILD.sh` regenerates all of them; the manager re-ran it at `rc=0`.**

⚠⚠ **TWO OTHER TASKS ARE LIVE IN THIS TREE (`TASK_127` owns `harness/` and
`results/`; `TASK_129` is an external-corpus census). YOU ARE READ-ONLY ON THE
TREE: write NOTHING outside `.temp/t130/` and `.tasks/TASK_130_REPORT.md`.**
⚠ **DO NOT RUN `harness/check.py`, `build.py`, `measure.py` or `report.py`.**
✅ **`git show HEAD:<path>` for every committed artefact. Verus via
`./verus_run.py` single-file mode is fine and you will need it.**

---

## §A — ⚠⚠⚠ THE CRUX, AND IT IS A DISAGREEMENT BETWEEN THE ENGINEER AND THE MANAGER

**The engineer held a kernel byte-identical (243 B, one sha256, both arms) and
changed only the bound's provenance — input extent → prior-pass count:**

```
armE      3 verified    bound = input extent
armP      5 verified    bound = PRIOR-PASS COUNT              <- the mechanism
_calib2   5 verified    bound = input extent + an UNRELATED proved counting loop
```

**The engineer read `armE → armP` as *the ladder CAN price limb 2, on the
published `obligations` column*, and read `_calib2` as CALIBRATION (decomposing
the `+2` into *1 function + 1 loop*).**

⚠⚠ **The manager re-ran the arms and read `_calib2` as a REFUTATION: `armP` and
`_calib2` are indistinguishable on `obligations`, one carrying the mechanism and
one carrying dead code, so the column moves with ADDED PROVED CODE and not with
PROVENANCE.**

> ⚠⚠⚠ **DECIDE IT, WITH EVIDENCE. AND ⚠ THE MANAGER'S OBJECTION IS THE
> MANAGER'S, SO RULE 3 SAYS THE MANAGER CANNOT CLEAR IT — THIS IS THE ONE CALL
> IN THIS TASK THAT MUST NOT BE DEFERRED BACK.**

**The defence of the engineer's reading, at full strength, so you do not have to
reconstruct it:**

> *"`_calib2`'s loop is DEAD CODE no real pattern would contain. A prior-pass
> bound INHERENTLY costs one proved pass — you cannot equalise the code without
> deleting the mechanism. This project accepts `Ir` as PRICING a bounds check
> even though an unrelated `add` also costs instructions. By that same standard,
> `obligations` prices limb 2, and the manager is applying a stricter test to
> the proof column than it has ever applied to the instruction column."*

⚠ **The crux in one sentence: does *pricing a mechanism* require distinguishing
it from ANY change of the same size, or only from ITS OWN ABSENCE?** ⚠⚠ **Do not
answer it by argument. Find the case that decides it** — ✅ **and the obvious
place to look is whether this project has EVER accepted an `Ir` figure whose
control was *"the same work spelled a different way"* rather than *"the work
removed"*. `p23`'s `k_u5` (tautological conjunct, same object code, `150.00
Ir`/call cheaper) and `p46`'s rolled-vs-rolled control look like precedents in
opposite directions. **Read them before deciding.**

## §B — the OPEN question finding 44 names, and it is cheap and it may settle §A

> **Does ANY published column distinguish `armP` from `_calib2`?**

**Six columns: assembly, `Ir`, timing, proof burden, trusted base, harm matrix.**
✅ **The arms already exist and `BUILD.sh` rebuilds them.** ⚠ **`ghost_clauses_total`
and `proof_fn` are already computed by the engineer's `count_burden.py` — check
whether they separate where `verified` does not.** ⚠⚠ **A YES here rescues the
engineer's headline in a stronger form than it was written. A NO strengthens the
manager's. Either way it is one run.**

## §C — attack limb 1's census, which is the ONLY surviving positive result

```
rows 100   |dIr| > 4.6% floor: 35   wall: 26   patterns 25   12 with any row above
```

⚠⚠ **THE LOAD-BEARING PREMISE IS *"the hardened-C twin IS the plain rung plus
the safety-line operator and nothing else"*, AND NOBODY HAS CHECKED IT.**
⚠ **If `R1h` differs from `R1` by anything besides the safety-line operator — a
different flag set, a different libc entry point, a stack-protector's prologue —
then this is not limb 1's control and the 35 is measuring something else.**
✅ **`harness/build.py` names the R1h flags; read them, do not run it.**
⚠ **And check the ±4.6% floor's provenance: it is `p06`'s LAYOUT floor from a
source-path-length artefact. Is it the right floor for a C-to-C comparison at
all? Say so either way.**

## §D — the clean negative, and verify it because it is the sharpest thing here

**`p23` — the only row ever admitted under this bar — is reported as CLAIMING all
three limbs and EXHIBITING at most one** (limb 1: `−1.39 / −3.66 / +0.13 /
−1.60 %`, all below floor, sign flips; limb 2: `obligations 16`, mid-tree,
`proof_fn 0`; limb 3: its own `NOTES` says the cause is OPEN).

⚠ **Verify all three cells from the committed record.** ⚠⚠ **AND THEN ASK THE
QUESTION THE ENGINEER DID NOT: is *"exhibits a limb"* even well defined? A row
can bring a new mechanism and still land inside the floor. If *exhibit* has no
operational definition, this clean negative is rhetoric — ✅ and saying so would
be a better result than confirming it.**

## §E — the instruments, and there are three self-caught defects to re-check

**The engineer disclosed three of its own:** a callgrind `fn=`/`cfn=`
name-compression **silent zero**; an LLVM-hoisted `calls=1` printing
`0.42 Ir`/call; and a `git ls-tree` pathspec resolving against the wrong
directory, printing **`rows: 0`** — *a detector that was not running.*
✅ **Self-disclosure is the good outcome.** ⚠⚠ **BUT THE THIRD ONE IS THE LIMB-1
CENSUS'S OWN READER, so re-run §C's row count from your OWN independent code and
say whether you get 100 rows and 35.**

⚠ **Read the failure-class list at the end of `.memory/03-measurement.md` — it
carries no usable count; read the list.** ⚠⚠ **Entry 8 is this task's shape
exactly: a control that FIRED and whose firing did not support its printed
sentence. `_calib2` fired. The dispute is about what its firing supports.**

## §F — ⚠ what the review must NOT do

- ⚠⚠ **Do not re-open `CVE-2021-23017`.** **It is refused on grounds INDEPENDENT
  of limb 2 — the port-property split, the three-R3-answers control, and
  `R4 = Miri UB` not being an admissible R4. Finding 44 touches only the limb-2
  ground.**
- ⚠ **Do not propose a 27th pattern.**
- ⚠ **Do not conclude "build more" or "stop".** **Three generalisations over the
  refusal set have died; the standing conclusion is to publish none.**
- ⚠⚠ **Do not edit `RECAP.md`.** **Say what should change and the manager
  applies it.**

---

## Constraints

- **`.temp/t130/` only. No `/tmp`.** **Notes in `.temp/t130/NOTES.md` AS YOU GO.**
  **Keep the generator, delete the artefact.**
- ⚠⚠ **Write NOTHING outside `.temp/t130/` and `.tasks/TASK_130_REPORT.md`.**
  **`.memory/`, `RECAP.md`, `results/SYNTHESIS.md` are manager-only;
  `results/synthesis.md` (lower case) is GENERATED and never hand-edited.**
  ⚠ **`.temp/t128/` is another task's evidence: you may RUN `BUILD.sh` and READ
  everything, but do not edit its sources — copy into `.temp/t130/` first.**
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠⚠ **DO NOT RUN `harness/check.py`, `build.py`, `measure.py` or `report.py`.**
- **Verus via `./verus_run.py` only, single-file mode, never `--cargo`.** Do not
  bump the pin.
- ⚠ **A whole-program total is not a measurement below ~100 `Ir`.**
  **Kernel-exclusive, per call.** ⚠⚠ **Probe 2 has SIX known defects; take the
  symbol extent from the ELF symbol table.**
- **Hand-run ASan needs `env -u LD_PRELOAD`; never truncate a sanitiser log with
  `head`.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_130_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 594** (`TASK_128` carried 583 → 594;
⚠ **a rigour signal, not a ledger — do not re-add it. `TASK_127` and `TASK_129`
are carrying it concurrently and the manager reconciles**). The calls I am least
sure of:

1. ⚠⚠⚠ **That `_calib2` refutes the headline.** **It is the manager's own
   reading, produced by re-running the engineer's arms, and the defence in §A is
   strong enough that the manager is not confident.** ⚠ **If the engineer's
   reading is right, SAY SO PLAINLY — the manager has been wrong on this class of
   call repeatedly and the correction is worth more than the finding.**
2. ⚠⚠ **That finding 44 is worth keeping at all rather than collapsing back into
   a one-line correction of finding 42.** ⚠ **What is CERTAIN is small:
   `TASK_124` measured 2 of 6 columns and said so itself. Everything built on top
   of that is disputed.** **If your read is *"correct finding 42's sentence,
   delete finding 44"*, say it — that is a legitimate and cheap outcome.**
3. ⚠ **That limb 1's 35-of-100 is a limb-1 result at all** (§C). **If `R1h` is
   not *plain rung plus the operator*, the ONLY surviving positive result in
   finding 44 goes too, and the honest state of the bar becomes *no limb has a
   measurement behind it* — which would be a large and publishable finding, and
   ⚠ is exactly the conclusion the manager most wants to reach, so give it the
   most hostile evidence you can.**

Carry **594** forward, incremented by what you find.
