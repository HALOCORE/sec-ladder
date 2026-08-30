# TASK_147 — land `p32`'s review corrections, bundled into ONE re-measure

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You own
`harness/check.py`, `harness/measure.py` and the records.

⚠⚠ **RUN THIS BEFORE `TASK_146`** (which builds `p28`). `TASK_146` was written
first and is numbered lower; **execution order is this file, then that one.**
`p32` is built and reviewed but its corrections are not landed, and the loop is
*build → review once → **land corrections** → write the finding*.

⚠⚠⚠ **EVERYTHING HERE IS BUNDLED BECAUSE EACH ITEM COSTS THE SAME RE-RUN AND
DOING THEM SEPARATELY COSTS FOUR.** `model.py` and `c/*` are both in
`measure.py::measurement_sources`, so **M1 and M2 cost a `p32` RE-MEASURE**;
`spec.md` and `controls/*` cost a **re-gate** only. **Budget one re-measure and
one re-gate. Do not run either twice.** (`TASK_141` is the precedent.)

Read first: `.tasks/TASK_145_REPORT.md` **in full** — §4b, §8, §9 especially;
`.tasks/TASK_144_REPORT.md`; `patterns/p32-free-list-pool/`; `RECAP.md`
finding **55**; `.memory/03-measurement.md` entries **12–18**; `PROTOCOL.md`.

## ⚠⚠⚠ M1 — the sharpest, and it is a claim that CANNOT FIRE

**In `spec.md`'s HASHED `idiom.why`, in `README.md`, in `NOTES.md` 2a, in
`sanitizer_expect`'s own docstring, in `TASK_144_REPORT` §4 and in `RECAP` 55:**

> ~~*"`model.py` **DERIVES** that silence rather than declaring it: its
> simulation computes **every index the buggy rung would compute** and reports
> whether one escapes."*~~

**Measured false four ways** (`.temp/t145/touch_probe.py`):

- `Pool.oob` is set only from `_touch(blk.slot)`; a `Block` is constructed at
  **exactly one site**, from `pop()`, which draws from a successor map over
  `0..SLOTS-1`. **The guard `0 <= s < SLOTS` is a TAUTOLOGY of the simulation's
  own representation.** **0 firings in 20 000 fuzzed buggy windows.**
- The one case that *would* set it — `Pool().read(Block(255))` — **crashes the
  model** with `IndexError` on the next line, before `sanitizer_expect` is read.
- It never touches `gen[h]`, `nx[h]` or `regs[r]`, so *"every index the buggy
  rung would compute"* is **false three times over**.
- ⚠ **`M3-nil-test`'s failure mode — the ONE memory-safety failure this row's own
  R5 battery finds — is UNREPRESENTABLE**, because an empty register is `None`,
  never slot 255.

✅ **THE CONCLUSION IS STILL TRUE.** ASan/UBSan/Miri really are silent on all
nine inputs. **What is false is that `model.py` ESTABLISHES it.**

### Choose ONE, and say in `NOTES.md` why

**(a) MAKE THE CHECK REAL** — have the simulation compute the indexes the buggy
rung actually computes (`gen[h]`, `nx[h]`, `regs[r]`, ALLOC's own `pool[s*BLK]`
write) and report an escape, without crashing first.
**(b) RETRACT THE CLAIM** — `sanitizer_expect` is **declared**, and say so in
the same six places, with the reason silence is nonetheless known (the gate ran
ASan/UBSan/Miri; `p27`/`p29` fire on the same machinery).

⚠⚠⚠ **WHICHEVER YOU PICK, IT OWES A MUST-FIRE ARM.** Under (a): an input or a
planted mutation on which `sanitizer_expect` returns `"fires"` — **and
`M3-nil-test`'s slot-255 shape is the natural one, so make it representable.**
Under (b): a one-line demonstration that the field is a constant, so nobody
later "confirms" the derivation by finding nothing. ⚠ **A forward-only fix is
one somebody later confirms by finding nothing** (`TASK_141` repair 2).

⚠ **(a) is the better outcome if it is reachable — but do NOT force it.** If the
honest answer is that a Python simulation of a pool cannot represent an
out-of-range slot without becoming the C kernel, **that is a finding and (b) is
correct.** Report the cost either way.

## M2 — `c/kernel.h` says THREE SITES

`c/kernel.h:73` and `:143` say the safety line is at **three sites**, against
**six** other places including the hashed contract **twice**, and against a
control that fails at ≠1. **Stale text from `TASK_143`'s three-site
demonstration.** ⚠ `c/*` is measurement-hashed — this is why it rides here.

## M3 — `controls/storage_arms.py`, two narrowings

1. Its docstring calls the `c-arena` arm *"the SHIPPED C kernels … exactly as
   `harness/build.py` builds them"*. **`build()` never compiles `c/kernel.c`.**
   ✅ **The reviewer closed the conclusion by measurement — driving the shipped
   rungs on the control's own op streams, 10/10 match — so fix the DESCRIPTION
   and cite that run; do not re-derive it.**
2. ⚠⚠ **The two storage cells do NOT differ only in storage: a 17-line teardown
   differs as well.** *"One C source, storage the only variable"* is **narrowed**
   wherever it appears. ✅ **The aborts ARE the bug** — ASan frames put
   `attempting double-free` at `arm_body.inc:112` and `heap-use-after-free` at
   `:119`, and **the teardown's `free` at `:148` appears in no trace.** Say the
   narrowed thing and keep the evidence.

## ✅ RIDE-ALONGS the review earned — land these, they are the good half

1. ⚠⚠ **ADD `X3-spec-only-weaken` TO `controls/proof_mutants.py`.** The reviewer
   built it and **it FAILS**, which the shipped battery lacked. With it the R5
   headline becomes a **three-cell result** — **exec-only → fail, spec-only →
   fail, both → verify** — instead of one must-verify arm asserted alone.
   **Take the reviewer's arm; re-derive its verdict, do not quote it.**
2. **Give `controls/repro.py` a NEGATIVE CONTROL.** It ships with none. The
   reviewer used `p29`'s R1 (20/20 distinct at `randomize_va_space=2`) and
   `p32`'s 1-of-20 claim survived. ⚠ **A reproducibility test is evidence only
   once it has been shown capable of failing** — the manager's
   `.temp/mgr146/aslr/k.c` is the same shape.
3. **Minors, all from `TASK_145_REPORT` §8:** `Pool`'s docstring says *"no
   generation counter anywhere"* over an `__init__` that declares one (`rel[]`,
   bumped by every FREE, folded as `8 * rel[s]`) — ✅ **the true and sufficient
   claim is narrower: NO COUNTER IN THE STALENESS TEST**; `arm_forgeable.c`'s
   `alias` flag is true of a *correct* allocator and its line is quoted as
   evidence; `spec.md` says *"four operations"* where everything else says
   **five**; `NOTES.md` §10 compares twinned-item count against total-trusted
   count (the gate required **3** twin sections for `p32`'s **5** trusted items;
   `p27` and `p29` have **7** each — §4's TCB sentence is correct and §10's is
   not).

## ⚠ NOT in this task — recorded so it is not silently absorbed

- **`assume(false)` verifies `15/0` while `check.py` only SHOUTS
  `[tcb-axiom]`.** ⚠ **This is a GATE finding, not a `p32` defect** — `p32`'s own
  `assume(` count is `0`. `check.py` is in the gate digest, so changing it costs
  a **28-pattern re-gate**, which is a different bundle. **Leave it. Report if
  you disagree.**
- **RECAP finding 54's `p32 +9/−0` with no forward pointer to `+2/−0`.** The
  manager owns `RECAP.md`; do not edit it.

## Then

`harness/check.py p32` → PASS · `harness/measure.py` for `p32` ·
`harness/report.py p32` if the gate fails on `[tables]` · then
`harness/measure.py --check-stale` (expect **0 STALE**),
`harness/tools/composition.py --check`, `harness/tools/temp_citations.py`, and
`python3 synthesis/synthesize.py`.
⚠⚠ **`results/SYNTHESIS.md` (CAPITALS) is HAND-WRITTEN — NEVER regenerate over
it.** ⚠ **Read `blocked` out of the RECORD, never `grep` the log.** Expect
`p01 = 1`, `p42 = 1`; `p42` may legitimately be 2.

## Rules

- `.temp/t147/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`** — the manager applies those. No `git add`/`git commit`.
- ⚠ **Do not touch `.temp/t136/ t137/ t139/ t140/ t141/ t142/ t143/ t144/ t145/
  t91/ mgr146/ mgr147/ mgr148/ mgr149/`** — all cited evidence. **Copy from
  `t145/`; do not modify it.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate a sanitiser log
  with `head`; every harm probe owes a positive control that must fire.
- ⚠ **Generate control JSONs AFTER the sources are final** — `TASK_139` edited
  doc comments after generating them and paid a re-measure.
- ⚠ **Expect `p32`'s measurement record to move on wall-clock, timestamps and
  hashes and NOT on `Ir`/`md5`/identity/checksum.** `TASK_141` saw 102 of 1345
  leaves move that way and the reviewer saw **2 of 1318**. **If an `Ir` or an
  identity leaf moves, STOP: that is not a comment edit** — unless you took M1
  option (a), which changes `model.py`'s *behaviour* and may legitimately move a
  `model_stdout`. **Say which you expected before you look.**
- Keep the generator, delete the artefact (`.memory/00-environment.md`
  constraint 6).
- ⚠ **If any item costs more than this file says, STOP AND REPORT rather than
  half-landing it.** The tree is green; leaving it green and reporting a cost is
  strictly better than leaving it half-changed.
- Report to `.tasks/TASK_147_REPORT.md`. **PROTOCOL rule 2: the count is in
  `TASK_145_REPORT.md`'s closing paragraph — read it there, do not guess.**
