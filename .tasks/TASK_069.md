# TASK_069 — close the two blockers before p22 is written against them

**Role:** research engineer (you made the TASK_068 changes; this is their
corrections task).
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_068_REVIEW_REPORT.md`
in full**, then your own `.temp/p68/NOTES.md`.

**The review returned 2 blockers, 5 majors, 7 minors, and 13 of 38 named attacks
landed.** Do not re-measure the 25 that did not — they are listed with outcomes.

✅ **Your direction on item 1 was upheld**, and specifically: the p27 precedent
passes `.memory/02-bench-rules.md`'s own *"could the check have SEEN it"* rule
that p05's precedent failed. **Keep the fail.** What shipped with it is a
false-positive surface understated by at least five shapes.

⚠ **Both blockers must close before p22 exists**, because **p22 trips both**: it
would write `proof { assert(i + step <= cap); }` to discharge its `decreases`
(B1), and it is the pattern `expected_hang` was built for (B2).

## B1 — `exec_code` blanks CLAUSES only, and 11 of 14 honest shapes now hard-fail

`check.py:715-756`, enforced at `:1265` → `:1402`. Measured **after** `exec_code`
across all 20 shipped `verus.rs`: **270 `assert(` (20/20 files), 126 `spec fn`
(20/20), 77 `proof {` (20/20), 63 `Ghost/ghost` (11/20), 10 `proof fn` (4/20)**.

> ⚠ **The tree already paid for this and nobody noticed.**
> `patterns/p09-bitset/spec.md`'s `idiom.why` — **inside `contract_sha256`** —
> documents the trap and says p09's spec functions spell the index
> `q as int / 64` to dodge it. **p09's author contorted the SPECIFICATION to keep
> an audit count at zero, and since `ce06c21` that contortion is the only thing
> keeping p09 green.** That is the strongest possible argument that the surface
> is real.

**Fix `exec_code` to blank ghost code, not just ghost clauses**: `proof { … }`
blocks, statement-level `assert(…)`, `spec fn` bodies, `proof fn` bodies and
`Ghost`/`ghost` bindings. `spelling_matches`' own stated justification for
blanking invariants — *"they erase before codegen and their arithmetic is over
unbounded `int`"* — **applies verbatim to every one of them**; quote it.

⚠ **Then re-run `.temp/p68rev/fp_probe.py` and report how many of its 14 shapes
still fail.** Four are NOT ghost code and need separate judgement — **say what
you decided and why** for each:

- `#[cfg(test)]` unit test using the forbidden call;
- a hand-written `slb_strlen(` matching forbidden `strlen(`, and
  `rposition(`/`position(`, `split_first()`/`split` — **substring matching**;
- whitespace-collapse (`freq / 64` vs `q / 64`, `tmp + 3` vs `p + 3`);
- a `forbidden` entry that backticks the **replacement** rather than the banned
  spelling (`strcpy(` — use `memcpy(`), which makes `why`'s prose the thing that
  decides.

⚠ **Also close the `#[cfg(slb_twin)]` gap in the same pass** — RECAP "Owed" 10.
It was hygiene while nothing failed; **the hard fail inverted its harm
direction**, and its denominator is now **197 forbidden spellings across 20 files,
every one containing twin bodies**.

## B2 — `run.timeout_s` has no floor: a slow-but-terminating cell is accepted as a hang

`check.py:602`, `:2405`, `:5144`, `:5333-5377`. Measured: `timeout_s = 1e-9` is
accepted; and a real gcc binary that **terminates in 3.5 s**, declared with
`timeout_s: 2`, is recorded as a declared hang with **0 failures** — after which
`check_sanitizers:5144` skips the whole sanitizer expectation and
`check_miri:5361-5377` raises the row BLOCKED.

⚠ **`check_miri:5367-5369`'s comment — *"it cannot be used to skip a Miri check
quietly … stage 4 fails the declaration unless a cell really did run forever"* —
is FALSE**, because *"really did run forever"* is only ever measured against the
author's own budget. **Fix the comment as well as the code; a false comment is
the thing the next reader trusts instead of reading.**

**The review's fix, which the manager endorses: re-run one hung cell at
`min(10 × timeout_s, RUN_TIMEOUT)` and FAIL if it terminates.** Implement it, or
propose better **with the measurement**.

> ⚠ **And record the general point, because it is the real finding.** The review
> answered a question this task asked and the answer is worth more than the bug:
> **every other `slb-contract` pin is either prose-judgeable (`driver.statements`,
> `identity`, `collapse.probe_inputs`) or cross-checked against a measurement
> (`verus.obligations`, identity digests, `miri.required`). `run.timeout_s` is
> NEITHER — the first pin to break that principle** — and it reproduces
> `min_ir_per_work`'s known weakness, which is bounded only by `> 0` and which
> TASK_006_REVIEW drove through the whole gate at `1e-9`
> (`.memory/02-bench-rules.md:345-360`). **The re-run check is what converts it
> into a cross-checked pin.** Say so in the code comment.

## The five majors

**M1 — `check.py:1191-1193`'s *"`CONTROL_CELLS` … which no pattern ships"* is
false.** p01 ships `safe_naive_verus.rs` (5688 B) and its gate record shows
`idiom_audit.rungs: 6`. ✅ **The manager has already fixed
`.memory/02-bench-rules.md:196`, which is where it was copied from** — fix the
`check.py` copy.

**M2 — the vacuity shout fires only when ALL forbidden entries lack backticks, so
the list is FIVE patterns, not two.** `check.py:1422-1437`. **p08 (3 of 4 entries
unaudited), p16 (1 of 2), p17 (2 of 3)** take the `ok` branch and print *"0 hit(s)
over N forbidden spelling(s) … Decidable and ENFORCED"* while most of their
declaration is audited **zero times**. **No selftest constrains that branch** —
add one. ⚠ **And note the trap in the obvious repair**: p05's `forbidden[1]` is
*"a running row pointer"*, which has **no token to backtick**, so backticking
`forbidden[0]` moves p05 *out* of the loud shout into exactly this silent state.
**Make the shout per-entry, not all-or-nothing.**

**M3 — three numbers are wrong against artefacts in the same commit**, and two of
them are the stated **evidence for the hard fail**: `check.py:1171` says **183**
forbidden spellings, the 20 gate records sum to **197** (manager verified
independently); `:1173-1176` says **29 hits across 11 patterns**, re-measured
**40 across 13** (raw 40/13, comments+strings-only 2/2, ghost-only 39/13, both
0/0 — **no decomposition gives 29/11**); `.temp/p68/NOTES.md:14` says **153**
matrix rows, the probe's own JSON gives **143**. ✅ `.memory/` is already
corrected; fix `check.py` and your notes. ⚠ **State the denominators as
recomputable, not as constants** — that is this project's standing lesson and it
has now bitten inside a justification for a hard fail.

**M4 — `expected_hang` silently discharges a `sanitizer_expect: "fires"`
obligation** via a bare `print` rather than `rep.ok`, so it does not appear in
the verdict counts (`:5144-5154`), with no cross-check in `build_models`.

**M5 — `KeyError: 'why'` at `:5502-5505`.** `run_budgets` correctly fails on a
missing `why` but still returns the budgets, and `main` then indexes
`contract['run']['why']`. **The author gets a traceback and NO gate record
instead of the clean failure the guard was written for.** One line.

## The seven minors

m1 `:762-764` `spelling_matches`' docstring still says *"Nothing in this file
calls it against a rung source"* — `idiom_audit:1265` does, **and it now
hard-fails** · m2 `:2409` the failure text's first diagnosis is backwards (*"budget
too short"* makes cells hang, not terminate) · m3 `:1652` *"a pattern that forbids
nothing is legal (p01/p08)"* — p01 declares 1, p08 declares 4, and **no pattern
has `nforb == 0`** · m4 the ≈18% session-shift figure is a **2-observation
high-water mark** (RECAP has p10 at ~8%), and item 3 has an **unnamed third
route**: `measure.py --no-wall` clears the hash without re-taking the wall block
— ⚠ **but it DELETES those rows rather than moving them**, since `measure.py`
never merges; record that trade rather than taking it silently · m5 a declared-hang
input is not excluded from `collapse.probe_inputs`, and `_callgrind_total:1864`
has no `except TimeoutExpired` (latent) · m6 retrofitting `expected_hang` onto an
existing pattern costs a re-measure (`model.py` is in `measurement_sources:228`)
— **document it where a pattern author will see it** · m7 `rung_sources` excludes
`c/kernel.h`, **which is compiled into the rung it audits** (no `static inline`
today, so latent).

## Done when

Both blockers closed, five majors and seven minors addressed or explicitly
declined with a reason; **`.temp/p68rev/fp_probe.py` re-run with its outcome
pasted**; **`check.py` green on all 20 patterns**; `measure.py --check-stale`
clean and **no measurement record moved**. **Paste all 20 verdicts.**
⚠ Use a sweep script whose `rc` is not read after a pipeline — `.temp/p68/sweep.sh`
is the fixed one.

## Constraints

No root; no `/tmp` (scratch `.temp/p69/`; `.temp/p68/` and `.temp/p68rev/` are
readable, not writable); **no `git add`/`git commit`**; do not edit `pilot/`,
`.memory/`, or `common/`. **You MAY edit `harness/check.py`.** ⚠ **Do NOT touch
`harness/build.py`** and **do not edit any pattern's `model.py` or
`inputs/gen.py`** — both are measurement-hashed and would force a re-measure;
if a fix seems to need one, **STOP and report it**. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none but gcc on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**. **You are
the only agent running.**

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 148** — 146, plus the review refuting the manager's **183** premise (it is
197, and the manager verified it independently) and the *"6 citations
(p12, p13 ×3, p16 ×2, p38)"* list, which enumerates **7 sites**.

**What I am least sure of, by name: whether B1's fix should blank ghost code or
whether `forbidden` should simply be scoped to exec code by CONSTRUCTION.**
Blanking is a growing list of syntactic special cases — `proof`, `assert`,
`spec fn`, `proof fn`, `Ghost`, `#[cfg(slb_twin)]`, `#[cfg(test)]` — and every
one this project has added arrived *after* something slipped through. **If there
is a structural way to ask "is this token in code that reaches codegen?" —
`vparse.py` already parses items and clauses — that is worth more than a seventh
special case. Tell me if there is; take the special cases if there is not.**
