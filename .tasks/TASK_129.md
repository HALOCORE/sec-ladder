# TASK_129 — the idiom census this project declared impossible, on the corpus it did not know it had

**Role: research engineer.** ⚠ **Deliverable is a FREQUENCY TABLE with a measured
error rate, and a bounded statement of what it does and does not license.**
⚠⚠ **Do not build a pattern. Do not propose one. Do not conclude "build more" or
"stop".**

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` finding 42 IN FULL,
INCLUDING ITS STRUCK CODA** (⚠ **the coda is why this task exists and it is a
worked example of the failure class this task is most likely to repeat**), then
**`.tasks/TASK_123_REPORT.md` §D** (the 20-CVE table — the census that CANNOT
answer this question, and why), then `.memory/06-catalogue.md`.

Scratch in **`.temp/t129/`**.

⚠⚠ **TWO OTHER TASKS ARE LIVE IN THIS TREE (`TASK_127` edits `harness/` and
regenerates `results/`; `TASK_128` is read-only). YOU ARE THE MOST ISOLATED OF
THE THREE AND MUST STAY THAT WAY: WRITE NOTHING OUTSIDE `.temp/t129/` AND
`.tasks/TASK_129_REPORT.md`.** ✅ **Read committed sec-ladder state with
`git show HEAD:<path>`.** ⚠ **DO NOT RUN `harness/check.py`, `build.py` or
`measure.py`.**

---

## §0 — why this task exists, and the mistake it is descended from

**`TASK_113` asked for the admission bar to be argued from the DISTRIBUTION
rather than from taste. `TASK_123` correctly answered that a CVE corpus cannot
do it — CVEs select for EXPLOITABILITY, not FREQUENCY, and 8 of its 20 rows are
pure decision bugs.** ⚠⚠ **The manager then published, in `RECAP.md` AND in
`results/SYNTHESIS.md` §7, that the census therefore CANNOT BE RUN because no
independent C corpus exists on this box. THAT WAS FALSE AND THE CAUSE WAS
`-maxdepth 6` IN THE MANAGER'S OWN ONE-LINER.** ✅ **Both sites are now
corrected.**

**Manager-measured, and re-derive it rather than trusting it:**

```
/home/apt/repos_common/php-in-safe-rust/build/php-4.0.2/
    301 .c + 252 .h,  186 805 lines of .c,  22 MB   <- UPSTREAM PHP 4.0.2, WHOLE TREE
    ext/ 220   Zend/ 25   main/ 22   sapi/ 15   win32/ 9   regex/ 8   TSRM/ 1
    memcpy 235 · strcpy 123 · strcat 145 · strncpy 52 · malloc 899 · alloca 303
    goto 324  (p42's axis) · "[i]" 847 · for(...;...<...;) 579 · for( 916

/home/apt/repos_common/unsafe-rust-pitfall/TASKS/TASK014_eng_coreutils_u2/.temp/work/coreutils/
    310 .c,  56 873 lines            <- GNU coreutils
    ⚠⚠ HEAVILY DUPLICATED: one gnulib copy per utility directory. DEDUP BY CONTENT
       HASH BEFORE COUNTING ANYTHING, and report how many distinct files remain.
```

⚠⚠ **AND A SECOND INSTRUMENT DEFECT, INSIDE THE CORRECTION ITSELF, DISCLOSED SO
YOU DO NOT REPEAT IT: the manager's first density probe used `for *(`, in which
`*` quantifies the SPACE and `(` OPENS A GROUP — it reported ZERO for-loops in a
tree with 916.** ⚠ **Failure-class entry 8: a control that returned a number that
did not support its printed sentence. TWO instrument defects in ONE
correction — assume yours has one too and go looking for it.**

## §A — ⚠⚠ THE CATEGORIES ARE THE BAR'S LIMBS. THAT IS THE DESIGN.

**Do not invent an idiom taxonomy and do not classify by pattern name.**
⚠ **`.memory/06-catalogue.md`'s own `census.py --naive` arm shows a KEYWORD
CLASSIFIER READS 10 BUILT AGAINST A TRUE 26, because adjudication prose contains
the word "BUILD". A classifier over source text will be worse.**

✅ **Classify each site by the three limbs of the reviewed admission bar, because
that is the object this census is supposed to inform:**

> **A row is admissible whenever it brings a new MECHANISM — *(1)* a new
> **operator on the safety line**, *(2)* a new **source of the bound**, or
> *(3)* a new **reason the check is or is not elided**.**

**A SITE, for this census, is a memory access whose safety depends on a bound.**
**For each site record, at minimum:**

- **the OPERATOR** — index / pointer-offset / `mem*` call / `str*` call / cast-and-deref;
- **the SOURCE OF THE BOUND** — a `#define` capacity, an attacker length field, a
  `strlen`, a struct field, a prior pass's count, a loop's own induction
  variable, another cursor, **or NONE (unbounded)**;
- ⚠ **whether the bound is CHECKED at the site, checked EARLIER, or not at all** —
  ⚠⚠ **the third limb, ELISION, is a COMPILER property and is NOT observable in
  source. SAY SO AND DO NOT FAKE IT. Recording *"checked / checked earlier /
  unchecked"* is the closest a source census gets, and it is a DIFFERENT thing
  from limb 3.**

⚠⚠ **`TASK_128` IS CONCURRENTLY TESTING WHETHER THESE THREE LIMBS ARE PRICEABLE
AT ALL, AND MAY STRIKE ONE. THAT IS FINE — report all three and let the
adjudication follow. Do not wait for it, do not read its report, and do not
adjust your categories to agree with it.**

## §B — ⚠⚠⚠ THE ARM WITHOUT WHICH THIS TASK IS WORTHLESS

> **HAND-CLASSIFY A RANDOM SAMPLE AND MEASURE YOUR CLASSIFIER'S ERROR RATE.**

**Draw a random sample of sites — 60 is enough to be useful and small enough to
do honestly — classify them BY HAND from the surrounding source, and report
agreement with the automatic pass, per field.** ⚠ **Report the DISAGREEMENTS
individually, not just a percentage: the interesting output of this arm is
*which* category the classifier confuses, because that is what biases the
ranking.**

⚠⚠ **A frequency table with no measured error rate is a number nobody can check,
and this project has a standing rule against exactly that shape.** ✅ **If the
error rate is bad, THAT IS THE RESULT — report the table as UNUSABLE and say
which field killed it. That is a complete and respectable outcome and it costs
one task instead of a false ranking that gets cited for a year.**

⚠ **Sample by SITE, not by file** — files vary enormously in site density and a
per-file sample would over-weight small files. **Say how you drew it and seed it
reproducibly.**

## §C — the replication arm, and it is the control that makes the census mean anything

⚠⚠ **ONE CORPUS CANNOT DISTINGUISH *"a property of C"* FROM *"a property of
PHP 4.0.2"*.** **PHP is 2000-era interpreter C in one house style; coreutils is
GNU-style utility C. They are two samples, not a distribution over C, and the
whole census is worth exactly what its cross-corpus agreement is worth.**

✅ **So: run the census on PHP as the PRIMARY, then re-run it unmodified on
deduplicated coreutils, and publish BOTH RANKINGS SIDE BY SIDE.**

- **If the top of the ranking AGREES across the two, the census has a claim to be
  about C rather than about PHP** — ⚠ **a weak claim from n=2, and say so in
  those words.**
- ⚠⚠ **If they DISAGREE, that is the finding and it is a better one than
  agreement would be: it would mean idiom frequency is a property of the PROGRAM
  and not of the LANGUAGE, and a frequency-argued admission bar is therefore not
  available on any corpus this size.** ✅ **That outcome retires `TASK_113`'s
  request honestly, which nothing so far has.**

## §D — the question the table is for, and its ONE honest form

**Cross the ranking against the 26 built patterns and the 22 adjudicated rows:**

> ⚠ **Do the built patterns cover the FREQUENT mechanisms, or the INTERESTING
> ones?**

✅ **Both answers are publishable and neither is embarrassing.** ⚠⚠ **BUT STATE
THE FINDING ABOUT COVERAGE AND NOT ABOUT QUALITY: *"the most common bound-source
in 187 000 lines is X and no built pattern carries it"* is a measurement.
*"therefore the project built the wrong things"* is not — the bar was never
frequency-based, so a frequency gap is a DESCRIPTION of the bar's choice, not a
refutation of it.**

⚠ **And the reverse gap is as interesting: a mechanism this project BUILT that
occurs ZERO times in 240 000 lines of real C is a row whose realism claim is now
measured and negative.** ⚠⚠ **If you find one, name it and give its count, and
do NOT soften it — but check the classifier's confusion matrix for that category
first, because a zero from a classifier that cannot see the category is not a
zero.**

## §E — ⚠ the bounds on what you may claim

- ⚠⚠ **n = 2 PROGRAMS. Not "C". Every headline sentence must carry the corpus.**
- ⚠ **PHP 4.0.2 is from 2000.** **Say it. An idiom's frequency in 2000-era C is
  evidence about 2000-era C.**
- ⚠ **The corpora are OTHER PROJECTS' TREES — `CLAUDE.md`'s `../LearnVeri/` rule
  applies: READ ONLY. Copy what you need into `.temp/t129/`.**
- ⚠⚠ **The coreutils tree is under another project's `.temp/`, which by that
  project's own convention is DELETABLE AT ANY TIME. RECORD A SHA256 MANIFEST OF
  EVERY FILE YOU READ, from both corpora, and commit the MANIFEST — not the
  corpus.** ⚠ **Do not copy 22 MB into this tree: *promote, don't publish* is
  about kilobytes.**

---

## Constraints

- **`.temp/t129/` only. No `/tmp`.** **Notes in `.temp/t129/NOTES.md` AS YOU GO.**
  **Keep the generator, delete the artefact** — ⚠ **the census SCRIPT and the
  MANIFEST and the RESULT `.json` stay; any extracted copy of the corpus goes.**
- ⚠⚠ **Write NOTHING outside `.temp/t129/` and `.tasks/TASK_129_REPORT.md`.**
  **`.memory/`, `RECAP.md`, `results/SYNTHESIS.md` are manager-only;
  `results/synthesis.md` (lower case) is GENERATED and never hand-edited.**
- ⚠⚠ **DO NOT RUN `harness/check.py`, `harness/build.py`, `harness/measure.py`,
  or `harness/report.py`.** **Two other tasks are live in this tree.**
- **No `git add` / `git commit`.** Read-only git is fine and you will need
  `git show HEAD:` for sec-ladder's own files.
- ⚠ **Every probe needs an arm that MUST FIRE, and §B IS that arm for the census
  itself.** ⚠ **Read the failure-class list at the end of
  `.memory/03-measurement.md` — it carries no usable count; read the list.**
- `timeout <N> <cmd>`; never `pkill`/`killall`. ⚠ **A `grep -r` over 240 000
  lines is seconds; a per-site parse in Python may not be. Budget it and say
  what you skipped if you skipped anything — `.memory/`'s rule is NO SILENT
  CAPS.**

Write your report to `.tasks/TASK_129_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 583** (⚠ **a rigour signal, not a ledger —
do not re-add it; `TASK_127` and `TASK_128` are carrying it concurrently and the
manager reconciles**). The calls I am least sure of:

1. ⚠⚠ **That a source-level census can classify *the source of the bound* at
   all.** **It is the field this project cares most about and the one hardest to
   read off a line of C — the bound may be established three functions away.**
   ⚠ **If §B's hand-check says that field is unclassifiable at acceptable error,
   SAY SO AND REPORT THE OTHER FIELDS. A census of operators alone, with a
   measured error rate, beats a census of three fields with an unmeasured one.**
2. ⚠⚠ **That two corpora are enough to be worth running at all.** ⚠ **My honest
   read is that AGREEMENT would be weak evidence and DISAGREEMENT would be strong
   evidence — the test is asymmetric, and I am spending a task on a design whose
   good outcome is weak. If you see a third corpus on this box, take it — the
   manager's file list is 31 929 rows and is NOT fully characterised. Rebuild it
   with** `find / -name '*.c' -type f 2>/dev/null | grep -v -e /proc -e /sys -e sec-ladder`
   **(⚠ no `-maxdepth`, which is the whole point; ~4 minutes).** ⚠ **Most of them are another project's
   synthetic c2rust benchmark and are NOT independent — check before using
   anything from `unsafe-rust-pitfall/TASKS/TASK003*`.**
3. ⚠⚠ **That this changes anything even if it works.** **The catalogue is closed,
   the domain is enumerated, nothing is queued that would USE a frequency
   ranking, and the standing conclusion is *publish no generalisation over the
   refusal set*.** ⚠ **The argument FOR is that `SYNTHESIS.md` §7 now says the
   census is RUNNABLE AND UNRUN, and an unrun census named in the outward
   document is a debt this project has watched rot before. Running it converts a
   limitation into a result either way.** ⚠ **If after §A you judge the design
   unsound, say so in one page and stop — that is cheaper than a bad table.**

Carry **583** forward, incremented by what you find.
