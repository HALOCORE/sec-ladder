# TASK_161 — build `p49`: interned / deduplicated string pool (the LAST admitted row)

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You may use
`harness/check.py` and `harness/measure.py`.

Read first: `.temp/mgr161/NOTES.md` **in full** — the manager's pre-build pass,
**and it names a defect the build would otherwise inherit**; then
`.tasks/TASK_160_REPORT.md`; `.temp/t160/red/k40304.c` and `.temp/t160/red/run.sh`;
`.memory/06-catalogue.md`'s **Family I** `p49` row; `RECAP.md` finding **61**;
`CLAUDE.md` **rule 6**; `.memory/03-measurement.md` entries **19–23**;
`patterns/p34-refcount-stack/` and `patterns/p25-realloc-growth/` as the two most
recent structural templates.

## The bar — already met, and this is a BUILD

`CVE-2022-40304` was **admitted at `TASK_143`** and **re-adjudicated and UPHELD
at `TASK_160` BY RUNNING IT** against the 32-row tree. **The C demonstration is
DONE**: 120 cells × 20 runs, `n_distinct = 1` in all 120, every hardened arm
silent in 12/12, positive controls firing on both compilers.

> ⚠⚠⚠ **NOTHING about Rust, Verus, Miri, a cost gradient or what the ladder can
> "price" may shrink or retire this row. Whatever the Rust and Verus rungs land
> on IS THE RESULT.** ✅ **C-side duplication of a BUILT row is the only kill,
> and it was adjudicated one task ago.**

## The C mechanism, and why it is a new shape

Content under a length threshold is **INTERNED — deduplicated** — so two records
*correctly* share one buffer. The cycle-breaker then **WRITES THROUGH IT**,
silently rewriting the other record's value.

⚠⚠ **NOTHING IS FREED, EVERY INDEX IS IN BOUNDS, AND ASan AND UBSan ARE BOTH
SILENT ON EVERY CELL — THE CHECKSUM IS THE ONLY INSTRUMENT.** ✅ **That is the
exact INVERSE of `p34`'s detector-only cell** (checksums agree bit for bit and
ASan is the only discriminator). **The two rows bracket *which instrument sees
the harm* from opposite ends; say so, because neither could be written without
the other.**

✅ **A FOURTH REPAIR-SITE POSITION — PROVENANCE / MUTATION.** `p27`/`p29`/`p32`
fix the READ; `p28` the DESTROY; `p34` the ACQUIRE; `p49` the **write through a
pointer the record does not own**. ⚠ **Its nearest built row is `p32` and it
INVERTS: `p32`'s alias is created BY the bug and its line asks a LIFETIME
question; here the alias IS THE CONTRACT and the line asks an OWNERSHIP one.**

## ⚠⚠⚠ THE DEFECT YOU MUST FIX BEFORE MEASURING ANYTHING

`.temp/t160/red/k40304.c` sets `K_CLEN 3` and `K_THRESH 5`, so
`if (K_CLEN < K_THRESH)` is **`if (3 < 5)` — a compile-time constant** and the
non-interned branch is **dead in the bug rung**. Therefore:

- the `INLINE_THRESHOLD`, which is **the CVE's own precondition**, is never
  exercised; and
- ⚠⚠⚠ **`r_shared[i]` is ALWAYS `1`, so the copy-on-write safety line's guard
  `if (r_shared[i])` CAN NEVER BE FALSE. That is `.memory/03-measurement.md`
  entry 19 exactly — a check that is a TAUTOLOGY of the representation it is
  written over — the defect found on `p32` at `TASK_145`, where a guard fired
  0 times in 20 000 fuzzed windows.**

✅ **DERIVE THE CONTENT WIDTH FROM THE INPUT** so both branches are live and
`r_shared` genuinely varies. ⚠ **Then MEASURE how often the guard is false and
publish it** — a guard that can fire and does is the whole difference. ⚠ **Do
this before any measurement; it moves every checksum in the row.**
⚠ Note the probe that did *not* settle it: `objdump | grep -c 'call.*memcpy'`
reads `0` at both levels because gcc inlines the 3-byte copy. **The source-level
fact decided it; the object-level one could not.**

## ⚠⚠ THE THREE TRAPS `TASK_160` MEASURED — do not rediscover them

1. **The safety line is `cow` (`+12/−2`), NOT the upstream `intern` spelling
   (`+3/−10`).** ⚠ **Upstream CHANGES A BENIGN OBSERVABLE** — `9 passed,
   1 failed` on the port's own tests, `"interned":true → false` — while **`cow`
   is byte-identical to `bug` on benign**. ✅ **An upstream patch is not
   automatically a safety line; check it against the benign observable.**
   ⚠ The reduction ships `SLB_HARDEN == 2` as the provenance/upstream spelling —
   **keep it as a `controls/` arm and price it, do not ship it as R1h.**
2. ⚠⚠ **DO NOT PORT `pool_reclaim_owner` AS-IS.** `lib.c` 229–236 writes
   `free(e)` **twice, three lines apart**, and **gcc diagnoses it with no input**
   (`warning: pointer 'e' used after 'free'`). **`TASK_143`'s *"the double free
   is emergent, never written"* is FALSE.** ⚠ **Stage `7h` passed in the
   demonstration only because the safety line makes that `free` UNREACHABLE, not
   because it is gone. A hardened arm that is clean for the wrong reason is
   exactly what `7h` exists to catch.**
3. **Keep the dict INSIDE the kernel** (`p27`'s precedent), or the deduplication
   — which IS the row's distinction — is lost. ✅ The reduction already does.

## ⚠⚠ THE CLASS IS OPEN AND THE MANAGER HAS NO SETTLED ANSWER

`harness/tools/composition.py --check` will FAIL with `built but unclassified` —
**that is the check working.** ⚠ **Do not edit that file.** **Two candidates and
both are defensible:**

- **`aliasing`** — *"two live references to overlapping storage, one of them
  mutable"*, `p08`'s declared class, which describes `p49` **word for word**.
  ⚠⚠ **SO THE SHARPEST QUESTION A REVIEWER WILL ASK IS WHETHER `p49` DUPLICATES
  `p08` C-SIDE. Answer it in your own `NOTES.md`, in the row's own words, with
  the C quoted from both.** The manager's reading — **attack it**: `p08`'s
  overlap is *within one operation* and is UB; `p49`'s sharing is by design,
  correct, and **not UB at all**, and the bug is the write-through.
- **`logical`** — *"wrong answer, memory-safe throughout"*, which `p49` also
  satisfies literally (`p04`/`p06`/`p19`).

✅ **State the case for BOTH and propose one. The manager decides; the reviewer
attacks.**

## ⚠⚠ NEW OBLIGATIONS `TASK_143`-era task files do not mention

- **(a) stage `7h`** — R1h must be sanitizer-CLEAN on EVERY input, adversarial
  included; **it cannot be declared away.**
- **(b) `spec.md` must declare `verus.assumptions[<src>]`** if any rung uses
  `assume(` or `admit(`, or the source is a hard FAIL.

## Deliverables

1. **Build `patterns/p49-interned-pool/`** (confirm or improve the name) to
   `p01-array-sum/`'s structure and `p34`/`p25`'s recent example: seven rungs,
   `spec.md` with the machine-readable `slb-contract` pins, `model.py`,
   `inputs/gen.py`, `NOTES.md`, `README.md`, `controls/`.
   **`harness/check.py p49` must PASS and `measure.py` must record it** — or the
   gate must fail for a reason you have isolated and reported.
2. ⚠⚠⚠ **`model.py` IS THE ONLY INSTRUMENT ON THIS ROW, WHICH IS NEW.** Every
   other pattern has a detector as a second witness; here ASan and UBSan are
   silent everywhere, so **the model carries the whole result.**
   **(i) NOT TRANSLITERATED** — the independent formulation is an explicit
   `(record → buffer id)` map with a shared/owned flag, not a copy of the
   kernel's pointer arithmetic. **(ii) NO CHECK THAT IS A TAUTOLOGY OF THE
   MODEL'S OWN REPRESENTATION** (entry 19) — ⚠ **and you have already been
   handed one instance of that defect in the reduction; do not reproduce it in
   Python.** ✅ **`sanitizer_expect` is `clean` on EVERY input including the
   adversarial ones — DECLARE it and say plainly that this row's harm is
   invisible to every detector the gate runs.**
3. **The R5 owes an ATTACK arm that must FAIL and a VACUITY arm.** ✅ `p32`'s
   three-cell battery is the shape, extended by `p35`'s `X1` and `p34`'s `Z1`:
   **delete the central obligation and see whether anything but a hand-written
   pin notices.**
4. ⚠⚠ **THE COST AXIS — THE FLATTERING-DIRECTION TRAP HAS FIRED SEVEN TIMES.**
   Search **both** rungs' spellings, count the levers on each side, name the
   weaker-searched endpoint, **give every figure at BOTH optimisation levels**
   (`p35`: the comparison can reverse) and **name the inline mode**. ✅ **`p34`
   and `p25` are the standard: ship a CONTROL that makes the search
   re-derivable.** ⚠ **You have TWO repair spellings here (`cow` and
   `provenance`) — price both, as `p34` prices its two repair sites.**
   ✅ **A row may ship with NO cost axis — say so explicitly if it does.**
5. **Tell the manager the bug class** (above). ⚠ **Do not edit
   `composition.py`.** Propose the wording; do not apply it.
6. **PROTOCOL definition-of-done rule 6: record the `slb-contract` block's
   sha256 in `NOTES.md` the moment you first write it**, with the words *"as
   first written, before any measurement"* — ⚠⚠ **AND KEEP THE BLOCK TEXT
   VERBATIM, NOT ONLY THE HASH.** `p34`'s first contract move proved
   unreconstructible six ways; `TASK_156` fixed the standard. ⚠ On a new pattern
   `git show HEAD:` is **vacuous** — say so rather than citing a command that
   cannot fire. ⚠ Before finishing, **re-read the hashed `why` against your own
   measured numbers**: rule 6 does nothing about a declaration measurement has
   since falsified, and both `p34` and `p25` shipped a false sentence inside a
   matching hash.

## Rules

- `.temp/t161/` for scratch. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md`, or `harness/tools/composition.py`.** No `git add`/`git
  commit`.
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — all cited
  evidence. **Copy from `t160/` and `mgr161/`; do not modify them.**
- ⚠⚠ **`../LearnVeri/` IS ANOTHER PROJECT'S REPOSITORY — READ ONLY.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`. ⚠ Grep
  `~/tools/verus/vstd/std_specs/` **specifically** before any "no spec exists".
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; **every harm probe owes a positive control that must fire — in
  the detector whose column it licenses.** ⚠ **On this row every detector is
  expected SILENT, so the positive control is the ONLY thing standing between
  "silent" and "not linked in". It is load-bearing here in a way it is not
  elsewhere.**
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log**, and
  ⚠ **`rc=$?` after a PIPE reads the LAST command's status.** Expect
  `p01 = 1`, `p42 = 1`, `p35 = 3`; `p42` may legitimately be 2.
- ⚠⚠ **If the gate fails on `[tables]`, run `harness/report.py p49` and
  re-gate.** ⚠ **A `why` rewrite moves `contract_sha256` and the published table
  cites it, so a late `why` edit costs TWO gate runs** (`TASK_156` measured it).
- ⚠ **Generate control JSONs AFTER the sources are final** — `c/*`, top-level
  `*.rs`, `model.py` and `inputs/gen.py` are MEASUREMENT-HASHED and `measure.py`
  hashes them **above** the loop. ⚠ **Stage 9b's sidecar deadline is SEPARATE
  from `measure.py`'s** — `TASK_157` lost a gate run to exactly that.
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING** — a waiter's own command line
  contains the string it greps for, so its exit condition can never be true.
  **Use `wait <pid>` or a `.done` sentinel** (`.memory/00-environment.md`).
- **Keep the generator, delete the artefact** ⚠ **and a generator that edits
  source by string substitution MUST ASSERT ITS SUBSTITUTION COUNT.**
- Report to `.tasks/TASK_161_REPORT.md`.

**PROTOCOL rule 2 running count: launched from 914**
(`.tasks/TASK_160_REPORT.md`'s closing paragraph). Carry it forward.
⚠ **Reconciliation across branches is the manager's job.**
⚠⚠ **The manager has been refuted in every one of the last six tasks — the
last time by reading a value out of the wrong column of a table. The calls to
attack here are the `p08`-distinctness argument and the claim that deriving the
content width from the input is a SMALL change.**
