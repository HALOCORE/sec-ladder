# TASK_077 — the `harness/` batch: five measured defects, one sweep

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`RECAP.md`'s "Owed" items 5, 12,
14, 19, 20 and 22**, then `.memory/02-bench-rules.md`'s **last three sections**
and `.memory/03-measurement.md`'s **outward-dispatch block**. ⚠ **Then
`.tasks/TASK_068_REVIEW_REPORT.md`** — the last batched gate task, whose review
found **2 blockers and 5 majors** in work that reported success. **That is the
prior for this one.**

⚠ **PROTOCOL rule 5 (*prefer producing a pattern over hardening the gate*) is
being OVERRIDDEN for the second task running.** The standard is TASK_068's:
*fixes to **measured** defects, not speculative hardening*. **All five items
below were measured by an agent, and three were measured twice.** Rule 5's own
test — *"could this happen by accident?"* — is passed by every one. **If you
think the override is wrong, say so.**

**Why one sweep and not five tasks:** every item stales **all 22 gate records**
via `check.py::main`'s `harness/*.py` glob. One batch = one sweep.

## §0 — settle the COST before you edit anything

⚠ **Two of these five may force a RE-MEASURE, which is the project's most
expensive operation and churns published wall-clock rows** (RECAP settled
answer 4). **Establish which, with the command, before writing code.**

- **Item 14 definitely does**: `p38/model.py::sanitizer_expect` is
  measurement-hashed.
- ⚠ **Item 22 is the open one.** `bulk_calls` is recorded at *measure* time, so
  fixing `harness/asm.py`'s symbol table may leave **p09, p11 and p47** carrying
  records that are correct-by-hash and wrong-by-content — the exact shape of
  RECAP "Owed" 6, where five records were declared clean by a command that
  could not see the defect. **Is `asm.py` in `measure.py::measurement_sources`?
  Run `--check-stale` after the edit and paste the verdict.** ⚠ **Remember
  TASK_076's lesson: `GEN-ONLY`-style branches mean "hashed" and "forces a
  re-measure" are NOT the same claim.** Do not infer it — read the verdict.
- **If a re-measure is forced, bundle every measurement-hashed change into ONE**
  — item 14, item 22's affected patterns, **and "Owed" 12's six deliberately-left
  citations** (`p12`, `p13` ×3, `p16` ×2, `p38`), whose targets are in
  `.temp/p68/NOTES.md` and which have been waiting for exactly this.

**Write the plan in `.temp/p77/NOTES.md` before editing.** A re-measure that
turns out to be unnecessary costs hours; one skipped that was necessary ships a
wrong record.

## The five items

**1 — "Owed" 14: `-fstrict-aliasing` on stage 7.** MEASURED, CORRECT and
BLOCKED since TASK_068. `check.py::check_sanitizers` builds C at `-O1`
**without** the flag, so it cannot see a flag-gated UB class. **Adding it makes
stage 7 see p38 at `-O1`** (ASan `stack-buffer-overflow READ of size 2`).
**Blast radius measured across all gate records: exactly one pattern** — 16
patterns declare a `fires` input and **all 16 already fire at `-O1`**, p18
included. ⚠ **But the token turns p38's gate RED**, because
`p38/model.py::sanitizer_expect` returns `"clean"` unconditionally and two
adversarial rows then fire on an input declared clean. **Token +
`sanitizer_expect` + re-measure is ONE unit.** ⚠ **Do NOT raise stage 7's
optimisation level instead** — that perturbs 22 patterns to fix one.

**2 — "Owed" 19a: `check_miri`'s block reason is structurally false for every
pattern here.** It says *"R4 does not return under Miri either"*; measured,
`miri` on p22's shipped `unsafe.rs` gives `rc=0 UB=False`. `expected_hang` is
per-**input**, but its Miri consequence assumes the hanging rung is the one Miri
runs — and **`.memory/01-ladder.md` puts the bug in R1 only, so `miri.sources`
always names a rung carrying the fix.** **Cost today: one genuinely unchecked
Miri row per declared hang.** Needs a **per-rung axis** on `expected_hang`;
`model.py` has a per-input bool only. ⚠ **Fix the COMMENT as well as the code** —
TASK_069 already had to do that once here, and a false comment is what the next
reader trusts instead of reading.

**3 — "Owed" 19b: `_confirm_hang` picks the first cell in sorted order** —
`c-clang O0` on p22, **never an `-O3` cell**, which is the one C11 6.8.5p6 puts
at risk. ⚠ **The obvious repair is REFUTED**: per distinct *rung* still picks
two `O0` cells and **would have caught nothing**. **The axis is (rung × opt).**

**4 — "Owed" 20: `harness/vparse.py::duplicate_names` keys by BARE NAME.** So a
pinned `verus.rs` cannot define one item name twice — **eight `impl Op for OpN`
blocks verify `19/0` and the gate refuses them** (p36 §9b). `parse()` **already
computes each item's enclosing impl**, so the fix is to key by `(impl, name)`.
⚠ **This forced a spelling**: p36 ships one generic
`impl<const K: u8> Op for OpTag<K>` because of it. **Do not respell p36** —
fixing the gate does not oblige a pattern to change, and p36's contract is
hashed.

**5 — "Owed" 22: `harness/asm.py`'s bulk-symbol table is wrong in three measured
places.**

- **`asm.is_bulk_symbol('bcmp')` is `False`** → `results/p47-ct-compare.json`
  records `c-gcc: ['memcmp@plt']`, `c-clang: []`, `safe_naive: []` for **three
  cells calling the same entry point** (`0x188320`, confirmed by call counts —
  the entire apparent difference is gcc's 2-instruction PLT thunk).
- **`__popcountdi2` is unrecognised** → **p09's gcc column records `[]`** while
  carrying **378.00 / 2625.00 `Ir` per call** of libgcc software popcount.
- **p11's four plain `c-gcc`/`c-clang` cells record `[]` while calling
  `strlen@plt`** — and `is_bulk_symbol('strlen@plt')` is **`True`**, so this one
  is a **stale record, not a table defect**. ⚠ **It supersedes "Owed" 6's
  follow-up sentence**, which says p11's `bulk_calls` are populated today; only
  its two **R1h** cells are.

> ⚠ **Distinguish the two failure modes in your report**, because they have
> different fixes: a **table** defect (fix `asm.py`, re-derive) versus a **stale
> record** (fix nothing, re-measure). **Getting this wrong is how "Owed" 6 stood
> closed for ten tasks on a command that could not see the defect.**

## Also worth deciding, since you are in here anyway

⚠ **"Owed" 5: `check.py`'s `harness/*.py` glob is over-broad.** It imports five
modules and hashes **all** of them, so a `measure.py` edit costs a full gate
sweep for a file **the gate never executes** — 13 minutes measured, and it is
why this batch exists as a batch. **You are about to pay that cost. Say whether
narrowing the glob to the modules `check.py` actually imports is safe**, and
what it would have missed historically. ⚠ **Belt-and-braces cannot under-cover,
so the burden is on narrowing** — it is a judgement call and the manager's lean
is to leave it alone. **Argue it either way; do not silently do it.**

## Done when

All five items fixed or **explicitly declined with a reason**; §0's re-measure
plan executed as written or amended **with the measurement that changed it**;
**`check.py` green on all 22 patterns — paste all 22 verdicts**;
`measure.py --check-stale` clean; **and for every record that moved, say why and
whether a published number moved with it.** ⚠ Use a sweep script whose `rc` is
not read after a pipeline — `.temp/p68/sweep.sh` is the fixed one.

## Constraints

No root; no `/tmp` (scratch `.temp/p77/`; ⚠ **`ls` any scratch path before
writing — `.temp/pNN/` collides between patterns and tasks**; `.temp/p68/` and
`.temp/p76/` are readable, **not writable**); **no `git add`/`git commit`**; do
not edit `pilot/`, `.memory/`, or `common/`. **You MAY edit `harness/check.py`,
`harness/vparse.py` and `harness/asm.py`.** ⚠ **Do NOT touch `harness/build.py`**
— it is measurement-hashed and would force a **tree-wide** re-measure, not a
per-pattern one. ⚠ **Do not edit any pattern's `model.py` or `inputs/gen.py`
EXCEPT `p38/model.py::sanitizer_expect`, which item 1 requires**; if another
seems to need one, **STOP and report it**. Verus only via `./verus_run.py`.
clang `~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — **none but gcc on
PATH**. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; **no
self-matching `pgrep` wait-loops.** ⚠ **Any re-measure runs in the FOREGROUND
and alone** — concurrent CPU load corrupts a `ns` column silently. **You are the
only agent running.**

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 184**, and the last four entries are all *the review being wrong and the
next agent re-deriving the number instead of citing it*. **That is the behaviour
this task most needs**, because five of its six premises are numbers someone
else measured.

**What I am least sure of, by name: §0's re-measure scope, and specifically
whether item 5 forces one.** If `asm.py` is measurement-hashed, fixing it either
re-measures p09/p11/p47 or leaves three records correct-by-hash and wrong-by-
content — and **the second is worse than the defect**, because `--check-stale`
will call them clean. **If that is where it lands, say so plainly and let the
scope grow; do not fix the table and leave the records.**
