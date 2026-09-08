# TASK_PHP_015_REPORT — the template fixes landed; `ph07` NOT built

**Role:** research engineer, one agent alone.
**Scope taken:** `§1` and `§2` in full, plus the `ph07` reconnaissance `§5`
asked for. **`§3` (build `ph07`) was NOT done — the task's own `§5.3` escape
was taken, and `§5.2`'s premise turns out to need a decision before `ph07` can
be built at all.** Reasons in §7.

**Status of `ph03`:** rebuilt, **re-measured**, re-gated.
`contract_sha256` moved `0302248bc9868121…` → **`2fcd6802b9042dd2…`**, disclosed
and itemised in `NOTES.md` §0.

⚠ **Reconciliation of the running count is the manager's job.** This task was
launched from **74** and I do not carry it forward.

Scratch: `.temp/php15/`. `.temp/php12–14/` were reused, not rewritten
(`04-uufold-divergence.py`, `05-real-divergence.py`, `06-hunk.c`,
`07-zval-slack.c`, `14-mechanism.sh`); nothing under them was deleted.
**`.web/` was never touched, `git add -A` was never run, and no file under
`harness/`, `common/`, `patterns/`, `results/` or `pilot/` was created, edited
or deleted.**

---

## §0 The bracket

**Open** (first two commands of the session, `.temp/php15/00-bracket-open-*.log`):

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH       results/gate/ph00-smoke.json               29 source(s)
FRESH       results/gate/ph03-uudecode-bound.json      33 source(s)
FRESH       results/ph00-smoke.json                    19 source(s) + 8 input(s)
FRESH       results/ph03-uudecode-bound.json           19 source(s) + 6 input(s)
4 record(s) examined, 0 STALE
```

`git status --porcelain` was **empty** at the open.

**Close** — §6.

---

## §1 M1 — the model did not mirror the proof, and the fixture hid it

All three parts landed. **The third is the one that generalises and it is now
`PROTOCOL_PHP.md` §A2a.**

### 1.1 Which side was wrong: `model.py`. Measured, not argued.

`verus.rs:215-223` is `fold_bytes(w.0, w.1, 0)` — Horner over the **first
`total_len`** emitted bytes. `model.py`'s `_fold_line` threaded an accumulator
and folded **every** emitted byte. Same sequence only when `total_len == p`.

Reproduced against a faithful independent transcription of `verus.rs`'s three
spec functions over `ln = 1..63` (`.temp/php15/01-prefix-divergence.log`):

```
ln  fl  nsteps emitted total_len   model.uu_fold        verus uu_fold      agree
  1   1     1        3        1              154280600            152010033  **DIFFER**
  2   2     1        3        2              154280601            151950586  **DIFFER**
  3   3     1        3        3              154280606            154280606  OK
...
42 of 63 single-line windows DISAGREE
```

After the repair (`.temp/php15/04-postfix-divergence.log`):

```
0 of 63 single-line windows DISAGREE
```

**Decisive, against the shipped binaries** rather than against another Python
(`.temp/php15/05-real-divergence-postfix.log`, the reviewer's probe re-run
unmodified on a window declaring `ln = 1`):

```
model _window result (folds out[:total_len]) : 152010033
model uu_fold  (the ENSURES helper)          : 152010033     <- was 154280600
model.selfcheck: []                                          <- was a problem
c-gcc-h-O3-isolated / safe_naive / safe_tuned / unsafe / verus : all 4679476855872
```

**`model.py` was wrong and `verus.rs` was right**, which is the direction the
task predicted: `verus.rs` is what R5 proves and what PHP does
(`:202 RETURN_STRINGL(dst, dst_len, 0)`).

### 1.2 `spec.md:215` and `model.py:38-40` corrected — and the hash moved

`spec.md`'s `note` is **inside the hashed contract**, so this is a
`contract_sha256` move. Disclosed with its three siblings in `NOTES.md` §0:

```
875387e901b85b5e…   AS FIRST WRITTEN            (TASK_PHP_013)
bb2eb51917d2aabc…   after gate run 1            (TASK_PHP_013)
0302248bc9868121…   as shipped at TASK_PHP_013
2fcd6802b9042dd2…   AS SHIPPED (TASK_PHP_015)
```

Four edits inside the fence, itemised in `NOTES.md` §0: the `note` (M1);
`deletions` → `divergences` (the tier clause); `collapse.note` /
`miri.blocked_reason` / `uses_allocator_why` (the fixture moved the window sizes
and the `cap` bound); and `idiom.why` (the dead hunk 1, plus m6's marker).
⚠ **The `0302248b…` line is verifiable against `git show HEAD:` on the previous
commit**, which is the check `§0`'s original text could not offer for a
brand-new row.

### 1.3 The fixture, and the rule

⚠ The task's phrasing was **"the generator must span the parameter that selects
the code path the defect lives on"**. `§5.1` asked whether that generalises.
**It does not quite, and the version that covers both rows is in
`PROTOCOL_PHP.md` §A2a** — see §5.1 below. What was built:

**(a) `inputs/gen.py` emits a short final line**, which is also what
`php_uuencode` really emits (`uuencode.c:79-124`, padding case included), so the
monoculture was **unfaithful as well as blind**. Strides moved
`498 → 556` and `4032 → 4090`; `_check_residues` still passes (they differ mod
4, 8 and 16).

**(b) `inputs/gen.py::_check_span` ASSERTS the span**, in the shape
`_check_residues` already had — it re-decodes what it just generated with its
own transcription of the walk and refuses to write a corpus that misses the
`floor()` arm, the strict case `declared < emitted`, or the equality case
`declared == emitted`:

```
span ok: small.bin   windows=32    floor()-arm lines=32    declared<emitted=22    declared==emitted=10
span ok: large.bin   windows=2050  floor()-arm lines=2050  declared<emitted=1367  declared==emitted=683
```

**(c) The must-fire the task asked for, and it is the MEASURED inputs
themselves** (`.temp/php15/08-fixture-mustfire.log`). The pre-fix `uu_fold` was
re-installed and **only** `selfcheck`'s corpus half was run, against a
reconstruction of `TASK_PHP_013`'s corpus shape and against the new one:

```
                          OLD corpus (45-only)   NEW small.bin   NEW large.bin
PRE-FIX uu_fold                 silent               FIRES           FIRES
SHIPPED uu_fold                 silent               silent          silent
```

**(d) `model.py::selfcheck` now builds its own domain** — 896 windows in three
families spanning `ln = 0..63`. With must-fire **and** must-NOT-fire controls
(`.temp/php15/03-sweep-mustfire.log`):

```
SHIPPED    (control)       MUST NOT fire  -> silent     0/896 windows disagree   ok
all_bytes  (the M1 bug)    MUST fire      -> FIRED    294/896 windows disagree   ok
nofold                     MUST fire      -> FIRED    440/896 windows disagree   ok
resume_ee                  MUST fire      -> FIRED     65/896 windows disagree   ok
srclen_e                   MUST NOT fire  -> silent     0/896 windows disagree   ok
```

⚠ `resume_ee` is `TASK_PHP_013` §6's **other** modelling error — the one found
"by writing the Verus termination argument, not by any test". **The sweep kills
it too**, so both of this row's mis-readings of PHP are now mechanically caught.

**(e) A fifth adversarial input, `adversarial-floor.bin`.** ⚠ **The task's
finding is sharper than it was written**: it is not only that the *benign*
corpus never took the `floor()` arm — **no input did**. All four adversarial
blobs declared 45 too. The new one declares **40**: `fl = floor(40·1.33) = 53`
against a true end 44 characters away, so hunk 1 does not fire and it is the
only input that isolates hunk 2 — the one guard of the 2004 fix that decides
anything. ASan, `env -u LD_PRELOAD` (`.temp/php15/22-asan-lines.log`):

```
adversarial-floor (R1)   heap-buffer-overflow READ of size 1
                         #0 in php_uudecode c/kernel.c:143        <- uuencode.c:144
                         0 bytes after 45-byte region
adversarial-floor (R1h)  clean, 10286939257659585152
```

⚠ It is also the row's **first input on which R1 exits 0 with a wrong answer**
(`15053435816339650688` against the model's `10286939257659585152`) — the other
three corrupt heap metadata badly enough that glibc aborts. Recorded in
`NOTES.md` §6 with the reason, because *"the rung returned"* is not safety.

---

## §2 The rest of `TASK_PHP_014`

| finding | landed | where | cost |
|---|---|---|---|
| **M1** | ✅ | `model.py`, `spec.md` (hashed), `inputs/gen.py` | contract move + re-measure |
| **M2** | ⛔ **deliberately NOT landed** | `PROTOCOL_PHP.md` §E untouched | — |
| **M3** | ✅ | `NOTES.md` §11 `identity` row | gate |
| **M4** | ✅ | `NOTES.md` §8b, rewritten | gate |
| **M5** | ✅ | `NOTES.md` §5 + new §5e, `controls/negatives.py`, `c/kernel_hardened.c`, `idiom.why` | gate + re-measure |
| **M6** | ✅ | `NOTES.md` §5a | gate |
| tier clause | ✅ | `PROTOCOL_PHP.md` §A1 | — |
| ledger rename | ✅ | `provenance.divergences` + `kind`, and 4 docs | contract move |
| **m1** | ✅ | `c/kernel_hardened.c` hunk spans | re-measure |
| **m2** | ✅ | `verus.rs` "Four" → **FIVE** | re-measure |
| **m3** | ⚠ **DEFERRED, with the design written down** | `NOTES.md` §12 | — |
| **m4** | ✅ | `NOTES.md` §11 `verus.obligations` row | gate |
| **m5** | ✅ **and I confirm the reviewer** | §6 below | — |
| **m6** | ✅ (partly) | `idiom.why`; residue named as owed in `NOTES.md` §12 | contract move |
| **m7** | ✅ | `NOTES.md` §5b | gate |

**M2 — changed nothing.** `harness/check.py:1910` is `NAMED_SPELLING_LEN =
11003`, `PROTOCOL_PHP.md:576` pairs 11 003 with sha256 `59748cce2db5…`, and §E
is correct. Not edited, not touched, not "clarified".

### 2.1 M4 — the complete account, done with per-instruction counts

The task said only 5 of a 9-instruction saving were named and the cost side
never mentioned. **Correct.** Rather than hand-tracing basic blocks — which is
what produced the partial account — I read callgrind's **per-instruction** Ir
for `kernel` out of both C rungs (`--dump-instr=yes`,
`.temp/php15/26-attribute.py`, `27-band.py`).

⚠ **Grouping by instruction TEXT is useless here** and that is worth recording:
R1 and R1h allocate registers differently, so a text diff shows ~180
full-magnitude differences that cancel. **The stable classifier is execution
FREQUENCY**, because on `small.bin` each call runs 9 line iterations and 134
group iterations:

```
band                               R1 Ir/line  R1h Ir/line     delta
inner loop (~14.9/line)               773.526      773.526    +0.000
per line  (~1/line)                    44.667       41.667    -3.000
per call  (~0.111/line)                15.556       15.111    -0.444
TOTAL                                 833.748      830.304    -3.444
```

**The inner loop cancels to +0.000** (27 instructions in both,
`.temp/php15/25-loopcount.log`) and the per-line band is **exactly −3.000**.
`−3.444 × 9 = −31.0 Ir/call`, which is the record's own `small` delta.

Full alignment in `.temp/php15/28-alignment.md`. In short:

- **R1h ADDS 6** — three two-instruction tests: hunk 1 (`cmp %edi,%r12d ; jl`),
  hunk 2 (`cmp %rsi,%r9 ; jb`), and the inner loop's entry test
  (`cmp %rsi,%r8 ; jae`) which R1 emits **only on the non-45 path**.
- **R1h DROPS 9** — the five `NOTES.md` named (`setae`, two `test %dl,%dl`, two
  `cmove`), **plus the predicate computation itself** (`lea 0x2(%rbx),%rax ;
  cmp %rax,%rsi`) **and a spill/reload pair** (`mov %r9,(%rsp)` /
  `mov (%rsp),%r9`).
- **Two address computations swap shape and cancel** (+1 / −1).

⚠ **My decomposition of the other four differs slightly from the reviewer's**,
and mine is measured: the reviewer put them as *"a spill/reload pair plus two
address computations gcc folds into `lea`s"*. The spill/reload pair is right;
the other two are the **predicate computation**, and the `lea` folding is a
separate ±1 that cancels. Same total, sharper account.

### 2.2 M5 — reproduced both ways, and it now has a control

`.temp/php15/20-hunk-rerun.log` (the reviewer's `06-hunk.c`, re-run unmodified):

```
   hunk 1 (`len > src_len`) fired : 1953
   hunk 2 (`ee > e`)        fired : 1511
   of hunk-1 firings, hunk 2 would ALSO have refused : 1953
   of hunk-1 firings, hunk 2 would NOT have refused  : 0  <- HUNK 1 IS REDUNDANT
```

**`controls/negatives.py` gained the two must-PASS mutants the reviewer asked
for**, and all three now run against their declared expectations in one pass
(`.temp/php15/19-run-negatives.sh`, `19-negatives.log`):

```
no2014         expect REFUSE got REFUSE  verification results:: 24 verified, 1 errors ok
no2004a        expect VERIFY got VERIFY  verification results:: 25 verified, 0 errors ok
no2004a_both   expect VERIFY got VERIFY  verification results:: 25 verified, 0 errors ok
verus.rs sha256 BEFORE/AFTER identical; no mutant left in the tree
```

⚠ **A must-PASS control is a weaker instrument than a must-FAIL one** and
`controls/negatives.py`'s docstring now says so, with the two guards that make
it usable: the anchor-uniqueness check refuses to emit a no-op (and it now
validates **every** anchor before applying **any**, because one edit can destroy
the next one's anchor), and `no2014` shares the emit path and is must-FAIL, so a
`negatives.py` that had stopped mutating anything would be caught there.

### 2.3 M6 — the ASan limb, softened exactly as far as the measurement goes

`.temp/php15/21-zval-slack.log` (the reviewer's probe, re-run per arm):

```
----- control   CONTROL reading b[8] of an 8-byte malloc   AddressSanitizer: heap-buffer-overflow
----- exact     allocation 2 bytes, slack 0                AddressSanitizer: heap-buffer-overflow
----- zvalraw   allocation 3 bytes, slack 1                AddressSanitizer: heap-buffer-overflow
----- zvalmm    allocation 8 bytes, slack 6                NO DETECTOR FIRED
```

`NOTES.md` §5a now says *"a detector fires under this allocator"*, not *"PHP
faults"*, **and states why limbs 1 and 3 are untouched** (the interpreter uses
offsets and no allocator; `i < v@.len()` is a property of the source slice).
⚠ **The finding is stated as STRONGER for it** — *this residual is not
ASan-observable on a stock PHP build at all, which is part of why it survived
ten years* — which is what the task asked for and not an over-correction.

### 2.4 The tier clause, and the ledger

**`PROTOCOL_PHP.md` §A1** now says `verbatim` admits substitutions, with the
three-part test §A2 already implied: itemised individually with a line citation,
a `why` ending in "no semantics", and **DEMONSTRATED behaviour-preserving over
the reachable domain by a differential with a must-fire control**. ⚠ The third
part is what keeps it from being a hole, and §B's
`ZEND_SIGNED_MULTIPLY_LONG` — **84 523 disagreements** — is named there as the
case where "modelled by an equivalent builtin" was 84 523 away from faithful.

**`provenance.deletions` → `provenance.divergences`**, with a `kind` per entry
(`deletion` / `substitution` / `projection`). ph03's four entries are 1 / 2 / 1.
Renamed in `spec.md` (hashed), `PROTOCOL_PHP.md` §A2, `PLAN_PHP.md` ×2,
`patterns-php/SOURCES.md` ×2 and `harness-php/provenance.py`'s docstring.
⚠ **`ph00-smoke` has no such key** (`php_provenance: false`), so nothing else
moved, and `provenance.py` never read the key — it is still `✗ NOT CHECKED`, and
`NOTES.md` and §A2 both say `kind` is **declared, never detected**.

### 2.5 m3 — the one finding I did NOT land, and why

`provenance.c_lines` pins one span; this row lifts two (`PHP_UU_DEC` at
`uuencode.c:66`, in both C rungs, covered by no `extract_sha256`). **The
reviewer's fix is right** — a list of `[a, b]` spans, hashing the concatenation.
I did not take it, and the reason is written into `NOTES.md` §12 with the design
attached: it changes the **enforced** half of the only provenance check there is
(`PROTOCOL_PHP.md` §D: *"`c_file` in the manifest, the span in range,
`extract_sha256` — those are not heuristics"*), on the row whose provenance
claim is load-bearing, inside a task already carrying a fixture change and a
re-measure. **A schema decision for 90 rows deserves its own task and its own
reviewer.** `PROTOCOL.md`: *"Do not improve scope beyond the task. If you see
adjacent work, report it."*

---

## §3 The measurement — and an accidental replication worth more than a planned one

Full table in `NOTES.md` §8; `.temp/php15/23-ir-table.log` is the derivation.

⚠⚠⚠ **EVERY MARGINAL FIGURE CAME BACK IDENTICAL TO TWO DECIMAL PLACES ACROSS A
COMPLETELY DIFFERENT FIXTURE.** Both strides moved, every benign byte changed, a
seventh input was added and all 32 cells were rebuilt:

| cell | `Ir`/group, `TASK_PHP_013` | `Ir`/group, now |
|---|--:|--:|
| `c-gcc` (R1) | 53.27 | **53.27** |
| `c-gcc-h` (R1h) | 53.07 | **53.07** |
| `c-clang` (R1) | 45.39 | **45.39** |
| `c-clang-h` (R1h) | 45.59 | **45.59** |
| `safe_naive` (R2) | 69.32 | **69.32** |
| `safe_tuned` (R3) | 56.52 | **56.52** |
| `unsafe` (R4) | 50.39 | **50.39** |
| `verus` (R5) | 50.39 | **50.39** |

and §8b's ∓171 → ∓3.00 `Ir`/line came back on the nose:

```
gcc    (52712 - 7339) - (52914 - 7370) = -171  over 57 lines  =  -3.0 Ir/line
clang  (45250 - 6273) - (45051 - 6245) = +171  over 57 lines  =  +3.0 Ir/line
```

⚠ **Nobody planned this as a replication, and it is worth more than one that
was**: a marginal is a slope, and a slope that survives a change of *both*
endpoints is a slope and not a fit. The divisor is still 855 because both
windows gained exactly one 14-group short line, so the difference is still
exactly 57 full lines — that was designed (`TAILS` all encode to 14 groups)
precisely so §8b's arithmetic stayed a clean subtraction.

⚠ **The FIXED column is the half that moved** (Rust ≈ 85 → ≈ 75/66, C ≈ 234 →
≈ 232), for the reason `TASK_PHP_013` §12.8 already flagged: it is a two-point
extrapolation `small − 134 × marginal`, and the short line's groups cost
slightly less than a full line's. The ordering is robust; the values are not,
and never were.

**Identity re-confirmed from the new record**: O3 both cells `md5_fn
338505795ee18db952aafcdaec522df4`, 200 instructions, 708 bytes; O0 **335 vs 352
instructions, 1906 vs 2042 bytes**, `md5_fn_norel` differs. **`differ` at O0 is
right and `norel` was not** — which is M3.

---

## §4 What was run

| | |
|---|---|
| `gate.py --tool build ph03 --all` | `all builds ok`, 32 builds |
| `gate.py --tool measure ph03` | `wrote results/ph03-uudecode-bound.json` |
| `gate.py ph03` (run 1) | **FAIL, 2 failures — both `[tables]`**, the expected staleness |
| `gate.py --tool report ph03` | `wrote results/tables/ph03-uudecode-bound.md` |
| `gate.py ph03` (run 2) | see §6 |
| `verus_run.py verus.rs` | `25 verified, 0 errors`, twice (before and after the source edits) |
| `provenance.py ph03` | `1 row(s) checked, 0 FAILED`, overlap **95 % (18/19)**, 1 unevaluable conditional |
| `model.py inputs/*.bin` | 7 inputs, `selfcheck=[]` on every one |
| cross-rung, `-O3 isolated` | 6 rungs + model agree on all 7 inputs (`11-crossrung.log`) |
| ASan, `env -u LD_PRELOAD` | R1 fires on 4 adversarial inputs, R1h clean on all 7, both clean on `small`/`large` |
| `controls/negatives.py` × 3 | all three match their declared expectations |
| `.temp/php13/14-mechanism.sh` | re-run, **byte-identical** to the recorded log |

⚠ **Two measure runs were started and the first was killed**, and that is my
error rather than a harness one: I edited `c/kernel.c` (m1's sibling, a comment
fix) **after** starting a measure, which would have pinned a source hash the
binaries were not built from. I stopped it by exact PID
(`/proc/1780346/cmdline` confirmed as `measure.py ph03-uudecode-bound`), landed
every measurement-hashed edit, and re-ran `build --all` + `measure` cleanly.
**The lesson is `PROTOCOL.md` rule 6's "batch every rung-source doc fix into ONE
pass" read forwards: finish the batch BEFORE the measure, not during it.**

---

## §5 The three calls the manager was least sure of

### 5.1 ⚠⚠ The fixture rule does NOT generalise as written, and here is the version that does

*"The generator must span the parameter that selects the code path the defect
lives on"* is **two words wrong**, and both matter:

- ⚠ **"span" is not achievable inside a fixed stride.** `work_per_call` is the
  window and must be constant per input, so a corpus **cannot** span
  `ln = 1..63`. ph03's fixture reaches three tail lengths and no more. Written
  as "span", the rule is one no row can satisfy — which is the shape
  `RECAP_PHP.md` open item 19 already records twice for the `why` size limit.
- ⚠⚠ **and it names the fixture as the only repair when the cheaper and
  stronger one is in the MODEL.** The synthetic sweep is ~30 lines, costs
  milliseconds, needs no `.bin`, no measurement and no re-gate, and it covers
  the whole domain rather than three points of it.

✅ **What is now in `PROTOCOL_PHP.md` §A2a, as two rules because they fail
differently:**

> **1.** The fixture must **REACH every arm** of the branch the defect lives on,
> and `inputs/gen.py` must **ASSERT that it does** — in the shape
> `_check_residues` already had. *An intention in a comment is what ph03 had,
> and it was wrong for a task.*
>
> **2.** `model.py::selfcheck` must drive its two implementations over a domain
> **it constructs**, not only over the calls the corpus makes. *A second
> implementation is only as strong as the domain it is exercised over, and
> `inputs/` is not a domain — it is seven files.*

**Neither subsumes the other.** (1) buys *reachability* and is bounded by the
stride; (2) buys coverage free but checks the **model** and cannot see a
*measurement* taken down a path nothing executes.

✅ **And the manager's real question — does it apply to `ph07`, where the cursor
is driven by a static `mblen_table` rather than a length byte? YES, and I
checked it at source before writing it down** (`PROTOCOL.md` rule 14). From the
pinned tarball, `ext/mbstring/libmbfl/mbfl/mbfilter.c:1202-1210`:

```c
1202  for (;;) {
1203      m = mbtab[*p];
1204      n += m;
1205      p += m;
1206      if (n > from) { break; }
1209      start = n;
1210  }
```

`m` is 1, 2 or 3, and **the arms are the lead-byte classes**. An all-ASCII
benign corpus takes `m == 1` on every byte, and with `m == 1` the cursor `p`
tracks `n` exactly, so it can never overshoot the buffer end between two
iterations. **That is `ph03`'s defect with a different name**, and it is exactly
what rule 1 forbids. The rule carries unchanged; only the word *parameter* had
to go.

### 5.2 ⚠⚠⚠ `ph07` may be the right row, but its RISK IS NOT THE `narrowed` MACHINERY — IT IS THAT NO `fix_commit` HAS BEEN IDENTIFIED

The task expected the hard part to be the tiers. **From the reconnaissance, the
`narrowed` extraction looks cheap and something else looks expensive.**

**The extraction is small.** `mbfl_strcut` is `mbfilter.c:1155-1300`; the row
needs `:1177-1259` — the `mblen_table != NULL` arm. What comes off is
`mbfl_no2encoding()` (an encoding lookup) and the `else` arm at `:1260+`, which
is the libmbfl filter-chain object model the corpus's kill-sentence was about.
`mbfl_string` really is `{val, len, no_encoding, no_language}` and `mbtab`
really is a 256-entry static array. ✅ **`F27`'s recovery is confirmed at
source.** ⚠ Note that dropping the `else` arm is a **domain restriction**, not a
deletion — it is only sound because the kernel is always handed an
`mblen_table`. `PROTOCOL_PHP.md` §A2 says a deletion that changes behaviour is a
`modelled` tier, so that argument has to be written, not assumed. It is exactly
the test of the tiers the row was chosen for, and it looks passable.

**The `fix_commit` is the problem.** `PROTOCOL_PHP.md` §F item 5 requires
`kernel_hardened.c` to be the real `fix_commit`, sha-pinned, and §C leans on it
hard. Measured (`.temp/php15/35-mbtab-lifetime.log`, `34-f8dd1050.patch`, and
raw tag snapshots):

| | |
|---|---|
| php-5.0.0 `mbfl_strcut` | `for(;;)` with no `string->len` test — the defect |
| php-5.1.0 / 5.2.0 / **5.3.0** | ⚠ **byte-for-byte the same `for(;;)`** (5.3.0 `mbfilter.c:1379-1382`) |
| php-5.3.0 `mbfl_substr` | **has the guard**: `while (k <= from) { start = n; if (n >= len) break; … }` at `:1213-1223` |
| php-5.4.0 `mbfl_strcut` | **rewritten** as `for (m=0, p=string->val, q=p+from; p<q; p += (m = mbtab[*p]));` — ⚠ **still no `string->len` in the start search** |
| `f8dd10508bd6` / `64f42c73efc5` (bug #71906, 2016-03-28) | the **only** php-src commit whose subject names an `mbfl_strcut` memory-safety bug — and its hunks fix a **different** defect, `from + length` overflow → `length >= string->len - from`, in the rewritten function |

⚠⚠ **So: the sibling function next door got the guard and `mbfl_strcut` never
did, across at least four major releases.** That is potentially a *stronger*
finding than ph03's — *"the fix exists, in the same file, in the function
beside it"* — but **it is not a `fix_commit`**, and `ph07` cannot be built on
`ph03`'s shape until the manager decides what R1h is when upstream never shipped
one.

⚠ **Bound on this claim, stated because it decides a task:** I searched the
GitHub commit-search API on two queries and read five tag snapshots. **I did not
bisect `php-src` history**, so *"no `fix_commit` exists"* is **not** proved —
what is proved is that the 5.0.0 loop survives unchanged to 5.3.0, that 5.4.0's
replacement still does not consult `string->len` in the start search, and that
the one commit the search surfaces fixes something else. **That is enough to say
the premise needs settling before the row is written, and not enough to say
which way.**

**Would a second `verbatim` row have been safer?** On this evidence, the
`narrowed` machinery is *not* what would have hurt — so the ordering was
defensible. But the row that would have been safest is one with a **known
`fix_commit`**, and that is a property nobody was tracking when the order was
chosen. ⚠ **Suggest adding "does a `fix_commit` for THIS mechanism exist?" to
the pre-build checklist**, beside `PROTOCOL_PHP.md` §A3's reachability: it is one
`curl` and it changes which row goes next.

### 5.3 ⚠ Batching a template fix with a new row WAS too big, and I stopped after §2

The task's own escape, taken. §1 and §2 alone came to: a `contract_sha256` move,
a full input regeneration, **two** rebuild+measure cycles (one my error), a
`gate → report → gate` chain, four measurement-hashed source edits, six
`.temp/php15` harnesses with must-fire and must-NOT-fire controls, and ~450
lines of `NOTES.md`. **`ph07` is a whole task** — `TASK_PHP_013` was exactly that
— and §5.2 now shows it needs a decision taken *before* the engineer starts.

⚠ **What I did instead of pushing through** was the `ph07` reconnaissance above,
because §5.1 could not be answered honestly without it and §5.2's premise turned
out to be false in a way that changes the next task file. **That is `PROTOCOL.md`
rule 14 — run the premise before you write it into a task file — done one step
early.**

---

## §6 The bracket, closed, and the gate

**Close** (last two commands, `.temp/php15/41-bracket-close-*.log`):

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH       results/gate/ph00-smoke.json               29 source(s)
FRESH       results/gate/ph03-uudecode-bound.json      33 source(s)
FRESH       results/ph00-smoke.json                    19 source(s) + 8 input(s)
FRESH       results/ph03-uudecode-bound.json           19 source(s) + 7 input(s)
4 record(s) examined, 0 STALE
```

⚠ **`+ 7 input(s)`, up from 6** — `adversarial-floor.bin`.

**The gate**, `.temp/php15/32-gate2.log`:

```
check.py: PASS
verdict PASS | failures 0 | contract 2fcd6802b9042dd2982a37636fda972cb649711ddb20bad61b2ae2893099bbc7
inputs_checked ['adversarial-floor.bin', 'adversarial-nowin.bin', 'adversarial-read.bin',
                'adversarial-shortsrc.bin', 'adversarial-write.bin', 'large.bin', 'small.bin']
loud entries: 2
```

**The chain that produced the record was three commands, not thirteen** —
`gate → report → gate`, with gate 1 failing on `[tables]` ×2 exactly as
`PROTOCOL_PHP.md` §E predicts and nothing else. `TASK_PHP_013` paid ten extra
commands to sequencing; ⚠ **the cost of getting it right is landing every edit
before the FIRST gate**, which is the same discipline that failed me once on the
measure (§4).

⚠ **Full disclosure, because a false one is worse than the thing it describes:
a FOURTH gate run was started and killed before that chain.** I began
`gate.py ph03` while still owing the `NOTES.md` m3 note, realised that any
`NOTES.md` edit after gate 1 costs a whole extra `gate → report → gate` cycle
(the record pins `NOTES.md`'s hash and `report.py` renders from the record), and
stopped it by exact PID — `/proc/1810366/cmdline` confirmed as
`check.py ph03-uudecode-bound`, together with its three parents. Nothing it
wrote survives: the chain above rewrote `results-php/gate/ph03-uudecode-bound.json`
and `results-php/tables/` from scratch. **So the true count is four gate
invocations, three of which were the chain.**

The `idiom` audit after the rename and the new entries:
`5 required, 3 forbidden spelling(s), 3 of them per-language`;
`forbidden: 6 spelling(s), 0 hit(s), 0 entry/entries with NO backticked spelling`.

### ⚠⚠ m5 — I refute the REVIEWER here, and both earlier claims are right conditionally

`TASK_PHP_013_REPORT.md` §12.3b said *"the closing bracket itself dirties the
tree"* (+59 lines to `results-php/preflight/_norow.preflight.json`).
`TASK_PHP_014` m5 said it *"does not reproduce"* — four bracket runs, tree clean
throughout.

**It reproduced here, exactly: +59 lines, same file.** `git status --porcelain`
captured immediately before and immediately after the two bracket commands
(`.temp/php15/40-status-before-bracket.txt` vs `42-status-after-bracket.txt`)
differ in exactly one line:

```
16a17
>  M results-php/preflight/_norow.preflight.json
```

**Both earlier claims are true and neither is the rule.** `PROTOCOL_PHP.md` §E's
*"identical runs collapse on CONTENT"* is the rule, and the reviewer named it
correctly — but then generalised from a session that had changed nothing the
preflight records. **This session changed two things it does record**:
`harness_php_sha256` (I edited `harness-php/provenance.py` for the ledger
rename) and `why_sizes` (ph03's row-specific `why` went 339 → 572 words), so the
entry is new content and does not collapse. Verified in the diff.

✅ **The statement that holds for the next agent, and it is neither of the two
that were made:** *the closing bracket dirties `_norow.preflight.json` **iff**
this session changed something the preflight record carries — the harness-php
sources, the manifest, the shim, or any row's `why` size. **A task that only
touches `patterns/` leaves it clean; a task that touches `harness-php/` does
not.*** `TASK_PHP_013` touched `harness-php/`; `TASK_PHP_014` touched nothing;
this one touched `harness-php/provenance.py`.

---

## §7 What I did NOT do, and what I am unsure about

1. ⛔ **`ph07` was not built.** §5.3.
2. ⚠ **m3 was not landed.** §2.5 — deferred with the design written into
   `NOTES.md` §12, not dropped.
3. ⚠ **m6 is only partly closed.** `idiom.why` now carries a marker saying the
   four clean `sanitizer_hardened` rows are not evidence the fix is complete,
   and that lands in the gate record and the rendered table because `why` is the
   only part of the contract the record echoes (**checked**:
   `'fix_commit_note' in json.dumps(record)` is `False`, `'provenance' in record`
   is `False`). **The structural gap remains** — a machine consumer reading
   `sanitizer_hardened` alone still sees four clean rows — and closing it needs a
   `harness/check.py` edit and a 33-pattern re-gate. Named as owed in
   `NOTES.md` §12.
4. ⚠ **`doc-citation-other` now shouts FOUR, and none of them is live code in
   this row.** Three are pre-existing citations inside
   `common-php/emalloc_shim.h`; the fourth is `NOTES.md`'s own sentence
   *describing* the citation it fixed, which quotes the old span in order to say
   it is gone. `c/kernel.c` was the fifth and is now `build.py::build_c`.
   Rephrasing the fourth would cost a full `gate → report → gate` for a `loud`
   entry that is not a failure, **and I chose not to pay it** — said here so the
   number is not read as four unfixed citations.
5. ⚠ **I did not re-run the mutation suite** (`TASK_PHP_014` §1.2, 19 mutants).
   `verus.rs` changed only in a comment and re-verifies `25 verified, 0 errors`,
   so the suite's conclusions carry — but I did not re-derive them, and the
   `NOTES.md` §11 cell that now cites "17 of 19" cites the review rather than a
   run of mine.
6. ⚠ **Unsure: whether `adversarial-floor.bin` earns its measurement slot.** It
   is 8 iterations over a 45-byte window, so it costs almost nothing, and it is
   the only input that reaches `:141`'s `floor()` arm adversarially and the only
   one that isolates hunk 2. But it is scope the task did not ask for, and a
   reviewer may reasonably say the benign short line was the whole assignment.
7. ⚠ **Unsure: the `kind` field on `provenance.divergences`.** It is documentation
   nothing reads, which `PROTOCOL_PHP.md` explicitly permits (`uses_allocator`
   has the same standing) — but that file's own durable lesson is that a
   declaration one step from being load-bearing is a hazard. **Nothing may come
   to depend on it**, and both `NOTES.md` and §A2 say so.
8. ⚠⚠ **THIS ITEM SAID THE OPPOSITE OF §6 UNTIL I RE-READ IT, AND I AM LEAVING
   THE CORRECTION VISIBLE BECAUSE IT IS THIS PROJECT'S OWN FAILURE MODE.** I
   drafted it as *"m5 confirmed against the reviewer — the closing bracket did
   not reproduce here either"* **before running the closing bracket**, on the
   strength of the reviewer's finding rather than a run. The bracket then
   dirtied `results-php/preflight/_norow.preflight.json` by +59 lines and §6
   records the refutation. **That is `PROTOCOL.md` rule 13 exactly** — a summary
   written from a report rather than from a measurement, contradicting the body
   below it — **committed by me, in the report whose §2 lands three findings of
   the same shape.** The check that caught it cost one `grep` of my own
   headers against my own §6.
9. ⚠ **The scratch was cleaned per `.memory/00-environment.md` constraint 6.**
   Deleted: the two probe binaries, the callgrind `.out` dumps (316 KB), the
   patched-tarball tree, the reconstructed old corpus, and three fetched
   `mbfilter.c` snapshots. Kept: every `.log`, `.py`, `.sh`, `.asm`, `.patch`
   and `.md`. **`.temp/php15/REBUILD.sh` regenerates every deleted blob**,
   including the callgrind step §2.1 rests on — which is the constraint's *"if a
   blob has no script that rebuilds it, write one before finishing"*.
   ⚠ It is **not** a re-run of this task's evidence and I did not execute it end
   to end; it is a recipe assembled from the commands that were run.
10. ⚠ **`NOTES.md` §0 cites `.temp/php13/bin/`, which no longer exists.**
   Pre-existing from `TASK_PHP_013` and correct as history (constraint 6
   mandates deleting those binaries), but it is a citation a reader cannot
   follow. Not fixed — `NOTES.md` is gate-hashed, so it would cost a full
   `gate → report → gate` for a sentence that is true.
11. ⚠ **I did not touch `RECAP_PHP.md`.** Manager-only. **What I refute or
   confirm is listed here and reconciliation is the manager's job**, including
   whether M5 belongs inside F29 or beside it, and whether §6's m5 adjudication
   retires both earlier claims or annotates them.
