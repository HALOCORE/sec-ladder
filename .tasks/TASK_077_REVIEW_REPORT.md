# TASK_077_REVIEW — report

Reviewer, adversarial. Target: `01bf438` (`harness/check.py` +287/−69,
`harness/vparse.py`, `p38/model.py`, 22 gate records, 1 measurement record,
1 published table). **2 blockers, 7 majors, 8 minors, 65 named attacks of which
24 landed.** Scratch under `.temp/p77rev/`; `.temp/p77/` read only.

**Verdict on the manager's two least-certain calls, A0 and A2: both are
UPHELD, and I could not break either on the axis that mattered.**

* **A0** — p22's `PASS-WITH-BLOCKED-ROWS → PASS` is a strengthening. I re-ran
  the gate end to end (221 s, `PASS`) and the record came back **byte-identical
  to the committed one, 0 leaves differing**. Unchecked-for-UB rows go 1 → 0 and
  the row now records `ub=False` with a model-matching stdout. I drove
  `check_miri` with **nine** doctored stage-4 tables: the block fires in six of
  them, including the two cases the task named (*"hangs only at `-O3`"*, *"only
  in `whole` mode"*) — `_hung_rungs`'s `any()` collapses conservatively. It does
  **not** fire in three, and two of those are the wrong-rung-set shape the task
  asked me to construct (m2); neither is reachable on a committed record.
* **A2** — the 97 moved leaves are environmental. I reproduced the probe
  independently on a binary this task did not touch and **sharpened it**: the
  discriminator is the *presence* of one environment variable, not its length
  (pad 1 / 7 / 8 / 40 / 200 / 700 all give the pre-task value; pad 0 gives the
  post-task one). `isolated` is exactly invariant across all seven pads. p03's
  `NOTES.md` §3b names the same 7-`Ir` `__memset_avx2_unaligned_erms` term, and
  **no consumer reads a `whole`-mode marginal** — one call site, `mode="isolated"`.

What did not survive is elsewhere: **item 4 does not do what it claims** (B1) and
**the "committed sentences these changes make false" list is materially
incomplete** (B2).

---

## Blockers

### B1 — item 4 does not admit the eight-impl spelling. Five gate stages still refuse it, and RECAP "Owed" 20 is about to be closed on that basis.
`harness/vparse.py::by_name` (unchanged, bare-keyed **on purpose**) is called by
`check.py::check_call_site`, `check.py::check_clause_deletion`,
`check.py::check_requires_strength`, `check.py::check_trusted_twins` and
`check.py::derive_contract`. Every one **raises** on a bare duplicate, and every
one turns that into a `rep.fail`. Only `check_verus_contract` and
`_verus_verified_files` were switched to `qualified=True`.

Measured (`.temp/p77rev/` inline probe) on the selftest's own `eight` source:

```
duplicate_names(qualified=True) -> {}                        <- check_verus_contract now PASSES
unique_names                   -> ['Op0::apply','Op1::apply'] <- and keys it
by_name                        -> RAISES: vparse: duplicate item name(s): apply at lines [6, 7]
```

**Failure scenario, on the next pattern:** an author takes RECAP "Owed" 20 at its
word, writes p36's original eight `impl Op for OpN` blocks, qualifies
`verus.items` as the new comment instructs, and gets `FAIL [call-site]`,
`FAIL [clause-mut]`, `FAIL [requires-strength]`, `FAIL [twin]` and
`FAIL [derive]` — five failures whose text says *"duplicate item name(s): apply"*
and which the new `check_verus_contract` comment has just told them is *"fine and
gets qualified names"*.

The engineer **knew** `by_name` stays bare and wrote the justification for it
(`duplicate_names`' new docstring, second bullet), but did not check who calls it.
`.temp/p77/NOTES.md` reports item 4 as **DO / done** and the commit message says
*"vparse keys duplicate names by scope"* without qualification.
**Do not close "Owed" 20.** The honest status is: the *contract* stage was
widened; the spelling is still refused.

### B2 — the "committed sentences these changes make FALSE" list is incomplete, and one of the misses is a published `results/` artefact
`.temp/p77/NOTES.md`, section *"Committed sentences these changes make FALSE"*.
The task file says *"a missed one is a shipped falsehood"*. Measured misses:

| site | what is now false | on the list? |
|---|---|---|
| **`results/synthesis.md`, §3 table, p22 row** | publishes `p22-hash-probe … PASS-WITH-BLOCKED-ROWS`; the gate record says `PASS`. **Generated** by `synthesis/synthesize.py` from the gate records — the artefact-vs-generator class the engineer invoked for `p38/spec.md`, applied to the tree's headline cross-pattern file. | **no** |
| **`patterns/p38-alias-pun/NOTES.md` §4d** | quotes all three previously-discarded cells by name and spread and annotates the row `<- what SHIPS`. The tree now ships **six**, and `safe_naive/whole` reads 11.1% not 12.5%. This is also the *only* place that answers "does p38 prose quote a discarded cell": **it does.** | **no** |
| `patterns/p38-alias-pun/NOTES.md` §6b (*"**15** patterns declare at least one `sanitizer_expect: "fires"` input"*) | 17 today | **no** (the census section names README and `model.py` only) |
| `patterns/p38-alias-pun/NOTES.md` §6b (*"p38 is the only pattern in this tree whose declared-clean adversarial row is clean because of the gate's BUILD FLAGS"*) | two of its rows now declare `"fires"`; the third is clean for a kernel reason | **no** |
| `patterns/p36-vtable-dispatch/NOTES.md` §9b — heading *"EIGHT `impl` BLOCKS VERIFY AND THE GATE REFUSES THEM"*, *"It cannot ship, because …"*, *"a pinned `verus.rs` may not define one item name twice"*, *"REPORTED HERE, NOT FIXED"* | partly fixed (see B1) — the section is now history and must not be left asserting a live constraint | **no** |
| `patterns/p36-vtable-dispatch/spec.md` (prose, above the `slb-contract` block at 159) — *"The GATE refuses them"* | same | **no** |
| `patterns/p36-vtable-dispatch/README.md` (*"(`vparse.duplicate_names`)"* rationale for the shipped shape) | same | **no** |
| `.memory/04-verus.md` — *"`harness/vparse.py::duplicate_names` keys by BARE NAME"* | same | **no** |
| `.memory/02-bench-rules.md`, the paragraph immediately above *"Two gate defects…"* — *"⚠ `_confirm_hang` checks **one** cell (first in sorted matrix order)"* | it checks one per (rung × opt), four on p22 | **no** (the list names the *next* paragraph) |
| `RECAP.md` "Owed" 20 | see B1 — must be **corrected, not closed** | **no** |

**Item 4 has ZERO entries on the list.** That is the miss with a mechanism: the
engineer wrote the list from the two items whose *verdicts* moved (p22's and
p38's) and never asked what item 4's own fix falsified.

**Failure scenario:** the manager lands the list as written, commits, and the
tree ships a cross-pattern synthesis table saying p22 is
`PASS-WITH-BLOCKED-ROWS`, a p38 NOTES section pointing at a superseded discard
set as *what SHIPS*, and a p36 section telling the next pattern author that a
gate limitation still exists. Nothing detects any of it: `results/synthesis.md`
is in **no** hash set, and `patterns/*/*.md` staleness is only detectable *after*
a gate re-run that nobody is scheduled to do (see M6).

---

## Majors

### M1 — `harness/asm.py` stales **17** measurement records, not 18, and the sentence explaining the remainder is refuted by the engineer's own log
`.temp/p77/NOTES.md` §0, *"THE HEADLINE"*. Counted directly from the committed
records (`'harness/asm.py' in rec['source_sha256']`):

```
measurement records with harness/asm.py hashed: 17   (22 patterns - 5 NO BASELINE)
gate records with harness/asm.py hashed:        22 of 22
```

`.temp/p77/stale-asm-probe.log`'s own total is `44 record(s) examined, 39 STALE`
= 22 + **17**. The engineer counted **log lines**, and `results/p18-varint-shift.json`
prints twice (once for `asm.py`, once for `inputs/gen.py`). The follow-up
sentence — *"The 4 measurement records that do not go STALE are the 5 `NO
BASELINE` ones minus p11"* — is contradicted three lines above it in the same
log: `NO BASELINE results/p11-nul-scan.json`. There are **5** such records
(p02, p05, p07, p11, p17) and p11 is one of them.

**The decline itself stands** — 17 vs 3 is the same argument as 18 vs 3 — but
"18" is stated three times and is the number PROTOCOL rule 9 is holding out of
`.memory/`. This is TASK_068_REVIEW M3's shape exactly: a headline count in the
justification, wrong against an artefact committed in the same commit.

### M2 — item 5's three sub-claims were re-derived on `isolated` cells only; the true cell counts are 6 / 6 / 4, not 4 / — / 3
`.temp/p77/callscan.py` hard-codes a 12-entry `CELLS` list and appends
`-isolated` to every path. I re-scanned every `(cell, opt, mode)` p47, p09 and
p11 build (`.temp/p77rev/callscan2.py`, `.temp/p77rev/callscan2.out`) and
compared against `results/pNN.json::cells[].static.bulk_calls`:

```
p11  RECORD DIFFERS on 6 cells, not 4:
     c-gcc   O0 isolated  []                      -> ['strlen@plt']
     c-gcc   O3 isolated  []                      -> ['strlen@plt']
     c-gcc   O3 whole     ['__memcpy_chk@plt']    -> ['__memcpy_chk@plt','strlen@plt']
     c-clang O0 isolated  []                      -> ['strlen@plt']
     c-clang O3 isolated  []                      -> ['strlen@plt']
     c-clang O3 whole     ['memcpy@plt']          -> ['memcpy@plt','strlen@plt']
p09  __popcountdi2 present and unrecorded on 6 cells (c-gcc and c-gcc-h,
     O0/isolated, O3/isolated, O3/whole)
p47  bcmp present and unrecorded on 4 cells (c-clang O3 isolated+whole,
     safe_naive O3 isolated+whole), not 3
```

**Failure scenario:** the manager takes the engineer's *"the p11 half is
separable and costs one pattern's re-measure … it is the manager's call and it
is cheap"*, re-measures p11, and the report of what changed says four cells while
six moved — the same isolated-only blind spot then propagates into `.memory/`
as the closing text for "Owed" 22.
(The engineer's *re-derivation* of RECAP's *"three cells calling the same entry
point"* as *"three different spellings of two symbols"* is **confirmed**:
`memcmp@plt`, `bcmp@plt`, and `bcmp@GLIBC_2.2.5` reached through the GOT.)

### M3 — the account of the one published table this task moved describes a run that was overwritten, and is false against the table that shipped
`.temp/p77/NOTES.md`, *"The p38 re-measure — exactly what moved"*.

Shipped table (`results/tables/p38-alias-pun.md`, regenerated 18:11:43Z from the
**second** re-measure) vs the pre-task one, and my independent recomputation of
the 10% crossings straight from the two records
(`.temp/p77rev/p38meas.py`):

```
before: 3 ✗  safe_naive/whole 12.5   verus/isolated 10.9   c-clang-h/isolated 10.7
after:  6 ✗  c-clang/whole 10.5  safe_naive/whole 11.1  safe_tuned/isolated 10.4
             verus/isolated 11.1  verus/whole 10.6       c-clang-h/isolated 12.0
=> 3 GAINED, 0 LOST.  Record-level crossings of the 10% line: exactly 3, the same 3.
wall figures: 64 (min_s + median_s over 16 wall-bearing cells x 2 inputs),
              median |move| 0.50%, max 3.62%
```

`NOTES.md` says **`median 0.73%, max 4.49%`** and lists **5 gained / 1 lost**,
naming `verus/isolated` and `c-clang-h/isolated` as *gained* when both were
already ✗, `c-gcc-h/whole` as *gained* when it reads 6.8%, and
`safe_naive/whole` as *lost (12.5% → 6.1%)* when it is still ✗ at 11.1%. It also
omits `verus/whole`, which really is new. **3 + 5 − 1 = 7, not 6.**

Mechanism: `.temp/p77/measure-p38.log` (17:17) and `measure-p38-2.log` (18:12)
are **byte-identical** (`sha256 9450f5f3…`) — they log `Ir` and checksums only —
so nothing in the scratch dir distinguishes the two runs, and `NOTES.md`
(mtime 18:56, *after* run 2) still carries run 1's figures. The commit message
carries run 2's. **The commit message and `NOTES.md` describe different runs and
the task file quotes one of each.**

**Consequence for the manager's question — is a 10% cliff the right instrument?
No, and the evidence is stronger than the delivery states.** `p38/NOTES.md` §4d
already records 4 → 0 → 3 discards across three runs of an unchanged tree; this
task adds a fourth run (6) and a fifth (run 1, a *different* 6 by the engineer's
own list). `safe_naive/whole` on `small.bin` has read **12.5% → 6.1% → 11.1%**
on the same binary. And the statistic the threshold reads is far noisier than
the one the report quotes:

```
min_s + median_s : n=64  median  0.50%  max  3.62%
spread_pct       : n=32  median 14.18%  max 48.77%   <- what the 10% test reads
```

### M4 — `p38/model.py::sanitizer_expect` is derived, but derived from the DEFINED window chain, which is not the chain the miscompiled binary follows. Constructed input where it says `clean` and stage 7 fires.
`patterns/p38-alias-pun/model.py::sanitizer_expect` /
`Model::_ub_scratch_overrun`. The property iterates `self._win` and skips
`None` — *"a window the driver loop never visits"* — but `_win` is populated by
`Model::_run`, which walks `k = (acc * nwin) >> 64` using the **defined**
checksum. A clamped record is precisely where the miscompiled kernel's return
value parts company with the model's, so from the first divergence the binary
visits a different window sequence.

First, the clean negative, because it matters: I built gate stage 7's exact
command line (including the new `-fstrict-aliasing`) and ran it over **13 inputs
p38 does not ship** — both sides of the `255`/`256` index boundary in two
alignments, a short window whose over-read stays inside the array, a wide
window with `nw` capped, a zero-length-record chain, `nrec == 0`, and a 2³²
declared length (`.temp/p77rev/p38_ninth.py`):

```
13/13 agree; 0 mismatch(es)
```

So the derivation is **genuine, not fitted**. But `.temp/p77rev/p38_chain.py`
constructs a two-window blob — window 0 clamps with the over-read staying inside
`sc[256]`, window 1 overruns — and searches for the case where the defined chain
never leaves window 0:

```
seed  4: model 'clean' (defined chain visits [0]), binary FIRED rc=1
seed 11: model 'clean' (defined chain visits [0]), binary FIRED rc=1
seed 35: model 'clean' (defined chain visits [0]), binary FIRED rc=1
  kernel.c:119:42: runtime error: index 256 out of bounds for type 'uint16_t [256]'
3 mismatch(es) found in 400 seeds
```

The answer to the task's *"would it have been wrong on a ninth input?"* is
**yes**, and the docstring's stated reason is the part that is wrong: *"the
condition is a property of the *blob*, computed by `_ub_scratch_overrun` from the
same decode the rungs perform, so appending a sweep band cannot silently acquire
or lose a declaration."* It is a property of the blob **and of the defined window
chain**.

**Latent today, and I measured why**: every shipped p38 input visits every window
(`visited == nwin` on all 39 blobs) and every input that clamps has `nwin == 1`,
so the chain has nowhere to diverge to. A mismatch would also be a **loud** gate
`FAIL` in both directions, not a silent pass — which is why this is a major and
not a blocker. **Failure scenario:** a future sweep band with >1 window and one
clamping record turns p38's gate red with a message blaming the model's
declaration rather than the model's chain, and `model.py` is
measurement-hashed, so fixing it costs a p38 re-measure and another discard
reshuffle (M3).

### M5 — the same commit measured Verus's THIRD answer to `--verify-function` and did not add the branch for it; the gate reports it as the wrong one of the other two
`harness/check.py::_verify_function` and `check.py::_verus_verified_files`.

Both halves of the engineer's refutation are **confirmed** at the pinned Verus
(`.temp/p77rev/vprobe/dupname.rs`, re-run here):

```
$ ./verus_run.py dupname.rs --verify-root --verify-function apply
error: more than one match found for --verify-function apply, ... matched results are:
         - A::apply   - A::spec_apply   - B::apply   - B::spec_apply   - Op::apply   - Op::spec_apply
$ ./verus_run.py dupname.rs --verify-root --verify-function A::apply
verification results:: 1 verified, 0 errors
```

So the pre-TASK_077 comment (*"Verus … silently reports `1 verified`"*) really
was false, and matching really is by substring. But driving `_verify_function`
itself:

```
--verify-function apply        -> verified=None errors=None resolved=True
--verify-function spec_apply   -> verified=None errors=None resolved=True
--verify-function nosuchfn     -> verified=None errors=None resolved=False
--verify-function A::apply     -> verified=1    errors=0    resolved=True
```

`_UNRESOLVED_RE` only matches *"could not find function"*, so an **ambiguous**
query returns `resolved=True` with `nv is None`, and `_verus_verified_files`
falls into its final `else`:

> *"…which claims a `verus!` span, but `verus --verify-function NAME
> --verify-root` reports **None** verified / **None** errors — **Verus resolved
> the item and has no verified body for it.** Ghost statements are stripped from
> the driver diff only for code Verus actually verified."*

That is the false diagnosis TASK_008_REVIEW major E existed to prevent, one
answer over. The new comment's promise — *"the gate refuses first so the reason
is stated rather than inferred from an aborted run"* — does **not** cover this
case: the refusal only fires on duplicates qualification cannot separate, and
`apply` vs `spec_apply` in one impl is not a duplicate at all.

Reachability: the label handed to `--verify-function` is `main` on **23 of 23**
verus-bearing files today, so it is latent. But **22 of 22 `verus.rs` files
already contain at least one item name that is a proper substring of another's**
— every `slb_twin_*` pair, plus `shift_round`/`shift_rounds` (p08),
`popcnt`/`lemma_popcnt_le` (p09), `toks`/`fold_toks` (p14),
`suf_at`/`nsuf_at` (p17) and `apply`/`spec_apply` (p36). One pattern whose
driver region sits outside `fn main` reaches it.

### M6 — the cost column mis-scopes "hashed": every prose fix on the list costs that pattern's gate re-run, and the delivery says only which ones move `contract_sha256`
`check.py::main`'s `srcs` glob includes `glob.glob(os.path.join(pdir, "*.md"))`.
Confirmed from the committed record:

```
md files hashed into results/gate/p22-hash-probe.json:
  patterns/p22-hash-probe/{NOTES.md, README.md, spec.md}
md files in results/p22-hash-probe.json (measurement):  []
```

`.temp/p77/NOTES.md`'s table has a **`hashed?`** column that answers only *"is
this inside the `slb-contract` block"*, and it says **no** for
`p22/spec.md:12-14`, `p22/README.md`, `p22/NOTES.md` ×4, `p38/NOTES.md:556` and
`p38/README.md`. A reader takes that as free. It is not: editing any of them
makes that pattern's **gate** record `STALE`, which `measure.py --check-stale`
reports and which the project's own *"before quoting any number"* rule depends
on. Landing the corrections without re-running costs **p22 (221 s), p36 (94 s),
p38 (96 s)** — about 7 minutes — or a red `--check-stale`.

### M7 — RECAP "Owed" 5's cost premise, which the decline argument leans on, is 3.3× stale
Not the engineer's error, but it is the number the manager will weigh. "Owed" 5
says the over-broad glob costs *"eight gate re-runs (13 min measured)"*. The
timings in the engineer's own `.temp/p77/sweep2.out` sum to **2593 s = 43.2
minutes** over 22 patterns. The engineer's three arguments against narrowing are
otherwise **sound and I could not break them**: `harness/limbs.py`'s docstring
does say *"the staleness is the alarm"* and does pre-date the item; the
imported-vs-hashed split really is 5 of 9; and the *"the gate never executes
it"* test really is the wrong one. But argument 3 (*"the cost is one sweep"*) is
the one that moved, and the recommendation should be re-stated against 43
minutes rather than 13. (My recount of the doc-reference counts gives 6 / 58 /
84 / 9 for `limbs` / `measure` / `check` / `report` on a bare grep and 6 / 51 /
83 / 5 with the `harness/` prefix, against the reported 6 / 53 / 84 / 5; the
grep was not stated, and the conclusion is unaffected either way.)

---

## Minors

* **m1 — `check_miri`'s new `rung_of` comment is false, in the function
  TASK_069 already had to fix a false comment in.** It says *"`verus.rs` is not
  in the measured-cell set for this purpose only when a pattern renames it; the
  map is `build.py`'s, so the two cannot drift."* `verus.rs` **is** a measured
  cell; a pattern cannot rename it (`RUST_SRC` is module-level); and the two
  things that *can* drift are `contract['miri']['sources']` and `RUST_SRC`,
  which are independent. The code is fail-closed (`rung is None` → block), so
  the sentence describes a mechanism that does not exist and omits the one that
  does.
* **m2 — `_hung_rungs` cannot tell "this rung terminated" from "this rung was
  never measured", which is the distinction its own docstring is careful about
  one level up.** Demonstrated (`.temp/p77rev/miriblock.py`): deleting
  `advtable['adversarial-full.bin/unsafe']`, or setting it to `[]`, both make the
  gate **run** Miri and print *"stage 4 measured the hang in ['c-clang','c-gcc']
  and NOT in 'unsafe'"* — a sentence stage 4 never said. Fail-closed only by
  neighbours: an all-builds-failed rung dies at stage 1, and `--cells measured`
  forces `PARTIAL` into `.temp/gate-partial/`. One line
  (`rung not in {k[len(pre):] for k in keys}` → block) would close it.
* **m3 — `_confirm_hang` replaced one unmeasured axis-collapse argument with
  another.** `sorted(hung_cells)` puts `isolated` first, so the representative
  for every `(rung, opt)` is the **isolated** cell and the `whole` cell — where
  the kernel is inlined into `main` and the C11 6.8.5p6 licence is most
  available — is never re-run. The docstring asserts *"the remaining collapse is
  over `mode` … which is a linkage difference and not a licence to delete a
  loop"*, which is the same shape as the *per-distinct-rung* argument the item
  itself refuted. On p22 all 8 hung cells hang, so nothing is missed today; the
  fix is `chosen.setdefault((rung, opt, mode), path)` at 8 × 20 s.
* **m4 — the record does not show what un-blocked the row.** `hung_rungs` is
  written only on the `rep.block` branch. The p22 record's
  `miri.runs[1]` now carries `ub/exit/stdout` and **no** trace of the stage-4
  measurement that let it run, so a reviewer reading `results/gate/` alone
  cannot tell a row that was never blocked from one this change un-blocked.
  TASK_068 added `run_timeout_s` and `expected_hang` to the record for exactly
  this reason.
* **m5 — a denominator in a measurement-hashed file is wrong.**
  `p38/model.py::sanitizer_expect`'s docstring says *"the sweep blobs clamp
  nothing either — 0 clamped records across all **30** of them"*. Measured:
  **31** sweep blobs, 0 clamped records. `.memory/02-bench-rules.md`'s own rule
  is *"denominators are RECOMPUTABLE, not constants"*, and correcting this one
  costs a p38 re-measure.
* **m6 — `vparse.impl_self_type` collapses generic arguments, and the error
  message it produces is false.** `impl Op for OpTag<0>` … `impl Op for
  OpTag<7>` — eight monomorphisations of one generic type, which is the shape
  p36 actually writes — all map to `OpTag`, so `unique_names` raises
  *"`OpTag::apply` is defined more than once even after qualification … no key
  distinguishes them"*. Verus distinguishes them. Undocumented limit of the fix.
* **m7 — 87 gate-record leaves moved that the delivery does not account for.**
  The task's *"Done when"* asks *"for every record that moved, say why"*.
  `.temp/p77/NOTES.md` accounts for `marginal_ir_per_call` (97), p22's
  `miri`/`blocked`/`verdict` and p38's `sanitizer`. It does not mention the
  **85 `adversarial`** leaves (p03 25, p05 12, p06 2, p13 4, p27 31, p38 11 —
  nondeterministic uninitialised/UAF stdout plus the row re-sort that follows
  it) or the **2 `derived_contract.collapse_tightest_margin`** leaves (p08
  26.870423→26.870442, p38 15.2248→15.1695). All are the documented churn class
  of `.memory/03-measurement.md`, so this is hygiene — but the sentence
  *"four patterns' gate marginals moved"* reads as the whole diff and is not.
* **m8 — `check_marginal_ir` and `_callgrind_total` both under-state the term
  A2 identifies.** `_callgrind_total`'s docstring says the environment terms
  *"cancel when the same binary is run twice in the same shell"* — true of the
  constant, false of the per-call `memset` term, which is exactly what does not
  cancel. `check_marginal_ir` bounds the residual at *"±0.20 Ir/call"* and says
  *"it is bounded and small, and it threatens no published number"*; both are
  p08-specific and both are 35× off for p03/p04/p38. The engineer's proposed
  rule (*never quote a `whole`-mode marginal across sessions*) is **right and
  still too weak in one respect**: the term is **bistable, not scattered** —
  every pad length ≥ 1 gives one value and pad 0 gives the other — so two gate
  runs from shells whose environment differs by a single variable will disagree
  by exactly 7 `Ir`/call, forever, on an unchanged tree.

---

## Attacks run, with outcomes (65; 24 landed)

### A0 — the p22 verdict move (19)
| # | attack | outcome |
|---|---|---|
| 1 | re-run `harness/check.py p22` end to end | **did not land** — `PASS`, 221 s, record **byte-identical** to the committed one (0 of ~3400 leaves differ). Nothing to restore |
| 2 | diff p22's `miri`/`blocked`/`verdict` leaves across the task commit | **did not land** — 1 blocked row → 0; the row now records `ub=False`, `exit=0`, stdout `15820751917455319872` matching the model |
| 3 | is `_confirm_hang`'s representative set really (rung × opt), with both `-O3` cells? | **did not land** — 4 representatives, `c-clang O0/O3` and `c-gcc O0/O3`, all confirmed at 20 s |
| 4 | `check_miri` with `advtable = None` | **did not land** — BLOCKS, with the `hung is None` reason |
| 5 | `advtable = {}` | **did not land** — BLOCKS |
| 6 | `advtable` carrying rows for other inputs only | **did not land** — BLOCKS |
| 7 | the rung Miri runs is itself recorded hung | **did not land** — BLOCKS, naming `['c-clang','c-gcc','unsafe']` |
| 8 | **the rung hangs ONLY in the `O3/whole` cell** | **did not land** — BLOCKS; `_hung_rungs`'s `any()` collapses opt and mode conservatively. This answers the task's *"only at `-O3` / only in `whole` mode"* |
| 9 | rows exist for the input, nothing marked hung | **landed in `check_miri` alone** — Miri runs; but `check_adversarial`'s `hangs and n_hung == 0` arm fails the pattern first, so the gate is red |
| 10 | the rung's key absent from stage 4's table | **LANDED** → m2 |
| 11 | the rung's key present with an empty row list | **LANDED** → m2 |
| 12 | can a restricted invocation put a wrong-rung-set record into `results/gate/`? | **did not land** — `cells != "all"` sets `partial`, which writes `.temp/gate-partial/*.partial.json` and `--check-stale` skips it |
| 13 | can `--skip adversarial*` un-check the declared-hang input? | **did not land** — refused at `main` with a message |
| 14 | does any pattern's `miri.sources` name a file `RUST_SRC` cannot map (→ `rung is None`)? | **did not land** — 22 of 22 name `unsafe.rs`; `rung_of` resolves it |
| 15 | input-name prefix collision in `_hung_rungs`'s `startswith` (`adversarial-oob` vs `adversarial-oobmax`, live on p36) | **did not land** — the `/` separator makes the prefix exact |
| 16 | does any added line touch the `ub`/`returncode`/`stdout` chain TASK_051_REVIEW M6 hardened? | **did not land** — 0 of 356 changed lines match `Undefined Behavior|ub =|returncode|expected_exit|model_stdout` |
| 17 | does the new `rung_of` comment match the code? | **LANDED** → m1 |
| 18 | is `_confirm_hang`'s `mode` collapse measured or asserted? | **LANDED** → m3 |
| 19 | does the record show what un-blocked the row? | **LANDED** → m4 |

### A1 — item 5 and the `asm.py` decline (11)
| # | attack | outcome |
|---|---|---|
| 20 | is `harness/asm.py` in `measure.py::measurement_sources`? | **did not land** — it is, one line below `build.py`; the `GEN-ONLY` hatch cannot cover it |
| 21 | recount the measurement records an `asm.py` edit stales | **LANDED** → M1 (17, not 18) |
| 22 | *"the 4 that do not go STALE are the 5 `NO BASELINE` ones minus p11"* | **LANDED** → M1 (refuted by the engineer's own log line) |
| 23 | does p18 flip `GEN-ONLY → STALE`? | **did not land** — confirmed in `stale-asm-probe.log` |
| 24 | re-derive `is_bulk_symbol`'s answers for `bcmp`/`bcmp@plt`/`bcmp@GLIBC_2.2.5`/`__bcmp_avx2`/`__popcountdi2`/`strlen@plt`/`__memcmpeq` | **did not land** — all as reported |
| 25 | re-derive the call targets over **all** cells × opts × modes, not the engineer's 12 | **LANDED** → M2 (6 / 6 / 4) |
| 26 | is `__popcountdi2` inside `is_bulk_symbol`'s documented scope? | **did not land — rejection UPHELD.** `_BULK_STR_WORDS`'s own rationale excludes `strtoul`/`strerror` as *"conversions and table lookups, not a loop over a caller's buffer"*; a one-register popcount is that class |
| 27 | would widening it widen gate stage 3a? | **did not land — the engineer is right.** `check_no_collapse` has **two** escape conditions reading `bulk`: `not k.has_loop and not bulk` and `not loads and not bulk` |
| 28 | is there a real cell where the hatch would open? | **did not land, and it sharpens the engineer's case** — p09 `c-gcc O3 isolated`'s *only* call is `__popcountdi2` |
| 29 | is p11 a stale record and not a table defect? | **did not land** — `is_bulk_symbol('strlen@plt')` is `True` and today's scan gives `['strlen@plt']`; fixing it is `measure.py p11` alone |
| 30 | is RECAP's *"three cells calling the same entry point"* accurate? | **partially LANDED** — three *spellings* of two symbols (`memcmp@plt`, `bcmp@plt`, `bcmp@GLIBC_2.2.5` via the GOT), and four mis-recorded cells |

### A2 — the 97 moved leaves (9)
| # | attack | outcome |
|---|---|---|
| 31 | recount the moved leaves from `git`, leaf by leaf | **did not land** — 97, split p03 8 / p04 4 / p08 80 / p38 5, exactly as reported |
| 32 | reproduce the environment probe independently, 7 pad lengths × 4 cells, on p03/p04 binaries | **did not land — UPHELD and sharpened.** pad 0 → 33328.00 / 12543.00 / 26721.30 (the new committed values); pad 1, 7, 8, 40, 200, 700 → 33335.00 / 12550.00 / 26728.30 (the old ones). Bistable on the *presence* of one variable, not its length |
| 33 | is `isolated` really immune? | **did not land** — p04 `safe_naive O3 isolated` reads 28342.00 at all seven pads |
| 34 | did p03 or p04 have a file of theirs changed? | **did not land** — `git show --stat 01bf438` touches neither, and my independent recompute of all 22 gate `source_sha256` maps finds 0 mismatches against the tree |
| 35 | is `p03/NOTES.md` §3b's mechanism real and the same constant? | **did not land** — verbatim: *"differ by 7 Ir/call inside libc's `__memset_avx2_unaligned_erms`, because `main`'s frame puts the 512-byte array at a different alignment"* |
| 36 | **does any consumer read a `whole`-mode marginal?** (task: *check every consumer, not just that one*) | **did not land** — `synthesize.py::marginal` has exactly **one** call site (`:290`), which passes no `mode`; `report.py` reads no marginal *value*, only prose about the column; `results/tables/*.md`'s boilerplate quotes no number |
| 37 | is the whole record diff accounted for? | **LANDED** → m7 (85 `adversarial` + 2 `derived_contract` leaves) |
| 38 | do the harness docstrings already bound this term? | **LANDED** → m8 (`±0.20`, *"threatens no published number"*, *"every one of those terms cancels"*) |
| 39 | is the proposed rule the right one? | **partially LANDED** → m8 — right, but the term is bistable rather than scattered, so *"do not quote"* should be *"and expect a 7-`Ir` step between any two sessions"* |

### A3 — p38's published table (7)
| # | attack | outcome |
|---|---|---|
| 40 | verify `Ir` 48/48, `static` 32/32, `checksum` 32/32 byte-identical | **did not land** — all identical (I count checksums per value, 64/64; the engineer counts per cell, 32/32) |
| 41 | verify the 64 wall figures | **LANDED** → M3 — 0.50% / 3.62% in the shipped record, not `NOTES.md`'s 0.73% / 4.49% |
| 42 | recompute the 10% crossings from the two records | **LANDED** → M3 — 3 gained, 0 lost; `NOTES.md`'s 5-gained/1-lost list is false against the shipped table and sums to 7 |
| 43 | is `spread_pct` noisier than the timings it is computed from? | **LANDED** — median 14.18%, max 48.77%, vs 0.50% / 3.62% for the timings quoted |
| 44 | does any p38 prose quote a discarded cell? | **LANDED** → B2 — `p38/NOTES.md` §4d names all three with spreads and calls them *what SHIPS* |
| 45 | is the ≈18% estimate now wrong enough to restate? | **LANDED — yes, and further than the delivery says.** The `.memory/03-measurement.md` claim is *"~18% lower on **every** `large` cell"*, i.e. a coherent level shift. p38's `large` cells: `median_s` mean **−0.22%** (−1.52…+0.89), `min_s` mean **−0.05%** (−0.56…+0.56), **sign-mixed**. There is no level shift at all. Restate as "0–18%, and not reliably a level shift" |
| 46 | is the discard count stable at all? | **LANDED** — `p38/NOTES.md` §4d records 4 → 0 → 3 on an unchanged tree; this task adds 6 (and, by `NOTES.md`'s own list, a *different* 6 in run 1). `safe_naive/whole` on `small.bin`: 12.5% → 6.1% → 11.1% |

### item 1 — `-fstrict-aliasing` and the census (6)
| # | attack | outcome |
|---|---|---|
| 47 | recount the sanitizer row denominator | **did not land** — 158 rows over 22 patterns, independently |
| 48 | recount the `fires` census from the gate records | **did not land** — 17 patterns / 40 rows / 158 after, **16 / 38 / 158** before. All three stale sites confirmed: `.memory/02-bench-rules.md` *"36 `fires` rows across 15 patterns"*, `p38/README.md` *"20 gate records … all 36"*, `RECAP.md` |
| 49 | is the blast radius really 3 rows on 1 pattern? | **did not land — CONFIRMED at the record level.** Every non-p38 `sanitizer` change across all 22 records lies inside the `diagnostic` string (ASan pid, stack/heap addresses); `exit`, `fired`, `expect` and `stdout` move **only** on p38's `adversarial-huge`, `adversarial-oob` (clean→fires) and `adversarial-stale` (checksum 10509230270850152637 → 16931469174358590653, no diagnostic) |
| 50 | is `sanitizer_expect` derived or fitted to the 8 shipped inputs? | **did not land** — 13 constructed inputs the pattern does not ship, 13/13 agree with the real stage-7 binary, including both sides of the exact 255/256 boundary in two alignments |
| 51 | **would it have been wrong on a ninth input?** | **LANDED** → M4 |
| 52 | is the sweep-blob claim right? | **partially LANDED** → m5 — 0 clamped records confirmed, but there are **31** sweep blobs, not 30 |

### item 4 — `vparse` and `--verify-function` (8)
| # | attack | outcome |
|---|---|---|
| 53 | `harness/vparse.py selftest` | **did not land** — `PASS`, including the 24 new assertions |
| 54 | is `unique_names` the identity on every verus-bearing file? | **did not land** — 25/25 (22 `verus.rs`, p01's `safe_naive_verus.rs`, 2 under `pilot/`); no `spec.md` item pin moves |
| 55 | re-run the Verus `--verify-function` probe at the pinned toolchain | **did not land — both halves CONFIRMED.** *"more than one match found"*, and `A::apply` → `1 verified, 0 errors`. Substring matching confirmed: `apply` matched `spec_apply` |
| 56 | what does `_verify_function` **return** on an ambiguous name? | **LANDED** → M5 |
| 57 | is the substring hazard live in the tree? | **partially LANDED** → M5 — 22/22 `verus.rs` files carry a substring-ambiguous name pair, but the label actually passed is `main` on 23/23, so it is latent |
| 58 | does the eight-impl spelling now pass the gate? | **LANDED** → B1 |
| 59 | can the decoy get through the widened check? | **did not land — fail-closed.** A same-scope duplicate still fails `duplicate_names(qualified=True)`; a scope-distinguished one gets `decoy::kernel` and the item-set check catches it; and that check **cannot be skipped** — `want_items is None` → `rep.fail("no item pin in spec.md")`. Coverage is complete too: any `.rs` with a `verus!` block that is absent from `verus.obligations` fails up front |
| 60 | eight monomorphisations of one generic type | **LANDED** → m6 |

### tables, hygiene and provenance (5)
| # | attack | outcome |
|---|---|---|
| 61 | regenerate all 22 `results/tables/*.md` and diff | **did not land — CONFIRMED.** 22/22 differ; all 22 by a trailing blank line; p09 `23169852ace6`→`c391270c673f`, p27 `01e2137f9a1b`→`397de62b01ea`, p36 `d19d4b502b01`→`5bd8b4ad42f4`; p12 84→83 present and a missing `absent — .wrapping_add(nstr as u64)`; p27 86→85, `pins nothing` 3→4, missing `pins nothing — deallocate` |
| 62 | does regenerating cost a gate run or a re-measure? | **did not land — CONFIRMED FREE.** `results/tables/` is in neither `check.py::main`'s `srcs` glob nor `measure.py::measurement_sources` |
| 63 | do the *doc* fixes cost anything? | **LANDED** → M6 |
| 64 | were all 22 gate records really written by the shipped harness? | **did not land** — I recomputed every record's `source_sha256` against the tree independently of `check.py`: **0 of 22** disagree. The 18:11 `check.py` edit really did precede the second sweep |
| 65 | `measure.py --check-stale` and PROTOCOL rule 10's dangling-citation sweep | **did not land** — `44 record(s) examined, 0 STALE`; the only missing citation is this report, plus the two `TASK_NNN` placeholders |

---

## Restoring what I touched

`harness/check.py p22` was re-run, as the task permits. **Its record came back
byte-identical to the committed one** — I diffed all leaves before and after and
`git status --porcelain` is empty — so there was nothing to `git checkout --`.
I did **not** run `measure.py` at all; every measurement comparison above is
`git show` against `018c1d1`. I built four binaries under `.temp/build/`
(p04 `safe_naive`/`safe_tuned` O3 whole, plus p09/p11/p47 cells `build.py`
re-created for the call scan) and one ASan binary under `.temp/p77rev/`; all are
re-derivable from `harness/build.py` and the scripts in `.temp/p77rev/`. No file
under `patterns/`, `harness/`, `.memory/`, `common/`, `synthesis/`, `pilot/`
or `results/` was modified. No `git add` or `git commit` was run. `.temp/p77/`
was read only.

## What I did not do

* Did not build a synthetic pattern directory to drive B1 through `main()` end
  to end. B1 was demonstrated by calling `vparse.by_name` on the engineer's own
  selftest source and by locating the five `rep.fail` call sites that consume it.
* Did not re-run the first p38 re-measure to recover run 1's discard set — the
  two `measure-p38*.log` files are byte-identical and carry no wall figures, so
  the run-1 table is unrecoverable. M3 is stated against the shipped table only.
* Did not run `synthesis/synthesize.py`; it writes `results/synthesis.md`, which
  I may not modify. B2's p22 row was read from the committed file and checked
  against the committed gate record.
* Did not re-run the gate on the other 21 patterns. Attack 64 establishes that
  all 22 committed records match the shipped harness, and the engineer's 22 logs
  under `.temp/p77/log/` all end in `PASS`/`PASS-WITH-BLOCKED-ROWS`.
* Did not attempt to price the p38 chain-divergence bug (M4) against a real
  sweep band; the construction is synthetic by design.

## Memory updates owed (for the manager to land — reviewers do not edit `.memory/`)

1. **`RECAP.md` "Owed" 20 — correct, do not close.** The contract stage was
   widened; `vparse.by_name` is still bare-keyed and five gate stages call it
   (B1). The remaining work is those five call sites plus the `verus.obligations`
   / `tcb_items` pin keying p36 §9b already named.
2. **`.memory/02-bench-rules.md`, "Two gate defects the hang machinery shipped
   with"** — both are fixed; rewrite as history, and fix the paragraph **above**
   it too (*"`_confirm_hang` checks one cell (first in sorted matrix order)"* →
   one per (rung × opt), 4 on p22, always the `isolated` representative — m3).
3. **`.memory/02-bench-rules.md`, "A gate hole that is one FLAG wide"** —
   CLOSED. Blast radius **158 rows / 3 differ / 1 pattern**, verified at the
   record level. Its census (*"36 `fires` rows across 15 patterns"*) recomputes
   to **40 / 17**; write it as recomputable, not as a constant.
4. **`.memory/03-measurement.md`, `marginal_ir_per_call` does not always cancel
   the environment block** — the section is p08-specific (`±0.08`, `±0.20`) and
   the tree now has three patterns at **±7**, all of which `memset` a stack
   array. Record that the term is `whole`-mode only, that `isolated` is exactly
   invariant, and that it is **bistable on the presence of one environment
   variable** rather than scattered with its length (m8).
5. **`.memory/03-measurement.md`, the ≈18% session shift** — restate. p38 is a
   third observation and it is **~0.1% mean on `large` with sign-mixed ±1.5%
   scatter**: no level shift at all. The figure is a p08 one-off, not a
   between-session property (A3 #45).
6. **`.memory/03-measurement.md` step 4, the 10% min-to-median threshold** — the
   discard *set* is not stable: 4 → 0 → 3 → 6 on an unchanged tree, and one
   cell has read 12.5% / 6.1% / 11.1%. Record that the count is a presentation
   artefact and that `spread_pct` moves 30× more than the timings it summarises
   (M3).
7. **`.memory/04-verus.md`** — `--verify-function` has **three** answers, not
   two: verified, unnameable, and *ambiguous by substring*. Record the exact
   error text, that a qualified `Type::name` resolves, and that `apply` matches
   `spec_apply` (M5). The `duplicate_names` entry needs updating for B1's actual
   scope.
8. **`.memory/05-layout.md`** — `results/tables/*.md` and `results/synthesis.md`
   are generated, are in **no** hash set, and are systematically stale (22/22 and
   at least one false p22 verdict row). Either hash them or record that they must
   be regenerated after every sweep.
9. **`.memory/02-bench-rules.md` / `05-layout.md`** — `patterns/*/*.md` is inside
   the gate's `source_sha256`, so a prose fix costs that pattern's gate re-run.
   This is not written anywhere and it is the cost the next correction pass will
   pay (M6).
10. **RECAP "Owed" 5** — the recommendation *leave the glob alone* is sound and
    should be recorded with `limbs.py`'s *"the staleness is the alarm"* as the
    reason; but the item's own cost figure is **43 minutes over 22 patterns**,
    not 13 over 8 (M7).
11. **RECAP "Owed" 22** — `bcmp` upheld as a table defect (**4** cells), p11
    upheld as a stale record (**6** cells, fixable by `measure.py p11` alone),
    `__popcountdi2` **REJECTED on the merits** — it is outside
    `is_bulk_symbol`'s documented scope and widening it would also widen gate
    stage 3a's anti-collapse escape hatch, on a cell (p09 `c-gcc O3 isolated`)
    whose only call it is. p09's real need is the outward-dispatch column, which
    RECAP "Owed" 21 already closed as derivable from `marginal_ir_per_call`.
