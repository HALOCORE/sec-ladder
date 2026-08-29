# TASK_139 — `p29`: re-settle two design questions on a stated criterion, then BUILD

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You may use
`harness/check.py` and `harness/measure.py`.

`p29` is **the only live row in this project** and it is **cleared to build**
(`TASK_137`). ⚠ **But not on `TASK_136`'s design as written, and this task file
deliberately does NOT quote RECAP findings 47/49/51 as they stood — three
sentences in them were false and are now struck. Read the CURRENT text.**

Read first: `.tasks/TASK_137_REPORT.md` **in full** (the review that cleared the
build and re-opened the design), then `.tasks/TASK_136_REPORT.md`;
`RECAP.md` findings **49 and 51** *as they now read*; `.memory/06-catalogue.md`'s
`p29` cell; `.memory/02-bench-rules.md` last section; `patterns/p01-array-sum/`
(the template) and `patterns/p27-handle-table/` (the other temporal row).

## What is SETTLED. Do not re-litigate these.

- ✅ **The row is admissible, on LIMB 1** — a new operator on the safety line.
  **`p27`'s read-path line needs ONE conjunct (liveness); `p29`'s needs TWO
  (liveness AND occupant identity).** ⚠ **That is the row's headline. It is
  stronger than the limb-4 framing it replaces — do not revert to *"the safe
  rung is silently wrong"* as the headline.**
- ✅ **The safe rung is `Option<Box<Rec>>` with slots NEVER recycled**, and the
  reason is now stated rather than aesthetic: the third spelling
  (`Vec<Node>` + free list) is **bit-identical to buggy C on BOTH halves**,
  which is verbatim `p32`/`p33`'s already-REFUSED result. ⚠⚠ **Choosing it would
  retire the row. It is not a presentational choice.**
- ✅ **`H2` is exact for a reason, not by luck** — a fixed record's key is
  monotonically increasing under substitution, so it can never re-acquire its
  found key; and the delete cursor visits exactly the victim and the successor.
  **Put that argument in `spec.md`; it is worth more than the fuzz count.**
- ✅ **`p25`'s *"nondeterministic R1"* kill does NOT apply** — 19-of-20 distinct
  on use-after-free inputs, **1 of 20 on recycle inputs**.

## Deliverable 1 — settle the SAFETY-LINE SITE on a STATED CRITERION

⚠⚠⚠ **There are now TWO exact candidates and `TASK_136` compared only one
family.** Both are measured exact; the choice must be argued, not fuzzed.

```
H2  write path, one site   null the saved handle at the LOCATED VICTIM   exact 1511/1511
T3  read  path, O(1)       && live[g_slot] == 1 && tab[g_slot][0] == g_key
                                                exact 614/614, 0 ASan lines
```

**State the criterion FIRST, then apply it.** ⚠ **Candidate criteria, and you
should say which you are using and why:** which one is the *idiomatic C
omission* a real program makes; which produces an R1h that differs from R1 by
the **safety line and nothing else**; which makes `p29`'s two-conjunct headline
**visible on the line itself** (⚠ **`T3` does — it is literally `p27`'s conjunct
plus one more; that is an argument FOR it, and you should weigh whether it is
the decisive one**); and which the R5 can state.

## Deliverable 2 — settle whether `tab[]` is NULLED on free

⚠⚠ **`p27`'s own `c/kernel.c` argues BY NAME that nulling the table slot on free
turns the bug into a different class.** `TASK_136` pinned `p29` without
reconciling that. **Read `p27`'s argument, decide, and record which way and
why** — this interacts with deliverable 1, because `T3` reads `tab[g_slot]`.

## Deliverable 3 — BUILD `p29`

Clone `patterns/p01-array-sum/`'s structure: seven rungs, `spec.md` with the
machine-readable `slb-contract` pins, `model.py`, `inputs/gen.py`, `NOTES.md`,
`controls/`. **`harness/check.py p29` must pass, and `harness/measure.py` must
record it.**

⚠⚠⚠ **`model.py` MUST BE WRITTEN FROM THE CONTRACT, NOT TRANSLITERATED.**
`TASK_136`'s `p29c/model.py` REMOVE is a **line-by-line transliteration** of its
`kernel.c` — same variable names (`cur`, `par`, `goleft`, `guard`, `sp`, `s`,
`sgoleft`), same `guard < CAP + 1`, same cursor move. **That satisfies the
model-sandbox rule mechanically and defeats it in substance, and it is exactly
how the engineer's first delete-by-substitution bug went undetected: the model
mirrored the same error and the two agreed.** ✅ **Write the model as a
REACHABILITY WALK or another structurally different formulation, and say in
`NOTES.md` how it differs from the kernel.**

⚠⚠ **THE R5 OWES AN ATTACK ARM THAT MUST FAIL TO VERIFY.** ✅ **You start from a
verified BST** — `.tasks/TASK_095_REPORT.md`, `9 verified, 0 errors`, TCB 0,
three-case `remove` with in-order successor. ⚠ **And note what `TASK_137`
established: a value-equality `ensures` of the shape 26/26 fences pin DOES
reject the recycle bug, and a stale permission is `E0502`. So the R5 is expected
to work — the risk is not a linearity gap, it is a TRANSLITERATED FOLD.**

⚠ **No performance headline.** The row's result is the safety line, not a cost
gradient. **If you publish any rung-to-rung difference, search BOTH rungs'
spellings and count the levers on each side** — five patterns here have
published a headline wrong in the flattering direction.

⚠⚠ **If a deliverable-1 or -2 answer makes the row unbuildable, STOP AND REPORT.**
That remains a real result and is worth more than a forced build.

## Rules

- `.temp/t139/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not edit `.temp/t136/` or `.temp/t137/`** — both are cited evidence.
  Copy what you need. **Do not edit a shell script while `sh` is executing it.**
- Verus via `./verus_run.py`, single-file mode, **never `--cargo`**.
- ⚠ Grep `~/tools/verus/vstd/std_specs/` **specifically** before any "no spec
  exists" claim.
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; every harm probe owes a **positive control that must fire**.
- ⚠ **Read `blocked` out of the RECORD, never `grep` the log.** Expect
  `p01 = 1`, `p42 = 1`.
- ⚠ **A gate record is not byte-reproducible** — sanitizer `diagnostic` strings,
  `miri.runs[].seconds`, adversarial group order and the `N distinct behaviours`
  note move on their own. Do not report those as consequences of your work.
- ⚠ **Shipping `p29` moves what `harness/tools/composition.py` derives.** Do NOT
  edit that file; **tell the manager the bug class** and the manager classifies
  it and updates the published table.
- Report to `.tasks/TASK_139_REPORT.md`. **PROTOCOL rule 2: you carry 672** —
  reconciled by the manager from three branches off 664 (`TASK_137` +5,
  `TASK_138` +3, disjoint). Close with your branch delta and the sum.
