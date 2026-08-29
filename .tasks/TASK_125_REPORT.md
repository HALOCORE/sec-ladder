# TASK_125 report — the `.temp/` convention is now checkable, and §B is a baseline, not a cleanup

**Role: research engineer.** Scratch: `.temp/t125/` (`NOTES.md`, four probes with
their logs, `classify.py`, `acceptance.py`, `sweep.sh`, `chain.sh`, all logs).
No `/tmp`. No `git add`, no `git commit`.

## Did

| path | what |
|---|---|
| `harness/tools/temp_citations.py` | **NEW.** The checker. `--list`, `--census`, `--update`, `--include-tasks`. |
| `harness/tools/temp_citations_baseline.json` | **NEW.** 66 classified entries (77 citations), each with a `kind` and a `note`. |
| `TOOLCHAIN.md` | **+1 section**, `## The .temp/ citation check`: the commands, the this-box caveat, the blind spot, and why the tool is not in `harness/`. |

**Nothing else in the tree was edited.** In particular **no file in any gate or
measurement digest**, which is a deliberate property and is what the §E sweep
proves (below).

---

## §A — where the checker landed, and why it is NOT in `harness/`

⚠ **I took the manager's least-sure #2 and moved it: `harness/tools/`, not
`harness/`.** It is one directory deeper, and that difference is worth a
26-pattern sweep **every time the tool is ever edited again**.

`check.py`'s gate digest builds `source_sha256` from a `srcs` list that includes
`glob.glob(os.path.join(REPO, "harness", "*.py"))`. **That glob is
non-recursive**, exactly as `common/*.py` is non-recursive and does not reach
`common/layout/` — which `check.py`'s own `srcs` comment says in those words.
Measured, not assumed:

```
$ python3 -c "import glob,os; print(sorted(os.path.basename(p) for p in glob.glob('harness/*.py')))"
['asm.py','build.py','check.py','dloop.py','fixture.py','limbs.py','measure.py','report.py','vparse.py']
$ ... 'harness/tools/_probe_only.py' in glob.glob('harness/*.py')  ->  False
```

and, after the full 26-pattern sweep with the new file in place:

```
26 gate records: source_sha256 IDENTICAL in 26/26, and 0 records gained a
                 `harness/tools/...` key
p01 source_sha256 key count HEAD/now: 35 / 35
harness keys now: asm build check dloop fixture limbs measure report vparse   (9, unchanged)
```

**The argument, in the manager's own terms.** The objection was *"it is a
documentation check, not a gate stage, and putting it in `harness/` costs a
26-pattern sweep and implies it certifies measurements."* Both halves are right,
and both are answered by one directory:

* it decides no pattern's verdict, so putting it in the digest **asserts
  something false**;
* the recurring cost is the real one. A comment fix inside `harness/*.py` costs
  ~58 minutes of sweep (measured this task: 26 patterns, 3447 s sequential). **A
  documentation-hygiene tool whose own upkeep costs an hour is a tool nobody
  will keep up** — this project already has that pathology named for rung
  sources (*"THERE IS NO CHEAP DOC FIX IN ANY RUNG SOURCE"*), and there is no
  reason to build a second one deliberately.

**What it costs instead**, stated in the module docstring and in `TOOLCHAIN.md`:
nothing under `harness/tools/` may ever be imported by `check.py`, `measure.py`
or `build.py`. If it were, the digest would silently stop covering a file that
does decide a verdict. That is the whole downside, and it is one sentence.

I also checked the two alternatives before choosing: `synthesis/` is in no hash
set either (verified) but means *the outward document*, and `common/` **is** in
the digest (`common/*.py`), so it would have cost exactly what `harness/` costs.

### The five requirements

1. **`git ls-files`, not a walk** — `tracked()`. Arm 3 below proves an untracked
   file is not scanned.
2. **`.tasks/*_REPORT.md` exempt, reason in the code** — *"a report is a DATED
   RECORD of what was true when it was written; repointing its citations would
   falsify the record"*. ⚠ **I extended it to all of `.tasks/`, behind
   `--include-tasks`**, on the same argument one step weaker: a task file is a
   dated instruction, and `TASK_029.md`'s citation is literally to a path its own
   sentence says *never existed*. Default scan 77 dangling / 43 files;
   `--include-tasks` 85 / 49.
3. **Placeholders, narrow and explicit** — `PLACEHOLDER` skips a path *component*
   that is or ends in a run of capital `N`s (`pNN`, `tNN`, `TASK_NNN`).
   ⚠ **A second spelling existed and the manager's list did not have it**:
   `harness/build.py` documents its output as `.temp/build/<pNN>/<cell>-<opt>-<mode>`,
   so `TEMPLATE` skips a component that is *entirely* `<...>`. A component that
   merely *contains* one is still checked — `.temp/check/p22/miri/miri.<name>.bin`
   still resolves and p27's `irt<pid>` still dangles.
4. **An arm that must fire** — eight arms, below.
5. **Baseline: a FILE.** `--update` writes the skeleton with an **empty** `kind`
   and the check **fails** on an empty `kind`, so `--update` is not a blessing
   button. Keyed on `(citing file, path)` with the line numbers as a *list*:
   ⚠ keying on the line number would reproduce the `check.py:NNNN` rot this
   project already has a rule against, and three files cite one path from
   several lines. A count was rejected for `PROTOCOL.md` rule 13's reason.

### The acceptance run — 8 arms, 4 of which MUST fire (`.temp/t125/acceptance.log`)

Every arm backs the file up, edits it, runs, restores, and re-checks the sha256,
so a crash cannot leave a planted string in the tree.

```
[PASS] arm 0  clean tree                                rc=0  77 dangling  OK
[PASS] arm 1  MUST FIRE: planted citation in TOOLCHAIN.md
                                                        rc=1  78 dangling  FAIL (new=1)
[PASS] arm 2  count RETURNS when the plant is removed    rc=0  77 dangling  OK
[PASS] arm 3  MUST NOT FIRE: same citation, UNTRACKED file
                                                        rc=0  77 dangling  OK
[PASS] arm 4  MUST NOT FIRE: `.temp/pNN/...` placeholder rc=0  77 dangling  OK
[PASS] arm 5  MUST NOT FIRE: same plant inside a committed *_REPORT.md
                                                        rc=0  77 dangling  OK
[PASS] arm 6  MUST FIRE: one baseline `kind` blanked     rc=1  FAIL (unclassified=1)
[PASS] arm 7  a baseline entry that starts RESOLVING is REPORTED, not failed
              (recreated .temp/p36/bin/k_gcc)           rc=0  76 dangling  OK (resolved=1)
      arm 8  --include-tasks widens the scan: 77 -> 85 citations, 43 -> 49 files
ACCEPTANCE: ALL ARMS AS EXPECTED       git status afterwards: only `?? harness/tools/`
```

⚠ **And the checker caught a bug in itself before any of that.** My first draft
stripped a trailing `*` as prose punctuation, which turned
`` `.temp/review021/v05/z3_*` `` into the stem `.../z3_` and reported **two live
directories as dangling**. The comment at the strip site now says so.

---

## §B — ⚠⚠ BASELINE-AND-FREEZE, and the measurement says the cleanup was mostly a cleanup of NON-DEFECTS

**Taking the manager's own offer, and with a stronger reason than "churn".**
I read every dangling citation with its source line
(`.temp/t125/dangling_context.txt`) before deciding. **The 88 are not 88 broken
references.** Classified, all 66 entries / 77 citations:

| kind | n | what it means |
|---|---:|---|
| `destination` | **25** | the citing script **creates** the path when it runs (`mkdir -p`, `BIN=`, `--out`). Nothing to fix. |
| `regenerable` | **15** | gone, but a surviving generator or an inline recipe rebuilds it |
| `lost` | **9** | genuinely gone and not regenerable |
| `negative` | **7** | the sentence asserts the path is **wrong** or never existed |
| `promoted` | 4 | the artefact is in the tree; the note names the tree path and the repoint cost |
| `transient` | 3 | per-PID scratch that never persists by design |
| `quote` / `example` / `generated-record` | 1 / 1 / 1 | a quoted tool diagnostic; a usage-line example; a sanitizer frame inside a **generated** gate record |

⚠⚠ **The second row is the interesting one: `regenerable` is constraint 6
WORKING.** `.temp/p05/cvar/gcc-intcheck` is gone while
`.temp/p05/cvar/kernel_intcheck.c` sits beside it; the same for p12's
`d2_unsafe_nocheck` (`.rs` present), p18's Miri blob (`gen_miri_inputs.py`
present), p10c's identity builds (`unsafe.rs`, `verus.rs` present). **A dangling
binary whose source survives is compliance with *keep the generator, delete the
artefact*, not rot.** A raw dangling count therefore partly *measures obedience*
and calling it debt is backwards.

**So §B's prose edit would have touched ~40 files to "fix" 57 citations that are
already honest, and 9 that are not.** And ⚠ **every one of the 9 keeps its
evidence in the transcript beside it** — p36's two binaries are gone but the
`nm --print-size` output quoting *eight symbols, every one 0x12 / 0x0e bytes* is
in the file; p17's two cross-task builds are gone but the line records
`n_fn=135 md5_fn=532201c7… md5_raw=12fd8fac…` for both, which **is** the identity
claim; p16's 22 review inputs are gone and the sentence citing them already says
they were never in the tree and that the axis has since been re-derived from
committed blobs.

**What I did instead**, and it is the *same* remedy in one reviewable place:
each of the 66 entries carries the `(a)/(b)/(c)` annotation §B asked for —
`kind` plus a `note` that names the generator, the rebuild command, or what the
artefact showed. `--list` prints them grouped; `--list --kind lost` is nine
paragraphs and is the honest inventory of what this repo has actually lost.

**The cost of my choice, stated plainly:** a reader of `p17/NOTES.md` still sees
`.temp/p17/sweep/` with no marker beside it, and has to run one command to learn
it is gone. I judged that against ~40 prose edits to files that carry measured
numbers, each one a chance to introduce the error class this project spends most
of its review time on. **Opportunistic rule stands: annotate the citation when
the file is next opened for another reason.**

---

## §C — ⚠⚠ ALL THREE MEASUREMENT-HASHED FILES ARE FALSE POSITIVES. THE OWED-AND-COSTED LIST IS EMPTY.

I did not edit them. I also did not need to:

| file | citation | verdict |
|---|---|---|
| `patterns/p22-hash-probe/model.py` | `.temp/check/p22/miri/miri.<name>.bin` | ✅ **RESOLVES.** It is a glob; the naive regex truncated it at `<`. The files are there. |
| `patterns/p36-vtable-dispatch/verus.rs` | `.temp/p36/probe_a*.rs` | ✅ **RESOLVES.** Same artefact; 14 `probe_a*.rs` are on disk. |
| `patterns/p47-ct-compare/inputs/gen.py` | `.temp/p47/a` | ⚠ dangles, and is a **`destination`**: the docstring line is `sha256sum … > .temp/p47/a`, then `sha256sum -c`. The path is *created* by the recipe. |

**Nothing is owed against a future re-measure of p22, p36 or p47.**

⚠ **`synthesis/synthesize.py` needed no edit either.** Its `.temp/r98/treescan_{small,large}.json`
citation **resolves** under the glob rule, so `results/synthesis.md` (generated,
never hand-edited) was never publishing a dead path from it.

---

## ⚠⚠ Two premises in the task file that do not survive

**1. The figures.** *"2454 distinct `.temp/` paths cited, 88 already dangling
across 59 files"* does not reproduce. Mine, with the definition stated so it can
be re-run — `git ls-files`, minus `*_REPORT.md`, placeholders dropped:

| | task file | mine (naive regex) | mine (glob-aware, `.tasks/` exempt) |
|---|---:|---:|---:|
| distinct cited paths | 2454 | 1716 | **1441** |
| dangling | 88 | 76 | **77 citations / 53 paths** |
| files | 59 | 61 | **43** |

I tried five regex variants and two exemption sets (`.temp/t125/probe1.log`);
the closest to 88/59 is *dangling **pairs** with all of `.tasks/` excluded* =
87 / 56. Not important on its own — but the **shape** of the gap is, because it
is the same regex artefact that produced the §C false positives.

**2. ⚠⚠ `TASK_122`'s loss was NOT a dangling citation.** The task file says
*"`TASK_122` could not raise an 18.9 M `Ir` drift from sufficiency to actuality
because the probe source it needed was one of these."*

```
$ ls -la .temp/t86/cost.rs
-rw-rw-r-- 1 apt apt 6743 Aug 24 16:39 .temp/t86/cost.rs
$ git grep -n "t86/cost.rs" -- .        # ONLY .tasks/TASK_122_REPORT.md (exempt)
```

**The file is present.** `TASK_122_REPORT.md` says why that does not help:
*"`TASK_120` compared its copy to `.temp/t86/cost.rs` **as it stands today**,
which is evidence about today, not about the p40 measurement."* **The defect is
that the probe is UNVERSIONED, not that it is missing** — and this checker
resolves it and says nothing.

⚠ **The forward rule still buys that case back** — a promoted file gets git's
content pin for free — **but the DETECTOR does not.** That is stated at the top
of the tool's docstring and in `TOOLCHAIN.md` rather than left for the next agent
to discover.

**3. `TASK_121`'s five "already lost, cited by committed files a reader is meant
to be able to check" — at least three are misclassified.** `.temp/p07/twin/r4_ptr_twin.rs`
is cited by a sentence that says *it never existed*; `.temp/t89/genvar/v46_nosafety.rs`
is cited **on the line below its own rebuild command**, whose generator
(`patterns/p46-bignum-mac/controls/mkvariants.py`) is committed; the p17 mirror
`.rs` is written by a `python3 - <<'PY'` block printed immediately above it,
with a hit-count assertion so it cannot drift.

---

## The SIZE BOUND the manager asked for (least-sure #3) — measured, and the answer is "yes, it needs one"

`harness/tools/temp_citations.py --census`, so it is re-derivable from the tree:

```
cited .temp/ paths : 1441   plain file 1234 / dir 119 / neither 88
STRICT closure (cited files + everything under cited dirs): 10563 files, 3103.7 MB
WEAK   closure (paths cited AS FILES)                     :  1234 files, 1862.06 MB
  under .temp/{build,check,clausemut} (a committed script rebuilds these)
                                                             833 files, 1848.76 MB
  KEEP extensions (constraint 6's own list)                  394 files,    4.54 MB
  KEEP + not rebuilt + <= 256 KB                             393 files,    3.62 MB
  source only (.py/.rs/.c/.h/.sh), not rebuilt               315 files,    2.13 MB

committed files SCANNED, for scale: 575     (`git ls-files` total: 838)
```

**A strict forward rule is unbounded — 3.1 GB over 10 563 files — and it needs
TWO bounds, not one:**

1. ⚠ **Exempt the rebuilt directories.** `833 of 1234` cited files live under
   `.temp/build`, `.temp/check`, `.temp/clausemut`, which committed scripts
   re-derive; they are **99.3% of the bytes**. This single carve-out takes the
   rule from 1.86 GB to 13 MB and is not a compromise — constraint 6 already
   says those are not evidence.
2. **Bound to constraint 6's own KEEP extension list**: 394 files, 4.54 MB. A
   256 KB per-file cap removes one file and 0.9 MB; a `.py/.rs/.c/.h/.sh`-only
   bound gives 315 files, 2.13 MB.

⚠⚠ **The binding constraint is NOT bytes, it is FILE COUNT.** Even the tightest
bound promotes **315 files into a tree that currently tracks 838** — a 38%
increase in tracked files, all of it scratch, to buy back a class whose measured
harm this task could not find a single live instance of. **So: keep *promote,
don't publish*, but as an ON-DEMAND rule — promote when a reader is meant to
check the artefact — never as a retroactive sweep.** The size bound to write
down, if one is wanted, is *(1) + (2) + on-demand*, and (1) is doing all the
work.

---

## §D — the family, and whether it has a common fix

`TASK_121` called `results/tables/*.md`-pinned-on-the-contract the **third**
instance of *"a claim in a committed file with nothing that detects it going
false"*. This checker is a fourth — and building it made the shape of the family
visible, so here is the paragraph, with a partial answer rather than a forced one.

**The family splits in two, and only one half has a common fix.**

* **Claims about CONTENT have one**, and this project already built it four
  times: a **content pin** — `source_sha256`, `contract_sha256`,
  `derived_from_sha256`, `gate_source_sha256`. Every one is the same mechanism:
  hash what the claim depends on, store it beside the claim, compare. The
  `results/tables/*.md` gap is not a missing *kind* of instrument, it is the
  known instrument pointed at the wrong input (the contract instead of the gate
  record it was rendered from). ⚠ **And the `.temp/` case belongs here, which is
  the finding**: TASK_122's loss was a *content* failure wearing an *existence*
  failure's clothes, and it is why **promotion is the real fix and this checker
  is only the cheap half** — a promoted file is content-pinned by git itself, for
  free, forever.
* **Claims about the OUTSIDE WORLD do not.** *"`.temp/p17/sweep/` holds 340
  callgrind runs"*, *"valgrind cannot run here"*, *"vstd has no spec for
  `copy_from_slice`"* — there is nothing to hash. The only instruments are
  case-by-case: **re-run the probe** (what `asm.py::selftest` does for the pilot
  numbers), or **make the claim self-refuting when false** (a must-fire arm), or
  — cheapest and the one this task used — **write down which of the two kinds a
  claim is**, so a reader knows whether anything is watching it.

**One transferable rule, then, rather than a common fix:** ⚠ **before adding an
instrument, ask whether the claim is about content or about the world. If it is
about content, do not build a new instrument — point the existing pin at the
right input. If it is about the world, the instrument will always be a probe with
a must-fire arm, and it will always be case-by-case.** This checker is the second
kind, and its docstring says so in its first paragraph, because a reader who
mistakes it for the first kind will trust it for something it cannot do.

---

## §E — the sweep and the publishing chain

**Sequential, 26 patterns, `.temp/t125/sweep.out` (3447 s total, 57.5 min):**

```
24 × check.py: PASS
 2 × check.py: PASS-WITH-BLOCKED-ROWS      (p01 and p42)
 0 failures      (`grep -c "^ *FAIL"` == 0 in all 26 logs)
stage 9 (published table cites THIS contract): 26/26 "which is this run's"
```

⚠ `p22` shows one blocked row and still `PASS`; `p42`'s blocked count came back
**3**, at the high end of the 1-or-2 environment band the task file names. **I
did not chase it**, per instruction.

**⚠⚠ THE PREDICTION THIS SWEEP WAS RUN TO TEST, AND IT HELD:**
`source_sha256` is **byte-identical in 26 of 26 records**, and **no record gained
a `harness/tools/…` key**. That is the placement decision, measured rather than
argued (`.temp/t125/gate_identity.log`).

⚠ **A clean by-product worth recording: a gate record is NOT byte-reproducible,
and 17 of 26 differ across two runs of the same tree.** Everything that moved is
run-scoped: sanitizer `diagnostic` strings (PID and ASLR addresses),
`miri.runs[].seconds`, the *order* of equal-behaviour cell groups in
`adversarial`, and — the only one with prose consequences — `notes` lines of the
form *"opt/mode variants of this rung disagree (**N** distinct behaviours)"*,
where **N moved 3→4 on p03 and 3→2 on p23** because those cells read
uninitialised memory and print garbage. **Anyone diffing gate records must
diff them modulo those fields**, and a reviewer who treats a moved `notes` line
as a regression will be chasing UB, not a defect.

**The publishing chain, in the mandated order** (`.temp/t125/chain.log`):

```
md5 BEFORE  licence=738c21e7…  outward=902de92f…  synth=fbe0bc22…
licence.py --emit      rc=0  md5=738c21e7…   <- BYTE-IDENTICAL
synthesize.py (1)      rc=0  md5=fbe0bc22…   <- BYTE-IDENTICAL
outward_ir.py --emit   rc=0  md5=d3e04d30…   <- ⚠ MOVED
synthesize.py (2)      rc=0  md5=c199a031…   <- ⚠ MOVED, because outward_ir did
measure.py --check-stale  rc=0   52 record(s) examined, 0 STALE
```

⚠⚠ **`outward_ir.py --emit` MOVED, AND IT IS THE DOCUMENTED `±7` PHASE, NOT
ANYTHING THIS TASK DID.** The re-emit redrew the environment phase, so
`results/synthesis.md`'s calibration line moved from **190 hit / 4 miss / 14
false alarm** to **188 / 4 / 16**, and the two misses named changed from p08's
pair to **p04's `R3-R4` pair** — which is exactly the term `synthesis.md`'s own
text says is *"`0.00` at 16 of 32 environment phases and `±7.00` at the other
16"*. The licence-tag score moved `177/19/2/10` → `179/17/2/10` the same way.
**Nothing in this task is an input to either number.**

**So I restored the tree to HEAD for everything I did not intend to change**, and
kept the regenerated artefacts as evidence:

```
.temp/t125/regen/{outward_ir.json, synthesis.md, gate/}   <- the fresh draw, 2.0 MB
restored: synthesis/outward_ir.json, results/synthesis.md, 21 results/gate/*.json
          (git show HEAD:<f> > <f>, per file — no ref was touched)
```

and then **proved the restored tree is self-consistent, not merely reverted**:

```
$ python3 synthesis/synthesize.py       -> results/synthesis.md md5 fbe0bc22…  (== HEAD)
$ python3 harness/measure.py --check-stale -> 52 record(s) examined, 0 STALE
$ python3 harness/tools/temp_citations.py  -> OK (new=0 unclassified=0 resolved=0)
$ git status --porcelain
 M TOOLCHAIN.md
?? .tasks/TASK_125_REPORT.md
?? harness/tools/
```

⚠ **Manager's call, and I recommend leaving it restored.** Committing the new
draw would move two published numbers in `results/synthesis.md` for no reason
connected to this task, and `RECAP.md` quotes that line. If the fresh draw is
wanted instead, it is `cp .temp/t125/regen/outward_ir.json synthesis/ && python3
synthesis/synthesize.py`. **Expected result restated: `24 PASS + 2
PASS-WITH-BLOCKED-ROWS`, 0 failures, `52 records 0 STALE` — all three hold.**

---

## Problems

* **I violated `.memory/00-environment.md` constraint 2 once and corrected it.**
  I launched the sweep with `nohup … &`, which that constraint explicitly
  forbids (*"a job you cannot see the exit status of"*). I resolved the exact
  PIDs, read `/proc/<pid>/cmdline` for each, and killed only those — by which
  time the shell had already reaped them. The sweep was relaunched through the
  harness's own background mode, which does report an exit status. **No sweep
  ran twice and no record was written by a killed run** (`check.py` writes its
  record at the end; `git status` showed no gate change at that point).
* **The manager's three figures and two premises did not survive** (above). I
  report my own with the definition attached rather than asserting a better
  number.

## Unsure / not done

* **I did not fix a single dangling citation in prose.** That is §B's decision,
  argued above; it is a judgement, and a reviewer who thinks the 9 `lost` ones
  deserve an inline `(artefact deleted; NOT regenerable)` marker would be
  disagreeing with a trade-off, not with a measurement. The cost of doing it
  later is one gate re-run per pattern touched.
* ⚠ **`common/layout/{analyze,loopfit,q3_convergence}.py` are the one genuine
  OWED-AND-COSTED item**, `kind: promoted` in the baseline. Their usage lines
  say `python3 common/layout/loopfit.py .temp/layout/layout_p01.json`, and that
  artefact **is in the tree** at `common/layout/data/layout_p01.json` (TASK_032).
  Repointing them costs a 26-pattern sweep because `check.py` globs
  `common/layout/*.py` into every `source_sha256`. **Bundle it with the next edit
  to those files.** `common/layout/README.md`'s two copies are free to fix and I
  left them for consistency with the three scripts — the recipe's own step 1
  regenerates the file, so nobody is stuck today.
* **Nothing runs this checker automatically, and I could not fix that from
  here.** ⚠ **Recommended manager action (one line, `PROTOCOL.md` is not mine to
  edit):** put `python3 harness/tools/temp_citations.py` next to rule 10's
  dangling-report `grep`, which is the same class of pre-commit check and is
  credited with catching a real defect. **Wiring it into `check.py` was
  considered and rejected**: a tree-wide prose check inside a per-pattern gate
  makes one pattern's verdict depend on 25 other patterns' documentation, which
  `check.py`'s own `NAMED_SPELLING_SHA256` comment rejects in those words.
* **The `destination` and `negative` kinds are hand-assigned and cannot be
  re-derived.** A future agent adding a control script will trip the checker on
  its own output directory and must add a one-line baseline entry. I judged an
  auto-classifier (match `mkdir`/`--out`/`>`/`VAR=` on the citing line) to be a
  heuristic that would eventually silence a real citation; it is the obvious
  next improvement if the friction turns out to matter.
* **This is a this-box check** and cannot be otherwise while `.temp/` is
  gitignored. In a fresh clone it reports 1441 dangling citations and is useless.
* **The baseline is hand-maintained data, not a derived artefact**, so nothing
  in `.temp/` is load-bearing for it — which matters, because a checker whose
  own input lived in `.temp/` would be this task's own joke. `.temp/t125/classify.py`
  was a **one-time bootstrap**; `--update` preserves every `kind` and `note`, and
  I verified idempotence: md5 `824cb20f…` before and after a full `--update`.
* **`--census` counts a glob citation under "neither"** (neither a plain file nor
  a directory), so its 88 is not the 77 the check reports. Labelled in the
  output; not reconciled, because a glob has no size and the closures are a size
  question.

## Memory updates

**None — `.memory/` is manager-only.** Durable facts that belong there, for the
manager to land **after review**:

1. `.memory/05-layout.md`: `harness/tools/` exists, is **outside** the gate
   digest because `harness/*.py` is non-recursive, and nothing in it may be
   imported by `check.py`/`measure.py`/`build.py`.
2. `.memory/00-environment.md` constraint 6: **a dangling `.temp/` citation whose
   source survives is the constraint WORKING** (15 of 66 baseline entries). Worth
   one sentence so the next agent does not read the count as debt.
3. `.memory/03-measurement.md`: **a gate record is not byte-reproducible** —
   sanitizer `diagnostic` (PID/ASLR), `miri.runs[].seconds`, `adversarial` group
   ordering, and the `notes` *"N distinct behaviours"* line all move run to run
   on an identical tree; 17 of 26 records differed here with `source_sha256`
   identical in all 26.
4. TASK_122's loss was **unversioned, not absent** — the *existence* class and
   the *content* class are different, and only the second has a common fix
   (§D).

---

⚠ **PROTOCOL rule 2:** I was launched carrying **551**. My branch delta is
**15**: the three unreproducible figures; the two false premises (TASK_122's
loss, and §C's three files being owed); the glob-stem regex class; the
`destination` class; `regenerable`-is-compliance; three of TASK_121's five
"already lost" being misclassified; `harness/*.py` being non-recursive; the
strict-rule size bound and its file-count constraint; the trailing-`*` bug I
found in my own first draft; the checker's blind spot at the case that motivated
it; and the gate record's run-to-run nondeterminism. **551 + 15 = 566.**
⚠ **Reconciliation is the manager's job, not mine.**
