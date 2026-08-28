# TASK_116 — review `TASK_109` + `TASK_110`: `p42`, the ghost ledger, and a sign that already flipped once

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then **`.tasks/TASK_110_REPORT.md` in
full**, then `.tasks/TASK_109_REPORT.md`, then
`patterns/p42-goto-cleanup/{NOTES.md,spec.md,verus.rs,unsafe.rs}`, then
`RECAP.md` **finding 39** and `.memory/04-verus.md`'s **ghost-ledger** section.

Scratch in **`.temp/r116/`**.

⚠ **YOU ARE NOT THE ONLY AGENT RUNNING.** `TASK_114` (reviewing `TASK_107`, the
instrument) and `TASK_115` (probing `p26`/`p37`) are live. **See Constraints.**

---

## Why this pair, and why now

`TASK_113` triaged fifteen unreviewed tasks down to three and put this one
second, with a specific aim: ⚠ **"don't aim it at the number — `R3 − R4 =
+12.00/+11.00` reproduces exactly from the record. Aim it at the GHOST-LEDGER
R5."**

**`TASK_110` is the only unreviewed task that shipped new measured cells**, and
**`SYNTHESIS.md` §4's sharpest claim and `RECAP` finding 39 both rest on it**,
both marked PROVISIONAL for exactly that reason. ✅ **It is a strong report** —
it verified both of the manager's stop conditions, disclosed six things it did
not do, and found a ninth retraction site the review that preceded it had
missed. **Attack it where it says it is weakest.**

## §A — ⚠⚠ THE GHOST LEDGER. THIS IS THE DELIVERABLE.

`p42`'s R5 escrows a dealloc token in a tracked `Map<int, Dealloc>` and `ensures`
the domain comes back empty. **This is the encoding that replaced a published
claim (*"Verus at the pin CANNOT state leak-freedom"*) which was refuted within
hours of landing.** ⚠ **A replacement that arrived that fast, on a claim that
wrong, deserves more scrutiny than the claim it replaced.**

1. ⚠⚠ **DOES THE LEDGER PROVE LEAK-FREEDOM, OR DOES IT PROVE THAT A MAP IS
   EMPTY?** **The two come apart if anything can leave the ledger without the
   memory being freed, or free memory without going through the ledger.**
   **Attack both directions:**
   - **Can a token be removed from the map without a `dealloc`?** If yes the
     `ensures` is satisfiable by a leaking program and the proof is decorative.
   - **Can memory be freed without ever entering the map?** Then the empty
     domain says nothing about *that* allocation, and the property is
     conditional on a discipline **nothing checks**.
   ⚠ **Write the leaking program that satisfies the `ensures` if one exists.
   That is the finding; an argument that one might exist is not.**
2. ⚠⚠ **THE SURVIVING CAVEAT IS THE THREAD TO PULL: DELETING THE LEDGER'S
   LEAK-FREEDOM `ensures` STILL GIVES `18 verified, 0 errors`.** The project
   publishes this as *"the obligation is load-bearing for the PROGRAM and not for
   the COUNT"*. ⚠ **Verify that reading is right and not a symptom.** `TASK_110`
   offers `controls/ledger_leak.py` as the anti-vacuity evidence — it deletes
   each release in turn and Verus names the rejected exit. **Re-run it. Does it
   fire for the reason claimed, or would it fire for a program with no ledger at
   all?** **A control that fires is not the same as a control that fires *because
   of the thing under test*.**
3. ⚠ **`Tracked<Dealloc>` and AFFINENESS.** `TASK_110`'s negative — *"there is no
   linear must-consume tracked mode at the pin"* — rests on **(a)** none of 22
   `strings`-extracted attributes being a linear mode and **(b)**
   `grep -rn affine ~/tools/verus/vstd/` returning **0 hits**. ⚠⚠ **THAT IS AN
   ABSENCE ARGUMENT BUILT FROM A KEYWORD SEARCH, WHICH IS RECAP'S RULE 6 FAILURE
   MODE VERBATIM — *"a grep that can only find what you already thought of is not
   a census"*, which cost this project a committed false finding.** **And the
   affine question has ALREADY been retracted once on this pattern**
   (`.memory/04-verus.md`'s affine-token section). ⚠⚠ **GREP
   `~/tools/verus/vstd/std_specs/` SPECIFICALLY — a `vstd/<mod>.rs` trait
   declaration is NOT the specification, and that exact confusion has produced a
   false "no spec exists" claim TWICE.** ⚠ **Also grep the INHERENT spelling as
   well as the free one.**
4. **TCB.** The report says `_is_trusted` is `False` for all three new items and
   the tally is unchanged at **5 / 3**. ⚠ **Recount it yourself** — the reviewer
   checklist says recount the TCB, and this pattern added items to a proof whose
   whole selling point is that it cost **zero new trusted items**.

## §B — ⚠⚠ THE SIGN FLIPPED ONCE ALREADY, AND THE REPORT SAYS THE R4 ENDPOINT IS HELD BY FIAT

`R3ship − R4ship` kernel-exclusive went **`−198.00 / −8696.00` → `+12.00 /
+11.00`** when `r4_foldonly` was found. **A published comparative headline
reversed sign because somebody searched one side harder.**

⚠⚠ **AND `TASK_110` DISCLOSES THE PROBLEM ITSELF, IN ITS OWN "unsure" LIST:**
*"I cannot show that five spellings is enough on the R4 side. Four was not, and
nothing in the declaration constrains the fold shape. **The R4 endpoint is held
by fiat.**"*

**So ask the question the disclosure implies and does not answer: HAS ANYONE
SEARCHED R3 WITH THE SAME EFFORT?**

- **This project's most repeated failure is a headline wrong in the FLATTERING
  direction** — `p10`, `p27`, `p38`, `p22` (510×), and `p36` in mirror image.
- ⚠⚠ **AND `TASK_111` FOUND THE MIRROR IMAGE: the correction reflex became a
  bias the other way.** **`p42`'s current `+12/+11` is the UNFLATTERING-to-safety
  direction. That is exactly where an over-corrected project stops looking.**
- **RECAP's rule:** *a difference is only as honest as its WEAKER-searched
  endpoint. Count the levers on each side and say whether they are comparable.*

⚠ **Five R4 spellings against how many R3 spellings? If the answer is "fewer",
the number is not publishable as a comparison** and the honest form is a span or
a refusal, as `p36` and `p22` were forced to.

⚠ **Every R3 candidate must be IN CONTRACT.** `p05`'s two-task detour happened
because out-of-contract spellings were measured and reported as the pattern's
numbers, and the declaration was right both times and failed only by being
**invisible**. **Read `spec.md`'s hashed block before you measure anything.**

## §C — `p42`'s Miri evidence versus the configuration the gate now runs

`TASK_110` certifies `r4_foldonly` clean on **seeds 0–7**. ⚠⚠ **`TASK_107` then
landed `MIRI_FLAGS = ()` tree-wide, because setting `MIRIFLAGS` AT ALL — even to
the empty string — costs ≈4.6× and turned a 74 s UB-checked p42 row into a
blocked one.**

⚠ **So `p42`'s seed evidence was taken in a configuration the gate no longer
uses.** **Say whether "seeds 0–7 clean" still describes the shipped
configuration, or whether it is evidence about a regime that has since been
removed.**

⚠ **SCOPE: `TASK_114` owns the `MIRIFLAGS` decision itself and owns
`spec.md::miri.blocked_reason`. DO NOT duplicate that.** **You own exactly one
question: does `p42`'s own Miri evidence survive the change?**

## §D — clean negatives are wanted, and one is already half-established

✅ `TASK_113` verified that `R3 − R4 = +12.00/+11.00` **reproduces exactly from
the committed record**. ⚠ **So do not re-derive the number; that is done.**
**Confirm instead that the two rungs are semantically equivalent** (reviewer
checklist: *did a rung quietly change the algorithm?*) — the R4 became a
**do-while fold**, which is a control-flow change, and `identity` pins bytes, not
semantics. ⚠ **And `p42` is one of the two `PASS-WITH-BLOCKED-ROWS` patterns, so
one input is NOT Miri-checked at all.**

**Also report the adjacent item `TASK_110` disclosed and did not fix:**
`controls/sweep.py`'s docstring says *"Cells default to the six measured ones"*
while `CELLS` lists **seven**.

---

## Constraints

- **`.temp/r116/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `results/`, `synthesis/`, `harness/`,
  `pilot/` or any `patterns/*/` file. You are a reviewer.** ⚠⚠ **If you need to
  measure a spelling, COPY the rung into `.temp/r116/` and edit the copy** —
  every rung `.rs`, `c/*`, `model.py` and `inputs/gen.py` is
  **measurement-hashed**, so touching one in place stales the record.
- ⚠⚠ **DO NOT RUN `harness/check.py`, `harness/build.py` or `harness/measure.py`**
  (except `measure.py --check-stale`) — a gate run rewrites `results/gate/*.json`
  while two other agents are reading them. **Use `./verus_run.py` and direct
  `rustc`/`clang` invocations under `.temp/r116/`.**
- ⚠ **Callgrind `Ir` is deterministic and immune to the other agents' load.**
  Wall clock is not — repeat anything that decides something and say so.
- ⚠ **Every probe needs an arm that MUST FIRE.** The list at the end of
  `.memory/03-measurement.md` holds **six live entries numbered 1–7** (entry 5 is
  retracted). ⚠ **Do not quote its ordinal — doing so is itself a documented
  failure, committed five times by the manager after writing the rule against it.**
- Verus via `./verus_run.py` only, **single-file mode; never `--cargo`**. Do not
  bump the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_116_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 425** (`TASK_113` reconciled 414 → 425).
⚠ **`TASK_114` and `TASK_115` are running concurrently from 414. Report YOUR
increment as a branch delta — *"425 + N on this branch"* — and do not reconcile
with them. Reconciliation is the manager's job.**

The calls I am least sure of:

1. ⚠⚠ **That the ghost ledger is sound.** It replaced a false published claim
   within hours, it is clever, and **clever is where this project's errors
   live.** §A.1 is the concrete way to break it: **exhibit a leaking program that
   satisfies the `ensures`.** **If you cannot, say so — a serious failed attack
   on the load-bearing proof of the project's most-cited pattern is worth as much
   as a finding, and I will record it as one.**
2. ⚠ **That `TASK_113` was right to say "don't aim at the number".** It verified
   `+12.00/+11.00` against the record — **but §B is about whether that number is
   a fair COMPARISON, which is a different question from whether it reproduces,
   and the report's own disclosure says the R4 endpoint is held by fiat.**
   **If you think §B outranks §A, do §B first and say why.**
3. ⚠ **That reviewing this pair is worth a task at all.** `TASK_113` closed nine
   of the fifteen as superseded or self-checking. ⚠ **If `109`/`110` are
   self-checking too — the gate is green, the record reproduces, the corrections
   landed — SAY SO AND STOP.** That would clear `RECAP` finding 39's PROVISIONAL
   marker honestly and let this debt close.

Carry **425** forward, incremented by what you find, **as a branch delta.**
