# TASK_084 — report: finish "Owed" 0

**Role: research engineer.** Ran concurrently with `TASK_085` / `TASK_085_REVIEW`
/ `TASK_086`. **UNREVIEWED** — `.tasks/TASK_084_REVIEW.md` attacks it next.
Working notes: `.temp/t84/NOTES.md` (375 lines).

**All eight deliverables done; every acceptance limb passes.**
**⚠ Two measurements contradict the task file, both inside acceptance limbs.
Running count: carry 237** (235 + #236 + #237).

---

## D1 — B1, `#[verifier::external_trait_specification]`

`harness/vparse.py` gains `trait_spans(text, code)` →
`[(name, attrs, body_start, body_end)]`. `axiom_decls()` now emits
`external_trait_specification` (**one entry per body-less method declaration**
inside a trait carrying the attribute; default-bodied methods excluded; fallback
`Name::?` when the trait is unparseable) and `external_type_specification` (one
per declared item).

## D2 — B2, `#[verifier::external_fn_specification]`

`vparse.parse`'s attribute matcher now recognises
`verifier::external_(fn|trait|type)_specification` and sets `.external` to the
full attribute path. **Disjointness rule, documented in both docstrings:
body-less → `axiom_decls`; bodied → `.external`.**

**Plus a hole D2 would otherwise have opened, closed here:** `_axiom_items` (the
Miri trigger) now also walks `_path_includes` **and** reports bodied
`external_fn_specification` items — `_is_trusted` keys on `external_body` alone,
so without it **a false `ensures` on a *safe* std fn would print *"no trusted
item, so Miri is not required"***. A `tcb-axiom` shout was added for any
`*_specification` external, because **B2 was the one route with no sentence in
the verdict at all.**

## D3 — B3, the `#[path]`-included subdir

`check_verus_contract` walks `_path_includes(pdir, pinned + *.rs)` after the
per-source loop and runs `_check_axiom_decls` on each.

**Key convention: the path relative to the REPO root** —
`verus.axioms["common/driver.rs"] = 1`. Chosen over `"../../common/driver.rs"`
because that has many spellings normalising to one file, moves if the pattern dir
moves, and repo-relative is what `_scan_unsafe_sites` already prints; it **cannot
collide with a `verus.obligations` key**, which are bare filenames with no `/`.
Hits land as `record["verus"][<relpath>] = {"path_included": true,
"axiom_decls": [...]}`, so `synthesize.py`'s `.get("verus.rs")` is untouched.

## D4 — the published column: route (b), plus two things (b) did not have

A separate **`axioms`** column, and:

- a `**Trusted base, all 22 rows: 90 items (188 lines) and 0 axioms.**` line,
  which **answers the manager's own stated counter-argument** that the total
  would still undercount;
- prose that a 7-line reviewed `external_body` wrapper and a zero-line axiom with
  **no `requires` and no `ensures`** are **not tradeable at par**, and that a
  column of `0`s **is a result** — this tree's statement that no published number
  rests on a hand-written axiom, which the table previously could not make either
  way.

## D5 — the fifth route: disclose-and-pin, plus a derived footnote

`TCB_SRC = "verus.rs"`, mirroring `R5_PAIR`, with the reasoning that reading one
source is *correct* and summing would publish a number describing no rung.
**The footnote table is computed from the records every run**, so a second
pattern growing a second Verus source **announces itself** instead of being
silently dropped — which closes the manager's actual complaint (*"no gate check
would notice"*) **at no gate cost.** An actual gate check was **declined** under
PROTOCOL rule 5.

## D6 / D7 / D8

- **D6** — `patterns/p17-http-range/NOTES.md`, four sites (§0 ×2, §10's pointer,
  §10b): the level law, the retraction of `6.50/request`, the generator-step
  table, the `30 ≠ 32` mechanism.
- **D7** — `patterns/p01-array-sum/spec.md:82`, one-line prose correction.
- **D8** — 22-pattern sweep (45 min), `licence.json` re-emitted,
  `results/synthesis.md` regenerated.

---

## ⚠⚠ #236 — limb 2's *"TCB total 92"* is NOT the published number

`results/synthesis.md` reads `| **total** | **283** | | **90** | **188** | | |`.

```
sum over ALL verus sources = 92   <- what RECAP, TASK_082, TASK_083,
                                     TASK_083_REVIEW_REPORT and TASK_084 all say
sum over `verus.rs` only   = 90   <- what the table PRINTS
the difference is p01's safe_naive_verus.rs (['load_input','emit'])
```

⚠ **`TASK_083_REVIEW_REPORT` names this very table while quoting 92.** **This is
the fifth route showing up in the project's own bookkeeping**: because p01 has
two sources, *"the TCB total"* has two values, and everyone quotes the one the
table does not print. **It is the strongest argument for D5.**

## ⚠⚠ #237 — D7's edit does NOT move `contract_sha256`

The `slb-contract` block spans chars 5676–26397; the `| identity |` row sits at
offset **5473 — 203 characters before the fence.**

```
contract_sha256 BEFORE (git HEAD): 5360d6f3dd7a4607eaf3599433ca95c0ed43dd66fe20fc85c86d52661597e1e7
contract_sha256 AFTER  (worktree): 5360d6f3dd7a4607eaf3599433ca95c0ed43dd66fe20fc85c86d52661597e1e7
contract block identical: True
spec.md sha256: 3655bdb1867d…b90 -> 35f710878db9…dea
```

The cost is `source_sha256[patterns/p01-array-sum/spec.md]` — **a gate re-run**,
which `.memory/05-layout.md` already documents. **Limb 4 restated: no pattern's
`contract_sha256` moves; exactly one `spec.md` sha256 does.**

**Rule-6 disclosure:** p01 is an existing pattern so `git show HEAD: | diff` is
real, and it is the single hunk above. p01 is p27's `mkspec.py` donor and the
**shared paragraph is untouched** (11003 bytes, sha `59748cce…` ==
`check.NAMED_SPELLING_SHA256`).

---

## ✅ Clean negative — the task file's B2 structural claim is RIGHT, and it was tested not trusted

Body-less `external_fn_specification` is rejected **twice**:
`error[E0308]: ... implicitly returns () as its body has no tail`, and on a unit
return `error: assume_specification encoding error: body should end in call
expression`.

⚠ **Bonus: Verus's own error message calls an `external_fn_specification` an
"assume_specification".** The two are **one mechanism**, which is the argument
for treating the bodied form as trusted-not-verified.

**All 14 line citations in `TASK_084.md` are exact at HEAD.**

## ✅ The p36 negative control holds

All four rung sources: `axiom_decls == []`, `trait_spans == [('Op', [])]`, gate
**PASS**. `vparse.py selftest` PASS with **9 new pins**, including `trait_dup`
(an ordinary trait, **not** an axiom) beside `extspec` (an external trait,
**is** an axiom) — **the two shapes differ only by the enclosing attribute.**

## ✅ Inertness, measured not argued

`.temp/t84/sweep_vparse.py` runs HEAD's `vparse` and the new one over every `.rs`
in `patterns/`, `common/`, `pilot/`:
**`94 .rs files scanned; 0 differ old-vs-new; 0 carry any axiom decl`.**

## ✅ Limb 3 — four planted axioms, each caught, and the published column MOVES

Generators kept at `.temp/t84/plant/{plant.py,blast22.py,b4_published.py}`; every
plant restores from `git show HEAD:` in a `finally:` and re-verifies the sha256.

- **B1** — Verus `7 verified, 0 errors` (**pinned count unmoved**). Before:
  `axiom_decls []`, TCB 3. After: `FAIL [proof-axiom] verus.rs: 2 body-less
  trusted declaration(s) [('external_type_specification','T84ExW',32),
  ('external_trait_specification','T84ExWidget::t84_width',38)]`, plus *"Miri is
  REQUIRED because: … declares 2 hand-written axiom(s)"*.
- **B2** — Verus `7 verified, 0 errors`. **TCB inventory 3 → 4**,
  `('t84_ex_count_ones', 'verifier::external_fn_specification')` — the published
  TCB column moves. Miri now fires on it.
- **B3** — Verus `7 verified, 0 errors`, and **every other pin still says
  green**: `ok verus.rs: 7 verified, 0 errors … 3 TCB items, all contracts
  identical to spec.md`, `verus.rs: body-less trusted declarations: 0`, then
  `scanned for hand-written axioms in #[path]-included files: ['common/driver.rs',
  '.temp/t84/plant/ax_mod.rs']` → `FAIL [proof-axiom] … 1 …
  [('assume_specification','u64::count_ones',6)]`. **Before the fix the file list
  was `sorted(pinned_obl)` and the module was never opened.**
- **B3 blast radius** (`blast22.py`, one axiom in the **real**
  `common/driver.rs`): **BEFORE 0 of 22 → AFTER 22 of 22 patterns fail.** Driver
  restored byte-identically.
- **B4** (`b4_published.py`, ⚠⚠ **which EXITS 1 ON A BYTE-IDENTICAL SECTION 3**):
  p01 axioms `0 → 3` (2 in `verus.rs` + 1 in the `path_included`
  `common/driver.rs`), p47 `0 → 1`, `**total** 0 → 4`, the trusted-base sentence
  moves, and the derived second-source footnote fires for a *new* pattern reading
  *"not a known control — this source is unclassified and its trusted base is
  unaccounted for above."*

## ✅ D8 — the sweep

**14:18 → 15:03, 45 min, exactly as budgeted.** `.temp/t84/verify.py`, exit 0,
**ALL LIMBS PASS**:

- **21 PASS + p01 PASS-WITH-BLOCKED-ROWS, 0 failures across 22**;
- per-source TCB identical; **92 → 92 and 90 → 90**; `axiom_decls` present and
  **0** everywhere; **no `path_included` entry in any record**;
- obligation counts, identity levels, loud/blocked counts all identical;
  **`contract_sha256` moved: []**; the `#[path]` scan line present in all 22
  logs;
- `measure.py --check-stale`: **`44 record(s) examined, 0 STALE`** (38 FRESH / 5
  NO BASELINE / 1 SKIP / 1 GEN-ONLY — same as TASK_082);
- `relicence.py`: 88 pair verdicts, **cells changed: NONE, pair verdicts changed:
  NONE**, only the pinned hash block moved (4 keys) → pure re-certification;
- `synthesize.py` → `wrote results/synthesis.md (57086 bytes, 478 lines)`, **zero
  `LICENCE STALE` verdicts**, diff 37+/25− all in §3.

**D6's mechanism was re-derived, not copied** (`asm.py show`,
`.temp/t84/p17-r{3,4}.asm`): R3's outer per-request loop is
`inc %rax / inc %r15 / cmp %r11,%r15 / je` + two `movzbl` — **one request per
iteration, scalar**; the 4× unroll is the **inner byte fold**
(`and $0x3,%r10d`, four `movzbl` at `-0x3/-0x2/-0x1/0`, `add $0x4,%rcx`,
`test`-guarded epilogue); R4 identical in shape. Constants checked:
`sweep_suffixes(3) = [497,460,423]` → mod 4 `[1,0,3]` → one `≡0` → **30**;
`small [2,3,2]` and `large [1,1,3]` → none → **32**.

---

## Problems

**None outstanding.** Two fixed mid-flight:

1. ⚠ **`trait_spans`' item-position guard MUST allow `]`, where `impl_spans`'
   identical guard does not** — that is `impl_spans`' documented **LIMIT 2**, and
   copying it verbatim made `trait_spans` miss **every attributed trait**, i.e.
   every external-trait declaration. **Caught by the probe, not by reading.**
2. D2 left a Miri hole (`_is_trusted` keys on `external_body` only), closed as
   described under D2.

The plant gate runs used `--no-build --no-callgrind --skip small --skip large
--no-verus-mutants`, so 7 of the 8–9 reported failures are the standard
diagnostic-mode ones, identical across routes; the plant-caused ones are
`[proof-axiom]` (B1, B3) and `[proof-pin] added=[...]` (B1, B2 — an artefact of
the plant adding a *local* item; **a real accident about a std trait adds
none**).

## Unsure / not done

- ⚠ **Adjacent, measured, NOT done — this is RECAP "Owed" 23: 3 of 22
  `results/tables/*.md` are content-stale.** p09 (cites contract
  `23169852ace6`, record `c391270c673f`), p12 (audit 84 → 83 present), p27 (cites
  `01e2137f9a1b`, record `397de62b01ea`; audit 86 → 85, *"pins nothing"* 3 → 4).
  **Pre-existing, not caused here**: all three `contract_sha256` are identical
  before and after the sweep and all three `idiom_audit` blocks are byte-identical
  to HEAD. Same defect `.memory/05-layout.md` records from TASK_077/078 (then 4 of
  22). **Repair: `python3 harness/report.py pNN` for those three; no gate run, no
  re-measure.**
- **Gate-record diff beyond `source_sha256`**: `.invocation` (21 — `check.py p01`
  was run where HEAD says `p01-array-sum`), `.sanitizer.*.diagnostic` (16 — ASan
  text carries addresses/pids), `.adversarial.*` (6 — the C rung reading
  uninitialised memory; row *order* and garbage checksums move, cell sets do
  not). p38's `adversarial-stale.bin/c-gcc` shows `diverges` on a different
  **row** — same two rows re-sorted; `patterns/p38-alias-pun/NOTES.md:250` and
  `:1140` already document it.
- **Not addressed**: TASK_083_REVIEW MINOR 5 (`axiom_decls` counts a decl inside
  an uninvoked `macro_rules!` and a `#[cfg(slb_twin)]` one; **both over-count,
  the safe direction**).
- **Declined**: a *gate* check for a second Verus source — the derived footnote
  does the job at zero gate cost (PROTOCOL rule 5).
- ⚠ **Minor precision correction, not counted:** `TASK_084.md` §1 B1 and RECAP
  say the B1 probe's *"TCB inventory is empty"*. **It is not** — it contains the
  probe's own `external_body` `print_u64`. Nothing from the external trait
  reaches it, which is the substantive claim.

## Memory updates owed (manager applies)

1. The repo-relative `verus.axioms["common/driver.rs"]` key convention.
2. The disjointness rule **body-less → `axiom_decls`, bodied → `.external`**,
   with the measurement that `external_fn_specification` **cannot** be written
   body-less and that **Verus calls it an `assume_specification` in its own
   errors**.
3. ⚠ **`impl_spans`' LIMIT 2 guard shape is a live trap for any new span
   function** — `trait_spans` had to allow `]`.
4. ⚠ **The published TCB total is 90, not 92**, and four documents say otherwise.
5. **The `identity` row is 203 characters outside p01's hashed block**, so that
   class of `spec.md` prose fix costs a **gate re-run**, not a contract move.
