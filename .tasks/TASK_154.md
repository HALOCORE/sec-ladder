# TASK_154 — build `p34`: manual reference counting (the TEMPORAL axis's fifth row)

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You may use
`harness/check.py` and `harness/measure.py`.

Read first: `.temp/mgr149/NOTES.md` **in full** (the manager's re-verification —
it carries a proof and a cell `TASK_143` did not have); `.memory/06-catalogue.md`'s
`p34` cell **rather than `TASK_143_REPORT.md`**, which the cell corrects;
`patterns/p32-free-list-pool/` and `patterns/p35-tagged-union/` as the two most
recent structural templates; `RECAP.md` findings **53–58**; `CLAUDE.md` **rule 6**;
`.memory/03-measurement.md` entries **19–22**.

## The bar, because it is the whole reason this row exists again

`CLAUDE.md` **rule 6** and `.memory/02-bench-rules.md`'s *THE ADMISSION BAR IS
C-SIDE ONLY*. **ADMITTED at `TASK_143`, ranked 4th of 7.**

> ⚠⚠⚠ **THIS ROW WAS REFUSED TWICE AND BOTH REFUSALS WERE LADDER-SIDE.**
> *"There is no working leak detector for the C rungs on this box"* (**dead** —
> `__lsan_default_options()` returning `use_stacks=0` costs one line and zero
> `Ir`); *"the safe rung leaks only in the `Rc`-both-ways spelling and `Weak` is
> equally idiomatic"*. **Neither may be reused, and nothing the Rust or Verus
> rungs do may shrink, weaken or retire this row.** Whatever they land on **is
> the result.**

⚠ **And the LEAK class is NOT this row.** `.memory/01-ladder.md`'s outcome 4
(*the safe rung is worse than C*) is scoped to the statically-asymmetric DLL
case. **`p34` here is the PREMATURE-FREE class only.** If you find the leak
cheap to observe alongside, report it as adjacent; **do not widen the row to it.**

## What already exists — promote it, do not re-derive it

`.temp/mgr149/{NOTES.md,repro.sh,build.sh,difflines.sh,common/,p34/{k.c,body.inc}}`.
✅ **Manager-re-run today, every figure identical**, and `repro.sh` runs ASan on
**both** arms on **all four** inputs (the `p28d` lesson — *run the detector on
the arm you EDITED*). ✅ **Keep the include-twice construction** (`body.inc` with
`SLB_HARDEN` 0 and 1), and ⚠ **put it in `controls/` and measure the shipped
preprocessed files, as `p32` and `p35` do** — applying it to the rungs removes
the C kernel bodies from `forbidden_verdict`'s text scan.

## The C mechanism, and why it duplicates nothing

Every object carries its own `rc`. `POP` decrements and frees at zero. `DUP`
publishes a **second reference** — and R1 omits the matching `rc++`.

```
p27  the free discipline is correct; the READ does not ask.        Fix the READ.
p29  the free discipline is correct; the READ does not revalidate.  Fix the READ.
p34  THE READ IS CORRECT AND ASKS NOTHING WRONG.  A refcounted pointer is valid
     by construction; it is the ACQUIRE that broke the invariant.
```

**The safety line is nowhere near the harm site**, and no check on the read path
could repair it without becoming a liveness table. **The free happens EARLY
rather than the read happening LATE** — a different C program with a different
repair site. `p32` is the furthest thing from it in the tree: `p32` allocates
nothing at all. ✅ **Safety line: `+1 / −0` preprocessed lines** — the smallest
in the tree; re-derive it with `difflines.sh` and publish the figure.

## ⚠⚠⚠ HEADLINE 1 — THE BENIGN COST GRADIENT IS `0.00` BY CONSTRUCTION, AND IT IS PROVED

Not searched — **proved, in two lines** (`.temp/mgr149/NOTES.md` §1):

> The safety line `t->rc = t->rc + 1` is the **only increment in the kernel**, so
> in R1 every object's `rc` is permanently `1`. Any executed `DUP` therefore
> leaves **two stack entries naming a one-reference object**, and the two
> releases that must follow (each entry is released exactly once, by `POP` or by
> the epilogue) go `1 → 0` — *`free`* — then `0 → underflow`, **reading `o->rc`
> out of a freed block.** There is **no** input on which the safety line executes
> and R1 stays memory-safe.

✅ And the tree's own convention closes it, **measured**: across 28 gate records
and 211 per-input sanitizer rows, **54 declare `expect = fires` and every one is
on an `adversarial-*` input.** So *safety line executes ⇒ ASan trips ⇒ the input
is adversarial ⇒ **no matrix input executes the safety line***.

⚠⚠ **THIS IS A HARD CONSTRAINT ON `inputs/gen.py`: NO MATRIX INPUT MAY CONTAIN A
`DUP` OP.** Verify it mechanically over the generated blobs, do not assume it.

⚠⚠⚠ **AND `0.00` IS A PREDICTION, NOT A RESULT — MEASURE IT.** *No executed
instruction* is not the same claim as *no `Ir` difference*: R1h is a **different
compiled function**, and a never-executed statement can still move layout,
register allocation and inlining. **State the prediction before you run, then
report the measured R1 − R1h delta at BOTH optimisation levels and BOTH
compilers.** ⚠ **A non-zero delta is the more interesting outcome and owes a
disassembly mechanism** (PROTOCOL rule 12 — *"it vanished" is not a mechanism*).
✅ **Say `0.00` explicitly with the proof beside it, so the absence does not read
as an unmeasured zero** (`TASK_144`'s deliverable 4).

## ⚠⚠⚠ HEADLINE 2 — TWO BUG CLASSES SEPARATED BY WHICH INSTRUMENT SEES THEM

Manager-re-run today, gcc `-O1`, `n = 1` in 20 runs on every row:

```
input                        shape         arm  checksum    asan
040000000005000902000200     no-DUP        bug  4887708     -
040000000005000902000200     no-DUP        fix  4887708     -     IDENTICAL, clean
040000000005010002000200     DUP+POP       bug  4649380     ASan
040000000005010002000200     DUP+POP       fix  4649380     -     IDENTICAL, ASan fires
040000000005010002000300     DUP+READ      bug  4650434     ASan
040000000005010002000300     DUP+READ      fix  4650434     -     IDENTICAL, ASan fires
0500000000050100020000090300 DUP+NEW+READ  bug  144139491   ASan
0500000000050100020000090300 DUP+NEW+READ  fix  144138623   -     DIVERGES, ASan fires
POSITIVE CONTROL   ctl asan  hits=2  heap-use-after-free   FIRED
```
(op encoding: `c%4` = 0 NEW · 1 DUP · 2 POP · 3 READ; header = `nops` as u32 LE.)

- **`DUP+POP` / `DUP+READ` — the checksums AGREE BIT FOR BIT and ASan is the only
  discriminator.** The refcount header comes first and `data` starts at offset
  16, clear of glibc's tcache words at user offsets 0 and 8, so the stale read
  returns the *right* value. ⚠ **Disclose the layout**, as `p28` does.
- **`DUP+NEW+READ` — the checksum DIVERGES** because the next `NEW` **recycles**
  the freed block. ⚠ `TASK_143`'s four-shape search had no such cell.

**Ship BOTH**: `DUP+NEW+READ` as the gateable divergent one, and `DUP+POP` as the
checksum-blind one, each `sanitizer_expect: "fires"` with a `describe` saying in
terms that the checksum cannot discriminate. ✅ Stage 4 **records** adversarial
behaviour and does not require it to differ, so the blind cell is gate-legal.

⚠⚠⚠ **THE NOVELTY CLAIM IS A QUESTION TO BE MEASURED, NOT A FACT TO INHERIT.**
The manager believes *"no built temporal row has a cell that is reproducible AND
checksum-divergent AND detector-firing at once, and nothing in the tree has the
detector-only pair"* — the mirror image of `p29`'s headline. **Both axis claims
the manager has written into a task file as fact were FALSE and one `grep` plus
one run settled each** (RECAP item 4). **Derive it from `results/gate/p*.json`
and report what you find, including if it refutes the claim.**

⚠⚠ **AND EVERY FIGURE ABOVE IS gcc `-O1` ONLY.** The tree measures `-O0` and
`-O3`, gcc and clang. **The checksum-agreement result and the recycle-divergence
must be re-derived at both levels and both compilers before either is published.**

## ⚠⚠ THE QUESTION THIS ROW EXISTS TO ANSWER — and the manager's answer may be wrong

Outcome 3 now has **three demonstrations and they disagree**: `p32`'s safe Rust
reproduces the buggy C bit for bit, `p28`'s **cannot reproduce it at all**, and
`p35` shows **both shapes in one row**. The governing law is
`.memory/01-ladder.md`'s: *"safe Rust's temporal guarantee is a guarantee about
the **ALLOCATOR**; a structure that **recycles its own storage** gets no
guarantee at all."*

⚠⚠ **THE MANAGER'S LEAST-CERTAIN CALL, NAMED SO YOU CAN REFUTE IT (PROTOCOL rule
2): `p34` uses the real allocator, so an owned/`Rc` safe port should land in
`p28`'s shape (cannot reproduce), while an INDEX-ARENA port recycles its own
storage and should land in `p32`'s shape (reproduces exactly) — putting BOTH
BRANCHES OF THE LAW IN ONE ROW, SELECTED BY THE PORT CHOICE.** **Measure it.
Every agent that has contradicted the manager with a measurement has been right.**
⚠ **Whichever way it falls, `Rc::clone` incrementing unconditionally is a FINDING
about what safe Rust removes, never a reason to shrink the row.**

## ⚠⚠ THE R5 — the hardest in the project, and the gap is the result if there is one

⚠ **Manager-verified, do not re-derive:** the pinned
`~/tools/verus/vstd/std_specs/smart_ptrs.rs` is **78 lines** and has **no
`strong_count`, no `Rc::clone`, no `into_raw`/`from_raw`, no
`increment_strong_count`** — so an R5 must **model the counter itself** in a
raw-pointer rung. **That is a RESULT to report, never a reason to shrink the row.**

✅ **`p42` and `p35` are the standing precedents and they are good ones: a row
whose R5 cannot fully state its obligation STILL SHIPS, with the gap as the
finding**, both alternatives visible and the honest sentence written out
(*"what stands behind this is Miri plus this pin"*). ⚠ **If the gate hard-FAILS,
STOP AND REPORT the exact stage and predicate rather than working around it** — a
`check.py` change is a 30-pattern re-gate and is the manager's call.

⚠⚠ **NEW SINCE THE `TASK_143`-ERA TASK FILES, AND BOTH ARE HARD REQUIREMENTS
(`TASK_151`, RECAP finding 57):**
- **(a) stage `7h` — R1h must be sanitizer-CLEAN on EVERY input, adversarial
  included. It cannot be declared away.** ✅ Pre-verified above on all four
  demonstration inputs; confirm it in the real gate.
- **(b) `spec.md` must declare `verus.assumptions[<src>]` if any rung uses
  `assume(` or `admit(`** — otherwise the source is a hard FAIL.

## Deliverables

1. **Build `patterns/p34-refcount-stack/`** (confirm or improve the name) to
   `p01-array-sum/`'s structure and `p32`/`p35`'s recent example: seven rungs,
   `spec.md` with the machine-readable `slb-contract` pins, `model.py`,
   `inputs/gen.py`, `NOTES.md`, `README.md`, `controls/`.
   **`harness/check.py p34` must PASS and `measure.py` must record it** — or the
   gate must fail for a reason you have isolated and reported.
2. ⚠⚠⚠ **`model.py`: TWO failure modes.**
   **(i) NOT TRANSLITERATED** — `TASK_136`'s was a line-by-line copy of its own
   kernel and that is how its bug went undetected.
   **(ii) NO CHECK THAT IS A TAUTOLOGY OF THE MODEL'S OWN REPRESENTATION**
   (`.memory/03-measurement.md` entry **19**). ⚠⚠ **Python has no dangling
   pointers, so `p34`'s harm is very likely UNREPRESENTABLE in the model by
   construction. DECIDE THAT FIRST AND WRITE THE ANSWER DOWN.** ✅ **If the model
   cannot see it, DECLARE `sanitizer_expect` and say so plainly — declaring is
   honest; a derivation that cannot fire is not.** ⚠ **Any must-fire arm must
   REPORT rather than CRASH when broken** — `p32`'s crashes and the diagnostic is
   lost.
3. **The R5 owes an ATTACK arm that must FAIL and a VACUITY arm.** ✅ **`p32`'s
   three-cell battery is the shape to copy** (exec-only → fail, spec-only → fail,
   both → verify), ⚠ **extended by `p35`'s `X1`: delete the central obligation
   from the trusted readers' `requires` and see whether anything but a
   hand-written pin notices.** `p42`'s ghost ledger verified `18/0` while
   leaking; `p32`'s `assume(false)` verifies `15/0`.
4. ⚠⚠ **If you publish any rung-to-rung cost difference, search BOTH rungs'
   spellings, count the levers on each side, and say which side is the
   weaker-searched endpoint.** ⚠⚠⚠ **SIX patterns have published a headline wrong
   in the FLATTERING direction — `p10`, `p27`, `p38`, `p22`, `p36` and now `p35`,
   whose R4 side was never searched and WINS by 6.63% once given R3's own two
   levers.** ⚠ **And `p35` added a lesson none of the other five had: THE
   COMPARISON REVERSES BETWEEN OPTIMISATION LEVELS. Give every figure at BOTH
   levels and NAME THE INLINE MODE.** ✅ **A row may ship with NO cost axis —
   `p29` and `p32` do — but say so explicitly so the absence does not read as a
   zero.** Here headline 1 makes the *safety-line* gradient `0.00` by
   construction; the NEW/POP/READ gradient across languages is a separate,
   real axis and is where the flattering-direction risk actually lives.
5. **Tell the manager the bug class** for `harness/tools/composition.py` — this
   should be the **`temporal` axis's FIFTH row** (`p27 p28 p29 p32` today).
   ⚠ **Do not edit that file.** Expect `--check` to FAIL with `built but
   unclassified` until the manager classifies it — **that is the check working.**
6. **PROTOCOL definition-of-done rule 6: record the `slb-contract` block's
   sha256 in `NOTES.md` the moment you first write it, before building any
   cell**, with the words *"as first written, before any measurement"*.
   ⚠⚠ **`p28` shipped with NO rule-6 disclosure and that evidence is
   unrecoverable; `p35`'s reconstructed EXACTLY. Keep `p35`'s standard.**
   ⚠ On a new pattern `git show HEAD:` is **vacuous** — say so rather than citing
   a command that cannot fire. ⚠ And before finishing, **re-read the hashed `why`
   against your own measured numbers**: rule 6 protects against a declaration
   edited after measuring and does **nothing** about one measurement has since
   falsified (`p46`, whose hash matched perfectly while the `why` was false).

## Rules

- `.temp/t154/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — all cited
  evidence. **Copy from them; do not modify them.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`. ⚠ Grep
  `~/tools/verus/vstd/std_specs/` **specifically** before any "no spec exists"
  claim — that confusion has produced a false claim twice.
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; **every harm probe owes a positive control that must fire — in
  the detector whose column it licenses.**
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log — not
  with a regex alternation, and not with a loop matching a prefix a log header
  shares with its verdict.** Three mechanisms, one cure
  (`.memory/03-measurement.md` entries 21–22). Expect `p01 = 1`, `p42 = 1`,
  `p35 = 3`; `p42` may legitimately be 2.
- ⚠⚠ **If the gate fails on `[tables]`, run `harness/report.py p34` and re-gate.**
- ⚠ **Generate control JSONs AFTER the sources are final** — `c/*`, `*.rs`,
  `model.py` and `inputs/gen.py` are MEASUREMENT-HASHED, and `measure.py` hashes
  them at line 450 **above** the loop, so a mid-run edit wastes the whole run
  (`TASK_150` paid two).
- ⚠ `python3 harness/tools/contract_diff.py p34` says what moved inside the
  hashed block, from `git` alone. Use it for your disclosure.
- **Keep the generator, delete the artefact** (`.memory/00-environment.md`
  constraint 6).
- ⚠ **A re-gate is not value-free**: `marginal_ir_per_call` moved in 673 of 2772
  cells across 18 patterns on an unchanged tree (entry 21). Do not read small
  moves elsewhere as your doing.
- Report to `.tasks/TASK_154_REPORT.md`.

**PROTOCOL rule 2 running count: launched from 882**
(`.tasks/TASK_153_REPORT.md`'s closing paragraph). Carry it forward in your
closing paragraph. ⚠ **Reconciliation across branches is the manager's job.**
⚠⚠ **And the highest-value thing you can do is contradict the manager with a
measurement — the named target is the safe-Rust prediction above, and the
`0.00` gradient beside it.**
