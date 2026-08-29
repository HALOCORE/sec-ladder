# TASK_138 — the two PROVISIONAL markers inside hashed contract fences. Report.

**Role: research engineer. NOTHING WAS EDITED.** No file under `patterns/`,
`.memory/`, `RECAP.md`, `results/`, `harness/` or `pilot/` was written. No
`git add`, no `git commit` — `git status --porcelain` is empty. All scratch is
`.temp/t138/`. I ran `harness/measure.py --check-stale` (read-only) and did
**not** run `harness/check.py`, `build.py` or `measure.py`. `.temp/t136/` and
`.temp/t137/` were not touched.

---

## ⚠⚠⚠ DELIVERABLE 1 — THE VERDICT IS A **SPLIT**, AND THE TASK FILE'S OWN PREMISE IS WRONG

| marker | verdict |
|---|---|
| `patterns/p09-bitset/spec.md:408` | **MARKER STANDS** — and it is **not a marker** in the sense the triage assumed |
| `patterns/p16-tlv-walk/spec.md:298` | **STALE AS WORDED** — but the staleness is **inherited**, and the primary defect site is `.memory/01-ladder.md:262`, which is **free** and is the manager's |

⚠⚠ **THE TASK FILE SAYS *"Both markers say the same thing: that … the
direction-test repair is 'unattacked'."* THAT IS FALSE. `p09`'s marker does not
contain the word `unattacked`, does not claim the repair is unattacked, and
carries no prohibition.** Verified by parsing the fence, not grepping:

```
$ python3 .temp/t138/fence.py patterns/p09-bitset/spec.md PROVISIONAL unattacked
# patterns/p09-bitset/spec.md: fence lines 355..677
# fence body parses as JSON: yes
--- line 408  marker=PROVISIONAL  INSIDE_FENCE=True
```
…and **zero** `unattacked` hits. The whole of `p09`'s occurrence is:

> *"`.memory/01-ladder.md`'s direction test is what a reviewer should apply to
> every entry above, and it is flagged BROKEN there, so apply the PROVISIONAL
> repair and note that the one entry with a measured direction — the `/ 64`
> exclusion — moves p09's published figure by ZERO, which is neither for nor
> against interest."*

Four clauses, and **every one is still true**: `.memory/01-ladder.md:253` still
flags the test broken; `:262` still marks the repair PROVISIONAL; *"apply it"* is
still exactly what reviewers do (nine of them have — see below); and p09's `/ 64`
direction is a p09 measurement that the repair's status cannot move.

⚠ **And `p09`'s `PROVISIONAL` spends no scepticism about `p09`.** It is an
adjective inside a **citation of another document**, not a flag on p09's own
content. That is `TASK_135`'s own site-6 disposition — *"NOT A MARKER —
past-tense narrative"* — applied to a site `TASK_135` classified the other way.
`.memory/03-measurement.md` entry 13's rule (*"A marker spends a reader's
scepticism. Point it at a live claim or remove it"*) has nothing to bite on here.

`p09`'s wording is a faithful copy of a manager task-file instruction:
`.tasks/TASK_026.md:44-45` — *"`.memory/01-ladder.md`'s direction test is flagged
BROKEN with a PROVISIONAL repair. Do not cite it for anything."*

### `p16` is the only real marker, and the contested word is `unattacked`

`patterns/p16-tlv-walk/spec.md:298`, inside `idiom.why`, in the `WITHDRAWN (a)`
clause:

> *"…it is now flagged as broken there with a repair marked **PROVISIONAL and
> unattacked**, and **must not be cited here again until a reviewer has attacked
> it**."*

Its scope is narrow: *"cited **here**"* = re-instated as **this block's**
load-bearing reason for refusing to pin p16's fold spelling.

### ⚠⚠ THE MANAGER'S DOUBT IS CORRECT. *"APPLIED AND IT FIRED"* ≠ *"ATTACKED"*, AND THE EVIDENCE SUPPORTS THE FORMER ONLY.

**1. The review task said `Apply`, not `attack`.** `.tasks/TASK_045_REVIEW.md:161-164`,
in the §6 miscellany, not in a numbered section:

> *"**The `idiom` block was written AFTER the rung sources**, before any perf
> measurement. That is not the mandated ordering. **Apply the direction test**:
> does any exclusion move a published figure, and by how much? p04's moved by
> exactly 0.00, which is what a clean answer looks like."*

**2. The reviewer reported a magnitude, not a verdict on the rule.**
`.tasks/TASK_045_REVIEW_REPORT.md:214-215`, filed under *"Clean negatives"*:

> *"**The direction test FIRES on p13**: the byte-loop copy/fill idiom entries
> move the headline by **105.00 / 193.00** Ir/call. (p04's moved by 0.00.)"*

That sentence is about **how far a figure moved**. The repair's criterion is
about **which direction flatters the author's thesis**. The reviewer never
states the flattery step, never asks whether the criterion is well-formed, and
nowhere questions it.

**3. What the reviewer attacked was `p13`'s declaration, not the repair.**
Blocker 1's target is `p13/spec.md:374`/`:394`. The direction test was the
**instrument**. An instrument that has been used successfully is *validated by
use*; on this project *attacked* has a specific meaning (PROTOCOL: *"Adversarial
by design. A review that says 'looks good' without having tried to break
something is a failed review"*), and its template exists — `TASK_025_REVIEW`
major 5, which took the **original** test apart by showing its stated clause and
its own cited precedent point in opposite directions. **Nothing of that shape has
ever been aimed at the repair.**

**4. `.memory/01-ladder.md:285`'s own body argues NON-VACUITY, not attack.**

> *"⚠ **THE REPAIR HAS NOW BEEN ATTACKED, AND IT FIRED** … Until then every
> direction test on this project had come out at or near **0.00**, which is what
> a clean declaration looks like **and also what a test that cannot fire looks
> like. It can fire.**"*

*"It can fire"* is a **non-vacuity** claim. ⚠⚠ **So the word `ATTACKED` in that
header is stronger than the evidence in its own paragraph — PROTOCOL rule 13's
header/body shape, one level down from the one `TASK_135` found.** The manager
should **not** simply flip `:262` to *"attacked"*; that would repeat, in the
authoritative layer, exactly the overclaim it is correcting.

**5. Exhaustive check: no task file has ever asked a reviewer to attack the
repair, and no report claims to have.** Every post-`TASK_026` mention in a
`*_REVIEW.md` is an instruction to *apply / run / check* it
(`TASK_042_REVIEW:87,193`, `045:162`, `057_REVIEW:87,93`, `060_REVIEW:91`,
`068_REVIEW:135`, `072_REVIEW:144,161,165`). `TASK_026` itself **was** reviewed
(`TASK_026_REVIEW*.md`) and the review does not touch the repair.

### ⚠ SO WHAT IS TRUE — AND IT IS A BETTER SENTENCE THAN EITHER SIDE'S

Reviewers have **applied the repair by name on nine patterns**, verified quote by
quote:

| review | pattern | what the reviewer did with it |
|---|---|---|
| `TASK_042_REVIEW_REPORT:66,223` | p04 | *"§13's direction test holds"* — both exclusions move the figure by **0.00** |
| **`TASK_045_REVIEW_REPORT:214`** | **p13** | **FIRED — 105.00 / 193.00 Ir/call**; blocker 1; `TASK_046` then relaxed the scoped pin |
| `TASK_047_REVIEW_REPORT:484-491` | p06 | CN-12 — excluding `.reverse()` makes the figure **larger**, *"against the author's thesis"* |
| `TASK_049_REVIEW_REPORT:390-408` | p14 | CN10/CN11 — run **in writing** on two fiats; *"For a safety-tax number the flattering direction is down; both exclusions push up"* |
| `TASK_051_REVIEW_REPORT:394` | p18 | *"ran the direction test in writing"* — entry is **whole-pattern**, directionally neutral |
| `TASK_057_REVIEW_REPORT:403` | p10 | A5 — *"the direction test has nothing to bite on"* (no declaration edit) |
| `TASK_060_REVIEW_REPORT:515` | p27 | **verified BYTE-EXACTLY** — pre-build contract reconstructed from the disclosed edits alone |
| `TASK_064_REVIEW_REPORT:312` | p47 | *"The direction test does not bite here"*, with the counterfactual worked |
| `TASK_072_REVIEW_REPORT:227` | p36 | §11a's direction test checked and found to quote a **dead rung** |

Two more (`TASK_066_REVIEW_REPORT:18-23` on p38, `TASK_070_REVIEW_REPORT:124,165`
on p22) apply the flattering-direction reasoning without naming the test — and
`p38`'s is the sharpest datum available on the criterion's **usability**: the
reviewer caught the manager computing the flattering direction **backwards**.

> **The accurate sentence: the repair is EXERCISED, not ATTACKED. It has been
> applied by reviewers on nine patterns, it fired once decisively on shipped
> code, and a blocker and a pin relaxation rest on it — but it has never itself
> been the OBJECT of a review, and the one time anybody tried to break the
> direction test as a rule, they succeeded (`TASK_025_REVIEW` major 5, on the
> version this repair replaced).**

⚠ **And `p16`'s WITHDRAWN (a) is dead on the merits regardless**, which nobody
has said out loud: `.memory/01-ladder.md:271-273` re-scores p16's `TASK_017`
exclusion **under the repair** and it **passes** (*"against interest"*). So the
repaired test does not supply the withdrawn reason either. The prohibition is
belt-and-braces, not load-bearing.

---

## Deliverable 2 — NOTHING LANDED, DELIBERATELY, AND THE ORDER IS THE FINDING

**I did not edit either fence.** Three reasons, in order of weight.

**1. `p09` STANDS → no edit is licensed.** Editing it is precisely the *"wrong
edit … expensive to unwind"* the task warns about.

**2. `p16`'s fence is a CITATION, and the cited text is still accurate today.**
Parse it: *"a repair **marked** PROVISIONAL and unattacked"* is reportage about
`.memory/01-ladder.md`'s marking, and `.memory/01-ladder.md:262` **still reads**
*"The repair, and it is PROVISIONAL — proposed by the manager at TASK_026, **not
yet attacked by anyone**."* ⚠⚠ **Fix the citation before the cited text and the
tree gets *less* consistent, and you pay a `contract_sha256` move to do it.**
The order is forced: `.memory/01-ladder.md:262` first — it is **free**
(`.memory/` appears in no `source_sha256`; ✅ re-verified independently against
`results/gate/p16-tlv-walk.json`'s own 37 keys) and it is the manager's file —
then the fence.

**3. PROTOCOL rule 9's refined form forbids it.** My deliverable-1 finding
**contradicts `.memory/01-ladder.md:285`**, which is the manager's own text and
is unreviewed by anyone but me. Rule 9: *"If you must record a contradiction
pre-review, ANNOTATE … Do not delete, and do not replace."* A **hashed contract
fence** is the worst place on the project to land an unreviewed re-wording — it
is the one artefact whose whole purpose is to be evidence that a declaration did
not move.

### ⚠⚠ THE BILL IS HALF WHAT IS PUBLISHED — ONE HASH MOVE, NOT TWO

`RECAP.md:12`, `RECAP.md:3955`, `.memory/03-measurement.md:2897-2904` and
`TASK_135_REPORT:90-93` all say **two `contract_sha256` moves + two gate
re-runs**. **It is one and one**, because `p09` needs no edit.

### The `p16` edit, pre-computed so whoever lands it pays one move

`.temp/t138/p16_candidate.py` — dry-run by default, `--apply` to land it. It
proves the substitution is unique, proves the target is inside the fence, proves
the fence still parses as JSON, and prints the hash the gate will record:

```
$ python3 .temp/t138/p16_candidate.py
occurrences of the target sentence in patterns/p16-tlv-walk/spec.md: 1
target is INSIDE the slb-contract fence: yes
contract_sha256 before : a0d431d916e061f9cfd391e3bd75f1555df40d6f1ab808ad5c1b3bcb14c53f72
contract_sha256 after  : 7d7683e1f6b84f22eba8c0a3c4bd4e823b22de6559d81485399999de21277041
fence still parses as JSON after the edit: yes
```

Proposed replacement (preserves the prohibition; states what is true):

> *"…it is now flagged as broken there with a repair (proposed TASK_026) that
> reviewers have APPLIED by name on nine patterns as of TASK_138 — p04 p06 p10
> p13 p14 p18 p27 p36 p47 — and that FIRED once on shipped code with a measured
> number (TASK_045_REVIEW blocker 1, p13: 105.00 / 193.00 Ir/call; TASK_046 then
> relaxed the scoped pin it caught), but that has never itself been the OBJECT
> of a review — it is EXERCISED, not ATTACKED — and must not be reinstated as
> this block's load-bearing reason until a reviewer has attacked the repair
> itself."*

⚠ **The count `nine` is dated in the sentence on purpose** — a count is a cached
derivation (`.memory/03-measurement.md`), and this one will rot.

⚠ **And there is a SECOND `p16` site carrying the same claim**, gate-tier only:
`patterns/p16-tlv-walk/NOTES.md:2005` — *"a repair that is explicitly PROVISIONAL
and **has not been attacked by anyone**"*. Batch it with the fence edit; it costs
nothing extra once the gate re-runs.

### ✅ The *"no re-measure"* claim is TRUE, and I verified it two ways instead of one

The task asked for `--check-stale` before and after. With no edit made, a
before/after is vacuous, so I proved the **mechanism** instead, which is
stronger:

1. `harness/measure.py:224-235` — `measurement_sources()` globs `pdir/*.rs`,
   `pdir/c/*`, `pdir/model.py`, `pdir/inputs/gen.py`, `common/driver.*`,
   `common/slb.py`, `harness/{build,asm,measure}.py`, `verus_run.py`.
   **No `*.md`, no `spec.md`.**
2. The records' own key lists. `results/p16-tlv-walk.json`'s `source_sha256` has
   **18 keys, none ending `spec.md`** (same for `p09`), while
   `results/gate/p16-tlv-walk.json`'s **does** carry
   `patterns/p16-tlv-walk/spec.md`.

So `spec.md` → **gate only**. A fence edit costs one gate re-run and one
`results/tables/p16-tlv-walk.md` re-render (stage 9 pins the table on
`contract_sha256`), and **cannot** stale a measurement record.

Baseline, for the diff after the edit lands:

```
$ timeout 600 python3 harness/measure.py --check-stale
…
52 record(s) examined, 0 STALE
```
(`p05 p07 p11 p17` and `p02-buffer-copy` report `NO BASELINE` — records predating
`source_sha256`; `p18` reports `GEN-ONLY`. All pre-existing, none mine.)

✅ **Both fences reproduce their committed `contract_sha256` from the working
tree exactly**, so the markers are live in the committed records, not an artefact
of an uncommitted edit:

```
patterns/p09-bitset/spec.md   ea0295eaea6ae199… MATCH
patterns/p16-tlv-walk/spec.md a0d431d916e061f9… MATCH
```

---

## Deliverable 3 — the sweep of `patterns/`, and it found a THIRD in-fence marker

**The command** (`.temp/t138/sweep_markers.py`, tiers read out of the **records**
so they cannot drift from what the harness hashes):

```sh
python3 .temp/t138/sweep_markers.py          # classified table
python3 .temp/t138/sweep_markers.py --raw    # every hit with context
```

Tiers = the three costs: **A** = inside the `slb-contract` fence
(`contract_sha256` → gate → published table); **B** = in the gate record's
`source_sha256` only (spec.md prose, `NOTES.md`, `README.md`, `controls/*.py`) →
one gate re-run; **C** = also in the measurement record → a re-measure.

Named token list (`PROVISIONAL UNREVIEWED unattacked TODO FIXME XXX`), all 27
patterns, every committed file:

```
15 marker occurrence(s) under patterns/

== A contract: 3 occurrence(s) in 2 file(s)
   patterns/p09-bitset/spec.md: 1  ['PROVISIONAL']  lines=[408]
   patterns/p16-tlv-walk/spec.md: 2  ['PROVISIONAL','unattacked']  lines=[298]
== C measure: 0
== B gate: 12 occurrence(s) in 2 file(s)
   patterns/p09-bitset/NOTES.md: 11  ['XXX']  lines=[781..793]
   patterns/p16-tlv-walk/NOTES.md: 1  ['PROVISIONAL']  lines=[2005]
== - untracked: 0
```

- ✅ **`C measure` is empty** — no marker sits in any `.rs`, `c/*`, `model.py` or
  `inputs/gen.py`. **Nothing in this class costs a re-measure.**
- ⚠ **`p09/NOTES.md`'s eleven `XXX` are FALSE POSITIVES** — an equivalence-legend
  column (`` `XXXX=` ``) in a control table. Named here so the next triage does
  not re-chase them.
- `p16/NOTES.md:2005` is the tier-B twin of the fence sentence (above).

### ⚠⚠ THE NAMED TOKEN LIST IS INCOMPLETE — a widened sweep finds a THIRD in-fence hit

```sh
python3 - <<'EOF'   # case-insensitive, provisionality phrases the list omits
import glob,os,re
PAT=re.compile(r"awaiting review|not yet reviewed|not yet attacked|unreviewed|"
               r"provisional|\bWIP\b|\bHACK\b|OPEN QUESTION|\bTBD\b", re.I)
def span(p):
    t=open(p).read(); m=re.search(r"```slb-contract\s*\n(.*?)```",t,re.S)
    return (m.start(1),m.end(1)) if m else None
for f in sorted(glob.glob("patterns/p*-*/**/*",recursive=True)):
    if not os.path.isfile(f) or f.endswith(('.bin','.pyc','.json')): continue
    try: t=open(f,encoding='utf-8').read()
    except Exception: continue
    s=span(f) if f.endswith('spec.md') else None
    for m in PAT.finditer(t):
        if s and s[0]<=m.start()<s[1]:
            print(f"{f}:{t.count(chr(10),0,m.start())+1}  {m.group(0)!r}")
EOF
```

Result: `open question` ×27 (once per pattern — **shared boilerplate prose in the
named-spelling paragraph, not debt**), `PROVISIONAL` ×2 (p09, p16), and:

> ⚠ **`patterns/p42-goto-cleanup/spec.md:335` — `unreviewed`, INSIDE the
> `slb-contract` fence.** *"⚠ THIS IS PROTOCOL RULE 9's TASK_099 SHAPE FOR THE
> SECOND TIME — a true sentence struck on the strength of an **unreviewed
> mechanism** — and the first time it happened inside a block whose hash is the
> project's evidence that a declaration did not move."*

**My classification: NARRATIVE, not a marker** — it describes a past defect and
its resolution (citing `.tasks/TASK_118_REPORT.md`), the same disposition
`TASK_135` gave its site 6. **I did not re-adjudicate it**; it is reported, not
cleared. ⚠ **The lesson for the census is the mechanical one: the task's token
list is CASE-SENSITIVE, `UNREVIEWED` ≠ `unreviewed`, and that one letter hid an
in-fence hit from both `TASK_135` and this task's own brief.**

**So the corrected in-fence census is three occurrences in three patterns, not
two in two — and exactly one of them (p16) is live debt.**

---

## Corrections owed in files I may not edit

The manager applies these. Each is free (no hash).

1. **`.memory/01-ladder.md:262`** — *"not yet attacked by anyone"* is the root
   defect. Replace with the exercised-not-attacked sentence. ⚠ **Do not write
   "attacked".**
2. **`.memory/01-ladder.md:285`** — *"THE REPAIR HAS NOW BEEN ATTACKED"* is
   stronger than its own body, which argues non-vacuity. Reword to
   *"THE REPAIR HAS NOW BEEN APPLIED ON SHIPPED CODE, AND IT FIRED"*, and keep
   *"It can fire"*, which is the real result.
3. **`.memory/03-measurement.md:2897-2904`** — *"`p09-bitset/spec.md` and
   `p16-tlv-walk/spec.md` each carry a `PROVISIONAL` inside the `slb-contract`
   block, calling a repair *"unattacked"*"* — **`p09` says no such thing**, and
   *"that `TASK_045_REVIEW` blocker 1 attacked"* overstates what that review did.
   Also: **and `p42-goto-cleanup/spec.md` carries a third**, and the count of
   in-fence sites is **3**, not 2.
4. **`RECAP.md:3955` and `RECAP.md:12`** — same two errors, plus **two
   `contract_sha256` moves + gate re-runs → ONE**, and the `.memory/` fix must
   come first.

---

## Problems

None. Nothing failed, nothing was worked around.

## Unsure / not done

- **I did not run `harness/check.py` on anything.** Deliverable 2's gate runs
  were conditional on *"If the markers change"*, and they did not. Running the
  gate with no edit would rewrite `results/gate/pNN.json` with the four
  run-scoped fields `.memory/03-measurement.md:3219` names — sanitizer
  `diagnostic`, `miri.runs[].seconds`, adversarial group order, the
  `N distinct behaviours` note — producing a dirty tree for the manager and
  **zero** information. **The `blocked` fields I read out of the records
  (`results/gate/{p09,p16}`) are both `[]`, verdict `PASS`.** I never grepped a
  log.
- **I did not re-measure p09's `/ 64` exclusion.** Its *"moves p09's published
  figure by ZERO"* is a p09 fact independent of the repair's status; I took it as
  given. If it were wrong, that is a p09 defect, not a marker defect.
- **`p42-goto-cleanup/spec.md:335` was classified, not adjudicated.** Deciding
  whether the mechanism it calls unreviewed is now reviewed means reading
  `TASK_116`/`TASK_118`'s arc in full; that is a task, not a clause.
- **The nine-pattern application count is a floor.** I verified each by quote;
  I did not exhaustively read all 40-odd review reports, so the true number may
  be higher. Two further patterns (p38, p22) apply the reasoning without naming
  the test and I excluded them from the nine.
- **My deliverable-1 finding contradicts `.memory/01-ladder.md:285`, and no
  second agent has attacked *me*.** Under PROTOCOL rule 9 that is exactly the
  status the direction-test repair itself has, which I note rather than hide:
  **this report is a conclusion with an argument, not a measurement.** The
  cheapest attack on it is to name a review whose *object* was the repair. I
  looked and found none; a second reader should look again before the fence
  moves.
- **Whether to keep p16's prohibition at all is a judgement I did not make for
  the manager.** Its ground is intact (nobody has attacked the repair) but its
  purpose is largely spent (the withdrawn reason is dead on the merits anyway).
  My proposed wording keeps it. Deleting it is defensible and I did not.

## Memory updates

**None written** — subagents may not edit `.memory/`. Four corrections are owed
and listed above under *"Corrections owed in files I may not edit"*.

## Scratch

`.temp/t138/` — generators only, no artefacts to delete:

- `fence.py` — extracts a `slb-contract` fence, hashes it, reports marker context
  with an `INSIDE_FENCE` flag. Reusable on any pattern.
- `sweep_markers.py` — deliverable 3's classifier.
- `p16_candidate.py` — the priced, unapplied `p16` edit; `--apply` lands it.

---

**Running count.** Launched carrying **664** (PROTOCOL rule 2). Branch delta
**+3**: (1) the task file's *"Both markers say the same thing … 'unattacked'"* is
false — `p09` makes no such claim; (2) `.memory/01-ladder.md:285`'s *"HAS NOW
BEEN ATTACKED"* is stronger than the evidence it cites and than its own body —
the repair is **exercised, not attacked**; (3) the published bill of **two**
`contract_sha256` moves + two gate re-runs (`RECAP:12`, `RECAP:3955`,
`.memory/03-measurement.md:2899`, `TASK_135_REPORT:90-93`) is **one and one**,
and the free `.memory/` fix must precede it. (A fourth, not counted as a
contradiction: the deliverable-3 token list is case-sensitive and missed an
in-fence `unreviewed` in `p42`.) **Sum: 667.** ⚠ **A concurrent branch also
carries 664; reconciliation is the manager's, not mine.**
