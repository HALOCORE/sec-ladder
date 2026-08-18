# TASK_017_REVIEW_REPORT — the token reading is a new restriction adopted after the measurement, not a reading of what the declaration said; and the manager's premise about *which way* it protects the number is wrong

**The one line.** p16's token reading is **not defensible as a disambiguation**
— the pre-TASK_017 hashed block says the opposite three times and TASK_017
deleted one of the three — but it is also **not "a declaration written to
protect a number" in the direction the task assumes**: measured, the token
reading makes p16's published safety tax **4.5× larger**, not smaller. What it
protects is the shipped cells' *standing* and a swept law, not a favourable
figure. It is defensible as **policy adopted at TASK_017, after measuring**, and
must be labelled that way; it is not defensible as a statement about what
`required[0]` already meant. The deciding evidence is not rhetorical: **the same
standard is refused for p17, in the same commit, in a sentence the same engineer
wrote** (B1).

---

## Part 1 — the four grounds, each on its own merits

### Ground (iii) — "the exclusion falls SYMMETRICALLY". Verified true, and load-bearing beyond what it supports.

**The factual half is correct and I checked it.**
`.temp/p05r3/v16/unsafe_consume.rs:22,26` walks on `while rem >= 3` and
`if vlen > rem - 3` with a raw pointer; neither named token appears. Under the
token reading it is out of contract, exactly as rows 3 and 4 are. The consuming
*R4* control does go out with the consuming R3s. Ground (iii) is not a bluff.

**The inference is where it overreaches.** "Symmetrically … it excludes a
representation, on both sides of the pair" invites the reader to conclude the
choice is delta-neutral. It is not. From `patterns/p16-tlv-walk/NOTES.md:963-970`
(whole-program marginal `Ir`/call, `small`/`large`):

| | small | large |
|---|---:|---:|
| R3 shipped − R4 shipped (**published**) | **+27** | **+77** |
| R3′ − R4′ (the excluded matched pair) | +7 | +17 |
| headroom removed from the **safe** side | 49 | 109 |
| headroom removed from the **unsafe** side | 29 | 49 |

And as laws, swept over 68 blobs with zero residual
(`patterns/p16-tlv-walk/NOTES.md:993-1000`): the published pair is
`7 + 5·nrec` / `7 + 7·nrec`; the excluded pair is `7` **flat** / `7 + nrec`.

So the exclusion is symmetric in *existence*, 2:1 in *cardinality*, and
**3.9× / 4.5× asymmetric in effect on the published headline**. At `nrec = 10`
the reading is the difference between "safe Rust costs 77 instructions per call
more than unsafe" and "17" — a 7× difference in the slope of p16's central
finding (`.memory/01-ladder.md` finding 4). A `why` that says "symmetrically"
without that number is doing rhetorical work its own `NOTES.md` §10 disproves
one file away.

**Consequence for the task's premise, which is a contradiction of the manager.**
The direction is the opposite of the one the review spec assumes. The token
reading does **not** make p16's number look better in magnitude; it makes the
safety tax bigger. What it actually buys is (a) the shipped R3 keeps its status
as *the* p16 R3 rather than "a spelling 109 `Ir`/call worse than an admissible
one", (b) §3's `7 + 5·nrec` law and its 16 occurrences across 5 files survive
un-re-derived, and (c) p16's headline retains a 7× larger `nrec` coefficient.
That is a real interest and it should be named as *that*, not as "looks better".

### Ground (i) — "house convention". The three cited precedents cut the other way, textually.

Every entry the `why` cites carries an explicit token-level marker that p16's
`required[0]` did **not** have before TASK_017 added one:

| pattern | entry | strictness marker | does its `forbidden` name the alternate representation? |
|---|---|---|---|
| p05 `required[0]` | "i\*ncol + j **written out** in every rung, **not strength-reduced**" | yes, twice | **yes** — `chunks_exact`, "a running row pointer" |
| p02 `required[0]` | "… **spelled identically** in every rung …" | yes | no (names the semantic complement) |
| p17 `required[1]` | "the one conjunctive `if start < end && start >= 0`, **not two `continue`s**" | yes (explicit negative) | no |
| **p16 `required[0]` (pre-TASK_017)** | "every comparison **is subtraction-first**: `end - p >= 3` and `vlen > end - (p + 3)`, in every rung" | **none** — property predicate + exemplar | **no** — names only the additive spellings |

p05 is the only self-consistent token pin in the set, and it is self-consistent
precisely because its `forbidden` names the two representation changes by name.
p16's `forbidden` names the additive spellings, i.e. the semantic complement of
the *property*. The fact that TASK_017 had to insert the words
"**AND IS SPELLED AS THESE TOKENS**" is itself evidence the original text did not
carry them.

Two further weaknesses in the citation:

- **p17's precedent is explained by its own `why` as a toolchain limit, not as a
  spelling pin**: "The `continue` spelling is **not expressible in Verus**
  ('for-loops do not yet support continue')". An entry that rejects a
  semantically identical spelling *because the verifier cannot compile it* is not
  evidence that `required` entries in this project constrain shape for
  measurement purposes.
- **p01 `required[2]`, p02 `required[4]`, p08 `required[1]`** all pin
  representation — and all do it by naming the rung and its construct explicitly
  ("R2 indexes `v[i]` element by element; R3 reslices the window once"). None
  does it by naming a comparison and relying on "in every rung".

### Ground (ii) — "these two tokens ARE the traversal representation". True, and a non-sequitur as stated.

The claim that pinning them "is what makes `R3 − R4` a difference in safety
rather than a difference in representation" does not follow. Under the semantic
reading p16 would have **two** matched pairs — cursor-and-end (`+27/+77`) and
consuming (`+7/+17`) — each internally matched. The unmatched-pair defect
TASK_014/TASK_015 shipped is produced by comparing `R3′` against the *shipped*
`R4` (`−22/−32`), which is a discipline failure, not a licensing failure; the
semantic reading does not require it and the token reading does not prevent it
(the gate cannot check either — see the fork re-run below). Ground (ii) is a good
argument for *wanting* one representation per pattern. It is not evidence about
what `required[0]` said.

### Ground (iv) — `inf(R4) ≤ inf(R3)`. Correct, and it proves too much.

Finding 14 (`RECAP.md:143-176`, restated `.memory/01-ladder.md:23-27`) is right
and the "no fixed point" consequence is right. But it is a property of **every**
pattern's R3/R4 pair, so as an argument it selects the token reading for p05,
p02, p08, p16 **and p17** alike. p17 was not narrowed. An argument that is
applied to exactly the one pattern where narrowing removes a cheaper competitor,
and not to the one where the competitor stays, is not being applied neutrally
— which is B1.

### The counterfactual defence is untestable *and* vacuous, and a testable one exists

The block asserts: "the same four reasons pick the same reading if the consuming
spelling had measured DEARER." In that world the reading has **no consequence**
— `.memory/01-ladder.md`'s "quote the cheapest spelling you can find" would leave
the shipped R3 in place either way, and nothing would have forced a resolution.
"I would have chosen the same in the world where the choice does not matter" is
not evidence. The testable counterfactual is p17, and it fails (B1).

### The question that matters: would a disinterested party have read it the same way? **No — 3:1 against, on the text of the same hashed block.**

Pre-TASK_017 block, `git show fd91ae7:patterns/p16-tlv-walk/spec.md`. Statements
bearing on the reading:

1. `required[0]`: "every comparison is subtraction-first: `end - p >= 3` and
   `vlen > end - (p + 3)`, in every rung" — supports (A) **only when read at
   maximal strictness**, and only if "in every rung" is doing the work that
   p05's "written out" and p02's "spelled identically" do explicitly.
2. `why`: "Note what is deliberately **NOT restricted: the R2/R3/R4 spelling of
   the walk** and of the value fold, beyond the comparisons above." — (B).
3. `why`: "A consuming spelling (`split_first_chunk::<3>()` plus `split_at`) **is
   admissible under this declaration**" — (B).
4. `why`: "if a later task wants it to be more than that, the honest move is to
   **declare the walk's spelling here BEFORE measuring**, the way p05 did at
   TASK_013." — (B), and decisively: it states that the walk's spelling **is not
   yet declared**. Under (A) that sentence is incoherent.

Three sentences to one, and the three are the *specific* disclosures, written
knowing the consuming spelling was cheaper (TASK_016 wrote them after TASK_015
measured `10·nrec + 9`). A statement made against the author's own interest, with
the measurement already in hand, is the more credible one. The reading TASK_017
adopted required deleting one of them (`the walk` was removed from the
not-restricted list) and keeping sentence 4 verbatim in the new `why`, where it
now advises a future task to do — before measuring — the thing TASK_017 has just
done after measuring.

**The honest alternative**, which the task invited: keep the token pin if it is
the better contract going forward, but label it truthfully. Something neither
reading captures, e.g.:

> `required[0]` was **ambiguous** as written and both readings were defensible.
> TASK_017 **adopts** the token reading as a new restriction. It is adopted
> *after* the spellings were measured, which `.memory/02-bench-rules.md` warns
> against, and the mitigation is that it is stated here, dated, with the excluded
> rows and their deltas kept in `NOTES.md` §10 and marked *admissible under the
> declaration as it stood when they were measured, out of contract from TASK_017*.

The engineer's mitigation ("zero measured admissible alternates; 'cheapest
admissible' is unestablished") is honest and is **most** of what is owed — it is
recorded in three places and I confirmed all three. It is **not sufficient**,
because it discloses the *consequence* while describing the *act* as a
disambiguation rather than an adoption. `patterns/p16-tlv-walk/NOTES.md:975-976`
("Until then this section said all six rows were admissible, because `spec.md`'s
`idiom` block contradicted itself") is the closest the tree comes, and it still
frames the change as resolving a contradiction rather than as choosing a side of
it after seeing the numbers.

---

## Blocker

### B1 — the token standard is applied to p16 and refused for p17, in the same commit, and p17 is the precedent p16's own `why` cites for it

`patterns/p16-tlv-walk/spec.md` `idiom.why`, ground (i), cites p17's
`required[1]` — "the one conjunctive `if start < end && start >= 0`, not two
`continue`s" — as proof that "a `required` entry in this project constrains
shape, not only meaning".

p17's cheaper alternate, `.temp/p05r3/v17/tuned_suffix.rs:46-47`:

```rust
let start: i64 = content_len - s;
if start < content_len && start >= 0 {
```

`grep -n '\bend\b' .temp/p05r3/v17/tuned_suffix.rs` returns **two hits, both in
doc comments** (lines 13 and 18); there is **no `end` binding anywhere in the
code**. The shipped p17 rungs all have `let end: i64 = content_len;` followed by
`if start < end && start >= 0` (`safe_tuned.rs:46-47`, `unsafe.rs:56-57`,
`safe_naive.rs:50-51`).

Under the standard p16 adopts, `tuned_suffix.rs` is out of contract on **two**
entries: `required[1]` (the named tokens `start < end` are absent) and
`required[0]` ("start and **end** are int64_t / i64 in every rung" — there is no
`end`). Its doc comment even uses the identical rhetorical device that
TASK_016_REVIEW M2 cited as *proof* that `tuned_split.rs` is out of p16's
contract — a shipped-token ↔ replacement table:

```
tuned_split.rs:13-14   `end - p >= 3`         <-> `rest.split_first_chunk::<3>()` is `Some`
tuned_suffix.rs:18     `start < end`          <-> `start < content_len`
```

Yet the **same commit** (`89f6598`) writes into
`patterns/p17-http-range/NOTES.md`:

> `.temp/p05r3/v17/tuned_suffix.rs` … satisfies **all four** of p17's `required`
> entries: `i64` endpoints, **the one conjunctive `if start < end && start >= 0`**,
> `nserved` folded, no `Range:` text parsing.

and `patterns/p17-http-range/NOTES.md:~940` keeps "All four rows satisfy p17's
declared idiom — it constrains the *signedness*, the *guard* and what R1 omits,
**not how the fold or the table walk is spelled**" and "Row 3 keeps `start` and
`end` `i64`" — the last of which is **false of the file**.

So the tree now holds, simultaneously: *a `required` entry names tokens, and a
spelling that replaces the named tokens with an equivalent is a different
benchmark* (p16), and *a `required` entry names the guard's shape, and a
spelling that replaces its named tokens with an equivalent satisfies it* (p17).
The two patterns' cheaper alternates differ only in which one the project would
have to give up a shipped number for.

**Failure scenario.** A later agent is tasked with p17's owed `nsuf` sweep or
with reconsidering its R3. It applies p16's standard — cited in p16's block as
"house convention" — finds row 3 out of contract, and either (a) silently
retracts p17's published limitation ("+32 is the cost of *this* R3's spelling
and is not what safety costs on this kernel"), leaving p17 with zero measured
admissible alternates too and no record of why, or (b) notices the two patterns
disagree and has no way to tell which is the convention. This is TASK_016_REVIEW
M2's defect — "a future agent picks whichever half licenses the measurement it
wants" — reproduced one level up, *across* two hashed blocks instead of inside
one, and this time it was introduced by the repair.

**Not in scope to fix, and I am not proposing which way it resolves.** What is
owed is that one standard be applied to both, stated as an adoption with a date,
and that either p16's exclusion be withdrawn or p17's admissibility claim be
withdrawn — with the excluded rows' deltas kept either way.

---

## Major

### M1 — the repaired `why` deletes the disclosure that earned p16 its honesty verdict, and keeps the sentence that contradicts the new reading

Detailed above. Two specifics with file:line:

- `patterns/p16-tlv-walk/spec.md` `idiom.why`: pre-TASK_017 "NOT restricted: the
  R2/R3/R4 spelling of **the walk** and of the value fold"; post-TASK_017 "NOT
  restricted: the R2/R3/R4 spelling of **the value fold and of the header
  read**". `the walk` was removed. TASK_016_REVIEW's finding (a) — "the four
  post-hoc declarations are **honest**" — rests explicitly on "p01's and p16's
  `why` **do** disclose what is not restricted", quoting p16's "Note what is
  deliberately NOT restricted: the R2/R3/R4 spelling of the walk…". That verdict
  no longer applies to the block on its own terms.
- The same `why` still ends "the honest move is p05's at TASK_013 — **declare
  the walk's spelling here BEFORE measuring**", which is now advice not to do
  what the entry above it just did.

**Failure scenario.** A reviewer three tasks from now checks p16's declaration
for the disclosure TASK_016_REVIEW certified, does not find it, and either
re-opens the whole honesty question or (worse) concludes the walk's spelling was
declared at TASK_016 and that `+27/+77` is a pre-registered matched pair. It is
not: the cursor pin dates from `89f6598`, four tasks after the measurement.

### M2 — `harness/report.py` states a false mechanism for the failure it fixes, in the task whose Part 1 was deleting a false mechanism sentence from a harness docstring

`harness/report.py:105-107`:

> it is a reader who quotes `results/tables/p05-index-flatten.md` without ever
> opening `patterns/p05-index-flatten/spec.md`, **which happened in two
> consecutive tasks and cost a published headline**

and `harness/report.py:13-16`: "p05's number was quoted twice by agents who never
opened its `spec.md`".

Measured:

```
.temp/review014/NOTES.md : 0 hits "results/tables", 1 hit "01-ladder", 0 hits "spec.md"
.temp/p05r3/NOTES.md     : 0 hits "results/tables", 0 hits "01-ladder", 2 hits "spec.md"
```

Neither task read `results/tables/*.md`. The project's own record says what they
did read: `.memory/01-ladder.md:15-22` — "this table names `chunks_exact` as an
R3 technique … **Two consecutive tasks quoted this table as licence**, measured a
forbidden spelling, and reported the result as p05's number"; and
TASK_016_REVIEW B1 — TASK_014_REVIEW "built its `chunks_exact` variant under
`.temp/` and measured it with a private probe", with zero occurrences of
`check.py`.

`.memory/06-catalogue.md:118-121` inherits the overclaim in weaker form: "The
observed failure was a reader quoting a number without opening `spec.md`; **this
is the only mechanism that touches it**."

**The change itself is good and should stay** — a declaration above every table
is worth having on its own merits. What is wrong is the evidential claim
attached to it. **Failure scenario:** the next agent budgets against "this fixes
the observed failure", does not add the same declaration to the artefacts the two
agents *actually* read, and the next occurrence comes through the same door.

### M3 — `harness/check.py:868` still asserts the exact property TASK_017 measured to be false, in the docstring of the function that computes the affected number

`check_marginal_ir`'s docstring, describing the marginal-`Ir` slope:

> which is symbol-independent … and **cancels the loader and environment terms
> exactly**.

TASK_017 measured that it does not, on p08, and wrote that into
`patterns/p08-overlap-move/NOTES.md:167-190` and
`.memory/03-measurement.md:428-452`. `harness/check.py` was **open in this task**
(50+/10− applied to it) and two other docstrings in the same file were corrected
for exactly this class of error. `_callgrind_total`'s docstring at `:845-847` is
still true (within-session) and needs no change; `:868` is the one that is now
false.

**Failure scenario.** The next agent sees p08's 12 cells move by 0.02–0.08
between sessions, reads `:868`, concludes the marginal cannot move with the
environment, and spends the session hunting a phantom code change — which is
what TASK_017 itself had to do. Or quotes p08's marginals to the hundredth in a
cross-session comparison on the strength of that sentence.

### M4 — "the exclusion falls SYMMETRICALLY" is true in existence and misleading in effect

Numbers in Part 1 above. The word carries the block's whole claim to
neutrality — "this reading does not protect the shipped safe rung by excluding
only its competitor" — and the pair's delta moves from `7`/`7 + nrec` to
`7 + 5·nrec`/`7 + 7·nrec` under it. **Failure scenario:** a reader of
`results/tables/p16-tlv-walk.md` (where the whole `why` is now printed) takes
"symmetric" to mean "the published delta is unaffected by the reading", and
quotes `+77` as p16's safety cost without knowing that the excluded matched pair
measures `+17` on the same input.

---

## Minor

- **m1** — `.memory/06-catalogue.md:149` still carries the false mechanism
  sentence verbatim ("so changing a rung's idiom must move `contract_sha256`"),
  inside a block headed "Superseded design notes (kept because the argument
  matters)". A grep for the sentence finds it. Separately, `:130-139` describes
  p16's block as "**not even well-posed** … Disambiguate `required[0]` before
  deciding anything downstream of it" as if current, twenty lines after
  announcing it CLOSED at TASK_017.
- **m2** — p16's `why` is **3685 characters**, 3.0× the mean of the other five
  (1176–1317), and `report.py` renders it as a single markdown blockquote line
  (`results/tables/p16-tlv-walk.md:38`). Part 2's actual ask — the `forbidden`
  list above the numbers — *is* prominent (6 bullets at line 30-35 of 147, above
  every `Ir` table). The argument is not readable, and it is the argument that
  carries B1/M1/M4.
- **m3** — the "≤0.08 Ir/call" bound on p08's environment drift
  (`patterns/p08-overlap-move/NOTES.md:191`, `.memory/03-measurement.md:449`) is
  the movement observed between two gate runs, not the size of the effect. On
  `unsafe/O3/whole/small.bin` the committed record is **7292.12** and I measured
  **7292.14 / 7292.18 / 7292.24 / 7292.26 / 7292.30** across environments —
  spread **0.18**, 2.25× the stated bound. The operative advice ("quote to the
  instruction, not the hundredth") is right and unaffected.
- **m4** — `patterns/p16-tlv-walk/spec.md` `idiom.why` ground (iv): "the measured
  R4′ is already **29 Ir/call** cheaper than the shipped R4" quotes only the
  `small` figure for a quantity the same tree gives as `5·nrec + 9` / `4·nrec + 9`
  (29 small, **49** large). The project's own rule is to say which input, every
  time.
- **m5** — the ambiguity was three-way, not two-way, and the `why` lumps rows 3,
  4 and 6 together in a way none of the readings supports.
  `tuned_split.rs` satisfies "every comparison is subtraction-first"
  **vacuously** (it contains no comparison at all). `tuned_splitat.rs:17,21` has
  `rest.len() >= 3` and `vlen > tail.len()` — comparisons that are neither
  subtraction-first nor additive, so it is arguably out of contract under the
  *literal semantic* reading too. `unsafe_consume.rs:22,26` has one of each
  (`rem >= 3` is not a subtraction; `vlen > rem - 3` is). Only the token reading
  gives a clean partition, which is a reason to prefer it as *policy* and not
  evidence about what the text meant.

---

## Part 2 — did the repair actually repair it? (largely yes)

- **The false mechanism sentence is gone from the places that matter and what
  replaced it is true.** `harness/check.py:565-570` (stage list) and `:570-592`
  (stage 0b) now state the three real properties, and `.memory/05-layout.md:235-249`
  matches. It does **not** over-correct: it keeps "required / visible / hashed"
  and says why the hash is worth having. Residual: m1.
- **`contract_sha256` is exactly what the repaired text says it is.**
  Proved rather than demonstrated: `sha256(fenced slb-contract block)` reproduces
  the recorded `contract_sha256` in **6/6** patterns. Rung sources are provably
  outside it.
- **Fork re-run against the repaired tree: behaviour unchanged, description
  changed** (`.temp/review017/gate-p05fork2b.log`, `.temp/review017/gate-p05fork2.json`).
  Full gate, all stages, no flags, on a p05 copy whose `safe_tuned.rs` is the
  **forbidden** `chunks_exact` variant:
  `check.py: PASS`, `complete_run=True`, `failures=[]`, `contract_sha256`
  `fb5b93c485f71a7b1711d98a…` — **byte-identical to shipped p05's**, `idiom`
  object identical — certifying `R3 − R4 = 1369.0 − 1381.0 = −12.00` /
  `8377.7 − 8435.7 = −58.00`, the retracted "safe beats unsafe", as green p05.
  The repair changed the sentence and nothing else, which is what it claimed.
- **`report.py` reads `spec.md`, not the gate record** — `read_idiom()`,
  `harness/report.py:75-97`; confirmed behaviourally (the p16 table carries the
  post-TASK_017 `required[0]` text while `results/p16-tlv-walk.json`'s provenance
  is `f473198bfcab`, 2026-08-17).
- **All six tables regenerate**, byte-identically bar one trailing newline the
  `--stdout` path adds. The committed diff is **pure addition**: +14/+16/+16/+20/
  +16/+17, **0 deletions**.
- **`check.py`'s failure-summary reprint works** — observed live in
  `.temp/review017/gate-p05fork2.log:544-552`, which prints
  `idiom FORBIDDEN chunks_exact` / `idiom FORBIDDEN a running row pointer`
  directly beneath `22 FAILURE(S)`.
- **Prominence:** the `forbidden` list is genuinely above the numbers
  (`results/tables/p16-tlv-walk.md:26-35` of 147 lines, before every `Ir`
  table). The `why` is not readable (m2). One structural caveat: the table's
  header line is the *measurement's* provenance ("Generated 2026-08-17T17:02:54Z
  … git `f473198bfcab`, working tree dirty") while the declaration beneath it is
  read at generation time. A reader can reasonably infer the declaration is as of
  that commit. It is not — p16's `required[0]` there did not exist until
  `89f6598`. This is m2's family: the declaration now has a **third** copy that
  can drift, and this one carries no stamp of its own.
- **p02's R1 carve-out — verified against the rung sources, not the prose.**
  `patterns/p02-buffer-copy/c/kernel.c:28-29` is two `(void)` casts and no fit
  check; stripping comments, the entire difference between `c/kernel.c` and
  `c/kernel_hardened.c` is those two lines against
  `if (len > dst_cap || len > src_len - (src_off + 2)) return 0;`. "R1h is R1
  plus the three-term check **and nothing else**" is exactly true.
- **p05's restored bullet — verified against all six rungs.** `nrow * ncol` is
  folded into the return in `c/kernel.c:76`, `c/kernel_hardened.c:62`,
  `safe_naive.rs:56`, `safe_tuned.rs:55`, `unsafe.rs:70`, `verus.rs:363`.
- **The duplication decision (prose + JSON, each prose section naming the block
  authoritative) was right.** The alternative — deleting the prose — would delete
  the arguments, which is where a human reads them, and m1 of TASK_016_REVIEW was
  a *dropped* bullet, i.e. evidence that moving loses content. The residual risk
  is real but now has a named owner in every file ("Edit both or neither"). The
  cost of the decision is that there are now **three** copies (prose, block,
  generated table) and only the first two are covered by the "edit both" rule.

---

## Part 3 — the numbers

- **M1's correction is right and M1 was wrong.** All eight offsets confirmed on
  **both** inputs (c-gcc/c-gcc-h +15.72, c-clang/c-clang-h +14.72, R2/R3/R4
  +14.30, R5 +13.30), all nine "moves by" values confirmed (+1.42, +1.42, +0.42,
  +0.42, −1.00, and 0 for `R3−R4`, `R2−R4`, `R1h−R1` in each compiler), from the
  committed `results/gate/p16-tlv-walk.json` against
  `patterns/p16-tlv-walk/NOTES.md` §2. **No delta changes sign.** `c-clang − R4`
  is negative under both conventions (−17 → −16.58; −37 → −36.58). The one
  status change is `R5 − R4`, 0 → −1.00, which TASK_017's own text flags and
  correctly says the R4≡R5 finding does not rest on.
- **The invariant, from git at `fd91ae7 → 89f6598`.** `md5_fn` **28/28
  unchanged**. `marginal_ir_per_call` **541/564 unchanged**; all **23** movers are
  p08 (12 input cells, 11 derived `d_ir_d_work` slopes); max |Δ| = **0.08**
  (`p08 unsafe/O0/whole/large.bin`, 206209.54 → 206209.62). Zero movers in p01,
  p02, p05, p16, p17.
- **`contract_sha256` moved 6/6, not 4/6** — because the m2 fix rewrites all six
  `why` strings, including p01's and p08's. TASK_017.md predicted four; the
  engineer's `.temp/p17fix/NOTES.md` predicted and recorded six. **The task
  file's prediction was the error, not the work.**
- **`harness/` diff: 124+/10−** (check.py 50+/10−, report.py 74+/0−). The 10
  deletions are in-place docstring rewrites plus the `idiom_lines` signature
  change; the `why` block is re-added verbatim under `if why:` with the default
  preserving prior behaviour at existing call sites. No capability removed.
- **The env-block finding reproduces exactly, and I demonstrated the
  attribution rather than inferring it.** Same binary
  (`md5 0067f79ac6079df97a95d8460ea660f0`), same probe inputs, only the env
  block's length changed: **7292.26 / 7292.24 / 7292.14** at PAD 0/200/400 —
  identical to the engineer's three figures to the hundredth.
  **Mechanism, at symbol granularity:** between PAD 36 and PAD 40 (where the
  marginal steps 7292.26 → 7292.30), `callgrind_annotate` gives
  `unsafe::main` = 298,485 / 596,685 and the **memset** at libc+0x189480
  (`vmovdqu %ymm0` broadcast, no source pointer) = 411,337 / 822,637 —
  **bit-identical in both runs** — while the **memmove** at libc+0x188a80
  (`mov (%rsi),%cl`, `movzwl -0x2(%rsi,%rdx,1)`) goes 36,921→56,617 vs
  36,931→56,631, i.e. **196.96 → 197.00 Ir/iteration**. 100% of the drift is
  inside the memmove. The engineer's glibc-bulk-routine attribution is
  **confirmed and now demonstrated**.
  Two refinements: the effect is **not periodic and not monotone** over PAD 0-64
  — pads 4…36 give byte-identical whole-program totals and pads 40…64 give a
  second value; and the spread is larger than stated (m3).
  **It threatens no published p08 number.** The tightest is `R1h − R1 = 0.00`,
  and I attacked it directly: `c-gcc-O3-whole` and `c-gcc-h-O3-whole` both
  measure **4857.72** on `small`, and each is invariant across 8 and 4
  respectively differing argv path lengths (which shift the stack the same way
  the env block does, and which differ by 2 characters between those two cells in
  every real gate run). Difference exactly 0.00 in every configuration measured.

---

## Part 4 — clean negatives (named so nobody re-runs them)

1. **"A shipped p16 rung does not literally contain the tokens, so the token
   reading puts a shipped cell out of contract."** False. All six contain
   `end - p >= 3`; all but `c/kernel.c` contain `vlen > end - (p + 3)`, and
   `required[3]` carves R1 out for exactly that. Both readings really are true of
   the shipped tree; no experiment decides Part 1, as the task says.
2. **"TASK_017 moved a measured column."** It did not — 28/28 and 541/564 from
   git, all movers p08, max 0.08, and the 12 p08 input cells are the environment
   effect I reproduced independently.
3. **"The corrected p16 offset table is wrong / M1 was right about the sign."**
   The correction is exact on all 8 offsets × 2 inputs and all 9 deltas.
   TASK_016_REVIEW M1's "the sign flips" is refuted.
4. **"`report.py` reads the gate record."** It reads `spec.md`
   (`harness/report.py:75-97`), verified by code and behaviour.
5. **"The table regeneration is not reproducible / not a pure addition."** Six
   tables regenerate byte-identically (one trailing newline aside); +99/−0 total.
6. **"The empty-`forbidden` branch in `report.py` is wrong."** It is correct and
   unreachable — no shipped pattern has an empty `forbidden`, as TASK_016_REVIEW
   m3 already noted.
7. **"p02's carve-out or p05's restored bullet is true only of the prose."**
   Both verified against the six rung sources of each pattern.
8. **"`contract_sha256` does not really cover the declaration."** It does: the
   sha256 of the fenced block reproduces the recorded value in 6/6.
9. **"The repair changed gate behaviour on a forbidden respelling."** It did not:
   PASS / `complete_run=True` / `failures=[]` / identical `contract_sha256` and
   `idiom` object, re-run in full against the repaired tree.
10. **"The new check.py wording over-corrects into 'the key is useless'."** It
    does not — three concrete properties are claimed and all three are true.
    `report.py`'s generated caveat ("a claim about intent that a reader must
    check against the rung sources, not a verified property of the numbers
    below") is accurate, not defeatist.
11. **"The p08 env drift is inferred, not demonstrated."** Demonstrated at
    symbol granularity (Part 3).
12. **"The p08 env drift threatens `R1h − R1 = 0.00`."** It does not; measured
    0.00 in 12 configurations.
13. **"p16's `required[1]`/`[2]`/`[3]` are false of some rung."** Checked; they
    hold, and `required[3]` carves R1 out correctly.
14. **"TASK_017 broke the six patterns' `idiom` schema."** All six still parse
    with exactly `{required, forbidden, why}` and stage 0b passes.

---

## Not done

- I did not re-run the six shipped gates. `results/gate/*.json` is byte-identical
  between `89f6598` and `HEAD`, and the invariant was checked from git rather
  than by re-measurement; p08's cells would not have reproduced anyway, which is
  Part 3's own finding.
- I did not re-measure p01/p02 (out of scope) and landed no cell swap.
- I did not attempt to decide **which** reading p16 should adopt going forward.
  B1 says one standard must cover p16 and p17; picking it is a design act and
  belongs to a task, not to a review.
