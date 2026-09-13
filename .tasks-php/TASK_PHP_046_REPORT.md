# TASK_PHP_046 — REPORT (engineer). `ph52`'s BOTH ENDPOINTS, searched.

**Role:** research engineer, one agent alone. **Deliverables:**
`patterns-php/ph52-concat-copy-uninit/controls/spellings.py` + `.json`, and this file.

---

## §0 The answers, before the evidence

| | |
|---|---|
| **R3 endpoint** | ⭐⭐⭐ **MOVES.** `r3_endpoint_degenerate: false`. `r3_chunks_exact` is **`−7.42 %` A1** against the shipped R3 (`1930.232` vs `2085.038` Ir/call, `small.bin`, `O3/isolated`). |
| **R3: spelling or mechanism?** | ⭐⭐⭐ **SPELLING.** The 6.71 % shipped R3−R4 gap is **four per-op window bounds checks** — 8 instructions per op, `128.00` Ir/call predicted statically against a measured gap of `131.19`, i.e. **97.6 %** — and a safe respelling recovers it with **no `unsafe` token and no trusted item**. It is *not* `Option`-vs-`MaybeUninit`+witness, which is what the row's own §8c/§10 imply. |
| **R4 endpoint** | ⛔ **DEGENERATE.** `r4_endpoint_degenerate: true`, **and also `true` with the gate-rule filter removed** — so it is degenerate on **cost**, as `ph07`'s and `ph16`'s are. The best R4 variant found is a **byte-identical tie**. |
| **What the R4 side found instead** | ⭐⭐ **three variants with a SMALLER trusted base, and `harness/check.py` refuses all three** — two by stage 5c-twin's `n_twins == 0` (**F104**), one by `_scan_unsafe_sites` (**F97**). `r4_no_wrapper` is `external_body` **4 → 3** at a **byte-identical `kernel`** and **34 verified / 0 errors**. |
| **Statistic** | **A1** for the search, **W1** quoted labelled beside it. Re-derived, not inherited: `inside_share` measured **98.56–98.68 %** on all 15 Rust cells this pipeline builds, against §8a's **22.24 %** on `c-gcc`. Both are right; `inside_share` is per-**cell**. |
| **Ordering** | ⛔ The `fixed-R4 bound`'s **ordering reverses** under search: R3 `+6.71 %` dearer → cheapest R3 `−1.21 %` against the shipped R4. ⚠ **Ordering, never interval.** |
| **Defects in my own work, found by running things** | **2**, both predicted by the laws I was told to obey as *steps*: an `idiom`-keyed rule that fired on the shipped rung's own spelling (item 100's class) and **F101's path-sensitive digest, producing a false negative and a false positive in one run**. Neither was found by reasoning. §7, §8. |

---

## §1 Brackets

**Opened** (before any edit):

```
python3 harness/measure.py --check-stale                   -> 66 record(s) examined, 0 STALE
python3 harness-php/gate.py --tool measure --check-stale    -> 18 record(s) examined, 0 STALE
```

**Mid-task, after the gate-only edits and before the re-gate** — the expected excursion:

```
python3 harness-php/gate.py --tool measure --check-stale    -> 18 record(s) examined, 1 STALE
STALE  results/gate/ph52-concat-copy-uninit.json   patterns/ph52-concat-copy-uninit/NOTES.md
```

⭐ **The tripwire did not fire.** The one stale record is the **gate** record, named by
`NOTES.md`; `results/ph52-concat-copy-uninit.json` stayed `FRESH` throughout, so **no
measurement record went stale and no re-measure was forced**. Closing readings: §14.

`contract_sha256` **before**: `d73ab3298ecd44f26a3288a500241134eef0ffc1f8dc6363d5f47525a0641fe3`.
`contract_sha256` **after**: see §13 — **unchanged**, because `spec.md` was not touched.

---

## §2 What I changed, and which digest each edit is in

| file | digest | cost |
|---|---|---|
| `patterns-php/ph52-concat-copy-uninit/controls/spellings.py` | **NEW.** `controls/*` → gate-only | one re-gate |
| `patterns-php/ph52-concat-copy-uninit/controls/spellings.json` | **NEW.** `controls/*` → gate-only | (same re-gate) |
| `patterns-php/ph52-concat-copy-uninit/NOTES.md` | gate-only (`source_sha256`) | (same re-gate) |

⛔ **Nothing else.** `spec.md` **not** touched, so `contract_sha256` does not move. No
`.rs` rung, no `c/*`, no `inputs/gen.py` — so **no 32-cell re-measure**, which is what
§5.2 asks to be stated and what the bracket in §1 confirms independently.

⭐ **`idiom.required` / `idiom.forbidden` prose: NOT TOUCHED AT ALL.** §3.1 says to say
so if that is the case. It is. ⚠ **I ran `controls/spellings.py --audit-only` anyway**
— it is the deliverable's own audit — **and reading its output is what found the first
of my two defects** (§7). So the procedural law paid even where its trigger condition
did not hold.

---

## §3 The R3 answer: SPELLING, and here is the disassembly

### 3.1 The shipped gap, and where it lives

`small.bin`, `O3/isolated`, A1 (`kernel_exclusive_ir / n_iters`, `n_iters = 25 000`):

| | A1 Ir/call | `kernel` instructions | **panic call sites** |
|---|---:|---:|---:|
| R3 `safe_tuned` shipped | **2085.038** | 412 | **5** |
| R4 `unsafe` shipped | **1953.850** | 444 | **1** |
| **Δ** | **131.187** | −32 | **+4** |

⭐ **The panic-site column is the whole argument in one number.** Every helper in this
row is `#[inline(always)]` and `kernel` calls nothing else, so a `call` inside `kernel`
can only be a panic path. The shipped R4 has **one** — the `&buf[off..off + len]` range
check. The shipped R3 has **five**: that one, plus **four** for the per-op reads.

The four, in the R3 hot loop, read off `objdump -d`:

```
  inc    %r9
  add    $0x4,%rdi
  cmp    %r12,%r9
  mov    0x98(%rsp),%r12
  jae    <loop exit>
  cmp    %rdi,0xb0(%rsp)       <- win[p]
  je     <panic 1>
  cmp    %rdi,0xa8(%rsp)       <- win[p + 1]
  je     <panic 2>
  cmp    %rdi,0xa0(%rsp)       <- win[p + 2]
  je     <panic 3>
  cmp    %rdi,0x38(%rsp)       <- win[p + 3]
  je     <panic 4>
  movzbl -0x3(%r12,%rdi,1),%r11d
```

LLVM has loop-rotated the four `p + k < win.len()` tests into four **equality** tests
against precomputed limits in stack slots, because `p` advances by a constant 4. That is
**4 × (`cmp` + `je`) = 8 instructions per op**. `small.bin` has stride 74, so
`cap = (74 − 8) / 4 = 16` ops per call, and the static prediction is

```
8 instructions/op × 16 ops/call = 128.00 Ir/call   against a measured gap of 131.187
                                                   = 97.6 % of it
```

⚠ **Magnitude floor with the sign claim** (§5.3): the gap is `131.19` Ir/call on a base
of `1953.85`, i.e. `+6.71 %` — two orders of magnitude above `TIE_PCT = 0.05 %` and not
an outlier test at zero.

### 3.2 The variants, and the winner

| R3 variant | A1 Ir/call | vs shipped R3 | insns | panic sites | note |
|---|---:|---:|---:|---:|---|
| `r3_chunks_exact` | **1930.232** | **−7.42 %** | 388 | **1** | ⭐ the winner |
| `r3_oprec_slice` | 2067.299 | −0.85 % | 372 | 2 | |
| `r3_oprec_array` | 2067.299 | −0.85 % | 372 | 2 | **byte-identical** to `r3_oprec_slice` |
| `r3_both` | 2067.299 | −0.85 % | 372 | 2 | **byte-identical** to `r3_oprec_slice` |
| `v0_shipped` | 2085.038 | — | 412 | 5 | |
| `r3_head_slice` | 2085.038 | +0.00 % | 412 | 5 | **NULL, byte-identical to shipped** |
| `r3_loop_for` | 2085.038 | +0.00 % | 412 | 5 | **NULL** (tie, not byte-identical) |

**The answer to §6.3's question is SPELLING, and three things make it more than a
one-number claim:**

1. ⭐ **`r3_head_slice` is the null that localises it.** It applies the *same* sub-slice
   lever to the two head words (`rd32(win, 0)`, `rd32(win, 4)`) and is
   **byte-identical** to the shipped rung — 412 instructions, 5 panic sites, the same
   digest. LLVM already proves `len >= 8` from `cap = (len − 8) / 4`, so the head reads
   were never checked. **The four surviving checks are the per-op reads and only those.**
2. ⭐ **`r3_both` = `r3_oprec_slice` byte-identically**, so the null is independent of
   the lever rather than merely small.
3. ⭐ **The R4 side mirrors it.** `r4_oprec_checked` puts the same four checks *back*
   into R4 at an unchanged trusted surface: `+7.77 %`, 481 instructions, **5** panic
   sites. And `r4_win_checked` (which additionally makes the head reads checked) is
   **byte-identical to `r4_oprec_checked`** — the R4-side echo of the same null. ▶ **The
   four checks are worth the same in both rungs and in both directions**, which is what
   makes them the row's dominant same-language term rather than an R3 quirk.

⚠ **Why `chunks_exact` beats the sub-slice by 6.6 points** when both collapse the
checks: the sub-slice keeps **one** range check (`p + 4 <= win.len()`, 2 panic sites)
and keeps computing `p = OPS_OFF + OP_BYTES * o`; `chunks_exact` drops to **one** panic
site and walks a cursor, deleting the per-op offset arithmetic as well. So it is two
levers, not one, and the panic-site column separates them.

### 3.3 ⛔ A correction to my own framing, forced by the measurement

I built `ctl_r3_unchecked` — the shipped R3 with `win.get_unchecked` everywhere — and
called it **the ceiling of the R3 search**. **It is not a ceiling.**

```
ctl_r3_unchecked   1946.174 Ir/call A1    −6.66 % vs shipped R3
r3_chunks_exact    1930.232 Ir/call A1    −7.42 % vs shipped R3      ⭐ CHEAPER
```

⭐ **A safe respelling of this row's R3 beats the same rung with every window bounds
check removed by `get_unchecked`**, by `0.82 %`, because `get_unchecked` removes the
checks and leaves the offset arithmetic. That is a stronger statement than the one I set
out to make, and it is in the sidecar as
`ctl_r3_unchecked_is_not_an_upper_bound` with the retraction named. The control is still
the right control — it isolates the bounds-check term *at the shipped spelling*, which
is what makes the 128-of-131 attribution checkable — but it bounds nothing.

### 3.4 The ordering, and the interval I am not computing

| family | `fixed-R4 bound` (R3ship − R4ship) | R3-side span, cheapest .. dearest in contract |
|---|---:|---|
| **A1** | **`+6.71 %`** (2085.0 vs 1953.9) | **`−1.21 % .. +6.71 %`**, `r3_chunks_exact` .. `v0_shipped` |
| **W1** | `+6.62 %` (2113.2 vs 1982.0) | `−1.19 % .. +6.62 %`, `r3_chunks_exact` .. `r3_loop_for` |

⛔ **THE ORDERING REVERSES**: the published bound says R3 is `+6.71 %` *dearer* than
R4; the cheapest in-contract R3 is `−1.21 %` *cheaper* than the shipped R4.
⚠ **Ordering, never interval** — `min(R3 found) − min(R4 found)` differences two upper
bounds and bounds nothing, which `ph03`'s hashed `why` retracts in terms. The file says
so in prose and in the stage-5 output.

---

## §4 The R4 answer: DEGENERATE ON COST, and the TCB axis is where the result is

### 4.1 Six variants priced, every one verified

| R4 variant | A1 Ir/call | vs shipped | `external_body` | twin | identity | gate |
|---|---:|---:|---:|---|---|---|
| `v0_shipped` | 1953.850 | — | 4 | 33 v / 0 e | `norel` | clean |
| `r4_slot_byval` | **1953.850** | **+0.00 %** | 4 | 33 v / 0 e | `norel` | clean |
| `r4_no_wrapper` | **1953.850** | **+0.00 %** | **3** | **34 v / 0 e** | `norel` | ⛔ `5-tcb-unsafe` |
| `r4_win_oprec` | 2033.661 | +4.08 % | **3** | 33 v / 0 e | `norel` | ⛔ `5c-twin` |
| `r4_oprec_checked` | 2105.661 | +7.77 % | 4 | 33 v / 0 e | `norel` | clean |
| `r4_win_checked` | 2105.661 | +7.77 % | **3** | 33 v / 0 e | `norel` | ⛔ `5c-twin` |

**`r4_endpoint_degenerate: true`.** ⭐ **And I recorded the stronger form the task asked
for**: `r4_endpoint_degenerate_ignoring_gate_rules` is **also `true`**, so the verdict
does not depend on my gate-rule filter. The two cheapest non-shipped R4 variants are
**byte-identical ties**, not wins.

⚠ **`r4_slot_byval` is the R4-side calibration null and it is byte-identical** to the
shipped rung: `*m.assume_init_ref()` on a reference and `m.assume_init()` on a copy
compile to the same `kernel`. A search whose every entry moves is a search nobody can
calibrate; this row has three such nulls (`r3_head_slice`, `r3_loop_for`,
`r4_slot_byval`), two of them byte-identical.

### 4.2 ⭐⭐ `r4_no_wrapper`: one fewer axiom, zero bytes of difference, refused by a gate rule

The substitution is **one attribute**: `#[verifier::external_body]` comes off
`slot_read_unchecked` in `verus.rs`. Nothing else changes — the name, the signature, the
`requires`, the `ensures` and the body are all unchanged, and the **exec** source is
`unsafe.rs` byte for byte.

* Verus then **checks** the body against the pinned vstd's own
  `assume_specification` for `MaybeUninit::assume_init_ref`
  (`~/tools/verus/vstd/std_specs/maybe_uninit.rs:45-49`) instead of trusting it:
  **34 verified / 0 errors**, one *more* than the shipped twin's 33, because the body
  became an obligation.
* `external_body` items **4 → 3**; `harness/check.py::_is_trusted`'s count **2 → 1**.
* `kernel` is **byte-identical** to the shipped rung's (same 444 instructions, same
  digest `2f8fbf60a9eb`), and A1 is equal to the digit.
* ⛔ **`harness/check.py::_scan_unsafe_sites` refuses it**, because the `unsafe` token
  now sits in a body the gate does not treat as trusted. **There is no hatch.**

▶ **So the cheapest way to shrink this row's trusted base is free, verifiable, and
unshippable.** §11d and §11f argued F97's collision from the shipped configuration;
this prices it as a rung candidate, which is the stronger object.

### 4.3 ⛔⛔ And F104, measured on a variant rather than argued

`r4_win_checked` and `r4_win_oprec` delete `win_get_unchecked` — the row's **only
twinnable** trusted item. What remains trusted is `slot_read_unchecked`, which
`spec.md`'s `verus.twin_justifications` excuses, so:

```
trusted = ['slot_read_unchecked']   twins = []   n_twins = 0
-> check.py::check_trusted_twins hard-fails: "every trusted item in this pattern
   is excused by verus.twin_justifications, so stage 5c-twin checked the strength
   of NOTHING."
```

That is **F104 exactly**: the rule refuses the configuration whose trusted base is
*smallest*. It is computed here with the gate's **own** `_is_trusted`, `vparse.parse`,
`vparse.blank_noncode` and `_UNSAFE_RE`, imported — not predicted.

⛔⛔ **I did not touch `harness/check.py`** (item 105 prices that and it is the
manager's call), **and I did not add a twinnable trusted item to make any stage
happier.** Every R4 variant here *reduces* the surface. The measured answer is that the
gate refuses all three, and the one that costs nothing is refused by the other stage.

### 4.4 The one R4 lever I did **not** build, with its ceiling

`ph53`'s `u32`-bitmask witness bought **`−11.40 %` A1**. It cannot repeat here, and the
bound is free from the row's own numbers rather than from a variant:

* `ph53`'s witness is an **array** — `[bool; MAXD]`, one byte per slot, re-read on every
  consumer iteration.
* `ph52`'s is **two `bool`s for the whole kernel**, and §8g prices the **entire**
  witness at **`+0.622 %` W1** against `controls/r4_nowitness.rs` (**reproduced in this
  pipeline at `+0.621 %`**, a 0.001 pp agreement across two instruments).
* ▶ A perfectly *free* witness representation could therefore buy **at most 0.62 %**.

⚠ **`UNTESTED`.** That is a ceiling derived from the row's own measurement, not a
measurement of a bit-packed variant. I judged the Verus proof work (the ghost `Sl`
state, the loop invariants and `s_dtor`'s contract all thread `*constructed`) not worth
a ceiling of 0.62 %, and I am stating the judgement rather than implying coverage.
It is also §11c's two-row law holding in a second way.

---

## §5 §2's statistic decision, confirmed by my own measurement

⚠ I verified both of the manager's figures from the record before relying on them, as
§2 requires.

| source | figure | verified |
|---|---|---|
| `results-php/ph52-concat-copy-uninit.json`, `O3/isolated`, `small.bin` | `safe_tuned` A1 **52 125 944**, `unsafe` A1 **48 846 257** | ✅ read directly; `52 125 944 / 48 846 257 = +6.714 %` |
| `NOTES.md` §8d | `unsafe` W1 **49 549 469** | ✅ reproduced at `1981.9923` Ir/call vs §8d's `1981.9788`, **0.0007 %** apart |
| `NOTES.md` §8c | `safe_tuned` W1 **52 829 203** | ✅ reproduced at `2113.1818` vs `2113.1681`, **0.0006 %** apart |
| Rust-cell `inside_share` | **≈98.6 %** | ✅ `48 846 257 / 49 549 469 = 98.58 %`; and recomputed per cell in-pipeline: **98.5633 % .. 98.6813 % over all 15 Rust cells** |
| C-cell `inside_share` (§8a) | **22.24 %** | ✅ `32 509 505 / 146 152 976 = 22.24 %` from §8a's own table |

**Decision confirmed: A1 for the search, W1 for the row, both right.** `spellings.py`
stage 2b recomputes `inside_share` on every run and raises a `problems` entry if any
Rust cell falls below 50 %, so the choice is re-derived rather than inherited.

⭐ **A1 reproduced the shipped record to `0.0000 %` in all four cells** (both rungs ×
both inputs), where W1 reproduced to `0.0006–0.0007 %`. That is
`.memory-php/03-numbers.md` item 99's *A is reproducible and the whole-program column
is not*, seen again: the W1 residual is the argv/env term, which is also §8d's `+40 Ir`
between R4 and R5.

### 5.1 Spreads, and the `in_contract` filter question — answered explicitly, both ways

⚠ §4.2 requires this to be explicit either way. **`a1_spread_pp` applies NO filter** —
no `in_contract`, no `english_verdict`, no `gate_refusals` — which is what `ph45`'s and
`ph53`'s copies do (`TASK_PHP_044` §3.4 established that `ph53` does **not** filter,
against `_043`'s assumption) and therefore the only figure comparable with theirs.
**I also publish the filtered twin**, so no reader has to assume:

| | R3 | R4 |
|---|---:|---:|
| `a1_spread_pp` (unfiltered) | **7.923098** | **7.769824** |
| `a1_spread_pp_admissible` (filtered) | **7.923098** | **7.769824** |
| `wp_spread_pp` | 7.810729 | 7.659630 |
| `wp_spread_pp_admissible` | 7.810729 | 7.659630 |

⭐ **On this row the filter makes no difference to the digit, and that is itself
informative**: the gate-refused R4 variants span the same range as the admissible ones
(`r4_win_checked`, refused, and `r4_oprec_checked`, clean, are byte-identical at
`+7.77 %`). So the live question `_043` got wrong cannot bite here — but the answer is
recorded as a field rather than as a reader's inference.

⚠ **And the spread is a fact about this row's variants, not about family A** (item 82).
`ph45`'s A1 spread is `0.000000` pp; `ph53`'s is `39.9/45.3`; ph52's is `7.9/7.8`. Three
rows, three answers, and the difference is `inside_share`. **I am not quoting any of
them as evidence about the statistic.**

---

## §6 §H — the negatives are INSIDE the validator, and the case count

⛔ §3.2 is a step, not a sentence. **`controls/spellings.py` ships with three
batteries as module functions, all three run on every invocation including
`--audit-only`, and all three feed `problems`** — which
`harness/check.py::control_json_verdict` turns into `FRESH+VERDICT-FAILED` at gate stage
9b. **Nothing is cited in `.temp/`.**

| battery | arms | must-FIRE | must-NOT-fire | what it attacks |
|---|---:|---:|---:|---|
| `english_verdict_selftest()` | **10** | 4 | 6 | the item-83 exclusion path, over synthetic `rows` |
| `gate_rule_selftest()` | **8** | 4 | 4 | `gate_refusals()`, over synthetic **Verus source text** |
| `checksum_selftest()` | **6** | 3 | 3 | `checksum_problems()`, over synthetic answer maps |
| **total** | **24** | **11** | **13** | |

**Case count: 24 arms, 11 must-fire, 13 must-NOT-fire**, plus the consistency check on
the real rows (`english_verdict_problems`) and five runtime invariants that append to
`problems` (a `required[7]` checksum divergence, an `unsafe` token in an R3 variant, an
`inside_share` below 50 %, a stale-vs-record A1/W1 delta above 0.5 %, and the
equal-length-path invariant of §8).

Three arms are worth naming because they exist *because* something went wrong:

* **`E8` (must-NOT-fire)** — a variant that misses a *different* backticked span of the
  *same* `required` entry is **not** a violation. This is my first defect (§7) turned
  into a regression case: it fails if the rule is ever re-keyed on the entry index.
* **`G4` (must-FIRE)** — a Verus source `vparse` cannot parse must **refuse**, not
  return `[]`. `[]` reads exactly like *admissible*, which is the silent-pass shape the
  whole file is written against.
* **`C2` (must-FIRE)** — a **declared** divergence that *fails to happen* is a problem.
  `controls/r4_nowitness.rs` must disagree with the shipped rung on
  `inputs/adversarial-dblfree.bin`, because it **is** `zend.c:243` with nothing between;
  if it ever quietly started agreeing, `witness_cost_pct_w1` would become a comparison
  of one program with itself and a one-directional check would print `ok`.
  ⛔ **I did not take the easy route** of `if side == "CTL": continue` — that exempts
  the whole class to excuse one cell, and a control that started answering differently
  on a *benign* input would then read as expected.

✅ **`python3 .tasks-php/citecheck.py`**: `unresolved in a LIVE doc: 0`; the §H-at-risk
list is **still the same 13 citations across the same 4 rows** (`ph16`, `ph29`, `ph45`,
`ph53`) and the `controls/*` `.temp/` total is **still 31** — **`ph52` contributes
none**, which is what §3.2 asks. The one `ROT` this task opened with
(`TASK_PHP_046.md` citing a `controls/spellings.py` that did not exist) is resolved by
the file existing.

---

## §7 ⛔ DEFECT 1 IN MY OWN WORK — found by running `--audit-only`, not by reasoning

**The first draft of `english_verdict_problems` keyed on the `required` ENTRY.** It
reported, on the real rows:

```
*** R4 r4_no_wrapper     records `required[0]` in required_absent and carries NO english_verdict ...
*** R4 r4_oprec_checked  ...
*** R4 r4_slot_byval     ...
*** R4 r4_win_checked    ...
*** R4 r4_win_oprec      ...
```

**Five of six R4 variants, including ones that change nothing about the witness.** The
cause: `idiom.required[0].rust`'s pin is `` `*constructed = true;` ``, but the entry
*also* contains `` `Option` `` — quoted only to say that *"safe_naive.rs's ordering pin
is the `Option`'s own discriminant"*. Under
`harness/check.py::spelling_matches` that incidental backtick is a declared spelling
matched against **every** Rust rung, so **every unsafe rung records
`required[0] `Option`` in `required_absent` by design, the shipped R4 included** — and
an entry-indexed rule reads the entry's own English as a violation of itself.

**Repair:** `WITNESS_PIN` is now a **triple** — `("required[0]", "*constructed = true;",
"R4")` — and the rule keys on the **span**. Arm `E8` is the must-NOT-fire that pins it.

⭐ **This is item 100's class on a third row**, and it is the exact thing
`.memory-php/02-ladder.md`'s backtick law exists to catch: *a backtick in a `required`
entry IS a pin, including around a type name.* I was not touching `idiom` prose at all,
so the law's trigger condition did not apply to me — **and running the audit anyway is
what found it.** ⚠ It also means the law has a second, weaker corollary worth
recording: **a validator that READS `idiom` inherits every incidental backtick in it**,
so the law binds readers of that prose and not only its authors.

ⓘ **`ENGLISH_VERDICTS` is therefore EMPTY on this row, and that is a result rather than
an oversight.** No variant here drops a backticked `required` span: `r4_no_wrapper`
keeps the name `slot_read_unchecked`, every R4 variant keeps `*constructed = true;`,
every variant keeps `al.free(p.req)` and `if p.req != 0`, and the two `CTL` variants
carry their verdicts inline in their own declarations. ⛔ **And it is not empty because
emptying it helped**: nothing excluded by English would have moved either endpoint —
the R3 winner satisfies every `required` span its shipped rung does, and the R4 endpoint
is degenerate on cost *before* any English is applied. (`.memory-php/02-ladder.md`: a
pin ruling is only credible when it can cost the row something. On `ph53` it did; here
there is nothing for it to cost.)

---

## §8 ⛔⛔ DEFECT 2 — **F101 fired live, in both directions, in a fresh copy of the machinery**

`RECAP_PHP.md` **F101** records that `kernel_fingerprint`'s digest is **path-sensitive**
— `rustc` embeds the source path in panic-location data, a longer path moves everything
after it, and the function deliberately keeps the rip-relative displacements that move.
F101 was narrowed to *"on `ph29` that is a live false negative"*, 1 of 3 spellings
measured, with `ph29` out of scope for repair.

**It fired here, on a row nobody had looked at, and in BOTH directions in the same
run.** With the obvious scratch naming (`R4_<name>.rs`):

| | measured | truth |
|---|---|---|
| ⛔ **FALSE NEGATIVE** | `r4_no_wrapper` digest `0a7bd074f8b6` vs `v0_shipped`'s `2f8fbf60a9eb` | `r4_no_wrapper`'s exec source **is** `unsafe.rs` byte for byte — its `rs` substitution list is empty |
| ⛔ **FALSE POSITIVE** | `r4_slot_byval` and `r4_no_wrapper` **shared** a digest | two genuinely different sources; `R4_r4_slot_byval.rs` and `R4_r4_no_wrapper.rs` are merely the **same length** |
| ⛔ **FALSE NEGATIVE** | `r3_head_slice` digest `a4a8b847bab1` vs shipped `4664d8975683` | byte-identical — which is the **stronger** form of the null in §3.2 |

**A false positive is the bad direction**: a function whose whole job is to say
*byte-identical* reported two different programs identical. ⚠ **And F101's published
narrowing — *"1 of 3 spellings measured"* — understates it: here it hit 3 of the 6 pairs
I compare.**

**Repair, inside the row, no `harness/` edit:** every scratch source is named with a
**fixed-width slug** `vNN.rs`, so every exec source path has the same length and the
term cannot vary. `main` **asserts** the invariant rather than trusting the convention:

```
exec source paths: 1 distinct length(s) [62] -- must be 1, or kernel_digest is
path-sensitive (F101)
```

and appends to `problems` if it is ever more than one. The exec-vs-**twin** question —
the one where the paths legitimately differ — is answered by
`harness/asm.py::identity_level` at **`norel`** instead, which masks exactly those
fields; `asm.py` is **imported**, so that is the gate's own definition and not a
re-implementation of it.

**After the repair, all six byte-identity claims are true and three of them changed:**

```
r3_oprec_array  == r3_oprec_slice     true     (ph45 §5.6 on a third row, byte-identically)
r3_head_slice   == v0_shipped   (R3)  true  <- was FALSE
r3_both         == r3_oprec_slice     true  <- was FALSE
r4_slot_byval   == v0_shipped   (R4)  true  <- was FALSE
r4_no_wrapper   == v0_shipped   (R4)  true  <- was FALSE (and was falsely == r4_slot_byval)
r4_win_checked  == r4_oprec_checked   true
```

▶ **Routing note for the manager, not acted on:** F101's repair is *reported for
routing* on `ph29`/`ph16`/`ph45`/`ph53` and those rows are out of this task's scope
(items 57/63). What this adds is that **the defect is not `ph29`-specific and its
direction is not only "false negative"** — a fresh clone produced a false *positive*
within one run. The fixed-width slug is a ~6-line fix that removes the question rather
than managing it, and it is now on file in `ph52`'s copy for the next row to clone.

---

## §9 ⚠ The `identity` bar: `norel` is not `exact`, and I did not treat it as either extreme

§1's ruling says an R4 candidate needs `norel` equality with its twin at `O3`, **not**
byte identity, and to read `check.py`'s own definition first. I did:

* `harness/asm.py::identity_level`'s docstring — `exact` = declared extents
  byte-identical; **`norel` = byte-identical once pc-relative displacement fields are
  zeroed**; `counts` = counts agree, bytes do not; `differ` = not even that. Ordered
  `IDENTITY_LEVELS = ["differ", "counts", "norel", "exact"]`.
* `identity_premise()` reads the **pin** (`spec.md`: `O0 differ` / `O3 norel`) **and the
  record** (`results-php/gate/...json`: `O0 differ` / `O3 norel`). It reads the record
  as well as the prose because F82's negative N6 found `p25` carrying
  `identity: unsafe == verus, O3 exact` as shared-block **boilerplate** while its real
  pin is `norel`.
* `admissibility()` returns the level *this row pins and measures*, and
  `meets_level()` compares by index in `asm.py`'s own ordering. So the bar tightens or
  loosens with the pin instead of being hard-coded — `ph29`'s copy hard-codes
  *"`exact`, so a twin must be byte-identical"*, which on this row would have been
  wrong in one direction and on a re-pinned row wrong in the other.
* **All six R4 twins reach `norel`**, and `v0_shipped`'s reaching it is asserted (a
  bar the shipped rung does not meet would be this file's defect, not the candidates').
  `None` is **false**, not "not applicable".

---

## §10 Item 104 — ⛔ THE PREMISE IS FALSE: the four `build.py` citations have **not** rotted

§4.1 asks whether my work forces a re-measure and, if so, to repair item 104's citations
in the same run. **It does not force one** (§1, §2) — so the answer would be *"leave
them and say so"*. ⚠ **But checking them found that there is nothing to repair.**

Item 104 says *"Four citations of `harness/build.py` line numbers have drifted"*. The
four are in `results-php/gate/ph52-concat-copy-uninit.json`'s `doc_citations.other`.
I resolved each against `harness/build.py` as it stands today:

| citation | cited by | `harness/build.py` at that line | verdict |
|---|---|---|---|
| `build.py:163-165` *"compiles EXACTLY THREE translation units"* | `c/emalloc_shim.h:117` | 163-165 are the three `srcs = [driver.c, kernel.c, main.c]` entries | ✅ **correct** |
| `build.py:167` *"`-I common-php` is already on the compile line"* | `c/emalloc_shim.h:133` | 167 is the `["-I", COMMON, "-I", <row>/c] + srcs + ["-o", out]` line | ✅ **correct** |
| `build.py:168-171` *"INSERTS `-fuse-ld=lld` for every clang whole-mode cell"* | `c/emalloc_shim.h:492` | 168-171 are exactly `if mode == "whole" and "clang" in …: lld = …; if os.path.exists(lld): cmd.insert(1, "-fuse-ld=lld")` | ✅ **correct** |
| `build.py:168-171` (same claim) | `controls/d0_stack.py:73` | same | ✅ **correct** |

**And the mechanism that made them look rotted:** `check_doc_citations` splits hits into
`fatal` and `other` on **one criterion only** —
`CITE_FATAL_MODULE = "check.py"` (`harness/check.py:1006`, and
`citation_verdict` at `:1074-1081`). `other` means *"a line citation of a harness module
that is not `check.py`"*. ⛔ **It is not a claim that the citation is wrong, and nothing
in the gate resolves these citations at all.**

**What is true, and it is still worth something:**

1. The four are in the class the gate flags as an **aging-pointer risk**, which is
   item 98's general repair (*a file in the measurement digest carries no pointer that
   can age — cite a symbol name, not a line number*). They have not aged **yet**.
2. ⚠⚠ **Three of the four are NOT `ph52`'s to repair.** `c/emalloc_shim.h` is a
   **symlink** to `common-php/emalloc_shim.h`, which every php row carries
   unconditionally (§B2). So repairing those three pointers stales **all nine php
   measurement records**, not one — a 9-row re-measure, not a 32-cell one. Item 104's
   *"free the moment item 102's endpoint search forces a re-measure on this row"* is
   therefore wrong twice over: this search forces no re-measure, and three quarters of
   the debt is not this row's.
3. The fourth (`controls/d0_stack.py:73`) **is** gate-only and would have been free to
   repair in this run. ⛔ **I did not repair it**, because it is correct, and rewriting
   a correct citation into a symbol reference is a change to a file in the **gate**
   digest whose only effect is stylistic — and `CLAUDE.md`'s rule about hash-pinned
   pointers is that you do not pay a gate for a pointer. ▶ **Recommendation: reclassify
   item 104 from *"four rotted citations"* to *"four line citations in the
   aging-pointer class, three of them in the shared allocator header"*, and fold it into
   item 98's policy decision.** I have not edited `RECAP_PHP.md`.

---

## §11 What the search says about the row's own published claims

| claim | status |
|---|---|
| `NOTES.md` §8c: the R2→R3 saving is *"the four things R3 removes"* | **untouched** — that is an R2-vs-R3 column and this search does not price R2 |
| `NOTES.md` §10: R3-vs-R4 is `Option` vs `MaybeUninit`+witness | ⚠ **incomplete as an account of the COST.** The representations differ as §10 says, but **97.6 % of the 6.71 % gap is four bounds checks**, and a safe respelling removes it without changing the representation at all |
| `NOTES.md` §8f: the `win_get_unchecked` repair was worth `−7.12 %` W1 | ✅ **reproduced in reverse**: `r4_win_checked` is `+7.66 %` W1 / `+7.77 %` A1. §8f's `−7.12 %` is against the *pre-repair* base, so `+7.66 %` against the post-repair base is the same difference divided by a smaller denominator — arithmetically consistent |
| `NOTES.md` §8g: the witness costs `+0.622 %` W1 | ✅ **reproduced at `+0.621 %`** in one pipeline, 0.001 pp apart |
| `NOTES.md` §9: *"this row ships no respelling search … the largest single gap"* | ✅ **closed**, and §9/§13.1 corrected in place (§12) |
| `NOTES.md` §9: the row publishes in **W1** | ✅ **still right**, and now explicitly beside *"the search publishes in A1"*, with `inside_share` recomputed per cell to show why both hold |
| `NOTES.md` §11f: the `n_twins == 0` rule *"puts pressure on a row to ENLARGE its trusted base"*, **latent rather than live** | ⚠ **now measured on candidates, and still latent only because the row declined the pressure.** Two of the three smaller-surface variants are refused by that rule and the third by `_scan_unsafe_sites` |
| `NOTES.md` §13.2: the witness law rests on n = 2 | ✅ unchanged; this search adds a **ceiling** (§4.4) and no third point |

---

## §12 The `NOTES.md` edits

Two committed statements became false when `controls/spellings.py` landed, so I
corrected them rather than leaving the row asserting its own absence:

1. **§9** — the paragraph *"AND THIS ROW SHIPS NO RESPELLING SEARCH AT ALL …
   `controls/spellings.py` DOES NOT EXIST IN THIS ROW"* is replaced by a new **§9a**
   carrying the result: the two endpoint verdicts, the spreads, the ordering reversal,
   the bounds-check mechanism, the three gate-refused smaller-surface variants, and the
   un-built lever's ceiling. The replaced sentence is **quoted in §9a's own
   block-quote**, so a reader of the diff sees what was retracted.
2. **§13.1** — *"THIS ROW SHIPS NO RESPELLING SEARCH … the largest single gap in the
   row"* becomes **closed**, with open item 81's prediction (*a new suite would find a
   further shared defect*) recorded as **UPHELD twice**, and the half this search does
   **not** reach left open: **the two C rungs' spellings are still unsearched**, so how
   much of §8b's `−0.342 %` survives a search remains `UNTESTED`.

⚠ Both are in the **gate** digest only. `spec.md` is untouched.

---

## §13 Gate, as fields

One re-gate, **green on the first run** — no `gate → report → gate` chain was needed,
because `spec.md` did not move, so the published table still cites this run's
`contract_sha256` and renders byte-identically.

```
python3 harness-php/gate.py ph52-concat-copy-uninit        -> exit 0
check.py: PASS-WITH-BLOCKED-ROWS
```

From `results-php/gate/ph52-concat-copy-uninit.json`, **as fields**:

| field | value |
|---|---|
| `verdict` | `"PASS-WITH-BLOCKED-ROWS"` |
| `failures` | `[]` |
| `complete_run` | `true` |
| `contract_sha256` | `"d73ab3298ecd44f26a3288a500241134eef0ffc1f8dc6363d5f47525a0641fe3"` — **unchanged**, before and after |
| `controls_json` | `{"spellings.json": "FRESH"}` ◀ **was `{}`; this is item 102's other half** |
| `identity[0]` | `pair "unsafe vs verus"`, `opt "O0"`, `level "differ"`, `expected "differ"`, counts `[773, 773, 4458]` / `[770, 770, 4441]` |
| `identity[1]` | `pair "unsafe vs verus"`, `opt "O3"`, `level "norel"`, `expected "norel"`, counts `[433, 425, 1685]` / `[433, 425, 1685]` |
| `blocked` | 1 entry — `verus.rs slot_read_unchecked (strength unchecked)`, unchanged, the row's pre-existing F97 block |
| `loud` | 4 |
| `idiom_audit.forbidden_hits` | `0` |
| `idiom_audit.required_pins_nothing` | `25` |
| `table_render.verdict` | `FRESH` — `render_sha256 == published_sha256 == 5103c9b27251…` |

⭐ **And the gate record independently corroborates §7's defect.** Its own
`idiom_audit.absent` contains

```
{"entry": "required[0]", "lang": "rust", "spelling": "Option", "rung": "unsafe.rs"}
{"entry": "required[0]", "lang": "rust", "spelling": "Option", "rung": "verus.rs"}
```

— i.e. **the gate itself records that the two shipped unsafe rungs miss
`required[0]`'s `Option` span**. My first draft's entry-indexed rule was reading exactly
these two rows of the gate's own output as a violation. The repair is keyed on the span,
and these two entries are now correctly ignored by it.

⛔ Fields named from **`controls/spellings.json`** and not from the gate record, per
§5.4: `verus_checked` (`true`), `problems` (`[]`), `r3_endpoint_degenerate` (`false`),
`r4_endpoint_degenerate` (`true`),
`r4_endpoint_degenerate_ignoring_gate_rules` (`true`), `a1_spread_pp`,
`wp_spread_pp`, `inside_share_pct_by_cell`, `byte_identical_pairs`,
`r3_gap_mechanism`, `witness_cost_pct_w1`, `gate_refusals` (per variant).
The twin verdicts **33 / 34 verified, 0 errors** are in
`spellings.json`'s `variants[].verus_msg` — `verus_checked` is a bare `true` and not a
count, which is item 84's lesson applied rather than restated.

---

## §14 Brackets, closed

```
python3 harness/measure.py --check-stale                   -> 66 record(s) examined, 0 STALE
python3 harness-php/gate.py --tool measure --check-stale    -> 18 record(s) examined, 0 STALE
```

✅ **`66/0` never moved** — the PAT side is untouched. ✅ **`18/0` → `18/1` → `18/0`**, the
excursion §5 calls expected, and the one stale record was the **gate** record named by
`NOTES.md`. ⭐ **No measurement record went stale at any point**, so the real tripwire
did not fire and no re-measure was forced.

`python3 .tasks-php/citecheck.py`: `unresolved in a LIVE doc: 0`; §H-at-risk **13
citations across 4 rows** (`ph16`, `ph29`, `ph45`, `ph53`) — **unchanged, `ph52`
contributes none**; `.temp/` citations in committed `controls/*` **31 across 12 files**
— unchanged.

⚠ `results-php/preflight/_norow.preflight.json` did **not** move, which is item 103's
de-duplication working: the closing bracket's run was content-identical to an existing
entry. `git status --short` at the end of the task:

```
 M patterns-php/ph52-concat-copy-uninit/NOTES.md
 M results-php/gate/ph52-concat-copy-uninit.json
?? .tasks-php/TASK_PHP_046_REPORT.md
?? patterns-php/ph52-concat-copy-uninit/controls/spellings.json
?? patterns-php/ph52-concat-copy-uninit/controls/spellings.py
```

**Nothing outside `patterns-php/ph52-concat-copy-uninit/`, `results-php/gate/` and
`.tasks-php/`.** No `git add`, no `git commit`.

### 14.1 Scratch

`.temp/php46/` (gitignored), **1.3 MB after cleanup**. Binaries, `.o` and callgrind
outputs deleted once the gates were green; what is kept is the evidence and the
generators that rebuild it:

* `probe/disasm_shipped.py` — builds the two shipped rungs and counts `kernel`
  instructions and panic call sites. **Regenerates `R3.asm` / `R4.asm`**, which are §3.1's
  disassembly evidence and are kept as `R3-shipped-kernel.asm` / `R4-shipped-kernel.asm`.
* `probe/proto.py`, `probe/proto4.py` — the substitution prototypes (R3 and R4),
  which established that every variant builds, answers identically and verifies, before
  `controls/spellings.py` was written.
* `probe/gatecheck.py` — the first measurement of the two gate refusals, using
  `check.py::_is_trusted` and `vparse`. ⭐ **Superseded on purpose**: it is now
  `controls/spellings.py::gate_refusals`, **committed**, with 8 §H arms, so this probe is
  history and not the evidence.
* `audit-only.log`, `full.log` … `full4.log`, `gate1.log` — the runs, including the two
  that **failed** and found my defects.
* `spellings/v*.rs` — the 15 materialised variant sources from the final run;
  rebuildable by `controls/spellings.py`.

⛔ **No committed file cites any of these paths**, which is §3.2's whole point.

---

## §15 ⚠ WHAT I AM UNSURE OF

1. ⚠⚠ **The R4 search is the weaker half and I want to say so first.** Six variants is
   not many, and five of them are *reductions* — the space of R4 spellings that might be
   **cheaper** is the one I found least to try in. `unsafe.rs`'s `kernel` already carries
   no per-op bounds check, the witness is 0.62 %, and the slot read is one instruction
   after inlining, so I believe the endpoint is genuinely degenerate — but
   ⛔ **"searched" is not "exhausted"** and `r4_endpoint_degenerate: true` is a statement
   about 6 variants, not about R4.
2. ⚠ **`Pr { req: usize, len: usize }` → `{ req: u32, len: u32 }` is an unexplored
   cheaper candidate.** It halves `MaybeUninit<Pr>` from 16 bytes to 8, and both fields
   are bounded by 31. I did not build it because `required[3].rust` backticks
   `al.free(p.req)` and `if p.req != 0`, so keeping the pin would force
   `Alloc::free(u32)` while `alloc` stays `usize` — a change to the shared allocator
   simulation that risks moving the tally, i.e. the checksum. **Not built, declared.**
3. ⚠ **I did not search the C rungs at all.** `spellings.py` derives every variant from
   `safe_tuned.rs` or `unsafe.rs`. The row's *headline* (§8b, R1h vs R1 at `−0.3497 %` /
   `−0.7532 %`) is a C-vs-C column whose spread over respellings is therefore still
   **UNTESTED**, and it is the column where `inside_share` is **22.24 %** — so a C-side
   search would have to publish in W1, not A1. That is §13.1's surviving half.
4. ⚠ **`gate_refusals()` is two stages, not the gate.** It reproduces
   `_scan_unsafe_sites` and 5c-twin's `n_twins == 0`, chosen because a `spec.md`
   re-declaration cannot move either. It does **not** reproduce the `verus.items` /
   `verus.obligations` pins, the contract-sha stages, stage 3c or Miri — all of which a
   real ship would have to satisfy and some of which a `spec.md` edit *can* move. So
   *"the gate refuses this variant"* is sound; *"the gate accepts that one"* is **not**
   something this file establishes, and it does not claim it.
5. ⚠ **I did not run `controls/negatives.py`.** It is a different control from
   `spellings.py` and nothing I changed touches it, but `RECAP_PHP.md` item 101(b)
   records that `ph53`'s task left the same gap and that declaring it is the right move.
   **`UNTESTED` in this run.**
6. ⚠ **The `chunks_exact` variant removes a panic path the shipped spelling has.**
   `take(n_ops)` cannot run off the end where `win[p]` would panic. I argued it is
   unreachable (`n_ops = rd32(win, 0) % (cap + 1)`, and `chunks_exact` yields exactly
   `cap` chunks) and the six checksums are unchanged — but that is an argument plus six
   blobs, not a proof, and it is the same class of change as `ph53`'s `r3_pool_mask`.
   **A reviewer should check the arithmetic rather than the checksums.**
7. ⚠ **`r3_loop_for` is a tie in Ir but NOT byte-identical** (digest `f8b49fc0ec5a` vs
   `4664d8975683`, same 412 instructions, same 5 panic sites, same A1 to the digit). I
   did not chase what moved. Two nulls, one byte-identical and one not, is better
   calibration than one — but I cannot tell you what the second one re-ordered.
8. ⚠ **`+0.621 %` vs §8g's `+0.622 %` is within the W1 wobble, so the agreement is
   weaker evidence than it looks.** Item 99 measures the whole-program column moving
   ±14–28 Ir between runs, which at 25 000 iterations is ~0.001 Ir/call — the same order
   as the disagreement. ▶ **It is consistency, not independent confirmation.**
9. ⚠ **I have not re-read the row's `spec.md` `verus.items` / `verus.obligations` pins
   against the variants.** A variant that deletes `win_get_unchecked` would also
   contradict those declarations, which is a *second* reason it cannot ship, and I have
   not enumerated which pins each variant breaks. **It does not change any verdict** —
   those variants are already refused — but the sidecar's `gate_refusals` is
   consequently a **lower bound** on the refusals, and says so.
10. ⚠ **Whether `r4_no_wrapper` is *really* a smaller TCB is a judgement, not a
    measurement.** `external_body` goes 4 → 3 and the row stops asserting its own axiom
    — but the obligation moves to the **pinned vstd's** `assume_specification`, which is
    trusted too. My reading is that a shared, pinned, many-eyes vstd specification is a
    smaller marginal trusted base than a row-local axiom, and `.memory/04-verus.md`
    counts `external_body` items, so the count agrees. **A reviewer may disagree, and
    the distinction is not one any number here settles.**
11. ⚠ **`a1_spread_pp` and `a1_spread_pp_admissible` being equal to the digit is a
    coincidence of this row's variant set, not a general fact**, and I am flagging it so
    nobody reads it as *"the filter never matters"*. It holds because
    `r4_win_checked` (refused) and `r4_oprec_checked` (clean) are byte-identical at
    `+7.77 %`, so removing the refused cells does not move either extremum. Add one
    refused variant outside that range and the two fields diverge.
12. ⚠ **I measured `inside_share` only on `small.bin`.** Stage 2b's 98.56–98.68 % is the
    `small.bin` column; `large.bin` is priced in both families for every variant but I did
    not compute the share there. I expect it to be the same to a fraction of a point
    (both families scale together across the two strides in the table) but **I did not
    check, and the statistic decision therefore rests on one input.**

---

## §16 Definition of done, item by item

| § | requirement | status |
|---|---|---|
| 6.1 | `controls/spellings.py` + `.json`, negatives **inside** the validator, case count stated | ✅ 15 variants; **24 arms in 3 batteries, 11 must-fire, 13 must-NOT-fire**, all run on every invocation and feeding `problems`; §6 |
| 6.2 | both endpoints' verdicts, variants priced, winner, degenerate-or-moves recorded explicitly | ✅ `r3_endpoint_degenerate: false`, `r4_endpoint_degenerate: true` (**and `…_ignoring_gate_rules: true`**); §3, §4 |
| 6.3 | **is the 6.7 % R3−R4 gap a SPELLING or a MECHANISM**, with the disassembly | ✅ **SPELLING**, 128.00 of 131.19 Ir/call, with the four `cmp`/`je` pairs quoted and two independent nulls; §3.1–3.2 |
| 6.4 | §2's statistic decision confirmed by my own measurement; `a1_spread_pp` + whole-program spread; `in_contract` filter answered explicitly | ✅ both manager figures re-verified; A1 reproduced the record to `0.0000 %`; spreads published **filtered and unfiltered**; §5 |
| 6.5 | gate green, `contract_sha256` before/after, `verdict`/`failures`/`complete_run`/`identity` **as fields** | ✅ §13 |
| 6.6 | `citecheck.py` clean for `ph52`, **no new §H-subclass citation** | ✅ §14 — 13 unchanged across the same 4 rows, `ph52` contributes none |
| 6.7 | what I am unsure of, in its own section | ✅ §15, **12 items** |
| 6.8 | if a search finds nothing, that is a result; do not manufacture a variant | ✅ **The R4 endpoint IS degenerate and I reported it as such**, with the strongest honest thing beside it — three smaller-surface variants the gate refuses — rather than a manufactured winner. `ph07`/`ph16` precedent |
| §4.1 | item 104: does anything force a re-measure? | ✅ **No.** And checking the four citations found **item 104's premise is false**; §10 |
| §4.2 | item 102's second half: the row's in-contract spread | ✅ delivered; `controls_json` went `{}` → `{"spellings.json": "FRESH"}` |
| §1.1 | ⛔ do **not** add a twinnable trusted item to make a gate stage happier | ✅ none added; every R4 variant **reduces** the surface, §4.2–4.3 |
| scope | no edits outside `patterns-php/ph52-concat-copy-uninit/`; no `harness/check.py`; no `git add`/`commit` | ✅ §14's `git status` |

---

## §17 For the manager — what is routable out of this

1. ⭐⭐ **F-candidate: `ph52`'s R3−R4 gap is a bounds-check spelling, and the safe
   respelling beats the unsafe control.** `r3_chunks_exact` `−7.42 %` A1; the ordering of
   the `fixed-R4 bound` reverses; `ctl_r3_unchecked` at `−6.66 %` is *dearer* than the
   safe winner. ▶ **Endpoint-search score is now 4 of 5 rows properly searched with a
   moving endpoint** (`ph29` R4, `ph45` R4+R3, `ph53` R3, `ph52` R3), against `ph07` and
   `ph16` degenerate.
2. ⭐⭐⭐ **F-candidate: on `ph52` the R4 endpoint is pinned by the HARNESS, not by cost or
   by contract.** Three variants shrink the trusted base; `check.py` refuses all three,
   two by F104's rule and one by F97's. `r4_no_wrapper` is **one fewer axiom at a
   byte-identical `kernel` with 34 verified / 0 errors**. ▶ **This is the first time
   either F97 or F104 has been measured on a RUNG CANDIDATE rather than on the shipped
   configuration**, and it sharpens item 105: option (c) — *leave it* — costs this row a
   free TCB reduction that verifies.
3. ⛔ **Item 104 needs reclassifying, not repairing.** All four `build.py` citations
   resolve correctly today; `doc_citations.other` is *"a line citation of a module other
   than `check.py`"* and never a rot claim. Three of the four are in the **shared**
   `common-php/emalloc_shim.h`, so repairing them is a **9-row** re-measure. §10.
4. ⛔⛔ **F101 is not `ph29`-specific and its direction is not only "false negative".**
   A fresh clone produced **a false positive and two false negatives in one run**, 3 of
   6 compared pairs. The fixed-width-slug repair is ~6 lines and is now on file in
   `ph52`'s copy; the four other rows' copies still carry the defect (items 57/63). §8.
5. ⚠ **A corollary to the backtick law worth adding to `.memory-php/02-ladder.md`:**
   *a validator that READS `idiom` prose inherits every incidental backtick in it*, so
   the law binds readers of that prose and not only its authors. My rule fired on the
   shipped rung's own spelling because `required[0].rust` quotes `` `Option` `` to
   describe a **different** rung. §7.
6. ⓘ **Open, and cheap:** `controls/negatives.py` was not re-run (§15.5) — item 101(b)'s
   exact gap on the next row.
