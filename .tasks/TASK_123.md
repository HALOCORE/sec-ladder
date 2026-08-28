# TASK_123 — the enumeration nobody has run: 20 worked CVEs against the reviewed bar

**Role: research engineer.** ⚠ **But your deliverable is a TRIAGE, not a
pattern.** **Do not build anything. Do not write a catalogue row.**

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` findings 40 and 41
and the endgame box row**, then **`.tasks/TASK_120_REPORT.md` §B5**, then
**`.temp/mgr121/NOTES.md`** (the manager's independent census of the same corpus
— ⚠ **read it AFTER you have formed your own view, and say where you differ**),
then `.memory/06-catalogue.md`'s probe descriptions.

Scratch in **`.temp/t123/`**.

⚠⚠ **`TASK_122` HAS LANDED AND FINDING 41 FELL, SO THIS TASK IS NOW THE PROJECT'S
MAIN LINE, NOT AN OPTION.** **Three generalisations have been offered over the
refusal set and all three died; the standing conclusion is *keep the
classification, publish no generalisation*. ⚠⚠ THERE IS THEREFORE NO MEASURED
REASON TO STOP, and `TASK_122`'s result closes the CATALOGUE, not the DOMAIN.**

⚠⚠⚠ **AND ONE KILL CRITERION IS NOW BANNED IN THIS TASK: DO NOT REFUSE ANYTHING
ON *"the five-rung ladder has nothing to price on it"*.** **That was finding 41
and it died because it has NO CONTROL ARM — 8 of the 26 BUILT patterns publish a
ZERO on their own headline axis, and `p46` ships `0.00000` AND *"the boundary
vanished"* AS ITS PUBLISHED RESULT.** ✅ **Use the catalogue's OWN probe-3
distinction instead, which survived: *a zero with a NAMED AXIS and a MECHANISM is
a FINDING; a zero because two rungs compiled to the SAME BYTES is an ARTEFACT.***

---

## Why this task exists

⚠⚠ **THE MANAGER ASKED FOR THIS ARGUMENT AT `TASK_113` AND NEVER GOT IT** —
*argue the admission bar from the CVE DISTRIBUTION rather than from taste* —
**and `TASK_120` found that the corpus for it has been in the repo the whole
time and was cited twice in the project's entire history, never as a row source.**

`../LearnVeri/microbench/` — **18 CVE directories + 2 issue directories, all with
COMPLETED Verus proofs**, from nginx, OpenSSL, libxml2 and PHP. Its own tracker
classifies them **spatial 5 / logical 7 / temporal 8**.

⚠ **THE POINT IS NOT TO FIND A 27th PATTERN. The point is that the project has
been deciding "the domain is worked out" WITHOUT EVER ENUMERATING A DOMAIN.**
✅ **A rigorous "all 20 die, here is why" is a COMPLETE SUCCESS and is the
outcome the manager expects.**

## §A — ⚠⚠ PROBE 1 FIRST. IT IS WHAT MAKES THIS CHEAP.

**Both independent censuses predict the LOGICAL SEVEN die on probe 1** — a
decision bug (an overwritten `ret`, a counter that drifts, a policy loop starting
at index 1) **has no boundary between C, safe-naive, safe-tuned and unsafe**, so
the ladder is flat by construction. **That is `p31`'s and `p33`'s death exactly.**

⚠⚠ **THAT IS A REAL PREDICTION AND IT IS CHEAP TO FALSIFY. RUN IT, DO NOT ASSUME
IT.** **Take the two clearest — `CVE-2021-3450` and `CVE-2023-0465`, both
literally *a wrong decision* — and probe them.** ✅ **If they die, say so and
retire all seven with one measurement plus a stated argument.** ⚠ **If one
SURVIVES, that is a much more interesting result than anything else in this task
and you should stop and report it.**

## §B — the TEMPORAL eight, where BOTH censuses already agree

**All eight are fixed by a generational index, which maps onto the
`p27`/`p28`/`p29`/`p32`/`p33`/`p34` family the project has worked to
exhaustion.** ⚠⚠ **AND THE MANAGER'S NOTES CARRY THE DECISIVE CITATION, WHICH IS
`p27`'s OWN SOURCE:** a freelist push into a slab leaves the stale read **in
bounds of a live allocation** — Miri-clean, `PointsTo`-licensed — *"`p17`'s
LOGICAL class rather than this one"* (`patterns/p27-handle-table/verus.rs`, on
`rec_free` and `rec_close`; `TASK_055` §2.8 caveat 1, **which also records that
the manager offered the `(slot, gen)` formulation AT THE TIME and the engineer
rejected it for this reason**).

✅ **So this family is expected to close on a CITATION rather than a
measurement.** ⚠ **Confirm the citation is load-bearing and say so. Do not spend
a measurement here unless the citation fails.**

## §C — ⚠⚠ THE SPATIAL FIVE, AND THE ONE CANDIDATE. THIS IS THE DELIVERABLE.

**Four map onto built rows** (`CVE-2017-7529` IS `p17`; `CVE-2014-0160`,
`CVE-2014-3508`, `CVE-2017-8872` look like `p20`/`p13`/`p14`/`p16` shapes).
⚠ **The manager's census mapped all FIVE away and `TASK_120`'s mapped four —
THE DIVERGENCE IS THE WHOLE VALUE OF THIS TASK, and it is on:**

> ⚠⚠ **`CVE-2021-23017` (nginx DNS). A SIZING pass under-counts a separator that
> the WRITING pass emits, so THE BOUND COMES FROM AN EARLIER PASS OVER THE SAME
> INPUT AND THE TWO PASSES DISAGREE.**

**Against the built tree's sources of the bound — attacker length field (`p02`,
`p16`), byte-value count (`p14`), buffer extent (`p01`), carry width (`p46`), two
moving cursors (`p23`) — *a bound computed by a previous pass* is not present.**
**That is limb 2 of the reviewed admission bar verbatim: *a new SOURCE OF THE
BOUND*.**

⚠⚠⚠ **AND NOW THE STANDING RULE THAT HAS KILLED TWO MANAGER PROPOSALS: RUN THE
NOVELTY CLAIM BEFORE YOU WRITE THE ROW.** **Both axes the manager has proposed
were refused, and both died on a distinguishing justification that ONE `grep`
PLUS ONE RUN would have settled.** ✅ **The manager applied this rule to its own
third proposal in `.temp/mgr121/NOTES.md` and it KILLED the proposal for four
commands. Do the same here.** **Concretely:**

1. ⚠ **`grep` the built tree for a two-pass bound.** **Does any of the 26 already
   compute a size in one pass and write in another?** ⚠ **`p16` (TLV walk) and
   `p14` (field split) are the two most likely to already do this — CHECK THEM
   FIRST, and if either does, the candidate is dead and you have saved a task.**
2. ✅ **Then probe 1**: do the rungs actually separate on it, or is the
   two-pass disagreement a LOGICAL bug wearing a spatial coat? ⚠ **The corpus's
   own description says the off-by-one corrupts an ADJACENT FIELD, which sounds
   spatial — but `p04` is the precedent for *"every index still `< CAP`, no OOB
   access, and both guards are invisible to a memory-safety proof"*.**
3. ⚠ **Only if 1 and 2 both survive:** state it as a CANDIDATE with its novelty
   claim MEASURED, and stop. **Do not write a catalogue row; the manager will.**

## §D — the deliverable

**A table: 20 rows × {category, mechanism in one line, mapped-to built row or
NONE, which limb of the bar it would meet, verdict, evidence}.** ⚠ **Every
verdict cites a `grep`, a run, or a load-bearing citation — not a reading.**

⚠⚠ **AND THE HONEST HEADLINE, WHICHEVER IT IS:** *"the domain really does look
worked out, and here is the enumeration that shows it"* **or** *"N candidates
survive"*. ⚠ **Do not manufacture a candidate to justify the task** — and
⚠⚠ **do not suppress one to agree with a finding that no longer exists. Finding
41 is DEAD; there is nothing left to agree with.**

---

## Constraints

- **`.temp/t123/` only. No `/tmp`.** **Notes in `.temp/t123/NOTES.md` AS YOU GO.**
  Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **`../LearnVeri/` IS ANOTHER PROJECT'S REPOSITORY — READ ONLY. Do not edit,
  build into, or otherwise touch anything under it.** Copy what you need into
  `.temp/t123/`.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `results/` or any `patterns/*/` file.**
  **You are producing a triage, not a change.**
- ⚠⚠ **DO NOT RUN `harness/check.py`, `build.py` or `measure.py`** unless the
  manager says the tree is free. **Build probes with direct `clang`/`gcc`/`rustc`
  under `.temp/t123/`.**
- ⚠ **Every probe needs an arm that MUST FIRE.** **The list at the end of `.memory/03-measurement.md` is the catalogue of
  named failure classes — ⚠ **READ THE LIST; IT CARRIES NO USABLE COUNT.**
  ⚠⚠ **Its own entry says a count is a cached derivation that goes stale like
  any other cached number, and that count has now rotted THREE times — most
  recently because this manager added an entry after writing the old figure
  into three task files. If you need a number, derive it where you write it.**
- Verus via `./verus_run.py` only, **single-file mode, never `--cargo`.** Do not
  bump the pin. ⚠ **You probably need no Verus at all — the corpus ships proofs
  and you are triaging, not proving.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_123_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 502** (⚠ **a rigour signal, not a ledger —
do not re-add it**). The calls I am least sure of:

1. ⚠⚠ **That this corpus is the right domain at all.** **It is 20 CVEs chosen by
   ANOTHER project for ITS purposes — provable security invariants — which is a
   selection this benchmark did not make and might not want.** ⚠ **If your read
   is that a CVE corpus is the wrong instrument for a PERFORMANCE benchmark
   because CVEs select for exploitability rather than for idiom frequency, SAY
   SO — that is a serious objection and it would mean the enumeration should be
   over C IDIOMS, not over bugs.**
2. ⚠ **That `CVE-2021-23017` is a real candidate.** **Two independent censuses
   disagreed about it and I am the one who mapped it away, so I am probably the
   one who is wrong — but "two readers disagreed" is not evidence FOR it either.**
   **Kill it if `grep` kills it.**
3. ⚠⚠ **That a "0 candidates" outcome would be believed.** **This project has
   refused nine consecutive proposals. There is a real risk that refusal has
   become the reflex and that a tenth refusal is the path of least resistance.**
   ⚠ **If you find yourself reaching for a refusal reason, check it against
   `p28`'s precedent — RIGHT VERDICT, WRONG REASON — and against `TASK_120`'s
   finding that TWO OF THREE spot-checked refusal reasons were broken.**

Carry **502** forward, incremented by what you find.
