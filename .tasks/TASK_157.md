# TASK_157 — build `p25`: dynamic array with `realloc` growth (the LAST unbuilt admitted row)

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You may use
`harness/check.py` and `harness/measure.py`.

Read first: `.temp/mgr155/NOTES.md` **in full** — the manager's second-pass
pre-build verification, and **it REFUTES `.temp/mgr148/`'s own closing advice**;
then `.temp/mgr148/NOTES.md`; `.memory/06-catalogue.md`'s `p25` cell **rather
than `TASK_143_REPORT.md`**, which the cell corrects;
`patterns/p34-refcount-stack/` and `patterns/p32-free-list-pool/` as the two most
recent structural templates; `RECAP.md` findings **53–59**; `CLAUDE.md` **rule
6**; `.memory/03-measurement.md` entries **19–22**.

## The bar, because it is the whole reason this row exists again

`CLAUDE.md` **rule 6** and `.memory/02-bench-rules.md`'s *THE ADMISSION BAR IS
C-SIDE ONLY*. **ADMITTED at `TASK_143`, ranked 2nd of 7.**

> ⚠⚠⚠ **THIS ROW WAS REFUSED AND ITS KILL RESTED ON DRIVER-ARTEFACT AND
> LADDER-SIDE GROUNDS THE NEW BAR FORBIDS.** *"In `p25`'s shipped heap topology
> `realloc` never moves"* (**a fact about that driver, not about C** — see §4
> below); *"there is no safety conjunct to omit, the safety line is an ADDRESSING
> MODE"* (**refuted: the diff is literally the conjunct `curbase == toks`**);
> *"safe Rust makes the bug a compile error"* (**a FINDING, and a weak one — see
> the warning in deliverable 4**). **None may be reused.** Whatever the Rust and
> Verus rungs land on **is the result.**

## What already exists — promote it, do not re-derive it

`.temp/mgr155/{NOTES.md,repro.sh,sentprobe.sh,mksent.sh,build.sh,difflines.sh,
common/,p25/{k.c,body.inc,matrix.json},sent/,probe_move.c,probe_when.c}`.
✅ **Keep the include-twice construction** (`body.inc` with `SLB_HARDEN` 0 and 1),
and ⚠ **put it in `controls/` and measure the shipped preprocessed files**, as
`p32`, `p35` and `p34` do.

## The C mechanism, and why it duplicates nothing

**The program NEVER CALLS `free` ON THE OBJECT IT LATER READS.** `realloc`
**relocates** the vector and retires the old block as a side effect of *growth*,
and the stale reference is an **INTERIOR pointer into the middle of a
container**, not a pointer to a whole object.

✅ **MANAGER-MEASURED, not asserted (`.temp/mgr155/` §6): `grep -rln 'realloc'
patterns/*/c/` returns ZERO files across all 31 patterns.** Only 6 of 31 C rungs
call `malloc` at all. **No built row has an allocation that MOVES while
logically live, and none has a stale INTERIOR pointer.** ⚠ **`p34` is the
sharpest attack to pre-empt in your own `NOTES.md`** — it is also "a read of a
retired block" — **but `p34`'s block is explicitly `free`d by a refcount
reaching zero and its repair site is the ACQUIRE, while `p25` never calls `free`
at all and its repair site is the READ.** ⚠ **Say this in the row's own words
after checking it, and report it if you disagree.**

✅ **Safety line: `+4 / −1` preprocessed lines, manager-re-run** — and the diff
is confined to one `else` branch:

```
-                acc = acc * 31 + (uint64_t)*cur;
+                if (curbase == toks)
+                    acc = acc * 31 + (uint64_t)*cur;
+                else
+                    acc = acc * 31 + 251;
```

## ⚠⚠⚠ THE THING THAT WILL BITE YOU, AND IT IS ALREADY MEASURED

`.temp/mgr148/` told a build task that *"R1's answer is a draw from a range
**disjoint** from R1h's single value."* ⚠⚠ **THAT IS FALSE, and `.temp/mgr155/`
§2 closes the mechanism exactly:**

```
600 runs, adv-realloc-move, BUG arm, gcc -O1
  min 17004291282180250410   max ...258315   span 7905 == 255*31
  values NOT of the form min + 31*b :  0 of 600
  R1h == min + 31*251                :  TRUE
  exact R1 == R1h collisions         :  4/600 gcc, 2/400 gcc, 4/400 clang (~0.7%)
```

**Every R1 answer is `min + 31·b` where `b` is the single stale byte**, because
the READ is the last op and the epilogue multiplies once more. **R1h substitutes
`P25_SENT = 251` at that same position**, so **R1 equals R1h exactly when the
stale byte happens to be 251** — about **1 run in 130**.

⚠⚠ **DO NOT PIN *"R1 ≠ R1h on the adversarial input"* AS AN INVARIANT OR IN A
`controls/*.json`.** ✅ **`p29` is the precedent and already solved this: gate on
the INVARIANT, publish no pinned count. Pin R1h's value** — `17004291282180258191`,
`n = 1`, **identical on all five builds and both compilers** — **and pin the
DETECTOR, never R1's.**

✅ **A repair exists and the manager MEASURED it rather than asserting it
(`.temp/mgr155/sentprobe.sh`): move the sentinel out of byte range.**

```
variant  arm  kernel_Ir(benign-grow)  static insns   collisions (large sentinel)
p25      fix  1304                    194            0/600, nearest R1 value 34T away
sent     fix  1304                    199
benign / benign-grow checksums: BYTE-IDENTICAL under both sentinels, both arms
```

⚠⚠ **The manager first wrote *"impossible at zero cost"* and *"it moves every
checksum in the row"* — HALF OF EACH WAS FALSE.** Impossible: yes. Zero `Ir`:
yes (the sentinel sites never execute on benign inputs). **Zero cost: NO — `+4`
static instructions in R1 and `+5` in R1h, and the project publishes a static
count beside `Ir`.** **Moves every checksum: NO — only the adversarial R1h
value moves.** ⚠ **Decide the sentinel BEFORE measuring and say which you took
and why; both are defensible and the collision must be disclosed either way.**

## ⚠⚠ THE OTHER MEASURED FACTS YOU INHERIT — all manager-re-run at TWO compilers

1. ✅ **STAGE `7h` PASSES**: R1h is clean in all 15 (arm × input × build) cells,
   ASan and UBSan, both compilers. ⚠ **`.temp/mgr148/` ran no detector on the
   `fix` arm at all — `p28d`'s exact blind spot. Keep the repaired standard.**
2. ✅ **The benign half is identical across both compilers and all five builds**:
   `benign` → `29377263588`, `benign-grow` → `16044208871906170630`, both arms,
   `n = 1` in 20 runs. **`benign-grow` EXECUTES every relocating `realloc`**, so
   admission question 1 is met **with growth exercised**, not by avoiding it.
3. ✅ **The `TASK_134` kill is void, re-run at two compilers**: `probe_move` gives
   `11/48` single-vector and **`24/48` with a token vector + string table**.
   ⚠⚠ **AND `probe_when` NARROWS THE HARM WINDOW, which nothing had recorded:
   EXACTLY ONE of six growths relocates (`16 → 32`).** **The adversarial input
   must be tuned to that growth, and `NOTES.md` must say so** — otherwise a
   reader takes *"`realloc` moves"* for a general property of the kernel.
4. ⚠ **ASan is a BIASED instrument here** — its allocator moves on *every*
   `realloc`, so it fires even under a topology where glibc never relocates.
   **The plain-build divergence is the unbiased evidence. Do not rest the row on
   the ASan cell**, and say so where you quote it.
5. ⚠ **The demonstration's positive control is ASan-shaped and DID NOT FIRE under
   UBSan** (`rc=0`, no diagnostic) — the same gap `p35` was built to close.
   **Ship one control per detector**, as `p34` does (`ctl_asan.c`/`ctl_ubsan.c`).
6. ⚠ **All manager figures are `-O1`.** The tree measures `-O0` and `-O3`.
   **Re-derive at both levels and both compilers.**

## ⚠⚠ NEW OBLIGATIONS `TASK_143`-era task files do not mention

- **(a) stage `7h`** — R1h must be sanitizer-CLEAN on EVERY input, adversarial
  included. **It cannot be declared away.** ✅ Pre-verified above; confirm it in
  the real gate.
- **(b) `spec.md` must declare `verus.assumptions[<src>]`** if any rung uses
  `assume(` or `admit(` — otherwise the source is a hard FAIL.

## Deliverables

1. **Build `patterns/p25-realloc-growth/`** (confirm or improve the name) to
   `p01-array-sum/`'s structure and `p34`/`p32`'s recent example: seven rungs,
   `spec.md` with the machine-readable `slb-contract` pins, `model.py`,
   `inputs/gen.py`, `NOTES.md`, `README.md`, `controls/`.
   **`harness/check.py p25` must PASS and `measure.py` must record it** — or the
   gate must fail for a reason you have isolated and reported.
2. ⚠⚠⚠ **`model.py`: TWO failure modes.** **(i) NOT TRANSLITERATED.**
   **(ii) NO CHECK THAT IS A TAUTOLOGY OF THE MODEL'S OWN REPRESENTATION**
   (`.memory/03-measurement.md` entry **19**). ⚠⚠ **Python has no dangling
   pointers and no `realloc`, so decide FIRST whether the harm is representable
   and write the answer down.** ✅ **If the model cannot see it, DECLARE
   `sanitizer_expect` and say so plainly — declaring is honest; a derivation
   that cannot fire is not.** ⚠ **`p34` contradicted the same prediction and
   DERIVED it; do not assume either way.** ⚠ **Any must-fire arm must REPORT
   rather than CRASH when broken.**
3. **The R5 owes an ATTACK arm that must FAIL and a VACUITY arm.** ✅ **`p32`'s
   three-cell battery is the shape to copy**, extended by `p35`'s `X1` and
   `p34`'s `Z1`: **delete the central obligation and see whether anything but a
   hand-written pin notices.**
4. ⚠⚠ **THE COST AXIS, AND THE TRAP HAS NOW FIRED SEVEN TIMES.** If you publish
   any rung-to-rung difference, **search BOTH rungs' spellings, count the levers
   on each side, and name the weaker-searched endpoint.** ⚠ **Give every figure
   at BOTH optimisation levels — `p35` showed the comparison can REVERSE — and
   NAME THE INLINE MODE.** ✅ **`p34` is the standard to beat: it shipped a
   CONTROL that makes the search re-derivable and caught its own overstatement
   before any review saw it.**
   ⚠⚠⚠ **AND THE SAFE-RUST HALF IS WHERE THIS ROW IS MOST LIKELY TO GO WRONG.**
   The catalogue records that `p25`'s `E0502` is **NOT distinguishing** — **seven
   controls that CANNOT have the bug print the same error, including a
   `struct S { v: u32 }` with no container at all** — and `p34` made it the third
   instance (`p28`'s `E0382`/`E0499` was the second). ⚠ **If you claim safe Rust
   cannot express this bug, you owe a NEGATIVE CONTROL that cannot have the bug
   and must not print the same error.** ⚠ **Also recorded so you do not
   rediscover it: the INDEX port has NO BUG AT ALL — `realloc` copies, so `v[k]`
   names the same element afterwards. That is a finding, not a failure.**
5. **Tell the manager the bug class** for `harness/tools/composition.py`.
   ⚠ **Do not edit that file.** Expect `--check` to FAIL with `built but
   unclassified` — **that is the check working.** ⚠ **The catalogue calls this
   row *"growth overflow, stale pointer"*; the growth-overflow half is SPATIAL
   and is refused on sight, so the shipped bug is the stale-pointer half.
   Propose the wording and say which axis it lands on.**
6. **PROTOCOL definition-of-done rule 6: record the `slb-contract` block's
   sha256 in `NOTES.md` the moment you first write it**, with the words *"as
   first written, before any measurement"*. ⚠⚠ **AND KEEP THE BLOCK TEXT
   VERBATIM, NOT ONLY THE HASH** — `p34`'s first contract move proved
   unreconstructible six ways at `TASK_155`, and `TASK_156` fixed the standard.
   ⚠ On a new pattern `git show HEAD:` is **vacuous**; say so rather than citing
   a command that cannot fire. ⚠ Before finishing, **re-read the hashed `why`
   against your own measured numbers** — rule 6 does nothing about a declaration
   measurement has since falsified, and `p34` shipped a FALSE sentence inside a
   matching hash.

## Rules

- `.temp/t157/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — all cited
  evidence. **Copy from them; do not modify them.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`. ⚠ Grep
  `~/tools/verus/vstd/std_specs/` **specifically** before any "no spec exists".
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; **every harm probe owes a positive control that must fire — in
  the detector whose column it licenses.**
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log**, and
  ⚠ **`rc=$?` after a PIPE reads the LAST command's status, not the script's —
  the manager misread a FAILING `composition.py --check` as `rc=0` that way.**
  Expect `p01 = 1`, `p42 = 1`, `p35 = 3`; `p42` may legitimately be 2.
- ⚠⚠ **If the gate fails on `[tables]`, run `harness/report.py p25` and
  re-gate.** ⚠ **A `why` rewrite moves `contract_sha256`, and the published
  table cites it, so a `why` edit costs TWO gate runs** (`TASK_156` measured it).
- ⚠ **Generate control JSONs AFTER the sources are final** — `c/*`, `*.rs`,
  `model.py` and `inputs/gen.py` are MEASUREMENT-HASHED, and `measure.py` hashes
  them **above** the loop, so a mid-run edit wastes the whole run.
- ⚠ `python3 harness/tools/contract_diff.py p25` says what moved inside the
  hashed block, from `git` alone. Use it for your disclosure.
- **Keep the generator, delete the artefact** ⚠ **and a generator that edits
  source by string substitution MUST ASSERT ITS SUBSTITUTION COUNT** — `p28d`
  shipped an uninitialised pointer because a `str.replace()` silently matched
  nothing. `.temp/mgr155/mksent.sh` is the shape.
- Report to `.tasks/TASK_157_REPORT.md`.

**PROTOCOL rule 2 running count: launched from 892**
(`.tasks/TASK_156_REPORT.md`'s closing paragraph; the manager has reconciled it). ⚠ **Reconciliation across branches is the
manager's job, not yours.** ⚠⚠ **The single highest-value thing you can do is
contradict the manager with a measurement: five of the last seven majors were
the manager's, and `TASK_156` refuted three more sentences in this very file's
predecessor. The named targets here are the sentinel decision (deliverable §"the
thing that will bite you") and the `p34`-distinctness paragraph.**
