# TASK_PHP_018_REPORT — `ph07` rebuilt: a new R1h, an unrestricted corpus, the spellings control, and the third span

**Role:** research **engineer**, one agent, alone. `PROTOCOL.md` rule 1 — I did
not build this row and I am not its reviewer.

**Verdict in one line:** ⭐ **the rebuild was worth it and it is done** — every
number on `ph07` moved, the gate is green on the new contract, and **upstream's
own regression test decides the question the task was uncertain about**; the
spellings control is built and the **R4 endpoint is degenerate**; the third span
is pinned and **exposed something worse than it fixed**.

---

## Bracket — both, first and last

**Open** (before any edit):

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE
$ python3 harness-php/gate.py --tool measure --check-stale
6 record(s) examined, 0 STALE
```

**Close**: see §7. ⚠ One process note: `harness/measure.py --check-stale` is
executable and `harness-php/gate.py` is **not** (mode 644), so the task file's
spelling of the second bracket fails with `Permission denied`. It needs
`python3` in front. That is a one-character difference between two commands
printed side by side, and it cost a first run.

`git status --porcelain` scope: `harness-php/provenance.py` (§3, explicitly
in scope and costing no PAT re-gate), `patterns-php/ph07-strcut-cursor/*`, and
`results-php/{,gate/,tables/,preflight/}ph07-strcut-cursor*`.
⚠ **Plus `results-php/preflight/_norow.preflight.json`**, which the two
`--check-stale` runs grew: `PROTOCOL_PHP.md` §E's *"not read-only — a run grows
a COMMITTED file"* row, firing exactly as documented, on the command the task
prescribes as its own bracket. **Nothing under
`harness/`, `common/`, `patterns/`, `results/`, `pilot/` or `.web/` was created,
edited or deleted.** No `git add`, no `git commit`. `patterns-php/CATALOGUE.md`,
`.tasks-php/PROTOCOL_PHP.md`, `PLAN_PHP.md`, `.tasks-php/ADJUDICATION_00*.md`,
`.memory-php/` and `RECAP_PHP.md` were **read and not written** (rule 11) — §4
carries the proposed text instead. Scratch: `.temp/php18/` only; `.temp/php17/`
and `.temp/mgr165/` were read and reused, never written.

---

# §1 THE DECISION — and §5.1's stopping point was declined, on evidence

## 1a ⚠⚠⚠ THE ANSWER TO THE QUESTION THAT COULD HAVE INVALIDATED THE PLAN: **YES, ALL OF THEM DID**

**Reported before anything was changed, as asked.** F41 says R2–R5 are ports of
R1h. They were, and they carried hunk (b) **everywhere**:

| where | what it carried |
|---|---|
| `safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs`, `verus.rs` **exec** | `let length = if frm.saturating_add(length) > slen { slen - frm } else { length };` |
| ⚠⚠⚠ **`verus.rs`'s SPEC — `strcut_fold`** | `let length = if f0 + l0 > slen { slen - f0 } else { l0 };` |
| `model.py` — **all three** implementations | `_window`, `strcut_fold` and `_dumb`, each with `if frm + length > slen: length = slen - frm` |
| `model.py::selfcheck` check 2 | asserted `from + length <= slen` on every measured window |
| `inputs/gen.py` | `FRACTIONS` all summing ≤ 1, plus a `min(..., slen - frm)` in `window()` |

⭐⭐ **AND THAT IS THIS ROW'S STRONGEST ARGUMENT FOR A VALUE POSTCONDITION,
ARRIVING FROM A DIRECTION NOBODY DESIGNED.** `verus.rs`'s `ensures` is
`r == strcut_fold(...)`, a functional value spec rather than a memory-safety
one. When R1h stopped computing the same function, **the postcondition had to
change with it** — the spec function is the thing that says *which* function the
rung implements. A memory-safety-only `ensures` would have stayed green through
the entire rebuild and told nobody anything. This is the concrete payoff of the
choice `spec.md`'s `obligations_note` defends on principle.

Removing it did **not** break the proof. It made it **cheaper** — §1e.

## 1b–1e What was done

**1b. `c/kernel_hardened.c` = hunk (a) alone**, at `mbstring.c:1807`, in the
frame the kernel already runs on every call (`TASK_PHP_017`'s R1h TRANSPLANT
RULE: *does the kernel run the repair frame's code today?* — yes, and that frame
is now **pinned**, §3). The two-hunk variant stays measurable in **three**
places under `controls/`: `fix_scope.py`'s `R1h_ab` variant (133 932 calls),
`guard_equiv.c`'s new `length_ab` column (5 122 triples against a build of the
C), and `bug49354.py`. `c2471b495009.patch` sits beside `cb3cca21b345.patch`.

**1c. `inputs/gen.py`: the restriction is gone and its INVERSE is asserted.**

```
span ok: small.bin   windows=32    steps=[1,2,3,4,5,6] k>=len=10  k<len=22
                     start==from=14 start<from=18 from==len=3
                     hunk(a)-fires=0 from+len>len=6   hunk(b)-would-move=4
span ok: large.bin   windows=2050  steps=[1,2,3,4,5,6] k>=len=662 k<len=1388
                     start==from=885 start<from=1165 from==len=205
                     hunk(a)-fires=0 from+len>len=410 hunk(b)-would-move=297
```

- ⭐ **The second assertion is the sharp one.** *"Windows with
  `from + length > slen` are present"* is true but weak: most of that region
  takes the `k >= slen` shortcut under **both** configurations and answers
  identically. So `_check_span` also requires windows on which hunk (b) **would
  have changed the answer** — the arm `bug49354.phpt` exercises. **20.0 %** of
  windows are in the region; **14.5 %** are in the sharp part, against
  `fix_scope.py` Q2's independent **13.5 %** over a uniform sweep. That
  agreement is the cross-check that the fixture is neither over- nor
  under-weighting what it just re-admitted.
- ⚠ **Which `_check_*` was relying on the restriction, measured rather than
  guessed.** `_check_residues()` was **not** and is unchanged — it is the only
  other one. `_check_span`'s `fix_fires` counter conflated the two guards and is
  split. `model.py::selfcheck` check 2 **was** relying on it and is **reversed**:
  it now requires the region to be present.
- ⚠⚠ **AND THE `min(..., slen - frm)` CLAMP IN `window()` NEVER FIRED.**
  Measured before deleting it (`.temp/php18/fractions.log`): over the eight
  shipped `FRACTIONS` entries, clamped and unclamped produce **byte-identical
  corpora**. The restriction was carried entirely by the `FRACTIONS` table. The
  dead clamp was deleted anyway — a clamp that would silently re-impose the old
  domain the moment somebody adds a fraction pair is the failure mode this task
  exists to remove.
- ⚠ **Five must-fire controls, all as declared** (`.temp/php18/gen-negatives.log`):
  the pre-018 table is REFUSED on `from+len>len`; a table whose over-sum windows
  can never move the answer is REFUSED on the sharper assertion; a hand-edited
  byte setting `from = slen + 1` is REFUSED on hunk (a); the shipped table
  PASSES; and `_cut` separates the two configurations on `bug49354.phpt`'s own
  case 3. ⚠ The hunk-(a) branch is unreachable *through `FRACTIONS`* because
  `window()`'s own assert refuses `ff > 1.00` first — defence in depth, and the
  right layering, so the control drives it on bytes.

**1d. `spec.md`.** `idiom.required[4]` now pins the **configuration** (tag
range, function, body sha256, both commits) and — as asked — **states the choice
AND the alternative**: the three measurements that rejected shipping the whole
2005 commit, and the cost of the choice (a tag range is not a commit; it is
still a subset of a labelled security fix, and the entry says so). A new
`idiom.forbidden[3]` pins hunk (b)'s two spellings ABSENT, per-language.

⚠⚠ **TWO SCHEMA FACTS LEARNED THE HARD WAY, AND BOTH ARE WORTH RECORDING:**

1. **`idiom` accepts exactly `required`, `forbidden`, `why`.** A
   `forbidden_note` sibling **hard-fails** the gate: *"idiom has unknown key(s)
   ['forbidden_note']; expected exactly [...] — a mistyped key is silently
   empty."* The note went inside the entry.
2. ⚠⚠⚠ **Every backtick inside a `forbidden` entry is a PINNED SPELLING that
   hard-fails if any rung contains it.** A draft wrote `` `length` `` in that
   entry's *prose*. `length` is in every rung. Caught before the gate by
   extracting the tokens the way `check.py` does
   (`_TICK.findall` per language), not by running it. **A `forbidden` entry's
   English cannot use backticks for emphasis.**

**1e. Re-gate and re-measure.** Full six-command cycle, plus two extra
`report → gate` rounds for the two schema mistakes above.
`contract_sha256` **`be5f5818ffa6…` → `1f1508531bd4…`**, disclosed in
`NOTES.md` §0 and checkable against `results-php/gate/ph07-strcut-cursor.json`.

---

# §1e THE NEW LADDER, IN FULL

`-O3 / isolated`, kernel-exclusive `Ir`, from
`results-php/ph07-strcut-cursor.json`:

| cell | `Ir`/call small | `Ir`/call large | **`Ir`/window byte** | fixed `Ir`/call | vs R4 | *was* |
|---|--:|--:|--:|--:|--:|--:|
| `c-gcc` (R1) | 2 482.4 | 17 023.0 | **4.1297** | 198.7 | +28.72 % | *3.8643* |
| `c-gcc-h` (R1h) | 2 485.2 | 17 026.1 | **4.1298** | 201.4 | +28.72 % | *3.8643* |
| `c-clang` (R1) | 2 078.5 | 13 862.3 | **3.3467** | 227.7 | +4.32 % | *3.1814* |
| `c-clang-h` (R1h) | 2 084.7 | 13 868.4 | **3.3467** | 233.9 | +4.31 % | *3.1813* |
| `safe_naive` (R2) | 2 966.3 | 21 014.3 | **5.1258** | 131.7 | **+59.77 %** | *+57.67 %* |
| `safe_tuned` (R3) | 2 061.3 | 14 711.1 | **3.5926** | 74.6 | **+11.98 %** | *+13.50 %* |
| `unsafe` (R4) | 1 850.5 | 13 146.8 | **3.2083** | 76.3 | 0.00 % | — |
| `verus` (R5) | 1 850.5 | 13 146.8 | **3.2083** | 76.3 | 0.00 % | — |

⭐ **R4 ≡ R5 still byte-identical**; the `identity` pin did not move. Every rate
rose because the new corpus takes the `k >= slen` shortcut on **32 %** of
windows instead of 16 %, so more of each call is start walk and copy.

## Which of F41's three measured claims survive

**(a) *"the over-read does not change the answer"* — ✅ SURVIVES UNCHANGED.**
`fix_scope.py` Q3 re-runs identically: **0 of 15 333** over-reading calls move
under seven fillers, must-fire control **13 293 of 15 333**. This claim is about
R1 alone and no corpus change can touch it. `TASK_PHP_017` §5a's point stands:
the zero is structurally forced, and the mechanism — not the seven fillers — is
the argument.

**(b) *"the 2010 walk rewrite alone still over-reads"* — ✅ SURVIVES UNCHANGED.**
Q1, with the new labels (`R1h` = shipped, `R1h_ab` = withdrawn):

```
variant    reads past val[slen]  answer != R1
R1                        15333             0
R1h                           0         16320     <- hunk (a) alone: ALL of them
R1h_ab                        0         32190
R1_2010                       0          5717
R1_walk                   13293             0     <- the walk rewrite alone
```

**(c) *"the fix costs a CONSTANT, not a rate"* — ✅ SURVIVES, ⚠ AND IT GOT
SMALLER WITHOUT GETTING CLEANER. Saying so plainly because the task predicted
the opposite.**

| | gcc | clang |
|---|--:|--:|
| `Ir`/call delta, `small` (553 B) | **+2.8164** | **+6.1863** |
| `Ir`/call delta, `large` (4 074 B) | **+3.0734** | **+6.1046** |
| fixed-term delta | **+2.7761** | **+6.1991** |
| *pre-018 fixed-term, TWO guards* | *+7.3022* | *+9.2685* |

**It halved, as one guard instead of two predicts.** ⚠⚠ **But it got cleaner on
only ONE of the two compilers, and the task predicted both:**

```
                marginal delta   4-dp equal?   small -> large delta   spread
pre-018  gcc    -3.504e-05       YES           7.2828 -> 7.1594       0.1234
pre-018  clang  -3.518e-05       no            9.2490 -> 9.1252       0.1238
NOW      gcc    +7.298e-05       no            2.8164 -> 3.0734       0.2570  2.1x WORSE
NOW      clang  -2.320e-05       YES           6.1863 -> 6.1046       0.0817  1.5x better
```

⚠⚠⚠ **AND THE CROSS-CHECK `TASK_PHP_017` §5c RELIED ON HAS EVAPORATED.** Before
the rebuild the two compilers' marginal residuals were `-3.504e-05` and
`-3.518e-05` — *identical to three significant figures* — and §5c read that as
the evidence that the residual is a decomposition artefact and not an effect.
**After the rebuild they are `+7.3e-05` and `-2.3e-05`: different magnitudes and
opposite signs.** **That agreement was a coincidence of one corpus.** It does not
damage the conclusion, but it removes the argument that was carrying it, and the
argument has to be replaced rather than restated.

**What replaces it, and it is what `NOTES.md` §8a now says:** the marginal moves
by at most **7.3e-05 on a rate of 3.3–4.1 — within 0.002 % on both compilers** —
while the delta is **2.82–3.07 `Ir`/call (gcc) and 6.10–6.19 (clang) across a
7.4× range of window size**. A statement about a constant, two points per
compiler, no dependence on a rounding boundary. The four-decimal-place wording is
**retired**.

## ⭐ Three things the rebuild bought that nobody asked for

1. **`negatives.py --emit noguard` now isolates ONE guard.** It used to have to
   delete both hunks, because hunk (b)'s `slen - frm` needed `frm <= slen` too —
   so a hunk-(a)-only mutant died on an **arithmetic underflow one line later
   and never reached the walk**. Now it fails at **the start walk's own loop
   invariant `frm <= slen`** (`.temp/php18/noguard-site.log`), which is the
   obligation the control exists to demonstrate. *A control that could only fire
   for a confounded reason now fires for the right one.*
2. **The proof got CHEAPER on both sides.** `#[verifier::rlimit(30)]`'s
   justification changed: the requirement was ~10–12 plain / **15 twin** and is
   now **9 on both** (bisected, `.temp/php18/rlimit-sweep.log`). ⚠ The override
   **stays** — 9 against a default of 10 is a margin of one — but the *reason*
   printed in `spec.md` and `NOTES.md` §10b is now true instead of stale.
   ⚠ And the plain/twin asymmetry **reversed** (twin used to need more; plain
   now does). I have no mechanism for that and report it because a disclosure
   that only survives while its number is convenient is not one.
3. **The §8b arithmetic check tightened by an order of magnitude.** Re-derived
   by replaying the *driver's own window selection* instead of averaging
   `FRACTIONS`: predicted `2×0.129198 + 2×0.063052 = 0.384500`, measured
   `0.384374` — **0.03 %**, against 2 % before.

## ⚠ And the wall clock now contradicts a fact you can count

R4 and R5 are byte-identical and their wall marginals differ by **2.73 %**; on
this corpus the wall clock says **safe Rust is 5–6 % FASTER than unsafe**, while
the instruction count says it executes 12 % more. **A measurement that reverses
a fact you can count is measuring the box.** That is a *stronger* form of the
row's existing refusal to use ns than the one `TASK_PHP_017` m2 correctly
objected to (which compared magnitudes and had a counter-example).

---

# §2 THE SPELLINGS CONTROL — built, both sides, and the rule was NOT "re-ship R3"

`controls/spellings.py` — **the first in `patterns-php/`**, ported after reading
all four PAT examples (`p13`, `p34`, `p42`, `p49`). It does **not** replace
`safe_tuned.rs`.

⚠⚠ **`TASK_PHP_017` B1's `+2.62 %` IS NOT CARRIED OVER.** It was measured
against the corpus §1c deleted. Everything below is re-derived.

⚠⚠⚠ **AND THE FIRST DRAFT MEASURED THE WRONG STATISTIC — reported because it is
exactly the size of error that gets absorbed as noise.** It used `check.py`'s
100-vs-200 marginal and its `v0_shipped` came out **1 %** from the shipped
record (R3 2084.1 where the record says 2061.3). They are different statistics,
not a discrepancy: the driver picks its window from a checksum, so 200
iterations visit a different *sample* of the 32 or 2 050 windows than 25 000 do.
**A control quoted beside the row's headline has to compute the row's headline.**
Switched to `harness/measure.py`'s own — `kernel_exclusive_ir / n_iters` on the
shipped inputs — and stage 3 now reports:

```
safe_tuned  small.bin  record= 2061.3435 here= 2061.3435  delta=0.000%
safe_tuned  large.bin  record=14711.0554 here=14711.0554  delta=0.000%
unsafe      small.bin  record= 1850.4543 here= 1850.4543  delta=0.000%
unsafe      large.bin  record=13146.7822 here=13146.7822  delta=0.000%
```

## 2a The R3 side

```
cell                Ir/call small  Ir/call large  Ir/win-byte  fixed/call  vs R4ship
R3 v0_shipped              2061.3        14711.1       3.5926        74.6   +11.98%
R3 r3_reslice              1892.6        13410.5       3.2712        83.6    +1.96%
R3 r3_reslice_st           1926.7        13666.6       3.3343        82.8    +3.93%
R3 r3_reslice_en           2027.2        14454.9       3.5296        75.4   +10.02%
R3 r3_get_unwrap           2163.6        15490.2       3.7849        70.6   +17.97%
R4 v0_shipped              1850.5        13146.8       3.2083        76.3    +0.00%
```

Loop census (`.temp/php18/loops-variants.log`): R3 shipped **9/1 and 8/1**,
`r3_reslice` **7/0 and 7/0**, R4 **7/0 and 6/0**. ⭐ **`r3_reslice`'s start walk
is instruction-for-instruction R4's, in safe Rust, and the entire residue is one
instruction in the end walk.** Predicted with no fitting from the measured step
rates: `R3 → r3_reslice` **0.32145** vs measured **0.32137** (0.02 %);
`r3_reslice → R4` **0.06305** vs **0.06290** (0.24 %). It captures **83.6 %** of
the gap.

⚠ `r3_get_unwrap` (`s.get(n).unwrap_or(&0)`) is the calibrating **negative** —
safe, total, the spelling most people reach for, and **6 % worse than shipped**.

## 2b ⭐ The R4 side — SEARCHED, AND DEGENERATE. A clean negative.

`SYNTHESIS.md:271-277` — the headline moves toward whichever side you did not
search, and on 19 searched PAT rows **eleven found no cheaper R4**. **`ph07`
makes it twelve.**

```
r4_fused      3.2082 Ir/window byte   -0.004%   fixed/call 88.3   TIE (< 0.05%)
v0_shipped    3.2083                  +0.000%   fixed/call 76.3   SHIPPED
r4_index0     3.2083                  +0.000%   fixed/call 76.3   TIE (< 0.05%)
r4_nozero     INADMISSIBLE -- no verifying twin
```

**What I tried, and how long I looked: four R4 spellings and five R3 spellings,
over about one working session** — a few hours of build/callgrind/Verus, not a
systematic sweep. The R4 side is the one to attack; I do not claim it is
exhausted.

- ⭐ **`r4_index0` is FREE and strictly better on the trusted side.** Spelling
  the first table read `s[0]` instead of `*s.get_unchecked(0)` compiles to **the
  same bytes at the same addresses** (every loop at an identical offset), its
  Verus twin verifies at **21/0**, and it removes one of `get_unchecked`'s four
  call sites. ⚠ **Not shipped** — `.memory/02-bench-rules.md` forbids re-shipping
  for a cheaper in-contract spelling, and this is not even cheaper; it is a
  *smaller trusted surface at the same price*. **That is a finding for a future
  row, and a `p34`-style `r4_readdirect` result re-derived here rather than
  inherited.**
- ⚠ **`r4_fused` is a TIE, not a win.** Merging copy and fold moves the marginal
  by **0.004 %** and makes the fixed term **12 `Ir`/call worse**. Its twin
  verifies but at **20** obligations, not the pinned 21 (`lemma_fold_shift`
  becomes unnecessary). `spellings.py` carries a `TIE_PCT` threshold precisely so
  that a −0.004 % cannot be read as "the R4 endpoint moves" — which is what my
  own first draft's `min()` did.
- ⚠ **`r4_nozero` is the refusal with a reason** (`p42`'s `endptr` shape):
  `Vec::with_capacity` + `set_len` is `set_len` over uninitialised memory, the
  pinned vstd has no spec that makes it sound, and the twin does not verify.
  ⭐ **It would also have bought nothing** — it measures identically to shipped,
  because `vec![0u8; cap]`'s zeroing is a `memset` CALL and therefore outside
  `kernel_exclusive_ir`. That accidentally puts a number on §8e's C-vs-Rust
  confound: **the zeroing is invisible to the column it confounds.**

## 2c ⚠⚠ THE TWO NUMBERS THE CRASH COURSE MAY QUOTE, AND ONLY THESE

```
fixed-R4 bound              R3ship - R4ship          +11.98 %
cheapest-found in-contract  inf(R3 found) - R4ship    +1.96 %   spelling `r3_reslice`
                                                                inputs small.bin + large.bin
```

⚠⚠ **NO PAIR INTERVAL** — `min(R3 found) − min(R4 found)` differences two upper
bounds and bounds nothing; `ph03`'s hashed `why` retracts that construction and
this row does not resurrect it. ⭐ **Because the R4 side is degenerate, the
`fixed-R4 bound` here is a bound over a SEARCHED endpoint** — materially stronger
than the same number was before this task, and the honest counterpart to §2a.

---

# §3 THE PROVENANCE GAP — closed, and it exposed something worse than it fixed

`harness-php/provenance.py` gained **`extra_spans`**, an **additive** optional
key: a list of `{c_file, c_lines, extract_cmd, extract_sha256, why}`, each
validated exactly as the primary span is (in the manifest, in range, canonical
`extract_cmd`, `extract_sha256` over the bytes `sed` prints). **The primary four
fields do not move**, so `ph03` and `ph00-smoke` are byte-identical in output and
owe nothing. The kernel overlap is now computed over the **union**, and the
per-span numbers are printed beside it.

⚠ **Why not `c_lines: [[a,b],[c,d]]`** (the more literal reading of "a LIST of
spans"): it would force `extract_cmd` and `extract_sha256` into lists too, move
every row, and *still* not express `ph07`'s shape — **three spans in three
different files**. §3's escape hatch ("if the schema costs more than one row's
churn, stop and pin the third span in prose") was **not needed**: the change is
~60 lines in `harness-php/`, costs **no** PAT re-gate, and moved **one** row.

```
mbfilter.c, mbfilter_utf8.c, mbstring.c are in the manifest
OK   .../mbfl/mbfilter.c:1179-1259          1489 B  5edc6c04b7ff5f64  tier=narrowed
OK+1 .../filters/mbfilter_utf8.c:39-56       852 B  716ba3fb219d4fb4  -- the step table
OK+2 ext/mbstring/mbstring.c:1774-1812       845 B  4ef738b3546c31c1  -- the caller frame
per-span overlap: span0 75% (39/52), span1 100% (5/5), span2 15% (3/20)
kernel overlap 61% (46/76 ...)
```

⚠⚠⚠ **THE HEADLINE FELL FROM 75 % TO 61 %, AND THE INTERESTING NUMBER IS
`span2` AT 15 %.** `PROTOCOL_PHP.md` §F item 9 asks what I think of it, so:

**The caller frame is `modelled`, inside a row whose tier says `narrowed`.** The
kernel's wrapper *is* `PHP_FUNCTION(mb_strcut)` semantically — `TASK_PHP_017` §3
verified that by function diff — but almost none of it is the same **text**:
where PHP writes `zend_parse_parameters`, `Z_STRVAL_PP(arg1)` and
`RETVAL_STRINGL`, the benchmark writes a little-endian unpack, `str_len` and a
Horner fold. The three lines that match are the two negative clamps and the
call. **So the overlap heuristic measures exactly what its own warning says it
measures, and on this span it is measuring a re-expression rather than a lift.**

⭐ **The finding is that a single `tier` word is the wrong shape for a
multi-span row.** `ph07` cites three spans at three fidelities — 100 % (a real
`verbatim` lift), 75 % (`narrowed`, the declared removals), 15 % (`modelled`).
The schema now lets a row *say* that it lifts three; it does not yet let it say
*at what fidelity each*. I did **not** extend `tier` to per-span — that is a
second schema change on n = 1 and §4 is where I argue against exactly that — but
it is the natural next question and `NOTES.md` §1a states it.

---

# §4 WHAT I PROPOSE AND DID NOT LAND

⚠ Rule 9 and rule 11. Exact text below; **the manager lands it.**

## 4.1 `PROTOCOL_PHP.md` §C — and I attacked it first, as asked

### The attack, before the wording

`UPSTREAM_002` §4 claims the difference from the refused §A2a clause is that
*"§A2a narrowed the EVIDENCE to fit the ARTEFACT, and this widens the ARTEFACT
to fit the EVIDENCE."* **I ran `TASK_PHP_017`'s own three tests against it.**

**(a) *"It makes something a selection criterion with no bound."*
⚠⚠ THIS ONE DOES NOT PASS, AND I DO NOT BELIEVE THE MANAGER'S CLAIM AS STATED.**
A permission to cite *"a tagged upstream configuration"* lets the next engineer
choose **among tags** — and a function's guard set changes over many of them. An
engineer whose R1h trips stage 7h, or whose R1h costs more than they would like,
can now scan tags until one is convenient and cite protocol. That is the same
shape as §A2a's unbounded narrowing, one level up: instead of choosing the
corpus to fit the fix, choose the *fix* to fit the corpus. **The manager's
distinction is TRUE OF THIS ROW and NOT TRUE OF THE RULE UNQUALIFIED**, and the
wording has to carry the qualification or it becomes the thing it denies being.

**(b) *"It states as a property of the FIX what is a property of the GATE."*
✅ PASSES, and this is the strongest part of the manager's case.** Stage 7h is
what surfaced the problem, but it is not what makes the answer right. **If stage
7h learned tomorrow to express *"this R1h legitimately differs on benign
inputs"*, `ph07`'s R1h would still be hunk (a) alone**, because hunk (b) is a
behaviour bug that upstream removed with a regression test. The §A2a clause
would have retired with the gate check; this would not. That is a real,
checkable difference and it is not rhetorical.

**(c) *"It was invented to rescue an avoidable choice."* ✅ PASSES — inverted.**
It **retires** a choice. Item 24 closes by deletion.

**But the criterion `TASK_PHP_017` §3.2 actually landed is the KIND OF CLAIM:**
an *observation* is settled by one command; a *norm* is settled by surviving
adversarial use, which needs n ≥ 2. **A permission about what a row MAY ship as
R1h is a norm, and it is on n = 1.** By the programme's own accepted standard it
should be **held, not landed** — and holding it costs `ph07` nothing, because
the row does not need the protocol to change in order to ship: `spec.md`
`idiom.required[4]` already discloses that R1h is a subset of `fix_commit`, why,
and what it was chosen against.

### ⭐ MY RECOMMENDATION: land 4.1-A, hold 4.1-B until a second row needs it

**4.1-A — an OBSERVATION, and it is what I would land.** Append to §C:

> ⚠⚠ **AND A ROW MAY SHIP A SUBSET OF ITS `fix_commit`, IF IT SAYS SO AND SAYS
> WHY.** `ph07`'s R1h is `cb3cca21b345` **hunk (a) alone** — the configuration
> `php-5.2.12 … php-5.2.17` shipped and kept, `PHP_FUNCTION(mb_strcut)` body
> sha256 `26e2099e33433c74` — because `c2471b495009` (2009-09-23) **removed hunk
> (b) as bug #49354, with a regression test**. Hunk (b) removes **none** of the
> 15 333 out-of-bounds reads and changes the answer on **13.5 %** of benign
> calls. ⭐ **`check.py` stage 7h had refused it in the first hour the row
> existed, and stage 7h was right**: it detected the same defect PHP's
> maintainers detected four years later, from a bug report.
>
> **This is a WORKED EXAMPLE, not yet a general permission** (`.tasks/PROTOCOL.md`
> rule 9 and `TASK_PHP_017` §3.2: a norm needs n ≥ 2). A row that wants to do the
> same owes, in `spec.md` inside the hashed block, all four of:
> **(i)** the configuration pinned as `(tag range, function, body sha256)`, with
> every commit that produces it cited and its patch bytes under `controls/`;
> **(ii)** what each hunk of the original commit buys, measured — reads removed
> and benign answers changed, separately;
> **(iii)** an upstream artefact that decides it — a later removal, a regression
> test, a bug number — and **not** the row's own convenience;
> **(iv)** the alternative it was chosen against, and the cost of the choice.
> ⚠⚠ **(iii) IS THE LOAD-BEARING ONE.** Without it, *"cite a tagged
> configuration"* lets the next engineer scan tags until one suits the corpus —
> which is `§A2a`'s unbounded narrowing wearing a different hat, and it is the
> objection this clause exists to answer.

**4.1-B — the general permission, if the manager takes it anyway.** Replace
§C's first sentence with:

> `c/kernel_hardened.c` is the `fix_commit` patch **backported and sha-pinned**,
> with the commit id in `spec.md` — **or** a **tagged upstream configuration**
> of the repaired function, pinned as `(tag range, function, body sha256)`, when
> upstream itself later changed what that commit shipped. **A configuration is
> admissible only with all four disclosures of the `ph07` worked example above,
> and (iii) is not optional.** ⚠ It is what upstream *kept*, which is a stronger
> citation than what it once merged; it is also **a subset of a labelled
> security fix presented as that fix**, and the row must say so in terms.

## 4.2 `PROTOCOL_PHP.md` §A2a — item 24 closes by DELETION. Confirmed.

**One sentence, as asked:** with hunk (b) gone from R1h there is no corpus
restriction left to legitimise, so **no §A2a clause is needed and item 24 should
be closed by deleting the proposal rather than by landing anything.**

⚠ **One thing in `TASK_PHP_017`'s guard clause is worth keeping, and it is not a
corpus rule.** Its item 2 — *"does a memory-safety-SUFFICIENT SUBSET of the fix
exist that does not change benign output?"* — is the question that would have
found this two tasks earlier. It belongs in `PROTOCOL_PHP.md` §F's checklist as
an **observation** beside item 5, not in §A2a as a permission:

> 5b. ⚠ **Ask whether a memory-safety-SUFFICIENT SUBSET of the `fix_commit`
> exists that changes no benign output, and answer it in `NOTES.md` before any
> rung is measured.** `ph07`'s answer is **yes** (hunk (a) alone, `php-5.2.12`),
> and finding that out two tasks late cost a full rebuild of the row.
> ⚠ **Where the whole fix changes benign output and no such subset exists, that
> is a RESULT to publish beside the ladder with its rate** — it is not a licence
> to restrict the measured corpus.

## 4.3 `.memory-php/02-ladder.md` — proposed corrected text

**(i) Replace the F31 bullet** (*"a green php gate does NOT mean the upstream fix
is complete"*) with:

> - ⚠ **A green php gate does NOT mean the upstream fix is complete, and cannot.**
>   `check_sanitizers_hardened` hard-fails on any R1h diagnostic — correct for a
>   hand-written PAT control, wrong for a shipped fix that is incomplete. That
>   evidence lives in the row's `controls/`. **Standing limitation, not a bug to
>   file.** (F31.)
>   ⚠⚠⚠ **BUT THE SIBLING CLAIM ABOUT STAGE 7h IS RETRACTED, AND THE RETRACTION
>   IS THE MORE USEFUL HALF** (`TASK_PHP_018`). `TASK_PHP_017` §4b filed stage 7h
>   — *R1h must be byte-identical to R1 on every non-adversarial input* — as
>   **the same defect on the same axis**, a known-wrong check to be worked around
>   until it learns better. **It is not.** On `ph07` it refused an R1h that
>   changes benign output on 13.5 % of calls while removing none of the 15 333
>   over-reads, and **upstream removed that same hunk four years later as bug
>   #49354, with a regression test** (`c2471b495009`; `controls/bug49354.py`
>   replays it). **Stage 7h detected a real defect in the first hour the row
>   existed; the workaround was the defect.** ⭐ **The two checks are NOT the
>   same axis: 7h asks whether R1h changes BENIGN OUTPUT, which is a property of
>   the fix; `check_sanitizers_hardened` asks whether R1h still faults, which is
>   a property of the fix's COMPLETENESS. One of them was right.**
>   ⚠ The general lesson, and it is the one to carry: **a gate refusal is a
>   hypothesis about the artefact before it is a complaint about the gate.**

**(ii) Replace the `ph07` half of the ladder table and the F39 addendum** with:

> ## `ph07`, and it is the first php row with a searched spelling span
>
> `Ir`(kernel), `-O3 / isolated`, marginal per window byte — ⚠ within-row ratios
> only, and ⚠⚠ **these are the `TASK_PHP_018` numbers; every figure published
> before it is about a corpus that no longer exists** (`R1h` carried
> `cb3cca21b345` hunk (b), which upstream withdrew, and `inputs/gen.py`
> restricted the domain so it could not fire):
>
> | `safe_naive` | `safe_tuned` | `unsafe` | `verus` | `c-gcc-h` vs `c-gcc` |
> |---:|---:|---:|---:|---:|
> | **+59.77 %** | **+11.98 %** | 0.00 % | **0.00 %** | +2.8…3.1 `Ir`/call, flat |
>
> - ⭐ **`verus` is byte-identical to `unsafe`** at O3 up to relocations — the
>   proof costs nothing at run time. n = 2 on the php side.
> - ⭐⭐ **`ph07` IS THE FIRST php ROW TO DISCHARGE THE `fixed-R4 bound` DEBT**,
>   and it discharges it **on both sides**: `controls/spellings.py`, five R3
>   spellings and four R4 spellings.
>
>   ```
>   fixed-R4 bound              R3ship - R4ship          +11.98 %
>   cheapest-found in-contract  inf(R3 found) - R4ship    +1.96 %  (`r3_reslice`)
>   R4 side, searched                                     DEGENERATE
>   ```
>
>   ⚠⚠ **NO PAIR INTERVAL** — two minima differenced bound nothing.
>   ⭐ **The R4 endpoint is degenerate: no admissible R4 moved by more than
>   0.004 %**, so `ph07`'s bound is over a *searched* endpoint. That makes **12
>   of 20** searched rows across both programmes where the R4 side did not move.
> - ⭐ **The R3-side lever is a RE-SLICE, and it is available because of R1h.**
>   `&s[..=frm]` and `&s[..=k]` are facts the guard has already proved, not new
>   checks; `r3_reslice`'s start walk is instruction-for-instruction R4's and the
>   whole residue is one `mov`. **The retracted claim — *a variable-stride cursor
>   is not an iterator, therefore no safe spelling reaches it* — has a false
>   second half.** Re-slicing is not iteration; it is telling the compiler what
>   the guard established.
> - ⚠ **`ph03` still owes its own spread on both sides.** The debt is now on one
>   row, not two.

**(iii) Add, to the F34/F38 group** (a fifth frame):

> - ⭐⭐ **AND A FIX CAN BE PARTLY WITHDRAWN, WHICH MAKES *"the fix commit"* AN
>   AMBIGUOUS PHRASE.** `ph07`'s `cb3cca21b345` (2005) added two guards; hunk (a)
>   closed the memory-safety defect and hunk (b) introduced **bug #49354**, which
>   `c2471b495009` (2009-09-23) removed with a regression test — **committed
>   three times in the same second, one per live branch**. So the row's R1h is a
>   **tagged configuration** (`php-5.2.12 … php-5.2.17`, body sha256
>   `26e2099e33433c74`) and not a commit. ⚠ `RECAP_PHP.md` F38's *"the column
>   names A fix, not necessarily the one that removes the 5.0.0 defect"* now has
>   a sharper sibling: **the column can name a commit HALF of which upstream
>   later deleted.** Check what the fix looks like at later tags, not only
>   whether it exists.
> - ⭐⭐ **AND THIS IS `ph03`'s FINDING FROM THE OPPOSITE DIRECTION.** There, a
>   stated obligation caught in 2026 what a patch missed for ten years — the fix
>   was **incomplete**. Here the fix was **too big**, and the excess was not
>   merely dead: it was **wrong**, and upstream removed it. **Two rows, two
>   shipped security fixes, neither minimal nor sufficient as shipped.** n = 2,
>   not an anecdote.

---

# §5 THE MANAGER'S THREE UNCERTAINTIES

**5.1 — *"That §1 is worth a rebuild of row 2 at all."* ⭐ IT WAS, AND THE
EVIDENCE THAT DECIDED IT IS NOT IN `UPSTREAM_002`.** I did not take the stopping
point, and the reason is `controls/bug49354.py`: upstream shipped a **regression
test** with the removal, and running its six expectations against all three
configurations settles the question mechanically rather than by argument.

```
call                      --EXPECT--            R1                   R1h_ab                R1h
mb_strcut($crap,2,100)    string(11) "åBäCöDü"  string(11) "åBäCöDü" string(9) "åBäCöD" ✗  string(11) "åBäCöDü"
mb_strcut($crap,13,100)   bool(false)           <<OOB READ>> ✗       bool(false)           bool(false)

R1     : 1 of 6 wrong -- the over-read (CRASH-124)
R1h_ab : 1 of 6 wrong -- bug #49354, a DIFFERENT row of the table
R1h    : AGREES on all 6
```

⭐ **Case 3 and case 6 are two different defects in two different
configurations, and hunk (a) alone fixes one while leaving the other correct.**
The row's shipped R1h **failed upstream's own regression test**. Against that,
"land the guard clause and keep the R1h the row has" was not a live option: it
would have kept a rung that PHP itself calls a bug, and defended it with a
protocol clause.

**5.2 — *"That a subset of a commit may be called R1h."*
⚠ I think the row must ship the subset, AND the protocol must not yet be
generalised to permit it.** Those are separable and §4.1 separates them. The
argument against shipping the whole 2005 commit is not that it is inconvenient:
it is that **the whole commit is a program upstream tested and rejected**, and
that shipping it forces the corpus restriction which is what made the row
un-measurable over its own domain. ⚠ The honest residual is exactly the one the
manager names — *it is still a subset of a labelled security fix, presented as
that fix* — and I have put that sentence **inside the hashed block**
(`idiom.required[4]`) rather than in a footnote, so it cannot be quietly
withdrawn.

**5.3 — *"That `r202895` is `cb3cca21b345`."* ⚠ NOT RESOLVED, AND IT IS NOT IN
THE ROW.** php-src's converted history carries **no `git-svn-id` trailer**
(checked on the commits either side), `svn.php.net` no longer resolves, and a
harvest of self-referencing revision numbers from php-src commit messages across
four windows (2005-12, 2006-06, 2008-01, 2009-09) returned **only the three
copies of `c2471b495009` itself** (`.temp/php18/svnprobe.py`). The sentence is
marked **UNVERIFIED** in `spec.md`'s `fix_commit_note` and in
`controls/fix_scope.py`'s history table, and nothing depends on it. ⭐ **What
replaces it is measured**: the three lines removed in 2009 are byte-identical to
three of the seven added in 2005, and the function carries them **continuously**
at every tag from `php-5.1.2` to `php-5.2.11`.

⭐ **One thing I did resolve that `UPSTREAM_002` did not have:** the removal was
committed **three times in the same second** — `c2471b495009`, `0c974164e248`,
`ce3c028803aa` — one per live branch, all with `bug49354.phpt`. It is not one
branch's local decision.

---

# §6 CLEAN NEGATIVES AND THINGS THAT DID NOT LAND

These cost real time; they should stop the next agent re-running them.

1. **Removing hunk (b) does NOT break the R5 proof.** `21 verified, 0 errors`
   plain and `24, 0` twin — the **same obligation counts** as before, so
   `spec.md`'s `verus.obligations` and `twin_obligations` did not move.
2. **The one place the proof got harder is `k = start.saturating_add(length)`,
   and it cost three `assert`s and NO new trusted item.** With hunk (b) gone,
   `length` is no longer bounded by `slen - frm`, so saturation is reachable in
   Verus's model (it does not fix `usize::BITS`). The repair is that saturation
   is exactly the case the `k >= slen` shortcut already covers:
   `k as int <= ks`, `k < slen ==> k as int == ks`, `k >= slen ==> ks >= slen`.
3. **The loop census did NOT move.** 9/1, 8/1 on R2/R3 and 7/0, 6/0 on R4/R5,
   identical to the pre-rebuild figures. Only the *rates* moved.
4. **`fix_scope.py` Q1/Q2/Q3/Q4 all re-run identically** — 15 333 over-reads,
   15 870/117 612 (13.5 %), 0 of 15 333 moved with a 13 293 control.
5. **`guard_equiv.py`'s three historical mutants reproduce exactly** —
   2 376 / 269 / 509 — and its two must-NOT-fire variants (`c32`, `ord`) still
   do not fire. The new eighth case `hb` (two-hunk vs shipped) fires at
   **1 134 of 5 122**, which is what makes the removal a behaviour change rather
   than a tidy-up.
6. **All four shipped Verus negatives behave** (`noguard`/`nopos`/`notable` FAIL,
   `noconsume` PASS) after the anchor update.
7. **`ph03` and `ph00-smoke` provenance output is byte-identical** after the
   `extra_spans` schema change. The additive design cost zero churn.
8. **`r4_index0`, `r4_fused` and `r3_reslice*` all return the shipped checksum on
   all seven inputs**, adversarial included.
9. ❌ **`r4_nozero` does not verify** — a real refusal, and it would have bought
   nothing anyway (the zeroing is a `memset` outside `kernel_exclusive_ir`).
10. ❌ **No cheaper admissible R4 was found.** The endpoint is degenerate.

## Not done / unsure

1. ⚠ **The R4-side search is four spellings over one session.** I do not claim
   it is exhausted, and the R3 side leaves **one instruction** unclosed.
2. ⚠ **`tier` is still one word for a row that cites three spans at three
   fidelities** (§3). I did not extend it — that is a second schema change on
   n = 1 — but `NOTES.md` §1a states the gap.
3. ⚠ **`nopos` still has no isolating control for the termination premise.** The
   docstring is corrected (`TASK_PHP_017` m1) and the isolating mutant exists in
   `.temp/php17/mut/`; shipping it is a fifth negative and another
   `contract_sha256` move.
4. ⚠ **The plain/twin rlimit asymmetry reversed and I have no mechanism for it.**
5. ⚠ **`.temp/php16/` and `.temp/php17/` logs use the OLD `fix_scope.py` labels**
   — there, `R1h` means both hunks and `R1h_a` means hunk (a). Here `R1h` means
   the shipped configuration. The swap is disclosed in `fix_scope.py`'s
   docstring, but it is a real reading hazard for anyone quoting an old log.
6. ⚠ **I did not re-run `ph03` or `ph00-smoke`'s gates.** The `provenance.py`
   change is additive and their output is unchanged, but their *preflight
   records* will move on their next run.

---

# §7 CLOSING BRACKET, AND THE GATE

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH  results/gate/ph00-smoke.json           29 source(s)
FRESH  results/gate/ph03-uudecode-bound.json  33 source(s)
FRESH  results/gate/ph07-strcut-cursor.json   38 source(s)     <- was 35
FRESH  results/ph00-smoke.json                19 source(s) + 8 input(s)
FRESH  results/ph03-uudecode-bound.json       19 source(s) + 7 input(s)
FRESH  results/ph07-strcut-cursor.json        19 source(s) + 7 input(s)
6 record(s) examined, 0 STALE
```

**The php number stayed 6**, as the task predicted; `ph07`'s gate record went
from 35 pinned sources to **38** (`bug49354.py`, `spellings.py`,
`c2471b495009.patch` — `spellings.json` is a sidecar and is pinned by stage 9b
rather than by the digest).

```
$ python3 harness-php/gate.py ph07-strcut-cursor
check.py: PASS

results-php/gate/ph07-strcut-cursor.json  verdict PASS
                                          contract_sha256 1f1508531bd41975…
spec.md, re-hashed with check.py's own regex:            1f1508531bd41975…
```

## ⚠ The gate cost more rounds than the six-command cycle, and each extra one was a real defect

Recorded because `RECAP_PHP.md` open item 11 plans against six:

| round | what it caught |
|---|---|
| 4 | `idiom` carried an unknown key `forbidden_note` — **hard fail** |
| 6 | table render lag on the new `contract_sha256` (expected) |
| 8 | ⭐ **`controls/spellings.json` pinned 5 of 5 sources that are ABSENT** — I wrote ROW-relative keys where stage 9b re-hashes against the REPO root, so the pin named the right files and checked nothing |
| 10 | one line of table-render lag from round 8's warning clearing |
| 11 | ⚠ a `NOTES.md` correction after the green gate — `patterns/*/*.md` is in the gate digest, so **prose edits after a green gate owe another gate run**; caught by the bracket, not by me |

⚠ **Round 11 is a discipline note for anyone finishing a php row**: the row's
`.md` files are hashed into `source_sha256`, and `spec.md`, the four `.rs`
rungs and `inputs/gen.py` are additionally pinned by `controls/spellings.json`'s
own `derived_from_sha256`. **Once `spellings.py` has run, editing any of those
six stales the sidecar** — so the last things to touch are `NOTES.md` and
`README.md`, and even those cost a gate.

⭐ **Round 8 is the one worth carrying**: `derived_from_sha256` keys must be
**repo-relative**, and on a php row that means `patterns/<row>/…` — which
resolves in both trees, because the shim root's `patterns` is a symlink to
`patterns-php`. **A sidecar whose pin cannot be resolved is reported as
`UNDATED`, not as `STALE`**, so it fails loudly rather than passing quietly; the
mechanism worked and I am recording it so the next `spellings.py` author does
not spend the round.

## Scratch

`.temp/php18/` — generators, probes and logs kept; `.bin`, `.rs` mutants and
callgrind dumps deleted. **`.temp/php18/REBUILD.sh` regenerates every one**, and
it drives the row's own `controls/spellings.py` and `controls/negatives.py`
rather than re-deriving them. `.temp/php17/` and `.temp/mgr165/` were reused
(`spell/loops.py`, `r1h/fn.py`, `mgr165/c2471b495009.patch`) and not written.

---

**Running count: launched from 74.** This task rebuilt row 2 on the evidence
`UPSTREAM_002` assembled, and the piece that decided it — upstream's own
`bug49354.phpt`, replayed against all three configurations — was not in that
document. It also **declined to land the protocol rule the task offered**
(§4.1): the manager's own accepted criterion says a norm needs n = 2, the row
does not need the rule to ship, and one of `TASK_PHP_017`'s three tests against
the §A2a clause **does not pass** for it unqualified. **§4.1-A is what I would
land, and it is an observation.**
