# TASK_139 — `p29` BUILT. Both design questions settled on a stated criterion; the 27th pattern ships.

**Role: research engineer.** `harness/check.py p29` and `harness/measure.py p29`
were both run. `.temp/t136/` and `.temp/t137/` were **read and never written**;
`.memory/`, `RECAP.md`, `results/SYNTHESIS.md` and `harness/tools/composition.py`
were **not touched**; no `git add` / `git commit`. Scratch is `.temp/t139/`.

---

## VERDICT IN ONE SCREEN

| item | verdict |
|---|---|
| **Deliverable 1 — the safety-line SITE** | ✅ **READ PATH, on a stated criterion — and BOTH candidates re-measured exact on the SHIPPED kernel, so the measurement does not decide it.** The criterion: *the shipped R1h must be the artefact the row's headline is a claim about, and the same claim must be legible in every rung.* ⚠ **Two of the five rows in the comparison do not discriminate and the report says which.** The losing arm ships as a control derived from `c/kernel.c` by substitution. |
| **Deliverable 2 — is `tab[]` nulled on free?** | ✅ **NO — `p27`'s convention, and its argument is now a MEASUREMENT.** Adding `tab[cur] = NULL` changes the one-conjunct control's sanitizer class from `heap-use-after-free` to **`SEGV`**. Two further reasons found, one of them proof-side: not nulling is what makes `wf`'s cache invariant free. |
| **Deliverable 3 — BUILD** | ✅ **BUILT as `patterns/p29-bst-delete/`. `check.py: PASS`** — `failures: []`, `blocked: []`, read out of `results/gate/p29-bst-delete.json` and not grepped. `harness/measure.py p29` recorded; `results/tables/p29-bst-delete.md` rendered and stage 9c calls it *byte-identical to a fresh render*. **27 patterns.** |
| **The R5** | ✅ **`25 verified, 0 errors`** shipped, **`30 / 0`** twin, **TCB 7** — the same seven `p27` ships, and **the second conjunct costs none of them**. Full functional refinement: `ensures r == bst_fold(buf@, off, len)` over an abstract machine with three walks. |
| **The attack arm** | ✅ **10 mutants, 10 as expected.** `M3b` deletes the occupant-identity conjunct and nothing else — **linearity has no objection and the FUNCTIONAL refinement is what rejects it**, which is `TASK_137`'s prediction confirmed. `M2b` fails on a **precondition**: the identity test cannot be *written* first. |
| **`model.py`** | ✅ Written from the contract: a **purely functional BST**, recursive three-case delete with a separate `_del_min`, tree shape held **outside** the record, and a **reachability walk** as the read test — no cursor, no `par`, no `goleft`, no guard, no liveness array. Cross-checked against a second implementation that mirrors the Verus `run`. |
| **⚠ FIRST `identity: differ` ROW IN THE TREE** | `O3: norel`, `O0: differ`. `.memory/02-bench-rules.md` records `differ` as a legal pin **that no pattern had exercised** — *"one real run is owed"*. This is that run, and `p27`'s one-line `-O0` fix provably does not transfer. |
| **⚠⚠ FOR THE MANAGER** | `harness/tools/composition.py --check` now prints `FAIL: built but unclassified: ['p29']`. **Not edited, per the task file.** p29's class is **TEMPORAL** — the second one — and the published table in `.memory/02-bench-rules.md` moves from `TEMPORAL 1` / total `26` to `TEMPORAL 2` / total `27`. **The START HERE box's derived counts all move by one pattern's worth** — 26 → **27** patterns, 27 gate records, 27 published tables, and `52 → 54` if that figure is `json + table` per pattern, which is what it looks like. ⚠ **DERIVE them; do not take this line for it.** ⚠⚠ **The blocked-row count does NOT move: p29's gate record carries `blocked: []`**, so `p01 = 1`, `p42 = 1` and every other pattern `0` still holds. |
| **Running count** | base **672**, branch delta **+7**, **= 679**. |

---

## 1 — DELIVERABLE 1: the criterion, stated first, then applied

⚠⚠ **The measurement does NOT decide this and I want that on the record before
the argument.** `controls/arms.py` rebuilds both candidates from the shipped
`c/kernel.c` by substituting one line, and over 500 random windows:

```
                              wrong  on 104 UAF  on 18 RECYCLE   ASan lines
  R1h  read path, 2 conjuncts     0     0/104        0/18             0
  H2   write path, 1 site         0     0/104        0/18             0
```

Both exact, both silent. `TASK_137` was right that the choice was open and right
that it could not be closed by fuzzing.

> ### THE CRITERION
> **The shipped R1h must be the artefact the row's headline is a claim about,
> and the same claim must be legible in every rung.**

A benchmark row's product is its `c/kernel.c` ↔ `c/kernel_hardened.c` diff plus
the numbers hung on it. A headline describing a line the tree does not contain is
an anecdote, not a measurement — `.memory/03-measurement.md` entry 12's class.

| | read path (SHIPPED) | write path (`H2`) |
|---|---|---|
| **the headline is the shipped diff** | ✅ `p27`'s `&& live[h] == 1` and `p29`'s `&& live[g_slot] == 1 && tab[g_slot][0] == g_key` are two committed files a reader can diff | ✗ `p29`'s diff would be a pointer-nulling *statement inside `REMOVE`*, which has no `p27` counterpart at all |
| **legible in every rung** | ✅ C spells both conjuncts; **safe Rust gets the first from `Option` and must write the second by hand**; R5 turns the first into `perms.dom().contains(g_slot)` and the second into a value equality | ✗ the safe rungs would null a cached *index* — neither what the language gives them nor what C does |
| **R5 tractability** | ✅ the check discharges its own precondition **locally** | ✗ needs a global existential re-established by every mutation. ⚠ **ARGUED, NOT MEASURED — no `H2` R5 was built** |
| **exactness** | exact | exact — **does not discriminate** |
| **one line, one site** | yes | yes — **does not discriminate** |

✅ **The losing arm is kept and measured, not described**: `controls/arms.py`
splices the write-path line into the shipped `c/kernel.c`, so it cannot drift
away from the rung it varies.

---

## 2 — DELIVERABLE 2: `tab[]` is NOT nulled, and `p27`'s argument is now measured

`p27`'s `c/kernel.c` argues by name that nulling the table slot *"would turn the
stale read into a NULL dereference, which is a **crash**, not a use-after-free,
and a different bug class."* `TASK_136`'s draft `p29` nulled it anyway.

**Measured on p29's own kernel** (`controls/arms.json`, `nulltab_*` columns —
the same arms with `tab[cur] = NULL;` restored after the free):

```
arm        shipped: class                 with tab[cur]=NULL: class        wrong
keyonly    heap-use-after-free            SEGV                             7 -> 104
R1         heap-use-after-free            heap-use-after-free            122 -> 122
deref      heap-use-after-free            heap-use-after-free              7 -> 7
R1h / H2   (none)                         (none)                           0 -> 0
```

**Exactly one arm moves, and it changes CLASS, not magnitude.** `p27` had the
argument in prose in two places; nothing had measured it on a second kernel.

**Two further reasons, and the second is new:**

1. Not nulling is what makes `tab[g_slot][0]` and `g_saved[0]` **the same load
   from the same address**, so the only thing separating the shipped safety line
   from a use-after-free is the short-circuit order. Null the table and that
   sharpness is replaced by a different crash.
2. ⚠ **It is what makes the R5's cache invariant free.** `wf`'s last conjunct is
   `st.gh ==> g_saved == tab[st.gs as int]`, and with `tab[]` written once per
   slot **no operation has to re-establish it** — not the insert, not the splice,
   not the free. Nulling would make it conditional on liveness and force a
   re-proof at every deletion. The design question and the proof turn out to have
   the same answer for different reasons.

⚠ **And the interaction `TASK_136` missed**: the read-path line *can* be spelled
`tab[g_slot] != NULL` instead of `live[g_slot] == 1`, and that spelling
**requires** the nulling. Deliverable 2 therefore decides part of deliverable 1:
`live[]` — `p27`'s own spelling — is the only one available.

---

## 3 — DELIVERABLE 3: what shipped

```
patterns/p29-bst-delete/
  c/kernel.h  c/kernel.c  c/kernel_hardened.c  c/main.c
  safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
  model.py  spec.md  NOTES.md  README.md
  inputs/gen.py                      + 8 gitignored blobs
  controls/mkspec.py  arms.py  proof_mutants.py  repro.py  miri_arms.py
           arms.json  proof_mutants.json  repro.json  miri_arms.json
```

**The row, in one diff.** `c/kernel.c` and `c/kernel_hardened.c` are
character-identical apart from one line and its comment:

```c
R1    if (g_saved != NULL) {
R1h   if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key) {
                             ^^^^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^^^^^^^^^^
                             p27's WHOLE line     NEW: occupant identity
```

**One omission, two bug classes, selected by the DEGREE of the deleted node** —
0/1 child → the record is **freed** (ASan aborts, the value is not reproducible);
2 children → the successor's key/val are copied **into** it and the *successor*
is freed (ASan silent, wrong answer **stable**).

### 3a. THE SHARPEST NEW RESULT: the two conjuncts fail in DIFFERENT CURRENCIES

500 windows, `controls/arms.json`:

| dropped conjunct | wrong answers | ASan lines |
|---|---|---|
| **liveness** (`live[g_slot] == 1`) | **7 of 104** UAF windows — the freed bytes usually still hold the old record | **208** |
| **occupant identity** (`tab[g_slot][0] == g_key`) | **18 of 18** recycle windows — every one | **0** |

**Neither subsumes the other and their harms are not the same kind.** One is
memory-unsafety that is usually *not* a wrong answer; the other is a wrong answer
that is *never* a memory error. `TASK_137` had the two-conjunct claim; this is
the sentence that makes it non-trivial.

### 3b. The four-mechanism table, and one row that needed a control the gate cannot supply

| mechanism | use-after-FREE | use-after-RECYCLE |
|---|---|---|
| ASan | fires (gate stage 7, three inputs) | **clean** (gate stage 7, `adversarial-recycle.bin`) |
| Miri | ⚠ **UB**: `memory access failed: alloc… has been freed` (`controls/miri_arms.json`) | ⚠⚠ **no UB, and it prints a different number** — `2751827421526092736` against the correct `2755550117516839872` |
| safe Rust `Option` | the class cannot occur | **`Some`, and it is somebody else's record** |
| Verus linear `PointsTo` | consumed; unprovable | **survives; nothing linear objects** (`M3b`) |

⚠⚠ **THE GATE'S MIRI STAGE CANNOT SUBSTANTIATE THE MIRI ROW OF THIS TABLE, AND I
NEARLY PUBLISHED IT ANYWAY.** `check.py` runs Miri over `unsafe.rs` — the
**correct** rung — so all eight rows read `no UB` and say nothing about either
bug class. I had written the Miri row from the argument; reading the gate log
caught it. `controls/miri_arms.py` now measures it, running Miri over
`unsafe.rs` with the two conjuncts deleted, with the shipped file as the
must-be-clean control — and the result is the one the table claims: **UB on both
use-after-free inputs, and on the recycle input Miri runs the buggy program to
completion, says nothing, and prints a different number.** **This generalises
past p29: any pattern whose mechanism table has a Miri row needs its own arm,
because the gate only ever runs the rung that is right.**

### 3c. Stability, and it goes further than the earlier work knew

`TASK_136` §2f measured that the recycle read is stable **within one binary**.
The gate's stage-4 table measures more: on `adversarial-recycle.bin` **all eight
buggy C cells — gcc and clang × `-O0`/`-O3` × isolated/whole — print one wrong
value**, against *"4 distinct behaviours"* per C rung on the use-after-free
inputs. ⚠ `controls/repro.py` re-runs `p25`'s kill on the shipped inputs and
publishes the **invariant** with a dated history, never a pinned count — `p23`'s
rule.

### 3d. The gate, three runs, and the second one is worth reading

| run | verdict | what it found |
|---|---|---|
| `gate1` | **FAIL, 7** | all mechanical and all mine: one twin signature formatted differently from its trusted item, five missing `SLB-TRUSTED-ARGUMENT` sections, and the published table not yet rendered. **Nothing about the kernel, the model, the proof, the checksums, the sanitizers, Miri, the driver loop or the identity pin.** |
| `gate2` | **FAIL, 5** | the seven were fixed and **five STALENESS pins fired instead** — I had corrected doc comments in `c/kernel.{c,h}`, `unsafe.rs` and `verus.rs` after generating the control JSONs and the table, and every one of the four `controls/*.json` plus the render said so by name. ⚠ **That is stage 9b doing exactly its job on a pattern that had just shipped it**, and it is the reason `controls/` sidecars carry `derived_from_sha256`. |
| `gate3` | ✅ **`check.py: PASS`** | **`failures: []`, `blocked: []`**, `contract_sha256 f77972d2d5da…` matching `spec.md`, `identity` `O0 differ / O3 norel` both **as pinned**, stage 9c *"byte-identical to a fresh render"*, all four `controls/*.json` **FRESH**. Log: `.temp/t139/logs/gate3.log`. |

⚠ **The `gate2` cycle is the honest cost of the doc corrections in §7's last
bullets** — four control re-runs, a re-measure and a re-render — and it is
recorded rather than hidden, because `PROTOCOL.md`'s own advice is to batch
rung-source doc fixes into one pass and I did not, the first time.

### 3e. What the gate itself measured about the row (not my probes — its own stages)

```
stage 3c  unsafe vs verus O0: differ   (as pinned)      O3: norel   (as pinned)
stage 4   adversarial-recycle.bin  model 6826524771972934656
          ALL EIGHT buggy C cells (gcc/clang x O0/O3 x isolated/whole)
                                   10466247628510718976   <- ONE wrong value
          adversarial-uaf / -succ / -many:  "4 distinct behaviours" per C rung
stage 7   uaf / succ / many : ASan `heap-use-after-free`, fired as declared
          recycle           : CLEAN, exit 0, and the checksum is still wrong
stage 8   miri unsafe.rs, all 8 inputs : no UB   <- the CORRECT rung; see 3b
```

⚠⚠ **Stage 7's `adversarial-recycle.bin` row is the row's whole thesis in one
line of gate output: the sanitizer is clean, the exit code is 0, and the number
is wrong.**

---

## 4 — THE R5

```
./verus_run.py patterns/p29-bst-delete/verus.rs                -> 25 verified, 0 errors
./verus_run.py patterns/p29-bst-delete/verus.rs --cfg slb_twin -> 30 verified, 0 errors
```

`ensures r == bst_fold(buf@, off as int, len as int)` — the full functional
refinement the tree's 26 other contracts pin. `TASK_136` §2e named this as the
item that would dominate the row's cost, and it did.

**What made it tractable, recorded so the next temporal row does not re-derive it:**

- **`walk` is a verified helper with a refinement `ensures`**, shared by INSERT,
  FIND and REMOVE, so the loop-invariant work happens once instead of three
  times: `r == descend(st, st.root, NIL, false, k, TABCAP)`, with
  `descend(.., TABCAP - steps) == descend(.., TABCAP)` as the invariant.
- **`wf` is split** into `base` (read side) and the dealloc/cache conjuncts, so
  `walk` — which frees nothing — requires only the half it needs.
- **The friction was entirely re-establishing quantified facts after a ghost
  state update.** Verus does not carry `forall j. lv[j] ==> rec_ok(.., st, ..)`
  across `st = St { root: ch, ..st }` even though `rec_ok` does not mention
  `root`; nine short `assert forall .. by` blocks are the bulk of the ghost code.

### 4a. ⚠⚠ AT R5 THE `&&` ORDERING OF THE SAFETY LINE IS FORCED

In C the short-circuit is what keeps the identity test from being a
use-after-free, and a reviewer could call the ordering style. **One rung up it is
not available as a choice**: reading the record needs
`perms.tracked_borrow(g_slot)`, whose precondition is
`dom().contains(g_slot)`, and only `live[g_slot] == 1` discharges it. Measured —
`M2b` fails with **`precondition not satisfied` at the borrow**, not with a
postcondition failure. C's `&&` ordering is a type-system consequence.

### 4b. The mutation battery — 10 of 10

| mutant | expect | got | what fails |
|---|---|---|---|
| `M0-control` | verify | ✅ | — |
| `M1-live-store` | fail | ✅ | `loop invariant not satisfied` — the permission is gone and `live[cur]` still claims it |
| `M2b-liveness-no-hint` | fail | ✅ | ⚠ **`precondition not satisfied` at `tracked_borrow`** (§4a) |
| `M3b-identity-no-hint` | fail | ✅ | ⚠⚠ **the `run(..) == run(..)` refinement.** Nothing linear objects |
| `M4-r1-line` | fail | ✅ | `c/kernel.c`'s line verbatim |
| `M5-fold-multiplier` | fail | ✅ | `postcondition not satisfied` — it reads the body |
| `M6-constant-body` | fail | ✅ | `return 0;` does NOT discharge the `ensures` — `TASK_136`'s ARM_C hazard, closed |
| `M7-drop-walk-fuel` | fail | ✅ | no termination measure |

*(`M2`/`M3` are the same two mutations with the localising ghost asserts left in;
they fail on the assert instead, which is why the `b` variants exist.)*

### 4c. TCB is 7, and the new obligation costs none of it

The occupant-identity conjunct is discharged by the **functional postcondition**,
an ordinary value equality — not by an axiom. **The new half of `p29`'s safety
line is free in trust and expensive in proof.** One declaration `p27` does not
need: `global layout Rec is size == 4, align == 1;`, because the tree's links
live inside the record and Verus gets nothing from `#[repr(C)]`. It emits a
static check at codegen, and `NOTES.md` counts it as an axiom anyway.

### 4d. What the proof actually costs, and it is not the safety line

**Six liveness conjuncts and five step bounds — eleven terms in
`c/kernel_hardened.c`, and not one of them can fire.** They exist because the
alternative is proving the link structure **is a tree** (unique parents,
acyclicity), which is what *"every link points at a live slot"* needs and which
no per-slot invariant gives you. With them the licence for a record read is
`p27`'s own `live[i] == 1 <==> perms.dom().contains(i)`. ⚠ **They are in EVERY
rung**, so no rung-to-rung comparison is confounded by them — and the safe rungs
would need the liveness half anyway (`unwrap` on `None` is a panic).

---

## 5 — ⚠ THE FIRST `identity: differ` ROW, AND `p27`'s FIX DOES NOT TRANSFER

| level | R4 | R5 | verdict |
|---|---|---|---|
| `-O3 isolated` | 611 insns, `md5_raw e24fc411…` | 611, `02fd34b9…` | **`norel`** — `md5_raw_norel 9f816ce2…` on both; `asm.py diff`: *"normalised text identical"* |
| `-O0 isolated` | **870** | **900** | **`differ`** |
| `-O0`, R4 via `core::ptr::write` | **886** | 900 | still `differ` |

`p27` bought `-O0` identity with one line — `*base = v` instead of
`core::ptr::write(base, v)`, because vstd's `ptr_mut_write` is
`#[inline(always)]` over a precompiled vstd. **Once the record is a four-byte
struct rather than a byte, no R4 spelling matches**; three were built and
counted. `.memory/02-bench-rules.md` says `differ` is legal and *"no pattern with
`identity: differ` has been through the gate; one real run is owed"*. **This is
that run, and the gate's consequence is the right one**: `check_miri` treats
R4 ≠ R5 as a *reason Miri is required*, with Miri as the compensating control.

⚠ **One second-order consequence, disclosed in the `rec_alloc` trusted
argument**: `p27` closes the body-drift gap with two legs — byte-identity at
`-O3` and Miri. On p29 leg one is `md5_raw_norel`, not `md5_raw`, and at `-O0` it
says nothing at all. Leg two is unchanged and is the independent one.

---

## 6 — `.memory/` UPDATES OWED (the manager applies; I touched nothing)

1. **`.memory/04-verus.md`** — ⚠ **a `struct` inside `verus!` is its own
   obligation, exactly as a `const` is.** Measured, not inferred: p29's
   per-function census sums to **24** against a measured total of **25**, and
   adding one further bare `#[repr(C)] struct Rec2 { a: u8 }` to a copy takes it
   to **26** (`.temp/t139/verus/probe_ob.rs`). The `global layout` directive
   carries **zero**. The file records the `const` rule and not this one.
2. **`.memory/02-bench-rules.md`**, the `identity` pin section — the debt it
   names is **discharged**: p29 is the first pattern through the gate with
   `identity: differ` (at `-O0`), it passes, and `check_miri`'s handling is as
   documented. ⚠ Also worth adding: **`p27`'s `*base = v` fix is
   record-shape-specific** and does not transfer to a struct payload.
3. **`.memory/02-bench-rules.md`** composition table — p29 is **TEMPORAL**, the
   second one. `harness/tools/composition.py --check` FAILS today with
   `built but unclassified: ['p29']`; **I did not edit it**, per the task file.
   The published block becomes `TEMPORAL 2`, total `27`.
4. **`.memory/03-measurement.md`** — ⚠ **the gate's Miri stage runs the CORRECT
   rung, so it can never substantiate a "Miri sees / does not see" row.** Any
   pattern publishing a mechanism table with a Miri row owes a dedicated arm.
   p29 ships one (`controls/miri_arms.py`); no other pattern in the tree has one.
5. **`RECAP` 51 / the `p29` catalogue cell** — the two re-opened questions are
   settled and the row is built; the four-mechanism table's Miri row is now
   measured rather than assumed; and the recycle divergence is stable **across
   the matrix**, not merely within one binary.

⚠ **All of the above is ENGINEER work and unreviewed** (PROTOCOL rule 9).
Everything regenerates from committed generators — the command list is
`NOTES.md` §10.

---

## 7 — WHAT I DID NOT DO, AND WHAT I AM UNSURE OF

- **NO COST AXIS IS PUBLISHED.** Not one rung-to-rung difference appears in
  `NOTES.md`, `spec.md`, `README.md` or this report. The measurement record has
  the numbers; nothing reads them. `.memory/02-bench-rules.md`'s count-the-levers
  rule would require searching both rungs' spellings first, and **neither side
  was searched.**
- **The `H2`-vs-shipped R5 argument is an ARGUMENT.** No `H2` R5 was built. What
  is measured is that the shipped read-path R5 needs only the write-once
  invariant; that the alternative is worse is inference.
- **One C shape and one Verus encoding were searched.** A record with the links
  in slot arrays would make the proof smaller — and would make the two-child
  splice a *choice* rather than a consequence of the algorithm, which is why it
  was rejected. It was not built.
- **The `-O0` `differ` was not chased to its last instruction.** Three R4 write
  spellings were built and counted; which of the five write sites contributes
  which of the thirty instructions was not disassembled.
- **`inputs/gen.py`'s benign invariant is enforced by the generator's own copy of
  the checked semantics**, which cannot import `model.py` (it imports `slb`
  against a file that does not exist yet). p27 has the same duplication.
- ⚠ **The obligation census's residual was attributed by experiment, but only
  one experiment.** I showed a second struct adds 1; I did not show that removing
  the `global layout` directive subtracts 0 (it cannot be removed — the file stops
  verifying).
- **`spec.md`'s `contract_sha256` MOVED ONCE, before anything was committed**,
  and `NOTES.md` §0 says so in full rather than reporting a compliant-looking
  hash. The move deleted two rebuild-produced counts from the hashed fence.
- ⚠ **The safe rungs are CORRECT, deliberately, and that is a design call a
  reviewer may want to attack.** `TASK_133`/`TASK_136` measured a safe rung that
  omits the identity conjunct and is silently wrong on the recycle class; here
  that arm is a **control**, not a rung, because the row is admitted on **limb 1**
  and does not need a broken safe rung. The honest statement is sharper anyway:
  *safe Rust writes the first conjunct for you and does not write the second, in
  any language.* ⚠ **If the reviewer disagrees, the change is one conjunct in two
  files and a re-gate.**

---

## 8 — CLEAN NEGATIVES: attacks that did NOT land

1. **"The read-path line is not exact once the two-child liveness tests are
   added."** No — re-derived on the shipped kernel: `0` wrong of 500 windows,
   `0` ASan lines.
2. **"`H2` was rejected because it is worse."** No. It is exactly as exact and
   exactly as quiet; it lost on comparability, and the report says which two rows
   of the comparison do not discriminate.
3. **"The recycle class is an artefact of one optimisation level."** No — all
   eight buggy C cells across two compilers, two opt levels and two inline modes
   print one wrong value.
4. **"The R5's `ensures` is vacuous / the cheapest body discharges it."**
   `TASK_136`'s ARM_C hazard, closed: `M6` replaces the body with `return 0;` and
   gets `postcondition not satisfied`.
5. **"The identity conjunct is rejected by linearity, so the second conjunct is
   not really new."** No — `M3b` deletes it, every permission is where the
   invariant says it is, and the failure is the functional refinement.
6. **"ASan is blind on this box."** Positive control fires in every probe
   (`rc=1 hits=2 heap-use-after-free`), and the `keyonly` arm fires 208 times on
   the same corpus where the shipped line fires zero.
7. **"`model.py` agrees with the kernel because it is the kernel again."** Two
   implementations of different shapes — a functional tree with a reachability
   read test, and the slot-sequence machine that mirrors the Verus `run` — and
   `selfcheck()` runs them against each other on every gate run.

---

## 9 — PROTOCOL rule 2 running count. Base **672** (as given). Branch delta **+7**:

1. **A `struct` inside `verus!` carries its own proof obligation**, exactly as a
   `const` does — measured (24 named + 1 residual; a second bare struct → 26).
   `.memory/04-verus.md` records the `const` rule and not this one.
2. **`identity: differ` has now been through the gate** — the run
   `.memory/02-bench-rules.md` says is owed — and it passes; and **`p27`'s
   one-line `-O0` identity fix does not transfer** to a struct payload
   (870 / 886 / 900, three spellings built).
3. **`p27`'s `tab[h]`-nulling argument is now a measurement on a second kernel**:
   the class changes from `heap-use-after-free` to `SEGV`.
4. **The two conjuncts fail in different currencies** — liveness: 208 ASan lines
   and 7/104 wrong; identity: 0 ASan lines and 18/18 wrong. Neither subsumes the
   other, and `TASK_137`'s two-conjunct headline becomes non-trivial.
5. **The recycle divergence is stable across the whole matrix**, not just within
   one binary as `TASK_136` §2f measured: one wrong value in all eight buggy C
   cells.
6. **At R5 the safety line's `&&` ORDER is forced by the type system**, not
   chosen: `tracked_borrow`'s precondition is discharged only by the liveness
   conjunct (`M2b`, `precondition not satisfied`).
7. **The gate's Miri stage runs the CORRECT rung and therefore cannot
   substantiate any "Miri sees / does not see" claim.** I had drafted the Miri
   row from the argument and the gate log caught it; a dedicated control now
   measures it, and no other pattern in the tree has one.

**672 + 7 = 679.**
