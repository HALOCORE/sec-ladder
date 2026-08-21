# TASK_054 report — the sole-catcher sentence, measured on p12 and audited across 16 patterns

**Role:** research engineer. **Edited:** `patterns/p12-strcat-fixed/NOTES.md`
only (plus `results/gate/p12-strcat-fixed.json`, rewritten by `check.py p12` as
the task file says it will be). No `git add`, no `git commit`. Nothing under
`pilot/`, `.memory/`, `harness/`, `common/` or any other pattern was touched.

**Answer to the manager's least-sure call (item 2's scope), up front:
"p12 was the last one" is FALSE. The phrase-hunt found five more patterns
carrying the same claim, and on all five the mechanism it names as sole is
measurably not sole.** Four of them (p03, p04, p11, p18) are as wrong as p12
was; the fifth (p05) states the overclaim in two places and the *correction* in a
third, in the same file. The general rule is worth a `.memory/` entry, and the
sharp form of it is not the one the task file proposed — see §4.

All scratch under `.temp/p54/`: `limbs.py` (the limb prober), `mkmut.py` (mutant
re-derivation), `stages.py` (check.py's Verus stages run against a mutant in a
repo-layout mirror), `id/` (the identity control), `pinmoved/` (the
pin-moved counterfactual), `NOTES.md`, and the logs each command wrote.
**`.temp/p54/repro.sh` rebuilds all of it from the committed tree in order**;
the two compiled binaries it produces are deleted after their digests print
(CLAUDE.md rule 1).

---

## 1. The tool, and why it is not just `pinsim.py`

`.temp/p48/pinsim.py` (the precedent) simulates stage 5a's clause comparison and
nothing else. `.memory/04-verus.md:506-521` requires a mutation report to say
**which twin limb** fired, and 5a itself has four ways to fail. So
`.temp/p54/limbs.py` re-derives the comparison from `harness/check.py` directly
(it imports `harness/vparse` and `check._is_trusted`) and reports eight limbs,
each with the `check.py` line range it is copied from:

```
5a-items   item set added/removed                  check.py:2204-2208
5a-clause  per-item external/requires/ensures      check.py:2210-2241
5a-obl     shipped `N verified` vs verus.obligations         :2264-2287
5a-verify  shipped errors > 0                                :2273-2274
5ct-sig    5c-twin LIMB (i)  twin signature == trusted's     :3374-3382
5ct-cfg    twin cfg/in_verus/external/banned-word hygiene    :3362-3392
5ct-run    5c-twin LIMB (ii) `--cfg slb_twin` errors > 0     :3410-3421
5ct-obl    `--cfg slb_twin` count vs verus.twin_obligations  :3446-3454
```

`.temp/p54/stages.py` goes further where it matters: it builds a repo-layout
mirror under `.temp/p54/mirror/` and calls `check.py`'s **actual** stage
functions (`check_verus_contract`, `check_call_site`, `check_clause_deletion`,
`check_requires_strength`, `check_trusted_twins`) on it — p05 §10's
"mutant swapped into the pattern dir, gate run, tree restored" without the swap,
so the pattern directory is never written to and no gate JSON is rewritten.
**Negative control: the shipped `verus.rs` through that mirror gives
`total failures: 0`** (`.temp/p54/stages-shipped.log`).

---

## 2. p12, measured

### 2.1 What the sentence said

`patterns/p12-strcat-fixed/NOTES.md:1047-1050`, as published:

> ### 9b. `p2_weak_write_requires` -- one character, and only the TWIN sees it
> `i < old(v)@.len()` → `i <= old(v)@.len()` in `dst_set_unchecked` **and** in its
> twin, so the two signatures still match and `spec.md`'s item pin does not move.

### 2.2 Which limbs actually fire

`.temp/p54/limbs-full.log`, all four p12 proof mutants regenerated from the
committed `controls/gen_controls.py`:

```
=== verus.rs                     shipped 15/0  twin 18/0     NO LIMB FIRES
=== p1_no_capacity_check.rs      shipped 14/1  twin 17/1
      [5a-verify] 14 verified, 1 errors: invariant not satisfied before loop
      [5ct-run]   17 verified, 1 errors: invariant not satisfied before loop
=== p2_weak_write_requires.rs    shipped 15/0  twin 17/1
      [5a-clause] dst_set_unchecked.requires ['i <= old(v)@.len()'] != pinned ['i < old(v)@.len()']
      [5a-clause] slb_twin_dst_set_unchecked.requires ['i <= old(v)@.len()'] != pinned ['i < old(v)@.len()']
      [5ct-run]   --cfg slb_twin: 17 verified, 1 errors: precondition not met
=== p3_slotwise_write_ensures.rs shipped 14/1  twin 17/1
      [5a-clause] dst_set_unchecked.ensures ['final(v)@[i as int] == x'] != pinned [...]
      [5a-verify] invariant not satisfied at end of loop body
      [5ct-sig]   slb_twin_dst_set_unchecked sig != dst_set_unchecked sig
      [5ct-run]   invariant not satisfied at end of loop body
=== p4_taut_kernel_ensures.rs    shipped 14/1  twin 17/1
      [5a-clause] kernel.ensures ['r == r'] != pinned ['r == strcat_fold(...)']
      [5a-verify] assertion failed
      [5ct-run]   assertion failed
```

**Two limbs fire on `p2_weak_write_requires`: stage 5a with two clause diffs,
and 5c-twin limb (ii).** The cause is structural, and it is the same one
TASK_047_REVIEW found on p06: `p12/spec.md`'s `verus.items` pins the clause text
of **`slb_twin_dst_set_unchecked` as well as `dst_set_unchecked`**, both at
`requires ["i < old(v)@.len()"]`, so an edit that moves both moves two pinned
clauses. `spec.md`'s item pin does not merely move — it moves twice.

Run through `check.py`'s real stage functions (`.temp/p54/stages-p2.log`):

```
== 5a. the Verus contract matches the pin in spec.md ==
  FAIL [proof-pin] verus.rs:327 `dst_set_unchecked` drifted from spec.md --
      requires: ['i <= old(v)@.len()'] != pinned ['i < old(v)@.len()']
  FAIL [proof-pin] verus.rs:343 `slb_twin_dst_set_unchecked` drifted -- (same)
== 5b. rule 2 ==               ok  main 5 verified, kernel 5 verified
== 5c. clause deletion ==      ok  4 `ensures` conjunct(s), every one load-bearing
== 5c-req. precondition strength ==
  ok  dst_set_unchecked requires[0] is not a tautology -- `i <= old(v)@.len()`
== 5c-twin. verified twin ==
  FAIL [twin] verus.rs: with `--cfg slb_twin` Verus reports 17 verified, 1 errors
      (15 verified without the twins)
    error: precondition not met: index in bounds for this access --> verus.rs:350:5

total failures: 3   sections: ['proof-pin', 'twin']
```

Three of the four Verus-side checks pass it — exactly p05 §10's shape — and the
two that fail are **5a** and **5c-twin limb (ii)**.

### 2.3 What is TRUE in the old sentence, and it is half of it

**5c-twin limb (i) does NOT fire.** `signature_identical` stays `True` — the
signatures really do still match, which is what makes limb (ii) the interesting
one and distinguishes this mutant from p13's M2 (which weakens the item alone
and trips limb (i)).

### 2.4 The identity pin does NOT fire — a clean negative, and p12 differs from p06 here

p06's correction has two halves; only one of them transfers. On p06 a *second*
mutant (`b_scrmod_msonly`, an exec-code change) also broke the `identity` pin.
p12's `p2_weak_write_requires` cannot: a `requires` is ghost. Measured rather
than argued — the mutant and the shipped file copied to **equal-length paths**
(`.temp/p54/id/{A,B}/verus.rs`, so TASK_051_REVIEW M1's source-path-length
artefact cannot confound it), the only textual difference being the two
`requires` lines, compiled at the gate's own flags
(`-C codegen-units=1 -C opt-level=3 -C debug-assertions=off --cfg slb_isolated`,
both `15 verified, 0 errors`):

```
                shipped R5           p2_weak_write_requires
n_fn / n_nopad  142 / 138            142 / 138
md5_raw         f154b78fc39aaeab…    f154b78fc39aaeab…
md5_fn          f2572cd58e4426e4…    f2572cd58e4426e4…
md5_raw_norel   e9c07b59d678d482…    e9c07b59d678d482…
```

and `results/gate/p12-strcat-fixed.json` records `unsafe vs verus O3 exact` at
`md5_fn f2572cd58e44` — the same kernel, so the equal-length-path build is the
shipped one.

### 2.5 The counterfactual that makes "Verus-level sole catcher" a measurement

The corrected claim only means something if the twin really is what is left when
the pin is silent. Measured: weaken the two pinned clauses in a copy of
`spec.md` (`.temp/p54/pinmoved/`), i.e. build the mutant the way p16, p17, p09
and p02 build theirs — the author who edits proof and pin in one commit, which
is TASK_008_REVIEW's original attack:

```
$ python3 .temp/p54/limbs.py .temp/p54/pinmoved/patterns/p12-strcat-fixed \
      verus.rs .temp/p12/controls/p2_weak_write_requires.rs --no-verus
=== p2_weak_write_requires.rs   NO LIMB FIRES
```

with the twin run still at `17 verified, 1 errors`. **With the pin moved,
5c-twin limb (ii) is the only thing left.** That is the sentence p12 should have
had.

### 2.6 The edit

`patterns/p12-strcat-fixed/NOTES.md` §9b rewritten: heading, the false sentence
replaced with the measurement, the limb named, the two clean negatives (limb (i)
and identity) recorded, and the counterfactual quoted. No other p12 file repeats
the claim — `grep -niE "twin|only the|sole"` over `README.md` and `spec.md`
returns only the obligation-count prose.

---

## 3. The cross-pattern audit

**Method.** `.temp/p54/mkmut.py` re-derives each pattern's own weak-`requires`
mutant by the same exact-string substitution its committed generator performs
(`patterns/<p>/controls/gen_controls.py`, or the inline generator in p05's
`NOTES.md` §5b), writing to `.temp/p54/mut/<pattern>/verus.rs` — **not** to
`.temp/<pattern>/`, so a concurrent agent's scratch is untouched. Each mutant
was diffed against its shipped `verus.rs`: exactly the two intended clause lines
differ, in every case. Then `.temp/p54/limbs.py` (§1). Logs:
`.temp/p54/audit-limbs.log`, `.temp/p54/audit-p18.log`, `.temp/p54/limbs-full.log`.

**The structural fact that decides the whole audit,** read off all 16
`spec.md` files at once: **every pattern pins the twin's `requires`/`ensures`
text in `verus.items` alongside the trusted item's.** So the weakening applied
to item + twin *always* moves two pinned clauses and *always* fails stage 5a —
unless the mutant edits `spec.md` in the same commit. The discriminator is not
the pattern, not the accessor, and not read-vs-write: **it is whether the mutant
moved the pin.**

### 3.1 Claims that a mutant is caught by exactly one mechanism

| # | pattern | the claim (file:line) | mutant edits `spec.md`? | limbs measured to fire | verdict |
|---|---|---|---|---|---|
| 1 | **p12** | `NOTES.md:1047` *"only the TWIN sees it"*; `:1050` *"`spec.md`'s item pin does not move"* (line numbers as published, before this task's edit) | **no** | 5a-clause ×2 + 5ct-run | **overstated — the second sentence is FALSE.** FIXED here |
| 2 | **p03** | `NOTES.md:785` heading; `:787-788` *"the contract pin does not move"*; `:804` *"the verified twin is the only mechanism in this project that catches it"* | **no** | 5a-clause ×2 (`stack_get_unchecked` + twin) + 5ct-run; shipped 9/0, twin 11/1 | **overstated — `:788` is FALSE** |
| 3 | **p04** | `NOTES.md:1065-1067` *"the contract pin does not move … only `--cfg slb_twin` catches it"*; `:1069-1070` *"the verified twin is the only mechanism in this project that catches it"* | **no** | 5a-clause ×2 (`ring_get_unchecked` + twin) + 5ct-run; shipped 9/0, twin 11/1 | **overstated — FALSE** |
| 4 | **p11** | `NOTES.md:588` heading; `:608` *"The contract pin does not move (both clauses change together)"*; `:611-612` *"the only mechanism…"*; `:781` *"it was the only stage that moved"* | **no** | 5a-clause ×2 (`get_unchecked` + twin) + 5ct-run; shipped 12/0, twin 12/1 | **overstated — `:608` and `:781` are FALSE** |
| 5 | **p18** | `NOTES.md:1578` table column *"which gate stage fails"* → **`5c-twin`**, and `:1580-1584` draws a contrast that does not exist: *"weakening only the trusted one … is caught earlier and more cheaply by `spec.md`'s `items` pin at stage 5a. The attack the twin regime exists for is the author who weakens both in one commit, and that is the mutant."* | **no** | 5a-clause ×2 (`buf_get_unchecked` + twin) + 5ct-run; shipped 12/0, twin 12/1 | **overstated — the column names one stage and two fail, and the one-side/both-sides contrast is FALSE: the pin catches both** |
| 6 | **p05** | `NOTES.md:722` verdict column *"only the verified twin catches it"*; `:898` *"the twin is the only mechanism that catches `i <= v@.len()`"* | **no** | 5a-clause ×2 (`get_unchecked` + twin) + 5ct-run; shipped 12/0, twin 12/1 | **overstated at `:722`/`:898` — but `:1027-1046` already prints both `[proof-pin]` FAILs and the correct hedge. The file contradicts itself; only the summary lines are wrong** |
| 7 | p06 | `NOTES.md:992-993`, `:1450-1493`, `README.md:120` | no | 5a-clause ×2 + 5ct-run | **correct** — corrected at TASK_048 to *"sole **Verus-level** catcher"*, with the 2 diffs quoted |
| 8 | p14 | `NOTES.md:1330`, `:1390-1404` (`pm2_weakreq`) | no | 5a-clause ×2 + 5ct-run | **correct** — states *"'the twin is the SOLE catcher' is FALSE here too"* and quotes the 2 diffs |
| 9 | p14 | `NOTES.md:1365` *"on this mutant the *proof* is the sole catcher"* (`pm1_nocap`, an exec-code deletion) | n/a — no clause moves | 5a-verify; contract pin 0 diffs, measured in-pattern | **correct**, with one omission: a `verus.rs` that fails to verify also fails `[build]` (×4), `[proof-rule2]`, `[clause-mut]` and `[req-mut]` downstream — p08 `NOTES.md:927-934` documents that cascade and p14 does not mention it |
| 10 | p13 | `NOTES.md:1059` "caught by" column: **M2** → *"`spec.md`'s `verus.items` pin (5a) **and** 5c-twin LIMB (i)"*; **M2b** → *"5c-twin LIMB (ii) + the pin"*; `:1074` *"M2 is caught twice"* | no | as stated | **correct — the gold standard.** It is the only pattern whose table names the limb *and* the pin |
| 11 | p08 | `NOTES.md:915-919` *"The `spec.md` pin catches it because the mutation is a source diff a reviewer can read; the twin catches it semantically, and the twin is the only mechanism that would still object if the pin had been edited in the same commit"* | no | 5a-clause ×2 + 5ct-run, both printed at `:904-912` | **correct** |
| 12 | p16 | `NOTES.md:919` *"the twin is the **only** oracle standing between the gate and a green run certifying CWE-125 as an axiom"* | **YES** (`:900-901`: *"in the item, in the twin … *and* in `spec.md`'s pin, all in one edit"*) | 5ct-run only | **correct — and this is the construction the six above should have used** |
| 13 | p17 | `NOTES.md:1081-1093` M1 oracle table, 5c-twin the only FAIL | **YES** (`:1083-1084`) | 5ct-run only | **correct** |
| 14 | p09 | `NOTES.md:1012-1026` M1 *"Only the verified twin catches it"* | **YES** (`:1012-1015`, and it says why: *"the pin is unmoved because it was edited in the same commit"*) | 5ct-run only | **correct.** p09 additionally runs M2 **twice**, pin-moved and pin-left-alone, and tabulates both columns (`:1032-1036`) — the most complete treatment on the project |
| 15 | p02 | `NOTES.md:773-779` mutant table | **YES** — the table header is literally *"mutant (verus.rs **and** the spec.md pins, one commit)"* | 5ct-run; the twin-left-alone row → limb (i) | **correct — the clean negative the task file predicted.** Confirmed |
| 16 | p01, p07 | — | — | — | **no claim of this shape exists.** p07's `:828`/`:872` and p01's twin section make no sole-catcher claim about a mutant |

### 3.2 Adjacent hits of the shape that are NOT about a mutant, checked and left alone

| pattern | claim | verdict |
|---|---|---|
| p09 `spec.md:124`, `:232` | *"caught only by the functional `ensures`"* / *"caught only by the *postcondition*"* for the `q & 31` and `q >> 7` mask bugs | **correct.** The scope is stated in the sentence (*"no sanitiser, no bounds check and no memory-safety proof"*) and `model.py` is named as the co-catcher in the same clause. It is a statement about **which Verus obligation**, not about which gate stage |
| p17 `NOTES.md:893`, `:911-912` | *"The only thing in `verus.rs` that rejects it is `r == range_fold(…)`"* | **correct**, and explicitly scoped to `verus.rs`. §7 M4 measures it (`9 verified, 1 error`, the one error functional; strip the functional spec → `10 verified, 0 errors`) |
| p13 `NOTES.md:1148` | *"Nothing but the idiom pin excluded it"* (the bulk `copy_nonoverlapping`/`write_bytes` route) | **correct as stated** — it enumerates the alternatives it rules out (not `is not supported`, verifies, clean twin, `identity: exact`). **Not re-measured by me**; and it is superseded anyway, `:1149-1151` records the entry was relaxed at TASK_046 |
| p16 `NOTES.md:789`, p17 `NOTES.md:944` | *"5c-twin is the only one that judges *strength*"* | **correct** — a statement about what each stage judges, not about what caught a mutant. `check.py`'s own 5c-twin summary line says the same thing verbatim |

---

## 4. The general rule, in `.memory/`-ready form

The task file proposed: *"a sole-catcher claim must name the layer — Verus-level,
gate-level or pin-level — because a mutant that edits a proof usually also moves
a pin."* **The audit says something sharper, and the difference matters: the pin
is not moved by the mutant, it is moved by the *author*, and whether the author
moved it is the entire content of the claim.**

> **A "the twin is the sole catcher" claim is a claim about the MUTANT'S
> CONSTRUCTION, not about the gate.** Every pattern's `spec.md` pins the clause
> text of the **twin** in `verus.items` alongside the trusted item's. So the
> canonical weakening — `i < v@.len()` → `i <= v@.len()` in the item *and* its
> twin — moves **two pinned clauses** and fails stage 5a (`verus_contract`),
> which runs **before** 5c-twin. Measured on p03, p04, p05, p11, p12 and p18:
> 2 clause diffs each, plus 5c-twin limb (ii); shipped configurations 9/0, 9/0,
> 12/0, 12/0, 15/0, 12/0, so the *Verus-alone-is-blind* premise is true every
> time and only the conclusion about the gate is wrong. Limb (i) does **not**
> fire on any of them — the signatures do still match.
>
> **The twin is the sole catcher only of the mutant that edits `spec.md` in the
> same commit** — TASK_008_REVIEW's original attack, and the reason the twin
> exists. p16, p17, p09 and p02 build it that way and say so in the mutant's own
> description; their "only the twin" is correct. p03, p04, p05, p11, p12 and p18
> do not, and theirs is not.
>
> **So: build the mutant with the pin moved, or write *Verus-level* sole
> catcher. Do not write "the pin does not move" — check it, with
> `check.py`'s own comparator, because on every pattern on this project it does.**
> Report the limb (`.memory/04-verus.md`'s twin section), and say whether the
> `identity` pin moved: a `requires` edit is ghost and cannot move it (p12,
> byte-identical kernels), an exec-code edit can (p06's `b_scrmod_msonly`).

p13 `NOTES.md:1059` is the template for the "caught by" column; p09
`NOTES.md:1032-1036` is the template for reporting a mutant both ways.

---

## 5. Gate

`harness/check.py p12`, complete run, no flags (`.temp/p54/gate-p12.log`, 331
lines):

```
check.py: PASS
$ grep -c 'FAIL \[' .temp/p54/gate-p12.log   ->  0
```

`results/gate/p12-strcat-fixed.json`:

```
verdict        PASS
complete_run   True
failures       []
blocked        0        loud 1  (the standing `tcb-unsafe` shout about
                                 `dst_set_unchecked`'s `x` parameter, justified
                                 in spec.md and unchanged by this task)
verus          verus.rs 15 verified / 0 errors, pinned 15
twins          verus.rs 18 verified / 0 errors
identity       unsafe vs verus  O0 norel (pinned norel)
               unsafe vs verus  O3 exact (pinned exact)
```

`git diff` on the gate JSON is **two keys**: `source_sha256` for
`patterns/p12-strcat-fixed/NOTES.md` (the file I edited) and three
ASLR-dependent UBSan `store to address 0x…` strings in `sanitizer`. Nothing
substantive moved.

```
$ git status --porcelain
 M patterns/p12-strcat-fixed/NOTES.md
 M results/gate/p12-strcat-fixed.json
?? .tasks/TASK_054_REPORT.md
```

---

## 6. Problems / not done / adjacent

- **I fixed only p12.** p03, p04, p05, p11 and p18 carry the same defect and are
  reported, not touched, per item 3 of the task file. Four of the five need the
  same one-sentence correction p06 and p14 already carry; p05 needs only its two
  summary lines aligned with its own §10.
- **An adjacent claim inside the paragraph I rewrote, measured and left alone.**
  `p12/NOTES.md:1064-1065` says *"p12 is the second pattern to exercise it on a
  WRITE (p03 is the first)"*. p03's `p1_weak_requires` weakens
  **`stack_get_unchecked`** — a **read** (`p03/controls/gen_controls.py:431-443`);
  p03's only write-accessor mutant is `p3_weak_invariant`, which fails at
  `stack_set_unchecked`'s precondition in the **shipped** configuration, i.e.
  not in the twin regime at all. p04's `p1_weak_requires` is likewise on the
  reader. So on the evidence p12 is the **first** pattern to exercise the twin
  regime on a write, not the second. It is a different claim from the one I was
  sent to fix and it is a "first/second" bookkeeping sentence, so I report it
  rather than editing it.
- **No wall-clock measurement of any kind was run**, per the constraint.
- **I did not re-run the other five patterns' generators**; I re-derived their
  mutants by the identical substitution and diffed each against the shipped
  `verus.rs` (exactly the two clause lines). That avoids writing into
  `.temp/p03/`, `.temp/p04/`, `.temp/p05/`, `.temp/p11/`, `.temp/p18/` while
  other agents may be running.
- **The five other patterns' full-gate behaviour is inferred from stages 5a and
  5c-twin only.** I ran `check.py`'s real stage functions end-to-end on p12's
  mutant (`.temp/p54/stages-p2.log`) but not on theirs.
- **p13 `NOTES.md:1148` was not re-measured** (see §3.2).
- **`RECAP.md` needs the manager's hand, twice, and I did not touch it** (it was
  modified in the working tree by another agent when I started). `RECAP.md:996-998`
  says *"**p12's `NOTES.md:1046-1049` is still wrong** (queue item)"* — now fixed
  — and `:1363-1366` says the phrase *"should be audited wherever it appears"* —
  now done, with four more hits.
- **Reproducibility of the new NOTES citations.** `.temp/p54/limbs.py` and
  `.temp/p54/stages.py` are gitignored, exactly like `.temp/p48/pinsim.py` which
  `p06/NOTES.md:1459` already cites. I mitigated it by naming the five `check.py`
  functions and their line numbers in the p12 text, so the tool is re-derivable
  from the description rather than from the file. **Suggestion, not done because
  it is outside the task:** `limbs.py` is pattern-agnostic and would be more use
  in `harness/` (or as a `controls/` file per pattern) than in scratch — six
  patterns now need it.
- **`.memory/` was not edited** (subagents may not). §4 is the text to land, and
  PROTOCOL rule 9 applies: it has not been through a review.
