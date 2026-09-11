# TASK_PHP_033 — report

**Role:** research engineer, alone.

> ## HEADLINE — **STAGE A COMPLETE AND GATE-GREEN. STAGE B NOT COMPLETE.**
>
> **Stage A**: `ph29`'s `required[0..3]` are backticked in both language keys
> with the two respellings and the new English, §2.5's correction is landed, and
> the row re-gates **`PASS`**. **All eight of §2.7's predicted numbers came out,
> first try, with the two absences exactly where predicted.**
> ⚠⚠ **That verdict is read out of `results-php/gate/ph29-recvfrom-alloc.json`**
> — `verdict: PASS`, `failures: []`, `complete_run: true` — **and not out of a
> log or out of a gate that was still running.** It took three gate-chain
> commands: gate (FAIL on `[tables]`, as predicted), `--tool report`, gate (PASS).
>
> **Stage B is DEFERRED, and §6 says why in full.** What it has is groundwork,
> in `.temp/php33/`, and it is **not** the discharge: **no `controls/spellings.py`
> and no `controls/spellings.json` were written, and no Verus twin verifies, so
> every R4 figure in §4 is a CONTROL and not a rung and NO BOUND MAY BE PUBLISHED
> OFF IT.** What the groundwork does buy is §4's mechanism, which closes exactly
> against the measured gap, and §5's answer to the one question that decides the
> row.

**Brackets.** `harness/measure.py --check-stale` → **66 / 0** and
`harness-php/gate.py --tool measure --check-stale` → **12 / 0**, first (before
anything was touched) and last. Both agree with the task file's figures.
⭐ **No measurement record moved and no re-measure was needed** — `spec.md` is
not among `measure.py`'s 19 pinned sources — so the cost was **two gate rounds
and one render**, and `results-php/ph29-recvfrom-alloc.json` is still `FRESH`.

**What landed**

| | |
|---|---|
| `patterns-php/ph29-recvfrom-alloc/spec.md` | the only file I edited. `idiom.required[0..3]` × 2 language keys backticked; `required[0]` and `required[1]` gained English; `forbidden[0]`'s closing sentence corrected (§2.5) |
| `results-php/gate/ph29-recvfrom-alloc.json` | the gate's own output — `PASS` |
| `results-php/tables/ph29-recvfrom-alloc.md` | the gate's own re-render |
| `results-php/preflight/ph29-recvfrom-alloc.preflight.json` | the preflight's own append |
| `.temp/php33/` | scratch: 5 probes, 6 logs, `NOTES.md` as the index. **456 KB, every blob deleted, every file a generator or a log** |

`git status --porcelain` at the end shows **exactly those four tracked paths and
nothing else**.

**Not touched:** any rung `.rs`, `NOTES.md`, `README.md`, `model.py`,
`inputs/`, `controls/`, `harness/`, `common/`, `patterns/`, `results/`,
`pilot/`, `.web/`, `RECAP_PHP.md`, `.memory-php/`, `ph03`, `ph07`, `ph16`,
`ph64`, `ph00-smoke`. No `git add`, no `git commit`, no `/tmp`.

---

## §1 THE THREE PROBES, RUN BEFORE ANYTHING WAS EDITED — §4 item 1

All three `--selftest` **PASS**, verbatim:

```
$ python3 .temp/mgr169/ph29_pins.py --selftest
selftest: PASS (0 failure(s))

$ python3 .temp/mgr169/charlit_reach.py --selftest
selftest: PASS (0 failure(s))
```

Bare runs:

```
$ python3 .temp/mgr169/ph29_pins.py
SUMMARY  7 candidate(s) would pin at least one rung, 1 would pin nothing, 2 are propositions.

$ python3 .temp/mgr169/charlit_reach.py
=== PAT  patterns/  (33 rows scanned) ===
  no declared spelling contains blankable text
  -> 0 affected spelling(s), 0 of them `forbidden`
=== PHP  patterns-php/  (6 rows scanned) ===
  no declared spelling contains blankable text
  -> 0 affected spelling(s), 0 of them `forbidden`

$ python3 .temp/mgr169/ph29_predict.py
key                             committed    now  PREDICTED
spellings                               4      4         12
forbidden_spellings                     4      4          4
pairs                                  12     12         36
present                                 0      0         22
required_pins_nothing                   0      0          0
required_absent                         0      0          2
forbidden_hits                          0      0          0
forbidden_unaudited_entries             2      2          2
no_rung_entries                         0      0          0
```

⭐ **`committed` and `now` agree on all nine keys**, so the tree had not moved
under the decision. Nothing in §1 was contradicted by anything I found.

I also re-derived §2.1's and §2.2's line-level claims independently before
editing (`.temp/php33/pin_lines.py`), because §2.1 asks for line level and not
rung level. **Every one of them holds**, and the probe carries a straddle guard
so a span spread over two lines could not pass as a single-line pin:

| span | rungs | line(s) |
|---|---|---|
| `` `.wrapping_add(1)` `` | all four Rust | `safe_naive:100`, `safe_tuned:64`, `unsafe:88`, `verus:450` — **one each** |
| `tr.wrapping_add(1)` (the rejected spelling) | **2 of 4** | `unsafe:88`, `verus:450` only — the two safe rungs would have been out of contract |
| `` `read_buf[recvd] =` `` | both C | `kernel.c:247`, `kernel_hardened.c:175` — **one each** |
| `read_buf[recvd] = '\0'` (the rejected spelling) | **none** | 0 occurrences — the char-literal blind spot, confirmed |
| `` `emalloc(to_read + 1)` `` | both C | `226` / `160` |
| `` `php_shim_tally()` `` | both C | `271` / `189` |
| `` `php_shim_reset` `` | both C | `199` / `131` |
| `` `1000039` `` | all four Rust | `72` / `43` / `156` / `546` |
| `` `real_size` `` | all four Rust | **7 / 7 / 3 / 3 occurrences** — §2.4's weak pin, confirmed weak |
| `` `vset_unchecked(&mut read_buf, recvd, 0)` `` | **2 of 4** | `unsafe:129`, `verus:500` |

⚠ `.wrapping_add(1)` does **not** also catch `.wrapping_add(1000039)`: the fold
constant is on a different line in every Rust rung and the closing paren keeps
the span off it. Checked, not assumed.

---

## §2 STAGE A — THE EDIT, AND THE §2.7 PREDICTION BESIDE THE RESULT

`contract_sha256` moved
`28a92facffb331484bd1e708e8a1c6696b27b479c91d976515a8ec01dbb6bcf6`
→ `a5dfc7d473a223251e8c8c5e7e9a06e714679291447b3efe6b3ace19db20c38f`.

### 2.1 The eight numbers, predicted against measured

**Read out of `results-php/gate/ph29-recvfrom-alloc.json` after the green run:**

| key | committed | §2.7 PREDICTED | **MEASURED** | |
|---|---:|---:|---:|---|
| `spellings` | 4 | **12** | **12** | ✅ |
| `forbidden_spellings` | 4 | 4 | **4** | ✅ |
| `pairs` | 12 | **36** | **36** | ✅ |
| `present` | 0 | **22** | **22** | ✅ |
| `required_pins_nothing` | 0 | 0 | **0** | ✅ |
| `required_absent` | 0 | **2** | **2** | ✅ |
| `forbidden_hits` | 0 | 0 | **0** | ✅ |
| `forbidden_unaudited_entries` | 2 | 2 | **2** | ✅ |

```
absent: [('required[1]', 'rust', 'safe_naive.rs'), ('required[1]', 'rust', 'safe_tuned.rs')]
```

**Both absences are exactly the ones §2.7 predicts**, i.e. the one genuine scope
of §2.3. **No number was adjusted to make the prediction come out**; the
declaration was written once, checked against the shipped `idiom_audit` in
memory (`.temp/php33/check_edit.py`), and gated. It came out green on the first
attempt in both.

⚠ **The numbers are NOT the naive column** (`present 20`, `required_absent 4`,
one dead pin), so the two respellings did what §2.1 and §2.2 say they do.

### 2.2 The gate chain, and each verdict read out of the record

| | command | verdict | where read |
|---|---|---|---|
| 1 | `harness-php/gate.py ph29-recvfrom-alloc` | **FAIL**, 2 failures, **both `[tables]`** | `.temp/php33/gate1.log`, and `results-php/gate/…json` `verdict: FAIL` |
| 2 | `harness-php/gate.py --tool report ph29-recvfrom-alloc` | rc 0, `wrote results/tables/ph29-recvfrom-alloc.md` | `.temp/php33/report.log` |
| 3 | `harness-php/gate.py ph29-recvfrom-alloc` | **PASS** | `.temp/php33/gate2.log`, and the record below |

Round 1's two failures were `results/tables/…md is STALE: it cites contract
['28a92facffb3'] and spec.md's slb-contract block now hashes to a5dfc7d473a2`
and `STALE IN ITS CONTENT: 28 line(s) differ`. **That is exactly what
`PROTOCOL_PHP.md` §E's `gate → report → gate` chain predicts for a
`contract_sha256` move**, and nothing else failed in either round.

The final record:

```
verdict       PASS
failures      []
complete_run  True
contract      a5dfc7d473a223251e8c8c5e7e9a06e714679291447b3efe6b3ace19db20c38f
controls_json {}
```

### 2.3 What the edit says, per entry

* **`required[0].c`** `` `emalloc(to_read + 1)` `` + new English: binds all six
  rungs, names the two C lines, and records that the entry carried no English
  at all before.
* **`required[0].rust`** `` `.wrapping_add(1)` `` + new English: binds all four
  Rust rungs, names the two spellings the rungs actually use **without
  backticks**, says so explicitly, gives the four line numbers, and records that
  the line-level check was done because `idiom_audit`'s docstring names
  substring matching as a false-positive shape.
* **`required[1].c`** `` `read_buf[recvd] =` `` + new English: the fault line and
  its hardened twin, the matcher artefact, the writing rule (*never backtick a
  character literal*), the explicit statement that this is **not** a bug report
  against `harness/`, and the latency measurement (0 of 33 PAT + 0 of 6 PHP).
* **`required[1].rust`** spelling kept + **the scoping sentence §2.3 asks for**:
  R4/R5 only, what the safe rungs write instead (**without backticks**), why
  per-language keys cannot express it, and that the two absences are the
  declaration working rather than failing.
* **`required[2].c/.rust`, `required[3].c/.rust`** — backticks only, prose
  untouched. `required[3].rust`'s `real_size` is **left weak on purpose**
  (§2.4): not respelled, not strengthened. **It is a bare identifier occurring
  3–7 times per rung and it pins "this name occurs", not a construction** —
  recorded here so nobody later reads it as a tight pin.
* **`forbidden[0]`** — the false sentence corrected per §2.5, with no backticks
  added.

⚠ **Every new sentence is backtick-free apart from the one leading pin**, which
is what keeps `spellings` at 12 and not higher. That was checked by running the
shipped `idiom_audit` before the gate, not by inspection.

---

## §3 ⚠⚠ WHAT I FOUND THAT THE TASK FILE DOES NOT SAY — §4 item 7

### 3.1 ⭐ THE §2.6 TRAP HAS A SIBLING, IT IS ON THIS ROW ALREADY, AND I WALKED INTO IT

§2.6 asks for a cheaper way to make the backtick trap unmissable, and warns it
has now bitten three readers. **There is a second trap of the same family on
this exact row and the task file does not mention it, and my first draft of the
edit hit it.**

I wrote the new English into a **`"note"` key** beside `c` and `rust`, because
that read like the natural home for prose that is not a spelling. `idiom_problems`
refuses **any** key outside `IDIOM_LANGS`:

```python
bad = sorted(set(e) - set(IDIOM_LANGS))
if bad:
    probs.append(f"idiom.{k} entry has unknown language key(s) {bad}; ...")
```

so it would have **hard-failed the gate**. I caught it by reading
`idiom_problems` before running, not by running.

⚠⚠ **And this row has already paid for it once.** `NOTES.md` §12 item 0:

> **Two `idiom.required` entries carried a `why` key.** The gate's schema admits
> only `c` and `rust`, so **that text pinned nothing in either language** while
> reading like a pin. Folded into the `c`/`rust` strings.

⭐⭐ **AND HERE IS THE PART NOBODY HAS WRITTEN DOWN: THAT REPAIR IS WHY
`required[0]` AND `required[1]` HAD NO ENGLISH.** From `git show HEAD:` on the
committed `spec.md`, the four per-language `required` entries were:

| entry | `c` bytes | `rust` bytes | trailing prose identical across the two keys? |
|---|---:|---:|---|
| `required[0]` | **20** | **18** | no — there is no prose |
| `required[1]` | **22** | **39** | no — there is no prose |
| `required[2]` | 722 | 713 | **yes** |
| `required[3]` | 410 | 405 | **yes** |

**`required[2]` and `required[3]` carry the same paragraph in both keys — the
signature of one `why` folded into two strings.** So §12 item 0 folded the two
entries that HAD a `why` and left the two that did not, and the report said
*"two `idiom.required` entries"* as though that were all of them. **Nothing
caught it**, because `required` is given no verdict and `spellings: 0` prints as
a clean number rather than as an absence.

> ⭐ **The transferable half, offered as §2.6 asks and NOT as a new gate check:
> the trap is not "backticks" and it is not "unknown keys". It is that
> `idiom.required` is a JSON object whose schema is CLOSED, whose extra keys are
> SILENT in the audit, and whose misuse is only visible in a count that reads
> fine when it is zero.** Three distinct people have now put prose somewhere the
> schema does not read it — a `why` key, my `note` key — or taken prose out to
> fix that and not put it back. **The cheapest unmissable fix is one sentence in
> the entry itself**, which the repaired `required[0]` and `required[1]` now
> carry: *an entry with no English declares a spelling and says neither what it
> binds nor what it is required for.* A reader who meets that sentence in the
> entry cannot write the next bare span. **I did not invent a gate check, per
> §2.6.**

### 3.2 `ph29_pins.py` reports `required[0].rust` as SCOPED, which is right about the OLD spelling and would be wrong about the new one

The probe prints `required[0].rust  SCOPED  tr.wrapping_add(1)  on: unsafe.rs,
verus.rs  off: safe_naive.rs, safe_tuned.rs`. That is correct — it is auditing
the **committed** span. It is worth saying only because the probe's own output
is the strongest single argument for §2.1's respelling and a reader could take
the `SCOPED` label as a property of the entry rather than of the old spelling.
After the edit the entry is **not** scoped: `.wrapping_add(1)` binds all four.

### 3.3 Nothing else in §1 or §2 was contradicted

I looked for a reason to disagree with the manager's derivation and did not find
one. §2.4's "weak" call on `real_size` is measured and right (7/7/3/3
occurrences). §2.2's latency claim reproduces. §2.7's arithmetic reproduces
exactly. **This is a clean negative and it is worth as much as a finding**
(`PROTOCOL.md` rule 6 for reviewers).

---

## §4 STAGE B GROUNDWORK — THE MECHANISM, WHICH CLOSES EXACTLY

⚠⚠ **READ §6 FIRST IF YOU ARE ABOUT TO QUOTE A NUMBER FROM THIS SECTION.
NOTHING HERE IS A PUBLISHED BOUND.** No Verus twin verifies, so `spec.md`'s
`identity: unsafe == verus, O3 exact` makes **every R4 row below a control and
not a rung**.

`.temp/php33/probe_b.py`, `--selftest` **PASS**, 9 must-fire/must-not-fire cases
over the callgrind parser and the substitution engine. The statistic is
`harness/measure.py::_sum_rows`, **imported and not transcribed**
(`TASK_PHP_022` §3.2's defect), and it reproduces the shipped record **to the
digit**:

```
R3: callgrind_annotate 23,441,029   per-instruction sum 23,441,029   AGREE
R4: callgrind_annotate 24,951,895   per-instruction sum 24,951,895   AGREE
safe_tuned   record=23,441,029  here=23,441,029  delta=0.0000%
unsafe       record=24,951,895  here=24,951,895  delta=0.0000%
```

### 4.1 ⭐⭐⭐ THE GAP IS THE FOLD SPELLING, AND IT IS AN LLVM UNROLL FACTOR

Decomposed by execution-count class, `small.bin`, O3/isolated:

```
R3 hot fold loop   43 insn x 475,346 iter = 20,439,878 Ir    UNROLLED 8x
   + scalar epilogue 8 insn x  42,844     =    342,752
R4 hot fold loop   23 insn x 956,243 iter = 21,993,589 Ir    UNROLLED 4x
   + scalar epilogue 8 insn x  20,640     =    165,120
   both fold the SAME 3,845,612 bytes
fold delta                                  +1,376,079   =  91.1% of the gap
prologue (56 vs 62 insn x 25,000)           +  150,000
header decode / clamp / tail classes        -   15,213
------------------------------------------------------------------
net                                         +1,510,866
measured  24,951,895 - 23,441,029         = +1,510,866      CLOSES, no residue
```

**And the per-byte body is IDENTICAL.** From the disassembly
(`.temp/php33/attrib_view.log`), each folded byte costs five instructions in
**both** rungs — `mov / shl $0x5 / sub` for the `×31`, then `movzbl`, then `add`
— and the loop overhead is three instructions in both:

```
R3:  ... movzbl 0x7(%r14),%r8d ; add %r9,%r8 ; add $0x8,%r14 ; add $-8,%rdi ; jne
R4:  ... movzbl 0x3(%r14,%rsi,1),%edi ; add %r9,%rdi ; add $0x4,%rsi ; cmp %rsi,%r8 ; jne
     5*8 + 3 = 43                              5*4 + 3 = 23
```

> ⭐ **The unsafe rung is not doing more work per byte. It is doing exactly the
> same work per byte, and amortising the same three-instruction loop overhead
> over four bytes instead of eight, because LLVM unrolled the safe slice
> iterator 8× and the unchecked index walk 4×.**

### 4.2 It is symmetric, and that is the strong form of the claim

Nine variants, all returning the **shipped checksum on all six inputs**, all
**IN CONTRACT** by `harness/check.py::spelling_matches` over the repaired
declaration. `Ir` per window byte; `R4ship` = 1.7325:

| variant | Ir/win-byte | vs R4ship | `kernel` |
|---|---:|---:|---|
| **R3 `v0_shipped`** — `.iter()` fold | **1.6198** | **−6.51 %** | 218 insn `fed2bdbf41eb` |
| **R3 `r3_fold_index`** — R4's index walk, spelled safely | **1.7325** | **+0.00 %** | 199 insn `dbfd867a9ba1` |
| R3 `r3_fold_fold` — `.iter().fold(..)` | 1.7325 | +0.00 % | 200 insn `5fef264578b5` |
| R3 `r3_head_shift` — R2's shift-loop header | 1.6199 | −6.50 % | 236 insn (fixed term only) |
| R3 `r3_copy_loop` — R2's byte copy | 1.7153 | −0.99 % | 236 insn — the calibration loser |
| **R4 `v0_shipped`** — index walk | **1.7325** | 0 | 183 insn `05d6b672b204` |
| **R4 `r4_fold_iter`** — R3's `.iter()` fold | **1.6198** | **−6.51 %** | 209 insn `d71669d3c0e6` |
| R4 `r4_fold_slice` — `&[u8]` + the existing `get_unchecked` | 1.7325 | +0.00 % | **183 insn `05d6b672b204` — BYTE-IDENTICAL to R4ship** |
| R4 `r4_head_array` — `from_le_bytes` header | 1.7325 | −0.00 % | 173 insn (fixed term only) |

**Put R4's fold into R3 and R3 measures R4 exactly. Put R3's fold into R4 and R4
measures R3 exactly.** The safe/unsafe distinction contributes nothing at all to
this row's spread; the fold spelling contributes all of it.

⚠ **Three of these are calibration and they behave**: `r3_copy_loop` and
`r3_head_shift` move, `r4_fold_slice` comes back byte-identical. **A search
where nothing moves is a search whose substitutions did not apply.**

⚠ `r3_fold_fold` is worth flagging: `.iter().fold(..)` is **not** free — it
measures exactly R4ship, i.e. the combinator loses the 8× unroll that the `for`
over `.iter()` gets. Two spellings a reader would call the same thing are
6.5 % apart.

---

## §5 THE QUESTION THE ROW TURNS ON, AND HOW FAR I GOT

> **Is `ph29`'s negative spread a spelling artefact, or a result?**

**The sign is explained. The verdict is NOT yet decidable, and it turns on one
thing:** `spec.md` pins `identity: unsafe == verus, O3 exact`, so
`r4_fold_iter` moves the R4 endpoint **only if it has a byte-identical Verus
twin that verifies**. If it does, the negative spread is an artefact of an
**unsearched R4 side**. If it cannot, the row is `.memory/02-bench-rules.md`
reason 2 in its purest form — *the R4 side is chained to the prover* — and the
negative spread is a **result about the ladder** rather than about Rust.

**Five Verus attempts, `.temp/php33/v/iterprobe*.log`, on the same `foldb` shape
`verus.rs` already uses.** Per `spec.md`'s own rule — *read the ERROR TEXT, not
the exit code* — here is every one:

| # | spelling | error text | reads as |
|---|---|---|---|
| 1 | `it.pos()` | `no method named pos` | my API error |
| 2 | `it.seq() =~= sub` | `expected Seq<&u8>, found Seq<u8>` | my type error; `.unref()` fixes it |
| 3 | `v[..n].iter()` | **`precondition not satisfied`** at `v[..n]` | ⭐ see below |
| 4 | `v[0..n].iter()`, body `assume(false)` | — | **`4 verified, 0 errors`** |
| 5 | `v[0..n].iter()`, real body | `invariant not satisfied at end of loop body` | proof work |

⭐⭐ **`is not supported` DOES NOT APPEAR IN ANY OF THE FIVE.** The pinned vstd
ships `assume_specification[ <[T]>::iter ]`, an `IteratorSpecImpl` for
`core::slice::Iter` and the `VerusForLoopWrapper` machinery
(`~/tools/verus/vstd/std_specs/slice.rs`, `…/iter.rs`). **Attempt 4 verifies
4/0**, which says the `requires`, the `ensures`, the iterator plumbing and the
invariant-before-the-loop all discharge; what is left is the inductive step.
**So nothing measured here disqualifies the candidate and nothing forces a new
TRUSTED item** — which is the opposite of `p16`'s `r4_hdr` and `p05`'s
`c4_hu16_nz`, where the route really was `is not supported`.

⚠ **I did not close the proof and I am not claiming it closes.** The obstacle is
that inside the loop body `it.index()` is the **pre-`next`** value —
`assert(it.index() >= 1)` fails — so the invariant I wrote cannot be re-established
at the end of the body. The next attempt should re-read
`VerusForLoopWrapper::next`'s `ensures` before writing more invariants.

### 5.1 ⭐ A spelling fact the next task should not re-derive, and it is free

The pinned vstd gives `SliceIndexSpecImpl` to **`usize` and `Range<usize>` and
to nothing else** — **`RangeTo` has no spec**, which is why attempt 3's
`precondition not satisfied` is undischargeable rather than merely unproved. And
the provable spelling costs nothing:

```
r4_fold_iter     kernel 209 insn  d71669d3c0e6     read_buf[..recvd]
r4_fold_iter0    kernel 209 insn  d71669d3c0e6     read_buf[0..recvd]
fingerprints equal? True     answers equal on all 6 inputs? True
```

**`[..recvd]` and `[0..recvd]` are byte-identical machine code.** A candidate
should be written `0..recvd` from the start.

### 5.2 What this would be if it closed — stated so nobody over-reads §4

If the twin verifies, `r4_fold_iter` is **not** merely a cheaper R4. It replaces
`vget_unchecked`'s **only** call site with a checked slice index, so it is
**6.5 % cheaper AND one trusted call site smaller** — `ph07`'s `r4_index0` and
`ph16`'s `r4_fold_index` result, except that those two were byte-identical ties
and this one moves the number. ⚠ **`.memory/02-bench-rules.md` still forbids
re-shipping the rung**; what would move is the published bound, and the honest
publication would be `R3ship − R4ship` beside the R3-side span, **with no pair
interval** — `min(R3 found) − min(R4 found)` is not the repair.

---

## §6 STAGE B IS DEFERRED. THE REASON, AND WHAT IS LEFT — §4 item 4

**I stopped at the authorisation the task file gives in its ⭐ box, and I think
it was right.** What Stage B still owes, sized against `TASK_PHP_028`, which
spent a whole task on `ph16` alone:

1. **`controls/spellings.py` + `controls/spellings.json`** under
   `patterns-php/ph29-recvfrom-alloc/`. `ph16`'s is **1 505 lines**; mine is
   scratch at **701** and covers the audit, the substitution engine, the parser,
   the pricing and the attribution — but **not** `--attribute`'s shipped form,
   the sidecar schema, `pin.regenerate`, the three-valued `admissible`, or the
   `verus_checked` flag.
2. **§H's must-fire negatives.** `ph16` shipped **54 cases** and they found
   **four real defects in its own validator, one of which had already published
   a false comparison against another row.** Mine has **9**, they cover the
   parser and the substitution engine only, and **9 is not 54**. §H binds: *a
   validator lands with its must-fire negatives or it does not land.* **So I did
   not land one.**
3. **The Verus twin** (§5) — the single thing the verdict turns on, and the one
   piece that cannot be hurried.
4. **The R4 candidates that need a twin each**, and `r4_head_array` priced
   properly against the `from_le_bytes` unsupported claim.
5. **One more gate round at least** — `controls/*.py` is in the gate digest, so
   landing the control re-gates the row, and a non-`FRESH` `controls_json` entry
   makes `report.py` render a line, which costs `gate → report → gate` again.

⚠⚠ **And the honest reason, not just the arithmetic one: the verdict Stage B
exists to produce is a single word — artefact or result — and I can produce the
mechanism but not the word.** Shipping a `spellings.json` that prices nine
variants and leaves `verus_checked: false` would publish a sidecar that **looks
complete and is not**, which is precisely the defect `TASK_PHP_024` §1.6
demonstrated live on `ph07`. A half-validator is worse than none.

**What the next task inherits, and it is not nothing:** the mechanism closes
exactly (§4), the candidate that decides the question is identified and priced
(§5), the construct is measured **not** `is not supported` (§5), the spelling to
write it in is measured free (§5.1), and the parser/substitution machinery with
its negatives is in `.temp/php33/probe_b.py` ready to be cloned into the row.

---

## §7 WHAT I DID NOT DO, AND WHAT I AM UNSURE OF

1. **Stage B, as above.** No `controls/` file was added to any row.
2. **No `NOTES.md` or `README.md` edit on `ph29`.** ⚠ **This is a real gap and
   it is the manager's call.** `NOTES.md` §0's disclosure table now has a
   **sixth** move it does not list (`28a92fac…` → `a5dfc7d4…`), and `PROTOCOL.md`
   rule 6 says a disclosure a reviewer trusts *instead of* re-checking is worse
   than useless if it is incomplete. I did not add the row because `NOTES.md` is
   not in my task's deliverables and because the entry should say what §3.1
   found, which is a finding the manager lands. **`NOTES.md` §8's "`controls/
   spellings.py` was not built" is still true and still correct.**
3. **No `.memory-php/` or `RECAP_PHP.md` edit** — manager-only. The entries this
   task implies: open item 51 is **closed**; `02-ladder.md`'s *"`ph29` cannot
   simply be cloned into — its `.idiom_audit` is `spellings: 4, forbidden: 4,
   required: 0`"* is now **stale** (it is `12 / 4 / 8`, `present 22`); and
   `ph29`'s spellings debt is **still undischarged**, so *"`ph03`, `ph29` and
   `ph64` REMAIN UNDISCHARGED"* stands, with `ph29` now **searchable** rather
   than blocked.
4. **I did not re-run the other five php rows' gates.** Nothing I touched is in
   their digests; the `--check-stale` bracket is the evidence and it is `12 / 0`.
5. ⚠ **Unsure: whether `required[0]`'s new English overstates by saying the
   entry "binds all six rungs".** It binds all six *in the sense that both
   language keys are now pinned and every rung matches*, which is what the audit
   shows (`present` 2 + 4 = 6 for that entry). A reader could take "binds" to
   mean something stronger. I chose the phrasing because the alternative — say
   nothing — is what created the problem.
6. ⚠ **Unsure: whether the unroll-factor mechanism is stable across rustc
   versions.** It is a heuristic in LLVM's unroller, not a language property.
   The row's numbers are pinned to `rustc 1.97.1 / LLVM 22.1.6`, and §4's claim
   should be read as a claim about **this toolchain**. I did not test another.
7. **I did not price the variants on a third input shape**, so the slope is a
   two-point fit exactly as `ph07`/`ph16` compute it. Same statistic, same
   limitation.
8. ⚠ **`.temp/mgr169/` probes are the manager's own work and carry no review.**
   I ran all three and re-derived their load-bearing claims independently (§1),
   which is the closest I could get to reviewing them inside this task.

---

## §8 REPRODUCE

```
python3 .temp/mgr169/ph29_pins.py --selftest && python3 .temp/mgr169/ph29_pins.py
python3 .temp/mgr169/charlit_reach.py --selftest && python3 .temp/mgr169/charlit_reach.py
python3 .temp/mgr169/ph29_predict.py

python3 .temp/php33/pin_lines.py            # §1's line-level table
python3 .temp/php33/check_edit.py           # §2.1's eight numbers, before the gate
python3 harness-php/gate.py ph29-recvfrom-alloc            # FAILS on [tables]
python3 harness-php/gate.py --tool report ph29-recvfrom-alloc
python3 harness-php/gate.py ph29-recvfrom-alloc            # PASS

python3 .temp/php33/probe_b.py --selftest                  # 9 negatives
python3 .temp/php33/probe_b.py --attribute --price         # §4
python3 .temp/php33/attrib_view.py                         # §4.1's disassembly
python3 .temp/php33/rangecheck.py                          # §5.1
python3 ./verus_run.py .temp/php33/v/iterprobe.rs          # §5 attempt 5

python3 harness/measure.py --check-stale                   # 66 / 0
python3 harness-php/gate.py --tool measure --check-stale   # 12 / 0
```

`.temp/php33/NOTES.md` is the scratch index. **456 KB, all binaries, `.o`,
`.cg` and `__pycache__` deleted; every remaining file is a generator, a source
or a log, and every one has a regenerate command in that table.**
