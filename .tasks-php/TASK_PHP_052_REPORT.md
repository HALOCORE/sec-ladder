# TASK_PHP_052 — REPORT · `ph56`, R5, `spec.md`, the gate and the statistic

**Role:** research **engineer**, alone. **Subject:** finish row 10, `ph56` —
resume from `TASK_PHP_051`'s stopping point and take the row to a green gate
with a published statistic.

> # ⭐⭐⭐ HEADLINE, AND IT IS THREE THINGS
>
> ## 1. THE ROW IS BUILT AT SIX RUNGS AND GATED
> `verus.rs` verifies **66 / 0**, **76 / 0** under `--cfg slb_twin`, with **no
> `#[verifier::rlimit]`** — and the row's obligation, `operand_present`, is the
> compile pass's own loop invariant. ⭐ **Deleting `1e708a5aeb30`'s three lines
> makes it stop verifying, ON THE ASSERT THAT ESTABLISHES THE OBLIGATION** —
> measured, `controls/negatives.py --emit r1`.
>
> ## 2. ⛔⛔ THE CROSS-LANGUAGE SIGN DEPENDS ON WHICH STATISTIC YOU PICK
> R4 against `c-gcc-h` on `large.bin`, O3/isolated, is **+5.879 % in A1** and
> **−8.423 % in W1** — same binaries, same input, opposite signs. `inside_share`
> predicts it exactly: gcc keeps **11–15 %** of the per-call work outside the
> `kernel` symbol where the Rust cells keep **0.8–2.9 %**. **And the sign flips
> between the two C COMPILERS as well, independently**, in family B.
>
> ## 3. ⭐⭐⭐ R4 AND R5 ARE ONE EXEC TEXT, AND IT COST EXACTLY ZERO
> **0.000 Ir/call** in A1 on both inputs, **0.00** in family B across all 32 pad
> residues, and `md5_fn_norel` / `md5_norm` identical at both O0 and O3 — so
> `identity` pins **`norel`**, not `differ`. ⚠ `ph55` could not say this: it
> ships two different spellings of one expression and measured **+0.071 %** and
> *"`norel` does not rescue it either"*. **This row normalised all four Rust
> rungs onto one spelling to buy it.**

---

## §0 BRACKETS — first and last

| | first (before any work) | last (after everything) |
|---|---|---|
| `python3 harness/measure.py --check-stale` | **`66 record(s) examined, 0 STALE`** | **`66 record(s) examined, 0 STALE`** |
| `python3 harness-php/gate.py --tool measure --check-stale` | **`20 record(s) examined, 0 STALE`** | **`22 record(s) examined, 0 STALE`** |

✅ **PAT UNMOVED. PHP AT `22/0` — the two new records landed**, which is exactly
what `TASK_PHP_051` predicted and honestly could not report.

⚠⚠ **AND IT READ `22 / 1 STALE` FIRST, TWICE, AND BOTH WERE REAL.** Recorded
because the bracket is only worth something if its misses are reported too:

| reading | stale against | why |
|---|---|---|
| `22 / 1` | `results/ph56-…json` ← `verus.rs` | I deleted the two non-load-bearing `requires` (§1.4) **after** the measure step. ⭐ The binaries are BYTE-IDENTICAL before and after — `md5sum` plus a full rebuild, `verus-O3-isolated ecf9521fdebbe03c…` both times — but the record pins the SOURCE hash, so the whole six-command sequence was re-run. Every A1 cell came back **identical to the digit**, so §4's numbers are unaffected |
| `22 / 1` | `results/gate/ph56-…json` ← `NOTES.md` | I added §11.7's byte-identity paragraph after the previous gate. The final gate refreshed it |

▶ **The lesson, and it is cheap to state and expensive to learn: finish editing
every rung BEFORE `--tool measure`, not after.** A ghost clause costs nothing at
run time and a full re-measure at record time.

`git status --short` at close:

```
 M patterns-php/ph56-fetchmode-arith/NOTES.md
 M patterns-php/ph56-fetchmode-arith/README.md
 M patterns-php/ph56-fetchmode-arith/safe_naive.rs      <- §1.6, the modulus spelling
 M patterns-php/ph56-fetchmode-arith/safe_tuned.rs      <- §1.6
 M patterns-php/ph56-fetchmode-arith/unsafe.rs          <- §1.6
 M results-php/preflight/_norow.preflight.json          <- expected, PROTOCOL_PHP.md §F6b
?? .tasks-php/TASK_PHP_052_REPORT.md
?? patterns-php/ph56-fetchmode-arith/controls/negatives.{py,json}
?? patterns-php/ph56-fetchmode-arith/controls/spellings.{py,json}
?? patterns-php/ph56-fetchmode-arith/controls/statistic.{py,json}
?? patterns-php/ph56-fetchmode-arith/controls/rlimit_bisect.sh
?? patterns-php/ph56-fetchmode-arith/spec.md
?? patterns-php/ph56-fetchmode-arith/verus.rs
?? results-php/gate/ph56-fetchmode-arith.json
?? results-php/ph56-fetchmode-arith.json
?? results-php/preflight/ph56-fetchmode-arith.preflight.json
?? results-php/tables/ph56-fetchmode-arith.md
```

**Checks run as required:**

| | result |
|---|---|
| `.tasks-php/cbaseline_check.py --ratchet` | **rc 0** — 68 hits, ratchet 69. ⭐ `ph56` contributes **0** — see §9, where three new hits were adjudicated BY HAND and repaired rather than regex-tuned |
| `.tasks-php/citecheck.py` | **rc 1 — CORPUS-WIDE AND PRE-EXISTING**, in `ph00`, `ph03`, `ph07`, `ph16`, `ph29`, `ph45` and `ph53`. ⭐ **`ph56` contributes 0**: `grep -c -i 'ph56'` over the whole report is **0**, and this row's two new validators keep their must-fire arms INSIDE themselves — which is the §H subclass the other rows are flagged for. ⚠ An earlier line of this report said rc 0; that was a shell mistake (`$?` after a pipe captures `tail`'s status), corrected here rather than left |
| `harness-php/provenance.py ph56` | **rc 0**, 7 spans, all `OK`, tier `modelled` |
| `controls/spellings.py` (the contract audit) | **rc 0** — 78 (spelling × rung) obligations, **0 required absent, 0 forbidden present** |
| `controls/negatives.py` | **rc 0** — pristine 66/0 and 76/0; **five mutants, all FAIL as declared** |
| `controls/statistic.py` | **rc 0** — 16 cells, both families |
| `.tasks-php/php50_align_sweep.py --row ph56 --pads 32` | **rc 0** — 18 pairs, two verdicts each |

---

## §1 ⭐⭐⭐ `verus.rs` — the obligation, and it is `ph55`'s one file over

### 1.1 What is proved

```
requires  off + len <= buf@.len()
ensures   r == ph56_fold(buf@, off as int, len as int)
```

A **value** postcondition over the whole machine — the compile pass, the
executor, the zval store, the refcounts and the next-free indices — not a
memory-safety-only retreat. `ph56_fold` is PHP 5.0.0's compiler-plus-executor
with `1e708a5aeb30` applied, as eight recursive spec functions, and
`model.py::ph56_run` re-derives the same `u64` from a different decomposition.
`main`'s `assert(r == ph56_fold(...))` is what *consumes* it; without that the
postcondition is decoration.

### 1.2 The obligation

> **`operand_present(ops, n)`** — *for every `j < n`, an opline whose opcode is
> `ZEND_ISSET_ISEMPTY_DIM_OBJ` carries an op2 that is `IS_CONST` or `IS_VAR`,
> and never `IS_UNUSED`.*

Exactly the property `_051` §9 wrote down, with one strengthening that the
proof forced: the conclusion is *`T_CONST` or `T_VAR`*, not merely
*`!= T_UNUSED`*, because `zunwrap`'s precondition needs `get_zval_ptr` to return
`Some`, and that needs the operand kind to be one of the two present kinds
rather than merely not the absent one. **Three facts carry the per-statement
step and the middle one is the 2004 patch:**

1. `ZEND_ISSET_ISEMPTY_DIM_OBJ` is reachable only through
   `zend_do_isset_or_isempty`'s `ZEND_FETCH_DIM_IS` arm (`:3229`), and
   `ZEND_FETCH_DIM_IS` is `ZEND_FETCH_DIM_W + 6` and nothing else — the
   six-groups-of-three layout is doing the work;
2. `case BP_VAR_IS:` **refuses** `ZEND_FETCH_DIM_W` with an `IS_UNUSED` op2;
3. `zend_do_isset_or_isempty` rewrites the **last** opline only, so a chain's
   leading `[]` opline is judged by (2) as well.

⭐ **It is established by the EMITTER and consumed by the EXECUTOR without
testing.** `NOTES.md` §11.2, §11.5.

### 1.3 ⛔ THE MUTATION TEST IS THE ARGUMENT

`controls/negatives.py`. Five mutants, each declared in advance, **all five
FAIL**; `pristine` re-verifies the shipped file at 66/0 and 76/0 on every run so
a broken toolchain cannot read as a clean sweep.

| mutant | removes | result |
|---|---|---|
| `r1` | ⭐ `1e708a5aeb30`'s three lines, from `s_parse_ok` and the exec arm together | **65 / 1**, and the error is the `assert forall` that re-establishes `operand_present` — arm 3 checks the DIAGNOSTIC, not the exit code |
| `noinv` | `operand_present` from the **executor** loop's invariant | **65 / 1** — the invariant is consumed, not decoration |
| `nocap` | the `nops + 1 + chain > MAX_OPS` break | **65 / 1** |
| `noclamp` | the `nstmt > MAX_STMT` clamp | **65 / 1** |
| `nobuf` | `off + len <= buf@.len()` | **65 / 1** |

### 1.4 ⭐⭐ THE PRECONDITION COUNT WENT 3 → 1, AND THE GATE DID IT

The first draft copied `ph55`'s signature: `off + len <= buf@.len()`,
`16 <= len`, `len <= 8 * MAX_STMT`. The gate's own `req-mut` stage deleted each
and re-ran Verus:

```
[req-mut] verus.rs kernel requires[1] is NOT load-bearing   (16 <= len)
[req-mut] verus.rs kernel requires[2] is NOT load-bearing   (len <= 8 * MAX_STMT)
```

Both **deleted**. `ph56` ESTABLISHES in code what `ph55` ASSUMES in a signature
— the `nstmt` clamp and the `nops` break — and `noclamp` and `nocap` are the
mutants that measure that nothing else does. ⚠ **The lesson is about copying a
sibling's signature**: a precondition that is not load-bearing narrows the
admissible call sites for nothing, and reading would not have caught it.

### 1.5 ⭐ THE RLIMIT IS **2**, BISECTED

`controls/rlimit_bisect.sh`: rlimit 1 → 65/1 plain and 75/1 twin; rlimit **2** →
66/0 and 76/0; every value from 3 to 200 → 66/0 and 76/0; **no attribute** →
66/0 and 76/0, which is what ships. ⭐ **`ph55` bisected to the same 2** — an
`n = 2` result about the proof SHAPE.

⚠⚠ **The first draft DID exceed the default, and the cause was a wrong loop
invariant, not proof size.** Two clauses that cannot hold at a `break` were
declared `invariant` instead of `invariant_except_break`; Z3 spent the budget
failing to prove them and reported `Resource limit (rlimit) exceeded`. ▶ **An
rlimit error is a symptom, not a size** — and the obvious repair would have
shipped a wrong invariant under a 20× budget.

### 1.6 ⚠ THE ONE THING THE PROOF CHANGED IN THE OTHER RUNGS, DECLARED

Verus models `usize` as 32 **or** 64 bits and will not assume a `u64`→`usize`
cast is lossless, so R5 must take the modulus **before** the cast. `ph55`
resolved that by shipping two spellings — `(x as usize) % NVAR` in `unsafe.rs`,
`(x % (NVAR as u64)) as usize` in `verus.rs`. ▶ **This row normalised ALL FOUR
Rust rungs onto the second spelling** (nine expressions across three files), so
R4 and R5 are one exec text and the R2→R3 / R3→R4 gradients carry no
representation change. Itemised in `spec.md`'s `provenance.divergences`;
demonstrated behaviour-preserving by the gate's stage-3 cross-rung checksum.

---

## §2 `spec.md`

Written, and generated rather than typed: `idiom.why`'s mandatory 11 003-byte
`NAMED-SPELLING STANDARD` tail is copied byte-exact (sha256 `59748cce2db5…`,
verified) and `verus.items`' 56 entries are **derived** through
`harness/vparse.py` rather than transcribed.

**Contract**, derived from `verus.rs` through `verus.translate`:

```
requires   off + len <= buf_len
ensures    result == ph56_run(buf, off, len)
```

⛔⛔ **`spellings.py --audit-only` WAS RUN ON THE DRAFT BEFORE IT LANDED, AND IT
FIRED.** The first draft's `required` entries carried **24 absent spellings out
of 40** — every one a backtick in a sentence *explaining* a pin rather than
stating it: `` `BP_VAR_IS` ``, `` `:753` ``, `` `new_zval->refcount++` ``,
`` `EG(uninitialized_zval)` ``, `` `$a[] = 1` ``,
`` `zend_fetch_dim_is_handler` ``, `` `inputs/adversarial-chain.bin` `` and
seventeen more. ▶ **Item 100's exact shape, caught before the contract landed
rather than by the gate.** The shipped contract audits **0 absent, 0
forbidden-present** over 78 (spelling × rung) obligations, and the gate agrees:
`idiom forbidden: 0 hit(s) over 12 forbidden spelling(s)`.

**Tier declared `modelled`, and the catalogue's `narrowed` is refuted by
measurement**: `harness-php/provenance.py` reports the kernel overlap at
**10 % (14/143)** over the union of seven cited spans and **23 % (7/30)** over
the defect site alone, where `narrowed` leads a reader to expect 25 %. Seven
spans are pinned; four of the seven are the HARM rather than context, and
`zend_compile.c:3229` is among them — without it a reader concludes the harm is
in `zend_fetch_dim_is_handler`, which is what the task that commissioned this
row concluded and what measurement refuted.

**`identity` pins `norel` at both levels**, on the strength of the record:
`md5_fn` differs, `md5_fn_norel` and `md5_norm` are identical at O0/isolated and
O3/isolated, and the instruction counts are equal (929 and 632). ⚠ `whole` is
not covered by the pin and does differ structurally, because there the kernel is
inlined into `main` and there is no common symbol.

---

## §3 THE GATE

### 3.1 ⭐ THE VERDICT, QUOTED FROM THE RECORD AND NAMED

`results-php/gate/ph56-fetchmode-arith.json`:

```
verdict          = PASS
complete_run     = True
failures         = []
blocked          = []
contract_sha256  = e76ae727f70b5f2faafe68b754ce14e9184eae4f6162ab63b9d8c8d2327d6577
verus            = {"verus.rs": {"verified": 66, "errors": 0, "pinned": 66}}
identity         = [(O0, norel, expected norel), (O3, norel, expected norel)]
```

and `check.py: PASS` on stdout.

### 3.2 THE SIX-COMMAND SEQUENCE, AND IT WAS RUN TWICE

⛔ **`harness/check.py` was never run directly on this row.** Every invocation
went through `harness-php/gate.py`.

| # | command | first pass | second pass |
|---|---|---|---|
| 1 | `--tool build ph56 --all` | 28 binaries, ok | ok, **byte-identical** |
| 2 | `--tool measure ph56` | ok | ok, **every A1 cell identical** |
| 3 | `--tool report ph56` | ok | ok |
| 4 | `gate ph56` | ⛔ **16 failures** → §3.3 | ✅ **PASS** |
| 5 | `--tool report ph56` | ok | — |
| 6 | `gate ph56` | ✅ **PASS** | — |

⚠ The second pass exists because of the stale-source repair in §0, not because
the first was wrong.

### 3.3 ⭐ WHAT THE FIRST GATE CAUGHT, AND ALL 16 WERE REAL

Not one was a false alarm, and three of the four classes were things reading
would not have found:

| n | class | what it was |
|---:|---|---|
| 1 | `[proof-pin]` | `verus.items` was written as a flat `{name: …}` where the gate wants `{file: {name: …}}`. **The entire item pin was silently doing nothing**, and four later stages cascaded off it |
| 2 | `[req-mut]` | ⭐ `16 <= len` and `len <= 8 * MAX_STMT` **are not load-bearing** — §1.4. Both deleted |
| 10 | `[twin]` | `NOTES.md` carried no `SLB-TRUSTED-ARGUMENT` section for any of the ten trusted items. Ten written, §11.8 |
| 1 | `[driver]` | a cascade of the `[proof-pin]` failure |
| 2 | `[tables]` | ✅ **expected** — the `gate → report → gate` chain, exactly as the task said |

⭐ **The two `[req-mut]` findings are the interesting half of this task's gate
work**, and they came from a stage that mutates the proof rather than reads it.

### 3.4 THE STAGES WORTH QUOTING

* **5c-twin**: *10 verified twin(s) for 10 trusted item(s), n=10 > 0 and none
  justified away* — no hatch, no blocked row. **This is prediction 1.**
* **5c-req**: *11 `requires` conjunct(s) probed and 1 deleted … no `requires`
  conjunct is a tautology.*
* **3c identity**: `unsafe vs verus O0: norel` and `O3: norel`, both matching the
  pin, both with `counts_a == counts_b` (929 / 632 instructions).
* **8 Miri**: required (10 trusted items **and** `spec.md` sets it), ran on all
  **8** inputs, **no UB**, and every exit code and checksum matches the model.
* **0b idiom audit**: *forbidden: 0 hit(s) over 12 forbidden spelling(s)*, and
  26 backticked spellings over 6 rungs → 78 pairs.

---

## §4 ⭐⭐⭐ THE STATISTIC

⛔ Everything below is **O3**, and every percentage names **statistic · input ·
opt/mode · base · which C compiler**, with **both** C columns. No `O0` figure is
quoted as a performance result.

### 4.1 `inside_share` PER CELL, PUBLISHED BEFORE THE STATISTIC IS CHOSEN

A1 / W1, per call, O3/isolated.

| cell | `small.bin` (16 stmts) | `large.bin` (64 stmts) |
|---|---:|---:|
| `c-gcc` (R1) | **0.8848** | **0.8547** |
| `c-gcc-h` (R1h) | **0.8856** | **0.8560** |
| `c-clang` (R1) | 0.9368 | 0.9791 |
| `c-clang-h` (R1h) | 0.9371 | 0.9792 |
| `safe_naive` (R2) | 0.9761 | 0.9922 |
| `safe_tuned` (R3) | 0.9720 | 0.9905 |
| `unsafe` (R4) | 0.9707 | 0.9897 |
| `verus` (R5) | 0.9707 | 0.9897 |

The gap between `c-gcc-h` and the Rust cells is **0.085–0.137**, far past
`STATISTICS_001.md` §1's `0.02`. **Exactly one pair set is narrow**: the Rust
cells against `c-clang-h` on `large.bin`, at **0.0104–0.0130**.
`controls/statistic.py` pins that set and checks the wide and narrow halves in
**opposite directions**, so neither claim can rot silently.

⛔ **And a high share is still not a certificate** — `ph55`'s two C cells,
`c-gcc` and `c-clang`, sit at 74–83 % and A1 reads `0.000 %` on that row's own
defect site anyway. What matters is whether **the difference** lands inside the
symbol.

### 4.2 ⛔⛔ AND ON THIS ROW IT DOES NOT — THE CROSS-LANGUAGE SIGN FLIPS

O3/isolated; bases `c-gcc-h` and `c-clang-h`.

| rust cell | input | **A1** vs `c-gcc-h` | **A1** vs `c-clang-h` | **W1** vs `c-gcc-h` | **W1** vs `c-clang-h` |
|---|---|---:|---:|---:|---:|
| `safe_naive` | `small.bin` | +28.232 % | +40.716 % | +16.344 % | +35.103 % |
| `safe_tuned` | `small.bin` | +8.994 % | +19.605 % | **−0.694 %** | +15.318 % |
| `unsafe` | `small.bin` | +3.922 % | +14.039 % | **−5.185 %** | +10.103 % |
| `verus` | `small.bin` | +3.922 % | +14.039 % | **−5.185 %** | +10.103 % |
| `safe_naive` | `large.bin` | +41.172 % | +39.891 % | +21.787 % | +38.057 % |
| `safe_tuned` | `large.bin` | +14.854 % | +13.812 % | **−0.741 %** | +12.520 % |
| `unsafe` | `large.bin` | +5.879 % | +4.918 % | **−8.423 %** | +3.811 % |
| `verus` | `large.bin` | +5.879 % | +4.918 % | **−8.423 %** | +3.811 % |

▶ **The figure this row publishes**, naming all five things: **R4/R5 against the
R1h C cells, W1, O3/isolated, `large.bin` — `−8.423 %` against `c-gcc-h` and
`+3.811 %` against `c-clang-h`.** Two C columns, two signs, and the row says so
rather than picking the flattering one.

### 4.3 THE LADDER

A1, O3/isolated, base named per column.

| step | `small.bin` | `large.bin` |
|---|---:|---:|
| R2 → R3 | −628.731 Ir/call, **−15.003 %** | −2465.411 Ir/call, **−18.642 %** |
| R3 → R4 | −165.749 Ir/call, **−4.653 %** | −840.748 Ir/call, **−7.814 %** |
| R4 → R5 | **0.000 Ir/call, 0.000 %** | **0.000 Ir/call, 0.000 %** |

⭐ The R3 → R4 step is what the **whole** ten-item trusted surface buys. The row
does **not** attribute it to `zunwrap` alone — see §6.1.

### 4.4 ⛔ FAMILY B THROUGH §B5's SWEEP — TWO VERDICTS PER PAIR

Full 32-residue pad sweep, O3/isolated. **Step per cell: `c-clang` 7.0,
`c-clang-h` 7.0, and 0.0 for the other six.** ⓘ Corpus-wide the step takes
`0.00`, `0.02`, `7.00`, `34.49`; this row draws two of the four in one record.

⛔ **ONE PAIR IS NOT PUBLISHABLE AS A MAGNITUDE**: `c-clang` → `c-clang-h` on
`small.bin`, median `+17.53`, range `14.00`, `|d|/step = 1.25` → **NOT
RESOLVABLE / SIGN-STABLE**. The row does not quote it as a family-B figure.

✅ **The other 17 pairs are RESOLVABLE and SIGN-STABLE**, and the three this row
leans on have range **0.00 across all 32 residues**: `safe_tuned` → `unsafe`
(−165.88 / −842.49), `unsafe` → `verus` (**0.00 / 0.00**, SIGN-ZERO) and
`c-gcc-h` → `unsafe` (−197.87 / −917.45).

⭐⭐ **The two families agree on the R3 → R4 step to within 0.2 Ir** (A1
−165.749 / −840.748, family B −165.88 / −842.49). It is the one figure that does
not depend on which statistic you pick.

⚠ **And family B flips sign between the two C COMPILERS, independently of the
family flip**: against `c-gcc-h` the R3 and R4 cells are cheaper
(−31.99 / −197.87 small, −74.96 / −917.45 large); against `c-clang-h` they are
dearer (+486.00 / +320.12 and +1209.31 / +366.82).

---

## §5 THE THREE §2 PREDICTIONS, SCORED

| # | prediction | verdict |
|---|---|---|
| **1** | **stage 5c-twin passes cleanly — no hatch, no blocked row** | ✅ **UPHELD.** Gate stage 5c-twin: *10 verified twin(s) for 10 trusted item(s), n=10 > 0 and none justified away*, and the twin build is **76 verified / 0 errors**. **No hatch, no blocked row, no `justified_away`.** ⭐ The task cites `ph55` upholding this at `n_twins = 8`; **this row adds TEN more**, and F97's narrowing — that the collision is a property of the `MaybeUninit` ITEM and not of php rows — survives a second php row whose ten twins include an `Option::unwrap_unchecked` |
| **2** | **the R1h costs ~nothing at run time — the guard is in the COMPILER, so it runs once per emitted opline, not per execution** | ⚠ **UPHELD ON THE MECHANISM, AND THE NUMBER IS NOT "~NOTHING" IN THIS HARNESS.** Measured (A1, O3/isolated, base = the R1 cell of the same compiler): `c-gcc` → `c-gcc-h` **+0.753 %** on `small.bin` and **+1.073 %** on `large.bin`; `c-clang` → `c-clang-h` **+0.587 %** and **+0.725 %**. ⭐ **The mechanism is confirmed by the shape of the number rather than asserted**: dividing by the statement count gives **1.526 / 1.554 Ir per emitted statement for gcc** and **1.086 / 1.063 for clang** — *flat across a 4× change in statement count*, which is what "once per emitted opline" predicts and what "per execution" does not. ⛔ **AND I SAY WHICH I AM MEASURING: this kernel compiles AND executes on every call**, so the percentage is a LOOSE UPPER BOUND on PHP's cost of `1e708a5aeb30` and may not be quoted as PHP's cost of it. The **per-opline** figure is the one that transfers |
| **3** | **NEW: no prediction is made about `ph56`'s R3 and R4 endpoints; search decides it** | ✅ **HONOURED — and no endpoint search was run**, which the task says is not owed. `NOTES.md` §13.1 records that this row therefore has **no in-contract spread on either side**, unlike `ph55`, and names it as the row's largest gap |

---

## §6 ⭐ THE `ph55` PAIRING — the R5 half, and the family is `n = 2` on three axes

`_051` §3 established *one family, one fix shape, two harms*. This task adds the
proof axis, and it closes with a fourth measured coincidence neither row
predicted:

| | `ph55` | `ph56` |
|---|---|---|
| the obligation | `ok_from` — *every word the PC lands on is an instruction word* | `operand_present` — *every opline that reads op2 was emitted with op2 present* |
| about | the **program counter** | the **operand contract** |
| established by | the **emitter** | the **emitter** |
| consumed by | the **executor**, untested, at `zend_execute.c:1391` | the **executor**, untested, at `zend_execute.c:3973` |
| discharges | `hunwrap`'s `requires t.is_some()` | `zunwrap`'s `requires t.is_some()` |
| trusted items | 8 (+8 twins) | 10 (+10 twins) |
| **rlimit needed** | **2** | **2** |
| Verus's obstacle | ⛔ **function pointer types unsupported** — TYPE-LEVEL, no `external_body` fix; forced `Option<u8>` + `match` on all four Rust rungs | **none** |
| must-fire negative | `--emit nofixup` | `--emit r1` |
| **A1 sees the fix?** | ⛔ **no — exactly `0.000 %`** | ✅ **yes — +0.59 % to +1.07 %** |
| R4 vs R5 | **+0.071 %**, and `norel` does **not** rescue it | **0.000 %**, and `norel` **does** |

> ⭐⭐ **THE SENTENCE:** *in both rows the obligation is a property the EMITTER
> establishes and the EXECUTOR relies on WITHOUT TESTING; both are loop
> invariants of the emitting pass; both discharge exactly one
> `unwrap_unchecked` precondition; and both need an rlimit of 2 against a
> default of 10.* **One family, one fix shape, one proof shape, two harms.**

⭐ **And the two rows differ on whether A1 can see their own defect — for a
reason that is about neither defect.** `ph55`'s three lines sit behind a
function pointer, which is why A1 reads `0.000 %` there; `ph56`'s sit in a
`static` the compiler inlines, which is why A1 reads `+0.75 %` here. ▶ **The
statistic's blindness is a property of the CALL PATH between the kernel symbol
and the fix, not of the fix.** That generalises past both rows and is the most
transferable thing in this report.

---

## §7 ⭐ WHAT I AM UNSURE OF

1. ⚠⚠ **The R3 → R4 step is not decomposed.** `−4.653 % / −7.814 %` (A1,
   O3/isolated, base = R3) is the price of the WHOLE ten-item trusted surface.
   `ph55` ships a `controls/spellings.py` that reduces the surface one class at
   a time and prices `hunwrap` alone; **this row's file of that name is the
   CONTRACT AUDIT only** and says so in its own docstring. So the number that
   would answer *what does THIS ROW's own unsafe cost* — `zunwrap` versus the
   nine index accessors — **is not measured**. That is the largest gap.
2. ⚠ **No in-contract spread on either side, and no endpoint search.** The
   shipped R3 and R4 are pinned by idiom; nothing measures how much cheaper an
   in-contract R3 could be. `ph45` and `ph52` both reversed their ordering under
   search.
3. ⚠ **The R1h is still not verified against a rebuilt PHP.** `_051` §8.1 asked
   for it and I did not do it either — it was the optional extra and §1–§4 took
   the depth. That `1e708a5aeb30` also kills `isset($a[][0])` is an inference
   from the source plus a measurement in the kernel, **not** a measurement on
   the interpreter. It remains the cheapest open check on this row.
4. ⚠ **`inside_share` was taken at one repeat per cell.** The spread column is
   therefore `0.000` trivially and is not evidence of stability. What IS
   evidence is §4.4's sweep: 32 residues per cell with the range reported, and
   six of the eight cells have range `0.00`.
5. ⚠ **I could not tell whether the `switch` dispatch is a *substitution* or a
   *projection***, which is `_051` §8.4's open question and is still open.
   `spec.md` declares `substitution` and argues it — every opcode this compiler
   emits has a handler, so no behaviour depends on the table's representation —
   but the row does **not** differentially demonstrate it against a
   table-driven variant. §A1(c) would want that differential; `modelled` does
   not oblige it, which is part of why the tier is declared where it is.
6. ⚠ **Why R4 and R5's raw bytes differ at all is not identified.** `norel` and
   `norm` are identical, so it is addresses and relocations; *which* driver
   decision produces them (`rustc` vs the Verus driver) is not distinguished,
   exactly as `ph55` left it.

---

## §8 HOUSEKEEPING

* **Scratch**: `.temp/php52/` only, never `/tmp`. `.temp/php51/NOTES.md` was
  read before anything was recreated. Artefacts deleted per `CLAUDE.md`
  constraint 6; the `.py` probes, the `.rs` mutants' generator, the logs and the
  JSON stay, and every binary is re-derivable with the commands in
  `README.md`'s *Reproducing* block.
* **Liveness**: **no `pgrep` was used at any point** and no process was killed.
  Long commands ran under `timeout` or as backgrounded jobs the harness reaps.
* **`grep -a`** wherever a binary might be in scope.
* ⚠ **`git apply --check` was not trusted alone** — `controls/r1h_backport.py`
  measures the bytes and reproduces the gitignore trap on every run; nothing in
  this task re-ran a bare `--check`.
* ⛔ **No edit under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`,
  `common-php/`, `.web/`, `RECAP_PHP.md` or `.memory-php/`.** No `git add`, no
  `git commit`.
* ⚠ **One `.tasks-php/` tool reports a suggestion I did not act on**:
  `cbaseline_check.py` prints *"68 hits < ratchet 69 — lower RATCHET to 68"*.
  `ph56` contributes 0, the drop is not mine, and tightening a corpus-wide
  ratchet is a manager decision.

---

## §9 ⭐ THE CBASELINE RATCHET FIRED, AND I REPAIRED THE PROSE RATHER THAN THE REGEX

`NOTES.md` §12 as first drafted took `cbaseline_check.py` from **68 hits to 71**
and the ratchet to `RATCHET FAIL: 71 hits > 69`. **Three new hits, adjudicated by
hand, one at a time:**

| line | what it said | adjudication |
|---|---|---|
| §12a | *"`ph55`'s C cells sit at 74–83 % and A1 reads `0.000 %`"* | ⓘ **False positive of the grep** — these are `inside_share` shares and `ph55`'s own same-compiler R1→R1h delta, not a cross-language magnitude. **But the sentence is better if it names the cells**, so it now reads *"`ph55`'s two C cells — `c-gcc` and `c-clang` — … (base there: the R1 cell of the same compiler)"* |
| §12b | *"`0.000 %` in A1 on both of its C cells"* | same class, same repair: *"on both of its C cells, `c-gcc` and `c-clang`, against the same R1-cell base"* |
| §12d | *"gcc hides 11–15 % … A1 compares 88 % of the C program"* | an `inside_share` statement that named the compiler but not the CELL. Now *"`c-gcc` and `c-gcc-h` hide 11–15 % … 88 % of the `c-gcc-h` program"* |

▶ **All three are genuine improvements and none is regex-tuning**: each names
the C cell the number belongs to, which is the rule's actual purpose. The count
returned to **68**, `ph56` contributes **0**, and the regex was not touched.
