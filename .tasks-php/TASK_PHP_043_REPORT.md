# TASK_PHP_043_REPORT — THE REVIEW ROUND: rulings on items 83 / 82 / 78, verdicts on F94 / F95 / F92, and a coverage table for F88–F101

**Role:** research **reviewer**, one agent alone. **Scratch:** `.temp/php43/`.
**Nothing edited** under `harness/`, `common/`, `common-php/`, `patterns/`,
`patterns-php/`, `results/`, `results-php/`, `pilot/`, `.web/`, `RECAP_PHP.md`
or `.memory-php/`. No `git add`, no `git commit`, no history-mutating git.

## ⭐ BRACKETS — FIRST

Taken before reading anything else:

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE
$ python3 harness-php/gate.py --tool measure --check-stale
16 record(s) examined, 0 STALE
```

**`66/0` and `16/0`.** Unmoved. Re-quoted at the end of this report.

---

## §0 HEADLINE — WHAT THIS ROUND FOUND

| | |
|---|---|
| **items ruled** | **83 RULED** (reading **(a)**, so **F100's R4 half falls**) · **82 RULED CLOSEABLE WITHOUT A ROW EDIT** · **78 ANSWERED — the missing 2×2 cell was found FREE, and the rival LOSES on it** |
| **verdicts** | **12 of 14 verdicted · 2 UNREVIEWED** (F96, F97). ⚠⚠ **BUT THE DEPTH IS NOT UNIFORM AND THAT IS THE NUMBER THAT MATTERS: 8 got a SECOND METHOD** (F91 F92 F94 F95 F98 F99 F100 F101) and **4 got only §5's deliberately-low bar (i)–(iii)** (F88 F89 F90 F93). **Read §8's table and §6's stop line, not this cell.** Split: **4 UPHELD · 7 UPHELD-NARROWED · 1 REFUTED · 2 UNREVIEWED** |
| ⛔ **retractions owed** | **1** — F100's *"BOTH ENDPOINTS MOVE"* headline loses its R4 half. ⭐ Its R3 half, its `r4_bitmask_min` smaller-surface result and its A1-spread result **all survive the ruling**, and I verified that separately rather than assuming it |
| ⭐ **new defects found** | **9**, none of them in the task file's list: (1) a **FIFTH** shared-`spellings.py` defect — the `invariant` field's opening clause is false as written in **5 of 5 php rows**; (2) **`r3_no_capacity` is out of contract on `required[0]`** under the same ruling and nobody noticed; (3) the manager's own §1 evidence 1 **is an over-read** — reading (a) does not follow from the sentence cited, it follows from a different sentence; (4) **F98's `+21.8 %` is W1-on-`small.bin`-against-a-RUST-control, is stated nowhere as such, and is only ~44 % the witness**; (5) **F94's screen route has been withdrawn by F95 and F94 still cites it**; (6) **`preimage_screen.py::same_function`'s guard accepts a zero-context hunk as proof** (latent, reach 0); (7) **`citecheck.py`'s `inherited` intersection fails SILENT at one row**; (8) **item 81's consequence for `ph29` is backwards in direction**; (9) **F92's *"hopeless"* is false for the absolute 1-pp target — `W ≤ 574`, from the probe's own TABLE 7** |
| ⚠ **manager claims re-derived and CONFIRMED** | F100's six A1 percentages, all to the digit; the item-83 degeneracy premise; F95's `25`; F92's two exponents; F94's two routes |
| ⛔ **STOPPED** | after §5.7. **F96 and F97 are UNREVIEWED** and I say so rather than stretch. Exactly where, and what I would do next: §6 |

---

## §1 ⭐⭐⭐ ITEM 83 — RULING: **READING (a)**. THE PIN BINDS A SPELLING, F100's R4 ENDPOINT IS **DEGENERATE**, AND THE MANAGER'S OWN ROUTE TO THAT ANSWER IS AN OVER-READ

### 1.1 The pin, extracted rather than quoted

`harness/check.py::read_contract('patterns-php/ph53-iface-tail-uninit')` — note
the call takes the **pattern directory**, not `spec.md`; the task file's
spelling `read_contract` applied to a file path raises `NotADirectoryError`.
`idiom.required` has **9 entries**. `required[4]` is a dict with **one key,
`rust`**, and reads (verbatim, whole):

> `` `wrote[i]` `` -- THE ONE-BYTE-PER-SLOT WITNESS, present in unsafe.rs and
> verus.rs and in no other rung. IT IS NOT IN THE C AND IT IS NOT UPSTREAM: it
> is what makes R4's unsafe read dischargeable, and the row's Verus-side result
> is that a faithful witness-free R4 CANNOT BE VERIFIED at all -- coverage is a
> property of the op stream, i.e. of attacker data, and the pinned driver loop
> offers no call site at which to establish it. controls/r4_nowitness.rs is that
> program, measured, run under Miri and put through Verus with its error text.
> It is indexed SAFELY on purpose: reaching a rung's own safety witness with an
> unchecked access would make the witness rest on the thing it exists to
> establish.

**Exactly one backticked span in the entry** — `wrote[i]`. `controls/r4_nowitness.rs`
is deliberately unbackticked, which is `p42-goto-cleanup/required[1]`'s stated
convention (*"quoting a file name or a retracted span would pin it too"*). So
there is no ambiguity about *which* span is the pin.

### 1.2 ⭐⭐ THE RULING, AND IT IS DECIDED BY A SENTENCE THE MANAGER DID NOT CITE

**Reading (a) holds. Reading (b) is REFUTED. Reading (c) is REFUTED AS STATED
and survives only in a narrowed form (§1.7).**

⛔⛔ **But the manager's evidence 1 does NOT establish (a), and I think it is an
over-read.** The task offers the `why`'s *"WHAT NO GREP SETTLES"* sentence —
*"the POLARITY of a quoted span … and the SET OF RUNGS it scopes to live in the
entry's English. `spelling_matches` decides one spelling against one rung;
**which spelling and which rung is a reading**, and no gate stage reproduces
it"* — and infers *"English decides SCOPE, backticks decide SPELLING, therefore
(a)"*. **That inference does not go through**, for two reasons I can show in the
infrastructure's own text:

1. The sentence's own final clause says **"which spelling … is a reading"**. It
   puts *identifying the pinned spelling* on the same footing as identifying the
   rung — i.e. it is the opposite of *"backticks decide spelling"*.
2. ⭐⭐ **`harness/check.py::idiom_audit`'s docstring (`check.py:2198–2212`) is
   far more explicit, and it is the authoritative statement about the `required`
   half.** It says `required` *"has no such scope"*, that `TASK_020` measured
   the naive every-span-in-every-rung reading at **41 misses of 158 obligations,
   all 41 non-defects**, that **17 of the 41 are ANTI-signal** because a
   `required` entry *"may quote a span in order to say it is ABSENT"*, and that
   therefore *"`required` is reported as PRESENCE, in two shapes, and **the
   reader judges against the entry beside it**"*. ▶ **So the mechanical presence
   report is explicitly NOT self-interpreting, and a ruling cannot be read off
   `required_absent`.** The manager's route would license reading (a) on *every*
   backticked `required` span, which `check.py` measured as 41-of-41 wrong.

▶ **Reading (a) is nevertheless right, on two different pieces of text:**

**(i) THE MAIN RULE OF THE NAMED-SPELLING STANDARD**, byte-identical in six
patterns, `sha256 59748cce2db5…` pinned at `check.py:1908`:

> *where a `required` entry quotes an expression in backticks it pins THAT
> SPELLING, not merely the property the expression has, so a rung that
> establishes the same fact by a different expression is out of contract **even
> when it is semantically identical and even when it compiles to the same
> bytes***

A `u32` bitmask is precisely *"establishes the same fact by a different
expression"*. The rule names that case and resolves it against the challenger.
There is no polarity inversion to worry about here: the entry's English is
positive (*"present in unsafe.rs and verus.rs"*), so the anti-signal class
`check.py` warns about does not apply.

**(ii) ⭐⭐⭐ AND THE ENTRY'S OWN ENGLISH DOES NOT SAY WHAT READING (b) NEEDS IT
TO SAY.** This is the finding that actually closes the item, and it refutes the
manager's framing of the whole dispute. F100 and item 83 both say *"its
backticked spelling is `wrote[i]` … its English says … a **purpose**"*. **The
English does not only say a purpose. Its leading appositive — the clause that
defines what the backticked span IS — reads "THE ONE-BYTE-PER-SLOT WITNESS",
which is a REPRESENTATION.** Measured: the shipped witness is
`patterns-php/ph53-iface-tail-uninit/unsafe.rs:230`, `let mut wrote: [bool;
MAXD] = [false; MAXD];` — one `bool`, i.e. **one byte**, per slot. The
challenger is declared in `controls/spellings.py::R4_VARIANTS` as *"a u32
bitmask witness **instead of `[bool; MAXD]`**"* — **one BIT per slot.**

▶ **So the bitmask fails the entry's ENGLISH as well as its backticks.** Reading
(b) — *"the English names a role and the bitmask discharges it"* — is true of
one clause of the English (*"what makes R4's unsafe read dischargeable"*) and
**false of the clause that defines the pinned object**. A second clause,
*"It is **indexed** SAFELY on purpose"*, also fails: a bitmask performs no
indexed access at all. **The entry's English is 2-for-2 against the bitmask on
representation and access shape, and 1-for-1 for it on purpose.** That is not a
spelling-versus-English conflict; **it is a 2-to-1 English verdict that happens
to agree with the backticks.**

⭐ **Consequence for the record: item 83's own one-line summary —
*"PINS A SPELLING AND ARGUES A PURPOSE, AND THE TWO DISAGREE"* — is itself
wrong, and it is the sentence that made this look undecidable for two tasks.
They do not disagree.**

### 1.3 ⛔ THE CONSEQUENCE, SIMULATED THROUGH THE ROW'S OWN VERDICT FUNCTIONS

I did **not** inherit the task file's premise that (a) makes
`r4_endpoint_degenerate` true. Probe: **`.temp/php43/item83_sim.py`**, which
reads the committed `controls/spellings.json`, rebuilds the `rows` dict, flips
`in_contract` on exactly the variants (a) excludes — **computed from
`required_absent`, not hardcoded** — and then calls
`cheaper_than_shipped` / `cheapest_in_contract` / `dearest_in_contract`
**imported from `ph53`'s own `controls/spellings.py`**, so the verdict is
produced by the same code that published `r4_endpoint_degenerate: false`.
It **builds nothing and runs no callgrind**; measurement cost **zero**.

`--selftest` **PASSES**, with four negatives: **N1** the unmodified rows must
reproduce all five committed verdict fields (they do — `r4_endpoint_degenerate
False`, `r3_endpoint_degenerate False`, `cheapest_r3 r3_chunks_mask`,
`cheapest_r4 r4_bitmask`, `dearest_r3 r3_slice_param`); **N2** must-FIRE
(excluding every R4 challenger degenerates the endpoint); **N3** must-NOT-FIRE
(excluding only the dearer `r4_win_checked` does not); **N4** the exclusion set
is exactly `{r4_bitmask, r4_bitmask_min, r4_bitmask_pool}` on the R4 side.

**Result, reading (a) applied with each entry's English scope honoured:**

| | committed (b) | **reading (a)** |
|---|---|---|
| `r4_endpoint_degenerate` | `False` | ⛔ **`True`** |
| `cheapest_r4_in_contract` | `r4_bitmask` | **`v0_shipped`** |
| R4 variants beating shipped | `r4_bitmask`, `r4_bitmask_pool`, `r4_bitmask_min` | ⛔ **none** |
| `r3_endpoint_degenerate` | `False` | ✅ **`False` (unchanged)** |
| `cheapest_r3_in_contract` | `r3_chunks_mask` | ✅ **`r3_chunks_mask`** |
| `dearest_r3_in_contract` | `r3_slice_param` | ✅ **`r3_slice_param`** |

⭐ **And the arithmetic reason it degenerates, which is the thing worth putting
in the record because it means the ruling is not close:** on A1
(`ir_per_call_small`, the row's `headline_statistic`, from
`controls/spellings.json`), R4 shipped is **1116.94724 Ir/call** and **every
single in-contract R4 variant other than the three bitmask ones is DEARER** —
`r4_set_checked` 1122.58 (+0.50 %), `r4_win_oprec` 1150.32 (+2.99 %),
`r4_pool_checked` 1150.75 (+3.03 %), `r4_min_trusted` 1190.69 (+6.60 %),
`r4_win_checked` 1495.79 (+33.92 %). `r4_mu_ref` was already
`in_contract: false`. **So the R4 endpoint does not merely degenerate, it
degenerates with no near miss: the margin to the next candidate is +0.50 %
against a `tie_pct` threshold, in the wrong direction.**

✅ **The task file's premise is therefore CONFIRMED, independently.** ⚠ And it
is the one premise in §1 I would have been most willing to believe without
checking, which is why I checked it.

### 1.4 ⭐⭐ A SECOND INSTANCE NOBODY FLAGGED: `r3_no_capacity` IS OUT OF CONTRACT TOO

Ruling (a) does not apply only to `required[4]`. Running it over **every**
`required` entry, with each entry's English scope transcribed from `spec.md`
(`required[0]` → safe_tuned + unsafe + verus, so **R3 and R4**; `required[1]` →
safe_naive + unsafe + verus, **not R3**; `required[2]` and `required[4]` →
unsafe + verus, **R4 only**), a **second** variant falls:

> **`r3_no_capacity` records `required_absent: ["required[0]
> \`Vec::with_capacity(num_interfaces)\`", …]` — and `required[0]`'s English
> explicitly scopes it to `safe_tuned.rs`, which IS the R3 rung. So
> `r3_no_capacity` is out of contract under the same ruling, and
> `controls/spellings.json` records it `in_contract: true`.**

⭐ **It changes nothing**, and I checked rather than asserted that: its A1 is
1369.65, interior to the R3 span (cheapest 942.48, dearest 1388.14), so neither
R3 endpoint moves and `r3_endpoint_degenerate` stays `false`. **That is a real,
independent corroboration of F100's *"The R3 result is untouched by any of
this"* — by a route the manager did not use.** ⚠ But it means the repair owed is
**two** entries' worth of audit on this row, not one, and it is the concrete
instance of the task file's *"then every row's `required` owes the same audit"*.

### 1.5 ⛔⛔ EVIDENCE 2 — THE `invariant` FIELD IS **FALSE AS WRITTEN**, AND IT IS A FALSE DILEMMA

The task asks: *"Either the invariant is false as written, or those variants are
not in contract. Say which."* ▶ **Neither horn. The invariant is false as
written, and the code settles it in one line.**

`patterns-php/ph53-iface-tail-uninit/controls/spellings.py:1561`:

```python
"forbidden_hits": forb, "required_absent": miss,
"in_contract": not forb,
```

**`in_contract` is `not forbidden_hits`. It never consults `required_absent` at
all.** So the variants *are* in contract *by the field's own definition*, and
the `invariant`'s clause *"Every variant is in contract by
`harness/check.py::spelling_matches` over **EVERY** backticked idiom entry"* is
false: the determination ranges over the **`forbidden` half only**. The same
file's `audit()` docstring says so in terms — *"a `required` miss is REPORTED
and does not [disqualify]"* — so the `invariant` field contradicts a docstring
**45 lines above the code it describes**.

⭐⭐ **AND IT IS A FIFTH DEFECT IN THE SHARED `spellings.py` MACHINERY, CORPUS-WIDE
ON THE PHP SIDE — 5 of 5 FILES.** Measured over every `spellings.json` in the
tree: `ph07`, `ph16`, `ph29`, `ph45`, `ph53` **all five** open their `invariant`
with that byte-identical clause. The two PAT-side files that exist
(`p34-refcount-stack`, `p49-interned-pool`) **do not carry it at all** — their
`invariant`s are about checksums and per-cell pricing. ▶ **So the false clause
entered with the php copy and was cloned four times**, which is exactly F101's
law (*"a control cloned between rows carries its defects"*) at a **fifth**
generation, and this one was found by reading the field against the code rather
than by a new negatives suite.

⚠ **It is false on its own data in 4 of the 5, not just on `ph53`:**

| row | variants | variants with `required_absent` | the clause |
|---|---|---|---|
| `ph07` | 9 | **9 — including BOTH sides' `v0_shipped`** | ⛔ false |
| `ph16` | 17 | **17 — including BOTH sides' `v0_shipped`** | ⛔ false |
| `ph29` | 9 | **5 — all R3, including R3 `v0_shipped`** | ⛔ false |
| `ph45` | 9 | **0** | ✅ vacuously true |
| `ph53` | 20 | **13** | ⛔ false |

⚠ **The charitable reading, stated so the repair is not over-sold**: *"is in
contract **by** X **over** Y"* can be read as a claim about the *procedure*
(`spelling_matches` was run over every entry) rather than about the *result*.
Under that reading the clause is true. ▶ **But then it is a procedure
description and not an invariant**, and the field is called `invariant`. **Under
the only reading on which it asserts something falsifiable, it is false in 4 of
5 php rows.** That is my ruling and the repair is one clause, in five files.

### 1.6 ⚠⚠ EVIDENCE 3 — THE SIGNAL *DOES* DISCRIMINATE ON `ph53`'s R4 SIDE, AND THAT IS **UNIQUE IN THE CORPUS**

The task's counter was that `required_absent` is a raw presence report that
fires on shipped rungs, so its firing on the bitmask variants may be an artefact
of which pins are R4-scoped. **I surveyed all five php `spellings.json` as
instructed. The counter does not hold, and the survey settles it:**

| row | does `required_absent` fire on a **non-shipped** variant of a side whose **own `v0_shipped` is CLEAN**? |
|---|---|
| `ph07` | **No** — it fires on *every* variant on *both* sides, shipped included. Zero discriminating power |
| `ph16` | **No** — same, all 17 |
| `ph29` | **No** — fires on all 5 R3 variants including R3 `v0_shipped`; R4 side entirely clean |
| `ph45` | **No** — fires on nothing at all |
| ⭐⭐ **`ph53`** | ⭐⭐ **YES, and it is the ONLY instance in either programme.** R4 `v0_shipped` records `[]`; exactly three R4 challengers record `required[4]` |

▶ **That kills the artefact hypothesis by construction.** The "artefact of
scoping" story requires the entry to be out of scope for R4. But the R4 rung
**on the same side, in the same file** satisfies the same pin, and the entry's
English names `unsafe.rs` explicitly. **An entry that the shipped rung of its
own scope matches and three challengers in that same scope do not is a CONTRACT
DISTINCTION, not a scoping artefact.** ⓘ And I confirmed the degenerate case
too: applying (a) **without** honouring English scope excludes all nine R3
variants as well (they all miss `required[4]`, which is R4-scoped) and makes
*both* endpoints degenerate — which is the 41-of-41 failure mode `check.py`
documents, reproduced. **The scope read is load-bearing and I did it by hand
from `spec.md`; see §6 for the uncertainty that leaves.**

### 1.7 READING (c) — REFUTED AS STATED, AND THE NARROWED FORM IS THE REAL DEFECT CLASS

(c) says the entry *"does not belong in `idiom.required` AT ALL"* because
`idiom.required` pins the C-extracted idiom. **Measured across both programmes
(`check.py::read_contract` over all 8 php and all 33 PAT rows, 318 required
entries): `rust`-only dict entries already exist and are legitimate.** There are
**two** on the PAT side — `p19-state-machine/required[2]` and
`p46-bignum-mac/required[4]` — against 229 two-key dicts, 2 `c`-only, 85 bare
strings, and `ph53/required[4]` is the only `rust`-only one on the php side.

⛔ **So (c) is too strong** and a repair that moves the entry out of
`idiom.required` would be inconsistent with two shipped PAT rows.

⭐⭐ **But the narrowed form is exactly right, and it names the defect better
than (a) or (b) do.** Both PAT precedents are *"**THE RUNG BOUNDARY INSIDE THE
SAFE CLASS**"* declarations, and **both carry a sentence `ph53/required[4]` does
not**: *"Each is present in exactly one rung by construction, so the audit
reports the other three as absent for both — **that is the declaration working,
not failing**."* ▶ **They declare their own non-discrimination. `ph53`'s
`required[4]` declares nothing of the kind, and it discriminates.** And neither
`p19` nor `p46` has a `controls/spellings.json`, so **neither precedent has ever
been exposed to a spread search** — their pins' discriminating power is
untested.

▶ **THE REAL CLASS, and it is new:** `ph53/required[4]` is the first entry in
either programme that is simultaneously (i) in `idiom.required`, (ii) scoped to
one rung class by English, (iii) carrying a backticked spelling, and (iv) **able
to exclude an in-scope candidate that the shipped rung of that same scope
satisfies**. The PAT precedents have (i)–(iii) and explicitly disclaim (iv).
**That is what nothing measures, and it is what item 56 predicted.**

### 1.8 ⭐ THE DRAFTED REPLACEMENT SENTENCE

⛔ I edited nothing. `spec.md` is in `source_sha256`, so this costs **one `ph53`
re-gate and no re-measure** (`idiom` does not enter any measurement digest; I
verified `required` is presence-only, §1.5). ⚠ **This draft does NOT weaken the
pin to match a winner** — it states (a), which is the reading under which the
cheap variants LOSE, so `.memory/02-bench-rules.md`'s *a rung is never
cost-selected* is honoured in the direction that costs the row its headline.

**Replace `idiom.required[4].rust` in `patterns-php/ph53-iface-tail-uninit/spec.md`
with:**

> `` `wrote[i]` `` -- THE ONE-BYTE-PER-SLOT WITNESS, `[bool; MAXD]`, present in
> unsafe.rs and verus.rs and in no other rung. ⚠⚠ THIS ENTRY PINS THE
> REPRESENTATION AND NOT MERELY THE ROLE, per the NAMED-SPELLING STANDARD below:
> an R4 or R5 that establishes the same slot-coverage fact by a different
> expression -- a `u32` bitmask, a fill count, a sentinel value -- is OUT OF
> CONTRACT on this entry even though it discharges the identical obligation and
> even if it is cheaper, and `controls/spellings.json`'s `required_absent` is
> where that exclusion is recorded. The reason the representation is pinned and
> not left free is that the row's R4 trusted surface is counted per accessor and
> a bit-packed witness changes what is counted, so leaving it free would make
> the R4 endpoint a choice of witness width rather than a result. IT IS NOT IN
> THE C AND IT IS NOT UPSTREAM: it is what makes R4's unsafe read dischargeable,
> and the row's Verus-side result is that a faithful witness-free R4 CANNOT BE
> VERIFIED at all -- coverage is a property of the op stream, i.e. of attacker
> data, and the pinned driver loop offers no call site at which to establish it.
> controls/r4_nowitness.rs is that program, measured, run under Miri and put
> through Verus with its error text. It is indexed SAFELY on purpose: reaching a
> rung's own safety witness with an unchecked access would make the witness rest
> on the thing it exists to establish.

⚠⚠ **THREE THINGS THAT MUST LAND IN THE SAME RE-GATE OR THE ROW GOES OUT
INCONSISTENT**, and the manager should route them together:

1. **`controls/spellings.py` must exclude the three bitmask variants**, by
   `ENGLISH_VERDICTS` — which is the row's own mechanism for precisely this and
   is currently **`ENGLISH_VERDICTS = {}`**, empty, with a comment saying *"A
   module constant so a negative can assert the exclusion actually reaches
   `cheapest_in_contract`"*. ▶ **The mechanism was built for this case and is
   unused.** Populating it flips `r4_endpoint_degenerate` to `true` mechanically
   and the existing negatives already cover the path (§H is satisfied by the
   suite that ships).
2. **`r3_no_capacity` owes the same treatment** (§1.4) — and it is the test of
   whether the repair was applied as a *rule* or as a patch on the one variant
   that embarrassed the headline.
3. **The `invariant` clause (§1.5), in all five php files.** Suggested
   replacement for the opening clause: *"Every variant's
   `forbidden_hits` is empty by `harness/check.py::spelling_matches`, which is
   what `in_contract` means here; `required_absent` is reported beside it and is
   judged against each entry's English, because `required` is presence-only and
   cannot fail the gate (`check.py::idiom_audit`)."*

### 1.9 ⛔ WHAT F100 MAY AND MAY NOT SAY AFTER THIS RULING

**Falls:** the headline *"BOTH ENDPOINTS MOVE — 2nd row in either programme"*;
the table rows `r4_bitmask` **−11.40 %** and `r4_bitmask_min` **−3.12 %** as
*endpoint* results; `r4_endpoint_degenerate false`.

**Survives, each checked separately rather than assumed:**

* ✅ **The R3 half in full** — `r3_chunks_mask` **−32.08 %**, and it survives
  even the stricter audit of §1.4.
* ✅ **`r4_bitmask_min` is cheaper *and* smaller-surface** (3 trusted call sites
  vs 10, 2 accessors vs 4) — it is now a **control-class** result rather than an
  endpoint, i.e. *"a witness-representation change that would be cheaper and
  smaller-surface is out of this row's contract"*, which is a **more**
  interesting sentence and is `.memory/02-bench-rules.md`-clean.
* ✅ **The R3 mechanism result** — nine window bounds checks, **281.8 Ir/call,
  20.3 % of the rung**, larger than the **270.7 Ir/call** R3−R4 gap, with
  `r4_win_checked` **+33.92 %** as the mirror. Nothing in it touches
  `required[4]`.
* ✅ **The A1-spread result (item 82's subject) is INSENSITIVE to this ruling.**
  `a1_spread_pp` is computed at `controls/spellings.py:2020` as
  `max−min` of `pct_vs_r4ship_a1` **over all variants on a side, with no
  `in_contract` filter**. Recomputed with (a)'s exclusions: R3 **39.899657 pp
  unchanged** (8 variants), R4 **45.313019 → 33.917949 pp** (6 variants). **Tens
  of pp either way, so F100's *"A1 is not respelling-blind"* stands under both
  readings.** ⓘ The published `45.313019` is over **10** variants including one
  that is `in_contract: false` — worth a footnote, not a retraction.
* ✅ **All six of F100's published A1 percentages re-derive to the digit** from
  `controls/spellings.json`: −32.08, −11.40, −3.12, +33.92, and the four
  shipped-witness reductions +0.50 / +2.99 / +3.03 / +6.60. **F100's arithmetic
  is clean; its ruling was not.** That matches the manager's own record —
  *"eight corrections, none of them arithmetic"*.

⚠ **One F100 citation I could not re-derive from `controls/spellings.json`**:
the twin verdicts *"`31/0`, `32/0`". `spellings.json`'s `verus_checked` is a
bare `true`, not a count. The figures are in
`patterns-php/ph53-iface-tail-uninit/NOTES.md:550` (**31 verified / 0 errors**,
`r4_bitmask`) and `:741` (**32 verified / 0 errors**). **Naming the file is
F99's own rule and the task file did not.**

---

## §2 ⭐⭐ ITEM 82 — **CLOSEABLE WITHOUT A ROW EDIT.** THE ATTRIBUTION TO F87 IS WRONG, I FOUND WHY, AND THE CENSUS MISSED TWO SITES

### 2.1 The two rows' numbers, re-measured from the artefacts

Read directly out of each row's `controls/spellings.json` (not from the task file):

| row | `a1_spread_pp` | `wp_spread_pp` | variants | `headline_statistic` |
|---|---|---|---|---|
| `ph45` | `{R3: 0.0, R4: 0.0}` | `{R3: 66.730637, R4: 44.454781}` | 9 | `ir_per_call_small_wp` (**W1**) |
| `ph53` | `{R3: 39.899657, R4: 45.313019}` | `{R3: 67.930558, R4: 39.543977}` | 20 | `ir_per_call_small` (**A1**) |

✅ **Both match the task file to the digit.** ⭐ **And one thing the task file did
not point out, which reframes the whole item: the two rows' WHOLE-PROGRAM spreads
are COMPARABLE — 66.7/44.5 against 67.9/39.5.** ▶ **So the two searches found
code differences of similar whole-program size. The difference between the rows
is entirely in whether A1 could SEE them.** That is the shape of an observer
property, not of a row property, and it is why the restatement matters.

### 2.2 ⛔ QUESTION 1 — THE ATTRIBUTION TO F87 IS **WRONG**, AND HERE IS THE CONFUSABLE TWIN THAT EXPLAINS IT

Item 82 says *"F87 published a row fact as a statistic fact"*. **Measured over
F87's whole body** (`RECAP_PHP.md:2630` to the start of F86, 150 lines, extracted
programmatically):

| token | occurrences in F87 |
|---|---|
| `spread` | **0** |
| `blind` | **0** |
| `inside_share` | **0** |
| `0.000000` | **1** |

⭐⭐ **AND THE ONE `0.000000` IN F87 IS A DIFFERENT MEASUREMENT.** `RECAP_PHP.md:2769`:
*"✅ **AND FAMILY A's NULL IS RE-DERIVED THROUGH A DIFFERENT CODE PATH:** `max |A|
= 0.000000` over all 8 true-null cells, computed off the **callgrind profiles**
here rather than off `results-php/` as F82 did"*. **That is family A's NULL
CONTROL, over 8 byte-identical pairs. It is not a respelling spread and it is not
about respelling at all.**

▶ ⭐⭐⭐ **SO THE ATTRIBUTION ERROR HAS A MECHANISM, AND IT IS NOT CARELESSNESS:
F87 carries a `0.000000` and item 82 attributed the wrong one to it.** Two
distinct A-family measurements print the same six-decimal zero in the same
finding's neighbourhood — A's *null* (Δ between byte-identical programs, which
**ought** to be zero and is) and A's *respelling spread* on `ph45` (which ought
to be non-zero and is not). ⚠ **The first is A working; the second is A failing.
They are confusable on sight and they are opposite in meaning.** ⭐ **That is
worth a line in `.memory-php/03-numbers.md` beside both figures**, and it is the
generalisable half of item 82.

### 2.3 ⭐⭐ THE CENSUS — TWO SITES THE TASK FILE'S TABLE OMITS

Swept: `RECAP_PHP.md`, `.memory-php/` (all 5 files), `results-php/` (recursive,
including `gate/`, `tables/`, `preflight/`), all 8 rows' `NOTES.md` and
`README.md`, all 5 php `controls/spellings.json`, both PAT `spellings.json`, and
`.tasks-php/*.md`. **`grep -a` throughout.**

| site | wording | scoped correctly? |
|---|---|---|
| `patterns-php/ph45-.../NOTES.md:609–633` | *"A1 CANNOT RESOLVE **THIS ROW** AT ALL … Its spread over a side is `0.000000` pp"*, + the mechanism at `:633` | ✅ **YES** |
| `.tasks-php/TASK_PHP_037_REPORT.md:29` | *"A1's spread over **all nine variants**"* | ✅ **YES** |
| **F87's body** | ⭐ **no A1-spread claim exists in it.** §2.2 | — **attribution WRONG** |
| **F91's table, `RECAP_PHP.md:2465`** | the clause as evidence for A's definitional blindness | ✅ **ALREADY WITHDRAWN IN PLACE**, verified: *"⚠⚠ The second clause this row used to carry … IS WITHDRAWN as evidence for blindness"* |
| ⭐⭐ **`.tasks-php/STATISTICS_001.md:50`** — **MISSED BY THE CENSUS** | *"**A** ⛔ **blind to callees** \| `ph45`'s `inside_share` is 0.055–0.094, **and** A1's spread over **nine** searched R3/R4 variants is `0.000000` pp against 66.7/44.5 pp whole-program (F87, `_037` §5.4)"* | ⛔⛔ **NO — and it is LIVE.** The *number* is scoped (*"nine"*); the *inferential role* is not: it sits in a column headed **"the measurement that shows it"** under a claim about **A's DEFINITIONAL gap**. That is precisely the role `RECAP_PHP.md:2465` withdrew |
| ⭐⭐ **`.memory-php/02-ladder.md:531`** — **MISSED BY THE CENSUS, AND IT IS THE AUTHORITATIVE LAYER** | *"⚠⚠ **AND A1 IS BLIND ON THIS ROW**: spread `0.000000` pp across **all NINE searched variants**, against 66.7 pp (R3) and 44.5 pp (R4) whole-program"* | ✅✅ **YES — BOTH scope qualifiers present** (*"ON THIS ROW"* **and** *"all NINE searched variants"*). **The authoritative layer is CLEAN** |
| `ph53` `controls/spellings.json` `statistic` | *"A1 IS THE HEADLINE ON THIS ROW and that is **the opposite of `ph45`**: every helper here is `inline(always)` into `kernel`, so `kernel` carries **89.5 per cent** of the program and A1 resolves the search (`a1_spread_pp` below is tens of percentage points, where `ph45`'s was `0.000000`)"* | ✅ **YES — and it IS the reconciliation item 82 asks for, already written, inside the row, naming `ph45`** |
| `ph45` `controls/spellings.json` `statistic` | *"⚠⚠ **A1 SEES 9.5 % OF THIS ROW**: `dec` is a separate symbol carrying ~90 % of every rung's instructions, **every lever searched here lives in `dec`**, and A1 therefore reports EVERY variant on a side as exactly 0.00 %"* | ✅ **YES — mechanism stated** |

▶ ⭐⭐⭐ **VERDICT: ITEM 82 IS CLOSEABLE, AND NO ROW EDIT IS OWED.**

* **F87 owes no restatement — it never made the claim.** Item 82's opening
  sentence should be struck, not discharged.
* **The authoritative layer is already correct**, with both qualifiers.
* **Both rows' own hashed-adjacent `controls/spellings.json` already carry the
  reconciliation, in the `statistic` field, each naming the other row.** A
  re-gate would buy nothing.
* ⛔ **ONE edit is owed and it is cheap: `.tasks-php/STATISTICS_001.md:50`.** A
  committed `.tasks-php/` file, **not hashed, not in any `source_sha256`, not in
  any measurement digest** — zero gate cost. ⚠ **And it is item 73's exact shape
  for the third time: the correction landed in `RECAP_PHP.md` and not in the
  document `RECAP_PHP.md:82` calls *"the whole argument"*.**

**Drafted replacement for `STATISTICS_001.md:50`'s evidence cell:**

> `ph45`'s `inside_share` is **0.055–0.094** — **A sees 9.5 % of that row** — and
> A1 reports a whole-program effect of `+23.37 %` as `+0.000 %` (F86's **BLIND**
> class). ⓘ A1's spread over `ph45`'s nine searched variants is also
> `0.000000` pp against 66.7/44.5 pp whole-program, which is **the same BLIND
> class on a respelling population** and is **a fact about a row whose every
> searched lever lives in the callee `dec`, not about A**: on `ph53`, whose
> `kernel` carries **89.5 %**, the same statistic spreads **39.9/45.3 pp** over
> 20 variants (F100, item 82). ▶ **The gap is real; its measure is
> `inside_share`, not the spread.**

### 2.4 ⭐⭐ QUESTION 2 — YES, IT IS F86's **BLIND** CLASS, AND THE PROGRAMME HAD THE NAME *AND AN INSTANCE ON THIS VERY ROW*

**F86's definition:** *"**BLIND** = A is exactly `0` while the whole-program
figure is not — A says nothing at all"*, counted **14 of 366**.

✅ **`ph45`'s `0.000000` pp spread satisfies that definition exactly.** If A1 is
identical across all nine variants on a side while W1 spreads 66.7 pp, then every
pairwise variant comparison has `ΔA` exactly `0` and `ΔW1 ≠ 0` — **BLIND, by
F86's own predicate.**

⭐⭐ **AND F86 ALREADY NAMES `ph45` AS A BLIND INSTANCE, WITH A NUMBER**: *"BLIND
is the worse failure: on `ph45` it is **A `+0.000 %` against a `+23.37 %`
effect**"*. ⭐⭐⭐ **AND `.memory-php/02-ladder.md` USES THE WORD `BLIND` FOR
`ph45` AT `:531` AND DEFINES F86's BLIND CLASS AT `:546` — **FIFTEEN LINES
APART, IN THE SAME FILE.** ▶ **So the programme had the concept, the name, the count and an
instance on this row, and F91's evidence table failed to use any of it.** **That
is a better finding than the restatement, exactly as the task predicted.**

⚠⚠ **BUT THE RECONCILIATION IS NOT "IT IS ONE OF THE 14" — AND I WANT THIS SAID
PRECISELY, BECAUSE THE LOOSE VERSION WOULD BE WRONG.** F86's 366 comparisons are
**rung-pair** comparisons (8 cells choose 2, per row per input). `ph45`'s
`a1_spread_pp` is over **respelling variants within one rung class**. ▶ **Same
definition, DIFFERENT POPULATION.** `ph45`'s respelling instances are **not
among** the 14, because the respelling population was never enumerated — so:

* ✅ **F86's 14 of 366 stands** (its population is declared).
* ⚠ **but the BLIND class is LARGER than its headline**: `ph45` alone contributes
  up to `C(9,2) = 36` BLIND comparisons per side on a population F86 never
  scored. **Not a refutation — a scope note, and it belongs beside the 14.**
* ✅ `ph45` is a **clean** BLIND instance, not one of the ambiguous 5 that
  `_038` §2.4 found *"lump A genuinely sees nothing together with A correctly
  reads a true zero"* — here A genuinely sees nothing (`inside_share` 0.055,
  levers in `dec`).

⭐ **THE RIGHT NAME FOR THE REPAIRED SENTENCE IS THEREFORE `BLIND`**, and the
drafted sentence in §2.3 uses it.

### 2.5 ✅ QUESTION 3 — **NO.** F91's `|B/A|` = 49.6–393.9× CLAIM DOES NOT DEPEND ON THE MISREADING. VERIFIED, NOT INHERITED

F91's Result 5 table (`RECAP_PHP.md:2346`) has columns
`row · opt · inp · Δnopad · A Ir/call · rate/insn · B Ir/call · |B/A| · sign`
over **9 cells**: `ph45` O3 small/large, `ph64` O3 small/large, and five O0
cells. **Its population is the `unsafe vs verus` pair, by `Δnopad`**, and F91
states the limit itself: *"`Δnopad` exists only for the `unsafe vs verus` pair"*.

▶ **Not one of the nine is a respelling comparison. `a1_spread_pp` does not enter
the computation, is not a column, and is not cited in the result.** The manager's
position is **correct** and I am not inheriting it — the table's own population
settles it.

⚠ **BUT THERE *IS* A DEPENDENCY, ONE STEP FURTHER ON, AND IT IS WHERE THE TASK
FILE'S QUESTION STOPS ONE SENTENCE SHORT.** F91's **conclusion** section —
*"WHAT IT CHANGES: THE AXIS IS SAME-LANGUAGE vs CROSS-LANGUAGE"* — has an
evidence table whose `A ⛔ blind to callees` cell was the withdrawn clause. **The
`|B/A|` MEASUREMENT is independent; the AXIS INFERENCE drawn from it was partly
resting on the misreading.** ✅ That clause is withdrawn in place at
`RECAP_PHP.md:2465`. ▶ **And §3 shows the axis has a second, larger problem that
the withdrawal does not fix.**

⭐ **One correction in F100's direction too, so this is not one-sided:** F100
writes *"here A resolves respellings to **40 pp**, which is the same property
working"* and offers it as support for F91's regime argument. ⚠ **It is not
support for the REGIME argument.** F91's regime is about **1–2-instruction**
differences; `ph53`'s R3 span is **942 → 1388 Ir/call**, a **445 Ir/call**
spread. **`ph53`'s respellings are LARGE-Δ, so they say nothing about the small-Δ
regime.** They do support the weaker and still-useful claim that A is
*symbol-scoped and therefore resolves differences inside the symbol*.

### 2.6 ⭐ QUESTION 4 — THE RIGHT GENERAL STATEMENT, AND ITS **PRE-SEARCH** PREDICATE ALREADY EXISTS AND IS ALREADY PUBLISHED

**The statement** (the task's candidate, which I accept with one tightening):

> **A1 resolves a code difference exactly to the extent that the difference's
> INSTRUCTIONS land inside the kernel symbol.** `ph45` (every searched lever in
> the callee `dec`, A1 sees 9.5 %) and `ph53` (every helper `inline(always)` into
> `kernel`, A1 sees 89.5 %) are **two instances of one rule, not a
> contradiction.**

⚠ **The tightening: it is the DIFFERENCE's location, not the WORK's location.**
`inside_share` measures where the *work* is. A row could have low `inside_share`
and levers inside `kernel`, and then A1 would resolve the search while still
being unsafe for a cross-language comparison. **The two are separate and the
published rule only measures the second.** ⓘ No row in the corpus is that case,
so this is a stated limit and not an observed one.

⭐⭐ **THE PRE-SEARCH PREDICATE IS ALREADY IN THE AUTHORITATIVE LAYER AND I DID
NOT NEED TO INVENT ONE.** `.memory-php/02-ladder.md:370–372`, the **corrected
two-condition rule** (F74 as corrected, *"conjunction measured clean at 151 of
366 comparisons with ZERO flips"*):

> **(i)** `min(inside_share)` over the two cells must be **HIGH** — A must
> actually SEE both — **AND (ii)** `|Δinside_share| ≤ 0.02`.

▶ **Condition (i) IS the pre-search predicate**, and it is computable from the
shipped rungs' own callgrind record **before any variant exists**:

| row | A1's share of the program, shipped | condition (i) | `headline_statistic` the row actually chose | agree? |
|---|---|---|---|---|
| `ph45` | **9.5 %** (`dec` carries ~90 %) | ⛔ **fails** | **W1** (`ir_per_call_small_wp`) | ✅ |
| `ph53` | **89.5 %** (34 691 877 of 38 765 393 `Ir`, `NOTES.md:810`) | ✅ **passes** | **A1** (`ir_per_call_small`) | ✅ |

⭐⭐ **2 of 2 rows already chose the right ranking key by this predicate, before
their searches ran, and each row's `statistic` field gives the share as the
reason.** ▶ **So the predicate is retrodictively validated on both instances and
needs no new machinery — what is owed is that it be NAMED as the rule rather than
re-derived per row.**

⚠⚠ **THE MAGNITUDE FLOOR, AS DEMANDED.** The sign claim is *"A1 resolves / does
not resolve"*. The magnitudes are `0.000000` pp and `39.899657` / `45.313019` pp
— **an exact zero against tens of percentage points**, so there is no
outlier-at-`0.00 pp` hazard: the zero is the *predicted* value on the failing
side, and the passing side is 40 pp, not 0.4 pp. ⛔ **AND I WILL NOT PROPOSE A
THRESHOLD FOR CONDITION (i).** The two observations are `0.095` and `0.895`, a
**9.4× gap**, and `.memory-php/` already says the threshold is *"not tuned and
six rows cannot pin it (`>0.3`, `>0.5`, `>0.6` all give 0 flips)"*. **n = 2
cannot pin what six rows could not.** Any threshold in `(0.10, 0.89)` separates
the two rows, and that is all the data supports.

---

## §3 ⭐⭐⭐ ITEM 78 — THE MISSING CELL IS **FREE, NON-EMPTY, AND 9 NOT 10**. ⛔ **BOTH** THE AXIS AND THE RIVAL LOSE, AND THE WINNER IS §2's RULE

### ⭐ MEASUREMENT COST PAID: **ZERO.** No callgrind, no build. The fallback was not needed.

The free route exists. **I did not pay for the `ph53` `c-gcc` vs `c-gcc-h`
route**, so `W1` for `ph53` is still not in `results-php/` and that remains true.

### 3.1 The probes I relied on, and their selftests

| probe | selftest | note |
|---|---|---|
| `.temp/mgr172/flip_exact.py` | **PASS**, 6 negatives | ⚠ its `N5` (*"0 mispredictions"*) **cannot fire** — `_038` §2.2 showed the predicate is the definition of a flip. I did not rely on it |
| `.temp/php38/flip_columns.py` | ⛔ **FAIL — `N5`** | ✅ **and the failure is a STALE HARDCODE, not a defect in the data**: it asserts `cross-language == 28` and measures **29**. `RECAP_PHP.md` already records *"29, not 28"*. ▶ **This is the FOURTH hardcoded figure in a validator to go stale in this thread** (after `quota.py`'s `N7` and `preimage_screen.py`'s `N10e`). N1/N2/N3/N4/N6 PASS |
| `.temp/php43/item78_cell.py` (mine) | **PASS**, 7 negatives | ⭐ **N3 pins that I am reading the CORRECTED classifier** — `BLIND == 14`, so not the version F86 says scored BLIND as FLIP and inflated 38 to 52. **N7 is the load-bearing one** (below) |

✅ **I confirmed the classifier in source**: `flip_columns.py:86–88` scores
`flip` as `sign(a)!=0 and sign(b)!=0 and sign(a)!=sign(b)` and `blind` as
`sign(a)==0 and sign(b)!=0` — **separated**, which is the corrected form.

### 3.2 ⛔ THE COUNT IS **9**, NOT 10 — THE TASK FILE'S ARITHMETIC USED THE SUPERSEDED 28

Measured, `O3/isolated`, 7 rows × 2 inputs × C(8,2) cells = **366 comparisons**:

```
38 flips = 29 CROSS-LANGUAGE  +  0 C-vs-C  +  9 SAME-LANGUAGE (Rust vs Rust)
14 BLIND =  2 cross-language  +  4 C-vs-C  +  8 same-language
```

▶ **`38 − 29 = 9`.** The task file computes `38 − 28 = 10`. ⚠ **Item 73's shape
a fourth time**: the corrected count `29` is published in `RECAP_PHP.md` and the
task file used the superseded `28`. ⓘ Also settled in passing: **0 C-vs-C
flips**, so `flip_columns.py`'s own hypothesis (c) (*"a C-vs-C pair belonging to
no named column"* ) is **NEGATIVE on the flip population** — though **4 of the 14
BLIND cells ARE C-vs-C**, which is its nearest relative.

### 3.3 ⭐⭐ THE MISSING CELL, IN FULL — AND A FLIP **ENTAILS** CALLEE DIVERGENCE, SO THE CELL NEEDED NO EXTRA MEASUREMENT

`A` = `kernel_exclusive_ir`/call %Δ, `B` = `marginal_ir_per_call` %Δ,
`s` = `inside_share` of each side. All `O3/isolated`.

| row | inp | comparison | column | **A %** | **B %** | \|B/A\| | s_x | s_y |
|---|---|---|---|---|---|---|---|---|
| `ph45` | large | `safe_tuned` vs `verus` | R3 vs R5 | **+0.056** | −3.428 | 60.9 | 0.094 | 0.091 |
| `ph45` | small | `safe_tuned` vs `verus` | R3 vs R5 | **+0.404** | −3.188 | 7.9 | 0.100 | 0.096 |
| `ph45` | large | `unsafe` vs `verus` | the R4/R5 null | **+0.005** | −0.194 | 35.8 | 0.091 | 0.091 |
| `ph45` | small | `unsafe` vs `verus` | the R4/R5 null | **+0.038** | −0.183 | 4.8 | 0.096 | 0.096 |
| `ph64` | small | `unsafe` vs `verus` | the R4/R5 null | **+0.007** | −2.364 | 350.5 | 0.946 | 0.923 |
| `ph45` | large | `safe_tuned` vs `unsafe` | **the fixed-R4 bound** | **+0.051** | −3.241 | 63.7 | 0.094 | 0.091 |
| `ph45` | small | `safe_tuned` vs `unsafe` | **the fixed-R4 bound** | **+0.365** | −3.010 | 8.2 | 0.100 | 0.096 |
| `ph64` | large | `safe_naive` vs `safe_tuned` | the safe span R2 vs R3 | **−2.636** | +25.435 | 9.6 | 0.721 | 0.929 |
| `ph64` | small | `safe_naive` vs `safe_tuned` | the safe span R2 vs R3 | **−2.809** | +32.682 | 11.6 | 0.695 | 0.949 |

⭐⭐⭐ **THE CELL IS FILLED WITHOUT MEASURING DIVERGENCE, AND HERE IS WHY — THIS IS
THE ARGUMENT THE FREE ROUTE TURNS ON.** `A` is the kernel-exclusive Δ and `B` the
whole-program Δ. **If they disagree in sign, the out-of-kernel Δ must be opposite
in sign to the kernel Δ AND larger in magnitude.** ▶ **So every flip IS an
instance of *the callee work diverges*, by construction.** My `N7` checks it
numerically — `a·b < 0` on all 38, **0 exceptions** — rather than leaving it as an
argument.

### 3.4 ⛔⛔ THE RIVAL IS **REFUTED**, THREE TIMES OVER

**The rival:** the axis is *does the callee work diverge*; language is merely
correlated.

1. ⛔⛔ **ITS VARIABLE DOES NOT VARY ON THE POPULATION THAT DEFINES THE
   PHENOMENON.** By §3.3, callee work diverges in **all 38** flips — the 29
   cross-language ones **and** the 9 same-language ones. ▶ **So divergence cannot
   distinguish the cells it was proposed to distinguish.** A variable that is
   `true` on every member of the class is not an axis.
2. ⛔ **ITS PRESCRIPTION IS WRONG WHERE THERE IS GROUND TRUTH.** The rival says:
   where callee work diverges, the callee-inclusive column is the right one.
   **Three cells of the missing cell are the `R4/R5 null`, and F91's Result 5
   gives those cells an independent ground truth — `Δnopad`.** On `ph45` the two
   programs differ by **2 instructions** and A reads **−2.0000 Ir/call, rate
   exactly 1.0000/insn on both inputs 7.5× apart in call count**, while B reads
   **+99.250 / +787.860** — **49.6× and 393.9× off, opposite in sign.** On `ph64`
   `Δnopad = −1` and A reads **−0.5093 / −0.5100**. ▶ **Divergence is present and
   the callee-inclusive column is wrong by two to three orders of magnitude. The
   rival would pick it.**
3. ⚠ **AND `ph53`'s AGREEMENT WAS NEVER EVIDENCE FOR THE RIVAL.** Item 78 says
   *"`ph53` — A and B AGREE. Rival predicted it; axis did not."* ⛔ **The axis
   makes no prediction that agreement violates.** The axis is a **prescription**
   (*cross-language, do not use A alone*), not a prediction of disagreement. When
   A and B agree, the prescription costs nothing and loses nothing. ▶ **So the
   2×2's top-right cell is not a scoring cell for either hypothesis.**

### 3.5 ⚠⚠ BUT THE AXIS LOSES TOO, AND ON ITS OWN TABLE — **THE AXIS IS A PROXY FOR `inside_share`, NOT FOR LANGUAGE AND NOT FOR DIVERGENCE**

⛔ **All nine cells of F91's own Result 5 are SAME-LANGUAGE.** F91 states the
reason itself: *"`Δnopad` exists only for the `unsafe vs verus` pair"*, and the
table's fifth row is `ph03`·`ph07`·`ph16`·`ph45`·`ph64` at **O0**, Δnopad
`+17 … −170`, `|B/A|` **0.2×–3.0×**. ▶ ⭐⭐⭐ **So F91's regime separation
(49.6–393.9× small-Δ vs 0.2–3.0× large-Δ) is measured ENTIRELY WITHIN the
same-language class and is indexed by |Δ| MAGNITUDE — there are same-language
cells in BOTH regimes.** **"Same-language ⇒ only A can resolve it" is therefore
false as a general statement, by F91's own fifth table row.** ⓘ F91 does declare
the limit (*"the regime is directly measurable on R4/R5 and INFERRED
elsewhere"*), so this is an over-reach in the conclusion section, not a hidden
one — but item 78 should be closed against **both** candidate axes, not one.

⭐⭐ **AND THE MISSING CELL SETTLES WHAT THE REAL PREDICATE IS. ALL NINE CELLS ARE
CAUGHT BY §2.6's TWO-CONDITION `inside_share` RULE, AND IT IS LANGUAGE-AGNOSTIC:**

| cells | condition (i) `min(s)` HIGH | condition (ii) `\|Δs\| ≤ 0.02` | caught by |
|---|---|---|---|
| **`ph45` × 7** | ⛔ **FAILS** — `min(s)` = **0.091–0.096** | passes (`\|Δs\|` ≤ 0.004) | ✅ **(i)** |
| **`ph64` × 2** | ✅ passes — `min(s)` = **0.695 / 0.721** | ⛔ **FAILS** — `\|Δs\|` = **0.208 / 0.254**, 10× the threshold | ✅ **(ii)** |

▶ **The conjunction catches 9 of 9, and it never mentions language or
divergence.** ⓘ Consistent with `.memory-php/`'s own *"conjunction measured clean
at 151 of 366 comparisons with ZERO flips"*.

### 3.6 ⚠ MAGNITUDE FLOOR ON THE SIGN CLAIM, AS DEMANDED — AND IT SHRINKS THE CELL BUT NOT THE CONCLUSION

**Four of the nine have `|A| < 0.06 %`** (+0.056, +0.051, +0.038, +0.005) — which
is F86's own caveat about *"two ways of measuring approximately nothing"*, and two
of them are literally the `ph45` R4/R5 cells F86 named. ▶ **At a `|A| ≥ 0.1 %`
floor the missing cell is 4 cells, not 9**: `ph45/small` R3-vs-R5 (+0.404) and
R3-vs-R4 (+0.365), and `ph64` R2-vs-R3 (−2.636, −2.809).

✅ **The conclusion is UNCHANGED under the floor**: 2 of the 4 survivors are
`ph45` (caught by condition (i)) and 2 are `ph64` (caught by condition (ii)).
**9 of 9 and 4 of 4.**

### 3.7 ▶ THE VERDICT AND WHAT IT DOES TO ITEM 62

> **ITEM 78: ANSWERED. F91's same-language/cross-language axis is a PROXY — but
> for `inside_share` (and, within the same-language class, for `|Δ|` magnitude),
> NOT for *does the callee work diverge*. The rival is REFUTED; the axis is
> REFUTED AS A GENERAL STATEMENT and survives only as a correlate. The operative
> rule is the two-condition `inside_share` conjunction already published in
> `.memory-php/02-ladder.md`, and it is measurable per comparison with no new
> machinery.**

⭐ **Item 62 (family C) gets narrower and cheaper, as the task hoped, but by a
different route than it expected**: the condition is **`inside_share`, already
computed for every cell in every record**, not a per-comparison declaration of
callee divergence. ▶ **And F91's own open demand stands unchanged and is now the
only thing item 62 must do first: measure C's SENSITIVITY, not just its null.**

⚠⚠ **SCOPE, STATED.** The missing cell is **7 cells from `ph45` and 2 from
`ph64`** — **two rows**, both with known statistic pathologies (`ph45` is the
`inside_share` outlier at 0.055–0.094; `ph64` is the row that broke §B1a's
O(1)-allocation precondition). ⛔ **I have not settled a programme-wide axis on
`ph53`, and I have not settled one on these two either.** What I have done is
show that **the two candidate axes in item 78 both fail on data already on disk**,
and that a third predicate already in the authoritative layer catches every
instance. ⓘ **`ph03`, `ph07`, `ph16`, `ph29` and `ph00` contribute ZERO
same-language flips**, which is itself worth recording: the phenomenon is
concentrated on two rows.

---

## §4 THE THREE LOAD-BEARING FINDINGS — **F94 UPHELD-NARROWED · F95 UPHELD · F92 UPHELD-NARROWED**

### 4.1 ⛔ F94 — **UPHELD-NARROWED.** THE CONCLUSION STANDS, BUT *"REFUTED TWICE INDEPENDENTLY"* IS NOW *"REFUTED ONCE"* — F95 WITHDREW THE OTHER ROUTE AND F94 STILL CLAIMS IT

**Second method: the 5.0.0 source tree itself** (`.temp/php11/_cache/php-5.0.0/`),
read directly, plus `preimage_screen.py --row ph53 --verbose`.

**Route A — the screen.** Run today:

```
### ph53 · CRASH-158 · `be8daf1f47fa` · `Zend/zend_compile.c` [[2571, 2571], [1951, 1951]]
    5.0.0     :1951  if (ce->interfaces[i] == entry) {
    5.0.0     :2571  ce->interfaces = (zend_class_entry **) erealloc(...*ce->num_interfaces);
→ verdict INAPPLICABLE-SAME-FILE        (NOT `NOT-THE-REPAIR`)
→ the screen's own banner: "⭐ CITE 0 EXCLUSIONS, NOT 1"
→ and: "## INAPPLICABLE-SAME-FILE -- ⛔ NOT exclusions. The screen says
         nothing about these"
```

⛔⛔ **F94's table says *"screen `NOT-THE-REPAIR` 0/2"*. THAT LABEL IS GONE.** F95's
own `same_function` soundness guard demoted **this exact record** — N11 prints it:
`ph53 be8daf1f47fa: same_function=False, crossed_into='void
zend_do_implements_interface(znode *interface_name TSRMLS_DC)'`. ▶ **So route A is
no longer an exclusion at all, by the screen's own words.**

▶ **VERDICT: the EXCLUSION stands; the EVIDENCE BASE is overstated by one
route.** `be8daf1f47fa` (2008) cannot be the fix for a line that left the release
series at **php-5.0.5 (2005)**, and `d09cdd9f71f3` is positively identified and
`patch -p1`es onto the pristine tarball at zero fuzz. **F94's conclusion is
correct. Its *"REFUTED TWICE INDEPENDENTLY"* must become *"REFUTED by the tag
walk; the text screen is INAPPLICABLE-SAME-FILE and says nothing."***
⚠⚠ **Item 73's shape a FIFTH time, and this one is 100 lines from its own
correction inside `RECAP_PHP.md`.** ⛔ **Row 8 (`ph52`) is queued on the words
*"R1h settled (F94)"* — that is still true, but a reader who follows F94 to the
screen will find a label that is not there.**

### ✅ ARE THE TWO ROUTES THE SAME EVIDENCE TWICE? **NO** — and I can say why precisely

| | artefact | proposition | failure mode |
|---|---|---|---|
| **route A** (screen) | `be8daf1f47fa`'s patch + **its own parent tree** (`sha256 1dc76c81013f6067`) | *the commit's hunks do not reach :2571 or :1951* | text-only; blind to semantics; **and blind to a mislabelled hunk, which is what bit it** |
| **route B** (tag walk) | the **release tags** php-5.0.1 … php-5.0.5 | *:2571's line left the series at 5.0.5, 2 y 9 m before the commit* | **count-based**; blind to which site a count refers to |

▶ **Different artefacts, different propositions, and neither is derivable from
the other** — route A could hold with route B false (a commit that misses a site
still present) and vice versa. ✅ **Not the same evidence twice.**

### ⭐⭐ DOES `preimage_screen.py` DISAMBIGUATE SITES? **YES — AND BETTER THAN THE TAG WALK DOES**

The task's worry is sound but lands on route **B**, not route A.

**Measured: 5.0.0's `Zend/zend_compile.c` has exactly TWO `erealloc(ce->interfaces`
sites**, and `grep -an` gives their line numbers:

| line | text | which |
|---|---|---|
| **`:1944`** | `ce->interfaces = (zend_class_entry **) erealloc(ce->interfaces, sizeof(zend_class_entry *) * (ce_num + if_num));` | the inheritance merge — **the SURVIVOR** |
| **`:2571`** | `ce->interfaces = (zend_class_entry **) erealloc(ce->interfaces, sizeof(zend_class_entry *)*ce->num_interfaces);` | **the CITED site** |

⚠ **AND THE LINE NUMBER IS `:1944`, NOT `:1945`.** The task file (§4.1) and the
manager's read say *"the inheritance-merge line at `:1945`"*. **Measured: 1944.**
(`:1942` is the `realloc` arm of the same `if`; `:1943` is `} else {`.) A
one-line citation slip, recorded because it is the kind that propagates.

▶ **The screen does not count anything.** It anchors on a **5.0.0 line NUMBER**
from the corpus citation, reads **that line's full text**, normalises it, and
looks for it in the patch's pre-image. The two sites' texts differ in the size
expression (`* (ce_num + if_num)` vs `*ce->num_interfaces`) **and** in spacing,
so they cannot be confused. ✅ **Route A is site-exact by construction; route B
was the count-based one, and the manager's *"2 occurrences at php-5.0.4, 1 at
php-5.0.5"* confusion is route B's failure mode, resolved by exactly the
distinction route A makes mechanically.**

### 4.2 ✅ F95 — **UPHELD.** `43 = 25 + 18` REPRODUCES; N10e IS **NOT** CIRCULAR; AND I MADE A MUST-FIRE NEGATIVE NOT FIRE

**`.tasks-php/preimage_screen.py --selftest` → `selftest: PASS`**, run by me.
N10e prints, computed:

```
records=170  NOT-THE-REPAIR=25  INAPPLICABLE-SAME-FILE=18  sum=43
CANDIDATE=106  INAPPLICABLE=18
```

✅ **F95's headline — *"the 43 exclusions are 25"* — reproduces exactly.**

#### ✅ IS N10e's COMPUTATION CIRCULAR? **NO.** But it traded one hardcode for a coarser one

The N10e I was told to doubt derives nothing from the call it tests. Its
expectation `43` is an **external historical constant** (F64/F68's single-label
count); the **split** `25/18` is computed from `Counter(r["verdict"] for r in
allres)` and *printed*, not asserted. The invariant half (`NOT-THE-REPAIR ⇒
decisive and file touched`; `INAPPLICABLE-SAME-FILE ⇒ not decisive, file
touched, zero hits`; `INAPPLICABLE ⇒ file not touched`) is a **structural**
partition check, not a count check. ✅ **Not circular.**

⚠ **But the repair is partial and the residue is the same class.** The comment
says the line *"used to say 26/17 … AS A LITERAL"* and is *"Computed now"* — **and
`43` is still a literal.** ▶ **The sum is the figure that will move when row 9
arrives with a new corpus record**, and then N10e fires falsely. ⓘ The honest
framing: **the STALE-PRONE quantity was moved from the split to the sum, which is
one degree more stable and not stable.**

#### ⛔⛔ AND THE MUST-FIRE NEGATIVE I MADE NOT FIRE: `same_function`'s GUARD IS **NECESSARY, NOT SUFFICIENT**

The task asks whether the guard — *"the matched hunk must contain no
function-definition header before its first changed line"* — is sufficient.
**It is not, and here is the hole, tested rather than argued.**

⭐ **The guard inspects ONLY the context lines that PRECEDE the first changed
line** (`preimage_screen.py:637-641`: the loop `break`s on the first `+`/`-`).
**If there are none, there is nothing to inspect and the function returns
`True`** — i.e. *"the commit's window PROVABLY REACHES the site"* — **on a hunk
that supplies no evidence whatever.**

**Probe: `.temp/php43/samefunc_hole.py`.** It calls `ps.same_function` directly on
synthetic hunk text against a synthetic 5.0.0 file whose cited line 4 sits in
`fn_A` and whose `fn_B` is the function actually edited:

| case | hunk | want | got | |
|---|---|---|---|---|
| 1 | the `ph53` shape — leading context crosses into `fn_B` | `False` | `False` | ✅ the guard works |
| **2** | **same situation, ZERO leading context** (`@@ -9,1 +9,1 @@ void fn_A(void)` then `-`/`+`) | `False` | ⛔ **`True`** | ⛔ **HOLE** |
| **3** | **same situation, PURE ADDITION** (`@@ -8,0 +9,1 @@ void fn_A(void)`) | `False` | ⛔ **`True`** | ⛔ **HOLE** |
| 4 | honest — the change really is in `fn_A` | `True` | `True` | ✅ not over-demoted |

⚠ **I got this wrong once and caught it**: my first run passed the hunk as a
string where `split_hunks` expects a **list of section texts**, so it iterated
characters and every case returned `False`. **The table above is the corrected
run.** Recording it because a harness that returns the answer you expect for the
wrong reason is this task's own subject.

⭐⭐ **LIVE REACH ON TODAY'S CORPUS: `0`.** Probe `.temp/php43/samefunc_reach.py`
wraps `same_function`, runs the whole screen, and counts: **43 calls · 24 returned
`True` · 137 matched hunks · 1 hunk with zero leading context · 0 records where a
`True` verdict rested on such a hunk.** ▶ **So this is a LATENT soundness gap, not
a live defect** — precisely the shape F95 itself repaired *before* it bit on more
than one record. ⛔ **It should be closed with the next `preimage_screen.py`
change, by treating `zero leading context` as "no evidence" rather than as
"no counter-evidence".** ⓘ The guard's own regex `_FUNCHEAD = ^[A-Za-z_$]` is
**permissive**, so its recall on definition headers is high and the OTHER
direction (a missed header) is not the worry — which is why the zero-context case
is the whole residual.

### 4.3 ⚠ F92 — **UPHELD-NARROWED.** THE EXPONENT AND THE F52 CONTROL REPRODUCE EXACTLY; *"HOPELESS"* IS TARGET-DEPENDENT AND THE PROBE'S OWN TABLE 7 SAYS THE CHEAP HALF

#### What I ran, and what it did

⚠⚠ **`.temp/php39/width.py --selftest` DOES NOT COMPLETE ON THIS BOX TODAY.** It
runs **19 negatives, all PASS**, then raises `ZeroDivisionError` at
`width.py:1297` inside **X3b**'s message formatting, so **X4 and the final
`SELFTEST PASS` line never print.** ▶ **And the cause is the check passing MORE
cleanly than when it was written**: X3b divides by the worst per-cell cross-session
`Ir` swing, which was `14 Ir` in the committed log and is **`0`** now. **A
validator that crashes when its own result improves.** ⓘ Not a defect in F92 —
F92's verdict does not pass through X3/X4 — but F92 cites *"`--selftest` PASS"*
and that is **no longer reproducible as stated.** Full log:
`.temp/php43/width_selftest_rerun.log`.

**PASSING in my own run** (not read from the committed log): **N5** `K == 8` at
every width with *identical* start positions `[100, 900, 1700, 2500, 3300, 4100,
4900, 5700]`; **N6** the 8 spans pairwise **disjoint** at every width (`S = 800 ≥
max W`); **N5b** 33 endpoints; **N8** all 12 binaries' `md5_fn` match the
published `results-php/<row>.json` records; **N1/N1b/X2/N2/N2b/N4/N7/N3/N3b**.
▶ ✅ **All four design guards the task names — fixed `K = 8`, fixed n-range,
disjoint spans, SD not range — HELD, and I verified each one myself.**

#### ⭐⭐ THE ATTACK: DOES THE EXPERIMENT DISTINGUISH *"THE LEVER IS WEAK"* FROM *"THE LEVER IS ABSENT AND WE ARE MEASURING SAMPLING NOISE"*?

⚠ **The question is half malformed, and saying so is the answer.** `W^(−0.5)` **IS**
the lever's mechanism — averaging `W` i.i.d. draws. *"The exponent is −0.5"* and
*"the lever is sampling-averaging and nothing more"* are the **same statement**,
not a confound. There is no separate *"absent"* hypothesis with a different
predicted exponent.

**The real confusable hypothesis is: the pipeline manufactures −0.5 out of
measurement noise.** ⭐ **That is ruled out three ways, all reproduced in my run:**

| control | what it would show if the exponent were manufactured | measured |
|---|---|---|
| **X1-L** | a fit on a series with no spread | **SD = 0 at every W and `fit = None`** — no exponent is invented |
| **X1-T** | −0.5 on a non-sampling spread | **+0.0000** over 400 series — a POSITION TREND is reported as one |
| **N3 / N3b** (`ph03`, the control row) | `ph03` showing the same law | **SD ≤ 1 % of the effect at every W, and `338×` below `ph64`'s.** A generic pipeline artefact would appear here |

✅ **And the pipeline returns four DIFFERENT answers on four synthetic truths**
(`None` / `+0.0000` / `−0.5047` / `−0.9799`), so it encodes none of them. **That is
the F52 control doing its job, and it is the strongest part of F92.**

#### ⚠ BUT THE TASK'S SUSPICION LANDS SOMEWHERE REAL: THE **ESTIMATOR IS VERY WIDE**, AND F92's TABLE HIDES HOW WIDE

Under a **true −0.5**, the 4-point `K = 8` fit's own 5–95 % band is
**`[−0.804, −0.212]`**; under a **true −1** it is **`[−1.229, −0.736]`**. They
overlap only on `[−0.804, −0.736]`. ▶ **So the experiment answers *"NOT −1"* at
better than 5 %, and *"≈ −0.5"* only as a point estimate with roughly ±0.3 of
slack. It cannot distinguish −0.5 from −0.35 or −0.65.** ✅ **That is exactly what
item 68 needs** (the decision is `−0.5`-like vs `−1`-like), so the `≈` in F92's
headline is load-bearing and correct.

⭐ **AND THE CLEANEST DEMONSTRATION OF THE ESTIMATOR'S WIDTH IS IN THE PROBE AND
NOT IN THE FINDING.** TABLE 3 gives **`ph03`, the control, THREE fits:
`−0.842`, `−0.328`, `−0.930`** — i.e. at a floor-level SD the estimator returns
values in **both** calibration bands. **F92's table prints only `−0.842` and
dashes the other two.** ▶ **Printing all three would have made the width
visible.** Presentational, not an error — but it is the line a reader needs.

#### ⛔⛔ THE NARROWING THAT MATTERS: *"WIDENING IS HOPELESS"* IS TRUE FOR ONE TARGET ON ONE ROW AND **FALSE** FOR THE OTHER TARGET EVERYWHERE

F92's heading says *"so widening `probe_iters` is HOPELESS"* with no qualifier.
Its body does qualify — *"1 % of `ph29`'s `+14.3 %` effect needs `W ≈ 6 474–17
321`, a 22–58× gate stage"* — and `STATISTICS_001 §5` repeats that, correctly
scoped. ⭐⭐ **But the probe's own TABLE 7 carries the other half, and no finding
publishes it**, under the probe's own warning *"⚠ THE TARGET MATTERS AS MUCH AS
THE EXPONENT"*:

| target | `W` needed |
|---|---|
| **`SD ≤ 1 pp` (ABSOLUTE)** | ⭐ **`W ≤ 574` on every one of the nine pairs** — `ph64` 433/574 and 378/539, `ph29` 160/147 and 195/172, and **already met at `W = 100`** on five pairs |
| **`SD ≤ 1 % of the effect` (RELATIVE)** | ⛔ **`ph29` `c-gcc` vs `safe_naive`: `17 321` (or `6 474` at an exact −0.5)**; `ph29` `safe_tuned` vs `unsafe`: `1 386`; met at `W = 100` on six pairs |

▶ **So: for an absolute 1-pp target, widening costs ≤ 6× the shipped pin and is
CHEAP. For a 1-%-of-effect target on `ph29`'s cross-language pair it costs
22–58× and is not.** **F92's unqualified *"hopeless"* is false; its body's
qualified claim is true.**

#### ✅ AND THE `NO` SURVIVES ANYWAY, ON TWO GROUNDS THE EXPONENT DOES NOT TOUCH

1. **F93's bias.** `ph29`'s pin is a **`+6.9σ` start-of-run transient** and
   widening keeps `lo = 100`, so it keeps the transient **inside** the span. **No
   exponent reaches a bias.**
2. **F91's small-Δ insensitivity** is `|B/A|` = **49.6–393.9×** — also a **bias**,
   not a variance, so averaging cannot touch it either.

▶ ⭐ **Therefore item 68's `NO` and F90's refutation do NOT reopen**, even though
F92's *"hopeless"* framing is too broad. **`STATISTICS_001 §5`'s published text is
the careful one and needs no edit; F92's heading does.**

✅ **F92's arithmetic, re-derived from `.temp/php39/sweep.log`:** six fits on the
two real rows in **`[−0.6492, −0.4045]`** (`ph64` −0.5963 / −0.6492 / −0.6336;
`ph29` −0.4045 / −0.5225 / −0.4047), `SD100/SD800` **3.16** and **2.19** against
`√8 = 2.83` for −0.5 and `8.00` for −1. **Every figure in F92's table matches.**

---

## §5 THE BOUNDED PASS — F101 · F98 · F99 deeply, F90 · F93 · F88 · F89 at the bar, F96 · F97 **UNREVIEWED**

### 5.1 ⛔⛔ F101 / item 81 — **UPHELD-NARROWED, AND ITS STATED CONSEQUENCE FOR `ph29` IS BACKWARDS**

**The direction question, which the task says the manager has not checked:**
path-sensitivity makes byte-identical things read *different*. ▶ **That is a
FALSE NEGATIVE on identity, and a false negative cannot manufacture a false
POSITIVE.**

**F77's headline is a POSITIVE identity claim** — *"`r4_fold_iter` verifies
BYTE-IDENTICALLY and is 5.63 pp cheaper"*. ▶ ⭐⭐ **A defect that can only turn
`identical` into `different` CANNOT have produced it.** Re-derived from
`patterns-php/ph29-recvfrom-alloc/controls/spellings.json`:

| variant | `kernel_fingerprint` | `verus_kernel_fingerprint` | `kernel_insns` / `verus_` | `ir_per_call_small` |
|---|---|---|---|---|
| R4 `v0_shipped` | `05d6b672b204` | `05d6b672b204` | 183 / 183 | **998.0758** |
| ⭐ R4 `r4_fold_iter` | **`d71669d3c0e6`** | **`d71669d3c0e6`** | **209 / 209** | **941.89548** |
| R4 `r4_fold_slice` | `05d6b672b204` | `05d6b672b204` | 183 / 183 | 998.0758 |

✅ **`(941.89548 − 998.0758) / 998.0758 = −5.629 %`. F77's `−5.63 pp` re-derives
to the digit, and the byte-identity is present on BOTH the digest and the
instruction count.**

⛔⛔ **SO ITEM 81's SENTENCE IS WRONG IN DIRECTION.** It says *"a path-sensitive
digest there is a **false negative on the one property that sentence rests
on**"*. **A false negative on identity cannot undermine a claim OF identity — it
can only suppress one.** ▶ **The correct statement is the opposite and it is
stronger: the defect makes F77's byte-identity HARDER to obtain, and F77 obtained
it anyway, so F77 is SAFER than it looked.**

⭐ **AND `ph29` IS STILL LIVE — I checked, and the mechanism is the FILENAME, not
the directory.** `ph29`'s `controls/spellings.py:172` puts **everything in ONE
directory** (`.temp/php35/spellings/`), but the exec source is
`{side}_{name}.rs` and the twin is `{side}_{name}_verus.rs` — **exactly 6
characters apart**, which is the *"six characters"* F101 quotes for `ph29`. ✅ So
the two compared sources really do differ in path length and the defect can fire.
**Item 81's *"LIVE on `ph29`"* is CORRECT; only its consequence is wrong.**

▶ **WHAT THE DEFECT CAN ACTUALLY HAVE COST `ph29`:** an R4 candidate whose twin
*was* byte-identical could have been wrongly refused (`ph29` pins `O3 exact`, so
`twin_identical` is a **bar** there). ▶ **That biases `ph29`'s R4 endpoint toward
being too EXPENSIVE — the conservative direction for a `fixed-R4 bound`.**
ⓘ `r4_head_array` is `in_contract: false` with `verus_kernel_fingerprint: null`
and is the only candidate that could be in that class; settling whether it was
refused for this reason needs a `ph29` build and **I did not pay for it.**

⚠ **One thing I could NOT verify: F101's claim that the digest is path-sensitive
at all.** It rests on `_042` §8's demonstration at 38 characters, which I did not
reproduce — doing so costs two builds. **The DIRECTION argument above does not
depend on it**, which is why it is the useful half.

### 5.2 ⛔⛔ F98 — **UPHELD-NARROWED, AND THREE QUALIFIERS ARE OWED. THE ROW HAS ALREADY WITHDRAWN ONE READING OF ITS HEADLINE**

**WHICH INPUT, WHICH STATISTIC — answered from the artefact.**
`controls/spellings.json`'s field is literally named **`witness_cost_pct_w1`**:

```json
"witness_cost_pct_w1": {
  "shipped_bool_array": 21.775124,
  "u32_bitmask": 9.665408,
  "note": "Per cent whole-program Ir/call above controls/r4_nowitness.rs on
           inputs/small.bin at O3/isolated ..." }
```

▶ **`+21.8 %` is: W1 (whole-program `Ir`/call) · `inputs/small.bin` · `O3/isolated`
· against `controls/r4_nowitness.rs`. NOT A1, and NOT against the C rung.**
**F98 says none of those four things.**

⛔ **QUALIFIER 1 — THE COMPARISON IS AGAINST A RUST CONTROL, NOT AGAINST THE C.**
F98 writes *"the shipped R4/R5 carry a coverage WITNESS that the C rung does not
have, and it costs `+21.8 %`"*, and *"the cost sits between R1 and R4"*. **The C
rung is not in the measurement.** The base is `controls/r4_nowitness.rs`, a
witness-free **Rust** port. ▶ **The number is the witness's cost relative to
witness-free Rust; F98 attributes it to a difference from the C.**

⛔⛔ **QUALIFIER 2 — IT IS NOT THE WITNESS'S COST ALONE, AND THE ROW DECOMPOSES IT.**
This is the F83 shape the task predicted. `controls/spellings.py:66-70`: of the
shipped witness's **+228.87 `Ir`/call** over `r4_nowitness`, **+101.59 is the
witness TEST and +127.28 is "the array being in MEMORY"**. ▶ **Only ~44 % of the
`+21.8 %` is the witness test; ~56 % is the witness array's memory traffic.**
ⓘ And the witness test costs **39.42 `Ir`/call in BOTH spellings** (12 `cmpb`
sites vs 2 `bt` sites, summing identically) — so the *test* is not where the
spellings differ at all.

⛔ **QUALIFIER 3 — THE HEADLINE'S NATURAL READING IS ALREADY WITHDRAWN BY THE ROW,
AND `RECAP_PHP.md` STILL CARRIES IT.** `NOTES.md:555` and
`controls/spellings.py:57-58`, both byte-committed: *"**The cheapest witness that
makes R4 provable costs 21.8 %**" is **withdrawn**; the measured figure is
**9.7 %***. ⚠ **The `21.775 %` itself is NOT withdrawn** — the row says so
explicitly — *"It is a correct measurement of the SHIPPED witness spelling. What
was wrong was calling it the cheapest."* ▶ **But F98's heading reads `— +21.8 %`
as the price of making R4 verifiable, and that reading is the withdrawn one.**
⚠⚠ **Item 73 again: the withdrawal is in the ROW and the superseded reading is in
the FINDING HEADLINE and in `RECAP_PHP.md:288`'s index.**

⭐⭐⭐ **AND HERE IS WHERE §1's RULING PUTS IT BACK.** The `+9.67 %` figure is
`u32_bitmask` — i.e. **`r4_bitmask`, which reading (a) puts OUT OF CONTRACT**
(§1.3). ▶ **So under the item-83 ruling the correct sentence is: *the cheapest
IN-CONTRACT witness costs `+21.775 %` (W1, `small.bin`, `O3/isolated`, against
`controls/r4_nowitness.rs`), and `+9.67 %` is what a respelling OUTSIDE this
row's contract would buy.*** ⭐ **Two of this report's sections push in opposite
directions and the combination is coherent — that is the check, not a
coincidence.**

### 5.3 ✅ F99 — **UPHELD.** EVERY NUMBER RE-DERIVES, AND THE INTERSECTION HOLE IS REAL IN THE **OTHER** DIRECTION

**`.tasks-php/citecheck.py --selftest` → `SELFTEST PASS`**, N1 · N1b · N1c · N2 ·
N3 · N4, run by me. Full run:

| F99's claim | measured today | |
|---|---|---|
| **9** `.temp/` citations inside hashed `spec.md`, **6 of 8 rows** | **8, across 5 rows** — `ph00`×1, `ph03`×3, `ph07`×1, `ph16`×1, `ph45`×2 | ✅ **F99 EXACTLY RIGHT; the delta is its own round's repair.** `N1c` asserts `ph53` now carries none and names `_042` as the repairer. `9 − 1 = 8`, `6 − 1 = 5` |
| **3 already GONE** | ✅ **3, and the same three** — `ph03/NOTES.md → .temp/php13/bin`, `ph07/NOTES.md → .temp/php16/tb`, `ph45/NOTES.md → .temp/php36/bin` | ✅ ⓘ **all three are in `NOTES.md`, NOT in a hashed contract** — F99's table has them on a separate row and is right to; a reader could merge them |
| **3 inherited** from the shared `why` | ✅ **3** — `.temp/p05r3/v16/tuned_split.rs`, `.temp/p05r3/v17/tuned_suffix.rs`, `.temp/p19/pins.py` | ✅ |
| ~90 in `NOTES.md` across all 8 | not counted exactly; the report is long and consistent with it | ⓘ **UNTESTED** |

#### ⭐⭐ THE `inherited = set.intersection(*per_spec.values())` QUESTION — THE TASK'S DIRECTION FAILS **LOUD**; THE OTHER ONE FAILS **SILENT**

**The ADD direction (the task's):** a new row whose `spec.md` lacks one of the 3
shared citations shrinks `inherited`, and that citation reclassifies to
row-specific and is reported **once per row that has it**. ▶ ✅ **This fails
LOUD** — it produces 7–8 extra warnings, and the underlying fact (*the shared
block is no longer shared*) **is a real defect worth an alarm**, namely the
partial-amendment accident `check.py`'s `NAMED_SPELLING_SHA256` exists to catch.
**Noisy, correctly-alarming, acceptable.**

⛔⛔ **THE UNHANDLED DIRECTION IS THE OPPOSITE ONE, AND IT FAILS SILENT.**
`set.intersection(X) == X`. ▶ **If `glob.glob('patterns-php/*/spec.md')` ever
matches exactly ONE row, `inherited` becomes that row's ENTIRE citation set and
every one of its citations is SUPPRESSED as *"inherited by all 1 rows"*.**
Demonstrated (`python3 -c`, one line): with `per_spec = {'only/spec.md':
{'.temp/a','.temp/b','.temp/c'}}`, `inherited` = all three **and `N2` still
passes** — `N2` asserts only `len(inherited) >= 1` and *all present in all rows*,
both trivially true at n = 1. ⚠ The glob is **relative with no cwd guard**, so
this is reachable by running the checker from the wrong directory, not only by
deleting rows. ▶ **The repair is one line: require `len(specs) >= 2` before
computing `inherited`, and assert it in `N2`.** ⓘ F99's *"the split is MECHANICAL,
and it had to be"* is right about the *design*; this is the degenerate case the
mechanism does not guard.

### 5.4 ✅ F90 — **REFUTED** (already), AND THE STRUCK RECORD IS CORRECT — with one residue

✅ **The refutation is stated at the TOP of F90** under *"READ THIS FIRST"*, names
F92 and the `W^(−0.5)` measurement, separates **UPHELD** (`probe_iters` is a
parameter) from **REFUTED** (*"the cheaper and better fix is to RAISE it"*), and
says *"The section below is left as written"*. ✅ **Correctly recorded.**

**Does it still read as live anywhere?** Swept every `.md` outside `.temp/`,
`.git/`, `.web/`. ⚠ **One residue, and it is item 73's shape:**
`.tasks-php/STATISTICS_001.md:14-15` — the document's **OPENING BOX** — still
reads *"**F88, F89 and F90 have not been reviewed at all**, and F90 **disagrees
with the reviewer**"*, and its settlement sits at `:159`, **145 lines later**. ▶ **A
reader who stops at the box gets the superseded state from the document
`RECAP_PHP.md:82` calls *"the whole argument"*.** ⓘ `:135`'s *"**F90
disagrees**"* is the same thing 24 lines above its own answer. ⚠ One more
mis-citation found in passing, historical and not live:
`TASK_PHP_039_REPORT.md:551` attributes *"C is blind to `main`"* to **F90**;
`STATISTICS_001 §2` and `RECAP_PHP.md:2465` attribute it to **F84 as corrected by
`_038` §4.2**.

### 5.5 ✅ F93 — **UPHELD.** `z = +6.91` RE-DERIVES EXACTLY

**(i) The number, from `.temp/php39/sweep.log:419`:**
`ph29  c-gcc vs safe_naive   17.852   14.649   0.4633   6.91   1/8` — pin
**17.852**, mean of the other seven disjoint W=100 spans **14.649**, their SD
**0.4633**, **z = +6.91**, and the pin is the extreme in **1 of 8**. ✅ Offset
`3.203 pp` against N7a's measured effect `15.0483 %` = **21.3 %**, matching F93's
*"21 % of the effect"*. **`ph64` +1.76 and `ph03` +0.60…−1.23 do not fire.**

**(ii) Scoping:** `ph29` · `c-gcc vs safe_naive` (and `c-gcc vs safe_tuned` at
+3.31) · `small.bin` · `O3/isolated` · `W = 100` · 8 disjoint spans. **One row,
two pairs.** ⭐ Its declared two-part floor (`|z| ≥ 3` **and** offset > 1 % of the
effect) is F89's own outlier misfire repaired, and it holds: `ph03`'s near-zero
SDs do not produce a fire.

**(iii) UPHELD.** ⓘ I did not re-derive the *decay with n* half.

### 5.6 ✅ F88 — **UPHELD** (and already narrowed in place by F93)

**(i)** `ph29`'s level spread, from `.temp/php39/sweep.log:322` — an
**independent** sweep (K = 8 disjoint spans out to n = 6500, where F88 used
`mgr173`'s 9 consecutive spans): `safe_naive` levels
`1657.0 · 1448.3 · 1774.5 · 1670.0 · 1280.0 · 1689.9 · 1561.1 · 1509.9`, mean
**1573.84**, range **494.5**. ▶ **`range/mean = 31.42 %`** against F88's
published **32 %**. ✅ And `ph03`'s control reproduces at **0.02–0.03 %** on all
four cells, exactly as F88's own narrowing note claims.
⚠ **Two normalisations are in play and neither document says which**: the
probe's own `spread %` column is **`range/min` = 38.63** for the same cell.
**32 % is `range/mean`; 38.6 % is `range/min`. 7 pp apart.**

**(ii)** Scoping: `ph29` · `safe_naive` · `small.bin` · `O3/isolated` · family
**B**. The claim is about a **cell's own B level**, not about a ratio.

**(iii) UPHELD.** ⓘ The narrowing already in the record (F93: *"largest because
it is EARLIEST"*) is confirmed by §5.5.

### 5.7 ⚠ F89 — **UPHELD-NARROWED.** THE CONTRAST REPRODUCES BY A DIFFERENT DESIGN; THE TWO PUBLISHED NUMBERS DO NOT COMPARE DIRECTLY

**(i)** `width.py`'s **N4**, run by me: `ph64/small.bin` at `W = 100`, **K = 8
disjoint** spans — cross-language (`c-gcc` vs `safe_naive`) **SD 2.3951 pp /
range 7.3306 pp**; same-language (`safe_tuned` vs `unsafe`) **SD 0.0431 pp /
range 0.1365 pp**. **Measured factor 55.6× against a declared floor of 10×.**
✅ **F89's direction and order of magnitude reproduce on an independent span set.**

⚠⚠ **(ii) BUT THE NUMBERS DO NOT LINE UP AND I WANT THAT ON THE RECORD.** F89
published **8.12 / 8.63 pp against 0.07 pp**, **as RANGES over 9 consecutive
spans from n = 100**; my re-derivation is **ranges over 8 disjoint spans spread to
n = 6500**. Cross-language: **7.33 vs 8.12** — close. Same-language: **0.1365 vs
0.07 — 1.95× apart**, which the `K = 9 → 8` change in `E[range] = d(K)·σ` (2.970
→ ~2.847, a 4 % effect) **does not explain.** ▶ **The span sets are different
populations and the same-language figure is the one that moves.** ⓘ Not a
refutation — the ratio `8.63/0.07 = 123×` and my `7.33/0.1365 = 54×` both clear
any floor — **but F89's `0.07 pp` should not be quoted as *the* same-language
spread.** ⭐ And the record already carries half of this: F88's narrowing note
says *"F89's spread figures were RANGES, not SDs, which nothing said at the
time."*

**(iii) UPHELD-NARROWED.**

### 5.8 ⛔ F96 and F97 — **UNREVIEWED**

**I did not review these and I am not going to pretend otherwise.** Neither has a
cheap second method available to me at this point.

* **F96** (*row 7 is built, 3 of 4 predictions refuted*) is a **build record plus
  a prediction ledger**; checking it means re-reading four pre-registered
  predictions against the built row, which is a task's worth of work. ⓘ **One
  fragment of it is checked elsewhere in this report**: §1 and §5.2 confirm the
  `r4_bitmask` / witness figures it rests on, and §3.5 argues its result 2
  (item 78's premise) is **not evidence for the rival**. That is not a review of
  F96.
* **F97** (*two sound gate rules are jointly unsatisfiable for a `MaybeUninit`
  read*) is a **Verus-side argument** requiring `verus_run.py` invocations and a
  reading of `controls/r4_nowitness.rs`'s error text. ⓘ F100's item-79 arms
  (`mu_ref.rs` **8/0**, `mu_ref_cmp.rs` a must-FIRE refusal) are cited as turning
  it *"from an argument into a MEASURED FLOOR"*, and **that is exactly the claim
  a reviewer should attack** — I have not.

---

## §6 ⛔ WHERE MY DEPTH RAN OUT, EXACTLY

**It ran out after §5.7.** §§1–4 are done to the task's bar. §5's three named
cheap attacks (F101, F98, F99) are done deeply. F90, F93, F88, F89 are done to
bar (i)–(iii). **F96 and F97 are UNREVIEWED.**

**What I would do next, in order, if this were `TASK_PHP_044`:**

1. **F97**, because it is the one remaining finding whose subject is a *gate rule*
   rather than a number, and because F100 promotes it from argument to measured
   floor on the strength of three arms nobody has re-run.
2. **F96's four predictions**, read against the built row, one at a time.
3. **F101's own premise** — reproduce the path-sensitivity at 38 characters. Two
   builds. §5.1 shows F77 is safe *without* it, but item 81's repair cost depends
   on it being real.
4. **Whether `ph29`'s `r4_head_array` was refused by the F101 defect.** One build.

---

## §7 ⭐ WHAT I AM UNSURE OF

1. ⚠⚠ **§1.4's English-scope transcription is MINE, by hand, from `spec.md`.**
   The exclusion sets in §1.3's "every required entry" column depend on my
   reading that `required[0]` scopes to `{R3, R4}`, `required[1]` to `{R4}`,
   `required[2]` and `required[4]` to `{R4}`. **No gate stage reproduces this —
   `check.py`'s own docstring says so in terms.** If I have mis-scoped
   `required[0]`, §1.4's second instance evaporates. ▶ **§1.3's PRIMARY result
   (the R4 endpoint degenerates) does NOT depend on it** — it needs only
   `required[4]` scoped to R4, which the entry states in so many words.
2. ⚠ **I did not re-run `ph53`'s `controls/spellings.py`.** §1.3 re-computes the
   verdicts from the COMMITTED `spellings.json` through the row's own functions.
   If the committed JSON is itself wrong, my simulation inherits it. **N1 of my
   selftest checks only that I reproduce what was published, which is exactly the
   thing that cannot catch that.**
3. ⚠⚠ **The `invariant` ruling (§1.5) rests on an English judgement.** I give
   both readings and say which makes it falsifiable. **A reader who takes
   *"in contract BY X OVER Y"* as procedural will say the clause is true and I am
   wrong.** I do not think that reading survives the word `invariant`, but it is
   a reading.
4. ⚠ **§3's rival-refutation argument 1 (*"a flip entails divergence"*) is
   logical, not measured** — though `N7` checks its numeric consequence (`a·b < 0`
   on all 38). **If `marginal_ir_per_call` is not a whole-program quantity on
   some cell, the entailment fails there.** I did not audit that per cell.
5. ⚠⚠ **§3.5's claim that all nine of F91's Result-5 cells are same-language
   rests on F91's own sentence** *"`Δnopad` exists only for the `unsafe vs verus`
   pair"*. **I did not independently verify that `Δnopad` is unavailable for a
   cross-language pair.** If it is available, the fifth table row might contain
   cross-language cells and §3.5's argument weakens.
6. ⚠ **§2.6's pre-search predicate is validated on n = 2 and I refuse to threshold
   it.** The two values are `0.095` and `0.895`. **That is two points.**
7. ⚠ **F101's underlying premise is UNVERIFIED by me** (§5.1). I verified the
   *direction* argument and the `ph29` 6-character mechanism; I did not reproduce
   the digest difference itself.
8. ⚠ **F92's `width.py --selftest` does not complete on this box** (§4.3), so X4
   and the final verdict line are read from the **committed log**, not from my own
   run. 19 negatives I ran myself; X4 I did not.
9. ⚠ **I nearly published two wrong results from harness bugs of my own.** The
   `same_function` test returned the expected answer for the wrong reason until I
   found I was passing a string where a list was wanted (§4.2); and I read
   `cheapest_r4_in_contract = None` on `ph29` as an inconsistency before finding
   **the key does not exist in that file at all** — trap 5's shape, an absent key
   read as a null value. **Both caught; I cannot promise there is not a third.**
10. ⚠ **The `+101.59 / +127.28 Ir`/call decomposition in §5.2 is quoted from
    `controls/spellings.py`'s docstring, not re-measured.** It is the load-bearing
    number for qualifier 2.
11. ⚠ **I did not count F99's *"~90 `NOTES.md` citations"*.** Reported as
    UNTESTED.
12. ⚠ **`flip_columns.py`'s `N5` FAILS** (28 vs 29). I judged it a stale hardcode
    against a published correction. **If instead the 29 is wrong and 28 right,
    §3.2's count becomes 10 and the task file was right** — but `RECAP_PHP.md`
    records *"29, not 28"* as the correction, so I went with 29.
13. ⚠ **§1.8's drafted replacement sentence is a DRAFT.** I have not checked that
    it leaves `contract_sha256`'s JSON parseable or that no other entry's English
    now contradicts it.
14. ⚠ **I did not check whether the item-83 ruling has consequences for `ph45`,
    `ph16`, `ph07` or `ph29`'s published endpoints.** §1.6 shows their
    `required_absent` never separates a challenger from its own shipped rung, so
    I believe the answer is no — **but "never separates" is a weaker statement
    than "no endpoint moves", and I checked the former.**

---

## §8 ⛔⛔ THE COVERAGE TABLE — EVERY ONE OF F88–F101, EXACTLY ONE VERDICT EACH

**This is the deliverable the manager routes off. 9 verdicted, 5 UNREVIEWED.**

| finding | verdict | one line |
|---|---|---|
| **F88** | ✅ **UPHELD** | `ph29`'s 32 % re-derives as `range/mean = 31.42 %` on an **independent** 8-span sweep; `ph03` control at 0.02–0.03 %. ⚠ two normalisations in play (31.4 % vs 38.6 %), neither document says which. §5.6 |
| **F89** | ⚠ **UPHELD-NARROWED** | the same-language/cross-language contrast reproduces at **55.6×** by a different design; ⚠ **F89's `0.07 pp` is 1.95× from my `0.1365 pp`** and the two span sets are different populations, so `0.07` must not be quoted as *the* same-language spread. §5.7 |
| **F90** | ⛔ **REFUTED** (confirmed) | the struck record states the refutation correctly, at the top, splitting UPHELD from REFUTED. ⚠ residue: `STATISTICS_001.md:14-15`'s **opening box** still reads it as live, 145 lines before its own settlement. §5.4 |
| **F91** | ⚠ **UPHELD-NARROWED** | ✅ `\|B/A\|` **49.6–393.9×** does **NOT** depend on the `ph45` misreading — verified from the table's own population (`Δnopad`, `unsafe vs verus`, 9 cells, zero respellings). ⛔ **But its AXIS is refuted as a general statement**: all nine of its own cells are *same-language* and separate by `\|Δ\|` magnitude, so *"same-language ⇒ only A resolves it"* is false by its own fifth table row. §2.5, §3.5 |
| **F92** | ⚠ **UPHELD-NARROWED** | exponents `[−0.6492, −0.4045]`, the F52 control (`None`/`+0.0000`/`−0.5047`/`−0.9799`) and all four design guards reproduced by me. ⛔ *"hopeless"* is target-dependent: the probe's own TABLE 7 gives `W ≤ 574` for an **absolute** 1-pp target on every pair. ✅ The `NO` survives on F93's bias and F91's bias regardless. ⚠ `--selftest` no longer completes. §4.3 |
| **F93** | ✅ **UPHELD** | `z = +6.91` re-derives exactly (`sweep.log:419`), offset 21.3 % of the effect, declared two-part floor holds and does not fire on `ph03`/`ph64`. Scope: one row, two pairs. §5.5 |
| **F94** | ⚠ **UPHELD-NARROWED** | the exclusion of `be8daf1f47fa` **stands by the tag walk**; ⛔ **the screen route is GONE** — F95's own guard demoted that record to `INAPPLICABLE-SAME-FILE`, which the screen prints as *"NOT exclusions … says nothing about these"*. ***"REFUTED TWICE INDEPENDENTLY"* must become *"REFUTED ONCE"*.** ✅ The two routes are **not** the same evidence twice, and the screen **does** disambiguate the two `erealloc` sites (by 5.0.0 line number + full text). ⚠ the inheritance-merge line is `:1944`, not `:1945`. §4.1 |
| **F95** | ✅ **UPHELD** | `43 = 25 + 18` reproduces exactly; `--selftest PASS`; N10e is **not** circular (its `43` is an external historical constant, the split is computed). ⚠ the `43` is still a hardcode and will move at row 9. ⛔ **And the `same_function` guard is NECESSARY, NOT SUFFICIENT** — I made it accept a zero-leading-context hunk as proof, **live reach `0`**, latent. §4.2 |
| **F96** | ⛔ **UNREVIEWED** | a build record plus a four-prediction ledger; no cheap second method. One fragment checked in §3.5 (its result 2 is not evidence for item 78's rival). §5.8 |
| **F97** | ⛔ **UNREVIEWED** | needs `verus_run.py` and `controls/r4_nowitness.rs`'s error text. F100 promotes it to a *measured floor* on three arms I did not re-run. §5.8 |
| **F98** | ⚠ **UPHELD-NARROWED** | the statistic is **W1**, the input **`small.bin`**, the level **`O3/isolated`**, the base **`controls/r4_nowitness.rs`** — and **F98 states none of the four.** ⛔ the comparison is **not against the C**; ⛔ only **~44 %** (+101.59 of +228.87 `Ir`/call) is the witness, the rest is the array in memory; ⛔ and the row has **already withdrawn** the *"cheapest witness"* reading. ⭐ §1's ruling **restores `21.775 %` as the in-contract figure.** §5.2 |
| **F99** | ✅ **UPHELD** | `9 → 8` and `6 → 5` rows, and the delta is its own round's `ph53` repair; the **3 already-GONE** paths are the same three. ⛔ new: the `set.intersection` split **fails SILENT at one row** (all citations suppressed, `N2` still passes) — the task's ADD direction fails LOUD and is acceptable. §5.3 |
| **F100** | ⚠ **UPHELD-NARROWED** | ⛔ **the *"BOTH ENDPOINTS MOVE"* headline loses its R4 half** — item 83 rules **(a)**, `r4_endpoint_degenerate → true`, and every remaining in-contract R4 variant is **DEARER** (+0.50…+33.92 %). ✅ The **R3** half (−32.08 %), the 281.8 `Ir`/call window-check mechanism, the `r4_bitmask_min` smaller-surface result (now a *control*-class result) and the A1-spread result **all survive**, each checked separately. ✅ All six published A1 percentages re-derive to the digit. §1 |
| **F101** | ⚠ **UPHELD-NARROWED** | ✅ *"LIVE on `ph29`"* is **correct** and the mechanism is the **filename**, 6 characters (`_verus`), inside one build directory. ⛔ **Its stated consequence is BACKWARDS**: a false negative on identity cannot undermine F77's claim **of** identity, and `r4_fold_iter`'s digests are **equal** (`d71669d3c0e6`, 209/209) with `−5.629 %` re-derived. **F77 is SAFE, and the defect's direction is why.** ⚠ I did not reproduce the path-sensitivity itself. §5.1 |

### ▶ WHAT MAY ENTER `.memory-php/` ON THIS REVIEW

| | |
|---|---|
| ✅ **eligible, as written** | **F93 · F95 · F99** (plus **F90** as a struck record) |
| ⚠ **eligible ONLY with the narrowing in the same sentence** (item 73: **apply, do not append**) | **F88 · F89 · F91 · F92 · F94 · F98 · F100 · F101** |
| ⛔ **NOT eligible — rule 9's cycle is still open** | **F96 · F97** |

### ▶ THE EDITS THIS REVIEW IMPLIES, PRICED

| | what | cost |
|---|---|---|
| 1 | `ph53` `spec.md` `required[4]` (§1.8) **+** `controls/spellings.py`'s `ENGLISH_VERDICTS` **+** `r3_no_capacity` **+** the `invariant` clause | ⛔ **ONE `ph53` re-gate, NO re-measure.** Land them together or the row goes out inconsistent |
| 2 | the `invariant` clause in `ph07` · `ph16` · `ph29` · `ph45` | **one re-gate each**; batch with each row's next |
| 3 | `.tasks-php/STATISTICS_001.md:50` (§2.3) and its **opening box** `:14-15` (§5.4) | ✅ **free** — not hashed, in no digest |
| 4 | `RECAP_PHP.md`: F100's R4 half · F94's *"twice"* · F98's four qualifiers · F101's direction · item 81's consequence · item 83 **closed** · item 82 **closeable** · item 78 **answered** | manager-only, free |
| 5 | `preimage_screen.py`'s zero-context guard · `citecheck.py`'s `len(specs) >= 2` · `flip_columns.py`'s `N5` 28→29 · `width.py`'s X3b divide-by-zero | ✅ free, **each with its must-fire negative** (§H) |

---

## §9 BRACKETS — LAST

Re-run after all work, with nothing edited outside `.temp/php43/` and this file:

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE
$ python3 harness-php/gate.py --tool measure --check-stale
16 record(s) examined, 0 STALE
```

**`66/0` and `16/0` — UNMOVED, first and last.** ✅ **Zero re-gates, zero
re-measures caused by this task.** `git status` over `patterns-php/`,
`results-php/`, `harness/`, `harness-php/`, `common-php/` and `.memory-php/` is
**empty**; the only new files are `.tasks-php/TASK_PHP_043_REPORT.md` and four
probes under `.temp/php43/`.

### Probes written, all re-runnable

| file | `--selftest` | what it is for |
|---|---|---|
| `.temp/php43/item83_sim.py` | ✅ **PASS**, 4 negatives | §1.3 — simulates reading (a) through `ph53`'s OWN verdict functions; builds nothing |
| `.temp/php43/item78_cell.py` | ✅ **PASS**, 7 negatives | §3 — the missing 2×2 cell from the 38 flips already on disk; zero measurement |
| `.temp/php43/samefunc_hole.py` | n/a (is itself the negative) | §4.2 — makes `same_function`'s must-fire guard NOT fire |
| `.temp/php43/samefunc_reach.py` | n/a | §4.2 — live reach of that hole on the real corpus: **0** |

ⓘ Also `.temp/php43/width_selftest_rerun.log` (the crash, §4.3) and
`.temp/php43/req4.txt` (the extracted `idiom.required` entries, §1.1) and
`.temp/php43/ph53_why.txt` (the full 18 367-byte `idiom.why`, §1.2). **No
binaries, no `.o`, no `.pyc`, no `__pycache__` produced; nothing to delete.**
