# TASK_086 — probe 8–10 catalogue rows and return a RANKED QUEUE

**Role: research engineer (selection probe).** You are **not** building
anything. You are producing the **pipeline** — a ranked, evidenced queue of rows
worth building — so that pattern selection stops being a one-row-at-a-time
bottleneck that the manager keeps getting wrong.

Read `.tasks/PROTOCOL.md` first, then this file, then
`.memory/06-catalogue.md` — **all of it**, but especially the section
**"⚠⚠ THE LADDER TEST"**, which carries the three probes you will apply, *and*
carries the retraction of its own first version. Then `RECAP.md`'s **"Pattern
selection"** and **"Throughput"** box rows, and its **item 4** under *"the three
things most likely to waste your time"*.

Scratch in `.temp/t86/` — free, I checked. ⚠ **`.temp/pNN` in this tree is
ambiguous between pattern NN and task NN**; `ls` any scratch path before naming
it.

---

## ⚠⚠ 0. TWO OTHER AGENTS ARE WORKING. STAY IN `.temp/t86/`.

`TASK_084` is editing `harness/check.py`, `harness/vparse.py`,
`synthesis/synthesize.py`, two pattern docs, and writing `results/gate/*.json`.
`TASK_085_REVIEW` is working in `.temp/r85/`.

- **Do NOT run `harness/check.py` or `harness/measure.py`.**
- **Write NOTHING outside `.temp/t86/`.** Reading anything is fine.
- Read `check.py` via **`git show HEAD:harness/check.py`** — the working tree is
  half-edited.
- `./verus_run.py <file.rs>` **single-file mode is concurrency-safe**. **Not
  `--cargo`.**
- The box has **80 cores and a load average near 1**, so build in parallel
  freely; you are not competing for CPU.

---

## 1. Why this task exists

**The last five tasks produced zero new patterns.** 22 are built, **23 rows are
available** (`48 − 22 built − 3 REFUSED`), and the measured cost is **three
tasks per pattern**. Selection is the bottleneck.

⚠⚠ **And it has failed the same way twice, both times the manager's fault.**
Both axis proposals the manager made were refused, and **both died on the same
finding: the axis's own distinguishing justification was false, and one `grep`
plus one run settled it each time.** `p48`'s was *"no pattern exercises
`is_init`"* — p27 exercises it in four places. `p31`'s was *"provenance — the
property Miri checks and nothing else does"* — Miri **warns** on the round-trip
and **errors only on aliasing**, which is p08's shipped class. **Both were
written from source reads and vstd greps with NOTHING RUN.**

Then `TASK_083_REVIEW` did it properly: it cleared **four rows in part of one
session** with the three probes and returned a *ranked queue* rather than a
single guess. **That is the method. You are scaling it.**

⚠ **The scaling is not free of the same trap.** If you triage 10 rows by reading
the catalogue and arguing, you will produce 10 confident wrong answers instead of
1. **Every row you rank must carry at least one thing you RAN.**

---

## 2. Which rows

**Available (23):** `p15 p19 p20 p21 p23 p24 p25 p26 p28 p29 p30 p32 p33 p34
p35 p37 p39 p40 p41 p42 p43 p44 p46`

**Already decided — do NOT spend a probe on these:**

- **`p15`** — under decision now; a probe recommends refusal
  (`.tasks/TASK_085_REPORT.md`). Out of scope.
- **`p42`** (`goto cleanup` leak) — `TASK_083_REVIEW` triaged it **Refuse with a
  measurement**: *"`Ir` sees the leak with the wrong sign."* Out of scope.
- **`p25`** (`realloc` growth) — triaged **Defer**: the stale-pointer harm is
  p27's, measured at the detector. Include only if you think that triage is
  wrong, and say why.
- **`p23`** (quicksort partition) — **already probed and ranked 2**; its
  permutation invariant verifies **`2 verified, 0 errors`** at the pin with no
  `assume`. ⚠ **Do not re-probe the invariant. DO probe what
  `TASK_083_REVIEW` named as its kill risk and did not run: the partition
  LOOP's invariant** — the multiset preserved while two moving indices partition
  the range. That is the whole risk and one run tells us a lot.

**So: choose 8–10 from the remaining 19, plus p23's loop probe.** ⚠ **The choice
is YOURS, not the manager's** — manager-chosen rows are 0 for 2. Spread across
families rather than clustering; say in one line why you picked each.

⚠ **One preference, stated as a preference and not a rule, to be overridden by
evidence:** **the tree's bug classes are heavily concentrated — `index >= len`
is now FOURTEEN of them.** A fifteenth is not disqualifying (p36 shipped the
twelfth and was worth building) **but a row whose harm is something else is
worth more, all else equal, and any row you rank must NAME its class and say
which existing pattern shares it.** ⚠ **The novelty of the bug class predicts
neither way — the ladder test does.** Do not let this preference override a
probe result.

---

## 3. The three probes — apply all three to every row you rank

From `.memory/06-catalogue.md`. ⚠ **Use the CURRENT version. The "LADDER TEST"
that preceded it was retracted one task after it was written** — it
misclassifies **p08** (satisfies it, shipped) and **p47** (violates it, shipped)
**in opposite directions**.

1. **A rung boundary must exist somewhere, and the row must NAME it.** p08's is
   at compile time, p47's is inside the safe class, p16's is a slope. *"Safe
   Rust pays a bounds check"* is not naming it.
2. **The rungs must differ AS MACHINE CODE.** Extract each candidate kernel's
   bytes and `md5` them. ⚠ **Not** the retracted "two symbols in one section"
   form, which cannot fire when every rung is its own binary. `p45` was killed
   by this probe; `p15` passed it (206 B vs 146 B).
3. **Any published `0.00` must name its axis and `Ir` convention IN ADVANCE.**

**And a fourth, new since `TASK_085` and mandatory for every row:**

4. ⚠⚠ **DOES THE ROW'S UNSAFE OPERATION HAVE A `vstd` SPEC?**
   `check.py::_scan_unsafe_sites` requires every `unsafe` token in a pinned
   Verus source to sit inside a `#[verifier::external_body]` item. Measured:
   **47 `unsafe` tokens across 22 `patterns/*/verus.rs`, all inside
   `external_body`, zero outside**, and `grep -rn "get_unchecked"
   ~/tools/verus/vstd/` → **0 hits**, so every existing wrapper was
   unavoidable. **`p15` is the first row where vstd DOES spec the operation
   (`str::from_utf8_unchecked`), and that is precisely why it is blocked.** So
   for each row: **`grep` the pinned vstd (`~/tools/verus/vstd/`) for the
   operation the R4 rung needs.** A hit means the row inherits p15's obstacle
   and must say so; a miss means it takes the ordinary wrapper route.
   ⚠ **Grep the PINNED vstd, not `../LearnVeri/_VERUS_DOC_/vstd/`**, which is a
   different, older snapshot that produced a false "no spec exists" claim that
   stood for 44 tasks. **And grep the INHERENT spelling as well as the free
   one** — `core::str::from_utf8_unchecked` is `is not supported` while
   `str::from_utf8_unchecked` verifies `2/0`.

---

## 4. What to return

A **ranked queue**, best first, one block per row:

- **the named rung boundary** (probe 1);
- **the machine-code difference**, with the two `md5`s and sizes (probe 2);
- **the cost axis and its `Ir` convention**, declared in advance (probe 3);
- **the vstd-spec answer** (probe 4) and what it implies;
- **the bug class, named, and which existing pattern shares it**;
- **the kill risk, in one sentence** — the thing most likely to burn a session;
- **a verdict**: `BUILD` / `FALLBACK` / `DEFER` / `REFUSE`, with the measurement
  behind it.

⚠ **Say explicitly which rows you did NOT probe and why**, so the next selection
task does not re-derive it. And ⚠ **a `REFUSE` with a measurement is a GOOD
outcome** — three rows have been refused and all three were the right call.

⚠ **State novelty as a QUESTION you measured, never as a fact.** *"The first
termination proof in the project"* was a manager sentence in a task file; it was
**false**, the engineer had no reason to doubt it, and it shipped into **eight
places, two inside `contract_sha256`** — a review and a re-gate to remove.
**PROTOCOL rule 9 protects `.memory/` from unreviewed findings and protects
NOTHING from the task file itself.**

---

## 5. Constraints

- `.temp/t86/` only. No `/tmp`. **Keep the generator, delete the artefact** —
  sources, probes, `.json` and logs stay; binaries go. If a blob has no script
  that rebuilds it, write one.
- **Notes in `.temp/t86/NOTES.md` as you go.** Agents here die to transient API
  errors; the ones who kept notes lost nothing.
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only. Report durable facts; do not write them.
- `timeout <N> <cmd>` on anything long. Never `pkill`/`killall`.
- Do not bump the Verus/vstd pin. Do not edit `pilot/`.
- Do not widen scope: **rank rows, do not start building one.**

---

⚠ **PROTOCOL rule 2's running count is 237.** **Every agent that has
contradicted the manager with a measurement has been right, 237 times.** The
calls I am least sure of here: **that `p23` is really the best fallback** (it was
ranked by one agent on one probe, and its loop invariant — the actual risk — has
never been run), and **the §2 preference against a fifteenth `index >= len` row**,
which is a taste I am imposing and which the catalogue's own text says predicts
neither way. **Contradict either with a measurement and say so.** Carry **237**
forward incremented by what you find.
