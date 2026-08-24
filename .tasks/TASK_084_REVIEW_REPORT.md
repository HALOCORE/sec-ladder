# TASK_084_REVIEW — report

**Role: research reviewer.** Attacked `TASK_084` with **ten planted gate runs**
(`.temp/r84/plant/rplant.py`, routes A–J), a 17-construct over/under-breadth
battery (`.temp/r84/breadth.py`), an independent disassembly of p17 R3, and
re-derivation of every acceptance limb from `git` and the records. Notes:
`.temp/r84/NOTES.md`.

Every plant snapshots `patterns/p01-array-sum/{verus.rs,spec.md}` **by bytes**
(not `git show HEAD:` — `spec.md` was dirty at the start) and restores in a
`finally:`. **`git status --porcelain` is empty**, verified after every run.

**PROTOCOL rule 2 running count: 237 → 240.**

⚠⚠ **THE HEADLINE: `TASK_084`'s *"every acceptance limb passes"* IS
CONTRADICTED. Limb 3's own stated failure mode — a byte-identical
`synthesis.md` under a planted axiom — REPRODUCES ON THREE ROUTES.**

**The join nobody ran.** `TASK_084` verified limb 3 in **two halves**:
`plant.py` proved *source → gate log*, and `b4_published.py` proved *hand-edited
JSON → `synthesis.md`*. These routes run the **whole chain**: real axiom → real
gate → the record it wrote → `synthesize.py` → §3 diff.

---

## major 1 — the `#[path]` walk feeds ONE of three detectors

D3 widened `_check_axiom_decls` and `_axiom_items` to `_path_includes`. It did
**not** widen `_trusted_items` — *the function immediately above `_axiom_items`,
same shape, same purpose* — nor the TCB inventory
`tcb = [i for i in item_list if i.external]` inside `check_verus_contract`. Both
still iterate `contract["verus"]["obligations"]` only.

Three measured instances, all in a `#[path]`-included module:

| plant | gate says | §3 |
|---|---|---|
| **J** `#[verifier::external_body] fn r84_lie(x:u64)->(r:u64) ensures r==0 { x }` | **`grep -c r84_lie gate-J.log` → 0.** `ok verus.rs: 7 verified, 0 errors — matches the pinned obligation count; 3 TCB items`. 7 failures, **all** diagnostic-mode | **byte-identical** |
| **D** `#[verifier::external_fn_specification] … ensures r == 0` | axiom stage `0 (spec.md declares 0)`; 7 failures, **all** diagnostic-mode; the only trace is stage 8's Miri reason, which exists **only because p01 already has a trusted item** | **byte-identical** |
| **C** `assume(x==0); admit();` in a proof fn | axiom stage **silent** — the `for kw in ("assume(", "assume_specification", "admit(")` shout runs over `sorted(pinned_obl)` only | (count moved 7→8, caught) |

**Failure scenario:** a pattern factors its proof into a `#[path]`-included
`proof_helpers.rs`, writes
`external_body fn checked_len(v) -> (r: usize) ensures r == v@.len()` there with
an off-by-one, ships **fully green**, and publishes `TCB items 3 / axioms 0` —
**the number wrong in the column this task built.**

✅ **Clean negative inside the same finding: route I.** `unsafe` in the included
module **is** caught — `[tcb-unsafe] .temp/r84/plant/ax_mod.rs:9`. **So the
vector is limited to false claims about SAFE operations** — which is precisely
the threat `_check_axiom_decls`' own docstring names.

## major 2 — M2 answered: **NO**, a reader quoting the TCB total does not get a true number

The design choice **(b) is right**. The **prose defending it** is not — and it is
the prose a reader relies on. Three claims in `results/synthesis.md` §3 are false
in the shipped tree:

1. *"A TCB item is an `#[verifier::external_body]` wrapper"* — **false since
   D2.** Route E: an `external_fn_specification` moves `TCB items` 3→4 and
   `TCB lines` 6→7. And `.memory/05-layout.md` — **this task's own text** — says
   it and `assume_specification` are **one mechanism**, so one mechanism is now
   split across two columns whose stated difference is *"has a reviewable
   body"*.
2. *"and — under this project's rules — a verified twin and a written
   `(a)/(b)/(c)` argument"* — **44 of the 90 published TCB items have neither.**
   `load_input` and `emit` (22 each) are `external_body` with **no `ensures`**,
   so `_is_trusted` is false and `_check_trusted_unsafe` requires nothing.
   Measured: **`_is_trusted` = 46/90**. And route E's item class was
   *deliberately* exempted by this task.
3. ⚠⚠ *"the `axioms` column reading `0` in every row today is a result … this
   tree's statement that no published number rests on a hand-written axiom"* —
   **FALSE. All 22 `verus.rs` carry `broadcast use vstd::slice::group_slice_axioms`**,
   which is **six `broadcast axiom fn`s** at `~/tools/verus/vstd/slice.rs:186`;
   10 also import `group_array_axioms`, and `lemma_u128_shr_is_div` appears 23
   times. `axioms` counts **pattern-local declarations only**. **Every published
   number rests on hand-written axioms; they are vstd's.**

## major 3 — G2, asked for by name: the `if not why_required` sentence PRINTS, and it was made to print

Route G: `get_unchecked` de-`external_body`'d, body → `v[i]` (bound discharged by
vstd's `#[verifier::external_trait_specification] ExSliceIndex`), `obligations`
re-pinned 7→8, `miri.required` removed. Result: `8 verified, 0 errors` matching
the pin, `verus.rs: TCB items (2)`, axiom stage 0 everywhere, and stage 8 printed
**verbatim**:

> `ok R4/R5 (unsafe vs verus) are the same machine code at O3 (identity 'exact' >= 'norel') and this pattern has NO trusted item and NO hand-written axiom, so there is no trusted `ensures` whose incompleteness Miri would have to backstop -- Miri not required.`

**Miri was skipped while `miri.sources == ["unsafe.rs"]`, which still contains
`*v.get_unchecked(i)`.** Published: **TCB total 90 → 89** — the trusted base
moved *into* vstd and the published number went **down**.

⚠ **`miri.required: true` cannot save a future pattern**: with
`n_trusted == 0 and n_axioms == 0` the `required is False` FAIL guard **cannot
fire**, and the branch returns before it.

⚠ **Caveat, stated plainly:** run with `--no-build`, so `identity 'exact'` came
from the **pre-plant** binaries. **This proves the branch is reachable and
prints; it does not prove a checked-index R5 is byte-identical to R4 on p01.**
The shape is real in the pinned vstd regardless: `string.rs:136
assume_specification[ str::from_utf8_unchecked ]`, `std_specs/slice.rs:99
[ core::hint::unreachable_unchecked ]`, and `raw_ptr.rs`'s **safe** exec wrappers
whose bodies contain `unsafe` — **a pattern using any of them declares nothing
locally.**

## minor 1 — a shared axiom multiplies in the published total

One axiom in `common/driver.rs` lands in **all 22** records' `path_included`
entries → `| **total** | … | **22** |` and *"Trusted base … and 22 axioms"* for
**one** axiom. Per-row `1` is right; **the total is not a count of distinct
axioms, and the prose tells the reader to quote it.** Fix: dedupe on
`(key, name, line)` for `path_included` rows.

## ⚠ minor 2 — the manager's citation habit propagated into a SHIPPED HASHED DOCUMENT

`patterns/p01-array-sum/spec.md` (D7) now reads *"(`check.py:67-72`, and the
stage header at `check.py:2943`)"*. `.memory/02-bench-rules.md`: **"name the
FUNCTION and give NO LINE NUMBER AT ALL"** — the *"line as a hint"* compromise
failed inside one session. **Both citations are correct today; they landed in
the same commit that grew `check.py` by +127 lines.**

## minor 3 — the report says the selftest gained *"9 new pins"*; `git diff bce8aa8^ bce8aa8 -- harness/vparse.py` contains **8** `want(` calls

## minor 4 — `pub(crate) trait` under an external-trait attribute under-counts

`trait_spans` returns `[]` (its item-position guard stops at `)`), so the
fallback fires and reports **one** `ExW::?` instead of one axiom per body-less
method. **Visible, not silent** — but the count is wrong for a legal spelling.

## minor 5 (code read, not measured) — a `#[path]` include resolving INSIDE `pdir`

If it is also a pinned obligation source it gets **two keys** (`helper.rs` and
`patterns/pNN-x/helper.rs`), must be declared twice, and its axioms are **counted
twice** in the published column. `.memory/05-layout.md`'s *"cannot collide"* is
true; ***"cannot duplicate"* is not.**

---

## Unsure / not done

- **Route Gb not run.** p01 was not rebuilt to measure whether a checked-index R5
  is byte-identical to R4 at O3. **major 3's identity came from stale binaries
  and that is stated in the finding.**
- **No full 22-pattern sweep.** Limb 1 relied on the committed records; limbs
  2/4/5 were re-derived from `git` and `--check-stale`.
- **minor 5 is a code read**, not a gate run.
- `.temp/gate-partial/p01-array-sum.partial.json` now holds the route-J run,
  overwriting the engineer's 14:17 copy. Gitignored scratch; regenerable.
- ⚠ **Process, not a finding:** the manager committed `bce8aa8` / `087a0af` /
  `ae19119` at **15:14:01–15:14:49** while this review was live; the first plant
  into `patterns/p01-array-sum/{verus.rs,spec.md}` began at **15:18**. **Three
  minutes.** All HEAD blobs equal the pre-plant snapshots so nothing was
  contaminated, **but PROTOCOL rule 11's hazard is live whenever a reviewer
  plants into tracked pattern files.**

## Clean negatives, by name

1. ✅ **Limb 3 end-to-end (route B) — HOLDS.** A *declared*
   `assume_specification[u64::count_ones] ensures r==0` in `verus.rs` plus a
   `uninterp spec fn` in a `#[path]` module: gate `7 verified, 0 errors` (count
   unmoved), both files' axiom stages 1/1, two `[tcb-axiom]` shouts, the
   `#[path]` scan line listing both files, and the **real record** through
   `synthesize.py` moves p01 axioms **0→2**, `**total**` **0→2**, and the
   trusted-base sentence.
2. **Limb 4** — `contract_sha256` moved `[]` across all 22, re-derived against
   `bce8aa8^`.
3. **#237** — `identity` row at index 5473, fence at 6065 → outside; fenced block
   byte-identical; `contract_sha256` unmoved.
4. **#236** — 90 over `verus.rs`, 92 over all sources, table prints 90. Both
   re-derived from the records.
5. **Limb 5** — `44 record(s) examined, 0 STALE`; `build.py` and `asm.py` are
   **not in `bce8aa8`**.
6. **Limb 1** — committed verdicts `{'PASS': 21, 'PASS-WITH-BLOCKED-ROWS': 1}`.
7. **p36 negative control** — `axiom_decls == []`,
   `trait_spans == [('Op', [])]` on all four rung sources; `vparse selftest:
   PASS`.
8. **Over-breadth — 17 legal constructs probed; none refused, none
   mis-classified, no exception.** `unsafe trait`, generics + `where`,
   `cfg_attr`-wrapped attribute, macro-body trait, turbofish
   `assume_specification`, external trait outside `verus!{}` all handled;
   `broadcast group`, `broadcast proof fn` and bodied `open spec fn` correctly
   **not** axioms.
9. **The sixth-form hunt in the pinned vstd** — `external_trait_extension` (18
   uses) appears **0/18** times without `external_trait_specification`, so it is
   **not** a sixth route; `external_const_specification` does not exist;
   `broadcast group` groups, it does not axiomatise.
10. ✅ **G1, both halves, EXECUTED.** Route F: pinning `identity: differ` gives
    `ok unsafe vs verus O3: exact … (stronger than pinned)` with **zero**
    identity failures — floor-only confirmed. Route H: a **measured** `differ`
    produces *"R4 and R5 differ at O3 (identity 'differ'), so R4 does not inherit
    R5's discharged obligations at all"* as **a reason Miri is required, not a
    failure**. **TASK_085's probe is upheld and the manager's *"none allows
    R4 ≠ R5"* is false of the gate. The p15 design space is open on this axis.**
11. **B3's key convention** — repo-relative key works end to end
    (`verus.axioms[".temp/r84/plant/ax_mod.rs"]`); all 22 patterns' `obligations`
    keys are bare filenames, so **no collision** (see minor 5 for duplication).
12. **D6** — the level law predicts **32** for both shipped inputs and the
    **measured** `R3ship − R4` is **32.00 / 32.00**;
    `sweep_suffixes(3) = [497,460,423] → mod 4 [1,0,3] → 30`; `6.50/request`
    survives only as an explicit retraction. **Mechanism re-derived from the
    reviewer's own `asm.py show --raw`**: the outer per-request loop is scalar,
    the 4× unroll is the **inner byte fold**.
13. **licence.json** — 46 changed leaves, **all** `gate_source_sha256`, over
    exactly **4** file keys; no cell, no pair verdict.
14. **D2's structural claim** — `external_fn_specification` is bodied and is
    classified in `parse()`: **upheld** (route E).

## The three contradictions counted

- **#238** — G1 settled **by an executed gate** against the manager's *"none
  allows R4 ≠ R5"*.
- **#239** — M2 answered **NO**: a reader quoting the TCB total does **not** get
  a true number, against D4's claim that the footnote answers the
  counter-argument.
- **#240** — *"every acceptance limb passes"* is contradicted: **limb 3's stated
  failure mode reproduces on three routes.**
