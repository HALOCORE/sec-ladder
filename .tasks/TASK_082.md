# TASK_082 — the gate cannot see a trusted item Verus tells you to write. Fix it, and batch everything that rides free.

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_081_REVIEW_REPORT.md`
BLOCKER 1 in full** (it is the specification for the main deliverable, with the
demonstration already built), then **`RECAP.md` "Owed" 0** and **"Owed" 4**, then
`.memory/04-verus.md`'s final section (*"the escape Verus PRINTS FOR YOU is
VACUOUS"*), `.memory/02-bench-rules.md`'s **threat model** and `.memory/05-layout.md`
(**what a `harness/*.py` edit stales, and what it does not**). Reviewer's evidence
and `repro.sh`: `.temp/r81/` — **readable, NOT writable.**

⚠⚠ **READ THIS BEFORE YOU AGREE WITH THE TASK: THE MANAGER OVERSTATED THE
JUSTIFICATION AND IS CORRECTING IT HERE.** The TASK_081 commit message called
this *"a measured defect in a published column."* **That is half true and the
half that is false matters.** ✅ The *defect* is measured — the gate demonstrably
cannot see two false axioms added to `p01/verus.rs`. ❌ **But NO published number
is currently wrong:** `grep -rn 'assume_specification\|broadcast axiom fn\|uninterp spec fn' patterns/*/verus.rs`
returns **one hit and it is a COMMENT** (`p08/verus.rs:322`). **So this is
PROSPECTIVE hardening, and PROTOCOL rule 5 says prospective hardening owes the
*"could this happen by accident?"* test.**

**The manager's answer to that test, offered to be attacked:**

1. **Verus PRINTS the declaration and invites you to paste it.** The accident
   vector is the tool's own help text, not an author going looking.
2. **The pasted form is not merely uncounted — it is UNSOUND.** TASK_081 measured
   `4 verified, 0 errors` with a **1 MiB out-of-bounds read and a null
   dereference** both verifying. So the accident produces a hidden trusted item
   **and** a false green **in the same edit**.
3. **Someone now has a measured reason to want it.** TASK_081 established this is
   the only route to several R4 spellings, one worth **−35%** on p11.

⚠ **If you think that fails the test, say so and argue for doing "Owed" 4 alone.**
The manager would rather be told the batch is wrong than have it built politely.

## Deliverable 1 — make body-less Verus items visible (RECAP "Owed" 0)

**The defect, already demonstrated — do not re-derive it, just re-run
`.temp/r81/repro.sh`'s relevant block to confirm before and after:**
`harness/vparse.py`'s item matcher keys on `fn NAME` **with a body** and drops
every body-less item, so **`assume_specification`, `broadcast axiom fn` and
`uninterp spec fn` are invisible to the parser**; `check.py::_is_trusted`
additionally requires `verifier::external_body`. Blind to it today: the TCB
column published in `results/synthesis.md`, the pinned obligation count, the
`identity` pin, `check_miri` (`n_trusted == 0` ⇒ *"Miri not required"*), and
stages 5c / 5c-req / 5c-twin.

**The reviewer's proposed repair, which you are not obliged to take:** a declared
count plus `rep.note` → `rep.shout`.

⚠⚠ **THE HAZARD THAT MAKES THIS NOT A ONE-LINER, AND IT HAS BITTEN THIS PROJECT
BEFORE.** Making the parser see *more* items changes `vparse.by_name`, and
**RECAP "Owed" 20 is the record of exactly that going wrong**: `by_name` is
bare-keyed and **six** consumers turn its `ValueError` into a failure —
`check_call_site`, `check_clause_deletion`, `check_requires_strength`,
`check_trusted_twins`, `derive_contract`, and `harness/limbs.py`. **A new item
whose name collides with an existing one turns a green pattern red.**

> **So the acceptance test is not "the new items appear." It is:**
> **(a)** all 22 patterns still `PASS` with **0 failures**, and
> **(b)** every pattern's **TCB count is UNCHANGED**, because no pattern has one
> of these items today — ⚠ **if any count moves, you have found something and
> you must stop and report it, not absorb it.**
> **(c)** the `.temp/r81/p01_axiom.rs` demonstration now **fails or shouts**,
> where today it is silently identical to the untouched file.

⚠ **Rule 5's other half applies to your own design: do not add a gate stage if a
count plus a shout does the job.** The threat here is *invisibility*, not
*misuse* — an author who declares an axiom and says so in the TCB tally is doing
nothing wrong. **Make it visible; do not make it forbidden.**

## Deliverable 2 — p17's sweep bands (RECAP "Owed" 4)

**The spec is already written and was handed back by TASK_080's engineer.** p17
ships **no** `sweep-*` inputs, which is how *"+32 `Ir`/call flat"* was published
from two bands that **both had `nsuf = 3`** — the residue-class failure that
broke p38's additivity, sitting inside a published law.

- Add `--sweep` to `patterns/p17-http-range/inputs/gen.py`, **modelled on p16's
  `inputs/gen.py`**, emitting `sweep-nsuf-NN.bin` over **`nsuf = 1..8`**
  (TASK_015_REVIEW measured `≈7·nsuf + 9`).
- **Regenerate twice and diff** for determinism.
- ✅ **One gate re-run, NO re-measure** — both `check.py` and `measure.py` skip
  the `sweep-` prefix. ⚠ **Confirm that on the actual record rather than trusting
  this line**, and if `--check-stale` disagrees, **stop and report**.
- ⚠ **Then FIT THE LAW ACROSS THE NEW BAND.** The point of the item is not the
  blobs — it is finding out whether *"+32 flat"* survives a non-degenerate
  `nsuf`. **If it does not, that is a published number moving and it is the most
  valuable thing in this task.** Report it; do not quietly re-fit.

## Deliverable 3 — the doc fixes that ride along free

⚠ **Only because deliverable 1 stales every gate record anyway.** A
`patterns/*/*.md` edit costs a gate re-run and **no** re-measure
(`measure.py::provenance` does not glob `*.md`). **In priority order; report what
you did not reach:**

1. **`patterns/p11-nul-scan/NOTES.md:1029`** — it says the unsafe class *"cannot
   reach it at all"*. TASK_081 measured all four items escaping at **4 trusted
   items**, and ⚠ **two of the four are TYPES, both functions are SAFE, so there
   is no `requires` to bite.** The supported sentence is **"the unsafe class
   reaches `core::slice::memchr` at four hand-written axioms that no gate stage
   checks"** — and after deliverable 1, *some* stage does. **p11's own NOTES
   already contains both the old and the new sentence; that contradiction is the
   thing to fix.** ⚠ **Do NOT flip p11's finding** — the −35% is still not a
   measured admissible rung, and its `Ir` cost is unmeasured.
2. **`harness/check.py`'s stage-3c `head()` string** still reads *"recorded as a
   result"*; the comments beside it were corrected long ago. RECAP's *"Deferred
   with a stated reason"* says it is free on any task that already re-runs all
   gates. **This is that task.**
3. **RECAP "Owed" 18** — p27's `required[2]` finding lives in `check.py`'s
   docstring rather than in `patterns/p27-handle-table/NOTES.md`. ⚠ **Only if p27
   is being re-gated anyway**, which deliverable 1 makes true.

⚠ **NOT in scope and do not touch: RECAP "Owed" 12's six remaining citations.**
They live in `model.py` / `inputs/gen.py`, which are **measurement-hashed** — a
full re-measure, not a gate re-run. **They do not ride free and this task must
not pull them in.**

## Done when

- `harness/check.py <every pattern>` green — **paste the verdict line for all
  22** and the failure count. ⚠ **Say up front which verdicts you expect.**
  Recompute rather than quoting a constant:
  ```
  python3 -c "
  import json,glob
  for f in sorted(glob.glob('results/gate/*.json')):
      d=json.load(open(f)); print(f.split('/')[-1][:-5], d['verdict'], len(d.get('failures') or []))"
  ```
- **The TCB count of every pattern is unchanged** — show it, do not assert it.
- The `.temp/r81/p01_axiom.rs` demonstration no longer passes silently.
- `harness/measure.py --check-stale` → **0 STALE** (deliverable 2 must not force
  a re-measure; if it does, **stop and report**).
- Dangling-citation check clean but for the two documented placeholders.
- **Paste actual output.** ⚠ Doc edits make a gate record STALE — sequence your
  edits so the final gate run is last.

## Constraints

⚠ **`ls` any scratch path before you name it** — `.temp/pNN/` is a live
PATTERN-vs-TASK collision (`.temp/p31/` is TASK_031's evidence, `.temp/p48/` is
TASK_048's, and both were nearly destroyed by a manager prescription). Suggested
scratch: **`.temp/t82/`** — `ls` it first. `.temp/r81/`, `.temp/p45pat/` and
`.temp/p31pat/` are **readable, NOT writable.**

⚠ **This task edits `harness/` — which is normally forbidden — and it is the
ONLY task in flight.** Do not edit `pilot/`, `.memory/`, `common/`, or
`build.py`. ⚠⚠ **`harness/build.py` and `harness/asm.py` are MEASUREMENT-hashed:
touching either costs a full re-measure of 17 records, not a gate re-run. This
task must not touch them.** `check.py`, `vparse.py` and a pattern's
`inputs/gen.py` are the writable surface.

No root; no `/tmp`; **no `git add`/`git commit`**. Verus only via
`./verus_run.py`; `~/tools/verus/vstd/` for vstd source — **never**
`../LearnVeri/_VERUS_DOC_/vstd/`. clang `~/tools/llvm/bin/clang`, gcc
`/usr/bin/gcc`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — **none but gcc on PATH**. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**; ⚠ **no self-matching `pgrep` wait-loops**.
Gate runs in the **FOREGROUND**. **You are the only agent running.**

⚠ **A full gate sweep is ~30 minutes and a full re-measure is 43 minutes — they
are different things.** This task owes the first and must not trigger the second.

Notes to `.temp/t82/NOTES.md` as you go, and ⚠ **write them per step, not at the
end** — two agents died to API 529s two tasks ago having produced nothing.

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 223** — **+9 from the last task, seven against manager-written text, two of
them inside the task file that forwarded the rule against them.**

**What I am least sure of, by name: whether deliverable 1 is worth its blast
radius at all.** It stales every gate record for a defect that **moves no
published number today**, on a tree that has not gained a pattern in five tasks.
**I think the accident argument above carries it** — Verus prints the
declaration, the printed form is unsound, and someone now has a reason to paste
it — **but that is a judgement about the future and you are entitled to disagree
with it.** ⚠ **If you would rather do deliverable 2 alone and leave the gate
until a pattern actually needs it, say so with your reasoning and do that
instead.** Three catalogue rows in a row were refused by agents who pushed back;
**that is the behaviour this project runs on, not an exception to it.**

**Second-least sure: the `by_name` collision hazard.** I believe making the
parser see body-less items cannot collide today **because no pattern has one** —
but that is an argument from the same `grep` that justifies the whole task, and
if it is wrong the failure mode is a green pattern turning red. **Run all 22
before you believe me.**

---

## Outcome (recorded by the manager at the task boundary)

✅ **All three deliverables landed, the acceptance test passes on all three
limbs, and the tree is unchanged where it had to be: 22 verdicts identical,
0 failures, TCB 92 → 92, `--check-stale` 0 STALE.** ⚠ **"Owed" 0, 4 and 18
CLOSE**, and a fourth item was **retired as already-done**.

⚠⚠ **THE MANAGER'S SECOND-LEAST-SURE CALL WAS WRONG, AND THE REPAIR THIS TASK
PRESCRIBED WOULD HAVE BROKEN A GREEN PATTERN.** The task file said the `by_name`
collision *"cannot happen today because no pattern has one of these items"*.
**The collision is real today and has nothing to do with `assume_specification`:
a TRAIT METHOD DECLARATION is body-less**, and `p36-vtable-dispatch/verus.rs`
declares `fn apply` (`:141`) and `spec fn spec_apply` (`:146`) in the trait and
defines them in the impl (`:166`, `:186`). Deleting `parse()`'s
`if body_open is None: continue` — **the obvious repair, and the one the task
file's own hazard note pointed at** — raises
`duplicate item name(s): apply at lines [166, 141]` and turns **p36 red in six
stages**; its other three rung sources declare `apply` the same way.
⚠ **And it would have counted the wrong thing**: a trait method declaration is
not trusted, it is proved by its impl. ⚠ **And `assume_specification` has no `fn`
token at all**, so widening `parse()` would have paid p36's price *and still not
found the target.* ✅ **Manager-verified** (`:141`/`:146` against `:166`/`:186`).

**The engineer's design instead: a separate keyword-keyed matcher**
(`vparse.axiom_decls()`), `parse()` untouched, and `vparse.py selftest` now pins
**both** directions — body-less trait decls stay out of `parse()` *and* are not
counted as axioms. **That is a better design than the one the task specified.**

**What the new stage does, and the shape is deliberate:** counts body-less
trusted declarations, compares against an optional `spec.md` `verus.axioms` key
(**default 0**), `rep.fail("proof-axiom")` on mismatch, `rep.shout("tcb-axiom")`
whenever any exist; the `assume(`/`admit(` scan went `rep.note` → `rep.shout`.
⚠ **VISIBILITY, NOT PROHIBITION** — declare the axiom and it passes, loudly.
⚠ **Deliberately NOT fed into `_is_trusted`**, because stage 5c-twin would then
demand a twin of an item with no body, making a legal declaration unpassable.
✅ **Matcher validated against the pinned vstd, not just the demo: 400 raw-grep
hits, 400 matched, 0 mismatched files.**

✅ **Acceptance limb (c), manager-re-verified**: with two false axioms injected
into `p01/verus.rs`, `parse()` still returns **the same 7 items with the same
names**, `_is_trusted` is unchanged, the obligation count still matches — **every
other pin says green** — and only the new stage fires (`FAIL [proof-axiom]` plus
`!! [tcb-axiom]`). The real file returns `[]`.

**Deliverable 2 — and a published law's CHARACTER moved while its VALUE did
not.** `R3ship − R4` over `nsuf = 1..8` is **18, 23, 30, 37, 44, 49, 56, 63**:
steps of `+5,+7,+7,+7,+5,+7,+7`. ⚠ **`≈7·nsuf + 9` is a straight line through a
STAIRCASE** (max residual 0.81); **lag-4 differencing gives 26 four times with
zero residual = 6.50 `Ir` per request**, a mod-4 sawtooth from the 4×-unrolled
table walk. It **reproduces TASK_015_REVIEW's table byte-for-byte**, now from
committed inputs and a hashed generator. ✅ **No published p17 number is wrong**
— `+32` is the shipped pair at `nsuf = 3` and this band gives 30 there, which
§10 already discloses. **PROVISIONAL, in p17's `NOTES.md` §10b per rule 9.**

**Manager decisions:**

1. ⚠ **The engineer's push-back on the justification is ACCEPTED and is sharper
   than the manager's.** It agreed the batch was worth it but narrowed the
   reason: **the strongest limb is that the accident produces a false green in
   the same edit**, not that Verus prints the declaration. The demonstration
   above is why — every other pin says green. **The manager's framing *"the gate
   cannot see it"* is replaced by *"the gate cannot see it, and nothing else
   catches it either."***
2. **`synthesis/licence.json` was re-emitted BY THE MANAGER**, since `synthesis/`
   was outside the engineer's writable surface and the engineer correctly
   reported rather than reached. ✅ **Verified pure re-certification: 88 pair
   verdicts, 0 licence properties changed, only the pinned hash block moved.**
   ✅ **And `results/synthesis.md` regenerates BYTE-IDENTICAL** — so adding
   `axiom_decls` to 22 gate records moved **no published number**, which is the
   claim the acceptance test was really making.
3. ⚠ **A deferred item was RETIRED AS ALREADY DONE — after fifty tasks.** RECAP
   said stage 3c's `head()` still reads *"recorded as a result"*; it has read
   *"…AND enforced"* since TASK_032. **The correction APPENDED rather than
   replaced, so a naive substring grep still hits it** and every re-audit
   confirmed a live item. ⚠ **A substring search cannot tell a claim from its own
   correction** — third instance of *"a wrong command is worse than a wrong
   constant"*. **Adjacent and queued, not fixed:** `p01/spec.md` still carries the
   retracted `identity | recorded as a result, not a gate condition`.
4. **The sweep cost figure in this task file was wrong: ~45 minutes, not ~30**
   (11:40:41 → 12:26:09; p22 301 s and p01 337 s are the outliers, the rest
   76–203 s). ⚠ **And `check.py`'s stdout is block-buffered when redirected — a
   stalled log is not a stalled process**, and `grep '^check.py:'` is a useless
   completion marker because that is its *first* line.

⚠ **PROTOCOL rule 2's running count is 227:** 223 at TASK_082's writing, **+4** —
the `by_name` collision being live today via p36's trait declarations (the named
least-sure call), the prescribed `parse()` widening being wrong in two
independent ways, the deferred display-string item having been done fifty tasks
ago, and the sweep-cost figure. **Carry 227 forward.**

**The single most useful thing in this block.** ⚠ **The task file named the
hazard, pointed at the exact repair that triggers it, and asserted it could not
fire — all in the same paragraph.** The hazard note said *"making the parser see
more items changes `by_name`… a new item whose name collides turns a green
pattern red"*, and the least-sure call then said the collision *"cannot happen
today because no pattern has one of these items"*. **Both sentences were about
`assume_specification`; the collision was about trait declarations, which the
manager never considered and which are four lines from the thing being counted.**
✅ **What saved it is that the acceptance test was written as "all 22 still PASS
and every TCB count UNCHANGED" rather than "the new items appear"** — a
behavioural test the engineer had to run, and which fails loudly on the wrong
design. **Specify the acceptance test, not the implementation; the implementation
was wrong here and the test caught it.**
