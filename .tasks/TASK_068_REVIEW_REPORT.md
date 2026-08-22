# TASK_068_REVIEW — report

Reviewer, adversarial. Target: `ce06c21` (`harness/check.py` +421 lines, 3 of 4
batched items landed). **2 blockers, 5 majors, 6 minors, 24 named attacks of
which 13 landed.** All scratch under `.temp/p68rev/`; `.temp/p68/` unmodified.

**Verdict on the manager's least-certain call (should item 1 have shipped?):**
the *direction* is right and the accident test was applied correctly — but
**item 1 shipped with its false-positive surface understated by at least five
shapes, one of which is documented in a shipped pattern's own contract and
present in 20 of 20 `verus.rs` files.** Keep the fail; fix `exec_code` before
another pattern is written against it (B1).

---

## Blockers

### B1 — an honest pattern that this now blocks: ghost code that `exec_code` does not blank
`harness/check.py:715-756` (`_blank_ghost` / `exec_code`), enforced at
`:1265` → `:1402`.

`exec_code` blanks Verus **clauses** only — the nine keywords in `_GHOST_KW`.
It does **not** blank `proof { … }` blocks, statement-level `assert(…)`,
`spec fn` bodies, `proof fn` bodies or `Ghost`/`ghost` bindings. Measured
across all 20 shipped `verus.rs`, *after* `exec_code`:

| construct surviving into the audit | count | files |
|---|---:|---:|
| `assert(` | 270 | 20/20 |
| `spec fn` | 126 | 20/20 |
| `proof {` | 77 | 20/20 |
| `Ghost`/`ghost` | 63 | 11/20 |
| `proof fn` | 10 | 4/20 |

`spelling_matches`' own justification for blanking invariants — *"they erase
before codegen and their arithmetic is over unbounded `int`, so they cannot
carry the overflow an additive spelling is forbidden for"* — applies verbatim to
every one of these. Before TASK_068 a hit here moved a printed counter. Since
TASK_068 it **hard-fails the pattern**.

**It is not hypothetical; the tree already paid for it.** `patterns/p09-bitset/spec.md`'s
`idiom.why` (inside `contract_sha256`) says so verbatim:

> *"`check.py::exec_code` blanks Verus ghost CLAUSES (`requires`/`ensures`/`invariant`/`decreases`)
> and does NOT blank a `spec fn` BODY, so a forbidden entry of `q / 64` would fire on p09's own
> `verus.rs` if the specification spelled the index that way — p16's `verus.rs:275` trap exactly.
> p09's spec functions therefore spell it `q as int / 64` …"*

p09's author **contorted the specification** to keep an audit *count* at 0.
Since `ce06c21` that contortion is the only thing keeping p09 **green**.

Constructed honest pattern that is now blocked (`.temp/p68rev/fp_probe.py`,
cases 1-3, each `1 hit → GATE FAILS`):

```
verus `proof {}` block spells the forbidden additive form   1 hit  *** GATE FAILS ***
verus `spec fn` body spells the forbidden additive form     1 hit  *** GATE FAILS ***
verus `assert(...)` at statement level                      1 hit  *** GATE FAILS ***
```

**Failure scenario, on the next pattern:** p22 — the pattern item 2 exists to
unblock — forbids an additive probe-index spelling and writes
`proof { assert(i + step <= cap); }` to discharge its `decreases`. Gate: `FAIL
[idiom-forbidden]`, and the failure text points the debugger at *two* "known
false-positive shapes", neither of which is this one.

Same probe found four more shapes the failure text does not name, 11 of 14
honest shapes blocked in total:

| shape | blocked? |
|---|---|
| `#[cfg(slb_twin)]` twin body | yes (named in the text) |
| `#[cfg(test)]` module | yes (**not** named) |
| hand-written replacement helper `slb_strlen(` vs forbidden `` `strlen(` `` | yes (**not** named) |
| `rposition(` vs forbidden `` `position(` ``; `split_first()` vs `` `split` `` | yes (**not** named) |
| whitespace-collapse cross-token: `freq / 64` vs `` `q / 64` ``, `tmp + 3` vs `` `p + 3` `` | yes (**not** named) |
| forbidden entry backticks the **replacement** (`` `strcpy(` — use `memcpy(` ``) | yes (**not** named) |
| comment / string literal / raw string / loop invariant | **no** — correctly blanked |

The last one is live-shaped: the tree's `required` entries already write in
exactly that style (`idiom_audit`'s own docstring quotes p08's *"written `%` and
not `&`"*), and nothing stops the same prose in a `forbidden` entry, where
**every** backticked span becomes a forbidden token.

**Fix before the next pattern:** extend `exec_code` to blank `proof`/`assert`/
`spec fn`/`proof fn` bodies and `#[cfg(slb_twin)]` items; name the remaining
shapes in the failure text.

### B2 — `run.timeout_s` has no floor, and a slow-but-terminating cell is accepted as a declared hang — which skips stage 7 and stage 8 on that input
`harness/check.py:602` (range check), `:2405` (stage 4), `:5144` (stage 7),
`:5333-5377` (stage 8). Reproduce: `.temp/p68rev/hang_attack.py`.

**Smallest accepted `timeout_s` — measured, there is no floor:**

```
timeout_s=1e-09    -> accepted={'adversarial-full': 1e-09}  failures=0
timeout_s=0.001    -> accepted={'adversarial-full': 0.001}  failures=0
timeout_s=901 / 0 / -1 / True  -> rejected
```

`:602` is `not 0 < secs <= RUN_TIMEOUT`. Any positive float passes.

**A genuinely terminating cell reads as a declared hang.** A real gcc binary
that finishes in **3.5 s**, declared `expected_hang` with `timeout_s: 2`:

```
== 4. adversarial inputs ...
    -- adversarial-full.bin: ... [declared NON-TERMINATING; budget 2s]
       c-gcc  O0/isolated  exit=None  stderr='<timeout after 2s>'  <-- diverges  [DID NOT TERMINATE]
    ok   adversarial-full.bin: declared non-terminating and 1 of 1 cell(s) did not
         terminate within 2s (RUN_TIMEOUT is 900s; the budget is a `contract_sha256` pin).
    stage-4 failures = 0   -> ACCEPTED AS A DECLARED HANG
    (control, no budget) real runtime = 3.5s, exit=0, stdout='41098211948544'  <-- it TERMINATES
```

Once a row is "hung":
* `check_sanitizers:5144` (`if hangs and rc is None:`) precedes the
  `elif expect == "fires"` arm — the whole sanitizer expectation for that input
  is skipped, in **both** directions;
* `check_miri:5361-5377` raises the row **BLOCKED** — the input is unchecked for UB.

**Nothing re-runs a "hung" cell at a longer budget**, so "hang" and "slow" are
indistinguishable to the gate. Stage 4 fails only in the *other* direction
(nothing hung). `check_miri:5367-5369`'s comment —

> *"it cannot be used to skip a Miri check quietly, because only an `adversarial*`
> input may declare a hang and stage 4 fails the declaration unless a cell really
> did run forever"*

— **is false as written**: "really did run forever" is evaluated only against
the author's own budget, and the run above satisfies it with a cell that
terminates.

**The precedent the write-up should have cited and did not.**
`.memory/02-bench-rules.md:345-360` already records the tree's other
author-written number whose only lower bound is `> 0`: TASK_006_REVIEW passed
the whole gate with `min_ir_per_work = 1e-9` and `why = "see NOTES.md"`, because
*nothing inspects `why` — it is free text*. `run.timeout_s` reproduces that
shape exactly, on a knob that switches **two checks off** rather than loosening
one floor. Answering A3's second half: **every other pin in a `slb-contract`
block is either prose-judgeable (`driver.statements`, `driver.regions`,
`identity`, `collapse.probe_inputs`) or cross-checked against a measurement
(`verus.obligations`, `identity` digests, `miri.required`).** `run.timeout_s` is
neither — the stated principle holds of the existing pins, and this is the first
pin to break it.

**Cheap fix:** after a declared hang is recorded, re-run **one** hung cell at
`min(10 × timeout_s, RUN_TIMEOUT)` and fail if it terminates. That converts the
declaration from self-certifying to declared-vs-measured, which is the model
`.memory/02-bench-rules.md` names as the one to copy.

---

## Majors

### M1 — the failure text says one of its two named false-positive shapes is unreachable. It is live on p01.
`harness/check.py:1191-1193` (carried verbatim from `.memory/02-bench-rules.md:196`):

> *"`rung_sources` includes `CONTROL_CELLS`, today `["safe_naive_verus"]`, **which no pattern ships**."*

```
$ ls -l patterns/p01-array-sum/safe_naive_verus.rs
-rw-rw-r-- 1 apt apt 5688 Aug 15 17:48 patterns/p01-array-sum/safe_naive_verus.rs
$ python3 -c "...C.rung_sources('patterns/p01-array-sum')"
[('c/kernel.c','c'),('safe_naive.rs','rust'),('safe_tuned.rs','rust'),
 ('unsafe.rs','rust'),('verus.rs','rust'),('safe_naive_verus.rs','rust')]
$ results/gate/p01-array-sum.json  ->  idiom_audit.rungs = 6
```

p01 ships it, it is p01's 6th audited rung, and it is a **control cell, not a
rung of the ladder**. So a future p01 `forbidden` pin is hard-enforced against a
cell that is by construction a *different* implementation — and the failure text
tells the debugger that shape was ruled out. Both `check.py` and the
authoritative `.memory/` layer are wrong; one `ls` refutes them.
(Latent today: 0 tokens appear in p01's control cell and in no measured rung.)

### M2 — the vacuous-audit shout only fires when **all** forbidden entries lack backticks. The "list of 2" is a list of 5.
`harness/check.py:1422-1437`. The `elif nforb:` shout is reached only when
`forbidden_spellings == 0`. A pattern with *some* backticked entries takes the
`elif au["forbidden_spellings"]:` branch and gets a clean

> `ok idiom forbidden: 0 hit(s) over N forbidden spelling(s) … Decidable and ENFORCED since TASK_068`

Measured across all 20:

| pattern | forbidden entries | backticked | **prose (unaudited)** | verdict |
|---|---:|---:|---:|---|
| p01 | 1 | 0 | **1** | shout (vacuous) |
| p05 | 2 | 0 | **2** | shout (vacuous) |
| **p08** | 4 | 1 | **3** | **`ok` — 3 of 4 entries audited zero times** |
| **p16** | 2 | 1 | **1** | **`ok` — 1 of 2** |
| **p17** | 3 | 1 | **2** | **`ok` — 2 of 3** |
| other 15 | — | all | 0 | `ok`, correct |

p17's two silent entries are *"unsigned start/end"* and *"a window-relative sign
guard where a slice-relative one is meant, and vice versa"* — real declarations
the new `ok` line now asserts enforcement over. This is the p09 vacuous-truth
defect one degree weaker, and the mutation test confirms **no selftest
constrains this branch** (`.temp/p68rev/selftest_mutants.py` M5 survives).

**And the prescribed repair makes p05 worse.** The shout says *"Backtick every
`forbidden` entry you want enforced"*. p05's `forbidden[1]` is *"a running row
pointer"* — a structural property with **no token to backtick**. Backticking
`forbidden[0]` moves p05 out of the loud state into exactly this silent one:

```
p05 backtick as '`chunks_exact`'        -> spellings=2 hits=0  green
p05 'a running row pointer'             -> spellings=0         still vacuous, forever
```

(p01's obvious backticking, `` `v_len` ``, is safe — it occurs only in a comment.)

### M3 — three numbers in the new justification are wrong against artefacts committed in the same commit
* `check.py:1171` *"183 forbidden spellings at the time of writing"* — the 20
  gate records **written by this task's own sweep** sum to **197**
  (183 is the pre-p38 count; p38 contributes 14).
* `check.py:1173-1176` *"the same sweep with comments, string literals and ghost
  clauses NOT blanked gives 29 hits across 11 patterns"* — re-measured:
  **40 hits across 13 patterns**. No decomposition reproduces 29/11:

  ```
  raw (no blanking)             ->  40 hits across 13 patterns
  comments+strings blanked only ->   2 hits across  2 patterns
  ghost clauses blanked only    ->  39 hits across 13 patterns
  shipped exec_code (both)      ->   0 hits across  0 patterns
  ```
* `.temp/p68/NOTES.md:14` and the commit message *"153 matrix rows × 20
  patterns"* — the probe's own `aliasing_probe.json` sums `n_inputs` to
  **143**, and `inputs_of` over the 20 patterns independently gives **143**.

Both `forbidden` figures are the stated *evidence* for turning a printed number
into a hard fail, and both were transcribed from `.memory/`/the task file rather
than re-measured. (The task file told the engineer to *carry* them — so
`TASK_068.md`'s own "183 forbidden spellings at last count" is the wrong
premise, with the measurement above.)

### M4 — `expected_hang` silently discharges a `sanitizer_expect: "fires"` obligation
`harness/check.py:5144-5154`. The hang arm precedes `elif expect == "fires"`, so
if a model declares both on one input and the ASan C rung times out, the check
that *"the adversarial input is supposed to be the one that triggers this
pattern's bug; if it does not, the security half of the result is unsupported"*
never runs. It is discharged by a bare `print(…)`, **not** `rep.ok`, so it does
not appear in the verdict's counts either. `build_models:1698-1712` validates
`sanitizer_expect` and `expected_hang` independently and never cross-checks them.

### M5 — the gate crashes with `KeyError: 'why'` on a malformed `run` block
`harness/check.py:5502-5505`. `run_budgets` correctly `rep.fail`s when `why` is
missing (`:585-589`) but still **returns the parsed budgets**; `main` then does

```python
budgets = run_budgets(contract, rep, all_stems)
if budgets:
    print(f"  run budgets {budgets} s (RUN_TIMEOUT {RUN_TIMEOUT}s "
          f"otherwise) -- {contract['run']['why']}")     # <-- KeyError
```

Reproduced (`.temp/p68rev/hang_attack.py` H4): `run_budgets` returns
`{'adversarial-full': 5}` with 1 failure, then `contract['run']['why']` raises.
The author gets a Python traceback, **no verdict and no `results/gate/*.json`**,
instead of the clean failure the guard was written to produce. One line:
`contract['run'].get('why')`.

---

## Minors

* **m1 — `check.py:762-764`: the definition every backticked pin in the tree
  refers to now contradicts itself.** `spelling_matches`' docstring still reads
  *"This is a DEFINITION, not a gate check. Nothing in this file calls it
  against a rung source: stage 0b is presence-only…"*. `idiom_audit:1265` calls
  it against every rung source and since TASK_068 the result hard-fails.
  Untouched by `ce06c21`.
* **m2 — `check.py:2405-2411`: the new failure text's first diagnosis is
  backwards.** *"all N cell(s) terminated inside the {budget}s budget. Either
  the budget is too short to be a hang detector at all, or …"* — a *too short*
  budget makes cells appear to **hang**, which is the branch that cannot be
  reached here.
* **m3 — `check.py:1652`: the new selftest cites two patterns that refute it.**
  *"A pattern that forbids nothing is legal (p01/p08)"* — p01 declares 1
  forbidden entry and p08 declares 4. **No pattern in the tree has
  `nforb == 0`**, so case 3 is unreachable on the shipped tree, and p01 is in
  fact case 4's shape — which the same commit's `NOTES.md` says.
* **m4 — the ≈18% session-shift figure is a 2-observation high-water mark.**
  `.memory/03-measurement.md:632-638` records p08 at ~18%; `RECAP.md:1528-1530`
  records p10's TASK_059 re-measure at **~8%**. Item 3's scheduling argument
  survives at 8%, but 18% is quoted as *the* figure.
  Also: **item 3 has one route the write-up does not name** —
  `measure.py --no-wall` (`measure.py:432, 557`) clears `source_sha256` without
  re-taking the wall block. It does not *move* p38's timing rows; it **deletes**
  them, because `measure.py` writes a fresh `doc` and never merges
  (`measure.py:451-578`). Whether that is better is the manager's call, but it
  is a third option beside "bundle it" and "don't".
* **m5 — a declared-hang input is not excluded from `collapse.probe_inputs`, and
  `_callgrind_total` (`check.py:1864-1877`) has no `except TimeoutExpired`.** No
  shipped pattern names an adversarial probe input (all 20 use
  `["small.bin","large.bin"]`), so this is latent — but if p22 did, `run.timeout_s`
  would not apply and the gate would die with an uncaught traceback after
  `RUN_TIMEOUT`.
* **m6 — retrofitting `expected_hang` onto an existing pattern costs a
  re-measure**, because `model.py` is in `measure.py::measurement_sources:228`.
  Free for p22 (new); not free for anything already measured. Same trap that
  blocked item 3, not stated in the design write-up.
  (Nit inside this: `stem = name[:-4] if name.endswith(".bin") else name` is
  written three times — `:1726`, `:2350`, `:5125` — with no helper.)
* **m7 — the audit's coverage excludes `c/kernel.h`, which is compiled into the
  rung it audits.** `rung_sources:1111-1125` reads `c/kernel.c`,
  `c/kernel_hardened.c` and the `RUST_SRC` map. All 20 patterns ship a
  `c/kernel.h` and a `c/main.c`, neither audited. No `kernel.h` contains a
  `static inline` today, so this is latent — but it is the honest-refactor
  escape route, and it is the same coverage class
  `.memory/02-bench-rules.md:137-150` named when it *declined* this check.

---

## Attacks run, with outcomes (24; 13 landed)

### `forbidden_hits` (A1) — `.temp/p68rev/fp_probe.py`, `.temp/p68rev/selftest_mutants.py`
| # | attack | outcome |
|---|---|---|
| 1 | forbidden spelling in a Verus `proof {}` block | **LANDED** → B1 |
| 2 | forbidden spelling in a `spec fn` body | **LANDED** → B1 (already disclosed in p09's own contract) |
| 3 | forbidden spelling in a statement-level `assert(…)` | **LANDED** → B1 |
| 4 | forbidden spelling in a `#[cfg(slb_twin)]` body | **LANDED** (named in the text; 43 `cfg(slb_twin)` attributes, **20/20** files) |
| 5 | forbidden spelling in a `#[cfg(test)]` module | **LANDED**, not named |
| 6 | substring of a longer identifier (`slb_strlen(` vs `` `strlen(` ``) | **LANDED**, not named |
| 7 | `rposition(` vs `` `position(` ``, `split_first()` vs `` `split` `` | **LANDED**, not named (p47 and p11 ship both spellings as pins today) |
| 8 | whitespace-collapse cross-token (`freq / 64` vs `` `q / 64` ``) | **LANDED**, not named |
| 9 | forbidden entry backticks the replacement (`` `strcpy(` — use `memcpy(` ``) | **LANDED**, not named |
| 10 | forbidden spelling in a `//` comment | did not land — correctly blanked |
| 11 | …in a string literal / `r#"…"#` raw string | did not land — correctly blanked |
| 12 | …in a loop `invariant` (the shipped p16 shape) | did not land — correctly blanked |
| 13 | `_blank_ghost` **over**-blanking exec code (`returns`/`when` as identifiers) | did not land — only `opens_invariants` (p27) beyond the four clause keywords; no exec text lost |
| 14 | is `forbidden_verdict` reachable from the real path? | did not land — **it is**; p01's live run prints `!! [idiom-forbidden] … EMPTY set` |
| 15 | do the 4 selftests constrain or restate? 7 mutants | **5 of 7 killed** (no-fail, fail-once, drop-shout, ok-over-empty-set, per-language-scope). 2 survive: **the partial-vacuous branch** (→ M2) and **message content** (expected: `_StubReport` counts only) |
| 16 | is `_StubReport` re-implementing `Report`? | did not land — `Report.ok()` only prints, never records; a counting stub is necessary |
| 17 | does the shout's own prescription (backtick everything) break p01/p05? | **partially LANDED** → M2 (p01 safe; p05's second entry is unbacktickable) |
| 18 | is the p27 precedent one the check could have SEEN? (`.memory/02-bench-rules.md`'s own rule) | did not land — **it could**; the `2` was in `results/gate/p27-handle-table.json`. Unlike p05's, this precedent passes that test |

### the declared hang (A2) — `.temp/p68rev/hang_attack.py`
| # | attack | outcome |
|---|---|---|
| 19 | is there a floor on `run.timeout_s`? | **LANDED** → B2 (`1e-9` accepted) |
| 20 | slow-but-terminating cell + short budget = declared hang? | **LANDED** → B2 (3.5 s cell, 2 s budget, 0 failures) |
| 21 | `expected_hang` + `sanitizer_expect: "fires"` | **LANDED** → M4 |
| 22 | `run` block with no `why` key | **LANDED** → M5 (KeyError) |
| 23 | can a declared hang leak into `measure.py`? | **did not land** — `measure.py` executes binaries only on `small.bin`/`large.bin` (checksums `:528`, `CG_PLAN :56-61`, wall `:558`). The `:484` loop touches every `.bin` but only calls `model.build(...).describe()`, which is Python and terminates |
| 24 | can `expected_hang` / a budget be declared on a non-adversarial input? | **did not land** — guarded twice (`build_models:1707-1712`, `run_budgets:592`); the engineer's scoping ("fail-closed defence in depth, not a live hole") is **correct**: `check_checksums:1770` calls `run_bin` with no budget and compares `rc == 0` without reading any model expectation |
| 25 | can the two declarations be split (one without the other)? | **did not land** — `check_hang_declarations:1720-1754` fails in both directions; an invalid budget also fails twice (rejected → "no budget") |
| 26 | does `run` need a contract-key whitelist entry? | **did not land** — there is no top-level whitelist; `run` is accepted |
| 27 | can stage 4's "≥1 cell hung" false-*fail* an honest pattern on a fast box / after an optimisation change? | **did not land** — `n_hung` aggregates over **every** cell of every rung and opt level for that input, so one hanging cell suffices; and C's forward-progress rule means the O3 C cell terminating (loop deleted) cannot take the count to 0 while any O0 cell hangs |
| 28 | `expected_exit = None` (the refuted design) — is the refutation right? | **did not land, refutation upheld** — `check_adversarial:2383` computes `diverges=(rc != m_exit or …)`. With `m_exit=None` a hung cell scores `diverges=False` and the terminating R5 scores `True`. The replacement keeps the column right way up |

### item 3, the citation sweep and the rest
| # | attack | outcome |
|---|---|---|
| 29 | is `model.py` really in `measure.py`'s source list? | **did not land** — `measure.py:228`, confirmed |
| 30 | does stage 7 read `sanitizer_expect` from the model only? | **did not land** — `check_sanitizers:5130` `sbg(mod,"sanitizer_expect")`; no contract path exists |
| 31 | is there a route that avoids the re-measure? | **partially LANDED** → m4 (`--no-wall` deletes rather than moves the timing rows) |
| 32 | are p02's/p11's 5 apparent diffs really BuildId-only? | **did not land — CONFIRMED**. Exit, `fired` and stdout identical on all 5; every differing span in the `diagnostic` lies inside the hex BuildId (e.g. `715b7fe21cbe70082fb05b3b52b2eb1e61719c9f` → `091594c59ab7e9b2f8…054`). Item 3's blast radius really is one pattern |
| 33 | is the 6-row "left deliberately stale" citation list complete? | **did not land — COMPLETE.** Exactly **7 sites / 6 rows** live in measurement-hashed files, and they are exactly the ones recorded (p12 gen.py:30, p13 gen.py:30, p13 model.py:50 + :52, p16 model.py:19 + :181, p38 gen.py:28). No seventh unrecorded. (`controls/*.py` is *not* in `measurement_sources`, which is why p08/p13's control citations were free to fix.) Nit: the task file's parenthetical "(p12, p13 ×3, p16 ×2, p38)" adds to 7, not 6 |
| 34 | do the 25 re-cited citations point at what they claim? | **did not land** — I checked **all 27** free-to-edit sites, not a sample: every one resolves inside the function it names by name |
| 35 | p09's `contract_sha256` disclosure | **did not land — ACCURATE.** `23169852…1b5a` → `c391270c…e540fd` matches `NOTES.md`; `read_contract` on both shows **all keys equal except `idiom.why`**, `idiom.required` and `idiom.forbidden` byte-identical, and the only `why` deltas are the two citation strings (`check.py:929`→`:752`, `:1249`→`:1262`). No obligation, identity, collapse or driver pin moved |
| 36 | `.temp/t60-sweep.sh`'s `rc=$?`-after-a-pipeline | **HYGIENE, as the task guessed.** The bug is real (`$?` is `tr`'s). But `check.py` prints `check.py: FAIL` as its **last** line on failure (`:5753`) and `check.py: PARTIAL/PASS…` otherwise (`:5756`), and `t60-sweep.sh` captured `tail -2`, so every per-pattern line carried the true verdict. No committed claim can rest on a hidden failure |
| 37 | is the +421 lines proportionate / re-implementing? | **did not land.** Of 460 added lines: 31 blank, 65 `#` comment, ~249 docstring prose, **~115 code**. No duplication found beyond the 3× `stem` expression (m6) |
| 38 | reproducibility: re-run the gate on two patterns | **did not land.** `harness/check.py p01` (5m37s, rc=0) → `PASS-WITH-BLOCKED-ROWS`, record **byte-identical** to the committed one. `harness/check.py p27` (3m24s, rc=0) → `PASS`, `audit forbidden: 18 spelling(s), 0 hit(s) … a hit FAILS` and the new `ENFORCED since TASK_068` line both print. p27's record *did* move — on ASan PIDs and on the `adversarial` `stdout` values, which is expected on a use-after-free pattern whose checksum reads freed memory. **Every TASK_068-introduced key is identical**: `verdict`, `run_timeout_s`, `expected_hang`, `idiom_audit`, `contract_sha256`, `source_sha256` |

---

## Restoring the gate records

`harness/check.py p01` and `harness/check.py p27` were run, as the task
permits. **p01's record came back byte-identical (nothing to restore);
p27's moved on ASan PIDs and UAF-dependent stdout and I restored it with
`git checkout -- results/gate/p27-handle-table.json`.** `git status
--porcelain` afterwards shows only this untracked report file. No `git add` or
`git commit` was run; no file under `patterns/`, `harness/`, `.memory/`,
`common/` or `pilot/` was modified. `.temp/p68/` was read only.

## What I did not do

* Did not re-measure the ≈18% p08 session shift (would move a measurement
  record). Cross-checked against RECAP's independent ~8% p10 observation instead.
* Did not re-run the 20-pattern `-fstrict-aliasing` probe; audited the
  engineer's committed `aliasing_probe.json` and re-derived the 143 row count
  independently from `inputs_of`.
* Did not run the gate on all 20 (two patterns, ~11 min total). The engineer's
  20 logs under `.temp/p68/log/` all end in `PASS`/`PASS-WITH-BLOCKED-ROWS` and
  the two I re-ran reproduce byte-identically.
* Did not build a synthetic pattern directory to exercise `run_budgets` through
  `main()` end to end — B2/M5 were reproduced by driving the shipped functions
  directly, which is what `.temp/p68/hang_demo.py` also does.

## Memory updates owed (for the manager to land — reviewers do not edit `.memory/`)

1. `.memory/02-bench-rules.md:196` — *"`CONTROL_CELLS`, today
   `["safe_naive_verus"]`, which no pattern ships"* is **false**; p01 ships it
   and it is p01's 6th audited rung (M1).
2. `.memory/02-bench-rules.md:137-205` — the `forbidden_hits` entry is still
   written as a *known residual we are deliberately not closing*. It shipped as
   a hard fail at `ce06c21`; the entry needs rewriting, with the corrected
   figures **197** and **40 across 13** (M3), and with the five unnamed
   false-positive shapes (B1).
3. `.memory/02-bench-rules.md` "which pins are legitimate" — `run.timeout_s` is
   the first `slb-contract` pin that is neither prose-judgeable nor
   cross-checked against a measurement, and it reproduces `min_ir_per_work`'s
   measured `> 0`-only weakness (B2).
4. `RECAP.md:1691-1696` "Owed" item 10 — the `#[cfg(slb_twin)]` blanking gap is
   **no longer hygiene**. Its harm direction inverted at `ce06c21`: it used to
   produce a false *satisfaction* of a `required` presence count (harmless,
   `required` never fails); it now produces a false *hit* on `forbidden`, which
   hard-fails. The "0 of 15 pins" denominator is **197 forbidden spellings**
   across 20 files, all 20 of which contain twin bodies.
