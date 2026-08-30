# TASK_144 — build `p32`/`p33`: free-list allocator / object pool with recycling

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You may use
`harness/check.py` and `harness/measure.py`.

## The bar, because it changed and it governs everything here

`CLAUDE.md` **rule 6** and `.memory/02-bench-rules.md`'s *THE ADMISSION BAR IS
C-SIDE ONLY*. **This row is ALREADY ADMITTED** (`TASK_143`, finding 54).

> ⚠⚠⚠ **NOTHING the Rust or Verus rungs do can shrink, weaken or retire this
> row. Whatever they land on IS THE RESULT.** *"Safe Rust reproduces the bug
> bit-identically"*, *"no cost gradient"*, *"the R5 cannot state the
> obligation"*, *"Miri does not see it"* — **all are findings to REPORT.**

## What already exists — promote it, do not re-derive it

`.temp/t143/p32/` and `.temp/t143/p32m/`: `body.inc` (**included twice**, so R1
and R1h provably differ by the safety line alone — `+9/−0` preprocessed lines),
`k.c`, `safe_naive.rs`, `matrix.json`, and `.temp/t143/build.sh`,
`difflines.sh`, `matrix.py`. ✅ **Keep the include-twice construction — it is
better than the tree's convention and it makes the R1/R1h claim mechanical.**

## The headline, already measured. ⚠ Manager-re-run; ship it as a CONTROL.

**One C source, storage the only variable:**

```
input             C bug (ARENA)   C bug (MALLOC)             safe Rust     C fix
benign              37906190170      37906190170           37906190170  37906190170
adv-stale-read            31093   ABORT heap-UAF                 31093        38533
adv-recycle              962025           962025                962025       968783
adv-doublefree      28444043583            ABORT           28444043583  35593724680
```

✅ **`#![forbid(unsafe_code)]` safe Rust reproduces the BUGGY C bit for bit on
every input — including the two where the answer is WRONG — while the same
source with `malloc` storage ABORTS.** ⚠⚠ **The `malloc` arm is the control that
makes this a two-cell detector-coverage experiment rather than an anecdote.
Ship it as `controls/storage_arms.py` with a JSON sidecar and a
`derived_from_sha256` pin.**

## The C mechanism, and why it is not `p27` or `p29`

A pool of fixed-size blocks with a **LIFO free list**; a handle is a
`(slot, generation)` pair in one byte. **Nothing is malloc'd or freed per use —
storage belongs to the program throughout.** Two bug classes from one omitted
conjunct:

- **FREE with a stale handle** → the block is pushed a second time,
  `nx[h] = freehead` with `freehead == h` **self-loops the list**, so every later
  ALLOC returns the SAME slot: **two live handles ALIAS one block** and the rest
  of the list is lost.
- **READ with a stale handle** → the block was recycled; the read returns the
  **new occupant's** payload.

⚠⚠ **The ALIASING harm has no analogue in `p27` or `p29`** — that is the
C-mechanism distinction the row rests on. **State it in `spec.md`; a reviewer
will attack it first.**

## Deliverables

1. **Build `patterns/p32-...`** to `patterns/p01-array-sum/`'s structure: seven
   rungs, `spec.md` with the machine-readable `slb-contract` pins, `model.py`,
   `inputs/gen.py`, `NOTES.md`, `README.md`, `controls/`.
   **`harness/check.py p32` must PASS and `measure.py` must record it.**
   ⚠ `p33` merges into this row — say so in `spec.md` and `README.md`.
2. ⚠⚠⚠ **`model.py` MUST BE WRITTEN FROM THE CONTRACT, NOT TRANSLITERATED.**
   `TASK_136`'s was a line-by-line copy of its own kernel — same variable names,
   same guard — which satisfies the model-sandbox rule mechanically and defeats
   it in substance, and is exactly how its delete bug went undetected.
   ✅ **`p29`'s model is the good example: a structurally different formulation
   (a reachability walk). Say in `NOTES.md` how yours differs.**
3. **The R5 owes an ATTACK ARM THAT MUST FAIL TO VERIFY**, plus a **VACUITY arm**
   (a constant/trivial body that must also fail). ⚠ **`p42`'s ghost ledger
   verified `18/0` while leaking, and `TASK_136`'s ARM_C was discharged by
   `fn arm_c() -> u8 { 9 }`. Both are in this project's history; do not repeat
   them.**
4. ⚠ **If you publish any rung-to-rung cost difference, search BOTH rungs'
   spellings and count the levers on each side.** Five patterns here published a
   headline wrong in the flattering direction. **A row may ship with NO cost
   axis — `p29` does — but say so explicitly so the absence does not read as a
   zero.**
5. **Tell the manager the bug class** for `harness/tools/composition.py`.
   ⚠ **Do not edit that file.** Expect `--check` to FAIL with
   `built but unclassified` until the manager classifies it — **that is the
   check working, not a defect.**

## Rules

- `.temp/t144/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not touch `.temp/t136/ t137/ t139/ t140/ t141/ t142/ t143/`** — all
  cited evidence. **Copy from `t143/`, do not modify it.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`. ⚠ Grep
  `~/tools/verus/vstd/std_specs/` **specifically** before any "no spec exists".
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; **every harm probe owes a positive control that must fire.**
  ⚠ **`TASK_143` had clang ELIMINATE one of its positive controls** — a
  malloc-elision artefact `p31` also hit. **Check your controls actually run.**
- ⚠ **Read `blocked` out of the RECORD, never `grep` the log.** Expect
  `p01 = 1`, `p42 = 1`.
- ⚠⚠ **Stage 9c was repaired at `TASK_141` but the ordering still matters:
  if the gate fails on `[tables]`, run `harness/report.py pNN` and re-gate.**
- ⚠ **Generate control JSONs AFTER the sources are final** — `TASK_139` edited
  doc comments after generating them and paid a re-measure.
- Keep the generator, delete the artefact (`.memory/00-environment.md`
  constraint 6).
- Report to `.tasks/TASK_144_REPORT.md`. **PROTOCOL rule 2: you carry 711.**
