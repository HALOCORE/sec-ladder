# TASK_165 — review `TASK_164`, and attack the DEVIATION first because it is one line and the manager cannot judge it

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

⚠⚠⚠ **THIS ONE CHANGED THE GATE.** `harness/check.py` and `harness/vparse.py`
are the instrument all 33 records rest on, so a defect here does not spoil one
row — it spoils the certificate on every row. That is why this review exists
even though the sweep came back at the exact expected baseline.

⚠⚠ **AND `PROTOCOL` RULE 3 IS THE OTHER REASON: THE MANAGER DESIGNED THIS
BUNDLE**, wrote its scope, and has already landed its `.memory/` fold. **A
different agent must attack it.** Item 5 is that half and it is not optional.

Read first: `.tasks/TASK_164_REPORT.md` **in full** (901 lines);
`.tasks/TASK_164.md` (what was asked, including the two premises the manager got
wrong); `RECAP.md` **finding 63** and queue items **26** and **30**;
`.memory/03-measurement.md` entries **19** and **23**; `.memory/05-layout.md`'s
*"a `check.py` edit … IS NOT THE WHOLE COST"* section; `git show fb7cdb0` and
`git show 8273bfd` (the two commit messages — **the manager's own summaries,
and a documented place it overstates**).

✅ **YOU NEED NO SWEEP.** Every arm is a pure function or a `vparse._selftest()`
cell and can be driven **in process** — which is how `TASK_164` itself drove
stage `5e`. ⚠ **If you believe an item genuinely needs a 33-pattern run, say so
and STOP; do not start one.**

✅ **Two soundness questions are ALREADY SETTLED by the manager, so do not spend
the review on them:**
- **No record from the aborted first sweep survived.** All 33 `source_sha256`
  blocks carry the **exact** hashes of the committed `check.py` and `vparse.py`
  (manager-checked, 0 mismatches). The digest proves it; you need not re-derive.
- **The verdicts are the expected baseline**, read out of the records:
  `30 PASS + 3 PASS-WITH-BLOCKED-ROWS`, 0 failures, `blocked` `p01` 1 / `p35` 3
  / `p42` 1.

---

## 1. ⚠⚠⚠ THE DEVIATION — the engineer's own least-certain call, and the manager cannot adjudicate it

`check.py::_check_axiom_decls` **partitions the `global` kinds OUT** of the
`verus.axioms` declared-count comparison, out of the `tcb-axiom` shout, and out
of `_axiom_items`. The gate **records** them (`verus.<src>.global_decls`) and
does not **require** them to be declared.

**The engineer's two reasons, in its own order:**

1. *"A `global` is not an unchecked axiom.* The other five forms are trusted
   because **nothing** checks them. This one is const-evaluated by rustc, and
   stage 5e already fails on a lie. `_axiom_items` is the set that **mandates
   Miri**, on the argument *'the axiom is ghost but the call it licenses is
   executed'* — and Miri is not the backstop for a `global`; rustc is. Putting
   them in a list captioned *'axioms that NOTHING checks'* would be false."*
2. *"Counting them there demands a declaration on 10 patterns → **10
   `contract_sha256` moves, 10 stale published tables, 10 `report.py` runs and a
   SECOND full sweep.**"*

⚠⚠ **ATTACK REASON 1, NOT REASON 2.** Reason 2 is a cost and costs do not decide
soundness; if reason 1 is wrong then the cost is simply what the repair costs.
**The question is whether a `global` directive is trusted in the sense
`verus.axioms` means.**

- ✅ **Re-derive the four probes** (`.temp/t164/globalprobe/`, generators kept).
  Does a false `global layout` and a false `global size_of` really produce the
  identical `error[E0080]` at the identical stage with the identical exit code,
  **in verify-only mode, on a never-constructed type, and under
  `--crate-type=lib`**? ⚠ **The Verus guide says the check *"only happens when
  codegen is run"*** — the report says the pinned Verus is stricter than its own
  guide, which is a strong claim about a third-party tool.
- ⚠⚠⚠ **THE ATTACK THE REPORT DID NOT TRY: is there ANY route by which a
  `global` lie survives to a running binary?** The engineer tried three
  (never-constructed, `--crate-type=lib`, verify-only) and reports none. **Try a
  fourth it did not**: a `global` whose falsity depends on a `cfg`, a generic
  parameter, or a type alias; a `global size_of` for a type whose layout is
  `repr(Rust)`; a `global` in a file the gate verifies but `build.py` compiles
  with different flags. ⚠ **`--cfg slb_twin` is exactly such a flag and this
  project has one file per pattern compiled both ways.**
- ⚠⚠ **AND ATTACK THE STAGE-5e CLAIM AT ITS JOINT.** The engineer says
  `check.py::_verus` treats *"summary parsed and `errors == 0` and
  `returncode != 0`"* as an anomaly, and stage 5e turns it into a failure.
  **Is that true for every path a `global` lie can take, or only for the one it
  drove?** Specifically: **what happens when a `global` lie coexists with a REAL
  verification error?** Then `errors != 0`, the anomaly condition is false, and
  the run fails for the other reason — which is fine — **but what if the lie
  coexists with a stage that SKIPS Verus** (`--no-verus-mutants`, a blocked row,
  a pattern with no `verus.rs`)? **Say which stages are protected and which are
  not, by name.**
- ✅ **If the partition is right, say so plainly and say what the RECORDED-only
  form buys and does not buy.** *"The net holds"* is a finding, and it is the
  answer the manager currently believes; **your job is to make it earn that.**

## 2. ⚠⚠ DOES THE NEW STAGE-9b VERDICT READ FAIL OPEN? The arm is the ENTIRE evidence

**Exposure today is zero** — 35 CLEAN, 11 NO-VERDICT, 0 FAILED across all 46
sidecars — so **a green 33-pattern sweep says NOTHING about whether this check
can fire.** `.memory/03-measurement.md` entry 19 and `RECAP` trap 2 both name
this shape: *before believing a check, ask what would make it FAIL.*

- ✅ **`control_json_verdict()` is PURE**, so drive it directly.
  `_CONTROL_VERDICT_CASES` has **17** cells. ⚠ **Manager-verified that all 17
  pass and that the six headline shapes behave** (non-empty `problems` → FAILED;
  `summary 7 of 9` → FAILED; `9 of 9` → CLEAN; `[]` → CLEAN; a `problems` given
  as a **STRING** → FAILED, not "no problems"; no key → NO-VERDICT). **Do not
  re-run that; break it instead.**
- ⚠⚠ **Find the shape it gets WRONG.** Candidates the manager could not rule
  out: `problems` as a **dict**; `summary` with `as_expected > n`; `summary`
  missing `n`; `summary` present but `null` (**two shipped sidecars do exactly
  this** — `p25`'s and `p35`'s `proof_mutants.json`); both keys present and
  disagreeing; a sidecar that is a **list** at top level; a `problems` list of
  empty strings.
- ⚠⚠⚠ **AND THE ONE THAT MATTERS MOST: does a sidecar whose GENERATOR crashed
  half-way — leaving a truncated or partially-written JSON — read as CLEAN?**
  Stage 9b already handles `UNREADABLE`; **check that the verdict path does
  too, and that a doc missing the keys entirely is NO-VERDICT rather than
  silently fine.**
- ⚠ **The four bespoke verdict shapes it deliberately does NOT read** —
  `arms_as_designed`, `cells_ok`, `hardened_kernel_broke`, `unstable_cells`.
  **Which sidecars, and what would each miss?** ✅ **The engineer proposes the
  repair be generator-side** (have `p35`'s two emit `summary: {n, as_expected}`
  beside what they already write). **Say whether that is right, and whether four
  is really the count.**

## 3. ⚠⚠ ITEM C's DOCSTRING — every number, and the list that was ASSERTED

The engineer says *"every number in it was re-derived from `results/gate/p*.json`
by `.temp/t164/r45_null.py`, not copied from entry 23."*

- ✅ **The four-axis null table is MANAGER-RE-DERIVED and reproduces exactly**
  (`p25` 0.00/269.52, `p28` 281.28/1732.73 at `O0/iso`, `p29` 113.76/425.80,
  `p42` 0.00/−31.00, `p11` −494.00 on **small** at `O3/whole`). **Do not spend
  the review re-deriving it.** ⚠ **Do check the tree-wide counts** — *"8 of 66
  at `-O3 isolated`, 35 in `[1,2)` of which 34 are exactly `−1.00`, 23 below
  1.00"*, and *"10 of 66 at `-O0 isolated`"*, and *"37 of 66 clear 2.00 and 15
  clear 20.00 at `-O3 whole`"*. **Those are NOT re-derived by anyone yet.**
- ⚠⚠ **THE ASSERTED LIST.** The engineer first wrote *"nine patterns (p25, p27,
  p28, p29, p32, p34, p35, p47, p49) have never been probed"*, caught itself,
  and re-derived the true nine (`p23 p25 p28 p29 p32 p34 p35 p42 p49`) from
  `.temp/r98/treescan_large.json`. ✅ **Self-caught, and it disclosed the
  mechanism.** ⚠ **Check the SHIPPED list is the derived one and not the
  asserted one** — a correction that lands in the report and not in the code is
  the failure mode this project has hit before.
- ⚠ **The census block now says `2026-08-22`, 24 patterns, tree of 33.**
  Confirm both numbers against the artefact, not against the prose.
- ⚠⚠ **AND ASK WHETHER THE DOCSTRING IS NOW TOO LONG TO BE READ.**
  `check_marginal_ir`'s docstring was already the longest in the file and this
  task added to it. **A warning nobody reaches is not a warning** — say whether
  the second mechanism is findable by someone who opens the function to change
  it, or whether it is buried at the bottom of the first mechanism's essay.

## 4. ⚠ ITEM D — the twin was BUILT, so check the build

`slb_twin_copy_bytes` respelled as
`let (a, _b) = dst.split_at_mut(n); a.copy_from_slice(&src[from..from + n]);`
is reported as **`11 verified, 0 errors`**, and as a working strength oracle
(weakened → `10 verified, 1 errors`, *"precondition not satisfied"*).

- ✅ **Re-run it** (`.temp/t164/twinprobe/`, generators kept). ⚠ **Verus via
  `./verus_run.py`, single-file mode, never `--cargo`.**
- ⚠⚠ **The shipped indexed twin gives `12 verified` and the bulk twin `11`.
  WHY ONE FEWER?** The report attributes it to `twin_obligations` being a count
  of SMT query units. ⚠ **A twin that discharges FEWER obligations is exactly
  what a weaker oracle looks like** — **settle whether the bulk twin is as
  strong an oracle as the indexed one, or merely a shorter one.** ✅ **The
  weakening arm is the right test and it fired; ask whether ONE weakening arm is
  enough.**
- ⚠ **`.memory/04-verus.md:133 / :813` are cited from `p02`'s and `p06`'s docs
  and are reported STALE, one of them INSIDE `p06`'s contract fence.**
  Confirm, and price it.

## 5. ⚠⚠⚠ WHAT THE MANAGER OVERSTATED — and this half is mandatory

**The manager has been refuted in every one of the last nine tasks, and this
task file's own predecessor contained two manager errors.** Fresh places, all
landed **from an unreviewed report**:

- **`RECAP` finding 63** — long, and it separates ✅ manager-re-derived from ⊘
  engineer-only. ⚠ **Check that separation is HONEST.** Anything marked ✅ that
  the manager did not actually re-run is the defect this item exists for.
- **`.memory/03-measurement.md` entry 23's new four-axis table** and its new
  tree-wide distribution paragraph.
- **`.memory/05-layout.md`'s new harness-pin section.** ⚠ **It contains a
  confession — the manager wrote a `grep -l` recipe, ran it, got FOUR against a
  true THREE, and replaced it with a python one-liner.** ✅ **Re-run BOTH and
  confirm the confession is accurate and the replacement is right**; a wrong
  correction is worse than the error it replaces.
- **Queue items 26 and 30's closures** — item 30's says the manager's own
  scheduling sentence *"conflated two mechanisms"* and withdraws it. **Is that
  the right reading, or is it over-generous to the original?**
- **The two commit messages** `fb7cdb0` and `8273bfd`.
- ⚠⚠ **AND THE SENTENCE THE MANAGER IS LEAST SURE OF: finding 63 says stage 5e
  *"already fails on"* a `global` lie, which REFUTES `TASK_156` minor 2's *"no
  verify-only stage is protected"*. That is a refutation of published text
  written from ONE agent's in-process drive, landed by the manager the same
  day.** **If item 1 breaks it, finding 63 has to change.**

## 6. ⚠ THE PROCESS DISCLOSURES — verify them rather than accepting them

- **The sweep ran TWICE** and the engineer disclosed it as an overrun.
  ✅ **Manager-checked: no stale record survived.** ⚠ **Check the OTHER half —
  the engineer says the cost was *"wall clock only: no `contract_sha256` moved,
  no published table went stale, no `report.py` ran and no re-measure was
  needed."*** **`git show fb7cdb0 --stat` settles it; confirm no
  `patterns/*/spec.md` is in it.**
- **`p35`'s two sidecars were regenerated** with *"ZERO substantive leaves
  moved"* — only the two pinned hashes and `measured_utc`.
  ⚠ **`.temp/t164/sidecar_diff.py` is the instrument; re-run it against
  `git show fb7cdb0^:` rather than against the engineer's snapshot.**
- **`.temp/t164/p01.log` is disclosed as unusable** (two overlapping runs).
  ✅ That is the right disclosure. ⚠ **Confirm nothing in the report or in
  `RECAP` reads a number out of it.**
- ⚠ **`temp_citations.py` reports 4 baseline entries "NO LONGER DANGLING" and
  the engineer did not run `--update`.** **Say whether that is the right call
  and what the manager owes.**

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
2. **A verdict on the DEVIATION (item 1)** — should `global` be counted in
   `verus.axioms`? ⚠ **A recommendation either way is fine; an unargued *"leave
   it"* is not.** **If it should be reversed, say what the 10-pattern
   declaration would cost and whether it can ride the Results task's sweep.**
3. ✅ **CLEAN NEGATIVES ARE WORTH AS MUCH AS FINDINGS** — name the attacks that
   did not land so the next agent does not re-run them.
4. ⚠ **Is `TASK_164` FINISHED?** Not *"is the gate green"* — is there anything
   a reader would need that no artefact carries?

## ⚠ NOT in this task

- **Any fix.** You report; the manager lands.
- **`results/SYNTHESIS.md`'s Results gap** — that is the NEXT task and the
  manager's pre-task pass is already written at `.temp/mgr164/`. ⚠ **You MAY
  read `.temp/mgr164/` and, if you find an error in it, that is a finding worth
  more than most** — it is about to become a task file.
- **A 33-pattern sweep.**
- **Re-taking the ±7 environment census.**

## Rules

- `.temp/t165/` for scratch. ⚠ **Do not touch any earlier `.temp/t*/` or
  `.temp/mgr*/`** — cited evidence. **Copy out; do not modify.**
  **No `git add`/`git commit`.**
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING** — a waiter's own command line
  contains the string it greps for, so its exit condition can never be true, and
  the enclosing tool `bash -c` matches too. **Use `wait <pid>` or a `.done`
  sentinel** (`.memory/00-environment.md`).
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log**, and
  ⚠ **`rc=$?` after a PIPE reads the LAST command's status.**
- Verus via `./verus_run.py`, **single-file mode, never `--cargo`**.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`.
- ⚠⚠ **`../LearnVeri/` IS ANOTHER PROJECT'S REPOSITORY — READ ONLY.**
- ⚠ **If you plant into a tracked file, restore in a `finally:` and verify by
  BYTES against `git show HEAD:`.**
- Report to `.tasks/TASK_165_REPORT.md`. **Write the file before citing it.**

**PROTOCOL rule 2 running count: launched from 926**
(`.tasks/TASK_164_REPORT.md`'s closing paragraph, which carried 925 → 926).
⚠ **Reconciliation across branches is the manager's job, not yours.**

⚠⚠ **The one I want attacked by name is item 1's REASON 1** — *"a `global` is
not an unchecked axiom, because rustc checks it"*. The manager believes it, the
engineer believes it and named it as its own least-certain call, and **nobody
has tried to defeat it.** Two agents agreeing is not a review.
