# TASK_PHP_016_REPORT — `ph07`, the second real row and the first `narrowed` one

**Role:** research engineer, one agent alone.
**Row:** `patterns-php/ph07-strcut-cursor/` — `mbfl_strcut`'s `mblen_table` arm,
`ext/mbstring/libmbfl/mbfl/mbfilter.c:1179-1259`, CRASH-124, tier `narrowed`.
**Status:** ✅ **BUILT, MEASURED, GATE GREEN** — `check.py: PASS`, 0 failures,
contract `be5f5818ffa625c7…`, 2 `loud` entries (both justified, §6). All five
rungs plus R1h; R5 verifies **21 / 0** (**24 / 0** under `--cfg slb_twin`) with a
full functional postcondition. Brackets `66 / 0 STALE` (PAT) and `6 / 0 STALE`
(php) at both ends.

⚠ **Reconciliation of the running count is the manager's job.** This task was
launched from **74** and I do not carry it forward.

Scratch: `.temp/php16/` (824 KB after cleanup, `REBUILD.sh` regenerates every
deleted blob). `.temp/php12–15/` were **read, not written**, and nothing under
them was deleted — 45 / 34 / 49 / 50 entries, unchanged. **`.web/` was never
touched, `git add -A` was never run, and no file under `harness/`, `common/`,
`patterns/`, `results/` or `pilot/` was created, edited or deleted.**

---

## §0 The bracket

**Open** (first command of the session):

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
4 record(s) examined, 0 STALE
```

**Close** (last two commands):

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH       results/gate/ph00-smoke.json               29 source(s)
FRESH       results/gate/ph03-uudecode-bound.json      33 source(s)
FRESH       results/gate/ph07-strcut-cursor.json       35 source(s)
FRESH       results/ph00-smoke.json                    19 source(s) + 8 input(s)
FRESH       results/ph03-uudecode-bound.json           19 source(s) + 7 input(s)
FRESH       results/ph07-strcut-cursor.json            19 source(s) + 7 input(s)

6 record(s) examined, 0 STALE
```

⚠ **The php side is 6 records, not 4** — ph07's gate and measurement records
join the four that were there. ⚠ `0 STALE` means *every source that was pinned
still matches*, not *everything is pinned* and not *every pinned source still
exists* (`RECAP_PHP.md` F14, `PROTOCOL_PHP.md` §E); the preflight is what closes
that and it is green.

`git status --porcelain` at the close:

```
 M results-php/preflight/_norow.preflight.json
?? .tasks-php/TASK_PHP_016_REPORT.md
?? patterns-php/ph07-strcut-cursor/
?? results-php/gate/ph07-strcut-cursor.json
?? results-php/ph07-strcut-cursor.json
?? results-php/preflight/ph07-strcut-cursor.preflight.json
```

⚠ The `_norow.preflight.json` modification is `PROTOCOL_PHP.md` §E's *"not
read-only"* row and `TASK_PHP_015` §6's adjudication of it: this session
changed nothing under `harness-php/`, but it added a row, so `why_sizes` gained
an entry and the bracket run does not collapse on content. **Expected, and
consistent with the rule `TASK_PHP_015` landed** — *the bracket dirties that
file iff the session changed something the preflight record carries.*

---

## §1 What was built

```
patterns-php/ph07-strcut-cursor/
  spec.md                     contract be5f5818ffa625c7… (first written
                              13bb0b70d031be73…; it MOVED ONCE — §5, NOTES.md §0)
  NOTES.md                    the findings, §§0-11
  README.md                   the reader's entry point
  model.py                    TWO independent implementations + a third spelling
                              + a synthetic sweep, and `selfcheck` runs all of it
  c/kernel.h  c/kernel.c      R1  — mbfilter.c:1179-1259 narrowed. The bug.
  c/kernel_hardened.c         R1h — + cb3cca21b345 (2005), both guards
  c/main.c                    the driver
  c/emalloc_shim.h            -> ../../../common-php/emalloc_shim.h  (symlink)
  safe_naive.rs safe_tuned.rs unsafe.rs verus.rs        R2 R3 R4 R5
  inputs/gen.py               + small, large, adversarial-{offbyone,silent,
                                                            wild,empty,nowin}
  controls/cb3cca21b345.patch          the fix, 829 B, sha256 14dbafc9a3b970d0…
  controls/d9dda48f8a7e-mbfilter.patch the 2010 in-library restoration
  controls/fix_scope.py                what each upstream guard actually buys
  controls/guard_equiv.c/.py           the Rust clamps against the C's
  controls/negatives.py                four Verus mutants
```

**Provenance**, validating: `ext/mbstring/libmbfl/mbfl/mbfilter.c:1179-1259`,
1 489 bytes, sha256 `5edc6c04b7ff5f64…`, against the pinned tarball
`5783e0c0ba94f165…`. Kernel overlap **75 % (39/52 excerpt lines)** against a
`narrowed` expectation of 25 %; **1** unevaluable preprocessor condition, and it
is the header guard `#ifndef PH07_KERNEL_H`. `PROTOCOL_PHP.md` §F item 9 is
answered in `NOTES.md` §1a — in short, the 13 missing lines are exactly the ones
the divergence ledger declares, and **for a `narrowed` row the number is less
informative than for a `verbatim` one**, because narrowing is *defined* as
removing lines.

---

## §2 ⚠⚠ §2 OF THE TASK FILE — AND THE MANAGER'S CORRECTION WAS RIGHT

**What I did with the task file's §2, and what it produced.** I identified the
commit that introduced 5.4.0's prologue clamp: **`d9dda48f8a7e182ed8c0f56e5fde9e367131a07a`**,
Moriyoshi Koizumi, 2010-03-12, *"— Update the bundled libmbfl to the latest on
upstream"*, **64 files, +3435 −4164, no CVE, no bug number, no security label**,
first shipped in **php-5.3.3**. Verified three ways: its parent
`d73a7cdfe124b44d…` has neither the clamp nor the rewrite; the commit has both;
and the release tags bracket it. `.temp/php16/01-fixcommit.log`.

**So the task file's §2 premise — *"5.4.0's prologue carries the missing bound"*
— is TRUE, and the manager's F34 correction of `TASK_PHP_015` stands.** ✅

⚠⚠ **But it is not the `fix_commit`, and the manager found the real one while I
was building.** `cb3cca21b34518caf45852ed90597052e99294c3` (Ilia Alshanetsky,
2005-12-15, *"Fixed possible memory corruption inside mb_strcut()."*), **in
`ext/mbstring/mbstring.c` — the CALLER, in another file.** I verified it
independently before rebuilding R1h on it:

- the corpus's `index.csv` `fix_commit` column reads `cb3cca21b345` for
  CRASH-124, and reads `f95c1df58349` for CRASH-115 — which is exactly what
  `ph03` established independently, so the column is trustworthy;
- the patch fetches at 829 B, sha256 `14dbafc9a3b970d0…`, and is now
  `controls/cb3cca21b345.patch`;
- `mbstring.c` at php-5.0.5 and php-5.1.1 has neither guard; **php-5.1.2 has
  both**; php-5.2.17 has the first and **not the second**.

### 2a. ⚠ How I missed it, stated because the mechanism is reusable

The corpus's `c_file_line` for CRASH-124 reads, in full:

```
ext/mbstring/libmbfl/mbfl/mbfilter.c:1203 (OOB read site);
missing guard at ext/mbstring/mbstring.c:1807
```

**It named the repair frame all along.** I read `patterns-php/CATALOGUE.md`'s
paraphrase of that field — which quotes the guard site correctly and then
discusses the loop — and searched the *defect* file's history. ⚠ That is
`.memory-php/00-corpus.md`'s standing rule with the roles swapped: *the label is
a hint; the line is the claim* — here the **line was right and the derived prose
was where I stopped**. And it is `.memory-php/01-extraction.md` F1 one frame
further on: **the REPAIR SITE is a fourth frame**, and on this row it coincides
with the guard site rather than with the defect site.

⚠ **Neither `PROTOCOL_PHP.md` §F item 5 nor `PLAN_PHP.md` §6 says the corpus
carries a `fix_commit` column.** `PLAN_PHP.md:109` lists it among the CSV's
fields and nothing points a builder at it. **One line in `PROTOCOL_PHP.md` §F
item 5 — *"read `index.csv`'s `fix_commit` cell first"* — would have saved this
task an hour and `TASK_PHP_015` a wrong conclusion.**

### 2b. ⭐ The history, and it is the row's second finding

`mbfl_strcut`'s **body** is byte-identical — sha256 `613648930a3d2551…`,
4 693 B — at **six** release tags (5.0.0, 5.1.0, 5.2.17, 5.3.0, 5.3.1, 5.3.2).
`.temp/php16/07-history.log`, built by parsing `PHP_FUNCTION(mb_strcut)` out of
each tag's `mbstring.c`:

| tag | `mb_strcut`'s own guards | `mbfilter.c` prologue |
|---|---|---|
| 5.0.0 · 5.0.5 · 5.1.0 · 5.1.1 | — | — |
| **5.1.2** ← `cb3cca21b345` | `from >` **+ the sum clamp** | — |
| 5.2.17 | `from >` only (**sum clamp gone**) | — |
| 5.3.0 · 5.3.1 | `from >` **+ the sum clamp (back)** | — |
| 5.3.2 | `from >` only (**gone again**) | — |
| **5.3.3** ← `d9dda48f8a7e` · 5.3.29 · 5.4.0 | `from >` only | **YES** |

⭐ **The bound was restored TWICE, four years and three months apart, in two
different files.** The 2005 fix repaired the userland entry point; the library
function stayed unbounded for any other caller until the unlabelled 2010 libmbfl
refresh. ⚠ And hunk (b) went out, came back and went again — a guard that
changes benign output (§4 item 3) and could not settle down for three minor
releases.

### 2c. ⚠⚠ THE HISTORY TABLE WAS WRONG TWICE, IN OPPOSITE DIRECTIONS, AND I CAUGHT IT LATE

**I am reporting this as a defect of mine, because it nearly shipped.** I built
the table above with two `grep`s over `mbstring.c`:

* `if (from > Z_STRLEN_PP(arg1))` — the 5.1.2 spelling. It scored **5.3.0–5.4.0
  as UNGUARDED**, because by 5.3 the same guard reads
  `if ((unsigned int)from > string.len)`. **A spelling-dependent grep reporting
  ABSENCE**, which is `.memory-php/`'s own recurring class — *a guard that is a
  string search is a guard with a spelling* — arriving in a history table
  instead of in a gate.
* `from > Z_STRLEN_PP(arg1)` unanchored — it scored **5.0.5 and 5.1.1 as
  GUARDED**, because the hit is inside `PHP_FUNCTION(mb_strimwidth)`. **A
  function-blind grep reporting PRESENCE.**

⚠ **Neither error is visible from its own output; each is visible only from the
other's.** The first version had already been written into `NOTES.md` §4c and
into `controls/fix_scope.py`'s Q4 and had passed a green gate. What caught it
was running the broader pattern while creating a cited log — and then **chasing
the discrepancy instead of accepting the newer answer.** Both files are
corrected and re-gated; `07-history.log` now parses the function out of the file
rather than matching text, and `NOTES.md` §4c-bis keeps the mistake.

**Cost of the correction: one `gate → report → gate` cycle.** No measurement
moved — `NOTES.md` and `controls/` are gate-hashed only, so `contract_sha256`
did not change either.

### 2d. ⭐⭐ WHAT CHASING IT FOUND: THE SIBLING ENTRY POINT ALREADY HAD THE GUARD

In the **pinned 5.0.0 tarball**, `ext/mbstring/mbstring.c:1900`:

```c
/* PHP_FUNCTION(mb_strimwidth) */
if (from < 0 || from > Z_STRLEN_PP(arg1)) {
    RETURN_FALSE;
}
```

**It is the only occurrence of that text in the whole file.** `mb_strimwidth`
clamps `from` from above; `mb_strcut`, one screen away, in the same file, in the
same style, against the same zval accessor, clamps it only from below — and
`cb3cca21b345` is, five and a half years later, that same line copied down.

⭐ **So this row's asymmetry is three asymmetries at three scales:**

| scale | guarded | unguarded |
|---|---|---|
| **within one function** | `mbfl_strcut`'s END walk, `:1213` | its START walk, `:1202` |
| **within one file** | `mb_strimwidth`, `mbstring.c:1900` | `mb_strcut`, `:1807` |
| **across time** | the caller (2005) · the library (2010) | 5.0.0 – 5.1.1 |

⚠ **That is a stronger finding than "the author forgot a bound": at every scale
the correct code is ADJACENT to the incorrect code.** The bound was never
unknown; it was never in the one place it was needed.

## §3 The three calls the manager was least sure of

### 3.1 ⚠ `narrowed` WORKS — and one thing in `PROTOCOL_PHP.md` §A2a needs adding

**The tier machinery fits.** The deletion ledger holds ten entries with a `kind`
each; the overlap report ran and printed **75 % against the 25 % `narrowed`
expectation**; the tier definition (*"a wrapper comes off; the body is
unchanged"*) describes this extraction exactly. **Nothing had to be forced.**

⚠ **Two things I would change, and neither is a refutation of the tier.**

1. **Three of the ten ledger entries are DOMAIN RESTRICTIONS written as
   `deletion`s** (the encoding lookup, the two WCS arms, the filter-chain `else`
   arm). `PROTOCOL_PHP.md` §A2 says *a divergence that CHANGES BEHAVIOUR is a
   `modelled` tier*, and a domain restriction changes behaviour **off** the
   domain and not on it. §A1's substitution clause has a three-part test;
   **there is no equivalent clause for a restriction**, so I wrote the argument
   into each `why` and it rests on one checkable fact (UTF-8's `mbfl_encoding`
   record has a non-NULL `mblen_table` and flag `MBFL_ENCTYPE_MBCS`,
   `mbfilter_utf8.c:58-65`). ⭐ **Suggested wording for §A2, and it is §A1's
   clause with one word changed:** *a `deletion` whose `why` is "unreachable on
   the extracted domain" must name the DOMAIN and cite the fact that establishes
   it, in the tarball.* Three of my ten entries would have been written better
   if that sentence had existed.
2. ⚠ **The overlap number is LESS informative for `narrowed` than for
   `verbatim`, and the per-tier expectation reads as if the opposite were
   true.** `verbatim` 50 % / `narrowed` 25 % suggests a `narrowed` row is
   expected to score lower — but narrowing is *defined* as removing lines, so a
   low score is expected **and a high one only says the removals were small**.
   Mine is 75 %, three times the expectation, and it means nothing more than
   *"13 lines came off"*. **The load-bearing artefact for a `narrowed` row is
   the ledger, and nothing checks the ledger.**

### 3.2 ⭐ The `mblen_table` LIFTS as static data, and it costs the PROOF one lemma

**It does not drag in the encoding registry.** In PHP it *is* a 256-byte
`static const unsigned char` (`mbfilter_utf8.c:39-56`) reached as a field of a
`const mbfl_encoding`; `c/kernel.c`'s copy is **byte-identical to the tarball's
16 lines** (diffed). What comes off is the *lookup*, and it comes off because
UTF-8's flag is a compile-time constant.

⭐ **And in Verus it costs one lemma rather than a tier, an `assume` or a sixth
trusted item.** `lemma_mbtab_matches` proves `MBTAB@[b] == mbtab_of(b)` for all
256 `b` mechanically — `by (compute_only)` over a recursive conjunction plus one
induction, which is `ph03`'s `emit_ok_upto` recipe applied to static data.
`controls/negatives.py --emit notable` changes **one** entry and the proof
fails.

⚠ **It must NOT be in the blob**, and that is the part of the manager's question
worth keeping: an attacker who could choose the table could put a zero in it and
the start walk would spin for ever — a defect PHP does not have. Putting static
data in the input **invents** a defect, which is `PLAN_PHP.md` §4.2's failure
mode.

⚠ **The one place it cost something is `provenance.c_lines`, which pins a single
span** — the table is a second span in a second file and `extract_sha256` does
not cover it. That is `TASK_PHP_015` §2.5's deferred schema decision arriving on
a **second** row. I did not take it either; the bytes are pinned three other
ways (the diff, `model.py::selfcheck` check 5 which parses the 256 numbers out
of `c/kernel.c`, and the Verus lemma).

### 3.3 ⛔ ONE ROW PER TASK IS STILL THE RIGHT SIZE — no room to spare

The manager asked whether `ph07` would finish with room for a second row.
**No.** This task produced two template-level findings (§4), a `fix_commit`
correction, a Verus proof-cost result that took three redesigns, and six probes
with must-fire controls — two of which **did not fire on the first attempt** and
had to be rewritten (§4.3). ⚠ **Pairing `ph21`+`ph16` would have meant shipping
one of them with the controls unexamined**, which is the failure `TASK_PHP_014`
M1 found on `ph03`.

---

## §4 What I refute, confirm, and add

**Reconciliation is the manager's job; this is the list.**

### Refuted / refined

1. ⚠ **`.memory-php/02-ladder.md`: *"`ph07`'s vulnerable code went out
   byte-identical from 5.0.0 through 5.3.x"* — it is 5.0.0 through **5.3.2**.**
   php-5.3.3 carries `d9dda48f8a7e`'s rewrite. The sentence's point survives;
   the range is one release too wide.
2. ⚠ **`.memory-php/02-ladder.md` F34: *"the guard moved to the PROLOGUE"* is
   the 2010 story and not the fix.** The fix moved **to the CALLER, in another
   file**, in 2005. ⭐ **The reusable lesson is one level up from F34's:** a
   missing bound is often restored **in a different FRAME**, and possibly **more
   than once**. `.memory-php/01` F1 names three frames; this row adds a fourth,
   the **repair site**.
3. ⚠⚠ **`PROTOCOL_PHP.md` §A2a rule 1 says what the fixture must REACH. On this
   row the load-bearing assertion was what it must NOT reach, and §A2a has no
   word for it.** `cb3cca21b345` hunk (b) **changes benign output** on 15 870 of
   117 612 non-crashing calls, and `check.py` stage 7h requires R1h to be
   byte-identical to R1 on every non-adversarial input. So `inputs/gen.py`
   refuses a measured window with `from + length > string->len` and asserts
   `cb3cca21b345-fires=0`. ⭐ **Proposed addition:** *where the upstream fix
   changes behaviour on benign inputs, the measured corpus must leave its guards
   DEAD and `inputs/gen.py` must assert that; the behaviour change is measured
   in `controls/`, where it does not contaminate the ladder.* Without this the
   row is not gateable at all.
4. ⚠ **`controls/guard_equiv.py`'s `ord` variant is a prediction of mine that
   was refuted and I left it in the file.** I expected swapping
   `cb3cca21b345`'s two guards to change the answer; it does not, because hunk
   (a)'s `RETURN_FALSE` **discards** whatever hunk (b) computed. A control
   written to fire and then quietly reclassified is how a probe stops measuring
   anything.
5. ⚠ **`TASK_PHP_013` §2 B4 claimed the shared named-spelling paragraph is
   11 004 bytes. It is 11 003**, sha256 `59748cce2db5…`, matching
   `check.py::NAMED_SPELLING_SHA256`. `TASK_PHP_015` M2 already said so; I
   confirm it independently by extraction, and `PROTOCOL_PHP.md` §E is correct
   as written.

### Confirmed, with a measurement rather than an argument

6. ✅ **The task file's §2 premise.** 5.4.0's prologue does carry the clamp, and
   it entered at `d9dda48f8a7e` (§2).
7. ✅ **`TASK_PHP_015` §5.2's bound on its own claim.** It said *"no fix_commit
   exists"* was **not proved** and that it had not bisected history. It was
   right to hedge: the fix existed, in a file its search never covered.
8. ✅ **`TASK_PHP_015` §5.2 on `f8dd10508bd6` / bug #71906** — *"its hunks fix a
   different defect"*. Confirmed, and the different defect is real: `k = start +
   length` on two `int`s at `mbfilter.c:1212`. This row scopes it out explicitly
   and `inputs/gen.py` asserts the corpus never reaches it (`NOTES.md` §9).
9. ✅ **`PROTOCOL_PHP.md` §A2a's replacement fixture rule carries to a
   table-driven cursor unchanged.** `.memory-php/04-process.md` flagged this as
   *"being tested on `ph07` … if it does not cover both, it is wrong"*. It
   covers: the arms are the six `mblen_table_utf8` step sizes **and** the two
   arms of `if (k >= (int)string->len)`, and `_check_span` asserts all eight
   plus `start == from` / `start < from` and a `from == string->len` window.
   ⚠ **The rule needs the addition in item 3, not a rewrite.**
10. ✅ **`.memory-php/02`: R2–R5 are not ports of R1h** — but here they *are*,
    and the reason is a measurement: unlike ph03's, this fix is **complete**
    (15 333 over-reads → 0, no residue), so no rung has to carry a second fix.
    **The rule's conditional is what matters and it held.**

### New findings this row carries

10b. ⭐⭐ **THE ASYMMETRY IS THREE ASYMMETRIES AT THREE SCALES, AND AT EVERY
    SCALE THE CORRECT CODE IS ADJACENT TO THE INCORRECT CODE** — §2d. The
    sibling entry point `mb_strimwidth` already clamped `from` from above in the
    pinned 5.0.0 tarball, `mbstring.c:1900`, and it is the only occurrence of
    that text in the file.
10c. ⚠⚠ **A HISTORY TABLE BUILT BY GREPPING FOR A GUARD IS WRONG IN BOTH
    DIRECTIONS** — §2c. One spelling reports absence where the guard was
    renamed; one unanchored pattern reports presence where the hit is in a
    different function. **Neither error is visible from its own output.** Ask a
    question about a FUNCTION, not about text.
11. ⭐⭐ **ONE FUNCTION, ONE GUARDED WALK AND ONE UNGUARDED ONE.**
    `mbfilter.c:1213`'s `if (k >= (int)string->len)` bounds the end search;
    three lines earlier the start search has no bound at all. **The proof makes
    the asymmetry visible as a proof obligation that exists on one loop and not
    the other.** ⚠ It is not "the author forgot": the start search *is* compared
    against `from`, and **a comparison against an attacker-controlled scalar
    reads as a bounds check.**
12. ⭐⭐ **THE OVER-READ DOES NOT CHANGE THE ANSWER — and the clamp that arrives
    too late to prevent it is exactly the clamp that hides it.** 15 333
    over-reading calls re-run under seven different out-of-bounds fillers:
    **0 answers move.** Must-fire control (`mbfilter.c:1227`'s `start > len`
    deleted): **13 293 of 15 333 move.** That is why this shipped byte-identical
    in six releases and why no test suite could see it.
13. ⭐ **THE 2010 WALK REWRITE IS NOT THE FIX.** `d9dda48f8a7e` changed the walk
    to test before it reads; **that rewrite alone still over-reads on 13 293 of
    the same calls.** The loop shape is not the fix; the bound on `from` is.
14. ⭐ **THE UPSTREAM FIX COSTS A CONSTANT, NOT A RATE.** `c-gcc` and `c-gcc-h`
    have the same marginal `Ir` to four decimal places; the whole cost is
    **+7.3 `Ir`/call on gcc, +9.2 on clang**, because both guards sit outside
    both loops. ⚠ **Contrast ph03**, where the 2004 fix moved the marginal by
    ∓3.0 `Ir`/line with a compiler-dependent sign. **The same question has a
    different SHAPE on the two rows, and the shape is decided by where in the
    loop nest the guard sits.**
15. ⭐⭐ **A MODULE-LEVEL `broadcast use` IS A COST EVERY FUNCTION PAYS, AND ON
    THIS ROW IT DECIDED WHETHER THE FILE VERIFIED AT ALL.** The kernel first did
    not verify at `--rlimit 100`; `--profile` showed **4 127 instantiations of
    `Seq::new(len,f)[i] == f(i)`, 88 % of the cost**, because `MBTAB@` is a
    256-element `array_view` and the spec functions mentioned it on every
    recursive step. Taking the table out of the spec path and **scoping
    `group_array_axioms` to the three items that need it** took the same kernel
    from *"does not verify at 10× the default budget"* to **"verifies at the
    default in five seconds"**.
16. ⚠ **`memcpy` IS OUTSIDE `kernel_exclusive_ir`, AND ON THIS ROW THREE RUNGS
    CALL IT AND THREE DO NOT.** `.memory/03-measurement.md` rule 7 bites.
    Hand-run total-process callgrind: the hidden term is **~2 % of the total**,
    and R2-vs-R4 is +55.4 % on total `Ir` against +57.7 % kernel-exclusive.
    **The caveat is real, bounded, and bounded by a measurement.**
17. ⚠ **THE WALL CLOCK CANNOT DECIDE ANYTHING ON THIS ROW AND I SAY SO RATHER
    THAN QUOTING IT.** R4 and R5 are the same machine code (`md5_fn_norel`
    identical, 255 instructions both) and their wall medians differ by **5.4 %**,
    which is larger than every difference in the table. Spreads run 3–14 %.

---

## §5 What was run

| | |
|---|---|
| `provenance.py ph07-strcut-cursor` | `1 row(s) checked, 0 FAILED`, overlap **75 % (39/52)**, 1 unevaluable conditional |
| `gate.py --tool build … --all` | `all builds ok`, 32 builds. One diagnostic in all 8 R1h cells: `-Wsign-compare` on `((unsigned)from + (unsigned)length) > str_len` — **upstream's own spelling, kept verbatim** |
| `gate.py --tool measure` | `wrote results/ph07-strcut-cursor.json`, 32 cells |
| `gate.py` (run 1) | **FAIL, 4** — 3 × `[twin]` (no `SLB-TRUSTED-ARGUMENT` sections) + 1 × `[tables]` |
| `gate.py` (run 2) | **FAIL, 1** — `[tables]` only, the expected staleness |
| `gate.py --tool report` | `wrote results/tables/ph07-strcut-cursor.md` |
| `gate.py` (run 3) | ✅ `check.py: PASS`, 0 failures, contract `be5f5818ffa625c7`, 2 `loud` |
| *then the history correction, §2c* | `NOTES.md` §4c rewritten, `controls/fix_scope.py` Q4 rewritten — both gate-hashed only, so `contract_sha256` did not move and no re-measure was owed |
| `gate.py` (run 4) → `--tool report` → `gate.py` (run 5) | ✅ **`check.py: PASS`, 0 failures, contract `be5f5818ffa625c7`** |
| `verus_run.py verus.rs` | `21 verified, 0 errors` ×3; `--cfg slb_twin` `24 verified, 0 errors` ×3 |
| `model.py inputs/*.bin` | 7 inputs, `selfcheck=[]` on every one |
| cross-rung, `-O3 isolated` | 6 rungs + model agree on all 7 inputs; R1 diverges on the 4 over-reading ones (`.temp/php16/11-crossrung6.log`) |
| ASan+UBSan, `env -u LD_PRELOAD` | R1 fires `heap-buffer-overflow READ of size 1` at `kernel.c:171` on 4 adversarial inputs; **R1h clean on all 7**; both clean on `small`/`large` |
| `controls/fix_scope.py` | 133 932 calls × 5 historical variants; Q1–Q4 |
| `controls/guard_equiv.py` | 5 122 triples, **0 disagreements**, 3 firing mutants, 2 must-NOT-fire variants |
| `controls/negatives.py` | 4 mutants, all matching their declared expectations |
| total-`Ir` callgrind cross-check | 3 rungs × 2 inputs (`.temp/php16/25-totalir.log`) |

**Fidelity — `PROTOCOL_PHP.md` §A4.** The corpus records CWE-125 / an
out-of-bounds read at `mbfilter.c:1203`, and that is exactly what reproduces:

```
==1904204==ERROR: AddressSanitizer: heap-buffer-overflow
READ of size 1 at 0x50b0000000a9 thread T0
    #0 in ph07_strcut  patterns-php/ph07-strcut-cursor/c/kernel.c:171   <- mbfilter.c:1203
    #1 in kernel       patterns-php/ph07-strcut-cursor/c/kernel.c:299
    #2 in main         patterns-php/ph07-strcut-cursor/c/main.c:59
0x50b0000000a9 is located 0 bytes after 105-byte region [0x50b000000040,0x50b0000000a9)
allocated by thread T0 here:
    #1 in slb_head1_u64_bytes common-php/driver.c:157
```

⚠ **A sanitizer limb is a claim about THIS allocator** (`.memory-php/02`): *a
detector fires under this allocator*. The row does not claim "PHP faults" —
`crashes_pristine_5_0_0` is `False` for CRASH-124 and the corpus is right about
that, because in PHP the byte past the terminator is usually mapped.

**The chain was six commands plus one repair cycle**, `PROTOCOL_PHP.md` §E's
figure plus the three the `[twin]` sections cost. ⚠ **I landed every edit before
the FIRST gate except the ones gate 1 itself demanded**, which is
`TASK_PHP_015` §6's discipline followed as far as it can be followed: nothing
in the tree tells you which trusted items need `SLB-TRUSTED-ARGUMENT` sections
until the gate prints the list.

**`contract_sha256` moved ONCE and `NOTES.md` §0 says why:**

```
13bb0b70d031be7354077ee852e80f3dced307729fee71eb5b418e43816176a0   AS FIRST WRITTEN
be5f5818ffa625c72af87eea036735219de01b8d61e05ce3b8271805d241359c   AS SHIPPED
```

The single edit inside the fence is the `identity` entry, which **cannot** be
written before the measurement: the honest O3 level is `norel`, not `exact`,
and I could not know that until the record showed `md5_fn` differing while
`md5_fn_norel` and both instruction counts matched. `spec.md` is not in
`measure.py::measurement_sources`, so no re-measure was owed and none was taken.
⚠ `NOTES.md` §0 also discloses a pre-build draft at `09b46bfecaab118d…` that was
never built or gated — it pinned a Rust spelling (`` `n > frm` ``) that appears
in no Rust rung, caught by grepping the pins against the sources.

---

## §6 The measurement

`-O3 isolated`, kernel-exclusive `Ir` per call, from
`results-php/ph07-strcut-cursor.json`. Full table, mechanism and caveats:
`NOTES.md` §8.

| cell | `Ir` / window byte | vs `unsafe` |
|---|--:|--:|
| `c-gcc` (R1) | 3.8643 | +27.31 % |
| `c-gcc-h` (R1h) | **3.8643** | +27.31 % |
| `c-clang` (R1) | 3.1814 | +4.81 % |
| `c-clang-h` (R1h) | 3.1813 | +4.81 % |
| `safe_naive` (R2) | 4.7860 | **+57.68 %** |
| `safe_tuned` (R3) | 3.4451 | **+13.50 %** |
| `unsafe` (R4) | 3.0354 | — |
| `verus` (R5) | 3.0354 | **0.00 %** |

⚠ **`RECAP_PHP.md` open item 9 / F14 respected: no number here is beside a `pNN`
number, in a table or in prose.**

**The mechanism, per loop, off `objdump`** (`.temp/php16/23-loops.log`):

| loop | R2 | R3 | R4 / R5 |
|---|--:|--:|--:|
| start walk, per character | **9** insns, 1 bounds branch | **9**, 1 | **7**, 0 |
| end walk, per character | **8**, 1 | **8**, 1 | **6**, 0 |
| copy, per byte | **13**, 1 | `memcpy` | `memcpy` |
| fold, per byte | **10**, 0 | **8**, 0 | **8**, 0 |

⭐⭐ **R3's two walks are byte-for-byte R2's.** A variable-stride cursor is not
an iterator — `n` advances by a value read out of the byte it is standing on —
so no safe spelling I found removes that check. **R3's entire gain over R2 is
the copy and the fold; R4's entire gain over R3 is the two walks.** The row's
cost sits exactly where safe Rust cannot reach it.

**Predicted from the mechanism with no fitting**: `(0.441 + 0.291)/3.5 = 0.209`
walk steps per window byte × 2 deleted instructions = **0.418**, against a
measured R3→R4 delta of **0.4097**. ✅ Within 2 %.

**R4 ≡ R5, `norel` at O3**: 255 instructions and 953 bytes in both,
`md5_fn_norel` identical at `702235d5f057…`, `md5_fn` different. ⚠ **`norel`
and not `exact`** because the kernel calls `memcpy@GLIBC` and the two crates lay
their PLT out differently. **The proof licenses two unchecked walks, an
unchecked copy and an unchecked fold at zero instructions.**

**The 2 `loud` entries, both justified and neither mine to fix:**
`doc-citation-other` ×3, all three inside `common-php/emalloc_shim.h` (the
shared shim, measurement-hashed in every php row); and `tcb-unsafe` on
`vset_unchecked`'s `x`, which `spec.md` justifies in the same terms `ph03` does.

---

## §7 What I did NOT do, and what I am unsure about

1. ⚠ **No `controls/spellings.py`.** `PLAN_PHP.md` §5.3's trap. **No ratio in §6
   is *the* cost of safety on this kernel** — each is the cost of *these*
   spellings. The debt is now on two rows.
2. ⚠ **No `sweep-*` band.** Two points and a line is not a curve.
3. ⚠ **`provenance.c_lines` pins one span and this row lifts two.**
   `TASK_PHP_015` §2.5's deferred schema change, wanted by a second row and
   still not taken.
4. ⚠ **R1h is cited to a DIFFERENT FUNCTION from the extracted one** — the
   manager asked for this to be said rather than smoothed over, and `NOTES.md`
   §4d says it with the argument and what to attack. In short: this row's kernel
   is two frames, the wrapper **is** `PHP_FUNCTION(mb_strcut)`, and the fix lands
   in upstream's own position — **but the row therefore answers *"what does the
   fix cost `mb_strcut`?"* and not *"what does it cost inside `mbfl_strcut`?"*.**
   ⭐ `controls/fix_scope.py` already measures the `R1_2010` variant, so building
   R1h from `d9dda48f8a7e` instead is a decision and not a rebuild.
5. ⚠ **`#[verifier::rlimit(30)]` on the kernel.** Measured need: ~10–12 plain,
   **15 under `--cfg slb_twin`**; the default is 10, and at the default it
   verified plain and failed twin. A reviewer should ask whether 30 hides a
   proof that is one edit from not closing. ⚠ **The cost was attacked before it
   was budgeted around** (finding 15), which is why it is 30 and not 300.
6. ⚠ **`identity` in `whole` mode differs at BOTH optimisation levels**
   (875 vs 888 instructions at O3). The pin is about the `isolated` cells, where
   the kernel is its own symbol; the gate did not object, but I did not
   investigate the `whole`-mode divergence and a reviewer may want to.
7. ⚠ **Miri's boundary coverage on this row is weaker than on `ph03`, and
   `NOTES.md` §10c-bis says so.** R4/R5 **refuse** the adversarial calls at
   `cb3cca21b345` hunk (a) and never reach the walk, so Miri exercises the
   refusal, not the boundary. The boundary read (`s[slen]`, the terminator) is
   reached on the benign windows whose `from == string->len` — which
   `inputs/gen.py` guarantees exist and `_check_span` asserts. **The backstop is
   real but it is not where a reader would look for it.**
8. **Unsure: the `FRACTIONS` table.** `from` and `length` are fixed fractions of
   the window so the work scales with `work_per_call`. Consequence: **every
   window's `from` sits at the same relative position**, so the *measurement*
   does not span the distribution of `from` a real workload has.
   `model.py::selfcheck`'s synthetic sweep does; the measurement does not.
9. **Unsure: whether `adversarial-silent.bin` earns its measurement slot.** Eight
   iterations over a 105-byte window, and it is the only cell that *shows* the
   over-read's effect is invisible while its trajectory is not. A reviewer may
   say `controls/fix_scope.py` Q3 already says that.
10. ⚠ **I did not touch `RECAP_PHP.md` or `.memory-php/`.** Manager-only. What I
    refute and confirm is §4; reconciliation is the manager's — including
    whether item 3's fixture addition belongs in `PROTOCOL_PHP.md` §A2a or
    beside it, and whether item 1's domain-restriction clause belongs in §A2.

---

## §8 Memory updates

**None written.** `PROTOCOL.md` rule 9. Every durable fact from this task is in
`patterns-php/ph07-strcut-cursor/NOTES.md` (measured claims, per rule 9's
ordering) and in this report; `.memory-php/` is the manager's to write **after
the review**, from the reviewed text.

⚠ Candidates I would nominate, in the order I would land them:

1. **The corpus's `index.csv` has a `fix_commit` column — read it first.**
   §2a. It would have saved this task and corrected `TASK_PHP_015` before it
   reported.
2. **A missing bound can be restored in a different FRAME, and more than
   once.** §2b, §4 item 2 — F34 one level up, and F1's three frames plus a
   fourth.
3. **Where the upstream fix changes BENIGN output, the measured corpus must
   leave its guards dead and `gen.py` must assert it.** §4 item 3 — the
   addition `PROTOCOL_PHP.md` §A2a needs.
4. **A module-level `broadcast use` is a cost every function in the file pays.**
   §4 item 15 — decided whether this row's proof closed at all.
5. **`memcpy` is outside `kernel_exclusive_ir`**, so a rung that delegates its
   copy is undercharged relative to one that does not. §4 item 16, with the
   bound.
6. **An over-read whose result is invisible is one no test suite can see** —
   and here the clamp that is too late to prevent it is the one that hides it.
   §4 item 12.
7. **A history table built by grepping for a guard is wrong in both
   directions.** §2c, §4 item 10c. This one passed a green gate before it was
   caught.
8. **At every scale, the correct code was adjacent to the incorrect code.**
   §2d, §4 item 10b — the row's sharpest sentence and the one a reader will
   remember.
