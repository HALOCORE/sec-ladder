# TASK_078 — land TASK_077's review: an item was one commit from being closed wrongly

**Role:** research engineer (you made the TASK_077 changes; this is their
corrections task).
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_077_REVIEW_REPORT.md`
in full**, then your own `.temp/p77/NOTES.md`.

**The review ran 65 named attacks, 24 landed: 2 blockers, 7 majors, 8 minors,
41 clean negatives.** ⚠ **Do not re-measure the 41** — they are listed with
outcomes at the end of the report, and they include most of what you would
naturally re-check.

✅ **BOTH of the manager's least-certain calls were UPHELD, and the reviewer
could not break either on the axis that mattered. Read this first.**

- **A0 — p22's `PASS` is a STRENGTHENING.** An independent gate re-run returned
  `PASS` with the record **byte-identical** (0 of ~3400 leaves). **Nine doctored
  stage-4 tables were built and the block fires in six**, including **both cases
  the task named** — hangs only at `-O3`, and only in `whole` — because
  `_hung_rungs`' `any()` collapses conservatively. Unchecked-for-UB rows 1 → 0.
- **A2 — the 97 moved leaves are environmental, and the reviewer SHARPENED your
  finding**: the discriminator is the **presence** of one environment variable,
  **not its length** (pads 1/7/8/40/200/700 all give the pre-task values; pad 0
  gives the post-task ones), and `isolated` is **exactly invariant across all
  seven**. **No consumer reads a `whole`-mode marginal** — one call site,
  `mode="isolated"`. p03/p04 files confirmed untouched from `git`.
- **Item 1's blast radius is confirmed** — 158 rows, 3 differ, all 3 on p38; and
  **`sanitizer_expect` is derived, not fitted: 13/13 on inputs p38 does not
  ship.**
- **The `__popcountdi2` rejection is UPHELD on every leg** — outside the
  documented scope, and **widening really would widen stage 3a.**

## F1 — BLOCKER. Item 4 does not do what it claims, and "Owed" 20 was one commit from being closed on it

`harness/vparse.py::by_name` **stays bare-keyed** — deliberately, and you wrote
the justification — but it is called by **five** `check.py` stages that each
turn its `ValueError` into a `rep.fail`: `check_call_site`,
`check_clause_deletion`, `check_requires_strength`, `check_trusted_twins` and
`derive_contract`. **Only `check_verus_contract` and `_verus_verified_files`
were switched.** On your own selftest source:

```
duplicate_names(qualified=True) -> {}          <- the new path says "fine"
by_name(same source)            -> RAISES: duplicate item name(s): apply at lines [6, 7]
```

> **Failure scenario, and it is the one the item exists to prevent**: an author
> writes p36's original eight `impl Op for OpN`, qualifies `verus.items` as your
> new comment instructs, and collects **five failures whose text says
> *"duplicate item name(s): apply"*** — which the same commit's comment has just
> called fine.
> **Two honest routes; pick one and argue it.** (a) Thread `qualified=True`
> through all five consumers and re-sweep. (b) Leave `by_name` alone and
> **correct the claim** — the comment, and RECAP "Owed" 20, which must say
> *narrowed, not closed*. ⚠ **The manager's lean is (a) if it is genuinely five
> call sites and no semantic change, (b) otherwise — but this is your
> measurement to make.** ⚠ **Either way "Owed" 20 does NOT close in its current
> wording, and the manager was about to close it.**

## F2 — BLOCKER. The "sentences these changes make false" list is materially incomplete, and one miss is a published artefact

**Missing, at least:**

- ⚠ **`results/synthesis.md` §3 still publishes `p22-hash-probe …
  PASS-WITH-BLOCKED-ROWS`.** It is **generated from the gate records and hashed
  in no set**, so nothing will ever detect it. **Regenerate it**
  (`synthesis/synthesize.py`) and check nothing else in it moved.
- ⚠ **`p38/NOTES.md` §4d quotes all three previously-discarded cells and
  annotates them `<- what SHIPS`.** **This also answers the manager's A3
  question: p38 prose DOES quote a discarded cell**, so the table's *"no claim
  rests on a marked row"* needs re-checking against §4d rather than asserting.
- **`p38/NOTES.md` §6b's *"15 patterns"*** and its *"p38 is the only pattern
  whose declared-clean row is clean because of BUILD FLAGS"*.
- **`.memory/02-bench-rules.md`'s `_confirm_hang` paragraph** — your list names
  the *next* one. ⚠ **`.memory/` is the MANAGER's to edit — report the exact
  wording needed, do not edit it.**
- ⚠ **Item 4 has ZERO entries at all**: `p36/NOTES.md` §9b, `p36/spec.md`
  (prose, above the block), `p36/README.md`, `.memory/04-verus.md`, RECAP
  "Owed" 20.

> ⚠ **And the cost column mis-scopes "hashed" (M6).** `patterns/*/*.md` **is**
> in the gate `source_sha256` — verified: p22's record hashes its `NOTES.md`,
> `README.md` and `spec.md`. Your column answers only *"inside `slb-contract`"*
> and says **no** for eight prose sites a reader will take as free. **Landing
> them costs p22 + p36 + p38 gate re-runs (~7 min) or a red `--check-stale`.
> Say so, and pay it.** ⚠ **`p22/spec.md`'s `PASS-WITH-BLOCKED-ROWS` sentence is
> INSIDE the contract block, so it moves `contract_sha256` and owes the
> direction test**; `p38/spec.md`'s is **generated** — fix
> `controls/mkcontract.py` too.

## The seven majors

**M1 — `asm.py` stales 17 measurement records, not 18.** `39 STALE` = 22 gate +
**17**; your 18 counts **log lines** and p18 prints twice. And *"the 4 that do
not go STALE are the 5 `NO BASELINE` minus p11"* is refuted by your own log,
which shows `NO BASELINE results/p11-nul-scan.json`. ✅ **The decline stands** —
17 is still `build.py`'s radius — but the number is stated three times.

**M2 — item 5's sub-claims were re-derived on `isolated` cells ONLY**
(`.temp/p77/callscan.py` hard-codes 12 cells and appends `-isolated`). True
counts across all cells × opts × modes: **p11 6 stale cells (not 4), p09 6,
p47 4 (not 3).** ⚠ **This changes the manager's "re-measure p11, it is cheap"
decision — restate it with the real count.**

**M3 — your account of the one published table this task moved describes an
OVERWRITTEN run**, and the two `measure-p38*.log` files are byte-identical, so
run 1 is unrecoverable. `NOTES.md` says 0.73% / 4.49% and 5 gained / 1 lost; the
shipped table and record give **0.50% / 3.62% and 3 gained / 0 lost**, and
3 + 5 − 1 = 7, not 6. The "gained" list names two cells already ✗, one that is
not ✗ now, calls `safe_naive/whole` *lost* when it is still ✗ at 11.1%, and
**omits the one that really is new** (`verus/whole`).

> ✅ **And it answers the manager's other question outright: the 10% cliff is
> the WRONG INSTRUMENT.** The discard set reads **4 → 0 → 3 → 6 on an unchanged
> tree**; `safe_naive/whole` has read 12.5% / 6.1% / 11.1%; and `spread_pct`
> moves **30× more** than the timings you quoted (median 14.18%, max 48.77%
> against median 0.50%). **Rewrite the account from the shipped artefacts, say
> run 1 is unrecoverable, and record the instrument finding** — the manager will
> land it in `.memory/`.

**M4 — `p38/model.py::sanitizer_expect` is derived, but from the DEFINED window
chain**, which is not the chain the miscompiled binary follows once a clamp
diverges the checksum feeding `k = (acc*nwin)>>64`. Constructed 2-window blob:
model `clean`, **binary FIRES** (seeds 4, 11, 35 of 400). **The docstring's
stated reason is refuted** — *"a property of the blob … appending a sweep band
cannot silently acquire or lose a declaration"*. ✅ **Latent** (all 39 shipped
blobs visit every window; every clamping input has `nwin == 1`) **and loud in
both directions**, which is why it is a major. **Fix the docstring to state the
real domain, and say what would break it.**

**M5 — you measured Verus's THIRD `--verify-function` answer and did not add the
branch.** `_UNRESOLVED_RE` matches only *"could not find function"*, so an
ambiguous query returns `resolved=True, nv=None` and prints *"reports None
verified / None errors — Verus resolved the item and has no verified body"* —
**TASK_008_REVIEW major E's false diagnosis, one answer over.** ⚠ **Latent
today (label is `main` on 23/23) but 22 of 22 `verus.rs` files already carry a
substring-ambiguous pair** — `slb_twin_*`, `shift_round`/`shift_rounds`,
`popcnt`/`lemma_popcnt_le`, `toks`/`fold_toks`, `suf_at`/`nsuf_at`,
`apply`/`spec_apply`. **Add the branch.**

**M7 — RECAP "Owed" 5's cost premise is 3.3× stale, and it is the manager's
number, not yours**: *"13 min"* against **2593 s = 43.2 min** in your own
`sweep2.out`. ✅ **The decline's other two legs are sound and the reviewer could
not break them.** **Report the corrected figure; the manager lands it.**

## The eight minors

**m1** a false `rung_of` comment — **in the function TASK_069 already
de-falsified once**. **m2** `_hung_rungs` conflates *"terminated"* with *"never
measured"* at rung level: key absent or empty row list → Miri runs and prints a
sentence **stage 4 never said**. **m3** `_confirm_hang` always picks the
`isolated` representative and **asserts the `mode` collapse — the same shape as
the argument it refuted**. **m4** `hung_rungs` is recorded only on the block
branch, so the record does not show what *un-blocked* a row. **m5**
`p38/model.py` says *"all 30"* sweep blobs; measured **31** — ⚠ **in a
measurement-hashed file, so bundle it or leave it with a reason.** **m6**
`impl_self_type` collapses generics, so eight `OpTag<0..7>` raise *"no key
distinguishes them"*, **which is false**. **m7** 87 record leaves (85
`adversarial`, 2 `derived_contract`) unaccounted against the task's *"for every
record that moved, say why"*. **m8** `check_marginal_ir`'s ±0.20 and
`_callgrind_total`'s *"every one of those terms cancels"* are **p08-specific and
35× off**.

## Done when

Both blockers closed; seven majors and eight minors addressed **or explicitly
declined with a reason**; `results/synthesis.md` regenerated; **`check.py` green
on every pattern you touch — paste the verdicts**; `measure.py --check-stale`
clean. **Paste actual output.** ⚠ **If `p22/spec.md`'s contract block moves,
disclose the hash with the direction test**, and use `git show 01bf438:` rather
than `HEAD`. ⚠ **A full 22-pattern sweep is NOT required unless you touch
`harness/`** — say which you needed and why.

## Constraints

No root; no `/tmp` (scratch `.temp/p78/`; ⚠ **`ls` any scratch path before
writing**; `.temp/p77/` and `.temp/p77rev/` are readable, **not writable**);
**no `git add`/`git commit`**; do not edit `pilot/`, `.memory/`, or `common/`.
**You MAY edit** `harness/check.py`, `harness/vparse.py`, `synthesis/*`, and the
p22/p36/p38 pattern docs named above. ⚠ **Do NOT touch `harness/build.py` or
`harness/asm.py`** — both are measurement-hashed (`asm.py` stales **17**
measurement records). ⚠ **`p38/model.py` is measurement-hashed**: a docstring
fix there forces a re-measure, so **decide deliberately and say which you
chose.** Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, gcc
`/usr/bin/gcc`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — **none but gcc on PATH**. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**; **no self-matching `pgrep` wait-loops.**
⚠ **Any re-measure runs in the FOREGROUND and alone.** **You are the only agent
running.**

⚠ **Use `stat -c %Y` and epoch seconds for any "did this change after X"
question.** `git status` reports *that* a file differs from `HEAD`, never
*when*; `ls -l` with `%H:%M` compares yesterday's 19:56 as later than today's
18:55. **Both cost the manager an error this arc.**

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 197** — 188, plus this review's nine.

**What I am least sure of, by name: F1's route.** (a) threading `qualified=True`
through five consumers touches five gate stages at once, on a code path **no
pattern exercises today** — which is how a latent fix becomes a live
regression. (b) leaves the tree honest but leaves the eight-impl spelling
refused, so "Owed" 20 stays open with a smaller claim. **I lean (a) only if the
five call sites are mechanical; if any consumer's semantics depend on the bare
key, take (b) and say so.** **Do not take (a) to make an item close.**
