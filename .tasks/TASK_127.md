# TASK_127 — point the content pin at the right input: `results/tables/*.md`

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
**`.tasks/TASK_121_REPORT.md` §A finding 1 and its artefact table in full**, then
**`.tasks/TASK_125_REPORT.md` §D** (⚠ **it already answered the FAMILY question
and named the fix for this case — do not re-derive it**), then
`.memory/03-measurement.md`'s section on gate records not being byte-reproducible.

Scratch in **`.temp/t127/`**.

⚠ **Needs the tree. It edits `harness/check.py` and (probably) `harness/report.py`,
so it costs ONE 26-pattern gate sweep and NO re-measure — provided you obey the
Constraints. `TASK_125` measured the sweep at 3447 s sequential (57.5 min).**

---

## §0 — ⚠⚠ THE PREMISE, MANAGER-RUN, AND IT IS NOT WHAT YOU MIGHT ASSUME

**`TASK_121` caught `results/tables/p23-partition.md` publishing a sentence that
had become false while gate stage 9 (`check_published_tables`) reported
`FRESH`.** Stage 9 pins the table on `contract_sha256` — the sha256 of the
`slb-contract` block in `spec.md` — and the contract had not moved.

⚠⚠ **BUT THERE IS NO LIVE INSTANCE TODAY. Manager-measured before writing this
file:**

```
for each of 26: harness/report.py <pNN> --stdout  >  .temp/mgr127/<name>.rendered
compared to the committed results/tables/<name>.md
                                        SAME 26   DIFF 0
```

⚠ **The naive comparison reports 26/26 MOVED BY ONE LINE and that is an
artefact** — `report.py --stdout` uses `print(md)` and the file path uses
`write(md)`, so the captured render carries one extra trailing newline. **Strip
it and the tables are byte-identical to a fresh render.** ⚠ **If your first probe
reports 26 moved tables, that is this artefact and not a finding.**

✅ **So this task is FORWARD protection, not a repair.** ⚠⚠ **SAY THAT IN YOUR
REPORT, because a task whose value is forward-only is a task somebody will later
"confirm" by finding nothing and calling the gap closed.** **The same shape as
`TASK_125` §A, where nearly all the value was in preventing the 89th dangling
citation rather than in fixing the 88.**

## §A — ⚠ MEASURE THE INPUTS BEFORE YOU DESIGN THE PIN

**`report.py` reads exactly THREE things per pattern** — manager-read from the
source, ⚠ **verify it, do not trust it**:

| read by | path | why it is read that way |
|---|---|---|
| `load(pid)` | `results/pNN-<slug>.json` | the measurement record; discriminated by carrying a `cells` list |
| `read_idiom(pattern)` | `patterns/<pattern>/spec.md` | the **declaration**, deliberately re-read live so the table shows what the pattern declares TODAY |
| `read_gate_audit` + `read_gate_loud` | `results/gate/<pattern>.json` | the **measurement**, deliberately NOT recomputed, so the table cannot disagree with the artefact |

⚠ **Those two "deliberately" clauses are opposite on purpose and both docstrings
explain why. Do not collapse them.**

⚠⚠ **THE THING THAT DECIDES THE DESIGN, AND IT IS ONE MEASUREMENT:**

> **Is `results/gate/<pattern>.json` stable enough, run to run, to be hashed?**

**`.memory/03-measurement.md` says gate records are NOT byte-reproducible** —
sanitizer strings, `miri.runs[].seconds`, adversarial group order, and the
`N distinct behaviours` notes line all move. ⚠⚠ **A whole-file hash of the gate
record would therefore make stage 9 fire on ITS OWN GATE RUN, which is worse than
no pin at all.**

✅ **One datum in your favour, manager-checked:** the `N distinct behaviours`
line appears in the gate records and **reaches ZERO of the 26 tables**
(`grep -c "distinct behaviour" results/tables/*.md` → 0 everywhere). ⚠ **But
`shout_section` DOES render `loud`, and nobody has asked whether `loud` entries
carry volatile text.** **Ask. That is the measurement.**

**Deliverable of §A: a table of the three inputs × {stable, volatile, volatile in
a field the render does not read}, with the evidence.**

## §B — the design, and pick it on the MEASUREMENT rather than on elegance

**`TASK_125` §D already settled the shape:** *"the `results/tables/*.md` gap is
not a missing KIND of instrument, it is the known instrument pointed at the wrong
input."* ✅ **So you are pointing `derived_from_sha256` — which stage `9b`
(`check_control_json_pins`) already knows how to check — at what the table was
actually rendered from. Three candidate spellings:**

1. **Whole-file `derived_from_sha256` over the three paths.** Simplest, reuses
   stage 9b's shape verbatim. ⚠ **Dies if §A says the gate record is volatile.**
2. **A projection hash** — hash only the keys `report.py` reads
   (`idiom_audit`, `loud`, `controls_json`, `verdict`, `contract_sha256`).
   Survives volatility. ⚠⚠ **BUT TWO IMPLEMENTATIONS OF THE SAME PROJECTION IS
   `TASK_084`'s FAILURE EXACTLY — *a test split across two artefacts tests
   neither seam*.** **One function, imported by both, or a written justification
   for why two cannot drift.**
3. **Recompute-and-compare** — `check.py` imports `report.py`, re-renders, and
   compares bytes. ⚠ **Directly answers the real question (*would a fresh render
   differ?*) and needs no projection and no path list.** ⚠⚠ **Two costs, name
   both: (i) the gate then fails for a REPORTING reason if `report.py` ever reads
   something volatile; (ii) there is a ONE-RUN LAG — stage 9 runs mid-gate and
   reads the PREVIOUS run's `results/gate/<pattern>.json`, so a change this run
   makes to the record surfaces on the NEXT run.** ⚠ **`TASK_121` already
   documented the loop as *gate → `report.py` → gate, twice*, so the lag may be
   the status quo rather than a new defect — decide and say which.**

⚠ **Digest note so nobody pays a phantom cost: `check.py` importing `report.py`
is free — `check.py`'s gate digest globs `harness/*.py` non-recursively and both
are already in it.** ⚠ **What is NOT free is importing anything from
`harness/tools/`, which is OUTSIDE the digest by design (`TASK_125`); doing so
would silently drop a file out of the digest.**

## §C — ⚠ ADDITIVE. DO NOT DELETE A WORKING CHECK TO INSTALL A BETTER ONE.

**Stage 9's contract pin catches a real and different thing: *the declaration
moved since the table was rendered*.** ⚠ **Keep it unless you can SHOW the new
pin strictly subsumes it** — `spec.md` is one of the three inputs, so subsumption
is plausible and is exactly the kind of plausible-and-unmeasured claim this
project keeps paying for. ✅ **Show it or keep both; both is fine and cheap.**

⚠ **And whatever you land, stage 9's three existing verdicts (`MISSING`,
`UNPINNED`, `STALE`) each carry a diagnostic naming its own fix, and `TASK_119`
had to correct the `MISSING` one because the two fixes are NOT the same fix
(`MISSING` deadlocks the two-command loop; it needs three commands, `measure.py`
first). **Any new verdict you add owes the same: the exact command that fixes
it, verified by running it.**

## §D — the free ride-alongs, same sweep, from `TASK_121`'s own follow-on list

1. ✅ **`patterns/p23-partition/controls/controls.log` has NO pin and the fix is
   FREE:** `run.sh` emits a `controls_pin.json` beside it —
   `derived_from_sha256` over `guard_variants.c` + `run.sh`, plus a
   `pin.regenerate` command — **and stage 9b covers it with ZERO new gate code**,
   because 9b globs `patterns/*/controls/*.json`. ⚠ **The log embeds ASLR
   addresses and absolute repo paths, so it is NOT byte-reproducible: do not try
   to self-hash it.** ⚠ **Its four quoted figures live in `p23/NOTES.md`
   (`k_ij 586 B`, `k_mz 608 B`, `k_bug 614 B`, `k_selfpivot 612 B`) — check they
   still hold, and if they do not, THAT is a live instance of the class and it
   outranks everything else in this file.**
2. **`common/layout/data/` ×3.** `TASK_121` recommended **documenting as
   ACCEPTED** rather than pinning: the generators live in `common/layout/*.py`,
   which IS in every gate `source_sha256`, so a pin there costs a sweep for low
   value (RECAP finding 16 already withdrew the wall-clock rows). ⚠ **And
   `predictions_p01oos.json`'s own sha256 IS a pre-registration commitment — a
   DIFFERENT and STRONGER thing than a staleness pin; do not "upgrade" it.**
   ⚠⚠ **If you accept, WRITE THE ACCEPTANCE INTO THE FILE THAT WOULD OTHERWISE
   NEED THE PIN, not only into your report** — an acceptance that lives only in a
   report is the same class of claim this task is about.
3. ⚠ **The 31 gitignored `controls/*.py` that `json.dump` into `.temp/`: DO NOT
   FIX HERE.** `TASK_125` §D concluded **promotion** is the real fix and that is
   31 files across 14 patterns. ✅ **One paragraph only: does the tables fix
   change that estimate?**

## §E — ⚠⚠ THE ARMS. THE FALSE-POSITIVE ONE IS THE ONE THAT MATTERS HERE.

**Three arms, all required, all shown in the report with their output:**

1. **MUST FIRE:** plant a change into a measurement record (or whichever input
   your design pins) → stage 9 goes STALE → **and the printed diagnostic names a
   fix command you then RUN and show works** → restore → FRESH.
2. **MUST NOT FIRE — and this is the arm that kills a bad design:** ⚠⚠ **run the
   gate TWICE on one pattern with no source change and show stage 9 is FRESH both
   times.** **A staleness pin that fires on its own gate run is strictly worse
   than no pin.** ⚠ **Use `p03` or `p23`: `TASK_125` measured that their
   `N distinct behaviours` notes line MOVES BETWEEN RUNS because those cells read
   uninitialised memory, so they are the two patterns most likely to expose a
   false positive.** ⚠ **`TASK_126` then measured the nondeterminism footprint at
   SEVEN patterns, not two — get the list from `TASK_126_REPORT.md` §A4 and pick
   from it rather than from this sentence.**
3. **The `MISSING` arm still has to work** — it is the verdict `p23` shipped past
   once. Re-run it.

⚠ **Read the failure-class list at the end of `.memory/03-measurement.md` — it
carries no usable count; read the list.** ⚠⚠ **Entry 8 is the one to read twice:
*a control that FIRED and whose firing did not support its printed sentence*.**

## §F — the sweep and the publishing chain, LAST

**Full 26-pattern `harness/check.py`, then `report.py` where tables moved, then
`synthesis/licence.py --emit` BEFORE `synthesize.py`, then `outward_ir.py
--emit`, then `synthesize.py` AGAIN, then `measure.py --check-stale`.**
**Expect `24 PASS + 2 PASS-WITH-BLOCKED-ROWS`, 0 failures, `52 records 0 STALE`.**
⚠ **`p42`'s blocked-row count is environment-selected: `TASK_125` saw 3 against a
documented band of 1–2. Do NOT chase a Miri block.** **Anything else red: STOP AND
REPORT.**

---

## Constraints

- **`.temp/t127/` only. No `/tmp`.** **Notes in `.temp/t127/NOTES.md` AS YOU GO.**
  **Keep the generator, delete the artefact.**
- ⚠⚠ **PROMOTE, DON'T PUBLISH: do not commit `.temp/`, and any `.temp/` path you
  cite from a COMMITTED file must be promoted into the tree first.**
  **`.tasks/*_REPORT.md` citations are EXEMPT.** ⚠ **`harness/tools/temp_citations.py`
  enforces this; run it before you finish and expect `rc=0`.**
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **`.memory/`, `RECAP.md` and `results/SYNTHESIS.md` are manager-only.**
  ⚠⚠ **`results/synthesis.md` (lower case) is GENERATED — never hand-edit it.**
- ✅ **You MAY edit `harness/check.py`, `harness/report.py`,
  `patterns/*/NOTES.md`, `patterns/*/README.md`, `patterns/*/controls/*`,
  and regenerate `results/tables/*.md`.**
- ⚠⚠ **DO NOT TOUCH `harness/{build,asm,measure}.py`, `verus_run.py`, or ANY
  `patterns/*/{*.rs,c/*,model.py,inputs/gen.py}`** — every one is
  measurement-hashed and a comment-only edit stales the record. ⚠ **`controls/*`
  is NOT measurement-hashed — the glob is non-recursive — but it IS in the gate
  `source_sha256`.**
- ⚠ **Cite `check.py` by FUNCTION NAME, never a line number.** ⚠ **`TASK_121`
  found `_check_controls_json` cited in a task file resolves NOWHERE; the real
  name is `check_control_json_pins`. Verify any name you cite.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_127_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 583** (`TASK_126` carried 566 → 583;
⚠ **a rigour signal, not a ledger — do not re-add it**). The calls I am least
sure of:

1. ⚠⚠ **That recompute-and-compare (§B3) is the right shape.** **I lean to it: it
   is the only one that answers the actual question and it needs no second
   implementation of anything.** ⚠ **But it makes the GATE depend on the
   REPORTER, and a gate that fails for a reporting reason is a gate people start
   ignoring.** **If §A's measurement says the projection or the whole-file hash is
   the honest one, take it and say why I was wrong.**
2. ⚠⚠ **That this is worth a 57.5-minute sweep at all, given §0 says there is NO
   live instance.** ⚠ **THE ALTERNATIVE I WANT YOU TO WEIGH SERIOUSLY AND COST:
   make the publishing chain ALWAYS re-render all 26 tables, unconditionally.
   Staleness then becomes structurally impossible rather than detected, it costs
   NO gate stage, and a re-render is seconds.** ⚠ **Its weakness is that it is
   PREVENTION and only holds while the chain is actually run — which is exactly
   the assumption that failed for `p09` (16 tasks stale) and `p23` (no table at
   all).** **If after §A you think the one-line chain rule beats the gate stage,
   SAY SO AND DO THAT INSTEAD. I would not argue, and it would be the cheapest
   good outcome available.**
3. ⚠ **That the contract pin should stay (§C).** **It may be strictly subsumed
   once `spec.md` is in the pinned set, and carrying two checks for one property
   has its own cost — a reader who sees two pins assumes two properties.**

Carry **583** forward, incremented by what you find.
