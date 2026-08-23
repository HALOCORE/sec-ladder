# TASK_077_REVIEW — the batched gate task whose predecessor's review found two blockers

**Role:** research reviewer. **Adversarial by design.** You do **not** fix; you
report. A review that says "looks good" without having tried to break something
is a failed review.

**Read first:** `.tasks/PROTOCOL.md` (roles, reviewer checklist, severity), then
`.tasks/TASK_077.md`, then **`.temp/p77/NOTES.md` in full** (492 lines), then
⚠ **`.tasks/TASK_068_REVIEW_REPORT.md`** — the last batched gate task, whose
review found **2 blockers and 5 majors in work that reported success, past a
fully green sweep**. **That is the prior for this one, and both of its blockers
turned out to matter on the very next pattern built.**

The tree is green: **22 patterns, 21 `PASS` + 1 `PASS-WITH-BLOCKED-ROWS`
(p01 only), 0 failures, 44 records 0 STALE**, committed at `01bf438`.
**PROTOCOL rule 9 holds everything out of `.memory/` until you land.**

⚠ **The engineer refuted three premises and declined an item the task file
authorised.** Those are dead. **Attack the replacements**, and note that
**RECAP "Owed" 14, 19a, 19b and 20 are all claimed closed by this one task** —
four standing items retiring together deserves more scepticism than one.

## A0 — a gate stage got WEAKER-LOOKING and the engineer says it got stronger

**p22 moved `PASS-WITH-BLOCKED-ROWS` → `PASS`.** ⚠ **That is exactly the shape a
weakened check takes**, and the engineer offers five grounds: the block's
premise was false (verified outside `check.py` — `miri` on p22's shipped
`unsafe.rs` gives `rc=0`, no UB, 0.2 s); the new condition is stage 4's
*measured* per-rung `hung` column rather than a per-input declaration; **the
block still fires in two constructed cases**; 0 added lines touch the
`ub`/`returncode`/`stdout` chain that TASK_051_REVIEW M6 hardened; and
unchecked-for-UB rows go **1 → 0** while confirmed hang cells go **1 → 4**.

> **Test all five, and then test the one they do not make.** ⚠ **Can you
> construct a pattern shape where `_hung_rungs` returns the wrong rung set and a
> row that SHOULD be blocked runs and passes?** Stage 4 measures; a measurement
> can be wrong. **What happens if a rung hangs only at `-O3`, or only on one
> input, or only in `whole` mode?** The old code was per-input and provably
> wrong; per-rung is better, but *better* is not *right*.
> **And check the comment matches the code** — TASK_069 already had to fix a
> false comment in this exact function, and a false comment is what the next
> reader trusts instead of reading.

## A1 — item 5's decline, and the sub-claim rejected ON THE MERITS

`harness/asm.py` was **authorised by the task file** and the engineer **declined
it**, measuring that it sits at `measure.py::measurement_sources:233` — one line
below `build.py:232` — and stales **18 measurement records**, i.e. `build.py`'s
tree-wide radius, which the same task file forbids for that reason.

> ✅ **The manager accepts the decline. Verify the measurement anyway** — it is
> the load-bearing fact and it was produced by the agent it exonerates.
> ⚠ **The sharper item is `__popcountdi2`, REJECTED rather than deferred.** The
> argument: `is_bulk_symbol`'s contract is *"is this call the kernel's loop?"*,
> scoped to routines scanning or copying an unbounded run of the **caller's
> bytes**; `__popcountdi2` is a libgcc arithmetic helper over **one register**,
> the class `_BULK_STR_WORDS` explicitly excludes (`strtoul`, `strerror`); and
> widening it would also widen **gate stage 3a**'s anti-collapse escape hatch.
> **Is that right?** RECAP "Owed" 22 — which the manager wrote — calls it a
> defect. **If the engineer is right, RECAP is wrong and p09's real need is the
> outward-dispatch list, a different question.** ⚠ **Check the stage 3a
> consequence specifically**; that is the part that would have turned a "fix"
> into a regression.
> **And check `bcmp` and p11 are correctly classified** — table defect vs stale
> record. **Getting that distinction wrong is how "Owed" 6 stood closed for ten
> tasks.**

## A2 — 97 measurement leaves moved and the engineer says it is not this task's doing

`marginal_ir_per_call` moved on **97 leaves**: `isolated` max |Δ| **0.14**,
`whole` max |Δ| **7.14**. The attributed mechanism is **7 `Ir`/call in
`__memset_avx2_unaligned_erms` from stack-array alignment**, and the probe is
that **adding one environment variable restores the committed values exactly**
(3/3 runs) where its absence gives the new ones (2/2).

> ⚠ **This is the most dangerous claim in the delivery, because it exonerates
> the delivery.** *"Not mine"* is exactly what a subtle regression would also
> say. **Attack it:**
> - **Reproduce the environment-variable probe independently.** If it holds, the
>   mechanism is real and `p03/NOTES.md` §3b already names it.
> - **p03 and p04 had no file of theirs changed** — verify that, from `git`, not
>   from the report.
> - ⚠ **Does any published number rest on a `whole`-mode marginal?** The engineer
>   says no, because `synthesis/synthesize.py::marginal` defaults to
>   `mode="isolated"`. **Check every consumer**, not just that one.
> - **`check_marginal_ir`'s "quote to the instruction, never to the hundredth"
>   reads as ±1 and the measured spread is ±7.** Is the proposed rule — *never
>   quote a `whole`-mode marginal across sessions* — the right one, or too
>   narrow?

## A3 — a published table moved, and the threshold is a cliff

**p38's discard count went 3 → 6.** `Ir` **48/48**, static **32/32**, checksums
**32/32 byte-identical**; 64 wall figures moved by **median 0.50%, max 3.62%** —
yet the **10% min-to-median threshold flipped on 5 cells, all on `small.bin`**,
and **both independent re-measures landed on 6.**

> **Verify the byte-identity claims** — they are what makes this a presentation
> change rather than a result change. **Then ask the question the engineer
> raised and did not settle: is a 10% cliff the right instrument at all**, if a
> 0.50% median movement reclassifies 16% of cells? ⚠ **And check the claim that
> no p38 prose quotes a discarded cell**; if one does, a published claim moved.
> ✅ **Third data point for "Owed" 14's ≈18% estimate** — p08 ~18%, p10 ~8%,
> p38 **3.62%**. **Is the estimate now wrong enough to restate?**

## Also in scope

- **Item 1's blast radius, re-derived as 158 rows / 3 differ / all 3 on p38.**
  Verify, and verify p38's new `sanitizer_expect` is **derived** rather than
  fitted to the answer — it walks the window *"the way the miscompiled build
  does"*, which is a model of a miscompilation and could be tuned until 8/8
  agreed. **Would it have been wrong on a ninth input?**
- **Item 4 is a NO-OP on today's tree by the engineer's own admission** — no
  pattern exercises either path and the qualified `--verify-function` was only
  tested on a synthetic file. ⚠ **So RECAP "Owed" 20 is closed by untested-on-a-
  real-pattern code.** Is fail-closed really fail-closed? **Try to construct the
  silent case.**
- **`check.py:5242`'s `--verify-function` justification is refuted** — Verus
  errors with *"more than one match found"* and **matches by substring**, so
  `apply` matches `spec_apply`. Verify both halves; the substring behaviour is
  a live hazard for any future pattern.
- **The `fires` census is stale in three places** — recounted **17 patterns / 40
  rows / 158 total**, against the task file's 16, `.memory/02-bench-rules.md`'s
  **15/36**, and p38's README's *"20 gate records"*. **Recount independently.**
- ⚠ **`results/tables/*.md` is systematically stale — all 22 of 22** differ from
  what `report.py` produces today; p09/p27/p36 cite a superseded
  `contract_sha256` and p12/p27 publish pre-TASK_069 audit counts. **Hashed
  nowhere, so nothing ever detected it.** **Verify the scope and confirm
  regenerating costs no gate run and no re-measure** — the manager intends to do
  it and wants the claim checked first.
- **Committed sentences the changes make false.** ⚠ **`p22/spec.md:577` is
  INSIDE the `slb-contract` block** (215–581), so fixing *"p22 therefore lands
  PASS-WITH-BLOCKED-ROWS"* moves `contract_sha256` and owes the direction test;
  **`p38/spec.md:202` is GENERATED** by `controls/mkcontract.py`. **Check the
  list in `.temp/p77/NOTES.md` is complete** — a missed one is a shipped
  falsehood.
- **"Owed" 5 was argued and declined**, recommendation *leave the glob alone*,
  on the ground that the item's test (*"the gate never executes it"*) is the
  wrong one and the right one is *"does a committed claim depend on it"* — 64
  committed doc references, and `harness/limbs.py:14-19` already decided it.
  **Is that argument sound?**

## Clean negatives are wanted

PROTOCOL rule 6. Recent reviews returned 35, 38, 41, 48 and 54 named attacks.
**List every attack you ran with its outcome.**

## Constraints

No root; no `/tmp` (scratch **`.temp/p77rev/`** — ⚠ **`ls` any scratch path
before writing; `.temp/pNN/` collides between patterns and tasks**; read
`.temp/p77/` but do not modify it); **no `git add`/`git commit`**; do not edit
`pilot/`, `.memory/`, `harness/`, `common/`, **any** file under `patterns/`, or
**anything under `synthesis/`**. You may re-run `harness/check.py` — ⚠ **a gate
run rewrites that pattern's record, so restore with `git checkout --` and say
that you did.** ⚠ **Any re-measure runs in the FOREGROUND and alone**;
`measure.py` rewrites a measurement record — **prefer not to run it at all**,
and if you must, restore and say so. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — **none but gcc on
PATH**. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; **no
self-matching `pgrep` wait-loops.** **You are the only agent running.**

⚠ **A practical note that cost the manager two errors this arc**: `git status`
tells you **THAT** a file differs from `HEAD`, never **WHEN** it changed, and
`ls -l` with `%H:%M` silently compares yesterday's 19:56 as later than today's
18:55. **Use `stat -c %Y` and epoch seconds** for any "did this change after
X" question.

**Write `.tasks/TASK_077_REVIEW_REPORT.md` before you finish** (rule 10), then
return the same content in the report format. Rank findings `blocker` · `major` ·
`minor`, with **file:function** (⚠ not `file:line`) and a concrete failure
scenario. **Do not pad.**

**If a premise here is wrong, say so with the measurement.** ⚠ **Running count
188** — 184, plus this task's four: `asm.py`'s blast radius being `build.py`'s
(the task file authorised it), `check.py`'s `--verify-function` justification,
the `fires` census being stale in three places, and RECAP "Owed" 5's test being
the wrong test.

**What I am least sure of, by name: A0 and A2, and they share a shape.** Both
are cases where **the thing that would look identical to a regression is being
reported as an improvement**, by the agent that made the change: a gate row that
now runs where it used to be blocked, and 97 moved measurement leaves attributed
to a mechanism that predates the task. **The engineer's evidence is good in both
cases. It is also exactly the evidence someone would assemble if they were
wrong.** Settle them before anything reaches `.memory/`.
