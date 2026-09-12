# TASK_PHP_037 REPORT — `ph45`'s R4 endpoint SEARCHED, and **neither** endpoint is degenerate

**Role:** research engineer, alone. **Scratch:** `.temp/php37/` (expectations
written before each probe, in `.temp/php37/NOTES.md`, and not edited afterwards).

---

## §0 THE HEADLINE, IN FIVE LINES

1. ⭐⭐⭐ **`ph45`'s R4 endpoint MOVES.** `r4_buf_slice_inline` is **−23.47 %**
   whole-program against the shipped R4, has a Verus twin that verifies at
   **41 verified, 0 errors** — the shipped rung's own count, no `assume`, no new
   trusted item, no `is not supported` — and has **10 unchecked-dereference call
   sites against the shipped rung's 12**. Cheaper **and** two trusted call sites
   smaller. `r4_endpoint_degenerate: false`; this is the **second** row in either
   programme where it moves.
2. ⭐⭐⭐ **AND SO DOES THE R3 ENDPOINT — the first row where BOTH do.**
   `r3_namecmp_fn` is **18.1 % cheaper than the shipped R3**.
   `r3_endpoint_degenerate: false`. **Neither published endpoint of this row's
   `fixed-R4 bound` is a searched endpoint.** ⚠ And the **sign of the bound
   REVERSES** under search: shipped, R3 is cheaper; under the cheapest spelling
   found on each side, R4 is cheaper by 3.5 %.
3. ⭐⭐⭐ **THE MIRROR CONTROL IS THE SHARPEST RESULT: `get_unchecked` IS THE
   EXPENSIVE SPELLING HERE.** `r4_mirror_unchecked` is the winner's shape
   *exactly* — same signature, same hoist, same inline hint, same 12 trusted
   sites — with the arena reads left unchecked. **+20.97 %, i.e. 44 percentage
   points dearer than the checked spelling of the same program.**
4. ⚠⚠⚠ **AND A NEGATIVE RESULT ABOUT THE ROW'S OWN HEADLINE STATISTIC, WHICH IS
   THE THING I MOST WANT ATTACKED. A1's spread over all nine variants is
   `0.000000` percentage points on both sides** — every variant reports exactly
   `+0.37 %` (R3) or `+0.00 %` (R4) — against 66.7 pp (R3) and 44.5 pp (R4)
   whole-program. ▶ **A control that priced this row in A1 alone would have
   reported BOTH endpoints degenerate, and would have been wrong for a reason
   that has nothing to do with Rust.**
5. ⚠⚠ **AND THE ROW'S OWN STATED MECHANISM FOR ITS R3 LEVER IS REFUTED.**
   `safe_tuned.rs`'s header says *"the bound LLVM gets free from the TYPE is
   worth more than the check it removes"*. The `&[u8; REQ]` type is a **TIE**
   against a plain `&[u8]` sub-slice at the same place — measured **three
   independent times**, twice on the safe side and once on the unsafe side. The
   lever is the **HOIST**, not the type.

**§2's premise CONFIRMED. §3's cost table CONFIRMED in every row. §3.2's margin
measured (`max |ent| = 20 013`, margin **1 073×**). §3.3's correction and §3.4's
calibration written. §H: 128 cases, 77 must-FIRE, 51 must-NOT-fire, ALL PASS —
and three found real defects.**

---

## §1 BRACKETS

**Opening, before any work** — both exactly as `TASK_PHP_037.md` predicted, so
nothing was damaged:

```
harness/measure.py --check-stale                  66 record(s) examined, 0 STALE
harness-php/gate.py --tool measure --check-stale   14 record(s) examined, 0 STALE
```

**Closing:** see §8.

---

## §2 THE PREMISE §2 ASKED ME TO RE-DERIVE — CONFIRMED ON BOTH HALVES

`spec.md`'s `slb-contract`, key `identity`:

```
[{"a": "unsafe", "b": "verus", "O0": "differ", "O3": "differ", "why": "..."}]
```

`results-php/gate/ph45-htmlent-cache-int.json`, key `identity`:

```
pair "unsafe vs verus"  opt O0  level "differ"  expected "differ"
pair "unsafe vs verus"  opt O3  level "differ"  expected "differ"
   counts_a (unsafe) [313, 308, 1433]   counts_b (verus) [311, 306, 1417]
```

✅ **Pinned `differ` and MEASURED `differ` at both levels. §2 is correct.** An R4
candidate on this row needs only a twin that VERIFIES.

⭐ **And I re-derived the antecedent itself rather than taking item 61's word for
it.** `ph45`'s own hashed `why` block contains, verbatim:

> *"All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not
> merely a program that MAY use `unsafe`: it is a program that must have a
> byte-identical R5 twin that Verus verifies."*

**That sentence is in this row's `contract_sha256` and it is false of this row.**
Item 61 is confirmed at source, not just in the record.

⚠⚠ **AND IT IS NOT A FREE WIDENING IN PRACTICE, WHICH §2 DOES NOT SAY.** All
four admissible twins here compile to a `kernel` that is **not** byte-identical
to their exec rung (318 instructions against 320) — including `v0_shipped`'s.
**So on this row the wider bar is not a convenience, it is a necessity: F77's
method would have refused every candidate including the shipped rung's own
twin.** That is a stronger statement of item 61 than "the search is wider".

⭐ **I did not hard-code the consequence.** `controls/spellings.py::identity_premise`
reads the pin **and** the gate record; `admissibility()` derives the bar from
what it finds. If this row is ever re-pinned to `exact` the rule tightens with
it. And it reads the RECORD as well as the prose precisely because F82's negative
N6 found a PAT row (`p25`) carrying `identity: unsafe == verus, O3 exact` as
shared-block boilerplate while its real pin is `norel`. Twelve §H cases attack
both halves (group H).

---

## §3 §3's COST TABLE — RE-DERIVED, CORRECT IN EVERY ROW

| §3's claim | measured |
|---|---|
| the measurement record's `source_sha256` has **21** entries | ✅ 21 |
| `NOTES.md`, `spec.md`, `controls/*` are **not** among them | ✅ none present |
| ⛔ `inputs/gen.py` **is** in the measurement digest | ✅ present (and in the gate digest too) |
| `controls/*.py` **is** in the gate digest | ✅ 5 of them, plus `.patch`, `.c` and `.rs` |
| `controls/*.json` is in neither | ✅ `ph29`'s `spellings.json` is in **0** of its 39 gate entries |
| a `NOTES.md` prose fix costs one gate re-run | ✅ `NOTES.md` is in the gate digest |
| adding `controls/spellings.py` costs one gate re-run | ✅ |

✅ **All four of §3's owed items rode on one gate run, exactly as §3 predicted.**

---

## §4 §3.2 — THE `:193` OVERFLOW MARGIN. `max |ent| = 20 013`, MARGIN **1 073×**

⛔ **`inputs/gen.py` was neither edited nor run.** `.temp/php37/entmargin.py`
unpacks the **shipped** `.bin` files through `common-php/slb.py`
(`slb.read` → `slb.head1_u64_bytes`, the exact inverse of `gen.py::write`) and
decodes them **twice**. `sys.dont_write_bytecode = True` is set before `gen.py`
is imported, so not even a `__pycache__` entry appears beside a file in the
measurement digest; the probe re-hashes all eight blobs before and after and
confirms none moved.

| | `small.bin` | `large.bin` |
|---|---:|---:|
| windows, all `place = 0` | 32 | 2 050 |
| arms of the nine reached | 9 / 9 | 9 / 9 |
| numeric-arm evaluations | 528 | 251 323 |
| longest numeric body reached | **5 digits** | **5 digits** |
| **max abs ent** | **20 013** | **20 013** |
| margin vs `ENT_CEILING` (= 21 474 836) | **1 073.04×** | **1 073.04×** |
| margin vs `INT_MAX` | **107 304×** | **107 304×** |

**The two decoders AGREE**, and so do their entity tables and their
`html_entity_chars` sets. Decoder A is `gen.py`'s own `_arms_of`/`_entities`,
imported; decoder B is an independent re-implementation with its own table parser
over `c/mbfl__html_entities.h` and its own character set read from
**`c/kernel.c`**, so the two share no constant.

⭐ **And decoder B tracks the accumulator in unbounded integers AND in wrapped
32-bit at the same time. The two are identical on both inputs** — which is the
**direct** statement that `:193` never overflowed on a shipped input, rather than
an inference from a margin.

⚠ **The guard is NOT vacuous a priori, which is why the observed number is worth
keeping and not just the ceiling.** The `buffull` arm permits a **13-digit**
numeric body, i.e. `~7.4e12`, three orders of magnitude **above** `INT_MAX`. What
keeps this corpus safe is the token grammar, not the arm bound.

⚠ **One probe defect, and the probe's own refusal is what caught it.** Decoder B
first looked for `html_entity_chars` in `c/mbfl__html_entities.h`, which carries
the 251-entry table only. It printed `CANNOT EVALUATE` and stopped rather than
falling back to `gen.py`'s copy — which would have made the two decoders share
the very constant the comparison exists to test. Repaired to read `c/kernel.c`.

⚠ **Still not traced to a fix.** Nothing here is evidence about whether upstream
ever repaired `:193`. Open item 59's F46 half is discharged; its
*"untraced to any fix"* half is not.

▶ Written into `NOTES.md` §12b.

---

## §5 THE SEARCH — BOTH SIDES, BOTH FAMILIES

`patterns-php/ph45-htmlent-cache-int/controls/spellings.py` (**cloned from
`ph29`'s, not `ph16`'s** — `ph29`'s guarded `disasm` and `kernel_fingerprint`,
both F79 defects absent) and `controls/spellings.json`. Nine variants, exit
**0**, `problems: []`.

Stage 3 reproduces the shipped cells **in both families** before any variant is
quoted: **A1 to `0.0000 %`** against `results-php/ph45-htmlent-cache-int.json`,
**W1 to `0.014 %`** against `NOTES.md` §8b.

`O3 / isolated`, `small.bin`, per kernel call:

| variant | side | A1 vs R4ship | **W1 vs R4ship** | trusted sites | twin |
|---|---|---:|---:|---:|---|
| `v0_shipped` | R3 | +0.37 % | **−3.06 %** | 0 | — |
| `r3_subslice` | R3 | +0.37 % | −3.07 % | 0 | — |
| `r3_namecmp_fn` | R3 | +0.37 % | **−20.66 %** | 0 | — |
| `r3_arena_index` | R3 | +0.37 % | +46.07 % | 0 | — |
| `v0_shipped` | R4 | +0.00 % | **+0.00 %** | 12 | verifies 41/0 |
| `r4_buf_slice_inline` | R4 | +0.00 % | **−23.47 %** | **10** | **verifies 41/0** |
| `r4_buf_slice` | R4 | +0.00 % | +16.65 % | 10 | verifies 41/0 |
| `r4_mirror_unchecked` | R4 | +0.00 % | +20.97 % | 12 | verifies 41/0 |
| `r4_buf_array` | R4 | +0.00 % | (−23.48 %) | 10 | ⛔ `is not supported` |

**What ships, labelled — two quantities per family, never three:**

> **`fixed-R4 bound`** (R4 held fixed by fiat) — **A1 `+0.37 %`**,
> **W1 `−3.06 %`**.
> **R3-side span**, cheapest-found .. dearest-found in contract —
> **W1 `−20.66 %` .. `+46.07 %`** (`r3_namecmp_fn` .. `r3_arena_index`).
> ⚠ **In family A1 the span is NOT COMPUTABLE and the control says so instead of
> naming a variant**: all four in-contract R3 variants measure the same figure,
> and a `min` over equal values is the enumeration order, not a minimum.
>
> ⚠⚠ **NO PAIR INTERVAL.** `min(R3 found) − min(R4 found)` differences two upper
> bounds and bounds nothing in either direction.

### 5.1 ⭐⭐⭐ The R4 endpoint moves, and the claim is two claims

`r4_buf_slice_inline` — `name_eq` takes the work buffer as a **hoisted `&[u8]`**
and reads it with a **checked** index, forced inline.

* **cheaper**: **−23.47 %** W1. ⚠ A1 says `+0.00 %`, which is §5.4.
* **admissible**: twin **41 verified, 0 errors**; `external_body` count **6, the
  same as the shipped `verus.rs`**; `assume(` count **0**;
  `external_type_specification` count **0**; no `is not supported`; twin compiles
  under `verus_run.py --compile` with `build.py`'s own flags.
* **smaller**: **10** `bget`/`bset` call sites against the shipped rung's **12**,
  measured by `trusted_call_sites` with comments stripped and the two `fn`
  definitions subtracted. `ph07`'s `r4_index0` result and `ph29`'s
  `r4_fold_iter` result at once.
* **still an R4**: `unsafe` token count unchanged (5), 10 of 12 unchecked
  dereferences retained, all three `required` Rust pins present.

**The proof is one equation.** Changing `name_eq`'s signature creates exactly one
obligation — `b@[1 + k] == ctx.arena@[buffer + 1 + k]` — which comes off
`Seq::subrange`'s own index axiom; `1 + i <= REQ - 1 < REQ` follows from the
`n + 2 <= REQ` guard the rung **already carries** for `strcmp`'s missing bound.
Two `assert`s trigger it. **No lemma, no new trusted item.** That the rung's
declared divergence turned out to be exactly the fact the new proof needed is the
nicest thing in this task.

### 5.2 ⭐⭐ The R3 endpoint moves too — the first row where both do

`r3_namecmp_fn` (the compare lifted into a forced-inline helper over the hoisted
sub-slice) is **−20.66 %** W1 against R4ship, i.e. **18.1 % cheaper than the
shipped R3** (43 389 against 53 015 `Ir`/call).

⚠⚠ **AND THE SIGN OF THE BOUND REVERSES UNDER SEARCH.** Shipped: R3 cheaper than
R4 by 3.06 %. Cheapest-found on each side: **R4 cheaper than R3 by 3.5 %**
(41 851 against 43 389). ⚠ **That 3.5 % is a difference of two minima and is
therefore NOT a bound** — it is quoted as an ordering and never as an interval,
and it is the reason `NO PAIR INTERVAL` is stated three times in the shipped
artefacts.

⚠⚠ **So this row is NOT `ph16`'s F67 mechanism, and `NOTES.md` §8d guessed that
it was.** F67 is *two rungs cheapest under DIFFERENT spellings with a degenerate
R4*. Here the **same** spelling is cheapest on both sides and R4 is **not**
degenerate. **F67 stays n = 1** — the same conclusion `ph29`'s search reached.

### 5.3 ⭐⭐⭐ The mirror control: `get_unchecked` is the expensive spelling here

`r4_mirror_unchecked` is `r4_buf_slice_inline`'s shape **exactly** — same
four-argument signature, same hoist, same `#[inline(always)]`, same **12**
trusted call sites — with the arena reads left as `bget`, i.e. `get_unchecked`.

```
r4_buf_slice_inline   (checked index into the hoisted slice)   41 851.1 Ir/call
r4_mirror_unchecked   (get_unchecked into the whole arena)     66 155.2 Ir/call
                                                               +44.44 pp
```

▶ **On this row, in this loop shape, `get_unchecked` is not merely free — it is
the expensive spelling.** Reading through the whole 512-byte arena at a computed
offset is what blocks the hoist, and `unsafe` is what *forces* that spelling: an
unchecked read has to name the object the bound was removed from.

⚠ **What this does and does not license.** One loop, one row, one toolchain. It
says nothing about `get_unchecked` in general. What it does say is that *"remove
the bounds check"* and *"make it faster"* came apart here, and the mirror is what
separates them — the two programs differ in nothing else, and the trusted-surface
count is identical so the difference cannot be attributed to the trusted base.

### 5.4 ⚠⚠⚠ THE THING I MOST WANT ATTACKED: A1 CANNOT RESOLVE THIS ROW AT ALL

```
a1_spread_pp   {"R3": 0.0,       "R4": 0.0}
wp_spread_pp   {"R3": 66.730637, "R4": 44.454781}
```

**Every one of the nine variants reports exactly `+0.37 %` (R3 side) or exactly
`+0.00 %` (R4 side) in family A1.** The mechanism is `NOTES.md` §8a's: A1 sums
only the `kernel` symbol, `dec` is a separate symbol carrying ~90 % of every
rung's instructions, and every lever found lives in `dec`.

⭐ **And it is a sharper statement than "the symbol is identical", because the
symbols are NOT identical**: `kernel_digests_distinct` is `{"R3": 3, "R4": 4}` —
three distinct `kernel` digests across four R3 variants, four across five R4
variants, because `dec_flush` inlines into `kernel`. **The `kernel` symbol's CODE
changes and its EXECUTED COUNT does not move at all.**

▶ **A control that priced this row in A1 alone would have written
`r4_endpoint_degenerate: true` and `r3_endpoint_degenerate: true`.** Both are
false. `spellings.json`'s `headline_statistic` is therefore
`ir_per_call_small_wp`, both families are printed for every comparison, and
`cheapest_in_contract`'s default key is the whole-program one — with a §H case
(C11) pinning that default, because if it were A1 the "minimum" would be the
enumeration order.

⚠ **Which "whole-program" W1 is, stated precisely, because this programme now has
several.** W1 is `callgrind_annotate`'s own `PROGRAM TOTALS` divided by
`n_iters` — **the column `NOTES.md` §8b publishes**. It is **not** F74's family B
(`marginal_ir_per_call`, a two-point slope) and **not** F83's family C (kernel
inclusive). Measured relationship on the shipped comparison:

```
W1  R3 - R4  = -3.0573 %      B  R3 - R4  = -3.0105 %      0.047 pp apart
W1 - B = the fixed per-PROGRAM cost over 1500 calls:  R3 +472 Ir/call (0.89 % of W1)
                                                      R4 +514 Ir/call (0.94 % of W1)
  and the two fixed terms differ by 41 Ir/call = 0.075 % of W1
```

**So W1 carries a fixed per-program term of ~0.9 %, of which ~0.075 % fails to
cancel between two variants.**
⚠ **And a SECOND, larger margin on the whole-program family, quoted and NOT
re-measured** (`RECAP_PHP.md` F83/F84, manager, **UNREVIEWED**): a whole-program
statistic on this programme carries an **attribution confound** — work in a
callee that neither compared rung's own code caused — measured at up to
**~266 `Ir`/call**, running in **both** directions, and on the two-point-slope
spelling of the family it can reportedly reach a large fraction of the figure.
Against the **−23.47 %** above (≈ 12 800 `Ir`/call) that is about **2 %** of the
effect, and against the **44 pp** mirror it is smaller still. **Nothing in this
report turns on it**; it would matter to a sub-percent claim and this row makes
none.
⭐ **And the reason W1 is a single-run PROGRAM TOTAL rather than a two-point
slope was written into the control BEFORE I had seen any of that**: *"from ONE
callgrind run per (variant, input)"*, so a variant is never priced across two
runs and there is no slope to be an artefact of. I claim no foresight about the
confound — I claim only that the reason is on the record in advance and is
checkable. Every effect quoted above is 3–47 %, so the
contamination is three orders of magnitude below the signal — but it is a real
difference from family B and it is named rather than left to be noticed. W1 was
chosen over B because it comes from the **same single callgrind run** as A1 (so a
variant is never priced on two runs) and because it is the column the row already
publishes, so §8g's numbers line up with §8b's.

### 5.5 ⛔ The R3 lever cannot be moved to R4 in its own spelling — vstd coverage

`r4_buf_array` is `safe_tuned.rs`'s own `&[u8; REQ]` / `try_into` lever put into
R4. It builds, returns the shipped checksum on all eight inputs, and is
**−23.48 %**. Its twin is refused:

```
error: `core::array::TryFromSliceError` is not supported (note: you may be able
to add a Verus specification to this type with the `external_type_specification`
attribute) ...
```

**`is not supported` DISQUALIFIES.** ⚠ **And I took the repair the compiler
offers, which is what the prediction earned** (`.temp/php37/v/t0b_tryinto.log`):
with `#[verifier::external_type_specification]` **plus**
`#[verifier::external_body]` on the error type, the error becomes

```
error: precondition not satisfied   --> vstd/std_specs/result.rs:181  (Result::unwrap)
verification results:: 3 verified, 1 errors
```

because nothing establishes the conversion returned `Ok`; discharging that needs
a `TryFromSpecImpl<&[u8]> for &[u8; N]`, and `std_specs/convert.rs`'s only
`TryFromSpecImpl` is a macro over integer types. **Two new `external`
declarations and it still does not close. Both routes are barred by the bar.**

⭐ **This is `ph29`'s `r4_head_array` result on a second row** — *the R3-side
lever is out of contract on the R4 side for a vstd-coverage reason.*
⭐⭐ **And the shared `why` block ALREADY NAMES `TryFromSliceError` as one of its
six `is not supported` routes.** The control reproduces the error text from a
Verus run on this row's own twin rather than quoting the declaration, because a
control that inherits a claim cannot detect the day the claim stops being true.
⭐⭐⭐ **What makes this cheap rather than a loss is §5.6: the `&[u8]` spelling is
a TIE with the `&[u8; REQ]` one, so complying with the prover costs nothing.**

### 5.6 ⚠⚠ THE ROW'S OWN STATED MECHANISM IS REFUTED, THREE MEASUREMENTS

`safe_tuned.rs`'s header: *"the bound LLVM gets free from the TYPE is worth more
than the check it removes."*

| pair | whole-program `Ir`/call, `small.bin` | verdict |
|---|---:|---|
| shipped R3 `&[u8; REQ]` (`try_into`) vs `r3_subslice` `&[u8]` | 53 015.2 vs **53 008.2** | **TIE** (0.013 %) |
| `r4_buf_array` `&[u8; REQ]` vs `r4_buf_slice_inline` `&[u8]` | 41 844.1 vs **41 851.1** | **TIE** (0.017 %) |
| (both under this row's own `TIE_PCT` of 0.05 %) | | |

⭐ **The second pair is the sharp one: the same two spellings are a tie on the
UNSAFE side too, so it is not an artefact of one rung.** The lever is the
**HOIST** — resolving the work-buffer base once, outside the 251-entity scan —
and `r3_arena_index` (no hoist, R2's own spelling) is **+46.07 %**, which is what
the hoist is worth.

⚠ **`safe_tuned.rs` is NOT EDITED.** `.rs` sources are in this row's
**measurement** digest, so a comment fix costs a 32-cell re-measure; open item
53's ruling on `ph16` is *batch it, never land it alone*. ▶ The correction is in
`NOTES.md` §8d, where it is free, and the `.rs` comment is flagged below.
⚠ **What the header gets right and I am not touching**: the `&mut [u8]`
sub-slice hoisted per `dec` call really was +6.9 % worse, and three of its four
candidates really were pessimisations. **The refutation is about WHY the shipped
one wins, not about whether it wins.**

### 5.7 ⚠⚠⚠ THE HONEST CAVEAT, AND IT IS LARGE

**`r4_buf_slice` and `r4_buf_slice_inline` differ by ONE ATTRIBUTE and by 40
percentage points** (+16.65 % against −23.47 %). And `#[inline(always)]` applied
to the shipped `name_eq` **without** the hoist is a **pessimisation** (+13.35 %,
`.temp/php37/explore2.log`). **The two levers are not separable and neither is a
property of Rust.** Both variants ship, side by side, so the attribute's
contribution is visible rather than buried in one number.

**Every figure here is about `rustc 1.97.1` / `LLVM 22.1.6` and Verus
`0.2026.08.09.92f466f` on this box.** Inlining is an LLVM heuristic.

⚠ **R4 searched is NOT R4 exhausted.** Nine spellings shipped; **seven more
priced and dropped** before any twin was written for them
(`.temp/php37/explore*.log`): a `for` over the table **+14.21 %**, `.position()`
**+13.31 %**, the table as a `static` an **exact tie** (identical whole-program
and identical `dec`; not fingerprinted, so *exact tie* and not *byte-identical*),
a name-byte iterator a **tie**, the loop bound hoisted a **tie**,
`#[inline(never)]` **+56.79 %**, and two trusted-surface reductions in
`dec_flush` and the numeric arm at **+4.07 %** and **+7.51 %** (both **dearer**,
so neither is the *"smaller trusted surface at the same price"* result they were
proposed as). **The honest
claim is *"an admissible cheaper R4 exists"*, never *"this is the cheapest"*.**

---

## §6 §H — 128 CASES, 77 must-FIRE, 51 must-NOT-fire, **ALL PASS**, AND THREE FOUND REAL DEFECTS

`.temp/php37/negatives_spellings.py --all`, groups A–J
(`negatives_final.log`). `ph29`'s bar was 75; `ph16`'s was 54.

| group | what it attacks |
|---|---|
| A (12) | the spelling audit — the three forbidden Rust tokens fire, the comment hole is recorded not hidden, all three shipped rungs are in contract, a `required` miss reports and never disqualifies, and `i64` is a **rust-only** ban |
| B (13) | `apply_subs` / `materialise` — hit counts, the twin gets the **verus** list and not the exec one, and **all five twins are distinct programs** |
| C (19) | the verdict functions, incl. the **English** exclusion (3 cases) and C11 pinning the **default key** to the whole-program family |
| **H (12)** | ⭐⭐ `identity_premise` / `admissibility` — the machinery this row needs and `ph29` does not |
| **I (8)** | ⭐ `trusted_call_sites` |
| D (18) | the fingerprint — F79's two defects re-attacked on this row's clone, plus **a third** |
| E (14) | both `Ir` families, incl. the new `PROGRAM TOTALS` parse (5 shapes) and **E7/E8 pinning the headline choice to the measured A1 spread** |
| F (13) | the Verus reader — `is not supported` vs a failed postcondition, and the winner's twin re-verified here rather than trusted from the sidecar |
| G (15) | `check.py::control_json_verdict` driven directly, and the sidecar's pin |
| J (4) | the CLI end to end; writes no sidecar |

**Three real defects, and two of them are in code I wrote in this task:**

1. ⭐⭐ **`trusted_call_sites` was reading a LEAKED LOOP VARIABLE.** Stage 1
   called it with the `src` left over from the stage-0b audit loop, so every
   variant reported the **last audited** variant's count. The printed number was
   **12 for the three SAFE R3 variants, which contain no `bget` at all** — a
   plausible wrong number rather than an error. **What exposed it was a safe rung
   reporting a trusted surface**, i.e. group I's first case. Fixed; the function
   now re-reads the variant source, and the fix is commented with the failure.
2. ⭐⭐ **A THIRD WAY `twin_identical` CAN SAY *byte-identical* ABOUT NOTHING,
   AND `ph29`'s COPY DOES NOT REFUSE IT.** F79 fixed the *producer* (`disasm`
   raises on an empty disassembly) and gave `twin_identical` a `None` refusal.
   Neither covers the **value**: hand `ph29`'s `twin_identical` two
   `(0, 'd41d8cd98f00')` rows and **it returns `True`**. Guarded here — a zero
   instruction count or the empty-string digest is refused outright.
   ⚠ **Latent, not live, on `ph29`**, exactly as F79 said of its own two on
   `ph16`: the producer cannot emit the value. ⚠ **But it is the same general
   shape F79 named — *a control cloned between rows carries its defects with it,
   and only the row that writes NEW negatives finds them* — arriving one level
   deeper, on the copy that fixed the first two.** ▶ `ph29` NOT edited; it is a
   `ph29` re-gate and outside this task. **Reported for routing.**
3. ⚠⚠ **A MUST-NOT-FIRE CASE OF MINE PASSED VACUOUSLY.** Group G's *"pin matches
   this tree"* resolved the sidecar's `patterns/...` keys against the **real**
   repo root, where `patterns/` is the PAT tree and has no `ph45` — so every path
   was absent, the comprehension skipped all seven and the case passed on an
   empty list. The keys resolve against the **shim root** `.temp/php-root/`,
   which is where `check.py` stage 9b's `REPO` points. Fixed, **and a companion
   must-FIRE case now asserts that 7 paths were actually hashed**, so the vacuous
   pass cannot recur. ⚠ **That is trap 7's shape inside the file that exists to
   enforce trap 7.**

⚠ **Trap 7 honoured deliberately in group F**: the false-postcondition case
writes `requires` before `ensures` (or Verus will not parse it and the case fires
for the wrong reason, which is what happened on `ph29`'s first run), and a
companion case asserts the output really carries a `verification results::` line.

---

## §7 §3.3 AND §3.4 — THE OWED PROSE

**§3.3 — `NOTES.md` §8b's closing caution.** The withdrawn paragraph is quoted
in place, struck, and replaced by a box that says the observation **became** the
correction: F74's rule is withdrawn in its published one-condition form, and the
corrected two-condition form is cited with its measured figure (0 flips in 151
comparisons) and with the explicit note that **the threshold in (i) is not tuned
and six rows cannot pin it**.
⚠ **Not overstated, and the box says so in terms**: this row supplied the
counterexample; **the 366-comparison sweep is the manager's and is UNREVIEWED
under rule 9, and nothing in `NOTES.md` re-derives it.** What the row can still
say on its own evidence is the sentence it always said — the condition passes and
A1 is still wrong.

**§3.4 — `NOTES.md` §8f, the sensitivity calibration.** Re-derived from
`results-php/` alone (`.temp/php37/sens.py`, `sens.log`), **not transcribed**:

```
             n_fn_nopad   A1 small       A1 large     n_iters   exec_rate
ph45 unsafe     308       7,823,432      7,389,999   1500/200
ph45 verus      306       7,820,432      7,389,599             1.0000 / 1.0000
  D               -2         -3,000           -400
ph64 unsafe     380      11,330,956     11,363,881
ph64 verus      379      11,330,192     11,363,779             0.5093 / 0.5100
  D               -1           -764           -102
```

✅ **The task file's table reproduces exactly.** Family A resolves a
2-instruction static difference **to the instruction**, on two inputs 7.5× apart
in call count: `−3 000` over 1 500 calls and `−400` over 200 are both exactly
`2 × n_iters`.

⚠ **`exec_rate == 1.0000` is *too clean* and the section says so, with `ph64` as
the control beside it** — `ph64`'s extra instruction sits on a **conditional**
path, its rate is **0.51**, and its two inputs agree on that rate to **0.0007**.
⭐ **And `ph45`'s rate is 1.0 for a stated reason rather than an assumed one**:
both instructions are on the unconditional path through `kernel`, which is what
`exec_rate == 1` *means* — that is why this row is the clean calibration point
and `ph64` is not.

⭐ **The sign is recorded: the shipped R5's `kernel` is two instructions SMALLER
than the shipped R4's, so the proved rung is cheaper than the hand-written unsafe
one with no search at all.** Nothing is violated — the row pins `differ`. ⚠ And
§8f says explicitly that the **value is the calibration and not the direction**,
because §8e already calls R5 − R4 a codegen coin flip and −0.04 % is what a coin
flip looks like.

---

## §8 THE GATE AND THE CLOSING BRACKET, READ OUT OF `results-php/gate/`

⚠ **Every verdict below is read out of `results-php/gate/ph45-htmlent-cache-int.json`
with a `python3 -c`, never out of a log — §5 trap 2.**

### 8.1 ⚠⚠ ROUND 1 **FAILED**, AND IT WAS MY OWN SEQUENCING ERROR — THE PIN WORKING

```
verdict        FAIL
failures       2, both [tables]
controls_json  {"spellings.json": "STALE"}
```

> *"`controls/spellings.json` is STALE: 1 of 7 pinned source(s) moved under it
> (`NOTES.md`), so its numbers were NOT taken against this tree."*
> *"`results/tables/ph45-htmlent-cache-int.md` is STALE IN ITS CONTENT: 1 line
> differs …"*

**Cause: I regenerated the sidecar, then made one more `NOTES.md` edit** (weakening
an over-claimed *"byte-identical"* to *"exact tie"* — §5.7), **and `NOTES.md` is
in this sidecar's `derived_from_sha256` because stage 3 reproduces the W1 family
against §8b.** So the pin correctly reported that a file the numbers derive from
had moved under them.

⭐ **This is the pin doing exactly the job §3.1 asked for, on its first
opportunity, against its own author.** It is reported rather than quietly
re-run because the alternative reading — *"the sidecar pinned too much"* — is
wrong: `NOTES.md` **is** where W1's reference values live, and a pin that
excluded it would have let a `NOTES.md` edit silently change what stage 3
compares against.
⚠ **The lesson for the next row: `NOTES.md` in `derived_from_sha256` means the
regeneration order is PROSE FIRST, SIDECAR SECOND, GATE THIRD**, and I had it
prose–sidecar–prose–gate.

### 8.2 ⭐ ROUND 2 **PASSED CLEAN**, AND STAGE 9c DID NOT FAIL — THE MECHANISM IS WORTH KNOWING

```
verdict        PASS-WITH-BLOCKED-ROWS
failures       0
controls_json  {"spellings.json": "FRESH"}
```

⚠ **I had predicted round 2 would still fail stage 9c** (the published-table
content check), on the reasoning that the committed table carries no
`controls/spellings.json` line and the record now has one. **Wrong, and the
reason is a real property of `report.py` worth recording**:
`report.py::shout_section` prints a line for **every `controls_json` entry whose
value is NOT `"FRESH"`**. So a **STALE** sidecar adds a line to the table and a
**FRESH** one adds nothing. Round 1 failed 9c because the sidecar was STALE;
round 2 passed it because the sidecar was FRESH and the table therefore needed
**no change at all**.

▶ **Consequence, and it saved two runs: adding a FRESH `controls/*.json` sidecar
to a row needs NO `harness/report.py` re-render and NO extra gate round.**
`results-php/tables/ph45-htmlent-cache-int.md` is **unmodified** in
`git status`. `TASK_PHP_035`'s four-round chain on `ph29` was paying for a
`spec.md` edit it had not made; this row needed one round once the ordering was
right.

### 8.3 ROUND 3 — THE FINAL RUN, AFTER THE THREE PROSE REPAIRS

Between rounds 2 and 3 I applied, as **one** edit so the sidecar regenerates
once (`.temp/php37/fix_notes_hedge.py`, all three anchors dry-checked to match
exactly once before anything was written):

1. ⭐ **THE F72 HEDGE — the defect I found by re-reading my own prose after the
   numbers were settled.** §8g point 4 stated the mirror's **mechanism** as fact
   inside a `▶` box, where a reader takes it as measured. It is not measured.
   The section now separates the two claims at their real confidence: the
   **conclusion** (44 pp, attributable to the read because nothing else differs)
   is measured and boxed; the **mechanism** is marked *"A STORY I HAVE NOT
   VERIFIED. DO NOT QUOTE IT AS A RESULT"*, with the disassembly diff named as
   what would settle it and `PROTOCOL.md` rule 9's conclusion/mechanism split
   cited. ⚠ **My report had already marked it open; the ROW had not, and the row
   is what outlives the report.**
2. §8g's A1 result promoted to its own heading — *"A1 CANNOT RESOLVE THIS ROW AT
   ALL"* — with the consequence stated flatly (a control pricing this row in A1
   alone writes `r4_endpoint_degenerate: true` **and**
   `r3_endpoint_degenerate: true`, both false) and tied to which condition of
   the corrected rule catches it.
3. One sentence of margin on the whole-program family (§5.4), and one clause in
   `spellings.json` naming what `reproduces_shipped_record` is and is **not**
   about (see §9.7).

Then, **in this order, which is the order round 1 got wrong**: regenerate the
sidecar → re-run the §H negatives (**128 cases, ALL PASS**, against the edited
control) → gate.

**ROUND 3 — GREEN. Read out of `results-php/gate/ph45-htmlent-cache-int.json`
with a `python3 -c`, not out of `.temp/php37/gate3.log`:**

```
verdict           PASS-WITH-BLOCKED-ROWS
failures          []
complete_run      True
controls_json     {"spellings.json": "FRESH"}
contract_sha256   d3cb3219ef3ef5c84a7a82601adbca76dcc70fef090c9c8dd5fef9114ff1186f
source_sha256     42 files      (41 before -- `controls/spellings.py` is the 42nd)
loud              9 entries
blocked           ['verus.rs `ent_table` (strength unchecked)']
idiom_audit       forbidden_hits 0
```

✅ **`PASS-WITH-BLOCKED-ROWS` and `failures []` — the predicted verdict, and NOT
bare `PASS`, which is correct for this row**: the one blocked row is
`verus.rs`'s `ent_table` trusted item, which has no possible twin (its `ensures`
is `r@ == tbl()` over an uninterpreted spec function, so no checked body can
prove it), justified in `spec.md`. `p01`, `p35` and `ph00-smoke` carry the same
verdict. **I did not "fix" it.**

✅ **`controls_json` reads `{"spellings.json": "FRESH"}`** — §6 item 6 of the
task file asked for this quoted out of the record. It read `{}` before this
task.

✅ **`contract_sha256` did NOT move** (`d3cb3219…1186f`, identical to the build
task's shipped value) — I did not touch `spec.md`, which is why no `[tables]`
staleness chain was owed.

⚠ **`loud` is 9 entries and NONE of them is mine.** Verified against the
previous record rather than assumed: `git show HEAD:results-php/gate/ph45-htmlent-cache-int.json`
also has **9**, with the identical section list (`doc-citation-other`,
`idiom-forbidden`, `collapse-ir`, `tcb-unsafe` ×3, `tcb-axiom`, `twin` ×2).

### 8.4 THE CLOSING BRACKETS — **UNCHANGED**, AS §6 ITEM 5 PREDICTED

```
harness/measure.py --check-stale                  66 record(s) examined, 0 STALE
harness-php/gate.py --tool measure --check-stale   14 record(s) examined, 0 STALE
```

✅ **Identical to the opening bracket in both figures.** Nothing in this task's
scope is in a measurement digest — re-derived in §3, not assumed — and the php
figure did **not** move, so no measurement was staled. Two `.bin`-free rounds of
`NOTES.md` editing, a new `controls/*.py` and a new `controls/*.json` cost
**zero** re-measures, exactly as §3's cost table said they would.

---

## §9 ⚠ WHAT CONTRADICTS THE TASK FILE, AND OTHER CORRECTIONS

**Nothing in §2 or §3 was wrong.** Both re-derived clean. The corrections below
are smaller, and the first two are the substantive ones.

1. ⚠⚠ **§1's MOTIVATED HYPOTHESIS IS HALF RIGHT AND ITS MECHANISM IS WRONG.**
   §1 says the lever is *"resolve the work buffer to a `&[u8; REQ]` whose length
   is a compile-time constant"* and that it *"was applied to R3 and NEVER TO
   R4"*. ✅ **The candidate exists and is cheaper — §1 was right that the obvious
   candidate is one nobody compiled.** ⛔ But the **compile-time-constant length
   is worth nothing**: it is a tie against a plain `&[u8]` sub-slice, measured
   twice, and the `&[u8; REQ]` spelling is the one Verus **refuses**. So the
   lever §1 names could not have been shipped as an R4 at all, and the one that
   can be is the spelling §1 did not name. ⭐ **§1's own warning — *"that is a
   motivated hypothesis, not a result… Measure it; do not assume it"* — is what
   this is.**
2. ⚠⚠ **§2 UNDERSTATES ITEM 61: THE WIDER BAR IS NECESSARY HERE, NOT MERELY
   PERMITTED.** §2 says an R4 candidate *"need NOT compile byte-identically"*.
   Measured: **no** twin on this row does, including `v0_shipped`'s (318
   instructions against 320). Under F77's method this row has **no** admissible
   R4 — not even its own shipped one. That is a stronger statement of open item
   61 than the task file makes and it is worth the manager's attention.
3. ⚠ **§3.4's TABLE PERCENTAGES ARE `small.bin`-SPECIFIC AND UNLABELLED.** F82
   and the task file both quote family A as **−0.0383 %** for `ph45` and
   **−0.0067 %** for `ph64`. Those are the `small.bin` figures; `large.bin` is
   **−0.0054 %** and **−0.0009 %**. The Δ and `exec_rate` columns *are* labelled
   per input; the percentages are not, and they are 7× apart.
4. ⚠ **`§B1.1` / `§B1.2` / `§B1.3` ARE NOT HEADINGS IN `PROTOCOL_PHP.md`.**
   `grep -an 'B1\.1\|B1\.2\|B1\.3' .tasks-php/PROTOCOL_PHP.md` → **0 hits**. They
   are the three numbered items *inside* §B1 (*"Three mechanical consequences"*),
   and that is how six other files cite them (`ph03`'s `spec.md`, `ph29`'s
   `spec.md`, two reports, two `results-php/tables/`). **Not an error, a
   convention** — recorded because a reader who greps for the heading finds
   nothing.
5. ⚠⚠ **`safe_tuned.rs`'s HEADER CITES A LOG FOR NUMBERS THE LOG DOES NOT
   CONTAIN.** Its four-candidate table cites `.temp/php36/logs-06-r3search.log`.
   That file is **68 bytes, two lines**, and carries `safe_naive large` and
   `unsafe large` whole-program totals only — **none of the four candidate
   figures (98.07 / 104.80 / 101.18 / 79.51 / 73.90 M) is in it**, nor in any
   other file under `.temp/php36/`. The *sources* survive
   (`.temp/php36/r3try/{base,cand,scan,c1,c2,c3}.rs`) so the numbers are
   re-derivable, and the two shipped figures I re-measured independently agree
   with the header to 0.014 %. **It is a dangling citation, not a wrong number**
   — and `.temp/` is gitignored, so the citation was never reachable from a fresh
   clone anyway. ⚠ Fixing it is a `.rs` comment, i.e. a 32-cell re-measure:
   **batch it with §5.6's correction, never alone.**
6. ⚠ **`RECAP_PHP.md` WAS EDITED UNDERNEATH THIS TASK** — F83 was added while I
   was working (`git status` showed it modified mid-session; it is committed
   now). `PROTOCOL.md` rule 11's widened form covers exactly this. **No harm
   done**: I had already read F74/F82 and the edit does not contradict them.
   ⭐ **And F83 is directly relevant to §5.4**: it concludes that family C
   (kernel-inclusive) *strictly dominates* family B, and that **`ph45` publishing
   both families labelled is the right answer rather than a compromise.** ⚠ My W1
   is neither B nor C — §5.4 says which it is and quantifies the difference from
   B (0.047 pp on the shipped comparison). **A third family on this row is
   available for ~zero marginal cost** (`callgrind_annotate --inclusive=yes` on
   dumps the control already takes) and I did **not** add it, because §4 asks for
   two labelled quantities and the row already publishes two families.
   **Manager's call.**

7. ⚠ **`reproduces_shipped_record`'s NAME READS BROADER THAN WHAT IT VERIFIES,
   and it now says so in its own record.** The boolean covers the **two `Ir`
   families at a 0.5 % tolerance** — A1 against
   `results-php/ph45-htmlent-cache-int.json`, W1 against `NOTES.md` §8b — and
   **nothing else**. In particular it says nothing about the **static counts**:
   this file's `kernel_insns` is **320** where the measurement record's
   O3/isolated `n_fn_nopad` is **308**, because `kernel_fingerprint` counts every
   disassembled instruction in the symbol while `asm.py` reports a non-pad count,
   and because `dec_flush` inlines into `kernel`. ⭐ **What is comparable is the
   exec-vs-twin DELTA, and it agrees with the record exactly**: `320 − 318` here
   against `308 − 306` there, **−2 both ways**. ▶ A new
   `reproduces_shipped_record_scope` field states all of this, added inside the
   regeneration that was already being paid for. **No re-measure.**

### ⚠ Things I declined to do, and they are scope reductions not results

* **`r3_firstbyte` (the header's `c3`) was NOT built.** I had declared it in my
  expectations. On re-reading `safe_tuned.rs`'s header I judged that shipping the
  row's own already-declared-out-of-contract candidate would add an English-only
  exclusion to a verdict function for no measurement the header does not already
  carry. ⭐ **The exclusion MECHANISM is shipped and tested anyway**
  (`english_verdict`, three §H cases in group C), so the next variant that needs
  it has it. **Recorded as a reduction.**
* **`README.md` is unchanged.** It is in the gate digest, so it was free inside
  this run, and it now omits the row's largest new result — but nothing in it is
  **false** (it describes the A1/whole-program sign disagreement correctly) and
  §6 scoped the prose to `NOTES.md`. ▶ **One sentence pointing at §8g is the
  manager's call and it is free the next time this row is gated.**
* **`ph29`'s and `ph16`'s `spellings.py` are unchanged.** §6.2's third defect is
  latent on `ph29` and open item 57's two are latent on `ph16`; both are re-gates
  of other rows.
* **`spec.md` is unchanged**, so `contract_sha256` did not move and no `[tables]`
  failure is expected from a stale render.

---

## §10 WHAT I AM UNSURE OF, AND WHERE I MOST WANT TO BE ATTACKED

1. ⚠⚠⚠ **IS `#[inline(always)]` A RESPELLING?** This is the call I am least sure
   of and it is load-bearing: without it the winner is +16.65 % instead of
   −23.47 %. Arguments for admitting it: the `idiom` declaration says nothing
   about attributes; the row already declares `#[cfg_attr(slb_isolated,
   inline(never))]` on `dec` and `kernel` as *measurement decisions*; adding it
   to a helper **inside** `dec` changes no attribution, since the work is in
   `dec` either way (the table shows `kernel` unmoved); and the answer is
   identical on all eight inputs. Argument against: a 40-point swing from an
   attribute means the row's whole-program number is substantially an LLVM
   inlining decision, and a search that may pull that lever can find a "cheaper
   spelling" on almost any row. ▶ **Both variants ship so the attribute's
   contribution is separable, and I would not object to the manager ruling
   `r4_buf_slice` (+16.65 %, no attribute) the only admissible entry — in which
   case the R4 endpoint is DEGENERATE and §0's first headline is withdrawn.**
   **Please rule on this by name.**
2. ⚠⚠ **THE `let _ = (ctx, buffer, b);` LINE.** The exec variants carry it and
   the twins do not, because in `verus.rs` those parameters are live (in the
   `requires`, the `ensures` and the invariant) and in the exec rung they are
   not. It is a no-op at codegen. **But it means exec and twin are not related by
   a single substitution**, which is a weaker relationship than `ph29`'s
   variants have. An alternative — dropping the parameters from the exec
   signature — would make the call sites differ instead, which is worse. **I
   think this is the least-bad shape and I am not certain.**
3. ⚠ **W1 vs family B vs family C.** §5.4 quantifies W1's fixed-cost term
   (0.9 %, of which 0.075 % fails to cancel). I believe that is negligible
   against 3–47 % effects. **If the manager prefers B or C the control can be
   re-run for the cost of one `callgrind_annotate` pass per dump** — the dumps
   are the expensive part and they are already taken.
4. ⚠ **The mirror's mechanism is an inference.** I measured that
   `r4_mirror_unchecked` is 44 pp dearer than the checked spelling of the same
   program. **The explanation I offer — that reading through the whole arena at a
   computed offset blocks the hoist — is a story I have NOT verified at the
   instruction level.** F72's shape is exactly this: a stated cause that turned
   out to be a story. ▶ **The measurement stands on its own; treat the mechanism
   as open.** A disassembly diff of the two `dec` symbols would settle it and I
   did not do one.
5. ⚠ **`r3_namecmp_fn` and `r4_buf_slice_inline` are the same program up to R4's
   nine remaining unchecked sites, and R4 is 3.5 % cheaper.** That is the
   cleanest measurement on this row of what `unsafe` is worth once the spelling
   is held fixed — **and I have not checked whether the 3.5 % is those nine sites
   or a codegen difference**, so I have not written it into `NOTES.md` as a
   result. It is here for a reviewer.
6. ⚠ **`exec_rate == 1.0000` on both `ph45` inputs.** I give a reason (both
   instructions on the unconditional path) but I did **not** verify that at the
   instruction level either — I inferred it from `exec_rate` being exactly 1,
   which is circular. **`ph64` is the control that makes the pair informative;
   the per-row explanation is open.**

---

## §11 FILES

**Committed (manager's to stage):**

```
 M patterns-php/ph45-htmlent-cache-int/NOTES.md
?? patterns-php/ph45-htmlent-cache-int/controls/spellings.py
?? patterns-php/ph45-htmlent-cache-int/controls/spellings.json
 M results-php/gate/ph45-htmlent-cache-int.json
?? .tasks-php/TASK_PHP_037_REPORT.md
```

**Five paths, and that is the whole change set.** `git status --porcelain` at the
end of the task, verbatim.

⭐ **`results-php/tables/ph45-htmlent-cache-int.md` is NOT in that list and that
is correct, not an omission** — §8.2: a **FRESH** sidecar adds no line to the
published table, so no `harness/report.py` re-render was needed. Verified:
`git status --porcelain -- results-php/tables/` is **empty**.

⚠ **`results-php/preflight/ph45-htmlent-cache-int.preflight.json` MOVED
MID-TASK AND CAME BACK.** It showed modified after the **failing** round 1 —
`PROTOCOL_PHP.md` §E's *"a FAILING run grows a COMMITTED file"*, the same
behaviour this row's `NOTES.md` §0b records from its build task — and after the
two passing rounds it is **byte-identical to `HEAD` again** (`git diff --stat`
empty). **So it is not in the change set**, and it is recorded here only because
a reader watching `git status` mid-task would have seen it and should not file it
as damage.

✅ **`git status --porcelain` over `harness/`, `common/`, `patterns/`,
`results/`, `pilot/`, `common-php/`, `.web/`, `RECAP_PHP.md` and `.memory-php/`
is EMPTY**, and `results-php/tables/` is empty too.

**Untouched, deliberately:** `harness/`, `common/`, `patterns/`, `results/`,
`pilot/`, `common-php/`, `.web/`, `RECAP_PHP.md`, `.memory-php/`, this row's
`spec.md` / `README.md` / every `.rs` / `c/*` / `inputs/*`.

**`.temp/php37/`** — generators, sources, logs and `NOTES.md` (the expectations,
with the misses left in). Every binary, `.bin` and callgrind dump deleted; the
three commands at the top of `.temp/php37/NOTES.md` rebuild all of it.
