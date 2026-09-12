# TASK_PHP_042 REPORT — `ph53`'s **BOTH ENDPOINTS SEARCHED**, both move, and two of the row's own mechanism claims are refuted

**Role:** research engineer, alone. **Scratch:** `.temp/php42/`
(`00-EXPECTATIONS.md` written before the first `rustc` invocation of this task
and not edited afterwards; the misses are quoted in §9).

---

## §0 THE HEADLINE, IN SEVEN LINES

1. ⭐⭐⭐ **BOTH ENDPOINTS MOVE, AND BY THE LARGEST MARGINS IN EITHER
   PROGRAMME.** `r3_chunks_mask` is **−32.08 %** A1 against the shipped R3;
   `r4_bitmask` is **−11.40 %** against the shipped R4.
   `r3_endpoint_degenerate: false`, `r4_endpoint_degenerate: false`. **SECOND
   row in either programme where BOTH move** — `ph45` was the first (F87),
   `ph29` moved only its R4 (F77) — and **the ordering
   between the two sides REVERSES**: the shipped `fixed-R4 bound` says R3 is
   `+24.238 %` dearer, and the cheapest found on each side has R3 **cheaper**.
   ⚠ An ORDERING, never an interval.
2. ⭐⭐⭐ **THE SHARPEST R4 RESULT IN EITHER PROGRAMME: `r4_bitmask_min` IS
   CHEAPER *AND* HAS ONE TRUSTED ACCESSOR INSTEAD OF FOUR.** −3.12 % A1, twin at
   **32 verified / 0 errors**, `#[verifier::external_body]` items **3 against
   6**, no `assume`, no `is not supported`, twin compiles under `build.py`'s own
   flags. `ph45`'s two trusted-surface reductions both came out DEARER, and so
   do **all four** of this row's reductions that keep the shipped witness
   (+0.50 %, +2.99 %, +3.03 %, +6.60 %). **The reduction is free only in
   combination with the cheaper witness, and both halves ship separately so the
   two contributions are separable rather than buried in one number.**
3. ⭐⭐⭐ **THE ANSWER ON R3 IS *THE PREDICTION'S MECHANISM WAS WRONG*, NOT *the
   shipped spelling is not the prediction's spelling*** — with the disassembly.
   The shipped R3 **is** push-as-you-go and both deletions the prediction named
   really happened. What it missed is a term four times larger and **not in the
   slot representation at all**: nine window bounds checks per op record, which
   LLVM emits as nine `cmp <threshold>,%r13 / je <panic>` pairs before the first
   byte is read — **281.8 Ir/call = 20.3 % of the rung**, against an R3−R4 gap
   of 270.7. ⚠⚠ **And the row's OWN later gloss on the same gap — §8c's
   vectorisation story — is wrong about the same term**, so headline 5 is not a
   separate result but the other half of this one. §3.
4. ⭐⭐ **THE ROW'S LARGEST SINGLE NUMBER IS MORE THAN HALVED BY THE CANDIDATE
   THE ROW ITSELF NAMED AND DID NOT BUILD.** `NOTES.md` §8e's witness cost goes
   from **+21.775 %** to **+9.665 %** whole-program. The +21.775 % reproduces to
   **0.0009 %** in this pipeline; what is withdrawn is *"the cheapest witness"*.
5. ⛔⛔ **TWO COMMITTED MECHANISM CLAIMS ARE REFUTED BY INSTRUCTION-LEVEL
   MEASUREMENT.** §8c's *"R3's scan loops vectorise … R4's do not"* and §8e's
   *"the reason is lost vectorisation"*: **R3 has 5 vector instructions and R4
   has 23, and in neither rung does a single one execute more than ONCE per
   call.** Both scan loops are scalar. Corrected in place in `NOTES.md`.
6. ⭐ **ITEM 79 MEASURED**: +1.79 % A1, shipped checksum on all seven inputs, and
   **three of `_041` §8.12's four supporting statements are wrong while its
   verdict is right.** `ptr::eq` is not *"unspecified"* — the comparison is
   fully specified at `vstd/raw_ptr.rs:221` and what Verus refuses is the
   `&T → *const T` coercion. §4.
7. **F99's citation gone**, `citecheck.py` clean for `ph53`. **§H: 161 cases,
   138 must-FIRE / 23 must-NOT-fire, ALL PASS — and THREE of them found real
   defects, all three in code written this task, one of which is a `−1` in the
   function that measures the trusted surface.** §6. ⛔ **A FOURTH defect no
   negative could find — my own docstring endorsing the mechanism §5 refutes —
   was caught by re-reading the prose against the settled numbers.** §6.1.
   ⭐ **And a FOURTH defect in the SHARED machinery, latent here and LIVE on
   `ph29`.** §8.

---

## §1 BRACKETS

**Opening, before any work** — both exactly as `TASK_PHP_042.md` §5 predicted:

```
python3 harness/measure.py --check-stale                -> 66 record(s) examined, 0 STALE
python3 harness-php/gate.py --tool measure --check-stale -> 16 record(s) examined, 0 STALE
```

**Closing, after the final gate — BOTH UNMOVED:**

```
python3 harness/measure.py --check-stale                -> 66 record(s) examined, 0 STALE
python3 harness-php/gate.py --tool measure --check-stale -> 16 record(s) examined, 0 STALE
```

✅ **Identical to the opening bracket in both figures**, so **no measurement was
staled** — and §2 shows why that was structural rather than lucky.

⚠ **MID-TASK THE PHP FIGURE READ `16 / 1 STALE` AND THAT IS NOT THE ALARM THE
TASK FILE WARNS ABOUT.** The stale record was
`results/gate/ph53-iface-tail-uninit.json` — the **GATE** record — over
`spec.md`, `NOTES.md` and `README.md`, which the re-gate regenerates.
`results/ph53-iface-tail-uninit.json` — the **MEASUREMENT** record — stayed
`FRESH` at `19 source(s) + 7 input(s)` throughout, which is the figure trap 2 is
about. ▶ **`--tool measure --check-stale` examines 16 records = 8 measurement +
8 gate**, so a `spec.md` edit moves that counter without touching a measurement.
**Stated because a reader watching the bracket mid-task would otherwise file it
as damage.**

---

## §2 WHICH SIDE OF THE DIGEST LINE EVERY EDIT IS ON (trap 2)

| file | edit | digest | cost |
|---|---|---|---|
| `patterns-php/ph53-iface-tail-uninit/controls/spellings.py` | **NEW** | gate only | re-gate |
| `…/controls/spellings.json` | **NEW** | **neither** (`check.py` excludes `controls/*.json` from `source_sha256` by design — stage 9b is the mechanism for outputs) | — |
| `…/controls/mu_ref.rs` `mu_ref_cmp.rs` `mu_ref_exec.rs` | **NEW** | gate only | re-gate |
| `…/spec.md` | F99's citation retargeted, **one sentence** | gate only, **and `contract_sha256`** | re-gate + a table re-render |
| `…/NOTES.md` | §8c/§8e mechanism corrections, §8g's answer, new §8j/§8k, §11a/§12 amendments, two citations restated | gate only | re-gate |
| `…/README.md` | the debt line replaced, three `controls/` rows added | gate only | re-gate |

⛔ **NOTHING IN THE MEASUREMENT DIGEST WAS TOUCHED, AND HERE IS THE DIGEST SO IT
CAN BE VERIFIED RATHER THAN TRUSTED.**
`results-php/ph53-iface-tail-uninit.json`'s `source_sha256`, all **19** entries,
listed out of the record:

```
common/driver.c            common/driver.h            common/driver.rs
common/slb.py              harness/asm.py             harness/build.py
harness/measure.py         verus_run.py
patterns/ph53-iface-tail-uninit/c/emalloc_shim.h
patterns/ph53-iface-tail-uninit/c/kernel.c
patterns/ph53-iface-tail-uninit/c/kernel.h
patterns/ph53-iface-tail-uninit/c/kernel_hardened.c
patterns/ph53-iface-tail-uninit/c/main.c
patterns/ph53-iface-tail-uninit/inputs/gen.py
patterns/ph53-iface-tail-uninit/model.py
patterns/ph53-iface-tail-uninit/safe_naive.rs
patterns/ph53-iface-tail-uninit/safe_tuned.rs
patterns/ph53-iface-tail-uninit/unsafe.rs
patterns/ph53-iface-tail-uninit/verus.rs
```

▶ **`spec.md`, `NOTES.md`, `README.md` and every `controls/*` are in NONE of
them**, and the five files this task wrote or edited are exactly those four
kinds. ✅ **The two checks that settle it, not an argument:**

```
python3 harness-php/gate.py --tool measure --check-stale
  FRESH  results/ph53-iface-tail-uninit.json   19 source(s) + 7 input(s)
git status --porcelain -- patterns-php/ph53-iface-tail-uninit/c       patterns-php/ph53-iface-tail-uninit/inputs       patterns-php/ph53-iface-tail-uninit/model.py       patterns-php/ph53-iface-tail-uninit/*.rs
  (empty)
```

**Zero re-measures. The 32-cell matrix was never rebuilt and never needed to
be.** ⚠ The one thing that DID move in that family is `contract_sha256`
(`7013be6f…` → `c41ffad2b795…`), and that is the **gate** digest, not the
measurement one — it cost one extra `report.py` render and two extra gate
rounds, and no cell.

---

## §3 ⭐⭐⭐ THE ANSWER ON R3 — *"the prediction's mechanism was wrong"*, with the disassembly

**The question (task file §6.3): why is the shipped R3 dearest-but-one when
`TASK_PHP_040_REPORT` §5.6 predicted it would be the cheapest rung on the row?**
A1, `small.bin`, `O3`/`isolated`, from the shipped record: R2 1 472.435 **>
R3 1 387.675** > R1h 1 379.721 > R1 1 376.538 > R4 1 116.947 > R5 1 102.947 —
**second dearest of the six.**

### 3.1 It is NOT *"the shipped spelling is not the prediction's spelling"*

`_040` §5.6's mechanism is *"push-as-you-go … deletes both the discriminant
check and the zeroing"*. `safe_tuned.rs` **is** exactly that:
`Vec::with_capacity(num_interfaces)` + `slots.push(pi)`, no `Option`, no fill.
**Both deletions happened and both are worth what the prediction said** — R3 is
5.8 pp under R2 on `small` and 9.0 pp on `large`, and R2's dearness is precisely
the discriminant (`NOTES.md` §8d). So the first of the task file's two candidate
findings is **false**.

### 3.2 It IS *"the prediction's mechanism was wrong"* — incomplete about what REMAINS

Method: `callgrind --tool=callgrind --dump-instr=yes` on the shipped R3 binary,
joined against `objdump -d` by address, so every instruction carries its
**execution count**. `.temp/php42/{instr.py,02-r3-annot.txt}`. The parse is
asserted against callgrind's own `summary:` line, and the sum over the `kernel`
symbol is **34 691 877 Ir = 1 387.675/call, identical to the shipped record's
`kernel_exclusive_ir`.**

**The hot block, verbatim** (`kernel+0x268`, the op loop head; `%r13` is `o`):

```
+616     391385    15.66  cmp    0x70(%rsp),%r13
+621     391385    15.66  je     15c9e   <- panic
+638     391385    15.66  cmp    0x68(%rsp),%r13
+643     391385    15.66  je     15cb6   <- panic
+649 … +736                              seven more cmp/je pairs
+742     391385    15.66  movzbl 0x4c(%r15,%rax,1),%r8d     <- win[p], AT LAST
```

▶ **NINE `cmp`/`je` PAIRS BEFORE THE FIRST BYTE IS READ.** They are the bounds
checks for the nine indexings `rd32`/`rd64` perform per op record — `win[p]`,
`win[p+1..p+4]`, `win[p+5..p+8]` — which LLVM has strength-reduced from
`p + k < win.len()` into an equality test of `o` against nine precomputed
thresholds, hoisted into the prologue (`+407`…`+542`, eight `lea/mul/shr/mov`
groups, ~32 instructions once per call).

**The arithmetic, and it is the whole answer:**

| | Ir/call | share of R3 |
|---|---:|---:|
| the nine window bounds checks (18 instructions × 391 385) | **281.80** | **20.3 %** |
| the pool bounds check `cmp $0x7 / ja` (2 × 422 478) | 33.80 | 2.4 % |
| **R3 − R4, the gap the prediction was about** | **270.73** | — |

▶ **THE SINGLE TERM IS LARGER THAN THE ENTIRE GAP.** And it is **not in the slot
representation**: every safe rung pays it and no unsafe rung does, because R4
spells the same reads `win_get_unchecked`. **No amount of reasoning about
`Option` vs `MaybeUninit` vs `push` could have reached it.**

⚠⚠ **AND THIS IS WHERE §3 AND §5.5 MEET, WHICH IS THE THING WORTH SAYING
PLAINLY.** The row already HAD an answer to *"why is R3 dear"* — `NOTES.md`
§8c's *"R3's `Vec<u32>` scan loops vectorise … R4's do not, because the per-slot
`if wrote[i]` is a branch inside the loop"*. **That answer is refuted** (§5.5:
R3 has 5 vector instructions, R4 has 23, and not one of them in either rung
executes more than ONCE per call). ▶ **So the two findings are one finding in two
halves: the row's published mechanism was wrong, and the nine window bounds
checks are what replaces it.** The vectorisation story is not an incidental
error — **it is the sentence that stood where this measurement now stands**, and
the only reason it survived the build task is that nobody took an
instruction-level profile. ⓘ It is *not* the answer to §6.3 by itself: the
prediction under test is `_040` §5.6's, and §5.6 never mentioned vectorisation.
§8c's was the ROW's later gloss on the same gap, and both are wrong about the
same term.

### 3.3 And the prediction's CONCLUSION is true of a spelling nobody had written

| spelling | A1 Ir/call | vs shipped R3 | remaining window checks |
|---|---:|---:|---:|
| shipped R3 | 1 387.675 | — | **9** per op |
| `r3_oprec_slice` — the op record as ONE 9-byte `&[u8]` | 985.420 | **−28.99 %** | **1** |
| `r3_chunks_exact` — `chunks_exact(9).take(n_ops)` | 969.399 | **−30.14 %** | 1 |
| `r3_chunks_mask` — the above + the pool mask | **942.477** | **−32.08 %** | 1 |

Verified at instruction level: the nine `cmp <threshold>,%r13 / je` pairs are
down to **one** in `r3_oprec_slice` (`.temp/php42` re-profile). The saving the
check removal alone predicts is `16 × 391 385 / 25 000 = 250.5 Ir/call`; the
measured saving is **402.3**, so ~62 % is the checks and the rest is the eight
freed stack slots and the smaller kernel (371 → 282 raw instructions).

⭐ **Under that spelling R3 IS the cheapest rung on the row** (942.477 against
R4's 1 116.947). ▶ **The prediction was refuted by the shipped spelling and
vindicated by a spelling nobody had written** — which is a more interesting
result than either of the two the task file offered.

⚠ **The panic condition does not change.** The shipped reads need
`p + 8 < win.len()`; the sub-slice needs `p + 9 <= win.len()`. Same predicate,
same panics, and all seven checksums unchanged — asserted per variant by stage 1.

### 3.4 The mirror, because a one-sided lever is a story

`r4_win_checked` puts the nine checks **back into R4**: **+33.92 %**. ▶ **The
window-check spelling is worth ~30 % in BOTH rungs and in both directions**,
which is what makes it the row's dominant term rather than an R3 quirk.

---

## §4 ⭐ OPEN ITEM 79, MEASURED — and `_041` §8.12's verdict is right for the wrong reasons

`_041` §8.12: *"the COMPARE-ONLY consumer must read the slot and NOT dereference
it … Comparing without dereferencing needs `core::ptr::eq`, which is
address-dependent (§2.3 forbids that reaching the checksum) and which the pinned
vstd does not specify. So the reference representation can express the faulting
consumer and NOT the comparing one … ZERO `external_body` items … **UNTESTED**,
and it is the first thing I would look at."*

**✅ THE REJECTION STANDS. THREE OF ITS FOUR SUPPORTING STATEMENTS DO NOT.**

### 4.1 The cost, and which consumer it drops

`controls/mu_ref_exec.rs` — `unsafe.rs` with the slot changed from a pool INDEX
(`u32`) to a pool REFERENCE (`Vec<MaybeUninit<&u64>>`), nine substitutions, hit
counts asserted. ⚠ `&u64` rather than `&Iface` because `c/kernel.h:97` declares
`struct ph53_iface { uint64_t id; }` — one `u64` field — so `&u64` is that
struct's reference with the newtype elided; nothing turns on which, and using the
row's own `pool` is what makes it a substitution instead of a fork.

| | |
|---|---|
| cost | **A1 +1.79 %, W1 +1.56 %** against the shipped R4 (`small.bin`, `O3`) |
| answer | **the shipped R4 checksum on ALL SEVEN inputs**, `adversarial-cmp.bin` included |
| the consumer it drops | **the COMPARE-ONLY one**, and only on the VERUS side |

⛔ **So *"can express the faulting consumer and NOT the comparing one"* is FALSE
ON THE EXEC SIDE.** `core::ptr::eq(p, target)` expresses it and gives the *same*
answer, because distinct pool elements have distinct addresses, so
`ptr::eq(&pool[i], &pool[t])` **is** `i == t`. That is not an argument; it is the
seven checksums.

### 4.2 ⭐⭐ Is `ptr::eq` *genuinely unavailable, or unspecified in the pinned vstd*? — **NEITHER. A third thing.**

Three Verus runs, in `controls/mu_ref_cmp.rs`'s header and **executed** by
`controls/spellings.py --verus`:

| spelling | Verus `0.2026.08.09.92f466f` |
|---|---|
| `core::ptr::eq(a, b)` on two `&u64` | ⛔ `error: The verifier does not yet support the following Rust feature: dereferencing a pointer (here the dereference is implicit)` |
| `(a as *const u64) == (b as *const u64)` | ⛔ **the same refusal at the same character position** |
| `a == b` on two ALREADY-RAW `*const u64` | ✅ **verifies**, against `ensures r <==> (a@.addr == b@.addr && a@.metadata == b@.metadata)` |

⭐ **`~/tools/verus/vstd/raw_ptr.rs:221` ships
`assume_specification[ <*const T as PartialEq<*const T>>::eq ]` with exactly that
postcondition.** So **the comparison is fully specified** and *"the pinned vstd
does not specify it"* is false of the comparison and true of nothing that
matters. ▶ **What Verus refuses is turning a `&T` into a `*const T` at all** —
in the free spelling and in the cast spelling alike.

⚠ **That distinction is worth having**: *"a spec is missing"* is something a row
could fix (`external_type_specification`, a `proof fn`); *"the verifier does not
support the coercion"* is not. ⓘ This is `CLAUDE.md`'s standing *grep the
INHERENT spelling as well as the free one* firing again — and this time **the
inherent spelling exists, is specified, and still does not rescue the row.**

⚠⚠ **AND A SECOND, INDEPENDENT BLOCKER SURVIVES EVEN WITH A POINTER IN HAND.**
`vstd::raw_ptr::SharedReference` is the stop-gap route from `&'a T` to `*const T`
(`new` then `as_ptr`) — but `new`'s `ensures` names only `s.value()`, and `ptr()`
is `uninterp`. **Nothing in the pinned vstd relates `&arr[i]`'s address to `i`**,
and `scan_c`'s answer is an INDEX, so the compare-only consumer's postcondition
could not close even if the coercion were supported.

### 4.3 ⛔ *"ZERO trusted items"* is true of a probe and unreachable in a rung

`check.py::_scan_unsafe_sites` requires every `unsafe` token in a pinned Verus
source to sit inside an `external_body` body, and there is no safe exec route
from `MaybeUninit<T>` to `T`. ▶ **ONE trusted accessor is the FLOOR for a
shippable `verus.rs` on this row** (`NOTES.md` §11.5, this row's own finding C);
zero is reachable only in a control. `_041`'s *"ZERO"* came from a probe that is
not gate-admissible.
⭐⭐ **And one accessor is already reached WITHOUT the reference representation,
by `r4_bitmask_min`, at −3.12 % instead of +1.79 %.** So the representation is
dominated on every axis it was proposed for.

### 4.4 ✅ The one advertised benefit is real, and it is now a committed object

**What each of the three committed files establishes — the item asked for one
measurement and these are three objects, so here is the division of labour:**

| file | what it is | what it establishes | how it is exercised |
|---|---|---|---|
| `controls/mu_ref_exec.rs` | the **exec rung**: `unsafe.rs` with the slot changed to `MaybeUninit<&u64>`, 9 substitutions, hit counts asserted | **the COST (+1.79 % A1, +1.56 % W1) and that `ptr::eq` DOES express the compare-only consumer** — shipped checksum on all 7 inputs, `adversarial-cmp.bin` included | a `spellings.py` variant (`r4_mu_ref`), built, run and priced on every invocation; **inadmissible by rule** (`r4_no_twin_reason`) and by English |
| `controls/mu_ref.rs` | the **verifying half** of the Verus side | the **faulting** consumer verifies on this representation at **8 verified / 0 errors** with ONE trusted item, **and `unsafe.rs`'s FOURTH precondition (`p < MAXP`) disappears** | `spellings.py --verus` stage 4b, **must-NOT-fire** |
| `controls/mu_ref_cmp.rs` | the **refused half** — the same program plus the compare-only consumer | the exact refusal text, and the three-layer analysis of it in its header | `spellings.py --verus` stage 4b, **must-FIRE**, with `does not yet support` asserted as the needle |

⭐ **That is why it is three files and not one**: a sentence saying *"Verus
refuses it"* rots silently, and an arm that must FIRE stops being true out loud
the day Verus supports the coercion. §H case `F12` re-runs the refusal
independently of the sidecar.


`controls/mu_ref.rs` verifies the FAULTING consumer on this representation at
**8 verified / 0 errors** with one trusted item, and `instanceof_ref` does not
take `pool` at all — so `unsafe.rs`'s header's FOURTH precondition, *"`p < MAXP`
… the PRICE OF THE REPRESENTATION and not part of the C's obligation"*,
**disappears**. That is the row's own claim, checked.

### 4.5 ⚠ Is a two-representation row admissible? — **STATED, NOT DECIDED**

§B/§A1 give a row one kernel, one `u64` and one oracle, and `spec.md`'s `u64` is
address-free by construction (`_041` §5.5 dropped a redundant `||` disjunct from
the C for exactly that reason). `ptr::eq` puts an address back into a
control-flow decision every rung would have to agree on. ▶ **It therefore ships
as `controls/` variants, which is what the task file's §2.3 asked me to state and
not settle.** Nothing in the row's published numbers changes either way.

---

## §5 THE SEARCH — 20 variants shipped, 4 priced and dropped

`patterns-php/ph53-iface-tail-uninit/controls/spellings.{py,json}`, cloned from
`ph45`'s (itself `ph29`'s guarded copy, carrying F79's two fixes and item 63's
third). Exit **0**, `problems: []`. Full table and mechanisms: `NOTES.md` §8j.

**Stage 3 reproduces the shipped cells before any variant is quoted:** A1
against `results-php/ph53-iface-tail-uninit.json` in **four** cells, all to
**`0.0000 %`**, and W1 against `NOTES.md` §8e's committed whole-program total to
**`0.0009 %`**.

### 5.1 What moved, in one table (A1, `small.bin`, `O3`/`isolated`)

| | cheapest in contract | vs shipped | TCB | degenerate? |
|---|---|---:|---:|---|
| **R3** | `r3_chunks_mask` | **−32.08 %** | — | **`false`** |
| **R4** | `r4_bitmask` | **−11.40 %** | 6 | **`false`** |

**Published, labelled, two quantities per family** (and **NO PAIR INTERVAL**):

> **`fixed-R4 bound`** (both endpoints held by fiat) — **A1 `+24.24 %`**,
> **W1 `+21.15 %`**.
> **R3-side span**, cheapest-found .. dearest-found in contract —
> **A1 `−15.62 %` .. `+24.28 %`** (`r3_chunks_mask` .. `r3_slice_param`,
> measured against R4ship).

⚠⚠ **THE ORDERING REVERSES AND IT IS AN ORDERING.** Cheapest R3 found 942.477
against cheapest R4 found 989.670 — R3 cheaper — where the shipped bound says R3
is +24.24 % dearer. **A difference of two minima bounds nothing in either
direction** and is never quoted as an interval, here or in the sidecar.

### 5.2 ⭐⭐⭐ The R4 side: cheaper AND smaller-surface, at the same time

| variant | A1 vs R4ship | TCB (`external_body`) | accessor call sites | twin |
|---|---:|---:|---:|---|
| `r4_bitmask` | **−11.40 %** | 6 | 10 | 31 / 0 |
| `r4_bitmask_pool` | **−8.37 %** | **5** | 8 | 31 / 0 |
| `r4_bitmask_min` | **−3.12 %** | **3** | **3** | **32 / 0** |
| **shipped R4** | — | 6 | 10 | 27 / 0 |
| `r4_set_checked` | +0.50 % | **5** | 9 | 27 / 0 |
| `r4_win_oprec` | +2.99 % | **5** | 5 | 27 / 0 |
| `r4_pool_checked` | +3.03 % | **5** | 8 | 27 / 0 |
| `r4_min_trusted` | +6.60 % | **3** | 3 | 28 / 0 |
| `r4_win_checked` | +33.92 % | 5 | 5 | 27 / 0 |

**`r4_bitmask_min` is the row's answer to the question `ph07`'s `r4_index0` and
`ph29`'s `r4_fold_iter` each answered half of**: cheaper *and* a strictly smaller
trusted base, with the twin verifying at a HIGHER count (32) than the shipped
rung's (27) because the bit-vector lemmas are real proof obligations.

**And the two effects are separable, which is why both halves ship:**

* the trusted-surface reduction **with the shipped witness** is `r4_min_trusted`
  at **+6.60 %**;
* the witness **with the shipped surface** is `r4_bitmask` at **−11.40 %**;
* together, **−3.12 %**.

⚠ **So a smaller trusted surface is NOT free on this row either** — `ph45`'s
result reproduced, four times over (+0.50 %, +2.99 %, +3.03 %, +6.60 %). What is
new is that a *different* lever pays for it.

**The bitmask's proof cost, exactly:** one `spec fn wbit(w: u32, j: int)` and
**two `by (bit_vector)` lemmas** (`lemma_set_bit`, `lemma_zero_bit`), ~45 lines.
**No new trusted item, no `assume`, no `external_type_specification`, no
`is not supported`.** ⚠ It does not carry `idiom.required[4]`'s backticked
`wrote[i]`; that is reported as a `required` miss and, per `check.py`'s own
semantics, does not disqualify. **A reader who thinks the shipped witness
spelling is part of the contract should read that miss as the argument against
this variant, and it is printed for exactly that reason.**

### 5.3 ⭐⭐ `&[u8; N]` + `try_into` is **BYTE-IDENTICAL** to the plain sub-slice

Same 282 instructions, same `kernel` digest, same A1 and W1 to the digit — and
**re-verified in two different build directories**, so it is not an artefact of
§8's path sensitivity. ▶ **`ph45` §5.6's result on a second row and in its
sharper form**: there the fixed-size type was a TIE *within a 0.05 % threshold*,
here it needs no threshold at all. **The compile-time-constant length buys
exactly nothing.**
⭐ And the three spellings of that lever are **not all a tie**: `chunks_exact` is
1.63 % under the two byte-identical ones, because the iterator deletes the per-op
offset arithmetic as well. **The TYPE buys nothing, the ITERATOR buys 1.63 %, the
CHECK COUNT buys 29 %.**

### 5.4 ⭐⭐ The witness, re-priced in ONE pipeline

| | W1 Ir/call | above `ctl_nowitness` |
|---|---:|---:|
| `controls/r4_nowitness.rs` | 1 051.044 | — |
| `r4_bitmask` | 1 152.632 | **+9.665 %** |
| shipped R4 (`[bool; MAXD]`) | 1 279.911 | **+21.775 %** |

✅ **The +21.775 % reproduces `NOTES.md` §8e to 0.0009 %**, across two
independent pipelines (`controls/negatives.py --cost` and this one).
⭐ **The bitmask witness costs 9.665 %.** *"The cheapest witness that makes R4
provable costs 21.8 %"* is **withdrawn**; 9.7 % replaces it and is itself an
upper bound.

**And the cost splits, exactly** (A1, `small.bin`): the witness TEST costs
**39.42 Ir/call in BOTH spellings** — 12 `cmpb` sites in the shipped rung and 2
`bt` sites in the bitmask one, summing to the identical figure, i.e. one
instruction per slot iteration (985 384 iterations / 25 000 calls). So of the
shipped witness's **+228.87 Ir/call** over `r4_nowitness`, **+101.59 is the
witness as such** and **+127.28 is the array being in MEMORY**.

### 5.5 ⛔⛔ TWO COMMITTED MECHANISM CLAIMS REFUTED

Method: vector-instruction census over the `kernel` symbol **with execution
counts**, not static counts.

| | `xmm` instructions | of which executed > ONCE per call |
|---|---:|---:|
| R3 `safe_tuned` | **5** | **0** |
| R4 `unsafe` | **23** | **0** |
| `controls/r4_nowitness.rs` | 17 | 0 |
| `r4_bitmask` | 21 | 0 |
| `r3_oprec_slice` | 5 | 0 |

* ⛔ **`NOTES.md` §8c**: *"R3's `Vec<u32>` scan loops **vectorise** (352 static
  instructions, `xmm`); R4's do not"* — **R4 has 4.5× as many vector
  instructions as R3, and in neither rung is one of them inside a scan loop.**
  All of them are the `pool` / `idx` / `wrote` array zero-fills, once per call.
  The `xmm` the sentence pointed at was `[0u64; MAXP]`'s initialiser.
* ⛔ **`NOTES.md` §8e**: *"the witness-free scan loops are branch-free … and LLVM
  **vectorises and unrolls** them"* — **neither.** `r4_nowitness` has 17 vector
  instructions, all once-per-call, and is *smaller* (266 raw instructions against
  766), so the duplication is in the SHIPPED rung.

✅ **What survives in both cases**: the static counts (352 / 758) are right, R4
really is cheaper than R3 as shipped, and the +21.775 % is a correct measurement.
**The refutations are about WHY** — `PROTOCOL.md` rule 9's conclusion/mechanism
split, and F72/F87-result-3's discipline applied to two claims this row shipped.
Both are struck and replaced **in place** in `NOTES.md`, not only here, because
the row outlives the report.

### 5.6 The four priced and dropped, and two of them close open questions

| spelling | A1 | vs shipped side | verdict |
|---|---:|---:|---|
| R3 `[u32; MAXD]` + `len` for `Vec<u32>` | 1 184.996 | −14.60 % A1 / **−21.73 % W1** | ⛔ English: deletes the allocation, where `required[8]` declares **exactly one** per call. ⭐ With `r3_no_capacity` (+27.36 % W1) it **BRACKETS** the declaration, and **A1 reads −14.60 % and −1.30 % on those two cells — 7 pp short on the first and the WRONG SIGN on the second** |
| R4 `wrote` via `get_unchecked` | 1 001.936 | **−10.30 %** | ⭐⭐ **refutes `_041` §8.4**, which guessed *"the choice is probably free and I did not verify that"*. **It is not free.** And it would cost a FIFTH trusted item |
| R4 without `#[inline(always)]` on the consumers | 1 117.947 | **+0.09 %** | ⭐⭐ a **clean negative about `ph45`** |
| R3 without `#[inline(always)]` on the consumers | 1 387.675 | **+0.00 %** | identical to the digit |

⭐⭐ **THE LAST TWO ARE A CROSS-ROW RESULT AND THEY ANSWER `TASK_PHP_037` §10.1
BY NAME.** That report asks the manager to rule on *"IS `#[inline(always)]` A
RESPELLING? … without it the winner is +16.65 % instead of −23.47 %"* — a **40
percentage-point** swing. ▶ **On `ph53` the same attribute on the same kind of
helper is worth +0.09 % and 0.00 %.** So `ph45`'s 40 pp is a property of
`ph45`'s loop shape, not of the programme. ⚠ **It does not settle `ph45`'s
ruling** — it says the lever is not generic.

⚠⚠ **AND THE HONEST SHAPE OF THIS SECTION IS THAT ALMOST NOTHING WAS DROPPED.**
`ph45` priced seven and dropped them; here 20 of 24 shipped, because the
substitution machinery makes shipping a priced variant nearly free and because
the two out-of-contract ones are more informative inside the sidecar than in a
log. **That is a difference in method, not in rigour — but it also means this
search is WIDER on the levers I thought of and no deeper on the ones I did
not.** §9 lists what I did not try.

---

## §6 §H — 161 CASES (138 must-FIRE, 23 must-NOT-fire), ALL PASS; 3 DEFECTS FOUND BY A NEGATIVE AND A FOURTH BY RE-READING

`.temp/php42/negatives_spellings.py --all`, groups A–K. `ph16`'s bar was 54,
`ph29`'s 75, `ph45`'s 128.

| group | n | what it attacks |
|---|---:|---|
| A | 14 | the spelling audit — a planted `forbidden` fires and DISQUALIFIES, a `required` miss REPORTS and does not, the comment hole, the `lang` key, and the bitmask variant's `wrote[i]` miss recorded and non-fatal |
| B | 19 | `apply_subs` / `materialise` — hit counts in both directions, **the ORDERING TRAP**, all 9 exec and all 9 twin lists applied, the twin gets the VERUS list, every variant and every twin a distinct program, both driver-path depths |
| C | 21 | the verdict functions — four exclusions, `TIE_PCT` either side, `RUNG_SIDES`, `smaller_surface` on equal/unknown TCB, **C17 pinning the DEFAULT KEY to A1**, `witness_cost` |
| **D** | 22 | the fingerprint — F79's two on this clone, item 63's third, `byte_identical_pair`, offset normalisation, register sensitivity, **and §8's path-length property in all three of its measured spellings** |
| E | 13 | both Ir families, the `PROGRAM TOTALS` parse in 5 shapes, `_sum_rows` identity, **E7/E8 pinning the headline choice to the MEASURED spread**, PROBES against the record |
| **F** | 14 | the Verus reader — **F5/F6: the `does not yet support` needle `ph45`'s copy does not have**, a failed postcondition is NOT a disqualification, and the shipped twin plus all three `controls/*.rs` Verus arms re-run here |
| G | 15 | `check.py::control_json_verdict` driven directly, and the sidecar's pin — **G7 resolves all 11 pinned paths and asserts the COUNT, so it cannot pass vacuously** |
| **H** | 12 | `identity_premise` / `admissibility` — pin and record read separately, `exact`/`differ` disagreement, the shared block's boilerplate `O3 exact` string present while the pin is `differ` |
| **I** | 17 | `trusted_accessors` / `trusted_items` / `unsafe_tokens` — `ph45`'s leaked-loop-variable shape, comment stripping, generic definitions, **and the `−1`** |
| **J** | 7 | ⭐ `r4_no_twin_reason` — the rule `ph45`'s copy leaves as a silent skip, and that it REACHES the sidecar |
| K | 7 | the CLI end to end; `--audit-only` writes no sidecar; the shipped sidecar's own invariants |

**THREE real defects, all three in code written this task, and the first two
produced a PLAUSIBLE WRONG NUMBER rather than an error:**

1. ⭐⭐ **`trusted_accessors` RETURNED `−1` ON A GENERIC DEFINITION, and
   `controls/mu_ref_exec.rs` reported SEVEN call sites where it has NINE.** The
   call regex was `\bNAME\s*\(`, which does not reach across `<'a>`, while the
   definition regex did — so each of `mu_ref_exec.rs`'s two generic accessors
   scored 0 calls and 1 definition and the subtraction went negative. **This is
   `TASK_PHP_037` §6.2's leaked-loop-variable defect in the same function, one
   generation on**: a safe-looking count, in the function whose whole job is to
   measure the trusted surface, found by a case (`I6`) and not by reading.
   ▶ Fixed to match the bare identifier, **with an `assert c >= 0` so the next
   miscount is an error**, and three more cases added (`I6b`, `I6c`, `I6d`, the
   last asserting the corrected **9**).
2. ⚠ **A case of mine passed on prose rather than on code.** `B16` asserted the
   bitmask variant no longer contains `[bool; MAXD]` — but `unsafe.rs`'s HEADER
   explains that witness at length, so the string survives a code-only
   substitution and the case FAILED. Fixed to strip comments first, **with a
   companion (`B16b`) asserting the string really is in the shipped rung's code,
   so the repaired case cannot pass on an empty haystack.**
   ⓘ **And the underlying fact is a real cosmetic defect I am not fixing**: every
   materialised variant carries the shipped rung's header, so `r4_bitmask`'s doc
   comment describes a `[bool; MAXD]` witness it does not have. A doc comment is
   not measured; `ph45`'s variants have the same property; recorded rather than
   hidden.
3. ⚠⚠ **A CASE OF MINE ASSERTED A PROPERTY THAT IS TRUE OF ONE SPELLING AND
   NOT OF THE OTHER TWO.** `D18a` — §8's path-length property — was written over
   `safe_tuned.rs` and **FAILED**: the shipped R3's digest is path-INSENSITIVE.
   Measured over three spellings: `r3_oprec_slice` moves, `v0_shipped` and
   `r3_chunks_exact` do not. ▶ **So the claim I was about to publish — *"the
   digest is not comparable across build directories"* — was right in its usable
   form and wrong as stated**, and a control that had checked one spelling would
   have concluded either way. Repaired to `r3_oprec_slice` **with two companion
   must-NOT-fire cases recording the two insensitive spellings** (`D18a2`,
   `D18a3`), and the docstring and `NOTES.md` §11a now say *never compare a
   digest across directories* rather than *it always differs*.
   ⭐ **This is the only one of the three that would have put a false sentence
   into a committed file.**

⚠⚠ **AND THE SIDECAR'S OWN PIN FIRED AGAINST ITS AUTHOR, ON ITS FIRST
OPPORTUNITY.** After the third regeneration I made one more `NOTES.md` edit — a
table caption — and `G7` came back `got=None`, i.e. it RAISED: *"NOTES.md moved
under the sidecar"*. ▶ **`ph45` §8.1's lesson, reproduced exactly: `NOTES.md` is
in `derived_from_sha256` because stage 3 reproduces the W1 family against §8e,
so the regeneration order is PROSE FIRST, SIDECAR SECOND, GATE THIRD — and I had
it prose–sidecar–prose.** Reported rather than quietly re-run, because it is the
pin doing the job it exists for.

### 6.1 ⛔⛔ AND A FOURTH DEFECT THAT NO NEGATIVE COULD HAVE FOUND — IT WAS IN MY OWN PROSE

**`ph45` §8.3's *"F72 hedge"* on this row, and it is the F72 / F87-result-3 shape
exactly: a docstring asserting the mechanism its own file's measurement
overturns.** Re-reading `controls/spellings.py`'s docstring after the numbers
were settled, its witness paragraph ended

> ~~*"the measured figure is 9.7 %, and the mechanism §8e gives (lost
> vectorisation, not the byte) is what a register-resident witness recovers."*~~

⛔ **That endorses, in a committed file, the mechanism THIS TASK REFUTED two
sections earlier.** Nothing vectorises inside a scan loop in any rung of this row
(§5.5). ▶ Struck and replaced with what the measurement does support — the
39.42 / +101.59 / +127.28 split — and the same edit named the R3 winner
(`r3_chunks_mask`, −32.08 %), which the header quoted `r3_oprec_slice` and
`r3_both` instead of. `.temp/php42/fix_docstring.py` carries both anchors and a
`--check` dry run, applied as ONE edit so the sidecar regenerates once.

⚠⚠ **THE TWO DEFECTS, NAMED.** (i) ⛔ **the causal clause above — a file whose
stage 2 measures 5 / 23 / 17 / 21 `xmm` instructions and 0 executed more than
once per call, telling its reader the cost is *lost vectorisation*.** (ii) ⚠ the
same paragraph's R3 headline quoted `r3_oprec_slice` (−29.0 %) and `r3_both`
(−30.6 %) and **did not name the winner**, `r3_chunks_mask` (−32.08 %), which
existed only in the stage-5 output and the sidecar's
`cheapest_r3_in_contract`. Both are in `.temp/php42/fix_docstring.py`, applied
as one edit with a `--check` dry run.

⚠ **A negative cannot catch (i) and I am not pretending otherwise**: the
sentence was internally consistent, cited a real section, and every number in it
was right. **What was wrong was the causal clause, and the only detector is
re-reading the prose against the numbers after they are settled.** That is
`PROTOCOL.md` rule 9's conclusion/mechanism split turned on its author — and the
**second** time in this task I repeated a claim I had inherited rather than
measured. **The first cost me a prediction** (§11.1: I predicted the bitmask
witness would fail, on the strength of the same refuted sentence). **This one
would have cost a committed file.**

⚠ **Trap 7 honoured deliberately in group F**: F4 asserts that the
failed-postcondition case's output really carries a `verification results::`
line, so F2/F3 cannot pass because Verus refused to parse the file; and G7 is
written to resolve the sidecar's **shim-root** keys against the ROW directory,
because resolving `patterns/<row>/…` against the real repo root finds the PAT
tree, every path is absent, and the case passes on an empty list — which is
`TASK_PHP_037` §6.2 defect 3 exactly.

---

## §7 THE GATE AND THE CLOSING BRACKET

⚠ **Every verdict below is read out of
`results-php/gate/ph53-iface-tail-uninit.json` with a `python3 -c`, never out of
a log** (task file §4 trap 4's discipline, and `ph45` §8's).

### 7.1 ROUND 1 **FAILED** on exactly three `[tables]`, and all three were mine

```
verdict   FAIL      failures 3, all [tables]
```

1. *"`results/tables/…md` is STALE: it cites contract `['7013be6f7c1c']` and
   `spec.md`'s `slb-contract` block now hashes to `c41ffad2b795`"* — **expected
   and owed**: F99's citation lives inside the hashed block, so repairing it
   moves `contract_sha256` and the published table has to be re-rendered.
2. *"`controls/spellings.json` is STALE: 1 of 11 pinned source(s) moved under it
   (`NOTES.md`)"* — ⚠ **the sidecar's pin firing against its author for the
   second time in this task.** Same cause as the `G7` self-catch in §6: I made a
   prose edit after regenerating.
3. *"STALE IN ITS CONTENT: 5 line(s) differ"* — the two contract-hash lines (in
   both of the table's two copies of the header) plus the line a **STALE**
   sidecar adds. ⭐ `ph45` §8.2's mechanism, confirmed on a second row:
   `report.py::shout_section` prints a line for every `controls_json` entry whose
   value is **not** `"FRESH"`, so the STALE sidecar *added* a line and a FRESH
   one adds none.

▶ **So the fix was the documented chain and nothing more**: regenerate the
sidecar → **gate** (so the record carries `FRESH`) → **`report.py`** (which
reads that record, and only after the gate has written it) → **gate**. Stage 9c
says so in terms: *"`harness/report.py` reads that record only after this run has
written it, which is why `report.py` comes after the gate and not before."*

### 7.2 THE FINAL RUN — **GREEN**, read out of the record AS FIELDS

⚠ **There were TWO green rounds, and the second is the shipped one.** Round 3
(`27-gate-final.log`) went green over the tree as it then stood; then §6.1's
docstring fix landed, the sidecar was regenerated, the 161 negatives re-run
(**161 as declared, 0 failures**), and **one** more gate round
(`30-gate-shipped.log`) went green — one round and not three, because the
published table renders `contract_sha256`, the audit rows, `loud` and
`controls_json`, **none of which a docstring edit moves.** That prediction was
made before the run and held.

⚠ **Quoted with a `python3 -c` over
`results-php/gate/ph53-iface-tail-uninit.json`, field by field, not summarised**
(task file §6 item 6):

```
verdict         = PASS-WITH-BLOCKED-ROWS
failures        = []
complete_run    = True
contract_sha256 = c41ffad2b795767b221141f4f2332a68a9800eb79c594997ae474d46795dbe80
controls_json   = {'spellings.json': 'FRESH'}
source_sha256   = 41 files          (37 before -- the four new controls/ files)
loud            = 6 entries: doc-citation-other, idiom-forbidden, tcb-unsafe x2, twin x2
verus           = {'verus.rs': {'verified': 27, 'errors': 0, 'pinned': 27}}
blocked         = 1: verus.rs `slot_read_unchecked` (strength unchecked)
idiom_audit     = spellings 15, rungs 6, pairs 46, present 20,
                  forbidden_spellings 6, forbidden_hits 0,
                  required_pins_nothing 0, required_absent 8,
                  forbidden_unaudited_entries 1, no_rung_entries 0
miri            = ran True, available True, ub False on all 7 runs
identity        = unsafe vs verus  O0  level 'differ'  expected 'differ'
                    counts_a [888, 888, 5087]  counts_b [789, 789, 4406]
                    md5_raw_equal False
identity        = unsafe vs verus  O3  level 'differ'  expected 'differ'
                    counts_a [764, 758, 3038]  counts_b [746, 741, 2996]
                    md5_raw_equal False
```

✅ **`PASS-WITH-BLOCKED-ROWS` with `failures []` is the CORRECT verdict for this
row and not a near-miss** — the one blocked row is `slot_read_unchecked`'s
missing twin, which **cannot exist** (`NOTES.md` §11.5, this row's own finding
C), justified in `spec.md`, and present in the build task's record too. `p01`,
`p35` and `ph00-smoke` carry the same verdict. **I did not "fix" it.**

✅ **`controls_json` reads `{'spellings.json': 'FRESH'}`.** It read `{}` before
this task.

✅ **`contract_sha256` moved exactly once and only for F99's sentence**
(`7013be6f…` → `c41ffad2b795…`), disclosed in `NOTES.md`'s first box with what
moved and what did not.

✅ **`loud` is 6 entries and NONE of them is new.** Verified against the previous
record rather than assumed: `git show HEAD:results-php/gate/ph53-iface-tail-uninit.json`
also has **6**, with the identical section list.

✅ **`identity` is pinned `differ`/`differ` and MEASURED `differ`/`differ`** —
which is the premise `admissibility()` reads at run time, and the reason nine
twins were admissible on verification alone.

ⓘ **`verus_checked` and `problems` are NOT keys of a gate record** — F99, and
re-confirmed here: `'verus_checked' in g` and `'problems' in g` are both
**False**. They ARE keys of `controls/spellings.json`, where they read `true`
and `[]`.

### 7.3 ⚠ FOR ROUTING — four things this task measured that are not about this row

1. ⛔ **`kernel_fingerprint`'s digest is path-sensitive and it would be a LIVE
   false-negative on `ph29`.** §8.
2. ⚠ **OPEN ITEM 61's COUNT PREDATES THIS ROW.** The shared `why` block argues
   R4 admissibility from *"All six patterns pin `identity: unsafe == verus, O3
   exact`"*, and item 61 records that as false on **three** rows. Measured over
   all eight php `spec.md`s just now: the `O3` pin is `exact` on `ph00`, `ph03`,
   `ph16`, `ph29`; **`norel` on `ph07`; `differ` on `ph45`, `ph53` and `ph64`.**
   ▶ **Four of eight, not three of six** — `ph53` joins the group, and its
   search was wider for exactly that reason (an R4 candidate here needs only to
   VERIFY, which is what let nine twins in).
3. ⭐ **`TASK_PHP_037` §10.1's `#[inline(always)]` RULING NOW HAS A SECOND DATA
   POINT**, and it points the other way: +0.09 % and 0.00 % here against
   `ph45`'s 40 pp. §5.6.
4. ⭐ **`ph53`'s OWN FINDING C — *two sound gate rules are jointly unsatisfiable
   for a `MaybeUninit` read* — IS NOW A MEASURED FLOOR RATHER THAN AN
   ARGUMENT.** `r4_bitmask_min` reaches **one** trusted accessor and verifies;
   `r4_mu_ref`/`mu_ref.rs` reach one on a different representation and verify;
   **zero is reachable only in a control, on either representation.** §4.3.

---

## §8 ⚠ A FOURTH DEFECT IN THE *SHARED* `spellings.py` MACHINERY — latent here, LIVE on `ph29`

`kernel_fingerprint`'s digest **is not comparable across build directories**.
`r3_oprec_slice` built in two directories whose paths differ by 38 characters
gives **282 instructions both times and two different digests**
(`452842362705`, `0abc7468b349`), because `rustc` embeds the source path in its
panic-location data and the **rip-relative displacements the function
deliberately keeps** move with it.

⚠⚠ **AND IT IS VARIANT-DEPENDENT — 1 of 3 SPELLINGS MEASURED — WHICH IS THE
SHARPER STATEMENT AND WHICH I ONLY LEARNED BECAUSE A NEGATIVE FAILED.**
`v0_shipped` and `r3_chunks_exact` come out IDENTICAL across the same two
directories; only `r3_oprec_slice` moves. ▶ **So the usable rule is *never
compare a digest across directories*, not *it always differs***, and the first
draft of the case that tests this used `safe_tuned.rs` and **failed** — §6
defect 3. A control that had checked one spelling would have concluded either
way.

* ✅ **LATENT ON `ph53`.** `identity` is pinned and measured `differ`, so
  `twin_identical` is information here and not a bar; and §5.3's byte-identity
  claim was re-verified in **both** directories, so it is not an artefact.
* ⛔ **IT WOULD BE LIVE ON `ph29`.** `ph29` pins `identity: O3 exact` and uses
  the same function as a **BAR**, and its `materialise` compares
  `<side>_<name>.rs` against `<side>_<name>_verus.rs` — **six characters
  apart**. ▶ The failure mode there is a **FALSE `!= exec`**: refusing an
  admissible candidate and reporting an endpoint as DEGENERATE when it is not.
  ⓘ **`ph29` NOT edited** (open items 57/63's scope). **Reported for routing**,
  with the guard and the measurement written into this row's
  `kernel_fingerprint` docstring and `NOTES.md` §11a.

⭐ **That is items 57 and 63's shape one generation further on**, and this time it
is not a false POSITIVE (two missing binaries comparing equal) but a false
NEGATIVE (two identical programs comparing different) — a defect a green run
cannot show you, because it makes the search look *narrower* than it is.

---

## §9 ⚠ WHAT I AM UNSURE OF, AND WHERE I MOST WANT TO BE ATTACKED

⭐ `UNTESTED` and *I could not tell* are the intended answers here.

1. ⚠⚠⚠ **IS `r3_chunks_exact` A RESPELLING OR A DIFFERENT PROGRAM? This is the
   call I am least sure of and it carries the R3 headline.** It removes a panic
   path the shipped spelling HAS: `take(n_ops)` cannot run off the end, where
   `win[p]` would panic. Arguments for admitting it: the condition is
   unreachable (`n_ops = rd32(win, 8) % (cap + 1)` and `chunks_exact` yields
   exactly `cap` chunks), all seven checksums are unchanged, nothing in `idiom`
   pins the op loop's form, and `r3_pool_mask` — which I also ship — removes an
   unreachable panic the same way. Argument against: a search that may delete
   unreachable panic paths can find a "cheaper spelling" on almost any safe
   rung, and *"the bounds check LLVM could not eliminate"* is arguably the thing
   the safe rung is FOR. ▶ **`r3_oprec_slice` (−28.99 %) does NOT have this
   property** — its sub-slice panics on exactly the shipped predicate — so if
   the manager rules `chunks_exact` out, the R3 endpoint still moves by 29 % and
   nothing in §0 is withdrawn. **Please rule on it by name.**
2. ⚠⚠ **THE `required[4]` MISS ON EVERY BITMASK VARIANT.** `idiom.required[4]`
   backticks `wrote[i]` and calls it *"THE ONE-BYTE-PER-SLOT WITNESS"*. The
   three bitmask variants do not contain it. I treated that as `check.py` does —
   report, do not disqualify — and `ph45`'s control does the same. **But the
   entry's English is emphatic about the representation** (*"THE
   ONE-BYTE-PER-SLOT WITNESS … It is indexed SAFELY on purpose"*), and a
   reviewer could reasonably read it as pinning `[bool; MAXD]`.
   ▶ **Under that reading the three cheapest R4 variants all drop out, the
   remaining in-contract set is `{+0.50, +2.99, +3.03, +6.60, +33.92}` % — none
   cheaper than the shipped rung — so `r4_endpoint_degenerate` becomes TRUE and
   §0's headlines 2 and 4 both fall.** (Headline 1 survives on the R3 side and
   headline 3 does not depend on it.) **This is the single reading that would
   cost the most, I cannot settle it from inside the row, and the `required`
   miss is printed for every affected variant so a reviewer meets it before the
   number.**
3. ⚠ **I DID NOT RE-MEASURE THE ROW'S PUBLISHED CELLS, I REPRODUCED THEM.** A1
   matches the record to `0.0000 %` in four cells — which is strong evidence
   that the pipeline measures this row, and **no** evidence that the record is
   right about anything the record and this pipeline share (`measure.py`,
   `build.py`, the binaries). A common-mode error would reproduce perfectly.
4. ⚠ **THE `+127.28 Ir/call` ATTRIBUTION IS A SUBTRACTION, NOT A PROFILE.** I
   measured that the witness TEST costs 39.42 Ir/call in both spellings and that
   the totals differ by 127.28; I did **not** walk the disassembly to say where
   those 127 go. The story I offer — LLVM peels the memory-witness loops into
   twelve copies and pays address arithmetic — is consistent with 766 against
   296 static instructions and with 12 `cmpb` sites against 2 `bt` sites, and it
   is **NOT verified at the instruction level**. F72's shape. ▶ **Treat the split
   as measured and the reason as open.**
5. ⚠ **THE NINE-CHECK ACCOUNTING IS 62 % OF THE SAVING, NOT 100 %.** 250.5 of
   402.3 Ir/call. I attribute the rest to the eight freed stack slots and the
   smaller kernel; I did not measure that split. The **term** (281.8 Ir/call,
   20.3 %) is measured directly and does not depend on it.
6. ⚠⚠ **`r4_bitmask_min`'s TWIN VERIFIES AND I HAVE NOT AUDITED ITS TRUSTED
   ITEM's CONTRACT the way `spec.md` audits the shipped four.** `mu_read`'s
   `requires` is one conjunct (`is_init`) where `slot_read_unchecked`'s is two,
   which is *weaker surface* — but nobody has written the
   `SLB-TRUSTED-ARGUMENT` block for it, and if the manager ever moved the
   shipped rung that block is owed. **A variant is not a rung and this is why.**
7. ⚠ **THE BIT-VECTOR LEMMAS ARE MINE AND UNREVIEWED.** `lemma_set_bit` and
   `lemma_zero_bit` are two `by (bit_vector)` facts with `j < 32` preconditions.
   They verify. **I did not attack them with a mutant** the way
   `controls/negatives.py` attacks the shipped proof — so *"31 verified /
   0 errors"* is evidence that Verus accepted them and **not** evidence that the
   invariant they support is non-vacuous. ⓘ The non-vacuity that IS checked is
   the row's own: the twin still carries the value postcondition
   `r == iface_fold(...)`, so a vacuous witness invariant could not have
   produced the right answer.
8. ⚠ **`MAXD = 64` IS STILL UNTESTED** (`_041` §8.2). It needs `c/kernel.h` and
   `inputs/gen.py`, i.e. a 32-cell re-measure. ⛔ Out of this task's scope by
   trap 2, and the bitmask witness is the one candidate whose cost *would* move
   with it (a `u32` mask holds 32 bits).
9. ⚠ **THE `r3_no_capacity` / stack-array PAIR IS A BRACKET, NOT php-5.2.0.**
   `Vec::new()` doubles, i.e. O(log n) allocations; `erealloc(..., ++n)` is O(n).
   **So +27.36 % W1 is a LOWER bound on 5.2.0's schedule**, and `_041` §8.6's
   question is priced rather than answered.
10. ⚠ **I DID NOT TRY**: an iterator-based *scan* (`slots.iter().position()`),
    `pool` as a `&[u64]` of length `n_pool`, a `u64` mask, `#[inline(never)]`
    anywhere, or any R2 respelling. **The search is wider on the levers I
    thought of and no deeper on the ones I did not**, and §5.6's honesty note
    says so.
11. ⚠ **`NOTES.md` PUBLISHES TWO WHOLE-PROGRAM TOTALS FOR THE SAME CELL** —
    §8e's 31 997 489 and §8f's 31 997 125, 364 Ir apart (0.0011 %), with kernel
    counts 760 and 762 — because they come from two different
    `controls/negatives.py` runs. **Neither is wrong; they are not the same
    build.** I pinned §8e (it is the section this task corrects) and said so in
    `reproduces_shipped_record_scope` rather than silently choosing.
12. ⚠ **THE `english_verdict` MECHANISM IS DOING MORE WORK HERE THAN ON `ph45`**
    — two shipped variants and one control use it, against `ph45`'s zero. Each
    sentence is the row's own declaration (`required[8]`, §2.3), and each is
    printed with its priced figure beside it so a reader who disagrees with the
    exclusion can still read the number. **But an exclusion no grep can check is
    the weakest thing in this control**, and three of them is three chances to
    be wrong.
13. ⓘ **The materialised variants' HEADERS are stale** (§6 defect 2). Cosmetic;
    `ph45` has it too; named rather than hidden.
14. ⚠ **`.temp/php42/` is gitignored**, so every number this report rests on is
    **in this report and in `NOTES.md`**, not behind a pointer. The paths in §10
    are for re-derivation only.

---

## §10 EVIDENCE

⚠ **Keep the generator, delete the artefact** (`CLAUDE.md` constraint 6): every
binary, `.bin`, `__pycache__` and callgrind dump under `.temp/php42/` is deleted
once the gates are green; what stays is a generator, a source or a log.

| path | what it is |
|---|---|
| `00-EXPECTATIONS.md` | my predictions, written **before the first `rustc` call**, with the named bias (*"I want the R3 endpoint to move"*) and the guard set against it. **Three of them are wrong — §11** |
| `explore.py` | the build + price + fingerprint + checksum harness; the logic that survived is in `controls/spellings.py` |
| `instr.py` | ⭐ **per-INSTRUCTION `Ir` inside `kernel`**, which is what §3 and §5.5 rest on. Its docstring records the three parse defects it started with, each of which returned a figure-shaped zero; the totals are asserted against callgrind's own `summary:` line, and that assertion is what caught the `calls=` double count (397 362 327 against 38 765 393) |
| `02-r3-annot.txt` | the shipped R3's `kernel`, every instruction with its execution count — §3.2's block |
| `01-baseline.log` `03-r3-explore.log` `04-r4-explore.log` `05-r4-combo.log` `13-explore2.log` `15-explore3.log` | the exploration, in order |
| `mk4.py` `mkv.py` `mkref.py` | the substitution generators; `mkv.py`'s comment records the ordering trap the hit counts caught |
| `probe_bits.rs` | the bitmask feasibility probe, **run before any twin was written**: 9 verified / 0 errors |
| `probe_ptreq.rs` | §4.2's three `ptr::eq` spellings |
| `06-verus-surface.log` `07-verus-bitmask.log` | the twins' Verus runs |
| `negatives_spellings.py` `11-` `17-` `19-` `21-` `24-` `29-negatives-*.log` | §H; **`11-` is the FIRST run and records two of the three self-catches**, `19-` the third (the sidecar pin firing). `29-` is the run against the shipped tree |
| `10-` `12-` `14-` `16-` `18-` `20-` `23-` `28-spellings-*.log` | the **eight** `spellings.py` regenerations. ⚠ Eight and not one because the sidecar pins `NOTES.md` and pins ITSELF, so **every prose edit and every docstring edit costs a regeneration** — `ph45` §8.1's lesson, learned the same way and twice |
| `22-gate1.log` `25-gate2.log` `26-report.log` `27-gate-final.log` `30-gate-shipped.log` | the gate chain: FAIL (3 tables) → FAIL (1 table) → `report.py` → **PASS** → **PASS** after the docstring fix |
| `chain.sh` `chain2.sh` | the two chains, so the ORDER is reproducible and not remembered |
| `fix_docstring.py` | §6.1's two edits, with a `--check` dry run and both anchors asserted to occur exactly once |
| `pathtest/` | §8's two-directory fingerprint measurement (generator kept, binaries deleted) |
| `cleanup.sh` `NOTES.md` | the artefact deletion, and the index of this directory with the three rebuild commands |

**Committed, and this is where a reader should go:**

| path | |
|---|---|
| `patterns-php/ph53-iface-tail-uninit/controls/spellings.py` `.json` | the search |
| `…/controls/mu_ref.rs` `mu_ref_cmp.rs` `mu_ref_exec.rs` | open item 79 |
| `…/NOTES.md` §8j §8k | the numbers and the mechanisms |
| `…/NOTES.md` §8c §8e §8g §11a §12 | the five corrections, struck in place |
| `results-php/gate/ph53-iface-tail-uninit.json` | the verdict |

---

## §11 ⚠ WHERE MY OWN PRE-REGISTERED EXPECTATIONS WERE WRONG

`.temp/php42/00-EXPECTATIONS.md`, unedited:

1. ⛔ **I predicted the bitmask witness would be a TIE or DEARER** — *"§8e
   measured that the witness cost is lost vectorisation, not the byte, and a
   bitmask keeps the data-dependent branch. I expect the named candidate to
   FAIL, and that is a result."* **It is −11.40 %, the R4 winner, and the reason
   I gave was `NOTES.md`'s refuted mechanism.** ▶ **I inherited a claim instead
   of measuring it, and it is the single largest miss in this task.**
2. ⛔ **I predicted the R3 term would be the POOL check and the margin
   single-digit.** The pool check is 33.80 Ir/call (2.4 %) and the margin is
   **32 %**. I had the right *kind* of term — a bounds check LLVM could not
   eliminate — and the wrong one, and I found the real one only by taking the
   instruction-level profile. ✅ **The profile is what my expectations file said
   I would do and it is why the miss was cheap.**
3. ⛔ **I predicted `r4_win_checked`-with-the-sub-slice (`r4_win_oprec`) would
   lean DEARER and was "genuinely unsure".** It is +2.99 %, so the direction was
   right by luck; `ph45`'s winner shape (a checked read of a hoisted slice) does
   NOT transfer, because here the window was already hoisted.
4. ✅ **Right**: `r3_slice_param` a TIE; `r4_pool_checked` dearer;
   `r4_set_checked` nearly free; `ptr::eq` the blocker on item 79; that a search
   would move something on this row; and *"I expect to find at least one defect
   in code I write this task; if I find none I should suspect the suite"* —
   **three found by a negative, all in this task's code, plus a fourth in my own
   docstring found by re-reading it** (§6, §6.1).
5. ⚠ **AND ONE PREDICTION I DID NOT MAKE AT ALL, WHICH IS THE MORE USEFUL
   OMISSION.** My expectations file lists the R3 candidates I intended to price
   and **`chunks_exact` is not among them** — I proposed `slots.iter()` for the
   SCAN and never thought of the op-record loop as an iterator. It is the
   cheapest in-contract R3 found. ▶ **The winner on the side I had a mechanism
   for was a spelling I had not listed**, which is the honest measure of how
   complete a spelling search of this kind can claim to be.

---

## §12 SCOPE

⚠ **`RECAP_PHP.md` and `.memory-php/` NOT written.** ⚠ **No `git add`, no
`git commit`**, no history-mutating git command. ⚠ **`.web/` not touched.**
⚠ **No `/tmp` file** — all scratch under `.temp/php42/`. ⚠ Every corpus grep
used `-a`. ⚠ No `pkill`/`killall`; every long run was one tracked background job
under `timeout`.

**Untouched, deliberately:** `harness/`, `common/`, `common-php/`, `patterns/`,
`results/`, `pilot/`, `patterns-php/CATALOGUE.md`,
`patterns-php/MANIFEST.sha256`, every **other** `patterns-php/` row (including
`ph29`'s and `ph16`'s `spellings.py`, §8), and this row's `spec.md` **except one
sentence**, `model.py`, every `.rs` rung, `c/*` and `inputs/*`.

### 12.1 `git status --porcelain` AT THE END, VERBATIM — twelve paths

```
 M patterns-php/ph53-iface-tail-uninit/NOTES.md
 M patterns-php/ph53-iface-tail-uninit/README.md
 M patterns-php/ph53-iface-tail-uninit/spec.md
 M results-php/gate/ph53-iface-tail-uninit.json
 M results-php/preflight/_norow.preflight.json
 M results-php/tables/ph53-iface-tail-uninit.md
?? .tasks-php/TASK_PHP_042_REPORT.md
?? patterns-php/ph53-iface-tail-uninit/controls/mu_ref.rs
?? patterns-php/ph53-iface-tail-uninit/controls/mu_ref_cmp.rs
?? patterns-php/ph53-iface-tail-uninit/controls/mu_ref_exec.rs
?? patterns-php/ph53-iface-tail-uninit/controls/spellings.json
?? patterns-php/ph53-iface-tail-uninit/controls/spellings.py
```

✅ **Three EMPTY guards, run rather than asserted:**

```
git status --porcelain -- harness/ common/ common-php/ patterns/ results/     pilot/ .web/ RECAP_PHP.md .memory-php/ patterns-php/CATALOGUE.md     patterns-php/MANIFEST.sha256 patterns-php/ph0* patterns-php/ph16*     patterns-php/ph29* patterns-php/ph45* patterns-php/ph64*     -> (empty)

git status --porcelain -- <the 7 row paths in the MEASUREMENT digest>  -> (empty)

git diff --stat -- results-php/preflight/ph53-iface-tail-uninit.preflight.json
                                                                     -> (empty)
```

⚠ **`results-php/preflight/_norow.preflight.json` (+lines) is `PROTOCOL_PHP.md`
§E's documented second-order effect and I did not edit it**: every
`gate.py --tool measure --check-stale` and `gate.py --audit` appends a row-less
entry. ⭐ **And the row's OWN preflight moved mid-task and came back**: it grew
during the two FAILING gate rounds (§E's *"a FAILING run grows a COMMITTED
file"*) and is **byte-identical to `HEAD` again** after the passing ones — which
is `ph45` §11's observation on a second row, recorded here so a reader watching
`git status` mid-task does not file it as damage.
`harness-php/gate.py --audit` → **`preflight coverage: complete`**.

✅ **`python3 .tasks-php/citecheck.py` reports NO row-specific `.temp/` citation
for `ph53`** in either `spec.md` or `NOTES.md`. The only two `ph53` lines it
still prints are `hist` entries — `_041`'s report citing `results/…` — and the
three remaining `.temp/` strings in `spec.md` are the PAT-era **inherited**
shared-`why` citations (`.temp/p19/pins.py`, `.temp/p05r3/v16/tuned_split.rs`,
`.temp/p05r3/v17/tuned_suffix.rs`), which are open items 55/61 and a six-row
re-gate, **not this row's debt** and explicitly out of scope by the task file's
§3.
