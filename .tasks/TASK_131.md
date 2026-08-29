# TASK_131 — REVIEW of `TASK_129` and finding 45: is `ptr_offset = 0` a gap, an artefact, or a property of the LADDER?

**Role: research reviewer.** ⚠ **ATTACK. The headline is landed in `RECAP.md`
finding 45 and in `results/SYNTHESIS.md` §7, both marked UNREVIEWED, and the
manager raised an objection to it AFTER landing it — that objection is yours to
settle, not the manager's (rule 3).**

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` finding 45 IN
FULL**, then **`.tasks/TASK_129_REPORT.md` IN FULL**, then `.tasks/TASK_129.md`
(what was asked), then **`RECAP.md` finding 42's coda** (the retraction that
made this census possible, and the manager's `-maxdepth 6`).

Scratch in **`.temp/t131/`**. ✅ **`TASK_129`'s census is in `.temp/t129/`;
`REBUILD.sh` regenerates it in ~1 min and the manager re-ran `agree.py`.**

⚠⚠ **`TASK_127` IS STILL LIVE AND OWNS `harness/` AND `results/`. YOU ARE
READ-ONLY ON THE TREE: write NOTHING outside `.temp/t131/` and
`.tasks/TASK_131_REPORT.md`. Do NOT run `check.py`, `build.py`, `measure.py` or
`report.py`.** ✅ **`git show HEAD:<path>` for committed artefacts.**
⚠ **The three C corpora are OTHER PROJECTS' TREES — READ ONLY.**

---

## §A — ⚠⚠⚠ THE HEADLINE, AND THE OBJECTION THE ENGINEER APPLIED TO ONE NUMBER AND NOT THE OTHER

**The census reports `ptr_offset` — a pointer cursor walking memory — at
`0 of 255` in the built tree, against `5.7–8.8%` of the corpora and a **top-3
operator in every one of the 22 programs**. Confirmed independently of the
classifier: a raw regex returns `0` over all 26 kernels and `845` over PHP.**

✅ **The engineer DECLINED to publish a different ladder-vs-corpus comparison for
exactly the right reason:** *"the ladder reads `param 51.4%` because all 255
sites are leaf kernels taking `(buf, len)` from a shared driver — a HARNESS
ARTEFACT, not a mechanism gap."*

> ⚠⚠⚠ **SO WHY IS `ptr_offset = 0` NOT THE SAME ARTEFACT? ✅ MANAGER-VERIFIED:
> every C rung has the signature `kernel(const T *v, size_t off, size_t len)` —
> the driver hands a POINTER, AN OFFSET AND AN EXPLICIT LENGTH. A kernel handed
> an explicit length has little reason to walk.** **THE ENGINEER APPLIED ITS OWN
> ARTEFACT TEST TO ONE NUMBER AND NOT TO THE OTHER, AND THE MANAGER LANDED THE
> FINDING BEFORE NOTICING.**

⚠ **It is NOT obviously fatal, and do not treat it as a foregone conclusion:**
`const T *p = v + off; while (p < v + off + len) { ... *p++ ... }` **is perfectly
natural C under that very signature**, and plenty of real C with an explicit
length still walks with a cursor. ✅ **Test it: how many of the corpora's
`ptr_offset` sites sit in a function that ALSO receives an explicit length?
If most do, the harness does not force indexing and the zero is real.**

## §B — ⚠⚠ THE THIRD READING, WHICH WOULD BE THE BEST RESULT AND WHICH NOBODY HAS TESTED

> **That the zero is forced by THE LADDER'S OWN COMPARABILITY REQUIREMENT.**

**Safe Rust cannot express a raw pointer cursor at all.** ⚠ **So a pattern whose
C rung walked would have no R2 — and the `identity` pin plus each pattern's
`required` idiom would then be pinning every C rung to an INDEXED spelling to
keep the six rungs comparable.**

⚠⚠⚠ **IF THAT IS THE MECHANISM, THE FINDING IS NOT *"the corpus has a gap"* BUT
*"THE FIVE-RUNG LADDER STRUCTURALLY CANNOT HOST C's SECOND-MOST-COMMON MEMORY
OPERATOR, BECAUSE RUNG 2 CANNOT EXPRESS IT"* — a statement about the INSTRUMENT,
and a far better result than a coverage gap.**

**How to settle it, and it is all reading plus one grep:**

1. ⚠ **Do any `spec.md` `slb-contract` blocks FORBID pointer arithmetic in the C
   rung, or REQUIRE an indexed spelling?** **Read the `idiom` blocks — 26 of
   them — and count.** ⚠⚠ **`p08` is the pattern whose whole point is *"the bug
   safe Rust CANNOT EXPRESS"*, so if any row was going to walk, it was that one.
   Look at it first and say what it does.**
2. ⚠ **Is a pointer-cursor C rung actually INADMISSIBLE, or merely unused?**
   **`.memory/01-ladder.md` defines the rungs. Does anything there require the C
   rung to mirror R2's shape?** **Quote it or report that nothing does.**
3. ✅ **The decisive cheap experiment: write a pointer-cursor C kernel for an
   EXISTING pattern's contract in `.temp/t131/`, and check whether it satisfies
   that pattern's `required`/`forbidden` spellings.** ⚠ **You may NOT run
   `check.py` — but `check.py::spelling_matches` is importable and `TASK_101`
   used it exactly this way. ⚠ Verify that function name before citing it;
   `TASK_121` found a task file citing `_check_controls_json`, which resolves
   nowhere.**

⚠ **Three outcomes and all are publishable: the zero is a real corpus gap; the
zero is a harness artefact of the `(ptr, off, len)` signature; the zero is forced
by rung 2's expressiveness. ⚠⚠ SAY WHICH, WITH THE MEASUREMENT. Mixed answers
are allowed — say what fraction each accounts for.**

## §C — attack the REPLICATION arm, which is what makes the census mean anything

**Reported: `index` tops 21 of 22 programs, `const` tops 19 of 22, shares swing
42–50 points, second place flips between four categories → *the ordinal top is a
property of C, the distribution is a property of the program.***

⚠⚠ **THE OBVIOUS OBJECTION, AND THE MANAGER WANTS IT MEASURED RATHER THAN
ARGUED: `n = 22 PROGRAMS` IS NOT `n = 22 INDEPENDENT SAMPLES`. Twenty-one of
them are GNU packages in one house style, sharing gnulib, sharing a coding
standard, and several sharing authors. PHP is the ONE non-GNU member.**
✅ **So test it: does PHP sit OUTSIDE the GNU packages' spread on the fields that
carry the headline, or inside it?** ⚠ **If PHP is an outlier, the "property of C"
claim rests on 21 correlated samples plus one disagreeing one, and should be
restated. If PHP sits inside, the claim is stronger than the engineer argued.**

⚠ **And check the shared-source contamination directly: gnulib files appear in
coreutils AND in the GNU packages. Deduplication was BY CONTENT HASH — does that
actually remove them, or do version skews leave near-duplicates counted twice?**

## §D — the arms, and one of them the engineer named against itself

- ⚠⚠ **The engineer's own most-attackable call, in its words: it hand-labelled
  `bound` SEMANTICALLY (tracing one assignment) rather than by the classifier's
  syntactic rule, which is why `local` scores `3/7`.** ✅ **A reviewer could
  fairly say the honest reading is *"the classifier implements its definition
  perfectly; the definition is 43% useful."* ⚠ **BOTH READINGS ARE RECOMPUTABLE
  FROM `hand_labels.tsv`. Recompute them and say which number should be
  published.**
- ⚠ **`check` was measured at `45/60` and DECLARED UNUSABLE rather than
  published.** ✅ **That is the behaviour to copy — verify it was actually
  withheld everywhere, including from the per-program tables and any derived
  claim.** ⚠ **A field declared unusable that still feeds a published ratio is
  worse than one published with its error rate.**
- ⚠ **Generated files: `0/5` recall inside bison/flex output, then flagged and
  excluded.** **Was the exclusion applied to ALL THREE corpora consistently, or
  only to PHP where it was discovered?** ⚠⚠ **An exclusion applied to one arm of
  a comparison is a bias, not a fix.**
- ⚠ **Four self-caught defects, one hiding 29% of PHP.** ✅ **Re-run
  `REBUILD.sh` and confirm the row set is byte-identical, as the report claims.**

## §E — ⚠ what this review must NOT do

- ⚠⚠ **Do not propose a `ptr_offset` pattern.** **RECAP's standing rule binds:
  run a proposed axis's novelty claim BEFORE writing the row, and both
  manager-proposed axes died on a claim one `grep` plus one run would have
  settled.** ⚠ **If §B comes out *"the zero is real and a row is possible"*, say
  so in one paragraph marked UNPROBED and stop.**
- ⚠ **Do not conclude "build more" or "stop".**
- ⚠⚠ **Do not edit `RECAP.md`, `.memory/` or `results/SYNTHESIS.md`.** **Say what
  should change; the manager applies it.**

---

## Constraints

- **`.temp/t131/` only. No `/tmp`.** **Notes in `.temp/t131/NOTES.md` AS YOU GO.**
  **Keep the generator, delete the artefact.**
- ⚠⚠ **Write NOTHING outside `.temp/t131/` and `.tasks/TASK_131_REPORT.md`.**
  ⚠ **`.temp/t129/` is another task's evidence: RUN and READ freely, but copy
  into `.temp/t131/` before editing anything.**
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠⚠ **DO NOT RUN `harness/check.py`, `build.py`, `measure.py` or `report.py`.**
  ✅ **IMPORTING `check.py` to call one function is allowed and `TASK_101` did
  it; running the gate is not.**
- ⚠ **The three C corpora are OTHER PROJECTS' REPOSITORIES — READ ONLY.**
- ⚠ **Every probe needs an arm that MUST FIRE.** ⚠⚠ **This task's headline is a
  ZERO, and a zero is what a broken detector prints. The engineer's raw-regex
  cross-check is the right shape — reproduce it, and give it a PLANTED
  pointer-cursor kernel in `.temp/t131/` that the same regex MUST find.**
- ⚠ **Read the failure-class list at the end of `.memory/03-measurement.md` —
  it carries no usable count; read the list.** ⚠⚠ **Entry 9 is three tasks old
  and is this exact hazard: a calibration arm and a specificity control can be
  the same program.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_131_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 617** (`TASK_130` carried 594 → 617;
`TASK_129` ran concurrently from 583 and the manager has NOT yet reconciled it —
⚠ **a rigour signal, not a ledger; do not re-add**). The calls I am least sure
of:

1. ⚠⚠⚠ **That `ptr_offset = 0` survives §A at all.** **I landed it into `RECAP`
   and `SYNTHESIS.md` and only then noticed the engineer's own artefact test
   applies to it. If it is an artefact of the `(ptr, off, len)` signature, TWO
   published documents need correcting and I would rather know now.**
2. ⚠⚠ **That §B's third reading is not just a nicer story.** **It is the reading
   I find most interesting, which by this project's own history is the strongest
   reason to distrust it** — three successive manager generalisations over the
   refusal set all died, and the manager's guesses on instrument questions have
   been wrong repeatedly in the last ten tasks. ⚠ **Give it the most hostile
   evidence you can and be willing to come back with *"nothing forces it; the
   rungs simply were not written that way."***
3. ⚠ **That the census is worth reviewing rather than accepting.** ⚠ **The
   argument FOR: it is the first frequency evidence this project has ever had, it
   is published in the outward document, and its headline is a ZERO. The argument
   AGAINST: the engineer already withheld one field, declined one comparison and
   self-caught four defects, which is better hygiene than most reviewed work
   here.** ⚠ **If after §A you judge the rest sound, say so and close short —
   that is a legitimate outcome and it costs one page.**

Carry **617** forward, incremented by what you find.
