# TASK_068 — the batched `check.py` change: four owed edits, one sweep

**Role:** research engineer.
**Read first:** `.tasks/PROTOCOL.md` (**rule 5's "could this happen by accident?"
test governs item 1**), then `.memory/02-bench-rules.md` (the `forbidden_hits`
arc **and** the stage-7 hole at the end), then `.memory/06-catalogue.md`'s **p22
triage**, then `RECAP.md` "Owed" items **5 and 12**.

**Why these four together.** Each one alone costs a **full 20-gate sweep**,
because `check.py` hashes `harness/*.py` into every gate record and every pattern
doc into its own. Batched, they cost **one**. ⚠ **PROTOCOL rule 5 says prefer a
pattern over gate work; the manager considered it and overrode it** — three of
these are fixes to *measured* defects, not speculative hardening, and the fourth
**unblocks p22**, which is the next pattern and cannot be built without it. **If
you think that trade is wrong, say so before you start.**

⚠ **A sweep script already exists**: `.temp/t60-sweep.sh` (written for 18/19
patterns — check it still does what you need before trusting it).

## Order matters. Do them in this order, and gate between.

### 1 — `forbidden_hits`: make it FAIL

Open since TASK_053, where it was **declined**; re-opened at TASK_062 when it saw
a real defect; TASK_063 settled the underlying defect and recommended **fail,
batched with the next `check.py` change**. This is that change.

- **Today it is `0` across every pattern** (183 forbidden spellings at last
  count; the invariant is the **zero**, not the denominator). So the
  false-positive surface is nil *right now*.
- ⚠ **Apply rule 5's test explicitly and write the answer down: could a
  `forbidden_hit` happen BY ACCIDENT on an honest pattern?** TASK_063's engineer
  argued a counter-case and it is recorded in `.memory/02-bench-rules.md`
  alongside the recommendation. **If the counter-argument now looks stronger than
  the recommendation, say so and leave it printing.** That is a legitimate
  outcome and it costs this task nothing.
- Carry the two figures TASK_063 attached: the **29 hits across 11 patterns**
  that appear if comments/strings/ghost clauses are *not* blanked (that number is
  the value of `spelling_matches`'s blanking half), and the engineer's own
  counter-argument.

### 2 — a contract-declared per-input TIMEOUT, which is what p22 needs

⚠ **This is the item the manager is least sure of and it is a DESIGN question.
Argue with the proposal below before implementing it.**

The problem, measured (`.memory/06-catalogue.md`'s p22 triage): **a hang is
already in the gate's vocabulary** — `run_bin` returns
`(None, "", "<timeout after Ns>")`, `check_adversarial` folds that into an
ordinary behaviour row without crashing, stage 2 excludes adversarial inputs, and
`measure.py` never executes one. **What kills it is `RUN_TIMEOUT = 900`**: p22
hangs 12–20 cells, so **3–5 hours per gate run**, paid again on every doc edit.

**The manager's proposal — measure it, then tell me where it is wrong:**

- `model.py` grows an **optional per-input `run_timeout_s`**, defaulting to
  `RUN_TIMEOUT`. Precedent: `sanitizer_expect` is already a per-input model
  attribute the gate reads (`build_models`, `check.py:1433`).
- **`expected_exit = None` means "this input is expected NOT to terminate."**
  Stage 4 already computes `diverges` against `expected_exit`, so a declared hang
  stops reading as a divergence.
- ⚠ **A NON-adversarial input must never be allowed to declare a hang** — that
  would let a pattern skip stage 2's checksum agreement by declaring the cell
  hangs. **Add that check**; it is the accident this design could enable.

> **What I do not know**: whether the timeout belongs in `model.py` at all rather
> than in the pinned `slb-contract` block. `model.py` is the *independent
> reference*; a declared timeout is arguably a **pin**, and pins live in the
> contract where a change moves `contract_sha256` and shows up in review.
> **Make the call, and write the reasoning down** — this is exactly the kind of
> decision that is invisible later.

**Deliverable beyond the code: a worked example.** Build a throwaway
non-terminating cell under `.temp/p68/` and show the gate recording it in ~5 s
instead of 900. **Do not add it to any pattern.**

### 3 — one token: `-fstrict-aliasing` at `check.py:4739`

Stage 7 builds `gcc -std=c99 -O1 -g -fsanitize=address,undefined`, and gcc
enables `-fstrict-aliasing` only at `-O2`+. So stage 7 **cannot see a flag-gated
UB class**. p38 is the only affected pattern (recounted at TASK_067: **36 `fires`
rows across 15 patterns, all 36 already fire at `-O1`**).

⚠ **Do NOT raise stage 7's optimisation level instead** — that perturbs 20
patterns' sanitizer rows to fix one.

⚠ **The risk this item carries, and it is the one to measure FIRST:** adding
`-fstrict-aliasing` changes the build for **every** pattern's stage 7. **A
pattern that passes today could start miscompiling and diverge.** Before
committing anything, build all 20 patterns' stage-7 C rung with and without the
token and **diff the outcomes**. Report the count. If any pattern other than p38
changes behaviour, **stop and report** — that is a finding, not a chore.

### 4 — the doc-citation sweep (rides along free)

`RECAP` "Owed" 12. **22 `check.py:NNNN` citations across 12 patterns** are
stale — `check.py` grew to ~5460 lines and every insertion moves them.
Spot-checks: p04/p09 `spec.md` cite `:929`, now a **blank line**; p05/p17
`NOTES.md` cite `:1446`, now `return {}`; p10 cites `:1254-1292`, now an
unrelated comment. ⚠ **Not all are wrong** — p47's `:1755-1760` is still right.

- **The rule is: name the FUNCTION, line beside it as a hint** — the convention
  and a tested audit aid are at the end of `.memory/02-bench-rules.md`.
- ⚠ **Dedupe on `file:line:ref`, not on `ref`** — the aid's first version
  collapsed duplicates and found 4 of 5.
- **Also audit CONTROL NAMES**, same class: TASK_066_REVIEW found `s_asan_O3`
  cited in three committed p38 files while being unselectable by name (fixed at
  TASK_067). **No cross-pattern audit exists.** Registries are heterogeneous — a
  dict plus hardcoded prints on p38, a `VARIANTS` list on p47 — so this wants
  `--list` per pattern, not a grep.
- ⚠ **If a pattern's `spec.md` is generated, fix the GENERATOR too and re-run
  it.** Three tasks in a row shipped an edit the generator silently reverted.

## Done when

All four landed (or item 1 explicitly declined with the argument);
**`check.py` green on all 20 patterns**; `measure.py --check-stale` clean; every
pattern whose `spec.md` moved re-generated and verified with
`git show HEAD:… | diff - …`. **Paste the sweep's actual output — all 20
verdicts, not a summary.** ⚠ Doc edits make a gate record STALE: sweep **after**
editing.

⚠ **Measurement records must NOT move.** `measure.py`'s `provenance()` does not
glob `*.md`, and `check.py` is not in its source list — so if `--check-stale`
reports any `results/pNN.json` stale, **something touched a hashed source and you
should stop and report it.**

## Constraints

No root; no `/tmp` (scratch `.temp/p68/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `.memory/`, or `common/`. **You MAY edit `harness/check.py`** —
that is this task — and pattern `*.md`/`controls/` files for item 4 only. **Do
not touch `harness/build.py`**: it is hashed into the *measurement* records, so
one edit costs a full re-measure of 20 patterns. Verus only via `./verus_run.py`.
clang `~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none but gcc on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**. **You are
the only agent running.**

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 143** — 140, plus three from TASK_067 refuting the *review's* numbers
(which the manager had transcribed as given): the blast radius is **15/5, not
16/4** (p04 was missed), the `opaque_off` construction needs the offset opaque on
**one side only**, and `rlen == 1` is a **law term, not an anomaly**.

**What I am least sure of, by name: item 2's design** — whether a declared
timeout is a `model.py` attribute or a `slb-contract` pin. I have argued both
sides above and I do not know. **The deciding question is probably: should
declaring a hang move `contract_sha256`?** If yes it is a pin. Measure nothing;
argue it, write it down, and pick.
