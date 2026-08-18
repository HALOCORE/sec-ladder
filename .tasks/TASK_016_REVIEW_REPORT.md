# TASK_016_REVIEW_REPORT — the declarations are honest; the key would not have caught the thing it exists for

**(a) Are the four post-hoc declarations (p01, p02, p08, p16) honest?** **Yes** —
nothing was invented, every entry traces to prose that predates TASK_016, and
p01's and p16's `why` do say which spellings are *not* restricted. Two defects
inside that yes: p02 declares two things its own R1 does not do (M3), and p05's
retrofit silently dropped one of its four load-bearing prose bullets (m1).

**(b) Would the key have caught the TASK_014/TASK_015 defect?** **No.**
Demonstrated, not argued: `.temp/review016/gate-p05fork.log` is a **complete,
green `check.py: PASS`** on a p05 tree whose R3 is `data.chunks_exact(ncol)` —
the spelling its own verdict prints as `idiom FORBIDDEN chunks_exact` three
lines above the PASS — with `contract_sha256` **byte-identical** to the shipped
pattern's.

---

## Blocker

### B1 — the stated mechanism is false: changing a rung's idiom does *not* move `contract_sha256`, and a forbidden rung passes a full green gate

`harness/check.py:564-566` (stage 0b docstring), `.tasks/TASK_016.md:61-63`, and
`.memory/06-catalogue.md:112-115` all state the same value proposition:

> the whole value is that the declaration is inside the hashed block: **changing
> a rung's idiom must now move `contract_sha256`**, which is a signal review
> already reads.

`read_contract()` (`harness/check.py:455-466`) hashes the fenced `slb-contract`
block of `spec.md` **and nothing else**. A rung's spelling is not in it. So
changing a rung's idiom moves `source_sha256[.../safe_tuned.rs]` — which the
gate already recorded before TASK_016 — and leaves `contract_sha256` untouched.
`contract_sha256` moves only if somebody edits the *declaration*.

**Demonstration.** I forked `patterns/p05-index-flatten` into
`.temp/review016/patterns/p05fork/` (no file under `patterns/` was touched;
`check.py` accepts an absolute pattern path) and replaced `safe_tuned.rs` with
TASK_015's `.temp/p05r3/v05/tuned_chunks.rs` — the `chunks_exact` R3 that
`spec.md`'s `idiom.forbidden` names. Full run, all stages, no flags:

```
== verdict ===========================================================
    results -> results/gate/p05fork.json
    idiom REQUIRED  i*ncol + j written out in every rung, not strength-reduced
    ...
    idiom FORBIDDEN chunks_exact
    idiom FORBIDDEN a running row pointer
    ...
check.py: PASS
```

| | shipped p05 | p05fork (forbidden R3) |
|---|---|---|
| verdict / `complete_run` / `failures` | PASS / True / `[]` | PASS / True / `[]` |
| `contract_sha256` | `f133df87cbc992b8…` | `f133df87cbc992b8…` **same** |
| `idiom` object | — | **identical** |
| R3 marginal `Ir`/call, `-O3 isolated` | 1504.00 / 8834.70 | **1369.00 / 8377.70** |
| R4 marginal `Ir`/call | 1381.00 / 8435.70 | 1381.00 / 8435.70 |

So the gate now certifies, as a complete green run under the name p05, an
`R3 − R4` of **−12.00 / −58.00** — "safe Rust beats unsafe Rust", the retracted
headline — while printing the declaration that forbids it, unchanged, in the
same verdict.

**And the historical counterfactual is worse than that.** The two tasks the key
exists to stop did not run the gate on the number they published:

- `.temp/review014/NOTES.md` contains **zero** occurrences of `check.py`.
  TASK_014_REVIEW built its `chunks_exact` variant under `.temp/` and measured
  it with a private probe. Stage 0b would have printed **nothing at all** in
  that task.
- TASK_015 *did* run the gate — `.temp/p05r3/NOTES.md:207-208`,
  `check.py p05 -> PASS complete_run=True failures=[]  (1m24s)` — but on the
  *shipped* tree, at the end, as a regression check, hours after the forbidden
  number was measured (`.temp/p05r3/NOTES.md:56-60`) and written up. The
  declaration would have scrolled past once, in a log for a different purpose,
  attached to a different kernel than the one being reported.

**What the key actually buys** (real, and worth keeping): an author who *relaxes
the declaration* to license a swap moves `contract_sha256`, and the declaration
now appears in every verdict and in every committed `results/gate/*.json`. That
is a defence against quietly weakening the pin. It is not a defence against
measuring an unshipped variant, which is what happened twice.

**Failure scenario.** The next agent reads `.memory/06-catalogue.md:112-115`,
believes `contract_sha256` guards rung spelling, swaps p16's R3 for
`v16-tuned_split.rs`, re-runs the gate, sees PASS and an unmoved
`contract_sha256`, and concludes the swap is in-contract. Nothing in the tree
contradicts it.

**Fix (report only, per scope):** correct the three copies of the mechanism
sentence to what is true — *the hash makes weakening the declaration visible; it
does not detect a rung that violates it* — and, since Part 2 asked for a cheap
suggestion: `harness/report.py` has **zero** occurrences of `idiom`, so
`results/tables/*.md` — the artefact a writeup actually reads — carries no
declaration at all. Emitting the `forbidden` list as a header line there is one
function and reaches the reader who is not running gates.

---

## Major

### M1 — p16's "+14.30 on every rung, no published delta moves" is false: there are four different offsets and three published deltas move

`patterns/p16-tlv-walk/NOTES.md:882-884` and `.memory/03-measurement.md:390-392`
(landed, marked PROVISIONAL):

> the offset is a uniform **+14.30** across all three rungs … so every
> *difference* is unaffected and **no published delta moves**

Measured from the committed artefact `results/gate/p16-tlv-walk.json`
(`marginal_ir_per_call`, `-O3 isolated`) against `NOTES.md:153-160`'s table:

| cell | §2 (kernel-exclusive) small/large | gate (whole-program) | offset |
|---|---|---|---|
| `c-gcc` | 4062.0 / 32694.0 | 4077.72 / 32709.72 | **+15.72** |
| `c-gcc-h` | 4079.0 / 32735.0 | 4094.72 / 32750.72 | **+15.72** |
| `c-clang` | 2993.0 / 23761.0 | 3007.72 / 23775.72 | **+14.72** |
| `c-clang-h` | 3017.0 / 23815.0 | 3031.72 / 23829.72 | **+14.72** |
| R2 | 5095.0 / 40921.0 | 5109.30 / 40935.30 | +14.30 |
| R3 | 3037.0 / 23875.0 | 3051.30 / 23889.30 | +14.30 |
| R4 | 3010.0 / 23798.0 | 3024.30 / 23812.30 | +14.30 |
| **R5** | 3010.0 / 23798.0 | **3023.30 / 23811.30** | **+13.30** |

"Every rung" is three of eight cells. Published deltas that **do** move:

- **`R5 − R4 = 0`** (`NOTES.md:160`, the identity headline) → **−1.00 / −1.00**;
- **`R4 − c-clang = −17 / −37`** (`NOTES.md:155`) → **+16.58 / +36.58**;
- **`R4 − c-gcc = +1052 / +8896`** (`NOTES.md:153`) → **−1053.42 / −8897.42**.

Unaffected, correctly: `R3 − R4` (+27/+77), `R2 − R4` (+2085/+17123),
`R1h − R1` within each compiler (+24/+54 clang, +17/+41 gcc).

The cause is obvious once looked at: the offset is *the driver's per-iteration
work outside the kernel symbol*, and that is compiled by a different compiler per
rung. The engineer generalised from the only three rungs `.temp/p05r3` happened
to carry, and did not check the five it did not.

The R4≡R5 *conclusion* survives — it rests on `md5_fn` byte-identity, not on this
column — but the sentence "no published delta moves" is false, and the deltas it
breaks are exactly the **C-vs-Rust** ones that `PROTOCOL.md`'s checklist singles
out. **Failure scenario:** a writeup differences p16's R4 against p05's or p17's
C column, both quoted "whole-program marginal", and inherits a 1.4-instruction
error it has been told cannot exist.

### M2 — p16's hashed block contradicts itself, and the "owed decision" in `.memory/06-catalogue.md` rests on the contradiction

`patterns/p16-tlv-walk/spec.md:269` (`idiom.required[0]`):

> every comparison is subtraction-first: `end - p >= 3` and
> `vlen > end - (p + 3)`, **in every rung**

`patterns/p16-tlv-walk/spec.md:278` (`idiom.why`), same fenced block, nine lines
below:

> A consuming spelling (`split_first_chunk::<3>()` plus `split_at`) is
> **admissible under this declaration** and measures `10*nrec + 9` CHEAPER than
> the shipped R3 … So p16's published R3 number is a spelling's number

The named variant is `.temp/p05r3/v16/tuned_split.rs`. It contains **neither**
comparison. Its own doc comment (lines 14-16) says so:

```
//!   `end - p >= 3`            <-> `rest.split_first_chunk::<3>()` is `Some`
//!   `vlen > end - (p + 3)`    <-> `tail.split_at_checked(vlen)` is `None`
```

Two readings of `required[0]` exist and nothing disambiguates them: **(A)** those
two comparisons must be written, in which case `tuned_split` is *out of
contract* exactly as `chunks_exact` is out of p05's (p05's `required[0]` is
token-naming in exactly this style — "`i*ncol + j` written out in every rung");
**(B)** merely "no additive comparison", in which case it is admissible. `why`
asserts (B); `required[0]` reads as (A); `forbidden[0]` (the additive spellings)
is consistent with both.

This matters because the whole downgrade of p16's published R3 number turns on
it. `.memory/06-catalogue.md:100-106` has already landed:

> a cheaper *admissible* R3 exists for both (p16's `split_first_chunk::<3>()` is
> `10·nrec + 9` cheaper than shipped). Either swap those cells or state in each
> `NOTES.md` …

Under reading (A) there is no admissible cheaper R3 for p16 and the owed decision
is p17-only. **Failure scenario, and it is B2's own shape one level up:** a
future agent picks whichever half of the block licenses the measurement it wants
— which is precisely what happened when `.memory/01-ladder.md` and p05's
`spec.md` disagreed and "the general one won twice". The defect has been
reproduced *inside a single hashed block*.

p17's equivalent claim is **correct** and I checked it:
`.temp/p05r3/v17/tuned_suffix.rs` keeps `i64` start/end, keeps the conjunctive
`if start < content_len && start >= 0`, keeps `nserved`, so it satisfies p17's
four `required` entries. p17's "not restricted" note stands.

### M3 — p02's `idiom.required` states two things its own R1 does not do, with no R1 carve-out, in the one pattern whose R1 *is* the bug

`patterns/p02-buffer-copy/spec.md:210` and `:213`:

> "the fit check is subtraction-first … **spelled identically in every rung**"
> "the kernel is **total in len**: all 65536 values a u16 prefix can express are
> handled"

`patterns/p02-buffer-copy/c/kernel.c:28-31` has **no fit check at all** and is
not total in `len` — the two `(void)` casts and the unguarded `memcpy` are p02's
entire finding. R1 is a shipped, measured, gated cell.

p16 (`spec.md:272`, "R1 omits only the second check — it keeps `end - p >= 3`")
and p17 (`spec.md:385`, "R1 omits only `&& start >= 0`") both carve R1 out
explicitly in their `required` lists. p02, retrofitted in the same task, does
not. The inherited prose (`spec.md:47`, "Every rung spells the test
identically") carries the same inaccuracy, so this is faithful transcription of a
sloppy sentence rather than invention — but it is now a *hashed pin*, which is a
different object.

**Failure scenario.** A later agent is told the `idiom` block is the machine-read
statement of what every rung must do, reads `required[0]`, notices `c/kernel.c`
violates it, and adds the three-term check to R1 — deleting the bug, the
`R1`-vs-`R1h` axis and p02's whole reason to exist. That is a *more* plausible
accident than the one stage 0b was built for, because this one is licensed by
the pin rather than merely unmentioned by it.

---

## Minor

### m1 — p05's retrofit dropped a load-bearing bullet, in the pattern the key exists for

`patterns/p05-index-flatten/spec.md:83-85` (prose, TASK_013):

> **`nrow * ncol` is folded into the result**, so a rung that walks a different
> number of elements cannot produce the same checksum

That bullet is **not** in `idiom.required` (`spec.md:318-322`), which reproduced
the other three bullets of the same section. p16 declared its equivalent
(`"nrec is folded into the result"`, `spec.md:271`) and p17 declared its
(`"nserved is folded into the result"`, `spec.md:386`). Only p05 lost it — and
p05's `why` is the one that says "**Moved** into the hashed block … from the
prose section 'Load-bearing, do not improve'". The task said "do not rewrite it";
one quarter of it was dropped.

Low severity because the bullet is an anti-skipped-work guard that stage 2
(model checksum) enforces anyway, and because the `chunks_exact` variant keeps
it. It is still a hole in a pin that is now the authoritative copy.

### m2 — "Moved into the hashed block" is inaccurate in all six `why` texts: the prose was **duplicated**, and the copies can now drift

`git show 4bd7deb -- patterns/*/spec.md` is +0/−0 on every prose section; p05's
lines 69-88 and p17's 125-146 are untouched and still present. So each pattern
now carries two statements of its idiom in one file — one hashed (the JSON), one
not (the prose) — and nothing checks they agree. m1 is that drift, already
present on the day the key landed.

Reporting it as minor rather than asking for a delete: keeping the prose is
probably right (it is where a human reads it), but the `why` should say
*"restated in the hashed block; the prose above is the same statement"* rather
than "moved", and whoever edits one must edit the other.

### m3 — the check's residuals, named so the next agent does not re-run them

Re-ran the 8 shipped selftests: **8/8 pass**. Then 18 further attacks
(`.temp/review016/attack_idiom.py`). Rejected as they should be: bare-string
`idiom`, `null`, list-valued `idiom`, unknown key alongside three good ones,
`forbid`-for-`forbidden`, non-string list entries, whitespace-only entries,
list-valued `why`, bare-string `required`/`forbidden`. **Accepted, and I judge
all of them correctly accepted under the "honest mistake, not malicious author"
threat model** — but they are the residuals, and none is currently named
anywhere:

- a one-word `why` (`"reasons"`), and a one-character `why` (`"."`);
- a one-character `required` entry;
- `required` padded with 40 copies of the same string (the verdict then reports
  "40 required");
- the same string in **both** `required` and `forbidden`;
- `forbidden` naming something no rung could use;
- a declaration that inverts the pattern's own prose.

The empty-`forbidden` path is **confirmed correct**: `check_idiom` shouts and
does not fail, and an absent `forbidden` key behaves identically —
`!! [idiom] this pattern forbids no spelling by name …`, `failures: []`. The
`MAX_TWIN_JUSTIFICATIONS` shape is not reintroduced. Note that no shipped
pattern exercises it: all six declare ≥1 forbidden spelling.

### m4 — the manager's Part 4 baseline is the wrong commit

`TASK_016_REVIEW.md:78` says to check `git show 9272a41^:results/gate/<p>.json`
against the committed one. `9272a41` touched only `.memory/` and `RECAP.md`
(`git show --stat 9272a41`), so `9272a41^` **is** `4bd7deb` — the post-change
tree. That comparison is vacuously equal and certifies nothing. The correct
baseline is `4bd7deb^` (= `fb28921`), which is what I used.

---

## Confirmed as claimed

- **The invariant holds, from git, at the right baseline.** `4bd7deb^ → 4bd7deb`:
  **28/28 `md5_fn` unchanged, 564/564 `marginal_ir_per_call` cells unchanged**,
  `contract_sha256` moved in **6/6**. The only other value changes in all six
  artefacts are 7 ASan PID/ASLR strings and p05's two nondeterministic C stdouts
  on `adversarial-dims.bin` — the latter documented at
  `patterns/p05-index-flatten/NOTES.md:694-701` ("four different answers from
  four builds", "unrepeatable") and varying across all three historical gate
  records, so not a TASK_016 regression.
- **`check.py` changed nothing else.** `git diff --numstat 4bd7deb^ 4bd7deb --
  harness/check.py` = `145  0`, six hunks, **pure additions**: the stage-list
  docstring, `import textwrap`, the stage 0b block, one `check_idiom` call, the
  `"idiom"` key in the JSON doc, and the verdict print. No existing line moved.
- **Nothing invented.** Every `required`/`forbidden` entry in p01, p02, p08 and
  p16 traces to prose or a rung doc comment that predates TASK_016. p16's five
  "load-bearing" bullets (`spec.md:51-85`) map exactly onto its 4+2 entries;
  p08's five bullets plus its "The scratch buffer" section map onto its 6+4;
  p02's "four things" map onto four of its five, the fifth being the
  retraction-critical R2/R3 copy spelling from `NOTES.md §3a`; p01's three come
  from `spec.md:13-19` and `:29-38`. (p16's bullets: `spec.md:51-84`.)
- **p01's and p16's `why` do disclose what is not restricted**, as the engineer
  claimed. p01: *"beyond the three required entries no spelling of the fold is
  excluded and p01's numbers are a spelling's numbers"*. p16: *"Note what is
  deliberately NOT restricted: the R2/R3/R4 spelling of the walk and of the
  value fold"*.
- **Cross-references (Part 6a).** I resolved **all 46** `NOTES.md <n>` references
  in `patterns/*/{*.rs,model.py,spec.md,c/*}` against the target file's actual
  section headings: 46/46 resolve. Content-checked the two the engineer
  corrected — `p05/spec.md:397 → §9` lands on "The `Ir` floor: derived, 124.5 /
  992.2 … tightest margin 8.5×" (`NOTES.md:835-838`), and `p08/spec.md:401` +
  `p08/model.py:257 → §9` land on the same passage in p08's `NOTES.md:1091-1094`.
  Both correct. The engineer's "two mis-targeted, not one" contradiction of the
  task stands.
- **Refuted claims (Part 6c).** p05's `+11.00 … flat, O(1)` is struck in
  `README.md:117-123` and `NOTES.md:1046-1051` with the retraction text
  following; `nrec + 3`, "first true O(n) safety cost", "+32 Ir/call flat" and
  "O(1) per call" are all struck or explicitly corrected in the pattern files,
  `RECAP.md:205-235` and `.memory/01-ladder.md:258, :468-470`. **There is no
  top-level `README.md`** (only `CLAUDE.md`, `PLAN.md`, `RECAP.md`,
  `TOOLCHAIN.md`); `PLAN.md` carries none of the refuted numbers. I found no
  unstruck survivor.
- **Reproducibility.** Re-ran the full p05 gate. Every one of ~550 recorded
  values reproduces byte-for-byte except the 2 ASan diagnostics (PID/ASLR) and
  the 2 documented nondeterministic C stdouts. All 96 `marginal_ir_per_call`
  cells and all 4 `md5_fn` values are exact.

---

## Part 5 — adjudication: **state the limitation; do not swap either cell**

**p16: the premise is broken (M2).** Under `required[0]`'s token-naming reading —
the reading p05 established and the reading that makes the whole key mean
anything — `v16-tuned_split.rs` is *out of contract*, not admissible, because it
contains neither of the two comparisons the entry names. So there may be no
cheaper admissible R3 for p16 at all. **The first owed action is to disambiguate
`required[0]`, not to swap a cell.** Doing it the other way round decides the
question by choosing a measurement.

**p17: admissible, and still do not swap.** `tuned_suffix.rs` genuinely satisfies
p17's four `required` entries. Three arguments against swapping anyway:

1. **The beater beats its own R4 too.** `R3′ − R4 = −19.00`
   (`.temp/p05r3/NOTES.md:50-51`). Swapping R3 alone publishes "safe Rust beats
   unsafe Rust" from an *unmatched pair* — which is TASK_014/015's defect
   exactly, re-committed as a shipped cell. An honest swap has to move R4 as
   well; TASK_015_REVIEW measured that pair (`R3′ − R4 ≈ −10·nsuf + 9`), so the
   swap does not produce a stable number, it produces a different one.
2. **No swap can ever terminate.** `.memory/01-ladder.md` finding 14:
   `inf(R4) ≤ inf(R3)` **by construction**, because R4 is defined by permission.
   Chasing the cheapest admissible R3 is chasing a quantity that has no fixed
   point, and TASK_015_REVIEW measured the gap moving from `+11` to `nrow + 9`
   on the first extra round.
3. **Cost is real and buys nothing.** For p16: a new `safe_tuned.rs`, 32 cells
   rebuilt, a ~2-minute gate, a `measure.py` wall-clock re-run (30 interleaved
   reps), and **16 occurrences across 5 files** (`p16/NOTES.md` ×9,
   `p16/README.md`, `RECAP.md` ×2, `.memory/01-ladder.md` ×3, plus
   `results/tables/p16-tlv-walk.md` regeneration) rewritten — and `§3`'s whole
   `7 + 5·nrec` / `7 + 7·nrec` law, which TASK_015_REVIEW swept over 68 blobs,
   deleted and re-derived. p17 is comparable and additionally owes the sweep
   inputs it does not ship.

**So: state the limitation.** Both `NOTES.md` §10 sections and both `idiom.why`
texts already do; what is missing is the same sentence in `README.md`'s headline
table, where the number is actually quoted. And adopt p16's own `why`'s
prescription for anything stronger: *"the honest move is to declare the walk's
spelling here BEFORE measuring, the way p05 did at TASK_013."*

**Was it right not to add a p16 restriction that would have excluded the cheaper
spelling retroactively? Yes** — and for a stronger reason than the engineer gave.
Writing a `forbidden` entry *after* seeing which spelling is cheaper is the
self-certification shape `.memory/02-bench-rules.md` warns about, in its purest
form: the declaration would have been selected by the measurement. Declining
that was correct. M2 is a different problem — an ambiguity that was already
there, not a restriction that should have been added.

---

## Part 7 — clean negatives (attacks that did not land)

1. **"A `required` entry no rung honours" on p01, p08, p16.** Read every rung of
   all three against every entry, R1/R1h and `verus.rs`/`safe_naive_verus.rs`
   included. All hold. p16's `required[3]` and p17's `required[2]` correctly
   carve out R1; p08's "in all six rungs" claims for the guard, `dr = d + r`,
   `nrep_w % 4` and the zero-initialised local `SCR` array hold in
   `c/kernel.c:54-77`, `c/kernel_hardened.c:37-59`, `safe_naive.rs:63-79`,
   `safe_tuned.rs:50-66`, `unsafe.rs:67-83` and `verus.rs:409-419`. Only p02
   (M3) failed this probe.
2. **"p02's `memcpy` idiom is conspicuously absent"** — the manager's first
   suspect. It is not: `required[4]` pins "R2 copies index-by-index; R3 reslices
   both sides once and copies with `copy_from_slice`", `required[0]` pins the
   subtraction-first check that is *why* rustc forms no memcpy in R2, and `why`
   spells out the `bulk_calls [] → ['memcpy@GLIBC_2.14']`, `118 → 87` mechanism
   and that it was 100% of the retracted delta. p02 is the best-protected of the
   four.
3. **"p16's unroll is conspicuously absent"** — the manager's second suspect.
   Also not, in the sense that matters: the 4× unroll is a *codegen consequence*
   of R2-vs-R4, `NOTES.md:31-34` already calls R2 "the naive indexed **spelling**"
   and the 2.00/2.25 split was confirmed by construction with a rolled-vs-rolled
   control (`NOTES.md §3.4`), so the headline is not resting on an undeclared
   choice presented as a language fact. The residual is only that `why` draws the
   "spelling's number" conclusion for R3 and not for R2; R2's disclaimer lives in
   `NOTES.md` instead.
4. **"TASK_016 moved a measured column."** It did not — 28/28 and 564/564, from
   git at the correct baseline, plus a full re-run of p05 that reproduces every
   measured value exactly.
5. **"`check.py` changed something else while nobody was looking."** It did not:
   145 insertions, 0 deletions.
6. **"The empty-`forbidden` path can hard-fail an honest pattern."** It cannot —
   run, it shouts and passes, and an *absent* `forbidden` key behaves the same.
7. **"A cross-reference is still mis-targeted."** 46/46 resolve, and the two
   corrected ones are content-correct. The previous review's "65 checked, one
   mis-targeted" and the engineer's "two, not one" are both consistent with what
   I see.
8. **"An unstruck refuted claim survives somewhere."** Swept `patterns/`,
   `RECAP.md`, `PLAN.md`, `.memory/` for `+11.00`, `nrec + 3`, `+32 Ir/call
   flat`, `O(1) per call`, "first true O(n)", "not caught by ASan". Every hit is
   struck, corrected in place, or is a live claim about a different pattern.
9. **"p05's `adversarial-dims` C stdout changing between gate runs is an
   undocumented nondeterminism."** It is documented, sharply, at
   `patterns/p05-index-flatten/NOTES.md:694-701`.
10. **"p17's `why` overclaims like p16's."** It does not; `tuned_suffix.rs`
    satisfies all four of p17's `required` entries. Checked line by line.
