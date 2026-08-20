# The ladder — five rungs, precisely defined

Every pattern is implemented five times. The rungs must be **semantically
equivalent on well-formed input** (same checksum) and differ only in what
enforces memory safety.

| Rung | Dir/file stem | Definition |
|---|---|---|
| **R1 C** | `c/` | Idiomatic C99. No bounds checks. Written the way a competent systems programmer writes it — *including* the bug class the pattern is about, if the pattern models one. |
| **R2 safe-naive** | `safe_naive.rs` | The mechanical port a working Rust programmer writes first: `for i in 0..n { ... v[i] ... }`, indexing, `Vec`, no cleverness. Must contain **zero** `unsafe`. |
| **R3 safe-tuned** | `safe_tuned.rs` | Same semantics, rewritten to help LLVM elide checks: iterators, `chunks_exact`, `zip`, slice reslicing, `split_at`, hoisted length assertions. Still **zero** `unsafe`. **Subject to the pattern's declared idiom** — see below. |
| **R4 unsafe** | `unsafe.rs` | `get_unchecked`, raw pointers, `from_raw_parts` — whatever it takes to reach C's codegen. Unsound-by-inspection is not allowed: it must be *correct*, just unverified. **Subject to the pattern's declared idiom** — see below. |
| **R5 verus** | `verus.rs` | R4's exec code, plus Verus specs and proofs discharging every unsafe precondition. Ships the same machine code as R4. |

**The spelling list above is permissive, and a pattern's `spec.md` overrides it.**
This was a live contradiction until TASK_015_REVIEW: this table names
`chunks_exact` as an R3 technique, while p05's `spec.md` names it as
*pattern-deleting* and says a rung that uses it "is a different benchmark and
its numbers are not comparable". **Two consecutive tasks quoted this table as
licence, measured a forbidden spelling, and reported the result as p05's number**
— the manager's own retraction of p05's headline among them. Read the pattern's
`spec.md` before treating any technique here as available.

**R4 is defined by *permission*, not obligation** — every safe program is
textually an admissible R4 — **but the consequence drawn from that for six
patterns is FALSE, measured at TASK_025_REVIEW.** The claim was
`inf(R4) <= inf(R3)` **by construction**, "a reason available without measuring".
It does not hold here, and the counterexample is this project's own gate:

> **Every one of the six patterns pins `identity: unsafe ≡ verus, O3 exact`**
> (checked, all six `results/gate/*.json`). So an R4 is not merely a program that
> *may* use `unsafe` — **it is a program that must have a byte-identical R5 twin
> that Verus verifies.** R4 is therefore constrained by what vstd can express,
> and R3 is not constrained at all. The two classes are **incomparable**, not
> nested, and the inclusion runs the *opposite* way from the one that was
> published.

Measured instance: p16's `u_c32` — the `chunks_exact(32)` fold on the unsafe side,
in contract on all four `required` entries and 95/95 equivalent — **cannot be a
p16 rung**, because `chunks_exact`, `ChunksExact`, `by_ref`, `TryFromSliceError`
and `get_unchecked` are each unsupported by vstd at the pin. Shipping it needs
**five** new trusted items on a pattern whose entire memory-safety claim is *one*
trusted `requires` (`.tasks/TASK_025_REVIEW_REPORT.md`, blocker 1, with the four
Verus logs). The *safe* rung with the identical fold needs none.

So **"safe Rust beats unsafe Rust here" is not disposed of by the definition**,
and on p16 it now has a mechanism instead: the safe class can reach spellings the
unsafe class cannot, because the unsafe class is chained to the prover. Whether
`inf(admissible R4) > inf(admissible R3)` on p16 is **open** — a hand-unrolled
32× fold with explicit indices is Verus-expressible in principle and was not
tried. See `.memory/06-catalogue.md`, which carried the same false claim.

**The rule, stated at its true width** (TASK_027_REVIEW, which validated the step
on three independent grounds — the pin names *roles* and not files, so a candidate
substituted into the role inherits it; this file's own R5 definition already says
"ships the same machine code as R4", so a candidate R4 with no verifying twin
leaves the pattern with four rungs; and the project has read the *other* key in
the same hashed block, `idiom`, as a class constraint on unshipped variants since
TASK_017):

> **A rung covered by an `identity` pin is chained to the prover.** It is not
> specific to R4 — p01 also pins `safe_naive ≡ safe_naive_verus, O3 exact`, so
> p01's **R2** candidates are chained too.

**Two qualifications, both measured, and both required before you use this to
disqualify anything:**

1. **"At the pinned vstd" is part of the claim.** Verus prints
   *"you may be able to add a Verus specification to this function with
   `assume_specification`"* on every rejection, and an upstream vstd that ships
   one costs the pattern **zero** TCB. A disqualification is a statement about
   `0.2026.08.09.92f466f`, not about Rust.
2. **Unsupported-feature disqualifies; a failed transplant does not.** Measured on
   p05 with the *same exec code* two ways: transplant plus minimal ghost tidy gave
   `11 verified, 1 errors` — *postcondition not satisfied* — while the same exec
   code with one real lemma and one `proof` block gave **`13 verified, 0 errors`**.
   So "the twin did not verify" means nothing; only `is not supported` does,
   because that is what forces a new **trusted** item. Read the error text, not the
   exit code.

**The named-spelling standard (TASK_018), and what it does and does not buy.**
Every pattern's `slb-contract` block carries an `idiom` object naming the tokens
each rung must spell literally. It is a **policy adopted after measuring**, not a
reading of what any earlier text meant, and all six carry a byte-identical
statement of it. One clause is load-bearing and was found by measurement: **a
rung spells the same operands the way its language forces, and nothing else
varies**.

**That clause was deleted at TASK_019, and the "eight shipped cells" figure
attached to it is retracted twice over.** TASK_018_REVIEW made it "10 literal, 4
whitespace-normalised"; TASK_019 audited the *whole* declaration against every
rung it scopes to and measured **20 raw / 15 comment-stripped / 9 fully
normalised violations out of 78 obligations** — then repaired the declarations to
**0 of 82**, measured, not asserted.

Two violation classes nobody had counted, and both are about the **ruler**, not
the code:

- **p17's `required[1]` backticked an ellipsis** — `if start < end && start >= 0
  { ... }`. No rung in any language can contain that. 5 obligations.
- **p16's `verus.rs:275` contains p16's own `forbidden[0]` literally**, as a
  *ghost loop invariant*. The grep that is supposed to settle admission **fires
  on a shipped cell of the pattern the previous review had called decidable** —
  because the pin has no notion of which code *runs*.

**Comment-stripping is load-bearing, and was unstated until TASK_019 defined the
matching rule** (`check.spelling_matches`: blank comments and string literals,
blank Verus ghost clauses, then delete all whitespace). Two hardened-C files
quote their own `forbidden` spelling *inside the comment explaining why they do
not use it*, and p17's C rung matched `2 + 2*nsuf > len` on raw text **only
because a comment spells it that way** while the code writes the spaced form — a
match for the wrong reason.

The resolution: `required`/`forbidden` entries may be **per-language objects**,
so a check whose operands are `src_len` in C and `src.len()` in Rust can be named
honestly. It **narrows** rather than loosening — 78 → 82 obligations, and on p02
the pin decided 0 of 3 variants before and 3 of 3 after.

- It does **not** buy attributability. On p17 the excluded spelling and an
  admissible one compile to the **same 478 bytes**, so the exclusion moves no
  number; on p16 the in-contract class **spans 42** of the 77 Ir/call at `large`,
  of which **32 is removable** by an admissible respelling.
- It was argued to buy **decidability** — the semantic alternative cannot settle
  a variant that satisfies "every comparison is subtraction-first" *vacuously* by
  having no comparison. **That is refuted on p02**, where the grep the standard
  says settles admission excludes four *shipped* cells, so the pin is not
  decidable-and-correct simultaneously. What survives as the justification is the
  narrow one in `check.py`: the declaration is **required, visible and hashed**.
- "Pin nothing and report the spread" fails differently: with no pin the spread
  has no boundary on either side. (This bullet used to add "and
  `inf(R4) <= inf(R3)` makes it unbounded below on both sides" — **withdrawn**,
  that inclusion is refuted; see the R4-by-permission paragraph above. The
  boundlessness stands on its own without it.) The pin is what makes the spread
  finite and searchable.

**So: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR — and
therefore `R3ship − R4ship` is an upper bound on the in-contract safety tax
ONLY WHILE ONE RUNG IS HELD FIXED.** **Replaced in all six `idiom.why` at
TASK_023** with the one-sided form; the sentence survived *outside* the hashed
blocks in eleven further places, found by grepping.
⚠ **The reason originally given here was itself refuted** (TASK_027_REVIEW). It
was: *"with both rungs free to be respelled, p05 has an admissible pair whose tax
is exactly 0."* **That pair's R4 is `r4_dataslice`, which is not a rung** —
`from_raw_parts` is `is not supported` at the pinned vstd. See the p05 entry
below. **The qualification survives and is if anything stronger**: it holds
because nobody has yet built an admissible R4 that moves *at all*, not because a
free pairing reaches zero.

**The unpinned unroll factor is not a p16 problem.** `5 + 3/K` follows from a
declaration that licenses unrolling and an inner byte loop, so **any pattern with
an inner byte loop is exposed** — p17 and p02 both publish one-sided R3 bounds
today and are the obvious next targets. Note also what makes the safe-side lever
different in kind: `r4_hdr`'s unaligned `u16` read **cannot be a p16 rung at all**
(vstd does not support `read_unaligned`, and the `identity` pin needs R5 ≡ R4),
so it would need a **fourth trusted item** in a pattern whose whole claim rests on
one trusted `requires`. The R3-side variants cost **zero TCB** and are the larger
effect. "The same category of edit on the safe side" was the argument for
`r4_hdr`; it is measurably not the same category.

**And do not replace it with `min(R3) − min(R4)`** — that is the difference of
two upper bounds and bounds nothing in either direction.

⚠ **The instruction that used to follow — "report the in-contract PAIR INTERVAL
beside every headline" — is REVERSED (TASK_028).** There are **three distinct
quantities** and the project has confused them repeatedly, so name them:

| quantity | p05 | what it is |
|---|---|---|
| **fixed-R4 bound** | `6·nrow + 9` = 123 / 399 | **one number.** `R3ship − R4ship`, bounding `inf(in-contract R3) − R4ship`. The only sound one. |
| **R3-side span** | `5·nrow + 6 … 6·nrow + 13` = 101…127 / 331…403 | the in-contract R3 search, R4 held by fiat. Width `nrow + 7` = 26 / 72. |
| **pair interval** | *the same numbers* | both rungs free — and it **collapses onto the R3-side span**, because every admissible R4 measures exactly `R4ship`. |

So **do not publish a pair interval — not because it is unavailable, but because
it is DEGENERATE**: it duplicates the R3-side span, and its R4 endpoint has zero
measured width. (An earlier manager note said it "is identical to the fixed-R4
bound"; that is **wrong** — the fixed-R4 bound is a single number and sits
*inside* the span.) State the degeneracy rather than the absence: it is
falsifiable in one sentence, and **it stops being degenerate the day somebody
builds an admissible R4 that moves.**
⚠ **ANSWERED AT p03 (TASK_036_REVIEW). Somebody built one.** `m_clamp_unsafe` —
R4 plus a *dead* `if sp > STACK_CAP { return 0; }` — has a twin that verifies
**`9 verified, 0 errors`** with **zero new trusted items**, holds the `identity`
pin byte-for-byte (`md5_fn 40d374bfb669`, `md5_raw` equal), is in contract by the
gate's own matcher, and measures **−118 on `small` / +497 on `large`** against
`R4ship`. The **back-edge** variant (`m_clamp_unsafe_tail`, also `9/0`, identity
byte-for-byte) measures **−118 / −207**, so the R4 endpoint has *measured width*:
**2884…3002** on `small`, **8177…8881** on `large`. So p03 has a **non-degenerate
pair interval**, the first on this project, and "nobody has, on any pattern" is
retired. ⚠ Note what it is **not**: the two class minima are 5 apart on both
blobs, and that is the per-call constant, **not a tax** — `min(R3) − min(R4)`
differences two upper bounds and bounds nothing (finding 12).
**And the asymmetry is measured on the same pattern**: the *safe* side's cheapest
lever is `assert!(sp <= STACK_CAP)`, and on the unsafe side that is
`error: panic is not supported` — so the safe class reaches a spelling the unsafe
class cannot. Third measured instance of the R4-by-permission result, and the
first where the safe-side lever is a **one-line assertion**.

**How to tell a legitimate declaration edit from self-certification — the
direction test (TASK_019).** The obvious guard is *provenance*: "this edit was
forced by shipped code that predates the standard, not by a number anyone
wants." **That guard does not survive**, and the engineer who was asked to attack
it took it apart: only one of TASK_019's four repair mechanisms is about code at
all. An ellipsis in a `required` entry is a **typo in the ruler**; a ghost
invariant matching a `forbidden` entry is the pin having **no notion of what code
runs**. Three of four repairs are about how the declaration is *read*, and
provenance cannot license them. Worse, provenance is **unfalsifiable**.

**The audit is reproducible from the tree since TASK_020** — `check.idiom_audit`,
stage `0b`, reporting-only and never-failing, its count in all six gate records
and rendered by `report.py` with a **STALE** banner when `spec.md` no longer
hashes to the record. But it splits into a decidable half and an undecidable one,
and the file must not imply otherwise:

- **`forbidden` is decidable and reports a verdict: 0 hits on all six.** That is
  the reproducible core of "0 of 82". Raw substring matching gives **5** — two
  hardened-C files quoting their own forbidden spelling in the comment explaining
  why they avoid it, p16's *ghost* loop invariant, and two p17 comment/format
  strings — so the 0 is a property of the **matching rule** (blank comments and
  string literals, blank Verus ghost clauses, delete whitespace), not of the
  text.
- **`required` is NOT decidable, and the manager's prescription to audit it
  universally was refuted by measurement.** Applying every entry to every rung of
  its declared languages gives **41 misses over 158 obligations — all 41
  non-defects** (18 backticked prose like a filename or the word "why", 17 spans
  quoted *in order to be absent*, 6 scoped by the entry's English). Worse, it
  inverts: **9 of the 117 "matches" match for the wrong reason** — p02's `|`
  matching the `||` of a guard, p08's `&` matching `&mut` — so the naive rule
  contradicts the declaration it audits. `required` therefore reports
  **presence in two buckets with no verdict**, which is the smallest thing that
  works.
- **`pins_nothing` is the useful signal**: an entry that matches *no* rung of a
  language it declares is a bug in the **ruler**. It ran 16 → 11 across
  TASK_019's repair, and the five that vanished are exactly the ellipsis and
  p02's single-string entry.

Use **direction**, which is a number.

⚠ **THE TEST AS RECORDED HERE IS BROKEN, AND IT WAS CITED AS LOAD-BEARING BEFORE
ANYONE CHECKED IT** (TASK_025_REVIEW major 5). It said: *"an edit that **shrinks**
the admissible class and **lowers or does not raise** the pattern's own published
figure is not self-certification"* — and then offered as a **passing** example
"p16's exclusion makes its published tax **4.5× larger**", an exclusion that
**raises** the figure. The stated clause and its own cited precedent point in
opposite directions, so the rule decided nothing, and TASK_024 read it the other
way round and made it the load-bearing reason not to pin p16's unroll factor.

**The repair, and it is PROVISIONAL — proposed by the manager at TASK_026, not
yet attacked by anyone.** The quantity that matters is not up-or-down, it is
*whose interest*: this project's thesis is "safety is cheap", so the flattering
direction for a safety-tax number is **smaller**.

> *An edit to a declaration is self-certification if it moves the pattern's own
> published figure in the direction that flatters the author's thesis. For a
> safety-tax number that direction is **down**.*

Re-scored under it: p16's TASK_017 exclusion shrank the class and made the tax
**4.5× larger** — against interest, **passes**. p02's repair was not a
declaration edit at all but a *measurement* of an in-contract minimum, so the
test does not apply to it and citing it here was a category error.

**And TASK_024's decision does not survive either reading, for an independent
reason**: excluding the chunked fold would *not* have restored `+19`, because
p16's declaration licenses **manual unrolling by name** and a manual 32× unroll
measures 5.18750, still below the shipped 5.75. So "we are not allowed to pin it"
was an argument from a broken rule about an exclusion that would not have worked.
**The conclusion — do not pin the unroll factor — stands; every stated reason for
it has been withdrawn.** Do not cite this test again until a reviewer has
attacked the repair.

⚠ **THE REPAIR HAS NOW BEEN ATTACKED, AND IT FIRED — on p13, on shipped code,
with a measured number** (TASK_045_REVIEW blocker 1). Until then every direction
test on this project had come out at or near **0.00**, which is what a clean
declaration looks like and also what a test that cannot fire looks like. It can
fire.

**The shape it caught is new and is the one to look for: an idiom entry SCOPED to
some rungs and not others.** p13's `spec.md:374` and `:394` pin the byte-loop
copy and fill in **`safe_naive.rs`, `unsafe.rs` and `verus.rs`**, exempting
`safe_tuned.rs` **by name**. So R3 was permitted the bulk spelling and R4 was
forbidden it — and p13's headline is *"safe Rust beats unsafe by 13.6–17.3%"*.
Relax the pin symmetrically and it is **−7.54% / −14.74%**: **48% (small) and 17%
(large) of the published margin was the pin.** The sign survives; the magnitude
does not.

> **An idiom entry whose scope names some rungs and excludes others is a thumb on
> the scale until its direction is measured.** A whole-pattern exclusion is
> visible — every rung loses the spelling and the comparison stays matched. A
> *scoped* one silently makes the two sides of the comparison unequal, and the
> `pins_nothing` signal cannot see it because the entry does pin something on
> every rung it names.

⚠ **But a scoped entry is NOT automatically a thumb, and the repair is not
"delete the scoping".** p13 had three of them and measuring each separately gave
**three different answers** (TASK_046) — which is the whole method in one
pattern:

| scoped entry | what the measurement said | disposition |
|---|---|---|
| byte-loop **copy + fill** | the bulk spelling verifies (**17/0, twin 24/0**); the prover never excluded it | **relax symmetrically** — it *was* a thumb |
| consumer **`position()`** | `` `…iter::…::position` is not supported `` at the pinned vstd | **keep** — the exclusion is one layer down, not a thumb |
| consumer **bound** | a bounded unchecked scan verifies **19/0, twin 22/0, no new TCB** | **keep by fiat and PRICE it** — nothing but English excludes it |

**So the rule is: price every scoped entry, then dispose of each on what the
price says.** An entry the prover already excludes costs nothing to keep and is
not a thumb. An entry only the declaration excludes is a **fiat**, and a fiat is
legitimate — the whole named-spelling standard is fiat — **but its price must be
published beside the number it protects.** p13's third entry is worth the sign of
its headline.

⚠ **And note where the error was reported.** p13's `NOTES.md:842` said the R4
side "is not searched" and attributed it to **the prover** — the R4-is-chained-to
-the-prover mechanism (finding 14) is real, invoked constantly, and it is now
also **the most available wrong explanation on this project**. The prover did not
bind: `copy_nonoverlapping` and `write_bytes` verify at the pinned vstd
(15/0, twin 22/0, `identity: exact` holding). **Before blaming vstd for an
unsearched R4 side, run `./verus_run.py`** — the same eleven minutes that has
already killed five published figures.

### R1h — the hardened C cell (optional, added at TASK_004)

| Rung | Dir/file stem | Definition |
|---|---|---|
| **R1h C-hardened** | `c/kernel_hardened.c` | R1's kernel plus the bounds check a careful C programmer writes. Same signature, same calling convention, same driver — the *only* difference is the check. |

**Ship it for every pattern that models a bug.** With only R1, "C is faster" and
"C is unsafe" are the same sentence, because C is faster precisely in that it
skipped the check. R1h separates them:

- R1 vs R1h = what the check costs, **inside one language**
- R1h vs R4 = what Rust's unsafe rung costs against *safe* C
- R1h vs R2/R3 = what Rust's additional machinery costs beyond the bare check

`harness/build.py` creates the `c-gcc-h` / `c-clang-h` cells for any pattern that
ships `c/kernel_hardened.c` and for no other — presence of the file is the
switch, there is nothing to declare. A pattern with R1h builds 32 cells, not 24.
Use `buildmod.measured_cells(pdir)` / `all_cells(pdir)`, never the module-level
`MEASURED_CELLS` / `ALL_CELLS`, which exist only for argparse.

Measured on p02 (`-O3`, marginal Ir per call, both `small` and `large`): the
check costs **+5 instructions with gcc and +12 with clang, per call, independent
of the size of the copy** — 2.2% and 5.4% of the call on the L1-resident input,
0.05% and 0.12% on the memory-bound one. So the headline p02 supports is *safety
costs about the same in both languages, and Rust makes it non-optional*, which
is a much stronger claim than any p01 could produce.

## The structural findings (established by `pilot/`, do not re-litigate)

**Numbering warning — 26 stale citations exist.** The findings in *this* file are
numbered **1–7, one per pattern**. `RECAP.md` carries a *different* list, its own
digest, numbered **1–14**. "`.memory/01-ladder.md` finding 14" appears in 26
places and points at nothing. **Name the pattern, never the number.**


1. **A Verus proof costs zero instructions.** Ghost code, `requires`, `ensures`,
   invariants, `decreases` all erase. Established at the pilot, corrected at
   TASK_001, and independently re-derived at TASK_001_REVIEW **on the raw
   machine-code bytes** — the only oracle that can establish this (normalised text
   collides; see `.memory/03-measurement.md`):

   | | static raw | static padding-excl | raw-byte md5 |
   |---|---|---|---|
   | R2 safe / R2 verified-safe | 57 / 57 | 46 / 46 | `935221a8…` both |
   | R4 unsafe / R5 verified-unsafe | 37 / 37 | 33 / 33 | `98e4a665…` both |

   Executed instructions (`Ir`) equal too. *(The pilot's published 58/38/33 are
   each one too high — the old pipeline counted the symbol header line.)*

   **Two digest conventions exist; always say which.** `935221a8…`/`98e4a665…`
   are `harness/asm.py`'s `md5_raw`, which includes trailing alignment padding;
   `e5310297…`/`a23e076c…` are the `nm --print-size` extent, i.e. the function
   proper. Both are reproducible (TASK_002 claimed the latter was not — it was
   wrong, TASK_002_REVIEW re-derived them first try). The counts and the
   equalities are unaffected either way. See `.memory/03-measurement.md`.

   Reproduced independently on p01 (TASK_002), `-O3 isolated`, and re-derived at
   TASK_003 under **both** conventions:

   | pair | `md5_raw` (objdump grouping) | `md5_fn` (`nm` extent) | counts |
   |---|---|---|---|
   | R4 ≡ R5 | `fb90a96c…` | `619b1d1b…` | 36 / 34 (+3 insn padding) |
   | R2 ≡ R2v | `f1e7f951…` | `12d307f2…` | 49 / 47 (+10 insn padding) |

   The R2≡R2v digests were `6c85987d…`/`f8e1fe32…` and went stale at the TASK_005
   barrier swap; re-measured at TASK_006_REVIEW. The R4≡R5 pair is unchanged and
   current. **Every *equality* held throughout** — only the absolute digests
   moved — but `.memory/03-measurement.md` requires an identity claim to cite a
   reproducible raw-byte digest, and for three tasks these two were not. p01's
   `NOTES.md` carried the same stale pair plus three more (the `O0` rows).
   The instruction counts in this table have **not** been re-verified since the
   swap; treat them as unconfirmed until something re-measures them.

   TASK_002 published the counts as 39/34 and 59/47; those are objdump's
   grouping, i.e. the function *plus* its trailing padding. Quote `md5_fn` for
   identity — `harness/asm.py` now reads padding separately so a benign relink
   at a different alignment cannot be mistaken for "the proof cost something".
2. **A proof buys nothing on its own.** Proving R2 panic-free leaves every bounds
   check in place — rustc never learns what Z3 knew. The win only materialises
   when the proof *licenses unsafe code* (R5 = R4 codegen + discharged obligations).

3. **The static safe-vs-unsafe gap is mostly not a dynamic gap, and the tuned safe
   rung nearly closes it.** (TASK_001, corrected at TASK_001_REVIEW.) On the pilot
   kernel at `-O3`, LLVM hoists the bounds check clean out of the vectorised loop,
   so the safety tax is **O(1) per call, not O(n)** — confirmed across
   n = 999 … 100 000. The static delta is prologue, panic landing pad and padding.

   Magnitudes, per call, versus unsafe R4:

   | rung | static raw | static padding-excl | executed `Ir` delta |
   |---|---|---|---|
   | R2 safe-naive (`v[i]`) | +20 | +13 | **+7 … +22** |
   | R3 safe-tuned (iterator) | +24 (largest of *all* rungs) | +16 | **+6 … +8** |

   Three traps here, all of which bit the first write-up:

   - **The delta is not a constant.** It varies with `n mod 4`: 22 / 7 / 9 / 11 for
     residues 0 / 1 / 2 / 3. R2's vectoriser peels a 4-element scalar epilogue when
     `n % 4 == 0`; R4 does not. The original "+22, independent of n" came from three
     data points that were all ≡ 0 (mod 4). Quote a range, or state the residue.
   - **Quote the padding-excluded static number**, or say which you are quoting.
     `.memory/03-measurement.md` calls the raw count overstated; do not then
     headline the raw gap.
   - **R3 is the honest comparison for "what safe Rust costs."** Idiomatic
     iterator code lands within ~6 instructions per call of unsafe while being
     *statically the largest cell in the ladder* — a sharper refutation of
     static-count-as-proxy than the gcc/clang one. Reporting R2 alone overstates
     safe Rust's cost by ~3.7×. **Never publish a safety-cost claim without R3.**
   - **…and the corollary, which cost us three retractions: without the *best*
     R3.** A safety-cost claim is a claim about the *language*, so it is only as
     good as the best spelling anyone can find — and this project has now
     published a spelling's cost as safety's cost **three times**: p02 (a lost
     `memcpy` idiom, retracted), p16 ("only the naive indexed spelling is O(n)",
     caught at review), p05 (`chunks_exact` beats the *unsafe* rung, caught at
     TASK_014_REVIEW). The failure mode is always the same — one plausible R3 is
     written, measured, and reported as what safe Rust costs.
     **Before any safety-cost headline, write at least two independent
     *in-contract* R3 spellings and quote the cheaper.** "In contract" is the
     whole of TASK_018: a spelling that violates the pattern's declared idiom
     measures a different kernel, and one that respects it may still be much
     cheaper than the shipped cell. The iterator/slice-consuming forms
     (`chunks_exact`, `split_at`, `iter().zip()`) are the ones that keep winning,
     because they hand the optimiser a length it does not have to re-derive.
     ⚠ **The TWO-STEP RESLICE is a distinct lever from all of those, it wins for
     a different reason, and it was untried on every pattern before p04**
     (TASK_042_REVIEW). Replace the one-shot `&buf[off..off + len]` with
     `buf.split_at(off).1.split_at(len).0` — or `get(off..).unwrap()` then
     `get(..len).unwrap()`, five distinct machine codes, all equal — and the
     window reslice costs **one instruction less**, on every pattern that reslices
     a window this way. **The mechanism is REGISTER ALLOCATION, not bounds-check
     removal**: both forms keep both checks, but `off + len` needs a scratch
     register (`mov ; add ; jb ; cmp ; ja`) while `buf_len - off` is computed in
     place in `%rsi`, which is dead afterwards (`sub ; jb ; cmp ; ja`). It took
     p04's published safety tax from `+5.00` to `+4.00` — the *whole* tax — and
     falsified *"the shipped R3 is the cheapest found"*. **Try it on any pattern
     whose R3 opens with a window reslice**, which is most of them.
   - **…and that rule is still not enough — but the fix is not "match the
     idioms" either.** The audit measured four safe spellings of p05's kernel and
     the review took it to eleven; the spread across them **exceeds the
     safe-versus-unsafe gap**. Quoting "the cheaper of two" publishes a number
     the third spelling moves, and **R4 is a spelling too**.

     "Compare idiom-matched rungs" was the obvious repair and **it does not
     work**: "same idiom" has **no fixed point**. R3′ and R4′ were idiom-matched
     under the audit's own criterion; R4″ satisfies that criterion too and is
     `nrow + 2` cheaper; R4‴ — the *safe* program with only its checked slice
     constructions replaced, the most matched unsafe rung it is possible to
     write — lands on R4″'s number. "Same idiom" picks out an equivalence class
     whose members differ by `O(nrow)`, so no gate check can decide between them.

     **The rule that survives: a safety number is only meaningful as a
     matched-pair delta under an idiom the pattern *declared before measuring*.**
     A published spread cannot carry a safety claim at all — see finding 14 for
     why that is a theorem rather than a preference. The declaration is p05's
     `spec.md:69-73` mechanism, which was right both times it was tested and
     failed only by being **invisible** to the gate. Fix: move it into the hashed
     contract block (`.memory/06-catalogue.md`).

   Reproduced on p01 at TASK_002, with the residue effect measured properly this
   time (16 window lengths, `inputs/gen.py --sweep`), `-O3 isolated`, per call:

   | rung | res 0 | res 1 | res 2 | res 3 |
   |---|---:|---:|---:|---:|
   | R2 safe-naive | **+29** | +11 | +13 | +15 |
   | R3 safe-tuned | +5 | +4 | +4 | +4 |
   | R5 verus | 0 | 0 | 0 | 0 |
   | R1 gcc | +368 … +384 (≈ +41%) | | | |

   Constant in `win_len` within a residue class (+29 at 500, 504, 508 *and* 512),
   so the tax is per call, not per element. **Give every pattern's `small` and
   `large` inputs different residues mod 4** — p01's first draft used 500 and
   4096, both ≡ 0, which is the single worst residue for R2 and would have
   overstated it 2.4×. That is the third time this trap has been stepped in.

   One new caveat: the +29 is the *out-of-line* figure. In `whole` mode on
   `large`, R2's inlined kernel costs ≈ **+340** per call — its scalar epilogue
   keeps a live per-element bounds check and the driver's `div` is
   rematerialised. R3 and R5 show no such amplification. Derived from a
   difference of two builds, so: an observation, not a settled result.

   Do **not** generalise any of this to patterns with data-dependent indices — the
   interesting patterns are precisely the ones where LLVM cannot hoist, and that is
   where the ladder earns its keep.

   **p02 first appeared to be that case and was not.** The claim published at
   TASK_004 — "R2 pays an O(n) bounds-check tax on a data-dependent copy,
   +178 at 61 B and +1025 at 4092 B" — was **refuted at TASK_004_REVIEW**. Keep
   the refutation, not the claim; it is the most instructive result so far.

   | rung | 61 B | 4092 B | vs R4 |
   |---|---:|---:|---|
   | R2 safe-naive, as first written | 407.0 | 11226.0 | +178 / +1025 |
   | …`copy_from_slice`, indexed fold kept | 239.0 | 10210.8 | **+10 / +10** |
   | …indexed copy kept, one `&src[a..b]` reslice added | 239.0 | 10210.8 | **+10 / +10** |
   | …identical but the check written *additively* | 237.0 | 10208.8 | **+8 / +8** |
   | R3 safe-tuned | 239.0 | 10210.8 | +10 / +10 |

   The decomposition that kills it: changing **only the fold** moves nothing;
   changing **only the copy** removes 100% of the tax. R2's and R4's fold loops
   are the *same* 19-instruction unrolled body — the indexed fold's bounds checks
   cost **zero**. The real cause is that `len > src.len() - (src_off + 2)`
   (subtraction-first) leaves LLVM unable to prove the index bound, so
   loop-idiom recognition never forms a `memcpy`; one operator change flips
   `bulk_calls []` → `['memcpy@GLIBC_2.14']`, 118 insns → 87. So the comparison
   was **inline SSE2 copy vs `call memcpy`** — two different algorithms — and C
   written the same way pays the same (clang +532; gcc's byte loop is 94 Ir
   *faster* than glibc's memcpy).

   The honest claim: *rustc failed to idiom-recognise one spelling of a byte-copy
   loop; three other spellings, including the reslice a competent Rust programmer
   writes, are +10 flat.* That is a codegen fragility finding, not a safety-cost
   finding — still worth publishing, but not as a safety tax.

   Note also that "gcc's byte loop beats glibc `memcpy`" — briefly believed — is a
   mislabelled comparison. gcc's byte loop is faster than **R4** (10106 vs 10201),
   not than gcc's own `memcpy` build (9200). *Within* one compiler the byte loop is
   dearer: gcc +906, clang +528. The conclusion survives and is stronger.

   **Two rules follow.** (1) Before attributing a cost to bounds checking,
   decompose: change one loop at a time and re-measure. A whole-kernel delta
   attributes nothing. (2) Residues bite harder than recorded. Swept over 68
   lengths at two scales (TASK_006), R2−R4 is a **sawtooth of constant amplitude
   179 Ir, resetting at `len ≡ 1 (mod 16)`**, on a linear term of 0.21 Ir/byte —
   so copying *one more byte* (2048→2049) made R2 174 instructions *cheaper*.
   `gen.py` pinned residues mod 4 and mod 8; the modulus that mattered was 16, and
   it now checks mod 16 before writing any input. Sweep, do not sample — and sweep
   **two full cycles**: the first sweep design used 16 lengths per band and could
   not distinguish period 16 from period 64.

   **R3 remains the honest number** — +10 per call, flat — the third pattern in a
   row where that is the finding.

   Also from p02, against p01's gcc-vs-clang result: **gcc executed ~10% fewer
   instructions than clang here and took 23% longer** (8765 vs 9764 Ir per call;
   30.8 vs 25.0 ms). Neither compiler is reliably ahead, and instruction count
   and wall clock disagreed in *direction* on the same source. Report both
   columns; do not let `Ir` stand in for time without saying so.

4. **p16 is the case p01 said not to generalise to. One *spelling* of safe Rust
   pays an O(n) cost there; idiomatic safe Rust still does not.** (TASK_007,
   corrected at TASK_007_REVIEW — the first write-up of this said "first real O(n)
   safety cost" and that **overclaimed**.) A TLV walker: trip count from attacker
   data, each record's position depending on every previous length field, nothing
   hoistable, nothing idiom-recognisable.

   **The number that settled it — 5.7500 Ir per folded byte for both R3 and R4,
   "safe Rust costs zero per byte" — was published as SIGN-WRONG IN CONTRACT**
   (TASK_023_REVIEW) **and that framing is itself withdrawn** (TASK_024,
   TASK_025_REVIEW). What is true, swept and mechanised is directly below; the
   history is kept because three tasks argued about it.

   **THE STATEMENT TO QUOTE: p16's per-byte safety tax is 0.00000 Ir/byte,
   swept.** Fold both rungs the same way and safe−unsafe is a *single integer per
   call* at every length — 10 / 11 / 12 / 12 / 12 for `chunks_exact` 4 / 8 / 16 /
   32 / 64, and 17 (`vlen ≡ 0 mod 4`) / 21 for the shipped fold — over **127
   consecutive `vlen`**, slope of the difference `0.0000000`, max residual 0.00
   (TASK_025_REVIEW; TASK_024's three "residue-matched bands" were three pairs at
   one offset, ≡ 24 mod 32, so the sweep is what makes this a result). The
   mechanism is visible and is why it cannot be otherwise: **the reslice (R3) and
   the `get_unchecked` (R4) both sit *outside* the fold loop**, so the chunk body
   is mnemonic-identical on the two sides at K = 4, 8, 16, 32 and 64.

   **What must NOT be quoted: any bare per-byte rate, or any difference of rates
   across unmatched spellings.** In contract, one exact-string substitution apart,
   p16's rate ranges **5.04688 … 6.62500** — a 31% spread — with a seventh
   spelling at 5.37500; and the measured rates carry ±0.01 Ir/byte from the
   driver's `println` digit-count term, which does **not** cancel within a binary
   and is 20× the gap between two published rates. The 5-decimal figures are exact
   as *disassembly* quantities (`body/K`), not as measured slopes.
   The cross-spelling figure that reached four files as a headline was
   ~~`−0.5625`~~ and is **`−0.65625`** — `5.09375 − 5.75` — the published value
   being the **K=16** number left pointing at the K=32 rung when the sentence was
   re-aimed (TASK_025_REVIEW major 2, confirmed independently by
   `(115 − 31)/(4·32)`). It is a **codegen difference between two folds** and was
   never a safety cost.

   Against the *shipped* R4 held fixed, an in-contract safe rung is cheaper on
   every blob — `R4ship − s_c32` = **+199** at `small` / **+2365** at `large`, and
   `s_c64` is cheaper still at **+127 / +2545**. ⚠ So **−199 / −2365 is not the
   in-contract minimum either** (TASK_025_REVIEW major 3): that is the **fifth**
   published p16/p05 "minimum" overturned by the next search, and nothing here
   should be published as one. Report it as *cheapest found*, with the spelling
   named.
   ~~`51·nrec − 5` (`vlen ≡ 0 mod 4`) / `48·nrec − 5`~~ — **domained wrong**
   (TASK_024, confirmed TASK_025_REVIEW): both are **fixed-`vlen` slices** (124
   and 126), not residue classes — at `vlen` 56 and 88, both `≡ 0 (mod 4)` at
   `nrec` 4, the difference is 31 and 115, not 199 — and extrapolated to `large`
   the law predicts 475 against a measured 2365. It scales with `vlen` because the
   effect is per byte.
   **`5 + 3/K` is not a law** (TASK_024): a three-point fit falsified by two more
   points of its own family, `chunks_exact(4)` = 6.50000 and `(8)` = 6.62500,
   *dearer* than the shipped 5.75 and not monotone in `K`. The mechanism is
   `try_into::<[u8;K]>()`, and TASK_025_REVIEW built the control that proves it:
   drop `try_into` and K=4 measures **5.37500** (43 insns / 8 bytes) and is
   **1509 Ir/call cheaper** than shipped R4 at `large`. **So "chunking is dearer,
   therefore the free parameter is not a dial that flatters the safe rung" is
   refuted** — it rested on the one spelling that happened to go the other way.
   **The free parameter is the whole fold spelling, not `K` and not the unroll
   factor.**

   **p16 is the second pattern after p17 where an admissible safe rung beats its
   own *shipped* R4** — a comparison against a shipped cell, not between classes.
   ⚠ **The class-level version of that sentence is refuted**: TASK_024 wrote *"the
   admissible unsafe class dips below the admissible safe class at matched
   spelling, as `inf(R4) ≤ inf(R3)` predicts by construction"*, and **it has no
   rung behind it** — `u_c32` cannot be a p16 R4 at all (blocker 1; see the
   R4-by-permission paragraph at the top of this file, which the same measurement
   overturned project-wide). Whether `inf(admissible R4) > inf(admissible R3)` on
   p16 is **open**: a hand-unrolled 32× fold with explicit indices is
   Verus-expressible in principle and nobody has tried it.

   **The clean negatives from TASK_025_REVIEW, so nobody re-runs them** — and note
   that this file previously carried a "stated so nobody re-runs them" bullet
   which told the next agent not to run the experiment that broke it, so read this
   list as *already run and reproduced*, never as *do not check*:
   all twelve probes honour **all four** of p16's `required` entries (not just the
   two `spelling_matches` checks — tag folded *before* the fit test and `nrec`
   folded were verified by hand, 12/12); mnemonic identity holds at K = 4 and 8 as
   well as 16/32/64, so §10a.2 under-claims; the band-A `+0.00469` offset is the
   `println` term, now **controlled** rather than asserted
   (`Ir = 354710 + 1459.91·n + 22.63·digits`, max residual 14.8 Ir) and it cancels
   exactly in every safe-minus-unsafe difference; 95/95 × 12 = 1140 equivalence
   comparisons, 0 mismatches; Miri clean on `small`, `large` and all three
   `adversarial-*`; and `harness/check.py p16` is `PASS` on the committed tree.

   ⚠ **Reproduction gap, still open — TASK_027.** §10a.2's twelve probes exist
   only in gitignored `.temp/p24/*.py`. `controls/*.py` is inside `source_sha256`
   precisely so a control's reproduction path ships. Three concrete items from the
   review: the fold variants drop into `controls/gen_controls.py` as a third dict
   but their hardcoded absolute `REPO` must become the `__file__`-derived path
   that file already uses; the K=64 row needs a fourth `inputs/gen.py` band
   appended **last** (so the 95 existing blobs stay byte-identical) or an explicit
   "scratch-only" marker; and `.temp/p24/foldbody.py` must **not** ship as-is —
   re-run as committed it prints `identical=False` at every K, the opposite of the
   verdict §10a.2 cites it for. Landing the first re-runs the p16 gate; the second
   re-runs every p16 measurement.

   The shipped-pair figures below (+27/+77, "O(1) per call") describe the shipped
   pair and nothing wider.
   **Corrected at TASK_015_REVIEW: "O(1) per call" is residue-dependent.** The
   +27/+77 pair decomposes as `7 + 5·nrec` at `vlen ≡ 0 (mod 4)` and `7 + 7·nrec`
   otherwise, so it is `O(nrec)` — the two published points happen to sit at
   nrec 4 and 10. A cheaper spelling exists (`split_at` / `split_first_chunk`,
   indistinguishable from each other) at `R3ship − R3′ = 10·nrec + 9`, and
   idiom-matched against an equivalent R4 the residual is **7 flat at
   `vlen ≡ 0 (mod 4)` and `7 + nrec` in the other three classes**, swept over 68
   blobs.
   **But it is OUT OF CONTRACT, decided at TASK_017.** p16's `idiom.required[0]`
   was disambiguated as naming **tokens** — `end - p >= 3` and
   `vlen > end - (p+3)` must appear literally — and `split_first_chunk` contains
   neither. The reading was chosen on four measurement-independent grounds (house
   convention across p05/p02/p17; those tokens *being* the cursor-and-end
   traversal; and the exclusion falling **symmetrically**, taking the consuming
   *R4* control out with the R3s), explicitly **not** on which answer made the
   cheaper spelling inadmissible.
   **The suspicion that the reading was self-serving was measured and refuted at
   TASK_017_REVIEW: it makes p16's published safety tax 4.5× LARGER.** Shipped
   pair `7 + 5·nrec` / `7 + 7·nrec` (+27/+77); excluded matched consuming pair
   `7` flat / `7 + nrec` (+7/+17). What it protects is the shipped cells'
   *standing* and §3's swept law, not a flattering number.
   **Both readings were superseded at TASK_018**, which adopted the named-spelling
   standard uniformly across all six patterns, **labelled as a policy adopted
   after measuring** rather than as a disambiguation of what the text meant.
   Ground (ii) of the four — that pinning the tokens holds the representation
   fixed and so makes `R3 − R4` a safety rather than a representation difference
   — **is withdrawn by measurement** and has been withdrawn from the spec block:
   42 of p16's 77 Ir/call at `large` sit inside the part of the spelling the pin
   does not fix.

   **And "cheapest admissible is unestablished" is now FALSE, not unestablished.**
   TASK_018 measured **three** admissible p16 respellings, all keeping both named
   comparisons literally, all byte-identical in output on 73/73 inputs; **two are
   cheaper than the shipped R3**. `R3ship − r3_endslice = 2·nrec − 2` and
   `R3ship − r3_window = 4·nrec − 8`, zero residual across four residue classes
   (the `nrec` coefficient was a 3-point fit; **TASK_018_REVIEW promoted it to a
   swept law** — 11 `nrec` values × 2 residue classes, 110 marginals, **zero
   residual**. The 68 committed blobs could not have tested it: both bands sit at
   `nrec` 2 and 4.)

   **`+27 / +77` is a bound on `inf(in-contract R3) − R4ship` — and on nothing
   else. MEASURED FALSE as a bound on p16's in-contract safety tax**
   (TASK_023). ⚠ **The reason TASK_023 gave is REFUTED and so is p05's half of
   it** (TASK_027_REVIEW). It was: *"p16's unsafe rung moves in contract too, by
   the same lever that moved p05's — respelling the header read as one unaligned
   `u16` — and unlike p05's constant it moves by a coefficient,
   `R4ship − r4_hdr = 4·nrec`."* The measurement is right and **the rung is
   not**: `r4_hdr` needs `read_unaligned` and `c4_hu16_nz` needs
   `read_unaligned`/`as_ptr`/`add`, all `is not supported` at the pinned vstd, and
   every alternative route (`from_raw_parts`, `TryFromSliceError`,
   `from_le_bytes`) is unsupported too. **Neither pattern's R4 side has moved by a
   single admissible instruction.** The `+27 / +77` bound is still one-sided —
   that part stands, on the R3 side alone.
   **The pair interval published at TASK_023 — 17…47 / 43…127,
   "111%/109% wide" — is refuted** (TASK_023_REVIEW): measured, it is
   **−239…+236 (1759%) / −2449…+2244 (6095%)**, and **its bottom is negative on
   all 24 points**. Do not re-point the "which declaration is loosest"
   comparison either; that compared a 2-lever search against p05's 46-spelling
   one, which is the same error one level down. Withdraw it.
   The R3-side figure below is one-sided, and **its number is refuted too**: the
   cheapest in-contract R3 found against shipped R4 is **−199 at `small`
   (`chunks_exact(16)`/`(32)`) and −2545 at `large` (`chunks_exact(64)`)** — not
   `+19 / +45` (TASK_023_REVIEW), not `−199 / −2365` (TASK_024), and not the
   `−127 / −2545` the manager wrote at TASK_025_REVIEW, which paired one rung at
   both inputs.
   ⚠ **NO SINGLE SPELLING IS CHEAPEST ON BOTH BLOBS** (TASK_027, measured):
   `chunks_exact(64)` is **72 Ir/call dearer than `(32)` at `small`** and 180
   cheaper at `large`. Mechanism: a larger `K` leaves a longer scalar
   `.remainder()` tail, and `small`'s `vlen` 124 is `1×64 + 60` against
   `3×32 + 28`. **So a cheapest-found figure must name its INPUT as well as its
   spelling** — one more reason the quantity is not a minimum in any useful
   sense. The bound survives, the value does not, and it has now moved four
   times. Write "cheapest found", never "minimum". And
   R3-side bound. This file already said, at finding 3: *"Never publish a
   safety-cost claim without R3."* The rule was violated by its own author on the
   next pattern. **Lead with R3 or do not lead.**

   `-O3 isolated`, marginal `Ir`/call:

   | rung | small (508 B win) | large (4090 B win) | vs R4 |
   |---|---:|---:|---|
   | c-clang / c-clang-h | 2993 / 3017 | 23761 / 23815 | check = +24 / +54 |
   | c-gcc / c-gcc-h | 4062 / 4079 | 32694 / 32735 | check = +17 / +41 |
   | **R2 safe-naive** | **5095** | **40921** | **+2085 (+69%) / +17123 (+72%)** |
   | R3 safe-tuned | 3037 | 23875 | +27 / +77 |
   | R4 unsafe / R5 verus | 3010 / 3010 | 23798 / 23798 | 0 |

   **R2's cost is per byte, not per call** — 10.00 Ir per folded byte against
   R3/R4's 5.75, over 68 consecutive value lengths in two bands 18× apart, exactly
   4.25 apart in both. The sweep is *exactly* linear (least-squares residual
   **0.00** over 34 points per band) and `R2 = 10·folded + 21·nrec + 11`
   reproduces both shipped totals to the instruction. Measured, not fitted.

   **Decompose before calling it a bounds-check tax — the same trap as p02.**
   Changing **only the fold** removes 98.0% / 99.3% of the gap; changing **only
   the walk** removes 1.5% / 0.5%; the two sum to 2091 against the whole gap's
   2085, so there is no interaction term. The cost is entirely in the inner byte
   fold: R2's is a rolled 10-instruction body, R4's is 4×-unrolled at 23 insns per
   4 bytes.

   **The attribution was then confirmed by construction at TASK_007_REVIEW**,
   which is why it is safe to state. `-C llvm-args=-unroll-count=1` rolls R4's
   fold and is a **bit-for-bit no-op on R2** (so it is not silently changing both
   sides). Rolled R4 and rolled R2 then differ by exactly `cmp %rax,%rsi ; je
   <panic>`:

   | fold | band A | band B |
   |---|---:|---:|
   | R2, rolled + checked | 10.0000 | 10.0000 |
   | R4 shipped, 4×unrolled + unchecked | 5.7500 | 5.7500 |
   | **R4, rolled + unchecked** | **8.0000** | **8.0000** |
   | **gap R2 − R4-rolled = the check alone** | **2.0000** | **2.0000** |

   So 4.2500 = 2.0000 + 2.2500 with **zero residual**. The 8.00 rolled-unchecked
   constant has four independent sightings, the best of which is free: **R4's own
   remainder loop in the shipped binary** is 8 insns/byte — R2's body minus
   exactly `cmp`+`je`. (The `shl $0x5` site count offered in `NOTES.md` is *not*
   independent corroboration — both counts follow from the same unroll factor.)

   **The split is exact but path-dependent, and the counterfactual is not what it
   looks like.** Forcing LLVM to unroll the *checked* loop
   (`-unroll-runtime-multi-exit -unroll-count=4`) gives **9.50**, not 7.75: four
   copies need four exit tests, `mov,or,cmp,je` = 15 insns = 3.75/byte. So
   unrolling R2 would recover **0.50, not 2.25**. `NOTES.md`'s "would have
   amortised" is a false counterfactual. The right word is the stronger one:
   **the check does not merely cost 2.00, it forecloses an optimisation worth
   2.25 that it could not have amortised anyway.**

   **The transferable lesson: a safety tax must be attributed to a mechanism,
   never to a comparison** — and the mechanism here is only half the check. Same
   shape as p02's retraction (a lost `memcpy` idiom), arriving this time at a real
   cost rather than a spurious one.

   **Three further things p16 establishes:**
   - **`Ir` and wall clock disagree in *magnitude*, not just direction: +72% `Ir`
     → +0.27% time.** Spreads are 0.96–2.31%, well inside the 10% discard
     threshold, so unlike p02's timing this is a *usable* null. **The null itself
     is safe** — it is a ratio taken inside one session — and so is the ns figure.
     The fold is a serial Horner chain, latency-bound: differencing `n_iters`
     gives **3.027–3.055 cycles/byte** for every rung on `large`, 3.03–3.08 on
     `small`.

     ⚠ **That cycles/byte figure is an inference, not a measurement, and it is
     now qualified (TASK_012).** It converts a wall time measured in TASK_007
     with a clock measured in TASK_007_REVIEW — *different sessions* — and this
     box's clock is set by other tenants: the same probe read 3.80–3.89 GHz in one
     session and 2.55–2.86 GHz in another (`.memory/00-environment.md`). At
     all-core turbo the same ns figure is ~2.2 cycles/byte.
     What survives independently: the Horner chain `(acc<<5) - acc + b` has a
     **hard 3-cycle serial latency floor**, so *if* the chain is the limiter the
     clock during measurement must have been ≥ ~3.8 GHz. Consistent, and it is
     why 3.03 looked so clean — but it is a consistency argument, not an
     independent confirmation. **Do not publish cycles/byte for p16 without an
     interleaved clock measurement.**
     Because L1-resident `small` gives the same rate as L3-resident `large`, the
     obvious alternative — memory-bandwidth-bound, which would equally hide a
     +70% `Ir` gap — is **ruled out**, not merely unconsidered.
     **This is a property of this kernel, not of bounds checks**: a kernel with
     independent inner iterations would turn the same 4.25 Ir/byte into time.
     *(The first write-up's cycle arithmetic was wrong — it implied 3.30 GHz while
     CPU 5 turbos to 3.85 GHz, and 13% / 21% of the quoted wall times is fixed
     overhead outside the kernel. Two errors that cancelled. **Always difference
     `n_iters`; never divide a total wall time by a byte count.**)*
   - **Vectorisation is not a confound, but "nothing vectorises in any rung" is
     false** — it is **23 of 32 cells**; the 9 with `['xmm']` are all `whole`-mode
     `main`, i.e. the driver, not the fold. The *fold* is scalar in every rung, so
     the gap is measured on a scalar loop on both sides. Quote the 23/32.
   - **R3 survives, and is now the *fourth* pattern in a row** — see the opening
     of this finding. `7 + 7·nrec` (`7 + 5·nrec` when vlen ≡ 0 mod 4) is a
     **zero-degrees-of-freedom interpolation**, and only `large` is genuinely
     out-of-sample; do not call it a prediction. **The residue modulus that
     matters here is 4** — the unroll factor — amplitude 1.5%. p01's was 4, p02's
     was 16; do not assume.
   - **gcc's 36% deficit is a flag default, not a codegen limit.** `c-gcc` is 4062
     against clang's 2993 on `small` — but with `-funroll-loops` gcc reaches
     **2823 and beats clang**. Not a fortify/ssp artefact. Before reporting any
     gcc-vs-clang gap, establish whether it is a default or a capability.

   Security half, and it was **directly demonstrated** at TASK_007_REVIEW rather
   than inferred: `end - p` wraps to `0xfffffffffffff03d` and the walk ran
   **200 MiB / 6459 records past the window without terminating** — only the
   reviewer's own cap stopped it. Equivalence was fuzzed too: 210 random
   adversarial chains × 12 binaries against `model.py`, **0 mismatches**.
   R1 does not merely over-read, it **walks unboundedly**. Once `p`
   passes `end`, `end - p` underflows `size_t` and the loop condition stays true
   forever, so R1 parses memory until it faults — SIGSEGV in both gcc and clang
   plain builds, ASan `heap-buffer-overflow` READ 0 bytes past a 3072-byte region.
   R1h and all four Rust rungs print the model's answer. Delete-the-check controls:
   C → SIGSEGV, unsafe Rust → SIGSEGV, safe Rust → **exit 101, index out of
   bounds**, Verus → will not compile. A missing check in a chained parser
   compounds; carry this to p17+.

5. **p17 — the limit. A program can be provably memory-safe and still leak, and
   we now have one.** (TASK_011.) A suffix-range parser mirroring CVE-2017-7529.
   `start = content_len - s` in **signed** arithmetic, guarded only by
   `start < end`. The served range is `[len - s, len)` — the last `s` bytes — so
   one attacker `u16` selects the harm:

   | `s` | the unchecked read | ASan on R1 | safe Rust |
   |---|---|---|---|
   | `≤ content_len` | correct | — | correct |
   | `content_len < s ≤ len` | the window's own header, **in bounds** | **clean, exit 0** | **reads it identically** |
   | `> len` | before the allocation | `6 bytes before 64-byte region` | panics, exit 101 |

   The two adversarial inputs are **the same 64 bytes with one suffix field 64 vs
   70**. Both C rungs exit 0 with a plausible answer on both.

   **Control 1 — safe Rust with the sign conjunct deleted.** On the leak input it
   prints `1395842226496950656`, **bit-identical to C's value, no panic** (the
   reviewer confirmed identity is structural: an identical 130-byte index
   sequence, derived independently, not a coincidence); on the OOB input it
   panics. So bounds checking kills exactly one of the two harms.

   **The shipped `adversarial-leak` row is *not* an information disclosure, and
   the first write-up of this finding said it was.** Corrected at
   TASK_011_REVIEW. R1 folds 130 bytes over window indices `[0,63]` where the
   checked rungs fold 66 over `[8,63]`; the excess is exactly indices `{0..7}` —
   `nsuf` plus the three suffix `u16`s, i.e. **the attacker's own request table**
   (`inputs/gen.py` literally labels it `ATTACKER DATA`). Structural, not an
   artefact of this input: the regime reads `[len-s, len)` with
   `len-s ∈ [0, body_start)`, so the excess is *always* a suffix of the
   attacker-written header, bounded by `2 + 2*nsuf` bytes. p17 as shipped
   demonstrates **provably memory-safe and functionally wrong** — real, and worth
   publishing — but not disclosure. p17's own `NOTES.md` said the true thing one
   paragraph below the headline that contradicted it.

   **Control 2 — the artefact, and it is one token away from what shipped.**
   The manager's first design (delete the sign check from R5) fails *both*
   obligations, because a proof quantifies over all inputs and that mutant admits
   both harms — **the separation needs a program change, not an input.** The
   engineer then built `start >= -(body_start as i64)`, which verifies with only
   the functional obligation failing. But that guard is **strictly stronger than
   what a bounds check buys**, and calling it "exactly what a bounds check buys"
   was the error that made the leak vacuous. The driver hands the kernel the
   **whole blob**, so bounds checking permits any *slice*-relative index ≥ 0:

   > `start >= -((off + body_start) as i64)`

   That verifies identically — **`9 verified, 1 errors`, functional only; `10
   verified, 0 errors` once the functional spec is stripped** — and it **does**
   disclose. On a two-window probe the output tracks the *victim window's* secret
   (`14940305438379539953` vs `10930790086150322769`), with no panic and no
   `unsafe`.

   **That is the real artefact: a program with no `unsafe`, whose memory-safety
   obligations all discharge, that reads another window's bytes.** It is
   Heartbleed's shape — a lawful read of a neighbour's buffer inside one
   allocation — and it puts a measurement under finding 2: the obligation that
   catches it is the functional `ensures`, never the access obligation. **The
   guard being one token weaker is the whole point**, and it is why "what a bounds
   check buys you" must be written *slice*-relative, not window-relative.

   **Independently reproduced at TASK_012 on shipped-format inputs**, with a
   committed input pair `adversarial-crosswin-{lo,hi}` differing in exactly 28
   bytes of window 0's secret and nowhere else. Every checked rung prints
   `15118011540968580209` on both; C, and the two slice-guarded variants, print
   two *different* values that track the secret. ASan+UBSan clean, exit 0, on
   both files.

   **And the sharpest part was not in the original claim: `safe_naive_sliceguard`
   does it too — plain safe Rust, zero `unsafe`, no proof.** So this is not a
   statement about a trusted accessor or about Verus at all. **It is a statement
   about what a bounds check *is*:** the language's bound is the slice it was
   given, and if the caller hands you the whole blob, "in bounds" spans every
   other client's data in it. Rust enforces that bound perfectly and the leak
   goes straight through it.

   Two design lessons from building the input, both non-obvious and both now in
   p17's `spec.md`: **window 0 must serve something**, because a window returning
   0 pins `acc` at 0 and `k = (acc*nwin) >> 64` is then 0 for ever — **the
   driver's Lemire index has an absorbing state**, and the first design never
   visited the attacker window; and the malicious suffix must keep `abs >= 0`, so
   that every rung including R1 stays in bounds and ASan must stay *silent* —
   which is what makes it a disclosure demonstration rather than a crash.

   **Perf — R3 is free for the fifth pattern in a row** (+32 Ir/call, 0 per
   byte; +0.61% / +0.08%). **Two corrections, and the second is the larger.**
   "Flat" is wrong (TASK_015_REVIEW): it is flat *per byte*, not per call.
   And **`+32` is a ONE-SIDED bound — R3-side only, with R4 held at the shipped
   cell — not p17's R3 cost and not a bound on its safety tax.** p17's unsafe
   side has never been searched in contract; after TASK_023 it is *unverified*,
   not verified-fixed, and the same header-respelling lever moved both p05's and
   p16's. (TASK_018): an in-contract
   respelling — keeping `let start: i64`, `let end: i64` and the literal
   `if start < end && start >= 0` — measures **−19.00 flat against the shipped
   R4** on both bands, and is **byte-identical** (`md5_fn 532201c70eeb…`, 135
   instructions) to the very row TASK_017 had declared out of contract. So p17's
   "R3 is free" survives *per byte* and does **not** survive as `+32`; and the
   R4 side has not been searched in contract, so −19 is an R3-side bound and
   emphatically **not** "safe beats unsafe" (finding 14). Both shipped bands
   happen to have `nsuf = 3`; swept over generated inputs at `nsuf` 1–8,
   `R3ship − R4` runs 18…63 and `R3ship − R3′` is exactly `17·nsuf`. p17 ships
   **no sweep inputs at all**, which is how a two-point constant got published as
   a law — `.memory`'s own residue rule ("sweep two full cycles, never sample two
   points") applied and was not followed. A shipped p17 sweep is owed. And **R2−R4 = 4.2500 Ir per folded byte, reproducing
   p16's swept constant on a completely different kernel** — *exactly*, in fact:
   the delivered 9.9991 / 5.7491 were contaminated by the driver's final
   `println!` (its digit count varies per input); the zero-residue lag-4 pair
   gives **10.0000 / 5.7500 exactly**. The constants reproduce *better* than
   claimed — so
   4.25 is a property of *rustc's checked indexed byte fold*, not of p16. Two
   further reproductions: gcc's default-vs-`-funroll-loops` deficit (2nd pattern —
   `-funroll-loops` takes gcc past clang again), and gcc's default rolled fold at
   **exactly 8.0000 Ir/byte**, the rolled-unchecked constant p16's review derived.
   Decomposition again puts 98.5% / 99.8% of R2's gap in the inner byte fold.

   **Two manager predictions killed by measurement**, both worth keeping:
   `i128` index arithmetic costs +4.0000 Ir/byte, but **signedness itself costs
   4 Ir per *call*, flat — 0.17% of the gap.** "The cost of the check is the
   conversion, not the comparison" is **false**.

   Wall clock: every rung folds a byte in **0.784–0.791 ns**, 0.9% spread across a
   73% `Ir` gap. **p17 quotes no cycles/byte, and that is correct** — a manager
   instruction to quote 3.02–3.05 was overturned at TASK_012 with the measurement
   that killed it. `scaling_cur_freq` is unusable (it reads 800 MHz under load),
   *and* the dependent-chain probe is not reproducible across sessions on this
   shared box: 3.80–3.89 GHz in one, 2.55–2.86 GHz in another, same code, same
   cores. The same ns figure is 2.2 or 3.1 cycles/byte depending on when you ask.
   **ns is a measurement here; cycles is an inference.** See
   `.memory/00-environment.md`.

6. **p05 — on a vectorised loop the cost is `O(nrow)` for two *spellings* of safe
   Rust and *negative* for a third. Safe Rust is not slower here; two ways of
   writing it are.** (TASK_013, corrected at TASK_013_REVIEW, and its headline
   **refuted at TASK_014_REVIEW** — see the "R3 is not free" bullet below, which
   was wrong. The first write-up also said "the check costs 0.0000 Ir/element"
   and "the wider the lane the cheaper safety gets"; **the first is true only of
   the steady state and the second is refuted by measurement.**)

   2-D index flattening, `a[i*ncol + j]`, associative inner sum so the loop can
   vectorise, Horner once per row.

   **What is exactly true.** In the vectorised steady state the per-element rate
   is **1.375000** (= 11/8, an 11-instruction body over 8 elements) for c-clang,
   safe-naive, safe-tuned and unsafe **alike**, six decimals, both bands; c-gcc
   `1.062500` (= 17/16). Five rungs emit identical mnemonics. Per *element*,
   inside the vector body, the check really is free.

   **Where the check actually went — the mechanism, supplied at review.** It is
   hoisted into a **22-instruction per-row trip-count computation** (a
   `cmova`/`cmovb` min-max chain computing `N = min(ncol, len − rowbase)`), and it
   **survives in the scalar epilogue** at 8 Ir/element against R4's 5. So the cost
   is `O(nrow)`, not zero. **"Per element" is a marginal derivative, not an
   average** — the average gap on shipped inputs is ~34%.

   **`f(0) = 84` is explained**, and it is the sharpest small result here:
   `mov $0x8,%r11d ; cmove %r11,%r8` — **a remainder of zero is forced to a full
   vector width**, because R2's loop is multi-exit and must keep a scalar
   epilogue. `84 = 29 + 64 − 11 + 2`. Every power-of-two `ncol` pays a full extra
   vector iteration it does not need.

   **The model has zero fitted parameters.** Derived at review from the listings
   alone: `R4 = 37 + nrow·(27+11q+5r)`, `R3 = 46 + nrow·(33+11q+5r)`,
   `R2 = 72 + nrow·(56+11V+8e)`, reproducing every measured point to the
   instruction. The published `35 + nrow·f(ncol mod 8)` form is the same thing with
   the structure hidden; `f` absorbs nothing. **Domain: `ncol > 8`** — the model is
   false below that (34755 measured against 41699 predicted at 496×8).

   **Four corrections that matter, all measured:**
   - **Wider lanes make safety *worse*, not better.** At AVX2 the gap at
     `ncol ≡ 0 (mod 32)` is **14601 Ir/call against SSE2's 4487**, ratio 1.42× →
     **4.58×**, and safe Rust is **absolutely slower** (18674 vs 15177). The peel
     is VF elements long, so it grows with the lane.
   - **The hypothesis is not inverted in general — it holds at `ncol = 8`.** R2's
     vector guard is `N >= 9` where R4's is `ncol >= 8`, so there the check **does**
     block vectorisation, and costs **2.94×**. p05 has both regimes in one kernel.
   - **R3 is *not* free here — and this bullet survived a retraction and a
     re-instatement, so read the whole of it.** Within p05's **declared
     contract**, shipped R3 pays `6·nrow + 9` Ir/call against shipped R4:
     +16.7% at 496×8, +4.7% at shipped `large`, an `O(nrow)` cost. **That number
     stands.**
     What does **not** stand is reading it as *what safe Rust costs*.
     TASK_014_REVIEW retracted the bullet on the ground that
     `data.chunks_exact(ncol)` — a spelling this file's own R3 row named — beats
     **R4** by `nrow − 7` on every one of 150 inputs. TASK_015_REVIEW then found
     that **`chunks_exact` is forbidden by `patterns/p05-index-flatten/spec.md`
     itself** (it deletes the `i*ncol + j` multiply, which *is* the pattern), as
     is the running row pointer used by the R4′ control that answered it. So
     both of the spellings that overturned this bullet are **out of contract**,
     the retraction was wrong, and the number is reinstated — *as a
     contract-relative number*.
     Keep all three facts together or the bullet misleads again: the cost is
     real at the declared idiom; the declared idiom is a real restriction; and
     outside it the gap moves by more than the gap.

     **Two numbers produced while chasing this are themselves refuted; do not
     quote either.** TASK_015's out-of-contract R4′ control gave *"+11.00
     Ir/call, flat in `nrow`, `O(1)` not `O(nrow)`"* as p05's idiom-matched
     safety number. One more unsafe round — replacing the loop counter with the
     canonical C test `while rp < end` — makes it **`nrow + 9`**, swept exactly
     over all 144 committed blobs with zero residual, and a second, textually
     unrelated unsafe spelling lands on the identical figure. **The `O(1)`
     conclusion flips on the first thing a reader tries.** Likewise p16's
     `nrec + 3` was a three-point fit; swept over 68 blobs it is **7 flat at
     `vlen ≡ 0 (mod 4)` and `7 + nrec` in the other three residue classes** —
     the audit's three points all sat at residue 0.

     **The `chunks_exact` `div` is real; its timing consequence is not.**
     `chunks_exact` with a runtime chunk size emits a hardware `div` per call
     (`len − len % chunk_size`), which callgrind prices at **1 instruction** —
     keep that as a rule (`.memory/03-measurement.md`). But the ns evidence for
     it does not reproduce: two 31-rep interleaved sessions disagree on cell
     ordering and on which cell has the worst spread, and between-run drift
     (~4%) exceeds every inter-cell `Ir` difference. And `split_at_checked`
     consumes the slice with **no `div` and is 4 Ir cheaper still**, so the
     `div` is one spelling's defect, not the idiom's.

     Two smaller corrections to TASK_014_REVIEW's write-up: its static counts mix
     conventions (105 is `n_fn`; 171 and 97 are `n_raw` — matched, 105/168/87 or
     109/171/97), and **shipped R3 also has zero `cmov`** — the five are R2's
     alone.
   - **4.2500 is not "the check".** The `-unroll-count=1` no-op control *does*
     exist here (bit-for-bit identical R2, `md5_fn 76d7c2380278`), and gives
     rolled+checked 7.0000, rolled+unchecked 5.0000, novec-unrolled 2.7500 →
     **4.25 = 2.00 check + 2.25 unroll**, the *identical split* TASK_007_REVIEW
     derived on p16. So the third reproduction is of the constant **and its
     decomposition**, which is stronger than the constant alone.

   **Why the check cannot be eliminated — and what that is worth.** R2's panic is
   dead on every execution, and LLVM keeps it: `nrow*ncol <= avail ⟹ i*ncol + j <
   avail` is **nonlinear**, which is exactly the obligation R5 discharges with
   `lemma_mul_inequality` and one `by (nonlinear_arith)`. Linearising that guard
   in an isolated compilation deletes the entire per-row apparatus — 5 `cmov` → 0,
   166 → 125 instructions, the `cmp $9` and residue `cmove` gone, an unchecked
   epilogue (TASK_014_REVIEW, `probe2.rs`, which also reproduces the shipped
   mechanism independently). So nonlinearity is the blocker **for this kernel**.

   It is **not necessary in general**: p08 keeps a provably-dead `copy_within`
   range check whose implication is purely *linear*, at 26.00 Ir/call, because
   the fact it needs is **relational** across the loop induction variable rather
   than nonlinear — LLVM's value-range machinery is per-value. Restating the
   relation inside p08's loop deletes the check outright (3 panic refs → 0).

   **And the cost is not intrinsic to safe Rust** — see the retracted bullet
   above. What the `29 + 3r` per row prices is the *indexed and the
   manually-resliced spellings*, not the missing lemma.

   Two further caveats, both measured at TASK_014_REVIEW. The linearisation
   counterfactual does **not** survive the shipped binary build: as a real p05
   cell, LLVM's induction-variable simplification re-derives `i*ncol` and the
   linearised R2 measures **2366 Ir/call against R2's 2081** — *worse*. And the
   whole question is moot for the headline, because a spelling with no lemma at
   all beats R4.

   **"The `29 + 3r` Ir per row is the price of the optimiser failing the lemma
   the proof proves"** — retracted at TASK_014_REVIEW, **partially reinstated at
   TASK_015_REVIEW**, and the final status is: *true of this kernel at its
   declared idiom, and not a statement about safety in general.* The cost is
   real (`6·nrow + 9` for shipped R3, more for R2), the nonlinear implication
   really is what blocks elimination (linearisation deletes the whole per-row
   apparatus), and the counterexample that overturned it used a spelling
   `spec.md` forbids. What the sentence may never do is generalise from "this
   kernel, written this way" to "safety costs this" — that is the step
   finding 14 shows is not available.

   **The sentence is REINSTATED, restricted to the row-scaled term** (TASK_021,
   adjudicated at TASK_021_REVIEW). Exactly these words and no wider:

   > **"On p05, the `O(nrow)` part of the in-contract safety tax is the price of
   > the optimiser failing the lemma the proof proves."**

   True of *this kernel*, *this declaration* and *this toolchain*, and of the
   **row-scaled term only**: the in-contract respelling removes exactly one
   instruction per row — `add %rsi,%rax`, the `add` that makes the row base
   buffer-absolute — and the five that survive are the reslice's bounds check,
   whose deletion needs `(i+1)·ncol <= nrow·ncol`, the nonlinear fact R5
   discharges with `lemma_mul_inequality`. **Not** true of the constants, which
   move in *both* rungs and by different amounts, and **not** a statement about
   safety in general.

   **p05 has no minimum, and this project should stop publishing one.** Three
   have now been published and all three refuted, each by the first lever the
   next agent pulled: `5·nrow + 6` (TASK_021) → `5·nrow + 11` (TASK_021_REVIEW,
   which respelled the header) → `5·nrow + 13` (TASK_022, which deleted a
   semantically redundant `nrow == 0 || ncol == 0` early return, worth 7 Ir/call
   flat against shipped R4). Each was reached by **several independent `md5_fn`
   bodies**, so — and this is the transferable lesson — **"reached by many
   spellings" is not evidence of a floor.**

   Worse, the quantity itself is unsound: **`min(R3 found) − min(R4 found)` is
   the difference of two upper bounds and bounds nothing in either direction.**
   Two measured consequences on p05:
   - the same edit is **−2 on R4 and +1 on R3**, so the constant does not cancel;
   - `5·nrow + 13` **exceeds** the published `6·nrow + 9` for `nrow < 4`, so a
     "minimum" can sit above the published number on 3 of 14 `nrow` values.

   **What to publish instead — and BOTH ENDPOINTS OF THE ANSWER THIS FILE GAVE
   ARE THEMSELVES REFUTED** (TASK_027_REVIEW, seven Verus twins). The pair
   interval ~~`2·nrow − 2 … 6·nrow + 20` = 36…134 / 128…410~~ was built from a
   *dearest* R4 (`r4_dataslice`) and a *cheapest* R4 (`c4_hu16_nz`) that **are
   not p05 rungs**: p05 pins `identity: unsafe ≡ verus, O3 exact` like every
   other pattern, and at the pinned vstd

   - `c4_hu16_nz` needs `read_unaligned`, `as_ptr` and `add` — all three
     `is not supported`; it verifies only with **one new trusted item**, exactly
     the cost `r4_hdr` was disqualified for on p16;
   - `r4_dataslice` needs `from_raw_parts` — `is not supported`;
   - **and the lever is blocked as a *lever*, not as one spelling**: the
     `try_into`-array route (`TryFromSliceError`) and the `from_le_bytes` route
     are unsupported too. There is no admissible respelling of p05's header read.

   So ⚠ **"p05's R4 moves 7 flat (TASK_022)" HAS NO RUNG BEHIND IT** — the same
   defect as p16's `u_c32`, on a figure that is load-bearing in this file, in
   `RECAP.md`, and inside the hashed `why` of **all six patterns**. The cheapest
   *measured and admissible* p05 R4 is **the shipped cell, at 0**.
   ⚠ **Say "the only R4 SHOWN admissible", not "seven admissible spellings"**
   (TASK_028). Six further round-1 variants measure 0 against the shipped R4 but
   **were never put through Verus**, and at least two of them (`r4_rowslice`,
   `r4_dataptr`) use the very `from_raw_parts`/`add` the logs reject. It moves no
   endpoint — they all measure 0 — but the claim we are entitled to is one
   verified cell, not seven.
   Substituting the admissible class into p05's own published laws gives
   `5·nrow + 6 … 6·nrow + 13` = **101…127 / 331…403**, width `nrow + 7` = 26 / 72
   — which is *exactly* the R3-side-only span of 21% / 18% that the pair interval
   was introduced to replace. **p05's R4 side has never moved by a single
   admissible instruction.**
   The one real bound is untouched: **hold R4 at the shipped cell**, and
   `6·nrow + 9` bounds `inf(R3) − R4ship` from above, with `5·nrow + 6` tighter.

   ~~**And an admissible pair exists whose tax is exactly 0**~~ (`nrow = 1`,
   `ncol ≢ 0 mod 8`; `sweep-r1c30` measures 0.00). **Withdrawn** — that pairing's
   R4 is `r4_dataslice`, which is not a rung. Do not quote "p05 has a free
   pairing".

   ⚠ **One residue is UNBUILT and it is the open question here.** The `−2` half
   (delete the redundant zero-guard, keep the shipped header) verifies at **zero
   TCB** — `13 verified, 0 errors` — but **all 26 of TASK_022's round-3 variants
   pair that deletion with `read_unaligned`**, so no admissible p05 R4 reaching
   `−2` has ever been compiled. `−2` is an inference (`−7` minus `−5`), never a
   measurement. This is the exact analogue of p16's never-built hand-unrolled 32×
   fold: **on two patterns now, the question "does the admissible R4 class move at
   all?" is open because nobody built the one spelling that would answer it.**

   **The number is also reading-dependent**, which an earlier write-up stated
   unconditionally: p05's `required[1]` read as p16's is gives one figure, the
   strict reading another. The *qualitative* claim survives both. See
   `patterns/p05-index-flatten/NOTES.md` §14.

   **Two things that stand unchanged:** `Ir` converts to time on this kernel
   (+34.4% `Ir` → **+32.9%** wall — the review's own remeasurement; the delivered
   +30.5% was over-precise), confirming a prediction p16's `NOTES.md` made that a
   kernel with independent inner iterations would convert where its latency-bound
   Horner chain did not (+72% → +0.27%). And the `u32` row accumulator deviation is
   **sound, and better justified than the delivery argued**: `ncol <= 65535` × `u8`
   caps a row sum at 16 711 425 < 2³², so `u32` and `u64` are equal on *every
   representable input*, confirmed by identical checksums.

7. **p08 — the first structural Rust win, and a bug that executes without
   consequence.** (TASK_014, reviewed at TASK_014_REVIEW.) A fixed buffer shifted
   right to make room; R1 spells the move `memcpy`, R1h `memmove`, and **that one
   token is the whole difference**. Every rung carries the same bounds guard, so
   this is the project's first result that is not about a bounds check.

   **`memcpy` *is* `memmove` on this libc.** glibc 2.39 x86-64: one function, one
   address, with a `dst-src < n → backward copy` branch — and the `_chk` forms
   alias too (`__memcpy_chk == __memmove_chk`), which matters because gcc's
   fortified cells call those. So the UB **executes and is unobservable**: 320
   runs across every size regime with zero divergence, all 32 builds print the
   model's answer, exit 0, no diagnostic. **R1 ≡ R1h at 0.00 Ir/call** — the same
   machine code with one different call target. That is a **libc** property, not
   a language or compiler one, and must never be quoted as "memmove is free".

   **What sees it.** ASan's `memcpy-param-overlap` fires, exact to the byte
   (`d=2045` fires, `d=2046` silent) — **but not when the call site is
   fortified**, because the check lives in the `memcpy` interceptor and ASan does
   not intercept `__memcpy_chk`. The discriminator is `_chk`, **not gcc**: clang
   at `-D_FORTIFY_SOURCE=3` is blind too. Miri catches the Rust mutant
   (`copy_nonoverlapping called on overlapping ranges`), the first time the
   gate's Miri stage has been aimed at aliasing UB rather than spatial. valgrind
   memcheck is unavailable on this box entirely.

   **The structural claim, stated precisely.** Safe Rust cannot express the bug —
   the borrow checker rejects it at compile time, and rustc even suggests
   `split_at_mut`. There is **no runtime check** and therefore no cost to
   measure. `unsafe` re-opens it exactly via `copy_nonoverlapping`. **What R5
   does *not* do is rule it out**: substituting `copy_nonoverlapping` into the
   trusted body verifies `11/0` shipped and `15/0` under the twin, invisible to
   Verus, to the twin, to the contract pin and to stages 5c/5c-req. Only the O3
   identity pin against R4 and Miri catch it. A proof of a `requires` is not a
   proof that the trusted body honours it.

   **The honest counterweight, which must ship with the claim**: safe Rust
   prevents the *UB*, not the *wrongness*. The forward-loop control compiles,
   does not panic, and silently replicates the buffer.

   **R3 == R4 flat at 26 Ir/call** (a dead, purely linear range check LLVM keeps),
   so R3 is free again — but this is the **sixth** pattern only if p05's shipped
   R3 is counted as the failure, and after TASK_014_REVIEW's blocker the honest
   count is that **no pattern has yet shown safe Rust paying an unavoidable
   per-element price.** Do not write "p08 restores the streak"; there was no
   break.
   ⚠ **That last sentence was true when written and is now ANSWERED — see finding
   8 (p07).** Safe Rust pays `6.0000` Ir per probe on a kernel with no inner loop,
   and the fraction rises in both `n` and `nq`. The six patterns before it shared
   a loop shape, and that is what they were measuring.

8. **p07 — the first pattern where R3's tax has NO axis along which it
   amortises, and the answer to "no pattern has yet shown safe Rust paying an
   unavoidable per-element price" directly above.** (TASK_026, reviewed at
   TASK_026_REVIEW; headline confirmed, the manager's framing of it refuted.)

   Binary search: `Θ(log n)` probes, **no inner loop to amortise a per-call
   constant over**. Matched-spelling laws, exact integers, verified **out of
   sample** on 30 fresh blobs with an independent probe-count implementation
   (30/30 exact), and re-derived from the listings rather than fitted:

   ```
   R3 − R4 =  9 +  4·nq +  6·probes      (one two-sided slice range check)
   R2 − R4 = 36 + 11·nq + 11·probes      (four one-sided index checks)
   probes  = nq·⌈log2 n⌉  (data-dependent; use the EXACT count replayed from the
                           file — ⌈log2 n⌉ leaves 600–1250 residuals)
   ```

   **R3's share of kernel `Ir` rises in both `n` and `nq`**: 42.53% → 46.63% over
   `n` = 7 … 16 385, asymptote `6/(12 + f_lo)` ∈ **[46.15%, 50.00%]** — 47.99% on
   the shipped 50/50 workload. **The asymptote is a property of the kernel AND the
   query distribution**, which is why it must be quoted with the workload.
   **Confirmed across six deliberately different workloads** (all-hit, all-miss,
   all-below, all-above, clustered, shipped), monotone rising in every one.

   **Why this is a first, stated precisely.** p16/p17's R3 tax is a per-**call**
   constant — 0.00000 Ir/byte swept, because the reslice sits *outside* the fold
   loop. p05's is `O(nrow)`, which vanishes along `ncol`. **p07's vanishes along
   nothing**, because there is no inner loop for it to be hoisted out of. That —
   not "safety is expensive here" — is the finding, and it says the six earlier
   answers were a property of the **loop shape** those kernels shared.

   ⚠ **It is NOT "the first counterexample to safety is cheap".** The manager
   wrote that and it is refuted by *this file*: finding 4 carries p16's swept
   **R2** tax of 4.25 Ir/folded byte, whose fraction also rises (toward
   `4.25/5.75` = 73.9%), reproduced on p17; finding 6 carries p05's `O(nrow)`
   **R3** tax. **The R3 scoping is the entire claim.**

   **Two structural results beside it.** The proof is 10/0 first try, and
   `kernel` costs **3** obligations where p05's costs 5 — every multiply is by the
   literal 4, so p07 has *zero* nonlinear arithmetic. And the half-open spelling
   (`hi = n`, `while lo < hi`, `hi = mid`) **removes** the `usize` underflow
   obligation rather than discharging it: **the spelling that makes the proof
   trivial is the one that makes the bug impossible**, at zero cost in
   instructions, obligations or TCB. The inclusive-`hi` spelling ships as a
   control and SIGSEGVs on p07's own `small.bin` — the underflow fires on
   *well-formed* input, any key below `elements[0]`.
   p07's R4 side is **degenerate, third pattern running**: `r4_ptr` measures
   −460/−1605 and its twin dies on *"dereferencing a raw pointer is not
   supported"*, so it is not a rung. Fixed-R4 bound `+3017.14 / +10019.42`;
   in-contract R3-side span `2554.45…3017.14 / 8412.35…10019.42`.

   ⚠ **Do not quote p07's R2 `ns` numbers or the "8× conversion factor" — they
   have NO SIGN** (TASK_029, 30 layouts; mechanism identified at
   TASK_030_REVIEW). Code layout selects between two modes and R2's comparison
   flips across them: **+26.42% at one residue, −0.93% at the other**, perfect
   separation 30/30. No number of reps recovers a sign from that.
   **The mechanism is the 32-byte instruction-fetch / DSB window grid** — `win32`
   (the loop body spans one more fetch window) or `jcc32` (a loop branch crosses a
   32-byte boundary; this box carries Intel's **SKX102** JCC erratum). Both are
   computable statically with zero fitted parameters and separate every mode
   measured, including on 20 **pre-registered** fresh layouts. "Bit 4 of the
   kernel address" is a *proxy* that works only because kernels are 16-byte
   aligned. Full treatment: `.memory/03-measurement.md`.
   **R3's counterweight survives by mode-matching** — but note that *dominance*,
   which an earlier version of this entry cited beside it, is **retracted**: it is
   defined against an extremum and does not converge (`.memory/03-measurement.md`).
   Use mode-matched comparison and pairwise `P(A > B)`.
   ⚠ **p07's R4 rung also has an unexplained 8–9% layout band** on `small`,
   reproducible across passes and CPUs, separated by no bit and unmoved by
   `jcc32`. It is larger than several published gaps and nothing accounts for it.

9. **p11 — a library difference, a spelling difference and a safety cost,
   separated; and a bounds check costs 2 or 3 Ir/byte depending on what the loop
   already holds.** (TASK_033, reviewed at TASK_033_REVIEW — headline confirmed
   by independent re-measurement, two majors and six minors against the prose,
   **no blockers**.) Family B's first pattern, and the first kernel whose **loop
   bound is not known before the loop**.

   **The three-way decomposition, which is the pattern's point.** All rates
   `body_len / K` off the listing; `vector_regs` empty on 8 of 8 kernels:

   | scan spelling | lowers to | Ir/byte |
   |---|---|---:|
   | C `strlen` | glibc IFUNC → **AVX2** | **0.078125** (measured 0.0788) |
   | C `memchr` (R1h) | AVX2, **but must also test its count** | **0.1023** |
   | `CStr::from_bytes_until_nul` (R3) | `core::slice::memchr`, SWAR 2×`u64` | **0.937500** |
   | `iter().position()` | scalar byte loop | 5.00000 |
   | R4 `get_unchecked` | scalar byte loop | 6.00000 |
   | R2 indexed | + `lea;cmp;jae` | 9.00000 |

   **12.0× is the library. 5.3× is which Rust spelling. 3.00000 Ir/byte is the
   bounds check.** Only the third is a safety number, and it is at matched
   spelling — the two loop bodies differ by exactly `lea; cmp; jae`.

   ⚠ **THE NEW CONSTANT, and it generalises past p11: a bounds check costs
   `2.00000` Ir/byte when the loop's induction variable already holds the address
   being checked, and `3.00000` when it does not — and which one you get is
   decided by the loop's OTHER exit test.** p11's fold has `add %rdx,%rax` hoisted
   outside the loop (bound test = `cmp; jae` = 2); its scan keeps `%rbx`
   window-relative *because its own exit test is `q < len`*, so the check must
   `lea` first = 3. One kernel, one compiler, matched spelling, and confirmed by a
   one-loop-at-a-time control: scan `(4730−1850)/(24·40) = 3.00000`, fold
   `(6190−2110)/(24·40) = 4.25000`, both exact, residual a constant −39/call.

   **`4.25000 = 2.00 + 2.25` is now reproduced on a THIRD kernel with the split
   intact** (p16, p17, p11), and on p11 by an isolating control rather than a
   whole-kernel delta. Swept law: `R2 − R4 = 7.25000` Ir per string byte
   `= 4.25000` (fold) `+ 3.00000` (scan), zero residual over 61 points, all four
   residues.

   **The largest instance of the R4-by-permission result** (see the paragraph at
   the top of this file): `r4_cstr` would be **−17 526 Ir/call, −35% of the kernel
   on `large`**, and its twin is rejected with **four** `is not supported`
   (`CStr`, `FromBytesUntilNulError`, `from_bytes_until_nul`, `to_bytes`). **The
   safe class reaches `core::slice::memchr` at zero TCB; the unsafe class cannot
   reach it at all.** The hand-written SWAR alternative is now *measured*
   inadmissible too — `from_le_bytes` `is not supported` on p11's own twin, and it
   is separately forbidden by p11's `idiom.forbidden[1]`. R3−R4 changes sign at
   string length 17–18, at `core::slice::memchr`'s 16-byte threshold, and
   `small`/`large` are specified on opposite sides of it.

10. **p03 — the safety tax IS the price of the optimiser failing the invariant
   the proof proves, on a LINEAR fact; and it is not a fact about Rust.**
   (TASK_036, reviewed at TASK_036_REVIEW: the causal claim **confirmed** with
   three negative controls, two blockers and two majors against the prose.)

   **The control.** `m_clamp` = R3 plus a *dead* `if sp > STACK_CAP { return 0; }`
   — R5's own invariant handed to LLVM. Safe goes **17 → 13** Ir per executed pop,
   unsafe **14 → 13**, and **the gap goes to exactly zero on both sides**, zero
   fitted parameters, max residual 0.000000 over 19 blobs. **Three negative
   controls say it is the INVARIANT and not range propagation in general:**
   `sp > 1000` is **byte-identical to shipped R3** (nothing); `sp > 65`, one past
   the invariant, leaves the check standing *and* is dearer; a non-dead early
   return that says nothing about `sp` is dearer with the check standing.

   **This generalises p05's reinstated causal sentence (finding 6) from a
   NONLINEAR fact to a linear one** — nonlinearity was p05's whole stated excuse
   for why LLVM could not do it. **But two qualifications are mandatory and both
   were measured:**

   1. ⚠ **It is NOT Rust-specific.** Give the C rung a manual bounds check on the
      pop read and **clang keeps it at 4.00000 Ir per executed pop, exactly**;
      gcc keeps it too. Hand either the identical clamp and **both delete 100% of
      it**, with the clamped-with-check binary **byte-identical** to the
      clamped-without-check one. **Two independent middle-ends fail the same
      lemma the same way**, and gcc shares none with rustc. Write it as *"any
      compiler asked to prove this"*, never as *"safe Rust"*.
   2. ⚠ **LLVM does eventually DERIVE the fact.** In `m_clamp`'s output the clamp
      is *gone* and its `return 0` semantics is not preserved on the `sp > 64`
      path — LLVM concluded that path unreachable, i.e. it did derive
      `sp ≤ STACK_CAP`. What it cannot do is find the fact **unseeded**. So this
      is analysis **seeding / phase ordering**, not an inability to prove the
      lemma — a different failure from p05's, where the fact itself is nonlinear.

   **The laws** (max residual 0.0000, 89 blobs, three bands; the pooled design is
   rank 5/5 and **every pair of bands is rank-deficient**, so only the pooled fit
   identifies the terms):

   | quantity | law |
   |---|---|
   | `R1h − R1`, the emptiness check in C | `2.00000 · xpop`, exact, gcc and clang identical |
   | `R3ship − R4ship` | `3.00000 · xpop + 5` |
   | on push / dropped push / empty pop | 0.00000 / 0.00000 / 0.00000 |

   ⚠ **`3.00000` is the SHIPPED SPELLING's rate, not the class's.** In contract
   the class reaches **1.00000** (`assert!` in the pop arm) and **−1.00000**
   (`assert!(sp <= STACK_CAP)` at the loop head, which is *byte-identical* to
   `m_clamp`). p03's in-contract R3-side span is **−113 … +5110** on `small` and
   **+212 … +17237** on `large`, and **the cheapest spelling differs between the
   two blobs** — one more instance of "a cheapest-found figure must name its
   input".

   ⚠ **The "same basic block" mechanism is REFUTED.** Hoisting the push guard into
   the loop head (`let can_push = sp < STACK_CAP;`) is **byte-identical to shipped
   R3** — LLVM normalises the hoist away and still deletes the check. **The real
   discriminator: the push guard supplies the UPPER bound the access needs,
   locally; the pop guard supplies only the LOWER bound, and the upper must come
   from the loop-carried invariant.** Confirmed by two in-contract controls
   (`if sp > 0 && sp <= STACK_CAP`, and the assert in the pop arm) which both go
   to 13–15 with the check deleted.

   **The bug**: `sp−1` at 0 wraps to `stack−1`, eight bytes below the array and
   **inside the kernel's own frame** — it does not fault, it returns a wrong
   answer, and **R1's checksum is not reproducible across runs** (bit-stable only
   under `addr-no-randomize`). A **pointer**-disclosure shape, distinct from p17's
   data disclosure. UBSan beats ASan here because the array has a static type. A
   sustained underflow faults at exactly the 8 MiB `ulimit -s`.

   **Verus 9/0 on the first run**, Z3 taking `sp <= STACK_CAP` across the
   attacker-chosen branch in one invariant clause — no lemma, no
   `nonlinear_arith`. TCB 10 lines / 5 items. And **the gate earned its keep on a
   trusted item**: a tautological `v@.len() == 64` on a `&[u64; 64]`, caught by
   5c-twin's per-conjunct deletion probe — the first time that TASK_010 refinement
   has fired on shipped code rather than a constructed mutant.

11. **p09 — one character, in one position, is the difference between a bug
   everything catches and a bug nothing catches.** (TASK_038, reviewed at
   TASK_038_REVIEW: invisibility claim **confirmed against four vacuity attacks**;
   one blocker and five majors against the prose, two of them project-wide.)

   ```
   words[q >> 6]   shipped
   words[q >> 5]   caught by memory safety ALONE, on every input:
                   rustc's bounds check, ASan, Miri, and the proof's precondition
   words[q >> 7]   caught by NOTHING:
                   no bounds check, no ASan/UBSan, no Miri, no memory-safety proof
   ```

   `q >> 7` is `q/128 ≤ q/64`, so under the guard `q < nbits` it is **always a
   legal word index** — and Verus proves it universally with one ghost line:
   `m_shift7_msonly` **19 verified, 0 errors**, `m_shift7_spec2` **20 / 0** once
   the spec moves to match. It costs **zero instructions** (6691.70 vs 6692.30),
   `n_fn` is **identical at 102**, and — measured at TASK_039 — **the whole
   368-byte R4 kernel differs in ONE BYTE** (offset 156, `06` → `07`); the
   103-instruction disassembly differs only in `shr $0x6` → `shr $0x7`. All five
   builds print the same wrong answer on **`small`, p09's headline blob**, not
   only on thin windows; ASan+UBSan at the gate's own flags are silent on **every**
   input including `thin.bin`, and Miri is `exit=0 UB=no`.
   ⚠ **And it is a class, not an instance — ≥ 9 members.** The obligation reduces
   to `C·(nwords−1) + 8 ≤ 8·nwords`, so **every shift digit above 6 and every
   scale below 8 is in bounds**. Second member measured: `4 * (q >> 6)` — again
   one differing byte (the SIB scale), wrong in all three rungs on every blob,
   Miri clean, and `m_scale4_msonly` verifies **18/0 with no ghost line at all**,
   where `q >> 7` needs one `by (bit_vector)`. `q >> 7` ships as the headline only
   because it is the one member in `q >> 5`'s own character position.
   ⚠ **This is the example to quote, not `q & 31`** — which is a *two*-character
   substitution costing **+32% on R4**. p09 shipped calling both "one-character
   bugs"; that is wrong on both counts.

   **The probe is not blind**, which is what makes it a result: `_msonly` survived
   four vacuity attacks — `assert(false)` in three separate places (17/1, 18/1),
   and deleting the guard (`precondition not satisfied`) — so a memory-safety-only
   proof that still catches R1's spatial bug on the same file discharges `q & 31`
   and `q >> 7` clean.

   **And the obligation that fires is a VERIFIED item's, not the trusted
   accessor's.** It is `load_u64`'s `p + 8 <= buf@.len()`; deleting
   `buf_get_unchecked`'s `requires` changes nothing (18/0 → 18/0, 19/0 → 19/0,
   17/1 → 17/1), and the trusted clause is **shadowed, not dead** (delete the
   decoders' and it fires inside them). p09 is the **only pattern with decoder
   wrappers carrying their own `requires`** — so this is the first time the
   memory-safety obligation sits **outside the TCB boundary**, which is a better
   result than the one it shipped. **TCB is 7 lines / 4 items** (the gate's own
   count), the second-smallest here — not the 12 its `NOTES.md` declared.

   **The three checks decompose with ZERO free parameters** — every coefficient is
   a loop-body instruction count off the listing, and out of sample the fit
   predicts `large` (3.5×–4.6× outside every band) to within **1.13 Ir of 73404**,
   with `R3 − R4` predicted **48885.00** against measured **48885.00**.

   ⚠ **The reslice hazard, conditional and checkable, and it is the whole of p09's
   R3 > R2 inversion** (the first in this project). LLVM loses the 8-byte
   load-merge idiom on exactly **one of eight loops**: `reslice` **+** a
   data-derived index **+** a multi-byte decode at it. R2 keeps the merge on the
   *same* shift-derived access. Decomposed: `+21` lost merge, `+1` spill, `−5`
   cheaper query checks the reslice buys = `+17` net. **Half of p03's
   seeding-style win here is the restored load idiom, not deleted checks**, and
   `q & 31`'s R4 cost is the *same* mechanism (it narrows the load to 32 bits and
   splits the merged `mov` into 4+2+1+1) — which unifies p09's two cost stories.

   **p03's seeding control does not transplant**: a dead clamp on the *word index*
   is **+461 dearer** and deletes nothing, in C as well as Rust; the same clamp on
   the **byte offset** deletes 49% of the kernel; one that says nothing is
   byte-identical to shipped R3. **The inference LLVM fails is the composition
   through the multiply, not the shift.**
   `q >> 6` and `q / 64` are **identical to rustc, clang and gcc** — the
   `forbidden` entry moves no number and is kept only because it makes "the shift
   implements the division" a real Verus obligation.

12. **p12 — the bulk-copy lowering needs BOTH ends of the copy free of a
   per-iteration check; and "safe beats unsafe" here is a fixed-R4 artefact.**
   (TASK_040, reviewed at TASK_040_REVIEW: two blockers, three majors — the
   headline mechanism **confirmed and sharpened**, two published numbers moved.)
   First bug here that is a **write** safe Rust cannot express; first time
   `c-gcc` and `c-clang` differ in **behaviour** rather than instruction count.

   **The mechanism, confirmed by the control p12 did not build.** A per-iteration
   bounds check kills the `memcpy` lowering of a hand-written byte loop — and the
   recovery is about **where the check is**, not about `copy_from_slice` carrying
   its own bound: a *safe byte loop* over `&mut dst[dlen..dlen+slen]` / `&w[p..q]`,
   with no bulk call anywhere in its source, lowers to `memcpy@GLIBC_2.14`.
   ⚠ **But "on the destination" is not the rule.** A cell with the destination
   *unchecked* and only the **source** per-byte checked also loses the lowering.
   **The bulk lowering needs both ends free of a per-iteration check.**
   Consequence: `R2 − R4` has **no per-byte law**, and the reason is precise —
   at constant `nacc` the R2 side is **exactly linear at 24.75 Ir per copied
   byte**; the non-law is entirely **R4's `memcpy` size dispatch**.

   **The capacity check's SIGN is a middle-end property** — `−4.00` Ir/string
   under gcc, `+2.00` under clang and rustc — and gcc's mechanism is off the
   listing: with no dominating branch, gcc computes the copy length *and* the
   `dlen` update **branchlessly** (`setae`, spill, two `cmove`) around an
   unconditional `call memcpy`; the capacity test supplies the branch, the work
   moves into a guarded out-of-line block, and the `cmove`s vanish.
   Out of sample on `large`, 3.5× outside the band, the laws predict
   **−125.00 / +57.00 / −26.00** against measured **−125.00 / +57.00 / −26.00**.

   ⚠ **The `−26.00` is a FIXED-R4 figure and must never be quoted without that
   word.** p12 called its pair interval degenerate on the *inference* that the
   cheaper R4 spelling could not verify; TASK_040_REVIEW **built it** — route A,
   plain additive test with one extra `requires` and one extra driver conjunct —
   and it verifies **15/0, twin 18/0**, holds `R4 ≡ R5 exact`, and measures
   **17.00 / 92.00 cheaper** than the shipped R4. On `large` that is **3.5× the
   headline and it flips the sign**: shipped R3 is **+66.00 dearer** than the
   cheapest-found *verifying* R4. So p12's R4 endpoint has measured width, and
   the fourth "safe beats unsafe" instance is **fixed-R4 only**.

   **And the `identity` pin's own price is 3.00 Ir per string walked**, not the
   `+2` p12 published — that was a static `n_fn` delta wearing a per-string label.
   Law `3.00·K − 1.00`, exact at four `K` including two its inputs never visit;
   92.00 Ir/call on `large`.

   The bug's observability is a function of **magnitude and compiler** (gcc here
   defaults to `-fstack-protector-strong`, upstream clang to nothing, and
   `build.py` passes neither): +1…+8 B **silent and wrong on both**; gcc fires the
   canary from **+12**; clang's loop is destroyed +12…+48 and SIGSEGVs from +64. So
   `-fno-stack-protector` is **both a thumb on the scale and unnecessary**.
   Unsafe Rust with the check deleted prints **byte-for-byte C's wrong answer**.

13. **p04 — known BITS survive a loop-carried phi where a range does not, and
   the rule is quantitative: `next_pow2(CAP) <= ARR_LEN`.** (TASK_042, reviewed
   at TASK_042_REVIEW: **headline confirmed by a stronger test than was asked
   for, and its stated mechanism refuted**; one blocker, three majors.) Ring
   buffer: the third operator in the bound-propagation series, the first kernel
   with two live cursors, and the first whose bug stays **in bounds**.

   **The result, as corrected.** Spelling the wrap as a **source-level branch**
   keeps both ring checks at `RING_CAP = 64` (`L_br64`, 86 → 101 instructions,
   1 → 3 pads) *and* at 60, at the identical provable cursor range. **So the
   range is never what carries; what carries is known bits contributed by the
   operator.** That is the sentence, and `L_br64` — which nobody asked for — is
   its strongest single piece of evidence.
   ⚠ **What is FALSE is the published explanation of the 60 case**: p04 shipped
   *"`% 60` fixes no bits — its fact is the range `[0,59]`"*. It fixes bits:
   `computeKnownBits(urem x, 60)` zeroes the high 58, i.e. `x % 60 < 64`, **and
   that fact does survive the phi** — `% 60` into a `[u64; 64]` array elides both
   checks. The measured rule, zero fitted parameters, is

   > `urem x, C` ⟹ `x < next_pow2(C)`, and **`next_pow2(CAP) <= ARR_LEN` is
   > NECESSARY for the access check to be elided, and sufficient only ABSENT a
   > cursor-relating guard.**

   ⚠ **The qualifier is not decoration and this file stated the rule without it
   for one commit** (TASK_044). `% 60` into `[u64; 64]` with **both** of p04's
   guards — the shipped shape — is **2 pads, not 1**: the *store* check goes and
   the *load* check stays. Sufficiency is clean only with no guard
   (`T_noguard_60_a64`, 1 pad) and in the one-cursor family.
   The necessary half reproduces every capacity p04 built (64, 128 elide; 48, 60,
   96, 33 do not) **and the mixed cases it never built** (`% 32` into `[u64;64]`,
   `% 64` into `[u64;96]`: both elide). Second refinement: the elision at a power
   of two is a property of the `%`/`&` **spelling**, not of the cursor's range —
   and a guard does **not** destroy the `and` form, which is what separates the
   two operators.
   Placed in the series: p05's **multiply** — no, the implication is nonlinear;
   p09's **shift** — yes alone, no through the composition with a multiply;
   p04's **modulus** — yes, whenever `next_pow2(CAP) <= ARR_LEN`.

   **⚠ p04's shipped R3 is NOT the cheapest found, and TWO NUMBERS come out of
   that — do not merge them.** Six in-contract spellings across **five distinct
   machine codes** measure `3367 / 11666` against the shipped `3368 / 11667`, all
   at `required_miss = 0`, `forbidden_hits = 0`, `model.py` agreeing on all five
   matrix inputs. p04 **did not re-ship** (see `.memory/02-bench-rules.md`), so:

   | quantity | value | what it is |
   |---|---|---|
   | **fixed-R4 bound**, `R3ship − R4ship` | **`+5.00`** | unchanged — the shipped rung did not move |
   | **cheapest-found in-contract bound** | **`+4.00`** | `inf(in-contract found) − R4ship`, **name the spelling** |

   ⚠ **This file conflated the two for one commit**, telling p04's engineer to
   "restate the fixed-R4 bound as `+4.00`"; that is only true if the rung is
   re-shipped, and the engineer refused the instruction and was right. So *"the
   first pattern whose shipped R3 is the cheapest found"* is **false** — beaten by
   the next lever exactly as on p03 — while the fixed-R4 bound is still `+5.00`. **The lever is new and is untried on every pattern before p04**: a
   **two-step reslice** (`buf.split_at(off).1.split_at(len).0`, or `get(..)`
   twice) — and its mechanism is **register allocation, not bounds-check
   removal**. Same two checks, one fewer instruction:
   `off + len` needs a scratch register, `buf_len - off` is computed in place in
   `%rsi`, which is dead after. `R2 - R3` is `20·ops + 12` against the cheapest.
   ⚠ **The `idiom` block pins no reslice spelling at all**, so all six candidates
   are in contract by construction: it is the *cheapest-found* claim that failed,
   **not** the declaration — p04's direction test holds (both exclusions are
   byte-identical to shipped R3 and move the figure by 0.00).

   **⚠ Two of the seven swept "exact integer cost models" are laws of a DIFFERENT
   COUNT VECTOR and fail out of sample.** The two R1 cells were fitted over all
   99 blobs on a licence verified only on band F — **where `epop == 0` by
   construction**. On a fresh blob with `dpush` *and* `epop` both non-zero, a
   combination **no shipped blob has**, they miss by **−385 (gcc) and −330
   (clang)**, and the same laws at *R1's own* counts land exactly. The other five
   rows re-derive exactly by independent exact-rational solve, the pooled rank
   5/5 reproduces, and `13·417 + 15·413 + 46 = 11662` holds out of sample. **The
   general lesson is in `.memory/03-measurement.md`: a law fitted over a rung
   whose own execution counts differ from the model's is a law in THAT RUNG's
   counts** — and 99 in-sample blobs could not see it because one band zeroed a
   regressor by construction.

   **The bug is invisible to memory safety — but the published characterisation
   of *why* is too specific, twice.** `m_nofull_msonly` and `m_noempty_msonly`
   both verify `9/0` with the functional spec stripped, against five positive
   controls; **both guards deleted at once** is also `9/0`. p04 published this as
   *"the relation between `head` and `tail` is exactly the part of the state the
   memory-safety obligation does not need"*. True, and **not a characterisation**:
   `x_swaphead_msonly` — read `ring[tail]` instead of `ring[head]`, memory-safe,
   functionally wrong, **no guard touched** — is also `9/0`. **The
   memory-safety-only configuration is blind to every functional change**, which
   is the honest statement and is p09's result restated, not a new mechanism.
   ⚠ **And it is NOT about the modulus.** Remove `%` entirely — wrap with a
   source branch reached under the guard — and the obligation is *still* two
   independent one-variable clauses (`9/0`) and the missing fullness check is
   *still* invisible. **The property is that the index bound is the array's own
   fixed capacity**, not that the update is modular; the next fixed-capacity
   container without a modulus is the same class, not a different one.

   Sound and unchanged: **R4 ≡ R5 `exact`** (`md5_fn c0573f691c95`, 74
   instructions), R5 `9/0` first try with **no lemma and no nonlinear
   arithmetic**; TCB **10 lines / 5 items**, recounted against the gate's own
   `tcb_items`; `p1_weak_requires` passes the shipped configuration at 9/0 and is
   caught **only** by `--cfg slb_twin` (second pattern where the twin is the sole
   catcher, first on a non-slice accessor); `ring_set_unchecked`'s whole-sequence
   `ensures` is load-bearing (weakening it to a slot-`i` clause fails the shipped
   configuration). The R4 side is **degenerate** — three candidates, all
   byte-identical to shipped R4 — for the pattern's own reason: **the clamp seeds
   a fact LLVM already has**, the opposite of p03 on the identical lever, and
   p04's own `RING_CAP = 60` control shows the same lever worth −358 Ir/call
   where the fact is missing. **R1's wrong answer IS reproducible** (unlike p03's)
   — established three ways, including 880 runs under randomised environment size
   and memcheck on a static build. And p04's `ns` figures **survive a real
   30-layout population**: `+25.7%` / `+9.7%` reproduce mode-matched at
   `+25.1…+26.0%` / `+9.3…+10.2%`, `P(A>B) = 100%`, with the `R3 − R4` null
   holding and its sign flipping between modes, which is what a null looks like.

   **The p03 reproduction has a named boundary.** `R2 − R3 = 20·(all four) + 11`
   is p03's law to the instruction because it is the **opcode-stream** half —
   both patterns walk the identical 5-byte record with the identical written-out
   LE decode. p03's extra `3.00000·xpop` in `R2 − R4` is the **container** half:
   p03's pop guard supplies only the lower bound `sp > 0`, so the upper bound
   must cross the attacker branch and LLVM drops it, while p04 has no container
   check to keep because `%` supplies both cursors' upper bounds unconditionally.
   **The law reproduces for the stream and not for the container.**

14. **p13 — a bound the optimiser can SEE is worth more than the check costs;
   and the first pattern whose rungs call different libc routines.** (TASK_043,
   reviewed at TASK_045_REVIEW: **three blockers, six majors** — the headline's
   sign survives, its magnitude and its entire stated mechanism do not.)
   `strncpy` truncation: the first bug here that is a **correctly-called library
   function** rather than an omitted line, and the first whose **harm lands at a
   different site from the bug**.

   **The mechanism, as corrected — and it is a better result than the one
   published.** p13 shipped the gap as *"R3's `copy_from_slice → memcpy` and
   `fill(0) → memset` against R4's byte loops"*. **That is wrong: R4 makes the
   same two library calls at the same cost** (identical `memcpy`/`memset`
   marginals across R3ship, R4ship, R4bulk). **72% (small) and 90% (large) of the
   gap is the CONSUMER scan, and its direction is the reverse of the published
   one:**

   > A consumer whose **bound is visible to LLVM** (`d < 32`) fully unrolls to
   > 32×(`cmpb`/`je`) = **2 Ir/byte**; an **unbounded** walk stays a
   > 4-instruction loop at **4 Ir/byte**. Measured at matched spelling on band L:
   > **+2.00000 Ir per consumed byte, exactly.**

   ⚠ **THE DISCRIMINATOR IS THE BOUND, NOT THE CHECK**, and this file said "the
   check" for one commit (TASK_046). An **unchecked but explicitly bounded** scan
   — `while d < DST_CAP && *dst.get_unchecked(d) != 0` — costs **exactly** what
   the safe `position()` costs, to the instruction (3718.70 / 9688.30 both). **A
   bounds check is one way of supplying the bound, and it is not what is being
   paid for.** (Nor is it the iterator: an unbounded *checked* `while dst[d] != 0`
   walk gives the same instruction count and the same band-L slope as
   `position()` — same 389 instructions and identical mnemonic multiset, though
   **not** byte-identical after the full-extent fold, which rotates a `%rax`/`%rcx`
   phase. Claim the exact `Ir` equality; do not claim byte-identity.)
   **This is p03's and p04's seeding result arriving from the other direction** —
   there the invariant had to be *handed* to LLVM as dead code; here the safety
   check supplies it as a side effect and more than pays for itself. Fourth
   pattern in the family, and the first where safety is net-negative *because* it
   carries a bound.

   ⚠ **The published margin was inflated by the contract itself, and THE SIGN
   DOES NOT SURVIVE.** `spec.md` pinned the byte-loop copy and fill in
   `unsafe.rs`/`verus.rs` and **exempted `safe_tuned.rs` by name**. Three numbers,
   all on the corrected (full-fold) tree, and the third is the one that decides
   what p13 is:

   | R4 permitted | `R3ship − R4` small / large | status |
   |---|---|---|
   | shipped byte loops (**fixed-R4 bound**) | **−177.00 (−4.49%) / −1054.00 (−9.74%)** | published |
   | + bulk copy/fill (**cheapest found in contract**) | **−85.00 (−2.21%) / −885.00 (−8.31%)** | the pin was **52% / 16%** |
   | + a **bounded** unchecked consumer | **+44.00 / +77.00** | ⚠ **sign flips** |

   The bulk pair is admissible (**17/0, twin 24/0, `identity: exact`**, TCB 5→7,
   shipped as a **control**). The bounded unchecked consumer verifies at **19/0,
   twin 22/0, with NO new trusted items** and is excluded by nothing but
   `spec.md`'s English. **So p13's "safe beats unsafe" is the price of a bound,
   and it reverses the moment the unsafe rung is allowed one.** Quote the fiat
   whenever the margin is quoted. See the direction test above: **this is its
   first fire.**

   ⚠ **THE KERNEL-EXCLUSIVE COLUMN IS NOT COMPARABLE ACROSS p13's RUNGS**, and
   this is the first pattern where that is true — its rungs dispatch **different
   work into libc**, all outside the kernel symbol (c-gcc: `strlen`; c-clang:
   `strlen`+`memcpy`+`memset`; R2: `memset`; R3/R4/R5: `memcpy`+`memset`). Two
   published figures move: the gcc-vs-clang gap **494 → 188**, and
   **`R2 − R4 = +70.3% / +43.2%` → `+47.9% / +35.8%`** on totals. See
   `.memory/03-measurement.md`.

   ⚠ **And C's entire advantage here is a LIBRARY difference.** Every C `-O3`
   cell calls glibc `strlen` for the consumer — both compilers recognise the byte
   loop and rewrite it — while **no** Rust cell does. Priced with clang
   `-fno-builtin-strlen`: **the sign of every same-backend C-vs-Rust row flips**
   (C −130.97 / −1685.58 becomes **+38.03 / +70.42**). glibc `strlen` is
   **14.00 Ir/call, 0.00000 Ir/byte**. p11's separation, unapplied — apply it.
   **Consequence for the gate**: `strlen(` is a `forbidden` spelling, is absent
   from every source, and the audit reports **0 hits** while every C object calls
   it. **A text pin binds the source, not the object.** Blast radius, audited
   across all thirteen patterns' objects: **p13 is the only one whose `forbidden`
   list the optimiser reintroduces** — `strlen` in **8 of 16** p13 objects, **0 of
   16** p12, and the other eleven forbid no library routine.
   ⚠ **That audit is only correct SCOPED TO `kernel` + `main`.** Unscoped it
   reports p12 as a hit too, and the hit is spurious: `std::env`,
   `current_dir`, the backtrace machinery and `io::Error`'s `Display` call
   `strlen` in **every Rust binary of every pattern**. An object-level
   forbidden-token audit that does not scope to the measured symbols reports the
   standard library, not the kernel.

   Sound and unchanged: Verus **17/0 first attempt** (twin 20/0), `R4 ≡ R5
   exact`, TCB 5 matching the gate's own count, Miri clean 9/9. The
   **termination store costs `1.00000` Ir per string on both compilers** and is
   *not* dead-store-eliminated, because the fill's extent `DST_CAP − n` is a
   runtime value — the manager predicted DSE and was wrong. **`strlcpy` is
   dearer than `strncpy`** (+26 gcc, +30 clang) and `snprintf` far dearer
   (+339 / +343): **the unsafe routine is the cheapest, on both compilers.**
   And the two harms — memory-safe truncation, and the OOB read — **separate by
   RUNG, not by input**: an adversarial row that truncates while every rung stays
   memory-safe is **unsatisfiable** here, because content lost ⟺ no NUL in `dst`
   ⟺ R1 reads out of bounds.

   **What p13 does NOT have**: no cost law. `strncpy` lowers to size-dispatched
   vector code, so cost is a **step function**, every natural step basis is
   **singular** on a length-homogeneous fit set, and the published "no law"
   residuals are **estimator-dependent by ~3×** (exact interpolation 115/888
   against OLS 37/443).

So the research question is **not** "does verification cost performance" (it
doesn't). It is: *what must move into the trusted base to reach C's assembly, how
much proof keeps that base sound, and which C patterns resist this treatment.*
**And after p07, one more: which loop shapes let a safety check amortise — because
that, not safety, is what the first six patterns were measuring.**

## Build matrix

Primary, per pattern: **6 cells × 2 opt levels × 2 inline modes = 24 builds** —
the 5 rungs, with R1 built twice (gcc and clang).

| Axis | Values |
|---|---|
| opt | `O0` (non-opt, for reading the lowering) and `O3` (for perf claims) |
| inline mode | `isolated` and `whole` — **defined by effect, not by flags** (below) |

### The inline modes are defined by *effect*

Settled at TASK_002_REVIEW. The two modes are not "these flags" — they are two
observable states of the build, and each language reaches them its own way:

| mode | the effect that defines it | C | Rust (R2–R5) |
|---|---|---|---|
| `isolated` | the kernel survives as its own symbol and is reached through a real `call` | own TU, `__attribute__((noinline))`, no LTO | `#[inline(never)]` via `--cfg slb_isolated` |
| `whole` | the kernel **may** inline into the driver loop | `-flto` across the three TUs | single crate, `codegen-units=1`, no `#[inline(never)]` |

The flags differ because the languages start from different places, and matching
the *flags* would not match the experiment: **C without `-flto` does not reach
`whole` at all** — the kernel survives as its own symbol and the cell collapses
into `isolated` (verified at TASK_002_REVIEW). Meanwhile `-C lto=fat` is
impossible for R5, because Verus links a precompiled `vstd` rlib with no bitcode
(`.memory/04-verus.md`), and a single-crate Rust binary at `codegen-units=1`
already has the kernel and the driver in one module — which is exactly what
`-flto` buys the three-TU C build.

Matched on effect, the two columns are publishable side by side. Matched on
flags, they would not be the same experiment. `harness/check.py` checks the
effect directly: in `whole` it looks for the loop in `main`, and step 3b's
marginal-`Ir` floor is symbol-independent precisely so it works in both modes.

Flags:

- **C**: `-std=c99 -Wall -Wextra` + `-O0` / `-O3`. Build with **both** `/usr/bin/gcc`
  (13.3.0) and `~/tools/llvm/bin/clang` (22.1.6) — clang is the same-backend
  baseline and is mandatory for any C-vs-Rust claim; gcc is the "what a distro
  ships" baseline.
- **R2–R4**: `rustc -C opt-level=0 -C debug-assertions=on` / `-C opt-level=3 -C debug-assertions=off`.
- **R5**: `./verus_run.py --compile verus.rs -o <out> -C opt-level=N ...` (same flags as R2–R4).
- `-C codegen-units=1` everywhere for reproducible codegen.
- `panic=unwind` is the default. `panic=abort` is a **secondary axis** (it deletes
  landing pads and is a real safety-cost lever) — build it, report it separately.

### Two traps that invalidate the comparison

- **Debug Rust ≠ C `-O0`.** Debug Rust inserts *integer-overflow checks* — a
  semantic difference, not an unoptimised lowering. So also build R2–R5 at
  `opt-level=0 -C debug-assertions=off` as the semantics-matched `O0` column.
  Never make a perf claim from an `O0` row.
- **gcc ≠ LLVM — confirmed, and it is large.** TASK_001 settled the pilot's
  C-vs-unsafe-Rust gap: it is a *backend* artefact. Same `pilot/k.c`, same `-O3`:

  | compiler | static raw | static padding-excl | kernel `Ir` @ n=50 000 | loop shape |
  |---|---|---|---|---|
  | gcc 13.3.0 | 32 | 30 | **125,019** | SSE2, 2 elems/iter, 5 instrs, no unroll |
  | clang 22.1.6 | 33 | 31 | **87,518** | SSE2, 4 elems/iter, 7 instrs, 2× unroll |
  | rustc 1.97.1 unsafe | 37 | 33 | **87,520** | *the same 7-instruction loop body* |

  clang and rustc emit the identical loop body (modulo register allocation and
  addressing-mode scale). The real clang→rustc static delta is **+2 instructions**
  (`lea (,%rdx,8),%rax` + `and $-32,%rax`), not 4 — the other 2 are padding slots.
  And the cause is **not** an `&Vec<u64>` ptr+len reload (LLVM promotes the `&Vec`
  argument in both rungs): rustc's vector loop uses scale-1 *byte* addressing where
  clang uses scale-8 index addressing, so it computes a byte-count bound. An
  induction-variable choice, not an ABI cost. Worth exactly +2 executed
  instructions per call, measured at n = 999 / 4001 / 12345 / 50000.

  **Always report a clang column.** A gcc-only C baseline overstates C's dynamic
  cost here by 43% — gcc emits *fewer* instructions and executes 42.9% *more*.
