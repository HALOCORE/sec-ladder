# TASK_PHP_059_REPORT — the eighth review round

**Role:** research reviewer. **One agent.** Read-only on `patterns-php/`, `harness/`,
`common/`, `patterns/`, `results*/`, `pilot/`, `common-php/`, `.web/`,
`RECAP_PHP.md` and `.memory-php/`. **No `git add`, no `git commit`, no history
mutation.** Nothing under `.tasks-php/` was repaired, so the registry was re-run
only as the closing check.

**Every reading below is an EVENT.** Unless a commit is named, a reading was taken
against the working tree at **`c868e60`** (clean at start of session), on
**2026-09-15**.

**Generators.** Every number I report has a committed-or-scratch generator named
beside it. Two live under `.temp/rev059/`:

* `share059.py` — an independent re-derivation of `F74`'s share, the pair tally,
  the `(i)` sweep and the flip census. It shares **no code** with
  `.tasks-php/php58_record_share.py`: `n_iters` is parsed straight out of the
  `.bin` header with `struct` rather than through `common-php/slb.py`, the record
  walk is written from the schema, and the pair enumeration is **every unordered
  cell pair** rather than a hand-written list of nine, so it cannot inherit the
  manager's choice of which pairs count. `selftest` sub-command, 4 arms, all as
  expected.
* `marginal_at_n.py` — §1.4's discriminator. Rebuilds probe inputs the way
  `harness/check.py::_probe_input` does (rewrite the leading `<Q`), re-implemented
  in three lines rather than imported, and drives `callgrind` directly.

⚠ **`.temp/` is gitignored.** Both files are generators and both survive; the
`callgrind.out.*` blobs and the reconstructed historical trees they produced were
deleted, per `CLAUDE.md` rule 1. **If the manager wants these numbers to outlive
`.temp/`, the two `.py` files must be moved under `.tasks-php/` by the manager —
I am not permitted to add them there and have not.**

> ### ✅✅ MANAGER, SAME DAY — **DONE, AND IT WAS THE FIRST THING DONE WITH THIS REPORT**
>
> Both generators are **committed** and the `.temp/` copies are gone. They live
> under `.tasks-php/` as **`php59_share.py`** and **`php59_marginal_at_n.py`**,
> and both are **filed in `checkers.py`** — the share tool as a swept checker
> (`--selftest`, 4 arms, added as an alias of the reviewer's bare `selftest` so
> **every command line in this report still runs verbatim**), the discriminator
> as `kind="tool"`, deliberately **not** swept.
>
> ⭐⭐ **THE REVIEWER FLAGGED THIS AGAINST ITSELF RATHER THAN HIDING IT**, in a
> report whose §2 refutes a manager finding — *"every number in this report that
> is not a `git show` or a quotation comes from one of them, and if `.temp/` is
> cleared they are not re-derivable."* ▶ That is **`F51`/`F99`/`F116`'s defect**,
> and `F116` was UPHELD-with-its-REASON-REFUTED at `_057` for exactly this
> shape — *"its evidence is NOT re-derivable: the log AND its generator are both
> gitignored."* ⛔ **A reviewer may not `git add`. So a report that says *"the
> manager must move these"* has done everything it is permitted to do, and
> leaving it there would have been the manager's defect, not the reviewer's.**
>
> ⚠ **`php59_marginal_at_n.py`'s kernel-exclusive column is KNOWN BAD** and its
> registry entry says so: it returned `0` on `ph07` and over-counted on `ph45`,
> the reviewer discarded it and used `callgrind_annotate` for every `W` figure,
> and its `--selftest` does not cover that column. ▶ **Use its whole-program
> `summary:` total — which reproduces two committed marginals to the digit —
> never its kernel column**, and do not promote it to a validator without arms.

---

## § HEADLINE — what this round found

1. ⭐⭐⭐ **§1.3 lands on reading (b). `F129` §3's word *"inadmissible"* is
   WITHDRAWN.** The authoritative layer and the committed statistics argument both
   say, in terms, that this quantity **never gates** — and I found a live corpus
   pair on which the bar, used as a gate, **passes a comparison where `A1` is
   provably blind to a 66.14 `Ir`/call difference**. The manager's own prediction
   `P2` is **the one prediction of five that survives as written.**
2. ⛔⛔ **§1.1's corpus clause is REFUTED, and by the repair that ships it.** *"Every
   `inside_share` figure in `RECAP_PHP.md`, in `.memory-php/03-numbers.md` and in
   `ph29`'s `controls/spellings.py` is `F74`'s"* is **false in both of the first
   two documents**, and the sentence asserting it is inside the four-row control
   whose whole purpose is to stop the two being confused.
3. ⛔⛔ **`F130`'s headline is REFUTED. The ratchet WAS invoked** — two task files
   instruct it by name and one report records the run and its output. The true
   claim is narrower and still worth having: *no **automated** caller passed the
   flag*. It is a **birth defect**, not a regression. **I found the unattributed
   70th hit** and it is benign.
4. ⛔ **`F129` §4a's *"ZERO OF FIVE SURVIVED AS WRITTEN"* does not survive.** Two of
   the five are upheld as written once the scoring stops crossing spellings and
   stops depending on the clause this round was convened to settle.
5. ⛔ **Open item 130's *"`task_cost.py` `N5` … STILL UNREPAIRED"* is STALE.** The
   repair landed at `d9652b4`, one commit after the cell was written, and survived
   two later commits including a pre-compact audit.

---

## §1 `F129` — five separable claims, verdicted separately

### 1.1 The name collision

**CONCLUSION — that two quantities wear the name and are different numbers:**
✅ **UPHELD, and UNDER-STATED.**
**REASON — the arithmetic:** ✅ **UPHELD.**
**COROLLARY — the corpus clause:** ⛔⛔ **REFUTED.**

**Second method.** I ran `callgrind` myself on the committed binary and annotated
it, rather than reading either shipped tool's output:

| | | |
|---|---|---|
| `ph29` `c-gcc`/`O3`/`isolated`/`small.bin` | kernel exclusive `Ir` 39,273,585 · PROGRAM TOTALS 43,965,688 | **`W` = 89.33 %** |
| same cell, from the records via `share059.py` | `A1`/call 1570.943 · `marginal_ir_per_call` 1952.75 | **`F74` = 0.8045** |

Both reproduce. (My whole-run total is 74 `Ir` above the control's 43,965,614 —
run-to-run instability; the share is unchanged to 4 dp.)

⭐ **UNDER-STATED: `F129` picks the one row where the two nearly agree.** On `ph45`,
`O3`/`isolated`/`large.bin`, measured by my own `callgrind` run plus
`callgrind_annotate`:

| cell | `W` | `F74` |
|---|---|---|
| `c-gcc` | 5.52 % | 5.51 % |
| `safe_tuned` | 9.44 % | 9.42 % |

So the divergence is **8.9 pp on `ph29`** and **0.01 pp on `ph45`** — it is
**row-dependent**, and a reader given only the `ph29` example will under-rate the
risk on some rows and over-rate it on others. ▶ **The finding should say the gap is
a measurement, not a constant** — which is exactly what the layer already says
about `inside_share` itself (`.memory-php/03-numbers.md`, `ph52`: *"it is a
measurement and never a constant"*).

#### ⛔⛔ The corpus clause is FALSE, in two documents, and the repair ships it

The clause, verbatim, from `patterns-php/ph97-optarg-unwritten/controls/inside_share.py`
(byte-identical in four rows, one `sha256`
`10666ce0cb6e542159e3ff323843e86c88ada6b7253826ebf45792aa80cc484c`, read at
`c868e60`) and from `RECAP_PHP.md`'s `F129` §1:

> *"Every `inside_share` figure in `RECAP_PHP.md`, in `.memory-php/03-numbers.md`
> and in `ph29`'s `controls/spellings.py` docstring is that one [`F74`'s]."*

**Counterexample 1 — `RECAP_PHP.md`, the *which statistic* cell.** It publishes
`` (`inside_share` 98.84 % → 64.50 %) `` for `ph97`. Those two numbers are
`inside_share_pct` **98.83845934798373** and **64.50051970182074** in that row's
`controls/libc_compare.json` — i.e. the **`W`** quantity, produced by the control
that computes `W`. Under `F74`'s definition **no cell of `ph97` reads either
number**: the row's sixteen `F74` shares at `O3`/`isolated` span **0.8824–0.9946**
(`share059.py`). Searched over **every computable cell of every built row** at
±0.0005, both values return **0 hits**.

**Counterexample 2 — `.memory-php/03-numbers.md` itself,** the file whose own
preamble box says *"EVERY FIGURE IN THIS FILE IS THE FIRST ONE"*. Its `ph52`
entry gives *"**22.24 %** on its **C** rungs … and **≈98.6 %** on its **Rust**
rungs (`unsafe` A1 `48,846,257` against W1 `49,549,469`)"* — and that parenthesis
**spells out the `W` arithmetic**: 48,846,257 / 49,549,469 = 98.58 %. Under `F74`
the same row's Rust cells read **0.9892–0.9970** and its C cells **0.2023–0.2269**;
neither `0.2224` nor `0.986` is in the corpus at ±0.0005.

ⓘ **The tool's own adjudication ledger had already noticed half of this.**
`.tasks-php/cbaseline_check.py`'s hand table records `.memory-php/03-numbers.md:126`
as a TRUE hit with the note *"`inside_share` '22.24 % on its C rungs' — the four C
cells actually span 20.23–22.69 %"*. That span **is** the `F74` span. The ledger
recorded the discrepancy and nobody read it as a definition mismatch.

▶ **What changes.** The finding's headline stops being *"one definition is
published and the other is only in controls"* and becomes *"the two are
interleaved inside single sentences of the authoritative layer and of the
handoff, with no marker"* — which is **worse**, and which makes `F129`'s
`⛔⛔⛔ READ THIS BEFORE ANY inside_share FIGURE BELOW` box in
`.memory-php/03-numbers.md` **factually wrong about the file it heads**.
**Third instance this session of a repair carrying its own target** is now a
**fourth**.

#### The *"already computed for every cell"* tell

✅ **UPHELD. There is no reading on which it was about the `W` one.** Checked by
date, not by argument: the sentence entered `.memory-php/` at **`bd5dac6`,
2026-09-13** (`git log -S`), and the **first** `controls/inside_share.py` anywhere
in the tree was created at **`af135f9`, 2026-09-15** (`git log --diff-filter=A`).
On the day the sentence was written the `W` quantity had no shipped computation at
all, and it needs a `callgrind` run, so it cannot have been "already computed in
every record".

### 1.2 The `+33 %` and its sign flip

**CONCLUSION — the number reproduces and is one C compiler's:** ✅ **UPHELD.**
**REASON — the column it is contrasted against:** ⛔ **REFUTED IN ITS LABEL.**

**Second method**: `share059.py`, an independent record walk, reproduces every
figure in `F129` §2's table to the digit.

> **STATISTIC A1** (`kernel_exclusive_ir / n_iters`) · **INPUT `large.bin`** ·
> **`O3`/`isolated`** · **BASE `safe_naive`** · **BOTH C COLUMNS MEASURED**:
> `c-gcc` **+33.0086 %**, `c-clang` **−4.3566 %**.
> Same cell, **INPUT `small.bin`**: `c-gcc` **+39.9212 %**, `c-clang` **+0.9530 %**.

⛔ **But the column `F129` contrasts them with is mislabelled.** Its table heads the
second column **"W1 (whole-program marginal)"** and gives `−0.80 %` / `−27.54 %`.
Those are **family B** — `marginal_ir_per_call`, a two-run slope from the gate
record — and `.tasks-php/STATISTICS_001.md` §1 defines **W1** as something else
(`callgrind_annotate`'s `PROGRAM TOTALS / n_iters`, **one** run). The two are not
interchangeable and the layer **disqualifies B twice** (`.memory-php/02-ladder.md`:
*"Family B is disqualified twice — it misses real work (F84) and it is one unstable
draw (F88)"*).

**Second method, and it settles it.** `ph29`'s `controls/inside_share.json` carries
`whole_program_ir` per cell, so the **true W1** is computable without a new run:

> **STATISTIC W1** (`callgrind PROGRAM TOTALS / n_iters`) · **INPUT `large.bin`** ·
> **`O3`/`isolated`** · **BASE `safe_naive`** · **BOTH C COLUMNS**:
> `c-gcc` **−1.1881 %**, `c-clang` **−27.6121 %**.

⭐ **And `−27.61 %` is the figure `.memory-php/02-ladder.md` already publishes for
that cell** (*"A `−4.36 %`, C `−27.78 %`, W1 `−27.61 %`"*). So the layer's W1 is the
real W1 and `F129`'s is B wearing W1's name — **a label defect inside the finding
whose subject is label defects, on the one pair of numbers it puts in a table.**
It does not move the conclusion (`−1.19 %` and `−0.80 %` are both *"C is ~1 %
cheaper"*), which is why this is REASON-refuted and not CONCLUSION-refuted.

**The self-correction, checked.** ✅ The `c-clang` `−4.36 %` really is not new:
`git log -S'−4.36'` puts it in `.memory-php/02-ladder.md` at **`9313449`,
2026-09-14** (*"Land `_049`"*) and in `RECAP_PHP.md` at **`d45db57`, 2026-09-13**.
✅ The residual claim — *a correction reached the layer and the headline cell never
inherited it* — is what the history shows.

**Is `+33.01 %` the number `RECAP_PHP.md` publishes?** ⚠ **Not verbatim, and the
mismatch is in the finding's favour.** `RECAP_PHP.md`'s *which statistic* cell says
**`+33 %`**, with no opt/mode; `.memory-php/02-ladder.md` says **`+33.01 %`** with
`ph29/large`, `A1`, `O3/isolated`. Same cell, same input, same pair, same base.
✅ **So the finding is about that sentence.** ⓘ It could be sharper: the published
sentence omits **the opt/mode** as well as the compiler, so it fails **two** of
`F108`'s five things, not one.

### 1.3 ⭐⭐⭐ The admissibility verdict — **READING (b) WINS**

**CONCLUSION — *"the published comparison is INADMISSIBLE on the row's own written
bar"*:** ⛔ **REFUTED. The word *"inadmissible"* is withdrawn.**
**REASON — *"the published pair's Δ is 0.2355, more than eleven times the bar"*:**
✅ **UPHELD as arithmetic** (`share059.py`: Δ`0.2355`, min-share `0.6911`).
▶ **Net: `F129` §3 is UPHELD-NARROWED.** The manager's prediction **`P2` survives as
written** — the only one of five that does.

#### Four documents say the bar is not a gate, and one of them is the cell that says it is

1. `.tasks-php/STATISTICS_001.md` §4, **THE RULE**, item 2, verbatim:
   > *"`|Δinside_share|` is reported beside them as the **EXPLANATION, never as a
   > gate**. F80's `≤ 0.02` threshold, scored per class, calls **7 real FLIPS** and
   > **13 of the 14 BLIND cells** 'safe' and flags **153** that agree — **20
   > failures, not the 6 F80 published.**"*
2. `.memory-php/02-ladder.md` — **the authoritative layer**:
   > *"⭐⭐⭐ **NO FUNCTION OF THE SHARES CAN CERTIFY A AT ANY THRESHOLD. There is no
   > shortcut: PUBLISH BOTH, LABELLED, ALWAYS.**"*
3. `.memory-php/03-numbers.md`, `F109`: *"**So a high `inside_share` is NOT a
   certificate.**"*
4. ⭐⭐ `RECAP_PHP.md`'s *which statistic* cell — **the same table cell that carries
   the *"inadmissible"* sentence**:
   > *"The rule: publish BOTH, labelled, always — `inside_share` explains a
   > disagreement and **never gates one**, because `s ≡ A/B` so certifying A needs B
   > already."*

The two sentences are **in one cell**, and they contradict each other. That is
`F131`'s own class — *two homes for one fact* — inside the cell `F131` was filed
about.

#### And the gate reading is unsound on a live cell, not merely unsupported

`share059.py` + the gate record, **`O3`/`isolated`**:

> **`ph55` `c-gcc` vs `c-gcc-h`, INPUT `large.bin`.** Both C cells, **same
> compiler**, so `F108`'s fifth thing does not arise; the pair is C-against-C.
> `F74` shares **0.7417 / 0.7515** → **(i) passes at any threshold ≤ 0.74 and
> (ii) passes at `|Δ| = 0.0098`.** **The conjunction ADMITS the pair.**
> **STATISTIC A1** reads **exactly `+0.0000 %`** — the two kernels are
> byte-identical — while **STATISTIC B** (`marginal_ir_per_call`) reads
> **−1.2998 %**, an absolute **66.14 `Ir`/call**, comfortably above the ±14–28
> `Ir`/call instability the layer records for the whole-program column.

So the bar, read as a licence to publish `A1`, licenses a cell on which `A1` is
**provably blind to a 66 `Ir`/call difference** — the exact `ph55` case
`.memory-php/03-numbers.md` already narrates under *"a high `inside_share` is NOT a
certificate"*, now with the conjunction's verdict attached to it. **A gate that
passes its own documented counterexample is not a gate.**

#### What survives, and what the corpus tally means once "inadmissible" goes

The manager's uncommitted one-liner **reproduces exactly** under my independent
enumeration — and it is worth saying plainly that it did, because the brief invited
me to expect otherwise:

> **RULE (ii) ONLY · `F74`'s spelling · `O3`/`isolated` · `small.bin` and
> `large.bin` pooled · the manager's nine pair classes · 11 rows · 198 pairs:**
> cross-language **17 PASS / 71 FAIL (19.3 %)**; same-language **99 PASS / 11 FAIL
> (90.0 %)**.
> **Second method — every unordered cell pair instead of nine hand-picked classes,
> 616 pairs:** cross-language **65 / 287 (18.5 %)**; same-language **203 / 61
> (76.9 %)**. The shape is not an artefact of the pair list.

⛔ **But the sentence built on it must change.** *"Roughly four fifths of this
programme's cross-language comparisons are inadmissible"* does not follow from
reading (b). The defensible sentence is:

> **On 71 of 88 cross-language pairs the two cells' shares differ by more than
> `0.02`, so `A1` and the whole-program column are in the regime where they are
> expected to disagree. That is a reason to publish BOTH columns, labelled — which
> six of the eleven rows already do — and not a reason to withhold either.**

⭐ **And the tally is concentrated, which the percentage hides.** By row
(`share059.py`), cross-language pairs passing (ii): `ph16` **8**, `ph53` **3**,
`ph07`/`ph56`/`ph97` **2** each, and **six rows contribute ZERO** (`ph03`, `ph29`,
`ph45`, `ph52`, `ph55`, `ph64`). **`ph16` alone supplies 8 of the 17.** A
corpus-level *"19.3 %"* reads as a uniform rate and is nothing of the kind.

### 1.3a Item 132 — condition (i), swept on eleven rows

**Sweep done in `F74`'s spelling, as instructed.** `share059.py sweep` and
`share059.py flip`, both populations, `O3`/`isolated`, both inputs.

**Result 1 — (i) is VACUOUS on the cross-language column, and here is why.**

| threshold `t` for (i) | cross-language pairs (ii)-PASS | of those, killed by (i) |
|---|---|---|
| 0.00 … 0.90 | 17 | **0** |
| 0.95 | 17 | 5 |
| 0.99 | 17 | 11 |

The mechanism is **not** *"(ii) already fails on 81 % of them"* (the manager's `P3`
reason). It is that **all 17 survivors sit at min-share ≥ 0.9019**: (ii) forces the
two shares within `0.02` of each other, and in this corpus the cross-language pairs
whose shares are that close are all high-share pairs. The lowest is `ph97`
`c-clang` vs `safe_tuned`/`small.bin` at **0.9019**.

⛔⛔ **Result 2 — and it is the datum item 132 exists for: SIX OF THE SEVENTEEN
SURVIVORS HAVE A MIN-SHARE ABOVE 1.0.** `ph07` `c-gcc`/`c-clang` vs `safe_naive`
(`large.bin`) at **1.0162**, and four `ph16` pairs (`small.bin`) at **1.0232–1.0241**.
▶ **Six of the seventeen cross-language pairs the bar admits are admitted on the
strength of a share that exceeds 1.0** — the §1.4 pathology, inside the bar's own
verdict.

**Result 3 — on the FLIP criterion, which is the one the layer used** (*">0.3,
>0.5, >0.6 all give 0 flips"*), **eleven rows tighten the lower bound and still
cannot pin it.** In the nine-class population there are 22 flips; four pass (ii),
all four are `ph45` same-language pairs at min-share **0.0910–0.0963**, so **any
`t ≥ 0.10` gives 0 flips** — tighter than the layer's `>0.3`. In the all-pairs
population one further flip passes (ii) at min-share **0.9259** (`ph53` `c-gcc-h`
vs `unsafe`, `large.bin`), which would break every threshold up to 0.92 — **but its
whole-program leg is `+0.0372 %`, an absolute `+1.14 Ir`/call, inside the
documented ±14–28 `Ir`/call instability**, so it fails `STATISTICS_001` §4 rule 5's
magnitude-floor requirement and must not be quoted as a flip.

⛔ **Result 4 — the conjunction does NOT exclude the BLIND class at any usable
threshold.** 15 comparisons in which `A1` reads exactly `0.0000 %` against a
nonzero whole-program figure pass (ii); at `t = 0.80` two still pass, at `t = 0.90`
one does. The survivors at high share are the `ph55` C pairs above (0.7417/0.8215)
and `ph03`'s `unsafe` vs `verus` at 0.9340. ⓘ Several BLIND survivors are benign
(`unsafe` vs `verus` on a byte-identical kernel — `A1` is *correctly* zero and B is
the one inventing work), which is the taxonomy inversion
`.memory-php/03-numbers.md` already records. `ph55`'s is not benign.

▶ **ITEM 132's ANSWER, and it closes on it: eleven rows still cannot pin (i), and
the reason is now specific rather than "not enough rows".** (i) has **no discriminating
power on the cross-language column at any threshold in `[0, 0.90]`**, it is
**load-bearing only on the same-language column** (10 kills at `t = 0.10`, 18 at
`t = 0.50`, 37 at `t = 0.90`, of 99 (ii)-PASS same-language pairs), and the
population that would pin it — same-language flips passing (ii) — is **`ph45`
alone**, `n = 1` row. **A threshold fitted on one row's pathology is not a
threshold.** ✅ **Recommend item 132 be CLOSED on that result**, with the operative
sentence being *"(i) is vacuous cross-language and `ph45`-determined same-language;
do not fit it"*.

### 1.4 The over-`1.0` cells — the discriminator run

✅ **The census reproduces exactly**: **15 of 360** evaluable cells, largest `ph07`
`c-gcc`/`large.bin` at **1.035312**, **10 on `ph16` and 5 on `ph07`**
(`share059.py over1`).
⚠ **One clause of the brief is off**: they do **not** all sit at `O3`/`isolated` —
**13 do, and 2 are `O0`** (`ph16` `safe_naive`/`small.bin`, `isolated` and `whole`,
both 1.023278).

**The cheap discriminator, run.** `marginal_at_n.py`, one `callgrind` pair per
reading, total wall clock **under 3 s per pair** on `ph16`/`ph07`.

**Calibration first** — the method reproduces the committed denominator to the
digit, twice:

| | my `[100, 200]` slope | gate record's `marginal_ir_per_call` |
|---|---|---|
| `ph16` `c-gcc`/`O3`/`isolated`/`small.bin` | **3596.61** | **3596.61** |
| `ph07` `c-gcc`/`O3`/`isolated`/`large.bin` | **16442.43** | **16442.43** |

**`ph07` — the discriminator SETTLES it.**

> `c-gcc`/`O3`/`isolated`/`large.bin`, `n_iters` 12000. `A1`/call **17023.04**.
> Marginal at `[100, 200]` **16442.43** → share **1.0353**.
> Marginal at **`[11000, 12000]`** → **17789.12** → share **0.9569**.

**`ph16` — it does NOT settle it.**

> `c-gcc`/`O3`/`isolated`/`small.bin`, `n_iters` 25000. Record `A1`/call **3683.26**.
> Marginal at `[24000, 25000]` → **3689.59** → share **0.9983**.
> ⚠ But my own run's kernel-exclusive total gives `A1`/call **3697.26** (14.0
> `Ir`/call above the record — squarely inside the documented ±14–28 `Ir`/call
> band), and **3697.26 / 3689.59 = 1.0021 — still above 1.0.**

⛔⛔ **And the slope series refutes the mechanism as registered.** Five probe
windows on that one cell:

| window | marginal `Ir`/call | implied share vs my `A1`/call 3697.26 |
|---|---|---|
| `[100, 200]` | **3596.61** | 1.0280 |
| `[1000, 2000]` | 3706.31 | 0.9975 |
| `[6000, 7000]` | 3701.74 | 0.9988 |
| `[12000, 13000]` | 3641.34 | 1.0154 |
| `[24000, 25000]` | 3689.59 | 1.0021 |

The series is **non-monotone**, its spread is **109.7 `Ir`/call ≈ 3.0 %** of the
mean, and the published `[100, 200]` pin is **the lowest of the five**. ▶ **So this
is not a systematic "mean over `n_iters` vs slope at `probe_iters`" scale effect.
It is a DRAW effect** — `F88`'s heterogeneous per-window work and `F93`'s low
start-of-run pin — **and on this row the two candidates `F129` presents as rivals
are the same phenomenon.** The named discriminator therefore **cannot discriminate
between them**, because they are not disjoint.

▶ **What I would put on the record:** *the excess over 1.0 is dominated by the
denominator's draw, `[100, 200]` is low on both offending rows, and re-basing on an
`n_iters`-scale window removes all of it on `ph07` and most of it on `ph16`. The
residue on `ph16` is inside the whole-program column's own instability band, so its
sign is not resolvable by this method.* ⛔ **Still do not quote a bare `F74` share
above 1.0**, and note that `ph16`'s own `NOTES.md` already says so.

### 1.5 The two cheap clauses

**§5 — *"the repair shipped the defect it repairs"*.**
**CONCLUSION:** ✅ **UPHELD.** **REASON:** ✅ **UPHELD** — and the repair **shipped a
second defect of the same class**, which is §1.1's corpus clause above.
✅ The file is byte-identical across `ph03`, `ph16`, `ph29` and `ph97` (one
`sha256`), so *"is it right in all four"* is answered by one hash. The two shares
are now **labelled inline** (`F74's share 0.8045` / `THIS file's W 0.8933`) and the
labelling is correct.

⚠ **Two further defects the repair introduced, both reported and neither repaired
by me:**

* **`patterns-php/ph16-fdset-index/NOTES.md:924`** — *"`ph45`'s much-quoted
  0.055–0.094 is the OTHER definition and is not comparable with the column
  above."* ⛔ **Unsupported, and probably backwards.** `.memory-php/02-ladder.md:397`
  introduces `0.055–0.094` inside the paragraph stating `F74`'s corrected rule, and
  under `F74` `ph45`'s `large.bin` `O3`/`isolated` cells run **0.0506–0.0942** with
  `c-gcc` at **0.0551** and `safe_tuned` at **0.0942** — the stated endpoints
  exactly. ⓘ **I could not refute it numerically, and say so**: my own `callgrind`
  run gives the `W` values for the same two cells as **5.52 %** and **9.44 %**, so
  on this row the two definitions agree to 0.02 pp and **the number cannot identify
  its own definition.** ▶ The defect is that a row's `NOTES.md` **asserts a
  definition it has no way to know**, in the section whose purpose is labelling.
* **`patterns-php/ph16-fdset-index/NOTES.md` §8.6 mixes the two quantities in
  adjacent tables.** The LEVEL matrix is `W` (99.20–99.66 %); the Δ table beneath it
  is **`F74`'s** — `c-gcc` vs `safe_naive`/`small.bin` reads `0.0038` there, and
  `F74` gives `1.024091 − 1.027883 = 0.003792` while `W` gives `0.0002`, **19×
  apart**. ⓘ The section *does* say so, but two paragraphs **after** the table and
  obliquely (*"a difference of two such ratios"*). ▶ **Legibility defect, not a
  labelling absence** — but it is the defect `F129` §5 is about, one row on.
  ✅ **The Δ column being `F74`'s is CORRECT** and is what §1.3a asked for.

**§4/§4a — the prediction score.**
**CONCLUSION — *"ZERO OF FIVE SURVIVED AS WRITTEN"*:** ⛔ **REFUTED.**
**REASON — the per-prediction reasoning:** ✅ **UPHELD on `P1`, `P2`, `P5`;
REFUTED on `P3`; CIRCULAR on `P4`.** ⭐ **And the error runs AGAINST the manager, not
for him — the self-score is harsher than the evidence warrants.**

* **`P1`** (four docstring numbers reproduce, and the cell is `small.bin`) — ✅ the
  split is real and reproduces: `0.655`, `0.669`, `0.927` all land at **`large.bin`**
  (`share059.py --find`-equivalent search). Scored honestly.
* **`P2`** (no cell reproduces all four, *because* the C figure names no compiler) —
  ✅ scored honestly, and the *"right reason that does not entail its conclusion"*
  characterisation is exactly right: the columns **do** differ (`c-gcc` 0.926592 vs
  `c-clang` 0.912150 at `large.bin`), and a figure needs to match only one of them.
* **`P3`** (`ph03` and `ph16` read high on every cell) — ⛔ **the refuting datum is
  the wrong quantity in a scope the deliverable does not cover.** `P3` is a
  prediction about the control's output; `ph16`'s `controls/inside_share.json`
  records `cell_spec: "O3 / isolated"` and **has no `O0` cells at all**. The datum
  offered against it, *"`ph16` `c-gcc` reads `0.0418`"*, is an **`F74`** share at
  **`O0`**. In the control's own spelling and scope — read from the two rows'
  committed `controls/inside_share.json` at `c868e60` — **`ph16` spans
  99.20–99.66 % and `ph03` spans 90.13–99.18 %, and NOT ONE of the 32 cells is
  below 90 %.** ▶ **`P3` is UPHELD AS WRITTEN.** (`ph29`, for contrast, spans
  66.9–95.0 %, which is why `P3` named only the other two.)
* **`P4`** (the `+33 %` is under-qualified rather than false; the honest fix is a
  label) — ⚠ **scored as upheld-NARROWED, and the only thing narrowing it is §3's
  *"inadmissible"*, which this round withdraws.** ▶ **On reading (b), `P4` is UPHELD
  AS WRITTEN.**
* **`P5`** (the bar has no written definition) — ✅ **REFUTED, correctly and
  self-critically.**

▶ **CORRECTED SCORE: TWO OF FIVE SURVIVE AS WRITTEN (`P3`, `P4`); `P1` and `P2`
split; `P5` refuted.** ⛔ **The headline number was coupled to the clause under
review**, so it could not have been scored independently — which is itself worth
recording as a method note: **do not score a prediction against a finding published
in the same task.**

---

## §2 `F130` — the ratchet

**CONCLUSION — *"the corpus had already drifted past its adjudicated baseline and
no run anywhere would have said so"*:** ✅ **UPHELD.**
**REASON — *"A RATCHET THAT NOTHING EVER INVOKED … NOTHING PASSED IT"*:**
⛔⛔ **REFUTED.**

**Second method for the drift.** Rather than a worktree, I materialised the 31
scanned files at `1cc2c0e` with `git show` into `.temp/rev059/` and ran the
`1cc2c0e` copy of the tool against them: **`scanned 31 file(s); 70 hit(s); ratchet
69`**. Reproduced. At `42d66e9` and `5563228` the same procedure gives **69 / 69**.

#### ⛔⛔ It WAS invoked — by hand, by name, and there is a report of the output

* `.tasks-php/TASK_PHP_051.md:171` — *"`.tasks-php/cbaseline_check.py --ratchet`
  before finishing; adjudicate any …"*
* `.tasks-php/TASK_PHP_052.md:90` — *"Run `.tasks-php/cbaseline_check.py
  --ratchet`;"*
* `.tasks-php/TASK_PHP_051_REPORT.md:55` — **the run, with its output**:
  *"`.tasks-php/cbaseline_check.py --ratchet` | **rc 0** — 68 hits, ratchet 69"*, and
  at `:60` the agent records the tool's *"lower RATCHET to 68"* advice and declines
  it with a reason.

▶ **The claim that survives is narrower and still worth having:** *no **automated**
caller passed the flag — `checkers.py` files the tool with `argv=[]` plus a
`--selftest` arm, so enforcement depended on a task file remembering to ask for it,
and after `_052` no task file did.* ⛔ **That sentence is in the tool's own source
comment and in `RECAP_PHP.md` in the refuted form**, so the repair is a wording fix
in two places.

#### Regression or birth defect? — **BIRTH DEFECT**

`git log` on the file gives four commits. The guard `if '--ratchet' in argv` is
present in **the file's first commit**, `9313449` (2026-09-14 01:17 UTC, `_049`),
with `RATCHET = 63`, and in every commit until `d9652b4` (2026-09-15 09:38 UTC).
**Nothing unwired it; it was never wired.** ⓘ The un-enforced window is therefore
**about 32 hours and three commits**, not the open-ended stretch the finding's tone
suggests — and the ratchet was raised by hand, with adjudications, **twice** inside
that window (63 → 66 → 69).

#### ⛔ The unattributed 70th hit — **FOUND, and it is benign**

Diffing the hit sets at `42d66e9` and `1cc2c0e` by unit text (line numbers move):
**NEW 2, GONE 1, net +1.** One of the two "new" is the `RECAP_PHP.md` **Index**
unit, whose text merely shifted. The real arrival is:

> **`RECAP_PHP.md:1812` at `1cc2c0e` — the body of `F127` itself**, the paragraph
> *"AND `ph29` IS WORSE THAN MISSING … **It is made elsewhere**: this file's *which
> statistic* cell publishes *'on `ph29/large` A says C is +33 % dearer than naive
> safe Rust'*"*.

▶ **Adjudication: BENIGN, and it is the SAME CLASS the manager adjudicated one hit
later** — *a quotation of the defective sentence, made in order to criticise it*,
scoring as the defect. Item 115's class. ⭐ **So it is the EIGHTH instance, not the
seventh,** and *"the ratchet is honest again from 77, not retrospectively"* can be
strengthened: **the single unattributed hit is now attributed and benign, so the
ratchet is honest retrospectively too.**

### 2.1 My own adjudication of the eight new hits

Reproduced by diffing `1cc2c0e` against the working tree: **NEW 8, GONE 1**, exactly
the eight the finding names. **I agree that all eight are benign.** Three
disagreements on the *reason*:

| hit | manager's reason | mine |
|---|---|---|
| `ph03` `NOTES` 1317 | *"LINE-BOUNDARY artefact — sentence continues on the next line"* | ⛔ **Wrong mechanism.** The checker's unit is a **blank-line-separated paragraph**, not a line, and `BASE` is searched over the whole unit. It is flagged because the unit says *"Both C columns are present"* and never spells `c-gcc`/`c-clang` — i.e. **the `BASE`-spelling class**, the same class as `ph29` 1157, not a line boundary. ✅ benign |
| `ph03` `NOTES` 1352 | *"R1-vs-R1h — C against C, same compiler. Not x-language"* | ⚠ **Incomplete.** The unit *does* carry a cross-language sentence (*"Its CROSS-LANGUAGE pairs FAIL (ii) on both C columns"*), but carries **no cross-language magnitude** — the `+3.64 %` in it is the same-language null pair's. ✅ benign, on a different ground |
| `ph97` `README` 115 | *"a markdown table header. Normaliser artefact"* | ⚠ **Not a normaliser artefact.** It is a real unit: `MAG` matches `+0.0000 Ir` (in the `optional_cost.py` row) and `XLANG` matches two bare `C`s. ✅ benign — the `Ir` figure is a Rust-vs-Rust control's, not a cross-language one |

✅ Agreed as written: `ph03` 1335 and `ph16` 933 (the `F109` `ph55` **74–83 %** share
quote, same text in both rows), `ph16` 921 (*"EVERY CELL IS 99.20–99.66 %"*, a share
range), `ph29` 1145 (**the quotation-of-a-defect case**), `ph29` 1157 (**names both
columns as `gcc-C`/`clang-C` and is flagged on a spelling — confirmed, and it is the
sharpest hit in the set**).

ⓘ **One accounting note.** *"`RECAP_PHP.md` went 35 → 34, so eight arrived and one
left"* is arithmetically right, but **the departure is a checker artefact, not a
repair**: the `RECAP_PHP.md` **Index** unit stopped hitting because a later finding
title added the literal string `c-gcc` to it, so `BASE` now matches. ▶ **The ratchet
absorbed one new hit under cover of an accidental departure**, which is worth a line
in the ledger.

### 2.2 ⚠⚠ Item 134 — **MY RULING: REFUSE the widening as framed; do a different, cheaper repair**

**The premise checks out.** `cbaseline_check.py::selftest`'s `scores()` is
`MAG and XLANG and not BASE`, `BASE` is `c-(?:gcc|clang)(?:-h)?`, and the `N2`
must-NOT-fire exemplar is, verbatim at `c868e60`:

> `` `ph29/large`, `c-gcc` vs `safe_naive`: A says C is +33.01 % DEARER. ``

One column, of the pair whose columns have opposite signs. ✅ **The enforcer's model
of compliance is one item short of the rule it enforces.**

⛔ **But the stated SCOPE prices the wrong population, and is ~4× low.** The item
says *"5 lines name BOTH C columns and 2 name exactly one"*. On **lines** I measure
**6 both / 2 one** — close enough, the count moved. **On UNITS — which is what the
checker actually scans, and therefore what a `BASE` change would be evaluated on —
I measure 22 both / 10 one.**

⛔ **And *"there is NO live violation"* is FALSE on that population.** Two of the ten
one-column units are the same sentence, and it is the sentence `F129` is about:

* `RECAP_PHP.md:5281` — *"`ph29/large c-gcc vs safe_naive` is the sentence this is
  about: A says C is **33 % dearer** than naive safe Rust; three other statistics say
  **~1 % cheaper**."* One column, no clang column, no *"only one was measured"*.
* `.tasks-php/STATISTICS_001.md:92` — the same sentence. (That file is marked NOT
  AUTHORITATIVE, which mitigates but does not cure.)

Both currently **PASS** the checker.

**THE RULING.** ⛔ **Refuse the *"make `BASE` demand both spellings"* widening — an
eighth refusal, and here is the reason in terms of these two hits.**

1. ⭐⭐ **The two hits pull in OPPOSITE directions and are not one repair.**
   `ph29` 1157 wants `BASE` to recognise **more** spellings (`gcc-C` / `clang-C`);
   the `N2` exemplar wants `BASE` to demand **both** columns. Demanding both does
   **nothing** for `ph29` 1157 — it makes that line a hit for a **second,
   independent** reason. *"It cuts both ways"* is true of the **evidence** and false
   of the **repair**.
2. **The rule is a DISJUNCTION and half of it is not regex-decidable.**
   `.memory-php/03-numbers.md` says *"with both columns, **or an explicit statement
   that only one was measured**"*. A `BASE` that demands both implements only the
   first disjunct and would flag every legitimately-single-column unit — of which the
   ten include at least four (`ph64` `NOTES` 507's `O0` row, which cites the
   `O0` prohibition itself; `ph16` `README` 33, where naming gcc *is* the finding;
   `ph45` `NOTES` 353, a within-cell share; `.memory-php/02-ladder.md:170`, which
   gives the clang swap two lines later). Spelling *"only one was measured"* for a
   regex is `F10` one level up.
3. **The adjudication cost is 10 units, not 2**, and the ratchet moves by more than
   the item prices.

✅ **What I would do instead, and it is cheap (my estimate: ~15 minutes, NOT
measured):**

* **(a) LOOSEN `BASE` to recognise `gcc-C` / `clang-C`.** A pure false-positive
  removal that does not weaken the rule, and it retires the eighth bare-spelling
  instance **in the direction that instance actually points**. It lowers the hit
  count by one — a *"lower RATCHET"* move the house rule already provides for.
* **(b) Fix the `N2` exemplar** so the enforcer's model of compliance is not itself
  one item short: make `N2` assert that a **both-columns** sentence does not score.
* **(c) Add an `ⓘ` REPORT arm — not a verdict — listing units that carry a
  cross-language magnitude and name exactly one C column.** That prints today's ten,
  makes the disjunction's second branch a human judgement instead of a regex, and
  obeys `quota.py`'s discipline and `F128`'s Kind-A/Kind-B rule at once.
* **(d) Adjudicate the two live ones by hand** — `RECAP_PHP.md:5281` and
  `STATISTICS_001.md:92` — which need the `c-clang` column added to the sentence,
  not a checker change.

⛔ **Note for the manager: (a), (b) and (c) are edits to `.tasks-php/`, which I am
permitted to make. I deliberately did NOT make them**, because (a) moves the ratchet
and (d) is a `RECAP_PHP.md`/`.memory-php/` edit that only the manager may land, and
splitting one repair across two agents is how a half-repair ships.

---

## §3 `F127` — did `_058` test it, and did it close it?

**CONCLUSION — five built rows never measured `inside_share`, three publish an `A1`
headline:** ⚠ **UPHELD-NARROWED.**
**REASON — as stated, unqualified by which quantity:** ⛔ **REFUTED — `F127` is
itself a casualty of `F129`'s name collision.**

⭐⭐ **The sharp point: `F127`'s claim is true of the `W` quantity and FALSE of
`F74`'s.** `F74`'s share is **arithmetic over two committed records** and is
therefore already available for **all 360 evaluable cells of all eleven rows** — as
`.memory-php/03-numbers.md` says in terms (*"ALREADY COMPUTED FOR EVERY CELL IN
EVERY RECORD"*), and as `share059.py` demonstrates in 0.3 s with no build.
▶ **So *"five built rows never measured `inside_share`"* means *"five rows ship no
`W` control"*, and the remedy `_058` shipped measured the quantity the rule is
**not** stated in.** `F74`'s bar — the two conditions — is stated over `F74`'s
share, and that half was never missing.

**Was the scoping right?** ⚠ **The selector is right for the `W` remedy and moot for
the other half.** *"Publishes an `A1` headline"* correctly picks the rows whose
published claim most needs a whole-program companion. But under reading (b) the bar
is not a gate, so **no row "owes a share" in order to publish** — §1.3's landing
removes the argument that would have made the residue load-bearing. ▶ **The residue
(`ph07`, `ph53`, `ph64`) is bookkeeping, and should be priced as such.**
ⓘ **Cost is row-dependent and I did not measure it for those three.** Measured
comparators: a `ph16` `small.bin` cell costs **0.2 s** under `callgrind`; a `ph45`
`large.bin` cell costs **~60 s**. A sixteen-cell matrix is therefore anywhere from
seconds to ~20 minutes per row.

**Does `F129`'s correction weaken or strengthen `F127`?** ⛔ **The manager says
stronger. That verdict is CONDITIONAL ON READING (a), which this round refutes.**

* `F127`'s reason contained an **identity claim** — *"the **exact** comparison the
  row's own control disclaims"*. It is false: the docstring disclaims C vs
  `safe_tuned` (Δ `0.2715`), the headline publishes C vs `safe_naive` (Δ `0.2355`).
  Both re-derived independently (`share059.py`).
* Under reading **(a)** the correction strengthens: *"and the published pair is
  inadmissible too."*
* Under reading **(b)**, which wins, it **WEAKENS**: a disclaimer that names a
  *different* pair is weaker evidence than one that names the same pair, and
  *"the neighbouring pair has a similar Δ"* is an inference, not a disclaimer.
* ✅ **`F127`'s CONCLUSION survives anyway, on a ground that needs no bar at all**:
  `RECAP_PHP.md` publishes a **one-column, opt/mode-unlabelled, cross-language `A1`
  figure**, which violates `F108`'s fifth thing and its third. That is a defect on
  the authoritative layer's own labelling rule, independent of `F74` entirely.
  ▶ **Re-state `F127` on `F108`, not on `F74`'s bar.**

---

## §4 `F128` — the Kind-A/Kind-B rule and the unswept checkers

**CONCLUSION — `N13` asserted a sign and the rule as first worded is too broad:**
✅ **UPHELD.** **REASON — the replacement rule:** ⚠ **UPHELD-NARROWED; its boundary
is not where the rule puts it.**

### The boundary — *published* and *being estimated* are not disjoint, and the rule has no transition

⭐⭐ **The Kind-A/Kind-B split is not a property of the ARM. It is a property of the
arm's RELATION to a finding's current status — and that status changes without the
arm changing.** `F126` is the worked example already on file: `N11` was a textbook
Kind A arm (it defended the published first-in-family premium) right up to the
moment the premium was refuted at `n = 8`, at which point it became a textbook Kind
B arm — **with no edit to the arm**. The rule as written classifies arms; nothing
re-classifies them when a finding falls.

▶ **So the rule's second half is not a nicety, it is the whole mechanism**: *"and
then it **must print the measured margin** beside the floor, so the margin is
visible shrinking."* An arm that prints its margin converts a refutation into a
**visibly shrinking number** instead of a hard failure, which is precisely the
Kind-A→Kind-B transition handled safely. **An arm that asserts a published
direction without printing the margin is a Kind B arm that has not been caught
yet.** ✅ **I would land the rule with that sentence in it**, and with `width.py`
`N4`/`N3b` named as the model, which the sweep already does.

⛔ **A second gap: the rule has no RETIREMENT condition**, which the sweep itself
noticed on `task_cost.py` `N6` (*"a registered prediction with no expiry becomes a
pin"*) and then did not generalise.

### ⛔⛔ Open item 130's *"`N5` … STILL UNREPAIRED"* is STALE — and stale by the same mechanism it is about

`RECAP_PHP.md` item 130 reads *"⛔⛔ `task_cost.py` `N5`, THE THIRD INSTANCE, **STILL
UNREPAIRED** … ▶ **REPAIR OWED: demote `not rising` to an `ⓘ` report.**"*

**It is done.** At `c868e60` — and already at `f98e716`, the commit the brief's own
premises were measured at — `task_cost.py`'s live predicate is

```
check("N5", max(ser) - min(ser) > 1.0, …)
```

with an `ⓘ  N5b REPORT (no verdict)` printing the direction and saying in terms
*"the direction is NOT asserted — if it ever turns, that is a RESULT"*. The string
`not rising and` survives **only inside a comment** documenting the repair.
`git log -S'N5b REPORT'` dates the repair to **`d9652b4`, 2026-09-15** — **one commit
after `cddd82b`, where the *"STILL UNREPAIRED"* cell was written.**

⛔ **So the claim was falsified by the manager's own next commit and then survived
`f98e716`, a commit whose message is *"Pre-compact audit"*.** That is `F129`'s own
defect class — *a correction lands in one place and the other place that states the
same thing never inherits it* — and `F131`'s *two homes for one fact*, inside the
item that documents the sweep that produced the repair.

⚠ **And it is very likely the SAME reading error the sweep's census already made
once.** The census miscounted by reading a `check("N15b"…` **quoted inside a
comment**; the only `not rising and` in the file is a `check("N5", …` **quoted
inside a comment**. **Item 115's class, twice in one sweep, and the second time it
produced a live open item asking for work that was already done.**

### The sweep of `cbaseline_check.py` — done, and the residue priced

Read all ten arms (`N1`–`N9`, `N8b`), which the registry confirms:
`ok cbaseline_check.py claims 10 observed 10`.

* ⚠ **`N9` is a Kind B arm.** *"A checker that finds nothing on a corpus known to
  contain the defect is broken, not clean"* — `if len(hits()) == 0: fail`. The
  corpus containing the defect is an **empirical, mutable** fact; if every figure
  were ever labelled, `N9` would report the **good outcome as a tool failure**.
  ⓘ **Low severity** (the count is 77 and the trigger is 0) but the **shape is
  identical to `N11`/`N13`/`N5`**, and like `task_cost.py` `N6` it has **no
  retirement condition**.
* ⭐ **`N7` is the model the rule prescribes, and it is in the file the sweep
  skipped**: *"N7 THE RATCHET MUST BE ABLE TO FAIL. **Assert the comparison, not the
  data.**"* — `if not (RATCHET + 1 > RATCHET)`. That is the correct discipline
  written out in one line.
* ⓘ `N8`/`N8b` assert a **count** (`len(SCAN) < 10`) — `F121`'s class, benign here
  because the bound is a floor, not an equality.

▶ **IS THE RESIDUE WORTH A TASK? NO — worth a folded-in half-hour.** One of the six
unswept files produced **one** low-severity Kind B arm and **one** exemplary arm.
▶ **The higher-value work is not more hunting; it is applying the rule's second half
— *print the measured margin* — to the five already-identified Kind A arms.**

### Spot-check of the recount

✅ **`16` reproduces.** `task_cost.py --selftest` prints **16 `PASS`/`FAIL` verdict
arms** and **6 `ⓘ` reports**, and `checkers.py` independently prints
`ok task_cost.py claims 16 observed 16`. **The `ⓘ` reports correctly do not count.**

⚠ **`59` does not reproduce today.** The four swept files print, at `c868e60`:
`task_cost.py` **16**, `php_null.py` **14**, `width.py` **12**, `checkers.py` **20**
— **62** verdict arms. ⓘ **This is not asserted as a miscount**: `git diff --stat
1cc2c0e..c868e60` shows `checkers.py` and `task_cost.py` both gained ~140 lines since
the sweep, so arms were added. ▶ **It is `F121`'s trap all the same — the count is in
prose about the tools and it has already moved. Do not quote `59`; derive it.**

---

## §5 THE MANAGER'S FIVE PREDICTIONS — scored

| | prediction | CONCLUSION | REASON |
|---|---|---|---|
| **P1** | the name collision survives **as written**; definitions do not narrow | ⛔ **REFUTED in its corpus clause** — `ph97`'s `98.84 % → 64.50 %` in `RECAP_PHP.md` and `ph52`'s `22.24 %`/`≈98.6 %` in `.memory-php/03-numbers.md` are the **`W`** one | ⛔ **the reason is the error** — *"a definitional fact, not an inference"* is true of the two DEFINITIONS and false of the CORPUS CLAUSE, which is an empirical claim about every figure in three documents and was never checked. ✅ The definitional half is upheld and **under-stated** (the gap is 8.9 pp on `ph29`, 0.01 pp on `ph45`) |
| **P2** | §1.3 lands on **(b)**; *"inadmissible"* withdrawn; `F129` §3 **UPHELD-NARROWED** | ✅✅ **UPHELD AS WRITTEN — the only one of five** | ✅ **UPHELD, and stronger than the stated ground.** The manager's ground was `STATISTICS_001.md`'s *"explains a disagreement and never gates one"*. Three further documents say it, one of them the **authoritative layer** (*"NO FUNCTION OF THE SHARES CAN CERTIFY A AT ANY THRESHOLD"*), and one of them **the very `RECAP_PHP.md` cell that carries the *"inadmissible"* sentence.** ⭐ Plus a measured counterexample: `ph55` `c-gcc` vs `c-gcc-h`, `large.bin`, `O3`/`isolated`, both C cells same compiler — the conjunction admits a pair on which `A1` reads `+0.0000 %` against **66.14 `Ir`/call** |
| **P3** | no threshold for (i) in `[0.3, 0.9]` changes any cross-language verdict | ✅ **UPHELD — and wider: no threshold in `[0.00, 0.90]` does** | ⛔ **REFUTED.** Not *"because (ii) already fails on ~81 %"*. **All 17 (ii)-survivors sit at min-share ≥ 0.9019**, so (i) is vacuous there by construction — (ii) forces the shares together and the close-shared cross-language pairs in this corpus are all high-share. ⭐ **And six of the seventeen have min-share ABOVE 1.0** |
| **P4** | the over-`1.0` mechanism **will be isolated**, and **will be** the slope, not a transient | ⚠ **SPLIT. UPHELD on `ph07`** (1.0353 → **0.9569** when the marginal is taken at `[11000, 12000]`); ⛔ **REFUTED on `ph16`** (1.0241 → **1.0021** against my own numerator, still above 1) | ⛔ **REFUTED.** The five-window slope series on `ph16` (**3596.61 · 3706.31 · 3701.74 · 3641.34 · 3689.59**) is **non-monotone**, spread **3.0 %**, with the published `[100, 200]` pin **the lowest**. That is a **DRAW** effect — `F88` + `F93` — so on this row the two candidates are **the same phenomenon** and **the named discriminator cannot discriminate between them** |
| **P5** | item 134 judged **WORTH DOING**; the eighth instance flips the seven-time refusal | ⚠ **SPLIT. The false-positive half is worth doing; the *"require both"* half is REFUSED — an eighth refusal** | ⛔ **REFUTED.** *"It fails in both directions at once"* is true of the **evidence** and false of the **repair**: the two hits want `BASE` **loosened** and **tightened** respectively, and doing the second makes the first a hit for a second reason. ⛔ Plus the scope is ~4× low on the checker's own population (**22 both / 10 one by unit**, vs 6/2 by line) and *"no live violation"* is **false** — `RECAP_PHP.md:5281` and `STATISTICS_001.md:92` |

▶ **One survives as written (`P2`), two split, two are conclusion-or-reason
refuted.** ⭐ **`P2` was the one the manager marked *low confidence* and predicted
against his own finding's strongest clause. It is the one that held.**

---

## § WHAT I AM UNSURE OF

1. **Whether `0.055–0.094` is `F74`'s or `W`'s on `ph45`. I could not decide it and
   I say so.** My `callgrind` run gives `W` **5.52 %** (`c-gcc`) and **9.44 %**
   (`safe_tuned`) at `O3`/`isolated`/`large.bin`; `F74` gives **5.51 %** and
   **9.42 %**. **The two definitions agree to 0.02 pp on this row**, so the number
   identifies nothing. My finding is only that `ph16` `NOTES.md:924` **asserts** a
   definition it has no evidence for, and that `.memory-php/02-ladder.md:397`
   introduces the range inside `F74`'s own rule paragraph, which points the other
   way. **Cost of settling it properly: it cannot be settled from the numbers.**
2. **The `ph16` over-1.0 residue.** After re-basing on an `n_iters`-scale window the
   share is **1.0021** against my own numerator and **0.9983** against the record's.
   The two numerators differ by **14.0 `Ir`/call**, which is exactly inside the
   ±14–28 `Ir`/call band the layer documents, so **the sign of the residue is not
   resolvable by this method.** Settling it needs a numerator and a denominator from
   **one** run in **one** shell. **Measured cost of one such run on that cell: 0.9 s.
   I did not do it** because the measurement record's numerator is the published one
   and replacing it is an engineer's call, not a reviewer's.
3. **Whether the sweep's `59` was ever right.** The four files gained ~260 lines
   since `1cc2c0e`, so `62` today is consistent with `59` then. **I did not
   reconstruct and run them at the sweep's commit** — that needs the whole tree
   materialised, and I judged the answer not worth it. **Estimate, not measured:
   ~10 minutes.**
4. **The `.temp/` generators.** `share059.py` and `marginal_at_n.py` are under
   `.temp/`, which is gitignored. **Every number in this report that is not a
   `git show` or a quotation comes from one of them, and if `.temp/` is cleared they
   are not re-derivable without re-writing the scripts.** ▶ **This is `F99`/`F116`'s
   defect and I am flagging it rather than committing a fix I am not allowed to
   commit.**
5. **`ph07`'s kernel symbol.** My hand parser returned `0` kernel-exclusive `Ir` on
   `ph07` and an over-count on `ph45`; I discarded it and used
   `callgrind_annotate` for every `W` figure above. **The whole-program totals from
   my `summary:` parse are sound** — they reproduce two committed marginals to the
   digit — but **do not reuse `marginal_at_n.py`'s kernel-exclusive column.**
   ⚠ **Its `--selftest` does not cover that column**; the script is a probe, not a
   validator, and should not become one without arms.
6. **I did not attack `F131`.** The brief scopes it *"by implication, not as a
   section"*. I read the RULE-9 table and used it; its one-row-per-key shape held
   while I read it, and the four `⛔ UNREVIEWED` rows are the four I verdicted.

---

## § WHAT I DID NOT DO

* **I did not re-run any gate, build, measurement or `--check-stale` bracket.**
  Nothing in this report needed one, exactly as the brief said.
* **I did not verdict `F131`** (see above).
* **I did not sweep the other five unswept checkers** — `quota.py`, `citecheck.py`,
  `contract_audit.py`, `preimage_screen.py`, `fixsurvey.py`. I swept
  `cbaseline_check.py` only, as §4 instructed, and priced the residue from that one
  sample.
* **I did not measure the `W` share for `ph07`, `ph53` or `ph64`**, so §3's residue
  is priced by analogy to `ph16` and `ph45` and not directly.
* **I did not repair anything.** No `.tasks-php/` tool was edited, so the registry
  run below is a baseline, not a re-validation.
* **I did not check whether the eight new hits are the only corpus changes since
  `1cc2c0e`** — I diffed the **hit sets**, not the documents.

---

## § ORDER TO RESUME IN

I reached all four sections. What is left is work this round *created* or
*deliberately left*, in the priority I would give it. **This ordering binds.**

1. ⭐⭐⭐ **Land §1.3 — withdraw *"inadmissible"* from `F129` §3, from `RECAP_PHP.md`'s
   *which statistic* cell, and from `F127`'s correction box.** It is currently in
   the same cell as its own refutation. **Highest stakes, and it is a wording edit
   over an already-settled argument.** ⓘ Do it before anything else touches that
   cell.
2. ⭐⭐⭐ **Repair §1.1's corpus clause in the four-row control.** It is **false**, it
   is hashed into four rows, and it is the sentence a future agent will trust.
   ⚠ **This costs four re-gates (~2 m 30 s each by the brief's own figure) and is
   the only item here that costs a gate run** — so batch it with any other pending
   edit to that file, including the `ph16` `NOTES.md:924` and §8.6 items, which are
   in the **gate** digest and not the measurement digest.
3. ⭐⭐ **Correct `F129` §2's column label**: the *"W1"* column is **family B**, and
   the real W1 for the same cell is **−1.1881 % / −27.6121 %**, one of which the
   authoritative layer already publishes. **Free — a table header and two numbers.**
4. ⭐⭐ **Correct `F130`'s headline** to *"no automated caller invoked it"*, record
   the **birth-defect** finding, and attribute the 70th hit to `RECAP_PHP.md:1812`
   as **benign, item 115's class, eighth instance**. **Free.**
5. ⭐⭐ **Strike item 130's *"`N5` … STILL UNREPAIRED"*** and replace it in place
   (never beside) with the repair's commit. **Free, and it is a live false claim in
   the open-items table.**
6. ⭐ **Close item 132** on §1.3a's result: *(i) is vacuous cross-language at any
   `t ≤ 0.90` and `ph45`-determined same-language; eleven rows cannot pin it and the
   reason is now specific.* **Free.**
7. ⭐ **Item 134: do (a)+(b)+(c) and refuse the *"require both"* widening**, with the
   reason stated in terms of the two hits. **My estimate ~15 minutes, NOT measured.**
   Then **(d)**, the two live one-column sentences, which is a `RECAP_PHP.md` edit.
8. **Re-score `F129` §4a to two-of-five** and record the method note: *do not score a
   prediction against a finding published in the same task.* **Free.**
9. **Item 127's residue (`ph07`, `ph53`, `ph64`)** — re-price as bookkeeping, not as
   a precondition. **Lowest priority of this list**, and §1.3's landing is why.
10. **The five unswept checkers** — fold a half-hour into another task; do not
    dispatch one. **And put the *print the measured margin* clause into the Kind-A
    rule before sweeping anything else**, because that is what makes the sweep's
    output actionable.

---

## § FOR THE MANAGER — numbered, routed

1. **`F129` §1 corpus clause is FALSE.** Needs a `RECAP_PHP.md` edit, a
   `.memory-php/03-numbers.md` edit (its `⛔⛔⛔ READ THIS BEFORE ANY inside_share
   FIGURE BELOW` box is wrong about its own file), and a **four-row control edit
   costing four re-gates**. Evidence: §1.1. **Decision owed: batch or defer.**
2. **`F129` §3: withdraw *"inadmissible"*; `F129` §3 is UPHELD-NARROWED; `P2`
   survives.** `RECAP_PHP.md` edit. Evidence: §1.3.
3. **`F129` §2 mislabels family B as W1.** `RECAP_PHP.md` edit. The true W1 is
   `−1.1881 %` (`c-gcc`) and `−27.6121 %` (`c-clang`), `ph29`, `large.bin`,
   `O3`/`isolated`, base `safe_naive`, both C columns. Evidence: §1.2.
4. **`F129` §4a: the score is TWO of five, not zero.** `P3` and `P4` are upheld as
   written. `RECAP_PHP.md` edit. Evidence: §1.5.
5. **`F130`'s headline is refuted; the narrower claim stands; it is a birth defect;
   the 70th hit is found and benign.** `RECAP_PHP.md` edit **and** a source-comment
   edit in `.tasks-php/cbaseline_check.py`, which carries the refuted sentence too.
   Evidence: §2.
6. **Item 134: my ruling is REFUSE-AS-FRAMED plus a three-part cheaper repair.**
   Needs the manager's go-ahead because part (a) moves the `RATCHET` and part (d) is
   a `RECAP_PHP.md` edit. Evidence: §2.2. ⛔ **`P5` is scored SPLIT, not upheld.**
7. **Item 130's `N5` cell is a live false claim.** Strike in place. Evidence: §4.
8. **Item 132 closes** on §1.3a. Evidence: §1.3a.
9. **`F127` should be re-stated on `F108`, not on `F74`'s bar** — its conclusion
   survives on the labelling rule and needs no bar. Evidence: §3.
10. ⚠ **`F128`'s Kind-A rule needs one sentence added before it lands**: *an arm that
    asserts a published direction without printing the margin is a Kind B arm that
    has not been caught yet*, plus a retirement condition. Evidence: §4.
11. ⚠ **Two generators live in gitignored `.temp/rev059/`** and every derived number
    above comes from them. **If these numbers are to be citable, the manager must
    move `share059.py` and `marginal_at_n.py` under `.tasks-php/` and commit them.**
    I am not permitted to add them there and did not.

---

## § CLOSING CHECK

```
$ python3 .tasks-php/checkers.py
  ...
  ARM-COUNT CLAIMS -- `why` prose vs what the checker PRINTS
    ok cbaseline_check.py       claims  10  observed  10
    ok contract_audit.py        claims   8  observed   8
    ok task_cost.py             claims  16  observed  16

  CHECKERS PASS
  [exited with code 0]

$ python3 .tasks-php/cbaseline_check.py
  cbaseline_check -- cross-language magnitudes with NO C baseline named
  scanned 31 file(s); 77 hit(s); ratchet 77
  real 0m0.129s   rc 0
```

**`CHECKERS PASS`**, read at `c868e60`. No `.tasks-php/` tool was edited, so this is
the unchanged baseline. The ratchet is green at 77/77 and now enforces on the bare
run.
