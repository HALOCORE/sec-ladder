# TASK_PHP_062 — ROW 13: `ph66`, **THE TEMPORAL AXIS'S SECOND ROW** — and the first row in this programme whose target error is a **VALUE**, not a signal

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_062_REPORT.md` — **write the FILE** (rule 10).

---

## §0 ⛔ READ FIRST, IN THIS ORDER

1. `patterns-php/CATALOGUE.md` — **`ph66`'s own Part B entry** (search `ph66 ·`).
   ⚠ **Its closing sentence — *"The DJBX33A preimage the fixture needs was never
   computed; compute it before building"* — NAMES THE WRONG DIRECTION AND THE
   ONE IT NAMES IS INFEASIBLE.** Read §2.2 before you act on it.
   ✅ **Its `⚠ risk` note, by contrast, is exactly right and outranks me** — see
   §2.3, where it refuted a manager claim.
2. `.tasks-php/ROW13_001.md` — the scoping, **including two of its own sections
   struck and rewritten** (§4 measured false, §6's `F133` prediction refuted).
3. `.tasks-php/PROTOCOL_PHP.md` — §A1 tiers, **§A3a and its obligation 5**
   (⛔ **and `F141`: obligation 5's GATE excuses this row; §2.5 says discharge it
   anyway**), §B/§B1a the allocator rule, §B5 family-B publishability, **§C
   R1h**, §E the six-command sequence, §F6/§F6a, §H.
4. `.tasks-php/TASK_PHP_060.md` + `_060_REPORT.md` — **the most recent BUILD, and
   your closest template for shape.** ⭐ **Clone the DESIGN, not the text.**
   ⚠ Then `_061_REPORT.md` §2, which **refuted `_060`'s headline**.
5. `patterns-php/ph64-callback-frees-cursor/` — **the programme's ONLY other
   temporal row**, and therefore the only precedent for what a temporal
   `spec.md` looks like here.
6. `.memory-php/03-numbers.md` — the **five** things every percentage owes, **and
   `02-ladder.md`'s F74 block: that bar is NOT a gate.**

---

## §0.1 ⭐⭐ MEASURED PREMISES — EVERY ROW NAMES THE COMMAND THAT PRODUCED IT

> `PROTOCOL.md` rule 14: **a premise in a task file is one an engineer has no
> reason to doubt** — which is exactly why the two premises this programme got
> wrong (*"7 000 words"*, *"123 ASan reports"*) did so much damage. Everything
> below was run by me on **2026-09-16**. **Re-run anything you lean on.**

| # | premise | command that produced it |
|---|---|---|
| **A** | `ph66` is `E2`; **7 of 8 temporal families have ZERO rows**; 15 of 25 owed rows are temporal | `python3 .tasks-php/quota.py` |
| **B** | The trigger needs **no preimage**: `DJBX33A("abc\0") = 6385036779`, usable directly as the integer index | `python3 .tasks-php/probes/ph66_djbx33a_collide.py` |
| **C** | On real 5.0.0, `unset($a["abc"])` destroys `$a[6385036779]` — **5 cells, all `rc=0`** | `sh .tasks-php/probes/ph66_key_identity.sh` |
| **D** | ⭐ Cell D: the defect can leave **the named key alive and kill the unnamed one** | same |
| **E** | ⛔ There is **NO use-after-free variant** — a reference-held victim is still silent | same, cell B |
| **F** | `Zend/zend_hash.c` holds **10** `p->h == h` predicates; **9** already spell the R1h's conjunct form; `:464` is the **only dual-kind site** | `python3 .tasks-php/probes/ph66_djbx33a_collide.py --selftest` (N6–N8) |
| **G** | The R1h `b73349dbe4e9` applies to pristine 5.0.0 **verbatim, `-p1`, one file, no backport** | `sh .tasks-php/probes/rebuild_hardened_php.sh --label ph66 --patch … --trigger …` |
| **H** | Post-image: adversarial `count=1 → count=2`; benign **identical**; **`rc=0` on both sides** | same |
| **I** | Obligation-5 cost on this row: **cold 30 s · incremental 619 ms · 60 MB · no sudo · no network** | same |
| **J** | `preimage_screen.py` gives **1 record, `CANDIDATE`, 0 exclusions** — ⚠ and `CANDIDATE` is **not** a confirmation; I read the patch BODY | `python3 .tasks-php/preimage_screen.py --row ph66 --verbose` |
| **K** | `fixsurvey.py` flags **30 of 102** rows as owing an R1h decision; **`ph66` is not one** — one id, one commit, one file | `.tasks-php/FIXSURVEY_001.md` |
| **L** | Live task cost, **as an EVENT**: marginal **2.50**, searched-only **2.48**, first-in-family **2.38** (n=8), follow-on **2.75** (n=4), **PUBLISH `~63 .. ~79`, middle `~64`**. ⛔ **These MOVED while this brief was being written** — see the note below | `python3 .tasks-php/task_cost.py` |
| **M** | `I7/O3` — one of the two obligations this row is filed under — is broken by **exactly one case in all 166**, and it is this one | `paper/_old_story/invariants-list.md`, `invariants-166.json` `cases[98]` |

> ⛔⛔ **PREMISE L MOVED WHILE THIS FILE WAS BEING WRITTEN, AND THE REASON IS
> WORTH ONE PARAGRAPH OF YOUR TIME.** Adding row 13's task file made
> `task_cost.py`'s `N1` fire (an unclassified task — the arm working). Filing it
> then exposed that **`"040"`, the R1h hunt for `ph52` AND `ph53`, had sat
> classified `PENDING` for ~20 tasks after both its rows gated** — so real row
> cost was parked outside the numerator and the **published projection was
> understating by ~2 tasks**. ⭐ `N8` could not see it: `N8` bounds the *size*
> of the pending pile, and the pile was small. ▶ ***The size of the pile was
> never the property; its membership was*** — `F132`'s class one level up, in a
> validator. Repaired with `N8b`/`N8c`/`N8d` (`F142`).
> ⚠ **So: RE-RUN `task_cost.py` rather than quoting premise L.** The guard is
> not a better number, it is the date beside it (`F126`).

---

## §1 Why this row

**The temporal axis has ONE built row against 15 owed**, and **seven of its eight
families have zero** (premise A). ⛔ **The ground that was used to defer temporal
rows is refuted and inverted** (`_057` §3.2): executed reproducers fault on
**78.6 %** of type rows, **58.5 %** of spatial and **38.7 %** of temporal, so
waiting does not make a temporal row cheaper. **Row 13 is temporal. This is it.**

⭐⭐⭐ **AND THE REASON `ph66` IS THE ONE TO TAKE IS NOT THAT IT IS EASY — IT IS
THAT IT IS THE CONTROL THIS PROGRAMME HAS NEVER HAD.** Every one of the twelve
built rows exhibits its defect as **a signal**: a segfault, an ASan report, an
address. `ph66` exhibits its defect as **a wrong answer** — `rc=0`, clean
stderr, `count($a)` off by one (premises C, D, H). That single difference
propagates all the way up the ladder, and it is worth stating what it predicts
before anyone builds anything:

| instrument | what it sees on `ph66` | why |
|---|---|---|
| a CLI reproducer | ✅ **the wrong VALUE** | the survivor list differs |
| ASan | ⛔ **nothing** | every free is a correct free (§2.3) |
| Miri | ⛔ **nothing** | there is no UB to detect — the boolean is wrong, the memory is not |
| safe Rust (R2/R3) | ⛔ **nothing, if ported faithfully** | a wrong predicate is expressible in safe Rust |
| **Verus (R5)** | ⭐ **the only rung that can refuse it** | it is the only rung that can *state* "the bucket deleted is the bucket named" |

⚠⚠⚠ **`CLAUDE.md` rule 6 — READ IT BEFORE YOU FEEL A DOUBT.** *"Safe Rust
reproduces the bug bit-identically"*, *"Miri doesn't see it"*, *"no column
moves"* and *"the bug is in-bounds so it's logical, not temporal"* are **ALL
FINDINGS, NEVER KILLS**, and **six of ten historical temporal refusals** were
made on exactly these grounds. ▶ **If this row's R2 column is identical to its
R1 column, THAT IS THE RESULT — publish it.** A ladder whose every rung buys
safety is a ladder that has never measured a defect the rungs do not address.

⚠ **THE COST OF PICKING IT, STATED SO IT CAN BE HELD AGAINST ME.** `ph66` is
filed `E2` (*"released, then still named"*) and its harm is better described as
*"the wrong thing released"*. ⓘ **I am not re-filing it and neither should you**
— the axis and family are the corpus's, carried across unmodified — **but say in
the report whether the `E2` fit is real**, because the family's *within-family
control* argument (`QUOTA_001`) depends on the members sharing a mechanism.
⭐ Premise M is the related datum: the corpus's own labeller wrote that the true
primary invariant here would be a **new** one, `NEW:container-key-identity`, and
filed `I7/O2+O3` only because a freeze rule forbade new entries (§2.6).

---

## §2 THE MANAGER'S DECISIONS, AND THE FACTS BEHIND THEM

### 2.1 ⭐ THE MECHANISM, QUOTED FROM THE PRISTINE TARBALL

`php-5.0.0/Zend/zend_hash.c`, `zend_hash_del_key_or_index`, the chain walk:

```c
464  if ((p->h == h) && ((p->nKeyLength == 0) || /* Numeric index */
465      ((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, nKeyLength))))) {
```

A **numeric** bucket is marked by `nKeyLength == 0` (`:387`, *"Numeric indices
are marked by making the nKeyLength == 0"*). So for a numeric bucket the **left
disjunct fires and the key is never compared at all** — hash equality alone is
treated as identity.

The delete's tail then runs, in order: `ht->pDestructor(p->pData)`,
`if (!p->pDataPtr) pefree(p->pData, …)`, `pefree(p, …)`, `ht->nNumOfElements--`.
⭐ **Read the four lines above the destructor call too** —
`if (ht->pInternalPointer == p) ht->pInternalPointer = p->pListNext;` — because
that line is why §2.3's answer is what it is.

### 2.2 ⭐⭐⭐ THE CATALOGUE SAYS "COMPUTE THE PREIMAGE". DO NOT. IT IS THE WRONG DIRECTION AND IT IS INFEASIBLE.

`zend_inline_hash_func` is **DJBX33A accumulating in a `ulong`**, and
`Zend/zend_types.h` makes that **64-bit on LP64**. ⛔ A preimage is therefore a
64-bit target, and it has **no digit structure to lift**: every `33^k` is odd,
hence a **unit** mod 2^64, so no byte position owns a bit range. It needs
lattice work or a ~2^32 meet-in-the-middle.
ⓘ **I tried the lifting route and it failed for exactly that reason. The failure
is the evidence, which is why it is recorded rather than quietly dropped.**

⭐⭐ **NO PREIMAGE IS NEEDED.** `_zend_hash_index_update_or_next_insert` stores
`p->h = h` with `h` the **raw user-chosen index**. ▶ **Run the hash FORWARDS on
any string key and publish the result as the integer index.** One line, no
search. `"abc"` → **`6385036779`** (premise B). ⚠ `nKeyLength` **includes the
NUL** — `Zend/zend_execute.c:3612` passes `varname->value.str.len + 1`.

### 2.3 ⛔⛔ THE HARM IS **NOT** SELECTABLE. I CLAIMED IT WAS; THE MEASUREMENT SAYS OTHERWISE.

`ROW13_001.md` §4 asserted the defect yields *either* a silent wrong answer *or*
an ASan-visible use-after-free, **"selectable from the blob"**. ⛔ **Measured
(premise C), all five cells `rc=0`:**

| cell | fixture | survivors |
|---|---|---|
| A | victim alone | `'other'` |
| B | **a reference still holds the victim** | `'other'` |
| C | victim is an array | `'other'` |
| ⭐ **D** | `"abc"` inserted **before** the numeric index | **`'abc'`** |
| E | benign — every key really present | `6385036779,'other'` |

⭐ **Why there is no UAF**: `pDestructor` is `zval_ptr_dtor`, which frees **only
at count 0** — so the last holder's free is a *correct* free of a value nobody
else names — and the bucket's one external alias is repaired four lines above
the free (§2.1). **There is no dangling holder left.**

⭐⭐⭐ **AND CELL D IS A BETTER HEADLINE THAN THE ONE I INVENTED.**
`unset($a["abc"])` **leaves `'abc'` in the array** and destroys an unrelated live
element instead. *Both halves wrong at once*: the key you named survives, the key
you never named dies, PHP exits 0. It is order-sensitive (the chain is walked
head-first; inserts go to the head), so **the blob selects WHICH element dies,
never WHETHER a fault occurs.**

⚠ **THE LESSON, AND IT IS FOR ME NOT YOU**: the catalogue's `⚠ risk` note said
*"it produces no fault — a silent wrong answer"* and was right; §4 was a second
home for the fact and it disagreed (`F131`). ▶ **Where this brief and
`CATALOGUE.md` disagree, say so in the report rather than picking one.**

### 2.4 ⭐⭐⭐ THE PREDICATE CENSUS — AND WHY IT SPLITS `F133`(i) IN TWO

Premise F, from `probes/ph66_djbx33a_collide.py` (arms N6–N8):

| line | function | how it settles the key kind |
|---|---|---|
| 215 | `_zend_hash_add_or_update` | conjunct, string |
| 280 | `_zend_hash_quick_add_or_update` | conjunct, string |
| 356 | `_zend_hash_index_update_or_next_insert` | conjunct, numeric |
| ⛔ **464** | **`zend_hash_del_key_or_index`** | **DISJUNCT — the defect** |
| 854 | `zend_hash_find` | conjunct, string |
| 881 | `zend_hash_quick_find` | conjunct, string |
| 906 | `zend_hash_exists` | conjunct, string |
| 932 | `zend_hash_quick_exists` | conjunct, string |
| 955 | `zend_hash_index_find` | conjunct, numeric |
| 976 | `zend_hash_index_exists` | conjunct, numeric |

⛔⛔ **This REFUTES `ROW13_001.md` §6's own prediction** that `ph66` would be
`F133`(i)'s counterexample. **Nine of ten already spell the R1h's required-
conjunct form** — a higher ratio than `ph96`'s 7-of-23.

⭐⭐ **But the count is not the finding; the split is.**
`zend_hash_del_key_or_index` is **the only one of the ten that serves BOTH key
kinds from one call site** (its `flag` parameter). The other nine are
single-kind and never face the choice. ▶ ***The repair's SPELLING was present
nine times; the repair's PROBLEM was present nowhere.*** ⓘ This is **item 139**,
and the report should say whether the two-column reading holds up when you look
at it from inside the row.

### 2.5 ⭐⭐⭐ §A3a IS FULLY DISCHARGEABLE HERE, AND ITS OBLIGATION 5 WOULD HAVE TOLD YOU TO SKIP IT

Premises G–I, run end to end:

| | pre-image (pristine 5.0.0) | post-image (R1h `b73349dbe4e9`) |
|---|---|---|
| adversarial (cell D's script) | `count=1`, victim destroyed | `count=2`, **victim survives** |
| benign | correct | **identical** |
| **exit status** | **`rc=0`** | **`rc=0`** |

⭐ **The patch applies VERBATIM** — `-p1`, one file, six lines, no backport.
Contrast `ph96`, whose R1h *bound but did not apply* and needed a 3-line
backport (`_060` §2.4). **This is the cleanest R1h the programme has handled.**
⭐⭐ And **the repair is narrow**: it moves the adversarial case and leaves the
benign one byte-identical, which a "delete less in general" fix would not.

⛔⛔⛔ **BUT OBLIGATION 5 SAYS *"REQUIRED, GATED ON 'the pre-image run faulted'.
If the row's trigger did not fault, this is vacuous and you skip it."*** This
row's pre-image run does **not** fault. ▶ **DISCHARGE IT ANYWAY AND SAY THAT YOU
DID.** That is `F141` (⛔ **UNREVIEWED** — it is a manager finding about the
protocol and you are free to say it is wrong).
⚠ **The generator is already repaired**: `rebuild_hardened_php.sh` takes
`--patch/--trigger/--label/--workdir`, prints rc **and** stdout for both images,
and **adjudicates nothing**. Its old form asserted `rc=139 → rc=0` and would have
printed *"expect 139"* at you on a row where 0 is correct.

### 2.6 ⭐⭐ THE CORPUS'S OWN LABELLER THINKS THIS ROW'S INVARIANT DOES NOT EXIST YET

Premise M. `invariants-166.json` `cases[98]` is this defect, and its `notes`
say — the labeller's words, not mine:

> *The true primary is arguably a NEW entry:* **`NEW:container-key-identity`** —
> *"a hash-table operation acts on the bucket whose key equals the requested key
> in both key kind and key bytes, and on no other bucket"* — *which by the
> restatement test is **T1-universal** (no PHP noun) and **construct-bound** (a
> single defective predicate at `zend_hash.c:464`; every sibling lookup in the
> same file is correct). I did not file it as the label because the rule says
> NEW only if genuinely nothing fits.*

⭐ **The same notes record that the `T3`-honesty sub-rule FIRES here and has
nowhere to send the case** — *"this case's counts are not the sharing oracle,
they are pure lifetime"* — which the labeller offers as **evidence against `I7`
being a single entry**.

▶ **WHY THIS MATTERS TO YOU AND NOT JUST TO A PAPER.** `spec.md`'s obligation is
what `R5` must prove. **`I7/O2`+`I7/O3` are refcount obligations, and a Verus
proof about refcounts is not the proof this row needs.** The property that
actually excludes the defect is the labeller's: *the bucket deleted is the
bucket named, in kind and in bytes.* ▶ **State THAT as `R5`'s obligation, and
record in `NOTES.md` that you did and why** — quoting the labeller's note, which
is a corpus artefact and not a manager opinion. ⚠ **Do NOT edit `CATALOGUE.md`'s
`inv/obl` column**; it is carried across unmodified by design.

### 2.7 THE KERNEL — the blob, the fold, and the allocator

- **Blob** (the catalogue's own words): *"an insert/delete key stream."*
  ▶ Each record is `(kind, key-or-index, op)`. ⭐ **The blob must be able to
  express cell D's ORDER** — a string key inserted before the colliding index —
  because order is the only knob the defect has.
- **Benign fold**: `u64` over **the surviving keys**, per the catalogue.
- ⚠⚠ **"THE ALLOCATOR ENTIRELY OUT OF THE PICTURE" IS ABOUT THE OBSERVABLE, NOT
  THE IMPLEMENTATION.** Every other temporal row folds `(allocs, frees)` into
  its `u64`; this one folds values. **The buckets are still allocated per
  insert** — a faithful lift allocates plenty. ▶ **Do not narrow the allocator
  out of the kernel on the strength of that phrase.**
- ⛔⛔ **THE KERNEL MUST NOT INTRODUCE UB THE C ORIGINAL DOES NOT HAVE.** §2.3 is
  the whole research value: every free in `zend_hash_del_key_or_index` is a
  *correct* free. A kernel that frees the bucket and then reads it has built a
  **different row** — and worse, it would hand ASan and Miri something to find
  and destroy §1's table.
- ⚠ **§B1a: keep allocations O(1) per kernel call** so A1/B1 agree (item 78).
- ⛔ **Make `small.bin` and `large.bin` GENUINELY DIFFERENT SIZES.** `ph64`
  shipped both at **9 bytes** — one draw sampled twice — which silently weakened
  every two-input argument that row made (F119/M4).

### 2.8 TIER, STATISTIC, AND THE PREDICTIONS

* **TIER** — the catalogue says `verbatim`. ⚠ **That is a mining-wave label and
  `ph55` REFUTED its own.** ⭐ It is plausible here — the construct is one file
  and one predicate — **but the whole of `zend_hash.c` is not the kernel.**
  ▶ **Declare what you measured** (§A1), and if the narrowing costs `verbatim`,
  **that is a result, not a failure.**
* ⭐⭐⭐ **`inside_share` PER CELL AS A MATRIX, BEFORE the statistic is chosen** —
  ⛔⛔ **and `F74`'s two-condition bar is NOT A GATE**, settled in `_059` with
  four documents and a measured counterexample. **Use the share to EXPLAIN a
  disagreement, never to withhold a column.**
* ⚠⚠ **TWO quantities wear the name `inside_share`** (`F129`). **Label which.**
* ⛔⛔ **EVERY PERCENTAGE OWES FIVE THINGS: STATISTIC · INPUT · OPT/MODE · BASE ·
  and if the base is a C cell, WHICH COMPILER — with BOTH C COLUMNS, or an
  explicit statement that only one was measured** (`F108`). ⭐⭐ **AND `_061`
  JUST PRICED THIS**: `ph96` published `A1` only, having shown a 16-cell matrix
  **at `O3/isolated` only**, and its headline was refuted at `O0` where `A1`
  reads `+0.0000` while `W1` moves `−2.24 … −19.58 Ir/call`. ▶ **Show the matrix
  AT MORE THAN ONE OPTIMISATION LEVEL, or say plainly that you did not.**
* ▶ Run `.tasks-php/cbaseline_check.py --ratchet` before finishing; **adjudicate
  any new hit BY HAND, never widen the regex**, and **adjudicate the SET by unit
  text, not the count** (`cbaseline_diff.py`, `F132`).
* ⛔⛔ **ANY FAMILY-B FIGURE IS BOUND BY §B5**, with **two verdicts per pair**:
  *magnitude resolvable?* and *sign stable?*

**PREDICTIONS, REGISTERED.** ⚠ **Nine consecutive review rounds have refuted
manager or engineer claims; in `_061` my own §1.1 was wrong and `F136`'s headline
fell. That is the expected yield — score these honestly, either way.**

1. ⭐⭐⭐ **P1 — R1, R2, R3 and R4 ALL REPRODUCE THE DEFECT, and their benign
   `u64` values agree exactly.** The defect is a wrong boolean, not a memory
   error, so no safety rung addresses it. ▶ **Falsifier: any rung below R5 whose
   adversarial fold differs from R1's.** ⓘ If it holds, **this is the row's
   headline and arguably the programme's**: *the first defect in the corpus that
   the entire safety stack is blind to.*
2. ⭐⭐ **P2 — MIRI REPORTS NOTHING on the adversarial input**, because there is
   no UB: every free is a correct free (§2.3). ▶ **Falsifier: any Miri
   diagnostic.** ⚠⚠ **A Miri diagnostic would mean YOUR KERNEL introduced UB
   the C does not have** (§2.7) — treat it as a bug in the port first.
3. ⭐⭐ **P3 — R5 IS THE ONLY RUNG THAT CAN REFUSE IT**, and its obligation is
   §2.6's *the bucket deleted is the bucket named, in kind and in bytes* — not a
   refcount property. ▶ **Falsifier: an R5 that verifies with the defective
   predicate in place.** ⛔ **If Verus cannot state it, THAT IS A FINDING**
   (`CLAUDE.md` rule 6), and a large one — say exactly which part resists.
4. **P4 — the R1h is NOT free at `O0` and is within noise at `O3`.** It adds a
   conjunct evaluated per chain step, but it also **short-circuits the `memcmp`
   earlier** on length-mismatched keys, so the sign is genuinely uncertain and
   may depend on the blob's chain depth. ▶ **Falsifier: either direction, with
   both C columns, at both levels.** ⓘ **I am registering this one because I do
   not know the answer, which is what a prediction is for.**
5. **P5 — the `verbatim` tier does NOT survive the narrowing** (§2.8). ▶
   **Falsifier: a kernel that lifts the construct with no edit and still gates.**

---

## §3 TRAPS

1. ⛔⛔⛔ **A LIVENESS CHECK MAY NOT BE TRUNCATED AND MAY NOT MATCH ITSELF**
   (item 113). `pgrep` feeding a decision gets **no `head`, no `tail`**.
   ▶ **Confirm `/proc/<pid>/cmdline` for an exact PID; best of all, need no
   `pgrep`.** ⛔ Never `pkill` / `killall` / substring-match. Prefer
   `timeout <N> <cmd>`.
2. ⚠⚠⚠ **`grep -a` ALWAYS** (`F35`). A line-grep misses a phrase that wraps.
3. ⛔ **`F101` / item 109 — `kernel_fingerprint` is PATH-SENSITIVE and fired LIVE
   in BOTH directions on `ph52`.** ▶ Clone `ph52`/`ph55`'s repair: fixed-width
   `vNN` slug, asserted equal-path-length invariant, `asm.py::identity_level`.
   ⓘ **Suggested row directory: `ph66-hashdel-uncompared`** — 23 characters,
   the same length class as `ph96-outparam-unwritten`.
4. ⛔⛔ **A BACKTICK IN AN `idiom.required`/`forbidden` ENTRY IS A PIN** (item
   100, three instances in three tasks). **Run `spellings.py --audit-only` on any
   contract prose BEFORE quoting it, and read the output.**
   ⚠ **And never backtick a span containing a character literal** — `exec_code`
   blanks them, so `` `p->nKeyLength == 0` `` is safe but a span containing
   `'\0'` is not.
5. ⛔⛔ **§H: a validator lands with its must-fire negatives INSIDE it**, feeding
   `problems` so stage 9b sees them. ⚠ **Never in gitignored `.temp/`.**
   ⭐ **If a checker is a grep, ADJUDICATE hits by hand and RATCHET.**
   ⓘ `.tasks-php/checkers.py` is at **31 filed / 31 on disk**; **if you add a
   `.py` or `.sh` under `.tasks-php/`, FILE IT** — it globs both.
6. ⚠⚠ **A `c/*` COMMENT MAY POINT AT AN ARGUMENT; IT MAY NOT STATE THAT
   ARGUMENT'S VERDICT** (§F6a). ▶ **§2.3's refutation, §2.4's split and §2.6's
   invariant note go in `NOTES.md`, which is gate-only. `c/*` is the MEASUREMENT
   digest and costs 32 cells to repair.**
7. ⛔ **A `spec.md` / `NOTES.md` MUST NOT CITE `.temp/`** (§F6) — cite the
   committed probe. ⭐ **`probes/ph66_key_identity.sh`,
   `probes/ph66_djbx33a_collide.py` and `probes/rebuild_hardened_php.sh` are all
   committed; cite THOSE, never a workdir.**
8. ⚠ **`.temp/php66/` only — never `/tmp`.** Keep the generator, delete the
   artefact; if a blob has no script that rebuilds it, write one.
9. ⚠ **A comment is not code.** Test behaviour, not text. ⓘ On this row `:387`'s
   comment (*"Numeric indices are marked by making the nKeyLength == 0"*) is
   load-bearing as **evidence of the convention**, never as proof of runtime
   behaviour.
10. ⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY for writing.**
    ⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`,
    `pilot/`, `common-php/`.** ⚠ **No `git add` / `git commit`.** Never touch
    `.web/` — a concurrent session owns it.
11. ⛔ **QUOTE A RE-GATEABLE READING AS AN EVENT, NEVER A STATE** (`F119`/M2).
    *"`contract_sha256` was `X` at commit `Y`"*, never *"…is `X`"*.
12. ⛔ **WHEN YOU REPAIR A DEFECT FOUND IN ONE PLACE, CHECK EVERY PLACE THAT
    SHARES THE ARTEFACT.** `_059` named `ph16`'s Δshare table; `ph03` and `ph29`
    carried the same table with the same two defects and were missed for a day.
13. ⛔⛔ **A CHECK THAT REFUSES YOUR ROW IS A HYPOTHESIS ABOUT YOUR ROW FIRST**
    (`F43`/`F47`). **Never edit an expectation to match an observation.**
14. ⭐ **COUNT IT, DON'T ASSERT IT**, and ⛔ **"I called the tool's function" is
    NOT "I ran the tool"** (`F138`). If a tool prints a SET, **run it for its
    set**; `len()` of something you never printed is how a false superlative got
    published.
15. **Brackets**: `harness/measure.py --check-stale` → **`66/0`** (must NEVER
    move); `harness-php/gate.py --tool measure --check-stale` → **`26/0` before
    you start, `28/0`** once this row's two records land. **Quote first and
    last.** ⓘ Both were green at `HEAD` when this file was written.

---

## §4 DEFINITION OF DONE

1. ⭐⭐⭐ **§2.3's FIVE-CELL MATRIX RE-RUN AND RECORDED AS AN EVENT** — the
   binary named, **both §A3a cautions repeated in `NOTES.md`** (oracle build ≠
   museum default, **flags not recorded in a `.buildinfo`** — do not name flags,
   `F139`; and a clean run is not evidence of absence, `F3`). **If it does not
   reproduce, that is the headline and the task stops there.**
2. **The row built at all five rungs + R1h**, gated, verdict quoted **from the
   gate record, named**.
3. ⭐⭐⭐ **§2.5's obligation 5 discharged AND THE GATE-DEFECT ADDRESSED IN ONE
   SENTENCE**: you ran it on a row the protocol excuses, and whether you agree
   with `F141` that the gate is stated on the wrong predicate.
4. ⭐⭐⭐ **§2.8's P1 SCORED WITH ITS FULL LADDER TABLE** — R1/R2/R3/R4/R5
   adversarial folds side by side. ⛔ **If they agree, PUBLISH THAT.** It is the
   row's reason for existing and `CLAUDE.md` rule 6 makes it a finding.
5. ⭐⭐ **§2.6's obligation stated for R5 and justified in `NOTES.md`**, with the
   labeller's note quoted as the corpus artefact it is. ⚠ **`CATALOGUE.md`'s
   `inv/obl` column is NOT edited.**
6. ⭐ **§2.7's UB constraint honoured, and SHOWN**: say explicitly that every
   free in your kernel is a correct free, and how you know.
7. **`inside_share` per cell as a matrix, BEFORE the statistic is chosen**;
   **which of the two quantities you mean, labelled**; both statistics labelled;
   **both C columns on every cross-language figure**; **more than one
   optimisation level, or an explicit statement that you measured one**; any
   family-B figure cleared through §B5 with **two verdicts**.
8. **The five §2.8 predictions scored, either way, by name.**
9. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.** `UNTESTED` and *"I could
   not tell"* are valued answers, and they are what the reviewer reads first.
   ⚠ **If you route a question to the manager, put it HERE and say so in the
   report's headline** — and ⛔ **do not route it to a PROCESS** (*"the next
   round"*, *"a reviewer"*): that is `F140`, measured on the manager, and a
   question with no named addressee is one nobody answers.
10. **Brackets quoted first and last.**
11. ⛔ **If a prediction survives, say so plainly. Do not manufacture a
    refutation to have something to report.**
12. ⚠ **If you stop mid-row, stop CLEANLY and write a `§N ORDER TO RESUME IN`**
    — `_051` did exactly that and `_052` finished the row from it. **A
    task-notification means STOPPED, not FINISHED** (item 118).
13. ⭐ **WHERE THIS BRIEF IS WRONG, SAY SO.** §2.3 is here *because* the manager's
    own scoping document asserted the opposite and had to be rewritten; §2.4
    refutes another of its predictions. **Two of this brief's premises started
    life as manager claims that measurement destroyed.** ▶ **Expect more.**
