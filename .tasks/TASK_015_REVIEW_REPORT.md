# TASK_015_REVIEW — report

**(a) Is R4′ a fair unsafe rung?** As an unsafe *spelling*, **yes** — it does the
same work, it is not tuned to win, and it is if anything *under*-tuned (I found
two cheaper unsafe spellings). As **p05's R4, no**: `spec.md:69-73` forbids the
running pointer *and* `chunks_exact` in every rung, so +11.00 is a number for a
kernel p05's own contract excludes.

**(b) Which reporting policy:** **(3) a declared canonical idiom per pattern —
moved out of prose and into the hashed `slb-contract` block — with a mandatory
measured "spelling spread" appendix per rung that is published but never
headlined**; (1) is undecidable (my measurement shows "same idiom" has no fixed
point) and (2) cannot produce a safety number at all (see Part 2).

---

## Blocker

### B1 — "+11.00 Ir/call, flat in `nrow`, `O(1)` and not `O(nrow)`" is refuted by one more unsafe round: it becomes `nrow + 9`

`patterns/p05-index-flatten/NOTES.md:1047-1054`, `README.md:117-123`,
`.memory/01-ladder.md:529-537`, `RECAP.md:148-151`,
`.memory/06-catalogue.md:76-78`.

The **+11.00 itself reproduces perfectly** — see the clean negatives, I swept it
and it did not move. What does not survive is the conclusion drawn from it.
`unsafe_consume.rs` still carries **two** induction variables per row: the row
pointer *and* the `i < nrow` counter. Dropping the counter for the canonical C
test `while rp < end` — ten lines, `.temp/review015/v05/u2_end.rs` — removes
exactly one instruction from the row-loop head, and the gap reopens as `O(nrow)`.

Marginal `Ir`/call, `-O3 isolated`, callgrind `n_iters` 100→200, my own rebuild
(bit-identical `md5_raw` to the engineer's binaries and to the shipped cells):

| cell | small 19×26 | large 65×61 | `−` R4″ |
|---|---:|---:|---|
| R3′ `chunks_exact` | 1369.00 | 8377.70 | `nrow + 13` |
| R3″ `split_at_checked` (mine, no `div`) | **1365.00** | **8373.70** | **`nrow + 9`** |
| R4′ `unsafe_consume` (the audit's control) | 1358.00 | 8366.70 | `nrow + 2` |
| **R4″ `while rp < end`** (mine) | **1337.00** | **8299.70** | 0 |
| R4‴ `from_raw_parts` mirror (mine) | **1337.00** | **8299.70** | 0 |

Swept over **all 144 committed p05 sweep blobs** (three `nrow` bands × eight
`ncol` residues, ≥2 full cycles of the modulus-8 residue in each band), the
differences are *exact constants* with zero residual:

```
R3′  − R4′  = 11.00   on all 144 points, every residue, every nrow   (reproduced)
R3″  − R4′  =  7.00   on all 144 points
R4′  − R4″  = nrow + 2   (19→21, 41→43, 65→67)      ← O(nrow), and it is the counter
R3″  − R4″  = nrow + 9   (19→28, 41→50, 65→74)      ← THE GAP REOPENS
R4″  − R4‴  =  0.00   on all 144 points
```

**Mechanism, from the listings** (`.temp/review015/asm-*.txt`), row-loop head:

```
R4′ (unsafe_consume:36-38)   add %r9,%rdi ; inc %rdx ; cmp %rsi,%rdx ; je      = 9 insns
R4″ (u2_end:34-36)           add %r9,%rdi ;            cmp %rax,%rdi ; jae     = 8 insns
R3″ (t2_splitchk:41-49)      add %rdx,%rdi ; sub %rdx,%rsi ; cmp %rsi,%rdx ; ja = 9 insns
```

This is *the same mechanism the audit itself named* — "R4 maintains two row
bases, `chunks_exact` one; that single `add` per row **is** the `−1·nrow` slope"
(`NOTES.md:995-998`). The audit applied it once on the unsafe side and stopped.
Applied once more it finds another instruction per row, and it is the *safe*
rung that is then stuck with two updates, because a safe cursor is a fat pointer:
there is no `end` pointer in safe Rust, so the remaining length must be
maintained (`sub %rdx,%rsi`) *and* tested. That is a better finding than +11 —
it is a named, structural, per-row safe-Rust cost — but it is the opposite
conclusion.

**Concrete failure scenario.** The README states, as p05's headline safety
number, *"idiom-matched, safety costs eleven instructions per call on a
vectorised 2-D fold, `O(1)` and not `O(nrow)`."* A reader writes the most
obvious unsafe spelling in existence — the C `for (p = base; p < end; p += ncol)`
loop — and measures `nrow + 9`. The `O(1)`-vs-`O(nrow)` conclusion, which is the
whole point of the sentence, flips on the first thing anyone tries. Note that
R4‴, built by taking the *safe* R3′ program and replacing only its two checked
slice constructions with unchecked ones — the most idiom-matched unsafe rung it
is possible to write — lands on the identical 1337.00, so 1337 is not an exotic
tuning; two independent unsafe spellings converge on it.

**Direct answer to the question the task most wanted:** **the gap does not
converge.** One more round on each side moved it from `+11` (O(1)) to `nrow + 9`
(O(nrow)), and the sign of the headline conclusion moved with it. The assumption
in `TASK_015_REVIEW.md:134-136` ("I have assumed one more round of chasing
settles it") is wrong, and it is wrong in the direction that matters.

There is also an **a priori** half, which is why no amount of further chasing
will settle it either. `.memory/01-ladder.md:12` defines R4 by what it is
*permitted* to use ("whatever it takes to reach C's codegen"), not by what it
must use. Every safe program is therefore an admissible R4. So
`inf(R4) ≤ inf(R3)` **by construction**: "safe Rust beats unsafe Rust" can never
be a language fact under these definitions, and the audit's central negative
result was available without measuring anything. What is *not* available a priori
is whether the infimum gap is 0 or positive — and that is precisely the quantity
that moved from 11 to `nrow + 9` when I looked.

### B2 — both R3′ and R4′ are excluded by p05's own contract, and two consecutive tasks measured them as p05

`patterns/p05-index-flatten/spec.md:69-73`, introduced at `a02d282` (TASK_013)
and **never edited since**:

> ### Load-bearing, do not "improve"
> - **`i*ncol + j` stays as written, in every rung.** Do not strength-reduce it
>   to a running pointer and do not use `chunks_exact` — either deletes the
>   pattern. R3 reslices `[base .. base+ncol]` … and that is the most a rung may
>   do.

and `spec.md:3-4`: *"Every rung implements exactly this. If a rung deviates, it
is a different benchmark and **its numbers are not comparable**."*

`chunks_exact` is named and forbidden; the running pointer is named and
forbidden. TASK_014_REVIEW's B1 measured the first, TASK_015 measured the second,
and **neither cites `spec.md` once**. `safe_tuned.rs:10-14` carries the same
warning in the pattern's own source — *"`chunks_exact(ncol)` … is deliberately
*not* used: it would delete the flattened index `i * ncol + j`, which is the
pattern"* — and both tasks walked past it.

The root cause is a live contradiction between two authoritative files:
`.memory/01-ladder.md:11` **names `chunks_exact` in the R3 definition itself**,
p05's `spec.md:70-73` forbids it. B1 quoted the former as licence
(`TASK_014_REVIEW_REPORT.md:36-38`). Nothing in the tree resolves the conflict,
and the gate cannot: the pin is prose at line 69, the hashed `slb-contract` block
starts at line 309, so `contract_sha256` is blind to it.

**Failure scenario.** The writeup publishes "p05's honest safety number is +11"
and a reader checks it against `spec.md`, which says in the second sentence that
a rung which strength-reduces the index is *a different benchmark whose numbers
are not comparable*. Both rungs in the +11 pair did exactly that. The number is
real; the label "p05" is not. This is the same class of defect as the three
retractions the corollary rule already documents — a measurement attached to the
wrong subject — arriving one level up.

Note what this does **not** do: it does not rescue the retracted "R3 is not
free". The shipped, contract-conformant R3 really does pay `6·nrow + 9`, and
whether that is "what safe Rust costs" is exactly what the spelling spread makes
unanswerable. It also **independently confirms the engineer's decision not to
swap p05's R3**, for a stronger reason than the four given: the replacement was
out of contract.

---

## Major

### M1 — p16's `nrec + 3` is a three-point fit across two residue classes and is wrong; swept, it is `O(nrec)` in three residue classes out of four

`.memory/01-ladder.md:534`, `RECAP.md:150`, `.memory/06-catalogue.md:78`.

p16 ships 68 sweep blobs and the audit used none of them. I ran all 68 against
shipped R3, shipped R4, `v16-tuned_split` (R3′) and `v16-unsafe_consume` (R4′)
(`.temp/review015/sweep16.log`):

| band | `nrec` | `vlen ≡ 0 (mod 4)` | `vlen ≢ 0 (mod 4)` |
|---|---:|---:|---:|
| v56 … v89 | 4 | **R3′ − R4′ = 7.00** | **11.00** |
| v2040 … v2073 | 2 | **7.00** | **9.00** |

So the measured law is `7` flat at residue 0 and **`7 + nrec`** otherwise — not
`nrec + 3`, which predicts 5 at `nrec = 2` and measures 7. Both of the audit's
`nrec = 4` points sit at residue 0, where the law is flat and the slope is
invisible; its third point (`large`) sits at residue 2, where the slope is 1 per
record. `7 + nrec` fits all three of the audit's own points once `large`'s record
count is taken as the 10 its own table records (`.temp/p05r3/NOTES.md:34`)
rather than the 14 its fit requires (`:93`) — an internal contradiction in the
audit's notes.

The controls reproduce exactly, so this is not a method disagreement:
`R3ship − R4 = 7 + 5·nrec` / `7 + 7·nrec` (the published p16 law) and
`R3′ − R4 = −(5·nrec + 2)` / `−(3·nrec + 2)` both hold on all 68 points.

**Failure scenario, and it is the same one as B1:** the amendment's two
supporting numbers are p05's "+11 flat, O(1)" and p16's "`nrec + 3`". Both are
offered as evidence that idiom-matched safety is O(1) per call. On p16 that is
false in three of four residue classes **without any extra spelling round at
all** — just by running the sweep the pattern already ships and
`.memory/01-ladder.md:210-213` already mandates ("Sweep, do not sample").

### M2 — p17's `−19.00` is not independent of `nsuf`; and the *published* "+32 Ir/call flat" is not either

`.memory/06-catalogue.md:76` (`51` flat), `.temp/p05r3/NOTES.md:50-51`, and —
this is the one that is already through review —
`.memory/01-ladder.md:437`: *"**Perf — R3 is free for the fifth pattern in a
row** (+32 Ir/call flat, 0 per byte …)"*.

p17 ships no sweep, so I generated eight inputs varying `nsuf` 1…8 at a fixed
body (`.temp/review015/gen17.py`, written under `.temp/` only; all four rungs
print identical checksums on all eight):

| `nsuf` | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `R3ship − R3′` | 17 | 34 | **51** | 68 | 85 | 102 | 119 | 136 |
| `R3′ − R4` | +1 | −11 | **−21** | −31 | −41 | −53 | −63 | −73 |
| `R3ship − R4` | 18 | 23 | **30** | 37 | 44 | 49 | 56 | 63 |

`R3ship − R3′ = 17·nsuf` **exactly**, zero intercept, zero residual over eight
points. The catalogue's "`51` flat on p17" is `17 × 3`. `R3′ − R4` is roughly
`−10·nsuf + 9`; the audit's "−19.00 flat, both bands" is one point of that line,
measured twice at the same `nsuf`. And `R3ship − R4` runs 18→63, so p17's
*shipped, reviewed, published* R3 number is `≈ 7·nsuf + 9`, not a per-call
constant: "flat" there is flat **in bytes folded**, which the two shipped bands
(8× apart in body size, both `nsuf = 3`) do establish, and it was written as
though it were flat per call, which they cannot establish at all.

Caveat, stated because it bounds the claim: my inputs are not the shipped ones
(different suffix values and body length), so the absolute figures are not
directly comparable — at `nsuf = 3` I get +30/−21 against the shipped +32/−19.
The **`nsuf` dependence** is what is established, and it is unambiguous.

**Failure scenario.** A reader takes "p17: safe Rust's tuned rung is free, +32
instructions per call, flat" and applies it to a server handling a request with
20 ranges. The real figure is ≈ +150, and it scales.

### M3 — the `div`'s *timing* consequence does not reproduce, and a fourth safe spelling deletes the `div` while being cheaper still

`.memory/03-measurement.md` (new "Callgrind prices a hardware `div` at 1 `Ir`"
section), `patterns/p05-index-flatten/NOTES.md:1056-1084`,
`README.md:121-123`.

The `div` **is real** — I confirmed it directly in the listing,
`.temp/review015/asm-tuned_chunks.txt:28-32`,
`mov %r8d,%eax ; xor %edx,%edx ; div %r11d ; mov %r8,%rax ; sub %rdx,%rax`, once
per call. Two things attached to it do not hold.

1. **The attribution of the spread to the `div` does not reproduce.** Two
   independent 31-rep interleaved runs, `taskset -c 3`, differenced 25 000→75 000
   on `small`, same protocol as the audit:

   | cell | run 1 min / med / spread | run 2 min / med / spread |
   |---|---|---|
   | R4 shipped | 83.53 / 87.27 / 4.48% | 86.97 / 88.87 / 2.19% |
   | R3′ `chunks_exact` (**has the `div`**) | 84.95 / 88.65 / 4.35% | 84.90 / 86.05 / **1.36%** |
   | R3″ `split_at_checked` (no `div`) | 84.74 / 84.86 / 0.14% | 84.06 / 86.59 / 3.01% |
   | R4′ `unsafe_consume` (no `div`) | 82.86 / 88.75 / **7.11%** | 86.69 / 86.35 / −0.39% |
   | R4″ `rp < end` (no `div`) | 84.65 / 84.63 / −0.03% | 84.50 / 86.55 / 2.42% |

   The audit's "8.61% min-to-median spread, the worst of the five and the only
   one near the discard threshold, which is what a variable-latency `div` looks
   like" does not survive: in my run 1 the worst spread belongs to
   `unsafe_consume`, which contains **no `div` at all**, and in run 2 the
   `div`-bearing cell has the *second lowest* spread. Between-run drift on the
   same cell is ~4%, larger than every inter-cell `Ir` difference in the table
   (0.8–3.3%). The ordering of the five cells is different in the two runs. So
   the specific numbers `+0.47%` and `8.61%` are below this box's reproducible
   floor and should not be in `.memory/`.

2. **The `div` is a property of one spelling, not of the consumed-slice idiom.**
   `split_at_checked` (`.temp/review015/v05/t2_splitchk.rs`) consumes the slice
   with no division at all and is **4 Ir cheaper than `chunks_exact` on every one
   of the 144 sweep points**. So "the consumed-slice safe spelling's win is
   instruction-count-only because of a `div`" is false as a general statement;
   it is true of `chunks_exact(runtime_n)` specifically.

   The *rule* the memory section draws — "a spelling whose win is one instruction
   wide needs a wall-clock column" and "a constant chunk size is a different
   measurement from a runtime one" — is right and should stay. The evidence
   offered for it should be the listing (which holds) and not the ns table (which
   does not).

### M4 — `.memory/06-catalogue.md:75` mislabels p05's `R3ship − R3′`

It says `R3ship − R3′ = 6·nrow + 9` on p05. `6·nrow + 9` is `R3ship − R4`
(123 / 255 / 399 at nrow 19 / 41 / 65 — I reproduced it on all 144 points).
`R3ship − R3′` is **`7·nrow + 2`** (135 at nrow 19, 289 at 41, 457 at 65). The
p16 (`10·nrec + 9`) and p17 (`51`, see M2) entries in the same sentence are
`R3ship − R3′`; the p05 one is a different quantity wearing the same label.

---

## Minor

### m1 — the safe/unsafe *spread* is now the whole story and no file states it at full width

Seven safe and four unsafe spellings of one kernel, `small` 19×26, marginal
`Ir`/call, all with **0/150 checksum mismatches against the shipped R4 binary**:

| safe | Ir | unsafe | Ir |
|---|---:|---|---:|
| R2 indexed (shipped) | 2081.00 | R4 `get_unchecked` flat index (shipped) | 1381.00 |
| R3 hand-reslice (shipped) | 1504.00 | R4′ row pointer + counter | 1358.00 |
| index cursor into `data` | 1446.00 | R4″ `rp < end` | **1337.00** |
| `split_at` | 1407.00 | R4‴ `from_raw_parts` mirror | **1337.00** |
| `ChunksExact::fold` | 1388.00 | | |
| `chunks_exact` for-loop | 1369.00 | | |
| `split_at_checked` while-let | **1365.00** | | |

Safe spread **716 Ir (52%)**, unsafe spread **44 Ir (3.3%)**, best matched pair
**28 Ir (2.1%)**. `.memory/01-ladder.md:130-135` quotes four safe spellings; the
spread is wider than that, and the asymmetry between the two columns (the safe
side is far more spelling-sensitive than the unsafe side) is itself the
publishable result.

### m2 — p05's `NOTES.md` §12c calls `unsafe_consume.rs` "shipped R4 verbatim except…"

`NOTES.md:1037-1039`. It is verbatim except for the one thing `spec.md:70-73`
forbids. The sentence is true and the omission is the whole of B2.

---

## Part 2 — the recommendation, argued

**Recommend (3), with two amendments that answer its stated objection.**

**Why not (1), idiom-matched pairs.** It needs a definition of "same idiom" a
gate can check, and my measurement shows the concept has **no fixed point**.
R3′ and R4′ *were* idiom-matched under the audit's own criterion ("consume the
slice / carry a row base rather than re-derive it"). R4″ satisfies that criterion
too, and is `nrow + 2` cheaper. R4‴ satisfies it in the strongest possible sense
— it is the safe program with only its checked slice constructions replaced —
and lands on the same number as R4″. So "same idiom" does not pick out one
program per rung; it picks out an equivalence class whose members differ by
`O(nrow)`. A rule that cannot decide between R4′ and R4″ cannot be the reporting
rule, and no gate check can make that decision either.

**Why not (2), a published spread.** Two reasons, the second decisive.
The readability objection is real and worse than feared — p05 alone is now
7 safe × 4 unsafe spellings. But the fatal one is that **a spread cannot express
a safety cost at all.** Because R4 is defined by permission and not by
obligation, every safe program is an admissible unsafe program, so
`inf(R4) ≤ inf(R3)` by construction and the two intervals *always* overlap with
the unsafe one extending lower. Publishing `R3 ∈ [1365, 2081]`,
`R4 ∈ [1337, 1381]` tells a reader nothing about safety; it tells them that one
interval contains the other's floor, which is a theorem, not a measurement. The
only quantity that can carry a safety claim is a **matched-pair delta**, and a
matched pair requires a declared idiom. (2) therefore presupposes (3).

**Why (3), and why the self-certification objection does not bite.**
`.memory/02-bench-rules.md` warns that a declared-and-then-measured idiom is
self-certifying. It is — and this project has now run the experiment. p05 already
implements (3): `spec.md:69-73` declared, in TASK_013, **before any of these
spellings were measured**, that `chunks_exact` and a running row pointer delete
the pattern. Two later tasks measured exactly those two things and reported them
as p05's numbers, and **the declaration turned out to be right both times**:
`chunks_exact` does delete the multiply, the running pointer does delete it on
the unsafe side, and the "+11" they produce is a number for a different kernel.
The self-certification risk is answered by the ordering the project already uses
for `requires`/`ensures`: the author declares *before* measuring, the declaration
is hashed, and a different agent attacks it. What failed here was not
self-certification — it was that the declaration was **invisible**.

Hence the two amendments:

1. **Move the idiom declaration into the hashed `slb-contract` block.** A new
   required key, e.g.
   `"idiom": {"required": ["i*ncol + j written out, every rung"], "forbidden": ["chunks_exact", "strength-reduced running row pointer"], "why": "…"}`.
   The gate cannot semantically check "is this the declared idiom" and should not
   try (`.memory/02-bench-rules.md`'s "could this happen by accident?" test says
   no). It only has to (a) require the key to be present and non-empty and
   (b) hash it — which it already does for the whole block. Then a task that
   wants to change a rung's idiom must move `contract_sha256`, which is exactly
   the signal review already knows how to read, and the failure mode of the last
   two tasks — measuring an excluded spelling and never noticing — becomes
   impossible to land silently.
2. **Require a "spelling spread" section in every pattern's `NOTES.md`**: at
   least two alternate spellings per rung, measured, with the contract-conformant
   cell marked, and an explicit "not the headline" note. Publish the spread as a
   *result about method*; publish the matched pair as the *number*. This keeps
   (2)'s honesty without (2)'s unreadability and without its impossibility.

**Retrofit cost across the six patterns.** Small, and it is almost entirely
prose. p05 (`spec.md:69-73`) and p17 (`spec.md:125-146`) already have the text
and only need it moved into the JSON block. p01, p02, p08 and p16 need one
paragraph each naming what their R2/R3/R4 do and what would delete the pattern
(p02's is already written in the retraction — the `memcpy` idiom; p16's is the
byte fold's unroll; p08's is the `memmove` spelling). **No cell source changes,
so no measured column can move** — but `contract_sha256` moves in all six, so all
six gates must be re-run and `results/gate/*.json` refreshed: on the observed
times (p05 1 m 24 s, p08 2 m 23 s) that is roughly 12–15 minutes of machine time
for the set. The spelling-spread sections are new writing per pattern; p05 has
11 spellings measured already (this review plus the audit), p16 has 5, p17 has 3.

**This recommendation implies no cell swap** — the opposite. p05's shipped
`safe_tuned.rs` is the contract-conformant R3 and must stay, and `chunks_exact`
must not be landed as a p05 cell at all, only as an out-of-contract control
labelled as such. So: recommended, and stopping here as instructed.

---

## Part 4 — did the corrections land correctly?

Verified, and they did. Specifics:

- **Gate records are consistent with the tree.** All 23 `source_sha256` entries
  in `results/gate/p05-index-flatten.json` and all 23 in
  `results/gate/p08-overlap-move.json` match the files byte for byte, recomputed
  independently. `contract_sha256` is identical to `11046ad`'s in both
  (`0b33d336…` / `29d348a1…`), so no `spec.md` pin moved. Both records read
  `verdict PASS, complete_run True, failures []`. `git status` clean.
- **Nothing refuted survives unstruck.** Every occurrence in the tree of "R3 is
  not free" or "price of the optimiser failing the lemma" is inside `~~…~~` with
  a retraction note: `README.md:81`, `README.md:109`, `NOTES.md:44`,
  `NOTES.md:75-77`, `RECAP.md:120`, `RECAP.md:201-202`. Grepped, not recalled.
- **p08's "full arc" row does not overcorrect.** `README.md:26-31` now reads
  *"yes — and the verifier does not see it. The **caller's** obligation is
  discharged; the trusted body is trusted"* with cost *"the proof moves the bug
  into the TCB, it does not remove it"*. That is the right claim and it does not
  imply R5 is worthless.
- **The four repointed cross-references point where they should.**
  `verus.rs:39` → §6a (which does carry the clause-count decision),
  `verus.rs:40,53-54` → §6a and §8(b) (§8's SLB-TRUSTED-ARGUMENT (b) now says
  the three clauses partition `old(v)@.len()` and that the contract is "complete
  only relative to one caller"), `verus.rs:81` → §8 (the TCB tally),
  `model.py:257` → §9 (which does carry the `Ir`-floor margin, "tightest margin
  26.9×"). The §4a ns correction is in place at `NOTES.md:433-442` with the
  0.37% floor quoted beside the 1.29%.
- **The fifth dangling reference is the only one.** I checked every
  `NOTES.md <n>` reference in `patterns/` (65 of them,
  `.temp/review015/xref.py`) against the actual section headings of each
  pattern's own `NOTES.md`: **no reference names a section that does not exist**.
  `p08/spec.md:383`'s "NOTES.md 7" is therefore not *dangling* — §7 exists — it
  is *mis-targeted* (the floor margin is §9), which no mechanical check can find.
  Confirmed as the only known one; it is inside the hashed block and correctly
  left alone.

---

## Part 5 — clean negatives (named attacks that did **not** land; do not re-run)

1. **"+11.00 is flat in `nrow` but moves with `ncol` residue."** No. Swept all
   **144** committed p05 sweep blobs — three `nrow` bands, all eight residues
   mod 8, ≥2 full cycles per band — `R3′ − R4′ = 11.00` on **every single
   point**, min = max = mean. The strongest single result in this review and it
   goes the engineer's way. `.temp/review015/sweep-sweep.json`.
2. **"R4′ is tuned to win / does different work / was only checked against
   itself."** No on all three. Same trip counts (`while i < nrow`,
   `while j < ncol`), same addresses, the `nrow*ncol` fold retained; **0/150
   mismatches in stdout and exit against the *shipped* R4 binary**
   `.temp/build/p05/unsafe-O3-isolated`, on all 150 committed inputs. And it is
   *under*-tuned, not over-tuned: two cheaper unsafe spellings exist (B1).
3. **"The `div` defect contaminates p16's and p17's beating spellings too, so
   all three 'cheaper' results are artefacts."** No. Zero `div`/`idiv` in
   `v16-tuned_split`, `v16-tuned_splitat`, `v17-tuned_suffix`,
   `v16-unsafe_consume` and both patterns' shipped `safe_tuned` kernels. p16's
   beater uses `split_first_chunk::<3>()` (const) and p17's `chunks_exact(2)`
   (const 2 → mask, not division). The defect is p05-specific and follows from
   the **runtime** chunk size.
4. **"The landed corrections did not really land / the gate record is stale."**
   No — 23/23 `source_sha256` match in both patterns, `contract_sha256`
   unchanged, both PASS/complete. See Part 4.
5. **"Some refuted p05 claim survives somewhere in the tree."** No. Grepped;
   all six occurrences are struck through with a retraction note.
6. **"p08's README overcorrected into implying R5 is worthless."** No — it says
   the caller's obligation *is* discharged and the bug moves into the TCB.
7. **"Safe Rust can chase back to parity with R4″."** Not with the two further
   spellings I tried, and both are recorded so nobody repeats them:
   `Iterator::fold` over `ChunksExact` measures **1388.00** (worse than the
   `split_at_checked` 1365.00) and a single-induction-variable index cursor into
   `data` measures **1446.00**. The safe floor stayed at 1365.00 across seven
   spellings. The mechanism (a safe cursor is a fat pointer and must maintain
   the length) suggests, but does not prove, that the one instruction per row is
   structural.
8. **Extending the engineer's `split_at`/`split_first_chunk` negative.** The
   same phenomenon appears on p05's *unsafe* side and is stronger there: R4″
   (`rp < end`) and R4‴ (`from_raw_parts` per row) have **identical marginal
   `Ir` on all 144 sweep points and identical static counts (91 / 75 / 79)** but
   **different `md5_fn`** (`f8636e24…` vs `61ecbe22…`) and different `md5_norm`.
   So the engineer's conclusion generalises: what does the work is consuming a
   cursor, and two textually unrelated programs that do it converge on the same
   machine-code *shape* without converging on the same bytes.
9. **"My rebuild does not reproduce the engineer's binaries."** It does, exactly:
   `md5_raw` for `tuned_chunks` (`31988fe2…`) and `unsafe_consume`
   (`c411416d…`) are bit-identical to `.temp/p05r3/bin/`, and my rebuilds of
   `safe_tuned.rs`/`unsafe.rs` are bit-identical to `.temp/build/p05/`. Build
   reproducibility is not a source of any disagreement here.

---

## What I did not do

- Did not modify `harness/`, `pilot/`, `.memory/` or `patterns/`; not a
  gate-bypass hunt; no cell swap landed; `git status` clean at exit; nothing
  written under `results/`.
- Did not re-run `harness/check.py` on any pattern (nothing in the tree changed;
  I verified the existing records against the tree instead).
- Did not build any variant at `O0` or in `whole` mode, and did not measure
  static identity of R4″/R4‴ against anything but each other.
- Did not re-measure p01 or p02, per scope.
- Did not establish that the safe side's one-instruction-per-row deficit is
  *irreducible* — seven spellings is evidence, not a proof, and I have a
  mechanism (fat-pointer cursor) but no counterfactual that closes it.
- p17's `nsuf` sweep uses inputs I generated under `.temp/`, not shipped ones, so
  M2 establishes the **`nsuf` dependence** and not the shipped absolute figures.
  Landing a shipped p17 `nsuf` sweep is its own task.
