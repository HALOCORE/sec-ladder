# TASK_111 — review `results/SYNTHESIS.md`, the artefact a reader will quote

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then **`results/SYNTHESIS.md` in
full**, then `.tasks/TASK_108_REPORT.md`, then `RECAP.md`'s findings section and
its **"Retracted — do not reinstate"** list.

Scratch in **`.temp/r111/`**. **You are the only agent running.**

---

## Why this review matters more than the last six

Every previous review attacked a **pattern**. This one attacks **the document a
reader outside this repo will actually read and quote**, and which nothing has
yet checked. ⚠⚠ **This project's single most repeated failure is publishing a
claim in the FLATTERING direction and retracting it later — five patterns did
it, and the widest was `510×`. A synthesis is where that failure would be
cheapest to commit and most expensive to discover.**

## §A — ⚠⚠ EVERY NUMBER, AGAINST ITS SOURCE. THIS IS THE DELIVERABLE.

**For each figure in `SYNTHESIS.md`:**

1. **Does it match the committed record?** ⚠ **Read `results/*.json`,
   `results/gate/*.json` and `results/synthesis.md` — NOT the task reports.**
   Two corrections in the `p23` cycle and one in `p42`'s existed purely because
   a number was copied from a report's prose rather than from the record, and in
   one case the report's own **table** had it right while its **prose** had it
   wrong.
2. **Does it carry its conditions?** Optimisation level, inline mode, `Ir`
   convention (kernel-exclusive vs whole-program marginal), and **domain**.
   ⚠ **`p23`'s rule is that a number quoted without its rank is quoted without
   its domain — and `p23` itself broke it on its own C row.**
3. ⚠⚠ **Does it quote anything WITHDRAWN?** The withdrawn cells are marked
   `‡ WITHDRAWN — not a quantity` in `results/synthesis.md`; the retraction list
   is in `RECAP.md`. **A withdrawn number reaching the headline document is the
   worst single outcome available here.**
4. **Is any figure a cached derivation that has gone stale?** ⚠ **This is a live
   class: `TASK_108` itself caught the manager quoting "seven controls" when the
   list holds six, in five task files, after writing the rule that says cite the
   list and not the ordinal.** **Recount every count.**

## §B — the four results: is each actually supported?

**Take each of the four in turn and try to break it.**

- ⚠ **Result 1 rests on a table of EXCEPTIONS** which the writer says is what
  makes it believable. **Check the exceptions are real and complete** — an
  exception table that omits an inconvenient row is the flattering direction
  wearing a disguise.
- ⚠⚠ **Result 2, *"where safe Rust does not help"*, is the section a
  decision-maker will act on.** **Check every claim in it individually.** Is
  `p34` fairly described given it is a **refused** row? Is the allocator-recycling
  result stated at its true scope? ⚠ **Overclaiming HERE is worse than
  overclaiming anywhere else in the document, because it argues against the
  safer choice.**
- **Result 3 concerns what a proof buys.** ⚠ **`p42`'s story is the load-bearing
  one and it was itself retracted once already** — verify the document tells it
  as *an encoding choice, not a limit of the prover*, and that it carries the
  surviving caveat (**deleting the ledger's leak-freedom `ensures` still gives
  `18 verified, 0 errors`** — load-bearing for the program, not for the count).
- **Result 4 is the instrument's own domain (finding 37).** ⚠ **It rests on
  `TASK_102`, which is UNREVIEWED.** **Is it marked PROVISIONAL where it is
  used, not only in §7?**

## §C — what a synthesis can get wrong that a pattern cannot

1. ⚠⚠ **COMPRESSION THAT DROPS A RESULT.** The document argues 26 patterns
   collapse to four results. **Go through all 39 findings and list any that the
   synthesis does not represent and should.** **A finding silently dropped is
   indistinguishable from a finding retracted, and only one of those is honest.**
2. **FALSE CONFIDENCE FROM AGGREGATION.** *"Replicated across N patterns"* is
   only as strong as the weakest N. ⚠ **Where the document counts patterns in
   support of a claim, check each one actually supports it.**
3. ⚠ **AN OUTSIDER CANNOT CHECK THE CAVEATS.** The audience is someone who has
   not read this repo. **Read §0–§1 as that person: is the ladder actually
   defined? Could they tell kernel-exclusive from whole-program marginal? Would
   they know which numbers are safe to quote?** ⚠ **If a claim is only correct to
   a reader who already knows the caveat, it is wrong in this document.**
4. **UNREVIEWED WORK CITED AS SETTLED.** §7 names the unreviewed tasks. ⚠ **But
   check the BODY: a claim marked PROVISIONAL only in a closing section reads as
   settled where it is used.**

## §D — clean negatives are wanted

⚠ **The writer made three corrections to the manager's own task file** (the stale
PROVISIONAL list, the seven-vs-six count, and `p24` being cited as a built
pattern when it is an unreviewed probe of a row whose purpose was to retract its
own cost figure). ✅ **Verify all three landed, and that `p24` really is absent
from the deliverable.** **If the writer caught the manager three times, the
question is what it did not catch.**

---

## Constraints

- **`.temp/r111/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit ANYTHING** — not `results/SYNTHESIS.md`, not `.memory/`, not
  `RECAP.md`, not a pattern. **You are a reviewer. Report.**
- **You may run `harness/measure.py --check-stale` and read anything. Do not run
  `check.py`, `build.py` or `measure.py` otherwise** — the tree is green and a
  gate run would rewrite `results/gate/` for no reason.
- ⚠ **Every probe needs an arm that must fire.** The list at the end of
  `.memory/03-measurement.md` holds **six live entries numbered 1–7** (entry 5 is
  retracted). **Do not become the next one — and do not quote its ordinal.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_111_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 407.** The calls I am least sure of:

1. ⚠⚠ **That the four-result compression is honest rather than convenient.**
   I asked for 3 000–6 000 words and the writer delivered at the top of that
   range, having first thought 2 000 was right. **A length target can quietly
   become a compression target, and the thing that gets cut is the awkward
   result.** **§C.1 is how you would find that, and I think it is the most likely
   real defect in the document.**
2. **That §2 (*where safe Rust does not help*) is at its true scope.** It is the
   section I pushed hardest for, ⚠ **and a manager pushing for a section is
   exactly how an overclaim gets in.** **Attack it as though I had written it.**
3. **That a synthesis was worth doing at all instead of a 27th pattern.** ⚠ **If
   the document turns out to be a restatement of the findings section with
   better prose, say so** — that would mean the value was in `RECAP.md` all along
   and the project should have kept building.

Carry **407** forward, incremented by what you find.
